---
id: DST-055
title: Observability in Distributed Systems
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-019, DST-025
used_by: DST-069, DST-070
related: DST-019, DST-025, DST-032
tags:
  - distributed
  - observability
  - tracing
  - logging
  - metrics
  - opentelemetry
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 55
permalink: /technical-mastery/distributed-systems/observability/
---

⚡ TL;DR - Observability in distributed systems is
the ability to understand internal state from external
outputs; built on three pillars: traces (how a request
flows through services), metrics (aggregate numbers
over time), and logs (timestamped events per service);
distributed tracing with correlation IDs is the
unique challenge vs single-system observability.

---

### 📋 Entry Metadata

| #055 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Health Checks and Readiness Probes, Rate Limiting | |
| **Used by:** | Production Diagnosis Toolkit, Incident Simulation | |
| **Related:** | Health Checks, Rate Limiting, Lamport Timestamps | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A user reports: "checkout is slow." You have 12
microservices involved in checkout. All services
look healthy individually (CPU normal, memory normal,
error rate low). The service that is actually slow
is the inventory service, but only when called during
a specific discount calculation code path that is
triggered by a particular combination of cart items.

Without distributed tracing: you don't know which
service is slow. Log correlation across services:
impossible without a shared request ID. Debugging:
look at 12 different log files, manually correlate
timestamps, hope for a smoking gun.

With distributed tracing: one trace ID shows the
full request tree: API gateway → auth service → cart
service → inventory service (3200ms). Immediately
see: inventory service call took 3200ms. Drill in:
the slow inventory call includes a sub-call to a
discount database query that returned 25,000 rows
and was not paginated. Bug found in 2 minutes.

---

### 📘 Textbook Definition

**Observability** is the measure of how well you can
understand the internal state of a system by examining
its outputs. From control theory: a system is
"observable" if its internal state can be determined
from its outputs.

**The Three Pillars:**
1. **Metrics:** Numeric aggregates over time (CPU,
   latency percentiles, error rate, throughput).
   Good for alerting and trending.
2. **Logs:** Timestamped, structured records of
   discrete events per service. Good for debugging
   specific errors.
3. **Traces:** End-to-end record of a single request's
   journey across multiple services. Good for
   understanding latency and dependency behavior.

**Distributed tracing specifics:**
- Every request gets a unique **trace ID**
- Each operation within the trace gets a **span ID**
- Spans have parent-child relationships (call tree)
- All spans share the trace ID and are aggregated
  to reconstruct the full request path

---

### ⏱️ Understand It in 30 Seconds

```
REQUEST FLOW (with distributed tracing):
  Client → API Gateway → Order Service → DB

TRACE (trace_id: abc-123):
  Span 1: API Gateway    [0ms - 45ms]   (root)
    Span 2: Order Svc    [5ms - 42ms]   (child of 1)
      Span 3: DB query   [10ms - 38ms]  (child of 2)

WHAT IT TELLS YOU:
  - Total request: 45ms
  - API Gateway overhead: 10ms (root - child = 5ms+3ms)
  - Order service logic: 4ms (excluding DB call)
  - DB query: 28ms (that's where the time went)
  
WITHOUT TRACING: "API is slow (45ms)" - useless.
WITH TRACING: "DB query caused 28ms of the 45ms" -
  actionable.
```

---

### 🔩 First Principles Explanation

**DISTRIBUTED TRACING PROPAGATION:**

```
Service A calls Service B via HTTP:

Service A:
  - Has active trace (trace_id=abc, span_id=001)
  - Creates child span (span_id=002, parent=001)
  - Injects into HTTP headers:
    traceparent: 00-abc-002-01   (W3C format)
  - Makes HTTP call to Service B

Service B:
  - Extracts trace context from headers
  - Creates child span (span_id=003, parent=002)
  - Records: start time, operation name, attributes
  - Makes DB call → creates child span (span_id=004)
  - Completes → records end time and status
  - Sends span to collector (async, sampled)

Service A:
  - Receives response
  - Marks span_002 complete with status and duration
  - Sends to collector

Collector aggregates all spans by trace_id=abc
→ reconstructs full call tree.
```

**OPENTELEMETRY CODE EXAMPLE:**

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor
)

# Setup (once at service startup):
provider = TracerProvider()
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831
)
provider.add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("order-service")

