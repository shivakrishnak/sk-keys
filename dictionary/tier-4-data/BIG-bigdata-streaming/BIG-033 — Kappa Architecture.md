---
layout: default
title: "Kappa Architecture"
parent: "Big Data & Streaming"
nav_order: 33
permalink: /big-data-streaming/kappa-architecture/
id: BIG-033
category: Big Data & Streaming
difficulty: ★★★
depends_on: Lambda Architecture, Batch vs Stream Processing, Apache Kafka
used_by: Real-Time Analytics, Data Engineering, Event-Driven Architecture
related: Lambda Architecture, Batch vs Stream Processing, Apache Flink
tags:
  - kappa-architecture
  - stream-only
  - kafka-replay
  - streaming
  - big-data
---

# BIG-033 — Kappa Architecture

⚡ TL;DR — **Kappa Architecture** (Jay Kreps, 2014) simplifies Lambda by **removing the batch layer** — a **single streaming pipeline** (Kafka + Flink/Kafka Streams) handles both real-time processing AND historical reprocessing; **historical reprocessing = replay Kafka events** from the beginning with new code; one codebase, one operational system; eliminates Lambda's dual-codebase problem; requires Kafka with sufficient retention (or S3 tiered storage); **preferred for most modern streaming systems** where business logic fits streaming semantics.

| #558            | Category: Big Data & Streaming                                   | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------- | :-------------- |
| **Depends on:** | Lambda Architecture, Batch vs Stream Processing, Apache Kafka    |                 |
| **Used by:**    | Real-Time Analytics, Data Engineering, Event-Driven Architecture |                 |
| **Related:**    | Lambda Architecture, Batch vs Stream Processing, Apache Flink    |                 |

---

### 🔥 The Problem This Solves

**LAMBDA'S TWO-CODEBASE PROBLEM:**
Lambda Architecture requires maintaining identical business logic in two different systems (Spark batch + Flink stream). When logic changes, you update both, test both, deploy both, and hope they produce the same answers. In practice, they diverge. Kappa Architecture's insight: "If streaming can handle historical reprocessing by replaying Kafka events, we don't NEED a separate batch layer." One pipeline, one codebase, one operational concern. Streaming IS the batch layer (just faster).

---

### 📘 Textbook Definition

**Kappa Architecture** is a stream-processing architecture with two components:

1. **Immutable event log** (Kafka with long retention or S3 offloading): all events stored durably; the single source of truth.
2. **Streaming processor** (Flink, Kafka Streams): processes events in real time AND can replay from beginning for reprocessing.

**Reprocessing algorithm:**

1. Deploy new version of streaming code (v2).
2. Start v2 processor reading from Kafka `offset=0` (beginning).
3. V2 writes results to a NEW output topic/table.
4. Once v2 catches up to real-time: switch serving layer to v2 output.
5. Decommission v1 processor and old output table.

No separate batch system. Historical correctness achieved by replaying the event log, not by running a different batch system.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Kappa = one streaming pipeline for both real-time AND historical; "batch" = replay Kafka from beginning with new code; one codebase eliminates Lambda's dual-maintenance problem.

**One analogy:**

> Git history is Kappa Architecture for code. You have ONE repository (Kafka topic = immutable event log). If you make a mistake (wrong business logic), you don't run a parallel "batch Git process" — you replay: check out the commit, apply your fix, rebuild. Your streaming code IS the "batch" process — it just processes all commits (events) since the beginning. Switch the "current state" (serving layer) to the rebuilt result.

**One insight:**
Kappa works because Kafka is an **immutable, replayable log**. This is the key insight: if your event source can replay events from any point, you don't need a separate batch layer. The stream processor IS the batch processor when pointed at the beginning of the log. This means Kappa requires: (1) Kafka retention that covers your reprocessing needs (30 days, 1 year, or infinite with tiered storage), and (2) business logic expressible in streaming semantics (no iterative algorithms, no global sorts).

---

### 🔩 First Principles Explanation

**KAPPA ARCHITECTURE IMPLEMENTATION:**

```
KAPPA COMPONENTS:

Component 1: Kafka as immutable log (single source of truth)
  - Topic: "order-events" (all orders ever placed)
  - Retention: 90 days (or infinite with Confluent Tiered Storage / Apache Pulsar)
  - No separate HDFS/S3 raw store needed (Kafka IS the raw store)
  - Events are immutable, append-only: never modified after writing

Component 2: Single Streaming Pipeline
  - Language: Flink (or Kafka Streams for simpler cases)
  - Processes: ALL events (real-time) OR ALL events from beginning (reprocessing)
  - Output: materialized views in downstream systems (DB, Redis, Elasticsearch)
```

