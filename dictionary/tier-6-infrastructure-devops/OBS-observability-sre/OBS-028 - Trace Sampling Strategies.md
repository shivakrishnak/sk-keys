---
id: OBS-028
title: Trace Sampling Strategies
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★☆
depends_on: OBS-008, OBS-017, OBS-018
used_by: OBS-039, OBS-047
related: OBS-008, OBS-017, OBS-018, OBS-034, OBS-039
tags:
  - observability
  - tracing
  - devops
  - sre
  - pattern
  - intermediate
  - tradeoff
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 28
permalink: /obs/trace-sampling-strategies/
---

# OBS-028 - Trace Sampling Strategies

⚡ TL;DR - Trace sampling determines which requests
have their full distributed trace recorded. At scale,
100% tracing is cost-prohibitive. The sampling strategy
you choose determines whether you can find the
traces you need when an incident happens - or whether
the interesting traces (errors, slow paths) were
silently discarded.

| #028            | Category: Observability & SRE                                  | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Tracing Fundamentals, OpenTelemetry, Jaeger/Zipkin |                 |
| **Used by:**    | Observability at Scale, Distributed Tracing Architecture       |                 |
| **Related:**    | Distributed Tracing, OpenTelemetry, eBPF Observability         |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A high-traffic e-commerce platform processes 50,000
requests per second. Every request generates a
distributed trace with 15 spans across 8 services.
Each trace is ~5 KB in storage. 100% tracing costs:
50,000 req/s x 5 KB x 86,400 s/day = 21.6 TB/day.
At $0.023/GB (AWS S3), that is $497/day in storage
alone. Plus ingest costs, query costs, bandwidth.
Total: ~$25,000/month for trace storage.

The team chooses 1% random sampling to cut costs.
Cost drops to $250/month. But now: when a 500ms
latency spike affects checkout at 14:32, the trace
for that specific request has a 99% chance of being
discarded. The engineer searches Jaeger and finds
only fast, successful traces from that time window.
The root cause cannot be found.

**THE INVENTION:**
Intelligent sampling strategies that keep interesting
traces (errors, slow requests, specific users) while
discarding uninteresting ones (fast, successful,
routine). The goal: 1% of traces stored, but 100%
of the traces you will ever actually need are kept.

---

### 📘 Textbook Definition

**Trace sampling** is the process of selecting which
distributed traces to record, transmit, and store.

**Sampling rate**: the fraction of requests that
produce a complete stored trace.

- `1.0` = 100% (all traces stored)
- `0.01` = 1% (1 in 100 traces stored)
- `0.001` = 0.1% (1 in 1000 traces stored)

**The sampling decision** determines whether a full
trace is recorded for a given request. Once made,
the decision must propagate to all downstream services
in the call chain (via the `sampled` flag in W3C
traceparent or B3 headers) so all spans in a trace
are consistently recorded or discarded.

**Sampling taxonomy:**

- **Head-based**: decision made at request start
- **Tail-based**: decision made after request completes
  (when full trace is available)
- **Adaptive**: sampling rate adjusts to traffic volume
- **Deterministic**: same trace ID always produces
  the same sampling decision (avoids partial traces)

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Sampling decides which traces to keep - the challenge
is that you need to keep the traces you want (errors,
slow paths) while discarding the ones you do not need
(fast, successful, routine).

> Imagine recording every phone call a call centre
> receives (100%). Too expensive - store 100%? Or
> record randomly (1%)? If you record randomly, you
> will rarely capture the calls where customers complained
> about billing errors. Instead: record all complaint
> calls (100% of calls where the customer asked for
> a supervisor), record all long calls (> 10 minutes),
> and sample 1% of routine calls. Now you have the
> evidence you need when the billing system has a bug,
> without storing every routine "where is my order?"
> conversation.

---

### 🔩 First Principles Explanation

**HEAD-BASED SAMPLING:**

The sampling decision is made at the entry point
(front door service, load balancer, API gateway)
before the request is processed. The decision is
encoded in the traceparent header and propagated
to all downstream services.

```
Request arrives at API gateway
  ↓
Sampling decision: Math.random() < 0.01
  → TRUE (1% chance): set sampled=1 in header
  → FALSE (99% chance): set sampled=0 in header
  ↓
All downstream services read sampled flag:
  sampled=1: record spans, send to collector
  sampled=0: create no-op spans (zero overhead)
  ↓
At trace completion:
  sampled=1: all spans arrive at Jaeger/Tempo
  sampled=0: no spans recorded anywhere
```

