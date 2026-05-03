---
layout: default
title: "BlockingQueue"
parent: "Java Concurrency"
nav_order: 360
permalink: /java-concurrency/blockingqueue/
number: "0360"
category: Java Concurrency
difficulty: ★★☆
depends_on: Queue, Thread, Producer-Consumer Pattern, Synchronization
used_by: Thread Pool (ThreadPoolExecutor), Producer-Consumer, Task Queues
related: ArrayBlockingQueue, LinkedBlockingQueue, PriorityBlockingQueue, SynchronousQueue
tags:
  - concurrency
  - queue
  - producer-consumer
  - java
  - intermediate
  - thread-safe
---

# 360 — BlockingQueue

⚡ TL;DR — BlockingQueue is a thread-safe queue that blocks the producer when full and blocks the consumer when empty, making the Producer-Consumer pattern naturally safe without manual synchronization.

| #0360           | Category: Java Concurrency                                                       | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Queue, Thread, Producer-Consumer Pattern, Synchronization                        |                 |
| **Used by:**    | Thread Pool (ThreadPoolExecutor), Producer-Consumer, Task Queues                 |                 |
| **Related:**    | ArrayBlockingQueue, LinkedBlockingQueue, PriorityBlockingQueue, SynchronousQueue |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You have a producer thread generating data faster than a consumer can process it. Without coordination, the producer buffers unbounded data in memory → `OutOfMemoryError`. Or you use a `Queue` with manual `synchronized` blocks, `wait()`, and `notify()` — a classic source of deadlocks, lost notifications, and spurious-wakeup bugs that consume days of debugging.

**THE BREAKING POINT:**
Manual thread coordination with `wait/notify` is notoriously difficult to get right. Missed signals, spurious wakeups, and forgotten `synchronized` blocks cause intermittent, hard-to-reproduce concurrency bugs. The underlying coordination pattern — "block producer if buffer full, block consumer if buffer empty" — is well-understood but painful to implement correctly every time.

**THE INVENTION MOMENT:**
`BlockingQueue` (introduced in Java 5 as part of `java.util.concurrent`) encapsulates the waiting and signalling logic behind a clean queue interface. Put when full → block. Take when empty → block. The implementation is correct by construction; you just push and pull data. This is the backbone of `ThreadPoolExecutor`'s work queue, Kafka consumer threads, and virtually every producer-consumer system in Java.

---

### 📘 Textbook Definition

**BlockingQueue** is an interface in `java.util.concurrent` that extends `Queue` with blocking operations. It guarantees thread-safe element insertion and removal. Key blocking operations: `put(e)` — inserts element, blocks if queue is full until space is available; `take()` — removes head element, blocks if queue is empty until an element is available. Non-blocking variants: `offer(e)` — returns false if full; `poll()` — returns null if empty; `offer(e, time, unit)` and `poll(time, unit)` — timed versions. Implementations: `ArrayBlockingQueue` (bounded, fair/unfair), `LinkedBlockingQueue` (optionally bounded), `PriorityBlockingQueue` (unbounded, ordered), `SynchronousQueue` (zero-capacity, handoff only), `DelayQueue` (elements available after delay). Does not accept `null` elements.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
BlockingQueue is a thread-safe buffer that automatically pauses producers when full and consumers when empty — no locks required in your code.

**One analogy:**

> BlockingQueue is a conveyor belt at a factory. Workers loading boxes (producers) can only place boxes when there's an empty slot. If the belt is full, they wait. Workers unloading boxes (consumers) wait when the belt is empty. Nobody needs to look at a clipboard or talk to each other — the belt's capacity handles all coordination automatically.

**One insight:**
`ThreadPoolExecutor` uses a `BlockingQueue` as its task queue — this is not an implementation detail but the architectural contract that makes the executor framework work. When you tune `corePoolSize`, `maxPoolSize`, and `queueCapacity`, you're tuning three components of a producer-consumer system backed by BlockingQueue.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Thread-safe: all operations acquire internal locks (two-lock for LinkedBlockingQueue; one-lock for ArrayBlockingQueue).
2. `put()` blocks indefinitely; `offer(e, time, unit)` blocks up to timeout; `offer(e)` never blocks.
3. `take()` blocks indefinitely; `poll(time, unit)` blocks up to timeout; `poll()` never blocks.
4. Never accepts `null` — null signals "queue empty" from `poll()`.
5. `size()` is O(1) for ArrayBlockingQueue, O(N) (not atomic) for LinkedBlockingQueue in concurrent contexts.

