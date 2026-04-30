---
layout: default
title: "StampedLock"
parent: "Java Concurrency"
nav_order: 343
permalink: /java-concurrency/stampedlock/
number: "343"
category: Java Concurrency
difficulty: ★★★
depends_on: ReadWriteLock, ReentrantLock, volatile, CAS
used_by: High-throughput Read-Heavy Structures, Optimistic Reads
tags: #java, #java8, #concurrency, #locks, #optimistic, #performance
---

# 343 — StampedLock

`#java` `#java8` `#concurrency` `#locks` `#optimistic` `#performance`

⚡ TL;DR — StampedLock is Java 8's highest-throughput lock for read-heavy workloads, adding an **optimistic read** mode that requires no lock acquisition at all — just validate the stamp after the read; only upgrade to a real lock on conflict.

| #343 | category: Java Concurrency
|:---|:---|:---|
| **Depends on:** | ReadWriteLock, ReentrantLock, volatile, CAS | |
| **Used by:** | High-throughput Read-Heavy Structures, Optimistic Reads | |

---

### 📘 Textbook Definition

`java.util.concurrent.locks.StampedLock` (Java 8) provides three locking modes, each returning a **stamp** (long) used to unlock or validate: (1) **Write lock** — exclusive, like `ReentrantReadWriteLock.writeLock()`; (2) **Read lock** — shared, like `ReentrantReadWriteLock.readLock()`; (3) **Optimistic read** — a non-locking read that returns a stamp; you read the data and then call `validate(stamp)` — if true, no writer interfered; if false, fall back to a real read lock. StampedLock is **non-reentrant** and does not support `Condition` objects.

---

### 🟢 Simple Definition (Easy)

`ReadWriteLock` makes readers wait while a writer works. `StampedLock` adds a shortcut: optimistic reads don't wait at all. You note the current "version" (stamp), read the data, then check "did the version change?" If not — you got a clean read with zero locking. If a write sneaked in — fall back to a real read lock. Most of the time, reads succeed optimistically.

---

### 🔵 Simple Definition (Elaborated)

Optimistic concurrency is common in databases (MVCC, optimistic locking). StampedLock brings it to in-memory Java. The logic: "I'll assume nobody is writing right now. I'll read without locking. Afterward, I'll check if my assumption was correct. If wrong, I retry with a real lock." For read-heavy structures with rare writes, optimistic reads eliminate all lock overhead — threads never block each other for reads. The trade-off: extra validation step after every read + must copy fields out before validating.

---

### 🔩 First Principles Explanation

```
ReadWriteLock read path:
  acquire read lock (CAS on lock state)
  read data
  release read lock
  → Even reads require two CAS operations

StampedLock optimistic read path:
  stamp = tryOptimisticRead()   // reads volatile lock state — single read
  x = point.x; y = point.y;    // read data (no lock)
  if (!validate(stamp)) {       // check: did state change?
    // write occurred → retry with real read lock
    stamp = readLock();
    try { x = point.x; y = point.y; }
    finally { unlockRead(stamp); }
  }
  // Use x, y → guaranteed consistent if validate passed

Throughput improvement:
  ReadWriteLock: read = 2 CAS + memory barriers
  StampedLock optimistic: 2 volatile reads (validate = single read)
  → ~3-5× higher throughput for read-heavy, rarely-written data
```

---

### 🧠 Mental Model / Analogy

> A museum exhibit with a "do not touch" sign. Optimistic: you glance at the exhibit (read data), then check the sign hasn't been replaced (validate stamp). If the sign is unchanged — your glance was accurate. If a curator swapped exhibits while you were looking (write happened) — you go back and look again properly (real read lock). Most visitors never had a problem — the optimistic approach is almost always free.

---

### ⚙️ How It Works

```
Three modes:
  writeLock() / unlockWrite(stamp)     → exclusive, blocks all
  readLock()  / unlockRead(stamp)      → shared, blocks writers (like RWLock)
  tryOptimisticRead()                  → no lock; returns stamp or 0 if write locked

  validate(stamp)  → returns true if no write occurred since stamp was obtained
  isWriteLocked()  → check state
  isReadLocked()   → check state

IMPORTANT rules:
  1. Never use references obtained during optimistic read after validate fails
  2. Copy primitive values out before validating (if validate fails, values are inconsistent)
  3. StampedLock is NON-REENTRANT — calling writeLock() while holding it = deadlock
  4. No Condition support (use ReentrantLock if Conditions needed)

Lock conversions:
  tryConvertToWriteLock(stamp)   → convert readLock → writeLock (if no other readers)
  tryConvertToReadLock(stamp)    → convert writeLock → readLock (downgrade)
  tryConvertToOptimisticRead(stamp) → if only reader, convert to optimistic
```

---

### 🔄 How It Connects

