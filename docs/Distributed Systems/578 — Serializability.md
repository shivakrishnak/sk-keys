---
layout: default
title: "Serializability"
parent: "Distributed Systems"
nav_order: 578
permalink: /distributed-systems/serializability/
number: "578"
category: Distributed Systems
difficulty: ★★★
depends_on: "Consistency Models, ACID"
used_by: "Database Transactions, Isolation Levels"
tags: #advanced, #distributed, #transactions, #isolation, #acid
---

# 578 — Serializability

`#advanced` `#distributed` `#transactions` `#isolation` `#acid`

⚡ TL;DR — **Serializability** guarantees that the outcome of concurrently executing transactions is equivalent to executing them one-at-a-time (serially) in some order — the gold standard for transaction isolation that prevents all read and write anomalies.

| #578            | Category: Distributed Systems           | Difficulty: ★★★ |
| :-------------- | :-------------------------------------- | :-------------- |
| **Depends on:** | Consistency Models, ACID                |                 |
| **Used by:**    | Database Transactions, Isolation Levels |                 |

---

### 📘 Textbook Definition

**Serializability** is the strongest isolation level for database transactions, defined in the ANSI SQL standard as "Serialisable." A schedule (interleaving) of concurrent transactions is serialisable if it is equivalent — in terms of final database state and values returned to transactions — to some serial execution of those transactions (where one transaction runs to completion before the next begins). Serializability prevents all transaction anomalies: dirty reads (reading uncommitted data), non-repeatable reads (same read returning different values within a transaction), phantom reads (new rows appearing mid-transaction), and write skew (two transactions each reading overlapping data and writing non-overlapping data in a conflicting way). It is implemented via: **Two-Phase Locking (2PL)** (pessimistic: locks held until transaction end), **Serialisable Snapshot Isolation (SSI)** (optimistic: detects and aborts conflicting transactions), or **serialisation graphs** (transaction conflict graphs must be acyclic). Note: Serializability differs from Linearisability — serializability is about multi-operation transactions (no real-time ordering requirement); linearisability is about single operations with real-time ordering.

---

### 🟢 Simple Definition (Easy)

Serializability: "Even though many transactions ran at the same time, the database looks as if they ran one after another." Like a bank with 1000 simultaneous transactions — the database ensures the final result is the same as if transactions ran one by one. No "half-done" transaction visible to another. No lost updates. No impossible outcomes like both users successfully booking the last seat.

---

### 🔵 Simple Definition (Elaborated)

Write skew — the anomaly that serializability prevents: Alice and Bob both work on-call. Rule: at least 1 person must always be on-call. Alice reads: 2 on-call (Alice + Bob). Bob reads: 2 on-call (Alice + Bob). Alice thinks: "2 > 1, I can go off-call" → removes herself. Bob thinks: "2 > 1, I can go off-call" → removes himself. Result: 0 on-call! Both transactions were legal in isolation but illegal together. Serializability prevents this by detecting the conflict (both read the same rows, both wrote different rows that collectively violated a constraint).

---

### 🔩 First Principles Explanation

**Transaction anomalies prevented by serializability, with SQL examples:**

