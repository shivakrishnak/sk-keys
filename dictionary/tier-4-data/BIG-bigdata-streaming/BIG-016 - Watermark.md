---
version: 2
layout: default
title: "Watermark"
parent: "Big Data & Streaming"
grand_parent: "Technical Dictionary"
nav_order: 16
permalink: /big-data-streaming/watermark/
id: BIG-016
category: Big Data & Streaming
difficulty: ★★★
depends_on: Event Time vs Processing Time, Windowing (Tumbling, Sliding, Session), Apache Flink
used_by: Event-Time Windows, Late Data Handling, Stream Processing
related: Event Time vs Processing Time, Windowing (Tumbling, Sliding, Session), Apache Flink
tags:
  - watermark
  - event-time
  - late-data
  - flink
  - stream-processing
---

# BIG-016 - Watermark

⚡ TL;DR - A **Watermark** is a progress marker in event-time stream processing that says "I've seen all events with timestamp ≤ T" - when a watermark passes a window's end time, the window closes and results are emitted; computed as `watermark = max_event_time_seen - allowed_lateness`; enables **event-time windowing** on out-of-order streams; tradeoff: smaller allowed_lateness → lower latency, more late data dropped; larger → higher latency, higher completeness.

| #555            | Category: Big Data & Streaming                                                      | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Event Time vs Processing Time, Windowing (Tumbling, Sliding, Session), Apache Flink |                 |
| **Used by:**    | Event-Time Windows, Late Data Handling, Stream Processing                           |                 |
| **Related:**    | Event Time vs Processing Time, Windowing (Tumbling, Sliding, Session), Apache Flink |                 |

---

### 🔥 The Problem This Solves

**EVENT-TIME WINDOWS DON'T KNOW WHEN THEY'RE DONE:**
You're running a 5-minute event-time window for [14:00, 14:05). You've seen events up to T=14:04:55. When should you close this window and emit results? You can't wait forever (the stream is infinite). But you can't close at 14:05:00 processing time - mobile events from 14:04:58 might arrive at 14:05:30 due to network delays. A **watermark** is the mechanism: "if I've seen events up to T=14:05:45 event time, it's safe to assume all events for the [14:00-14:05) window have arrived (with 40s of lateness tolerance). Close the window."

---

### 📘 Textbook Definition

A **Watermark** is a special record in a stream that asserts: "no more events with event_time ≤ W will arrive." It serves as the event-time clock for the stream processor:

**Formula:**

```
Watermark(t) = max_observed_event_time(up to t) - max_out_of_orderness
```

Where `max_out_of_orderness` is the allowed delay for late-arriving events.

**How watermarks flow:**

1. Producer embeds event timestamps in messages.
2. Stream processor tracks the maximum event timestamp seen.
3. Periodically emits a watermark = max_event_time - allowed_lateness.
4. When a window's end time ≤ current watermark: window closes, results emitted.
5. Events arriving with event_time < current_watermark: "late data" - can be discarded, sent to side output, or handled with `allowedLateness`.

In parallel operators (multi-partition Flink): watermark = min of all input watermarks. One slow partition can hold back the entire operator's watermark.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Watermark = "I've processed everything up to timestamp T" - it's the event-time clock that tells windows when to close; accounts for out-of-order and late-arriving events.

**One analogy:**

> A shipping company closes an order manifest for a truck at 5pm. But they allow packages that arrive at the dock up to 15 minutes late (15-minute buffer). The "watermark" is 4:45pm → "any package with a shipping label ≤ 4:45pm should have arrived by now." When the clock hits 5pm (watermark 4:45 + 15 min buffer), they close the manifest. A package labeled 4:43pm arriving at 4:59pm: included (within buffer). A package labeled 4:30pm arriving at 5:30pm: late (missed the manifest, handled separately).

**One insight:**
Watermarks are a HEURISTIC, not a guarantee. `forBoundedOutOfOrderness(Duration.ofSeconds(30))` says "I expect at most 30 seconds of out-of-orderness." If an event arrives 60 seconds late, it's treated as "late" and handled by your late data policy. The tradeoff is: bigger allowed delay → more complete windows → higher latency. Smaller delay → lower latency → more events classified as late/dropped. Production systems must measure actual event time latency distributions (P95, P99) and set allowed_lateness accordingly.

