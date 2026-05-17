---
id: OBS-045
title: Observability System Design Internals
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★★
depends_on: OBS-001, OBS-006, OBS-008, OBS-015, OBS-027, OBS-039, OBS-041, OBS-046, OBS-047
used_by: OBS-051
related: OBS-044, OBS-038, OBS-040
tags:
  - observability
  - reliability
  - devops
  - sre
  - advanced
  - internals
  - system-design
  - production
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 45
permalink: /obs/observability-system-design-internals/
---

# OBS-045 - Observability System Design Internals

⚡ TL;DR - Building an observability system means solving
four hard problems simultaneously: ingesting high-volume
telemetry without dropping data, storing time-series data
efficiently with variable retention, querying across
billions of data points under 1 second, and correlating
three separate data streams (metrics, logs, traces) by
time and trace ID.

| #045            | Category: Observability & SRE                                                                                                                                                                                                | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | What Is Observability, Prometheus, Distributed Tracing, Grafana, Log Aggregation at Scale, Observability at Scale, Observability Platform Architecture, Time-Series Database Design, Distributed Tracing System Architecture |                 |
| **Used by:**    | Reliability Mental Model                                                                                                                                                                                                     |                 |
| **Related:**    | Platform Observability Engineering, Capacity Planning with Metrics, SRE Book Core Principles                                                                                                                                 |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You are asked in a system design interview (or a staff
engineering review) to design a monitoring system for
a 500-service platform processing 1 million requests/sec.
You know the high-level components: Prometheus, Grafana,
logs. But when pressed on internals - "how does Prometheus
store 10 million time series without running out of memory?",
"how does Loki make log queries across 1TB of logs return
in 2 seconds?", "how do you correlate a trace with the
logs from that specific request across 5 services?" -
you cannot answer. You can name the tools but cannot
explain why they work, what their limits are, or how
to design around those limits.

**THE BREAKING POINT:**
At senior/staff level, not knowing the internals creates
a critical gap: you can configure existing systems but
cannot diagnose when they fail in novel ways, cannot
evaluate trade-offs between systems, and cannot design
a system that scales beyond the defaults. System design
interviews and architecture reviews both expose this gap
immediately.

**THE INVENTION MOMENT:**
Understanding observability system design internals means
understanding the data structures and algorithms that make
each component fast at its job: time-series databases
use chunk-based columnar compression; distributed log
systems use inverted indexes for label queries; trace
storage systems use sparse indexes with trace-ID sharding.
Knowing these internals converts abstract component names
into a system you can reason about and design for.

---

### 📘 Textbook Definition

**Observability system design internals** refers to the
data structures, storage models, compression algorithms,
query execution engines, and correlation mechanisms that
enable an observability platform to: ingest millions of
metric samples per second, store years of time-series
data efficiently, query billions of log lines in under
2 seconds, and correlate traces spanning multiple services
across days of historical data. Key internals include:
TSDB chunk compression for metrics, inverted label indexes
for log and trace queries, bloom filters for trace ID
lookup, and the correlation model that joins metrics,
logs, and traces by time + trace ID.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The internals are what make "a database for time-series
data" work at 10 million series without collapsing under
its own memory pressure.

**One analogy:**

> Understanding observability internals is like understanding
> how a library's card catalog works, not just how to use
> the library. A library patron just asks the librarian
> for a book. A librarian can find any book in 30 seconds
> because the card catalog organizes books by subject,
> author, and date. Without that organization, finding
> a specific book in a 10-million-book library would
> take hours. Observability internals are the "card catalog
> design" - they determine whether a query across 1 year
> of metrics returns in 200ms or 200 seconds.

**One insight:**
The key insight across all observability systems is that
the data is append-only (new data always goes to the
newest time range) and time-bounded queries (most queries
ask about recent data) create specific access patterns
that every system exploits: recent data lives in memory
or fast local storage; old data is compressed and shipped
to cheap object storage. The compression ratios matter
enormously - Prometheus achieves 1.37 bytes per sample
(vs 16 bytes raw) through delta-of-delta encoding.

