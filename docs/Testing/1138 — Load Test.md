---
layout: default
title: "Load Test"
parent: "Testing"
nav_order: 1138
permalink: /testing/load-test/
number: "1138"
category: Testing
difficulty: ★★☆
depends_on: Performance Test, HTTP and APIs, Observability
used_by: Capacity Planning, SRE, Black Friday Preparation
related: Stress Test, Spike Test, Soak Test, k6, Gatling, JMeter
tags:
  - testing
  - performance
  - capacity
  - sre
---

# 1138 — Load Test

⚡ TL;DR — A load test applies the expected maximum concurrent user load to a system and verifies it sustains acceptable throughput, latency, and error rate — answering "can we handle our busiest day?"

| #1138 | Category: Testing | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Performance Test, HTTP and APIs, Observability | |
| **Used by:** | Capacity Planning, SRE, Black Friday Preparation | |
| **Related:** | Stress Test, Spike Test, Soak Test, k6, Gatling, JMeter | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
An e-commerce site handles 200 req/sec on normal days. Black Friday approaches — estimated 2,000 req/sec peak. Without load testing: the team has no idea if the system handles 2,000 RPS. They guess "probably fine" based on 200 RPS experience. Black Friday arrives: at 1,400 RPS, connection pool exhausted, database becomes the bottleneck, p99 latency spikes to 15 seconds. Checkout fails. Revenue loss: $2M.

THE BREAKING POINT:
Traffic growth is non-linear. A system that handles 200 RPS smoothly may fail at 1,400 RPS because: the database connection pool is sized for 200 RPS; a blocking mutex becomes a bottleneck at high concurrency; caches heat at low load but miss under different access patterns at high load. These failure modes don't appear at low load. Only load testing at the target level reveals them.

THE INVENTION MOMENT:
Load testing as a discipline became critical with internet-scale applications in the late 1990s (dot-com era). The failure of online retailer toysrus.com in 1999 (site went down during Christmas due to load) made load testing mainstream. Netflix's Chaos Engineering (2010s) extended the concept: if failure under load is inevitable, simulate it continuously and build resilience.

### 📘 Textbook Definition

A **load test** is a type of performance test that applies the expected **maximum operational load** to a system — typically the number of concurrent users or requests per second expected at peak traffic — and measures whether the system's throughput, latency, and error rate remain within acceptable bounds throughout the test duration. Load tests answer: "Can our system handle its expected maximum load sustainably?"

Load tests are distinguished from: **stress tests** (load exceeding maximum to find the breaking point), **spike tests** (sudden traffic surges), and **soak tests** (moderate load for extended duration to detect resource leaks).

### ⏱️ Understand It in 30 Seconds

**One line:**
Load test = simulate your busiest day, measure if the system survives with acceptable performance.

**One analogy:**
> A fire drill in an office building tests if all 500 occupants can evacuate in under 3 minutes. The drill uses the real building, all 500 people, the real stairs. You don't do the drill with 10 people and extrapolate. Load testing is the fire drill for your application.

**One insight:**
Bottlenecks don't appear until load exceeds the bottleneck's capacity. Common bottlenecks that only appear under load: database connection pool, HTTP keep-alive connection limit, OS file descriptor limit, GC pause frequency at high allocation rate, mutex contention at high concurrency.

### 🔩 First Principles Explanation

LOAD TEST DESIGN:
```
1. Define target load: "peak expected traffic"
   - Normal day: 200 RPS
   - Sale event: 10× = 2,000 RPS
   - Black Friday: 20× = 4,000 RPS (size for this)
   
2. Define user scenarios (realistic traffic mix):
   - 60% browse products (lightweight GET)
   - 25% search products (complex query)
   - 10% add to cart / checkout (writes, transactions)
   - 5% authentication (high CPU)
   
3. Think time: users don't send requests as fast as possible
   - Think time: 1–5 seconds between requests (models human behavior)
   - Without think time: 100 VUs × 10 req/s = 1,000 RPS
   - With 2s think time: 100 VUs × 0.5 req/s = 50 RPS
   
4. Data variety: 
   - Don't reuse same product ID (cache hit rate 100% → unrealistic)
   - Use realistic distribution (80% of traffic hits 20% of products)
   
5. Assert thresholds:
   - p95 < 500ms, p99 < 1000ms
   - Error rate < 0.5%
   - Throughput > 1800 RPS sustained (90% of target)
```

