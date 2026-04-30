---
layout: default
title: "ConcurrentLinkedQueue"
parent: "Java Concurrency"
nav_order: 360
permalink: /java-concurrency/concurrentlinkedqueue/
number: "360"
category: Java Concurrency
difficulty: ★★★
depends_on: Atomic Variables, CAS, Race Condition, Queue
used_by: Lock-free Queues, Message Passing, High-throughput Pipelines
tags: #java, #concurrency, #lock-free, #queue, #cas
---

# 360 — ConcurrentLinkedQueue

`#java` `#concurrency` `#lock-free` `#queue` `#cas`

⚡ TL;DR — ConcurrentLinkedQueue is an unbounded, lock-free, thread-safe FIFO queue using CAS on head/tail nodes — offering high-throughput non-blocking enqueue/dequeue without the blocking semantics of BlockingQueue.

| #360 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Atomic Variables, CAS, Race Condition, Queue | |
| **Used by:** | Lock-free Queues, Message Passing, High-throughput Pipelines | |

---

### 📘 Textbook Definition

`java.util.concurrent.ConcurrentLinkedQueue<E>` is an unbounded, thread-safe FIFO queue based on Michael & Scott's lock-free linked-queue algorithm. It uses CAS operations on `AtomicReference` head and tail node pointers to achieve non-blocking concurrent access. `offer()` and `poll()` are the primary operations — both are non-blocking. `size()` is O(n) and imprecise under concurrency. Unlike `BlockingQueue`, `ConcurrentLinkedQueue` never blocks — `poll()` returns `null` if empty.

---

### 🟢 Simple Definition (Easy)

ConcurrentLinkedQueue is a thread-safe queue where adding and removing never block. Multiple threads can `offer()` and `poll()` simultaneously at high throughput. If the queue is empty, `poll()` returns null — it doesn't wait. Use when you want non-blocking concurrent queue access.

---

### 🔵 Simple Definition (Elaborated)

The distinction from `BlockingQueue` is fundamental: `BlockingQueue.take()` blocks when empty; `ConcurrentLinkedQueue.poll()` returns null. This makes CLQ unsuitable for producer-consumer (consumers would need to busy-poll or sleep). CLQ shines when producers and consumers are loosely coupled and the consumer naturally checks available work in a loop — like a work-stealing scheduler or a non-blocking message dispatcher.

---

### 🔩 First Principles Explanation

```
Lock-free queue algorithm (Michael & Scott 1996):
  Node: { value, AtomicReference<Node> next }
  Head: points to sentinel (dummy) node
  Tail: points to last node (may lag by one)

  offer(e):
    while (true):
      last = tail.get()
      next = last.next.get()
      if (last == tail.get()):         // tail still current
        if (next == null):             // tail is last node
          if (last.next.CAS(null, newNode)): // try to link
            tail.CAS(last, newNode)    // try to advance tail
            return true
        else:
          tail.CAS(last, next)         // advance stale tail

  poll():
    while (true):
      first = head.get()
      next = first.next.get()
      if (next == null) return null;  // empty
      if (head.CAS(first, next)):     // advance head
        return next.item;
```

---

### 🧠 Mental Model / Analogy

> A self-service restaurant with a conveyor belt. Cooks (producers) place dishes on the belt (`offer()`). Diners (consumers) take dishes (`poll()`). If the belt is empty, the diner finds nothing — no waiting. Multiple cooks and diners operate simultaneously without blocking each other, using careful choreography (CAS) to never collide.

---

### ⚙️ How It Works

```
Key methods:
  offer(E e)       → add to tail; always non-blocking; returns true
  poll()           → remove from head; returns null if empty; non-blocking
  peek()           → view head without removing; null if empty
  isEmpty()        → non-blocking empty check
  size()           → O(n) traversal; imprecise under concurrency

When to use:
  ✅ High-throughput concurrent producers/consumers
  ✅ Non-blocking polling in event loops
  ✅ Task queues where consumers check periodically
  ❌ Blocking wait when empty → use BlockingQueue instead
  ❌ Bounded capacity needed → use ArrayBlockingQueue
```

---

### 🔄 How It Connects

```
ConcurrentLinkedQueue
  ├─ vs BlockingQueue → CLQ never blocks; BQ can block on empty/full
  ├─ vs ArrayBlockingQueue → CLQ unbounded, lock-free; ABQ bounded, uses lock
  ├─ Lock-free    → uses CAS on node pointers (no mutex)
  └─ Used in      → non-blocking event queues, work-stealing schedulers
```

---

### 💻 Code Example

```java
ConcurrentLinkedQueue<Task> queue = new ConcurrentLinkedQueue<>();

// Multiple producer threads — non-blocking add
for (int i = 0; i < 4; i++) {
    final int id = i;
    pool.submit(() -> {
        for (int j = 0; j < 1000; j++) {
            queue.offer(new Task(id, j)); // never blocks
        }
    });
}

// Consumer: polling-based (not blocking)
pool.submit(() -> {
    while (!done) {
        Task task = queue.poll(); // null if empty
        if (task != null) {
            processTask(task);
        } else {
            Thread.yield(); // brief pause before retrying
        }
    }
    // drain remaining
    Task remaining;
    while ((remaining = queue.poll()) != null) processTask(remaining);
});
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| `size()` is accurate under concurrency | `size()` traverses the list — O(n) and counts nodes transiently added/removed |
| CLQ can replace BlockingQueue | CLQ is non-blocking — consumers must poll/retry; BQ blocks cleanly on empty |
| CLQ is bounded | CLQ is unbounded — add items faster than consumed → OOM |

---

### 🔗 Related Keywords

- **[BlockingQueue](./081 — BlockingQueue.md)** — blocking counterpart; better for producer-consumer
- **[Atomic Variables](./077 — Atomic Variables.md)** — CAS is the internal mechanism
- **[ConcurrentHashMap](./082 — ConcurrentHashMap.md)** — lock-free map companion

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Unbounded lock-free FIFO — offer/poll never   │
│              │ block; poll returns null when empty           │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ High-throughput non-blocking queue; consumers │
│              │ poll in a loop with other work to do          │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Blocking wait-when-empty → BlockingQueue;    │
│              │ need bounded capacity → ArrayBlockingQueue    │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Thread-safe queue: take or get null —       │
│              │  never waits, never blocks"                  │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ BlockingQueue → Atomic Variables → Lock-free  │
│              │ Data Structures → Disruptor pattern          │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Why is `ConcurrentLinkedQueue.size()` O(n) and inaccurate? Would you ever rely on it for a capacity check? What would you use instead?

**Q2.** The Michael-Scott queue allows the tail pointer to lag one node behind the actual tail. Why is this safe? What does the algorithm do when it detects a lagging tail?

**Q3.** Compare the throughput characteristics of `ConcurrentLinkedQueue` vs `LinkedBlockingQueue` under high concurrency. Under what specific conditions does CLQ outperform LBQ?

