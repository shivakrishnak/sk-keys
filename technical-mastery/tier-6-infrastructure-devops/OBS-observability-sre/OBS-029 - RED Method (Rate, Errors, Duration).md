---
id: OBS-029
title: "RED Method (Rate, Errors, Duration)"
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★☆☆
depends_on: OBS-006, OBS-001, OBS-002
used_by: OBS-010, OBS-031, OBS-042
related: OBS-006, OBS-030, OBS-031, OBS-011, OBS-012
tags:
  - observability
  - metrics
  - sre
  - devops
  - pattern
  - foundational
  - mental-model
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Mastery"
nav_order: 29
permalink: /technical-mastery/obs/red-method-rate-errors-duration/
---

⚡ TL;DR - RED is a three-metric framework for
monitoring request-based services: Rate (requests
per second), Errors (failed requests per second),
Duration (latency distribution). These three metrics
answer "is this service healthy from the user's
perspective?" and serve as the starting point for
every service dashboard and alert.

| #029            | Category: Observability & SRE                          | Difficulty: ★☆☆ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | Metrics -- Types, What Is Observability, Three Pillars |                 |
| **Used by:**    | Dashboards, Golden Signals, SLO-Based Alerting         |                 |
| **Related:**    | Metrics Types, USE Method, Golden Signals, SLI, SLO    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A new microservice is deployed. The team adds 43
metrics: JVM heap, GC pause duration, thread count,
database connection pool utilization, CPU usage,
disk IO, network bytes in/out, cache hit rate, queue
depth, and 34 others. The Grafana dashboard has 43
graphs. When the service starts degrading, the
on-call engineer opens the dashboard and is confronted
with 43 graphs. Which one shows the problem?
CPU at 60% - normal. Heap at 70% - normal. The
engineer spends 15 minutes scanning graphs before
noticing that the "p99 request duration" graph
(buried in row 6, graph 4) has crept from 200ms
to 2400ms. Users have been experiencing 12x slower
response times for 18 minutes while the engineer
was scanning infrastructure graphs.

**THE INVENTION:**
Tom Wilkie (Grafana Labs) formalized the RED method:
every request-based service should display three
metrics above the fold, in the first panel of every
dashboard. Rate, Errors, Duration. These three metrics
directly answer "are users experiencing degradation?"
without requiring the engineer to interpret 43
infrastructure metrics.

---

### 📘 Textbook Definition

**RED Method** - a monitoring framework for request-
based (microservices, APIs, web services) systems:

- **Rate** (R): number of requests per second.
  Answers: "How much traffic is the service handling?"

  ```
  rate(http_requests_total[5m])
  ```

- **Errors** (E): number of failed requests per second
  (or error rate as a percentage of total requests).
  Answers: "How many users are experiencing failures?"

  ```
  rate(http_requests_total{status=~"5.."}[5m])
  rate(http_errors_total[5m]) / rate(http_requests_total[5m])
  ```

- **Duration** (D): distribution of request durations
  (latency). Focus on percentiles: P50 (median),
  P95, P99. Not just average (which hides tail latency).
  Answers: "How fast or slow is the service for users?"
  ```
  histogram_quantile(
    0.99,
    sum by (le) (rate(http_duration_seconds_bucket[5m]))
  )
  ```

**Origin:** Created by Tom Wilkie at Weaveworks/Grafana
Labs. Companion to the USE Method (for resources).
Subset of the Four Golden Signals (from Google SRE Book).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
RED gives you three numbers that answer the question
"is my service working for users?" - volume (Rate),
quality (Errors), and speed (Duration).

> A restaurant health check: how many tables are
> being served (Rate), how many orders are wrong
> or returned (Errors), how long customers wait for
> their food (Duration). These three numbers tell you
> whether the restaurant is healthy from the customer's
> perspective - without needing to know about the
> kitchen temperature, staff headcount, or
> inventory levels.

---

### 🔩 First Principles Explanation

**WHY THESE THREE AND NOT OTHERS:**

