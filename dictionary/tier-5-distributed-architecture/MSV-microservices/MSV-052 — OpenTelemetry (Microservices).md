---
layout: default
title: "OpenTelemetry (Microservices)"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 52
permalink: /microservices/opentelemetry-microservices/
id: MSV-052
category: Microservices
difficulty: ★★★
depends_on: Distributed Logging, Correlation ID (Microservices), Cross-Cutting Concerns
used_by: Chaos Engineering, Observability & SRE, Distributed Tracing
related: Correlation ID (Microservices), Distributed Logging, Jaeger (Distributed Tracing)
tags:
  - microservices
  - observability
  - tracing
  - standards
  - deep-dive
---

# MSV-052 — OpenTelemetry (Microservices)

⚡ TL;DR — OpenTelemetry is the open standard for collecting traces, metrics, and logs from microservices with vendor-neutral instrumentation, enabling unified observability across any backend (Jaeger, Prometheus, Datadog, etc.).

| #667            | Category: Microservices                                                           | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Logging, Correlation ID (Microservices), Cross-Cutting Concerns       |                 |
| **Used by:**    | Chaos Engineering, Observability & SRE, Distributed Tracing                       |                 |
| **Related:**    | Correlation ID (Microservices), Distributed Logging, Jaeger (Distributed Tracing) |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your team uses Zipkin for tracing (Zipkin SDK), Prometheus for metrics (Micrometer), and ELK for logs (Logstash). Each uses a different SDK, different header formats, and different data models. Switching from Zipkin to Jaeger requires updating every service's tracing SDK. Switching from Prometheus to Datadog requires rewriting metric instrumentation. Vendor lock-in: your observability is tightly coupled to specific tools, not to open standards. Teams implement tracing differently — some services have traces; some don't; cross-service traces are broken.

**THE BREAKING POINT:**
Proprietary observability SDKs create lock-in, inconsistency, and massive migration costs. Every new observability tool means re-instrumenting every service.

**THE INVENTION MOMENT:**
OpenTelemetry (OTel) was created — via the merger of OpenCensus and OpenTracing — to provide one open standard for all observability signals: traces, metrics, and logs. Instrument once; send anywhere.

---

### 📘 Textbook Definition

**OpenTelemetry (OTel)** is a CNCF open-source observability framework and standard that provides: (1) a vendor-neutral API for instrumenting applications (spans, metrics, logs); (2) SDK implementations in all major languages; (3) the OpenTelemetry Protocol (OTLP) for exporting telemetry data; (4) the OTel Collector — an agent/gateway for receiving, processing, and exporting telemetry to any backend; (5) W3C Trace Context (`traceparent` / `tracestate` headers) for cross-service trace propagation. OTel replaces OpenTracing, OpenCensus, and proprietary SDKs.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Instrument your code once with OTel; export traces/metrics/logs to any backend (Jaeger, Prometheus, Datadog, Grafana) by changing config, not code.

**One analogy:**

> OpenTelemetry is like a universal power adapter. Instead of having a different adapter for every country (different SDK per observability backend), you use one universal adapter (OTel SDK) and swap just the plug attachment (exporter config) depending on where you are. The device (your application) never changes.

**One insight:**
The OTel Collector is the architectural linchpin: services send telemetry to the collector (one destination), and the collector fans out to multiple backends — Jaeger for traces, Prometheus for metrics, Loki for logs. Swap the backend by updating collector config, not service code.

---

### 🔩 First Principles Explanation

**THE THREE SIGNALS:**

**1. Traces (spans):**

```
Trace: complete picture of a request's journey
  └── Span: "HTTP GET /orders" (100ms, order-service)
        └── Span: "SELECT * FROM orders" (10ms, DB)
        └── Span: "HTTP GET /products/123" (50ms, product-service)
              └── Span: "SELECT * FROM products" (5ms, DB)
```

**2. Metrics:**

