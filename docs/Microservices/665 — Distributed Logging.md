---
layout: default
title: "Distributed Logging"
parent: "Microservices"
nav_order: 665
permalink: /microservices/distributed-logging/
number: "665"
category: Microservices
difficulty: ★★★
depends_on: "Cross-Cutting Concerns, Correlation ID"
used_by: "OpenTelemetry, Observability & SRE"
tags: #advanced, #microservices, #observability, #distributed, #architecture
---

# 665 — Distributed Logging

`#advanced` `#microservices` `#observability` `#distributed` `#architecture`

⚡ TL;DR — **Distributed Logging** is the practice of collecting, correlating, and querying log entries from multiple microservices as if they were a single unified log stream. Requires: structured log format (JSON), correlation IDs propagated across service calls, centralized log aggregation (ELK/Grafana Loki), and trace context (OpenTelemetry). Without it, debugging multi-service requests is forensically impossible.

| #665            | Category: Microservices                                  | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------- | :-------------- |
| **Depends on:** | Cross-Cutting Concerns, Correlation ID                   |                 |
| **Used by:**    | OpenTelemetry, Observability & SRE                       |                 |

---

### 📘 Textbook Definition

**Distributed Logging** in microservices refers to the architecture and practices for capturing, aggregating, and querying log data produced by multiple independent services. Each service writes logs to its local stdout/stderr (or file); a log shipping agent (Filebeat, Fluentd, Promtail) forwards logs to a centralized aggregation system (Elasticsearch/Kibana — ELK stack; Grafana Loki; AWS CloudWatch; Datadog). Logs from different services are correlated using a **Correlation ID** (unique request identifier propagated through all service calls via HTTP headers or Kafka message headers) and **distributed trace context** (OpenTelemetry TraceID/SpanID). Without these identifiers, logs from a single user request are indistinguishable from logs of concurrent requests across 10 services. Best practices: structured logging in JSON (queryable fields, not free-text parsing); minimum required fields per log entry (timestamp, level, service name, correlation ID, trace ID, span ID); log levels (DEBUG, INFO, WARN, ERROR) used consistently; sensitive data (PII, passwords, tokens) never logged.

---

### 🟢 Simple Definition (Easy)

In a microservices system, one user request touches 5 services. Each service writes log messages. Without distributed logging: 5 separate log files, no way to connect them. With distributed logging: all logs go to one central system, and each log line carries a correlation ID. Search for the correlation ID → see all log lines from all 5 services, in time order, for that one request.

---

### 🔵 Simple Definition (Elaborated)

User clicks "Place Order." Request flow: Browser → API Gateway → OrderService → PaymentService → InventoryService. Something fails silently. Without distributed logging: you check 5 separate log sources, manually matching timestamps to find which service failed. With distributed logging: the API Gateway injects `X-Correlation-ID: abc-123`. Every service adds `correlationId: "abc-123"` to its log entries. Search `correlationId=abc-123` in Kibana: all log entries from all 5 services appear in timestamp order. The failed step is immediately visible.

---

### 🔩 First Principles Explanation

**Structured logging — JSON format is non-negotiable:**

```
❌ UNSTRUCTURED LOG (Useless for distributed systems):
  2024-01-15 10:30:00 INFO  Order placed for customer 123 amount 49.99
  
  Problems:
  - Parsing required to extract fields: regex = brittle, slow
  - No standard field names: correlationId? traceId? Where?
  - Different format per service: 15 services = 15 parsing rules in log aggregator

✅ STRUCTURED LOG (JSON — queryable, correlatable):
  {
    "timestamp": "2024-01-15T10:30:00.123Z",
    "level": "INFO",
    "service": "order-service",
    "version": "2.3.1",
    "correlationId": "550e8400-e29b-41d4-a716-446655440000",
    "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",
    "spanId": "00f067aa0ba902b7",
    "userId": "user-123",
    "orderId": "ord-456",
    "message": "Order placed successfully",
    "durationMs": 142
  }
  
  Benefits:
  - Kibana/Loki: query by ANY field instantly
  - No parsing required: fields already extracted
  - Standard format: same across all 15 services
  - Correlation: filter by correlationId → all related entries
```

**Log aggregation architecture — how logs flow from service to query:**

