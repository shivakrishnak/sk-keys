---
id: JCC-048
title: "Condition Interface (Lock Conditions)"
category: Java Concurrency
tier: tier-3-java
folder: JCC-java-concurrency
difficulty: ★★☆
depends_on: JCC-040, JCC-014, JCC-039
used_by: JCC-079
related: JCC-041, JCC-020, JCC-057
tags:
  - java
  - concurrency
  - pattern
  - intermediate
  - foundational
status: complete
version: 3
layout: default
parent: "Java Concurrency"
grand_parent: "Technical Dictionary"
nav_order: 27
permalink: /java-concurrency/condition-interface-lock-conditions/
---

# JCC-027 - CONDITION INTERFACE (LOCK CONDITIONS)

⚡ **TL;DR** - The `Condition` interface gives `ReentrantLock` users
selective `await`/`signal` control: wake only the threads waiting
for a *specific* condition, not all lock waiters.

---

| Field      | Value                                              |
|------------|----------------------------------------------------|
| Depends on | JCC-040 ReentrantLock, JCC-014 Future, JCC-039 Thread Lifecycle |
| Used by    | JCC-079 Lock-Free Data Structures                  |
| Related    | JCC-041 synchronized, JCC-020 Semaphore (Java), JCC-057 BlockingQueue |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
`synchronized` + `wait`/`notify` provides one implicit condition
per object monitor. In a bounded buffer with both producers and
consumers waiting, `notifyAll()` wakes EVERY waiter (both producers
and consumers), even though only one type is relevant. This causes
*spurious wakeups* that all re-check their condition, fail, and
go back to sleep - burning CPU cycles for no progress.

**THE BREAKING POINT:**
A bounded blocking queue has 50 producer threads waiting for space
and 50 consumer threads waiting for items. An item is added.
`notifyAll()` wakes all 100 threads. 50 consumers re-check "is
there an item?" - one succeeds; 99 go back to sleep.
Under high load this wasted context-switching degrades throughput
significantly.

**THE INVENTION MOMENT:**
`Java.util.concurrent.locks.Condition` (Java 5) allows a single
`ReentrantLock` to have *multiple named condition queues*. A bounded
buffer has `notEmpty` and `notFull` conditions. Adding an item
signals only `notEmpty` - waking only consumers. Removing signals
only `notFull` - waking only producers.

**EVOLUTION:**
- **Java 5:** `Condition`, `ReentrantLock.newCondition()`
- `ArrayBlockingQueue` and `LinkedBlockingQueue` internally use
  exactly this two-condition pattern (`notEmpty`, `notFull`)
- **Java 21:** `StructuredTaskScope` and virtual threads reduce
  the need for manual conditions in many patterns

---

### 📘 Textbook Definition

`java.util.concurrent.locks.Condition` is an interface obtained from
a `Lock` via `lock.newCondition()`. It mirrors `Object.wait/notify`
but:
- Supports multiple conditions per lock
- Provides `awaitUninterruptibly()` (ignores interrupt)
- Supports timed waits returning whether condition was met
- Must be used only while holding the associated lock

Key methods: `await()`, `awaitNanos(long)`, `awaitUntil(Date)`,
`signal()` (wakes one), `signalAll()` (wakes all on this condition).

---

### ⏱️ Understand It in 30 Seconds

**One line:** Multiple waiting rooms for one lock - signal only the
room with threads that are actually ready to run.

**One analogy:**
> An airport lounge has separate waiting areas: "gate A passengers"
> and "gate B passengers." When gate A boards, only gate A passengers
> are called - gate B remains seated. With `Object.wait/notifyAll`,
> there is one waiting area: every passenger jumps up, checks the
> board, and sits back down when it's not their gate.

**One insight:** `Condition.signal()` is targeted; `notifyAll()`
is a broadcast. For multiple thread types sharing one lock, targeted
signalling eliminates unnecessary wakeups.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A `Condition` is always associated with exactly one `Lock`.
2. `await()` atomically releases the lock and suspends the thread;
   upon return, the thread re-acquires the lock before proceeding.
3. `signal()` moves exactly one waiting thread from this condition's
   queue to the lock's acquisition queue.
4. Spurious wakeups are possible (OS-level) - always check the
   condition in a loop, not an `if`.
5. The lock must be held before calling `await()`, `signal()`, or
   `signalAll()` - violation causes `IllegalMonitorStateException`.

