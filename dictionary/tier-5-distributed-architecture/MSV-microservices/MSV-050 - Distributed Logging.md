---
layout: default
title: "Distributed Logging"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 50
permalink: /microservices/distributed-logging/
id: MSV-050
category: Microservices
difficulty: ★★★
depends_on: Cross-Cutting Concerns, Correlation ID (Microservices), Observability & SRE
used_by: OpenTelemetry (Microservices), Correlation ID (Microservices), Chaos Engineering
related: Correlation ID (Microservices), OpenTelemetry (Microservices), Centralized Log Management (ELK)
tags:
  - microservices
  - observability
  - logging
  - operations
  - deep-dive
status: complete
---

# MSV-050 - Distributed Logging

⚡ TL;DR - Distributed logging aggregates structured logs from all microservices into a centralised system, correlated by a common request ID, making distributed system behaviour observable and debuggable.

| #665            | Category: Microservices                                                                         | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Cross-Cutting Concerns, Correlation ID (Microservices), Observability & SRE                     |                 |
| **Used by:**    | OpenTelemetry (Microservices), Correlation ID (Microservices), Chaos Engineering                |                 |
| **Related:**    | Correlation ID (Microservices), OpenTelemetry (Microservices), Centralized Log Management (ELK) |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A user reports: "My order #4521 failed." Your system has 8 microservices. Order failure could be in: Order Service, Inventory Service, Payment Service, Notification Service. Each service logs to its own file on its own server. To investigate, you SSH into 8 servers, find 8 log files, grep for the order ID - but each service uses a different log format. Some log the order ID as `orderId`, some as `order_id`, some as `id`. Some logs have timestamps in UTC, some in local timezone. The error occurred 2 hours ago; some log files have been rotated. You spend 90 minutes gathering logs and another 45 minutes piecing together what happened in what order. The customer is still waiting.

**THE BREAKING POINT:**
Distributed systems fail in distributed ways. Without a unified, correlated, structured log view, debugging distributed failures is exponentially harder than debugging monoliths. Each additional service multiplies the investigation complexity.

**THE INVENTION MOMENT:**
Distributed logging - centralising structured logs from all services, correlated by a common request identifier - was the observability foundation that made distributed systems debuggable.


**EVOLUTION:**
Distributed logging evolved from per-host log files (1990s) to centralised log aggregation as distributed systems multiplied the number of hosts. Splunk (2004) introduced centralised search. The ELK Stack (Elasticsearch, Logstash, Kibana, 2010-2013) made centralised aggregation open-source and accessible. Structured logging (logs as JSON rather than unstructured text) became standard with Logback/Log4j2 in Java and Winston in Node.js. OpenTelemetry Logs (2021) standardised log format across platforms. The discipline evolved from 'grep through log files on each server' to 'centralised, structured, correlated, searchable logs across all services.'
---

### 📘 Textbook Definition

**Distributed logging** in microservices is the practice of emitting _structured logs_ (JSON format with standardised fields) from all services, forwarding them to a _centralised log aggregation system_ (ELK stack, Loki/Grafana, Splunk, CloudWatch), and correlating log entries across services using a _correlation ID_ that propagates through all service calls in a request chain. This enables engineers to search and reconstruct the complete narrative of any distributed request - across any number of services - as a single chronological log stream.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Every service writes structured logs with a shared request ID; all logs go to one place so you can see the full story of any request, regardless of which services it touched.

**One analogy:**

> A flight data recorder (black box) in an aircraft records all systems' readings with timestamps. After an incident, investigators reconstruct exactly what happened in sequence. Distributed logging is the "black box" for your microservices system - all services record to a shared timeline, allowing full incident reconstruction.

**One insight:**
The correlation ID is what transforms scattered logs into a coherent story. Without it, you have data; with it, you have narrative.

---

### 🔩 First Principles Explanation

**THE THREE REQUIREMENTS:**

