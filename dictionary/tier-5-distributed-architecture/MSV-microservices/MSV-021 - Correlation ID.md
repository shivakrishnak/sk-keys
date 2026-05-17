---
id: MSV-021
title: Correlation ID
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★☆
depends_on: MSV-010, MSV-002
used_by: MSV-022, MSV-064
related: MSV-022, MSV-064, MSV-065, MSV-063, MSV-011
tags:
  - microservices
  - observability
  - intermediate
  - debugging
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 21
permalink: /microservices/correlation-id/
---

# MSV-021 - Correlation ID

⚡ TL;DR - A Correlation ID is a unique identifier
attached to every request at its origin and propagated
through all downstream service calls, enabling log
correlation across services. Without it, debugging a
multi-service failure requires guessing which log entries
belong together across 10 different service logs.

| #021 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Inter-Service Communication, Microservices Architecture | |
| **Used by:** | Distributed Tracing, Distributed Logging | |
| **Related:** | Distributed Tracing, Distributed Logging, OpenTelemetry in Microservices, Cross-Cutting Concerns, Synchronous vs Async Communication | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A user reports: "My order placed at 2:34 PM failed." You
check logs:

- API Gateway: 10,000 log lines. Which one is this user?
- Order Service: 50,000 lines. Which 3 lines are related
  to this request?
- Payment Service: 20,000 lines. Which error corresponds
  to this order failure?
- Notification Service: Was the failure email sent?

Each service logs independently. There is no shared
identifier. You search by userId, but 500 requests were
made by this user. You search by timestamp, but clock
skew between services means timestamps don't align.
Investigation takes 4 hours.

**THE INVENTION MOMENT:**
A Correlation ID is a unique token (UUID) generated at
the entry point and included in every log line of every
service that processes this request. To debug any issue:
grab the Correlation ID, search all logs for that ID.
10 seconds to find every relevant log line across all
services.

---

### 📘 Textbook Definition

**Correlation ID** is a unique identifier assigned to
an incoming request at the system entry point (API Gateway
or first service) and propagated as an HTTP header
(`X-Correlation-ID`, `X-Request-ID`) or message property
to every downstream service call. Each service includes
the Correlation ID in all log entries for the duration
of processing that request. It enables log correlation:
given one ID, all log entries across all services for
one logical request can be retrieved with a single query.
Correlation ID is the foundation of distributed tracing
(where it is extended with span IDs for parent-child
call relationships).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A Correlation ID is a unique "thread" that ties together
all log entries from all services that processed a single
user request, making distributed debugging possible.

**One analogy:**
> A tracking number on a package. When the package ships,
> it gets one tracking number (the Correlation ID). Every
> logistics system (services) that handles the package
> records the tracking number in their database (logs).
> To find the package: search one tracking number across
> all logistics databases. Without tracking numbers:
> describe the package by weight and colour and guess
> which entries match.

**One insight:**
Correlation ID is free. Adding `log.info("Processing...",
kv("correlationId", MDC.get("correlationId")))` costs
nothing at runtime but reduces incident investigation
from hours to minutes. The teams that invest 2 hours to
implement Correlation ID properly save 200+ hours per
year in debugging. It is the highest-ROI observability
investment in microservices.

---

### 🔩 First Principles Explanation

**HOW IT PROPAGATES:**

```
Request origin: mobile app
  Generates UUID: "a4f8-9b12-34c5"
  (or API Gateway generates on ingress)

API Gateway:
  Receives request, no X-Correlation-ID header
  Generates: X-Correlation-ID: a4f8-9b12-34c5
  Adds to MDC: MDC.put("correlationId", "a4f8...")
  Logs: [a4f8-9b12-34c5] Routing to order-service
  Passes header downstream to Order Service

Order Service:
  Receives X-Correlation-ID: a4f8-9b12-34c5
  Puts in MDC
  Logs: [a4f8-9b12-34c5] Creating order for user U123
  Calls Payment Service WITH SAME HEADER

Payment Service:
  Receives X-Correlation-ID: a4f8-9b12-34c5
  Logs: [a4f8-9b12-34c5] Charging card XXXX-4242
  Logs: [a4f8-9b12-34c5] Payment declined: insufficient

Notification Service:
  Receives X-Correlation-ID: a4f8-9b12-34c5
  Logs: [a4f8-9b12-34c5] Sending failure email to U123

TO INVESTIGATE: grep 'a4f8-9b12-34c5' all_logs.txt
  Shows full request lifecycle across all 4 services
```

**MDC (Mapped Diagnostic Context):**