**DERIVED DESIGN:**
Internally, each `Condition` is a separate `AbstractQueuedSynchronizer`
node list. `await()` atomically moves the current thread from the
lock's owner slot to the condition's wait list and parks the thread.
`signal()` moves one thread from the condition wait list back to the
AQS lock queue.

**THE TRADE-OFFS:**

**Gain:** Selective signalling eliminates unnecessary wakeups;
multiple conditions model complex state machines clearly.

**Cost:** More code than `synchronized`; forgetting to hold the
lock causes `IllegalMonitorStateException`; spurious wakeup
handling still required.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** A thread must be able to wait for a *specific*
condition without being woken by unrelated state changes.

**Accidental:** The `await/signal` naming mirrors `wait/notify` but
uses a different interface - mixing them with `synchronized` is
a compilation error when possible but a runtime error when casting.

---

### 🧪 Thought Experiment

**SETUP:** Implement a bounded buffer (capacity=10) with producer
and consumer threads using only one condition (`synchronized` +
`notifyAll()`).

**WHAT HAPPENS WITHOUT Condition:**
50 producers, 50 consumers, buffer half full.
- Producer adds item, calls `notifyAll()`.
- All 50 sleeping consumers AND all 50 sleeping producers wake.
- First consumer takes item; all others check condition and sleep.
- Net: 98 wasted wakeups per produced item.

**WHAT HAPPENS WITH two Conditions:**
```java
final Lock lock = new ReentrantLock();
final Condition notFull  = lock.newCondition();
final Condition notEmpty = lock.newCondition();

void put(T item) throws InterruptedException {
    lock.lock();
    try {
        while (count == capacity) notFull.await();
        buffer[putIndex++] = item;
        notEmpty.signal(); // wake ONE consumer only
    } finally { lock.unlock(); }
}
```
Producer signals `notEmpty` - only sleeping consumers are woken.
Zero wasted wakeups.

**THE INSIGHT:** Granular conditions eliminate cross-type wakups,
converting O(n) unnecessary-wakeup cost to O(1).

---

### 🧠 Mental Model / Analogy

> A hospital has one nurse station (the lock) and two call buttons:
> "patient needs medication" (notEmpty) and "bed is ready"
> (notFull). Pressing the medication button signals only nurses
> assigned to medication. Pressing "bed ready" signals only
> admissions staff. Without separate buttons, every nurse must
> check every call and return if it's not their type.

**Element mapping:**
- Nurse station = `ReentrantLock`
- Patient call buttons = `Condition` objects
- Pressing medication button = `notEmpty.signal()`
- Nurses waiting for their call = threads in `await()`
- Nurse checks if task is relevant and returns = spurious wakeup
  handled by while loop

Where this analogy breaks down: human nurses can tell from context
which call is for them; Java threads must re-test the condition
boolean after every wakeup because spurious wakeups are possible.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
It's a way for a thread to say "wake me up when SPECIFICALLY THIS
thing happens" - and only those threads are woken, not everyone
waiting on the lock.

**Level 2 - How to use it (junior developer):**
```java
Lock lock = new ReentrantLock();
Condition hasItems = lock.newCondition();

// Producer signals when item added
void produce(T item) throws InterruptedException {
    lock.lock();
    try {
        addItem(item);
        hasItems.signal(); // wake one consumer
    } finally { lock.unlock(); }
}

// Consumer waits for items
T consume() throws InterruptedException {
    lock.lock();
    try {
        while (isEmpty()) {
            hasItems.await(); // release lock, sleep
        }
        return removeItem();
    } finally { lock.unlock(); }
}
```

**Level 3 - How it works (mid-level engineer):**
`ReentrantLock` internally uses `AbstractQueuedSynchronizer` (AQS).
Each `Condition` has a separate singly-linked list of waiting nodes.
`await()` adds the current thread's node to the condition's list
and releases the AQS lock, then parks. `signal()` removes the head
of the condition list and transfers it to the AQS sync queue (the
lock queue). The thread wakes when it wins the AQS lock acquisition.

**Level 4 - Why it was designed this way (senior/staff):**
The AQS design (Doug Lea) separates lock state management from
condition waiting lists. This allows one synchroniser to support
multiple condition queues with zero extra monitors - all managed in
userspace as linked lists, with LockSupport.park/unpark for
suspension. This is orders of magnitude faster than OS mutex + CV
operations for high-contention workloads.

**Expert Thinking Cues:**
- ALWAYS use `while`, not `if`, before `await()` - spurious wakeups
  and stolen signals require re-checking the condition.
