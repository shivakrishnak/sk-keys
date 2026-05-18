---
id: OBS-039
title: "Observability at Scale (Sampling, Aggregation)"
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★★
depends_on: OBS-001, OBS-006, OBS-008, OBS-027
used_by: OBS-041, OBS-044, OBS-045
related: OBS-028, OBS-032, OBS-046, OBS-047
tags:
  - observability
  - reliability
  - devops
  - sre
  - advanced
  - production
  - deep-dive
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Mastery"
nav_order: 39
permalink: /technical-mastery/obs/observability-at-scale-sampling-aggregation/
---

⚡ TL;DR - Observability at scale is the discipline of
answering "what is wrong with my system" across 1,000
services and billions of events per hour - which requires
sampling, aggregation, and intelligent routing to avoid
the cost and noise of capturing everything at full fidelity.

| #039            | Category: Observability & SRE                                                                                                   | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | What Is Observability, Prometheus, Distributed Tracing, Log Aggregation at Scale                                                |                 |
| **Used by:**    | Observability Platform Architecture, Platform Observability Engineering, Observability System Design Internals                  |                 |
| **Related:**    | Trace Sampling Strategies, Cardinality in Metrics Systems, Time-Series Database Design, Distributed Tracing System Architecture |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A company grows from 10 services to 1,000 services over
5 years. The observability stack that worked at 10 services
is scaled horizontally for 1,000 services. Every trace is
captured. Every log is indexed. Every metric cardinality
label combination is stored. The result: Prometheus storage
costs increase 100x. Elasticsearch indexing costs increase
100x. Jaeger receives 500,000 traces per minute at peak.
The observability system requires a team of 10 engineers
just to keep it running. During incidents, queries timeout
because the system is overwhelmed by the data it is
collecting. The observability system itself causes incidents.

**THE BREAKING POINT:**
At scale, capturing everything at full fidelity is not
a better observability strategy - it is an economic and
operational impossibility. The signal-to-noise ratio also
degrades: with 500,000 traces per minute, finding the 50
anomalous traces requires searching through 499,950 normal
ones. Scaling observability linearly with system size is
the wrong model.

**THE INVENTION MOMENT:**
Observability at scale requires a different model: instead
of capturing everything, define what questions need to be
answered, and capture only the data needed to answer those
questions with sufficient accuracy. Sampling theory,
statistical aggregation, and intelligent routing are the
mathematical tools that make this possible.

**EVOLUTION:**
Early observability stacks captured everything (and worked
at small scale). Google's Dapper paper (2010) introduced
probabilistic trace sampling for production at scale.
Netflix's Atlas metrics system introduced query-time
aggregation. Honeycomb introduced tail-based sampling
for traces (sample intelligently based on trace outcome,
not randomly). Modern observability platforms combine
head-based sampling (random, cheap), tail-based sampling
(intelligent, expensive), metric aggregation at the edge,
and tiered storage routing.

---

### 📘 Textbook Definition

**Observability at scale** is the architectural and
operational discipline of maintaining sufficient visibility
into a large-scale distributed system to answer diagnostic
questions about service behavior, performance, and failure

- while managing the data volume, cost, and operational
  complexity of the observability infrastructure through
  sampling (probabilistic event selection), aggregation
  (computing statistics at collection time rather than query
  time), and intelligent routing (directing data to storage
  tiers based on diagnostic value).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
At scale, you cannot store everything - so you store the
right things: sampled traces, aggregated metrics, and
indexed critical logs.

**One analogy:**

> Observability at scale is like a statistical poll.
> A pollster cannot interview all 330 million Americans,
> but they can interview 2,000 carefully selected ones
> and produce an accurate picture of the whole. The poll
> does not tell you what every individual thinks, but it
> tells you what 95% of Americans think with a margin of
> error. In the same way, a 1% sample of your production
> traces tells you with high statistical confidence what
> 99% of your traces look like, without storing 100x
> more data.

**One insight:**
The critical insight is that different observability signals
require different scale strategies. Metrics should NEVER
be sampled - they should be aggregated (pre-compute
histograms and counters at collection time). Traces should
be sampled - either probabilistically or tail-based.
Logs should be partially indexed (hot tier for ERROR/WARN,
cold archive for everything else). Conflating these
strategies leads to either data blindness or cost explosion.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Data volume grows super-linearly with system complexity:
   1,000 services with cross-calls produce more than 100x
   the trace data of 10 services
