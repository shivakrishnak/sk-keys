---
id: OBS-018
title: "Jaeger / Zipkin -- Distributed Tracing"
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★☆
depends_on: OBS-008, OBS-017
used_by: OBS-009
related: OBS-008, OBS-017, OBS-015, OBS-016
tags:
  - observability
  - tracing
  - devops
  - pattern
  - intermediate
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Mastery"
nav_order: 18
permalink: /technical-mastery/obs/jaeger-zipkin-distributed-tracing/
---

⚡ TL;DR - Jaeger and Zipkin are the two dominant
open-source distributed tracing backends. Both store
and visualise traces collected from services. Jaeger
(CNCF-graduated, Uber-origin) is the current standard;
Zipkin (Twitter-origin) is the predecessor still widely
deployed. Both accept OpenTelemetry data via OTLP.

| #018            | Category: Observability & SRE                           | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------ | :-------------- |
| **Depends on:** | Distributed Tracing Fundamentals, OpenTelemetry         |                 |
| **Used by:**    | Alerting Fundamentals                                   |                 |
| **Related:**    | Distributed Tracing, OpenTelemetry, Prometheus, Grafana |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A user reports "checkout is slow sometimes." The SRE
on-call knows the checkout API calls: authentication
service, inventory service, payment gateway, and a
database. The P99 latency is 3,400ms. Normal is 180ms.
Without distributed tracing, the engineer logs into
each service in sequence, grepping for the request ID,
computing time differences manually. The checkout API
log shows: request received at 14:23:01.100, response
sent at 14:23:04.500. Which service caused the 3.4-second
delay? Unknown. The engineer checks each service. 45
minutes later: the payment gateway latency log shows
a 3.2-second call. Could have been found in 30 seconds
with a distributed trace.

**THE INVENTION:**
Zipkin was open-sourced by Twitter in 2012, implementing
Google Dapper's distributed tracing architecture. It
introduced the trace/span model and context propagation.
Jaeger was open-sourced by Uber in 2017 with a more
scalable architecture (Cassandra/Elasticsearch backends,
sampling strategies). Both: given a trace ID, show
the full waterfall of every service call in a request,
with timing, status, and tags - answering "which
service is slow?" in seconds.

---

### 📘 Textbook Definition

**Jaeger** is a CNCF-graduated distributed tracing
system. It receives span data from instrumented
services (via OTel/OTLP, Jaeger client, or Zipkin
protocol), stores traces in a backend (Elasticsearch,
Cassandra, or in-memory for dev), and provides a
UI for trace search, waterfall visualisation, and
service dependency graphs.

**Zipkin** is a distributed tracing system
(originally by Twitter). It uses a compatible but
different data model (Zipkin format vs Jaeger/OTLP
format). Both accept Zipkin-format spans from
compatible SDKs and modern OTel exporters.

**Shared core concepts:**

- **Trace:** the complete record of one request
  through all services. One trace_id.
- **Span:** one unit of work within a trace (one
  service call, one DB query). Has duration, status,
  and key-value tags.
- **Service dependency graph:** auto-generated from
  traces - shows which services call which services
  and how often.
- **Root cause isolation:** use the trace waterfall
  to see which span consumed most of the total duration.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Jaeger (or Zipkin) answers "which service slowed down
this user's request?" by storing the timing of every
hop in a request and visualising it as a waterfall.

> Think of tracking a package through a delivery
> network. The tracking system records: picked up
> at 9:00 AM (origin warehouse), arrived sorting
> facility at 11:30 AM, departed sorting at 2:00 PM,
> in transit 6 hours, delivered 8:00 PM. If the
> package is late, you can pinpoint: the delay was
> at the sorting facility (2 hours vs expected 30 min).
>
> Jaeger does this for requests. Each service is a
> "sorting facility." Each hop is a span. The "delay
> at sorting" is the slow span. The trace ID is the
> tracking number.

---

### 🔩 First Principles Explanation

**THE TRACE WATERFALL MODEL:**