---

### 🔩 First Principles Explanation

**WATERMARK CONFIGURATION IN FLINK:**

```java
// Flink: WatermarkStrategy defines how watermarks are generated

// 1. BOUNDED OUT-OF-ORDERNESS: most common for real-world data
WatermarkStrategy<Order> strategy = WatermarkStrategy
    .<Order>forBoundedOutOfOrderness(Duration.ofSeconds(30))
    // "Allow events up to 30 seconds late"
    // Watermark = max_event_time_seen - 30s
    .withTimestampAssigner((order, recordTimestamp) -> order.getEventTimestamp());
    // Extract event time from the Order object

// 2. MONOTONOUS TIMESTAMPS: for perfectly ordered streams (no out-of-orderness)
WatermarkStrategy<Order> monotonous = WatermarkStrategy
    .<Order>forMonotonousTimestamps()  // watermark = max_event_time (no delay)
    .withTimestampAssigner(...);
// Use for: perfectly ordered sources (database CDC), synthetic test data

// 3. CUSTOM WATERMARK GENERATOR: for special cases
WatermarkStrategy<Order> custom = WatermarkStrategy
    .forGenerator(context -> new WatermarkGenerator<Order>() {
        private long maxTimestamp = Long.MIN_VALUE;
        private final long OUT_OF_ORDER_MS = 30_000; // 30 seconds

        @Override
        public void onEvent(Order event, long eventTimestamp, WatermarkOutput output) {
            // Called for every event: track max timestamp
            maxTimestamp = Math.max(maxTimestamp, event.getEventTimestamp());
            // Don't emit watermark on every event - emit periodically (see below)
        }

        @Override
        public void onPeriodicEmit(WatermarkOutput output) {
            // Called every 200ms (configurable): emit watermark
            output.emitWatermark(new Watermark(maxTimestamp - OUT_OF_ORDER_MS));
        }
    })
    .withTimestampAssigner((order, ts) -> order.getEventTimestamp());

// Apply strategy to source:
DataStream<Order> orders = env
    .fromSource(kafkaSource, strategy, "kafka-orders");
```

**WATERMARK PROPAGATION IN PARALLEL OPERATORS:**

```java
// CRITICAL: In parallel Flink jobs, watermarks are the MINIMUM across all input sources

// Scenario: Kafka source with 4 partitions
// Partition 0 watermark: 14:05:00
// Partition 1 watermark: 14:05:30
// Partition 2 watermark: 14:03:00  ← ONE SLOW PARTITION
// Partition 3 watermark: 14:05:20

// Effective watermark at downstream operator: min(14:05, 14:05:30, 14:03, 14:05:20) = 14:03:00
// !! Window [14:00-14:05) CANNOT close because one partition still at 14:03
// !! This causes WINDOW STALENESS: windows don't close because one idle/slow partition

// FIX 1: idleness detection - mark partition as idle if no events for N seconds
WatermarkStrategy<Order> withIdleness = WatermarkStrategy
    .<Order>forBoundedOutOfOrderness(Duration.ofSeconds(30))
    .withIdleness(Duration.ofMinutes(1));
    // If a source partition produces no events for 1 minute:
    // Flink marks it as idle → excludes from watermark min calculation
    // Windows can advance even when some partitions are quiet

// FIX 2: separate streams with different watermarks (union):
DataStream<Order> highVolumeOrders = orders.filter(o -> o.getAmount() > 1000);
DataStream<Order> regularOrders = orders.filter(o -> o.getAmount() <= 1000);
// If regular orders are very sparse, their watermark may lag and hold back
// high-volume order windows
// Solution: reassign watermarks AFTER splitting:
DataStream<Order> highVolumeWithWatermark = highVolumeOrders
    .assignTimestampsAndWatermarks(strategy);
DataStream<Order> regularWithWatermark = regularOrders
    .assignTimestampsAndWatermarks(strategy);
```

