---
id: OBS-041
title: Observability Platform Architecture Design
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★★
depends_on: OBS-001, OBS-006, OBS-008, OBS-015, OBS-027, OBS-039
used_by: OBS-044, OBS-045
related: OBS-046, OBS-047, OBS-038
tags:
  - observability
  - reliability
  - devops
  - sre
  - advanced
  - architecture
  - deep-dive
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Mastery"
nav_order: 41
permalink: /technical-mastery/obs/observability-platform-architecture-design/
---

⚡ TL;DR - An observability platform architecture is the
full-stack design of how metrics, traces, and logs flow
from thousands of services through collection, routing,
processing, and storage to queryable dashboards - with
explicit decisions on HA, retention, cost, and the
collection/query separation that makes it scale.

| #041            | Category: Observability & SRE                                                                                           | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | What Is Observability, Prometheus, Distributed Tracing, OpenTelemetry, Log Aggregation at Scale, Observability at Scale |                 |
| **Used by:**    | Platform Observability Engineering, Observability System Design Internals                                               |                 |
| **Related:**    | Time-Series Database Design, Distributed Tracing System Architecture, Capacity Planning with Metrics                    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
100 development teams each run their own observability
stack: some use Datadog, some use home-built dashboards,
some use CloudWatch, several use nothing. During a P1
incident involving 8 services, the incident commander
opens 6 different dashboards in different systems. No
common trace_id correlation standard. No cross-service
latency view. The SRE team cannot find the root cause
across 8 heterogeneous systems. MTTR is 4 hours. Post-
incident: 8 different postmortem formats, no consolidated
learning. Cost analysis: 100 teams with separate tools
are paying 3x what a unified platform would cost.

**THE BREAKING POINT:**
Ad hoc, per-team observability stacks are not an
engineering choice - they are the absence of a choice.
They produce cost inefficiency (duplicate tooling budgets),
operational fragmentation (no cross-service visibility),
and reliability risk (dark services with no observability
at all). The platform architecture decision is not just
about tools - it is about creating an organizational
observability contract: every service must be observable,
and "observable" must have a consistent definition.

**THE INVENTION MOMENT:**
The observability platform architecture is the answer:
a shared infrastructure that every service in the
organization integrates with through a standard SDK
(OpenTelemetry), routes data through a standard pipeline,
and stores in a shared queryable backend. The platform
team maintains the infrastructure; development teams
produce the signals.

**EVOLUTION:**
Early observability platforms were vendor-specific (Splunk
for logs, Nagios for metrics, Zipkin for traces - all
separate). The movement toward unified platforms started
with Grafana's expansion from metrics to logs to traces
(G.L.A.S.S. - Grafana, Loki, Alertmanager, Prometheus,
Tempo). OpenTelemetry (2019) provided the vendor-neutral
collection SDK that made platform independence possible.
Modern platforms support: vendor-managed SaaS (Datadog,
New Relic) for teams that want zero infrastructure,
open-source self-hosted (Grafana stack) for cost control,
and hybrid approaches.

---

### 📘 Textbook Definition

An **observability platform architecture** is the end-to-end
design of a system that: (1) collects observability signals
(metrics, traces, logs) from distributed services via
instrumentation agents (OpenTelemetry SDKs); (2) routes
signals through a pipeline (OTel Collector, Kafka) that
applies filtering, enrichment, sampling, and routing
decisions; (3) stores signals in purpose-built backends
(Prometheus/Thanos for metrics, Tempo/Jaeger for traces,
Loki/Elasticsearch for logs); and (4) provides query
and visualization interfaces (Grafana) for incident
investigation and capacity planning. Platform design must
address: high availability, data retention, multi-cluster
federation, cost management, and the collection/query
separation that enables scale.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An observability platform is the shared infrastructure
that makes every service in your organization debuggable
from a single pane of glass.

**One analogy:**

