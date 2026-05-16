---
id: OBS-008
title: Distributed Tracing Fundamentals
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★☆☆
depends_on: OBS-002, OBS-007
used_by: OBS-015, OBS-016, OBS-017
related: OBS-002, OBS-007, OBS-006
tags:
  - observability
  - tracing
  - foundational
  - first-principles
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 8
permalink: /obs/distributed-tracing-fundamentals/
---

# OBS-008 - Distributed Tracing Fundamentals

⚡ TL;DR - Distributed tracing reconstructs the complete
path of a request across services by attaching a unique
trace ID and recording timed spans at every service hop,
so you can see exactly where latency and errors originate.

| #008 | Category: Observability & SRE | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Three Pillars of Observability, Logging Fundamentals | |
| **Used by:** | OpenTelemetry, Jaeger, Zipkin, Tempo | |
| **Related:** | Three Pillars, Logging Fundamentals, Metrics Types | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A checkout request takes 4 seconds for 2% of users.
The checkout service alone takes 200ms. Somewhere in
the 12 downstream services it calls, 3.8 seconds are
being consumed. Without distributed tracing, the
investigation process is:
1. Add timing logs to checkout service
2. Redeploy checkout service
3. Observe: checkout calls payment in 50ms
4. Add timing logs to payment service
5. Redeploy payment service
6. Observe: payment calls fraud check in 3.8 seconds
7. Identify root cause: fraud check has a slow path
   for certain card types

This iterative investigation cycle takes hours or days
in a system with 12 services, each requiring a separate
deployment to add timing logs.

**THE BREAKING POINT:**
In a microservices architecture with 50+ services, a
single user request may touch 8-20 services. When
latency degrades, the causal service is unknown.
Without distributed tracing, finding the root cause is
a manual, slow, multi-service investigation. Service
dependency is also unknown: which services does the
checkout call? Directly? Transitively? Without tracing,
this map must be manually maintained.

**THE INVENTION MOMENT:**
Google's Dapper paper (2010) described the first
large-scale distributed tracing system. It introduced
the core concepts: trace, span, trace context
propagation. Zipkin (Twitter, 2012) was the first
open-source implementation. Jaeger (Uber, 2016)
followed. OpenTelemetry (2019) unified the ecosystem
with a single standard for trace context propagation
and SDK instrumentation.

---

### 📘 Textbook Definition

**Distributed tracing** is a technique for tracking the
flow of a request through a distributed system by
attaching a unique trace identifier to the request and
recording timed spans at each service that processes it.

**Core concepts:**
- **Trace:** the complete journey of a single request
  through all services, represented as a tree of spans
- **Span:** a single unit of work within a trace,
  with a start time, end time, service name, operation
  name, and key-value attributes
- **Trace context:** the `trace_id` + `span_id` pair
  propagated in HTTP headers and message headers to
  link spans across service boundaries
- **Parent span:** the span that triggered the current
  span (defines the tree structure)
- **Root span:** the first span in a trace, typically
  the API gateway or entry point

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A distributed trace is a timeline of everything that
happened for one request across all services - like a
Gantt chart for your microservices.

> Think of a relay race. The baton (trace context) is
> passed from runner to runner. Each runner's leg is a
> span: it has a start time, end time, and the runner's
> identity. At the finish line, you can see the complete
> race: how long each leg took, where the baton was
> dropped and recovered (error), and the critical path
> (which legs determine the total time).
> Without the baton, you only know the total race time.
> You cannot tell which runner was slow.

**One insight:**
The critical path of a trace is the sequence of spans
where each span's start depends on the previous span's
end. Reducing total request latency requires reducing
the latency of spans on the critical path. Spans that
run in parallel are not on the critical path even if
they are slow.

---

### 🔩 First Principles Explanation

**THE CORE MECHANISM:**

A distributed trace works by:
1. Generating a globally unique `trace_id` at the
   request entry point
2. Attaching the `trace_id` to every outgoing request
   (HTTP header, message header)
