---
layout: default
title: "Snowflake Architecture (Virtual Warehouse, Storage)"
parent: "NoSQL & Distributed Databases"
nav_order: 13
permalink: /nosql/snowflake-architecture/
id: NDB-013
category: NoSQL & Distributed Databases
difficulty: ★★★
depends_on: Snowflake (Cloud Data Warehouse), Distributed Systems, Columnar Storage
used_by: Data Fundamentals, Big Data & Streaming
related: Snowflake (Cloud Data Warehouse), Databricks, Redshift
tags:
  - database
  - cloud
  - dataengineering
  - advanced
  - architecture
---

# NDB-013 — Snowflake Architecture (Virtual Warehouse, Storage)

⚡ TL;DR — Snowflake's three layers — cloud services (brain), virtual warehouses (muscles), and shared micro-partitioned storage (memory) — are independently scalable and interact through metadata, not data movement.

| Relation | Keywords |
|---|---|
| Depends on | Snowflake (Cloud Data Warehouse), Distributed Systems, Columnar Storage |
| Used by | Data Fundamentals, Big Data & Streaming |
| Related | Snowflake (Cloud Data Warehouse), Databricks, Redshift |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Traditional MPP warehouses (Redshift, Teradata) store data on the same nodes that execute queries. Scaling compute requires redistributing data. Data redistribution at petabyte scale takes hours. Concurrency isolation requires separate clusters with separate copies of the data. The engineering team provisioning the warehouse must predict peak compute demand weeks in advance, over-provisioning for the occasional spike.

**THE BREAKING POINT:** A Redshift cluster serving 200 GB of data needs an 8-node cluster for peak BI reporting. Data grows to 50 TB. Scaling requires a multi-hour resize operation with query interruptions. A concurrent data science team needs an isolated environment — they provision a second cluster and manually replicate data, doubling storage costs. The underlying problem: coupling the data with the compute makes independent scaling impossible.

**THE INVENTION MOMENT:** Snowflake's architecture solves this by introducing a stateless compute tier. Virtual warehouse nodes hold no persistent data — they are pure CPU and RAM. They read micro-partitions from shared object storage, cache locally for performance, and can be added, removed, or replaced without touching the data tier. This is the engineering unlock: compute becomes ephemeral; storage becomes permanent; both scale completely independently.

---

### 📘 Textbook Definition

**Snowflake Architecture** consists of three independently scaled layers: (1) the **Database Storage layer** — tables stored as columnar micro-partitions (50–500 MB compressed) in cloud object storage (S3/Azure Blob/GCS), with per-column min/max metadata for query pruning; (2) the **Query Processing layer** — **virtual warehouses** (MPP compute clusters) that read micro-partitions, cache them locally on SSD, execute query plans, and are billed per second of active use; and (3) the **Cloud Services layer** — a globally distributed control plane managing query compilation, optimization, metadata, authentication, ACID transaction control via MVCC, and the **result cache** (24-hour TTL for identical queries on unchanged data). These layers communicate via metadata pointers, not data movement.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Snowflake's architecture is "stateless compute reading stateful storage, coordinated by a smart control plane" — the compute can be replaced or scaled without touching the data.

> Think of Snowflake like a streaming service plus a data center. The movies (data) live on a distributed file server (S3). The smart TV remote (Cloud Services) knows which movie you want and where the files are. The TV screen (virtual warehouse) plays the movie from the file server. You can replace the TV, add more TVs, or turn them off — the movies remain unchanged.