**Advantages:**

- Zero overhead for unsampled requests (no-op spans)
- Simple to implement in OpenTelemetry SDK
- Low latency: no buffering needed

**Disadvantage:**

- Decision made before outcome is known. An error
  that happens 200ms after the request starts was
  already sampled (or not) before it occurred.
- Cannot guarantee error traces are kept.

---

**TAIL-BASED SAMPLING:**

All spans for a request are buffered in a Collector
(or sampling proxy). After the request completes,
the full trace is evaluated against sampling rules.
High-value traces are forwarded to storage; low-value
traces are discarded.

```
Request starts: ALL spans sent to OTel Collector
  ↓
Collector buffers spans in memory per trace ID
  ↓
Request completes (root span closes)
  ↓
Sampling policy evaluation:
  Rule 1: status_code = ERROR → keep (100%)
  Rule 2: duration > 1000ms → keep (100%)
  Rule 3: user_tier = "premium" → keep (100%)
  Rule 4: otherwise → keep 1% (random)
  ↓
Matching trace:
  Keep → forward all spans to Jaeger/Tempo
  Discard → drop all spans, free buffer
```

**Advantages:**

- Keeps 100% of error traces, 100% of slow traces
- The traces you actually want are almost never
  discarded
- Configurable rules: keep by user segment, operation,
  service, tag value

**Disadvantage:**

- Memory overhead: entire trace buffered until root
  span arrives. At 50,000 req/s with average 500ms
  duration: buffer size = 50,000 x 0.5 x 5KB = 125MB
  minimum. With P99 latency = 5s: buffer = 50,000 x 5
  x 5KB = 1.25 GB. Requires significant Collector RAM.
- Latency: spans arrive at Collector with delay;
  trace assembly requires waiting for root span close.
- Requires a stateful Collector tier (cannot use
  stateless horizontal scaling without consistent
  hashing by trace ID).

---

**DETERMINISTIC (CONSISTENT) SAMPLING:**

Without deterministic sampling, 50% rate applied at
service A and 50% at service B will produce traces
where: A records the span but B does not (or vice
versa). The trace is incomplete - a useless broken
trace, not a useful partial trace.

```
# BAD: each service samples independently
Service A: Math.random() < 0.5 = YES (records span)
Service B: Math.random() < 0.5 = NO (skips span)
Service C: Math.random() < 0.5 = YES (records span)
Result: broken trace with gaps

# GOOD: deterministic - hash the trace ID
# Same trace ID always produces the same decision
def should_sample(trace_id: str, rate: float) -> bool:
    # Convert trace ID hex to integer
    trace_int = int(trace_id.replace("-", ""), 16)
    # Consistent across all services for same trace ID
    return (trace_int % 10000) < (rate * 10000)

# With 50% rate:
# trace_id=abc123... → int % 10000 = 3421 < 5000 → YES (all services)
# trace_id=def456... → int % 10000 = 7890 > 5000 → NO (no service)
```

OpenTelemetry SDK's `TraceIdRatioBased` sampler uses
deterministic sampling by default.

---

**ADAPTIVE SAMPLING:**

Sampling rate automatically adjusts to keep a target
throughput (e.g., 100 traces/second) regardless of
traffic volume.

```
Traffic: 1,000 req/s → sample 10% (100 traces/s)
Traffic: 10,000 req/s → sample 1% (100 traces/s)
Traffic: 100,000 req/s → sample 0.1% (100 traces/s)
Traffic: 50 req/s → sample 100% (50 traces/s, below target)
```

Used in: AWS X-Ray (reservoir sampling), Jaeger's
adaptive sampler, OTel Collector's probabilistic
sampler processor.

---

### 🧪 Thought Experiment

**THE SAMPLING TRAP:**

You have 100 services. You deploy 1% random head-based
sampling. Your error rate is 0.1% (1 in 1000 requests
fails). In a day, 10 million requests are processed.
10,000 will fail. With 1% sampling, only 100 failed
traces will be stored. Meanwhile, 100,000 successful
traces are stored.