- `signal()` is preferred over `signalAll()` when exactly one
  thread can make progress after the state change.
- `Condition` must be from the *same* lock you hold. Using a
  condition from a different lock is a programming error.
- `ArrayBlockingQueue` is the canonical reference implementation
  of the two-condition pattern - study its source code.

---

### ⚙️ How It Works (Mechanism)

**AQS node states:**
```
Condition wait list (per Condition):
  [node_T1] -> [node_T2] -> [node_T3]

signal() transfers node_T1 to AQS sync queue:
  AQS sync queue: [node_T1 (waiting for lock)]

When lock is released:
  node_T1 unparked, acquires lock, continues from await()
```

**await() internals:**
```
1. Check caller holds the lock
2. Save lock state (reentrance count)
3. Add current node to condition queue
4. Release lock fully (all reentrance levels)
5. LockSupport.park() (suspend)
6. On wakeup: spin/park until lock re-acquired
7. Restore saved lock state
8. Return to caller (condition re-checked in while loop)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (bounded buffer put/take):**
```
Producer: lock.lock()           <- YOU ARE HERE
       |
  buffer full? while: notFull.await()
       |          -> releases lock, parks producer
       |          <- consumer signals notFull
       |          <- producer re-acquires lock
  add item to buffer
  notEmpty.signal()
       |
  Consumer unparked, re-acquires lock
  takes item from buffer
  notFull.signal()
       |
  Producer unparked, re-acquires lock
  loop again
```

**FAILURE PATH:**
Thread interrupted while in `await()` -> `InterruptedException`
thrown; thread removed from condition queue, re-acquires lock,
exception propagates to caller.

**WHAT CHANGES AT SCALE:**
- Many condition objects per lock: negligible overhead (each is a
  pointer to a list node; no OS resource).
- Under very high contention, AQS's CLH queue fairness (FIFO lock
  grant to waiting threads) prevents starvation, unlike `synchronized`.

---

### 💻 Code Example

**BAD - using synchronized/notifyAll (wakes all threads):**
```java
// BAD: notifyAll wakes producers AND consumers
class BoundedBuffer<T> {
    private final Queue<T> q = new ArrayDeque<>();
    private final int cap;

    synchronized void put(T item) throws IE {
        while (q.size() == cap) wait();
        q.add(item);
        notifyAll(); // wakes everything!
    }

    synchronized T take() throws IE {
        while (q.isEmpty()) wait();
        T item = q.poll();
        notifyAll(); // wakes everything!
        return item;
    }
}
```

**GOOD - two conditions, targeted signals:**
```java
// GOOD: selectively wake only one type of waiter
import java.util.concurrent.locks.*;

public class BoundedBuffer<T> {
    private final Object[] items;
    private int head, tail, count;
    private final Lock lock = new ReentrantLock();
    private final Condition notFull  = lock.newCondition();
    private final Condition notEmpty = lock.newCondition();

    public BoundedBuffer(int capacity) {
        items = new Object[capacity];
    }

    public void put(T item) throws InterruptedException {
        lock.lock();
        try {
            // ALWAYS while, not if (spurious wakeup guard)
            while (count == items.length) notFull.await();
            items[tail] = item;
            tail = (tail + 1) % items.length;
            count++;
            notEmpty.signal(); // wake exactly one consumer
        } finally { lock.unlock(); }
    }