```
ANOMALIES AND ISOLATION LEVELS:

  ISO SQL defines isolation levels by which anomalies they prevent:

  ┌──────────────────────┬──────────────┬────────────────┬───────────────┬───────────────┐
  │ Isolation Level      │ Dirty Read   │ Non-Rep. Read  │ Phantom Read  │ Write Skew    │
  ├──────────────────────┼──────────────┼────────────────┼───────────────┼───────────────┤
  │ Read Uncommitted     │ Possible     │ Possible       │ Possible      │ Possible       │
  │ Read Committed       │ Prevented    │ Possible       │ Possible      │ Possible       │
  │ Repeatable Read      │ Prevented    │ Prevented      │ Possible*     │ Possible       │
  │ Serialisable         │ Prevented    │ Prevented      │ Prevented     │ Prevented      │
  └──────────────────────┴──────────────┴────────────────┴───────────────┴───────────────┘
  * MySQL InnoDB Repeatable Read prevents phantoms via gap locks (exception to standard)

ANOMALY 1: DIRTY READ (Read Uncommitted):

  T1: BEGIN; UPDATE accounts SET balance=50 WHERE id=1; -- (was 100, not yet committed)
  T2: BEGIN; SELECT balance FROM accounts WHERE id=1; → returns 50 (uncommitted!)
  T1: ROLLBACK; -- balance reverts to 100
  T2: made a decision based on balance=50 (which never existed) → wrong decision.

  Prevention: Read Committed isolation or higher.

ANOMALY 2: NON-REPEATABLE READ (Read Committed allows):

  T1: BEGIN; SELECT balance FROM accounts WHERE id=1; → returns 100
  T2: BEGIN; UPDATE accounts SET balance=50 WHERE id=1; COMMIT;
  T1: SELECT balance FROM accounts WHERE id=1; → returns 50 (DIFFERENT from first read!)
  T1: total = first_read + second_read = 100 + 50 = 150 → incorrect logic

  Prevention: Repeatable Read (hold shared locks on read rows until transaction end).

ANOMALY 3: PHANTOM READ (Repeatable Read allows):

  T1: SELECT COUNT(*) FROM employees WHERE dept='engineering'; → returns 10
  T2: INSERT INTO employees VALUES (..., dept='engineering'); COMMIT; -- new employee
  T1: SELECT COUNT(*) FROM employees WHERE dept='engineering'; → returns 11 (PHANTOM!)

  T1: decides "10 engineers, room for 5 more" → hires 5 more.
  But dept already had 11 (not 10) when T1 started. Decision based on phantom data.

  Prevention: Serialisable (gap locks in 2PL, or predicate locks).

ANOMALY 4: WRITE SKEW (Repeatable Read allows):

  Setup: on_call_doctors table. Business rule: ≥ 1 doctor on-call at all times.
  Currently: Alice (on-call), Bob (on-call). Both eligible to sign off.

  T1 (Alice signs off):
    SELECT COUNT(*) FROM doctors WHERE on_call=true; → returns 2 (≥1, so can sign off)
    UPDATE doctors SET on_call=false WHERE name='Alice';

  T2 (Bob signs off):
    SELECT COUNT(*) FROM doctors WHERE on_call=true; → returns 2 (T1 not committed yet)
    UPDATE doctors SET on_call=false WHERE name='Bob';

  T1 COMMIT, T2 COMMIT. Result: 0 on-call doctors. Business rule violated!

  Under Repeatable Read: no dirty reads, no non-repeatable reads, no phantoms.
  But write skew IS possible: T1 and T2 read the same rows, wrote DIFFERENT rows.
  Repeatable Read protects the rows read, not the logical constraint they represent.

  Under Serialisable: T1 and T2 have a conflict detected (both read on_call rows, both wrote).
  Database aborts one: "would violate serialisable schedule" → one transaction retries.
  Retry: sees count=1 (other signed off) → cannot sign off → correct!

IMPLEMENTING SERIALIZABILITY:

  Method 1: TWO-PHASE LOCKING (2PL) — Pessimistic:

    Phase 1 (Expanding): transaction acquires locks. Cannot release any lock.
    Phase 2 (Shrinking): transaction releases locks. Cannot acquire new locks.

    In practice: all locks held until COMMIT or ROLLBACK.

    Shared (S) lock: for reads. Multiple transactions can hold S locks simultaneously.
    Exclusive (X) lock: for writes. Only one transaction can hold X lock. Blocks all S locks.

    Predicate lock: lock not on a specific row but on a CONDITION (used for phantoms).
    "Lock on all rows where dept='engineering'" — prevents INSERT of new engineering rows.

    Downside: deadlocks. T1 holds lock on A, wants B. T2 holds lock on B, wants A.
    Detection: cycle in wait-for graph. Resolution: abort one transaction.

  Method 2: SERIALISABLE SNAPSHOT ISOLATION (SSI) — Optimistic (PostgreSQL ≥ 9.1):

    Based on MVCC (Multi-Version Concurrency Control):
    Each transaction sees a snapshot of the database at its start time.
    No locks on reads (high concurrency).

    At commit time: detect SERIALISATION CONFLICTS (anti-dependencies):
    If T1 read data later written by T2 AND T2 read data later written by T1 →
    these form a "dangerous structure" (rw anti-dependency cycle) → abort one transaction.

    The on-call write-skew scenario:
    T1 reads on_call_doctors, writes Alice's row.
    T2 reads on_call_doctors, writes Bob's row.
    T1→T2: T1's read (on_call_doctors) was written by T2 (indirectly, via count affected).
    T2→T1: T2's read was written by T1.
    Cycle detected → one transaction aborted → correct!

    SSI advantages vs 2PL:
      No read locks → readers don't block writers (unlike 2PL with S locks).
      Higher concurrency for read-heavy workloads.
      Deadlock-free (optimistic).
    SSI disadvantage:
      Abort rate: transactions can be aborted at commit time → must retry.
      For high-contention workloads: frequent aborts → worse throughput than 2PL.

  Method 3: TOTAL ORDER (single-node or single-writer):
    All writes serialised through a single writer → inherently serial → serialisable.
    Example: Redis (single-threaded) is inherently serialisable for single operations.
    Cost: throughput limited to single thread.

DISTRIBUTED SERIALIZABILITY:

  Across multiple database nodes: harder.
  Must coordinate locks across nodes (distributed 2PL) or coordinate SSI abort decisions.

  Google Spanner: uses TrueTime to assign globally unique commit timestamps.
  Transactions with non-overlapping timestamp ranges are serialisable by timestamp order.
  Transactions with overlapping ranges: wait for timestamp uncertainty to resolve.

  CockroachDB: distributed SSI. Each range (shard) runs SSI locally.
  Cross-range transactions: two-phase commit (2PC) to atomically commit across ranges.
  Serialisability: SSI detects conflicts within and across ranges.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT serializability:

- Write skew: booking conflicts, on-call violations, inventory overselling
- Non-repeatable reads: financial aggregations inconsistent within a single transaction
- Phantom reads: business rules violated by concurrent inserts during a validation transaction

WITH serializability:
→ Transactions behave as if they ran alone — all invariants maintained
→ No complex application-level locking required
→ Business rules enforced by the database, not by the application

---

### 🧠 Mental Model / Analogy

> A ticket office that processes reservation requests on multiple windows simultaneously but guarantees the final booking ledger looks as if every request was processed at a single window one by one. Two customers simultaneously try to book the last seat. The ticket office ensures only one succeeds — the result is identical to: customer A processed, seat taken, customer B processed, told "no seats." The simultaneous processing is invisible to the result. Write skew: customer A looks at "window 1" available seats, books. Customer B looks at "window 1" available seats (still shows available as A not committed), also books. Serializability: office detects both are booking from the same "seat check" and aborts one.

"Processing requests one by one at single window" = serial execution (the target outcome)
"Multiple windows simultaneously, same result" = serialisable schedule
"Two customers book from same seat check simultaneously" = write skew scenario
"Office detects conflict, aborts one booking" = SSI or 2PL conflict detection

---

### ⚙️ How It Works (Mechanism)

**PostgreSQL: setting serialisable isolation and handling serialisation failures:**

```sql
-- Set transaction isolation level to SERIALISABLE:
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Read on-call doctors:
SELECT COUNT(*) FROM doctors WHERE on_call = true;  -- returns 2

