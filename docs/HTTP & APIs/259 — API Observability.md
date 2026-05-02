---
layout: default
title: "API Observability"
parent: "HTTP & APIs"
nav_order: 259
permalink: /http-apis/api-observability/
number: "0259"
category: HTTP & APIs
difficulty: ★★★
depends_on: REST, HTTP, Observability, Distributed Tracing
used_by: API Operations, SRE, Platform Engineering
related: Observability, Distributed Tracing, API Rate Limiting, SLOs
tags:
  - api-observability
  - monitoring
  - tracing
  - sre
  - advanced
---

# 259 — API Observability

⚡ TL;DR — API observability is the ability to understand the internal state of an API from its external outputs — using the three pillars (metrics, logs, traces) to answer "why is the API misbehaving?" not just "is the API up?"; specifically: tracking per-endpoint error rates/latencies/throughput, recording structured request/response logs, and using distributed traces to follow a request through all microservices it touches.

| #259 | Category: HTTP & APIs | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | REST, HTTP, Observability, Distributed Tracing | |
| **Used by:** | API Operations, SRE, Platform Engineering | |
| **Related:** | Observability, Distributed Tracing, API Rate Limiting, SLOs | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
`POST /payments` starts returning errors at 3:47 AM. On-call engineer gets paged.
They check: is the service up? Yes. Logs: 500 errors for payment requests. They
can see requests are failing but have no idea why. Was it the database? The payment
provider? A timeout? A bad deployment? Which users are affected? What percentage
of payments are failing? How long has this been happening? Without API observability:
30 minutes of manual log grep, no clear answer, escalation to database team, payment
provider team, SRE team — all hands debug a production incident with no visibility.

---

### 📘 Textbook Definition

**API Observability** is the property of an API system that allows its internal state
to be understood from its external outputs at any point in time. Built on three pillars:
(1) **Metrics**: quantitative measurements (request count, error rate, latency
percentiles, throughput) tracked over time per endpoint, per consumer, per status code —
enabling SLO alerting and capacity planning. (2) **Logs**: structured records of
individual API requests/responses with requestId, userId, endpoint, status, latency,
relevant context — enabling post-incident investigation of what happened.
(3) **Traces**: distributed, cross-service request flow tracks showing which services
a request touched, where time was spent, and where errors occurred — enabling
microservice-level root cause analysis. Together called the "Three Pillars" (coined
by Peter Bourgon, 2017). In Spring Boot: Micrometer (metrics), Logback/structured JSON (logs),
Micrometer Tracing / OpenTelemetry (traces).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
API observability means being able to answer "what is wrong and why?" from your
API's metrics, logs, and traces — not just "is it up?"

**One analogy:**
> API observability is like an aircraft's flight instruments vs. a window.
> A pilot looking out the window can see: is it cloudy? Are we near land?
> But they can't see: airspeed, altitude, engine temperature, fuel remaining, heading.
> Instruments (observability) give the complete internal picture.
> An API "working" (HTTP 200) doesn't tell you: latency is 4× normal, error rate spiking,
> database connection pool 95% full. Only instruments reveal the full picture.

**One insight:**
The three pillars are complementary — each answers a different question:
- Metrics answer "how bad is it?" (5% error rate, p99 latency = 3s)
- Logs answer "what exactly happened?" (this specific request failed for this reason)
- Traces answer "where did it go wrong?" (slow in the payment-service, specifically in the DB call to `payments` table)

---

### 🔩 First Principles Explanation

**THE THREE PILLARS IN DETAIL:**