```
StampedLock (Java 8)
  │
  ├─ Write lock   → equivalent to ReentrantReadWriteLock.writeLock
  ├─ Read lock    → equivalent to ReentrantReadWriteLock.readLock
  ├─ Optimistic   → NO equivalent in ReadWriteLock; unique to StampedLock
  │
  ├─ vs ReadWriteLock  → StampedLock higher throughput; but non-reentrant, no Condition
  ├─ vs ReentrantLock  → StampedLock better for read-heavy; RL has Condition support
  └─ vs Atomic         → Atomic ops are lock-free for single values; StampedLock for compound reads
```

---

### 💻 Code Example

```java
// Classic StampedLock pattern: optimistic read with fallback
public class Point {
    private double x, y;
    private final StampedLock lock = new StampedLock();

    // Write: exclusive
    public void move(double deltaX, double deltaY) {
        long stamp = lock.writeLock();
        try {
            x += deltaX;
            y += deltaY;
        } finally {
            lock.unlockWrite(stamp);
        }
    }

    // Optimistic read — the StampedLock idiom
    public double distanceFromOrigin() {
        long stamp = lock.tryOptimisticRead();   // no lock acquired
        double cx = x, cy = y;                  // copy fields out

        if (!lock.validate(stamp)) {             // check: was a write in progress?
            // Optimistic read failed — fall back to real read lock
            stamp = lock.readLock();
            try {
                cx = x; cy = y;
            } finally {
                lock.unlockRead(stamp);
            }
        }
        return Math.sqrt(cx * cx + cy * cy);     // use local copies
    }
}
```

```java
// Convert readLock to writeLock atomically (if possible)
long stamp = lock.readLock();
try {
    while (value < target) {
        long writeStamp = lock.tryConvertToWriteLock(stamp);
        if (writeStamp != 0L) {
            stamp = writeStamp;
            value++;   // now holding write lock
            break;
        } else {
            // Couldn't upgrade (other readers) → release read, acquire write
            lock.unlockRead(stamp);
            stamp = lock.writeLock();
        }
    }
} finally {
    lock.unlock(stamp);  // works for both read and write stamps
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Optimistic read is lock-free for the writer too | Writer still acquires exclusive write lock; optimistic READER avoids locking, not writer |
| validate() being true means data is 100% consistent | True — validate() confirms no write occurred between tryOptimisticRead() and validate() |
| StampedLock can replace ReentrantLock everywhere | StampedLock is non-reentrant and has no Condition — can't replace RL for those features |
| StampedLock prevents starvation | Like RWLock, writers can starve; additionally, has no fairness mode |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Using object references from failed optimistic read**

```java
// ❌ If validate() returns false, cx may be inconsistent
long stamp = lock.tryOptimisticRead();
String name = object.getName();          // could be partially written!
if (!lock.validate(stamp)) { /* handle */ }
// Bad: still using 'name' which may be from a torn write

// ✅ Re-read inside the fallback:
long stamp = lock.tryOptimisticRead();
String name = object.getName();
if (!lock.validate(stamp)) {
    stamp = lock.readLock();
    try { name = object.getName(); }  // safe re-read with real lock
    finally { lock.unlockRead(stamp); }
}
```

**Pitfall 2: Re-entrance deadlock (StampedLock is non-reentrant)**

```java
// ❌ Deadlock: same thread tries to acquire writeLock it already holds
long stamp = lock.writeLock();
helperMethod();      // helperMethod() also calls lock.writeLock() → deadlock!

// Fix: pass stamp to helpers, or use ReentrantLock if re-entrance is needed
```

---

### 🔗 Related Keywords

- **[ReadWriteLock](./083 — ReadWriteLock.md)** — simpler predecessor; supports Conditions
- **[ReentrantLock](./076 — ReentrantLock.md)** — reentrant, has Conditions
- **[volatile](./070 — volatile.md)** — optimistic reads use volatile internally for stamp
- **[ConcurrentHashMap](./082 — ConcurrentHashMap.md)** — uses similar optimistic strategies internally

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Optimistic read: no lock, just validate stamp │
│              │ after — highest read throughput when writes  │
│              │ are rare; non-reentrant; no Conditions       │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Read:write >> 10:1; hot-path fields read by  │
│              │ many threads; want to eliminate read contention│
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Need re-entrance; need Conditions; read:write │
│              │ is near 1:1 (optimistic overhead outweighs)  │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Read without locking; check after —         │
│              │  only retry if a write sneaked in"           │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ ReadWriteLock → ReentrantLock → Conditions → │
│              │ ConcurrentHashMap → lock-free algorithms     │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** In the optimistic read pattern, you copy `x` and `y` to local variables before calling `validate()`. Why must you copy to LOCAL variables rather than using the fields directly after a successful validation?

**Q2.** When `tryOptimisticRead()` returns `0L`, what does that indicate? What should your code do in that case?

**Q3.** StampedLock is non-reentrant. Design a scenario in a codebase where a developer accidentally causes a deadlock by treating it like a reentrant lock. How would you detect this at runtime?

