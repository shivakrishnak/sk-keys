---
layout: default
title: "Graceful Shutdown (Microservices)"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 57
permalink: /microservices/graceful-shutdown-microservices/
id: MSV-057
category: Microservices
difficulty: ★★★
depends_on: Zero-Downtime Deployment, Health Check (Microservices), Kubernetes
used_by: Zero-Downtime Deployment, Canary Deployment (Microservices), Blue-Green Deployment
related: Zero-Downtime Deployment, Sidecar Pattern (Microservices), Readiness Probe
tags:
  - microservices
  - deployment
  - resilience
  - operations
  - deep-dive
status: complete
version: 1
---

# MSV-057 - Graceful Shutdown (Microservices)

⚡ TL;DR - Graceful shutdown is the process of stopping a service pod in an orderly way: stop accepting new requests, finish in-flight requests, release resources cleanly - without dropping active connections or corrupting in-progress work.

| #672            | Category: Microservices                                                            | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Zero-Downtime Deployment, Health Check (Microservices), Kubernetes                 |                 |
| **Used by:**    | Zero-Downtime Deployment, Canary Deployment (Microservices), Blue-Green Deployment |                 |
| **Related:**    | Zero-Downtime Deployment, Sidecar Pattern (Microservices), Readiness Probe         |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Kubernetes scales down your Order Service from 10 pods to 5 pods (auto-scaling). Kubernetes sends `SIGTERM` to 5 pods. The pods immediately call `System.exit(0)`. At the moment of termination, each pod has 15–20 in-flight HTTP requests. Those requests receive connection-reset errors. Users see: "Network error - please try again." Your load balancer still has the pod in its pool for 2 more seconds (health check interval). Requests continue to arrive at the terminating pods for 2 seconds, all erroring.

**THE BREAKING POINT:**
Every rolling deployment, scaling event, or pod eviction terminates pods. If pod termination drops in-flight requests, every deployment creates a brief cascade of user-visible errors. At high traffic (1000 RPS), even a 5-second ungraceful shutdown window produces ~5000 failed requests per pod termination.

**THE INVENTION MOMENT:**
Graceful shutdown is the solution: on `SIGTERM`, the pod (a) removes itself from the load balancer pool; (b) stops accepting new connections; (c) finishes all active requests; (d) releases resources (DB connections, Kafka consumers); (e) exits. All existing requests complete normally; no user sees an error from pod termination.


**EVOLUTION:**
Graceful shutdown became a critical operational concern as container-based deployments made service restarts routine. In traditional VM deployments, services were rarely restarted (uptime was a virtue). Kubernetes' rolling deployments made pod restarts a frequent, expected event. The SIGTERM/SIGKILL lifecycle was defined in Kubernetes 1.0 (2015). Spring Boot's @PreDestroy hooks and Quarkus's fast startup became standard Java implementations. The discipline evolved from 'protect my long-running process' to 'design for graceful, fast shutdown as a normal daily operation.'
---

### 📘 Textbook Definition

**Graceful shutdown** is the ordered, controlled termination of a service process that ensures: (1) no new requests are accepted after a shutdown signal is received; (2) all in-flight requests are allowed to complete; (3) stateful resources (database connections, Kafka consumer group members, caches) are cleanly released; (4) the process exits with success (exit code 0) when all work is complete. In Kubernetes, graceful shutdown is coordinated with the pod lifecycle: `SIGTERM` initiates shutdown; `terminationGracePeriodSeconds` sets the maximum time allowed; `SIGKILL` is sent if graceful shutdown doesn't complete within the grace period.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Before dying, a service politely finishes what it's doing, closes all doors, and leaves everything tidy.

**One analogy:**

> A restaurant closing for the night. At 10PM (SIGTERM), the manager stops seating new diners. Existing diners finish their meals. Staff clean tables as diners leave. At midnight (grace period end), the restaurant is empty and locked. No diner was kicked out mid-meal. No table was left dirty. Contrast: a power outage (SIGKILL) - diners mid-meal, food on the stove, cash register open.

**One insight:**
Graceful shutdown is a contract between the service and the infrastructure. Kubernetes promises to send `SIGTERM` and wait `terminationGracePeriodSeconds` before forcing `SIGKILL`. The service promises to honour `SIGTERM` and finish its work within that window.