```java
// SINGLE FLINK JOB: handles both real-time and historical processing

public class RevenueComputationJob {

    public static void main(String[] args) throws Exception {

        // Parameter: start from beginning or latest
        ParameterTool params = ParameterTool.fromArgs(args);
        String startMode = params.get("start-mode", "latest");
        // "latest" → real-time processing (normal mode)
        // "earliest" → historical reprocessing (replay mode)

        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        // Configure Kafka source start offset:
        KafkaSource<OrderEvent> source;
        if ("earliest".equals(startMode)) {
            // REPROCESSING: read ALL events from the beginning
            source = KafkaSource.<OrderEvent>builder()
                .setBootstrapServers("kafka:9092")
                .setTopics("order-events")
                .setGroupId("revenue-computation-v2")  // NEW group ID for v2!
                .setStartingOffsets(OffsetsInitializer.earliest())  // FROM BEGINNING
                .setValueOnlyDeserializer(new OrderEventDeserializer())
                .build();
        } else {
            // NORMAL: process only new events
            source = KafkaSource.<OrderEvent>builder()
                .setBootstrapServers("kafka:9092")
                .setTopics("order-events")
                .setGroupId("revenue-computation-v1")
                .setStartingOffsets(OffsetsInitializer.committedOffsets(OffsetResetStrategy.LATEST))
                .setValueOnlyDeserializer(new OrderEventDeserializer())
                .build();
        }

        DataStream<OrderEvent> orders = env.fromSource(
            source,
            WatermarkStrategy.<OrderEvent>forBoundedOutOfOrderness(Duration.ofMinutes(2))
                .withTimestampAssigner((e, t) -> e.getEventTimestamp()),
            "kafka-orders"
        );

        // SAME BUSINESS LOGIC for both real-time and historical:
        DataStream<HourlyRevenue> hourlyRevenue = orders
            .filter(order -> "COMPLETED".equals(order.getStatus()))
            .keyBy(order -> order.getHour())  // "2024-01-15T14"
            .window(TumblingEventTimeWindows.of(Time.hours(1)))
            .process(new RevenueWindowProcessor());

        // Write to output: for reprocessing, write to DIFFERENT table
        String outputTable = startMode.equals("earliest") ?
            "hourly_revenue_v2" : "hourly_revenue_v1";
        hourlyRevenue.addSink(new JdbcSink<>(outputTable));

        env.execute("RevenueComputation-" + startMode);
    }
}
```

**KAPPA REPROCESSING WORKFLOW:**

```
WHEN TO REPROCESS:
  1. Bug found: revenue calculation was double-counting refunds
  2. New business rule: exclude orders from test accounts
  3. New metric added: unique products per hour

REPROCESSING STEPS:

Step 1: Deploy v2 code
  git commit -m "fix: exclude refunded orders from revenue calculation"

Step 2: Start v2 job in reprocessing mode
  flink run -jar revenue-job.jar --start-mode=earliest --group-id=revenue-v2
  → v2 reads from Kafka offset=0 (all 90 days of history)
  → Writes to "hourly_revenue_v2" table
  → v1 continues running, serving current traffic → NO DOWNTIME

Step 3: Monitor catch-up
  flink job status → consumer lag for revenue-v2 group
  kafka-consumer-groups.sh --group revenue-v2 --describe | grep LAG
  → Initially: 90 days × 1M events/day = 90M events behind
  → Flink processes at ~5M events/min → catches up in ~18 minutes

Step 4: v2 catches up to real-time (lag = 0)
  → Switch serving layer: app reads from hourly_revenue_v2
  → This is a config/feature flag change, no downtime

Step 5: Decommission v1
  kubectl delete deployment revenue-v1-flink
  DROP TABLE hourly_revenue_v1;  -- after verification

Total migration time: ~20 minutes
Downtime: ZERO (v1 runs until v2 catches up)
Historical data corrected: YES (all 90 days corrected)
```

**KAPPA WITH TIERED STORAGE (INFINITE RETENTION):**