```
Trace: checkout-request-abc123
Total duration: 3,400ms

checkout-api        [=======================] 3,400ms
  auth-service       [=]                       120ms
  inventory-service     [==]                   210ms
  payment-gateway          [==================] 3,050ms  ←
    CULPRIT
    stripe-api              [================] 2,990ms
  db-write                                    [=]   80ms

Root cause: payment-gateway spent 3.05s waiting for
stripe-api. stripe-api internal: 2.99s of that was
a timeout + retry to stripe's API.
```

**JAEGER ARCHITECTURE:**

```
[Application services] → OTel Collector → OTLP
        ↓
[Jaeger Collector]
  Receives spans via OTLP/gRPC
  Validates and normalises
  Writes to storage backend
        ↓
[Storage Backend]
  Development: in-memory (lost on restart)
  Production: Elasticsearch or Cassandra
  Search index: trace_id → spans, service_name, tags
        ↓
[Jaeger Query Service]
  REST API: search traces by service, operation, tags,
  duration range, start time
  Powers the Jaeger UI
        ↓
[Jaeger UI]
  Trace search: find traces for checkout-api
    where duration > 1000ms AND status=error
  Trace view: waterfall + span details
  Service map: dependency graph
```

**THE ZIPKIN FORMAT vs JAEGER FORMAT:**

```
Zipkin span format:
{
  traceId: "abc123",
  id: "span001",
  parentId: "root001",
  name: "checkout",
  timestamp: 1681234567890000,  # microseconds
  duration: 3400000,            # microseconds
  localEndpoint: {
    serviceName: "checkout-api"
  },
  tags: {"http.status_code": "200"}
}

OTel/Jaeger format (OTLP):
{
  trace_id: bytes,
  span_id: bytes,
  parent_span_id: bytes,
  name: "checkout",
  start_time_unix_nano: 1681234567890000000,
  end_time_unix_nano: 1681234571290000000,
  status: {code: OK},
  attributes: [{key: "http.status_code", value: 200}]
}
```

Modern Jaeger accepts both formats. OTel Collector
can translate between them.

---

### 🧪 Thought Experiment

**THE DEBUGGING EXERCISE:**

A user reports checkout is slow. You have Jaeger.
Your investigation:

**Step 1: Find the trace**
Jaeger UI: Service = checkout-api, Operation = POST /checkout,
Duration > 1000ms, Last 1 hour → finds 47 slow traces.

**Step 2: Open one trace (3,400ms)**
Waterfall shows:

```
checkout-api: 3,400ms
  auth-service: 120ms ← normal
  inventory: 210ms ← normal
  payment-gateway: 3,050ms ← SLOW
    stripe-http-call: 2,990ms ← VERY SLOW
      [span tags]:
        http.url=https://api.stripe.com/v1/charges
                  http.status_code=200 (success!)
                  retry_count=1 ← there was a retry
```

**Step 3: Understand the retry**
The stripe HTTP call shows `retry_count=1`. The first
attempt timed out after 1,500ms. The retry succeeded
after 1,490ms. Total: 2,990ms instead of normal 500ms.

**Step 4: Root cause**
Stripe API response time spiked. The payment gateway
is configured to retry once with a 1,500ms timeout.
The mitigation: check Stripe status page (confirmed
regional degradation). Action: add circuit breaker
to payment gateway so that if Stripe is degraded,
we fail fast rather than holding connections open
for 3 seconds.

**Without Jaeger:** this investigation takes 30-60
minutes. With Jaeger: 4 minutes.

---

### 🧠 Mental Model / Analogy

> An X-ray or MRI of a distributed request. When a
> patient comes in with unexplained symptoms
> (slow/failed request), the doctor (SRE) could
> examine each organ (service) separately - time-
> consuming and inconclusive. Or they can order an
> MRI (Jaeger trace) that shows the complete internal
> picture: every organ, every connection, every
> timing - all in one view.
>
> The MRI does not change the patient (trace IDs
> are just metadata, minimal overhead). It reveals
> what is happening internally across the whole
> system at once. The radiologist (on-call engineer)
> can pinpoint the problem - the kidney (payment
> gateway) is enlarged (slow) and specifically the
> renal artery (Stripe HTTP connection) is partially
> blocked (timing out and retrying).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone):**
Jaeger shows you a timeline of every step a request
took through your services, with the time for each
step. When something is slow, you can see which step
was the bottleneck.

