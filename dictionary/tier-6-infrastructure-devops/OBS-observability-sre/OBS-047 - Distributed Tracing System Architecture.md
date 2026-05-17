---
id: OBS-047
title: Distributed Tracing System Architecture
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★★
depends_on: OBS-001, OBS-008, OBS-017, OBS-015, OBS-039, OBS-041
used_by: OBS-045
related: OBS-044, OBS-046, OBS-053
tags:
  - observability
  - reliability
  - devops
  - sre
  - advanced
  - architecture
  - distributed-tracing
  - production
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 47
permalink: /obs/distributed-tracing-system-architecture/
---

# OBS-047 - Distributed Tracing System Architecture

⚡ TL;DR - A distributed tracing system consists of four
layers: instrumentation (OTel SDK injecting trace context
into every request), collection (OTel Collector fan-in),
storage (Tempo/Jaeger writing spans to object storage
indexed by bloom filter), and query (TraceQL/trace ID
lookup with exemplar links from metrics).

| #047            | Category: Observability & SRE                                                                                                   | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | What Is Observability, Distributed Tracing, OpenTelemetry, Grafana, Observability at Scale, Observability Platform Architecture |                 |
| **Used by:**    | Observability System Design Internals                                                                                           |                 |
| **Related:**    | Platform Observability Engineering, Time-Series Database Design, Service Level Objectives Deep Dive                             |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A user reports that checkout was slow for 8 seconds. Your
Grafana dashboard shows a p99 latency spike of 8 seconds
starting at 14:32. You have 8 services involved in
checkout. Which service was slow? You look at each service's
latency dashboard individually. All show normal latency.
How? The 8 seconds of latency must be hiding somewhere
but each service looks fine in isolation. After 2 hours
of investigation, you discover the latency is in the
sequential waiting time between services (a callback
chain with 6 sequential HTTP calls, each normal, but
6 × 1.3s = 7.8s total). Without tracing, this was
invisible - each service was performing normally in
isolation but the composition was broken.

**THE BREAKING POINT:**
Metrics and logs are per-service signals. They cannot
show you the execution path across services for a single
request. At 8 services, cross-service latency composition
is invisible without distributed tracing. At 50 services,
diagnosing any cross-service issue without tracing takes
hours or is impossible.

**THE INVENTION MOMENT:**
Distributed tracing was introduced by Google's Dapper
system (2010 paper), which proposed propagating a trace
context (trace ID + span ID) through every service call.
Each service records a "span" containing its local timing
and links to its parent span. After the request completes,
all spans from all services are assembled into a trace
tree that shows the full execution path, timing of every
hop, and where time was spent. This makes cross-service
latency visible.

**EVOLUTION:**
Dapper inspired Zipkin (Twitter, open-source 2012),
Jaeger (Uber, open-source 2017), and OpenTelemetry (CNCF,
merged OpenCensus + OpenTracing 2019). OTel became the
standard API; backends (Jaeger, Zipkin, Tempo) became
pluggable. Tempo (Grafana Labs, 2020) introduced object-
storage-first trace backend that scales to billions of
traces without Elasticsearch (the previous common backend,
expensive at scale).

---

### 📘 Textbook Definition

A **distributed tracing system** is an observability
system that records the execution path of individual
requests across multiple services (a "trace"), where each
service's contribution is recorded as a "span" (a named,
timed operation with start time, end time, tags, and a
link to its parent span). The system consists of:
(1) **instrumentation** - SDK code that creates spans,
injects trace context into outbound requests, and reports
span data; (2) **propagation** - the W3C TraceContext header
(or B3) that carries trace ID + parent span ID across
service calls; (3) **collection** - the pipeline that
receives spans from all services and routes them to storage;
(4) **storage** - the backend that stores spans indexed
for fast lookup by trace ID; (5) **query** - the interface
for finding and visualizing traces.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Distributed tracing follows a single request through
every service it touches and records a timeline of every
operation, making cross-service latency visible.

**One analogy:**

