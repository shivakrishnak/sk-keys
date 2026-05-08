---
layout: default
title: "Batch vs Stream Processing"
parent: "Big Data & Streaming"
nav_order: 34
permalink: /big-data-streaming/batch-vs-stream-processing/
id: BIG-034
category: Big Data & Streaming
difficulty: ★★☆
depends_on: Lambda Architecture, Apache Spark, Apache Flink
used_by: Data Engineering, Analytics, Real-Time Systems
related: Lambda Architecture, Kappa Architecture, Apache Spark
tags:
  - batch-processing
  - stream-processing
  - latency
  - throughput
  - data-engineering
---

# BIG-034 — Batch vs Stream Processing

⚡ TL;DR — **Batch processing** operates on **bounded, finite datasets** (yesterday's orders → process all at once at midnight) with high throughput and high latency; **stream processing** operates on **unbounded, infinite data** (orders as they arrive → process within milliseconds) with low latency but requires state management for aggregations; **batch wins for**: complex analytics, historical backfill, ML training; **stream wins for**: fraud detection, real-time dashboards, alerting, event-driven pipelines; tools: Spark (batch), Flink/Kafka Streams (streaming), both (Apache Beam, Spark Streaming).

| #559            | Category: Big Data & Streaming                        | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------- | :-------------- |
| **Depends on:** | Lambda Architecture, Apache Spark, Apache Flink       |                 |
| **Used by:**    | Data Engineering, Analytics, Real-Time Systems        |                 |
| **Related:**    | Lambda Architecture, Kappa Architecture, Apache Spark |                 |

---

### 🔥 The Problem This Solves

**NOT ALL DATA PROBLEMS NEED REAL-TIME PROCESSING:**
A company runs two jobs: (1) "detect fraudulent transactions" — needs to run within 100ms of transaction. (2) "compute monthly financial report" — runs once a month, processes 50TB. Using streaming for monthly reports wastes money (stateful processing 24/7 for one monthly run). Using batch for fraud detection fails users (waiting 24 hours for fraud alerts). Understanding when batch vs stream is appropriate prevents over-engineering and under-engineering.

---

### 📘 Textbook Definition

**Batch Processing**:

- Operates on a bounded (finite, complete) dataset.
- Data is collected over a period, then processed as a whole "batch."
- High latency (minutes to hours between data collection and results).
- High throughput (optimized for processing large volumes of data efficiently).
- Tools: Apache Spark, Hive, Pig, MapReduce.

**Stream Processing**:

- Operates on an unbounded (infinite, continuous) data stream.
- Data is processed as it arrives, event by event or in micro-batches.
- Low latency (milliseconds to seconds).
- Requires stateful processing for aggregations (state = running total, window, join buffer).
- Tools: Apache Flink, Kafka Streams, Spark Structured Streaming, Apache Beam.

The core difference: **batch = finite bounded data**, **stream = infinite unbounded data**.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Batch = collect data, process all at once, high latency; Stream = process as it arrives, low latency; tradeoffs are latency, complexity, and cost.

**One analogy:**

> **Batch**: Doing laundry once a week — collect all dirty clothes (batch), wash them together (batch job), done. Efficient use of machine, but you wait a week for clean clothes.
> **Stream**: A dishwasher running automatically after every meal — cleans items as they're dirtied. Always available, but machine runs more often (higher overhead per item).

**One insight:**
The real question is not "which is better?" but "what is the acceptable latency?" If business decisions must be made within seconds (fraud, stock trading, real-time personalization), stream is required. If you need deep analytics, complex ML, or cost-efficient large-scale processing, batch is often superior. Modern systems increasingly use **both** (Lambda/Kappa) or use streaming frameworks that can handle both (Spark Structured Streaming, Apache Beam).

---

### 🔩 First Principles Explanation

**BATCH PROCESSING CHARACTERISTICS:**

```java
// Apache Spark batch job: daily revenue calculation
// Runs: once per day at 02:00 AM
// Input: S3 parquet files (previous day's completed orders)
// Output: revenue_summary table in data warehouse

SparkSession spark = SparkSession.builder()
    .appName("daily-revenue-batch")
    .getOrCreate();

// Read bounded dataset (yesterday's complete data):
Dataset<Row> orders = spark.read()
    .parquet("s3://data-lake/orders/date=2024-01-15/");

// Complex aggregation (easy in batch — data is finite):
Dataset<Row> revenue = orders
    .filter(col("status").equalTo("COMPLETED"))
    .groupBy("product_category", "region")
    .agg(
        sum("amount").as("total_revenue"),
        count("order_id").as("order_count"),
        avg("amount").as("avg_order_value"),
        percentile_approx(col("amount"), 0.95).as("p95_order_value")
    )
    .orderBy(col("total_revenue").desc());

// Write:
revenue.write()
    .mode(SaveMode.Overwrite)
    .saveAsTable("data_warehouse.daily_revenue");

// BATCH ADVANTAGES shown here:
// 1. Complete dataset: all yesterday's orders are present (no missing data)
// 2. Efficient: Spark optimizes full-scan with predicate pushdown, column pruning
// 3. Complex: percentile_approx on full dataset is trivial in batch
//    (in streaming: requires approximate sketch data structures)
// 4. Reproducible: run again → same result (idempotent batch job)
// 5. No state management: each run starts fresh
// BATCH DISADVANTAGES:
// 1. Latency: up to 26 hours after an event occurs (midnight batch + 2h processing)
// 2. No real-time: can't answer "what's today's revenue so far?"
```

**STREAM PROCESSING CHARACTERISTICS:**

```java
// Flink streaming job: real-time fraud detection
// Runs: 24/7 continuously
// Input: Kafka "transactions" topic (unbounded)
// Output: Kafka "fraud-alerts" topic

DataStream<Transaction> transactions = env.fromSource(
    kafkaSource, WatermarkStrategy.noWatermarks(), "transactions"
);

// Stateful processing (HARD part of streaming):
DataStream<FraudAlert> alerts = transactions
    .keyBy(txn -> txn.getUserId())
    .process(new KeyedProcessFunction<String, Transaction, FraudAlert>() {

        // STATE: must be maintained across events (this is what makes streaming hard)
        private ValueState<UserTransactionHistory> historyState;

        @Override
        public void open(Configuration config) {
            historyState = getRuntimeContext().getState(
                new ValueStateDescriptor<>("txn-history", UserTransactionHistory.class)
            );
        }

        @Override
        public void processElement(Transaction txn, Context ctx,
                                    Collector<FraudAlert> out) throws Exception {
            UserTransactionHistory history = historyState.value();
            if (history == null) history = new UserTransactionHistory();

            history.addTransaction(txn);

            // Fraud rule: > 5 transactions in 5 minutes
            if (history.countInLastMinutes(5) > 5) {
                out.collect(new FraudAlert(txn.getUserId(), "RAPID_TRANSACTIONS", txn));
            }

            // Clean old transactions (> 10 minutes)
            history.pruneOlderThan(10, TimeUnit.MINUTES);
            historyState.update(history);
        }
    });

// STREAM ADVANTAGES:
// 1. Latency: milliseconds (fraud detected as transaction happens)
// 2. Continuous: always running, always processing
// 3. Unbounded: handles infinite data without restarting
// STREAM DISADVANTAGES:
// 1. State management: must handle state storage, cleanup, fault tolerance
// 2. Complexity: watermarks, windowing, late data, exactly-once semantics
// 3. Cost: cluster runs 24/7 even during low-traffic hours
// 4. Limited analytics: complex SQL over full history is expensive/impossible in streaming
```

**WHEN TO USE EACH:**

```
BATCH is better when:
  ✓ Latency acceptable: hours, daily, weekly
  ✓ Complete dataset required (monthly billing, financial close)
  ✓ Complex analytics (full-dataset percentiles, global sorts, graph algorithms)
  ✓ ML model training (iterative algorithms, large feature matrices)
  ✓ Data corrections / backfills
  ✓ Cost efficiency (run once per day vs 24/7)

  Examples:
  - Nightly ETL: load raw data → transform → load to DWH
  - Monthly revenue report
  - Weekly ML model retraining
  - Annual compliance reports
  - Historical trend analysis

STREAM is better when:
  ✓ Latency required: seconds, milliseconds
  ✓ Continuous, real-time decisions
  ✓ Event-driven triggers
  ✓ Unbounded data (continuously arriving)
  ✓ Real-time dashboards / monitoring

  Examples:
  - Fraud detection (< 100ms decision)
  - Real-time inventory updates
  - Live dashboards (orders/sec, active users)
  - Alerting and anomaly detection
  - Event-driven microservices
  - Real-time recommendations

BOTH (Lambda / Kappa) when:
  ✓ Need both: real-time approximation + accurate historical results
  ✓ Complex analytics + real-time decisions
  ✓ Compliance: audit trail (batch) + live monitoring (stream)
```

**MICRO-BATCH: THE MIDDLE GROUND:**

```java
// Spark Structured Streaming: micro-batch model
// NOT true streaming (not per-event like Flink)
// Processes events in small batches every N seconds
// Simpler than Flink (no manual state management for many cases)

StreamingQuery query = spark.readStream()
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("subscribe", "orders")
    .load()
    .selectExpr("CAST(value AS STRING) as json")
    .select(from_json(col("json"), orderSchema).as("order"))
    .select("order.*")
    .groupBy(window(col("event_time"), "5 minutes"), col("product_id"))
    .count()
    .writeStream()
    .outputMode("update")
    .format("console")
    .trigger(Trigger.ProcessingTime("30 seconds"))  // micro-batch every 30s
    .start();

// Micro-batch characteristics:
// Latency: 30s (the trigger interval) — not milliseconds
// Throughput: high (batch optimization within each micro-batch)
// Simplicity: SQL-based, no manual state management
// Use when: 1-60 second latency is acceptable; team knows Spark SQL
```

---

### 🧪 Thought Experiment

**THE LATENCY-THROUGHPUT TRADEOFF:**

Consider processing 1 billion events per day:

- **Batch (daily)**: 86,400 seconds to collect events, then process all in 1 hour (3,600s). Throughput: ~278K events/sec sustained during processing window. Latency: up to 25 hours.
- **Stream (per-event)**: Process each event immediately. Throughput: ~11,574 events/sec sustained (1B/day = ~11.5K/sec). Latency: milliseconds.

Batch is actually doing more work per unit time (higher instantaneous throughput during the batch window). Stream processes fewer events per second but has dramatically lower latency. This is the fundamental tradeoff: streaming is not always "faster" in terms of throughput — it's just more timely.

---

### 🧠 Mental Model / Analogy

> **Batch**: A once-a-day newspaper. All events from yesterday → collected → edited → printed → distributed. High quality, complete story, but 24-hour delay.
> **Stream**: Breaking news ticker. Events published as they happen. Immediate but may miss context, may have errors, no complete picture.
> **Micro-batch**: Hourly news updates. Better latency than daily, better completeness than live ticker.

> Most organizations need both: breaking news ticker for immediate alerts (streaming) + comprehensive newspaper for in-depth analysis (batch).

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Batch = bounded data, high latency, simple. Stream = unbounded data, low latency, complex (state, watermarks). Latency requirement drives the choice. Most systems need both.

**Level 2:** Batch strengths: complete data, complex analytics, cost-efficient. Stream strengths: real-time, continuous, event-driven. Micro-batch: compromise (Spark Structured Streaming, 1-60s latency). Tools: Spark (batch), Flink/KStreams (stream), Beam (both).

**Level 3:** Stream complexity sources: (1) State management (store running aggregations in RocksDB), (2) Watermarks and event-time (handle out-of-order data), (3) Exactly-once (reprocessing after failure must not produce duplicates), (4) Schema evolution (stream runs forever; message format changes must be backward-compatible). Batch doesn't have most of these concerns — you control when it runs, what data it processes, and you can re-run if it fails.

**Level 4:** The boundary is blurring. Apache Iceberg + Flink: stream writes to Iceberg tables (with ACID semantics), Spark reads the same tables for batch analytics. "Streaming" and "batch" are access patterns over the same storage, not fundamentally different pipelines. Delta Live Tables (Databricks): define transformations declaratively; DLT runs them as stream or batch based on trigger configuration. The industry trend: unified storage (Iceberg/Delta), flexible processing patterns (stream or batch as needed).

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ BATCH vs STREAM: SAME DATA, DIFFERENT PROCESSING    │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Event log: [E1 E2 E3 E4 E5 E6 E7 E8 E9 E10]       │
│ Time: 00:00 → 23:59                                 │
│                                                      │
│ BATCH PROCESSING (midnight job):                   │
│ 00:00: collect E1-E10 in batch                     │
│ Process: group E1-E10 together → result at 00:30   │
│ Latency: up to 24h (E1 processed 24h after arrival)│
│ Throughput: high (all 10 events in one pass)       │
│                                                      │
│ STREAM PROCESSING (continuous):                    │
│ E1 arrives → processed within 10ms → result at 10ms│
│ E2 arrives → processed within 10ms                 │
│ ... each event individually                        │
│ [STREAM ← YOU ARE HERE: continuous per-event flow] │
│ Latency: 10ms per event                            │
│ Throughput: limited by event rate (10 events × 10ms)│
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
E-commerce platform: batch + stream (Lambda-lite):

Streaming pipeline (always running — Flink):
  Every transaction → fraud check within 100ms → APPROVE/DECLINE
  Every order → inventory update within 1s
  Every session → real-time personalization within 500ms

Batch pipeline (nightly — Spark):
  02:00: Read all of yesterday's orders from S3
  Compute: daily revenue by region, product, campaign
  Compute: ML features for recommendation model
  Compute: customer lifetime value updates
  Write: data warehouse tables for BI tools
  Duration: 3 hours

Result:
  Real-time: Fraud prevented, inventory accurate, users personalized
  Business intelligence: Accurate daily/weekly/monthly reports

If you tried to do everything in streaming:
  Revenue reports: possible but complex (windowing, watermarks)
  ML features: iterative algorithms don't fit streaming → batch needed

If you tried to do everything in batch:
  Fraud detection: 24-hour lag → bank loses $10M/day to fraud
  Inventory: stale → oversell → customer complaints
```

---

### ⚖️ Comparison Table

| Dimension        | Batch                         | Stream                   | Micro-Batch                |
| ---------------- | ----------------------------- | ------------------------ | -------------------------- |
| Latency          | Hours-days                    | Milliseconds-seconds     | 1-60 seconds               |
| Throughput       | Very high (optimized bulk)    | High (sustained)         | High                       |
| Data model       | Bounded (finite)              | Unbounded (infinite)     | Both                       |
| Complexity       | Low                           | High                     | Medium                     |
| State management | Not needed (restart each run) | Required (RocksDB)       | Optional                   |
| Fault tolerance  | Re-run the job                | Checkpointing + replay   | Checkpointing              |
| Best for         | Analytics, ML, ETL            | Fraud, alerts, real-time | 30s-latency analytics      |
| Tools            | Spark, Hive                   | Flink, Kafka Streams     | Spark Structured Streaming |

---

### ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                                                                                                                                                                                   |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Streaming is always better than batch" | Streaming is better only when low latency is REQUIRED. For nightly ETL, monthly reports, ML training: batch is simpler, cheaper, and produces more accurate results on complete datasets                                                  |
| "Spark Streaming is true streaming"     | Spark's DStream (legacy) and Structured Streaming are micro-batch (except continuous processing mode). True streaming (per-event, <10ms) is Apache Flink. Spark Streaming latency is ~100ms-1s minimum                                    |
| "Streaming can't do complex analytics"  | Streaming can do most aggregations, joins, and analytics — but requires state management, watermarks, and streaming-appropriate algorithms. Global sorts and iterative algorithms (ML training) are genuinely harder. Use batch for these |

---

### 🚨 Failure Modes & Diagnosis

**1. Streaming Job Accumulates Unbounded State**

**Symptom:** Stream processing job's memory/RocksDB grows continuously. Job eventually crashes with OOM.

**Root Cause:** Stateful operation without state cleanup. E.g., maintaining a running total per userId forever — unlimited users → unlimited state.

**Fix:**

```java
// ADD TTL to state: automatically expire inactive keys
StateTtlConfig ttlConfig = StateTtlConfig
    .newBuilder(Duration.ofHours(24))  // expire state after 24h of inactivity
    .setUpdateType(StateTtlConfig.UpdateType.OnCreateAndWrite)
    .setStateVisibility(StateTtlConfig.StateVisibility.NeverReturnExpired)
    .build();

ValueStateDescriptor<UserTransactionHistory> descriptor =
    new ValueStateDescriptor<>("txn-history", UserTransactionHistory.class);
descriptor.enableTimeToLive(ttlConfig);
// Keys not updated for 24h: state automatically evicted
// RocksDB size: bounded by active users in last 24h
```

---

### 🔗 Related Keywords

**Prerequisites:** Lambda Architecture, Apache Spark
**Builds On This:** Kappa Architecture, Lambda Architecture
**Related:** Lambda Architecture, Kappa Architecture, Apache Spark

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ BATCH       │ Bounded data, high latency, simple        │
│ STREAM      │ Unbounded data, low latency, complex      │
│ MICRO-BATCH │ Small batches every N sec (compromise)    │
│ BATCH USE   │ ETL, reports, ML training, backfill       │
│ STREAM USE  │ Fraud, alerts, real-time dashboards       │
│ STATE MGMT  │ Stream needs it; batch doesn't            │
│ LATENCY     │ Batch: hours; Stream: ms; μBatch: 1-60s  │
│ TOOLS       │ Spark (batch), Flink (stream), Beam (both)│
│ OOM FIX     │ TTL on stateful stream operators          │
│ ONE-LINER   │ "Batch = big bounded jobs; stream =      │
│             │  continuous per-event; choose by latency  │
│             │  requirement, not by trendiness"          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What are the key differences between batch processing and stream processing? For each, name a technical characteristic (latency, data boundedness, state management) and explain why that characteristic exists.

**Q2.** (TYPE C — Design) A healthcare company wants to: (1) detect anomalous vital signs from ICU monitors within 5 seconds, (2) run nightly cohort analysis on all patients, (3) retrain ML risk models weekly. Which data processing approach (batch, stream, both) would you use for each? What tools would you choose and why?
