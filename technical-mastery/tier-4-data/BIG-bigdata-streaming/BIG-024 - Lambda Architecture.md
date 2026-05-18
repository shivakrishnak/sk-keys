---
version: 2
layout: default
title: "Lambda Architecture"
parent: "Big Data & Streaming"
grand_parent: "Technical Mastery"
nav_order: 24
permalink: /technical-mastery/big-data-streaming/lambda-architecture/
id: BIG-034
category: Big Data & Streaming
difficulty: ★★★
depends_on: Batch vs Stream Processing, Apache Spark, Apache Flink
used_by: Real-Time Analytics, Big Data Systems, Data Engineering
related: Kappa Architecture, Batch vs Stream Processing, Apache Spark
tags:
  - lambda-architecture
  - batch-layer
  - speed-layer
  - serving-layer
  - big-data
---

⚡ TL;DR - **Lambda Architecture** runs **two parallel pipelines**: a **batch layer** (Spark, reprocesses all history, high accuracy, high latency) + a **speed layer** (Flink/Spark Streaming, processes recent data, low latency, approximate) + a **serving layer** (merges both views for queries); provides eventual accuracy - batch results overwrite speed layer results once complete; the main criticism: **maintaining two codebases** (one batch, one streaming) with identical logic is operationally expensive; largely superseded by **Kappa Architecture**.

| #557            | Category: Big Data & Streaming                               | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------- | :-------------- |
| **Depends on:** | Batch vs Stream Processing, Apache Spark, Apache Flink       |                 |
| **Used by:**    | Real-Time Analytics, Big Data Systems, Data Engineering      |                 |
| **Related:**    | Kappa Architecture, Batch vs Stream Processing, Apache Spark |                 |

---

### 🔥 The Problem This Solves

**STREAMING ALONE ISN'T ALWAYS ACCURATE:**
Before exactly-once streaming became reliable (~2017+), stream processing had a dilemma: fast but approximate (streaming) vs. slow but accurate (batch). Lambda Architecture solved this with both layers running in parallel:

1. **Batch layer**: reprocesses all historical data hourly/daily → 100% accurate, but hours old.
2. **Speed layer**: processes new data in real time → seconds old, but possibly approximate or incomplete.
3. **Serving layer**: queries both → returns "most recent batch + recent stream delta."

This gave the best of both worlds at the cost of maintaining two separate pipelines.

---

### 📘 Textbook Definition

**Lambda Architecture** (proposed by Nathan Marz, ~2012) is a data processing architecture with three layers:

1. **Batch Layer** (cold path):
   - Stores all raw data immutably (HDFS, S3)
   - Periodically (hourly, daily) reprocesses ALL data with batch jobs (Spark, MapReduce)
   - Produces **batch views**: pre-computed, accurate query results
   - High latency (hours) but 100% accurate

2. **Speed Layer** (hot path):
   - Processes only recent data (since last batch run)
   - Uses stream processing (Flink, Spark Streaming, Kafka Streams)
   - Produces **real-time views**: low latency, potentially approximate
   - Discards old data once batch layer catches up

3. **Serving Layer**:
   - Responds to queries by merging batch view + real-time view
   - Tools: Apache Druid, Cassandra, HBase, Elasticsearch
   - Query: `total = batch_result (up to T-2h) + stream_result (last 2h)`

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Lambda = batch (accurate, slow) + streaming (fast, approximate) + merge layer; queries see both; batch catches up eventually for full accuracy.

**One analogy:**

> Weather forecast + current sensor: The weather bureau's official forecast (batch) is accurate but calculated overnight. Your phone's live weather widget (stream) shows current temperature from nearby sensors, updating every minute. The weather app (serving layer) shows: "Official forecast: 22°C tomorrow | Current: 19°C." You get both the authoritative long-term data AND the latest real-time update.

**One insight:**
Lambda Architecture's fatal flaw is **two codebases problem**: you write the same business logic TWICE - once in Spark batch (Scala) and once in Flink/Kafka Streams (Java). When the business logic changes (new formula, new filter), you must update BOTH consistently. In practice, they diverge. Teams spend 40% of their time ensuring batch and stream produce the same results. This led directly to the creation of Kappa Architecture (stream-only) and the Apache Beam model (one API for both batch and streaming).

---

### 🔩 First Principles Explanation

**LAMBDA ARCHITECTURE IMPLEMENTATION:**

