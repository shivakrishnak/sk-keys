---
id: OBS-004
title: The Observability Ecosystem Map
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★☆☆
depends_on: OBS-001, OBS-002
used_by: OBS-015, OBS-016, OBS-017
related: OBS-001, OBS-002, OBS-003
tags:
  - observability
  - reliability
  - foundational
  - mental-model
  - devops
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Mastery"
nav_order: 4
permalink: /technical-mastery/obs/the-observability-ecosystem-map/
---

⚡ TL;DR - The observability ecosystem spans instrumentation,
collection, storage, and visualisation layers - knowing the
map prevents vendor lock-in and wrong tool choices.

| #004            | Category: Observability & SRE                                                                             | Difficulty: ★☆☆ |
| :-------------- | :-------------------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | What Is Observability and Why It Matters, The Three Pillars of Observability                              |                 |
| **Used by:**    | Prometheus - Metrics Collection, Grafana - Dashboards, OpenTelemetry - The Standard                       |                 |
| **Related:**    | What Is Observability and Why It Matters, The Three Pillars of Observability, Monitoring vs Observability |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An engineer joins a new team and is told "we use observability."
They find: Datadog agents on every server, a Prometheus server
no one maintains, an ELK stack collecting application logs, a
Jaeger instance for traces (which no service actually
instruments), and three separate Grafana instances with
conflicting dashboards. No one knows what each tool does,
which is authoritative, or whether the data in each is
trustworthy. Budgets are spent three times on overlapping
functionality. Incidents are investigated using whichever tool
the on-call engineer is most comfortable with, producing
inconsistent results.

**THE BREAKING POINT:**
Without a mental map of the observability ecosystem, teams
buy tools reactively - a vendor demo here, a blog post there.
The result is a fragmented, expensive, unmaintainable
patchwork. Different teams in the same company instrument
their services differently. Correlation between services is
impossible because one uses Zipkin and another uses Jaeger.
The observability budget is high; the diagnostic capability
is low.

**THE INVENTION MOMENT:**
This is exactly why ecosystem literacy matters - to give
engineers the map they need to make intentional architecture
decisions: which layer needs which tool, what the open-source
baseline looks like, and when a vendor solution is worth its
cost.

**EVOLUTION:**
The observability tool landscape exploded between 2016 and 2022. Prometheus (2012) standardised metrics collection. The
ELK Stack (Elasticsearch/Logstash/Kibana, 2010-2014)
standardised log management. Jaeger and Zipkin (2015-2016)
brought distributed tracing to open source. OpenTelemetry
(2019, merged from OpenCensus and OpenTracing) unified the
instrumentation layer. By 2024, the ecosystem has stabilised
around four architectural layers with clear open-source
defaults and commercial alternatives at each layer.

---

### 📘 Textbook Definition

The **observability ecosystem** is the set of tools, protocols,
and standards that collectively implement the collection,
transmission, storage, query, and visualisation of
observability signals (logs, metrics, and traces) from
production software systems.

The ecosystem is structured in four layers: instrumentation
(SDK and auto-instrumentation in the application),
collection (agents and collectors that gather and route
signals), storage (backends optimised for each signal type),
and query/visualisation (dashboards, trace UI, and alert
engines).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The observability ecosystem is a four-layer stack: instrument
your code, collect the signals, store them, then query them.

> Think of a city's water system. Pipes in the building
> (instrumentation) carry water to collection mains (collectors).
> Mains route water to reservoirs (storage backends). Treatment
> plants and taps (query/visualisation) deliver clean,
> accessible water on demand. Each layer has its own
> engineering standards and can be swapped independently.

**One insight:**
The ecosystem's four layers are independent. You can change
your storage backend from Elasticsearch to Loki without
changing your instrumentation SDK. You can swap Grafana for
Kibana without changing Prometheus. Understanding this layering
prevents you from accidentally creating tight coupling between
layers that should be modular.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. The instrumentation layer must be decoupled from the storage
   layer - changing the backend should not require rewriting
   application code
2. Each signal type (logs, metrics, traces) has a different
   optimal storage model and query pattern
3. The collection layer must buffer, sample, and route signals
   independently of both the application and the backend
4. Open standards (OpenTelemetry, Prometheus remote write,
   OTLP) are the interfaces that enable layer substitution

