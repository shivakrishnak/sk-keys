---
id: DPT-032
title: Producer-Consumer
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-005, DPT-031
used_by: DPT-033, DPT-037, DPT-064
related: DPT-033, DPT-035, DPT-037, DPT-025
tags:
  - pattern
  - concurrency
  - intermediate
  - blocking-queue
  - thread-coordination
  - back-pressure
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 32
permalink: /technical-mastery/design-patterns/producer-consumer/
---

⚡ TL;DR - Producer-Consumer decouples work generation
(producers) from work processing (consumers) via a shared
buffer (queue), letting each side run at its own pace
and absorb burst traffic without dropping work.

| #32 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-031 | |
| **Used by:** | DPT-033, DPT-037, DPT-064 | |
| **Related:** | DPT-033, DPT-035, DPT-037, DPT-025 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An HTTP server receives image upload requests.
For each upload, the server resizes the image (CPU-bound,
500ms). Synchronous: the HTTP thread blocks for 500ms
per resize. Under 100 concurrent uploads: 100 threads
block for 500ms. HTTP handler is saturated. Latency
spikes. New requests time out or are rejected.

**THE DEEPER PROBLEM:**
Producer rate (100 req/s burst) does not match consumer
rate (2 req/s per resize thread). When they are directly
coupled, the slowest side blocks the fastest side.
The result: either dropped requests (producers cannot
submit) or wasted capacity (consumers idle during lulls).

**THE INVENTION MOMENT:**
Insert a buffer (queue) between HTTP handlers (producers)
and resize workers (consumers). HTTP handlers (producers)
enqueue the resize task and immediately return. Resize
workers (consumers) dequeue tasks and process at their
own rate. The queue absorbs bursts. Back-pressure: when
the queue is full, producers block or reject new work
(rather than crashing consumers).

**EVOLUTION:**
Java's `ExecutorService.submit()` is Producer-Consumer:
the caller (producer) submits tasks to the thread pool's
work queue; worker threads (consumers) dequeue and execute.
Kafka is Producer-Consumer at massive scale: publishers
write to partitions; consumer groups read at their own
pace. `java.util.concurrent.BlockingQueue` is the standard
Java implementation of the shared buffer.

---

### 📘 Textbook Definition

The **Producer-Consumer** pattern is a concurrency design
pattern that separates the production of data (or tasks)
from the consumption (or processing) of that data using
a shared, bounded buffer (queue). Producers add items
to the buffer; consumers remove items. The buffer
decouples producers from consumers in time: a producer
does not wait for a consumer to be ready; a consumer
does not wait for a specific producer. The buffer absorbs
rate differences. Back-pressure is applied when the
buffer is full (producers block or drop work), preventing
consumers from being overwhelmed.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Producer-Consumer is a buffer between fast-producing
code and slow-consuming code, so neither blocks the other.

**One analogy:**
> A restaurant kitchen (producer) makes dishes at its
> own rate. The serving counter (queue) holds finished
> dishes. Waiters (consumers) take dishes when ready.
> The kitchen does not wait for a waiter; the waiter does
> not wait for a specific dish. During rush hour: counter
> fills (back-pressure - kitchen slows or rejects new orders).
> During lull: kitchen produces ahead; waiters are idle
> until dishes appear.

**One insight:**
Producer-Consumer is the fundamental pattern behind
every async/queue-based system. `ExecutorService`,
Kafka, RabbitMQ, Java's `BlockingQueue`, log buffers,
network socket receive buffers - all implement
Producer-Consumer. The queue IS the contract between
producers and consumers.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. **Shared buffer**: producers add, consumers remove;
   access is thread-safe.
2. **Blocking on empty**: consumers block (or sleep/poll)
   when the buffer is empty - they do not spin.
3. **Blocking on full (back-pressure)**: producers block
   (or reject) when the buffer is at capacity.
