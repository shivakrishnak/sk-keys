---
id: LNX-104
title: "Linux Observability Platform Design"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-064, LNX-065, LNX-101
used_by: LNX-105
related: LNX-064, LNX-065, LNX-101, LNX-105
tags: [observability, platform-engineering, prometheus, grafana, loki, tempo, node-exporter, alertmanager, fluent-bit, fluentd, opentelemetry, jaeger, zipkin, metrics-logs-traces, sli-slo-sla, red-method, use-method, cardinality, scraping, service-discovery, pushgateway, recording-rules, alerting-rules, grafana-dashboards, linux-monitoring, sre-platform, observability-stack]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 104
permalink: /technical-mastery/lnx/linux-observability-platform-design/
---

## TL;DR

An observability platform provides three signals: **metrics** (time-series
numbers: CPU, memory, request rate), **logs** (structured or unstructured
text events), and **traces** (distributed request flows across services).
Standard Linux/cloud-native stack: **Prometheus** (pull-based metrics, `scrape_interval`
15s, stores in TSDB) + **node_exporter** (host metrics: CPU, memory, disk, network)
+ **Grafana** (dashboards) + **Alertmanager** (routing alerts to PagerDuty/Slack)
+ **Loki** (log aggregation, same query language family as Prometheus) + **Tempo**
(distributed tracing, Jaeger/Zipkin compatible). **OpenTelemetry** is the
standard instrumentation SDK and collection pipeline. SLI/SLO design: measure
user-facing reliability; alert on error budget burn rate, not raw metric thresholds.
Cardinality is the critical scaling challenge: too many unique label combinations
causes Prometheus OOM.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-104 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | observability, Prometheus, Grafana, Loki, OpenTelemetry, SLI/SLO, metrics, logs, traces, node_exporter |
| **Prerequisites** | LNX-064 (performance tools), LNX-065 (network monitoring), LNX-101 (eBPF) |

---

### The Problem This Solves

**Problem 1**: Production outage at 3 AM. Alert fires: "API error rate > 5%."
Without observability: look at logs manually, guess which service is causing
it, SSH to servers to run ad-hoc commands. With a full observability platform:
Grafana shows error rate spike starting at 02:47 on the payment service. Loki
shows "connection pool exhausted" logs from payment service at that time.
Prometheus shows database connection count hit maximum at 02:46. Correlation
is instant: database connection pool was the root cause. Time-to-detection:
1 minute vs 30 minutes.

**Problem 2**: New service deployment causes latency regression. Without
observability: user complaints after deployment, rollback based on "feels
slow." With SLO-based alerting: p99 latency SLI exceeds SLO threshold, error
budget burn rate alert fires within 5 minutes of deployment. Automated
rollback triggered or on-call paged with full context.

---

### Textbook Definition

**Observability**: The ability to infer the internal state of a system from
its external outputs. The "three pillars" framework:

| Pillar | What | Tool |
|--------|------|------|
| Metrics | Numeric measurements over time | Prometheus, InfluxDB, Datadog |
| Logs | Text/structured event records | Loki, Elasticsearch, Splunk |
| Traces | Request flow across service boundaries | Tempo, Jaeger, Zipkin, AWS X-Ray |

**SLI (Service Level Indicator)**: A metric that measures service quality from
the user's perspective (e.g., "fraction of requests completed in <200ms").

