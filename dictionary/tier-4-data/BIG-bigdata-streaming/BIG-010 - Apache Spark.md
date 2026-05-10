---
version: 2
layout: default
title: "Apache Spark"
parent: "Big Data & Streaming"
grand_parent: "Technical Dictionary"
nav_order: 10
permalink: /big-data-streaming/apache-spark/
id: BIG-010
category: Big Data & Streaming
difficulty: ★★★
depends_on: MapReduce, Apache Hadoop, Distributed Computing
used_by: Spark RDD, Spark Streaming, Data Engineering
related: Spark RDD, Spark DataFrame, Spark Streaming
tags:
  - apache-spark
  - distributed-computing
  - in-memory
  - big-data
  - deep-dive
---

# BIG-010 - Apache Spark

⚡ TL;DR - Apache Spark is a **unified analytics engine** for large-scale data processing with **in-memory computation** - processes data 10-100× faster than Hadoop MapReduce by keeping intermediate results in RAM rather than writing to disk; provides unified APIs for **batch** (RDD/DataFrame), **SQL** (Spark SQL), **streaming** (Spark Streaming/Structured Streaming), and **ML** (MLlib) - runs on YARN, Kubernetes, or standalone, and reads from HDFS, S3, databases, and Kafka.

| #535            | Category: Big Data & Streaming                  | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------- | :-------------- |
| **Depends on:** | MapReduce, Apache Hadoop, Distributed Computing |                 |
| **Used by:**    | Spark RDD, Spark Streaming, Data Engineering    |                 |
| **Related:**    | Spark RDD, Spark DataFrame, Spark Streaming     |                 |

---

### 🔥 The Problem This Solves

**ITERATIVE ALGORITHMS AND MULTI-STEP PIPELINES - SLOW ON DISK:**
Hadoop MapReduce writes intermediate results to HDFS between every job step. A machine learning algorithm requiring 100 iterations of gradient descent = 100 MapReduce jobs = 100 HDFS reads + 100 HDFS writes = slow. Spark keeps intermediate data in RAM across all iterations: read data once → 100 in-memory passes → write result once. For PageRank (requires ~50 iterations): Hadoop = hours; Spark = minutes. Spark's DAG engine also eliminates the Map→Shuffle→Reduce restriction, allowing arbitrary computation graphs.

---

### 📘 Textbook Definition

**Apache Spark** is a distributed data processing engine with these abstractions:

- **RDD (Resilient Distributed Dataset)**: the foundational abstraction. An immutable, partitioned collection of records distributed across the cluster. Supports **transformations** (lazy: `map`, `filter`, `groupByKey`, `join`) and **actions** (eager: `count`, `collect`, `saveAsTextFile`).
- **DataFrame/Dataset**: higher-level abstraction with schema. Optimized by **Catalyst** query optimizer and **Tungsten** execution engine (code generation, off-heap memory management). ~10× faster than RDD for SQL-like operations.
- **SparkSession**: entry point. Replaces `SparkContext`, `HiveContext`, `SQLContext`.
- **DAG Scheduler**: converts logical operation graph into physical stages of tasks. Pipelined operations within a stage avoid intermediate shuffles.
- **Shuffle**: when data must be repartitioned (e.g., `groupByKey`, `join`) - involves network transfer. Most expensive operation; minimize shuffles for performance.
- **Lazy evaluation**: transformations build a logical plan; actions trigger execution. Allows Catalyst to optimize before running.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Spark = distributed in-memory data processing with a DAG engine - 10-100× faster than Hadoop MapReduce, supporting batch, SQL, streaming, and ML with a unified API.

**One analogy:**

> MapReduce is like cooking a 10-course meal one course at a time, washing all dishes between courses (disk I/O between each step). Spark is like a modern restaurant kitchen: all courses prepared in parallel using shared counter space (RAM), minimal cleanup between courses. The end result is the same meal, but Spark delivers it 10× faster and the chef (developer) writes much simpler recipes (DataFrame/Spark SQL API vs. verbose Mapper/Reducer classes).

**One insight:**
Spark's most powerful optimization is **pipelining**: consecutive `map` transformations don't create intermediate files - they're pipelined in a single pass through data within one stage. Only **shuffle boundaries** (operations requiring all data for a key to be on the same node: `groupByKey`, `join`, `sortBy`) create stage boundaries with network transfer. Minimizing shuffle operations is the most impactful Spark performance optimization.

---

### 🔩 First Principles Explanation

**SPARK ARCHITECTURE:**

