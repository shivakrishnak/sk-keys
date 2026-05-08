---
id: DST-069
title: Distributed Tracing Architecture
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on:
used_by:
related:
tags:
  - dst
  - advanced
  - architecture
  - bestpractice
status: draft
version: 1
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 69
permalink: /dst/distributed-tracing-architecture/
---

# DST-069 - Distributed Tracing Architecture

⚡ TL;DR - Distributed tracing architecture stitches together spans from every service in a request path into a single timeline — it is the only tool that answers "why was this request slow?" in a microservices system.

| DST-069         | Category: Distributed Systems      | Difficulty: ★★★ |
| :-------------- | :--------------------------------- | :-------------- |
| **Depends on:** | DST-049, DST-050, DST-051          |                 |
| **Used by:**    | DST-066                            |                 |
| **Related:**    | DST-049, DST-050, DST-051, DST-052 |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A request fails in a microservices system that spans
12 services. Engineers check logs in service A: nothing.
Service B: nothing. They can't correlate which log
lines belong to the same request across services. They
can't see the request's full path. Diagnosing P99 latency
spikes takes days, not minutes.

**THE BREAKING POINT:**
Uber's 2018 case study: their ride-sharing backend had
2,200+ microservices. A P99 latency spike in the booking
flow affected 0.1% of rides. Without distributed tracing,
finding which of the 2,200 services was responsible
was effectively impossible. With distributed tracing
(Jaeger), the slow service was identified in 3 minutes.

**THE INVENTION MOMENT:**
Google Dapper (2010): internal distributed tracing system.
Twitter Zipkin (2012): open-source Dapper-inspired system.
OpenTracing (2016): vendor-neutral API. OpenCensus (2018).
OpenTelemetry (2019): merger of OpenTracing + OpenCensus;
now the industry standard.

**EVOLUTION:**
Modern distributed tracing: OpenTelemetry SDK (vendor-neutral
instrumentation) → collector (routing, sampling) → backend
(Jaeger, Tempo, Honeycomb, Datadog). W3C Trace Context
standard (2021) ensures trace propagation across vendors.

---

### 📘 Textbook Definition

**Distributed tracing** is a method for tracking a request
as it flows through multiple services. A **trace** is a
collection of **spans** — each span represents work done
in one service for that request. Spans are linked by
a shared **trace ID** (propagated in HTTP headers) and
a **parent span ID** (forms the tree structure). The
trace shows the complete request path, timing of each
service, and causal relationships. **Sampling** is the
strategy for deciding which traces to capture (head-based,
tail-based, or adaptive).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Distributed tracing tracks one request across all services so you can see exactly where time was spent and where errors occurred.

**One analogy:**

> Distributed tracing is like a flight itinerary for
> a request. Without it, you know the passenger (request)
> departed and arrived, but you don't know which
> connecting flights they took, which leg was delayed,
> or which airline lost the bag. The trace is the full
> itinerary: every leg, every handoff, every delay.

**One insight:**
A trace is a timeline built from fragments collected
across services; each service contributes its fragment.
The challenge is: (1) propagating the trace ID across
all service boundaries, and (2) sampling intelligently
so storage is finite but interesting traces are captured.

---

### 🔩 First Principles Explanation

**CORE COMPONENTS:**

```
Trace ID: UUID; unique per request; propagated in headers
  W3C traceparent: 00-{traceId}-{spanId}-{flags}

Span: unit of work within a service
  Fields: traceId, spanId, parentSpanId,
          operationName, start, duration, tags, logs

Span relationship types:
  ChildOf: parent->child (sync; parent waits)
  FollowsFrom: fire-and-forget (async; parent doesn't wait)

Sampling strategies:
  Head-based: decide at trace start (random %)
    + Simple; no storage overhead
    - Misses tail-latency anomalies (not sampled)

  Tail-based: buffer spans; decide after request completes
    + Captures 100% of errors and slow requests
    - Requires span buffer; complex collector

  Adaptive: vary sampling rate based on traffic volume
    + Cost-efficient at scale
    - Complex configuration
```

**PROPAGATION HEADERS:**