**DERIVED DESIGN:**
The separation of concerns across four layers is what enables
the observability ecosystem to evolve. OpenTelemetry was
created specifically to break the coupling between
instrumentation and vendor-specific agents. Before it,
switching from Datadog to Honeycomb required rewriting all
instrumentation code. With OpenTelemetry, switching backends
requires only reconfiguring the collector.

**THE TRADE-OFFS:**

**Gain:** Vendor independence. Layer-by-layer upgrades.
Best-in-class tooling at each layer. Open-source cost control.

**Cost:** Integration complexity. Multiple operational systems
to maintain. Need to understand each layer's failure modes.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Signal collection, storage, and query are
genuinely different engineering problems with different
optimal solutions. This layering is inherent.

**Accidental:** The proliferation of incompatible agents,
wire protocols, and data formats before OpenTelemetry was
accidental complexity - now largely resolved by the standard.

---

### 🧪 Thought Experiment

**SETUP:**
A startup builds an e-commerce platform. They have 5
engineers and a $2,000/month infrastructure budget. They
need observability but cannot afford Datadog at scale
($50,000/month at their projected traffic). They need to
choose a stack.

**WHAT HAPPENS WITHOUT AN ECOSYSTEM MAP:**
The team Googles "best observability tool" and installs
Datadog because it appears first. At 100k requests per day,
the bill is manageable. At 10 million requests per day
(12 months later), the Datadog bill is $45,000/month.
Migration is painful because all instrumentation uses
the Datadog proprietary agent SDK - not OpenTelemetry.
Rewriting takes 3 months.

**WHAT HAPPENS WITH AN ECOSYSTEM MAP:**
The team instruments with OpenTelemetry from day 1 (free,
open standard). They use Prometheus (free) for metrics,
Loki (free) for logs, Tempo (free) for traces, and Grafana
(free) for dashboards. At 10 million requests per day,
the self-hosted stack costs $800/month. Because they used
OpenTelemetry, if they later want Datadog's AI features,
migration requires only reconfiguring the OTel collector

- not rewriting application code.

**THE INSIGHT:**
Knowing the ecosystem map before you start avoids months of
painful migration later. The key decision is always:
instrument with an open standard, then choose your storage
and visualisation later.

---

### 🧠 Mental Model / Analogy

> The observability ecosystem is like a city's telecommunications
> infrastructure. The handset (instrumentation SDK) creates
> the signal. Cell towers (collectors) aggregate and route
> signals from many devices. Data centers (storage backends)
> store the data. Apps on your phone (query/visualisation)
> let you access it. Each layer has standards (GSM, LTE, HTTP)
> that allow substitution - you can switch from an iPhone to
> an Android without the cell towers changing.

Mapping:

- "Handset / phone app code" - instrumentation SDK
  (OpenTelemetry in application code)
- "Cell towers" - collectors (OpenTelemetry Collector, agents)
- "Data centers" - storage backends (Prometheus, Loki, Tempo)
- "Apps on phone" - query and visualisation (Grafana, Kibana)
- "Communication standards (LTE, 5G)" - open protocols
  (OTLP, Prometheus remote write, OpenTelemetry)

**Where this analogy breaks down:** In telecoms, the network
is shared infrastructure. In observability, each company
operates its own stack. The analogy holds for the layering
principle but not for the ownership model.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
The observability ecosystem is all the tools that work
together to let you see what your software is doing. Some
collect data, some store it, some help you search and
visualise it. They are designed to work together like
puzzle pieces.

**Level 2 - How to use it (junior developer):**
Start with the instrumentation layer: add OpenTelemetry to
your service. Pick a storage backend for each signal type
(Prometheus for metrics, Loki for logs, Tempo for traces).
Use Grafana to visualise all three. This is the minimal
open-source stack and it works well at startup-to-mid scale.

**Level 3 - How it works (mid-level engineer):**
Each layer communicates via standard protocols. Your service
sends OTLP (OpenTelemetry Protocol) to the OTel Collector.
The Collector processes and routes: metrics via Prometheus
remote write to a TSDB, logs via Loki's push API, traces via
OTLP to Tempo or Jaeger. Grafana queries all backends and
correlates them by trace ID. Every component is replaceable
because they talk via open protocols.

