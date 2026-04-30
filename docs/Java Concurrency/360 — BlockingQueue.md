---
layout: default
title: "BlockingQueue"
parent: "Java Concurrency"
nav_order: 81
permalink: /java-concurrency/blockingqueue/
number: "081"
category: Java Concurrency
difficulty: ★★☆
depends_on: Thread, ExecutorService, Producer-Consumer Pattern
used_by: Producer-Consumer, Thread Pools, Task Queues
tags: #java, #concurrency, #queue, #producer-consumer, #blocking
---

# 081 — BlockingQueue

`#java` `#concurrency` `#queue` `#producer-consumer` `#blocking`

⚡ TL;DR — BlockingQueue is a thread-safe queue that blocks producers when full and consumers when empty — the idiomatic Java mechanism for producer-consumer decoupling without manual wait/notify.

| #081 | Category: Java Concurrency | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Thread, ExecutorService, Producer-Consumer Pattern | |
| **Used by:** | Producer-Consumer, Thread Pools, Task Queues | |

---

### 📘 Textbook Definition

`java.util.concurrent.BlockingQueue<E>` is a `Queue` that additionally supports blocking operations: `put(e)` blocks if the queue is full until space is available; `take()` blocks if the queue is empty until an element is available. Non-blocking variants (`offer`, `poll`) and timed variants (`offer(e, time, unit)`, `poll(time, unit)`) are also provided. Implementations: `LinkedBlockingQueue` (optionally bounded), `ArrayBlockingQueue` (bounded FIFO), `PriorityBlockingQueue` (unbounded, ordered), `SynchronousQueue` (zero-capacity handoff), `DelayQueue` (time-ordered delayed delivery).

---

### 🟢 Simple Definition (Easy)

BlockingQueue is a conveyor belt between producers and consumers. Producers put items on; consumers take items off. If the belt is full, producers wait. If the belt is empty, consumers wait. No manual coordination needed — the queue does it automatically.

---

### 🔵 Simple Definition (Elaborated)

The classic producer-consumer problem requires careful synchronization: producers must signal consumers when they add items, and consumers must signal producers when they remove items. BlockingQueue encapsulates all of this internally. `put()` and `take()` are the idiomatic choice: both block appropriately and respond to interruption. `ExecutorService`'s `FixedThreadPool` uses a `LinkedBlockingQueue` internally to queue submitted tasks.

---

### 🔩 First Principles Explanation

```
Producer-Consumer without BlockingQueue:
  Shared list + synchronized + wait/notify
  → 30+ lines of tricky, bug-prone code
  → Easy to miss spurious wakeup handling, notify vs notifyAll

With BlockingQueue:
  BlockingQueue<Task> queue = new ArrayBlockingQueue<>(100);

  Producer thread:
    queue.put(task);     // blocks if full, wakes when space available

  Consumer thread:
    Task t = queue.take(); // blocks if empty, wakes when item arrives

  → All synchronization, waiting, signalling handled internally
  → 2 lines replace 30 lines of manual coordination
```

**Key implementations compared:**

```
ArrayBlockingQueue(N)       → bounded FIFO; backed by array; single lock
LinkedBlockingQueue()       → optionally bounded; backed by linked list; two locks (head/tail)
LinkedBlockingQueue(N)        → bounded variant; higher throughput than Array for high concurrency
SynchronousQueue            → zero capacity; each put() waits for a take() — direct handoff
PriorityBlockingQueue       → unbounded; priority-ordered; no blocking on put()
DelayQueue<E extends Delayed> → elements available only after their delay expires
```

---

### 🧠 Mental Model / Analogy

> A restaurant pass-through window. Cooks (producers) place dishes on the shelf (`put()`). Waiters (consumers) collect dishes (`take()`). If the shelf is full, cooks wait. If the shelf is empty, waiters wait. Nobody needs to shout at each other — the pass-through window handles the coordination.

---

### ⚙️ How It Works — Method Comparison

| Operation | Throws exception | Returns special value | Blocks | Times out |
|---|---|---|---|---|
| Insert | `add(e)` | `offer(e)` → false | `put(e)` | `offer(e,t,u)` |
| Remove | `remove()` | `poll()` → null | `take()` | `poll(t,u)` |
| Examine | `element()` | `peek()` → null | — | — |

**For producer-consumer: always use `put()` and `take()`** — they block correctly and respond to interruption.

---

### 🔄 How It Connects