> An observability platform is like a city's traffic
> management center. Individual cars (services) have
> sensors (OTel SDKs) that report speed and position.
> Data flows through communication infrastructure
> (the pipeline) to a central monitoring room (Grafana).
> Traffic engineers (SREs) see all cars simultaneously
> and can identify bottlenecks, accidents, and flow
> problems without getting in any individual car. Without
> the central management system, each traffic light would
> operate independently and nobody would have a city-wide
> view.

**One insight:**
The critical architectural insight is the separation of
the collection plane from the query plane. The collection
plane (OTel agents) must be lightweight and service-local;
it runs in every pod. The query plane (Grafana, Kibana)
can be centralized and expensive because it only runs
when queried. This separation enables the platform to
collect at massive scale while keeping individual service
overhead minimal.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Collection must be service-local (agent per pod/node)
   to handle service failures without central dependency
2. The collection pipeline must be decoupled from storage
   via a buffer (Kafka) to handle storage slowdowns without
   backpressure into services
3. Each signal type (metrics, traces, logs) requires a
   purpose-built storage backend - no single backend
   efficiently handles all three
4. Query performance requires pre-computed aggregations
   or indexes - raw event queries at scale are too slow

**DERIVED ARCHITECTURE:**
These invariants drive the four-layer architecture:

- **Instrumentation layer**: OTel SDK embedded in each service;
  zero-latency local emission; no network call in hot path
- **Collection layer**: OTel Collector as DaemonSet (per node)
  or sidecar (per pod); collects spans, metrics, logs;
  lightweight processing (filtering, enrichment, sampling)
- **Pipeline layer**: Kafka as durable buffer between
  collection and storage; absorbs backpressure; enables
  replay
- **Storage + query layer**: Prometheus/Thanos (metrics),
  Tempo (traces), Loki (logs), Grafana (unified query UI)

**THE TRADE-OFFS:**

**Gain:** Unified observability contract across all services;
cost efficiency through shared infrastructure; cross-service
correlation; centralized SRE visibility.

**Cost:** Platform engineering overhead; platform team becomes
a dependency of all other teams; vendor lock-in risk when
choosing proprietary backends; configuration management
complexity.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Multi-signal (metrics + traces + logs) pipeline
with purpose-built backends and a unified query layer is
necessary to provide the full observability picture.

**Accidental:** Separate pipelines per team, multiple query
UIs with no correlation support, manual sampling configuration
per service.

---

### 🧪 Thought Experiment

**SETUP:**
Design an observability platform for an organization with
500 services running in 3 Kubernetes clusters across 2
regions. Requirements: sub-30-second metric freshness,
P99 trace retention for 7 days, all logs for 90 days,
error logs for 1 year, $500K/year platform budget.

**DESIGN DECISIONS:**

1. **Collection**: OTel Collector DaemonSet per cluster
   (3 clusters \* 20 nodes each = 60 collector instances)
   - lightweight, per-node overhead only

2. **Metrics storage**: Per-cluster Prometheus (scrape local
   targets, 15-second interval) + Thanos sidecars
   (ship to S3 for long-term) + Thanos Query (cross-cluster
   global view). Cost: 6 Prometheus instances + Thanos
   Query cluster. ~$15K/year.

3. **Trace storage**: OTel Collector tail-based sampling
   (1% normal + 100% errors) → Tempo cluster (S3 backend).
   7-day retention. ~$25K/year storage.

4. **Log storage**: Fluent Bit per node → Kafka → Logstash
   routing → Loki (7-day hot) + S3/Glacier (90-day/1-year).
   ~$40K/year.

5. **Query UI**: Grafana (unified UI for metrics, traces,
   logs via data source plugins). $10K/year.

6. **Remaining budget**: $410K for: platform team salaries
   (2 FTE SREs dedicated to platform), on-call coverage,
   tooling licenses.

