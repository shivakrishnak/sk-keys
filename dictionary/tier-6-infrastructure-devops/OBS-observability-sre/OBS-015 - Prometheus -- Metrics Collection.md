---
id: OBS-015
title: "Prometheus -- Metrics Collection"
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★☆
depends_on: OBS-006, OBS-001
used_by: OBS-016, OBS-009, OBS-011, OBS-012
related: OBS-006, OBS-016, OBS-017, OBS-009
tags:
  - observability
  - metrics
  - devops
  - pattern
  - intermediate
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 15
permalink: /obs/prometheus-metrics-collection/
---

# OBS-015 - Prometheus -- Metrics Collection

⚡ TL;DR - Prometheus is a pull-based, time-series
metrics system with a powerful query language (PromQL)
that has become the de facto standard for cloud-native
application metrics. It scrapes /metrics endpoints,
stores data locally, and powers the SLO alerting
that drives SRE practice.

| #015            | Category: Observability & SRE                   | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------- | :-------------- |
| **Depends on:** | Metrics Types, Observability Fundamentals       |                 |
| **Used by:**    | Grafana Dashboards, Alerting, SLI/SLO           |                 |
| **Related:**    | Metrics Types, Grafana, OpenTelemetry, Alerting |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In 2012, SoundCloud needed to monitor 500+ Go and
Java microservices. Their existing monitoring (Graphite,
Nagios) required push-based metric collection: each
application had to know where to send its metrics.
Adding a new service meant updating monitoring
configuration. Checking if a service was alive required
querying a separate system. There was no native way
to alert on "the error rate of the checkout service
is burning through the SLO budget faster than
sustainable."

**THE INVENTION:**
Prometheus (built 2012, open-sourced 2015) inverted
the model. Instead of services pushing metrics to
a central server, Prometheus pulls metrics by scraping
HTTP endpoints that services expose. Any service that
exposes `/metrics` in the Prometheus text format is
automatically discovered and scraped. The pull model
also means Prometheus can detect when a target is
down (scrape fails = target is down).

---

### 📘 Textbook Definition

**Prometheus** is an open-source monitoring system
and time-series database. It:

- **Scrapes** metrics from instrumented services via
  HTTP pull (not push)
- **Stores** data as time-series (metric name + labels
  - timestamp + float64 value)
- **Queries** data using PromQL, a functional query
  language for time-series
- **Alerts** via Alertmanager, which routes and
  deduplicates alerts to PagerDuty, Slack, email
- **Discovers** targets dynamically via service
  discovery (Kubernetes, Consul, AWS EC2)

**Four metric types:**

- **Counter:** monotonically increasing total (requests,
  errors, bytes). Use `rate()` or `increase()`.
- **Gauge:** current snapshot value (memory, queue depth,
  active connections). Use directly.
- **Histogram:** bucketed duration or size distribution.
  Use `histogram_quantile()`.
- **Summary:** pre-computed quantiles client-side.
  Cannot be aggregated across replicas.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Prometheus scrapes /metrics endpoints from your services,
stores the time-series data, and lets you query and
alert on it using PromQL.

> Think of Prometheus as a health inspector who
> visits every restaurant (service) on a schedule,
> reads their posted health metrics, and records
> them in a central logbook. When a restaurant's
> health score drops below threshold, the inspector
> raises an alert. The restaurant does not need to
> know the inspector exists - it just posts its
> metrics on the door. The inspector pulls the data.
> Contrast with push-based monitoring: the restaurant
> would need to mail its health report to the inspector
>
> - which means the inspector never knows if the
>   restaurant stopped sending reports because it closed
>   or because the mail service failed.

**One insight:**
The pull model is the key architectural choice.
Prometheus knows a service is unhealthy not just
when the service sends a "I'm unhealthy" message,
but also when the scrape fails entirely (target down).
Push-based systems cannot distinguish "healthy and
silent" from "crashed and silent."

---

### 🔩 First Principles Explanation

**THE PROMETHEUS DATA MODEL:**

Every metric is identified by:

```
<metric_name>{<label_name>=<label_value>, ...}

Example:
http_requests_total{
  service="checkout",
  method="POST",
  status="200",
  instance="checkout-pod-1:8080"
}
= 14523
```