```
Spark Cluster (YARN mode):
  [Driver Program]                              ← your main() runs here
    SparkSession (DAG Scheduler + Task Scheduler)
       │
       │ submits tasks to
       ↓
  [Cluster Manager] (YARN ResourceManager or Kubernetes)
       │
       │ allocates executors on
       ↓
  [Executor 1] [Executor 2] ... [Executor 100]  ← workers
    JVM process on each node
    Multiple cores → multiple threads → parallel task execution
    In-memory storage for cached RDDs/DataFrames

  Data flow:
  Driver → reads metadata from HDFS/NameNode
  Executor → reads data partitions from HDFS DataNodes or S3
  Executors → shuffle data directly between themselves (no driver in data path)
  Driver → receives final results from actions (collect, count)
```

**LAZY EVALUATION + DAG:**

```python
# PySpark example
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("LogAnalysis") \
    .master("yarn") \
    .config("spark.executor.memory", "8g") \
    .config("spark.executor.cores", "4") \
    .config("spark.sql.shuffle.partitions", "200") \
    .getOrCreate()

# All of these are TRANSFORMATIONS (lazy - nothing executes yet):
df = spark.read.parquet("s3://bucket/logs/2024/")  # lazy: just reads metadata
errors = df.filter(df.level == "ERROR")             # lazy: logical plan grows
by_service = errors.groupBy("service")              # lazy: plan grows (shuffle boundary!)
counts = by_service.count()                         # lazy: plan grows

# ACTION: this triggers actual execution:
counts.show(20)  # ← execution starts HERE

# Spark internal execution plan:
# Stage 1: read parquet + filter level==ERROR (pipelined, no shuffle)
#   Task 1 (partition 0): read 128MB → filter → partial counts
#   Task 2 (partition 1): read 128MB → filter → partial counts
#   ...200 tasks in parallel...
#
# SHUFFLE: hash partition partial counts by service (network transfer)
#
# Stage 2: aggregate counts per service (reduce side)
#   Task 1: sum counts for service=auth
#   Task 2: sum counts for service=payment
#   ...

# Optimization: use show() / take() to avoid collect() on huge datasets
# collect() pulls ALL data to driver → driver OOM if data > driver memory
```

**KEY TRANSFORMATION TYPES:**

```python
# NARROW transformations: each output partition depends on ONE input partition
# No shuffle - pipelined within a stage:
rdd.map(lambda x: x.split(","))     # transform each record
rdd.filter(lambda x: x[2] == "US")  # keep matching records
rdd.flatMap(lambda x: x.split(" ")) # 1 record → 0-N records

# WIDE transformations: output partition depends on MULTIPLE input partitions
# Require shuffle (= stage boundary):
rdd.groupByKey()    # all values for each key → same partition (NETWORK)
rdd.reduceByKey(lambda a, b: a+b)  # like groupByKey but pre-aggregates locally (better!)
rdd.sortBy(lambda x: x[1])        # global sort requires redistribution
df.join(other_df, "key")           # shuffle both sides by join key

# PERFORMANCE RULE: reduceByKey vs groupByKey
# groupByKey: shuffles ALL values across network, then aggregates
#   (k, [v1, v2, v3, v4, v5...]) - all values move over network
# reduceByKey: locally pre-aggregates first (like Combiner in MapReduce)
#   then shuffles partial results - MUCH less network traffic for aggregation

# Example: word count
# BAD: groupByKey → lots of network transfer
word_counts = rdd.map(lambda w: (w, 1)) \
                 .groupByKey() \
                 .mapValues(sum)  # sum happens AFTER network transfer

# GOOD: reduceByKey → locally pre-aggregate first
word_counts = rdd.map(lambda w: (w, 1)) \
                 .reduceByKey(lambda a, b: a + b)  # pre-aggregate then shuffle
```

**CACHING:**

```python
# Caching: keep DataFrame/RDD in memory across multiple actions
# Without cache: each action re-reads from disk and re-processes

# BAD: reads parquet file twice (for train and validation split)
df = spark.read.parquet("s3://bucket/training_data/")
train = df.filter(df.date < "2024-01-01").count()  # reads all of S3 once
val = df.filter(df.date >= "2024-01-01").count()   # reads all of S3 AGAIN

# GOOD: cache the source DataFrame
df = spark.read.parquet("s3://bucket/training_data/")
df.cache()   # or df.persist(StorageLevel.MEMORY_AND_DISK)
# On first action: data loaded from S3 into executor memory
train = df.filter(df.date < "2024-01-01").count()  # caches to memory
val = df.filter(df.date >= "2024-01-01").count()   # reads from memory (fast)
df.unpersist()  # release memory when done

# StorageLevel options:
# MEMORY_ONLY: fastest, but data lost if executor OOM → recomputed from source
# MEMORY_AND_DISK: spill to disk if OOM (slower but safe)
# DISK_ONLY: for checkpointing fault tolerance
# MEMORY_AND_DISK_SER: serialized (less memory, more CPU)
```

