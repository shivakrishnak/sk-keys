---
layout: default
title: "MVCC"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 27
permalink: /databases/mvcc/
id: DBF-027
category: Database Fundamentals
difficulty: ★★★
depends_on: Isolation Levels, Transaction, ACID
used_by: Phantom Read, Non-Repeatable Read, VACUUM
related: Locking, WAL, Isolation
tags:
  - database
  - transactions
  - concurrency
  - internals
  - deep-dive
---

# DBF-027 — MVCC

⚡ TL;DR — MVCC (Multi-Version Concurrency Control) lets readers and writers work simultaneously without blocking each other by keeping multiple versions of every row — each transaction sees the version that was current when it started.

| #422            | Category: Database Fundamentals           | Difficulty: ★★★ |
| :-------------- | :---------------------------------------- | :-------------- |
| **Depends on:** | Isolation Levels, Transaction, ACID       |                 |
| **Used by:**    | Phantom Read, Non-Repeatable Read, VACUUM |                 |
| **Related:**    | Locking, WAL, Isolation                   |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Traditional locking: a writer acquires an exclusive lock on a row; every reader of that row must wait until the writer commits. On a product catalog page with 10,000 readers per second and a background price update running every 30 seconds, those 30-second price updates cause 5-minute queues of blocked readers. The database becomes a bottleneck: writes block reads, reads block writes, and the system thrashes under concurrency.

**THE BREAKING POINT:**
At web scale, reads vastly outnumber writes. A pure locking model where reads and writes compete for the same locks makes read-heavy workloads — social feeds, product pages, dashboards — unsustainable. The write throughput must not degrade the read throughput.

**THE INVENTION MOMENT:**
"This is exactly why MVCC was invented — readers never block writers, writers never block readers."

---

### 📘 Textbook Definition

**MVCC (Multi-Version Concurrency Control)** is a concurrency control mechanism used by most modern relational databases (PostgreSQL, MySQL InnoDB, Oracle, SQL Server) that maintains multiple versions of each row simultaneously. When a transaction modifies a row, it creates a new version of that row rather than overwriting the existing one. Readers see the version of the row that was committed at the start of their snapshot (transaction or statement, depending on isolation level), while writers create new versions without touching the versions being read. This eliminates read-write lock contention: readers never block writers and writers never block readers. Write-write conflicts are still resolved via row-level locking.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
MVCC stores multiple timestamped versions of each row so readers and writers can work simultaneously without blocking each other.

**One analogy:**

> A versioned document system (like Google Docs revision history). When someone edits a document, a new version is created — the old version remains accessible. A reader looking at the document sees the version current at the time they opened it. The editor and reader work simultaneously, neither waiting for the other. MVCC is this for database rows.

**One insight:**
MVCC's price is storage: old row versions accumulate until a background process cleans them up (VACUUM in PostgreSQL). Long-running transactions that hold their snapshot open prevent cleanup — old versions accumulate indefinitely, causing "table bloat." The cost of MVCC's concurrency benefit is paid in storage and cleanup complexity.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every transaction sees a consistent snapshot of the database at a fixed point in time.
2. A write creates a new row version; the old version remains for transactions that started before the write.
3. A row version is visible to a reader if and only if: (a) the transaction that created it was committed before the reader's snapshot, and (b) the transaction that deleted/replaced it was NOT committed before the reader's snapshot.
4. Old versions are cleaned up only when no active transaction needs them (VACUUM).

**DERIVED DESIGN:**
PostgreSQL implementation:

- Each row version (tuple) has two hidden fields: `xmin` (transaction ID that inserted this version) and `xmax` (transaction ID that deleted/updated this version, or 0 if current).
- A reader's snapshot is its `xid` (transaction ID) at `BEGIN`.
- Visibility rule: a tuple is visible if `xmin` is committed AND `xmin ≤ snapshot_xid` AND (`xmax` is 0 OR `xmax` is not committed OR `xmax > snapshot_xid`).
- VACUUM removes tuples where `xmax` is committed and no active transaction's snapshot predates `xmax`.

