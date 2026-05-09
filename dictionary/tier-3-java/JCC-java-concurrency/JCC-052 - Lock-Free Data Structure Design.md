---
id: JCC-052
title: Lock-Free Data Structure Design
category: Java Concurrency
tier: tier-3-java
folder: JCC-java-concurrency
difficulty: ★★★
depends_on: JCC-049, JCC-022, JCC-039, JCC-051
used_by:
related: JCC-049, JCC-022, JCC-039, JCC-051
tags:
  - java
  - concurrency
  - advanced
  - deep-dive
  - algorithm
  - datastructure
status: complete
version: 1
layout: default
parent: "Java Concurrency"
grand_parent: "Technical Dictionary"
nav_order: 52
permalink: /jcc/lock-free-data-structure-design/
---

# JCC-052 - Lock-Free Data Structure Design

⚡ TL;DR - Lock-free data structures use CAS operations to allow concurrent access without mutual exclusion, enabling progress even when threads are delayed or preempted.

| Metadata        |                                    |     |
| :-------------- | :--------------------------------- | :-- |
| **Depends on:** | JCC-049, JCC-022, JCC-039, JCC-051 |     |
| **Related:**    | JCC-049, JCC-022, JCC-039, JCC-051 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
All concurrent data structures use locks. A lock-based stack: `push()` acquires a mutex, modifies state, releases. This is correct. But problems emerge at scale: (1) a thread holding the lock gets preempted by the OS scheduler - all other threads block and make no progress. (2) Priority inversion: a low-priority thread holds a lock needed by a high-priority thread. (3) Lock contention becomes a scalability bottleneck when thousands of threads compete.

**THE BREAKING POINT:**
Real-time systems, high-frequency trading systems, and OS kernels cannot afford the unpredictable latency of lock-based structures. A 100-thread application spending 90% of CPU time in mutex contention is effectively single-threaded. When the shared queue in a work-stealing thread pool becomes the bottleneck, the entire system throughput is capped.

**THE INVENTION MOMENT:**
Maurice Herlihy (1991) proved that any data structure can be implemented in a lock-free manner using a universal primitive with consensus number infinity - Compare-And-Swap (CAS). Herlihy's "Wait-Free Synchronization" paper established the theoretical foundation. Michael and Scott (1996) published the practical lock-free queue algorithm used in Java's `ConcurrentLinkedQueue` today.

**EVOLUTION:**
1991: Herlihy's consensus hierarchy. 1996: Michael-Scott lock-free queue. 2004: Java 5 `java.util.concurrent.atomic`. 2017: Java 9 `VarHandle` enabling portable lock-free patterns. Modern: LMAX Disruptor - lock-free ring buffer achieving 25M+ ops/sec on single machine.

---

### 📘 Textbook Definition

A **lock-free data structure** is a concurrent data structure where at least one thread is guaranteed to make progress in a finite number of steps, regardless of the state or scheduling of other threads. It is implemented using atomic read-modify-write (RMW) operations such as CAS (Compare-And-Swap) instead of mutual exclusion. The JMM guarantees that CAS is atomic and has volatile memory semantics (establishes happens-before). Lock-free is weaker than wait-free (all threads make progress) but stronger than obstruction-free (a single thread running alone makes progress).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Lock-free structures replace mutex locks with CAS loops: read current state, compute new state, CAS from old to new, retry if CAS fails.

**One analogy:**

> Lock-free is like a checkout-free supermarket where customers scan and pay simultaneously. If two customers reach for the same last item, the scanner system detects the conflict and one retries. No one waits for a cashier (mutex). Progress happens continuously - at least one customer always succeeds.

**One insight:**
Lock-free does NOT mean "without locking overhead." It means without mutual exclusion. CAS can loop many times under contention. The benefit is system-level progress guarantee: no thread can block the entire structure by being preempted.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **CAS atomicity:** `compareAndSet(expected, update)` is atomic at hardware level. Either the full swap happens or nothing happens.
2. **CAS memory ordering:** CAS has volatile read + volatile write semantics. A successful CAS establishes happens-before.
3. **Progress guarantee:** Lock-free: at least one thread makes progress. The overall system never deadlocks or livelocks.
4. **No blocking:** A lock-free operation never blocks waiting for another thread to complete a critical section.