- Counter: total requests, total errors
- Gauge: active connections, memory usage
- Histogram: request duration distribution (P50/P95/P99)

**3. Logs:**

- OTel connects logs to traces via `traceId` and `spanId` injection into MDC
- Log entries become linkable to their parent span in Jaeger/Grafana

**THE OTEL ARCHITECTURE:**

```
Application (instrumented with OTel SDK)
      │ OTLP (gRPC or HTTP)
      ▼
OTel Collector (agent or gateway)
  - Receivers: OTLP, Zipkin, Jaeger (legacy)
  - Processors: batch, filter, attribute transform
  - Exporters: Jaeger, Prometheus, Loki, Datadog, OTLP
      │
      ├──► Jaeger (traces)
      ├──► Prometheus (metrics)
      └──► Loki (logs)
```

**W3C Trace Context propagation:**

```
HTTP header: traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
             version-traceId-spanId-flags
```

Every service that uses OTel automatically reads and writes `traceparent` headers — distributed traces work cross-service and cross-language automatically.

**AUTO-INSTRUMENTATION:**
OTel Java agent: `-javaagent:opentelemetry-javaagent.jar`
Zero code changes. Automatically instruments:

- Spring Boot web endpoints (HTTP spans)
- JDBC queries (DB spans)
- RestTemplate / WebClient (outbound HTTP spans)
- Kafka producer/consumer (messaging spans)

**THE TRADE-OFFS:**
**Gain:** Vendor-neutral; one SDK for all signals; auto-instrumentation for many frameworks; W3C standard for propagation; switch backends without re-instrumentation; CNCF support (long-term standard).
**Cost:** OTel Collector is critical infrastructure; sampling strategy required (100% trace sampling is expensive); Java agent adds JVM startup time; learning curve for Collector configuration; distributed tracing adds ~5ms overhead per hop.

---

### 🧪 Thought Experiment

**SETUP:**
Your 20-service system uses Zipkin for traces, Prometheus for metrics, and a custom log format. New business requirement: switch tracing backend from Zipkin to Jaeger (better UI) AND add traces to Datadog for the security team.

**WITHOUT OTEL:**
Update Zipkin SDK to Jaeger SDK in 20 services. Each service redeploys. Datadog requires its own SDK. Now each service has two tracing SDKs. Schema changes for trace data. 3 months of work.

**WITH OTEL:**
All 20 services already use OTel SDK. Update OTel Collector config:

```yaml
exporters:
  jaeger: # add Jaeger exporter
  datadog: # add Datadog exporter  ← just add this
  # remove zipkin exporter

service:
  pipelines:
    traces:
      exporters: [jaeger, datadog] # fan-out to both
```

Deploy updated Collector. Done. Zero service code changes. 2-hour config change replaces 3 months of SDK updates.

**THE INSIGHT:**
The OTel Collector absorbs backend complexity. Services are abstracted from backend choice. This is not just a technical benefit — it's an organisational one: the platform team can change observability infrastructure without requiring every service team to act.

---

### 🧠 Mental Model / Analogy

> OTel is to observability what USB-C is to device charging. Before USB-C, every device had a different charging port (proprietary observability SDK). USB-C (OTel) provides one standard port. Your device (application) doesn't care what's on the other end — a laptop charger, a monitor, a phone. The universal standard handles the translation. The adapter (OTel Collector) can split the signal to multiple destinations simultaneously.

- "Different charging ports" → proprietary observability SDKs (Zipkin, Jaeger, Datadog SDK)
- "USB-C standard" → OTel standard API + OTLP protocol
- "Device doesn't change" → application code doesn't change when backend changes
- "The adapter/hub" → OTel Collector
- "Multiple destinations from one port" → fan-out: traces to Jaeger, metrics to Prometheus

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
OpenTelemetry is an industry-standard way for applications to say "I'm doing X, it took Y milliseconds" and send that information to a monitoring tool. The same code works with any monitoring tool — you don't need to rewrite when you switch tools.

