---
layout: default
title: "Consumer Lag"
parent: "Big Data & Streaming"
nav_order: 18
permalink: /big-data-streaming/consumer-lag/
number: "BIG-018"
category: Big Data & Streaming
difficulty: ★★★
depends_on: Apache Kafka, Consumer Group, Kafka Topic / Partition / Offset
used_by: Kafka Monitoring, SRE, Observability
related: Consumer Group, Kafka Topic / Partition / Offset, ISR (In-Sync Replicas)
tags:
  - consumer-lag
  - kafka-monitoring
  - observability
  - kafka
  - deep-dive
---

# BIG-018 — Consumer Lag

⚡ TL;DR — **Consumer Lag** is the gap between a Kafka partition's latest produced offset and a consumer group's committed offset for that partition — `LAG = LOG-END-OFFSET - COMMITTED-OFFSET`; high lag means consumers are falling behind producers; monitor via `kafka-consumer-groups.sh --describe`, JMX (`kafka.consumer.consumer-fetch-manager-metrics.records-lag`), or Prometheus/Burrow; reduce via more partitions + consumers, faster processing, or autoscaling.

| #548            | Category: Big Data & Streaming                                           | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Apache Kafka, Consumer Group, Kafka Topic / Partition / Offset           |                 |
| **Used by:**    | Kafka Monitoring, SRE, Observability                                     |                 |
| **Related:**    | Consumer Group, Kafka Topic / Partition / Offset, ISR (In-Sync Replicas) |                 |

---

### 🔥 The Problem This Solves

**REAL-TIME PIPELINES FALLING BEHIND WITHOUT WARNING:**
Your order processing service reads from Kafka. On Black Friday, order volume triples. The consumers keep running (no errors), but they're processing events slower than they're arriving. The Kafka topic now has 5 million unprocessed orders — events from 2 hours ago are just being processed now. Your "real-time" pipeline is now 2 hours behind. Without lag monitoring, this goes undetected until users complain that orders aren't showing up. Consumer lag monitoring provides the early-warning system.

---

### 📘 Textbook Definition

**Consumer Lag** (also called **consumer offset lag**) is the number of messages a consumer group has not yet consumed from a Kafka topic partition:

```
LAG = LOG-END-OFFSET - CURRENT-OFFSET
    = (latest produced message offset) - (last committed consumer offset)
```

Where:

- `LOG-END-OFFSET` (LEO): the next offset to be written — i.e., the highest produced offset + 1
- `CURRENT-OFFSET` (committed offset): the offset of the last message the consumer group successfully committed
- `LAG`: number of unprocessed messages in this partition for this consumer group

Total lag for a topic = sum of lag across all partitions for that consumer group.

A lag of 0 means the consumer is fully caught up. A growing lag (lag increasing over time) means consumers are processing slower than producers are writing.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Consumer lag = unprocessed messages waiting in Kafka = `latest_produced_offset - consumer_committed_offset`.

**One analogy:**

> Your email inbox has 1000 unread emails. You read 10/hour. New emails arrive at 20/hour. Your "lag" grows by 10 emails/hour. The lag (unread count) tells you: you're falling behind. To catch up: read faster (more parallel processing) or stop new emails from arriving (backpressure). Kafka consumer lag is the same metric for event streams.

**One insight:**
Consumer lag is a **rate problem**, not just a count problem. A lag of 1 million messages sounds alarming. But if your consumer processes 10M messages/minute, you'll catch up in 6 minutes. If your consumer processes 1M messages/hour, you'll never catch up. Always monitor **lag + consumer throughput rate** together. A static lag (not growing) is usually acceptable; a growing lag is the real problem.

---

### 🔩 First Principles Explanation

**MEASURING LAG:**

```bash
# Command-line: kafka-consumer-groups.sh
kafka-consumer-groups.sh \
  --bootstrap-server kafka:9092 \
  --group my-consumer-group \
  --describe

# Output:
# GROUP               TOPIC        PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
# my-consumer-group   orders       0          8905            8910            5
# my-consumer-group   orders       1          7832            7890            58
# my-consumer-group   orders       2          9100            9100            0
# my-consumer-group   orders       3          6540            7200            660
#
# Partition 3: LAG=660 — consumer group is 660 messages behind on this partition
# Partition 1: LAG=58 — mild lag
# Partition 2: LAG=0 — fully caught up
#
# Total lag for this consumer group on "orders": 5 + 58 + 0 + 660 = 723

# List all consumer groups:
kafka-consumer-groups.sh --bootstrap-server kafka:9092 --list

# Reset offsets (CAREFUL: moves what consumer will read next):
kafka-consumer-groups.sh \
  --bootstrap-server kafka:9092 \
  --group my-consumer-group \
  --topic orders \
  --reset-offsets \
  --to-latest \
  --execute
# WARNING: this skips all messages from current offset to latest (loses events)
# Use --to-datetime or --to-offset for precise reset
```

