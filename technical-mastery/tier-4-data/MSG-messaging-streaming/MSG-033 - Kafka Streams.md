---
version: 2
layout: default
title: "Kafka Streams"
parent: "Messaging & Event Streaming"
grand_parent: "Technical Mastery"
nav_order: 33
permalink: /technical-mastery/messaging-streaming/kafka-streams/
id: MSG-045
category: Messaging & Event Streaming
difficulty: ★★★
depends_on: Apache Kafka, Exactly-Once Semantics
used_by: KTable vs KStream, Event-Driven Architecture, Stream Processing
related: KTable vs KStream, Apache Kafka, Exactly-Once Semantics
tags:
  - kafka-streams
  - stream-processing
  - kstream
  - ktable
  - deep-dive
---

⚡ TL;DR - **Kafka Streams** is a **lightweight Java library** (no separate cluster) for building real-time stream processing applications that read from and write to Kafka - provides **KStream** (record stream), **KTable** (changelog/state), **stateful operations** (aggregations, joins) backed by embedded **RocksDB**, **exactly-once semantics** via transactions, and scales by adding partitions; runs as a normal Java app - no Flink/Spark cluster required.

| #546            | Category: Big Data & Streaming                                  | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------- | :-------------- |
| **Depends on:** | Apache Kafka, Exactly-Once Semantics                            |                 |
| **Used by:**    | KTable vs KStream, Event-Driven Architecture, Stream Processing |                 |
| **Related:**    | KTable vs KStream, Apache Kafka, Exactly-Once Semantics         |                 |

---

### 🔥 The Problem This Solves

**STREAM PROCESSING WITHOUT A SEPARATE CLUSTER:**
Apache Flink and Spark Streaming require separate dedicated clusters (JobManager, TaskManagers, Executors). For many use cases (enrich events, aggregate metrics, join streams), this overhead is unnecessary. Kafka Streams is a Java library - it runs inside your Spring Boot application, scales by deploying more instances, and requires only a Kafka cluster. No separate infrastructure, no new operational expertise, no cluster to manage.

---

### 📘 Textbook Definition

**Kafka Streams** is a client-side Java library for stream processing directly on Kafka data:

- **KStream**: represents an unbounded stream of records. Each record is an independent event (insert semantics).
- **KTable**: represents a changelog stream where the latest value per key is the "current state" (upsert semantics). Backed by a local RocksDB state store.
- **GlobalKTable**: replicated to ALL application instances (vs. KTable which is partitioned). Use for lookup tables that all instances need.
- **Topology**: the processing graph (DAG) of source processors, stream processors, and sink processors.
- **Tasks**: the parallelism unit. Each input partition → one task. Tasks distributed across all running instances.
- **State stores**: local RocksDB databases in each instance. Backed by changelog topics (compacted Kafka topics) for fault tolerance.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Kafka Streams = Kafka → [your Java code] → Kafka, with stateful operations (aggregation, joins), running as a library in your app - no separate cluster, scales with partition count.

**One analogy:**

> Kafka Streams is like a smart mail sorter built INTO your mailroom, not a separate sorting facility. When mail arrives (Kafka events): your mailroom software sorts, routes, and tracks it (stream processing) in real time, maintaining a ledger (KTable state store) of current deliveries. No shipping to an external sorting facility (Flink cluster). The mailroom scales by adding more sorters (app instances) - each handles some mail delivery routes (partitions).

**One insight:**
The most important conceptual distinction: **KStream vs KTable semantics**.

- **KStream (event/insert)**: every record is a new, distinct event. "User clicked," "order placed." No deduplication by key.
- **KTable (state/upsert)**: every record is an update to the current state for that key. "User profile updated" (latest value per user_id wins). Reading a KTable gives you the current state of all keys.
- **Join semantics differ dramatically**: KStream-KStream join = match events within a time window. KStream-KTable join = enrich each event with the current state. KTable-KTable join = join current states.

---

### 🔩 First Principles Explanation

**KAFKA STREAMS TOPOLOGY:**

