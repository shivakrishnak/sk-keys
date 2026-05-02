---
layout: default
title: "Stress Test"
parent: "Testing"
nav_order: 1139
permalink: /testing/stress-test/
number: "1139"
category: Testing
difficulty: ★★★
depends_on: Load Test, Performance Test, Observability
used_by: SRE, Capacity Planning, Chaos Engineering, Incident Prevention
related: Load Test, Soak Test, Chaos Test, Breaking Point, Autoscaling
tags:
  - testing
  - performance
  - resilience
  - sre
---

# 1139 — Stress Test

⚡ TL;DR — A stress test pushes a system beyond its expected maximum load until it fails, revealing where it breaks and how gracefully it degrades — answering "what is our actual limit, and do we fail safely?"

| #1139           | Category: Testing                                              | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------- | :-------------- |
| **Depends on:** | Load Test, Performance Test, Observability                     |                 |
| **Used by:**    | SRE, Capacity Planning, Chaos Engineering, Incident Prevention |                 |
| **Related:**    | Load Test, Soak Test, Chaos Test, Breaking Point, Autoscaling  |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You load-tested at 2,000 RPS (expected peak) — the system passes. Black Friday arrives, actual peak is 2,400 RPS (demand exceeded forecast). You have no idea: Does the system fail at 2,001 RPS? At 5,000 RPS? Does it fail gracefully (return 503 and recover) or catastrophically (cascade failure, data corruption, 30-minute recovery)? Without a stress test, you discover your failure mode in front of real users.

**THE BREAKING POINT:**
Load tests verify "can we handle expected maximum?" Stress tests answer "what ACTUALLY breaks, HOW does it break, and CAN WE RECOVER?" Systems under extreme stress exhibit failure modes invisible under normal load: thread pool exhaustion leads to queued requests building memory pressure; database deadlocks appear at high concurrency; the circuit breaker doesn't trip, causing cascade; autoscaling doesn't trigger fast enough.

**THE INVENTION MOMENT:**
Destructive testing (stress testing physical materials to failure) has been engineering practice for centuries. Applied to software: Amazon's GameDays (2004+), Netflix's Chaos Monkey (2010), and the SRE discipline formalised the concept of deliberately inducing failures to understand system limits before users discover them.

---

### 📘 Textbook Definition

A **stress test** is a type of performance test that increases load beyond the system's expected maximum capacity until it fails — or until a predetermined saturation point is reached. The goal is to: (1) find the **breaking point** (load level where acceptable performance degrades to unacceptable); (2) observe **failure mode** (does the system fail gracefully with error messages, or catastrophically?); (3) verify **recovery** (after stress is removed, does the system return to normal, or does it require intervention?). Stress tests answer: "How does our system break, and does it break safely?"

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Stress test = push past maximum until it breaks, observe HOW it breaks, verify it recovers.

**One analogy:**

> Material stress testing: engineers apply increasing force to a bridge beam until it breaks, observe the failure point, and examine whether it bends gracefully (ductile failure: warning before collapse) or shatters suddenly (brittle failure: no warning). Software stress tests look for the same: does your service degrade gracefully (shed load, return 503) or fail brittlely (deadlock, data corruption, unrecoverable state)?

**One insight:**
The most important outcome of a stress test is not the breaking point itself — it's the **failure mode**. A system that breaks at 3,000 RPS with clean 503 responses is far better than a system that breaks at 5,000 RPS with data corruption. You'd rather have a lower breaking point with graceful degradation than a higher breaking point with catastrophic failure.

---

### 🔩 First Principles Explanation

STRESS TEST PROTOCOL:

```
1. Establish baseline: run load test at expected peak (2,000 RPS) → confirm PASS
2. Increment load beyond peak in steps: +20% per step, hold 5 minutes each:
   2,000 RPS → 2,400 → 2,800 → 3,200 → 3,600 → 4,000 → ...

3. At each step, observe:
   - Latency: p99 rising → approaching saturation
   - Error rate: > 1% → entering degradation
   - Error type: 503 (capacity) vs 500 (logic) vs timeout vs crash
   - Resource utilization: CPU, memory, connections, thread pool

4. Record breaking point: first step where:
   - Error rate > 5%, OR
   - p99 > 5× baseline, OR
   - Service becomes unavailable

5. After breaking point:
   a. Ramp load back to normal
   b. Observe recovery: does system return to baseline latency?
   c. Check: memory leaked? Thread pool still exhausted? DB connections freed?

6. Document:
   - Breaking point: 3,200 RPS
   - Failure mode: DB connection pool exhausted → 503s returned cleanly
   - Recovery: 45 seconds to return to baseline after load removed
   - Recommendation: autoscaling threshold at 2,400 RPS (75% of breaking point)
```

