---
id: MSV-069
title: Graceful Shutdown
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-068, MSV-001
used_by: MSV-068, MSV-066
related: MSV-068, MSV-066, MSV-001, MSV-025, MSV-063
tags:
  - microservices
  - reliability
  - deep-dive
  - lifecycle
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 69
permalink: /microservices/graceful-shutdown/
---

# MSV-069 - Graceful Shutdown

⚡ TL;DR - Graceful Shutdown: when a service receives
a shutdown signal (SIGTERM from Kubernetes), it
should: (1) stop accepting new requests, (2) finish
all in-flight requests (with a timeout), (3) close
database connections cleanly, (4) commit or roll
back pending transactions, (5) flush logs/metrics,
then exit. Without graceful shutdown: Kubernetes
pod kill = requests mid-flight are dropped = HTTP
500 or connection reset errors for those users.
Spring Boot config: `server.shutdown=graceful` +
`spring.lifecycle.timeout-per-shutdown-phase=30s`.
Also needed: Kubernetes `terminationGracePeriodSeconds`
must be >= application shutdown timeout.

| #069 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Zero-Downtime Deployment, What are Microservices | |
| **Used by:** | Zero-Downtime Deployment, Chaos Engineering | |
| **Related:** | Zero-Downtime Deployment, Chaos Engineering, What are Microservices, Health Check API, Cross-Cutting Concerns | |

---

### 🔥 The Problem This Solves

**POD KILL = DROPPED REQUESTS:**
Kubernetes terminates a pod (during rolling update,
scale-down, node drain). Without graceful shutdown:
all in-flight requests to that pod receive: TCP
connection reset (RST) or HTTP 502/503. User
experience: error page or failed form submission.
For payment APIs: partially processed transactions
that may have charged the customer but not
completed the order. Graceful shutdown: ensures
the pod processes all in-flight requests before
shutting down. Zero dropped requests during
planned pod terminations.

---

### 📘 Textbook Definition

**Graceful Shutdown** is the process by which
a service responds to a shutdown signal (SIGTERM
in Linux/Kubernetes) by completing its current
work before exiting, rather than terminating
immediately. For an HTTP microservice: (1) receive
SIGTERM; (2) stop accepting new incoming connections
(Kubernetes simultaneously removes the pod from
service endpoints, so no new traffic arrives);
(3) wait for in-flight HTTP requests to complete;
(4) close downstream connections (DB connections,
HTTP clients, Kafka consumers); (5) flush telemetry
(logs, metrics, in-progress spans); (6) exit with
status 0. For Kafka consumers: (1) receive SIGTERM;
(2) complete processing of current message batch;
(3) commit offsets to Kafka; (4) close consumer
client; (5) exit. The timeout prevents hanging:
if in-flight work doesn't complete within a
configured timeout, forced shutdown occurs. Spring
Boot: `server.shutdown=graceful` enables graceful
HTTP shutdown. Kubernetes: `terminationGracePeriodSeconds`
is the hard limit.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Graceful shutdown: finish what you started before
quitting. Stop accepting new work, complete
in-flight work, close connections cleanly, exit.

**One analogy:**
> Graceful shutdown is like a restaurant's closing
> time. At 10pm (SIGTERM): the door is locked (stop
> accepting new requests). But existing customers
> are not thrown out (in-flight requests complete).
> Staff finishes serving the existing tables (finish
> in-flight requests). Kitchen cleans up and turns
> off equipment (close DB connections, flush logs).
> Staff goes home (process exits). Forced closure
> (SIGKILL): all customers thrown out immediately;
> kitchen left dirty. Graceful shutdown: orderly
> close; all commitments honored.

**One insight:**
Graceful shutdown is the difference between planned
terminations being invisible to users (zero downtime
deployments) and causing error spikes. Kubernetes
terminations are PLANNED (rolling updates, scale-
down): happen hundreds of times per week in a
healthy system. Without graceful shutdown: each
termination causes a burst of errors for requests
in-flight at that moment. With graceful shutdown:
terminations are completely invisible to users.

