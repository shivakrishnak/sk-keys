---
layout: default
title: "Serializability"
parent: "Distributed Systems"
nav_order: 578
permalink: /distributed-systems/serializability/
number: "0578"
category: Distributed Systems
difficulty: ★★★
depends_on: Consistency Models, Linearizability, Database Transactions, ACID
used_by: Financial Transactions, Distributed Databases, OLTP Systems
related: Linearizability, ACID, Isolation Levels, Snapshot Isolation
tags:
  - serializability
  - transactions
  - isolation
  - distributed-systems
  - advanced
---

# 578 — Serializability

⚡ TL;DR — Serializability is the strongest isolation level for database transactions: a history of concurrent transactions is serializable if the result is equivalent to some serial (sequential, one-at-a-time) execution. It prevents all transaction anomalies (dirty reads, non-repeatable reads, phantom reads, write skew). In distributed databases, achieving serializability requires protocols like Two-Phase Locking (2PL), Serializable Snapshot Isolation (SSI), or Spanner's TrueTime-based distributed transactions.

| #578 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Consistency Models, Linearizability, Database Transactions, ACID | |
| **Used by:** | Financial Transactions, Distributed Databases, OLTP Systems | |
| **Related:** | Linearizability, ACID, Isolation Levels, Snapshot Isolation | |

### 🔥 The Problem This Solves