You also have a specific bug that only manifests
when: (a) the user has > 1000 items in their cart
AND (b) the payment service is under high load AND
(c) the inventory service returns a specific edge-case
response. This combination occurs 3 times per day.

With 1% random sampling: the probability that at
least one of the 3 buggy traces is sampled = 1 -
(0.99)^3 = 2.97%. So 97% of the time, you have zero
evidence of this bug in your trace store. It takes
an average of 33 days before you get even one trace
that shows the bug path.

With tail-based sampling (rule: keep all errors +
slow requests):

- All 3 buggy traces are errors → 100% kept
- On day 1 you have evidence. Root cause found.

**The insight:** random head-based sampling is not
"good enough" for debugging. It systematically
discards exactly the traces you need most.

---

### 🧠 Mental Model / Analogy

> A hospital pathology lab receives 10,000 blood
> samples per day. Processing and storing all of them
> at full detail is too expensive. The lab's sampling
> strategy: all samples flagged "abnormal" by the
> automated analyser are processed fully (100%); all
> samples from high-risk patient groups are processed
> fully (100%); routine annual checkup samples for
> healthy patients are processed at 10% (statistical
> population monitoring). The 90% of routine samples
> discarded are predictable, boring, and their absence
> causes zero diagnostic harm. The 100% of abnormal
> samples kept are the ones clinicians will actually
> look at.
>
> Tail-based trace sampling works the same way. The
> "abnormal" traces (errors, slow requests) are the
> ones diagnosticians will look at. The "routine"
> traces (fast, successful) are kept at low rates for
> statistical baseline measurement.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone):**
Sampling means "only record some requests as traces,
not all." The challenge is making sure the interesting
requests (errors, slow ones) are always in the "some"
category.

**Level 2 - How to use it (junior):**
Use the OpenTelemetry SDK's `TraceIdRatioBased(0.01)`
sampler for 1% random sampling. Use `ParentBased`
to ensure child spans follow the parent's decision.
Do not implement independent sampling in each service
(causes broken traces). Start with 1% random and
measure: are your error traces present in Jaeger?

**Level 3 - How it works (mid-level):**
Head-based = decision at request start, propagated
via `sampled` flag in traceparent header. Tail-based
= buffer all spans, evaluate complete trace after
root span closes, apply rules (error/slow/user tier).
Deterministic = hash trace ID for consistency across
services. Adaptive = rate adjusts to traffic to hit
a target throughput. For production debugging,
tail-based is required - head-based discards errors
at the same rate as successes.

**Level 4 - Cost/design (senior):**
Tail-based Collector sizing: buffer memory = max
concurrent traces x average trace size. For 50,000
req/s, P99 5s latency: 50,000 x 5 = 250,000 concurrent
traces x 5KB = 1.25 GB buffer per Collector instance.
With redundancy: 3 Collector instances each holding
1.25 GB trace buffer. Consistent hashing for stateful
fan-out: all spans for the same trace_id must route
to the same Collector instance (use consistent hashing
on trace_id in the OTel Collector load balancer
exporter). Cost model: target 10-100 MB/s storage
ingest to Jaeger/Tempo, not 50+ GB/s.

**Level 5 - Platform design (staff):**
Multi-tier sampling architecture: head-based at
edge (1%) for baseline load control, tail-based in
Collector tier for error/slow guarantees, adaptive
layer for cost management. Dynamic sampling policy
API: sampling rules updated at runtime without
redeployment (Jaeger adaptive sampler pulls config
from remote). Cross-service sampling budget: if
Collector buffer fills (OOM risk), degrade sampling
rate for low-priority services first, maintain 100%
for tier-1 services. Sampling observability: the
sampling decision itself is a metric (traces_sampled_total,
traces_dropped_total, buffer_utilization) monitored
by the observability platform team.

---

### ⚙️ How It Works (Mechanism)

**OTEL COLLECTOR - TAIL SAMPLING PIPELINE:**

