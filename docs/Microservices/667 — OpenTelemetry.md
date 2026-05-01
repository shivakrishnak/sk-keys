---
layout: default
title: "OpenTelemetry"
parent: "Microservices"
nav_order: 667
permalink: /microservices/opentelemetry/
number: "667"
category: Microservices
difficulty: ★★★
depends_on: "Distributed Logging, Correlation ID"
used_by: "Observability & SRE, Cross-Cutting Concerns"
tags: #advanced, #microservices, #observability, #distributed, #architecture
---

# 667 — OpenTelemetry

`#advanced` `#microservices` `#observability` `#distributed` `#architecture`

⚡ TL;DR — **OpenTelemetry (OTel)** is the CNCF-standard observability framework that unifies distributed **traces**, **metrics**, and **logs** under one SDK and wire protocol (OTLP). Services instrument once; telemetry is exported to any backend (Jaeger, Zipkin, Prometheus, Grafana Tempo, Datadog). OTel replaces vendor-specific SDKs and eliminates observability vendor lock-in.

| #667            | Category: Microservices                     | Difficulty: ★★★ |
| :-------------- | :------------------------------------------ | :-------------- |
| **Depends on:** | Distributed Logging, Correlation ID         |                 |
| **Used by:**    | Observability & SRE, Cross-Cutting Concerns |                 |

---

### 📘 Textbook Definition

**OpenTelemetry (OTel)** is a CNCF (Cloud Native Computing Foundation) open-source observability framework and specification that provides vendor-neutral APIs, SDKs, and tooling for collecting distributed **traces** (request flow and timing across services), **metrics** (quantitative measurements of service health), and **logs** (structured event records) — the three pillars of observability. OpenTelemetry was formed by merging OpenCensus (Google) and OpenTracing (CNCF) in 2019. It defines: the **OpenTelemetry Protocol (OTLP)** — the wire format for exporting telemetry data; the **OpenTelemetry Collector** — a vendor-agnostic agent/aggregator that receives OTLP, processes it, and exports to backends (Jaeger, Prometheus, Grafana, Datadog, New Relic); language-specific **SDKs** (Java, Python, Go, Node.js, .NET) for instrumenting code; and **auto-instrumentation agents** that instrument code automatically with zero code changes (Java: `-javaagent:opentelemetry-javaagent.jar`). The key benefit: instrument once with OTel → switch backends without code changes. Context propagation uses the W3C Trace Context standard (`traceparent` header), replacing proprietary formats like Zipkin's `X-B3-TraceId`.

---

### 🟢 Simple Definition (Easy)

OpenTelemetry is a standard way for services to report what they're doing (traces), how they're performing (metrics), and what happened (logs) — to any monitoring tool. Like a universal power adapter: instead of one adapter for Datadog, one for Jaeger, one for Prometheus — OTel is the one adapter that works with all of them.

---

### 🔵 Simple Definition (Elaborated)

Without OTel: `OrderService` uses Zipkin SDK, `PaymentService` uses Jaeger SDK, `InventoryService` uses Datadog SDK. Three different trace formats, three different header propagation schemes, impossible to create a single trace across all services. With OTel: all services use OTel SDK, all use `traceparent` header, all send OTLP to the OTel Collector. The Collector fans out to: Jaeger (traces), Prometheus (metrics), Grafana Loki (logs). Switch from Jaeger to Tempo? Change Collector config — zero code changes in services.

---

### 🔩 First Principles Explanation

**OTel data model — traces, spans, and context:**