**Level 4 - Why it was designed this way (senior/staff):**
The layered design evolved from painful lessons. Early
observability was vertically integrated: Datadog had its own
agent, its own wire protocol, its own backend, and its own
UI. Switching required rewriting everything. OpenTelemetry
breaks this coupling at the instrumentation layer. Grafana
breaks it at the visualisation layer. The ecosystem has
converged on a pattern: OpenTelemetry for instrumentation
and collection, vendor choice for storage, Grafana for
unified visualisation.

**Level 5 - Mastery (distinguished engineer):**
The staff engineer's ecosystem decision is a make-vs-buy
problem at each layer. Self-hosted open-source gives cost
control but operational burden. Managed vendors give
operational simplicity but create lock-in and cost
unpredictability at scale. The sophisticated approach:
instrument with OpenTelemetry (open standard, no lock-in),
use managed services for storage at startup scale (pay for
simplicity), migrate to self-hosted as volume grows (pay
for cost control). The inflection point is typically around
$5,000-$10,000/month on observability vendors.

**EXPERT THINKING CUES:**

- Always instrument with OpenTelemetry. Never use a vendor's
  proprietary instrumentation SDK. This is the one decision
  that cannot be undone without rewriting all services.
- The storage layer is the most costly and most replaceable.
  Prometheus is the open-source standard for metrics; Loki
  is viable for logs at moderate scale; Tempo for traces.
- Grafana is the de facto open-source visualisation standard
  and queries all backends with one UI.

---

### ⚙️ How It Works (Mechanism)

The four layers and their standard tools:

**Layer 1 - Instrumentation:**
Application code emits signals using an SDK.

- Open standard: OpenTelemetry SDK (Java, Go, Python, etc.)
- Vendor proprietary: Datadog Agent SDK, New Relic Agent
- Auto-instrumentation: OTel Java Agent (zero-code tracing)
- Protocol out: OTLP (OpenTelemetry Protocol) over gRPC/HTTP

**Layer 2 - Collection:**
Agents and collectors receive signals and route them to
storage backends.

- Open source: OpenTelemetry Collector
- Log-specific: Fluentd, Fluent Bit, Logstash
- Metrics-specific: Prometheus (pull-based scraping)
- Functions: sampling, batching, filtering, enrichment,
  routing to multiple backends

**Layer 3 - Storage:**
Signal-type-specific backends:

- Metrics TSDB: Prometheus, Thanos, Cortex, VictoriaMetrics,
  Mimir (open source); Datadog, New Relic (managed)
- Log store: Loki (open source, label-based),
  Elasticsearch/OpenSearch (full-text), Splunk (enterprise)
- Trace store: Jaeger, Tempo (open source),
  Zipkin; Honeycomb, Datadog APM (managed)

**Layer 4 - Query and Visualisation:**

- Unified dashboard: Grafana (queries all backends)
- Metrics query: Prometheus UI (PromQL)
- Log query: Kibana (Lucene/KQL), Grafana Explore (LogQL)
- Trace query: Jaeger UI, Tempo UI, Grafana Explore

```
┌─────────────────────────────────────────┐
│  Observability Ecosystem Layers         │
├─────────────────────────────────────────┤
│  L4: Query/Viz                          │
│      Grafana | Kibana | Jaeger UI       │
├─────────────────────────────────────────┤
│  L3: Storage                            │
│  Metrics: Prometheus / Thanos / Mimir   │
│  Logs:    Loki / Elasticsearch          │
│  Traces:  Tempo / Jaeger                │
├─────────────────────────────────────────┤
│  L2: Collection                         │
│      OTel Collector | Fluent Bit        │
│      Prometheus Scraper                 │
├─────────────────────────────────────────┤
│  L1: Instrumentation                    │
│      OpenTelemetry SDK (app code)       │
│      OTel Auto-Instrumentation Agent    │
└─────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
[App: OTel SDK instruments code]
    ↓
[Signals emitted via OTLP protocol]
    ↓
[OTel Collector ← YOU ARE HERE: receives all signals]
    ↓
[Collector routes by signal type:]
├── Metrics → Prometheus (remote write)
├── Logs    → Loki (push API)
└── Traces  → Tempo (OTLP)
    ↓
[Grafana queries all three backends]
    ↓
[Engineer: unified view via trace ID correlation]
```