**One insight:** The Cloud Services layer is the real differentiator. It holds all metadata — which micro-partitions belong to each table, which rows were deleted, what the min/max values are per partition. Virtual warehouses are stateless; they receive execution plans and micro-partition locations, fetch data, and return results.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Micro-partitions are immutable**: DML operations (`UPDATE`, `DELETE`) do not modify existing micro-partition files. They mark old rows as deleted (MVCC metadata) and write new micro-partitions. Old micro-partitions are retained for time travel.
2. **Virtual warehouse nodes are stateless**: all persistent state lives in the Cloud Services metadata store and the Storage layer. A virtual warehouse node failure is transparent — the query is retried or migrated to another node.
3. **The result cache is query-level, not row-level**: if the exact same SQL text runs twice on unchanged underlying data, the second execution returns the cached result without consuming virtual warehouse credits.
4. **Columnar compression** at the micro-partition level achieves 3–10× compression ratios using Run-Length Encoding (RLE), delta encoding, and dictionary encoding per column — reducing S3 read bytes and improving scan speeds.
5. **MVCC (Multi-Version Concurrency Control)**: reads never block writes; each query sees a consistent snapshot of the data as of its start time, regardless of concurrent DML operations.

**DERIVED DESIGN:**

- Query the Cloud Services result cache aggressively: schedule recurring reports to run at the same time so the result cache serves repeated executions.
- Size virtual warehouses based on query memory requirements, not data volume — data lives in S3, not in the warehouse.
- Use clustering keys on high-cardinality filter columns to maximize micro-partition pruning — reducing the number of partitions read directly reduces S3 I/O and credits consumed.
- Avoid SELECT * on large tables — columnar storage means selecting only needed columns reads far less data.

**THE TRADE-OFFS:**

**Gain:** Complete independent scalability of storage and compute; ACID semantics without a shared-memory lock manager; time travel and zero-copy cloning enabled by immutable micro-partitions; workload isolation between independent virtual warehouses reading the same data.

**Cost:** Cold virtual warehouse startup takes 3–10 seconds (loading metadata and warming local SSD cache); the Cloud Services layer adds a compilation and optimization overhead of 50–500 ms per query (significant for very short queries); very small queries (sub-second execution time) may spend more time in Cloud Services than in computation.

---

### 🧪 Thought Experiment

**SETUP:** A table `orders` has 100 billion rows across 3 years. A query filters `WHERE order_date = '2024-12-25'` — Christmas Day orders only. That represents 0.1% of all data.

**WHAT HAPPENS IN A TRADITIONAL ROW-STORE DATABASE:**
Full table scan: read all 100 billion rows, check `order_date` condition for each. I/O: ~50 TB read. Time: hours.

**WHAT HAPPENS IN REDSHIFT (COLUMNAR BUT COUPLED STORAGE/COMPUTE):**
Column-skip: read only the `order_date` column first. Still, all nodes must participate; data redistribution during query execution involves inter-node network traffic. Cannot use compute from other regions or accounts without data replication.

**WHAT HAPPENS IN SNOWFLAKE:**
1. Cloud Services layer looks up micro-partition metadata: each micro-partition's min/max for `order_date`.
2. Partitions where `max_order_date < '2024-12-25'` or `min_order_date > '2024-12-25'` are **pruned** (skipped entirely).
3. Typically, only 1–3 micro-partitions (out of thousands) contain December 25 data — these are fetched.
4. Virtual warehouse reads only those partitions, scanning only the needed columns within each.
5. Total data read: ~50 MB. Time: 200 ms.

**THE INSIGHT:** The combination of micro-partition pruning (partition-level skip) and columnar storage (column-level skip within each partition) creates a two-dimensional data filtering mechanism that dramatically reduces I/O regardless of table size.

---

### 🧠 Mental Model / Analogy

> Think of a well-organized physical library. The Cloud Services layer is the librarian who knows every book's location and can find any book in seconds using a card catalog. The micro-partitions are the bookshelves — organized, labeled, immutable once shelved. The virtual warehouse is the reading room — you rent a table (pay per second), the librarian fetches only the books you need, and multiple reading rooms can access the same library simultaneously.

