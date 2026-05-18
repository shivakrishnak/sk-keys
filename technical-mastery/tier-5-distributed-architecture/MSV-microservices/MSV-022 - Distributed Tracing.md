---
id: MSV-022
title: Distributed Tracing
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★☆
depends_on: MSV-021, MSV-010, MSV-002
used_by: MSV-065
related: MSV-021, MSV-065, MSV-064, MSV-063, MSV-040
tags:
  - microservices
  - observability
  - intermediate
  - debugging
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Mastery"
nav_order: 22
permalink: /technical-mastery/microservices/distributed-tracing/
---

⚡ TL;DR - Distributed Tracing tracks the journey of
a request across multiple services, recording the start
time, duration, and result of each service hop as a
"span". The collection of spans for one request is a
"trace". It answers "which service made my request slow?"
and "what is the dependency graph of a user request?"

| #022 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Correlation ID, Inter-Service Communication, Microservices Architecture | |
| **Used by:** | OpenTelemetry in Microservices | |
| **Related:** | Correlation ID, OpenTelemetry in Microservices, Distributed Logging, Cross-Cutting Concerns, Service Mesh | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Checkout takes 2.3 seconds. P99 SLO is 1 second. You
have 12 microservices involved in checkout. Logs show
all services received requests. Which service is slow?

You check:
- API Gateway logs: 50ms overhead
- Order Service logs: "Order created" in 200ms
- Payment Service logs: "Payment processed" in 1800ms?
But Payment Service logs don't show timestamps
for which sub-operations took how long. Is it the
credit card authorisation? The fraud check? The DB write?

With logs alone: you know checkout is slow but you
cannot pinpoint which operation within which service.

**THE BREAKTHROUGH:**
Distributed Tracing captures timing for every operation
with parent-child relationships. You see:
```
Checkout (2300ms total)
  ├─ API Gateway (50ms)
  ├─ Order Service (200ms)
  └─ Payment Service (1800ms)
      ├─ Fraud Check (1600ms) <-- THE CULPRIT
      └─ Card Auth (100ms)
      └─ DB Write (100ms)
```
Root cause identified in 10 seconds.

---

### 📘 Textbook Definition

**Distributed Tracing** is an observability technique
that tracks requests as they propagate through multiple
services, recording each service call as a **span** (a
unit of work with start time, duration, metadata, and
status). All spans belonging to one user request share
a **Trace ID** and are linked in a parent-child hierarchy,
forming a **trace** (a directed acyclic graph of spans
that shows the full execution timeline). Modern distributed
tracing follows the OpenTelemetry standard, using the
W3C `traceparent` header to propagate context across
service boundaries.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Distributed Tracing records a timeline of every service
call for a single user request with parent-child
relationships, showing exactly which service and which
operation caused latency or failure.

**One analogy:**
> A flight itinerary with actual departure/arrival times.
> Your trip (trace) has 3 flights (spans). Each flight
> records: airline, departure gate, departure time, arrival
> time, delay reason. If your total trip took 15 hours
but should take 10, you can see: Flight 1 was on time,
> Flight 2 had a 4-hour delay, Flight 3 was on time.
> The tracing system is the itinerary that records
> timing and status for every leg of the journey.

**One insight:**
Distributed Tracing is complementary to, not a replacement
for, logging. Logs provide rich business context (user
IDs, order amounts, error messages). Traces provide
latency topology (which services are in the critical
path, where time is spent). Use both: trace for "where
is the bottleneck", log for "what went wrong with
business data".

---

### 🔩 First Principles Explanation

**CORE CONCEPTS:**

```
TRACE:
  The complete record of one user request journey
  Identified by: Trace ID (unique per request)
  Contains: all spans for this request
  Analogy: the complete hospital visit record

SPAN:
  One unit of work within a trace
  Identified by: Span ID (unique per operation)
  Contains: service name, operation name, start, duration
            status (OK/ERROR), parent span ID,
              tags/attributes
  Analogy: one department visit within the hospital stay

PARENT-CHILD RELATIONSHIP:
  Span A calls Span B
  Span B is child of Span A
  Span B.parentSpanId = Span A.spanId
  Allows reconstruction of call graph

W3C TRACEPARENT HEADER:
  traceparent: 00-{traceId}-{spanId}-{flags}
  Example:
  traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736
               -00f067aa0ba902b7-01
  traceId:     4bf92f3577b34da6a3ce929d0e0e4736
  parentSpanId: 00f067aa0ba902b7
  flags:       01 (sampled)
```