**FAILURE PATH:**
OTel Collector is a critical path. If it is down or
misconfigured, all three signal types stop flowing. Signals
accumulate in the application's SDK queue and are dropped
when the queue is full. The first symptom: dashboards go
stale. The second: alerts stop firing (no metrics = no
alerts). Recovery requires restarting the collector;
historical data is not recoverable for the gap period.

**WHAT CHANGES AT SCALE:**
At high volume, the Collector becomes a bottleneck. It must
be scaled horizontally (multiple Collector pods) and
configured with tail-based sampling for traces. Metrics
storage must move from standalone Prometheus to a distributed
TSDB (Thanos, Cortex, Mimir) for long-term retention and
horizontal query scaling.

---

### 💻 Code Example

**Example 1 - BAD: Vendor lock-in instrumentation:**

```java
// BAD: Datadog proprietary instrumentation
// Cannot switch to Honeycomb or Jaeger without rewriting
import com.datadoghq.trace.api.Trace;

@Trace(operationName = "checkout")
public Response checkout(CheckoutRequest req) {
    // All trace spans are Datadog-proprietary
    // Switching vendors requires rewriting every annotation
    return processCheckout(req);
}
```

**Example 2 - GOOD: OpenTelemetry instrumentation (vendor-neutral):**

```java
// GOOD: OpenTelemetry - switch backends by config only
import io.opentelemetry.api.GlobalOpenTelemetry;
import io.opentelemetry.api.trace.Tracer;

public class CheckoutService {
    private final Tracer tracer =
        GlobalOpenTelemetry.getTracer("checkout-service");

    public Response checkout(CheckoutRequest req) {
        var span = tracer
            .spanBuilder("checkout")
            .setAttribute("user.id", req.getUserId())
            .startSpan();
        try (var scope = span.makeCurrent()) {
            return processCheckout(req);
        } finally {
            span.end();
        }
    }
    // To switch from Jaeger to Honeycomb: change 1 line
    // in OTel collector config - zero application changes
}
```

**Example 3 - OTel Collector routing config:**

```yaml
# GOOD: OTel Collector routes all three signal types
# Change the exporter section to switch backends
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

exporters:
  prometheusremotewrite:
    endpoint: http://prometheus:9090/api/v1/write
  loki:
    endpoint: http://loki:3100/loki/api/v1/push
  otlp/tempo:
    endpoint: tempo:4317

service:
  pipelines:
    metrics:
      receivers: [otlp]
      exporters: [prometheusremotewrite]
    logs:
      receivers: [otlp]
      exporters: [loki]
    traces:
      receivers: [otlp]
      exporters: [otlp/tempo]
```

---

### ⚖️ Comparison Table

| Stack option                         | Cost at scale | Ops burden | Lock-in  | Best For                  |
| ------------------------------------ | ------------- | ---------- | -------- | ------------------------- |
| **Open-source (OTel+Grafana stack)** | Low           | High       | None     | Cost control, large teams |
| Datadog                              | High          | Low        | High     | Fast setup, AI features   |
| Honeycomb                            | Medium        | Low        | Medium   | High-cardinality ad-hoc   |
| New Relic                            | High          | Low        | High     | APM-first teams           |
| AWS CloudWatch                       | Medium        | Low        | AWS-only | All-in AWS shops          |
| Grafana Cloud                        | Medium        | Low        | Grafana  | Open-source + managed     |

**How to choose:** Instrument with OpenTelemetry regardless
of which row you choose. At startup scale (under $2k/month
observability budget): Grafana Cloud or Datadog for
operational simplicity. At growth scale (over $5k/month):
evaluate self-hosted open-source (Prometheus + Loki + Tempo

- Grafana) to control cost.