- **Librarian + card catalog** = Cloud Services (metadata, query planner, result cache)
- **Bookshelf with labeled spines** = micro-partitions with min/max metadata
- **Only fetching relevant books** = micro-partition pruning
- **Multiple simultaneous reading rooms** = multiple independent virtual warehouses
- **Returning the table when done** = auto-suspend

Where this analogy breaks down: a physical library has one copy of each book; Snowflake's S3 storage replicates micro-partitions across availability zones automatically, so "book loss" (node failure) is automatically handled by cloud storage durability, not by Snowflake itself.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Snowflake splits the database into three parts: where data is stored (cheap cloud files), where queries run (rented computers), and a smart coordinator that knows where everything is. All three can be changed independently.

**Level 2 — How to use it (junior developer):**
When you run a query, Snowflake's coordinator (Cloud Services) checks if the result is already cached. If not, it compiles the query and sends an execution plan to your virtual warehouse. The warehouse fetches only the relevant micro-partitions from S3, applies columnar scans, and returns results. Your warehouse can be any size (XS to 6XL). Stop the warehouse when done; data persists in S3.

**Level 3 — How it works (mid-level engineer):**
Cloud Services runs the query optimizer, which produces a distributed execution plan. This plan is sent to the virtual warehouse coordinator node, which distributes work across worker nodes. Each worker node is assigned a set of micro-partitions to scan. Worker nodes maintain a local SSD cache (the "data cache") of recently accessed micro-partitions — subsequent queries on the same data hit local cache rather than S3, achieving near-memory-speed reads. The local cache is node-specific; scaling a warehouse up or down changes the effective cache size. MVCC is implemented in the Cloud Services metadata layer — each query receives a consistent snapshot ID, and micro-partitions are tagged with the transaction IDs that created or deleted them.

**Level 4 — Why it was designed this way (senior/staff):**
The immutability of micro-partitions is not just an implementation convenience — it is the cornerstone of three major features: (1) **time travel** (old micro-partitions are retained, queryable by snapshot timestamp); (2) **zero-copy cloning** (a clone is a new metadata entry pointing to the same micro-partition set); (3) **fail-safe** (Snowflake retains micro-partitions for 7 days beyond time travel for disaster recovery). All three emerge naturally from immutability with zero additional engineering. The Cloud Services layer's global metadata store (built on FoundationDB-like distributed key-value storage) is the centralized brain — it enables consistent ACID semantics across independent virtual warehouses without the warehouses communicating with each other. This is the critical insight: the statefulness that traditional coupled systems put in the compute tier (buffer pools, write-ahead logs, lock managers) is instead centralized in Cloud Services, enabling truly stateless, independently scalable compute.

---

### ⚙️ How It Works (Mechanism)

**Query Execution Deep Dive:**

```
1. SQL submitted to Cloud Services endpoint
          │
          ▼
2. Cloud Services: parse → semantic analysis
   → check result cache (24h TTL)
          │ cache miss
          ▼
3. Query optimizer: choose join order, pushdown
   predicates, generate distributed plan
          │
          ▼
4. Metadata lookup: which micro-partitions
   are in the table's current version?
   Apply min/max pruning → partition list
          │
          ▼
5. Plan dispatched to virtual warehouse
   coordinator node
          │
          ▼
6. Coordinator assigns partitions to worker nodes
   Worker: check local SSD cache first
   Cache miss: fetch from S3
          │
          ▼
7. Columnar scan: read only needed columns
   Apply filter predicates
   Aggregate/join per worker
          │
          ▼
8. Partial results sent to coordinator
   Final aggregation + sort
          │
          ▼
9. Result returned to Cloud Services
   Cloud Services caches result (if query eligible)
          │
          ▼
10. Client receives result rows
```

**Micro-Partition Structure:**

