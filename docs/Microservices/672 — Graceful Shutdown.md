---
layout: default
title: "Graceful Shutdown"
parent: "Microservices"
nav_order: 672
permalink: /microservices/graceful-shutdown/
number: "672"
category: Microservices
difficulty: ★★★
depends_on: "Zero-Downtime Deployment, Kubernetes"
used_by: "Blue-Green Deployment, Canary Deployment"
tags: #advanced, #microservices, #distributed, #reliability, #kubernetes
---

# 672 — Graceful Shutdown

`#advanced` `#microservices` `#distributed` `#reliability` `#kubernetes`

⚡ TL;DR — **Graceful Shutdown** ensures a service stops accepting new requests and completes in-flight requests before terminating. In Kubernetes: pod receives `SIGTERM` → stops accepting new connections → drains in-flight requests → exits. Without it: pod kills drop active HTTP requests and leave database transactions partial, causing 500 errors during every deployment.

| #672            | Category: Microservices                  | Difficulty: ★★★ |
| :-------------- | :--------------------------------------- | :-------------- |
| **Depends on:** | Zero-Downtime Deployment, Kubernetes     |                 |
| **Used by:**    | Blue-Green Deployment, Canary Deployment |                 |

---

### 📘 Textbook Definition

**Graceful Shutdown** (or graceful termination) is the process by which a service, upon receiving a termination signal (`SIGTERM` on Linux/Kubernetes), performs an orderly shutdown: (1) stops accepting new incoming connections or requests; (2) completes all currently in-flight requests within a configurable drain period; (3) closes database connections and message consumer subscriptions; (4) flushes in-progress telemetry (metrics, traces, logs); and (5) exits cleanly. The opposite — **ungraceful shutdown** — is a `SIGKILL` that immediately terminates the process, dropping in-flight HTTP requests, leaving database transactions open (causing lock timeouts), and potentially corrupting local state. In Kubernetes, the pod lifecycle provides: `terminationGracePeriodSeconds` (default: 30 seconds) during which the pod processes `SIGTERM` before `SIGKILL` is sent. The load balancer (kube-proxy, Istio) must stop routing new traffic to the pod before or simultaneously with `SIGTERM` to avoid a race condition where new requests arrive on a draining pod.

---

### 🟢 Simple Definition (Easy)

Graceful shutdown = "finish what you're doing, then stop." When Kubernetes kills a pod, it first says "please stop." The application: stops accepting new requests, finishes current requests, then exits cleanly. Without this: Kubernetes kills the pod mid-request — users get errors during deployments.

---

### 🔵 Simple Definition (Elaborated)

Pod receives `SIGTERM`. Order service has 12 in-flight HTTP requests being processed. Without graceful shutdown: pod exits immediately — those 12 requests get `500 Connection Reset`. With graceful shutdown: pod marks itself as unhealthy (readiness probe returns 503 → load balancer stops routing here), continues processing the 12 existing requests, closes DB connection pool after the last request finishes, exits. Those 12 users get their responses. New requests went to healthy pods. Zero user-visible errors during the deployment.

---

### 🔩 First Principles Explanation

**Kubernetes pod termination sequence — the race condition:**

```
KUBERNETES POD TERMINATION (problematic if not handled):

T+0:  User runs: kubectl delete pod order-service-abc123
      OR: Kubernetes controller kills pod for rolling update

T+0:  TWO THINGS HAPPEN SIMULTANEOUSLY:
      1. SIGTERM sent to pod's main process
      2. Pod removed from Service Endpoints list
         → kube-proxy: will stop routing new requests to this pod
         → But: kube-proxy propagation delay: 1-10 seconds!

T+0 to T+10: RACE CONDITION WINDOW:
      Pod has received SIGTERM (knows to stop).
      kube-proxy still routing requests to pod (hasn't propagated yet).
      If pod exits immediately on SIGTERM → new requests arrive on dead pod → 502/503

CORRECT SEQUENCE:
  T+0:    SIGTERM received
  T+0-1:  Sleep for 5-10 seconds (allow kube-proxy to propagate endpoint removal)
            During this window: pod is STILL healthy, serving new requests normally
  T+10:   Mark readiness probe as unhealthy (or pod already removed from endpoints)
  T+10:   Stop accepting new connections
  T+10-30: Drain in-flight requests (complete pending HTTP requests, transactions)
  T+30:   Close DB connections, flush telemetry
  T+30:   Exit with code 0 (clean shutdown)
  T+30+:  If still alive: Kubernetes sends SIGKILL (hard kill)
            Set terminationGracePeriodSeconds >= drain window + buffer

THE CRITICAL FIX: add delay between SIGTERM and stopping new requests:
  This "pre-stop" delay allows kube-proxy to remove the pod from rotation
  before the pod stops accepting connections.
```

