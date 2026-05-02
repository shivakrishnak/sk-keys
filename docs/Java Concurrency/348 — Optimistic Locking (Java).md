---
layout: default
title: "Optimistic Locking (Java)"
parent: "Java Concurrency"
nav_order: 348
permalink: /java-concurrency/optimistic-locking/
number: "0348"
category: Java Concurrency
difficulty: ★★★
depends_on: CAS (Compare-And-Swap), StampedLock, Race Condition
used_by: Database Fundamentals, StampedLock
related: CAS (Compare-And-Swap), StampedLock, Pessimistic Locking
tags:
  - java
  - concurrency
  - locking
  - deep-dive
  - pattern
---

# 0348 — Optimistic Locking (Java)

⚡ TL;DR — Optimistic locking assumes conflicts are rare: read without locking, detect at commit time if a conflict occurred, retry if so — eliminating lock contention overhead for low-conflict workloads at the cost of retry logic.

| #0348 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | CAS (Compare-And-Swap), StampedLock, Race Condition | |
| **Used by:** | Database Fundamentals, StampedLock | |
| **Related:** | CAS (Compare-And-Swap), StampedLock, Pessimistic Locking | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT (pessimistic locking):
Pessimistic locking says: "conflicts WILL happen — lock first, do work, release." For 1,000 users reading a product price and 1 batch job updating it per hour, the 1,000 readers all acquire and release the lock synchronously. They block each other (pessimistically) even though they never actually conflict. 99.9% of lock acquisition is wasted overhead for conflicts that never happen.

THE BREAKING POINT:
A global product catalog receives 100,000 reads/second and updates once per hour. With pessimistic locking (synchronized), all reads serialise — throughput capped at 1M reads/min. With optimistic locking, reads proceed without locks; the hourly update detects no conflict and succeeds immediately. Throughput: effectively unlimited reads.

THE INVENTION MOMENT:
**Optimistic locking** assumes conflicts are rare and expensive verification is preferable to the constant overhead of locks.

---

### 📘 Textbook Definition

**Optimistic Locking** is a concurrency control strategy where reads proceed without acquiring any lock, and a conflict detection check is performed at the point where state is committed (written). If no conflict occurred (no other writer modified the data), the write proceeds. If a conflict is detected, the operation is retried. Implemented in Java as: CAS operations (`AtomicInteger.compareAndSet()`), `StampedLock.tryOptimisticRead()` + `validate()`, JPA `@Version` annotation with an integer/timestamp column, and custom version-based in-memory updates.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
"Assume no conflict, verify at the end, retry if wrong" vs. "assume conflict, lock first, always."

**One analogy:**
> Two chefs sharing a recipe notebook. Optimistic: each chef copies the recipe they need (reads), modifies their copy, then tries to update the notebook — checking the page number hasn't changed (validate). If another chef changed it, they re-read and redo work. Pessimistic: each chef locks the notebook with a physical padlock before reading.

**One insight:**
Optimistic locking wins when: conflicts are rare AND the cost of re-doing work on conflict is low AND lock overhead is significant. JPA `@Version` is the canonical production pattern — version column detects stale reads before committing database changes.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. No exclusive lock is held during the read — other writers can modify concurrently.
2. At commit time, the state is verified to be unchanged since the read.
3. On conflict, the transaction is retried (not blocked — it fails fast and starts fresh).

DERIVED DESIGN:
```
Optimistic locking flow:

  1. Read state (record version V1)
  2. Compute new state (no lock held)
  3. Commit: compare stored version to V1
     - If equal: update, increment version to V2 → SUCCESS
     - If changed: conflict detected → RETRY (not BLOCK)
```

This contrasts with pessimistic locking:
```
  1. Lock resource
  2. Read state
  3. Compute
  4. Write
  5. Release lock
  → Other threads BLOCKED throughout steps 1-5
```

THE TRADE-OFFS:
Gain: No lock contention overhead for reads; high read throughput; no blocking.
Cost: Writes may fail and require retry (wasted work); under high write contention, retry storms can degrade throughput; ABA problem exists if version not used (CAS-based optimistic); more complex code.

---

### 🧪 Thought Experiment

SETUP:
10,000 threads reading inventory, 1 thread updating.

PESSIMISTIC (synchronized):
```
T1 acquires lock, reads stock=100, computes, releases
T2 acquires lock, reads stock=100 (or updated value)...
...10,000 sequential reads under lock
Throughput: ~1M reads/sec (limited by lock acquisition)
```

OPTIMISTIC:
```
T1-T9999 read stock=100 simultaneously (no lock)
Each validates: no update since read (version matches)
All 9,999 reads succeed without waiting for each other
T10000 (updater): reads version=1, sets stock=99, version=2
Next reads: read stock=99, validate version=2: success
Throughput: effectively unlimited reads (CPU/memory bound)
```