**Level 2 — How to use it (junior developer):**

1. Add OTel Java agent as a JVM arg (zero code changes for auto-instrumentation).
2. Configure agent with environment variables: `OTEL_SERVICE_NAME`, `OTEL_EXPORTER_OTLP_ENDPOINT`.
3. Deploy OTel Collector (Helm chart).
4. Configure Collector pipelines in `otel-config.yaml`.
5. Access traces in Jaeger UI; metrics in Prometheus/Grafana.
6. For custom spans: use the OTel API (`Tracer`, `Span`).

**Level 3 — Sampling strategy (mid-level engineer):**
Tracing every request at 10k req/sec = expensive. Sampling strategies:

- **Head-based sampling**: decide at trace start (fast, but loses context of "interesting" traces)
- **Tail-based sampling**: collect all spans; decide after trace completes (keeps error traces; expensive storage)
- **Probabilistic**: sample X% of traces (simple; misses rare errors)
- **Rate-limited**: max N traces/sec (protects storage; drops in spikes)
- Recommended for production: 1–5% probabilistic + 100% for errors (tail-based in Collector).

**Level 4 — OTel semantic conventions (senior/staff):**
OTel defines semantic conventions — standardised attribute names for common operations:

- HTTP: `http.method`, `http.url`, `http.status_code`
- DB: `db.system`, `db.statement`, `db.operation`
- Messaging: `messaging.system`, `messaging.destination`
  These conventions enable cross-service querying: "show all spans where `db.statement` contains 'orders' AND `http.status_code = 500`." They also enable auto-dashboards in Grafana that work for any service following conventions. The deeper principle: OTel semantic conventions are the observability equivalent of API contracts — standardised names mean standardised tooling can interpret any service's telemetry without custom configuration.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│           OpenTelemetry — Full Architecture             │
└─────────────────────────────────────────────────────────┘

Service (with OTel Java Agent):
  Auto-instruments:
    - HTTP requests (Spring MVC/Boot)
    - DB queries (JDBC, R2DBC)
    - Outbound HTTP (RestTemplate, WebClient, OkHttp)
    - Kafka (spring-kafka, kafka-clients)

  Creates spans:
    Span{
      traceId: "4bf92f35...",
      spanId:  "00f067aa...",
      name:    "GET /orders/{id}",
      service: "order-service",
      startTime: ..., duration: 45ms,
      attributes: {
        http.method: GET,
        http.status_code: 200,
        http.url: /orders/order-123
      }
    }

  Exports via OTLP → OTel Collector

OTel Collector:
  receivers:
    otlp:              # receives from services
      protocols:
        grpc:
          endpoint: 0.0.0.0:4317

  processors:
    batch:             # batch before export
    memory_limiter:    # protect collector RAM
    tail_sampling:     # keep errors; sample success
      policies:
        - type: status_code
          status_code: {status_codes: [ERROR]}
        - type: probabilistic
          probabilistic: {sampling_percentage: 1}

  exporters:
    jaeger:
      endpoint: jaeger:14250
    prometheusremotewrite:
      endpoint: prometheus:9090

  service:
    pipelines:
      traces:
        receivers: [otlp]
        processors: [memory_limiter, tail_sampling, batch]
        exporters: [jaeger]
      metrics:
        receivers: [otlp]
        exporters: [prometheusremotewrite]
```

---

### 🔄 The Complete Picture — Cross-Service Trace

```
[Client: GET /checkout]
  traceparent: 00-4bf92f35...-00f067aa...-01

[API Gateway span: "checkout-ingress" (2ms)]
  └─[Order Service span: "POST /orders" (80ms)]
       │ sets traceparent header
       ├─[DB span: "INSERT orders" (10ms)]
       └─[Inventory Service span: "reserve stock" (40ms)]
            │ sets traceparent header
            └─[DB span: "UPDATE stock" (15ms)]

