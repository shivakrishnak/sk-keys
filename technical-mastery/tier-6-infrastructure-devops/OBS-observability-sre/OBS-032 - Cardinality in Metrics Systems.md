---
id: OBS-032
title: Cardinality in Metrics Systems
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★★
depends_on: OBS-006, OBS-015, OBS-001
used_by: OBS-039, OBS-044, OBS-045
related: OBS-006, OBS-015, OBS-019, OBS-039
tags:
  - observability
  - metrics
  - prometheus
  - production
  - advanced
  - tradeoff
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Mastery"
nav_order: 32
permalink: /technical-mastery/obs/cardinality-in-metrics-systems/
---

⚡ TL;DR - Cardinality is the number of unique label
value combinations for a metric. High cardinality
(user IDs, request IDs, URLs as labels) causes
Prometheus to create millions of time series per
metric, exhausting memory and crashing the metrics
system. It is the single most common cause of
production Prometheus outages.

| #032            | Category: Observability & SRE                                    | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------- | :-------------- |
| **Depends on:** | Metrics -- Types, Prometheus -- Metrics Collection               |                 |
| **Used by:**    | Observability at Scale, Platform Observability                   |                 |
| **Related:**    | Metrics Types, Prometheus, ELK/EFK Stack, Observability at Scale |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A developer adds user analytics to a payment service.
They instrument a counter with a `user_id` label:

```python
payment_count = Counter(
  "payments_total",
  "Total payments",
  ["user_id", "currency", "status"]
)
```

The service has 10 million users, 5 currencies, and
3 status values. Cardinality: 10M x 5 x 3 = 150
million time series. Each series uses ~500 bytes.
Total: 75 GB of RAM consumed by this one metric.
Prometheus crashes with OOM. All metrics are lost.
All dashboards are blank. All alerts stop firing.
The engineering team spent 3 hours debugging an outage
caused by one metric label.

**THE INVENTION:**
Understanding cardinality - the number of unique
label value combinations - as the fundamental
constraint of time-series metric systems. Every
high-cardinality label exponentially multiplies the
memory cost. The cardinality management framework:
audit, enforce limits, use bounded labels, and move
high-cardinality data to log systems (where it
belongs).

---

### 📘 Textbook Definition

**Cardinality** in metrics: the number of unique
time series a metric name creates, determined by
the product of the number of unique values for each
label:

```
cardinality = |label_1_values| x |label_2_values|
              x ... x |label_N_values|

Example:
  http_requests_total{
    method,    # GET, POST, PUT, DELETE = 4 values
    status,    # 200, 201, 400, 401, 403, 404, 500 = 7
    service    # checkout, payment, inventory = 3
  }
  Cardinality = 4 x 7 x 3 = 84 time series
  (Low cardinality - safe)

  http_requests_total{
    method,    # 4 values
    user_id,   # 10,000,000 values
    status     # 7 values
  }
  Cardinality = 4 x 10M x 7 = 280,000,000 time series
  (Catastrophic cardinality - will OOM Prometheus)
```

**Time series memory cost:**

- Prometheus: ~500-1,000 bytes per active time series
  (WAL entry + chunk header + label storage)
- 1 million series = ~500 MB - 1 GB RAM (manageable)
- 10 million series = ~5-10 GB RAM (needs large instance)
- 100 million series = ~50-100 GB RAM (approaching limits)
- 1 billion series = ~500 GB RAM (impractical)

**Bounded vs unbounded cardinality:**

- Bounded: finite set of known values (HTTP methods:
  GET/POST/PUT/DELETE/PATCH - at most 5)
- Unbounded: grows with traffic (user_id, request_id,
  URL path with path variables, IP addresses)
- Rule: only bounded labels are safe for metrics.
  Unbounded labels belong in logs or traces.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Every unique combination of label values creates a
separate time series in Prometheus - one label with
a million unique values creates a million time series
for that metric, consuming gigabytes of RAM.

> A library has a card catalogue with one card per
> book (the time series). Adding a "reader ID" column
> to every card creates one card per book per reader
> who has ever borrowed it. If 100,000 readers have
> borrowed 50,000 books: the catalogue grows to
> 5 billion cards. The library cannot store them all.
>
> In Prometheus: labels are the columns. Each
> unique column value combination = one card (time series).
> Using user_id (100,000 users) as a label on a metric
> with 50,000 endpoints = 5 billion time series.
> The library burns down (Prometheus OOM).

---

### 🔩 First Principles Explanation

**HOW PROMETHEUS STORES TIME SERIES:**