**SAMPLING:**

```
PROBLEM: At 10,000 req/s, recording every span
  generates 500,000+ spans/second (assuming 50 spans/trace)
  Storage: ~100GB/day. Too expensive.

SOLUTION: Sampling - only trace a % of requests

HEAD SAMPLING (at trace start):
  Decide at entry point: sample this trace? (1%)
  Propagate decision (flags in traceparent header)
  All services: only record spans if trace is sampled
  Simple, low overhead
  Problem: misses rare slow requests if sampling is low

TAIL SAMPLING (at trace completion):
  Buffer ALL spans for all traces
  After trace completes: apply sampling rule
  Always keep: error traces, slow traces (P99+)
  Discard: fast, successful traces
  Better: captures rare important events
  Higher overhead: must buffer all spans in collector

PRODUCTION DEFAULT: head sampling 1-10%
  + tail sampling to keep 100% of errors and slow traces
```

---

### 🧪 Thought Experiment

**TRACE ANALYSIS WORKFLOW:**

```
SYMPTOM: checkout P99 = 2.3s (SLO: 1s)

STEP 1: Find slow traces in Jaeger/Zipkin
  Filter: service=checkout-bff AND duration>1000ms
  Sample trace: traceId=4bf92f...

STEP 2: Open the trace waterfall
  checkout-bff [0ms - 2300ms] = 2300ms total
  ├ gateway-filter [0ms - 50ms]
  ├ order-service [51ms - 270ms]
  └ payment-service [270ms - 2290ms]
      ├ fraud-check [271ms - 1875ms] <-- 1600ms!
      └ card-auth [1876ms - 2090ms]
      └ db-write [2091ms - 2290ms]

STEP 3: Drill into fraud-check span
  Tags: {ml_model: "v2.3", user_risk_score: 0.72,
         model_inference_time_ms: 1580}
  Root cause: ML model inference taking 1580ms
  Fix: async fraud check + approve fast, reconcile
  later (or upgrade to faster ML serving
  infrastructure)

DEBUG TIME: 10 seconds to root cause
(vs hours without distributed tracing)
```

---

### 🧠 Mental Model / Analogy

> Distributed Tracing is like an orchestral score. Each
> musician (service) plays their part. The score (trace)
> shows all parts simultaneously on a timeline - when
> each instrument starts, how long it plays, and whether
> it plays correctly. A conductor (oncall engineer) can
> see at a glance which section (service) fell behind
> or played a wrong note (error). Without the score:
> you'd need to interview each musician separately and
> piece together the timeline manually.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Distributed Tracing tracks a request as it visits
multiple services, recording how long each service
took. You see a visual timeline showing exactly where
your request spent time.

**Level 2 - How to use it (junior developer):**
Add OpenTelemetry Java agent to the JVM:
`java -javaagent:opentelemetry-javaagent.jar -jar app.jar`.
Auto-instrumentation traces HTTP calls, database queries,
and Kafka messages without code changes. Configure the
collector endpoint:
`OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317`.

**Level 3 - How it works (mid-level engineer):**
OpenTelemetry SDK: instruments the application at startup.
For each HTTP request: creates a root span, stores in
Thread Context (or Reactor Context). For each outbound
call: creates a child span, injects `traceparent` header.
For each DB query: creates a DB span. Spans are batched
and exported to the OTel Collector (OTLP protocol). The
collector exports to backend (Jaeger, Zipkin, Honeycomb,
Datadog). Jaeger/Zipkin stores and visualises the trace
waterfall.

