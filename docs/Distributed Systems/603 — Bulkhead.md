---
layout: default
title: "Bulkhead"
parent: "Distributed Systems"
nav_order: 603
permalink: /distributed-systems/bulkhead/
number: "0603"
category: Distributed Systems
difficulty: ★★☆
depends_on: Circuit Breaker, Timeout, Thread Pool, Failure Modes
used_by: Hystrix, Resilience4j, Service Mesh, Graceful Degradation
related: Circuit Breaker, Retry with Backoff, Timeout, Fallback, Graceful Degradation
tags:
  - distributed
  - reliability
  - resilience
  - pattern
---

# 603 — Bulkhead

⚡ TL;DR — A bulkhead isolates different types of service calls into separate thread pools (or semaphores), so that if one downstream service exhausts its pool, it cannot consume threads meant for other services — preventing one slow dependency from taking down the entire application.

| #603            | Category: Distributed Systems                                                | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Circuit Breaker, Timeout, Thread Pool, Failure Modes                         |                 |
| **Used by:**    | Hystrix, Resilience4j, Service Mesh, Graceful Degradation                    |                 |
| **Related:**    | Circuit Breaker, Retry with Backoff, Timeout, Fallback, Graceful Degradation |                 |

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A service has one shared thread pool of 200 threads. It makes calls to three downstream services: Payment (fast, critical), Recommendation (slow, non-critical), and Search (medium). Recommendation service has a memory leak — it's now taking 60 seconds per call. All 200 threads are eventually consumed by Recommendation calls. Payment calls — which are fast and critical — cannot get a thread. The entire service is down because a non-critical, slow service consumed all the shared resources. One slow, non-critical dependency killed a healthy, business-critical path.

**THE INVENTION MOMENT:**
Shipbuilders divide a ship's hull into separate watertight compartments (bulkheads). If one compartment floods, it doesn't flood the entire ship. Apply this to software: divide the thread pool into separate compartments (one per downstream service). If the Recommendation pool fills up, the Payment pool is unaffected. Recommendation service problems cannot sink the entire ship.

---

### 📘 Textbook Definition

A **bulkhead** pattern partitions service resources (thread pools, connection pools, semaphores) by downstream dependency, limiting the blast radius of any single downstream failure. **Two implementations:**

1. **Thread Pool Bulkhead**: Each dependency gets its own thread pool. Calls to Dependency A use Pool-A; calls to Dependency B use Pool-B. Adds overhead of thread context switching; provides strong isolation. Best for: I/O-bound calls with variable latency.

2. **Semaphore Bulkhead**: Each dependency gets a semaphore with a maximum concurrency count. Calls must acquire the semaphore; if maxConcurrent is reached, calls are immediately rejected (no thread overhead). Best for: compute-bound operations or when thread-per-call is too expensive.

**Key parameters:** `max_concurrent_calls` (semaphore) or `max_thread_pool_size + max_wait_duration` (thread pool). **Rejection policy:** when capacity exceeded, either queue (with max queue depth) or reject immediately (fail-fast).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Bulkhead gives each downstream service its own resource quota — one service's slowness can only hurt that service's callers, not everyone else's.

**One analogy:**

> A hospital emergency room uses bulkheads: different waiting rooms for Orthopedics, Cardiology, and General. If the General queue fills up (flu season), Cardiology's queue is still open for urgent heart patients. Without bulkheads: one room for everyone — chest pain patients wait 4 hours because flu patients filled all the chairs.

**One insight:**
The bulkhead doesn't make slow services faster — it prevents resource starvation from propagating. The downstream service is still slow; but its slowness is contained within its dedicated pool. This is why bulkhead and circuit breaker are complementary: bulkhead limits blast radius; circuit breaker stops ongoing calls once the failure is detected.

---

### 🔩 First Principles Explanation

**THREAD POOL BULKHEAD (HYSTRIX MODEL):**

```
Shared Pool (NO BULKHEAD):
  Thread Pool: [████████████████████] (200 threads)
  Payment calls: takes threads from shared pool
  Recommendation calls: takes threads from shared pool
  Search calls: takes threads from shared pool

  Recommendation goes slow (60s/call):
  [RECC RECC RECC RECC RECC RECC ... RECC] ← 200 Recommendation threads
  [WAIT WAIT WAIT WAIT] ← Payment threads cannot get a slot → 503 errors

Thread Pool Bulkhead (WITH BULKHEAD):
  Pool A - Payment:        [██████] (20 threads max)
  Pool B - Recommendation: [████]   (10 threads max)
  Pool C - Search:         [██████████] (50 threads max)

  Recommendation goes slow (60s/call):
  Pool B - Recommendation: [FULL FULL FULL ... FULL] ← 10 threads full
  Pool A - Payment:        [██ ██] ← unaffected. Payment works fine!

  Recommendation callers get RejectedExecutionException from Pool B.
  Payment callers continue to be served from Pool A.
```

