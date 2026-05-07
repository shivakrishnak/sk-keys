---
layout: default
title: "Time-Series DB"
parent: "NoSQL & Distributed Databases"
nav_order: 16
permalink: /nosql/time-series-db/
number: "NDB-016"
category: NoSQL & Distributed Databases
difficulty: ★★★
depends_on: Column Family, LSM Tree, Observability & SRE
used_by: Observability & SRE, IoT, System Design
related: Column Family, InfluxDB, Prometheus
tags:
  - nosql
  - time-series
  - observability
  - deep-dive
---

# NDB-016 — Time-Series DB

⚡ TL;DR — A time-series database is purpose-built for append-only, timestamped data streams — using columnar compression, time-partitioned storage, and downsampling to store and query billions of metrics, sensor readings, or events far more efficiently than a general-purpose database.

| #455            | Category: NoSQL & Distributed Databases      | Difficulty: ★★★ |
| :-------------- | :------------------------------------------- | :-------------- |
| **Depends on:** | Column Family, LSM Tree, Observability & SRE |                 |
| **Used by:**    | Observability & SRE, IoT, System Design      |                 |
| **Related:**    | Column Family, InfluxDB, Prometheus          |                 |

---

### 🔥 The Problem This Solves

**METRICS IN POSTGRESQL:**
`INSERT INTO metrics (host, metric, value, ts) VALUES (...)`. 10,000 metrics/second from 5,000 servers: 864 million rows/day. PostgreSQL: random write I/O to B-tree index pages. Table bloat. Autovacuum churning. Queries like "average CPU over last 1 hour across all hosts" require scanning hundreds of millions of rows. Storage: no compression (full row overhead per metric). After 90 days: 78 billion rows. Database becomes unusable.

**TIME-SERIES DB:**
Columnar storage: all timestamps in one compressed column, all values in another. Delta-delta encoding: timestamps are nearly sequential (1592838450, 1592838451, 1592838452...) → store differences (1,1,1...) → near-zero space. Time-based partitioning: auto-drop partitions older than retention period. Downsampling: automatically compress 1-second data to 1-minute averages after 7 days, to 1-hour averages after 30 days. Result: 10× to 100× storage reduction; queries that scan 1 day instead of all time.

---

### 📘 Textbook Definition

A **time-series database (TSDB)** is a database optimized for storing and querying time-indexed, append-mostly data where each record is associated with a timestamp. Key design choices: **columnar storage** (all timestamps together, all values together — enables column compression and vectorized scans), **time-based partitioning** (chunks by time window for fast retention management and query pruning), **compression algorithms** tuned for time-series data (delta-of-delta for timestamps, XOR/Gorilla for float values), **downsampling** / **rollup** (automatically aggregate high-resolution data into coarser resolutions for long-term retention). Leading implementations: **InfluxDB** (most widely used standalone TSDB), **TimescaleDB** (PostgreSQL extension — SQL + time-series optimizations), **Prometheus** (pull-based metrics + PromQL + local TSDB), **VictoriaMetrics** (InfluxDB-compatible, lower memory), **OpenTSDB** (HBase-based), **QuestDB** (SQL, very high write throughput), **Amazon Timestream** (managed cloud).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A TSDB is a database built around the assumption that data always comes in with a timestamp, is mostly appended (rarely updated), and must be efficiently compressed, retained, and queried over time ranges.

**One analogy:**

> A weather station log book. Every 10 minutes, the station writes one line: timestamp, temperature, humidity, pressure. The log book is always appended at the end (never random insertions). After a year, pages are photo-compressed (downsampled: hourly averages). After 5 years, further compressed to daily averages. To find last week's temperatures: flip to the recent pages — fast. To find the annual average from 3 years ago: read from the compressed section — also fast, because daily averages are tiny. A relational database would store each reading as a row with all columns, never compress, never drop old rows automatically.

