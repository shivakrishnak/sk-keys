---
layout: default
title: "Correlation ID"
parent: "Microservices"
nav_order: 666
permalink: /microservices/correlation-id/
number: "666"
category: Microservices
difficulty: ★★☆
depends_on: "Distributed Logging, Cross-Cutting Concerns"
used_by: "OpenTelemetry, Distributed Logging"
tags: #intermediate, #microservices, #observability, #distributed, #architecture
---

# 666 — Correlation ID

`#intermediate` `#microservices` `#observability` `#distributed` `#architecture`

⚡ TL;DR — A **Correlation ID** is a unique identifier (UUID) attached to an incoming request and propagated through every service call in the chain. Every log entry for that request, across all services, carries this ID. Searching the ID in a centralized log system returns the complete request journey — essential for debugging distributed systems.

| #666            | Category: Microservices                     | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------ | :-------------- |
| **Depends on:** | Distributed Logging, Cross-Cutting Concerns |                 |
| **Used by:**    | OpenTelemetry, Distributed Logging          |                 |

---

### 📘 Textbook Definition

A **Correlation ID** (also called **Request ID** or **Trace ID** in simpler systems) is a unique identifier — typically a UUID v4 — generated at the entry point of a request (API gateway, edge service, or the first service that handles a client request) and propagated through the entire call chain via HTTP headers, message headers (Kafka), and gRPC metadata. Every service in the chain: (a) reads the correlation ID from the incoming request header; (b) adds it to all log entries via MDC (Mapped Diagnostic Context) or equivalent; (c) forwards it in headers to all downstream service calls. In a centralized log aggregation system, querying by correlation ID returns every log entry from every service that participated in processing the original request — in timestamp order. The Correlation ID is the minimal form of distributed tracing. More advanced distributed tracing (OpenTelemetry) extends this with span hierarchy, timing data per span, and parent-child relationships — but the correlation ID remains the foundation.

---

### 🟢 Simple Definition (Easy)

When a user's request enters your system, you stamp it with a unique ID (like a UPS tracking number). Every service that handles this request writes that ID in its log messages. When something goes wrong, you search all logs for that ID — and see everything that happened to that request, across all services, in order.

---

### 🔵 Simple Definition (Elaborated)

User places an order. API gateway generates `X-Correlation-ID: abc-123` and forwards it. `OrderService` logs: `{msg: "Order received", correlationId: "abc-123"}`. Calls `PaymentService` with header `X-Correlation-ID: abc-123`. `PaymentService` logs: `{msg: "Processing payment", correlationId: "abc-123"}`. Calls `InventoryService` with same header. `InventoryService` logs: `{msg: "Reserving inventory", correlationId: "abc-123"}`. Payment fails silently. Search `abc-123` in Kibana: see all 3 services' logs in timestamp order — payment failure log entry immediately visible.

---

### 🔩 First Principles Explanation

**Correlation ID vs Distributed Trace ID — what's the difference:**

```
CORRELATION ID (simple):
  - Single UUID per request
  - Groups ALL log entries for one request from ONE user
  - No hierarchy, no timing data
  - Answers: "What happened during request X?"

OPENTELEMETRY TRACE ID + SPAN IDs (distributed tracing):
  - Trace ID: similar to Correlation ID (identifies the whole request)
  - Span ID: identifies individual units of work within the request
  - Parent/child span relationships: represents call hierarchy
  - Timing: each span has start time + duration
  - Answers: "What happened, HOW LONG did each step take, WHICH call was slow?"

RELATIONSHIP:
  Correlation ID ⊆ Distributed Tracing
  (Correlation ID is the trace ID in OpenTelemetry terminology)
  When using OpenTelemetry:
    MDC traceId = OpenTelemetry Trace ID (same as correlation ID function)
    MDC spanId = current span (finer granularity)
    No need for separate correlationId if using OTel — trace ID serves the same purpose

WHEN TO USE WHAT:
  Minimal observability setup (small team, few services):
    → Correlation ID only (simple, cheap to implement)

  Production microservices at scale:
    → OpenTelemetry (trace ID + spans) — correlation ID benefits + timing + hierarchy
```

