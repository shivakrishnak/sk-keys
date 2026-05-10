---
version: 2
layout: default
title: "Spark DataFrame  Dataset"
parent: "Big Data & Streaming"
grand_parent: "Technical Dictionary"
nav_order: 12
permalink: /big-data-streaming/spark-dataframe-dataset/
id: BIG-012
category: Big Data & Streaming
difficulty: ★★★
depends_on: Spark RDD, Apache Spark
used_by: Spark SQL, Spark Streaming, MLlib
related: Spark RDD, Spark SQL, Spark Streaming
tags:
  - spark-dataframe
  - spark-dataset
  - catalyst-optimizer
  - tungsten
  - deep-dive
---

# BIG-012 - Spark DataFrame  Dataset

⚡ TL;DR - Spark **DataFrame** is a distributed collection of **schema-aware rows** (like a SQL table in memory), and **Dataset** adds compile-time type safety (Scala/Java only); both are powered by the **Catalyst query optimizer** (transforms logical plans to optimized physical plans - predicate pushdown, projection pruning, join reordering) and **Tungsten execution engine** (binary in-memory layout, code generation) - resulting in **5-10× faster execution** than equivalent RDD operations.

| #537            | Category: Big Data & Streaming        | Difficulty: ★★★ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | Spark RDD, Apache Spark               |                 |
| **Used by:**    | Spark SQL, Spark Streaming, MLlib     |                 |
| **Related:**    | Spark RDD, Spark SQL, Spark Streaming |                 |

---

### 🔥 The Problem This Solves

**UNOPTIMIZED RDD CODE - SLOW AND VERBOSE:**
An RDD word count requires 5-10 lines of Scala/Python. Spark has no way to optimize it - it runs the user's functions as black boxes. A DataFrame equivalent using `groupBy().count()` tells Catalyst: "group these rows by this column and count." Catalyst can now optimize: push filters down to scan time (read less data), prune unused columns, choose optimal join strategies, and generate efficient JVM bytecode. The result: 5-10× faster with less code, and identical behavior across Python, Scala, and Java.

---

### 📘 Textbook Definition

**DataFrame**: a `Dataset[Row]` - a distributed table with named columns and a schema. Schema is known at compile time (Scala/Java) or inferred/declared at runtime (Python). API: SQL-like operations (`select`, `filter`, `groupBy`, `join`, `agg`). Catalyst can inspect and optimize the schema-aware operations.

**Dataset**: `Dataset[T]` where T is a typed JVM class (case class in Scala). Combines RDD's type safety with DataFrame's Catalyst optimization. Available in Scala and Java only (Python has no compile-time types). `Dataset[Row]` = DataFrame.

**Catalyst Optimizer** pipeline:

1. **Unresolved Logical Plan** (parsed SQL or DataFrame operations)
2. **Analyzed Logical Plan** (column names resolved against schema)
3. **Optimized Logical Plan** (rules applied: predicate pushdown, constant folding, etc.)
4. **Physical Plans** (multiple candidate execution strategies)
5. **Cost Model** selects best physical plan
6. **Code Generation** (Tungsten: compiles to JVM bytecode)

---

### ⏱️ Understand It in 30 Seconds

**One line:**
DataFrame = schema-aware distributed table + Catalyst optimizer (10+ optimization rules applied automatically) + Tungsten code generation = 5-10× faster than RDD with SQL-like API.

**One analogy:**

> An RDD is telling a chef (Spark): "Do exactly these steps in this order: 1. chop carrots, 2. boil water, 3. add carrots, 4. add salt..." (no flexibility for the chef to optimize). A DataFrame is telling the chef: "I want carrot soup" - the chef (Catalyst) decides the most efficient way to make it: maybe pre-chill the bowl while chopping, use a faster knife for large carrots, combine prep steps - all optimizations invisible to you but dramatically faster.