```yaml
# otelcol-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

processors:
  # Step 1: Route spans by trace_id to a single
  # Collector instance (required for tail sampling)
  # (Use load_balancing exporter upstream for this)

  tail_sampling:
    decision_wait: 30s # Wait 30s for root span
    num_traces: 50000 # Max traces buffered in memory
    expected_new_traces_per_sec: 1000
    policies:
      # Policy 1: Always keep error traces
      - name: errors-policy
        type: status_code
        status_code:
          status_codes: [ERROR]

      # Policy 2: Keep slow requests (> 1 second)
      - name: slow-traces-policy
        type: latency
        latency:
          threshold_ms: 1000

      # Policy 3: Keep traces tagged as "premium"
      - name: premium-user-policy
        type: string_attribute
        string_attribute:
          key: user.tier
          values: [premium, enterprise]

      # Policy 4: 1% random sample of everything else
      - name: baseline-policy
        type: probabilistic
        probabilistic:
          sampling_percentage: 1

exporters:
  otlp/jaeger:
    endpoint: jaeger-collector:4317

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [tail_sampling]
      exporters: [otlp/jaeger]
```

**OTEL SDK - HEAD-BASED SAMPLING SETUP:**

```java
// Java - deterministic head-based sampling at 1%
// Uses trace ID hash for consistency across services

SdkTracerProvider tracerProvider = SdkTracerProvider
  .builder()
  .setSampler(
    // ParentBased: if parent says "sampled", respect it
    // If no parent: use TraceIdRatioBased (1%)
    Sampler.parentBased(
      Sampler.traceIdRatioBased(0.01)
    )
  )
  .addSpanProcessor(
    BatchSpanProcessor.builder(
      OtlpGrpcSpanExporter.builder()
        .setEndpoint("http://otel-collector:4317")
        .build()
    ).build()
  )
  .build();

// IMPORTANT: ParentBased ensures:
// If the upstream (Nginx, API gateway) said sampled=0,
// this service also creates no-op spans.
// Without ParentBased: each service makes independent
// decisions → broken traces (missing spans).
```

---

### 🔄 The Complete Picture - End-to-End Flow

**HYBRID SAMPLING ARCHITECTURE:**

```
[User Request → Load Balancer]
  ↓
[API Gateway (head-based, 10%)]
  Sets sampled flag in W3C traceparent header
  sampled=1: 10% of requests flow through
  sampled=0: downstream services create no-ops
  ↓
[Services A, B, C (ParentBased sampler)]
  All respect the sampled flag from API gateway
  sampled=1: all 3 services create and export spans
  sampled=0: no-op spans, zero overhead
  ↓
[OTel Collector (tail-based, rules-based)]
  Receives 10% of all spans (from head-based gate)
  Buffers by trace_id (30s wait for root span)
  Applies policies:
    errors: keep 100% → stored
    slow: keep 100% → stored
    premium: keep 100% → stored
    other: keep 10% of remaining 10% = 1% total
  ↓
[Jaeger / Grafana Tempo (final storage)]
  Stores:
    100% of error traces
    100% of slow traces
    100% of premium user traces
    1% of routine traces (statistical baseline)
  Total stored: ~2-5% of all requests
  But: 100% of the traces you will actually need
```

---

### 💻 Code Example

**Example 1 - BAD: Independent sampling per service:**

```java
// BAD: each service independently decides whether to sample
// This is the DEFAULT if you do not use ParentBased sampler

// Service A (checkout): 50% sampling
SdkTracerProvider.builder()
  .setSampler(Sampler.traceIdRatioBased(0.5))
  // No ParentBased wrapper!

// Service B (inventory): 50% sampling
SdkTracerProvider.builder()
  .setSampler(Sampler.traceIdRatioBased(0.5))
  // No ParentBased wrapper!

// Result for a given trace_id:
// A samples it (50% chance): YES
// B independently flips its own coin: NO
// Jaeger trace: checkout span present, inventory span absent
// The trace appears to skip inventory entirely.
// Is it a bug? Is it a sampling artifact?
// The engineer cannot tell. Useless trace.
```

**Example 2 - GOOD: ParentBased with deterministic root:**

```java
// GOOD: ParentBased sampler ensures consistency
// Entry point (API gateway): makes the decision
// All downstream services: respect the decision

// API Gateway (makes the sampling decision):
SdkTracerProvider.builder()
  .setSampler(
    // 10% at the edge - deterministic hash of trace_id
    Sampler.traceIdRatioBased(0.10)
    // No ParentBased here - this IS the decision maker
  )

// All downstream services:
SdkTracerProvider.builder()
  .setSampler(
    Sampler.parentBased(
      // Fallback for unexpected root spans: 10%
      Sampler.traceIdRatioBased(0.10)
    )
  )
// Now: if trace_id=abc123 was sampled at the API gateway,
// ALL services sample it consistently.
// If it was not sampled: ALL services create no-op spans.
// Zero broken traces.
```