2. Diagnostic value per event is not uniform: an ERROR trace
   is 1,000x more diagnostic value than a healthy 200ms trace
3. Statistical sampling preserves aggregate behavioral
   insights while discarding individual event fidelity
4. Aggregation at collection time is always cheaper than
   aggregation at query time for high-cardinality questions

**DERIVED DESIGN:**
These invariants drive the three scale strategies:

- **Metrics aggregation**: never store raw events for metrics;
  compute counters, histograms, and gauges at scrape time;
  Prometheus TSDB compresses 1 billion raw events into
  a queryable metric series efficiently
- **Trace sampling**: store only a representative sample
  of traces; head-based (random) is simple; tail-based
  (keep traces with errors/high latency, discard fast success
  traces) is smarter but requires a buffer to make sampling
  decisions after the trace completes
- **Log routing**: index only ERROR/WARN to hot search;
  archive all logs to cheap cold storage; derive metrics
  from logs instead of querying logs for aggregate questions

**THE TRADE-OFFS:**

**Gain:** Sustainable observability costs at scale; faster
query performance (aggregated queries outperform scans);
focus on high-value signals.

**Cost:** Sampled traces miss rare events in the unsampled
fraction; head-based sampling may discard a failing trace
that was sampled out; aggregated metrics cannot answer
"what was the trace_id of the specific request with the
highest latency?"

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Any observability system at scale must solve
the volume problem through one of: sampling, aggregation,
or routing. These are mathematically necessary.

**Accidental:** Maintaining separate sampling configurations
for 50 different services, manually tuning sampling rates
per service, building custom log pipelines per team.

---

### 🧪 Thought Experiment

**SETUP:**
Your service processes 100,000 requests per second.
P99 latency is 50ms. Error rate is 0.01% (10 errors/sec).
You are deciding on a trace sampling strategy.

**OPTION A: Capture all traces**
Data volume: 100,000 traces/second.
At 2KB per trace: 200MB/second = 17TB/day.
Jaeger storage at $0.02/GB: $340/day = $124,000/year.
Jaeger cluster to process 100K traces/sec: 50 nodes.
Total cost: $500K-$1M/year for trace storage + infra.
Query performance: searching 8.6 billion traces per day
for the 10 erroring ones takes minutes.

**OPTION B: 1% head-based sampling**
Data volume: 1,000 traces/second.
Storage: $1,240/year. Jaeger: 5 nodes.
Diagnostic value: 99% reduction in storage at 99%
statistical accuracy for latency distributions and
error patterns.
Risk: You capture 1% of the 10 errors/sec = 0.1 error
traces/sec. In a 1-minute window, you may have 0 error
traces captured by chance.

**OPTION C: Tail-based sampling (keep all errors + 1% success)**
Storage: 1% of normal + 100% of errors.
10 errors/sec _ 100% = 10 error traces/sec (always captured).
99,990 success/sec _ 1% = 1,000 traces/sec.
Total: 1,010 traces/sec. Negligible cost increase vs B.
Diagnostic value: EVERY error is captured. Statistical
view of normal traffic preserved. Best of both worlds.

**THE INSIGHT:**
Tail-based sampling is the correct scale strategy for
trace capture: keep all anomalous traces (errors, high
latency), sample normal ones. This is the design that
maximizes diagnostic value per byte stored.

---

### 🧠 Mental Model / Analogy

> Observability at scale is like a hospital triage system.
> Not every patient gets an MRI (full-fidelity capture)
>
> - that would be impossibly expensive and slow. Instead,
>   vital signs are taken for everyone (metrics aggregation -
>   cheap, always-on), chest X-rays for concerning cases
>   (logs for WARN/ERROR), and MRI only for high-priority
>   diagnoses (trace capture for errors and anomalies). The
>   triage decision routes each patient to the right level
>   of diagnostic investigation. You get 90% of the diagnostic
>   value at 10% of the cost.

Element mapping:

- "Vital signs for everyone" → metrics aggregation (cheap, universal)
- "Chest X-ray for concerning cases" → log indexing for WARN/ERROR
- "MRI for high priority" → trace capture for errors/anomalies
- "Triage decision" → tail-based sampling + log routing policy
- "Cost of MRI for all" → full-fidelity observability at scale

Where this analogy breaks down: hospital triage is done by
humans with judgment; observability triage is automated
with configurable rules. The rules are imperfect - you can
still miss a "symptom" that your routing policy did not
recognize as high-priority until after the fact.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
When you have thousands of services, you cannot record
everything - there is too much data and it costs too much.
Observability at scale means deciding what to record
(important errors, a sample of normal traffic), what to
aggregate (counts and percentiles rather than raw events),
and what to discard (repetitive normal traffic).

