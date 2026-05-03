---
layout: default
title: "BlockingQueue"
parent: "Java Concurrency"
nav_order: 360
permalink: /java-concurrency/blockingqueue/
number: "0360"
category: Java Concurrency
difficulty: ★★☆
depends_on: Thread, Producer-Consumer Pattern, Queue (Data Structure), ExecutorService
used_by: ExecutorService, ThreadPoolExecutor, Kafka
related: ConcurrentLinkedQueue, ArrayDeque, LinkedBlockingQueue
tags:
  - java
  - concurrency
  - intermediate
  - data-structures
  - producer-consumer
---

# 0360 — BlockingQueue

⚡ TL;DR — `BlockingQueue` is a thread-safe queue where `put()` blocks when the queue is full and `take()` blocks when it's empty — providing built-in backpressure and decoupling producers from consumers without any manual synchronisation code.

| #0360           | Category: Java Concurrency                                                 | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Thread, Producer-Consumer Pattern, Queue (Data Structure), ExecutorService |                 |
| **Used by:**    | ExecutorService, ThreadPoolExecutor, Kafka                                 |                 |
| **Related:**    | ConcurrentLinkedQueue, ArrayDeque, LinkedBlockingQueue                     |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You have a producer thread that generates work items and consumer threads that process them. Without a shared queue, producers and consumers must be tightly coupled — the producer can only generate one item per consumer's processing time. Or you add a raw `ArrayList` as a queue — but now you need `synchronized` blocks on every add/remove, `wait()`/`notify()` to pause producers when full and consumers when empty, and careful handling of spurious wakeups. 40+ lines of synchronisation code, all of which must be correct.

**THE BREAKING POINT:**
The manual `wait`/`notify` pattern on a shared `ArrayList` is:

- Verbose (40+ lines for basic producer-consumer)
- Error-prone (missing `notifyAll`, wrong condition check, spurious wakeup mishandling)
- Unbounded by default — no backpressure, producer can out-run consumer until OOM
- Non-composable — can't easily add timeout, try-once, or priority behaviour

**THE INVENTION MOMENT:**
`BlockingQueue` was introduced in Java 5 (`java.util.concurrent`) as the standard producer-consumer mechanism. It encapsulates the `wait`/`notify` logic inside the queue itself, exposing a clean API with four operation styles: blocking, time-limited, conditional, and non-blocking.

---

### 📘 Textbook Definition

**BlockingQueue:** A `java.util.Queue` extension (`java.util.concurrent.BlockingQueue`) that additionally supports operations that wait for the queue to become non-empty when retrieving an element and wait for space to become available when storing an element. Implementations include `ArrayBlockingQueue` (bounded, array-backed), `LinkedBlockingQueue` (optionally bounded, linked-node-backed), `PriorityBlockingQueue` (unbounded, priority-ordered), `SynchronousQueue` (zero-capacity, direct handoff), and `LinkedBlockingDeque` (double-ended).

**Bounded queue:** A `BlockingQueue` with a fixed maximum capacity. `put()` blocks when the queue is at capacity (backpressure). Required for production workloads to prevent unbounded memory growth.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
BlockingQueue is a thread-safe queue where producers wait when it's full and consumers wait when it's empty — no manual synchronisation needed.

**One analogy:**

> BlockingQueue is a factory's loading dock with a fixed number of parking spots. Delivery trucks (producers) pull in to drop off inventory. If all spots are full (queue at capacity), the truck parks on the street and waits (blocks) until a spot opens. Warehouse workers (consumers) take items from the dock. If the dock is empty, workers wait (block) until a truck arrives. Neither the drivers nor the workers need a radio or coordinator — the dock itself manages the flow.

**One insight:**
The critical capability is bounded capacity with blocking. An unbounded queue (`LinkedBlockingQueue` with default `Integer.MAX_VALUE` capacity) lets producers outrun consumers until memory is exhausted. A bounded `ArrayBlockingQueue(1000)` means that at most 1,000 items can be queued — if producers are faster than consumers, producers slow down (block) rather than causing OOM. This is the textbook definition of backpressure.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Thread-safe: concurrent `put()` and `take()` calls are safe without external synchronisation.
2. `put()` blocks when queue is at capacity (`ArrayBlockingQueue`) until a consumer takes an item.
3. `take()` blocks when queue is empty until a producer adds an item.
4. Both operations respond to interruption (`InterruptedException`).

