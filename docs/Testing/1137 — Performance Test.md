---
layout: default
title: "Performance Test"
parent: "Testing"
nav_order: 1137
permalink: /testing/performance-test/
number: "1137"
category: Testing
difficulty: ★★☆
depends_on: Integration Test, HTTP and APIs, Observability
used_by: CI-CD, SRE, Capacity Planning, SLA Verification
related: Load Test, Stress Test, Latency, Throughput, Gatling, k6
tags:
  - testing
  - performance
  - non-functional
  - sre
---

# 1137 — Performance Test

⚡ TL;DR — A performance test measures whether a system meets its speed and throughput requirements under defined conditions — verifying that p99 latency, throughput, and resource utilisation stay within SLA bounds.

| #1137 | Category: Testing | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Integration Test, HTTP and APIs, Observability | |
| **Used by:** | CI-CD, SRE, Capacity Planning, SLA Verification | |
| **Related:** | Load Test, Stress Test, Latency, Throughput, Gatling, k6 | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
A new feature is added — a product search endpoint that joins 3 tables. Unit tests: pass (mock DB). Integration tests: pass (5 test rows). Production: 2 million product rows. The first search query takes 4.2 seconds. p99 latency is 8.5 seconds. SLA: 200ms. The feature is functionally correct but performance-incorrect. Without performance tests, this is discovered under production load.

THE BREAKING POINT:
Correctness and performance are orthogonal. A function can return the right answer in O(n²) time and pass all correctness tests. Only by running it under representative load — the right number of users, the right data volume, the right concurrency — does the performance gap become visible.

THE INVENTION MOMENT:
Apache JMeter (1998) was the first widely adopted HTTP load testing tool. Gatling (2011, Scala) brought a code-first, high-throughput approach. k6 (2017) brought modern JavaScript-based performance tests as code, with CI/CD integration. The shift: from "performance test before release (QA team)" to "performance test in every CI pipeline."

### 📘 Textbook Definition

**Performance testing** is the practice of testing a system's speed, scalability, and stability under defined workloads to verify it meets non-functional requirements (NFRs). Performance tests are categorised by their purpose: **load tests** (verify normal + expected peak load), **stress tests** (find breaking point), **soak/endurance tests** (detect memory leaks over extended runs), **spike tests** (sudden load increase), and **scalability tests** (verify horizontal scaling). Key metrics: **throughput** (requests/second), **latency** (response time percentiles: p50, p95, p99), **error rate**, **resource utilisation** (CPU, memory, connections).

### ⏱️ Understand It in 30 Seconds

**One line:**
Performance test = run many concurrent users at the system, measure latency and throughput, verify SLA is met.

**One analogy:**
> Correctness tests check that a bridge is built according to spec. Performance tests check that the bridge can handle 10,000 cars per day without collapsing. Both are required — a structurally correct bridge that can only handle 100 cars/day fails in production.

**One insight:**
Always measure **percentiles**, not averages. Average latency can be 50ms while p99 is 5 seconds — 1% of users have terrible experience. SLAs are written in terms of percentiles for this reason.

### 🔩 First Principles Explanation

KEY METRICS:
```
Throughput:    Requests per second (RPS) the system can sustain
Latency:       Response time distribution:
               p50 = median (50% of requests faster than this)
               p95 = 95th percentile (5% of requests slower)
               p99 = 99th percentile (1% of requests slower)
               p999 = 99.9th percentile (the long tail)
Error rate:    % of requests failing (target: <0.1% under load)
Saturation:    CPU %, memory %, connection pool exhaustion
```

LOAD PROFILE TYPES:
```
Baseline:  Measure single-user latency (no load)
Ramp up:   Gradually increase from 0 → 1000 users over 5 minutes
Sustained: Hold 1000 users for 30 minutes (steady state)
Peak:      Spike to expected maximum (e.g., Black Friday: 10x normal)
Soak:      Run at 70% load for 24 hours (detect memory leaks, GC degradation)
Stress:    Increase past peak until error rate > 1% → find breaking point
```

PERFORMANCE REGRESSION DETECTION:
```
CI gate: performance test in every deployment
  → Current p99 latency: 185ms
  → Baseline (last green build): 190ms
  → Threshold: ±20% regression
  → 185 < 190 × 1.2 → PASS

New code introduces N+1 query:
  → Current p99: 520ms
  → 520 > 190 × 1.2 (228ms) → FAIL → deployment blocked
```

THE TRADE-OFFS:
Gain: Catches performance regressions before production; documents capacity; enables SLA commitments.
Cost: Requires production-like environment + production-like data volumes; expensive to run continuously; results affected by test environment noise.

### 🧪 Thought Experiment