```
PILLAR 1 — METRICS:
  What: numeric time-series data aggregated over time windows
  
  Key API metrics:
  - api_requests_total{endpoint, method, status, consumer}  ← request count
  - api_request_duration_seconds{endpoint, quantile}        ← latency percentiles
  - api_errors_total{endpoint, error_code}                  ← error rate
  - api_active_connections                                  ← concurrent connections
  
  SLO alerts:
  - error_rate > 1% for 5 minutes → page on-call
  - p99_latency > 2000ms for 3 minutes → page on-call
  
  Tools: Prometheus → Grafana, Datadog, New Relic

PILLAR 2 — LOGS:
  What: discrete event records for each operation
  
  Structured log (JSON, NOT plain text):
  {
    "timestamp": "2024-01-15T10:30:05.123Z",
    "level": "INFO",
    "requestId": "req-abc123",              ← correlate across services
    "traceId": "trace-xyz789",              ← correlate with distributed trace
    "userId": "user-456",
    "endpoint": "POST /api/v1/payments",
    "statusCode": 402,
    "latencyMs": 234,
    "errorCode": "CARD_DECLINED",
    "consumerId": "api-key-merchant-xyz"    ← which consumer
  }
  
  NOT: [ERROR] 2024-01-15 Payment failed    ← unstructured, unsearchable
  
  Tools: Logback + JSON encoder → ELK stack, Datadog Logs, Grafana Loki

PILLAR 3 — TRACES:
  What: end-to-end request timeline across all services
  
  Trace (unique traceId):
    Span 1: API Gateway (10ms)
    ├─ Span 2: Auth Service (15ms)
    └─ Span 3: Payment Service (200ms) ← slow here
         ├─ Span 4: DB query payments (180ms) ← DB is the bottleneck
         └─ Span 5: Notification Service (20ms)
    
    Total: 225ms. Root cause: DB query in Payment Service.
    Without traces: "API is slow" — unknown where.
    With traces: "DB query is slow" — actionable.
  
  Tools: Micrometer Tracing → Zipkin, Jaeger, Tempo; OpenTelemetry (vendor-neutral)
```

**GOLDEN SIGNALS (Google SRE Book):**

```
Four Golden Signals (the most critical API metrics):

  1. LATENCY:   Time to serve a request (p50, p95, p99 percentiles)
               Both success and error latency tracked separately

  2. TRAFFIC:   Requests per second (throughput)
               Spike = traffic surge; drop = consumer issues or outage

  3. ERRORS:    Rate of failed requests (4xx, 5xx separately)
               5xx = our fault; 4xx = client errors (may be our API usability issues)

  4. SATURATION: How "full" the service is (CPU, connection pools, queue length)
                Leading indicator: saturation increases before errors appear

  SLO (Service Level Objective) based on golden signals:
  Availability SLO:  99.9% of requests return non-5xx in any 30-day window
  Latency SLO:       99% of requests respond within 500ms
  → Alert when SLO error budget is draining faster than expected
```

---

### 🧪 Thought Experiment

**SCENARIO:** Debug a payment error spike using the three pillars.

```
ALERT: payment 5xx error rate > 5% (fires at 3:47 AM)

STEP 1 — METRICS (how bad is it?):
  Prometheus query: rate(api_errors_total{endpoint="/api/v1/payments",status="500"}[5m])
  → 8% error rate since 3:45 AM (started 2 minutes ago)
  → Only affects POST /api/v1/payments (not GET)
  → All other endpoints: normal

STEP 2 — LOGS (what's happening?):
  Kibana query: endpoint="/api/v1/payments" AND status=500 since 3:45AM
  → Log: {"errorCode": "DB_CONNECTION_TIMEOUT", "latencyMs": 30001, ...}
  → All failures show DB_CONNECTION_TIMEOUT
  → Narrowed: it's a database issue

STEP 3 — TRACES (where exactly?):
  Open trace from failing request in Jaeger
  → Span payment-service: 30001ms
       └─ Span DB_query_payments: 30001ms ← timed out
  → p99 DB query time jumped from 20ms to 30000ms at 3:44 AM
  
  Correlate with deployment log: database connection pool size reduced
  at 3:43 AM by a config change pushed by another team.

ROOT CAUSE: DB connection pool exhausted → queries queue → timeout
FIX: revert connection pool config change
TIME TO RESOLUTION: 8 minutes (vs 45 minutes without observability)
```

---

### 🧠 Mental Model / Analogy

> API observability is a hospital patient monitoring system vs. asking "how do you feel?"
> "I feel fine" (API returning 200) is insufficient for a hospital patient.
> Vitals monitors (metrics): heart rate, blood pressure, oxygen saturation over time.
> Doctor's notes (logs): "at 3:45 PM, patient complained of chest pain, requested nitroglycerin."
> MRI scan (traces): "blockage found in left anterior descending artery, 80% occlusion."
> Each gives a different level of detail. Together: complete clinical picture.
> You can't treat a patient without the detailed internal view.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Observability means your API tells you what's wrong, not just whether it's up. Three types: numbers over time (metrics), detailed event records (logs), and request journey maps across services (traces).