**FOUR OPERATION STYLES:**

```
For INSERT:
  add(e)      → throws IllegalStateException if full (fails immediately)
  offer(e)    → returns false if full (no wait)
  put(e)      → BLOCKS if full (waits indefinitely)
  offer(e, timeout, unit) → waits up to timeout

For REMOVE:
  remove()    → throws NoSuchElementException if empty (fails immediately)
  poll()      → returns null if empty (no wait)
  take()      → BLOCKS if empty (waits indefinitely)
  poll(timeout, unit) → waits up to timeout

For EXAMINE (peek, no removal):
  element()   → throws NoSuchElementException if empty
  peek()      → returns null if empty
  (no blocking peek in BlockingQueue)
```

**IMPLEMENTATIONS:**

```
ArrayBlockingQueue(int capacity)
  - Bounded, fixed capacity
  - Array-backed (pre-allocated, no GC pressure)
  - Single lock (put and take share one ReentrantLock)
  - FIFO ordering
  - Best for: bounded work queues, known peak load

LinkedBlockingQueue(int capacity) or LinkedBlockingQueue()
  - Bounded (optional; default: Integer.MAX_VALUE)
  - Linked node (dynamic allocation)
  - Two locks: putLock and takeLock → higher throughput under contention
  - FIFO ordering
  - Best for: high-throughput pipelines

PriorityBlockingQueue()
  - Unbounded (grows dynamically)
  - Heap-backed, priority order (requires Comparable or Comparator)
  - Single lock
  - Best for: priority-scheduled tasks

SynchronousQueue()
  - Zero capacity (no elements ever stored)
  - put() blocks until a consumer calls take(), and vice versa
  - Direct handoff: producer and consumer must rendezvous
  - Used by: Executors.newCachedThreadPool()

LinkedBlockingDeque(int capacity)
  - Double-ended (addFirst/addLast/takeFirst/takeLast)
  - Work-stealing algorithms
```

---

### 🧪 Thought Experiment

**SETUP:**
An HTTP server receives requests and dispatches to a worker thread pool. Requests arrive in bursts: 10,000 requests/second for 1 second, then 100/second. Worker threads can process 1,000 requests/second.

**WITH UNBOUNDED QUEUE (`new LinkedBlockingQueue()`):**

```
Burst: 10,000 requests queued in 1 second.
Workers consume at 1,000/second → queue drains in 10 seconds.
After burst: 9,000 items in queue → 9 second tail latency for last request.
Memory: 9,000 request objects kept alive → memory pressure.
Worst case: sustained burst → queue grows without bound → OOM.
```

**WITH BOUNDED QUEUE (`new ArrayBlockingQueue(2000)`):**

```
Burst: first 2,000 requests queued immediately.
Request 2,001+: producers (HTTP accepting threads) BLOCK.
→ Backpressure to HTTP accept loop → TCP receive buffer fills.
→ TCP backpressure to client → client sees latency (not OOM crash).
After burst ends: queue drains within 2 seconds.
Memory: capped at 2,000 items.
Trade-off: some requests rejected/slowed vs. server stability.
```

**THE INSIGHT:**
Backpressure is a feature. A server that slows down (applies backpressure) under load is far preferable to one that accepts all work and crashes with OOM. `BlockingQueue`'s bounded capacity makes backpressure automatic.

---

### 🧠 Mental Model / Analogy

> BlockingQueue is a physical inbox tray with a fixed height (bounded capacity). Producers add documents to the top of the tray. If the tray is full, the producer sets their document down and waits patiently until space opens up — they don't drop it on the floor (no data loss) and they don't pile documents on top (no overflow). Consumers remove documents from the bottom. If the tray is empty, they sit and wait until something arrives. Neither producer nor consumer needs to coordinate with the other — the tray manages everything.

Explicit mapping:

- "inbox tray" → BlockingQueue
- "documents" → work items / task objects
- "fixed tray height" → capacity (bounds)
- "producer waiting when full" → `put()` blocking
- "consumer waiting when empty" → `take()` blocking
- "tray manager" → internal ReentrantLock + Condition (notEmpty/notFull)

