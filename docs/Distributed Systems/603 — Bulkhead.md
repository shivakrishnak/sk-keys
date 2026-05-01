---
layout: default
title: "Bulkhead"
parent: "Distributed Systems"
nav_order: 603
permalink: /distributed-systems/bulkhead/
number: "603"
category: Distributed Systems
difficulty: ★★☆
depends_on: "Circuit Breaker, Failure Modes"
used_by: "Resilience4j, Hystrix, Istio, Thread Pool Executors"
tags: #intermediate, #distributed, #resilience, #isolation, #thread-safety
---

# 603 — Bulkhead

`#intermediate` `#distributed` `#resilience` `#isolation` `#thread-safety`

⚡ TL;DR — **Bulkhead** isolates resources (threads, connections, memory) for different services or operations so that one slow or failing consumer cannot exhaust shared resources and starve others — partitioning failure blast radius.

| #603            | Category: Distributed Systems                       | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------- | :-------------- |
| **Depends on:** | Circuit Breaker, Failure Modes                      |                 |
| **Used by:**    | Resilience4j, Hystrix, Istio, Thread Pool Executors |                 |

---

### 📘 Textbook Definition

**Bulkhead** (named after watertight compartments in ship hulls) is a resilience pattern that isolates resources consumed by different service calls, operations, or tenants so that failures or slowdowns in one partition cannot consume resources needed by another. In microservices: Service A calls both Service B (payment) and Service C (notifications). Without bulkhead: both share a single thread pool. If payment is slow: all 50 threads wait → notifications can't send either → complete A failure. With bulkhead: payment gets 10 threads, notifications get 10 threads, core operations get 30 threads. Payment slowdown: only payment's 10 threads affected. Notifications: still have their 10 threads. **Two implementations**: (1) **Thread Pool Bulkhead** — each service call runs in a dedicated thread pool; full isolation; thread-level overhead; suitable for CPU-bound operations. (2) **Semaphore Bulkhead** — uses a counting semaphore to limit concurrent calls; no new thread; same thread (lighter weight); suitable for reactive/async applications. Istio/Envoy: connection pool limits (maxConnections, http1MaxPendingRequests) = bulkhead at infrastructure level.

---

### 🟢 Simple Definition (Easy)

Ship hull has watertight compartments. If one compartment floods (a torpedo hits): only that compartment fills with water. Ship stays afloat. Without compartments: one hole → whole hull fills → ship sinks. Bulkhead in software: each service dependency gets its own "compartment" (thread pool or connection limit). If payment service is slow: only payment compartment fills (thread pool full). Order service still works. Notification service still works. The ship stays afloat.

---

### 🔵 Simple Definition (Elaborated)

Two bulkhead types in Resilience4j: ThreadPoolBulkhead (creates a dedicated ExecutorService for each service): actual thread isolation. Calls to service B run in pool B (10 threads). Calls to service C run in pool C (10 threads). They can't interfere. SemaphoreBulkhead (uses semaphore): limits max concurrent calls to a service. No new thread created. Caller thread itself executes, but only N at a time. Lighter. Good for non-blocking code. Pick ThreadPoolBulkhead: I/O-bound calls, need true isolation. Pick SemaphoreBulkhead: reactive / virtual thread workloads, low overhead.

---

### 🔩 First Principles Explanation

**Bulkhead mechanics and isolation strategies:**