# In order processing code:
def process_order(order_id: str, user_id: str) -> Order:
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)
        span.set_attribute("user.id", user_id)

        # Nested span for DB call:
        with tracer.start_as_current_span("db.fetch_order"):
            order = db.fetch(order_id)

        # Nested span for inventory check:
        with tracer.start_as_current_span(
            "inventory.check"
        ) as inv_span:
            inv_span.set_attribute("items.count",
                                   len(order.items))
            result = inventory_client.check(order.items)

        return order
```

**TRACE SAMPLING:**

```
PROBLEM: High-traffic services (1000 req/s) would
generate millions of spans per minute.
Cost: storage, network, processing.

SAMPLING STRATEGIES:

1. HEAD-BASED (at request start):
   - Sample at API gateway (before trace propagates)
   - Simple: always sample 1% of requests
   - Problem: low-error traces sampled; high-error
     traces may be missed (random chance)

2. TAIL-BASED (at request end):
   - Collect all spans, decide after seeing outcome
   - Sample 100% of errors, 1% of successes
   - Requires: buffer all spans until decision
   - Problem: storage and latency cost

3. ADAPTIVE/DYNAMIC:
   - Sample high-latency requests (P99+ outliers)
   - Always sample error traces
   - Rate-limit sampling per service (fairness)

PRODUCTION RECOMMENDATION:
  1% head-based sampling for normal traffic
  + 100% error/slow trace tail-sampling
  Tools: OpenTelemetry Collector with tail sampler
```

**STRUCTURED LOGGING:**

```python
import json
import logging

