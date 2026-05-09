---
id: DST-013
title: Serializability
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-008, DST-012, DST-024
used_by: DST-024, DST-025
related: DST-008, DST-009, DST-012, DST-024, DST-025
tags:
  - distributed
  - consistency
  - database
  - advanced
  - deep-dive
  - algorithm
status: complete
version: 1
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 13
permalink: /distributed-systems/serializability/
---

# DST-013 - Serializability

⚡ TL;DR - Serializability guarantees that the result of executing concurrent database transactions is identical to some sequential (serial) execution of those transactions, preventing anomalies like dirty reads and phantom reads that arise when transactions overlap.

| Metadata        |                                             |     |
| :-------------- | :------------------------------------------ | :-- |
| **Depends on:** | DST-008, DST-012, DST-024                   |     |
| **Used by:**    | DST-024, DST-025                            |     |
| **Related:**    | DST-008, DST-009, DST-012, DST-024, DST-025 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A bank runs two concurrent transactions: T1 transfers $500 from Account A to Account B; T2 calculates the total balance across all accounts for a report. Without serializability, T2 might read Account A AFTER T1 debited it (balance $500 less) but Account B BEFORE T1 credited it ($500 missing from the count). The report shows $500 less than the true total. No error. No exception. Silent inconsistency — a phantom $500 loss from the accounting system's perspective.

**THE BREAKING POINT:**
An airline booking system runs thousands of concurrent reservation transactions. Without serializability, two passengers can book the last seat simultaneously: T1 reads `seats_available = 1`, T2 reads `seats_available = 1`, T1 writes `seats_available = 0` (sold to Alice), T2 writes `seats_available = 0` (sold to Bob). Both succeed. One seat, two bookings. The system has no mechanism to prevent this without serializable isolation.

**THE INVENTION MOMENT:**
Jim Gray formalized serializability in the context of database transactions in the 1970s (IBM Research). The core insight: correctness for transactions means the result is indistinguishable from some serial order. This gave database systems a formal target for their isolation implementations — moving beyond "it seems to work" to "it is provably equivalent to serial execution."

**EVOLUTION:**
1976: Eswaran et al. formalize serializability for databases. 1981: Two-Phase Locking (2PL) proven to ensure serializability. 1995: Snapshot Isolation (Oracle) — provides many serializable properties but NOT full serializability (write skew possible). 1999: Adya's weak isolation definitions formalize anomalies. 2008: Serializable Snapshot Isolation (SSI) — serializable performance close to snapshot isolation. 2012: PostgreSQL 9.1 implements SSI. 2018-2020: CockroachDB, YugabyteDB ship SSI at scale.

---

### 📘 Textbook Definition

**Serializability** is the strongest isolation level for database transactions. A concurrent schedule S (execution history of interleaved transactions) is serializable if it produces the same database state as some serial schedule S' (where transactions execute one at a time, with no interleaving). Serializability prevents all standard transaction anomalies: dirty reads (reading uncommitted data), non-repeatable reads (reading different values in the same transaction), phantom reads (seeing different rows in repeated range queries), and write skew (transactions reading shared state and writing conflicting updates based on stale reads). **Strict Serializability** (or linearizable transactions) additionally requires the serial order to be consistent with real-time transaction order — this is the gold standard implemented by Spanner and CockroachDB.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Serializability means concurrent transactions produce the same result as if they ran one at a time, in some order.

> Serializability is the "table-turn" rule at a restaurant kitchen. Each order might be prepared simultaneously by different chefs. But the final result must be as if orders were taken one at a time — no order sees a half-prepared state of another order. If two orders need the same ingredient, one waits. The customer sees a correct, consistent meal, not a confused mixture of two orders.

**One insight:** Serializability is about multi-operation atomicity across multiple keys. Linearizability is about single-operation recency. A system can be linearizable (every read sees latest write) but not serializable (concurrent transactions can produce incorrect results). Full correctness requires both — and the combination is called Strict Serializability.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Each transaction sees a consistent snapshot of the database as of some point in time.
2. No transaction sees the partial effects of another concurrent transaction.
3. The combined effect of all committed transactions is equivalent to some serial ordering.
4. This serial ordering doesn't need to match real-time order (that's strict serializability).
5. Conflicts (read-write, write-read, write-write on the same data) must be resolved to prevent anomalies.