**Level 2 - How to use it (junior):**
In Jaeger UI: select the service, select the operation,
filter by duration > N milliseconds. Open a slow trace.
Look at the waterfall - find the widest bar. That is
the slow span. Look at its tags for more context.

**Level 3 - How it works (mid-level):**
Services instrument with OTel SDK (or Jaeger client).
Each span includes: operation name, start time,
duration, tags, parent_span_id. OTel Collector
exports spans to Jaeger Collector via OTLP. Jaeger
stores spans indexed by trace_id, service_name,
operation_name, duration, and tags. The Jaeger UI
queries this index.

**Level 4 - Production operations (senior):**
Sampling strategy is the critical production decision.
100% sampling generates too much data at high traffic.
Head-based sampling (decide at trace start): simple
but cannot selectively keep error traces. Tail-based
sampling (in OTel Collector): keeps all error traces
and a percentage of success traces. Jaeger with
Elasticsearch backend: index management (ILM policies),
retention (typically 7-14 days for traces). Trace
context in logs: add trace_id and span_id to every
log line so you can jump from log to trace.

**Level 5 - Platform (staff):**
Jaeger vs alternatives: Grafana Tempo (OTel-native,
object storage backend, lower cost than Elasticsearch),
Honeycomb (traces + arbitrary event columns, columnar
storage), AWS X-Ray (AWS-native, limited OTel support).
Trace-based testing: use traces to assert that a
specific service path was taken in an integration test
(no mocking required). Service dependency graph analysis
for architecture review. Flame graph visualisation for
performance profiling.

---

### ⚙️ How It Works (Mechanism)

**JAEGER COMPONENTS (PRODUCTION):**

```
[Kubernetes namespace: observability]

jaeger-collector (StatefulSet, 3 replicas)
  - Receives spans via OTLP (port 4317) or
    Jaeger protocol (port 14250)
  - Validates and normalises span data
  - Writes to Elasticsearch in batches

jaeger-query (Deployment, 2 replicas)
  - REST API and Jaeger UI
  - Queries Elasticsearch for trace search
  - Reconstructs trace trees from span index

elasticsearch (or Cassandra)
  - Index: jaeger-service-YYYY-MM-DD
  - Index: jaeger-span-YYYY-MM-DD
  - ILM policy: delete after 14 days

jaeger-ui
  - Built into jaeger-query component
  - React SPA served on port 16686
```

**ELASTICSEARCH INDEX STRUCTURE:**

```json
// jaeger-span-2024-04-15 document
{
  "traceID": "abc123def456",
  "spanID": "span001",
  "operationName": "checkout.process_payment",
  "process": {
    "serviceName": "checkout-api",
    "tags": [
      { "key": "hostname", "value": "pod-xyz" },
      { "key": "version", "value": "1.47.2" }
    ]
  },
  "startTime": 1681234567890000,
  "duration": 3400000,
  "tags": [
    { "key": "http.status_code", "value": "200" },
    { "key": "error", "value": "false" }
  ]
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**INCIDENT TRACE INVESTIGATION:**

```
[14:23:01] User reports: checkout 10x slower than normal
        ↓
[14:24] On-call opens Jaeger UI
  Search: service=checkout-api, duration>1000ms, last 15min
  Result: 47 slow traces in 15 minutes
        ↓
[14:25] Opens trace for duration=3,400ms
  Waterfall visible:
    checkout-api: 3,400ms
      payment-gateway: 3,050ms ← 90% of total time
  Clicks payment-gateway span
  Tags: retry_count=1, http.status_code=200
        ↓
[14:26] Opens payment-gateway service view in Jaeger
  Service map: payment-gateway → stripe-api → [external]
        ↓
[14:27] Checks payment-gateway metrics in Grafana
  payment_gateway_p99 latency: 3,200ms (normal: 400ms)
  stripe_api_timeout_total: 42 in last 15min (normal: 0)
        ↓
