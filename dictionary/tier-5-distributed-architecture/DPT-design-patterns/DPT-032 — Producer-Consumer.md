---
layout: default
title: "Producer-Consumer"
parent: "Design Patterns"
nav_order: 32
permalink: /design-patterns/producer-consumer/
id: DPT-032
category: Design Patterns
difficulty: ★★☆
depends_on: Concurrency, BlockingQueue, Thread, Semaphore, Java Concurrency
used_by: Thread Pool Pattern, Message Queue, Work Queues, Async Processing
related: Thread Pool Pattern, Observer, Pipeline Pattern, Bulkhead, BlockingQueue
tags:
  - pattern
  - intermediate
  - concurrency
  - java
  - architecture
---

# DPT-032 — Producer-Consumer

⚡ TL;DR — Producer-Consumer decouples work creation from work execution using a shared queue — producers add tasks, consumers process them independently and at their own pace.

| #792 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Concurrency, BlockingQueue, Thread, Semaphore, Java Concurrency | |
| **Used by:** | Thread Pool Pattern, Message Queue, Work Queues, Async Processing | |
| **Related:** | Thread Pool Pattern, Observer, Pipeline Pattern, Bulkhead, BlockingQueue | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An HTTP server receives upload requests. For each request, the request handler thread directly processes the image: `handler.resizeImage(uploaded)`. When processing takes 500 ms and requests arrive at 200/second, 100 threads are blocked in image processing — HTTP accepting stops because all threads are occupied. A burst of 10 uploads simultaneously blocks 10 threads for 5 seconds each. Users waiting for HTTP responses time out.

**THE BREAKING POINT:**
Work creation (receiving requests) and work execution (resizing images) have very different throughput characteristics. Coupling them forces the slower consumer's rate to limit the faster producer's rate. The server effectively stops accepting connections while processing current work.

**THE INVENTION MOMENT:**
This is exactly why the Producer-Consumer pattern was created. Producers put work into a queue immediately and return. Consumers read from the queue and process in the background. Producers and consumers operate at their own rates, decoupled by the queue.

---

### 📘 Textbook Definition

The **Producer-Consumer** pattern is a concurrency design pattern in which **producer** threads generate work items and place them into a shared **buffer** (queue), while **consumer** threads retrieve and process work items from the buffer. The buffer decouples the producers' creation rate from the consumers' processing rate. When the buffer is full, producers wait; when the buffer is empty, consumers wait. Java's `BlockingQueue` interface (`LinkedBlockingQueue`, `ArrayBlockingQueue`) provides the synchronised buffer with built-in blocking semantics.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A shared queue between work creators and work processors so neither blocks the other.

**One analogy:**
> A restaurant kitchen: waiters (Producers) take orders and place them on a ticket rail (Queue). Chefs (Consumers) pull tickets and cook. A rush of 10 orders doesn't make waiters stand at the stove — they keep taking orders. Chefs work at their own pace. The kitchen doesn't grind to a halt when orders arrive faster than chefs can cook immediately.

**One insight:**
The queue is not just a data structure — it's a rate buffer and a coupling point. It absorbs the difference between production rate and consumption rate, smoothing bursts. Without it, the slower side governs the entire system's throughput.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Work creation and work execution have independent rates.
2. Producers must not block on consumer completion.
3. Consumers must not busy-spin when no work is available.
4. Long-term: production rate must not exceed consumption rate indefinitely (queue grows unbounded → OOM).

**DERIVED DESIGN:**
Given invariants 1+2: producers call `queue.put(item)` (blocking only if queue is full) and return immediately. Consumers call `queue.take()` (blocking only if queue is empty) and process. Producer and consumer threads live on independent thread pools.

Given invariant 3: `BlockingQueue.take()` parks the consumer thread when empty — no CPU spin. This is critical for systems where work is bursty (mostly idle).

Given invariant 4: the queue capacity must be bounded. An unbounded queue allows producers to outpace consumers indefinitely, consuming heap until OOM. `ArrayBlockingQueue(capacity)` provides a bounded queue: producers block when full, creating natural backpressure.