**Level 2:** Spring Boot: add Micrometer (auto-instruments HTTP endpoints for metrics), configure Logback with JSON appender (structured logs), add Micrometer Tracing + Zipkin exporter (traces). Use `@Timed("api.request")` for custom metrics. Include `requestId` in all log entries for correlation.

**Level 3:** Define SLOs from golden signals (error rate, latency p99). Configure Prometheus alerts on SLO error budget burn rate. Use `traceId` to correlate logs and traces. Implement distributed propagation: `traceparent` header (W3C Trace Context) propagated to all downstream service calls. Add custom span tags for high-cardinality dimensions (userId, consumerId, productId) to enable trace filtering.

**Level 4:** Observability's fundamental challenge is cardinality. High-cardinality dimensions (userId, orderId, traceId) are valuable in traces and logs but toxic in metrics: each unique label combination creates a new time-series in Prometheus, leading to "cardinality explosion" that degrades Prometheus performance. Solution: use labels for low-cardinality dimensions in metrics (endpoint, status), logs for medium-cardinality, traces for high-cardinality. OpenTelemetry's unified model (metrics + logs + traces) with a single SDK simplifies this — one instrumentation library outputs all three signals. The SLO-based alerting model (burn rate alerts vs. static threshold alerts) reduces alert fatigue by paging based on business impact rather than individual signal deviations.

---

### ⚙️ How It Works (Mechanism)

```
SPRING BOOT OBSERVABILITY STACK:

  Dependencies:
  - micrometer-registry-prometheus    → HTTP metrics → Prometheus
  - micrometer-tracing-bridge-otel    → Trace instrumentation
  - opentelemetry-exporter-zipkin     → Export traces to Zipkin/Jaeger
  - logstash-logback-encoder          → Structured JSON logs

  Auto-instrumented metrics (via Spring Actuator):
    http_server_requests_seconds{method,uri,status,...}
    → p50, p95, p99 latency per endpoint
    → request rate, error rate

  Trace propagation:
    Incoming: extract traceparent from request header
    Outgoing: inject traceparent into downstream calls
    → Complete trace across all services

  Log correlation:
    Micrometer Tracing: injects traceId and spanId into MDC
    Logback: %X{traceId} in pattern → every log line includes trace ID
    → Can click traceId in log → open trace in Jaeger
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
OBSERVABILITY SIGNAL FLOW:

  API Request
       │
  Spring Boot App:
  ├── Micrometer → increments api_requests_total, records latency histogram
  ├── Logback → emits structured JSON log with traceId, requestId, status, latency
  └── OTel Tracer → creates/continues trace span, propagates to downstream calls
       │
       ├── Prometheus scrapes → Grafana dashboard + SLO alerts
       ├── Filebeat/Fluent Bit ships logs → Elasticsearch/Kibana or Grafana Loki
       └── OTel Collector exports traces → Jaeger/Zipkin/Tempo

  On-call workflow:
  Metric alert fires → Opens Grafana → High error rate on POST /payments
  → Click "View Logs" → Filtered traces for failing payments
  → Click traceId → Waterfall view in Jaeger → DB timeout visible
  → Root cause identified in 5 minutes
```

---

### 💻 Code Example

```java
// Spring Boot API observability — custom metrics + structured logging + tracing
@RestController
@RequiredArgsConstructor
public class PaymentController {

    private final MeterRegistry meterRegistry;
    private final PaymentService paymentService;

    @PostMapping("/api/v1/payments")
    public ResponseEntity<PaymentResponse> createPayment(
            @RequestBody @Valid CreatePaymentRequest request,
            @RequestHeader(value = "X-Request-Id", 
                          defaultValue = "#{T(java.util.UUID).randomUUID().toString()}")
            String requestId) {

        Timer.Sample timer = Timer.start(meterRegistry);
        MDC.put("requestId", requestId);  // propagate to all log entries

        try {
            PaymentResult result = paymentService.processPayment(request);

            timer.stop(Timer.builder("api.payment.processing")
                .tag("result", "success")
                .register(meterRegistry));

            log.info("Payment processed: amount={}, currency={}, txnId={}",
                request.getAmount(), request.getCurrency(), result.getTransactionId());

            return ResponseEntity.status(201).body(toResponse(result));

        } catch (CardDeclinedException e) {
            timer.stop(Timer.builder("api.payment.processing")
                .tag("result", "declined")
                .tag("declineCode", e.getDeclineCode())
                .register(meterRegistry));

            log.warn("Payment declined: declineCode={}, amount={}",
                e.getDeclineCode(), request.getAmount());

            return ResponseEntity.status(402).body(errorResponse(e));

        } finally {
            MDC.remove("requestId");
        }
    }
}

// application.yml
// management:
//   endpoints:
//     web:
//       exposure:
//         include: prometheus, health, info
//   metrics:
//     tags:
//       application: payment-service
//       environment: production
// 
// logging:
//   format: json   ← Spring Boot 3.4+ native JSON logging
```

