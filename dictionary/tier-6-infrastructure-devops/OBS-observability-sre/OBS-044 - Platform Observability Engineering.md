---
id: OBS-044
title: Platform Observability Engineering
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★★
depends_on: OBS-001, OBS-006, OBS-008, OBS-015, OBS-017, OBS-027, OBS-039, OBS-041
used_by: OBS-049, OBS-051
related: OBS-037, OBS-040, OBS-043
tags:
  - observability
  - reliability
  - devops
  - sre
  - advanced
  - architecture
  - production
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 44
permalink: /obs/platform-observability-engineering/
---

# OBS-044 - Platform Observability Engineering

⚡ TL;DR - Platform observability engineering treats the
observability stack itself as a product: the platform team
builds and operates the telemetry pipeline, storage, and
tooling so that application teams ship observable services
by default - with zero infrastructure setup, because the
platform handles it automatically.

| #044 | Category: Observability & SRE | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | What Is Observability, Prometheus, Distributed Tracing, Grafana, OpenTelemetry, Log Aggregation at Scale, Observability at Scale, Observability Platform Architecture | |
| **Used by:** | Observability-First Thinking, Reliability Mental Model | |
| **Related:** | Toil Reduction Strategy, SRE Book Core Principles, Observability-Driven Development Strategy | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In a 300-service organization, each team manages its own
observability stack. Team A uses Datadog. Team B uses
Prometheus + Grafana. Team C uses CloudWatch. Team D uses
a custom home-grown solution. When a cross-service incident
occurs, the on-call engineer switches between 4 different
dashboards, each with different query languages, different
alert configurations, and different trace correlation
models. Service A's traces cannot link to Service B's
traces because they use different trace ID formats.
The incident takes 2 hours to diagnose. Post-mortems
across teams cannot be compared because metrics have
different definitions. SLO reports require a manual
spreadsheet because the data is in 4 systems.

**THE BREAKING POINT:**
At 50 services, the fragmentation creates coordination
overhead that slows every cross-service incident. At 300
services, it is operationally impossible to have a
coherent reliability picture. Each team duplicates the
work of configuring, scaling, and operating its own
observability stack. Platform observability engineering
solves this fragmentation.

**THE INVENTION MOMENT:**
Platform observability engineering applies the platform
engineering model to observability: instead of each
application team managing infrastructure, a dedicated
platform team builds and operates the observability
infrastructure as an internal product that all application
teams consume. The platform team owns: the telemetry
collection pipeline (OTel Collector fleet), the metric
storage (Prometheus/Thanos/Cortex), the trace storage
(Tempo/Jaeger), the log storage (Loki/Elasticsearch),
the visualization layer (Grafana), and the alerting
infrastructure (Alertmanager). Application teams instrument
their services and let the platform handle the rest.

**EVOLUTION:**
This model emerged as organizations moved from monolith
to microservices and discovered that per-team observability
management was not scalable. The OpenTelemetry project
was central to enabling this model: OTel provides a
standardized API that applications write to, while the
platform controls where the telemetry is routed.
This clean separation of concerns - application teams
control what to observe, platform teams control how to
collect, store, and query it - is the architectural
foundation of platform observability engineering.

---

### 📘 Textbook Definition

**Platform observability engineering** is the discipline
of designing, building, and operating the organization's
shared observability infrastructure as an internal
product. The platform team owns the full telemetry
pipeline from collection through storage to visualization
and alerting, providing application teams with standardized
SDKs, auto-instrumentation, and self-service tooling that
makes services observable by default. The platform is
responsible for: data reliability, query performance,
cost management, cardinality governance, and providing
the data model that enables cross-service correlation
and organization-wide SLO reporting.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The observability platform team owns the infrastructure
so application teams only need to instrument their code -
the rest is automatic.

**One analogy:**
> Platform observability engineering is like a city's
> electrical grid. Individual buildings (application teams)
> do not build their own power plants. They plug into the
> city grid and consume electricity. The city utility
> (platform team) manages the power plants, distribution
> lines, substations, and metering. The building only
> needs to manage the wiring inside its walls. In the
> same way, application teams instrument their code (the
> wiring), and the observability platform handles
> collection, transmission, storage, and visualization
> (the grid). Without the grid, every building builds its
> own power plant - inefficient, inconsistent, and fragile.

