---
id: OBS-052
title: "OpenTelemetry: Collector Pipeline and SDK Deep Dive"
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★☆
depends_on: OBS-001, OBS-017, OBS-006, OBS-008, OBS-015, OBS-044, OBS-041
used_by: OBS-047
related: OBS-039, OBS-045, OBS-053
tags:
  - observability
  - reliability
  - devops
  - sre
  - intermediate
  - operational
  - opentelemetry
  - production
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 52
permalink: /observability-sre/opentelemetry-collector-pipeline/
---

# OBS-052 - OpenTelemetry: Collector Pipeline and SDK Deep Dive

⚡ TL;DR - The OTel Collector is a language-agnostic telemetry
routing layer: it receives signals via OTLP from application
SDKs, enriches them with environment metadata, applies
cardinality and sampling controls, and fans out to multiple
backends - decoupling instrumentation code from backend choices.

> **See also:** OBS-017 (OpenTelemetry - The Standard) for
> the OTel API/SDK concepts and W3C trace propagation standard.
> This entry focuses on the Collector architecture,
> SDK configuration, and production tuning.

| #052 | Category: Observability & SRE | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | What Is Observability, OpenTelemetry - The Standard, Prometheus, Distributed Tracing, Grafana, Platform Observability Engineering, Observability Platform Architecture | |
| **Used by:** | Distributed Tracing System Architecture | |
| **Related:** | Observability at Scale, Observability System Design Internals, Service Level Objectives Deep Dive | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A Java service uses the Datadog SDK. A Node.js service
uses the New Relic SDK. A Python service uses a custom
Prometheus client. When the organization decides to migrate
from Datadog to Grafana Cloud, all three services need
SDK changes simultaneously. The Java team's sprint is
blocked for 2 weeks on instrumentation migration. The
Python service developer has left - no one knows how
the custom client works. The migration takes 4 months
and costs more than the annual Datadog bill.

**THE INVENTION MOMENT:**
The OTel Collector solves vendor lock-in at the collection
layer. Application code writes to the OTel SDK (language-
agnostic API). The SDK sends OTLP to a local OTel Collector
sidecar. The Collector handles routing to whichever backend
is currently configured. Switching from Datadog to Grafana
Cloud requires a Collector config change, not an SDK change.
Application code is never touched.

**EVOLUTION:**
OTel Collector started as a single binary. It evolved
into two distributions: the **Core Collector** (minimal,
for building custom distributions) and the **Contrib
Collector** (includes all community receivers, processors,
exporters). The Collector Builder tool (`ocb`) enables
organizations to build custom Collector binaries with
exactly the components they need - reducing binary size
and attack surface.

---

### 📘 Textbook Definition

The **OTel Collector** is a language-agnostic telemetry
processing pipeline that receives telemetry signals (metrics,
logs, traces) from multiple sources via configurable
receivers (OTLP, Prometheus, Jaeger, Zipkin, Kafka, etc.),
processes them through a chain of processors (enrichment,
filtering, sampling, batching, rate-limiting), and exports
them to one or more backends via configurable exporters
(Prometheus remote write, OTLP, Jaeger, Loki, Kafka, etc.).
It is the standard middleware layer between application
instrumentation and observability backends, enabling
vendor-agnostic instrumentation and centralized telemetry
policy enforcement.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The OTel Collector is a telemetry router: your code sends
to it once, and it sends to every backend you need, now
or in the future - without touching your application code.

**One analogy:**
> The OTel Collector is like an email server with flexible
> routing rules. Your email client (OTel SDK) sends mail
> to one address (the Collector). The mail server applies
> rules: add the sender's organization tag (k8s enrichment
> processor), filter spam (drop debug metrics), forward to
> multiple mailboxes (export to Prometheus AND Datadog
> simultaneously), and archive some (long-term S3 export).
> You never need to change the email client when the mail
> routing rules change. The client just sends to the server.

---

### 🔩 First Principles Explanation

**COLLECTOR PIPELINE ARCHITECTURE:**

