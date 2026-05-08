---
layout: default
title: "Transaction Isolation Levels"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 45
permalink: /spring/transaction-isolation-levels/
id: SPR-045
category: Spring Core
difficulty: ★★★
depends_on: "@Transactional, Transaction Propagation, Database Fundamentals"
used_by: Spring Data JPA, JDBC, JTA, Concurrent Systems
related: "@Transactional, Transaction Propagation, N+1 Problem, Optimistic Locking, Pessimistic Locking"
tags:
  - spring
  - database
  - advanced
  - transactions
  - concurrency
---

# SPR-045 - Transaction Isolation Levels

⚡ TL;DR - Isolation levels define how much one transaction can "see" the uncommitted or concurrent changes of other transactions - from READ_UNCOMMITTED (see everything, fastest) to SERIALIZABLE (see nothing concurrent, slowest) - a trade-off between data consistency and throughput.

| #397            | Category: Spring Core                                                                         | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | @Transactional, Transaction Propagation, Database Fundamentals                                |                 |
| **Used by:**    | Spring Data JPA, JDBC, JTA, Concurrent Systems                                                |                 |
| **Related:**    | @Transactional, Transaction Propagation, N+1 Problem, Optimistic Locking, Pessimistic Locking |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Two users simultaneously read an account balance, both see $1000, both add $500, both write back $1500. The correct result should be $2000. This is the **lost update** problem. Or: User A reads a record, User B deletes it, User A reads again - the record vanished. This is a **non-repeatable read**. Without isolation, concurrent transactions corrupt each other's data. With full isolation, every transaction runs as if it's alone - but performance collapses because every operation blocks every other.

**THE INVENTION MOMENT:**
"Isolation levels are a dial between 'completely isolated and slow' and 'completely concurrent and corrupt' - you choose where on the dial your application needs to be."

---

### 📘 Textbook Definition

**Transaction isolation levels** (defined in SQL standard ANSI/ISO SQL-92) specify the degree to which the operations in one transaction are isolated from the operations in other concurrent transactions. Spring's `@Transactional(isolation = Isolation.X)` maps to the underlying JDBC `Connection.setTransactionIsolation()` constant. Four SQL anomalies define the isolation level spectrum:

- **Dirty Read**: Reading uncommitted changes of another transaction (wrong)
- **Non-Repeatable Read**: Reading the same row twice gets different values (changed and committed by another tx between reads)
- **Phantom Read**: Re-executing a range query gets different rows (another tx inserted/deleted rows in the range)
- **Lost Update**: Two transactions read-then-write the same row; one update is lost

Spring's `Isolation` enum: `DEFAULT` (DB default), `READ_UNCOMMITTED`, `READ_COMMITTED`, `REPEATABLE_READ`, `SERIALIZABLE`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Isolation levels control visibility: "Can my transaction see your uncommitted changes? Your committed-but-after-my-start changes? Your new rows?"

**One analogy:**

> Imagine a shared whiteboard in a meeting room. READ_UNCOMMITTED = you can see half-erased notes that haven't been confirmed yet (other people's drafts). READ_COMMITTED = you only see notes that have been confirmed (committed), but if you look twice, the notes might have changed between looks. REPEATABLE_READ = once you read a note, it stays consistent for your entire session - but someone might add NEW notes you'll see on a new scan. SERIALIZABLE = your entire transaction runs as if you're the only person in the room.

**One insight:**
Most production databases default to `READ_COMMITTED`. PostgreSQL and MySQL InnoDB default here. Using `SERIALIZABLE` in high-throughput systems is usually a design error - use application-level optimistic locking instead.

---

### 🔩 First Principles Explanation

**THE 4 ANOMALIES:**

**1. Dirty Read** - Reading another transaction's UNCOMMITTED data:

```
TX_A: UPDATE accounts SET balance = 0 WHERE id = 1   (not committed)
TX_B: SELECT balance FROM accounts WHERE id = 1      → reads 0 (dirty!)
TX_A: ROLLBACK  → balance is actually still the original value
TX_B: made a decision based on a value that never existed
```

**2. Non-Repeatable Read** - Same row read twice, different values:

```
TX_A: SELECT balance FROM accounts WHERE id = 1      → 1000
TX_B: UPDATE accounts SET balance = 2000 WHERE id = 1; COMMIT
TX_A: SELECT balance FROM accounts WHERE id = 1      → 2000 (different!)
```

**3. Phantom Read** - Same query range executed twice, different rows:

```
TX_A: SELECT * FROM accounts WHERE balance > 1000    → returns 5 rows
TX_B: INSERT INTO accounts (balance) VALUES (5000); COMMIT
TX_A: SELECT * FROM accounts WHERE balance > 1000    → returns 6 rows! (phantom!)
```

**4. Lost Update** - Two transactions both overwrite the same row:

```
TX_A: SELECT balance FROM accounts WHERE id = 1      → 1000
TX_B: SELECT balance FROM accounts WHERE id = 1      → 1000
TX_A: UPDATE accounts SET balance = 1500 WHERE id = 1; COMMIT
TX_B: UPDATE accounts SET balance = 1500 WHERE id = 1; COMMIT  ← TX_A's +500 lost!
```

**ISOLATION LEVEL PROTECTION TABLE:**

| Level            | Dirty Read | Non-Repeatable Read | Phantom Read | Lost Update |
| ---------------- | ---------- | ------------------- | ------------ | ----------- |
| READ_UNCOMMITTED | Possible   | Possible            | Possible     | Possible    |
| READ_COMMITTED   | Prevented  | Possible            | Possible     | Possible    |
| REPEATABLE_READ  | Prevented  | Prevented           | Possible\*   | Prevented   |
| SERIALIZABLE     | Prevented  | Prevented           | Prevented    | Prevented   |

\*MySQL InnoDB's REPEATABLE_READ also prevents phantom reads via MVCC gap locks.

---

### 🧪 Thought Experiment

**SETUP:**
E-commerce checkout: read current inventory (100 units), reduce by ordered quantity (1 unit), write back (99 units). 100 concurrent customers all want to order 1 unit.

**WITH READ_COMMITTED (default):**
All 100 transactions read "100 units." All 100 transactions write "99 units." Final inventory: 99 instead of 0. You've oversold 99 units. Classic lost update.

**FIX 1 - Pessimistic locking (SELECT FOR UPDATE):**

```sql
SELECT inventory FROM products WHERE id = 1 FOR UPDATE;
-- Other transactions block until this one commits
-- Sequential: 100 → 99 → 98 → ... → 0
-- Correct but serialized - throughput falls
```

**FIX 2 - Optimistic locking (application-level):**

```java
// JPA @Version for optimistic locking
@Entity
public class Product {
    @Version private Long version;
    private int inventory;
}
// First committer wins; others get OptimisticLockException → retry
```

**FIX 3 - Database atomic operation (best for simple case):**

```sql
UPDATE products SET inventory = inventory - 1
WHERE id = 1 AND inventory > 0;
-- Atomic - no read-modify-write cycle needed
```

**THE INSIGHT:**
Isolation levels prevent ANOMALIES but don't eliminate the need for application-level concurrency design. Atomic SQL operations, optimistic locking, and pessimistic locking are the actual tools for correctness. Isolation level SERIALIZABLE is a nuclear option - it prevents everything but destroys throughput.

---

### 🧠 Mental Model / Analogy

> Isolation levels are like different restaurant table booking policies. READ_UNCOMMITTED = you can sit at a table that's still being set up (see dirty work). READ_COMMITTED = you can only sit at a fully ready table, but the menu might change between when you order and when you re-read it. REPEATABLE_READ = once you've read the menu, it stays the same for your entire meal - but the restaurant might add new specials you can now see. SERIALIZABLE = the restaurant serves one customer at a time - perfect consistency, infinite wait.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When multiple users use a database at the same time, their reads and writes can interfere. Isolation levels decide how much one user's "in-progress" work can affect another user's reads. Higher isolation = less interference, but slower. Lower isolation = more interference, but faster.