```java
// BATCH LAYER: Spark job runs every 2 hours
// Processes ALL data from S3/HDFS, produces accurate views
// Example: hourly user engagement metrics

public class BatchEngagementJob {
    public static void main(String[] args) {
        SparkSession spark = SparkSession.builder()
            .appName("batch-engagement")
            .getOrCreate();

        // Read ALL historical events from S3:
        Dataset<Row> allEvents = spark.read()
            .parquet(
                "s3://data-lake/events/year=*/month=*/day=*/hour=*/");

        // Compute accurate hourly engagement per user:
        Dataset<Row> batchView = allEvents
            .groupBy("userId", "hour")
            .agg(
                count("eventId").as("totalEvents"),
                countDistinct("pageId").as("uniquePages"),
                sum("duration").as("totalDuration")
            );

        // Write batch view to serving layer (Cassandra):
        batchView.write()
            .format("org.apache.spark.sql.cassandra")
            .option("keyspace", "serving")
            .option("table", "user_engagement_batch")
            .mode(SaveMode.Overwrite)
            .save();

        // Update batch view timestamp (so serving layer knows latest
        // batch):
        spark.sparkContext().hadoopConfiguration()
            .set("batch.view.timestamp", Instant.now().toString());
    }
}
// Runs: every 2 hours, processes terabytes, takes 30-60 minutes to
// complete
// Lag: up to 3 hours behind real-time (2h batch interval + 1h
// processing time)
```

```java
// SPEED LAYER: Kafka Streams / Flink job (always running)
// Processes only RECENT events (since last batch completed)
// Produces approximate real-time view

@Component
public class StreamEngagementProcessor {

    @Autowired
    void buildTopology(StreamsBuilder builder) {

        // Process only recent events (last 4 hours in Kafka
        // retention):
        KStream<String,
            UserEvent> events = builder.stream("user-events");

        // 5-minute tumbling windows for recent engagement:
        KTable<Windowed<String>, UserEngagement> streamView = events
            .groupBy((key, event) -> event.getUserId())
            .windowedBy(TimeWindows.ofSizeWithNoGrace(
                Duration.ofMinutes(5)))
            .aggregate(
                UserEngagement::new,
                (userId, event, agg) -> agg.add(event),
                Materialized.as("stream-engagement-store")
            );

        // Write to serving layer (separate from batch view):
        streamView.toStream()
            .to("user-engagement-stream-view");
    }
}
```

```java
// SERVING LAYER: merges batch + stream views
// Returns: batch_result (accurate, up to T-2h) + stream_delta (recent
// 2h)

@RestController
public class EngagementQueryController {

    private final CassandraTemplate cassandra;
    private final KafkaStreamsInteractiveQuery streamQuery;

    @GetMapping("/engagement/{userId}/last-hour")
    public UserEngagementResponse getEngagement(
        @PathVariable String userId) {

        // 1. Query batch view (accurate, but 2+ hours behind):
        UserEngagement batchResult = cassandra
            .selectOne(
                Query.query(Criteria.where("userId").is(userId)
                    .and("hour").is(LocalDateTime.now().minusHours(2)
                        .truncatedTo(HOURS))),
                UserEngagement.class
            );
        // batchResult: accurate data for T-3h to T-2h

        // 2. Query stream view (recent, possibly approximate):
        UserEngagement streamDelta = streamQuery.queryState(
            "stream-engagement-store", userId
        );
        // streamDelta: data for last 2 hours

        // 3. Merge: batch + stream = complete picture
        UserEngagement merged = merge(batchResult, streamDelta);
        // merged: accurate for T-3h, real-time for last 2h

        return UserEngagementResponse.from(merged);
    }

    private UserEngagement merge(UserEngagement batch,
        UserEngagement stream) {
        // Simple merge: add counts (if no overlap)
        // Complex merge: handle overlap period carefully
        return UserEngagement.builder()
            .totalEvents(batch.getTotalEvents() +
                stream.getTotalEvents())
            .uniquePages(mergeSets(batch.getUniquePages(),
                stream.getUniquePages()))
            .build();
    }
}
```

**WHY LAMBDA IS DECLINING:**

