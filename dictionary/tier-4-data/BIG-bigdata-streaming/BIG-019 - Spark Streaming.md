---
version: 2
layout: default
title: "Spark Streaming"
parent: "Big Data & Streaming"
grand_parent: "Technical Dictionary"
nav_order: 19
permalink: /big-data-streaming/spark-streaming/
id: BIG-030
category: Big Data & Streaming
difficulty: ★★★
depends_on: Apache Spark, Spark DataFrame, Apache Kafka
used_by: Real-Time ETL, Stream Analytics, Event Processing
related: Apache Kafka, Apache Flink, Windowing
tags:
  - spark-streaming
  - structured-streaming
  - micro-batch
  - real-time
  - deep-dive
---

# BIG-025 - Spark Streaming

⚡ TL;DR - Spark **Structured Streaming** is a **micro-batch streaming engine** (default 100ms-1s trigger intervals) built on Spark SQL - treats an incoming stream as an unbounded table, appending new rows as data arrives; provides **exactly-once semantics** via WAL + idempotent sinks (Kafka, Delta Lake); latency: 100ms-1s (not milliseconds - use Flink for sub-100ms); the older **DStream API** is deprecated.

| #538            | Category: Big Data & Streaming                    | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------ | :-------------- |
| **Depends on:** | Apache Spark, Spark DataFrame, Apache Kafka       |                 |
| **Used by:**    | Real-Time ETL, Stream Analytics, Event Processing |                 |
| **Related:**    | Apache Kafka, Apache Flink, Windowing             |                 |

---

### 🔥 The Problem This Solves

**BATCH ETL PROCESSING EVENTS AN HOUR LATE:**
Traditional ETL: collect logs → wait for batch → process batch → insights available hours later. Structured Streaming applies the same Spark DataFrame operations (SQL, joins, aggregations) to data as it arrives from Kafka, eliminating the wait. Engineers reuse the same Spark SQL skillset, the same APIs, the same DataFrame transformations - just replace `spark.read` with `spark.readStream`. The micro-batch model means you don't need to learn a new processing framework (Flink) for most latency requirements (>100ms).

---

### 📘 Textbook Definition

**Spark Structured Streaming** processes an incoming stream as an **unbounded table**: new data is appended as new rows, and the user defines queries over this table (like a batch query). Spark executes the query continuously in micro-batches.

Key concepts:

- **Trigger**: how often to run a micro-batch (once per X time, or as fast as possible, or once for batch backfill).
- **Checkpoint**: saves progress (last processed Kafka offset + intermediate state) to HDFS/S3. Enables recovery after failure without reprocessing or missing data.
- **Output modes**: `append` (new rows only), `update` (changed rows), `complete` (entire result table).
- **Watermark**: handles late-arriving data - tells Spark to wait N minutes for late events before closing a time window. Events arriving later than watermark are dropped.
- **State store**: maintains aggregation state across micro-batches (e.g., running counts, windowed aggregations). Stored in executor memory (with optional RocksDB backend).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Structured Streaming = treat a stream as an ever-growing table, run batch-like Spark SQL queries on it in micro-batches every 100ms-1s, with exactly-once semantics via checkpoint + idempotent sinks.

**One analogy:**

> A streaming query is like a database VIEW on a live table. Orders table keeps getting new rows (from Kafka). Your view says "total revenue by hour." Every 500ms, Spark refreshes the view: reads new rows since last batch, updates the running aggregation. The engineer wrote a normal SQL GROUP BY query - Spark handles the incremental update logic automatically.

**One insight:**
Structured Streaming's most important guarantee: **exactly-once end-to-end**. This requires three things working together: (1) replayable source (Kafka tracks offsets), (2) checkpoint (Spark saves the last committed offset before processing), (3) idempotent sink (writing to Delta Lake with the same `batchId` doesn't create duplicates). Without all three, you get at-least-once (duplicates) or at-most-once (data loss). Most production failures happen at the sink: if your output is a JDBC write without idempotency keys, re-runs will duplicate rows.