**1. Structured logging (machine-parseable):**

```json
// ✅ Structured (queryable, filterable)
{
  "timestamp": "2026-05-06T10:00:01.234Z",
  "level": "INFO",
  "service": "order-service",
  "version": "2.1.4",
  "correlationId": "abc-123-xyz",
  "traceId": "f1a2b3c4d5e6f7a8",
  "orderId": "order-456",
  "message": "Order created successfully",
  "durationMs": 45
}

// ❌ Unstructured (only grep, no query)
[2026-05-06 10:00:01] INFO - Order 456 created OK (45ms)
```

**2. Centralised aggregation:**
All logs → log aggregation pipeline → searchable store

- Log shipper: Fluentd, Logstash, Filebeat, Vector
- Storage: Elasticsearch, Loki, CloudWatch Logs, Splunk
- Query: Kibana (Elasticsearch), Grafana (Loki), Splunk UI

**3. Correlation ID propagation:**
Every inbound HTTP request either has an `X-Correlation-Id` header (from upstream caller or client) or gets one assigned at the API gateway. Every service:

- Extracts the correlation ID from the incoming request
- Puts it in the thread-local context (MDC in Java, AsyncLocalStorage in Node.js)
- Includes it in every log line
- Forwards it in every outgoing HTTP request header

**LOG LEVELS - WHEN TO USE EACH:**

| Level | When to Use                                           | Production Volume |
| ----- | ----------------------------------------------------- | ----------------- |
| ERROR | Service cannot proceed; action required               | Low               |
| WARN  | Unexpected but recoverable; worth monitoring          | Low-medium        |
| INFO  | Key business events (order created, payment received) | Low               |
| DEBUG | Detailed flow tracing for debugging                   | Off in production |
| TRACE | Very fine-grained; SQL queries, wire bytes            | Off always        |

**THE TRADE-OFFS:**
**Gain:** Full request narrative across all services; instant root cause diagnosis; correlation with traces; audit trail for business events.
**Cost:** Log storage costs at scale (logs are verbose); log aggregation pipeline is critical infrastructure; careless logging leaks PII or secrets; high-volume logging degrades service performance.

---

### 🧪 Thought Experiment

**SETUP:**
User places an order. The flow crosses: API Gateway → Order Service → Inventory Service → Payment Service → Notification Service. Payment fails.

**WITHOUT DISTRIBUTED LOGGING:**
5 separate log files. You know payment failed (from payment service log). But why? Was the order valid? Was inventory available? Was the payment declined or was there a network error? You spend 2 hours correlating 5 log files.

**WITH DISTRIBUTED LOGGING:**
Search: `correlationId: "abc-123"` in Kibana. One query returns all log entries across all 5 services, sorted by timestamp:

```
10:00:00.100 [api-gateway]       Request received. correlationId=abc-123
10:00:00.150 [order-service]     Order validated. orderId=456
10:00:00.250 [inventory-service] Stock reserved. productId=789 qty=2
10:00:00.350 [payment-service]   Charge attempt. cardId=*4242
10:00:00.450 [payment-service]   ERROR: Charge declined. code=INSUFFICIENT_FUNDS
10:00:00.460 [order-service]     Saga: compensating. orderId=456
10:00:00.500 [inventory-service] Stock released. productId=789 qty=2
10:00:00.510 [notification-svc]  Sending failure email. userId=user-1
```

**THE INSIGHT:**
Full diagnosis in 10 seconds instead of 2 hours. Correlation ID is the single thread that connects 8 log entries across 5 services into one coherent narrative.

---

### 🧠 Mental Model / Analogy

> Distributed logging is like air traffic control radar. Each aircraft (service) broadcasts its position (logs) continuously. ATC (log aggregation) collects all broadcasts into one unified display. Controllers (engineers) can track any specific flight (request) across its entire journey - regardless of how many sectors (services) it passed through. Without radar, each sector keeps its own paper records; correlating a flight's journey requires hours of manual record reconciliation.