**DERIVED DESIGN:**

```
BLOCKING BEHAVIOUR MATRIX:
┌──────────────────────┬───────────┬──────────────┬──────────┐
│ Operation            │ Full queue│ Empty queue  │ Returns  │
├──────────────────────┼───────────┼──────────────┼──────────┤
│ put(e)               │ BLOCKS    │ N/A (insert) │ void     │
│ offer(e)             │ false     │ N/A          │ boolean  │
│ offer(e, time, unit) │ BLOCKS    │ N/A          │ boolean  │
│ take()               │ N/A       │ BLOCKS       │ element  │
│ poll()               │ N/A       │ null         │ element  │
│ poll(time, unit)     │ N/A       │ BLOCKS       │ element  │
└──────────────────────┴───────────┴──────────────┴──────────┘
```

```
INTERNAL STRUCTURE (ArrayBlockingQueue):
┌─────────────────────────────────────────────────────────┐
│  Object[] items [capacity]                              │
│  int takeIndex  ── consumer reads here                  │
│  int putIndex   ── producer writes here                 │
│  int count      ── current element count                │
│  ReentrantLock lock          ── single shared lock      │
│  Condition notEmpty ── signalled on put()               │
│  Condition notFull  ── signalled on take()              │
└─────────────────────────────────────────────────────────┘

Put flow: lock → check count==capacity → if full: notFull.await()
         → insert at putIndex → count++ → signal notEmpty → unlock

Take flow: lock → check count==0 → if empty: notEmpty.await()
          → remove at takeIndex → count-- → signal notFull → unlock
```

**THE TRADE-OFFS:**

- **Gain:** Zero synchronization code in producer/consumer; backpressure is built-in; correct by construction.
- **Cost:** Bounded queues can block producers (backpressure propagation); unbounded queues can OOM; single-lock ArrayBlockingQueue has lower throughput than LinkedBlockingQueue's two-lock design under high concurrency.

---

### 🧪 Thought Experiment

**SETUP:**
An HTTP request handler receives 10,000 requests/second. Each request creates a work task. A thread pool of 50 workers processes tasks. Processing takes ~5ms per task — pool capacity: ~10,000 tasks/second. System is balanced. Now a downstream service becomes slow: processing jumps to 50ms/task. Producer rate unchanged; consumer capacity drops to 1,000 tasks/second.

**WITHOUT bounded BlockingQueue:**
Tasks pile up in an unbounded queue. After a few seconds: millions of queued tasks. Memory exhaustion. JVM crash. All 10,000 RPS fail at once.

**WITH bounded BlockingQueue (capacity 1000):**
Queue fills in ~0.1 seconds. Producer (HTTP handler) blocks on `put()`. But HTTP handlers are typically non-blocking or have their own timeout. The system applies **backpressure**: the slowdown propagates up the call chain. HTTP clients start timing out and retrying later. System degrades gracefully — 1,000 RPS served well rather than 0 RPS served after crash.

**THE INSIGHT:**
Bounded BlockingQueue is a backpressure mechanism. The capacity is not just a buffer size — it's the lever that controls how failure propagates. Too large: OOM on overload. Too small: premature blocking during legitimate bursts.

---

### 🧠 Mental Model / Analogy

> BlockingQueue is a parking garage with a fixed number of spaces. Cars arriving (producers) drive in immediately if spaces are available. If the garage is full, they wait at the entrance barrier — not wasting fuel circling the block. Cars leaving (consumers) exit normally; when the last car leaves an empty section, the entrance barrier opens to let waiting arrivals in. Nobody needs a coordinator standing at the entrance manually counting — the gate mechanism handles everything.