MySQL InnoDB implementation:

- Uses a "cluster index" with row versioning in undo tablespace.
- The current row is in the clustered index; older versions are in the undo log.
- Readers follow an "undo chain" back through versions to find the one visible at their read view.

**THE TRADE-OFFS:**
**Gain:** Readers never block writers; writers never block readers. Higher concurrency for read-heavy workloads. Snapshot isolation at any isolation level above READ UNCOMMITTED.
**Cost:** Storage overhead (multiple row versions). Background cleanup needed (PostgreSQL VACUUM, InnoDB purge thread). Long-running transactions hold back cleanup, causing bloat. Transaction ID wraparound is a critical PostgreSQL operational concern.

---

### 🧪 Thought Experiment

**SETUP:**
A product table has 1 million rows. A background job runs `UPDATE products SET price = price * 1.05` (price inflation). Simultaneously, 5,000 concurrent read requests query product pages.

**WITHOUT MVCC (pure locking):**
The UPDATE acquires shared locks on all 1 million rows (or an exclusive table lock). All 5,000 read requests queue up and wait. Update takes 30 seconds. 5,000 users stare at a loading spinner. When the update finishes, all 5,000 readers unblock simultaneously, creating a thundering herd on the database. Response time: 30+ seconds for users during the update window.

**WITH MVCC:**
The UPDATE creates 1 million new row versions. Each new version has `xmin = update_transaction_id`. The 5,000 concurrent readers each have their own snapshot (`xmin` from when they started). All readers see the old versions (their snapshot predates the update). Readers and the updater run fully concurrently — zero blocking. Readers see consistent pre-update prices; after the update commits, new reader snapshots see the new prices. Response time: normal for all 5,000 users.

**THE INSIGHT:**
MVCC transforms write operations from "block all readers" to "create a parallel version for new readers." The cost is storage for multiple versions, but the gain is consistent, non-blocking reads at any concurrency level.

---

### 🧠 Mental Model / Analogy

> MVCC is like a library with a copy machine. When the librarian wants to update a book (write), they make an updated copy and put it on the shelf, leaving the old copy accessible. Any patron who was already reading the old book continues undisturbed. New patrons who arrive after the update get the new copy. Old copies are only discarded when no patron is reading them anymore.

- "Library copy" → row version in heap/undo log
- "Old book" → `xmin = old_xid` tuple
- "Updated copy" → `xmin = write_xid` new tuple
- "Patron reading old book" → transaction with snapshot before write
- "Discarding old copies" → VACUUM / InnoDB purge
- "Librarian" → write transaction

Where this analogy breaks down: unlike a library, the database is automatic — the "copy" is created atomically at write time, and cleanup is handled by a background process, not a librarian.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
MVCC keeps multiple copies of data, one per change. When you're reading, you see the copy that existed when you started. When someone changes the data, they create a new copy — they don't erase the one you're reading. So reading and writing can happen at the same time without getting in each other's way.

**Level 2 — How to use it (junior developer):**
MVCC is transparent to application developers — it's implemented entirely within the database engine. You benefit from it automatically. Your responsibility is to keep transactions short (long transactions hold old snapshots, preventing cleanup) and to monitor for MVCC bloat via `pg_stat_user_tables.n_dead_tup` in PostgreSQL.

**Level 3 — How it works (mid-level engineer):**
PostgreSQL: every heap tuple has `xmin` (creator txid) and `xmax` (deleter/updater txid). A SELECT evaluates each candidate tuple's visibility: `xmin` must be a committed txid ≤ current snapshot; `xmax` must be 0 or a txid > current snapshot. VACUUM removes tuples where `xmax` is committed and all active snapshots are newer than `xmax`. The PostgreSQL `pg_xact` directory stores the commit/abort status of each transaction ID, checked during visibility evaluation.

