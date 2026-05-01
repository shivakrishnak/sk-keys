---
layout: default
title: "Distributed Tracing"
parent: "Distributed Systems"
nav_order: 611
permalink: /distributed-systems/distributed-tracing/
number: "611"
category: Distributed Systems
difficulty: ★★★
depends_on: "Service Mesh, Correlation ID"
used_by: "Jaeger, Zipkin, OpenTelemetry, Datadog APM, AWS X-Ray"
tags: #advanced, #distributed, #observability, #microservices, #debugging
---

# 611 — Distributed Tracing

`#advanced` `#distributed` `#observability` `#microservices` `#debugging`

⚡ TL;DR — Distributed tracing assigns a unique **trace ID** to each request, propagating it across all services, so you can reconstruct the full call chain and see exactly where latency or failures occur in a multi-service system.

| #611 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Service Mesh, Correlation ID | |
| **Used by:** | Jaeger, Zipkin, OpenTelemetry, Datadog APM, AWS X-Ray | |

---

### 📘 Textbook Definition

**Distributed tracing** is an observability technique for tracking requests as they propagate through distributed systems. A single user request may traverse 10+ microservices; distributed tracing reconstructs the full execution path. Core concepts: **Trace** — the complete journey of a request (a tree of spans). **Span** — a named, timed unit of work within a service (e.g., "HTTP handler," "DB query"). Each span has: spanId, traceId (same across all spans in a trace), parentSpanId, start time, duration, status, and tags/logs. **Context propagation** — the traceId + spanId passed in HTTP headers (B3, W3C TraceContext standard) so downstream services can create child spans. **Sampling** — recording only a fraction of traces (e.g., 1%) to reduce overhead; or head-based (decision at entry) vs. tail-based (decision after trace complete). Standards: **OpenTelemetry** (CNCF) — vendor-neutral SDK for traces, metrics, and logs. Backends: Jaeger (open source), Zipkin, Datadog, Honeycomb, Tempo.

---

### 🟢 Simple Definition (Easy)

Imagine a package delivery tracked with a tracking number. You scan it at each checkpoint: origin → sorting → truck → destination. Distributed tracing: your HTTP request gets a tracking number (traceId). Every service it touches records a "checkpoint" (span) with timing. End result: timeline showing "API gateway: 5ms, Auth service: 12ms, DB query: 200ms (SLOW!), Response: 5ms." You see exactly where the 200ms went.

---

### 🔵 Simple Definition (Elaborated)

Without tracing: "The order service is slow." Which service is slow? Log search across 10 services for a specific request. With tracing: one query in Jaeger UI for traceId → full timeline, all services, all timings, exact error location. Production value: p99 latency regression → trace a slow request → "DB query in InventoryService: 850ms — missing index." Trace-driven debugging cuts mean-time-to-resolution (MTTR) from hours to minutes for latency issues.

---

### 🔩 First Principles Explanation

**Trace structure, context propagation, and sampling strategies:**