N+1 QUERY DETECTION BY PERFORMANCE TEST:
```
User list endpoint: GET /api/users?page=1
  → Returns 20 users
  
Code introduced N+1:
  for each user:
    SELECT * FROM addresses WHERE user_id = ?  (N queries)

Correctness test: returns correct 20 users with addresses ✓
Performance test with 100 virtual users:
  → p50: 2,400ms (was 45ms baseline)
  → p99: 8,900ms (was 120ms baseline)
  → Database connection pool exhausted after 30 seconds

Performance test: FAIL (p50 > 500ms threshold)
Developer: checks Dynatrace/Datadog → sees 21 queries per request
Fix: eager-load addresses (JOIN instead of N+1)
After fix: p50: 42ms, p99: 115ms → PASS
```

### 🧠 Mental Model / Analogy

> Performance testing is like a capacity assessment for a highway. You run cars (load) at different volumes: normal daily traffic, rush hour, holiday weekend. You measure: how fast they move (throughput), how long it takes to get from A to B (latency), how often there are accidents (errors). When a new construction project (code change) threatens to add a bottleneck, you re-run the capacity assessment before opening the new section.

> The key: the assessment must happen with representative traffic (the right number of cars), not just 10 test cars.

### 📶 Gradual Depth — Four Levels

**Level 1:** Performance tests check how fast your application responds when many users are using it at once. Run 100 users simultaneously and measure: does it respond in under 200ms? Does it slow down? Does it crash?

**Level 2:** Use Gatling (Scala/Java) or k6 (JavaScript). Define scenarios: ramp up to 100 users, hold for 5 minutes, ramp down. Assert: p95 < 500ms, error rate < 0.1%. Store baseline results. Fail CI if p99 increases by > 20% vs baseline. Run on production-like data (not 5 test rows).

**Level 3:** Performance tests in CI: use dedicated environment with representative data. Resource isolation: run performance test alone (not alongside other services that share CPU/network). Warm-up period: exclude first 30s from metrics (JIT compilation, connection pool warming). Compare against stored baseline (InfluxDB/Grafana for time series). The Little's Law approximation: `N = λ × R` (concurrent users = throughput × response time) — helps size load tests correctly: if you target 200 RPS at 100ms response time, you need 200 × 0.1 = 20 concurrent users minimum.

**Level 4:** The performance test reliability problem: test results are noisy. Two consecutive runs of identical code can show 10% latency variance due to: JIT compilation state, GC timing, OS scheduling, network variance. Solution: run multiple warmup iterations, discard first N results, compute moving average, use statistical significance (Mann-Whitney U test) for regression detection rather than fixed percentage thresholds. At Google/Netflix scale: performance testing moves to production via gradual rollouts (canary) with automatic rollback on latency regression — the production load IS the performance test.

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│              k6 PERFORMANCE TEST ARCHITECTURE            │
├──────────────────────────────────────────────────────────┤
│  k6 engine (Go): generates concurrent virtual users     │
│  Each VU runs the test script in a goroutine            │
│                                                          │
│  Script:  ramping-vus executor                          │
│  0→100 VUs over 2min                                    │
│  100 VUs for 5min                                       │
│  100→0 over 1min                                        │
│                        ↓ HTTP requests                  │
│  ┌─────────────────────────────────────────────────┐    │
│  │ Application server (production-like)            │    │
│  │ Database: 10M rows (production snapshot)        │    │
│  └─────────────────────────────────────────────────┘    │
│                        ↓ metrics                        │
│  k6 output → InfluxDB → Grafana                         │
│  Thresholds: http_req_duration p(99) < 500ms            │
│              http_req_failed rate < 0.01                │
│  → EXIT 0 (pass) or EXIT 1 (fail) → CI gate             │
└──────────────────────────────────────────────────────────┘
```

### 🔄 The Complete Picture — End-to-End Flow

```
CI Performance Gate Pipeline:
1. Build new version, deploy to perf environment
2. Run database seed: 10M synthetic products (representative volume)
3. Run warmup: 10 VUs for 2 min (JVM JIT, connection pool)
4. Run baseline measurement: 1 VU for 5 min (single-user latency)
5. Run load test: ramp 0→200 VUs over 3 min, hold for 10 min
6. Collect metrics: p50, p95, p99, error rate, CPU/memory
7. Compare to stored baseline (from last green build):
   p99 regression > 20% → FAIL
   error rate > 0.1% → FAIL
   CPU saturation > 80% → WARN
8. Publish report to CI (HTML/Grafana link in PR)
9. Pass → promote to staging → production canary
```

### 💻 Code Example

```javascript
// k6 performance test (JavaScript)
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Rate } from 'k6/metrics';