**LATE DATA HANDLING:**

```java
// Flink: handle events that arrive after their window's watermark has passed

OutputTag<Order> lateOutputTag = new OutputTag<Order>("late-orders") {};

SingleOutputStreamOperator<OrderAggregate> mainStream = orders
    .keyBy(order -> order.getProductId())
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .allowedLateness(Time.seconds(30))  // keep window state 30s after watermark passes
    .sideOutputLateData(lateOutputTag)  // events arriving > 30s late → side output
    .process(new OrderWindowProcessor());

// Main output: events up to 30 seconds late (included in window)
// Side output: events more than 30 seconds late
DataStream<Order> lateOrders = mainStream.getSideOutput(lateOutputTag);

// Late order handling:
lateOrders
    .map(order -> new LateOrderAlert(order.getId(), order.getEventTimestamp()))
    .addSink(alertSink);

// ALLOWEDLATENESS + WATERMARK INTERACTION:
// Window [14:00-14:05) closes when: watermark ≥ 14:05:00
// With allowedLateness=30s: window STATE kept until watermark ≥ 14:05:30
// Events arriving at 14:05:15 event time: LATE but within allowedLateness → included
// Events arriving at 14:04:00 event time but at 14:06:00 proc time: late by 2min → sideOutput
// This means: with watermark forBoundedOutOfOrderness(30s) AND allowedLateness(30s):
//   Total grace = 60 seconds of latency tolerance
```

**MEASURING WATERMARK LAG IN PRODUCTION:**

```java
// Custom metric: how much behind is the watermark vs wall clock?
public class WatermarkLagMetric extends AbstractRichFunction
    implements MapFunction<Order, Order> {

    private transient Counter lateEventCounter;

    @Override
    public void open(Configuration parameters) {
        lateEventCounter = getRuntimeContext().getMetricGroup()
            .counter("late.events");
    }

    @Override
    public Order map(Order order) {
        long now = System.currentTimeMillis();
        long lag = now - order.getEventTimestamp();

        // Emit Prometheus metric: kafka_event_processing_lag_ms
        if (lag > 30_000) {  // > 30 second lag
            lateEventCounter.inc();
            // Log for monitoring
            log.warn("Event lag: {}ms for orderId={}", lag, order.getId());
        }
        return order;
    }
}

// Flink metrics in Prometheus:
// flink_taskmanager_job_task_operator_watermarkLag
// Shows how far behind each operator's watermark is from current wall clock
// High watermark lag → windows not closing → stale results
```

---

### 🧪 Thought Experiment

**WHAT HAPPENS WITH NO WATERMARK (PROCESSING TIME ONLY)?**

If you use processing time windows (`TumblingProcessingTimeWindows`), no watermarks are needed - the window closes when the system clock passes the window end time. Simple! But:

- Mobile app events delayed 5 minutes (network): placed in the "wrong" window (the window they arrive in, not when they occurred).
- Replay/backfill: if you replay historical data, processing time windows put ALL events in the same window (the current time), not their original time buckets.
- Hourly billing: if you must charge users for their usage in the actual hour it occurred, processing time windows are incorrect.

Watermarks exist because **event time** is semantically correct; processing time is just convenient. For business metrics that matter (revenue, usage, fraud detection), always use event time with watermarks.

---

### 🧠 Mental Model / Analogy

> Watermarks are like a newspaper's "print deadline." The newspaper has a print deadline of 5pm. The editor waits until 5pm, then closes the edition - "all stories that happened before 4pm are in this edition" (watermark = 4pm, allowed_lateness = 1 hour). A reporter files a story at 4:55pm about a 3pm event → just makes it in (within 1-hour allowed_lateness). A reporter files at 5:30pm about a 2pm event → too late (exceeds 1-hour window), goes into tomorrow's paper (side output). The newspaper doesn't know if there are more 3:59pm stories coming - it sets a deadline and publishes.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Watermark = "all events up to timestamp T have arrived." When watermark passes a window's end, window closes. Configured as: `max_event_time - allowed_lateness`. `forBoundedOutOfOrderness(30s)` allows 30 seconds of late events.

