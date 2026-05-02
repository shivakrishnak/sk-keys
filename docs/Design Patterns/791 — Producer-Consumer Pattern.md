---
layout: default
title: "Producer-Consumer Pattern"
parent: "Design Patterns"
nav_order: 791
permalink: /design-patterns/producer-consumer-pattern/
number: "791"
category: Design Patterns
difficulty: ★★★
depends_on: "Thread Safety, BlockingQueue, Object Pool Pattern, Thread Pool Pattern"
used_by: "Task queues, message brokers, batch processing, log pipelines, async systems"
tags: #advanced, #design-patterns, #concurrency, #threading, #queue, #async
---

# 791 — Producer-Consumer Pattern

`#advanced` `#design-patterns` `#concurrency` `#threading` `#queue` `#async`

⚡ TL;DR — **Producer-Consumer** decouples producers (that create work items) from consumers (that process them) via a shared, thread-safe queue — enabling independent scaling, buffering rate differences, and asynchronous processing.

| #791            | Category: Design Patterns                                                    | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Thread Safety, BlockingQueue, Object Pool Pattern, Thread Pool Pattern       |                 |
| **Used by:**    | Task queues, message brokers, batch processing, log pipelines, async systems |                 |

---

### 📘 Textbook Definition

**Producer-Consumer**: a classic concurrency design pattern where one or more producer threads generate data/work items and place them into a shared buffer (queue), while one or more consumer threads retrieve and process items from the buffer. The buffer decouples producers from consumers: they operate at different rates, in different threads, without direct communication. Classic implementations: `BlockingQueue` (producers call `put()`, blocking if full; consumers call `take()`, blocking if empty). Modern Java: `ExecutorService` (producer = submitter, consumer = thread pool). Message broker (Kafka, RabbitMQ): distributed Producer-Consumer with persistent queue. The pattern solves: rate mismatch (bursty producers vs steady consumers), parallel processing (multiple consumers), back-pressure (full queue blocks producers).

---

### 🟢 Simple Definition (Easy)

A restaurant kitchen. Waiters (producers) take orders and place them on a ticket rail (queue). Cooks (consumers) pick up tickets and prepare the food. Waiter doesn't wait for the cook — places ticket and moves on (takes more orders). Cook doesn't wait for waiter — picks up next ticket when ready. If kitchen is overwhelmed (queue full): new orders wait (back-pressure). If no orders (queue empty): cooks wait. Producer-Consumer: decoupled by the queue.

---

### 🔵 Simple Definition (Elaborated)

Log pipeline: application threads (producers) generate log events at ~100,000/sec. Log appender (consumer) writes to disk at ~10,000 entries/sec. Without Producer-Consumer: every application thread blocks on disk I/O — 10× slowdown. With Producer-Consumer: application threads put log events on a `BlockingQueue`. A single appender thread takes from queue, batches writes, flushes to disk. Application threads: never blocked on I/O. Logback's async appender is exactly this. Rate mismatch absorbed by queue (bounded to prevent memory exhaustion).

---

### 🔩 First Principles Explanation

**BlockingQueue coordination, back-pressure, and bounded buffers:**