**Level 4 — Why it was designed this way (senior/staff):**
PostgreSQL's "heap-based" MVCC keeps old versions in the same heap file as new versions — reads don't chase pointers to an external undo log. This is fast for reads but creates bloat in the heap file. MySQL InnoDB's "undo log-based" MVCC keeps only the current version in the clustered index and stores deltas in the undo log — reads follow undo chains for old versions. This keeps the primary index compact but makes old-version reads slower for long undo chains. PostgreSQL's design favours reads (no undo chain traversal); InnoDB's design favours primary key lookups (compact current-version index). Both approaches converge on similar practical performance for OLTP workloads, diverging at extremes: very long transactions (PostgreSQL bloat) or very deep undo chains (InnoDB read slowdown). Transaction ID wraparound (PostgreSQL's `xid` is 32-bit, ~4 billion unique IDs) is the most critical operational risk — a database that runs for years with poor VACUUM scheduling can approach wraparound, requiring emergency VACUUM.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────┐
│ MVCC: POSTGRESQL ROW VERSIONING              │
├──────────────────────────────────────────────┤
│                                              │
│  Original row: xmin=100, xmax=0, val='A'    │
│                                              │
│  T200 runs: UPDATE SET val='B'              │
│    Creates: xmin=200, xmax=0, val='B'       │
│    Marks old: xmin=100, xmax=200, val='A'   │
│                                              │
│  Heap after update:                          │
│  ┌──────────────────────────────────────┐    │
│  │ xmin=100  xmax=200  val='A'  (old)  │    │
│  │ xmin=200  xmax=0    val='B'  (new)  │    │
│  └──────────────────────────────────────┘    │
│                                              │
│  T150 (snapshot before T200):                │
│    Sees xmin=100: committed, ≤150 ✅        │
│    Sees xmax=200: not committed at T150     │
│    → Returns val='A' (old version)          │
│                                              │
│  T250 (snapshot after T200 commits):         │
│    Sees xmin=200: committed, ≤250 ✅        │
│    Sees xmax=0: no deleter ✅               │
│    → Returns val='B' (new version)          │
│                                              │
│  VACUUM (after both T150 and T250 done):    │
│    xmax=200 committed; no snapshot < 200    │
│    → Delete old tuple (xmin=100, xmax=200)  │
└──────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Writer: UPDATE row → new version created (xmin=writer_xid)
→ Old version marked (xmax=writer_xid)
→ [MVCC ← YOU ARE HERE: version visibility managed]
→ Readers with snapshot < writer_xid see old version
→ Readers with snapshot > writer_xid see new version
→ VACUUM eventually removes old version
```

**FAILURE PATH:**

```
Long-running transaction holds old snapshot
→ VACUUM cannot remove dead tuples older than snapshot
→ Table/index bloat grows → query performance degrades
→ Eventually: transaction ID wraparound risk (PostgreSQL)
```

**WHAT CHANGES AT SCALE:**
At high write throughput, dead tuple accumulation rate can exceed VACUUM cleanup rate — table bloat grows continuously. Autovacuum triggers at a fraction of table size (default 20% dead tuples) but may be too slow for very high write rates. At extreme scale (100M+ rows, 100K+ writes/second), dedicated VACUUM scheduling and table partitioning are required. Transaction ID wraparound is an existential risk: at ~2 billion unvacuumed transactions ahead of current, PostgreSQL begins warning; at ~3 billion, it stops accepting writes and requires emergency maintenance.

---

### ⚖️ Comparison Table

| Approach                   | Read-Write Contention        | Storage Overhead            | Write Overhead             | Best For                         |
| -------------------------- | ---------------------------- | --------------------------- | -------------------------- | -------------------------------- |
| **MVCC (PostgreSQL heap)** | None — readers never block   | Heap bloat from dead tuples | Low (append new version)   | Read-heavy OLTP, analytics       |
| MVCC (InnoDB undo log)     | None                         | Undo log size               | Low-medium                 | OLTP with frequent point lookups |
| Pessimistic Locking        | High — readers block writers | None                        | Lock overhead              | Write-heavy, low-concurrency     |
| Optimistic Locking (app)   | None until commit            | None                        | Retry overhead on conflict | Low-conflict workloads           |

How to choose: MVCC is the default for all modern databases — choose between PostgreSQL's heap MVCC (better for reads) and InnoDB's undo log MVCC (better for primary key lookups) based on workload profile.

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                                             |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MVCC eliminates all locking                 | MVCC eliminates read-write locks; write-write conflicts still require row-level locks; SELECT FOR UPDATE still takes locks under MVCC                               |
| VACUUM is just a cleanup task               | In PostgreSQL, VACUUM is critical for preventing transaction ID wraparound — a missed vacuum cycle can result in a database emergency requiring offline maintenance |
| MVCC is free (no performance cost)          | Dead tuple accumulation degrades index performance (bloated indexes include dead entries); VACUUM consumes I/O; visibility checks add nanosecond overhead per row   |
| Long-running read transactions are harmless | Long reads hold back VACUUM, preventing dead tuple cleanup — they cause unbounded table and index bloat that degrades all subsequent queries                        |

---

### 🚨 Failure Modes & Diagnosis

**1. Table Bloat from Long-Running Transactions**

**Symptom:** `pg_relation_size()` growing unboundedly; query performance degrading; autovacuum running but not reducing table size.

**Root Cause:** A long-running transaction holds an old snapshot. VACUUM cannot remove dead tuples that are visible to the oldest active snapshot. Dead tuples accumulate at the write rate while VACUUM is blocked.

**Diagnostic:**

```sql
-- Find oldest active transaction preventing VACUUM
SELECT pid,
       age(backend_xmin) AS xmin_age,
       now() - xact_start AS duration,
       query, state
