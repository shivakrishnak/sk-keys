---
id: OBS-031
title: Golden Signals
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★☆☆
depends_on: OBS-006, OBS-001, OBS-029, OBS-030
used_by: OBS-010, OBS-042, OBS-044
related: OBS-006, OBS-029, OBS-030, OBS-011, OBS-012
tags:
  - observability
  - metrics
  - sre
  - devops
  - foundational
  - pattern
  - mental-model
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 31
permalink: /obs/golden-signals/
---

# OBS-031 - Golden Signals

⚡ TL;DR - The Four Golden Signals (from the Google
SRE Book) are the minimum sufficient set of metrics
for any distributed system: Latency, Traffic, Errors,
Saturation. They unify the RED Method (Latency +
Traffic + Errors) and USE Method (Saturation) into
one framework that covers both user experience and
resource health.

| #031            | Category: Observability & SRE                           | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------------------------ | :-------------- |
| **Depends on:** | Metrics -- Types, Observability, RED Method, USE Method |                 |
| **Used by:**    | Dashboards, SLO-Based Alerting, Platform Observability  |                 |
| **Related:**    | Metrics Types, RED Method, USE Method, SLI, SLO         |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Different teams in an organisation monitor different
things. The payments team monitors payment success
rate, payment latency, and database replication lag.
The checkout team monitors cart service throughput,
recommendation engine latency, and memory heap.
The infrastructure team monitors CPU, disk, and
network. When an incident spans all three teams (a
database replication lag causes slow queries, which
causes cart service latency, which causes failed
payments), no one has a shared language to describe
the problem. The post-mortem has three different
root causes from three different dashboards, none
of which pointed to the chain.

**THE INVENTION:**
The Google SRE Book (2016) proposed four universal
metrics that every service should monitor, using
consistent terminology. Latency, Traffic, Errors,
Saturation. When every team speaks this language,
the incident chain becomes: "Database Saturation
(disk IO queue) → Database Latency increase → Checkout
Errors increase → Payment Traffic drop." One causal
chain, four signal types, shared vocabulary.

---

### 📘 Textbook Definition

**The Four Golden Signals** (from Google SRE Book,
Chapter 6 "Monitoring Distributed Systems"):

- **Latency**: the time it takes to service a request.
  Distinguish successful-request latency from failed-
  request latency (a fast error is a different problem
  from a slow success).

  ```
  histogram_quantile(0.99, rate(duration_bucket[5m]))
  ```

- **Traffic**: a measure of how much demand is being
  placed on the system. For web services: requests/s.
  For audio/video: network I/O rate. For storage:
  transactions/s. Varies by system type.

  ```
  sum(rate(requests_total[5m]))
  ```

- **Errors**: the rate of requests that fail, either
  explicitly (HTTP 500), implicitly (200 with wrong
  content), or by policy (any response > 1s violates
  the SLO).

  ```
  rate(requests_total{status=~"5.."}[5m])
  / rate(requests_total[5m])
  ```

- **Saturation**: how "full" the service is. A measure
  of the resource that is most constrained. Often
  the metric that predicts degradation before it
  occurs. Latency usually increases as saturation
  approaches 100%.
  ```
  # Database connection pool saturation:
  hikaricp_connections_pending > 0
  # CPU saturation:
  node_load1 / count(node_cpu_seconds_total{mode="idle"})
  ```

**Origin:** Google SRE Book, 2016. Chapter 6,
"Monitoring Distributed Systems," by Rob Ewaschuk.
The most widely cited monitoring framework in
software engineering.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The Four Golden Signals answer: "How fast? How much?
How many failures? How full?" - the four questions
that define whether any distributed system is healthy.

> A city's health report: traffic congestion (Latency),
> number of commuters (Traffic), accidents per day
> (Errors), highway capacity usage (Saturation). Four
> numbers that give the mayor a complete picture of
> whether the city's transportation system is working.
> A mayor who monitors only accidents (Errors) misses
> congestion (Latency). One who monitors only traffic
> volume (Traffic) misses that the roads are 99% full
> (Saturation). All four signals together provide
> the complete picture.

---

### 🔩 First Principles Explanation

**THE RELATIONSHIP TO RED AND USE:**