All spans share traceId: 4bf92f35...
Jaeger UI: one timeline showing all 5 spans in hierarchy
Engineers see: checkout = 80ms total; DB insert fine;
               stock reservation slow (40ms) → bottleneck found
```

---

### 💻 Code Example

**Example 1 — Auto-instrumentation (no code changes):**

```bash
# Dockerfile: add OTel Java agent
COPY opentelemetry-javaagent.jar /app/
CMD ["java",
     "-javaagent:/app/opentelemetry-javaagent.jar",
     "-jar", "/app/order-service.jar"]
```

```yaml
# Kubernetes deployment env vars
env:
  - name: OTEL_SERVICE_NAME
    value: "order-service"
  - name: OTEL_EXPORTER_OTLP_ENDPOINT
    value: "http://otel-collector:4317"
  - name: OTEL_TRACES_SAMPLER
    value: "parentbased_traceidratio"
  - name: OTEL_TRACES_SAMPLER_ARG
    value: "0.01" # 1% sampling
  - name: OTEL_LOGS_EXPORTER
    value: "otlp"
```

**Example 2 — Custom spans for business events:**

```java
@Service
public class OrderService {
  private final Tracer tracer = GlobalOpenTelemetry
    .getTracer("order-service");

  public Order processOrder(OrderRequest req) {
    Span span = tracer.spanBuilder("process-order")
      .setAttribute("order.customerId", req.getCustomerId())
      .setAttribute("order.totalAmount", req.getAmount())
      .startSpan();

    try (Scope scope = span.makeCurrent()) {
      // Business logic...
      Order order = createOrder(req);
      span.setAttribute("order.id", order.getId());
      span.setStatus(StatusCode.OK);
      return order;
    } catch (Exception e) {
      span.recordException(e);
      span.setStatus(StatusCode.ERROR, e.getMessage());
      throw e;
    } finally {
      span.end();
    }
  }
}
```

**Example 3 — OTel Collector Helm values:**

```yaml
# helm install otel-collector open-telemetry/opentelemetry-collector
config:
  receivers:
    otlp:
      protocols:
        grpc: {}
        http: {}
  exporters:
    jaeger:
      endpoint: "jaeger-collector:14250"
      tls:
        insecure: true
    prometheusremotewrite:
      endpoint: "http://prometheus:9090/api/v1/write"
  service:
    pipelines:
      traces:
        receivers: [otlp]
        exporters: [jaeger]
      metrics:
        receivers: [otlp]
        exporters: [prometheusremotewrite]
```

---

### ⚖️ Comparison Table

| Approach                 | Vendor Lock-in | Languages | Signal Coverage         | Maturity   |
| ------------------------ | -------------- | --------- | ----------------------- | ---------- |
| **OpenTelemetry**        | None           | All major | Traces + Metrics + Logs | GA (2023)  |
| OpenTracing (deprecated) | None           | All major | Traces only             | Deprecated |
| OpenCensus (deprecated)  | None           | Java, Go  | Traces + Metrics        | Deprecated |
| Micrometer               | None           | JVM only  | Metrics only            | Stable     |
| Zipkin SDK               | Zipkin         | All major | Traces only             | Stable     |
| Datadog SDK              | Datadog        | All major | Traces + Metrics        | Stable     |

**How to choose:** Use **OpenTelemetry** for all new instrumentation. Replace legacy Zipkin/Jaeger/OpenCensus SDKs with OTel as services are updated. OTel is now the industry standard.

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                 |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| OTel replaces Jaeger, Prometheus, Grafana   | OTel is the instrumentation standard; Jaeger/Prometheus/Grafana are the backends                                        |
| OTel requires code changes in every service | Java agent provides auto-instrumentation with zero code changes                                                         |
| OTel is only for tracing                    | OTel covers traces, metrics, AND logs — all three observability signals                                                 |
| OTel Collector is optional                  | Technically optional, but strongly recommended — enables backend flexibility and protects services from backend changes |
| 100% trace sampling is the right default    | At high throughput, 100% sampling is prohibitively expensive; 1–5% + 100% for errors is correct                         |

---

### 🚨 Failure Modes & Diagnosis

**Traces Missing in Jaeger**

**Symptom:** Services are running but traces not appearing in Jaeger.

**Root Cause:** OTel Collector misconfiguration; sampling rate too low; OTLP endpoint wrong; Collector-to-Jaeger network issue.

**Diagnostic Command:**

```bash
# Check OTel Collector receiving spans
kubectl logs deployment/otel-collector | grep "Received"

