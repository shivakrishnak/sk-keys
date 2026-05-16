---
id: OBS-006
title: "Metrics -- Types (Counter, Gauge, Histogram)"
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★☆☆
depends_on: OBS-002
used_by: OBS-009, OBS-010, OBS-011
related: OBS-002, OBS-005, OBS-009
tags:
  - observability
  - metrics
  - foundational
  - first-principles
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 6
permalink: /obs/metrics-types-counter-gauge-histogram/
---

# OBS-006 - Metrics -- Types (Counter, Gauge, Histogram)

⚡ TL;DR - Counters monotonically increase, gauges measure
current state, and histograms bucket observations so you can
calculate latency percentiles and SLOs from raw data.

| #006 | Category: Observability & SRE | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | The Three Pillars of Observability | |
| **Used by:** | Alerting Fundamentals, Dashboards, SLI | |
| **Related:** | Three Pillars, SRE, Alerting Fundamentals | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without a typed metric system, teams instrument their code
inconsistently. One engineer records request counts as a
number that resets to zero on every restart. Another tracks
the same metric by storing the total count but subtracting
on process restart. A third adds a timestamp to each
sample to detect when the process restarted and corrects
the graph manually. When you try to build a dashboard
showing request rate across 12 services, each with its own
metric convention, the dashboard is meaningless.

**THE BREAKING POINT:**
As systems scale, ad-hoc metric formats break in two ways.
First, you cannot do mathematics across metrics that
represent different things (a total count and a windowed
count cannot be added). Second, calculating percentile
latencies (P50, P95, P99) from raw averages is
statistically incorrect - averaging averages does not give
you the average. You need the raw distribution.

**THE INVENTION MOMENT:**
Prometheus (2012, originally at SoundCloud) introduced a
four-type metric taxonomy - counter, gauge, histogram,
summary - that gives every metric a clear mathematical
identity. When you know the type, you know the legal
operations: rate() on a counter, delta() on a gauge,
histogram_quantile() on a histogram.

---

### 📘 Textbook Definition

**Metrics** are numerical measurements collected over time
from a system. They are the most efficient signal type in
the observability stack: high cardinality is possible at
low cost, and they support mathematical operations that logs
cannot.

**The four Prometheus metric types:**
- **Counter:** monotonically increasing value. Only goes up
  (or resets to zero on restart). Examples: total requests,
  total errors, bytes sent.
- **Gauge:** current value at a point in time. Can go up or
  down. Examples: current memory usage, queue depth, active
  connections.
- **Histogram:** pre-configured buckets that count observations
  falling within each range. Allows calculation of percentile
  latencies (P95, P99). Examples: request duration, response
  size.
- **Summary:** client-side pre-calculated quantiles. Less
  flexible than histograms for aggregation but requires no
  server-side calculation. Rarely used in modern stacks.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A counter measures how many times something happened; a
gauge measures the current state; a histogram tells you the
distribution of how long something took.

> Think of a car's instrumentation. The odometer is a
> counter: it only ever increases and measures total distance
> travelled. The fuel gauge is a gauge: it shows current
> state and can go up (after fuelling) or down (while
> driving). The speedometer at every moment is a gauge too.
> If you wanted to know "what percentage of my trips were
> shorter than 30 minutes?" you need a histogram: you'd need
> a record of every trip duration, grouped into buckets.

**One insight:**
The type determines the legal query operations. You never
call `avg()` on a counter - you call `rate()` to get the
per-second rate. You never call `rate()` on a gauge. The
type system prevents you from computing nonsense metrics,
which is the source of most incorrect dashboards.

---

### 🔩 First Principles Explanation

**WHY THREE TYPES CAPTURE EVERYTHING:**

Every observable system property is either:
1. An accumulation over time (counter) - e.g., "how many
   requests have arrived since this process started?"
2. A current instantaneous state (gauge) - e.g., "how much
   memory is in use right now?"
3. A distribution of observed values (histogram) - e.g.,
   "what is the spread of request durations?"

You cannot derive distributions from counters or gauges.
You cannot derive current state from a counter. These three
types are orthogonal: each captures something the others
cannot.

**THE MATHEMATICS:**

Counter:
```
rate(counter[5m]) = per-second rate over 5-minute window
increase(counter[1h]) = total increase over 1 hour
```

