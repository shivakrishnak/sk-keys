---
layout: default
title: "Stress Test"
parent: "Testing"
nav_order: 1139
permalink: /testing/stress-test/
number: "1139"
category: Testing
difficulty: ★★★
depends_on: "Load Test, Performance Test"
used_by: "Capacity planning, breaking point analysis, resilience engineering"
tags: #testing, #stress-test, #breaking-point, #capacity, #resilience, #saturation
---

# 1139 — Stress Test

`#testing` `#stress-test` `#breaking-point` `#capacity` `#resilience` `#saturation`

⚡ TL;DR — **Stress testing** pushes a system beyond its expected capacity to find its breaking point and observe failure behavior. Unlike load tests (which validate normal conditions), stress tests deliberately overload the system. Goals: find maximum capacity, observe how the system fails (gracefully or catastrophically), verify it recovers after load drops. A system under stress should degrade gracefully (return 503, reject new work) rather than crash or corrupt data.

| #1139           | Category: Testing                                                  | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------- | :-------------- |
| **Depends on:** | Load Test, Performance Test                                        |                 |
| **Used by:**    | Capacity planning, breaking point analysis, resilience engineering |                 |

---

### 📘 Textbook Definition

**Stress test**: a performance test that applies load beyond the system's expected capacity to: (1) determine the maximum throughput the system can sustain; (2) observe failure behavior — does the system fail gracefully (return errors, drop excess requests) or catastrophically (crash, deadlock, corrupt data)? (3) verify recovery — when load drops back to normal, does the system recover automatically and quickly? (4) find resource exhaustion boundaries (connection pool full, memory exhausted, CPU at 100%). Stress test types: (a) **Increasing load stress**: gradually increase VUs/RPS until the system breaks — identify the "knee of the curve" where latency explodes; (b) **Spike stress**: sudden extreme load increase (simulating DDoS, viral traffic) — does the system survive or crash? (c) **Memory stress**: sustained load at high concurrency to find memory leaks — does memory grow indefinitely? (d) **Resource exhaustion**: saturate specific resources (database connections, file descriptors, thread pool) to observe behavior at limits. Key observations: (1) At what RPS/VUs does latency start increasing sharply? (2) Does the system return 429/503 errors gracefully or return 500 (unexpected errors)? (3) Does the system recover within minutes of load dropping, or does it need a restart? (4) Are there any data integrity issues under extreme load (duplicate orders, lost writes)?

---

### 🟢 Simple Definition (Easy)

Load test checks if the system handles normal traffic. Stress test checks what happens when traffic goes crazy — 10x, 50x normal load. Does the server crash? Does it start returning errors gracefully? Does it recover when the traffic drops? You want to know the answers to these questions in a test environment, not during a viral Reddit post or a DDoS attack.

---

### 🔵 Simple Definition (Elaborated)

Stress tests deliberately break the system to understand its failure mode. There are two types of failure:

1. **Graceful degradation**: system returns 503 Service Unavailable, rate-limits excess requests, queues work — users experience slowness or retry-able errors, but no data is lost
2. **Catastrophic failure**: system crashes, deadlocks, corrupts data, or silently drops requests — much worse

A well-designed system under extreme stress should:

- Return `503 Service Unavailable` or `429 Too Many Requests` to excess requests
- Keep serving existing requests (even if slowly)
- Not corrupt or lose data
- Recover automatically when load drops (no manual restart needed)

**What stress tests reveal**:

- **Connection pool exhaustion**: when DB connections run out, requests hang indefinitely (no timeout configured)
- **Thread pool saturation**: executor queue fills up, `RejectedExecutionException` thrown — is it caught and returned as 503, or does it bubble up as 500?
- **Memory leak under load**: heap grows under high concurrency, eventually causing OOM crash
- **Cascading failure**: Service A is slow → Service B waits → Service B thread pool fills up → Service B crashes → Service C loses all calls to B

---

### 🔩 First Principles Explanation

```javascript
// K6 STRESS TEST: find breaking point by gradually increasing load

import http from "k6/http";
import { check } from "k6";
import { Rate } from "k6/metrics";

const errorRate = new Rate("errors");

export const options = {
  // INCREASING LOAD STRESS PROFILE: keep adding VUs until system breaks
  stages: [
    { duration: "2m", target: 100 }, // normal load (baseline)
    { duration: "5m", target: 100 }, // hold normal load
    { duration: "2m", target: 500 }, // 5x load
    { duration: "5m", target: 500 }, // hold 5x load
    { duration: "2m", target: 1000 }, // 10x load
    { duration: "5m", target: 1000 }, // hold 10x load → usually where systems break
    { duration: "2m", target: 2000 }, // 20x load (extreme)
    { duration: "5m", target: 2000 }, // hold extreme load
    { duration: "5m", target: 0 }, // RECOVERY: ramp down
    { duration: "5m", target: 100 }, // hold normal load post-stress
    // Watch: does it recover to normal latency? Or stay degraded?
  ],

  // Thresholds are NOT used for pass/fail in stress tests
  // (the system is expected to fail at high load — that's the point)
  // Instead: record metrics at each stage and analyze the curve
};

export default function () {
  const resp = http.get("/api/products", { timeout: "10s" });

  const passed = check(resp, {
    "status 200": (r) => r.status === 200,
    "status 503 (graceful)": (r) => r.status === 503, // 503 is ACCEPTABLE under stress
    "NOT status 500": (r) => r.status !== 500, // 500 is NOT acceptable (bug)
  });

  errorRate.add(!passed);
}
```

