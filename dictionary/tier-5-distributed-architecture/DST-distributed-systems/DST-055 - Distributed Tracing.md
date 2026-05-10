---
id: DST-061
title: "Distributed Tracing"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-031
related: DST-031, DST-059
tags:
  - distributed
  - observability
  - deep-dive
  - advanced
  - production
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 55
permalink: /distributed-systems/distributed-tracing/
---

# DST-058 - Distributed Tracing

⚡ TL;DR - Distributed tracing reconstructs the complete execution path of a request across multiple microservices by propagating a unique trace context through every service call — making the otherwise invisible inter-service journey visible for debugging, performance analysis, and reliability engineering.

| Metadata        |                  |     |
| :-------------- | :--------------- | :-- |
| **Depends on:** | DST-031          |     |
| **Related:**    | DST-031, DST-059 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A user reports: "My order was slow — took 8 seconds." Your system has 12 microservices involved in the order path. Each service has its own logs. To debug: you search through 12 log files, trying to correlate entries by timestamp and order ID. Service A's log: "processed in 200ms." Service B's log: "processed in 500ms." But which INSTANCE of B handled THIS request? Did B call C, which called D, which called the slow database? Without tracing: you're reconstructing a distributed timeline from scattered log files — manual, slow, error-prone, and often impossible when the system is under load (logs from concurrent requests intermix).

**THE BREAKING POINT:**
At Google's scale (2003-2010): thousands of RPCs per user request, hundreds of services, millions of concurrent users. When a request was slow: which of the thousands of services was responsible? Log-based debugging was infeasible — the data volume was too high, the correlation too complex. Google needed a way to observe a request's path END-TO-END, with timing for each segment, without instrumenting every function call manually. The result: Dapper (2010 paper) — the foundational distributed tracing system that all modern tools (Jaeger, Zipkin, OpenTelemetry) are based on.

**THE INVENTION MOMENT:**
Google's Dapper paper (2010) introduced the core primitives still used today: **Trace** (the complete journey of one request), **Span** (one operation within the trace, with start/end timestamp), **SpanContext** (the trace ID + span ID propagated across service boundaries). The insight: instrument at the RPC/HTTP level, not at the application code level. Every outgoing call automatically creates a child span. The trace is reconstructed from collected spans by a trace backend. Minimal application code changes required.

**EVOLUTION:**
2010: Google Dapper paper — foundational concepts. 2012: Twitter Zipkin — open-source Dapper implementation. 2016: Uber Jaeger — OpenTracing-compatible, high-volume. 2016: OpenTracing spec (vendor-neutral API). 2019: OpenCensus (Google) merges with OpenTracing → OpenTelemetry. 2021: OpenTelemetry GA — the unified standard for traces, metrics, and logs. 2022+: W3C TraceContext standard for HTTP propagation headers. Today: OpenTelemetry is the de facto standard; Jaeger, Zipkin, Tempo, X-Ray are trace backends.

---

### 📘 Textbook Definition

**Distributed tracing** is an observability technique that records the path of a request as it propagates through a distributed system, capturing timing information for each segment (span) and linking all segments via shared identifiers (trace ID). **Core concepts:** (1) **Trace:** the complete record of one request's journey. Identified by a globally unique `traceId`. (2) **Span:** a named, timed operation within a trace. Has `traceId`, `spanId`, `parentSpanId`, start time, duration, service name, operation name, and key-value tags. (3) **SpanContext:** the minimal information propagated across service boundaries: `traceId + spanId + flags`. Propagated in HTTP headers (`traceparent` in W3C standard), gRPC metadata, Kafka message headers. (4) **Sampling:** not every request is traced (would double the data volume). Head-based sampling: decide at trace start (e.g., 1% of requests). Tail-based sampling: decide after trace completes (trace all requests > 1 second). (5) **Backend:** Jaeger, Zipkin, Tempo, AWS X-Ray collect spans and reconstruct the trace tree for visualization and querying.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Attach a unique ID to every request, propagate it through every service, collect timing records — reconstruct the whole journey.

> Distributed tracing is like a package tracking system. The package (request) gets a tracking number (traceId) at origin. At each carrier facility (service): a scan is logged (span) with timestamp, location, duration. The tracking website (Jaeger UI) assembles all scans into a timeline: you see the complete journey, where it slowed down, where it branched. Without tracking: you'd call each facility separately and hope they can find your package in their logs.