```
Each unique label set creates a time series:
  http_requests_total{method="GET", status="200"}  →
    series 1
  http_requests_total{method="GET", status="500"}  →
    series 2
  http_requests_total{method="POST", status="200"} →
    series 3
  http_requests_total{method="POST", status="500"} →
    series 4
  ... 84 series total for bounded labels above

In memory (WAL + head chunks):
  Series 1: [last 2h of samples] + metadata
  Series 2: [last 2h of samples] + metadata
  ... x 84 series = trivial

Now with user_id label:
  http_requests_total{user_id="user-1", ...}     → series 1
  http_requests_total{user_id="user-2", ...}     → series 2
  ...
  http_requests_total{user_id="user-10000000",...}→ series
    10M
  Total: 280M series, 140-280 GB RAM → OOM crash
```

**THE CARDINALITY EXPLOSION PATTERNS:**

```
Pattern 1: Unbounded label value
  SYMPTOM: metric series count growing with traffic
  CAUSE: label values that grow with user count,
         request count, or data volume
  EXAMPLES:
    user_id, session_id, request_id   → unbounded
    URL path with variables            → unbounded
      (/api/users/123 vs /api/users/456)
    IP addresses                       → large bounded
    Kubernetes pod names with hash     → grows with deploys

Pattern 2: Label multiplication
  SYMPTOM: sudden 10x series count
  CAUSE: adding a new label to an existing high-series
    metric
  EXAMPLE: adding service_version (10 versions) to a
    metric already having 10,000 series creates 100,000

Pattern 3: Missing label value validation
  SYMPTOM: metric with unexpected label values
  CAUSE: label values include raw user input, error
    messages,
         or uncontrolled strings
  EXAMPLE: error_type label containing full exception
           messages (thousands of unique strings)
```

**THE SAFE LABEL TAXONOMY:**

```
ALWAYS SAFE (bounded, small set):
  http_method         # GET, POST, PUT, DELETE, PATCH
  http_status_code    # 200, 201, 400, 401, 403, 500
  http_status_class   # 2xx, 3xx, 4xx, 5xx (better)
  service_name        # checkout, payment (known, finite)
  environment         # prod, staging, dev
  region              # us-east-1, eu-west-1 (5-10 values)
  database_operation  # read, write, delete

USUALLY SAFE (bounded, moderate set):
  http_endpoint       # /checkout, /payment, /health
                      # BUT: /api/users/{id} → NOT safe
  error_type          # TIMEOUT, CONNECTION_REFUSED
                      # BUT: not full exception messages
  pod_name            # CAUTION: grows with deployments

NEVER SAFE (unbounded):
  user_id, customer_id, session_id, request_id
  url (full URL with query params)
  IP address (unless small bounded set)
  timestamp, date, time
  full exception message or stack trace
  Any value proportional to traffic volume
```

---

### 🧪 Thought Experiment

**THE CARDINALITY AUDIT SCENARIO:**

A Prometheus instance is consuming 64 GB RAM (expected:
8 GB). The team runs a cardinality audit.

```bash
# Check current series count
curl -s http://localhost:9090/api/v1/query \
  --data-urlencode 'query=prometheus_tsdb_head_series' \
  | jq '.data.result[0].value[1]'
# Output: 85,000,000 (85 million active series!)
# Expected: ~500,000

# Find which metrics have the most series
curl -s http://localhost:9090/api/v1/label/__name__/values \
  | jq '.data[]' \
  | while read metric; do
      count=$(curl -s "http://localhost:9090/api/v1/query" \
        --data-urlencode "query=count({__name__=\"$metric\"})" \
        | jq '.data.result[0].value[1]')
      echo "$count $metric"
    done | sort -rn | head -20
```

**Output:**

```
45,000,000  payment_processing_duration_seconds (user_id
  label!)
30,000,000  recommendation_clicks_total (user_id + item_id)
 5,000,000  http_requests_total (url path label)
   200,000  checkout_requests_total (safe labels)
    50,000  jvm_gc_pause_seconds (normal)
```

**Finding:** Two metrics with `user_id` labels account
for 75 million of the 85 million series. Three options:

1. **Remove user_id label** (breaks the per-user analytics)
2. **Move user-level data to logging** (correct approach)
3. **Use aggregation**: record per-user metrics in
   application memory and emit only aggregated buckets
   (e.g., payment_duration_p99_bucket by `user_tier`
   instead of `user_id`)

---

### 🧠 Mental Model / Analogy

