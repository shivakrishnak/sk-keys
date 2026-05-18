---
id: MSV-065
title: OpenTelemetry in Microservices
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-064, MSV-063
used_by: MSV-064
related: MSV-064, MSV-063, MSV-001, MSV-025, MSV-030, MSV-072
tags:
  - microservices
  - observability
  - deep-dive
  - tracing
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Mastery"
nav_order: 65
permalink: /technical-mastery/microservices/opentelemetry-in-microservices/
---

⚡ TL;DR - OpenTelemetry (OTEL): the open-source
observability framework that standardizes collection
of TRACES, METRICS, and LOGS (the "three pillars")
across all microservices. Key: one Java agent
(`-javaagent:opentelemetry-javaagent.jar`)
auto-instruments Spring Boot, JDBC, Kafka, gRPC
without code changes. The OTEL Collector: receives
telemetry from all services, processes it, and
exports to any backend (Jaeger for traces, Prometheus
for metrics, Elasticsearch for logs). Vendor-
neutral: switch backends without changing service
code. Industry standard: replaces vendor-specific
SDKs (Zipkin, Jaeger, StatsD).

| #065 | Category: Microservices | Difficulty: ★★★☆ |
|:---|:---|:---|
| **Depends on:** | Distributed Logging, Cross-Cutting Concerns | |
| **Used by:** | Distributed Logging | |
| **Related:** | Distributed Logging, Cross-Cutting Concerns, What are Microservices, Health Check API, Service Resilience Patterns, Sidecar Pattern | |

---

### 🔥 The Problem This Solves

**OBSERVABILITY VENDOR LOCK-IN AND FRAGMENTATION:**
Before OpenTelemetry: each service team chose
their own observability tools. Team A: Zipkin for
tracing. Team B: Jaeger. Team C: StatsD for metrics.
Team D: custom logging format. Result: no unified
view of request flow across services. Switching
backends: required code changes in every service.
Vendor-specific SDK: upgrading one SDK breaks
another team's setup. OpenTelemetry: one standard,
one SDK, any backend. No vendor lock-in.

---

### 📘 Textbook Definition

**OpenTelemetry (OTEL)** is a CNCF (Cloud Native
Computing Foundation) open-source observability
framework providing vendor-neutral APIs, SDKs,
and tools for generating, collecting, and exporting
telemetry data (traces, metrics, logs) from
software applications. Key components:
(1) **Specification** - defines the data model
for traces (spans), metrics (gauges, counters,
histograms), and logs;
(2) **API** - language-specific interfaces for
creating traces/metrics/logs in code;
(3) **SDK** - implementation of the API; configures
sampling, processing, and export;
(4) **Auto-Instrumentation** - language-specific
agents/injectors that instrument popular frameworks
without code changes (Java agent instruments Spring
MVC, JDBC, Kafka, gRPC, HTTP clients automatically);
(5) **OTEL Collector** - a deployment component
that receives, processes, and exports telemetry
data. Receiving protocols: OTLP (OTEL native),
Zipkin, Jaeger, Prometheus. Exporting backends:
Jaeger, Tempo, Prometheus, Datadog, Dynatrace,
Splunk, Elasticsearch. The W3C `traceparent` header
is the OTEL standard for distributed trace context
propagation.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
OpenTelemetry: one Java agent, zero code changes,
automatic traces + metrics + logs from all services,
export to any backend. Vendor-neutral observability
standard.

**One analogy:**
> OpenTelemetry is like a universal power adapter.
> Before: each country (observability vendor)
had its own socket (SDK). You needed a different
> adapter (SDK) for each country. Switching
> countries: rewire everything. OpenTelemetry:
> a universal adapter that works with any socket
> (any backend: Jaeger, Datadog, Prometheus). Your
> device (application) doesn't change. The adapter
> (OTEL SDK/Collector) handles the translation.
> CNCF maintains the standard: it's not owned
> by any one vendor.

**One insight:**
The OTEL Java agent is the best return-on-investment
in microservices observability. One JAR file,
one JVM startup flag: instantly get distributed
tracing, HTTP request metrics, JDBC query metrics,
Kafka consumer lag metrics, gRPC call metrics
for ALL Java services - with zero code changes.
This is "zero-code instrumentation": the most
valuable observability capability with the lowest
implementation cost. The code changes come later
(custom business spans: "payment processing"
span), but the automatic instrumentation provides
immediate value.