**DERIVED DESIGN:**
The CAS loop pattern: read head pointer, compute next state, CAS head from old to new. If CAS succeeds, we "own" the update. If CAS fails, another thread updated head between our read and CAS - retry. Under low contention: fast path succeeds on first try. Under high contention: retries increase, approaching lock-based overhead but never blocking.

**THE TRADE-OFFS:**
**Gain:** No deadlock. No priority inversion. Predictable latency under preemption. Better throughput under high thread counts for short operations.
**Cost:** ABA problem. Memory reclamation (SMR/hazard pointers). Higher cognitive complexity. Can be slower than a single-mutex structure under low contention.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Concurrent state management without mutual exclusion is inherently complex. Some retry logic is unavoidable.
**Accidental:** ABA problem is an artifact of pointer reuse. Hazard pointers, epoch-based reclamation, and `AtomicStampedReference` exist to address it.

---

### 🧪 Thought Experiment

**SETUP:**
A lock-free stack. Two threads both call `push(item)` simultaneously. The stack head is `A`. Both threads read head=A, both compute "new head = their item, next = A".

**WHAT HAPPENS:**
Thread 1's `CAS(head, A, item1)` succeeds. head is now `item1`. Thread 2's `CAS(head, A, item2)` FAILS because head is now `item1`, not A. Thread 2 retries: reads head=`item1`, computes new head=`item2`, next=`item1`. CAS succeeds. Final: `item2 -> item1 -> A`. Correct result. Neither thread blocked.

**THE ABA PROBLEM:**
Thread 1 reads head=A. Thread 2 pops A, pushes B, pops B, pushes A again. head is A again. Thread 1's `CAS(head, A, item1)` SUCCEEDS. But the stack state changed dramatically between Thread 1's read and CAS. Depending on the structure, this may corrupt the data structure.

**THE INSIGHT:**
ABA is not hypothetical. In memory allocators that reuse addresses, pointer values repeat. Fix: add a version stamp (`AtomicStampedReference`) or use hazard pointers for memory reclamation.

---

### 🧠 Mental Model / Analogy

> Lock-free design is like optimistic concurrency control in databases. READ COMMITTED with optimistic locking: read the current row version, compute changes, attempt UPDATE WHERE version = read_version. If another transaction changed the row, retry with fresh data. No table lock is held during computation. The database compares (version) and swaps (update) atomically - exactly CAS semantics.

Element mapping:

- **Row version** = head pointer in lock-free structure
- **UPDATE WHERE version = X** = CAS(expected=X, update=new)
- **Row was changed by another transaction** = CAS failure, retry
- **Committed transaction** = successful CAS with HB established

Where this analogy breaks down: database transactions can conflict on multiple rows. CAS only atomically operates on a single memory location. Multi-location atomic updates require DCAS (double CAS) or software transactional memory.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Lock-free structures are data structures (stacks, queues, maps) where multiple threads can read and write simultaneously without waiting for each other to "unlock" access. They use a hardware operation (CAS) to make updates safely.

**Level 2 - How to use it (junior developer):**
Prefer `ConcurrentLinkedQueue`, `ConcurrentLinkedDeque`, `ConcurrentHashMap`, `AtomicReference` in Java. These are well-tested lock-free or fine-grained-locking implementations. Implementing your own lock-free structure is a very advanced task.

**Level 3 - How it works (mid-level engineer):**
Every lock-free structure is built on the CAS loop: read current state, compute new state, CAS from current to new. If CAS fails, retry from scratch. Linearizability (appearing atomic at a single instant) is the correctness criterion. `ConcurrentLinkedQueue` uses Michael-Scott algorithm: two CAS operations per enqueue, one per dequeue, linearized at the CAS.

**Level 4 - Why it was designed this way (senior/staff):**
Herlihy's consensus hierarchy proves that CAS has consensus number infinity (can solve n-thread consensus for any n), while test-and-set has consensus number 1, fetch-and-add has consensus number 2. CAS is the universal primitive for lock-free construction. Modern lock-free structures in Java use `VarHandle` with `compareAndSet()` for portability and correctness across JVM implementations. LMAX Disruptor avoids even CAS in the hot path for single-producer cases by using sequence numbers and memory barriers only.