**The time-series is the combination of metric name +
all labels.** Adding a new label creates a new time-series.
Removing a label loses that dimension of data.

**CARDINALITY - THE KEY CONSTRAINT:**
Cardinality = number of unique time-series in Prometheus.

```
If checkout service has:
  - 10 instances (pods)
  - 5 HTTP methods
  - 8 status codes
  - 100 URL paths

Counter for each combination:
  = 10 x 5 x 8 x 100 = 40,000 time-series
  per single metric

Add customer_id as a label:
  x 1,000,000 users = 40 billion time-series
  → Prometheus OOM and crashes
```

**Lesson:** Never use high-cardinality values as
Prometheus labels (user IDs, request IDs, session
tokens, free-form strings). Prometheus cannot handle
millions of unique time-series efficiently.

**THE PULL MODEL MECHANICS:**

```
[Prometheus server]
  ↓ (every 15s or 60s scrape interval)
[/metrics endpoint: http://checkout-pod:8080/metrics]
  → Reads all metrics in text exposition format
  → Stores each as timestamped time-series

Text exposition format (what /metrics returns):
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="POST",status="200"} 14523
http_requests_total{method="POST",status="500"} 12
http_requests_total{method="GET",status="200"} 89431
```

---

### 🧪 Thought Experiment

**THE RATE() TRAP:**

You have a counter: `checkout_errors_total`. You want
to know if errors are increasing. You run:

```promql
checkout_errors_total
# Returns: 14523 - a total count since process start
# This is useless for alerting - it always goes up
```

You try:

```promql
rate(checkout_errors_total[5m])
# Returns: 0.043 errors/second in the last 5 minutes
# This is the rate of change - what you want
```

**The gotcha:** When the process restarts, the counter
resets to 0. Prometheus `rate()` handles counter resets
automatically - it detects the counter went down and
adjusts the rate calculation. But `increase()` does
not handle the reset correctly across the boundary
in older Prometheus versions. Always use `rate()` for
continuous monitoring of restartable services.

**THE HISTOGRAM TRAP:**

You want to know P99 latency. You have a histogram
metric. You run:

```promql
# WRONG: this aggregates badly
checkout_request_duration_seconds_sum
/ checkout_request_duration_seconds_count

# This gives mean duration, not P99.
# Histogram_quantile is the correct approach:
histogram_quantile(0.99,
  rate(checkout_request_duration_seconds_bucket[5m]))
```

---

### 🧠 Mental Model / Analogy

> Prometheus metrics are like vital signs in a hospital.
> A counter is the cumulative heartbeat count (always
> increasing). A gauge is the current temperature
> (can go up or down). A histogram is the distribution
> of all blood pressure readings over the last hour
> (bucketed). The pull model is like a nurse who
> checks vitals on a schedule, rather than patients
> who call in their own vital signs. Service discovery
> is the hospital's patient roster - when a new patient
> (pod) is admitted (deployed), their vitals are
> automatically added to the monitoring schedule.

The most important lesson: use `rate()` on counters,
use histogram_quantile on histograms, use gauges
directly. Get this wrong and your metrics mean nothing.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone):**
Prometheus is the thing that collects numbers from
your services and lets you graph and alert on them.

**Level 2 - How to use it (junior):**
Expose a /metrics endpoint from your service using
a Prometheus client library. Prometheus scrapes it.
Use PromQL `rate()` for rates, `histogram_quantile()`
for latency percentiles. Use Grafana to visualise.

**Level 3 - How it works (mid-level):**
Pull-based scraping, service discovery via Kubernetes
pod annotations or static configs. Counters must use
`rate()` to get rates. Histograms need `_bucket`,
`_sum`, `_count` suffixes. Labels define cardinality -
never add user IDs as labels. Alertmanager handles
routing, silencing, and deduplication of alerts.

**Level 4 - Operations at scale (senior):**
High-cardinality management: recording rules to
pre-aggregate expensive queries, remote write to
Thanos/Cortex/VictoriaMetrics for long-term retention
and multi-cluster federation. Understand that default
Prometheus retention is 15 days on local disk.
Capacity planning: 1-2 bytes/sample in local TSDB.
10,000 time-series at 15s scrape interval ≈ 100MB/day.

