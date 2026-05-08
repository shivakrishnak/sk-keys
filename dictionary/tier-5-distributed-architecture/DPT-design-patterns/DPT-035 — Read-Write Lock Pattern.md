---
layout: default
title: "Read-Write Lock Pattern"
parent: "Design Patterns"
nav_order: 35
permalink: /design-patterns/read-write-lock-pattern/
id: DPT-035
category: Design Patterns
difficulty: ★★★
depends_on: Mutex, ReentrantLock, Java Concurrency, Java Memory Model (JMM), ReadWriteLock
used_by: Caching, In-Memory Data Stores, Configuration Management, Database Buffer Pools
related: Double-Checked Locking, StampedLock, ReentrantLock, Optimistic Locking, Mutex
tags:
  - pattern
  - deep-dive
  - concurrency
  - java
  - performance
---

# DPT-035 — Read-Write Lock Pattern

⚡ TL;DR — Read-Write Lock allows unlimited concurrent reads while ensuring exclusive access for writes, dramatically increasing read throughput for read-heavy shared data.

| #795 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Mutex, ReentrantLock, Java Concurrency, Java Memory Model (JMM), ReadWriteLock | |
| **Used by:** | Caching, In-Memory Data Stores, Configuration Management, Database Buffer Pools | |
| **Related:** | Double-Checked Locking, StampedLock, ReentrantLock, Optimistic Locking, Mutex | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An in-memory configuration store is read 50,000 times/second by every request handler and written once per minute by an admin update. Without a Read-Write Lock, a `synchronized` method serialises all 50,000 reads: each thread waits for the previous to finish reading (even though reads don't conflict with each other). 50,000 threads per second queueing for a mutex that protects read-only access — all that contention for data nobody is modifying.

**THE BREAKING POINT:**
A `synchronized` mutex treats read and write operations identically — both are mutually exclusive. This is correct but overly conservative: reads are safe to run concurrently (they don't modify state; they can't interfere with each other). Holding exclusive locks for reads wastes throughput that could be parallelised.

**THE INVENTION MOMENT:**
This is exactly why the Read-Write Lock pattern was created. Multiple readers acquire the read lock concurrently. A writer acquires the exclusive write lock — no readers or other writers may hold any lock simultaneously. Readers never block each other.

---

### 📘 Textbook Definition

The **Read-Write Lock** pattern (also: Readers-Writers problem) allows multiple readers to access a shared resource concurrently while ensuring that any writer has exclusive access. The lock has two modes: **read lock** (shared — many threads can hold it simultaneously) and **write lock** (exclusive — only one thread holds it; no readers may proceed). When a writer requests the lock, it waits for existing readers to finish, then proceeds exclusively. Java implements this with `java.util.concurrent.locks.ReadWriteLock` (`ReentrantReadWriteLock`) and the higher-performance `StampedLock`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Many can read at once; only one can write at a time — and writing blocks everyone.

**One analogy:**
> A library reading room has a special rule: anyone can read books simultaneously (multiple readers). But if a librarian needs to re-shelve and reorganise (write), everyone must leave the room and wait. The librarian gets the room to themselves. After the librarian leaves, readers flood back in.

**One insight:**
Read-Write Lock is a split mutex: the "write" half behaves like a traditional mutex; the "read" half cooperates with other readers. The performance gain is proportional to the read-to-write ratio. If reads are 99% of traffic, nearly all serialisation is eliminated.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Multiple reads on immutable-during-read data are always safe concurrently.
2. A write changes state — during a write, no other thread (reader or writer) must observe a partial update.
3. After a write completes, all subsequent reads must see the new state.

**DERIVED DESIGN:**
Given invariants 1+2: two lock modes. Read lock: acquired by many threads simultaneously as long as no writer holds the write lock. Write lock: exclusive — acquired only when NO readers and NO other writers hold any lock.

Given invariant 3: the write lock uses a `volatile` write or memory barrier to ensure new state is visible to all subsequent readers (Java Memory Model guarantee — lock release happens-before lock acquire).

The internal state machine: `(readers=0, writing=false)` is the idle state. `readers > 0, writing=false` = read-locked. `readers=0, writing=true` = write-locked. Transitions: read lock acquire requires `!writing`; write lock acquire requires `readers==0 && !writing`.

**THE TRADE-OFFS:**
**Gain:** Concurrent readers — throughput scales with reader thread count; write operations remain exclusive and safe.
**Cost:** Write starvation risk — if readers continuously arrive, a waiting writer is never granted the lock; `ReentrantReadWriteLock` includes optional writer-preference fairness; complexity higher than simple mutex; write lock downgrade is allowed (write→read) but upgrade (read→write) is not (deadlock risk).

---

### 🧪 Thought Experiment

**SETUP:**
AppConfiguration stores 50 settings. Read: `getConfig(key)`. Write: `updateConfig(key, value)` (once every 60 seconds). 10,000 reads/second.

**WITHOUT READ-WRITE LOCK (simple mutex):**
`synchronized getConfig()` and `synchronized updateConfig()`. 10,000 threads/second queue for an exclusive lock. Even though all reads are non-conflicting, they serialise. Throughput: limited by lock acquisition rate on a single mutex. At 10,000 μs contention overhead per second: ~10 seconds of lock wait accumulated every second.

**WITH READ-WRITE LOCK:**
`readLock.lock()` → `getConfig()` → `readLock.unlock()`. 10,000 read threads acquire read lock concurrently. No contention between readers. 1 writer/minute acquires write lock — pauses all readers for milliseconds. 10,000 reads/second served at full parallelism. Once per minute, a sub-millisecond pause for the config update.

**THE INSIGHT:**
Lock granularity should match data access pattern. Reads that don't conflict don't need a lock that prevents concurrency. The read-write lock's split mode aligns locking with actual data dependency.

---

### 🧠 Mental Model / Analogy

> Read-Write Lock is like a highway bridge with a special traffic rule. During normal hours (read lock held), cars flow in both directions simultaneously — traffic moves freely. For major maintenance (write lock), the bridge closes completely: all existing cars must clear; no new cars may enter. When maintenance finishes, normal bidirectional flow resumes. The key: cars going the same direction never interfere, so they don't need to take turns.

- "Cars flowing freely" → concurrent readers
- "Bridge closed for maintenance" → write lock held
- "Cars must clear before maintenance starts" → wait for readers to release
- "Same direction, no interference" → reads don't modify state
- "Maintenance complete, bridge reopens" → write lock released, readers resume

Where this analogy breaks down: in real traffic, bidirectional flow CAN conflict head-on. In the reader case, all readers truly share data without conflict. The analogy captures the "closed for exclusive work" semantics well.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Read-Write Lock is a two-mode lock. Lots of people can read a shared document at the same time. But when someone edits it, everyone else must wait — and the editor also waits for all readers to finish before starting.

**Level 2 — How to use it (junior developer):**
```java
ReadWriteLock rwLock = new ReentrantReadWriteLock();
Lock readLock = rwLock.readLock();
Lock writeLock = rwLock.writeLock();
// Read: readLock.lock(); try { ... } finally { readLock.unlock(); }
// Write: writeLock.lock(); try { ... } finally { writeLock.unlock(); }
```
Always use `try/finally` to guarantee unlock. Never hold a read lock and attempt to upgrade to a write lock — this deadlocks.

**Level 3 — How it works (mid-level engineer):**
`ReentrantReadWriteLock` uses an internal `int state` field split into two 16-bit halves: high 16 bits = shared (read) count; low 16 bits = exclusive (write) count. Read lock acquired via CAS on the high bits. Write lock acquired via CAS on both halves (requires full state = 0). The fair mode (`new ReentrantReadWriteLock(true)`) uses a CLH queue to prevent writer starvation — when a writer waits, new readers are also queued behind it. The unfair mode prioritises immediate lock acquisition, preferring throughput over fairness. `StampedLock` (Java 8+) is a higher-performance alternative: it offers optimistic reads (no lock acquisition — just a stamp validation) that avoid even the CAS overhead for the common case.

**Level 4 — Why it was designed this way (senior/staff):**
The Readers-Writers Problem is a classic OS concurrency problem (Courtois, 1971) with two variants: reader-preference (no reader waits if no writer has the lock) and writer-preference (no writer waits while other writers are waiting). `ReentrantReadWriteLock` with `fair=false` approximates reader-preference (higher read throughput, potential writer starvation). `StampedLock` (Java 8+) adds a third mode — optimistic read — which reads without acquiring any lock, then validates with a stamp. If the stamp is still valid, the read is committed. If not (a writer intervened), fall back to a read lock. This is an optimistic concurrency strategy: assume no writer, validate after. For very high read frequency with rare writes, `StampedLock` optimistic reads achieve near-zero overhead for the common case. The cost: `StampedLock` is not reentrant and does not support condition variables — different API contract from `ReentrantReadWriteLock`.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│  READ-WRITE LOCK — STATE MACHINE                     │
│                                                      │
│  State: (readers=N, writer=false)                    │
│                                                      │
│  readLock.lock():                                    │
│    if writer=false: readers++; proceed (CAS)         │
│    else: wait (writer must finish first)             │
│                                                      │
│  readLock.unlock():                                  │
│    readers--; if readers==0: signal waiting writer   │
│                                                      │
│  writeLock.lock():                                   │
│    wait until: readers==0 AND writer=false           │
│    then: writer=true; proceed exclusively            │
│                                                      │
│  writeLock.unlock():                                 │
│    writer=false; signal waiting readers/writers      │
│                                                      │
│  T=0: readers=3, writer=false [concurrent reads]    │
│  T=1: writer requests lock → waits (readers=3)      │
│  T=2: readers finish → readers=0                    │
│  T=3: writer proceeds exclusively                   │
│  T=4: writer done → readers allowed again           │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (read-heavy):**
```
1,000 parallel reads arrive:
  → each calls readLock.lock()
        ← YOU ARE HERE (read lock acquired)
  → all 1,000 acquire read lock concurrently
  → all execute getCachedValue() in parallel
  → each calls readLock.unlock()
  → throughput: 1,000× a single-lock approach
```

**WRITE FLOW:**
```
Admin update arrives:
  → writeLock.lock()
  → WAITED for 1,000 current readers to finish
        ← YOU ARE HERE (write lock acquired)
  → no new readers admitted
  → cache value updated
  → writeLock.unlock()
  → all waiting readers now admitted
```

**FAILURE PATH:**
```
Thread holds readLock → tries to upgrade to writeLock
  → writeLock.lock() waits for all readers to release
  → Thread A holds readLock AND waits for writeLock
  → writeLock waits for Thread A's readLock
  → DEADLOCK
Fix: release readLock before acquiring writeLock
     Or: use StampedLock with explicit upgrade path
```

**WHAT CHANGES AT SCALE:**
At 100,000 reads/second with 10 CPU cores, 10 read threads can run in parallel — limited by core count, not lock contention. At 1,000,000 reads/second on 64 cores, the CAS operations on the shared read count become the new bottleneck. `StampedLock` optimistic reads (no CAS for the common case) scale better at this extreme throughput.

---

### 💻 Code Example

**Example 1 — ReentrantReadWriteLock:**
```java
public class CachedConfigStore {
    private final ReadWriteLock rwLock =
        new ReentrantReadWriteLock(true); // fair
    private final Lock readLock  = rwLock.readLock();
    private final Lock writeLock = rwLock.writeLock();
    private final Map<String, String> config =
        new HashMap<>();

    // Concurrent reads — no serialisation between them
    public String get(String key) {
        readLock.lock();
        try {
            return config.get(key);
        } finally {
            readLock.unlock(); // ALWAYS in finally!
        }
    }

    // Exclusive write — waits for all readers
    public void put(String key, String value) {
        writeLock.lock();
        try {
            config.put(key, value);
        } finally {
            writeLock.unlock();
        }
    }

    // Write-to-read downgrade (allowed)
    public String putAndGet(String key, String value) {
        writeLock.lock();
        try {
            config.put(key, value);
            readLock.lock(); // acquire read WHILE holding write
        } finally {
            writeLock.unlock(); // release write (read still held)
        }
        try {
            return config.get(key); // now under read lock only
        } finally {
            readLock.unlock();
        }
    }
}
```

**Example 2 — StampedLock (optimistic read):**
```java
public class OptimisticPriceCache {
    private final StampedLock sl = new StampedLock();
    private double price = 0.0;

    // Optimistic read — NO lock acquisition for common case
    public double getPrice() {
        long stamp = sl.tryOptimisticRead(); // returns stamp
        double p = price;                   // read value

        if (!sl.validate(stamp)) {          // check write happened
            // Writer intervened — fall back to read lock
            stamp = sl.readLock();
            try {
                p = price;
            } finally {
                sl.unlockRead(stamp);
            }
        }
        return p;
    }

    // Exclusive write
    public void setPrice(double newPrice) {
        long stamp = sl.writeLock();
        try {
            price = newPrice;
        } finally {
            sl.unlockWrite(stamp);
        }
    }
}
// Optimistic read path: zero CAS, zero lock — just stamp check
// Fastest possible read path for rare-write scenarios
```

---

### ⚖️ Comparison Table

| Lock Type | Read Concurrency | Write Isolation | Complexity | Best For |
|---|---|---|---|---|
| `synchronized` / Mutex | None (serialised) | Exclusive | Minimal | Simple, any ratio |
| **ReentrantReadWriteLock** | Concurrent | Exclusive | Medium | Read-heavy, 10:1+ ratio |
| StampedLock | Optimistic (no lock) | Exclusive | High | Very read-heavy, low latency |
| ConcurrentHashMap | Segment-level | Segment-level | Zero (built-in) | Hash map specifically |

How to choose: use plain `synchronized` when read:write ratio is low (<5:1). Use `ReentrantReadWriteLock` for read-heavy shared maps/lists (50+:1 ratio). Use `StampedLock` when every nanosecond matters on extremely hot read paths.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Read-Write Lock always outperforms synchronized | Only when reads dominate (>5:1 ratio). At equal reads and writes, the overhead of two lock objects may make it SLOWER than a simple mutex |
| Lock upgrade (read→write) is safe | DEADLOCK. Never hold a read lock and request a write lock. Release the read lock first |
| ReentrantReadWriteLock prevents write starvation | In the default unfair mode, continuous readers can starve writers. Use `new ReentrantReadWriteLock(true)` for fair mode |
| StampedLock is always better than ReentrantReadWriteLock | StampedLock is NOT reentrant and has NO condition variables. Use ReentrantReadWriteLock when reentrancy or conditions are needed |
| Read locks don't need `finally` blocks | Any lock — read or write — MUST be released in a `finally` block. A thrown exception without `finally` leaves the lock permanently held |

---

### 🚨 Failure Modes & Diagnosis

**1. Write Starvation — Writers Blocked Indefinitely**

**Symptom:** Configuration updates (writes) take minutes to apply. Read throughput is fine; writes queue indefinitely.

**Root Cause:** Unfair `ReentrantReadWriteLock` in highly concurrent read environment. New readers continuously acquire read lock before waiting writers, starving writers indefinitely.

**Diagnostic:**
```bash
jstack <PID> | grep -A 10 "writeLock\|WAITING"
# If multiple writer threads stuck in WAITING state for 
# extended time: write starvation confirmed
```

**Fix:**
```java
// Use fair mode to prevent writer starvation
ReadWriteLock fairLock =
    new ReentrantReadWriteLock(true); // fair=true
// Fair: writer in queue → new readers also queue behind it
// Trade-off: slightly lower read throughput
```

**Prevention:** For systems where writes must complete within an SLA, always use fair mode or implement writer-priority using a semaphore.

---

**2. Lock Upgrade Deadlock**

**Symptom:** Two threads hang indefinitely. Thread dump shows both waiting for write lock while holding read lock.

**Root Cause:** Thread A and Thread B each hold a read lock and both attempt to upgrade to write lock. Write lock requires all read locks released. Deadlock: each waits for the other to release their read lock first.

**Diagnostic:**
```bash
jstack <PID> | grep -B 5 "BLOCKED\|WAITING" | grep -A 10 "writeLock"
# Two threads both waiting on write lock while holding read lock
```

**Fix:**
```java
// BAD: read-to-write upgrade attempt
readLock.lock();
try {
    if (needsUpdate()) {
        writeLock.lock(); // DEADLOCK if another reader also tries
    }
} finally { readLock.unlock(); }

// GOOD: release read lock, then acquire write lock
readLock.lock();
try { value = read(); } finally { readLock.unlock(); } // release!
if (needsUpdate()) {
    writeLock.lock();
    try { update(); } finally { writeLock.unlock(); }
}
```

**Prevention:** Architectural rule: never call `writeLock.lock()` while holding `readLock`. Use `StampedLock.tryConvertToWriteLock(stamp)` for atomic upgrade semantics.

---

**3. Missing Finally — Lock Never Released**

**Symptom:** Application gradually hangs. All threads eventually block waiting for a write lock that was acquired but never released.

**Root Cause:** A thread acquired `writeLock.lock()` but threw an exception before the `unlock()` call, and there was no `finally` block.

**Diagnostic:**
```bash
jstack <PID>
# All threads BLOCKED/WAITING on writeLock
# One thread holds writeLock but is no longer running
```

**Fix:**
```java
// ALWAYS wrap lock usage in try/finally
writeLock.lock();
try {
    performUpdate(); // may throw
} finally {
    writeLock.unlock(); // ALWAYS releases, even on exception
}
```

**Prevention:** Sonar rule `java:S2222` (locks must be released in all paths). Code review: every `lock()` must have a corresponding `unlock()` in a `finally` block.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `ReentrantLock` — Read-Write Lock builds on the same `AbstractQueuedSynchronizer` infrastructure; understanding `ReentrantLock` provides the foundation
- `Java Memory Model (JMM)` — lock release → lock acquire establishes happens-before; without JMM understanding, write visibility after lock release is unclear
- `Mutex` — the simpler alternative; Read-Write Lock is a mutex split into two modes; understanding mutex trade-offs justifies the added complexity

**Builds On This (learn these next):**
- `StampedLock` — Java 8+ optimistic read alternative; significantly faster for read-dominant workloads at the cost of API complexity
- `Optimistic Locking (Java)` — similar concept applied to database rows; version-based conflict detection instead of lock-based
- `ConcurrentHashMap` — uses segment-level locks (effectively a built-in read-write lock per bucket); understanding its internals applies Read-Write Lock concepts

**Alternatives / Comparisons:**
- `synchronized` — simpler, fully exclusive; use when write frequency is comparable to read frequency
- `StampedLock` — optimistic reads (no lock acquisition) for the hottest read paths; not reentrant
- `CopyOnWrite collections` — ultimate read optimisation: reads are lock-free; writes create a new copy; only valid for rarely-written, frequently-read collections

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Split lock: concurrent reads, exclusive    │
│              │ writes — readers never block each other   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Exclusive mutex serialises safe-to-        │
│ SOLVES       │ concurrent reads, destroying throughput   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Read:Write ratio drives the benefit;      │
│              │ 50:1+ → significant; 2:1 → negligible     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Shared data read far more than written:   │
│              │ caches, config stores, reference data     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Read:write ratio is low; or writes are    │
│              │ frequent — use simple mutex instead       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Read throughput vs write latency (writers │
│              │ wait for all current readers to finish)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "You may read while others read; you      │
│              │  must own the room to write."             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ StampedLock → ConcurrentHashMap →         │
│              │ Optimistic Locking                        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A `UserSessionCache` uses `ReentrantReadWriteLock` with unfair mode. At 50,000 reads/second from API handlers, a background thread performing periodic session cleanup (write) consistently waits 30+ seconds before acquiring the write lock. The business requirement is: "Session cleanup must complete within 5 seconds." Design a solution using fair-mode locking that guarantees the write lock is acquired within 5 seconds without reducing read throughput by more than 20%.

**Q2.** A developer argues: "For our config cache that is read 100,000 times/second but written only once per hour, `CopyOnWriteArrayList` is better than `ReentrantReadWriteLock` because reads are completely lock-free." Evaluate this claim: identify the one scenario where CopyOnWrite outperforms ReadWriteLock (be specific about the operation), identify the one scenario where ReadWriteLock significantly outperforms CopyOnWrite (be specific about the operation AND the data structure size), and give the precise condition at which one should switch strategies.

