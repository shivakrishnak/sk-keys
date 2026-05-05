---
layout: default
title: "Spark RDD"
parent: "Big Data & Streaming"
nav_order: 536
permalink: /big-data-streaming/spark-rdd/
number: "0536"
category: Big Data & Streaming
difficulty: ★★★
depends_on: Apache Spark, MapReduce
used_by: Spark DataFrame, Spark Streaming, MLlib
related: Apache Spark, Spark DataFrame, Distributed Computing
tags:
  - spark-rdd
  - resilient-distributed-dataset
  - lineage
  - fault-tolerance
  - deep-dive
---

# 536 — Spark RDD

⚡ TL;DR — Spark **RDD (Resilient Distributed Dataset)** is Spark's foundational abstraction — an **immutable, partitioned, fault-tolerant collection** distributed across the cluster; resilience comes from **lineage** (recorded transformation graph), not replication — if a partition is lost, recompute it from parent RDDs; superseded by DataFrames/Datasets for most use cases (Catalyst + Tungsten optimizations), but still the underlying engine and essential for custom partitioning and fine-grained control.

| #536            | Category: Big Data & Streaming                       | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------- | :-------------- |
| **Depends on:** | Apache Spark, MapReduce                              |                 |
| **Used by:**    | Spark DataFrame, Spark Streaming, MLlib              |                 |
| **Related:**    | Apache Spark, Spark DataFrame, Distributed Computing |                 |

---

### 🔥 The Problem This Solves

**FAULT-TOLERANT IN-MEMORY DISTRIBUTED DATA WITHOUT REPLICATION OVERHEAD:**
In a cluster of 1,000 executors, node failures happen regularly. Replicating all in-memory data 3× wastes 66% of memory. RDD solves this with **lineage**: record WHAT transformations produced each RDD (e.g., "RDD C = RDD B.filter(x>0); RDD B = RDD A.map(parse)"). If partition 42 of RDD C is lost: recompute only that partition by replaying the lineage: re-read partition 42 from source → apply map(parse) → apply filter(x>0). No replication needed — lineage is the fault tolerance mechanism.

---

### 📘 Textbook Definition

**RDD (Resilient Distributed Dataset)** is Spark's core data abstraction:

- **Resilient**: fault-tolerant via lineage (can recompute lost partitions from parent RDDs).
- **Distributed**: partitioned across multiple executors in the cluster; each partition is an independent unit of work.
- **Dataset**: a collection of data records (tuples, objects, key-value pairs).

An RDD has five properties:

1. **List of partitions**: how data is divided.
2. **Compute function**: how to compute each partition from parent partitions.
3. **List of dependencies**: parent RDDs (narrow: one parent partition per child partition; wide: multiple parent partitions per child).
4. **Partitioner** (optional): for key-value RDDs — how keys map to partitions (hash or range).
5. **Preferred locations** (optional): for data locality (which nodes have the data).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
RDD = immutable distributed collection, partitioned across cluster, resilient via recorded lineage — if a partition is lost, replay its transformation history to recompute it.

**One analogy:**

> An RDD is like a spreadsheet formula chain. Cell E1 = SUM(D1:D10). D1 = C1 _ 2. C1 = A1 + B1. If someone accidentally deletes D1, Excel can recompute it: D1 = C1 _ 2 = (A1 + B1) \* 2. The **formula chain (lineage)** is the backup — not a copy of D1's value. RDDs work the same way: the DAG of transformations (lineage) is stored, not copies of the data. Lose a partition → replay the lineage → recompute the partition.

**One insight:**
RDDs have two types of dependencies, and this distinction determines whether Spark can recover efficiently:

- **Narrow dependency**: each child partition depends on exactly one parent partition (e.g., `map`, `filter`). To recover lost child partition: re-read one parent partition — fast and local.
- **Wide dependency**: each child partition depends on ALL parent partitions (e.g., `groupByKey`, `sortByKey` — requires shuffle). To recover one child partition: re-read and re-process ALL parent partitions. This is expensive — checkpointing before wide dependencies avoids this.

---

### 🔩 First Principles Explanation

**CREATING AND TRANSFORMING RDDS:**

