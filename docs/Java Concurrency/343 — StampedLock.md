---
layout: default
title: "StampedLock"
parent: "Java Concurrency"
nav_order: 343
permalink: /java-concurrency/stamped-lock/
number: "0343"
category: Java Concurrency
difficulty: ★★★
depends_on: ReadWriteLock, ReentrantLock, Memory Barrier
used_by: Cache implementations, High-throughput reads
related: ReadWriteLock, ReentrantLock, volatile
tags:
  - java
  - concurrency
  - locking
  - deep-dive
  - performance
---

# 0343 — StampedLock

⚡ TL;DR — `StampedLock` extends read-write locking with an **optimistic read** mode that reads without acquiring any lock and validates afterward — providing near-zero-overhead reads when writes are infrequent, at the cost of non-reentrancy and complex validation logic.

| #0343 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ReadWriteLock, ReentrantLock, Memory Barrier | |
| **Used by:** | Cache implementations, High-throughput reads | |
| **Related:** | ReadWriteLock, ReentrantLock, volatile | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Even with `ReadWriteLock`, acquiring a read lock requires a CAS operation and memory barriers, tracking hold counts, and unblocking writers later. For a hot-path method called 10M times/second that reads two fields atomically, even the cheapest read lock adds ~50ns overhead per call = 500ms/second of pure lock overhead.

THE BREAKING POINT:
A geometry service reads `Point.x` and `Point.y` 50M times/second for distance calculations. With `ReentrantReadWriteLock`, even in uncontended mode (no writes in flight), the read lock acquire + release adds ~20ns × 50M = 1 second/second overhead. The service spends 100% CPU on lock management for reads that almost never conflict with writes.

THE INVENTION MOMENT:
This is exactly why **`StampedLock`** was created — its optimistic read mode reads without any lock, then validates that no write occurred. For low-write-frequency workloads, validation almost always succeeds, giving reads at ~1ns overhead vs. ~20ns for a full read lock.

### 📘 Textbook Definition

**`StampedLock`** is a non-reentrant lock introduced in Java 8 (Doug Lea) providing three modes: (1) **Write lock** (`writeLock()`) — exclusive, returns a stamp; (2) **Read lock** (`readLock()`) — shared, returns a stamp; (3) **Optimistic read** (`tryOptimisticRead()`) — not a lock at all, returns a stamp representing current lock state. After reading, `validate(stamp)` checks if a write occurred since the stamp was obtained. If validation fails, retry with a full read lock. All modes return a `long` stamp; 0 means acquisition failed. Stamps contain lock state information — not just a counter. **Not reentrant** — re-acquiring the same lock type deadlocks.

### ⏱️ Understand It in 30 Seconds

**One line:**
`StampedLock` reads without locking, then checks "did a write happen during my read?" — retrying only on the rare write-during-read case.

**One analogy:**
> Reading a shared whiteboard without getting a key: you glance at the whiteboard (optimistic read), read the data, then look at the timestamp (`validate`) to check if anyone erased and rewrote while you were reading. If yes, you read again with the key (full read lock). If no — common case — you saved the overhead of getting the key entirely.

**One insight:**
Optimistic reads are not locks — they can be used concurrently with writers. The guarantee is: if `validate(stamp)` returns true after reading, then the data was not modified during the read, and the read is consistent. The key is: reads may observe partially-updated data, and `validate` is the consistency checkpoint.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Optimistic read stamp is obtained without blocking; a write may be in progress during the optimistic read.
2. `validate(stamp)` returns `true` only if no write-lock was acquired since the stamp was issued.
3. If `validate` fails, the data may be partially updated — must retry (typically with a full read lock).

DERIVED DESIGN:
The stamp encodes the write version counter. Each write increments the counter. `validate(stamp)` checks if the counter changed. If unchanged, no write occurred — optimistic read is valid.

```
StampedLock State:
  stamp = (writeCount << 7) | readers_present_bit

  tryOptimisticRead():
    stamp = readLockBit=0, no lock acquired
  
  validate(stamp):
    return (state & WRITE_BIT_MASK) == (stamp & WRITE_BIT_MASK)
    // True if writeCount unchanged since stamp
  
  writeLock():
    stamp = increment writeCount, exclusive
  
  unlock(stamp):
    restore state using stamp's version info
```