**DERIVED DESIGN:**
Two classic approaches:

- **Two-Phase Locking (2PL):** Acquire all needed locks before releasing any. Ensures no conflicting concurrent access. Provably serializable. Deadlock-prone.
- **Serializable Snapshot Isolation (SSI):** Start with Snapshot Isolation (each transaction sees a consistent snapshot). Add conflict detection: if a transaction's reads would be affected by another concurrent transaction's writes, abort and retry. Optimistic approach. No deadlocks.

**THE TRADE-OFFS:**
**Gain:** Complete transaction correctness. No anomalies. Application can write sequential logic without explicit locking.
**Cost:** Reduced concurrency (transactions block or abort more than weaker isolation). Higher abort rate under contention (SSI). Write throughput limited by conflict detection overhead.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Preventing concurrent conflicts requires either pessimistic (locks) or optimistic (conflict detection + abort) approaches. Some coordination is irreducible.
**Accidental:** Many databases implement Snapshot Isolation (SI) and advertise it as "serializable" — SI is NOT serializable (write skew is possible). This accidental misrepresentation causes real bugs.

---

### 🧪 Thought Experiment

**SETUP:** A hospital system has a constraint: at least one on-call doctor per shift. Two doctors (Alice and Bob) both try to go off-call simultaneously using two concurrent transactions.

**WITHOUT SERIALIZABILITY (Snapshot Isolation):**
T1 (Alice goes off-call): reads `on_call_count = 2`, checks `count > 1`, proceeds.
T2 (Bob goes off-call): reads `on_call_count = 2`, checks `count > 1`, proceeds.
Both read the snapshot showing 2 on-call doctors. Both proceed.
T1 commits: `on_call_count = 1`.
T2 commits: `on_call_count = 0`.
Result: zero on-call doctors. Constraint violated. This is write skew — both transactions read stale shared state and make conflicting updates.

**WITH SERIALIZABILITY (SSI):**
T1 and T2 both read `on_call_count = 2`. SSI detects: T2's read overlaps with T1's write. One transaction must abort. T2 retries: now sees `on_call_count = 1`. Check `count > 1`: FAILS. T2 correctly cannot go off-call. Constraint preserved.

**THE INSIGHT:** Write skew cannot be prevented by row-level locking on individual rows. It requires either SELECT FOR UPDATE (pessimistic) or SSI (optimistic conflict detection on read sets). This is exactly the scenario that SNAPSHOT ISOLATION misses — causing real production data integrity bugs.

---

### 🧠 Mental Model / Analogy

> Serializability is the "one-at-a-time" guarantee for shared editing. Imagine 10 people editing a shared spreadsheet simultaneously. Serializability is the rule that, no matter how their edits interleave, the final spreadsheet must look exactly as if each person edited it one at a time in some order — nobody's changes are based on a mix of before-and-after states from other editors. If Alice's formula references a value that Bob is currently changing, one of them must wait or retry.

**Mapping:**

- **Spreadsheet** → database
- **Each editor** → a transaction
- **One-at-a-time rule** → serializability
- **Final spreadsheet state** → committed database state
- **Formula referencing changing value** → read-write conflict

Where this analogy breaks down: real spreadsheet editors see each other's changes in real time — this would be non-serializable. Serializable databases hide concurrent changes until they're committed, creating the illusion of sequential editing.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Serializability means: even if thousands of database operations happen at the same time, the final result is exactly as if they happened one after another. No mixed states. No two transactions seeing each other's "in progress" work.