- "Aircraft broadcasts" → service log emissions
- "Air traffic control radar" → centralised log aggregation
- "Specific flight ID" → correlation ID
- "Tracking across sectors" → querying by correlationId across all services
- "Paper records per sector" → siloed per-service log files

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
All services write their activity logs in the same format, with the same request ID, to the same central place. Engineers can search by the request ID to see everything that happened for a specific user action, across all services, in time order.

**Level 2 - How to implement it (junior developer):**
Configure structured JSON logging (Logstash JSON encoder for Java, winston/pino for Node.js). Add MDC filter for correlation ID injection. Configure log shipper (Filebeat/Fluentd) to forward to Elasticsearch. Create Kibana index pattern. Train team on Kibana query syntax. Add log level guidelines to team docs.

**Level 3 - How to manage it at scale (mid-level engineer):**
At 10k log lines/sec, you need: (1) log sampling for DEBUG (off in production); (2) log aggregation pipeline capacity planning (Elasticsearch cluster sizing); (3) log retention policy (7 days hot, 30 days warm, 90 days cold); (4) PII scrubbing in log pipeline (Logstash filter to mask credit card numbers, SSNs); (5) log-based alerting (Elasticsearch Watcher: alert if ERROR rate > 10/min); (6) index lifecycle management (ILM) to rotate/delete old indices automatically.

**Level 4 - Distributed logging vs distributed tracing (senior/staff):**
Logs and traces are complementary, not alternatives. **Logs** are textual records of discrete events - best for: "What happened? What was the data at that moment? What was the error?" **Traces** are structured spans measuring operations - best for: "How long did each step take? Where is the latency? Which service is slow?" A mature observability stack has both: OpenTelemetry injects `traceId` and `spanId` into the log context (MDC), creating a bridge. You can go from a log entry to its parent trace span with one click. This unified observability (logs + traces + metrics) is the "three pillars of observability" paradigm. At this level, distributed logging is not just a debugging tool - it is the primary audit trail for business events (payment received, fraud detected, consent granted) and a compliance requirement in regulated industries.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│          Distributed Logging - Full Pipeline            │
└─────────────────────────────────────────────────────────┘

Services emit structured logs:
  order-service  → stdout (JSON)
  payment-service → stdout (JSON)
  inventory-service → stdout (JSON)
        │
        ▼
Log Shippers (per node/pod):
  Fluentd / Filebeat
  - Collects stdout from all containers
  - Adds Kubernetes metadata (pod, namespace, node)
  - Forwards to Elasticsearch
        │
        ▼
Elasticsearch cluster:
  - Indexes logs for full-text search
  - Retains for configured duration
  - Index per day (logstash-2026.05.06)
        │
        ▼
Kibana:
  - Search: correlationId: "abc-123"
  - Dashboard: error rate per service
  - Alert: ERROR count > threshold
        │
        ▼
On-call engineer sees:
  Complete request narrative across all services
  in chronological order, within seconds
```

**Correlation ID propagation chain:**

```
Client → API Gateway
  Gateway assigns X-Correlation-Id: abc-123
  Forwards to Order Service

Order Service:
  Extracts abc-123 from header
  MDC.put("correlationId", "abc-123")
  Logs: {..., correlationId: "abc-123", ...}
  Calls Inventory Service:
    restTemplate.exchange(..., headers with X-Correlation-Id: abc-123)

Inventory Service:
  Extracts abc-123 from header
  Logs: {..., correlationId: "abc-123", ...}
  → Same correlation ID in Elasticsearch
```

---

### 🔄 The Complete Picture - ELK Stack Setup

```yaml
# Kubernetes logging stack (simplified)
# Fluentd DaemonSet on every node
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
spec:
  selector:
    matchLabels:
      app: fluentd
  template:
    spec:
      containers:
        - name: fluentd
          image: fluent/fluentd-kubernetes-daemonset:latest
          env:
            - name: FLUENT_ELASTICSEARCH_HOST
              value: "elasticsearch-service"
          volumeMounts:
            - name: varlog
              mountPath: /var/log