```
┌─────────────────────────────────────────────────┐
│ Micro-Partition Header (metadata)               │
│  created_tx: 1042  deleted_tx: null             │
│  row_count: 500000                              │
│  Columns:                                       │
│    order_date: min=2024-12-24 max=2024-12-26    │
│    region:     min="EU"       max="US"          │
│    amount:     min=0.01       max=9999.99       │
│─────────────────────────────────────────────────│
│ Column Data (PAX columnar layout)               │
│  [order_date col] [region col] [amount col]     │
│  (RLE/delta/dict compressed per column)         │
└─────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Table load: COPY INTO orders FROM @s3_stage
          │
          ▼
Cloud Services: create micro-partitions,
  write to S3, record metadata
  (min/max per column, transaction ID)
          │
          ▼
Query: SELECT sum(amount) WHERE date = today
          │
          ▼
Cloud Services: result cache check (miss)
          │
          ▼
Prune: 99% of partitions eliminated
  by date min/max metadata            ← YOU ARE HERE
          │
          ▼
Virtual warehouse fetches 3 partitions
  from S3 (or local cache if warm)
          │
          ▼
Columnar scan: read only 'amount' + 'date'
  columns → aggregation → result
          │
          ▼
Result cached in Cloud Services (24h)
```

**FAILURE PATH:**
- Virtual warehouse node failure → worker node is replaced, query partition is retried on replacement node
- Cloud Services outage → all queries fail (single point of control, though globally distributed)
- Micro-partition count exceeds pruning threshold → automatic clustering or manual RECLUSTER required
- Result cache miss due to DML on underlying table → full query execution on every run

**WHAT CHANGES AT SCALE:**
- 100 TB table: micro-partition count = 200 000+; partition metadata stored in Cloud Services metadata layer (not in the warehouse nodes)
- Multi-cluster warehouse: coordinator node distributes work across clusters; each cluster has its own local SSD cache (warm one cluster = cold cache on the other)
- Data sharing: external consumers read the same micro-partitions via a shared metadata pointer — no data movement, near-zero latency for data providers

---

### 💻 Code Example

**BAD — querying without partition pruning (no filter on clustering key):**
```sql
-- Scans all micro-partitions — no pruning benefit
SELECT
  customer_id,
  sum(order_total) AS lifetime_value
FROM orders
-- No filter on clustering key (order_date)
-- → Cloud Services cannot prune partitions
GROUP BY customer_id
ORDER BY lifetime_value DESC
LIMIT 100;
```

**GOOD — structured for pruning and columnar efficiency:**
```sql
-- Step 1: check result cache eligibility
-- Run this query periodically at the same time
-- so the 24h result cache serves it

-- Step 2: design for partition pruning
SELECT
  region,
  product_category,
  sum(order_total) AS total_revenue,
  count(*) AS order_count
FROM orders
-- Filter on clustering key → micro-partition pruning
WHERE order_date BETWEEN '2024-01-01' AND '2024-12-31'
  AND status = 'completed'
-- Select only needed columns (columnar efficiency)
GROUP BY region, product_category
ORDER BY total_revenue DESC;

-- Check pruning effectiveness via QUERY_HISTORY
SELECT
  query_id,
  partitions_scanned,
  partitions_total,
  (partitions_scanned * 100.0 / partitions_total)
    AS pct_scanned
FROM snowflake.account_usage.query_history
WHERE query_id = '<query_id>'
  AND partitions_total > 0;
-- Goal: pct_scanned < 10% for well-clustered data

-- Monitor cache effectiveness
SELECT
  result_cache_hit,
  count(*) AS query_count
FROM snowflake.account_usage.query_history
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
GROUP BY result_cache_hit;
```

---

### ⚖️ Comparison Table

