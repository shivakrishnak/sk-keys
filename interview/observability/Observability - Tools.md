---
title: "Observability - Tools"
topic: Observability
subtopic: Tools
keywords:
  - Prometheus
  - Grafana
  - ELK Stack
  - OpenTelemetry
  - Jaeger
  - Loki
difficulty_range: medium-hard
status: complete
version: 1
---

# Prometheus

**TL;DR** - Prometheus is a pull-based time-series monitoring system that scrapes metrics from instrumented services, stores them efficiently, and provides PromQL for powerful querying and alerting - the de facto standard for Kubernetes monitoring.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Custom monitoring scripts per service. Metrics stored in different formats. No unified querying. No dimensional data model. Alert rules scattered across various tools. No standard for metric exposition.

---

### Textbook Definition

Prometheus is an open-source systems monitoring and alerting toolkit that collects metrics via a pull model (scraping HTTP endpoints), stores them as time-series data with labels (dimensions), and provides PromQL for flexible querying, with Alertmanager for notification routing.

---

### How It Works

```
Prometheus architecture:
  +------------------+
  | Prometheus Server |
  | - TSDB storage   |
  | - Scrape engine  |
  | - PromQL engine  |
  | - Rule evaluator |
  +--------+---------+
           |
    Pull (scrape every 15s)
           |
  +--------+--------+--------+
  | App :9090/metrics | App   | App   |
  | counter, gauge,  |       |       |
  | histogram exposed|       |       |
  +------------------+-------+-------+
           |
  +--------v---------+
  | Alertmanager     |
  | - Routing        |
  | - Grouping       |
  | - Silencing      |
  +------------------+
           |
  Slack, PagerDuty, Email

Metric types:
  Counter:   Monotonically increasing (requests_total)
  Gauge:     Can go up/down (temperature, queue_size)
  Histogram: Distribution (request_duration_seconds)
  Summary:   Client-calculated percentiles (rare now)
```

```promql
# PromQL examples:

# Request rate over 5 minutes
rate(http_requests_total[5m])

# Error rate percentage
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m])) * 100

# 99th percentile latency
histogram_quantile(0.99,
  rate(http_request_duration_seconds_bucket[5m]))

# Top 5 endpoints by error rate
topk(5,
  sum by (endpoint) (
    rate(http_requests_total{status="500"}[5m])))
```

---

### Quick Recall

**If you remember only 3 things:**

1. Pull-based model: Prometheus scrapes /metrics endpoints (vs push-based like StatsD). Services expose metrics in Prometheus format.
2. PromQL is the query language. Key functions: `rate()` for counters, `histogram_quantile()` for latency percentiles, `sum by()` for aggregation.
3. Label-based dimensional model: same metric name with different labels (method="GET", endpoint="/api/users") enables flexible slicing.

**Interview one-liner:**
"Prometheus provides pull-based metric collection with a dimensional label model, PromQL for flexible querying (rate/histogram_quantile), and Alertmanager for alert routing - I use it with ServiceMonitor CRDs in Kubernetes for auto-discovery and recording rules for pre-computed expensive queries."

---

---

# Grafana

**TL;DR** - Grafana is an open-source visualization platform that creates dashboards from multiple data sources (Prometheus, Loki, Elasticsearch, CloudWatch), providing unified observability views with alerting, annotations, and exploration capabilities.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Prometheus has basic UI but no dashboards. Logs are in ELK. Traces in Jaeger. Switching between 5 tools to debug one issue. No unified view of system health across metrics, logs, and traces.

---

### Textbook Definition

Grafana is a multi-platform open-source analytics and interactive visualization application that connects to numerous data sources (Prometheus, InfluxDB, Elasticsearch, Loki, CloudWatch), providing configurable dashboards, alerting, annotations, and data exploration in a unified interface.

---

### How It Works

