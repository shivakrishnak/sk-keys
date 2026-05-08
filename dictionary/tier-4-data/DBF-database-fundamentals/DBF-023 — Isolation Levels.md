---
layout: default
title: "Isolation Levels"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 23
permalink: /databases/isolation-levels/
id: DBF-023
category: Database Fundamentals
difficulty: ★★☆
depends_on: Isolation, ACID, MVCC
used_by: Dirty Read, Non-Repeatable Read, Phantom Read
related: Locking, Optimistic vs Pessimistic Locking, MVCC
tags:
  - database
  - transactions
  - concurrency
  - intermediate
---

# DBF-023 — Isolation Levels

⚡ TL;DR — Isolation levels are the configurable dial between "fast but anomaly-prone" and "correct but slower" — they define exactly which concurrency anomalies a transaction is protected from.

| #418            | Category: Database Fundamentals                  | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------- | :-------------- |
| **Depends on:** | Isolation, ACID, MVCC                            |                 |
| **Used by:**    | Dirty Read, Non-Repeatable Read, Phantom Read    |                 |
| **Related:**    | Locking, Optimistic vs Pessimistic Locking, MVCC |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
The SQL standard defines full isolation (Serializability) as the default. In a high-traffic web application, every read requires a lock; every concurrent write blocks until the reading transaction commits. At 10,000 concurrent users reading product pages, 9,999 users wait behind the one transaction doing a price update. Throughput collapses. The database becomes a single-lane road instead of a highway.

**THE BREAKING POINT:**
Full serializability is too expensive for read-heavy workloads where a slightly stale read is acceptable. But reading uncommitted garbage from in-flight transactions is always unacceptable. The gap between "no isolation" and "full isolation" is enormous — and different workloads need different points on that spectrum.

**THE INVENTION MOMENT:**
"This is exactly why configurable Isolation Levels were created."

---

### 📘 Textbook Definition

**Isolation Levels** are standardised settings defined by SQL-92 that determine which concurrency anomalies a transaction may experience. From weakest to strongest: **READ UNCOMMITTED** (allows dirty reads — sees uncommitted changes from other transactions), **READ COMMITTED** (prevents dirty reads — only sees committed data; default in PostgreSQL and MySQL), **REPEATABLE READ** (prevents dirty and non-repeatable reads — same row read twice returns same result), and **SERIALIZABLE** (prevents all anomalies including phantom reads — results are identical to serial execution). Each level trades some correctness guarantees for increased concurrency.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Isolation levels control how much of other transactions' in-progress work you can see — weaker levels are faster but riskier.

**One analogy:**

> Isolation levels are like news sources. READ UNCOMMITTED is Twitter rumours — you see everything, including unverified in-progress stories that may be retracted. READ COMMITTED is a reputable newspaper — only published, confirmed stories. REPEATABLE READ is yesterday's print edition — consistent throughout, but new stories published after you picked it up won't appear. SERIALIZABLE is reading a sealed archive edition with complete, final history — perfectly consistent but published last.

**One insight:**
READ COMMITTED is the right default for 90% of web applications because web reads are typically "best effort" — showing a user a product price that's 50ms stale is not a problem. The expensive isolation levels should be applied surgically to specific transactions (financial read-modify-write cycles), not globally.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. READ UNCOMMITTED — no protection against concurrent in-progress writes.
2. READ COMMITTED — only committed data visible; snapshot refreshed per statement.
3. REPEATABLE READ — snapshot fixed at transaction start; same row read twice = same result.
4. SERIALIZABLE — full equivalence to serial execution; no concurrency anomalies possible.

**DERIVED DESIGN:**
Each isolation level prevents a specific set of anomalies:

- **Dirty Read**: reading another transaction's uncommitted write. Prevented at: READ COMMITTED.
- **Non-Repeatable Read**: same row read twice in same transaction returns different values. Prevented at: REPEATABLE READ.
- **Phantom Read**: same query run twice returns different rows (new rows inserted by concurrent transaction). Prevented at: SERIALIZABLE.

The higher the isolation level, the more the engine must restrict concurrent access — either via locks (blocking other transactions) or via MVCC snapshot isolation (creating versioned row copies and detecting conflicts at commit).

**THE TRADE-OFFS:**
**Higher isolation:**

- Gain: fewer anomalies; application logic can make stronger assumptions about data consistency.
- Cost: increased lock contention or MVCC version overhead; lower throughput; higher abort/retry rate at SERIALIZABLE.

**Lower isolation:**

- Gain: higher concurrency; more throughput.
- Cost: application code must handle potential anomalies; incorrect assumptions about data consistency can introduce bugs.