```
ARCHITECTURE (ELK stack):

  Service Pod
  ┌──────────────────────────┐
  │  application.jar         │ → stdout: JSON log lines
  │  Filebeat (sidecar)      │ → reads stdout, ships to Logstash
  └──────────────────────────┘

  OR (Kubernetes DaemonSet — one Filebeat per node):
  ┌──────────────────────────┐
  │  Node                    │
  │  All pods on this node   │ → /var/log/containers/*.log
  │  Filebeat (DaemonSet)    │ → reads all container logs, ships to Elasticsearch
  └──────────────────────────┘

  Logstash (optional transform layer):
  - Parse/enrich logs (add environment tag, strip sensitive fields)
  - Route: error logs → high-priority index; debug → low-priority

  Elasticsearch:
  - Store all logs (indexed by correlationId, traceId, service, level, timestamp)
  - Retention: 30 days hot storage, 90 days warm, 1 year cold (S3 snapshot)

  Kibana (query/visualize):
  - Discover: search logs by field
  - Dashboard: error rate per service, log volume, slow request count
  - Alerting: ERROR count > 50/min → PagerDuty alert

ALTERNATIVE — Grafana Loki (lower cost, simpler):
  - Loki: stores logs with labels (no full-text index = cheaper storage)
  - Promtail: log shipper (like Filebeat for Loki)
  - Grafana: unified view (same UI as Prometheus metrics + Loki logs)
  - LogQL: query language for Loki
  - Trade-off: less powerful text search vs Elasticsearch; lower cost
```

**Log levels — standard usage in microservices:**

```
ERROR — action required:
  Service cannot process a request due to unrecoverable error.
  External dependency unavailable, database error, data corruption detected.
  Every ERROR should generate an alert (PagerDuty for Sev-1 type errors).
  Example: "Payment processing failed: database connection refused"

WARN — investigate soon:
  Unexpected situation that was handled gracefully.
  Retry succeeded after 2 attempts, circuit breaker half-open.
  No immediate action required but should be reviewed.
  Example: "Customer service responded slowly (1200ms), fallback cache used"

INFO — normal operations:
  Business-significant events: order placed, user logged in, payment completed.
  High-level request lifecycle: start/end of significant operations.
  NOT: every function call, every DB query. INFO should be meaningful events.
  Example: "Order ord-123 confirmed. Customer cust-456. Amount $49.99"

DEBUG — diagnostic detail (disabled in production):
  Internal state, SQL queries, HTTP request/response bodies.
  Enabled dynamically via feature flag or log level API endpoint.
  Example: "Executing SQL: SELECT * FROM orders WHERE id = ? [params: ord-123]"

TRACE — exhaustive debugging (development only):
  Every function entry/exit, every variable state.
  Never in production (massive log volume, performance impact).

PRODUCTION LOG LEVEL RECOMMENDATION:
  Baseline: INFO (captures meaningful events, manageable volume)
  Dynamic DEBUG: enable per-service via Spring Boot Actuator:
  POST /actuator/loggers/com.example.orderservice
  Body: {"configuredLevel": "DEBUG"}
  → Enable DEBUG for 5 minutes, then reset to INFO
  → No restart needed
```

**Sensitive data — what must NEVER appear in logs:**

```
NEVER LOG:
  ❌ Passwords, PIN codes, secret keys
  ❌ Credit card numbers (PCI DSS: even masked cards should be avoided)
  ❌ Full JWT tokens (contains identity claims)
  ❌ Social Security Numbers / National ID numbers
  ❌ Full email addresses (GDPR PII concern in some jurisdictions)
  ❌ OAuth refresh tokens
  ❌ Database connection strings
  ❌ Full request/response bodies if they may contain above

SAFE TO LOG:
  ✅ User ID / Customer ID (opaque identifier, not direct PII)
  ✅ Order ID, payment transaction ID (business identifiers)
  ✅ Last 4 digits of card number (for debugging payment issues)
  ✅ Masked email: a***@example.com (some teams allow this)
  ✅ Correlation IDs, trace IDs
  ✅ Service names, endpoint paths

JAVA IMPLEMENTATION — @JsonIgnore in logged objects:
  @JsonInclude(JsonInclude.Include.NON_NULL)
  class PaymentRequest {
      private String orderId;           // ✅ safe to log
      @JsonIgnore
      private String cardNumber;        // ❌ never in logs
      @JsonIgnore
      private String cvv;               // ❌ never in logs
      private String cardLastFour;      // ✅ safe to log
  }
```

