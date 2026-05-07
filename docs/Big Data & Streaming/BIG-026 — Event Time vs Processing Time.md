---
layout: default
title: "Event Time vs Processing Time"
parent: "Big Data & Streaming"
nav_order: 26
permalink: /big-data-streaming/event-time-vs-processing-time/
number: "BIG-026"
category: Big Data & Streaming
difficulty: ★★★
depends_on: Watermark, Windowing (Tumbling, Sliding, Session), Apache Flink
used_by: Stream Processing, Event-Time Windows, Analytics
related: Watermark, Windowing (Tumbling, Sliding, Session), Apache Flink
tags:
  - event-time
  - processing-time
  - ingestion-time
  - stream-processing
  - temporal-semantics
---

# BIG-026 — Event Time vs Processing Time

⚡ TL;DR — **Event Time** is when an event actually **occurred** (embedded in the message), **Processing Time** is when the event is **processed by the pipeline** (system clock), **Ingestion Time** is when Kafka **received** the event; event time is semantically correct (accounts for mobile buffering, out-of-order delivery) but requires watermarks; processing time is simpler (no watermarks) but incorrect for late events; **always use event time for business metrics** (billing, fraud, analytics); use processing time only for operational/infrastructure metrics.

| #556            | Category: Big Data & Streaming                                  | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------- | :-------------- |
| **Depends on:** | Watermark, Windowing (Tumbling, Sliding, Session), Apache Flink |                 |
| **Used by:**    | Stream Processing, Event-Time Windows, Analytics                |                 |
| **Related:**    | Watermark, Windowing (Tumbling, Sliding, Session), Apache Flink |                 |

---

### 🔥 The Problem This Solves

**THE SAME DATA, DIFFERENT ANSWERS:**
A streaming pipeline counts hourly revenue. At 16:02:00, orders from 15:58 arrive (because mobile users were offline). If the pipeline uses processing time: these orders are counted in the 16:00-17:00 window (when processed). The 15:00-16:00 window is closed with incomplete revenue. Finance sees $98,000 for 15:00-16:00 and $2,000 for 16:00-17:00. Reality: $100,000 all occurred in 15:00-16:00. Using processing time gives you wrong answers for any out-of-order or delayed data.

---

### 📘 Textbook Definition

Three temporal notions in stream processing:

1. **Event Time**: the time when the event actually occurred in the real world. Embedded in the event payload by the producing system (e.g., `order.createdAt`, `sensor.measuredAt`). Most semantically meaningful for business logic.

2. **Processing Time** (also "system time"): the time when the stream processor observes the event. The processor's wall clock when `process()` is called. Simplest to implement (no watermarks), but incorrect for any non-trivial latency scenario.

3. **Ingestion Time**: the time when the event enters the streaming system (e.g., when Kafka received the message). A compromise between event time and processing time. Better than processing time for replays/backfills, but still incorrect if the event was buffered before reaching Kafka (e.g., mobile app offline for 30 minutes).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Event time = when it happened (in the event). Processing time = when you saw it (system clock). Ingestion time = when Kafka got it. Use event time for correct results.

**One analogy:**

> A crime reporter covers events. **Processing time**: "I'm writing the story now, so it happened now." (Wrong — the crime happened 3 hours ago.) **Ingestion time**: "The police report arrived at the newsroom at 2pm." (Better, but the crime happened at 11am.) **Event time**: "According to witnesses, the crime happened at 11am." (Correct — reflects when the event actually occurred.) Accurate journalism requires event time.

**One insight:**
The gap between event time and processing time — called **event lag** or **event skew** — is the key operational metric for stream processors. If P99 event lag is 45 seconds (99% of events arrive within 45 seconds of when they occurred), set your watermark's `forBoundedOutOfOrderness(45s)`. This means: for 99% of events, results are correct; for 1% of very late events, use side output / allowedLateness. Measure your actual event lag distribution before configuring watermarks.

---

### 🔩 First Principles Explanation

**THREE TIMESTAMPS IN KAFKA + FLINK:**