**Decision Tree:**
Need to be operational in 1 day? - Use Datadog or Grafana Cloud
Have >10 engineers to maintain infra? - Consider self-hosted
Have AWS-only infrastructure? - CloudWatch is viable
Need highest cardinality ad-hoc queries? - Honeycomb
Need to control costs at 1B+ events/day? - Self-hosted stack

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                                                                         |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| OpenTelemetry is an observability backend              | OTel is the instrumentation and collection layer only. You still need Prometheus, Loki, and Tempo (or equivalents) as storage and query backends.                                               |
| Prometheus replaces a log store                        | Prometheus stores only metrics (numeric time-series). Logs require a separate backend (Loki, Elasticsearch). Using metrics to store log-like data is a cardinality explosion waiting to happen. |
| Grafana is a data source                               | Grafana is a visualisation layer only. It queries data from backends (Prometheus, Loki, Tempo) but stores nothing itself.                                                                       |
| More tools equals better observability                 | Each tool added is another operational system. Two tools at 80% coverage is often better than six tools at 100% coverage with triple the operational burden.                                    |
| OpenTelemetry auto-instrumentation captures everything | Auto-instrumentation captures HTTP, database, and messaging library spans. Business-domain spans (order processed, payment validated) require manual instrumentation.                           |

---

### 🚨 Failure Modes & Diagnosis

**OTel Collector as single point of failure**

**Symptom:**
All dashboards go stale simultaneously. No alerts fire despite
production errors. Metrics, logs, and traces all stop flowing
at the same time.

**Root Cause:**
The OTel Collector is down or misconfigured. It sits on the
critical path between all application signal emission and all
storage backends. A single misconfigured Collector blocks the
entire observability pipeline.

**Diagnostic Command:**

```bash
# Check OTel Collector health endpoint
curl -s localhost:13133/

# Check Collector metrics for export failures
curl -s localhost:8888/metrics | \
  grep -E "otelcol_exporter_send_failed|otelcol_receiver"

# Check Collector logs for errors
kubectl logs -n monitoring deploy/otelcollector --tail=50
```

**Fix:**
Run multiple Collector replicas behind a load balancer. Use
Kubernetes DaemonSet for node-level collection. Configure
retry and queue settings for each exporter.

**Prevention:**
The Collector must be horizontally scalable and redundant.
Never run a single Collector instance in production.

---

**Vendor lock-in at the instrumentation layer**

**Symptom:**
Team decides to switch observability vendor. Engineers
discover that every service uses the vendor's proprietary
SDK - all spans, metrics, and logs use vendor-specific APIs.
Migration estimate: 3 months of engineering time.

**Root Cause:**
Instrumentation was implemented using a vendor's proprietary
SDK (Datadog `dd-trace`, New Relic agent APIs) instead of
OpenTelemetry. The vendor SDK emits to the vendor backend
only and is not re-routable.

**Diagnostic Command:**

```bash
# Find services using proprietary Datadog instrumentation
grep -r "com.datadoghq\|dd-trace\|@Trace" \
  src/ --include="*.java" | wc -l
# High count = high migration cost
```

**Fix:**
Migrate instrumentation to OpenTelemetry SDK. This is a
service-by-service rewrite. Estimated effort: 2-4 days per
service.

**Prevention:**
Always instrument with OpenTelemetry from the start. The
rule: OpenTelemetry for instrumentation, vendor choice for
storage only.

---

**Security: credentials in Collector configuration**

**Symptom:**
OTel Collector config is committed to version control with
Datadog API keys, Honeycomb API keys, or S3 credentials
in plaintext. Security scan flags the repository.

**Root Cause:**
Credentials for exporter backends are hardcoded in the
Collector configuration YAML rather than injected via
environment variables or secrets management.

**Diagnostic Command:**

```bash
# Scan git history for potential API key patterns
git log --all --full-history -- "**/otelcol*" \
  | xargs -I{} git show {} \
  | grep -E "api_key|apikey|api-key|password" | head -10
```

**Fix:**

```yaml
# BAD: credentials in config file
exporters:
  datadog:
    api:
      key: "dd-api-key-abc123-plaintext"  # NEVER do this

# GOOD: credentials injected via environment variable
exporters:
  datadog:
    api:
      key: ${DD_API_KEY}  # injected from Kubernetes Secret
```

**Prevention:**
Never hardcode credentials in configuration files. Use
Kubernetes Secrets, AWS Secrets Manager, or Vault to inject
credentials at runtime via environment variables.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `What Is Observability and Why It Matters` - the concept
  behind the ecosystem
- `The Three Pillars of Observability (Logs, Metrics, Traces)` -
  the three signal types the ecosystem is built to handle

**Builds On This (learn these next):**

- `Prometheus - Metrics Collection` - deep dive on the
  metrics storage layer
- `Grafana - Dashboards` - deep dive on the visualisation
  layer
- `OpenTelemetry - The Standard` - deep dive on the
  instrumentation and collection layer