```
TRACE ANATOMY:

  User request: GET /api/orders/123
  traceId: "abc-123-xyz" (generated at entry point, e.g., API gateway)
  
  SPAN TREE:
  
  [API Gateway]          traceId=abc-123-xyz, spanId=A, parentSpanId=null
    start: 10:00:00.000  duration: 230ms
    |
    ├── [OrderService]   traceId=abc-123-xyz, spanId=B, parentSpanId=A
    │     start: 10:00:00.010  duration: 210ms
    │     |
    │     ├── [DB Query] traceId=abc-123-xyz, spanId=C, parentSpanId=B
    │     │     start: 10:00:00.015  duration: 5ms
    │     │     tags: {db.statement: "SELECT * FROM orders WHERE id=123", db.type: "postgresql"}
    │     |
    │     └── [InventoryService] traceId=abc-123-xyz, spanId=D, parentSpanId=B
    │           start: 10:00:00.025  duration: 200ms  ← SLOW!
    │           |
    │           └── [DB Query]  spanId=E, parentSpanId=D
    │                 duration: 195ms  ← ROOT CAUSE: slow DB query
    │                 tags: {db.statement: "SELECT * FROM inventory WHERE order_id=123"}
    │                 events: [{name: "slow query", timestamp: ...}]
    |
    └── [AuthService]  spanId=F, parentSpanId=A
          duration: 8ms

  WATERFALL VIEW (Jaeger/Zipkin timeline):
  
  API Gateway    |████████████████████████████████████| 230ms
  OrderService       |████████████████████████████| 210ms
  DB Query (orders)      |█| 5ms
  InventoryService           |████████████████| 200ms
  DB Query (inventory)         |██████████████| 195ms  ← spike!
  AuthService            |█| 8ms
  
  Immediate insight: InventoryService DB query = bottleneck. 195ms for inventory lookup.
  Next action: EXPLAIN ANALYZE on that query. Missing index on order_id column.

CONTEXT PROPAGATION (W3C TraceContext standard):

  HTTP request headers:
    traceparent: 00-abc123xyz-spanIdB-01
    tracestate: vendor-specific-data
    
  Format: version-traceId-spanId-flags
  
  Service receives request:
    1. Parse traceparent header → extract traceId, parentSpanId.
    2. Create new span: spanId=newId, parentSpanId=extractedSpanId, traceId=same.
    3. Do work (record timing, errors).
    4. On outgoing requests: inject traceparent with traceId + newSpanId.
    5. Downstream services: repeat steps 1-4.
    
  If no traceparent header: service is the root → generate new traceId.
  
  PROPAGATION ACROSS PROTOCOLS:
    HTTP: headers (traceparent)
    gRPC: metadata (grpc-trace-bin or traceparent)
    Kafka: message headers (W3C traceparent in Kafka header)
    
  KAFKA TRACING CHALLENGE:
    Producer: inject traceId in Kafka message headers.
    Consumer: extract traceId from headers, create child span.
    BUT: there may be significant time between produce and consume (hours).
    Solution: create a separate "consumer span" with the producer's span as parent,
    even if the time gap is large. Shows async causality, not chronological co-occurrence.

SAMPLING STRATEGIES:

  Full trace recording: too expensive at scale. 10K RPS × 50 spans = 500K spans/sec.
  
  1. HEAD-BASED SAMPLING (decision at entry point):
     API gateway: roll dice (1% = record, 99% = discard).
     Decision propagated in headers (flags bit = 1 = sampled).
     Downstream services: record span only if sampled=1.
     
     PROS: Low overhead (most traces never recorded at all).
     CONS: "Interesting" traces (errors, slow) randomly discarded.
     
  2. TAIL-BASED SAMPLING (decision after trace complete):
     All services: record spans in memory (or edge buffer).
     Trace collector: receives ALL spans for a trace.
     Collector: makes sampling decision AFTER seeing full trace.
     Decision criteria: "was there an error? Was duration > 500ms? → keep."
     
     PROS: Always keep interesting traces (errors, slow).
     CONS: Higher memory overhead (buffering complete traces before decision).
     Complexity: all spans for a trace must route to same collector.
     
  3. ADAPTIVE/DYNAMIC SAMPLING:
     New endpoints, new error types: 100% sampled.
     High-volume, healthy paths: 0.1% sampled.
     Adjust sampling rate per route/service automatically.
     OpenTelemetry Collector: supports rule-based sampling.

OPENTELEMETRY (OTEL) ARCHITECTURE:

  SDK (in each service) → OTEL Collector → Backend (Jaeger/Datadog/etc.)
  
  SDK components:
    Tracer: creates traces and spans.
    Context: stores current span for automatic parent detection.
    Exporter: sends spans to collector (OTLP protocol).
    
  OTEL Collector:
    Receives from multiple services (OTLP receiver).
    Processes (batching, filtering, attribute enrichment).
    Exports to multiple backends simultaneously (Jaeger + Datadog + Prometheus).
    
  Value: instrument once (OTEL SDK) → switch backends without code changes.
  
  AUTO-INSTRUMENTATION:
    Java agent: -javaagent:opentelemetry-javaagent.jar
    Automatically instruments: HTTP clients, JDBC, gRPC, Kafka, Spring, etc.
    Zero code changes. Just attach agent.
    
    // Manual span creation (when auto-instrumentation isn't sufficient):
    Tracer tracer = GlobalOpenTelemetry.getTracer("my-service");
    Span span = tracer.spanBuilder("process-order")
        .setAttribute("order.id", orderId)
        .setAttribute("order.amount", amount)
        .startSpan();
    try (Scope scope = span.makeCurrent()) {
        // work here; child spans automatically parented to this span
        processOrderInternal(orderId);
    } catch (Exception e) {
        span.recordException(e);
        span.setStatus(StatusCode.ERROR, e.getMessage());
        throw e;
    } finally {
        span.end();
    }

TRACE CORRELATION WITH LOGS AND METRICS:

  LOGS + TRACES:
    Add traceId + spanId to every log line:
    logger.info("Processing order {}", orderId, 
        Map.of("traceId", span.getSpanContext().getTraceId(),
               "spanId", span.getSpanContext().getSpanId()));
    
    Log output: {"message": "Processing order 123", "traceId": "abc-123", "spanId": "span-B"}
    
    In Grafana/Datadog: click on a trace span → jump to logs filtered by traceId.
    Click on a log line → jump to the trace. Full correlation.
    
  METRICS + TRACES:
    Exemplars: attach a traceId to a metric data point.
    "p99 latency spiked at 10:05AM" → click metric point → 
    "exemplar traceId = abc-999" → open that trace → see why it was slow.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT distributed tracing:
- "The checkout is slow" → logs across 10 services → hours of correlation by timestamp
- No way to link a user's experience to specific service calls
- Latency root-cause analysis requires expert knowledge of the whole system

WITH distributed tracing:
→ One traceId query → complete request timeline across all services
→ Exact latency breakdown per service and per operation
→ MTTR for latency issues: hours → minutes

---

### 🧠 Mental Model / Analogy

> Airport luggage tracking: your bag (request) gets a barcode (traceId) at check-in. Every conveyor belt checkpoint (service) scans it and records time + location (span). The airline app: shows the full journey — check-in → sorting → gate → plane → destination carousel. If the bag is delayed: "stuck at sorting (200ms)." Same model for requests.

"Barcode on bag" = traceId propagated in HTTP headers
"Checkpoint scan" = span created in each service
"Airline app timeline" = Jaeger/Zipkin waterfall view
"Bag stuck at sorting" = slow span identified in UI

---

### ⚙️ How It Works (Mechanism)

```
SPRING BOOT + OPENTELEMETRY AUTO-INSTRUMENTATION:

  # application.yml
  management:
    tracing:
      sampling.probability: 1.0  # 100% for dev; 0.01 for production
  spring:
    application:
      name: order-service  # appears as service name in traces

  # build.gradle — OTEL Java agent (zero code changes):
  # Run with: java -javaagent:opentelemetry-javaagent-1.x.jar -jar app.jar
  
  # Result: all HTTP, JDBC, Kafka calls automatically traced.
  # Spring's @Observed annotation for custom spans:
  
  @Service
  public class OrderService {
      @Observed(name = "order.process", contextualName = "process-order")
      public Order processOrder(String orderId) {
          // This method = automatic span "process-order"
          return orderRepo.findById(orderId)...;
      }
  }