**SEMAPHORE BULKHEAD (RESILIENCE4J):**

```java
BulkheadConfig config = BulkheadConfig.custom()
    .maxConcurrentCalls(25)          // max concurrent calls allowed
    .maxWaitDuration(Duration.ofMillis(500))  // wait 500ms for a slot
    .build();

Bulkhead recommendationBulkhead = BulkheadRegistry.of(config)
    .bulkhead("recommendation-service");

Supplier<List<Product>> decoratedCall = Bulkhead.decorateSupplier(
    recommendationBulkhead, () -> recommendationService.getRecommendations(userId));

Try.ofSupplier(decoratedCall)
    .recover(BulkheadFullException.class, ex -> Collections.emptyList()); // fallback
```

**THREAD POOL vs SEMAPHORE COMPARISON:**

```
Thread Pool Bulkhead:
  ✅ True async: calling thread released immediately; downstream call runs on worker thread
  ✅ Works with synchronized/blocking code
  ❌ Thread context switching overhead
  ❌ ThreadLocal propagation issues (security context, MDC logging)
  Use when: calling external HTTP services, DB calls (I/O bound)

Semaphore Bulkhead:
  ✅ Low overhead (no thread switching)
  ✅ ThreadLocal context propagates correctly
  ✅ Works with reactive stacks (Project Reactor, RxJava)
  ❌ Blocking: if all 25 semaphore slots are busy, caller thread blocks (or rejects)
  Use when: in-process calls, reactive/non-blocking I/O, high-throughput internal methods
```

---

### 🧪 Thought Experiment

**SIZING THE BULKHEAD:**

Service A makes calls to Payment (1ms avg), Recommendation (500ms avg), Search (50ms avg).
Service A handles 100 requests/second. Each request calls all three services sequentially.

**Little's Law: L = λ × W (queue depth = throughput × latency)**

- Payment: L = 100 req/s × 0.001s = **0.1 concurrent calls** → pool size: 2 (headroom)
- Recommendation: L = 100 req/s × 0.5s = **50 concurrent calls** → pool size: 60
- Search: L = 100 req/s × 0.05s = **5 concurrent calls** → pool size: 10

If Recommendation goes from 500ms to 5 seconds under load:

- Recommendation: L = 100 × 5 = 500 concurrent → ALL 60 slots full in < 1s → rejection!
- Payment remains unaffected: its pool never gets touched.

**Key insight:** Size bulkhead pools based on `Little's Law` (throughput × latency) plus headroom. When actual latency exceeds design parameters, the pool fills and starts rejecting — exactly what you want. The bulkhead limits the blast radius to the Recommendation callers; Payment is untouched.

---

### 🧠 Mental Model / Analogy

> Bulkhead is like a ship's watertight compartments. The Titanic had compartments but they weren't tall enough — water flowed over the top when the bow tilted. Similarly, without proper sizing, a bulkhead that's too small gets overwhelmed and the rejection propagates upward (load-shedding from the full pool). The key is: right-size the bulkhead so normal load fits, and excess load at the boundary is rejected cleanly rather than overflowing into other pools.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Bulkhead: give each downstream service its own resource quota. If one fills up, it can't take resources from others. Prevents one slow service from breaking everything else.

**Level 2:** Thread pool bulkhead (async, overhead) vs. semaphore bulkhead (low overhead, blocking). Size using Little's Law: pool_size = throughput × expected_latency + headroom. Combine with circuit breaker: circuit breaker stops ongoing calls; bulkhead contains blast radius.

**Level 3:** Resilience4j: `BulkheadConfig.maxConcurrentCalls`. Hystrix: `HystrixThreadPoolKey`. Rejection policy: queue (with depth limit) or immediate reject. Queue adds latency under load; immediate reject gives back-pressure faster. Reactive bulkheads use semaphore model (non-blocking, virtual thread-compatible).

**Level 4:** For microservice architectures: bulkheads should align with SLA boundaries. Critical paths (payment) get dedicated pools with large headroom. Non-critical paths (recommendations) get smaller pools with aggressive rejection. This embeds priority into resource allocation without explicit priority queues. Service mesh Istio implements bulkheads via `destinationRule.trafficPolicy.connectionPool.http.http1MaxPendingRequests` and `http2MaxRequests` — applied at the sidecar proxy level without application code changes. JVM thread pools have overhead: prefer semaphore bulkheads with virtual threads (Java 21 Project Loom) for extremely high concurrency, as virtual threads eliminate the thread-per-call cost that makes thread pool bulkheads expensive.

