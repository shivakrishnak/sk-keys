---
layout: default
title: "Structured Logging"
parent: "Observability & SRE"
nav_order: 1179
permalink: /observability/structured-logging/
number: "1179"
category: Observability & SRE
difficulty: ★★☆
depends_on: "Logging, Log Levels"
used_by: "Log Aggregation, ELK Stack, Loki, Observability"
tags: #observability, #structured-logging, #json-logging, #log-aggregation, #logstash
---

# 1179 — Structured Logging

`#observability` `#structured-logging` `#json-logging` `#log-aggregation` `#logstash`

⚡ TL;DR — **Structured logging** means emitting logs as machine-parseable key-value pairs (typically JSON) instead of free-form text strings. `{"level":"ERROR","userId":"123","orderId":"456","error":"payment_declined"}` instead of `"ERROR: payment declined for user 123 order 456"`. Structured logs can be indexed, searched, filtered, and aggregated programmatically — essential for centralized log aggregation in distributed systems.

| #1179           | Category: Observability & SRE                   | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------- | :-------------- |
| **Depends on:** | Logging, Log Levels                             |                 |
| **Used by:**    | Log Aggregation, ELK Stack, Loki, Observability |                 |

---

### 📘 Textbook Definition

**Structured logging**: a logging approach where log entries are emitted as structured data (typically JSON) rather than unstructured text strings, enabling programmatic parsing, indexing, and querying without regex. Each log event is a map of key-value pairs: predefined fields (`timestamp`, `level`, `service`, `traceId`) plus event-specific fields (`userId`, `orderId`, `duration_ms`, `event`). Benefits over unstructured logs: (1) **Queryable**: filter logs by exact field values without regex (`level="ERROR" AND service="order-service" AND userId="123"`); (2) **Aggregatable**: group by field, count by event type, compute average duration; (3) **Consistent**: all services emit the same core fields — log aggregation tools can process them uniformly; (4) **Parseable without configuration**: JSON is self-describing — no custom Logstash patterns needed to parse it. Java implementations: **Logstash Logback Encoder** (`net.logstash.logback:logstash-logback-encoder`) — the standard Spring Boot structured logging library; outputs Logback events as JSON automatically. Fields can be added via: MDC (request-scoped context), `StructuredArguments` (log-line-specific fields), custom `LogstashEncoder` configuration. Standards: **OpenTelemetry Log Data Model** defines a standard schema for structured log fields (`body`, `traceId`, `spanId`, `severityText`, `resource`, `attributes`).

---

### 🟢 Simple Definition (Easy)

Unstructured log: `"ERROR: failed to create order for user 123 - insufficient funds"`

Problem: to find all order failures by userId, you need a regex: `grep "user (\d+)" logs | awk...`

Structured log: `{"level":"ERROR","event":"order.failed","userId":"123","reason":"insufficient_funds"}`

Now you can query in Kibana: `level:ERROR AND event:order.failed AND reason:insufficient_funds` — no regex, instant results across all services, all dates, all machines.

---

### 🔵 Simple Definition (Elaborated)

Structured logging becomes essential when you have multiple services, multiple instances, and millions of log lines per day. Log aggregation tools (ELK, Loki, Datadog) ingest all logs centrally. With unstructured logs:

- To find a field, you write regex patterns → error-prone, fragile
- Each service has different log formats → different parsers needed
- Aggregation ("how many order failures per hour?") requires complex text processing

With structured logs:

- Every field is an indexed key — instant query with exact match
- All services use the same schema → uniform querying
- Aggregation is a simple `GROUP BY event, COUNT(*)` query

**Canonical fields for every log line**:

```json
{
  "timestamp": "2024-03-15T14:23:01.456Z", // ISO 8601 UTC
  "level": "ERROR", // TRACE/DEBUG/INFO/WARN/ERROR
  "service": "order-service", // which service
  "version": "1.2.3", // which version
  "environment": "production", // which environment
  "traceId": "abc123", // distributed trace ID (OpenTelemetry)
  "spanId": "def456", // span within the trace
  "userId": "user-789", // who triggered this event
  "event": "order.checkout.failed", // machine-readable event name
  "message": "Checkout failed: insufficient inventory", // human-readable
  "error": "InsufficientInventoryException", // error type if applicable
  "duration_ms": 234 // how long the operation took
}
```

---

### 🔩 First Principles Explanation

```xml
<!-- pom.xml: Logstash Logback Encoder for Spring Boot structured logging -->
<dependency>
    <groupId>net.logstash.logback</groupId>
    <artifactId>logstash-logback-encoder</artifactId>
    <version>7.4</version>
</dependency>
```