[14:28] Root cause: Stripe API degradation
  Action: enable payment fallback (PayPal)
  Timeline: checkout restored to normal in 3 minutes
  Post-mortem: add circuit breaker, Stripe status alert
```

---

### 💻 Code Example

**Example 1 - BAD: Log-only debugging (no traces):**

```java
// BAD: cannot correlate logs across services
// Each service logs independently with no shared ID
log.info("Payment processing started for order " + orderId);
// In payment-gateway (different service, different log):
log.info("Stripe charge initiated for amount " + amount);
// At 3 AM trying to find what happened for order 12345:
// grep through 3 different service log files manually
// Cannot determine timing or which service was slow
```

**Example 2 - GOOD: OTel + Jaeger trace linking:**

```java
// GOOD: span with trace context propagated to downstream
// All spans linked in Jaeger by trace_id

// checkout-api
Span span = tracer.spanBuilder("checkout.process")
    .startSpan();
try (var scope = span.makeCurrent()) {
    String traceId = span.getSpanContext().getTraceId();
    // Add trace_id to logs for log-trace correlation
    MDC.put("trace_id", traceId);
    log.info("Processing checkout for order {}", orderId);

    // HTTP call to payment-gateway:
    // OTel injects traceparent header automatically
    // payment-gateway creates child span with same trace_id
    paymentGatewayClient.charge(orderId, amount);
} finally {
    span.end();
    MDC.clear();
}

// In Jaeger: search by trace_id → see full waterfall
// In ELK: search by trace_id → see correlated log lines
// Both views linked to the same request lifecycle
```

**Example 3 - Jaeger query API:**

```bash
# Search traces via Jaeger API (not just UI)
# Useful for automated analysis or CI/CD trace assertions

# Find all error traces for checkout-api in last 1h
curl "http://jaeger:16686/api/traces?service=checkout-api&tags=%7B%22error%22%3A%22true%22%7D&lookback=1h&limit=20"

# Get specific trace by ID
curl "http://jaeger:16686/api/traces/abc123def456"

# Get service dependency graph
curl "http://jaeger:16686/api/dependencies?endTs=1681237600000&lookback=86400000"
```

**Example 4 - Jaeger with Helm (production deployment):**

```yaml
# values.yaml for jaeger Helm chart
jaeger:
  collector:
    replicaCount: 3
    resources:
      requests:
        memory: "512Mi"
        cpu: "250m"
      limits:
        memory: "1Gi"
        cpu: "500m"
  query:
    replicaCount: 2

storage:
  type: elasticsearch
  elasticsearch:
    host: elasticsearch.observability.svc.cluster.local
    port: 9200
    indexPrefix: jaeger

# Sampling: use remote sampling config
# (served to agents via Jaeger remote sampling API)
sampling:
  strategies:
    defaultSamplingProbability: 0.05 # 5% base rate
    perOperationSamplingStrategies:
      - operation: "checkout.process"
        probabilisticSampling:
          samplingRate: 0.10 # 10% for critical path