**Level 2 - How to use it (junior developer):**
Use Prometheus for metrics - it handles aggregation
automatically; never disable Prometheus scraping.
For tracing, configure a 10% head-based sampling rate
as a starting point. For logs, log ERROR and WARN at
full fidelity; log INFO only for significant events;
do not log DEBUG in production.

**Level 3 - How it works (mid-level engineer):**
Metrics aggregation: Prometheus scrapes counters and
histograms from services every 15 seconds. Data points
are pre-aggregated at scrape time. Queries run against
aggregated data, not raw events. Trace sampling: configure
the OTel SDK with a probabilistic sampler at 10-20% for
head-based, or use Jaeger's remote sampling with adaptive
rates per endpoint. Log routing: Logstash routes ERROR/WARN
to Elasticsearch hot tier (queryable in <1s); INFO/DEBUG
to S3 cold tier (queryable via Athena in minutes).

**Level 4 - Why it was designed this way (senior/staff):**
Head-based sampling makes the keep/discard decision at the
start of the trace (at the entry service). It is simple but
loses correlation across services: if service A samples in
but service B samples out independently, the distributed
trace is incomplete. Consistent sampling (use the trace_id
to deterministically decide keep/discard - same trace_id
always makes the same decision) solves the coherence problem
but still makes decisions before knowing the trace outcome.
Tail-based sampling delays the decision until the trace
completes (all spans have arrived at the collector), then
decides based on the full trace outcome. It requires a
buffer to hold traces while waiting for all spans, which
adds memory and complexity.

**Level 5 - Mastery (distinguished engineer):**
At platform scale (1,000+ services), sampling configuration
cannot be managed per-service manually - it must be driven
by a central adaptive sampling policy. Google's Dapper
and LinkedIn's OpenTelemetry infrastructure implement
adaptive sampling: the sampling rate adjusts dynamically
based on the service's request volume to maintain a constant
trace volume at the collection tier. Services at 1,000 RPS
are sampled at 1%; services at 10 RPS are sampled at 100%.
This produces a uniform trace volume regardless of service
load. The sampling decision is communicated from the
sampling server to the OTel SDK via the remote sampling
API. Combined with tail-based sampling for error cases
(always capture errors regardless of sampling rate),
adaptive + tail-based is the reference architecture for
large-scale distributed tracing.

---

### ⚙️ How It Works (Mechanism)

**THREE-TIER SCALE ARCHITECTURE:**

```
┌──────────────────────────────────────────────────────┐
│           OBSERVABILITY AT SCALE                     │
├──────────────┬───────────────────┬───────────────────┤
│ SIGNAL       │ SCALE STRATEGY    │ STORAGE           │
├──────────────┼───────────────────┼───────────────────┤
│ METRICS      │ Aggregation       │ Prometheus TSDB   │
│              │ (compute at       │ Thanos/Cortex     │
│              │ scrape time)      │ (long-term)       │
├──────────────┼───────────────────┼───────────────────┤
│ TRACES       │ Tail-based        │ Jaeger/Tempo      │
│              │ sampling          │ S3 (archive)      │
│              │ (keep errors +    │                   │
│              │ 1% normal)        │                   │
├──────────────┼───────────────────┼───────────────────┤
│ LOGS         │ Tiered routing    │ Elasticsearch     │
│              │ ERROR/WARN → hot  │ (hot, 7 days)     │
│              │ ALL → cold S3     │ S3 (cold, 90d)    │
└──────────────┴───────────────────┴───────────────────┘
```

**TAIL-BASED SAMPLING ARCHITECTURE:**

```
Requests arrive at all 1,000 services
  Each service sends spans to OTel Collector (local)
     │
     ↓
  OTel Collector buffers spans
  Waits for trace completion (all spans for trace_id)
  After 30s, makes sampling decision:
     │
     ├── Has ERROR span? → Keep trace (100%)
     ├── P99 latency > 500ms? → Keep trace (100%)
     └── Normal healthy trace? → Keep 1% (drop 99%)
     │
     ↓
  Kept traces → Jaeger/Tempo storage
  Dropped traces → discard
```

**HEAD-BASED VS TAIL-BASED:**