> Cardinality is the postal system's address problem.
> A post office handles mail for a city. It has
> filing cabinets organised by: country (3 values),
> state (50), city (100), street (1,000). Total
> combinations: 3 x 50 x 100 x 1,000 = 15 million
> possible addresses. Manageable with large cabinets.
>
> Now add "apartment number" to the label: potentially
> 10,000 unique values per building. Now: 3 x 50 x
> 100 x 1,000 x 10,000 = 150 billion combinations.
> The post office needs a warehouse larger than the
> city to store the filing cabinets for all possible
> combinations.
>
> In Prometheus: adding one unbounded label to a metric
> multiplies the storage requirement by the number of
> unique values. The filing cabinets are RAM. When RAM
> runs out: OOM crash.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone):**
In Prometheus, every different combination of label
values is stored separately. If you use a user ID
as a label and have a million users, Prometheus stores
a million separate counters for that metric. This
uses too much memory and crashes the system. Use
labels with only a few known possible values.

**Level 2 - The rule (junior):**
Rule: a label is safe only if you can enumerate all
its possible values ahead of time and there are fewer
than ~1,000 unique values. HTTP method: safe (5 values).
HTTP status: safe (10-20 values). User ID: never safe
(unbounded). URL path with path variables: never safe.
When in doubt: count the possible values. If it
can grow with traffic, it is not a metric label.

**Level 3 - Diagnosis and audit (mid-level):**
Detect cardinality issues: monitor
`prometheus_tsdb_head_series`. Alert if > 2 million
(warning), > 5 million (critical). Find the offending
metric: use TSDB status API to list metrics by series
count. Fix: remove the high-cardinality label, move
that dimension to logs or traces. Add a cardinality
lint step in CI: check metrics definitions against
a known-safe label set before deployment.

**Level 4 - Architecture (senior):**
Design cardinality budgets: total Prometheus capacity
= available RAM / 1 KB per series. With 16 GB RAM
for Prometheus: budget = 16 million series. Divide
by expected number of metrics: 50 metrics = 320,000
series per metric average. This bounds the maximum
cardinality per metric. Enforce via a metrics registry
that validates label cardinality at registration time.
Recording rules to pre-aggregate high-cardinality
data: aggregate `payment_duration` from per-pod to
per-service before storing in TSDB.

**Level 5 - Platform (staff):**
Platform-wide cardinality governance: every new metric
requires a cardinality review before production
deployment. The metric registry API (Prometheus
remote write to Cortex/Mimir) enforces per-tenant
series limits. Cardinality observability: a second-
level Prometheus that monitors the first-level
Prometheus's series count, scrape duration, and WAL
checkpoint time. Automatic cardinality enforcement:
a Prometheus recording rule pipeline that demotes
metrics exceeding their budget to low-cardinality
aggregates automatically. Vendor comparison: Datadog
charges per metric per host per time interval -
high cardinality = very high cost. OpenTelemetry
Collector's cardinality reduction processor trims
high-cardinality attributes before export.

---

### ⚙️ How It Works (Mechanism)

**PROMETHEUS TSDB CARDINALITY MONITORING:**

```bash
# Real-time series count
curl -s "http://localhost:9090/api/v1/query" \
  --data-urlencode \
  "query=prometheus_tsdb_head_series" | \
  jq '.data.result[0].value[1]'

# TSDB status: top metrics by series count
# Available at Prometheus UI: /tsdb-status
# Or via API:
curl -s "http://localhost:9090/api/v1/status/tsdb" | \
  jq '.data.seriesCountByMetricName[:10]'
# Returns: [{name: "payment_duration_seconds",
#             value: 45000000}, ...]

# Top labels contributing to cardinality:
curl -s "http://localhost:9090/api/v1/status/tsdb" | \
  jq '.data.seriesCountByLabelValuePair[:10]'
# Returns: [{name: "user_id=user-123456",
#             value: 1200}, ...]
# If user_id is the top label: cardinality problem confirmed
```

**CARDINALITY LINT IN CI/CD:**