```

---

### 💻 Code Example

**Example 1 - Structured logging setup (Spring Boot):**

```xml
<!-- pom.xml: Logstash JSON encoder -->
<dependency>
  <groupId>net.logstash.logback</groupId>
  <artifactId>logstash-logback-encoder</artifactId>
  <version>7.4</version>
</dependency>
```

```xml
<!-- logback-spring.xml -->
<configuration>
  <springProperty name="SERVICE_NAME"
    source="spring.application.name"/>
  <appender name="JSON"
    class="ch.qos.logback.core.ConsoleAppender">
    <encoder
      class="net.logstash.logback.encoder.LogstashEncoder">
      <customFields>
        {"service":"${SERVICE_NAME}"}
      </customFields>
      <includeMdcKeyName>correlationId</includeMdcKeyName>
      <includeMdcKeyName>traceId</includeMdcKeyName>
      <includeMdcKeyName>spanId</includeMdcKeyName>
      <includeMdcKeyName>orderId</includeMdcKeyName>
    </encoder>
  </appender>
  <root level="INFO">
    <appender-ref ref="JSON"/>
  </root>
</configuration>
```

**Example 2 - Correlation ID filter:**

```java
@Component
@Order(1)
public class CorrelationIdFilter extends OncePerRequestFilter {

  private static final String HEADER = "X-Correlation-Id";

  @Override
  protected void doFilterInternal(
      HttpServletRequest req, HttpServletResponse res,
      FilterChain chain) throws IOException, ServletException {

    String correlationId = Optional
      .ofNullable(req.getHeader(HEADER))
      .filter(s -> !s.isBlank())
      .orElse(UUID.randomUUID().toString());

    MDC.put("correlationId", correlationId);
    res.setHeader(HEADER, correlationId);

    try {
      chain.doFilter(req, res);
    } finally {
      MDC.remove("correlationId");
    }
  }
}
```

**Example 3 - Correlation ID forwarding in HTTP client:**

```java
// Spring RestTemplate interceptor - propagates correlation ID
@Bean
public RestTemplate restTemplate() {
  RestTemplate template = new RestTemplate();
  template.getInterceptors().add((req, body, execution) -> {
    String correlationId = MDC.get("correlationId");
    if (correlationId != null) {
      req.getHeaders().set("X-Correlation-Id", correlationId);
    }
    return execution.execute(req, body);
  });
  return template;
}
```

**Example 4 - PII-safe logging:**

```java
// ❌ NEVER log sensitive data
log.info("Processing payment: card={}, cvv={}",
         creditCardNumber, cvv);

// ✅ Log business identifiers only
log.info("Processing payment: paymentId={}, orderId={}",
         payment.getId(), order.getId());