```java
// STRESS TEST OBSERVATIONS AND ANALYSIS

// What to look for in stress test results:
//
//  VUs    | RPS     | p99    | Error Rate | CPU | Memory
// ─────────────────────────────────────────────────────────
//  100    | 250/s   | 45ms   | 0.0%       | 15% | 2.1 GB  ← baseline
//  500    | 1,000/s | 89ms   | 0.0%       | 45% | 2.3 GB  ← good
//  1,000  | 1,800/s | 420ms  | 0.2%       | 78% | 2.8 GB  ← warning
//  2,000  | 2,100/s | 3,400ms| 12%        | 95% | 3.9 GB  ← KNEE OF THE CURVE
//  3,000  | 2,050/s | 8,900ms| 45%        | 99% | 4.2 GB  ← SATURATED
//
// OBSERVATIONS:
// 1. RPS plateaus at ~2,100/s (max throughput) despite more VUs — CPU bound
// 2. Latency explodes at 2,000 VUs (the "knee") — requests queuing
// 3. Error rate starts at 2,000 VUs — DB connection pool exhausted
// 4. CPU reaches 99% — need either horizontal scaling or code optimization
//
// ERRORS at 2,000+ VUs:
// - 80% are 503 (from circuit breaker) → graceful ✓
// - 15% are 504 Gateway Timeout → acceptable ✓
// - 5% are 500 (NullPointerException in CartService) → BUG! ✗
//   → unhandled concurrent modification of shopping cart
//   → FIX: add ConcurrentHashMap or synchronization
//
// RECOVERY TEST (after ramp-down to 100 VUs):
// - Latency returned to 45ms within 2 minutes ✓
// - Memory GC'd back to 2.1 GB within 5 minutes ✓
// - No manual restart needed ✓

// THREAD POOL TUNING (common stress test finding):

// Before (default settings — breaks at 200 concurrent requests):
@Bean
public TaskExecutor taskExecutor() {
    return new SimpleAsyncTaskExecutor();  // unbounded — memory exhaustion
}

// After (tuned based on stress test findings):
@Bean
public ThreadPoolTaskExecutor taskExecutor() {
    ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
    executor.setCorePoolSize(50);
    executor.setMaxPoolSize(200);
    executor.setQueueCapacity(500);
    executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
    // CallerRunsPolicy: when queue full, caller thread executes the task
    // This provides natural back-pressure instead of throwing exception
    executor.setThreadNamePrefix("async-");
    executor.initialize();
    return executor;
}
```

```
STRESS TEST CHECKLIST: What to verify under extreme load

  GRACEFUL DEGRADATION:
  ✓ Returns 503/429 when overloaded (not 500)
  ✓ Existing requests complete (not aborted)
  ✓ Circuit breakers open (prevent cascading failure)
  ✓ Load shedding: new requests rejected with Retry-After header

  DATA INTEGRITY:
  ✓ No duplicate writes under high concurrency
  ✓ No lost writes (request accepted but not persisted)
  ✓ Transaction isolation maintained (no dirty reads)
  ✓ Database constraints respected under concurrent inserts

  RECOVERY:
  ✓ Latency returns to normal within 5 minutes of load drop
  ✓ Memory GC'd back to baseline (no permanent leak)
  ✓ No manual restart required
  ✓ Connection pools drained and reset correctly

  ALARMS:
  ✓ PagerDuty alert fired when error rate > 1%
  ✓ Auto-scaling triggered at appropriate CPU threshold
  ✓ Circuit breaker alerts fired at correct thresholds
```

---

### ❓ Why Does This Exist (Why Before What)

Load tests verify normal conditions. But production traffic is not always normal: viral content, DDoS attacks, botnet traffic, the Hacker News effect, coordinated sales events. Understanding the system's breaking point and failure mode before it's triggered by real events allows engineers to: (1) set meaningful auto-scaling thresholds; (2) configure circuit breakers and load shedding; (3) fix graceful degradation before it matters; (4) capacity plan for worst-case scenarios. A system that crashes catastrophically under 2x load is dangerous; a system that gracefully returns 503 at 2x load and recovers at 1x load is resilient.

---

### 🧠 Mental Model / Analogy

> **Stress tests are like structural load tests in civil engineering**: before a building is opened, structural engineers apply loads beyond the design specification to find the safety margin and observe failure mode. Will the beam buckle slowly and visibly (graceful failure with warning signs) or will it snap suddenly without warning (catastrophic failure)? They want to know the safety margin AND the failure mode. Software stress tests answer the same questions: what is the safety margin above expected load, and when the system does fail, does it fail gracefully or catastrophically?