```python
# metrics_lint.py
# Validates metric definitions against cardinality rules
# Run in CI before deployment

import re
import sys

# Known bounded labels (safe)
SAFE_LABELS = {
    "http_method", "http_status", "http_status_class",
    "service", "environment", "region", "database_op",
    "error_type", "queue_name", "cache_hit"
}

# High-cardinality labels (forbidden in metrics)
FORBIDDEN_LABELS = {
    "user_id", "customer_id", "session_id",
    "request_id", "trace_id", "span_id",
    "url", "path", "ip", "ip_address",
    "email", "username"
}

def check_metric_labels(metric_name: str,
                        labels: list[str]) -> list[str]:
    violations = []
    for label in labels:
        if label in FORBIDDEN_LABELS:
            violations.append(
                f"FORBIDDEN label '{label}' in "
                f"metric '{metric_name}'. "
                f"Use logs/traces for per-{label} data."
            )
        elif label not in SAFE_LABELS:
            violations.append(
                f"UNKNOWN label '{label}' in "
                f"metric '{metric_name}'. "
                f"Add to SAFE_LABELS after cardinality review."
            )
    return violations

# Parse metrics definitions from source code
# (simplified - real implementation scans code)
metrics_to_check = [
    ("payments_total", ["currency", "status"]),        # OK
    ("user_payments_total", ["user_id", "currency"]),  # FAIL
    ("request_duration_seconds",
     ["method", "status", "endpoint"]),                # OK
    ("page_views_total", ["user_id", "page_url"]),     # FAIL
]

errors = []
for metric_name, labels in metrics_to_check:
    errors.extend(check_metric_labels(metric_name, labels))

if errors:
    print("CARDINALITY LINT FAILURES:")
    for error in errors:
        print(f"  ERROR: {error}")
    sys.exit(1)

print("Cardinality lint passed.")
```

**RECORDING RULES TO REDUCE CARDINALITY:**

```yaml
# Transform high-cardinality metric to low-cardinality
# before long-term storage

groups:
  - name: cardinality-reduction
    rules:
      # BAD source metric (has pod_name label - grows with deploys)
      # checkout_requests_total{pod_name, method, status}
      # = pod_count x 4 methods x 7 statuses = potentially 10,000+

      # GOOD recording rule: aggregate across pods
      - record: checkout:requests:rate5m
        expr: |
          sum by (method, status) (
            rate(checkout_requests_total[5m])
          )
        # Result: only 4 x 7 = 28 series
        # Pod-level data preserved in original metric (short
        # retention)
        # Aggregated data used for long-term trending

      # For per-service dashboard (acceptable cardinality):
      - record: checkout:requests_by_status:rate5m
        expr: |
          sum by (status_class) (
            label_replace(
              rate(checkout_requests_total[5m]),
              "status_class",
              "${1}xx",
              "status",
              "([0-9]).*"
            )
          )
        # Collapses 200,201,204 → 2xx; 400,401,404 → 4xx
        # 4 status classes instead of 7+ status codes
```

---

### 🔄 The Complete Picture - End-to-End Flow

**CARDINALITY INCIDENT LIFECYCLE:**

```
[Developer adds user_id label to metric]
  ↓
[Cardinality lint in CI]
  lint.py detects "user_id" in FORBIDDEN_LABELS
  Build fails with error:
    "FORBIDDEN label 'user_id' in 'payment_total'.
    Use logs/traces for per-user_id data."
  Developer must redesign metric.
  → INCIDENT PREVENTED

[If lint is absent - incident path]
  ↓
[Metric deployed to production]
  Prometheus scrapes the metric
  New time series created: 1 per user per scrape
  10,000 users → 10,000 new series per metric per scrape
  ↓
[5 minutes after deploy]
  prometheus_tsdb_head_series: 500,000 → 2,500,000
  Prometheus memory: 4 GB → 20 GB (approaching limit)
  Prometheus alert: "High cardinality warning"
  ↓
[15 minutes after deploy]
  prometheus_tsdb_head_series: 25,000,000
  Prometheus OOM killed by OS (or Kubernetes)
  Prometheus restarts. WAL replay: 3 minutes dark.
  All dashboards: blank (no metrics)
  All SLO burn rate alerts: not firing
  ↓
[Incident: 18 minutes]
  On-call notified: "Prometheus is down"
  Discovery: user_id label in new metric
  Fix: remove user_id label from metric definition
  Rollback: revert deployment, drain high-cardinality
    metrics
  Resolution: Prometheus restarts with low-cardinality
    metrics
  ↓
[Post-mortem]
  Root cause: unbounded label (user_id) in metric
    definition
  Action items:
    1. Add cardinality lint to CI (HIGHEST PRIORITY)
    2. Add prometheus_tsdb_head_series alert
    3. Add label cardinality review to metric PR checklist
    4. Add per-metric series limit enforcement
      (Cortex/Thanos)
```

---

### 💻 Code Example

**Example 1 - BAD: Unbounded labels:**