---

### ⚙️ How It Works (Mechanism)

**Thread Pool Bulkhead with Spring Cloud + Resilience4j:**

```java
@Service
public class RecommendationService {

    private final ThreadPoolBulkhead bulkhead;
    private final RecommendationClient client;

    public RecommendationService(RecommendationClient client) {
        this.client = client;
        ThreadPoolBulkheadConfig config = ThreadPoolBulkheadConfig.custom()
            .maxThreadPoolSize(10)
            .coreThreadPoolSize(5)
            .queueCapacity(20)
            .keepAliveDuration(Duration.ofMillis(20))
            .build();
        this.bulkhead = ThreadPoolBulkheadRegistry.of(config)
            .bulkhead("recommendation");
    }

    public CompletableFuture<List<Product>> getRecommendations(String userId) {
        return ThreadPoolBulkhead.decorateSupplier(bulkhead,
            () -> client.fetchRecommendations(userId))
            .get()  // returns CompletableFuture
            .exceptionally(ex -> Collections.emptyList()); // fallback
    }
}
```

---

### ⚖️ Comparison Table

| Pattern         | What It Isolates                      | Prevents                      | Limitation                                |
| --------------- | ------------------------------------- | ----------------------------- | ----------------------------------------- |
| Bulkhead        | Thread/semaphore pools per dependency | Resource starvation cascade   | Doesn't reduce # of failed calls          |
| Circuit Breaker | Call attempts (open = no calls)       | Ongoing failure amplification | Doesn't prevent initial thread exhaustion |
| Rate Limiter    | Calls per unit time                   | Overloading downstream        | Doesn't isolate pools                     |
| Timeout         | Per-call duration                     | Indefinite blocking           | Doesn't isolate pools                     |

---

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                                        |
| -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Bulkhead makes a slow service faster                           | No — it only prevents the slow service from starving resources for healthy services                                                            |
| A large shared thread pool is better than many small bulkheads | Large shared pool is more efficient under balanced load, but offers zero isolation. Under imbalanced load, a large shared pool is catastrophic |
| Circuit breaker and bulkhead do the same thing                 | Circuit breaker: stops calling the failing service. Bulkhead: limits resources available to each service. Complementary, not redundant         |

---

### 🚨 Failure Modes & Diagnosis

**Bulkhead Sized Too Small — Legitimate Traffic Rejected**

Symptom: Recommendation API returns 503 errors during normal traffic. Metrics show
`bulkhead.recommendation.rejected_calls` increasing during business hours.

Cause: Thread pool max size (10) is insufficient for actual concurrency during peak.
Little's Law: expected 15 concurrent calls at p99 latency, but pool is 10.

Fix: Recalculate pool size using production traffic metrics. Set pool = p99_concurrent_calls
× 1.5 safety factor. Set queue depth = 2 × pool_size. Monitor
`bulkhead.recommendation.available_concurrent_calls` — alert if < 25% free at p99 load.

---

### 🔗 Related Keywords

- `Circuit Breaker` — stops calling a failing service; bulkhead limits its resource usage
- `Timeout` — bounds the time each call in the pool can occupy a thread
- `Fallback` — what to do when the bulkhead rejects a call
- `Graceful Degradation` — the business-level strategy that bulkheads enable
- `Retry with Backoff` — works inside the bulkhead for transient failures

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  BULKHEAD: separate resource pools per dependency        │
│  Thread Pool: async, overhead, strong isolation          │
│  Semaphore: low overhead, blocking, no thread switch     │
│  Size with Little's Law: L = λ × W (+ safety factor)    │
│  On pool full: reject fast (back-pressure)               │
│  Combine with: Circuit Breaker + Timeout + Fallback      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Service A processes user requests calling three services: Auth (5ms), Inventory (200ms), and Analytics (2000ms). Throughput: 50 req/s. Analytics goes from 2000ms to 30000ms avg latency. Calculate the required bulkhead pool size for each service using Little's Law. If you had not implemented bulkheads and were using a shared pool of 200 threads, how many seconds until the entire pool is consumed by Analytics calls?

**Q2.** You implement a semaphore bulkhead (`maxConcurrentCalls=25`) for calls to a payment gateway from a reactive (Project Reactor) application. Under load, the circuit breaker opens because 26+ calls are in-flight which overflows the semaphore and causes rejections, which count as failures. Is this expected behavior? Explain the interaction between the semaphore bulkhead, the circuit breaker, and the failure rate threshold. Should semaphore rejections count as failures in the circuit breaker's failure rate calculation?