```
Grafana in the observability stack:
  +-------------------------------------------+
  |              Grafana UI                    |
  |  +----------+  +--------+  +-----------+ |
  |  | Dashboard|  | Explore|  | Alerting  | |
  |  | (panels) |  | (adhoc)|  | (rules)   | |
  |  +----+-----+  +---+----+  +-----+-----+ |
  +-------+------------+-------------+--------+
          |            |             |
  +-------v--+ +------v---+ +------v--------+
  |Prometheus | | Loki     | | Jaeger/Tempo  |
  |(metrics)  | | (logs)   | | (traces)      |
  +-----------+ +----------+ +--------------+

Dashboard best practices:
  Top row:    Golden signals (latency, traffic, errors)
  Second row: SLO burn rate, error budget remaining
  Third row:  Resource saturation (CPU, memory, disk)
  Bottom:     Detailed breakdowns (by endpoint, by pod)

  USE method dashboards for infrastructure
  RED method dashboards for services
```

---

### Quick Recall

**If you remember only 3 things:**

1. Grafana = visualization layer connecting to many data sources. Not a database itself. Prometheus stores metrics, Grafana displays them.
2. Dashboard design: start with golden signals overview, drill down to details. RED for services, USE for infrastructure.
3. Grafana Explore for ad-hoc investigation (correlating metrics+logs+traces). Dashboards for steady-state monitoring.

**Interview one-liner:**
"Grafana provides unified visualization across Prometheus (metrics), Loki (logs), and Tempo (traces) - I design dashboards following RED/USE patterns, use Explore for ad-hoc investigation with metric-to-trace correlation, and Grafana alerting with contact points for multi-channel notification."

---

---

# ELK Stack

**TL;DR** - The ELK Stack (Elasticsearch, Logstash, Kibana) is a log management platform: Elasticsearch stores and indexes logs, Logstash/Beats ingest and transform them, and Kibana provides search and visualization - handling terabytes of log data daily.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Logs scattered across 100 servers. SSH + grep to search. Can't correlate events across services. Can't handle volume (millions of events/second). No full-text search. No log retention management.

---

### Textbook Definition

The ELK Stack is a collection of three open-source products: **Elasticsearch** (distributed search and analytics engine), **Logstash** (data processing pipeline for ingestion), and **Kibana** (visualization and exploration UI) - together providing centralized log management at scale, often supplemented by Beats (lightweight shippers) and called the Elastic Stack.

---

### How It Works

```
ELK Architecture:
  Applications -> Filebeat (lightweight shipper)
    -> Logstash (parse, transform, enrich)
      -> Elasticsearch (index, store, search)
        -> Kibana (visualize, explore, alert)

  Modern variant:
  Apps -> Fluent Bit -> Elasticsearch -> Kibana
  (or)
  Apps -> Vector -> Elasticsearch -> Kibana

Elasticsearch concepts:
  Index:    Collection of documents (like a DB table)
  Document: Single log entry (JSON)
  Shard:    Partition of an index (distributed)
  Replica:  Copy of a shard (redundancy)

Index lifecycle management (ILM):
  Hot:    Active writes + frequent search (SSD)
  Warm:   Read-only, less frequent search (HDD)
  Cold:   Rarely searched, compressed
  Delete: Remove after retention period

  hot (7 days) -> warm (30 days) -> cold (90 days)
    -> delete (after 365 days)
```

---

### Quick Recall

**If you remember only 3 things:**

1. Elasticsearch = distributed search engine (stores + indexes). Logstash = ingestion pipeline. Kibana = UI. Beats/Fluentbit = lightweight shippers.
2. Index Lifecycle Management (ILM) is critical for cost: hot/warm/cold/delete tiers with automatic rollover
3. Alternative: Grafana Loki (simpler, cheaper, only indexes labels not full text). Choose ELK for full-text search needs, Loki for label-based search.

**Interview one-liner:**
"ELK provides full-text log search at scale - I use Filebeat for collection, Logstash for parsing/enrichment, Elasticsearch with ILM policies (hot/warm/cold tiers) for cost-effective retention, and Kibana for visualization - choosing Loki as a lighter alternative when label-based search suffices."