3. Recording a `span` at each service: start, end,
   name, attributes, parent span ID
4. Shipping spans to a central trace collector
5. Reconstructing the tree from parent-child span links

**CONTEXT PROPAGATION:**
The W3C Trace Context standard defines how to propagate
the trace context:
```
traceparent: 00-<trace-id>-<parent-span-id>-<flags>
```
Example:
```
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
```
This single HTTP header carries the trace ID and the
parent span ID across service boundaries.

**TRADE-OFFS:**
**Gain:** Instant root cause identification across
services. Latency decomposition (which service is slow).
Service dependency map. SLO measurement per service.
**Cost:** Every span adds serialisation and network
overhead to ship to the trace backend. High-traffic
systems must sample traces (1-10%) to control cost.
Instrumentation requires code changes or agent injection.

**SAMPLING:**
Tracing 100% of requests at high traffic (10,000
requests/second) generates 10,000 root spans + all
child spans per second - too expensive. Sampling
strategies:
- **Head sampling:** decide at the root span (1% of
  requests are traced). Simple but misses rare errors.
- **Tail sampling:** decide after the trace completes
  (keep all error traces, sample non-error traces at 1%).
  Captures all failures. Requires buffering full traces.

---

### 🧪 Thought Experiment

**SETUP:**
An e-commerce checkout takes 2.8 seconds for some users.
The checkout service calls 5 downstream services:
inventory (parallel), pricing (parallel), payment
(sequential), fraud (sequential), fulfillment (parallel).

**WITHOUT TRACING:**
The team measures checkout service response time: 200ms.
They add logging to each service individually, redeploying
each one. After 3 days of investigation: fraud service
is slow for some payment methods.

**WITH TRACING:**
The on-call engineer queries Jaeger for slow checkout
traces (> 2 seconds) from the last hour:
```
Trace ID: abc123
  checkout (root): 0ms → 2800ms (2.8s total)
    ├── inventory: 50ms → 120ms (parallel)
    ├── pricing:   50ms → 80ms  (parallel)
    ├── payment:   150ms → 350ms (sequential)
    │     └── fraud-check: 160ms → 2750ms (2.59s!)
    └── fulfillment: 2800ms → 2850ms (parallel, ok)
```
Root cause: `fraud-check` takes 2.59 seconds on specific
payment methods. The trace shows this in 30 seconds.

**THE INSIGHT:**
The trace provides the causal structure (who called what),
the timing (how long each call took), and the critical
path (fraud-check is on the path, fulfillment is not).
Without tracing, this requires manual instrumentation
across multiple services.

---

### 🧠 Mental Model / Analogy

> A flight operations centre tracks each aircraft with
> a transponder code. The transponder broadcasts the
> aircraft's identity, altitude, and position every
> second. When controllers see that a flight is delayed,
> they can reconstruct exactly where in the route the
> delay originated: taxi (30 min ground hold), takeoff
> (5 min queue), or en-route (weather diversion).
> Without the transponder, controllers only know the
> scheduled arrival and actual arrival. With it, they
> have the complete flight trajectory.

In distributed tracing terms:
- Transponder code = trace_id
- Each aircraft leg = span
- Position broadcast = span attributes (service, latency)
- Flight trajectory = complete trace tree
- Delay diagnosis = critical path analysis on spans

**Where this breaks down:** Aircraft follow fixed routes.
Distributed requests fork, fan out, and have dynamic
paths through microservices. A checkout request may call
different services depending on user location, payment
method, or A/B test group. The trace tree captures
this dynamic structure; the aircraft analogy is linear.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone):**
Distributed tracing is a way of following a request
through all the services it touches, and recording how
long each step takes. It's like a detailed receipt
showing every service that handled your request and
how long each took.

**Level 2 - How to use it (junior developer):**
Add OpenTelemetry to your service. It auto-instruments
HTTP clients and servers. Every request gets a `trace_id`.
Use Jaeger or Zipkin to search for slow traces. Click on
a trace to see the waterfall of spans.