**SLO (Service Level Objective)**: A target value for an SLI (e.g., "99.9% of
requests must complete in <200ms").

**Error budget**: 1 - SLO. If SLO is 99.9%, error budget is 0.1% (43.8 minutes
of downtime per month). Alerts fire when burn rate threatens to exhaust the
error budget.

---

### Understand It in 30 Seconds

```bash
# === Prometheus: pull-based metrics collection ===

# prometheus.yml (configuration):
cat prometheus.yml
# global:
#   scrape_interval: 15s      # scrape targets every 15 seconds
#   evaluation_interval: 15s  # evaluate rules every 15 seconds
#
# scrape_configs:
#   - job_name: 'node_exporter'
#     static_configs:
#       - targets: ['server01:9100', 'server02:9100', 'server03:9100']
#
#   - job_name: 'kubernetes_pods'
#     kubernetes_sd_configs:
#       - role: pod             # automatically discover pods
#     relabel_configs:
#       - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
#         action: keep
#         regex: true

# Start Prometheus:
./prometheus --config.file=prometheus.yml --storage.tsdb.path=/data/prometheus

# Prometheus HTTP API:
curl 'localhost:9090/api/v1/query?query=node_cpu_seconds_total'

# === PromQL: query language ===

# CPU utilization (1-idle) on all nodes:
# 1 - avg by (instance) (
#   rate(node_cpu_seconds_total{mode="idle"}[5m])
# )
# Result: per-instance CPU utilization 0.0 - 1.0

# 99th percentile HTTP request duration:
# histogram_quantile(0.99, 
#   rate(http_request_duration_seconds_bucket[5m])
# )

# Request error rate:
# rate(http_requests_total{status=~"5.."}[5m]) 
# / rate(http_requests_total[5m])

# === Alertmanager rules ===
cat alert_rules.yml
# groups:
#   - name: host_alerts
#     rules:
#       - alert: HighCPU
#         expr: |
#           1 - avg by (instance) (
#             rate(node_cpu_seconds_total{mode="idle"}[5m])
#           ) > 0.9
#         for: 5m              # must be true for 5 minutes
#         labels:
#           severity: warning
#         annotations:
#           summary: "High CPU on {{ $labels.instance }}"
#           description: "CPU > 90% for 5+ minutes"

# === node_exporter: host metrics ===

# Install and run:
./node_exporter --web.listen-address=:9100

# Key metrics exposed by node_exporter:
# node_cpu_seconds_total{cpu="0",mode="idle"}: CPU idle time
# node_memory_MemAvailable_bytes: available memory
# node_filesystem_avail_bytes{mountpoint="/"}: disk free
# node_network_receive_bytes_total{device="eth0"}: network in
# node_load1: 1-minute load average

# Check what's exported:
curl -s localhost:9100/metrics | grep -E "^node_(cpu|memory|disk)" | head -20

# === Grafana: dashboards ===
# Key Grafana queries for Linux host dashboard:
# 
# Panel: CPU Utilization (%):
# 100 * (1 - avg by (instance) (
#   rate(node_cpu_seconds_total{mode="idle"}[5m])
# ))
#
# Panel: Memory Usage (%):
# 100 * (1 - (
#   node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes
# ))
#
# Panel: Disk I/O (MB/s):
# rate(node_disk_read_bytes_total[5m]) / 1024 / 1024  # reads MB/s
# rate(node_disk_written_bytes_total[5m]) / 1024 / 1024  # writes MB/s

# === Loki: log aggregation ===
# Loki uses LogQL (similar to PromQL):

# All error logs from the payment service:
# {service="payment"} |= "ERROR"

# Error rate per minute for a specific service:
# rate({service="payment"} |= "ERROR" [1m])

# Parse structured JSON logs and filter by field:
# {service="payment"} | json | duration > 1000

# === Fluent Bit: log shipping ===
# Lightweight log forwarder (100MB RAM vs Fluentd's 1GB+)
cat fluent-bit.conf
# [INPUT]
#   Name tail
#   Path /var/log/app/*.log
#   Tag app.*
#   Multiline on        # handle Java stack traces spanning multiple lines
#
# [FILTER]
#   Name parser
#   Match app.*
#   Key_Name log
#   Parser json         # parse JSON structured logs
#
# [OUTPUT]
#   Name loki
#   Match app.*
#   Host loki.monitoring.svc.cluster.local
#   Port 3100
#   Labels job=fluentbit,service=payment
```

---

### First Principles

```
The observability problem:

Single server (1990s):
  "Is server slow?" -> SSH, run top, ps, netstat
  Answer in 5 minutes
  One brain can hold entire system state

Microservices cluster (now):
  200 services, 500 pods, 20 nodes
  "Is payment slow?" -> which of 200 services is the bottleneck?
  Request traverses: API gateway -> auth -> user -> payment -> fraud -> db
  Each hop adds latency
  Manual SSH is impossible at this scale

Observability platforms solve:
  "Correlated visibility across all services simultaneously"
  
THREE PILLARS and when to use each:

Metrics (Prometheus/Grafana):
  What: numeric measurements sampled over time
  Use for: dashboards, alerting, trend analysis, capacity planning
  Format: metric_name{label1="value1",...} numeric_value timestamp
  
  When metrics are insufficient:
  "CPU is 90% but why?" -> need traces or logs to find root cause
  
  Characteristics:
  - Aggregated: exact individual events not stored
  - Efficient: high-cardinality aggregation before storage
  - Retrospective: historical analysis easy
  - Low storage overhead vs logs
  
Logs (Loki/Elasticsearch):
  What: text records of discrete events
  Use for: debugging, audit trail, error details, context
  Format: timestamp + text (or structured JSON)
  
  When logs are insufficient:
  "Error in payment service" -> but which request caused it?
  Hard to correlate across services without trace IDs in logs
  
  Characteristics:
  - Verbose: full event detail preserved
  - Expensive: high storage cost at scale
  - Flexible: arbitrary text, any format
  - Isolated: per-service, hard to correlate across services

Traces (Tempo/Jaeger):
  What: end-to-end path of a single request across services
  Use for: latency breakdown, service dependency analysis, root cause
  Format: span tree (parent-child spans, each with timing)
  
  When traces are insufficient:
  "Request was slow" but need resource-level metrics to understand why
  (traces show what happened, not system resource state)
  
  Characteristics:
  - Request-scoped: per-request detail
  - Correlated: spans linked by trace ID across services
  - Sampling: typically 0.1-1% sampled (too expensive to store all)
  - Requires instrumentation: app must propagate trace context

SLI/SLO design:
  SLIs capture what users experience (not what you measure internally)
  
  WRONG SLI: "CPU < 80%" (infrastructure metric, not user-facing)
  WRONG SLI: "Error rate < 1%" (aggregate, misses latency)
  WRONG SLI: "Availability > 99.9%" (vague, no definition of "available")
  
  GOOD SLI: "Fraction of requests in <200ms with status 2xx"
  Good because: directly measures user experience, quantifiable,
                threshold makes sense for this service
  
  Error budget:
  Monthly budget for 99.9% SLO = 43.8 minutes
  
  Burn rate alerting:
  If burning at 14.4x rate: will exhaust monthly budget in 1 hour
  Alert: "page immediately" (1-hour budget, fast burn)
  
  If burning at 1x rate: will exhaust exactly at end of month
  Alert: "next day response" (slow burn, not emergency)
  
  This is more actionable than: "error rate > 1%"
  (which may or may not be impacting your SLO)

Cardinality: the primary scaling challenge:

Each unique {metric_name, label_values} combination = one time series
High cardinality = too many unique combinations = OOM in Prometheus

BAD: request_total{user_id="abc123",...}
  1M users * 10 metrics = 10M time series
  Prometheus stores each series in memory during scrape window
  Memory: 10M series * ~3KB = 30GB memory! OOM crash.

GOOD: request_total{service="payment",status="200",...}
  10 services * 5 statuses = 50 time series
  Memory: 50 * 3KB = negligible

Rule: NEVER use high-cardinality values as labels (user IDs, IP addresses,
      request IDs, UUIDs). These belong in traces, not metrics.
```

---

### Thought Experiment

Building a production observability stack for 20 Kubernetes nodes:

```bash
# === Kubernetes observability stack with kube-prometheus-stack ===

# kube-prometheus-stack: Helm chart that installs:
# - Prometheus operator
# - node_exporter DaemonSet
# - kube-state-metrics
# - Grafana
# - Alertmanager
# - Default Kubernetes dashboards and alerts

# Install:
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install monitoring prometheus-community/kube-prometheus-stack \
    --namespace monitoring \
    --create-namespace \
    --set grafana.adminPassword=SecurePassword123 \
    --set prometheus.prometheusSpec.retention=15d \
    --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=100Gi

# Verify:
kubectl -n monitoring get pods
# prometheus-monitoring-kube-prometheus-0  Running
# alertmanager-monitoring-kube-alertmanager-0  Running
# monitoring-grafana-xxx  Running
# monitoring-prometheus-node-exporter-xxx (one per node)

# Access Grafana:
kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80
# Navigate: http://localhost:3000, admin/SecurePassword123
# Built-in dashboards: Kubernetes / Cluster Resources, Node, Pod

# === Custom SLO alerting ===

# Define SLO: 99.9% of payment requests complete in <500ms
# Prometheus recording rules for SLI:
cat slo-rules.yml
# groups:
#   - name: payment_slo
#     interval: 1m
#     rules:
#       # SLI: fraction of requests with latency < 500ms and status 2xx
#       - record: payment:request_success_rate:1m
#         expr: |
#           rate(http_requests_total{
#             service="payment",status=~"2..",
#             le="0.5"  # histogram bucket: <500ms
#           }[1m])
#           / rate(http_requests_total{service="payment"}[1m])
#
#       # Error budget burn rate alert (fast burn: 14.4x for 1-hour window):
#       - alert: PaymentSLOBudgetBurnFast
#         expr: |
#           (1 - payment:request_success_rate:1m) > 14.4 * (1 - 0.999)
#         for: 2m
#         labels:
#           severity: critical
#         annotations:
#           summary: "Payment SLO: fast burn rate"
#           description: "Burning error budget at 14.4x rate. Will exhaust in 1h."

# === Cardinality monitoring ===

# Check which metrics have high cardinality:
curl -s 'localhost:9090/api/v1/query?query=topk(10,count({__name__=~".+"} by (__name__, job)))' \
    | python3 -m json.tool

# Or use Grafana explore:
# {__name__="http_requests_total"} -> count distinct label sets
# If count > 10,000: check which labels are high-cardinality

# === Distributed tracing with OpenTelemetry ===

# OpenTelemetry collector (central collection and routing):
cat otel-collector.yml
# receivers:
#   otlp:
#     protocols:
#       grpc:  # OpenTelemetry GRPC protocol (default port 4317)
#       http:  # OpenTelemetry HTTP (default port 4318)
#   jaeger:
#     protocols:
#       grpc:  # Accept Jaeger format
#
# processors:
#   batch:  # batch spans before sending (reduces network calls)
#   tail_sampling:  # only keep interesting traces (slow, errors)
#     decision_wait: 10s
#     policies:
#       - name: errors, type: status_code, status_code: {status_codes: [ERROR]}
#       - name: slow, type: latency, latency: {threshold_ms: 500}
#       - name: sample-1pct, type: probabilistic, probabilistic: {sampling_percentage: 1}
#
# exporters:
#   otlp:
#     endpoint: tempo:4317  # Grafana Tempo
#
# service:
#   pipelines:
#     traces:
#       receivers: [otlp, jaeger]
#       processors: [batch, tail_sampling]
#       exporters: [otlp]
```

---

### Mental Model / Analogy

```
Observability platform = aircraft instrument panel

Metrics (Prometheus/Grafana) = flight instruments:
  Altitude, airspeed, heading, fuel level
  Continuous numerical readings over time
  Dashboard: all instruments visible simultaneously
  Alerting: "altitude < 1000ft, pull up!" (threshold violation)
  
  Limitation: tells you "airspeed = 250 knots"
  Doesn't tell you WHY airspeed dropped (need more investigation)

Logs (Loki) = pilot's voice recorder (CVR):
  Detailed event-by-event records
  "Engine 2 flame-out warning at 14:23:15"
  "Fuel pump alert at 14:23:16"
  Full context for every event
  
  Limitation: 10 hours of recordings, hard to correlate
  across multiple aircraft (cross-service correlation)

Traces (Tempo/Jaeger) = flight data recorder (FDR):
  Records the JOURNEY of each flight (request)
  "Flight NYC->LAX: departed 09:00, cruised 10h, landed 19:00"
  Spans: departure, each leg, landing (each with timing)
  Can see: which leg was delayed (which service added latency)
  
  Limitation: expensive (store every flight = too much data)
  Solution: sample (keep 1% of flights, all error flights)

SLI/SLO = airline performance guarantee:
  SLI (indicator): "% of flights arriving within 30min of schedule"
  SLO (objective): "95% of flights on time"
  Error budget: "5% of flights can be late"
  
  WRONG approach: alert when "any flight is 5 minutes late"
  (too many alerts, desensitizes team)
  
  RIGHT approach: alert on burn rate
  "In the last hour, 3% late flights vs 0.42% budget per hour
  -> burning budget 7x too fast -> will exhaust monthly budget in 4 days"
  (one meaningful alert, not noise)

Cardinality = number of distinct flight paths recorded:
  Low cardinality: count by airline (20 airlines = 20 metrics)
  High cardinality: count by passenger name (1M passengers = 1M metrics!)
  
  Prometheus rule: label values must be bounded
  Use traces (not metrics) for per-request, per-user data

OpenTelemetry = universal flight data format:
  Before: each airline had proprietary black box format
  After: all airlines use same format, any airport can read any black box
  
  OpenTelemetry: vendor-neutral SDK + protocol
  Instrumented once, export to any backend (Jaeger, Tempo, Datadog, etc.)
  
node_exporter = airport weather station:
  Measures environmental conditions: wind, visibility, temperature
  (CPU, memory, disk, network = "weather conditions" for the kernel)
  Prometheus reads the station every 15 seconds
  Grafana shows the weather history
```

---

### Gradual Depth - Five Levels

**Level 1:**
Three pillars: metrics, logs, traces. Prometheus: what it does (pull-based
metric collection). node_exporter: what it measures. Grafana: dashboards
from Prometheus. SLI/SLO concepts: what you're measuring and why. Difference
between alerting on raw metrics vs user experience.

**Level 2:**
Prometheus data model: metric name + labels + value + timestamp. PromQL basics:
rate(), avg_by(), histogram_quantile(). Alert rule structure: expr, for, severity.
Alertmanager routing. Loki and LogQL basics. Fluent Bit for log shipping. kube-
prometheus-stack for Kubernetes. node_exporter key metrics: CPU, memory, disk, network.

**Level 3:**
Cardinality: what causes high cardinality, how to detect and mitigate.
Prometheus recording rules for pre-computation. Error budget and burn rate
alerting math. OpenTelemetry: SDK instrumentation, collector configuration,
tail sampling. Grafana Loki correlation with Prometheus (exemplars). Remote
write for long-term storage (Thanos, Cortex, Mimir). Service discovery in
Prometheus: Kubernetes SD, EC2 SD.

**Level 4:**
Prometheus federation for multi-cluster. Thanos/Cortex/Mimir for horizontally
scalable Prometheus. Custom exporters: writing a Go Prometheus exporter.
OpenTelemetry collector tail sampling: keeping only interesting traces.
Prometheus TSDB internals: block-based storage, head block, compaction.
Grafana OnCall for alert routing and escalation. DORA metrics (deployment
frequency, lead time, MTTR, change failure rate) as observability.

**Level 5:**
Prometheus query optimization: expensive PromQL queries, reducing scrape
overhead with relabeling. High-cardinality handling at scale: pre-aggregation
recording rules, metric cardinality reduction pipeline. Observability for
serverless (Lambda, Cloud Functions): distributed tracing challenges without
persistent processes, cold start measurement. Streaming telemetry vs polling:
eBPF-based continuous profiling (Parca, Pyroscope). Correlation across
pillars: exemplars (link from metrics to traces), trace-to-log correlation
(trace ID in logs). OpenTelemetry semantic conventions for consistent naming.
Vendor lock-in avoidance strategy: OTel for instrumentation, open backends
vs commercial APM.

---

### Code Example

**BAD - low-quality observability instrumentation:**
```python
# BAD: High-cardinality labels (user_id, ip_address)
# This will OOM Prometheus within days!
from prometheus_client import Counter

request_counter = Counter(
    'http_requests_total',
    'Total HTTP requests',
    # BAD: user_id has 1M unique values, ip_address has 10M+
    # 1M users * 5 status codes * 10 endpoints = 50M time series!
    ['user_id', 'ip_address', 'status_code', 'endpoint']
)

def handle_request(user_id, ip, status, endpoint):
    # BAD: creating new time series for every unique user!
    request_counter.labels(
        user_id=user_id,    # NEVER use user_id as label
        ip_address=ip,       # NEVER use IP as label
        status_code=status,
        endpoint=endpoint
    ).inc()

# BAD: alerting on raw metrics without considering user impact
# ALERT: CPU > 80% (irrelevant if users aren't affected!)
# ALERT: Error rate > 1% (irrelevant if SLO is 99%)
# These generate noise without actionable context
```

```python
# GOOD: low-cardinality metrics with user-impacting alerting

from prometheus_client import Counter, Histogram, start_http_server
import time

# Low-cardinality labels: bounded set of values for each label
# service: 10 services, method: GET/POST/PUT/DELETE (4),
# status: 1xx/2xx/3xx/4xx/5xx (5)
# Total: 10 * 4 * 5 = 200 time series (reasonable!)
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['service', 'method', 'status_code_class']  # NOT user_id, NOT IP
)

# Histogram for latency SLI measurement:
# Buckets at SLO thresholds + percentiles
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['service', 'endpoint'],
    buckets=[0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
    # 0.5s bucket = SLO threshold (easy to calculate %ile above threshold)
)

def handle_request(service, method, endpoint, user_id):
    start = time.time()
    # Process request...
    duration = time.time() - start
    status = 200  # or actual status

    # LOW-CARDINALITY: group status codes into classes
    status_class = f"{status // 100}xx"  # "2xx", "4xx", "5xx"

    REQUEST_COUNT.labels(
        service=service,
        method=method,
        status_code_class=status_class  # NOT raw status code
    ).inc()

    REQUEST_LATENCY.labels(
        service=service,
        endpoint=endpoint
    ).observe(duration)

    # High-cardinality data belongs in TRACES, not metrics:
    # Add user_id to trace span attributes (sampled, not aggregated)
    # span.set_attribute("user.id", user_id)
```

```yaml
# GOOD: SLO-based alerting rules
groups:
  - name: slo_alerts
    rules:
      # SLO: 99.9% of requests in <500ms with 2xx status
      # Fast burn: alert immediately (will exhaust monthly budget in 1h)
      - alert: ServiceSLOFastBurn
        expr: |
          (
            rate(http_requests_total{status_code_class!="2xx"}[1h])
            + rate(http_request_duration_seconds_bucket{le="0.5"}[1h])
              / rate(http_request_duration_seconds_count[1h])
          ) > 14.4 * 0.001
        for: 2m
        labels:
          severity: page  # wake someone up
        annotations:
          summary: "SLO fast burn: error budget exhausting in 1h"
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "More metrics = better observability" | More metrics with high cardinality = OOM Prometheus, slower queries, increased cost, harder to find what matters. Effective observability requires choosing the RIGHT metrics, not all metrics. The RED Method (Rate, Errors, Duration) and USE Method (Utilization, Saturation, Errors) provide systematic frameworks: 5-10 metrics per service following these methods tell you more than 100 ad-hoc metrics. High-cardinality detail belongs in traces (sampled, per-request), not metrics (aggregated system-wide). The goal is the minimum number of metrics that allows you to answer "is the service healthy and what's wrong if not?" without noise. |
| "Distributed tracing requires modifying all application code" | Zero-code instrumentation options: (a) eBPF-based tracing (Pixie, Odigos): trace Go, Java, Python applications with uprobes, no application changes required; (b) Java agent (opentelemetry-javaagent.jar): `-javaagent:otel-agent.jar` JVM argument instruments the JVM automatically; (c) Service mesh (Istio/Linkerd): sidecar proxy intercepts all traffic, adds tracing headers automatically; (d) AWS X-Ray daemon: intercepts SDK calls without code changes. Even when code changes are needed: OpenTelemetry auto-instrumentation libraries handle common frameworks (Spring, Express, Django, Flask) with minimal configuration. Adding tracing to an existing service often requires 5-10 lines of configuration, not significant code changes. |
| "Prometheus stores data forever" | Prometheus is designed for short-to-medium-term storage (15 days default, practical maximum ~6 months on a single instance before storage costs and query latency become problems). For long-term storage (years of metrics for capacity planning, trends, compliance): use Prometheus remote write to Thanos, Cortex, Mimir, or a cloud service (Amazon Managed Prometheus, Grafana Cloud). These systems handle: infinite retention (limited only by storage cost), global query (metrics from multiple Prometheus instances), horizontal scalability (single Prometheus can store ~millions of series; Thanos scales to hundreds of millions). The correct architecture: Prometheus for recent, hot data + remote write to long-term store for historical analysis. |
| "Alerting on every error is better than missing errors" | Alert fatigue is the #1 failure mode for on-call teams. If alerts fire constantly during normal operations: engineers learn to ignore them (the "boy who cried wolf" effect). When a real incident occurs: the important alert is lost in the noise. Effective alerting principles: (a) Alert on user impact, not system symptoms (error RATE above SLO threshold, not any error); (b) Alert on what requires immediate human response (not "CPU briefly hit 90%"); (c) Burn rate alerting: the error budget is YOUR customer's patience - alert when it's at risk, not on every wobble; (d) Minimum viable alerts: start with 3-5 high-signal alerts (service down, SLO burn rate critical, disk full in 1 hour) and add more only when you prove they're actionable. Many mature SRE teams run with <10 alert rules per service. |

---

### Failure Modes & Diagnosis

```bash
# === Failure: Prometheus OOM (Out of Memory) ===
# Prometheus pod crashes repeatedly: OOMKilled

# Diagnose cardinality issue:
# In Prometheus UI -> Status -> TSDB Status
# Or via API:
curl -s 'localhost:9090/api/v1/status/tsdb' | \
    python3 -c "import sys,json; d=json.load(sys.stdin); 
    [print(s['metric'],s['seriesCount']) 
     for s in d['data']['seriesCountByMetricName'][:10]]"
# http_requests_total: 15,000,000  <- WAY too high! 15M time series!
# Expected: < 100,000 for most metrics

# Find high-cardinality labels:
curl -s 'localhost:9090/api/v1/label/user_id/values' | \
    python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d['data']))"
