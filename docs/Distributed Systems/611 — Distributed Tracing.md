---
layout: default
title: "Distributed Tracing"
parent: "Distributed Systems"
nav_order: 611
permalink: /distributed-systems/distributed-tracing/
number: "0611"
category: Distributed Systems
difficulty: ★★★
depends_on: Correlation ID, Observability, Microservices, HTTP & APIs
used_by: Service Mesh, OpenTelemetry, Jaeger, Zipkin, SRE
related: Correlation ID, Logging, Metrics, Service Mesh, OpenTelemetry
tags:
  - distributed
  - observability
  - debugging
  - sre
  - deep-dive
---

# 611 — Distributed Tracing

⚡ TL;DR — Distributed tracing records the path a request takes through every microservice, annotating each span with timing and metadata, so engineers can visualize the full call tree, identify which service introduced latency or errors, and debug cross-service performance problems.

| #611            | Category: Distributed Systems                                 | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------ | :-------------- |
| **Depends on:** | Correlation ID, Observability, Microservices, HTTP & APIs     |                 |
| **Used by:**    | Service Mesh, OpenTelemetry, Jaeger, Zipkin, SRE              |                 |
| **Related:**    | Correlation ID, Logging, Metrics, Service Mesh, OpenTelemetry |                 |

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A user reports their checkout takes 8 seconds (it should take 1 second). The checkout service calls 12 microservices. You look at logs in Service A — nothing unusual. Service B — a few slow queries. Service C — fine. Service D — fine... After 40 minutes of log-diving across 12 services — in 12 different dashboards with 12 different log formats — you find that Service H called Service I, which called an external API, which was taking 6 extra seconds due to a connection pool exhaustion bug.

**WITH DISTRIBUTED TRACING:**
You look up the trace ID from the slow checkout request. The tracing system shows a flame chart: Service A → B → C (all fine), A → D (fine), A → H → I → ExternalAPI (6 seconds in ExternalAPI). One screen, one view, root cause obvious in 2 minutes.

---

### 📘 Textbook Definition

**Distributed tracing** records the end-to-end journey of a request as it propagates through a distributed system. Key concepts: **Trace** — the complete picture of a single request's path across all services (identified by a globally unique `trace_id`). **Span** — a single unit of work within a trace (identified by `span_id`); has a parent span (forming a tree). **Parent span** — the span that created the current span; root span has no parent. **Context propagation** — passing trace context (`trace_id`, `parent_span_id`) through HTTP headers or message metadata so each service can link its span to the correct trace. **Sampling** — only recording a fraction of traces (e.g., 1%) to limit storage and overhead; head-based (decide at entry) vs. tail-based (decide after seeing full trace outcome). Standards: **OpenTelemetry** (OTEL) — vendor-neutral SDK and specification; **W3C Trace Context** — HTTP header standard (`traceparent`, `tracestate`).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Attach a unique ID to every request, pass it through every service, and record the timing and metadata of every hop — then visualize the entire call tree as one trace.

**One analogy:**

> Distributed tracing is like a parcel tracking system for requests. Each service the package passes through scans it and logs: "arrived at Service B at 10:00:01.234, left at 10:00:01.250 — 16ms processing time." The parcel tracking dashboard shows the complete journey: originated at ServiceA, went through B, C, D — stopped for 6 seconds at carrier ServiceH because the warehouse (ExternalAPI) was backed up.

**One insight:**
The most common mistake is treating distributed tracing as just "colored logs." It's fundamentally a **timing tree** — the parent-child span relationship that shows which work is sequential vs. parallel, what the critical path is, and where the latency actually sits. Without the tree structure, you have the same problem as reading flat logs.

---

### 🔩 First Principles Explanation

**TRACE STRUCTURE:**

```
Trace ID: abc-123 (same across ALL services for this request)

Span Tree:
  [0ms - 250ms] API Gateway (root span, parent=none)
  │  span_id: s1, trace_id: abc-123, service: api-gateway
  │
  ├─[5ms - 80ms] Product Service (child of s1)
  │  span_id: s2, parent_span_id: s1, service: product-svc
  │  │
  │  └─[10ms - 75ms] DB Query (child of s2)
  │     span_id: s3, parent_span_id: s2, operation: db.query
  │     attributes: {db.statement: "SELECT * FROM products WHERE id=?"}
  │
  ├─[82ms - 90ms] Inventory Service (child of s1)
  │  span_id: s4, parent_span_id: s1, service: inventory-svc
  │
  └─[91ms - 240ms] Payment Service (child of s1)
     span_id: s5, parent_span_id: s1, service: payment-svc
     │
     └─[95ms - 235ms] External Payment API (child of s5)
        span_id: s6, parent_span_id: s5, service: stripe
        ERROR: timeout after 140ms

Critical path = Gateway → Payment → Stripe (140ms of the 250ms total)
```