**Level 5 - Platform engineering (staff):**
Thanos (or Cortex) for multi-cluster, multi-tenant
Prometheus at scale. Operator pattern for Kubernetes:
PrometheusRule and ServiceMonitor CRDs for declarative
monitoring configuration. The cardinality budget
per team concept: each team owns X time-series;
exceeding the budget triggers cardinality alerts.
Remote write for centralised retention vs per-cluster
local TSDB: tradeoffs in cost, latency, and SPOF.

---

### ⚙️ How It Works (Mechanism)

**SCRAPE CYCLE:**

```
[Prometheus scheduler]
  Every scrape_interval (default: 1m):
    For each target in scrape_configs:
      HTTP GET <target>/metrics
        ↓ Success: parse text format, store time-series
        ↓ Failure: record scrape_duration_seconds,
                   up{job="...", instance="..."} = 0
        → up{job="checkout"} = 0 fires InstanceDown alert

[Text format response body]
# HELP checkout_requests_total Total requests
# TYPE checkout_requests_total counter
checkout_requests_total{status="200"} 14523 1681234567890
checkout_requests_total{status="500"} 12 1681234567890
#         metric_name        labels        value  timestamp(optional)
```

**STORAGE (TSDB - Time Series DB):**

```
Local disk layout:
/prometheus/
  data/
    01H2X.../       ← 2-hour block
      chunks/       ← compressed time-series data
      index         ← inverted index for labels
      meta.json     ← block metadata
    head/           ← current in-memory block
  wal/              ← write-ahead log

Compaction:
  head block (2h) → persisted to disk block
  multiple 2h blocks → merged into larger blocks
  Default retention: 15 days (configurable: --storage.tsdb.retention.time)
```

**SERVICE DISCOVERY (Kubernetes):**

```yaml
scrape_configs:
  - job_name: kubernetes-pods
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      # Only scrape pods with annotation
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: "true"
      # Use the pod's prometheus port annotation
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        target_label: __address__
```

---

### 🔄 The Complete Picture - End-to-End Flow

**PROMETHEUS IN PRODUCTION:**

```
[Application: checkout-service]
  Exposes: /metrics (Prometheus client library)
  Metrics: http_requests_total, request_duration_bucket
  Annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
        ↓
[Prometheus]
  ServiceMonitor CRD detects new pod
  Scrapes /metrics every 30s
  Stores time-series in local TSDB
        ↓
[Prometheus Alertmanager rule]
  eval: burn rate alert fires
        ↓
[Alertmanager]
  Routes to PagerDuty (page) or Slack (ticket)
  Deduplicates repeated alerts
  Silences during maintenance windows
        ↓
[Grafana]
  Reads from Prometheus via PromQL
  Displays SLO dashboard, golden signals
  On-call engineer opens dashboard, runs queries
        ↓
[Thanos / remote write]
  Long-term storage (90+ days)
  Multi-cluster aggregation
  Global query across all clusters
```

---

### 💻 Code Example

**Example 1 - BAD: Counter used directly without rate():**

```promql
# BAD: raw counter value - always increasing,
# useless for detecting if error rate increased
checkout_errors_total
# Returns: 14523 (total since service started)
# Cannot distinguish: is it 1 error/hour or 100/second?
```

**Example 2 - GOOD: Rate over a time window:**

```promql
# GOOD: rate of errors per second over 5-minute window
rate(checkout_errors_total[5m])
# Returns: 0.043 errors/second (meaningful, alertable)

# GOOD: fraction of requests that are errors (SLI)
sum(rate(checkout_errors_total{status=~"5.."}[5m]))
/ sum(rate(checkout_requests_total[5m]))
# Returns: 0.003 (0.3% error rate)
```

**Example 3 - Application instrumentation (Go):**

