---
layout: default
title: "Lock-Free Data Structures"
parent: "Java Concurrency"
nav_order: 101
permalink: /java-concurrency/lock-free-data-structures/
number: "101"
category: Java Concurrency
difficulty: ★★★
depends_on: Atomic Variables, CAS, ConcurrentLinkedQueue, Memory Barrier
used_by: High-throughput Systems, Non-blocking Algorithms, LMAX Disruptor
tags: #java, #concurrency, #lock-free, #non-blocking, #cas, #advanced
---

# 101 — Lock-Free Data Structures

`#java` `#concurrency` `#lock-free` `#non-blocking` `#cas` `#advanced`

⚡ TL;DR — Lock-free data structures use CAS loops instead of mutexes — threads never block each other; at least one thread always makes progress even when others fail their CAS, eliminating deadlock and reducing context-switching overhead.

| #101 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Atomic Variables, CAS, ConcurrentLinkedQueue, Memory Barrier | |
| **Used by:** | High-throughput Systems, Non-blocking Algorithms, LMAX Disruptor | |

---

### 📘 Textbook Definition

A **lock-free** data structure guarantees that at least one thread makes progress in a finite number of steps, regardless of what other threads do. Lock-free algorithms use compare-and-swap (CAS) operations: read a value, compute the new value, attempt CAS; if another thread won the CAS, retry. A **wait-free** structure gives stronger guarantees: every thread completes in a bounded number of steps. Java's `AtomicInteger`, `ConcurrentLinkedQueue`, and `ConcurrentHashMap` are all lock-free.

---

### 🟢 Simple Definition (Easy)

Lock-based: "I lock the door, do my work, unlock." Lock-free: "I read the current state, compute my change, try to apply it in one shot. If someone else changed it first, I re-read and retry." No door, no blocking — threads race optimistically instead of waiting in line.

---

### 🔵 Simple Definition (Elaborated)

Lock-free algorithms are harder to write but offer three critical advantages: (1) no deadlock (no locks = no lock cycles); (2) no priority inversion; (3) higher throughput under high contention when CAS retries are cheap compared to OS thread suspension. The trade-off: under extreme contention, CAS retries cause busy-spinning. For most real workloads (medium concurrency), lock-free collections outperform lock-based ones significantly.

---

### 🔩 First Principles Explanation

```
Lock-based stack push:
  lock.lock()
  stack.push(item)
  lock.unlock()
  → If 100 threads call push: 99 blocked waiting (OS suspended)
  → 2 context switches per thread (in + out)
  → 100 threads × 2 switches = 200 context switches per batch

Lock-free stack push (Treiber Stack):
  while (true):
    Node oldTop = head.get()     // read current
    newNode.next = oldTop        // link to current top
    if head.CAS(oldTop, newNode) // try to swing head
      break                      // success
    // else: another thread pushed first → retry

  → No blocked threads; failed CAS = one volatile read + retry
  → 100 threads: some succeed, others retry; at any moment, one is making progress

Progress guarantees:
  wait-free  : every thread completes in bounded steps (strongest)
  lock-free  : at least one thread makes progress (weaker, but practical)
  obstruction-free: thread makes progress when it runs alone (weakest)
```

**Treiber Stack (lock-free stack):**

```
State: AtomicReference<Node> head

push(T item):
  Node node = new Node(item)
  do {
    node.next = head.get()
  } while (!head.compareAndSet(node.next, node))

pop():
  Node oldHead
  do {
    oldHead = head.get()
    if (oldHead == null) return null  // empty
  } while (!head.compareAndSet(oldHead, oldHead.next))
  return oldHead.item
```

---

### 🧠 Mental Model / Analogy

> Post-it notes on a shared whiteboard. Lock-based: one person holds the marker — everyone else waits. Lock-free: everyone writes on their own sticky note, then tries to slap it on the board at the same time. One note sticks — the others see the board changed, update their note, and try again. Nobody waits; the board always makes progress.

---

### ⚙️ How It Works — Java Lock-Free Structures

```
java.util.concurrent.atomic:
  AtomicInteger     → lock-free int (CAS increment, getAndSet)
  AtomicReference<V>→ lock-free object reference
  AtomicStampedReference → CAS with version stamp (ABA prevention)
  LongAdder         → striped lock-free counter (high contention)
  DoubleAccumulator → lock-free custom accumulation

java.util.concurrent:
  ConcurrentLinkedQueue   → Michael-Scott lock-free linked queue
  ConcurrentLinkedDeque   → lock-free double-ended queue
  ConcurrentHashMap       → lock-free reads; CAS inserts to empty buckets
  CopyOnWriteArrayList    → lock-free reads; copy-on-write for writes

External:
  LMAX Disruptor          → ring buffer, mechanical sympathy, wait-free sequencer
  JCTools                 → SPSC/MPSC/MPMC queues optimised for specific concurrency profiles
```