FROM pg_stat_activity
WHERE backend_xmin IS NOT NULL
ORDER BY xmin_age DESC;

-- Check dead tuple count per table
SELECT relname,
       n_dead_tup,
       n_live_tup,
       n_dead_tup::float / NULLIF(n_live_tup,0) AS dead_ratio
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY dead_ratio DESC;
```

**Fix:** Terminate the offending long-running transaction (`pg_terminate_backend(pid)`). Run manual VACUUM: `VACUUM ANALYZE table_name`. Configure `idle_in_transaction_session_timeout`.

**Prevention:** Set `idle_in_transaction_session_timeout = '5min'`. Monitor `pg_stat_activity` for transactions with `backend_xmin` older than 5 minutes.

---

**2. Transaction ID Wraparound Emergency**

**Symptom:** PostgreSQL logs `WARNING: database "mydb" must be vacuumed within N transactions`; eventually `ERROR: database is not accepting commands to avoid wraparound data loss`.

**Root Cause:** The 32-bit transaction ID counter (`xid`) is approaching 2^31 transactions ahead of the oldest unfrozen tuple. Without VACUUM FREEZE, old tuples become "invisible" after wraparound.

**Diagnostic:**

```sql
-- Check transaction ID age of oldest unfrozen tuple per database
SELECT datname,
       age(datfrozenxid) AS datfrozenxid_age,
       2147483647 - age(datfrozenxid) AS txns_remaining
FROM pg_database
ORDER BY datfrozenxid_age DESC;