- "Parking spaces" → queue capacity
- "Car arrives, parks" → `put(element)` when not full
- "Car arrives, waits at barrier" → `put()` blocking when full
- "Car exits" → `take()` when not empty
- "Barrier opens for waiting car" → `notFull.signal()` after `take()`

Where this analogy breaks down: multiple producers can pile up at the entrance simultaneously, but `ArrayBlockingQueue` uses a single lock, so only one "car" can actually enter at a time — the others queue at the lock level, not the capacity level.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
BlockingQueue is a thread-safe waiting room for data. When a producer has data to hand off, it puts it in the queue. When a consumer wants data, it takes it. If the queue is full, the producer waits. If empty, the consumer waits. No extra code needed to make this safe.

**Level 2 — How to use it (junior developer):**
Use `ArrayBlockingQueue` for a bounded buffer: `new ArrayBlockingQueue<>(capacity)`. Use `put()` on the producer side (blocks if full) and `take()` on the consumer side (blocks if empty). For graceful shutdown: use a sentinel value or `poll(timeout, unit)` in the consumer loop to check a `volatile boolean running` flag. Always catch `InterruptedException` and restore the interrupt flag.

**Level 3 — How it works (mid-level engineer):**
`ArrayBlockingQueue` uses a single `ReentrantLock` with two `Condition` objects (`notEmpty`, `notFull`). On `put()`: lock, check count, if full call `notFull.await()` (releases lock, parks thread), on wakeup re-check count, insert, increment count, signal `notEmpty`. The double-check after `await()` (loop, not if) handles spurious wakeups. `LinkedBlockingQueue` uses **two** locks: a `putLock` for the tail and a `takeLock` for the head — allowing concurrent puts and takes for higher throughput, though `size()` requires checking both locks for consistency.

**Level 4 — Why it was designed this way (senior/staff):**
The two-lock design of `LinkedBlockingQueue` (inspired by Michael-Scott queue) enables head-and-tail operations to proceed concurrently, maximizing throughput in producer-heavy or consumer-heavy systems. ArrayBlockingQueue's single-lock design is simpler and has better memory locality (contiguous array) but constrains throughput to one operation at a time. `SynchronousQueue` (used by `Executors.newCachedThreadPool()`) has zero capacity — every `put` directly hands off to a waiting `take`. This eliminates buffering entirely, creating a pure rendezvous point: the producer must wait for a consumer, enforcing tight coupling and natural flow control. Choosing between implementations is a throughput-vs-latency-vs-fairness decision that affects executor performance directly.

---

### ⚙️ How It Works (Mechanism)

```
PRODUCER-CONSUMER FLOW:
┌─────────────────────────────────────────────────────────┐
│  PRODUCER THREAD                                        │
│  queue.put(item)                                        │
│    lock.lockInterruptibly()                             │
│    while (count == capacity) notFull.await()            │
│    → Thread parks (releases lock)                       │
│    → ... consumer takes() an item ...                   │
│    → Consumer signals notFull                           │
│    → Producer thread wakes, re-acquires lock            │
│    → Re-checks: count < capacity → proceed              │
│    enqueue(item), count++                               │
│    notEmpty.signal()                                    │
│    lock.unlock()                                        │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│  CONSUMER THREAD                                        │
│  item = queue.take()                                    │
│    lock.lockInterruptibly()                             │
│    while (count == 0) notEmpty.await()                  │
│    → Thread parks (releases lock)                       │
│    → ... producer puts() an item ...                    │
│    → Producer signals notEmpty                          │
│    → Consumer thread wakes, re-acquires lock            │
│    → Re-checks: count > 0 → proceed                     │
│    item = dequeue(), count--                            │
│    notFull.signal()                                     │
│    lock.unlock()                                        │
│  return item                                            │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
NORMAL FLOW (ThreadPoolExecutor uses BlockingQueue internally):
Task submitted to ThreadPoolExecutor
→ If < corePoolSize threads: create thread
→ Else: queue.offer(task) → [BlockingQueue ← YOU ARE HERE]
→ Worker threads run: task = queue.take() → execute task
→ Worker loops back to take() for next task

FAILURE PATH:
Queue full + maxPoolSize reached
→ ThreadPoolExecutor's RejectedExecutionHandler fires
→ Default: AbortPolicy → RejectedExecutionException
→ Or: CallerRunsPolicy → calling thread executes task itself
→ Backpressure propagated to caller

WHAT CHANGES AT SCALE:
At high throughput (>100K ops/sec), ArrayBlockingQueue's
single lock becomes a bottleneck. Consider
LinkedTransferQueue (non-blocking where possible) or
Disruptor (ring buffer with no locks) for ultra-high
throughput event pipelines. ThreadPoolExecutor with
LinkedBlockingQueue unbounded can OOM — always prefer
bounded queues in production.
```