**One insight:**
Catalyst's most impactful optimization is **predicate pushdown**: if you filter `date > 2024-01-01` on a Parquet table partitioned by date, Catalyst pushes this filter to the file scan layer - Spark reads ONLY partitions matching that date, skipping all others. Without this: Spark reads all data and then filters. With Parquet column pruning: Spark reads only the columns you `select`, not all columns. For a 100-column table where you select 3 columns: 97% less data read.

---

### 🔩 First Principles Explanation

**DATAFRAME API - CREATING AND USING:**

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType

spark = SparkSession.builder \
    .appName("DataFrameDemo") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.skewJoin.enabled", "true") \
    .getOrCreate()

# 1. Creating DataFrames from various sources:

# From Parquet (most common for big data):
orders = spark.read \
    .parquet("s3://warehouse/orders/")
    # Catalyst: reads only needed columns (projection pushdown)
    # Parquet predicate pushdown: skip row groups not matching filters

# From JSON:
logs = spark.read.json("hdfs:///logs/2024/")

# From CSV with schema (always specify schema - avoids full scan for inference):
schema = StructType([
    StructField("order_id", StringType(), nullable=False),
    StructField("user_id", IntegerType(), nullable=True),
    StructField("amount", IntegerType(), nullable=True),
    StructField("status", StringType(), nullable=True)
])
orders_csv = spark.read.schema(schema).csv("s3://raw/orders.csv")

# From JDBC (relational DB):
jdbc_df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://db-host:5432/mydb") \
    .option("dbtable", "orders") \
    .option("user", "spark") \
    .option("password", "secret") \
    .option("numPartitions", "50") \
    .option("partitionColumn", "order_id") \
    .option("lowerBound", "1") \
    .option("upperBound", "10000000") \
    .load()

# 2. Transformations (all lazy):
result = orders \
    .filter(F.col("status") == "completed") \      # predicate pushdown to scan
    .filter(F.col("amount") > 100) \               # combined with above
    .select("user_id", "amount", "order_date") \   # projection pushdown (3 cols only)
    .withColumn("year", F.year("order_date")) \    # derived column
    .groupBy("user_id", "year") \                  # wide: shuffle boundary
    .agg(
        F.sum("amount").alias("total_spent"),
        F.count("*").alias("order_count"),
        F.avg("amount").alias("avg_amount")
    ) \
    .orderBy(F.desc("total_spent")) \              # wide: global sort
    .limit(1000)

# 3. Actions (trigger execution):
result.show(20)                                    # print to console
result.write.parquet("s3://output/user-spending/")  # write to storage

# 4. Spark SQL alternative (identical execution plan):
orders.createOrReplaceTempView("orders")
result_sql = spark.sql("""
    SELECT user_id, YEAR(order_date) as year,
           SUM(amount) as total_spent,
           COUNT(*) as order_count
    FROM orders
    WHERE status = 'completed' AND amount > 100
    GROUP BY user_id, YEAR(order_date)
    ORDER BY total_spent DESC
    LIMIT 1000
""")
# IDENTICAL execution plan as the DataFrame version above
```

**CATALYST OPTIMIZER - INTERNALS:**

```python
# View Catalyst's execution plan:
df = orders.filter(F.col("status") == "completed") \
           .select("user_id", "amount")

# Logical plan:
df.explain(True)
# Output:
# == Parsed Logical Plan ==
# Project [user_id, amount]
#   Filter (status = completed)
#     Relation[...] parquet
#
# == Analyzed Logical Plan ==
# (column types resolved)
#
# == Optimized Logical Plan ==
# Project [user_id#0, amount#1]    ← projection pruning (only 2 cols)
#   Filter (isnotnull(status) AND (status = completed))  ← null check added
#     Relation[user_id, amount] parquet  ← pushed to scan level
#   ↑ Catalyst moved filter BEFORE projection and to scan level
#
# == Physical Plan ==
# *(1) Project [user_id#0, amount#1]
# +- *(1) Filter (isnotnull(status#2) && (status#2 = completed))
#    +- *(1) ColumnarToRow         ← Parquet column batch → rows
#       +- FileScan parquet [user_id#0,amount#1,status#2]
#          PushedFilters: [IsNotNull(status), EqualTo(status,completed)]
#          ReadSchema: struct<user_id:int,amount:int,status:string>
#          ↑ Catalyst pushed filter to Parquet scan: skip non-matching row groups
#          ↑ Only reads 3 columns (status, user_id, amount) from Parquet