---

### 🔩 First Principles Explanation

**STRUCTURED STREAMING - KAFKA TO DELTA LAKE:**

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType

spark = SparkSession.builder \
    .appName("OrdersStreaming") \
    .config("spark.sql.streaming.checkpointLocation", "s3://checkpoints/orders/") \
    .config("spark.sql.adaptive.enabled", "true") \
    .getOrCreate()

# 1. SOURCE: Read from Kafka (replayable source - Spark tracks offsets)
orders_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka-broker1:9092,kafka-broker2:9092") \
    .option("subscribe", "orders") \
    .option("startingOffsets", "latest") \  # or "earliest" for backfill
    .option("maxOffsetsPerTrigger", 100000) \  # rate-limit per micro-batch
    .load()
# orders_stream: streaming DataFrame with columns:
#   key(binary), value(binary), topic, partition, offset, timestamp

# 2. DESERIALIZE: Kafka value is binary → parse as JSON
order_schema = StructType([
    StructField("order_id", StringType()),
    StructField("user_id", IntegerType()),
    StructField("amount", IntegerType()),
    StructField("event_time", TimestampType()),
    StructField("status", StringType())
])
orders = orders_stream \
    .select(F.from_json(F.col("value").cast("string"), order_schema).alias("data")) \
    .select("data.*")

# 3. WATERMARK: tell Spark to wait 10 minutes for late events
#    Events arriving > 10 minutes after event_time will be dropped
orders_with_watermark = orders \
    .withWatermark("event_time", "10 minutes")

# 4. TRANSFORMATION: windowed aggregation (counts per 1-minute tumbling window)
windowed_counts = orders_with_watermark \
    .groupBy(
        F.window("event_time", "1 minute"),  # tumbling 1-minute windows
        "status"
    ) \
    .agg(
        F.count("*").alias("count"),
        F.sum("amount").alias("total_amount")
    )

# 5. SINK: Write to Delta Lake (exactly-once with batchId idempotency)
query = windowed_counts.writeStream \
    .format("delta") \
    .option("checkpointLocation", "s3://checkpoints/windowed-orders/") \
    .outputMode("update") \        # only write changed aggregation rows
    .trigger(processingTime="500 milliseconds") \  # micro-batch every 500ms
    .toTable("order_window_counts")

# 6. Monitor and wait for termination:
query.awaitTermination()
# query.status → current batch info
# query.lastProgress → metrics (processed rows/sec, trigger time, etc.)
```

**EXACTLY-ONCE SEMANTICS - HOW IT WORKS:**

```
Exactly-once requires: replayable source + checkpoint + idempotent sink

Scenario: Structured Streaming reads from Kafka → writes to Delta Lake

Micro-batch N:
  1. Checkpoint BEFORE processing:
     Spark records: "starting offsets for batch N = {partition-0: offset-1500}"
     Writes to: s3://checkpoints/offsets/N

  2. Process: read Kafka offsets 1500-1700 → transform → prepare Delta writes

  3. Commit: write to Delta Lake with batchId=N
     Delta Lake: checks if batchId=N was already committed
     If no: commit → marks batchId=N as complete in Delta transaction log
     If yes: no-op (idempotent - same batchId never written twice)

  4. Checkpoint AFTER processing:
     Spark records: "completed batch N, end offsets = {partition-0: offset-1700}"
     Writes to: s3://checkpoints/commits/N

Failure scenarios:
  A) Crash after step 1, before step 3:
     Restart: load checkpoint N → see uncommitted batch N
     Replay batch N: re-read Kafka offsets 1500-1700 (replayable source)
     Delta: batchId=N not committed → commits fresh → no duplicate

  B) Crash after step 3, before step 4:
     Restart: load checkpoint N-1 (last committed) → try batch N again
     Delta: batchId=N was ALREADY committed → idempotent no-op → no duplicate
     Proceed to batch N+1