```
The user's experience of a service is entirely
determined by:
  1. Whether their requests are being received (Rate)
     If Rate drops → service is unreachable or traffic
     has shifted away (possibly a routing problem)
  2. Whether their requests succeed (Errors)
     If Errors rise → users are experiencing failures
  3. How long their requests take (Duration)
     If Duration rises → users are experiencing slowness

EVERYTHING ELSE is a cause (infrastructure metric),
not an effect (user experience metric).

Infrastructure metrics explain WHY the RED metrics
changed. RED metrics tell you IF something is wrong.

Alert on: RED metrics (customer impact)
Diagnose with: everything else (infrastructure metrics)
```

**RATE - DETECTING TRAFFIC ANOMALIES:**

```
Normal: Rate = 500 req/s ± 10%

Anomalies that rate reveals:
- Sudden drop (rate = 0 or near 0):
  → Service is down or unreachable
  → Load balancer routing problem
  → DNS failure
  → Deployment broke health checks

- Gradual drop:
  → Traffic shifting to other service versions
  → Users abandoning due to slow responses (cascade)

- Sudden spike:
  → Traffic surge (marketing campaign, viral event)
  → Retry storm (upstream is retrying aggressively)
  → DDoS / traffic anomaly
```

**ERRORS - DISTINGUISHING ERROR TYPES:**

```
4xx errors: client errors (bad requests, auth failures)
  - Often not a service health indicator
  - Spike in 400s may indicate API changes
  - Spike in 401/403: auth system issue
  - Spike in 404: broken URLs or missing resources

5xx errors: server errors (bugs, dependency failures)
  - Always a service health indicator
  - 500 Internal Server Error: application bugs
  - 502/503: dependency or upstream failures
  - 504 Gateway Timeout: downstream latency too high

Rule: Alert on 5xx rate. Investigate 4xx spikes
separately (usually not on-call worthy).

Error rate formula:
  error_rate = 5xx_count / total_request_count
  Threshold for SLO: error_rate > (1 - SLO_target)
```

**DURATION - WHY PERCENTILES NOT AVERAGES:**

```
Scenario: 1,000 requests in 1 minute
  990 requests: 50ms
  9 requests: 500ms
  1 request: 30,000ms (30 seconds)

Average: (990*50 + 9*500 + 1*30000) / 1000
       = (49500 + 4500 + 30000) / 1000
       = 84ms

P50 (median): 50ms (990/1000 requests = 50ms)
P95: 500ms (50/1000 requests were slower than this)
P99: 30,000ms (10/1000 requests were slower)
P99.9: 30,000ms

Average (84ms) is completely misleading.
A user who got the 30-second experience would
never guess the average is 84ms.
P99 (30s) shows that 1% of users had a terrible
experience - often caused by a specific path,
a timeout, or a lock contention scenario.

USE PERCENTILES. Average latency is useless
for understanding tail user experience.
```

---

### 🧪 Thought Experiment

**THE RED TRIAGE PROTOCOL:**

An alert fires at 3 a.m.: "Checkout SLO burn rate
elevated." The engineer opens the checkout dashboard.
RED is the first panel:

```
Rate:     Current: 320 req/s | Baseline: 500 req/s
           → Traffic is 36% below normal. Possible:
             fewer users (3am?), or upstream problem,
             or retry storm causing rejected requests

Errors:   Current: 2.1% | Baseline: 0.1%
           → Error rate 21x higher than normal
             Mostly 5xx (internal server errors)
             This is the SLO burn trigger

Duration: P99: 8,200ms | Baseline: 250ms
           P50: 380ms  | Baseline: 80ms
           → All percentiles elevated, not just tail
             Systemic slowness, not isolated timeouts
```

**Three numbers. 30 seconds. The engineer knows:**

1. Service is receiving less traffic than usual
2. 2.1% of requests are failing (21x normal)
3. ALL requests are slow (not just tail)

This pattern is consistent with: a database connection
pool saturation event. The few requests that get
a connection are slow (wait + query). The others
fail immediately (pool exhausted, 5xx).

Next diagnostic step: database connection pool
utilization metric. Not a full dashboard scan.
Three numbers pointed directly at the diagnosis.

---

### 🧠 Mental Model / Analogy