```
HTTP request across services:
  Service A -> Service B -> Service C

  A injects:  traceparent: 00-abc123-span1-01
  B reads + propagates: traceparent: 00-abc123-span2-01
    B creates span: {traceId:abc123, parentSpanId:span1}
  C reads + propagates: traceparent: 00-abc123-span3-01
    C creates span: {traceId:abc123, parentSpanId:span2}

  All spans collected: form a tree
  Tree = the complete trace
```

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Trace context must be propagated across every service boundary; missing one link breaks the trace.
**Accidental:** Vendor-specific SDKs that cause lock-in; replaced by OpenTelemetry.

---

### 🧪 Thought Experiment

**SETUP:**
P99 latency on the checkout endpoint spikes from 50ms
to 3s. 12 services are involved in checkout.

**WITHOUT DISTRIBUTED TRACING:**

```
- Check each service's average latency metric: all normal
  (P99 spike is in tail; averages miss it)
- Read logs from service A: no errors
- Read logs from service B: no errors
- Cannot correlate logs to the same request
- Cannot see which service is slow for the specific
  requests that hit P99
- Investigation time: hours to days
```

**WITH DISTRIBUTED TRACING:**

```
- Filter traces by duration > 1000ms
- Select a slow trace: full span tree visible
- Span tree reveals:
  checkout-service: 3001ms total
    -> inventory-check: 12ms (normal)
    -> payment-service: 2987ms  <- HERE
      -> fraud-check: 12ms (normal)
      -> external-payment-gateway: 2975ms <- HERE
- Root cause: external payment gateway latency spike
- Investigation time: 3 minutes
```

---

### 🧠 Mental Model / Analogy

> Distributed tracing is like an air traffic control
> radar system for requests. Each aircraft (request)
> has a transponder (trace ID). Every airport (service)
> it passes through reports its position and timing.
> The radar (tracing backend) assembles all reports
> into a complete flight path. Without the transponder,
> you know planes take off and land but nothing about
> what happens in between.

**Element mapping:**

- Aircraft = request
- Transponder = trace ID
- Airport = service
- Report = span
- Radar system = tracing backend (Jaeger/Tempo)
- Flight path = complete trace

Where this analogy breaks down: aircraft transponders
are mandatory and standardised; trace propagation in
software is optional and must be explicitly instrumented.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When a request goes through 12 services, distributed
tracing puts a tracker on it so you can see exactly
where it went and how long each step took.

**Level 2 - How to use it (junior developer):**
Add OpenTelemetry auto-instrumentation to your service
(Java agent: `-javaagent:opentelemetry-javaagent.jar`).
It automatically: propagates trace context in HTTP
headers; creates spans for incoming/outgoing HTTP calls;
exports to the configured backend (Jaeger).

**Level 3 - How it works (mid-level engineer):**
Auto-instrumentation handles HTTP; add manual spans for
business operations. Configure head-based sampling at
1% for normal traffic; force 100% sampling for all errors
(error sampling). Use tail-based sampling (OpenTelemetry
Collector) for capturing all slow requests. Connect
traces to logs via trace ID in structured log fields.

**Level 4 - Why it was designed this way (senior/staff):**
OpenTelemetry's architecture separates instrumentation
(SDK in app), transport (OTLP protocol), and storage
(backend). The Collector sits between SDK and backend:
it fans out to multiple backends, applies sampling,
batches, and retries. This separation allows:

- changing backend without redeployment (Jaeger -> Tempo)
- centralised sampling policy (not per-service config)
- PII scrubbing in collector before storage

**Expert Thinking Cues:**

- If traces are missing: check propagation headers at every service boundary.
- If sampling is 100% and storage is filling: switch to tail-based; sample 100% of errors, 1% of successes.
- Connect logs to traces: add trace_id field to all log entries; enables jump from trace to log.

---

### ⚙️ How It Works (Mechanism)

**OpenTelemetry Java setup:**