**SPRING BOOT: PROGRAMMATIC LAG MONITORING:**

```java
// Using AdminClient to query consumer group lag programmatically
@Component
public class ConsumerLagMonitor {

    private final AdminClient adminClient;

    public ConsumerLagMonitor(AdminClient adminClient) {
        this.adminClient = adminClient;
    }

    @Scheduled(fixedDelay = 60000)  // check every 60s
    public void checkLag() throws Exception {
        String groupId = "order-processing-group";

        // Get committed offsets for this consumer group
        Map<TopicPartition, OffsetAndMetadata> committedOffsets =
            adminClient.listConsumerGroupOffsets(groupId)
                .partitionsToOffsetAndMetadata()
                .get();

        // Get end offsets (LOG-END-OFFSET) for those partitions
        Map<TopicPartition, Long> endOffsets =
            adminClient.listOffsets(
                committedOffsets.keySet().stream()
                    .collect(Collectors.toMap(tp -> tp,
                        tp -> OffsetSpec.latest()))
            ).all().get().entrySet().stream()
            .collect(Collectors.toMap(
                Map.Entry::getKey,
                e -> e.getValue().offset()
            ));

        // Calculate lag per partition
        long totalLag = 0;
        for (Map.Entry<TopicPartition, OffsetAndMetadata> entry : committedOffsets.entrySet()) {
            TopicPartition tp = entry.getKey();
            long committed = entry.getValue().offset();
            long endOffset = endOffsets.getOrDefault(tp, committed);
            long lag = endOffset - committed;
            totalLag += lag;

            if (lag > 10000) {  // alert if partition lag > 10K messages
                log.warn("HIGH LAG: group={}, partition={}, lag={}", groupId, tp, lag);
                // push metric to Prometheus/Micrometer
                meterRegistry.gauge("kafka.consumer.lag",
                    Tags.of("group", groupId, "partition", tp.toString()), lag);
            }
        }
        log.info("Total lag for {}: {}", groupId, totalLag);
    }
}
```

**PROMETHEUS + GRAFANA MONITORING:**

```yaml
# kafka-exporter (prometheus-kafka-exporter) or strimzi Kafka Operator

# Key metrics to monitor:
# kafka_consumergroup_lag{consumergroup, topic, partition}
#   → Current lag per partition per consumer group

# kafka_consumergroup_lag_sum{consumergroup, topic}
#   → Sum of lag across all partitions for a topic

# PromQL alerts:
# Alert if lag growing for 5 minutes:
- alert: KafkaConsumerLagGrowing
  expr: |
    increase(kafka_consumergroup_lag_sum{consumergroup="order-processing"}[5m]) > 0
  for: 5m
  annotations:
    summary: "Consumer group lag is growing — consumers falling behind"

# Alert if total lag exceeds threshold:
- alert: KafkaConsumerLagHigh
  expr: |
    kafka_consumergroup_lag_sum{consumergroup="order-processing"} > 50000
  for: 2m
  annotations:
    summary: "Consumer lag exceeds 50K messages — investigate processing speed"
# Burrow (LinkedIn's open source consumer lag monitor):
# More sophisticated: detects lag trends, not just point-in-time values
# Classifies consumer state: OK, WARNING, STALLED, STOPPED
# Useful for consumers that pause intentionally (e.g., batch processing)
```

**UNDERSTANDING LAG SPIKES:**

```
LAG SPIKE ANALYSIS DECISION TREE:

Lag suddenly increases → ask:
  1. Did producer throughput increase? (e.g., traffic spike)
     → Is lag growing or stable at a new higher point?
     → If stable: consumer is keeping up with current rate, just behind temporarily
     → If growing: consumer throughput < producer throughput → PROBLEM

  2. Did a consumer instance crash or restart?
     → Rebalancing: all consumers paused during rebalance (eager) or
       partially paused (cooperative)
     → Lag increases briefly, then stabilizes once rebalance completes
     → Duration: seconds to minutes

  3. Is a consumer stuck on one message?
     → max.poll.records: consumer polled too few records per call
     → max.poll.interval.ms exceeded → consumer kicked from group
     → Poison pill: one bad message that always fails (DLQ pattern needed)

  4. Is one partition's lag much higher than others?
     → Data skew: one partition is "hot" (too many events for one partition key)
     → Processing bottleneck: specific consumer thread is slow
     → Fix: review partitioning strategy, redistribute keys

Common lag causes:
  - Slow downstream (DB write bottleneck)
  - Consumer GC pauses (Java heap too small → frequent GC)
  - Consumer doing synchronous HTTP calls per record (use batch + async)
  - Insufficient consumer threads (max = partition count)
  - Large messages (high serialization/deserialization overhead)
```

