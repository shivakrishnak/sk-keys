---
layout: default
title: "Gatling / k6 (Load Testing)"
parent: "Testing"
nav_order: 1173
permalink: /testing/gatling-k6-load-testing/
number: "1173"
category: Testing
difficulty: ★★★
depends_on: Performance Test, Load Test, Stress Test
used_by: Performance Engineers, DevOps, SREs
related: Performance Test, Load Test, Stress Test, Observability, Grafana, k6
tags:
  - testing
  - load-testing
  - performance
  - gatling
  - k6
---

# 1173 — Gatling / k6 (Load Testing)

⚡ TL;DR — Gatling and k6 are load testing tools that simulate thousands of concurrent users against your application, measuring response times, throughput, and error rates to validate performance requirements and find breaking points.

| #1173           | Category: Testing                                                    | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Performance Test, Load Test, Stress Test                             |                 |
| **Used by:**    | Performance Engineers, DevOps, SREs                                  |                 |
| **Related:**    | Performance Test, Load Test, Stress Test, Observability, Grafana, k6 |                 |

### 🔥 The Problem This Solves

"IT WORKS FOR 10 USERS — WHAT ABOUT 10,000?":
Unit and integration tests verify correctness for a single user. Load testing verifies behavior under concurrent load — does the API still respond in < 200ms when 5,000 users hit it simultaneously? Does it degrade gracefully under 10,000? When does it fall over (stress test)? Without load testing, performance problems are discovered in production, often during your highest-traffic event (Black Friday, product launch, marketing campaign).

### 📘 Textbook Definition

**Gatling** is a Scala-based, high-performance load testing tool where test scenarios are defined as code (Gatling DSL or Java API). It generates detailed HTML reports and can simulate thousands of concurrent virtual users from a single machine using a non-blocking Netty/Akka architecture. **k6** (Grafana k6) is a modern, Go-based load testing tool with test scripts written in JavaScript. It's designed for developer workflows: tests in version control, CLI-driven, integrates with Grafana for live metrics, and supports cloud execution (Grafana Cloud k6) for distributing load across multiple regions. Both tools execute **scenarios** (sequences of HTTP requests) from multiple **virtual users** simultaneously and report: **response time** (p50, p90, p95, p99), **throughput** (requests/second), and **error rate**.

### ⏱️ Understand It in 30 Seconds

**One line:**
Load testing = simulate N concurrent users hitting your app; measure response time + error rate; find breaking point.

**One analogy:**

> Load testing is a **fire drill for your infrastructure**: instead of discovering your building's evacuation capacity when there's a real fire, you schedule a drill — 500 people, all at once, through the exit doors. You measure: how long does evacuation take? When does it become chaotic? Where are the bottlenecks (narrow staircase = database connection pool)? You fix them before the real emergency.

### 🔩 First Principles Explanation

LOAD TEST TYPES:

```
LOAD TEST (expected peak):
  Simulate expected maximum concurrent users
  Goal: verify system meets performance SLOs under normal peak load
  E.g.: "We expect 5,000 concurrent users at peak. Verify p95 < 500ms."

STRESS TEST (beyond peak):
  Gradually increase load beyond expected peak
  Goal: find the breaking point; observe degradation behavior
  E.g.: 5k → 10k → 20k → 50k users. At what point do errors appear?

SOAK TEST (sustained load):
  Run at normal load for hours/days
  Goal: find memory leaks, connection pool exhaustion, gradual degradation
  E.g.: 1,000 users for 8 hours. Does response time degrade over time?

SPIKE TEST (sudden surge):
  Instant jump from 0 to 10,000 users
  Goal: test cold-start, autoscaling, circuit breaker behavior
  E.g.: Marketing email sends — instant traffic spike
```

k6 EXAMPLE:

```javascript
// k6 script: load test the checkout API
import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";

// Custom metrics
const errorRate = new Rate("errors");
const checkoutTime = new Trend("checkout_duration_ms");

export const options = {
  stages: [
    { duration: "2m", target: 100 }, // ramp up: 0 → 100 users
    { duration: "5m", target: 100 }, // steady: 100 users for 5 min
    { duration: "2m", target: 500 }, // spike: 100 → 500 users
    { duration: "5m", target: 500 }, // sustained: 500 users
    { duration: "2m", target: 0 }, // ramp down
  ],
  thresholds: {
    http_req_duration: ["p(95)<500"], // 95% of requests < 500ms
    http_req_failed: ["rate<0.01"], // < 1% error rate
    errors: ["rate<0.01"],
  },
};

export default function () {
  const start = Date.now();

  const response = http.post(
    "https://staging.myapp.com/api/v1/checkout",
    JSON.stringify({ cartId: "12345", paymentToken: "tok_test" }),
    {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${__ENV.AUTH_TOKEN}`,
      },
    },
  );

  const duration = Date.now() - start;
  checkoutTime.add(duration);

  const passed = check(response, {
    "status is 200": (r) => r.status === 200,
    "response time < 1s": (r) => r.timings.duration < 1000,
    "has orderId": (r) => JSON.parse(r.body).orderId !== undefined,
  });

  errorRate.add(!passed);

  sleep(1); // Think time between requests (realistic user pacing)
}
```

GATLING EXAMPLE (Java DSL):

```java
public class CheckoutSimulation extends Simulation {

    HttpProtocolBuilder httpProtocol = http
        .baseUrl("https://staging.myapp.com")
        .acceptHeader("application/json")
        .header("Authorization", "Bearer " + System.getenv("AUTH_TOKEN"));

    ScenarioBuilder checkoutScenario = scenario("Checkout Flow")
        .exec(
            http("Search Products")
                .get("/api/v1/products?q=laptop")
                .check(status().is(200))
                .check(jsonPath("$[0].productId").saveAs("productId"))
        )
        .pause(1)
        .exec(
            http("Add to Cart")
                .post("/api/v1/cart/items")
                .body(StringBody(session ->
                    "{\"productId\":\"" + session.getString("productId") + "\",\"quantity\":1}"))
                .asJson()
                .check(status().is(201))
        )
        .pause(2)
        .exec(
            http("Checkout")
                .post("/api/v1/checkout")
                .body(StringBody("{\"paymentToken\":\"tok_test\"}"))
                .asJson()
                .check(status().is(200))
                .check(responseTimeInMillis().lt(500))
        );

    {
        setUp(
            checkoutScenario.injectOpen(
                nothingFor(5),                         // warmup pause
                atOnceUsers(10),                       // initial 10 users
                rampUsers(100).during(60),             // ramp to 100 over 1 min
                constantUsersPerSec(50).during(300)    // 50 users/sec for 5 min
            )
        ).protocols(httpProtocol)
         .assertions(
             global().responseTime().percentile(95).lt(500),
             global().failedRequests().percent().lt(1)
         );
    }
}
```

INTERPRETING RESULTS:

```
k6/Gatling report key metrics:

http_req_duration p(50) = 85ms    → median response time
http_req_duration p(95) = 342ms   → 95% of requests faster than this
http_req_duration p(99) = 891ms   → 99% of requests faster than this
http_req_failed = 0.2%            → error rate (should be < 1%)
http_reqs = 8,450/s               → throughput (requests per second)

RED FLAGS:
  p99 >> p95 → outliers present (GC pauses? DB lock waits?)
  Error rate climbing → approaching breaking point
  Response time increasing under sustained load → memory leak or connection pool exhaustion
  p95 OK but p99 spikes → occasional slow queries (missing index? lock contention?)
```

### 🧪 Thought Experiment

THE CONNECTION POOL SOAK TEST DISCOVERY:

```
Application: 50 concurrent DB connections in connection pool.
Load: 200 concurrent users.

Short load test (5 minutes): passes. p95 = 200ms. ✓