> RED is the instrument cluster of a car: speedometer
> (Rate - how fast are we going?), warning lights
> (Errors - is something broken?), temperature/fuel
> gauges (Duration - are we running hot or running
> out?). These instruments do not tell you what is
> wrong with the engine - that requires opening
> the hood and examining individual components.
> But they tell you immediately whether to keep
> driving, pull over, or call a mechanic.
>
> The 43-metric Grafana dashboard is the equivalent
> of displaying every sensor in the engine bay on
> the dashboard. Technically complete, practically
> unusable when you are driving.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone):**
RED is a rule for which three metrics to put at the
top of every microservice dashboard: how many requests
per second, how many are failing, and how long they
take. These three numbers are all you need to know
if the service is healthy.

**Level 2 - How to use it (junior):**
For any new service, create a Grafana dashboard with
three panels: (1) `rate(requests_total[5m])`, (2)
`rate(errors_total[5m]) / rate(requests_total[5m])`,
(3) `histogram_quantile(0.99, ...)` for P99 latency.
Put these on the first row, always visible without
scrolling. Put infrastructure metrics on subsequent
rows for diagnosis.

**Level 3 - How to instrument it (mid-level):**
Use the OpenTelemetry or Prometheus client to instrument
every service entry point with three metrics:
a counter for requests (with status label), a
counter for errors (5xx label), and a histogram
for duration. Use consistent label names across
services (`service`, `method`, `status`). The histogram
bucket boundaries should cover your SLO: for a 200ms
P99 SLO, include buckets at 0.1, 0.2, 0.5, 1.0, 2.0.

**Level 4 - Alerting (senior):**
RED metrics are the basis for SLO burn rate alerts.
Error rate maps directly to SLI: `errors/total = 1 -
availability`. Duration P99 maps to SLI latency:
`requests_under_threshold/total = latency_compliance`.
Create dual SLOs: one for availability (error rate),
one for latency (P99 compliance). Both feed into
error budget burn rate alerts. Rate is used for
anomaly detection (traffic drop = possible routing
failure, traffic spike = capacity risk).

**Level 5 - Platform (staff):**
Standardised RED across all services via platform
conventions: shared Prometheus library that auto-
instruments HTTP frameworks with the correct metrics.
Grafana dashboard template with RED pre-wired,
deployed by default to all new services via the
service template / Cookiecutter scaffold. Platform
SLO: every service must have RED metrics available
for the platform observability team to include in
the organisation-wide health dashboard. RED as
the common language: when any team reports a service
health issue, they speak in RED terms (rate dropped,
error rate spiked, latency elevated) as the shared
vocabulary.

---

### ⚙️ How It Works (Mechanism)

**PROMETHEUS INSTRUMENTATION (Java Spring Boot):**

```java
// Auto-instrumented with Spring Boot Actuator +
// micrometer-registry-prometheus:
// /actuator/prometheus exposes these by default

// For custom endpoints: use MeterRegistry
@RestController
public class CheckoutController {

  private final Counter requestsTotal;
  private final Counter errorsTotal;
  private final Timer requestDuration;

  public CheckoutController(MeterRegistry registry) {
    this.requestsTotal = Counter.builder("checkout_requests_total")
      .description("Total checkout requests")
      .tag("service", "checkout")
      .register(registry);

    this.errorsTotal = Counter.builder("checkout_errors_total")
      .description("Checkout request errors (5xx)")
      .tag("service", "checkout")
      .register(registry);

    this.requestDuration = Timer.builder("checkout_duration_seconds")
      .description("Checkout request duration")
      .tag("service", "checkout")
      // Buckets matching SLO thresholds:
      .publishPercentileHistogram(true)
      .minimumExpectedValue(Duration.ofMillis(10))
      .maximumExpectedValue(Duration.ofSeconds(10))
      .register(registry);
  }

  @PostMapping("/checkout")
  public ResponseEntity<CheckoutResponse> checkout(
      @RequestBody CheckoutRequest req) {

    requestsTotal.increment();
    return requestDuration.record(() -> {
      try {
        CheckoutResponse resp = checkoutService.process(req);
        return ResponseEntity.ok(resp);
      } catch (Exception e) {
        errorsTotal.increment();
        throw e;
      }
    });
  }
}
```

