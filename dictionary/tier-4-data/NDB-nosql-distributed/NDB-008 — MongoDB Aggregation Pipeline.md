---
layout: default
title: "MongoDB Aggregation Pipeline"
parent: "NoSQL & Distributed Databases"
nav_order: 8
permalink: /nosql/mongodb-aggregation-pipeline/
id: NDB-008
category: NoSQL & Distributed Databases
difficulty: ★★★
depends_on: MongoDB Document Schema Design, MongoDB Indexing Strategies
used_by: Data Fundamentals, Big Data & Streaming
related: SQL Window Functions, MapReduce, OpenSearch / Elasticsearch
tags:
  - database
  - distributed
  - advanced
  - algorithm
---

# NDB-008 — MongoDB Aggregation Pipeline

⚡ TL;DR — MongoDB's aggregation pipeline transforms documents through ordered stages; `$match` early for index use, `$group` for aggregation, and `$lookup` for joins — with `allowDiskUse` for large datasets.

| Relation | Keywords |
|---|---|
| Depends on | MongoDB Document Schema Design, MongoDB Indexing Strategies |
| Used by | Data Fundamentals, Big Data & Streaming |
| Related | SQL Window Functions, MapReduce, OpenSearch / Elasticsearch |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Before the aggregation pipeline (pre-MongoDB 2.2), complex data transformations required MapReduce — a two-phase JavaScript-based framework that was slow, hard to debug, and sent all data to the application layer for processing. Reporting queries required pulling millions of documents over the network, aggregating in application memory, and hoping the server had enough RAM.

**THE BREAKING POINT:** A reporting dashboard needs daily revenue by product category for the last 30 days. Without the aggregation pipeline: fetch all 5 million orders from the last 30 days to the app, group in memory, sum totals. Network transfer: 15 GB. Memory required: 8 GB. Time: 45 seconds. The query kills the application server every night.

**THE INVENTION MOMENT:** The aggregation pipeline processes data *server-side* using a declarative stage-based model. Each stage transforms the document stream, filters are applied before large data movements, and indexes accelerate the early stages. The same report runs in 800 ms — the processing happens where the data lives, network transfer is the aggregated result only.

---

### 📘 Textbook Definition

The **MongoDB Aggregation Pipeline** is a server-side data processing framework that transforms a stream of documents through a sequence of **stages**. Each stage accepts documents, performs a transformation (filter, reshape, join, group, sort, limit), and passes results to the next stage. The pipeline executes server-side in the `mongod` process, using indexes on early stages to minimize the document set. Stages include `$match` (filter), `$project` (reshape), `$group` (aggregate), `$sort`, `$limit`, `$skip`, `$lookup` (join), `$unwind` (flatten arrays), `$addFields`, `$bucket`, `$facet`, and `$out`/`$merge` (write results). Pipelines support `explain()` for execution plan analysis and `allowDiskUse: true` for datasets exceeding the 100 MB in-memory sort limit.

---

### ⏱️ Understand It in 30 Seconds

**One line:** The aggregation pipeline is a Unix pipe for documents — each stage filters or transforms the stream, and ordering of stages determines performance.

> Think of it like an assembly line. Raw car parts enter at one end; each station does one operation (paint, weld, inspect); finished cars exit at the other end. Moving the inspection station earlier catches defects sooner and saves work on parts that would have been discarded anyway.

**One insight:** Pipeline stage order is a performance variable, not just a semantic choice. `$match` before `$group` uses an index to reduce documents early; `$match` after `$group` processes the full dataset. The same logical query can differ by 100× in execution time based solely on stage order.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Stages execute sequentially; each stage receives the output of the previous stage as its input stream.
2. The first stage that can use an index is the `$match` stage (and `$sort` for prefix-covered sorts) — no later stage benefits from collection-level indexes.
3. MongoDB enforces a **100 MB RAM limit** per aggregation stage; `allowDiskUse: true` spills to disk for `$sort` and `$group`.
4. `$lookup` performs a nested-loop join by default; an indexed `$lookup` (with pipeline syntax) uses an index on the foreign collection.
5. `$unwind` on an array of N elements explodes one document into N documents — cardinality can multiply dramatically and must be controlled with early `$match` on array elements.

**DERIVED DESIGN:**

