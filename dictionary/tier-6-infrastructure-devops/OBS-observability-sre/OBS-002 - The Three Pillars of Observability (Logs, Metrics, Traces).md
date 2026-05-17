---
id: OBS-002
title: "The Three Pillars of Observability (Logs, Metrics, Traces)"
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★☆☆
depends_on: OBS-001
used_by: OBS-007, OBS-006, OBS-008
related: OBS-001, OBS-017, OBS-019
tags:
  - observability
  - reliability
  - foundational
  - mental-model
  - devops
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 2
permalink: /obs/the-three-pillars-of-observability-logs-metrics-traces/
---

# OBS-002 - The Three Pillars of Observability (Logs, Metrics, Traces)

⚡ TL;DR - Logs record what happened, metrics measure how
much and how fast, and traces follow a request through every
service - together they answer any production question.

| #002            | Category: Observability & SRE                                                            | Difficulty: ★☆☆ |
| :-------------- | :--------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | What Is Observability and Why It Matters                                                 |                 |
| **Used by:**    | Logging Fundamentals, Metrics - Types, Distributed Tracing Fundamentals                  |                 |
| **Related:**    | What Is Observability and Why It Matters, Prometheus - Metrics Collection, ELK/EFK Stack |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before the three-pillar model was articulated, teams used
whatever tools were available: application logs in flat files,
server-level metrics from Nagios, and nothing resembling
distributed tracing. When a request was slow, engineers ran
`grep` over gigabytes of unstructured logs across a dozen
servers, looking for anything suspicious. Correlating a single
user's request across six microservices was a multi-hour manual
exercise involving timestamps, server hostnames, and educated
guesses.

**THE BREAKING POINT:**
Three classes of question emerge in every production incident,
and no single signal type answers all three:

- "What happened?" (events, state changes, errors)
- "How much, how fast, how often?" (rates, percentiles, counts)
- "Which exact request, through which exact path?" (causality)

Without a framework that separates these concerns, engineers
mix signals into one giant log stream, use metrics for things
that need traces, or add traces where metrics were sufficient.
The result: an expensive, inefficient, and still-incomplete
picture of what the system is doing.

**THE INVENTION MOMENT:**
This is exactly why the three-pillar model was created - to
give engineers a clear mental taxonomy: three signal types,
each optimised for a different class of question, all emitted
by the same system, all correlated by a shared identifier.

**EVOLUTION:**
Peter Bourgon's 2017 article "Metrics, Tracing, and Logging"
first articulated the three pillars as distinct, complementary
concerns. The Google SRE book (2016) covered metrics and logs
implicitly. OpenTelemetry (2019-2023) unified all three under
one SDK, one collector, and one wire protocol - marking the
maturation of the model from framework to industry standard.

---

### 📘 Textbook Definition