**PROMQL - RED DASHBOARD QUERIES:**

```promql
# Rate: requests per second (5-minute rolling average)
sum(rate(checkout_requests_total[5m]))
# by service for multi-service overview:
sum by (service) (rate(http_requests_total[5m]))

# Errors: error rate as percentage
100 * (
  sum(rate(checkout_errors_total[5m]))
  / sum(rate(checkout_requests_total[5m]))
)
# 5xx specifically:
100 * (
  sum(rate(http_requests_total{status=~"5.."}[5m]))
  / sum(rate(http_requests_total[5m]))
)

# Duration: P99 latency in milliseconds
1000 * histogram_quantile(
  0.99,
  sum by (le) (
    rate(checkout_duration_seconds_bucket[5m])
  )
)
# Multiple percentiles in one query (Grafana "instant"):
1000 * histogram_quantile(
  $percentile,    # Grafana variable: 0.50, 0.95, 0.99
  sum by (le) (
    rate(checkout_duration_seconds_bucket[5m])
  )
)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**RED TRIAGE DECISION TREE:**

```
[Incident alert fires]
  ↓
[Check Rate]
  Dropped to near 0?
    → Service unreachable. Check health checks,
      load balancer, DNS. Not a RED/metrics issue.
  Significantly lower than baseline?
    → Possible cascading failure upstream.
      Users abandoning? Upstream service down?
  Spike 10x above normal?
    → Traffic surge or retry storm. Capacity risk.
  Normal?
    → Traffic OK. Move to Errors.
  ↓
[Check Errors]
  0 or baseline (< 0.1%)?
    → No failures. Move to Duration.
  Elevated (> SLO threshold)?
    What type?
    4xx spike: auth failure, bad API client, deployment
    5xx spike: service bug, dependency failure, timeout
    → Check dependency health, recent deployments.
  ↓
[Check Duration]
  P99 elevated, P50 normal?
    → Tail latency issue. Long tail caused by:
      timeouts, lock contention, GC pause, specific
      user data paths. Examine traces for slow requests.
  All percentiles elevated?
    → Systemic slowness. Database? External call?
      Queue backup? Resource contention.
  P50 elevated more than P99?
    → Unusual pattern. Possible: all requests slow
      uniformly (e.g., a shared database is slow),
      or caching layer broken (all requests miss cache).
  ↓
[Diagnose with infrastructure metrics]
  Red observations → targeted diagnostic:
    High errors + high latency → dependency failure
    Low rate + high errors → health check failing
    High latency only → database/cache performance
    High rate + high latency → capacity constraint
```

---

### 💻 Code Example

**Example 1 - BAD: Alerting on infrastructure metrics:**

```yaml
# BAD: these alerts fire on causes, not symptoms
# The on-call engineer cannot determine customer impact

- alert: HighCPU
  expr: cpu_usage_percent > 80
  # A background batch job causes CPU 80% with
  # zero customer impact. This fires and wakes
  # someone up for nothing.

- alert: HighJVMHeap
  expr: jvm_memory_heap_used_bytes /
    jvm_memory_heap_max_bytes > 0.8
  # GC will run and reduce heap to 30%.
  # No customer impact. False alarm.

- alert: DBConnectionPoolSaturation
  expr: db_pool_active_connections /
    db_pool_max_connections > 0.9
  # UNLESS this is causing slow queries that
  # are causing high checkout latency - but
  # without the RED metrics, you do not know.
```

**Example 2 - GOOD: RED-based alerts + diagnostics:**

```yaml
# GOOD: alert on symptoms (RED metrics)
# Diagnose with causes (infrastructure metrics)

# PRIMARY ALERTS (symptom-based, wake-up worthy)
- alert: CheckoutHighErrorRate
  expr: |
    (
      sum(rate(checkout_errors_total[5m]))
      / sum(rate(checkout_requests_total[5m]))
    ) > 0.01    # 1% error rate (SLO threshold)
  for: 3m
  labels:
    severity: page
  annotations:
    runbook: "https://wiki.internal/runbooks/checkout-errors"