```
HEAD-BASED (simple, stateless):
  Decision: at trace start, before any processing
  Decision basis: random number < sampling_rate
  Overhead: minimal (no buffer needed)
  Problem: may discard error traces that were not
           yet known to be errors at decision time

TAIL-BASED (intelligent, stateful):
  Decision: after all spans arrive (trace complete)
  Decision basis: trace outcome (errors, latency)
  Overhead: buffer required (1 minute of trace data)
  Problem: memory-intensive, complex at high volume

CONSISTENT HEAD-BASED (hybrid):
  Decision: at trace start using trace_id hash
  same trace_id = same decision at all services
  Benefit: complete traces (no broken chains)
  Problem: still doesn't know outcome; may discard errors
```

---

### 🔄 The Complete Picture - End-to-End Flow

**SCALE ROUTING DECISION FLOW:**

```
Event arrives (trace span, log line, metric scrape)
   │
   ↓
WHAT TYPE?
   ├── METRIC → compute counter/histogram, store in TSDB
   │   (no sampling; aggregation handles scale)
   │
   ├── TRACE SPAN → buffer at OTel Collector
   │    Wait for trace completion (30s timeout)
   │         │
   │    Complete trace → sampling decision:
   │         ├── Error/slow → keep always
   │         └── Normal → keep at configured rate (1-10%)
   │
   └── LOG → routing by level:
        ├── ERROR/WARN → index in Elasticsearch hot tier
        └── INFO/DEBUG → archive in S3 cold tier
```

**WHAT CHANGES AT 10X SCALE:**
At 10,000 services, the OTel Collector cluster for tail-
based sampling must scale horizontally. Trace spans for
the same trace_id must be routed to the same collector
(consistent hashing by trace_id). This requires a load
balancer layer that hashes trace_ids to collectors. The
Prometheus federation model is also required: individual
Prometheus instances per cluster, with Thanos/Cortex as
the global query layer for cross-cluster metrics.

---

### 💻 Code Example

**Example 1 - BAD: unsampled trace collection**

```yaml
# BAD: OTel SDK configured to send all traces
# At 10,000 RPS this sends 600,000 spans/min to Jaeger
# Jaeger overwhelmed; query latency spikes

# OpenTelemetry Java agent config:
# -Dotel.traces.sampler=always_on
# Results: 100% sampling at all services
# Cost: $500K+/year in trace storage at 10K RPS
# Query: find 5 error traces in 600K spans/min
```

**Example 2 - GOOD: tail-based sampling configuration**

```yaml
# GOOD: OTel Collector with tail-based sampling
# Keeps 100% of error traces, 1% of normal

# otel-collector-config.yaml
processors:
  tail_sampling:
    decision_wait: 30s # wait for all spans
    num_traces: 100000 # buffer size
    expected_new_traces_per_sec: 10000
    policies:
      # Always keep traces with errors
      - name: keep-errors
        type: status_code
        status_code:
          status_codes: [ERROR]

      # Always keep slow traces (P99 > 500ms)
      - name: keep-slow-traces
        type: latency
        latency:
          threshold_ms: 500

      # Keep 1% of all other traces
      - name: probabilistic-fallback
        type: probabilistic
        probabilistic:
          sampling_percentage: 1

exporters:
  jaeger:
    endpoint: jaeger:14250

service:
  pipelines:
    traces:
      processors: [tail_sampling]
      exporters: [jaeger]
```

**Example 3 - Prometheus: cardinality protection at scale**

```yaml
# BAD: high-cardinality label in Prometheus
# trace_id as label = billions of unique series
http_request_duration_seconds{
  service="api",
  trace_id="abc123def456"   # NEVER do this
}

# GOOD: service, endpoint, status_code only
# Cardinality: 100 services * 50 endpoints
# * 5 status codes = 25,000 series (manageable)
http_request_duration_seconds{
  service="api",
  endpoint="/checkout",
  status_code="200"
}

# To link metrics to traces: use exemplars
# (Prometheus 2.26+) - attach trace_id as metadata
# to a histogram sample, not as a label
# exemplar: {traceID="abc123"} value=0.45
```

**How to test / verify correctness:**
Test sampling effectiveness: inject 100 error traces
into a load-tested environment. Verify 100% appear in
Jaeger (tail-based captures all errors). Inject 10,000
normal traces. Verify approximately 100 (1%) appear.
Validate that the latency distribution of sampled normal
traces matches the unsampled distribution statistically.

---

### ⚖️ Comparison Table

