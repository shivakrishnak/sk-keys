---
layout: default
title: "Transaction Isolation Levels"
parent: "Spring & Spring Boot"
nav_order: 129
permalink: /spring/transaction-isolation-levels/
number: "129"
category: Spring & Spring Boot
difficulty: ★★★
depends_on: "@Transactional, ACID, Databases, Concurrent Transactions"
used_by: "Read anomaly prevention, Spring Data JPA, @Transactional isolation param"
tags: #java, #spring, #database, #advanced, #deep-dive, #concurrency
---

# 129 — Transaction Isolation Levels

`#java` `#spring` `#database` `#advanced` `#deep-dive` `#concurrency`

⚡ TL;DR — Controls what data a transaction can see from other concurrent transactions — trading data consistency for concurrency performance at four progressively stricter levels.

| #129 | Category: Spring & Spring Boot | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | @Transactional, ACID, Databases, Concurrent Transactions | |
| **Used by:** | Read anomaly prevention, Spring Data JPA, @Transactional isolation param | |

---

### 📘 Textbook Definition

**Transaction Isolation** defines the degree to which one transaction is isolated from others that run concurrently. The SQL standard defines four levels — `READ_UNCOMMITTED`, `READ_COMMITTED`, `REPEATABLE_READ`, and `SERIALIZABLE` — each preventing a different set of read anomalies: **dirty reads** (reading uncommitted data), **non-repeatable reads** (same row reads differently in same transaction), and **phantom reads** (a range query returns different rows on repeat). In Spring, isolation is set via `@Transactional(isolation = Isolation.READ_COMMITTED)`. The default is `Isolation.DEFAULT`, which defers to the database's default (PostgreSQL: READ_COMMITTED, MySQL InnoDB: REPEATABLE_READ).

---

### 🟢 Simple Definition (Easy)

Isolation level answers: "While my transaction is running, can I see changes other transactions are making?" Higher isolation = more protection from weird data, but slower because more locking.

---

### 🔵 Simple Definition (Elaborated)

When multiple transactions run at the same time on the same database, they can interfere with each other's reads in three distinct ways — dirty reads, non-repeatable reads, and phantom reads. Each isolation level is a trade-off: low isolation allows more concurrency (better performance) but exposes your transaction to stale or changing data; high isolation gives you a consistent view of the database but reduces throughput because transactions must wait for each other. In practice, READ_COMMITTED (the PostgreSQL default) prevents the most dangerous anomaly (dirty reads) while keeping concurrency high.

---

### 🔩 First Principles Explanation

**Three read anomalies — the problems isolation solves:**

```
DIRTY READ:
  TX1: UPDATE users SET balance=500 WHERE id=1  (not committed)
  TX2: SELECT balance FROM users WHERE id=1 → reads 500 (dirty!)
  TX1: ROLLBACK
  TX2 read data that never actually existed

NON-REPEATABLE READ:
  TX1: SELECT balance FROM users WHERE id=1 → 100
  TX2: UPDATE users SET balance=500 WHERE id=1; COMMIT
  TX1: SELECT balance FROM users WHERE id=1 → 500 (changed!)
  Same query, same transaction, different result

PHANTOM READ:
  TX1: SELECT COUNT(*) FROM orders WHERE status='PENDING' → 5
  TX2: INSERT INTO orders (status='PENDING'); COMMIT
  TX1: SELECT COUNT(*) FROM orders WHERE status='PENDING' → 6
  Same range query, different rows returned
```

**The four isolation levels and what they prevent:**

```
┌────────────────────────────────────────────────────────────┐
│  LEVEL             DIRTY  NON-REP  PHANTOM                 │
│                    READ   READ     READ                     │
├────────────────────────────────────────────────────────────┤
│  READ_UNCOMMITTED  ❌     ❌       ❌   (prevents nothing)  │
│  READ_COMMITTED    ✅     ❌       ❌   (PG/Oracle default)  │
│  REPEATABLE_READ   ✅     ✅       ❌   (MySQL default)      │
│  SERIALIZABLE      ✅     ✅       ✅   (full protection)    │
└────────────────────────────────────────────────────────────┘
```

---

### ❓ Why Does This Exist (Why Before What)

**Without isolation levels:**

```
Without isolation control:

  Full isolation (always SERIALIZABLE):
    All transactions run as if sequential
    → 1/10th throughput in high-concurrency apps
    → Deadlocks more frequent
    → Reporting queries block all writes

  No isolation (READ_UNCOMMITTED):
    Financial calculations on dirty data:
    TX1 debits account (not committed)
    TX2 reads debited balance as new balance
    TX1 rolls back → TX2 made decision on phantom data
    → Silent data corruption
```

**WITH isolation level control:**