---

### 🔩 First Principles Explanation

**OTEL DATA MODEL:**

```
THREE TELEMETRY SIGNALS:

TRACES ("how long did it take"):
  Trace: a complete request journey (tree of spans)
  Span: a single operation within the trace
  Span attributes: key-value metadata
  (e.g., http.method=GET, http.url=/customers/123,
   db.statement=SELECT * FROM customers WHERE id=?)
  Context propagation: W3C traceparent header
  links spans across service boundaries
  
  Example trace:
  Trace: req-abc-123 (total: 245ms)
  ├ Span: order-service (245ms)
  │ ├ Span: HTTP GET /customers/123 (45ms)
  │ └ Span: JDBC INSERT orders (12ms)
  │   Span: Kafka publish OrderCreated (8ms)
  ├ Span: customer-service (45ms)
  │ └ Span: JDBC SELECT customers (10ms)
  └ Span: payment-service (180ms)
      └ Span: HTTP POST to payment gateway (170ms)

METRICS ("what are the current numbers"):
  Counter: order_created_total (monotonically increasing)
  Gauge: jvm_memory_used_bytes (current value)
  Histogram: http_request_duration_ms
    (distribution; enables p50, p95, p99)
  Exported to: Prometheus (scrape) or
               push to OTLP receiver

LOGS ("what happened"):
  OTEL logs include trace_id, span_id fields
  Enables: automatic correlation of logs to traces
  In Grafana: click on a trace span;
    see all log entries generated during that span
  OTEL log bridge: connects existing logging
    frameworks (Logback, Log4j) to OTEL
```

**OTEL ARCHITECTURE:**

```
SERVICE (Java)
  OTEL Java Agent (auto-instrumentation)
  |
  v
  OTLP (gRPC/HTTP) export
  |
  v
  OTEL COLLECTOR (per cluster or per region)
  Receivers: otlp (from services),
             prometheus (scrape exporters)
  Processors: batch (aggregate), tail-sampling
    (only record traces with errors),
    attribute-filter (remove PII)
  Exporters:
    -> Jaeger (traces)
    -> Prometheus/Cortex (metrics)
    -> Elasticsearch/Loki (logs)
  |
  +---> Jaeger UI: trace visualization
  +---> Grafana: metrics dashboards + log search
  +---> Alertmanager: metric-based alerts
```

---

### 🧪 Thought Experiment

**OTEL TAIL SAMPLING: ONLY KEEP WHAT MATTERS**

```
HIGH-VOLUME SYSTEM: 10,000 RPS
  At 100% trace sampling: 10,000 traces/second
  Each trace: ~20 spans, ~2KB each
  Storage: 10,000 * 20 * 2KB = ~400MB/second
  Daily: 34TB of trace data
  Cost: prohibitive
  
  HEAD SAMPLING (at service start):
  Sample 1% of requests randomly
  100 traces/second -> manageable
  Problem: the 1% might not include the failures
    (failures might be 0.1% of requests)
    You're sampling 99% of normal requests
    and potentially MISSING the errors
  
  TAIL SAMPLING (at OTEL Collector):
  Collector: receives ALL spans from all services
  Waits: for complete trace (all spans collected)
  Decision rules:
    - trace has any ERROR span: ALWAYS keep
    - trace duration > 2 seconds: ALWAYS keep
    - trace from /health endpoint: DROP
    - random 1% of remaining: keep
  Result:
    - 100% of error traces kept
    - 100% of slow traces kept
    - 99% of normal traces dropped
    - Storage: 95% reduction
    - Coverage: all failures captured
  
  This is why OTEL Collector is essential:
  only at the collector level can you make
  decisions based on the COMPLETE trace
```

---

### 🧠 Mental Model / Analogy

