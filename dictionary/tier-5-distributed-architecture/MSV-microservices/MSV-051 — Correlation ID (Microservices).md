---
layout: default
title: "Correlation ID (Microservices)"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 51
permalink: /microservices/correlation-id-microservices/
id: MSV-051
category: Microservices
difficulty: ★★☆
depends_on: Distributed Logging, Cross-Cutting Concerns, Inter-Service Communication
used_by: OpenTelemetry (Microservices), Distributed Logging, Chaos Engineering
related: Distributed Tracing, OpenTelemetry (Microservices), Distributed Logging
tags:
  - microservices
  - observability
  - logging
  - operations
  - patterns
---

# MSV-051 — Correlation ID (Microservices)

⚡ TL;DR — A correlation ID is a unique identifier assigned to each incoming request and propagated through all service calls, linking every log entry and trace span for that request into one coherent narrative.

| #666            | Category: Microservices                                                  | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Logging, Cross-Cutting Concerns, Inter-Service Communication |                 |
| **Used by:**    | OpenTelemetry (Microservices), Distributed Logging, Chaos Engineering    |                 |
| **Related:**    | Distributed Tracing, OpenTelemetry (Microservices), Distributed Logging  |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
User "alice@example.com" reports: "My checkout failed." You search logs across 6 services for "alice" — you find 10,000 log entries over the past hour. You can't tell which log entries belong to her specific failed checkout attempt vs. other requests. The error message appears in multiple services for multiple users. You can't correlate which Payment Service error corresponds to which Order Service request. Investigation takes hours.

**THE BREAKING POINT:**
Without a shared identifier across service calls, individual log entries from different services are isolated fragments. You have data, but no way to assemble it into a coherent story for a specific request.

**THE INVENTION MOMENT:**
The correlation ID is the simplest and most powerful observability primitive: one UUID that every service stamps on every log line, every trace span, and every outgoing request header — turning a sea of logs into searchable, correlated narratives.

---

### 📘 Textbook Definition

A **correlation ID** (also called request ID, trace ID, or transaction ID) is a globally-unique identifier — typically a UUID — assigned to an incoming request at the system entry point (API gateway or first service). It is propagated through all downstream service calls via HTTP headers, message headers, or event metadata, and is included in every log line and trace span generated for that request. Engineers can query the centralised log system using the correlation ID to retrieve the complete, cross-service log narrative for any specific request.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
One UUID per user request; stamped on every log line from every service it touches; lets you find the full story of any request instantly.

**One analogy:**

> A package tracking number. When you ship a package, UPS assigns one tracking number. Every scan — departure, transit, arrival, delivery — is stamped with that same number. You can see the package's entire journey with one search. A correlation ID is the tracking number for a request moving through your microservices.

**One insight:**
The correlation ID is fundamentally simple — it's just a UUID in a header and an MDC variable. But its impact on incident response time is disproportionate. It transforms a 2-hour investigation into a 2-minute search.

---

### 🔩 First Principles Explanation

**THE FOUR-STEP PATTERN:**

**Step 1 — Assign at entry:**

```
Client request → API Gateway
  If X-Correlation-Id header present: use it
  If not: generate UUID, assign it
  Forward in all downstream calls
```

**Step 2 — Extract in every service:**

```java
// Every service extracts from incoming request
String correlationId = request.getHeader("X-Correlation-Id");
MDC.put("correlationId", correlationId);
```

**Step 3 — Include in every log line:**

```json
// Automatically included via MDC
{
  "message": "Order validated",
  "correlationId": "a1b2c3d4-e5f6-..."
}
```

**Step 4 — Forward in every outgoing call:**

```java
// Every outgoing HTTP call includes the header
headers.set("X-Correlation-Id",
            MDC.get("correlationId"));
```

**STANDARD HEADER NAMES:**

- `X-Correlation-Id` — most common in REST APIs
- `X-Request-Id` — used by AWS, GitHub
- `X-B3-TraceId` — Zipkin / B3 format
- `traceparent` — W3C Trace Context standard (OpenTelemetry)

**CORRELATION ID vs TRACE ID:**
Modern systems use both:

- **Correlation ID**: business-level request tracking; human-readable; used for log search
- **Trace ID**: distributed tracing span hierarchy; used for latency analysis in Jaeger/Zipkin
- OpenTelemetry bridges these: trace ID injected into MDC; log entries contain `traceId`; link from log to trace with one click

**THE TRADE-OFFS:**
**Gain:** Instant cross-service log correlation; rapid incident diagnosis; compliant audit trail; requires zero complex infrastructure.
**Cost:** Every service must propagate the header (one missing link breaks the chain); correlation ID must not contain PII (it appears in all logs and headers); async flows (events) need explicit metadata propagation.

---

### 🧪 Thought Experiment

**SETUP:**
Five services in a checkout flow. No correlation IDs. An error occurs in the Payment Service.

**INVESTIGATION WITHOUT CORRELATION ID:**
Search Payment Service logs for `ERROR` in the last hour: 45 errors. Which one is yours? You know the user's email but the Payment Service only logs `paymentId`. You don't have the paymentId. You go to Order Service, find the order by email, get the orderId. Go back to Payment Service, find the paymentId from the orderId. Now search Payment Service logs again. Find the error. But which Inventory Service call corresponds to this order? Search Inventory Service logs for the product ID in that order. 45 minutes.

**INVESTIGATION WITH CORRELATION ID:**
Kibana query: `correlationId: "a1b2c3d4"`.
Result: All log entries from all 5 services, in timestamp order, for exactly that checkout attempt. Error in Payment Service on line 4. Root cause visible in 30 seconds.

**THE INSIGHT:**
The correlation ID doesn't add information — it adds _organisation_. The data was always there; the correlation ID makes it instantly accessible as a coherent story.

---

### 🧠 Mental Model / Analogy

> A correlation ID is like a thread colour in a tapestry. Each service is a different weave running through the tapestry. Without a thread colour, you can't follow any individual strand through the complex weave. With a unique colour per request, you can trace exactly one request's thread from entry to exit, ignoring all other threads.

- "Individual threads" → individual service log entries
- "Thread colour" → correlation ID value
- "Complex tapestry" → centralised log system with millions of entries
- "Tracing one thread" → querying `correlationId: "abc-123"`
- "Ignoring other threads" → filtering out other requests' log entries

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When a user's action starts, it gets a unique ID number. Every service that handles that action writes that ID in their logs. Later, when you search for that ID, you see everything that happened for that exact action — from start to finish, across all services.

**Level 2 — How to implement it (junior developer):**

1. Add a servlet filter that extracts or generates the correlation ID and puts it in MDC.
2. Configure logback to include MDC in every log line (`includeMdcKeyName`).
3. Add a RestTemplate/Feign/WebClient interceptor that copies MDC correlation ID to outgoing request headers.
4. For Kafka: include correlation ID in message headers; extract in consumer.

**Level 3 — Handling async flows (mid-level engineer):**
HTTP: correlation ID lives in request headers + MDC (thread-local). Works automatically.
Async (Kafka): correlation ID must be explicitly added to message headers/payload and extracted by consumer. Thread-local MDC doesn't survive across thread/process boundaries.

```java
// Kafka producer: add correlation ID to header
ProducerRecord<String, String> record = new ProducerRecord<>(...);
record.headers().add("X-Correlation-Id",
  MDC.get("correlationId").getBytes());

// Kafka consumer: extract and set MDC
String correlationId = new String(
  record.headers().lastHeader("X-Correlation-Id").value());
MDC.put("correlationId", correlationId);
```

**Level 4 — OpenTelemetry integration (senior/staff):**
The W3C Trace Context standard (`traceparent` header) carries a `traceId` that serves as a standardised correlation ID across observability backends. OpenTelemetry instrumentation automatically propagates `traceparent` headers and injects `traceId`+`spanId` into MDC. This means the correlation ID for logs and the trace ID for distributed tracing are the same identifier, enabling: click from a log entry → open the parent trace in Jaeger. This is the "convergence" of logs and traces — a correlation ID becomes a first-class observability artifact, not just a log search helper.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│         Correlation ID — Propagation Chain              │
└─────────────────────────────────────────────────────────┘

Request:  GET /checkout
          X-Correlation-Id: a1b2c3-4d5e-6f7g-8h9i