```java
// Each Kafka message has THREE timestamps:
// 1. Producer timestamp: when producer called send()
//    (approximates event time if set correctly)
// 2. Broker append time: when broker wrote to partition log
//    (ingestion time)
// 3. Flink processing time: when Flink's process() function runs
//    (processing time)

// Kafka topic-level config for which timestamp to use:
// message.timestamp.type=CreateTime   (default, uses producer timestamp)
// message.timestamp.type=LogAppendTime (uses broker time — ingestion time)

// In Flink: explicit timestamp assignment from event payload (CORRECT approach):
WatermarkStrategy<OrderEvent> eventTimeStrategy = WatermarkStrategy
    .<OrderEvent>forBoundedOutOfOrderness(Duration.ofSeconds(30))
    .withTimestampAssigner((event, recordTimestamp) -> {
        // EXTRACT event time from the event object:
        return event.getEventTimestamp();  // milliseconds since epoch
        // This is WHEN THE EVENT ACTUALLY OCCURRED
    });

// Using Kafka broker timestamp (ingestion time — LESS CORRECT):
WatermarkStrategy<OrderEvent> ingestionTimeStrategy = WatermarkStrategy
    .<OrderEvent>forBoundedOutOfOrderness(Duration.ofSeconds(30))
    .withTimestampAssigner((event, recordTimestamp) -> {
        return recordTimestamp;  // recordTimestamp = Kafka broker append time
        // Records the time Kafka received the message, NOT when it occurred
    });

// Using processing time (AVOID for business metrics):
WatermarkStrategy<OrderEvent> processingTimeStrategy =
    WatermarkStrategy.noWatermarks();
// Then use: TumblingProcessingTimeWindows instead of TumblingEventTimeWindows
// Window closes based on system clock — no watermarks needed — simple but semantically wrong
```

**CONCRETE COMPARISON — SAME EVENTS, DIFFERENT TIME SEMANTICS:**

```
Scenario: Mobile app sends 3 order events (user offline for 30 min, then comes online)
  Order A: occurred at 14:50:00 (event_time)
  Order B: occurred at 14:51:00 (event_time)
  Order C: occurred at 14:52:00 (event_time)

  All 3 events arrive at Kafka/Flink at: 15:22:00 (processing_time)
  (30-minute delay due to mobile offline buffering)

Tumbling Windows (1-hour):
  Window using EVENT TIME (correct):
    Window [14:00-15:00): Orders A, B, C → revenue for 14:00-15:00 CORRECT

  Window using PROCESSING TIME (incorrect):
    Window [15:00-16:00): Orders A, B, C → WRONG — attributed to wrong hour
    The revenue "happened" in 14:00-15:00 but is counted in 15:00-16:00

  Impact on hourly revenue report:
    Event time:      14:00-15:00: $X+A+B+C,  15:00-16:00: $Y (correct)
    Processing time: 14:00-15:00: $X,         15:00-16:00: $Y+A+B+C (wrong!)

Replay scenario (replaying 30 days of historical data today):
  Event time: events correctly placed in their original 30-day window buckets
  Processing time: ALL events land in today's window (replay time) → USELESS
  Ingestion time: ALL events land in today's window (current ingestion) → USELESS

  → Event time is THE ONLY correct approach for replay/backfill
```

**CHOOSING TIME SEMANTICS IN PRACTICE:**

```java
// DECISION GUIDE:

// 1. Business metrics (revenue, orders, clicks, conversions):
//    → EVENT TIME
//    Must reflect when events ACTUALLY occurred
//    Replay must produce correct historical results
//    Out-of-order events (mobile, network delays) must be in correct windows
//    Code: TumblingEventTimeWindows + forBoundedOutOfOrderness

// 2. Real-time operational dashboards (requests/sec, error rates):
//    → PROCESSING TIME (acceptable simplification)
//    You care about "what's happening NOW in the pipeline"
//    Out-of-order doesn't matter (these are infrastructure metrics)
//    Code: TumblingProcessingTimeWindows (no watermarks needed)

// 3. SLA monitoring (latency percentiles):
//    → BOTH: event time for "when did the event occur?" + processing time for "when did we see it?"
//    lag = processing_time - event_time
//    This lag IS the metric you care about

// 4. Fraud detection (events must be checked within N minutes of occurrence):
//    → EVENT TIME for window boundaries + processing time for SLA enforcement
//    "Flag if > 5 transactions in 5-minute event-time window" → event time
//    "Alert if fraud check took > 10s" → processing time

// Spring Boot + Kafka: event time in message header
@Service
public class OrderEventProducer {
    public void publishOrder(Order order) {
        ProducerRecord<String, Order> record = new ProducerRecord<>(
            "order-events", order.getId(), order
        );
        // Kafka default: producer sets timestamp = System.currentTimeMillis() (creation time)
        // This is CLOSE to event time if the producer runs on the same machine
        // For strict event time: embed event timestamp in the ORDER PAYLOAD
        // (not just the Kafka record timestamp — payload is more reliable):
        order.setEventTimestamp(Instant.now().toEpochMilli());
        kafkaTemplate.send(record);
    }
}
```