```java
// Spring Boot + Kafka Streams example: Order enrichment pipeline
// Reads orders stream, enriches with user profile (KTable), writes
// enriched orders

@Configuration
@EnableKafkaStreams
public class StreamsConfig {

    @Bean(name = KafkaStreamsDefaultConfiguration.DEFAULT_STREAMS_CONFIG_BEAN_NAME)
    public KafkaStreamsConfiguration streamsConfig() {
        Map<String, Object> props = new HashMap<>();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG,
            "order-enrichment-service");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG,
            "kafka:9092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG,
            Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG,
            JsonSerde.class);

        // Exactly-once semantics:
        props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG,
            StreamsConfig.EXACTLY_ONCE_V2);

        // State store directory (RocksDB files):
        props.put(StreamsConfig.STATE_DIR_CONFIG,
            "/var/kafka-streams");

        // Commit interval: how often to commit processed offsets
        // (EOS: every record in txn)
        props.put(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG, 100);

        return new KafkaStreamsConfiguration(props);
    }
}

@Component
public class OrderEnrichmentTopology {

    @Autowired
    void buildPipeline(StreamsBuilder streamsBuilder) {

        // SOURCE 1: KStream - incoming orders (insert semantics: each
        // order is new)
        KStream<String, Order> ordersStream = streamsBuilder
            .stream("orders",
                Consumed.with(Serdes.String(),
                    JsonSerde.of(Order.class)));

        // SOURCE 2: KTable - user profiles (upsert semantics: latest
        // profile per user)
        // Backed by compacted topic "user-profiles"
        KTable<String, UserProfile> userProfilesTable = streamsBuilder
            .table("user-profiles",
                Consumed.with(Serdes.String(),
                    JsonSerde.of(UserProfile.class)),
                Materialized.<String,
                    UserProfile>as("user-profiles-store")
                    .withKeySerde(Serdes.String())
                    .withValueSerde(JsonSerde.of(UserProfile.class))
            );

        // JOIN: KStream-KTable join = enrich each order with current
        // user profile
        // Requires: ordersStream and userProfilesTable have SAME key
        // (userId)
        KStream<String, EnrichedOrder> enrichedOrders = ordersStream
            .selectKey((orderId, order) -> order.getUserId())
            // rekey by userId
            .join(
                userProfilesTable,
                (order, profile) -> EnrichedOrder.builder()
                    .order(order)
                    .userEmail(profile.getEmail())
                    .userTier(profile.getTier())
                    .build()
                // No windowing needed: KTable always has latest
                // profile
            );

        // SINK: write enriched orders to output topic
        enrichedOrders
            .selectKey((userId, enriched) -> enriched.getOrderId())
            // rekey back
            .to("enriched-orders", Produced.with(Serdes.String(),
                JsonSerde.of(EnrichedOrder.class)));
    }
}
```

**STATEFUL AGGREGATION:**

```java
// Count orders per user per 5-minute window
// Demonstrates: KStream → groupBy → windowed aggregation → KTable →
// output

KStream<String, Order> orders = streamsBuilder.stream("orders");

// 1. Rekey by userId (required for partitioned aggregation):
KStream<String, Order> byUser = orders
    .selectKey((orderId, order) -> order.getUserId());

// 2. Group by key (userId):
KGroupedStream<String, Order> grouped = byUser.groupByKey(
    Grouped.with(Serdes.String(), JsonSerde.of(Order.class))
);

// 3. Windowed aggregation: tumbling 5-minute windows
TimeWindows windows =
    TimeWindows.ofSizeWithNoGrace(Duration.ofMinutes(5));
// "NoGrace": no waiting for late events; use .ofSizeAndGrace(5min,
// 30sec) for grace period

KTable<Windowed<String>, Long> orderCountsPerWindow = grouped
    .windowedBy(windows)
    .count(Materialized.as("order-counts-store"));
// Each record in this KTable: key=(userId, window), value=count

// 4. Convert KTable to KStream for output:
orderCountsPerWindow
    .toStream()
    .map((windowedKey, count) -> KeyValue.pair(
        windowedKey.key(),  // userId
        new UserWindowCount(
            windowedKey.key(),
            windowedKey.window().startTime(),
            windowedKey.window().endTime(),
            count
        )
    ))
    .to("user-order-counts");

// Query state store (Interactive Queries - query without going to
// Kafka):
// ReadOnlyKeyValueStore<String, Long> store =
//   kafkaStreams.store(
//     StoreQueryParameters.fromNameAndType("order-counts-store",
//       QueryableStoreTypes.keyValueStore())
//   );
// Long currentCount = store.get("user-42");  // query from local
// RocksDB
```

**SCALING AND PARTITIONING:**

```
Kafka Streams parallelism = task count = partition count

Topic "orders" has 6 partitions:
  1 instance with 6 threads: handles 6 tasks (all 6
    partitions)
  2 instances with 3 threads each: each handles 3 tasks (3
    partitions each)
  6 instances with 1 thread each: each handles 1 task (1
    partition each)
  7 instances: 1 instance is idle (no partitions left)

Task assignment:
  Application ID = consumer group (Kafka Streams uses
    consumer group protocol)
  Each instance announces its available threads
  Kafka distributes tasks across instances (like consumer
    group partition assignment)

  Rebalance on instance crash:
  Remaining instances take over the crashed instance's
    tasks
  State stores: re-loaded from changelog topics (Kafka's
    compacted topics)
  Standby replicas: configure num.standby.replicas=1 → one
    warm standby per task
    → faster failover (standby already has recent state,
      minimal catch-up)
```

