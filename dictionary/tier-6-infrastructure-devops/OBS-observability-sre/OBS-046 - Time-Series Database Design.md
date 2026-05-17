---
id: OBS-046
title: Time-Series Database Design
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★★
depends_on: OBS-001, OBS-006, OBS-004, OBS-038, OBS-039
used_by: OBS-045, OBS-047
related: OBS-044, OBS-030, OBS-053
tags:
  - observability
  - reliability
  - devops
  - sre
  - advanced
  - internals
  - database
  - production
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 46
permalink: /obs/time-series-database-design/
---

# OBS-046 - Time-Series Database Design

⚡ TL;DR - A time-series database (TSDB) is purpose-built
for append-only (timestamp, value) data with label-based
queries: it achieves 10-15x compression over row stores
through delta encoding, stores data in immutable time-
partitioned blocks, and answers range queries by scanning
only the blocks covering the requested time range.

| #046            | Category: Observability & SRE                                                                                                 | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | What Is Observability, Prometheus, Metrics and Time-Series Monitoring, Capacity Planning with Metrics, Observability at Scale |                 |
| **Used by:**    | Observability System Design Internals, Distributed Tracing System Architecture                                                |                 |
| **Related:**    | Platform Observability Engineering, Alerting Fundamentals, Service Level Objectives Deep Dive                                 |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team stores application metrics in a relational database
(PostgreSQL). The schema: `metrics (timestamp TIMESTAMP,
metric_name VARCHAR, labels JSONB, value FLOAT8)`. At
startup, 50 metrics × 1 scrape/15s = 200 inserts/minute.
After 6 months of growth to 500 services × 100 metrics:
3 million inserts/minute. The PostgreSQL table has 2 trillion
rows. Queries for "HTTP error rate in the last 1 hour
grouped by service" take 45 seconds (full table scan despite
indexes). The storage volume is 80TB despite the data
compressing well. Vacuum and autovacuum thrash the server.
The monitoring system is causing more incidents than it
is detecting.

**THE BREAKING POINT:**
General-purpose relational databases cannot efficiently
handle metrics data because they are optimized for random
read/write access to arbitrary rows, while metrics data
has unique properties: always appended (never updated),
always queried by time range, individual values are highly
compressible when compared to adjacent samples, and the
majority of reads access recent data while old data is
rarely read.

**THE INVENTION MOMENT:**
Purpose-built TSDBs exploit these properties: (1) columnar
storage per metric (all values for one metric in one
column, enabling delta encoding), (2) time-partitioned
blocks (only read the blocks covering the query range),
(3) aggressive compression (XOR encoding for float64
values reduces storage 10-15x), (4) inverted label index
(fast label-filtered queries without full scans), (5) tiered
retention (hot storage for recent data, compressed cold
storage for historical data).

---

### 📘 Textbook Definition

A **time-series database (TSDB)** is a database management
system optimized for the time-ordered storage and retrieval
of sequences of (timestamp, value) pairs, called time
series, each identified by a unique label set. Key
distinguishing characteristics from general-purpose
databases: (1) append-only write path (no updates to
historical data), (2) columnar per-series storage enabling
aggressive compression via delta/XOR encoding, (3) time-
partitioned immutable blocks enabling range query pruning,
(4) label-based indexing for multi-dimensional querying,
and (5) tiered storage for cost-efficient long-term
retention. Examples: Prometheus TSDB, InfluxDB (IOx),
TimescaleDB, VictoriaMetrics, QuestDB.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A TSDB is a database where write is always append-at-now,
read is always range-by-time, and both operations are
10-100x faster than in a relational DB because the schema
is fixed and the storage is optimized for exactly this pattern.

**One analogy:**

