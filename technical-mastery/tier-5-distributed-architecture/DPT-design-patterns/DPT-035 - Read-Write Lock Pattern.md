---
id: DPT-035
title: Read-Write Lock Pattern
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-005, DPT-031, DPT-033
used_by: DPT-064
related: DPT-031, DPT-033, DPT-036
tags:
  - pattern
  - concurrency
  - advanced
  - read-write-lock
  - synchronized
  - reentrantreadwritelock
  - cache
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 35
permalink: /technical-mastery/design-patterns/read-write-lock/
---

⚡ TL;DR - Read-Write Lock allows unlimited concurrent
readers OR one exclusive writer at a time - optimizing
for read-heavy data structures by avoiding the bottleneck
of mutual exclusion between readers.

| #35 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-031, DPT-033 | |
| **Used by:** | DPT-064 | |
| **Related:** | DPT-031, DPT-033, DPT-036 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An in-memory configuration cache: 1000 reads per second,
1 write per second (config refresh). Standard `synchronized`:

```java
synchronized Map<String, String> configCache;

synchronized String get(String key) {
    return configCache.get(key);
}
synchronized void put(String key, String value) {
    configCache.put(key, value);
}
```

**THE PERFORMANCE PROBLEM:**
1000 readers/second all try to acquire the same lock.
Only one reader runs at a time even though reads are
safe to run concurrently. 999 threads queue behind
one reader thread. Throughput bottleneck for a read-heavy,
write-rare data structure. The synchronization that is
REQUIRED for the 1 write/second is applied to ALL 1000
reads/second - massive over-synchronization.

**THE INVENTION MOMENT:**
Read-Write Lock: reads can run concurrently with each
other (multiple threads hold the read lock simultaneously).
A write requires exclusive access (blocks all readers
and other writers). This removes the serialization
bottleneck for reads, which is correct because reads
do not modify shared state and therefore do not conflict
with each other.

---

### 📘 Textbook Definition

The **Read-Write Lock** pattern is a concurrency design
pattern that provides two types of locks for shared data:
a shared read lock (multiple threads can hold it
simultaneously) and an exclusive write lock (only one
thread can hold it, blocking all readers and other writers).
The pattern optimizes for read-heavy access: reads
never block each other. Writes have exclusive access.
In Java, `ReentrantReadWriteLock` implements this pattern.
`StampedLock` (Java 8+) provides an optimistic variant
where reads can proceed without blocking even during
a write (validated after the fact).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Read-Write Lock says "reads can happen together; a write
needs everyone to step back."

**One analogy:**
> A library reading room. Multiple readers can sit at
> desks simultaneously (shared read lock: concurrent reads).
> When a librarian needs to rearrange shelves (write lock):
> the room empties first; all readers leave; the librarian
> rearranges; then readers return. The librarian does NOT
> need to clear the room between individual readers -
> only before rearranging.

**One insight:**
Read-Write Lock's correctness invariant: "Two threads
reading the same immutable data cannot produce an inconsistent
state." The lock exploits this: reads are concurrent-safe
when no write is happening. The lock ONLY serializes
the moments of data modification.

---

### 🔩 First Principles Explanation

**LOCK COMPATIBILITY MATRIX:**
```
         No lock    Read lock   Write lock
No lock    OK          OK          OK
Read lock  OK          OK          BLOCKED
Write lock OK        BLOCKED      BLOCKED
```
Read lock: compatible with other read locks; blocks write.
Write lock: incompatible with both read and write locks.

**JAVA API: `ReentrantReadWriteLock`:**
```java
ReentrantReadWriteLock rwLock = new ReentrantReadWriteLock();
Lock readLock  = rwLock.readLock();
Lock writeLock = rwLock.writeLock();

// READ:
readLock.lock();
try { return data.get(key); } finally { readLock.unlock(); }

// WRITE:
writeLock.lock();
try { data.put(key, value); } finally { writeLock.unlock(); }
```

**WRITER STARVATION:**
If readers continuously hold the read lock, writers
may wait indefinitely. `ReentrantReadWriteLock(fair=true)`:
fairness prevents starvation (FIFO ordering of waiters).
But fair mode reduces throughput. Most uses: non-fair
(default) with occasional writes is fine. If writes are
frequent: fairness or a different data structure.

**`StampedLock` (Java 8+ optimistic reads):**
```java
StampedLock lock = new StampedLock();

// Optimistic read: no lock acquired
long stamp = lock.tryOptimisticRead();
int value = readData();
if (!lock.validate(stamp)) {  // a write happened during our read
    // Fall back to a full read lock
    stamp = lock.readLock();
    try { value = readData(); } finally { lock.unlockRead(stamp); }
}
// If validate() succeeds: no write happened - value is correct
// Optimistic path: ZERO lock acquisition cost
```