Soak test (4 hours at 200 users):
  Hour 1: p95 = 200ms ✓
  Hour 2: p95 = 350ms
  Hour 3: p95 = 800ms
  Hour 4: p95 = 5,000ms, error rate = 15%

Root cause: connection leak.
  Each request creates a new connection AND returns it to the pool.
  But: 0.1% of requests encounter an exception path that doesn't return the connection.
  Over 4 hours: 50,000 requests × 0.1% = 50 leaked connections = pool exhausted.

Fix: try-with-resources / proper connection management.

Lesson: soak tests find what load tests miss — gradual resource exhaustion.
```

### 🧠 Mental Model / Analogy

> A load test is a **stress test for infrastructure**: just as materials engineers test steel by applying increasing load until it yields (to know its tensile strength and behavior near failure), performance engineers apply increasing virtual users to discover: the system's capacity, the failure mode (crash vs. graceful degradation), and the recovery behavior.

### 📶 Gradual Depth — Four Levels

**Level 1:** k6 script sends HTTP requests from N virtual users simultaneously. Set thresholds (`p95 < 500ms`). Run: `k6 run script.js`. Check if thresholds pass or fail.

**Level 2:** Load test scenarios: ramp up (realistic), constant (steady-state), spike (sudden surge). Think time: `sleep(1)` between requests (simulates real user behavior). Parametrize with different user data (CSV data source in k6/Gatling) to avoid cache-friendly test patterns.

**Level 3:** Performance SLOs as test thresholds: p95 < 500ms, error rate < 0.1%, throughput > 1000 req/s. These become CI gates: if performance degrades beyond threshold → fail the pipeline. Live metrics with Grafana: k6 can stream metrics to InfluxDB or Prometheus → Grafana dashboard shows real-time percentiles, throughput, and error rates during the test.

**Level 4:** Distributed load generation: single machine can generate ~10k-20k RPS. For higher loads, use k6 Cloud (Grafana Cloud) or distributed k6 with multiple instances. Test environment isolation: load tests must not run against production (except controlled canary load tests). Dedicated staging environment with same sizing as production — load test results only translate to production if the environment is identical. Load test data: test must use realistic data volume (10M records in DB, not 100) for valid query performance.

### 💻 Code Example

```bash
# k6 CLI — run load test
k6 run \
  --env AUTH_TOKEN=eyJ... \
  --out influxdb=http://localhost:8086/k6 \
  checkout-load-test.js

# Output:
#      ✓ status is 200
#      ✓ response time < 1s
#      ✓ has orderId
#
# checks.........................: 99.85% ✓ 89865  ✗ 135
# http_req_duration..............: avg=127ms  min=45ms  med=108ms  max=1.2s   p(90)=211ms  p(95)=342ms  p(99)=891ms
# http_req_failed................: 0.15%   ✓ 135    ✗ 89865
# http_reqs......................: 90000  300/s
#
# ✗ errors: rate=0.15% > threshold=0.01%  ← THRESHOLD FAILED
```

```yaml
# GitHub Actions — performance regression check
- name: Run k6 load test
  uses: grafana/k6-action@v0.3.0
  with:
    filename: tests/load/checkout.js
  env:
    AUTH_TOKEN: ${{ secrets.TEST_AUTH_TOKEN }}
    K6_CLOUD_TOKEN: ${{ secrets.K6_CLOUD_TOKEN }}