> OpenTelemetry is like a standardized medical
> diagnostic protocol. Before: each hospital (vendor)
> had its own diagnostic machines (SDK) and report
> formats. Transferring a patient between hospitals:
> all tests re-run (re-instrument) because reports
> are incompatible. OpenTelemetry: an international
> standard diagnostic protocol (like DICOM for
> medical imaging). Any machine (Java/Python/Go
> service) generates standard-format reports
> (OTLP telemetry). Any hospital (Jaeger/Datadog/
> Prometheus) can read them. Patient transfer
> (switching backends): seamless, no re-testing.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
OpenTelemetry: one standard tool to see what
happens inside all your microservices - how long
requests take, where they fail, how many requests
per second. Works with any monitoring dashboard
tool (Grafana, Datadog, etc.).

**Level 2 - Getting started (junior developer):**
Java Spring Boot: add `opentelemetry-javaagent.jar`
to your Docker image. Add JVM args:
`-javaagent:/opt/otel/opentelemetry-javaagent.jar
-Dotel.service.name=order-service
-Dotel.exporter.otlp.endpoint=http://otel-collector:4317`
Deploy OTEL Collector (Helm chart). Deploy Jaeger.
Result: automatic traces visible in Jaeger for
all HTTP requests, JDBC queries, Kafka messages.

**Level 3 - Custom instrumentation (mid-level):**
Beyond auto-instrumentation: add custom business
spans. `Tracer tracer = GlobalOpenTelemetry
.getTracer("order-service")`. Create spans:
`Span span = tracer.spanBuilder("processPayment")
.startSpan()`. Add attributes:
`span.setAttribute("payment.amount", amount)`. Add
events: `span.addEvent("fraud-check-passed")`. The
auto-instrumentation handles HTTP/JDBC; custom
spans capture business operations. Visible in
Jaeger as child spans.

**Level 4 - Operational (senior engineer):**
OTEL Collector pipeline design: use multiple
pipelines for different telemetry types. Processors:
`batch` (reduce export calls), `memory_limiter`
(prevent OOM), `tail_sampling` (only keep
interesting traces), `attributes` (remove PII
fields from spans). Export to multiple backends:
Jaeger for recent traces (7 days), Tempo for
long-term storage (90 days), Prometheus for
metrics (15 days). Resource attributes: add
`k8s.deployment.name`, `k8s.namespace.name` to
all telemetry via K8s Downward API.

**Level 5 - Mastery (principal engineer):**
OTEL Exemplars: link a specific Prometheus metric
data point to the trace that generated it. Grafana:
click on a histogram bucket (e.g., p99 latency
spike at 14:23); see the specific trace that
caused it. Requires Prometheus Exemplars support
and Grafana > 7.5. OTEL Semantic Conventions:
standardized span attribute names (e.g.,
`http.request.method` not `http.method` in OTEL 1.21).
Schema versioning: OTEL specs can change attribute
names between versions; Collector transform
processor can bridge old to new. OTEL Profiles
(experimental): continuous profiling integrated
with traces (see CPU flame graph for a specific
trace span - why did this span take 200ms?).

---

### ⚙️ How It Works (Mechanism)

```dockerfile
# Dockerfile: add OTEL Java agent (zero code change)
FROM eclipse-temurin:21-jre

# Download OTEL Java agent
ADD https://github.com/open-telemetry/opentelemetry-\
java-instrumentation/releases/latest/download/\
opentelemetry-javaagent.jar \
    /opt/otel/opentelemetry-javaagent.jar

COPY target/order-service.jar /app/order-service.jar

ENTRYPOINT ["java",
    # OTEL auto-instrumentation agent
    "-javaagent:/opt/otel/opentelemetry-javaagent.jar",
    # Service identification
    "-Dotel.service.name=order-service",
    # Export to OTEL Collector (gRPC)
    "-Dotel.exporter.otlp.endpoint=http://otel-collector:4317",
    # Enable all signals
    "-Dotel.logs.exporter=otlp",
    "-Dotel.metrics.exporter=otlp",
    "-Dotel.traces.exporter=otlp",
    "-jar", "/app/order-service.jar"]

# What this instruments automatically (zero code):
# - Spring MVC: spans for every HTTP request
# - Spring WebClient/RestTemplate: spans for
#   outbound HTTP calls + trace header injection
# - JDBC: spans for every SQL query
# - Kafka Producer/Consumer: spans for
#   message publish/consume
# - Spring Scheduling: spans for scheduled tasks
```