**Level 3 - How it works (mid-level):**
A trace is a tree of spans. Each span has a `trace_id`
(same for all spans in the tree) and a `span_id` (unique
per span). When service A calls service B, A sends its
`span_id` as the `parent_span_id` in the request header.
Service B creates a child span with A's span_id as its
parent. The trace backend reconstructs the tree from
these parent-child relationships.

**Level 4 - Why it matters (senior/staff):**
The practical power of distributed tracing is latency
decomposition and critical path analysis. For a request
that takes 3 seconds total, tracing can show that 2.8
seconds is consumed in a single external API call that
was previously invisible. This insight has clear action:
add a circuit breaker, cache the result, or set a timeout.
Without tracing, the same investigation requires adding
instrumentation across services, deploying, and running
load tests - a multi-hour or multi-day cycle.

**Level 5 - Mastery (distinguished engineer):**
The hardest distributed tracing problem is propagating
trace context through asynchronous boundaries: message
queues, batch jobs, cron tasks, and event-driven
workflows. A trace started by an HTTP request can be
broken if the message published to a queue does not
carry the trace context in its headers. Tail-based
sampling is the other hard problem: to make intelligent
sampling decisions (always keep error traces), you need
to buffer the full trace and make the decision after
completion - but at high QPS, buffering full traces
requires significant memory. Production-grade trace
pipelines (OpenTelemetry Collector with tail sampling
processor) add significant operational complexity.

---

### ⚙️ How It Works (Mechanism)

**SPAN LIFECYCLE:**

```
[Service A receives HTTP request]
   Creates root span: {
     trace_id: "abc123",
     span_id:  "span001",
     parent_span_id: null (root),
     service: "checkout",
     operation: "POST /checkout",
     start_time: 14:23:41.000
   }
        ↓
[Service A calls Service B]
   Injects headers:
     traceparent: 00-abc123-span001-01
   Creates child span: {
     trace_id: "abc123",
     span_id:  "span002",
     parent_span_id: "span001",
     service: "checkout",
     operation: "HTTP GET payment-service"
   }
        ↓
[Service B receives request]
   Extracts headers: trace_id=abc123, parent=span001
   Creates span: {
     trace_id: "abc123",
     span_id:  "span003",
     parent_span_id: "span001",
     service: "payment",
     operation: "processPayment"
   }
        ↓
[Spans complete and are exported to collector]
   Service B ends span003, exports
   Service A ends span002, span001, exports
        ↓
[Trace backend reconstructs tree]
   span001 (root)
     └── span003 (payment, child of span001)
```

**OPENTELEMETRY SDK COMPONENTS:**
- **Tracer:** creates spans in application code
- **Propagator:** reads/writes trace context from/to
  headers (W3C traceparent format)
- **Exporter:** sends completed spans to collector
  (OTLP over gRPC or HTTP)
- **Collector:** receives spans, processes, forwards
  to backend (Jaeger, Zipkin, Tempo, Datadog)

---

### 🔄 The Complete Picture - End-to-End Flow

**REQUEST THROUGH THE TRACING PIPELINE:**

```
[Browser] POST /checkout
      ↓
[API Gateway]
  Generates: trace_id=abc123, span_id=root01
  Sets HTTP header: traceparent: 00-abc123-root01-01
      ↓
[Checkout Service]
  Reads traceparent header
  Creates child span: span_id=ck01, parent=root01
  Calls Payment Service:
    Sets header: traceparent: 00-abc123-ck01-01
      ↓
[Payment Service]
  Creates span: span_id=pay01, parent=ck01
  [SRE team ← YOU ARE HERE: incident in progress]
  Calls Fraud Service - slow!
  Creates child span: span_id=fr01, parent=pay01
      ↓
[All spans exported to OTel Collector]
  Collector processes, ships to Jaeger
      ↓
[Jaeger reconstructs tree]
  root01 (api-gw, 2800ms)
    └── ck01 (checkout, 2780ms)
          └── pay01 (payment, 2760ms)
                └── fr01 (fraud, 2590ms) ← SLOW!
      ↓
[Engineer queries slow traces in Jaeger UI]
  Duration > 2s → finds trace abc123
  Critical path: fraud-check is 93% of total time
```