```
PROBLEM: SHARED THREAD POOL FAILURE PROPAGATION

  Service A: 50-thread Tomcat thread pool. A calls B (payment) and C (notification).
  Normal: 10 concurrent payment calls (10 threads). 10 notification calls (10 threads).
          30 threads available for other operations.

  B degrades: response time 10s (normally 100ms).
    Payment calls: 10 threads waiting. Each new payment request: +1 thread waiting.
    After 50 requests (10s × 50 RPS): all 50 threads consumed waiting on payment.
    New request arrives (notification): no threads → 503. Notification fails!
    New health check: no threads → health probe times out → pod restarted!
    ALL functionality down because of payment service.

THREAD POOL BULKHEAD:

  Service A: still 50-thread main pool for incoming requests.
  Bulkhead: separate ExecutorService per downstream service.

  PaymentBulkhead: ThreadPoolExecutor(corePoolSize=10, maxPoolSize=10, queueCapacity=5).
  NotificationBulkhead: ThreadPoolExecutor(corePoolSize=10, maxPoolSize=10, queueCapacity=5).

  Incoming request (payment):
    - Main thread: submits task to PaymentBulkhead.
    - If PaymentBulkhead has available thread: task runs in payment thread.
    - If PaymentBulkhead full (10 running + 5 queued): BulkheadFullException.
    - Main thread: not blocked (returns immediately after submission).

  B degrades:
    PaymentBulkhead: 10 threads waiting on B. Queue: filling up.
    At 15 concurrent payment requests: BulkheadFullException for new payment requests.
    Main thread pool: unaffected. NotificationBulkhead: unaffected.
    Notification: still works. Health check: still works.

  TRADE-OFF:
    Extra threads: 10 (payment) + 10 (notification) = 20 extra threads per instance.
    Thread overhead: ~1MB stack per thread. 20 extra threads = ~20MB per instance.
    Context switching: more threads = more OS context switching.
    OK for I/O-bound (mostly waiting): CPU not wasted. Threads just sleep while I/O pending.
    Poor for CPU-bound: 20 idle threads still consume stack memory; lots of context switching.

SEMAPHORE BULKHEAD:

  Uses java.util.concurrent.Semaphore(permits=10).

  Incoming request (payment):
    - Same thread that received the request: acquires permit (semaphore.tryAcquire()).
    - Executes payment call on same thread.
    - Releases permit after completion.

  B degrades:
    10 threads concurrently calling B (each holding a permit).
    11th payment request: tryAcquire() → no permits → BulkheadFullException.
    Main thread pool: these 10 threads ARE from the main pool.

  KEY DIFFERENCE: Semaphore bulkhead uses the caller's thread.
    Thread pool bulkhead: submits to dedicated pool → main pool thread freed immediately.
    Semaphore bulkhead: main pool thread occupied until call completes.

  SEMAPHORE BULKHEAD STILL HELPS:
    Without bulkhead: all 50 threads can call B simultaneously. 50 threads stuck.
    With semaphore bulkhead: max 10 threads can call B. 40 threads free for other work.
    Still valuable — just less isolated than thread pool bulkhead.

  BEST FOR REACTIVE/VIRTUAL THREADS:
    Reactive (WebFlux): single event loop thread. Semaphore limits concurrent async operations.
    Virtual threads (Java 21+): millions of cheap threads. ThreadPoolBulkhead less meaningful.
                Semaphore still limits concurrency (prevents 10,000 concurrent B calls).

ISTIO/ENVOY BULKHEAD (INFRASTRUCTURE LEVEL):

  ConnectionPool settings in DestinationRule:

  apiVersion: networking.istio.io/v1alpha3
  kind: DestinationRule
  metadata:
    name: payment-service
  spec:
    host: payment-service
    trafficPolicy:
      connectionPool:
        tcp:
          maxConnections: 100       # Max TCP connections to payment-service pods.
        http:
          http1MaxPendingRequests: 50   # Max queued HTTP/1.1 requests.
          http2MaxRequests: 100         # Max concurrent HTTP/2 requests.
      outlierDetection:                 # Circuit breaker at mesh level.
        consecutive5xxErrors: 5
        interval: 30s
        baseEjectionTime: 30s

  If payment-service is slow → connections fill up → new requests: 503 immediately.
  Caller service: gets fast failure → can use its own fallback logic.
  Infrastructure-level: no code changes needed. But: no semantic knowledge (sees HTTP, not business logic).

COMBINING BULKHEAD + CIRCUIT BREAKER:

  Best practice: use both together.

  Execution order (Resilience4j decorator chain):
    Bulkhead → CircuitBreaker → TimeLimiter → remote call.

  Flow:
    1. Bulkhead: is there a slot available? No: BulkheadFullException (fast fail, shed load).
    2. CircuitBreaker: is circuit OPEN? Yes: CallNotPermittedException (fast fail).
    3. TimeLimiter: wrap in timeout. Exceeds time: TimeoutException (counts as CB failure).
    4. Remote call: actual HTTP/gRPC call to service.

  Failure propagation:
    B slow → TimeLimiter fires (timeout) → counts as CB failure.
    CB failure rate exceeded → CB OPENS → fast fail.
    Bulkhead: prevents more than N concurrent calls even while CB is deciding to open.

  Bulkhead alone: limits concurrency but doesn't fail fast. Threads still waiting.
  CircuitBreaker alone: fails fast after threshold. But during "deciding" phase: threads block.
  Together: bulkhead limits damage during CB measurement window. CB provides fast fail after threshold.

MULTI-TENANT BULKHEAD:

  SaaS app: shared service. Tenant A, Tenant B.
  Without bulkhead: Tenant A sends massive batch → 50 threads busy → Tenant B degraded.
  With per-tenant bulkhead:
    Tenant A: max 20 concurrent operations.
    Tenant B: max 20 concurrent operations.
    Premium Tenant C: max 40 concurrent operations.

  Implementation: dynamic semaphore per tenant-ID from JWT/header.
    Semaphore cache: ConcurrentHashMap<String, Semaphore>.
    Per request: tenantId = extractFromToken(request).
                 semaphore = cache.computeIfAbsent(tenantId, id -> new Semaphore(getLimit(id))).
                 semaphore.tryAcquire() or fail fast.
    Ensures: no tenant monopolises the service.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT bulkhead:

- Shared resources: one slow downstream exhausts threads/connections for all operations
- Blast radius: single service degradation → total service failure
- No tenant isolation: one abusive client degrades all other clients

WITH bulkhead:
→ Resource isolation: each service/tenant gets bounded resource allocation
→ Contained blast radius: slow payment affects only payment's allocation
→ Graceful degradation: core functionality available even when dependencies fail

---

### 🧠 Mental Model / Analogy

> Ship's watertight hull compartments. A torpedo hits compartment 3 — water floods only that compartment. The ship lists but stays afloat. Other compartments (engine room, crew quarters, bridge) remain dry. Without compartments: one hit → entire hull fills → ship sinks. The compartments don't prevent the torpedo hit — they contain its damage.

"Compartments" = thread pools or semaphore limits per downstream service
"Torpedo hit" = slow or failing downstream service call
"Ship staying afloat" = core service functionality remaining available despite dependency failure

---

### ⚙️ How It Works (Mechanism)

```
Resilience4j ThreadPoolBulkhead:

  Wraps: each async remote call in a dedicated ExecutorService.

  Call submitted → bulkhead pool:
    Pool has slot (running + queued < max): run in dedicated thread → return CompletableFuture.
    Pool full: throw BulkheadFullException immediately (no waiting).

