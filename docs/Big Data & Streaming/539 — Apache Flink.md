---
layout: default
title: "Apache Flink"
parent: "Big Data & Streaming"
nav_order: 539
permalink: /big-data-streaming/apache-flink/
number: "0539"
category: Big Data & Streaming
difficulty: ★★★
depends_on: Distributed Computing, Apache Kafka
used_by: Real-Time Stream Processing, Event-Driven Architecture, CDC
related: Spark Streaming, Apache Kafka, Windowing, State Backend (Flink)
tags:
  - apache-flink
  - stream-processing
  - stateful
  - exactly-once
  - deep-dive
---

# 539 — Apache Flink

⚡ TL;DR — Apache Flink is a **true streaming engine** (event-by-event processing, not micro-batch) with **sub-10ms latency**, **stateful computations** backed by RocksDB, **exactly-once semantics** via distributed snapshots (Chandy-Lamport algorithm), and rich **windowing** (tumbling, sliding, session); the gold standard for real-time applications where Spark Streaming's 100ms-1s latency is unacceptable — fraud detection, real-time metrics, CDC pipelines, gaming leaderboards.

| #539            | Category: Big Data & Streaming                                  | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Computing, Apache Kafka                             |                 |
| **Used by:**    | Real-Time Stream Processing, Event-Driven Architecture, CDC     |                 |
| **Related:**    | Spark Streaming, Apache Kafka, Windowing, State Backend (Flink) |                 |

---

### 🔥 The Problem This Solves

**SUB-SECOND LATENCY WITH LARGE STATE:**
A payment fraud detection system must block a fraudulent card within 50ms of the first suspicious transaction — not 500ms (Spark micro-batch minimum). Flink processes each event individually as it arrives, not in batches. Additionally, fraud detection requires maintaining per-user state (transaction history, velocity counts) that may span gigabytes — Flink's RocksDB state backend handles 100s of GB of state per TaskManager (operator process) with incremental checkpoints.

---

### 📘 Textbook Definition

**Apache Flink** is a distributed stream processing framework with:

- **True streaming**: processes one event at a time, no batching internally. Latency = milliseconds.
- **DataStream API**: typed event streams with operators (`map`, `filter`, `keyBy`, `window`, `process`).
- **Table API / Flink SQL**: declarative SQL on streaming data, statically compiled to DataStream operators.
- **Keyed State**: stateful operators maintain per-key state (ValueState, ListState, MapState, ReducingState, AggregatingState) stored in an embedded RocksDB instance.
- **Exactly-once semantics**: Flink takes distributed **checkpoints** (asynchronous snapshots of all operator state) using the Chandy-Lamport algorithm. On recovery: restore from last checkpoint and replay sources (Kafka offsets).
- **Windowing**: tumbling, sliding, and session windows on event time or processing time.
- **Watermarks**: advance event-time clock to handle late data; events arriving after watermark are dropped.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Flink = true event-by-event streaming (not micro-batch), per-key stateful processing with RocksDB, exactly-once via distributed snapshots — choose Flink when you need <100ms latency.

**One analogy:**

> Spark Streaming is like a post office that batches mail every 30 minutes (micro-batch). Flink is like a courier who delivers each letter the moment it arrives (true streaming). The Flink courier also keeps a personal notebook (keyed state) for each recipient: "John Smith: delivered 3 packages this week" — no need to look up a central database for every delivery.

**One insight:**
Flink's **keyed state** is what makes it uniquely powerful for stateful streaming. After `.keyBy("user_id")`, all events for a user always go to the same Flink operator instance, which maintains local RocksDB state for that user. No external database lookup needed for per-user aggregations — the state lives in the operator itself. For a fraud detection rule "block user if > 5 transactions/minute," the operator maintains a local counter per user_id, increments on each event, and emits a fraud alert when the counter exceeds 5. This eliminates the need for Redis or a database for this hot-path state.

---

### 🔩 First Principles Explanation

**FLINK CLUSTER ARCHITECTURE:**