---

### 🧪 Thought Experiment

**DATA SKEW - THE SILENT KILLER:**

A `groupByKey` on user_id. Power-law distribution: top 1% of users have 90% of the records. The reducer handling top-user keys takes 100× longer than others.

Symptoms: Job is 99% complete, one task has been running for 3 hours while all others finished in 10 minutes.

Diagnosis: Spark UI → Stage detail → Task metrics → find the single task that's running much longer. Look at the data it's processing.

Fix options:

1. **Salting**: add random prefix to hot keys: `(user_123, v1)` → `(user_123_shard0, v1), (user_123_shard1, v2)` across N reducers → then a second reduce pass to merge shard results.
2. **Adaptive Query Execution (AQE)**: Spark 3.0+ feature. Automatically splits skewed partitions at runtime using actual data statistics collected during shuffle. Enable: `spark.sql.adaptive.enabled=true`, `spark.sql.adaptive.skewJoin.enabled=true`.
3. **Broadcast join**: if one side of join is small (< `spark.sql.autoBroadcastJoinThreshold`, default 10MB), broadcast it to all executors - no shuffle at all.

---

### 🧠 Mental Model / Analogy

> Spark is like a modern supply chain system. The **Driver** is the supply chain manager who plans all operations (DAG planning). **Executors** are workers in multiple warehouses who process shipments in parallel. **Shuffle** is when goods need to be redistributed between warehouses by category - expensive (needs trucks/network). **Caching** is keeping frequently-needed inventory on local shelves (RAM) instead of fetching from the main depot (disk/S3) every time. The key to efficiency: **minimize redistribution** (shuffle) and **keep hot items on local shelves** (cache wisely).

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Spark = in-memory distributed processing, 10-100× faster than Hadoop MapReduce. DataFrames with SQL-like API. Supports batch, streaming, and ML.

**Level 2:** Lazy evaluation: transformations build a plan; actions execute it. Narrow transformations (map, filter) are pipelined in one stage - no shuffle. Wide transformations (groupBy, join) require shuffle = network transfer = stage boundary. `reduceByKey` >> `groupByKey` for aggregation (pre-aggregates locally).

**Level 3:** Catalyst optimizer: logical plan → analyzed plan → optimized plan (predicate pushdown, projection pruning) → physical plans → best plan via cost model. Tungsten: binary in-memory format (off-heap), code generation (compiles operations to JVM bytecode at runtime). Together: DataFrame operations run near C++ speed on JVM.

**Level 4:** Spark's fault tolerance is based on RDD lineage: if a partition is lost (executor failure), Spark re-computes it from its parent RDD using the recorded transformation. This is **lineage-based fault tolerance** - no replication needed. But for long lineages (100+ transformations), re-computation from scratch is expensive. Solution: `checkpoint()` - writes RDD to HDFS, truncates lineage. Structured Streaming: micro-batch execution over write-ahead log; exact-once semantics via Kafka offset tracking + transactional file writes to Delta Lake/Parquet. Adaptive Query Execution (AQE, Spark 3.0+): re-optimizes the plan at runtime using actual shuffle statistics - automatically handles skew, coalesces small partitions.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ SPARK EXECUTION MODEL                                │
├──────────────────────────────────────────────────────┤
│                                                      │
│  [Driver: DAG Scheduler]                             │
│  Logical Plan → Optimized Plan → Physical Plan      │
│       Stage 1 [tasks] → Stage 2 [tasks] → Stage 3  │
│                              ↕ shuffle                │
│  [SPARK ← YOU ARE HERE: in-memory DAG engine]        │
│                                                      │
│  [Executor 1]  [Executor 2]  [Executor 3]            │
│  JVM + tasks   JVM + tasks   JVM + tasks             │
│  cached RDDs   cached RDDs   cached RDDs             │
│       ↕ shuffle data via network (stage boundary)    │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Spark job: analyze 10TB of e-commerce logs

spark-submit --master yarn \
  --num-executors 200 \
  --executor-memory 8g \
  --executor-cores 4 \
  --class AnalyzeOrders \
  orders-analysis.jar

Stage 1 (200 tasks, 50GB/200 = 256MB per partition, NARROW ops, no shuffle):
  Each task: read parquet from S3 → filter status=='completed' → select(user_id, amount)
  200 tasks run in parallel on 200 executor cores
  Zero shuffle within Stage 1 (all narrow transforms)