```
RED Method (Tom Wilkie):
  Rate     → Golden Signal: Traffic
  Errors   → Golden Signal: Errors
  Duration → Golden Signal: Latency
  (Missing: Saturation)

USE Method (Brendan Gregg):
  Utilization → precursor to Saturation
  Saturation  → Golden Signal: Saturation
  Errors      → Golden Signal: Errors (overlaps)
  (Missing: Latency, Traffic)

Golden Signals (Google SRE Book):
  Latency     → service quality (user experience)
  Traffic     → demand (scale context)
  Errors      → reliability (user impact)
  Saturation  → capacity (predicts future degradation)

Golden Signals = RED + Saturation
             = the superset of both frameworks
```

**WHY ALL FOUR ARE NEEDED:**

```
Without Latency:
  A service returning instant 500 errors looks
  "healthy" in Traffic (high) and Saturation (low).
  Errors catches it - but Latency distinguishes
  between "fast failures" (circuit breaker open,
  rejecting quickly) and "slow failures" (request
  times out after 30s). Different root causes,
  different fixes.

Without Traffic:
  Errors at 5% may be fine for a low-traffic test
  service (10 requests/day, 0.5 errors/day) or a
  critical incident for a high-traffic service
  (100,000 req/s = 5,000 failed users/second).
  Traffic provides the scale context for all other
  signals.

Without Errors:
  A service at 99% Saturation with good Latency
  appears healthy. But if 1% of connections are
  being rejected at the queue boundary (connection
  refused errors), those users experience complete
  failure. Errors catches what Latency and Traffic
  cannot see if errors are fast.

Without Saturation:
  Latency is currently 50ms (healthy). Traffic is
  500 req/s. Errors = 0. But CPU is at 95%, disk
  queue depth = 8, and the system is at 98% of
  maximum throughput. In 30 minutes, when a traffic
  spike arrives, the system will collapse. Saturation
  is the predictive signal - it shows degradation
  before it becomes visible in Latency and Errors.
```

**LATENCY: THE MOST NUANCED SIGNAL:**

```
Track successful and failed requests separately:

Successful latency (200 responses):
  The time a working request takes.
  Establishes the baseline user experience.
  High → service is slow (capacity or dependency issue)

Failed latency (5xx responses):
  The time a failed request takes.
  Short (< 5ms) → circuit breaker or fast rejection.
    Not a capacity issue. Check circuit breaker state.
  Long (> 30s) → timeout-based failure.
    Threads held for duration. Resource exhaustion risk.
  Same as success → success and failure take same time.
    Failure is happening at the end of processing
    (e.g., database write fails after full request).
```

---

### 🧪 Thought Experiment

**THE FOUR SIGNALS FAILURE SCENARIOS:**

```
Scenario A: Latency spike only
  L: P99 200ms → 4,000ms   T: 500→500   E: 0%   S: 60%
  Interpretation: service is slow but not failing.
  Users experience slowness. No Saturation cause yet.
  Cause: dependency (downstream service or DB) slow.
  Next: check RED for the downstream service.

Scenario B: Traffic drop + Error spike
  L: P99 80ms→15ms   T: 500→50   E: 0%→85%   S: 10%
  Interpretation: fast failures. 85% error rate but
  very low latency (15ms). Requests are failing
  immediately, not slowly. 90% traffic drop.
  Cause: circuit breaker open, health check failing,
  or auth system down. Low saturation rules out capacity.
  Next: check circuit breaker state, health endpoints.

Scenario C: Saturation building
  L: P99 150ms→180ms   T: 500→550   E: 0%   S: 60%→92%
  Interpretation: Latency slightly elevated, Traffic
  slightly higher, no Errors yet, but Saturation
  approaching limit. The service is operating normally
  but is near capacity.
  Cause: traffic growth hitting resource limits.
  Action: scale before Latency and Errors spike.
  This is saturation's unique value: predicts
  the incident before it happens.

Scenario D: All four elevated
  L: 8000ms   T: 50/s   E: 40%   S: 99%
  Interpretation: full saturation event. Service is
  at capacity, most requests timing out (slow latency),
  many failing (40% error rate), traffic accepted is
  a fraction of normal (50 vs 500 = only successful
  requests getting through). Classic cascade.
  Next: immediate scale or traffic shedding (load shedding
  / circuit breaker) while root cause is identified.
```