---

### ❓ Why Does This Exist (Why Before What)

In a monolith, all log lines go to one file/stream. Debugging is: `grep "user-123" app.log`. In microservices, the equivalent request generates log entries in 10 different services, 10 different processes, 10 different containers. Without centralized aggregation and correlation, debugging production issues requires manual correlation of timestamps across 10 separate log sources — effectively impossible under pressure. Distributed logging is not optional in microservices; it is the minimum observability baseline.

---

### 🧠 Mental Model / Analogy

> Distributed logging is like a hospital patient tracking system. A patient (request) visits multiple departments: Emergency, Radiology, Pharmacy, Surgery. Each department writes notes in the patient's file. Without a central patient ID system: each department has separate paper files — if the patient goes unconscious and can't speak, you cannot find their history across departments. With a central patient ID (correlation ID): search "Patient ID: P-12345" → see all department notes in chronological order, from any terminal in the hospital. Distributed logging is building that patient ID system for your microservices.

---

### ⚙️ How It Works (Mechanism)

**Logback JSON configuration for Spring Boot services:**

```xml
<!-- logback-spring.xml — standard configuration via shared chassis -->
<configuration>
    <springProfile name="!local">
        <!-- Production: JSON format for log aggregators -->
        <appender name="JSON_STDOUT" class="ch.qos.logback.core.ConsoleAppender">
            <encoder class="net.logstash.logback.encoder.LogstashEncoder">
                <includeMdcKeyName>correlationId</includeMdcKeyName>
                <includeMdcKeyName>traceId</includeMdcKeyName>
                <includeMdcKeyName>spanId</includeMdcKeyName>
                <includeMdcKeyName>userId</includeMdcKeyName>
                <customFields>{"service":"${spring.application.name}",
                               "env":"${ENVIRONMENT}"}</customFields>
            </encoder>
        </appender>
        <root level="INFO">
            <appender-ref ref="JSON_STDOUT"/>
        </root>
    </springProfile>

    <springProfile name="local">
        <!-- Local: human-readable format -->
        <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
            <encoder>
                <pattern>%d{HH:mm:ss.SSS} [%thread] %-5level [%X{correlationId}] %logger{36} - %msg%n</pattern>
            </encoder>
        </appender>
        <root level="DEBUG">
            <appender-ref ref="STDOUT"/>
        </root>
    </springProfile>
</configuration>
```

---

### 🔄 How It Connects (Mini-Map)

```
Cross-Cutting Concerns
(logging as a concern all services share)
        │
        ▼
Distributed Logging  ◄──── (you are here)
(centralized log collection + correlation)
        │
        ├── Correlation ID → the identifier that links logs across services
        ├── OpenTelemetry → adds trace/span context to correlate logs + traces
        └── Observability & SRE → logs + metrics + traces = golden triangle
```

---

### 💻 Code Example

**Querying correlated logs in Kibana (Lucene/KQL query):**