    @SuppressWarnings("unchecked")
    public T take() throws InterruptedException {
        lock.lock();
        try {
            while (count == 0) notEmpty.await();
            T item = (T) items[head];
            items[head] = null;
            head = (head + 1) % items.length;
            count--;
            notFull.signal(); // wake exactly one producer
            return item;
        } finally { lock.unlock(); }
    }
}
```

**How to test / verify correctness:**
```java
@Test
void boundedBufferBlocksWhenFull() throws Exception {
    BoundedBuffer<Integer> buf = new BoundedBuffer<>(2);
    buf.put(1); buf.put(2);

    CountDownLatch blocked = new CountDownLatch(1);
    Thread producer = new Thread(() -> {
        try {
            blocked.countDown();
            buf.put(3); // should block
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    });
    producer.start();
    blocked.await();
    Thread.sleep(100); // give time to block

    assertThat(producer.getState())
        .isIn(Thread.State.WAITING, Thread.State.TIMED_WAITING);

    buf.take(); // unblocks producer
    producer.join(500);
    assertThat(producer.isAlive()).isFalse();
}
```

---

### ⚖️ Comparison Table

| Feature | `Object.wait/notify` | `Condition` | `Semaphore` |
|---------|---------------------|-------------|-------------|
| Multiple condition queues | No (one per monitor) | Yes | No |
| Selective wakeup | Only `notifyAll` or random `notify` | `signal()` targeted | Release N permits |
| Interruptible await | Yes | Yes + uninterruptible variant | Yes |
| Timed wait | Yes | Yes (nanosecond precision) | Yes |
| Used with | `synchronized` | `Lock` implementations | Standalone |
| Spurious wakeup risk | Yes | Yes | No |
| Fairness control | No | Via lock option | Yes |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "`signal()` wakes all threads waiting on this condition" | `signal()` wakes exactly ONE thread in the condition queue. Use `signalAll()` to wake all - but usually `signal()` is correct in multi-condition patterns. |
| "Can use `Condition.await()` inside `synchronized` block" | `Condition` must be used with a `Lock` (e.g., `ReentrantLock`), not with `synchronized`. Mixing them causes `IllegalMonitorStateException`. |
| "Use `if (condition) await()` is safe" | Always use `while (condition) await()`. Spurious wakeups and signal stealing by other threads mean the condition may not hold after returning from `await()`. |
| "`await()` is the same as `Thread.sleep()`" | `await()` releases the lock and parks the thread; `sleep()` keeps the lock and sleeps. Critical difference for concurrent access. |
| "One Condition object is enough for all scenarios" | Two conditions (`notFull`, `notEmpty`) prevent cross-signalling. One condition for both means producers wake producers - all must re-check and sleep again. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Using `if` instead of `while` before `await()`**

**Symptom:** Intermittent `NullPointerException` or incorrect results
under load; works in single-threaded tests.

**Root Cause:** Spurious wakeup or signal stealing: thread wakes
from `await()` when condition is NOT actually met, proceeds to
consume a null or non-existent item.

**Diagnostic:**
```java
// Check: is condition guaranteed after await()?
// BAD:
if (buffer.isEmpty()) condition.await();
T item = buffer.remove(); // NPE if woken spuriously

// GOOD:
while (buffer.isEmpty()) condition.await();
T item = buffer.remove(); // guaranteed non-empty
```

---

**Failure Mode 2: Lock not held when calling await/signal**

**Symptom:** `IllegalMonitorStateException` at runtime.

**Root Cause:** `condition.await()` or `condition.signal()` called
without holding the associated lock.

**Diagnostic:**
```java
// Verify lock is held - add assertion in dev:
assert lock.isHeldByCurrentThread() :
    "Lock not held before await/signal";
condition.await();
```

**Fix:** Always wrap `await()` and `signal()` inside `lock.lock() /
finally { lock.unlock(); }` pattern.

---

**Failure Mode 3: Missed signal (signal before await)**

**Symptom:** Thread waits in `await()` indefinitely after condition
was already satisfied.

**Root Cause:** Producer signals `notEmpty` before consumer has
called `await()`. Signal is lost (no thread waiting = no effect).

**Diagnostic:**
```bash
jstack <pid> | grep "WAITING"
# Consumer stuck waiting while producer signalled earlier
```

**Fix:** Always check the condition state inside the lock BEFORE
calling `await()`:
```java
lock.lock();
try {
    while (isEmpty()) {   // check state first
        notEmpty.await(); // only wait if actually empty
    }
    return item;
} finally { lock.unlock(); }
```

This prevents the race: if condition is already met, `await()` is
never called and the already-fired signal is irrelevant.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JCC-040 - ReentrantLock]] - `Condition` is obtained from a Lock
- [[JCC-041 - synchronized]] - the simpler alternative (one condition)
- [[JCC-039 - Thread Lifecycle]] - WAITING state entered via `await()`

**Builds On This (learn these next):**
- [[JCC-079 - Lock-Free Data Structures]] - avoiding conditions
  entirely via CAS
- [[JCC-057 - BlockingQueue]] - `ArrayBlockingQueue` source implements
  this exact pattern

**Alternatives / Comparisons:**
- [[JCC-020 - Semaphore (Java)]] - counting semaphore for permit-
  based coordination, simpler but less flexible
- `Object.wait/notifyAll` - simpler but no multiple conditions

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS   | Named condition queues for a Lock; |
|              | targeted signal vs. broadcast      |
+--------------+------------------------------------+
| PROBLEM      | synchronized/notifyAll wakes all   |
|              | threads; most re-sleep wasting CPU |
+--------------+------------------------------------+
| KEY INSIGHT  | Multiple conditions = selective    |
|              | wakeup; signal only relevant waiters|
+--------------+------------------------------------+
| USE WHEN     | Multiple thread types wait on same |
|              | lock (producer/consumer, readers/writ)|
+--------------+------------------------------------+
| AVOID WHEN   | Single condition suffices; simpler |
|              | synchronized/notifyAll works fine  |
+--------------+------------------------------------+
| TRADE-OFF    | Eliminates spurious wakeups /      |
|              | more code; IMSE if lock not held   |
+--------------+------------------------------------+
| ONE-LINER    | while(empty) notEmpty.await();     |
|              | notFull.signal() after remove      |
+--------------+------------------------------------+
| NEXT EXPLORE | JCC-057 BlockingQueue internals,   |
|              | JCC-079 Lock-Free Data Structures  |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. Always use `while`, never `if`, to guard `await()` - spurious
   wakeups require re-checking the condition.
2. `signal()` wakes ONE thread; `signalAll()` wakes all on that
   condition - not all threads on the lock.
3. The lock MUST be held when calling `await()` or `signal()` -
   violation throws `IllegalMonitorStateException`.

**Interview one-liner:** "`Condition` gives `ReentrantLock` multiple
named wait queues; `signal()` wakes one thread on a specific
condition rather than all threads via `notifyAll()`, eliminating
cross-type wakeups in producer-consumer scenarios."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Precision beats broadcast in
notification systems. Notify only the threads (or services, or
subscribers) that can act on the change. Broadcasting to all and
letting each re-check wastes resources proportional to the size
of the waiting set.

**Where else this pattern appears:**
- **Linux futex (fast userspace mutex):** Multiple futex addresses
  act as separate condition variables - waiting on `futex_A` does
  not interfere with `futex_B` waiters. Same selective-wakeup design.
- **Postgres NOTIFY/LISTEN:** Clients listen on named channels;
  `NOTIFY channel_name` wakes only clients listening to that channel,
  not all database clients.
- **Reactive publish-subscribe (e.g., Reactor):** A `Flux` with
  multiple subscribers uses per-subscriber backpressure signals -
  each subscriber's demand signal only wakes publishers relevant
  to that subscriber's capacity.

---

### 💡 The Surprising Truth

`ArrayBlockingQueue` - the most-used bounded blocking queue in Java -
uses exactly one `ReentrantLock` and exactly two `Condition` objects
(`notEmpty`, `notFull`) for ALL operations. This means a single
lock serialises both puts and takes. Despite this bottleneck,
`ArrayBlockingQueue` outperforms `synchronized`-based equivalents
in benchmarks because selective signalling eliminates the thundering
herd that `notifyAll()` creates. The lesson: adding precision to
signalling is often worth more than adding lock sharding.

---

### 🧠 Think About This Before We Continue

**Question 1 (System Interaction):** `ArrayBlockingQueue` uses
one lock for both puts and takes, meaning producers and consumers
always contend. `LinkedBlockingQueue` uses two locks (one for puts,
one for takes). Under what traffic pattern does `LinkedBlockingQueue`
outperform `ArrayBlockingQueue`, and what is the cost of two-lock
design?

*Hint:* Study `LinkedBlockingQueue` source code and its `putLock`/
`takeLock` fields. Consider what happens when the queue transitions
from empty to non-empty with two separate locks.

---

**Question 2 (Design Trade-off):** You have 3 thread types sharing
one lock: readers, writers, and validators. Each type needs to wait
for different conditions. Design the `Condition` objects and explain
the signalling rules to prevent starvation of any thread type.

*Hint:* Research the Readers-Writers problem and how
`ReentrantReadWriteLock.Condition` objects express read/write
conditions. Consider whether using `ReentrantReadWriteLock` instead
simplifies the design.

---

**Question 3 (Root Cause):** A production system using
`ReentrantLock` and `Condition` sporadically hangs with some
threads stuck in `WAITING` on a condition. After 2 minutes, the
system self-heals without any code change. What are two plausible
root causes for this pattern, and what monitoring would distinguish
them?

*Hint:* Investigate spurious wakeup frequency on Linux, missed
signal races between check-and-await, and what happens if the
signalling thread itself gets stuck for 2 minutes before signalling.