# 2,345,678  <- user_id has 2.3M values: NEVER a metric label!

# Fix: drop high-cardinality labels with metric_relabel_configs:
# In prometheus.yml scrape config:
# metric_relabel_configs:
#   - regex: user_id  # drop the user_id label entirely
#     action: labeldrop

# === Failure: Grafana dashboard shows "No data" ===
# Dashboard panels show "No data" even though Prometheus is running

# Debug steps:
# 1. Test query directly in Prometheus UI (localhost:9090):
#    http_requests_total  <- does this return results?

# 2. Check Prometheus targets:
curl -s 'localhost:9090/api/v1/targets' | \
    python3 -m json.tool | grep -E '"health"|"lastError"'
# "health": "down",
# "lastError": "connection refused (server:9100)"
# ^ Target is down! node_exporter not running on that host

# 3. Verify metric name and labels in Prometheus:
curl -s 'localhost:9090/api/v1/series?match[]=http_requests_total' | \
    python3 -m json.tool | head -20
# Shows all label sets for this metric

# 4. Check time range: is Grafana time range correct?
# (Sometimes dashboard shows "last 1 hour" but metric only exists in last 5 min)

# === Failure: Alert never fires despite known issue ===
# Known error rate is high, alert should have fired

# Check alert state in Prometheus:
curl -s 'localhost:9090/api/v1/alerts' | \
    python3 -c "import sys,json; d=json.load(sys.stdin);
    [print(a['name'], a['state']) for a in d['data']['alerts']]"