---

### 🧠 Mental Model / Analogy

> A hospital emergency department with four vitals:
> Blood pressure (Latency - how hard the heart works
> to push blood through = how hard the service works
> to respond), Heart rate (Traffic - how many beats/
> requests per minute), Oxygen saturation (Errors -
> percentage of oxygen successfully delivered = percentage
> of requests successfully served), Body temperature
> (Saturation - how overloaded the system is, a proxy
> for resource strain).
>
> A doctor who only checks blood pressure misses
> hypoxia (low oxygen = high errors). A doctor who
> only checks heart rate misses that the heart is
> working at 110% capacity (saturation). All four
> vitals together form the minimum sufficient picture
> of patient health. The Four Golden Signals are the
> vital signs of a distributed service.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone):**
The Four Golden Signals are four numbers that tell
you if a service is healthy: how fast (Latency), how
busy (Traffic), how many failures (Errors), and how
full (Saturation). Every service dashboard should
show these four things.

**Level 2 - How to use it (junior):**
Create a Grafana dashboard row showing all four signals
for every service. If any signal looks unusual, it
tells you where to look next. Latency up → dependency
issue or resource contention. Traffic down → routing
failure. Errors up → service bug or dependency down.
Saturation up → approaching capacity limit.

**Level 3 - Framework unification (mid-level):**
Golden Signals = RED + Saturation. For pure service
monitoring: RED is sufficient. For services that
interact with resources (all production services):
add Saturation. The Saturation signal is the one that
is most often missing from dashboards. Without it,
teams are reactive (respond after Latency and Errors
degrade). With it, teams are proactive (scale or fix
before Latency degrades).

**Level 4 - SLO alignment (senior):**
Each Golden Signal maps to an SLI type:

- Latency → Latency SLI (P99 < threshold)
- Errors → Availability SLI (1 - error_rate)
- Traffic → not typically an SLI (context metric)
- Saturation → predictive SLI (saturation < threshold
  before degradation)
  Alerting strategy: Errors and Latency → SLO burn rate
  alerts (page). Traffic anomalies → ticket (routing
  investigation). Saturation approaching limits → ticket
  (capacity planning).

**Level 5 - Organisational standards (staff):**
Enforce Golden Signals as the organisational monitoring
standard: every service must expose all four via the
shared observability library. Platform observability
team builds a "Golden Signals at a glance" dashboard
covering all 200 services. Service quality score:
each service is scored based on Golden Signal SLO
compliance. Services with > 20% Saturation headroom
consumed, > 0.1% Errors, or P99 Latency within 20%
of SLO threshold are flagged for reliability review.
Quarterly engineering health review: Golden Signal
trends per team, per service, reported to engineering
leadership as reliability health indicators.

---

### ⚙️ How It Works (Mechanism)

**PROMETHEUS - ALL FOUR SIGNALS:**

```promql
# ===== LATENCY (P99) =====
# Successful requests only
histogram_quantile(
  0.99,
  sum by (le) (
    rate(http_request_duration_seconds_bucket{
      status!~"5.."}[5m])
  )
)
# Failed requests P99 (track separately)
histogram_quantile(
  0.99,
  sum by (le) (
    rate(http_request_duration_seconds_bucket{
      status=~"5.."}[5m])
  )
)

# ===== TRAFFIC =====
# Requests per second
sum(rate(http_requests_total[5m]))

# ===== ERRORS =====
# Error rate as percentage
100 * (
  sum(rate(http_requests_total{status=~"5.."}[5m]))
  / sum(rate(http_requests_total[5m]))
)

# ===== SATURATION =====
# Most constrained resource - varies by service type.
# For database-backed services: connection pool
hikaricp_connections_pending
  + hikaricp_connections_active
  / hikaricp_connections_max * 100

# For CPU-intensive services: normalized CPU load
node_load1
  / count without(cpu, mode) (
      node_cpu_seconds_total{mode="idle"}
    )

# For memory-intensive: available memory fraction
1 - (
  node_memory_MemAvailable_bytes
  / node_memory_MemTotal_bytes
)
```