```go
package main

import (
    "net/http"
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
    // Counter: use rate() in PromQL
    requestsTotal = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "checkout_requests_total",
            Help: "Total checkout requests",
        },
        []string{"status"},
    )

    // Histogram: use histogram_quantile() in PromQL
    requestDuration = promauto.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "checkout_request_duration_seconds",
            Help:    "Checkout request latency",
            Buckets: []float64{
                0.005, 0.01, 0.025, 0.05, 0.1,
                0.25, 0.5, 1, 2.5, 5, 10,
            },
        },
        []string{"method"},
    )
)

func handleCheckout(w http.ResponseWriter, r *http.Request) {
    timer := prometheus.NewTimer(
        requestDuration.WithLabelValues(r.Method))
    defer timer.ObserveDuration()

    err := processCheckout(r)
    if err != nil {
        requestsTotal.WithLabelValues("500").Inc()
        http.Error(w, "checkout failed", 500)
        return
    }
    requestsTotal.WithLabelValues("200").Inc()
    w.WriteHeader(200)
}

func main() {
    http.Handle("/metrics", promhttp.Handler())
    http.HandleFunc("/checkout", handleCheckout)
    http.ListenAndServe(":8080", nil)
}
```

**Example 4 - Failure: High cardinality label:**

```go
// BAD: user_id as a label = millions of time-series
// Prometheus will OOM and restart
requestsTotal = promauto.NewCounterVec(
    prometheus.CounterOpts{
        Name: "checkout_requests_total",
    },
    []string{"status", "user_id"},  // user_id = cardinality bomb
)
requestsTotal.WithLabelValues("200", userID).Inc()
// 1M users = 2M x statuses = 2M time-series per counter

// GOOD: use attributes that have bounded cardinality
requestsTotal = promauto.NewCounterVec(
    prometheus.CounterOpts{
        Name: "checkout_requests_total",
    },
    []string{"status", "payment_method"},
    // payment_method: visa, mastercard, paypal, crypto = 4 values
    // status: 200, 400, 500 = 3 values
    // Total: 12 time-series per instance
)
```

---

### ⚖️ Comparison Table

| Aspect                | Prometheus (pull)             | Graphite/StatsD (push)       | Datadog (agent push)            |
| --------------------- | ----------------------------- | ---------------------------- | ------------------------------- |
| Collection model      | Prometheus scrapes /metrics   | Apps push to carbon relay    | Datadog agent pushes to cloud   |
| Target down detection | Scrape fails = up=0, alert    | Must use heartbeat metric    | Agent health check              |
| Cardinality limit     | ~10M time-series per instance | Less flexible                | Managed by cloud                |
| Query language        | PromQL (functional, powerful) | Graphite functions (limited) | MetricsQL / DQL                 |
| Long-term storage     | External (Thanos, Cortex)     | Built-in (whisper files)     | Cloud (managed)                 |
| Cost model            | Open source + infra cost      | Open source                  | SaaS per-host pricing           |
| Best for              | Kubernetes-native, SLO-based  | Legacy app metrics           | Managed SaaS, less ops overhead |

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                                                                           |
| ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Use `increase()` for counter rates"              | Use `rate()` for real-time alerting. `increase()` is for human-readable totals in dashboards. `rate()` handles counter resets; `increase()` may show negative spikes on pod restart in some Prometheus versions.  |
| "More labels = more information"                  | More labels = more cardinality. Every unique label value combination creates a new time-series. High-cardinality labels (user ID, request ID) will OOM Prometheus.                                                |
| "Summary and Histogram are equivalent"            | Histograms can be aggregated across replicas using `histogram_quantile()`. Summaries calculate quantiles client-side and cannot be meaningfully aggregated. For multi-instance deployments, always use Histogram. |
| "Prometheus can store long-term history"          | Default local TSDB retention is 15 days. For long-term (90+ days) storage and multi-cluster querying, you need Thanos, Cortex, or VictoriaMetrics with remote write.                                              |
| "Prometheus pull model requires firewall changes" | In Kubernetes, Prometheus runs inside the cluster and scrapes pods over the cluster network. No firewall changes needed for internal services. External services require pushgateway.                             |

---

### 🚨 Failure Modes & Diagnosis

**Prometheus OOM crash due to cardinality explosion**

**Symptom:**
Prometheus pod crashes with OOMKilled. This happens
within 24 hours of a new application deployment.
Metrics stop flowing. All SLO-based alerts go silent.
Grafana shows "No data" for all panels.

**Root Cause:**
A developer added a high-cardinality label to a
high-volume counter. The new label has 100,000 unique
values (request IDs, session tokens, or URL paths
including query parameters). This creates 100,000x
more time-series than before.