**WHAT CHANGES AT SCALE:**
At 10,000 requests/second, 100% sampling is impossible
(too many spans). 1% head sampling misses rare errors.
The production solution: tail sampling with an OTel
Collector that buffers 30-second windows of traces
and makes sampling decisions based on the complete trace
properties (error=true → keep 100%; no error → sample 1%).

---

### 💻 Code Example

**Example 1 - BAD: No trace context, manual timing:**

```java
// BAD: manual timing with no propagation.
// Each service measures its own time independently.
// Cannot reconstruct the cross-service causal chain.
// Cannot see that this payment call is part of a checkout.
long start = System.nanoTime();
PaymentResult result = paymentClient.process(request);
long elapsed = System.nanoTime() - start;
logger.info("Payment call took: " + elapsed + "ns");
// These timing logs cannot be joined to checkout timings.
```

**Example 2 - GOOD: OpenTelemetry auto-instrumentation:**

```java
// GOOD: OTel Java agent auto-instruments HTTP clients
// and servers. No code changes needed for basic tracing.
// Add javaagent to startup:
// java -javaagent:opentelemetry-javaagent.jar \
//   -Dotel.service.name=checkout \
//   -Dotel.exporter.otlp.endpoint=http://collector:4317 \
//   -jar checkout.jar

// For manual custom spans, inject Tracer:
@Autowired Tracer tracer;

public PaymentResult processCheckout(Order order) {
    // Auto-instrumented HTTP calls carry trace context.
    // Add custom span for business logic visibility:
    Span span = tracer.spanBuilder("validateOrder")
        .setAttribute("order.id", order.getId())
        .setAttribute("order.amount_cents",
            order.getAmountCents())
        .startSpan();
    try (Scope scope = span.makeCurrent()) {
        validateOrder(order); // business logic
        return paymentClient.charge(order); // auto-traced
    } catch (Exception e) {
        span.recordException(e);
        span.setStatus(StatusCode.ERROR, e.getMessage());
        throw e;
    } finally {
        span.end();
    }
}
```

**Example 3 - Trace context through message queue:**

```java
// GOOD: propagate trace context in message headers
// so async processing is linked to the original request
import io.opentelemetry.api.trace.propagation.W3CTraceContextPropagator;
import io.opentelemetry.context.Context;
import io.opentelemetry.context.propagation.TextMapSetter;

// Producer: inject current trace context into message
Map<String, String> carrier = new HashMap<>();
W3CTraceContextPropagator.getInstance().inject(
    Context.current(), carrier,
    (map, key, value) -> map.put(key, value));
// carrier now contains: {"traceparent": "00-abc123-..."}

Message msg = MessageBuilder
    .withPayload(event)
    .copyHeaders(carrier)   // inject trace headers
    .build();
queue.send(msg);

// Consumer: extract and restore trace context
Map<String, String> headers = extractMessageHeaders(msg);
Context ctx = W3CTraceContextPropagator.getInstance().extract(
    Context.current(), headers,
    (map, key) -> map.get(key));
try (Scope scope = ctx.makeCurrent()) {
    // New span is a child of the original trace
    processPaymentEvent(msg.getPayload());
}
```

---

### ⚖️ Comparison Table

| Signal | What it captures | Best for | Limitation |
|---|---|---|---|
| **Traces** | Request path + timing across services | Latency root cause, service dependencies | Sampling; not all requests traced |
| **Logs** | Event details with context | What happened at a specific service | Cannot reconstruct cross-service flow |
| **Metrics** | Aggregated statistics over time | SLO measurement, alerting | No per-request detail |

**Tracing backend comparison:**