Where this analogy breaks down: a real tray doesn't support timeout (`poll(5, SECONDS)`) or non-blocking try (`offer()`). `BlockingQueue` does — giving producers and consumers precise control over how long they'll wait.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
BlockingQueue is a thread-safe queue where: if you try to add something when it's full, you automatically wait; if you try to remove something when it's empty, you automatically wait. It handles all the threading complexity for you.

**Level 2 — How to use it (junior developer):**
Create a `new ArrayBlockingQueue<>(capacity)` and share it between producer and consumer threads. Producers call `queue.put(item)` (blocks if full). Consumers call `queue.take()` (blocks if empty). Use `queue.offer(item, timeout, unit)` when you need timeout-bounded production. Handle `InterruptedException` — these operations can be interrupted for clean shutdown.

**Level 3 — How it works (mid-level engineer):**
`ArrayBlockingQueue` uses a `ReentrantLock` with two `Condition` variables: `notEmpty` (consumers wait on this) and `notFull` (producers wait on this). When `take()` is called on an empty queue, the thread calls `notEmpty.await()` (releases lock, sleeps). When `put()` adds an item, it calls `notEmpty.signal()` to wake one waiting consumer. The bounded capacity enforcement is checked under the lock: if `count == capacity`, `put()` calls `notFull.await()`. `LinkedBlockingQueue` uses separate `putLock` and `takeLock` — producers and consumers don't contend on the same lock, enabling higher throughput.

**Level 4 — Why it was designed this way (senior/staff):**
The split-lock design of `LinkedBlockingQueue` (putLock + takeLock) is a deliberate trade-off: it allows concurrent puts and takes at the expense of a slightly more complex implementation (the lock to update the element count must be acquired by both locks via a `count.getAndIncrement()` atomic). `ArrayBlockingQueue` uses a single lock because the array's head/tail pointers and count are all shared state that would require complex atomic coordination to access independently. The design decision: use `ArrayBlockingQueue` when the queue will be a bottleneck and you need memory predictability (no GC overhead from node allocation); use `LinkedBlockingQueue` when you need maximum throughput (split locks) and can tolerate GC overhead from node allocation. This same two-lock design appears in many high-performance concurrent queues (e.g., the basis for Kafka's internal queue implementations).

---

### ⚙️ How It Works (Mechanism)

```
ArrayBlockingQueue INTERNALS:

State:
  Object[] items    (circular array)
  int takeIndex     (head)
  int putIndex      (tail)
  int count         (current size)
  ReentrantLock lock
  Condition notEmpty
  Condition notFull

put(e):
  lock.lockInterruptibly()
  while (count == capacity) notFull.await()  ← BLOCKS HERE IF FULL
  items[putIndex] = e
  putIndex = (putIndex + 1) % capacity
  count++
  notEmpty.signal()   ← wake one waiting consumer
  lock.unlock()

take():
  lock.lockInterruptibly()
  while (count == 0) notEmpty.await()  ← BLOCKS HERE IF EMPTY
  e = items[takeIndex]
  items[takeIndex] = null  (GC)
  takeIndex = (takeIndex + 1) % capacity
  count--
  notFull.signal()    ← wake one waiting producer
  lock.unlock()
  return e
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Producer thread(s):
  while (true):
    WorkItem item = generateWork()
    queue.put(item)          ← BLOCKS if queue full
    [if queue full: blocks until consumer takes]

Consumer thread(s):
  while (true):
    WorkItem item = queue.take()  ← BLOCKS if queue empty
    process(item)
    [if queue empty: blocks until producer adds]

BACKPRESSURE PATH:
  Producer outpaces consumers
    → queue fills to capacity
    → put() blocks
    → producer thread pauses
    → upstream pressure builds
    → system self-regulates

SHUTDOWN PATH:
  Producers stop adding items
  Consumers drain remaining items (take() continues)
  Use poison pill (null or sentinel) to signal consumers to stop:
    queue.put(POISON_PILL)  // consumers check for sentinel
```

---

### 💻 Code Example

**Example 1 — Basic producer-consumer:**