**Level 2 - How to use it (junior developer):**
Use `SERIALIZABLE` isolation level in SQL for critical transactions. In PostgreSQL: `BEGIN; SET TRANSACTION ISOLATION LEVEL SERIALIZABLE; ...`. In Java/Spring: `@Transactional(isolation = Isolation.SERIALIZABLE)`. Be prepared for `SerializationFailureException` (SSI conflict) — always retry serialization failures with exponential backoff. Avoid using `REPEATABLE READ` or `SNAPSHOT` isolation for transactions with write skew risk (the on-call doctor pattern).

**Level 3 - How it works (mid-level engineer):**
SSI (PostgreSQL 9.1+, CockroachDB) works in two phases: (1) Execute as Snapshot Isolation — each transaction reads from a consistent point-in-time snapshot. (2) Track "anti-dependencies": record when transaction T1 reads a version that T2 subsequently modifies. If T2 also reads something T1 modifies, a cycle exists in the dependency graph → one must abort (typically the one that committed later). This dependency cycle detection is the SSI "magic" — it avoids false positives (abort only when cycle actually exists, not on mere conflict).

**Level 4 - Why it was designed this way (senior/staff):**
Classic 2PL (Two-Phase Locking) achieves serializability by preventing conflicts at access time — expensive, deadlock-prone. SSI (Cahill et al. 2008) achieves serializability by allowing optimistic execution and detecting conflict patterns that would result in non-serializable histories. The insight: only certain patterns of anti-dependencies (read-write, write-read, write-write cycles) violate serializability. By tracking only these patterns and aborting when a cycle is complete, SSI achieves serializable correctness with throughput close to Snapshot Isolation. The PostgreSQL implementation uses SIREAD locks (read-set tracking, not blocking) — lightweight markers that track which rows were read without blocking writers.

**Expert Thinking Cues:**

- "Does your transaction read a value and write something else based on it?" → Potential write skew — need SERIALIZABLE.
- "Are you using PostgreSQL REPEATABLE READ?" → NOT serializable. Write skew is still possible.
- "Does your application retry on `SerializationFailureException`?" → Mandatory with SSI. No retry = correctness bug.
- "Does your ORM set isolation level?" → Most ORMs default to READ COMMITTED. Check explicitly.

---

### ⚙️ How It Works (Mechanism)

**Two-Phase Locking (2PL) — pessimistic:**

1. Expanding phase: acquire locks (shared for reads, exclusive for writes) as needed.
2. Shrinking phase: release locks after operation. Once a lock is released, no new locks acquired.
3. Strict 2PL: hold all locks until transaction commit/abort.
4. Guarantee: no conflicting transaction can proceed while locks held → serializable.
5. Deadlock possible: T1 holds lock A, waits for B; T2 holds B, waits for A. Resolution: timeout or deadlock detection + abort.

**Serializable Snapshot Isolation (SSI) — optimistic:**

1. Each transaction gets a snapshot timestamp (SI phase).
2. All reads are from the snapshot (consistent, non-blocking).
3. All writes go to a write buffer (not visible until commit).
4. On commit: check for dependency cycles (SIREAD locks track read sets).
5. If cycle detected (another concurrent transaction's write invalidates this transaction's reads): ABORT.
6. Retry: transaction runs again with a new snapshot.

**Conflict types tracked by SSI:**