- alert: CheckoutHighLatency
  expr: |
    histogram_quantile(
      0.99,
      sum by (le) (
        rate(checkout_duration_seconds_bucket[5m])
      )
    ) > 2.0     # P99 > 2 seconds
  for: 5m
  labels:
    severity: page
# DIAGNOSTIC DASHBOARDS (not alerts - for investigation)
# Row 2 on the dashboard (below RED):
# - DB connection pool utilization
# - JVM heap and GC pause
# - CPU and memory
# - Thread pool saturation
```

**Example 3 - RED multi-service overview dashboard:**

```yaml
# Grafana dashboard JSON excerpt (multi-service RED)
# One row per service, three panels per row:
# Rate | Error Rate | P99 Latency

panels:
  - title: "Checkout Service - Requests/s"
    type: stat
    targets:
      - expr: sum(rate(http_requests_total{
          service="checkout"}[5m]))
    fieldConfig:
      defaults:
        thresholds:
          steps:
            - value: 0
              color: red # Rate = 0 → critical
            - value: 100
              color: yellow # Rate low → warning
            - value: 300
              color: green # Normal rate

  - title: "Checkout Service - Error Rate %"
    type: stat
    targets:
      - expr: |
          100 * sum(rate(http_requests_total{
            service="checkout",status=~"5.."}[5m]))
          / sum(rate(http_requests_total{
            service="checkout"}[5m]))
    fieldConfig:
      defaults:
        thresholds:
          steps:
            - value: 0
              color: green
            - value: 0.1
              color: yellow
            - value: 1.0
              color: red

  - title: "Checkout Service - P99 Latency (ms)"
    type: stat
    targets:
      - expr: |
          1000 * histogram_quantile(0.99,
            sum by (le) (rate(
              http_duration_seconds_bucket{
                service="checkout"}[5m])))
    fieldConfig:
      defaults:
        unit: ms
        thresholds:
          steps:
            - value: 0
              color: green
            - value: 500
              color: yellow
            - value: 2000
              color: red
```

---

### ⚖️ Comparison Table

| Framework           | Metrics                              | Target system                                | Best for                         |
| ------------------- | ------------------------------------ | -------------------------------------------- | -------------------------------- |
| RED                 | Rate, Errors, Duration               | Request-based services (APIs, microservices) | User-facing service health       |
| USE                 | Utilization, Saturation, Errors      | Resources (CPU, disk, network, memory)       | Infrastructure capacity          |
| Four Golden Signals | Latency, Traffic, Errors, Saturation | Any system                                   | Comprehensive service + resource |
| LETS                | Latency, Errors, Traffic, Saturation | Variation of Golden Signals                  | (Less common)                    |

**When to use which:**

| Situation                           | Use                                                    |
| ----------------------------------- | ------------------------------------------------------ |
| Is this API healthy?                | RED                                                    |
| Is the database server healthy?     | USE                                                    |
| Is this Kubernetes node overloaded? | USE                                                    |
| Do I need to scale my service?      | RED + USE                                              |
| Is this microservice SLO being met? | RED (feeds SLI)                                        |
| Why is this service slow?           | RED (identifies slow), then USE (finds resource cause) |

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                                                                                                                                                                                                                  |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Average latency is good enough"              | Average hides tail latency. P99 at 10 seconds with P50 at 50ms gives an average of ~150ms. The 1% of users with 10-second experiences are not visible in the average. Always use percentiles.                                                                                                                                            |
| "RED is for microservices only"               | RED works for any request-based system: monolith HTTP endpoints, gRPC services, message queue consumers (rate = messages/s, errors = processing failures, duration = processing time), batch jobs.                                                                                                                                       |
| "I need all 43 metrics to know what is wrong" | No. 43 metrics tell you what the infrastructure is doing. RED tells you what the user is experiencing. Use RED to detect, then infrastructure metrics to diagnose.                                                                                                                                                                       |
| "Errors means 5xx only"                       | Errors means "request did not succeed from the user's perspective." This includes: 5xx (server errors), 4xx where appropriate (auth failures may indicate a real issue), timeouts (request timed out at client - logged as error even if server returned 200), and application-level errors (payload with error field even if HTTP 200). |
| "RED and USE are competing frameworks"        | They are complementary. RED is for services (user perspective). USE is for resources (infrastructure perspective). A complete dashboard has both.                                                                                                                                                                                        |

---

### 🚨 Failure Modes & Diagnosis

**P99 latency elevated but P50 normal - the tail latency problem**

**Symptom:**
RED dashboard shows:

- Rate: normal (500 req/s)
- Errors: normal (0.08%)
- Duration: P50 = 85ms (normal), P99 = 4,200ms (20x normal)

SLO burn rate is elevated. 1% of users are experiencing
4-second latency on a service with a 500ms SLO.

**Root Cause candidates:**

1. GC pause (P50 not affected, only requests that
   start during a GC pause are slow)
2. Specific user data path (certain users trigger
   a complex query not in the common path)
3. Connection pool exhaustion for a specific operation
4. Hot partition in a sharded database

**Diagnosis using traces:**

```promql
# Step 1: Confirm via histogram buckets which percentile
# is affected
sum by (le) (
  rate(checkout_duration_seconds_bucket[5m])
)
# Find the bucket where cumulative count stops growing
# at the expected rate - that is where the tail starts