```
TRACE:
  Represents a complete request journey across all services.
  Has a unique Trace ID (128-bit, 32 hex chars).
  Contains one or more Spans.

SPAN:
  Represents a single unit of work within the trace.
  Has:
    SpanID (64-bit)
    ParentSpanID (the span that called this span, or root if null)
    Name (operation name: "HTTP GET /orders", "PostgreSQL SELECT")
    Start timestamp + end timestamp (duration = end - start)
    Status (OK / ERROR)
    Attributes (key-value metadata: http.method, db.statement, etc.)
    Events (timestamped annotations within the span: "retry attempt 2")
    Links (references to related spans in other traces)

EXAMPLE TRACE for "place order":

  Trace: 4bf92f3577b34da6a3ce929d0e0e4736 (root → leaf)

  [OrderService] HTTP POST /orders         SpanID: a3c    ParentID: null (root)
    Duration: 350ms
    Attributes: http.method=POST, http.route=/orders, http.status_code=201
    │
    ├── [OrderService] PostgreSQL INSERT    SpanID: b4d    ParentID: a3c
    │   Duration: 15ms
    │   Attributes: db.system=postgresql, db.statement="INSERT INTO orders..."
    │
    └── [PaymentService] HTTP POST /pay    SpanID: c5e    ParentID: a3c
        Duration: 280ms
        Attributes: http.method=POST, http.status_code=200
        │
        └── [PaymentService] Stripe API   SpanID: d6f    ParentID: c5e
            Duration: 240ms
            Attributes: http.url=https://api.stripe.com, net.peer.name=api.stripe.com

  Visual timeline:
  |--- OrderService POST /orders (350ms) ----------------------------------|
    |--PostgreSQL (15ms)--|  |--- PaymentService POST /pay (280ms) --------|
                                |--- Stripe API call (240ms) ------------|

  Immediate insight: Stripe API call is the bottleneck (240ms of 350ms total)
```

**W3C traceparent header — context propagation:**

```
FORMAT: version-traceId-parentSpanId-flags
EXAMPLE: traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-a3ce929d0e0e4736-01

BREAKDOWN:
  00 = version (W3C spec version)
  4bf92f3577b34da6a3ce929d0e0e4736 = Trace ID (128-bit = 32 hex chars)
  a3ce929d0e0e4736 = Parent Span ID (64-bit = 16 hex chars)
  01 = flags: 01=sampled (record this trace), 00=not sampled

PROPAGATION:
  Service A creates root span (no parent) → generates traceparent header
  Service A calls Service B → includes traceparent with A's SpanID as parent
  Service B creates child span → traceparent: same Trace ID + B's SpanID as parent
  Service B calls Service C → includes traceparent with B's SpanID as parent
  All spans: same Trace ID → single unified trace in Jaeger UI

KAFKA:
  ProducerRecord headers: same traceparent value
  Consumer: extracts traceparent → creates child span from extracted context
  → Async Kafka call appears as child span in the same trace
  → Even async boundaries are represented in the trace hierarchy
```

**OTel Collector — the processing pipeline:**

```
COLLECTOR PIPELINE:

  Services → OTLP (gRPC or HTTP) → OTel Collector
                                          │
                                   RECEIVERS (input):
                                   - OTLP (from services)
                                   - Prometheus scrape (pull metrics)
                                   - Jaeger/Zipkin (for migration)
                                          │
                                   PROCESSORS (transform):
                                   - Batch (reduce export calls)
                                   - Memory limiter (prevent OOM)
                                   - Attribute filter (remove PII)
                                   - Sampling (reduce trace volume)
                                          │
                                   EXPORTERS (output):
                                   - Jaeger (traces)
                                   - Prometheus remote_write (metrics)
                                   - Loki (logs)
                                   - Datadog (all three — if using SaaS)

SAMPLING STRATEGIES (critical for production cost):
  HEAD-BASED SAMPLING (at trace start):
    10% probability: only keep 10% of traces
    Fast: decision made immediately
    Risk: may discard the one trace showing an error

  TAIL-BASED SAMPLING (at trace end — smarter):
    Keep 100% of error traces (status=ERROR)
    Keep 100% of slow traces (duration > 2s)
    Keep 1% of successful fast traces (low value for debugging)
    Requires: collector buffers complete traces before sampling decision
    Cost: more collector memory (buffering complete traces)
    Value: never miss an important trace
```

**Java auto-instrumentation — zero-code OTel:**