---

### ⚖️ Comparison Table

| Signal | Aggregation | Cardinality | Best Answers | Tools |
|---|---|---|---|---|
| **Metrics** | Time-series aggregate | Low (counters/gauges) | "How bad? How much? When?" | Prometheus + Grafana |
| **Logs** | Individual events | Medium | "What happened exactly?" | ELK / Loki |
| **Traces** | End-to-end flow | High | "Where did it slow down/fail?" | Jaeger / Zipkin / Tempo |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Logging 5xx errors = monitoring | Logs tell you "what happened." Metrics tell you "how prevalent." Traces tell you "where." All three are needed for full observability |
| High cardinality labels in Prometheus are fine | Each unique label combination = a time-series. `label: userId` = millions of time-series. Prometheus OOM. Use high-cardinality IDs only in traces and logs |
| p99 latency isn't important if p50 is fine | 1% of users see p99 latency. At 1M req/day: 10,000 users per day experiencing the slow tail. SLOs must cover p99 |

---

### 🚨 Failure Modes & Diagnosis

**Alert Fatigue — Too Many Metrics Alerts**

Symptom:
Team has 50 metric alerts. On-call engineers acknowledge them without investigating
("alert fatigue"). Real incidents missed because alerts are background noise.

Root Cause:
Static threshold alerts on too many signals. Alerts not tied to SLO impact.

Fix:
```yaml
# Instead of: alert on p99 > 500ms
# Use SLO burn rate alert (Google SRE approach):
# "Burn through error budget 14× faster than normal (1-hour window)"

- alert: PaymentAPIHighErrorBurnRate
  expr: |
    (
      rate(http_server_requests_seconds_count{
        uri="/api/v1/payments", status=~"5.."}[1h])
    /
      rate(http_server_requests_seconds_count{
        uri="/api/v1/payments"}[1h])
    ) > 14 * 0.001  # 14× the 0.1% SLO error budget burn rate
  for: 5m
  annotations:
    summary: "Payment API burning error budget 14× — page immediately"
# Result: fewer alerts, higher signal-to-noise, each alert = real user impact
```

---

### 🔗 Related Keywords

- `Observability` — the broader engineering discipline; API observability is the applied form
- `Distributed Tracing` — the trace pillar specifically for microservices
- `SLOs` — Service Level Objectives: the targets that make alert thresholds meaningful
- `OpenTelemetry` — the vendor-neutral standard for all three observability signals

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ THREE PILLARS│ Metrics ("how bad?") + Logs ("what?")    │
│              │ + Traces ("where?")                       │
├──────────────┼───────────────────────────────────────────┤
│ GOLDEN SIGS  │ Latency, Traffic, Errors, Saturation      │
├──────────────┼───────────────────────────────────────────┤
│ SLO ALERTS   │ Burn rate alerts > static thresholds     │
├──────────────┼───────────────────────────────────────────┤
│ SPRING BOOT  │ Micrometer + OTel + structured JSON logs  │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULE     │ No userId in Prometheus labels (cardinality)│
│              │ Use traceId/logs for high-cardinality dims │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Know why, not just whether"             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** Your payment API processes 100M requests/day. An incident occurs where 0.2% of
payment requests silently fail (return 200 OK but no payment is actually processed —
a bug in the payment gateway response handler). Neither metrics nor logs catch it:
metrics show 200 OK (success), logs show "Payment processed." Describe what observability
strategy would detect this class of "semantic failure" (request technically succeeds
but business outcome is wrong). What specific signals — beyond HTTP status codes and
standard latency metrics — would you instrument, and how would you define an alert
that catches 0.2% silent failures within 5 minutes?
