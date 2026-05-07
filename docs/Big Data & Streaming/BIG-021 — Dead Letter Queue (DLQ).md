---
layout: default
title: "Dead Letter Queue (DLQ)"
parent: "Big Data & Streaming"
nav_order: 21
permalink: /big-data-streaming/dead-letter-queue/
number: "BIG-021"
category: Big Data & Streaming
difficulty: ★★☆
depends_on: Apache Kafka, Consumer Group, Message Ordering
used_by: Error Handling, Resilient Pipelines, Observability
related: Consumer Group, Consumer Lag, Fan-Out Pattern
tags:
  - dlq
  - dead-letter-queue
  - error-handling
  - kafka
  - resilience
---

# BIG-021 — Dead Letter Queue (DLQ)

⚡ TL;DR — A **Dead Letter Queue (DLQ)** is a special queue or Kafka topic where messages that **cannot be processed** (invalid format, downstream error, repeated failures) are routed instead of blocking the main pipeline — prevents one bad message ("poison pill") from stopping all processing; Spring Kafka's `@RetryableTopic` automatically creates retry topics (`topic.RETRY-0`, `topic.RETRY-1`) and a DLT (`topic.DLT`) with configurable backoff; messages in DLQ are investigated and replayed or discarded manually.

| #551            | Category: Big Data & Streaming                     | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------- | :-------------- |
| **Depends on:** | Apache Kafka, Consumer Group, Message Ordering     |                 |
| **Used by:**    | Error Handling, Resilient Pipelines, Observability |                 |
| **Related:**    | Consumer Group, Consumer Lag, Fan-Out Pattern      |                 |

---

### 🔥 The Problem This Solves

**ONE BAD MESSAGE BLOCKS ALL PROCESSING:**
Your Kafka consumer processes orders. Someone sends a malformed JSON event — the consumer throws a `JsonParseException`. The consumer commits no offset. Kafka replays the same message. Exception again. Kafka replays. This "poison pill" message loops forever: your consumer processes ZERO new orders while replaying a message it can never succeed on. Consumer lag grows by thousands while the poison pill cycles. The DLQ routes unreprocessable messages aside — the pipeline continues processing good messages.

---

### 📘 Textbook Definition

A **Dead Letter Queue (DLQ)** (also called Dead Letter Topic in Kafka) is a destination for messages that fail processing after exhausting retry attempts:

1. **Consumer receives message M from topic T.**
2. **Processing fails** (exception thrown).
3. **Retry**: consumer retries N times (with optional backoff).
4. **Exhausted retries**: message is routed to a DLQ topic (e.g., `T.DLT`).
5. **Main pipeline continues**: M is no longer blocking; consumer advances to the next message.
6. **DLQ consumers**: separate consumers monitor the DLQ — alert on new entries, investigate root causes, manually replay or discard.

In Spring Kafka, the `@RetryableTopic` annotation implements a **retry topic pattern**: messages that fail are sent to retry topics with increasing delays before landing in the DLT (Dead Letter Topic):

```
main-topic → [fail] → main-topic-RETRY-0 (delay 1s)
           → [fail] → main-topic-RETRY-1 (delay 5s)
           → [fail] → main-topic-DLT
```

---

### ⏱️ Understand It in 30 Seconds

**One line:**
DLQ = "parking lot for broken messages" — failed messages go here instead of blocking the main pipeline; investigate and replay later.

**One analogy:**

> Post office sorting: most packages routed to correct departments. A package with illegible address → "undeliverable mail" bin (DLQ). Post office doesn't stop sorting because of one bad package. Someone from undeliverable mail team investigates: fix address, re-deliver, or return to sender.

**One insight:**
The key design question: **what counts as DLQ-worthy?** Two categories of failures need different handling:

- **Transient failures** (DB temporarily down, network timeout): should RETRY with backoff — eventually succeed. Don't DLQ these.
- **Permanent failures** (invalid message format, business rule violation, schema mismatch): will NEVER succeed no matter how many retries. These belong in the DLQ immediately.

Good DLQ design distinguishes these two types. Retry-then-DLQ handles the mixed case: retry N times for transient failures; DLQ after N failures (assuming either it's permanent or the transient issue isn't resolving).

---

### 🔩 First Principles Explanation

**SPRING KAFKA @RetryableTopic (RECOMMENDED PATTERN):**