BOTTLENECK IDENTIFICATION:
```
When load test fails, correlate:
  High latency + high DB connection wait → connection pool too small
  High latency + high CPU + normal DB → computation bottleneck
  High latency + normal CPU + normal DB → thread pool full
  High error rate (429) → rate limiting triggered
  High error rate (503) → upstream service overwhelmed
  High latency late in test → memory leak / GC pressure
```

THE TRADE-OFFS:
Gain: Identifies bottlenecks before production load events; enables capacity planning; validates horizontal scaling.
Cost: Requires production-like environment (expensive); risk of accidental production data corruption if run against production; results depend heavily on test data quality.

### 🧪 Thought Experiment

DISCOVERING THE CONNECTION POOL BOTTLENECK:
```
Load test: ramp to 2,000 RPS

Observations:
  0–1,000 RPS: p99 = 85ms (excellent)
  1,000–1,500 RPS: p99 = 320ms (acceptable)
  1,500–2,000 RPS: p99 = 4,200ms (FAIL)

Metrics at 2,000 RPS:
  DB connection pool: wait_count = 2,340, timeout_count = 89
  DB CPU: 40% (not saturated)
  App CPU: 35% (not saturated)
  DB response time: 8ms (fast)

Analysis: DB is fast, CPU is fine, but connection pool is exhausted.
Requests queue for a connection, causing latency buildup.

Current config: spring.datasource.maximum-pool-size=20
At 2,000 RPS × 8ms avg DB time = 16 concurrent connections needed
But at peak: requests pile up → all 20 connections busy → queue grows

Fix: increase pool size to 50 (with DB max_connections validated)
Re-run: p99 = 92ms at 2,000 RPS → PASS
```

### 🧠 Mental Model / Analogy

> A load test is a **capacity audit**. A restaurant serving 50 customers/day has enough tables, chefs, and waiters. Does it have enough if 500 customers arrive on Valentine's Day? A load test is: invite 500 people simultaneously, time how long each gets served, count how many are turned away. No restaurant runs Valentine's Day without a capacity plan.

> In software: connection pool = tables, database = kitchen, API threads = waiters. Run 500 customers at once, find which resource runs out first.

### 📶 Gradual Depth — Four Levels

**Level 1:** A load test simulates many users using your app at the same time — like the number of users you'd have on your busiest day. You measure how fast it responds and whether it breaks.

**Level 2:** Use k6 or Gatling. Design realistic user scenarios (not just hammering one endpoint). Use proper think time. Load target: 2× expected peak for headroom. Assert SLA thresholds in the test script. Fail CI if thresholds breached. Run before Black Friday, major marketing campaigns, and product launches.

**Level 3:** Load test scenario design: use real user journey data from production logs (`GET /api/products` 60%, `POST /api/search` 25%, etc.). Parameterise with realistic product IDs (Pareto distribution: 80% of requests use 20% of IDs). Use k6's `SharedArray` for large test data (memory efficient). Request correlation: response from step 1 (login) feeds JWT to step 2 (purchase). Result analysis: Little's Law to verify test is correctly designed; Apdex score (ratio of satisfied/tolerated/frustrated users) as a single business metric.