**THE INSIGHT:**
The open-source Grafana stack (Prometheus + Tempo + Loki)
achieves the requirements at $90K/year in infrastructure.
The equivalent Datadog contract for 500 services would
be $1.5M-3M/year. The trade-off is 2 FTE platform
engineers vs vendor support.

---

### 🧠 Mental Model / Analogy

> An observability platform architecture is like a city's
> utility grid. Electricity generation (instrumentation)
> happens at each building (service). Transmission lines
> (OTel pipeline) carry power to the grid. The grid
> routes power to different distribution points (storage
> backends) based on type (DC vs AC). End users
> (SRE/developers) connect to outlets (Grafana) and
> receive power without knowing which generator produced
> it. The utility company (platform team) maintains
> the grid, not the individual buildings. Every building
> uses the same standard interface (power outlets = OTel
> SDK standard).

Element mapping:

- "Building" → individual service
- "Power generation" → OTel SDK instrumentation
- "Transmission lines" → OTel Collector + Kafka
- "Grid distribution points" → Prometheus/Tempo/Loki
- "Outlets" → Grafana data sources
- "Utility company" → platform SRE team

Where this analogy breaks down: power grids require physical
infrastructure that cannot be changed quickly; observability
platforms can be reconfigured relatively easily - backends
can be swapped if OpenTelemetry is used as the collection
standard.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
An observability platform is the shared system that collects
information from all your services and displays it in one
place. Instead of every team building their own monitoring,
they all use the same platform.

**Level 2 - How to use it (junior developer):**
Add the OpenTelemetry SDK to your service using the language
SDK. Configure it to export to the local OTel Collector
endpoint (localhost:4317). Your service will automatically
send traces, metrics, and logs to the platform. View them
in Grafana at the platform team's provided URL.

**Level 3 - How it works (mid-level engineer):**
The OTel Collector DaemonSet on each Kubernetes node
receives spans, metrics, and logs from local service pods.
It applies sampling (tail-based for traces), filters debug
logs, adds cluster/region labels, and routes to: Prometheus
remote_write (metrics), Tempo (traces), Loki (logs). Grafana
connects to all three as data sources and provides unified
querying with trace/log/metric correlation via trace_id
and time range.

**Level 4 - Why it was designed this way (senior/staff):**
The DaemonSet vs sidecar collection decision is a resource
trade-off: a DaemonSet runs one collector per node (N nodes
= N collectors); a sidecar runs one per pod (M pods = M
collectors, typically 10-20x more). DaemonSet is more
resource-efficient but requires all pods on a node to share
one collector (a collector failure affects all pods on
that node). Sidecar provides stronger isolation but higher
resource cost. The Kafka buffer between collection and
storage is included because Loki/Elasticsearch write latency
spikes during index rotation - without Kafka, these spikes
would cause backpressure into the Fluent Bit collectors and
potentially block application log writes.

**Level 5 - Mastery (distinguished engineer):**
Platform architecture decisions have decade-long consequences.
The collection standard (OpenTelemetry vs vendor-specific
agents) determines whether the backend is swappable. Choosing
proprietary agents (Datadog Agent) locks all 500 services
into that vendor - switching requires re-instrumenting every
service. Choosing OTel enables backend switching by changing
the Collector export configuration. This is the "build the
platform for exit" principle: design the architecture so
that the most expensive part (the storage + query backend)
can be replaced without touching the services. The OTel
Collector as the routing hub (not the agents) means all
backend decisions are made in one place. Multi-cluster
federation (Thanos/Cortex for metrics, Grafana datasource
federation for traces and logs) is the scaling architecture
that enables cross-cluster/cross-region querying without
each backend having a global deployment footprint.

---

### ⚙️ How It Works (Mechanism)

**REFERENCE PLATFORM ARCHITECTURE:**