```
BASIC PRODUCER-CONSUMER WITH BlockingQueue:

  BlockingQueue<Task> queue = new LinkedBlockingQueue<>(100);  // bounded: max 100 items

  // PRODUCER thread:
  class Producer implements Runnable {
      @Override
      public void run() {
          while (!Thread.currentThread().isInterrupted()) {
              Task task = generateTask();             // create work item
              try {
                  queue.put(task);                    // blocking put: if queue full, waits
                  // Back-pressure: producer slows when consumer can't keep up
              } catch (InterruptedException e) {
                  Thread.currentThread().interrupt(); // restore interrupt flag
                  break;
              }
          }
      }
  }

  // CONSUMER thread:
  class Consumer implements Runnable {
      @Override
      public void run() {
          while (!Thread.currentThread().isInterrupted()) {
              try {
                  Task task = queue.take();           // blocking take: if queue empty, waits
                  processTask(task);
              } catch (InterruptedException e) {
                  Thread.currentThread().interrupt();
                  break;
              }
          }
      }
  }

  // Multiple producers + multiple consumers (N:M Producer-Consumer):
  ExecutorService producers = Executors.newFixedThreadPool(3);  // 3 producers
  ExecutorService consumers = Executors.newFixedThreadPool(5);  // 5 consumers

  IntStream.range(0, 3).forEach(i -> producers.submit(new Producer()));
  IntStream.range(0, 5).forEach(i -> consumers.submit(new Consumer()));

BLOCKINGQUEUE VARIANTS:

  LinkedBlockingQueue<T>(capacity):
    Bounded FIFO queue. Separate locks for put and take (better concurrency).
    ✓ General-purpose; most common.

  ArrayBlockingQueue<T>(capacity):
    Bounded array-backed FIFO. Single lock (put and take compete).
    ✓ Better memory locality; predictable capacity.

  PriorityBlockingQueue<T>:
    Unbounded; consumers take HIGHEST-PRIORITY item (not FIFO).
    ✓ Task scheduling by priority.
    ⚠ No back-pressure (unbounded!).

  SynchronousQueue<T>:
    Zero-capacity queue. put() blocks until take() is ready (rendezvous).
    ✓ Direct handoff: producer waits until consumer is ready.
    Used by: Executors.newCachedThreadPool()

  DelayQueue<T extends Delayed>:
    Consumer can only take items whose delay has expired.
    ✓ Scheduled task execution.

PRODUCER-CONSUMER WITH EXECUTORSERVICE (COMMON PATTERN):

  // ExecutorService IS a Producer-Consumer:
  // Producer: code that calls submit()/execute()
  // Consumer: worker threads in the pool
  // Queue: the work queue (LinkedBlockingQueue by default for fixed pools)

  ExecutorService pool = Executors.newFixedThreadPool(4);

  // Producers submit tasks from multiple threads:
  Future<Result> f1 = pool.submit(() -> processItem(item1));
  Future<Result> f2 = pool.submit(() -> processItem(item2));
  // ... many more ...

  // Consumers (4 threads): pick up and execute tasks from the queue

  // Shutdown: stop accepting new tasks; finish existing ones:
  pool.shutdown();
  pool.awaitTermination(60, TimeUnit.SECONDS);

KAFKA AS DISTRIBUTED PRODUCER-CONSUMER:

  // Kafka: scalable, persistent, distributed Producer-Consumer queue.

  // Producer (Spring Kafka):
  @Service
  class OrderProducer {
      @Autowired KafkaTemplate<String, OrderEvent> kafka;

      void publishOrderPlaced(Order order) {
          kafka.send("orders.placed", order.getId(), new OrderPlacedEvent(order));
          // Non-blocking: message written to Kafka broker — producer continues immediately
      }
  }

  // Consumer (Spring Kafka):
  @Component
  class OrderConsumer {
      @KafkaListener(topics = "orders.placed", groupId = "inventory-service")
      void processOrderPlaced(OrderPlacedEvent event) {
          inventoryService.reserve(event.getOrderId());
      }

      // Multiple consumers in same group = parallel consumption of partitions:
      @KafkaListener(topics = "orders.placed", groupId = "notification-service")
      void notifyOrderPlaced(OrderPlacedEvent event) {
          emailService.sendOrderConfirmation(event.getOrderId());
      }
  }

BACK-PRESSURE:

  UNBOUNDED queue: producers never blocked. If consumers fall behind:
  → Queue grows infinitely → OutOfMemoryError.

  BOUNDED queue: queue.put() blocks when full.
  → Producers slow down automatically when consumers can't keep up.
  → Back-pressure propagates upstream.

  Reactive Streams (Project Reactor/RxJava): backpressure built in.
  subscriber.request(n): consumer requests exactly n items.
  Publisher: sends at most n items without new request.
  Prevents publisher from overwhelming subscriber.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Producer-Consumer:

- Producer directly calls consumer: synchronous coupling — producer blocked during processing
- Rate mismatch: fast producer overwhelms slow consumer; or slow producer starves fast consumer

WITH Producer-Consumer:
→ Producer puts to queue (fast, non-blocking unless queue full). Consumer takes from queue independently. Rate mismatch absorbed by queue. Producer and consumer scale independently.

---

### 🧠 Mental Model / Analogy

> A factory assembly line with a staging area. Parts factory (producer) makes parts. Assembly crew (consumer) assembles finished products. The staging area (bounded queue) sits between. Parts factory fills staging area; assembly picks up parts as needed. Factory doesn't stop when assembly is busy — fills staging area. Assembly doesn't stop when factory pauses — works from staging area stock. If staging area full: factory waits (back-pressure). If staging area empty: assembly waits.

"Parts factory" = Producer threads
"Assembly crew" = Consumer threads
"Staging area" = BlockingQueue (the shared buffer)
"Factory fills staging area" = producer.put()
"Assembly picks from staging area" = consumer.take()
- "Staging area full → factory waits" = back-pressure (bounded queue blocks put)

---

### ⚙️ How It Works (Mechanism)

```
PRODUCER-CONSUMER COORDINATION:

  Queue EMPTY:  take() blocks → consumer thread parked until item available
  Queue FULL:   put() blocks  → producer thread parked until space available
  Queue NORMAL: put() and take() proceed without blocking

  BlockingQueue internals (LinkedBlockingQueue):
  Two ReentrantLocks: putLock + takeLock (higher throughput than single lock)
  Two Conditions: notFull (put waits here when full) + notEmpty (take waits here when empty)

  Graceful shutdown:
  Producer: set "done" flag, put poison pill (sentinel) on queue
  Consumer: check for poison pill → exit loop