| Strategy                        | Cost      | Diagnostic Completeness | Complexity | Best For                |
| ------------------------------- | --------- | ----------------------- | ---------- | ----------------------- |
| **Full fidelity (no sampling)** | Very high | 100%                    | Low        | <100 RPS, dev only      |
| Head-based sampling (1%)        | Low       | ~1%                     | Low        | Simple, stateless       |
| Consistent head-based           | Low       | ~1% (coherent)          | Medium     | Distributed correctness |
| **Tail-based sampling**         | Low       | 100% errors + 1% normal | High       | Production at scale     |
| Adaptive sampling               | Medium    | Configurable            | Very high  | Very large scale        |

**How to choose:**
Start with 10% head-based for all services. As volume grows
(>10K RPS), move to tail-based for high-traffic services
where error traces are critical. Use adaptive sampling
only with dedicated platform engineering support.

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                              |
| ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Higher sampling rate = better observability | Above a threshold, more samples add cost without adding diagnostic value; 1% gives 99%+ statistical accuracy for P99 |
| Sampling means missing errors               | Tail-based sampling captures 100% of error traces by design                                                          |
| Metrics and traces need the same strategy   | Metrics: aggregate (never sample); Traces: sample; Logs: tier-route                                                  |
| Sampling rates should be fixed              | Adaptive rates per service volume are more efficient                                                                 |
| Reducing log volume = better observability  | Discarding WARN/ERROR to save cost is trading reliability for savings                                                |

---

### 🚨 Failure Modes & Diagnosis

**Missing Trace in Jaeger Queries**

**Symptom:**
Engineer searches Jaeger for a trace_id from an error log.
Trace not found. The error log clearly shows the trace_id.

**Root Cause (two causes):**

1. Head-based sampling discarded the trace before the error
   occurred
2. Downstream services are not instrumented; trace is
   incomplete and was filtered out

**Diagnostic Steps:**

```bash
# Check if trace exists anywhere
curl "http://jaeger:16686/api/traces/${TRACE_ID}"

# Check OTel Collector sampling logs
kubectl logs -n observability otel-collector-xxx | \
  grep "${TRACE_ID}"
```

**Fix:** Migrate to tail-based sampling with error retention.

---

**Prometheus Cardinality Explosion**

**Symptom:**
Prometheus memory grows from 4GB to 64GB over 2 weeks.
Queries that took 200ms now take 30 seconds.

**Root Cause:**
A developer added `user_id` as a metric label. 100K users
= 100K time series from a single metric.

**Diagnostic Command:**

```bash
# Find highest cardinality metrics
curl -s 'http://prometheus:9090/api/v1/query?query=
  topk(10,count by (__name__)({__name__=~".+"}))'
```

**Fix:** Remove the high-cardinality label; use exemplars
to link metrics to individual trace_ids instead.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `What Is Observability` - the three-pillar model that
  observability at scale must address
- `Prometheus - Metrics Collection` - primary metrics aggregation
- `Distributed Tracing Fundamentals` - trace concepts for
  understanding sampling strategies
- `Log Aggregation at Scale` - log routing foundation

**Builds On This (learn these next):**

- `Observability Platform Architecture Design` - full
  platform architecture implementing scale strategies
- `Platform Observability Engineering` - running observability
  at scale organizationally
- `Observability System Design Internals` - deep-dive into
  how each scale component works

**Alternatives / Comparisons:**

- `Trace Sampling Strategies` - dedicated deep-dive on
  head-based vs tail-based vs adaptive sampling
- `Cardinality in Metrics Systems` - the specific cardinality
  problem in metrics at scale
- `Time-Series Database Design` - the storage layer for
  aggregated metric data

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Architecture for maintaining observabilit│
│              │ across 1,000+ services without cost      │
│              │ explosion or query degradation           │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Full-fidelity capture at scale is        │
│ SOLVES       │ economically impossible and creates      │
│              │ signal-to-noise collapse                 │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ Different signals need different scale   │
│              │ strategies: metrics=aggregate,           │
│              │ traces=tail-sample, logs=tier-route      │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ >100K events/sec across any signal type; │
│              │ observability cost growing proportionally│
│              │ with service count                       │
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ Disabling observability to save cost is  │
│              │ never acceptable; routing and sampling   │
│              │ are the only valid trade-offs            │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Sampling metrics (should aggregate) or   │
│              │ not sampling traces at significant scale │
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Sampling rate vs diagnostic completeness:│
│              │ 1% sampling = 99% statistical accuracy + │
│              │ 100% error capture (tail-based)          │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Store the signal, sample the noise."    │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Platform Architecture → System Design    │
│              │ Internals                                │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Metrics: aggregate (never sample). Traces: tail-sample
   (100% errors, 1% normal). Logs: tier-route (hot for
   ERROR/WARN, cold archive for all). Three signals, three
   different scale strategies.