THE TRADE-OFFS:
Gain: Optimistic reads add ~1-2ns vs ~20ns for read lock; no writer starvation; better throughput for read-dominant workloads.
Cost: Non-reentrant (re-acquiring deadlocks); more complex code (must handle validation failure); partial reads require loop; cannot use with `try/finally` safety pattern (must pass stamp to unlock); not a `Lock` interface implementor.

### 🧪 Thought Experiment

SETUP:
Geometric Point with x and y, read millions of times/second.

WITH ReentrantReadWriteLock:
```java
readLock.lock();
try { return Math.sqrt(x*x + y*y); }
finally { readLock.unlock(); }
// Cost: ~20ns per call for lock overhead
// 50M reads/sec → 1 SECOND of overhead per second
```

WITH StampedLock optimistic read:
```java
long stamp = lock.tryOptimisticRead();
double localX = x, localY = y;
if (!lock.validate(stamp)) {
    stamp = lock.readLock();
    try { localX = x; localY = y; }
    finally { lock.unlockRead(stamp); }
}
return Math.sqrt(localX*localX + localY*localY);
// Cost: ~2ns when no writer (99.9% case)
// Fallback to read lock only when writer active (0.1% case)
```

THE INSIGHT:
For a workload with 50M reads/second and 1 write/minute, the optimistic read succeeds 99.9999% of the time. Lock overhead drops from 1s/second to 0.1ms/second — a 10,000× improvement.

### 🧠 Mental Model / Analogy

> Taking a photo of a scoreboard vs. getting an official stat printout. You snap a photo (optimistic read), note the game clock (stamp). After looking at your photo, you check if the game clock changed since you snapped (validate). If yes, the scoreboard may have changed — you wait for the official printout (read lock). If no, your photo is accurate facts for that moment.

"Snapping a photo" → `tryOptimisticRead()` + read variables.
"Checking game clock" → `validate(stamp)`.
"Game clock changed" → validate fails → data inconsistent.
"Official printout" → fallback to read lock.

Where this analogy breaks down: A photo captures a moment atomically. Optimistic read captures variables sequentially — if a write interleaves between two field reads, `x` is from before the write and `y` is from after. `validate(stamp)` detects this and triggers retry.

### 📶 Gradual Depth — Four Levels

**Level 1:** `StampedLock` reads data without locking, then does a quick "did anything change?" check. If yes, re-reads with a lock. If no, done — saved the overhead of the lock entirely.

**Level 2:** Three modes: `tryOptimisticRead()` + `validate(stamp)` for reads without locks; `readLock()` for guaranteed read; `writeLock()` for exclusive write. Always use the stamp returned to identify which lock to release. Unlike `ReentrantLock`, this is NOT a `try/finally lock.unlock()` pattern — you pass the stamp to `unlockRead(stamp)`.

**Level 3:** Optimistic reads are implemented as a versioned write counter in the lock state. Each write increments the version. `validate(stamp)` checks that the version hasn't changed. The optimistic read does a load-acquire barrier at `validate()` to ensure freshness of the read variables. The JIT can often eliminate the barrier on x86 TSO (where loads are already acquire-reads).

**Level 4:** `StampedLock` is not a `Lock` interface implementation — it's a different paradigm. It supports lock conversion: `tryConvertToWriteLock(stamp)` and `tryConvertToReadLock(stamp)` allow conditional mode upgrade. It's non-reentrant by design — simpler state management enables the stamp-based version tracking. Reentrancy would require per-thread tracking that would add overhead negating the optimistic read benefit.

### ⚙️ How It Works (Mechanism)

**Optimistic read pattern:**
```java
StampedLock sl = new StampedLock();
double x, y; // shared fields

double distanceFromOrigin() {
    // Try optimistic read first (NO lock acquired)
    long stamp = sl.tryOptimisticRead();
    double localX = x, localY = y; // may be inconsistent!
    
    if (!sl.validate(stamp)) {
        // Optimistic read failed (write was in progress)
        stamp = sl.readLock(); // full read lock
        try { localX = x; localY = y; } // consistent read
        finally { sl.unlockRead(stamp); }
    }
    // Either path: localX and localY are consistent
    return Math.sqrt(localX * localX + localY * localY);
}

void updatePosition(double newX, double newY) {
    long stamp = sl.writeLock(); // exclusive write
    try { x = newX; y = newY; }
    finally { sl.unlockWrite(stamp); }
}
```