```yaml
# Problem: 90-day Kafka retention isn't enough for 5-year historical analysis

# Solution 1: Confluent Tiered Storage
# - Kafka moves old segments to S3 automatically
# - Old events still readable via Kafka API
# - "Infinite" Kafka retention at S3 cost (~$23/TB/month)

# Confluent Cloud / MSK configuration:
confluent.tier.feature: true
confluent.tier.s3.bucket: my-kafka-tiered-storage
confluent.tier.s3.region: us-east-1
log.retention.ms: -1 # infinite (segments offloaded to S3)


# Solution 2: Kafka + S3 (separate)
# Producers write to both Kafka (7-day retention for real-time) AND S3 (infinite)
# Real-time: Kafka source
# Historical replay: S3 source → Flink batch mode
# Downside: two sources → back to Lambda-like complexity for historical

# Solution 3: Apache Pulsar
# Built-in tiered storage: Pulsar broker + BookKeeper + S3 offloading
# Natively supports infinite retention at S3 pricing
# Alternative to Kafka for Kappa-pure architectures
```

---

### 🧪 Thought Experiment

**WHAT CAN'T KAPPA DO?**

Kappa struggles with:

1. **Iterative algorithms** (PageRank, collaborative filtering): require multiple passes over all data. Streaming processes data once per pass. Spark's distributed iterative computation (MLlib) doesn't have a direct streaming equivalent.
2. **Global sorts**: sorting 10TB of data requires batch semantics. Streaming can partition-sort but not global.
3. **Very large historical joins**: joining two 10-year event streams requires either very large state (RocksDB for entire 10 years of data) or batch semantics.
4. **Non-Kafka sources**: if historical data is only in S3 (not in Kafka), you can't use Kafka replay for Kappa. You need batch reads.

For these cases, Lambda (or a hybrid) remains relevant. Kappa is best when: business logic is streaming-expressible AND Kafka has sufficient retention.

---

### 🧠 Mental Model / Analogy

> Kappa Architecture is like a DVR (digital video recorder) for your business. Every event is recorded (Kafka). Your "real-time TV" (streaming pipeline) watches live. If you miss something or want to re-watch (bug fix / new analysis), you rewind to any point and replay. The same TV and remote (one streaming codebase) work for both live viewing and replays. No separate "movie theater" (batch cluster) needed just for replay.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Kappa = stream-only architecture. Kafka = immutable log. Reprocessing = replay from beginning with new code. One codebase vs Lambda's two. Requires long Kafka retention.

**Level 2:** Reprocessing workflow: new version → read from offset=0 with new group ID → write to new output → catch up → switch serving layer → decommission old. Zero downtime migration. Same streaming code for both real-time and historical.

**Level 3:** Kafka retention limits reprocessing range. Solutions: Confluent Tiered Storage (S3-backed infinite retention), Apache Pulsar (native tiered storage), separate S3 archive + batch fallback for very old data. Kappa doesn't replace batch for iterative ML algorithms or complex historical joins — hybrid is sometimes needed.

**Level 4:** Kappa + Delta Lake / Apache Iceberg: stream writes events to Delta table (on S3) with ACID semantics. Reprocessing = Spark batch reads Delta table (not Kafka). "Batch layer" is just a Spark query on the same Delta table the stream writes to — no separate pipeline. This blurs the Lambda/Kappa distinction: one storage layer (Delta), one batch query, one streaming pipeline. Modern "Lakehouse" architecture (Databricks Delta Live Tables) is a natural evolution of Kappa thinking.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ KAPPA ARCHITECTURE                                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Kafka "order-events" (90-day retention)             │
│ [offset=0 ... offset=50M (90 days ago) ... offset=99M (now)]│
│                                                      │
│ V1 Streaming Job (revenue-v1):                      │
│   Reads from offset=99M (latest)                    │
│   Writes to "hourly_revenue_v1" → serves traffic    │
│                                                      │
│ V2 Streaming Job (revenue-v2, bug fixed):           │
│   Reads from offset=0 (replay all 90 days)          │
│   Writes to "hourly_revenue_v2"                     │
│ [KAPPA ← YOU ARE HERE: stream-only replay approach] │
│                                                      │
│ After v2 catches up (lag=0):                       │
│ Serving layer: switch → "hourly_revenue_v2"        │
│ Decommission: v1 job + hourly_revenue_v1 table     │
│                                                      │
│ One codebase. Zero downtime. Historical corrected.  │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Kappa Architecture for real-time analytics:

Day 1: Launch
  revenue-v1 runs: processes live orders → hourly_revenue_v1
  Kafka "order-events": retention=90 days

Day 45: Bug discovered — refunds double-counted
  Developer fixes RevenueWindowProcessor.java
  CI/CD: builds revenue-v2.jar

Day 45, 14:00: Deploy v2 in replay mode
  flink run revenue-v2.jar --start-mode=earliest --group=revenue-v2
  v2 reads from day 1 (offset=0): 45 days × 2M orders/day = 90M events
  Flink parallelism=20: processes 10M events/min → catchup in 9 minutes
  v1 continues serving → no impact to users