```
→ READ_COMMITTED (most apps): block dirty reads,
  allow high concurrency, acceptable for OLTP
→ REPEATABLE_READ: consistent snapshot for reports
  (run same query multiple times, same results)
→ SERIALIZABLE: financial ledger, inventory alloc
  where phantom reads would cause double-booking
→ READ_UNCOMMITTED: only for approximate stats/counts
  (never for financial data)
→ PostgreSQL MVCC: READ_COMMITTED essentially free
  (uses snapshots, not locks for reads)
```

---

### 🧠 Mental Model / Analogy

> Isolation levels are like **levels of soundproofing between hotel rooms**. READ_UNCOMMITTED: thin cardboard walls — you hear everything neighbours do, even conversations they'll take back (dirty reads). READ_COMMITTED: regular walls — you only hear what's finalised (committed). REPEATABLE_READ: good soundproofing — what you heard at check-in is what you'll hear all night (stable reads). SERIALIZABLE: complete sensory isolation booth — you have no idea what's happening next door at all, but you wait longer for breakfast.

"Hearing uncommitted conversation" = dirty read (not yet committed)
"Hear only what's finalised" = READ_COMMITTED (only committed data)
"Heard same music all night" = REPEATABLE_READ (stable snapshot)
"Complete isolation booth" = SERIALIZABLE (serial execution)
"Waiting longer for breakfast" = performance cost of high isolation

---

### ⚙️ How It Works (Mechanism)

**Setting isolation in Spring:**

```java
// Use database default (READ_COMMITTED on PostgreSQL)
@Transactional
public void normalOperation() { ... }

// Override for this specific method
@Transactional(isolation = Isolation.REPEATABLE_READ)
public ReportData generateReport() {
  // All reads in this transaction see a consistent snapshot
  // No non-repeatable reads even on long-running reports
}

@Transactional(isolation = Isolation.SERIALIZABLE)
public boolean reserveSeat(long seatId) {
  // Full concurrency control
  // Prevents double-booking under parallel requests
  boolean available = seatRepo.isAvailable(seatId);
  if (available) seatRepo.book(seatId);
  return available;
}

// READ_UNCOMMITTED (rare in production):
@Transactional(
    isolation = Isolation.READ_UNCOMMITTED,
    readOnly   = true)
public long approximateCount() {
  // Dirty read acceptable for a rough COUNT(*)
  // Avoids blocking on long-running writes
  return orderRepo.count();
}
```

**PostgreSQL MVCC — why READ_COMMITTED is "almost free":**

```
PostgreSQL uses Multi-Version Concurrency Control (MVCC):
  Each row has multiple versions (xmin, xmax)
  Readers see the latest COMMITTED version as of TX start
  Writers create a new version — don't block readers
  → READ_COMMITTED: readers NEVER block writers
  → Writers NEVER block readers
  → Only write-write conflicts cause locking
  → Most production apps can use READ_COMMITTED safely
```

---

### 🔄 How It Connects (Mini-Map)

```
Concurrent transactions on same database
        ↓
  READ ANOMALIES possible:
  dirty / non-repeatable / phantom reads
        ↓
  TRANSACTION ISOLATION (129)  ← you are here
  (@Transactional(isolation=...))
        ↓
  Database implements via:
  Locking (row/page/table locks) — MySQL, SQL Server
  MVCC (snapshot versions) — PostgreSQL, Oracle
        ↓
  Trade-off: isolation vs concurrency
        ↓
  Related: Transaction Propagation (128)
  (boundary control, orthogonal to isolation)
```

---

### 💻 Code Example

**Example 1 — Non-repeatable read scenario and fix:**

```java
// PROBLEM: balance report runs two queries under load
@Transactional
// Default: READ_COMMITTED — non-repeatable read possible
public BalanceReport generateBalance() {
  BigDecimal totalDebit  = txRepo.sumDebits();
  // Another transaction commits between these two reads!
  BigDecimal totalCredit = txRepo.sumCredits();
  // balance = totalDebit - totalCredit could be incorrect
  // because totals are from different points in time
}

// FIX: consistent snapshot with REPEATABLE_READ
@Transactional(isolation = Isolation.REPEATABLE_READ)
public BalanceReport generateBalance() {
  BigDecimal totalDebit  = txRepo.sumDebits();
  BigDecimal totalCredit = txRepo.sumCredits();
  // Both queries see exact same committed snapshot
  // Non-repeatable reads eliminated
}
```

**Example 2 — Phantom read in seat booking:**