# Key optimizations applied automatically by Catalyst:
# 1. Predicate pushdown: filter moved to scan level
# 2. Projection pruning: reads only 3 of N columns from Parquet
# 3. Null checks: isnotnull added automatically for safety
# 4. Constant folding: 1 + 1 → 2 at plan time, not per-row
# 5. Join reordering: smaller tables joined first when possible
```

**DATASET - TYPE-SAFE API (SCALA):**

```scala
// Dataset[T]: compile-time type safety (Scala/Java only)
import org.apache.spark.sql.{Dataset, SparkSession}

case class Order(orderId: String, userId: Int, amount: Double, status: String)

val spark = SparkSession.builder().appName("TypedDS").getOrCreate()
import spark.implicits._

// Create typed Dataset from Parquet:
val orders: Dataset[Order] = spark.read
  .parquet("s3://warehouse/orders/")
  .as[Order]  // encode schema into typed Dataset

// TYPE-SAFE operations (compile error if wrong type/column):
val completed: Dataset[Order] = orders.filter(_.status == "completed")
val totals = completed
  .groupByKey(_.userId)    // typed key
  .agg(
    typed.sum[Order](_.amount)  // compile error if amount isn't numeric
  )

// HYBRID: use DataFrame for complex SQL, encode to Dataset for typed post-processing:
val rawDf = spark.read.parquet("s3://orders/")
val typedOrders: Dataset[Order] = rawDf.as[Order]
// Now have both: Catalyst optimizations + compile-time type safety

// Python has no Dataset (no compile-time types) - only DataFrame[Row]
```

**BROADCAST JOIN - ELIMINATE SHUFFLE FOR SMALL TABLES:**

```python
# Regular join: both sides shuffled by join key (expensive for large tables)
orders.join(products, "product_id")  # shuffle both DataFrames

# Broadcast join: small table sent to all executors (no shuffle of large table)
from pyspark.sql.functions import broadcast

# Explicit broadcast hint:
small_products = spark.read.parquet("s3://products/")  # 50MB
large_orders = spark.read.parquet("s3://orders/")       # 10TB

result = large_orders.join(
    broadcast(small_products),  # broadcast 50MB to all executors
    "product_id"
)
# large_orders: NOT shuffled (stays partitioned as-is)
# small_products: sent as broadcast variable to every executor
# Each executor: performs local hash join (no network for large_orders)
# Result: NO shuffle for 10TB orders dataset