> Distributed tracing is like a flight's journey log for
> a package in a courier network. The package gets a
> tracking number (trace ID) at the first sorting center.
> Every sorting center, transfer flight, and delivery van
> stamps its "received at X, handed to Y at time T" record
> with reference to the tracking number. At the end, the
> full journey is visible: sorted at Chicago (2h), on
> flight AA123 (4h), at Denver hub (1h), local delivery
> (30min). Without the tracking number propagated through
> every hop, each facility would have records of packages
> but could not assemble the journey of any specific package.

**One insight:**
The critical insight in distributed tracing architecture
is that spans are recorded locally by each service but
must be assembled into a tree globally. This creates a
design constraint: spans from a single trace are written
by different services at different times and stored
independently. The trace query layer must reassemble
them by trace ID. The bloom filter indexing approach
(Tempo) is the key innovation that makes trace ID lookup
O(log n) across petabytes of span data without requiring
a centralized index.

---

### 🔩 First Principles Explanation

**THE TRACE DATA MODEL:**

```
Trace (one per request):
  trace_id: a128-bit random ID, same for all spans
  spans: array of Span objects

Span (one per service boundary / operation):
  span_id: 64-bit random ID, unique per span
  parent_span_id: span_id of the caller (nil for root)
  trace_id: same as parent trace
  name: operation name (e.g., "payment.process")
  service_name: which service generated this span
  start_time: Unix timestamp (nanoseconds)
  end_time: Unix timestamp (nanoseconds)
  status: OK | ERROR | UNSET
  attributes: key-value pairs (user_id, db.name, etc.)
  events: timestamped log messages within the span
  links: cross-trace references (e.g., async messaging)

TREE STRUCTURE:
  Frontend (root span, 8.2s)
    └── APIGateway (1.1s)
          ├── AuthService (0.2s)
          └── CheckoutService (6.8s)
                ├── InventoryService (0.3s)
                └── PaymentService (6.3s)   ← slow!
                      └── DB call (6.1s)    ← root cause
```

**CONTEXT PROPAGATION:**

```
HTTP request flow:
  Frontend sends to APIGateway:
    Header: traceparent: 00-TRACEID-SPANID-01
    (W3C TraceContext format)

  APIGateway reads header:
    - Extracts trace_id and parent_span_id
    - Creates its own span (with parent = frontend span)
    - Passes new traceparent to CheckoutService:
      traceparent: 00-TRACEID-APIGATEWAY_SPANID-01

  Each service continues the chain.

  This propagation is automatic with OTel auto-instrumentation
  for HTTP clients/servers, gRPC, AMQP, Kafka.
```

**SAMPLING:**

```
Problem: 1000 RPS × 50 spans/trace × 500 bytes/span
  = 25 MB/s of span data unsampled
  Annual storage: ~800 TB - expensive

Solutions:
  1. Head-based sampling (probabilistic at root span):
     Record only N% of traces. Simple, low overhead.
     Problem: does not guarantee capturing slow or error traces.

  2. Tail-based sampling (at collector, after all spans arrive):
     Wait until the full trace is assembled, then decide:
     - If any span has error status → keep
     - If root span duration > 1s → keep
     - Otherwise: sample at 1% rate → keep
     Captures ALL interesting traces, discards routine fast ones.
     Problem: requires buffering the full trace in memory at
     the collector (seconds to minutes) before deciding.

  3. Exemplars (linked from metrics):
     Sample 1 trace per histogram bucket per metric evaluation.
     These traces are always kept because they are reference
     examples tied to specific metric anomalies.
```

---

### 🧪 Thought Experiment

**DESIGN: trace storage for 100M traces/day**