```bash
# No code changes needed. Add JVM argument:
java -javaagent:opentelemetry-javaagent.jar \
     -Dotel.service.name=order-service \
     -Dotel.exporter.otlp.endpoint=http://otel-collector:4317 \
     -Dotel.exporter.otlp.protocol=grpc \
     -Dotel.traces.sampler=parentbased_traceidratio \
     -Dotel.traces.sampler.arg=0.1 \  # 10% sampling
     -jar order-service.jar

# What auto-instrumentation captures automatically:
# - All inbound HTTP requests (Spring MVC, Spring WebFlux)
# - All outbound HTTP calls (RestTemplate, WebClient, OkHttp)
# - JDBC database calls (query text, database name, duration)
# - Kafka producer/consumer operations
# - Redis operations (Lettuce, Jedis)
# - Spring @Scheduled methods
# - @Async method calls

# Manual span for custom business logic:
@Autowired Tracer tracer;

public Order processOrder(CreateOrderRequest request) {
    Span span = tracer.spanBuilder("order.process")
        .setAttribute("order.customerId", request.getCustomerId())
        .setAttribute("order.productId", request.getProductId())
        .startSpan();

    try (Scope scope = span.makeCurrent()) {
        Order order = orderRepository.save(new Order(request));
        span.setAttribute("order.id", order.getId());
        span.setStatus(StatusCode.OK);
        return order;
    } catch (Exception e) {
        span.setStatus(StatusCode.ERROR, e.getMessage());
        span.recordException(e);
        throw e;
    } finally {
        span.end();
    }
}
```

---

### ❓ Why Does This Exist (Why Before What)

Before OTel, every APM vendor (Datadog, New Relic, Dynatrace, Zipkin, Jaeger) had its own SDK. Switching vendors required updating code in every service. Worse: different teams used different APMs, making cross-service tracing impossible. OpenTelemetry unifies the data model and wire protocol, making observability vendor-neutral and interoperable. It is rapidly becoming the industry standard — AWS, Google, Microsoft, and most major APM vendors now support OTLP natively.

---

### 🧠 Mental Model / Analogy

> OpenTelemetry is like the USB-C standard for observability. Before USB-C: every device had its own proprietary charging cable (Zipkin SDK, Datadog agent, Dynatrace oneagent). Changing phones meant changing all your cables. USB-C: one cable, every device, every charger. OTel is the USB-C of telemetry: one SDK (OTel), every service, every backend (Jaeger, Grafana, Datadog). The OTel Collector is the USB-C hub that takes one signal and distributes it to multiple outputs.

---

### ⚙️ How It Works (Mechanism)

**Spring Boot application.properties for OTel (with Micrometer bridge):**

```yaml
# application.yml — OTel configuration for Spring Boot 3:
management:
  tracing:
    sampling:
      probability: 0.1 # 10% sampling rate (100% in dev)
  otlp:
    tracing:
      endpoint: http://otel-collector:4318/v1/traces
    metrics:
      export:
        url: http://otel-collector:4318/v1/metrics

spring:
  application:
    name: order-service # appears as service.name in OTel


# Spring Boot 3.x: auto-configures OTel with Spring Actuator + Micrometer
# No javaagent needed if using Spring Boot 3 with micrometer-tracing-bridge-otel
```

---

### 🔄 How It Connects (Mini-Map)

```
Correlation ID
(simple request linking — OTel extends this)
        │
        ▼
OpenTelemetry  ◄──── (you are here)
(traces + metrics + logs, vendor-neutral)
        │
        ├── Distributed Logging → logs enriched with OTel trace/span IDs
        ├── Observability & SRE → OTel provides the data for SRE metrics (SLOs)
        └── Cross-Cutting Concerns → OTel instrumentation is a cross-cutting concern
```

---

### 💻 Code Example

**OTel Collector configuration (otel-collector-config.yaml):**

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 5s
    send_batch_size: 1000
  memory_limiter:
    limit_mib: 512
  attributes/remove_pii:
    actions:
      - key: http.request.header.authorization
        action: delete
      - key: enduser.email
        action: delete

exporters:
  jaeger:
    endpoint: jaeger:14250
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
      processors: [memory_limiter, batch]
      exporters: [jaeger]
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [prometheus]
    logs:
      receivers: [otlp]
      processors: [memory_limiter, attributes/remove_pii, batch]
      exporters: [loki]