---

### 🔩 First Principles Explanation

**KUBERNETES TERMINATION SEQUENCE:**

```
KUBERNETES POD TERMINATION (step by step):

1. Pod deletion requested
   (kubectl delete, rolling update, scale-down)

2. Pod status: Terminating
   Kubernetes: removes pod from Endpoints object
   kube-proxy: updates iptables/ipvs on all nodes
   Takes: up to 5 seconds for iptables propagation

3. preStop hook executes (if configured)
   Recommendation: sleep 5
   Reason: wait for iptables propagation
   so no new traffic arrives before SIGTERM

4. SIGTERM sent to container process (PID 1)
   Application: starts graceful shutdown
   - Stop accepting new requests
   - Finish in-flight requests
   - Close connections
   
5. Kubernetes waits: terminationGracePeriodSeconds
   (default: 30s; recommended: 60s for services)
   
6a. Application exits before timeout: clean exit
6b. Application still running after timeout:
    Kubernetes sends SIGKILL (forced kill)
    All in-flight requests: dropped

RACE CONDITION WITHOUT preStop sleep:
  T=0: Pod deletion requested
  T=0: SIGTERM sent (immediately)
  T=0-5s: iptables still routing traffic to pod
  T=0: Pod starts shutdown (stops accepting new requests)
  T=0-5s: New requests arrive, but pod is shutting down
  T=0-5s: Connection refused or 503
  
WITH preStop sleep 5:
  T=0: Pod deletion requested
  T=0: preStop: sleep 5 runs
  T=0-5s: iptables propagates (pod removed from routing)
  T=5s: SIGTERM sent
  T=5s: No new traffic arriving (iptables updated)
  T=5s: Pod starts shutdown
  Result: no race condition; truly zero dropped requests
```

---

### 🧪 Thought Experiment

**KAFKA CONSUMER: GRACEFUL SHUTDOWN vs ABRUPT KILL**

```
SCENARIO: Payment processing Kafka consumer
  Message: process payment for order ORD-001
  
  ABRUPT KILL (no graceful shutdown):
  Consumer: received message
  Consumer: called payment gateway (200 OK, charged)
  Consumer: about to commit to DB: orders.status=PAID
  SIGKILL: process terminated
  Result: payment charged, order not updated
  Customer: charged but no order confirmation
  Kafka offset: NOT committed
  Next restart: message redelivered, payment charged TWICE
  Data inconsistency: double charge
  
  GRACEFUL SHUTDOWN:
  Consumer: received message
  Consumer: called payment gateway (charged)
  SIGTERM: received
  Consumer: "I'm in the middle of processing; complete first"
  Consumer: commits to DB: orders.status=PAID
  Consumer: commits Kafka offset (message processed)
  Consumer: closes Kafka consumer client
  Consumer: exits
  Result: clean; message processed; offset committed
  Next restart: no redelivery (offset committed)
  Zero data inconsistency
```

---

### 🧠 Mental Model / Analogy

> Graceful shutdown is like a surgeon finishing
> an operation. If the hospital needs to evacuate
> (SIGTERM): a surgeon doesn't walk out mid-operation
> (abrupt kill). The surgeon finishes the current
> procedure (in-flight request), ensures the patient
> is stable (transaction committed), then leaves
> (process exits). An empty operating room (no
> new requests accepted). If the evacuation is
> urgent (SIGKILL timeout): forced exit, incomplete
> operation (data loss). Graceful shutdown: all
> the steps a professional does before leaving
> their workspace.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
When a service is shut down: it should finish
what it's doing first (in-flight requests), then
close cleanly. Like saving your work before closing
a program.

**Level 2 - Spring Boot config (junior developer):**
```yaml
# application.yaml
server:
  shutdown: graceful        # Enable graceful shutdown
spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
```
And in Kubernetes:
```yaml
terminationGracePeriodSeconds: 60
lifecycle:
  preStop:
    exec:
      command: ["sleep", "5"]
```
This is sufficient for most Spring Boot HTTP services.