```

---

### 🔄 How It Connects (Mini-Map)

```
Decouple work generation from work processing via thread-safe shared queue
        │
        ▼
Producer-Consumer Pattern ◄──── (you are here)
(producers → BlockingQueue → consumers; back-pressure; N:M scaling)
        │
        ├── Thread Pool Pattern: thread pool = Consumer side; submit() = Producer side
        ├── Observer Pattern: observers are async consumers; subject is producer
        ├── Event Bus Pattern: event bus = queue; publishers = producers; handlers = consumers
        └── Kafka/RabbitMQ: distributed, persistent Producer-Consumer at system level
```

---

### 💻 Code Example

```java
// Log pipeline with async producer-consumer:
public class AsyncLogger {
    private static final int QUEUE_CAPACITY = 10_000;
    private final BlockingQueue<LogEntry> queue = new ArrayBlockingQueue<>(QUEUE_CAPACITY);
    private final Thread worker;
    private volatile boolean running = true;

    public AsyncLogger() {
        // Consumer: single dedicated writer thread
        this.worker = new Thread(this::processLogs, "async-logger");
        this.worker.setDaemon(true);
        this.worker.start();
    }

    // Producer: called from any application thread (non-blocking)
    public boolean log(String level, String message) {
        return queue.offer(new LogEntry(level, message, Instant.now()));
        // offer() returns false if queue full (non-blocking drop vs blocking put)
        // For critical logs: use put() for back-pressure
    }

