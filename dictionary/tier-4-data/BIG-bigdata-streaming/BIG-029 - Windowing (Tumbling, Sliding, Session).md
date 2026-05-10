---
version: 2
layout: default
title: "Windowing (Tumbling, Sliding, Session)"
parent: "Big Data & Streaming"
grand_parent: "Technical Dictionary"
nav_order: 29
permalink: /big-data-streaming/windowing/
id: BIG-029
category: Big Data & Streaming
difficulty: ★★★
depends_on: Watermark, Event Time vs Processing Time, Apache Flink
used_by: Stream Processing Aggregations, Fraud Detection, Analytics
related: Watermark, Event Time vs Processing Time, Apache Flink
tags:
  - windowing
  - tumbling-window
  - sliding-window
  - session-window
  - stream-processing
---

# BIG-029 - Windowing (Tumbling, Sliding, Session)

⚡ TL;DR - **Windowing** groups streaming events into **bounded time intervals** for aggregation - **Tumbling** (fixed non-overlapping, e.g., every 5 min), **Sliding/Hopping** (fixed overlapping, e.g., last 5 min every 1 min), **Session** (variable-length, ends after N seconds of inactivity per key); window semantics apply to **event time** (when event occurred) not processing time; combined with **watermarks** (late event tolerance) to determine when a window closes and results are emitted.

| #554            | Category: Big Data & Streaming                             | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------- | :-------------- |
| **Depends on:** | Watermark, Event Time vs Processing Time, Apache Flink     |                 |
| **Used by:**    | Stream Processing Aggregations, Fraud Detection, Analytics |                 |
| **Related:**    | Watermark, Event Time vs Processing Time, Apache Flink     |                 |

---

### 🔥 The Problem This Solves

**AGGREGATING UNBOUNDED STREAMS REQUIRES TEMPORAL BOUNDS:**
Counting "all orders ever" grows without bound. Useful analytics require bounded questions: "orders per hour," "unique users per 5 minutes," "revenue per day." But streaming data arrives continuously, often out of order. You can't wait for "all data for this hour" - some events arrive late. Windowing provides the temporal boundary: "process all events that occurred between 14:00 and 15:00, allowing up to 30 seconds of late arrivals." Windows allow you to apply bounded aggregations (COUNT, SUM, AVG) to unbounded event streams.

---

### 📘 Textbook Definition

**Windowing** divides an infinite stream of events into finite, bounded collections ("windows") based on time. Three main types:

1. **Tumbling Window** (Fixed, non-overlapping): Equal-sized windows that don't overlap. Window [0:00-5:00), [5:00-10:00), [10:00-15:00)... Each event belongs to exactly ONE window.

2. **Sliding (Hopping) Window** (Fixed, overlapping): Windows of fixed size that advance by a smaller step. Window size=5min, slide=1min: [0:00-5:00), [1:00-6:00), [2:00-7:00)... Each event may belong to MULTIPLE windows. Also called "hopping window" in some frameworks.

3. **Session Window** (Variable, per-key): Groups events per key separated by gaps longer than a timeout. If user-42 is active from 14:00-14:05 then inactive for 10 min (> timeout=5 min): session window closes at 14:05. New session starts at 14:15 if activity resumes. Window size varies per user per session.

All three can be applied to **event time** (when the event happened) or **processing time** (when the event arrived at the processor).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Windowing = group events into time buckets; tumbling = non-overlapping fixed buckets; sliding = overlapping buckets; session = activity-bounded per entity.

**One analogy:**

> **Tumbling**: a bank statement, monthly. January's transactions are in the January statement, February's in February's - no overlap.
> **Sliding**: a 7-day rolling average in a stock ticker - updated every day, always covering the last 7 days. Each day's price appears in 7 consecutive windows.
> **Session**: a Google Analytics "session" - all page views during a continuous visit. Session ends after 30 minutes of inactivity. Next visit = new session.