class StructuredLogger:
    def __init__(self, service_name: str):
        self.service = service_name

    def log(self, level: str, message: str,
            trace_id: str | None = None,
            **kwargs):
        """Log in JSON format with trace correlation."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "service": self.service,
            "message": message,
            "trace_id": trace_id,  # For correlation
            **kwargs  # Additional structured fields
        }
        # Remove None values:
        entry = {k: v for k, v in entry.items()
                 if v is not None}
        print(json.dumps(entry))  # stdout → collector

# Usage:
logger = StructuredLogger("order-service")
logger.log("INFO", "Order created",
           trace_id=current_trace_id(),
           order_id="ord-123",
           amount=49.99,
           currency="USD")

# Output (query with trace_id to find related logs):
# {
#   "timestamp": "2024-03-15T10:00:00Z",
#   "level": "INFO",
#   "service": "order-service",
#   "message": "Order created",
#   "trace_id": "abc-123",
#   "order_id": "ord-123",
#   "amount": 49.99,
#   "currency": "USD"
# }
```

---

### 🧠 Mental Model / Analogy

> Observability is like the cockpit of an airplane.
> Metrics are the gauges (altitude, speed, fuel) -
> give you aggregate state at a glance. Logs are the
> black box recorder - every event recorded in sequence.
> Traces are the flight path tracker - show exactly
> where the plane went, when, and at what altitude.
> During a normal flight, you mainly watch gauges.
> After an incident, you combine all three: gauges
> show when altitude dropped, the recorder shows
> what the pilot did, the flight path shows where
> it happened. In distributed systems: metrics alert
> you, logs help you debug, traces show you which
> service to debug.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
Observability is your ability to understand "what
is the system doing right now and what did it do?"
in a distributed system where no single node has
the full picture.

**Level 2 - The three pillars:**
Metrics: numbers over time (alert on anomalies).
Logs: events per service (debug specific errors).
Traces: request paths across services (find latency).
You need all three; each answers different questions.

**Level 3 - Correlation IDs are the key:**
Without a shared trace ID, correlating logs across
12 services requires manual timestamp matching.
With a trace ID propagated in every request:
one query in your trace backend shows the full
request journey. The trace ID is the distributed
system's equivalent of a thread dump.

**Level 4 - OpenTelemetry standardizes instrumentation:**
Before OpenTelemetry, every observability tool
had its own SDK. Switching from Jaeger to Zipkin
required rewriting instrumentation. OpenTelemetry
separates instrumentation (in code) from export
(to backend): instrument once, route to any backend
(Jaeger, Zipkin, Datadog, Honeycomb). OTEL is now
the standard.

**Level 5 - Service Level Objectives (SLOs):**
Observability data feeds SLO management. An SLO
(e.g., "99.9% of requests complete in < 200ms")
is measured from trace/metric data. Error budget
(how much SLO violation is allowed per month)
is calculated from metrics. When error budget is
being consumed too fast, observability data shows
which service and which operation is responsible.
This connects observability to production reliability
management.

---

### 💻 Code Example

**Distributed Tracing: Without vs With Context Propagation**

```python
# BAD: Service calls without trace propagation
# (impossible to correlate logs across services)

import httpx

def process_order_bad(order_id: str) -> dict:
    # No trace ID in request - logs will be isolated:
    response = httpx.get(
        f"http://inventory-service/check/{order_id}"
    )
    # When this fails, you'll see:
    # order-service log: "Inventory check failed"
    # inventory-service log: "Request failed"
    # No way to correlate the two without timestamp hunting
    return response.json()
```

```python
# GOOD: With OpenTelemetry trace propagation

from opentelemetry import trace
from opentelemetry.propagate import inject

tracer = trace.get_tracer("order-service")

def process_order_good(order_id: str) -> dict:
    with tracer.start_as_current_span(
        "process_order",
        attributes={"order.id": order_id}
    ) as span:
        headers = {}
        # Inject W3C traceparent header:
        inject(headers)  # adds traceparent=00-abc-xyz-01

        try:
            response = httpx.get(
                f"http://inventory-service/check/{order_id}",
                headers=headers  # Propagates trace context
            )
            response.raise_for_status()

            span.set_attribute("inventory.status", "ok")
            return response.json()

        except httpx.HTTPStatusError as e:
            # Mark span with error:
            span.set_status(
                trace.StatusCode.ERROR,
                str(e)
            )
            span.record_exception(e)
            raise

# In inventory-service: extract context from headers
# (OpenTelemetry middleware does this automatically):
# from opentelemetry.propagate import extract
# context = extract(request.headers)
# → spans in inventory-service have correct parent_span_id
# → both services' spans appear in same trace in Jaeger
```

---

### ⚖️ Comparison Table

| Pillar | Question It Answers | Tool Examples | Alert On |
|---|---|---|---|
| **Metrics** | Is the system healthy right now? | Prometheus, CloudWatch, Datadog | Threshold breach |
| **Logs** | What happened for a specific error? | ELK Stack, Loki, CloudWatch Logs | Error keywords |
| **Traces** | Which service caused latency? | Jaeger, Zipkin, Tempo, X-Ray | - (exploration) |

| Tool | Type | Strength |
|---|---|---|
| **OpenTelemetry** | Instrumentation SDK | Vendor-neutral; instrument once |
| **Jaeger** | Trace backend | Open source, Kubernetes-native |
| **Prometheus** | Metrics | Pull-based; powerful query language |
| **Loki** | Logs | Low cost; integrates with Grafana |
| **Datadog** | All three | Managed; expensive; powerful |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Logs are sufficient for debugging microservices" | Logs per service are insufficient for cross-service debugging. Without trace IDs, correlating logs from 10 services for a single user request requires manual timestamp matching. Logs need trace context to be useful in microservices. |
| "Metrics alone can identify the root cause" | Metrics show THAT something is wrong and which service's aggregate metrics are anomalous. They cannot show the execution path within a specific request. Traces show WHY a specific request was slow. Both are needed. |
| "100% trace sampling is too expensive" | 100% trace sampling in a high-throughput service (10,000 req/s) generates enormous data. But 100% sampling for error traces and high-latency outliers (tail-based sampling) is the right approach and can be done with OpenTelemetry Collector's tail sampler. |
| "Observability is the same as monitoring" | Monitoring checks known failure modes (alert when CPU > 80%). Observability enables exploration of unknown failure modes ("why is this specific user's request slow?"). Monitoring is predefined; observability is exploratory. |

---

### 🚨 Failure Modes & Diagnosis

**Missing Traces in Jaeger Under High Load**

**Symptom:** During high traffic, trace queries in
Jaeger show no results for recent requests. Metrics
show normal traffic. Services are functioning.

**Root Cause:** Span exporter is dropping spans due
to queue saturation. The BatchSpanProcessor queue
is full (default: 2048 pending spans). When full,
new spans are silently dropped.

**Diagnosis:**
```python
# Check OpenTelemetry SDK span drop metrics:
# otelcol_processor_dropped_spans (in OTEL Collector)
# exporter_queue_size (in OTEL SDK metrics)

# Example: expose SDK metrics and check:
from opentelemetry.sdk.metrics import MeterProvider
from prometheus_client import start_http_server

# Monitor in Prometheus:
# rate(otelcol_exporter_send_failed_spans[5m]) > 0
# → Spans are being dropped at exporter

# Quick check: reduce sampling to reduce volume:
# Or: increase BatchSpanProcessor queue and workers:
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor
)
BatchSpanProcessor(
    exporter,
    max_queue_size=8192,       # Default: 2048
    max_export_batch_size=512, # Default: 512
    export_timeout_millis=10000 # Default: 30000
)
```

**Fix:**
1. Reduce trace sampling rate (head-based).
2. Increase BatchSpanProcessor queue size.
3. Scale the OpenTelemetry Collector.
4. Ensure Jaeger/Tempo backend is not overloaded.

---

### 🔗 Related Keywords

**Prerequisites:** `Health Checks and Readiness Probes`
(DST-019), `Rate Limiting` (DST-025)

**Builds On This:** `Production Diagnosis Toolkit`
(DST-069), `Production Incident Simulation` (DST-070)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ THREE PILLARS                                           │
│  Metrics: aggregate numbers over time (alert)          │
│  Logs: per-event records (debug)                       │
│  Traces: end-to-end request paths (latency)            │
├────────────┬────────────────────────────────────────────┤
│ TRACE IDs  │ Every request → unique trace_id           │
│            │ Propagate via HTTP header: traceparent    │
│            │ All spans share trace_id                 │
├────────────┼────────────────────────────────────────────┤
│ SAMPLING   │ 1% head-based + 100% error tail-based     │
│ STANDARD   │ OpenTelemetry (OTEL) - instrument once    │
├────────────┼────────────────────────────────────────────┤
│ BACKENDS   │ Jaeger/Zipkin (traces), Prometheus         │
│            │ (metrics), Loki/ELK (logs)               │
├────────────┼────────────────────────────────────────────┤
│ ONE-LINER  │ "Metrics alert, logs explain, traces find │
│            │  which service and why."                 │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

Observability teaches the discipline of designing
systems that can explain themselves. A system that
can explain its own behavior is far more maintainable
and debuggable than one that is a black box. This
principle extends beyond distributed systems:
functions should return meaningful errors (not just
"error"), APIs should include request IDs in all
responses, databases should expose query plans and
slow query logs, and message queues should surface
consumer lag. The observability mindset: every time
you write code, ask "if this breaks at 2am, will I
be able to tell which line, which service, and
which input caused it?" If not, add instrumentation.
The cost of observability is paid once at development
time; the benefit is paid every time something goes
wrong in production.

---

### 💡 The Surprising Truth

The term "observability" in distributed systems was
popularized by the paper "Distributed Systems
Observability" (Charity Majors, Liz Fong-Jones,
George Miranda, 2018) at Honeycomb.io. The core
insight that distinguished it from traditional
monitoring: traditional monitoring is about checking
known-failure modes (threshold alerts). True
observability allows you to ask ARBITRARY questions
about production state that you never anticipated
needing to ask. This requires high-cardinality data
(trace data with user_id, order_id, feature_flag
dimensions) - which is exactly what traditional
monitoring tools (time-series databases like
Prometheus) cannot efficiently handle. The emergence
of purpose-built observability backends (Honeycomb,
Grafana Tempo, Jaeger) was a direct response to this
limitation.

---

### ✅ Mastery Checklist

1. [IMPLEMENT] Instrument a two-service HTTP
   interaction with OpenTelemetry: propagate the
   trace context in headers, create child spans in
   both services, verify the trace appears in Jaeger.
2. [DESIGN] For a checkout service with 8 downstream
   dependencies, design the sampling strategy:
   what sampling rate for normal traffic, errors,
   and high-latency requests?
3. [COMPARE] A service's P99 latency alert fires.
   Walk through using all three pillars in sequence:
   metrics first, then logs, then traces. What does
   each pillar tell you that the others cannot?
4. [DIAGNOSE] Traces are missing from Jaeger during
   high traffic. Identify the likely cause and the
   fix.
5. [EXPLAIN] What is the difference between
   observability and monitoring? Give a concrete
   example where monitoring is insufficient but
   observability solves the problem.