    // Consumer: background thread drains queue and writes to disk
    private void processLogs() {
        List<LogEntry> batch = new ArrayList<>(100);
        while (running || !queue.isEmpty()) {
            try {
                LogEntry entry = queue.poll(100, TimeUnit.MILLISECONDS);
                if (entry != null) {
                    batch.add(entry);
                    queue.drainTo(batch, 99);  // batch up to 100 at once
                    writeBatchToDisk(batch);
                    batch.clear();
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }

    public void shutdown() throws InterruptedException {
        running = false;
        worker.join(5000);  // wait for queue to drain
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                                                                                                                                                                                                                                          |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Unbounded queue prevents blocking — that's better     | Unbounded queue means: no back-pressure. A fast producer will fill the queue until `OutOfMemoryError`. Bounded queues with `put()` propagate back-pressure — slowing producers to match consumer capacity. This is correct behavior in most systems. `offer()` (non-blocking, drops on full) is appropriate only when dropping is acceptable (e.g., metrics sampling, logging).                  |
| Single producer/consumer is enough for any throughput | Not for high-throughput systems. With a single consumer, the bottleneck is the slowest consumer operation. Multiple consumers: partition the work across consumer threads. N producers + M consumers is the general form. Java's `ExecutorService` gives you this automatically: submit() = producer, thread pool = M consumers. Kafka partitions provide distributed multiple-consumer scaling. |
| BlockingQueue.poll() is always better than take()     | Both are valid for different scenarios. `take()` blocks indefinitely — appropriate when the consumer MUST process every item and should wait. `poll(timeout, unit)` returns null on timeout — appropriate when the consumer should periodically check other conditions (shutdown flag, health check). `take()` without shutdown handling leaves threads blocked forever at shutdown.             |

---

### 🔥 Pitfalls in Production

**Thread leaks when producer-consumer shutdown is not handled:**

```java
// ANTI-PATTERN: consumer thread cannot stop — stuck in take() forever:
class DataProcessor {
    private final BlockingQueue<Data> queue = new LinkedBlockingQueue<>(1000);
    private final Thread consumer = new Thread(() -> {
        while (true) {                  // ← infinite loop with no exit condition
            try {
                Data item = queue.take(); // blocks indefinitely on empty queue
                process(item);
            } catch (InterruptedException e) {
                // BAD: swallowing interrupt — thread can never stop
            }
        }
    });

    // When DataProcessor is shut down: consumer thread is STUCK in queue.take()
    // JVM shutdown: consumer thread holds, JVM won't exit (non-daemon thread).
    // Memory leak: DataProcessor GC'd but consumer thread keeps it alive.
}

// FIX: proper shutdown with interrupt + poison pill:
class DataProcessor {
    private static final Data POISON_PILL = new Data(null);
    private final BlockingQueue<Data> queue = new LinkedBlockingQueue<>(1000);
    private volatile boolean running = true;
    private final Thread consumer = new Thread(() -> {
        while (running) {
            try {
                Data item = queue.take();
                if (item == POISON_PILL) break;  // received shutdown signal
                process(item);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    });

    void shutdown() throws InterruptedException {
        running = false;
        queue.put(POISON_PILL);   // wake up consumer if waiting
        consumer.join(5000);       // wait for graceful stop
    }
}
```

---

### 🔗 Related Keywords

- `Thread Pool Pattern` — consumer side of Producer-Consumer; thread pool processes submitted tasks
- `BlockingQueue` — thread-safe queue that coordinates producer and consumer threads
- `Back-Pressure` — bounded queue mechanism that slows producers when consumers fall behind
- `Kafka / RabbitMQ` — distributed, persistent, scalable Producer-Consumer at system level
- `Observer Pattern` — async Observer uses Producer-Consumer internally (event bus buffers events)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Producers generate work → queue → consumers│
│              │ process work. Decoupled, async, rate-     │
│              │ mismatch-tolerant via bounded buffer.     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Producers and consumers run at different  │
│              │ rates; need parallel processing; decouple │
│              │ task creation from task execution; async  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Tight synchronous coupling needed;        │
│              │ ordering guarantees per-producer required;│
│              │ queue introduces unacceptable latency     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Restaurant kitchen: waiters place orders │
│              │  on ticket rail; cooks take tickets when  │
│              │  ready — neither waits for the other."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Thread Pool Pattern → BlockingQueue →     │
│              │ Back-Pressure → Kafka → Reactive Streams  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Logback's `AsyncAppender` is a production implementation of Producer-Consumer for logging. It uses a `BlockingQueue` and a single consumer thread that flushes to the real appender (file, database). It has a `discardingThreshold` (default 20%): when the queue is 80% full, it starts dropping TRACE and DEBUG messages (lower-severity logs). This is a deliberate back-pressure policy: protect the application from blocking on logging at the cost of log completeness. How does this design decision reflect the tradeoff between reliability and observability? What alternative back-pressure policies could you design?

**Q2.** Kafka's Producer-Consumer is fundamentally different from an in-process `BlockingQueue` Producer-Consumer. Kafka retains messages durably on disk, supports replay (consumer can re-read old messages), and supports multiple independent consumer groups (each group gets its own offset cursor — same messages consumed multiple times by different groups). A `BlockingQueue` is destructive (message consumed once, gone). When does this "persistent, replayable, multi-consumer" property of Kafka become essential? Give a concrete scenario where a `BlockingQueue` would fail and Kafka is required.
