---
layout: default
title: "Producer-Consumer Pattern"
parent: "Java Concurrency"
nav_order: 792
permalink: /java-concurrency/producer-consumer-pattern/
number: "792"
category: Java Concurrency
difficulty: ★★☆
depends_on: BlockingQueue, Thread, ExecutorService
used_by: Task Queues, Pipeline Processing, Event Systems
tags: #java, #concurrency, #pattern, #producer-consumer, #blocking-queue
---

# 792 — Producer-Consumer Pattern

`#java` `#concurrency` `#pattern` `#producer-consumer` `#blocking-queue`

⚡ TL;DR — Producer-Consumer decouples work generation (producers) from work processing (consumers) via a shared buffer — producers add items when available; consumers take items when ready; the buffer absorbs rate differences between the two.

| #792 | Category: Java Concurrency | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | BlockingQueue, Thread, ExecutorService | |
| **Used by:** | Task Queues, Pipeline Processing, Event Systems | |

---

### 📘 Textbook Definition

The **Producer-Consumer** pattern is a concurrency design pattern that separates the concerns of producing data/tasks (producers) from consuming/processing them (consumers) through a shared bounded or unbounded buffer. Producers add items to the buffer; consumers remove and process items. The buffer decouples producer and consumer rates — producers block when the buffer is full; consumers block when the buffer is empty. In Java, `BlockingQueue` implementations provide the idiomatic buffer with built-in blocking semantics.

---

### 🟢 Simple Definition (Easy)

A bakery (producer) puts bread on a shelf (queue). Customers (consumers) take bread from the shelf. The shelf holds a limited number of loaves. If the shelf is full, bakers wait. If the shelf is empty, customers wait. Bakers and customers work at their own pace, independent of each other — the shelf absorbs the difference.

---

### 🔵 Simple Definition (Elaborated)

Without this pattern, producers call consumers directly — tight coupling, brittle, rate-sensitive. With producer-consumer: the queue absorbs bursts (producer spike → queue fills; consumer catches up later). Multiple producers can feed into one queue; multiple consumers can drain it — easy to scale each side independently. The pattern shows up everywhere: HTTP request queues → thread pools, Kafka topics, database connection pools, async logging, batch ETL pipelines.

---

### 🔩 First Principles Explanation

```
Problem: producer generates work faster than consumer processes it
  Direct call: producer.produce() → consumer.process()
    → If consumer is slow → producer blocks (or data is lost)
    → Tight coupling: producer must know about consumer

  Shared counter (naive):
    shared_queue.add(item) [producer]
    shared_queue.remove()  [consumer]
    → Race condition without synchronization
    → Manual wait/notify = brittle, 30+ lines

  BlockingQueue solution:
    queue.put(item)   [producer  — blocks if full]
    queue.take()      [consumer  — blocks if empty]
    → Built-in blocking, signalling, thread-safety
    → Decoupling: producer and consumer only know about the queue

Rate absorption:
  Producer: 1000 items/sec
  Consumer: 800 items/sec
  Buffer (queue capacity = 10,000):
    → Queue fills over time
    → Producer backs off when queue full (backpressure)
    → Consumer drains queue during producer idle periods
```

---

### 🧠 Mental Model / Analogy

> A toll booth on a highway. Cars (work items) arrive from the highway (producer). The toll collector (consumer) processes cars one at a time. During rush hour, cars queue up. During off-peak, the queue drains. The queue (buffer) absorbs the mismatch. Adding more toll lanes (consumers) increases throughput. The highway doesn't need to know how many toll lanes exist.

---

### ⚙️ How It Works — Variants

```
Classic:
  1 producer  + 1 consumer  + bounded queue → simple P/C
  N producers + M consumers + bounded queue → parallel P/C

Pipeline (chained):
  Stage1 → Queue1 → Stage2 → Queue2 → Stage3
  Each stage is both consumer of previous queue and producer to next queue
  → Streaming processing pipeline

Poison pill (shutdown):
  Producer sends a special sentinel value (null or a specific object)
  Consumer receives sentinel → exits loop
  → Clean shutdown without external interruption

Drain and stop:
  Producer sets a volatile flag
  Consumer checks flag and drains remaining items
```

---

### 🔄 How It Connects

```
Producer-Consumer
  │
  ├─ Buffer  → BlockingQueue (ArrayBlockingQueue, LinkedBlockingQueue)
  ├─ vs direct call → decouples rates; enables independent scaling
  ├─ Pattern in:
  │   Kafka/RabbitMQ    → distributed version of P/C
  │   ExecutorService   → task queue IS a bounded P/C
  │   Log4j AsyncAppender → logs produced by app, consumed by I/O thread
  │   Spring @Async     → method call queued, consumed by thread pool
  └─ Backpressure → bounded queue blocks producer when full (natural backpressure)
```

---

### 💻 Code Example