**One insight:**
The critical insight is that observability instrumentation
(in application code) and observability infrastructure
(collection, storage, querying) have different owners.
Conflating the two creates a situation where every team
manages infrastructure they are not specialized for.
Separating them allows application teams to focus on
what to observe and the platform team to focus on how
to observe it at scale.

---

### 🔩 First Principles Explanation

**THE FOUR PLATFORM INVARIANTS:**
1. **Standardization**: all services emit telemetry in a
   common format (OTel) enabling cross-service correlation
   and consistent query semantics
2. **Zero-config default**: a new service joining the
   platform should be observable with zero configuration
   (auto-instrumentation handles the baseline; developers
   add custom instrumentation for business-specific signals)
3. **Reliability of reliability data**: the observability
   platform must have higher reliability than the services
   it monitors - if the observability stack fails during
   an incident, the incident becomes impossible to diagnose
4. **Cost governance**: observability cost scales with
   data volume; the platform must provide cost controls
   (cardinality limits, retention policies, sampling) to
   prevent runaway spend

**DERIVED ARCHITECTURE:**
These invariants drive the platform architecture:
- OTel SDK + OTel Collector as the standard collection
  layer (satisfies standardization)
- Kubernetes DaemonSet or sidecar OTel Collector deployment
  (satisfies zero-config - every pod gets an agent)
- Prometheus HA pairs + Thanos for long-term storage
  (satisfies reliability of reliability data)
- Recording rules for high-cardinality aggregation
  (satisfies cost governance)

**THE TRADE-OFFS:**
**Gain:** Economies of scale in infrastructure operations;
cross-service correlation and organization-wide SLO reporting;
application teams focus on business logic.
**Cost:** Platform team becomes a dependency - its failures
affect all services; standardization sometimes conflicts
with specialized team needs; platform migration is expensive.

---

### 🧪 Thought Experiment

**THE PLATFORM MIGRATION SCENARIO:**
Your organization has 100 services using direct-to-Prometheus
pushgateway for metrics. The platform team proposes migrating
to OTel Collector + Prometheus remote write. The migration
must happen without service downtime and without requiring
100 application teams to change their code simultaneously.

**NAIVE APPROACH (fails):**
Announce a migration date. Tell all teams to switch to OTel
SDK by that date. Result: 40% of teams migrate on time,
30% miss the deadline, 30% never migrate. After the
"migration", you have a hybrid system that requires
supporting both the old and new pipeline indefinitely.

**PLATFORM ENGINEERING APPROACH:**
The platform team deploys OTel Collectors as sidecar
containers in all existing Kubernetes pods using a mutating
webhook - no application code changes required. The OTel
Collector runs in parallel with the existing pushgateway
and forwards the same metrics. Application teams have 3
months to switch their SDK (with platform team support),
during which both pipelines are live. After 3 months,
the platform team removes the pushgateway support.
The migration was transparent to 80% of teams who never
needed to change their code.

**KEY INSIGHT:**
Platform engineering separates the "what" (application
teams instrument their code) from the "how" (platform
decides how to collect and route it). This separation
enables infrastructure migrations without requiring
application team action in most cases.

---

### 🧠 Mental Model / Analogy

> The platform observability team is like the postal
> service. Individual senders (application teams) put
> messages in envelopes (telemetry data) with addresses
> (metric names, trace IDs). The postal service (platform
> team) handles the collection, routing, sorting, and
> delivery - the sender does not need to know how the
> mail sorting centers work or how the delivery trucks
> are routed. The postal service also handles scale:
> when 10x the mail volume arrives, the postal service
> adds sorting capacity - the senders do not need to
> manage the infrastructure. And the postal service sets
> standards: envelopes must have stamps (OTel semantic
> conventions) or they cannot be delivered.

Element mapping:
- "Sender" → application team
- "Envelope format" → OTel semantic conventions
- "Mail sorting center" → OTel Collector pipeline
- "Delivery address" → metric name / trace endpoint
- "Postal infrastructure" → Prometheus/Loki/Tempo cluster
- "Stamps" → required labels/tags for routing

Where this analogy breaks down: mail delivery is one-way;
telemetry delivery requires low-latency feedback (alerting
must be fast), requires query capability (not just storage),
and requires correlation across multiple streams
simultaneously - more complex than postal delivery.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
The platform observability team builds and runs the shared
monitoring tools so every other team can plug in and get
monitoring for free. You don't have to set up your own
Grafana or Prometheus - the platform provides them.