---

### 🔩 First Principles Explanation

**THE KUBERNETES POD TERMINATION LIFECYCLE:**

```
User/scheduler: DELETE pod

Kubernetes:
  1. pod.status = Terminating
  2. Remove pod from Service endpoints (load balancer pool)
     [NOTE: this propagates asynchronously - takes 1-3 seconds]
  3. Execute preStop hook (if configured)
  4. Send SIGTERM to all containers
  5. Wait terminationGracePeriodSeconds (default: 30s)
  6. If process still running: send SIGKILL (force kill)

THE RACE CONDITION:
  Steps 2 and 3-4 happen in parallel (not sequential!).
  Load balancer removal (step 2) may take 1-3 seconds.
  SIGTERM is received immediately.
  → Service may receive requests AFTER receiving SIGTERM
     (because LB still has it in pool)
  → SOLUTION: preStop hook sleep to absorb the propagation delay
```

**THE GRACEFUL SHUTDOWN SEQUENCE (correct):**

```
1. SIGTERM received
   Service: set flag: "shutting down = true"

2. preStop hook sleep (5-10 seconds)
   Purpose: wait for LB to remove pod from pool
   (absorbs endpoint propagation delay)

3. Stop accepting new connections / mark readiness false
   (if readiness probe checks shutdown flag)

4. Drain in-flight requests
   HTTP: wait for active request handlers to complete
   Kafka: commit offsets; leave consumer group
   DB: complete active transactions; close connection pool

5. Release resources
   Close DB connections
   Flush buffers / commit final Kafka offsets
   Close file handles

6. Exit cleanly (exit code 0)
```

**THE RACE CONDITION SOLUTION (preStop hook):**

```yaml
lifecycle:
  preStop:
    exec:
      command: ["/bin/sh", "-c", "sleep 10"]
# This 10-second sleep runs BEFORE SIGTERM.
# Actually: preStop runs at the same time as SIGTERM propagation.
# Effective sequence: preStop starts → SIGTERM sent →
#   preStop sleeps 10s → SIGTERM handler runs → drain starts
```

**THE TRADE-OFFS:**
**Gain:** Zero dropped requests during pod termination; clean resource release; no data corruption from abrupt termination; Kafka consumer group rebalance is clean.
**Cost:** Pod termination takes longer (grace period must be sufficient); must implement SIGTERM handler in application; must tune `terminationGracePeriodSeconds` to match actual drain time; streaming connections (WebSocket, SSE) require special handling.

---

### 🧪 Thought Experiment

**SETUP:**
Pod A receives `SIGTERM`. The application has: 20 active HTTP requests (avg 100ms each), a Kafka consumer processing a batch of 50 messages, and 3 open database transactions.

**WITHOUT GRACEFUL SHUTDOWN:**
Immediate exit: 20 HTTP requests → connection reset. Kafka: 50 messages in-flight, no offset commit → reprocessed by other consumer (duplicate messages). 3 DB transactions → rolled back by DB after connection close.

**WITH GRACEFUL SHUTDOWN:**

1. SIGTERM: mark shutdown=true.
2. HTTP server: stop accepting new connections; complete the 20 active requests (100–200ms).
3. Kafka consumer: finish current message batch; commit offsets; call `consumer.wakeup()` to stop poll loop; leave consumer group.
4. DB: complete the 3 transactions; close connection pool.
5. Exit after all three are done (typically 1–5 seconds total).

**THE INSIGHT:**
Graceful shutdown for Kafka is particularly important: without it, the consumer group rebalance on pod kill is slow (session timeout: default 10 seconds), messages are reprocessed (duplicate processing), and the rebalance blocks all consumers in the group.

---

### 🧠 Mental Model / Analogy

> Graceful shutdown is like an aircraft landing procedure. A pilot doesn't cut the engines mid-flight when ATC says land (SIGTERM). The pilot: (a) stops accepting new passengers (won't take new flights); (b) completes the current flight; (c) follows the landing sequence; (d) parks at the gate; (e) shuts down engines only when everything is safely stopped. Emergency landing (SIGKILL) skips all this - acceptable in emergencies, not for routine operations.