GRACEFUL DEGRADATION PATTERNS:

```
Load shedding: when at capacity, reject new requests with 503 (Retry-After)
  → Users see error, can retry; server stays responsive for current load

Circuit breaker: when downstream fails, open circuit, return fallback
  → Users get cached/degraded response; server not overwhelmed by retries

Bulkhead: thread pool per service; one overwhelmed service can't flood main pool
  → Other services continue to work even when one is saturated

Backpressure: producer slows when consumer is full (reactive streams)
  → Flow control prevents unbounded queues
```

**THE TRADE-OFFS:**
**Gain:** Discovers real failure modes before production; enables capacity planning with safety margin; validates autoscaling; tests graceful degradation.
**Cost:** Requires dedicated environment (stress can damage or leave residual state); stress tests can cascade to dependent systems; time-consuming to design well.

---

### 🧪 Thought Experiment

DISCOVERING THE CASCADING FAILURE:

```
Stress test at 4,000 RPS (2× expected peak):
  t=0: 4,000 RPS applied
  t=30s: Service A database connection pool exhausted
  t=35s: Service A requests back up in thread pool (waiting for DB connections)
  t=40s: Service A thread pool exhausted (threads waiting for DB connections)
  t=45s: Service B (calls Service A) → requests hanging, timeouts after 30s
  t=75s: Service B thread pool exhausted (waiting for A's timeout)
  t=90s: Service C (calls B) → timeouts
  t=120s: Entire service mesh unavailable (cascading failure)

WITHOUT CIRCUIT BREAKERS: single point overwhelm → full cascade

With circuit breakers (stress test reveals they work):
  t=30s: DB pool exhausted
  t=35s: Service A circuit breaker opens → returns 503 immediately (no queuing)
  t=36s: Service B's circuit breaker opens → returns fallback response
  t=37s: Service C continues serving (with degraded B response)
  t=120s: Load reduced → circuit breakers close → system recovers in 10s

Stress test outcome: circuit breakers are correctly configured. ✓
```

---

### 🧠 Mental Model / Analogy

> A stress test is a **controlled demolition** with cameras at every structural joint. You apply increasing force, observe every joint's behavior, note when the first joint fails (breaking point), and observe whether the failure propagates (cascade) or is contained. The goal is NOT to see the building stand forever — it's to learn exactly how it fails so you can design better containment.

> Graceful degradation = the building loses its upper floors but the lower structure holds. Brittle failure = the building collapses all at once with no warning.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** A stress test pushes your app beyond its limits to see how it breaks. Does it tell users "too busy, try later" (good) or silently fail and corrupt data (bad)?

**Level 2:** Design stress test in incremental steps: 100% → 150% → 200% → ... of expected peak, each step held for 5 minutes. Record: at what load does error rate exceed 1%? After the test ends, reduce load and time how long the system takes to recover to baseline. Verify circuit breakers, load shedding, and autoscaling all trigger correctly under stress.

**Level 3:** Stress test infrastructure requirements: use the same hardware/Kubernetes node types as production (not a smaller staging environment). Ensure dependent services can handle the stress test load or mock them (stress testing your service vs. stress testing your dependencies are different goals). Monitor during stress test: DB slow query log, GC logs (JVM), connection pool metrics, thread pool queue depth. After stress test: check for resource leaks (compare memory/connection counts before and after).

