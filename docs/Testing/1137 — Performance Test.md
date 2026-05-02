---
layout: default
title: "Performance Test"
parent: "Testing"
nav_order: 1137
permalink: /testing/performance-test/
number: "1137"
category: Testing
difficulty: ★★☆
depends_on: "Load Test, Stress Test, E2E Test"
used_by: "SLO/SLA validation, capacity planning, release validation"
tags: #testing, #performance-test, #latency, #throughput, #sla, #jmeter, #gatling, #k6
---

# 1137 — Performance Test

`#testing` `#performance-test` `#latency` `#throughput` `#sla` `#jmeter` `#gatling` `#k6`

⚡ TL;DR — **Performance testing** measures how a system behaves under load — validating response time, throughput, and resource utilization against defined targets (SLAs/SLOs). Umbrella term covering: **load test** (expected load), **stress test** (beyond capacity), **spike test** (sudden surge), **soak test** (prolonged load). Tools: **Gatling**, **k6**, **JMeter**, **Locust**. Run in a production-like environment; results are meaningless if the environment is undersized.

| #1137           | Category: Testing                                         | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------- | :-------------- |
| **Depends on:** | Load Test, Stress Test, E2E Test                          |                 |
| **Used by:**    | SLO/SLA validation, capacity planning, release validation |                 |

---

### 📘 Textbook Definition

**Performance test**: a non-functional test that evaluates a system's speed, scalability, and stability under various load conditions. Metrics: (1) **Response time / latency**: time for a single request to complete (p50, p95, p99, p999 percentiles); (2) **Throughput**: requests per second (RPS) or transactions per second (TPS) the system handles; (3) **Error rate**: percentage of requests that fail under load; (4) **Resource utilization**: CPU, memory, disk I/O, network under load; (5) **Concurrency**: maximum simultaneous users/connections. Types: (a) **Load test**: system under expected production load — does it meet SLO? (b) **Stress test**: gradually increase load until the system fails — what is the breaking point? (c) **Spike test**: sudden sharp increase in load — does it survive a traffic spike? (d) **Soak test (endurance test)**: sustained load over hours/days — memory leaks, resource exhaustion, gradual degradation? (e) **Scalability test**: measure how performance changes as resources scale (horizontal/vertical). Tools: **k6** (JavaScript DSL, cloud-native), **Gatling** (Scala DSL, code-first, CI-friendly), **Apache JMeter** (GUI-based, Java), **Locust** (Python, programmable). Performance test environments must mirror production in hardware/configuration — otherwise results are meaningless.

---

### 🟢 Simple Definition (Easy)

Your API handles 1,000 users/day normally. Black Friday is coming — maybe 50,000 users in one hour. Performance testing finds out NOW: does it hold up? How fast does it respond under 10,000 concurrent users? Where does it break? You find out before Black Friday, not during it.

---

### 🔵 Simple Definition (Elaborated)

Performance testing is about answering: "Does the system meet its performance requirements?" Those requirements are defined as SLOs (Service Level Objectives): "p99 response time ≤ 500ms under 1,000 RPS; error rate < 0.1%."

**Key metrics and why percentiles matter**:

- **Average response time** is misleading: if 95% of requests take 10ms but 5% take 5,000ms, the average might look fine but 5% of users have a terrible experience
- **p50**: median — 50% of requests are faster than this
- **p95**: 95% of requests are faster than this (the slow tail)
- **p99**: 99% of requests are faster than this (the slowest 1%)
- **p999**: 1 in 1,000 requests (important for high-traffic systems: 1 million RPS × 0.1% = 1,000 slow requests per second)

**Performance test types visualized**:

```
Load test:     ████████████ (constant expected load → validate SLO)
Stress test:   ████████████████████░ (increase until failure → find limit)
Spike test:    ████████▓▓▓▓████████  (sudden spike → survival test)
Soak test:     ████████████████████████████████████ (hours → find leaks)
```

**Common performance bugs discovered**:

- N+1 query problem: 1 request → 1,000 database queries (not visible in unit tests)
- Missing database indexes: fine for 100 rows, slow for 1 million rows
- Memory leaks: stable at first, gradual degradation over hours
- Connection pool exhaustion: works at 10 concurrent users, times out at 500
- Thread contention: synchronized blocks cause bottlenecks under concurrency

---

### 🔩 First Principles Explanation

