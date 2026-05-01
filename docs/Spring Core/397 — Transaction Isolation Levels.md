---
layout: default
title: "Transaction Isolation Levels"
parent: "Spring Core"
nav_order: 397
permalink: /spring/transaction-isolation-levels/
number: "397"
category: Spring Core
difficulty: ★★★
depends_on: "@Transactional, Transaction Propagation"
used_by: "@Transactional, Spring Data JPA, HikariCP"
tags: #advanced, #spring, #database, #concurrency, #deep-dive
---

# 397 — Transaction Isolation Levels

`#advanced` `#spring` `#database` `#concurrency` `#deep-dive`

⚡ TL;DR — **Isolation levels** control what a transaction can see from concurrent uncommitted or committed changes. Higher isolation prevents more anomalies but increases lock contention. Spring sets the isolation level via `@Transactional(isolation = Isolation.READ_COMMITTED)` on the JDBC Connection.

| #397            | Category: Spring Core                     | Difficulty: ★★★ |
| :-------------- | :---------------------------------------- | :-------------- |
| **Depends on:** | @Transactional, Transaction Propagation   |                 |
| **Used by:**    | @Transactional, Spring Data JPA, HikariCP |                 |

---

### 📘 Textbook Definition

**Isolation levels** define how and when changes made by one transaction become visible to other concurrent transactions. The SQL standard (ISO/IEC 9075) defines four isolation levels in order of increasing isolation: **READ_UNCOMMITTED** — a transaction can read data modified but not yet committed by another transaction (dirty reads allowed); **READ_COMMITTED** — a transaction can only read committed data, but repeated reads within the same transaction may return different values if another transaction commits between them (non-repeatable reads allowed); **REPEATABLE_READ** — a transaction reads the same data for the same query throughout its lifetime, even if another transaction commits a change; and **SERIALIZABLE** — transactions execute as if they are the only ones running (no phantom reads, full serializability). Spring maps these to `@Transactional(isolation = Isolation.X)`, which calls `Connection.setTransactionIsolation(int)` before the transaction begins. `Isolation.DEFAULT` uses the database's default (typically `READ_COMMITTED` for PostgreSQL/MySQL, `READ_COMMITTED` for Oracle, `READ_COMMITTED` for SQL Server). Note: `REPEATABLE_READ` is MySQL InnoDB's default; PostgreSQL implements `REPEATABLE_READ` as Snapshot Isolation (MVCC-based, not lock-based).

---

### 🟢 Simple Definition (Easy)

Isolation levels decide: "can my transaction see changes that another transaction is currently making or has just made?" Lower isolation = more visibility = more anomalies. Higher isolation = less visibility = slower due to locks.

---

### 🔵 Simple Definition (Elaborated)

Imagine two bank tellers accessing the same account simultaneously. Without isolation, Teller A could see Teller B's in-progress transfer before it is finalised — and make decisions based on money that might be rolled back. `READ_COMMITTED` stops Teller A from seeing Teller B's uncommitted changes, but if Teller A reads the balance twice, it might get different values if Teller B committed between reads. `REPEATABLE_READ` guarantees Teller A gets the same balance both times within one transaction. `SERIALIZABLE` makes it appear as if only one teller works at a time. Each level trades concurrency (speed) for correctness.

---

### 🔩 First Principles Explanation

**The four anomalies and which isolation levels prevent them:**

```
ANOMALY         │ DESCRIPTION                           │ READ_UNCOMMITTED │ READ_COMMITTED │ REPEATABLE_READ │ SERIALIZABLE
────────────────┼───────────────────────────────────────┼──────────────────┼────────────────┼─────────────────┼────────────
Dirty Read      │ Read uncommitted data from another tx │ ✗ POSSIBLE       │ ✓ Prevented    │ ✓ Prevented     │ ✓ Prevented
Non-Repeatable  │ Same row read twice → different values │ ✗ POSSIBLE       │ ✗ POSSIBLE     │ ✓ Prevented     │ ✓ Prevented
Read            │ (another tx committed between reads)  │                  │                │                 │
Phantom Read    │ Same query twice → different row set  │ ✗ POSSIBLE       │ ✗ POSSIBLE     │ ✗ POSSIBLE*     │ ✓ Prevented
                │ (another tx inserted/deleted rows)    │                  │                │ *varies by DB   │
Lost Update     │ Two txns read-then-write same row     │ ✗ POSSIBLE       │ ✗ POSSIBLE     │ ✓ Prevented     │ ✓ Prevented
                │ → one overwrite is lost               │                  │                │ (with locking)  │
```