**Level 4:** The SRE perspective on stress tests: the breaking point defines the **safety margin** = (breaking point - expected peak) / expected peak. A safety margin of 50% means you can absorb a 50% traffic surge above peak before hitting the breaking point. Safety margins should drive autoscaling triggers: if breaking point is 3,000 RPS, autoscaling should trigger at ~2,000 RPS (67% of breaking point) to ensure scale-out completes before saturation. Amazon's 10× traffic sizing rule: each service must handle 10× steady-state traffic. Derived from the distribution of traffic spikes: marketing emails, breaking news, viral social media posts can drive 5–10× normal traffic in minutes — before autoscaling can respond.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│               STRESS TEST INCREMENTAL LOADING            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Load (RPS)                    Metrics                  │
│  ┌───────┐                                              │
│  │ 2,000 │ Baseline ─────────── p99: 95ms, errors: 0%  │
│  │ 2,400 │ +20% ────────────── p99: 112ms, errors: 0%  │
│  │ 2,800 │ +40% ────────────── p99: 180ms, errors: 0.1%│
│  │ 3,200 │ +60% ────────────── p99: 620ms, errors: 2.1%│
│  │ 3,600 │ +80% ────────────── p99: 4200ms, errors: 12%│
│  │ 4,000 │ +100% ─────────────── Service unavailable   │
│  └───────┘                                              │
│                     ↑ BREAKING POINT: ~3,200 RPS        │
│                                                          │
│  Recovery:                                              │
│  Load reduced to 2,000 RPS                             │
│  t+0s: p99 still 800ms (queues draining)               │
│  t+45s: p99 back to 98ms ← RECOVERED                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Pre-release stress test for new search feature:
1. Load test: 2,000 RPS for 30min → PASS (p99: 95ms)
2. Stress test: ramp from 2,000 to 6,000 RPS in 4 steps

   Step 1: 2,500 RPS → p99: 120ms, errors: 0% ✓
   Step 2: 3,500 RPS → p99: 280ms, errors: 0.2% ✓
   Step 3: 4,500 RPS → p99: 850ms, errors: 3.8%
     ← search query timeout (Elasticsearch 30s timeout, no retry limit)
   Step 4: 5,500 RPS → p99: 8,000ms, errors: 45%
     ← Elasticsearch connection pool exhausted → stack overflow (bug!)

3. Breaking point: 4,500 RPS
4. Failure mode: Elasticsearch timeout without backpressure → thread pool fills
5. Recovery: manual Elasticsearch restart required (not automatic!)

6. Fixes:
   - Add circuit breaker to Elasticsearch client (open after 5 consecutive timeouts)
   - Limit concurrent ES connections with bulkhead (separate thread pool)
   - Add load shedding: reject search requests when p99 > 500ms

7. Re-run stress test:
   Breaking point: now 4,500 RPS (same)
   Failure mode: circuit breaker opens → 503 returned cleanly → app recovers in 10s
   Recovery: automatic, 10 seconds (vs. manual restart before)
   → PASS (graceful degradation verified)
```

---

### 💻 Code Example

```javascript
// k6 stress test with incremental stages
import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";

const errorRate = new Rate("error_rate");

export const options = {
  stages: [
    // Baseline
    { duration: "5m", target: 200 },
    { duration: "5m", target: 200 },
    // Stress phases (incremental)
    { duration: "3m", target: 300 },
    { duration: "5m", target: 300 },
    { duration: "3m", target: 400 },
    { duration: "5m", target: 400 },
    { duration: "3m", target: 600 },
    { duration: "5m", target: 600 },
    { duration: "3m", target: 800 },
    { duration: "5m", target: 800 },
    // Recovery phase: return to baseline
    { duration: "5m", target: 200 },
    { duration: "5m", target: 200 },
  ],
  // No hard thresholds — observe rather than fail
  // (Stress tests document behavior; they're not pass/fail gates)
};

export default function () {
  const res = http.get(`${__ENV.BASE_URL}/api/products/search?q=laptop`, {
    timeout: "10s",
  });

  errorRate.add(res.status >= 500 || res.status === 0);

  check(res, {
    "status ok or overloaded": (r) =>
      r.status === 200 || r.status === 503 || r.status === 429,
    "no unexpected errors": (r) => r.status !== 500, // 503 is expected, 500 is not
  });

  sleep(1 + Math.random() * 2);
}
```

Spring Boot load shedding with `RateLimiter`:

```java
@RestController
public class SearchController {
    private final RateLimiter rateLimiter = RateLimiter.create(500.0); // 500 RPS max
    private final SearchService searchService;