**TRADE-OFFS:**

**Gain:** Read throughput improvement for read-heavy,
write-rare data. No false contention between readers.

**Cost:** More complex than `synchronized`. Write starvation
risk in write-heavy scenarios. `ReentrantReadWriteLock`
is heavier than a simple mutex for write-heavy access.
Lock upgrading (read → write) is NOT supported: must
release read lock before acquiring write lock. `StampedLock`
does not support `Condition` variables.

---

### 🧪 Thought Experiment

**SETUP:**
10 reader threads + 1 writer thread, all sharing a config
map.

**`synchronized` (mutex):**
Reader 1 holds lock: readers 2-10 and the writer all queue.
One thread at a time. Total throughput: 1 / (avg lock hold time).

**`ReentrantReadWriteLock`:**
Readers 1-10 all hold the read lock simultaneously.
When writer wants the write lock: readers finish, writer
proceeds, then readers resume. Total read throughput:
10x higher than mutex during non-write periods.

**When `ReentrantReadWriteLock` is WORSE than mutex:**
If writes are frequent (>10% of operations): the
write-lock acquisition overhead + reader suspension
overhead can exceed the savings from concurrent reads.
At >50% writes: a `ConcurrentHashMap` or `synchronized`
is often faster.

---

### 🧠 Mental Model / Analogy

> Read-Write Lock is a ROAD BRIDGE. Multiple cars (readers)
> can cross simultaneously in normal operation. When
> maintenance is needed (writer): the bridge signals
> "no more cars on-ramp." When the last car clears (existing
> readers finish): maintenance crew (writer) enters,
> does the work, leaves. Then the bridge opens again.
> Cars never block each other in normal operation -
> only when maintenance is happening.

- "Cars crossing simultaneously" = concurrent reads
- "Bridge maintenance" = write lock
- "Wait for all cars to clear" = wait for readers to finish
- "No new cars while maintenance in progress" = new readers blocked

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Read-Write Lock lets many people read shared data at
the same time (no blocking between readers). When someone
needs to change the data: everyone waits while the change
is made, then everyone can read again. Normal mutex
(synchronized) makes everyone wait even for reads.

**Level 2 - How to use it (junior developer):**
Create `ReentrantReadWriteLock`. Get `readLock()` and
`writeLock()`. Wrap reads in `readLock().lock()/unlock()`.
Wrap writes in `writeLock().lock()/unlock()`. Always use
try/finally to release locks. Never acquire the write
lock while holding the read lock (deadlock risk).

**Level 3 - How it works (mid-level engineer):**
`ReentrantReadWriteLock`'s state is stored in one `int`.
Upper 16 bits: number of active read lock holders.
Lower 16 bits: write lock hold count (reentrant writer).
Reading: `getReadHoldCount()` threads increment the
upper 16 bits via CAS. Writing: requires upper 16 bits
to be 0 AND lower 16 bits to be 0 (exclusive). Writers
queue in an `AQS` (AbstractQueuedSynchronizer) queue.
New readers arriving while a writer is waiting: depends
on fairness mode. Non-fair (default): new readers can
sneak past a waiting writer (writer starvation possible).
Fair: waiting writer gets priority over new readers.

**Level 4 - Why it was designed this way (senior/staff):**
The fundamental insight: concurrent reads are safe iff
the data does not change during the read. This is true
for any data structure that is not modified. A mutex
(synchronized) does not distinguish between conflicting
operations (write-write, read-write) and non-conflicting
operations (read-read). Read-Write Lock exploits the
non-conflicting read-read case to allow concurrency.
The pattern is most valuable for shared caches, lookup
tables, and configuration stores where 99% of accesses
are reads and writes are rare refreshes. For truly
concurrent data: `ConcurrentHashMap` (which uses
a read-optimized stripe locking internally) may be
better than manual `ReentrantReadWriteLock`.

**Level 5 - Mastery (distinguished engineer):**
`StampedLock` (Java 8) is the evolution of Read-Write Lock
with optimistic reads. The insight: if a write is very
rare, even the read lock acquisition (a CAS on the state)
is overhead. Optimistic read: read without acquiring
any lock, then validate that no write occurred during
the read. If validation fails: retry with a full read
lock. In practice, optimistic reads are very fast
(no CAS, no AQS) when writes are absent. Throughput:
much higher than `ReentrantReadWriteLock` for read-heavy
workloads. Caveat: `StampedLock` is NOT reentrant and
does NOT support `Condition`. For complex locking
logic: `ReentrantReadWriteLock` is safer. For maximum
performance in read-heavy cache scenarios: `StampedLock`
optimistic reads.

---

### ⚙️ How It Works (Mechanism)