```

---

### ⚖️ Comparison Table

| Approach                                 | Searchable     | Cross-Service | Real-Time      | Cost               |
| ---------------------------------------- | -------------- | ------------- | -------------- | ------------------ |
| **Centralised structured logging (ELK)** | Yes            | Yes           | Near real-time | Medium             |
| Per-service log files                    | No (grep only) | No            | No             | Low                |
| Cloud logging (CloudWatch, GCP Logging)  | Yes            | Yes           | Near real-time | Scales with volume |
| Distributed tracing only (Jaeger)        | No text search | Yes           | Yes            | Medium             |
| Logs + Traces (OpenTelemetry)            | Yes            | Yes           | Yes            | High               |

**How to choose:** Centralised ELK/Loki for most production systems. Cloud-native logging (CloudWatch/GCP) for cloud-native shops. OpenTelemetry for full observability (logs + traces + metrics) in complex systems.

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                               |
| ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| More logging is always better                               | Excessive logging degrades performance and inflates storage costs; log purposefully                                   |
| Logging and tracing are interchangeable                     | Logs are discrete events (what happened); traces are time spans (how long); both serve different debugging needs      |
| Centralised logging eliminates the need for local debugging | Both are needed; centralised logging for production incidents, local dev logging for development                      |
| DEBUG logs should always be enabled                         | DEBUG in production creates severe performance and storage issues; use dynamic log level changes for ad-hoc debugging |
| Log format doesn't matter                                   | Inconsistent formats are as bad as no centralised logging; the query system needs consistent field names              |

---

### 🚨 Failure Modes & Diagnosis

**Log Pipeline Backlog - Logs Not Appearing in Kibana**

**Symptom:** Logs missing in Kibana for recent time window; on-call can't find recent log entries.

**Root Cause:** Elasticsearch ingestion slow (disk I/O, indexing bottleneck); Fluentd/Filebeat buffer overflow; network congestion between shippers and Elasticsearch.

**Diagnostic Command:**

```bash
# Check Fluentd buffer status
kubectl exec -it daemonset/fluentd -- \
  fluent-cat --port 24224 --host localhost \
  debug.test '{"message":"test"}'

# Check Elasticsearch index queue
curl http://elasticsearch:9200/_cat/thread_pool/write?v
# Look for "queue" and "rejected" columns
```

**Fix:** Scale Elasticsearch; increase indexing thread pool; reduce log volume temporarily by raising log level.

---

**PII in Production Logs**

**Symptom:** Audit finds customer email addresses, credit card numbers, or SSNs in production Elasticsearch.

**Root Cause:** Developer accidentally logged sensitive data (full request body, user object).

**Diagnostic Command:**

```bash
# Search for potential PII patterns in recent logs
curl -XGET 'elasticsearch:9200/logstash-*/_search' \
  -H 'Content-Type: application/json' \
  -d '{"query":{"regexp":{"message":"[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{4}"}}}'
```

**Fix:** Immediately restrict access to affected indices; add Logstash filter to scrub PII pattern before re-indexing; identify and fix the logging code.

**Prevention:** Code review checklist for logging PRs; automated test that checks log output doesn't contain PII patterns; Logstash PII scrubbing filter as defence-in-depth.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Cross-Cutting Concerns` - distributed logging is a canonical cross-cutting concern
- `Correlation ID (Microservices)` - the mechanism that makes distributed logs coherent
- `Observability & SRE` - the broader context of system observability

**Builds On This (learn these next):**

- `OpenTelemetry (Microservices)` - unified logs + traces + metrics with W3C trace context
- `Chaos Engineering` - uses log analysis to understand failure modes
- `Correlation ID (Microservices)` - the key field that ties distributed logs together

**Alternatives / Comparisons:**

- `Distributed Tracing (Jaeger/Zipkin)` - complements logging; focuses on latency/spans not events
- `Metrics (Prometheus)` - quantitative aggregate data vs. log's per-event narrative
- `ELK Stack` - the canonical distributed logging implementation (Elasticsearch, Logstash, Kibana)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Structured logs from all services,        │
│              │ correlated by request ID, in one place    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Distributed failures invisible without    │
│ SOLVES       │ unified log view across services          │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Correlation ID converts scattered logs    │
│              │ into a complete request narrative         │
├──────────────┼───────────────────────────────────────────┤
│ STACK        │ Services (JSON logs) → Fluentd/Filebeat   │
│              │ → Elasticsearch → Kibana                  │
├──────────────┼───────────────────────────────────────────┤
│ NEVER LOG    │ Passwords, card numbers, SSNs, tokens,    │
│              │ PII (name, email, DOB)                    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "One correlation ID; one place; full story"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Correlation ID → OpenTelemetry →          │
│              │ Three Pillars of Observability            │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
A log line is only useful if it can be found. A log line in a format that can't be indexed, or lacking a correlation ID linking it to other log lines, might as well not exist. The discipline of structured logging (consistent field names, consistent formats, correlation IDs in every log line) is not about aesthetics - it is about making log lines findable in under 60 seconds during a production incident.