Gauge:
```
avg_over_time(gauge[1h]) = average over last hour
max_over_time(gauge[1d]) = peak over last day
delta(gauge[5m]) = change over 5 minutes
```

Histogram:
```
histogram_quantile(0.99, rate(histogram_bucket[5m]))
  = P99 latency over 5-minute window
```

**TRADE-OFFS:**
**Gain:** Type-safe arithmetic. Cross-service aggregation
works correctly. P99 latency can be calculated accurately.
SLOs can be defined on histogram percentiles.
**Cost:** Histograms require pre-configured buckets. If
your latency distribution moves outside the buckets, you
lose accuracy. Bucket selection is an upfront design
decision.

---

### 🧪 Thought Experiment

**SETUP:**
Two teams each build a checkout service and expose a metric
called `checkout_duration_seconds`. Team A stores it as a
gauge set to the last request's duration. Team B stores it
as a histogram with buckets at 0.1, 0.25, 0.5, 1, 2.5, 5s.

**TEAM A PROBLEM:**
Three months later, a product manager asks: "What percentage
of checkout requests took more than 1 second last Tuesday?"
Team A cannot answer. The gauge only stores the current
(last) value. There is no distribution. Team A's average
latency looks fine at 250ms, but several users experience
5-second checkouts. The gauge average masks the long tail.

**TEAM B ANSWER:**
```promql
histogram_quantile(0.99,
  sum(rate(checkout_duration_seconds_bucket
    [1h])) by (le))
```
Team B can calculate P99 latency, identify that 1% of
requests take more than 3.5 seconds, and correlate this
with a specific region.

**THE INSIGHT:**
The choice of metric type at instrumentation time determines
what questions you can answer at query time. Changing from
gauge to histogram later requires rewriting all dashboards
and alerts. Type the metric correctly the first time.

---

### 🧠 Mental Model / Analogy

> Think of an airline's flight operations monitoring.
> "Total flights operated this year" is a counter: it only
> goes up. "Number of gates currently occupied" is a gauge:
> it rises and falls with departures and arrivals.
> "Distribution of on-time performance across all flights
> this year" - what percentage were within 15 minutes, what
> percentage were 15-60 minutes late, what percentage were
> over 60 minutes late - that is a histogram.

You could try to derive the on-time distribution from total
flights (a counter) and total delay (a gauge), but you lose
the shape of the distribution. You would know the average
delay is 12 minutes, but not that 5% of flights are delayed
by more than 2 hours - which is the number that matters to
customers.

**Where this analogy breaks down:** Airline metrics are
measured per flight (low cardinality). Service metrics can
have very high cardinality (millions of requests per
second). Histograms pre-aggregate into buckets to handle
this scale - they do not store individual observations.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone):**
There are three types of numbers in monitoring. A counter
counts total events (keeps going up). A gauge measures
current state (can go up or down). A histogram tracks the
distribution of something like request time.

**Level 2 - How to use it (junior developer):**
Use a counter for things that accumulate: requests, errors,
bytes sent. Use a gauge for current snapshots: memory,
queue depth, active connections. Use a histogram for latency
and response sizes where you need P99 calculations.

**Level 3 - How it works (mid-level):**
Counters reset to zero when a process restarts. The `rate()`
function in Prometheus handles resets automatically. Gauges
can be read directly. Histograms expose three series:
`_bucket` (cumulative counts per bucket), `_count` (total
observations), `_sum` (total of all observed values). P99
is computed server-side from the `_bucket` series.

**Level 4 - Why it matters (senior/staff):**
Histogram bucket selection is critical. If your service
normally responds in 50-200ms but buckets are configured
at 0.1, 0.5, 1.0, 5.0 seconds, all your normal traffic
falls in the 0.1-0.5s bucket. You cannot distinguish between
a 50ms and a 400ms response. The buckets must be defined
around your actual latency distribution. The standard
Prometheus defaults (5ms, 10ms, 25ms, 50ms, ..., 10s) are
a good starting point but must be tuned per service.

**Level 5 - Mastery (distinguished engineer):**
The most important histogram insight: `histogram_quantile()`
uses linear interpolation within buckets. The result is an
estimate, not an exact percentile. For SLO violation alerts
("alert if P99 exceeds 500ms"), this estimation error
matters. Design histogram buckets so that the bucket
boundaries bracket your SLO threshold. If your SLO is P99 <
500ms, have buckets at both 250ms and 500ms. This minimises
interpolation error at the threshold you care about.
At scale, histograms from multiple instances can be summed
before applying `histogram_quantile()` because their bucket
structures are identical. This is a key advantage over
summaries, which cannot be aggregated across instances.