| Backend | Open source | Host | Strengths |
|---|---|---|---|
| **Jaeger** | Yes | Self-hosted | Standard, Kubernetes native |
| **Zipkin** | Yes | Self-hosted | Simple, wide client support |
| **Grafana Tempo** | Yes | Self-hosted/cloud | Grafana native, cost-efficient |
| **Honeycomb** | No | SaaS | Best-in-class query UX |
| **Datadog APM** | No | SaaS | Full observability platform |
| **AWS X-Ray** | No | AWS-only | Zero setup on AWS Lambda |

---

### 🔁 Flow / Lifecycle

**Span lifecycle from creation to storage:**

```
[1] Request arrives at service
    OTel SDK extracts traceparent header
    Creates new span (child of parent or root)
        ↓
[2] Service processes request
    Span accumulates: attributes, events, errors
    Outgoing calls propagate trace context
        ↓
[3] Request completes (or errors)
    Span.end() records end timestamp
    Duration calculated: end - start
    Status set: OK or ERROR
        ↓
[4] Span exported to OTel Collector
    OTLP protocol over gRPC (default 4317)
    Batched: max 512 spans or 5s, whichever first
        ↓
[5] Collector processes
    Tail sampling: buffer trace, decide keep/drop
    Transform: enrich with host/k8s metadata
    Forward to backend (Jaeger, Tempo, Datadog)
        ↓
[6] Backend stores trace
    Indexed by trace_id, service, duration, error
    Retained for 7-30 days typically
        ↓
[7] Engineer queries trace
    Search: service=fraud AND duration > 2s
    Waterfall view shows critical path
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Tracing replaces logging" | Tracing and logging are complementary. Traces show the flow and timing across services. Logs show what happened at a specific point. The `trace_id` links them. |
| "100% sampling is best" | At high traffic, 100% sampling is too expensive. Well-configured tail sampling (100% error traces, 1-5% normal) provides full incident visibility with 10-50x less cost. |
| "Tracing adds significant latency" | Modern OTel SDK overhead is < 1ms per span for synchronous export. Async export adds < 100 microseconds. For most services, tracing overhead is unmeasurable in production. |
| "OpenTelemetry only works with Java" | OTel supports 15+ languages with official SDKs (Java, Go, Python, Node.js, .NET, Ruby, Rust, C++). Language SDKs have varying maturity but all support traces. |
| "Span attributes are free" | Each attribute added to a span increases memory and network cost. High-cardinality attributes (user_id on every span in a high-traffic service) can cause collector memory pressure. |
| "Tracing shows all code paths" | Without manual instrumentation, auto-instrumentation only creates spans for instrumented frameworks (HTTP, gRPC, JDBC). Internal business logic is invisible unless you add custom spans. |

---

### 🚨 Failure Modes & Diagnosis

**Trace context not propagated through async boundaries**

**Symptom:**
Traces in Jaeger are fragmented. The checkout service
trace shows a payment call that terminates immediately
after the queue send. The actual payment processing
appears as a separate, unconnected trace with no parent.
The cross-service timeline is broken.

**Root Cause:**
When the checkout service sends a message to the payment
queue, it does not inject the `traceparent` header into
the message. The payment consumer creates a new root
trace instead of a child trace.

**Diagnostic Command:**
```bash
# Check if message headers contain trace context
# (example: checking a RabbitMQ message)
rabbitmqctl list_messages checkout-queue \
  | grep -i traceparent
# Empty result = trace context not propagated
```

**Fix:**
Inject W3C trace context into every message sent to a
queue. Consumer must extract and restore context before
processing.

**Prevention:**
Write an integration test: (1) send a request that
triggers a queue message, (2) assert that the resulting
log lines in the consumer contain the same `trace_id`
as the original request.

---

**Tail-based sampler dropping all error traces**

**Symptom:**
A production incident is occurring (elevated error rate).
Engineers open Jaeger to find error traces but find no
traces with errors. The trace backend appears healthy.
Error traces are missing.

**Root Cause:**
The OTel Collector tail sampling policy is misconfigured.
The policy samples traces by `status=OK` rather than
`status=ERROR`. All error traces are being dropped.

**Diagnostic Command:**
```bash
# Check OTel Collector tail sampling metrics
curl -s localhost:8888/metrics | grep \
  otelcol_processor_tail_sampling