# Step 2: Pull traces for requests > 2s (tail threshold)
# In Jaeger: filter by duration > 2000ms
# In OTel Collector: tail sampling rule:
#   latency > 2000ms → keep 100%
# Examine: which span is slow?
# Common finding: DB query span 4,000ms (index miss)
#   or external service call 3,800ms (timeout)
```

---

**Rate drop = upstream routing failure (not service failure)**

**Symptom:**
Rate drops from 500 req/s to 50 req/s. Errors are
also elevated (10% error rate, all 503). P99 latency
is very low (20ms - requests are failing fast).

**Interpretation:**
Low latency + high error rate + low rate = the service
is failing requests fast, not processing them slowly.
503 Service Unavailable = the service is rejecting
requests (circuit breaker open, or the health check
is failing and load balancer removed pods from rotation).

This is NOT a RED degradation for the surviving service

- it is a routing/availability failure. The service
  pods are healthy (20ms response = not overloaded),
  but traffic is being lost before or at the load
  balancer.

**Diagnosis:**

```bash
# Check Kubernetes pod status
kubectl get pods -n checkout -l app=checkout
# If pods show CrashLoopBackOff or NotReady:
# health check is failing → load balancer removed them

# Check load balancer health check logs
# Check recent deployment history
kubectl rollout history deployment/checkout-api -n checkout
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Metrics -- Types (Counter, Gauge, Histogram)` -
  RED metrics use all three: rate() over counters,
  histogram_quantile over histograms
- `What Is Observability` - RED is the practical
  application of observability to service health

**Builds On This (learn these next):**

- `USE Method` - the complement to RED for resource
  monitoring (CPU, memory, disk, network)
- `Golden Signals` - the Google SRE Book's four-metric
  framework that extends RED with Saturation
- `SLO (Service Level Objective)` - RED metrics feed
  directly into SLI calculations for SLO compliance

**Alternatives / Comparisons:**

- `USE Method` - for infrastructure resources
- `Four Golden Signals` - adds Saturation to RED;
  the Google SRE Book original. Choose Golden Signals
  when you also need a single Saturation metric.

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ RED          │ Rate, Errors, Duration                   │
│ TARGET       │ Request-based services (APIs, services)  │
├──────────────┼──────────────────────────────────────────┤
│ RATE         │ sum(rate(requests_total[5m]))            │
│              │ Drop → service unreachable or traffic    │
│              │ Spike → surge or retry storm             │
├──────────────┼──────────────────────────────────────────┤
│ ERRORS       │ rate(errors_total) / rate(total)         │
│              │ 5xx = service issue (alert)              │
│              │ 4xx = client issue (investigate)         │
├──────────────┼──────────────────────────────────────────┤
│ DURATION     │ histogram_quantile(0.99, ...)            │
│              │ ALWAYS use percentiles, never average    │
│              │ P50 normal, P99 high → tail latency issue│
│              │ All elevated → systemic slowness         │
├──────────────┼──────────────────────────────────────────┤
│ DASHBOARD    │ RED on row 1, always visible             │
│ RULE         │ Infrastructure metrics on rows 2+        │
│              │ Alert on RED; diagnose with infra        │
├──────────────┼──────────────────────────────────────────┤
│ COMPLEMENT   │ USE Method for resource monitoring       │
│              │ Golden Signals = RED + Saturation        │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Alerting on CPU/memory (not RED)         │
│              │ Average latency instead of percentiles   │
│              │ RED metrics buried below infrastructure  │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ USE Method, Golden Signals, SLI/SLO      │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Separate "is something wrong?" metrics from "why is
something wrong?" metrics. RED answers the first
question for services. The second question requires
infrastructure metrics. This separation principle
applies everywhere: application logs (ERROR logs
answer "is something wrong?"; DEBUG logs answer "why?"),
CI/CD pipelines (build pass/fail answers "is something
wrong?"; step-level timing answers "why is the build
slow?"), database monitoring (query success rate and
P99 latency answer "is the database serving users?";
lock waits and index utilization answer "why is it
slow?"). Design your primary dashboards and alerts
around the "is something wrong?" layer. Design your
diagnostic tools around the "why?" layer. Never mix
the two in the same panel.

---

### 💡 The Surprising Truth

The most counterintuitive RED insight: Rate is often
the most important metric, and it is the one most
often omitted from dashboards. Engineers intuitively
focus on Errors and Duration (things going wrong and
going slow). But a sudden Rate drop to zero is the
single fastest indicator of a complete service outage

- often visible 30 seconds before error rates and
  latency metrics become meaningful (no requests means
  no errors to count, no latency to measure). A Rate
  drop to zero means: no traffic is reaching the
  service. Possible causes: DNS failure, load balancer
  misconfiguration, all pods removed from rotation,
  network partition. None of these will show up in
  your error rate metrics if no requests are being
  processed. Always include Rate - and always add
  an alert for "Rate near zero during business hours."

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[EXPLAIN]** Describe why average latency is
   insufficient for service health monitoring and
   give a concrete example where average latency
   is misleading but P99 reveals the real problem.
2. **[INSTRUMENT]** Write Prometheus metric registration
   code for a REST endpoint that captures all three
   RED metrics with appropriate labels.
3. **[QUERY]** Write the three PromQL queries for
   a Grafana dashboard showing Rate (req/s), Error
   rate (%), and P99 latency (ms) for a service.
4. **[TRIAGE]** Given RED observations (rate normal,
   errors 8%, P99 5000ms), describe the diagnostic
   steps and the infrastructure metrics you would
   look at to find the root cause.
5. **[COMPARE]** Explain the difference between RED
   and USE methods, and describe a scenario where
   you would use both together.

---

### 🧠 Think About This Before We Continue

**Q1.** Your service receives 10,000 req/s. Latency
histogram data for the last 5 minutes:

- `le=0.1`: 6,000 requests (60% under 100ms)
- `le=0.5`: 8,500 requests (85% under 500ms)
- `le=1.0`: 9,700 requests (97% under 1s)
- `le=5.0`: 9,990 requests (99.9% under 5s)
- `le=+Inf`: 10,000 requests
  Calculate P50, P95, P99. Which users are experiencing
  problems if the SLO is P99 < 1 second?
  _Hint: P50: 60% are below 100ms, P50 is in the
  0-100ms bucket. P95: 97% are below 1s, 95% are
  below 1s (between le=0.5 and le=1.0 - interpolate:
  P95 ≈ 750ms). P99: 99% boundary - 97% are below 1s,
  99.9% below 5s. P99 is between 1s and 5s. With
  histogram_quantile interpolation: P99 ≈ 1.5s. SLO
  P99 < 1s is breached (P99 = 1.5s). 3% of users
  (300/10,000 per second) are experiencing > 1 second
  latency._

**Q2.** Your checkout service shows this RED state:
Rate = 50 req/s (baseline: 500 req/s). Error rate =
80% (baseline: 0.1%). P99 latency = 15ms (baseline:
250ms). What does this pattern tell you about the
service state? What is the most likely cause? What
do you do first?
_Hint: High errors + very LOW latency + very low rate
= service is rejecting requests very quickly (not
processing them slowly). 15ms P99 means requests are
failing immediately - not being processed and timing
out. 80% error rate at 15ms = likely 503/429 errors
(rate limiting, circuit breaker open, health check
failing and LB removed pods). First action: check
pod readiness and load balancer health check status.
Not a performance investigation - it is an availability
investigation._

**Q3 (TYPE G):** You are standardising observability
for a 200-service microservices platform. Design a
RED implementation standard for the platform team:
(a) What shared library/instrumentation framework
will you provide to service teams? (b) What metric
naming convention will you enforce? (c) What Grafana
dashboard template will be deployed to all services?
(d) What RED-based alerts will be auto-applied to
all services? (e) How will the platform team enforce
compliance across 200 services?
\*Hint: (a) A shared Micrometer/OTel auto-instrumentation
library injected via Spring Boot starter or Java agent

- zero-config RED metrics for any HTTP service. (b)
  Convention: http_requests_total{service, method,
  status}, http_errors_total{service, status_class},
  http_duration_seconds{service, le}. Enforced via PR
  template and platform code review. (c) Grafana template:
  service variable, three panels (rate/errors/duration),
  deployed via Grafonnet as code, version-controlled.
  (d) Auto-applied alerts: error_rate > 1% for 3m (page),
  P99 > SLO_threshold for 5m (page), rate < 10% of
  baseline for 5m (page - service gone). SLO thresholds
  configured per service in a service registry. (e)
  Compliance: platform monitoring agent checks if RED
  metrics are present for each registered service.
  Weekly compliance report. Non-compliant services
  flagged in engineering all-hands reliability review.\*

---

### 🎯 Interview Deep-Dive

**Q1: "What is the RED method and when would you use it?"**
_Why they ask:_ Baseline SRE/observability literacy test.
_Strong answer includes:_

- RED = Rate, Errors, Duration. For request-based services.
- Rate: requests per second (traffic volume, anomaly detection)
- Errors: failed requests per second or error rate %
- Duration: latency distribution (always P50/P99, never average)
- Use for: any HTTP/gRPC/queue-consuming service dashboard
- Companion: USE Method for resource monitoring
- Origin: Tom Wilkie, Weaveworks. Simplification of
  Google's Four Golden Signals (adds Saturation).
- Key principle: RED metrics measure user experience
  directly. Alert on RED; diagnose with infrastructure metrics.

**Q2: "Why are percentiles better than averages for
latency monitoring?"**
_Why they ask:_ Tests mathematical understanding of
monitoring, not just pattern recognition.
_Strong answer includes:_

- Average is distorted by outliers. 990 requests at
  50ms + 10 at 10,000ms = average of ~150ms. The 1%
  experiencing 10s latency are invisible in the average.
- P99 shows the worst experience for the 99th percentile
  user - directly maps to SLO compliance.
- Concrete example: a checkout service with average
  latency 80ms but P99 = 8,000ms has a severe tail
  latency problem affecting 1% of users (potentially
  thousands/day) that the average completely hides.
- Use P50 for "typical" user, P95 for "mostly", P99
  for SLO compliance, P99.9 for "worst case."

**Q3: "How does RED relate to SLOs?"**
_Why they ask:_ Tests whether the engineer connects
RED to the broader reliability framework.
_Strong answer includes:_

- RED metrics are the natural basis for SLI measurement.
- Availability SLI = `1 - (errors/total)` = derived
  directly from RED Error metric.
- Latency SLI = `requests_under_threshold/total` =
  derived directly from RED Duration histogram.
- SLO = target value for each SLI. Error budget =
  (1-SLO) x window.
- SLO burn rate alerts fire when RED error rate or
  latency compliance deviates from the SLO target
  faster than sustainable.
- So: RED → SLI → SLO → error budget → burn rate alert.
  The full chain starts with the three RED metrics.

> Entry stub. Generate full content using Master Prompt v3.0.