```yaml
# otel-collector-config.yaml: complete pipeline
receivers:
  otlp:  # receives from services
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
    check_interval: 1s
    limit_mib: 512
  # Tail sampling: keep errors and slow traces
  tail_sampling:
    decision_wait: 10s
    policies:
    - name: errors-policy
      type: status_code
      status_code: {status_codes: [ERROR]}
    - name: slow-traces-policy
      type: latency
      latency: {threshold_ms: 2000}
    - name: probabilistic-1pct
      type: probabilistic
      probabilistic: {sampling_percentage: 1}
  # Remove PII from span attributes
  attributes:
    actions:
    - key: user.email
      action: delete
    - key: http.request.header.authorization
      action: delete

exporters:
  jaeger:
    endpoint: jaeger:14250
    tls: {insecure: true}
  prometheus:
    endpoint: 0.0.0.0:8889
  elasticsearch:
    endpoints: [https://elasticsearch:9200]
    index: otel-logs

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, tail_sampling, batch]
      exporters: [jaeger]
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [prometheus]
    logs:
      receivers: [otlp]
      processors: [memory_limiter, attributes, batch]
      exporters: [elasticsearch]
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
OTEL IN PRODUCTION: REQUEST JOURNEY VISIBILITY

User: places order
  |
  v
  API Gateway: injects W3C traceparent header
    traceparent: 00-<traceId>-<spanId>-01
  |
  v
  order-service (OTEL agent running)
    Creates: root span "POST /orders"
    Calls: customer-service
      OTEL agent: propagates traceparent header
      Creates: child span "HTTP GET /customers/123"
    Calls: JDBC INSERT orders
      OTEL agent: creates child span "db.execute"
    Publishes: Kafka OrderCreated
      OTEL agent: creates child span "kafka.produce"
  |
  v
  OTEL Collector (receives all spans)
    tail_sampling: no errors; 1% random -> kept
    batch processor: aggregate spans
    export to Jaeger
  |
  v
  Jaeger UI:
    Trace: req-abc-123 | 245ms
    order-service: 245ms
      HTTP GET customer-service: 45ms
      db.execute INSERT orders: 12ms
      kafka.produce OrderCreated: 8ms
    customer-service: 45ms
      db.execute SELECT customers: 10ms
  
  INCIDENT: order-service timeout after 30s
    tail_sampling: latency > 2000ms -> ALWAYS keep
    Jaeger: shows which span timed out
    "HTTP GET /payment-gateway/charge": 30000ms
    Root cause: payment gateway timeout
    Visible without any additional logging
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: custom spans without vs with attributes**

```java
// BAD: custom span with no useful attributes
// Visible in Jaeger as a span but no debugging value
Span span = tracer.spanBuilder(
    "processOrder").startSpan();
try (Scope scope = span.makeCurrent()) {
    processOrder(orderId);
} finally {
    span.end();
}
// Jaeger shows: "processOrder" span, 250ms
// But: which orderId? What went wrong? Unknown.
// Not useful for debugging
```

```java
// GOOD: span with semantic attributes and events
Span span = tracer.spanBuilder("processOrder")
    .setAttribute("order.id", orderId)
    .setAttribute("customer.id", customerId)
    .setAttribute("order.total", totalAmount)
    .startSpan();