**Expert Thinking Cues:**

- "What is the linearization point of this operation?"
- "Where can ABA occur, and is `AtomicStampedReference` needed?"
- "Is this structure lock-free or wait-free? Does the application require the stronger guarantee?"

---

### ⚙️ How It Works (Mechanism)

**TREIBER STACK (LOCK-FREE):**

```java
public class TreiberStack<T> {
    private final AtomicReference<Node<T>> head =
        new AtomicReference<>(null);

    public void push(T item) {
        Node<T> newHead = new Node<>(item);
        Node<T> oldHead;
        do {
            oldHead = head.get();       // read
            newHead.next = oldHead;     // compute
        } while (!head.compareAndSet(oldHead, newHead)); // CAS
        // retry if CAS fails (another thread pushed)
    }

    public T pop() {
        Node<T> oldHead;
        Node<T> newHead;
        do {
            oldHead = head.get();
            if (oldHead == null) return null;
            newHead = oldHead.next;
        } while (!head.compareAndSet(oldHead, newHead));
        return oldHead.item;
    }

    private static class Node<T> {
        final T item;
        Node<T> next;
        Node(T item) { this.item = item; }
    }
}
```

**ABA FIX WITH STAMPED REFERENCE:**

```java
// BAD: ABA possible with plain AtomicReference
AtomicReference<Node<T>> head = new AtomicReference<>();

// GOOD: stamp prevents ABA false-positive
AtomicStampedReference<Node<T>> head =
    new AtomicStampedReference<>(null, 0);

// push with stamp:
int[] stampHolder = new int[1];
Node<T> oldHead = head.get(stampHolder);
head.compareAndSet(
    oldHead, newHead,
    stampHolder[0], stampHolder[0] + 1
);
```

**How to test / verify correctness:**
Use `jcstress` to test for linearizability violations under concurrent access. Write a stress test that spawns N threads doing concurrent push/pop, then verifies the stack invariants. Use `-XX:+StressLCM -XX:+StressGCM` to trigger JIT reorderings.

---

### 🔄 The Complete Picture - End-to-End Flow

**TREIBER STACK PUSH - NORMAL FLOW:**

```
T1: read head=A  -->  compute newHead{item,next=A}
                             |
                      CAS(head, A, newHead)
                             | SUCCESS
                             v
                      head = newHead  <- YOU ARE HERE

T2 arrives after T1: reads head=newHead, CAS succeeds
```

**TREIBER STACK PUSH - CAS CONTENTION:**

```
T1: read head=A  -->  compute new{item1, next=A}
T2: read head=A  -->  compute new{item2, next=A}
T1: CAS(A, new1) SUCCEEDS. head=new1
T2: CAS(A, new2) FAILS (head=new1, not A)
T2: retry: read head=new1 --> compute new{item2,next=new1}
T2: CAS(new1, new2) SUCCEEDS
```

**FAILURE PATH:**
ABA: T1 reads head=A. T2 pops A, pushes B, pops B, pushes A back. T1's CAS(A, new1) succeeds but the linked list below A may be corrupted (B is freed memory). Use `AtomicStampedReference` or epoch-based reclamation to prevent.

**WHAT CHANGES AT SCALE:**
Under high contention, CAS retry loops burn CPU. Consider: partitioned structures (ConcurrentHashMap uses 16-256 segments), queue-based lock (CLH queue), or LMAX Disruptor ring buffer for producer-consumer patterns. Lock-free is not always faster than a well-tuned lock-based structure.

---

### ⚖️ Comparison Table