---

### 🧪 Thought Experiment

**THE TRADEOFF: COMMIT FREQUENCY vs LAG ACCURACY**

More frequent offset commits (`enable.auto.commit=true`, `auto.commit.interval.ms=100`) → more accurate lag measurement BUT higher Kafka broker load.

Less frequent commits (commit every 1000 records) → lag measurement is less granular (could show 0 lag but have 999 unprocessed records in-memory) BUT lower overhead.

Manual commit (`enable.auto.commit=false`, commit after processing) → most accurate lag (committed = truly processed) AND enables at-least-once guarantees. This is the production recommendation.

The lag metric you monitor is only as accurate as your commit strategy.

---

### 🧠 Mental Model / Analogy

> Consumer lag is like a highway traffic monitor. LOG-END-OFFSET = cars currently entering the highway. COMMITTED-OFFSET = cars that have exited. LAG = cars on the highway (in transit). A lag of 1,000 with 10,000 cars/hour throughput = highway clears in 6 minutes. A lag of 1,000 with 100 cars/hour = 10 hours to clear = traffic jam.

> Burrow is like a traffic management system that doesn't just count cars but CLASSIFIES the situation: OK (normal), WARNING (traffic building), STALLED (cars stopped completely), STOPPED (no cars moving at all). Point-in-time lag count isn't enough — you need trend classification.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Consumer lag = unread messages. `LAG = LOG-END-OFFSET - COMMITTED-OFFSET`. Check with `kafka-consumer-groups.sh --describe`. High lag = consumers falling behind. Fix: more consumer instances (up to partition count), faster processing.

**Level 2:** Monitor lag with Prometheus + `kafka_consumergroup_lag` metric. Alert on growing lag (not just absolute value). Burrow for trend-based classification. Identify hot partitions (skewed lag across partitions). Manual commit (`enable.auto.commit=false`) gives most accurate lag.

**Level 3:** Lag root causes: slow downstream (DB bottleneck), partition skew, rebalance pauses (use CooperativeStickyAssignor), poison pill messages (use DLQ). `max.poll.records` and `max.poll.interval.ms` interact: if processing 500 records takes > `max.poll.interval.ms` (5 min default), consumer is kicked from group → lag spikes. Tune: reduce `max.poll.records` or increase `max.poll.interval.ms`.

**Level 4:** Lag-based autoscaling (KEDA — Kubernetes Event-Driven Autoscaling): `ScaledObject` with `kafka` trigger → automatically scales Deployment based on consumer lag. Target: `lagThreshold: 100` → scale up consumer pods when lag > 100 per partition. Combines with HPA for CPU-based scaling. Production pattern for Black Friday scale: lag metric drives horizontal pod autoscaler dynamically. Limitation: partitions cap max instances — scale partitions first if you need more than N consumers.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ CONSUMER LAG VISUALIZATION                           │
├──────────────────────────────────────────────────────┤
│                                                      │
│ "orders" Topic - Partition 3:                       │
│                                                      │
│ Offsets: [0][1][2]...[6539][6540][6541]...[7199][7200→]│
│                           ↑                    ↑    │
│                     COMMITTED-OFFSET     LOG-END-OFFSET│
│                     (consumer is here)  (producer wrote here) │
│                                                      │
│ LAG = 7200 - 6540 = 660 messages                    │
│ [CONSUMER LAG ← YOU ARE HERE: gap measurement]       │
│                                                      │
│ If throughput = 100 msg/sec:                        │
│   Time to catch up = 660 / 100 = 6.6 seconds       │
│ If throughput = 1 msg/sec:                          │
│   Time to catch up = 660 seconds = 11 minutes      │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Black Friday Lag Incident Response:

T=11:00: Normal traffic. Lag = 50 messages (steady state, fully caught up).
T=11:30: Black Friday sale starts. Order rate 10× normal.
T=11:35: Prometheus alert fires: "KafkaConsumerLagGrowing" (5 consecutive minutes of growth)
T=11:40: Lag = 250,000 messages. Pager fires: "KafkaConsumerLagHigh" (> 50K)
T=11:41: SRE checks: `kafka-consumer-groups.sh --describe` → Partition 3 LAG=180K (hotspot)
         All other partitions: LAG ~10K-15K → partition 3 is disproportionately behind
