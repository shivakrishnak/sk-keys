---
id: MSV-064
title: Distributed Logging
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-063, MSV-001
used_by: MSV-065
related: MSV-065, MSV-063, MSV-072, MSV-001, MSV-025, MSV-030
tags:
  - microservices
  - observability
  - deep-dive
  - logging
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 64
permalink: /microservices/distributed-logging/
---

# MSV-064 - Distributed Logging

⚡ TL;DR - Distributed logging in microservices:
aggregate logs from ALL services into a centralized,
searchable store, correlating them with a shared
trace/correlation ID. Without it: debugging a
failed order requires SSHing into 5 different
servers, reading 5 log files, and manually
correlating timestamps. With it: search by
correlation ID in Kibana; see the complete request
journey across all services in one query.
Key components: structured logging (JSON, not
plain text), correlation ID propagation (MDC in
Java), log aggregation (Fluent Bit/Fluentd),
centralized store (Elasticsearch), visualization
(Kibana) = ELK/EFK stack.

| #064 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Cross-Cutting Concerns, What are Microservices | |
| **Used by:** | OpenTelemetry in Microservices | |
| **Related:** | OpenTelemetry in Microservices, Cross-Cutting Concerns, Sidecar Pattern, What are Microservices, Health Check API, Service Resilience Patterns | |

---

### 🔥 The Problem This Solves

**THE MULTI-SERVICE DEBUGGING NIGHTMARE:**
A customer reports: "My order failed 30 minutes
ago." Without distributed logging: developer
SSHs into order-service server (logs are there,
but are plain text, not searchable). Finds a
"call to customer-service failed" error. SSHs
into customer-service server. Finds logs but
CAN'T TELL which log lines correspond to this
specific order (no correlation). Checks payment-
service. Checks inventory-service. Total time:
2 hours, 4 servers, manual timestamp correlation.
With distributed logging: search correlation
ID in Kibana in 30 seconds.

---

### 📘 Textbook Definition

**Distributed Logging** in microservices is the
practice of collecting, aggregating, and centralizing
logs from all service instances into a single
queryable store, with a consistent format and
correlation identifiers that link log entries
across services to the same user request. Key
principles: (1) **Structured logging** - logs
emitted as JSON (not plain text) with consistent
field names (timestamp, level, service, traceId,
correlationId, message); (2) **Correlation ID**
- a unique ID generated at the entry point
(API gateway or first service) and propagated
in HTTP headers (`X-Correlation-Id`, `traceparent`)
through all downstream calls, included in every
log line; (3) **Centralized aggregation** - Fluent
Bit or Fluentd sidecar/DaemonSet reads container
logs from all pods, ships to Elasticsearch;
(4) **Visualization** - Kibana for search and
dashboards. The complete stack: ELK (Elasticsearch,
Logstash, Kibana) or EFK (Elasticsearch, Fluentd,
Kibana) or LOKI stack (Grafana Loki + Promtail
+ Grafana).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Distributed logging: all services log JSON with
a shared request ID. All logs ship to Elasticsearch.
Search by ID in Kibana: see the full request
journey across all services.

**One analogy:**
> Distributed logging is like a flight data recorder
> (black box) for every request. Every aircraft
> (service) records events. After a crash (incident):
you don't read all aircraft logs individually;
> you correlate all flight data recorders by
> flight number (correlation ID). The air traffic
> control database (Elasticsearch) stores all
> recordings. Kibana: the cockpit display that
> shows you the complete flight history for
> flight OR-12345 across all system components.

**One insight:**
The most valuable investment in distributed logging
is not the tool selection (ELK vs Loki) but the
CORRELATION ID discipline. If even one service
in the chain loses the correlation ID (doesn't
propagate it to downstream calls or doesn't
include it in log lines): the chain is broken.
You can only see the journey up to that service.
This is why OpenTelemetry trace propagation
(W3C `traceparent` header) is so valuable: it
standardizes correlation ID propagation across
all languages and frameworks.

---

### 🔩 First Principles Explanation

**THE LOG PIPELINE:**