try (Scope scope = span.makeCurrent()) {
    span.addEvent("validation-started");
    validateOrder(order);
    span.addEvent("payment-initiated",
        Attributes.of(
            AttributeKey.stringKey("payment.method"),
            "CREDIT_CARD"
        ));
    processPayment(order);
    span.addEvent("order-fulfilled");
    span.setStatus(StatusCode.OK);
} catch (InsufficientStockException e) {
    span.setStatus(StatusCode.ERROR, e.getMessage());
    span.recordException(e);
    throw e;
} finally {
    span.end();
}
// Jaeger: "processOrder" span, 250ms
// Attributes: orderId=ord-001, customerId=cust-123,
//   total=99.99
// Events: validation-started, payment-initiated
//   (method=CREDIT_CARD), order-fulfilled
// If error: exception recorded with stack trace
// Debugging: all context available from the span
```

---

### ⚖️ Comparison Table

| Observability Signal | Tool | What It Answers | Storage |
|---|---|---|---|
| **Traces** | OTEL + Jaeger/Tempo | Why is this request slow? Where did it fail? | High (spans per request) |
| **Metrics** | OTEL + Prometheus | How many requests/second? What is p99 latency? | Low (aggregated numbers) |
| **Logs** | OTEL + Elasticsearch/Loki | What exactly happened? What was the error message? | Medium-high |
| **Profiles** | OTEL + Pyroscope (experimental) | Why is CPU high? Which code is slow? | Medium |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| OpenTelemetry replaces Jaeger/Prometheus/Elasticsearch | OpenTelemetry is the COLLECTION and STANDARDIZATION layer. Jaeger, Prometheus, and Elasticsearch are the STORAGE and VISUALIZATION backends. OTEL does not replace them - it makes your application independent of them. You still need backends. OTEL Collector routes telemetry to backends. You can have multiple backends simultaneously. |
| 100% trace sampling is fine in production | At high RPS (1000+), 100% sampling generates enormous amounts of trace data (each trace = 10-50KB). 1000 RPS = 1-50MB/second of trace data = 86-4,320GB/day. Use tail sampling in OTEL Collector: 100% of error/slow traces, 1-5% of normal traces. This captures all actionable traces while dramatically reducing storage costs. |
| OTEL auto-instrumentation is production-ready for all frameworks | OTEL Java agent auto-instrumentation is mature and production-ready for common frameworks (Spring MVC, Kafka, JDBC, gRPC). However: some instrumentation adds non-trivial overhead (e.g., high-cardinality URL patterns causing metric explosion). Always validate: measure CPU/memory overhead with agent vs without agent under your actual load. For most Spring Boot services: agent overhead is < 3-5% CPU, acceptable. |

---

### 🚨 Failure Modes & Diagnosis

**Trace not connecting across services (spans orphaned)**

**Symptom:**
Jaeger shows two separate traces for what should
be one request: order-service trace and customer-service
trace are disconnected. They have different trace
IDs. Cannot see the complete request journey.

**Root Cause:**
The `traceparent` W3C header is not being propagated
from order-service to customer-service. Possible
causes:
1. order-service uses a custom HTTP client
   (not auto-instrumented): header not added.
2. API gateway strips non-standard headers
   (some gateways are configured to remove
   headers starting with `x-` or non-standard).
3. OTEL Java agent version mismatch: different
   versions use different trace context formats
   (B3 vs W3C). If order-service sends B3 and
   customer-service expects W3C: disconnected.

**Diagnosis:**
```bash
# Check what headers are sent by order-service
# Deploy a simple echo service that returns all
# incoming headers:
kubectl run echo --image=mendhak/http-https-echo

# Make order-service call the echo service:
# Check if traceparent header appears in request
# Expected: traceparent: 00-<32-hex>-<16-hex>-01

