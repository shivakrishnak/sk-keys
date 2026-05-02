---
layout: default
title: "Load Test"
parent: "Testing"
nav_order: 1138
permalink: /testing/load-test/
number: "1138"
category: Testing
difficulty: ★★☆
depends_on: "Performance Test"
used_by: "Stress Test, Spike Test, capacity planning, SLO validation"
tags: #testing, #load-test, #throughput, #rps, #virtual-users, #k6, #gatling
---

# 1138 — Load Test

`#testing` `#load-test` `#throughput` `#rps` `#virtual-users` `#k6` `#gatling`

⚡ TL;DR — **Load testing** validates that a system performs correctly under **expected production load**. Unlike stress tests (which push beyond limits), load tests simulate realistic user volumes and verify that SLOs (response time, error rate) are met. Key metrics: throughput (RPS), latency percentiles (p95, p99), error rate. Tools: k6, Gatling, JMeter. Always run in a production-equivalent environment.

| #1138           | Category: Testing                                          | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------- | :-------------- |
| **Depends on:** | Performance Test                                           |                 |
| **Used by:**    | Stress Test, Spike Test, capacity planning, SLO validation |                 |

---

### 📘 Textbook Definition

**Load test**: a type of performance test that applies a specific, expected level of load (user traffic, request rate, data volume) to a system and measures whether it meets its performance requirements (SLOs/SLAs). Load tests model realistic user behavior: concurrent virtual users, think times, realistic request mixes (80% reads, 20% writes). The goal is to verify: (1) the system handles expected peak load without violating SLOs; (2) resources (CPU, memory, database connections) are within expected bounds; (3) no memory leaks or resource exhaustion under sustained load. Load test phases: (a) **ramp-up**: gradually increase load from 0 to target (avoids cold-start artifacts); (b) **steady state**: maintain target load for 10-30 minutes (expose steady-state behavior); (c) **ramp-down**: gradually decrease load (observe graceful degradation). Load test targets come from: production traffic analysis (p95 concurrent users, peak RPS from access logs), capacity requirements (support 10x current users), SLO definitions (must serve 1,000 RPS at p99 < 500ms). Tools: **k6** (JavaScript, cloud-native, excellent CI integration), **Gatling** (Scala DSL, detailed HTML reports), **Apache JMeter** (GUI, enterprise, mature), **Locust** (Python, extensible). Critical: load tests in non-production-equivalent environments are misleading.

---

### 🟢 Simple Definition (Easy)

Load testing asks: "Can your system handle its normal, expected traffic?" You simulate 500 users using the app at the same time (a typical Monday morning), run the test for 30 minutes, and verify: response times are under your SLO, error rate is near zero, the server isn't maxing out CPU or memory. It's not about breaking the system — it's about verifying it handles what you expect.

---

### 🔵 Simple Definition (Elaborated)

Load testing is the most common and most important type of performance test. It answers: **"Does the system meet its SLOs under expected production load?"**

**Defining "expected load"**:

1. **Current peak**: analyze production logs — what's the p99 concurrent users, peak RPS?
2. **Target load**: what must the system support? (e.g., planned marketing campaign, seasonal peak)
3. **Growth projection**: 6-12 months ahead if the system needs to scale

**Load test anatomy**:

```
Concurrent Virtual Users

500 ─────────────────────────────────────────────────────
    ...........................████████████████████.........
100 ──────────────────────────/                    \──────
    ──────────────────────────/                    \──────
 0  ─────────────────────────────────────────────────────
    [  ramp-up (5m)  ][  steady state (20m)  ][ ramp-down ]
```

**What load tests find**:

- Database connection pool too small → connection timeout errors under load
- Thread pool exhaustion → request queuing and latency spikes
- Slow queries that are fine at 10 req/s but cause CPU saturation at 500 req/s
- External API calls without timeouts → cascading failure under load
- Unoptimized code paths that are "fast enough" for a single user but bottleneck at 500

**Difference from other test types**:

- **Load test**: expected load → does it MEET SLOs?
- **Stress test**: increasing beyond capacity → WHEN does it fail?
- **Spike test**: sudden burst → SURVIVES unexpected spikes?
- **Soak test**: sustained load over hours → STABLE over time?

---

### 🔩 First Principles Explanation