    @GetMapping("/api/products/search")
    public ResponseEntity<SearchResults> search(@RequestParam String q) {
        if (!rateLimiter.tryAcquire()) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                .header("Retry-After", "1")
                .body(null);  // Load shedding: reject excess requests with 503
        }
        return ResponseEntity.ok(searchService.search(q));
    }
}
```

---

### ⚖️ Comparison Table

| Type            | Load                    | Goal                               | Pass/Fail                 |
| --------------- | ----------------------- | ---------------------------------- | ------------------------- |
| Load Test       | Expected max            | Verify SLA met                     | Hard threshold            |
| **Stress Test** | Beyond max              | Find breaking point + failure mode | Observe (no hard fail)    |
| Soak Test       | 70% load, long duration | Detect resource leaks              | Resource growth threshold |
| Spike Test      | Sudden surge            | Verify autoscaling response        | Recovery time threshold   |

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                         |
| --------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| "Stress tests should have pass/fail criteria" | Stress tests document behavior; the outcome (failure mode) is the result — not a binary pass/fail               |
| "High breaking point = better"                | Breaking point matters less than failure mode; graceful degradation at 3,000 RPS > data corruption at 5,000 RPS |
| "Recovery is automatic"                       | Recovery must be TESTED — many systems require manual intervention after stress                                 |
| "Stress test and load test are the same"      | Load test: verify SLA at expected load; stress test: find limits beyond expected load                           |

---

### 🚨 Failure Modes & Diagnosis

**1. System Doesn't Recover After Stress Removed**

**Symptom:** Load reduced to normal, but error rate remains high; latency stays elevated.
Cause: Thread pool not draining (tasks still running); memory not GC'd (heap full); DB connections in bad state; circuit breaker not closing.
Diagnosis: Check thread pool queue depth, JVM heap, DB connection active count, circuit breaker state.
**Fix:** Implement health check that verifies recovery; circuit breaker `halfOpen` timeout; thread pool bounded queue (not unbounded).

**2. Cascading Failure to Dependent Services**

Cause: Stress test on Service A overflows its retry/timeout behavior → Service B (calls A) also overwhelmed.
**Prevention:** Use WireMock or mocks for downstream dependencies during stress tests (isolate the system under test). OR: deliberately include downstream services and verify circuit breakers contain the cascade.

---

### 🔗 Related Keywords

- **Prerequisites:** Load Test, Performance Test, Observability
- **Builds on:** Chaos Test, Circuit Breaker, Bulkhead, Autoscaling
- **Related:** Soak Test (duration), Spike Test (sudden surge)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Push beyond max load until failure;      │
│              │ observe HOW it fails; verify recovery     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Graceful failure mode > higher breaking  │
│              │ point; test recovery, not just breakage   │
├──────────────┼───────────────────────────────────────────┤
│ PROTOCOL     │ Incremental steps +20% past peak;        │
│              │ hold each step; observe; ramp down; time  │
│              │ recovery                                  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Controlled damage (test env) vs unknown  │
│              │ damage (production incident)             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Push until it breaks; ensure it breaks  │
│              │  gracefully and recovers automatically"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Chaos Test → Circuit Breaker → Bulkhead  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Netflix's Chaos Monkey randomly terminates production EC2 instances during business hours. This is effectively a stress test in production with a specific failure injection (instance death). Netflix found that by normalising chaos in production (small continuous failures), they build more resilient systems than companies that only experience failures during accidental outages. Compare Netflix's production chaos engineering to a pre-production stress test: (a) what class of failures does production chaos catch that staging stress tests miss (different traffic patterns, actual production data, real third-party API behavior), (b) what safety requirements must be in place before running production chaos (circuit breakers, graceful degradation verified, business hours only), and (c) why Netflix runs chaos during business hours (not nights/weekends) — what does this tell you about their confidence in their resilience?

**Q2.** The "thundering herd" problem occurs when many clients retry simultaneously after a service recovers from an outage. If 10,000 clients were waiting for a service that was down for 60 seconds, when it comes back online, all 10,000 clients retry at the same instant — creating a spike 10× normal load on a freshly restarted service, immediately overwhelming it again. This creates a second outage. Describe: (1) why retry-with-exponential-backoff alone doesn't solve this (all clients backed off to ~60s at the same time → all retry at t=60s together), (2) why full jitter (`sleep = random(0, cap * 2^attempt)`) does solve it (requests spread across the recovery window), (3) how Kubernetes `podDisruptionBudgets` and AWS ELB health check intervals interact with the thundering herd problem during pod restarts, and (4) the mathematical model for the expected spike factor as a function of retry window vs client count.