**One insight:**
The choice between event time and processing time windows is critical. **Processing time** is simpler (no watermarks needed) but unreliable for late-arriving data. If your IoT sensor has spotty connectivity and sends events 5 minutes late, a processing-time window will put those events in the "wrong" hour. **Event time** windows are semantically correct (events grouped by when they actually happened) but require watermarks to know when a window is "done enough" to emit results. Always prefer event time for business metrics; use processing time only for operational metrics where latency matters more than accuracy.

---

### 🔩 First Principles Explanation

**WINDOWING IN FLINK:**

```java
// Apache Flink: Tumbling, Sliding, Session windows with event time

DataStreamSource<Order> orders = env.fromSource(kafkaSource,
    WatermarkStrategy.<Order>forBoundedOutOfOrderness(Duration.ofSeconds(10))
        .withTimestampAssigner((order, ts) -> order.getTimestamp()),
    "kafka-orders");

// 1. TUMBLING WINDOW: 5-minute non-overlapping
// Aggregates: total orders and revenue per product per 5-minute window
orders
    .keyBy(order -> order.getProductId())
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .aggregate(new OrderAggregator())
    .print();

// Resulting windows for productId="P1":
// [00:00, 00:05): count=42, revenue=$4200
// [00:05, 00:10): count=38, revenue=$3800
// [00:10, 00:15): count=55, revenue=$5500
// Each 5-minute period: separate aggregation, results emitted when window closes

// 2. SLIDING WINDOW: 10-minute window, slide every 2 minutes
// Overlapping: event at T=4 appears in windows [0:00-10:00), [2:00-12:00), ..., [4:00-14:00)
// = 5 windows (10/2 = 5 overlapping windows per event)
orders
    .keyBy(order -> order.getProductId())
    .window(SlidingEventTimeWindows.of(Time.minutes(10), Time.minutes(2)))
    .aggregate(new OrderAggregator())
    .print();
// Higher overhead: each event stored in (windowSize/slideSize) = 5 windows simultaneously
// Use for: rolling averages, trend detection

// 3. SESSION WINDOW: closes after 5 minutes of inactivity per user
// Merges adjacent events close together into one session
orders
    .keyBy(order -> order.getUserId())
    .window(EventTimeSessionWindows.withGap(Time.minutes(5)))
    .aggregate(new SessionAggregator())
    .print();
// User active 14:00-14:07 then inactive until 14:15:
// Session 1: [14:00, 14:07) → aggregated
// Session 2: [14:15, ...] → new session (gap > 5 min)

// LATE DATA HANDLING: events arriving after window closes
orders
    .keyBy(order -> order.getProductId())
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .allowedLateness(Time.minutes(2))  // keep window open 2 extra minutes for late events
    .sideOutputLateData(lateOutputTag)  // events beyond 2min → side output (don't discard)
    .aggregate(new OrderAggregator());
// Window [00:00, 00:05):
//   Closed at 00:05 (watermark passes 00:05)
//   Still accepts late events until 00:07 (allowedLateness=2min)
//   Events after 00:07 → sideOutput (can inspect separately)
```

**WINDOWING IN KAFKA STREAMS:**