**Spring Boot graceful shutdown configuration:**

```yaml
# application.yml:
server:
  shutdown: graceful # enables Spring Boot graceful shutdown

spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s # max time to drain in-flight requests


# Combined with Kubernetes lifecycle preStop hook:
```

```yaml
# Kubernetes Deployment spec:
spec:
  template:
    spec:
      terminationGracePeriodSeconds: 60 # must be > preStop delay + drain timeout
      containers:
        - name: order-service
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 10"]
                # preStop runs BEFORE SIGTERM is sent to the main process
                # Provides time for kube-proxy to propagate endpoint removal
                # After preStop completes: SIGTERM is sent to application
          readinessProbe:
            httpGet:
              path: /actuator/health/readiness
              port: 8080
            periodSeconds: 5
            failureThreshold: 1
            # When SIGTERM received, Spring Boot sets readiness to DOWN
            # kube-proxy: stops routing to this pod within 1 probe period
```

**Kafka consumer graceful shutdown — handling in-flight message processing:**

```java
@Service
class OrderEventConsumer {
    private final AtomicBoolean shuttingDown = new AtomicBoolean(false);

    @KafkaListener(topics = "order-placed-events", groupId = "inventory-service")
    @Transactional
    void handleOrderPlaced(OrderPlacedEvent event) {
        if (shuttingDown.get()) {
            // Don't process: we're shutting down. Kafka will rebalance to another consumer.
            throw new IllegalStateException("Service shutting down — rejecting message");
        }
        inventoryService.reserve(event.getProductId(), event.getQuantity(), event.getOrderId());
        // If successful: offset committed (Kafka consumer ACK)
        // If exception: offset NOT committed → Kafka redelivers to another instance
    }

    @PreDestroy
    void shutdown() {
        log.info("Graceful shutdown initiated — stopping Kafka consumption");
        shuttingDown.set(true);
        // Spring Kafka: kafkaListenerEndpointRegistry.stop() stops all consumers
        // Outstanding messages: Kafka rebalances to another consumer group member
        // DB transactions: Spring @Transactional rollback on exception → consistent state
    }
}
```

**Complete graceful shutdown sequence for a Spring Boot Kafka microservice:**

```java
@SpringBootApplication
public class OrderServiceApplication {

    @Autowired private KafkaListenerEndpointRegistry kafkaRegistry;
    @Autowired private DataSource dataSource;

    @PreDestroy
    void gracefulShutdown() throws Exception {
        log.info("=== GRACEFUL SHUTDOWN START ===");

        // STEP 1: Stop accepting new HTTP requests
        // Spring Boot shutdown=graceful handles this automatically

        // STEP 2: Stop Kafka consumers (stop consuming new messages)
        log.info("Stopping Kafka consumers...");
        kafkaRegistry.stop(() -> log.info("Kafka consumers stopped"));

        // STEP 3: Wait for in-flight HTTP requests to complete
        // Spring Boot's graceful shutdown timeout handles this (timeout-per-shutdown-phase)

        // STEP 4: Close database connection pool
        log.info("Closing database connection pool...");
        if (dataSource instanceof HikariDataSource hikari) {
            hikari.close();
        }

        // STEP 5: Flush OpenTelemetry traces/spans
        // OTel SDK shutdown hook handles this automatically

        log.info("=== GRACEFUL SHUTDOWN COMPLETE ===");
    }
}
```