```
receivers → processors (chain) → exporters
    ↑                                 ↓
[OTLP gRPC/HTTP]           [Prometheus remote write]
[Prometheus scrape]         [OTLP to Tempo]
[Jaeger]                    [Loki HTTP]
[Zipkin]                    [Kafka]
[Kafka]                     [Datadog]
[File log]                  [AWS CloudWatch]

Multiple independent pipelines can run in one Collector:
  pipeline "metrics": {receivers: [otlp, prometheus],
                       processors: [batch, k8s_attrs],
                       exporters: [prometheusremotewrite]}
  pipeline "traces":  {receivers: [otlp],
                       processors: [batch, tail_sampling],
                       exporters: [otlp/tempo]}
  pipeline "logs":    {receivers: [otlp, filelog],
                       processors: [batch],
                       exporters: [loki]}
```

**KEY PROCESSORS:**

```
1. batch processor:
   Accumulates data points and sends in bulk.
   Reduces network connections: 1000 spans/s sent as
   50 batches/s instead of 1000 individual requests.
   Config: send_batch_size=8192, timeout=200ms

2. k8sattributes processor:
   Enriches telemetry with Kubernetes metadata.
   Reads from k8s API: pod name, namespace, deployment,
   node, labels, annotations.
   Enables: filtering by namespace, alerting by deployment.

3. memory_limiter processor:
   Prevents the Collector from consuming unbounded RAM
   during traffic spikes.
   Config: limit_mib=400, spike_limit_mib=100
   When limit reached: drops telemetry (configurable)
   MUST be first processor in the chain.

4. filter processor:
   Drops telemetry matching conditions.
   Use case: drop debug metrics in production,
             drop metrics from non-production namespaces.

5. tail_sampling processor:
   Makes sampling decisions after seeing all spans in a trace.
   Config: buffer traces for 10-30s, apply rules:
     - keep all error traces
     - keep all traces > 1s duration
     - sample 1% of normal traces

6. resource processor:
   Adds or modifies resource attributes:
   service.environment = "production"
   service.version = ${SERVICE_VERSION}
```

**THE TRADE-OFFS:**
**Gain:** Vendor-agnostic instrumentation; centralized
telemetry policy (one place to change sampling rates,
cardinality rules, backend routing); fan-out to multiple
backends simultaneously; enrichment without SDK changes.
**Cost:** Additional infrastructure component to operate;
Collector memory/CPU overhead (~50-200MB RAM per instance);
Collector failure = telemetry loss (mitigated by local
buffering); configuration complexity for advanced pipelines.

---

### 🧪 Thought Experiment

**SCENARIO: Zero-downtime backend migration**

Your organization runs 200 Java services all using the
OTel Java agent pointing to a Collector fleet. You need
to migrate from Prometheus remote write to VictoriaMetrics
(drop-in replacement with better performance at scale).

**NAIVE APPROACH (wrong):**
Change all 200 services to point to VictoriaMetrics.
Requires 200 deployments, coordination across 30 teams,
2-week migration window.

**COLLECTOR APPROACH:**
1. Add VictoriaMetrics exporter to Collector config alongside
   existing Prometheus remote write exporter:
```yaml
exporters:
  prometheusremotewrite/old:
    endpoint: "http://prometheus:9090/api/v1/write"
  prometheusremotewrite/victoriametrics:
    endpoint: "http://victoriametrics:8428/api/v1/write"
pipelines:
  metrics:
    exporters: [prometheusremotewrite/old,
                prometheusremotewrite/victoriametrics]
```
2. Roll out new Collector config (zero application changes)
3. Validate VictoriaMetrics has correct data (2 weeks)
4. Remove the old Prometheus exporter from Collector config
5. Migration complete with zero application deployments

The Collector's fan-out capability enables dual-write
migrations with zero application changes.

---

### 🧠 Mental Model / Analogy

> The OTel SDK + Collector relationship is like a factory
> assembly line and shipping department. The assembly line
> (SDK) manufactures telemetry data according to standard
> dimensions (OTel semantic conventions). The shipping
> department (Collector) is separate from manufacturing:
> it receives goods, labels them with additional shipping
> metadata (k8s attributes), inspects for quality issues
> (filter processor), groups into efficient shipments
> (batch processor), and ships to multiple destinations
> simultaneously (fan-out exporters). The assembly line
> workers never need to know where the goods are being
> shipped or how. They just produce to the standard and
> hand off to shipping.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
The OTel Collector is a program that receives monitoring
data from your services and forwards it to your monitoring
tools (Grafana, Datadog, etc.). Your services only talk
to the Collector; the Collector talks to the backends.
This means switching backends doesn't require changing
service code.