---

### 🔩 First Principles Explanation

**TSDB INTERNALS (Prometheus):**

**The memory-to-disk problem:**
A time series is an ordered sequence of (timestamp, value)
pairs. Naive storage: 16 bytes per sample (8-byte timestamp

- 8-byte float64 value). At 1M active series × 1 sample/15s
  over 2 hours (in-memory window): 1M × 480 samples × 16B
  = 7.6GB of raw data in RAM just for 2 hours of metrics.
  Prometheus uses head blocks (in RAM) with XOR compression
  from the Gorilla paper (Facebook 2015):

```
Delta-of-delta timestamp encoding:
  t₀ = 1700000000
  t₁ = 1700000015  → delta = 15
  t₂ = 1700000030  → delta = 15, delta-of-delta = 0
  t₃ = 1700000060  → delta = 30, delta-of-delta = 15
  Most timestamps have delta-of-delta = 0 → 1 bit!

XOR value encoding:
  v₀ = 12.0   → stored as full float64 (8 bytes)
  v₁ = 12.1   → XOR(12.0, 12.1) has leading zeros
               → store only the significant bits
  Most metrics change slowly → high compression ratio
  Result: ~1.37 bytes per sample (vs 16 bytes raw)
  Compression ratio: 11.7x
```

**Chunk lifecycle:**

```
Head block (in RAM): last 2h of data
  ├── Chunks: 120-sample segments, XOR-compressed
  └── Index: label set → series ID → chunk offsets

Persistence (WAL replay on restart):
  Every 15min: head block checkpointed to WAL
  Every 2h: head block compacted to disk block
  Disk blocks: immutable once written

Block compaction:
  Level 0: raw 2h blocks (many, small)
  Level 1: 6h compacted blocks
  Level 2: 24h compacted blocks
  Level 3: 1-week blocks (max)

Tombstones: deleted series marked but not removed
  until next compaction (immutable block design)
```

**LOKI LOG INTERNALS:**

```
Log data model:
  stream = {namespace="prod", app="payment-api"}
  entries = [{timestamp, log_line}, ...]

Index design (minimalist vs Elasticsearch):
  Loki indexes ONLY the stream labels (namespace, app)
  NOT the log content
  → Index size 100x smaller than Elasticsearch
  → Log content stored as compressed chunks in S3

Query execution:
  Query: {app="payment-api"} |= "ERROR"
  Step 1: Index lookup → list of S3 chunk paths
          for matching stream labels
  Step 2: Retrieve chunks from S3 in parallel
  Step 3: Decompress and grep for "ERROR"

  Fast because: S3 chunks retrieved in parallel,
  only relevant streams fetched (label filtering),
  recent chunks cached in local disk (cache hit rate ~80%)

  Slow queries: no label filter (full scan) or
  regex on very high-cardinality log field
```

**TEMPO TRACE INTERNALS:**

```
Trace storage challenge:
  A trace ID is a random 128-bit value
  Querying "all traces where duration > 1s" requires
  a full scan of all traces (no obvious sort key)

Tempo's approach: object storage + local bloom filter
  1. Traces written to local SSD buffer (WAL)
  2. Every N minutes: flush to S3 as block
     - Block has: trace_id → offset index (sorted)
     - Bloom filter per block covering all trace IDs

  Query for trace ID:
    Check bloom filter for each block
    (~80-90% of blocks eliminated without S3 reads)
    For remaining blocks: binary search in offset index
    Fetch the trace object from S3

  Query for "all slow traces" (TraceQL):
    No efficient index → requires reading all blocks
    TraceQL pipelines this with pipeline hint caching
    Still O(data volume) - expensive for wide-time queries
```

---

### 🧪 Thought Experiment

**DESIGN CHALLENGE: 10TB/day log ingestion**

You receive 10TB of application logs per day. Requirements:

- Query any log line from the last 90 days in < 2 seconds
- Cost: < $2,000/month for storage
- No data loss