**One insight:** Tracing doesn't require changing business logic. Auto-instrumentation (Java agent, Python auto-instrument, Node.js SDK) instruments HTTP clients, databases, and message brokers automatically — application code is unmodified. The tracing infrastructure is transparent.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **traceId must be globally unique and propagated.** Same traceId across all services for one request. If any service creates a new traceId: the chain breaks. Propagation must be universal — every HTTP client, Kafka producer, gRPC stub must propagate the context.
2. **Spans must be collected and shipped asynchronously.** Tracing adds latency only if span collection is synchronous. The exporter must be async (fire-and-forget to collector). Span export must not fail the request if the collector is unavailable.
3. **Sampling is mandatory at scale.** Tracing 100% of requests at 100,000 req/s generates 100,000 spans/s × (average 10 spans/trace) = 1,000,000 spans/s. Storage cost is prohibitive. Sample: 1% → 10,000 spans/s. Use tail-based sampling to keep 100% of slow/error traces while sampling fast successful traces.
4. **SpanContext propagation defines service boundaries.** If a service makes an async call (thread handoff, event publication): it must pass SpanContext to the new thread/event. Without explicit propagation: the trace breaks at async boundaries.

**DERIVED DESIGN:**

```
Request enters Service A:
  1. Extract SpanContext from incoming HTTP headers
     (or create new Span if first service)
  2. Start child Span: {traceId, new spanId,
     parentSpanId=incoming spanId}
  3. Set span attributes: HTTP method, URL, service name
  4. Execute business logic
  5. On each outgoing call: inject SpanContext into headers
  6. On completion: record duration, status, end span
  7. Export span asynchronously to OpenTelemetry Collector
```

**THE TRADE-OFFS:**
**Gain:** End-to-end visibility across service boundaries. Bottleneck identification (which span is slow?). Error propagation tracking (where did the error originate?). Dependency map (which services call which?).
**Cost:** Overhead (serialization, export — typically 1-3ms per request). Storage (sampled traces). Configuration complexity (propagation through every transport type). Sampling decision affects which traces are visible.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Async boundaries (thread handoffs, Kafka, message queues) require explicit SpanContext propagation — there is no automatic mechanism for this. Each async transport must be instrumented specifically.
**Accidental:** W3C TraceContext vs B3 headers vs Datadog headers — different propagation formats, same concept. OpenTelemetry Java vs Python vs Node.js SDK — same API, different language bindings.

---

### 🧪 Thought Experiment

**SETUP:** User request hits API Gateway → Service A → Service B → Database. Total time: 3 seconds. SLO: 1 second. Which component is responsible?

**WITHOUT DISTRIBUTED TRACING:**