---

### ❓ Why Does This Exist (Why Before What)

Microservices deployments happen frequently (multiple times per day in CD environments). Each deployment kills old pods and starts new ones. Without graceful shutdown, every deployment causes a brief spike of 500 errors for users whose requests land on a terminating pod. In a system with 10 deployments per day across 20 services, ungraceful shutdown creates measurable error rate increases and SLO violations. Graceful shutdown is the difference between "zero-downtime deployment" being a marketing claim vs a technical reality.

---

### 🧠 Mental Model / Analogy

> Graceful shutdown is like a restaurant closing at the end of the night. The polite version: at 10pm (SIGTERM), the door is locked (no new customers). But: the customers already seated are served their meals and finish dining. After the last customer leaves, the kitchen is cleaned and locked (DB connections closed). At 11pm (terminationGracePeriodSeconds), everyone is gone and the restaurant closes cleanly. The ungraceful version: at 10pm, turn off all lights, kick everyone out mid-meal. That's SIGKILL.

---

### ⚙️ How It Works (Mechanism)

**Verification: test graceful shutdown in dev:**

```bash
# Deploy and test graceful shutdown locally:

# 1. Send continuous traffic to the service:
watch -n 0.1 'curl -s http://localhost:8080/api/orders | jq .status'

# 2. Simultaneously send SIGTERM to the Spring Boot process:
kill -SIGTERM $(pgrep -f order-service.jar)

# EXPECTED:
#   Requests in-flight: continue to return 200 (no errors)
#   New requests after preStop delay: load balancer stops routing here
#   Service exits cleanly after drain timeout
#   Zero 5xx errors in the log

# FAILURE (ungraceful - what NOT to have):
#   Some requests return "Connection refused" or 500
#   "java.lang.RuntimeException: Context closed" in logs
#   Database connections not properly closed (orphaned locks)
```

---

### 🔄 How It Connects (Mini-Map)

```
Zero-Downtime Deployment
(deploys without user impact)
        │
        ▼
Graceful Shutdown  ◄──── (you are here)
(pod termination without dropping requests)
        │
        ├── Blue-Green Deployment → traffic cutover requires graceful drain of Blue
        ├── Canary Deployment → pod rotation during canary progression needs graceful shutdown
        └── Kubernetes → terminationGracePeriodSeconds + preStop lifecycle hook
```

---

### 💻 Code Example