**DESIGN ANALYSIS:**

```
Storage cost with S3 standard: $0.023/GB/month
90 days × 10TB/day = 900TB
900TB × $0.023 = $20,700/month - 10x over budget

Solution: compression + tiering

Raw logs (10TB/day) compress to ~1TB/day with zstd
(text data compresses ~10:1)
90 days × 1TB/day = 90TB compressed
90TB × $0.023 = $2,070/month - within budget

Query performance:
To find "ERROR" in last 1 hour:
- 1 hour = 1TB/24 ≈ 40GB raw → 4GB compressed
- Loki fetches only the streams matching the label filter
- If {app="payment-api"} matches 5% of volume
  → fetch 200MB → decompress → grep
- At S3 throughput ~100MB/s: 2 seconds to fetch
- 200MB × 10:1 decompression at CPU: 0.5 seconds
- Total: ~2.5 seconds → close to requirement

To hit < 2s: use Loki bloom filter compactor
  (additional bloom filter on log content words)
  → eliminates 90% of chunk reads for exact word queries
  → 200ms → 20MB → 0.2 seconds ✓
```

---

### 🧠 Mental Model / Analogy

> Observability data internals is like a bank's transaction
> ledger system. The bank has billions of transactions
> (telemetry data points) that must be recorded instantly,
> never lost, queryable by account (label filter), and
> never modified once written. The bank uses three techniques:
> (1) append-only ledger (like WAL) - never modify, always
> append new entries; (2) periodic compaction (monthly
> statements) - aggregate and compress old data while
> preserving queryability; (3) tiered storage (online vs
> archive) - recent transactions in fast database, old
> transactions in compressed archives. The bank also
> maintains separate indexes (checking account index,
> by-date index) that enable fast queries without scanning
> every transaction. This is exactly what Prometheus, Loki,
> and Tempo do - with compression algorithms tuned to
> the specific statistical properties of each data type.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Observability systems store huge amounts of data (metrics,
logs, traces) efficiently and make it queryable quickly.
They use clever compression and indexing tricks to make
this practical. Without these tricks, storing and querying
a year of metrics would cost 100x more and take 100x longer.

**Level 2 - How to use it (junior developer):**
Understanding internals helps you configure systems
correctly: Prometheus's 2-hour head block size is why
queries over 2h use disk I/O; Loki's label-only index is
why you should put high-cardinality values in log content
not in stream labels; Tempo's bloom filter is why trace
lookup by ID is fast (milliseconds) but "all traces with
latency > 1s" is slow (seconds to minutes).

**Level 3 - How it works (mid-level engineer):**
Prometheus XOR compression (Gorilla paper), chunk-based
storage, head block → WAL → disk block lifecycle.
Loki label-indexed streams + compressed log chunks in S3,
querying by decompressing only matching stream chunks.
Tempo object storage with bloom filter index per block
for trace-ID lookup and TraceQL for content-based search.

**Level 4 - Why it was designed this way (senior/staff):**
Each system is optimized for its primary access pattern.
Prometheus is optimized for recent data queries (in RAM),
recent-to-historical range queries (read compact blocks),
and batch ingestion. The head block size (2h default)
balances RAM use against query speed. Loki is optimized
for stream-filtered log queries (most log queries include
a label filter) and minimizes index size to keep Loki
as stateless as possible (index goes to object storage).
Tempo is optimized for trace-ID point queries (the most
common use case: user reports slowness → find their trace).
TraceQL support for content queries is a recent addition
that trades storage for faster content-based queries.

**Level 5 - Mastery (distinguished engineer):**
The fundamental tension in all three systems is between
the cost of indexing (faster queries, more storage, more
RAM for index) and the cost of not indexing (slower queries,
less storage, simpler architecture). Prometheus chose to
index all label dimensions fully (every unique label set
creates a time series). This gives it O(1) time series
lookup but creates cardinality explosion when a label has
many unique values. Loki chose to index only stream labels
(not content), giving it massive storage efficiency but
requiring full chunk scans for content queries. Tempo
chose bloom filter indexes (probabilistic, compact) over
full indexes, trading perfect precision (bloom filters
have false positives, no false negatives) for drastically
reduced index storage. Understanding these trade-offs
lets you answer "what happens when my use case pushes
against these boundaries?" - which is the staff engineer
question in every system design review.