```java
// BAD: user_id as a label - 10M series per metric
Counter payments = Counter
  .builder("payments_total")
  .tags("user_id", userId,        // FORBIDDEN: unbounded
        "currency", currency,     // OK: bounded (5 values)
        "status", status)         // OK: bounded (3 values)
  .register(registry);

// Memory: 10M users x 5 currencies x 3 statuses x 500B
// = 75 GB RAM from this one metric

// BAD: full URL as label
Timer requestDuration = Timer
  .builder("http_request_duration")
  .tags("url", request.getRequestURI())
  // /api/users/123?filter=active → unique per user
  // /api/orders/abc-123 → unique per order
  // FORBIDDEN: grows with traffic
  .register(registry);
```

**Example 2 - GOOD: Bounded labels only:**

```java
// GOOD: remove user_id; use bounded labels only
Counter payments = Counter
  .builder("payments_total")
  .tags("currency", currency,       // OK: 5 values max
        "status", status,           // OK: success/failure/pending
        "payment_method", method)   // OK: card/bank/wallet
  .register(registry);
// Cardinality: 5 x 3 x 3 = 45 series. Trivial.

// Per-user data → use logs, not metrics
log.info("payment_completed",
  "user_id", userId,        // Goes to Elasticsearch/Loki
  "currency", currency,
  "amount", amount,
  "status", status,
  "trace_id", traceId);     // Correlate with trace

// GOOD: normalise URL paths
Timer requestDuration = Timer
  .builder("http_request_duration")
  .tags(
    "method", request.getMethod(),
    "endpoint", normalizeEndpoint(request.getRequestURI()),
    // /api/users/{id} → "/api/users/{id}" (normalised)
    "status_class", statusClass(response.getStatus()))
  .register(registry);

private String normalizeEndpoint(String uri) {
  // Replace path variables with placeholders
  return uri
    .replaceAll("/[0-9a-f]{8}-[0-9a-f-]{27}", "/{uuid}")
    .replaceAll("/[0-9]+", "/{id}");
  // /api/users/12345 → /api/users/{id}
  // /api/orders/abc-def → /api/orders/{uuid}
}
```

**Example 3 - Prometheus cardinality alert:**

```yaml
groups:
  - name: prometheus-cardinality
    rules:
      # Alert when total series count exceeds safe threshold
      - alert: HighMetricsCardinality
        expr: prometheus_tsdb_head_series > 2000000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Prometheus has {{ $value | humanize }} active series"
          description: |
            Expected: < 500,000 active series.
            Current: {{ $value | humanize }} series.
            Run the TSDB status check to find the offending metric:
            curl http://prometheus:9090/api/v1/status/tsdb | \
              jq '.data.seriesCountByMetricName[:5]'
            Action: identify and remove high-cardinality labels.

      - alert: CriticalMetricsCardinality
        expr: prometheus_tsdb_head_series > 10000000
        for: 2m
        labels:
          severity: page
        annotations:
          summary: "Prometheus cardinality CRITICAL: OOM risk"
          description: |
            {{ $value | humanize }} active series.
            Prometheus OOM risk. Immediate action required.
            Emergency: restart Prometheus with TSDB limit flag
            --storage.tsdb.max-block-chunk-seg-size=10MB
            to reduce memory pressure during fix.
```

---

### ⚖️ Comparison Table

| Label type            | Example                 | Cardinality        | Memory impact | Safe?   |
| --------------------- | ----------------------- | ------------------ | ------------- | ------- |
| HTTP method           | GET, POST, PUT          | 5 values           | Trivial       | Yes     |
| HTTP status class     | 2xx, 4xx, 5xx           | 5 values           | Trivial       | Yes     |
| Service name          | checkout, payment       | 10-50 values       | Trivial       | Yes     |
| Region                | us-east-1, eu-west      | 5-20 values        | Trivial       | Yes     |
| Pod name              | checkout-7f4b-xz9p      | 100s-1000s, grows  | Medium        | Caution |
| Endpoint (normalised) | /api/users/{id}         | 20-200 values      | Low           | Usually |
| IP address            | 203.0.113.42            | 1k-1M values       | Medium-High   | No      |
| User ID               | user-12345              | 1M-100M values     | Catastrophic  | Never   |
| Request ID            | req-abc-123-def         | Unique per request | Catastrophic  | Never   |
| Exception message     | NullPointerException... | Thousands          | High          | Never   |

---

### ⚠️ Common Misconceptions