```javascript
// K6 PERFORMANCE TEST (JavaScript DSL - modern, cloud-native)

import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";

// Custom metrics
const errorRate = new Rate("errors");
const orderCreationDuration = new Trend("order_creation_duration");

// TEST CONFIGURATION: define load profile
export const options = {
  stages: [
    { duration: "2m", target: 100 }, // ramp-up to 100 VUs in 2 min
    { duration: "5m", target: 100 }, // steady state at 100 VUs for 5 min
    { duration: "2m", target: 500 }, // ramp-up to 500 VUs (stress)
    { duration: "5m", target: 500 }, // steady state at 500 VUs
    { duration: "2m", target: 0 }, // ramp-down
  ],

  // SLO thresholds: test FAILS if these are violated
  thresholds: {
    http_req_duration: [
      "p(95)<500", // 95% of requests under 500ms
      "p(99)<2000", // 99% of requests under 2s
    ],
    errors: ["rate<0.01"], // error rate < 1%
    http_req_failed: ["rate<0.01"],
    order_creation_duration: ["p(95)<1000"],
  },
};

// Authentication (run once, reuse token)
export function setup() {
  const loginResponse = http.post(
    `${BASE_URL}/auth/login`,
    JSON.stringify({
      email: "perf-test@example.com",
      password: "password",
    }),
    { headers: { "Content-Type": "application/json" } },
  );

  return { token: loginResponse.json("accessToken") };
}

// VIRTUAL USER SCENARIO: simulates a real user browsing + ordering
export default function (data) {
  const headers = {
    Authorization: `Bearer ${data.token}`,
    "Content-Type": "application/json",
  };

  // 1. Browse products
  const productsResponse = http.get(
    `${BASE_URL}/products?category=electronics`,
    { headers },
  );
  check(productsResponse, {
    "products status 200": (r) => r.status === 200,
    "products response time < 200ms": (r) => r.timings.duration < 200,
  });
  errorRate.add(productsResponse.status !== 200);

  sleep(1); // simulate user reading

  // 2. View product detail
  const productId = productsResponse.json("items.0.id");
  const detailResponse = http.get(`${BASE_URL}/products/${productId}`, {
    headers,
  });
  check(detailResponse, { "product detail 200": (r) => r.status === 200 });

  sleep(2); // simulate user deciding

  // 3. Add to cart
  const cartResponse = http.post(
    `${BASE_URL}/cart/items`,
    JSON.stringify({ productId, quantity: 1 }),
    { headers },
  );
  check(cartResponse, { "add to cart 201": (r) => r.status === 201 });

  sleep(1);

  // 4. Checkout (CRITICAL PATH - track separately)
  const startTime = Date.now();
  const orderResponse = http.post(
    `${BASE_URL}/orders/checkout`,
    JSON.stringify({ paymentToken: "tok_visa" }),
    { headers },
  );
  orderCreationDuration.add(Date.now() - startTime);

  const orderOk = check(orderResponse, {
    "order created 201": (r) => r.status === 201,
    "order has id": (r) => r.json("orderId") !== null,
  });
  errorRate.add(!orderOk);

  sleep(Math.random() * 3); // random think time (realistic user behavior)
}
```

```scala
// GATLING PERFORMANCE TEST (Scala DSL - CI-friendly, generates HTML reports)

class CheckoutSimulation extends Simulation {

  val httpProtocol = http
    .baseUrl("http://staging.myapp.com")
    .acceptHeader("application/json")
    .contentTypeHeader("application/json")

  // Scenario: critical checkout flow
  val checkoutScenario = scenario("Checkout Flow")
    .exec(http("Login")
      .post("/auth/login")
      .body(StringBody("""{"email":"perf@test.com","password":"password"}"""))
      .check(jmesPath("accessToken").saveAs("token")))

    .pause(1)

    .exec(http("Browse Products")
      .get("/products")
      .header("Authorization", "Bearer #{token}")
      .check(status.is(200))
      .check(responseTimeInMillis.lt(200)))   // inline assertion

    .pause(2)

    .exec(http("Place Order")
      .post("/orders/checkout")
      .header("Authorization", "Bearer #{token}")
      .body(StringBody("""{"paymentToken":"tok_visa"}"""))
      .check(status.is(201))
      .check(responseTimeInMillis.lt(1000)))  // order creation < 1s

  // LOAD PROFILE
  setUp(
    checkoutScenario.inject(
      nothingFor(5.seconds),                      // warm-up pause
      atOnceUsers(10),                            // initial burst
      rampUsers(500).during(2.minutes),           // ramp to 500 over 2 min
      constantUsersPerSec(100).during(5.minutes), // steady 100 req/s for 5 min
    )
  )
  .protocols(httpProtocol)
  .assertions(
    global.responseTime.percentile3.lt(500),     // p99 < 500ms
    global.successfulRequests.percent.gt(99.0),  // >99% success rate
    forAll.responseTime.percentile2.lt(300)       // p95 < 300ms for all requests
  )
}
```

```
PERFORMANCE TEST METRICS EXAMPLE REPORT:

  Scenario: Checkout Flow (500 concurrent VUs, 5 minutes)

  Request         | Count | p50  | p95   | p99   | Errors
  ──────────────────────────────────────────────────────────
  Login           | 2,500 | 45ms | 87ms  | 120ms | 0.0%
  Browse Products | 2,500 | 32ms | 65ms  | 89ms  | 0.0%
  View Product    | 2,498 | 28ms | 61ms  | 85ms  | 0.1%
  Add to Cart     | 2,495 | 55ms | 134ms | 289ms | 0.2%
  Place Order     | 2,490 | 189ms| 487ms | 1,204ms| 0.4%  ← ⚠ p99 > SLO 1000ms

  RESULT: FAIL — Place Order p99 exceeds 1000ms SLO
  INVESTIGATION: database index missing on orders.user_id + status
```