API Gateway:
  - Receives request
  - Extracts X-Correlation-Id: a1b2c3-4d5e-...
  - Logs: {correlationId: "a1b2c3...", msg: "request received"}
  - Forwards to Order Service with same header

Order Service:
  - Extracts X-Correlation-Id: a1b2c3-4d5e-...
  - MDC.put("correlationId", "a1b2c3...")
  - Logs: {correlationId: "a1b2c3...", msg: "order validated"}
  - Calls Inventory Service: adds header a1b2c3-...
  - Calls Payment Service: adds header a1b2c3-...

Inventory Service:
  - Extracts, logs: {correlationId: "a1b2c3..."}

Payment Service:
  - Extracts, logs: {correlationId: "a1b2c3..."}
  - ERROR: {correlationId: "a1b2c3...", msg: "card declined"}

Kibana query: correlationId: "a1b2c3-4d5e-6f7g-8h9i"
→ All 8 log entries from 4 services, in time order
→ Complete incident narrative
```

**MDC lifecycle management:**

```java
// CRITICAL: always clean up MDC to prevent leaks
// (thread pool reuse can carry old correlation IDs)
try {
  MDC.put("correlationId", correlationId);
  chain.doFilter(req, res);
} finally {
  MDC.remove("correlationId"); // ALWAYS in finally
}
```

---

### 🔄 The Complete Picture

**PASSING THROUGH KAFKA:**

```
Order Service (produces):
  Event: OrderPlaced
  Headers: X-Correlation-Id: a1b2c3

Notification Service (consumes):
  Extract header: X-Correlation-Id: a1b2c3
  MDC.put("correlationId", "a1b2c3")
  Logs: {correlationId: "a1b2c3", msg: "sending email"}

→ Async flow fully correlated in logs
```

**RETURNING CORRELATION ID TO CLIENT:**

```
HTTP Response headers:
  X-Correlation-Id: a1b2c3-4d5e-6f7g-8h9i

Client-facing error message:
  "An error occurred. Reference: a1b2c3"