**Integration test validating graceful shutdown:**

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class GracefulShutdownTest {

    @LocalServerPort int port;
    @Autowired ApplicationContext ctx;

    @Test
    void shutdownCompletesInFlightRequests() throws InterruptedException {
        // Start a slow request (simulates an in-flight request during shutdown):
        CompletableFuture<ResponseEntity<String>> inFlightRequest = CompletableFuture.supplyAsync(() ->
            new RestTemplate().getForEntity(
                "http://localhost:" + port + "/api/orders/slow-endpoint", String.class
            )
        );

        Thread.sleep(100);  // Request is now in-flight

        // Trigger shutdown:
        ctx.publishEvent(new ContextClosedEvent(ctx));

        // In-flight request must complete (not fail):
        ResponseEntity<String> response = inFlightRequest.get(10, TimeUnit.SECONDS);
        assertThat(response.getStatusCodeValue()).isEqualTo(200);
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                          | Reality                                                                                                                                                                                                                                                             |
| ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `terminationGracePeriodSeconds: 30` is always sufficient               | The correct value depends on: preStop sleep duration + maximum expected request duration + DB connection close time. For services with long-running requests (batch operations), set to 120+ seconds                                                                |
| Setting `server.shutdown=graceful` is all that's needed in Spring Boot | Also required: `terminationGracePeriodSeconds` in Kubernetes pod spec >= Spring Boot drain timeout + preStop sleep. Without the Kubernetes setting, Kubernetes sends SIGKILL at 30 seconds regardless of Spring Boot's drain timeout                                |
| Graceful shutdown handles `SIGKILL`                                    | `SIGKILL` cannot be caught or handled — the OS kills the process immediately. Graceful shutdown handles `SIGTERM`. `SIGKILL` is only sent by Kubernetes after `terminationGracePeriodSeconds` expires. The goal is to always complete shutdown before that deadline |
| Readiness probe returning DOWN stops all requests instantly            | Load balancer stops routing NEW requests to the pod, but existing in-flight requests on existing connections continue. HTTP/1.1 persistent connections may still deliver new requests briefly. Use `Connection: close` response header during drain period          |

---

### 🔥 Pitfalls in Production

**terminationGracePeriodSeconds too short for long-running requests:**

```
SCENARIO:
  Payment processing: some requests take up to 45 seconds (external bank API).
  terminationGracePeriodSeconds: 30 (Kubernetes default).

  Deployment: pod receives SIGTERM at T+0.
  Spring Boot: draining. 3 requests in-flight, one started 20 seconds ago.
  T+30: Kubernetes loses patience → sends SIGKILL.
  Spring Boot: killed mid-drain. 1 request still in-flight (at 20 seconds, bank API pending).
  Bank API: completes successfully → payment charged.
  Order database: transaction rolled back by SIGKILL.
  State: payment charged, order not confirmed → inconsistent state.

FIX:
  # Calculate correct terminationGracePeriodSeconds:
  # preStop sleep (10s) + max request duration (45s) + buffer (15s) = 70s
  terminationGracePeriodSeconds: 70

  # AND: Spring Boot drain timeout must be less than terminationGracePeriodSeconds:
  spring.lifecycle.timeout-per-shutdown-phase: 55s
  # (leaves 15s for K8s overhead after Spring Boot finishes draining)

  ALSO: Idempotency key in payment processing:
  If SIGKILL occurs mid-transaction: payment may have been charged.
  On restart: order retry checks for existing payment before charging again.
  Idempotency key prevents double-charge.
```

---

### 🔗 Related Keywords

- `Zero-Downtime Deployment` — graceful shutdown is the pod-level requirement for zero-downtime
- `Blue-Green Deployment` — Blue environment requires graceful drain during traffic cutover
- `Canary Deployment` — pod rotation during canary requires graceful shutdown
- `Kubernetes` — `terminationGracePeriodSeconds` and `preStop` hooks configure graceful shutdown

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ SEQUENCE     │ SIGTERM → preStop sleep → stop accepting  │
│              │ → drain requests → close resources → exit │
├──────────────┼───────────────────────────────────────────┤
│ SPRING BOOT  │ server.shutdown=graceful                  │
│              │ spring.lifecycle.timeout-per-shutdown: 30s│
│ KUBERNETES   │ terminationGracePeriodSeconds: 60         │
│              │ preStop.exec: sleep 10                    │
├──────────────┼───────────────────────────────────────────┤
│ CALCULATE    │ preStop + max req duration + buffer = TGP │
│ DANGER       │ TGP too short → SIGKILL mid-transaction   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your service processes Kafka messages. During graceful shutdown, the Kafka consumer stops, but 3 messages are mid-processing (transactions started, not committed). Kubernetes SIGKILL fires before they complete. Kafka: no ACK received → messages redelivered to another consumer instance after group rebalance. The other instance processes them again. Design the idempotency mechanism that ensures these re-delivered messages are safe to process again without double-application of their effects. What state must be persisted to detect "already processed" messages?

**Q2.** You are reviewing a microservice that currently uses `terminationGracePeriodSeconds: 30` (default). The service: (a) processes HTTP requests that typically take 50ms but occasionally spike to 60 seconds during database maintenance windows; (b) maintains a Kafka consumer group with 5 topic partitions; (c) uses HikariCP with max pool size 20. Calculate the correct `terminationGracePeriodSeconds` value. Describe what happens to Kafka partition rebalancing during the shutdown period and whether there's a risk of message loss or duplication.
