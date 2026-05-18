---
version: 2
layout: default
title: "Performance Testing (JMeter, Gatling)"
parent: "Testing"
grand_parent: "Technical Mastery"
nav_order: 59
permalink: /technical-mastery/testing/performance-testing-jmeter-gatling/
id: TST-059
category: Testing
difficulty: ★★★
depends_on: Testing, HTTP & APIs, Distributed Systems
used_by: CI-CD, Testing, Observability & SRE
related: Load Testing, JMeter, k6
tags:
  - testing
  - performance
  - advanced
  - production
---

⚡ **TL;DR -** Performance testing applies controlled synthetic load to a system to measure throughput, latency percentiles, and breaking points before real users do.

| Field | Value |
|---|---|
| **Depends on** | Testing, HTTP & APIs, Distributed Systems |
| **Used by** | CI-CD, Testing, Observability & SRE |
| **Related** | Load Testing, JMeter, k6 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Engineering teams build features that pass unit and integration tests but have no data on how the system behaves under realistic or peak load. Response times measured on a developer's laptop with one user mean nothing at 10,000 concurrent sessions.

**THE BREAKING POINT:**
A product launches successfully. Marketing runs a flash sale. Traffic spikes 20×. The database connection pool exhausts in 30 seconds, timeouts cascade, and the entire service is unavailable for four hours. Post-mortem reveals the breaking point was 300 concurrent users - a fact discoverable in one afternoon of load testing.

**THE INVENTION MOMENT:**
Tools like Apache JMeter (1998) and Gatling (2012) emerged to simulate hundreds of thousands of virtual users executing request scripts, recording latency distributions, error rates, and throughput curves - giving teams objective, reproducible performance data before production exposure.

---

### 📘 Textbook Definition

**Performance testing** is a non-functional testing practice that evaluates system behaviour - throughput, response time, resource utilisation, and stability - under a specified workload. **Load testing** applies expected production load. **Stress testing** increases load until failure. **Soak testing** applies sustained load over hours or days to surface memory and resource leaks. **Spike testing** sends a sudden traffic burst. Tools: **Apache JMeter** (Java, GUI + CLI, `.jmx` XML plans), **Gatling** (Scala DSL, HTML reports), and **k6** (JavaScript, cloud-native).

---

### ⏱️ Understand It in 30 Seconds

**One line:** Performance testing is the practice of sending fake users at your system to find its breaking point before real users do.

> Performance testing is like a stress test on a bridge before it opens - engineers apply known forces and measure deflection so they know the safe load limit and the failure mode.

**One insight:** The p99 latency matters more than the average. An average of 200 ms can coexist with 1-in-100 requests taking 5 seconds - the users who hit that tail are the ones who churn.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Under increasing load, every system has a point where throughput flattens and latency climbs - Little's Law: `L = λ × W` (users = arrival rate × response time).
2. Bottlenecks are always singular at any moment: CPU, I/O, memory, locks, or network.
3. Percentile SLAs (p95, p99) capture tail behaviour; averages hide it.
4. Test results are only valid against the same hardware, configuration, and data volume as production.

**DERIVED DESIGN:**
Load generators simulate virtual users (VUs) sending HTTP requests in parallel. The generator records response times per request, computes histograms, and reports throughput (req/s), error rate (%), and percentile latencies (p50/p95/p99).

**THE TRADE-OFFS:**

**Gain:** Objective data on capacity limits; regression detection for latency SLAs; early bottleneck identification before production exposure.

**Cost:** Requires representative environments (size, data, config); results are invalid on under-provisioned infra; test maintenance as API evolves.

---

### 🧪 Thought Experiment

**SETUP:** You are launching a ticket-booking service. Expected peak: 5,000 concurrent users during event releases. SLA: p99 < 500 ms, error rate < 0.1%.

**WHAT HAPPENS WITHOUT PERFORMANCE TESTING:**
You deploy to production sized for average load. On event day, 5,000 users hit simultaneously. The database connection pool (default: 10) exhausts in under one second. JDBC timeouts cascade to HTTP 500s. The release is a catastrophe.