```java
// Auto-instrumentation via Java agent:
// java -javaagent:otel-javaagent.jar \
//   -Dotel.service.name=checkout-service \
//   -Dotel.exporter.otlp.endpoint=http://collector:4317 \
//   -jar checkout-service.jar

// Manual span for business operation:
Tracer tracer = GlobalOpenTelemetry.getTracer("checkout");
Span span = tracer.spanBuilder("processPayment")
    .setAttribute("payment.amount", amount)
    .setAttribute("payment.currency", currency)
    .startSpan();
try (Scope scope = span.makeCurrent()) {
    result = paymentService.charge(amount, currency);
    span.setStatus(StatusCode.OK);
} catch (PaymentException e) {
    span.recordException(e);
    span.setStatus(StatusCode.ERROR, e.getMessage());
    throw e;
} finally {
    span.end();
}

// Connect to logs:
log.info("Payment processed",
    Map.of(
        "trace_id", span.getSpanContext().getTraceId(),
        "span_id", span.getSpanContext().getSpanId()
    ));
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Distributed tracing architecture:**

```
Service A (auto-instrumented)        <- YOU ARE HERE
  -> Span created; trace_id=abc123
  -> HTTP to Service B:
     Header: traceparent: 00-abc123-span1-01
  |
Service B:
  -> Span extracted from header
  -> New span: {traceId:abc123, parent:span1}
  -> HTTP to Service C:
     Header: traceparent: 00-abc123-span2-01
  |
Service C:
  -> Span extracted from header
  -> New span: {traceId:abc123, parent:span2}
  |
OTLP export: A, B, C -> OTel Collector
Collector:
  -> Apply sampling (tail-based; buffer 5min)
  -> PII scrubbing
  -> Fan-out: Jaeger + Prometheus
Jaeger:
  -> Assemble span tree from trace_id
  -> Render trace timeline
  -> Search: trace_id, service, duration, error
```

---

### ⚖️ Comparison Table

| Backend         | Strength                                 | Storage        | Use Case                |
| --------------- | ---------------------------------------- | -------------- | ----------------------- |
| Jaeger          | K8s-native, full-featured, OSS           | Cassandra/ES   | Production default      |
| Zipkin          | Simple, lightweight                      | MySQL/ES       | Low-scale, legacy       |
| Tempo (Grafana) | Integrates with Loki/Prometheus          | Object storage | Cost-efficient at scale |
| Honeycomb       | Columnar query, fast on high cardinality | Proprietary    | Complex queries         |
| Datadog APM     | Full observability platform              | Proprietary    | All-in-one              |

---

### ⚠️ Common Misconceptions

| Misconception                              | Reality                                                                             |
| ------------------------------------------ | ----------------------------------------------------------------------------------- |
| "100% sampling is necessary for accuracy"  | Tail-based 100% error + 1% success captures all anomalies at manageable cost        |
| "Auto-instrumentation is sufficient"       | Auto-instrumentation covers HTTP/DB; manual spans needed for business operations    |
| "Distributed tracing replaces logging"     | They complement: trace shows where; logs show what; connect via trace_id in logs    |
| "OpenTelemetry is just another vendor"     | OpenTelemetry is a CNCF standard; all major vendors support it; it's vendor-neutral |
| "Tracing only works for synchronous calls" | Async (Kafka, async HTTP): propagate trace context in message headers/metadata      |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Broken Trace (Missing Spans)**
**Symptom:** Trace shows service A span; service B span missing.
**Root Cause:** Service B does not extract/propagate the `traceparent` header.
**Diagnostic:**

```bash
curl -v https://service-b/endpoint \
  -H 'traceparent: 00-abc123def456-span1-01'