# Auto-broadcast threshold: tables smaller than this are auto-broadcast
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "20m")  # 20MB default = 10MB
# With AQE enabled: Spark can convert to broadcast join at runtime
# even if size estimates were wrong at plan time
```

---

### 🧪 Thought Experiment

**AVOID THE `collect()` TRAP:**

A common mistake: developer writes `df.collect()` to pull all 10TB of data to the driver → driver JVM OOM. The fix: use `df.write.parquet(...)` to write results to storage, or `df.show(n)` for inspection, or `df.limit(n).collect()` for small samples.

But there's a subtler version: `df.groupBy("category").agg(...)` returns a small summary (100 rows). Calling `.collect()` here is fine - only 100 rows come to driver. The danger is forgetting that `collect()` before aggregation pulls the pre-aggregated data.

Rule: **collect() is only safe after aggregation reduces data to a small result set**. For intermediate large DataFrames: use `write`, `show`, `count`, or `take(n)`.

---

### 🧠 Mental Model / Analogy

> Catalyst is like a database query planner (like PostgreSQL's EXPLAIN). You write a high-level query (DataFrame ops or SQL). The planner considers multiple ways to execute it, estimates costs (using data statistics), and picks the cheapest physical plan. It applies automatic optimizations: moves filters earlier (predicate pushdown), uses indexes (column pruning in Parquet), and picks join algorithms (broadcast hash join for small tables, sort-merge join for large ones). Unlike RDD, where you specify HOW to compute, DataFrame/SQL specifies WHAT you want - the planner decides HOW.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** DataFrame = schema-aware distributed table. SQL-like API (`filter`, `groupBy`, `join`). Auto-optimized by Catalyst. Much faster than RDD for tabular data. Use `spark.read.parquet()`, transform with DataFrame API, write with `df.write.parquet()`.

**Level 2:** Catalyst optimizations: predicate pushdown (filter at read time), projection pruning (read only selected columns), constant folding. Broadcast joins: send small table to all executors, no shuffle for large table. Use `df.explain(True)` to see the physical plan.

**Level 3:** Tungsten: stores data in binary off-heap format (avoids GC pressure), generates bytecode at runtime instead of interpreting operations (Whole-Stage Code Generation). Dataset[T]: adds Scala/Java compile-time type safety at the cost of object deserialization from binary rows. Adaptive Query Execution (AQE): re-optimizes at runtime based on actual shuffle statistics - converts sort-merge join to broadcast join if one side turns out small, coalesces small shuffle partitions.

**Level 4:** Spark's physical plan shows "whole-stage code generation" markers (`*(1)` prefix): these stages compile all operations into a tight, CPU-cache-friendly bytecode loop. Operations without the marker (e.g., Python UDFs) break out of code generation. This is why Python UDFs in Spark are 5-100× slower than native DataFrame operations: each row crosses the JVM-Python boundary. **Pandas UDFs (vectorized UDFs)**: use Apache Arrow to transfer data in batches between JVM and Python, bypassing row-at-a-time serialization. For complex Python logic: always prefer Pandas UDF over row-level Python UDF.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ CATALYST OPTIMIZER PIPELINE                          │
├──────────────────────────────────────────────────────┤
│                                                      │
│ User code: df.filter(...).groupBy(...).agg(...)      │
│        ↓                                             │
│ Unresolved Logical Plan (AST)                       │
│        ↓ resolve columns against catalog             │
│ Analyzed Logical Plan                               │
│        ↓ apply optimization rules (60+ rules)       │
│ Optimized Logical Plan                              │
│   - predicate pushdown (filter → scan time)         │
│   - projection pruning (only needed columns)        │
│   - constant folding                                 │
│        ↓ generate multiple candidates               │
│ Physical Plans [hash join, sort-merge join, ...]    │
│        ↓ cost model picks best                      │
│ Selected Physical Plan                              │
│ [DATAFRAME ← YOU ARE HERE: optimized execution]     │
│        ↓ Tungsten code generation                   │
│ JVM Bytecode (compiled per plan, cache-friendly)    │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Spark SQL query on Parquet table:
SELECT user_id, SUM(amount) FROM orders
WHERE status='completed' AND year=2024
GROUP BY user_id

1. Parse SQL → Unresolved Logical Plan
2. Catalog lookup: resolve "orders" → s3://warehouse/orders/ (Parquet, partitioned by year)
3. Catalyst optimizations:
   - Partition pruning: year=2024 → read ONLY s3://warehouse/orders/year=2024/ folder
   - Column pruning: only read 'user_id', 'amount', 'status' columns from Parquet
   - Predicate pushdown: status='completed' pushed to Parquet row-group filter
4. Physical plan: partial aggregation on read → shuffle → final aggregation
5. Tungsten: compile Stage 1 tasks to bytecode (read+filter+partial agg in one tight loop)
6. Execute:
   Stage 1 (200 tasks, parallel): read 200 Parquet partition files (year=2024 only)
   → 97% I/O reduction vs. full table scan
   → 3 columns read instead of 50 (98% column I/O reduction)
   → Row groups not matching status='completed' skipped via Parquet statistics
   → Partial aggregation: (user_id, partial_sum) emitted per task
   Shuffle: partial aggregates redistributed by user_id
   Stage 2: final SUM per user_id
7. Output: write result
```