- Put `$match` and `$sort` as early as possible → index usage, smaller document set flowing to subsequent stages.
- Put `$project` or `$addFields` before stages that transmit documents over the network in a sharded cluster.
- Use `$limit` early when only the top-N results are needed (e.g., leaderboard queries).
- Use `$facet` to run multiple sub-pipelines in parallel on the same input set for dashboard queries.

**THE TRADE-OFFS:**

**Gain:** Server-side processing eliminates network transfer of raw documents; declarative pipeline syntax is composable, testable stage-by-stage, and optimizable by the query planner; `$merge` enables incremental materialized views.

**Cost:** Complex pipelines are harder to debug than SQL; the 100 MB per-stage RAM limit requires `allowDiskUse` for large sorts/groups; `$lookup` is a scan-time join (not an optimizer-planned join as in SQL), so cardinality must be managed manually.

---

### 🧪 Thought Experiment

**SETUP:** You need to produce a monthly sales report: total revenue and order count per product category, for orders placed in the last 30 days, sorted by revenue descending, top 10 categories only.

**WHAT HAPPENS WITHOUT THE AGGREGATION PIPELINE:**
Fetch all orders from the last 30 days (via `find()`), stream 3 million documents to the application, group by category in application memory using a `Map<String, Double>`, sort the map, take the top 10. Network bandwidth consumed: 4 GB. Application memory: 2 GB spike. Duration: 40 seconds. If the process crashes mid-query, no partial result is available.

**WHAT HAPPENS WITH THE AGGREGATION PIPELINE:**
```javascript
db.orders.aggregate([
  { $match: { createdAt: { $gte: thirtyDaysAgo } } }, // uses index
  { $group: {
    _id: "$category",
    totalRevenue: { $sum: "$total" },
    orderCount: { $count: {} }
  }},
  { $sort: { totalRevenue: -1 } },
  { $limit: 10 }
])
```
Network transfer: 10 documents (the result). Server RAM usage: the 30-day filtered documents only. Duration: 180 ms. The pipeline is a first-class citizen of the query planner — MongoDB optimizes `$match` + `$sort` into an index scan.

**THE INSIGHT:** The aggregation pipeline shifts the architectural principle from *"move data to the logic"* to *"move logic to the data"*. This is the same insight that drove MapReduce, Spark, and SQL itself — minimize data movement, maximize server-side computation.

---

### 🧠 Mental Model / Analogy

> The aggregation pipeline is like a series of colanders (strainers) of different sizes stacked in a sink. You pour in a bag of mixed gravel, sand, and marbles. The first colander catches marbles, the second catches gravel, the third catches sand. Each layer passes only what fits through its holes and transforms the stream. At the end you have sorted output, not the original mix.

- **Pour the bag** = `db.collection.aggregate([...])`
- **Each colander** = each pipeline stage
- **Colander mesh size** = the filter or transformation criteria
- **First colander = finest mesh** = put `$match` first to eliminate most documents early
- **What passes through** = the document stream from stage to stage

Where this analogy breaks down: colanders in a sink work in parallel on all input simultaneously; pipeline stages in MongoDB process documents one-at-a-time (streaming), which means memory use is bounded by the largest single document set in any stage, not the total collection size.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
The aggregation pipeline is a set of instructions that MongoDB follows to process and summarize data without sending it all to your application. You describe *what* you want as a series of steps; MongoDB does the work on the server and returns only the answer.

**Level 2 — How to use it (junior developer):**
Build pipelines with three fundamental stages: `$match` to filter documents (like SQL's `WHERE`), `$group` to aggregate (like SQL's `GROUP BY` + `SUM`/`COUNT`), and `$project` to select and rename fields (like SQL's `SELECT`). Always put `$match` first. Use `explain()` to verify index use.

**Level 3 — How it works (mid-level engineer):**
The aggregation pipeline is evaluated by the **aggregation executor** in `mongod`. Stages are linked via an internal cursor. MongoDB's query optimizer rewrites the pipeline before execution — it merges adjacent `$match` stages, pushes `$match` before `$lookup` when possible, and converts `$sort` + `$limit` into a top-K heap operation to avoid full sorts. `$lookup` uses a sub-pipeline that runs a `find()` on the foreign collection for each input document — it benefits from an index on the foreign collection's join key. The `allowDiskUse` flag enables spill files for `$sort` and `$group` when in-memory limits are exceeded.

**Level 4 — Why it was designed this way (senior/staff):**
The aggregation pipeline's stage-based design mirrors the relational algebra operators (selection, projection, join, aggregation) but exposes them as composable, inspectable steps rather than hiding them behind a query optimizer. This transparency is a deliberate trade-off: engineers can see and control stage order (unlike SQL's optimizer-black-box), enabling deterministic performance tuning. The 100 MB per-stage limit is a safety valve — it prevents runaway queries from monopolizing RAM on multi-tenant `mongod` instances. The `$merge` stage (MongoDB 4.2+) enables incremental materialized views by merging pipeline output back into a collection, bridging OLTP and OLAP workloads without external ETL.