**Level 2 - How to use it (junior developer):**
Stick with the database default (`READ_COMMITTED` for PostgreSQL/MySQL). Use `REPEATABLE_READ` when your transaction reads data that must stay consistent across multiple reads in the same transaction. Never use `READ_UNCOMMITTED` in production. Avoid `SERIALIZABLE` unless correctness absolutely requires it (financial auditing, critical counters) - and pair it with retry logic.

**Level 3 - How it works (mid-level engineer):**
Most modern databases implement isolation via **MVCC** (Multi-Version Concurrency Control). In MVCC, each write creates a new version of the row rather than overwriting. Readers see a snapshot of the database as of a specific timestamp - without acquiring read locks. This eliminates the dirty read problem without blocking. `READ_COMMITTED` sees a new snapshot for each statement. `REPEATABLE_READ` takes one snapshot at the start of the transaction and sees it consistently. `SERIALIZABLE` uses predicate locking or SSI (Serializable Snapshot Isolation in PostgreSQL) to detect and abort conflicting transactions.

**Level 4 - Why it was designed this way (senior/staff):**
The ANSI SQL-92 standard defines isolation levels in terms of the anomalies they permit - not in terms of implementation. This is why databases differ subtly: MySQL's `REPEATABLE_READ` prevents phantom reads (via gap locks) but the standard says it doesn't have to. PostgreSQL's `REPEATABLE_READ` is effectively snapshot isolation. The standard's four levels map poorly to real-world MVCC databases - Martin Kleppmann (DDIA) identifies additional anomalies like write skew and read skew that the ANSI model doesn't capture. Snapshot Isolation (used by PostgreSQL for READ_COMMITTED and REPEATABLE_READ) prevents more anomalies than the standard requires but still allows write skew. True SERIALIZABLE (PostgreSQL's SSI, since v9.1) prevents write skew by tracking read/write dependencies and aborting conflicting transactions.

---

### ⚙️ How It Works (Mechanism)

**MVCC snapshot timing:**

```
READ_COMMITTED snapshot per STATEMENT:
    T=1: TX_A starts
    T=2: TX_B starts, modifies row X, commits
    T=3: TX_A reads row X → sees TX_B's committed change (new snapshot)
    T=4: TX_A reads row X again → SAME result (TX_B already committed at T=2)
         (Non-repeatable read is possible if TX_B committed between TX_A's two reads)

REPEATABLE_READ snapshot per TRANSACTION:
    T=1: TX_A starts → takes snapshot S1
    T=2: TX_B starts, modifies row X, commits
    T=3: TX_A reads row X → sees S1's version (ignores TX_B's change)
    T=4: TX_A reads row X again → SAME S1 version (repeatable!)
```

**Write skew under Snapshot Isolation (REPEATABLE_READ allows this!):**

```
Invariant: At least one doctor must be on-call
TX_A: reads on_call doctors → 2 (Alice, Bob)
TX_B: reads on_call doctors → 2 (Alice, Bob)
TX_A: sets Alice off_call (1 remaining) → COMMIT
TX_B: sets Bob off_call (1 remaining based on snapshot!) → COMMIT
Result: 0 doctors on call. INVARIANT VIOLATED.
Fix: SERIALIZABLE isolation (PostgreSQL SSI prevents this) or SELECT FOR UPDATE
```

---

### 🔄 The Complete Picture - Bank Transfer with Isolation

```
SCENARIO: Transfer $500 from Account A to Account B
         (Balance A = $1000, Balance B = $500)

CORRECT TRANSFER with READ_COMMITTED:
  TX_1: BEGIN
  TX_1: SELECT balance FROM accounts WHERE id = 'A'  → $1000

  [CONCURRENT: TX_2 reads balance A → also $1000 (committed value)]

  TX_1: UPDATE accounts SET balance = $500 WHERE id = 'A'  (not committed)

  [TX_2 reads balance A with READ_COMMITTED → still sees $1000 committed version]

  TX_1: UPDATE accounts SET balance = $1000 WHERE id = 'B'
  TX_1: COMMIT

  [Now TX_2 reads balance A with READ_COMMITTED → sees $500 (committed)]
  → READ_COMMITTED is consistent for simple bank transfer
  → But: two tx simultaneously doing this without row-level locks = Lost Update!

SOLUTION: SELECT ... FOR UPDATE (pessimistic) or @Version (optimistic)
```