Result: exactly-once delivery guaranteed by this protocol
```

**OUTPUT MODES:**

```python
# APPEND mode: only emit new rows (never update previous results)
#   Use for: simple filtering, stateless transformations, appending events
#   Cannot use for: aggregations (aggregate values change as new data arrives)
query = flat_orders.writeStream \
    .outputMode("append") \
    .format("parquet") \
    .start("s3://output/orders/")

# UPDATE mode: emit rows that changed since last batch
#   Use for: aggregations where only updated groups should be written
#   Cannot use for: sorting (need complete result to sort)
query = windowed_counts.writeStream \
    .outputMode("update") \
    .format("delta") \
    .start()

# COMPLETE mode: emit the ENTIRE result table every batch
#   Use for: aggregations where consumer always needs the full current state
#   Warning: result table can grow unboundedly without watermark
#   Expensive: rewrites everything every batch
query = global_counts.writeStream \
    .outputMode("complete") \
    .format("memory") \   # for testing: write to in-memory table
    .queryName("counts_table") \
    .start()

# Access in-memory sink:
spark.sql("SELECT * FROM counts_table ORDER BY count DESC LIMIT 10").show()
```

**STATEFUL STREAMING - CUSTOM STATE:**

```python
from pyspark.sql.streaming import GroupState, GroupStateTimeout
from typing import Iterator, Tuple
import pandas as pd

# flatMapGroupsWithState: custom stateful logic per key
# Use case: detect user sessions (inactivity timeout = session end)

def session_detector(
    user_id: int,
    events: Iterator[pd.DataFrame],
    state: GroupState
) -> Iterator[pd.DataFrame]:

    SESSION_TIMEOUT_SECS = 300  # 30 min inactivity = new session

    if state.hasTimedOut:
        # Session expired - emit session summary
        session_data = state.get
        yield pd.DataFrame({
            "user_id": [user_id],
            "session_id": [session_data["session_id"]],
            "event_count": [session_data["event_count"]],
            "session_start": [session_data["start_time"]],
            "session_end": [session_data["last_time"]]
        })
        state.remove()
        return

    for event_batch in events:
        if state.exists:
            current = state.get
            state.update({
                "session_id": current["session_id"],
                "event_count": current["event_count"] + len(event_batch),
                "start_time": current["start_time"],
                "last_time": event_batch["event_time"].max()
            })
        else:
            state.update({
                "session_id": f"{user_id}_{int(event_batch['event_time'].min().timestamp())}",
                "event_count": len(event_batch),
                "start_time": event_batch["event_time"].min(),
                "last_time": event_batch["event_time"].max()
            })
        # Set expiry timeout
        state.setTimeoutDuration(SESSION_TIMEOUT_SECS * 1000)  # milliseconds
    yield pd.DataFrame()  # no immediate output; emit on timeout

# Apply:
session_output = orders \
    .withWatermark("event_time", "10 minutes") \
    .groupBy("user_id") \
    .applyInPandasWithState(
        session_detector,
        outputStructType="user_id int, session_id string, ...",
        stateStructType="session_id string, event_count int, ...",
        outputMode="append",
        timeoutConf=GroupStateTimeout.ProcessingTimeTimeout
    )