---

### ⚙️ How It Works (Mechanism)

**Pipeline Execution Flow:**

```
db.orders.aggregate([...])
          │
          ▼
Query Planner rewrites pipeline
  (push $match early, merge stages)
          │
          ▼
Stage 1: $match  ──► index scan on createdAt
  Output: filtered document cursor
          │
          ▼
Stage 2: $group  ──► hash aggregation in RAM
  (spills to disk if > 100 MB)
          │
          ▼
Stage 3: $sort   ──► top-K heap (with $limit)
          │
          ▼
Stage 4: $limit  ──► return first N docs
          │
          ▼
Driver deserializes result → application
```

**Key Stage Reference:**

| Stage | Purpose | Index Eligible | Cost |
|---|---|---|---|
| `$match` | Filter documents | Yes (first stage) | Low with index |
| `$group` | Aggregate + summarize | No | Medium–High (hash) |
| `$project` | Reshape, add/remove fields | No | Low |
| `$lookup` | Join foreign collection | Yes (foreign key) | High at scale |
| `$unwind` | Flatten array to N docs | No | Multiplies cardinality |
| `$sort` | Order documents | Yes (prefix) | High without limit |
| `$facet` | Parallel sub-pipelines | No | High (two passes) |
| `$out`/`$merge` | Write results to collection | N/A | I/O bound |

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Application calls aggregate([pipeline])
          │
          ▼
mongod: query planner analyses pipeline
  rewrites: push $match before $lookup
          │
          ▼
$match stage: index scan on filtered field
  Documents: 500 000 → 12 000    ← YOU ARE HERE
          │
          ▼
$lookup stage: for each doc, index lookup
  on foreign collection (products)
          │
          ▼
$group stage: hash-based aggregation
  RAM: up to 100 MB; else spill to disk
          │
          ▼
$sort + $limit: top-K heap, return 10 docs
          │
          ▼
Result cursor streamed to driver
```

**FAILURE PATH:**
- `$sort` on unindexed field without `$limit` → full in-memory sort → `MongoServerError: Exceeded memory limit for $sort` (> 100 MB) → add `allowDiskUse: true` or add sort index
- `$unwind` without prior `$match` on array → 1 document with 10 000 array elements → 10 000 output documents → downstream `$group` OOM
- `$lookup` on unindexed foreign field → COLLSCAN on foreign collection → 30-second timeout

**WHAT CHANGES AT SCALE:**
- Sharded clusters: `$lookup` across shards requires the `mongos` to scatter-gather — foreign collection must be unsharded or `$lookup` must be performed on the shard local to the primary shard
- `$group` without `$match` on a sharded collection → two-phase aggregation: parallel groups per shard, then merge on `mongos`
- `$out` writes to a new collection atomically; `$merge` supports upsert/replace/keepExisting modes for incremental refresh

---

### 💻 Code Example

**BAD — fetch all to application, aggregate in memory:**
```javascript
// Bad: pulls all orders to Node.js for grouping
const orders = await db.orders
  .find({ createdAt: { $gte: thirtyDaysAgo } })
  .toArray()  // 3 million documents over network