- API Gateway log: `order/place 200 3001ms` (total time only)
- Service A log: `handleOrder 200 2800ms` (A's total, includes waiting for B)
- Service B log: `reserveInventory 200 1500ms` (B's total)
- Database log: hundreds of queries from many services — can't tell which belong to this request.
- To debug: manually correlate logs by timestamp and orderId. In high-traffic system: 50 other requests also running at the same time. Timestamps overlap. Manual correlation takes 30-60 minutes.

**WITH DISTRIBUTED TRACING:**

- Query Jaeger for traceId=abc123.
- See trace tree:
  ```
  [API Gateway] 3001ms
    [Service A: handleOrder] 2800ms
      [HTTP call to B: reserveInventory] 1800ms  ← slow
        [Service B: processReservation] 1500ms
          [DB: SELECT * FROM inventory] 1400ms   ← root cause
  ```
- Root cause: DB query in Service B taking 1.4 seconds.
- Time to diagnosis: 30 seconds. Not 30 minutes.

**THE INSIGHT:** Distributed tracing converts an O(N×log_files) debugging problem (search N log files, correlate manually) into an O(1) problem (query trace by ID, see the complete picture). The time savings compound with system complexity — the more services, the more valuable tracing becomes.

---

### 🧠 Mental Model / Analogy

> Distributed tracing is like an airport flight management system. Every flight (request) has a flight number (traceId). At each airport (service): arrival time, departure time, gate, and duration on ground are logged (spans). The flight operations center (Jaeger/Zipkin) sees every flight's complete itinerary: departed JFK at 14:00, arrived Chicago at 16:30, departed Chicago at 18:00, arrived LAX at 20:15. A delay at Chicago (slow service B) is immediately visible in the complete timeline.

**Mapping:**

- **Flight number** → traceId (globally unique, same across all legs)
- **Airport log** → span (service name, operation, timestamps)
- **Leg of the flight** → one span (one operation in one service)
- **Connecting flight** → parent-child span relationship
- **Flight operations center** → Jaeger/Zipkin UI (reconstructed trace)

Where this analogy breaks down: flights are sequential (JFK → Chicago → LAX). Distributed traces can be parallel — Service A calls B and C simultaneously. The trace tree is a DAG (directed acyclic graph), not a linear path. The flight analogy holds for sequential calls but breaks for fan-out patterns.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When a user clicks "Buy," the request travels through 10 different programs before the order is confirmed. Distributed tracing puts a label (like a package tracking number) on the request. Every program the request visits records: "I saw this request, it took me 200ms." At the end: you can see the complete journey — which program was slow, which was fast, where the request spent most of its time.

**Level 2 - How to use it (junior developer):**
Add OpenTelemetry to your Java service:

```xml
<!-- pom.xml -->
<dependency>
  <groupId>io.opentelemetry</groupId>
  <artifactId>opentelemetry-sdk</artifactId>
  <version>1.38.0</version>
</dependency>
```

Java agent (zero code changes): `java -javaagent:opentelemetry-javaagent.jar -jar myapp.jar`. The agent auto-instruments Spring MVC, Spring WebFlux, JDBC, HttpClient, Kafka. Every HTTP request: automatic span creation. Every outgoing call: automatic context propagation. Send to Jaeger: `-Dotel.exporter.otlp.endpoint=http://jaeger:4317`.

**Level 3 - How it works (mid-level engineer):**
W3C TraceContext header (`traceparent`): `00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`. Format: `version-traceId(32hex)-parentSpanId(16hex)-flags(2hex)`. Every HTTP client injects this header on outgoing requests. Every HTTP server extracts it on incoming requests. The trace backend receives spans via OTLP (OpenTelemetry Protocol) — either gRPC or HTTP/protobuf. Jaeger stores spans in Cassandra or Elasticsearch. Reconstruction: query by traceId, load all spans, build parent-child tree using `parentSpanId` links.

**Level 4 - Why it was designed this way (senior/staff):**
Google Dapper's critical design decision: per-call overhead must be < 0.01% of total request latency for tracing to be "always on." This required: (1) Sampling (not every request traced). (2) Async export (spans queued and shipped in batch, not blocking the request). (3) Minimal data per span (only: traceId, spanId, parentSpanId, timestamp, duration, service name, operation name). Application-level annotations (tags) are optional. The design succeeded: Dapper ran at Google with 1/1024 sampling (0.1%) and provided meaningful coverage because of the volume of traffic. Modern OpenTelemetry: W3C standardized the propagation format, OTLP standardized the export protocol. Vendor lock-in is eliminated — instrument once, send to any backend.

**Expert Thinking Cues:**

- "Trace is broken — spans from Service B don't appear under Service A's span" → Context propagation failed. Check: does Service A's HTTP client inject `traceparent` header? Check: does Service B's server extract `traceparent`? Common issue: `RestTemplate` is not the instrumented instance (application created a `new RestTemplate()` instead of using the Spring-managed auto-instrumented one). Fix: use `@Autowired RestTemplate` or `@Bean RestTemplate` with OTel SDK-provided interceptor.
- "Traces appear in Jaeger but without database spans" → JDBC auto-instrumentation not active. Check: is the JDBC instrumentation in the agent jar? `opentelemetry-javaagent.jar` includes JDBC. But: if using a non-standard driver or connection pool: may need explicit instrumentation. Also: check OTEL_JAVAAGENT_ENABLED=true env var.
- "Sampling is 1% but I need to see traces for specific users" → Use attribute-based sampling with Collector sampling rules: keep 100% of traces where `user.tier=premium` or `http.status_code=5xx`. This is "tail-based sampling" at the Collector level. Configure OpenTelemetry Collector with `tailsampling` processor: rule `status_code=ERROR → sample_rate=100%`.

---

### ⚙️ How It Works (Mechanism)

**Span propagation through service chain:**

```
Client                Service A             Service B
  │                       │                     │
  │─GET /order─────────────▶                    │
  │  (no traceparent yet)  │                    │
  │                        │ create root Span:  │
  │                        │ traceId=abc        │
  │                        │ spanId=001         │
  │                        │─GET /inventory──────▶
  │                        │  traceparent:       │
  │                        │  00-abc-001-01      │
  │                        │                     │ create child Span:
  │                        │                     │ traceId=abc
  │                        │                     │ spanId=002
  │                        │                     │ parentSpanId=001
  │                        │◀─200────────────────│ end span 002
  │◀─200───────────────────│ end span 001        │
                           │                     │
  [Both spans exported async to OTLP Collector]
  [Collector sends to Jaeger]
  [Jaeger reconstructs: span 002 under span 001]
```

**Sampling strategies:**

```
HEAD-BASED (decide at trace start):
  On root span creation: random(0-1) < 0.01 → sample
  Propagated as Sampled flag in traceparent
  All downstream services respect the flag
  Cost: can't prefer slow/error traces

TAIL-BASED (decide after trace completes):
  Collector receives ALL spans for all traces
  After trace completes: evaluate rules:
    error=true → keep (100%)
    duration>1s → keep (100%)
    otherwise → drop (99%)
  Cost: Collector must buffer all spans temporarily
```

---

### 🔄 The Complete Picture - End-to-End Flow

**TRACE LIFECYCLE:**

```
User  Gateway  OrderSvc  InvSvc  DB  Collector  Jaeger
  │      │        │         │    │       │          │
  │─req──▶        │         │    │       │          │
  │       │create root      │    │       │          │
  │       │ span (traceId)  │    │       │          │
  │       │─call────────────▶    │       │          │
  │       │  (propagate context) │       │          │
  │       │        │create child │       │          │
  │       │        │ span        │       │          │
  │       │        │─query──────▶│       │          │
  │       │        │        ← YOU ARE HERE          │
  │       │        │◀─result─────│       │          │
  │       │        │ end span ───────────▶           │
  │       │◀───────│             │   [async export]  │
  │       │ end span─────────────▶           │       │
  │◀──────│ [async export]                   │       │
  │                                          │─spans─▶│
  │                                      [reconstruct trace]
```

**WHAT CHANGES AT SCALE:**
At scale: tail-based sampling becomes critical. At 100,000 req/s with head-based 1% sampling: only 1,000 req/s are traced. If a bug affects 0.1% of requests: statistically, only 1 per 1,000 traced requests shows the bug → 0.001 per second. Hard to find. With tail-based: all error requests are kept regardless of sampling rate — the 0.1% bug is visible in 100% of error cases.

---

### 💻 Code Example

**BAD - Manual correlation ID logging (pre-tracing):**

```java
// BAD: manual correlation, no cross-service linking
// Different log format in every service
// Correlation by timestamp = unreliable under load
@GetMapping("/order/{id}")
public Order getOrder(@PathVariable String id,
    HttpServletRequest req) {
    String corrId = req.getHeader("X-Correlation-Id");
    log.info("[{}] getOrder called for {}", corrId, id);
    // corrId not propagated to downstream calls
    // No timing data per segment
    return orderService.get(id);
}
```

**GOOD - OpenTelemetry auto-instrumentation + manual spans:**

```java
// GOOD: Java agent handles HTTP + JDBC automatically
// Add manual spans only for business-critical segments

@Service
public class OrderService {
    private final Tracer tracer = GlobalOpenTelemetry
        .getTracer("order-service");

    public Order processOrder(String orderId) {
        // Create a child span for a specific business step
        Span span = tracer.spanBuilder("validate-fraud")
            .startSpan();
        try (Scope scope = span.makeCurrent()) {
            span.setAttribute("order.id", orderId);
            span.setAttribute("order.type", "standard");
            FraudResult result = fraudService.check(orderId);
            span.setAttribute("fraud.score",
                result.getScore());
            if (result.isSuspicious()) {
                span.addEvent("fraud-flagged");
                span.setStatus(StatusCode.ERROR,
                    "Fraud check failed");
            }
            return result;
        } catch (Exception e) {
            span.recordException(e);
            span.setStatus(StatusCode.ERROR,
                e.getMessage());
            throw e;
        } finally {
            span.end(); // ALWAYS end span in finally
        }
    }
}

// Async context propagation (manual):
public void processAsync(String orderId) {
    Context ctx = Context.current();
    executor.submit(() -> {
        // Propagate context to new thread explicitly:
        try (Scope scope = ctx.makeCurrent()) {
            // Child spans here will appear under parent trace
            doAsyncWork(orderId);
        }
    });
}
```

---

### ⚖️ Comparison Table

| Observability signal | Traces                      | Metrics                 | Logs                 |
| :------------------- | :-------------------------- | :---------------------- | :------------------- |
| Granularity          | Per-request, per-span       | Aggregated (rates, p99) | Per-event (line)     |
| Correlation          | Cross-service via traceId   | None                    | By timestamp, corrId |
| Volume               | Sampled (1-100%)            | All (aggregated)        | All (filtered)       |
| Best for             | Root cause in one request   | System-wide trends      | Event details        |
| Latency data         | Yes (per span, per segment) | Yes (aggregated)        | No                   |
| Error context        | Yes (trace of error path)   | Error rate only         | Error message        |

---

### ⚠️ Common Misconceptions

| Misconception                                                        | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| :------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Distributed tracing replaces logging"                               | Traces and logs are complementary. Traces show the STRUCTURE (which services, which order, how long each). Logs show the CONTENT (what happened within a span — error messages, SQL queries, business events). Best practice: correlate logs to traces by storing traceId in log records. Then: from trace → click to logs for that span. Neither replaces the other.                                                                                                          |
| "100% sampling gives complete visibility"                            | 100% sampling at high volume creates problems: 10× storage cost, 10× export overhead, Jaeger/backend may not handle the volume. More importantly: you don't need 100% sampling for most debugging — 1% sampling gives statistical coverage for performance analysis. Use tail-based sampling to keep 100% of ERROR and SLOW traces (the ones you actually need) while sampling successful fast traces at 1%.                                                                   |
| "OpenTelemetry auto-instrumentation traces everything automatically" | Auto-instrumentation covers: HTTP clients, HTTP servers, JDBC, Spring, gRPC, Kafka, Redis (for supported libraries). It does NOT cover: async work dispatched to executor services without context propagation, custom binary protocols, in-process queues. For those: manual instrumentation is required. Review: every async boundary in your code needs explicit `Context.makeCurrent()` propagation.                                                                       |
| "Span timing shows database query time"                              | Span timing shows the client-side duration of the database call (from when the client sent the query to when it received the response). This includes: network RTT + database processing time. To measure database processing time alone: instrument the database (Postgres pg_stat_statements, MySQL performance_schema). Client-side span duration is useful for "how long did this DB call take from my service's perspective?" — which is what matters for SLO compliance. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Broken Trace at Async Boundary**

**Symptom:** Jaeger shows trace with spans from Service A, then Kafka message published, then... nothing. Service B consumed the message and processed it, but Service B's spans appear as orphaned root traces (separate, unlinked). Cannot trace the end-to-end path through Kafka.
**Root Cause:** Kafka producer does not inject `traceparent` into message headers. Or Kafka consumer does not extract SpanContext from message headers. The trace chain breaks at the Kafka boundary.
**Diagnostic:**

```bash
# Check if Kafka messages have trace headers:
kafka-console-consumer.sh --bootstrap-server kafka:9092 \
  --topic order-events --from-beginning --max-messages 1 \
  --property print.headers=true
# Should see: traceparent:00-<traceId>-<spanId>-01
# If no traceparent header: producer not injecting context

# Check OpenTelemetry Kafka instrumentation:
# For Java: otel-java-agent includes Kafka auto-instrumentation
# Check agent version includes kafka-clients support:
java -javaagent:otel-javaagent.jar \
  -Dotel.javaagent.debug=true -version 2>&1 | \
  grep -i kafka
```

**Fix:**
BAD: `producer.send(new ProducerRecord<>(topic, key, value))` — no headers.
GOOD: Use OTel Kafka instrumentation (auto-instruments KafkaProducer/Consumer) OR manually inject:

```java
W3CTraceContextPropagator.getInstance().inject(
    Context.current(), headers, (h, k, v) ->
        h.add(k, v.getBytes(StandardCharsets.UTF_8)));
producer.send(new ProducerRecord<>(topic, null, key,
    value, headers));
```

**Prevention:** Integration test: verify Kafka messages contain `traceparent` header. Chaos test: consume message, verify span appears under producer's trace.

**Failure Mode 2: Trace Backend Unavailable — Request Latency Impact**

**Symptom:** OpenTelemetry Collector is down for maintenance. Services start timing out during high traffic. Investigation: span export calls are synchronous and blocking — when Collector is unreachable, each span export blocks for the TCP connection timeout (30 seconds default). 30 seconds × concurrent requests = thread exhaustion.
**Root Cause:** OTel SDK configured with synchronous exporter and no timeout/retry limits. Connection failure blocks the calling thread.
**Diagnostic:**

```bash
# Check OTel exporter timeout config:
env | grep OTEL_EXPORTER_OTLP_TIMEOUT
# Default: 10 seconds (but should be 1-2s max)

# Check thread pool saturation during collector outage:
curl http://service/actuator/metrics/executor.active | jq
# If active ≈ max AND latency high: thread exhaustion
# From span export blocking

# Test: kill collector, measure request latency:
kubectl delete pod -l app=otel-collector
# Observe: does service latency increase?
```

**Fix:**
BAD: `OtlpGrpcSpanExporter.getDefault()` (default 10s timeout, synchronous retries).
GOOD: Use BatchSpanProcessor (async, fire-and-forget): spans queued in memory, shipped in batches. Set `OTEL_EXPORTER_OTLP_TIMEOUT=2000` (2 seconds). Configure BatchSpanProcessor with `maxQueueSize` and `exportTimeout`: if queue full or timeout exceeded → spans dropped (tracing fails gracefully, requests unaffected).
**Prevention:** Tracing infrastructure must be non-critical to request path. Export must be async + bounded. Alert on span drop rate > 5% (indicates Collector is overwhelmed), but do NOT alert on Collector outage causing request failures (that's a configuration bug).

**Failure Mode 3: Security - Trace Data Contains Sensitive Information**

**Symptom:** Security audit reveals: Jaeger UI shows traces containing HTTP request bodies (including credit card numbers, passwords), SQL queries with user data (PII), and authentication tokens in span attributes. Any engineer with Jaeger access can read sensitive data from production traces.
**Root Cause:** OTel auto-instrumentation captures HTTP body and SQL query text by default. These attributes are added to spans and shipped to Jaeger. Jaeger has no data masking. Engineers with Jaeger access (often broad) can read production user data.
**Diagnostic:**

```bash
# Check what span attributes are captured:
# OTel HTTP semantic conventions capture:
# - http.request.body (if enabled)
# - db.statement (SQL query text)
# - http.request.header.authorization

# Search Jaeger for sensitive data:
# Jaeger API: GET /api/traces?service=payment-service&limit=10
# Check: do spans contain db.statement with SSN/PAN?
curl http://jaeger:16686/api/traces?service=payment-service | \
  jq '.data[].spans[].tags[] | select(.key=="db.statement")'
```

**Fix:**
BAD: Default OTel config captures `db.statement` (full SQL with values), HTTP request body.
GOOD: Disable sensitive attribute capture: `OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST=false`. Disable `db.statement` for production: `OTEL_INSTRUMENTATION_JDBC_STATEMENT_SANITIZER_ENABLED=true` (sanitize query by removing literal values). Never log span attributes containing user data. Apply Jaeger RBAC: limit access to production traces to SRE/security team.
**Prevention:** OTel security policy: all span attributes must be reviewed against PII/sensitive data policy. Auto-instrumentation defaults must be reviewed for security implications. Consider separate Jaeger instances for production (restricted access) vs staging (developer access).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-031 - Correlation ID (simpler precursor to distributed tracing — single ID without timing tree)

**Builds On This (learn these next):**

- DST-059 - Service Mesh (Istio/Linkerd implement distributed tracing at the infrastructure layer)

**Alternatives / Comparisons:**

- DST-031 - Correlation ID (lighter-weight alternative — no span timing, just request correlation)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Trace = all spans for one req  |
|                  | Span = one operation, one svc  |
|                  | traceId propagated everywhere  |
+------------------+--------------------------------+
| PROBLEM SOLVED   | "Which microservice caused     |
|                  | this slow request?" — invisible|
|                  | without tracing                |
+------------------+--------------------------------+
| KEY INSIGHT      | Propagate traceId + spanId in  |
|                  | EVERY transport: HTTP, Kafka,  |
|                  | gRPC, async threads            |
+------------------+--------------------------------+
| USE WHEN         | Microservices, distributed     |
|                  | systems, performance debugging,|
|                  | SLO analysis                   |
+------------------+--------------------------------+
| AVOID WHEN       | Monolith with APM (profiling   |
|                  | is more effective than tracing |
|                  | for single-process systems)    |
+------------------+--------------------------------+
| TRADE-OFF        | Observability vs overhead;     |
|                  | sampling rate determines both  |
+------------------+--------------------------------+
| ONE-LINER        | Tracking number for requests   |
|                  | across services with timing    |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-031 Correlation ID,        |
|                  | OpenTelemetry docs             |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. traceId must be propagated through EVERY transport boundary: HTTP headers, Kafka message headers, gRPC metadata, thread context. Every unhandled async boundary breaks the trace chain. Auto-instrumentation handles common libraries; manual propagation required for custom async code.
2. Span export must be asynchronous and non-blocking. If the trace collector is down: requests must be unaffected. Use BatchSpanProcessor with bounded queue. Tracing infrastructure failure = span data loss, NOT request failure.
3. Never put sensitive data (passwords, PAN, SSN, tokens) in span attributes. Span data is shipped to trace backends that may have broad access. Enable SQL sanitization (`db.statement` sanitizer) and disable HTTP body capture in production.

**Interview one-liner:**
"Distributed tracing instruments each service to record a 'span' (start time, end time, service name, operation) with a shared 'traceId' propagated through HTTP headers (`traceparent`). All spans for a request are collected by a backend (Jaeger, Zipkin, Tempo) and reconstructed into a trace tree — showing the complete request path with timing for each segment. Implemented with OpenTelemetry (CNCF standard): Java agent for zero-code-change instrumentation. Key operational rules: async export only, sampling (1% default + 100% errors via tail sampling), no PII in span attributes."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Observability requires active instrumentation — it doesn't emerge from code that "just works." The principle: design systems to be observable FROM THE START, not after production incidents reveal blind spots. Observability primitives (traces, metrics, logs) are not debugging tools — they are first-class features that make systems understandable. This principle applies to all complex systems: audit logs in financial software (observability for compliance), flight data recorders in aircraft (observability for incident analysis), clinical trial data systems (observability for regulatory review). The cost of observability is always lower than the cost of the blind spots it prevents.

**Where else this pattern appears:**

- **Database query plan tracing (`EXPLAIN ANALYZE`):** A SQL `EXPLAIN ANALYZE` shows the execution tree for one query: each node (Seq Scan, Hash Join, Index Scan) shows rows processed, time spent, and cost estimate. This is distributed tracing for the database query engine — one "request" (query), decomposed into its execution steps, with timing. The same mental model: trace the operation tree, find the slow node, fix it.
- **Browser performance tracing (Chrome DevTools Timeline):** Chrome's Performance tab shows a flame graph of every function call, network request, rendering paint, and JavaScript execution during a page load. This is distributed tracing for the browser — the "request" is a page load, the "services" are JavaScript, the network, and the rendering engine. Each operation is a span with start/end time. The flame graph is the trace tree visualization.
- **Git commit history as execution trace:** A git log with branches and merges is structurally identical to a distributed trace: each commit is a "span" (author, timestamp, message), branches are parallel execution (choreography), merges are joins. `git log --graph` visualizes this as a trace tree. The traceId is the repository — all commits are linked to one codebase history. The analogy shows that DAG-based execution recording is a universal pattern for complex systems.

---

### 💡 The Surprising Truth

Google's Dapper paper revealed a counterintuitive finding: the engineers who benefited most from distributed tracing were not the ones who built the systems being traced — they were the engineers who joined the team years later and needed to understand a system they hadn't designed. Tracing provided "institutional memory" encoded in the system's runtime behavior, not in documentation (which is often outdated) or in the original engineers' heads (who may have left). The surprising truth: distributed tracing's greatest value is not debugging production incidents (though it does that well) — it is onboarding new engineers and enabling safe changes to systems no single person fully understands. At Google's scale: no engineer understands the complete call graph of a system. Tracing makes the system legible to anyone who can query a traceId. This shifts distributed tracing from a debugging tool to a knowledge management tool for complex systems.

---

### 🧠 Think About This Before We Continue

**Q1 (A - System Interaction):** Service A calls Service B synchronously (HTTP). Service A also publishes a Kafka message consumed by Service C. All three are instrumented with OpenTelemetry. A user reports their order is slow. You have a traceId. In Jaeger, you see: Span A → Span B (linked, correct). But you cannot find Span C from the same trace. The Kafka message was published in the same A execution. What went wrong, and what is the complete fix?
_Hint:_ Kafka producer did not inject `traceparent` into the message headers at the time of publish. Or Kafka consumer (Service C) is not extracting SpanContext from headers. Or Service C is creating a new trace root instead of using the extracted parent. Check: (1) Does Service A's Kafka producer inject headers? OTel auto-instrumentation for `kafka-clients` ≥ 2.6 auto-injects if the agent is present. (2) Does Service C's Kafka consumer extract headers and create a child span? Same auto-instrumentation. (3) If manual: verify `W3CTraceContextPropagator.inject()` at producer and `.extract()` at consumer. Also: Kafka consumer creates spans with `kind=CONSUMER` and parent set to the producer's span. This appears as a linked span (not child) in Jaeger — check for "links" not only "children" in the trace view. This is the W3C standard for messaging: producer→consumer is a "link," not a parent-child relationship (because the consumer may run long after the producer).

**Q2 (B - Scale):** An e-commerce system runs 500,000 requests/second. Each request generates an average of 8 spans. Span size: ~2KB. System uses head-based 1% sampling. Calculate: (a) sampled spans per second, (b) bytes per second sent to collector, (c) bytes per day stored in Jaeger. Is 1% sampling sufficient? When would you need tail-based sampling?
_Hint:_ (a) 500,000 req/s × 1% = 5,000 req/s × 8 spans = 40,000 spans/s. (b) 40,000 × 2KB = 80 MB/s to Collector. Over 1 day: 80 MB/s × 86,400 = ~6.9 TB/day (before compression). With 5× compression: ~1.4 TB/day. Manageable for large systems, expensive for startups. Is 1% sufficient? For P99 analysis (performance): yes. 1% of 500K req/s = 5,000/s — statistically sufficient to see tail latency patterns. For rare errors (0.01% error rate = 50 req/s): 1% sampling captures 0.5 error traces/second — barely sufficient. For very rare events (0.001% = 5 req/s): 1% sampling captures 0.05/second → likely miss many. When tail-based is needed: when error rate is low enough that head-based sampling misses most errors. Tail-based: keep 100% of errors (50 error traces/second), sample 0.1% of successes (500 req/s) → 550 traces/second total, captures ALL errors.

**Q3 (C - Design Trade-off):** A team is choosing between distributed tracing (OpenTelemetry + Jaeger) and structured logging with correlation IDs (ELK stack with `traceId` field in every log line). Both can answer "what happened for request X?" Which questions can tracing answer that structured logging cannot, and vice versa? Under what circumstances is structured logging sufficient?
_Hint:_ Tracing unique value: (1) Span duration — tracing shows TIMING for each operation. "DB query took 1.4s" is a trace fact. Logs don't have per-operation timing unless you manually log start/end time. (2) Automatic parent-child relationship — tracing reconstructs the call tree. Logging requires log volume and timestamps to infer sequence. (3) Fan-out visibility — Service A calls B, C, D in parallel. Tracing shows all three as children of A's span with overlapping times. Logging: three separate log streams, manual correlation. Logging unique value: (1) Log content (error messages, SQL text, business events) — traces carry minimal metadata (attributes, events), not full log lines. (2) 100% coverage — logs capture every event; traces are sampled. (3) Lower cost — logging is cheaper than tracing infrastructure (Collector, Jaeger, storage). Structured logging is sufficient: single-service or 2-3 service systems where manual correlation is feasible; when inter-service timing is not a diagnostic requirement; when budget for tracing infrastructure is unavailable. Switch to distributed tracing when: debugging requires identifying WHICH service in a multi-service chain is slow, and manual log correlation is too slow or error-prone.