```
SERVICE -> STDOUT/STDERR (JSON format)
  |
  v
 KUBERNETES POD LOG STORAGE
  /var/log/containers/*.log
  |
  v
 FLUENT BIT (DaemonSet on every K8s node)
  - Reads: /var/log/containers/*.log
  - Parses: JSON fields
  - Enriches: adds pod name, namespace, node name
  - Filters: removes health check spam
  - Ships: to Elasticsearch
  |
  v
 ELASTICSEARCH (cluster)
  - Index: logs-2024-01-15 (one per day)
  - Stores: all log documents with all fields
  - Searchable: by any field
  |
  v
 KIBANA
  - Dashboard: error rate, log volume by service
  - Search: traceId:"abc-123-xyz"
  - Result: all log lines for this request from
    ALL services, in chronological order

CORRELATION ID FLOW:
  API Gateway: receives request
    Generates: X-Correlation-Id: req-abc-123
    Logs: {"traceId":"req-abc-123","msg":"request in"}
    Passes: X-Correlation-Id header to order-service
  
  order-service: receives request
    Reads: X-Correlation-Id header
    Stores: in MDC (Mapped Diagnostic Context)
    All subsequent logs: include traceId=req-abc-123
    Calls: customer-service; passes header
  
  customer-service: same process
  payment-service: same process
  
  Kibana: search traceId:"req-abc-123"
  Result: 47 log entries, 5 services,
          chronological order, complete journey
```

---

### 🧪 Thought Experiment

**DEBUGGING WITH vs WITHOUT DISTRIBUTED LOGGING:**

```
INCIDENT: 5% of orders showing "Payment pending"
  but customer charged; order never fulfilled
  
  WITHOUT DISTRIBUTED LOGGING:
  Step 1: SSH into payment-service server
    grep "CHARGED" /var/log/payment/payment.log
    Finds: payment_id=pay-001 CHARGED at 14:23:01
    But: which order_id? Log doesn't show it.
    Plain text log: no structured fields
  Step 2: SSH into order-service server
    grep "payment" /var/log/order/order.log
    Finds: many matches; no correlation to payment
  Step 3: grep by timestamp range
    Finds: 3 orders at 14:23:xx
    Still not sure which one
  Total time: 2 hours, not conclusive
  
  WITH DISTRIBUTED LOGGING:
  Step 1: Kibana search:
    level:ERROR AND service:payment-service
    AND timestamp:[2024-01-15T14:20 TO 14:25]
    Finds: traceId="req-abc-789" error at 14:23:01
    "Payment charge succeeded but order event
     publish FAILED"
  Step 2: Search traceId:"req-abc-789"
    See: all 23 log lines for this request
    See: order-service: order created
    See: payment-service: charged
    See: payment-service: Kafka publish FAILED
         (Kafka broker timeout)
    See: order-service: never received OrderPaid event
  Root cause: Kafka timeout in payment-service
  Fix: implement Outbox pattern (MSV-054)
  Total time: 5 minutes
```

---

### 🧠 Mental Model / Analogy

> Distributed logging is like airport security
> cameras. Each gate (service) has cameras recording
> all passengers. Without a central system: to find
> where passenger "John Smith" (correlation ID)
> went, you would check every camera manually.
> With a central VMS (Video Management System =
> Elasticsearch): search "John Smith" in all cameras
> simultaneously. The system: shows his complete
> journey through the airport (request journey
> through services) in chronological order. Kibana:
> the security monitor's screen. Fluent Bit: the
> cable connecting all cameras to the VMS.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
All services write logs with a shared request ID.
All logs are collected into one searchable database.
To debug: search the request ID; see all logs
from all services for that request.

**Level 2 - How to implement (junior developer):**
Spring Boot: add MDC (Mapped Diagnostic Context)
filter to set correlation ID from request header.
Log format: Logback with JSON format (logstash-
logback-encoder). Kubernetes: deploy Fluent Bit
as DaemonSet (helm chart available). Elasticsearch:
use Elastic Cloud or self-hosted. Kibana: comes
with Elasticsearch.

**Level 3 - How it works (mid-level engineer):**
Fluent Bit: reads `/var/log/containers/*.log`
(Kubernetes routes all container stdout/stderr
there). Parses JSON. Adds Kubernetes metadata
(pod name, namespace, labels). Enriches with
node hostname. Ships to Elasticsearch over HTTPS.
Index lifecycle management (ILM): auto-delete
logs older than 30 days; optimize storage.

**Level 4 - Operational concerns (senior engineer):**
Log volume at scale: 100 services, 1000 RPS each
= potentially millions of log lines/second. Solutions:
log sampling (only log 10% of INFO; 100% of ERROR),
Fluent Bit buffer (disk buffer to handle Elasticsearch
backpressure), Elasticsearch write tuning (bulk
API, index buffering). Log retention: compliance
requirements (HIPAA: 7 years) vs storage cost
(Elasticsearch: compress older indices, move to
cold tier). Log security: PII in logs -> log
scrubbing (mask email, credit card numbers) in
Fluent Bit filter.