---

### ⚙️ How It Works (Mechanism)

**Counter internals:**
```
A counter is a 64-bit float that only increases.
In Prometheus, the counter is exposed via /metrics as:
  http_requests_total{status="200"} 47382
Prometheus scrapes this every 15s and stores the value.
rate(http_requests_total[5m]) computes:
  (latest_value - oldest_value_5m_ago) / 300 seconds
If a reset is detected (latest < oldest), rate() handles
it by treating the entire increase after the reset as
the delta (avoiding a negative rate).
```

**Gauge internals:**
```
A gauge is the current value at scrape time.
No rate() needed. Read directly or use avg_over_time.
  process_resident_memory_bytes 134217728
```

**Histogram internals:**
```
A histogram maintains N+3 time series:
  - _bucket{le="0.1"}: count of obs <= 0.1s
  - _bucket{le="0.25"}: count of obs <= 0.25s
  - ...
  - _bucket{le="+Inf"}: count of all observations
  - _count: total observations (= _bucket{le="+Inf"})
  - _sum: sum of all observed values

The buckets are cumulative (each includes all smaller).
histogram_quantile(0.99, rate(..._bucket[5m])):
  1. Compute rate() on each bucket series
  2. Find the bucket where 99% of observations fall
  3. Linear-interpolate within that bucket for exact value
```

---

### 🔄 The Complete Picture - End-to-End Flow

**FLOW FROM CODE TO DASHBOARD:**

```
[Application code]
  checkout_duration.observe(elapsed_ms / 1000)
        ↓
[Prometheus client library]
  increments the correct bucket in memory
  exposes /metrics endpoint
        ↓
[Prometheus server scrapes /metrics every 15s]
  stores time series:
  checkout_duration_seconds_bucket{le="0.5"} 9821
  checkout_duration_seconds_bucket{le="1.0"} 9990
  checkout_duration_seconds_count 10000
  checkout_duration_seconds_sum 4821.3
        ↓
[SRE team ← YOU ARE HERE: Grafana query]
  histogram_quantile(0.99,
    sum(rate(checkout_duration_seconds_bucket[5m]))
    by (le))
  Result: 0.94s (P99 latency is 940ms)
        ↓
[Alert rule]
  P99 > 0.5s → fire alert
```

**WHAT CHANGES AT SCALE:**
At 10,000 instances, the `sum(rate(...))` aggregation in the
Prometheus query sums bucket series across all instances
before applying `histogram_quantile()`. This produces a
global P99. The bucket structure must be identical across
all instances. Remote write to a long-term storage system
(Thanos, Cortex, Mimir) allows querying across months.

---

### 💻 Code Example

**Example 1 - BAD: Wrong metric type for latency:**

```java
// BAD: using a gauge for request duration
// You can only read the LAST request's duration.
// You cannot calculate P99. You cannot see the distribution.
// Average of this gauge is meaningless across time.
private final AtomicDouble lastRequestDuration =
    new AtomicDouble();

public void processRequest() {
    long start = System.nanoTime();
    // ... process ...
    double elapsed = (System.nanoTime() - start) / 1e9;
    lastRequestDuration.set(elapsed); // WRONG TYPE
}
```

**Example 2 - GOOD: Correct types per purpose:**

```java
// GOOD: counter for totals, histogram for latency
import io.prometheus.client.Counter;
import io.prometheus.client.Histogram;

// Counter: only counts total requests (monotonically inc)
static final Counter requests = Counter.build()
    .name("checkout_requests_total")
    .labelNames("status") // "success" or "error"
    .help("Total checkout requests")
    .register();

// Histogram: captures latency distribution with SLO-aware
// buckets. Bucket boundaries chosen around SLO (500ms)
static final Histogram duration = Histogram.build()
    .name("checkout_duration_seconds")
    .help("Checkout request duration")
    .buckets(0.05, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0)
    //       50ms 100ms             500ms (SLO threshold)
    .register();

// Gauge: current queue depth (can go up or down)
static final Gauge queueDepth = Gauge.build()
    .name("checkout_queue_depth")
    .help("Items waiting to be processed")
    .register();

public void processRequest() {
    Histogram.Timer timer = duration.startTimer();
    try {
        // ... process ...
        requests.labels("success").inc();
    } catch (Exception e) {
        requests.labels("error").inc();
        throw e;
    } finally {
        timer.observeDuration();
    }
}
```