**Level 4 - Why it was designed this way (senior/staff):**
The OpenTelemetry spec separates instrumentation from
export backend. The same instrumented code exports to
Jaeger (open source), Honeycomb (managed), or Datadog
(enterprise) by changing the collector configuration.
This vendor neutrality prevents lock-in. Before OTel:
each APM vendor (Jaeger, Zipkin, Datadog) had proprietary
SDKs. Switching vendors required re-instrumenting. OTel
makes instrumentation write-once, export-anywhere.

**Level 5 - Mastery (distinguished engineer):**
High-cardinality tracing at scale: in production at
100K req/s, storing 100% of traces is cost-prohibitive.
Honeycomb and Lightstep use high-cardinality, head-based
sampling with dynamic rates: increase sampling during
incidents, decrease during normal operation. Tail-based
sampling (Open Telemetry Collector tail sampler) buffers
all spans and samples at trace completion: keep 100%
of error and slow traces, sample 1% of fast-success
traces. The tail sampler must see ALL spans for a trace
to make the sampling decision - requires all services
to export to the SAME collector cluster.

---

### ⚙️ How It Works (Mechanism)

**OPENTELEMETRY MANUAL INSTRUMENTATION:**

```java
// Manual span creation for business operations
@Service
public class FraudCheckService {

    private final Tracer tracer = GlobalOpenTelemetry
        .getTracer("fraud-check-service");

    public FraudResult check(Payment payment) {
        // Create child span (auto-linked to current trace)
        Span span = tracer.spanBuilder("fraud.check")
            .setAttribute(
                "payment.amount", payment.getAmount())
            .setAttribute(
                "payment.userId", payment.getUserId())
            .startSpan();

        try (Scope scope = span.makeCurrent()) {
            FraudResult result = mlModel.evaluate(
                payment);
            span.setAttribute(
                "fraud.score", result.getScore());
            span.setAttribute(
                "fraud.decision", result.getDecision());
            return result;
        } catch (Exception e) {
            span.setStatus(
                StatusCode.ERROR, e.getMessage());
            span.recordException(e);
            throw e;
        } finally {
            span.end();
        }
    }
}
// In Jaeger: this span appears as child of payment-service
// span with duration and all attributes visible
```

**OTEL COLLECTOR CONFIGURATION:**

```yaml
# opentelemetry-collector.yaml
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
  tail_sampling:
    decision_wait: 10s
    num_traces: 100000
    policies:
      - name: errors-policy
        type: status_code
        status_code: {status_codes: [ERROR]}
      - name: slow-traces-policy
        type: latency
        latency: {threshold_ms: 1000}
      - name: probabilistic-policy
        type: probabilistic
        probabilistic: {sampling_percentage: 5}

exporters:
  jaeger:
    endpoint: jaeger-collector:14250
    tls:
      insecure: true

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch, tail_sampling]
      exporters: [jaeger]
```

---

### 🔄 The Complete Picture - End-to-End Flow

**TRACE LIFECYCLE:**

```
1. Mobile app → API Gateway:
   No traceparent header
   Gateway creates: traceId=4bf92f, spanId=0001
   Gateway span: {service:gateway, op:route, 0-50ms}

2. Gateway → Checkout BFF:
   Header: traceparent: 00-4bf92f-0001-01
   BFF creates: spanId=0002, parentSpanId=0001
   BFF span: {service:checkout-bff, op:checkout, 0-2300ms}

3. BFF → Order Service (parallel with Payment):
   Header: traceparent: 00-4bf92f-0002-01
   Order span: {service:order, op:create, 51-270ms}

4. BFF → Payment Service:
   Header: traceparent: 00-4bf92f-0002-01
   Payment span: {service:payment, op:charge, 270-2290ms}
   └ Fraud span: {service:fraud, op:check, 271-1875ms}
     (child of payment span)

5. All spans exported to OTel Collector
6. Collector tail-samples: this trace > 1000ms -> KEEP
7. Exported to Jaeger
8. Visible in Jaeger UI: waterfall diagram
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: no span attributes**

```java
// BAD: span exists but no attributes
// Trace shows: payment-service called, took 1800ms
// Can't tell WHY it was slow (which operation?)
Span span = tracer.spanBuilder("payment").startSpan();
try (Scope s = span.makeCurrent()) {
    return processPayment(req);
} finally { span.end(); }
// Trace: payment [1800ms] - nothing more
```

```java
// GOOD: rich span attributes for diagnosis
Span span = tracer.spanBuilder("payment.process")
    .setAttribute(
        "payment.amount", req.getAmount())
    .setAttribute(
        "payment.provider", "stripe")
    .setAttribute(
        "payment.method", req.getMethod())
    .startSpan();
