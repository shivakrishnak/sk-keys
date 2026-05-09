---
id: JCC-068
title: Lock-Free Data Structures
category: Java Concurrency
tier: tier-3-java
folder: JCC-java-concurrency
difficulty: ★★★
depends_on: JCC-026, JCC-067, JCC-043
used_by: JCC-069, JCC-077
related: JCC-038, JCC-036, JCC-042
tags:
  - java
  - concurrency
  - advanced
  - datastructure
  - performance
status: complete
version: 1
layout: default
parent: "Java Concurrency"
grand_parent: "Technical Dictionary"
nav_order: 68
permalink: /java-concurrency/lock-free-data-structures/
---

# JCC-068 - LOCK-FREE DATA STRUCTURES

⚡ **TL;DR** - Data structures that use CAS (Compare-And-Swap)
operations to guarantee progress without mutual exclusion locks -
at least one thread always makes progress even if others are delayed.

---

| Field      | Value                                              |
|------------|----------------------------------------------------|
| Depends on | JCC-026 CAS (Compare-And-Swap), JCC-067 JMM Happens-Before, JCC-043 VarHandle |
| Used by    | JCC-069 Memory Visibility Diagnostics, JCC-077 Lock-Free Algorithm Theory |
| Related    | JCC-038 Atomic Classes, JCC-036 ConcurrentHashMap, JCC-042 Atomic Classes |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
`synchronized` data structures use mutual exclusion. When thread A
holds a lock, threads B through Z spin or block. A slow or paused
thread A (GC pause, OS scheduling delay) blocks all others. Under
high contention, lock convoys form: the OS schedules threads in
and out, each acquisition incurs a context switch, and throughput
collapses to near-zero - the "thundering herd" on lock release.

**THE BREAKING POINT:**
A high-frequency trading system processes 1 million messages/second.
A `synchronized` queue works at 100k/s load but collapses at
800k/s. Thread dumps show 95% of threads in BLOCKED state. The
lock holder is occasionally paused by GC for 50ms - that pause
cascades to stall the entire system.

**THE INVENTION MOMENT:**
Maurice Herlihy's 1991 paper "Wait-Free Synchronization" proved
that hardware CAS instructions can implement data structures where
no thread blocks another. The key: use compare-and-swap to
*atomically attempt an update*; retry if another thread interfered.
No thread is ever stuck waiting for a lock.

**EVOLUTION:**
- **Java 5:** `AtomicReference`, `AtomicInteger` with CAS
- **Java 6:** `ConcurrentLinkedQueue`, `ConcurrentLinkedDeque`
  (Michael & Scott non-blocking queue)
- **Java 8:** `LongAdder`, `LongAccumulator` (lock-free counters)
- **Java 9:** `VarHandle` for fine-grained access modes without
  boxing overhead
- **Java 21:** Structured concurrency/virtual threads make some
  blocking patterns cheap enough to prefer over lock-free complexity

---

### 📘 Textbook Definition

**Lock-free data structures** are concurrent data structures that
guarantee *system-wide progress*: at any moment, at least one thread
is making progress (completing an operation). They achieve this via
CPU compare-and-swap (CAS) operations without holding any lock.

**Progress guarantees (hierarchy):**
- **Obstruction-free:** Progress if the thread runs in isolation
- **Lock-free:** System-wide progress (at least one thread completes)
- **Wait-free:** Every thread completes in bounded steps (strongest)

Java's `AtomicReference.compareAndSet()`, `ConcurrentLinkedQueue`,
`LongAdder`, and `ConcurrentSkipListMap` are lock-free.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Multiple threads simultaneously attempt to update
shared state; only one succeeds per CAS; losers retry - but nobody
blocks nobody.

**One analogy:**
> Imagine 10 people trying to change a shared whiteboard number by
> crossing out the old value and writing a new one. Each person
> reads the value, crosses it out, and writes "old_value + 1" -
> but only if the value is still what they read. If someone else
> changed it first, they erase and try again with the new value.
> Nobody waits for a lock on the whiteboard.