**Level 5 - Mastery (principal engineer):**
Loki vs ELK: Grafana Loki doesn't index log
content (only labels), stores log lines as
compressed chunks. 10x cheaper than Elasticsearch
for the same data volume. Trade-off: only searchable
by LABEL (service name, pod, namespace), not by
content (cannot search "traceId:abc-123" efficiently
unless you add it as a label). Best approach:
Loki for recent logs (1-7 days, cheap), Elasticsearch
for structured search and compliance (30-90 days,
expensive but full-text searchable). OpenTelemetry
Logs (OTEL): emerging standard for log correlation
with traces - log records include trace_id, span_id
natively, enabling automatic log-trace correlation
in Jaeger/Tempo.

---

### ⚙️ How It Works (Mechanism)

```java
// SPRING BOOT: Correlation ID propagation via MDC

// 1. MDC Filter: set correlation ID on every request
@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public class CorrelationIdFilter
        implements Filter {
    // W3C traceparent format: 00-<traceId>-<spanId>-01
    private static final String TRACE_HEADER =
        "traceparent";
    // Fallback for legacy clients:
    private static final String CORRELATION_HEADER =
        "X-Correlation-Id";
    
    @Override
    public void doFilter(ServletRequest req,
            ServletResponse res,
            FilterChain chain)
            throws IOException, ServletException {
        HttpServletRequest request =
            (HttpServletRequest) req;
        
        // Extract trace ID from header (or generate)
        String traceId = request.getHeader(
            TRACE_HEADER);
        if (traceId == null) {
            traceId = request.getHeader(
                CORRELATION_HEADER);
        }
        if (traceId == null) {
            traceId = UUID.randomUUID().toString();
        }
        
        // Set in MDC: Logback includes in EVERY log line
        MDC.put("traceId", traceId);
        MDC.put("service", "order-service");
        
        try {
            chain.doFilter(req, res);
        } finally {
            // Always clean up MDC (thread pool reuse)
            MDC.clear();
        }
    }
}

// 2. HTTP client: propagate correlation ID downstream
// (when calling customer-service)
@Bean
public RestTemplate restTemplate() {
    RestTemplate rt = new RestTemplate();
    rt.getInterceptors().add(
        (request, body, execution) -> {
            String traceId = MDC.get("traceId");
            if (traceId != null) {
                // Propagate to downstream service
                request.getHeaders().set(
                    "X-Correlation-Id", traceId);
            }
            return execution.execute(request, body);
        });
    return rt;
}
```

```xml
<!-- logback-spring.xml: JSON structured logging -->
<configuration>
    <appender name="JSON_CONSOLE"
              class="ch.qos.logback.core.ConsoleAppender">
        <encoder class="net.logstash.logback.encoder
                        .LogstashEncoder">
            <!-- All MDC fields included automatically -->
            <!-- Output format: one JSON object per line -->
            <!--
            {
              "timestamp": "2024-01-15T14:23:01.234Z",
              "level": "ERROR",
              "service": "order-service",
              "traceId": "req-abc-789",
              "message": "Payment event publish failed",
              "logger": "c.e.OrderService",
              "exception": "KafkaTimeoutException..."
            }
            -->
        </encoder>
    </appender>
    <root level="INFO">
        <appender-ref ref="JSON_CONSOLE" />
    </root>
</configuration>
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
DISTRIBUTED LOGGING STACK IN KUBERNETES:

  CLUSTER (one Fluent Bit per node via DaemonSet)
  |
  +-- Node 1
  |   +-- order-service pod: logs JSON to stdout
  |   +-- Fluent Bit: reads /var/log/containers/
  |       -> parses JSON, adds k8s metadata
  |       -> ships to Elasticsearch
  |
  +-- Node 2
  |   +-- customer-service pod: logs JSON to stdout
  |   +-- Fluent Bit: same pipeline
  |
  ELASTICSEARCH CLUSTER
  - Indices: logs-2024-01-15, logs-2024-01-16...
  - Retention: 30 days (ILM policy)
  - Shards: 3 primary, 1 replica (HA)
  |
  KIBANA
  - Index pattern: logs-*
  - Discovery: search traceId:"req-abc-789"
  - Dashboard: error rate by service per minute
  - Alert: ERROR count > 100/min -> PagerDuty
  
  DEPLOYMENT:
  helm repo add fluent https://fluent.github.io/helm-charts
  helm install fluent-bit fluent/fluent-bit \
    --set backend.type=es \
    --set backend.es.host=elasticsearch.monitoring
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: plain text vs structured JSON logging**

```java
// BAD: plain text logging - impossible to query
log.info("Processing order for user " + userId +
    " amount: " + amount);