```

---

### 🧪 Thought Experiment

**WHAT HAPPENS WHEN A STREAMING JOB FALLS BEHIND?**

Scenario: Kafka produces 1M events/second. Spark processes 500K events/second (falling behind). Kafka consumer lag grows: 100K, 200K, 1M, 10M records behind.

If unconstrained: each micro-batch reads all accumulated events - 10M records. Batch takes much longer than trigger interval. State store grows huge. Memory pressure.

Solutions:

1. `maxOffsetsPerTrigger`: caps how many Kafka records per batch → gradual catch-up, predictable memory
2. Scale: add more Spark executors / increase executor cores
3. Optimize: reduce transformation complexity, use more efficient serialization (Avro/Protobuf over JSON)
4. Alert: monitor `kafka.consumer.lag` metric → trigger scaling before lag becomes critical

---

### 🧠 Mental Model / Analogy

> Structured Streaming is like a bank's real-time balance update system. Transactions (events) arrive on a conveyor belt (Kafka). Every 500ms, the processing clerk (micro-batch) picks up all transactions from the belt since the last pickup, processes them (update account balances), and saves the new balances (sink). The clerk's notebook (checkpoint) records "I processed up to transaction #15,237." If the clerk is sick (executor failure): a new clerk starts, reads the notebook ("last done: #15,237"), and continues from #15,238 - no transaction is missed or double-counted.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Structured Streaming = run Spark SQL queries on streaming data in micro-batches. Read from Kafka, transform with DataFrame API, write to Delta Lake/Parquet. Trigger every 100ms-1s. Checkpoint enables recovery.

**Level 2:** Watermark: tolerate late events - wait N minutes for late data before closing a window. Output modes: append (new rows), update (changed rows), complete (whole result). Exactly-once = replayable source + checkpoint + idempotent sink (Delta Lake).

**Level 3:** State store: maintains aggregation state between micro-batches. For large state: use RocksDB state backend (`spark.sql.streaming.stateStore.providerClass=RocksDBStateStoreProvider`). Custom state: `mapGroupsWithState`/`flatMapGroupsWithState` for session detection, fraud detection. Continuous processing mode: sub-millisecond latency (experimental, limited operators).

**Level 4:** Structured Streaming vs. Flink: Structured Streaming uses micro-batching (latency = trigger interval, min ~100ms). Flink uses true event-by-event processing (latency ~1-10ms). For >100ms latency: use Structured Streaming (simpler, native Spark). For <100ms: use Flink. State checkpointing: Structured Streaming checkpoints state to HDFS/S3 on every batch. Flink uses incremental RocksDB checkpoints (much faster for large state). When NOT to use Structured Streaming: IoT alerting in <50ms, financial fraud detection in <10ms - use Flink or purpose-built stream processors.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ STRUCTURED STREAMING EXECUTION MODEL                 │
├──────────────────────────────────────────────────────┤
│                                                      │
│  [Kafka Topic: orders]  ← producers write events    │
│         ↓ micro-batch trigger (every 500ms)         │
│  [Structured Streaming Engine]                       │
│    reads Kafka offsets N to M                        │
│    applies DataFrame transformations                 │
│    updates state store (aggregations)               │
│    [STREAMING ← YOU ARE HERE: incremental query]    │
│         ↓ writes output                             │
│  [Delta Lake / Parquet / Kafka / JDBC]               │
│                                                      │
│  [Checkpoint on S3/HDFS]                             │
│    last committed offsets                            │
│    state store snapshots                             │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Real-time order analytics pipeline:
Orders → Kafka → Structured Streaming → Delta Lake → BI Dashboard

T=0ms: 10,000 order events arrive in Kafka (partition 0: offsets 1000-1500)
T=500ms: Trigger fires - micro-batch 42 starts
  1. Read checkpoint: "last committed batch 41, offsets = partition-0: 999"
  2. Read Kafka: partitions 0: 1000-1500 (5,000 events → 10 executors)
  3. Transform: parse JSON, apply watermark, compute windowed counts
  4. State update: window [10:00-10:01] count: 2500→4800 (new events in window)
  5. Write to Delta: UPDATE order_counts SET count=4800 WHERE window='10:00-10:01'
     Delta: batchId=42 committed atomically
  6. Checkpoint: record "batch 42 complete, offsets = partition-0: 1500"
T=520ms: Batch 42 complete. StreamingQueryProgress:
  "numInputRows": 5000,
  "inputRowsPerSecond": 10000,
  "processedRowsPerSecond": 9615,
  "triggerExecution": {"durationMs": 520}
T=1000ms: Trigger fires - micro-batch 43 starts (next 500ms of events)
```