# Check OTEL propagator config:
# -Dotel.propagators=tracecontext,baggage
# (default for W3C)
# If: -Dotel.propagators=b3 and downstream
# expects W3C -> disconnected
```

**Fix:**
1. Ensure all services use same propagation format.
2. Default OTEL: W3C TraceContext (`tracecontext`).
3. If mixed (some services still use B3):
   configure OTEL to accept both:
   `-Dotel.propagators=tracecontext,b3,b3multi`
4. Check API gateway: ensure `traceparent` header
   is not stripped.

---

### 🔗 Related Keywords

**Foundation this builds on:**
- `Distributed Logging` - logs correlated with
  OTEL trace IDs for complete observability
- `Cross-Cutting Concerns` - OpenTelemetry is
  the observability cross-cutting concern solution

**Infrastructure:**
- `Sidecar Pattern` - OTEL Collector can run as
  sidecar alongside each service pod

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ SIGNALS      │ Traces (spans), Metrics, Logs (unified)  │
│              │ W3C traceparent: standard propagation    │
├──────────────┼──────────────────────────────────────────┤
│ JAVA AGENT   │ -javaagent:otel-agent.jar = zero code    │
│              │ Auto-instruments Spring/JDBC/Kafka/gRPC  │
├──────────────┼──────────────────────────────────────────┤
│ COLLECTOR    │ Receives all telemetry -> tail sampling  │
│              │ -> export to Jaeger, Prometheus, Loki    │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Vendor-neutral: one agent, any backend; │
│              │  traces+metrics+logs, zero code change"  │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. OTEL = vendor-neutral standard for traces,
   metrics, and logs. One SDK, any backend.
2. Java agent: `-javaagent:otel-agent.jar` = zero
   code auto-instrumentation for Spring, JDBC,
   Kafka. Most valuable observability ROI.
3. OTEL Collector: central pipeline. Tail sampling:
   100% of errors/slow traces, 1% of normal.
   Export to Jaeger (traces) + Prometheus (metrics)
   + Loki (logs).

**Interview one-liner:**
"OpenTelemetry: CNCF standard for vendor-neutral
observability. Three signals: traces (spans with
W3C traceparent propagation), metrics (counters,
gauges, histograms), logs (correlated with trace
IDs). Java: -javaagent:opentelemetry-javaagent.jar
= zero-code auto-instrumentation for Spring MVC,
JDBC, Kafka, gRPC. OTEL Collector: receives all
telemetry, applies tail sampling (keep errors +
slow traces, drop 99% of normal), exports to
Jaeger/Prometheus/Elasticsearch. Benefit: switch
from Jaeger to Tempo, or add Datadog - zero service
code changes, only Collector config changes."

---

### 💡 The Surprising Truth

The hardest part of OpenTelemetry is not the
technical setup - it's CARDINALITY. OTEL makes
it trivially easy to add custom metric attributes
(labels). Example: a developer adds a metric
`http_requests_total` with attributes including
`user_id` (to track per-user request rates). There
are 10 million users = 10 million unique attribute
combinations = 10 million time series in Prometheus.
Prometheus: crashes (out of memory). This is the
"cardinality explosion" problem. Rule: metric
attributes should have LOW cardinality (< 1000
unique values): `http.method`, `http.status_code`,
`service.name`. Never: `user.id`, `order.id`,
`request.id`. For high-cardinality data: use
traces (span attributes), not metrics.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **SETUP** Configure OTEL Java agent for a Spring
   Boot service: Dockerfile changes, JVM args,
   service name, OTEL Collector endpoint. Verify:
   traces appear in Jaeger, metrics in Prometheus
   `/metrics` endpoint.
2. **CUSTOM SPANS** Implement a custom business
   span for a "payment processing" operation:
   span builder, set attributes (amount, currency,
   payment method), add events (fraud-check-passed,
   payment-authorized), record exceptions on error.
3. **COLLECTOR** Write an OTEL Collector config
   with: OTLP receiver (gRPC), tail sampling
   (keep errors + latency > 2s + 1% random),
   attribute processor (remove user.email), Jaeger
   exporter (traces), Prometheus exporter (metrics).
4. **DEBUGGING** Diagnose disconnected traces:
   check propagator config (W3C vs B3), check
   API gateway header stripping, verify HTTP client
   auto-instrumentation is working.
5. **CARDINALITY** Identify which metric attributes
   are high-cardinality and should NOT be added
   (user.id, order.id), vs low-cardinality that
   are safe (service.name, http.method, http.status_code).
   Design a metric schema for an order-service
   that avoids cardinality explosion.

---

### 🧠 Think About This Before We Continue

**Q1.** You are deploying OpenTelemetry across 40
microservices in 3 languages (Java, Python, Node.js).
All should send traces to one OTEL Collector, which
routes to Jaeger (traces), Prometheus (metrics),
and Loki (logs). Design the deployment architecture:
should the OTEL Collector be a per-node DaemonSet,
a per-namespace Deployment, or a cluster-wide
centralized service? What are the failure modes
if the Collector becomes unavailable?

**Q2.** Prometheus is reporting that a service's
time-series count has grown from 500 to 500,000
in two weeks. The team recently started using
OpenTelemetry for metrics. Diagnose: what caused
the cardinality explosion? Write a PromQL query
to identify which metric and which label set has
the highest cardinality. How do you fix it without
breaking existing dashboards?

**Q3.** Your organization is currently using Jaeger
(traces) and Prometheus/Grafana (metrics) separately,
with different trace context propagation (some
services use Zipkin B3, some use Jaeger native).
You want to migrate to a unified OpenTelemetry
setup. Design the migration plan: what changes
in what order, how do you handle the period when
some services are on OTEL and some are not (mixed
propagation formats), and how do you validate
the migration is successful?