---

---

# OpenTelemetry

**TL;DR** - OpenTelemetry (OTel) is the vendor-neutral observability framework that provides a single set of APIs, SDKs, and tools to instrument applications for metrics, logs, and traces - replacing vendor-specific agents with one standard.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Prometheus client for metrics. Jaeger SDK for traces. Fluentbit for logs. Each with different configuration, context propagation, and vendor lock-in. Switch from Datadog to New Relic? Re-instrument everything.

**THE INVENTION MOMENT:**
"This is exactly why OpenTelemetry was created - one standard for all observability signals."

---

### Textbook Definition

OpenTelemetry is a CNCF project providing a vendor-agnostic, standard set of APIs, SDKs, and tools for observability. It supports metrics, logs, and traces with automatic and manual instrumentation, context propagation, and export to any backend (Prometheus, Jaeger, Datadog, etc.).

---

### How It Works

```
OpenTelemetry architecture:
  Application (instrumented with OTel SDK)
    |
    | (OTLP protocol)
    v
  OTel Collector (receive, process, export)
    |
    +---> Prometheus (metrics)
    +---> Jaeger/Tempo (traces)
    +---> Loki (logs)
    +---> Datadog/New Relic (vendor)

Collector pipeline:
  Receivers -> Processors -> Exporters
  (OTLP,       (batch,       (Prometheus,
   Kafka,       filter,       Jaeger,
   Prometheus)  transform)    OTLP, S3)

Instrumentation types:
  Auto-instrumentation:
    Java agent, Python auto-instrumentor
    Zero code changes - attaches via agent
    Covers: HTTP clients, DB drivers, frameworks

  Manual instrumentation:
    tracer.startSpan("process-order")
    span.setAttribute("order.id", orderId)
    Add custom spans and attributes for business logic
```

```yaml
# OTel Collector config
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 5s
    send_batch_size: 1000
  memory_limiter:
    limit_mib: 512

exporters:
  prometheus:
    endpoint: 0.0.0.0:8889
  otlp/tempo:
    endpoint: tempo:4317

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch, memory_limiter]
      exporters: [otlp/tempo]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus]
```

---

### Quick Recall

**If you remember only 3 things:**

1. OpenTelemetry = ONE SDK for metrics + traces + logs. Vendor-neutral. Export to any backend. No vendor lock-in.
2. Auto-instrumentation (Java agent, Python instrumentor) = observability with zero code changes for common frameworks/libraries
3. OTel Collector is the central hub: receives telemetry (OTLP), processes (batch, filter), exports to backends (Prometheus, Jaeger, vendor)

**Interview one-liner:**
"OpenTelemetry provides vendor-neutral instrumentation for all three observability signals - I use auto-instrumentation (Java agent) for zero-code-change coverage, manual spans for business logic, and the OTel Collector as a central pipeline for processing and exporting to our chosen backends without vendor lock-in."

---

---

# Jaeger

**TL;DR** - Jaeger is an open-source distributed tracing platform that stores, searches, and visualizes request traces across microservices - helping identify latency bottlenecks, error sources, and dependency issues in distributed systems.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
You know the request was slow (metrics told you). Logs from 10 services show various timestamps. Which service actually caused the delay? What was the call sequence? Was it sequential or parallel? How did the error propagate?

---

### Textbook Definition

Jaeger is a CNCF graduated distributed tracing platform that implements the OpenTelemetry and OpenTracing standards, providing trace collection, storage (Elasticsearch, Cassandra, Kafka), and a UI for trace search, comparison, dependency graph visualization, and performance analysis.

---

### How It Works