- **RW anti-dependency:** T1 reads X; T2 writes X (T1's read depends on pre-T2 state).
- **WR dependency:** T1 writes X; T2 reads X after T1 commits.
- **WW conflict:** T1 writes X; T2 writes X concurrently.
  SSI aborts on: T1 has RW from T2 AND T2 has RW from T1 (dangerous pattern).

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (SSI write skew detection):**

```
T1: Read on_call_count=2, write Alice.oncall=false
T2: Read on_call_count=2, write Bob.oncall=false

SSI tracking:
  T1 reads: {on_call_count, Alice.oncall}
  T2 reads: {on_call_count, Bob.oncall}
  T2 writes: {Bob.oncall} → touches T1's read set?
    → on_call_count is derived from Bob.oncall: YES
  T1 writes: {Alice.oncall} → touches T2's read set?
    → on_call_count is derived from Alice.oncall: YES

  Cycle detected:
  T1 RW← T2 RW← T1 (dangerous pattern)
  ← YOU ARE HERE: SSI aborts T2

T2 retries → reads on_call_count=1 → aborts (count not > 1)
T1 commits: Alice off-call. Bob stays on-call. Constraint preserved.
```

**FAILURE PATH (high-contention abort storm):**
Under heavy write load on a popular row, SSI conflict detection causes many transactions to abort and retry. If retry adds the same conflict: exponential abort storm. System throughput collapses.
Resolution: limit contention through better key distribution (avoid hot rows), use SELECT FOR UPDATE for known conflict points (fall back to 2PL for specific operations).

**WHAT CHANGES AT SCALE:**
Distributed SSI (CockroachDB, Spanner) requires cross-node conflict tracking. SIREAD locks must be replicated or tracked at a central coordinator. At scale, dependency graphs become global — each node must know what other nodes' transactions are reading and writing. CockroachDB uses an optimistic approach with CRDB's timestamp oracle and retry-on-uncertainty.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Distributed transactions under SSI: if T1 spans nodes N1 and N2, conflict detection spans both nodes. N1's SIREAD locks must be visible to N2's conflict checker. This is the scalability challenge — either a global conflict detector (bottleneck) or a distributed tracking protocol (complexity). Spanner avoids this with TrueTime: timestamp-based ordering eliminates most conflicts without explicit tracking.

---

### 💻 Code Example

**BAD - Snapshot Isolation with write skew (on-call doctor):**

```java
// REPEATABLE READ (PostgreSQL default) — NOT serializable
// Write skew IS possible: two doctors can both go off-call
@Transactional(isolation = Isolation.REPEATABLE_READ)
public void goOffCall(String doctorId) {
    int onCallCount = doctorRepo.countOnCallDoctors();
    if (onCallCount <= 1) {
        throw new BusinessException("Last on-call doctor");
    }
    // DANGER: Another transaction may have read the same count
    // and is also about to proceed — write skew possible
    doctorRepo.setOffCall(doctorId);
}
```

**GOOD - Serializable isolation (SSI) with retry:**

```java
// SERIALIZABLE — SSI detects and prevents write skew
@Transactional(isolation = Isolation.SERIALIZABLE)
public void goOffCall(String doctorId) {
    int onCallCount = doctorRepo.countOnCallDoctors();
    if (onCallCount <= 1) {
        throw new BusinessException("Last on-call doctor");
    }
    // SSI will abort if another concurrent transaction
    // also modified the on-call set
    doctorRepo.setOffCall(doctorId);
}

// Service layer: retry on serialization failure
public void goOffCallWithRetry(String doctorId) {
    int maxRetries = 3;
    for (int attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            goOffCall(doctorId);
            return;  // success
        } catch (CannotAcquireLockException |
                 TransactionSystemException e) {
            if (e.getMessage().contains("serialization failure")
                || e.getMessage().contains("40001")) {
                if (attempt == maxRetries) throw e;
                try {
                    Thread.sleep(50 * attempt); // backoff
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt(); throw e;
                }
            } else {
                throw e; // non-serialization error: rethrow
            }
        }
    }
}
```

**How to test / verify correctness:**

```bash
# PostgreSQL: test for write skew with REPEATABLE READ:
# Run two concurrent sessions simultaneously:
# Session 1: BEGIN; SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
# Session 2: BEGIN; SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
# Both: SELECT COUNT(*) FROM doctors WHERE on_call=true;
# Both: UPDATE doctors SET on_call=false WHERE id=?;
# Both: COMMIT;
# If both succeed: write skew confirmed (broken)

# With SERIALIZABLE:
psql -c "BEGIN; SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
SELECT COUNT(*) FROM doctors WHERE on_call=true;
UPDATE doctors SET on_call=false WHERE id='alice';
COMMIT;" &
psql -c "BEGIN; SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
SELECT COUNT(*) FROM doctors WHERE on_call=true;
UPDATE doctors SET on_call=false WHERE id='bob';
COMMIT;" &
wait
# One transaction should fail with: ERROR 40001: serialization failure
```

---

### ⚖️ Comparison Table

| Isolation Level     | Dirty Read | Non-Rep. Read | Phantom | Write Skew | Throughput  |
| :------------------ | :--------- | :------------ | :------ | :--------- | :---------- |
| Read Uncommitted    | YES        | YES           | YES     | YES        | Highest     |
| Read Committed      | No         | YES           | YES     | YES        | High        |
| Repeatable Read     | No         | No            | YES     | YES        | Medium      |
| Snapshot Isolation  | No         | No            | No      | YES        | Medium-High |
| Serializable (SSI)  | No         | No            | No      | No         | Medium      |
| Strict Serializable | No         | No            | No      | No         | Low         |

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                                                                                                                |
| :------------------------------------------------------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "REPEATABLE READ is almost serializable"                | REPEATABLE READ in PostgreSQL is actually Snapshot Isolation. Write skew is possible. It is NOT close to serializable for correctness — the gap is the entire class of write-skew bugs.                                |
| "Snapshot Isolation prevents all anomalies"             | Snapshot Isolation prevents dirty reads, non-repeatable reads, and phantom reads — but NOT write skew. Write skew is a common, subtle, and real production bug under SI.                                               |
| "Serializability means operations happen one at a time" | Serializability only requires that the RESULT is equivalent to some serial order. Actual execution is concurrent — only the outcome must match. Operations run in parallel; the apparent order is what's serializable. |
| "Using transactions gives you serializability"          | Most databases default to READ COMMITTED isolation, not SERIALIZABLE. Using `@Transactional` in Spring doesn't give serializability unless you explicitly set `isolation = Isolation.SERIALIZABLE`.                    |
| "SERIALIZABLE is too slow for production"               | PostgreSQL SSI is typically 10-40% slower than Snapshot Isolation, not 10x slower. For most applications, this is acceptable. The alternative (write skew bugs in production) is far more costly.                      |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Write Skew Under Snapshot Isolation**

**Symptom:** Invariant violated in production. Business rule ("at least one on-call doctor," "account balance >= 0") broken despite individual transactions looking correct. No error thrown, no exception logged.
**Root Cause:** Snapshot Isolation allows write skew. Two transactions read shared state, make decisions based on consistent snapshots, write non-conflicting rows — but the combined effect violates the invariant.
**Diagnostic:**

```sql
-- Check current isolation level:
SHOW transaction_isolation;
-- Check for write skew pattern:
-- Look for transactions that:
--   1. Read an aggregate (COUNT, SUM)
--   2. Write a row based on that aggregate
-- If isolation < SERIALIZABLE: vulnerable to write skew
```

**Fix:**
BAD: Using `REPEATABLE READ` for write-skew-vulnerable transactions.
GOOD: Use `SERIALIZABLE` + retry-on-serialization-failure for all transactions with write skew risk.
**Prevention:** Audit all transactions for write skew pattern (read aggregate → write row). Apply SERIALIZABLE to affected transaction types.

**Failure Mode 2: Abort Storm Under High Contention**

**Symptom:** During peak load, transaction success rate drops from 99% to 40%. Application logs fill with `ERROR 40001: could not serialize access`. Retry logic causes load amplification. System becomes unresponsive.
**Root Cause:** SSI detects many conflicts on a "hot" shared row (e.g., global counter, popular product inventory). Each transaction reads the counter, many abort, retry, read the (now updated) counter, conflict again. Exponential retry storm.
**Diagnostic:**

```sql
-- Check serialization failure rate:
SELECT sum(xact_rollback), sum(conflicts)
FROM pg_stat_database WHERE datname = 'mydb';
-- Check for hot tables/rows:
SELECT schemaname, relname, n_tup_upd, n_tup_hot_upd
FROM pg_stat_user_tables ORDER BY n_tup_upd DESC LIMIT 10;
```

**Fix:**
BAD: Pure SSI on globally contended counters.
GOOD: Use atomic operations (`UPDATE counter SET val=val+1`) instead of read-modify-write. Use `SELECT FOR UPDATE` on the specific contended row (falling back to 2PL for that row). Or: use application-level sharded counters.
**Prevention:** Identify hot rows at design time. Apply targeted locking (not SSI) to globally contended resources.

**Failure Mode 3: Security - TOCTOU (Time-of-Check to Time-of-Use) Under Weak Isolation**

**Symptom:** A financial system checks balance before transfer (check: balance >= amount), but by commit time, another transfer has reduced the balance below zero. Account goes negative despite the check.
**Root Cause:** READ COMMITTED or REPEATABLE READ isolation. The balance check reads the committed value at time T1. Between T1 and commit T2, another transaction deducted funds. The original check is stale.
**Diagnostic:**

```sql
-- Identify TOCTOU-vulnerable code:
-- Look for: SELECT balance FROM accounts WHERE id=?
-- followed by: UPDATE accounts SET balance=balance-? WHERE id=?
-- In the same transaction — without SERIALIZABLE isolation
EXPLAIN ANALYZE SELECT balance FROM accounts WHERE id=1;
-- If the plan doesn't include "Serialize" or lock markers:
-- TOCTOU is possible
```

**Fix:**
BAD: READ COMMITTED isolation with check-then-act transactions.
GOOD: Use `SELECT balance FROM accounts WHERE id=? FOR UPDATE` (2PL), or use SERIALIZABLE isolation + retry, or use atomic `UPDATE accounts SET balance=balance-? WHERE id=? AND balance>=?` with rowcount check.
**Prevention:** Classify all check-then-act operations as SERIALIZABLE candidates. Apply the `FOR UPDATE` pattern for balance-critical operations.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-008 - Consistency Models (serializability in the distributed context)
- DST-012 - Linearizability (single-op strong consistency; serializability extends to transactions)
- DST-024 - ACID Properties (the transaction model serializability fulfills)

**Builds On This (learn these next):**

- DST-024 - ACID Properties (full correctness model for transactions)
- DST-025 - Distributed Transactions (2PC, Saga for cross-database serializability)

**Alternatives / Comparisons:**

- DST-012 - Linearizability (single-operation recency vs. multi-operation transaction correctness)
- DST-009 - Strong Consistency (linearizability in the storage layer)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Result of concurrent txns =    |
|                  | some serial execution of them  |
+------------------+--------------------------------+
| PROBLEM SOLVED   | Write skew, phantom reads,     |
|                  | dirty reads in concurrent DB   |
+------------------+--------------------------------+
| KEY INSIGHT      | Result-equivalent to serial;   |
|                  | actual execution can be parallel|
+------------------+--------------------------------+
| USE WHEN         | Financial txns, constraint-     |
|                  | enforcing business logic, 2PL  |
+------------------+--------------------------------+
| AVOID WHEN       | High-throughput, low-conflict   |
|                  | workloads (use REPEATABLE READ) |
+------------------+--------------------------------+
| TRADE-OFF        | Correctness vs. concurrency;   |
|                  | abort rate vs. anomaly rate    |
+------------------+--------------------------------+
| ONE-LINER        | Concurrent transactions produce|
|                  | same result as serial ordering |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-024 ACID Properties,       |
|                  | DST-025 Distributed Txns       |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. Serializability = result of concurrent transactions equals some serial execution; prevents ALL isolation anomalies including write skew.
2. Snapshot Isolation (PostgreSQL REPEATABLE READ) is NOT serializable — write skew is possible and causes real bugs.
3. SSI (PostgreSQL SERIALIZABLE, CockroachDB) provides full serializability with optimistic concurrency — always retry on `ERROR 40001: serialization failure`.

**Interview one-liner:**
"Serializability is the strongest transaction isolation level, guaranteeing that the result of any concurrent transaction execution is identical to some serial (one-at-a-time) execution — preventing all anomalies including write skew, which Snapshot Isolation misses — typically implemented through Two-Phase Locking (pessimistic) or Serializable Snapshot Isolation (optimistic, with abort-and-retry on conflict)."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Optimistic approaches (SSI) work best when conflicts are rare; pessimistic approaches (2PL) work best when conflicts are common. The right choice is not about preference — it's about your actual conflict rate under production load. Measure first: if abort rate under SSI exceeds 10%, switch to targeted `SELECT FOR UPDATE`. If deadlock rate under 2PL exceeds 1%, consider SSI. The trade-off is not theoretical — it shows up in P99 latency and error rates.

**Where else this pattern appears:**

- **Git merge strategies:** A `git rebase` is a serializable operation — it replays your commits as if they happened after the base branch's commits. A `git merge` is non-serializable — it accepts interleaved history. `git rebase` gives serializable-equivalent history; `git merge` gives snapshot-isolation-equivalent history.
- **Optimistic UI locking (Figma, Google Docs):** When two users edit the same element simultaneously, operational transforms (OT) or CRDTs are the "SSI" of collaborative editing — allowing concurrent edits and detecting conflicts. The "abort and retry" is the "last writer's change overrides" or "merge dialog" presented to the user.
- **Database schema migrations (Flyway, Liquibase):** Migration scripts are executed serially (one at a time) to ensure database schema changes are serializable. Running migrations concurrently without locks would violate serializability of the schema state.

---

### 💡 The Surprising Truth

The SQL standard defines four isolation levels: Read Uncommitted, Read Committed, Repeatable Read, and Serializable. But the standard definition of Repeatable Read was written to match what IBM DB2's implementation provided in the 1980s — which used range locks and prevented phantom reads. PostgreSQL's Repeatable Read is NOT the SQL standard Repeatable Read — it's Snapshot Isolation, which does NOT prevent phantoms in the standard sense (it prevents them differently, via consistent snapshots, but can produce write skew which SQL's Repeatable Read theoretically also prevents). This means: the same isolation level NAME means different things in different databases, and the SQL standard's definitions don't cleanly map to actual implementation behaviors. The only safe rule: read your database's actual documentation and run Jepsen-style tests to verify actual isolation behavior — never assume based on the isolation level name.