```xml
<!-- logback-spring.xml: output JSON in production -->
<configuration>
  <springProfile name="production">
    <appender name="JSON_CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
      <encoder class="net.logstash.logback.encoder.LogstashEncoder">
        <!-- Include standard fields automatically -->
        <includeCallerData>false</includeCallerData>  <!-- skip expensive caller info -->
        <includeContext>true</includeContext>           <!-- include logback context -->

        <!-- Add custom global fields to every log line -->
        <customFields>{"service":"order-service","environment":"${ENVIRONMENT}"}</customFields>

        <!-- Include MDC fields automatically (traceId, userId, etc.) -->
        <includeMdcKeyName>traceId</includeMdcKeyName>
        <includeMdcKeyName>userId</includeMdcKeyName>

        <!-- Field name overrides for OpenTelemetry compatibility -->
        <fieldNames>
          <timestamp>timestamp</timestamp>
          <version>[ignore]</version>  <!-- don't include logback version -->
        </fieldNames>

        <!-- Mask sensitive fields (credit card numbers, passwords) -->
        <jsonGeneratorDecorator class="net.logstash.logback.mask.MaskingJsonGeneratorDecorator">
          <valueMasker class="net.logstash.logback.mask.RegexValueMasker">
            <regex>\b\d{13,16}\b</regex>  <!-- mask potential card numbers -->
            <mask>****</mask>
          </valueMasker>
        </jsonGeneratorDecorator>
      </encoder>
    </appender>
  </springProfile>
</configuration>
```

```java
// LOGGING WITH STRUCTURED ARGUMENTS (Logstash Logback Encoder API)
import static net.logstash.logback.argument.StructuredArguments.*;

@Slf4j
@Service
public class OrderService {

    public OrderResponse createOrder(OrderRequest request) {
        // v() = value: adds field to JSON; message still gets the value interpolated
        log.info("Creating order",
            kv("userId", request.getUserId()),      // kv = key-value pair in JSON
            kv("itemCount", request.getItems().size()),
            kv("event", "order.create.started")
        );
        // Output: {"level":"INFO","message":"Creating order",
        //          "userId":"123","itemCount":3,"event":"order.create.started",...}

        long start = System.currentTimeMillis();
        try {
            OrderResponse response = processOrder(request);

            log.info("Order created",
                kv("userId", request.getUserId()),
                kv("orderId", response.getOrderId()),
                kv("total", response.getTotal()),
                kv("duration_ms", System.currentTimeMillis() - start),
                kv("event", "order.create.completed")
            );
            return response;

        } catch (InsufficientInventoryException e) {
            log.warn("Order creation blocked: insufficient inventory",
                kv("userId", request.getUserId()),
                kv("productId", e.getProductId()),
                kv("requested", e.getRequestedQty()),
                kv("available", e.getAvailableQty()),
                kv("event", "order.create.blocked.inventory"),
                kv("duration_ms", System.currentTimeMillis() - start)
            );
            throw e;
        }
    }

    // EXAMPLE OUTPUT (formatted for readability):
    // {
    //   "timestamp": "2024-03-15T14:23:01.456Z",
    //   "level": "WARN",
    //   "message": "Order creation blocked: insufficient inventory",
    //   "service": "order-service",
    //   "traceId": "abc123",          ← from MDC (set by LoggingFilter)
    //   "userId": "user-456",
    //   "productId": "prod-789",
    //   "requested": 5,
    //   "available": 2,
    //   "event": "order.create.blocked.inventory",
    //   "duration_ms": 45
    // }
}
```

```
QUERYING STRUCTURED LOGS IN KIBANA / LOKI:

  FIND ALL ORDER FAILURES IN LAST HOUR:
  level:"ERROR" AND event:"order.create.*" AND @timestamp:[now-1h TO now]

  FIND ALL EVENTS FOR A SPECIFIC TRACE (correlate across services):
  traceId:"abc123"  → returns ALL log lines from ALL services for that request

  FIND SLOW CHECKOUT OPERATIONS:
  event:"order.create.completed" AND duration_ms:>1000

  AGGREGATE: average order creation time per hour (Kibana):
  filter: event:"order.create.completed"
  metric: avg(duration_ms) over time

  STRUCTURED LOG SCHEMA EVOLUTION:
  ─────────────────────────────────────────────────────────
  Adding new fields: safe (Elasticsearch/Loki auto-discovers new fields)
  Renaming fields: BREAKING (all queries using the old name stop working)
  → Version your event names: "order.create.v2.completed" OR
  → Use a log schema registry (rare in practice; most teams use naming conventions)
```

---

### ❓ Why Does This Exist (Why Before What)

A single microservice in production might emit 10,000 log lines per minute. With 20 services, that's 200,000 log lines per minute. Finding a specific event — "what happened with user 123's checkout at 14:23?" — in unstructured text requires regex-based grep that is slow, fragile, and can't aggregate. Structured logging was adopted industry-wide as distributed systems scaled beyond the ability to grep log files manually. JSON became the de facto standard because it's self-describing, parseable by all log aggregation tools without configuration, and supports nested data.

---

### 🧠 Mental Model / Analogy

> **Structured logs are like a relational database vs a text file**: imagine storing all your orders in a text file: "Order 456: User 123 bought Widget for $49.99 on 2024-03-15." Finding all orders above $50 requires text parsing — slow, error-prone. Now imagine storing orders in a database with columns: orderId, userId, productName, amount, date. Finding orders above $50 is instant: `SELECT * WHERE amount > 50`. Structured logging applies the same principle to log data: each field is indexed, queryable, and aggregatable — not buried in unstructured text.