**WORLD WITHOUT SERIALIZABILITY (snapshot isolation only):**
Hospital's on-call scheduling: at least one doctor must be on-call at any time.
Transaction T1: Bob reads on-call list = [Bob, Alice]. Bob is tired. T1 sets Bob as off-call.
Transaction T2: Alice reads on-call list = [Bob, Alice] (concurrent snapshot). T2 sets Alice as off-call.
Both transactions pass their invariant check: "at least one other doctor remains."
Both commit under snapshot isolation (each saw the others' presence in its snapshot).
Result: zero doctors on call — a phantom. THIS IS WRITE SKEW. Snapshot isolation allows write skew; serializability does not. Under serializability, one transaction would see the committed result of the other and abort (or retry with the corrected list), maintaining the invariant.

---

### 📘 Textbook Definition

**Serializability** is a correctness criterion for concurrent transactions: a schedule (history of interleaved transaction operations) is serializable if it produces the same result as some serial execution of the same transactions (one at a time, in some order).

**View Serializability:** the reads and final writes match some serial execution.
**Conflict Serializability:** the order of conflicting operations (read/write to same object) matches a serial execution. More restrictive, but more commonly implemented via precedence graphs.

Relation to isolation levels (SQL standard): ANSI SQL defines Read Uncommitted < Read Committed < Repeatable Read < Serializable. Snapshot Isolation (MVCC default in Postgres/Oracle) is BETWEEN Repeatable Read and Serializable — it prevents dirty reads, non-repeatable reads, phantom reads in most cases, BUT still allows write skew.

**Strict Serializability** = Serializability (transaction isolation) + Linearizability (real-time ordering). This is the strongest practical model, implemented by Google Spanner.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Serializability = concurrent transactions look as if they ran one at a time, even though they ran in parallel.

**One analogy:**
> Two chefs cooking in a kitchen must share a knife. Serializability means: even though both are cooking simultaneously, the result of their work on any shared ingredient must be as if one chef used the knife first, then the other — no chaotic mid-chop handoffs, no shared partial cuts. The final dish must be achievable by some valid sequential order of complete operations.

---

### 🔩 First Principles Explanation

```
ISOLATION ANOMALIES — WHAT SERIALIZABILITY PREVENTS:

DIRTY READ (Read Uncommitted → Read Committed boundary):
  T1: writes x=5 (not committed)
  T2: reads x=5 (dirty — T1 might rollback)
  T1: ROLLBACK → x is still 3
  T2 saw x=5 that never existed ❌
  Prevented by: Read Committed and above

NON-REPEATABLE READ (Read Committed → Repeatable Read boundary):
  T1: reads x=3
  T2: writes x=5, commits
  T1: reads x=5 (different value — same query, different result)
  Prevented by: Repeatable Read and above (locks row until T1 commits)

PHANTOM READ (Repeatable Read → Serializable boundary):
  T1: SELECT * WHERE age > 30 → returns 5 rows
  T2: INSERT new row with age=35, commits
  T1: SELECT * WHERE age > 30 → returns 6 rows (phantom appeared!)
  Prevented by: Serializable (range locks) and Snapshot Isolation (in most cases)

WRITE SKEW (Snapshot Isolation → Serializable boundary):
  T1: reads check = [doctor_bob_on_call=true, doctor_alice_on_call=true]
      writes: doctor_bob_on_call = false (satisfied check: alice still on)
  T2: reads check = [doctor_bob_on_call=true, doctor_alice_on_call=true]  ← SAME SNAPSHOT
      writes: doctor_alice_on_call = false (satisfied check: bob still on)
  Both commit: zero doctors on call ❌
  Prevented by: Serializable ONLY (not Snapshot Isolation)
```

---

### 🧪 Thought Experiment

**SCENARIO:** Stock trading — buy 100 shares if balance ≥ $10,000.

```
CONCURRENT TRANSACTIONS:
  T1: buy_stock(AAPL, 100 shares, $9000 cost)
      READ balance = $15,000 ✓ (≥ $9000)
  T2: buy_stock(GOOG, 100 shares, $8000 cost)
      READ balance = $15,000 ✓ (≥ $8000)  [concurrent snapshot]

  T1: WRITE balance = $15,000 - $9,000 = $6,000
  T2: WRITE balance = $15,000 - $8,000 = $7,000

  WITH SNAPSHOT ISOLATION / LAST WRITER WINS:
  Final balance = $7,000 (T2 wins, overwrites T1)
  But T1 deducted $9,000! Customer's actual position: -$11,000 shortfall.

  WITH SERIALIZABILITY (2PL or SSI):
  T1 and T2 conflict on "balance" (both read + write)
  One of them aborts and retries with fresh read.
  
  Serializable execution:
  T1 commits: balance = $6,000
  T2 retries: READ balance = $6,000 — below $8,000 → purchase rejected
  Customer keeps $6,000 balance: correct ✓

REAL-WORLD: Banking, trading systems, booking systems require serializability
            for any multi-step read-check-write pattern.
```

---

### 🧠 Mental Model / Analogy

> Serializability is like a single checkout lane at a grocery store. Even though many customers arrived simultaneously, each customer's coupon + payment interaction is processed completely before the next starts. This prevents the "coupon double-use" race condition (customer A and B both use the same one-time coupon in the same second — serializable checkout only lets one proceed, the other sees the coupon already used).
> 
> The key: customers can shop in parallel (READ-ONLY phase), but checkout (the READ-MODIFY-WRITE commit) is serialized.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Serializability means your transactions are safe — no matter how many run at the same time, the database ensures the result is equivalent to running them one at a time. This prevents all the classic banking/booking/inventory race conditions.

**Level 2:** Two primary implementation strategies: 2-Phase Locking (2PL) — pessimistic, acquire locks during the transaction, release all at commit time; and Serializable Snapshot Isolation (SSI) — optimistic, run transactions without blocking, detect conflicts at commit time and abort one of the conflicting transactions. 2PL has higher concurrency overhead (blocking under contention). SSI (Postgres, FoundationDB, CockroachDB) has higher abort rate under high contention but lower latency under low contention.

**Level 3:** In practice, many OLTP databases default to Snapshot Isolation (Postgres `REPEATABLE READ`, Oracle), NOT Serializable, due to performance. Postgres Serializable isolation uses SSI (introduced in 9.1): it tracks read-write dependencies via "siread locks" (not blocking locks), detects dangerous dependency cycles at commit time, and aborts the transaction forming the cycle. The cost: ~10-20% overhead vs MVCC. Application must handle serialization errors (40001 in Postgres) with retry logic. In distributed databases: Spanner uses a global read-write transaction protocol with Paxos consensus + TrueTime external consistency — achieves strict serializability globally.

**Level 4:** The formal definition uses serialization graphs (dependency graphs): a schedule is conflict-serializable if its conflict precedence graph is acyclic. SSI makes this graph construction explicit: it tracks RW anti-dependencies (T1 reads old version, T2 writes new version) as "SIRead locks." A cycle involving an RW anti-dependency is a dangerous structure → SSI aborts. For distributed transactions, serializability requires atomic commit across shards (2PC — two-phase commit) plus concurrency control across nodes. This is why distributed serializable transactions are expensive: they combine 2PC (cross-shard coordination) with a consensus protocol per shard for durability, resulting in 2–4 network round-trips per transaction.

---

### ⚙️ How It Works (Mechanism)

```
TWO-PHASE LOCKING (2PL) — PESSIMISTIC SERIALIZABILITY:

  PHASE 1 (GROWING): acquire all needed locks
  PHASE 2 (SHRINKING): release locks (only at/after commit)
  
  T1: READ(balance) → acquire shared lock on balance row
  T2: READ(balance) → acquire shared lock on balance row (can share ✓)
  T1: WRITE(balance) → upgrade to exclusive lock → BLOCKS (T2 holds shared lock)
  T2: WRITE(balance) → upgrade to exclusive lock → BLOCKS (T1 holds shared lock)
  → DEADLOCK! (both wait for each other)
  
  2PL deadlock resolution: abort one transaction (DEADLOCK DETECTED → ROLLBACK T2)
  T2 retries → system is serializable (at cost of deadlock detection + retry overhead)
  
SERIALIZABLE SNAPSHOT ISOLATION (SSI) — OPTIMISTIC:

  T1: READ(balance) from MVCC snapshot version V1 → siread lock on balance
  T2: READ(balance) from MVCC snapshot version V1 → siread lock on balance
  T1: WRITE(balance=6000) → write intent recorded
  T2: WRITE(balance=7000) → write intent recorded
  
  T1 commits:
    Check: any concurrent T wrote to what T1 read? → T2 wrote balance, T1 read balance
    → T1-T2 RW anti-dependency detected
    But T1 committed first, no cycle yet
  
  T2 commits:
    Check: T1 wrote balance; T2 read old balance (before T1's write)
    RW anti-dependency cycle: T2 read old value → T1 wrote new value → T2 wrote based on old
    → DANGEROUS CYCLE → ABORT T2 with serialization error 40001
  T2 retries with fresh read → sees balance=6000  → rejects purchase ✓
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
GOOGLE SPANNER — STRICT SERIALIZABILITY:

  External client initiates read-write transaction:
  1. Client starts transaction → receives timestamp from Spanner leader
  2. Client performs reads (from Paxos leader of each relevant shard)
  3. Client sends commit request with mutations (writes)
  4. Spanner coordinator initiates 2PC across shards:
     a. PREPARE phase: each shard's Paxos group votes to commit
     b. COMMIT phase: coordinator commits after majority vote
  5. Spanner assigns commit timestamp using TrueTime: timestamp = now.earliest
     → Commit WAIT: Spanner waits until TrueTime.now.earliest > commit_timestamp
       (ensures commit timestamp is in the past for ALL subsequent transactions)
  6. Client receives success ✓
  
  RESULT: Strict Serializability
  - Serializable: equivalent to some serial execution ✓
  - Linearizable: commit timestamp respects real wall-clock time ✓
  - External consistency: transactions started after T committed see T's writes ✓
  
  Cost: 7-12ms commit latency within a region (TrueTime wait + Paxos rounds)
        ~100ms cross-region (network RTT dominates)
```

---

### 💻 Code Example

```java
// Postgres: Serializable isolation to prevent write skew (doctor on-call example)
@Service
public class OnCallScheduleService {

    private final OnCallRepository onCallRepository;

    // @Transactional with SERIALIZABLE isolation: prevents write skew
    @Transactional(isolation = Isolation.SERIALIZABLE)
    public void requestDayOff(Long doctorId) {
        List<Doctor> currentlyOnCall = onCallRepository.findAllOnCall();

        // Business invariant: at least 1 doctor must remain on call
        long otherDoctorsOnCall = currentlyOnCall.stream()
            .filter(d -> !d.getId().equals(doctorId))
            .filter(Doctor::isOnCall)
            .count();

        if (otherDoctorsOnCall == 0) {
            throw new InsufficientCoverageException(
                "Cannot take day off: no other doctor available");
        }

        // With SERIALIZABLE: if a concurrent transaction also read and passed this check,
        // Postgres SSI detects the RW anti-dependency cycle and aborts one transaction.
        // The aborted transaction gets: org.postgresql.util.PSQLException (SQLState 40001)
        // Application must retry:
        onCallRepository.setOffCall(doctorId);
    }
}

// Service layer must handle serialization failures with retry
@Component
public class RetryableOnCallService {

    private final OnCallScheduleService service;

    // Spring Retry: handle serialization failures transparently
    @Retryable(
        value = {SerializationFailureException.class},
        maxAttempts = 3,
        backoff = @Backoff(delay = 50, multiplier = 2.0)
    )
    public void requestDayOffWithRetry(Long doctorId) {
        service.requestDayOff(doctorId);
    }
}
```

---

### ⚖️ Comparison Table

| Isolation Level | Dirty Read | Non-Rep Read | Phantom Read | Write Skew | Implementation |
|---|---|---|---|---|---|
| **Read Uncommitted** | Possible | Possible | Possible | Possible | No locks |
| **Read Committed** | Prevented | Possible | Possible | Possible | Row locks released at stmt |
| **Repeatable Read** | Prevented | Prevented | Some | Possible | Row locks held to commit |
| **Snapshot Isolation** | Prevented | Prevented | Most | Possible | MVCC snapshots |
| **Serializable** | Prevented | Prevented | Prevented | Prevented | 2PL or SSI |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Serializable = Linearizable | Different properties! Serializability is multi-object transaction isolation; linearizability is single-object real-time ordering. Both together = strict serializability (Spanner) |
| Snapshot Isolation is serializable | SI prevents most anomalies but NOT write skew. Postgres `REPEATABLE READ` uses SI. Postgres `SERIALIZABLE` uses SSI |
| Serializability is too slow for real systems | Postgres SSI adds only ~10-20% overhead vs MVCC. CockroachDB and FoundationDB use SSI at scale. The key is handling serialization errors with retry logic |

---

### 🚨 Failure Modes & Diagnosis

**Write Skew Under Snapshot Isolation**

```
Symptom:
Two concurrent bookings both succeed for the "last available room."
OR: Two transactions both pass the "non-negative balance" check and both deduct.

Diagnosis:
SELECT pg_stat_activity where query ~ 'BEGIN';  -- how many concurrent TXs
Check isolation level: SHOW transaction_isolation;
-- If "repeatable read" → snapshot isolation → write skew possible

Test for write skew (Postgres):
  Session 1: BEGIN ISOLATION LEVEL REPEATABLE READ;
  Session 2: BEGIN ISOLATION LEVEL REPEATABLE READ;
  Session 1: SELECT count(*) FROM rooms WHERE available=true;  -- 1 room
  Session 2: SELECT count(*) FROM rooms WHERE available=true;  -- 1 room
  Session 1: UPDATE rooms SET available=false WHERE id=1;
  Session 2: UPDATE rooms SET available=false WHERE id=1;
  Session 1: COMMIT;
  Session 2: COMMIT;
  -- BOTH succeed under Snapshot Isolation → double-booking bug

Fix:
  Option 1: Use SERIALIZABLE isolation (Postgres SSI handles this)
  Option 2: Explicit SELECT FOR UPDATE (pessimistic lock on the row)
    SELECT * FROM rooms WHERE id=1 FOR UPDATE;  -- blocks concurrent T
  Option 3: Optimistic locking with version column:
    UPDATE rooms SET available=false, version=version+1
    WHERE id=1 AND available=true AND version=:expected_version
    -- If 0 rows updated: conflict detected, retry
```

---

### 🔗 Related Keywords

- `Linearizability` — the single-object real-time ordering property; serializability + linearizability = strict serializability
- `ACID` — serializability is the "I" (isolation) in ACID
- `Two-Phase Commit (2PC)` — required for distributed serializable transactions
- `Snapshot Isolation` — the common alternative that allows write skew (NOT fully serializable)
- `Raft / Paxos` — consensus protocols used to replicate transaction logs in distributed serializable systems

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ DEFINITION    │ Concurrent transactions ≡ some serial exec  │
├───────────────┼─────────────────────────────────────────────┤
│ PREVENTS      │ All anomalies incl. write skew (SI doesn't) │
├───────────────┼─────────────────────────────────────────────┤
│ METHODS       │ 2PL (pessimistic), SSI (optimistic)         │
├───────────────┼─────────────────────────────────────────────┤
│ POSTGRES      │ SET isolation level SERIALIZABLE; retry on  │
│               │ SQLState 40001 (serialization failure)      │
├───────────────┼─────────────────────────────────────────────┤
│ vs SI         │ Snapshot Isolation allows write skew;       │
│               │ Serializable prohibits all anomalies        │
├───────────────┼─────────────────────────────────────────────┤
│ DISTRIBUTED   │ 2PC + Paxos/Raft per shard (expensive);    │
│               │ Spanner TrueTime achieves strict-ser global │
└───────────────┴─────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** A hotel booking system uses Postgres with REPEATABLE READ isolation. The system stores room availability in a `rooms` table and bookings in a `bookings` table. Overbooking incidents are reported: two guests both received confirmation for the last room in the same time window. The engineering team considers three fixes: (1) upgrade to SERIALIZABLE isolation, (2) add `SELECT FOR UPDATE` on the room availability read, (3) use an optimistic locking version field on the rooms table. For each option: describe the exact mechanism that prevents the overbooking anomaly, identify the trade-off (latency, error handling complexity, throughput), and recommend which is most appropriate for a booking system that processes 500 concurrent searches/second but only 10 concurrent bookings/second.