- "Cut engines mid-flight" → `System.exit(0)` on SIGTERM
- "Landing procedure" → graceful shutdown sequence
- "ATC says land" → SIGTERM
- "Emergency landing" → SIGKILL after grace period expires
- "Passengers exit safely" → in-flight requests complete

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When your service receives a "stop" signal, instead of stopping immediately and dropping everything, it finishes what it's doing, saves its state, closes connections cleanly, and then stops. No requests are lost; no data is corrupted.

**Level 2 - Spring Boot implementation (junior developer):**
Spring Boot automatically handles `SIGTERM` for HTTP: it drains active requests via `server.shutdown: graceful` in `application.yml`. For Kafka consumers, you need to handle `@PreDestroy` to commit offsets and call `KafkaListenerEndpointRegistry.stop()`.

**Level 3 - Kubernetes integration (mid-level engineer):**
The critical issue: Kubernetes removes the pod from endpoints asynchronously. Without a preStop sleep, the pod receives SIGTERM immediately but the load balancer still routes requests to it for 1–5 seconds. Solution: `preStop: exec: sleep 10` gives the LB propagation time before the SIGTERM handler stops accepting requests. Also: `terminationGracePeriodSeconds` must be > max request duration + preStop duration (e.g., max request 30s + preStop 10s → terminationGracePeriodSeconds: 60).