**Level 2 - How to use it (junior developer):**
Your service runs in a Kubernetes cluster with an OTel
Collector sidecar injected automatically. Your code uses
the OTel SDK to emit metrics, logs, and traces. The
platform routes this telemetry to Prometheus, Loki, and
Tempo automatically. Your Grafana dashboard is provisioned
automatically from a service template. You only need to
add business-specific metrics and log fields - the platform
handles the infrastructure layer.

**Level 3 - How it works (mid-level engineer):**
The platform provides: an OTel Collector deployed as a
DaemonSet or sidecar (collects from all pods), a Prometheus
cluster in HA mode with Thanos for long-term storage and
cross-cluster querying, a Loki cluster for log aggregation,
a Tempo cluster for distributed traces, and a Grafana
instance with standard dashboards auto-provisioned per
service. The platform also provides: a cardinality governance
service that blocks labels exceeding the cardinality limit,
a cost allocation dashboard showing telemetry cost per
service, and a standard alert rule library that service
teams can adopt.

**Level 4 - Why it was designed this way (senior/staff):**
The separation between instrumentation API (OTel SDK
in application code) and the collection/storage pipeline
is the critical architectural decision. This separation
means the platform can migrate storage backends (e.g.,
from Elasticsearch to Loki for logs) without requiring
application teams to change their code. The OTel Collector
acts as a vendor-agnostic routing layer: the application
sends to the Collector, and the Collector routes to
whichever backend the platform has selected. This
reduces vendor lock-in significantly and gives the
platform team the freedom to optimize the backend without
application team involvement.

**Level 5 - Mastery (distinguished engineer):**
Platform observability at 1000+ services requires solving
the cardinality explosion problem fundamentally. Each new
service adds N time series per unique label combination.
At 1000 services with 50 metrics each and 100 unique
label combinations per metric, you have 5 million time
series. Prometheus performance degrades above ~10M series
per instance. The solution is a tiered query layer:
Prometheus for recent high-resolution data, Thanos or
Cortex for long-term aggregated data, with recording
rules pre-aggregating the high-cardinality metrics into
low-cardinality aggregates before they reach the long-term
storage. The platform team designs and enforces this
recording rule strategy - application teams cannot see
this complexity; they just send their metrics and query
the results.

---

### ⚙️ How It Works (Mechanism)

**PLATFORM ARCHITECTURE - END TO END:**

```
┌────────────────────────────────────────────────────┐
│         PLATFORM OBSERVABILITY ARCHITECTURE        │
├────────────────────────────────────────────────────┤
│                                                    │
│  Application Pods                                  │
│  ┌──────────────────────────────────────────────┐  │
│  │  App Code + OTel SDK                         │  │
│  │  sidecar: OTel Collector (injected by webhook)│  │
│  └───────────────────┬──────────────────────────┘  │
│                      │ OTLP (gRPC/HTTP)             │
│                      ↓                              │
│  ┌──────────────────────────────────────────────┐  │
│  │  OTel Collector Fleet (DaemonSet)            │  │
│  │  - Receives from all pods on node            │  │
│  │  - Enriches with k8s metadata               │  │
│  │  - Routes to appropriate backends           │  │
│  └──────┬──────────────┬────────────┬───────────┘  │
│         │ Metrics       │ Traces     │ Logs         │
│         ↓              ↓           ↓              │
│  ┌────────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Prometheus │  │  Tempo   │  │   Loki   │       │
│  │   (HA 2x) │  │ (traces) │  │  (logs)  │       │
│  │     +      │  └────┬─────┘  └────┬─────┘       │
│  │   Thanos   │       │             │              │
│  └─────┬──────┘       │             │              │
│        └──────────────┴──────────┬──┘              │
│                                  ↓                 │
│                          ┌───────────────┐         │
│                          │    Grafana    │         │
│                          │ (dashboards, │         │
│                          │  alerting)   │         │
│                          └───────────────┘         │
└────────────────────────────────────────────────────┘
```

**CARDINALITY GOVERNANCE:**

