---
id: OBS-017
title: "OpenTelemetry -- The Standard"
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★☆
depends_on: OBS-008, OBS-006, OBS-007
used_by: OBS-018, OBS-015, OBS-016
related: OBS-008, OBS-018, OBS-015, OBS-016
tags:
  - observability
  - tracing
  - metrics
  - devops
  - pattern
  - intermediate
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 17
permalink: /obs/opentelemetry-the-standard/
---

# OBS-017 - OpenTelemetry -- The Standard

⚡ TL;DR - OpenTelemetry (OTel) is the vendor-neutral
standard for instrumenting applications to emit logs,
metrics, and traces. It defines APIs, SDKs, and a
wire protocol (OTLP) so that instrumentation code is
written once and backend (Jaeger, Prometheus, Datadog)
is swapped without code changes.

| #017            | Category: Observability & SRE                                         | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Tracing Fundamentals, Metrics Types, Logging Fundamentals |                 |
| **Used by:**    | Jaeger/Zipkin, Prometheus, Grafana                                    |                 |
| **Related:**    | Distributed Tracing, Jaeger/Zipkin, Prometheus, Grafana               |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In 2018, a team building a Java microservice needed
distributed tracing. They chose Jaeger. They added
the OpenTracing SDK. A year later, the organisation
decided to evaluate Datadog. To switch, every service
had to replace all tracing instrumentation code -
a multi-month migration. The next year, the org
evaluated Honeycomb. Another multi-month migration.
Each tool had its own SDK, its own API, its own agent.
Instrumenting for observability was permanently
coupled to the choice of backend tool.

**THE MERGER:**
OpenTracing (for distributed tracing) and OpenCensus
(for metrics + tracing) were competing standards.
Both had the right idea (vendor-neutral APIs) but
split the ecosystem. In 2019, they merged to form
OpenTelemetry, hosted by the CNCF. OTel defines:

- APIs (what your code calls to emit telemetry)
- SDKs (language-specific implementations)
- OTLP (the wire protocol for transmitting telemetry)
- Collector (an agent that receives, processes, and
  exports telemetry to any backend)

Now: instrument once with OTel, send to Jaeger today,
switch to Datadog tomorrow without touching application
code.

---

### 📘 Textbook Definition

**OpenTelemetry (OTel)** is a CNCF-hosted open-source
framework that provides vendor-neutral APIs, SDKs,
and a data transmission protocol (OTLP) for collecting
and exporting logs, metrics, and traces from
applications and infrastructure.

**Core components:**

- **API:** the interface your application code calls
  (create span, record metric). Language-specific.
  Zero overhead if no SDK is configured.
- **SDK:** the implementation that processes and
  batches telemetry. Configurable with processors
  and exporters.
- **OTLP (OpenTelemetry Protocol):** the wire protocol
  for sending telemetry data. Supports gRPC and HTTP.
- **OTel Collector:** a standalone binary that receives
  telemetry (from apps or other collectors), processes
  it (filter, transform, sample), and exports to one
  or more backends.
- **Auto-instrumentation:** agents that instrument
  popular libraries (HTTP frameworks, database drivers,
  message queues) without code changes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
OpenTelemetry is the USB standard for observability
instrumentation - write once, connect to any backend.

> Think of USB. Before USB, every peripheral (mouse,
> keyboard, printer) had its own connector. Switching
> from one mouse manufacturer to another required
> a different port. USB standardised the connection
> layer: any USB device works in any USB port,
> regardless of manufacturer. OpenTelemetry is USB
> for observability instrumentation. Any OTel-
> instrumented application can export telemetry to
> any OTel-compatible backend (Jaeger, Zipkin,
> Datadog, Honeycomb, Prometheus) without changing
> the instrumentation code.

**One insight:**
The most important property of OTel: the API is
completely separate from the SDK and the backend.
Code written against the OTel API will compile and
run with zero overhead if no SDK is installed.
This means open-source libraries can safely add
OTel instrumentation without forcing their users
to import observability dependencies.

---

### 🔩 First Principles Explanation

**THE THREE-LAYER ARCHITECTURE:**