```
Jaeger architecture:
  Services (instrumented with OTel SDK)
    |
    | OTLP / Jaeger native protocol
    v
  Jaeger Collector (receives spans)
    |
    v
  Storage (Elasticsearch, Cassandra, Kafka)
    |
    v
  Jaeger Query (API + UI)
    - Search traces by service, operation, duration
    - Visualize trace timeline (waterfall)
    - Compare traces (before/after deploy)
    - Service dependency graph (DAG)

Trace visualization:
  +-- API Gateway [50ms] ----------------+
  |   +-- Auth Service [20ms] --+        |
  |   +-- Product Svc [350ms] --------+  |
  |   |   +-- DB Query [300ms] --+    |  |
  |   +-- Payment Svc [200ms] ------+ |  |
  |       +-- Stripe API [180ms] -+  | |  |
  +-----------------------------------+--+
  Total: 620ms
  Bottleneck: Product Service DB Query (300ms)

Use cases:
  - Find slow requests and identify bottleneck span
  - Compare traces before/after a deployment
  - Discover service dependencies (auto-generated DAG)
  - Root cause analysis for errors in deep call chains
```

---

### Quick Recall

**If you remember only 3 things:**

1. Jaeger stores and visualizes distributed traces. Shows waterfall timeline of spans across services revealing bottlenecks.
2. Use OpenTelemetry SDK for instrumentation (not Jaeger client directly). Jaeger is the BACKEND/UI, OTel is the instrumentation standard.
3. Alternative: Grafana Tempo (uses object storage = cheaper at scale, integrates with Grafana). Jaeger is proven, Tempo is cost-effective.

**Interview one-liner:**
"Jaeger provides trace storage and visualization with waterfall timelines and dependency graphs - I use it as an OpenTelemetry backend for identifying latency bottlenecks across services, comparing traces pre/post-deployment, and auto-discovering service dependencies through collected trace data."

---

---

# Loki

**TL;DR** - Grafana Loki is a log aggregation system designed for cost efficiency - it indexes only labels (not full text), stores log chunks in object storage (S3), and integrates natively with Grafana for metric-log-trace correlation.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Elasticsearch indexes every word in every log line. At 10TB/day, storage and compute costs are enormous. Most queries filter by time + service + level (labels), not full-text search. You're paying for full-text indexing you rarely use.

---

### Textbook Definition

Grafana Loki is a horizontally-scalable, highly-available log aggregation system inspired by Prometheus. It indexes only metadata labels (service, level, namespace) and stores compressed log content in object storage, enabling cost-effective log management where most queries filter by labels with optional grep-like full-text filtering.

---

### How It Works

```
Loki vs Elasticsearch:
  | Feature        | Elasticsearch | Loki            |
  |----------------|---------------|-----------------|
  | Indexing       | Full text     | Labels only     |
  | Storage        | Hot/warm SSDs | Object storage  |
  | Cost at scale  | Very high     | Low (10-20x less)|
  | Full-text      | Fast          | Slow (grep-like)|
  | Query language | Lucene/KQL    | LogQL           |
  | Integration    | Kibana        | Grafana         |

Architecture:
  Apps -> Promtail/Alloy (agent, adds labels)
    -> Loki (receives, stores, queries)
      -> Object Storage (S3/GCS for chunks)
      -> Grafana (UI, explore, dashboards)

LogQL query examples:
  # All errors from payment service
  {service="payment", level="error"}

  # Filter log content (grep-like)
  {service="api"} |= "timeout"

  # Parse and aggregate
  {service="api"} | json | duration > 5s

  # Rate of errors (metric from logs)
  rate({service="payment", level="error"}[5m])
```

---

### Quick Recall

**If you remember only 3 things:**

1. Loki indexes labels only (not full text) -> 10-20x cheaper than Elasticsearch at scale. Trade-off: full-text search is slower.
2. Same label model as Prometheus (service, namespace, pod). Query with LogQL (Prometheus-inspired syntax for logs).
3. Best for: Kubernetes environments with Grafana. Label-based filtering covers 90% of use cases. Choose ELK if you need fast full-text search.

**Interview one-liner:**
"Loki provides cost-effective log aggregation by indexing only labels (like Prometheus) and storing chunks in object storage - I use it for Kubernetes environments where 90% of queries are label-based (service, namespace, level), correlating with Prometheus metrics and Tempo traces through Grafana."