**Level 3 - Kafka consumer graceful shutdown (mid-level):**
Spring Kafka: `spring.kafka.listener.type=batch`
+ `@KafkaListener` with `ackMode=MANUAL`. On
SIGTERM: Spring Kafka container calls `stop()` -
waits for current batch to finish processing,
then stops polling. Ensure: processing time of
one batch < `terminationGracePeriodSeconds`.
Long-processing messages: implement checkpointing
(partial progress saved to DB; resume on restart).

**Level 4 - JVM shutdown hooks (senior engineer):**
Spring Boot `server.shutdown=graceful` registers
a `SmartLifecycle` bean. When SIGTERM received:
Spring's `LifecycleProcessor` calls `stop()` on
all lifecycle beans in reverse order. HTTP
connector: stops accepting requests (Tomcat
`Connector.pause()`). Waits for active request
count = 0 (or timeout). Then context closes:
`@PreDestroy` methods called, connection pools
closed, scheduled tasks stopped. SIGKILL (hard
kill, `kill -9`): bypasses JVM. No graceful shutdown
possible. Kubernetes: only sends SIGKILL if
terminationGracePeriodSeconds exceeded. Never
use `kill -9` for planned shutdowns.

**Level 5 - Distributed graceful shutdown (principal):**
For stateful processing: two-phase shutdown:
1. Drain: stop accepting new work, wait for in-flight.
2. Checkpoint: persist current state before exit.
Distributed transaction awareness: on SIGTERM,
if a distributed transaction is in-flight (Saga
coordinator mid-saga): must decide - commit
what's possible, or roll back and re-process on
restart. Kafka exactly-once semantics (EOS):
on consumer shutdown, transactional producer
should either commit or abort the current transaction.
Kafka streams: `streams.close(Duration.ofSeconds(30))`
- commits state stores, commits consumer offsets,
closes producer. Health check update: during
shutdown, set liveness/readiness to DOWN BEFORE
starting shutdown (Kubernetes removes from load
balancer faster).

---

### ⚙️ How It Works (Mechanism)

```java
// SPRING BOOT: multiple graceful shutdown concerns

// 1. HTTP graceful shutdown
// application.yaml:
// server.shutdown: graceful
// spring.lifecycle.timeout-per-shutdown-phase: 30s
// This is ENOUGH for HTTP. No code changes.

// 2. Kafka consumer graceful shutdown
@Component
public class OrderEventConsumer {
    
    @KafkaListener(topics = "orders",
                   containerFactory = "kafkaListenerFactory")
    public void processOrder(OrderCreatedEvent event) {
        // Processing...
        // Spring Kafka: will wait for this method
        // to complete before stopping on SIGTERM
        // No special code needed in listener itself
    }
    
    // Spring Kafka container auto-handles SIGTERM:
    // - Stops polling new messages
    // - Waits for current processOrder() to complete
    // - Commits offsets
    // - Closes Kafka consumer client
}

// 3. Custom cleanup on shutdown
@Component
public class DatabaseConnectionCleanup {
    
    @Autowired
    private HikariDataSource dataSource;
    
    // Called by Spring during context close
    @PreDestroy
    public void cleanup() {
        // HikariCP: close pool (waits for active
        // connections to complete first)
        dataSource.close();
        log.info("Database connection pool closed");
    }
}

// 4. Readiness: signal not-ready FIRST
// Spring Actuator: /actuator/health/readiness
// During shutdown phase: returns 503 automatically
// Kubernetes: removes pod from endpoints based on this
// DO NOT add custom shutdown code to readiness:
// Spring handles this automatically with server.shutdown=graceful
```