**Example 3 - Tail-based cost analysis:**

```python
# Calculate tail-based Collector memory requirements

requests_per_second = 50_000
p99_latency_seconds = 5.0    # buffer until root span
avg_trace_size_bytes = 5_000  # 5 KB per trace

# Max concurrent buffered traces
max_concurrent = requests_per_second * p99_latency_seconds
# = 50,000 * 5 = 250,000 traces

# Memory required for buffer
buffer_bytes = max_concurrent * avg_trace_size_bytes
# = 250,000 * 5,000 = 1,250,000,000 bytes = 1.25 GB

# Add overhead factor (hash maps, metadata, GC pressure)
overhead_factor = 2.5
required_memory_gb = (buffer_bytes * overhead_factor
  / 1_073_741_824)
# = 1.25 * 2.5 = 3.125 GB RAM per Collector instance

# For high availability (3 instances):
total_memory_gb = required_memory_gb * 3
print(f"Required Collector RAM: {total_memory_gb:.1f} GB")
# Output: Required Collector RAM: 9.4 GB
# Deploy as: 3 x r6i.xlarge (32 GB RAM instances)
# or use Grafana Tempo's streaming tail sampling
# which reduces memory via streaming aggregation
```

---

### ⚖️ Comparison Table

| Strategy                | Decision point   | Keeps errors?       | Memory         | Complexity | Best for                        |
| ----------------------- | ---------------- | ------------------- | -------------- | ---------- | ------------------------------- |
| Head-based (random)     | Request start    | 1% of errors lost   | Low            | Simple     | Dev/staging; baseline telemetry |
| Head-based (rate limit) | Request start    | 1% of errors lost   | Low            | Simple     | Traffic smoothing               |
| Tail-based (rules)      | Request complete | 100% of errors kept | High (1-10 GB) | High       | Production debugging            |
| Adaptive                | Request start    | 1% of errors lost   | Low            | Medium     | Autoscaling services            |
| Always-on               | N/A              | 100% kept           | Very high      | None       | Dev only, low traffic           |

**Sampling rate vs storage cost (1000 req/s, 5KB/trace):**

| Rate | Traces/day | Storage/day | Storage/month | Cost/month (S3) |
| ---- | ---------- | ----------- | ------------- | --------------- |
| 100% | 86.4M      | 432 GB      | 13 TB         | $302            |
| 10%  | 8.64M      | 43.2 GB     | 1.3 TB        | $30             |
| 1%   | 864K       | 4.32 GB     | 130 GB        | $3              |
| 0.1% | 86.4K      | 432 MB      | 13 GB         | $0.30           |

---

### ⚠️ Common Misconceptions

| Misconception                                      | Reality                                                                                                                                                                       |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "1% sampling means I see 1% of errors"             | With random head-based sampling, yes. With tail-based error sampling, you see 100% of errors (that is the point).                                                             |
| "Higher sampling rate = more useful traces"        | Not if the extra traces are all routine successful requests. A 1% tail-sampled store with 100% error capture is more useful than 10% random with 90% errors missing.          |
| "ParentBased sampler is optional"                  | Without it, every service samples independently and produces broken traces. ParentBased is required for multi-service tracing.                                                |
| "Tail-based sampling is always better"             | Tail-based requires 1-10 GB Collector RAM, stateful Collector tier, and consistent hash routing. For small traffic or simple systems, head-based is simpler and sufficient.   |
| "The sampling decision is hidden in SDK internals" | The decision is explicitly propagated in the W3C traceparent header (`traceflags` byte, last bit = sampled flag). Every service in the chain can inspect and must respect it. |

---

### 🚨 Failure Modes & Diagnosis

**Broken traces (missing spans from some services)**

**Symptom:**
In Jaeger, a trace shows spans from Service A and
Service C but is missing Service B (which sits
between them in the call chain). The trace appears
to show A calling C directly, which is architecturally
impossible.

