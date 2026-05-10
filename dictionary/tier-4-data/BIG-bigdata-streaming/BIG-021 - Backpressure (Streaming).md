---
version: 2
layout: default
title: "Backpressure (Streaming)"
parent: "Big Data & Streaming"
grand_parent: "Technical Dictionary"
nav_order: 21
permalink: /big-data-streaming/backpressure/
id: BIG-021
category: Big Data & Streaming
difficulty: ★★★
depends_on: Apache Flink, Batch vs Stream Processing, Consumer Lag
used_by: Stream Processing, Resilient Pipelines, Flow Control
related: Consumer Lag, Apache Flink, Apache Kafka
tags:
  - backpressure
  - flow-control
  - streaming
  - flink
  - resilience
---

# BIG-021 - Backpressure (Streaming)

⚡ TL;DR - **Backpressure** is the mechanism by which a **slow downstream operator signals an upstream operator to slow down** - preventing buffer overflow, data loss, or OOM; in Flink: natural backpressure via TCP credit-based flow control (downstream full buffer → stop requesting data from upstream → upstream slows automatically); in Kafka: consumer lag grows (implicit backpressure - producer doesn't slow down, consumer falls behind); backpressure is a **safety valve** that sacrifices throughput to preserve correctness.

| #560            | Category: Big Data & Streaming                         | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | Apache Flink, Batch vs Stream Processing, Consumer Lag |                 |
| **Used by:**    | Stream Processing, Resilient Pipelines, Flow Control   |                 |
| **Related:**    | Consumer Lag, Apache Flink, Apache Kafka               |                 |

---

### 🔥 The Problem This Solves

**FAST PRODUCER + SLOW CONSUMER = OVERFLOW:**
A Flink streaming job reads from Kafka at 1 million events/second. The downstream database can only accept 100,000 writes/second. Without backpressure: the buffer between the Flink operator and the database sink fills up. Overflow: either messages are dropped (data loss) or the JVM runs out of memory (OOM crash). With backpressure: the database sink signals "I'm full → slow down." The Flink operator upstream throttles. The Kafka source consumer slows down polling. Eventually: the entire pipeline runs at 100,000 events/second - matching the bottleneck. No data loss, no OOM, but reduced throughput.

---

### 📘 Textbook Definition

**Backpressure** is a flow control mechanism in streaming systems where a downstream component that cannot keep up with incoming data signals its upstream components to slow down (or pause) data production.

In **Apache Flink**:

- Uses **credit-based network flow control** (based on TCP-like credits).
- Each downstream TaskManager has a fixed number of input buffer "credits."
- Downstream sends credit grants to upstream: "I have room for N more records."
- Upstream only sends data when it has received credits.
- If downstream is backlogged (buffers full): stops issuing credits → upstream automatically slows down → propagates through the entire DAG to the source.
- **Natural backpressure**: no configuration needed; emerges from the network layer.

In **Apache Kafka** (consumer perspective):

- The producer doesn't "slow down" due to consumer lag (Kafka is a buffer, not a direct stream).
- Backpressure manifests as growing **consumer lag**.
- Consumer implicitly controls its own rate via `max.poll.records` and processing speed.
- To apply upstream rate limiting: use Kafka Streams `maxBytesPerSecond` or consumer-side throttling.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Backpressure = slow consumer tells fast producer "slow down" - prevents buffer overflow and data loss; in Flink: credit-based TCP flow control; in Kafka: consumer controls its own poll rate.

**One analogy:**

> A restaurant kitchen and the waiters. The kitchen (upstream) is cooking 100 orders/hour. The waiters (downstream) can deliver 50 orders/hour. Without backpressure: food piles up on the pass-through until it falls on the floor (data loss) or the kitchen collapses (OOM). With backpressure: head waiter tells kitchen "we're full, slow down." Kitchen cooks 50 orders/hour. No food wasted. System operates at the rate of the slowest component.

**One insight:**
Backpressure is a **feature, not a bug**. A system with effective backpressure gracefully degrades under load - it slows down but stays correct. A system without backpressure crashes under load. The Flink team designed natural backpressure intentionally: you should see it in the Flink dashboard when a downstream operator is slow. Backpressure dashboard metric > 50%: your job is bottlenecked at that operator → fix the bottleneck (scale, optimize), don't suppress backpressure.

---

### 🔩 First Principles Explanation

**FLINK CREDIT-BASED BACKPRESSURE:**

```
Flink Credit-Based Network Flow Control:

TaskManager A (producer):        TaskManager B (consumer):
  [Output Buffer]      →  network  →  [Input Buffer]
  capacity: 50 records              capacity: 50 records

Normal flow:
  B: "I have 50 credits (empty input buffer)" → grants to A
  A: sends up to 50 records → B's buffer fills
  B: processes 50 records (fast DB write) → buffer empties
  B: grants another 50 credits to A
  → Full throughput: 50 records per round trip

Backpressure scenario:
  B's downstream DB becomes slow: B's input buffer fills up
  B: "I have 0 credits (buffer full)" → stops granting credits to A
  A: has records to send but NO credits → STALLS (backpressure)
  A's output buffer fills up
  A: notifies its upstream (source): "I'm full too" → stalls
  Source (Kafka consumer): stops polling from Kafka

  Effect: entire pipeline stalls at the rate of the slowest operator
  (the slow DB write)

  Kafka source: consumer lag starts growing (producer still writes to Kafka,
  consumer paused) - this is visible in monitoring as consumer lag spike

When DB recovers:
  B: processes buffered records → input buffer drains
  B: grants credits to A again
  A: resumes sending
  Pipeline: gradually returns to full throughput
```

**OBSERVING BACKPRESSURE IN FLINK:**

```java
// Flink Web UI: Job → Metrics tab → backpressureRatio per task
// backpressureRatio = fraction of time a task was blocked waiting for credits
// 0.0 = no backpressure (fully flowing)
// 0.5 = task blocked 50% of time → moderate backpressure
// 1.0 = task blocked 100% of time → severe backpressure

// Flink Metrics API (Prometheus integration):
// flink_taskmanager_job_task_isBackPressured
// flink_taskmanager_job_task_backPressureTimeMsPerSecond

// Spring Boot: REST API to check Flink job metrics
@Service
public class FlinkMonitoringService {

    @Scheduled(fixedDelay = 30000)
    public void checkBackpressure() throws Exception {
        HttpClient client = HttpClient.newHttpClient();

        // Flink REST API: get job metrics
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create("http://flink-jobmanager:8081/jobs/" + jobId + "/vertices"))
            .build();

        String response = client.send(request, BodyHandlers.ofString()).body();
        JsonNode vertices = objectMapper.readTree(response).get("vertices");

        for (JsonNode vertex : vertices) {
            double backpressureRatio = vertex.get("metrics")
                .get("backPressuredTimeMsPerSecond").asDouble() / 1000.0;

            if (backpressureRatio > 0.5) {
                log.warn("HIGH BACKPRESSURE: task={}, ratio={}",
                    vertex.get("name").asText(), backpressureRatio);
                // Alert: prometheus counter, PagerDuty
                meterRegistry.gauge("flink.backpressure.ratio",
                    Tags.of("task", vertex.get("id").asText()),
                    backpressureRatio);
            }
        }
    }
}
```

**KAFKA CONSUMER-SIDE RATE LIMITING:**

```java
// Kafka: consumer controls its own processing rate
// No built-in backpressure signal TO the producer
// Producer writes at its own rate; consumer may fall behind

@Component
public class ThrottledOrderConsumer {

    // OPTION 1: max.poll.records - limit how many records per poll
    // This effectively throttles processing rate
    @Bean
    public ConsumerFactory<String, Order> consumerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 100);
        // Read max 100 records per poll() → limits batch processing size
        // If processing 100 records takes 1s: throughput = 100/sec
        return new DefaultKafkaConsumerFactory<>(props);
    }

    // OPTION 2: Kafka Streams fetch.max.bytes / max.poll.records
    props.put(StreamsConfig.MAX_TASK_IDLE_MS_CONFIG, 100);  // wait for data before processing
    props.put(ConsumerConfig.FETCH_MAX_BYTES_CONFIG, 1_048_576);  // 1MB max per fetch

    // OPTION 3: Reactive consumers (Project Reactor Kafka) - true backpressure
    @Bean
    public ReceiverOptions<String, Order> receiverOptions() {
        ReceiverOptions<String, Order> options = ReceiverOptions.<String, Order>create(
            consumerProps()
        ).subscription(Collections.singleton("orders"));
        return options;
    }

    @Bean
    public Disposable kafkaConsumerSubscription(ReactiveKafkaConsumerTemplate<String, Order> template) {
        return template.receive()
            .flatMap(record -> processAsync(record.value()), 10)  // max 10 concurrent
            // flatMap concurrency=10: natural backpressure via reactive streams spec
            // If downstream (processAsync) is slow: flatMap buffers, then stops requesting
            // Reactor: publisher.request(N) → pulls exactly N records → backpressure!
            .subscribe();
    }
}
```

**BACKPRESSURE STRATEGIES:**

```
When backpressure is detected:

STRATEGY 1: Scale up (add more consumers/operators)
  - Add more Flink task slots or TaskManagers
  - Add more Kafka consumer instances (up to partition count)
  - Removes the bottleneck → backpressure goes away
  - Cost: more infrastructure

STRATEGY 2: Optimize the bottleneck
  - Profile what makes the downstream slow
  - Slow DB write → switch to batch writes (batch 100 records per DB call)
  - CPU-intensive operation → vectorized/SIMD processing
  - N+1 DB queries → bulk fetch
  - Removes backpressure by making downstream faster

STRATEGY 3: Accept reduced throughput (let backpressure work)
  - For burst traffic: temporary backpressure is acceptable
  - Kafka acts as buffer: producer writes at full speed, consumers slowly catch up
  - Consumer lag grows during burst, then decreases as traffic normalizes

STRATEGY 4: Drop or sample under load
  - Some use cases: monitoring metrics, user activity tracking
  - Under load: sample 1 in 10 events (90% sampling)
  - Reduces processing load by 90%
  - ONLY for non-critical, high-volume metrics (NEVER for financial transactions)
  - Flink: custom `ProcessFunction` with `AtomicLong counter; counter.incrementAndGet() % 10 == 0`

STRATEGY 5: Circuit breaker
  - Detect downstream unavailable → stop producing (prevent buffer overflow)
  - Resume when downstream recovers
  - Combine with DLQ: circuit-break → route to DLQ → replay when circuit closes
```

---

### 🧪 Thought Experiment

**WHAT HAPPENS IF BACKPRESSURE IS SUPPRESSED?**

Suppose you "fix" backpressure by increasing buffer sizes to "unlimited." The slow downstream DB is still slow. The buffer accumulates. Eventually: 10 million records in-memory → JVM OOM crash. Flink restarts from last checkpoint. During checkpoint recovery: all in-flight (unprocessed) records must be re-read from Kafka → checkpoint offset recovery → process all 10M records again → downstream DB overloaded again → repeat crash cycle.

The "fix" (larger buffers) made the problem worse. Backpressure prevents this by throttling EARLY, keeping buffers manageable, and allowing the system to degrade gracefully instead of catastrophically.

---

### 🧠 Mental Model / Analogy

> Backpressure is like a highway on-ramp metering light. When the highway (downstream) is congested, the on-ramp traffic light (backpressure signal) turns red: cars on the on-ramp (upstream data producers) must stop. Cars don't pile up dangerously on the highway (no buffer overflow). When highway clears, light turns green: on-ramp cars enter. The system always operates within capacity.

> Without backpressure: no ramp metering → cars enter at full speed → highway jams → accidents (system crash).

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Backpressure = downstream slow → upstream stops. Prevents data loss and OOM. Flink: natural (credit-based, automatic). Kafka: consumer controls its own rate (consumer lag = implicit backpressure). See backpressure in Flink UI as metric.

**Level 2:** Flink credit-based: downstream issues credits = "send N records." No credits = upstream stalls. Propagates from sink to source. Entire pipeline throttles to slowest operator rate. Fix: scale the bottleneck, optimize it, or accept reduced throughput.

**Level 3:** Backpressure root causes: slow DB (N+1 queries, unindexed writes), CPU-intensive operations, external HTTP calls (sync, slow), GC pauses (large JVM heap, infrequent GC). Diagnosis: Flink UI → backpressureRatio per task → find the task with highest ratio = bottleneck. Fix that task first (scale/optimize).

**Level 4:** Reactive Streams (Project Reactor, RxJava): formalize backpressure via the `Publisher/Subscriber/Subscription` protocol. `Subscriber.request(N)` explicitly requests N records - publisher can only send what was requested. This makes backpressure a first-class API concept, not just a network-layer behavior. Spring WebFlux + Reactive Kafka: true reactive backpressure for Kafka consumers - only consume as fast as the downstream WebFlux pipeline can process. This is more flexible than Flink's network-layer backpressure for microservice architectures.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ FLINK BACKPRESSURE PROPAGATION                       │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Kafka Source → [Filter] → [Enrich] → [DB Write]    │
│                                         ↑ SLOW      │
│                                                      │
│ DB Write buffer fills up (100% busy):               │
│   DB Write: "0 credits" → Enrich stops receiving   │
│   Enrich buffer fills:                              │
│   Enrich: "0 credits" → Filter stops receiving     │
│   Filter buffer fills:                              │
│   Filter: "0 credits" → Kafka Source stops polling │
│ [BACKPRESSURE ← YOU ARE HERE: upstream throttled]   │
│                                                      │
│ Flink UI: DB Write shows backpressureRatio=1.0      │
│           Enrich: 0.9                               │
│           Filter: 0.8                               │
│           Source: 0.7 (highest = bottleneck = DB)  │
│                                                      │
│ Action: scale DB Write parallelism from 4 to 8     │
│ Result: 2× faster writes → backpressure clears     │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Black Friday surge: backpressure incident

Normal day:
  Producer: 100K orders/sec to Kafka
  Flink job: reads 100K/sec, writes 100K/sec to order DB
  DB: comfortable at 100K/sec
  Backpressure: 0

14:00 Black Friday sale starts:
  Producer: spikes to 1M orders/sec
  Flink: reads 1M/sec from Kafka
  DB: still only handles 100K/sec

14:00:01: DB Write operator buffer fills:
  DB Write: backpressureRatio → 1.0
  Enrich operator: backpressureRatio → 0.9
  Kafka Source: slows poll rate to match DB speed
  Kafka consumer lag: grows (producer writes 1M/sec, consumer does 100K/sec)
  Consumer lag after 1 hour: 1M × 60min × 60sec × 0.9 = 3.24 BILLION events behind

14:05: SRE alert fires: backpressure + consumer lag exceeding threshold
14:07: SRE increases Flink DB Write parallelism: 4 → 20 instances
       Each DB Write instance: handles 50K/sec → 20 × 50K = 1M/sec total
14:08: DB Write throughput = 1M/sec
       Backpressure clears: all operators show 0% backpressure
14:08: Consumer lag starts decreasing (pipeline catches up at 1M/sec)
14:15: Consumer lag = 0 (fully caught up)
14:16: All orders from the Black Friday spike have been processed correctly
       No data loss, no duplicates (EOS + checkpoint recovery)
```

---

### ⚖️ Comparison Table

| System           | Backpressure Mechanism       | Visibility                 | Control                               |
| ---------------- | ---------------------------- | -------------------------- | ------------------------------------- |
| Apache Flink     | Credit-based (automatic)     | Flink UI backpressureRatio | Implicit (propagates naturally)       |
| Kafka (consumer) | Consumer lag (implicit)      | Consumer group lag metrics | Explicit (max.poll.records, throttle) |
| Reactive Streams | request(N) protocol          | Application-level          | Explicit per-subscriber               |
| Spring WebFlux   | Project Reactor backpressure | Actuator metrics           | Implicit (Reactor)                    |
| HTTP (REST)      | 429 Too Many Requests        | HTTP status code           | Explicit (server responds 429)        |

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                                                                                   |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Backpressure = an error that needs to be fixed"             | Backpressure is a feature - it's the system working correctly to prevent data loss. The root cause to fix is the BOTTLENECK (slow downstream), not the backpressure signal itself. Suppressing backpressure (unlimited buffers) just delays the crash                     |
| "Kafka has automatic backpressure from producer to consumer" | Kafka is a decoupled buffer - the producer doesn't slow down because consumers are lagging. Consumer lag IS the Kafka "backpressure" mechanism (consumer falls behind, buffer grows). For actual producer throttling, use Kafka quotas or application-level rate limiting |
| "More parallelism always fixes backpressure"                 | Parallelism is capped by partition count (for Kafka sources) and available hardware. If the bottleneck is a single external system (one DB endpoint), adding more parallel writers just increases load on that system → may make it slower. Optimize the bottleneck first |

---

### 🚨 Failure Modes & Diagnosis

**1. Persistent Backpressure - Job Stuck**

**Symptom:** Flink job shows `backpressureRatio=1.0` for 30+ minutes. Consumer lag growing indefinitely. No recovery.

**Root Cause:** Downstream is permanently slow or unavailable (DB down, network partition to sink).

**Diagnosis:**

```bash
# Flink REST: find which task has highest backpressure
curl http://flink:8081/jobs/{jobId}/vertices/{vertexId}/backpressure

# Response: {"status":"deprecated","backpressure-level":"high","ratio":0.97}
# Shows the bottleneck operator and its ratio

# Check sink reachability:
curl http://order-db:5432/health  # is the DB up?
# If DB is down: fix DB → backpressure clears automatically

# If DB is slow (not down): increase parallelism or optimize query
```

**Fix strategies in order:**

1. Is the sink down? Fix it → immediate backpressure clearing.
2. Sink is slow? Scale sink parallelism (`.setParallelism(20)` for sink operator).
3. Slow per-event processing? Batch writes: accumulate 1000 records, write in one DB call.
4. Still slow? Rate-limit the source temporarily, or implement graceful degradation.

---

### 🔗 Related Keywords

**Prerequisites:** Apache Flink, Consumer Lag
**Builds On This:** Resilient Pipelines, Flow Control
**Related:** Consumer Lag, Apache Flink, Apache Kafka

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DEFINITION  │ Slow downstream → upstream slows down     │
│ FLINK       │ Credit-based TCP flow control (automatic) │
│ KAFKA       │ Consumer lag = implicit backpressure      │
│ METRIC      │ Flink: backpressureRatio (0.0-1.0)       │
│ DIAGNOSE    │ Find highest-ratio task = bottleneck      │
│ FIX         │ Scale, optimize, or batch the bottleneck │
│ DON'T       │ Don't suppress backpressure (→ OOM crash) │
│ REACTIVE    │ request(N) protocol for microservices     │
│ FEATURE     │ Backpressure = system working correctly   │
│ ONE-LINER   │ "Safety valve: fast producer throttled   │
│             │  by slow consumer; Flink: automatic;     │
│             │  Kafka: grow consumer lag = implicit"    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What is backpressure in stream processing? How does Apache Flink implement backpressure automatically? What does a high `backpressureRatio` indicate and what should you do about it?

**Q2.** (TYPE C - Design) A Flink pipeline reads from Kafka (100K events/sec), enriches each event with a Redis cache lookup, and writes results to PostgreSQL. The PostgreSQL sink can only handle 20K writes/sec. Design the complete backpressure strategy: how does Flink handle it automatically, how do you monitor it, how do you scale, and what happens to data during the throttling period?