**Lock conversion (optimistic → read lock):**
```java
long stamp = sl.tryOptimisticRead();
double localX = x;
// Instead of validate+readLock, convert directly:
stamp = sl.tryConvertToReadLock(stamp);
if (stamp == 0) {
    // Conversion failed — must try read lock
    stamp = sl.readLock();
}
try {
    double localY = y; // safe under read lock
    return compute(localX, localY);
} finally {
    sl.unlock(stamp);
}
```

**Write lock (same as ReentrantReadWriteLock write):**
```java
long stamp = sl.writeLock();
try {
    updateState();
} finally {
    sl.unlockWrite(stamp);
}
```

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW (no concurrent write):
```
[tryOptimisticRead() — no lock, returns stamp S]  ← YOU ARE HERE
    → [Read x, y variables (may be in CPU cache)]
    → [validate(S): writeCount unchanged?]
    → [YES: data consistent — proceed]
    → [compute and return — ~2ns total]
```

FAILURE PATH (concurrent write):
```
[tryOptimisticRead() — returns stamp S]
    → [Write begins concurrently: x updated]
    → [Read y — inconsistent with new x]
    → [validate(S): writeCount changed]
    → [NO: data inconsistent]
    → [Fallback: readLock() — blocks until write done]
    → [Re-read x, y consistently]
    → [unlockRead(newStamp)]
```

WHAT CHANGES AT SCALE:
At scale, StampedLock's advantage compounds: for a 10M read/second workload with rare writes, optimistic reads save the equivalent of a full CPU core vs. `ReentrantReadWriteLock`. For Geospatial services, financial tick data, and sensor data reading — patterns with millions of reads and seconds between writes — StampedLock is the correct choice. However, its non-reentrancy and stamp-based API are error-prone at scale; extensive testing of the retry logic is critical.

### 💻 Code Example

Example 1 — Point class with StampedLock:
```java
class Point {
    private double x, y;
    private final StampedLock sl = new StampedLock();

    void move(double deltaX, double deltaY) {
        long stamp = sl.writeLock();
        try { x += deltaX; y += deltaY; }
        finally { sl.unlockWrite(stamp); }
    }

    double distanceFromOrigin() {
        long stamp = sl.tryOptimisticRead();
        double lx = x, ly = y;
        if (!sl.validate(stamp)) {
            stamp = sl.readLock();
            try { lx = x; ly = y; }
            finally { sl.unlockRead(stamp); }
        }
        return Math.hypot(lx, ly);
    }
}
```

Example 2 — Choosing between lock types at runtime:
```java
// Read a value, update if below threshold
double updateIfNeeded(double threshold) {
    long stamp = sl.tryOptimisticRead();
    double current = value;
    if (!sl.validate(stamp)) {
        stamp = sl.readLock();
        try { current = value; }
        finally { sl.unlockRead(stamp); }
    }
    if (current < threshold) {
        // Need write — tryConvert or release + reacquire
        long writeStamp = sl.tryConvertToWriteLock(stamp);
        if (writeStamp == 0) {
            writeStamp = sl.writeLock(); // couldn't convert
        }
        try { value = threshold; }
        finally { sl.unlockWrite(writeStamp); }
    }
    return current;
}
```

### ⚖️ Comparison Table

| Lock | Read Cost | Write Cost | Reentrant | Optimistic | Starvation |
|---|---|---|---|---|---|
| `synchronized` | Medium | Medium | Yes | No | Possible |
| `ReentrantLock` | Medium | Medium | Yes | No | Possible |
| `ReadWriteLock` | Low-Medium | Medium | Yes | No | Write possible |
| **`StampedLock`** | Very Low (optimistic) | Medium | **No** | Yes | Minimal |

How to choose: Use `StampedLock` when: reads >> writes, read performance is critical, and you can accept non-reentrancy. For all other cases, `ReentrantReadWriteLock` is simpler and safer. Never use `StampedLock` when the code path could re-acquire the same lock.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| optimistic read is lock-free and always safe | It's lock-free but NOT always safe — reads may see inconsistent state during a write. `validate()` detects this. Forging to validate and proceeding with inconsistent data causes subtle bugs |
| StampedLock is strictly better than ReadWriteLock | StampedLock is NOT reentrant. Any code that re-calls a StampedLock-protected method recursively will deadlock. ReadWriteLock is reentrant — simpler and safer for most code |
| validate() succeeding means a consistent read | `validate()` means no write COMPLETED during your read. A write that started and finished between your individual field reads is detected by `validate`. But complex reads with intervening computation may still observe inconsistency if your fields are logically interdependent — always copy fields to locals before compute |
| You can ignore the stamp for unlocking | The stamp encodes version info used to unlock correctly. Discarding the stamp and using a hardcoded value for `unlockWrite`/`unlockRead` will corrupt the lock state |