// Log output:
// 2024-01-15 14:23:01 INFO  Processing order
// for user U-123 amount: 99.99

// To find: all orders over $100 in last hour
// Kibana: cannot do it (not structured fields)
// grep: regex nightmare, no index
```

```java
// GOOD: structured logging with MDC
// Logback + logstash-logback-encoder
log.info("Order processing started",
    StructuredArguments.keyValue("orderId", orderId),
    StructuredArguments.keyValue("userId", userId),
    StructuredArguments.keyValue("amount", amount),
    StructuredArguments.keyValue("currency", "USD")
);
// MDC already has: traceId, service name
// JSON output:
// {"timestamp":"...","level":"INFO",
//  "service":"order-service","traceId":"req-abc",
//  "orderId":"ord-001","userId":"U-123",
//  "amount":99.99,"currency":"USD",
//  "message":"Order processing started"}
// Kibana: amount:>100 AND timestamp:[now-1h TO now]
// Instantly finds all large orders last hour
```

---

### ⚖️ Comparison Table

| Stack | Indexing | Cost | Search | Best For |
|---|---|---|---|---|
| **ELK** | Full-text | High | Any field | Compliance, full-text search |
| **EFK** | Full-text | High | Any field | Same as ELK, lighter Logstash |
| **Loki** | Labels only | Low | Label-based | Cost-sensitive, recent logs |
| **CloudWatch** | Full-text | Medium | Limited | AWS-native, no ops overhead |
| **Datadog** | Full-text | Very high | Any field | Managed, APM + logs unified |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Correlation ID is automatically propagated by frameworks | Most frameworks do NOT automatically propagate correlation IDs between services. Spring Cloud Sleuth (deprecated) and OpenTelemetry Java agent DO propagate trace context automatically. Without these: developers must manually add header propagation interceptors to every HTTP client (RestTemplate, WebClient, Feign) and every message consumer (Kafka). Forgetting one service in the chain: breaks the correlation chain for all requests going through it. |
| Distributed logging replaces distributed tracing | They are complementary. Distributed logging: "what happened" (events, errors, data). Distributed tracing (OpenTelemetry/Jaeger): "how long each step took" (spans, latencies, dependencies). Use logging for: business event audit trail, error details, debugging specific issues. Use tracing for: performance debugging, identifying bottlenecks, understanding service dependencies under load. Both use the same correlation/trace ID. |
| All logs should be at DEBUG level to maximize observability | DEBUG logging at scale creates: massive storage costs, high log I/O overhead (CPU-intensive JSON serialization per log line), and signal-to-noise ratio problems (5 million DEBUG lines = cannot find the 3 ERROR lines that matter). Production standard: INFO for business events, WARN for degraded but functional, ERROR for failures. DEBUG: only enabled temporarily per-service for debugging (can be done with dynamic log levels in Spring Boot Actuator: `PATCH /actuator/loggers/com.example.OrderService` with `level: DEBUG`). |

---

### 🚨 Failure Modes & Diagnosis

**Correlation ID chain broken: cannot trace request across services**

**Symptom:**
Customer reports payment charged but no order
created. Developer searches Kibana for correlation
ID from API gateway logs. Finds: order-service
logs for the request, payment-service has NO
logs with this correlation ID. Cannot determine
what payment-service did with this request.

**Root Cause:**
payment-service: RestTemplate call does not
propagate `X-Correlation-Id` header. payment-
service logs the request but generates a NEW
correlation ID (UUID.randomUUID()) instead of
using the one from the incoming header. Logs
exist but are not findable by the original
correlation ID.

**Diagnosis:**
```bash
# Check if payment-service propagates the header
kubectl exec -it payment-service-pod -- curl -v \
  -H "X-Correlation-Id: test-123" \
  http://localhost:8080/payments

# Check Kibana: search for test-123 in payment-service
# If not found: header not propagated to MDC or
# not included in log output