**THE TRADE-OFFS:**
**Gain:** Decoupled production and consumption rates; producers are non-blocking (fast); consumer failures don't crash producers; natural backpressure via bounded queues; easy to scale consumers independently.
**Cost:** Work may be lost on consumer crash (if queue is in-memory); FIFO order not guaranteed under concurrent consumers; queue backlog indicates consumer underscaling; bounded queue blocks producers when consumers are too slow.

---

### 🧪 Thought Experiment

**SETUP:**
Log entry processing: HTTP handlers log events at 10,000/second. Disk writes take 1 ms each (1,000/second max). Direct write: each handler blocks on disk I/O — 10× overload.

**WHAT HAPPENS WITHOUT PRODUCER-CONSUMER:**
10,000 handler threads/second try to write to disk. 9,000 extra threads block waiting for disk. Thread pool exhaustion. HTTP requests time out. Service unavailable.

**WHAT HAPPENS WITH PRODUCER-CONSUMER:**
10,000 log events/second are `queue.offer(entry)` — microsecond operation. 10 consumer threads process the queue at 1,000 events/second total. Queue absorbs the burst. If the queue is bounded (100,000 entries max), at sustained overload producers start blocking at `put()` — backpressure signals callers to slow down. No thread exhaustion; no OOM from unbounded growth.

**THE INSIGHT:**
The queue is the rate shock absorber. Transient bursts (10× for 100 ms) drain without impact. Sustained overload (producers > consumers permanently) requires more consumers — the queue signals this by staying near capacity.

---

### 🧠 Mental Model / Analogy

> Producer-Consumer is like a post office's inbox and sorting floor. Letters (work items) arrive at the intake window (Producer). Sorters (Consumers) process them from the bin (Queue). A mail rush doesn't requires sorters to stand at the window — letters stack up in the bin and sorters work through it. The bin has a size limit — if it's full, the window closes temporarily (backpressure).

- "Intake window" → Producer (HTTP handler, event generator)
- "Letters in the bin" → work items in `BlockingQueue`
- "Bin has a size limit" → `ArrayBlockingQueue(capacity)` — bounded
- "Sorters" → Consumer threads
- "Bin overflows → window closes" → `put()` blocks when queue full
- "No letters — sorters wait" → `take()` blocks when queue empty

Where this analogy breaks down: a post office bin doesn't care about letter ordering. In code, `BlockingQueue` is FIFO — items are processed in order unless parallel consumers process them in different orders.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Producer-Consumer is a "work inbox" pattern. Work creators put tasks in an inbox. Workers pick up tasks from the inbox independently. Neither the sender nor the worker needs to wait for the other.

**Level 2 — How to use it (junior developer):**
Use `BlockingQueue<T>` as the shared buffer. Producer: `queue.put(item)` — blocks if queue full. Consumer loop: `while (true) { T item = queue.take(); process(item); }` — blocks if queue empty. Producers run on one thread pool; consumers run on another. Use `ArrayBlockingQueue` for bounded queues (recommended) and `LinkedBlockingQueue` for practically unbounded. Stop consumers with a poison pill: a sentinel item that tells consumers to exit.

**Level 3 — How it works (mid-level engineer):**
`BlockingQueue.put()` and `take()` use `ReentrantLock` with `Condition` internally. When `put()` finds the queue full it calls `notFull.await()` — releasing the lock and parking the thread. When `take()` removes an item, it calls `notFull.signal()` — unparking one waiting producer. The reverse (empty queue) uses a `notEmpty` condition. This is the classic single-lock, two-condition implementation of a bounded buffer. `LinkedBlockingQueue` uses two separate locks (head lock for `take()`, tail lock for `put()`) to reduce contention under concurrent producers and consumers — head and tail operations don't interfere.