# Verify Collector can reach Jaeger
kubectl exec deployment/otel-collector -- \
  wget -O- http://jaeger-collector:14250 2>&1

# Check service is sending to Collector
kubectl logs deployment/order-service | \
  grep -i "opentelemetry\|otlp\|export"
```

**Fix:** Verify `OTEL_EXPORTER_OTLP_ENDPOINT` env var; check Collector pipeline config; verify network policies allow port 4317.

---

**OTel Collector Memory OOM**

**Symptom:** OTel Collector pod OOMKilled; traces lost.

**Root Cause:** High-throughput system sending more spans than Collector can process; tail-based sampling buffer too large; no `memory_limiter` processor configured.

**Fix:**

```yaml
processors:
  memory_limiter:
    check_interval: 1s
    limit_mib: 400
    spike_limit_mib: 100
```

**Prevention:** Always include `memory_limiter` processor; set resource limits on Collector pod; scale Collector horizontally for high-throughput systems.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Distributed Logging` — OTel bridges logs and traces
- `Correlation ID (Microservices)` — OTel standardises this as W3C Trace Context
- `Cross-Cutting Concerns` — OTel is the canonical cross-cutting observability standard

**Builds On This (learn these next):**

- `Chaos Engineering` — uses OTel traces to understand failure behaviour
- `Observability & SRE` — OTel is the instrumentation foundation for full observability
- `Distributed Tracing` — OTel provides the spans; Jaeger/Zipkin provide the UI

**Alternatives / Comparisons:**

- `Zipkin` — older tracing system; OTel can export to Zipkin
- `Jaeger` — trace backend; OTel instrumentation → OTLP → Jaeger
- `Datadog APM` — commercial alternative; OTel can export to Datadog

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Open standard for traces + metrics + logs;│
│              │ vendor-neutral; any backend via Collector  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Proprietary SDK lock-in; re-instrumenting  │
│ SOLVES       │ all services when changing observability   │
│              │ backend                                   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Instrument once; route anywhere via the   │
│              │ OTel Collector                            │
├──────────────┼───────────────────────────────────────────┤
│ SETUP        │ Java agent (zero code changes) +           │
│              │ OTel Collector + OTLP endpoint            │
├──────────────┼───────────────────────────────────────────┤
│ SAMPLING     │ 1% default + 100% for errors              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "USB-C for observability"                  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ OTel Collector → Jaeger → Grafana Tempo   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your 25-service system currently uses: Zipkin Java SDK for tracing, Micrometer + Prometheus for metrics, and ELK for logs. You want to migrate to full OpenTelemetry. Describe a migration strategy that: (a) doesn't require a big-bang cutover; (b) keeps existing backends running during migration; (c) specifies the order in which services are migrated; and (d) explains how you validate each service's migration before proceeding to the next.

**Q2.** At 50,000 requests/sec, 100% trace sampling generates 2.5 million spans/sec. Calculate the approximate storage cost at 1KB per span, 7-day retention. Design a tail-based sampling strategy that: keeps 100% of error traces, keeps 100% of traces slower than P99 (500ms), and samples 0.5% of everything else. Describe how you implement this in the OTel Collector config.
