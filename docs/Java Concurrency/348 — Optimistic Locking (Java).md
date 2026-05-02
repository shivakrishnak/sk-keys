---
layout: default
title: "Optimistic Locking (Java)"
parent: "Java Concurrency"
nav_order: 348
permalink: /java-concurrency/optimistic-locking-java/
number: "348"
category: Java Concurrency
difficulty: ★★★
depends_on: CAS (Compare-And-Swap), StampedLock, Atomic Variables, Race Condition, Java Memory Model (JMM)
used_by: StampedLock, Lock-Free Data Structures
tags:
  - java
  - concurrency
  - advanced
  - deep-dive
---

# 348 — Optimistic Locking (Java)

`#java` `#concurrency` `#advanced` `#deep-dive`

⚡ TL;DR — A strategy that reads shared data without locking, then validates no concurrent modification occurred before committing — retrying on conflict rather than waiting.

| #348 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | CAS (Compare-And-Swap), StampedLock, Atomic Variables, Race Condition, Java Memory Model (JMM) | |
| **Used by:** | StampedLock, Lock-Free Data Structures | |

---

### 📘 Textbook Definition

**Optimistic Locking** in Java is a concurrency control pattern that assumes read operations are conflict-free, avoiding lock acquisition during reads. A thread reads shared state and records a version or stamp, performs its computation, then atomically validates that no concurrent writer modified the state during the computation; if validation succeeds, the operation commits; otherwise it retries. In Java, optimistic locking is implemented via `StampedLock.tryOptimisticRead()` for in-memory concurrent data structures, and via `@Version` JPA annotations for database-backed optimistic concurrency.

### 🟢 Simple Definition (Easy)

Optimistic locking reads without locking, checks afterward whether anyone changed the data while reading, and retries if they did — rather than making everyone wait upfront.

### 🔵 Simple Definition (Elaborated)

Pessimistic locking (the default `synchronized` / `ReentrantLock` model) works by grabbing a lock before reading or writing so nobody else can touch the data simultaneously. Optimistic locking flips the assumption: "conflicts are rare — don't lock for reads; just check if anything changed before committing." This works brilliantly when reads vastly outnumber writes and actual conflicts are infrequent. Under high write contention, however, optimistic locking degrades because retries happen frequently, wasting CPU. Java provides optimistic locking natively via `StampedLock.tryOptimisticRead()` and in the JPA/Hibernate layer via `@Version` for database rows.

### 🔩 First Principles Explanation

**Why pessimistic locking is costly for read-heavy workloads:**

A `ReadWriteLock` allows multiple concurrent readers. But acquiring even a read lock involves CAS operations on the lock state, memory barriers, and potential thread suspension. For high-frequency short reads, this overhead dominates.

**Optimistic read — the insight:**

If writes are rare and reads are fast:
1. Read the version/stamp (a number that changes on every write).
2. Read the data.
3. Check: "Is the version/stamp still the same?"
4. If yes → data was consistent during our read → use it.
5. If no → a write happened during our read → retry or fall back to a real lock.

**In-memory optimistic locking with StampedLock:**

```java
StampedLock lock = new StampedLock();
double x, y; // protected fields

double distanceSlow() {
    long stamp = lock.tryOptimisticRead(); // no lock acquired!
    double localX = x;                     // read field
    double localY = y;                     // read field
    if (!lock.validate(stamp)) {           // was there a write?
        // fell through - get real read lock
        stamp = lock.readLock();
        try {
            localX = x;
            localY = y;
        } finally {
            lock.unlockRead(stamp);
        }
    }
    return Math.sqrt(localX * localX + localY * localY);
}
```

`validate(stamp)` checks whether the write count has changed since `tryOptimisticRead()`. If it returns `false`, a concurrent write occurred during our read — data may be inconsistent.

**Key constraint:** Between `tryOptimisticRead()` and `validate()`, you MUST copy shared fields into local variables before using them. Otherwise, the validated-consistent copy is already stale by the time you compute with it.

### ❓ Why Does This Exist (Why Before What)

WITHOUT Optimistic Locking (only pessimistic):

- Every read operation acquires a lock — even when concurrent writes are extremely rare.
- High throughput read-heavy workloads (caches, coordinate systems, counters) degrade due to lock contention overhead.
- Read-heavy path performance bounded by lock acquisition, not by actual computation.