```
Problems with Lambda Architecture in practice:

1. DUAL CODEBASE MAINTENANCE:
   Same logic: "revenue = sum(order.amount) for paid
     orders in each hour"
   Batch version (Spark): Dataset.filter(_.status ==
     "paid").groupBy("hour").sum("amount")
   Stream version (Kafka Streams): KStream.filter(e ->
     "paid".equals(e.getStatus()))
                                         .groupBy(...).aggr

   When product says "exclude refunded orders":
   → Update batch job
   → Update stream job
   → Test both produce identical results
   → Deploy both
   → This happens 10× per sprint

2. RESULT INCONSISTENCY:
   Batch and stream diverge due to:
   - Different deduplication logic
   - Different timezone handling
   - Different null handling
   - Different join semantics
   Result: batch says $100K revenue, stream says $98.5K
   Finance wants to know which one is right. Answer: both,
     sort of.

3. OPERATIONAL COMPLEXITY:
   Run and maintain:
   → Spark cluster (batch)
   → Flink/Kafka Streams cluster (streaming)
   → Serving layer (Cassandra + merge query logic)
   → 3 separate monitoring systems
   → 3 failure modes

4. LATENCY STILL HOURS:
   The batch layer doesn't provide real-time data - it
     provides accurate data
   for N hours ago. The speed layer is real-time but
     approximate.
   "Eventually accurate" can mean 3-hour lag for
     corrections.
```

---

### 🧪 Thought Experiment

**IS LAMBDA EVER STILL THE RIGHT CHOICE?**

Yes, in specific scenarios:

1. **ML feature pipelines**: batch jobs produce complex features (collaborative filtering, graph algorithms) that can't be easily expressed in streaming. Speed layer provides simple real-time features (last 5 minutes activity). Serving layer merges both.

2. **Compliance and auditability**: batch layer is the "source of truth" (immutable, reprocessable). Stream layer is "best effort." Auditors verify against batch.

3. **Legacy systems**: existing batch infrastructure is reliable. Adding a speed layer (Kafka Streams) for low-latency dashboards without replacing the batch system is a pragmatic Lambda deployment.

4. **Complex historical analytics**: backfilling 5 years of data is a one-time batch job. Maintaining both a streaming pipeline AND this historical batch results in Lambda temporarily during migration.

---

### 🧠 Mental Model / Analogy

> Lambda Architecture is like a bank with two ledgers: a **real-time ledger** (teller updates balance after every transaction - fast, may have errors) and a **nightly reconciliation** (overnight audit of ALL transactions - slow but guaranteed accurate). Customer queries: "Your balance is approximately $1,234 (real-time) - final balance confirmed after nightly reconciliation (accurate)." If the real-time ledger had errors, the nightly reconciliation corrects them. Two ledgers, one truth.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Lambda = batch (Spark, historical accuracy) + streaming (Flink, real-time) + serving (merge). Queries = batch result + stream delta. Two codebases = main problem. Largely superseded by Kappa.

**Level 2:** Batch layer: immutable raw data in S3/HDFS, batch jobs reprocess all history. Speed layer: processes only recent data (since last batch). Serving layer: merges views. Apache Druid and Cassandra commonly used for serving layer (time-series, fast reads).

**Level 3:** Two codebases problem: same logic must be implemented identically in batch and stream. Apache Beam addresses this: write one pipeline, run on Spark (batch) OR Flink (stream). Unified model partially solves Lambda's dual codebase problem.

**Level 4:** Lambda vs Kappa decision: if your business logic is expressible in streaming (80% of cases) → Kappa (simpler, one codebase). If you need complex historical analysis (graph algorithms, iterative ML) or batch-only data sources (S3 dumps, daily DB exports) → Lambda or hybrid (Lambda for historical, Kappa for new data). Delta Lake / Apache Iceberg blur the line further: stream writes to Delta table, batch queries same table - "Lambda without separate pipelines" (but still batch semantics for the historical queries).

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ LAMBDA ARCHITECTURE                                  │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Raw Data (S3/HDFS) ← ALL events immutably stored   │
│     ↓ batch jobs (hourly)        ↓ stream (always) │
│ [BATCH LAYER]              [SPEED LAYER]            │
│ Spark/MapReduce             Flink/KafkaStreams       │
│ All history                 Last 2-4 hours           │
│ High accuracy               Low latency              │
│ High latency (hours)        Approximate              │
│     ↓                              ↓                │
│ Batch Views (Cassandra)    Real-time Views (Redis)  │
│     ↓                              ↓                │
│            [SERVING LAYER]                          │
│       Merges batch + stream for queries             │
│ [LAMBDA ARCH ← YOU ARE HERE: dual-layer merge]     │
│                                                      │
│ Query: total_revenue_last_hour                      │
│   = batch_result (T-3h to T-2h, accurate)          │
│   + stream_result (T-2h to now, real-time)         │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Daily reporting dashboard with Lambda Architecture:

00:00 each day: Spark batch job starts
  Reads ALL events from S3: 12 months of data (200TB)
  Processes: revenue, active users, conversion rates per
    hour/day/week
  Duration: 2 hours
  02:00: Batch views written to Cassandra + DynamoDB