**Concrete scenario for each anomaly:**

```
T1 and T2 both active concurrently:

DIRTY READ:
  T2: UPDATE account SET balance = 1000 WHERE id=1  -- not committed yet
  T1: SELECT balance FROM account WHERE id=1 → reads 1000 (T2's uncommitted change!)
  T2: ROLLBACK
  T1: Made decision based on 1000, but actual balance is still 500 → ERROR

NON-REPEATABLE READ (with READ_COMMITTED):
  T1: SELECT balance FROM account WHERE id=1 → 500
  T2: UPDATE account SET balance = 1000 WHERE id=1; COMMIT
  T1: SELECT balance FROM account WHERE id=1 → 1000  (different value!)
  T1: balance changed within same transaction → inconsistency in T1's logic

PHANTOM READ (with REPEATABLE_READ, MySQL style):
  T1: SELECT COUNT(*) FROM orders WHERE status='PENDING' → 5
  T2: INSERT INTO orders (status) VALUES ('PENDING'); COMMIT
  T1: SELECT COUNT(*) FROM orders WHERE status='PENDING' → 6 (new row appeared!)
  T1: Row set changed within same transaction → T1 cannot rely on stable counts

LOST UPDATE (with READ_COMMITTED):
  T1: SELECT stock FROM inventory WHERE id=1 → 10
  T2: SELECT stock FROM inventory WHERE id=1 → 10
  T1: UPDATE inventory SET stock = 10-1 = 9 WHERE id=1; COMMIT
  T2: UPDATE inventory SET stock = 10-1 = 9 WHERE id=1; COMMIT  ← overwrites T1!
  Result: stock=9 but TWO items sold → stock should be 8
```

**How Spring sets isolation on the Connection:**

```java
// TransactionAspectSupport / AbstractPlatformTransactionManager:
Connection conn = dataSource.getConnection();
conn.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED); // JDBC call
conn.setAutoCommit(false); // begin transaction
// Bind conn to TransactionSynchronizationManager for this thread

// @Transactional(isolation = Isolation.READ_COMMITTED) maps to:
// Connection.TRANSACTION_READ_COMMITTED = 2
// Connection.TRANSACTION_REPEATABLE_READ = 4
// Connection.TRANSACTION_SERIALIZABLE = 8
// Connection.TRANSACTION_READ_UNCOMMITTED = 1
// Isolation.DEFAULT = -1 → don't call setTransactionIsolation, use DB default
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT configurable isolation levels:

What breaks without it:

1. Financial systems using dirty reads would make transfer decisions on uncommitted (possibly rolled-back) data — phantom money.
2. Reporting queries running concurrently with writes would see inconsistent snapshots.
3. E-commerce inventory systems without REPEATABLE_READ or SERIALIZABLE would oversell stock (lost update anomaly).
4. No way to trade off consistency vs performance — all queries would use the same isolation.

WITH isolation levels:
→ Reporting queries use `READ_COMMITTED` for high concurrency and minimal locking.
→ Financial transfers use `SERIALIZABLE` for strict correctness guarantees.
→ Read-heavy dashboards use `READ_UNCOMMITTED` for maximum throughput (acceptable for approximate stats).
→ Different operations in the same app use different isolation levels via `@Transactional(isolation = ...)`.

---

### 🧠 Mental Model / Analogy

> Think of isolation levels as privacy screens on a whiteboard in a shared office. `READ_UNCOMMITTED` = no screen — everyone sees your half-written notes instantly, even before you decide to keep them. `READ_COMMITTED` = screen while writing, removed when done — others see your notes only once you are satisfied and accept them. `REPEATABLE_READ` = snapshot photo — others took a photo of the whiteboard when they started; they see only that snapshot for their entire session, regardless of what you write. `SERIALIZABLE` = only one person in the room at a time — absolute consistency, no concurrency.

"Half-written notes" = uncommitted transaction data
"Screen removed on commit" = READ_COMMITTED (see only committed)
"Snapshot photo at start" = REPEATABLE_READ / MVCC snapshot
"One person at a time" = SERIALIZABLE (sequential execution)

---

### ⚙️ How It Works (Mechanism)

**MVCC (Multi-Version Concurrency Control) — PostgreSQL's implementation:**

```
PostgreSQL uses MVCC for isolation levels:
  • Each row has a creation transaction ID (xmin) and deletion transaction ID (xmax)
  • No read locks needed — readers see a consistent snapshot of committed data
  • REPEATABLE_READ: snapshot taken at first statement in transaction
  • READ_COMMITTED: snapshot taken at each statement (fresh read per query)