# Check response: does service B propagate traceparent in
# outbound calls? Check OpenTelemetry auto-instrumentation
# is loaded (look for otel agent in JVM args)
```

**Fix:** Ensure OTel auto-instrumentation (Java agent) loaded on all services; verify propagation.

**Mode 2: Sampling Gap on Errors**
**Symptom:** Errors visible in metrics but not in traces (no error traces).
**Root Cause:** Head-based sampling at 1%; most error requests are not sampled.
**Fix:** Configure tail-based sampling: 100% sample all spans where error=true.

**Mode 3: High Cardinality Tag Breaking Jaeger**
**Symptom:** Jaeger storage fills; Jaeger query slow.
**Root Cause:** Tags with high cardinality (e.g., user_id on every span) create unbounded index entries.
**Fix:** Don't use user_id as tag; use resource attribute or store in log body instead.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[DST-049 - Observability]]
- [[DST-050 - Distributed Tracing]]
- [[DST-051 - OpenTelemetry]]

**Builds On This (learn these next):**

- [[DST-052 - Sampling Strategies]]

**Alternatives / Comparisons:**

- Centralized logging (ELK) — complements tracing; logs show details within a span

---

### 📌 Quick Reference Card

```
+-----------------------------------------------------+
| WHAT IT IS      Tracking one request across all     |
|                 services as a unified timeline      |
| PROBLEM         "Which of 12 services is slow?"     |
| IT SOLVES       is unanswerable without tracing     |
| KEY INSIGHT     Trace = spans linked by trace_id;   |
|                 propagate trace_id across every hop |
| USE WHEN        Any system with > 2 services        |
| AVOID           100% sampling in high-traffic prod  |
| TRADE-OFF       Storage cost vs trace completeness  |
| ONE-LINER       trace_id links spans across services|
| NEXT EXPLORE    OpenTelemetry, Jaeger, tail sampling|
+-----------------------------------------------------+
```

**If you remember only 3 things:**

1. A trace is a tree of spans linked by trace ID propagated in headers; missing propagation at any hop breaks the trace.
2. Use OpenTelemetry SDK (vendor-neutral); point the collector exporter at any backend without code change.
3. Tail-based sampling: capture 100% of errors and slow requests; sample 1% of normal traffic.

**Interview one-liner:**
"Distributed tracing stitches together spans from every service in a request path using a shared trace ID propagated in headers; OpenTelemetry provides the vendor-neutral SDK; tail-based sampling captures 100% of errors at manageable storage cost."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
End-to-end visibility requires a correlation ID that
travels with the work from start to finish. This applies
beyond distributed tracing: async job tracking (job ID),
batch processing (batch ID), document processing
(document ID). In all cases: generate once at entry;
propagate everywhere; include in all logs and metrics.

**Where else this pattern appears:**

- **Async job queues** — job_id propagated through queue; enables tracking job through worker
- **Document processing pipelines** — document_id propagated through each transformation stage
- **Financial transaction audit** — transaction_id propagated through all systems for end-to-end audit trail

---

### 💡 The Surprising Truth

Google's Dapper paper (2010) reported that even at 0.01%
sampling rate (1 in 10,000 requests), the Dapper system
was sufficient to diagnose nearly all latency anomalies
in Google's production systems. The reason: latency
problems tend to be systematic (a slow DB query affects
every request that hits it, not just one in 10,000).
Sampling at 0.01% still captures enough examples of
the systematic problem to diagnose it. Over-sampling
(high rates) wastes storage and compute without
improving diagnostic power for systematic issues.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** A request goes through
service A (HTTP) -> service B (HTTP) -> Kafka -> service C
(async consumer). Service A starts the trace. Describe
how the trace ID must be propagated through the Kafka
message so that service C's span is correctly linked
to the original trace.

_Hint:_ Kafka messages have headers. Propagate the
`traceparent` header into the Kafka message header in
the producer. Consumer reads the Kafka header; extracts
trace context; creates a new span with that context
as parent. W3C Trace Context spec covers this pattern.

**Q2 (Design Trade-off):** Tail-based sampling requires
buffering all spans from a request before making the
sampling decision. At 100,000 RPS with average 10
spans/request and 60-second max request duration, estimate
the memory required by the tail-based sampling buffer
in the collector. Is this feasible?

_Hint:_ 100,000 RPS x 10 spans x 60s = 60M spans buffered.
Avg span ~1KB = 60GB buffer. Not feasible in single
collector. Solution: partition traces by trace_id;
distribute across collector cluster; each collector
buffers only its subset. Jaeger's tail-based sampler
or OTel Collector can operate in clustered mode.

**Q3 (Scale):** Uber has 2,200+ microservices. If every
service call creates one span and average request
crosses 20 services, at 1M RPS Uber scale, calculate
the spans-per-second generated. What sampling rate
would reduce this to a manageable 100K spans/second?

_Hint:_ 1M RPS x 20 spans = 20M spans/sec. To reach 100K
spans/sec: 100K/20M = 0.5% sampling. At 0.5% sampling,
for every 200 requests of the same type, 1 is traced.
Systematic issues (affecting all 200) are still visible
in the 1 sampled trace.