```
MDC is a thread-local Map in Java (SLF4J/Logback).
Any value put in MDC is automatically included in
every log statement on that thread.

logger.info("Order created");
// With MDC correlationId set:
// Output: [a4f8-9b12-34c5] Order created
// Without MDC: just "Order created" (no ID in log)

Key: MDC is THREAD-LOCAL. For reactive code (WebFlux)
or virtual threads, MDC requires special handling:
  - WebFlux: use Reactor Context and contextWrite
  - Virtual threads: Java 21 ScopedValue API
```

---

### 🧪 Thought Experiment

**CORRELATION ID IN ASYNC MESSAGING:**

```
SYNC (HTTP propagation - straightforward):
  Order Service -> HTTP header -> Payment Service
  X-Correlation-ID: abc123
  Always propagates with the request

ASYNC (Kafka message - requires explicit handling):
  Order Service publishes to Kafka:
    topic: order.created
    headers: {"correlationId": "abc123"}
    value: {orderId: 1, userId: U123}

  Payment Service consumes from Kafka:
    Reads header: correlationId = abc123
    MDC.put("correlationId", "abc123")
    Logs: [abc123] Processing payment for order 1

Without explicit header passing in Kafka messages:
  Kafka consumer logs have no correlation to HTTP logs
  You can match by orderId or userId, but if user
  has 10 orders in 5 minutes, you can't tell which
  Kafka event corresponds to which HTTP request.

KEY: Correlation ID must be explicitly propagated
  in message headers for async communication.
```

---

### 🧠 Mental Model / Analogy

> Correlation ID is like the hospital wristband with a
> unique patient ID. Every department (radiology, surgery,
> pharmacy) scans the wristband before documenting in
> their system. To reconstruct a patient's care journey:
search one patient ID across all departmental records.
> Without the wristband: search by name and date of
> birth, match records by description, hope nothing
> conflicts with another patient with the same name.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A Correlation ID is a unique code that travels with
every request as it passes through services. All services
put this code in their logs. To find all logs for one
user request: search for the code.

**Level 2 - How to use it (junior developer):**
In Spring Boot: add `X-Correlation-ID` header filter,
store in MDC, log pattern includes `%X{correlationId}`.
For outgoing HTTP calls: add `X-Correlation-ID` header
to RestTemplate/WebClient from MDC.

**Level 3 - How it works (mid-level engineer):**
Spring MDC (Mapped Diagnostic Context) stores the ID
as a thread-local variable. Logback's PatternLayout
reads MDC values via `%X{key}` in the log pattern.
For outgoing calls, add a ClientHttpRequestInterceptor
(RestTemplate) or ExchangeFilterFunction (WebClient)
that reads MDC and injects as header. For incoming:
a `HandlerInterceptor` or `Filter` reads the header
and puts in MDC (or generates a new UUID if absent).

**Level 4 - Why it was designed this way (senior/staff):**
Correlation ID and Trace ID are related but different.
Correlation ID: human-generated string that groups logs
for one "business request" (e.g., one checkout flow
that spans 3 sync calls and 2 async events). Trace ID:
distributed tracing system-generated ID (OpenTelemetry)
that captures parent-child span relationships. For
debugging: Correlation ID is simpler (just grep logs).
For performance analysis: Trace ID + spans give you
latency breakdown per service hop. Use both: Correlation
ID for log correlation, Trace ID for distributed tracing
and latency analysis.

**Level 5 - Mastery (distinguished engineer):**
At scale, Correlation ID faces the "fan-out" problem.
One BFF request fans out to 10 services. All 10 share
the same Correlation ID (correct for log correlation).
But which service call caused which latency? Distributed
tracing solves this with Span IDs: each service call
creates a new span with its own ID, linked to the parent
span. Correlation ID = trace ID in OpenTelemetry. The
W3C TraceContext header (`traceparent`) carries both
trace ID (correlation) and span ID (parent-child) in
one standardised header, replacing ad-hoc `X-Correlation-ID`
with an industry standard.

---

### ⚙️ How It Works (Mechanism)

**SPRING BOOT CORRELATION ID IMPLEMENTATION:**

```java
// 1. Filter: extract/generate Correlation ID
@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public class CorrelationIdFilter
    implements Filter {

    private static final String HEADER
        = "X-Correlation-ID";
    private static final String MDC_KEY
        = "correlationId";

    @Override
    public void doFilter(ServletRequest req,
        ServletResponse res, FilterChain chain)
        throws IOException, ServletException {

        HttpServletRequest httpReq =
            (HttpServletRequest) req;
        HttpServletResponse httpRes =
            (HttpServletResponse) res;

        String correlationId =
            httpReq.getHeader(HEADER);
        if (correlationId == null ||
                correlationId.isBlank()) {
            // Generate new ID if not provided
            correlationId = UUID.randomUUID()
                .toString().replace("-", "");
        }
        // Store in MDC for all log statements
        MDC.put(MDC_KEY, correlationId);
        // Return correlation ID to caller
        httpRes.setHeader(HEADER, correlationId);
        try {
            chain.doFilter(req, res);
        } finally {
            MDC.remove(MDC_KEY); // cleanup
        }
    }
}
```