```
Layer 1: Application Code (uses OTel API)
  tracer.StartSpan("checkout.payment")
  meter.Float64Counter("checkout.requests")
  logger.Info("payment processed", ...)
  ↓ (OTel API calls - vendor-neutral)

Layer 2: OTel SDK (processes telemetry)
  - Samples traces (head or tail)
  - Batches metrics
  - Enriches with resource attributes
  - Exports via OTLP
  ↓ (OTLP: gRPC or HTTP)

Layer 3: OTel Collector / Backend
  Receive → Process → Export
  Process: filter, transform, aggregate
  Export: Jaeger, Prometheus, Datadog, S3
```

**THE TRACE DATA MODEL:**

```
Trace: a logical unit of work across services
  └── Span: one unit of work (HTTP call, DB query)
        ├── trace_id: globally unique trace identifier
        ├── span_id: unique span identifier
        ├── parent_span_id: links to parent span
        ├── name: "checkout.process_payment"
        ├── start_time / end_time
        ├── status: OK / ERROR
        ├── attributes: key-value metadata
        │   payment.method=visa
        │   http.status_code=200
        └── events: timestamped log entries within span
            {time: ..., name: "payment_gateway_called"}
```

**CONTEXT PROPAGATION:**
The key mechanism that makes distributed tracing
work across service boundaries:

```
Service A (checkout-api):
  Creates Span, adds trace_id + span_id to HTTP headers
  W3C Trace Context: traceparent: 00-{trace_id}-{span_id}-01
        ↓ HTTP request with headers
Service B (payment-gateway):
  Reads traceparent header
  Creates child Span with same trace_id
  All spans from both services linked in one trace
```

---

### 🧪 Thought Experiment

**THE BACKEND MIGRATION SCENARIO:**

Your company runs 50 microservices all instrumented
with OTel. Year 1: export to Jaeger (self-hosted).
Year 2: management decides to evaluate Datadog.

**Without OTel (vendor SDK):**
Migration plan: 8 weeks, 4 engineers, update all
service instrumentation, update CI/CD pipelines,
validate that all traces appear in Datadog.

**With OTel:**
Migration plan: 2 days, 1 engineer, update the
OTel Collector configuration to add a Datadog exporter.

```yaml
# Before (Collector config)
exporters:
  jaeger:
    endpoint: jaeger:14250

# After (add Datadog, keep Jaeger for parallel validation)
exporters:
  jaeger:
    endpoint: jaeger:14250
  datadog:
    api:
      key: ${DATADOG_API_KEY}
      site: datadoghq.com

service:
  pipelines:
    traces:
      exporters: [jaeger, datadog]  # fan-out
```

Zero application code changes. All 50 services
automatically export to both backends. Run in parallel
for 2 weeks to validate Datadog coverage, then remove
the Jaeger exporter.

**The insight:** OTel's value is not the day you
adopt it - it is the day you need to change backends.
Without OTel, vendor lock-in is the default state.

---

### 🧠 Mental Model / Analogy

> A music streaming service uses a media player with
> a standard audio output (3.5mm jack). When the
> speaker manufacturer changes, the listener swaps
> the speaker without replacing the music player.
> The music player (OTel SDK) doesn't care which
> speaker (backend) it connects to, because both
> use the standard interface (OTLP).
>
> The OTel Collector is the amplifier/router in this
> analogy: it receives audio from multiple sources
> (multiple services), processes it (equalise,
> normalise volume), and sends it to multiple outputs
> (Jaeger for operations, Datadog for business,
> S3 for archival). The application code only knows
> about the standard interface (OTel API), not about
> the amplifier or the speakers.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone):**
OTel is a standard way for applications to report
their performance data (timings, errors, logs) so
that any monitoring tool can read it.

**Level 2 - How to use it (junior):**
Add the OTel SDK to your application. Configure it
to export via OTLP to the OTel Collector. The Collector
sends data to Jaeger (traces) and Prometheus (metrics).
Use auto-instrumentation for HTTP frameworks and
database libraries.