---

### ⚖️ Comparison Table

| Feature        | RDD                        | DataFrame             | Dataset (Scala)         |
| -------------- | -------------------------- | --------------------- | ----------------------- |
| API            | Functional, low-level      | Declarative, SQL-like | Typed, functional       |
| Type safety    | None (Scala/Python)        | Runtime (schema)      | Compile-time            |
| Optimization   | None                       | Catalyst + Tungsten   | Catalyst + Tungsten     |
| Performance    | Baseline                   | 5-10× faster          | 5-10× faster            |
| Python support | Yes                        | Yes                   | No                      |
| Use case       | Custom logic, unstructured | Analytics, ETL, SQL   | Typed pipelines (Scala) |

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                                                                                                |
| ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "DataFrame operations are always faster than RDD" | DataFrames are faster for structured/columnar data with Catalyst optimizations. For non-tabular data (custom objects, binary data), RDD may be more appropriate. Python UDFs in DataFrames lose Catalyst optimization                  |
| "Dataset[T] in Python"                            | Dataset[T] with compile-time type safety only exists in Scala/Java. Python only has DataFrame (Dataset[Row]). Use type hints + schema validation for Python type safety                                                                |
| "schema inference is fine for production"         | `spark.read.json()` with no schema → Spark reads entire dataset to infer schema (O(n) extra scan). Always specify schema explicitly in production using `StructType` → faster startup, predictable types, no unexpected schema changes |

---

### 🚨 Failure Modes & Diagnosis

**1. Python UDF Performance Regression**

**Symptom:** A Spark job that previously took 5 minutes now takes 2 hours after adding a data transformation step.

**Root Cause:** A Python lambda or UDF was added that breaks Whole-Stage Code Generation. Each row crosses the JVM-Python boundary (serialization overhead per row).

**Diagnosis:** `df.explain()` - look for stages WITHOUT the `*(1)` prefix (no code generation). Also check SparkUI: look for stages with many tiny tasks and high task deserialization time.

**Fix:** Replace Python UDF with built-in Spark SQL functions (F.regexp_extract, F.split, etc.) when possible. If custom logic is required: use `pandas_udf` (Pandas UDF) with `@F.pandas_udf(returnType)` decorator - processes rows in Arrow batches, ~10× faster than row-level UDFs.

---

### 🔗 Related Keywords

**Prerequisites:** Spark RDD, Apache Spark
**Builds On This:** Spark SQL, Spark Streaming, MLlib
**Related:** Spark RDD, Spark SQL, Spark Streaming

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DATAFRAME   │ Schema-aware, Catalyst-optimized RDD[Row] │
│ DATASET     │ Typed DataFrame (Scala/Java only)          │
│ CATALYST    │ 60+ optimization rules: pushdown, pruning  │
│ TUNGSTEN    │ Code generation + off-heap binary format   │
│ PUSHDOWN    │ Filters + column pruning → read less data  │
│ BROADCAST   │ Small table → all executors; no shuffle    │
│ AQE         │ Runtime re-optimization (Spark 3+)         │
│ EXPLAIN     │ df.explain(True) → view physical plan      │
│ AVOID       │ Python UDFs (JVM boundary) - use built-ins │
│ ONE-LINER   │ "SQL table in Spark; Catalyst picks the   │
│             │  best execution plan from your intent"     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What is Catalyst's predicate pushdown optimization? How does it interact with Parquet file format to reduce I/O? Give a concrete example with a 100-column Parquet table partitioned by date.

**Q2.** (TYPE C - Performance) A Spark DataFrame job reads a 50-column Parquet table (200GB) and joins it with a 5MB lookup table. The join takes 20 minutes. Diagnose what is likely happening in the physical plan and propose optimizations to bring this to under 1 minute.