**Root Cause:**
Service B is using an independent sampler (not
`ParentBased`). When trace_id=abc123 was sampled
by A (50% chance), B independently flipped its own
coin and decided not to sample (50% chance). C used
ParentBased and read the sampled flag from B's
outgoing header - but B, having decided not to sample,
set sampled=0 in the header, causing C to also create
no-op spans. So the trace has A's span, nothing from
B, and nothing from C.

**Diagnosis:**

```bash
# Check sampler configuration across services
# In OTel SDK logs (DEBUG level):
# Look for: "Sampler: TraceIdRatioBased" vs
#   "Sampler: ParentBased{root=TraceIdRatioBased}"
# The first is the anti-pattern.

# In the Jaeger trace:
# Open affected trace → check span timeline
# A service with missing spans but present neighbors:
# almost always an independent sampler problem
```

**Fix:**

```java
// Replace in all downstream services:
// BEFORE (broken):
.setSampler(Sampler.traceIdRatioBased(0.1))

// AFTER (correct):
.setSampler(Sampler.parentBased(
  Sampler.traceIdRatioBased(0.1)
))
```

---

**Tail-based Collector OOM (out of memory)**

**Symptom:**
OTel Collector pods are OOM-killed repeatedly.
Kubernetes restarts them every 10-15 minutes. During
the restart window, no traces are collected at all.
The trace store has 10-minute gaps matching each
restart cycle.

**Root Cause:**
`num_traces` in the tail sampling config (250,000)
x average trace size (15 KB - underestimated during
config) = 3.75 GB. Collector was provisioned with
2 GB RAM limit. Under normal load it was fine (traces
averaged 5 KB), but a new microservice was deployed
with verbose spans, increasing average trace size 3x.

**Fix:**

```yaml
# Reduce num_traces or increase memory limit
tail_sampling:
  decision_wait:
    10s # Reduce from 30s to 10s
    # Clears buffer 3x faster
  num_traces:
    100000 # Reduce from 250,000
    # Monitor buffer utilization metric:
    # otelcol_processor_tail_sampling_
    #   sampling_decision_timer_latency

# Also: add a head-based pre-filter before tail sampling
# to reduce the volume entering the Collector:
# probabilistic processor at 10% BEFORE tail_sampling
# reduces buffered traces 10x
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Distributed Tracing Fundamentals` - traces, spans,
  context propagation - the base that sampling builds on
- `OpenTelemetry -- The Standard` - the SDK and
  Collector that implement sampling strategies
- `Jaeger / Zipkin -- Distributed Tracing` - the
  backends that store sampled traces

**Builds On This (learn these next):**

- `Observability at Scale (Sampling, Aggregation)` -
  combines trace sampling with metrics aggregation
  for high-scale observability architecture
- `Distributed Tracing System Architecture` - the
  full architecture including Collector tiers and
  storage backends

**Alternatives / Comparisons:**

- `eBPF for Observability` - kernel-level tracing that
  captures traces without SDK instrumentation. Does
  not require sampling decisions in application code,
  but has its own data reduction challenges at scale.

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ HEAD-BASED   │ Decision at request start                 │
│              │ Simple, low overhead                      │
│              │ Discards errors at same rate as successes │
├──────────────┼───────────────────────────────────────────┤
│ TAIL-BASED   │ Decision after request completes          │
│              │ Keeps 100% of errors and slow traces      │
│              │ Needs 1-10 GB Collector RAM               │
├──────────────┼───────────────────────────────────────────┤
│ DETERMINISTIC│ Hash trace_id for consistent decision     │
│              │ Same trace_id → same decision in all      │
│              │ services → no broken traces               │
├──────────────┼───────────────────────────────────────────┤
│ CRITICAL     │ Use ParentBased sampler in all downstream │
│ RULE         │ services - never independent samplers     │
│              │ Independent sampler → broken traces       │
├──────────────┼───────────────────────────────────────────┤
│ TAIL CONFIG  │ decision_wait: 30s (root span timeout)    │
│              │ num_traces: buffer size (watch OOM)       │
│              │ policies: errors, latency, attributes, %  │
├──────────────┼───────────────────────────────────────────┤
│ COST MODEL   │ 50k req/s, 5KB/trace, 1% rate = ~$3/mo   │
│              │ Tail-sampled: same cost, 100% error cover │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Random head-based discards error traces   │
│              │ Independent sampling = broken traces      │
│              │ Undersized Collector → OOM → trace gaps   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ OpenTelemetry -- The Standard             │
│              │ Observability at Scale                    │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Sample strategically, not uniformly. Uniform sampling
(random N%) is simple but it discards rare important
events at the same rate as common unimportant ones.
This principle applies beyond tracing: log sampling
(log all errors, sample 1% of INFO), database query
logging (log all slow queries > 1s, sample 0.1% of
fast queries), event streaming (keep all fraud signals,
sample 1% of routine transactions), A/B testing
(always include edge cases in the sample, not just
the statistical majority). The pattern: define what
is "important" (error, slow, rare, high-value) and
sample those at 100%; sample everything else at a
rate that provides statistical coverage without
overwhelming storage.