```java
@Component
public class OrderEventConsumer {

    private final OrderService orderService;

    // @RetryableTopic creates retry topics automatically:
    // Attempts: 1 main + 2 retries + 1 DLT = 4 total
    // Backoff: attempt 1 immediately, attempt 2 after 1s, attempt 3 after 5s → DLT
    @RetryableTopic(
        attempts = "3",  // 3 total attempts (1 main + 2 retries)
        backoff = @Backoff(delay = 1000, multiplier = 2.0, maxDelay = 30000),
        // → Retry 1: 1000ms delay, Retry 2: 2000ms delay

        autoCreateTopics = "true",  // creates retry and DLT topics automatically
        topicSuffixingStrategy = TopicSuffixingStrategy.SUFFIX_WITH_INDEX_VALUE,
        // Creates: orders-RETRY-0, orders-RETRY-1, orders-DLT

        // IMPORTANT: Classify which exceptions should NOT retry (go straight to DLT):
        exclude = {
            SerializationException.class,     // never retry deserialization failures
            IllegalArgumentException.class    // never retry validation failures
        }
        // Everything else: retry up to 3 attempts, then DLT
    )
    @KafkaListener(topics = "orders")
    public void handleOrder(Order order, @Header(KafkaHeaders.RECEIVED_TOPIC) String topic) {
        log.info("Processing order {} from topic {}", order.getId(), topic);
        orderService.process(order);  // throws if processing fails
    }

    // DLT Handler: runs when message arrives in DLT (after exhausted retries)
    @DltHandler
    public void handleDlt(Order order,
                          @Header(KafkaHeaders.RECEIVED_TOPIC) String topic,
                          @Header(KafkaHeaders.EXCEPTION_MESSAGE) String errorMsg,
                          @Header(KafkaHeaders.ORIGINAL_TIMESTAMP) long originalTimestamp) {
        log.error("Order {} sent to DLT from {} after all retries. Error: {}",
                  order.getId(), topic, errorMsg);

        // Actions in DLT handler:
        // 1. Alert on-call (PagerDuty, Slack)
        // 2. Store in database for investigation
        // 3. Metrics (increment DLT counter for alerting)
        deadLetterRepository.save(DeadLetterEntry.builder()
            .messageId(order.getId())
            .topic(topic)
            .errorMessage(errorMsg)
            .originalTimestamp(Instant.ofEpochMilli(originalTimestamp))
            .payload(order)
            .build());

        meterRegistry.counter("kafka.dlq.entries", "topic", "orders").increment();
    }
}
```

**MANUAL DLQ PATTERN (without @RetryableTopic):**

```java
@KafkaListener(topics = "orders")
public void handleOrder(ConsumerRecord<String, Order> record) {
    try {
        orderService.process(record.value());

    } catch (TransientException e) {
        // Transient failure: retry by NOT committing offset
        // (Kafka will re-deliver this message on next poll)
        // But: be careful — this blocks processing of subsequent messages on this partition
        // Better: use @RetryableTopic for non-blocking retries
        throw e;  // Spring Kafka: exception → no offset commit → re-deliver

    } catch (PermanentException e) {
        // Permanent failure: send to DLQ and commit offset (pipeline continues)
        sendToDlq(record, e);
        // Offset IS committed → this message won't be re-processed

    } catch (Exception e) {
        // Unknown: treat as retriable; after max retries, send to DLQ
        retryOrDlq(record, e);
    }
}

private void sendToDlq(ConsumerRecord<String, Order> record, Exception cause) {
    // Preserve original message headers + add error context:
    List<Header> headers = new ArrayList<>(Arrays.asList(record.headers().toArray()));
    headers.add(new RecordHeader("dlq-source-topic", record.topic().getBytes()));
    headers.add(new RecordHeader("dlq-source-partition",
        ByteBuffer.allocate(4).putInt(record.partition()).array()));
    headers.add(new RecordHeader("dlq-source-offset",
        ByteBuffer.allocate(8).putLong(record.offset()).array()));
    headers.add(new RecordHeader("dlq-error-message",
        cause.getMessage() != null ? cause.getMessage().getBytes() : "null".getBytes()));
    headers.add(new RecordHeader("dlq-timestamp",
        Instant.now().toString().getBytes()));

    ProducerRecord<String, Order> dlqRecord = new ProducerRecord<>(
        record.topic() + ".DLT",
        null,
        record.key(),
        record.value(),
        headers
    );
    kafkaTemplate.send(dlqRecord);

    log.error("Sent message {} to DLQ. Original offset {}-{}",
              record.key(), record.partition(), record.offset());
}
```

**MONITORING AND REPLAY:**