---

### 💻 Code Example

**Example 1 - Setting isolation in @Transactional:**

```java
@Service
public class AccountService {

    // Default: use DB default (usually READ_COMMITTED)
    @Transactional
    public void transfer(Long fromId, Long toId, BigDecimal amount) {
        Account from = accountRepo.findById(fromId).orElseThrow();
        Account to = accountRepo.findById(toId).orElseThrow();
        from.setBalance(from.getBalance().subtract(amount));
        to.setBalance(to.getBalance().add(amount));
        // Problem: concurrent transfer → lost update!
    }

    // REPEATABLE_READ: consistent reads within this transaction
    @Transactional(isolation = Isolation.REPEATABLE_READ)
    public BalanceSnapshot getBalanceSnapshot(Long accountId) {
        // Reads at T1 and T2 within this transaction see same values
        BigDecimal current = accountRepo.getBalance(accountId);
        // ... some processing ...
        BigDecimal stillCurrent = accountRepo.getBalance(accountId);  // same value!
        return new BalanceSnapshot(current, stillCurrent);
    }

    // SERIALIZABLE: highest isolation, lowest throughput
    @Transactional(isolation = Isolation.SERIALIZABLE)
    public void criticalTransfer(Long fromId, Long toId, BigDecimal amount) {
        // Full serialization - use only when absolutely necessary
        // Pair with retry logic for SerializationFailureException
    }
}
```

**Example 2 - Optimistic locking to prevent lost updates (preferred over SERIALIZABLE):**

```java
@Entity
public class Account {
    @Id private Long id;
    private BigDecimal balance;

    @Version  // JPA optimistic locking version column
    private Long version;
}

@Transactional
public void transferOptimistic(Long fromId, Long toId, BigDecimal amount) {
    Account from = accountRepo.findById(fromId).orElseThrow();
    Account to = accountRepo.findById(toId).orElseThrow();

    from.setBalance(from.getBalance().subtract(amount));
    to.setBalance(to.getBalance().add(amount));

    // On commit: UPDATE ... WHERE id=? AND version=?
    // If version changed: OptimisticLockException → caller retries
    // Much better throughput than SERIALIZABLE
}
```

**Example 3 - Pessimistic locking (SELECT FOR UPDATE):**

```java
@Repository
public interface AccountRepository extends JpaRepository<Account, Long> {

    @Lock(LockModeType.PESSIMISTIC_WRITE)  // SELECT ... FOR UPDATE
    @Query("SELECT a FROM Account a WHERE a.id = :id")
    Optional<Account> findByIdForUpdate(@Param("id") Long id);
}

@Transactional
public void transferPessimistic(Long fromId, Long toId, BigDecimal amount) {
    // Locks the row - other transactions wait
    Account from = accountRepo.findByIdForUpdate(fromId).orElseThrow();
    Account to = accountRepo.findByIdForUpdate(toId).orElseThrow();

    from.setBalance(from.getBalance().subtract(amount));
    to.setBalance(to.getBalance().add(amount));
    // Unlock on commit
}
```

---

### ⚖️ Comparison Table

| Level            | Dirty Read  | Non-Repeatable | Phantom | Performance | Typical Use                              |
| ---------------- | ----------- | -------------- | ------- | ----------- | ---------------------------------------- |
| READ_UNCOMMITTED | ✓ (allowed) | ✓              | ✓       | Fastest     | Reports where approximate data is fine   |
| READ_COMMITTED   | ✗           | ✓              | ✓       | Fast        | Most OLTP (default for PG, MySQL)        |
| REPEATABLE_READ  | ✗           | ✗              | ✓\*     | Moderate    | Consistent reads across multiple queries |
| SERIALIZABLE     | ✗           | ✗              | ✗       | Slowest     | Financial audit, critical counters       |