```yaml
# KUBERNETES: complete graceful shutdown config
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      # MUST be > Spring's timeout-per-shutdown-phase
      # 60 > 30: Kubernetes waits 60s before SIGKILL
      # Spring shuts down within 30s
      # 30s buffer for unexpected delays
      terminationGracePeriodSeconds: 60
      containers:
      - name: order-service
        lifecycle:
          preStop:
            exec:
              # Wait for kube-proxy iptables propagation
              # Before SIGTERM is sent
              # Prevents new requests arriving to dying pod
              command: ["sleep", "5"]
        readinessProbe:
          httpGet:
            path: /actuator/health/readiness
            port: 8080
          # readiness DOWN -> pod removed from endpoints
          # This happens BEFORE SIGTERM
          # New requests stop before shutdown starts
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
COMPLETE GRACEFUL SHUTDOWN TIMELINE:

  T=0s: Kubernetes: kubectl delete pod order-service-pod
  T=0s: Pod status: Terminating
        Kubernetes: removes pod from Endpoints
        kube-proxy: updating iptables (takes 0-5s)
  T=0s: preStop hook: sleep 5 starts
  T=5s: preStop completes
        iptables: updated (pod no longer gets new traffic)
  T=5s: SIGTERM sent to Java process (PID 1)
  T=5s: Spring Boot: receives SIGTERM
        /actuator/health/readiness -> DOWN (503)
        Tomcat: stop accepting new HTTP connections
        Kafka consumer: stop polling new messages
  T=5s-35s: Processing in-flight requests/messages
        If all complete: Spring exits
        If timeout (30s) reached: forced exit
  T=35s: All connections closed
         Connection pools drained
         Metrics flushed (OTEL)
         Spring context closed (@PreDestroy called)
         JVM exits (status 0)
  T=35s: Pod exits
  Kubernetes: records exit; pod removed
  
  Users: ZERO errors during this entire window
  In-flight requests: all completed normally
  Kafka offsets: committed
  DB connections: returned to pool, pool closed
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: immediate vs graceful shutdown**

```java
// BAD: custom shutdown hook that kills immediately
// (overrides Spring's graceful shutdown)
@Configuration
public class ShutdownConfig {
    
    @PostConstruct
    public void registerShutdownHook() {
        Runtime.getRuntime().addShutdownHook(
            new Thread(() -> {
                // Kills thread pool immediately!
                // Overrides Spring's graceful shutdown!
                executorService.shutdownNow();
                log.info("Shutdown complete");
            }));
    }
}
// Problem: shutdownNow() interrupts running threads
// In-flight HTTP requests: dropped
// Kafka messages: not committed
// Overrides Spring Boot's graceful shutdown mechanism
```

```java
// GOOD: let Spring manage graceful shutdown
// application.yaml:
// server.shutdown: graceful
// spring.lifecycle.timeout-per-shutdown-phase: 30s