2. Tail-based sampling captures 100% of error traces plus
   a statistical sample of normal traffic - best of both
   worlds at low cost.
3. Never add unbounded cardinality labels (user_id, trace_id,
   session_id) to Prometheus metrics. Use exemplars to link
   metrics to individual traces.

**Interview one-liner:**
"Observability at scale requires different strategies per
signal: metrics are aggregated at collection time so they
never grow with event volume; traces are tail-sampled to
capture 100% of errors and 1% of normal traffic; logs are
tiered with ERROR/WARN indexed to fast search and everything
archived cheaply. The biggest scale mistakes are high-
cardinality Prometheus labels that cause memory explosion,
head-based trace sampling that discards error traces, and
indexing all logs to full-text search when label-based
indexing handles 90% of queries at 10% the cost."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When data volume exceeds the ability to store everything
at full fidelity, the correct response is not to capture
nothing - it is to capture the minimum data sufficient to
answer your diagnostic questions with statistical confidence.
This principle applies to network packet capture, financial
transaction monitoring, genomics, and sensor networks.

**Where else this pattern applies:**

- **Network monitoring** - flow sampling (NetFlow) captures
  1 in 1,000 packets to characterize network behavior
- **A/B testing** - statistical sampling theory defines
  minimum sample size to detect an effect with confidence
- **Database query performance** - slow query logs sample
  only queries exceeding a threshold duration

---

### 💡 The Surprising Truth

The original Dapper paper (Google, 2010) revealed that
lowering the sampling rate from 1% to 0.01% made trace
investigation easier, not harder. At 1% sampling, Dapper
collected tens of millions of traces per day, making queries
slow. At 0.01%, queries returned in seconds and the sample
still contained hundreds of thousands of representative
traces per day. The insight: for aggregate statistical
analysis, 0.01% is indistinguishable from 1%. The right
sampling rate is the minimum needed to answer your diagnostic
questions with acceptable confidence - which is almost
always much lower than engineers intuitively assume.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. [EXPLAIN] Explain why metrics should never be sampled
   while traces should be sampled, using the difference in
   how each signal type is used for diagnostics
2. [DEBUG] Your Prometheus cluster memory doubled in 2 weeks.
   Diagnose the cause (likely cardinality explosion) and
   identify the specific metric and label causing it using
   Prometheus API queries
3. [DECIDE] Design a sampling strategy for a service at
   50,000 RPS with 0.1% error rate - quantify cost savings
   and diagnostic coverage for: 100% capture, 1% head-based,
   tail-based (100% errors + 1% normal)
4. [BUILD] Configure an OTel Collector tail-based sampling
   policy that retains all ERROR traces, all traces with
   latency >500ms, and 2% of remaining traces
5. [EXTEND] Design a multi-cluster Prometheus federation
   using Thanos for a 20-region global deployment - cover
   data replication, deduplication, and cross-region query

---

### 🎯 Interview Deep-Dive

**Q1: Your observability costs doubled last quarter without
a corresponding doubling in services. How do you diagnose
the cause?**
_Strong answer includes:_

- Check Prometheus series count trend (cardinality explosion?)
- Check Jaeger trace volume (new high-traffic service added
  with 100% sampling?)
- Check Elasticsearch indexing volume (INFO logs being indexed
  instead of archived?)
- Identify which signal type (metrics/traces/logs) doubled
  and trace it to a recent change

**Q2: Explain the trade-off between head-based and tail-based
trace sampling in production.**
_Strong answer includes:_

- Head-based: zero buffer overhead, but may discard error
  traces before they are known to be errors
- Tail-based: captures 100% of errors because decision is
  made after trace completes, but requires stateful buffer
  (memory-intensive at high volume)
- Consistent head-based: intermediate - deterministic
  sampling by trace_id ensures coherent traces but still
  cannot route on trace outcome

**Q3: Your Prometheus cluster is at 80% memory and growing.
How do you reduce cardinality without losing diagnostic value?**
_Strong answer includes:_

- Find high-cardinality metrics using Prometheus API
- Identify which labels have unbounded values
- Remove the label from the metric; use tracing for
  individual request correlation
- Implement a cardinality alert so this doesn't recur
- Add recording rules to pre-aggregate high-cardinality
  metrics into lower-cardinality summaries