Example (PostgreSQL REPEATABLE_READ with MVCC):
  T1 starts: takes snapshot at transaction start (sees all rows committed before T1 began)
  T2: INSERT row, COMMIT
  T1: SELECT * → still sees old snapshot (row not visible — committed AFTER T1 started)
  T1: SELECT * again → same result (snapshot unchanged throughout T1)

Comparison to lock-based (MySQL InnoDB REPEATABLE_READ):
  MySQL uses "gap locks" and "next-key locks" for range queries
  PostgreSQL uses MVCC snapshots — no gap locks for reads, higher concurrency
```

**Spring configuration:**

```java
@Transactional(isolation = Isolation.REPEATABLE_READ, readOnly = true)
public AccountSummary generateMonthlyReport(Long accountId, YearMonth month) {
    // Consistent snapshot throughout the reporting method
    // No other committed transactions will change what we see
    BigDecimal openingBalance = accountRepo.getBalanceAt(accountId, month.atDay(1));
    List<Transaction> txns = txnRepo.findInMonth(accountId, month);
    BigDecimal closingBalance = accountRepo.getBalanceAt(accountId, month.atEndOfMonth());
    return AccountSummary.build(openingBalance, txns, closingBalance);
    // All three queries are internally consistent — no non-repeatable reads
}
```

---

### 🔄 How It Connects (Mini-Map)

```
@Transactional
(isolation = Isolation.X)
        │
        ▼
Transaction Isolation Levels  ◄──── (you are here)
(controls concurrent visibility anomalies)
        │
        ▼
Database JDBC Connection.setTransactionIsolation(int)
        │
        ├── READ_UNCOMMITTED → dirty reads possible (avoid for production)
        ├── READ_COMMITTED   → default for most DBs, no dirty reads
        ├── REPEATABLE_READ  → consistent reads, possible phantom reads
        └── SERIALIZABLE     → strictest, slowest, fully isolated
        │
        ▼
Database engine:
  Lock-based (MySQL InnoDB) → shared/exclusive locks, gap locks
  MVCC-based (PostgreSQL)   → version snapshots, no read locks
```

---

### 💻 Code Example

**Isolation per use-case in a financial application:**

```java
@Service
class AccountService {

    // SERIALIZABLE: prevent lost updates when both tellers transfer simultaneously
    @Transactional(isolation = Isolation.SERIALIZABLE)
    public void transfer(Long from, Long to, BigDecimal amount) {
        Account source = accountRepo.findByIdForUpdate(from); // SELECT FOR UPDATE
        Account target = accountRepo.findByIdForUpdate(to);
        if (source.getBalance().compareTo(amount) < 0) {
            throw new InsufficientFundsException(from);
        }
        source.debit(amount);
        target.credit(amount);
        accountRepo.save(source);
        accountRepo.save(target);
    }

    // REPEATABLE_READ: consistent snapshot for monthly statement
    @Transactional(isolation = Isolation.REPEATABLE_READ, readOnly = true)
    public Statement generateStatement(Long accountId, Month month) {
        return Statement.build(
            accountRepo.getBalanceAtStartOfMonth(accountId, month),
            txnRepo.findAllInMonth(accountId, month),
            accountRepo.getBalanceAtEndOfMonth(accountId, month)
        );
    }