4. **Thread safety**: the buffer (queue) is the synchronization
   point; producers and consumers do not share state
   other than the queue.

**JAVA `BlockingQueue` OPERATIONS:**
```
put(item)      - block until space available (producer)
offer(item, t) - wait up to t, then return false
offer(item)    - return false immediately if full

take()         - block until item available (consumer)
poll(t)        - wait up to t, then return null
poll()         - return null immediately if empty
```

**BUFFER SIZING:**
- Too small: producers block frequently (high contention).
- Too large: memory pressure; back-pressure signal delayed.
- Typical: size = (consumer throughput) x (max acceptable latency).
  If consumer processes 100/s and acceptable queue time is
  5 seconds: buffer size = 500.

**TRADE-OFFS:**

**Gain:** Decouples producers and consumers in time.
Absorbs bursts. Enables independent scaling. Single point
of back-pressure.

**Cost:** Adds latency (items wait in queue). Memory for
the buffer. If consumers crash: items in the buffer may
be lost (unless the queue is durable like Kafka).
Complexity in graceful shutdown: drain the queue before
stopping consumers.

---

### 🧪 Thought Experiment

**SETUP:**
Log aggregation service. Log generators (producers): 50
apps writing logs at 10,000 events/second. Log archiver
(consumer): writes to S3, can handle 5,000 events/second.
Direct coupling: archiver cannot keep up, producer writes
fail.

**WITH PRODUCER-CONSUMER:**
Queue capacity 20,000 (4 seconds of buffer). Producers
write at 10,000/s; consumer reads at 5,000/s. Queue fills
at 5,000/s. After 4 seconds: queue full, producers block
(back-pressure). Add 2 more consumer threads: 3 x 5,000
= 15,000/s consume rate > 10,000/s produce rate. Queue
drains.

---

### 🧠 Mental Model / Analogy

> Producer-Consumer is a CONVEYOR BELT FACTORY.
> Machine A (producer) stamps metal parts. Conveyor belt
> (queue) holds stamped parts. Machine B (consumer) paints
> them. Machine A stamps at its maximum rate, drops parts
> on the belt. Machine B paints at its rate. If the belt
> fills: Machine A's sensor stops it (back-pressure).
> If the belt is empty: Machine B waits.
> Neither machine knows the other's current state -
> they communicate only through the belt.

- "Machine A" = producer
- "Machine B" = consumer
- "Conveyor belt" = BlockingQueue
- "Belt full sensor stops A" = back-pressure (put() blocks)
- "B waits when belt empty" = consumer blocks on take()

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Producer-Consumer is a buffer between fast and slow code.
The fast side produces work into the buffer; the slow
side consumes at its own pace. The buffer prevents the
fast side from overwhelming the slow side.

**Level 2 - How to use it (junior developer):**
Use `java.util.concurrent.BlockingQueue` (typically
`LinkedBlockingQueue` or `ArrayBlockingQueue`).
Producers call `put()` (blocks if full). Consumers call
`take()` (blocks if empty). Each side runs on its own
thread(s). Avoid sharing state other than the queue.

**Level 3 - How it works (mid-level engineer):**
`ExecutorService` built on `ThreadPoolExecutor` IS
Producer-Consumer. The work queue is a `BlockingQueue`.
The task submitters are producers (`executor.submit(task)`
calls `queue.offer(task)`). Worker threads are consumers
(`while (true) { task = queue.take(); task.run(); }`).
`ThreadPoolExecutor` parameters control:
- Core threads: consumers always active
- Max threads: consumers added when queue is too full
- Queue capacity: how much burst before blocking/rejection
- `RejectedExecutionHandler`: what to do when queue full
  and max threads reached (back-pressure policy)