**One insight:** CAS failures are not failures - they are retries.
Under low contention, nearly every CAS succeeds on the first try.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. CAS: atomically do `if (memory == expected) { memory = desired; return true; } else return false`
2. A successful CAS establishes a happens-before (volatile write
   semantics). Readers after the CAS see the new value.
3. A failed CAS leaves memory unchanged; the failing thread retries
   with the updated value.
4. The *ABA problem*: CAS on pointer P succeeds if P == expected,
   even if P was changed from A->B->A between reads. ABA is a
   correctness bug in naive lock-free structures.
5. Lock-free guarantees progress but NOT starvation-freedom: one
   thread may perpetually lose CAS races. Wait-free structures are
   needed for starvation freedom.

**DERIVED DESIGN:**
Lock-free linked structures (queues, stacks) use two-pointer CAS
to atomically swing a "next" pointer from null to a new node.
The Michael-Scott queue uses `tail->next` CAS for enqueue and
`head->next` CAS for dequeue - each with a single CAS point.

**THE TRADE-OFFS:**

**Gain:** No lock contention; no context switches on contention;
no deadlock possible; GC pauses in one thread do not block others.

**Cost:** ABA problem; algorithm complexity vs simple `synchronized`;
CAS retry loops can consume CPU under high contention (livelock
risk); memory reclamation is harder (hazard pointers needed in C++;
GC handles this in Java).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Atomic state transitions require hardware support
(CAS). The retry loop is unavoidable when multiple threads compete.

**Accidental:** The ABA problem is an accidental complication from
reusing memory addresses. Java's GC avoids ABA for reference-typed
structures (GC prevents address reuse while any live reference exists).

---

### 🧪 Thought Experiment

**SETUP:** Implement a concurrent stack. Compare lock-based vs
lock-free approaches under high contention.

**LOCK-BASED (synchronized):**
```
100 threads push/pop concurrently
lock contention: 99 threads block while 1 proceeds
GC pause in lock-holder: all 99 threads stall for 50ms
throughput: peaks around 50k ops/sec on 16 cores
```

**LOCK-FREE (CAS):**
```
100 threads push/pop concurrently
CAS contention: threads retry (no blocking)
GC pause in any thread: other 99 threads continue
throughput: 500k ops/sec on 16 cores under low-medium contention
```

```java
// Lock-free Treiber stack:
AtomicReference<Node<T>> top = new AtomicReference<>();

void push(T item) {
    Node<T> newNode = new Node<>(item);
    Node<T> current;
    do {
        current = top.get();
        newNode.next = current;
    } while (!top.compareAndSet(current, newNode));
    // Retry until CAS succeeds
}
```

**THE INSIGHT:** The retry loop replaces blocking - CPU busy but
making progress. Under high contention, CAS retry throughput can
still exceed lock throughput because no context switches occur.

---

### 🧠 Mental Model / Analogy

> Lock-free structures are like an optimistic transaction (optimistic
> locking). Read the state, compute the new state, atomically apply
> only if the state hasn't changed. If it changed (conflict), re-read
> and retry. Success rate depends on contention; under low contention,
> nearly every attempt succeeds immediately.

**Element mapping:**
- Reading the state = `AtomicReference.get()`
- Computing new state = building new node or computing new value
- Atomic apply = `compareAndSet(expected, new)`
- Conflict = another thread modified state between read and CAS
- Retry = the do-while loop
- No conflict = CAS returns true, operation complete

Where this analogy breaks down: unlike database transactions that
roll back all changes on conflict, a failed CAS simply discards
the failed computation (the new node or computed value) and retries
from scratch - allocation is wasted on failure.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Multiple threads compete to update shared data; they each try to
update atomically. If someone else got there first, they try again -
nobody waits.

**Level 2 - How to use it (junior developer):**
Use Java's built-in lock-free structures:
```java
// Thread-safe lock-free counter
LongAdder counter = new LongAdder();
counter.increment(); // lock-free, extremely fast under contention

// Thread-safe lock-free reference update
AtomicReference<Config> config = new AtomicReference<>(initial);
config.updateAndGet(old ->
    old.withNewValue(newValue)); // CAS loop internal
```