Resilience4j SemaphoreBulkhead:

  Wraps: each synchronous call with semaphore acquire/release.

  Request arrives → tryAcquire(maxWaitDuration):
    Permit available: acquire → run on caller thread → release when done.
    No permit: throw BulkheadFullException (after maxWaitDuration, default 0s = immediate).
```

---

### 🔄 How It Connects (Mini-Map)

```
Failure Modes (shared resources as single point of cascading failure)
        │
        ▼
Bulkhead ◄──── (you are here)
(resource partitioning — limit blast radius per dependency/tenant)
        │
        ├── Circuit Breaker: complements bulkhead (CB: fail fast after threshold; bulkhead: limit concurrency)
        └── Retry with Backoff: retries work within bulkhead slots (retries consume slots)
```

---

### 💻 Code Example

**Resilience4j Semaphore Bulkhead:**

```java
// application.yaml:
resilience4j:
  bulkhead:
    instances:
      payment-service:
        maxConcurrentCalls: 10       # Max 10 concurrent calls to payment service
        maxWaitDuration: 0ms         # Don't wait if no slot: fail immediately
      notification-service:
        maxConcurrentCalls: 15
        maxWaitDuration: 100ms       # Wait up to 100ms for a slot

// Service:
@Service
public class OrderService {

    @Bulkhead(name = "payment-service", type = Bulkhead.Type.SEMAPHORE,
              fallbackMethod = "paymentFallback")
    public PaymentResult chargePayment(Order order) {
        return paymentClient.charge(order);
    }

    @Bulkhead(name = "notification-service", type = Bulkhead.Type.SEMAPHORE,
              fallbackMethod = "notificationFallback")
    public void sendConfirmation(Order order) {
        notificationClient.send(order);
    }

    // Payment full: queue the charge (async processing)
    public PaymentResult paymentFallback(Order order, BulkheadFullException e) {
        paymentQueue.enqueue(order);  // Queue for later retry
        return PaymentResult.queued(order.getId());
    }