```python
from pyspark import SparkContext, SparkConf

conf = SparkConf().setAppName("RDDDemo").setMaster("yarn")
sc = SparkContext(conf=conf)  # entry point for RDD API

# 1. Creating RDDs:

# From file (HDFS or S3):
lines = sc.textFile("hdfs:///data/weblogs/*.log", minPartitions=200)
# lines: RDD[String], one record per line

# From collection (small data, for testing):
data = sc.parallelize([1, 2, 3, 4, 5], numSlices=4)
# data: RDD[Int], 4 partitions

# From in-memory collection:
kv = sc.parallelize([("a", 1), ("b", 2), ("a", 3)])

# 2. Narrow transformations (each output partition ← one input partition):
# No shuffle — fast, pipelined in same Stage
errors = lines.filter(lambda line: "ERROR" in line)
words = errors.flatMap(lambda line: line.split(" "))
word_pairs = words.map(lambda w: (w, 1))
# All 3 transformations pipelined: same Stage, no network transfer

# 3. Wide transformations (each output partition ← ALL input partitions):
# Requires shuffle — Stage boundary
word_counts = word_pairs.reduceByKey(lambda a, b: a + b)
# ← shuffle: all ("ERROR", ...) pairs routed to same partition

sorted_counts = word_counts.sortBy(lambda kv: kv[1], ascending=False)
# ← shuffle: global sort requires repartitioning

# 4. Actions (trigger execution):
top_10 = sorted_counts.take(10)    # returns 10 records to driver
total = word_pairs.count()          # returns count to driver
word_counts.saveAsTextFile("hdfs:///output/word-counts/")  # writes to HDFS
```

**LINEAGE AND FAULT TOLERANCE:**

```python
# RDD lineage example:
raw = sc.textFile("s3://bucket/raw-logs/")           # RDD A: 200 partitions
parsed = raw.map(parse_log_line)                      # RDD B = map(A)
filtered = parsed.filter(lambda r: r.status == 500)  # RDD C = filter(B)
keyed = filtered.map(lambda r: (r.path, 1))           # RDD D = map(C)
counts = keyed.reduceByKey(lambda a, b: a + b)        # RDD E = reduceByKey(D)
# ↑ This creates a SHUFFLE (wide dependency)

# Lineage DAG for RDD E, partition 5:
# E[5] ← shuffle of D[0..199] → D = map(C) = filter(B) = map(A)
# Full lineage: A[*] → B[*] → C[*] → D[*] → E[5]

# If partition 5 of RDD E fails during computation:
# Narrow deps (A→B→C→D): recompute ONLY partition 5 of each
#   A[5] → map → B[5] → filter → C[5] → map → D[5] (fast, local)
# Wide dep (D→E, shuffle): need D[0..199] to regenerate E[5]
#   Must recompute ALL partitions of D (can be expensive!)

# SOLUTION: checkpoint before expensive re-computation
counts.checkpoint()  # writes RDD E to HDFS, truncates lineage to here
# Now if any partition of counts fails: reread from HDFS checkpoint
# (not recompute from raw S3 data through the entire DAG)

sc.setCheckpointDir("hdfs:///spark-checkpoints/")
```

**PARTITIONER — CONTROLLING DATA DISTRIBUTION:**

```python
# HashPartitioner (default for key-value RDDs after shuffle):
# partition = hash(key) % numPartitions
# All values for same key → same partition (required for groupByKey, join)

# RangePartitioner: used by sortByKey for ordered data
# Samples data to determine key ranges → even distribution

# Custom partitioner: route related keys to same partition
from pyspark import Partitioner

class UserPartitioner(Partitioner):
    def __init__(self, partitions):
        super().__init__()
        self.num_partitions = partitions

    def numPartitions(self):
        return self.num_partitions

    def getPartition(self, key):
        # Route all keys for the same user region to same partition
        # key = (user_id, region)
        region = key[1]
        region_map = {"US": 0, "EU": 1, "APAC": 2}
        return region_map.get(region, self.num_partitions - 1)

rdd = sc.parallelize([((123, "US"), "order"), ((456, "EU"), "order")])
custom_partitioned = rdd.partitionBy(3, UserPartitioner(3))
# All US users → partition 0, EU → partition 1, APAC → partition 2

# This is useful for co-location: if two RDDs have same partitioner,
# joining them requires NO shuffle (each partition of A joins with
# corresponding partition of B locally)
```

**NARROW vs WIDE DEPENDENCIES:**