**Level 2 - How to use it (junior developer):**
Configure your OTel SDK to point to the local Collector:
```
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
```
The Collector is typically deployed as a DaemonSet (one
per node) or sidecar (one per pod). The platform team
manages the Collector config. Your service just sends
OTLP and the Collector handles routing.

**Level 3 - How it works (mid-level engineer):**
The Collector has three pipeline stages: receivers (accept
telemetry from sources), processors (transform/enrich/filter),
exporters (forward to backends). Processors run in a chain:
memory_limiter → k8sattributes → batch → filter → export.
The memory_limiter must be first to prevent OOM. The batch
processor must be last before export to reduce network
overhead. Configure the k8sattributes processor with
ServiceAccount permissions to read pod metadata from the
k8s API.

**Level 4 - Why it was designed this way (senior/staff):**
The Collector's pipeline model (receivers → processors → exporters)
was designed to be composable: each component is independently
configurable and the pipeline can be assembled from any
combination. This mirrors the Unix philosophy: small,
composable tools chained together. The fan-out model
(one receiver feeding multiple exporters) enables blue/green
migrations of backend systems without affecting application
instrumentation. The Collector also centralizes telemetry
policy: instead of each SDK needing configuration for
sampling rates, cardinality limits, and routing, these
policies live in the Collector config which is managed
by the platform team. This is the organizational benefit:
separation of instrumentation (app teams) from telemetry
policy (platform team).

**Level 5 - Mastery (distinguished engineer):**
The Collector's memory and CPU characteristics under load
are the primary operational concern at platform scale.
The memory_limiter processor is essential but its behavior
under load (drops telemetry when limit is reached) must
be designed around: the question is "when the Collector
is at capacity, which telemetry is dropped and how is that
known?" Answer: configure the Collector to export its
own metrics (self-monitoring), specifically:
`otelcol_processor_dropped_metric_points` and
`otelcol_exporter_queue_size`. Alert when queue size is
sustained > 80% of capacity (approaching backpressure).
Buffer overflow strategy: use a persistent queue
(Collector persists to disk before sending) to survive
backend outages without data loss - at the cost of local
disk usage.

---

### ⚙️ How It Works (Mechanism)

**OTLP PROTOCOL:**

```
OTLP (OpenTelemetry Protocol):
  gRPC transport: best performance, binary encoding
    - Port 4317 (standard)
    - Uses protobuf encoding
    - Bi-directional streaming
  
  HTTP transport: better firewall compatibility
    - Port 4318 (standard)
    - Supports both JSON and protobuf bodies
    - Simpler proxying

  Content types:
    application/x-protobuf (default, binary)
    application/json (debug-friendly, verbose)

  Services:
    ExportTraceServiceRequest (traces)
    ExportMetricsServiceRequest (metrics)
    ExportLogsServiceRequest (logs)
```

**COLLECTOR DEPLOYMENT PATTERNS:**

```
Pattern 1: DaemonSet (one Collector per node)
  Pros: low network overhead (local receiver),
        node-level resource isolation,
        node metadata available without k8s API
  Cons: all pods on node share one Collector
        (noisy neighbor for high-volume services)

Pattern 2: Sidecar (one Collector per pod)
  Pros: full resource isolation per service,
        service-specific Collector configs possible
  Cons: high Collector count (~100 per 100 pods),
        higher total resource overhead

Pattern 3: Standalone deployment (centralized)
  Pros: simpler to operate, fewer instances
  Cons: all traffic traverses the network to the
        Collector (higher latency, bandwidth cost)

Recommended: DaemonSet + standalone gateway
  DaemonSet: initial collection, k8s enrichment
  Standalone: tail-based sampling, fan-out to backends
  SDK → DaemonSet Collector → Gateway Collector → Backends
```

---

### 🔄 The Complete Picture - End-to-End Flow

**FULL PIPELINE: SDK TO BACKEND:**