```
Data volume:
  100M traces/day × 50 spans/trace × 500 bytes/span
  = 2.5 TB/day uncompressed

  With zstd compression (~3:1 for JSON span data):
  ~830 GB/day compressed

  S3 cost ($0.023/GB/month):
  90 days × 830 GB/day = 74.7 TB
  74.7 TB × $0.023 = $1,718/month

Query pattern:
  - 99% of queries: find trace by exact trace ID
    (user reports a problem, gives their session ID
    → resolve to trace ID → load full trace)
  - 1% of queries: "all slow traces in last 1 hour"
    (wide queries for analysis / SLO review)

Index design for trace ID lookup:
  Bloom filter per 1-hour block:
    - Each block: 100M traces/24h × 50 spans = 208K spans
    - Bloom filter for 208K trace IDs at 1% FPR:
      needs ~2M bits = 250KB per block
    - 24 blocks/day × 250KB = 6MB of bloom filter index per day
    - 90 days: 540MB of bloom filter index in RAM
    - FAST: check 90 bloom filters to find which block
      contains trace ID → O(1) effective lookup

Wide query design:
  "All traces with span.duration > 5s in last 1 hour"
  → Must scan all blocks in the 1-hour range
  → 208K spans per block
  → 1 block per hour
  → Read 1 block: 830GB/24 = 35GB per block
  → At S3 throughput ~500MB/s: 70 seconds
  → This is slow - TraceQL pipelining mitigates with parallelism
```

---

### 🧠 Mental Model / Analogy