```java
import java.util.concurrent.*;

public class Pipeline {
    private static final int CAPACITY = 1000;
    private final BlockingQueue<WorkItem> queue
        = new ArrayBlockingQueue<>(CAPACITY);
    private static final WorkItem POISON = new WorkItem(null); // sentinel

    // Producer thread
    public void producer(List<WorkItem> items) {
        try {
            for (WorkItem item : items) {
                queue.put(item);          // blocks if queue full (backpressure)
            }
            queue.put(POISON);            // signal consumer to stop
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    // Consumer thread
    public void consumer() {
        try {
            while (true) {
                WorkItem item = queue.take();  // blocks if empty
                if (item == POISON) break;     // sentinel check
                process(item);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
```

**Example 2 — With timeout (non-blocking try):**

```java
// Offer with timeout — don't block indefinitely
boolean enqueued = queue.offer(item, 100, TimeUnit.MILLISECONDS);
if (!enqueued) {
    // Queue still full after 100ms — apply backpressure upstream
    metrics.increment("queue.full.drops");
    throw new BackpressureException("Queue full, item dropped");
}

// Poll with timeout — don't block indefinitely
WorkItem item = queue.poll(100, TimeUnit.MILLISECONDS);
if (item == null) {
    // Queue empty after 100ms — continue (maybe check for shutdown)
    continue;
}
```

**Example 3 — ThreadPoolExecutor with custom queue:**

```java
// ThreadPoolExecutor uses BlockingQueue internally for task queuing
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    4,                               // corePoolSize
    8,                               // maximumPoolSize
    60L, TimeUnit.SECONDS,           // keepAliveTime
    new ArrayBlockingQueue<>(500),   // BOUNDED queue — apply backpressure
    new ThreadPoolExecutor.CallerRunsPolicy() // backpressure: caller runs task
);
// When queue is full AND all threads busy:
// CallerRunsPolicy → submitting thread executes the task directly
// → slows down the submitter → natural backpressure
```

---

### ⚖️ Comparison Table

| Implementation          | Bounded       | Ordering             | Lock strategy                 | Use case                             |
| ----------------------- | ------------- | -------------------- | ----------------------------- | ------------------------------------ |
| **ArrayBlockingQueue**  | Yes (fixed)   | FIFO                 | Single lock                   | Memory-predictable work queues       |
| **LinkedBlockingQueue** | Optional      | FIFO                 | Two locks (higher throughput) | High-throughput pipelines            |
| PriorityBlockingQueue   | No            | Priority             | Single lock                   | Priority-scheduled tasks             |
| SynchronousQueue        | Zero capacity | N/A (direct handoff) | CAS                           | Cached thread pool handoff           |
| LinkedBlockingDeque     | Optional      | FIFO/LIFO            | Two locks                     | Work-stealing algorithms             |
| ConcurrentLinkedQueue   | No            | FIFO                 | Lock-free (CAS)               | Non-blocking, no backpressure needed |

How to choose: `ArrayBlockingQueue` for bounded work queues with predictable memory. `LinkedBlockingQueue` when you need higher throughput and optional bounding. `PriorityBlockingQueue` for scheduled/priority tasks. `SynchronousQueue` inside thread pool implementations for direct thread handoff.

---

### ⚠️ Common Misconceptions

| Misconception                                                     | Reality                                                                                                                                                                                                     |
| ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "LinkedBlockingQueue is unbounded"                                | Default constructor creates capacity=Integer.MAX_VALUE (effectively unbounded). Always use `new LinkedBlockingQueue<>(capacity)` in production for backpressure.                                            |
| "BlockingQueue is slow due to locking"                            | `LinkedBlockingQueue`'s split-lock design allows concurrent puts and takes. It's fast enough for most production systems. If you need lock-free, use `ConcurrentLinkedQueue` (but lose blocking semantics). |
| "take() and poll() are interchangeable"                           | `take()` blocks indefinitely. `poll()` returns null immediately if empty. `poll(timeout, unit)` waits up to timeout. Choose based on whether you want to block.                                             |
| "BlockingQueue is thread-safe so I need no other synchronisation" | The QUEUE itself is thread-safe. The ITEMS in the queue are not. If multiple consumers might receive the same item type, the items themselves need to be immutable or independently thread-safe.            |
| "SynchronousQueue can hold one element"                           | It holds ZERO elements. A `put()` blocks until a `take()` is called simultaneously — it's a direct handoff, not a buffer.                                                                                   |

---

### 🚨 Failure Modes & Diagnosis

**1. Producer Deadlock — All Threads Producing, None Consuming**