**WHAT HAPPENS WITH PERFORMANCE TESTING:**
A Gatling stress test two weeks before launch reveals the connection pool bottleneck at 150 concurrent users. You raise the pool to 200, add a Redis cache for seat-map reads, and re-test. At 5,500 VUs, p99 is 380 ms and error rate is 0.02%. You deploy with confidence.

**THE INSIGHT:**
Performance testing does not make a system faster - it reveals where the bottleneck lives, so engineering effort goes to the right place at the right time.

---

### 🧠 Mental Model / Analogy

> A performance test is like a water-flow test on a plumbing network: you open all taps simultaneously, measure pressure at every fixture, and locate the pipe with the lowest diameter - that pipe is the bottleneck, not the pump.

**Mapping:**
- Water taps → virtual users (VUs)
- Pump pressure → server capacity (CPU, connections)
- Pressure gauge readings → latency percentile measurements
- Narrowest pipe → system bottleneck (DB connections, locks, CPU)
- Flow rate (litres/min) → throughput (requests/sec)
- Burst tap open → spike test

Where this analogy breaks down: plumbing is deterministic; software systems have non-linear failure modes (GC pauses, thread pool saturation) that don't map neatly to hydraulics.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Performance testing means sending many fake requests to a service at once - like simulating thousands of users - to see how fast it responds and when it starts breaking.

**Level 2 - How to use it (junior developer):**
In JMeter, create a Thread Group (500 users, ramp 60 s), add an HTTP Sampler (GET `/api/products`), add a Response Time Graph listener. Run and observe. In Gatling, write a `Simulation` class with a `scenario` and `inject(rampUsers(500).during(60.seconds))`. Run `mvn gatling:test`.

**Level 3 - How it works (mid-level engineer):**
JMeter spawns Java threads, each executing the sampler loop. Results land in a JTL file. Gatling uses Akka actors (non-blocking) to simulate far more VUs per JVM thread than JMeter. Both tools record timestamps per request, compute histograms, and export HTML reports. k6 uses a Go runtime with a JS scripting API, coroutines per VU - very low resource cost per VU.

**Level 4 - Why it was designed this way (senior/staff):**
JMeter's thread-per-VU model (2000s Java) is simple but limits VU count to JVM heap and OS thread limits (~10 k VUs per node). Gatling's actor model and k6's goroutine model decouple VU count from OS threads, enabling 50 k+ VUs per machine. The shift from GUI (JMeter `.jmx`) to code-as-config (Gatling Scala DSL, k6 JS) reflects CI/CD integration needs: a binary `.jmx` file cannot be code-reviewed or meaningfully diffed; a Scala DSL can. Modern perf pipelines version-control simulations, track p99 regressions in dashboards, and gate releases on SLA compliance.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────┐
│         Load Generator (JMeter / k6)       │
│  VU 1 ─┐                                  │
│  VU 2 ─┤──► HTTP request ──► SUT          │
│  VU N ─┘         │                        │
│                   │◄── response + latency  │
│  Record: t_start, t_end, status, bytes     │
└────────────────────────────────────────────┘
              │
              ▼
     Histogram computation
     p50 / p95 / p99 / max
     Throughput (req/s)
     Error rate (%)
              │
              ▼
     HTML Report / InfluxDB
     + Grafana dashboard
```

**Test types by load shape:**
- **Load** - ramp to expected prod VUs, hold steady
- **Stress** - ramp until error rate or latency SLA breaches
- **Soak** - hold normal VUs for 8–24 h (memory leak detection)
- **Spike** - jump from 0 to 10× VUs instantly, observe recovery

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Define SLA targets (p99 < 500 ms, errors < 0.1%)
  │
  ▼
Write test script (k6 / Gatling DSL / JMeter .jmx)
  │
  ▼
Provision load test environment  ◄── YOU ARE HERE
(mirror prod: same CPU, DB size, config)
  │
  ▼
Run: rampUsers(1000).during(5 minutes)
  │
  ▼
Collect results → InfluxDB + Grafana
  │
  ▼
Analyse: p99 latency, error rate,
         CPU/memory/DB connection graphs
  │
  ├─ SLA PASS → report + deploy
  └─ SLA FAIL → identify bottleneck → fix → re-run
```

**FAILURE PATH:**
p99 spikes at 600 VUs → check DB slow query log, JVM GC log, thread dump. Isolate the bottleneck layer before tuning.