---

### 🧪 Thought Experiment

**SETUP:**
Transaction A reads an account balance. Transaction B updates the account balance and commits. Transaction A reads the balance again.

**WHAT HAPPENS AT READ COMMITTED:**

- A reads: $1,000.
- B updates: $900. B commits.
- A reads: $900 (sees B's committed change).
- Non-repeatable read occurred: A saw two different values for the same row within one transaction.

**WHAT HAPPENS AT REPEATABLE READ:**

- A takes a snapshot at transaction start: $1,000.
- B updates: $900. B commits.
- A reads again: $1,000 (snapshot frozen at start).
- Non-repeatable read prevented: A sees a consistent view throughout its transaction.

**THE INSIGHT:**
The "correct" isolation level depends on the application logic. For a simple display query (show user their balance), READ COMMITTED is fine — the slight staleness is acceptable. For a "read balance, compute withdrawal, write new balance" sequence, READ COMMITTED allows a lost update; REPEATABLE READ or SELECT FOR UPDATE is required. The isolation level must match the business logic's consistency requirements.

---

### 🧠 Mental Model / Analogy

> Isolation levels are like the freshness of the menu you're reading at a restaurant. READ UNCOMMITTED: the chef tells you about dishes they're still preparing — some won't be available when you order. READ COMMITTED: you see only dishes currently ready to serve — but the menu can change between the time you look and when you order. REPEATABLE READ: you get a printed menu at the start — what you read is what you get, even if dishes sell out. SERIALIZABLE: the restaurant serves one table at a time — perfectly consistent, no surprises, but slow.

- "Dishes still being prepared" → uncommitted transactions
- "Ready to serve" → committed data (READ COMMITTED)
- "Printed menu at start" → MVCC snapshot (REPEATABLE READ)
- "One table at a time" → serialized execution (SERIALIZABLE)

Where this analogy breaks down: SERIALIZABLE doesn't literally serialize execution — modern SSI runs transactions concurrently and only detects conflicts, which is much faster than the menu analogy implies.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Isolation levels are settings that control how "protected" your database queries are from other people's simultaneous changes. Higher protection = slower performance. Lower protection = faster but with some risk of seeing inconsistent data.

**Level 2 — How to use it (junior developer):**
Set at the transaction level: `SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;` before `BEGIN`. In Spring: `@Transactional(isolation = Isolation.REPEATABLE_READ)`. Default is READ COMMITTED in PostgreSQL and MySQL — fine for most reads. Use REPEATABLE READ or SERIALIZABLE for financial operations, reservation systems, or any read-modify-write cycle where consistency matters.

**Level 3 — How it works (mid-level engineer):**
READ COMMITTED (PostgreSQL): MVCC snapshot refreshed per statement — each query sees the latest committed data at the moment the query starts. REPEATABLE READ (PostgreSQL): MVCC snapshot taken at transaction start — all queries in the transaction see data as of that snapshot. SERIALIZABLE (PostgreSQL): SSI (Serializable Snapshot Isolation) — tracks read-write dependencies between concurrent transactions; if a cycle is detected (indicating a serializability violation), one transaction is aborted with "ERROR: could not serialize access due to concurrent update."

**Level 4 — Why it was designed this way (senior/staff):**
The SQL-92 standard defined isolation levels based on which anomalies they prevent (dirty read, non-repeatable read, phantom read). But this definition is insufficient — it doesn't include "write skew" (two transactions each read disjoint sets, each makes a locally valid write, but together the writes violate a constraint). Write skew is only prevented by SERIALIZABLE. PostgreSQL's SSI (Cahill et al., 2008) made SERIALIZABLE practical by detecting serializability violations without full locking. MySQL InnoDB still uses locking-based SERIALIZABLE, which is why it's rarely used — gap locks can cause deadlocks and block reads. The practical recommendation: PostgreSQL + SERIALIZABLE is usable in production; MySQL + SERIALIZABLE is largely a theoretical option.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────┐
│ ISOLATION LEVELS vs ANOMALIES PREVENTED      │
├──────────────────────────────────────────────┤
│                                              │
│              Dirty  Non-Rep  Phantom         │
│              Read   Read     Read            │
│  READ UNCOMMITTED  ❌       ❌        ❌      │
│  READ COMMITTED    ✅       ❌        ❌      │
│  REPEATABLE READ   ✅       ✅       ~✅*     │
│  SERIALIZABLE      ✅       ✅        ✅      │
│                                              │
│  * MySQL InnoDB REPEATABLE READ prevents     │
│    phantoms via gap locks.                   │
│    PostgreSQL REPEATABLE READ does NOT       │
│    prevent all phantoms.                     │
│                                              │
│  Write Skew: only SERIALIZABLE prevents it  │
│                                              │
│  READ COMMITTED (PostgreSQL MVCC):           │
│    Each statement gets fresh snapshot        │
│    → sees latest committed rows              │
│                                              │
│  REPEATABLE READ (PostgreSQL MVCC):          │
│    Snapshot at transaction start             │
│    → same data throughout transaction        │
│                                              │
│  SERIALIZABLE (PostgreSQL SSI):              │
│    Track read-write conflicts between txns   │
│    → abort if cycle detected                 │
└──────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
BEGIN (REPEATABLE READ) → Snapshot taken
→ [ISOLATION LEVEL ← YOU ARE HERE: snapshot policy applied]
→ All reads return snapshot-consistent data
→ Writes create new row versions
→ COMMIT → new versions visible to future transactions
```

**FAILURE PATH:**

```
SERIALIZABLE: conflict cycle detected at COMMIT
→ ERROR: could not serialize access
→ Application catches error → retries full transaction
→ On retry: fresh snapshot, no conflict
```

**WHAT CHANGES AT SCALE:**
At high concurrency under SERIALIZABLE, the abort/retry rate increases with transaction length and conflict rate. The SSI overhead (tracking read-write dependencies) scales with the number of concurrent transactions accessing overlapping data. Under READ COMMITTED with MVCC, the overhead is minimal — each statement gets a fresh snapshot cheaply. Long-running REPEATABLE READ transactions at scale accumulate MVCC bloat (old row versions kept until the transaction releases its snapshot).

---

### ⚖️ Comparison Table

| Level              | Dirty Read   | Non-Repeatable Read | Phantom Read      | Write Skew   | Throughput |
| ------------------ | ------------ | ------------------- | ----------------- | ------------ | ---------- |
| READ UNCOMMITTED   | ❌ possible  | ❌ possible         | ❌ possible       | ❌ possible  | Highest    |
| **READ COMMITTED** | ✅ prevented | ❌ possible         | ❌ possible       | ❌ possible  | High       |
| REPEATABLE READ    | ✅ prevented | ✅ prevented        | ✅/❌ db-specific | ❌ possible  | Medium     |
| SERIALIZABLE       | ✅ prevented | ✅ prevented        | ✅ prevented      | ✅ prevented | Lower      |

How to choose: Default to READ COMMITTED for web application reads. Upgrade to REPEATABLE READ for read-modify-write cycles on shared resources. Use SERIALIZABLE for financial operations, reservations, or any logic where write skew or phantom reads could corrupt business invariants.

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                                          |
| ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| READ UNCOMMITTED is never safe                    | It's acceptable for approximate counters, analytics that can tolerate dirty reads — never for financial or state-changing operations                                             |
| REPEATABLE READ prevents phantom reads everywhere | PostgreSQL REPEATABLE READ does NOT prevent all phantoms; MySQL InnoDB REPEATABLE READ does prevent them via gap locks — behaviour is database-specific                          |
| SERIALIZABLE means transactions run one at a time | PostgreSQL's SSI runs transactions concurrently and only aborts on detected conflicts; throughput is much higher than literal serialization                                      |
| Higher isolation is always safer                  | Higher isolation introduces serialization failures that require retry logic; applications that don't handle retries properly can have infinite retry loops under high contention |

---

### 🚨 Failure Modes & Diagnosis

**1. Write Skew at REPEATABLE READ**

**Symptom:** Business invariant violated — e.g., two doctors simultaneously remove themselves from on-call, leaving no doctor on-call; the system allowed this despite a rule that at least one must always be on-call.

**Root Cause:** Both transactions read "2 doctors on call," each verified the constraint (1 remaining after their departure = OK), both wrote their update. Neither saw the other's write. Write skew is not prevented by REPEATABLE READ.

**Diagnostic:**

```sql
-- Find the invariant violation
SELECT COUNT(*) FROM on_call_schedule
WHERE date = CURRENT_DATE AND status = 'active';
-- Returns 0 — both doctors removed themselves
```

**Fix:**

```sql
-- Use SERIALIZABLE to prevent write skew
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
SELECT COUNT(*) FROM on_call_schedule
WHERE date = CURRENT_DATE AND status = 'active';
-- If count > 1, proceed to remove self
-- Concurrent transaction attempting same → serialization error
COMMIT;
```

**Prevention:** Identify business invariants that span multiple rows (count constraints, "at least one" rules) and ensure they're protected by SERIALIZABLE or explicit locking, not just REPEATABLE READ.

---

**2. Serialization Errors Under High Contention**

**Symptom:** Application logs show high rate of `ERROR: could not serialize access due to concurrent update`; high retry rate; latency spikes.

**Root Cause:** SERIALIZABLE isolation with high write concurrency to overlapping data — many transactions reading and writing the same rows, creating frequent serializability conflicts.

**Diagnostic:**

```sql
-- PostgreSQL: check serialization failure rate
SELECT datname,
       xact_rollback,
       xact_commit,
       xact_rollback::float /
         (xact_commit + xact_rollback) AS rollback_rate
FROM pg_stat_database
WHERE datname = current_database();
```

**Fix:** Implement retry logic in the application — wrap the transaction in a retry loop (max 3–5 retries with exponential backoff). Reduce transaction scope to minimize overlapping reads.

**Prevention:** Design SERIALIZABLE transactions to be short and narrow (access minimum rows). Use READ COMMITTED with explicit `SELECT FOR UPDATE` for specific rows where serializability is needed — often more efficient than full-transaction SERIALIZABLE.

---

**3. Stale Read at READ COMMITTED Causing Double-Booking**

**Symptom:** Two users book the last item simultaneously; both confirmations sent; inventory shows -1.

**Root Cause:** READ COMMITTED allows non-repeatable reads — both transactions read "1 available," both committed their booking before seeing the other's write.

**Diagnostic:**

```sql
-- Find overbooking evidence
SELECT sku, stock_count FROM inventory WHERE stock_count < 0;

-- Check concurrent booking volume in logs
SELECT DATE_TRUNC('second', created_at) as second,
       COUNT(*) as bookings
FROM orders
GROUP BY 1
ORDER BY bookings DESC
LIMIT 10;
```

**Fix:**

```sql
-- Atomic decrement with guard — no separate read needed
UPDATE inventory
SET stock_count = stock_count - 1
WHERE sku = 'ITEM-123' AND stock_count > 0;

-- Check affected rows = 1; if 0, item was already gone
-- No race condition possible — UPDATE is atomic
```

**Prevention:** For inventory/reservation systems, use atomic UPDATE patterns or SELECT FOR UPDATE rather than READ-then-WRITE. Never assume a read-time snapshot is valid by the time you write.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Isolation` — isolation levels are the configurable settings for the Isolation ACID property
- `ACID` — isolation levels implement the "I" of ACID
- `MVCC` — the mechanism behind most modern isolation level implementations

**Builds On This (learn these next):**

- `Dirty Read` — the specific anomaly prevented by READ COMMITTED
- `Non-Repeatable Read` — the anomaly prevented by REPEATABLE READ
- `Phantom Read` — the anomaly prevented only by SERIALIZABLE

**Alternatives / Comparisons:**

- `Locking (Row, Table, Gap, Next-Key)` — the pessimistic alternative to MVCC for isolation
- `Optimistic Locking` — application-level conflict detection as an alternative to DB isolation levels
- `SELECT FOR UPDATE` — a way to get REPEATABLE READ-level protection on specific rows within READ COMMITTED

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ 4 levels controlling which concurrency    │
│              │ anomalies a transaction is protected from │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Full isolation kills throughput; no       │
│ SOLVES       │ isolation corrupts data — need a dial     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Default (READ COMMITTED) is right for     │
│              │ most reads; use SERIALIZABLE surgically   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Financial/reservation ops: SERIALIZABLE   │
│              │ Standard web reads: READ COMMITTED        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never use READ UNCOMMITTED in production  │
│              │ for data-modifying transactions           │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Anomaly prevention vs concurrency/        │
│              │ throughput / abort rate                   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Pick the weakest level your business     │
│              │  logic can safely tolerate"               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ MVCC → Locking → Deadlock Detection       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A — System Interaction) A financial application uses REPEATABLE READ for all transactions. A "check balance, conditionally transfer" operation reads Account A ($500), reads Account B ($500), verifies Account A has enough, then debits A and credits B. Two concurrent transactions both check-then-transfer from the same two accounts simultaneously. Identify the specific anomaly that REPEATABLE READ fails to prevent here, explain the exact incorrect outcome, and prescribe the correct isolation level and SQL pattern.

**Q2.** (TYPE C — Design Trade-off) Your team debates whether to use SERIALIZABLE isolation globally vs. READ COMMITTED globally with explicit SELECT FOR UPDATE on contested rows. Describe three specific production workloads where SERIALIZABLE globally is the correct choice, and three workloads where READ COMMITTED + SELECT FOR UPDATE is correct. What is the deciding factor between the two approaches?