**Level 4:** AWS/GCP load test best practices: run load generators in the same region as the service (avoid WAN latency). Coordinate multi-region load (k6 cloud, Gatling Enterprise). Watch out for: DNS caching during load test (use IPs or long-running connections), TLS handshake overhead (first request), TCP connection creation overhead (keep-alive reduces this). At Netflix/Amazon scale: "production canary" IS the load test — a percentage of real traffic is the test. The load test environment that perfectly mirrors production is always more expensive to maintain than the production environment itself.

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│              LOAD TEST EXECUTION FLOW                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Load Generator (k6 / Gatling):                         │
│  ┌──────────────────────────────────────┐                │
│  │  Virtual Users: 0 → 500 over 5 min  │                │
│  │  Hold: 500 VUs for 20 min           │                │
│  │  Each VU:                           │                │
│  │    1. POST /api/auth/login          │                │
│  │    2. GET /api/products (random ID) │                │
│  │    3. sleep(2s) [think time]        │                │
│  │    4. POST /api/cart/add            │                │
│  │    5. sleep(3s)                     │                │
│  │    6. POST /api/checkout            │                │
│  │    7. sleep(5s) → repeat           │                │
│  └──────────────────────────────────────┘                │
│                  │ HTTP requests                        │
│                  ▼                                       │
│  Application server → DB → Cache → Downstream services  │
│                  │                                       │
│                  ▼                                       │
│  Metrics: Prometheus/InfluxDB → Grafana dashboard       │
│  Threshold check: p99 < 500ms, errors < 0.5% → pass/fail│
└──────────────────────────────────────────────────────────┘
```

### 🔄 The Complete Picture — End-to-End Flow

BLACK FRIDAY LOAD PREPARATION:
```
1. Define target: 10× normal traffic = 2,000 RPS, 30-minute sustained
2. Run load test on staging (production-identical infrastructure)
3. First run result:
   p99 = 4,200ms at 1,600 RPS → FAIL
   Bottleneck: DB connection pool (size: 20, needed: 80)
4. Fix: increase pool size, add read replica for product queries
5. Re-run: p99 = 95ms at 2,000 RPS → PASS
6. Continue: run stress test to find breaking point → 5,200 RPS
7. Autoscaling test: start at 500 RPS, spike to 3,000 → verify scale-out
8. Soak test: 1,500 RPS for 8 hours → no memory growth, no error rate increase
9. Sign off: system ready for Black Friday
10. Black Friday: peak 1,850 RPS; p99 = 108ms; no errors → success
```

### 💻 Code Example

```javascript
// k6 realistic load test with user journey
import http from 'k6/http';
import { check, sleep } from 'k6';
import { SharedArray } from 'k6/data';

const products = new SharedArray('products', () =>
  JSON.parse(open('./test-data/products.json'))  // 10,000 product IDs
);

export const options = {
  stages: [
    { duration: '5m', target: 200 },   // ramp up
    { duration: '20m', target: 500 },  // peak load
    { duration: '5m', target: 0 },     // ramp down
  ],
  thresholds: {
    'http_req_duration{name:checkout}': ['p(99)<2000'],
    'http_req_duration{name:search}': ['p(95)<300'],
    'http_req_failed': ['rate<0.005'],   // 0.5% error rate max
  },
};

export function setup() {
  // Login once and return auth token for reuse
  const res = http.post(`${__ENV.BASE_URL}/api/auth/login`, JSON.stringify({
    username: 'loadtest@example.com', password: 'loadtest123'
  }), { headers: { 'Content-Type': 'application/json' } });
  return { token: res.json('token') };
}