**Implementation: where to generate and how to propagate:**

```
GENERATION RULES:
  1. API Gateway always generates new correlation ID for inbound requests
     (client-provided IDs rejected or ignored — security: prevent log injection)
  2. If no X-Correlation-ID in incoming request: generate new UUID
  3. If X-Correlation-ID present in incoming request from trusted upstream: use it
  4. Return X-Correlation-ID in response (client can use for support tickets)

PROPAGATION CHAIN:

  HTTP (REST calls between services):
    Outbound: add header X-Correlation-ID: {correlationId from MDC}
    Inbound: extract header X-Correlation-ID → put in MDC

  Kafka (async events):
    Producer: add to message headers:
      producer.headers().add("X-Correlation-ID", correlationId.getBytes());
    Consumer: extract from message headers:
      String correlationId = new String(record.headers()
          .lastHeader("X-Correlation-ID").value());
      MDC.put("correlationId", correlationId);

  gRPC:
    Use metadata (equivalent of HTTP headers):
    Metadata.Key<String> CORRELATION_ID_KEY =
        Metadata.Key.of("x-correlation-id", Metadata.ASCII_STRING_MARSHALLER);
    ClientInterceptor: attaches correlationId to outbound metadata
    ServerInterceptor: extracts correlationId from incoming metadata
```

**Spring Boot implementation — complete end-to-end:**

```java
// 1. Filter: extract/generate correlation ID, place in MDC:
@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public class CorrelationIdFilter extends OncePerRequestFilter {
    private static final String CORRELATION_ID_HEADER = "X-Correlation-ID";
    private static final String MDC_KEY = "correlationId";

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {
        String correlationId = Optional
            .ofNullable(request.getHeader(CORRELATION_ID_HEADER))
            .filter(id -> id.matches("[0-9a-f-]{36}"))  // validate UUID format
            .orElse(UUID.randomUUID().toString());       // generate if missing/invalid

        MDC.put(MDC_KEY, correlationId);
        response.setHeader(CORRELATION_ID_HEADER, correlationId);  // return to client

        try {
            filterChain.doFilter(request, response);
        } finally {
            MDC.remove(MDC_KEY);  // clean up after request to prevent MDC leakage
        }
    }
}

// 2. RestTemplate interceptor: propagate correlation ID on outbound calls:
@Bean
public RestTemplate restTemplate() {
    RestTemplate restTemplate = new RestTemplate();
    restTemplate.getInterceptors().add((request, body, execution) -> {
        String correlationId = MDC.get("correlationId");
        if (correlationId != null) {
            request.getHeaders().set("X-Correlation-ID", correlationId);
        }
        return execution.execute(request, body);
    });
    return restTemplate;
}

// 3. WebClient (reactive) — propagate via context:
@Bean
public WebClient webClient() {
    return WebClient.builder()
        .filter((request, next) -> Mono.deferContextual(ctx -> {
            String correlationId = ctx.<String>getOrEmpty("correlationId")
                .orElse(MDC.get("correlationId"));
            ClientRequest modified = ClientRequest.from(request)
                .header("X-Correlation-ID", correlationId)
                .build();
            return next.exchange(modified);
        }))
        .build();
}

// 4. Kafka producer — propagate in message headers:
public void publishEvent(OrderPlacedEvent event) {
    ProducerRecord<String, OrderPlacedEvent> record =
        new ProducerRecord<>("order-placed-events", event.getOrderId(), event);
    String correlationId = MDC.get("correlationId");
    if (correlationId != null) {
        record.headers().add("X-Correlation-ID", correlationId.getBytes(StandardCharsets.UTF_8));
    }
    kafkaTemplate.send(record);
}

// 5. Kafka consumer — extract and restore correlation ID:
@KafkaListener(topics = "order-placed-events", groupId = "inventory-service")
public void handleOrderPlaced(ConsumerRecord<String, OrderPlacedEvent> record) {
    Header correlationHeader = record.headers().lastHeader("X-Correlation-ID");
    if (correlationHeader != null) {
        MDC.put("correlationId", new String(correlationHeader.value(), StandardCharsets.UTF_8));
    }
    try {
        inventoryService.reserve(record.value());
    } finally {
        MDC.remove("correlationId");
    }
}
```