What breaks without it:
1. ReadWriteLock read operations add 100–300ns overhead per read for CAS on lock state.
2. Under thousands of concurrent reader threads, this lock overhead dominates.

WITH Optimistic Locking:
→ Reads require zero CAS operations in the happy path — just a load + validate.
→ 3–5× throughput improvement over ReadWriteLock for read-dominated workloads.
→ Falls back to a real lock only on actual write conflicts.

### 🧠 Mental Model / Analogy

> Imagine a shared whiteboard in an office where people rarely erase it. Pessimistic approach: every person who wants to read takes a "reading token" from a token dispenser (acquires readLock), reads, returns the token. Optimistic approach: just read the number at the top of the whiteboard (version), read the content, then glance back at the number (validate). If the number changed while you were reading, someone erased and rewrote — re-read. If not, your read was consistent.

"Number at top of whiteboard" = stamp/version, "glancing back" = validate(), "someone erased and rewrote" = concurrent write, "re-read" = retry.

The optimistic approach only needs the "re-read" protocol when an erase actually happened — which is rare.

### ⚙️ How It Works (Mechanism)

**StampedLock optimistic read protocol:**

```
tryOptimisticRead():
  1. Read current write stamp (version counter)
  2. Return stamp; no lock acquired if no active write

[read shared fields into local copies]

validate(stamp):
  1. Check: current write stamp == original stamp?
  2. True  → no write occurred → data is consistent
  3. False → write occurred during read → retry needed
```

**StampedLock write path:**
```
writeLock():
  1. Acquire exclusive lock (blocks readers + writers)
  2. Increment the write stamp (invalidates all optimistic stamps)
  3. Perform write
unlockWrite(stamp):
  4. Release, stamp now changes → all validate() calls return false
```

**Read strategy cascade:**

```
tryOptimisticRead() → fast path (no lock)
       ↓ if validate() fails
readLock() → shared lock (allows other readers)
       ↓ if write-heavy (high contention)
writeLock() → exclusive lock (only when writing)
```

### 🔄 How It Connects (Mini-Map)

```
synchronized / ReentrantLock (pessimistic, exclusive)
           ↓ evolution
ReadWriteLock (pessimistic, read-shared)
           ↓ evolution
StampedLock tryOptimisticRead ← you are here
           ↓ foundation
CAS (Compare-And-Swap) → Atomic Variables
           ↓
Lock-Free Data Structures
```

### 💻 Code Example

Example 1 — StampedLock with optimistic read:

```java
import java.util.concurrent.locks.StampedLock;

public class Point {
    private double x, y;
    private final StampedLock lock = new StampedLock();

    public void move(double deltaX, double deltaY) {
        long stamp = lock.writeLock();
        try {
            x += deltaX;
            y += deltaY;
        } finally {
            lock.unlockWrite(stamp);
        }
    }

    public double distance() {
        // Optimistic read — no lock acquired
        long stamp = lock.tryOptimisticRead();
        double localX = x; // copy to local!
        double localY = y; // copy to local!

        if (!lock.validate(stamp)) {
            // Write occurred during read; fall back to read lock
            stamp = lock.readLock();
            try {
                localX = x;
                localY = y;
            } finally {
                lock.unlockRead(stamp);
            }
        }
        // Use LOCAL copies (not x, y directly — stale!)
        return Math.sqrt(localX * localX + localY * localY);
    }
}
```

Example 2 — Database optimistic locking with JPA @Version:

```java
@Entity
public class Product {
    @Id
    private Long id;
    private int stock;

    @Version  // JPA-managed version column
    private Long version;
}

// In service:
@Transactional
public void decrementStock(Long productId) {
    Product p = repo.findById(productId).orElseThrow();
    p.setStock(p.getStock() - 1);
    // JPA generates: UPDATE product SET stock=?, version=version+1
    //                WHERE id=? AND version=?
    // If version mismatch → OptimisticLockException thrown
}
// Caller retries on OptimisticLockException
```

Example 3 — Wrong pattern: using shared fields after validate():