export default function({ token }) {
  const headers = { 'Authorization': `Bearer ${token}` };

  // Browse product (Pareto: 80% of requests use 20% of products)
  const productIndex = Math.random() < 0.8
    ? Math.floor(Math.random() * products.length * 0.2)  // popular
    : Math.floor(Math.random() * products.length);        // long tail

  const productRes = http.get(
    `${__ENV.BASE_URL}/api/products/${products[productIndex].id}`,
    { headers, tags: { name: 'product-detail' } }
  );
  check(productRes, { 'product found': (r) => r.status === 200 });
  sleep(1 + Math.random() * 2);  // 1–3s think time

  // Search (25% of VUs)
  if (Math.random() < 0.25) {
    const searchRes = http.get(
      `${__ENV.BASE_URL}/api/products/search?q=laptop`,
      { headers, tags: { name: 'search' } }
    );
    check(searchRes, { 'search results': (r) => r.status === 200 });
    sleep(2 + Math.random() * 3);
  }

  // Checkout (10% of VUs)
  if (Math.random() < 0.10) {
    const checkoutRes = http.post(
      `${__ENV.BASE_URL}/api/checkout`,
      JSON.stringify({ productId: products[productIndex].id, quantity: 1 }),
      { headers: { ...headers, 'Content-Type': 'application/json' },
        tags: { name: 'checkout' } }
    );
    check(checkoutRes, { 'checkout success': (r) => r.status === 201 });
    sleep(3 + Math.random() * 5);
  }
}
```

### ⚖️ Comparison Table

| Type | Load Level | Duration | Goal |
|---|---|---|---|
| **Load** | Expected max (e.g., 2,000 RPS) | 30–60min | Verify SLA at peak |
| Stress | Beyond max (find breaking point) | 1–2h | Capacity limit |
| Spike | Sudden surge (0 → max in 30s) | 15–30min | Autoscaling response |
| Soak | 70% load | 8–24h | Resource leak detection |
| Scalability | Incremental (100→200→400 RPS) | Multi-step | Scaling efficiency |

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Load test with more VUs = higher load" | Without think time, 10 VUs can generate same load as 1000 VUs; target RPS, not VU count |
| "All test requests should be identical" | Real users access different URLs; identical requests = unrealistic cache hit rate |
| "Staging load test results predict production exactly" | Staging tests reveal bottlenecks; exact numbers differ based on hardware, data volume, network |
| "Load test once a year" | Load test before every significant traffic event and after major architecture changes |

### 🚨 Failure Modes & Diagnosis

**1. Load Test Passes in Staging, Fails in Production**

Cause: Staging has 1/10th the data of production; queries that hit indexes in staging scan full tables in production.
Fix: Use production data volume in staging (or anonymised copy). Add EXPLAIN ANALYZE for queries to catch missing indexes.

**2. Load Test Results Vary 50% Between Runs**

Cause: JVM JIT not warmed up, shared environment, GC timing variation.
Fix: 5-minute warmup run excluded from metrics. Dedicated isolated environment. Run 3 times and use median.

### 🔗 Related Keywords

- **Prerequisites:** Performance Test, HTTP and APIs
- **Builds on:** Stress Test, Spike Test, Soak Test, Capacity Planning
- **Tools:** k6, Gatling, JMeter, Locust

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Apply expected peak traffic; verify SLA  │
│              │ sustained for 30+ minutes                 │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Bottlenecks only appear at load; test at  │
│              │ peak to find them before production does  │
├──────────────┼───────────────────────────────────────────┤
│ DESIGN       │ Realistic scenario mix + think time +    │
│              │ Pareto data distribution                  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Production-like fidelity requires prod-  │
│              │ like infrastructure (expensive)           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "2000 users, 30 minutes — does it hold?" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Stress Test → Spike Test → Soak Test     │
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** The TCP TIME_WAIT state creates a performance trap in load tests: after a TCP connection is closed, the client port enters TIME_WAIT for 2× MSL (60–120 seconds on Linux). A load generator creating 1000 connections/second exhausts the ephemeral port range (32768–60999, ~28000 ports) in 28 seconds. Subsequent connection attempts fail with "Cannot assign requested address." Describe: (1) why this is a load generator problem (not a server problem), (2) how `SO_REUSEADDR` and `net.ipv4.tcp_tw_reuse` kernel settings mitigate it, (3) why HTTP keep-alive connections (persistent connections) are the correct architectural fix (reduce connection creation rate), and (4) how Gatling and k6 handle this by default (both use HTTP/1.1 keep-alive by default — but if your server closes connections aggressively, this reverts to the same problem).

**Q2.** During a load test, you observe that p50 latency is 45ms but p99 is 4,200ms. This "bimodal" distribution — most requests fast, some catastrophically slow — is characteristic of specific failure modes. List three distinct root causes that produce bimodal latency distributions (e.g., database connection pool wait, GC stop-the-world pause, connection timeout on retry), explain the exact mechanism by which each produces the bimodal pattern, and describe the diagnostic procedure (which metric to look at) to distinguish between them without instrumentation in the load-tested service.