```
┌──────────────────────────────────────────────────────┐
│           CARDINALITY CONTROL MECHANISMS            │
├──────────────┬───────────────────────────────────────┤
│ Mechanism    │ What It Does                          │
├──────────────┼───────────────────────────────────────┤
│ Label limits │ Collector rejects metrics with        │
│              │ cardinality > N unique label values   │
├──────────────┼───────────────────────────────────────┤
│ Recording    │ Pre-aggregate high-cardinality metrics│
│ rules        │ (e.g., per-user → per-cohort)         │
├──────────────┼───────────────────────────────────────┤
│ Cost alerts  │ Alert team when their metrics cost    │
│              │ exceeds budget ($/GB/month)            │
├──────────────┼───────────────────────────────────────┤
│ Drop rules   │ Collector drops debug metrics in prod │
│              │ (only forward metrics with SLO labels)│
└──────────────┴───────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NEW SERVICE ONBOARDING FLOW:**

```
Developer creates new service in k8s
   │
   ↓
Platform mutating webhook detects new pod
  → Injects OTel Collector sidecar automatically
  → No configuration required from developer
   │
   ↓
Service emits generic HTTP metrics via OTel SDK
  (OTel agent auto-instruments HTTP, DB calls)
   │
   ↓
OTel Collector sidecar receives OTLP data
  → Enriches with: cluster, namespace, service labels
  → Routes: metrics → Prometheus remote write
            logs → Loki push endpoint
            traces → Tempo OTLP endpoint
   │
   ↓
Platform CI job detects new service:
  → Provisions Grafana dashboard from service template
  → Creates standard Prometheus alerting rules
    (HIGH burn rate, pod OOM, etc.)
  → Creates PagerDuty service integration
   │
   ↓
Developer opens Grafana, finds their service dashboard
  with HTTP request rate, error rate, and latency
  already populated - zero configuration from developer
   │
   ↓
Developer adds custom business metrics:
  e.g., payment_processor_response{result="declined"}
  These flow through the same pipeline automatically
```

---

### 💻 Code Example

**Example 1 - BAD: per-team observability setup**

```yaml
# BAD: every team has its own Prometheus scrape config
# in their namespace - no standardization, no platform
# team ownership, no cross-service correlation
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: team-payments  # Each team runs their own!
data:
  prometheus.yml: |
    scrape_configs:
      - job_name: 'payment-service'
        static_configs:
          - targets: ['payment-svc:8080']
# Result: 50 services × 50 Prometheus instances
# = 50x operations overhead, no cross-service queries,
# no trace correlation, inconsistent retention policies
```

**Example 2 - GOOD: platform OTel Collector with routing**

```yaml
# GOOD: Platform-owned OTel Collector Config
# Routes all telemetry to platform-managed backends
# Application teams do NOT configure this

apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
  namespace: observability-platform   # Platform team owns
data:
  collector.yaml: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: "0.0.0.0:4317"
          http:
            endpoint: "0.0.0.0:4318"

    processors:
      # Enrich all telemetry with k8s metadata
      k8sattributes:
        auth_type: serviceAccount
        passthrough: false
        extract:
          metadata:
            - k8s.pod.name
            - k8s.namespace.name
            - k8s.deployment.name
            - k8s.node.name
      # Cardinality protection
      filter:
        metrics:
          metric:
            - >
              name == "debug_*" and
              resource.attributes["env"] == "production"

    exporters:
      prometheusremotewrite:
        endpoint: "http://prometheus:9090/api/v1/write"
        tls:
          insecure: false
          cert_file: /certs/client.crt
          key_file: /certs/client.key
      loki:
        endpoint: "http://loki:3100/loki/api/v1/push"
      otlp/tempo:
        endpoint: "http://tempo:4317"

    service:
      pipelines:
        metrics:
          receivers: [otlp]
          processors: [k8sattributes, filter]
          exporters: [prometheusremotewrite]
        logs:
          receivers: [otlp]
          processors: [k8sattributes]
          exporters: [loki]
        traces:
          receivers: [otlp]
          processors: [k8sattributes]
          exporters: [otlp/tempo]
```

**Example 3 - Application side (minimal OTel setup)**

```java
// Application team code - no infra knowledge needed
// Platform provides this in a shared library

@Configuration
public class ObservabilityConfig {

    @Bean
    public MeterRegistry meterRegistry() {
        // SDK configured to emit to localhost:4317
        // (the injected OTel Collector sidecar)
        OtlpGrpcMeterRegistry registry =
            OtlpGrpcMeterRegistry.builder()
                .baseUrl("http://localhost:4317")
                .build();
        return registry;
    }
}

// Application team instruments their business logic
@Service
public class PaymentService {
    private final Counter paymentAttempts;
    private final DistributionSummary paymentLatency;