-- Based on count, sign off:
UPDATE doctors SET on_call = false WHERE name = 'current_user';

COMMIT;
-- PostgreSQL SSI: if another concurrent SERIALISABLE transaction also read on_call
-- and wrote to doctors, one of the two will receive:
-- ERROR: could not serialize access due to read/write dependencies among transactions
-- DETAIL: Reason code: Canceled on identification as a pivot, during commit attempt.
-- HINT: The transaction might succeed if retried.
```

---

### 🔄 How It Connects (Mini-Map)

```
ACID (Atomicity, Consistency, Isolation, Durability)
        │
        ▼
Isolation Levels (spectrum: Read Uncommitted → Serialisable)
        │
        ▼
Serializability ◄──── (you are here)
(strongest isolation; prevents all anomalies)
        │
        ├── Two-Phase Locking (pessimistic implementation)
        ├── SSI (optimistic implementation — PostgreSQL)
        └── Distributed Transactions (2PC for cross-shard serializability)
```

---

### 💻 Code Example

**Write skew prevention with serialisable isolation:**

```java
@Service
@Transactional(isolation = Isolation.SERIALIZABLE)  // Prevent write skew
public class OnCallService {

    @Autowired
    private DoctorRepository doctorRepository;

    public void requestSignOff(String doctorName) {
        // Read: how many doctors currently on call?
        long onCallCount = doctorRepository.countByOnCallTrue();

        if (onCallCount <= 1) {
            throw new BusinessException("Cannot sign off: you are the last on-call doctor");
        }

        // Write: sign off this doctor.
        Doctor doctor = doctorRepository.findByName(doctorName)
            .orElseThrow(() -> new EntityNotFoundException("Doctor not found: " + doctorName));
        doctor.setOnCall(false);
        doctorRepository.save(doctor);

        // Under SERIALIZABLE: if two doctors call this simultaneously,
        // PostgreSQL SSI will abort one with SerializationFailureException.
    }
}