---

### 🔄 How It Connects (Mini-Map)

```
Logs need to be machine-parseable for aggregation and querying at scale
        │
        ▼
Structured Logging ◄── (you are here)
(JSON key-value log format; indexed fields; no regex required)
        │
        ├── Logging: structured logging is the production-grade approach to logging
        ├── Log Aggregation: requires structured logs to work effectively
        ├── ELK Stack: Elasticsearch indexes JSON fields automatically
        └── Loki: Grafana's log system — structured labels for efficient querying
```

---

### 💻 Code Example

```java
// COMPARING UNSTRUCTURED vs STRUCTURED LOGGING

// ❌ UNSTRUCTURED (don't do this):
log.error("Failed to process payment for order {} for user {} with card ending {}: {}",
    orderId, userId, cardLast4, e.getMessage());
// Output: "Failed to process payment for order 456 for user 123 with card ending 4242: Declined"
// Problem: to query this, you need: grep -P "order (\d+).*user (\d+)" — fragile

// ✓ STRUCTURED (do this):
log.error("Payment processing failed",
    kv("orderId", orderId),
    kv("userId", userId),
    kv("cardLast4", cardLast4),
    kv("errorCode", e.getErrorCode()),
    kv("errorMessage", e.getMessage()),
    kv("event", "payment.failed"),
    kv("paymentProvider", "stripe")
);
// Output: {"level":"ERROR","message":"Payment processing failed",
//          "orderId":"456","userId":"123","cardLast4":"4242",
//          "errorCode":"card_declined","event":"payment.failed",...}
// Query: event:"payment.failed" AND paymentProvider:"stripe" — instant, exact
```

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                                                                                                                                                                                                                                                                         |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Structured logging makes logs unreadable     | In development, JSON logs are hard to read visually. Solution: use text format in development (Spring profile `!production`) and JSON format in production (Spring profile `production`). Logback supports this with `<springProfile>` tags — the same codebase emits human-readable text locally and machine-parseable JSON in production.                                     |
| Any JSON output is structured logging        | Structured logging requires consistent, predictable schemas — not just wrapping the message in JSON. `{"message": "user 123 placed order 456"}` is technically JSON but functionally unstructured (the fields are embedded in the message string). True structured logging: `{"event": "order.placed", "userId": "123", "orderId": "456"}` — discrete, named, queryable fields. |
| Structured logging is only for large systems | Even a single-service application benefits: log aggregation services (like AWS CloudWatch Insights, Datadog) automatically parse JSON logs and enable instant ad-hoc queries without regex. A team of 3 engineers spending 30 minutes less per week debugging because of structured logging is significant ROI.                                                                 |

---

### 🔗 Related Keywords

- `Logging` — the broader practice; structured logging is the production best practice
- `Log Aggregation` — structured logs are the required input for effective aggregation
- `ELK Stack` — Elasticsearch indexes JSON fields; Kibana provides JSON log querying
- `Loki` — uses labels from structured logs for efficient indexing
- `OpenTelemetry` — defines a standard structured log schema

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STRUCTURED LOGGING = JSON log events with named fields  │
│                                                          │
│ CANONICAL FIELDS:                                       │
│  timestamp, level, service, version, environment       │
│  traceId, spanId (OpenTelemetry correlation)           │
│  userId, requestId (business context)                  │
│  event (machine-readable event name)                   │
│  message (human-readable description)                  │
│                                                          │
│ JAVA: Logstash Logback Encoder + kv() / StructuredArgs │
│ FORMAT: JSON in production; text in development        │
│ NEVER: embed IDs in message string (use kv() fields)  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Log schema governance in a multi-team microservices environment: Team A calls their field `userId`, Team B calls it `user_id`, Team C calls it `user`. When the security team queries "show me all events for user 123" across services, the inconsistent field names break queries. How do you enforce log schema standards across 10 teams with 30 services? Options: (a) publish and document a "logging schema specification" — relies on team discipline; (b) shared logging library that all teams must use — enforces schema but reduces flexibility; (c) log enrichment at the aggregation layer (normalize field names in Logstash/Fluent Bit pipeline) — fixes at collection but hides the underlying inconsistency. Which approach scales best? What governance process ensures the schema evolves without breaking existing queries?

**Q2.** Log-based metrics: modern log aggregation systems (Loki, Elasticsearch, Datadog) can generate metrics FROM logs — e.g., count log lines matching `event:order.created` per minute to produce an "orders per minute" metric, or calculate the average of `duration_ms` for all `event:payment.processed` events. This means you can get both logs AND metrics from a single structured logging implementation, without separate metric instrumentation. Compare this to a dedicated metrics system (Prometheus with Micrometer): what does Prometheus-based metrics give you that log-derived metrics can't? (Think: cardinality, storage efficiency, alerting latency, granularity.) When is log-derived metrics sufficient vs when do you need dedicated instrumentation?