# Look for: sampled_policy_counts by policy name
# and dropped_trace_counts
```

**Fix:**
Review the tail sampling policy configuration. The
correct priority order:
1. Policy 1: `status_code = ERROR` → always sample
2. Policy 2: `latency > 2000ms` → always sample
3. Policy 3: default → sample at 1%

**Prevention:**
Maintain a canary service that generates error traces.
Alert if no error traces appear in the tracing backend
for > 5 minutes.

---

**High-cardinality span attributes causing collector OOM**

**Symptom:**
The OTel Collector pods restart repeatedly, OOMKilled
by Kubernetes. Memory usage grows steadily until restart.
After restart, memory grows again at the same rate.

**Root Cause:**
Developers added `user_id` as a span attribute for every
service. With 1,000,000 unique users, each user has a
unique span attribute value. Tail-based sampling buffers
these spans in memory for 30 seconds per trace window.
100,000 requests/second x 30s buffer x `user_id`
attribute = millions of unique strings in memory.

**Diagnostic Command:**
```bash
# Check collector memory and identify which pipeline
# is consuming memory
kubectl top pod -n observability
# Check span attribute cardinality in collector metrics
curl -s localhost:8888/metrics | grep \
  otelcol_exporter_queue_size
```

**Fix:**
Remove `user_id` from span attributes. If user-level
tracing is needed for incidents, keep it only for error
traces using a sampling rule.

**Prevention:**
Establish a span attribute policy: attributes must be
low-cardinality (< 10,000 unique values). Use logs
with `trace_id` correlation for user-level context.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `The Three Pillars of Observability` - traces are one
  of the three signal types; understand how they
  complement metrics and logs
- `Logging Fundamentals` - `trace_id` in logs enables
  correlation with trace spans; structured logs are
  the complement to traces

**Builds On This (learn these next):**
- `OpenTelemetry Fundamentals` - the standard SDK and
  collector for distributed tracing
- `Jaeger and Zipkin` - open-source trace storage and
  query backends
- `Service Mesh Observability` - Istio/Linkerd can
  auto-propagate trace context without app code changes

**Alternatives / Comparisons:**
- `Logging Fundamentals` - logs provide event details;
  traces provide causal flow. Use both with `trace_id`
  correlation for complete incident visibility
- `Metrics Types` - metrics provide aggregated
  statistics; traces provide per-request detail

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ TRACE        │ Complete journey of one request.          │
│              │ Tree of spans with shared trace_id        │
├──────────────┼───────────────────────────────────────────┤
│ SPAN         │ One unit of work: start, end, service,    │
│              │ operation, attributes, status             │
├──────────────┼───────────────────────────────────────────┤
│ PROPAGATION  │ W3C traceparent header passed in every    │
│              │ HTTP request AND message queue header     │
├──────────────┼───────────────────────────────────────────┤
│ SAMPLING     │ Head (simple), Tail (smart, keeps errors) │
│              │ Production: 1-5% + 100% error traces      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Critical path: spans that determine total │
│              │ latency. Parallel spans not on it.        │
├──────────────┼───────────────────────────────────────────┤
│ ASYNC RISK   │ Propagate traceparent in message headers  │
│              │ or async traces are broken                │
├──────────────┼───────────────────────────────────────────┤
│ CARDINALITY  │ Low-cardinality attributes only.          │
│              │ Never user_id/request_id on hot spans     │
├──────────────┼───────────────────────────────────────────┤
│ STANDARD     │ OpenTelemetry (OTel) - use for all new    │
│              │ instrumentation. Avoid Zipkin-B3 headers. │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ OTel SDK → Jaeger → Service Mesh Tracing  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. A trace = tree of spans with a shared `trace_id`.
   Each span = one unit of work with start/end time and
   the service name. Parent-child links reconstruct the
   call tree.
2. Propagate the W3C `traceparent` header in every HTTP
   request AND every message queue header. Missing
   propagation in async calls breaks the trace tree.
3. Tail sampling (not head sampling) is the production
   choice: always keep error traces, sample normal at 1%.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Causality requires a shared identifier propagated through
every transition. Without a common key linking events
across boundaries (service calls, message queues, async
tasks), you have isolated event streams that cannot
be reconstructed into a causal narrative. This principle
applies to: distributed database transactions (distributed
transaction IDs), event sourcing (correlation IDs),
CQRS event handling (causation IDs), and microservices
debugging (trace IDs).

**Where else this pattern appears:**
- **Database distributed transactions** - a global
  transaction ID is propagated across all participating
  databases to link log entries and enable recovery.
  Same concept: shared identifier, different domain.
- **Event-driven CQRS** - an event carries both a
  `correlation_id` (the original command that started
  the workflow) and a `causation_id` (the immediate
  parent event). This reconstructs the causal chain
  through an event-driven system - same as span
  parent-child relationships.
- **Apache Kafka message tracing** - Confluent's
  `OpenTelemetry Kafka instrumentation` injects
  `traceparent` headers into Kafka messages and extracts
  them in consumers, exactly the same as HTTP trace
  propagation but for streaming.

---

### 💡 The Surprising Truth

The most counterintuitive fact about distributed tracing:
the most important spans in a trace are often the ones
you did not instrument. Auto-instrumentation creates
spans for HTTP calls, JDBC queries, and gRPC calls.
But the 3-second mystery latency is often in a business
logic loop, a serialisation step, or a cache lookup
that is invisible because it has no framework boundary.
Engineers who rely entirely on auto-instrumentation see
the skeleton of their request flow but miss the actual
bottleneck. Strategic custom span placement - around
business logic sections, not just framework calls -
is the difference between a trace that explains the
latency and one that shows the right total time but
no clear cause.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **[EXPLAIN]** Explain to a developer why the checkout
   request trace appears broken in Jaeger (the checkout
   span ends but there is no payment service span below
   it), and identify three possible causes, ranked by
   likelihood.
2. **[DEBUG]** Given a Jaeger trace showing: root span
   2800ms, checkout child span 2780ms, payment child span
   2760ms, fraud child span 2590ms - identify the critical
   path, calculate the non-fraud latency, and write the
   action item to fix the fraud service performance.
3. **[DECIDE]** For a payment service processing 5,000
   requests/second, design a sampling strategy that
   ensures 100% visibility of all error traces while
   keeping storage costs proportional to a 1% sampling
   rate for normal traces. Specify which sampler type
   to use and why.
4. **[BUILD]** Add OpenTelemetry instrumentation to a
   Spring Boot service: configure the Java agent, add
   a custom span for a business logic operation, propagate
   trace context through a RabbitMQ message, and write
   a test that verifies the trace_id appears in the
   consuming service's logs.
5. **[EXTEND]** Design the tracing strategy for an
   event-driven checkout workflow: HTTP request → Kafka
   topic → payment consumer → Kafka topic → fulfillment
   consumer. Specify how trace context flows through
   each Kafka message, what the resulting trace tree
   looks like, and how to handle the case where a
   Kafka consumer restarts and reprocesses old messages.

---

### 🧠 Think About This Before We Continue

**Q1.** Your checkout service sends 3 parallel requests
to: inventory service (100ms), pricing service (80ms),
and tax service (950ms). After all 3 return, checkout
calls payment service (200ms). Total checkout latency
is 1200ms. Your SLO is P99 < 1 second. A junior
engineer proposes optimising the inventory service from
100ms to 50ms. Using the trace data above, explain why
this optimisation will not help, identify which service
is on the critical path, and calculate the maximum
possible improvement from optimising that service.
*Hint: Parallel spans do not affect total latency -
only the slowest one does. The critical path is:
max(parallel) + sequential. Identify it from the
trace data provided.*

**Q2.** You are seeing fragmented traces in Jaeger:
checkout service traces terminate at a Kafka publish,
and payment service traces start as root traces (no
parent). What code change is needed in the producer,
what code change is needed in the consumer, and how
would you write an integration test to verify the
fix works? Provide the specific Java/Spring code for
both producer and consumer using OpenTelemetry.
*Hint: Producer must inject W3C traceparent into
Kafka message headers. Consumer must extract the
traceparent from Kafka headers and use it as the
parent context before creating the processing span.*

**Q3 (TYPE G):** You are designing the observability
strategy for a new payment platform with these
characteristics: 10,000 transactions/second at peak,
50 microservices, P99 SLO of 500ms for checkout,
regulatory requirement to keep all error events for
7 years, budget of $50,000/month for observability
infrastructure. Design the complete tracing strategy:
sampling policy (head vs tail, rates), backend choice,
retention policy, how you handle the 7-year error
retention requirement, and how you test that no error
traces are being dropped.
*Hint: At 10,000 TPS, 100% tracing = ~50,000 spans/s
(5 services per transaction). At 1KB/span, that is
50MB/s = 4.3TB/day of trace data. Budget of $50,000/month
limits retention to ~30 days at $0.10/GB. Tail sampling
at 1% (+ 100% error) = 430GB/day - manageable. The 7-year
error retention is a compliance requirement that needs
separate storage (S3 cold storage) at much lower cost
than the trace backend.*

---

### 🎯 Interview Deep-Dive

**Q1: "What is a span and what information does it contain?
How do spans relate to a trace?"**
*Why they ask:* Tests foundational understanding of
distributed tracing data model.
*Strong answer includes:*
- A span = one unit of work: single operation within
  a service. Contains: trace_id (same for all spans
  in the trace), span_id (unique), parent_span_id
  (links to calling span), service name, operation name,
  start time, end time, status (OK/ERROR), key-value
  attributes, events (timestamped log entries within span)
- A trace = tree of spans with the same trace_id.
  The root span has no parent. Parent-child relationships
  reconstruct the call tree.
- Key point: `trace_id` is the thread connecting all
  spans. Without it, you have individual timing records
  that cannot be assembled into a causal narrative.

**Q2: "Explain head sampling vs tail sampling.
Which should you use in production and why?"**
*Why they ask:* Tests whether the candidate understands
the real-world trade-offs of tracing, not just the concept.
*Strong answer includes:*
- Head sampling: decision made at the root span before
  the trace completes. Simple. Consistent (child spans
  are always sampled if parent is). Problem: a 1% head
  sample means 99% of error traces are dropped.
- Tail sampling: decision made after the trace completes
  (30s window). Can always keep error traces. Can keep
  slow traces. Requires buffering full traces in memory
  in the OTel Collector - operationally complex.
- Production choice: tail sampling with policies:
  (1) error → keep 100%, (2) duration > 2s → keep 100%,
  (3) default → sample 1%.
- When head sampling is OK: very high QPS where tail
  sampling buffer is too expensive, or when error rate
  is very low (< 0.01%) so error traces are preserved
  by chance at 1% head sample.

**Q3: "A developer asks why their checkout trace shows
only 3 spans for a request that touches 12 services.
What are the possible explanations, and how would you
diagnose each?"**
*Why they ask:* Tests practical debugging ability with
distributed tracing - a common real-world gap.
*Strong answer includes:*
- Possible cause 1: Auto-instrumentation not installed
  on 9 of the services. Diagnosis: check that OTel Java
  agent is in the startup command for each service.
- Possible cause 2: Trace context not propagated through
  an async message boundary (e.g., Kafka). Diagnosis:
  check if there is a queue between some services; verify
  that `traceparent` header is in outgoing messages.
- Possible cause 3: Sampling is dropping spans from
  some services. Diagnosis: check OTel Collector
  tail sampling policy - ensure child spans are always
  sampled when parent is sampled.
- Possible cause 4: Some services use a different
  trace propagation format (Zipkin B3 headers vs W3C
  traceparent). Diagnosis: check which propagator is
  configured on each service.