```
Flink Cluster:
  [JobManager]                    ← single master per job
    - accepts job (DAG of operators)
    - schedules tasks to TaskManagers
    - triggers checkpoints
    - manages failover (reassigns tasks)

  [TaskManager 1] [TaskManager 2] ... [TaskManager N]
    - JVM process on each node
    - contains N task slots (each slot = 1 parallel pipeline thread)
    - hosts operator state (RocksDB or heap)
    - communicates with Kafka, HDFS, etc.

  Task slot: isolated unit of execution (memory partition within a TM)
  Parallelism: each operator runs on P tasks across P slots

  Example:
    4 TaskManagers × 8 slots = 32 available slots
    Job with parallelism=32: each operator has 32 parallel instances
    keyBy("user_id") → hash(user_id) % 32 → routes to 1 of 32 instances
    Instance #5 handles all events for users in its key range
```

**DATASTREAM API — FRAUD DETECTION:**

```java
// Flink Java DataStream API example: payment fraud detection
// Detect if a user has > 5 transactions in 1 minute → emit alert

StreamExecutionEnvironment env =
    StreamExecutionEnvironment.getExecutionEnvironment();
env.setParallelism(32);
env.enableCheckpointing(30_000);  // checkpoint every 30 seconds
env.getCheckpointConfig()
   .setCheckpointingMode(CheckpointingMode.EXACTLY_ONCE);
env.getCheckpointConfig()
   .setMinPauseBetweenCheckpoints(10_000);  // min 10s between checkpoints

// Source: Kafka consumer (replayable source required for EOS)
KafkaSource<String> source = KafkaSource.<String>builder()
    .setBootstrapServers("kafka:9092")
    .setTopics("payments")
    .setGroupId("fraud-detector")
    .setStartingOffsets(OffsetsInitializer.latest())
    .setValueOnlyDeserializer(new SimpleStringSchema())
    .build();

DataStream<String> rawStream = env.fromSource(
    source,
    WatermarkStrategy
        .<String>forBoundedOutOfOrderness(Duration.ofSeconds(10))  // 10s late tolerance
        .withTimestampAssigner((event, timestamp) -> parseTimestamp(event)),
    "Kafka Source"
);

// Parse JSON → Payment objects
DataStream<Payment> payments = rawStream.map(Payment::fromJson);

// KEY BY user_id: all events for same user → same operator instance (keyed state)
DataStream<FraudAlert> alerts = payments
    .keyBy(payment -> payment.getUserId())  // partition by user_id
    .process(new FraudDetector());          // stateful operator per user

// Sink: write alerts to Kafka (exactly-once via 2PC sink)
KafkaSink<String> alertSink = KafkaSink.<String>builder()
    .setBootstrapServers("kafka:9092")
    .setRecordSerializer(KafkaRecordSerializationSchema.builder()
        .setTopic("fraud-alerts")
        .setValueSerializationSchema(new SimpleStringSchema())
        .build())
    .setDeliveryGuarantee(DeliveryGuarantee.EXACTLY_ONCE)  // 2PC with Kafka transactions
    .build();

alerts.map(FraudAlert::toJson).sinkTo(alertSink);

env.execute("Fraud Detection Pipeline");
```

**STATEFUL OPERATOR — KEYED STATE:**