| Architecture Aspect | Snowflake | Redshift | BigQuery | Databricks |
|---|---|---|---|---|
| Storage layer | S3/Blob/GCS (micro-partitions) | RA3 managed S3 (RMS) | Google Colossus | Delta Lake (S3/ADLS) |
| Compute layer | Virtual warehouses (per-second) | Nodes/slices (per-hour) | Serverless slots | Clusters (DBU/hour) |
| Metadata layer | Cloud Services (global, centralised) | Leader node | Google Cloud Bigtable | Delta transaction log |
| Result cache | 24h TTL, per-query | None native | Slot-time cache | Partial (Delta cache) |
| Concurrency model | Multi-cluster (parallel warehouses) | Queue-based | Slot reservations | Autoscaling clusters |
| Partition pruning | Min/max metadata on micro-partitions | Sortkey-based zone maps | Partitioned tables | Delta Z-order |
| MVCC | Cloud Services snapshot IDs | Block-level MVCC | Snapshot isolation | Delta log versioning |
| Time travel | Up to 90 days | No native | 7-day snapshot | Delta log (configurable) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Virtual warehouses cache all table data locally" | Virtual warehouses cache recently accessed micro-partitions on local SSD; the cache is bounded by node storage and is not a full data copy |
| "Larger warehouse = better partition pruning" | Partition pruning is a Cloud Services function using metadata — warehouse size does not affect which partitions are pruned |
| "Result cache works for all queries" | Result cache requires identical SQL text (including comments and whitespace), unchanged underlying table data since last cache, and the same role/warehouse context |
| "Scaling a virtual warehouse up migrates data" | Scaling a warehouse adds or replaces nodes; no data migration occurs because virtual warehouse nodes hold no persistent data |
| "The Cloud Services layer is free" | Cloud Services consumes credits (capped at 10% of compute credits); heavy metadata operations (listing stages, query compilation) can contribute to Cloud Services credit consumption |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Result Cache Not Being Used (Unexpected Credit Consumption)**

**Symptom:** Scheduled reports that run every hour consume credits on every execution; expected cache hits are misses; bill is 10× higher than estimated.
**Root Cause:** A DML operation (even a minor `UPDATE`) invalidates the result cache for all queries touching the affected table; alternatively, query text has non-deterministic elements (e.g., `CURRENT_TIMESTAMP()`) that prevent caching.
**Diagnostic:**
```sql
SELECT
  query_id,
  query_text,
  result_cache_hit,
  credits_used_cloud_services
FROM snowflake.account_usage.query_history
WHERE start_time >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
  AND query_text ILIKE '%orders%'
ORDER BY start_time;
-- Look for result_cache_hit = FALSE on repeated queries
```
**Fix:** Replace `CURRENT_TIMESTAMP()` in report queries with a parameterized date variable set to the start of the reporting period. Ensure no background DML runs between report executions.
**Prevention:** Design recurring report queries with static parameters. Schedule DML (ETL loads) at different times than scheduled report queries to preserve the result cache.

---

**Failure Mode 2: Cloud Services Credit Overrun**

**Symptom:** Monthly Snowflake bill shows Cloud Services credits exceeding 10% of compute credits, triggering additional billing; this occurs even when warehouses are suspended.
**Root Cause:** Excessive metadata operations: extremely high-frequency short queries (each requiring full compilation), large-scale `SHOW` operations, or automated tools issuing `LIST @stage` commands on large stages thousands of times per hour.
**Diagnostic:**
```sql
SELECT
  query_type,
  count(*) AS query_count,
  sum(credits_used_cloud_services) AS cs_credits
FROM snowflake.account_usage.query_history
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
GROUP BY query_type
ORDER BY cs_credits DESC;
-- Look for LIST, SHOW, DESCRIBE at high frequency
```
**Fix:** Reduce `LIST @stage` frequency in ETL orchestration. Cache stage listing results in the orchestration tool rather than re-listing on every pipeline run.
**Prevention:** Monitor Cloud Services credit ratio in the Snowflake resource monitor. Alert when Cloud Services credits exceed 5% of total credits.

---

**Failure Mode 3: Local Cache Miss After Warehouse Scaling**