---

### 🧪 Thought Experiment

**WHEN TO USE KAFKA STREAMS vs FLINK vs SPARK:**

| Scenario                                     | Choice         | Reason                              |
| -------------------------------------------- | -------------- | ----------------------------------- |
| Event enrichment in existing Spring Boot app | Kafka Streams  | Library in existing app, no cluster |
| Real-time fraud detection (<10ms)            | Flink          | True streaming, lower latency       |
| Hourly batch ETL on S3                       | Spark          | Batch, S3 source                    |
| Counting events per window (1-min window)    | Kafka Streams  | Simple, built-in windowing          |
| Complex ML inference on streams              | Flink or Spark | Richer ML ecosystem                 |
| Pure Kafka-to-Kafka transformations          | Kafka Streams  | Native integration, simplest        |

---

### 🧠 Mental Model / Analogy

> Kafka Streams is like an assembly line in a factory. The raw materials (events from Kafka) flow in on a conveyor belt. Workers at each station (stream processors) perform their operation: one worker sorts by product type (groupBy), another counts how many passed through this hour (windowed count), a third checks inventory (KTable join). Finished products go on the output belt (write to Kafka). No external factory needed - the assembly line IS the factory. Scale: add more workers on more conveyors (instances, partitions).

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Kafka Streams = Java library for Kafka-to-Kafka stream processing. KStream (event stream) + KTable (current state). Stateful operations: aggregate, join, window. Scales by adding app instances (up to partition count). No separate cluster needed.

**Level 2:** KStream-KTable join: enrich stream events with current state (no windowing). KStream-KStream join: match events within a time window. Windowing: tumbling (fixed non-overlapping), sliding (overlapping), session (activity-bounded). State stores: local RocksDB, backed by compacted changelog Kafka topics.

**Level 3:** Task = one partition. Tasks distributed across all running instances. State stores per task - isolated by partition key (keys always go to same task via partitioning). Changelog backup: every state store write → appended to a compacted changelog Kafka topic → on restart, re-read changelog to restore state. Standby replicas: `num.standby.replicas=1` → one warm copy of each state store on another instance → fast failover.