**Level 3 - How it works (mid-level):**
OTel API = interface your code uses. OTel SDK =
implementation that processes and exports. Collector
= receive/process/export pipeline. OTLP = the protocol.
Context propagation (W3C traceparent header) links
spans across services into a complete trace.
Sampling reduces trace volume at high traffic.

**Level 4 - Architecture (senior):**
Collector deployment patterns: agent (sidecar or
daemonset per host) vs gateway (centralised). Tail-
based sampling (route traces through a stateful
component that can decide based on the full trace
whether to keep it - e.g., keep all error traces).
Head-based sampling (decide at trace creation -
simple but cannot keep all error traces). Resource
attributes for fleet-wide correlation.

**Level 5 - Platform engineering (staff):**
The OTel Collector as a telemetry processing pipeline:
processors for PII redaction, span enrichment (add
k8s metadata), data normalization. Multi-tenant
Collector configurations. OTel for infrastructure
(host metrics, Kubernetes metrics) not just
application code. Managing Collector versions at
scale. Correlation of the three pillars via exemplars
(a metric sample linked to a trace ID).

---

### ⚙️ How It Works (Mechanism)

**COLLECTOR PIPELINE:**

```
[OTel SDK in application]
  Batches traces/metrics/logs
  Sends via OTLP gRPC to Collector
        ↓
[OTel Collector - Receiver]
  otlp receiver:
    grpc: 0.0.0.0:4317
    http: 0.0.0.0:4318
        ↓
[OTel Collector - Processor]
  batch: groups data to reduce API calls
  memory_limiter: prevents OOM
  resource_detection: adds k8s pod/node labels
  span_filter: drop health check spans (noisy)
  pii_scrubber: remove credit card numbers from attrs
        ↓
[OTel Collector - Exporter]
  jaeger: traces → Jaeger backend
  prometheus: metrics → Prometheus scrape endpoint
  loki: logs → Loki
  datadog: all signals → Datadog
```

**TRACE CONTEXT PROPAGATION:**

```java
// Service A: checkout-api (Java)
Span span = tracer.spanBuilder("process_payment")
    .setSpanKind(SpanKind.CLIENT)
    .startSpan();
try (Scope scope = span.makeCurrent()) {
    // HTTP client automatically injects
    // traceparent header via OTel HTTP instrumentation
    paymentGatewayClient.charge(request);
} finally {
    span.end();
}

// Service B: payment-gateway (Go)
// HTTP framework automatically extracts context
// from traceparent header and creates child span
func handleCharge(w http.ResponseWriter, r *http.Request) {
    ctx := otel.GetTextMapPropagator().Extract(
        r.Context(),
        propagation.HeaderCarrier(r.Header),
    )
    _, span := tracer.Start(ctx, "charge.process")
    defer span.End()
    // span is a child of Service A's span
    // same trace_id, different span_id
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**OTEL IN KUBERNETES:**

```
[checkout-service pod]
  Java app with OTel Java agent (auto-instrumentation)
  Agent instruments: Spring, JDBC, HTTP clients
  Exports OTLP to localhost:4317 (Collector sidecar)
        ↓
[OTel Collector sidecar container in pod]
  Receives OTLP from app
  Adds k8s resource attributes:
    k8s.pod.name, k8s.namespace.name
    service.name=checkout-api
    service.version=v1.47.2
  Exports to:
    traces → Jaeger Collector (central)
    metrics → Prometheus (via OTLP receiver)
    logs → Loki (central)
        ↓
[Central OTel Collector gateway]
  Aggregates from all pods
  Tail-based sampling: keep 100% error traces,
    5% success traces
  Exports to long-term storage
        ↓
[Backends]
  Jaeger → trace visualisation
  Prometheus → metrics, SLO alerting
  Loki → log aggregation
  Grafana → visualise all three, correlated
```

---

### 💻 Code Example

**Example 1 - BAD: Vendor-locked instrumentation:**

```java
// BAD: Jaeger-specific client library
// Migration to Datadog requires replacing ALL of this
import io.jaegertracing.Configuration;
import io.jaegertracing.internal.JaegerTracer;
import io.opentracing.Span;