| Property                     | Lock-Based               | Lock-Free               | Wait-Free  |
| ---------------------------- | ------------------------ | ----------------------- | ---------- |
| Progress guarantee           | None (deadlock possible) | System-level            | Per-thread |
| Complexity                   | Low-Medium               | High                    | Very High  |
| Throughput (low contention)  | High                     | High                    | High       |
| Throughput (high contention) | Degrades                 | Better                  | Best       |
| Deadlock risk                | Yes                      | No                      | No         |
| ABA problem                  | No                       | Yes (CAS)               | Yes (CAS)  |
| Java examples                | `LinkedBlockingQueue`    | `ConcurrentLinkedQueue` | N/A (rare) |

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                                                                          |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Lock-free is always faster than lock-based"           | Under low contention, a single uncontended `synchronized` block is faster than a CAS loop. Lock-free wins at high contention and when threads can be preempted mid-operation.                    |
| "Lock-free means no synchronization overhead"          | CAS has volatile semantics (memory barrier). Every CAS emits a memory fence instruction on ARM/x86. The overhead exists; it's just different from mutex overhead.                                |
| "ABA is rare in practice"                              | In memory allocators that recycle addresses (like `LockSupport`-based park/unpark, object pools), ABA is a real concern. The JVM's GC prevents some ABA cases but not all.                       |
| "ConcurrentHashMap is fully lock-free"                 | ConcurrentHashMap uses a mix: lock-free reads (volatile), CAS for empty bins, and synchronized for bin-level writes. It is NOT fully lock-free.                                                  |
| "Implementing lock-free structures is straightforward" | Designing and verifying a correct lock-free structure requires formal reasoning about linearization points, ABA, and memory reclamation. Even experts make mistakes. Use proven implementations. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: ABA Corruption**
**Symptom:** Lock-free stack or queue returns incorrect results or corrupts data intermittently. Hard to reproduce - only occurs under specific thread interleaving.
**Root Cause:** A node was popped and its memory address was reused for a new node. A waiting thread's CAS succeeds based on address equality, but the structural meaning changed.
**Diagnostic:**

```bash
# jcstress test targeting ABA
mvn verify -pl stress-tests -Dtest=ABATest
# Enable address reuse detection: -ea + reference tracking
```

**Fix:**

```java
// BAD: ABA possible
AtomicReference<Node<T>> head;
head.compareAndSet(oldHead, newHead);

// GOOD: stamp eliminates ABA false positive
AtomicStampedReference<Node<T>> head;
head.compareAndSet(
    oldHead, newHead, oldStamp, oldStamp+1
);
```

**Prevention:** Use `AtomicStampedReference` for pointer-based lock-free structures. Use epoch-based reclamation for production code.

---

**Failure Mode 2: Livelock Under Contention**
**Symptom:** High CPU usage. Operations take very long but threads never block. Throughput collapses.
**Root Cause:** All threads continuously fail CAS and retry, creating a livelock. Under extreme contention (e.g., 100 threads, 1 hot head pointer), CAS failure rate approaches 99%.
**Diagnostic:**

```bash
# Monitor CPU usage per thread vs throughput
pidstat -t -p <pid> 1
# High CPU, low throughput = CAS livelock
```

**Fix:** Add exponential backoff in retry loop, or switch to a lock-based structure with parking (which yields CPU):

```java
int backoff = 1;
while (!head.compareAndSet(old, next)) {
    if (backoff < 1024)
        backoff *= 2;
    Thread.onSpinWait(); // CPU hint for spin loop
    // Or: Thread.sleep(backoff) for heavy backoff
}
```

**Prevention:** Benchmark lock-free vs lock-based under representative contention levels. Don't choose lock-free purely on principle.

---

**Failure Mode 3: Memory Reclamation Hazard**
**Symptom:** Segfault or incorrect reads in non-GC languages; in Java - incorrect object access after logical removal.
**Root Cause:** A thread reads a node, another thread removes and "frees" it (returns to pool), and the first thread dereferences the now-invalid object.
**Diagnostic:** In Java, GC prevents actual memory-level issues, but object pooling can cause logical use-after-free. Review any code that re-uses node objects.
**Fix:** Avoid object pooling in lock-free structures in Java. In C++/Rust, use hazard pointers or RCU (Read-Copy-Update).
**Prevention:** In Java, prefer allocation over pooling for lock-free node objects. GC is your reclamation mechanism.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JCC-049 - Lock-Free Algorithm Strategy]] - CAS loop template and ABA analysis
- [[JCC-022 - CAS (Compare-And-Swap)]] - the fundamental primitive
- [[JCC-039 - VarHandle]] - portable CAS in Java 9+

**Builds On This (learn these next):**

- [[JCC-053 - Concurrent Algorithm Research]] - advanced concurrent algorithms