THE INSIGHT:
In the 10,000-read / 1-update scenario, optimistic locking has ~10,000× higher read throughput. Every conflict triggers a retry, but conflicts are rare (< 0.01% of reads coincide with the single update per testing cycle).

---

### 🧠 Mental Model / Analogy

> Optimistic locking is like editing a Wikipedia article without coordination. You read the current version (timestamp noted), make your edits, and try to save — the system checks if the article changed since you read. If yes, your edit is rejected (conflict) and you must re-read and redo. For most edits, no one else is editing the same section simultaneously, so saves succeed first try.

"Read version" → record current timestamp/version.
"Save with edit conflict check" → CAS or version check at commit.
"Edit conflict → redo" → optimistic locking retry.
"No conflict" → common case; succeeds without any lock at all.

Where this analogy breaks down: Wikipedia shows you the conflict clearly. Code retries silently — unless the developer implements conflict logging, retries are invisible and hard to diagnose under unexpected write contention.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Optimistic locking: read freely, check at the end if anything changed, redo if so. Pessimistic: lock first, no need to check.

**Level 2:** In JPA: add `@Version private int version` to entity — Hibernate automatically checks version on UPDATE and throws `OptimisticLockException` on conflict. In-memory: use `AtomicReference.compareAndSet()` or `StampedLock.tryOptimisticRead()` + `validate()`.

**Level 3:** CAS-based optimistic locking: the "version" is the value itself. `compareAndSet(expected, new)` succeeds only if value = expected. `StampedLock.tryOptimisticRead()` uses a clock/version stamp separate from the read locks, allowing detect if any write lock was acquired since the stamp was taken. JPA `@Version` adds a numeric column that's incremented on each UPDATE, and the WHERE clause includes `version = old_version` — if 0 rows updated (version mismatch), throw `OptimisticLockException`.

**Level 4:** Optimistic vs pessimistic is a throughput-under-conflict tradeoff. At conflict rate p: optimistic expected work = 1/(1-p) × single operation cost; pessimistic = 1 operation + average blocking time. For p < 0.1, optimistic dominates. For p > 0.5 (high write contention), pessimistic is better (no wasted work from retries). The crossover point depends on operation cost and contention topology.

---

### ⚙️ How It Works (Mechanism)

**JPA @Version (canonical database optimistic lock):**
```java
@Entity
class Product {
    @Id Long id;
    @Version int version; // auto-managed by Hibernate
    int stock;
}

// On save: Hibernate generates:
// UPDATE product SET stock=?, version=?+1
// WHERE id=? AND version=?  (optimistic check!)
// If 0 rows updated → OptimisticLockException
```

**In-memory CAS-based optimistic:**
```java
AtomicReference<BankAccount> accountRef =
    new AtomicReference<>(new BankAccount(1000.0));

void withdraw(double amount) {
    BankAccount current, updated;
    do {
        current = accountRef.get();
        if (current.balance < amount) throw new InsufficientFunds();
        updated = new BankAccount(current.balance - amount);
    } while (!accountRef.compareAndSet(current, updated));
    // Atomic: account reference only swapped if unchanged
}
```