    public PaymentService(MeterRegistry registry) {
        this.paymentAttempts = Counter
            .builder("payments.attempts")
            .tag("status", "initial")
            .description("Payment processing attempts")
            .register(registry);
        this.paymentLatency = DistributionSummary
            .builder("payments.latency")
            .publishPercentiles(0.50, 0.95, 0.99)
            .register(registry);
    }

    // The rest: OTel auto-instrumentation handles
    // HTTP request metrics, DB call tracing, etc.
}
```

**Example 4 - FAILURE: platform collector goes down**

```
Scenario: OTel Collector DaemonSet has a bug in new
deployment. All pods fail CrashLoopBackOff.

Symptoms:
- All metric scraping stops across all services
- Prometheus shows all targets as "unknown"
- Alertmanager has no data → no alerts fire
- On-call engineers get NO pages during this period

This is the observability reliability problem:
if the observability platform fails, you are blind
exactly when you most need visibility.

Fix: Platform must be deployed with:
  1. Multiple replicas (k8s rolling update, not recreate)
  2. Separate Prometheus scraping the platform itself
     (meta-monitoring / "monitor the monitor")
  3. Alert when OTel Collector drops below expected
     throughput or all targets go unknown
  4. Circuit-breaker in Collector: if cannot reach
     backend, buffer locally (configurable buffer size)
     and alert platform team, while continuing to
     accept from applications (don't lose data at
     collection layer due to backend issues)
```

---

### ⚖️ Comparison Table

| Approach | Setup Cost | Operational Overhead | Cross-Service Correlation | Standardization |
|---|---|---|---|---|
| **Platform observability** | High (initial) | Low (shared) | Full | Enforced |
| Per-team observability | Low (initial) | High (duplicated) | Difficult | None |
| Vendor SaaS (Datadog) | Low | Very low | Vendor-dependent | Vendor-imposed |
| Hybrid (platform + team-owned) | Medium | Medium | Partial | Partial |

**How to choose:**
Use platform observability for organizations with 20+
services or planning to scale. For very small organizations
(< 10 services), per-team or SaaS is simpler. For large
organizations, a managed SaaS (Datadog, New Relic) provides
many of the same benefits as self-hosted platform observability
with much lower initial investment, at higher recurring cost.
The self-hosted platform approach pays off at high scale
(hundreds of services) where SaaS cost becomes prohibitive.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| The platform team is responsible for instrumenting application code | The platform team owns the infrastructure; application teams own their instrumentation. The split is: "what to observe" (app team) vs "how to collect/store" (platform team) |
| Platform observability means one-size-fits-all | The platform sets standards and provides defaults; application teams can customize within those bounds (e.g., custom dashboards, custom alert rules built on platform infrastructure) |
| Auto-instrumentation makes ODD unnecessary | Auto-instrumentation covers generic signals (HTTP, DB); it cannot know business-specific semantics (e.g., payment declined vs payment succeeded is application knowledge) |
| A single OTel Collector handles everything | At scale, the Collector fleet requires capacity planning, sharding by service/namespace, and HA configuration. A single instance is a SPOF |

---

### 🚨 Failure Modes & Diagnosis

**Cardinality Explosion from a Single Service**

**Symptom:**
Prometheus memory usage increases 10x over 48 hours.
Query latency degrades from 200ms to 15 seconds.
Platform team's monitoring shows a single service (payment-v3)
added 2 million new time series.

**Root Cause:**
A developer added a label `request_id` to a business metric.
Every unique request has a unique ID. Over 48 hours, this
generates millions of unique label combinations.

**Diagnostic Query:**
```promql
# Find highest-cardinality metrics
topk(20,
  count by (__name__)({__name__=~".+"})
)
# This will surface payment_service_requests with
# 2M unique label combinations vs next highest at 50K
```

**Fix:**
```yaml
# OTel Collector drop rule: block high-cardinality labels
processors:
  attributes:
    actions:
      - key: request_id      # Never a valid metric label
        action: delete
      - key: user_id         # Also high cardinality
        action: delete
```

**Platform Response:**
Deploy label allow-list enforcement in Collector:
only predefined labels pass through. New labels require
a platform team review (PR to the Collector config).
Alert when any new service exceeds 10K time series.

---

**OTel Collector Memory Leak Under Load**

**Symptom:**
OTel Collector pods on high-traffic nodes OOM-killed
every 6 hours. The k8s restart recovers them in 30 seconds
but causes a 30-second telemetry gap per restart. This
is not visible to application teams but the platform
team's meta-monitoring shows regular gaps.

**Root Cause:**
Collector memory limit was set too low (512Mi) for
the traffic volume. The Collector buffers in memory
when the Prometheus remote write endpoint is slow.
At peak traffic, buffer fills the memory limit and
causes OOM-kill.

**Diagnostic:**
```bash
# Check Collector memory usage over time
kubectl top pods -n observability-platform
  --sort-by=memory