**GOLDEN SIGNALS ALERT STRATEGY:**

```yaml
groups:
  - name: golden-signals-checkout
    rules:
      # Latency SLO breach alert (burn rate)
      - alert: CheckoutLatencyBurnRate
        expr: |
          histogram_quantile(0.99,
            sum by (le) (rate(
              checkout_duration_seconds_bucket[1h]
            ))
          ) > 1.0    # P99 > 1s (SLO threshold)
          AND
          histogram_quantile(0.99,
            sum by (le) (rate(
              checkout_duration_seconds_bucket[5m]
            ))
          ) > 1.0
        labels:
          severity: page
          signal: latency

      # Error SLO burn rate alert
      - alert: CheckoutErrorBurnRate
        expr: |
          (
            (1 - sum(rate(checkout_ok_total[1h]))
            / sum(rate(checkout_requests_total[1h])))
          ) / (1 - 0.999) > 14.4
          AND
          (
            (1 - sum(rate(checkout_ok_total[5m]))
            / sum(rate(checkout_requests_total[5m])))
          ) / (1 - 0.999) > 14.4
        labels:
          severity: page
          signal: errors

      # Traffic anomaly alert (not SLO, but routing signal)
      - alert: CheckoutTrafficDrop
        expr: |
          sum(rate(checkout_requests_total[5m]))
          < sum(rate(checkout_requests_total[1h] offset 5m))
            * 0.5    # 50% traffic drop vs 1h-ago baseline
        for: 5m
        labels:
          severity: page
          signal: traffic

      # Saturation alert (predictive - before degradation)
      - alert: CheckoutConnectionPoolSaturation
        expr: hikaricp_connections_pending > 3
        for: 2m
        labels:
          severity: warning
          signal: saturation
        annotations:
          summary: "Connection pool saturated - scale before latency spike"
```

---

### 🔄 The Complete Picture - End-to-End Flow

**GOLDEN SIGNALS INCIDENT CHAIN:**

```
[Normal state]
  Latency P99: 120ms | Traffic: 500 req/s
  Errors: 0.05% | Saturation (pool): 45%
  All healthy.
    ↓
[Traffic spike - marketing campaign starts]
  Traffic: 500 → 1,200 req/s
  Saturation (pool): 45% → 88%  ← first signal
  Latency P99: 120ms → 180ms    ← slight rise
  Errors: 0.05% → 0.07%         ← minimal change
  Alert: "Connection pool saturation > 80% for 2 min"
  Action: scale the service (add pods) or increase pool
  Outcome if actioned: system scales, returns to normal.
  Outcome if ignored: continue...
    ↓
[Pool exhaustion]
  Saturation (pool): 100%
  Latency P99: 180ms → 2,400ms  ← requests waiting for pool
  Errors: 0.07% → 8%            ← pool timeouts = 5xx errors
  Traffic: 1,200 → 950 req/s    ← failed requests dropping off
  Alert: "SLO fast burn rate" (Errors + Latency)
  Action: emergency scale + circuit breaker
    ↓
[Cascade: payment service affected]
  Payment service receives slow/failed checkout calls
  Checkout timeouts = payment service upstream errors
  Payment: Latency elevated, Traffic dropping
  Action: checkout circuit breaker to prevent cascade
    ↓
[Recovery]
  New pods online. Pool pressure drops.
  Saturation: 100% → 55%
  Latency: 2,400ms → 140ms
  Errors: 8% → 0.06%
  Traffic: 950 → 1,100 req/s (normal for traffic level)
  SLO burn rate alert resolves.
```

---

### 💻 Code Example

**Example 1 - BAD: Incomplete signal coverage:**

```yaml
# BAD: monitoring only Errors and Traffic
# Missing Latency (no percentile tracking)
# Missing Saturation (no resource headroom)
# This team will always respond reactively

dashboards:
  - panel: "Error Rate"
    query: rate(errors_total[5m])
  - panel: "Request Rate"
    query: rate(requests_total[5m])
  # Missing: latency percentiles
  # Missing: saturation metric
  # Missing: average latency (even this would be better than nothing)
  # Result: cannot detect performance degradation without errors
  #   cannot see capacity limits approaching
  #   cannot distinguish slow service from failing service
```

