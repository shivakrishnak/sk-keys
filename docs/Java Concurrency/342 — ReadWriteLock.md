---
layout: default
title: "ReadWriteLock"
parent: "Java Concurrency"
nav_order: 83
permalink: /java-concurrency/readwritelock/
number: "083"
category: Java Concurrency
difficulty: ★★★
depends_on: ReentrantLock, synchronized, Race Condition
used_by: Read-Heavy Caches, Configuration Stores, Reference Data
tags: #java, #concurrency, #locks, #read-write, #performance
---

# 083 — ReadWriteLock

`#java` `#concurrency` `#locks` `#read-write` `#performance`

⚡ TL;DR — ReadWriteLock allows unlimited concurrent readers OR exactly one writer (never both) — maximising throughput for read-heavy workloads where writes are rare and reads dominate.

| #083 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ReentrantLock, synchronized, Race Condition | |
| **Used by:** | Read-Heavy Caches, Configuration Stores, Reference Data | |

---

### 📘 Textbook Definition

`java.util.concurrent.locks.ReadWriteLock` is an interface with two associated locks: a **read lock** (`readLock()`) that allows concurrent acquisition by multiple threads, and a **write lock** (`writeLock()`) that allows exclusive acquisition by a single thread. The read lock can be held by any number of threads simultaneously as long as no thread holds the write lock. The write lock is exclusive — no other thread may hold the read lock or write lock while one thread holds the write lock. `ReentrantReadWriteLock` is the standard implementation, with optional fairness.

---

### 🟢 Simple Definition (Easy)

A library reading room: unlimited people can read books simultaneously (read lock). But when the librarian needs to reorganise the shelves (write lock), everyone must leave and nobody new can enter until reorganisation is done. Reads never block each other — only writes block reads (and vice versa).

---

### 🔵 Simple Definition (Elaborated)

Most real-world data is read far more often than written. A config store might be read 10,000 times per second and written once per minute. Using `synchronized` or `ReentrantLock` means ALL 10,000 reads serialise — only one at a time — even though concurrent reads are perfectly safe. ReadWriteLock solves this: all reads proceed concurrently; writes get exclusive access. The gain is proportional to your read:write ratio.

---

### 🔩 First Principles Explanation

```
synchronized / ReentrantLock:
  ANY access (read or write) → mutually exclusive
  10,000 reads/sec → all serialised → throughput bottleneck

ReadWriteLock rules:
  Read lock:  Multiple threads can hold simultaneously
              UNLESS a write lock is held
  Write lock: ONLY one thread can hold
              No read OR write lock may be held by others

State machine:
  No locks held       → read lock: ✅ any threads  │ write lock: ✅ one thread
  Read locks held (N) → read lock: ✅ more readers  │ write lock: ❌ blocked
  Write lock held     → read lock: ❌ blocked        │ write lock: ❌ blocked

Benefit formula:
  If reads:writes = 100:1 and read time ≈ write time:
  synchronized: throughput ≈ 1x (all serialised)
  ReadWriteLock: throughput ≈ 100x for reads (all concurrent)
```

---

### 🧠 Mental Model / Analogy

> A whiteboard in a meeting room. Multiple people can look at it at the same time (read lock — non-destructive). But to erase and rewrite it (write lock), everyone must stop looking and leave the room — and no new viewers allowed until the rewrite is done.

---

### ⚙️ How It Works

```
ReentrantReadWriteLock rwLock = new ReentrantReadWriteLock();
Lock readLock  = rwLock.readLock();
Lock writeLock = rwLock.writeLock();

Read operation:
  readLock.lock();
  try {
      return data.read();  // any number of threads can be here simultaneously
  } finally {
      readLock.unlock();
  }

Write operation:
  writeLock.lock();       // blocks until all readers release AND no other writers
  try {
      data.write(value);  // exclusive access
  } finally {
      writeLock.unlock();
  }

Advanced: Lock downgrade (write → read, atomically, without releasing)
  writeLock.lock();
  try {
      data.write(value);
      readLock.lock();     // acquire read lock BEFORE releasing write lock
  } finally {
      writeLock.unlock();  // release write; read lock still held
  }
  try {
      return data.read();  // read with lock still held continuously
  } finally {
      readLock.unlock();
  }

Note: Lock UPGRADE (read → write) is NOT supported → deadlock risk
```

---

### 🔄 How It Connects