**Level 4 - Advanced shutdown scenarios (senior/staff):**
Streaming connections (WebSocket, SSE, gRPC streaming) require explicit close message during graceful shutdown (can't just stop the connection). Kafka consumer groups: Kafka's cooperative incremental rebalance (COOPERATIVE_STICKY assignor) enables graceful partition handover during shutdown - partitions are transferred incrementally, avoiding full stop-the-world rebalance. Database connection pools: close pool gracefully (wait for active connections to return before closing pool, not force-close). For very long-running requests (batch operations, 5+ minutes), you may need to implement checkpointing + resumption on restart, rather than waiting for completion during graceful shutdown (too long for `terminationGracePeriodSeconds`).

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│ Kubernetes Graceful Shutdown Timeline                   │
└─────────────────────────────────────────────────────────┘

t=0:  DELETE pod
      k8s: starts endpoint removal (async)
      k8s: starts preStop hook

t=0:  preStop hook: sleep 10 (running)
      LB: still routing to pod (removal not propagated yet)

t=5:  LB: endpoint removed (propagated)
      pod: preStop still sleeping (5 more seconds)
      → no new requests arrive at pod (LB removed)

t=10: preStop hook: complete
      k8s: sends SIGTERM

t=10: Application: SIGTERM received
      Spring Boot: server.shutdown=graceful
      → HTTP connector: stop accepting connections
      → existing requests: continue to completion

t=12: Last HTTP request completes
      Kafka consumer: committed offsets, left group
      DB pool: all connections closed

t=12: Application exits (exit 0)

terminationGracePeriodSeconds: 60
(if application didn't exit by t=60: SIGKILL at t=60)
```

---

### 💻 Code Example

**Spring Boot graceful shutdown (application.yml):**

```yaml
server:
  shutdown: graceful # enable graceful HTTP shutdown

spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s # wait up to 30s for requests
```

**Kubernetes deployment configuration:**

```yaml
spec:
  terminationGracePeriodSeconds: 60 # must be > preStop + drain time
  containers:
    - name: order-service
      lifecycle:
        preStop:
          exec:
            command: ["/bin/sh", "-c", "sleep 10"]
      # readinessProbe: use this to stop routing traffic early
      readinessProbe:
        httpGet:
          path: /actuator/health/readiness
          port: 8080
        failureThreshold: 1
        periodSeconds: 5
```

**Kafka consumer graceful shutdown (Java):**

```java
@Component
public class OrderKafkaConsumer {

    private final KafkaListenerEndpointRegistry registry;
    private volatile boolean shutdownRequested = false;

    @KafkaListener(topics = "orders", groupId = "order-service")
    public void consume(ConsumerRecord<String, Order> record) {
        if (shutdownRequested) return;  // stop processing on shutdown
        processOrder(record.value());
    }

    @PreDestroy
    public void shutdown() {
        log.info("Graceful Kafka shutdown started");
        shutdownRequested = true;

        // Stop all Kafka listeners; waits for in-progress messages
        registry.stop();

        log.info("Kafka consumers stopped; offsets committed");
    }
}
```

**Readiness probe returns false on shutdown (Spring Actuator):**

```java
@Component
public class GracefulShutdownHealthIndicator implements HealthIndicator {

    private volatile boolean shuttingDown = false;

    @EventListener(ContextClosedEvent.class)
    public void onShutdown() {
        shuttingDown = true;
    }

    @Override
    public Health health() {
        return shuttingDown
            ? Health.down().withDetail("reason", "shutting down").build()
            : Health.up().build();
    }
}
```

With readiness probe set up, the pod starts failing readiness checks the moment `ContextClosedEvent` fires → Kubernetes removes it from LB pool without needing to wait for the full endpoint propagation cycle.

---

### ⚖️ Comparison Table

| Shutdown Type                   | Requests Dropped | Resources Cleaned | Data Corrupted | Kafka Rebalance        |
| ------------------------------- | ---------------- | ----------------- | -------------- | ---------------------- |
| **Graceful (SIGTERM, drained)** | None             | Yes               | No             | Clean (fast)           |
| Abrupt (SIGTERM, no drain)      | In-flight        | No                | Possible       | Slow (session timeout) |
| Force (SIGKILL)                 | All in-flight    | No                | Possible       | Slow                   |
| Out-of-memory kill              | All in-flight    | No                | Possible       | Slow                   |

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                              |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `terminationGracePeriodSeconds: 30` is always sufficient    | Must be calculated: preStop duration + max request duration + cleanup time                           |
| preStop sleep delays shutdown and is wasteful               | preStop sleep absorbs endpoint propagation delay; without it, requests arrive at a shutting-down pod |
| Spring Boot `server.shutdown: graceful` handles everything  | It handles HTTP; you still need to handle Kafka, background threads, and scheduled tasks             |
| SIGTERM handling is automatic in JVM apps                   | JVM apps need explicit shutdown hooks or frameworks that register them (Spring Boot does)            |
| Graceful shutdown prevents all errors during rolling deploy | Still need preStop to absorb LB propagation delay; otherwise new requests arrive during drain        |

---

### 🚨 Failure Modes & Diagnosis

**SIGKILL Before Drain Completes**

**Symptom:** Pod logs show "Terminated" with exit code 137 (SIGKILL); in-flight requests were dropped; error rate spike during deployment.

**Root Cause:** `terminationGracePeriodSeconds` is shorter than the actual drain time (requests + preStop + cleanup).

**Diagnosis:**

```bash
# Check pod termination reason
kubectl describe pod <pod-name>
# Look for: "Reason: OOMKilled" or "Exit Code: 137"

# Check how long graceful shutdown actually takes
# from logs:
grep "Shutdown complete" pod-logs.txt | tail -5
```

**Fix:**

```yaml
# Increase terminationGracePeriodSeconds
terminationGracePeriodSeconds: 120 # was 30
```

---

### 🔗 Related Keywords

**Prerequisites:** `Zero-Downtime Deployment`, `Health Check (Microservices)`, `Kubernetes`

**Builds On This:** `Zero-Downtime Deployment`, `Canary Deployment (Microservices)`, `Blue-Green Deployment`

**Related Patterns:** `Readiness Probe`, `Liveness Probe`, `Sidecar Pattern (Microservices)`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Ordered stop: finish work, release        │
│              │ resources, then exit cleanly              │
├──────────────┼───────────────────────────────────────────┤
│ KUBERNETES   │ SIGTERM → preStop → drain → SIGKILL       │
│ SEQUENCE     │ (if not done in time)                     │
├──────────────┼───────────────────────────────────────────┤
│ KEY CONFIG   │ server.shutdown: graceful (Spring Boot)   │
│              │ preStop: sleep 10 (absorb LB propagation) │
│              │ terminationGracePeriodSeconds: 60         │
├──────────────┼───────────────────────────────────────────┤
│ KAFKA        │ registry.stop() in @PreDestroy            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Finish what you started before leaving"  │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
A service that cannot be gracefully stopped cannot be safely deployed. Graceful shutdown is not just about completing in-flight requests - it is about transitioning all service state (database transactions, message processing, scheduled tasks) to a clean, consistent state before the process exits. The same principle governs database connection pool shutdown, Kafka consumer shutdown, and HTTP server shutdown: drain before disconnect.

**Where else this pattern appears:**
- **Database connection pool shutdown:** HikariCP drains all connections (completes queries or rolls back transactions) before releasing the pool - graceful shutdown for database resources.
- **Kafka consumer shutdown:** A consumer that commits its last offset before disconnecting prevents message reprocessing - graceful shutdown for message consumption.
- **HTTP server shutdown:** Tomcat/Netty stops accepting new connections but completes in-flight requests before stopping the thread pool - graceful shutdown for HTTP serving.

---

### 💡 The Surprising Truth

Kubernetes' graceful shutdown has a subtle race condition even experienced teams miss: when a pod receives SIGTERM, Kubernetes simultaneously removes the pod's IP from Service endpoints. But the endpoint update propagates through kube-proxy to all nodes with a delay of up to several seconds. During this window, other pods may still connect to the terminating pod's IP and receive connection refused errors. Setting a preStop sleep (5-10 seconds) gives endpoint propagation time to complete before the pod starts shutting down. Without this sleep, the graceful shutdown of the process is correct but in-flight requests from other pods still fail.
---

### 🧠 Think About This Before We Continue

**Q1.** Your Order Service pod receives a SIGTERM. At that moment it has: 3 active HTTP requests (each ~2 seconds remaining), 1 Kafka message currently being processed (40ms left), and 2 open database transactions (both < 1 second from commit). `terminationGracePeriodSeconds` is set to 10. The preStop hook is `sleep 5`. Draw the shutdown timeline and determine if the pod will exit gracefully or be SIGKILL'd.

*Hint:* Think about the timeline: SIGTERM at T=0. preStop hook (`sleep 5`) runs: T=0 to T=5. SIGTERM delivered to application at T=5. Application starts graceful shutdown: closes HTTP listener, waits for 3 active HTTP requests (2s remaining, done by T=7), waits for Kafka message (40ms, done by T=5.04), waits for DB transactions (1s each, done by T=6). All work completes by T=7. Container exits at T=7. `terminationGracePeriodSeconds=10`: no SIGKILL is issued. All work completes gracefully within the grace period.

**Q2.** Your service processes large batch imports - a single import job takes up to 10 minutes. The team wants to enable graceful shutdown. But `terminationGracePeriodSeconds: 600` (10 minutes) is too long for rolling deployments. Design an alternative strategy that enables graceful shutdown of the service without requiring a 10-minute grace period.

*Hint:* Think about what the actual requirement is: completing in-progress work, not waiting 10 minutes for no-ops. Options: (1) make batch imports resumable (checkpoint progress, restart from the last checkpoint after a restart); (2) move batch imports to a dedicated batch service with its own shutdown behavior, isolated from the main service; (3) design each import unit as a short-lived operation (process one record at a time, short-lived, easily restartable). Explore whether checkpointing reduces the worst-case shutdown window from 10 minutes to the time for one import unit (seconds to minutes).

**Q3 (Design Trade-off):** Your service processes financial transactions. Graceful shutdown must guarantee: all in-flight HTTP requests complete, all open database transactions commit, and all Kafka messages being processed are either committed or returned to the queue. Design the shutdown sequence with zero duplicate transactions and zero lost transactions.

*Hint:* Think about the order of shutdown operations: (1) stop accepting new HTTP requests (close the listener); (2) wait for all in-flight HTTP requests to complete; (3) for Kafka: commit the offset of the last successfully processed message OR rewind to the last committed offset if processing was not complete (preventing both message loss and duplicate processing); (4) commit or rollback all open database transactions; (5) close the database connection pool; (6) exit. Key ordering constraint: commit the database transaction BEFORE committing the Kafka offset, so that a crash between the two causes the message to be reprocessed (idempotent) rather than lost.