```javascript
// K6 LOAD TEST: validate SLO under expected production load
import http from "k6/http";
import { check, sleep } from "k6";
import { Counter, Rate, Trend } from "k6/metrics";

// LOAD PROFILE based on production traffic analysis
export const options = {
  stages: [
    { duration: "5m", target: 200 }, // ramp up to 200 VUs over 5 min
    { duration: "20m", target: 200 }, // hold 200 VUs for 20 min (steady state)
    { duration: "5m", target: 0 }, // ramp down
  ],

  // SLO-BASED THRESHOLDS: build fails if violated
  thresholds: {
    // Latency SLO
    "http_req_duration{name:browse_products}": ["p(95)<200", "p(99)<500"],
    "http_req_duration{name:create_order}": ["p(95)<500", "p(99)<1500"],
    "http_req_duration{name:get_order}": ["p(95)<100", "p(99)<300"],

    // Availability SLO
    http_req_failed: ["rate<0.005"], // < 0.5% error rate

    // Custom business metric
    order_success_rate: ["rate>0.995"], // 99.5% of orders complete successfully
  },
};

const orderSuccessRate = new Rate("order_success_rate");
const browseProducts = new Trend("browse_products_duration");

// REALISTIC USER SCENARIO: models actual user behavior with think times
export default function () {
  const params = {
    headers: { Authorization: `Bearer ${getToken()}` },
    tags: { name: "browse_products" }, // name for threshold targeting
    timeout: "10s",
  };

  // Browse products (most common user action)
  const products = http.get("/api/products?page=1&limit=20", params);
  check(products, { "browse ok": (r) => r.status === 200 });

  sleep(1.5); // think time: user reads product list

  // 30% of users proceed to product detail
  if (Math.random() < 0.3) {
    const productId = products.json("items.0.id");
    http.get(`/api/products/${productId}`, {
      ...params,
      tags: { name: "get_product" },
    });

    sleep(3); // user reads product detail

    // 20% of those users add to cart and checkout
    if (Math.random() < 0.2) {
      http.post("/api/cart/items", JSON.stringify({ productId, quantity: 1 }), {
        ...params,
        tags: { name: "add_to_cart" },
      });

      sleep(2);

      const orderResp = http.post(
        "/api/orders/checkout",
        JSON.stringify({ paymentToken: "tok_visa" }),
        { ...params, tags: { name: "create_order" } },
      );

      orderSuccessRate.add(orderResp.status === 201);
    }
  }

  sleep(Math.random() * 2 + 1); // inter-request pause
}
```

```java
// LOAD TEST RESULTS ANALYSIS

// Interpreting k6 output:
//
// ✓ http_req_duration{name:browse_products} p(95)=156ms p(99)=289ms  ← SLO: 200ms/500ms ✓
// ✓ http_req_duration{name:create_order}    p(95)=412ms p(99)=890ms  ← SLO: 500ms/1500ms ✓
// ✗ http_req_duration{name:create_order}    p(99)=2,340ms            ← ✗ exceeds 1500ms SLO!
//
// ERROR DETAIL:
// 23 requests timed out on create_order — all between 18:32 and 18:34
//
// INVESTIGATION: check APM (Datadog/New Relic) at 18:32
// → Database connection pool hit max limit (pool size: 10)
// → Requests queued, timeout at 2s
// FIX: increase HikariCP connection pool to 25; add pool timeout alert
// RESULT: re-run load test → p99 create_order = 743ms ✓

// LOAD TEST ENVIRONMENT REQUIREMENTS:
// - Same CPU/RAM as production (or scaled proportionally if using auto-scaling)
// - Same database size (or at least same table size/index structure)
// - Same number of application instances as production
// - Real external dependencies OR realistic mocks with accurate latency
// - Separate load test environment (don't load test staging while devs use it)
```

```
LOAD TEST CONFIGURATION BEST PRACTICES:

  VIRTUAL USERS vs RPS:
  ─────────────────────────────────────────────────────
  Virtual Users model concurrent users (browser-like)
  Each VU sends request → waits (think time) → next request
  200 VUs × (1 req / 2 sec think time) ≈ 100 RPS throughput

  RPS (open model): specify requests per second directly
  Use for API load tests without think time

  RECOMMENDED WARM-UP:
  ─────────────────────────────────────────────────────
  5 minutes ramp-up (not 30 seconds) to:
  - Let JVM JIT compile hot paths
  - Fill database query caches
  - Pre-warm connection pools
  - Avoid measuring cold-start behavior

  DATA MANAGEMENT:
  ─────────────────────────────────────────────────────
  Use pre-generated test data (CSV file with 10,000 test accounts)
  Each VU picks a different account (no contention on same record)
  Clean up test orders after the run (or use a dedicated test tenant)
```

---

### ❓ Why Does This Exist (Why Before What)

Software systems fail in ways that only appear under concurrent load: a database query fine for 1 user causes CPU saturation at 500; connection pools sized for 10 concurrent connections time out at 200; a lock in shared state causes throughput collapse. Load tests discover these capacity limitations before production traffic reveals them. The cost of a load test is an engineer-day; the cost of a production capacity failure is user impact, SLA violations, and incident response.

---

### 🧠 Mental Model / Analogy

> **Load testing is like a fire drill**: you don't wait for a real fire to find out if your evacuation procedures work — you simulate it under controlled conditions. You don't wait for Black Friday traffic to find out if your checkout can handle 500 concurrent users — you simulate it under controlled conditions. The simulation is deliberately realistic (based on real traffic patterns, real user flows, real data volumes) so the results map to real behavior.