**W3C TRACEPARENT HEADER:**

```
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
              ^^ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^^ ^^
              version  trace_id (128-bit hex)      span_id (64-bit) flags

When Service A calls Service B:
  Service A: creates span with new span_id (s2).
  Service A: sends HTTP request to Service B with header:
    traceparent: 00-{SAME trace_id}-{A's span_id}-01

  Service B: extracts trace_id and parent_span_id from header.
  Service B: creates its own span with parent = A's span_id.
  Service B: everything Service B logs is linked to the trace.
```

**OPENTELEMETRY INSTRUMENTATION (JAVA):**

```java
// Manual instrumentation:
@GetMapping("/checkout/{orderId}")
public ResponseEntity<CheckoutResponse> checkout(@PathVariable String orderId,
                                                  HttpServletRequest request) {
    // Get current span (auto-instrumented by OTel Java agent):
    Span span = Span.current();
    span.setAttribute("order.id", orderId);
    span.setAttribute("user.id", getCurrentUserId());

    // Create child span for a specific operation:
    Tracer tracer = GlobalOpenTelemetry.getTracer("checkout-service");
    Span paymentSpan = tracer.spanBuilder("process-payment")
        .setAttribute("payment.amount", order.getTotal())
        .startSpan();

    try (Scope scope = paymentSpan.makeCurrent()) {
        PaymentResult result = paymentService.process(orderId);
        paymentSpan.setAttribute("payment.status", result.getStatus());
        return ResponseEntity.ok(new CheckoutResponse(result));
    } catch (PaymentException e) {
        paymentSpan.recordException(e);
        paymentSpan.setStatus(StatusCode.ERROR, e.getMessage());
        throw e;
    } finally {
        paymentSpan.end();
    }
}

// OTel Java Agent auto-instruments:
// Spring MVC, RestTemplate, WebClient, JDBC, Kafka,
// AWS SDK, MongoDB, Redis, gRPC — zero code changes needed.
```

**SAMPLING STRATEGIES:**

```
Head-Based Sampling (decide at trace entry point):
  Always sample: 100% traces recorded. High storage/CPU cost.
  Rate-based: sample 1% of traces. Miss slow/error traces in the 99%.

Tail-Based Sampling (decide AFTER seeing full trace):
  Collect all spans. Evaluate completed trace:
    - Trace has ERROR → KEEP (always capture errors)
    - Trace took > p95 latency → KEEP (capture outliers)
    - Trace is routine → DROP (save storage)
  Requires: collector holds all spans in memory until trace completes.
  Used by: Honeycomb, Grafana Tempo (with OTel Collector tail sampling processor).
  Benefits: never miss an error trace; storage same as head-based at same sampling rate.
```

---

### 🧪 Thought Experiment

**TRACING WITHOUT CONTEXT PROPAGATION:**

Service A sends request to B. Service B creates a new trace_id (doesn't extract trace context from A's header). Service C is called by B and creates yet another trace_id.

Result: 3 disconnected traces. The tracing dashboard shows 3 orphaned 1-span traces instead of one 3-span tree. You have no way to correlate them. This is the #1 tracing implementation bug: forgetting to propagate the traceparent header when making downstream calls.

**ASYNC CONTEXT LOSS:**

Service A handles request on thread T1. Creates a span. Queues work on a thread pool — work runs on thread T2. Thread T2 has no OTel context — no span parent.

Fix: use OTel's `Context.current().wrap(runnable)` when submitting to thread pools. This carriers the OTel context from T1 to T2, maintaining the parent-child span relationship across thread boundaries.

---

### 🧠 Mental Model / Analogy

> Distributed tracing is like a surgical procedure time log. Each surgeon, anesthesiologist, and nurse logs: "I started my task at 10:30:14, finished at 10:31:22." The hospital coordinator can reconstruct the full operation timeline: who was doing what, in parallel or sequentially, and exactly where the 3-hour operation spent its time. Without this log, post-op analysis is impossible: "the operation took longer than expected" — but where?

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Attach a trace_id to each request. Pass it through every service. Log the start/end time in each service. Visualize as a flame chart. Find which service was slow.

**Level 2:** Trace (full request), Span (unit of work), parent-child relationships form a tree. W3C traceparent header for propagation. OpenTelemetry SDK + Jaeger/Zipkin/Tempo/Honeycomb for collection and visualization. Sampling: head-based (fast, cheap) vs. tail-based (smarter, catches all errors).

**Level 3:** OTel Java agent: auto-instruments JDBC, HTTP clients, Kafka, Spring MVC, AWS SDK — zero code. Manual instrumentation for business-level spans (payment processing, recommendation computation). Span attributes: `user.id`, `order.id`, `db.statement` — enable filtering and searching traces by business context. Exemplars: link traces to Prometheus/Grafana metrics (e.g., a spike in p99 latency links directly to a specific trace showing the root cause).