---

### 💡 The Surprising Truth

The most counterintuitive trace sampling insight:
1% tail-based sampling is often more useful than
10% head-based sampling. At first this seems wrong -
surely 10x more traces gives 10x more visibility?
In practice, 99% of traces are routine fast successful
requests. A 10% head-based store is 99% routine
fast successful requests. A 1% tail-based store
(keeping all errors + slow requests) is ~50% errors,
~30% slow requests, ~20% routine samples. The tail-
based store is 80% signal; the head-based store is
1% signal (if the error rate is 1%). You can diagnose
an incident with 100 error traces far better than
you can with 100,000 successful traces and 100
(randomly sampled) error traces that may not include
the specific failure path you need.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[EXPLAIN]** Describe the difference between
   head-based and tail-based sampling, including
   why tail-based requires a stateful Collector
   while head-based does not.
2. **[CONFIGURE]** Write an OTel Collector tail
   sampling config that keeps 100% of error traces,
   100% of traces slower than 1s, and 1% of all
   other traces.
3. **[DEBUG]** A Jaeger trace shows spans from
   Service A and C but not B. Diagnose the cause
   and write the fix.
4. **[SIZE]** Given 10,000 req/s and P99 latency
   of 3s and 4KB average trace size, calculate
   the Collector buffer memory required for tail
   sampling. Apply an overhead factor of 2x.
5. **[DESIGN]** Design a hybrid sampling strategy
   for a service that handles 100,000 req/s, must
   capture 100% of errors, must stay within $500/month
   trace storage budget, and must keep tail-based
   Collector memory under 8 GB.

---

### 🧠 Think About This Before We Continue

**Q1.** You have 1,000 req/s. The error rate is
0.2% (2 errors/second). You use 1% random head-based
sampling. In a 1-hour window, how many error traces
do you expect to have in Jaeger? If a bug occurs
for exactly 10 minutes (causing 5% error rate, 50
errors/minute), how many error traces from that
10-minute window do you expect to have?
_Hint: Normal: 0.2% error rate x 1% sample = 0.002%
of all requests are sampled error traces. In 1 hour
= 3,600 seconds x 1,000 req/s = 3.6M requests.
Sampled errors: 3.6M x 0.002% = 72 error traces.
During the 10-min bug window: 50 errors/min x 10
min = 500 total errors. With 1% sampling: ~5 error
traces captured. With tail-based (100% errors kept):
500 error traces. The difference: 5 traces showing
the bug vs 500 traces showing it. For diagnosis:
5 may be enough, but there is a 36.6% chance that
ZERO of the 5 captured traces show the exact stack
path causing the bug if the bug is rare within
the error traces._

**Q2.** Your Collector is configured with
`decision_wait: 30s` and `num_traces: 100,000` at
1,000 req/s. What is the maximum average trace size
that can be safely buffered in 4 GB of RAM? If a
new verbose service doubles the average trace size,
what happens and how do you detect it before OOM?
_Hint: Max buffer: 4 GB / 100,000 traces = 40 KB/trace
(with no overhead). With 2x overhead: 20 KB/trace
max. If verbose service doubles from 10 KB to 20 KB:
buffer = 100,000 x 20 KB x 2 = 4 GB → borderline.
Detect early: monitor `otelcol_processor_tail_sampling_
sampling_decision_timer_latency` metric and Collector
RSS memory. Alert when Collector RAM > 70% of limit.
Fix: reduce decision_wait to 10s (reduces concurrent
traces 3x) or increase Collector memory._