- "Log book always appended" → append-mostly write pattern
- "Pages compressed after a year" → downsampling / rollup
- "Flip to recent pages" → time-based partitioning (queries prune to relevant chunks)
- "Daily averages after 5 years" → retention policies
- "Relational stores full rows forever" → no time-aware optimization

**One insight:**
The most powerful optimization in a TSDB is that you know the future won't change the past: time-series data is immutable once written. This allows aggressive compression — delta-delta encoding for timestamps is lossless but near-zero bits for regular intervals. Gorilla-style XOR encoding for float values exploits the fact that consecutive values are usually close together. TSDBs typically achieve 10× to 100× compression vs. raw storage.

---

### 🔩 First Principles Explanation

**COMPRESSION TECHNIQUES:**

```
Timestamp delta-delta encoding (Gorilla algorithm, Facebook):
  Raw:    [1592838450, 1592838460, 1592838470, 1592838480]  (10-second intervals)
  Delta:  [10, 10, 10, 10]  (constant interval)
  Delta of delta: [0, 0, 0]  → encodes as ~1 bit per value

  Irregular intervals:
  Raw:    [1592838450, 1592838453, 1592838461, 1592838462]
  Delta:  [3, 8, 1]
  Delta of delta: [5, -7]  → variable-length encoding

Float XOR compression:
  CPU usage often stays near previous value:
  0.55, 0.56, 0.55, 0.57 → XOR with previous: mostly leading zeros
  XOR encoding: store only the differing bits
  Compression ratio: ~1.37 bits per value (vs. 64 bits for raw double)
```

**INFLUXDB DATA MODEL:**

```
InfluxDB v1 (line protocol):
  measurement,tag_key=tag_val field_key=field_val timestamp

  cpu_usage,host=web-01,region=us-east user=0.55,system=0.12 1592838450000000000
  cpu_usage,host=web-02,region=us-east user=0.43,system=0.08 1592838450000000000

  measurement: cpu_cpu_usage (table-like grouping)
  tags: indexed dimensions (host, region) — LOW cardinality
  fields: actual values (user, system) — not indexed
  timestamp: nanosecond precision

  Rule: tags = dimensions you GROUP BY / filter on
        fields = values you measure (high cardinality ok)
  Anti-pattern: user_id as a tag → millions of tag values → high-cardinality hell
```

**TIMESCALEDB (POSTGRESQL + TIME-SERIES):**

```sql
-- TimescaleDB: PostgreSQL extension; full SQL + time-series optimizations
-- Create hypertable (time-partitioned):
SELECT create_hypertable('metrics', 'ts', chunk_time_interval => INTERVAL '1 day');
-- Every day = one chunk (separate file; old chunks compressed/dropped easily)

-- Insert (same as PostgreSQL):
INSERT INTO metrics (host, metric_name, value, ts)
VALUES ('web-01', 'cpu_usage', 0.55, NOW());

-- Time-series specific: downsampling with time_bucket
SELECT time_bucket('1 hour', ts) AS hour,
       avg(value) AS avg_cpu,
       max(value) AS max_cpu
FROM metrics
WHERE metric_name = 'cpu_usage' AND ts > NOW() - INTERVAL '7 days'
GROUP BY hour, host
ORDER BY hour DESC;

-- Retention policy: auto-drop data older than 30 days
SELECT add_retention_policy('metrics', INTERVAL '30 days');

-- Continuous aggregate (auto-updated materialized view):
CREATE MATERIALIZED VIEW metrics_hourly
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 hour', ts) AS hour, host, avg(value)
FROM metrics GROUP BY hour, host;
-- TimescaleDB auto-refreshes as new data arrives
```

**PROMETHEUS DATA MODEL:**