```

---

### ⚖️ Comparison Table

| Feature         | Jaeger                        | Zipkin                   | Grafana Tempo            | AWS X-Ray            |
| --------------- | ----------------------------- | ------------------------ | ------------------------ | -------------------- |
| Origin          | Uber (2017), CNCF-graduated   | Twitter (2012)           | Grafana Labs             | AWS                  |
| Storage backend | ES, Cassandra, in-mem         | MySQL, ES, Cassandra     | Object storage (S3)      | AWS managed          |
| OTel native     | Yes (OTLP receiver)           | Via exporter/translation | Yes (OTel-first)         | Partial              |
| UI quality      | Strong, mature                | Good, simpler            | Integrated with Grafana  | AWS console          |
| Scalability     | High (ES cluster)             | Medium                   | Very high (object store) | Managed              |
| Cost model      | Self-hosted + storage         | Self-hosted              | Object storage costs     | AWS pricing          |
| Best for        | Kubernetes-native, CNCF stack | Legacy compatibility     | Grafana-native stack     | AWS-only deployments |

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                                                                                                                            |
| ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Jaeger replaces logging"                   | Traces show timing and call paths. Logs provide the detailed context (error messages, stack traces, request payloads). They complement each other. Link them via trace_id in log fields.                                                           |
| "100% trace sampling is fine"               | At high traffic (1,000 rps), 100% sampling generates 1,000 traces/second. At 1KB/trace average, this is 86GB/day. Use 5-10% sampling for success traces, 100% for error traces.                                                                    |
| "Jaeger and Zipkin are interchangeable"     | They use different wire formats by default. Zipkin format uses different field names and timestamp units. OTel Collector handles translation, but verify compatibility before migrating between them.                                              |
| "Distributed tracing is only for debugging" | Traces also enable: service dependency mapping (who calls whom?), P99 latency attribution (which service contributes most to tail latency?), and architectural drift detection (is service A still calling service B directly when it shouldn't?). |
| "Trace data is not sensitive"               | Trace attributes can contain sensitive data: user IDs, payment amounts, session tokens, email addresses. Implement attribute scrubbing (OTel Collector processor) to remove PII from spans before storage.                                         |

---

### 🚨 Failure Modes & Diagnosis

**High trace volume causing Elasticsearch cluster to degrade**

**Symptom:**
Jaeger search is very slow (30-60 second response).
Elasticsearch cluster shows high CPU and heap pressure.
Trace ingestion is falling behind (buffer growing
in Jaeger Collector). Some traces are being dropped.

**Root Cause:**
Sampling rate is 100% (all traces stored). At 500 rps,
this generates 500 traces/second. Trace storage is
consuming Elasticsearch resources needed for other
indices (application logs).

**Diagnostic:**

```bash
# Check Elasticsearch index sizes
curl http://elasticsearch:9200/_cat/indices/jaeger*?v&h=index,
    docs.count,store.size

# Check Jaeger Collector drop rate
curl http://jaeger-collector:14269/metrics | grep dropped

# Check ES cluster health
curl http://elasticsearch:9200/_cluster/health
```

**Fix:**
Implement tail-based sampling in OTel Collector.
Reduce success trace sampling to 5%, keep 100%
of error traces:

```yaml
# In OTel Collector config
processors:
  tail_sampling:
    policies:
      - name: errors
        type: status_code
        status_code: { status_codes: [ERROR] }
      - name: success-sample
        type: rate_limiting
        rate_limiting: { spans_per_second: 25 } # ~5% at 500rps
```

---

**Disconnected traces (spans not linked across services)**

**Symptom:**
In Jaeger, each service shows its own root spans.
A checkout request produces 4 separate traces (one
per service) instead of one linked trace. Service
dependency graph shows no connections.

**Root Cause:**
Context propagation is not working. The `traceparent`
header is not being injected into outgoing HTTP
requests or is being stripped by a load balancer
or API gateway.

**Diagnostic:**

```bash
# Check if traceparent header is present in requests
# Enable debug logging in OTel SDK
OTEL_LOG_LEVEL=debug java -jar checkout-api.jar 2>&1 \
  | grep "traceparent"

# Expected: "Injecting traceparent: 00-abc123..."
# If missing: OTel HTTP instrumentation not loaded
```

**Fix:**

- Verify OTel HTTP instrumentation library is on
  the classpath (for Java: `opentelemetry-instrumentation-okhttp`)
- Check API gateway configuration: some gateways
  strip unknown headers (add `traceparent` to allowed
  headers whitelist)
- Verify W3C propagator is registered globally at
  application startup

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Distributed Tracing Fundamentals` - the trace/span
  data model that Jaeger and Zipkin implement
- `OpenTelemetry` - the standard instrumentation layer
  that feeds data into Jaeger/Zipkin backends

**Builds On This (learn these next):**

- `Alerting Fundamentals` - trace data can be used
  to correlate with alerts (link alert to the trace
  that caused it via trace_id)
- `ELK / EFK Stack` - integrate trace_id into log
  fields to enable log-to-trace correlation

**Alternatives / Comparisons:**

- `Grafana Tempo` - newer OTel-native backend using
  object storage. Lower cost than Jaeger + ES.
  Integrated with Grafana natively.