**Level 4 — Why it was designed this way (senior/staff):**
The Producer-Consumer pattern is at the core of every message broker (Kafka, RabbitMQ), every OS scheduler (work queues in Linux kernel), and every thread pool. Java's `ExecutorService` is Producer-Consumer: caller threads (producers) submit `Runnable`/`Callable` tasks to an internal `BlockingQueue`; worker threads (consumers) dequeue and execute them. The design insight of Java's `ThreadPoolExecutor` is that the queue is the primary backpressure mechanism: `LinkedBlockingQueue` (unbounded) lets producers never block; `ArrayBlockingQueue` (bounded) + `CallerRunsPolicy` means producers slow to consumer speed when overloaded. Reactive Streams (Project Reactor) formalise this with explicit backpressure: `Subscriber.request(n)` tells the publisher exactly how many items the consumer can handle — the exact same invariant as a bounded BlockingQueue, but expressed in a declarative pipeline.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────┐
│  PRODUCER-CONSUMER MECHANISM                       │
│                                                    │
│  Producers            Queue          Consumers     │
│  ┌──────────┐        ┌─────┐       ┌──────────┐   │
│  │Thread P1 │─put()──┤     ├─take()─│Thread C1 │  │
│  │Thread P2 │─put()──┤  ●  │        │Thread C2 │  │
│  │Thread P3 │─put()──┤  ●  ├─take()─│Thread C3 │  │
│  └──────────┘        │  ●  │        └──────────┘  │
│                       └─────┘                      │
│  Queue full:          capacity=N                   │
│    P1.put() blocks → waits on notFull condition    │
│                                                    │
│  Queue empty:                                      │
│    C2.take() blocks → waits on notEmpty condition  │
└────────────────────────────────────────────────────┘
```

**Poison pill shutdown:**
```
Producer sends: queue.put(POISON_PILL)
Consumer sees: if (item == POISON_PILL) break;

For N consumers, send N poison pills:
  for (int i = 0; i < consumers; i++)
    queue.put(POISON_PILL);
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
HTTP request arrives → ImageUploadHandler
  → image parsed from request body
  → queue.put(new ImageTask(bytes))
             ← YOU ARE HERE (enqueue, non-blocking)
  → handler returns HTTP 202 Accepted immediately

Consumer thread (background):
  → item = queue.take() (blocks until available)
  → resizeImage(item) → 500ms
  → storeToDisk(item)
  → done (next iteration blocks on take())
```

**FAILURE PATH:**
```
Consumer thread crashes during process(item)
  → item is LOST — queue has no acknowledgement
  → task is silently dropped
Fix: use persistent queue (Kafka, DB-backed queue)
  or: worker-level try/catch + dead-letter queue
```

**WHAT CHANGES AT SCALE:**
At 1 million events/second, an in-process `BlockingQueue` is insufficient (single JVM, bounded memory). Replace with an external message broker (Kafka topic). Producers publish asynchronously; consumers are independently deployable workers with durable subscriptions and at-least-once delivery guarantees. The same Producer-Consumer concept scales from in-process to distributed systems without changing the mental model.

---

### 💻 Code Example

**Example 1 — Basic Producer-Consumer:**
```java
// Shared queue: bounded to prevent OOM
BlockingQueue<String> queue =
    new ArrayBlockingQueue<>(1000);

// Producer thread
Thread producer = new Thread(() -> {
    try {
        for (String item : dataSource) {
            queue.put(item); // blocks if full (backpressure)
        }
        queue.put("POISON"); // signal consumers to stop
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
    }
});

// Consumer thread
Thread consumer = new Thread(() -> {
    try {
        while (true) {
            String item = queue.take(); // blocks if empty
            if ("POISON".equals(item)) break;
            process(item);
        }
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
    }
});

producer.start();
consumer.start();
producer.join();
consumer.join();
```

**Example 2 — Multiple consumers with ExecutorService:**
```java
BlockingQueue<Task> queue =
    new LinkedBlockingQueue<>(5000);

// Multiple producers (HTTP handlers)
ExecutorService producers = Executors.newCachedThreadPool();

// Multiple consumers (workers)
int workerCount = 4;
ExecutorService consumers =
    Executors.newFixedThreadPool(workerCount);