```

---

### 🔄 How It Connects (Mini-Map)

```
Correlation ID (simple request tracking — single ID in logs)
        │
        ▼ (distributed tracing extends this to full span trees)
Distributed Tracing ◄──── (you are here)
(trace + spans + context propagation = full request visibility)
        │
        ├── Service Mesh (Istio/Linkerd auto-inject trace headers at proxy level)
        ├── OpenTelemetry: vendor-neutral instrumentation standard
        └── Observability: traces + metrics + logs = full O11y stack
```

---

### 💻 Code Example

```java
// Manual OpenTelemetry tracing in Java:
@RestController
public class OrderController {
    
    private static final Tracer tracer = 
        GlobalOpenTelemetry.getTracer("order-service", "1.0.0");
    
    @PostMapping("/orders")
    public ResponseEntity<Order> createOrder(@RequestBody OrderRequest request) {
        // Auto-instrumented: HTTP span created automatically by OTEL agent.
        // Manual child span for business logic:
        Span span = tracer.spanBuilder("validate-and-create-order")
            .setAttribute("order.customer_id", request.getCustomerId())
            .setAttribute("order.item_count", request.getItems().size())
            .startSpan();
        
        try (Scope scope = span.makeCurrent()) {
            // All DB calls, HTTP calls inside here: automatically parented to this span.
            Order order = orderService.create(request);
            span.setAttribute("order.id", order.getId());
            span.setStatus(StatusCode.OK);
            return ResponseEntity.ok(order);
        } catch (Exception e) {
            span.recordException(e);
            span.setStatus(StatusCode.ERROR, "Order creation failed: " + e.getMessage());
            throw e;
        } finally {
            span.end(); // Always end the span.
        }
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Distributed tracing replaces logging | Tracing and logging are complementary. Traces: show WHAT happened and WHERE time was spent (request flow, latency). Logs: show WHY (detailed error messages, state, business context). Best practice: inject traceId into log MDC so logs and traces are linked. Then: use traces to find the problem, use logs to understand it |
| 100% trace sampling in production is fine | At 1000 RPS with 30 spans/request: 30,000 spans/sec. Each span ~1KB: 30MB/sec → 2.5TB/day. Storage and processing cost is significant. Use adaptive sampling: 100% for errors, 1% for healthy high-volume paths. Tail-based sampling keeps all interesting traces while discarding noise |
| Distributed tracing requires code changes in every service | OpenTelemetry Java agent, Python auto-instrumentation, and Node.js auto-instrumentation can instrument services with zero code changes. Attach the agent at startup. Service meshes (Istio) inject trace headers at the proxy level. For maximum detail: add manual spans for business operations. But baseline tracing: zero code changes |
| A trace shows the complete picture of what happened | Traces show the HAPPY PATH call chain. They miss: async work done after response returned, background jobs triggered by the request, eventual consistency side effects. Combine traces with events/logs for full picture. A trace ending at the API response doesn't show if the downstream Kafka consumer processed the message correctly |

---

### 🔥 Pitfalls in Production

**Missing trace context across async boundaries:**

```
SCENARIO: HTTP request → OrderService creates order → publishes Kafka message.
  Consumer (FulfillmentService) processes message, but trace is broken.
  In Jaeger: two separate traces. Can't link customer request to fulfillment.
  
BAD: Kafka message without trace context:
  // Producer: doesn't propagate trace context.
  kafkaTemplate.send("fulfillment-events", new FulfillmentEvent(orderId));
  // FulfillmentService consumer: creates NEW trace. No link to original request.
  
FIX: Propagate trace context in Kafka message headers:
  // Producer: inject W3C trace context into Kafka headers.
  @Service
  public class OrderEventPublisher {
      
      @Autowired private KafkaTemplate<String, FulfillmentEvent> kafkaTemplate;
      
      public void publishFulfillmentEvent(String orderId) {
          ProducerRecord<String, FulfillmentEvent> record = 
              new ProducerRecord<>("fulfillment-events", orderId, new FulfillmentEvent(orderId));
          
          // Inject current span context into Kafka headers:
          OpenTelemetry otel = GlobalOpenTelemetry.get();
          otel.getPropagators().getTextMapPropagator().inject(
              Context.current(), record.headers(),
              (headers, key, value) -> headers.add(key, value.getBytes()));
          
          kafkaTemplate.send(record);
      }
  }
  
  // Consumer: extract trace context from Kafka headers.
  @KafkaListener(topics = "fulfillment-events")
  public void onFulfillmentEvent(
          ConsumerRecord<String, FulfillmentEvent> record) {
      
      // Extract propagated context from Kafka headers:
      Context extractedContext = GlobalOpenTelemetry.get()
          .getPropagators().getTextMapPropagator().extract(
              Context.current(), record.headers(),
              (headers, key) -> {
                  Header h = headers.lastHeader(key);
                  return h != null ? new String(h.value()) : null;
              });
      
      // Create child span linked to the original HTTP request trace:
      Span span = GlobalOpenTelemetry.getTracer("fulfillment-service")
          .spanBuilder("process-fulfillment")
          .setParent(extractedContext)  // Links to original trace!
          .startSpan();
      
      try (Scope scope = span.makeCurrent()) {
          fulfillmentService.process(record.value());
      } finally {
          span.end();
      }
  }
  // Result: Jaeger shows SINGLE trace: HTTP request → OrderService → Kafka → FulfillmentService.
  // Full async request lifecycle visible as one trace.
```

---

### 🔗 Related Keywords

- `Correlation ID` — simpler predecessor: single ID in logs without span hierarchy
- `Service Mesh` — Istio/Linkerd automatically inject trace headers without code changes
- `OpenTelemetry` — vendor-neutral standard for traces, metrics, logs
- `Observability` — traces + metrics + logs = the three pillars of O11y
- `Jaeger` — open-source distributed tracing backend (CNCF project)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ traceId propagated in headers across all  │
│              │ services; each creates a span with timing │
│              │ → reconstruct full request timeline       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Debugging latency/errors in microservices;│
│              │ any system with 3+ service call chains    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Monolith (use profiler instead); overhead │
│              │ unacceptable → use 1% sampling, not 0%   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Airport luggage tracking: one barcode,  │
│              │  every checkpoint logged, delay visible." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Correlation ID → OpenTelemetry →          │
│              │ Service Mesh → Jaeger → Tail-Based Sample │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A distributed trace shows: API Gateway (5ms) → OrderService (200ms). The OrderService span has no child spans — just 200ms of unexplained time. What does this mean? What are 3 possible root causes for "time that doesn't show up as child spans"? How would you instrument the service to find the root cause?

**Q2.** Your system processes 50,000 requests/second. You use head-based sampling at 0.1% — recording 50 traces/second. A customer reports "my checkout was slow at 10:05 AM." The 0.1% sampling means their specific slow request was almost certainly NOT recorded. How do you solve this? What sampling strategy would ensure slow requests are always captured? What are the operational costs of that strategy?