### 🚨 Failure Modes & Diagnosis

**Deadlock from Reentrant Acquisition**

Symptom: Thread permanently WAITING after calling a method that re-acquires StampedLock.

Root Cause: StampedLock is NOT reentrant. Acquiring write lock while already holding write lock deadlocks.

Fix:
```java
// BAD: reentrant StampedLock acquisition
long stamp = sl.writeLock();
try {
    updateA();
    updateB(); // updateB() also calls sl.writeLock() → DEADLOCK
} finally { sl.unlockWrite(stamp); }

// GOOD: refactor to not call locked methods recursively
long stamp = sl.writeLock();
try { doUpdateA(); doUpdateB(); } // both inline, one lock
finally { sl.unlockWrite(stamp); }
```

Prevention: Audit ALL call chains for StampedLock usages. Prefer `ReentrantReadWriteLock` when reentrancy cannot be guaranteed.

---

**Inconsistent Read from Missing Validation**

Symptom: Intermittent wrong calculations; hard to reproduce; only occurs under write load.

Root Cause: Optimistic read without `validate()` — using potentially inconsistent data.

Fix: Always call `validate(stamp)` after reading in optimistic mode and retry with a full read lock on failure.

**Stamp Invalidation from Non-local Storage**

Symptom: `IllegalArgumentException` or corrupted lock state on `unlockWrite(stamp)`.

Root Cause: Stamp was obtained in a different context (e.g., different thread, stored stale stamp).

Fix: Never cache, share, or store stamps across threads or across lock acquisition cycles. Stamps are single-use.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `ReadWriteLock` — StampedLock extends read-write locking with optimistic reads; ReadWriteLock is prerequisite
- `Memory Barrier` — optimistic read's `validate()` uses memory barriers for correctness

**Builds On This (learn these next):**
- Cache implementations — StampedLock is most valuable for cache data structures with high read frequency

**Alternatives / Comparisons:**
- `ReadWriteLock` — simpler, reentrant, less performant for very high-read workloads
- `volatile` — single-field visibility without locks; even simpler than stamped for individual fields

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Lock with optimistic read mode: read      │
│              │ without locking, validate afterward       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Even uncontended read locks add ~20ns;    │
│ SOLVES       │ for millions of reads, adds up fast       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ NOT REENTRANT — re-acquiring deadlocks.   │
│              │ MUST validate after optimistic read.      │
│              │ Only wins when reads >> writes.           │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Millions of reads/sec, rare writes;       │
│              │ read performance is measurably critical   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Reentrant code paths; balanced IO;        │
│              │ maintenance simplicity is priority        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Near-zero read overhead vs non-reentrancy │
│              │ and complex validation retry logic        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Read first, then ask 'was it modified?'  │
│              │  — only block when the answer is yes"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ConcurrentHashMap → LockSupport →         │
│              │ AbstractQueuedSynchronizer                │
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** The `distanceFromOrigin()` example reads `x` and `y` separately in the optimistic read section. Between reading `x` and reading `y`, a writer calls `move(3.0, 4.0)`, updating both. After the write, `validate(stamp)` returns false. But what if the write updates ONLY `y` (not x) — and the programmer forgot to include `x` in the "moved" operation? Trace whether `validate(stamp)` still saves the programmer from seeing an inconsistent state, explain exactly what `validate()` checks vs. what it does NOT check, and describe a scenario where the validation succeeds (returns true) but the data is still logically inconsistent for the computation.

**Q2.** `StampedLock.tryConvertToWriteLock(readStamp)` allows converting a read lock to a write lock atomically. Explain why this operation exists but `ReentrantReadWriteLock` doesn't support the equivalent: at the AQS level, what specific state transition would be required for a read→write upgrade in `ReentrantReadWriteLock`, why that transition cannot be performed atomically when multiple readers hold the lock, and why `StampedLock` CAN offer this conversion with a clear failure path (returning 0) instead of deadlocking.