**Diagnostic Command:**

```promql
# Find the highest-cardinality metrics
topk(10,
  count by (__name__)(
    {__name__=~".+"}
  )
)

# Find metrics with many label combinations
count by (job, __name__)(
  {__name__=~"checkout.*"}
)
```

Also check:

```bash
# Prometheus API: cardinality statistics
curl http://prometheus:9090/api/v1/status/tsdb \
  | jq '.data.headStats'
# Check: numSeries, numChunks
```

**Fix:**
Remove or hash the high-cardinality label from the
metric definition. Redeploy the application. Prometheus
will recover as old time-series expire. Consider
adding a cardinality alert as a preventive measure:

```yaml
- alert: HighCardinalityMetric
  expr: |
    count({__name__=~".+"}) > 500000
  labels:
    severity: warning
  annotations:
    summary: "Prometheus cardinality approaching limit"
```

---

**Rate() returning no data after service restart**

**Symptom:**
After a service deployment, the error rate dashboard
shows 0 or no data for 5-10 minutes. On-call engineers
cannot tell if the new deployment is healthy.

**Root Cause:**
`rate()` requires at least 2 scrape intervals of data
to calculate a rate. After a pod restart, Prometheus
needs 2 scrapes (minimum 30-120 seconds depending on
scrape interval) before `rate()` returns data. With
`[5m]` lookback and a 1-minute scrape interval,
rate() needs 5 minutes of data to be statistically
meaningful.

**Fix:**
For startup health checks, use `up` metric (instantly
available after first scrape) or a shorter rate window
`[1m]` for faster feedback in dashboards:

```promql
# Deployment health: is the new pod being scraped?
up{job="checkout"} == 1

# Use shorter window for post-deployment monitoring
rate(checkout_requests_total[2m])
# vs typical monitoring window of [5m]
```

**Prevention:**
Separate your deployment monitoring queries (2m window)
from your alerting queries (5m window). Alerting should
have some stability window to avoid false alerts during
pod restarts.

---

**Histogram P99 query returning inaccurate results**

**Symptom:**
P99 latency query returns 150ms for the checkout
service. Manual inspection of response times shows
some requests are clearly taking 2+ seconds. The P99
appears to be significantly underreporting.

**Root Cause:**
The histogram bucket configuration has no bucket at
500ms, 1s, or 2s. The buckets stop at 100ms. When
all long requests fall into the last bucket (le="+Inf"),
`histogram_quantile()` cannot interpolate accurately
beyond the largest explicit bucket.

**Diagnostic:**

```promql
# Check histogram bucket boundaries
checkout_request_duration_seconds_bucket
# Look at le label values - are they fine enough?

# If last explicit bucket is 0.1:
# All requests > 0.1s are in le="+Inf"
# histogram_quantile returns at most 0.1 for P99
# even if 10% of requests take 5 seconds
```

**Fix:**
Extend the histogram buckets to cover the observed
range:

```go
Buckets: []float64{
    0.005, 0.01, 0.025, 0.05, 0.1,
    0.25, 0.5, 1, 2.5, 5, 10,
},
// Now histogram_quantile can accurately estimate
// P99 up to the 10s bucket boundary
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Metrics Types (Counter, Gauge, Histogram)` - the
  four Prometheus metric types and when to use each
- `Observability Fundamentals` - the three-pillar
  context in which Prometheus provides the metrics pillar

**Builds On This (learn these next):**

- `Grafana Dashboards` - Prometheus is the data source;
  Grafana provides the visualisation layer
- `Alerting Fundamentals` - Alertmanager receives
  firing alerts from Prometheus evaluation rules
- `SLI Service Level Indicator` - SLIs are implemented
  as PromQL expressions over Prometheus counters and
  histograms
- `OpenTelemetry` - OTel can export metrics to
  Prometheus via OTLP or Prometheus exporter format

**Alternatives / Comparisons:**

- `Datadog` - managed SaaS alternative; same concepts,
  less operational overhead, higher per-host cost
- `VictoriaMetrics` - Prometheus-compatible, more
  memory-efficient, better long-term storage