```
Java service starts
  OTel Java agent attaches (javaagent argument)
  Auto-instruments: HTTP server, HTTP client, JDBC, gRPC
  SDK configured: endpoint=localhost:4317
   │
   ↓
Span created on HTTP request:
  trace_id=abc123, span_id=def456
  service.name=checkout-service
  http.method=POST, http.route=/checkout
  start_time=1700000000.123
   │
   ↓
SDK exports to local Collector (OTLP gRPC, port 4317):
  ExportTraceServiceRequest {
    resource_spans: [{
      resource: {service.name=checkout-service},
      scope_spans: [{spans: [span_abc123_def456]}]
    }]
  }
   │
   ↓
DaemonSet Collector receives on node:
  1. memory_limiter: RAM OK (350MB / 400MB limit)
  2. k8sattributes: query k8s API
     → add k8s.pod.name=checkout-pod-xyz
     → add k8s.namespace.name=production
     → add k8s.deployment.name=checkout-v2.3
  3. batch: accumulate, flush every 200ms or 8192 spans
   │
   ↓ OTLP gRPC
Gateway Collector receives:
  1. tail_sampling:
     buffer trace abc123 for 30s
     all spans arrived? evaluate rules:
       - any error? NO
       - latency > 1s? YES (checkout is 1.8s)
       - Keep: YES (slow trace policy)
  2. Export: OTLP to Tempo (tempo:4317)
             Prometheus remote write (metrics pipeline)
             Loki (logs pipeline)
   │
   ↓
Grafana queries:
  Explore → Tempo → trace ID abc123 → waterfall chart
  Correlate: click "Logs" → Loki query with trace_id
  Correlate: click "Metrics" → Prometheus histogram
```

---

### 💻 Code Example

**Example 1 - BAD: SDK pointing directly to backend (vendor lock-in)**

```yaml
# BAD: Service SDK points directly to Datadog
# Changing backend = changing every service's config
# No central policy enforcement

# kubernetes deployment env vars
env:
  - name: DD_AGENT_HOST
    value: "datadog-agent.monitoring.svc.cluster.local"
  - name: DD_TRACE_AGENT_PORT
    value: "8126"

# When migrating away from Datadog:
# → Must update ALL 200 services
# → Requires coordination across all teams
# → 2-4 week migration window minimum
```

**Example 2 - GOOD: SDK to Collector (vendor-agnostic)**

```yaml
# GOOD: Service SDK points to local OTel Collector
# Changing backend = changing Collector config only
# Application code never changes for backend migrations

# kubernetes deployment env vars (auto-injected by webhook)
env:
  - name: OTEL_EXPORTER_OTLP_ENDPOINT
    value: "http://otel-collector.observability.svc:4317"
  - name: OTEL_SERVICE_NAME
    valueFrom:
      fieldRef:
        fieldPath: metadata.labels['app']
  - name: OTEL_RESOURCE_ATTRIBUTES
    value: >
      deployment.environment=$(ENVIRONMENT),
      service.version=$(APP_VERSION)
```

**Example 3 - Complete Collector config: metrics pipeline**

```yaml
# otel-collector-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
  namespace: observability
data:
  config.yaml: |
    extensions:
      health_check:
        endpoint: "0.0.0.0:13133"
      zpages:
        endpoint: "0.0.0.0:55679"

    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: "0.0.0.0:4317"
          http:
            endpoint: "0.0.0.0:4318"
      prometheus:   # scrape Prometheus-format metrics too
        config:
          scrape_configs:
            - job_name: "otel-collector-self"
              scrape_interval: 30s
              static_configs:
                - targets: ["localhost:8888"]

    processors:
      # MUST be first - prevents OOM under load
      memory_limiter:
        check_interval: 1s
        limit_mib: 400
        spike_limit_mib: 100

      # Enrich with k8s metadata
      k8sattributes:
        auth_type: serviceAccount
        passthrough: false
        extract:
          metadata:
            - k8s.pod.name
            - k8s.namespace.name
            - k8s.deployment.name
            - k8s.node.name
          labels:
            - tag_name: app.version
              key: app.kubernetes.io/version
              from: pod

      # Drop high-cardinality or debug metrics
      filter/metrics:
        metrics:
          metric:
            - >
              name == "jvm.thread.count" and
              attributes["thread.state"] == "blocked"
            - >
              name =~ "debug_.*"

      # Batch for efficient export
      batch:
        send_batch_size: 8192
        timeout: 200ms
        send_batch_max_size: 16384

    exporters:
      prometheusremotewrite:
        endpoint: >
          http://prometheus:9090/api/v1/write
        tls:
          insecure: true
        resource_to_telemetry_conversion:
          enabled: true  # convert resource attrs to labels

      # Dual-write during migration (remove old after validation)
      prometheusremotewrite/victoriametrics:
        endpoint: >
          http://victoriametrics:8428/api/v1/write

      debug:
        verbosity: basic  # only in dev/staging

    service:
      extensions: [health_check, zpages]
      pipelines:
        metrics:
          receivers: [otlp, prometheus]
          processors:
            - memory_limiter
            - k8sattributes
            - filter/metrics
            - batch
          exporters:
            - prometheusremotewrite
            - prometheusremotewrite/victoriametrics

      telemetry:  # Collector self-monitoring
        metrics:
          level: detailed
          address: "0.0.0.0:8888"
        logs:
          level: warn
```