Support engineer: searches Kibana for a1b2c3
→ Full incident context in seconds
```

---

### 💻 Code Example

**Complete correlation ID filter (production-ready):**

```java
@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public class CorrelationIdFilter extends OncePerRequestFilter {

  public static final String HEADER = "X-Correlation-Id";
  public static final String MDC_KEY  = "correlationId";

  @Override
  protected void doFilterInternal(
      HttpServletRequest req,
      HttpServletResponse res,
      FilterChain chain) throws IOException, ServletException {

    String correlationId = Optional
      .ofNullable(req.getHeader(HEADER))
      .filter(s -> !s.isBlank())
      .map(this::sanitize)
      .orElse(UUID.randomUUID().toString());

    MDC.put(MDC_KEY, correlationId);
    res.setHeader(HEADER, correlationId);

    try {
      chain.doFilter(req, res);
    } finally {
      MDC.remove(MDC_KEY);  // Prevent MDC leaks
    }
  }

  // Prevent header injection attacks — only allow UUID characters
  private String sanitize(String correlationId) {
    if (correlationId.matches(
        "[a-fA-F0-9\\-]{8,64}")) {
      return correlationId;
    }
    return UUID.randomUUID().toString();
  }
}
```

**WebClient propagation (reactive):**

```java
@Bean
public WebClient webClient() {
  return WebClient.builder()
    .filter((request, next) -> {
      String correlationId = MDC.get("correlationId");
      ClientRequest decorated = ClientRequest.from(request)
        .header("X-Correlation-Id", correlationId != null
          ? correlationId
          : UUID.randomUUID().toString())
        .build();
      return next.exchange(decorated);
    })
    .build();
}
```

---

### ⚖️ Comparison Table

| Identifier               | Scope                         | Format      | Primary Use                      |
| ------------------------ | ----------------------------- | ----------- | -------------------------------- |
| **Correlation ID**       | Business request (end-to-end) | UUID        | Log search, audit, support       |
| Trace ID (OpenTelemetry) | Distributed trace             | 128-bit hex | Latency analysis, span hierarchy |
| Span ID                  | Single operation              | 64-bit hex  | Individual operation timing      |
| Session ID               | User session                  | Opaque      | Session-scoped grouping          |
| Request ID               | Single HTTP request           | UUID        | Single-hop tracing               |

**How to choose:** Use correlation ID as the primary business-level identifier for log correlation. Let OpenTelemetry provide the trace ID for performance tracing. Align them when using W3C Trace Context.

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                               |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Correlation ID and trace ID are the same        | Correlation ID is for logs/business tracking; trace ID is for span hierarchy; OpenTelemetry aligns them               |
| One missing service breaks the entire chain     | Partial: logs before and after the missing service are still correlated; only the missing service's logs are unlinked |
| Correlation IDs can contain user data           | Never — correlation IDs appear in logs, headers, and error messages; they must be opaque UUIDs                        |
| Correlation ID tracking is complex to implement | A single filter + MDC configuration handles 95% of cases                                                              |
| You need a service mesh for correlation IDs     | A simple filter in each service is sufficient; service mesh can automate it but isn't required                        |

---

### 🚨 Failure Modes & Diagnosis

**MDC Leak — Wrong Correlation ID in Logs**

**Symptom:** Log entries appear with correlation IDs from different requests; logs for request A show correlation ID from request B.

**Root Cause:** Thread pool reuse (servlet threads) carrying stale MDC values; `MDC.remove()` not called in `finally` block.

**Diagnostic Command:**

```bash
# Find requests where multiple correlation IDs appear in one service trace
# (indicates MDC leakage)
curl -XGET 'elasticsearch:9200/logstash-*/_search' -d '{
  "aggs": {
    "by_thread": {
      "terms": { "field": "thread_name" },
      "aggs": {
        "unique_correlation_ids": {
          "cardinality": {
            "field": "correlationId"
          }
        }
      }
    }
  }
}'
```

**Fix:** Ensure all MDC operations are in try-finally blocks. Use a framework filter that guarantees cleanup.

---

**Correlation ID Not Forwarded in Async Calls**

**Symptom:** Kibana shows log entries stopping at Service B; no entries from Service C (which receives Kafka messages from B).

**Root Cause:** Kafka producer didn't add correlation ID to message headers; consumer didn't extract and set MDC.

**Fix:** Add correlation ID to Kafka message headers in producer; extract in consumer before processing.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Distributed Logging` — the system that makes correlation IDs queryable
- `Cross-Cutting Concerns` — correlation ID propagation is a cross-cutting concern
- `Inter-Service Communication` — the mechanisms across which correlation IDs propagate

**Builds On This (learn these next):**

- `OpenTelemetry (Microservices)` — standardises correlation ID as W3C `traceparent`
- `Distributed Tracing` — extends correlation ID with span hierarchy and latency data

**Alternatives / Comparisons:**

- `Distributed Tracing (Jaeger/Zipkin)` — provides structured spans; uses trace ID (same concept)
- `W3C Trace Context` — the standard `traceparent` header that unifies correlation and trace IDs

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ UUID per request, propagated through all  │
│              │ services, stamped on all log lines        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Cross-service log correlation is          │
│ SOLVES       │ impossible without a shared identifier    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ One ID per request; query once;           │
│              │ see complete cross-service story          │
├──────────────┼───────────────────────────────────────────┤
│ HEADER NAME  │ X-Correlation-Id (REST)                   │
│              │ traceparent (W3C/OpenTelemetry)           │
├──────────────┼───────────────────────────────────────────┤
│ CRITICAL     │ Must propagate through async flows (Kafka)│
│              │ MDC must be cleaned up in finally block   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "One UUID; every service; every log line" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Distributed Logging → OpenTelemetry →     │
│              │ Three Pillars of Observability            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A user calls support with an error. Your API gateway returns `X-Correlation-Id: a1b2c3` in the response. The support engineer searches Kibana for `correlationId: "a1b2c3"` and finds logs from only 3 of the 5 services the request touched. Name 3 reasons why 2 services might be missing, and the specific fix for each.

**Q2.** Your system is processing 10,000 Kafka messages per second. Each message triggers a processing pipeline that calls 3 downstream services. You want every log line — both for the Kafka consumer and the downstream service calls — to have the same `correlationId`. Sketch the exact implementation: what the Kafka message header contains, how the consumer extracts it, and how the downstream HTTP calls propagate it.