# Check MDC setup:
# Is CorrelationIdFilter registered in payment-service?
# Does Logback include %X{traceId} in pattern?
```

**Fix:**
1. Add `CorrelationIdFilter` to payment-service.
2. Add RestTemplate interceptor that propagates
   the header to all downstream calls.
3. OR: migrate to OpenTelemetry Java agent which
   handles propagation automatically.

---

### 🔗 Related Keywords

**Extends this with tracing:**
- `OpenTelemetry in Microservices` - adds distributed
  tracing and metrics alongside logging; uses
  the same trace/correlation ID

**Cross-cutting concern context:**
- `Cross-Cutting Concerns` - distributed logging
  is an observability cross-cutting concern

**Infrastructure that collects logs:**
- `Sidecar Pattern` - Fluent Bit as a log
  collection sidecar

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ REQUIREMENTS │ Structured logs (JSON), correlation ID,   │
│              │ ID propagation, centralized store         │
├──────────────┼───────────────────────────────────────────┤
│ STACK        │ ELK (full-text), Loki (cheap, label-based) │
│              │ Fluent Bit DaemonSet -> Elasticsearch/Loki │
├──────────────┼───────────────────────────────────────────┤
│ JAVA TOOLS   │ MDC for correlation ID; logstash-logback  │
│              │ -encoder for JSON; OTEL agent for auto    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "JSON logs + correlation ID propagation    │
│              │  + Fluent Bit + Elasticsearch + Kibana"    │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Structured JSON logging + correlation ID in
   every log line + ID propagated in HTTP headers
   across ALL services = distributed logging.
2. ELK stack: Fluent Bit (collect) ->
   Elasticsearch (store/index) -> Kibana (search).
3. MDC (Mapped Diagnostic Context): Java mechanism
   to include correlation ID in all log lines
   automatically without passing it as a method
   parameter everywhere.

**Interview one-liner:**
"Distributed logging: all microservices emit JSON
logs to stdout; Fluent Bit (DaemonSet) collects
them from all pods and ships to Elasticsearch;
Kibana for search. Key: correlation ID (from
X-Correlation-Id or W3C traceparent header) stored
in MDC, included in EVERY log line. Search
traceId in Kibana: see complete request journey
across all services. Java: MDC filter sets ID
from incoming header; RestTemplate interceptor
propagates it to downstream calls. Better:
OpenTelemetry Java agent handles all of this
automatically with zero code change."

---

### 💡 The Surprising Truth

The biggest distributed logging failure is not
technical - it's PII in logs. Teams add logging
"for debugging" and include customer email, phone
number, or even credit card numbers in log messages.
These logs flow to Elasticsearch, where they sit
for 30-90 days, accessible to all engineers.
GDPR and PCI-DSS: severe violations. The fix:
train engineers on what not to log, implement
log scrubbing in Fluent Bit (regex filter to
mask email patterns, credit card patterns), and
add a pre-commit hook or CI check that scans
for common PII patterns in log statements. Log
scrubbing at the collection layer (Fluent Bit)
is the most reliable: catches PII even if a
developer accidentally adds it.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **IMPLEMENT** Set up distributed logging in a
   3-service Spring Boot system: JSON logging with
   logstash-logback-encoder, MDC correlation ID
   filter, RestTemplate interceptor for propagation,
   Fluent Bit DaemonSet Helm chart, Elasticsearch
   and Kibana.
2. **QUERY** Given an incident (customer reports
   failed payment at 14:23 with correlation ID
   X), write the Kibana KQL query to find all
   logs for this request across all services,
   ordered by timestamp.
3. **OTEL** Configure OpenTelemetry Java agent
   for automatic trace propagation: startup args,
   OTEL collector endpoint, service name. Verify:
   trace IDs appear in Kibana logs across services.
4. **LOKI** Explain when to choose Loki over
   Elasticsearch: cost comparison, searchability
   trade-offs, what you CAN and CANNOT do with
   label-based Loki search.
5. **PII** Design a Fluent Bit filter configuration
   that: masks email addresses in log messages
   (replace with [REDACTED-EMAIL]), removes logs
   from `/actuator/health` endpoint (health check
   spam), adds service version label to all log
   documents.

---

### 🧠 Think About This Before We Continue

**Q1.** You have 50 microservices generating 2
million log lines per minute. Elasticsearch storage
cost is becoming prohibitive. Design a tiered
logging architecture: what logs go to ELK (expensive,
full-text search), what goes to Loki (cheap, label-
based), what gets dropped at the Fluent Bit level.
Define the routing rules in Fluent Bit configuration.

**Q2.** A security audit requires: no customer
email or phone number should appear in any log.
You have 50 services logging millions of lines
daily; manually reviewing all log statements is
impractical. Design an automated detection system:
what tools detect PII in logs, how do you enforce
it in CI/CD (pre-commit hooks, static analysis),
and how do you handle PII already in historical
logs (GDPR right to erasure)?

**Q3.** Your application team says: "Our correlation
IDs work within our service, but we lose the trace
when calling the third-party payment processor's
API." What can you do to maintain request correlation
even when calling external APIs that don't support
your correlation ID headers? How do you correlate
your internal logs with any error responses from
the external API?