**Example 4 - FAILURE: Collector OOM from missing memory_limiter**

```
Symptom:
  OTel Collector pods are OOM-killed every 2 hours.
  After restart, they take 30 seconds to recover.
  These 30-second gaps appear as holes in all dashboards
  and traces during that window.

Root Cause:
  Collector config has no memory_limiter processor.
  During traffic spike (hourly batch job), span/metric
  volume spikes 10x for 60 seconds.
  Collector buffers all incoming data in memory.
  Memory grows from 200MB to 3GB (batch job data).
  Kubernetes OOM killer terminates the pod.

Fix:
  Add memory_limiter as FIRST processor in all pipelines:
  
  processors:
    memory_limiter:
      check_interval: 1s
      limit_mib: 400        # 80% of container limit (500MB)
      spike_limit_mib: 100  # refuse new data when within
                            # 100MB of limit
  
  When limit is reached:
  - Collector returns "ResourceExhausted" gRPC status
  - SDK receives error and buffers locally (bounded)
  - New data may be dropped at SDK buffer boundary
  - This is preferable to Collector OOM and full data loss
  
  Alert on memory_limiter drops:
    otelcol_processor_dropped_metric_points > 0
    → pages platform team when data is being dropped
```

---

### ⚖️ Comparison Table

| Collection Architecture | Vendor Lock-in | Operational Complexity | Policy Control | Fan-out |
|---|---|---|---|---|
| **OTel Collector** | None | Medium | Centralized | Yes (multi-exporter) |
| Vendor agent (Datadog, NR) | High | Low | Per-vendor | Limited |
| Direct SDK to backend | High | Low (no collector) | None | No |
| Fluentd/Logstash (logs only) | Low | High | Partial | Yes |
| Custom pipeline (Kafka-based) | None | Very high | Full | Yes |

**How to choose:**
Use OTel Collector for all new observability infrastructure.
Use vendor agents during transition from existing vendor
while migrating to OTel. Use direct SDK to backend only
for prototyping where operational simplicity outweighs
flexibility. Use Kafka-based custom pipelines when you
need guaranteed delivery and complex routing not supported
by OTel Collector.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| OTel Collector and OTel SDK are the same thing | SDK = language library in application code (creates spans, meters, logs). Collector = separate process/binary that receives and routes telemetry. They are independent components that work together |
| The Collector adds significant latency | The Collector typically adds 1-5ms of latency per telemetry batch. For tracing, this is negligible. For metrics, it is invisible (scraping intervals are 15-60s). The async export model means the Collector never blocks application request processing |
| Each service needs its own Collector config | The platform team manages one Collector config for all services. Individual services don't need to know about backend routing. The SDK config (OTEL_EXPORTER_OTLP_ENDPOINT) is the only service-specific config needed |
| The Collector must be on the same node as the application | DaemonSet deployment (same node) is the most efficient; standalone deployment (remote) also works with slightly higher network overhead |

---

### 🚨 Failure Modes & Diagnosis

**Telemetry Lost During Backend Outage**

**Symptom:**
Grafana Cloud has a 20-minute outage. During this period,
all metrics and traces from all 200 services are lost.
The Prometheus remote write endpoint was returning errors;
the Collector dropped the data after retry exhaustion.

**Root Cause:**
The Collector's default queue configuration drops data
after N retry failures. The default exporter queue is
in-memory only and is lost on Collector restart.

