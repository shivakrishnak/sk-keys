---
layout: default
title: "ReadWriteLock"
parent: "Java Concurrency"
nav_order: 342
permalink: /java-concurrency/read-write-lock/
number: "0342"
category: Java Concurrency
difficulty: ★★★
depends_on: ReentrantLock, synchronized, Thread Lifecycle
used_by: StampedLock, Cache implementations
related: ReentrantLock, StampedLock, synchronized
tags:
  - java
  - concurrency
  - locking
  - deep-dive
  - performance
---

# 0342 — ReadWriteLock

⚡ TL;DR — `ReadWriteLock` separates read and write access: multiple readers can hold the read lock simultaneously, but a writer gets exclusive access — dramatically improving throughput for read-heavy workloads where a single `synchronized` lock forces readers to block each other unnecessarily.

| #0342 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ReentrantLock, synchronized, Thread Lifecycle | |
| **Used by:** | StampedLock, Cache implementations | |
| **Related:** | ReentrantLock, StampedLock, synchronized | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A cache reads data on every request and refreshes data occasionally. Using `synchronized` for all access means 1,000 concurrent reads block each other — only one read proceeds at a time. 999 threads wait even though reads don't interfere with each other. The cache becomes a bottleneck instead of a performance improvement.

**THE BREAKING POINT:**
A product catalog service has 10,000 reads/second and 1 write/minute. With `synchronized`, those 10,000 reads serialize through one lock — throughput is limited to one read per lock acquisition/release cycle. The single write per minute provides no benefit — reads still queue up 10,000 deep.