```java
// The stateful fraud detector operator:
public class FraudDetector extends KeyedProcessFunction<Long, Payment, FraudAlert> {

    // ValueState: one value per key (per user_id)
    private ValueState<Long> lastTransactionTime;
    private ValueState<Integer> transactionCount;

    @Override
    public void open(Configuration parameters) {
        // State descriptors: define state shape and serialization
        ValueStateDescriptor<Long> timeDesc =
            new ValueStateDescriptor<>("lastTxTime", Long.class);
        ValueStateDescriptor<Integer> countDesc =
            new ValueStateDescriptor<>("txCount", Integer.class);

        lastTransactionTime = getRuntimeContext().getState(timeDesc);
        transactionCount = getRuntimeContext().getState(countDesc);
    }

    @Override
    public void processElement(
            Payment payment,
            Context ctx,
            Collector<FraudAlert> out) throws Exception {

        long currentTime = payment.getTimestamp();
        Long lastTime = lastTransactionTime.value();
        Integer count = transactionCount.value();

        if (lastTime == null || currentTime - lastTime > 60_000) {
            // > 1 minute since last transaction: reset window
            transactionCount.update(1);
            lastTransactionTime.update(currentTime);
        } else {
            // Within the same 1-minute window
            int newCount = (count == null ? 0 : count) + 1;
            transactionCount.update(newCount);

            if (newCount > 5) {
                // FRAUD DETECTED: > 5 transactions in 1 minute
                out.collect(new FraudAlert(
                    payment.getUserId(),
                    currentTime,
                    "HIGH_VELOCITY: " + newCount + " transactions in 1 minute"
                ));
            }
        }

        // Register a timer: clean up state after 2 minutes of inactivity
        ctx.timerService().registerProcessingTimeTimer(currentTime + 120_000);
    }

    @Override
    public void onTimer(long timestamp, OnTimerContext ctx, Collector<FraudAlert> out) {
        // Timer fired: clean up stale state to prevent state growth
        transactionCount.clear();
        lastTransactionTime.clear();
    }
}
```

**FLINK CHECKPOINTING — CHANDY-LAMPORT:**

```
Flink Checkpoint Mechanism (simplified Chandy-Lamport barriers):

Normal flow:
  Kafka → [Source] → [Filter] → [keyBy] → [Process] → [Sink] → Delta Lake

Checkpoint triggered by JobManager:
  1. JobManager: inject CHECKPOINT BARRIER marker into each source stream
  2. Source operator: reads up to Kafka offset 15,237 → emits barrier

  3. Operators process events normally UNTIL they see the barrier
  4. When Filter receives barrier:
     a. Complete processing all events BEFORE barrier
     b. Snapshot its own state (async, non-blocking)
     c. Emit barrier to downstream operators

  5. When Process (keyed, stateful) receives barrier from ALL inputs:
     a. Wait until barriers from all parallel partitions arrive (align)
     b. Snapshot all keyed state (user_id → {count, lastTime} for all users)
     c. Async write state snapshot to S3/HDFS
     d. Emit barrier to Sink

  6. Sink: receives barrier → commits current transaction to Delta Lake
  7. JobManager: receives ACK from all operators → checkpoint N complete
  8. S3: now has snapshot of all operator states at Kafka offset 15,237

Recovery after failure:
  1. JobManager detects TaskManager failure (heartbeat timeout)
  2. Restart: restore all operators from last checkpoint N
     - Source: reset Kafka offset to 15,237 (replayable)
     - Process: reload all keyed state from S3 snapshot
     - Sink: state already committed (or will be replayed idempotently)
  3. Resume processing from Kafka offset 15,237

  No data lost, no data duplicated = exactly-once
```

---

### 🧪 Thought Experiment

**FLINK vs SPARK — CHOOSE WHICH ONE:**

| Scenario                               | Choose          | Reason                                      |
| -------------------------------------- | --------------- | ------------------------------------------- |
| Fraud detection, response in 50ms      | Flink           | Sub-millisecond event processing            |
| Daily batch ETL, large dataset         | Spark           | Batch processing, simpler operational model |
| IoT sensor alerting, 10ms threshold    | Flink           | True streaming, per-event processing        |
| Hourly aggregation reports             | Spark Streaming | Micro-batch sufficient, Spark ecosystem     |
| Session analytics with 30-min sessions | Flink           | Session windows + stateful operators        |
| One-time historical data migration     | Spark           | Batch processing, not a streaming concern   |

The decision boundary: **if latency requirement < 100ms, choose Flink. If > 100ms (most use cases), Spark Streaming is simpler.**

---

### 🧠 Mental Model / Analogy