try (Scope s = span.makeCurrent()) {
    PaymentResult result = processPayment(req);
    span.setAttribute(
        "payment.status", result.getStatus());
    span.setAttribute(
        "payment.provider_latency_ms",
        result.getProviderLatency());
    return result;
} catch (PaymentException e) {
    span.setStatus(StatusCode.ERROR,
        e.getMessage());
    span.setAttribute(
        "payment.error_code", e.getCode());
    throw e;
} finally {
    span.end();
}
// Trace: payment.process [1800ms]
//   provider=stripe, method=visa, amount=99.99
//   provider_latency_ms=1650
// Root cause visible: Stripe API took 1650ms
```

---

### ⚖️ Comparison Table

| Tool | Backend | Cost | Features |
|---|---|---|---|
| **Jaeger** | Self-hosted | Free | Full OTel support, good UI |
| **Zipkin** | Self-hosted | Free | Simpler, good for small teams |
| **Honeycomb** | SaaS | Paid | High-cardinality, excellent UX |
| **Datadog APM** | SaaS | Paid | Integrated metrics/logs/traces |
| **AWS X-Ray** | AWS SaaS | Pay-per-use | AWS-native integration |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Distributed Tracing replaces logging | Tracing shows WHERE time is spent (latency, call graph). Logging shows WHAT happened (user data, business events, error details). Both are required. Tracing without logging: you know it's slow but not why. Logging without tracing: you have details but no call graph. |
| 100% sampling is necessary | 100% sampling at scale is prohibitively expensive. 1-10% head sampling plus tail sampling of errors and slow traces gives excellent coverage at a fraction of the cost. You don't need to trace every successful fast request. |
| OpenTelemetry auto-instrumentation is sufficient | Auto-instrumentation traces HTTP calls, DB queries, and messaging. It does NOT capture business context (user tier, payment amount, fraud score). Add manual span attributes for business-specific data that matters for debugging. |

---

### 🚨 Failure Modes & Diagnosis

**Missing spans - incomplete trace**

**Symptom:**
Jaeger trace shows: API Gateway → Order Service.
Payment Service span is missing. But logs show Payment
Service was called and processed the request.

**Root Cause:**
Payment Service is not exporting traces to OTel Collector.
Either: (1) OTel agent not configured, (2) Collector
endpoint misconfigured, (3) service using different
tracing library (Zipkin B3 header instead of W3C traceparent).

**Diagnostic Command:**
```bash
# Check if OTel agent is loaded
jps -v | grep payment-service
# Should show: -javaagent:opentelemetry-javaagent.jar

# Check OTel exporter configuration
kubectl get pod payment-service-xxx -o jsonpath=
  '{.spec.containers[0].env}' | \
  python3 -m json.tool | \
  grep -i otel
# Look for: OTEL_EXPORTER_OTLP_ENDPOINT

# Test collector reachability from pod
kubectl exec payment-service-xxx -- \
  curl http://otel-collector:4318/v1/traces
# Should return 200 or 405 (method not allowed)
# Connection refused: collector not reachable

# Check if B3 vs W3C header mismatch
kubectl exec payment-service-xxx -- \
  env | grep OTEL_PROPAGATORS