```java
// BAD: Reading x,y after validate() — they may have changed!
long stamp = lock.tryOptimisticRead();
if (lock.validate(stamp)) {
    return Math.sqrt(x * x + y * y); // x,y accessed AFTER validate
    // validate() was true at that instant but x,y may change
    // between validate() return and x,y reads!
}

// GOOD: Copy to locals BEFORE validate()
long stamp = lock.tryOptimisticRead();
double lx = x; // local copy taken BEFORE validate
double ly = y; // local copy taken BEFORE validate
if (!lock.validate(stamp)) { /* retry */ }
return Math.sqrt(lx * lx + ly * ly); // use LOCAL copies
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Optimistic locking is always faster than pessimistic locking | Under high write contention, optimistic locking degrades due to frequent retries; pessimistic locking can be more efficient when conflicts are common. |
| validate() returning true means the data is entirely consistent | validate() confirms no write occurred between tryOptimisticRead() and validate(), but only if shared fields were read to locals BEFORE validate(). Reading fields AFTER validate() is a race condition. |
| Optimistic locking eliminates the need for any locks | Writes still require exclusive locks; optimistic locking only eliminates read locks on the happy read path. |
| StampedLock is a drop-in replacement for ReentrantReadWriteLock | StampedLock is non-reentrant and non-condition-variable; migrating from RRWL requires care. |
| @Version in JPA works the same as StampedLock | @Version is database-level optimistic locking; StampedLock is in-memory. They solve the same conceptual problem at different layers. |

### 🔥 Pitfalls in Production

**1. Accessing Shared Fields After validate() — Data Race**

```java
// BAD: Classic mistake — fields read AFTER validate
long stamp = lock.tryOptimisticRead();
if (lock.validate(stamp)) {
    return x + y; // x, y read AFTER validate → race condition!
}

// GOOD: Always copy to locals first
long stamp = lock.tryOptimisticRead();
double lx = x; double ly = y; // copy BEFORE validate
if (!lock.validate(stamp)) { /* fallback */ }
return lx + ly; // use locals only
```

**2. Infinite Retry Loop Under Write Starvation**

```java
// BAD: No bound on retry count under heavy write contention
double result;
while (true) {
    long stamp = lock.tryOptimisticRead();
    result = expensive_computation(x, y);
    if (lock.validate(stamp)) break;
    // Under constant writes: retries forever, CPU spins
}

// GOOD: Bound retries, then fall back to read lock
long stamp = lock.tryOptimisticRead();
double lx = x, ly = y;
if (!lock.validate(stamp)) {
    stamp = lock.readLock(); // fall through to pessimistic
    try { lx = x; ly = y; } finally { lock.unlockRead(stamp); }
}
```

**3. Non-Reentrant StampedLock Causing Deadlock**

```java
// BAD: StampedLock is NOT reentrant
// Acquiring writeLock twice from same thread → deadlock
long stamp1 = lock.writeLock();
long stamp2 = lock.writeLock(); // DEADLOCK — same thread!

// GOOD: restructure code to avoid nested lock acquisition
// or use ReentrantReadWriteLock if reentrancy is needed
```

### 🔗 Related Keywords

- `CAS (Compare-And-Swap)` — the hardware primitive enabling optimistic validation.
- `StampedLock` — Java's built-in optimistic locking mechanism for in-memory state.
- `ReentrantLock` — the pessimistic alternative; simpler, reentrant, higher overhead for reads.
- `Lock-Free Data Structures` — extend optimistic principles to full data structure operations.
- `Race Condition` — the problem optimistic locking detects and retries on.
- `Java Memory Model (JMM)` — validate() includes a full memory barrier.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Read without lock; validate consistency;  │
│              │ retry on conflict. Fast when writes rare. │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Read-heavy: >95% reads, rare writes;      │
│              │ StampedLock for in-memory; @Version for DB│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Write-heavy or high contention — retries  │
│              │ waste more CPU than locking would cost.   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Optimist reads first, apologises later;  │
│              │ pessimist asks permission before looking."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ StampedLock → VarHandle → Lock-Free DS    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A read-heavy counter service uses `StampedLock.tryOptimisticRead()`. During load testing with 95% reads and 5% writes, mean read latency is 50ns (excellent). But at P99.9, latency spikes to 50μs. What is the mechanism causing this spike, why is it specifically at high percentiles rather than the mean, and what would you change in the lock strategy to flatten this distribution?

**Q2.** `validate(stamp)` in StampedLock includes a full memory barrier. Explain why this memory barrier is necessary for correctness — specifically, what memory visibility guarantee it provides that would be absent without it, and what category of bugs could occur in a JVM with relaxed memory ordering if validate() did not include the barrier.