    // Notification full: non-critical, just log
    public void notificationFallback(Order order, BulkheadFullException e) {
        log.warn("Notification bulkhead full for order {}. Skipping.", order.getId());
        // Non-critical: user will see order confirmed without email (send later via retry job)
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                      | Reality                                                                                                                                                                                                                                                                                                                                                                                                         |
| ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Bulkhead prevents failures in downstream services                  | Bulkhead prevents upstream resource exhaustion caused by downstream failures. It does NOT fix the downstream service. If payment is down: bulkhead limits how many of your threads wait on payment — but payment still fails. Bulkhead + circuit breaker together: CB stops calls to payment after threshold; bulkhead limits damage before CB trips                                                            |
| Thread pool bulkhead is always better than semaphore bulkhead      | Thread pool bulkhead provides better isolation (dedicated pool, main thread freed) but uses more resources (threads, memory) and adds latency (thread submission). Semaphore bulkhead is lighter and sufficient for reactive/non-blocking code. For Java 21 virtual threads: ThreadPoolBulkhead is less meaningful (virtual threads are cheap); semaphore bulkhead is the right tool                            |
| Bulkhead size should match expected concurrency                    | Bulkhead size should be slightly BELOW what the downstream service can handle safely, to provide back-pressure. If payment can handle 20 concurrent requests safely: set bulkhead to 15-18 (not 20). This ensures that even if payment is slow (response time doubles), the total concurrent requests don't exceed its safe limit. Bulkhead = rate limiting by concurrency, not just protection of the upstream |
| Istio connection pool settings replace application-level bulkheads | Istio connection pools operate at L4/L7 HTTP level — they limit connections and requests. Application-level bulkheads can also limit by business operation type (e.g., payment vs. order lookup) within the same HTTP connection pool. Both layers are complementary. Istio catches overload at the network level; application bulkhead gives finer semantic control                                            |

---

### 🔥 Pitfalls in Production

**Bulkhead too small — legitimate traffic rejected:**

```
SCENARIO: Payment service. SemaphoreBulkhead maxConcurrentCalls=5.
  Black Friday: 50 simultaneous checkout requests.
  Payment service: running fine (fast responses, <100ms).

  What happens:
    5 concurrent payment calls: in bulkhead. 45 remaining: BulkheadFullException.
    fallback: returns "Payment service unavailable."
    45 orders: NOT processed. Revenue lost. Black Friday disaster.

  Root cause: bulkhead too small for peak load. Payment service was fine!
  Bulkhead became the bottleneck, not the protecting mechanism.

BAD: Static undersized bulkhead:
  maxConcurrentCalls: 5  # Black Friday: checkout requests = 50 RPS × 0.1s = 5 concurrent (avg)
                          # But P99 response time = 2s → 50 × 2s = 100 concurrent at peak spike.

FIX 1: Size bulkhead based on peak concurrency, not average:
  # Little's Law: concurrent = RPS × response_time.
  # Peak RPS = 500, P99 response time = 0.5s.
  # Peak concurrent = 500 × 0.5 = 250.
  # Set maxConcurrentCalls = 250-300 (with small buffer above peak).
  maxConcurrentCalls: 250

FIX 2: Monitor and alert on bulkhead metrics:
  # Prometheus metric: resilience4j_bulkhead_available_concurrent_calls
  # Alert: available_concurrent_calls < 5 for > 30s → "bulkhead near capacity"
  # Alert: resilience4j_bulkhead_rejected_calls > 0 → "requests being shed"

  # Grafana dashboard: available_concurrent_calls over time.
  # Tune maxConcurrentCalls based on observed peak usage + 20% headroom.

FIX 3: ThreadPoolBulkhead with queue for spikes:
  resilience4j:
    thread-pool-bulkhead:
      instances:
        payment-service:
          maxThreadPoolSize: 20
          coreThreadPoolSize: 10
          queueCapacity: 50          # Queue up to 50 excess requests instead of rejecting.
          keepAliveDuration: 20ms
  # Queue absorbs brief spikes. Queue full → then BulkheadFullException.
```

---

### 🔗 Related Keywords

- `Circuit Breaker` — complements bulkhead: CB stops calls after failures; bulkhead limits concurrent slots
- `Retry with Backoff` — retries consume bulkhead slots (consider retry concurrency in sizing)
- `Timeout` — essential with bulkhead: prevents slots from being held indefinitely on slow calls
- `Fallback` — what to do when bulkhead is full (queue, cached response, error)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Partition resources per service/tenant.  │
│              │ Slow dependency: only its pool fills.    │
│              │ Other operations: unaffected.            │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple downstream dependencies that    │
│              │ can independently degrade; multi-tenant  │
│              │ isolation; preventing single-service     │
│              │ failures from causing total outage       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Only one downstream service (no benefit  │
│              │ from isolation); very low concurrency    │
│              │ where overhead isn't justified           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Ship compartments: one torpedo, one     │
│              │  flooded section — ship still sails."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Circuit Breaker → Retry with Backoff →  │
│              │ Timeout → Fallback → Resilience4j        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a service with a ThreadPoolBulkhead (pool=10, queue=20) for calls to Payment service. Payment service goes down. Over 30 seconds (30 RPS), all 30 calls fail after 10s timeout. How many threads are occupied at any given time? Does the queue fill up? At what point does the circuit breaker (failureRateThreshold=50%, minimumNumberOfCalls=10) trip open? After CB opens: what happens to the bulkhead threads?

**Q2.** Multi-tenant SaaS: you implement per-tenant semaphore bulkheads stored in a ConcurrentHashMap. A new tenant onboards and their first request creates a new semaphore. What happens if 10,000 tenants onboard in one hour — each creating a new Semaphore object? What is the memory/GC impact, and how would you bound the number of active semaphores (hint: consider LRU eviction or a different coordination mechanism)?