// If you MUST add custom cleanup:
@Component
@Slf4j
public class CustomShutdownHook
        implements SmartLifecycle {
    
    private volatile boolean running = false;
    
    @Override
    public void start() { this.running = true; }
    
    @Override
    public void stop() {
        // Spring calls this on shutdown
        // (in reverse order of phase)
        log.info("Custom cleanup starting");
        // cleanup work here
        this.running = false;
    }
    
    @Override public boolean isRunning() {
        return running;
    }
    
    @Override
    public int getPhase() {
        // Lower = earlier in shutdown
        // After HTTP stops (phase DEFAULT_PHASE)
        return Integer.MAX_VALUE - 1;
    }
}
// Spring: calls stop() on all SmartLifecycle beans
// in reverse phase order during shutdown
// HTTP: stops first (lower phase)
// Custom cleanup: stops after HTTP
```

---

### ⚖️ Comparison Table

| Aspect | No Graceful Shutdown | With Graceful Shutdown |
|---|---|---|
| **In-flight HTTP** | Dropped (TCP RST) | Completed normally |
| **Kafka messages** | Not committed (redelivered) | Committed; no redelivery |
| **DB connections** | Abandoned (pool exhausted) | Returned to pool cleanly |
| **Distributed transactions** | Potentially partially complete | Rolled back or completed |
| **User experience** | Error page/failed request | No visible impact |
| **Rolling update** | Errors during update | Zero errors |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| terminationGracePeriodSeconds is the application shutdown timeout | `terminationGracePeriodSeconds` is the KUBERNETES timeout: how long Kubernetes waits before sending SIGKILL. The APPLICATION's graceful shutdown timeout is configured separately (`spring.lifecycle.timeout-per-shutdown-phase`). Both must be configured: Spring's app timeout (30s) < Kubernetes timeout (60s). If Spring's timeout is not configured: Spring defaults to immediate shutdown despite Kubernetes waiting. If Kubernetes timeout < Spring's timeout: Kubernetes sends SIGKILL before Spring finishes, defeating graceful shutdown. |
| Spring Boot with server.shutdown=graceful handles Kafka automatically | Spring Boot graceful HTTP shutdown (server.shutdown=graceful) only handles the HTTP server. Kafka consumer shutdown is handled by Spring Kafka container separately. Spring Kafka DOES implement graceful shutdown by default (waits for current poll to complete), but you must verify: the current batch processing time < terminationGracePeriodSeconds. For long-processing Kafka messages (> 60s): implement checkpointing to allow safe interruption. |
| Graceful shutdown is only needed for HTTP services | Any service that does work must shut down gracefully: Kafka consumers (commit offsets), scheduled batch jobs (checkpoint current progress), Saga coordinators (handle in-flight sagas), connection pools (drain active connections before closing). Even background threads that periodically flush metrics or flush write-behind caches need graceful shutdown to avoid data loss on pod termination. |

---

### 🚨 Failure Modes & Diagnosis

**User reports: payment charged but order not created**

**Symptom:**
During rolling update of payment-service: 3
customers report they were charged but received
no order confirmation. Investigation: payment-service
payment records exist (payment_id=PAY-001, 002,
003). Order-service: no corresponding orders.

**Root Cause:**
payment-service: on receiving SIGTERM, immediately
killed in-flight Kafka publish (publishing
OrderPaymentConfirmed event to Kafka). Payment:
charged but event not published. Order-service:
never received the event; never created orders.

**Root Cause Detail:**
payment-service Dockerfile: `CMD java -jar app.jar`
But: `java` is NOT running as PID 1. The shell
(`sh -c`) is PID 1. SIGTERM goes to the shell.
Shell: forwards SIGTERM to Java? NO: shell doesn't
forward signals to child processes by default.
Java: receives NO signal. Kubernetes: after
terminationGracePeriodSeconds: sends SIGKILL.
Java: killed immediately, mid-publish.

**Fix:**
```dockerfile
# BAD: shell form (shell is PID 1, doesn't forward signals)
CMD java -jar app.jar