JaegerTracer tracer = Configuration.fromEnv()
    .getTracer();

Span span = tracer.buildSpan("checkout").start();
span.setTag("payment.method", "visa");
span.finish();
// Jaeger-specific API throughout the codebase
// Switching to Datadog = rewrite all instrumentation
```

**Example 2 - GOOD: OTel API (vendor-neutral):**

```java
// GOOD: OTel API - switching backend = Collector config
import io.opentelemetry.api.GlobalOpenTelemetry;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.StatusCode;

Tracer tracer = GlobalOpenTelemetry.getTracer(
    "checkout-service", "1.47.2");

Span span = tracer.spanBuilder("checkout.payment")
    .startSpan();
try (var scope = span.makeCurrent()) {
    span.setAttribute("payment.method", "visa");
    span.setAttribute("payment.amount", 99.99);
    PaymentResult result = processPayment(request);
    if (!result.isSuccess()) {
        span.setStatus(StatusCode.ERROR, result.error());
        span.recordException(result.getException());
    }
} finally {
    span.end();
}
// To switch from Jaeger to Datadog: change Collector
// config only. Zero application code changes.
```

**Example 3 - OTel Collector config (production):**

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024
  memory_limiter:
    limit_mib: 512
    spike_limit_mib: 128
    check_interval: 5s
  resource_detection:
    detectors: [k8s_node, env]
    timeout: 2s
  # Drop health check spans (noise reduction)
  filter/health_check:
    spans:
      exclude:
        match_type: strict
        attributes:
          - key: http.url
            value: /health

exporters:
  otlp/jaeger:
    endpoint: jaeger-collector:4317
    tls:
      insecure: true
  prometheus:
    endpoint: "0.0.0.0:8889"
  loki:
    endpoint: http://loki:3100/loki/api/v1/push

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors:
        [memory_limiter, filter/health_check, resource_detection, batch]
      exporters: [otlp/jaeger]
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [prometheus]
    logs:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [loki]
```

---

### ⚖️ Comparison Table

| Aspect               | OpenTelemetry                              | OpenTracing (legacy)   | Vendor SDK (Datadog)  |
| -------------------- | ------------------------------------------ | ---------------------- | --------------------- |
| Signals              | Traces + Metrics + Logs                    | Traces only            | All (vendor-specific) |
| Vendor lock-in       | None (change Collector config)             | None                   | Full vendor lock-in   |
| Backend              | Any OTLP-compatible backend                | Jaeger, Zipkin         | Datadog only          |
| Auto-instrumentation | Yes (Java, Python, JS, Go)                 | Limited                | Yes (proprietary)     |
| Maturity             | Stable (traces/metrics), developing (logs) | Deprecated - use OTel  | Stable                |
| Operational overhead | OTel Collector to maintain                 | Simpler (no collector) | Low (managed agent)   |

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                                                                                                                                |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "OTel replaces Jaeger/Prometheus"             | OTel is the instrumentation layer; Jaeger and Prometheus are backends. OTel replaces vendor-specific instrumentation SDKs, not the storage and query backends.                                                                                         |
| "Auto-instrumentation covers everything"      | Auto-instrumentation covers popular frameworks (Spring, Express, Django) but custom business logic (the payment processing function itself) requires manual spans. Use auto-instrumentation as the foundation; add manual spans for custom operations. |
| "OTel Collector is optional"                  | Technically true - the SDK can export directly to a backend. But the Collector provides: tail-based sampling, PII scrubbing, backend decoupling, batching optimisation. For production, a Collector is strongly recommended.                           |
| "OTel logs are mature"                        | OTel tracing (stable) and metrics (stable) are production-ready. OTel logging is still evolving and less mature than traces/metrics. Many teams use OTel for traces/metrics and a separate log shipping solution.                                      |
| "All OTel data must go through one Collector" | The Collector supports fan-out (one receiver, multiple exporters) and fan-in (multiple receivers, one exporter). You can route traces to Jaeger and metrics to Prometheus from the same Collector.                                                     |

---