```

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                                                                                           |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| OpenTelemetry replaces Prometheus and Jaeger      | OTel is the collection and transmission standard. Prometheus (storage/querying for metrics) and Jaeger (storage/UI for traces) are still the backends. OTel gets telemetry TO these backends — it doesn't replace them            |
| Auto-instrumentation captures everything you need | Auto-instrumentation captures framework-level operations (HTTP, DB, Kafka). Business context (orderId, customerId, business rule applied) must be added with manual span attributes. Both are needed for effective debugging      |
| OTel sampling means losing data                   | Sampling means storing fewer traces — not losing them. Error traces and slow traces are typically sampled at 100%. Only successful, fast traces (the "happy path" with no debugging value) are sampled down to 1-10%              |
| OTel adds significant overhead to services        | OTel Java agent: ~2-5% CPU overhead, ~50MB additional heap. At 10% sampling, exporter overhead is minimal. For production services with millisecond SLAs, OTel overhead is negligible compared to the debugging value it provides |

---

### 🔥 Pitfalls in Production

**Trace context not propagated across async boundaries:**

```
SCENARIO:
  OrderService uses @Async method for notification:
  @Async void sendConfirmationEmail(String orderId) {
      // Runs on different thread — OTel context not propagated!
      // New root span created (not linked to original order request trace)
  }

  Result in Jaeger: order trace ends at OrderService.placeOrder span.
  Email sending: separate unlinked root trace.
  Cannot see email sending as part of the order flow.

FIX (Spring Boot + OTel Java agent):
  The OTel Java agent automatically instruments Spring @Async
  IF using Micrometer Observation + Context Propagation:

  @Bean
  TaskDecorator contextPropagatingDecorator() {
      return runnable -> {
          Context otelContext = Context.current();  // capture OTel context on calling thread
          return () -> {
              try (Scope scope = otelContext.makeCurrent()) {  // restore on async thread
                  runnable.run();
              }
          };
      };
  }

  @Bean
  ThreadPoolTaskExecutor asyncExecutor(TaskDecorator decorator) {
      ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
      executor.setTaskDecorator(decorator);
      executor.initialize();
      return executor;
  }
  // Now: @Async methods inherit the OTel context from the calling thread
  // Email sending span appears as child span of order placement trace
```

---

### 🔗 Related Keywords

- `Correlation ID` — the simple form of trace ID; OTel's trace ID extends it with spans
- `Distributed Logging` — OTel logs enrich log entries with trace/span IDs for correlation
- `Observability & SRE` — OTel provides the three pillars of observability data

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ THREE PILLARS│ Traces + Metrics + Logs (unified)         │
│ PROTOCOL     │ OTLP (gRPC or HTTP) — vendor-neutral      │
│ HEADER       │ W3C traceparent (replaces X-B3-TraceId)   │
├──────────────┼───────────────────────────────────────────┤
│ COMPONENTS   │ SDK → OTel Collector → Backends           │
│ JAVA         │ Auto-instrument: -javaagent:otel-agent.jar│
│              │ Or Spring Boot 3 + micrometer-otel bridge  │
├──────────────┼───────────────────────────────────────────┤
│ SAMPLING     │ Tail-based: 100% errors, 1% happy path    │
│ BACKENDS     │ Jaeger/Tempo (traces), Prometheus (metrics)│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have 20 microservices generating 100,000 traces per minute in production. Each trace contains an average of 8 spans. You're exporting 100% of traces to Jaeger. Storage cost is $5,000/month and growing. Design a tail-based sampling strategy using the OTel Collector: what sampling rules would you configure? How do you ensure you never miss: (a) error traces, (b) latency outliers (p99 > 2 seconds), (c) new error patterns from a recently deployed service? What percentage reduction in storage cost do you expect from your sampling strategy?

**Q2.** Your team uses OpenTelemetry for tracing but wants to correlate traces with specific user sessions for customer support. The trace ID changes per request (as expected). How do you implement "session-scoped trace aggregation" — the ability to see all traces generated by a specific user session (e.g., all API calls during a 30-minute user login session)? What attribute would you add to spans? How would you query across traces for a specific user session in Jaeger or Tempo?