**Level 3 - How it works (mid-level engineer):**
`AtomicReference.compareAndSet(expected, update)` compiles to the
`CMPXCHG` instruction on x86 or `LDXR/STXR` loop on ARM. These
are atomic at the hardware level. The JVM emits these instructions
directly from the HotSpot JIT compiler's intrinsic for CAS methods.
No OS call, no lock, no context switch.

**Level 4 - Why it was designed this way (senior/staff):**
Hardware CAS is non-blocking at the CPU level but still has a
serialisation point (only one core can win each CAS). The key
design insight of lock-free structures: the serialisation point is
extremely narrow (a single instruction), not a code region. A
`synchronized` block serialises everything inside it; CAS
serialises only the atomic update instruction. This 100x narrower
critical "section" is why lock-free structures outperform locks
under contention.

**Expert Thinking Cues:**
- `ConcurrentLinkedQueue` is lock-free: prefer for high-contention
  MPMC (multi-producer, multi-consumer) queues.
- `LinkedBlockingQueue` uses separate locks for head and tail, but
  is NOT lock-free. Scales better than one-lock but worse than CAS.
- `LongAdder` vs `AtomicLong`: `LongAdder` distributes cells across
  CPUs; sum() collects. Zero CAS contention under typical load.
  `AtomicLong` suffers CAS failure loops under heavy contention.
- ABA is real: use `AtomicStampedReference` or `AtomicMarkableReference`
  where ABA corrupts correctness (rare in Java due to GC).

---

### ⚙️ How It Works (Mechanism)

**Michael-Scott non-blocking queue (simplified):**
```
Enqueue:
  newNode = Node(value, next=null)
  loop:
    tail = this.tail  (volatile read)
    last = tail.next  (volatile read)
    if last == null:
      if CAS(tail.next, null, newNode): break  // SUCCESS
    else:
      CAS(this.tail, tail, last)  // help advance tail

Dequeue:
  loop:
    head = this.head  (volatile read)
    tail = this.tail
    first = head.next (volatile read)
    if first == null: return EMPTY
    if CAS(this.head, head, first): return first.value  // SUCCESS
```

**Treiber stack (simpler - single CAS per operation):**
```
push(v):
  node = Node(v)
  loop:
    top = this.top (volatile read)
    node.next = top
    if CAS(this.top, top, node): return  // done

pop():
  loop:
    top = this.top (volatile read)
    if top == null: return empty
    newTop = top.next
    if CAS(this.top, top, newTop): return top.value
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (enqueue to ConcurrentLinkedQueue):**
```
Thread calls offer(item)        <- YOU ARE HERE
       |
  new Node(item) allocation
       |
  Read tail (volatile)
       |
  CAS tail.next from null to node
  |           |
FAIL         SUCCESS
  |           |
Retry        tail advanced
             item enqueued
```

**FAILURE PATH:**
Under extreme contention (100+ threads on one queue), CAS failure
rate rises and retry loops consume CPU. Not a deadlock or livelock
(guaranteed forward progress globally), but throughput can degrade
to less than a `synchronized` queue due to wasted CAS cycles.

**WHAT CHANGES AT SCALE:**
- On NUMA systems, a single atomic location shared across sockets
  incurs cross-socket coherence traffic. Distributed counter
  patterns (`LongAdder` cells) spread the hot location across cores.
- At distributed scale: the Paxos/Raft consensus algorithms are
  the distributed equivalent of lock-free CAS - atomic distributed
  "compare-and-swap" via leader election.

---

### 💻 Code Example

**BAD - synchronized with lock contention:**
```java
// BAD under high contention:
// one lock serialises all pushes and pops
class SyncStack<T> {
    private final Deque<T> stack = new ArrayDeque<>();

    synchronized void push(T item) { stack.push(item); }
    synchronized T pop() { return stack.pop(); }
}
```

**GOOD - Treiber lock-free stack:**
```java
// GOOD: CAS-based, no blocking, GC-friendly (no ABA issue)
import java.util.concurrent.atomic.AtomicReference;