# Check Collector exporter queue length
# (high queue = backend is slow, causing buffering)
curl localhost:8888/metrics | grep \
  "otelcol_exporter_queue_size"
```

**Fix:**
Increase memory limit to 2Gi. Configure exporter
max queue size to prevent unbounded growth:
```yaml
exporters:
  prometheusremotewrite:
    sending_queue:
      enabled: true
      num_consumers: 10
      queue_size: 10000
    retry_on_failure:
      enabled: true
      max_elapsed_time: 300s
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `What Is Observability` - the three pillars the platform serves
- `Prometheus` - primary metrics storage in most platforms
- `Distributed Tracing` - trace storage and correlation
- `Grafana` - visualization layer
- `OpenTelemetry` - the standard API layer between apps and platform
- `Log Aggregation at Scale` - log storage and pipeline
- `Observability at Scale` - the scaling challenges the platform solves
- `Observability Platform Architecture Design` - the architecture
  this engineering practice implements

**Builds On This (learn these next):**
- `Observability-First Thinking` - organizational mindset this enables
- `Reliability Mental Model` - how platform observability
  supports organizational reliability practices

**Alternatives / Comparisons:**
- `Toil Reduction Strategy` - platform observability is one of
  the highest-ROI toil reduction investments
- `SRE Book Core Principles` - platform observability is the
  infrastructure supporting SRE organizational model
- `Observability-Driven Development Strategy` - the developer
  practice that platform observability enables

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Building and operating the organization's │
│              │ shared observability infrastructure as   │
│              │ an internal product for all app teams    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Per-team observability = 50x operations  │
│ SOLVES       │ overhead, no cross-service correlation,  │
│              │ no organization-wide SLO reporting       │
├──────────────┼───────────────────────────────────────────┤
│ KEY SPLIT    │ App team: what to observe (instruments   │
│              │ code) / Platform team: how to collect,   │
│              │ store, query, alert (owns pipeline)      │
├──────────────┼───────────────────────────────────────────┤
│ CORE STACK   │ OTel SDK + OTel Collector DaemonSet +    │
│              │ Prometheus/Thanos + Tempo + Loki + Grafana│
├──────────────┼───────────────────────────────────────────┤
│ ZERO-CONFIG  │ New service gets metrics/logs/traces     │
│ DEFAULT      │ automatically via sidecar injection and  │
│              │ OTel auto-instrumentation                │
├──────────────┼───────────────────────────────────────────┤
│ RELIABILITY  │ Platform must have higher reliability    │
│ TRAP         │ than services it monitors - meta-monitor │
│              │ the monitoring stack itself               │
├──────────────┼───────────────────────────────────────────┤
│ SCALE TRAP   │ Cardinality explosion from high-cardinality│
│              │ labels - enforce allow-list in Collector  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The platform team makes observable-by-  │
│              │ default the zero-config starting point,  │
│              │ not the engineering aspiration."         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Observability-First Thinking →           │
│              │ Reliability Mental Model                 │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Platform team owns the telemetry pipeline (collection,
   storage, querying, alerting). Application teams own
   the instrumentation code. This split is non-negotiable.
2. Zero-config default: new services should be observable
   with zero configuration. Auto-instrumentation handles
   the baseline; developers add business-specific signals.
3. Cardinality governance is a platform responsibility.
   Without enforcement, a single misbehaving service can
   degrade query performance for all services.

**Interview one-liner:**
"Platform observability engineering applies the platform
engineering model to observability: a dedicated team builds
and operates the shared telemetry pipeline (OTel Collector
fleet → Prometheus/Thanos + Loki + Tempo → Grafana) as an
internal product. Application teams instrument their code
with the OTel SDK and get metrics, logs, and traces
automatically routed to the platform. Key concerns: cardinality
governance (Collector drop rules), platform reliability
(meta-monitoring), and the zero-config onboarding path
(sidecar auto-injection + auto-instrumentation)."

> Entry stub. Generate full content using Master Prompt v3.0.