Day 45, 14:09: v2 lag = 0 (caught up to real-time)
  Dashboard config: switch from hourly_revenue_v1 → hourly_revenue_v2
  All 45 days of revenue data: corrected (no double-counted refunds)
  Users see: corrected historical data immediately

Day 45, 14:10: Decommission v1
  Stop revenue-v1 flink job
  DROP TABLE hourly_revenue_v1 (after verification)

Result:
  - Zero downtime during migration
  - 45 days of history corrected automatically
  - One codebase (no batch equivalent to maintain)
  - Total migration time: 9 minutes of catch-up + seconds for switch
```

---

### ⚖️ Comparison Table

|                         | Kappa               | Lambda                          |
| ----------------------- | ------------------- | ------------------------------- |
| Pipelines               | 1 (stream only)     | 2 (batch + stream)              |
| Codebases               | 1                   | 2                               |
| Historical reprocessing | Kafka replay        | Re-run batch job                |
| Operational complexity  | Medium              | High                            |
| Retention requirement   | High (weeks-months) | Low (stream short retention ok) |
| Iterative ML            | Limited             | Good (Spark MLlib)              |
| Trend                   | Growing (preferred) | Declining                       |

---

### ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                                                                                                                                                                     |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Kappa can't do historical analytics"     | Kappa CAN do historical analytics — by replaying Kafka from the beginning. The streaming job becomes the "batch job" when reading from offset=0. It's slower than Spark for complex analytics, but works for most use cases |
| "Kappa requires infinite Kafka retention" | Kappa requires Kafka retention that covers your reprocessing needs. 30 days is often sufficient. For longer history: Confluent Tiered Storage or S3 archiving with a fallback batch path                                    |
| "Kappa is always better than Lambda"      | Kappa is better for operational simplicity and most streaming use cases. Lambda remains better for: iterative ML, complex batch analytics (SQL over petabytes), and systems with non-Kafka event sources                    |

---

### 🚨 Failure Modes & Diagnosis

**1. Reprocessing Job Can't Catch Up (Too Slow)**

**Symptom:** v2 replay job started 2 hours ago but is still processing data from 30 days ago. At current rate, will take 48 hours to catch up.

**Root Cause:** Processing rate (events/sec) is less than required rate to catch up in acceptable time. This can happen if: (1) job parallelism is too low, (2) expensive operations (DB lookups per event), (3) backpressure from output sinks.

**Fix:**

1. Increase Flink parallelism: `env.setParallelism(40)` instead of 20 → 2× faster.
2. Optimize per-event DB calls: batch DB writes, use local state stores instead of external DB per event.
3. Use `allowedLateness(0)` during replay: no waiting for late events → windows close faster.
4. Scale Flink task managers: add more nodes to Flink cluster.
5. Consider running v1 and v2 simultaneously (v1 serves traffic, v2 reprocesses) until catch-up complete. Zero downtime is the goal.

---

### 🔗 Related Keywords

**Prerequisites:** Lambda Architecture, Batch vs Stream Processing, Apache Kafka
**Builds On This:** Event-Driven Architecture
**Related:** Lambda Architecture, Batch vs Stream Processing, Apache Flink

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY INSIGHT │ Streaming = batch when reading from start │
│ REPLAY      │ Start new version at offset=0, new group │
│ ZERO DOWN   │ Old version serves while new replays     │
│ CATCHUP     │ Switch serving layer when lag=0          │
│ ONE CODE    │ Same pipeline for real-time & historical  │
│ REQUIRES    │ Long Kafka retention (or tiered storage)  │
│ LIMIT       │ No iterative ML, no global sorts          │
│ vs LAMBDA   │ 1 pipeline vs 2; simpler ops; preferred  │
│ PULSAR      │ Alternative with native infinite retention│
│ ONE-LINER   │ "Eliminate batch layer; Kafka replay IS  │
│             │  the batch job; one codebase for both"   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What is the key insight behind Kappa Architecture? How does it achieve historical reprocessing without a separate batch layer? What are the requirements for Kafka to support Kappa Architecture?

**Q2.** (TYPE C — Design) A financial services company runs Lambda Architecture (Spark batch + Flink streaming). The team spends 30% of sprint time maintaining two codebases with equivalent logic. Design a migration to Kappa Architecture: what prerequisites must be met, how do you migrate without downtime, what limitations must be accepted, and how do you handle 5 years of historical data that exceeds Kafka retention?