```

### ⚖️ Comparison Table

|                | Gatling            | k6               | JMeter     |
| -------------- | ------------------ | ---------------- | ---------- |
| Language       | Java/Scala DSL     | JavaScript       | GUI/XML    |
| Performance    | Excellent          | Excellent        | Good       |
| Reports        | HTML (built-in)    | JSON + Grafana   | GUI        |
| CI integration | Maven plugin       | CLI              | CLI        |
| Cloud support  | Gatling Enterprise | Grafana Cloud k6 | BlazeMeter |
| Learning curve | Medium             | Low              | High       |

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                        |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| "Load tests should always run against production" | Use staging (same size as prod); load testing production risks real user impact                |
| "Passing load test = ready for production"        | If staging ≠ production (different DB size, different caching), results don't transfer         |
| "1,000 VUs = 1,000 concurrent requests"           | VUs include think time (sleep); actual concurrent requests = VUs × (request_time / cycle_time) |

### 🚨 Failure Modes & Diagnosis

**1. Load Test Doesn't Represent Real Traffic**
Cause: All virtual users request the same endpoint with same data → cache artificially inflates performance.
Fix: Use parameterized data sources (CSV with random user IDs, product IDs). Test realistic URL distributions.

**2. Thundering Herd on Ramp-Up**
Cause: All VUs start simultaneously (`atOnceUsers(1000)`) → 1000 cold-start connections at once.
Result: Database connection pool exhaustion at start, not under steady load.
Fix: Gradual ramp-up (`rampUsers(1000).during(60)`) — allows connection pool to fill gradually.

**3. Load Test Starves Real Monitoring**
Cause: Load test generates so many requests that monitoring data (Prometheus/CloudWatch) is overwhelmed; dashboards become unreadable.
Fix: Dedicate a separate monitoring stack for load test runs; or use a different Grafana data source.

### 🔗 Related Keywords

- **Prerequisites:** Performance Test, Load Test, Stress Test
- **Related:** k6, Gatling, JMeter, Grafana, InfluxDB, Prometheus, Response Time SLOs, Throughput

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT         │ Simulate N concurrent users; measure     │
│              │ p95/p99 response time, error rate        │
├──────────────┼───────────────────────────────────────────┤
│ TEST TYPES   │ Load (expected peak) / Stress (breaking  │
│              │ point) / Soak (8h+ for leaks)            │
├──────────────┼───────────────────────────────────────────┤
│ k6 KEY       │ stages (ramp) + thresholds (SLO gates)  │
├──────────────┼───────────────────────────────────────────┤
│ METRICS      │ p50/p95/p99 latency, RPS throughput,     │
│              │ error rate, active VUs over time         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Discover your capacity before Black     │
│              │  Friday does — on your terms"            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Percentile-based performance metrics (p50, p95, p99) are the industry standard for characterizing response time distributions. Describe: (1) why averages are misleading for response time (a 50ms average can mask a 10% of requests taking 5 seconds — 1 in 10 users has a terrible experience), (2) the "long tail" problem in distributed systems — how independent service calls compound: if 3 services each have p99=200ms, the p99 of the combined call is NOT 200ms (it's the probability that at least one of the 3 is slow), (3) the Apdex score — a standardized satisfaction metric (T=target, F=frustration threshold; satisfied=response<T, tolerating=T<response<4T, frustrated=response>4T; Apdex=(satisfied+0.5×tolerating)/total), and (4) why load testing with percentile thresholds at the p95 or p99 level is appropriate for SLO definition ("99% of users experience < 500ms" corresponds directly to p99 < 500ms).

**Q2.** k6's JavaScript runtime is NOT Node.js — it's Goja, a Go-based JavaScript engine. This has important implications for load test script writing: (1) you cannot use `node_modules` directly (only k6's built-in modules and xk6 extensions), (2) `async/await` is NOT the way k6 runs — k6 uses synchronous blocking HTTP calls (each `http.get()` blocks the VU until response arrives, which is intentional — each VU represents one user's sequential journey), (3) how k6's execution model differs from Node.js (k6 runs `default function()` for each VU in a goroutine, not a single event loop), (4) the initialization context (code outside `default function`) vs. VU context (code inside `default function`) — initialization runs once per VU; VU code runs for each iteration, and (5) k6 Cloud vs. self-hosted: when to use distributed k6 (when local machine can't generate enough load — typically > 10k RPS), cost considerations, and the test data privacy implications (k6 Cloud receives all HTTP request/response data).