# Should be: tracecontext,baggage (W3C)
# If: b3 -> mismatch with other services using W3C
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Correlation ID` - the simpler predecessor to distributed
  tracing; Trace ID is the standardised form of Correlation ID

**Builds On This (learn these next):**
- `OpenTelemetry in Microservices` - the implementation
  standard for distributed tracing (and metrics, logs)

**Context:**
- `Service Mesh` - Istio/Linkerd auto-generates traces at
  the sidecar level without application code changes
- `Distributed Logging` - complements tracing: logs
  provide business context; traces provide latency topology

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ CONCEPTS     │ Trace = full journey, Span = one hop     │
│              │ Spans linked by parent-child spanId      │
├──────────────┼──────────────────────────────────────────┤
│ HEADER       │ W3C traceparent (OTel standard)          │
│              │ traceId + parentSpanId + flags           │
├──────────────┼──────────────────────────────────────────┤
│ SAMPLING     │ Head: % at entry. Tail: keep errors/slow │
│              │ Production: 1-10% head + tail for errors │
├──────────────┼──────────────────────────────────────────┤
│ USE FOR      │ Latency root cause, dependency mapping   │
│              │ NOT for business event logging (use logs)│
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Timeline of all service hops for one    │
│              │  request: find latency bottleneck fast"  │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ OpenTelemetry → Service Mesh             │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Trace = full request journey; Span = one hop.
   Spans linked by parent/child via Span IDs.
2. Use tail sampling: keep 100% of error/slow traces,
   sample 1-10% of fast-success traces. Never 100% sample
   in production at scale.
3. Add business attributes to spans (`setAttribute`).
   Auto-instrumentation shows timing; custom attributes
   show the business context that explains the timing.

**Interview one-liner:**
"Distributed Tracing records each service call as a Span
with start time, duration, and status. All spans for one
request share a Trace ID and are linked parent-to-child,
forming a waterfall diagram. OpenTelemetry is the standard;
W3C traceparent header propagates context. Production:
tail-based sampling keeps 100% of error and slow traces,
samples 1-10% of successful fast ones. Complements
logging: tracing shows WHERE time is spent; logs show
WHAT happened."

---

### 💡 The Surprising Truth

Distributed tracing's biggest unsolved problem at scale
is trace completeness when sampling is involved. At 1%
head sampling, 99% of traces are dropped at the first
hop. If a downstream service is slow, the slow traces
are also sampled at 1% - meaning you might miss the
evidence that shows the slowdown. Tail sampling (keep
all traces > 1000ms) solves this by delaying the sampling
decision until after the trace completes. But tail sampling
requires all spans for a trace to arrive at the same
collector node (for the decision). In a distributed
collector cluster, this requires consistent hashing by
trace ID to route all spans of one trace to the same
collector node. Honeycomb calls this "refinery": a
tail-sampling pipeline that scales horizontally while
ensuring trace completeness.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **READ** Given a Jaeger trace waterfall, identify the
   critical path, the slowest span, and the root cause
   of a P99 latency regression.
2. **IMPLEMENT** Add OTel instrumentation to a Spring
   Boot service: agent config, custom spans with business
   attributes, error recording.
3. **CONFIGURE** OTel Collector with tail sampling:
   keep 100% of error traces, keep traces > 1s, sample
   5% of all others.
4. **DIAGNOSE** Given missing spans in Jaeger for a
   specific service, identify whether the cause is:
   agent not loaded, collector unreachable, header format
   mismatch (B3 vs W3C), or sampling filtering.
5. **DESIGN** A tracing strategy for a system where 3
   services use Datadog, 5 use Jaeger, and 2 use Zipkin.
   How do you get a unified trace view?

---

### 🧠 Think About This Before We Continue

**Q1.** A trace has 10 spans. The total trace duration
is 5 seconds. The root span is 5 seconds. Spans 2-9
are all children of span 1 and run in parallel, each
taking 500ms. Span 10 is a child of span 9 and takes
4.5 seconds. Draw the waterfall diagram. What is the
critical path? Which spans are not on the critical path?

**Q2.** At 100K req/s with 50 spans per trace, you
generate 5M spans/second. At 1KB per span: 5GB/second
of span data. Design a sampling strategy that: (a) keeps
100% of error traces, (b) keeps 100% of traces >2s,
(c) keeps 1% of all other traces. Calculate the
resulting span data rate and storage per day.

**Q3.** A business requirement: every payment transaction
must have a trace that is kept for 90 days for compliance.
All other traces can be kept for 7 days. Design the
tracing pipeline: how do you identify payment traces
vs other traces, how do you apply different retention
policies, and what OTel Collector configuration or
post-processing achieves this?