---

### ⚙️ How It Works (Mechanism)

**PROMETHEUS CHUNK COMPRESSION DETAIL:**

```
XOR Encoding for float64 values:

If v₁ = 1234.5 and v₂ = 1234.6:
  Binary representation:
  1234.5 = 0x4093400000000000
  1234.6 = 0x40934666...
  XOR   = 0x00000666...

  Leading zeros: 40 bits
  Trailing zeros: 10 bits
  Meaningful bits: 14 bits

  Storage: {40 leading zeros, 14 meaningful bits}
  = ~2 bytes vs 8 bytes raw

  For metrics that barely change (e.g., CPU at 23.1%
  for many samples), XOR produces near-zero output
  → compressed to 1-2 bits per sample in best case

Delta-of-delta timestamp encoding:
  Regular scrape at 15s intervals:
  t₀ = 0, t₁ = 15s, t₂ = 30s, ...
  Delta: 15, 15, 15, 15, ...
  Delta-of-delta: 0, 0, 0, 0, ...
  0 encodes to 1 bit (leading zero indicator)
  Irregular scrape: delta-of-delta ≠ 0 → variable bits
```

**LOKI QUERY EXECUTION:**

```
Query: {namespace="prod",app="api"} |= "TIMEOUT"
       for last 1 hour

Execution plan:
  1. Index lookup:
     namespace="prod" AND app="api"
     → returns list of stream IDs
     → stream IDs map to chunk store paths

  2. Chunk fetch:
     Get all chunk paths for matching streams
     in the 1-hour time range
     → Fetch chunks from S3 (or cache)
     → Parallel fetch (N goroutines)

  3. Decompress + filter:
     Decompress each chunk (zstd)
     Line-by-line grep for "TIMEOUT"
     Return matching lines with timestamps

  Performance impact:
  High cardinality labels: many chunks fetched
    → slow (must decompress all of them)
  Low cardinality labels: few chunks fetched
    → fast (decompress only matching streams)
  This is WHY: do not use request_id as a stream label
```

---

### 🔄 The Complete Picture - End-to-End Flow

**CROSS-SIGNAL CORRELATION FLOW:**

```
User reports: "My checkout was slow at 14:32 UTC"
User provides: their session_id = "abc123"

Step 1: Find the trace
  - Look up session_id in application log:
    Loki: {app="checkout"} |= "session_id=abc123"
    → Returns log line with trace_id=xyz789

Step 2: Load the trace
  - Tempo: GET /api/traces/xyz789
    → Returns full trace spanning 5 services
    → Shows slow span: payment-service.processPayment
      duration: 8.2 seconds (expected: < 200ms)

Step 3: Correlate with metrics
  - Prometheus: query payment_service_latency_p99
    at time range [14:31, 14:34]
    → Shows p99 was 8 seconds during this window
    → CPU and memory are normal → not resource-bound

Step 4: Investigate logs of slow span
  - Loki: {app="payment-service"} | trace_id="xyz789"
    → Shows: "DB connection pool exhausted, waited 7.8s"
    → Root cause: connection pool size too small

Step 5: Verify scope
  - Prometheus: count(payment_service_db_wait_seconds
    > 5) by (pod) → shows all pods affected
  - Loki: {app="payment-service"} |= "pool exhausted"
    | count_over_time[1h] → how many requests affected?

Total investigation time: 12 minutes
Enabled by: trace → log (trace_id in both),
            log → metric (same time range),
            metric → scope assessment
```

---

### 💻 Code Example

**Example 1 - BAD: high-cardinality stream label in Loki**