```java
// Kafka Streams: Tumbling, Hopping (sliding), Session windows
StreamsBuilder builder = new StreamsBuilder();
KStream<String, Order> orders = builder.stream("orders");

// 1. TUMBLING WINDOW (Kafka Streams: TumblingWindows)
orders
    .groupBy((key, order) -> order.getProductId(),
        Grouped.with(Serdes.String(), orderSerde))
    .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofMinutes(5)))
    .count(Materialized.as("product-order-counts"))
    .toStream()
    .to("product-order-counts-output");

// 2. HOPPING WINDOW (Sliding in Kafka Streams terminology)
orders
    .groupBy((key, order) -> order.getUserId())
    .windowedBy(
        TimeWindows.ofSizeAndGrace(Duration.ofMinutes(10), Duration.ofMinutes(1))
            .advanceBy(Duration.ofMinutes(2))  // advance every 2 min
    )
    .count();

// 3. SESSION WINDOW
orders
    .groupBy((key, order) -> order.getUserId())
    .windowedBy(SessionWindows.ofInactivityGapWithNoGrace(Duration.ofMinutes(5)))
    .count(Materialized.as("user-session-order-counts"));

// GRACE PERIOD vs ALLOWED LATENESS:
// Kafka Streams: Grace period = how long to wait for late events
//   ofSizeWithNoGrace: no late events allowed (emit immediately when watermark passes)
//   ofSizeAndGrace(5min, 30sec): accept events up to 30s late

// Query state store for current window counts:
ReadOnlyWindowStore<String, Long> store = kafkaStreams.store(
    StoreQueryParameters.fromNameAndType(
        "product-order-counts",
        QueryableStoreTypes.windowStore()
    )
);
// Query a specific window:
WindowStoreIterator<Long> it = store.fetch("P1",
    Instant.parse("2024-01-15T14:00:00Z"),
    Instant.parse("2024-01-15T14:05:00Z"));
while (it.hasNext()) {
    KeyValue<Long, Long> next = it.next();
    System.out.println("Window time: " + next.key + ", count: " + next.value);
}
```

**WINDOW MATHEMATICS:**

```
TUMBLING window (size=5min):
  Events: M1@0:01, M2@0:03, M3@0:04, M4@0:07, M5@0:09, M6@0:11
  Windows:
    [0:00-0:05): M1, M2, M3 → count=3
    [0:05-0:10): M4, M5 → count=2
    [0:10-0:15): M6 → count=1
  Each event: in EXACTLY 1 window

SLIDING window (size=5min, slide=2min):
  Events: M1@0:01, M2@0:03, M3@0:04
  Windows:
    [0:00-0:05): M1, M2, M3 → count=3
    [0:02-0:07): M1*, M2, M3 → count=3  (* M1@0:01 NOT in [0:02-0:07), M2@0:03 IS)
    Actually: M2@0:03, M3@0:04 in [0:02-0:07): count=2
    [0:04-0:09): M3 in [0:04-0:09)? M3@0:04 is at boundary: count=1
  Each event: may be in MULTIPLE windows (windowSize/slideSize = 5/2 = ~2.5 windows avg)

SESSION window (gap=5min, per user):
  User-A events: M1@0:01, M2@0:02, M3@0:04, [gap], M4@0:15, M5@0:16
  Sessions for User-A:
    Session 1: [0:01 - 0:04+gap]: M1, M2, M3 (gap after M3 > 5min) → closes ~0:09
    Session 2: [0:15 - 0:16+gap]: M4, M5 → closes ~0:21
  Window size: VARIABLE (determined by activity gaps, not fixed duration)
```

---

### 🧪 Thought Experiment

**TUMBLING vs SESSION FOR USER ENGAGEMENT:**

Goal: measure user engagement on a website.

**Tumbling window (1-hour)**: user visits at 14:01 and 14:59 → same 1-hour bucket. But 58 minutes apart - were they in one "session"? Also, what if user spans midnight: 23:50 and 00:10 → different windows (different days). Tumbling windows are oblivious to user behavior patterns.

**Session window (30-min inactivity)**: user visits at 14:01, 14:15, 14:30 (gap=15min < 30min → same session). Then visits at 15:15 (gap=45min > 30min → new session). Window accurately reflects one continuous engagement period. This is why Google Analytics uses session windows, not tumbling.

---

### 🧠 Mental Model / Analogy