```
┌────────────────────────────────────────────────────────┐
│         OBSERVABILITY PLATFORM REFERENCE ARCH          │
├────────────────────────────────────────────────────────┤
│                                                        │
│ INSTRUMENTATION LAYER (in-service)                    │
│   OTel SDK (Java/Python/Go) → local OTel Collector   │
│   Emits: spans, metrics, logs via OTLP gRPC          │
│                                                        │
│ COLLECTION LAYER (per Kubernetes node - DaemonSet)    │
│   OTel Collector receives from local pods            │
│   Fluent Bit tails container stdout                  │
│   Processors: tail sampling, enrichment, filtering   │
│                                                        │
│ PIPELINE LAYER                                        │
│   Kafka (durable buffer, absorbs backpressure)       │
│   Consumers: Prometheus remote_write, Tempo, Loki    │
│                                                        │
│ STORAGE LAYER (per cluster + global)                  │
│   Metrics: Prometheus (local) + Thanos (global)      │
│   Traces: Grafana Tempo (S3 backend)                 │
│   Logs: Grafana Loki (S3 backend) + Elasticsearch   │
│                                                        │
│ QUERY + VISUALIZATION LAYER                           │
│   Grafana (unified UI)                               │
│   Data sources: Prometheus, Loki, Tempo              │
│   Correlation: trace_id links metrics/traces/logs    │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**OPENTELEMETRY COLLECTOR PIPELINE:**

```yaml
# otel-collector-config.yaml (DaemonSet config)
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  # Add Kubernetes metadata to all telemetry
  k8sattributes:
    extract:
      metadata: [k8s.pod.name, k8s.namespace.name,
          k8s.deployment.name]

  # Tail-based trace sampling
  tail_sampling:
    decision_wait: 30s
    policies:
      - name: keep-errors
        type: status_code
        status_code:
          status_codes: [ERROR]
      - name: probabilistic
        type: probabilistic
        probabilistic:
          sampling_percentage: 2

  # Batch for efficiency
  batch:
    send_batch_size: 1000
    timeout: 5s

exporters:
  prometheusremotewrite:
    endpoint: "http://prometheus:9090/api/v1/write"
  otlp/tempo:
    endpoint: "http://tempo:4317"
  loki:
    endpoint: "http://loki:3100/loki/api/v1/push"

service:
  pipelines:
    metrics:
      receivers: [otlp]
      processors: [k8sattributes, batch]
      exporters: [prometheusremotewrite]
    traces:
      receivers: [otlp]
      processors: [k8sattributes, tail_sampling, batch]
      exporters: [otlp/tempo]
    logs:
      receivers: [otlp]
      processors: [k8sattributes, batch]
      exporters: [loki]
```

**MULTI-CLUSTER FEDERATION:**

```
Region 1                    Region 2
  Prometheus-US-EAST          Prometheus-EU-WEST
        │                           │
        └────────┬──────────────────┘
                 │
           Thanos Query
           (global metrics view)
                 │
              Grafana
        (cross-region dashboard)

Same pattern for Tempo (traces) and Loki (logs):
  Grafana supports multiple data sources of the
  same type - point to US Tempo + EU Tempo, query
  both, and Grafana merges results in the UI.
```

---

### 🔄 The Complete Picture - End-to-End Flow

**INCIDENT INVESTIGATION FLOW ON THE PLATFORM:**

```
Alert fires: payment-api error rate > 1% for 5min
   │
   ↓
SRE opens Grafana alert dashboard
  Click alert → linked Prometheus metric query
  View error rate timeseries: spike at 14:23
   │
   ↓
Click trace_id exemplar at 14:23 →
  Opens Grafana Tempo trace view
  Full distributed trace: frontend → API → DB
  Slow span: DB query taking 3.2s (N+1 detected)
   │
   ↓
Click "View Logs" for the slow span trace_id →
  Opens Grafana Loki log view filtered by trace_id
  Log line: "SELECT * FROM orders WHERE..."
  (ORM generated N+1 query - 1,000 separate queries)
   │
   ↓
Root cause identified in 8 minutes from alert fire
  (without platform: 4-hour investigation across
   5 separate systems)