**Symptom:** After scaling a virtual warehouse from Medium to Large to handle increased load, query latency temporarily increases and then recovers after 10–20 minutes.
**Root Cause:** Scaling up the warehouse replaces nodes (or adds new nodes). New nodes have cold local SSD caches. The first queries after scaling must fetch micro-partitions from S3 until the cache warms up.
**Diagnostic:**
```sql
-- Compare bytes scanned vs bytes from cache
SELECT
  query_id,
  bytes_scanned,
  bytes_scanned_from_cache,
  (bytes_scanned_from_cache * 100.0 / bytes_scanned)
    AS cache_hit_pct
FROM snowflake.account_usage.query_history
WHERE warehouse_name = 'BI_WH'
  AND start_time BETWEEN scaling_time AND
    DATEADD(minute, 30, scaling_time)
ORDER BY start_time;
-- Expect low cache_hit_pct immediately after scaling
```
**Fix:** Accept the warm-up period as expected behavior. For latency-critical workloads, run "warm-up queries" — representative SELECT queries on hot tables immediately after scaling.
**Prevention:** Pre-warm critical warehouses using automated warm-up scripts that run representative queries after warehouse resume. Consider keeping critical warehouses at a fixed size to maintain cache warmth.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Snowflake (Cloud Data Warehouse) — the product-level overview and use case context for this architecture deep dive
- Distributed Systems — the replication, consistency, and scalability principles that the three-tier architecture implements
- Columnar Storage — the storage format of micro-partitions; why column-skip and compression ratios are central to Snowflake's performance

**Builds On This (learn these next):**
- Data Fundamentals — Snowflake architecture is the compute and storage layer for enterprise data pipelines
- Big Data & Streaming — Snowpipe (continuous micro-batch ingestion) and Kafka connectors extend the architecture to streaming workloads

**Alternatives / Comparisons:**
- Snowflake (Cloud Data Warehouse) — the product-level entry providing context for this architecture entry
- Databricks — Lakehouse architecture with Delta Lake; unified analytics and ML on the same storage tier
- Redshift — AWS warehouse with RA3 (managed storage + compute separation); different architecture trade-offs

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ WHAT IT IS    Three-tier architecture:          │
│               Cloud Services + VW + S3 storage │
│ PROBLEM       Coupled storage+compute prevents  │
│               independent scaling or workload   │
│               isolation                         │
│ KEY INSIGHT   Immutable micro-partitions enable │
│               pruning, time travel, cloning,    │
│               and stateless compute in one step │
│ USE WHEN      Diagnosing Snowflake perf issues; │
│               sizing VWs; optimizing costs      │
│ AVOID WHEN    Treating Snowflake as OLTP;       │
│               sub-second query SLA workloads    │
│ TRADE-OFF     3-10s cold start vs true          │
│               serverless independence           │
│ ONE-LINER     Partition pruning + columnar scan │
│               + result cache = Snowflake speed  │
│ NEXT EXPLORE  ElastiCache                       │
└─────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(E — First Principles)** Snowflake uses MVCC for concurrency control implemented entirely in the Cloud Services metadata layer rather than in the virtual warehouse nodes. Explain exactly how a `SELECT` query can read a consistent snapshot of a table while a concurrent `UPDATE` is modifying rows, without either query holding locks visible to the other. What metadata does Cloud Services track to make this possible?

2. **(D — Root Cause)** After 6 months of daily loads into a 20 TB table clustered by `order_date`, the `SYSTEM$CLUSTERING_INFORMATION` function shows `average_depth: 8.3` (up from 1.2 initially). What has caused this degradation, what does `average_depth` physically represent in terms of micro-partition organization, and what operation does Snowflake perform to restore it?

3. **(A — System Interaction)** A Snowflake data sharing provider shares a live `sales` database with 5 consumer accounts. The provider runs a large `UPDATE` on the `orders` table. Describe the physical state of the micro-partitions before and after the update, and explain whether the consumers experience any query latency increase or data availability interruption during the update.