- `AWS X-Ray` - AWS-managed tracing. Best for AWS-only
  workloads. Limited OTel support compared to Jaeger.
- `Honeycomb` - SaaS tracing with columnar storage.
  Better query performance, higher cost per event.

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Distributed trace backend: stores and    │
│              │ visualises traces as waterfalls          │
├──────────────┼──────────────────────────────────────────┤
│ JAEGER       │ CNCF-graduated, ES/Cassandra storage,    │
│              │ mature UI, OTLP native                   │
├──────────────┼──────────────────────────────────────────┤
│ ZIPKIN       │ Older, wider library support, compatible │
│              │ format (OTel can translate)              │
├──────────────┼──────────────────────────────────────────┤
│ KEY USE      │ "Which service caused this latency?"     │
│              │ Find widest span in waterfall = culprit  │
├──────────────┼──────────────────────────────────────────┤
│ SAMPLING     │ Never 100% in production (storage cost)  │
│              │ Always 100% for error traces             │
│              │ 5-10% for success traces                 │
├──────────────┼──────────────────────────────────────────┤
│ STORAGE      │ Dev: in-memory. Prod: Elasticsearch      │
│              │ Retention: 7-14 days typical             │
├──────────────┼──────────────────────────────────────────┤
│ LOG-TRACE    │ Add trace_id to every log line (MDC)     │
│ CORRELATION  │ Jump from log in Kibana to trace in Jaege│
├──────────────┼──────────────────────────────────────────┤
│ COMMON BUG   │ Disconnected traces = context propagation│
│              │ not working (traceparent header missing) │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ OTel Collector → Grafana Tempo → ELK     │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Add correlation IDs at every system boundary. The
trace_id in distributed tracing is an instance of
a broader principle: any complex multi-step operation
needs a correlation ID that is visible in every
log, every metric, and every trace related to that
operation. This applies to: batch job run IDs (add
to every log line in the batch), user session IDs
(log on every API request), transaction IDs (log
on every step of a financial transaction). Without
correlation IDs, debugging complex operations means
manually correlating timestamps across multiple
disconnected log files.

---

### 💡 The Surprising Truth

The most counterintuitive tracing insight: the cost
of distributed tracing is not the instrumentation -
it is the storage and sampling decision. Instrumenting
a service with OTel adds less than 1% overhead to
request latency. But storing 100% of traces at 500
requests/second for 14 days requires 1.2TB of
Elasticsearch storage. The engineering discipline is
not "add spans to your code" - it is "design a
sampling strategy that gives you full coverage of
interesting events (errors, slow requests) while
limiting storage costs for routine traffic."

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[DEBUG]** Given a slow user request with a trace
   ID, use Jaeger UI to find the slowest span, identify
   the service responsible, and read the span tags to
   understand the root cause.
2. **[CONFIGURE]** Deploy Jaeger in Kubernetes with
   Elasticsearch backend, configure the OTel Collector
   to export to Jaeger, and verify traces appear in
   the Jaeger UI.
3. **[DESIGN]** Design a sampling strategy for a service
   handling 1,000 rps: define the head vs tail sampling
   policy, the percentage for success traces, the
   retention period, and the estimated storage cost.
4. **[CORRELATE]** Set up trace-log correlation: add
   trace_id and span_id to every log line using MDC
   in Java (or equivalent), and demonstrate jumping
   from a log in Kibana to the corresponding trace
   in Jaeger.
5. **[COMPARE]** Explain to a team evaluating tracing
   backends when you would choose Jaeger vs Grafana
   Tempo vs Honeycomb, with specific criteria for
   each choice.

---

### 🧠 Think About This Before We Continue

**Q1.** Your checkout service is at 500 rps with an
average span count of 15 spans per trace. Each span
is approximately 1KB. You want to keep traces in
Jaeger for 14 days. Calculate the required storage
assuming: (a) 100% sampling, (b) 5% success + 100%
error sampling (error rate = 1%). What is the storage
difference between the two strategies?
_Hint: (a) 500 rps x 15 spans x 1KB x 86400 seconds
x 14 days = 9.07TB. (b) Success traces: 495 rps x 5%
= 24.75 rps. Error traces: 5 rps x 100%. Total: 29.75
rps x 15 spans x 1KB x 86400 x 14 = 0.541TB. Savings:
94% storage reduction with intelligent sampling._