**Example 3 - PromQL: Correct queries per type:**

```promql
# Counter: rate (per-second request rate over 5 min)
rate(checkout_requests_total[5m])

# Counter: error ratio for SLO
sum(rate(checkout_requests_total{status="error"}[5m]))
/ sum(rate(checkout_requests_total[5m]))

# Gauge: current queue depth and max over 1 hour
checkout_queue_depth
max_over_time(checkout_queue_depth[1h])

# Histogram: P99 latency - THIS IS THE KEY QUERY
histogram_quantile(
  0.99,
  sum(rate(checkout_duration_seconds_bucket[5m])) by (le)
)

# Histogram: % of requests under SLO (< 500ms)
sum(rate(checkout_duration_seconds_bucket{le="0.5"}[5m]))
/ sum(rate(checkout_duration_seconds_count[5m]))
```

---

### ⚖️ Comparison Table

| Type | What it measures | Resets? | Key PromQL op | Use for |
|---|---|---|---|---|
| **Counter** | Total accumulated events | Yes (on restart) | `rate()`, `increase()` | Requests, errors, bytes |
| **Gauge** | Current instantaneous value | N/A | `avg_over_time()`, `delta()` | Memory, queue depth, connections |
| **Histogram** | Distribution of observations | Yes (on restart) | `histogram_quantile()` | Latency, response size, SLOs |
| **Summary** | Pre-calculated quantiles | Yes (on restart) | Direct read | Simple percentiles, no aggregation needed |

**When to choose histogram vs summary:**
- Use histogram when you need to aggregate across multiple
  instances or compute quantiles server-side in Prometheus.
- Use summary only when the quantile is computed client-side
  and you will never aggregate across instances (rare).
- In practice: always use histogram for latency.

---

### 🔁 Flow / Lifecycle

**Lifecycle of a histogram observation:**