| Misconception                                                   | Reality                                                                                                                                                                                                                                                     |
| --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Adding more labels gives more insight"                         | Each label multiplies the series count. Adding a 10-value label to a metric with 1,000 series creates 10,000 series. More labels = more memory, not more insight if the labels are high-cardinality.                                                        |
| "Cardinality only matters at large scale"                       | A 10M user service can OOM a Prometheus instance with a single unbounded label added to one metric. Cardinality issues occur at any scale when unbounded labels are used.                                                                                   |
| "I can use high-cardinality labels if the values are temporary" | Prometheus retains series in memory for 2+ hours after last seen. A deployment that creates 100,000 pod-name series keeps those series in memory for 2 hours after the old pods are gone. Churn (frequent creation and deletion of series) is also harmful. |
| "Recording rules fix cardinality problems"                      | Recording rules aggregate data, reducing future cardinality. They cannot remove already-created series from the TSDB head. The fix requires removing the high-cardinality label from the source metric and waiting for old series to expire.                |
| "The Prometheus operator or Grafana handles cardinality"        | No. Cardinality is a Prometheus TSDB constraint. Neither Grafana (visualisation layer) nor the Prometheus Operator (deployment management) limits or controls cardinality. It is a metric instrumentation design problem.                                   |

---

### 🚨 Failure Modes & Diagnosis

**Slow cardinality explosion (gradual OOM)**

**Symptom:**
Prometheus memory grows 500 MB per day. After 2 weeks
it hits the 16 GB limit and is OOM-killed. The team
notices Prometheus is restarting every 2 weeks but
has not connected it to cardinality.

**Root Cause:**
A metric with a `pod_name` label. Each Kubernetes
deployment creates new pods with new hash suffixes.
Old series expire after 2h, but new ones are created
faster than old ones expire during rolling deploys.
Over 2 weeks: 50 services x 3 replicas x 14 deployments
= 2,100 unique pod_names. With 50 metrics all having
`pod_name`: 50 x 2,100 = 105,000 extra series over
baseline.

**Diagnosis:**

```bash
# Check series count trend (growing = leak)
# Look at Prometheus memory over time in Grafana
process_resident_memory_bytes{job="prometheus"}
# Also: check series count growth
increase(prometheus_tsdb_head_series[7d])
# If growing linearly → cardinality leak

# Find metrics with pod-name churn:
curl http://prometheus:9090/api/v1/status/tsdb | \
  jq '.data.labelValueCountByLabelName | to_entries |
    sort_by(.value) | reverse | .[:5]'
# High "pod_name" count = churn problem
```

**Fix:**

```yaml
# Add recording rule to aggregate pod-level metrics
# to service-level before long-term retention
- record: service:requests:rate5m
  expr: |
    sum without (pod_name, pod, instance) (
      rate(http_requests_total[5m])
    )

# Drop pod_name from original metric after 1h retention
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Metrics -- Types (Counter, Gauge, Histogram)` -
  all metric types are affected by cardinality; the
  label system is the source of the issue
- `Prometheus -- Metrics Collection` - the pull-based
  metrics system where cardinality is the primary
  scaling constraint

**Builds On This (learn these next):**

- `Observability at Scale (Sampling, Aggregation)` -
  managing cardinality is the core challenge of
  scaling Prometheus; aggregation is the solution
- `Platform Observability Engineering` - platform
  teams enforce cardinality budgets and governance
  across all services

**Alternatives / Comparisons:**

- `Logs (ELK/EFK)` - the correct storage for high-
  cardinality data (user IDs, request IDs, full URLs).
  Logs are indexed differently: text search, not
  label-based time series. Use logs for per-user
  analytics, not metrics.