**Fix:**
Configure persistent queue and retry policy:
```yaml
exporters:
  prometheusremotewrite:
    endpoint: "https://grafana-cloud:443/api/v1/write"
    retry_on_failure:
      enabled: true
      max_elapsed_time: 300s  # retry for 5 minutes
      max_interval: 30s
    sending_queue:
      enabled: true
      queue_size: 10000       # 10K batches in memory
      storage: file_storage   # persist to disk
                              # requires file_storage extension

extensions:
  file_storage:
    directory: /var/lib/otelcol/queue
    timeout: 10s
```

This persists the queue to disk, surviving Collector
restarts. With 300s retry and 10K queue: ~8,000 seconds
of data buffered at 50 batches/s. Grafana Cloud outage
of < 22 minutes is handled with no data loss.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `What Is Observability` - the three pillars the Collector routes
- `OpenTelemetry - The Standard` (OBS-017) - the SDK and
  protocol before the Collector deep dive
- `Prometheus` - primary metrics backend receiving from Collector
- `Distributed Tracing` - trace concepts before Collector trace config
- `Grafana` - the visualization layer over Collector outputs
- `Platform Observability Engineering` - the organizational
  context the Collector is deployed in
- `Observability Platform Architecture Design` - where the
  Collector fits in the full stack

**Builds On This (learn these next):**
- `Distributed Tracing System Architecture` - how traces flow
  through the Collector to Tempo storage

**Alternatives / Comparisons:**
- `Observability at Scale` - the sampling and cardinality
  controls the Collector implements at scale
- `Observability System Design Internals` - the full data
  flow this Collector is part of
- `Service Level Objectives Deep Dive` - the SLO measurement
  that depends on Collector-routed metric data

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Telemetry routing pipeline: receive   │
│               │ (OTLP/Prometheus/Kafka) → process     │
│               │ (enrich/filter/sample/batch) →        │
│               │ export (multi-backend fan-out)        │
├───────────────┼────────────────────────────────────────┤
│ KEY PROCESSORS│ memory_limiter (MUST be first),       │
│               │ k8sattributes, filter, batch,          │
│               │ tail_sampling (for traces)            │
├───────────────┼────────────────────────────────────────┤
│ DEPLOY PATTERN│ DaemonSet (per-node) for base collect  │
│               │ + Standalone gateway for sampling and  │
│               │ fan-out to backends                   │
├───────────────┼────────────────────────────────────────┤
│ MIGRATION     │ Add new backend to exporters list (fan-│
│               │ out), validate data, remove old -     │
│               │ zero application changes required     │
├───────────────┼────────────────────────────────────────┤
│ SELF-MONITOR  │ otelcol_exporter_queue_size > 80%:   │
│               │ backend pressure. Alert platform team. │
│               │ otelcol_processor_dropped_*: data loss│
├───────────────┼────────────────────────────────────────┤
│ BACKPRESSURE  │ memory_limiter returns ResourceExhausted│
│               │ → SDK buffers locally → bounded data  │
│               │ loss preferred over Collector OOM      │
├───────────────┼────────────────────────────────────────┤
│ ONE-LINER     │ "SDK to Collector to backends: the    │
│               │ Collector is the seam between         │
│               │ application code and backend choice." │
├───────────────┼────────────────────────────────────────┤
│ NEXT EXPLORE  │ Distributed Tracing System Architecture│
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. The Collector separates "what to observe" (SDK in app
   code) from "where to send it" (Collector config). This
   enables zero-application-change backend migrations.
2. `memory_limiter` MUST be the first processor in every
   pipeline. Without it, traffic spikes OOM-kill the Collector,
   causing worse data loss than controlled dropping.
3. Monitor the Collector itself: `otelcol_exporter_queue_size`
   (backend pressure) and `otelcol_processor_dropped_*` (data
   loss). A Collector that silently drops data is worse than
   one that fails visibly.

**Interview one-liner:**
"The OTel Collector is a telemetry routing pipeline with
three stages: receivers (OTLP, Prometheus, Kafka), processors
(memory_limiter MUST be first, then k8sattributes enrichment,
filter, batch, tail_sampling for traces), and exporters
(fan-out to Prometheus, Tempo, Loki, Datadog simultaneously).
Key operational concern: memory_limiter prevents OOM under
load spikes. Key architectural value: switching backends
requires only Collector config change - zero application code
changes. Self-monitor with otelcol_exporter_queue_size and
otelcol_processor_dropped_* metrics."