-- Should never approach 2 billion — alert at 500 million
```

**Fix (preventive):** Run `VACUUM FREEZE` on tables with old frozen XIDs. Set `autovacuum_freeze_max_age` lower (e.g., 100 million). Monitor and alert on `age(datfrozenxid)` > 500 million.

**Prevention:** Ensure autovacuum is enabled and properly configured. Include `age(datfrozenxid)` monitoring in production database health checks.

---

**3. MVCC Index Bloat Slowing Queries**

**Symptom:** Index scans slower than expected; `pg_relation_size(index)` disproportionately large; `EXPLAIN` shows higher-than-expected row estimates.

**Root Cause:** Indexes in PostgreSQL include entries for dead tuples — index entries pointing to dead heap tuples (HOT updates partially mitigate this, but only for updates to non-indexed columns). High-write tables develop index bloat independently of heap bloat.

**Diagnostic:**

```sql
-- Check index bloat (requires pgstattuple extension)
CREATE EXTENSION IF NOT EXISTS pgstattuple;
SELECT *
FROM pgstattuple('idx_orders_status');
-- dead_leaf_percent > 20% indicates significant bloat

-- Alternative: check index size vs table size ratio
SELECT
  t.relname AS table,
  i.relname AS index,
  pg_size_pretty(pg_relation_size(i.indexrelid)) AS idx_size,
  pg_size_pretty(pg_relation_size(t.oid)) AS tbl_size
FROM pg_index x
JOIN pg_class t ON t.oid = x.indrelid
JOIN pg_class i ON i.oid = x.indexrelid
WHERE t.relname = 'orders';
```

**Fix:** `REINDEX INDEX CONCURRENTLY idx_orders_status` to rebuild without blocking queries. `VACUUM ANALYZE` reduces index bloat for HOT-eligible tables.

**Prevention:** Set `autovacuum_vacuum_scale_factor` lower (0.01–0.05) for high-write tables. Schedule `REINDEX CONCURRENTLY` during off-peak hours for critical indexes.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Isolation Levels` — MVCC implements snapshot isolation; understand the isolation level spectrum
- `Transaction` — MVCC versioning is transaction-scoped; understand transaction boundaries
- `ACID` — MVCC implements the Isolation property of ACID

**Builds On This (learn these next):**

- `WAL (Write-Ahead Log)` — works alongside MVCC; WAL handles durability, MVCC handles isolation
- `Phantom Read` — the anomaly that MVCC snapshot isolation (REPEATABLE READ) doesn't fully prevent
- `VACUUM` — the PostgreSQL background process that reclaims dead MVCC tuples

**Alternatives / Comparisons:**

- `Locking (Row, Table, Gap, Next-Key)` — the pessimistic alternative to MVCC; readers block writers
- `Isolation` — the ACID property that MVCC implements
- `Optimistic Locking` — application-level alternative to DB-level MVCC for specific use cases

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Keeps multiple row versions so readers    │
│              │ and writers never block each other        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Locks make reads wait for writes —        │
│ SOLVES       │ catastrophic for read-heavy workloads     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Old versions accumulate until VACUUM      │
│              │ cleans them — long txns cause bloat       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — it's the default in PostgreSQL,  │
│              │ MySQL InnoDB, Oracle, SQL Server          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Long-running reporting transactions on    │
│              │ OLTP databases — use a read replica       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Read-write concurrency vs storage bloat   │
│              │ + background cleanup complexity           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Readers get a snapshot; writers create   │
│              │  new copies — nobody waits for nobody"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ WAL → VACUUM → Locking                    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE B — Scale Thought Experiment) A PostgreSQL database processes 100,000 UPDATEs per second on a 10 GB orders table. Autovacuum runs every 5 minutes. At what point does dead tuple accumulation exceed autovacuum's cleanup capacity, how large does the table grow, and what are the three configuration parameters you would tune to prevent unbounded table bloat at this write rate?

**Q2.** (TYPE E — First Principles Challenge) PostgreSQL's MVCC stores old row versions in the same heap as new versions (heap-based MVCC). MySQL InnoDB stores old versions in a separate undo log (undo-based MVCC). Design a workload that makes PostgreSQL's heap MVCC significantly faster than InnoDB's undo MVCC, and then design a second workload where InnoDB's approach is faster. What is the fundamental architectural trade-off that creates this performance divergence?