---

### 🧪 Thought Experiment

**WHAT IF THE DEVICE CLOCK IS WRONG?**

IoT sensors often have incorrect system clocks (no NTP sync, battery-powered). Sensor A reports a temperature reading at "event_time=2024-01-15T14:00:00" but the sensor's clock is 2 years behind: the actual event time is 2026, but the sensor says 2024.

Using event time: this event is placed in a 2024 window. Processing time: correctly placed in a 2026 window.

**Mitigation:** Validate event timestamps at ingestion:

```java
.withTimestampAssigner((event, recordTimestamp) -> {
    long eventTs = event.getEventTimestamp();
    long now = System.currentTimeMillis();
    long MAX_SKEW = 24 * 3600 * 1000L;  // 24 hours max allowed skew

    if (Math.abs(now - eventTs) > MAX_SKEW) {
        log.warn("Suspicious event timestamp: {} (now: {}), using record time",
            eventTs, now);
        return recordTimestamp;  // fall back to Kafka broker timestamp
    }
    return eventTs;
})
```

This is why event-time systems must validate timestamp sanity — garbage event timestamps → garbage windowing.

---

### 🧠 Mental Model / Analogy

> Three historians documenting the same event:
>
> - **Processing time historian**: "I'm writing this down NOW, so it happened NOW." Fast, but historically inaccurate.
> - **Ingestion time historian**: "I received the report at 3pm, so the event happened at 3pm." Better, but still wrong if the report was delayed.
> - **Event time historian**: "The report says the battle occurred on July 4th, 1776. I'm writing that." Slower (need to verify sources, handle late reports), but historically accurate.

> For building a reliable historical record (business analytics, billing), you need the event-time historian.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Event time = when it happened (in payload). Processing time = when pipeline saw it (wall clock). Ingestion time = when Kafka received it. Use event time for business metrics, processing time for operational/infrastructure metrics.

**Level 2:** Event time requires watermarks (to know when a window is complete). Processing time is simpler (no watermarks). Ingestion time: better than processing time for non-Kafka-buffered sources, still wrong for mobile/buffered sources. Replay: only event time produces correct historical results.

**Level 3:** Event lag = processing_time - event_time. Measure P95/P99 event lag for your data sources. Set `forBoundedOutOfOrderness` to P99 lag. Accept that P99+ events will be "late." For multi-hop systems: lag = sum of latency at each hop (app → Kafka → Flink). Track end-to-end lag. Kafka `message.timestamp.type=CreateTime` uses producer send time — good approximation of event time IF the event is produced synchronously. Async producers (e.g., mobile buffering) should embed event time in payload.

**Level 4:** Time alignment in joins: if joining two streams (orders + payments) on event time, both must use the same event time reference. If orders use `order.createdAt` and payments use `payment.processedAt`, a 5-minute join window may miss valid matches if payment processing takes 6 minutes. Solution: use the same temporal reference (e.g., both keyed on `order.createdAt`) or use a wider join window that accounts for the payment processing delay. In Flink: interval join (`intervalJoin`) allows asymmetric time bounds: `-5min ≤ payment.time - order.time ≤ 10min` — covers orders where payment arrives up to 10 minutes later.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ THREE TIME PERSPECTIVES FOR THE SAME EVENT           │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Real World:  📱 User taps "order" at 14:50:00       │
│               ↓ mobile offline 30 minutes            │
│ Event Time:  event.timestamp = 14:50:00 (in payload) │
│               ↓ arrives at Kafka at 15:22:00         │
│ Ingestion:   Kafka record.timestamp = 15:22:00       │
│               ↓ Flink processes at 15:22:05          │
│ Processing:  System.currentTimeMillis() = 15:22:05   │
│                                                      │
│ [EVENT TIME ← YOU ARE HERE: timestamp in the payload]│
│                                                      │
│ Window assignment:                                   │
│   Event time → window [14:00-15:00) ✓ CORRECT       │
│   Ingestion/Processing → window [15:00-16:00) ✗ WRONG│
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Real-time + historical billing with event time:

Real-time processing:
  Mobile user buys at 14:50 (offline) → app buffers order
  App comes online at 15:22 → sends to API → Kafka → Flink
  Flink: event_time=14:50, processing_time=15:22, event_lag=32 minutes
  Watermark strategy: forBoundedOutOfOrderness(2min) — 32 min lag >> 2 min
  → This event is LATE DATA → sideOutput → handled by late data reconciler

  With forBoundedOutOfOrderness(60min):
  → Event fits within allowed lateness → correctly placed in [14:00-15:00) window
  → Tradeoff: billing results not final until 60 minutes after window ends