- `InfluxDB` - push-based TSDB, different data model,
  less common in Kubernetes-native stacks

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ COLLECTION   │ Pull-based: Prometheus scrapes /metrics   │
│ MODEL        │ every scrape_interval (default: 1m)       │
├──────────────┼───────────────────────────────────────────┤
│ METRIC TYPES │ Counter → rate() / increase()             │
│              │ Gauge → use directly                      │
│              │ Histogram → histogram_quantile()          │
│              │ Summary → avoid for multi-instance        │
├──────────────┼───────────────────────────────────────────┤
│ KEY QUERIES  │ Error rate: rate(errors_total[5m])        │
│              │        / rate(requests_total[5m])         │
│              │ P99: histogram_quantile(0.99,             │
│              │        rate(duration_bucket[5m]))         │
│              │ Is up: up{job="checkout"} == 1            │
├──────────────┼───────────────────────────────────────────┤
│ CARDINALITY  │ Never: user_id, request_id as label       │
│ RULES        │ OK: status_code, method, region          │
│              │ Limit: ~10M series per Prometheus         │
├──────────────┼───────────────────────────────────────────┤
│ RETENTION    │ Default: 15 days local TSDB               │
│              │ Long-term: Thanos / Cortex remote write   │
├──────────────┼───────────────────────────────────────────┤
│ TARGET DOWN  │ up{job="svc"} = 0 when scrape fails      │
│ DETECTION    │ → "InstanceDown" alert fires              │
├──────────────┼───────────────────────────────────────────┤
│ COMMON BUGS  │ Using raw counter (not rate())            │
│              │ Summary instead of Histogram              │
│              │ Cardinality explosion via bad labels      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Grafana → Alertmanager → Thanos → OTel   │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
The cardinality constraint in Prometheus is an instance
of a general systems principle: every abstraction has
a cost model that must be understood before use.
Labels in Prometheus, indexes in databases, event
listeners in UI frameworks - each provides power
at a cost. Adding an index to every column in a
database makes queries fast but writes slow and
storage large. Adding a Prometheus label for every
request attribute makes metrics "complete" but
crashes the monitoring system. Understanding the
cost model before reaching for the feature is what
distinguishes senior engineers from junior.

---

### 💡 The Surprising Truth

The most counterintuitive Prometheus behaviour:
the pull model means Prometheus is the source of
truth for whether a target is alive. When a pod
crashes, Prometheus does not receive a "I'm dying"
notification - it simply fails to scrape the target
and records `up = 0`. This means Prometheus can
detect a crashed pod that has no health check endpoint,
no heartbeat metric, and no push-based notification.
The absence of a response is itself the signal.
Push-based systems cannot distinguish "healthy and
quiet" from "dead and quiet." This is why the Prometheus
ecosystem has grown to dominate Kubernetes monitoring -
in dynamic environments where pods start and die
constantly, pull-based discovery with dead detection
is superior to push-based reporting.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[EXPLAIN]** Explain why `histogram_quantile()` on
   a Histogram is preferred over a Summary for P99
   latency in a multi-replica deployment, including
   what specifically goes wrong if you use Summary.
2. **[DEBUG]** Given a Prometheus OOM crash, identify
   the high-cardinality metric causing it using the
   `tsdb` API and `topk` cardinality queries, then
   propose a fix to the metric definition.
3. **[CODE]** Write a Go service instrumented with
   Prometheus: a counter for request total by status,
   a histogram for request duration with appropriate
   buckets, and expose /metrics. Use `promauto` for
   auto-registration.
4. **[QUERY]** Write the PromQL for: (a) 5-minute error
   rate as a fraction, (b) P99 latency from a histogram,
   (c) requests per second by status code, (d) whether
   all instances of the checkout service are up.
5. **[DESIGN]** Design a Prometheus deployment for a
   100-service Kubernetes cluster that needs 90-day
   metric retention and multi-cluster querying.
   Explain the role of Thanos sidecar, object storage,
   and the querier component.

---

### 🧠 Think About This Before We Continue