---

### ❓ Why Does This Exist (Why Before What)

A microservices request can touch 10 services, generating hundreds of log entries across 10 processes in 10 containers on 10 different nodes. Without a linking identifier, finding all log entries for one user's failing request requires: checking timestamps across all services simultaneously, hoping timestamps are synchronized (they're not — NTP drift is real), and manually correlating messages that look vaguely related. Correlation IDs provide a deterministic, O(1) lookup: "give me everything for this ID."

---

### 🧠 Mental Model / Analogy

> A Correlation ID is like an order number at a restaurant. When you order, you get a number (42). The kitchen has it on the ticket. The runner has it on the plate. Customer service has it if you complain. Anyone in the restaurant can look up "order 42" and see its complete history. Without the order number: the kitchen has a memory of preparing "one medium pizza, extra cheese" but can't connect it to your table, your complaint, or your receipt. The number is the link — the single identifier that connects all related activities.

---

### ⚙️ How It Works (Mechanism)

**Header format and naming conventions:**

```
COMMON HEADER NAMES:
  X-Correlation-ID        (most common in REST APIs)
  X-Request-ID            (used by some frameworks)
  X-Trace-ID              (Zipkin/Jaeger)
  traceparent             (W3C Trace Context standard — OpenTelemetry)
                           Format: "00-{traceId}-{parentSpanId}-{flags}"
                           Example: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01

RECOMMENDATION:
  If using OpenTelemetry: use W3C traceparent header (industry standard)
  Correlation ID is included as the trace ID component of traceparent
  No need for separate X-Correlation-ID — OTel trace ID serves same function

VALIDATION:
  Always validate the incoming correlation ID (prevent log injection attacks):
  - Expected format: UUID v4 regex: [0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}
  - If invalid: reject the incoming ID, generate a new one
  - Prevents: someone sending X-Correlation-ID: "...<script>alert(1)</script>.."
               from potentially polluting logs with injected content
```

---

### 🔄 How It Connects (Mini-Map)

```
Distributed Logging
(centralized logs need linking mechanism)
        │
        ▼
Correlation ID  ◄──── (you are here)
(links log entries across services)
        │
        ├── OpenTelemetry → extends correlation ID with span hierarchy + timing
        └── Cross-Cutting Concerns → correlation ID is a cross-cutting implementation
```

---

### 💻 Code Example

**Kibana query using correlation ID:**