**Level 4 - Why it was designed this way (senior/staff):**
Producer-Consumer is the fundamental solution to the
resource contention problem: multiple producers sharing
a fixed-capacity consumer. Without decoupling, each
producer must wait for the consumer - serializing what
could be parallel. The buffer enables parallelism:
producers and consumers run concurrently; the queue
is the coordination point, not a blocking call.
At scale, the back-pressure mechanism is critical:
without it, a slow consumer causes producer queue to
grow unbounded until OOM. Back-pressure propagates
the slowness signal upstream (caller gets blocked or
rejected), allowing the system to signal overload
without crashing. Kafka's consumer group offset model
is the durable, distributed version: consumers can
"fall behind" (large offset lag) without losing work,
and can catch up when capacity increases.

**Level 5 - Mastery (distinguished engineer):**
Producer-Consumer is a queue-based reactive system.
The queue IS the back-pressure signal. When the queue
grows, consumers need to scale out (horizontal scaling
signal). When the queue is empty, consumers can scale
in. In distributed systems (Kafka, SQS, RabbitMQ),
the queue is the contract between services: producers
publish without knowing consumers; consumers scale
independently. This is the "temporal decoupling"
of microservices: the producer does not need the consumer
to be live at the time of production. The queue
provides durability. Reactive Streams (Project Reactor,
RxJava) formalize back-pressure: `Publisher` (producer)
only sends as many items as the `Subscriber` (consumer)
requests (`request(n)`). This is Producer-Consumer with
explicit demand signaling: consumers control the flow
rate rather than letting the queue fill to capacity.

---

### ⚙️ How It Works (Mechanism)

```
Producer-Consumer with BlockingQueue
┌─────────────────────────────────────────────────────────┐
│                                                         │
│ Producer Thread(s)          Consumer Thread(s)          │
│                                                         │
│ task = createTask()         task = queue.take()         │
│ queue.put(task)   ──────►   task.process()              │
│ (blocks if full)    queue   (blocks if empty)           │
│                   [====]                                │
│                   capacity                              │
│                                                         │
│ Back-pressure:                                          │
│ queue full → put() blocks → producer slows              │
│                                                         │
│ Consumer saturation:                                    │
│ queue grows → add more consumer threads                 │
│                                                         │
│ Graceful shutdown:                                      │
│ producers stop submitting                               │
│ drain queue (consumers finish remaining items)          │
│ consumers exit when queue empty                         │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Image resize service:

HTTP Handler (producer):
  POST /upload → parseImage() → queue.put(imageTask)
  Returns 202 Accepted immediately (non-blocking)
  If queue full: returns 503 (back-pressure to client)

Resize Worker (consumer):
  while (running) {
      ImageTask t = queue.take();  // waits if empty
      resizedImage = resize(t.image, t.width, t.height);
      imageStore.save(t.userId, resizedImage);
  }

Graceful shutdown:
  Set running = false
  Add POISON_PILL to queue (consumer sees it → exits)
  Or: consumer polls with timeout and checks flag
```

---

### 💻 Code Example

**Example 1 - Broken: synchronized approach (overcomplicated):**

```java
// BAD: manual synchronized is error-prone
// Missing notify, spurious wakeup, etc.
class BrokenQueue<T> {
    private final List<T> items = new ArrayList<>();
    private final int capacity;

    synchronized void produce(T item) throws InterruptedException {
        while (items.size() == capacity) wait();
        // spurious wakeup risk
        items.add(item);
        notify(); // only wakes ONE consumer - may not be enough
    }

    synchronized T consume() throws InterruptedException {
        while (items.isEmpty()) wait();
        T item = items.remove(0); // O(n) - performance issue
        notify();
        return item;
    }
}
// Use BlockingQueue instead - it handles all this correctly
```

**Example 2 - Correct: BlockingQueue:**