public class LockFreeStack<T> {
    private static class Node<T> {
        final T value;
        Node<T> next;
        Node(T v) { value = v; }
    }

    private final AtomicReference<Node<T>> top =
        new AtomicReference<>();

    public void push(T item) {
        Node<T> node = new Node<>(item);
        Node<T> current;
        do {
            current = top.get();
            node.next = current;
        } while (!top.compareAndSet(current, node));
    }

    public T pop() {
        Node<T> current, next;
        do {
            current = top.get();
            if (current == null) return null;
            next = current.next;
        } while (!top.compareAndSet(current, next));
        return current.value;
    }
}
```

**GOOD - use LongAdder for high-contention counter:**
```java
// GOOD: avoids all CAS contention via per-CPU cells
LongAdder requestCount = new LongAdder();

// In request handler (called millions of times/sec):
requestCount.increment(); // nearly zero contention

// Periodically read:
long total = requestCount.sum();
```

**How to test / verify correctness:**
```java
@Test
void lockFreeStackIsSafe_underConcurrency() throws Exception {
    LockFreeStack<Integer> stack = new LockFreeStack<>();
    int threads = 16, opsPerThread = 10_000;
    CyclicBarrier barrier = new CyclicBarrier(threads);
    AtomicInteger sum = new AtomicInteger();

    List<Thread> workers = IntStream.range(0, threads)
        .mapToObj(i -> new Thread(() -> {
            try { barrier.await(); } catch (Exception e) {}
            for (int j = 0; j < opsPerThread; j++) {
                stack.push(1);
                Integer v = stack.pop();
                if (v != null) sum.addAndGet(v);
            }
        })).collect(toList());

    workers.forEach(Thread::start);
    for (Thread t : workers) t.join();

    // All pushed values should be popped (no data loss)
    // Some may remain in stack if push > pop:
    int remaining = 0;
    while (stack.pop() != null) remaining++;
    assertThat(sum.get() + remaining)
        .isEqualTo(threads * opsPerThread);
}
```

---

### ⚖️ Comparison Table

| Property | Lock-based | Lock-free | Wait-free |
|---------|-----------|-----------|-----------|
| Progress guarantee | Not guaranteed (lock holder can stall) | System-wide (1 thread always progresses) | Per-thread (all complete in bounded steps) |
| Deadlock possible | Yes | No | No |
| Starvation possible | Yes | Yes | No |
| Complexity | Low | Medium-High | Very High |
| Throughput (low contention) | High | High | High |
| Throughput (high contention) | Low (blocking) | High (retry) | Very High (bounded) |
| Java examples | `synchronized`, `ReentrantLock` | `ConcurrentLinkedQueue`, `LongAdder` | `CopyOnWriteArrayList.get()` |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Lock-free means no synchronisation" | Lock-free uses CAS at the hardware level, which IS synchronisation. It just avoids mutual exclusion *locks*, not atomic operations. |
| "Lock-free is always faster than synchronized" | Under very low contention, `synchronized` (biased locking) can be faster. Lock-free shines under high contention (many threads competing). |
| "ABA problem is specific to C/C++" | ABA is theoretically possible in Java for primitive-typed atomics (`AtomicInteger`). For reference-typed structures, Java's GC prevents address reuse while any live reference exists, making ABA impossible in practice. |
| "Lock-free structures are starvation-free" | Lock-free guarantees system-wide progress, not per-thread progress. One thread can repeatedly lose CAS races indefinitely. Wait-free structures guarantee per-thread bounded progress. |
| "`ConcurrentHashMap` is lock-free" | Java 8+ `ConcurrentHashMap` uses per-bucket CAS for inserts and lock-striped `synchronized` for other operations. It is partially lock-free, not fully. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: CAS retry storm under extreme contention**

**Symptom:** CPU at 100% with low actual throughput; many threads
show tight retry loops in thread dump.

**Root Cause:** 100+ threads competing on a single CAS location.
Retry rate scales with thread count - each failed CAS is wasted work.

**Diagnostic:**
```bash
jstack <pid> | grep -c "compareAndSet"
# High count in RUNNABLE state = CAS storm
# Also profile with async-profiler:
# asprof -e cpu -d 10 -f profile.html <pid>
# Look for: Unsafe.compareAndSetReference
```

**Fix:** Use `LongAdder` / `Striped64` pattern (distribute the hot
location across CPU-local cells). Or use bounded queues with
blocking to rate-limit producers.

---

**Failure Mode 2: Memory leak from abandoned nodes in lock-free queue**

**Symptom:** Heap grows continuously; heap dump shows many
`ConcurrentLinkedQueue$Node` or custom node objects.

**Root Cause:** Producer threads outpace consumer threads. Nodes
enqueue faster than dequeued and GC'd. Unbounded queue, no
backpressure.

**Diagnostic:**
```bash
jmap -dump:format=b,file=heap.hprof <pid>
# In Eclipse MAT: search for Node objects by count
```

**Fix:** Apply backpressure: use `LinkedBlockingQueue(capacity)`,
or a bounded `ArrayBlockingQueue`. Lock-free + unbounded = potential
OOM under sustained overload.

---

**Failure Mode 3: Correctness bug from naive ABA assumption**

**Symptom:** Rare data corruption in lock-free structure under
heavy churn (allocate/deallocate cycles).

**Root Cause:** ABA: thread reads pointer A, another thread changes
A->B->A; original thread CAS succeeds (sees A) but the node at A
is reused, corrupting invariants.

**Diagnostic:** 
This is extremely rare in Java (GC prevents address reuse). It CAN
occur with:
- Lock-free structures using `AtomicInteger` as a version counter
- Manual object pooling with `AtomicReference` without versioning

**Fix:** Use `AtomicStampedReference<T>` which includes a version
counter in the CAS:
```java
AtomicStampedReference<Node<T>> top =
    new AtomicStampedReference<>(null, 0);