**Level 4:** Trace-based testing: use traces in integration tests to assert performance contracts (e.g., "checkout must complete within 500ms, and payment span must be < 200ms"). Performance regression catches via trace diff: compare trace flame charts of the same request before and after a code change to identify new slowness. Distributed tracing is the "structured logging for requests" — just as structured logs are machine-parseable, traces are machine-queryable by span attributes and timing. Red-green deployment validation: compare trace distributions from canary (new) vs. stable (old) traffic to detect performance regressions before full rollout.

---

### ⚙️ How It Works (Mechanism)

**OpenTelemetry with Spring Boot (Auto-instrumentation):**

```yaml
# application.yml
management:
  tracing:
    sampling:
      probability: 1.0 # 100% sampling in dev; use 0.01 in prod


# Add OTel Java Agent to JVM:
# -javaagent:/path/to/opentelemetry-javaagent.jar
# Configure exporter:
# OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4318/v1/traces
# OTEL_SERVICE_NAME=checkout-service
```

---

### ⚖️ Comparison Table

| Tool          | Type        | Backend     | Best For                              |
| ------------- | ----------- | ----------- | ------------------------------------- |
| Jaeger        | Open source | Self-hosted | Kubernetes environments               |
| Zipkin        | Open source | Self-hosted | Simple setups                         |
| Grafana Tempo | Open source | Self-hosted | Free-form trace storage               |
| Honeycomb     | SaaS        | Managed     | Tail-based sampling, powerful queries |
| AWS X-Ray     | SaaS        | AWS-managed | AWS native environments               |
| Datadog APM   | SaaS        | Managed     | Full observability platform           |

---

### ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                                                                                                                    |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Distributed tracing replaces logging    | Traces tell you WHERE and HOW LONG; logs tell you WHAT HAPPENED. Use both: traces for navigation, logs for details                                                         |
| You need 100% sampling to find problems | Tail-based sampling at 5% captures 100% of errors and p99 latencies with 5% storage cost                                                                                   |
| Auto-instrumentation is sufficient      | Auto-instrumentation captures infrastructure spans (HTTP, DB). Business spans (saga steps, payment processing stages) require manual instrumentation for meaningful traces |

---

### 🚨 Failure Modes & Diagnosis

**Orphaned Spans (No Context Propagation)**

Symptom: Jaeger shows hundreds of single-span "micro-traces" — each a lone span with no
parent. User's checkout trace doesn't appear as one unified tree.

Cause: RestTemplate/HttpClient calls missing OTel context propagation. Async executor
(ThreadPoolExecutor) loses OTel context when switching threads.

Fix: (1) Use OTel Java agent (auto-injects context into RestTemplate, WebClient).
(2) For custom async: wrap runnable with `Context.current().wrap(() -> ...)`.
(3) For Kafka: include trace headers in ProducerRecord; extract in consumer.
(4) Verify: in test, assert that child service spans have parent_span_id matching
the calling service's span_id — this is a testable invariant.

---

### 🔗 Related Keywords

- `Correlation ID` — simplest form of request tracking; distributed tracing extends it to full trees
- `Observability` — tracing is one of the three pillars (logs, metrics, traces)
- `Service Mesh` — can inject trace headers automatically at the sidecar level
- `OpenTelemetry` — the standard SDK for traces, metrics, and logs
- `Saga Pattern` — tracing saga steps end-to-end requires trace propagation through message queues

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  DISTRIBUTED TRACING: request path + timing tree        │
│  Trace = full request journey (1 trace_id)              │
│  Span = 1 unit of work (start/end time + attributes)    │
│  Propagation: W3C traceparent header across all hops    │
│  OTel: auto-instrument HTTP/DB/Kafka + manual spans      │
│  Sampling: tail-based = capture all errors cheaply      │
│  Visualize: Jaeger / Grafana Tempo / Honeycomb          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A trace shows: checkout spans 250ms total. Product service span = 10ms. Inventory service span = 5ms. Payment service span = 235ms. Within the payment span, the external Stripe API span = 220ms. The Stripe API normally responds in 80ms. Reconstruct what happened: what is the "critical path"? What should you investigate? What instrumentation would you add to the payment service to provide more detail within the 220ms Stripe span?

**Q2.** You're adding distributed tracing to a system that uses Kafka for async communication. Service A sends a Kafka message → Service B processes it → Service B publishes another message → Service C processes it. How do you propagate the trace_id across the two Kafka message boundaries? Specifically: (a) where in the Kafka ProducerRecord do you put the trace context, (b) how does the consumer extract it, and (c) should Service B's processing span be a child of Service A's publishing span or a new root span?
