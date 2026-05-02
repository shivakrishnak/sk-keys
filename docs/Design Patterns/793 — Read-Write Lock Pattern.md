---
layout: default
title: "Read-Write Lock Pattern"
parent: "Design Patterns"
nav_order: 793
permalink: /design-patterns/read-write-lock-pattern/
number: "793"
category: Design Patterns
difficulty: ★★★
depends_on: "Thread Safety, Happens-Before, volatile, ReentrantLock"
used_by: "Caches, configuration stores, in-memory data structures, read-heavy shared state"
tags: #advanced, #design-patterns, #concurrency, #threading, #locking, #performance
---

# 793 — Read-Write Lock Pattern

`#advanced` `#design-patterns` `#concurrency` `#threading` `#locking` `#performance`

⚡ TL;DR — **Read-Write Lock** allows multiple concurrent readers OR one exclusive writer — maximizing read throughput in read-heavy workloads where plain `synchronized` would block all readers when any thread holds the lock.

| #793            | Category: Design Patterns                                                        | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Thread Safety, Happens-Before, volatile, ReentrantLock                           |                 |
| **Used by:**    | Caches, configuration stores, in-memory data structures, read-heavy shared state |                 |

---

### 📘 Textbook Definition

**Read-Write Lock**: a synchronization pattern that maintains a pair of locks — a read lock and a write lock. Multiple threads can hold the read lock simultaneously (shared access, since reads don't modify state). Only one thread can hold the write lock (exclusive access, since writes modify state), and it excludes all readers. This pattern optimizes for the common case in many systems: many readers, few writers. Java: `java.util.concurrent.locks.ReentrantReadWriteLock` implements this pattern. `ReadWriteLock` interface: `readLock()` returns the shared lock; `writeLock()` returns the exclusive lock. `StampedLock` (Java 8): adds optimistic read — read without locking, validate afterward; upgrade to write lock if needed.

---

### 🟢 Simple Definition (Easy)

A library reading room. Multiple students can read books simultaneously (concurrent readers — no problem). But when a librarian needs to reorganize the shelves (write), all readers must leave and no new readers admitted until reorganization is done. Read-Write Lock: "reading" acquires the read lock (allows others to read too). "Reorganizing" acquires the write lock (blocks all reads and other writes).

---

### 🔵 Simple Definition (Elaborated)

Configuration cache: 1000 requests/sec read config. Config refreshed every 5 minutes. Without Read-Write Lock: `synchronized` blocks all 1000 concurrent readers when even 1 reader holds the lock — serialized reads. With Read-Write Lock: all 1000 threads read simultaneously (concurrent). Every 5 minutes, config refresh acquires write lock — 1000 readers briefly paused, refresh completes (<1ms), readers resume. Net effect: massive throughput improvement for read-dominated access patterns.

---

### 🔩 First Principles Explanation

**Read lock vs write lock semantics and ReentrantReadWriteLock usage:**

```
READ-WRITE LOCK RULES:

  READ LOCK:
  ✓ Multiple threads can hold read lock simultaneously
  ✗ Cannot be acquired while write lock is held

  WRITE LOCK:
  ✓ One thread holds write lock exclusively
  ✗ Cannot be acquired while read lock is held by ANY thread
  ✗ Cannot be acquired while write lock is held by another thread

  UPGRADE:
  Cannot upgrade read lock to write lock directly (would deadlock):
  Thread A holds read lock. Tries to upgrade to write lock.
  Write lock waits for all readers. Thread A holds read lock.
  Thread A waits for write lock. DEADLOCK.

  DOWNGRADE:
  CAN downgrade write lock to read lock:
  1. Acquire write lock
  2. Write
  3. Acquire read lock (while holding write lock — allowed)
  4. Release write lock (now only read lock held)
  → Other readers can now proceed; no writer can proceed.

JAVA ReentrantReadWriteLock:

  class ConfigStore {
      private final ReentrantReadWriteLock rwLock = new ReentrantReadWriteLock();
      private final Lock readLock  = rwLock.readLock();
      private final Lock writeLock = rwLock.writeLock();

      private volatile Map<String, String> config = new HashMap<>();

      // READ — multiple threads can execute concurrently:
      String get(String key) {
          readLock.lock();
          try {
              return config.get(key);
          } finally {
              readLock.unlock();         // ALWAYS unlock in finally!
          }
      }

      // WRITE — exclusive; blocks all readers and other writers:
      void refresh(Map<String, String> newConfig) {
          writeLock.lock();
          try {
              this.config = new HashMap<>(newConfig);   // replace config
          } finally {
              writeLock.unlock();
          }
      }
  }

  // Concurrent reads — ALL proceed simultaneously:
  // Thread 1: readLock.lock() → get("host")     → readLock.unlock()
  // Thread 2: readLock.lock() → get("port")     → readLock.unlock()
  // Thread 3: readLock.lock() → get("timeout")  → readLock.unlock()
  // All 3 overlap — no blocking.

  // Write — exclusive:
  // Thread W: writeLock.lock() → waits for Thread 1,2,3 to finish → refresh() → unlock
  // Thread 1,2,3 resume after write.

STAMPEDLOCK (JAVA 8) — OPTIMISTIC READS:

  class PointCache {
      private final StampedLock lock = new StampedLock();
      private double x, y;

      // OPTIMISTIC READ — no lock acquired! Just reads a stamp.
      // If data wasn't modified since stamp: read is valid. No lock cost.
      // If data WAS modified: validate() returns false → fall back to read lock.
      double distanceFromOrigin() {
          long stamp = lock.tryOptimisticRead();  // get stamp (no locking)
          double curX = x, curY = y;              // read (might be inconsistent if writer ran)

          if (!lock.validate(stamp)) {            // was there a write? stamp invalidated?
              // Optimistic read FAILED — writer ran between stamp and validate.
              // Fall back to full read lock:
              stamp = lock.readLock();
              try {
                  curX = x; curY = y;
              } finally {
                  lock.unlockRead(stamp);
              }
          }
          return Math.sqrt(curX * curX + curY * curY);
      }

      void move(double deltaX, double deltaY) {
          long stamp = lock.writeLock();
          try {
              x += deltaX;
              y += deltaY;
          } finally {
              lock.unlockWrite(stamp);
          }
      }
  }

  // Optimistic read: ZERO lock cost on no-contention paths. Ultra-fast for read-heavy.
  // Falls back to read lock only if writer ran during read — rare in practice.

READ-WRITE LOCK vs synchronized:

  synchronized (same as ReentrantLock):
  Only ONE thread at a time — even multiple readers block each other.
  Simple to use. Always correct.

  ReentrantReadWriteLock:
  N concurrent readers. 1 exclusive writer.
  Faster for read-heavy workloads.
  More complex to use correctly (must always unlock in finally).

  StampedLock:
  N concurrent readers + 1 writer.
  PLUS: optimistic reads (zero lock cost in no-contention case).
  Fastest for read-dominated, write-rare scenarios.
  Most complex. Non-reentrant! (Cannot lock twice from same thread.)

WRITER STARVATION:

  Default ReentrantReadWriteLock (non-fair):
  Writers can starve if readers continuously hold the read lock.
  New reader can acquire read lock even while a writer is waiting.

  Fair mode: ReentrantReadWriteLock(true):
  Waiting writer blocks new readers — ensures writer eventually proceeds.
  Lower throughput (limits reader concurrency) but prevents starvation.

  Generally: non-fair mode unless write starvation is observed.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Read-Write Lock:

- `synchronized` on reads: only 1 thread reads at a time — serialized reads for a shared, read-mostly data structure

WITH Read-Write Lock:
→ N threads read concurrently. Only writes are exclusive. Throughput for read-heavy workloads increases proportional to the number of reader threads.

---

### 🧠 Mental Model / Analogy

> A museum gallery. Many visitors can view art simultaneously (multiple concurrent readers — OK). When the museum staff needs to hang a new painting (write), the gallery temporarily closes to visitors (exclusive write). No one new enters; current visitors finish and leave; staff does the work; gallery reopens to visitors. Read-Write Lock: visitors = readers (can be concurrent), staff = writer (must be exclusive).

"Gallery visitors" = reader threads (holding read lock)
"Staff hanging painting" = writer thread (holding write lock)
"Multiple visitors simultaneously" = concurrent read lock holders
"Gallery closed during staff work" = read lock blocked during write lock
"Gallery reopens" = write lock released; readers can acquire read lock again
"One staff job at a time" = write lock is exclusive (one writer at a time)

---

### ⚙️ How It Works (Mechanism)

```
READ-WRITE LOCK STATE MACHINE:

  State: (readCount, writeHeld)

  readLock.lock():
  - If writeHeld: BLOCK (writer holds exclusive lock)
  - Else: readCount++ (proceed concurrently)

  readLock.unlock():
  - readCount--
  - If readCount == 0 AND writer waiting: signal writer

  writeLock.lock():
  - If readCount > 0 OR writeHeld: BLOCK
  - Else: writeHeld = true (exclusive)

  writeLock.unlock():
  - writeHeld = false
  - Signal all waiting readers (and next writer)
```

---

### 🔄 How It Connects (Mini-Map)

```
Concurrent reads, exclusive writes — optimize for read-heavy shared state
        │
        ▼
Read-Write Lock Pattern ◄──── (you are here)
(readLock: shared; writeLock: exclusive; StampedLock: optimistic read)
        │
        ├── Double-Checked Locking: uses volatile (not RWLock) for lock-free lazy init
        ├── ConcurrentHashMap: built-in segment locking (similar to fine-grained RW lock)
        ├── Cache implementations: often use RWLock for shared read, exclusive write-through
        └── StampedLock: optimistic extension of Read-Write Lock concept
```

---

### 💻 Code Example

```java
// Thread-safe cache with read-write lock:
public class UserCache {
    private final ReentrantReadWriteLock rwLock = new ReentrantReadWriteLock();
    private final Lock readLock  = rwLock.readLock();
    private final Lock writeLock = rwLock.writeLock();
    private final Map<Long, User> cache = new HashMap<>();

    // Read: concurrent — many threads can call simultaneously
    public Optional<User> findById(long id) {
        readLock.lock();
        try {
            return Optional.ofNullable(cache.get(id));
        } finally {
            readLock.unlock();
        }
    }

    // Write: exclusive — blocks all reads during update
    public void put(User user) {
        writeLock.lock();
        try {
            cache.put(user.getId(), user);
        } finally {
            writeLock.unlock();
        }
    }

    // Write-downgrade: write → read (for cache-aside pattern)
    public User getOrLoad(long id, Supplier<User> loader) {
        // First: try read lock (fast path, no load needed)
        readLock.lock();
        try {
            User cached = cache.get(id);
            if (cached != null) return cached;
        } finally {
            readLock.unlock();
        }

        // Cache miss: acquire write lock, re-check, load if still missing
        writeLock.lock();
        try {
            // Re-check: another thread may have loaded while we waited for write lock
            User cached = cache.get(id);
            if (cached != null) return cached;

            User loaded = loader.get();
            cache.put(id, loaded);

            // Downgrade: acquire read lock before releasing write lock
            readLock.lock();   // downgrade — hold both briefly
            return loaded;
        } finally {
            writeLock.unlock();  // release write lock; now only read lock held
            readLock.unlock();   // release read lock
        }
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                                                                                                                                                                                                                                                          |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Read-Write Lock is always faster than synchronized       | Only for read-heavy workloads. Read-Write Lock has higher overhead per operation than `synchronized`. For write-heavy or balanced workloads, `synchronized` can be faster (lower overhead). Profile first. Rule: Read-Write Lock pays off when reads dominate (>80% reads). `ConcurrentHashMap` is often better than a `HashMap` wrapped with a `ReadWriteLock`. |
| Read lock → write lock upgrade is safe                   | WRONG. Attempting to upgrade (read→write) while holding a read lock will deadlock in `ReentrantReadWriteLock`. No thread can hold a read lock while another holds or is waiting for the write lock. The solution: release read lock first, then acquire write lock (with double-check for race condition in between).                                            |
| StampedLock is always better than ReentrantReadWriteLock | `StampedLock` is NOT reentrant — a thread cannot lock it twice (would deadlock). It also doesn't support the standard `Lock` interface, making it harder to compose. For simple use cases, `ReentrantReadWriteLock` is safer. `StampedLock` is the choice for maximum performance in non-reentrant, read-optimistic scenarios (coordinates, cached values).      |

---

### 🔥 Pitfalls in Production

**Forgetting to unlock in all code paths — lock forever held:**

```java
// ANTI-PATTERN: exception causes lock to never be released:
class BadConfigStore {
    private final ReentrantReadWriteLock rwLock = new ReentrantReadWriteLock();

    String get(String key) {
        rwLock.readLock().lock();
        String value = config.get(key);

        if (value == null) {
            throw new ConfigNotFoundException(key);  // EXCEPTION! readLock NEVER UNLOCKED!
        }

        rwLock.readLock().unlock();  // never reached if exception thrown
        return value;
    }
}
// One config miss → read lock never unlocked.
// Next write lock acquisition: waits forever → deadlock.
// All subsequent reads that wait for write lock: blocked forever.

// FIX: ALWAYS use try-finally:
String get(String key) {
    rwLock.readLock().lock();
    try {
        String value = config.get(key);
        if (value == null) throw new ConfigNotFoundException(key);  // OK — finally runs
        return value;
    } finally {
        rwLock.readLock().unlock();  // ALWAYS runs, exception or not
    }
}

// ALSO: holding locks too long:
// BAD: hold write lock during slow external call:
writeLock.lock();
try {
    String value = externalApiClient.fetch(key);  // SLOW! holds write lock during HTTP call
    cache.put(key, value);                         // all readers blocked for entire HTTP duration
} finally { writeLock.unlock(); }

// FIX: fetch without lock, then write:
String value = externalApiClient.fetch(key);  // slow operation WITHOUT lock
writeLock.lock();
try { cache.put(key, value); }               // fast write WITH lock
finally { writeLock.unlock(); }
```

---

### 🔗 Related Keywords

- `ReentrantLock` — single-mode lock; simpler but blocks all concurrent access (no shared read)
- `StampedLock` — extends Read-Write Lock with optimistic read (no lock cost on uncontested reads)
- `ConcurrentHashMap` — built-in fine-grained locking: better alternative to HashMap + RWLock for maps
- `volatile` — simpler alternative for single-variable reads (no locking; JMM visibility only)
- `Happens-Before` — RWLock guarantees: write lock release happens-before subsequent read lock acquisition

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Multiple concurrent readers OR one        │
│              │ exclusive writer. Read-heavy workloads:  │
│              │ far better throughput than synchronized.  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Many readers, few writers; read-heavy    │
│              │ shared state (cache, config, registry);  │
│              │ synchronized is a bottleneck on reads    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Mostly writes (>50%); lock upgrade needed;│
│              │ ConcurrentHashMap solves the problem;    │
│              │ low contention (synchronized is fine)    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Museum gallery: many visitors can view  │
│              │  art simultaneously; closed only when    │
│              │  staff installs new artwork."            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ StampedLock → ConcurrentHashMap →        │
│              │ volatile → ReentrantLock → Happens-Before │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `StampedLock.tryOptimisticRead()` returns a stamp without acquiring any lock. The thread then reads shared state and calls `lock.validate(stamp)`. If another thread did a write between `tryOptimisticRead()` and `validate()`, the stamp is invalidated and the read falls back to a full read lock. This is the "optimistic concurrency" concept applied to locking. How is `StampedLock` optimistic read similar to optimistic locking in databases (using a version number to detect concurrent updates)? What is the theoretical maximum performance gain of optimistic reads over regular read locks?

**Q2.** `java.util.concurrent.CopyOnWriteArrayList` and `CopyOnWriteArraySet` use a different concurrency strategy than Read-Write Lock: on every write, they create a COMPLETE COPY of the underlying array. Reads: lock-free (no synchronization, read the snapshot). Writes: expensive (full array copy). This is effectively "read lock = nothing; write lock = copy + replace." When is `CopyOnWriteArrayList` better than a `List` protected by `ReentrantReadWriteLock`? Consider: write frequency, list size, read concurrency, and iteration behavior.