> A TSDB is like a scientific data logger, not a general
> ledger. A general ledger (relational DB) supports any
> combination of operations: insert, update, delete, join
> across tables, arbitrary queries. A scientific data
> logger records sensor readings at regular intervals in
> a sequential roll of paper tape. You can never go back
> and change a reading. You can quickly find any time
> range (it's already in order). The tape compresses
> extremely well because adjacent readings are similar.
> When the tape is old, you keep a compressed summary
> (downsample), not every sample. The scientific data
> logger does 3 things perfectly; the general ledger
> does everything adequately. When you have billions of
> sensor readings per day, perfectly beats adequately.

**One insight:**
The TSDB design is fundamentally shaped by one observation:
metrics data has two phases in its lifecycle - it is
intensively queried while recent (last few hours to days)
and rarely queried when old (weeks to months). This creates
the hot/warm/cold storage model that all TSDBs implement:
recent data is in fast memory/local SSD, historical data
is compressed in object storage (S3). The compression
makes this economically viable - Prometheus achieves
1.37 bytes per sample vs 16 bytes raw.

---

### 🔩 First Principles Explanation

**THE FIVE TSDB DESIGN PILLARS:**

**Pillar 1 - Append-only write path:**
Metrics are immutable once written. This enables:

- No lock contention (readers don't block writers)
- Efficient WAL (write-ahead log = sequential disk write)
- Block compaction (merge multiple small files offline)
- Deletion by tombstone (mark a range, compact later)

**Pillar 2 - Columnar storage per series:**
Row storage: each row = (timestamp, value, labels).
Queries must read all row fields even if only value needed.
Column storage: all timestamps in one column, all values
in another. Delta encoding works because consecutive
timestamps differ only by the scrape interval, consecutive
values of stable metrics differ only by small amounts.

```
Row storage: [(T1,V1), (T2,V2), (T3,V3), ...]
  Each pair is stored together - bad for compression
  because timestamp and value types differ

Column storage: [T1, T2, T3, ...] | [V1, V2, V3, ...]
  Timestamps: highly compressible via delta-of-delta
  Values: highly compressible via XOR encoding
  Each column compresses independently
```

**Pillar 3 - Time-partitioned blocks:**

```
Data organized as:
  block_00h-02h/ (compact, immutable)
  block_02h-04h/ (compact, immutable)
  ...
  head_block/   (active, in RAM, accepting writes)

Query for [10h-14h]:
  Open only block_10h-12h and block_12h-14h
  Skip all other blocks (no scan needed)
  This is O(range_size / block_size), not O(total_data)
```

**Pillar 4 - Inverted label index:**

```
Metric: http_requests_total{method="GET", status="200"}
        http_requests_total{method="POST", status="500"}

Inverted index:
  "method=GET"   → [series_id_1]
  "method=POST"  → [series_id_2]
  "status=200"   → [series_id_1]
  "status=500"   → [series_id_2]

Query: method="POST" AND status="500"
  = intersection([series_id_2]) ∩ ([series_id_2])
  = [series_id_2]

Time complexity: O(matching series), not O(all series)
```

**Pillar 5 - Tiered retention:**

```
Hot tier (in RAM):
  Last 2h of data in head block
  Fastest possible read (L1/L2 cache)
  ~3KB per active series

Warm tier (local SSD):
  Last N days of compact immutable blocks
  Good read performance (NVMe: ~1GB/s)
  XOR-compressed: ~1.37 bytes/sample

Cold tier (object storage: S3/GCS):
  Historical data (weeks to years)
  Slow read (S3: ~100MB/s per object)
  Often further downsampled (1h resolution)
  Cost: ~$0.02/GB/month (vs $0.10/GB NVMe)
```

**THE TRADE-OFFS:**
**Gain:** 10-100x better write throughput vs relational DB;
10-15x storage compression; sub-second range queries on
years of data; economical long-term retention via S3.
**Cost:** Limited query flexibility (no JOINs, no ad-hoc
schema); cardinality constraints (each unique label set
= one series = memory cost); no updates to historical data
(immutability is a feature but prevents corrections);
complex cluster scaling (multi-node Thanos/Cortex for
global aggregation).

---

### 🧪 Thought Experiment

**DESIGN: A TSDB from scratch for 1M series at 10s intervals**

Requirements:

- 1M time series, 1 sample every 10 seconds
- Query: "all series matching {env="prod"} in last 1 hour"
- Query: "max value of metric X over last 30 days"
- Cost: < $500/month for 1 year of retention

**DATA VOLUME ANALYSIS:**

```
Write rate: 1M series × (1 sample/10s) = 100K samples/s
Raw size: 16 bytes/sample × 100K/s = 1.6 MB/s raw
Compressed (1.37 bytes/sample): 137KB/s
Daily volume: 137KB/s × 86400 = 11.8 GB/day compressed
Annual volume: 11.8 × 365 = 4.3 TB/year compressed

Storage cost (S3 standard at $0.023/GB/month):
  4.3TB × $0.023 × 12 = $1,186/year

  Reduce by downsampling: after 7 days, keep 1h resolution
  instead of 10s. 1h/10s = 360x fewer samples for old data.
  Total: 7 days × 11.8GB/day (full) +
         358 days × 11.8GB/day / 360 (downsampled)
  = 82.6GB + 11.7GB = 94.3GB
  Cost: 94.3 × $0.023 × 12 = $26/year  (MUCH cheaper)
```

**QUERY PERFORMANCE ANALYSIS:**

```
Query: {env="prod"} in last 1 hour
  1M series × 10% in prod = 100K series to scan
  1 hour at 10s intervals = 360 samples per series
  Compressed: 360 × 1.37 bytes = 493 bytes per series
  Total data to read: 100K × 493 bytes = 47MB
  S3 reads at 100MB/s: 0.47 seconds ✓

But: this assumes data is block-aligned.
  In practice: 1h query spans 1 block (1h blocks)
  or 2 blocks if it straddles a boundary.
  Read only 2 blocks, not all history. Fast.
```

---

### 🧠 Mental Model / Analogy

> A TSDB is like a daily newspaper archive - optimized
> for the way people actually use it, not for arbitrary
> access. Newspapers are organized by date (time partitioning).
> Old papers are stored in a compressed microfilm archive
> (cold tier). Recent papers are at the front desk (hot tier).
> A specific article can be found by date + section (label
> filter). The archive never modifies old newspapers
> (immutability). A standard librarian (relational DB)
> would need a completely different indexing scheme to
> answer "give me all articles about interest rates in
> the last 3 years" as efficiently.

Where this analogy breaks down: newspapers have unique
articles (no deduplication needed); time series data
may need deduplication in high-availability setups
(Prometheus HA pairs write duplicates that Thanos/Cortex
must deduplicate at query time).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A time-series database stores sequences of measurements
(like temperature readings, request counts) organized by
time. It is much faster and cheaper than a regular database
for this kind of data because it is purpose-built for
"write the current reading, read readings from this time
range" - nothing else.

**Level 2 - How to use it (junior developer):**
Use a TSDB for any metric that changes over time and you
want to query by time range. Prometheus is the standard
TSDB for application metrics. InfluxDB or TimescaleDB
are alternatives. Key rules: high-cardinality label values
(user_id, request_id) kill TSDB performance - keep
cardinality low. Query with PromQL's time range functions
(rate(), avg_over_time(), etc.).

**Level 3 - How it works (mid-level engineer):**
Prometheus TSDB stores data in blocks (2h by default for
the head/in-memory block, then compacted to larger blocks
on disk). Each block has: a series index (label set →
series ID), a chunk store (XOR-compressed value arrays
per series), and a tombstone file (deleted ranges). Queries
look up matching series IDs in the index, then read only
the chunk data for those series in the requested time range.

**Level 4 - Why it was designed this way (senior/staff):**
The block design enables background compaction: small
frequent blocks are merged into larger blocks offline,
improving query performance (fewer files to open) and
compression ratio (duplicate series across overlapping
scrapes can be deduplicated). The immutability of sealed
blocks means compaction is safe - you can write the new
block and only delete the originals after validating.
This is a copy-on-write compaction pattern that provides
crash safety without complex locking.

**Level 5 - Mastery (distinguished engineer):**
Multi-tenant and global TSDBs (Thanos, Cortex, Mimir)
add a shard layer on top of Prometheus TSDB. Each Prometheus
instance writes to local TSDB. Thanos sidecars upload
blocks to object storage. Thanos Querier fans out queries
across all Prometheus instances, deduplicates the results
(HA pairs write duplicate data), and applies downsampling
for long-term queries. The deduplication uses a priority-
based algorithm: given two identical time series from two
replicas, select the replica with most data, and fill gaps
from the other. This produces correct query results despite
the underlying storage being duplicated.

---

### ⚙️ How It Works (Mechanism)

**WRITE PATH:**

```
New sample arrives: (labels, timestamp, value)
   │
   ↓
1. Series lookup in head index:
   - Hash(labels) → check if series exists
   - If new: assign series_id, add to inverted index
   - If exists: get series_id
   │
   ↓
2. WAL append (crash recovery):
   Write raw (series_id, timestamp, value) to WAL
   WAL is sequential write → fast (~500MB/s on SSD)
   │
   ↓
3. Head block append:
   Find the current chunk for this series_id
   If chunk is full (120 samples) → seal and start new
   Append sample to XOR encoder → add to chunk buffer
   │
   ↓
4. Head block checkpoint (every 2h):
   Serialize compressed chunks to disk
   WAL is truncated (already persisted to block)

5. Block compaction (triggered when head overflows):
   Compress head block to immutable disk block
   Apply tombstones (deleted ranges)
   Background: merge small blocks into larger blocks
```

**QUERY PATH:**

```
Query: rate(http_requests_total{job="api"}[5m])
       for time range [T-1h, T]

   │
   ↓
1. Block selection:
   Find all blocks overlapping [T-1h, T]
   (head block + last few disk blocks typically)
   │
   ↓
2. Series resolution (per block):
   Index lookup: job="api" → [series_id_1, series_id_2, ...]
   Cross-block: union of matching series IDs
   │
   ↓
3. Chunk reading:
   For each series_id in [T-1h, T]:
     - Find chunk file and offset from block index
     - Read chunk bytes from disk
     - XOR-decompress to (timestamp[], value[]) arrays
   │
   ↓
4. PromQL evaluation:
   rate() function: compute (v_last - v_first) / duration
   Result: one float64 per series per evaluation step
   │
   ↓
5. Return to query engine (Grafana/API)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**LONG-TERM RETENTION WITH THANOS:**

```
                  Prometheus (local TSDB)
                   │ (head block - RAM)
                   │ (disk blocks - local SSD)
                   │
                   ↓
         Thanos Sidecar (co-located)
           │ - Uploads sealed blocks to S3
           │ - Exposes Prometheus store API
           │
      ┌────┘
      ↓
   S3 Bucket (all blocks from all Prometheus instances)
   ├── cluster-A/prometheus-0/01HB234.../
   ├── cluster-A/prometheus-1/01HB234.../  (HA duplicate)
   └── cluster-B/prometheus-0/01HB456.../
      │
      ↓
Thanos Store Gateway
  - Loads block metadata from S3 into RAM (not data)
  - Serves queries: fetches only needed chunks from S3
  - Applies downsampling (for queries > 30 days)

Thanos Querier (global view)
  - Fans out to: local Prometheus instances (recent data)
                  Thanos Store Gateways (old data)
  - Deduplicates (HA replicas produce duplicate series)
  - Returns merged, deduplicated result set

Query latency:
  Last 1h: <100ms (from local Prometheus in RAM)
  Last 7d: 200-500ms (from local disk blocks)
  Last 1y: 1-5s (from S3, many blocks to read)
```

---

### 💻 Code Example

**Example 1 - BAD: high-cardinality label usage**

```go
// BAD: using user_id as a metric label
// Creates O(unique_users) time series
// Prometheus OOM at scale

httpRequestsTotal := prometheus.NewCounterVec(
    prometheus.CounterOpts{
        Name: "http_requests_total",
        Help: "Total HTTP requests",
    },
    // user_id has millions of unique values!
    []string{"method", "path", "status", "user_id"},
)

// One unique (method, path, status, user_id) tuple = 1 series
// 10K users × 10 paths × 3 methods × 3 statuses = 900K series
// At 3KB/series RAM: 2.7GB just for this one counter
// Prometheus head block fills, OOM, restarts every 30 min
```

**Example 2 - GOOD: low-cardinality labels, use logs for high-cardinality**

```go
// GOOD: only low-cardinality labels in metrics
// High-cardinality data goes to structured logs

httpRequestsTotal := prometheus.NewCounterVec(
    prometheus.CounterOpts{
        Name: "http_requests_total",
        Help: "Total HTTP requests",
    },
    // Max distinct values: method(3) × path(20) × status(5)
    // = 300 series total - SAFE
    []string{"method", "path", "status"},
)

// Record the low-cardinality metric
httpRequestsTotal.With(prometheus.Labels{
    "method": r.Method,
    "path":   normalizePath(r.URL.Path), // /users/123 → /users/:id
    "status": strconv.Itoa(statusCode),
}).Inc()

// Log the high-cardinality data separately
log.Info("HTTP request",
    zap.String("user_id", userID),        // high-cardinality
    zap.String("request_id", requestID),  // unique per request
    zap.String("method", r.Method),
    zap.Int("status", statusCode),
    zap.Duration("duration", duration),
)
// user_id is searchable in logs (Loki content filter)
// but doesn't blow up Prometheus cardinality
```

**Example 3 - Recording rules for expensive queries**

```yaml
# BAD: computing 30-day error rate at query time
# Prometheus scans all 30 days of chunks on every query
# Takes 30+ seconds for high-cardinality metrics

# Query: expensive and slow
rate(http_requests_total{status=~"5.."}[30d])

# GOOD: recording rule computes this every 5 minutes
# Query uses pre-computed 1-minute rate (fast)

groups:
  - name: http.recording_rules
    interval: 1m
    rules:
      # Pre-compute per-job error rate (aggregated)
      - record: job:http_error_rate:rate5m
        expr: >
          sum by (job) (
            rate(
              http_requests_total{status=~"5.."}[5m]
            )
          )
          /
          sum by (job) (
            rate(http_requests_total[5m])
          )

# Dashboard query (fast): just reads the pre-aggregated metric
# Instead of scanning 30 days, reads 30 days of 1-min samples
# 30 days × 1440 min/day = 43,200 data points per series
# vs 30 days × 4 samples/min × N raw series = billions
```

**Example 4 - FAILURE: write stall from too many active series**

```
Symptom:
  Prometheus /metrics endpoint returns HTTP 503
  Prometheus logs: "write queue full" or WAL stall
  Ingestion rate drops to near zero
  Dashboard shows gaps in all metrics

Root Cause:
  A deployment pushed a service with 5M unique series
  (user_id label on all metrics).

  Prometheus head block capacity exceeded:
    Default max series: 2M (configurable via
    --storage.tsdb.max-block-duration)

  When head fills: Prometheus stops accepting new series
  WAL falls behind, write queue backs up
  Scrapes timeout → gaps in data

Diagnosis:
  # Head series count
  prometheus_tsdb_head_series
  # Should be < 2M for healthy operation

  # Series created per minute (churn)
  rate(prometheus_tsdb_head_series_created_total[5m])
  # Spike = new high-cardinality series being created

Fix (immediate):
  kubectl rollback the deployment (removes new series)
  Series evict from head after 2h of no new samples

Fix (permanent):
  Add label drop relabeling in Prometheus scrape config:
  metric_relabel_configs:
    - source_labels: [__name__, user_id]
      regex: ".*"
      target_label: user_id
      replacement: ""  # Drop user_id label entirely
```

---

### ⚖️ Comparison Table

| TSDB                | Write Model              | Query Language       | Scale Model                            | Best For                           |
| ------------------- | ------------------------ | -------------------- | -------------------------------------- | ---------------------------------- |
| **Prometheus TSDB** | Pull-based scraping      | PromQL               | Single-node + Thanos/Cortex for global | Kubernetes metrics, standard SRE   |
| **InfluxDB (IOx)**  | Push (line protocol)     | InfluxQL / Flux      | Serverless                             | IoT, developer-friendly            |
| **TimescaleDB**     | Push (SQL INSERT)        | SQL + time functions | PostgreSQL scaling                     | Teams with SQL expertise           |
| **VictoriaMetrics** | Prometheus-compatible    | MetricsQL            | Cluster mode built-in                  | High-volume Prometheus replacement |
| **QuestDB**         | Push (SQL/line protocol) | SQL                  | Single-node                            | High-speed ingestion, analytics    |

**How to choose:**
Use Prometheus TSDB for Kubernetes-native environments.
Use VictoriaMetrics as a drop-in Prometheus replacement
when scaling beyond single-node. Use TimescaleDB when the
team prefers SQL and the existing infrastructure is PostgreSQL.
Use InfluxDB for IoT or heterogeneous sensor data.

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                                                                       |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| TSDBs are just regular databases with a time column | TSDBs use specialized data structures (XOR encoding, immutable blocks, inverted label index) that general-purpose databases cannot replicate at comparable performance and storage efficiency |
| Prometheus is a TSDB cluster                        | Prometheus is single-node by design. Clustering requires Thanos, Cortex, or Mimir on top. This is a deliberate design choice for operational simplicity                                       |
| More retention requires proportionally more storage | Downsampling older data (5-min resolution after 7 days, 1-hour resolution after 30 days) reduces storage by 360x for the oldest data, making years of retention practical                     |
| TSDB is only useful for metrics                     | Log systems (Loki) and trace systems (Tempo) use TSDB-like design principles (time-partitioned blocks, append-only, columnar compression) - the pattern is general                            |

---

### 🚨 Failure Modes & Diagnosis

**Block Corruption After Unclean Shutdown**

**Symptom:**
Prometheus restarts after node failure. Queries return
"unexpected end of file" for time ranges before the
failure. Prometheus logs: "error opening block: block
is not complete."

**Root Cause:**
An in-progress block compaction was interrupted by the
OOM-kill. The partial block was written to disk but is
incomplete (missing the index or checksum file). The WAL
was not fully checkpointed before the kill.

**Diagnosis:**

```bash
# List Prometheus data directory for corrupt blocks
ls -la /prometheus/data/
# Look for blocks without meta.json or chunks/ directory

# Prometheus startup log will report:
# level=warn msg="Encountered corrupted block"
#   block=/prometheus/data/01HB...
```

**Fix:**

```bash
# Delete the incomplete block
rm -rf /prometheus/data/01HB_incomplete/
# Prometheus will replay WAL on next start
# Recent data (since last checkpoint) is recovered from WAL
# Older corrupt block data is lost (the WAL doesn't go that far)

# Prevention:
# Set resource limits to prevent OOM mid-compaction
# Use storage.tsdb.wal-segment-size for WAL durability tuning
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `What Is Observability` - the context for why TSDBs exist
- `Prometheus` - the primary TSDB in the SRE ecosystem
- `Metrics and Time-Series Monitoring` - the data the TSDB stores
- `Capacity Planning with Metrics` - primary use of TSDB queries
- `Observability at Scale` - the scaling problems TSDBs solve

**Builds On This (learn these next):**

- `Observability System Design Internals` - how TSDB internals
  combine with log and trace storage
- `Distributed Tracing System Architecture` - comparable
  design principles for trace data

**Alternatives / Comparisons:**

- `Platform Observability Engineering` - running TSDBs
  at organizational scale
- `Alerting Fundamentals` - the primary real-time consumer
  of TSDB data
- `Service Level Objectives Deep Dive` - the business
  context for TSDB long-term retention

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Append-only database for (label_set,   │
│               │ timestamp, value) tuples with 10-15x  │
│               │ compression and sub-second range queries│
├───────────────┼────────────────────────────────────────┤
│ KEY STRUCTURES│ Inverted label index (fast series     │
│               │ lookup) + XOR compressed chunks        │
│               │ + time-partitioned immutable blocks    │
├───────────────┼────────────────────────────────────────┤
│ COMPRESSION   │ XOR delta-of-delta: ~1.37 bytes/sample│
│               │ vs 16 bytes raw (11.7x ratio)          │
├───────────────┼────────────────────────────────────────┤
│ CARDINALITY   │ Each unique label set = 1 series =     │
│               │ ~3KB RAM. High-cardinality labels      │
│               │ (user_id) cause OOM. Keep cardinality  │
│               │ low; put high-cardinality in logs       │
├───────────────┼────────────────────────────────────────┤
│ BLOCK DESIGN  │ Head block: last 2h in RAM (fast)      │
│               │ Disk blocks: immutable, compact, fast  │
│               │ S3: historical, compressed, tiered     │
├───────────────┼────────────────────────────────────────┤
│ SCALING       │ Prometheus = single-node. Use Thanos/  │
│               │ Cortex/Mimir for global multi-cluster  │
│               │ or VictoriaMetrics for high throughput  │
├───────────────┼────────────────────────────────────────┤
│ ONE-LINER     │ "TSDBs win because they exploit the    │
│               │ monotone-time, append-only, label-     │
│               │ filtered access pattern of metrics."   │
├───────────────┼────────────────────────────────────────┤
│ NEXT EXPLORE  │ Observability System Design Internals →│
│               │ Distributed Tracing System Architecture │
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. TSDBs use XOR delta-of-delta compression achieving
   ~1.37 bytes/sample (vs 16 bytes raw). Columnar storage
   per series is what makes this compression possible.
2. Cardinality = active series = RAM cost. Every unique
   label set is a separate series. user_id as a label
   means 1M series for 1M users. Keep labels low-cardinality.
3. Time-partitioned immutable blocks = fast range queries.
   A 1-hour query reads only the blocks covering that hour
   (2-4 blocks typically), not all data. Block compaction
   merges small blocks offline for better read performance.

**Interview one-liner:**
"TSDBs exploit three properties of metrics data: append-only
writes (immutable blocks, fast WAL), temporal locality of
queries (time-partitioned blocks, only read relevant range),
and statistical regularity of consecutive samples (XOR
delta-of-delta compression achieving 1.37 bytes/sample vs
16 bytes raw). Cardinality is the primary operational risk:
each unique label set is one in-memory series at ~3KB RAM.
High-cardinality labels (user_id, request_id) cause
Prometheus OOM. Put high-cardinality data in structured
logs, not in metric labels."

> Entry stub. Generate full content using Master Prompt v3.0.