```
# Prometheus: pull-based metrics; stores as time-series locally
# Each time-series identified by metric name + label set

# Metric: http_requests_total{method="GET", status="200", service="orders"}
# Scrapes every 15s from /metrics endpoint of each service

# PromQL queries:
# Rate of requests per second over last 5 min:
rate(http_requests_total{service="orders"}[5m])

# P99 latency from histogram:
histogram_quantile(0.99,
  rate(http_request_duration_bucket{service="orders"}[5m]))

# Alert: error rate > 5% for 2 minutes:
alert: HighErrorRate
expr: rate(http_requests_total{status=~"5.."}[5m])
      / rate(http_requests_total[5m]) > 0.05
for: 2m

# Prometheus storage: local TSDB (blocks on disk, ~1.5B samples/server)
# Long-term: Thanos or VictoriaMetrics for multi-node, long-retention
```

---

### 🧪 Thought Experiment

**HIGH CARDINALITY: THE TSDB KILLER**

InfluxDB tag = indexed dimension. Low cardinality is fine: region (5 values), environment (3 values), service (50 values). High cardinality = disaster: user_id (10 million values) or request_id (unique per request) as a tag.

**WHY IT'S CATASTROPHIC:**
Each unique combination of tag values = one time-series in InfluxDB. 10M users × 5 metrics = 50 million time-series. The TSDB must maintain metadata for every time-series (inverted index of tag values). 50 million entries → the tag index grows to GBs of RAM just for metadata, before any actual data is stored. Queries filtering on user_id scan millions of index entries. This is the "cardinality bomb" — it can bring down a InfluxDB cluster.

**CORRECT APPROACH:**

- user_id → use as a FIELD (not a tag). Fields aren't indexed; you can store user_id in the data but can't efficiently filter by it.
- For per-user metrics: use a user-level aggregation (log per-user counts to a separate system — application DB) and store only aggregate metrics in the TSDB.
- Or: use a purpose-built high-cardinality TSDB (ClickHouse, Apache Druid) which uses columnar storage and can handle higher-cardinality dimensions.

---

### 🧠 Mental Model / Analogy

> A TSDB is like a smart bank statement printer. It only ever adds new transactions (append-only). Transactions from last month are automatically compressed into a monthly summary (downsampling). Transactions from 5 years ago are archived as annual summaries (long-term retention). When you ask "what happened last Tuesday?": it pulls out last week's page directly. When you ask "what was my average spending last year?": it reads the annual summary instead of billions of individual transactions. A regular spreadsheet (general DB) keeps every transaction forever at full detail, slowly growing until unusable.

- "Transactions appended" → time-series writes (append-mostly)
- "Monthly summary" → downsampling (1-minute averages from 1-second data)
- "Last week's page" → time-partitioned chunk (query pruning)
- "Annual summary" → long-term retention rollup
- "Spreadsheet keeping everything" → general DB: no time-aware optimization

---

### 📶 Gradual Depth — Four Levels

**Level 1:** A time-series database is a special database for storing things that change over time — like server metrics, sensor readings, or stock prices. Each measurement has a timestamp. The DB stores these efficiently (compressed) and makes it easy to ask "what happened between 2pm and 3pm yesterday" extremely fast.