**Q3 (TYPE G):** Design a complete trace sampling
strategy for a global payments platform that: processes
500,000 req/s globally, has a 0.01% error rate (50
errors/second), must keep all error traces, must keep
traces > 500ms, must support ad-hoc "sampling session"
for a specific user ID for 30 minutes (for debugging
a complaint), must stay within $5,000/month trace
storage, and must not use more than 32 GB total
Collector RAM. Show the architecture, the Collector
config, and the cost model.
_Hint: Two tiers. Tier 1 (edge, head-based): 2%
random sampling → reduces 500k to 10k req/s entering
Collector tier. Tier 2 (Collector, tail-based): rules:
errors (100% kept from 10k/s sample), latency > 500ms
(100% kept), user_id match (dynamic rule via API,
100% kept for 30-min window), baseline 0.5% of remainder.
Collector RAM: 10,000 req/s x 2s P99 x 5KB x 2.5 overhead
= 250 GB... too high. Solution: two-stage. First
stage head-based reduces to 10k. At 10k/s x 2s x 5KB
x 2.5 = 250 MB per Collector instance. Very manageable.
Storage: errors: 50/s x 86400 x 30 x 5KB = 648 GB/month.
Slow traces: estimate 0.1% of 500k = 500/s... 6.5 TB/month.
Too high. Cap slow traces at 100% of error-sampled + 10%
of slow. Cost math included._

---

### 🎯 Interview Deep-Dive

**Q1: "What is the difference between head-based
and tail-based trace sampling?"**
_Why they ask:_ Tests deep understanding of distributed
tracing infrastructure, not just surface API usage.
_Strong answer includes:_

- Head-based: decision at request start, propagated
  in traceparent header. Simple, low overhead. Cannot
  guarantee error traces are kept (they are sampled
  at the same rate as successful traces).
- Tail-based: all spans buffered in Collector, decision
  made after root span closes. Can keep 100% of errors,
  slow requests, and high-value users. Requires
  stateful Collector with significant RAM (1-10 GB).
- The key trade-off: head-based is simple and cheap;
  tail-based keeps the traces you actually need for
  debugging but requires infrastructure investment.
- For most production systems: hybrid is best. Head-based
  at edge for traffic control, tail-based in Collector
  for diagnostic value.

**Q2: "Why do broken traces (missing spans) appear
in Jaeger, and how do you fix them?"**
_Why they ask:_ Common production problem that reveals
whether the engineer understands propagation mechanics.
_Strong answer includes:_

- Most common cause: independent sampling in each
  service instead of ParentBased. Service A samples
  at 50%, Service B independently samples at 50%.
  A records its span; B independently decides not
  to sample and sets sampled=0 in its outgoing header.
  C reads sampled=0 from B and creates no-op spans.
  Result: A's span is present, B and C are absent.
- Fix: use `Sampler.parentBased(root_sampler)` in
  all downstream services. The root sampler (at API
  gateway) makes the decision; all others respect it.
- Also causes: spans sent to different Collector
  instances without consistent hash routing when
  using tail sampling.

**Q3: "How would you design trace sampling for a
service handling 100,000 requests per second?"**
_Why they ask:_ Tests ability to reason about cost,
architecture, and trade-offs at scale.
_Strong answer includes:_

- 100% sampling at 100k req/s = 100k x 5KB x 86400s
  = 43 TB/day. Not feasible.
- Strategy: hybrid. Head-based at edge (5%) reduces
  ingest to 5,000 traces/s entering Collector. Tail-
  based in Collector (errors 100%, slow > 1s 100%,
  baseline 1% of remainder).
- Collector sizing: 5,000 traces/s x P99 latency
  (3s) x 5KB x 2.5 overhead = ~188 MB RAM per
  instance. Feasible on standard VMs.
- Expected storage: errors (5k/s x 0.01% = 0.5/s),
  slow (assume 0.5% of 5k = 25/s), baseline (5k
  x 1% = 50/s). Total ~76/s = ~13M traces/day =
  ~65 GB/day = ~2 TB/month. At $0.023/GB = ~$46/month.
  Very feasible.
- Key design decision: consistent hash routing in
  front of Collector instances so all spans for the
  same trace_id go to the same Collector instance.

> Entry stub. Generate full content using Master Prompt v3.0.