const searchLatency = new Trend('search_latency');
const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '2m', target: 50 },   // ramp up
    { duration: '5m', target: 100 },  // sustained load
    { duration: '2m', target: 0 },    // ramp down
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500', 'p(99)<1000'],  // SLA gates
    'errors': ['rate<0.01'],           // < 1% error rate
    'search_latency': ['p(99)<500'],   // custom metric
  },
};

export default function() {
  // Simulate search user journey
  const searchRes = http.get(
    `${__ENV.BASE_URL}/api/products/search?q=laptop&page=1`,
    { headers: { 'Authorization': `Bearer ${__ENV.TEST_TOKEN}` } }
  );

  searchLatency.add(searchRes.timings.duration);
  errorRate.add(searchRes.status !== 200);

  check(searchRes, {
    'status 200': (r) => r.status === 200,
    'has products': (r) => JSON.parse(r.body).items?.length > 0,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(Math.random() * 2 + 1);  // think time: 1–3 seconds
}
```

### ⚖️ Comparison Table

| Test | Goal | Duration | Load Type | Key Metric |
|---|---|---|---|---|
| **Performance** | SLA verification | 15–30min | Expected + peak | p95/p99 latency |
| Load | Capacity validation | 30–60min | Expected max | Throughput, error rate |
| Stress | Breaking point | 1–2h | Beyond peak | First degradation point |
| Soak | Stability | 8–24h | Sustained moderate | Memory growth, error rate trend |
| Spike | Sudden peak | 15–30min | Instant surge | Recovery time |

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Average latency is the key metric" | Percentiles matter; p99 can be 100× average; SLAs are written in percentiles |
| "Performance test once before release" | Performance regressions are introduced by any code change; test in every CI pipeline |
| "More VUs = more realistic" | Test must reflect real user patterns (think time, user journeys); 1000 VUs with 0ms think time is not realistic |
| "Performance test environment doesn't need to match production" | 10x smaller environment gives completely different results; must use production-like data volumes and hardware |

### 🚨 Failure Modes & Diagnosis

**1. Performance Test Shows Degradation, Root Cause Unknown**

Tools: APM traces (Datadog, Dynatrace, Jaeger) — correlate high-latency requests with their internal spans. Flame graphs (async-profiler for JVM) — show CPU time distribution. SQL query logging: `spring.jpa.show-sql=true` + slow query log.

**2. Performance Test Results Not Reproducible**

Cause: GC pauses (G1GC stop-the-world), JIT compilation (not warmed up), test environment load.
Fix: 5-minute warmup run before measurement. Pin JVM: `-server -XX:+UseG1GC`. Use dedicated performance environment. Run multiple iterations and average.

### 🔗 Related Keywords

- **Prerequisites:** Integration Test, HTTP and APIs, Observability
- **Builds on:** Load Test, Stress Test, Gatling, k6, APM
- **Related:** Latency, Throughput, SLA/SLO, Little's Law

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Measure system speed under load; verify  │
│              │ p99 latency and throughput meet SLA       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Measure percentiles not averages;        │
│              │ p99 is what your worst-10ms-users see    │
├──────────────┼───────────────────────────────────────────┤
│ TOOLS        │ k6 (CI-friendly), Gatling (code-first),  │
│              │ JMeter (GUI, legacy)                      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Production-like fidelity requires        │
│              │ production-like environment + data        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "100 users, 10 min: is p99 < 500ms?"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Load Test → Stress Test → Flame Graphs   │
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** Little's Law states: `N = λ × R`, where N = average number of concurrent requests in the system, λ = throughput (requests/second), R = average response time (seconds). If your SLA requires p99 < 200ms and you expect 500 RPS peak load, calculate the minimum concurrency (N) required in your performance test. If your application has a connection pool of 20 connections and each query takes 10ms: what is the maximum throughput before connection pool exhaustion (hint: 20 connections × 100 queries/sec per connection = 2000 QPS), and at 500 RPS user load, what is the implied database concurrency (N_db = λ_db × R_db)?

**Q2.** High Dynamic Range (HDR) histograms (Gil Tene's HdrHistogram, used by k6, Gatling, and Cassandra) store latency measurements with high precision across a wide range without memory growth. A naive histogram with 1ms buckets from 0–10s requires 10,000 buckets. HdrHistogram stores values with ≤ 0.1% relative error using only ~80KB regardless of range. Explain: (1) why coordinated omission (the Heisenberg problem of load testing: the load generator doesn't send the next request until it receives the response, so slow responses reduce measured throughput AND measured latency) makes naive percentile measurements understate tail latency by 10–100×, (2) how Gil Tene's "corrected coordinated omission" fixes this using scheduled-interval histograms, and (3) why k6's default mode can exhibit coordinated omission and what the `--rps` flag does differently.