**Level 2:** Choose your TSDB by workload: Prometheus for Kubernetes monitoring (pull-based, short retention, PromQL, Grafana native). InfluxDB for IoT/device metrics (push-based, line protocol). TimescaleDB when you need SQL + time-series + existing PostgreSQL tooling. VictoriaMetrics as a drop-in Prometheus replacement with lower memory. Set retention policies to auto-drop old data. Use continuous aggregates/rollups for dashboards (don't re-aggregate raw data for every panel render). Never put high-cardinality identifiers as tags in InfluxDB.

**Level 3:** Chunk management in TimescaleDB: each hypertable is split into time-based chunks (default 7 days). Each chunk is an independent PostgreSQL table with its own B-tree index. Query planning: TimescaleDB's planner prunes chunks outside the time range — only scans relevant chunks. Old chunks are compressed using TimescaleDB compression (columnar, dictionary encoding): 5-20× storage reduction, but compressed chunks become read-only. InfluxDB v3 (IOx): rewritten in Rust + Apache Arrow + Apache Parquet; columnar storage in object store (S3); separation of write buffer (in-memory) from storage (object store). Query via Flight SQL. Massive improvement in compression and query performance for analytical workloads.

**Level 4:** The time-series problem is a special case of the general columnar storage problem. TSDBs apply insights from columnar databases (Parquet, ORC, Apache Arrow) to temporal data: store values together (not row-by-row), apply column-specific compression, enable vectorized SIMD operations on contiguous memory. The delta-delta / Gorilla compression achieves compression ratios that row-oriented storage cannot because it exploits temporal correlation (consecutive values are similar). The TSDB is also a practical application of the time-to-live and data lifecycle management pattern: data has a natural "freshness decay." High-resolution recent data (10-second intervals for last 7 days) is worth storing. Historical data (1-year-old CPU metrics) is only useful at aggregate granularity (hourly averages). TSDBs automate this lifecycle, which a general-purpose DB requires manual management of (partition drop jobs, manual rollup materialized views). The cardinality problem reveals a fundamental tension: TSDB indexes are optimized for a fixed, small number of dimensions (low-cardinality tags). When users treat TSDBs as event stores (logging per-user or per-request data), cardinality explodes and the index becomes the bottleneck. The solution is architectural: use an event store (Kafka, Elasticsearch, ClickHouse) for high-cardinality event data; use TSDB exclusively for aggregated, low-cardinality metric data.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ PROMETHEUS TSDB WRITE PATH                           │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Scrape: GET /metrics from service every 15s         │
│  Prometheus parses metric lines:                     │
│  http_requests_total{method="GET"} 12345 1592838450  │
│                                                      │
│  Write to WAL (Write-Ahead Log): immediate durability│
│  Write to Head Block (in-memory):                    │
│    chunk per series: compressed delta-delta bytes    │
│    inverted index: label → series IDs                │
│                                                      │
│  Every 2h: Head Block → sealed TSDB Block on disk    │
│    index file: (label key → label value → series IDs)│
│    chunks dir: compressed sample data per series     │
│    tombstones: markers for deleted series            │
│                                                      │
│  Query: rate(http_requests_total[5m])                │
│  → Prune blocks outside [now-5m, now]                │
│  → Load only matching series (label match on index)  │
│  → Decode delta-delta chunks for those series        │
│  → Apply rate() function on samples                  │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**MICROSERVICE METRICS PIPELINE:**

```
Service: instrumented with Micrometer (Java) / prometheus-client (Python)
→ /metrics endpoint: counters, gauges, histograms exposed

Prometheus:
→ [TIME-SERIES DB ← YOU ARE HERE: metrics ingestion]
→ Scrapes /metrics every 15s
→ Stores to local TSDB (2 weeks retention)
→ Evaluates alert rules → fires to Alertmanager

Grafana:
→ PromQL query: avg(rate(http_requests_total[5m])) by (service)
→ Prometheus: prune to last 5 min → decode → rate() → result
→ Dashboard panel renders in < 100ms

Long-term (Thanos / VictoriaMetrics):
→ Prometheus remote_write to long-term store
→ Retention: 1 year at 15s resolution, 5 years at 1h resolution
```

---

### ⚖️ Comparison Table

| Feature           | TSDB (Prometheus)             | TSDB (InfluxDB)      | TSDB (TimescaleDB)         |
| ----------------- | ----------------------------- | -------------------- | -------------------------- |
| Query language    | PromQL                        | InfluxQL / Flux      | SQL                        |
| Ingestion model   | Pull (scrape)                 | Push (line protocol) | Push (SQL INSERT)          |
| SQL support       | None                          | Partial (Flux)       | Full PostgreSQL SQL        |
| Long-term storage | Thanos/Cortex/VictoriaMetrics | InfluxDB Enterprise  | Native                     |
| Kubernetes native | Yes (Helm charts, operators)  | Yes                  | Yes                        |
| Best for          | Infrastructure metrics        | IoT, device metrics  | SQL teams, metrics + joins |

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                                                                                                                       |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Prometheus is a long-term storage solution"            | Prometheus local TSDB is designed for short-term storage (default 15 days). For long-term, use Thanos, Cortex, or VictoriaMetrics as a remote write target                                                                    |
| "High-cardinality tags are fine if I have enough RAM"   | High cardinality is not a RAM problem — it's an index explosion problem. 100 million unique series overwhelms the inverted index regardless of available RAM                                                                  |
| "A TSDB can replace an event log (Kafka/Elasticsearch)" | TSDBs are for aggregated numeric metrics. Event logs (per-user, per-request) need an event store. Using a TSDB for event logs causes cardinality explosions                                                                   |
| "Downsampling means data loss"                          | Downsampling is a designed lossy compression that retains statistical summaries (min, max, avg, percentiles). For capacity planning and trend analysis, hourly averages are as useful as second-level data and 3,600× smaller |

---

### 🚨 Failure Modes & Diagnosis

**1. InfluxDB High Cardinality OOM**

**Symptom:** InfluxDB memory usage grows continuously; eventually OOM or extreme slowness. Series cardinality metric climbing toward millions.

**Root Cause:** High-cardinality tag added (user_id, request_id, session_id, trace_id as tags).

**Diagnostic:**

```bash
# InfluxDB cardinality query
SHOW SERIES CARDINALITY ON mydb
# > 1,000,000 → investigate
SHOW TAG VALUES WITH KEY = "user_id" LIMIT 10
# → millions of values → the culprit

influx query 'import "influxdata/influxdb" show series count() from bucket: "mydb"'
```

**Fix:** Delete the offending measurement and re-ingest without the high-cardinality tag. For the data that needs user-level granularity: use a different system (ClickHouse, BigQuery, or your OLTP DB).

**Prevention:** Hard limit: InfluxDB `max-series-per-database = 1000000` (InfluxDB config). Alert when series cardinality > 500,000. Design review for every new measurement: are all tags low-cardinality (< 10,000 unique values)?

---

### 🔗 Related Keywords

**Prerequisites:** Column Family, LSM Tree, Observability & SRE
**Builds On This:** Observability & SRE, System Design
**Related:** Column Family, Prometheus, InfluxDB

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ MODEL        │ Timestamp + tags (low-card) + fields      │
│ COMPRESSION  │ Delta-delta (ts) + XOR/Gorilla (float)    │
│ PARTITIONING │ Time chunks → efficient retention + prune │
│ CARDINALITY  │ Tags must be low-cardinality (<10K values) │
│ RETENTION    │ Auto-drop/downsampling by policy          │
│ TOOLS        │ Prometheus, InfluxDB, TimescaleDB, VictMet│
│ ONE-LINER    │ "Append-only timestamps — columnar         │
│              │  compression + time-partition = 100× win" │
│ NEXT EXPLORE │ Search Engine (Elasticsearch) → CRDTs     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C — Design Question) Design a monitoring stack for a Kubernetes cluster with 500 microservices, each emitting 200 metrics every 15 seconds. Requirements: real-time alerting (< 1 minute), dashboards for last 7 days at 15s resolution, 1-year historical retention at 1-minute resolution, cost-efficient storage. Design: which TSDB(s), what resolution at what retention horizon, how to handle the cardinality of 500 services × 200 metrics, and where to store long-term data.

**Q2.** (TYPE D — Failure Scenario) Your Prometheus instance is collecting metrics from 1,000 pods. It has 128GB RAM. After 3 weeks of running, Prometheus is OOM-killed repeatedly. The WAL replay on restart takes 10 minutes. When it finally starts: it falls behind on scraping. Diagnose the root cause (consider: series cardinality, remote write lag, WAL size, head block size). What immediate mitigations would you apply? What architectural change prevents recurrence?