**Example 2 - GOOD: All four signals covered:**

```yaml
# GOOD: all four signals in one dashboard row
# Row 1: Golden Signals (always visible, above fold)
# Row 2+: Infrastructure metrics (for diagnosis)

panels:
  row_1_golden_signals:
    - title: "P99 Latency (ms)"
      description: "Successful requests only"
      query: |
        1000 * histogram_quantile(0.99,
          sum by (le) (rate(
            http_request_duration_seconds_bucket{
              status!~"5.."}[5m])))
      thresholds: [500ms warn, 1000ms critical]

    - title: "Traffic (req/s)"
      description: "Used to contextualise other signals"
      query: sum(rate(http_requests_total[5m]))
      thresholds: [50% drop warn, 80% drop critical]

    - title: "Error Rate (%)"
      query: |
        100 * sum(rate(errors_total[5m]))
        / sum(rate(requests_total[5m]))
      thresholds: [0.1% warn, 1% critical]

    - title: "Saturation (pool %)"
      description: "Most constrained resource"
      query: |
        hikaricp_connections_active
        / hikaricp_connections_max * 100
      thresholds: [70% warn, 90% critical]
      annotation: "Approaching 100% = latency spike imminent"
```

**Example 3 - Saturation as predictive signal:**

```promql
# Predict when connection pool saturation will
# reach 100% at current growth rate
# (gives advance warning before latency degrades)

predict_linear(
  hikaricp_connections_active[30m],
  1800     # predict 30 minutes ahead
)
  / hikaricp_connections_max
# Result > 1.0 = pool will be exhausted in < 30 min
# Alert on this to be proactive, not reactive

# Example: if active=14/20 and growing 1/min:
# predict_linear at t+30min = 14 + 30 = 44
# 44/20 = 2.2 (>1.0) → pool exhausted in 6 minutes
# Alert: scale NOW before latency and errors spike
```

---

### ⚖️ Comparison Table

| Signal     | Framework source     | Primary alert?                        | Diagnostic use                    |
| ---------- | -------------------- | ------------------------------------- | --------------------------------- |
| Latency    | RED + Golden Signals | Yes - SLO latency breach              | Distinguish slow vs fast failures |
| Traffic    | RED + Golden Signals | Yes - traffic drop (routing)          | Context for all other signals     |
| Errors     | RED + Golden Signals | Yes - SLO availability breach         | Primary customer impact signal    |
| Saturation | USE + Golden Signals | Yes - predictive (before degradation) | Capacity planning, bottleneck ID  |

**Which framework to use:**

| Need                                  | Use                                         |
| ------------------------------------- | ------------------------------------------- |
| Monitoring a microservice             | RED (subset of Golden Signals)              |
| Monitoring infrastructure (CPU, disk) | USE                                         |
| Unified service + infra monitoring    | Golden Signals                              |
| SLO compliance monitoring             | Golden Signals (Latency + Errors → SLIs)    |
| Capacity planning                     | Golden Signals (Saturation + Traffic trend) |

---

### ⚠️ Common Misconceptions

| Misconception                                      | Reality                                                                                                                                                                                                                                                                    |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Average latency is sufficient for Latency signal" | No. Average hides tail latency. The Google SRE Book explicitly recommends percentiles (P50, P95, P99). Use histogram_quantile over rate(histogram_bucket[5m]).                                                                                                             |
| "Saturation is just CPU utilization"               | Saturation is the most constrained resource for the given service. For database-backed services: connection pool saturation matters more than CPU. For memory-heavy: swap onset. For IO-heavy: disk queue depth. Choose the resource most likely to become the bottleneck. |
| "Errors should include all 4xx responses"          | No. 4xx are usually client errors (bad requests, missing auth). 5xx are server failures. The Errors signal is server-side failures. 4xx spikes may warrant investigation but are not typically SLO-impacting. Exception: 429 rate limiting errors indicate saturation.     |
| "Golden Signals replace RED and USE"               | Golden Signals extend them. RED is sufficient for pure service monitoring. USE is the correct framework for infrastructure-only monitoring. Golden Signals is the unified framework when you need both. Use whichever fits the context.                                    |
| "If Latency is fine, the service is fine"          | Not if Saturation is approaching 100%. A service at 98% connection pool saturation with good Latency has 5-10 minutes before a traffic spike triggers a cascade failure. Saturation is the signal Latency does not capture until it is too late.                           |