```bash
# Monitor DLQ size (consumer group that just reads but doesn't process = "monitor group"):
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group dlq-monitor --describe

# Manual replay: consume from DLQ and re-produce to original topic
# (after fixing the root cause)
kafka-console-consumer \
  --bootstrap-server kafka:9092 \
  --topic orders-DLT \
  --from-beginning \
  --max-messages 100 | \
kafka-console-producer \
  --bootstrap-server kafka:9092 \
  --topic orders

# Spring Boot DLQ replay endpoint (admin endpoint):
@PostMapping("/admin/dlq/replay/{topic}")
public ResponseEntity<String> replayDlq(@PathVariable String topic,
                                         @RequestParam int maxMessages) {
    // Consume from {topic}-DLT, republish to {topic}
    // Only after root cause is fixed!
    dlqReplayService.replay(topic + "-DLT", topic, maxMessages);
    return ResponseEntity.ok("Replayed " + maxMessages + " messages");
}
```

---

### 🧪 Thought Experiment

**DLQ vs SKIP vs BLOCK — THE THREE STRATEGIES:**

| Strategy               | Behavior                                | When to Use                                             |
| ---------------------- | --------------------------------------- | ------------------------------------------------------- |
| Block (retry forever)  | Pipeline stalls on failure              | NEVER — this is the poison pill problem                 |
| Skip (ignore failures) | Failed messages silently dropped        | Low-value data (metrics, logs) where loss is acceptable |
| DLQ                    | Failed messages parked for later review | Business-critical data — must not lose, must not block  |

The DLQ pattern is a tradeoff: you preserve the message (no data loss) while unblocking the pipeline. The "debt" is the DLQ queue that grows if root causes aren't fixed. A full DLQ is a silent failure mode — alerting on DLQ entry rate is essential.

---

### 🧠 Mental Model / Analogy

> DLQ is like a hospital triage system with an "observation room." Most patients (messages) are processed immediately (main topic). Patients who can't be immediately treated (failed messages) go to observation (retry topics). After multiple failed treatment attempts, they go to intensive care (DLT) — where specialists investigate and decide next steps (replay, discard, escalate). The ER doesn't stop because one patient is in observation.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** DLQ = poison pill messages go here instead of blocking the pipeline. Use `@RetryableTopic` in Spring Kafka. Retry N times then DLT. Add `@DltHandler` to alert and store DLT messages.

**Level 2:** Classify exceptions: permanent (ValidationException → DLT immediately) vs transient (NetworkException → retry). `@RetryableTopic(exclude=...)` for permanent exceptions. DLT handler persists to DB + alerts. Monitor DLT entry rate.

**Level 3:** Retry topics (`orders-RETRY-0`, `orders-RETRY-1`) are real Kafka topics. Each retry topic has its own consumer group. Messages flow: main → retry-0 (wait 1s) → retry-1 (wait 5s) → DLT. This is non-blocking: the main topic consumer continues while retried messages wait in retry topics. Backoff is implemented by the retry consumer delaying before re-processing.

**Level 4:** DLQ in event-sourced systems: a DLQ message may have side effects that have partially applied (e.g., DB updated, email sent, but Kafka publish failed). Replaying from DLQ could re-trigger those side effects. Solution: idempotent processors (deduplicate by message ID) + exactly-once design. Before replaying from DLQ: verify no partial side effects have occurred. Consider compensating events if partial processing happened.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ RETRY TOPIC PATTERN (@RetryableTopic)                │
├──────────────────────────────────────────────────────┤
│                                                      │
│ "orders" topic:                                     │
│  [M1][M2][M3-BAD][M4][M5]                          │
│             ↓ fails                                  │
│ "orders-RETRY-0" (delay 1s):                       │
│  [M3-BAD]                                           │
│             ↓ fails again                            │
│ "orders-RETRY-1" (delay 5s):                        │
│  [M3-BAD]                                           │
│             ↓ fails 3rd time                         │
│ "orders-DLT":                                       │
│  [M3-BAD + error headers]                           │
│ [DLQ ← YOU ARE HERE: dead letter holding area]      │
│                                                      │
│ Main pipeline: M1, M2, M4, M5 processed normally   │
│ M3-BAD parked in DLT, pipeline not blocked         │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Poison pill incident response:

T=0: Consumer receives M3: {"orderId": null, "amount": "notanumber"}
T=1: process(M3) → JsonParseException (permanent failure)
T=2: @RetryableTopic: exception is in `exclude` list → skip retries → send to orders-DLT immediately
T=3: M3 headers: dlq-source-topic=orders, dlq-error=JsonParseException, dlq-timestamp=...
T=4: @DltHandler: stores M3 in dead_letter_entries table, increments DLT counter metric
T=5: Alertmanager fires: "kafka.dlq.entries{topic=orders}" > 0
T=6: On-call SRE investigates: bad JSON from upstream service
T=7: Upstream service bug fixed
T=8: DLT has 5 messages (all from the bad upstream deployment)
T=9: Admin endpoint: POST /admin/dlq/replay/orders?maxMessages=5
     → Messages re-published to "orders" topic
     → This time: processed successfully (upstream fixed, valid JSON)
T=10: DLT: empty (5 messages replayed, processed successfully)
```

---

### ⚖️ Comparison Table

| Approach              | Behavior on Failure                | Message Loss | Pipeline Block    |
| --------------------- | ---------------------------------- | ------------ | ----------------- |
| Retry forever         | Retries indefinitely               | No           | YES (poison pill) |
| Discard on failure    | Drop failed messages               | YES          | No                |
| DLQ (retry-then-park) | Retry N times, then park           | No           | No                |
| Circuit breaker + DLQ | Stop calling failing service + DLQ | No           | No (fast-fail)    |

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                                                                                                                |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "DLQ means message loss is prevented completely" | DLQ stores the message — but if you never process the DLQ (no DLT consumer, no replay), messages accumulate and become invisible to the main pipeline. DLQ is only as useful as your DLT monitoring and replay process                 |
| "@RetryableTopic retries use the main partition" | Retry topics are SEPARATE Kafka topics. The main topic consumer advances to the next message immediately. Retries happen asynchronously via the retry topic consumer. This is the non-blocking advantage                               |
| "DLQ handles all failure modes"                  | DLQ handles consumer-side processing failures. It doesn't help with: serialization failures before the consumer (need Schema Registry), broker failures (Kafka availability), or producer-side failures (need producer error handling) |

---

### 🚨 Failure Modes & Diagnosis

**1. DLQ Growing Without Being Consumed**

**Symptom:** `kafka.dlq.entries` metric climbing. No one reading from DLT. Dead letters piling up.

**Root Cause:** DLT handler not alerting; on-call doesn't know DLT has messages; no DLT monitoring setup.

**Fix:**

1. Alert on DLT entry rate: `kafka_consumergroup_lag{topic="orders-DLT"} > 0` → PagerDuty.
2. Separate DLT consumer group with periodic health check.
3. Dashboard showing DLT entry counts per topic.
4. SLA: DLT messages must be investigated within 2 hours.

**2. Retry Storm — Transient Failure Amplification**

**Symptom:** DB is down for 5 minutes. All consumers retry simultaneously. When DB recovers: 10,000 retries hit simultaneously → DB overwhelmed again.

**Fix:** Exponential backoff with jitter in `@RetryableTopic`:

```java
@RetryableTopic(
    attempts = "5",
    backoff = @Backoff(delay = 1000, multiplier = 2.0, random = true)
    // random=true adds jitter to backoff → distributes retry load
)
```

---

### 🔗 Related Keywords

**Prerequisites:** Apache Kafka, Consumer Group
**Builds On This:** Error Handling, Resilient Pipelines
**Related:** Consumer Group, Consumer Lag, Fan-Out Pattern

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PURPOSE     │ Park failed messages; prevent poison pills │
│ SPRING      │ @RetryableTopic + @DltHandler              │
│ TOPICS      │ topic → topic-RETRY-0..N → topic-DLT      │
│ NON-BLOCK   │ Retry topics are separate; main continues │
│ EXCLUDE     │ Permanent exceptions → DLT immediately    │
│ DLT HANDLER │ Alert + store in DB for investigation     │
│ MONITOR     │ Alert on DLT entry count > 0              │
│ REPLAY      │ Fix root cause FIRST, then replay from DLT│
│ JITTER      │ random=true in backoff → avoid retry storm│
│ ONE-LINER   │ "Poison pills parked in DLT; main        │
│             │  pipeline unblocked; investigate + replay" │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What is a "poison pill" in Kafka? How does a DLQ (Dead Letter Queue/Topic) solve the poison pill problem? What is the difference between retry topics and the DLT?

**Q2.** (TYPE C — Design) A payment processing consumer receives events that call an external payment gateway. Design a DLQ strategy that: handles transient gateway failures (retry with backoff), handles permanent invalid payment events (DLT immediately), prevents retry storms, and provides a safe replay mechanism.