**Q2.** You set up Jaeger and instrument 10 microservices.
After a week, you notice that 30% of traces are
incomplete - some services have spans but they are
not linked to the parent trace. You suspect context
propagation is failing intermittently. What are the
three most common causes of intermittent propagation
failures? How do you diagnose each one?
_Hint: (1) Load balancer stripping X- headers but
not removing traceparent (check if pattern correlates
with LB vs direct routing). (2) Async processing
breaking context (if request goes through a queue,
the context must be explicitly serialised into the
message and extracted on the consumer side). (3)
One service in the chain using old SDK without OTel
(check which services are NOT appearing in partial
traces to find the non-instrumented service)._

**Q3 (TYPE G):** Your company has 100 microservices
deployed across 3 AWS regions. Jaeger is deployed
per-region (3 Jaeger instances). A user reports a slow
checkout. The checkout service is in us-east-1. It
calls a recommendation service in eu-west-1 and a
payment service in ap-southeast-1. The trace is split
across 3 regional Jaeger instances. Design a cross-
region tracing architecture that allows the on-call
engineer to see the complete trace for a cross-region
request in a single view.
_Hint: Options: (1) Central Jaeger gateway that all
regions export to (high cross-region data transfer
cost). (2) Use trace_id as the key - engineer opens
regional Jaeger instances separately but searches by
the same trace_id. (3) Grafana Tempo with S3 backend -
all regions write to the same S3 bucket, one global
Tempo query. (4) Grafana with multiple Jaeger data
sources - federation at the Grafana layer. Preferred:
option 3 (Tempo with global object storage) for new
deployments; option 4 (Grafana federation) for existing
Jaeger deployments without migration._

---

### 🎯 Interview Deep-Dive

**Q1: "What is distributed tracing and when would
you use it over logging?"**
_Why they ask:_ Tests understanding of when to use
each observability pillar.
_Strong answer includes:_

- Distributed tracing shows the timing and path of
  a request through multiple services - which service
  is slow, which call chain is responsible
- Logging shows the detailed context of what happened
  within one service - the error message, stack trace,
  variable values
- Use tracing for: cross-service latency attribution,
  understanding call paths, service dependency mapping
- Use logging for: error diagnosis within a service,
  audit trails, business events
- Best practice: use both together - trace_id in log
  fields enables jumping from a log to the trace

**Q2: "How would you set up distributed tracing for
a new microservice architecture?"**
_Why they ask:_ Tests end-to-end tracing setup knowledge.
_Strong answer includes:_

- Choose the instrumentation standard: OTel (vendor-
  neutral, recommended for new projects)
- Add OTel SDK with auto-instrumentation for HTTP
  framework and database driver
- Deploy OTel Collector (sidecar per pod or centralised
  gateway) to export to Jaeger
- Define sampling strategy: 100% in dev/staging,
  5-10% success + 100% error in production
- Add trace_id to log lines for correlation
- Set up Elasticsearch backend for Jaeger with 14-day
  retention policy
- Link runbooks to Jaeger search URLs filtered to
  the specific service/operation

**Q3: "A trace shows that Service B is slow, but
when you check Service B's metrics directly, latency
is normal. How do you explain this?"**
_Why they ask:_ Tests ability to think through tracing
edge cases.
_Strong answer includes:_

- This is typically a network latency problem, not
  a Service B processing problem
- The trace measures time from when Service A made
  the call to when Service A received the response
  (includes: network transit to B, B's queue wait,
  B's processing, network transit back)
- Service B's own metrics measure only its internal
  processing time (not network or queue wait)
- Diagnosis: check if the gap between Service A's
  span start and Service B's span start is large
  (that gap is pure network/queue time)
- If Service B span shows normal processing but the
  parent span shows long duration, the delay is in
  the network or load balancer between the two services