```
ReentrantReadWriteLock State Machine
┌─────────────────────────────────────────────────────────┐
│ State: [readers: N | writer: 0/1]                       │
│                                                         │
│ Acquire read lock:                                      │
│   if (writer == 0): readers++  (CAS) → read acquired    │
│   if (writer == 1): enqueue reader → BLOCKED            │
│                                                         │
│ Release read lock:                                      │
│   readers--                                             │
│   if (readers == 0 && writers waiting):                 │
│       wake up first waiting writer                      │
│                                                         │
│ Acquire write lock:                                     │
│   if (readers == 0 && writer == 0):                     │
│       writer = 1 → write acquired                       │
│   else: enqueue writer → BLOCKED                        │
│                                                         │
│ Release write lock:                                     │
│   writer = 0                                            │
│   wake up all waiting readers (or next waiting writer)  │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Config cache with 10 readers and 1 writer:

t=0: R1 acquires read lock (readers=1)
t=1: R2 acquires read lock (readers=2) - NO CONTENTION
t=2: R3...R10 all acquire read lock (readers=10) -
  concurrent
t=3: W1 tries write lock: readers=10 → BLOCKS
t=4: R1 releases read lock (readers=9)
...
t=13: R10 releases (readers=0) → W1 wakes up
t=13: W1 acquires write lock → refreshes config
t=14: W1 releases write lock
t=14: all waiting readers wake up, acquire read locks →
  concurrent again

Throughput comparison for 1000 reads/s, 1 write/s:
synchronized:   ~1 read per lock hold time, sequential
RW Lock:        10 reads simultaneously → ~10x throughput
                (blocked only during the 1 write/s)
```

---

### 💻 Code Example

**Example 1 - Synchronized read-heavy cache (over-synchronized):**

```java
// BAD: synchronized blocks all readers even from each other
class ConfigCache {
    private final Map<String, String> cache = new HashMap<>();

    synchronized String get(String key) {
        return cache.get(key);
        // 1000 readers/s all waiting for this synchronized block
        // Even though reads never conflict with each other
    }

    synchronized void refresh(Map<String, String> newConfig) {
        cache.clear();
        cache.putAll(newConfig);
    }
}
```

**Example 2 - Read-Write Lock (correct, performant):**

```java
// GOOD: reads concurrent, writes exclusive

import java.util.concurrent.locks.*;

class ConfigCache {
    private final Map<String, String> cache = new HashMap<>();
    private final ReentrantReadWriteLock rwLock =
        new ReentrantReadWriteLock();
    private final Lock readLock  = rwLock.readLock();
    private final Lock writeLock = rwLock.writeLock();

    String get(String key) {
        readLock.lock();
        try {
            return cache.get(key);  // concurrent with other readers
        } finally {
            readLock.unlock();  // ALWAYS in finally
        }
    }

    String getOrDefault(String key, String def) {
        readLock.lock();
        try {
            return cache.getOrDefault(key, def);
        } finally {
            readLock.unlock();
        }
    }

    void refresh(Map<String, String> newConfig) {
        writeLock.lock();
        try {
            cache.clear();
            cache.putAll(newConfig);
        } finally {
            writeLock.unlock();  // ALWAYS in finally
        }
    }

    // Read lock stats for monitoring
    int getReadHoldCount() {
        return rwLock.getReadHoldCount();
    }
}
```

**Example 3 - StampedLock with optimistic read:**

```java
// BEST for read-heavy: StampedLock with optimistic read

import java.util.concurrent.locks.StampedLock;

class HotConfigCache {
    private volatile Map<String, String> cache = new HashMap<>();
    private final StampedLock lock = new StampedLock();

    String get(String key) {
        // Try optimistic read first (no lock acquisition)
        long stamp = lock.tryOptimisticRead();
        String value = cache.get(key);
        // snapshot data under optimistic read

        // Validate: if a write happened during our read, stamp is
        // invalid
        if (!lock.validate(stamp)) {
            // Writer modified cache during our read: fall back to
            // read lock
            stamp = lock.readLock();
            try {
                value = cache.get(key);
            } finally {
                lock.unlockRead(stamp);
            }
        }
        return value;
        // Fast path (no writes): zero lock overhead
    }

    void refresh(Map<String, String> newConfig) {
        long stamp = lock.writeLock();
        try {
            cache = new HashMap<>(newConfig);
        } finally {
            lock.unlockWrite(stamp);
        }
    }
}
```

**Example 4 - Detecting write starvation:**

```java
// Monitoring: detect writer starvation
ReentrantReadWriteLock rwLock = new ReentrantReadWriteLock();

// Collect metrics periodically
void emitLockMetrics() {
    metrics.gauge("rw.read.lock.holders").set(
        rwLock.getReadLockCount());
    metrics.gauge("rw.write.queue.length").set(
        rwLock.getQueueLength()); // threads waiting for write lock

    if (rwLock.getQueueLength() > 10) {
        log.warn("Write lock contention: {} writers waiting. "
            + "Consider fair mode or reducing read duration.",
            rwLock.getQueueLength());
    }
}
```