08:00: Business analyst queries dashboard for "yesterday's
  revenue":
  Serving layer:
    Query batch view (Cassandra): accurate data through
      00:00
    Query stream view (Kafka Streams state store):
      real-time data 00:00-08:00
    Merge: $1.2M (batch, previous day) + $0.3M (stream,
      this morning)
    Display: $1.2M yesterday (accurate) | $0.3M today so
      far (real-time)

08:01: New order arrives:
  Speed layer: Kafka Streams processes within 100ms
  Stream view updated: $0.3M + $150 = $0.3015M
  Dashboard refreshes: $0.3015M today

23:59 yesterday's data has a correction (refund processed):
  Real-time: refund processed in stream view immediately
  Next batch run (02:00): reprocesses yesterday's data
    including refund
  Batch view corrected: $1.195M (was $1.2M)
  Dashboard after 02:00: shows corrected $1.195M for
    "yesterday"
  The correction took ~26 hours to appear in accurate
    batch view
```

---

### ⚖️ Comparison Table

|                        | Lambda Architecture                 | Kappa Architecture                   |
| ---------------------- | ----------------------------------- | ------------------------------------ |
| Pipelines              | 2 (batch + stream)                  | 1 (stream only)                      |
| Codebases              | 2 (dual maintenance)                | 1 (simpler)                          |
| Historical accuracy    | High (batch reprocessing)           | High (Kafka replay)                  |
| Real-time latency      | Low (speed layer)                   | Low                                  |
| Operational complexity | High                                | Medium                               |
| Use case               | Complex batch analytics + real-time | Streaming-expressible business logic |
| Trend                  | Declining                           | Preferred                            |

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                                                       |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Lambda guarantees eventually consistent results"            | Lambda's batch layer corrects stream errors EVENTUALLY - but the latency is hours. Business decisions made on stream-layer data may be wrong for hours. This is acceptable for analytics but not for financial commitments                    |
| "Lambda is dead / never use it"                              | Lambda is still useful for ML feature pipelines (complex batch features), large-scale historical analytics, and systems where batch infrastructure is already mature. Kappa is preferred for new systems, but Lambda has legitimate use cases |
| "The speed layer processes the same data as the batch layer" | The speed layer processes ONLY NEW data (since last batch run). It complements, not duplicates the batch layer. This is how the serving layer achieves: batch accuracy for old data + stream speed for new data                               |

---

### 🚨 Failure Modes & Diagnosis

**1. Batch-Stream Result Divergence**

**Symptom:** Batch shows 1M events, stream shows 1.05M events for the same time period. Business confused about which number is correct.

**Root Cause:** Logic divergence between batch and stream codebases. Common causes: deduplication (batch dedupes by messageId, stream doesn't), timezone handling (batch uses UTC, stream uses local time), late arrivals (batch includes late events in correct windows, stream discards them).

**Fix (short-term):** Add reconciliation job that compares batch vs stream outputs and logs discrepancies.

**Fix (long-term):** Migrate to Kappa Architecture (one codebase) or Apache Beam (single unified pipeline running on both Spark and Flink).

---

### 🔗 Related Keywords

**Prerequisites:** Batch vs Stream Processing, Apache Spark, Apache Flink

**Builds On This:** Kappa Architecture

**Related:** Kappa Architecture, Batch vs Stream Processing, Apache Spark

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ BATCH LAYER │ Spark/MR; all history; accurate; slow     │
│ SPEED LAYER │ Flink/Streams; recent data; real-time     │
│ SERVING     │ Merges batch + stream for queries         │
│ PROBLEM     │ Two codebases with same logic → diverge   │
│ DECLINE     │ Superseded by Kappa; Beam unifies both    │
│ STILL USE   │ ML features, complex batch analytics      │
│ DRUID/CASS  │ Common serving layer choices              │
│ vs KAPPA    │ Lambda: 2 pipes; Kappa: 1 stream-only    │
│ ONE-LINER   │ "Batch for accuracy + stream for speed + │
│             │  serving layer merges both; dual codebase │
│             │  is the fatal operational flaw"           │
└─────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) Explain the three layers of Lambda Architecture. What problem does the speed layer solve? What does the batch layer provide that the speed layer cannot? What is the "two codebases problem" and why does it matter?

**Q2.** (TYPE C - Design) A media company needs analytics for: (1) real-time content recommendations (< 500ms), (2) daily accurate engagement reports for billing, (3) historical trend analysis over 3 years. Design a Lambda Architecture for this, and then explain when you might prefer Kappa Architecture instead.