---

### 🚨 Failure Modes & Diagnosis

**Missing the saturation signal: reactive ops**

**Symptom:**
The team has a great error rate and latency dashboard.
They have never missed an outage in 6 months. But
they are always responding to incidents. Post-mortems
consistently show "traffic spike caused latency
degradation." The incidents are 15-30 minutes long.
The team responds fast but the recovery takes time
(scaling takes 5-10 minutes after the alert fires).

**Root Cause:**
No Saturation signal. The team only knows about
the problem when Latency and Errors degrade (after
the resource hits 100% capacity). With a Saturation
signal (connection pool > 80%, CPU saturation > 0.8),
the team would be alerted before degradation and
could scale proactively.

**Fix:**
Add the Saturation signal to the dashboard and create
a warning-level alert at 80% saturation (ticket,
not page). This gives 5-15 minutes of advance warning
before the service hits capacity. With autoscaling
(Kubernetes HPA), the saturation metric can trigger
scaling automatically before degradation occurs.

---

**Latency tracked as average - missing tail degradation**

**Symptom:**
The dashboard shows average latency 85ms (normal).
But 1% of users are experiencing 8-second timeouts.
A customer complaint escalates to the engineering
VP. The dashboard shows no anomalies. The team
initially disputes the user complaint - "our
dashboards show everything is fine."

**Root Cause:**
Average latency masks tail latency. With 99% of
requests at 50ms and 1% at 8,000ms:
Average = (99 x 50 + 1 x 8000) / 100 = (4950+8000)/100
= 129.5ms. Looks normal compared to 85ms baseline.

**Fix:**
Replace average latency with `histogram_quantile(0.99, ...)`
P99 would show 8,000ms immediately - a clear anomaly.
Always use histogram metrics for latency, never gauge/
summary averages.

```java
// BAD: gauge or summary metric for latency
// Cannot compute percentiles accurately
Gauge.builder("request_latency_ms")
  .register(registry);  // Only average is computed

// GOOD: histogram for latency
// Allows accurate percentile computation
Timer.builder("request_duration_seconds")
  .publishPercentileHistogram(true)  // Creates buckets
  .sla(Duration.ofMillis(500),       // Buckets at SLO
       Duration.ofSeconds(1),
       Duration.ofSeconds(2))
  .register(registry);
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Metrics -- Types (Counter, Gauge, Histogram)` -
  all four signals use these metric types
- `RED Method` - subset of Golden Signals (Rate +
  Errors + Duration)
- `USE Method` - source of the Saturation signal

**Builds On This (learn these next):**

- `SLO-Based Alerting Strategy` - each signal feeds
  into SLO burn rate alerting
- `Platform Observability Engineering` - applying
  Golden Signals as an organisation-wide standard
- `Dashboards and Visualization Basics` - the practical
  implementation of Golden Signals in Grafana

**Alternatives / Comparisons:**

- `RED Method` - simpler (3 signals). Use when
  Saturation monitoring is out of scope.
- `USE Method` - infrastructure-only (3 signals).
  Use when monitoring resources not services.