```
ReadWriteLock
  ├─ vs synchronized/ReentrantLock → RWL has higher throughput for read-heavy
  ├─ vs StampedLock (Java 8)       → StampedLock adds optimistic reads (even faster)
  ├─ write starvation risk         → fair=true helps; or use StampedLock
  ├─ lock downgrade                → write→read supported
  └─ lock upgrade                  → read→write NOT supported (deadlock)
```

---

### 💻 Code Example

```java
// Thread-safe cache with ReadWriteLock
public class RWCache<K, V> {
    private final Map<K, V> cache = new HashMap<>();          // not thread-safe alone
    private final ReentrantReadWriteLock rwLock = new ReentrantReadWriteLock();
    private final Lock readLock  = rwLock.readLock();
    private final Lock writeLock = rwLock.writeLock();

    public V get(K key) {
        readLock.lock();
        try {
            return cache.get(key);  // N threads can read simultaneously
        } finally {
            readLock.unlock();
        }
    }

    public void put(K key, V value) {
        writeLock.lock();
        try {
            cache.put(key, value);  // exclusive; blocks all readers
        } finally {
            writeLock.unlock();
        }
    }

    public V computeIfAbsent(K key, Function<K, V> loader) {
        // Try read first (common case — already cached)
        readLock.lock();
        try {
            V existing = cache.get(key);
            if (existing != null) return existing;
        } finally {
            readLock.unlock();
        }

        // Miss — acquire write lock; re-check (double-checked locking)
        writeLock.lock();
        try {
            return cache.computeIfAbsent(key, loader);
        } finally {
            writeLock.unlock();
        }
    }
}
```

```java
// Lock downgrade: write then read without releasing exclusivity gap
ReentrantReadWriteLock rwLock = new ReentrantReadWriteLock();
rwLock.writeLock().lock();
try {
    // Update data
    updateData();

    // Acquire read lock BEFORE releasing write lock (downgrade)
    rwLock.readLock().lock();
} finally {
    rwLock.writeLock().unlock(); // release write; still hold read
}
try {
    return readData(); // guaranteed to see own write
} finally {
    rwLock.readLock().unlock();
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| ReadWriteLock always outperforms ReentrantLock | Only wins when read:write ratio is high; overhead of two locks makes it SLOWER for write-heavy |
| Read lock is always non-blocking | Read lock blocks if a write lock is waiting (write-preferring policy) or held |
| Lock upgrade (read→write) is supported | Not supported — will deadlock if attempted. Only downgrade is supported |
| Fair mode eliminates starvation | Fair reduces it; under heavy read load, writers can still wait long |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Forgetting to unlock in finally — lock leak**

```java
// Same as ReentrantLock — must unlock in finally
readLock.lock();
return expensiveOp();  // ❌ if throws, lock never released → all writers block forever

// Fix:
readLock.lock();
try { return expensiveOp(); } finally { readLock.unlock(); }
```

**Pitfall 2: Write starvation — continuous readers starve writer**

```java
// High read traffic + unfair lock → writer waits indefinitely
// Fix 1: use fair lock: new ReentrantReadWriteLock(true)
// Fix 2: use StampedLock (optimistic reads don't block writers)
```

---

### 🔗 Related Keywords

- **[ReentrantLock](./076 — ReentrantLock.md)** — single-mode lock predecessor
- **[StampedLock](./087 — StampedLock.md)** — Java 8 evolution with optimistic reads
- **[ConcurrentHashMap](./082 — ConcurrentHashMap.md)** — CHM uses similar read-heavy strategy internally
- **[Race Condition](./072 — Race Condition.md)** — what ReadWriteLock prevents

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Concurrent reads OR exclusive write;          │
│              │ maximises throughput for read-heavy workloads │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Read:write ratio > 5:1; config stores; caches;│
│              │ reference data updated infrequently           │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Write-heavy workloads — overhead exceeds gain;│
│              │ need optimistic reads → use StampedLock       │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Unlimited readers, one writer —              │
│              │  readers never block readers"                 │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ StampedLock → ConcurrentHashMap →             │
│              │ Lock downgrade pattern → write starvation     │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A cache has a `computeIfAbsent` method that (1) checks cache with read lock, (2) misses and acquires write lock, (3) checks again, (4) computes and stores. Why is the second check (step 3) necessary even though step 2 is a write lock? What could happen without it?

**Q2.** Why is lock UPGRADE (read → write) not supported in ReentrantReadWriteLock? Construct a deadlock scenario with 2 threads that would occur if upgrade were allowed.

**Q3.** What is "write starvation"? Under what conditions can it occur in a non-fair ReadWriteLock? How does StampedLock's optimistic read mode mitigate this?