```
[1] Code instruments checkout handler
    Histogram.observe(0.34s)
        ↓
[2] Client library increments memory counters
    bucket{le="0.5"}: 9821 → 9822
    _count: 9999 → 10000
    _sum: 4820.96 → 4821.30
        ↓
[3] Prometheus scrapes /metrics (every 15s default)
    Reads all bucket/count/sum values
    Stores as time series with timestamp
        ↓
[4] Query engine receives PromQL
    histogram_quantile(0.99, rate(_bucket[5m]))
        ↓
[5] rate() applied per bucket series
    Calculates per-second rate of each bucket
        ↓
[6] histogram_quantile() finds 99th percentile
    Linear interpolation within target bucket
    Returns: 0.94 (940ms P99)
        ↓
[7] Alert rule evaluates P99 > 0.5s → FIRES
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Use average latency for dashboards" | Average hides outliers. P99 latency is what your slowest 1% of users experience. A 250ms average can coexist with a 5-second P99. Always use histogram percentiles. |
| "A counter that resets breaks rate()" | Prometheus `rate()` detects counter resets automatically and adjusts the calculation. A restart does not corrupt your rate metric. |
| "Gauges work for latency tracking" | A gauge stores only the most recent observation. You cannot calculate percentiles. You cannot see the distribution. Use a histogram for any latency measurement. |
| "Histogram bucket selection doesn't matter" | If buckets are too wide, `histogram_quantile()` interpolates over a large range and is inaccurate. Bucket boundaries should bracket your SLO thresholds. |
| "Summary and histogram are interchangeable" | Summaries cannot be aggregated across instances (you cannot average pre-calculated quantiles). Histograms can. For any distributed service, use histograms. |
| "More buckets are always better" | Each histogram bucket adds a time series. With high cardinality labels, many buckets can cause Prometheus memory pressure. Use the minimum number of buckets that cover your SLO thresholds. |

---

### 🚨 Failure Modes & Diagnosis

**Histogram bucket misconfiguration causing incorrect P99**

**Symptom:**
The P99 latency dashboard shows 499ms consistently, never
crossing the 500ms SLO threshold. Users are complaining
about slow checkouts. The SLO appears healthy.

**Root Cause:**
The histogram has a single bucket at `le="0.5"` (500ms).
All requests up to 500ms fall in this bucket. All requests
over 500ms fall in the `+Inf` bucket. `histogram_quantile()`
interpolates between these two buckets. If only 2% of
requests exceed 500ms, the P99 falls inside the 0-500ms
bucket and interpolates to ~490ms regardless of whether
the actual P99 is 250ms or 499ms.

**Diagnostic Command:**
```promql
# Check raw bucket distribution to see where observations
# actually fall - look for most traffic in one bucket
rate(checkout_duration_seconds_bucket[5m])
```

If almost all traffic is in one bucket, the resolution is
too low to distinguish request durations.

**Fix:**
Add buckets within your expected distribution range. If
most requests complete in 50-500ms, use buckets at 50ms,
100ms, 150ms, 200ms, 250ms, 300ms, 400ms, 500ms.

**Prevention:**
Define histogram bucket boundaries based on the actual
latency distribution from load testing, not default values.

---

**Using `avg()` on a counter instead of `rate()`**

**Symptom:**
A dashboard shows "average checkout requests" that jumps
from 50,000 to 90,000 with no corresponding traffic change.
The metric appears unstable.

**Root Cause:**
`avg(checkout_requests_total)` returns the average of the
raw counter value across instances. The total increases by
thousands each second. When an instance restarts, it
introduces a lower counter value, skewing the average.

**Diagnostic Command:**
```promql
# Compare the two queries
avg(checkout_requests_total)       # WRONG - jumps
rate(checkout_requests_total[5m])  # CORRECT - stable rate
```

**Fix:**
Replace all `avg()` on counter metrics with `rate()` or
`increase()`. Alert if the dashboard uses `avg()` on any
`_total` metric.

**Prevention:**
Code review metric queries. A `sum()` or `avg()` on a
counter is almost always wrong.

---

**High cardinality histogram labels exhausting Prometheus memory**

**Symptom:**
Prometheus memory usage grows steadily until it OOMs and
restarts. After restart, memory grows again at the same
rate.

**Root Cause:**
A histogram has a label with high cardinality (e.g.,
`user_id` or `request_id`). Each unique label combination
creates N+3 time series (one per bucket, plus count, sum,
and the base series). With 100,000 unique users, a histogram
with 10 buckets creates 1,300,000 time series.

**Diagnostic Command:**
```bash
# Check cardinality of all series
curl -s localhost:9090/api/v1/label/__name__/values \
  | jq '.data | length'

# Find high-cardinality labels
curl -s "localhost:9090/api/v1/query?query=\
topk(10, count by (__name__)({__name__=~\".+\"}))" \
  | jq '.data.result'