```java
// GOOD: BlockingQueue handles all concurrency correctly

import java.util.concurrent.*;

class ImageResizeService {
    private static final int QUEUE_CAPACITY = 500;
    private final BlockingQueue<ImageTask> queue =
        new ArrayBlockingQueue<>(QUEUE_CAPACITY);

    // Producers: HTTP handler threads submit here
    boolean submitResize(ImageTask task) {
        // offer() - returns false if full (don't block HTTP thread)
        boolean accepted = queue.offer(task);
        if (!accepted) {
            metrics.counter("queue.rejected").increment();
        }
        return accepted;
    }

    // Consumer worker (run on dedicated thread pool)
    void processLoop() {
        while (!Thread.currentThread().isInterrupted()) {
            try {
                // blocks until item available (no busy-wait)
                ImageTask task = queue.poll(100,
                    TimeUnit.MILLISECONDS);
                if (task != null) {
                    resize(task);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break; // shutdown signal
            }
        }
        // drain remaining items after interrupt
        drainRemaining();
    }

    private void drainRemaining() {
        ImageTask task;
        while ((task = queue.poll()) != null) {
            resize(task); // finish already-queued work
        }
    }

    private void resize(ImageTask task) {
        // CPU-bound work: isolated from HTTP threads
        BufferedImage scaled = scaleImage(
            task.image(), task.targetWidth(), task.targetHeight());
        imageStore.save(task.userId(), scaled);
    }
}
```

**Example 3 - ExecutorService as Producer-Consumer:**

```java
// RECOGNITION: ExecutorService IS Producer-Consumer

// The thread pool work queue IS the BlockingQueue
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    4,                           // core consumers always active
    8,                           // max consumers under load
    60, TimeUnit.SECONDS,        // idle consumer thread timeout
    new ArrayBlockingQueue<>(200), // queue capacity = buffer
    new ThreadPoolExecutor.CallerRunsPolicy() // back-pressure policy
    // CallerRunsPolicy: when queue full, caller thread runs the task
    // (slows down the producer - natural back-pressure)
);

// Producer: submits tasks
executor.submit(() -> processOrder(order));   // non-blocking if space
executor.submit(() -> processOrder(order2));  // CallerRuns if full

// Consumers: worker threads dequeue and run tasks
// Invisible: ThreadPoolExecutor manages them
```

**Example 4 - Monitoring queue health:**

```java
// Operational monitoring for Producer-Consumer
class QueueMonitor {
    private final ArrayBlockingQueue<?> queue;

    void emitMetrics() {
        int size = queue.size();
        int remaining = queue.remainingCapacity();
        double utilization = (double) size / (size + remaining);

        metrics.gauge("queue.size").set(size);
        metrics.gauge("queue.utilization").set(utilization);

        if (utilization > 0.8) {
            alerting.warn("Queue utilization > 80%: "
                + "consider adding consumers");
        }
        if (utilization > 0.95) {
            alerting.critical("Queue near capacity: "
                + "producers will block or reject soon");
        }
    }
}
```

---

### ⚖️ Comparison Table

| Queue Type | Bounded | Ordering | Best Use |
|---|---|---|---|
| `ArrayBlockingQueue` | Yes | FIFO | Known capacity, back-pressure |
| `LinkedBlockingQueue` | Optional | FIFO | Default; less contention |
| `PriorityBlockingQueue` | No | Priority | Task prioritization |
| `SynchronousQueue` | 0 (direct handoff) | N/A | Thread handoff (no buffer) |
| `DelayQueue` | No | Delay-ordered | Scheduled tasks |
| Kafka topic | Configurable | Partition-ordered | Distributed, durable |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Larger queue = more resilient | Larger queue delays back-pressure, increases latency and memory usage. A queue that is full means consumers cannot keep up - the right fix is more consumers or faster processing, not a larger queue |
| Producer-Consumer guarantees order | FIFO queues preserve insertion order, but concurrent producers can enqueue out of "logical" order. If ordering matters: use a single producer or sequence items with a monotonic counter |
| take() is better than poll(timeout) | `take()` blocks indefinitely. If the consumer thread needs to check a shutdown flag, it will never see it with `take()`. Use `poll(timeout)` to wake up periodically and check interrupt/shutdown flags |
| Multiple producers require producer-side locking | `BlockingQueue` implementations are thread-safe for multiple concurrent producers. Producers do NOT need external synchronization when calling `put()` or `offer()` |