```
BlockingQueue
  │
  ├─ Inside ExecutorService → FixedThreadPool uses LinkedBlockingQueue for tasks
  ├─ Producer-Consumer     → put() / take() decoupling
  ├─ SynchronousQueue      → used in CachedThreadPool (direct handoff to thread)
  ├─ DelayQueue            → ScheduledThreadPool uses it for scheduled tasks
  └─ vs manual wait/notify → BlockingQueue replaces all manual coordination
```

---

### 💻 Code Example

```java
// Classic producer-consumer
BlockingQueue<String> queue = new ArrayBlockingQueue<>(50);

// Producer thread(s)
Runnable producer = () -> {
    try {
        while (!Thread.currentThread().isInterrupted()) {
            String item = generateItem();
            queue.put(item);  // blocks if queue is full
        }
    } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
};

// Consumer thread(s)
Runnable consumer = () -> {
    try {
        while (!Thread.currentThread().isInterrupted()) {
            String item = queue.take();  // blocks if queue is empty
            processItem(item);
        }
    } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
};

ExecutorService pool = Executors.newFixedThreadPool(4);
pool.submit(producer);
pool.submit(consumer);
pool.submit(consumer);  // 1 producer, 2 consumers
```

```java
// Non-blocking offer with timeout — producer back-pressure
boolean accepted = queue.offer(item, 500, TimeUnit.MILLISECONDS);
if (!accepted) {
    metrics.recordDropped();  // queue full after 500ms — drop or retry
    return;
}
```

```java
// SynchronousQueue — direct hand-off between threads (zero buffer)
BlockingQueue<Runnable> handoff = new SynchronousQueue<>();
// put() blocks until a take() is ready — guarantees direct delivery
// Used in CachedThreadPool: task handed directly to waiting thread
```

```java
// DrainTo — batch consumption
List<Task> batch = new ArrayList<>();
int drained = queue.drainTo(batch, 100); // drain up to 100 items at once
processBatch(batch);  // efficient batch processing
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| `LinkedBlockingQueue` has no capacity limit | Default constructor creates Integer.MAX_VALUE capacity (virtually unbounded → OOM risk) |
| `offer()` throws if queue is full | `offer()` returns `false` (no blocking, no exception); use `put()` to block |
| `SynchronousQueue` stores one element | SynchronousQueue has ZERO capacity — put() blocks until take() is ready |
| BlockingQueue is thread-safe for atomic multi-step ops | Individual operations are atomic; compound operations (check-size-then-put) still need synchronization |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Unbounded LinkedBlockingQueue — silent OOM under load**

```java
// Default LinkedBlockingQueue is effectively unbounded
ExecutorService pool = Executors.newFixedThreadPool(10); // ← uses unbounded LBQ internally
// If tasks are produced faster than consumed → queue grows → OOM

// Fix: use ThreadPoolExecutor with bounded queue + rejection policy
new ThreadPoolExecutor(10, 10, 0L, MILLISECONDS,
    new ArrayBlockingQueue<>(1000),
    new ThreadPoolExecutor.CallerRunsPolicy());
```

**Pitfall 2: Catching and ignoring InterruptedException on take()**

```java
// Bad: swallowing interruption — thread can never be stopped
while (true) {
    try { process(queue.take()); }
    catch (InterruptedException e) {} // ❌ — loop continues forever
}
// Fix:
catch (InterruptedException e) { Thread.currentThread().interrupt(); break; }
```

---

### 🔗 Related Keywords

- **[Producer-Consumer Pattern](./085 — Producer-Consumer Pattern.md)** — canonical use case
- **[Semaphore](./080 — Semaphore.md)** — alternative for resource throttling
- **[ExecutorService](./074 — ExecutorService.md)** — uses BlockingQueue internally for task queue
- **[CountDownLatch](./078 — CountDownLatch.md)** — coordination without data transfer

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Thread-safe queue: put() blocks when full;    │
│              │ take() blocks when empty — zero manual sync   │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Producer-consumer decoupling; task queues;    │
│              │ pipeline stages between thread pools          │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Don't use unbounded LBQ in production pools — │
│              │ queue grows without limit → OOM               │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "A conveyor belt that stops the producers     │
│              │  when full and the consumers when empty"      │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ ArrayBlockingQueue → SynchronousQueue →       │
│              │ DelayQueue → PriorityBlockingQueue            │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `SynchronousQueue` has zero capacity — every `put()` waits for a `take()`. How is this useful in `Executors.newCachedThreadPool()`? What property of the thread pool does this enable?

**Q2.** You process items in batches using `drainTo(batch, 100)`. Is this operation atomic? What happens if a producer adds items to the queue while `drainTo` is running?

**Q3.** `ArrayBlockingQueue` vs `LinkedBlockingQueue` — which has higher throughput under high concurrency and why? (Hint: single lock vs two locks.)