T=11:42: Root cause: order-service routes "VIP" orders to specific partition key "VIP-USER"
         → All VIP orders go to partition 3 → hot partition
T=11:45: Short-term fix: `kubectl scale deployment order-consumer --replicas=6`
         → But max useful consumers = 4 (4 partitions) → 2 instances idle
T=11:46: Medium-term fix: add partitions (can't reduce, only increase)
         New topic with 12 partitions + consumer migration
T=12:30: New topic live. Lag trending down. T=13:00: Lag = 0. Fully caught up.
```

---

### ⚖️ Comparison Table

| Tool                       | Purpose                      | Granularity        | Alerting                |
| -------------------------- | ---------------------------- | ------------------ | ----------------------- |
| `kafka-consumer-groups.sh` | Manual CLI inspection        | Partition-level    | No                      |
| JMX metrics                | Per-consumer-instance lag    | Instance+partition | Via JMX alerts          |
| Prometheus kafka-exporter  | Automated metrics collection | Partition-level    | Via PromQL/Alertmanager |
| Burrow (LinkedIn)          | Trend-based consumer health  | Partition+trend    | YES (HTTP API)          |
| KEDA                       | Autoscaling based on lag     | Topic/group-level  | Acts (scales pods)      |

---

### ⚠️ Common Misconceptions

| Misconception                              | Reality                                                                                                                                                                                                                  |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Lag=0 always means healthy"               | A consumer that commits immediately (before processing) shows lag=0 but hasn't actually processed the messages. At-least-once (commit after processing) is the correct approach, and lag reflects true unprocessed count |
| "Lag grows → restart consumers"            | Restarting consumers during high lag causes rebalancing → more lag. Identify root cause first (slow processing? partition skew? downstream bottleneck?) and fix systematically                                           |
| "High absolute lag is always an emergency" | Lag in isolation is meaningless without throughput rate. LAG=1M with 10M/min throughput = 6 seconds behind. LAG=1M with 100/min throughput = 10K minutes behind. Monitor lag trend and time-to-catch-up                  |

---

### 🚨 Failure Modes & Diagnosis

**1. Lag Growing on One Partition Only**

**Symptom:** One partition has lag 10× higher than others. Total group lag is growing.

**Root Cause:** Partition skew — high-volume key always routes to the same partition. Could also be one consumer thread is slow (GC, downstream IO).

**Diagnosis:**

```bash
kafka-consumer-groups.sh --describe | sort -k6 -n -r | head -5
# Shows partitions with highest lag first

# Check if specific key dominates:
kafka-console-consumer --topic orders --partition 3 --max-messages 100 |
  jq '.userId' | sort | uniq -c | sort -n -r | head -10
```

**Fix:** Review partition key strategy. Use random partitioning for hot keys. Consider increasing partition count for the topic (requires topic recreation and migration or partition scaling).

---

### 🔗 Related Keywords

**Prerequisites:** Apache Kafka, Consumer Group, Kafka Topic / Partition / Offset
**Builds On This:** Kafka Monitoring, SRE
**Related:** Consumer Group, Kafka Topic / Partition / Offset, ISR (In-Sync Replicas)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ FORMULA     │ LAG = LOG-END-OFFSET - COMMITTED-OFFSET   │
│ CLI         │ kafka-consumer-groups.sh --describe        │
│ METRIC      │ kafka_consumergroup_lag (Prometheus)       │
│ BURROW      │ Trend-based: OK/WARNING/STALLED/STOPPED   │
│ KEDA        │ Autoscale Pods based on lag threshold     │
│ HOT PART.   │ One partition lag >> others → key skew    │
│ POISON PILL │ One bad message → consumer stuck → DLQ    │
│ TUNE        │ max.poll.records + max.poll.interval.ms   │
│ MONITOR     │ Lag + rate = time-to-catchup              │
│ ONE-LINER   │ "Unprocessed messages = producers ahead  │
│             │  of consumers; monitor trend, not just   │
│             │  absolute value"                          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) A consumer group has zero lag but you suspect it's not actually processing messages. How could this happen and how would you verify it?

**Q2.** (TYPE C — Design) Your team runs a Kafka consumer processing 5 topics with varying throughput. One topic gets traffic spikes during business hours. Design a monitoring and autoscaling strategy using consumer lag as the primary signal.