```
NARROW dependencies (1 parent partition → 1 child partition):
  map, filter, flatMap, mapPartitions, union

  Parent RDD:  [P0] [P1] [P2] [P3]
                ↓    ↓    ↓    ↓        (1:1 mapping)
  Child RDD:  [P0] [P1] [P2] [P3]

  Recovery: lose child P2 → recompute only from parent P2 (fast)

WIDE dependencies (all parent partitions → 1 child partition):
  groupByKey, reduceByKey, sortByKey, join (without co-partitioning)

  Parent RDD:  [P0] [P1] [P2] [P3]
                \  X  X  X  /      (all-to-all, shuffle)
  Child RDD:  [P0] [P1] [P2] [P3]

  Recovery: lose child P2 → need to recompute/re-read ALL parent partitions
  Spark materializes shuffle output to disk (so Reducers can re-read on failure)
```

---

### 🧪 Thought Experiment

**WHEN TO USE RDD vs DATAFRAME:**

Scenario: You have JSON log data with 50+ nested fields. You only need 3 fields. You want to filter, group, and count.

- **DataFrame/Spark SQL**: Catalyst optimizer applies predicate pushdown (filters pushed to read time) and projection pruning (only reads needed columns from Parquet). Result: reads only 3/50 columns, filters before deserialization. Catalyst may also choose a broadcast join or sort-merge join automatically.

- **RDD with map/filter**: reads all 50 fields (no projection pruning), filters after full deserialization. No Catalyst optimization. Much slower for Parquet sources.

**Use RDD when**: (1) your data isn't tabular (custom complex objects), (2) you need custom partitioners, (3) you need Python UDFs that Catalyst can't optimize, (4) working with unstructured binary data. For everything else: DataFrame/Dataset.

---

### 🧠 Mental Model / Analogy

> An RDD is like a recipe card and its ingredients. The RDD itself isn't the cake (data) — it's the **instruction for making the cake**: "Take flour from storage shelf A, mix with eggs from shelf B, bake for 30 minutes." If the cake burns (partition lost), you don't need a backup cake — you have the recipe (lineage) and can remake it. Wide transformations are like recipes requiring ingredients from multiple kitchens (shuffle) — if the finished dish is lost, you need to redo ALL kitchen preparations. Pre-baked intermediate results (checkpoint) prevent this.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** RDD = distributed collection, split into partitions across executors. Transformations are lazy (build a plan), actions execute. Fault tolerance via lineage (recompute lost partitions). Largely replaced by DataFrames for performance.

**Level 2:** Narrow dependencies (1:1 partition mapping, no shuffle) vs. wide dependencies (all-to-all, shuffle = stage boundary). `reduceByKey` > `groupByKey`: pre-aggregates locally, reduces network. Checkpoint before wide deps with long lineages.

**Level 3:** RDD lineage = the DAG of transformations. Each RDD stores references to parent RDDs and the function to compute it. Driver reconstructs the full lineage graph. Wide dependencies materialize shuffle output to disk (enabling re-read without re-running the full lineage). Custom partitioners enable co-partitioning → joins without shuffle.

**Level 4:** DataFrames are built on top of RDDs internally. `df.rdd` converts a DataFrame back to an `RDD[Row]`. The Catalyst optimizer generates optimized physical plans that compile to RDD operations via code generation (Tungsten). For Python DataFrames, PySpark serializes the plan from Python → JVM → Spark executes in JVM → results back to Python. Custom Python UDFs break out of the JVM optimization loop and execute in a Python subprocess (slow). Pandas UDFs (PyArrow-based vectorized UDFs) are much faster than row-at-a-time Python UDFs because they work on Arrow batches rather than individual rows.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ RDD LINEAGE DAG                                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Source RDD (textFile) — partition per HDFS block   │
│       ↓ map (narrow) — pipelined, same stage        │
│  RDD B (parsed)                                      │
│       ↓ filter (narrow) — pipelined                 │
│  RDD C (filtered)                                    │
│  ══════════════════ SHUFFLE BOUNDARY ═══════════════ │
│       ↓ reduceByKey (wide) — Stage 2 starts         │
│  [RDD E — YOU ARE HERE: shuffle output, aggregated] │
│       ↓ map (narrow)                                 │
│  RDD F (final result) → saveAsTextFile → HDFS       │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Job: count 500-errors per URL from 10TB access logs

1. sc.textFile("s3://...") → RDD A (10TB / 128MB = ~80,000 partitions)
2. .filter("HTTP 500") → RDD B (narrow, ~1% → 100GB)
3. .map(extract_url_pair) → RDD C = [(url, 1), ...] (narrow)
   Stage 1: reads S3, applies filter+map in single pass, 80K parallel tasks