**Alternatives / Comparisons:**

- [[JCC-020 - Java Memory Model (JMM)]] - the memory ordering that makes CAS safe

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Concurrent structures using CAS    │
│               │ instead of mutual exclusion        │
│ PROBLEM       │ Lock contention; preemption risk   │
│ KEY INSIGHT   │ CAS loop: read, compute, CAS,      │
│               │ retry on failure                   │
│ USE WHEN      │ High contention; preemption risk   │
│ AVOID WHEN    │ Low contention; simpler locking ok │
│ TRADE-OFF     │ Progress guarantee vs. complexity  │
│ ONE-LINER     │ At least one thread always progres-│
│               │ ses; no deadlock possible          │
│ NEXT EXPLORE  │ JCC-053 Concurrent Algorithm Res.  │
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Lock-free = CAS loop (read, compute, CAS, retry). At least one thread always makes progress.
2. ABA problem: same address, different meaning. Fix with `AtomicStampedReference`.
3. Lock-free is not always faster. Benchmark under realistic contention before choosing.

**Interview one-liner:**
"Lock-free data structures use CAS loops instead of mutual exclusion - guaranteeing system-level progress (no deadlock, no priority inversion) at the cost of ABA problem, retry overhead, and higher implementation complexity."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When a single lock creates a throughput bottleneck, the first question is not "how do I make the lock faster" but "can I eliminate the lock by restructuring state access?" Lock-free design forces clarity about what state is truly shared and what can be made thread-local. Often, the investigation reveals that most state can be made unshared - the lock-free structure is the last resort for what truly must be shared.

**Where else this pattern appears:**

- **Database MVCC:** PostgreSQL and MySQL InnoDB use optimistic multi-version concurrency control - readers never block writers, writers CAS a version counter. The same "read-compute-swap" pattern.
- **Git object store:** Git's object database is append-only and content-addressed (SHA). Concurrent writes never conflict because content identity is the "CAS." Two writers creating identical objects produce identical hashes - idempotent.
- **Kubernetes etcd CAS:** `kubectl apply` uses resourceVersion as a CAS stamp. The PUT request includes `resourceVersion: N`; if the server's version differs, the update is rejected (CAS failure) - retry with fresh read.

---

### 💡 The Surprising Truth

Java's `ConcurrentLinkedQueue` is based on the Michael-Scott (MS) non-blocking queue algorithm from 1996. The algorithm uses two CAS operations: one for the actual enqueue and one to update the tail pointer. The tail pointer is allowed to LAG - it may point to a node one behind the actual tail. This intentional inconsistency is not a bug. It reduces contention by allowing enqueuers to "help" each other complete the tail update, rather than blocking. The queue is always linearizable even though the tail pointer is transiently incorrect. This "helping" pattern - threads assisting other threads' incomplete operations - is a fundamental technique in non-blocking algorithm design.

---

### 🧠 Think About This Before We Continue

**Q1 (E - First Principles):** The Treiber stack `push()` is lock-free. But if Thread 1 is infinitely fast and Thread 2 is infinitely slow, can Thread 2's `push()` ever complete? Is the Treiber stack wait-free?
_Hint:_ Lock-free guarantees SYSTEM progress (at least one thread). Wait-free guarantees PER-THREAD progress (every thread). Determine which property the Treiber stack satisfies.

**Q2 (B - Scale):** Under very high contention (1000 threads pushing simultaneously to a Treiber stack), describe what happens to CAS retry rates. At what point does the lock-free structure perform worse than a single-mutex structure, and why?
_Hint:_ Each CAS failure wastes CPU cycles on a doomed attempt. With N threads, at most 1 CAS succeeds per round. Estimate total CAS operations vs. successful ones as N grows.

**Q3 (C - Design Trade-off):** The LMAX Disruptor achieves extremely high throughput by replacing a lock-free queue's CAS operations with sequence numbers and memory barriers. What concurrency property does the Disruptor sacrifice to achieve this? What usage constraint makes this trade-off acceptable?
_Hint:_ The Disruptor's single-writer optimization requires exactly one producer. What happens with multiple producers? Why is this acceptable in the Disruptor's intended use case (event sourcing, financial systems)?
