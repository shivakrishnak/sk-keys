---
version: 1
layout: default
title: "Locking (Row, Table, Gap, Next-Key)"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 39
permalink: /databases/locking/
id: DBF-039
category: Database Fundamentals
difficulty: ★★★
depends_on: Isolation Levels, MVCC, Transaction
used_by: Deadlock Detection (DB), Isolation, Phantom Read
related: Deadlock Detection, MVCC, Isolation Levels
tags:
  - database
  - concurrency
  - transactions
  - deep-dive
---

# DBF-039 - Locking (Row, Table, Gap, Next-Key)

⚡ TL;DR - Database locks prevent concurrent transactions from corrupting shared data - row locks for individual rows, table locks for DDL, gap locks for ranges, and next-key locks for phantom read prevention in InnoDB.

| #434            | Category: Database Fundamentals                  | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------- | :-------------- |
| **Depends on:** | Isolation Levels, MVCC, Transaction              |                 |
| **Used by:**    | Deadlock Detection (DB), Isolation, Phantom Read |                 |
| **Related:**    | Deadlock Detection, MVCC, Isolation Levels       |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Two bank tellers simultaneously process transactions for the same account: balance is $1,000. Teller A reads balance ($1,000), Teller B reads balance ($1,000). Teller A adds $200 → writes $1,200. Teller B subtracts $300 → writes $700 (based on the $1,000 they read, not the $1,200 after A's write). Final balance: $700. It should be $900. $200 has been lost - a lost update due to concurrent writes with no coordination.

**THE BREAKING POINT:**
Without locks, any concurrent write to the same row can corrupt data. Multiple transactions updating the same account balance, inventory count, or booking seat - all face this problem.

**THE INVENTION MOMENT:**
"Before modifying a row, acquire a lock. Other transactions wanting to modify the same row must wait."

---

### 📘 Textbook Definition

**Database locking** is a mechanism to manage concurrent access to data by serializing conflicting operations. Lock types include:

- **Row lock (record lock):** Locks a specific row; other transactions can read (shared lock) or are blocked from writing (exclusive lock).
- **Table lock:** Locks the entire table; used for DDL (ALTER TABLE) or full-table operations.
- **Gap lock (InnoDB):** Locks the gap between indexed values to prevent INSERTs into a range, preventing phantom reads.
- **Next-key lock (InnoDB):** A record lock + gap lock on the record and the gap before it; the default lock for range predicates in InnoDB REPEATABLE READ.
- **Shared lock (S):** Multiple readers can hold simultaneously; writer must wait.
- **Exclusive lock (X):** Only one holder; readers and writers both wait.
- **Intent locks:** Table-level signals indicating a transaction intends to acquire row-level locks (prevents conflicting table locks while row locks are held).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Locks serialize conflicting database operations - you must wait for the current holder to finish before modifying the same row, range, or table.

**One analogy:**

> A bathroom door lock. When occupied (row lock held), others must wait outside. A shared lock is like a reading room: multiple readers enter simultaneously, but nobody can enter to rearrange furniture while readers are present. An exclusive lock is the bathroom: one at a time. A gap lock is reserving a parking spot in a range: "spots 10–20 are reserved - nobody else can park here, even though they're currently empty."

**One insight:**
MVCC and locking are complementary, not alternatives. MVCC eliminates read-write lock contention (readers don't lock; they see their snapshot). Locking handles write-write contention (two writers to the same row must serialize). Almost all modern databases use both: MVCC for reads, locks for writes.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Compatibility matrix:** Two locks are compatible if they can be held simultaneously; otherwise one must wait.
2. **Lock granularity:** Row locks → fine-grained; table locks → coarse. Fine-grained = higher concurrency, higher overhead. Coarse = lower overhead, lower concurrency.
3. **Two-Phase Locking (2PL):** Transactions acquire locks during an "expanding phase" and release during a "shrinking phase." Strong 2PL (Strict 2PL): hold all locks until commit - prevents dirty reads and ensures serializability (at the cost of deadlock risk).
4. **Lock escalation:** Some databases convert many row locks to one table lock when row lock count exceeds a threshold - reduces lock overhead but reduces concurrency.

**LOCK COMPATIBILITY MATRIX:**

|                   | S (Shared)    | X (Exclusive) |
| ----------------- | ------------- | ------------- |
| **S (Shared)**    | ✅ Compatible | ❌ Conflict   |
| **X (Exclusive)** | ❌ Conflict   | ❌ Conflict   |

**EXPLICIT LOCKING:**

```sql
-- Shared lock (read, block writes)
SELECT * FROM orders WHERE id = 42 FOR SHARE;

-- Exclusive lock (read + block all other access)
SELECT * FROM orders WHERE id = 42 FOR UPDATE;

-- Lock entire table (rarely needed explicitly)
LOCK TABLE orders IN EXCLUSIVE MODE;

-- InnoDB: skip locked rows (non-blocking)
SELECT * FROM orders WHERE status = 'PENDING'
LIMIT 10 FOR UPDATE SKIP LOCKED;
```

**InnoDB SPECIFIC LOCK TYPES:**

**Record Lock:** Locks a single index record. `SELECT * FROM t WHERE id=5 FOR UPDATE` → record lock on id=5.

**Gap Lock:** Locks the gap between two index values. Prevents INSERT into the locked gap. Example: gap lock on (3, 7) prevents INSERT of id=4, 5, or 6. Gap locks are held between REPEATABLE READ transactions to prevent phantom reads.

**Next-Key Lock:** Record lock + gap lock on the preceding gap. Example: next-key lock on index value 10 means: lock record 10 AND the gap (last_record, 10]. This is the default lock for index range scans in InnoDB REPEATABLE READ.

**Insert Intention Lock:** Special gap lock for INSERT operations. Multiple INSERT intention locks on the same gap can coexist - they only conflict with gap locks (not with each other). This allows concurrent INSERTs into the same gap unless a gap lock is present.

**THE TRADE-OFFS:**
**Row locks:** High concurrency, higher overhead per lock, deadlock risk.
**Table locks:** Low overhead, low concurrency (entire table blocked), no deadlock (atomic acquisition).
**Gap locks:** Prevent phantoms in InnoDB, but cause deadlocks when two transactions acquire overlapping gap locks in different orders.
**MVCC + minimal locks:** Best balance - reads use snapshots (no locks), writes use row locks (minimal blocking).

---

### 🧪 Thought Experiment

**SETUP:**
A concert ticketing system has a `seats` table with columns: `seat_id, event_id, status ('AVAILABLE'/'RESERVED'), reserver_id`. 100 users simultaneously try to reserve seat #42 for event #100.

**WITHOUT LOCKING:**
100 simultaneous reads: `SELECT status FROM seats WHERE seat_id=42 AND event_id=100` → all see 'AVAILABLE'. All 100 proceed to UPDATE: `UPDATE seats SET status='RESERVED', reserver_id=user_id WHERE seat_id=42`. All 100 writes succeed. Seat is "reserved" by all 100 users - overbooking.

**WITH ROW LOCKING (`FOR UPDATE`):**

1. User 1: `SELECT * FROM seats WHERE seat_id=42 FOR UPDATE` → acquires exclusive row lock.
2. Users 2–100: `SELECT * FROM seats WHERE seat_id=42 FOR UPDATE` → blocked, waiting for User 1's lock.
3. User 1: `UPDATE seats SET status='RESERVED', reserver_id=1` → `COMMIT` → lock released.
4. User 2: acquires lock, reads status='RESERVED' → seat taken → book another seat or return error.
5. Users 3–100: same → all correctly see RESERVED.
   Result: Exactly one user reserves the seat.

**WITH GAP LOCK (InnoDB REPEATABLE READ):**
Query: `SELECT COUNT(*) FROM seats WHERE event_id=100 AND status='AVAILABLE'`
Gap lock on (event_id=100, status='AVAILABLE') range. Prevents new rows being inserted into this range while the count is being read. Used for phantom-read prevention in count-then-insert patterns.

**THE INSIGHT:**
`SELECT ... FOR UPDATE` is the correct pattern for "check then modify" operations (check availability, then reserve). It acquires the exclusive lock at read time, preventing concurrent modifications between the read and the subsequent write.

---

### 🧠 Mental Model / Analogy

> Database locks are like traffic lights at an intersection. A shared lock (S) is a green light for all readers - many cars (readers) can pass simultaneously. An exclusive lock (X) is a red light - one car (writer) goes through, everyone else waits. A gap lock is a road closure: "No new vehicles allowed to enter this section" - existing traffic flows, but no new entrants. An intent lock is a turn signal: "I'm about to turn (acquire a row lock at this table)"-warns other traffic controllers not to close the entire road (acquire a table lock) while you're maneuvering.

- "Green light for all" → Shared lock (multiple readers)
- "Red light, one at a time" → Exclusive lock (single writer)
- "Road closure section" → Gap lock (no new inserts in range)
- "Turn signal" → Intent lock (signals row-level lock intent to table-level)
- "Traffic accident / gridlock" → Deadlock

Where this analogy breaks down: traffic lights have a controller determining order; database locks use a wait graph and deadlock detection algorithm to determine who waits and who is selected as the deadlock victim.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A database lock is like a "currently being modified" flag on a row or table. When one transaction is changing data, others that want to change the same data must wait. When the first transaction finishes, the lock is released and a waiting transaction can proceed. Locks prevent two simultaneous writes from corrupting the same data.

**Level 2 - How to use it (junior developer):**
Use `SELECT ... FOR UPDATE` when your code reads a row and then updates it in the same transaction - this prevents another transaction from modifying the same row between your read and write. Use `FOR SHARE` when you need to read and prevent others from writing but you don't intend to write yourself. Avoid long-running transactions with locks - the longer you hold a lock, the more transactions queue up waiting. Use `SKIP LOCKED` for queue-processing patterns where you want to skip rows already locked by another worker.

**Level 3 - How it works (mid-level engineer):**
PostgreSQL lock modes (from weakest to strongest): `ACCESS SHARE` (SELECT), `ROW SHARE` (SELECT FOR UPDATE), `ROW EXCLUSIVE` (INSERT/UPDATE/DELETE), `SHARE UPDATE EXCLUSIVE` (VACUUM, ANALYZE), `SHARE` (CREATE INDEX), `SHARE ROW EXCLUSIVE`, `EXCLUSIVE`, `ACCESS EXCLUSIVE` (ALTER TABLE, DROP TABLE). ALTER TABLE requires ACCESS EXCLUSIVE - blocks all reads and writes. This is why long-running ALTER TABLE operations cause application outages; use tools like `pg_repack` or online DDL strategies instead. For row-level locks: `pg_locks` system view shows current locks; `pg_stat_activity` shows which sessions hold which locks. Lock wait timeout: `lock_timeout = '30s'` cancels queries that wait more than 30 seconds for a lock.

**Level 4 - Why it was designed this way (senior/staff):**
The lock hierarchy (intent locks → row locks → table locks) exists to make lock compatibility checks efficient. Without intent locks, a table-level lock request must check every row lock to see if the table is fully lockable - this is O(rows) per table lock request. Intent locks signal at the table level that row-level locks are held - the table lock check becomes O(1): check if any conflicting table-level lock (including intent locks) is held. InnoDB's gap locks are a pragmatic solution to phantom reads at REPEATABLE READ without requiring full serializable isolation. But gap locks cause a notorious class of deadlocks: Transaction A acquires a gap lock on range (10, 20). Transaction B acquires a gap lock on range (15, 25). Both try to INSERT into their locked ranges - deadlock, because each holds the other's needed gap range. This is why many teams avoid InnoDB REPEATABLE READ for high-concurrency INSERT workloads, preferring PostgreSQL's SSI or READ COMMITTED with application-level conflict handling.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ LOCK TYPES: INNODB ILLUSTRATION                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Index on id: ... | 5 | 10 | 15 | 20 | ...           │
│                  ^   ↑   ↑   ↑                       │
│                  gap  gap gap  gap                    │
│                                                      │
│ Record Lock on id=10:                                │
│   → Only id=10 row locked                            │
│                                                      │
│ Gap Lock on (5, 10):                                 │
│   → No INSERT with id=6,7,8,9 allowed                │
│   → Does NOT lock the record id=10 itself            │
│                                                      │
│ Next-Key Lock on id=10:                              │
│   → = Gap Lock (5,10) + Record Lock on 10            │
│   → Prevents: INSERT of 6-9 AND update of 10        │
│   → InnoDB default for range scans                   │
│                                                      │
│ T1: SELECT ... WHERE id BETWEEN 5 AND 15 FOR UPDATE  │
│ → Next-key locks on 10 and 15                        │
│ → Gap locks on (5,10) and (10,15)                    │
│ → T2: INSERT id=7 → BLOCKED (gap lock on (5,10))    │
│ → T2: INSERT id=12 → BLOCKED (gap lock on (10,15))  │
│ → T2: INSERT id=20 → ALLOWED (no lock on gap >15)   │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Transaction wants to update row 42
→ Request exclusive lock on row 42
→ [LOCKING ← YOU ARE HERE: acquire or wait]
→ If lock available → acquired → proceed with UPDATE
→ UPDATE committed → lock released
→ Waiting transactions proceed in queue order
```

**FAILURE PATH:**

```
T1: SELECT ... WHERE status='PENDING' FOR UPDATE → gap lock
T2: SELECT ... WHERE status='ACTIVE' FOR UPDATE → overlapping gap lock
T1: INSERT status='PENDING' → needs T2's gap → BLOCKED
T2: INSERT status='ACTIVE' → needs T1's gap → BLOCKED
→ DEADLOCK: T1 waiting for T2; T2 waiting for T1
→ DB detects wait cycle → aborts one (the "victim")
→ Victim receives: ERROR 1213: Deadlock found
→ Application must retry the aborted transaction
```

**WHAT CHANGES AT SCALE:**
At high concurrency, lock contention is a throughput ceiling. Contended rows (hot rows like inventory counts, like counters) serialize all writes - throughput = 1 write per lock hold time. Solutions: shard the hot row (multiple rows for the same counter, sum them), use optimistic locking (no locks; detect conflict at commit time), or use specialized structures (Redis counter with Lua atomicity). `SKIP LOCKED` enables queue consumer patterns: 10 workers each grab a different pending job without blocking each other.

---

### ⚖️ Comparison Table

| Lock Type          | Scope        | Prevents                         | Performance                    | InnoDB/PostgreSQL     |
| ------------------ | ------------ | -------------------------------- | ------------------------------ | --------------------- |
| Row (record) lock  | Single row   | Write-write conflicts on one row | Low overhead                   | Both                  |
| Table lock         | Entire table | All concurrent access            | High overhead, low concurrency | Both (DDL)            |
| Shared (S) lock    | Row/table    | Writers; allows other readers    | Moderate                       | Both                  |
| Exclusive (X) lock | Row/table    | All other access                 | Higher overhead                | Both                  |
| Gap lock           | Index range  | INSERTs into gap                 | Medium                         | InnoDB only           |
| Next-key lock      | Record + gap | INSERTs + row update             | Medium                         | InnoDB only (default) |

How to choose: Use row locks (FOR UPDATE) for concurrent modify patterns. Avoid table locks in OLTP. InnoDB gap locks happen automatically at REPEATABLE READ - understand them to avoid deadlocks.

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                                                                 |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MVCC eliminates all locks                    | MVCC eliminates read-write lock contention; write-write conflicts still require row locks; SELECT FOR UPDATE still takes explicit locks under MVCC                      |
| Table locks are always bad                   | Table locks are appropriate for DDL operations (ALTER TABLE) and are unavoidable; the problem is ACCIDENTAL table locks from poorly written queries or ORM behavior     |
| Gap locks only affect InnoDB SERIALIZABLE    | Gap locks are used by InnoDB at REPEATABLE READ for index range scans - they are the primary cause of phantom-read prevention AND gap lock deadlocks at REPEATABLE READ |
| SELECT FOR UPDATE always acquires a row lock | SELECT FOR UPDATE acquires locks only on rows that EXIST. Rows returned as null from a LEFT JOIN, or gaps between existing rows, require gap locks for full protection  |

---

### 🚨 Failure Modes & Diagnosis

**1. Lock Wait Timeout from Long-Running Transaction**

**Symptom:** `ERROR: canceling statement due to lock timeout` (PostgreSQL) or `ERROR 1205: Lock wait timeout exceeded` (MySQL) on writes; queries blocking each other.

**Root Cause:** A transaction holding a row lock is slow (or stuck) - other transactions waiting for the same row time out.

**Diagnostic:**

```sql
-- PostgreSQL: find lock waits
SELECT
  blocked.pid AS blocked_pid,
  blocked_query.query AS blocked_query,
  blocking.pid AS blocking_pid,
  blocking_query.query AS blocking_query
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_query ON blocked_query.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks
  ON blocking_locks.locktype = blocked_locks.locktype
  AND blocking_locks.granted = true
  AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_query ON blocking_query.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- MySQL: SHOW ENGINE INNODB STATUS\G
-- Look for: LOCK WAIT section
```

**Fix:** Terminate the blocking transaction: `SELECT pg_terminate_backend(blocking_pid)`. Investigate: why is the transaction long-running? Add `lock_timeout = '5s'` to fail fast rather than waiting forever.

**Prevention:** Set `lock_timeout = '5s'` and `statement_timeout = '30s'` in application connection configuration. Monitor `pg_stat_activity` for long-running transactions (> 1 minute).

---

**2. Gap Lock Deadlock (InnoDB REPEATABLE READ)**

**Symptom:** MySQL/InnoDB: `ERROR 1213: Deadlock found when trying to get lock; try restarting transaction` on INSERT operations; no obvious conflict between the transactions.

**Root Cause:** Two transactions each hold a gap lock and try to insert into the other's locked gap - a circular wait. Classic InnoDB gap lock deadlock pattern.

**Diagnostic:**

```sql
-- MySQL: check last deadlock
SHOW ENGINE INNODB STATUS\G
-- Look for: LATEST DETECTED DEADLOCK
-- Shows: which transactions, which locks, which waited

-- Pattern to look for:
-- T1: holds gap lock (A, B), waiting for gap lock (B, C)
-- T2: holds gap lock (B, C), waiting for gap lock (A, B)
-- → Deadlock
```

**Fix (immediate):** The database automatically resolves deadlocks by aborting one transaction - implement retry logic for `CannotAcquireLockException` / MySQL error 1213 in application code.

**Fix (structural):** Switch isolation level to READ COMMITTED (no gap locks): `SET TRANSACTION ISOLATION LEVEL READ COMMITTED`. Or use PostgreSQL with SERIALIZABLE + SSI (avoids gap locks via optimistic concurrency). Or redesign to avoid concurrent INSERTs into overlapping ranges.

**Prevention:** If using InnoDB REPEATABLE READ with high concurrent INSERTs into the same range: switch to READ COMMITTED. Always implement retry logic for deadlock errors.

---

**3. Accidental Table Lock from DDL in Production**

**Symptom:** Application goes down during a schema migration; all queries are blocked; `pg_stat_activity` shows "waiting for lock" on all connections.

**Root Cause:** `ALTER TABLE` requires `ACCESS EXCLUSIVE` lock in PostgreSQL (or metadata lock in MySQL), which blocks all reads and writes. If the table is busy, the ALTER waits - and while it waits, it blocks all subsequent queries.

**Diagnostic:**

```sql
-- PostgreSQL: check what's blocking the ALTER TABLE
SELECT pid, state, query, wait_event_type, wait_event
FROM pg_stat_activity
WHERE wait_event IS NOT NULL
ORDER BY wait_event_type;

-- If ALTER TABLE is waiting for ACCESS EXCLUSIVE:
-- All subsequent queries queue behind it
-- Effectively creates a total outage for the table
```

**Fix (immediate):** Kill the stuck ALTER TABLE migration. Use `lock_timeout = '2s'` to make the ALTER fail fast if it can't acquire the lock immediately, instead of blocking the queue.

**Prevention:** For production migrations: set `lock_timeout = '2s'` before running ALTER. Use `pg_repack` for table rewrites. Use `CREATE INDEX CONCURRENTLY` instead of `CREATE INDEX`. For zero-downtime schema changes, use additive-only migrations (add columns, don't drop or modify) with backward compatibility.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Isolation Levels` - locking implements the "I" in ACID at different isolation levels
- `MVCC` - locking and MVCC are complementary; MVCC handles read-write, locking handles write-write
- `Transaction` - locks are scoped to transactions; held until commit or rollback

**Builds On This (learn these next):**

- `Deadlock Detection (DB)` - what happens when locks form a circular wait cycle
- `Phantom Read` - gap locks are InnoDB's mechanism for phantom read prevention
- `Isolation Levels` - the isolation level determines which locks are acquired automatically

**Alternatives / Comparisons:**

- `Optimistic vs. Pessimistic Locking` - locking strategies that trade lock contention for retry overhead
- `MVCC` - the complementary mechanism for read-write concurrency without locks

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ROW LOCK     │ FOR UPDATE (exclusive) / FOR SHARE        │
│ TABLE LOCK   │ ALTER TABLE → ACCESS EXCLUSIVE → outage   │
│ GAP LOCK     │ InnoDB: prevents INSERT in range          │
│ NEXT-KEY     │ InnoDB default: record + preceding gap    │
├──────────────┼───────────────────────────────────────────┤
│ KEY PATTERN  │ SELECT ... FOR UPDATE for check-then-write│
│              │ SKIP LOCKED for queue consumers           │
├──────────────┼───────────────────────────────────────────┤
│ KEY PITFALL  │ InnoDB gap lock deadlocks at REP READ;    │
│              │ ALTER TABLE blocks all queries            │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Lock granularity (row vs table) vs        │
│              │ concurrency vs deadlock risk              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "MVCC for reads, locks for writes -       │
│              │  gap locks are phantom-read prevention"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Deadlock Detection → Optimistic Locking   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE B - Scale Thought Experiment) A social media platform has a `posts` table with a `like_count INT` column. 100,000 users simultaneously like the same viral post. Each like: `SELECT like_count FROM posts WHERE id=42 FOR UPDATE; UPDATE posts SET like_count = like_count + 1 WHERE id=42`. Trace: how many transactions execute concurrently? What is the maximum throughput (likes/second) if each lock hold time is 2ms? What alternative data structure would allow 100× higher throughput with eventual consistency?

**Q2.** (TYPE F - Comparison Depth) Compare InnoDB's gap lock approach to phantom read prevention vs. PostgreSQL's SSI (Serializable Snapshot Isolation) on three dimensions: (a) deadlock rate under high concurrent INSERT workloads, (b) overhead for read-only transactions, (c) correctness guarantee (does InnoDB REPEATABLE READ with gap locks give full serializability, or only phantom read prevention?). What class of anomaly can gap locks prevent that SSI would need to abort for, and vice versa?