- `LETS (Latency, Errors, Traffic, Saturation)` -
  a renaming of Golden Signals. Less common.
  Functionally identical.

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ 4 SIGNALS    │ Latency, Traffic, Errors, Saturation      │
│              │ = RED + Saturation (Google SRE Book)      │
├──────────────┼───────────────────────────────────────────┤
│ LATENCY      │ histogram_quantile(0.99, rate(bucket[5m]))│
│              │ Track success and failure separately       │
│              │ NEVER use average latency                  │
├──────────────┼───────────────────────────────────────────┤
│ TRAFFIC      │ sum(rate(requests_total[5m]))              │
│              │ Context for other signals. Drop = routing  │
│              │ Spike = capacity risk (check Saturation)   │
├──────────────┼───────────────────────────────────────────┤
│ ERRORS       │ rate(errors) / rate(total)                 │
│              │ 5xx = server errors (alert)                │
│              │ 4xx = client errors (investigate)          │
├──────────────┼───────────────────────────────────────────┤
│ SATURATION   │ Most constrained resource for this service │
│              │ Pool: pending/max, CPU: load/nproc         │
│              │ PREDICTIVE: alerts before Latency spikes   │
├──────────────┼───────────────────────────────────────────┤
│ FRAMEWORK    │ RED = Traffic + Errors + Latency           │
│ RELATION     │ USE = Utilization + Saturation + Errors    │
│              │ Golden = RED + Saturation = unified        │
├──────────────┼───────────────────────────────────────────┤
│ DASHBOARD    │ Row 1: all 4 signals (always visible)      │
│ RULE         │ Row 2+: infrastructure for diagnosis       │
│              │ Alert on: Errors + Latency (SLO burn)      │
│              │ Warn on: Saturation (predictive)           │
│              │ Alert on: Traffic drop (routing failure)   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ SLO-Based Alerting, Platform Observability │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Minimum sufficient monitoring beats comprehensive
monitoring. The Four Golden Signals exist because
any fewer signals leave gaps (no Saturation = missing
predictive signal), and adding more signals without
a framework creates noise that slows triage. This
principle - minimum sufficient set for complete coverage

- applies to: code review checklist (correctness,
  security, performance, maintainability = the four
  things every code change must be reviewed for), API
  design (naming, versioning, error handling, authentication
  = four areas every API must address), incident management
  (detect, diagnose, resolve, prevent = four phases
  every incident must go through). Design the minimum
  sufficient checklist for your domain; resist the urge
  to add more items beyond what is needed for complete
  coverage.

---

### 💡 The Surprising Truth

The most counterintuitive Golden Signals insight:
Saturation is the most valuable signal for preventing
incidents, but it is also the most often missing from
dashboards. Most teams add Error and Latency metrics
immediately (they are user-visible). Traffic is often
added as a graph. But Saturation - the predictive
signal that tells you the service is about to
degrade - is frequently absent. The reason: Saturation
requires knowing which resource is most constrained
for a given service, which varies by service type
(connection pool for DB-backed services, memory for
cache services, CPU for compute-heavy services). This
requires thinking about the service's architecture,
not just adding standard metrics. The teams with the
fewest incidents are the teams who have invested in
service-specific Saturation metrics that fire warning
alerts before Latency and Errors are affected.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[EXPLAIN]** Name the Four Golden Signals, explain
   what each measures, and explain why all four are
   needed (what gap each one fills that the others
   cannot).
2. **[COMPARE]** Explain the relationship between
   Golden Signals, RED Method, and USE Method. Show
   which signals overlap and which are unique.
3. **[QUERY]** Write PromQL queries for all four
   Golden Signals for an HTTP service with a
   HikariCP connection pool.
4. **[DESIGN]** Design the Saturation signal for
   three different service types: a stateless REST
   API, a database-backed service, and a message
   queue consumer. Explain why the Saturation metric
   differs for each.
5. **[ALERT]** Design the alerting strategy for a
   service using Golden Signals: which signals get
   page-level alerts, which get ticket-level, and
   which are dashboard-only.

---

### 🧠 Think About This Before We Continue

**Q1.** You are reviewing a monitoring dashboard for
a checkout service. The dashboard shows: Error rate
(excellent), P99 Latency (excellent), Request rate
(normal). Which Golden Signal is missing? Describe
a scenario where the missing signal would have
prevented an incident that the three monitored signals
would have missed until it was too late.
_Hint: Missing: Saturation. Scenario: checkout service
connection pool is at 85% and growing (traffic spike
from a sale). Errors: 0.05% (normal). Latency P99:
150ms (normal). Traffic: 600 req/s (slightly elevated).
Without Saturation, no alert fires. In 8 minutes,
pool hits 100%, requests start waiting, P99 spikes to
3s, errors spike to 12%. With Saturation alert at
80%, the team gets a warning-level alert 8 minutes
earlier - enough time to scale before degradation._