// CAS on both reference AND stamp prevents ABA
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JCC-026 - CAS (Compare-And-Swap)]] - the hardware primitive
  underlying all lock-free structures
- [[JCC-067 - JMM Happens-Before - Deep Rules]] - the visibility
  semantics of successful CAS
- [[JCC-043 - VarHandle]] - fine-grained CAS access from Java 9+

**Builds On This (learn these next):**
- [[JCC-069 - Memory Visibility Diagnostics (jstack, JFR)]] - detect
  CAS storms and contention in production
- [[JCC-077 - Lock-Free Algorithm Theory (CAS Foundations)]] - formal
  proofs and consistency models

**Alternatives / Comparisons:**
- [[JCC-036 - ConcurrentHashMap]] - partially lock-free, JDK built-in
- [[JCC-042 - Atomic Classes]] - building blocks for custom lock-free
  structures

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS   | Data structures using CAS atomic   |
|              | ops to progress without locks      |
+--------------+------------------------------------+
| PROBLEM      | Locks cause blocking, contention,  |
|              | GC pauses cascade to all waiters   |
+--------------+------------------------------------+
| KEY INSIGHT  | CAS narrows critical region to one |
|              | instruction; failed CAS = retry    |
+--------------+------------------------------------+
| USE WHEN     | High contention, latency-sensitive,|
|              | cannot tolerate GC pause cascades  |
+--------------+------------------------------------+
| AVOID WHEN   | Low contention (synchronized wins),|
|              | strict starvation freedom required |
+--------------+------------------------------------+
| TRADE-OFF    | High throughput under contention / |
|              | algorithm complexity, ABA, retry storm|
+--------------+------------------------------------+
| ONE-LINER    | do { old=ref.get(); new=compute(); }|
|              | while (!ref.compareAndSet(old,new))|
+--------------+------------------------------------+
| NEXT EXPLORE | JCC-077 Lock-Free Algorithm Theory,|
|              | JCC-069 Memory Visibility Diag     |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. CAS = read-modify-write atomically; retry on failure - no thread
   ever blocks another.