**Where else this pattern appears:**
- **Database slow query logs:** A database's slow query log is structured logging applied to query execution - consistent records of events that can be analysed centrally to find performance issues.
- **Web server access logs:** Apache/nginx access logs in combined format are an early form of structured logging - consistent fields (IP, method, URL, status, time) enabling programmatic analysis.
- **Security audit logs:** An immutable audit log with consistent fields (who, what, when, where) is structured distributed logging applied to security compliance requirements.

---

### 💡 The Surprising Truth

The correlation ID, which seems like a simple string to thread through all services, is one of the hardest things to implement correctly in a distributed system. Services receive the correlation ID from HTTP headers, store it in thread-local storage, pass it to async threads via context propagation, include it in Kafka message headers, reconstruct it when consuming from Kafka, and propagate it to all downstream calls. Every step is an opportunity to lose it. Teams that carefully implement correlation ID propagation in synchronous HTTP calls frequently find that their Kafka consumers don't propagate it at all, breaking the trace at every async boundary.
---

### 🧠 Think About This Before We Continue

**Q1.** Your 15-service microservices system has distributed logging set up with ELK. An engineer reports: "Kibana is returning 0 results for `correlationId: abc-123` but I can see the order was created." List 5 possible root causes in order of likelihood and how you would diagnose each.

*Hint:* Think about 5 root causes for missing correlation ID results in Kibana: (1) service doesn't propagate the correlation ID header to the next service in the chain (omission in the HTTP client interceptor); (2) different field names across services (some use `correlationId`, others `requestId` or `traceId` - Kibana search finds only the exact field name queried); (3) log aggregation lag (logs from 2 services haven't been indexed yet - check most recent log timestamp per service); (4) log format mismatch (service logs correlation ID as a nested JSON field, not top-level, making it not directly searchable by Kibana); (5) log shipping failure (Filebeat on that service's host is down).

**Q2.** Your service processes 50,000 requests/sec at peak. Each request generates 10 log lines. At DEBUG level, each request generates 100 log lines. Calculate the log volume difference between INFO and DEBUG. Design a log level strategy that lets you get DEBUG-level detail for specific user sessions or request IDs without enabling DEBUG globally - and without redeploying the service.

*Hint:* Think about the log volume difference: INFO = 50,000 req/s * 10 lines = 500,000 lines/s. DEBUG = 50,000 * 100 = 5,000,000 lines/s (10x more). At 1KB/line: INFO = 500 MB/s, DEBUG = 5 GB/s. For 7 days: DEBUG = ~3 PB. Explore whether Spring Boot's `/actuator/loggers` endpoint (allows runtime log level changes per class or package without restart), combined with a feature-flag-based log sampling (enable DEBUG only for requests matching a specific user ID or session ID header), provides targeted debug visibility without the 10x cost.

**Q3 (Design Trade-off):** Your ELK log pipeline processes 500,000 lines/second. Logstash is the bottleneck, taking 2 seconds to process each batch. During incidents, engineers need log results within 5 seconds. Design the pipeline architecture that achieves sub-5-second log availability without replacing ELK.

*Hint:* Think about what Logstash processing overhead includes: parsing unstructured log text (regex patterns), field extraction, and enrichment. If logs are already structured JSON, Logstash processing is minimal (passthrough routing). Explore whether (a) moving to structured JSON logging eliminates Logstash parsing overhead entirely, (b) Filebeat's direct Elasticsearch output (bypassing Logstash for structured logs while keeping Logstash for legacy unstructured logs), or (c) Kafka as a buffer between services and Logstash decouples log emission latency from Logstash processing latency so engineers see logs in Kafka immediately even if Logstash is behind.