**WHAT CHANGES AT SCALE:**
Distributed load generation: run k6 on 5 nodes behind a k6 Cloud orchestrator or use JMeter in distributed mode. Stream metrics to Grafana in real time. Embed performance tests in CI as nightly runs with SLA regression gates.

---

### 💻 Code Example

**BAD - JMeter GUI test plan (not CI-friendly):**
```xml
<!-- ❌ Binary .jmx - cannot be code-reviewed or diffed -->
<ThreadGroup>
  <intProp name="ThreadGroup.num_threads">500</intProp>
  <intProp name="ThreadGroup.ramp_time">60</intProp>
</ThreadGroup>
```

**GOOD - k6 load test script:**
```javascript
// ✅ k6 JavaScript - version-controlled, CI-runnable
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 500 },  // ramp up
    { duration: '3m', target: 500 },  // steady state
    { duration: '1m', target: 0   },  // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(99)<500'], // p99 < 500 ms
    http_req_failed:   ['rate<0.001'], // < 0.1% errors
  },
};

export default function () {
  const res = http.get('https://api.example.com/products');
  check(res, {
    'status 200': r => r.status === 200,
    'p99 ok':     r => r.timings.duration < 500,
  });
  sleep(1);
}
```

**GOOD - Gatling Scala DSL stress test:**
```scala
// ✅ Gatling simulation - code-reviewable
class ProductApiSimulation extends Simulation {

  val httpConf = http
    .baseUrl("https://api.example.com")
    .acceptHeader("application/json")

  val scn = scenario("Browse Products")
    .exec(http("GET /products")
      .get("/products")
      .check(status.is(200))
      .check(responseTimeInMillis.lte(500))
    )

  setUp(
    scn.inject(
      rampUsersPerSec(10).to(200).during(2.minutes),
      constantUsersPerSec(200).during(5.minutes)
    )
  ).protocols(httpConf)
   .assertions(
     global.responseTime.percentile3.lte(500),
     global.failedRequests.percent.lte(0.1)
   )
}
```

**CI pipeline gate (k6 exit code):**
```bash
# ✅ Fail CI if thresholds breach
k6 run --out influxdb=http://influx:8086/k6 \
  performance/load-test.js
# k6 exits non-zero if any threshold fails → CI fails
```

---

### ⚖️ Comparison Table

| Dimension | JMeter | Gatling | k6 |
|---|---|---|---|
| **Language / DSL** | XML `.jmx` (GUI) | Scala DSL | JavaScript |
| **VU model** | Thread per VU | Akka actor | Goroutine |
| **Max VUs per node** | ~10 k | ~50 k | ~100 k+ |
| **CI-friendly** | Moderate (CLI mode) | Yes | Yes |
| **Reports** | HTML (needs plugin) | Built-in HTML | JSON + k6 Cloud |
| **Distributed mode** | JMeter Remote | Gatling FrontLine | k6 Cloud / OSS |
| **Protocol support** | HTTP, JMS, JDBC, LDAP | HTTP, WebSocket | HTTP, WebSocket, gRPC |
| **Learning curve** | Medium (GUI heavy) | Medium (Scala) | Low (JS) |
| **Cloud SaaS** | BlazeMeter | Gatling Cloud | k6 Cloud |
| **License** | Apache 2.0 | Apache 2.0 | AGPL / k6 Cloud |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Performance testing is done once before go-live" | Latency regressions ship with every code change. Performance must be a CI gate or regressions accumulate silently. |
| "Average response time is the key metric" | p99 is the key metric. A 200 ms average with 3 s p99 means 1% of users - often thousands - have terrible experiences. |
| "Run tests against a dev environment" | Dev environments have different CPU, memory, connection limits, and cache warm-up than production. Results are invalid; decisions based on them are dangerous. |
| "More VUs always means harder load" | VU count × think time drives actual RPS. 1,000 VUs with 10 s sleep can be lighter than 100 VUs with no sleep. Measure requests/second, not VUs alone. |
| "Performance testing finds all bottlenecks" | It reveals the *first* bottleneck at a given load. After fixing it, re-run - a new bottleneck will emerge. Performance work is iterative. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1 - Latency spike but low CPU (connection pool exhaustion)**
**Symptom:** p99 climbs to 8 s at 400 VUs; CPU stays at 15%; error rate near zero.