**Level 4:** Kafka Streams Interactive Queries: expose your local state store via REST API. Kafka Streams knows which instance has the state for a given key (`queryMetadataForKey()` → host:port). Build a federated query layer: HTTP call to the right instance for any key's state without any external database. This is the "database inside Kafka Streams" pattern - used for real-time dashboards, per-entity state queries without additional DB infrastructure. Limitation: state is eventually consistent (within the commit interval). Not suitable for strong consistency requirements.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ KAFKA STREAMS TOPOLOGY (order enrichment)            │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Source: "orders" topic (6 partitions)               │
│         ↓                                            │
│ [selectKey: orderId→userId] (repartition if needed) │
│         ↓                                            │
│ [join with KTable "user-profiles"]                  │
│   ← local RocksDB: userId→UserProfile               │
│   ← backed by changelog topic "user-profiles"       │
│ [KAFKA STREAMS ← YOU ARE HERE: stateful join]        │
│         ↓                                            │
│ [map: rekey back to orderId]                        │
│         ↓                                            │
│ Sink: "enriched-orders" topic                       │
│                                                      │
│ Instance 1: handles orders P0, P1, P2               │
│ Instance 2: handles orders P3, P4, P5               │
│ RocksDB per instance: subset of user profiles (by partit│
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Spring Boot service with Kafka Streams (order enrichment):

Startup:
1. Application starts → KafkaStreams.start()
2. Joins consumer group "order-enrichment-service"
3. Assigned tasks: P0, P1, P2 (of 6 partitions)
4. Restores state for KTable "user-profiles" (partitions
  0-2):
   Reads from "user-profiles" changelog topic → populates
     local RocksDB
   (Takes 30s for 500K users on this instance's key range)
5. Ready to process

Runtime:
T=0ms: Order {orderId:abc, userId:42, amount:150} arrives
  in "orders" P1 offset 8901
T=1ms: selectKey: key changes to userId=42
T=2ms: join with KTable: lookup userId=42 in local RocksDB
  → UserProfile{email:..., tier:gold}
T=3ms: create EnrichedOrder{order:..., email:...,
  tier:gold}
T=4ms: write to "enriched-orders" P1 (hash(orderId) % 6 =
  3 → P3, different instance)
T=5ms: commit: atomic transaction (output written + input
  offset committed)

Instance crash (P0, P1, P2 orphaned):
1. Coordinator detects missing heartbeat
  (session.timeout.ms)
2. Rebalances: Instance 2 takes over P0, P1, P2
3. Instance 2: restores RocksDB state from changelog
  topics for P0, P1, P2
   (With num.standby.replicas=1: Instance 2 already has
     warm copy → fast restore)
4. Instance 2: resumes from last committed offset →
  at-most-once gap (EOS: exactly-once)
```

---

### ⚖️ Comparison Table

| Feature              | Kafka Streams                       | Apache Flink                    | Spark Streaming       |
| -------------------- | ----------------------------------- | ------------------------------- | --------------------- |
| Deployment           | Library in app (no cluster)         | Separate cluster                | Separate cluster      |
| Latency              | 1-100ms                             | 1-10ms                          | 100ms-1s              |
| State backend        | RocksDB (local)                     | RocksDB (local)                 | Memory/RocksDB        |
| Input/output         | Kafka only                          | Kafka, HDFS, S3, DB...          | Kafka, HDFS, S3...    |
| SQL support          | Basic (Kafka Streams Processor API) | Rich (Flink SQL)                | Rich (Spark SQL)      |
| Operational overhead | Low (just Java app)                 | High (cluster)                  | High (cluster)        |
| Best for             | Kafka-to-Kafka transformations      | Low-latency, complex topologies | Batch + streaming, ML |

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                                                                                     |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Kafka Streams requires a Kafka cluster per app" | Kafka Streams is a library - it runs in YOUR application process and uses your existing Kafka cluster. No separate deployment                                                                               |
| "KStream and KTable are interchangeable"         | KStream = event/insert semantics (each record is new). KTable = upsert semantics (latest per key). Joining them is asymmetric: KStream-KTable join enriches each event; it doesn't match events with events |
| "Kafka Streams can only process Kafka data"      | Kafka Streams reads and writes exclusively to Kafka topics. For non-Kafka sources/sinks, use Kafka Connect to bridge to/from Kafka, then use Kafka Streams for processing                                   |

---

### 🚨 Failure Modes & Diagnosis

**1. State Store Restoration Taking Too Long After Restart**

**Symptom:** Kafka Streams application takes 10-15 minutes to restart. During this time, processing is paused (tasks not assigned until state is restored).

**Root Cause:** Long changelog topics (state store backed by compacted topic with many records). Reading changelog from Kafka + populating RocksDB takes time.

**Fix:**

1. `num.standby.replicas=1`: maintain a warm standby on another instance → restore takes seconds (standby is already caught up).
2. `statestore.cache.max.bytes=52428800` (50MB): increase cache size → fewer flushes to RocksDB → faster processing.
3. Compact the changelog topic more aggressively: reduce `min.cleanable.dirty.ratio` → smaller changelog to replay.
4. For very large state (>50GB): use incremental RocksDB checkpoints to S3 → restore from checkpoint, not full changelog replay.

---

### 🔗 Related Keywords

**Prerequisites:** Apache Kafka, Exactly-Once Semantics

**Builds On This:** KTable vs KStream

**Related:** KTable vs KStream, Apache Kafka, Exactly-Once Semantics

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ KSTREAM     │ Event/insert stream (each record = new)   │
│ KTABLE      │ State/upsert (latest per key, RocksDB)    │
│ TASK        │ One partition → one task → one instance   │
│ STATE STORE │ Local RocksDB + changelog topic (backup)  │
│ EOS         │ EXACTLY_ONCE_V2 → atomic read+write       │
│ SCALING     │ More instances ≤ partition count          │
│ STANDBY     │ num.standby.replicas=1 → fast failover    │
│ JOINS       │ KStream-KTable (enrich) or KS-KS (window) │
│ vs FLINK    │ No cluster needed; Kafka-in-Kafka-out only│
│ ONE-LINER   │ "Stream processing as a library; Kafka→  │
│             │  Kafka with stateful ops; RocksDB state"  │
└─────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What is the difference between KStream and KTable in Kafka Streams? Give an example of when you would model a data source as each. How does Kafka Streams use changelog topics for fault tolerance?

**Q2.** (TYPE C - Design) Build a real-time inventory tracking system: Products topic (price/quantity updates) + Orders topic (order placements). Detect when inventory drops below threshold. Design the Kafka Streams topology, state stores, and alert mechanism.