> **Tumbling**: Time zones on a clock. Every hour starts a new reporting period, regardless of what's happening. Hour 14: everything from 14:00 to 14:59. Clean, predictable, no overlap.
> **Sliding**: A moving spotlight. Wherever the spotlight is pointing covers 5 minutes of time. Every 1 minute, the spotlight shifts 1 minute forward. Some events are caught in multiple spotlights.
> **Session**: A conversation. Starts when someone speaks, ends when the room has been silent for 5 minutes. Duration varies - could be 2 minutes or 2 hours. Each person has their own independent conversation timer.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Tumbling (fixed, non-overlapping), Sliding (fixed, overlapping, each event in multiple windows), Session (activity-based gap, per key). All can use event time or processing time. Use watermarks with event time to determine when windows close.

**Level 2:** Flink: `TumblingEventTimeWindows`, `SlidingEventTimeWindows`, `EventTimeSessionWindows`. Kafka Streams: `TimeWindows.ofSizeWithNoGrace()`, `advanceBy()`, `SessionWindows.ofInactivityGap()`. Late data: `allowedLateness` (Flink) or `Grace` period (Kafka Streams). Side output for events beyond allowed lateness.

**Level 3:** Window state: each open window maintains state (partial aggregation) in RocksDB. For tumbling 5-min with 1 hour of active data: 12 concurrent open windows in state. Sliding windows (windowSize/slideSize) windows per event - higher state and CPU cost. Session windows: dynamically merge when events bridge two adjacent session windows (Flink: SessionWindowMerger). Window triggers: `EventTimeTrigger` fires when watermark passes window end; `CountTrigger` for count-based early firing.

**Level 4:** Custom triggers and evictors (Flink): fire early (incremental results) + fire final (complete result when window closes). Pattern: emit incremental results every 30 seconds for dashboards, emit final result on window close for billing accuracy. Flink `ContinuousEventTimeTrigger` or `PurgingTrigger` for early + late firings. In Kafka Streams: use `suppress()` operator to suppress intermediate results and emit only the final per-window aggregate. Trade-off: suppress requires `TimeWindows.ofSizeAndGrace()` and buffers results in state until the window closes + grace expires.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ WINDOW TYPES COMPARISON                              │
├──────────────────────────────────────────────────────┤
│                                                      │
│ EVENT STREAM: t=1,2,3,4,5,6,7,8,9,10 (minutes)     │
│                                                      │
│ TUMBLING (size=5):                                  │
│ [1---2---3---4---5][6---7---8---9--10][...]         │
│  Window 1           Window 2                        │
│                                                      │
│ SLIDING (size=5, slide=2):                          │
│ [1---2---3---4---5]                                 │
│     [3---4---5---6---7]                             │
│         [5---6---7---8---9]                         │
│ Overlapping: events 3-5 appear in 2 windows        │
│ [WINDOWING ← YOU ARE HERE: temporal grouping]       │
│                                                      │
│ SESSION (gap=3min, per key):                        │
│ User A: [1--2] gap>3min [6--7--8] gap>3min [10]    │
│ Session: [1,2]           [6,7,8]          [10]     │
│ Variable length; per-user independent               │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Fraud detection: > 3 transactions in 5-minute session for same user

Flink session window job:
Window: EventTimeSessionWindows.withGap(Time.minutes(5))
Group by: userId

Events for User-42:
  T=14:00:01 txn $50 → session opens for User-42
  T=14:01:00 txn $150 → same session (gap < 5min)
  T=14:02:30 txn $200 → same session, count=3
  T=14:03:00 txn $1000 → same session, count=4
  T=14:08:01 (watermark advances past 14:03:00 + gap=5min = 14:08:00)
  → Session window closes: [14:00:01, 14:03:00+5min)
  → Aggregate: User-42, 4 transactions, $1400 total, 3 minutes
  → 4 > 3 threshold → FRAUD ALERT published to "fraud-alerts" topic

User-42 has no activity from 14:03 to 14:10+:
  New session starts only if new event arrives
  Each session independently evaluated for fraud