```

**WHAT CHANGES AT 10X SCALE:**
At 5,000 services, the OTel Collector DaemonSet itself
becomes a bottleneck if it runs heavy processing (tail-based
sampling requires buffering). The architecture evolves:
lightweight OTel Collectors on each node (minimal processing)
→ dedicated tail-sampling tier (horizontal cluster of
sampling servers) → storage backends. This "processing
tier" can scale independently of the collection tier.

---

### 💻 Code Example

**Example 1 - BAD: vendor agent instrumentation**

```java
// BAD: Datadog-specific instrumentation
// Every service is now locked into Datadog
import com.datadoghq.trace.Tracer;
import com.datadoghq.trace.TracerFactory;

// This Datadog-specific API in 500 services means:
// - Switching backends requires re-instrumenting 500 services
// - Vendor negotiation leverage = zero
// - License price increase = mandatory payment
```

**Example 2 - GOOD: OTel SDK (vendor-neutral)**

```java
// GOOD: OpenTelemetry - works with any backend
import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.api.trace.Span;

// OTel SDK is completely vendor-neutral
// Backend (Jaeger, Tempo, Datadog) is configured
// in the Collector, not in the application code

OpenTelemetry otel = OpenTelemetrySdk.builder()
    .setTracerProvider(
        SdkTracerProvider.builder()
            .addSpanProcessor(
                BatchSpanProcessor.builder(
                    OtlpGrpcSpanExporter.builder()
                        // Export to local Collector
                        // Collector handles routing
                        .setEndpoint("http://localhost:4317")
                        .build()
                ).build()
            ).build()
    ).build();

Tracer tracer = otel.getTracer("payment-service");

// Application code - completely vendor-neutral
Span span = tracer.spanBuilder("processPayment")
    .startSpan();
try (var scope = span.makeCurrent()) {
    span.setAttribute("payment.amount", amount);
    span.setAttribute("payment.currency", currency);
    // ... business logic
} finally {
    span.end();
}
```

**Example 3 - Grafana trace-to-log correlation**

```yaml
# grafana-datasource.yaml
# Link Tempo traces to Loki logs via trace_id
apiVersion: 1
datasources:
  - name: Tempo
    type: tempo
    url: http://tempo:3200
    jsonData:
      tracesToLogsV2:
        datasourceUid: loki
        # Link field: trace_id in Tempo spans
        # maps to traceID label in Loki logs
        filterByTraceID: true
        customQuery: true
        query: >
          {service_name="${__span.tags.service.name}"}
          |= "${__span.traceId}"

  - name: Loki
    type: loki
    url: http://loki:3100
    uid: loki