const report = orders.reduce((acc, order) => {
  acc[order.category] = (acc[order.category] || 0)
    + order.total
  return acc
}, {})
```

**GOOD — server-side aggregation pipeline:**
```javascript
const report = await db.orders.aggregate([
  // Stage 1: filter early — uses index on createdAt
  { $match: {
    createdAt: { $gte: thirtyDaysAgo },
    status: "completed"
  }},
  // Stage 2: join product category from products
  { $lookup: {
    from: "products",
    localField: "productId",
    foreignField: "_id",
    as: "product",
    pipeline: [
      { $project: { category: 1 } }  // reduce data
    ]
  }},
  { $unwind: "$product" },
  // Stage 3: group by category
  { $group: {
    _id: "$product.category",
    totalRevenue: { $sum: "$total" },
    orderCount: { $count: {} },
    avgOrderValue: { $avg: "$total" }
  }},
  // Stage 4: sort and limit
  { $sort: { totalRevenue: -1 } },
  { $limit: 10 },
  // Stage 5: rename output fields
  { $project: {
    category: "$_id",
    totalRevenue: 1,
    orderCount: 1,
    avgOrderValue: { $round: ["$avgOrderValue", 2] },
    _id: 0
  }}
], { allowDiskUse: true }).toArray()
```

**Inspecting execution with explain:**
```javascript
// Always verify index use before production deployment
const plan = await db.orders.aggregate([
  { $match: { createdAt: { $gte: thirtyDaysAgo } } },
  { $group: { _id: "$category", total: { $sum: "$amount" }}}
], { explain: true })

// Look for: "stage": "IXSCAN" in first $match stage
// Avoid: "stage": "COLLSCAN"
console.log(JSON.stringify(plan, null, 2))
```

---

### ⚖️ Comparison Table

| Feature | MongoDB Aggregation | SQL (Postgres) | Spark SQL | MapReduce (MongoDB legacy) |
|---|---|---|---|---|
| Execution location | Server-side | Server-side | Distributed cluster | Server-side (slow JS) |
| Index use | First `$match`/`$sort` | Query optimizer | Partition pruning | None |
| Join type | `$lookup` (scan/index) | Query-planned JOIN | Shuffle join | Manual in reduce phase |
| In-memory limit | 100 MB/stage | Work_mem per query | Executor memory | No explicit limit |
| Materialized results | `$out`/`$merge` | `CREATE TABLE AS` | `DataFrame.write` | Output collection |
| Debuggability | `explain()` + stages | `EXPLAIN ANALYZE` | Spark UI DAG | Difficult |
| Best for | Document-native aggregation | OLTP+OLAP mixed | Petabyte-scale ETL | Avoid (deprecated) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "`$match` anywhere in the pipeline uses an index" | Only the *first* `$match` stage (and `$sort` matching a sort index prefix) benefits from collection-level indexes |
| "`$lookup` is equivalent to a SQL JOIN in performance" | `$lookup` is a nested-loop join executed at query time; SQL optimizers may choose hash joins, merge joins, or indexed lookups based on statistics — MongoDB does not |
| "`allowDiskUse: true` solves all memory issues" | Disk spill for `$sort`/`$group` can be 10–100× slower than in-memory; it is a safety valve, not a performance strategy |
| "`$unwind` is always necessary to process arrays" | Many array operators (`$filter`, `$map`, `$reduce`, `$size`) work directly on arrays without unwinding; `$unwind` multiplies cardinality and should be avoided when not required |
| "Stage order doesn't matter if the result is the same" | Stage order directly determines whether indexes are used and how many documents flow through expensive stages — the same logical result can differ by 1000× in execution time |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: $sort Memory Limit Exceeded**

**Symptom:** `MongoServerError: Exceeded memory limit for $sort stage`; pipeline fails without returning results.
**Root Cause:** A `$sort` stage must sort more than 100 MB of documents in memory; `allowDiskUse` is not set; no `$match` or `$limit` precedes the `$sort` to reduce cardinality.
**Diagnostic:**
```javascript
db.orders.aggregate([
  { $group: { _id: "$category", total: { $sum: "$amount" }}},
  { $sort: { total: -1 } }
], { explain: true })
// Check: "memLimit" and "usedDisk" fields in explain output
```
**Fix:** Add `allowDiskUse: true` as a short-term fix. Long-term: add a `$match` stage before `$sort` to reduce the document set, or add a sort index so the `$sort` stage is index-backed.
**Prevention:** Always pair `$sort` with `$limit` when only top-N results are needed; this enables a heap-based top-K algorithm that never loads the full set.

---

**Failure Mode 2: $lookup Causing Full Collection Scan**

**Symptom:** Aggregation queries time out or take > 30 seconds; `db.currentOp()` shows long-running aggregations; `explain()` shows `COLLSCAN` on the foreign collection.
**Root Cause:** The `foreignField` in `$lookup` has no index on the foreign collection; every input document triggers a full scan of the foreign collection.
**Diagnostic:**
```javascript
db.orders.explain("executionStats").aggregate([
  { $lookup: {
    from: "products",
    localField: "productId",
    foreignField: "_id",  // _id has implicit index — fine
    as: "product"
  }}
])
// For non-_id foreignField, check for IXSCAN vs COLLSCAN
db.products.getIndexes()
```
**Fix:** Create an index on the foreign collection's lookup field:
```javascript
db.products.createIndex({ sku: 1 })
// Then use: foreignField: "sku"
```
**Prevention:** Treat `$lookup` as a join — always verify index coverage on the foreign field before deploying to production.

---

**Failure Mode 3: $unwind Cardinality Explosion**

**Symptom:** Pipeline returns millions of documents from a thousands-document input; downstream `$group` OOMs or times out.
**Root Cause:** `$unwind` on a large array field before any filtering multiplies document count; a collection of 10 k products each with 1 k tags produces 10 M intermediate documents.
**Diagnostic:**
```javascript
// Check intermediate cardinality with $count
db.products.aggregate([
  { $unwind: "$tags" },
  { $count: "totalAfterUnwind" }
])
// Compare to: db.products.countDocuments()
```
**Fix:** Filter before `$unwind`:
```javascript
// BAD: unwind then filter
{ $unwind: "$tags" },
{ $match: { tags: "sale" } }