```yaml
# BAD: request_id as Loki stream label
# Creates millions of unique streams
# Index size explodes, Loki OOM-kills

# Application sends log with:
{
  "timestamp": "2024-01-01T14:32:00Z",
  "message": "Payment processed",
  "stream_labels": {
      "app": "payment",
      "request_id": "uuid-a1b2c3d4", # WRONG: unique per request
    },
}
# Impact: 1000 RPS × 86400s/day = 86M unique streams/day
# Loki index cannot handle this
# Query performance degrades to minutes, then OOM
```

**Example 2 - GOOD: high-cardinality values in log content**

```yaml
# GOOD: request_id in log content, not stream labels
# Stream labels: only low-cardinality labels
# Log content: all high-cardinality values

{
  "timestamp": "2024-01-01T14:32:00Z",
  "message": "Payment processed",
  "stream_labels": {
      "app": "payment", # ~10 apps - LOW cardinality
      "env": "production", # 3 values - VERY LOW
      "namespace": "checkout", # ~50 namespaces - LOW
    },
  "log_content": {
      "request_id": "uuid-a1b2c3d4", # High cardinality
      "user_id": "user-789", # High cardinality
      "trace_id": "xyz789abc", # Unique per request
    },
}
# Stream count: 10 apps × 3 envs × 50 namespaces = 1500
# Fully manageable by Loki's index
# To find specific request: query content filter |= "uuid-a1b2c3d4"
# Loki decompresses only matching app/env/namespace chunks
```

**Example 3 - TSDB cardinality analysis**

```bash
# Find highest-cardinality metrics in Prometheus
# (exposes the metric + all its unique label combinations)
curl -s 'http://prometheus:9090/api/v1/label/__name__/values' \
  | jq '.data | length'  # Total distinct metric names

# Series count per metric
curl -s 'http://prometheus:9090/api/v1/query?query=
  topk(20,count+by+(__name__)+({__name__=~".+"}))' \
  | jq '.data.result[] | {metric: .metric.__name__,
         cardinality: .value[1]}'

# EXAMPLE OUTPUT shows which metrics are exploding:
# {"metric": "http_request_duration_seconds",
#  "cardinality": "2847392"}    ← 2.8M series = problem
# {"metric": "go_goroutines",
#  "cardinality": "47"}         ← fine

# For metric with high cardinality:
# Check which label is causing it
curl -s 'http://prometheus:9090/api/v1/query?query=
  count+by(uri)+(http_request_duration_seconds)' \
  | jq '.data.result | length'
# If "uri" has 50,000 unique values → uri should not be
# a metric label → move to structured log instead
```

**Example 4 - FAILURE: Prometheus OOM from cardinality**

```
Symptom:
  Prometheus pod restarts every 6 hours (OOM-killed)
  Memory usage grows linearly: 2GB → 16GB over 6 hours
  Kubernetes OOM killer terminates at 16GB (container limit)

Root Cause:
  A developer added `user_id` label to a business metric
  with 1M active users → 1M unique label combinations
  Each Prometheus series requires ~3KB RAM for head chunk
  1M series × 3KB = 3GB RAM
  Combined with existing 5M series: 5M × 3KB = 15GB
  Exceeds 16GB limit after 6 hours of accumulation

Diagnostic:
  # Check active series count
  prometheus_tsdb_head_series
  # If > 10M → investigate cardinality

  # Check series per metric
  topk(20, count by (__name__)({__name__=~".+"}))
  # Find the metric that grew 1M series

  # Check churn rate (new series per 5min)
  rate(prometheus_tsdb_head_series_created_total[5m])
  # High churn = labels with short-lived unique values

Fix:
  1. Drop the high-cardinality label via recording rule
     or relabeling in the scrape config
  2. Increase GOMAXPROCS and memory limit (short-term)
  3. Add cardinality alerts:
     prometheus_tsdb_head_series > 8000000 → alert
```

---

### ⚖️ Comparison Table