```

**How to test / verify correctness:**
Run a synthetic transaction through the full stack.
Verify the trace appears in Tempo within 60 seconds.
Verify metric counters for the synthetic transaction
appear in Prometheus. Verify log lines appear in Loki.
Click the trace_id exemplar in Grafana and verify it
links to the correct Loki log lines. This end-to-end
smoke test validates all signal types and the correlation
links.

---

### ⚖️ Comparison Table

| Platform Approach       | Cost            | Engineering Effort   | Vendor Lock-in | Scale           |
| ----------------------- | --------------- | -------------------- | -------------- | --------------- |
| **Grafana stack (OSS)** | Low ($)         | High (platform team) | Low (OTel)     | Very high       |
| Datadog (SaaS)          | Very high ($$$) | Low (no infra)       | High           | Very high       |
| AWS CloudWatch          | Medium          | Medium (AWS-native)  | High           | High (AWS only) |
| New Relic (SaaS)        | High ($$)       | Low                  | High           | High            |
| Hybrid (OSS + SaaS)     | Medium          | Medium               | Medium         | High            |

**How to choose:**
Choose SaaS (Datadog/New Relic) when: engineering bandwidth
is scarce, the team size is <50 engineers, and platform
cost is not a primary concern. Choose open-source Grafana
stack when: cost optimization is important, the team has
dedicated platform engineering capacity (2+ FTE), and
long-term vendor independence matters. Use OTel as the
collection standard regardless of backend choice - it
keeps the backend decision reversible.

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                                                       |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| More data = better observability             | More data increases cost and noise; structured, purposeful signals with trace correlation produce better incident investigation than data volume              |
| One backend for all signals                  | Metrics (time-series), traces (DAG traversal), logs (full-text search) have fundamentally different access patterns; no single backend optimizes all three    |
| SaaS platforms eliminate all platform work   | SaaS platforms still require: instrumentation standards, sampling policy, cardinality limits, cost governance - they just eliminate infrastructure management |
| OpenTelemetry is only for traces             | OTel covers all three pillars: metrics, traces, and logs - it is the universal collection SDK                                                                 |
| Platform architecture is a one-time decision | Observability platforms evolve as systems scale; the architecture must be designed with migration paths in mind                                               |

---

### 🚨 Failure Modes & Diagnosis

**OTel Collector DaemonSet Failure Cascades**

**Symptom:**
All metrics, traces, and logs from services on one Kubernetes
node stop appearing in Grafana. The services themselves are
healthy (user traffic is being served). Approximately 1/20
of the observability data is missing.

**Root Cause:**
The OTel Collector DaemonSet pod on one Kubernetes node
was OOMKilled due to a memory configuration misconfiguration.
All services on that node are sending telemetry to the local
Collector, which is now dead. Services are configured to
drop telemetry when the Collector endpoint is unavailable
(non-blocking mode) rather than buffering for retry.

**Diagnostic Commands:**

```bash
# Check DaemonSet pod status
kubectl get pods -n observability -l app=otel-collector

# Find OOMKilled collector pods
kubectl describe pod -n observability otel-collector-<node> | \
  grep -A5 "OOMKilled"

# Check which node is missing data
# In Prometheus/Grafana: find node with no
# up{job="otel-collector"} metric
```

**Fix:**

```yaml
# otel-collector DaemonSet resource limits
resources:
  requests:
    memory: 256Mi
    cpu: 100m
  limits:
    memory: 1Gi # prevent OOMKill
    cpu: 500m
# Also configure retry on application SDK side:
# exporter.retry_on_failure.enabled: true
```

---

**Storage Backend Single Point of Failure**

**Symptom:**
All Grafana dashboards show "No data" during an incident.
Engineers cannot investigate. The observability platform
itself is down during an incident. Prometheus pod is
in CrashLoopBackOff.

**Root Cause:**
Prometheus uses a single persistent volume (PVC). The
underlying storage node had a disk failure. Prometheus
is trying to restart but the PVC is unavailable.
No HA was configured.

**Fix:**

```yaml
# Prometheus HA with Thanos sidecar
# Run 2 Prometheus replicas with Thanos deduplication
# Store data in S3 via Thanos sidecar (durable, HA)
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
spec:
  replicas: 2 # HA replicas
  thanos:
    baseImage: quay.io/thanos/thanos
    objectStorageConfig:
      name: thanos-objstore-config
      key: objstore.yml # S3 bucket config
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `What Is Observability` - the three-pillar model this
  platform implements
- `Prometheus - Metrics Collection` - the metrics backend
- `Distributed Tracing Fundamentals` - trace collection
- `OpenTelemetry - The Standard` - the collection SDK
- `Log Aggregation at Scale` - the log pipeline
- `Observability at Scale` - the sampling/aggregation
  strategies this architecture implements

**Builds On This (learn these next):**

- `Platform Observability Engineering` - the organizational
  practice of running this architecture
- `Observability System Design Internals` - the internal
  design of each platform component

**Alternatives / Comparisons:**

- `Time-Series Database Design` - the storage layer for
  metrics in the platform
- `Distributed Tracing System Architecture` - the trace
  storage component in detail