---

### 🔄 How It Connects (Mini-Map)

```
Need to validate system performance under expected production traffic
        │
        ▼
Load Test ◄── (you are here)
(expected load; SLO validation; realistic user simulation; production-like environment)
        │
        ├── Performance Test: load test is the primary type of performance test
        ├── Stress Test: extends load test to find the breaking point
        ├── Spike Test: sudden load increase (subset of stress testing)
        └── SLO/SLA: load test results validate that SLOs are being met
```

---

### 💻 Code Example

```yaml
# k6 report: typical load test summary output
scenarios: (1) default: 200 looping VUs for 30m0s (gracefulStop: 30s)

     ✓ browse ok (100% pass)

     checks.........................: 99.82% ✓ 48,420 ✗ 87
     data_received..................: 412 MB 229 kB/s
     data_sent......................: 45 MB 25 kB/s
     http_req_blocked...............: avg=1.2ms  p(90)=2.4ms  p(99)=12ms
     http_req_duration..............: avg=145ms  p(90)=310ms  p(95)=421ms  p(99)=876ms
     ✓ { name:browse_products }....: avg=48ms   p(95)=156ms  p(99)=289ms
     ✓ { name:create_order }.......: avg=215ms  p(95)=412ms  p(99)=890ms
     http_req_failed................: 0.18% ✓ 87 ✗ 48,420   ← 87 failures
     http_reqs......................: 48,507 269/s

     RESULT: PASS — all SLO thresholds met
     NOTE: 87 failures investigated → all DNS timeout on external payment API
           (network blip, not application issue) → acceptable
```

---

### ⚠️ Common Misconceptions

| Misconception                         | Reality                                                                                                                                                                                                                                                                                                                                                                                |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Load tests can run against production | Running a load test against production is dangerous: it can degrade service for real users, trigger rate limits and fraud detection on payment APIs, and pollute production data with test orders. Always use a dedicated performance test environment. Exception: canary traffic profiling (passive monitoring of production traffic patterns) is different from active load testing. |
| Higher throughput is always better    | Throughput (RPS) and latency are inversely related at load — at some point, pushing more requests per second causes queuing and latency to increase sharply (Little's Law). The goal is to find the throughput level where SLOs are met, not to maximize throughput. A system that serves 1,000 RPS at p99 200ms is better than one serving 2,000 RPS at p99 5,000ms.                  |
| Load test pass = production is safe   | Load tests model expected behavior. Production is full of surprises: unusual request patterns, bots, correlated failures, infrastructure instability. A load test pass is necessary but not sufficient for production confidence. Combine with observability (APM, dashboards, alerting) to catch production anomalies that load tests miss.                                           |

---

### 🔗 Related Keywords

- `Performance Test` — load test is the primary subtype of performance testing
- `Stress Test` — extends load testing beyond expected capacity
- `SLO/SLA` — load tests validate that service level objectives are met
- `Capacity Planning` — load test results drive infrastructure sizing decisions
- `Observability` — APM tools used alongside load tests to identify bottlenecks

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ LOAD TEST = expected load → does it meet SLO?           │
│ PHASES: ramp-up → steady state (20m) → ramp-down       │
│ TOOLS: k6 | Gatling | JMeter | Locust                  │
│                                                          │
│ DEFINE LOAD FROM:                                       │
│  • Production traffic logs (peak concurrent users)     │
│  • Business requirements (support N users at peak)     │
│  • SLO definition (p99 < Xms at Y RPS)                │
│                                                          │
│ ENVIRONMENT: MUST match production hardware/data size  │
│ REALISTIC: use think times; mix of read/write traffic  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Auto-scaling (AWS Auto Scaling, Kubernetes HPA) changes load testing strategy. With auto-scaling, the system can add capacity as load increases — so there may not be a fixed breaking point. Load tests for auto-scaling systems must verify: (a) scale-out happens fast enough (before requests start failing — the lag between load spike and new instances being ready); (b) scale-in doesn't drop active connections; (c) cost scaling is acceptable (adding 10 instances = 10x compute cost). Design a load test strategy for an auto-scaling Kubernetes service: what load profiles should you test? How do you verify that auto-scaling triggers at the right threshold?

**Q2.** Load tests generate thousands of synthetic orders, users, and transactions in the test database. After the test, this data must be cleaned up — otherwise it pollutes analytics, billing reports, and audits. Cleanup strategies: (a) use a dedicated test tenant/namespace (all test data isolated by tenant ID); (b) mark all test records with a `is_test=true` flag and delete them post-test; (c) use a database snapshot — restore to pre-test state after the load test. What are the risks of each approach? Which is most appropriate for a multi-tenant SaaS application? How do you ensure test data cleanup doesn't fail silently (leaving gigabytes of test orders in the production database)?