**Symptom:** Application freezes. All producer threads BLOCKED at `put()`. `queue.size() == capacity`.

**Root Cause:** Consumer threads exited or threw exceptions without being restarted. Producer threads fill the queue and block. No consumers remain to drain it.

**Diagnostic:**

```bash
jstack <pid> | grep -A 10 "BlockingQueue\|put("
# Shows producer threads in WAITING state at put()

# Periodically log queue metrics:
log.info("Queue size: {}/{}", queue.size(), capacity);
# queue.size() == capacity AND not draining = consumer failure
```

**Fix:** Monitor consumer threads. Use `ExecutorService` to restart crashed consumers. Consider using `LinkedTransferQueue` which surfaces consumer absence more explicitly. Add a health check that alerts when queue size stays at capacity for > N seconds.

**Prevention:** Consumer threads should be wrapped in try-catch with restart logic. Use `ThreadPoolExecutor.setRejectedExecutionHandler()` to handle queue-full conditions instead of blocking indefinitely.

---

**2. Memory Exhaustion — Unbounded Queue Growing Without Bound**

**Symptom:** `OutOfMemoryError`. Heap usage growing linearly. `LinkedBlockingQueue.size()` continuously increasing.

**Root Cause:** `new LinkedBlockingQueue<>()` without capacity. Producers consistently outpace consumers. No backpressure mechanism.

**Diagnostic:**

```bash
# Check queue size in application metrics / JMX
# Or: enable heap dump on OOM:
-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp/

# In heap dump (using Eclipse Memory Analyzer):
# Look for large LinkedBlockingQueue.head chains
```

**Fix:** Replace `new LinkedBlockingQueue<>()` with `new ArrayBlockingQueue<>(MAX_CAPACITY)` or `new LinkedBlockingQueue<>(MAX_CAPACITY)`. Define `MAX_CAPACITY` based on acceptable memory budget and latency tolerance.

**Prevention:** NEVER use an unbounded `BlockingQueue` in a production system that handles user traffic. Always specify capacity.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Thread` — BlockingQueue coordinates threads
- `Producer-Consumer Pattern` — the design pattern BlockingQueue implements
- `Queue (Data Structure)` — the underlying data structure

**Builds On This (learn these next):**

- `ExecutorService` — built on top of BlockingQueue (ThreadPoolExecutor uses it internally)
- `ThreadPoolExecutor` — exposes the BlockingQueue used for task queuing
- `Kafka` — uses BlockingQueue-like semantics for partition management internally

**Alternatives / Comparisons:**

- `ConcurrentLinkedQueue` — lock-free, non-blocking, unbounded; no backpressure
- `ArrayDeque` — fast but NOT thread-safe; use only with external synchronisation
- `LinkedBlockingQueue` — the most commonly used BlockingQueue implementation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Thread-safe queue with blocking put/take: │
│              │ waits when full or empty automatically    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Manual wait/notify producer-consumer      │
│ SOLVES       │ synchronisation (40+ lines → 2 lines)     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Bounded capacity → automatic backpressure │
│              │ prevents OOM; always specify capacity     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Producer-consumer decoupling, task queues,│
│              │ rate-matching between pipeline stages     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Single-threaded code; need lock-free and  │
│              │ no backpressure (use ConcurrentLinkedQueue)│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Backpressure + simplicity vs. potential   │
│              │ producer blocking under heavy load        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Loading dock with fixed parking: trucks  │
│              │  wait if full; workers wait if empty."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ExecutorService → ThreadPoolExecutor      │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your microservice uses an `ArrayBlockingQueue(500)` to buffer work between HTTP request acceptance and internal processing. Under high traffic, `put()` blocks in the HTTP handler thread. HTTP connection-level timeout is 30 seconds. What is the exact failure mode when `put()` blocks for 31 seconds? How do you fix this to ensure the HTTP response is always sent within the SLA, even when the queue is full, without simply increasing queue capacity?

**Q2.** `LinkedBlockingQueue` uses two separate locks (putLock, takeLock) while `ArrayBlockingQueue` uses one. Both use a shared atomic count. Explain specifically why `ArrayBlockingQueue` cannot use split locks (what shared state prevents it), and why `LinkedBlockingQueue` can isolate put and take operations to different locks. What is the one remaining point of contention in `LinkedBlockingQueue` that requires a signal from one lock's holder to the other?