---

### 🚨 Failure Modes & Diagnosis

**Queue Growth Causes OutOfMemoryError**

**Symptom:**
`java.lang.OutOfMemoryError: Java heap space` under load.
Heap dump shows millions of task objects in a `LinkedBlockingQueue`.

**Root Cause:**
`LinkedBlockingQueue` with no capacity bound (defaults to
`Integer.MAX_VALUE`). Producers are faster than consumers;
the queue grows without bound until OOM.

**Diagnosis:**
```
# Monitor queue size
executor = (ThreadPoolExecutor) executorService;
System.out.println("Queue size: " +
  executor.getQueue().size());
# Increasing queue size = consumers cannot keep up
```

**Fix:**
Always bound the queue:
```java
// BAD: unbounded queue
new LinkedBlockingQueue<>() // default capacity = Integer.MAX_VALUE

// GOOD: bounded queue with back-pressure
new ArrayBlockingQueue<>(1000) // blocks producer when full
// Choose capacity based on: consumer_rate * acceptable_latency
```

---

**Silent Work Loss on Shutdown**

**Symptom:**
On service shutdown, tasks in the queue are lost. Orders
placed in the last 30 seconds before shutdown were never
processed.

**Root Cause:**
Consumer threads were killed immediately without draining
the queue. `ExecutorService.shutdownNow()` interrupts
workers and discards queued tasks.

**Fix:**
Use `shutdown()` + `awaitTermination()` for graceful drain:
```java
executor.shutdown(); // stop accepting new tasks
try {
    // wait up to 60 seconds for queued tasks to finish
    if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
        executor.shutdownNow(); // force after timeout
    }
} catch (InterruptedException e) {
    executor.shutdownNow();
    Thread.currentThread().interrupt();
}
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Double-Checked Locking` - DPT-031; understanding
  thread-safe initialization helps with concurrent queue setup

**Builds On This (learn these next):**
- `Thread Pool Pattern` - DPT-033; thread pool IS Producer-Consumer
  with managed consumer threads
- `Event Bus Pattern` - DPT-037; Event Bus extends Producer-Consumer
  to multi-topic publish/subscribe

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Buffer (queue) between producers and     │
│              │ consumers - decouples rate and lifecycle │
├──────────────┼──────────────────────────────────────────┤
│ KEY CLASS    │ ArrayBlockingQueue(N) or                 │
│              │ LinkedBlockingQueue(N) - N = buffer size │
├──────────────┼──────────────────────────────────────────┤
│ BACK-PRESSURE│ put() blocks when full → slows producer  │
│              │ offer() returns false → producer chooses │
├──────────────┼──────────────────────────────────────────┤
│ REAL EXAMPLES│ ExecutorService work queue, Kafka topic, │
│              │ OS network receive buffer                │
├──────────────┼──────────────────────────────────────────┤
│ FAILURE MODE │ Unbounded queue → OOM; always bound it  │
│              │ Shutdown: drain before stopping consumers│
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Thread Pool → Scheduler → Read-Write Lock│
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Producer-Consumer's core value is DECOUPLING producer
   and consumer rates via a bounded buffer. The buffer
   absorbs bursts. When the buffer is full, back-pressure
   slows producers rather than crashing consumers.
2. Always bound the queue (`ArrayBlockingQueue(N)` or
   `LinkedBlockingQueue(N)`). Unbounded queues (default
   `LinkedBlockingQueue`) grow without limit and cause OOM.
   Size = consumer_rate x acceptable_latency.
3. Java's `ExecutorService` IS Producer-Consumer: task
   submitters are producers; worker threads are consumers;
   the thread pool's work queue is the `BlockingQueue`.