// Caller must handle SerializationFailureException with retry:
@Service
public class OnCallFacade {

    @Autowired
    private OnCallService onCallService;

    public void requestSignOffWithRetry(String doctorName) {
        int maxRetries = 3;
        for (int attempt = 0; attempt < maxRetries; attempt++) {
            try {
                onCallService.requestSignOff(doctorName);
                return;  // Success
            } catch (org.springframework.dao.CannotSerializeTransactionException e) {
                // PostgreSQL serialisation failure → retry:
                if (attempt == maxRetries - 1) throw e;
                log.warn("Serialisation conflict on attempt {}, retrying...", attempt + 1);
                // Optionally add backoff: Thread.sleep(50 * (attempt + 1));
            }
        }
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Serializability and linearisability are the same          | They are different properties at different levels. Serializability: applies to multi-operation transactions; requires equivalent-to-serial execution; does NOT require real-time ordering. Linearisability: applies to single operations; requires real-time ordering. A system can be serialisable but not linearisable (e.g., snapshot isolation allows stale reads of single rows while transactions are serialisable). Strict serializability = both together |
| "Serializable" isolation level prevents all problems      | Serialisable isolation prevents all data anomalies WITHIN the defined operations. It does NOT prevent: application-level logic errors, network failures, hardware failures, or problems from reading data outside the transaction. Also: some databases claim "Serializable" but implement Snapshot Isolation (MySQL with some configurations, Oracle), which allows write skew. Check your database's actual implementation                                      |
| Serializable means slow                                   | Modern SSI implementations (PostgreSQL) have much lower overhead than 2PL. For read-heavy workloads with low write contention: SSI has near-zero overhead over Snapshot Isolation. The cost is borne only when conflicts occur (abort and retry). For many applications (low contention), serialisable is nearly as fast as Read Committed                                                                                                                        |
| All databases use the same implementation of Serializable | Major differences exist. PostgreSQL uses SSI (optimistic, low overhead, may abort). MySQL InnoDB uses 2PL (pessimistic, locking, may deadlock). Oracle calls Snapshot Isolation "Serializable" (does NOT prevent write skew). SQL Server uses 2PL by default, has SSI as an option. Always verify the implementation before assuming write skew is prevented                                                                                                      |

---

### 🔥 Pitfalls in Production

**Write skew with "Serializable" that is actually Snapshot Isolation (Oracle):**

```
PROBLEM: Application deployed on Oracle, uses SERIALIZABLE isolation,
         developer assumes write skew is prevented → write skew occurs in production.

  Oracle "SERIALIZABLE" = Snapshot Isolation (MVCC-based), NOT true serialisable.
  Write skew: possible. Oracle does NOT prevent it.

  Symptom: two doctors both successfully sign off, leaving 0 on-call doctors.
  Log: both transactions committed with SERIALIZABLE isolation → incorrect behavior.

  Root cause: Oracle's "SERIALIZABLE" ≠ SQL standard Serialisable. It's Snapshot Isolation.

BAD: Assuming Oracle SERIALIZABLE prevents write skew:
  -- Oracle:
  SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
  -- SELECT COUNT on-call → 2
  -- UPDATE set off-call
  -- COMMIT → SUCCEEDS (even if concurrent same transaction also committed) → write skew!

FIX OPTION 1: SELECT FOR UPDATE (explicit locking):
  -- Serialisable write skew: SELECT rows you depend on WITH FOR UPDATE lock:
  SELECT COUNT(*) FROM doctors WHERE on_call = true FOR UPDATE;
  -- This acquires an exclusive lock on the ON-CALL doctors rows.
  -- Concurrent transaction trying to also UPDATE doctors is BLOCKED until this commits.
  -- Ensures count is accurate and stable until commit.

FIX OPTION 2: MATERIALISE THE CONFLICT:
  -- Create a lock row that both transactions must write:
  -- on_call_slots table: slot_1, slot_2, etc. (one row per "on-call slot")
  -- Both transactions must claim/release a slot → conflicts on same row → detectable.

FIX OPTION 3: MOVE TO PostgreSQL (true SSI):
  -- PostgreSQL SERIALIZABLE = real SSI → write skew detected and aborted automatically.
  -- Requires retry logic but correct without application-level FOR UPDATE hacks.

  -- Always document which database you're using and which isolation level it actually provides.
  -- Never assume vendor's label matches SQL standard definition.
```

---

### 🔗 Related Keywords

- `Linearisability` — related but different: single-operation real-time ordering (not transactions)
- `ACID` — Serializability implements the "I" (Isolation) in ACID at the strongest level
- `Two-Phase Locking` — pessimistic implementation of serializability
- `Snapshot Isolation` — weaker than serialisable; allows write skew

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Concurrent transactions' outcome = some   │
│              │ serial execution; all anomalies prevented │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Financial transactions; inventory; any    │
│              │ multi-read-then-write requiring invariants│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ High-read-contention where SSI aborts     │
│              │ frequently; then consider FOR UPDATE locks│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "All ticket windows process simultaneously│
│              │  but the ledger looks like one window."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ACID → Two-Phase Locking → SSI →         │
│              │ Snapshot Isolation → Distributed 2PC      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A flight booking system uses PostgreSQL with Serialisable isolation. Two transactions both read `seats_available = 1` for flight AA101, then both try to insert a booking. Under 2PL: which transaction gets blocked and why? Under SSI: both transactions complete their reads and writes, then at commit time one is aborted. What specific conflict type (read-write dependency) does SSI detect that causes the abort?

**Q2.** Jepsen tests regularly find that database vendors claiming "Serializable" actually provide only Snapshot Isolation (allowing write skew). Why do vendors make this choice? What are the performance trade-offs between true SSI (PostgreSQL) and Snapshot Isolation (Oracle, MySQL) in terms of latency, throughput, and abort rate? When would a business choose to accept write skew risk in exchange for better performance?