```java
// 2. WebClient interceptor: propagate downstream
@Bean
public WebClient webClient() {
    return WebClient.builder()
        .filter(ExchangeFilterFunction
            .ofRequestProcessor(request ->
                Mono.just(
                    ClientRequest.from(request)
                        .header("X-Correlation-ID",
                            MDC.get("correlationId"))
                        .build())))
        .build();
}
```

```yaml
# 3. Logback pattern includes correlationId from MDC
# logback-spring.xml
<pattern>
  %d{ISO8601} [%X{correlationId}] %-5level
  %logger{36} - %msg%n
</pattern>
# Output:
# 2024-01-15T14:23:45 [a4f89b1234c5] INFO
#   o.s.OrderService - Creating order for U123
```

---

### 🔄 The Complete Picture - End-to-End Flow

**ASYNC PROPAGATION (Kafka):**

```java
// Producer: include correlationId in Kafka headers
public void publish(OrderCreatedEvent event) {
    String correlationId = MDC.get("correlationId");
    ProducerRecord<String, OrderCreatedEvent> record
        = new ProducerRecord<>(
            "order.created",
            event.getOrderId(),
            event);
    if (correlationId != null) {
        record.headers().add(
            "X-Correlation-ID",
            correlationId.getBytes());
    }
    kafkaTemplate.send(record);
}

// Consumer: restore correlationId from Kafka headers
@KafkaListener(topics = "order.created")
public void handle(
    @Header("X-Correlation-ID") String corrId,
    OrderCreatedEvent event) {
    try {
        MDC.put("correlationId", corrId);
        processOrder(event);
    } finally {
        MDC.remove("correlationId");
    }
}
// Async log entry now linked to original HTTP request
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: log without correlationId**

```java
// BAD: log entries cannot be correlated across services
log.info("Order created: orderId={}", orderId);
log.info("Payment charged: amount={}", amount);
// Across services, these look unrelated.
// To debug: filter by userId AND timestamp AND hope
```

```java
// GOOD: correlationId in MDC, included in every log
// MDC.put("correlationId", id) done in filter
log.info("Order created: orderId={}, userId={}",
    orderId, userId);
// Output:
// [a4f8-9b12] Order created: orderId=123, userId=U456

log.info("Payment charged: amount={}, currency={}",
    amount, currency);
// Output:
// [a4f8-9b12] Payment charged: amount=99.99, currency=USD

// Now: grep 'a4f8-9b12' in Kibana/CloudWatch
// Gets ALL log entries across ALL services
// for this single user request
```

---

### ⚖️ Comparison Table

| Pattern | Granularity | Requires library | Latency visible | Best For |
|---|---|---|---|---|
| **Correlation ID** | Request-level | No (just MDC) | No | Log correlation, debugging |
| **Distributed Tracing** | Span-level (per call) | Yes (OTel) | Yes | Performance profiling, latency analysis |
| **Log Aggregation** | Log-level | Yes (ELK/Splunk) | No | Centralized log search |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Correlation ID = Distributed Tracing | Correlation ID is a simple, human-assigned ID for log grouping. Distributed Tracing (OpenTelemetry) adds span IDs, parent-child relationships, and latency breakdown. Correlation ID is the foundation; tracing is the advanced extension. |
| MDC works in reactive/async code | MDC is thread-local. In Project Reactor (WebFlux), requests hop between threads. MDC is NOT automatically propagated. Reactor Context (`contextWrite`) must be used to propagate the correlation ID across reactive chains. |
| One correlation ID per microservice call | One correlation ID per user-facing request, propagated unchanged to ALL downstream services and async messages. The ID ties together the entire request lifecycle, not just one hop. |

---

### 🚨 Failure Modes & Diagnosis

**Correlation ID lost in async processing**

**Symptom:**
HTTP logs have correlationId. Kafka consumer logs don't.
Unable to link async payment processing back to the
original order request.

**Root Cause:**
Kafka producer not including correlationId in message
headers. Kafka consumer not reading headers or not
populating MDC.

**Diagnostic:**
```bash
# Check if correlationId appears in Kafka message headers
kafka-console-consumer.sh \
  --bootstrap-server kafka:9092 \
  --topic order.created \
  --from-beginning \
  --print-headers
# Should show: X-Correlation-ID:a4f8...
# If missing: producer is not setting headers