---

### 💻 Code Example

```java
import java.util.concurrent.*;

// Example 1 — Basic Producer-Consumer
BlockingQueue<String> queue = new ArrayBlockingQueue<>(100);

// Producer thread
Thread producer = new Thread(() -> {
    try {
        for (int i = 0; i < 1000; i++) {
            queue.put("item-" + i); // blocks if full
        }
        queue.put("POISON"); // shutdown signal
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

// Example 2 — WRONG: unbounded queue causes OOM under load
// BAD
ExecutorService executor = new ThreadPoolExecutor(
    10, 10, 0L, TimeUnit.MILLISECONDS,
    new LinkedBlockingQueue<>() // unbounded — OOM risk!
);

// Example 2 — GOOD: bounded queue with rejection policy
// GOOD
ExecutorService executor = new ThreadPoolExecutor(
    10,                          // core threads
    20,                          // max threads
    60L, TimeUnit.SECONDS,       // keepAlive
    new ArrayBlockingQueue<>(500), // bounded queue
    new ThreadPoolExecutor.CallerRunsPolicy() // backpressure
);

// Example 3 — Graceful shutdown with timed poll
volatile boolean running = true;

while (running || !queue.isEmpty()) {
    String item = queue.poll(100, TimeUnit.MILLISECONDS);
    if (item != null) process(item);
}
```

---

### ⚖️ Comparison Table

| Implementation         | Bounded        | Ordering         | Throughput           | Best For                            |
| ---------------------- | -------------- | ---------------- | -------------------- | ----------------------------------- |
| **ArrayBlockingQueue** | Yes (fixed)    | FIFO             | Medium               | Bounded buffers, fairness option    |
| LinkedBlockingQueue    | Optional       | FIFO             | Higher (2 locks)     | High-throughput pipelines           |
| PriorityBlockingQueue  | No             | Priority-ordered | Medium               | Priority task scheduling            |
| SynchronousQueue       | Zero (handoff) | N/A              | Very high (no queue) | Direct handoff (cached thread pool) |
| DelayQueue             | No             | Delay-ordered    | Low                  | Scheduled task execution            |

**How to choose:** Use `ArrayBlockingQueue` when you need a hard capacity bound and fairness. Use `LinkedBlockingQueue` with a bound for higher throughput. Use `SynchronousQueue` for `newCachedThreadPool` patterns where threads are cheap and tasks should be handed off immediately.

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                                                                                                     |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Unbounded LinkedBlockingQueue is "safer" than bounded  | Unbounded queues disguise backpressure problems — producers always succeed, queues grow unboundedly, and the first signal of trouble is an OOM crash. Bounded queues surface problems earlier and more gracefully           |
| `size()` on BlockingQueue is reliable for control flow | `size()` is a snapshot. Between checking `size()` and acting, other threads may have added/removed items. Always use `offer()`/`poll()` return values for flow control, not `size()` checks                                 |
| BlockingQueue eliminates all need for synchronization  | BlockingQueue handles queue insertion/removal safely, but the objects you put in the queue may still need synchronization if shared between threads. The queue protects the queue itself, not your data's internal state    |
| put() and take() are the fastest operations            | `offer()` and `poll()` (non-blocking) have lower overhead when you don't need blocking semantics. In high-throughput scenarios, non-blocking with retry can outperform blocking operations by avoiding park/unpark overhead |

---

### 🚨 Failure Modes & Diagnosis

**Producer Blocked Indefinitely (Full Queue, Slow Consumer)**