Stage 2 (200 tasks, WIDE op: groupBy user_id - shuffle boundary):
  All 200 tasks from Stage 1 write shuffle files partitioned by hash(user_id)
  Network transfer: ~1TB of intermediate data redistributed across executors
  Each Stage 2 task receives all records for its set of user_ids
  Aggregates: sum(amount) per user_id

Output: write 200 Parquet files to S3://results/user-revenue/

Total time: ~5 minutes (vs 60+ minutes in MapReduce)
Driver monitoring: SparkUI at http://driver:4040 (Stages, Tasks, Shuffle Reads/Writes)
```

---

### ⚖️ Comparison Table

| Feature          | Apache Spark                       | Hadoop MapReduce      | Apache Flink                |
| ---------------- | ---------------------------------- | --------------------- | --------------------------- |
| Execution        | In-memory DAG                      | Disk-based Map→Reduce | In-memory streaming DAG     |
| Speed            | 10-100× faster than MR             | Baseline              | Similar to Spark            |
| Streaming        | Micro-batch (100ms-1s latency)     | No                    | True streaming (ms latency) |
| SQL              | Spark SQL (fast, Catalyst)         | Hive (slow)           | Flink SQL                   |
| ML               | MLlib                              | Mahout (legacy)       | Flink ML                    |
| State management | Limited (accumulators, broadcasts) | None                  | Rich (RocksDB backend)      |
| Best for         | Batch analytics, ETL, ML           | Legacy pipelines      | Real-time stream processing |

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                                                                                                                                                                                        |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Spark always uses memory - OOM is common"     | Spark spills to disk automatically when memory is insufficient (with `MEMORY_AND_DISK` persistence). Modern Spark (3.x) with AQE is much better at avoiding OOM through dynamic partition coalescing and skew handling                                         |
| "More partitions = more parallelism = faster"  | Optimal: partitions ≈ 2-4× the number of CPU cores. Too many partitions → scheduling overhead and tiny tasks. Too few → uneven load distribution. Rule: 128-256MB per partition is a good starting point                                                       |
| "DataFrame and RDD performance are equivalent" | DataFrame/Dataset operations are significantly faster than equivalent RDD operations due to Catalyst optimizer (query planning) and Tungsten execution engine (code generation, off-heap memory). Use DataFrame/Spark SQL unless you need fine-grained control |

---

### 🚨 Failure Modes & Diagnosis

**1. Executor OOM - Java Heap Space**

**Symptom:** `java.lang.OutOfMemoryError: Java heap space` on executors. Job fails and retries, then fails again.

**Root Cause:** Either data skew (one partition has vastly more data than others) or insufficient executor memory for the data being processed.

**Diagnosis:** Spark UI → Stages → find the failed task → check its input size vs. other tasks. If one task has 100GB input and others have 100MB: data skew. If all tasks fail: insufficient memory.

**Fix for skew:** Enable AQE (`spark.sql.adaptive.skewJoin.enabled=true`). Fix for insufficient memory: increase `--executor-memory` or increase `--num-executors` to reduce data per task.

---

### 🔗 Related Keywords

**Prerequisites:** MapReduce, Apache Hadoop, Distributed Computing
**Builds On This:** Spark RDD, Spark DataFrame, Spark Streaming
**Related:** Spark RDD, Spark DataFrame, Spark Streaming

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ SPEED        │ 10-100× faster than MapReduce (in-memory)│
│ LAZY EVAL    │ Transformations → plan; Actions → execute │
│ SHUFFLE      │ Wide transforms (groupBy, join) = costly  │
│ reduceByKey  │ Pre-aggregates locally (>> groupByKey)    │
│ CATALYST     │ Optimizer: predicate pushdown, pruning    │
│ TUNGSTEN     │ Code generation, off-heap memory          │
│ AQE          │ Spark 3+: runtime plan re-optimization    │
│ CACHE        │ .cache() for multi-use DataFrames         │
│ PARTITION    │ ~128-256MB per partition, 2-4× cores      │
│ ONE-LINER    │ "In-memory DAG engine: batch+SQL+stream  │
│              │  in one API, 100× faster than MapReduce"  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) Explain Spark's lazy evaluation model. What is the difference between a transformation and an action? Give three examples of each. Why does lazy evaluation enable better optimization?

**Q2.** (TYPE C - Performance) A Spark job processing 500GB of data completes Stage 1 (200 tasks) in 3 minutes, but Stage 2 (groupByKey + count) takes 2 hours with 1 task still running after all others complete. Diagnose the problem and propose two different solutions.