The **three pillars of observability** are the three canonical
signal types that a software system emits to make its internal
state observable: **logs** (timestamped records of discrete
events), **metrics** (numeric measurements aggregated over
time), and **traces** (causal chains of spans representing a
single request's path through a distributed system).

Each pillar is independently useful and independently
queryable. Together, correlated by a shared trace ID, they
provide complete coverage of any production question: what
happened, how severe, and where exactly.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Three different lenses on the same system - logs for events,
metrics for trends, traces for causality.

> A hospital uses three types of records for each patient: the
> event log (nurse's notes - "patient complained of pain at
> 14:32"), the vital signs chart (metrics - heart rate 72,
> oxygen 98% over time), and the care pathway (trace - who
> ordered what, when, what happened next). Each answers a
> different question. Together they tell the complete story.

**One insight:**
The pillars are not redundant - they are complementary. Metrics
tell you something is wrong. Logs tell you what happened.
Traces tell you exactly which request, through which path,
caused it. Missing any one pillar leaves a class of questions
permanently unanswerable.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Events (logs) are discrete and have infinite cardinality -
   each event is unique and contains arbitrary key-value fields
2. Measurements (metrics) must be pre-aggregated to be scalable
   - you cannot store one data point per request at 100k rps
3. Causality (traces) requires context propagation across
   process boundaries - a trace only exists if every service
   participates in passing the trace ID forward
4. All three share a common coordinate: the timestamp and the
   trace ID, which link them together for a specific request

**DERIVED DESIGN:**
Because logs are verbose and expensive, they are filtered and
sampled. Because metrics are cheap, they are kept at full
fidelity. Because traces require coordination, they have the
highest instrumentation cost but the highest diagnostic value
for distributed systems. Optimising each pillar independently
while sharing the trace ID as a join key is the core design
insight of the three-pillar model.

**THE TRADE-OFFS:**
**Gain:** Complete coverage - every class of production
question is answerable from one of the three pillars.
Specialised storage and query engines optimised for each type.
**Cost:** Three backends to operate (TSDB, log store, trace
store). Three instrumentation models. Three query languages
(PromQL, Lucene/LogQL, Jaeger trace search). Integration
complexity between them.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** The three signal types are genuinely different
in their information density, cardinality, and query model.
Any unified observability system must reconcile these
differences.
**Accidental:** The fact that Prometheus uses PromQL, Loki
uses LogQL, and Jaeger has its own UI is an accident of
independent evolution. OpenTelemetry is working to reduce
this fragmentation.

---

### 🧪 Thought Experiment

**SETUP:**
A payment service processes 10,000 transactions per minute.
At 3 PM, the error rate rises from 0.1% to 3%. The on-call
engineer has all three pillars available.

**WHAT HAPPENS WITHOUT TRACES (logs + metrics only):**
Metrics show the error rate spike. Log search for `ERROR`
returns 18,000 lines. The errors say "database timeout." But
which code path? Which query? The engineer reads logs for
45 minutes. They narrow it down to the `/refund` endpoint
but cannot see why database calls from that endpoint are slow
when `/purchase` is fast. They cannot see that `/refund` calls
a third service that is the actual bottleneck.

**WHAT HAPPENS WITH ALL THREE PILLARS:**
Metrics show the error rate spike - the engineer knows WHAT
and WHEN. Log search for the error message in that time window
returns structured events with trace IDs. They pick one trace
ID, open it in Jaeger: the trace shows `/refund` calling the
`fraud-check` service, which is calling the `rule-engine`
service, which is making a slow Redis call. Total path visible
in 30 seconds. Fix identified in under 3 minutes.

**THE INSIGHT:**
Each pillar answers a different question in sequence: metrics
trigger the investigation, logs narrow the context, traces
reveal the causal path. Removing any one pillar breaks the
diagnostic chain.

---

### 🧠 Mental Model / Analogy

> A detective solving a crime uses three types of evidence.
> The case file (logs) records every event: "Witness saw
> suspect at 9:15 PM near the vault." The statistics board
> (metrics) shows patterns: "Break-ins spike on Fridays between
> 8 PM and midnight." The surveillance footage (traces) shows
> the exact sequence: who entered which door, at what time, in
> what order, and where they went next.

Mapping:

- "Case file / witness notes" - logs (discrete events, context)
- "Statistics board / crime pattern analysis" - metrics
  (aggregated measurements, trends, rates)
- "Surveillance footage with timestamps" - distributed traces
  (causal chains, service-to-service paths)
- "Case number linking all evidence" - the trace ID

**Where this analogy breaks down:** A detective works
retrospectively. Observability must work in real time, and
the "surveillance footage" (traces) is only as good as the
instrumentation deployed before the incident - you cannot
go back and add cameras after a crime occurs.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Three types of data your software emits: event records (logs),
numeric measurements (metrics), and request flow maps
(traces). Each answers a different question when something
goes wrong.

**Level 2 - How to use it (junior developer):**
Use logs for debugging specific events (what error message
appeared, in which function, for which user). Use metrics for
dashboards and alerts (error rate, request rate, latency
histogram). Use traces to follow a single request through all
services and see which step is slow.

**Level 3 - How it works (mid-level engineer):**
All three share a trace ID as a correlation key. When Service A
handles a request, it creates a trace ID, logs it in structured
fields, records it as a metric exemplar, and propagates it as
a span context header to Service B. When an incident occurs,
you start with a metric alert, search logs by trace ID for
the time window, then open the trace in Jaeger for the causal
path. The three pillars form a funnel: metrics detect, logs
contextualise, traces explain.

**Level 4 - Why it was designed this way (senior/staff):**
Each pillar has a fundamentally different cost model. Metrics
are pre-aggregated: 1 billion requests generate only one data
point per metric label combination per scrape interval. Logs
are raw: 1 billion requests can generate 1 billion log lines.
Traces are sampled: storing 100% of traces at high volume is
unaffordable; tail-based sampling keeps only the interesting
ones. These cost differences drive the architecture: different
storage engines, different retention policies, different
sampling strategies. The art is tuning the balance: enough
log verbosity to debug, enough metric cardinality to slice
by useful dimensions, enough trace sampling to capture rare
failures.

**Level 5 - Mastery (distinguished engineer):**
The three-pillar model is not sacred. A fourth signal type -
continuous profiling (CPU flame graphs per service, per code
path) - is emerging as a practical pillar. eBPF-based
observability can generate trace-like data without application
instrumentation, blurring the lines between pillars. The
staff engineer's job is to recognise when the model is not
enough: a latency issue that logs, metrics, and traces all
show as "normal" may require profiling to identify GC pauses
or CPU starvation in a hot loop.

**EXPERT THINKING CUES:**

- The three pillars are not a checklist - they are a lens. Ask
  "which pillar best answers this specific question?" before
  choosing instrumentation.
- Red flag: using metrics for per-user debugging (cardinality
  explosion) or logs for latency trend analysis (too slow,
  too expensive).
- Correlating across pillars is the hardest part. Ensure every
  log line and every metric exemplar carries the trace ID.

---

### ⚙️ How It Works (Mechanism)

**Logs - discrete event records:**
A log line is emitted when something worth recording happens:
a request arrives, an error occurs, a state changes. Each
line is a structured JSON object with a timestamp, severity,
message, and contextual key-value pairs. Log stores
(Elasticsearch, Loki) index these for full-text and field
search. Log query languages (Lucene, LogQL) filter by field
values, time ranges, and patterns.

**Metrics - pre-aggregated numeric measurements:**
A metric is a named, typed measurement with labels. Four
types are standard in Prometheus:

- Counter: monotonically increasing (request count, error count)
- Gauge: point-in-time value (queue depth, memory usage)
- Histogram: distribution over buckets (request latency P50/95/99)
- Summary: pre-computed quantiles (deprecated at scale)

Metrics are scraped or pushed at intervals (typically 15s).
The TSDB stores one data point per label combination per
scrape - making billions of requests produce manageable data.

**Traces - causal span trees:**
A trace is a tree of spans. The root span represents the
entry point (API gateway receives request). Child spans
represent downstream work (service calls, database queries,
cache lookups). Every span carries: trace ID, span ID,
parent span ID, service name, operation name, start time,
duration, status, and attributes.

Context propagation is the mechanism that links spans:

```
Service A span (trace-id: abc, span-id: 1)
  calls Service B with header:
    traceparent: 00-abc-1-01
  Service B creates span (trace-id: abc, span-id: 2,
    parent: 1)
```

```
┌─────────────────────────────────────────┐
│  Three Pillars - Signal Types           │
├─────────────────────────────────────────┤
│                                         │
│  REQUEST                                │
│     │                                   │
│     ├── LOG: structured event emitted   │
│     │   {ts, level, traceId, msg, ...}  │
│     │                                   │
│     ├── METRIC: counter/histogram incr  │
│     │   requests_total{status="ok"}++   │
│     │                                   │
│     └── TRACE: span created/propagated  │
│         {traceId, spanId, duration,...} │
│                                         │
│  All three share: traceId = "abc123"    │
│                                         │
└─────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
[API Request arrives]
    ↓
[Gateway: inject traceparent header, record metric]
    ↓
[Service A: emit structured log, start span, incr metric]
    ↓
[Service B ← YOU ARE HERE: child span, log with traceId]
    ↓
[Database: SQL span, duration recorded]
    ↓
[All signals flow to OTel Collector]
    ↓
[Collector routes: logs→Loki, metrics→Prometheus,
                   traces→Tempo]
    ↓
[Grafana correlates all three via trace ID]
```

**FAILURE PATH:**
Service B emits an error span with `status=ERROR` and an error
log line both carrying the same trace ID. The error rate
metric counter increments for that endpoint. An alert fires.
The engineer searches logs by trace ID, finds the error
context, then opens the trace to see which downstream call
failed.

**WHAT CHANGES AT SCALE:**
At 100,000 requests per second, logs must be sampled or
filtered - storing every log line is prohibitively expensive.
Metrics remain manageable because aggregation keeps data
volume constant. Traces require tail-based sampling: buffer
all spans for 30 seconds, then keep only traces with errors
or high latency, discarding the rest.

---

### 💻 Code Example

**Example 1 - BAD: Three signals emitted without correlation:**

```java
// BAD: log has no trace ID - cannot join with traces
log.info("request processed for user " + userId);

// BAD: metric has no exemplar - cannot jump from metric
// to the specific trace that caused the spike
requestCounter.increment();

// BAD: trace span has no business attributes
// - cannot filter by userId in trace search
Span span = tracer.spanBuilder("process").startSpan();
```

**Example 2 - GOOD: All three pillars correlated via trace ID:**

```java
Span span = tracer
    .spanBuilder("processOrder")
    .setAttribute("user.id",  userId)
    .setAttribute("order.id", orderId)
    .startSpan();

try (Scope s = span.makeCurrent()) {
    String traceId = span.getSpanContext().getTraceId();

    // LOG: structured, includes trace ID for correlation
    log.info("order.processing",
        "traceId", traceId,
        "userId",  userId,
        "orderId", orderId);

    processOrder(orderId);

    // METRIC: low-cardinality labels, exemplar links to trace
    orderCounter.add(1, Attributes.of(
        AttributeKey.stringKey("region"), region,
        AttributeKey.stringKey("status"), "success"
    ));
    span.setStatus(StatusCode.OK);
} catch (Exception e) {
    span.recordException(e);
    span.setStatus(StatusCode.ERROR);
    orderCounter.add(1, Attributes.of(
        AttributeKey.stringKey("region"), region,
        AttributeKey.stringKey("status"), "error"
    ));
} finally {
    span.end();
}
```

**How to verify:**
In Grafana, click a spike on the error rate metric panel.
Grafana Exemplar support jumps to the exact trace ID for a
request in that spike. Open the trace - the causal path is
visible. Click the trace ID in the trace view - Loki shows
all log lines from the same request.

---

### ⚖️ Comparison Table

| Pillar          | Best question answered             | Storage cost | Cardinality       | Sampling          |
| --------------- | ---------------------------------- | ------------ | ----------------- | ----------------- |
| **Logs**        | What happened, exactly?            | High         | Unlimited         | Recommended       |
| **Metrics**     | How many, how fast, what trend?    | Low          | Low (labels)      | Not needed        |
| **Traces**      | Which request, through which path? | Medium       | High (attributes) | Required at scale |
| Profiling (4th) | Which code path consumes CPU?      | Very high    | Medium            | Required          |

**How to choose which pillar to query first:**
Start with metrics - they are always available, fast to query,
and surface trends. If a metric anomaly is found, use logs to
find the relevant events in that time window. Use the trace ID
from the log to open the trace for full causal path. This
funnel - metric alert, log context, trace causality - is the
standard incident workflow.

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                                                                                 |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The three pillars are redundant - one is enough  | Each answers a fundamentally different class of question. Metrics cannot show you the specific code path; traces cannot show you trends over time; logs alone cannot reconstruct distributed causality. |
| Logs are the most important pillar               | At scale, logs are the most expensive and most frequently sampled. Metrics provide the fastest alert signal and should be the primary detection mechanism.                                              |
| Traces replace logs                              | Traces show the path and timing; logs show the business context and error detail at each step. A trace without correlated logs often cannot explain WHY a span failed, only THAT it did.                |
| Adding more log verbosity improves observability | Unstructured log verbosity increases noise and storage cost without improving diagnostic power. A single structured log line with good fields outperforms 100 unstructured lines.                       |
| OpenTelemetry replaces the three-pillar backends | OpenTelemetry is the instrumentation and collection layer. You still need Prometheus, Loki, and Tempo (or equivalents) as the storage and query backends.                                               |

---

### 🚨 Failure Modes & Diagnosis

**No trace ID correlation between pillars**

**Symptom:**
When an error metric spikes, engineers cannot find the
corresponding log lines or traces. Searching logs for the
same time window returns thousands of unrelated results.
Trace search returns nothing useful because log lines contain
no trace ID.

**Root Cause:**
Log statements do not include the active trace ID. The MDC
(Mapped Diagnostic Context) is not configured to propagate
the OpenTelemetry trace ID into the logging framework.

**Diagnostic Command:**

```bash
# Check if trace IDs appear in recent log lines
kubectl logs deploy/checkout-service --tail=50 \
  | jq 'select(.traceId != null) | {ts, traceId, msg}'

# If traceId is always null, MDC bridge is not configured
```

**Fix:**

```xml
<!-- Spring Boot + Logback: bridge OTel trace to MDC -->
<!-- GOOD: add dependency in pom.xml -->
<dependency>
  <groupId>io.micrometer</groupId>
  <artifactId>micrometer-tracing-bridge-otel</artifactId>
</dependency>
<!-- Logback pattern: include %X{traceId} in format -->
<pattern>
  %d{ISO8601} [%X{traceId}] %-5level %logger - %msg%n
</pattern>
```

**Prevention:**
Add a log output assertion to CI: verify every log line in
the test suite contains a non-null `traceId` field.

---

**Metrics covering trace-level questions (cardinality explosion)**

**Symptom:**
Prometheus memory usage grows continuously. `tsdb_head_series`
exceeds 5 million. Queries time out. Engineers added `userId`,
`orderId`, or `requestPath` as metric labels to answer
per-request questions.

**Root Cause:**
The wrong pillar was used for the question. Per-request
analysis belongs in traces, not metrics. Metrics use labels
for low-cardinality dimensions only.

**Diagnostic Command:**

```bash
# Find metric names with most series (potential explosion)
curl -sg 'localhost:9090/api/v1/query?query=
  topk(5,count+by(__name__)({__name__!=""}))' \
  | jq '.data.result[] | {name: .metric.__name__,
    series: .value[1]}'
```

**Fix:**
Move high-cardinality identifiers from metric labels to trace
span attributes. Keep metric labels to 5 or fewer distinct
values per dimension.

**Prevention:**
Code review checklist: every new `Tags.of(...)` call must
list all label values and confirm maximum unique count is
under 50.

---

**Missing spans from async or messaging boundaries**

**Symptom:**
Traces show a gap: Service A's span ends, and Service C's span
starts, but there is no span for the Kafka message transit.
Engineers cannot see the latency or failures in the messaging
layer.

**Root Cause:**
The Kafka producer is not injecting trace context into message
headers, and the consumer is not extracting it to create a
linked span. The trace context is lost at the async boundary.

**Diagnostic Command:**

```bash
# Check Kafka message headers for trace context
kafka-console-consumer --topic orders \
  --bootstrap-server localhost:9092 \
  --property print.headers=true \
  --max-messages 5 | grep -i traceparent
# Output should show: traceparent:00-abc123-1-01
# If empty, producer is not injecting context
```

**Fix:**
Use OpenTelemetry Kafka instrumentation or manually inject
context into message headers on the producer and extract
on the consumer to create a linked span.

**Prevention:**
Async boundaries (Kafka, RabbitMQ, SQS, async jobs) must be
treated as explicit context propagation points. Include
messaging trace propagation in the service template for all
new services.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `What Is Observability and Why It Matters` - the three
  pillars are the implementation of observability; understand
  the concept before the implementation

**Builds On This (learn these next):**

- `Logging Fundamentals (Structured Logs)` - deep dive into
  the log pillar: structure, ingestion, and query patterns
- `Metrics - Types (Counter, Gauge, Histogram)` - deep dive
  into the metrics pillar and Prometheus data model
- `Distributed Tracing Fundamentals` - deep dive into the
  trace pillar: spans, context propagation, and sampling
- `OpenTelemetry - The Standard` - the unified SDK that
  implements all three pillars in one instrumentation model
- `Alerting Fundamentals` - how metric signals become alerts

**Alternatives / Comparisons:**

- `The Observability Ecosystem Map` - maps the full tool
  landscape for each pillar to vendors and open-source options
- `Continuous Profiling (Pyroscope, Parca)` - the emerging
  fourth pillar that complements the three-pillar model

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Three signal types covering all classes   │
│              │ of production diagnostic questions        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ No single signal type answers every       │
│ SOLVES       │ question - each pillar fills a gap        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Metrics detect, logs contextualise,       │
│              │ traces explain - they form a funnel       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Designing instrumentation for any service │
│              │ that needs full production diagnostics    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Using metrics for per-request questions   │
│              │ or logs for latency trend analysis        │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Emitting all three pillars without a      │
│              │ shared trace ID to correlate them         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Complete diagnostic coverage vs three     │
│              │ backends, three query languages to master │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Each pillar answers one class of         │
│              │  question - together they answer all."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Structured Logs → Metrics → Tracing       │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Metrics detect problems (alert when error rate spikes).
   Logs contextualise them (what event happened, with what
   data). Traces explain causality (which path, which hop,
   which latency). Missing any one breaks the diagnostic chain.
2. All three must share a trace ID to be useful together.
   A metric exemplar, a log line, and a trace span that all
   carry the same trace ID can be joined in a single query.
3. Each pillar has a different cost model: metrics are cheap
   (aggregated), logs are expensive (verbose), traces are
   medium-cost but require sampling at scale.

**Interview one-liner:**
"Logs, metrics, and traces are the three signal types that
make a system observable. Metrics trigger the alert, logs
give you event context, and traces show you the exact causal
path through all services. OpenTelemetry instruments all
three from a single SDK."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Complex systems require multiple complementary observation
lenses because no single view captures all relevant
information. Combining orthogonal perspectives - each
designed for a specific question class - gives coverage
that no single comprehensive signal type could provide.

**Where else this pattern appears:**

- **Financial analysis** - balance sheet (point-in-time state,
  like a gauge metric), income statement (change over time,
  like a counter), and cash flow statement (causal path of
  money, like a trace) together tell a complete financial story
  that none alone can tell.
- **Medical diagnosis** - blood tests (metrics), patient history
  notes (logs), and imaging/scans (structural traces of
  causality) combine for a complete clinical picture.
- **Security operations** - SIEM logs, NetFlow metrics, and
  attack chain analysis (traces) are the three pillars of
  security observability.

**Industry applications:**

- **E-commerce** - the three pillars are the foundation of
  every SRE team at Amazon, Google, and Netflix. Traces were
  the key innovation: Google's Dapper paper (2010) inspired
  Zipkin, Jaeger, and eventually OpenTelemetry.
- **Financial services** - transaction tracing is mandated by
  regulators in many jurisdictions. Each payment must have a
  complete, auditable trace from initiation to settlement.

---

### 💡 The Surprising Truth

The three-pillar model is often presented as a neat,
comprehensive framework - but its most important insight is
the one it does not state explicitly: the pillars are only
useful when they are correlated. A system can emit gigabytes
of logs, thousands of metrics, and millions of spans and
still be effectively unobservable if those signals cannot be
joined. The trace ID is not just a debugging convenience -
it is the linchpin that transforms three isolated data
streams into a coherent diagnostic system. Engineers who
instrument each pillar independently but omit the trace ID
have done 90% of the work for 10% of the value.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[EXPLAIN]** Describe the three pillars to a junior
   engineer and explain which specific production question
   each one is best at answering - with a concrete example
   for each.
2. **[DEBUG]** Given only a Prometheus alert showing a spike
   in `checkout_errors_total`, describe the exact query
   sequence across all three pillars to identify the root
   cause service and code path.
3. **[DECIDE]** A team wants to add a metric with a `userId`
   label and a log entry with full request body. Explain
   why both are wrong and propose the correct pillar and
   signal design for each use case.
4. **[BUILD]** Write the OpenTelemetry instrumentation code
   for a Java service method that emits all three signals
   for a single operation, correctly correlated by trace ID.
5. **[EXTEND]** Describe how you would implement the
   three-pillar model for a Kafka consumer: what is the log
   event, what is the metric, what is the trace span, and
   how do you propagate context from the producer?

---

### 🧠 Think About This Before We Continue

**Q1.** A service emits all three pillars but uses different
timestamps for each: the log timestamp uses the application
clock, the metric timestamp uses the Prometheus scrape time,
and the trace span start time uses a third clock source with
clock skew. When you try to correlate a 200ms latency spike
visible in metrics with the corresponding log lines and trace,
the events do not align. What class of problems does clock
skew create across the three pillars, and how would you
design instrumentation to minimise its impact?
_Hint: Think about how Prometheus scrape times, OpenTelemetry
span timestamps, and log ingestion times relate to the actual
wall-clock time of the event in the application._

**Q2.** At 500,000 requests per second with a 0.05% error rate,
that is 250 errors per second. You need to investigate a
specific error type that appears in 10% of those errors -
25 per second. Storing every log line and every trace span
is unaffordable. Design a sampling strategy across all three
pillars that ensures you capture enough signal to diagnose
the error without breaking your storage budget.
_Hint: Consider tail-based trace sampling (keep all error
traces), head-based log sampling (keep a fixed percentage),
and full-fidelity metrics. Which pillar should never be
sampled? Why?_

**Q3.** Implement the three-pillar model for a background job:
a scheduled order reconciliation task that runs every 5
minutes, processes up to 10,000 orders, and reports to a
downstream accounting service. Define the exact log events,
metric counters and histograms, and trace spans you would
instrument. What makes this harder than instrumenting a
synchronous HTTP endpoint?
_Hint: Background jobs have no inbound HTTP request to carry
trace context. How do you create a root span for a job
invocation? How do you propagate context to the accounting
service call? How do you measure "job run duration" vs
"per-order processing time" in the same metric?_

---

### 🎯 Interview Deep-Dive

**Q1: "Explain the three pillars of observability and how
they complement each other. When would you use each one
during a production incident?"**
_Why they ask:_ Tests foundational observability knowledge and
whether the candidate uses the pillars as a coherent system
rather than as independent tools.
_Strong answer includes:_

- Metrics detect the problem (error rate alert fires)
- Logs provide event context for the time window (what
  happened, with what business data, for which user)
- Traces show the causal path (which service, which call,
  which database query was the bottleneck)
- The trace ID links all three and enables jumping between
  them in a single investigation workflow

**Q2: "Your team is using Elasticsearch for all three pillars:
metrics as JSON log events, traces as JSON log events, and
actual logs as JSON log events. What are the problems
with this approach?"**
_Why they ask:_ Tests whether the candidate understands why
the pillars require different storage engines, not just
different data formats.
_Strong answer includes:_

- Metrics in a log store cannot use PromQL or time-series
  aggregation - calculating P99 latency over 1 billion log
  events is extremely expensive vs a TSDB
- Traces stored as logs lose the parent-child span structure
  and cannot be queried as a tree - you cannot "open a trace"
  and see all its spans
- Elasticsearch is not optimised for time-series range queries
  (metric aggregations) - it is inverted-index for text search
- The correct architecture: TSDB for metrics, Loki/ES for
  logs, Jaeger/Tempo for traces, each using the right storage
  model for its query pattern

**Q3: "How do you ensure the three pillars stay correlated
when requests cross Kafka topic boundaries?"**
_Why they ask:_ Tests practical distributed tracing knowledge

- the hardest correlation challenge in real production systems.
  _Strong answer includes:_
- Kafka messages must carry W3C `traceparent` in their headers
- The producer injects the current span context into message
  headers before publishing
- The consumer extracts the context and creates a new span
  with the producer span as its parent, linking the two traces
- Without this, every Kafka consumer creates an independent
  root trace and the end-to-end causal chain is broken
- OpenTelemetry Kafka instrumentation handles this
  automatically; manual implementation requires using the
  OTel `W3CTraceContextPropagator` API