# Check MDC usage in consumer code
grep -r "MDC.put" payment-service/src/
# Should find: MDC.put("correlationId", corrId)
# in the @KafkaListener method
```

**Fix:**
1. In Kafka producer: add correlationId to RecordHeaders
2. In Kafka consumer: extract header, populate MDC
3. Add unit test: verify header in ProducerRecord
4. Add integration test: verify correlationId
   appears in Kafka consumer logs

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Inter-Service Communication` - Correlation ID is
  propagated via the inter-service communication headers

**Builds On This (learn these next):**
- `Distributed Tracing` - extends Correlation ID with
  span IDs and parent-child call relationships
- `Distributed Logging` - the aggregation infrastructure
  (ELK, Splunk) where you search by correlation ID

**Context:**
- `Cross-Cutting Concerns` - Correlation ID is a
  canonical cross-cutting concern: applies to every
  service, independent of business logic
- `OpenTelemetry in Microservices` - the W3C traceparent
  header is the standardised form of Correlation ID

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ HEADER       │ X-Correlation-ID (HTTP)                  │
│              │ Kafka message header (async)             │
├──────────────┼───────────────────────────────────────────┤
│ MDC          │ Thread-local: MDC.put / MDC.remove       │
│              │ Logback pattern: %X{correlationId}       │
├──────────────┼───────────────────────────────────────────┤
│ REACTIVE     │ WebFlux: MDC not thread-local            │
│ TRAP         │ Use Reactor Context + contextWrite()     │
├──────────────┼───────────────────────────────────────────┤
│ RULE         │ Generate once at entry, propagate ALL    │
│              │ downstream calls (HTTP + Kafka + gRPC)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Unique token per request, propagated to  │
│              │  all services, enabling log search"      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Distributed Tracing → OpenTelemetry     │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Generate once at entry point, propagate unchanged
   to ALL downstream services (HTTP header AND Kafka
   message header AND gRPC metadata).
2. MDC is thread-local and breaks in reactive code
   (WebFlux). For Project Reactor: use Reactor Context.
3. The W3C `traceparent` header is the standardised
   form. Consider using OpenTelemetry instead of ad-hoc
   `X-Correlation-ID` for new systems.

**Interview one-liner:**
"Correlation ID is a UUID generated at the entry point
and propagated as a header to every downstream service,
including Kafka message headers for async flows. Every
service stores it in MDC and includes it in all log
statements. This enables single-search investigation:
given one ID, grep all service logs to reconstruct
the complete request lifecycle. MDC is thread-local;
for reactive code, Reactor Context is required. W3C
traceparent header is the standardised version."

---

### 💡 The Surprising Truth

The most common failure mode for Correlation ID is not
not implementing it - it is implementing it only for
HTTP and forgetting async communication. A system may
have perfect Correlation ID propagation for synchronous
HTTP calls but lose the ID the moment a Kafka message
is published. Months later, an incident involves an
async Kafka consumer, and all async processing logs
are dark (no correlation). The retrospective reveals:
"We had Correlation IDs everywhere except Kafka." The
fix (adding headers to ProducerRecord) takes 10 minutes.
The operational cost of the missing implementation:
hours per incident. Treat async message propagation
as a first-class requirement alongside HTTP propagation.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **IMPLEMENT** Complete Correlation ID infrastructure:
Spring Filter (HTTP), Logback pattern, WebClient
interceptor (outbound HTTP), Kafka producer headers,
Kafka consumer MDC restore.
2. **FIX** Given a reactive WebFlux service where
correlationId disappears mid-chain, implement the
Reactor Context-based propagation solution.
3. **INTEGRATE** Align Correlation ID with W3C
traceparent header format for OpenTelemetry compatibility.
4. **AUDIT** Given a 10-service system, verify that
Correlation ID propagates correctly through: HTTP->HTTP,
HTTP->Kafka, Kafka->HTTP, HTTP->gRPC chains.
5. **QUERY** Given a specific Correlation ID, write
the Kibana query to find all log entries across all
services ordered by timestamp.

---

### 🧠 Think About This Before We Continue

**Q1.** A Correlation ID is used to tie logs together.
Distributed Tracing (OpenTelemetry) also uses a Trace ID.
If a system has both, what is the relationship between
them? Should they be the same value? Can one replace
the other? What does each add that the other doesn't?

**Q2.** A payment service processes messages from 3
Kafka topics: order.created, refund.requested, adjustment
.submitted. Each topic's producers have different
Correlation ID implementations (some use UUID, some use
orderId, some have no ID). Design a defensive Correlation
ID strategy for the consumer that provides useful IDs
regardless of what the producer sent.

**Q3.** With 1000 req/s, each request generating 50 log
lines across 10 services, your log volume is 50,000 lines
per second. Search by correlationId in Kibana takes 2
seconds (full text search over millions of logs). Design
an indexing strategy that makes correlationId lookup
sub-100ms. (Hint: consider Kibana index pattern, keyword
vs text field type, and log routing by correlationId
hash.)