4. .reduceByKey(+) → RDD D (wide → shuffle)
   Stage 1 complete: 80K tasks write shuffle files (partitioned by hash(url))
   Stage 2: 200 tasks (default spark.sql.shuffle.partitions)
   Each task: reads shuffle files for its key range → sums counts

5. .sortBy(lambda kv: -kv[1]) → RDD E (wide → sort shuffle)
   Stage 3: sort requires another shuffle

6. .take(100) → [("api/checkout", 15000), ("api/login", 8000), ...]
   Driver receives 100 records from Stage 3 executors
```

---

### ⚖️ Comparison Table

| Feature      | RDD                                    | DataFrame/Dataset                            |
| ------------ | -------------------------------------- | -------------------------------------------- |
| API          | Low-level, functional                  | High-level, declarative                      |
| Optimization | Manual (developer responsibility)      | Automatic (Catalyst + Tungsten)              |
| Type safety  | Python: none; Scala: typed             | Scala Dataset: compile-time; Python: runtime |
| Performance  | Baseline                               | 5-10× faster (code generation)               |
| Best for     | Custom partitioning, unstructured data | SQL analytics, structured data               |
| Python UDF   | Row-at-a-time (slow)                   | Pandas UDF (vectorized, fast)                |

---

### ⚠️ Common Misconceptions

| Misconception                              | Reality                                                                                                                                                                                                   |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "RDD is deprecated"                        | RDD is Spark's core. DataFrames compile to RDDs. RDD API is available and supported; just rarely the best choice for tabular data                                                                         |
| "Caching an RDD eliminates re-computation" | Cache helps for MULTIPLE actions on the same RDD. For a single action, caching adds overhead. Cache when you use the same RDD in multiple downstream operations                                           |
| "Checkpointing is the same as caching"     | Cache stores RDD in executor memory (temporary, lost on failure). Checkpoint writes to HDFS (persistent, truncates lineage). Checkpoint is for fault tolerance on long lineages; cache is for performance |

---

### 🚨 Failure Modes & Diagnosis

**1. Long Lineage Without Checkpoint — Expensive Re-computation**

**Symptom:** Spark job runs fine normally, but when an executor fails mid-job, the recovery takes much longer than expected — seemingly re-running the entire job from the start.

**Root Cause:** RDD has a deep lineage (100+ transformations, reading from S3). Wide dependency at shuffle step means recovering one partition requires re-reading all parent data.

**Fix:** Add `checkpoint()` after expensive transformations:

```python
sc.setCheckpointDir("hdfs:///spark-checkpoints/")
after_expensive_join = rdd_a.join(rdd_b)  # expensive shuffle
after_expensive_join.checkpoint()  # write to HDFS, truncate lineage
result = after_expensive_join.map(...)   # now lineage starts from HDFS checkpoint
```

---

### 🔗 Related Keywords

**Prerequisites:** Apache Spark, MapReduce
**Builds On This:** Spark DataFrame, Spark Streaming, MLlib
**Related:** Apache Spark, Spark DataFrame, Distributed Computing

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ RESILIENT   │ Lineage-based fault tolerance (no replication)│
│ PARTITIONS  │ Units of parallelism, one task per partition │
│ NARROW DEP  │ 1:1 parent partition (map, filter — fast)   │
│ WIDE DEP    │ N:1 parent partitions (shuffle — expensive) │
│ LINEAGE     │ DAG of transformations recorded by Spark    │
│ CHECKPOINT  │ Write to HDFS; truncate long lineages       │
│ RDD vs DF   │ DF: Catalyst optimizer → 5-10× faster      │
│ reduceByKey │ Pre-aggregate locally >> groupByKey         │
│ USE CASE    │ Custom partitioners, non-tabular data       │
│ ONE-LINER   │ "Immutable distributed collection; lineage  │
│             │  = fault tolerance without replication"     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) Explain the difference between narrow and wide RDD dependencies. How does Spark's fault tolerance model differ between these two types? When would you use `checkpoint()`?

**Q2.** (TYPE C — Architecture) You are building a Spark pipeline that: (1) joins two large datasets (10TB × 500GB), (2) applies 50 transformations, (3) runs hourly in production. What strategies do you use to make this fault-tolerant and performant? Consider: partitioner, checkpoint, broadcast join, caching.