```

---

### ⚖️ Comparison Table

| Window Type | Size     | Overlapping  | Events per Window         | State Cost  | Use Case                          |
| ----------- | -------- | ------------ | ------------------------- | ----------- | --------------------------------- |
| Tumbling    | Fixed    | No           | Each event in 1 window    | Low         | Hourly/daily aggregates, billing  |
| Sliding     | Fixed    | Yes          | Each event in N/S windows | High (N/S×) | Rolling averages, trend detection |
| Session     | Variable | No (per key) | Each event in 1 session   | Medium      | User sessions, activity bursts    |

---

### ⚠️ Common Misconceptions

| Misconception                                                                          | Reality                                                                                                                                                                                                                            |
| -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Processing time windows are simpler and equivalent to event time for ordered streams" | Only for perfectly ordered, low-latency streams. Real systems have network delays, mobile buffering, retries - events arrive late. Processing time windows misplace these events. Use event time for correctness                   |
| "Session windows have a fixed duration"                                                | Session window duration is VARIABLE - determined by the inactivity gap. A session can be 10 seconds or 10 hours. The gap parameter defines when a session ENDS (inactivity threshold), not its maximum duration                    |
| "Sliding windows are more accurate than tumbling"                                      | Sliding windows provide higher temporal resolution (more frequent results). They're not inherently more accurate - they count the same events but in more overlapping windows. Higher precision comes at higher computational cost |

---

### 🚨 Failure Modes & Diagnosis

**1. Window Results Are All Zero / Empty**

**Symptom:** Windowed aggregations produce no output or all-zero results.

**Root Cause A:** Event time not correctly assigned. Watermarks are 0 (epoch) instead of current time → windows never close.

**Diagnosis:**

```java
// Add debug: print watermarks
orders.assignTimestampsAndWatermarks(
    WatermarkStrategy.<Order>forBoundedOutOfOrderness(Duration.ofSeconds(10))
        .withTimestampAssigner((order, ts) -> {
            long timestamp = order.getTimestamp();
            if (timestamp <= 0) {
                log.error("INVALID TIMESTAMP: {} for order {}", timestamp, order.getId());
                return Instant.now().toEpochMilli();  // fallback
            }
            return timestamp;
        })
);
```

**Root Cause B:** No messages flowing through (empty stream). Verify source topic has data:

```bash
kafka-console-consumer --topic orders --max-messages 5
```

---

### 🔗 Related Keywords

**Prerequisites:** Watermark, Event Time vs Processing Time
**Builds On This:** Stream Processing Aggregations, Fraud Detection
**Related:** Watermark, Event Time vs Processing Time, Apache Flink

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ TUMBLING    │ Fixed, non-overlapping; event in 1 window │
│ SLIDING     │ Fixed, overlapping; event in N windows    │
│ SESSION     │ Variable per key; ends on inactivity gap  │
│ EVENT TIME  │ Use for correctness (handle late data)    │
│ PROCESS TIME│ Use for operational metrics only          │
│ WATERMARK   │ Threshold: when window is "done enough"   │
│ GRACE PERIOD│ Kafka Streams: accept late events for N   │
│ ALLOWED LAT.│ Flink: keep window open N extra time      │
│ SIDE OUTPUT │ Events beyond lateness → separate output  │
│ ONE-LINER   │ "Group infinite stream into time buckets;│
│             │  tumbling=fixed; sliding=overlapping;     │
│             │  session=activity-bounded"                │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) Explain the three types of windows (tumbling, sliding, session). For each, give a real-world use case where that window type is the correct choice. What is the difference between a window's "size" and the "slide" parameter?

**Q2.** (TYPE C - Design) Build a real-time fraud detection system that flags users with: (1) > 5 transactions in any 5-minute tumbling window, (2) any single transaction > $5000 in a session, (3) transactions from > 3 different countries in a 1-hour sliding window. Design the Flink topology with appropriate window types for each rule.