---

### 🔄 How It Connects

```
Lock-Free Data Structures
  │
  ├─ Built on    → CAS (compareAndSet), volatile, memory barriers
  ├─ Used by     → ConcurrentLinkedQueue, AtomicInteger, ConcurrentHashMap
  ├─ Advantages  → no deadlock, no priority inversion, low latency
  ├─ vs Lock-based → LF better at high concurrency; lock better for complex operations
  └─ Pitfalls    → ABA problem, livliness under extreme contention
```

---

### 💻 Code Example

```java
// Lock-free Treiber Stack
public class LockFreeStack<T> {
    private final AtomicReference<Node<T>> head = new AtomicReference<>();

    public void push(T item) {
        Node<T> node = new Node<>(item);
        do {
            node.next = head.get();
        } while (!head.compareAndSet(node.next, node));
    }

    public T pop() {
        Node<T> oldHead;
        do {
            oldHead = head.get();
            if (oldHead == null) return null;
        } while (!head.compareAndSet(oldHead, oldHead.next));
        return oldHead.item;
    }

    static class Node<T> {
        final T item;
        Node<T> next;
        Node(T item) { this.item = item; }
    }
}
```

```java
// Lock-free statistics accumulator
import java.util.concurrent.atomic.LongAdder;

public class Stats {
    private final LongAdder totalRequests   = new LongAdder();
    private final LongAdder failedRequests  = new LongAdder();
    private final LongAdder totalLatencyMs  = new LongAdder();

    public void record(boolean success, long latencyMs) {
        totalRequests.increment();                // lock-free per-stripe increment
        if (!success) failedRequests.increment();
        totalLatencyMs.add(latencyMs);
    }

    public void printStats() {
        long total   = totalRequests.sum();
        long failed  = failedRequests.sum();
        double avgMs = total > 0 ? (double) totalLatencyMs.sum() / total : 0;
        System.out.printf("Requests: %d, Failures: %d, AvgLatency: %.2fms%n",
            total, failed, avgMs);
    }
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Lock-free = no synchronization | Lock-free uses CAS + memory barriers — still synchronizes, just without OS mutex |
| Lock-free is always faster | Under low contention, mutex can beat CAS; CAS overhead accrues with retries |
| Lock-free prevents all races | It prevents deadlock and priority inversion; logic bugs still possible in CAS loops |
| Wait-free and lock-free are the same | Lock-free: one thread progresses; wait-free: ALL threads progress in bounded steps |

---

### 🔥 Pitfalls in Production

**ABA problem in lock-free stack:**

```java
// Thread A reads head = NodeA
// Thread B: pops A, pushes B, pushes A back
// Thread A: CAS(NodeA → newNode) ← succeeds! But NodeB is LOST from stack
// Fix: AtomicStampedReference<Node> — version stamp prevents ABA
AtomicStampedReference<Node<T>> head = new AtomicStampedReference<>(null, 0);
int[] stamp = {0};
Node<T> old = head.get(stamp);
head.compareAndSet(old, newNode, stamp[0], stamp[0] + 1); // must match BOTH ref AND stamp
```

---

### 🔗 Related Keywords

- **[Atomic Variables](./077 — Atomic Variables.md)** — the CAS primitives lock-free is built on
- **[ConcurrentLinkedQueue](./098 — ConcurrentLinkedQueue.md)** — concrete lock-free queue
- **[ConcurrentHashMap](./082 — ConcurrentHashMap.md)** — lock-free reads + CAS inserts
- **[Race Condition](./072 — Race Condition.md)** — lock-free eliminates lock-based races, not logic races

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ CAS loops instead of mutexes — one thread     │
│              │ always progresses; no block, no deadlock      │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ High-throughput counters, queues, stacks with │
│              │ high read:write; avoid deadlock by design     │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Very high contention (CAS retry storm);       │
│              │ complex multi-step operations → use lock      │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Try, check, swap — nobody waits,             │
│              │  but somebody always wins"                    │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ ABA Problem → AtomicStampedReference →        │
│              │ LMAX Disruptor → JCTools → wait-free          │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A lock-free algorithm is spinning (CAS retrying constantly) under extreme contention. How does this differ from a deadlock? Could you call this "safe" from a correctness standpoint? What would you do architecturally to reduce the contention?

**Q2.** `LongAdder` uses striped cells to avoid CAS contention on a single counter. How does it aggregate the cells into a final sum? What is the trade-off in terms of consistency / accuracy during a `sum()` call?

**Q3.** The LMAX Disruptor achieves near-zero latency for a sequential event queue. How does it eliminate CAS entirely in the common case? (Hint: think about the ring buffer design and pre-allocated slots.)

