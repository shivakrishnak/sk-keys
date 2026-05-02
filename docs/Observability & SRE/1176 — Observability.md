---
layout: default
title: "Observability"
parent: "Observability & SRE"
nav_order: 1176
permalink: /observability/observability/
number: "1176"
category: Observability & SRE
difficulty: ★★☆
depends_on: "Logging, Metrics, Distributed Tracing"
used_by: "SRE, incident response, debugging production, capacity planning"
tags: #observability, #sre, #monitoring, #three-pillars, #logs, #metrics, #traces
---

# 1176 — Observability

`#observability` `#sre` `#monitoring` `#three-pillars` `#logs` `#metrics` `#traces`

⚡ TL;DR — **Observability** is the ability to understand a system's internal state by examining its external outputs. The three pillars: **logs** (what happened), **metrics** (how much/how fast), **traces** (the path a request took). Observability goes beyond monitoring (knowing something is broken) to answering "why is it broken?" — without needing to redeploy code to add instrumentation.

| #1176           | Category: Observability & SRE                                   | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------------- | :-------------- |
| **Depends on:** | Logging, Metrics, Distributed Tracing                           |                 |
| **Used by:**    | SRE, incident response, debugging production, capacity planning |                 |

---

### 📘 Textbook Definition

**Observability**: a property of a system that describes how well internal states can be inferred from external outputs. Borrowed from control theory (Rudolf Kalman, 1960): a system is observable if its current state can be determined from its outputs. In software engineering: a system is observable if engineers can answer arbitrary questions about its behavior using the telemetry it emits — without needing to add new instrumentation to answer a new question. The **three pillars of observability**: (1) **Logs**: timestamped records of discrete events ("user 123 placed order 456 at 14:23:01"); (2) **Metrics**: numerical measurements aggregated over time ("200 RPS, p99 latency 450ms, error rate 0.2%"); (3) **Distributed traces**: the journey of a single request across multiple services ("request 789 took 1.2s total: auth=10ms, inventory=800ms, payment=390ms"). Modern observability extends to: **events**, **profiles** (code-level CPU/memory profiling), and **exceptions**. The distinction from monitoring: monitoring asks pre-defined questions ("is the error rate above 1%?"); observability allows asking ANY question about system state after the fact. Tools: **OpenTelemetry** (CNCF standard for instrumentation), **Jaeger/Zipkin** (distributed tracing), **Prometheus/Grafana** (metrics), **ELK/Loki** (logs), **Datadog/New Relic/Honeycomb** (commercial observability platforms).

---

### 🟢 Simple Definition (Easy)

Without observability: your service is slow, you have no idea why, you add print statements, redeploy, wait for the issue to happen again. With observability: your service is slow, you open your dashboard, see that database query latency spiked at 14:23, pull the trace for a slow request, see it spent 800ms in one inventory database query, find the query, see it's doing a full table scan. Fixed in 20 minutes, no redeployment needed. That's observability.

---

### 🔵 Simple Definition (Elaborated)

Observability is the answer to a fundamental distributed systems problem: **you can't attach a debugger to production**.

In distributed systems:

- A request might touch 8 different services
- Problems are emergent (individual services look fine; together they're broken)
- Production data and patterns differ from dev/staging
- You can't reproduce the issue locally

The three pillars answer three different questions:
| Pillar | Question | Example |
|---|---|---|
| Logs | What happened? | "NullPointerException in CartService at 14:23:01.456 for user 123" |
| Metrics | How much / how fast? | "error rate spiked from 0.1% to 12% at 14:23" |
| Traces | Which path did the request take? | "checkout request spent 850ms waiting for inventory service DB query" |

**Why you need all three**:

- Metrics tell you THAT something is wrong (error rate spiked)
- Logs tell you WHAT went wrong (the specific error message)
- Traces tell you WHERE in the call chain the problem originated (service A called service B which called service C which was slow)

---

### 🔩 First Principles Explanation

```java
// OPENTELEMETRY: the standard for observable Java applications
// OpenTelemetry provides unified SDK for logs, metrics, and traces

// Add to Spring Boot:
// implementation 'io.opentelemetry.instrumentation:opentelemetry-spring-boot-starter'

@RestController
@RequestMapping("/orders")
public class OrderController {

    private final Tracer tracer;  // OpenTelemetry tracer
    private final MeterRegistry meterRegistry;  // Micrometer metrics
    private static final Logger log = LoggerFactory.getLogger(OrderController.class);

    @PostMapping("/checkout")
    public ResponseEntity<OrderResponse> checkout(
            @RequestBody CheckoutRequest request,
            @RequestAttribute("traceId") String traceId) {

        // TRACE: create a span for this operation
        Span span = tracer.spanBuilder("checkout")
            .setAttribute("user.id", request.getUserId())
            .setAttribute("cart.size", request.getCartItems().size())
            .startSpan();

        try (Scope scope = span.makeCurrent()) {
            // LOG: structured log with trace correlation
            log.info("Checkout started",
                kv("traceId", traceId),          // ← links log to trace
                kv("userId", request.getUserId()),
                kv("cartItems", request.getCartItems().size()),
                kv("event", "checkout.started")
            );

            long startTime = System.currentTimeMillis();
            OrderResponse response = orderService.checkout(request);
            long duration = System.currentTimeMillis() - startTime;

            // METRIC: record checkout duration
            meterRegistry.timer("checkout.duration")
                .record(duration, TimeUnit.MILLISECONDS);

            // LOG: success with business context
            log.info("Checkout completed",
                kv("traceId", traceId),
                kv("orderId", response.getOrderId()),
                kv("total", response.getTotal()),
                kv("duration_ms", duration),
                kv("event", "checkout.completed")
            );

            span.setStatus(StatusCode.OK);
            return ResponseEntity.ok(response);

        } catch (Exception e) {
            // TRACE: record exception in span
            span.recordException(e);
            span.setStatus(StatusCode.ERROR, e.getMessage());

            // METRIC: increment error counter
            meterRegistry.counter("checkout.errors",
                "error.type", e.getClass().getSimpleName()).increment();

            // LOG: error with full context
            log.error("Checkout failed",
                kv("traceId", traceId),
                kv("userId", request.getUserId()),
                kv("error", e.getMessage()),
                kv("event", "checkout.failed")
            );

            throw e;
        } finally {
            span.end();
        }
    }
}
```

```yaml
# OPENTELEMETRY COLLECTOR CONFIG: route telemetry to backends
# The collector receives OTLP (OpenTelemetry Protocol) from all services
# and fans out to multiple backends

receivers:
  otlp:
    protocols:
      grpc: { endpoint: 0.0.0.0:4317 }
      http: { endpoint: 0.0.0.0:4318 }

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024

  resource:
    attributes:
      - key: environment
        value: production
        action: insert

exporters:
  # Traces → Jaeger
  jaeger:
    endpoint: jaeger-collector:14250

  # Metrics → Prometheus
  prometheus:
    endpoint: 0.0.0.0:8889

  # Logs → Elasticsearch (via Loki or directly)
  loki:
    endpoint: http://loki:3100/loki/api/v1/push

  # Everything → Datadog (commercial observability platform)
  datadog:
    api:
      key: ${DATADOG_API_KEY}

service:
  pipelines:
    traces:
      { receivers: [otlp], processors: [batch], exporters: [jaeger, datadog] }
    metrics:
      {
        receivers: [otlp],
        processors: [batch],
        exporters: [prometheus, datadog],
      }
    logs: { receivers: [otlp], processors: [batch], exporters: [loki, datadog] }
```

```
OBSERVABILITY IN PRACTICE — INCIDENT INVESTIGATION FLOW:

1. ALERT FIRES: "Error rate > 1% for checkout service" (Metric threshold)

2. DASHBOARD (Metrics): Grafana shows error rate spiked at 14:23
   → Which endpoint? → /api/orders/checkout → 12% errors
   → What error code? → 504 Gateway Timeout

3. TRACES (Jaeger): search for slow/failed requests at 14:23
   → Find trace for a failed request
   → Timeline: auth=8ms, cart=12ms, inventory=4,200ms ← CULPRIT
   → inventory-service is taking 4+ seconds

4. LOGS (Loki): filter inventory-service logs at 14:23
   → "SELECT * FROM inventory WHERE product_id IN (...): execution time 4,150ms"
   → "Slow query warning: full table scan detected"

5. ROOT CAUSE: inventory query doing full table scan after recent migration
   dropped an index. Fix: restore index.

CORRELATION KEY:
All three signals are linked by TRACE ID:
- Log line: {"traceId": "abc123", "message": "..."}
- Trace span: traceId=abc123, service=inventory-service, duration=4200ms
- Metric tag: {trace_id="abc123"} — some systems correlate exemplars
```

---

### ❓ Why Does This Exist (Why Before What)

Monolithic applications could be debugged with a local debugger or grep on a single log file. Distributed systems with dozens of microservices cannot: a single user request touches 8 services; a failure in one service has cascading effects; production traffic patterns don't reproduce in development. Observability emerged as the engineering discipline of making distributed systems understandable — not by adding more monitoring (pre-defined queries against known unknowns) but by building systems that can answer arbitrary questions about their behavior (unknown unknowns).

---

### 🧠 Mental Model / Analogy

> **Observability is like an aircraft flight data recorder (black box)**: the black box doesn't define in advance what questions crash investigators will ask. It records everything — speed, altitude, control surface positions, cockpit audio. When a crash happens, investigators can reconstruct exactly what happened from the recorded data. Software observability is the same: you can't predict in advance what questions you'll need to answer during an incident. So you instrument everything — logs, metrics, traces — and when an incident happens, you can reconstruct exactly what the system was doing.

---

### 🔄 How It Connects (Mini-Map)

```
Distributed systems need to be understood from the outside
        │
        ▼
Observability ◄── (you are here)
(logs + metrics + traces; answer any question about system state)
        │
        ├── Logging: first pillar — discrete events
        ├── Metrics: second pillar — aggregated measurements
        ├── Distributed Tracing: third pillar — request journey
        ├── OpenTelemetry: standard instrumentation framework
        └── SRE: observability is foundational to SRE practices
```

---

### 💻 Code Example

```java
// SPRING BOOT ACTUATOR + MICROMETER: automatic observability for Spring apps

// application.yml
management:
  endpoints:
    web:
      exposure:
        include: health, info, metrics, prometheus
  metrics:
    export:
      prometheus:
        enabled: true
    tags:
      application: order-service      # tag all metrics with app name
      environment: ${ENVIRONMENT}     # tag with environment
  tracing:
    sampling:
      probability: 1.0  # sample 100% of requests (reduce to 0.1 in production)
  zipkin:
    tracing:
      endpoint: http://jaeger:9411/api/v2/spans

// With this config, Spring Boot auto-instruments:
// - All HTTP endpoints (request rate, latency, status codes)
// - JVM metrics (GC, heap, thread count)
// - HikariCP (DB connection pool utilization)
// - Spring Data (query execution times)
// GET /actuator/prometheus → all metrics in Prometheus format
// All HTTP requests get a traceId header added automatically
```

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                                                                                                                                                                                                                                                       |
| ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Observability = monitoring                     | Monitoring is asking pre-defined questions about known failure modes ("is CPU > 90%?"). Observability is the ability to ask ANY question after the fact ("why was this specific request slow at 14:23 for this specific user?"). Monitoring answers known unknowns; observability handles unknown unknowns. You need both.    |
| More logs = better observability               | Logging everything at DEBUG level in production creates noise, storage costs, and makes finding signal harder. Good observability is about logging the RIGHT things at the RIGHT levels with structured, consistent data. A single log line with 10 structured fields is more observable than 100 lines of unstructured text. |
| Observability is only needed for large systems | Even a simple 2-service application benefits from basic observability: structured logging with correlation IDs makes debugging 10x faster. Start small: structured logging + basic metrics (request rate, error rate, latency) + health endpoints. Scale up instrumentation as the system grows.                              |

---

### 🔗 Related Keywords

- `Logging` — first pillar of observability
- `Metrics` — second pillar of observability
- `Distributed Tracing` — third pillar of observability
- `OpenTelemetry` — standard for instrumentation across all three pillars
- `SRE` — Site Reliability Engineering uses observability as its foundation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ THREE PILLARS:                                          │
│  Logs    → WHAT happened (discrete events)             │
│  Metrics → HOW MUCH / HOW FAST (aggregated numbers)   │
│  Traces  → WHICH PATH (request journey across services)│
│                                                          │
│ CORRELATION: all three linked by Trace ID              │
│ STANDARD: OpenTelemetry (CNCF)                         │
│ TOOLS: Prometheus+Grafana | Jaeger | ELK/Loki          │
│                                                          │
│ MONITORING vs OBSERVABILITY:                           │
│  Monitoring = known unknowns (pre-defined alerts)     │
│  Observability = unknown unknowns (any question)      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** OpenTelemetry (OTel) is a CNCF standard that provides vendor-neutral SDKs for all three observability pillars. Before OTel, each vendor (Datadog, New Relic, Jaeger, Prometheus) had its own SDK — switching vendors required changing all instrumentation code. With OTel: instrument once, route to any backend via the OTel Collector. The trade-off: OTel adds complexity (the collector is another component to manage). For a team considering adopting OTel: when is it worth the complexity? What migration path makes sense for a system currently using vendor-specific SDKs? What does the OTel semantic conventions standard add to make telemetry portable across tools?

**Q2.** Observability data is expensive: logs can be terabytes per day; high-cardinality metrics exhaust storage; tracing all requests at 100% sample rate creates storage and compute costs at scale. Cost management strategies: log sampling (log only 10% of INFO events; 100% of ERROR events); metrics aggregation (pre-aggregate high-cardinality metrics at the collector); trace sampling (head-based: sample 5% of requests randomly; tail-based: sample 100% of requests that errored or were slow). Design an observability cost optimization strategy for a system handling 100,000 RPS with an observability budget constraint. What trade-offs do you make between coverage and cost?