**THE INVENTION MOMENT:**
This is exactly why **`ReadWriteLock`** was created — reads are safe to run simultaneously (they don't modify state), so they should not block each other. Only writes need exclusive access.

---

### 📘 Textbook Definition

**`ReadWriteLock`** is an interface in `java.util.concurrent.locks` representing a pair of locks: a read lock (shared — multiple holders allowed simultaneously) and a write lock (exclusive — must be the sole holder). `ReentrantReadWriteLock` is the standard implementation. Rules: multiple threads may hold the read lock simultaneously if no thread holds the write lock; the write lock can only be acquired when no threads hold the read lock or write lock. Read lock and write lock are derived from the same `ReentrantReadWriteLock` instance. Supports optional fairness and lock downgrading (write → read).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Many readers can read at once; writers get exclusive access — maximising throughput for read-heavy data.

**One analogy:**
> A library reading room with a "research mode" and "restocking mode": in research mode, anyone can enter and read books simultaneously. When a librarian needs to restock (write), the room is closed until they're done. `ReadWriteLock` is this policy — parallel reads, exclusive writes.

**One insight:**
`ReadWriteLock` is only beneficial when reads are frequent AND reads significantly outnumber writes. For write-heavy workloads, the overhead of tracking read lock holders makes `ReadWriteLock` SLOWER than `synchronized`. Always measure before switching.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Read lock is shared: `N` threads can hold it simultaneously (N > 0) — provided no write lock is held.
2. Write lock is exclusive: only 1 thread can hold it — requires ALL read locks to be released first.
3. Write lock holder can acquire the read lock (lock downgrade), but read lock holder CANNOT upgrade to write lock (would deadlock: waiting for other readers to release, while they also wait).

**DERIVED DESIGN:**
Lock state is encoded as one 32-bit `int` in AQS: upper 16 bits = read hold count, lower 16 bits = write hold count. This allows atomic check of both counts.

```
ReadWriteLock State Logic:
  state = (readCount << 16) | writeCount

  Read lock acquire: state & WRITE_MASK == 0 (no writer)
    → CAS state to state + READ_UNIT
  
  Write lock acquire: state == 0 (no readers or writers)
    → CAS state to 1
  
  Read lock release: CAS state to state - READ_UNIT
  Write lock release: state = 0
```

**THE TRADE-OFFS:**
**Gain:** Parallel reads — dramatically improves throughput for read-heavy workloads; reads don't block each other.
**Cost:** Write lock must wait for ALL readers to release — write starvation possible if readers continuously hold; overhead of read count tracking; no lock upgrade (read→write); more complex than synchronized.

---

### 🧪 Thought Experiment

**SETUP:**
10,000 threads reading, 1 thread writing, same data.

WITH `synchronized`:
- 10,001 threads serialize through one lock
- Max throughput: ~1M lock acquires/second = 10,000 reads take 10ms
- 1 write in 60 seconds adds 0.01% overhead — irrelevant

WITH `ReadWriteLock`:
- All 10,000 readers acquire read lock simultaneously
- Throughput: 10,000 reads in parallel — bounded by CPU/memory, not lock
- Writer waits for readers, then gets exclusive access

**THE INSIGHT:**
`synchronized` turns reads into a sequential operation unnecessarily. `ReadWriteLock` preserves the natural concurrency of reads. The tradeoff appears when writers compete: writes can be starved if readers continuously hold, depending on the fairness policy.

---

### 🧠 Mental Model / Analogy

> A highway with "shared lanes" (reads) and one "exclusive lane" for construction (writes). Shared lane vehicles (readers) travel simultaneously — no mutual blocking. Construction crew (writer) needs to close all shared lanes — they wait until all vehicles exit, do their work, then reopen all lanes.

- "Shared lane travel" → concurrent read lock holders.
- "Closing all lanes" → write lock acquisition in exclusive mode.
- "Construction crew waiting" → write lock blocked until reads release.

Where this analogy breaks down: On a real highway, construction can start with "one lane closed" — partial closures. `ReadWriteLock` is all-or-nothing: write requires ALL readers to be gone.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Instead of everyone waiting for a locked door (synchronized), readers can all peek through a window simultaneously. Only the writer needs to lock the door.

**Level 2:** Use `rwLock.readLock().lock()` + try/finally in read methods. Use `rwLock.writeLock().lock()` + try/finally in write methods. Always unlock in `finally`. For cache patterns: read lock for `get()`, write lock for `put()` and `invalidate()`.

**Level 3:** `ReentrantReadWriteLock` stores reader count in upper 16 bits and writer count in lower 16 bits of a single AQS `state` int. Read lock tracks thread-local hold counts in a `ThreadLocal`. Write lock is reentrant (same thread can acquire again). Read lock is NOT reentrant from a write context by default — downgrade is supported (acquire read while holding write, release write), upgrade is not (deadlock).

**Level 4:** `ReadWriteLock` is fundamentally limited by write starvation on high-read-load systems. `StampedLock` (Java 8) solves this with optimistic reads: read without acquiring any lock, validate afterward; if data changed during read, retry with lock. `StampedLock` offers potentially higher throughput at the cost of more complex usage (no reentrancy, hard to use correctly).

---

### ⚙️ How It Works (Mechanism)

**Standard usage:**
```java
ReentrantReadWriteLock rwLock = new ReentrantReadWriteLock();
Lock readLock  = rwLock.readLock();
Lock writeLock = rwLock.writeLock();
Map<String, Data> cache = new HashMap<>();

// Read: multiple threads can execute concurrently
Data get(String key) {
    readLock.lock();
    try { return cache.get(key); }
    finally { readLock.unlock(); }
}

// Write: exclusive access
void put(String key, Data value) {
    writeLock.lock();
    try { cache.put(key, value); }
    finally { writeLock.unlock(); }
}

void invalidate(String key) {
    writeLock.lock();
    try { cache.remove(key); }
    finally { writeLock.unlock(); }
}
```

**Lock downgrade (write → read):**
```java
// Downgrade: acquire read lock while holding write, then release write
writeLock.lock();
try {
    updateData();       // exclusive write
    readLock.lock();    // acquire read lock before releasing write
    try { useData(); }  // use data under read lock
    finally { readLock.unlock(); }
} finally {
    writeLock.unlock(); // release write lock after acquiring read
}
// Lock downgrade is supported — prevents another writer sneaking in
```

**Fairness:**
```java
// Fair mode: writers don't starve readers don't starve
ReentrantReadWriteLock fairRwLock =
    new ReentrantReadWriteLock(true); // fair = true
// All waiting threads served in FIFO order
// Prevents write starvation but reduces throughput
```

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW (read-heavy):
```
[10,000 threads: readLock.lock()]
    → [AQS: readCount = 0, writeCount = 0]  ← YOU ARE HERE
    → [CAS: state += READ_UNIT × 10,000]
    → [All 10,000 threads hold read lock]
    → [All read data in parallel]
    → [Each releases: readLock.unlock()]
    → [state decrements per release]
    → [Writer waiting: writeLock.lock()]
    → [Blocked until readCount = 0]
    → [Last reader releases → writer unparked]
    → [Writer: exclusive access]
```

FAILURE PATH (write starvation):
```
[Non-fair mode, continuous readers]
    → [Writer waits for readCount = 0]
    → [New readers keep arriving, re-acquiring read lock]
    → [readCount never reaches 0]
    → [Writer waits indefinitely — STARVATION]
    → [Fix: use fair=true, or StampedLock with write priority]
```

**WHAT CHANGES AT SCALE:**
At scale, `CopyOnWriteArrayList` and `CopyOnWriteArraySet` provide an alternative: both use a similar "readers don't block" principle but via copy-on-write rather than locks — reads are completely non-blocking (no lock at all), writes create a new copy and do an atomic reference swap. For read-dominant data with infrequent writes, this is simpler and faster than `ReadWriteLock`.

---

### 💻 Code Example

Example 1 — Cache with invalidation:
```java
public class UserCache {
    private final ReentrantReadWriteLock lock =
        new ReentrantReadWriteLock();
    private final Map<Long, User> cache = new HashMap<>();

    public User get(Long id) {
        lock.readLock().lock();
        try { return cache.get(id); }
        finally { lock.readLock().unlock(); }
    }

    public void put(Long id, User user) {
        lock.writeLock().lock();
        try { cache.put(id, user); }
        finally { lock.writeLock().unlock(); }
    }

    public void invalidate(Long id) {
        lock.writeLock().lock();
        try { cache.remove(id); }
        finally { lock.writeLock().unlock(); }
    }

    public int size() {
        lock.readLock().lock();
        try { return cache.size(); }
        finally { lock.readLock().unlock(); }
    }
}
```

---

### ⚖️ Comparison Table

| Lock Type | Read Concurrency | Write Exclusivity | Starvation | Reentrancy | Best For |
|---|---|---|---|---|---|
| `synchronized` | No (single) | Yes | Possible | Yes | Simple critical sections |
| `ReentrantLock` | No (single) | Yes | Possible | Yes | Complex locking with timeout |
| **`ReadWriteLock`** | Yes (parallel) | Yes | Write possible | Yes | Read-heavy data structures |
| `StampedLock` | Yes (optimistic) | Yes | Minimal | No | Very read-heavy, low contention |

How to choose: Use `ReadWriteLock` when the access pattern is >90% reads and <10% writes. Use `StampedLock` for maximum performance with acceptable complexity. Use `synchronized` or `ReentrantLock` for balanced or write-heavy workloads.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| ReadWriteLock is always faster than synchronized | ReadWriteLock has higher overhead per acquisition than synchronized. It's faster ONLY when many threads read concurrently. For write-heavy or low-concurrency workloads, it's slower |
| Read lock allows concurrent writes | No — the read lock BLOCKS write lock acquisition and vice versa. Concurrent reads only |
| You can upgrade read lock to write lock | Lock UPGRADE (read→write) is not supported and causes deadlock: reader waiting for other readers to release, while another thread tries to write |
| ReadWriteLock prevents write starvation | In non-fair mode (default), continuous readers can starve writers indefinitely. Use `new ReentrantReadWriteLock(true)` for fair mode to prevent starvation |

---

### 🚨 Failure Modes & Diagnosis

**Write Starvation**

**Symptom:** Writers never execute; cache data grows stale indefinitely.

**Root Cause:** Non-fair `ReadWriteLock`; new readers continuously arrive, keeping `readCount > 0`.

**Fix:** Use `new ReentrantReadWriteLock(true)` (fair). Or redesign with `StampedLock`. Or rate-limit read acquisitions to allow writes.

---

**Deadlock from Lock Upgrade Attempt**

**Symptom:** Two threads deadlocked — both holding read lock, both waiting for write lock.

**Root Cause:** Thread attempts to acquire write lock while holding read lock.

**Fix:**
```java
// WRONG: upgrade attempt → deadlock
readLock.lock();
try {
    if (needsUpdate()) {
        writeLock.lock(); // DEADLOCK if another thread holds read!
        try { performUpdate(); }
        finally { writeLock.unlock(); }
    }
} finally { readLock.unlock(); }

// CORRECT: release read, acquire write
readLock.lock();
boolean needsUpdate;
try { needsUpdate = checkNeedsUpdate(); }
finally { readLock.unlock(); }

if (needsUpdate) {
    writeLock.lock();
    try { performUpdate(); }
    finally { writeLock.unlock(); }
}
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `ReentrantLock` — ReadWriteLock is built on the same AQS framework; understanding ReentrantLock is prerequisite
- `synchronized` — ReadWriteLock is an alternative for the specific read-heavy case

**Builds On This (learn these next):**
- `StampedLock` — the optimistic-read evolution; higher performance but more complex

**Alternatives / Comparisons:**
- `StampedLock` — adds optimistic reads for even better read performance
- `CopyOnWriteArrayList` — lock-free reads via copy-on-write; simpler model for infrequent writes

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Read lock (shared) + write lock (exclusive)│
│              │ — parallel reads, exclusive writes        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ synchronized serializes readers needlessly;│
│ SOLVES       │ reads are safe to run in parallel         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Faster only when reads >> writes. For     │
│              │ balanced workloads, synchronized is faster.│
│              │ Write starvation in non-fair mode.        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Read-dominant data: caches, catalogs,     │
│              │ frequently reads / rarely updates         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Write-heavy; balanced; single-threaded    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Parallel reads vs write starvation risk;  │
│              │ throughput vs upgrade limitation          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Many can read, one can write — never both"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ StampedLock → ConcurrentHashMap →         │
│              │ CopyOnWriteArrayList                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A distributed product catalog serves 50,000 reads/second and refreshes all data every 5 seconds (bulk write). Compare three implementation strategies for thread-safe access: (1) `ReentrantReadWriteLock`, (2) `CopyOnWriteArrayList` (reference swap), (3) `StampedLock` with optimistic reads. For each, calculate the approximate lock overhead per operation at 50,000 RPS, analyse the impact of the 5-second bulk write on read throughput, and identify which strategy provides zero read blocking during the write.

**Q2.** `ReentrantReadWriteLock` explicitly does NOT support lock upgrade (read→write). Explain why allowing lock upgrade would deadlock: trace the exact sequence with two threads T1 and T2 both holding read locks and both attempting write lock upgrade simultaneously, showing the precise state of the AQS state integer at each step. Then describe the "read-check-release-write" pattern that avoids the deadlock at the cost of a possible race condition during the gap between read release and write acquisition, and explain how to make this pattern correct.