// Start consumers
for (int i = 0; i < workerCount; i++) {
    consumers.submit(() -> {
        while (!Thread.currentThread().isInterrupted()) {
            try {
                Task task = queue.poll(
                    1, TimeUnit.SECONDS); // timeout
                if (task == null) continue; // idle
                task.execute();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    });
}

// Producer submits tasks (from HTTP handlers)
void onRequest(Request req) {
    boolean accepted = queue.offer(
        new Task(req), 100, TimeUnit.MILLISECONDS);
    if (!accepted) {
        throw new ServiceUnavailableException(
            "Work queue full — backpressure");
    }
}
```

**Example 3 — Monitoring queue health:**
```java
// Monitor queue depth as a key metric
@Scheduled(fixedRate = 1000)
void reportQueueDepth() {
    int depth = queue.size();
    int capacity = ((ArrayBlockingQueue<?>)queue).remainingCapacity()
        + depth;
    double fillPercent = 100.0 * depth / capacity;

    metricsRegistry.gauge("queue.depth", depth);
    metricsRegistry.gauge("queue.fill.percent", fillPercent);

    if (fillPercent > 80) {
        log.warn("Queue {}% full — consider adding consumers",
            (int) fillPercent);
    }
}
```

---

### ⚖️ Comparison Table

| Approach | Decoupling | Durability | Scale | Best For |
|---|---|---|---|---|
| **Producer-Consumer (in-process)** | Thread-level | None (in-memory) | Single JVM | Background processing, thread isolation |
| External Message Broker (Kafka) | Service-level | Durable | Multi-node | Distributed async, event streaming |
| Thread Pool (ExecutorService) | Task-level | None | Single JVM | Simple task execution, same process |
| Reactive Streams | Pipeline | None | Single JVM | Backpressure-aware async pipelines |

How to choose: use in-process Producer-Consumer for isolating slow work from fast work within a JVM. Use an external broker when producers and consumers are in different services or durability is required.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Unbounded queue is safer because it never blocks producers | Unbounded queue grows until OOM when consumers are slower than producers. A bounded queue with backpressure is safer at the system level |
| One poison pill stops all consumers | One poison pill stops one consumer. For N consumers, send N poison pills (or use a shutdown flag checked in the consumer loop) |
| Increasing consumer count always improves throughput | If the bottleneck is the queue (put/take contention) or downstream resource (single DB connection), more consumers may not help |
| Producer-Consumer only works for threads, not services | The pattern applies at any granularity: threads (BlockingQueue), services (Kafka topic), processes (Unix pipe) |
| Items in the queue are always processed in order | With multiple concurrent consumers, FIFO enqueue order does not guarantee FIFO processing order — each consumer grabs the next available item independently |

---

### 🚨 Failure Modes & Diagnosis

**1. Queue Saturation — Producers Block Indefinitely**

**Symptom:** HTTP request latency spikes from <5 ms to >10 seconds. Thread dump shows many threads blocked on `queue.put()`.

**Root Cause:** Consumers are processing slower than producers are producing. Bounded queue fills up. Producers block on `queue.put()` — the HTTP handler thread is now stuck in the queue, not handling requests.

**Diagnostic:**
```bash
# Check queue depth metric
curl http://localhost:8080/metrics | grep queue.depth
# Thread dump for blocked threads
jstack <PID> | grep -A 5 "queue.put"
```

**Fix:**
Scale consumers or switch from `put()` (blocking) to `offer()` with timeout and return 429 to caller:
```java
boolean accepted = queue.offer(task, 50, TimeUnit.MILLISECONDS);
if (!accepted) {
    throw new ServiceUnavailableException("Overloaded");
}
```

**Prevention:** Monitor `queue.size() / capacity` — alert at 70%. Add consumer instances automatically via autoscaling.

---

**2. Task Loss on Consumer Crash**

**Symptom:** After a consumer thread throws an exception, tasks are silently lost. Report jobs never complete.

**Root Cause:** Consumer takes item from queue (`item = queue.take()`), then crashes before `process(item)` completes. The item was dequeued but not processed; it's gone.

**Diagnostic:**
```bash
# Count produced vs consumed
metricsRegistry.counter("tasks.produced").increment();
metricsRegistry.counter("tasks.consumed").increment();
# If produced >> consumed over time: tasks are lost
```

**Fix:**
```java
// Wrap consumer with try/catch and dead-letter queue
while (!stopped) {
    Task task = queue.take();
    try {
        process(task);
        metrics.increment("tasks.consumed");
    } catch (Exception e) {
        log.error("Task failed: {}", task.id(), e);
        deadLetterQueue.offer(task); // preserve for retry
    }
}
```

**Prevention:** Use a dead-letter queue for failed tasks. For durability guarantees, use a message broker with ack-based delivery (Kafka consumer offsets, RabbitMQ manual ack).

---

**3. Consumer Thread Leaks on InterruptedException**

**Symptom:** Consumer threads silently exit without replacement. Queue fills with no consumers draining it. Detected by queue depth growing indefinitely.

**Root Cause:** Consumer catches `InterruptedException` and swallows it without exiting or re-interrupting the thread. Thread exits without logging, leaving the consumer pool under-resourced.

**Diagnostic:**
```bash
jstack <PID> | grep -c "Consumer"
# If consumer count decreases over time: thread leak
```

**Fix:**
```java
// BAD: swallows interrupt, thread silently exits
try { queue.take(); } catch (InterruptedException e) { /* oops */ }

// GOOD: restore interrupt flag or propagate exception
try {
    Task item = queue.take();
    process(item);
} catch (InterruptedException e) {
    Thread.currentThread().interrupt(); // restore flag
    log.info("Consumer shutting down gracefully");
    break; // exit loop cleanly
}
```

**Prevention:** Always handle `InterruptedException` by re-interrupting the thread (`Thread.currentThread().interrupt()`) or declaring the method to throw it.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `BlockingQueue` — the Java implementation of the shared buffer; `put()` and `take()` provide the thread-safe blocking semantics the pattern depends on
- `Thread` — producer and consumer run in separate threads; understanding thread lifecycle and interruption is fundamental
- `Concurrency` — Producer-Consumer is a concurrency pattern; understanding race conditions and thread safety motivates why a thread-safe queue is needed

**Builds On This (learn these next):**
- `Thread Pool Pattern` — an `ExecutorService` is a Producer-Consumer: caller threads push tasks to a queue, worker threads consume and execute them
- `Message Broker (Kafka, RabbitMQ)` — distributed Producer-Consumer with durability, acknowledgement, and multi-service decoupling
- `Backpressure (Streaming)` — reactive solution to the bounded-queue problem: consumers signal how much they can accept rather than blocking

**Alternatives / Comparisons:**
- `Observer` — observers react synchronously to events; Producer-Consumer decouples via a queue and allows asynchronous processing
- `Bulkhead` — limits concurrent access to a resource; Producer-Consumer manages work flow rate; both can be combined
- `Reactive Streams` — explicit backpressure via `request(n)`; equivalent to a bounded `BlockingQueue` but expressed declaratively in a pipeline

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Shared queue decoupling work creation     │
│              │ from work execution across threads        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Fast producers block on slow consumers;   │
│ SOLVES       │ burst work exhausts handler threads       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Queue absorbs rate mismatch; bounded      │
│              │ queue provides natural backpressure       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Work creation rate != processing rate;    │
│              │ async background processing needed        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Work must be processed synchronously or   │
│              │ before the caller can continue            │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Throughput decoupling vs task loss risk   │
│              │ and latency between produce and consume   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Receive fast, process at your own pace." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Thread Pool Pattern → Backpressure →      │
│              │ Message Broker (Kafka)                    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A payment processing service uses Producer-Consumer: HTTP request handlers (producers) enqueue payment tasks; 4 consumer threads process them. The queue capacity is 10,000. Load test shows that at 2,000 requests/second, queue depth stabilises at 3,000. At 2,500 req/s, queue depth grows without bound and OOM occurs in 3 minutes. Calculate exactly how many consumer threads are needed to handle 2,500 req/s given current processing time, and describe the monitoring and autoscaling strategy that would prevent the OOM from occurring in production.

**Q2.** A team converts their Producer-Consumer from `ArrayBlockingQueue` (bounded, 5,000 items) to `LinkedBlockingQueue` (unbounded). They argue: "Our consumers are fast enough — the queue will never fill up, so bounding it just blocks producers unnecessarily." Identify the exact failure mode this creates that didn't exist with the bounded queue, describe the condition under which it manifests (it may not manifest for months), and explain what monitoring signal would have caught this risk before the production incident.