- `Distributed Tracing (Jaeger/Zipkin)` - the correct
  storage for per-request context (trace ID, span ID).
  Traces handle high-cardinality per-request data;
  metrics aggregate across requests.

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ FORMULA      │ cardinality =                            │
│              │ |label_1_vals| x |label_2_vals| x ...    │
│              │ 4 methods x 7 statuses x 3 services = 84 │
├──────────────┼──────────────────────────────────────────┤
│ MEMORY COST  │ ~500-1000 bytes per active time series   │
│              │ 1M series = ~500 MB - 1 GB RAM           │
│              │ 100M series = ~50-100 GB → OOM risk      │
├──────────────┼──────────────────────────────────────────┤
│ SAFE LABELS  │ http_method, status_class, service_name  │
│              │ environment, region, error_type          │
│              │ Bounded: < ~1,000 unique values          │
├──────────────┼──────────────────────────────────────────┤
│ FORBIDDEN    │ user_id, customer_id, request_id         │
│ LABELS       │ url, ip_address, email, username         │
│              │ Any value that grows with traffic        │
├──────────────┼──────────────────────────────────────────┤
│ DETECTION    │ prometheus_tsdb_head_series              │
│              │ Alert: > 2M warn, > 10M critical         │
│              │ TSDB status: /api/v1/status/tsdb         │
├──────────────┼──────────────────────────────────────────┤
│ FIX          │ Remove high-cardinality label from metric│
│              │ Move that dimension to logs or traces    │
│              │ Use recording rules to pre-aggregate     │
├──────────────┼──────────────────────────────────────────┤
│ PREVENT      │ Cardinality lint in CI (before deploy)   │
│              │ Label allowlist in metrics registry      │
│              │ PR checklist: cardinality review required│
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Observability at Scale, Prometheus       │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Data schema design determines operational cost.
In Prometheus: label design determines RAM cost.
In relational databases: index design determines
query cost and storage. In Elasticsearch: field
mapping and cardinality determine heap usage
(high-cardinality keyword fields cause fielddata
heap exhaustion - the Elasticsearch equivalent of
Prometheus OOM). In Kafka: partition count determines
broker memory and consumer group coordination cost.
In Redis: key design determines memory usage and
eviction pressure. In every data system: the
dimensionality of the schema (how many unique
combinations of values can exist) is the primary
driver of storage and memory cost. Design schemas
and labels before optimising code - the multiplier
effect of poor dimension design dwarfs all other
performance concerns.

---

### 💡 The Surprising Truth

The most counterintuitive cardinality insight: the
Prometheus OOM that takes down your entire monitoring
system is usually caused by one developer adding
one label to one metric. Not a traffic spike. Not
a configuration change. Not a security incident.
One label. The asymmetry is stark: adding a `user_id`
label to a payment counter takes 10 seconds of
typing. The resulting 280 million time series can
crash Prometheus in under an hour, taking all
dashboards and all alerts offline, creating a
secondary incident during which the original services
may be degrading undetected. The prevention cost
(cardinality lint in CI, label allowlist) is measured
in days. The remediation cost (Prometheus restart,
metric rollback, post-mortem) is measured in hours.
Cardinality is the highest-leverage prevention
investment in the observability stack.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[CALCULATE]** Given a metric with labels
   `{status_class (5 values), method (5 values),
user_id (10M values), service (10 values)}`,
   calculate the total cardinality and the estimated
   RAM usage at 1KB per series.
2. **[IDENTIFY]** Review the following metric labels
   and classify each as safe, caution, or forbidden:
   `user_id`, `http_method`, `pod_name`, `region`,
   `error_message`, `payment_status`, `request_url`.
3. **[FIX]** Write the correct version of a metric
   that currently has a `user_id` label. Show where
   the per-user data should go instead.
4. **[MONITOR]** Write a PromQL query and Prometheus
   alert that detects cardinality growth before OOM.
5. **[PREVENT]** Design a cardinality enforcement
   system for a team of 20 engineers: what CI check,
   what runtime enforcement, and what label governance
   process.

---

### 🧠 Think About This Before We Continue

**Q1.** A metric `http_requests_total` has labels:
`method` (5 values), `status` (10 values), `service`
(20 services), `pod_name` (3 pods per service, new
hash on every deploy). Calculate: (a) current
cardinality, (b) after a monthly deploy cycle (10
deployments, 3 new pods each, old pods not immediately
expired - 2h TTL). How does this compare to budget
of 1M total series and 4 GB RAM?
_Hint: (a) Current: 5 x 10 x 20 x (20 services x 3 pods)
= 5 x 10 x 20 x 60 = 60,000 series. Fine.
(b) After 10 deploys: each deploy creates 3 new pods per
service = 3 x 20 = 60 new pod names. With 2h TTL, old
pods linger for 2h. During active deploy: up to 10 x 60
= 600 pod_names still alive. 5 x 10 x 20 x 600 = 600,000
series. Still under 1M budget. Memory: 600K x 1KB = 600 MB.
Acceptable. But at 100 services or 50 metrics sharing
pod_name: 10x to 60M series and 60 GB → OOM. Pod_name
is a "caution" label, not "safe."_