    // READ_COMMITTED: general reads — see committed data, max concurrency
    @Transactional(isolation = Isolation.READ_COMMITTED, readOnly = true)
    public BigDecimal getCurrentBalance(Long accountId) {
        return accountRepo.findById(accountId).map(Account::getBalance)
            .orElseThrow(() -> new AccountNotFoundException(accountId));
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                             | Reality                                                                                                                                                                                                                                                                                 |
| ------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Higher isolation levels always mean more locks                            | PostgreSQL's MVCC-based implementation uses snapshots for `READ_COMMITTED` and `REPEATABLE_READ` — no read locks are acquired. Lock contention increases mainly for write conflicts and only strictly at `SERIALIZABLE`. MySQL InnoDB does use more aggressive locking at higher levels |
| `Isolation.DEFAULT` means `READ_COMMITTED`                                | `Isolation.DEFAULT` tells Spring NOT to call `setTransactionIsolation()` — the database uses its own configured default. PostgreSQL default = `READ_COMMITTED`; MySQL InnoDB default = `REPEATABLE_READ`. Never assume `DEFAULT` means `READ_COMMITTED` across all databases            |
| Setting `SERIALIZABLE` prevents all concurrency issues in the application | `SERIALIZABLE` prevents SQL-level anomalies, but application-level race conditions (reading data in one transaction, passing it to another request, writing it in a third) are not covered by isolation levels — those require optimistic locking or explicit application locking       |
| `READ_UNCOMMITTED` is useful for better performance in most applications  | `READ_UNCOMMITTED` allows reading uncommitted (potentially rolled-back) data. It is only appropriate for rough analytics where approximate data is acceptable. For any business-critical read, `READ_UNCOMMITTED` can return data that never existed                                    |

---

### 🔥 Pitfalls in Production

**Isolation level not supported — silently falls back to database default**

```java
// PostgreSQL does NOT support READ_UNCOMMITTED
// Setting it does NOT cause an error — PostgreSQL silently uses READ_COMMITTED
@Transactional(isolation = Isolation.READ_UNCOMMITTED)
public List<Order> getApproximateOrders() {
    // Developer expected dirty reads for "fast approximate counts"
    // PostgreSQL gave READ_COMMITTED behaviour instead
    // Code "works" but developer's mental model is wrong
    // → Misguided performance assumptions about dirty reads not applying
}

// Always check database support for the isolation level you configure.
// And document WHY a non-default isolation level is used.
```

---

### 🔗 Related Keywords

- `@Transactional` — declares isolation level as an attribute; applied via `Connection.setTransactionIsolation()`
- `Transaction Propagation` — the other key `@Transactional` attribute; controls joining vs new transaction
- `HikariCP` — connection pool that returns connections with potentially modified isolation state; HikariCP resets isolation on return to pool (configurable)
- `N+1 Problem` — often addressed in the same `@Transactional` context via fetch joins

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ LEVEL            │ Dirty │ Non-Rep │ Phantom │ Perf     │
├──────────────────┼───────┼─────────┼─────────┼──────────┤
│ READ_UNCOMMITTED │  ✗    │  ✗      │  ✗      │ Fastest  │
│ READ_COMMITTED   │  ✓    │  ✗      │  ✗      │ Fast     │
│ REPEATABLE_READ  │  ✓    │  ✓      │  ✗*     │ Medium   │
│ SERIALIZABLE     │  ✓    │  ✓      │  ✓      │ Slowest  │
├──────────────────┴───────┴─────────┴─────────┴──────────┤
│ * REPEATABLE_READ phantom prevention: depends on DB      │
│   PostgreSQL MVCC: phantoms prevented                    │
│   MySQL InnoDB: gap locks prevent phantoms               │
├──────────────────────────────────────────────────────────┤
│ DB DEFAULTS: PostgreSQL=READ_COMMITTED                   │
│              MySQL InnoDB=REPEATABLE_READ                │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** PostgreSQL implements `REPEATABLE_READ` using MVCC snapshots — no read locks are acquired, yet it prevents non-repeatable reads. But MySQL InnoDB implements `REPEATABLE_READ` using shared read locks AND gap locks. For a high-throughput `REPEATABLE_READ` read-only transaction running concurrently with many writes: describe why PostgreSQL's implementation scales better (writers don't block readers), but explain the one case where PostgreSQL's MVCC snapshot can cause a transaction to fail that MySQL would not: the "serialization failure" (ERROR 40001) on write-write conflicts when using `SERIALIZABLE`. Is there an equivalent risk in `REPEATABLE_READ` in PostgreSQL?

**Q2.** `HikariCP` (the default Spring Boot connection pool) resets `Connection.setTransactionIsolation()` when a connection is returned to the pool, restoring it to the pool's configured default (`dataSourceProperties.transactionIsolation`). Describe the threading risk if isolation reset is NOT implemented: if a thread using `SERIALIZABLE` returns the connection to the pool, and the next thread picks it up expecting `READ_COMMITTED`, what is the observable behaviour? Then explain `HikariCP.setTransactionIsolation(String)` as a global pool default vs the per-transaction `@Transactional(isolation = ...)` override — which takes precedence and when?