Historical replay (at end of month for reconciliation):
  Replay all events from Kafka (30-day retention) or S3 archive
  Flink processes all events using event_time=event.timestamp
  All events correctly bucketed into their original hourly windows
  Processing time: irrelevant (all events processed in minutes today)
  → Monthly revenue report matches real-time results ✓

  Processing time replay:
  → All events land in "current hour" window → useless, all mixed together ✗
```

---

### ⚖️ Comparison Table

| Dimension                    | Event Time                        | Processing Time            | Ingestion Time         |
| ---------------------------- | --------------------------------- | -------------------------- | ---------------------- |
| Source                       | Event payload (`event.timestamp`) | System clock at processing | Kafka broker timestamp |
| Watermarks needed?           | YES                               | NO                         | Optional               |
| Correct for late events?     | YES                               | NO                         | Partially              |
| Correct for replay?          | YES                               | NO                         | NO                     |
| Simplicity                   | Complex                           | Simple                     | Medium                 |
| Use for business metrics?    | YES                               | NO                         | Sometimes              |
| Use for operational metrics? | Optional                          | YES                        | Optional               |

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                           |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "If Kafka processes in order, event time = processing time"  | Only for perfectly ordered, zero-latency systems. Any network hop, mobile buffering, or retry can cause a gap. Even in-datacenter Kafka can have 100-500ms jitter                 |
| "Ingestion time is good enough"                              | Ingestion time (Kafka broker timestamp) is wrong for: (1) mobile/IoT buffering before reaching Kafka, (2) replay scenarios, (3) any multi-hop pipeline with variable delay        |
| "Processing time windows are faster than event time windows" | Processing time windows are SIMPLER (no watermarks, no state management for late data). Latency is similar for on-time data. Event time adds overhead only for late data handling |

---

### 🚨 Failure Modes & Diagnosis

**1. Event Timestamp Extraction Failure — Watermark at Epoch**

**Symptom:** All windows are stuck, no results emitted. Flink watermark metric shows `-9223372036854775808` (Long.MIN_VALUE) or a timestamp from the year 1970.

**Root Cause:** `withTimestampAssigner` returns 0 or null (event timestamp field is null/missing in the payload). Watermark = 0 - 30s = still very early → no windows close.

**Diagnosis:**

```java
.withTimestampAssigner((event, recordTimestamp) -> {
    if (event.getEventTimestamp() == null || event.getEventTimestamp() <= 0) {
        log.error("NULL/ZERO event timestamp for event: {}", event.getId());
        // Option 1: use record timestamp as fallback
        return recordTimestamp;
        // Option 2: use current time (processing time as fallback)
        // return System.currentTimeMillis();
        // Option 3: throw to route to DLQ
        // throw new InvalidEventException("No event timestamp");
    }
    return event.getEventTimestamp();
})
```

---

### 🔗 Related Keywords

**Prerequisites:** Watermark, Windowing (Tumbling, Sliding, Session)
**Builds On This:** Stream Processing, Event-Time Windows
**Related:** Watermark, Windowing (Tumbling, Sliding, Session), Apache Flink

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ EVENT TIME  │ When event occurred (in payload)           │
│ PROC. TIME  │ When pipeline processes (system clock)     │
│ INGEST TIME │ When Kafka received (broker timestamp)     │
│ USE ET FOR  │ Business metrics, billing, fraud, replay  │
│ USE PT FOR  │ Operational metrics, infrastructure       │
│ ET REQUIRES │ Watermarks + timestamp extraction         │
│ LAG         │ processing_time - event_time → measure P99│
│ REPLAY      │ Only event time gives correct history     │
│ VALIDATION  │ Sanity-check event timestamps at ingest  │
│ ONE-LINER   │ "Event time = when it happened; process  │
│             │  time = when you saw it; use event time  │
│             │  for correct business results"            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What is the difference between event time, processing time, and ingestion time? For each, describe a scenario where it would give incorrect results for a business use case. Why is event time the recommended approach for business metrics?

**Q2.** (TYPE C — Design) An IoT platform collects sensor readings from 10,000 devices. Devices can be offline for up to 48 hours (ship in remote areas). Build a Flink pipeline that: uses event time correctly, handles the 48-hour offline buffering, alerts on anomalous temperature readings within their actual time window, and produces correct daily summaries even for backfilled data.