**Root Cause:** Database connection pool exhausted; requests queue waiting for a free connection.

**Diagnostic:**
```bash
# JVM: HikariCP pool metrics
curl http://app:8080/actuator/metrics/hikaricp.connections.active

# Postgres: active connections
psql -c "SELECT count(*) FROM pg_stat_activity
         WHERE state = 'active';"
```
**Fix:** Increase pool size to match expected concurrency; add a pool wait timeout to fail fast rather than queue.

**Prevention:** Set HikariCP `maximumPoolSize` and `connectionTimeout`; alert on pool utilisation > 80%.

**Mode 2 - Memory grows during soak test (heap leak)**
**Symptom:** JVM heap climbs from 2 GB to 6 GB over 8 hours; p99 spikes every ~90 min (GC pause).

**Root Cause:** Object not released - common causes: unbounded cache, ThreadLocal not cleared, static collection accumulating event listeners.

**Diagnostic:**
```bash
# Capture heap dump at high-memory point
jcmd <pid> GC.heap_dump /tmp/heap-$(date +%s).hprof

# Analyse with Eclipse MAT: find objects retained unexpectedly
```
**Fix:** Profile heap dump in Eclipse MAT; find the dominator tree; release or bound the leaking collection.

**Prevention:** Add heap usage SLA to soak tests (e.g., heap must not grow > 20% after warm-up).

**Mode 3 - Load generator is the bottleneck (tool-side saturation)**
**Symptom:** Throughput plateaus at 300 req/s even as VUs increase; server CPU is 20%.

**Root Cause:** Load generator is CPU/thread-saturated, not the SUT.

**Diagnostic:**
```bash
# Check generator CPU during test
top -p $(pgrep -f jmeter)

# k6: check dropped_iterations metric
k6 run --out json=results.json test.js | \
  grep dropped_iterations
```
**Fix:** Distribute load across multiple generator nodes; switch to k6 or Gatling (higher VU/CPU ratio than JMeter).

**Prevention:** Always monitor load generator CPU and `dropped_iterations` alongside SUT metrics.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Testing - testing pyramid and where performance tests fit (non-functional layer)
- HTTP & APIs - understanding request/response cycles, status codes, and headers
- Distributed Systems - why horizontal scaling, connection pools, and backpressure matter

**Builds On This (learn these next):**
- Observability & SRE - using Grafana, InfluxDB, and Prometheus to analyse performance results
- CI-CD - embedding performance tests as nightly regression gates
- Caching - the most common fix revealed by performance testing

**Alternatives / Comparisons:**
- Load Testing - the specific sub-type focused on expected production load levels
- JMeter - Apache's XML-based, GUI-first load testing tool
- k6 - modern JavaScript-based performance tool optimised for CI/CD

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────┐
│ WHAT IT IS    Synthetic load applied to measure  │
│               latency, throughput, and limits    │
│ PROBLEM       Unknown breaking points ship to    │
│               production; users pay the cost     │
│ KEY INSIGHT   p99 latency reveals tail behaviour │
│               that averages always hide          │
│ USE WHEN      Pre-release capacity validation,   │
│               SLA regression gating in CI        │
│ AVOID WHEN    Running against dev environments   │
│               (results are not transferable)     │
│ TRADE-OFF     Realistic env cost vs test value   │
│ ONE-LINER     Find bottlenecks before users do   │
│ NEXT EXPLORE  k6 Cloud, Gatling DSL, SLO/SLAs   │
└──────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(Root Cause)** During a load test you observe that p95 latency is fine at 500 VUs but p99 jumps from 300 ms to 4 s. CPU, memory, and DB metrics look healthy. What layers of the system would you investigate first, and in what order?

2. **(Scale)** Your organisation has 80 microservices. You want each team to run performance tests in CI, but provisioning a production-mirror environment for each service is cost-prohibitive. How do you design a performance testing strategy that gives useful signal without requiring full production parity per service?

3. **(Design Trade-off)** k6 thresholds can fail a CI build when p99 breaches an SLA. But performance baselines shift as features are added. How do you define and evolve SLA thresholds over time without either blocking valid deployments or letting real regressions through?