**Q1.** Your checkout service runs 20 pods. Each pod
exports a `checkout_request_duration_seconds` histogram.
You want P99 latency across all pods. You run:
`histogram_quantile(0.99, checkout_request_duration_seconds_bucket)`
The result appears incorrect - it shows a lower P99
than individual pod traces suggest. What is wrong?
How do you fix the query?
_Hint: You must aggregate the bucket counts across
all pods before passing to histogram_quantile. Use:
`histogram_quantile(0.99, sum by (le)(rate(checkout_request_duration_seconds_bucket[5m])))`
Without the `sum by (le)`, histogram_quantile attempts
to estimate quantiles on per-pod buckets, which may
not be correct when load is uneven across pods._

**Q2.** A developer wants to track which specific
customer IDs are causing the most checkout errors.
They propose adding `customer_id` as a Prometheus
label to `checkout_errors_total`. You have 2 million
customers. Explain specifically what will happen to
Prometheus if this label is added, and propose an
alternative approach to answer the underlying
business question.
_Hint: 2M customer IDs x status codes x methods =
potentially 10M+ new time-series. Prometheus will
exceed memory limits and crash. The underlying question
("which customers are getting errors?") is better
answered by: (1) a counter bucketed by customer_tier
(gold/silver/free - 3 values), (2) distributed traces
with customer_id as a trace attribute (not a metric
label), (3) log analysis with customer_id in the
structured log fields filtered via Kibana._

**Q3 (TYPE G):** You are building the observability
platform for a company migrating from monolith to
100 microservices over 18 months. Today you have one
Prometheus instance with 50,000 time-series. In 18
months you expect 5M time-series. Design the evolution
of the metrics infrastructure: what you deploy today,
what you add at 500K series, what you add at 5M series.
Address: storage (retention, capacity), multi-cluster
aggregation, cardinality governance (how do you
prevent teams from adding cardinality bombs?),
and query performance at scale.
_Hint: Today: single Prometheus, 15-day retention,
local TSDB. At 500K: add Thanos sidecar + object
storage for 90-day retention, remain single Prometheus.
At 5M: Prometheus operator with per-team Prometheus
instances, Thanos Querier for global view, recording
rules to pre-aggregate expensive global queries,
cardinality budget per team enforced via Prometheus
alerts on series count per job label._

---

### 🎯 Interview Deep-Dive

**Q1: "Explain the Prometheus data model. What is
a time-series?"**
_Why they ask:_ Tests whether the candidate understands
Prometheus fundamentally vs superficially.
_Strong answer includes:_

- A time-series is a unique combination of metric
  name and all label key-value pairs
- Stored as a sequence of (timestamp, float64) samples
- Identified by the combination: `metric_name{label1=v1, label2=v2}`
- Adding a label creates a new time-series - this
  is the cardinality model
- Metric types (counter, gauge, histogram, summary)
  are conventions on top of this model

**Q2: "When would you use histogram_quantile and
when would you use a Summary?"**
_Why they ask:_ Tests deep understanding of the most
commonly misused Prometheus feature.
_Strong answer includes:_

- Histogram: pre-defined buckets on the server side.
  Quantiles calculated at query time using PromQL.
  Can be aggregated across replicas with `sum by (le)`.
  Must have appropriate bucket boundaries.
- Summary: quantiles calculated client-side. Cannot
  be aggregated. Use only for single-instance metrics
  where aggregation across replicas is not needed.
- Rule of thumb: in Kubernetes (multi-replica) always
  use Histogram. Summary is useful for batch jobs or
  metrics where you know the distribution in advance.

**Q3: "Your Prometheus is using 40GB of memory and
growing. How do you diagnose and fix it?"**
_Why they ask:_ Tests production troubleshooting of
the most common Prometheus scaling problem.
_Strong answer includes:_

- Step 1: check cardinality via `tsdb` API endpoint
  `/api/v1/status/tsdb` - look at `headStats.numSeries`
- Step 2: find highest cardinality metrics with PromQL:
  `topk(10, count by (__name__)({__name__=~".+"}))`
- Step 3: examine the labels of the top metrics -
  is there a user_id, request_id, or URL path label?
- Step 4: work with the owning team to fix the metric
  definition (remove the high-cardinality label, or
  replace with a bounded categorical label)
- Step 5: reduce retention to free memory while the
  fix is deployed (`--storage.tsdb.retention.time=7d`)
- Long-term: implement cardinality budgets per team
  enforced by a recording rule alert

> Entry stub. Generate full content using Master Prompt v3.0.