# GOOD: exec form (java is PID 1, receives SIGTERM directly)
CMD ["java", "-jar", "/app/order-service.jar"]
# OR:
ENTRYPOINT ["java", "-jar", "/app/order-service.jar"]
```

---

### 🔗 Related Keywords

**Enables this:**
- `Zero-Downtime Deployment` - graceful shutdown
  is one of three requirements for ZDD

**Benefits from this:**
- `Chaos Engineering` - chaos pod kills test
  graceful shutdown; if in-flight requests drop
  during kill: graceful shutdown not working

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STEPS        │ 1.Stop new requests 2.Finish in-flight  │
│              │ 3.Close connections 4.Flush 5.Exit       │
├──────────────┼───────────────────────────────────────────┤
│ SPRING BOOT  │ server.shutdown=graceful +                │
│              │ timeout-per-shutdown-phase=30s            │
├──────────────┼───────────────────────────────────────────┤
│ K8S          │ terminationGracePeriodSeconds: 60         │
│              │ preStop: sleep 5 (iptables race fix)      │
├──────────────┼───────────────────────────────────────────┤
│ CRITICAL     │ Dockerfile: use exec form ["java","-jar"]│
│              │ Not shell form (SIGTERM not forwarded)    │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Spring Boot: `server.shutdown=graceful` +
   `timeout-per-shutdown-phase=30s`. These two
   lines enable HTTP graceful shutdown.
2. Kubernetes: `terminationGracePeriodSeconds: 60`
   (> Spring's 30s) + `preStop: sleep 5` (iptables
   propagation).
3. Dockerfile: use exec form `["java", "-jar", ...]`
   not shell form `java -jar ...`. Shell form: JVM
   doesn't receive SIGTERM -> graceful shutdown fails.

**Interview one-liner:**
"Graceful shutdown: on SIGTERM, stop accepting new
requests, finish in-flight, close connections cleanly,
flush telemetry, exit. Spring Boot: server.shutdown=
graceful + timeout-per-shutdown-phase=30s. Kubernetes:
terminationGracePeriodSeconds:60 (> Spring's 30s) +
preStop:sleep 5 (wait for kube-proxy iptables update
before shutdown). Critical: Dockerfile must use exec
form [java,-jar,...] not shell form - shell doesn't
forward SIGTERM to JVM, so graceful shutdown never triggers."

---

### 💡 The Surprising Truth

The single most common reason graceful shutdown
fails silently (appears configured but doesn't
work): Dockerfile shell form vs exec form. Shell
form: `CMD java -jar app.jar` - the shell (`sh
-c`) is PID 1. Kubernetes sends SIGTERM to PID 1
(the shell). The shell receives it and exits
immediately without forwarding to the Java child
process. Java gets SIGKILL from Kubernetes after
the grace period. No graceful shutdown ever ran.
All those `server.shutdown=graceful` and
`terminationGracePeriodSeconds: 60` configurations:
completely ignored. Fix: exec form everywhere:
`CMD ["java", "-jar", "/app/service.jar"]`. Java
becomes PID 1 and receives SIGTERM directly.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **CONFIGURE** Write the complete Spring Boot
   + Kubernetes configuration for graceful shutdown:
   application.yaml (2 lines), Deployment spec
   (terminationGracePeriodSeconds + preStop + exec
   form Dockerfile command).
2. **VERIFY** How do you test that graceful shutdown
   is actually working? Write a test: send HTTP
   request that takes 15 seconds; mid-request,
   `kubectl delete pod`; verify request completes
   normally (not dropped).
3. **KAFKA** Explain what happens to a Kafka consumer
   during pod termination: (a) message currently
   being processed - does it complete? (b) are
   offsets committed before shutdown? (c) what
   if processing takes longer than terminationGracePeriodSeconds?
4. **SIGTERM** A developer reports: "Graceful
   shutdown doesn't work, pods die immediately."
   Walk through the 3 most likely causes and how
   to diagnose each one with `docker inspect` and
   `kubectl describe pod`.
5. **SMART LIFECYCLE** Explain the Spring
   SmartLifecycle interface: what is `getPhase()`,
   how are phases ordered during shutdown, and
   when would you implement it over `@PreDestroy`?

---

### 🧠 Think About This Before We Continue

**Q1.** Your payment-service processes Kafka messages.
Each message calls an external payment gateway
(which can take up to 45 seconds). Your
terminationGracePeriodSeconds is 60 and Spring's
shutdown timeout is 50 seconds. During pod termination:
a message processing starts at T=0; SIGTERM arrives
at T=40 (after preStop). Processing would take
45 more seconds (T=85). Kubernetes will SIGKILL
at T=60. What happens? Design a solution that
handles this case without data loss.

**Q2.** Your team runs 50 microservices in Kubernetes.
A junior developer runs `grep 'CMD java'` on all
Dockerfiles and finds that 30 of them use shell
form. They are concerned about graceful shutdown.
Prioritize: which services are highest risk for
graceful shutdown failure? Write a script to
automate fixing all Dockerfiles from shell form
to exec form.

**Q3.** During a chaos engineering experiment:
you kill a pod that is mid-processing an important
business transaction (money transfer). With
graceful shutdown: the transaction completes.
Without graceful shutdown: the transaction is
partially complete (money debited but not credited).
Design the complete solution for the case where
graceful shutdown timeout is exceeded (forced
SIGKILL): how do you detect, compensate, and
recover from the partially-complete transaction?