> The distributed tracing system is like a network of
> CCTV cameras in a shopping mall, tied together by
> customer tracking. Each camera (service) records all
> activity in its area (spans). Each customer gets a
> loyalty card (trace ID) that is scanned at every camera.
> After a customer reports a problem ("my wallet was stolen
> at 3pm"), security can replay the exact journey of that
> specific customer through every camera: entered at Door 1
> (2:47pm), walked past Camera 3 (2:52pm), was near Camera 7
> at 2:58pm where the theft occurred. Without the loyalty
> card (trace ID) linking the cameras, security would see
> thousands of separate camera feeds with no way to follow
> a specific person's journey.

Where this analogy breaks down: CCTV stores continuous
video (high volume, continuous); distributed tracing
stores discrete span events (lower volume, event-driven).
The sampling challenge (keeping only 1% of traces) has
no direct analog in CCTV (you don't delete 99% of footage).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Distributed tracing follows a single user request through
all the services it touches and records how long each
service took. This makes it possible to identify exactly
which service is slow when an overall request takes too long.

**Level 2 - How to use it (junior developer):**
Add the OTel SDK to your service. The auto-instrumentation
handles context propagation for HTTP and gRPC automatically.
Add custom spans for important business operations. Use
Jaeger or Grafana Tempo to view traces. When debugging
latency issues, find the trace for the slow request and
look at which span took the most time.

**Level 3 - How it works (mid-level engineer):**
Each service creates a span when a request enters, adds
timing and tags, and links it to the parent span via the
W3C traceparent header. Spans are sent to the OTel Collector
which buffers and routes them to Tempo/Jaeger. At query
time, Tempo loads trace data from S3 using bloom filter
indexes to locate the correct storage block for a given
trace ID. The Grafana UI assembles spans into a waterfall
view and links them to correlated metrics and logs.

**Level 4 - Why it was designed this way (senior/staff):**
The key architectural tension is between head-based and
tail-based sampling. Head-based (decide at the first service
whether to trace) is simple and low overhead but loses
visibility into the rare slow or error traces. Tail-based
(decide after all spans arrive at the collector) ensures
all interesting traces are captured but requires the
collector to buffer entire traces in memory - adding latency
to the trace storage pipeline and requiring significant
collector memory for high-throughput services. Most
production systems use a combination: always capture errors
(tail-based rule), sample N% of normal traces (head-based),
keep all exemplar traces linked from SLO metrics.

**Level 5 - Mastery (distinguished engineer):**
Trace data volumes are bounded by request rate (not metric
cardinality), but even at 1000 RPS, unsampled trace data
generates 25 MB/s. The storage architecture must balance
three forces: completeness (tail-based sampling for
important traces), cost (aggressive sampling for routine
traces), and query performance (bloom filter indexes for
trace ID lookups, TraceQL for content search). The exemplar
model (Prometheus links a metric histogram bucket to a
specific trace via exemplar) is the highest-ROI integration
point because it connects the broad signal (metric anomaly
visible to all services) to the specific example (one trace
showing the actual failure path). This reduces investigation
from "scan all traces for this time period" to "look at
this specific trace linked from the p99 histogram bucket."

---

### ⚙️ How It Works (Mechanism)

**SPAN LIFECYCLE:**

```
1. Request arrives at ServiceA
   OTel SDK auto-instrumentation intercepts:
   - Read traceparent header (if present)
   - If present: extract trace_id, parent_span_id
   - If absent: generate new trace_id, no parent (root span)
   - Create span: {trace_id, span_id=new_64bit_random,
                   parent_span_id, service="serviceA",
                   name="GET /checkout", start=now()}

2. ServiceA calls ServiceB
   OTel HTTP client interceptor:
   - Inject traceparent header with:
     trace_id=same, parent_span_id=serviceA_span_id
   - ServiceB receives and creates child span

3. ServiceA request completes
   OTel SDK:
   - Set span end_time
   - Set span status (OK or ERROR with description)
   - Export span to OTel Collector (OTLP gRPC)

4. OTel Collector
   Receives spans from multiple services
   - Enriches with k8s metadata (pod, node, namespace)
   - If tail-based sampling: buffer in memory, evaluate
     trace completeness after N seconds
   - If head-based: forward all spans matching sample decision
   - Forward to Tempo (OTLP endpoint)

5. Tempo storage
   - Write spans to local WAL (fast, durable)
   - Flush to S3 as a block every N minutes
   - Block contains: spans (Parquet) + bloom filter index
   - Bloom filter covers all trace IDs in this block

6. Grafana query
   - User enters trace_id in Explore view
   - Tempo: check bloom filter for each block
   - Load chunks from blocks where bloom filter matches
   - Assemble trace tree from spans
   - Render waterfall chart
```

**TEMPO BLOCK LAYOUT:**

```
s3://trace-bucket/tempo/
  tenant-id/
    blocks/
      01HB234/
        meta.json        (block metadata, time range)
        bloom-0.bin      (bloom filter shard 0)
        bloom-1.bin      (bloom filter shard 1)
        ...
        bloom-255.bin    (256 shards, ~ 1KB each)
        data/
          00000001       (Parquet span data)
          00000002
          ...

Query for trace ID "abc123ef...":
  1. Compute shard: bloom_shard = trace_id[0] (first byte)
  2. For each block: read bloom-{shard}.bin
     Check if "abc123ef..." is in this shard's bloom filter
  3. For blocks where bloom says YES (or maybe):
     Read Parquet data, scan for exact trace_id match
  4. Fetch all spans with matching trace_id
  5. Assemble into trace tree and return
```

---

### 🔄 The Complete Picture - End-to-End Flow

**FULL TRACE INVESTIGATION FLOW:**

```
Incident: p99 checkout latency = 8s (SLO: < 1s)
   │
   ↓
Step 1: Metric → Exemplar
  In Grafana: click the p99 spike on checkout latency chart
  Prometheus exemplar shows: trace_id=abc123ef
  (Exemplar = a specific trace linked to this histogram bucket)
   │
   ↓
Step 2: Load trace
  Grafana → Tempo: GET /api/traces/abc123ef
  Tempo: bloom filter lookup → fetch from S3
  Return: 47 spans from 8 services, 8.2s total duration
   │
   ↓
Step 3: Identify slow span
  Waterfall view: PaymentService.processPayment = 6.3s
  Child span: DB.query("SELECT ... FROM payments") = 6.1s
   │
   ↓
Step 4: Correlate logs
  Click "Logs" button on DB.query span
  Grafana: Loki query {app="payment-service"}
          | trace_id="abc123ef"
  Returns: "DB connection pool exhausted, waited 6.1s"
   │
   ↓
Step 5: Confirm scope with metrics
  Prometheus: payment_service_db_pool_wait_seconds{quantile="0.99"}
  Shows: p99 wait = 6.2s for last 30 minutes
  Prometheus: payment_service_db_pool_used / total
  Shows: 100% pool utilization for 30 minutes
   │
   ↓
Root cause: DB connection pool size too small for load spike
Fix: increase pool size from 10 to 50 connections
Investigation time: 11 minutes
Enabled by: exemplar → trace → log correlation → metric scope
```

---

### 💻 Code Example

**Example 1 - BAD: no context propagation (traces broken)**

```java
// BAD: custom HTTP client without trace propagation
// All downstream calls appear as new root spans
// The trace tree is fragmented - can't see full request path

@Service
public class CheckoutService {
    public CheckoutResult checkout(CheckoutRequest req) {
        // Manual HTTP call without OTel instrumentation
        // trace context is NOT injected in headers
        HttpResponse response = httpClient.post(
            "http://payment-service/process",
            req.getPaymentDetails()
        );
        // PaymentService sees no traceparent header
        // Creates a new root span instead of child span
        // The checkout trace has no visibility into
        // what payment-service did for this request
        return parse(response);
    }
}
```

**Example 2 - GOOD: OTel auto-instrumented HTTP client**

```java
// GOOD: OTel auto-instrumentation handles propagation
// Auto-instrumentation wraps all HTTP clients on startup
// Manual span added only for custom business logic

@Service
public class CheckoutService {
    // OTel Tracer for custom business spans
    private final Tracer tracer = GlobalOpenTelemetry
        .getTracer("checkout-service");

    public CheckoutResult checkout(CheckoutRequest req) {
        // OTel auto-instrumentation intercepts this call:
        // reads traceparent from incoming request,
        // creates "CheckoutService.checkout" span as child

        // Custom span for business-level operation
        Span span = tracer.spanBuilder("validate_cart")
            .setAttribute("cart.items", req.getItems().size())
            .setAttribute("cart.value", req.getTotalValue())
            .startSpan();

        try (Scope scope = span.makeCurrent()) {
            validateCart(req.getItems());

            // OTel HTTP client auto-instrumentation:
            // injects traceparent with current span as parent
            // Payment service receives and creates child span
            HttpResponse response = restTemplate.postForObject(
                "http://payment-service/process",
                req.getPaymentDetails(),
                HttpResponse.class
            );

            span.setStatus(StatusCode.OK);
            return parse(response);
        } catch (Exception e) {
            span.setStatus(StatusCode.ERROR, e.getMessage());
            span.recordException(e);
            throw e;
        } finally {
            span.end();
        }
    }
}
```

**Example 3 - Tail-based sampling in OTel Collector**

```yaml
# OTel Collector config with tail-based sampling
# Ensures ALL errors and slow traces are captured
# while sampling only 1% of fast, successful traces

processors:
  tail_sampling:
    decision_wait: 10s # Wait 10s for trace to complete
    num_traces: 100000 # Buffer up to 100K traces in memory
    expected_new_traces_per_sec: 1000
    policies:
      # Always keep traces with errors
      - name: error_policy
        type: status_code
        status_code:
          status_codes: [ERROR]

      # Always keep slow traces (p99 SLO target is 1s)
      - name: slow_trace_policy
        type: latency
        latency:
          threshold_ms: 1000

      # Always keep traces with business-critical events
      - name: payment_failure_policy
        type: string_attribute
        string_attribute:
          key: payment.status
          values: [DECLINED, FAILED, TIMEOUT]

      # Sample 1% of remaining routine traces
      - name: sample_policy
        type: probabilistic
        probabilistic:
          sampling_percentage: 1
```

**Example 4 - FAILURE: trace context lost across Kafka**

```
Symptom:
  Traces for async order processing are fragmented.
  The producer span (OrderService sends to Kafka)
  and consumer span (FulfillmentService processes)
  appear as separate unlinked traces.
  Cannot determine which fulfillment operation
  corresponds to which order submission.

Root Cause:
  OrderService sends to Kafka without trace headers:
    producer.send(new ProducerRecord("orders", payload));
  FulfillmentService has no traceparent to extract.
  Creates a new root span on every message consumption.
  Traces are disconnected: no link between order and fulfillment.

Fix:
  Use OTel Kafka instrumentation that auto-injects
  trace context as Kafka message headers:

// Producer (auto-instrumented, no manual code needed
// if using opentelemetry-kafka-clients artifact):
producer.send(new ProducerRecord("orders", payload));
// OTel auto-instrumentation adds:
// header: traceparent=00-TRACEID-SPAN_ID-01

// Consumer (auto-instrumented):
ConsumerRecord<K,V> record = consumer.poll(...).first();
// OTel extracts traceparent from record.headers()
// Creates span as child of producer's span
// Even though they are in different processes/times,
// the trace tree is linked via the span link

  Result: Full trace from order submission through
  fulfillment visible in one trace tree (via span links)
```

---

### ⚖️ Comparison Table

| Backend           | Storage Model                      | Scale                | Query Language      | Cost                |
| ----------------- | ---------------------------------- | -------------------- | ------------------- | ------------------- |
| **Grafana Tempo** | Object storage (S3)                | Horizontal (sharded) | TraceQL             | Very low ($)        |
| **Jaeger**        | Cassandra / Elasticsearch / Badger | Moderate             | Jaeger UI (limited) | Medium ($$)         |
| **Zipkin**        | Cassandra / Elasticsearch          | Moderate             | Zipkin UI (limited) | Medium ($$)         |
| **AWS X-Ray**     | Managed (proprietary)              | Managed              | X-Ray Analytics     | Low (pay-per-trace) |
| **Honeycomb**     | Proprietary columnar               | Very high            | BQL (powerful)      | High ($$$)          |

**How to choose:**
Use Tempo for cost-effective self-hosted tracing (especially
in the Grafana stack with Loki and Prometheus). Use Jaeger
for teams already using Elasticsearch (reuse existing
cluster). Use Honeycomb when you need powerful column-based
queries across trace data beyond simple trace ID lookup.

---

### ⚠️ Common Misconceptions

| Misconception                                              | Reality                                                                                                                                                                             |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Distributed tracing requires sampling from day one         | Start with 100% sampling at low volume; implement tail-based sampling when ingestion cost becomes material. Starting with head-based sampling often means missing critical traces   |
| All spans in a trace arrive together                       | Spans arrive independently from different services; the collector must buffer and wait for the trace to be "complete" (configurable timeout) before making a tail-sampling decision |
| Trace context propagation requires changes to all services | OTel auto-instrumentation handles propagation for HTTP, gRPC, Kafka, and many other protocols automatically - no code changes required for standard clients                         |
| Tempo only supports trace ID lookup                        | TraceQL (introduced in Tempo 2.0) supports content-based queries: find all traces where a span attribute matches a condition, with arbitrary filters across trace data              |

---

### 🚨 Failure Modes & Diagnosis

**Broken Trace Tree (spans appear disconnected)**

**Symptom:**
A trace for a checkout request shows only the first
service's span. All other service spans are separate
unlinked traces with new trace IDs. Grafana shows dozens
of 1-span traces per checkout instead of one 50-span trace.

**Root Cause (most common):**
Context propagation is broken at one service boundary.
This usually means: (1) the HTTP client in one service
is not OTel-instrumented (doesn't inject traceparent
header), OR (2) a load balancer or API gateway is stripping
custom headers before forwarding to the service.

**Diagnostic:**

```bash
# Check if traceparent header reaches the service
kubectl exec -n production payment-service-pod -- \
  curl -v http://checkout-service:8080/health 2>&1 \
  | grep -i traceparent
# If no traceparent in response headers:
# The service is not generating spans

# Check if OTel agent is attached
kubectl describe pod checkout-service-pod | \
  grep -i OTEL
# Look for: OTEL_EXPORTER_OTLP_ENDPOINT env var
# If absent: auto-instrumentation is not configured
```

**Fix:**
Add OTel Java agent as JVM argument:

```yaml
# k8s deployment env for Java services
env:
  - name: JAVA_TOOL_OPTIONS
    value: "-javaagent:/otel-agent/opentelemetry-javaagent.jar"
  - name: OTEL_EXPORTER_OTLP_ENDPOINT
    value: "http://otel-collector:4317"
  - name: OTEL_SERVICE_NAME
    valueFrom:
      fieldRef:
        fieldPath: metadata.labels['app']
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `What Is Observability` - the three pillars tracing supports
- `Distributed Tracing` - the concepts before the system design
- `OpenTelemetry` - the standard API for tracing instrumentation
- `Grafana` - the primary query interface for traces
- `Observability at Scale` - the scaling problems trace sampling solves
- `Observability Platform Architecture Design` - where tracing fits in the platform

**Builds On This (learn these next):**

- `Observability System Design Internals` - the full system
  combining trace with metric and log internals

**Alternatives / Comparisons:**

- `Platform Observability Engineering` - running the trace
  system as part of the platform product
- `Time-Series Database Design` - comparable storage design
  for metric data
- `Service Level Objectives Deep Dive` - how exemplars link
  SLO metrics to specific traces

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ WHAT IT IS    │ System that records execution path of │
│               │ individual requests across all services│
│               │ and stores it for fast retrieval      │
├───────────────┼────────────────────────────────────────┤
│ DATA MODEL    │ Trace = tree of Spans. Span = (service,│
│               │ operation, start, end, attributes,    │
│               │ parent_span_id). Linked by trace_id   │
├───────────────┼────────────────────────────────────────┤
│ PROPAGATION   │ W3C traceparent header carries         │
│               │ trace_id + parent_span_id across HTTP,│
│               │ gRPC, Kafka. OTel auto-instruments all │
├───────────────┼────────────────────────────────────────┤
│ SAMPLING      │ Head-based: decide at root (simple,   │
│               │ misses rare errors). Tail-based: decide│
│               │ after all spans arrive (captures all  │
│               │ errors/slow, requires collector buffer)│
├───────────────┼────────────────────────────────────────┤
│ STORAGE       │ Tempo: S3-first, bloom filter per block│
│               │ for trace-ID O(1) lookup. TraceQL for  │
│               │ content queries (slow, full scan)      │
├───────────────┼────────────────────────────────────────┤
│ CORRELATION   │ Exemplars: Prometheus → trace ID link  │
│               │ trace_id in logs → Loki → trace join   │
├───────────────┼────────────────────────────────────────┤
│ ONE-LINER     │ "Trace is the surgical tool: metrics  │
│               │ show the anomaly, traces show the exact│
│               │ request that had the problem."         │
├───────────────┼────────────────────────────────────────┤
│ NEXT EXPLORE  │ Observability System Design Internals  │
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Trace context propagation is the fundamental mechanism:
   trace_id + parent_span_id propagated via W3C traceparent
   header through every service boundary. If propagation
   breaks at any hop, the trace tree is fragmented.
2. Tail-based sampling is the correct approach for production:
   buffer all spans for a trace for N seconds, then decide
   to keep or drop based on whether any span has an error
   or exceeds latency thresholds. Head-based sampling loses
   the rare but important traces.
3. Exemplars are the most valuable metric-trace integration:
   a Prometheus exemplar links a specific histogram bucket
   observation to a trace ID, turning "the p99 spiked"
   into "here is a specific trace showing why it spiked."

**Interview one-liner:**
"Distributed tracing system has four layers: instrumentation
(OTel SDK creates spans, propagates W3C traceparent header),
collection (OTel Collector with tail-based sampling - buffer
N seconds, keep all errors/slow traces, sample 1% of routine),
storage (Tempo: S3-backed blocks with bloom filter per block
for O(log n) trace-ID lookup, TraceQL for content queries),
and correlation (Prometheus exemplars link metric anomalies
to specific traces; trace_id in logs links traces to log lines).
Most broken traces are caused by context propagation failures
at service boundaries, usually missing OTel auto-instrumentation."

> Entry stub. Generate full content using Master Prompt v3.0.