---

### 🧠 Think About This Before We Continue

**Q1 (C - Design Trade-off):** A ticket-selling system needs to sell exactly 1,000 tickets, no more, no less. Two approaches: (A) SERIALIZABLE isolation with SSI on the `tickets_remaining` counter. (B) Optimistic locking: read counter, write with `WHERE tickets_remaining = ?` (fail if changed). Under 10,000 concurrent buyers at ticket release, which approach provides higher throughput? Which has lower abort/retry rate? Is there a third approach that beats both?
_Hint:_ Both approaches serialize contention on the same counter row. The throughput limit is the row's lock contention rate. What if you pre-allocated 1,000 individual ticket rows and used an `unclaimed` flag instead of a shared counter?

**Q2 (D - Root Cause):** A bank's nightly reconciliation report shows $50,000 "missing" from the total balance. No individual transaction has an error. The system uses Snapshot Isolation (PostgreSQL REPEATABLE READ). The report transaction runs during peak processing. What is the exact mechanism of the anomaly, and would using SERIALIZABLE fix it?
_Hint:_ The report transaction reads Account A's balance at snapshot time T1. A concurrent transfer transaction moves $50,000 from Account A to Account B between T1 and the report's read of Account B. The report sees Account A's pre-transfer balance and Account B's pre-transfer balance. What does the report "think" happened to $50,000?

**Q3 (E - First Principles):** Serializability requires that the result of concurrent transactions equals some serial execution. But serializability does NOT require the serial order to match real-time order. This means: T1 commits at 14:00, T2 commits at 14:01, but the serializable order could be T2 → T1 (T2 "appears to have happened first"). Is this ever observable by clients? Under what conditions does a client notice this time reversal? What is the name of the property that would prevent this reversal?
_Hint:_ If a client can observe T1's effects (reads T1's written value) before T2 starts, then T2 → T1 serial ordering is impossible — T2 can't precede T1 if T1's effects were visible before T2 began. What property ensures the serial order is consistent with real-time observation? (This is the definition of a property you've already learned.)