| Storage System      | Data Type    | Primary Index          | Compression        | Query Performance                      |
| ------------------- | ------------ | ---------------------- | ------------------ | -------------------------------------- |
| **Prometheus TSDB** | Metrics      | Label-set → chunk      | XOR delta-of-delta | O(1) by labels, O(range) by time       |
| **Loki**            | Logs         | Stream labels only     | zstd chunks        | Fast with labels, linear for content   |
| **Tempo**           | Traces       | Bloom filter per block | Parquet (v2)       | O(1) by trace ID, O(n) for content     |
| **Elasticsearch**   | Logs         | Full inverted index    | LZ4/zstd           | Fast for any field, 10x more RAM       |
| **ClickHouse**      | Logs/Metrics | Sparse + bloom         | LZ4                | Very fast for analytics, not streaming |

**How to choose:**
Use Prometheus + Loki + Tempo (LGTM stack) for self-hosted
platform with cost sensitivity. Use Elasticsearch when
full-text search across all log fields is the primary
use case (e.g., security logs where the field being searched
is not known at indexing time). Use ClickHouse for
high-volume analytics on logs (e.g., billing, compliance
reporting) where query patterns favor batch analytics
over real-time streaming.

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                                                                                                                                                                |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| More series = more RAM linearly              | Prometheus RAM scales with active series in head block (last 2h). 1M series ≈ 3GB RAM. But series that stop receiving samples are evicted from head, so churn (series created and deleted rapidly) is worse than having many stable series                             |
| Loki is just "cheap Elasticsearch"           | Loki is architecturally different: minimal indexing trades full-text search capability for drastically lower operational cost. Good choice when label-filtered queries suffice; wrong choice when you need arbitrary field search                                      |
| Trace storage requires much disk             | Traces are typically high-cardinality but low-volume (1 trace per request, not 50 metric samples per request per metric). At 1000 RPS with 50 spans/trace and 500 bytes/span, trace volume is 25MB/s = 2.1TB/day uncompressed, ~300GB/day compressed - similar to logs |
| Delta encoding only works for stable metrics | XOR encoding works for any float64 data; it just achieves better compression when consecutive values are close. Even volatile metrics (CPU usage) compress well because consecutive float64 values share most of their bits                                            |

---

### 🚨 Failure Modes & Diagnosis

**Prometheus Query Timeout on Wide Time Ranges**

**Symptom:**
Queries for 30-day aggregations time out. The Grafana
dashboard shows "Query timed out" for any panel covering
more than 7 days. Recent data (< 2h) queries are instant.

**Root Cause:**
Prometheus compacts data into blocks. Reading 30 days of
data requires reading multiple block files from disk,
decompressing, and merging. For 10M series over 30 days,
this is O(billions of chunks) to scan.

**Fix:**
Add recording rules that pre-aggregate the 30-day data
daily. Instead of computing `sum(http_requests_total)
over 30 days` at query time, compute it every hour
as a recording rule:

```promql
record: job:http_requests:rate1h
expr: rate(http_requests_total[1h])
```

Then query the pre-aggregated metric for the 30-day view.
Query time: O(30 data points) vs O(30-day raw series).

---

**Loki Log Query Returns Partial Results**

**Symptom:**
Querying "all ERROR logs in the last 7 days" returns
results but they seem incomplete - spot-checking shows
some known error periods are missing from results.

**Root Cause:**
The query hit Loki's query result limit (`max_entries_per_query`,
default 5000 lines). Results are returned up to the limit
and then cut off. The cut-off is not visually obvious -
Loki returns the 5000 most recent matches, not a random
sample, but the user expects all matches.

**Diagnostic:**
Check if results hit the limit:

```
# In Loki query log:
msg="query stats" entries=5000  # exactly at limit = truncated

# Solution: add time range restriction to fit within limit
# Or: use count_over_time for aggregates instead of
# log line retrieval
```

**Fix:**
For large result sets, use aggregation instead of raw
line queries:

```logql
# BAD: returns raw lines (hits 5000 limit)
{app="api"} |= "ERROR"

# GOOD: returns count per minute (no row limit issue)
sum by (level) (
  count_over_time(
    {app="api"} |= "ERROR" [1m]
  )
)
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `What Is Observability` - the three pillars these systems store
- `Prometheus` - metrics TSDB in detail
- `Distributed Tracing` - trace data model before the storage internals
- `Grafana` - the query interface over these storage systems
- `Log Aggregation at Scale` - Loki pipeline before storage internals
- `Observability at Scale` - the scaling problems these internals solve
- `Observability Platform Architecture Design` - the system that uses these components
- `Time-Series Database Design` - metrics storage deep dive
- `Distributed Tracing System Architecture` - trace storage deep dive

**Builds On This (learn these next):**

- `Reliability Mental Model` - how understanding internals
  informs reliability decisions

**Alternatives / Comparisons:**

- `Platform Observability Engineering` - operational practice
  that runs these systems at scale
- `Capacity Planning with Metrics` - uses these query
  internals for predict_linear() based forecasting
- `SRE Book Core Principles` - organizational context for
  why these systems must be reliable

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ PROMETHEUS    │ XOR delta-of-delta compression → 1.37 │
│ INTERNALS     │ bytes/sample. Head block = 2h in RAM.  │
│               │ WAL → compaction → immutable blocks.   │
│               │ Cardinality = active series = RAM cost  │
├───────────────┼─────────────────────────────────────────┤
│ LOKI          │ Label-indexed streams only (NOT content)│
│ INTERNALS     │ zstd compressed chunks in S3.           │
│               │ Query = label filter → chunk fetch →   │
│               │ decompress → grep. Fast with labels,   │
│               │ linear for content search               │
├───────────────┼─────────────────────────────────────────┤
│ TEMPO         │ Bloom filter per block for trace ID     │
│ INTERNALS     │ lookup. Object storage (S3). Fast for  │
│               │ trace-ID lookup, slow for "all slow     │
│               │ traces" (full block scan via TraceQL)  │
├───────────────┼─────────────────────────────────────────┤
│ CORRELATION   │ trace_id field in logs links trace to  │
│ MODEL         │ log lines. Time range aligns metrics to │
│               │ trace window. Exemplars in Prometheus  │
│               │ directly link metric anomaly to trace  │
├───────────────┼─────────────────────────────────────────┤
│ CARDINALITY   │ The single biggest operational risk.   │
│ DANGER        │ High-cardinality labels → Prometheus   │
│               │ OOM. High-cardinality stream labels →  │
│               │ Loki index explosion                   │
├───────────────┼─────────────────────────────────────────┤
│ ONE-LINER     │ "Name the data structure behind each   │
│               │ component to understand its limits."   │
├───────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE  │ Time-Series Database Design →          │
│               │ Distributed Tracing System Architecture │
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Prometheus RAM cost = active series × ~3KB. Cardinality
   is the primary scaling limit. High-cardinality labels
   cause OOM; drop them with relabeling or recording rules.
2. Loki only indexes stream labels, not log content. Put
   high-cardinality values (request_id, user_id) in log
   content, not in stream labels. Content queries require
   full chunk decompression.
3. Trace lookup by ID is fast (bloom filter eliminates
   90% of S3 reads). "All slow traces" queries are slow
   (require scanning all blocks). Design dashboards to use
   traces for specific investigation, not for aggregations.

**Interview one-liner:**
"Prometheus uses XOR delta-of-delta compression (Gorilla
paper) achieving 1.37 bytes/sample vs 16 bytes raw. The
head block (2h) lives in RAM. Cardinality = unique label
sets = RAM cost. Loki indexes only stream labels, not log
content - putting user_id as a stream label causes index
explosion. Tempo uses bloom filters per block for trace-ID
lookup, making point queries fast and range queries (all
slow traces) O(blocks). Correlation: trace_id in logs
links to Tempo; Prometheus exemplars link metric anomaly
to trace."

> Entry stub. Generate full content using Master Prompt v3.0.