```java
// RACE CONDITION: two concurrent booking requests
// Both check availability → both see available
// Both book → double booking!

// Thread 1:           Thread 2:
// isAvailable(5) = true
//                     isAvailable(5) = true
// book(5)
//                     book(5) ← PHANTOM! both booked seat 5

// FIX: SERIALIZABLE prevents phantom reads
@Transactional(isolation = Isolation.SERIALIZABLE)
public boolean bookSeat(long seatId) {
  if (!seatRepo.isAvailable(seatId)) return false;
  seatRepo.book(seatId);
  return true;
  // Under SERIALIZABLE: one of the concurrent TXs will
  // retry or fail with SerializationFailureException
}
// Or: use optimistic locking (@Version) instead
// → lighter weight than SERIALIZABLE
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| SERIALIZABLE means transactions run one at a time | Modern databases implement SERIALIZABLE via Serializable Snapshot Isolation (SSI) — transactions run concurrently and the DB detects serializability violations, causing retries, not blocking |
| Isolation.DEFAULT means READ_COMMITTED everywhere | Isolation.DEFAULT defers to the database's default. PostgreSQL: READ_COMMITTED. MySQL InnoDB: REPEATABLE_READ. Different DBs, different defaults |
| Higher isolation always solves concurrency problems | SERIALIZABLE prevents phantoms but doesn't prevent application-level race conditions outside the database (e.g. two API calls, each starting their own transaction, checking stock in sequence) |
| READ_COMMITTED prevents all dirty data issues | READ_COMMITTED prevents reading uncommitted changes (dirty reads) but DOES allow non-repeatable reads and phantom reads within a transaction |

---

### 🔥 Pitfalls in Production

**1. Using SERIALIZABLE without retry logic**

```java
// BAD: SERIALIZABLE without catching serialisation failures
@Transactional(isolation = Isolation.SERIALIZABLE)
public void criticalOperation() {
  // Under high concurrency, PostgreSQL may throw:
  // PSQLException: ERROR: could not serialize access
  // due to concurrent update
  // → HTTP 500 to the user!
}

// GOOD: retry on SerializationFailureException
@Retryable(value = {SerializationFailureException.class},
           maxAttempts = 3, backoff = @Backoff(100))
@Transactional(isolation = Isolation.SERIALIZABLE)
public void criticalOperation() { ... }
```

**2. Mixing isolation levels via nested transactions**

```java
// BAD: REPEATABLE_READ outer calls READ_COMMITTED inner
// The inner's READ_COMMITTED does NOT apply — it joins
// the outer REPEATABLE_READ transaction (REQUIRED propagation)
@Transactional(isolation = Isolation.REPEATABLE_READ)
public void outer() {
  inner(); // inner joins outer's TX, uses REPEATABLE_READ!
}

@Transactional(isolation = Isolation.READ_COMMITTED)
public void inner() {
  // READ_COMMITTED ignored — inherits REPEATABLE_READ from outer
}
// Isolation level of the FIRST transaction wins for joined TXs
// Use REQUIRES_NEW to truly apply a different isolation level
```

---

### 🔗 Related Keywords

- `@Transactional` — where isolation level is specified
- `Transaction Propagation` — controls TX boundaries; isolation is set within those boundaries
- `ACID` — the "I" is isolation; the four levels define the strictness
- `MVCC` — PostgreSQL/Oracle's concurrency mechanism enabling cheap reads
- `Optimistic Locking (@Version)` — alternative to SERIALIZABLE for preventing phantom reads
- `Deadlock` — more likely to occur at higher isolation levels with lock-based implementations

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Controls concurrent data visibility;      │
│              │ 4 levels trade consistency for throughput  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ READ_COMMITTED: most OLTP; REPEATABLE_READ│
│              │ for reports; SERIALIZABLE for reserve ops │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Don't use SERIALIZABLE without retry;     │
│              │ don't assume nested TX inherits your level │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Isolation is soundproofing between rooms  │
│              │  — thicker walls, more peace, more cost." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ N+1 Problem (130) → HikariCP (132) →      │
│              │ ACID → Optimistic Locking                 │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** PostgreSQL implements `REPEATABLE_READ` using snapshot isolation (MVCC), not shared lock acquisition. Explain in detail what a "snapshot" means in PostgreSQL's context — at what point in time the snapshot is taken, how `xmin`/`xmax` transaction IDs are used to determine row visibility, and why a long-running REPEATABLE_READ transaction can experience "transaction ID wraparound" vacuum pressure that causes operational problems in production.

**Q2.** Spring's `@Transactional(isolation = Isolation.REPEATABLE_READ)` sets the isolation AT THE JDBC connection level (`connection.setTransactionIsolation()`). In a connection pool (HikariCP), connections are reused across transactions. Explain the specific bug that occurs when a REPEATABLE_READ transaction ends and its connection is returned to the pool — if HikariCP doesn't reset the isolation level — and the next transaction that borrows that connection expects READ_COMMITTED. Describe how HikariCP's `connection-test-query` and `isolateInternalQueries` settings relate to this.