**Level 2:** Watermark propagates through operators (min of all inputs). Idle sources hold back watermarks → use `.withIdleness()`. `allowedLateness` keeps window open after watermark for late events. `sideOutputLateData` catches events beyond allowed lateness.

**Level 3:** Parallel watermarks: minimum of all input partition watermarks. Custom `WatermarkGenerator`: `onEvent()` tracks max, `onPeriodicEmit()` emits periodically (every 200ms by default). Watermarks advance monotonically - never go backwards. If a very late event arrives and max_event_time is already far ahead, the watermark doesn't move.

**Level 4:** Watermark strategies for specific cases: (1) Source with multiple Kafka partitions: one slow/idle partition blocks watermark - use `withIdleness`. (2) Multiple sources unioned: watermark = min across all - if one source has old data, all windows stall. (3) Kafka Streams: watermarks are implicit - `STREAM_TIME` advances as events arrive; `WALL_CLOCK_TIME` for processing time. (4) Production tuning: measure P95/P99 of event processing latency → set `forBoundedOutOfOrderness` to P99. Anything beyond P99 → late data. Accept that 1% of events will be in the side output and handled separately.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ WATERMARK ADVANCING AND WINDOW CLOSE                 │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Events arriving (event_time):                       │
│   14:00:01, 14:00:30, 14:01:15, 14:02:00, ...      │
│   14:04:55 ← max event time so far                  │
│   Watermark = 14:04:55 - 30s = 14:04:25            │
│                                                      │
│   14:05:35 arrives ← new max                        │
│   Watermark = 14:05:35 - 30s = 14:05:05 ≥ 14:05:00 │
│ [WATERMARK ← YOU ARE HERE: window trigger condition] │
│                                                      │
│   → Window [14:00-14:05) CLOSES                     │
│   → Results emitted: count=42, sum=$4200            │
│                                                      │
│   Event 14:04:45 arrives late (event_time < watermark│
│   14:04:45 < 14:05:05 → LATE DATA                  │
│   Within allowedLateness(30s)? 14:05:05 - 14:04:45 = 20s < 30s → YES│
│   → Added to [14:00-14:05) → corrected result emitted│
│   Beyond allowedLateness? → sideOutput              │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Real-time hourly revenue calculation with Flink + Kafka:

Source: Kafka "order-completed" topic
Events: {orderId, amount, eventTimestamp (ms)}
Strategy: forBoundedOutOfOrderness(Duration.ofMinutes(2))
Window: TumblingEventTimeWindows(1 hour)
allowedLateness: 5 minutes

T=15:59:50: event with event_time=15:59:50 arrives
  max_event_time = 15:59:50
  watermark = 15:57:50 (2 min allowed)
  Window [15:00-16:00): NOT closed (watermark < 16:00)

T=16:02:05: event with event_time=16:02:05 arrives
  max_event_time = 16:02:05
  watermark = 16:00:05 ≥ 16:00:00 → Window [15:00-16:00) CLOSES
  Result emitted: revenue for 15:00-16:00 = $125,000

T=16:04:30: late event with event_time=15:59:55 arrives
  Watermark = 16:00:05, event_time=15:59:55 < 16:00:05 → LATE
  Within allowedLateness(5min)? 16:00:05 - 15:59:55 = 10s < 5min → YES
  → Window [15:00-16:00) state still open (allowedLateness not expired)
  → Updated result emitted: $125,150 (corrected with this late order)

T=16:06:00: event with event_time=15:30:00 arrives
  watermark = ~16:04:xx
  Very late: 16:04 - 15:30 > 5min allowedLateness → sideOutput
  → Logged as "very late order", manual reconciliation process
```

---

### ⚖️ Comparison Table

| WatermarkStrategy              | Latency | Completeness          | Use Case                  |
| ------------------------------ | ------- | --------------------- | ------------------------- |
| forMonotonousTimestamps        | Minimal | 100% (no late events) | Perfectly ordered sources |
| forBoundedOutOfOrderness(10s)  | Low     | ~95%+                 | Low-latency metrics       |
| forBoundedOutOfOrderness(1min) | Medium  | ~99%                  | Most streaming analytics  |
| forBoundedOutOfOrderness(5min) | Higher  | ~99.9%                | Accurate business metrics |
| Custom (per-source tuning)     | Varies  | Tunable               | Complex multi-source jobs |

---

### ⚠️ Common Misconceptions

| Misconception                              | Reality                                                                                                                                                                                                                                                                                           |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Watermarks guarantee no late data"        | Watermarks are heuristics. `forBoundedOutOfOrderness(30s)` means: you EXPECT at most 30s latency. Events beyond 30s late ARE possible and will be "late data." The watermark makes a probabilistic bet, not a guarantee                                                                           |
| "Higher allowed_lateness = better results" | Higher allowed_lateness means more complete windows but higher output latency. A 5-minute allowed_lateness for a 1-hour window means results won't be final until 5 minutes AFTER the window end. For dashboards needing near-real-time data, this is unacceptable                                |
| "Watermarks only matter for Flink"         | Kafka Streams uses event-time processing via `StreamTime` (max event time seen), which is its own watermark concept. Spark Streaming uses watermarks for state cleanup in stateful streaming with `withWatermark()`. Watermarks are universal to event-time stream processing, not Flink-specific |

---

### 🚨 Failure Modes & Diagnosis

**1. Windows Never Closing (Stale Results)**

**Symptom:** Event-time windows accumulate state indefinitely. No results emitted. Flink dashboard shows windows stuck.

**Root Cause:** One idle/empty Kafka partition holding back the watermark. In Flink, the watermark is the minimum across all inputs. An idle partition with watermark=Long.MIN_VALUE prevents all windows from closing.

**Diagnosis:**

```bash
# Flink UI: check watermark per task → one task shows very old watermark
# Or: add logging to watermark generator
```

**Fix:**

```java
WatermarkStrategy<Order> strategy = WatermarkStrategy
    .<Order>forBoundedOutOfOrderness(Duration.ofSeconds(30))
    .withIdleness(Duration.ofMinutes(1));
    // Partitions idle > 1 min: excluded from watermark min calculation
    // Windows can advance even when some Kafka partitions are quiet
```

---

### 🔗 Related Keywords

**Prerequisites:** Event Time vs Processing Time, Windowing (Tumbling, Sliding, Session)
**Builds On This:** Event-Time Windows, Late Data Handling
**Related:** Event Time vs Processing Time, Windowing (Tumbling, Sliding, Session), Apache Flink

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ FORMULA     │ watermark = max_event_time - allowed_lag  │
│ WINDOW CLOSE│ watermark ≥ window_end → close + emit     │
│ FLINK API   │ forBoundedOutOfOrderness(Duration.ofXxx()) │
│ IDLENESS    │ .withIdleness(N min) → skip idle partitions│
│ ALLOWED LAT │ Keep window open N extra after close      │
│ SIDE OUTPUT │ Events beyond allowed lateness → tag      │
│ PARALLEL    │ Watermark = min of all input watermarks   │
│ LATENCY     │ Small allowed_lag → fast but drops late   │
│ COMPLETENESS│ Large allowed_lag → slow but complete     │
│ ONE-LINER   │ "Event-time clock: tells windows they're │
│             │  done; max_seen_time minus allowed_lag"   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What is a watermark in stream processing? How is it calculated? What problem does it solve for event-time windowing? What happens to events that arrive after the watermark has passed their window's end time?

**Q2.** (TYPE B - Trace) A Flink job reads from Kafka (3 partitions). Partition 0: sending events up to 14:05:00. Partition 1: sending events up to 14:05:30. Partition 2: idle for 3 minutes (no events). `forBoundedOutOfOrderness(30s)`. Window [14:00-14:05). Without `.withIdleness()`: what is the effective watermark? With `.withIdleness(Duration.ofMinutes(2))`: what is the effective watermark? In which case does the window close?