### 🚨 Failure Modes & Diagnosis

**Spans not appearing in Jaeger after OTel instrumentation**

**Symptom:**
OTel instrumentation added to the checkout service.
The application runs without errors. No spans appear
in Jaeger. The OTel SDK logs show "Exporter batched
0 spans."

**Root Cause candidates:**

1. OTel SDK configured with a no-op exporter (default
   when no exporter is explicitly configured)
2. OTLP endpoint misconfigured (wrong port or hostname)
3. Sampling rate set to 0 (all traces dropped)

**Diagnostic:**

```bash
# Check OTel SDK configuration via env vars
env | grep OTEL

# Expected:
# OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
# OTEL_SERVICE_NAME=checkout-api
# OTEL_TRACES_SAMPLER=parentbased_traceidratio
# OTEL_TRACES_SAMPLER_ARG=1.0

# Check Collector is receiving
kubectl logs deployment/otel-collector | grep "receiver"
# Expected: "TracesReceiver started"

# Check Jaeger is receiving from Collector
kubectl logs deployment/jaeger | grep "spans"
```

**Fix:**
Set the OTLP endpoint explicitly:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
export OTEL_TRACES_SAMPLER_ARG=1.0  # 100% sampling for debug
```

---

**Context propagation not working across services**

**Symptom:**
Traces in Jaeger show disconnected spans - spans
from service A and service B that should be part of
the same trace appear as separate, unlinked traces.
Each service generates its own root span instead of
child spans connected to the parent.

**Root Cause:**
The HTTP client or server framework is not propagating
the W3C `traceparent` header between services.
Either: (1) the propagator is not registered globally,
or (2) the HTTP framework integration is not installed
or configured to inject/extract context.

**Diagnostic:**

```bash
# Check if traceparent header is sent
# Add debug logging to HTTP client
curl -v http://checkout-api/checkout 2>&1 | grep traceparent

# Expected in outgoing request:
# traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
```

**Fix:**

```java
// Register W3C propagator globally at startup
OpenTelemetrySdk.builder()
    .setPropagators(ContextPropagators.create(
        W3CTraceContextPropagator.getInstance()
    ))
    .build();