- `ELK/EFK Stack - Log Management` - deep dive on the log
  storage layer
- `Jaeger/Zipkin - Distributed Tracing` - deep dive on the
  trace storage layer

**Alternatives / Comparisons:**

- `Datadog - Observability Platform` - vertically integrated
  vendor alternative to the open-source stack
- `Monitoring vs Observability - The Difference` - the
  conceptual boundary within which the ecosystem operates

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Four-layer stack: instrument, collect,   │
│              │ store, and query observability signals   │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Teams buy tools reactively - fragmented, │
│ SOLVES       │ overlapping, expensive, unintentional    │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ Layers are independent: change storage   │
│              │ without rewriting instrumentation        │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Designing or auditing an observability   │
│              │ architecture from scratch or at scale    │
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ Using vendor-proprietary instrumentation │
│              │ SDKs - always use OpenTelemetry          │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Instrumenting with Datadog SDK directly -│
│              │ creates instrumentation lock-in that     │
│              │ costs months to undo                     │
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Self-hosted: low cost, high ops burden.  │
│              │ Managed vendor: high cost, low burden.   │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Always instrument with OpenTelemetry.   │
│              │  Choose your storage and vendor later."  │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ OpenTelemetry → Prometheus → Grafana     │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. The ecosystem has four independent layers: instrument,
   collect, store, query. Each layer can be swapped
   independently if you use open standards.
2. Always instrument with OpenTelemetry (the one decision
   that locks you in permanently if you get it wrong).
3. Open-source (Prometheus + Loki + Tempo + Grafana) is
   viable from day one and saves significant cost at scale
   compared to managed vendors.

**Interview one-liner:**
"The observability ecosystem has four layers: instrumentation
(OpenTelemetry SDK), collection (OTel Collector), storage
(Prometheus for metrics, Loki for logs, Tempo for traces),
and visualisation (Grafana). The layers are decoupled via
open protocols, so you can switch backends without rewriting
application code."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Separate concerns across layers and define open interfaces
between them. Any system that couples its data production,
collection, storage, and presentation into a single vendor's
stack creates lock-in. Layered architectures with open
standards at the interfaces preserve optionality.

**Where else this pattern appears:**

- **Database abstraction** - ORM frameworks (Hibernate, JPA)
  decouple application code from the specific database
  vendor, just as OpenTelemetry decouples instrumentation
  from the observability vendor.
- **Cloud infrastructure** - Terraform with modular providers
  separates infrastructure definition from cloud vendor
  APIs, exactly as OTel Collector separates signal routing
  from storage backends.
- **Message queues** - AMQP protocol decouples message
  producers from specific broker implementations (RabbitMQ,
  ActiveMQ), enabling backend substitution.

**Industry applications:**

- **FinTech startups** - start with Grafana Cloud (managed,
  low ops burden), instrument with OpenTelemetry, then
  migrate to self-hosted Prometheus + Loki + Tempo when
  the monthly bill exceeds the cost of an SRE.
- **Enterprise** - OpenTelemetry allows different business
  units to use different observability vendors (one team
  on Datadog, another on Splunk) while using the same
  instrumentation SDK and shared collection infrastructure.

---

### 💡 The Surprising Truth

OpenTelemetry was not created by Google, Microsoft, or
Amazon as an altruistic open-source contribution. It was
created specifically because observability vendors' lock-in
was costing enterprises millions of dollars in migration
costs every time they changed vendors. The founding
companies - Google, Microsoft, Uber, Splunk, Datadog, and
others - agreed to standardise the instrumentation and
collection layers as a competitive moat removal exercise:
if the instrumentation layer is open and free, competition
moves to storage and AI features where vendors can still
differentiate. The lesson: when multiple large companies
agree to standardise something, the standard is usually
worth adopting immediately.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[EXPLAIN]** Draw the four-layer ecosystem map from memory
   and name at least two tool options (one open-source, one
   managed) at each layer.
2. **[DEBUG]** Given a scenario where all three signal types
   stop flowing simultaneously, identify the three most likely
   causes in order of probability and the diagnostic command
   for each.
3. **[DECIDE]** Given a company's scale (requests per second,
   number of engineers, monthly budget), recommend a specific
   observability stack at each of the four layers and justify
   the make-vs-buy decision at each layer.