---

### ⚖️ Comparison Table

| Lock Type | Concurrent reads | Write throughput | Complexity | Use when |
|---|---|---|---|---|
| `synchronized` | No | Good | Low | Write-heavy, simple access |
| `ReentrantLock` | No | Good | Medium | Complex locking, tryLock |
| **ReadWriteLock** | Yes | Fair | Medium | Read-heavy (>80% reads) |
| `StampedLock` | Yes + optimistic | Fair | High | Read-heavy, max performance |
| `ConcurrentHashMap` | N/A | Good | Low | Map-specific, concurrent access |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| ReentrantReadWriteLock is always faster than synchronized | Only for read-heavy (>80% reads). For write-heavy: RRWL overhead (state CAS, queue management) can make it SLOWER than synchronized. Benchmark in your scenario |
| Lock upgrading: hold read lock, then acquire write lock | DEADLOCK: RRWL does NOT support lock upgrading. Two threads both holding read locks both try to upgrade to write lock → each waits for the other to release read lock → deadlock. Must: release read lock, then acquire write lock |
| StampedLock is always better than ReentrantReadWriteLock | StampedLock is NOT reentrant, does NOT support Condition variables, and has a more complex API. For code that uses Condition.await/signal or recursively acquires locks, RRWL is safer |
| Fair mode prevents starvation completely | Fair mode (FIFO ordering) prevents WRITER starvation but reduces overall throughput by preventing readers from "batching" (multiple readers going through simultaneously). Use fair mode only if writer starvation is an observed problem |

---

### 🚨 Failure Modes & Diagnosis

**Deadlock: Read Lock Upgrade Attempt**

**Symptom:**
Application freezes. Thread dump shows multiple threads
in `BLOCKED` state, all inside `writeLock.lock()` while
holding the read lock.

**Root Cause:**
Thread 1: holds read lock, tries to acquire write lock.
Thread 2: holds read lock, tries to acquire write lock.
Neither can acquire write lock (the other holds read lock).
Neither releases read lock (both waiting for write lock).
DEADLOCK.

**Diagnosis:**
```
# Thread dump: jstack <pid>
# Look for:
"thread-1" - BLOCKED waiting for write lock
   at ...readWriteLock.writeLock().lock()
   - locked (RRWL read lock held)

"thread-2" - BLOCKED waiting for write lock
   at ...readWriteLock.writeLock().lock()
   - locked (RRWL read lock held)
```

**Fix:**
```java
// WRONG: upgrade attempt = deadlock
readLock.lock();
try {
    if (needsRefresh()) {
        writeLock.lock();
        // DEADLOCK if another thread also holds read
        ...
    }
} finally { readLock.unlock(); }

// CORRECT: release read, reacquire write
readLock.lock();
boolean refresh;
try { refresh = needsRefresh(); }
finally { readLock.unlock(); } // release first

if (refresh) {
    writeLock.lock();
    try { doRefresh(); }
    finally { writeLock.unlock(); }
}
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Double-Checked Locking` - DPT-031; understanding
  Java Memory Model (volatile, happens-before) is essential
  before understanding lock semantics

**Builds On This (learn these next):**
- `Active Object Pattern` - DPT-036; Active Object uses
  Read-Write Locks internally to protect shared state

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Multiple concurrent readers OR one       │
│              │ exclusive writer (never both)            │
├──────────────┼──────────────────────────────────────────┤
│ JAVA API     │ ReentrantReadWriteLock → readLock(),     │
│              │ writeLock(); StampedLock for optimistic  │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ >80% reads, rare writes (config cache,   │
│              │ reference data, lookup tables)           │
├──────────────┼──────────────────────────────────────────┤
│ DEADLOCK RISK│ Never acquire write lock while holding   │
│              │ read lock (lock upgrade = deadlock)      │
├──────────────┼──────────────────────────────────────────┤
│ STARVATION   │ Fair=true: prevents writer starvation    │
│              │ Fair=false (default): higher throughput  │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Active Object → Event Bus                │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Read-Write Lock: reads concurrent with each other,
   write is exclusive. Correct invariant: reads never
   conflict; only read-write and write-write conflict.
   Use when >80% accesses are reads (config caches, etc.).
2. NEVER try to "upgrade" from read lock to write lock
   while holding the read lock. Release the read lock
   first, then acquire the write lock. Upgrade attempts
   cause deadlock.
3. `StampedLock.tryOptimisticRead()` is the maximum-
   performance option for read-heavy: reads proceed with
   ZERO lock acquisition, validated after. Falls back to
   full read lock if a write occurred. Not reentrant.