> Flink is like a Formula 1 pit crew. Every event (tire change request) is processed the moment it arrives — no batching, no waiting. Each crew member (operator) has their own specialized tools (keyed state: torque wrench settings per car, history of past changes). The pit crew coordinator (JobManager) takes snapshots every 30 seconds (checkpoint: photos of all crew positions and car states). If a crew member is injured (TaskManager fails): restore from the last photo, replay the race from that moment. The result: a car back on track in seconds, with no tire change missed.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Flink = event-by-event stream processing (not micro-batch). Each event processed individually. Latency in milliseconds. Stateful (maintain per-key counters/maps). Exactly-once via checkpoints. Use when Spark Streaming's 100ms+ latency is too slow.

**Level 2:** KeyedProcessFunction: custom stateful logic per key. State types: ValueState (one value), ListState (list), MapState (map). Checkpoints: periodic snapshots of all operator state + Kafka offsets → recovery replays source from saved offset. Watermark: advance event-time clock, handle late events.

**Level 3:** Chandy-Lamport distributed snapshot: checkpoint barriers flow through the DAG; operators snapshot state when they see the barrier from all inputs. Asynchronous state snapshot: main processing thread continues while state is written to S3. Two-phase commit for sinks: Flink sends pre-commit to sink on checkpoint, final commit after JobManager confirms all operators checkpointed — enables exactly-once end-to-end.

**Level 4:** Flink's state backend options: HashMapStateBackend (in-heap JVM HashMap, fast but limited by GC), EmbeddedRocksDBStateBackend (off-heap LSM tree, handles 100s of GB, incremental checkpoints). Incremental checkpoints: only changed state blocks in RocksDB are written (not full snapshot) — 90%+ checkpoint size reduction for stable workloads. Flink 1.15+ introduced "generic incremental checkpointing" across all state backends. Network backpressure: Flink operators communicate via TCP-based network buffers. When a downstream operator is slow: input buffers fill → upstream operator blocks → natural backpressure propagation upstream to the source (Kafka consumer slows down automatically). This prevents OOM from unbounded queues.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ FLINK JOB EXECUTION                                  │
├──────────────────────────────────────────────────────┤
│                                                      │
│ [Kafka] → [Source x32] → [Filter x32] → [keyBy]    │
│                                    ↕ network shuffle │
│            [KeyedProcess x32] → [Sink x32] → Delta  │
│                   ↑                                  │
│            per-key RocksDB state                     │
│            (user_id → fraud_count)                   │
│  [FLINK ← YOU ARE HERE: event-by-event with state]  │
│                                                      │
│  Checkpoint every 30s: snapshot all state → S3      │
│  Recovery: reload state → replay Kafka from offset  │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Flink fraud detection job (parallelism=32):

T=0ms: Payment {user=42, amount=500, ts=10:00:00.100} arrives in Kafka
T=1ms: Source task 5 reads event, assigns event timestamp, emits watermark
T=2ms: Filter task 5: amount > 10? Yes → passes through
T=3ms: keyBy(user_id): hash(42) % 32 = 10 → routed to Process task 10
T=4ms: Process task 10: lookup ValueState for user_id=42 in RocksDB
        count=0 → increment to 1 → no alert → update state
T=5ms: Sink task 10: no alert to write (count < threshold)

T=5ms later: 5th payment for user_id=42 within 60 seconds
T=4ms: Process task 10: count=4 → increment to 5 → no alert

T=5ms later: 6th payment for user_id=42
T=4ms: Process task 10: count=5 → increment to 6 → FRAUD ALERT emitted

T=5ms: Sink: write alert to Kafka "fraud-alerts" topic via Kafka transaction
T=6ms: Alert delivered to fraud response system

Total end-to-end latency: ~5-10ms
(vs. Spark Streaming minimum: 100ms micro-batch interval)

T=30s: Checkpoint triggered by JobManager:
  All 32 Source tasks: save Kafka offset to S3
  All 32 Process tasks: async snapshot RocksDB state to S3
  Checkpoint complete in ~2s (incremental: only changed RocksDB blocks)