---

### ⚖️ Comparison Table

| Feature          | Structured Streaming                | DStream (legacy) | Apache Flink             |
| ---------------- | ----------------------------------- | ---------------- | ------------------------ |
| API              | DataFrame/SQL                       | RDD-based        | DataStream/Table API     |
| Latency          | 100ms-1s (micro-batch)              | 500ms-2s         | 1-10ms (true streaming)  |
| Exactly-once     | Yes (checkpoint + idempotent sinks) | Limited          | Yes                      |
| Windowing        | Tumbling, sliding, session          | Limited          | Rich (including session) |
| State management | State store (memory, RocksDB)       | Limited          | Rich (RocksDB backend)   |
| Recommendation   | Production standard                 | Deprecated       | For <100ms latency       |

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                                                                            |
| ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Structured Streaming is real-time (<10ms)" | Structured Streaming uses micro-batching. Minimum latency is the trigger interval (typically 100ms-1s). True sub-second, sub-100ms latency requires Apache Flink or similar true streaming engines |
| "DStream API is still recommended"          | DStream API is deprecated since Spark 3.0. Always use Structured Streaming API for new Spark streaming applications                                                                                |
| "Checkpoint stores the data"                | Checkpoint stores: (1) source offsets (how far we've read from Kafka), (2) streaming state (aggregation state between batches). NOT the processed data itself. Data is written to the sink         |

---

### 🚨 Failure Modes & Diagnosis

**1. State Store Growing Unboundedly - OOM on Executors**

**Symptom:** Streaming job runs fine for hours, then executors start failing with OOM. SparkUI shows state store size growing continuously.

**Root Cause:** Aggregations without watermark (or insufficient watermark). Spark keeps ALL historical aggregation state (e.g., counts per user since the beginning of time) because it doesn't know when a window/user is "done."

**Fix:** Add watermark: `.withWatermark("event_time", "1 hour")`. This tells Spark: "no events will arrive more than 1 hour late. After a window closes + 1 hour: drop its state." Without watermark: state grows forever.

**Also consider:** Switch to RocksDB state backend for large state: `spark.sql.streaming.stateStore.providerClass=org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider` - handles 100s of GB of state efficiently.

---

### 🔗 Related Keywords

**Prerequisites:** Apache Spark, Spark DataFrame, Apache Kafka
**Builds On This:** Windowing, Watermarks, Event Time vs Processing Time
**Related:** Apache Kafka, Apache Flink, Windowing

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ MODEL       │ Unbounded table (append rows from stream)  │
│ LATENCY     │ 100ms-1s (micro-batch; not true streaming) │
│ EOS         │ Checkpoint + replayable source + idem sink │
│ WATERMARK   │ Max late arrival tolerance → drop beyond   │
│ OUTPUT MODE │ append / update / complete                  │
│ CHECKPOINT  │ Saves offsets + state; enables recovery    │
│ STATE       │ RocksDB for large state (100s of GB)       │
│ vs FLINK    │ Flink for <100ms; use Spark for >100ms     │
│ TRIGGER     │ processingTime="500ms" or once (batch)     │
│ ONE-LINER   │ "Micro-batch SQL on streams; exactly-once  │
│             │  via checkpoint + idempotent Delta writes" │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) Explain how Structured Streaming achieves exactly-once semantics end-to-end. What are the three components required? What happens if the executor fails (1) before writing to sink, (2) after writing to sink but before checkpointing the offset?

**Q2.** (TYPE C - Design) Design a fraud detection streaming pipeline that: (1) reads payment events from Kafka, (2) detects if a user has > 5 transactions within any 1-minute window, (3) emits an alert to a separate Kafka topic. Consider: watermark, output mode, latency requirements.