4. **[BUILD]** Write an OTel Collector configuration that
   receives OTLP signals and routes metrics to Prometheus,
   logs to Loki, and traces to Tempo.
5. **[EXTEND]** Audit an existing observability setup for
   two specific risks: instrumentation lock-in (using
   proprietary SDK) and single points of failure in the
   collection layer. Describe the remediation for each.

---

### 🧠 Think About This Before We Continue

**Q1.** Your company's observability bill is $120,000 per
month on Datadog. The engineering team says migration to
self-hosted open-source would save $100,000 per month. The
CTO asks for a migration plan. You discover all 50 services
use the Datadog proprietary Java agent, not OpenTelemetry.
Walk through a migration strategy that minimises service
disruption while progressively reducing cost. What is the
order of operations, and which layer do you migrate first?
_Hint: The Datadog agent can be configured to export to the
OTel Collector via the OTLP exporter. Does this help? What
does it not solve?_

**Q2.** The OTel Collector is processing 10 million spans per
minute. During a traffic spike, the Collector falls behind
and its memory grows until it OOMs. Describe the three
configuration changes you would make to the Collector to
handle this gracefully - considering both the Collector's
own resource limits and the impact on the downstream trace
store.
_Hint: Think about the queue size, batch processor
configuration, tail-based sampling, and memory limiter
processor. What is the correct failure mode when the
Collector is overloaded - drop signals or backpressure
to the application?_

**Q3.** Design the observability stack for a new service that
will process HIPAA-regulated health data. The stack must
not send patient data to any third-party vendor. Define
which layers must be self-hosted, which vendor tools are
acceptable, and what data redaction must happen in the
collection layer before signals reach any storage backend.
_Hint: HIPAA defines protected health information (PHI).
Which pillar is most likely to accidentally capture PHI
(a patient name in a log line, a user_id that maps to
a patient record)? Where in the four layers is the
appropriate redaction point?_

---

### 🎯 Interview Deep-Dive

**Q1: "Describe the four layers of the observability
ecosystem and give an open-source tool for each layer."**
_Why they ask:_ Tests whether the candidate has an accurate
mental map of the ecosystem, not just tool name knowledge.
_Strong answer includes:_

- Layer 1 (Instrumentation): OpenTelemetry SDK - emits OTLP
  signals from application code
- Layer 2 (Collection): OpenTelemetry Collector - receives,
  processes, and routes signals
- Layer 3 (Storage): Prometheus (metrics), Loki (logs),
  Tempo (traces)
- Layer 4 (Query/Viz): Grafana - unified dashboard querying
  all three backends
- Key point: layers are independent and can be swapped via
  open protocols

**Q2: "Why should you always use OpenTelemetry for
instrumentation even if your company currently uses Datadog?"**
_Why they ask:_ Tests understanding of architectural lock-in
and the strategic value of open standards.
_Strong answer includes:_

- OpenTelemetry is the instrumentation layer; Datadog is a
  storage + visualisation backend
- Using Datadog's proprietary SDK ties ALL instrumentation
  to Datadog - switching vendors requires rewriting every
  service
- With OpenTelemetry, you configure the OTel Collector to
  export to Datadog today and to a different backend tomorrow
  with a config change - zero application code changes
- OpenTelemetry is an industry standard backed by CNCF with
  support from Google, Microsoft, Datadog, and every major
  vendor - it is the safe choice for instrumentation

**Q3: "Your team is moving from self-hosted Jaeger to
Grafana Tempo for trace storage. What changes in your
stack, and what doesn't change?"**
_Why they ask:_ Tests understanding of layer independence -
whether the candidate can identify which layers are affected
by a storage backend change.
_Strong answer includes:_

- What does NOT change: application instrumentation (OTel
  SDK), OTel Collector pipeline definition (still receives
  OTLP), Grafana dashboards (Tempo has same Grafana
  datasource interface as Jaeger via OTLP or Zipkin)
- What DOES change: OTel Collector exporter config (point
  to Tempo instead of Jaeger OTLP endpoint), storage
  infrastructure (deploy Tempo instead of Jaeger backend),
  Grafana data source config (add Tempo datasource)
- This demonstrates the value of open standards: a storage
  backend migration affects only the Collector config and
  the Grafana datasource - nothing in the application code