\*MySQL InnoDB prevents phantom reads at REPEATABLE_READ via gap locks.

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                                                                   |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Higher isolation always means safer              | Higher isolation introduces deadlock and serialization failure risk - you need retry logic. More "safe" in data terms but more complex in operational terms.                              |
| SERIALIZABLE prevents all concurrency problems   | SERIALIZABLE prevents the SQL standard anomalies. It may not prevent application-level logic bugs (e.g., checking email uniqueness before insert).                                        |
| READ_COMMITTED is "not safe"                     | READ_COMMITTED is safe for most OLTP workloads when combined with proper locking at the application or ORM level.                                                                         |
| Spring's `Isolation.DEFAULT` uses READ_COMMITTED | DEFAULT uses the database's default - which is typically READ_COMMITTED for PostgreSQL and MySQL, but READ_COMMITTED for Oracle and SQL Server. Always verify for your specific database. |

---

### 🚨 Failure Modes & Diagnosis

**Optimistic lock exception in production**

**Symptom:** `ObjectOptimisticLockingFailureException: Row was updated or deleted by another transaction` intermittently in production.

**Root Cause:** Multiple concurrent transactions updated the same entity. The second committer found a different `@Version` value than it read - optimistic lock conflict.

**Fix:**

```java
// Option 1: Retry the operation
@Retryable(value = OptimisticLockingFailureException.class, maxAttempts = 3)
@Transactional
public void updateEntity(Long id, UpdateRequest req) { ... }

// Option 2: Use pessimistic locking for high-contention entities
// Option 3: Redesign to avoid concurrent writes to the same row
```

---

**Phantom reads in report generation**

**Symptom:** Monthly totals differ between two reads in the same reporting transaction.

**Root Cause:** Using `READ_COMMITTED` - new rows inserted by concurrent transactions are visible on subsequent queries.

**Fix:**

```java
@Transactional(isolation = Isolation.REPEATABLE_READ)
public MonthlyReport generateReport(YearMonth month) {
    // All reads see consistent snapshot for this transaction
    List<Order> orders = orderRepo.findByMonth(month);    // consistent
    BigDecimal total = orderRepo.sumByMonth(month);        // consistent
    // No phantom reads within REPEATABLE_READ
    return new MonthlyReport(orders, total);
}
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `@Transactional` - the annotation where isolation is configured
- `Transaction Propagation` - the other key @Transactional attribute

**Builds On This (learn these next):**

- `N+1 Problem` - JPA performance issue within transactions
- `Optimistic Locking` - application-level concurrency control preferred over SERIALIZABLE
- `Pessimistic Locking` - row-level locking via SELECT FOR UPDATE

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ LEVEL               │ DIRTY │ NON-REPEAT │ PHANTOM │ PERF   │
│─────────────────────│───────│────────────│─────────│────────│
│ READ_UNCOMMITTED    │ Yes   │ Yes        │ Yes     │ Fast   │
│ READ_COMMITTED      │ No    │ Yes        │ Yes     │ Fast   │
│ REPEATABLE_READ     │ No    │ No         │ Yes*    │ Medium │
│ SERIALIZABLE        │ No    │ No         │ No      │ Slow   │
├─────────────────────┴───────┴────────────┴─────────┴────────┤
│ DEFAULT: database default (usually READ_COMMITTED)           │
│ USE: Optimistic locking (@Version) over SERIALIZABLE         │
│ DANGER: SERIALIZABLE → SerializationFailureException risk    │
└─────────────────────────────────────────────────────────────┘
*MySQL InnoDB REPEATABLE_READ also prevents phantom reads via MVCC/gap locks
```

---

### 🧠 Think About This Before We Continue

**Q1.** PostgreSQL implements `REPEATABLE_READ` using MVCC snapshot isolation. In snapshot isolation, each transaction sees the DB state as of when it started. Write skew is still possible (two transactions each read overlapping data and make conflicting writes). How does PostgreSQL's `SERIALIZABLE` (SSI - Serializable Snapshot Isolation) detect and prevent write skew without traditional locking? What data structure does PostgreSQL use internally to track read-write dependencies?

**Q2.** `@Transactional(isolation = Isolation.SERIALIZABLE)` on a Spring method wraps the method's JDBC connection with `SERIALIZABLE` isolation. But what if the transaction includes a JPA first-level cache hit (reading a row that was already loaded in this EntityManager session)? Does the SERIALIZABLE isolation protect against all anomalies even when JPA returns cached objects from memory rather than re-reading from the database?