- `Capacity Planning with Metrics` - one of the key use
  cases the platform enables

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ End-to-end architecture for collecting,  │
│              │ routing, storing, and querying metrics,  │
│              │ traces, and logs at organization scale   │
├──────────────┼──────────────────────────────────────────┤
│ 4 LAYERS     │ Instrumentation (OTel SDK) → Collection  │
│              │ (OTel Collector) → Pipeline (Kafka) →    │
│              │ Storage + Query (Prometheus/Tempo/Loki/  │
│              │ Grafana)                                 │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ Use OTel as collection standard to keep  │
│              │ backend choice reversible; never lock    │
│              │ application code to vendor-specific agent│
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Organization has 10+ services needing   │
│              │ cross-service observability correlation  │
├──────────────┼──────────────────────────────────────────┤
│ OSS vs SaaS  │ OSS (Grafana stack): low cost, high      │
│              │ platform engineering effort; SaaS        │
│              │ (Datadog): high cost, low platform effort│
├──────────────┼──────────────────────────────────────────┤
│ HA PATTERN   │ Prometheus x2 + Thanos (S3) for metrics;│
│              │ Tempo/Loki with S3 backend; Grafana HA   │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Vendor-specific agents in application    │
│              │ code - prevents backend portability      │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Instrument once (OTel), route anywhere."│
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Platform Engineering → System Design     │
│              │ Internals                                │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Use OpenTelemetry as the instrumentation standard - it
   keeps backend decisions reversible. Vendor-specific agents
   lock 500 services into one vendor contract.
2. Three separate backends for three signal types: Prometheus
   for metrics, Tempo for traces, Loki for logs. No single
   backend optimizes all three access patterns efficiently.
3. OTel Collector as the routing hub - all sampling decisions,
   enrichment, and backend routing happen here, not in
   the application code. This is the point of maximum leverage.

**Interview one-liner:**
"An observability platform architecture has four layers:
instrumentation (OTel SDK in each service), collection (OTel
Collector DaemonSet on each node), pipeline (Kafka buffer
for backpressure), and storage+query (Prometheus for metrics,
Tempo for traces, Loki for logs, Grafana as the unified
query layer). The critical design principle is using
OpenTelemetry as the collection standard so the backend is
swappable - all backend decisions live in the Collector
config, not in 500 services' application code."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
The adapter pattern at the system boundary is the most
powerful architectural tool for avoiding vendor lock-in.
OpenTelemetry is the adapter between instrumented services
(the producers) and observability backends (the consumers).
The adapter contains all the vendor-specific logic;
the producer and consumer are independent. This principle
applies to any system where the producer must be decoupled
from the consumer's implementation details.

**Where else this pattern applies:**

- **Database driver abstraction** - JDBC/JPA abstract
  application code from PostgreSQL/MySQL specifics;
  switching databases requires changing the driver config,
  not the application code
- **Message queue abstraction** - Spring's JMS template
  abstracts application code from ActiveMQ/RabbitMQ;
  the adapter pattern is the same as OTel Collector
- **Payment gateway abstraction** - Stripe/Braintree/PayPal
  adapters protect application code from payment vendor
  changes

---

### 💡 The Surprising Truth

The most expensive mistake in observability platform
architecture is not the choice of backend - it is the
choice of instrumentation SDK. Once 500 services are
instrumented with Datadog's proprietary agents (dd-trace),
the instrumentation cost to switch to any other backend
is 500 services \* average 2-3 engineering days each =
1,000-1,500 engineer-days of migration work. At $500/day
fully-loaded cost per engineer, this is a $500,000-
$750,000 hidden cost of the original instrumentation
decision. OpenTelemetry eliminates this cost entirely:
migrating the Collector export configuration takes 1
engineer-day. This is why "instrument with OTel, choose
your backend later" is the correct architectural guidance
regardless of which backend you choose today.

> Entry stub. Generate full content using Master Prompt v3.0.