```

**Fix:**
Remove high-cardinality labels from histograms. If user-
level latency is needed, use distributed tracing (one
span per request) not metrics (one series per user).

**Prevention:**
Enforce a cardinality budget per metric. Never use request
ID, user ID, session ID, or URL path as metric labels.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `The Three Pillars of Observability` - metrics are one
  of the three signal types; understanding their role in
  the observability stack provides context for why type
  correctness matters

**Builds On This (learn these next):**
- `Alerting Fundamentals` - SLO burn rate alerts are built
  on counter and histogram metrics using `rate()` and
  `histogram_quantile()`
- `SLI (Service Level Indicator)` - SLIs are defined as
  PromQL expressions over counters and histograms
- `Dashboards and Visualization Basics` - correct dashboard
  queries depend on knowing the metric type

**Alternatives / Comparisons:**
- `StatsD metric types` - similar taxonomy (counter, gauge,
  timer) used by StatsD/Telegraf ecosystem
- `OpenTelemetry metrics` - extends the Prometheus taxonomy
  with UpDownCounter and Observable variants

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ COUNTER      │ Only goes up. Use rate() for per-sec      │
│              │ rate. Use increase() for window total.    │
│              │ Example: requests_total, errors_total     │
├──────────────┼───────────────────────────────────────────┤
│ GAUGE        │ Current state. Up or down.                │
│              │ Read directly or avg_over_time()          │
│              │ Example: memory_bytes, queue_depth        │
├──────────────┼───────────────────────────────────────────┤
│ HISTOGRAM    │ Distribution in pre-set buckets.          │
│              │ Use histogram_quantile() for P99.         │
│              │ Example: request_duration_seconds         │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULE     │ Never avg() a counter.                    │
│              │ Never use gauge for latency.              │
│              │ Never avg() pre-aggregated percentiles.   │
├──────────────┼───────────────────────────────────────────┤
│ P99 QUERY    │ histogram_quantile(0.99,                  │
│              │   sum(rate(name_bucket[5m])) by (le))     │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ avg(checkout_duration_seconds) - WRONG   │
│              │ This averages last observation per inst.  │
├──────────────┼───────────────────────────────────────────┤
│ BUCKET TIP   │ Add bucket at your SLO threshold value   │
│              │ to minimise interpolation error           │
├──────────────┼───────────────────────────────────────────┤
│ CARDINALITY  │ Never use user_id, request_id, URL path  │
│              │ as metric labels - one series per value  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ SLI definition → SLO alerts → Dashboards │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Counter counts total events (only up). Use `rate()` to
   get a per-second rate. Never use `avg()` on a counter.
2. Gauge is current state (up or down). Read directly.
3. Histogram buckets observations into pre-configured ranges.
   Use `histogram_quantile(0.99, ...)` to get P99 latency.
   Buckets must be placed at your SLO threshold for accuracy.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Choose the data structure that preserves the mathematical
operations you need, not the simplest structure that stores
the value. A float gauge stores a duration number, but
loses the distribution. A histogram is more complex but
enables the percentile arithmetic that SLOs require. This
principle applies everywhere: choosing a sorted list vs a
hash map, or choosing an event log vs a snapshot.

**Where else this pattern appears:**
- **Percentile calculations in statistics** - you cannot
  calculate the median of medians (Savage's inequality).
  To aggregate percentiles, you must aggregate the
  underlying distributions - same reason histogram buckets
  can be summed but summary quantiles cannot.
- **Database query optimisation** - choosing an index type
  (B-tree for range, hash for equality) based on the query
  operations you need, not the storage simplicity.
- **Stream processing** - HyperLogLog for cardinality
  estimation, Count-Min Sketch for frequency estimation.
  The data structure determines which questions you can
  answer accurately and which are approximations.

---

### 💡 The Surprising Truth

The most counterintuitive fact about histograms:
`histogram_quantile()` is an estimate, not an exact
calculation. Prometheus histograms do not store individual
observations - they only count how many observations fall
within each pre-configured bucket. The P99 is estimated
by linear interpolation within the bucket that contains
the 99th percentile. This means that if your P99 is
exactly at a bucket boundary, the result is precise; if
it is in the middle of a wide bucket, the estimate can
be significantly off. This is why bucket selection matters:
designing buckets around your SLO threshold improves
accuracy where it counts most.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **[EXPLAIN]** Explain to a junior developer why they
   should not use a gauge to track request latency, and
   demonstrate what information is lost compared to a
   histogram by showing what PromQL queries become
   impossible.
2. **[DEBUG]** Given a Grafana dashboard where P99 latency
   appears to never exceed 450ms but users report 5-second
   checkouts, diagnose the histogram bucket misconfiguration
   and propose corrected bucket boundaries.
3. **[DECIDE]** For a new API endpoint with an SLO of P99 <
   500ms, choose the correct metric type, define the bucket
   boundaries, write the PromQL query for the SLO dashboard,
   and write the alert rule that fires when P99 exceeds 500ms.
4. **[BUILD]** Instrument a Java Spring Boot checkout handler
   with a counter (requests_total with status label), a
   histogram (request duration), and a gauge (queue depth),
   using the Prometheus Java client library. Write unit
   tests that verify the counter increments and the histogram
   records observations.
5. **[EXTEND]** Explain why Prometheus histograms can be
   aggregated across instances with `sum()` before applying
   `histogram_quantile()`, but pre-calculated summary
   quantiles cannot. Demonstrate with a PromQL example
   showing correct vs incorrect aggregation.

---

### 🧠 Think About This Before We Continue

**Q1.** You are building an e-commerce checkout service with
an SLO of P99 latency < 500ms. You need to instrument it.
The junior developer on your team proposes using a gauge
that records the duration of each request. You use a
histogram instead. Three months later, an incident occurs
where checkout latency spikes to 3 seconds for 2% of users
for 45 minutes. Walk through exactly what information the
gauge approach vs the histogram approach gives you during
the post-mortem. What questions can you answer with one
but not the other?
*Hint: Think about: what percentage of requests were
affected? When exactly did the spike start? Which region?
Which service version? The gauge can tell you that the
last request duration was 3 seconds. The histogram can
tell you the P99 over time, the bucket distribution, and
the rate of requests exceeding the SLO.*

**Q2.** A Prometheus histogram named `api_latency_seconds`
has buckets at [0.1, 0.5, 1.0, 5.0, +Inf]. Your SLO is
P99 < 500ms. Traffic is normally distributed with 95% of
requests completing in 100-500ms. A PromQL query returns
P99 = 498ms. An engineer says "we're fine, just under the
SLO." You suspect the bucket configuration is masking
actual P99 violations. How would you investigate, and how
would you reconfigure the buckets to get accurate P99
measurement near the 500ms threshold?
*Hint: With a bucket at 0.5s (500ms) as the upper bound
for most traffic, `histogram_quantile()` interpolates from
0 to 500ms. The estimated P99 will always be below 500ms
unless more than 1% of requests exceed 500ms. Add buckets
within the 100-500ms range to see the actual distribution.*

**Q3 (TYPE G):** Design a metric schema for a payment
gateway service that receives 10,000 requests per second
from 5 million unique users. You need to meet these
requirements: (1) P99 latency SLO alert, (2) error rate
by payment method (credit, debit, PayPal), (3) current
active payment sessions, (4) total payments processed by
currency. Define each metric (name, type, labels),
calculate the total number of time series at steady state,
and identify any cardinality risks. Show the PromQL query
for each requirement.
*Hint: 4 payment methods x 3 status labels = 12 counter
series. 10 histogram buckets x 4 payment methods = 60
histogram series. Gauge: 1 series. But what if you label
by user_id? 5 million users x 10 buckets = 50 million
series - Prometheus OOM. The lesson: labels must be finite,
bounded, and low-cardinality.*

---

### 🎯 Interview Deep-Dive

**Q1: "What is the difference between a counter and a
gauge in Prometheus? Give an example of when you would
use each."**
*Why they ask:* Tests whether the candidate has actually
instrumented services, not just read about monitoring.
*Strong answer includes:*
- Counter is monotonically increasing, only resets on
  process restart. Use for: requests_total, errors_total,
  bytes_sent_total. Query with rate() or increase().
- Gauge is current state, can go up or down. Use for:
  memory_bytes, queue_depth, active_connections. Read
  directly or use avg_over_time() / max_over_time().
- The tell: a strong candidate immediately mentions
  that using avg() on a counter is wrong and will give
  meaningless results. They know to use rate() instead.

**Q2: "Why should you use a histogram instead of a gauge
for request latency?"**
*Why they ask:* Tests understanding of statistical
correctness in observability. Candidates who only know
average latency will fail this question.
*Strong answer includes:*
- Gauge stores only the last observed value - cannot
  calculate P99, P95, or any percentile
- histogram_quantile(0.99, ...) gives you the latency
  that 99% of requests complete within
- Averaging a gauge is wrong - average of averages is
  not the average
- Key insight: P99 latency is what your slowest 1% of
  users experience. A 250ms average with a 3-second P99
  means 1% of users wait 12x longer than average. Without
  histograms, you cannot see this.

**Q3: "Explain why Prometheus histogram quantiles can be
aggregated across instances but Prometheus summary
quantiles cannot."**
*Why they ask:* Tests deep understanding of histogram
internals. This is a senior-level question.
*Strong answer includes:*
- Histograms store bucket counts (how many observations
  <= each threshold). Buckets are identical across all
  instances. You can sum bucket counts across instances:
  `sum(rate(latency_bucket[5m])) by (le)` gives the
  combined distribution. Then `histogram_quantile()`
  computes the global P99.
- Summaries compute quantiles client-side per instance.
  Each instance stores its own P99. You cannot average
  pre-computed quantiles: the average of two P99 values
  is not the P99 of the combined distribution. (If
  instance A's P99 is 100ms and instance B's P99 is
  900ms, the combined P99 could be anywhere between
  100ms and 900ms depending on the relative traffic.)
- In practice: always use histograms for distributed
  services. Never use summaries when you need to
  aggregate across instances.