**Q2.** A colleague proposes adding a `trace_id` label
to a latency histogram metric, arguing "it lets us
correlate metrics with specific traces for debugging."
What is wrong with this proposal? What is the correct
architecture for trace-metric correlation?
_Hint: trace_id is unique per request = unbounded.
10k req/s = 10k new trace_id values per second.
In 1 hour: 36M series created from this one metric.
In 2h: 72M series (before old series expire). OOM.
Correct architecture: do not embed trace_id in metrics.
Instead: (a) include trace_id in structured logs alongside
the request duration (log correlation). (b) OTel exemplars:
attach a trace_id as an exemplar (not a label) to a histogram
sample. Exemplars are sparse (1 per histogram bucket, stored
externally), not a separate time series per trace_id.
Grafana can follow an exemplar from a metric spike to
the corresponding Jaeger trace. This is the correct
metrics-to-trace correlation mechanism._

**Q3 (TYPE G):** You are the platform SRE lead for
a company with 500 microservices across 5 engineering
teams. Each team is independently adding metrics.
Current Prometheus instance: 8M series (healthy budget:
2M). Growing 500k per week. At this rate: OOM in 6
weeks. Design a cardinality governance programme to:
(a) stop the growth immediately, (b) identify and
fix the existing offenders, (c) prevent future
occurrences, (d) enforce limits without blocking
legitimate metric additions.
_Hint: (a) Immediate: set per-tenant series limit in
Cortex/Thanos (if using federation) or add
--storage.tsdb.max-block-chunk-seg-size limit to
Prometheus as emergency measure. Deploy cardinality
monitoring alert (tsdb_head_series > 2M warn).
(b) Run TSDB status API audit. Top-N metrics by series
count. Contact owning teams. SLA: fix within 1 week
or metric will be dropped. (c) CI cardinality lint
(Python script checking label names against allowlist).
Add to all service Dockerfiles/CI pipelines. Label
allowlist enforced by platform team. (d) Labels not
in allowlist: file a cardinality review request (JIRA).
Platform team reviews in 48h. If approved: add to
allowlist. New labels allowed only after review. Metrics
remain unblocked - only new/unknown labels need review.
Track compliance: weekly cardinality health report
per team._

---

### 🎯 Interview Deep-Dive

**Q1: "What is cardinality in Prometheus and why is it a problem?"**
_Why they ask:_ One of the most common production Prometheus
failure modes. Tests whether the engineer has real experience.
_Strong answer includes:_

- Cardinality = number of unique time series = product
  of unique values per label.
- Each unique label combination = one time series.
  One time series = ~500 bytes-1KB RAM in Prometheus head.
- High-cardinality labels (user_id, request_id) create
  millions of series, exhausting RAM → Prometheus OOM.
- Primary prevention: only use bounded labels (< 1000
  unique values, known set). Never use user_id, request_id,
  URL, IP as labels.
- Detection: `prometheus_tsdb_head_series`. Alert > 2M.
- Fix: remove the label; move that dimension to logs.

**Q2: "A colleague wants to add a user_id label to your
payment metric to track per-user payments. How do you respond?"**
_Why they ask:_ Tests ability to reason under pushback
and propose correct alternatives.
_Strong answer includes:_

- Decline the label: user_id is unbounded (10M users =
  10M series per metric per label combination). Will OOM
  Prometheus.
- The data belongs in logs, not metrics. Log the payment
  event with user_id, currency, amount, status, trace_id.
  Query Kibana/Loki for per-user payment history.
- If aggregated user analytics are needed (e.g., payments
  by user_tier): replace user_id with user_tier (gold,
  silver, free = 3 bounded values). The metric counts
  payments per tier, not per user.
- For specific user debugging: use traces (filter by
  user_id attribute in Jaeger). Traces handle per-request
  context; metrics aggregate across requests.

**Q3: "How would you design cardinality governance for
a team of 50 engineers adding metrics daily?"**
_Why they ask:_ Tests system design thinking for
the observability platform.
_Strong answer includes:_

- CI lint: Python script scanning metric definitions
  for forbidden labels (user_id, request_id, url, ip).
  Fails the build if detected.
- Label allowlist: maintained by platform team. New labels
  require a cardinality review (48h SLA). Labels not in
  the allowlist are blocked at CI. Prevents unknown labels
  from slipping through.
- Runtime: monitor prometheus_tsdb_head_series. Alert
  at 2M (warning) and 10M (critical/page). Per-metric
  cardinality report (TSDB status API) in weekly ops review.
- Cultural: cardinality review added to PR checklist
  template. "Does this metric have unbounded labels?"
  is a required checkbox. Engineers understand the cost
  because the team has experienced an OOM and documented
  it in the post-mortem playbook.

## OBS-027 - Cardinality in Metrics Systems

> Entry stub. Generate full content using Master Prompt v3.0.