2. ABA is mostly a non-issue in Java thanks to GC, but use
   `AtomicStampedReference` when using integer-keyed object pools.
3. Under extreme contention, distribute the hot CAS location using
   `LongAdder`/`Striped64` rather than a single `AtomicLong`.

**Interview one-liner:** "Lock-free data structures use CAS loops
to guarantee at least one thread always makes progress without
mutual exclusion - no blocking, no deadlock, but retry storms under
extreme contention require distribution strategies like `LongAdder`."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Narrowing the serialisation
point to the minimum necessary atomic unit reduces contention
proportionally. The art of lock-free design is identifying exactly
which state transition must be atomic, and making only that
transition atomic - nothing more.

**Where else this pattern appears:**
- **Optimistic concurrency in databases:** "Read, compute new state,
  write only if row version unchanged" is database-level CAS.
  PostgreSQL's MVCC and OCC (optimistic concurrency control) use
  this pattern for transaction isolation.
- **Paxos leader election:** A proposer reads the current ballot,
  proposes a higher ballot, and proceeds only if no competing
  proposal with a higher ballot appeared in between - CAS at
  distributed system scale.
- **Git merge with auto-merge disabled:** `git commit` succeeds
  only if the branch tip is still what the developer saw when they
  started working. If someone else pushed, the commit is rejected -
  a distributed CAS on the branch ref.

---

### 💡 The Surprising Truth

The `ConcurrentLinkedQueue` in Java's standard library is more complex
than it first appears - it uses a "lazy" tail update algorithm where
the tail pointer can lag one node behind the actual tail. This is a
deliberate optimisation: updating the tail pointer on every enqueue
would require two CAS operations (one for `next` pointer, one for
`tail`). By allowing `tail` to lag, only one CAS is needed per
typical enqueue, and the "help" mechanism (any thread can advance
the laggy tail) maintains lock-freedom. This means observing the
tail pointer externally gives you an approximate, not exact, view
of the queue tail - a subtle correctness hazard for any code that
tries to use the queue's internal state for coordination.

---

### 🧠 Think About This Before We Continue

**Question 1 (Root Cause):** Your `ConcurrentLinkedQueue`-based
message pipeline processes 500k messages/second at steady state.
Under a sudden spike (2M/second), throughput DROPS to 100k/second.
Thread dump shows 200 threads in RUNNABLE state with tight CAS
retry loops. Why does adding more threads make things worse, and
what is the correct solution?

*Hint:* Research the contention amplification effect in CAS retry
loops - each failed CAS causes a cache line invalidation that
forces ALL competing threads to reload the line, creating a
multiplicative slowdown. Explore `LinkedTransferQueue` vs
`ConcurrentLinkedQueue` and the striping pattern.

---

**Question 2 (First Principles):** The Treiber stack is provably
correct for Java (no ABA) because the GC prevents address reuse.
But if you implement the same algorithm in C++ with a custom
allocator that reuses freed node addresses, ABA becomes real.
Design a version of the Treiber stack that is ABA-safe in C++
without using hazard pointers, using only a 64-bit CAS and a
monotonically increasing tag counter.

*Hint:* Research tagged pointer CAS (packing a version counter into
the upper bits of a 64-bit pointer on 64-bit systems where only 48
bits are used for addresses) and how this is used in lock-free
implementations like Folly's MPMCQueue.

---

**Question 3 (Design Trade-off):** You need a high-throughput
bounded queue with the following requirements: O(1) enqueue, O(1)
dequeue, no starvation, maximum throughput at 16 cores, supports
1,000 producers and 100 consumers. Compare (a) `ArrayBlockingQueue`,
(b) `LinkedBlockingQueue`, (c) `ConcurrentLinkedQueue` with a
`Semaphore` for bounds, and (d) a ring buffer with CAS. Which
approach maximises throughput, and what are the correctness trade-offs?

*Hint:* Study LMAX Disruptor's ring buffer design and why it
achieves 10x `ArrayBlockingQueue` throughput, and where it trades
away fairness and bounded latency for throughput.