// GOOD: filter array elements before unwind
{ $match: { tags: "sale" } },  // uses multikey index
{ $unwind: "$tags" },
{ $match: { tags: "sale" } }   // filter non-matching after unwind
```
**Prevention:** Place `$match` before `$unwind` when filtering on array contents; use `$filter` operator inside `$project` to pre-filter array elements without unwinding.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- MongoDB Document Schema Design — document structure determines what fields are available to pipeline stages
- MongoDB Indexing Strategies — indexes are the mechanism that makes `$match` and `$sort` efficient in pipelines

**Builds On This (learn these next):**
- Data Fundamentals — the aggregation pipeline is a core tool for analytical queries in MongoDB deployments
- Big Data & Streaming — `$merge` and `$out` stages connect the aggregation pipeline to streaming and ETL workflows

**Alternatives / Comparisons:**
- SQL Window Functions — relational equivalent for ranking, running totals, and partitioned aggregations
- MapReduce — the legacy MongoDB processing model that the aggregation pipeline replaced
- OpenSearch / Elasticsearch — alternative search and aggregation engine with its own DSL

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ WHAT IT IS    Server-side document stream       │
│               transformation via ordered stages │
│ PROBLEM       Application-side aggregation of  │
│               millions of docs kills performance│
│ KEY INSIGHT   $match early = index use;         │
│               stage order is a perf variable    │
│ USE WHEN      Reporting, analytics, joins,      │
│               data transformation in MongoDB    │
│ AVOID WHEN    Simple key-value lookups (use     │
│               findOne instead)                  │
│ TRADE-OFF     Powerful server-side compute vs   │
│               100 MB/stage RAM limit            │
│ ONE-LINER     $match → $group → $sort → $limit  │
│               = the 80% query pattern           │
│ NEXT EXPLORE  MongoDB Indexing Strategies       │
└─────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(B — Scale)** Your aggregation pipeline `$group`s 200 million documents with `allowDiskUse: true`. Disk spill triples query time to 90 seconds. What two schema-level changes could you make so this same aggregation query runs in under 5 seconds without changing the pipeline itself?

2. **(C — Design Trade-off)** The `$facet` stage runs multiple sub-pipelines on the same input set. When would you prefer `$facet` over multiple separate `aggregate()` calls, and when does `$facet` actually make performance *worse* than separate queries?

3. **(A — System Interaction)** In a sharded MongoDB cluster, a pipeline starts with `$lookup` on an unsharded `products` collection from a sharded `orders` collection. Describe exactly where in the cluster the `$lookup` executes, why the `mongos` router cannot push it to individual shards, and what schema change would eliminate the cross-shard join entirely.