---

### 🔄 How It Connects (Mini-Map)

```
Load test passes → now push beyond capacity to find breaking point and failure mode
        │
        ▼
Stress Test ◄── (you are here)
(beyond capacity; find breaking point; verify graceful degradation; test recovery)
        │
        ├── Load Test: prerequisite — run load test first to establish baseline
        ├── Performance Test: stress test is a subtype of performance testing
        ├── Chaos Test: stress test focuses on load; chaos test on infrastructure failures
        └── Capacity Planning: stress test results define safe operating limits
```

---

### 💻 Code Example

```java
// CIRCUIT BREAKER: prevents cascading failure under stress
// When downstream service is overwhelmed, circuit opens → fast fail → system stable

@Service
public class InventoryServiceClient {

    // Resilience4j circuit breaker
    private final CircuitBreaker circuitBreaker = CircuitBreaker.ofDefaults("inventory");

    public InventoryResponse checkStock(String productId) {
        // Under normal load: calls real inventory service
        // Under stress: if >50% of calls fail in 60s → circuit OPENS
        // While open: all calls fail fast (return fallback immediately)
        // After 30s: circuit HALF-OPENS (try 1 real call; if OK, close circuit)

        return circuitBreaker.executeSupplier(() ->
            inventoryHttpClient.get("/inventory/" + productId)
        );
    }

    // FALLBACK: when circuit is open, serve degraded response
    @Recover
    public InventoryResponse fallback(String productId, CallNotPermittedException ex) {
        // Return "available=true" to avoid blocking checkout
        // Better to occasionally oversell than to block all purchases
        log.warn("Inventory circuit open for {}; assuming available", productId);
        return new InventoryResponse(productId, true, -1); // -1 = unknown stock
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                                                                                                                                                                                                                                                                                               |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Stress tests should pass                     | Stress tests are DESIGNED to push the system until it fails — the goal is to observe HOW it fails. A stress test where the system "passes" at 50x normal load just means you haven't found the breaking point yet (increase load further). The stress test is useful when it reveals: the breaking point, the failure mode, the safety margin above expected load, and the recovery behavior.         |
| A system that crashes under stress is broken | A system under 50x normal load crashing is expected and often acceptable — if it crashes gracefully (returns 503, recovers automatically, loses no data). The failure mode matters more than the fact of failure. A system that returns 503 under 10x load and recovers in 2 minutes is better than one that corrupts data at 3x load. Stress tests help you understand and accept the failure modes. |
| Stress tests and load tests are the same     | Distinct purposes: load test → "does it meet SLO at expected load?"; stress test → "what happens beyond expected load?" Load tests have pass/fail criteria (SLO thresholds). Stress tests explore behavior — the "failure" at high load is expected; what's being validated is HOW it fails and whether it recovers.                                                                                  |

---

### 🔗 Related Keywords

- `Load Test` — prerequisite to stress test; validates normal conditions first
- `Performance Test` — stress test is a subtype of performance testing
- `Chaos Test` — complements stress test; chaos tests infrastructure failures, not load
- `Circuit Breaker` — key resilience pattern validated by stress tests
- `Capacity Planning` — stress test results define safe operating bounds

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STRESS TEST = push beyond capacity → find breaking pt  │
│                                                          │
│ GOALS:                                                  │
│  1. Find max sustainable throughput                    │
│  2. Observe failure mode (graceful vs catastrophic)    │
│  3. Verify recovery after load drops                   │
│  4. Identify resource exhaustion boundaries            │
│                                                          │
│ GOOD FAILURE: returns 503, recovers automatically      │
│ BAD FAILURE: crashes, corrupts data, needs restart     │
│                                                          │
│ LOAD PROFILE: ramp up until failure + recovery test    │
│ KEY: find the "knee of the curve"                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Memory stress testing targets a specific failure mode: memory leaks under sustained load. A Java service might look stable for 30 minutes but show gradually increasing heap usage over 4 hours (a soak/endurance test). Common causes: thread-local variables not cleared after request; stateful objects accumulated in static maps; event listeners registered but never unregistered; JDBC ResultSet not closed in all code paths. Design a soak test strategy: what load level should you apply (100% of expected peak, or 80%)? How long should you run it (2 hours? 8 hours? 24 hours)? What metrics should trigger an alert? How do you analyze heap dumps to find the leak source?

**Q2.** Stress tests reveal the system's behavior at limits, but production surprises differ from controlled stress tests. In production, extreme load often comes from: botnet traffic with unusual request patterns; a bug in client code causing request storms (a mobile app bug that retries every 100ms instead of using exponential backoff); database slow query causing all threads to pile up (not CPU-bound but I/O-wait-bound). The stress test simulated CPU-bound load; the production incident was I/O-wait-bound. How do you design stress tests that cover multiple failure modes: CPU saturation, I/O saturation, connection pool exhaustion, memory exhaustion, and downstream service failures — without making the test infrastructure prohibitively complex?