---

### ❓ Why Does This Exist (Why Before What)

Unit and integration tests verify correctness of individual components. But production performance problems are often emergent: code that's fast for 1 request is slow for 1,000 simultaneous requests due to lock contention; code that's fast for 100 database rows is slow for 10 million rows; a service that's stable for 1 hour develops memory leaks over 8 hours. These problems can only be discovered by running the system under production-like load. Performance tests exist to find these problems before users do.

---

### 🧠 Mental Model / Analogy

> **Performance testing is like a load test for a bridge**: civil engineers don't just calculate that the steel and concrete should theoretically hold 10 tons. They apply actual load, measure deflection, look for stress fractures, and test to near-failure limits in a controlled way. Similarly, performance tests don't just predict that the code should be fast — they apply actual simulated load, measure actual latency, look for bottlenecks and failures, and find the real breaking point before real users arrive.

---

### 🔄 How It Connects (Mini-Map)

```
Need to verify system meets performance SLOs under realistic and extreme load
        │
        ▼
Performance Test ◄── (you are here)
(umbrella term: load test, stress test, spike test, soak test)
        │
        ├── Load Test: expected production load → SLO validation
        ├── Stress Test: beyond capacity → find breaking point
        ├── SLO/SLA: performance tests validate that SLOs are met
        └── Observability: APM tools (Datadog, New Relic) used during performance tests
```

---

### 💻 Code Example

```yaml
# k6 CI integration - fail the build if SLOs are violated
# .github/workflows/performance.yml

name: Performance Tests
on:
  schedule:
    - cron: "0 2 * * *" # run nightly at 2 AM
  workflow_dispatch: # or manually trigger

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run k6 performance test
        uses: grafana/k6-action@v0.3.0
        with:
          filename: tests/performance/checkout-load-test.js
        env:
          BASE_URL: ${{ secrets.STAGING_URL }}
          K6_CLOUD_TOKEN: ${{ secrets.K6_CLOUD_TOKEN }}

      # k6 exits with code 99 if thresholds are violated → CI fails
      # Grafana Cloud k6 shows detailed results with graphs
```

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                                                                                                                                                                                                                                                            |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Performance tests can run in the development environment | Performance test results depend entirely on the environment. A laptop with 16 GB RAM and a local database will show very different numbers than a production cluster. Always run performance tests in a production-like environment — same hardware class, same database size, same network topology. Otherwise the results are meaningless for capacity planning. |
| Average response time is the key metric                  | Average response time is severely misleading for web applications. If 95% of requests take 50ms but 5% take 10 seconds, the average might be 550ms — which looks acceptable but 5% of users are having a terrible experience. Always measure percentiles: p95, p99 (and p999 for high-traffic systems).                                                            |
| Performance testing is a one-time activity before launch | Performance characteristics change with every deployment: new code, database growth, traffic pattern changes, infrastructure changes. Performance tests should be automated and run regularly (nightly or per-release). Establish a performance baseline and alert when metrics regress.                                                                           |

---

### 🔗 Related Keywords

- `Load Test` — the primary type of performance test (expected production load)
- `Stress Test` — performance test pushed beyond capacity
- `SLO/SLA` — performance tests validate that service level objectives are met
- `Observability` — APM tools used during performance tests to find bottlenecks
- `Capacity Planning` — performance test results feed into infrastructure sizing decisions

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PERFORMANCE TEST TYPES:                                 │
│  Load test    → expected load → validate SLO           │
│  Stress test  → beyond limit → find breaking point     │
│  Spike test   → sudden surge → survival test           │
│  Soak test    → hours of load → find memory leaks      │
│                                                          │
│ KEY METRICS: p95, p99 latency | RPS | error rate       │
│ TOOLS: k6 | Gatling | JMeter | Locust                  │
│ ENVIRONMENT: must match production (hardware + data)   │
│                                                          │
│ SLO EXAMPLE: "p99 < 500ms, error rate < 0.1% at 1000 RPS" │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Database query performance degrades non-linearly with data volume. A query on a table with 10,000 rows might take 5ms; on 10 million rows without an index, 30 seconds. Performance tests in a staging environment with a small database won't catch this. How should teams handle the "production data volume" problem? Options: (a) copy (anonymized) production data to staging; (b) generate synthetic data at production volume; (c) use database query profiling tools to estimate scaling. What are the trade-offs of each approach? Which is most practical for a team with a 500 GB production database?

**Q2.** Performance test results are often treated as a pass/fail gate: "p99 < 500ms? ✓ deploy." But this misses gradual performance regressions: each deployment might be 2% slower, unnoticeable in isolation, but after 50 deployments the p99 is now 2.6x slower. This is "performance death by a thousand cuts." Describe a continuous performance monitoring strategy: how do you establish a baseline, track performance trends over time, set regression alerts, and distinguish code regressions from load/data volume growth?