**StampedLock optimistic (see #0343):**
```java
long stamp = sl.tryOptimisticRead();
double x = this.x, y = this.y;
if (!sl.validate(stamp)) {
    stamp = sl.readLock();
    try { x = this.x; y = this.y; }
    finally { sl.unlockRead(stamp); }
}
return Math.hypot(x, y);
```

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW (JPA):
```
[Transaction: read Product{stock=10, version=3}]
    → [No lock held: compute new stock=9]      ← YOU ARE HERE
    → [UPDATE WHERE version=3: 1 row updated]
    → [product.version becomes 4]
    → [Commit: success]
```

CONFLICT FLOW:
```
[T1 reads Product{stock=10, version=3}]
    → [T2 simultaneously decrements stock: version→4]
    → [T1: UPDATE WHERE version=3: 0 rows updated!]
    → [Hibernate throws OptimisticLockException]
    → [Service catches, retries: re-read product]
    → [Retry: product{stock=9, version=4}]
    → [T1: UPDATE WHERE version=4: success]
```

WHAT CHANGES AT SCALE:
Under write contention, optimistic retries compound. 100 threads updating the same entity: on average `N/2` retries per successful update. At extreme contention, optimistic locking degrades to N² work per N threads — much worse than pessimistic. Monitor retry rates with metrics: >5% retry rate indicates optimistic is wrong choice for this workload.

---

### 💻 Code Example

Example 1 — JPA service with retry:
```java
@Service
public class InventoryService {
    @Autowired InventoryRepository repo;

    @Retryable(include = OptimisticLockException.class,
               maxAttempts = 3)
    @Transactional
    public void decrementStock(Long productId) {
        Product p = repo.findById(productId).orElseThrow();
        if (p.getStock() <= 0) throw new OutOfStockException();
        p.setStock(p.getStock() - 1);
        // Hibernate saves on transaction commit: version check automatic
    }
}
```

Example 2 — Optimistic vs pessimistic choice:
```java
// Pessimistic: high write contention on same row
@Lock(LockModeType.PESSIMISTIC_WRITE)
@Query("SELECT p FROM Product p WHERE p.id = :id")
Product findForUpdate(@Param("id") Long id);
// Use when many concurrent updates to same entity

// Optimistic: frequent reads, occasional writes
@Version int version; // in entity — default JPA strategy
// Use when reads >> writes (most catalog scenarios)
```

---

### ⚖️ Comparison Table

| Strategy | Read Lock | Write Lock | Conflict Handling | Best For |
|---|---|---|---|---|
| **Optimistic** | None | Validate at commit | Retry on conflict | Read-heavy, low-write-contention |
| Pessimistic | Acquired | Held until commit | Block other writers | High write contention |
| Serializable | Full | Full | Database rollback | Financial, highest consistency |

How to choose: Use optimistic for catalog-style data (reads >> writes). Use pessimistic for booking/inventory with high concurrent writes to same row. Use serializable for financial transactions requiring strict isolation.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Optimistic locking never blocks | In JPA, `OptimisticLockException` causes a rollback and retry — this does involve Java exception overhead and transaction restart. It doesn't BLOCK the thread, but work is discarded and redone |
| Optimistic locking is always faster | Under high write contention (many concurrent writers to same data), the retry overhead makes optimistic worse than pessimistic. Always measure |
| `@Version` field must be managed manually | JPA/Hibernate manages `@Version` automatically: reading, incrementing, and checking on every UPDATE. You should NOT update the version field in application code |
| Optimistic locking prevents lost updates | Only if every reader checks the version before writing. If any write path bypasses the version check (native queries, direct JDBC), the optimistic lock is bypassed |

---

### 🚨 Failure Modes & Diagnosis

**Retry Storm Under High Contention**

Symptom: Database CPU spikes, many `OptimisticLockException` retries logged. Throughput degrades.

Root Cause: Many concurrent writers to same entity. Retry logic causes 2× work per conflict.

Fix:
```java
// Add exponential backoff to retries:
@Retryable(include = OptimisticLockException.class,
           maxAttempts = 5,
           backoff = @Backoff(delay = 50, multiplier = 2))
// Or: switch to pessimistic locking + connection-level queueing
```

---

**Silent Data Loss (Missing retry implementation)**

Symptom: `OptimisticLockException` logged but no retry. Update silently discarded.

Fix: Implement retry logic — use `@Retryable` (Spring Retry), manual retry loop, or return conflict to the caller to decide.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `CAS (Compare-And-Swap)` — the in-memory implementation mechanism for optimistic locking
- `StampedLock` — Java's thread-level optimistic locking with validation

**Builds On This (learn these next):**
- Database Fundamentals → Isolation Levels — the database-level concepts that optimistic locking pairs with

**Alternatives / Comparisons:**
- `CAS` — the hardware mechanism underlying optimistic locking
- Pessimistic locking — the complement strategy; use when conflicts are frequent

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Read without lock, validate at commit,    │
│              │ retry on conflict                         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Pessimistic locks add overhead even when  │
│ SOLVES       │ conflicts are rare (read-heavy workloads) │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Fast when conflicts are rare.             │
│              │ Degrades under high write contention.     │
│              │ Always implement retry logic.             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Catalogs, reads >> writes, distributed    │
│              │ scenarios where lock is expensive         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ High concurrent writes to same record     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Read free, verify before commit,         │
│              │  retry if stale"                          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Executor → ExecutorService →              │
│              │ ConcurrentHashMap                         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** JPA `@Version` with `OptimisticLockException` handling is a common pattern. A service calls `decrementStock()` in a transaction, catches `OptimisticLockException`, and retries 3 times. Under a Black Friday flash sale with 10,000 concurrent users trying to buy the last ticket simultaneously: trace how many `UPDATE` statements are executed against the database per successful purchase, calculate the maximum number of retries across all 10,000 transactions, explain why 9,999 of those transactions must fail (not just retry once), and describe the exponential backoff strategy that prevents the database from being overwhelmed by simultaneous retries.

**Q2.** Optimistic locking in distributed systems extends to multi-node scenarios. A distributed cache (Redis) uses `WATCH + MULTI + EXEC` (Redis optimistic transaction) as the equivalent of JPA `@Version`. Explain: how `WATCH` sets up the optimistic version check, what triggers an `EXEC` failure, why this is semantically equivalent to a CAS operation, and what additional challenge arises in a Redis Cluster (multiple shards) when the optimistic transaction spans keys on different nodes — and why this forces you to use a different strategy entirely.