# HighErrorRate: pending  <- pending means: condition true but 'for: 5m' not yet elapsed

# Check Alertmanager received alerts:
curl -s 'localhost:9093/api/v1/alerts' | python3 -m json.tool

# Check if alert is silenced:
curl -s 'localhost:9093/api/v1/silences' | python3 -m json.tool
# If: matchers include alertname=HighErrorRate -> alert is silenced!
```

---

### Related Keywords

**Foundational:**
LNX-064 (performance tools), LNX-065 (network monitoring), LNX-101 (eBPF)

**Builds on this:**
LNX-105 (Linux networking at fleet scale)

**Related:**
LNX-105 (DPDK, SR-IOV)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `curl localhost:9090/api/v1/query?query=...` | Prometheus HTTP API query |
| `curl localhost:9090/api/v1/status/tsdb` | TSDB status and cardinality |
| `curl localhost:9090/api/v1/targets` | Scrape targets and health |
| `curl localhost:9100/metrics` | node_exporter raw metrics |
| `curl localhost:9093/api/v1/alerts` | Alertmanager active alerts |
| `promtool check rules alert_rules.yml` | Validate alert rules |
| `logcli query '{job="app"} |= "ERROR"'` | Loki CLI query |

**3 things to remember:**
1. Cardinality kills Prometheus: NEVER use user_id, IP addresses, request IDs, or UUIDs as metric labels. Each unique label combination = one time series stored in RAM. For per-request detail: use traces (sampled), not metrics.
2. Alert on user-impact burn rate, not raw metrics. SLO burn rate alert fires when error budget is being consumed too fast - giving you actionable context (how long until SLO is missed) rather than raw "error rate > 1%" noise.
3. The three pillars are complementary: metrics show WHAT (high error rate), logs show WHAT HAPPENED (specific error messages), traces show WHERE (which service in the request chain is failing). Use all three for effective incident response.

---

### Transferable Wisdom

Observability platform design principles transfer directly to: application
performance monitoring (APM) in general (same three pillars, different tools:
Datadog, New Relic, Dynatrace use identical concepts), cloud provider monitoring
(AWS CloudWatch = Prometheus, AWS CloudTrail = Loki for API calls, AWS X-Ray =
Tempo/Jaeger). The SLI/SLO framework transfers to: service contract design
(SLAs between services), API design (specify p99 latency guarantees in API
contracts), product management (translate technical SLIs to user experience
metrics). Prometheus PromQL is the model for: InfluxDB Flux, Grafana Mimir,
AWS CloudWatch Metrics Insights - all use similar functional query languages.
The cardinality challenge (bounded labels) is the same as: database index
design (index on low-cardinality columns, not user_id), Apache Kafka partition
key selection (bounded set of keys for even distribution), CSS class naming
(reusable classes vs per-element styles). Alert fatigue avoidance (alert on
what requires immediate action) applies to: code review feedback (not every
style violation, just critical issues), security scanner results (prioritize
by exploitability, not just existence).

---

### The Surprising Truth

The concept of "observability" as distinct from "monitoring" was popularized
by Twitter and Honeycomb engineers around 2016-2017. Traditional monitoring:
define thresholds on known metrics, alert when crossed. This works when you
know in advance what can fail. Observability: store high-dimensional telemetry
data, ask arbitrary questions about system state after an incident.

The surprising insight: the difference is epistemological, not technical. A
monitoring system asks: "Is the metric above threshold?" (known failure mode,
pre-defined query). An observable system answers: "What was happening in the
system when this user experienced a 5-second response time?" (unknown failure
mode, exploratory query). This distinction led to the "high-cardinality
structured events" approach championed by Honeycomb: store every request as
a structured event with all attributes (user_id, service version, region,
feature flags, etc.), then query interactively. The "metrics + logs + traces"
three-pillars model is a compromise approach (each pillar optimized for cost
efficiency), but the true observability ideal is: one queryable store for all
telemetry with high cardinality support, which is exactly what products like
Honeycomb, Clickhouse-based APMs, and eBPF-based tools are moving toward.

---

### Mastery Checklist

- [ ] Can write basic PromQL queries for CPU, memory, error rate, and latency percentiles
- [ ] Understands cardinality and can identify high-cardinality labels that cause Prometheus problems
- [ ] Can design an SLI/SLO for a web service and write the burn rate alert rule
- [ ] Can set up a basic stack: Prometheus + node_exporter + Grafana for host monitoring
- [ ] Understands when to use metrics vs logs vs traces for different diagnostic questions

---

### Think About This

1. Your Prometheus instance is using 40GB of RAM and growing at 2GB/day.
   The cluster has 500 pods. Walk through your cardinality investigation:
   what queries would you run to identify the high-cardinality metric? Once
   found, what options do you have to fix it (relabeling, recording rules,
   migrating data to traces)? What is the impact of the fix on existing
   dashboards and alerts? How would you prevent this from happening again
   (metric review process, cardinality budgets)?

2. Design an observability strategy for a multi-region microservices deployment
   (3 regions, 50 services, 200 pods per region). Requirements: cross-region
   trace correlation, per-region SLO tracking, global dashboard, and alert
   routing by service ownership team. What would your Prometheus topology
   look like? How would you handle Prometheus federation vs remote write
   for global aggregation? How would you ensure traces can be correlated
   across regions when a request traverses multiple regions?

3. An engineer argues: "We should instrument our application with Datadog
   instead of open-source Prometheus + Grafana. Datadog costs money but
   we don't have to manage the infrastructure." Construct both sides of
   the argument. What are the total cost of ownership considerations for
   open-source vs SaaS observability at 100 services? At 1000 services?
   What lock-in risks exist, and how does OpenTelemetry mitigate them?
   In what scenarios is each approach clearly the better choice?

---

### Interview Deep-Dive

**Foundational:**
Q: Explain the three pillars of observability and when you would use each to debug a production issue.
A: THREE PILLARS OVERVIEW: (1) METRICS: Numerical measurements sampled over time. Prometheus scrapes metrics every 15 seconds from endpoints. Key metrics: request rate, error rate, latency percentiles, CPU/memory/disk. What metrics are GOOD FOR: "Is there a problem?" (dashboards), alerting (when does error rate exceed threshold?), trend analysis (is memory growing over time? capacity planning). What metrics CANNOT answer: "Why is the specific payment request for user X failing?" - metrics are aggregated, individual request detail is lost. (2) LOGS: Text records of discrete events. Stored in Loki or Elasticsearch. Structured JSON logs are searchable. What logs are GOOD FOR: "What exactly happened?" - detailed error messages, stack traces, request context (user ID, request ID). "When did the error start?" - exact timestamps. What logs CANNOT answer well: "Which downstream service is causing this 500ms latency?" - correlation across services requires trace IDs in logs, hard without tracing. (3) TRACES: End-to-end request journey across services. Each trace = tree of spans (one per service/operation), with timing. What traces are GOOD FOR: "Which service in the chain is slow?" - each span has timing, clearly shows where latency is added. "What called what?" - dependency analysis from trace data. What traces CANNOT answer: "Is this happening for all users?" - traces are sampled (0.1-1%), not comprehensive. DEBUGGING WORKFLOW: Use them in order: (1) Metrics: "Error rate is 5% for payment service, started 10 minutes ago" (alert fires). (2) Logs: filter Loki for payment service errors in that time window: "connection pool exhausted" -> root cause candidate. (3) Traces: find a slow trace for payment service, expand spans -> see that database span is 450ms vs normal 5ms -> database is the bottleneck. The correlation: trace ID in logs links a specific log message to a specific trace. Metrics give breadth (all requests), traces give depth (one request in detail), logs give context (what the service logged about that event).

**Expert:**
Q: How do you design SLIs and SLOs for a web service, and how do you use error budgets for alerting?
A: SLI DESIGN PRINCIPLES: Start from user perspective: what does the user care about? (1) Availability: "Is the service responding?" SLI: fraction of requests returning non-5xx response. (2) Latency: "Is the service fast enough?" SLI: fraction of requests completing in <N milliseconds. (3) Correctness: "Is the data right?" SLI: fraction of responses containing expected data. CHOOSE THE RIGHT THRESHOLD: For a payment API: SLI = "fraction of requests completing in <500ms with 2xx status." Why 500ms? User research shows >500ms feels "slow" for payment transactions. Why 2xx? 4xx (client errors) are user error, not service failure - exclude from SLI. HOW TO MEASURE: Using Prometheus histogram (not gauge or counter): `histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{le="0.5"}[5m]))` gives the 99th percentile, but for SLO compliance we want the RATE of requests in the bucket: `rate(http_request_duration_seconds_bucket{le="0.5"}[1h]) / rate(http_request_duration_seconds_count[1h])`. ERROR BUDGET MATH: SLO = 99.9% -> error budget = 0.1% = 43.8 minutes per month. If burning at 14.4x rate: 43.8 / 14.4 = ~3 hours to exhaustion from full budget. BURN RATE ALERTING: Two alerts per SLO: (a) Fast burn: `error_rate > 14.4 * (1 - SLO)` for 2 minutes -> page immediately. At 14.4x burn, monthly budget exhausts in 1 hour. Need immediate action. (b) Slow burn: `error_rate > 1 * (1 - SLO)` for 3 days -> ticket for next business day. At 1x burn: exactly exhausts at month end. Needs attention but not emergency. WHY THIS IS BETTER THAN THRESHOLD ALERTS: A 1% error rate on a service with 99% SLO is fine (still above SLO). A 0.05% error rate on a service with 99.9% SLO might be consuming your budget rapidly. Burn rate alerting is proportional to SLO impact, not raw metric value. OPERATIONAL USE: Error budget as conversation: "We have 5% of our monthly error budget left. Freeze changes until next month." This creates natural incentive alignment: engineering teams own their SLO error budget, they decide how to spend it (risky deployments vs stability).