// Ensure HTTP instrumentation is on classpath
// For Java: opentelemetry-instrumentation-okhttp-3.0
// For Spring: opentelemetry-spring-boot-starter
```

---

**Collector OOM crash due to trace volume spike**

**Symptom:**
During a Black Friday traffic spike (10x normal),
the OTel Collector crashes with OOMKilled. Traces
stop flowing. Metrics continue (separate pipeline).
The memory_limiter processor was not configured.

**Root Cause:**
The Collector buffers traces in memory before batching.
During a 10x traffic spike, the trace buffer exceeds
available memory. Without `memory_limiter`, the
Collector does not shed load and crashes.

**Fix:**

```yaml
processors:
  memory_limiter:
    # Refuse new data when memory exceeds this
    limit_mib: 512
    # Begin refusing when approaching limit
    spike_limit_mib: 128
    # Check interval
    check_interval: 5s
  # Add tail sampling to reduce volume
  tail_sampling:
    policies:
      # Always keep error traces
      - name: error-policy
        type: status_code
        status_code: { status_codes: [ERROR] }
      # Sample 5% of success traces
      - name: rate-limiting
        type: rate_limiting
        rate_limiting: { spans_per_second: 100 }
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Distributed Tracing Fundamentals` - the trace/span
  data model that OTel implements and standardises
- `Metrics Types (Counter, Gauge, Histogram)` - the
  Prometheus metric types that OTel metrics map to

**Builds On This (learn these next):**

- `Jaeger / Zipkin Distributed Tracing` - the trace
  backends that OTel sends data to
- `Prometheus Metrics Collection` - the metrics
  backend that OTel Collector exports to via OTLP
  receiver or Prometheus exporter

**Alternatives / Comparisons:**

- `Vendor SDKs (Datadog, Dynatrace)` - proprietary
  alternatives with higher lock-in but lower operational
  overhead. OTel is preferred when vendor flexibility
  is required.
- `OpenTracing` - deprecated predecessor to OTel.
  Covers only traces, not metrics or logs.

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Vendor-neutral standard for telemetry     │
│              │ instrumentation (traces, metrics, logs)   │
├──────────────┼───────────────────────────────────────────┤
│ COMPONENTS   │ API: what your code calls                 │
│              │ SDK: implements API, batches, exports     │
│              │ OTLP: wire protocol (gRPC/HTTP)           │
│              │ Collector: receive/process/export         │
├──────────────┼───────────────────────────────────────────┤
│ KEY BENEFIT  │ Change backend = change Collector config  │
│              │ Zero application code changes             │
├──────────────┼───────────────────────────────────────────┤
│ PROPAGATION  │ W3C traceparent header links spans across │
│              │ services into one trace                   │
├──────────────┼───────────────────────────────────────────┤
│ COLLECTOR    │ agent (sidecar): per-pod                  │
│ PATTERNS     │ gateway (central): per-cluster            │
│              │ hybrid: agent → gateway → backend         │
├──────────────┼───────────────────────────────────────────┤
│ SAMPLING     │ head: decide at trace start (simple)      │
│              │ tail: decide after full trace (smart)     │
│              │ keep all errors, sample success rates     │
├──────────────┼───────────────────────────────────────────┤
│ MATURITY     │ Traces: stable. Metrics: stable.          │
│              │ Logs: evolving.                           │
├──────────────┼───────────────────────────────────────────┤
│ COMMON BUG   │ No spans = no exporter configured.        │
│              │ Disconnected spans = propagator missing.  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Jaeger/Zipkin → Collector tail sampling   │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Decouple interface from implementation at every
system boundary. OTel does this for observability:
the API (interface) is permanent; the backend
(implementation) can change. This principle applies
broadly: use JDBC instead of MySQL-specific driver
calls, use Kafka producer API instead of broker-
specific APIs, use HTTP standards instead of
vendor-specific RPC protocols. Every time you
accept vendor lock-in at an interface, you pay
a migration tax on every future technology decision.

---

### 💡 The Surprising Truth

The most counterintuitive OTel insight: the OTel
API has zero overhead when no SDK is registered.
This means that open-source libraries (Spring,
Django, Express, AWS SDK) can safely add OTel
instrumentation to their source code without forcing
every user to import observability dependencies.
If the user does not register an OTel SDK, the API
calls are no-ops. This is why the OTel ecosystem
has grown so quickly: library authors add OTel
instrumentation, users get automatic traces from
their HTTP framework and database calls without
writing any instrumentation code themselves.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[EXPLAIN]** Explain the difference between the
   OTel API, SDK, and Collector to a junior developer
   who asks "why do we need three things?" Use the USB
   analogy or equivalent.
2. **[DEBUG]** Given a scenario where spans are not
   appearing in Jaeger, diagnose the issue by checking
   environment variables, Collector logs, and the
   W3C `traceparent` header in HTTP requests.
3. **[CODE]** Instrument a Java or Python HTTP service
   with OTel: create spans for the critical operations,
   add relevant attributes, propagate context to
   downstream HTTP calls. Use auto-instrumentation
   for the HTTP framework and manual spans for
   custom business logic.
4. **[CONFIGURE]** Write a complete OTel Collector
   configuration that: receives OTLP from applications,
   adds Kubernetes resource attributes, filters health
   check spans, and exports traces to Jaeger and
   metrics to Prometheus.
5. **[DESIGN]** Design the OTel deployment architecture
   for a 100-service Kubernetes cluster: agent vs
   gateway Collector topology, sampling strategy
   (head vs tail, what percentage), and backend
   selection justification.

---

### 🧠 Think About This Before We Continue

**Q1.** Your organisation runs 50 microservices in
5 languages (Java, Go, Python, Node.js, Ruby). The
current state: no distributed tracing, each service
has vendor-specific Datadog SDK. The decision has been
made to migrate to OTel for portability. What is your
12-week migration plan? What is the highest-risk
service to migrate first? What is the lowest-risk
service? How do you validate that traces are correct
after migration?
_Hint: Start with the lowest-traffic, best-tested
service (lowest blast radius if migration breaks
something). Run OTel and Datadog SDK in parallel for
2 weeks (use Collector fan-out to both backends).
Compare trace coverage in both backends. Highest risk:
the service with most custom tracing code (more code
to change). Validation: 95% of trace IDs appearing
in OTel backend that also appear in Datadog backend._

**Q2.** You deploy the OTel Java agent to the checkout
service using auto-instrumentation. You notice that
the Jaeger trace for a checkout request includes 150
spans - HTTP framework spans, database query spans,
cache read spans. The trace is too noisy to be useful
for incident investigation. How do you reduce the
noise while keeping the important spans?
_Hint: Options: (1) increase span sampling rate
threshold - drop spans shorter than 1ms (Collector
filter processor), (2) filter health check and metric
endpoint spans, (3) reduce auto-instrumentation scope
(configure agent to instrument only specific packages),
(4) promote key spans to higher sampling priority,
(5) use tail sampling - keep full trace only for
requests > P95 latency or with errors._

**Q3 (TYPE G):** You are the observability platform
architect. The company wants to unify its observability
data in a single vendor platform (Honeycomb). Currently:
Prometheus for metrics, Jaeger for traces, ELK for logs.
All 80 services need to be migrated. Design the
migration plan using OTel. What changes to application
code? What changes to infrastructure? What is the
rollback plan? What is the risk of the migration?
How do you ensure no observability blind spots during
the migration?
_Hint: Application code: add OTel SDK if not present
(auto-instrumentation where possible). Infrastructure:
deploy OTel Collector with Honeycomb exporter + existing
exporters (parallel for validation). Migration: fan-out
to both old backends and Honeycomb for 4 weeks per
service batch. Rollback: remove Honeycomb exporter
from Collector (zero app code changes). Risk: OTel
Collector becomes SPOF - mitigate with HA deployment
and agent model (each pod has its own Collector sidecar)._

---

### 🎯 Interview Deep-Dive

**Q1: "What is OpenTelemetry and why does it matter?"**
_Why they ask:_ Tests awareness of the current standard
in distributed observability.
_Strong answer includes:_

- OTel is the CNCF standard for vendor-neutral
  telemetry instrumentation
- It solves vendor lock-in: instrument once with OTel
  API, change backend via Collector configuration
- Components: API (what code calls), SDK (implements),
  OTLP (wire protocol), Collector (process/export)
- Why it matters: the entire observability ecosystem
  (Jaeger, Prometheus, Datadog, Honeycomb) is
  converging on OTel. Libraries are adding OTel
  instrumentation by default.

**Q2: "How does context propagation work in OTel
distributed tracing?"**
_Why they ask:_ Tests understanding of the key
mechanism that makes distributed tracing work.
_Strong answer includes:_

- Context propagation links spans across service
  boundaries into a single trace
- W3C traceparent header carries trace_id + span_id
  between services via HTTP headers (or message
  attributes for async communication)
- Service A creates a root span, injects traceparent
  into outgoing HTTP request
- Service B extracts traceparent, creates child span
  with the same trace_id
- Result: all spans from the entire request lifecycle
  are linked into one trace in Jaeger

**Q3: "When would you use head-based sampling vs
tail-based sampling in OTel?"**
_Why they ask:_ Tests understanding of the most
important production tracing decision.
_Strong answer includes:_

- Head-based: sampling decision made at the root span
  (first service). Simple, no state required, low
  latency. Cannot keep all error traces because the
  error is not known at trace start.
- Tail-based: decision made after the full trace is
  collected (in the Collector). Can implement "always
  keep error traces, sample 5% of success traces."
  Requires stateful Collector (all spans of a trace
  must arrive at the same Collector instance).
- Rule of thumb: head sampling for initial rollout
  (simpler), tail sampling for production (more
  intelligent). Tail sampling requires the OTel
  Collector's tail_sampling processor and a consistent
  hashing routing configuration if running multiple
  Collector replicas.

> Entry stub. Generate full content using Master Prompt v3.0.