```json
// KQL query in Kibana Discover:
correlationId: "550e8400-e29b-41d4-a716-446655440000"

// Returns all log entries in timestamp order:
// 10:30:00.100 | INFO | api-gateway    | Request received GET /orders → correlationId=550e...
// 10:30:00.115 | INFO | order-service  | Processing order for customer cust-123 → correlationId=550e...
// 10:30:00.145 | INFO | payment-service| Initiating payment for order ord-456 → correlationId=550e...
// 10:30:00.892 | ERROR| payment-service| Payment failed: card declined → correlationId=550e...
// 10:30:00.900 | WARN | order-service  | Payment failed, cancelling order → correlationId=550e...
// 10:30:00.912 | INFO | order-service  | Order ord-456 cancelled → correlationId=550e...

// Immediately clear: payment failed at 10:30:00.892 due to card declined.
// Root cause found in <60 seconds.
```

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                                                                                                                                                                       |
| ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Correlation IDs are only for error debugging                | They are equally valuable for performance debugging (finding which service is slow for a specific request), business analytics (tracking a complete customer journey), and capacity planning (which requests touch the most services)                                                         |
| Correlation IDs replace distributed tracing (OpenTelemetry) | Correlation IDs tell you "what happened." OpenTelemetry tells you "what happened, how long each step took, and the exact call hierarchy." For performance debugging in production, you need OpenTelemetry. Correlation IDs are the minimal baseline                                           |
| Accepting X-Correlation-ID from untrusted clients is safe   | Client-provided correlation IDs should be validated against expected format (UUID). Invalid values should be rejected. A malicious user could otherwise inject content into logs (log injection attack)                                                                                       |
| MDC cleanup is optional                                     | Without `MDC.remove("correlationId")` in the `finally` block, thread pool threads will carry the previous request's correlation ID into the next request. Log entries from subsequent requests will be wrongly attributed to the previous request's correlation ID — corrupting your log data |

---

### 🔥 Pitfalls in Production

**Correlation ID lost at service boundary — async events:**

```
SCENARIO:
  OrderService places order → publishes OrderPlaced event to Kafka.
  Kafka message: event body only, NO message headers set.
  InventoryService consumes event → handles inventory reservation.
  InventoryService MDC: correlationId = null (not propagated through Kafka).

  Production failure: inventory reservation fails for certain orders.
  Debug attempt: search correlationId in Kibana.
  OrderService logs: found with correlationId=abc-123.
  InventoryService logs: NO correlationId → cannot find related log entries.

  Debug time: 2 hours (had to match timestamps manually).

FIX:
  Propagate correlation ID in Kafka message headers (see producer code above).
  Add to Kafka consumer setup: extract header → MDC.put.

  ADD TO INTEGRATION TESTS:
  Verify that Kafka message headers contain X-Correlation-ID after publish:
  ProducerRecord<?,?> capturedRecord = kafkaTemplate.send(...);
  assertThat(capturedRecord.headers().lastHeader("X-Correlation-ID")).isNotNull();

  AND verify Kafka consumer restores MDC:
  @KafkaListener handler: after processing, assert MDC.get("correlationId") == event's correlationId
```

---

### 🔗 Related Keywords

- `Distributed Logging` — correlation IDs enable log correlation across distributed services
- `Cross-Cutting Concerns` — correlation ID propagation is a cross-cutting implementation concern
- `OpenTelemetry` — distributed tracing extends the correlation ID concept with span hierarchy

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ FORMAT       │ UUID v4: xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx│
│ HEADER       │ X-Correlation-ID (or W3C traceparent)     │
│ GENERATE     │ API Gateway (or first service in chain)    │
├──────────────┼───────────────────────────────────────────┤
│ PROPAGATE    │ HTTP headers + Kafka headers + gRPC meta   │
│ LOG VIA      │ MDC (Logback, Log4j2) — auto in all logs  │
├──────────────┼───────────────────────────────────────────┤
│ VALIDATE     │ UUID format only (prevent log injection)   │
│ CLEANUP      │ MDC.remove() in finally — always!          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have MDC-based correlation ID propagation working for synchronous Spring Boot HTTP calls. Your system now introduces async processing: a request handler submits work to a `@Async` Spring method (runs on a different thread from the ThreadPoolTaskExecutor). The MDC is thread-local — the child thread doesn't inherit the parent thread's MDC. How do you propagate the correlation ID across thread boundaries in Spring `@Async` methods? Describe the `TaskDecorator` mechanism and implement it.

**Q2.** Your API gateway generates correlation IDs and propagates them through the system. A customer calls support with a problem. You want them to be able to give you the correlation ID so you can trace their request. How do you expose the correlation ID to the end user in a secure, user-friendly way? Should you put it in the API response body? The response header? A support UI that shows it? What are the security considerations of exposing internal request identifiers to end users?