```java
// Classic single producer, multiple consumers
BlockingQueue<String> queue = new ArrayBlockingQueue<>(100);
ExecutorService pool = Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors() + 1);

// Producer
pool.submit(() -> {
    try {
        for (String task : generateTasks()) {
            queue.put(task);          // blocks if queue is at capacity
        }
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
    }
});

// Multiple consumers
int consumers = 4;
CountDownLatch doneLatch = new CountDownLatch(consumers);
for (int i = 0; i < consumers; i++) {
    pool.submit(() -> {
        try {
            while (!Thread.currentThread().isInterrupted()) {
                String task = queue.poll(1, TimeUnit.SECONDS);
                if (task == null) break; // timeout — producer likely done
                processTask(task);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            doneLatch.countDown();
        }
    });
}
doneLatch.await();
pool.shutdown();
```

```java
// Poison pill shutdown pattern
static final String POISON = "__DONE__";

// Producer
pool.submit(() -> {
    generateTasks().forEach(t -> { try { queue.put(t); } catch (InterruptedException e) {} });
    // Send one poison pill per consumer
    for (int i = 0; i < consumers; i++) {
        try { queue.put(POISON); } catch (InterruptedException e) {}
    }
});

// Consumer
pool.submit(() -> {
    while (true) {
        String item = queue.take();
        if (POISON.equals(item)) break; // graceful shutdown
        processTask(item);
    }
});
```

```java
// Pipeline: parse → validate → persist
BlockingQueue<RawRecord>   parseQueue    = new ArrayBlockingQueue<>(500);
BlockingQueue<ValidRecord> validateQueue = new ArrayBlockingQueue<>(500);

// Stage 1: Reader → parseQueue
pool.submit(() -> files.forEach(f -> parseQueue.put(parse(f))));

// Stage 2: Validator: parseQueue → validateQueue
pool.submit(() -> {
    while (true) {
        RawRecord r = parseQueue.take();
        if (r.isPoison()) { validateQueue.put(ValidRecord.POISON); break; }
        validateQueue.put(validate(r));
    }
});

// Stage 3: Persister: validateQueue → DB
pool.submit(() -> {
    while (true) {
        ValidRecord v = validateQueue.take();
        if (v.isPoison()) break;
        db.save(v);
    }
});
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Unbounded queue prevents producer blocking | Unbounded queue → OOM if consumer is permanently slower than producer |
| One consumer is always enough | Consumers should match the processing rate; scale consumers independently of producers |
| Poison pill is the only shutdown method | Also: interrupt all threads; timed poll and check volatile flag; drain then stop |
| The queue size doesn't matter | Too small → producer blocks frequently (bottleneck); too large → OOM risk |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Unbounded queue + slow consumers = OOM**

```java
// ❌ LinkedBlockingQueue default capacity = Integer.MAX_VALUE
BlockingQueue<Task> queue = new LinkedBlockingQueue<>();
// Producer outpaces consumer → queue grows → OOM in hours

// ✅ Always bound the queue; choose capacity based on processing rate
BlockingQueue<Task> queue = new ArrayBlockingQueue<>(1000); // backpressure at 1000
```

**Pitfall 2: Not handling InterruptedException in consumer loop**

```java
// ❌ Exception swallowed → consumer silently exits → queue fills → producer blocks forever
while (running) {
    try { process(queue.take()); }
    catch (InterruptedException e) {} // loop continues but flag not set
}
// ✅
catch (InterruptedException e) { Thread.currentThread().interrupt(); break; }
```

---

### 🔗 Related Keywords

- **[BlockingQueue](./081 — BlockingQueue.md)** — the canonical buffer implementation
- **[CountDownLatch](./078 — CountDownLatch.md)** — coordinate producer/consumer shutdown
- **[Semaphore](./080 — Semaphore.md)** — alternative for manual resource pooling
- **[ExecutorService](./074 — ExecutorService.md)** — ExecutorService IS a producer-consumer internally

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Decouple data generation from processing via  │
│              │ a shared bounded buffer — absorbs rate diffs  │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Producer and consumer at different rates; I/O │
│              │ pipeline stages; async task processing        │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Unbounded queues under sustained overload;    │
│              │ tight latency SLAs (queue adds latency)       │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Don't call directly — put on the shelf,      │
│              │  take from the shelf; shelf absorbs the gap"  │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ BlockingQueue → ExecutorService internals →   │
│              │ Kafka (distributed P/C) → Reactive Streams    │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have 1 producer generating 1000 items/sec and 4 consumers each processing 200 items/sec (total: 800/sec). With a bounded queue of 10,000, approximately how long before the system reaches steady state or runs into problems? What happens at that point?

**Q2.** The poison pill pattern sends N poison pills for N consumers. What happens if a consumer re-queues the poison pill instead of exiting? Is this ever intentional?

**Q3.** Apache Kafka is essentially a distributed, persistent producer-consumer system. What properties does Kafka add beyond a simple BlockingQueue that make it suitable for production systems? (Think: durability, replay, consumer groups, ordering guarantees.)