**Symptom:** Producer threads stuck in `put()` for minutes; application appears hung; thread dump shows threads in WAITING state at `ArrayBlockingQueue.put`.

**Root Cause:** Consumer processing slowed (downstream dependency, GC pause, deadlock in consumer), queue filled, producers blocked.

**Diagnostic Command:**

```bash
# Find threads blocked at BlockingQueue.put:
jstack <pid> | grep -B 5 "ArrayBlockingQueue"

# Check queue depth (if accessible):
# Add JMX bean or expose via Actuator for production monitoring
```

**Fix:** Investigate consumer slowdown. Add monitoring for queue depth and consumer throughput. Consider `offer(e, timeout, unit)` instead of `put()` to fail fast rather than block forever.

**Prevention:** Monitor queue depth as a metric. Alert when depth > 80% capacity. Add consumer health checks.

---

**Memory Exhaustion from Unbounded Queue**

**Symptom:** Heap usage climbs monotonically; `java.lang.OutOfMemoryError: Java heap space`; `LinkedBlockingQueue.size()` returns millions.

**Root Cause:** `new LinkedBlockingQueue<>()` with no capacity bound used as executor work queue; consumer throughput < producer throughput.

**Diagnostic Command:**

```bash
# Heap dump analysis - find largest collections:
jmap -dump:format=b,file=heap.hprof <pid>
# Analyse with Eclipse MAT: look for LinkedBlockingQueue$Node chains
```

**Fix:** Replace `new LinkedBlockingQueue<>()` with `new LinkedBlockingQueue<>(maxCapacity)` and add rejection handling.

**Prevention:** Never use unbounded queues in executor construction. Always specify capacity.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Queue` — FIFO data structure; BlockingQueue extends it
- `Thread` — understand threading to appreciate why blocking is needed
- `Producer-Consumer Pattern` — the design pattern BlockingQueue implements
- `ReentrantLock` — BlockingQueue is implemented with ReentrantLock internally

**Builds On This (learn these next):**

- `ThreadPoolExecutor` — uses BlockingQueue as its task queue
- `ConcurrentLinkedQueue` — non-blocking queue for high throughput without blocking semantics
- `Disruptor` — LMAX ring buffer for ultra-low-latency, lock-free event queuing

**Alternatives / Comparisons:**

- `ConcurrentLinkedQueue` — non-blocking, unbounded; no blocking semantics; use with Semaphore for bounded behavior
- `SynchronousQueue` — zero-capacity handoff; extreme case of BlockingQueue
- `TransferQueue` — extends BlockingQueue; producer can wait for consumer to take

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Thread-safe queue with blocking put/take  │
│              │ that implements the Producer-Consumer     │
│              │ pattern with zero manual synchronization  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Coordinating producers/consumers safely   │
│ SOLVES       │ without manual wait/notify code           │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Bounded queue = backpressure mechanism.   │
│              │ Unbounded queue = latent OOM time bomb    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Producer-consumer with multiple threads;  │
│              │ task queuing; rate-matching pipelines     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Single-threaded code; need non-blocking   │
│              │ polling only (ConcurrentLinkedQueue)      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Bounded: backpressure + blocking risk;    │
│              │ Unbounded: never blocks + OOM risk        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A conveyor belt that auto-pauses loaders │
│              │  when full and unloaders when empty"      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ThreadPoolExecutor → Disruptor →          │
│              │ Reactive Streams Backpressure             │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `LinkedBlockingQueue` uses two locks (putLock and takeLock) to enable concurrent puts and takes, while `ArrayBlockingQueue` uses one lock. Under what specific workload pattern does `LinkedBlockingQueue`'s two-lock design fail to outperform `ArrayBlockingQueue`'s single-lock design — and why does the number of producers vs. consumers matter here?

**Q2.** A `SynchronousQueue` has zero capacity — every `put()` must pair with a simultaneous `take()`. `Executors.newCachedThreadPool()` uses `SynchronousQueue` as its work queue. Trace step-by-step what happens when 100 tasks are submitted to a `newCachedThreadPool()` simultaneously with no existing worker threads — and explain why this specific queue choice makes `cachedThreadPool` unsuitable for bursty workloads with potentially unbounded concurrency.