**Q2.** Two services show identical Red/Error metrics:
both have 5% error rate and P99 latency 500ms. But
Service A has Traffic = 10 req/s, Service B has
Traffic = 10,000 req/s. How does the Traffic signal
change the severity interpretation of the same
Error and Latency values?
_Hint: Service A: 5% of 10 req/s = 0.5 errors/s.
At 500ms P99: 1-2 users affected at any time. Minor
incident, likely a test service or low-criticality
endpoint. Service B: 5% of 10,000 req/s = 500 errors/s.
At P99 500ms: 250 users experiencing slow or failed
responses every second. This is a major incident. Same
Error% and Latency values = completely different severity
without Traffic context. Traffic signal provides the
scale factor that converts percentages into absolute
user impact._

**Q3 (TYPE G):** You are joining a 300-person engineering
organisation. They have 150 services with inconsistent
monitoring: some use RED, some use infrastructure-only
dashboards, some have no standard monitoring at all.
Design a 6-month program to standardise all 150
services on Golden Signals. Include: (a) the technical
implementation (what shared library, what metrics
convention), (b) the rollout strategy (how to migrate
150 services without disrupting them), (c) the
governance model (how new services adopt the standard),
(d) the cross-service dashboard (how leadership sees
the organisational health), (e) the incentive structure
(why teams will comply).
_Hint: Month 1: Design the shared library (OTel
instrumentation, metric naming standard, the four
signals pre-wired for HTTP services). Month 2-3:
Pilot with 10 willing teams. Fix issues. Month 3-4:
Rolling adoption, team by team. Priority: customer-
facing services first. Month 5-6: Remaining services,
including legacy. Governance: new services MUST use
the shared library (enforced in service template/
Cookiecutter). Migration: old services can run parallel
(old + new metrics) during migration window. Cross-service
dashboard: Grafana with service variable, all four
signals, traffic-weighted health score. Incentive:
quarterly reliability health score published per team,
Golden Signals compliance is a prerequisite for reliability
score computation. Teams without compliant monitoring
receive "monitoring debt" label in engineering
all-hands._

---

### 🎯 Interview Deep-Dive

**Q1: "What are the Four Golden Signals and why
were they defined?"**
_Why they ask:_ Standard SRE vocabulary test.
_Strong answer includes:_

- Latency, Traffic, Errors, Saturation. Google SRE Book.
- Latency: how long requests take (successful and failed separately)
- Traffic: how much demand (req/s for web, transactions for storage, etc.)
- Errors: how many requests fail (5xx rate, policy violations)
- Saturation: how full the system is (most constrained resource)
- Why defined: minimum sufficient signal set. Any fewer
  leaves blind spots. Any more without a framework
  creates noise that slows triage.

**Q2: "What is the difference between Latency in Golden
Signals and Duration in RED Method?"**
_Why they ask:_ Tests depth of understanding, not just
term recitation.
_Strong answer includes:_

- Functionally equivalent. Both measure request processing time.
- Golden Signals adds one nuance: track successful-request
  latency and failed-request latency separately.
- Fast failures (5ms 503 errors) indicate circuit breaker
  or health check failure → routing/availability issue.
- Slow failures (30s timeout errors) indicate resource
  exhaustion → threads held, connection pool pressure.
- Same error rate (5%) but different failure latency =
  completely different root cause and fix.
- RED Duration typically does not make this distinction
  explicitly. This is the one place where Golden Signals
  adds value over bare RED.

**Q3: "How does the Saturation signal differ from
Errors and Latency, and what unique value does it provide?"**
_Why they ask:_ Discriminates engineers who understand
the predictive nature of Saturation.
_Strong answer includes:_

- Latency and Errors are reactive: they show a problem
  AFTER it has happened and users are affected.
- Saturation is predictive: it shows a resource is
  approaching its limit BEFORE users are affected.
- Brendan Gregg note in Google SRE Book: "latency
  usually increases as saturation approaches 100%."
  Saturation is the leading indicator.
- Value: allows proactive response (scale before incident)
  vs reactive response (scale after incident).
- Example: connection pool at 85% (Saturation) →
  no user impact yet. Alert at 85% → scale in 5 min
  → no incident. Without Saturation: alert fires when
  pool hits 100% and latency spikes → incident in progress
  → 10-15 min to scale → 10-15 min of user impact.
- Best Saturation metric varies by service type: choose
  the most constrained resource for each specific service.

---

# OBS-026 - Golden Signals

> Entry stub. Generate full content using Master Prompt v3.0.