```
# Find all log entries for a specific user request:
correlationId: "550e8400-e29b-41d4-a716-446655440000"
→ Returns: 47 entries from 5 services in timestamp order
→ Instantly see which service logged the error

# Find all errors in OrderService in the last hour:
service: "order-service" AND level: "ERROR"
AND @timestamp: [now-1h TO now]

# Find all requests taking more than 2 seconds (durationMs field):
service: "payment-service" AND durationMs: [2000 TO *]

# Find all requests where circuit breaker was triggered:
message: "Circuit breaker" AND level: "WARN"

# Find requests for a specific customer:
userId: "user-123" AND level: "INFO"
→ Full history of what OrderService, PaymentService, etc. did for user-123
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Centralised logging is too expensive for all services | Log volume is manageable with appropriate log levels (INFO in production, not DEBUG). Grafana Loki is significantly cheaper than Elasticsearch for pure log storage (labels-only indexing). Cost grows with log volume — which is controlled by log level discipline |
| Logs alone are sufficient for debugging microservices | Logs tell you what happened. Distributed traces tell you how long each step took and where the latency is. Metrics tell you the rate of occurrence. The "three pillars of observability" (logs, traces, metrics) are all needed — logs alone leave significant blind spots |
| Correlation IDs are automatically propagated | Correlation ID propagation must be explicitly implemented: extracted from incoming HTTP headers, placed in MDC for logging, and injected into all outbound HTTP calls and Kafka messages. If even one service in the chain doesn't propagate the ID, the correlation chain is broken |
| Service logs should capture every database query for debugging | DEBUG-level SQL logging in production causes: massive log volume (10-100x more entries), storage cost explosion, performance overhead (log serialization is not free), and PII exposure risk (queries may contain sensitive parameter values). Enable selectively and temporarily |

---

### 🔥 Pitfalls in Production

**Log volume explosion — DEBUG enabled in production:**

```
SCENARIO:
  On-call engineer enables DEBUG logging on payment-service during incident.
  Forgets to reset to INFO after incident resolved.
  payment-service: 1,000 requests/second.
  DEBUG: 200 log entries per request (SQL queries, HTTP internals, Spring internals)
  → 200,000 log entries/second from ONE service
  → Elasticsearch indexing queue fills up
  → Log aggregation lag: 15 minutes behind real-time
  → All services' logs are delayed (shared Elasticsearch cluster)
  → OTHER incident: team cannot see real-time logs to diagnose → operational blindness

  COST: at 200,000 entries/second → 720M entries/hour → ~1TB/hour of storage

PREVENTION:
  1. Automated log level reset:
     When enabling DEBUG via Actuator → auto-reset to INFO after 10 minutes
     Implementation: scheduled task or TTL on level override

  2. Log sampling: only log DEBUG for 1% of requests:
     @Around("@annotation(Debuggable)")
     Object logIfSampled(ProceedingJoinPoint pjp) {
         if (Math.random() < 0.01) {  // 1% sampling
             log.debug("Method call: {} args: {}", pjp.getSignature(), pjp.getArgs());
         }
         return pjp.proceed();
     }

  3. Log budget alerting:
     Alert: log ingestion rate > 50,000 entries/min for any single service
     → Auto-notify the service team to investigate and reset log level

  4. Separate log indices per log level:
     INFO logs → "logs-info-*" (30 days retention)
     DEBUG logs → "logs-debug-*" (1 day retention, small index)
     ERROR logs → "logs-error-*" (1 year retention for audit)
```

---

### 🔗 Related Keywords

- `Correlation ID` — the mechanism that links log entries across services
- `Cross-Cutting Concerns` — logging is a cross-cutting concern for all services
- `OpenTelemetry` — provides trace/span IDs that enrich distributed log correlation
- `Observability & SRE` — distributed logging is one pillar of the observability stack

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ REQUIRED     │ JSON format + correlationId + traceId     │
│ LOG LEVELS   │ ERROR (alert), WARN (review), INFO (ops)  │
│              │ DEBUG (off in prod, enable dynamically)   │
├──────────────┼───────────────────────────────────────────┤
│ STACK        │ Filebeat/Promtail → Elasticsearch/Loki    │
│ QUERY        │ Kibana/Grafana by correlationId           │
├──────────────┼───────────────────────────────────────────┤
│ NEVER LOG    │ Passwords, card numbers, tokens, SSNs     │
│ DANGER       │ DEBUG in prod = log volume explosion       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your distributed logging system uses Elasticsearch for 20 microservices. Average log volume: 50GB/day. Retention requirement: 90 days hot storage (searchable) + 1 year cold storage (compliance). Calculate the total storage requirements. Design the Elasticsearch index lifecycle policy (ILM): when do indices move from hot to warm to cold? How do you ensure compliance queries (find all logs for user X from 8 months ago) are still possible on cold storage? What are the query performance trade-offs between hot and cold tiers?

**Q2.** You're implementing distributed logging for a polyglot microservices system: 8 Java/Spring Boot services, 4 Node.js services, and 3 Python services. Each has different logging frameworks (Logback, Winston, Python logging). Design a company-wide logging standard that works across all three stacks. What shared configuration can be provided (Docker base image with pre-configured log shipper? Environment variables for log format?). How do you enforce the standard and detect when a new service is logging in a non-standard format before it reaches production?