```

---

### ⚖️ Comparison Table

| Feature          | Apache Flink                | Spark Structured Streaming           |
| ---------------- | --------------------------- | ------------------------------------ |
| Processing model | True streaming (per event)  | Micro-batch (100ms-1s)               |
| Latency          | 1-10ms                      | 100ms-1s                             |
| State backend    | RocksDB (100s GB) / heap    | Memory / RocksDB (Spark 3.2+)        |
| Checkpoint       | Incremental (fast)          | Full batch checkpoint                |
| Exactly-once     | Yes (Chandy-Lamport + 2PC)  | Yes (checkpoint + idempotent sink)   |
| Windowing        | Rich (event-time, session)  | Good (tumbling, sliding)             |
| SQL              | Flink SQL (streaming-first) | Spark SQL (batch-first)              |
| Batch support    | Yes (same API)              | Yes (native batch)                   |
| Ecosystem        | Smaller                     | Larger (MLlib, SQL, Spark ecosystem) |

---

### ⚠️ Common Misconceptions

| Misconception                       | Reality                                                                                                                                                                                  |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Flink is always faster than Spark" | For batch processing, Spark and Flink are comparable. Flink's advantage is real-time streaming latency (<10ms). For hourly batch ETL, Spark is often simpler and just as fast            |
| "Flink checkpoints are expensive"   | With RocksDB incremental checkpoints, only changed state blocks are written. For stable workloads (slowly changing state), checkpoint time may be seconds even with 100GB of total state |
| "Flink can't do batch"              | Flink has a batch execution mode (sets bounded sources, switches to sort-based shuffle for efficiency). You can run the same Flink code in streaming or batch mode                       |

---

### 🚨 Failure Modes & Diagnosis

**1. Checkpoint Timeout — State Too Large**

**Symptom:** JobManager logs show `Checkpoint 1234 expired before completing`. Job restarts. After recovery, the same checkpoint times out again. Increasing checkpoint interval doesn't help.

**Root Cause:** State is too large to snapshot within the checkpoint timeout. Heap state backend: takes full snapshot → GC pressure + slow S3 write.

**Fix:** Switch to `EmbeddedRocksDBStateBackend` with incremental checkpointing:

```java
env.setStateBackend(new EmbeddedRocksDBStateBackend(true)); // true = incremental
env.getCheckpointConfig().setCheckpointStorage("s3://checkpoints/");
env.getCheckpointConfig().setCheckpointTimeout(120_000);  // 2 min timeout
```

Incremental: only changed RocksDB SST files are written — typically 90-99% smaller than full snapshot.

---

### 🔗 Related Keywords

**Prerequisites:** Distributed Computing, Apache Kafka
**Builds On This:** Windowing, Watermarks, State Backend (Flink), Checkpointing (Streaming)
**Related:** Spark Streaming, Apache Kafka, Windowing

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ MODEL       │ True streaming: per-event, not micro-batch │
│ LATENCY     │ 1-10ms (vs. Spark 100ms-1s)               │
│ KEYED STATE │ Per-key RocksDB state (GB-scale)           │
│ CHECKPOINT  │ Chandy-Lamport barriers → S3 snapshots     │
│ EOS         │ Checkpoint + 2PC sink (Kafka transactions) │
│ vs SPARK    │ Use Flink for <100ms; Spark for >100ms     │
│ BACKPRESSURE│ Natural: TCP buffers → upstream slows down │
│ STATE TYPES │ ValueState, ListState, MapState, ...       │
│ INCREMENTAL │ RocksDB: only changed blocks checkpointed  │
│ ONE-LINER   │ "Per-event stateful streaming; sub-10ms    │
│             │  latency with exactly-once checkpoints"    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) Explain Flink's checkpoint mechanism (Chandy-Lamport algorithm). How do checkpoint barriers work? What is the difference between at-least-once and exactly-once checkpointing in Flink?

**Q2.** (TYPE C — Design) Design a real-time leaderboard for an online game: 1M concurrent players, scores update every 10 seconds, leaderboard must show top-100 players with < 5ms update latency. Use Flink. Consider: keyed state, windowing, state backend, sink.
