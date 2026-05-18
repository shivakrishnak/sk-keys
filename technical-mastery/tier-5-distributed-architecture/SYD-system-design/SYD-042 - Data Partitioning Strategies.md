---
id: SYD-042
title: Data Partitioning Strategies
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-031, SYD-041
used_by: ""
related: SYD-031, SYD-032, SYD-034, SYD-041
tags:
  - architecture
  - database
  - scalability
  - partitioning
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 42
permalink: /technical-mastery/syd/data-partitioning-strategies/
---

⚡ TL;DR - Data partitioning splits a dataset into
disjoint subsets (partitions) distributed across
nodes or stored in separate files. The four main
strategies are: horizontal partitioning (sharding by
row), vertical partitioning (by column), range
partitioning (by value range), and hash partitioning
(by hash of key). The right strategy depends on query
patterns (range queries vs point lookups), data size
growth, and hotspot risk. Partitioning decisions are
architectural - changing them later requires data
migration.

| #042 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Sharding, Write-Ahead Logging (System) | |
| **Used by:** | (multiple design entries) | |
| **Related:** | Sharding, Hot Shard, Denormalization for Scale, Write-Ahead Logging | |

---

### 🔥 The Problem This Solves

**SINGLE PARTITION BOTTLENECK:**
A time-series metrics database stores 10 billion rows
in one PostgreSQL table. Queries need data from the
last 7 days. The query planner scans 10B rows even
for a 7-day window. Table vacuum takes 8 hours. Adding
indexes barely helps: they are too large to fit in
memory. The table is unmaintainable.

**WITH PARTITIONING:**
Partition by month. Each partition holds ~30 days of
data (~800M rows/month). The 7-day query hits only
1 partition (partition pruning: the planner knows
which partition contains recent data). Old partitions
(>90 days) can be dropped in milliseconds (DROP
TABLE, not DELETE). Maintenance is fast. Queries
are fast. The dataset is operationally manageable.

---

### 📘 Textbook Definition

**Data partitioning:** The process of dividing a large
dataset into smaller, disjoint subsets (partitions)
based on a partition key and strategy. Each partition
can be stored independently (different nodes, disks,
or files). Queries that include the partition key
can be pruned to touch only relevant partitions.

**Four main strategies:**

1. **Horizontal partitioning (row-based sharding):**
   Rows split across partitions by a row attribute.
   All columns present in each partition. Reduces
   row count per partition.

2. **Vertical partitioning (column-based):**
   Columns split across tables. Hot columns in one
   table; cold columns in another. Reduces row width
   per access.

3. **Range partitioning:** Rows go to partitions based
   on value ranges. Efficient for range queries; risk
   of hot partitions at boundaries.

4. **Hash partitioning:** Rows go to partition `hash(key)
   % N`. Even distribution; efficient for point
   lookups; poor for range queries.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Split data by a key so each query only touches the
relevant slice. Different split strategies optimize
for different query patterns.

**One analogy:**
> A filing cabinet with multiple drawers:
> - Horizontal (by row): each drawer holds
>   documents for a date range (Jan, Feb, Mar).
>   Find "March reports": open March drawer only.
>
> - Vertical (by column): one drawer for "contact info,"
>   another for "financial data." For a quick name
>   lookup: open the contact drawer, not the large
>   financial drawer.
>
> - Hash: documents distributed by a code on the cover.
>   Consistent spread; no range queries (need to check
>   all drawers for "all documents from Q1").

**One insight:**
The partition key determines query efficiency. A
query that includes the partition key in its WHERE
clause can skip all irrelevant partitions (partition
pruning). A query that does not include the partition
key must scan all partitions (full scan). Design
partitions around the most common query pattern.

---

### 🔩 First Principles Explanation

**STRATEGY DETAILS:**

**1. Range Partitioning:**
```sql
-- PostgreSQL range partitioning by date
CREATE TABLE metrics (
    id BIGINT,
    ts TIMESTAMP,
    value FLOAT
) PARTITION BY RANGE (ts);

CREATE TABLE metrics_2025_01
    PARTITION OF metrics
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE metrics_2025_02
    PARTITION OF metrics
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- Query with partition key: hits 1 partition
SELECT * FROM metrics
WHERE ts >= '2025-01-15' AND ts < '2025-01-16';
-- EXPLAIN: "Seq Scan on metrics_2025_01" only

-- Drop old data: DROP TABLE, not DELETE
DROP TABLE metrics_2024_01;  -- instant; no vacuum needed

Best for: time-series, sequential IDs, date ranges
Risk: hot partition (all new writes to latest partition)
```

**2. Hash Partitioning:**
```sql
-- PostgreSQL hash partitioning by user_id
CREATE TABLE user_events (
    user_id BIGINT,
    event_type VARCHAR,
    ts TIMESTAMP
) PARTITION BY HASH (user_id);

CREATE TABLE user_events_0
    PARTITION OF user_events
    FOR VALUES WITH (modulus 4, remainder 0);

CREATE TABLE user_events_1
    PARTITION OF user_events
    FOR VALUES WITH (modulus 4, remainder 1);
-- ... 4 partitions total

-- Even distribution: each partition gets ~25% of rows
-- Point lookups: fast (know which partition to hit)
-- Range query on ts: must scan ALL 4 partitions

Best for: point lookups, even write distribution
Risk: no range queries without partition key
```

**3. Vertical Partitioning:**
```sql
-- Split wide user table: hot columns vs cold columns
-- Original: users(id, name, email, bio, avatar,
--   preferences_json, metadata_json)  -- 50KB per row!

-- Hot access pattern: name, email for auth (~100 bytes)
CREATE TABLE users_core (
    id BIGINT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    created_at TIMESTAMP
);

-- Cold access pattern: profile data (~50KB)
CREATE TABLE users_profile (
    user_id BIGINT PRIMARY KEY REFERENCES users_core,
    bio TEXT,
    avatar_url TEXT,
    preferences_json JSONB,
    metadata_json JSONB
);

-- Auth query: touches only users_core (100 bytes/row)
-- No longer pulls 50KB profile data unnecessarily
-- users_core fits entirely in memory (hot cache)

Best for: wide tables with mixed hot/cold columns
Trade-off: JOINs needed for full record; denormalize
  if frequently accessed together
```

**4. Composite Partitioning:**
```sql
-- Range + Hash (hybrid)
-- Range by month: limits scan to recent data
-- Hash by user_id: distributes within month

CREATE TABLE events_2025_01
    PARTITION OF events
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01')
    PARTITION BY HASH (user_id);

-- Sub-partitions: events_2025_01_shard_0, _shard_1, ...
-- Range query on month: hits 1 range partition
-- Within month: distributed across hash sub-partitions
-- Eliminates both range hot partition AND write bottleneck
```

**PARTITION PRUNING:**
```
Partition pruning = query planner skips irrelevant
partitions when partition key is in WHERE clause.

Enabled when:
  - WHERE clause includes partition key with
    equality or range comparison
  - Partition key is not transformed (no functions)
  
Disabled when:
  - WHERE ts::DATE = '2025-01-15'
    (cast applied to ts → planner can't prune)
  
  - WHERE ts >= (SELECT max_ts FROM settings)
    (runtime value → static pruning not possible;
     use dynamic partition pruning if supported)

Rule: Never apply functions to the partition key
in WHERE clauses. Use column = value, not func(column).
```

---

### 🧪 Thought Experiment

**SCENARIO: E-commerce order history - what to partition by?**

Table: `orders(id, user_id, status, created_at, total_amount)`
Scale: 5 billion rows, 50 million users, 3 years of data.

**Option A: Range partition by created_at (monthly)**
- 36 partitions (3 years × 12 months)
- "Orders in last 30 days": hits 1-2 partitions ✓
- "All orders for user_id=X": scans all 36 partitions ✗
- Drop old data by month: instant ✓
- New orders all go to latest partition: hot partition ✗

**Option B: Hash partition by user_id (16 shards)**
- "All orders for user_id=X": hits exactly 1 partition ✓
- "Orders in last 30 days": scans all 16 partitions ✗
- Old data cleanup: must DELETE (slow), not DROP ✗
- Even write distribution: no hot partition ✓

**Option C: Composite (range by month + hash by user_id)**
- Monthly partitions × 4 hash shards = 36 × 4 = 144 partitions
- "All orders for user_id=X in last 30 days": 4 partitions ✓
- Drop old months: instant ✓
- Even write distribution ✓
- Complexity: 144 partitions to manage ✗

**THE WINNER:** Depends on the top query pattern.
If "orders by user" is 90% of queries: Option B.
If "orders by date" is 90% of queries: Option A.
If both are critical: Option C (at operational cost).

Most e-commerce systems: Option B (by user_id hash)
because user timelines are the primary access pattern.

---

### 🧠 Mental Model / Analogy

> Data partitioning is like organizing a library by
> different indexing schemes:
>
> Range (by date): books shelved by publication year.
> "Find all 2023 books": one section. Fast.
> "Find all books by Stephen King": walk every shelf.
>
> Hash (by title hash): books distributed by a code.
> "Find 'Dune'": code → exact shelf. Fast.
> "Find all sci-fi books": walk every shelf.
>
> Vertical (by topic depth): reference section and
> popular section. Checking author: popular (small).
> Full text: reference (large). Don't pull the full
> text when you only need the author.
>
> The right scheme depends on your most common query.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Split a big table into smaller pieces. Queries that
know which piece to look in are much faster. Old pieces
can be deleted quickly.

**Level 2 - How to use it (junior developer):**
PostgreSQL: `PARTITION BY RANGE` or `PARTITION BY HASH`.
MySQL: similar syntax. For time-series data: partition
by month/week. For user data: partition by user_id hash.
Always include the partition key in WHERE clauses.

**Level 3 - How it works (mid-level engineer):**
Partition pruning is automatic when the WHERE clause
filters on the partition key. The query planner checks
partition constraints and skips partitions that cannot
contain matching rows. Monitor with EXPLAIN to confirm
pruning is happening. Apply indexes within partitions
(local indexes) rather than global indexes for better
parallelism.

**Level 4 - Why it was designed this way (senior/staff):**
Partitioning solves three separate problems: (1) query
performance via pruning, (2) maintenance efficiency
(DROP TABLE for old partitions instead of DELETE), and
(3) write scalability (parallel writes to separate
partitions, separate I/O subsystems, different nodes).
These three problems often require different partitioning
strategies. For example, time-series: range by date
(maintenance + pruning) combined with hash sub-partitions
(write parallelism).

**Level 5 - Mastery (distinguished engineer):**
The partition key selection has permanent architectural
implications. Adding a new partition key after the table
is large requires migrating billions of rows. The system
design question is: what query pattern are you optimizing
for, and will that pattern hold for the next 5 years?
E-commerce systems often start with time-based partitioning
(easy to reason about) but eventually need user-based
partitioning as the access pattern shifts from "what
happened today" (operational) to "what did this user
order" (account management). Plan for evolution by
choosing a partition key that works for the dominant
access pattern AND supports data archival.

---

### ⚙️ How It Works (Mechanism)

**Partition pruning in PostgreSQL query planning:**

```
┌──────────────────────────────────────────────────────┐
│ PARTITION PRUNING                                   │
│                                                      │
│ Table: orders PARTITION BY RANGE (created_at)       │
│   orders_2024_12: 2024-12-01 to 2025-01-01         │
│   orders_2025_01: 2025-01-01 to 2025-02-01         │
│   orders_2025_02: 2025-02-01 to 2025-03-01         │
│                                                      │
│ Query:                                               │
│   SELECT * FROM orders                              │
│   WHERE created_at >= '2025-01-15'                  │
│     AND created_at < '2025-01-16'                   │
│                                                      │
│ Planner checks each partition constraint:           │
│   orders_2024_12: [Dec 2024] - no overlap → SKIP    │
│   orders_2025_01: [Jan 2025] - overlap → SCAN       │
│   orders_2025_02: [Feb 2025] - no overlap → SKIP    │
│                                                      │
│ Result: scan 1 of 3 partitions                      │
│ If 36 monthly partitions: scan 1 of 36              │
│ 36x faster than full table scan                     │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Automated monthly partition creation**
```python
# Automatically create next month's partition
# Run as a monthly cron job

import psycopg2
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def create_next_month_partition(conn, table_name: str):
    """Create the partition for the next calendar month."""
    today = datetime.utcnow().date()
    next_month_start = (today.replace(day=1) +
                        relativedelta(months=1))
    next_month_end = next_month_start + relativedelta(months=1)

    partition_name = (
        f"{table_name}_"
        f"{next_month_start.strftime('%Y_%m')}"
    )

    sql = f"""
        CREATE TABLE IF NOT EXISTS {partition_name}
        PARTITION OF {table_name}
        FOR VALUES FROM ('{next_month_start}')
                     TO ('{next_month_end}');
    """
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print(f"Created partition: {partition_name}")

def drop_old_partitions(conn, table_name: str,
                          retention_months: int = 13):
    """Drop partitions older than retention window."""
    cutoff = (datetime.utcnow().date().replace(day=1) -
              relativedelta(months=retention_months))
    partition_prefix = f"{table_name}_"

    with conn.cursor() as cur:
        # Find all partitions for this table
        cur.execute("""
            SELECT relname FROM pg_class
            WHERE relname LIKE %s
              AND relkind = 'r'
        """, [f"{partition_prefix}%"])

        for (partition_name,) in cur.fetchall():
            # Parse date from partition name
            parts = partition_name.replace(
                partition_prefix, "").split("_")
            if len(parts) == 2:
                part_date = datetime(
                    int(parts[0]), int(parts[1]), 1).date()
                if part_date < cutoff:
                    cur.execute(
                        f"DROP TABLE {partition_name}")
                    print(f"Dropped: {partition_name}")
    conn.commit()
```

**Example 2 - Partition key query anti-pattern**
```sql
-- BAD: Function on partition key disables pruning
-- Table partitioned by RANGE(created_at)

EXPLAIN SELECT * FROM orders
WHERE DATE(created_at) = '2025-01-15';
-- Result: scans ALL partitions (function applied to key)
-- DATE() function prevents partition pruning

-- BAD: Cast disables pruning
EXPLAIN SELECT * FROM orders
WHERE created_at::DATE = '2025-01-15';
-- Also scans ALL partitions

-- GOOD: Range comparison on raw partition key
EXPLAIN SELECT * FROM orders
WHERE created_at >= '2025-01-15 00:00:00'
  AND created_at <  '2025-01-16 00:00:00';
-- Result: scans ONLY orders_2025_01 partition
-- Partition pruning active: 36x speedup for 36 partitions

-- RULE: Never apply functions to the partition key.
-- Use raw comparisons: >=, <=, =, BETWEEN.
```

---

### ⚖️ Comparison Table

| Strategy | Best Query Pattern | Hot Partition Risk | Data Archival | Distribution |
|---|---|---|---|---|
| **Range (date)** | Time-based queries | Yes (latest partition) | Easy (DROP TABLE) | Uneven (recent data hot) |
| **Range (ID)** | Sequential ID lookups | Yes (latest IDs) | Easy | Uneven |
| **Hash** | Point lookups by key | No (even spread) | Hard (must DELETE) | Even |
| **List** | Categorical filters | Depends on cardinality | Medium | Uneven if skewed |
| **Composite (range + hash)** | Both range and point | Reduced | Easy | Even within range |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Partitioning is the same as sharding | Partitioning typically refers to dividing one table across multiple files/indexes on a single node. Sharding distributes partitions across multiple nodes (network boundary). Partitioning is a prerequisite for sharding. |
| More partitions is always better | Each partition adds overhead: the query planner must check each partition's constraints. At 1,000+ partitions, planning time itself becomes significant. For PostgreSQL: 100-500 partitions is typically manageable; beyond 1,000 requires careful configuration (`enable_partition_pruning`, `constraint_exclusion`). |
| Partition pruning works even with OR conditions | OR conditions on partition keys typically prevent pruning because the planner cannot determine which partitions are excluded. Use UNION ALL to manually specify partition sub-queries when OR would defeat pruning. |

---

### 🚨 Failure Modes & Diagnosis

**Missing Partition for New Data (Constraint Violation)**

**Symptom:**
On the first day of a new month, insert operations fail:
`ERROR: no partition of relation "metrics" found for row`
The monthly partition for the new month was not created.

**Root Cause:**
The cron job creating next month's partition did not run
(or ran but failed silently). PostgreSQL has no "default
catch-all" partition configured.

**Fix:**
```sql
-- Immediate fix: create the missing partition manually
CREATE TABLE metrics_2025_03
    PARTITION OF metrics
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');

-- Prevention option 1: default partition (catch-all)
CREATE TABLE metrics_default
    PARTITION OF metrics DEFAULT;
-- Rows with no matching partition go here
-- Periodic job moves them to correct partition
-- Prevents data loss but masks the missing partition bug

-- Prevention option 2: create partitions in advance
-- Cron job creates partitions for next 3 months
-- (not just next 1 month)
-- Reduces blast radius of cron failures

-- Prevention option 3: alert when latest partition
-- covers less than 30 days into the future
SELECT max(upper(part.partrangedatums[1].val::text)::date)
FROM pg_partitioned_table pt
JOIN ...
-- Alert if < (NOW() + INTERVAL '30 days')
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Sharding` - sharding distributes partitions across
  nodes; partitioning creates the partitions
- `Write-Ahead Logging (System)` - WAL is partitioned
  per shard in distributed systems

**Builds On This (learn these next):**
- `Hot Shard` - range partitioning's primary failure mode
- `Denormalization for Scale` - data modeling to
  keep partition-local queries efficient

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ RANGE         │ Time series, archival. Easy DROP TABLE. │
│               │ Risk: hot latest partition.             │
├───────────────┼─────────────────────────────────────────┤
│ HASH          │ Even distribution. Point lookups.       │
│               │ No archival (must DELETE). No range QRY.│
├───────────────┼─────────────────────────────────────────┤
│ VERTICAL      │ Split hot/cold columns. Reduces row     │
│               │ width for frequent queries.             │
├───────────────┼─────────────────────────────────────────┤
│ COMPOSITE     │ Range × Hash: best of both.             │
│               │ Cost: more partitions to manage.        │
├───────────────┼─────────────────────────────────────────┤
│ PRUNING RULE  │ WHERE clause must use raw column,       │
│               │ not func(column). Range comparisons OK. │
├───────────────┼─────────────────────────────────────────┤
│ AUTOMATION    │ Create next month's partition via cron. │
│               │ Create 3 months in advance for safety.  │
├───────────────┼─────────────────────────────────────────┤
│ ONE-LINER     │ "Split by access pattern. Range for     │
│               │  time; hash for point lookups."         │
├───────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE  │ URL Shortener Design → Rate Limiter Desi│
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Range partitioning: great for time-series, easy
   archival (DROP TABLE), bad for hotspots. Hash
   partitioning: even distribution, good for point
   lookups, bad for archival and range queries.
2. Partition pruning only works when the WHERE clause
   filters directly on the partition key with a raw
   comparison. Never apply functions to the partition
   key in queries.
3. Automate partition creation (cron job, 3 months
   in advance). Missing partition = data loss or errors.
   Monitor: alert when latest partition covers less
   than 30 days into the future.

**Interview one-liner:**
"Data partitioning divides a table into disjoint subsets. Range
partitioning (by date or ID) enables partition pruning for range
queries and instant data archival via DROP TABLE - ideal for
time-series. Hash partitioning distributes rows evenly and speeds
point lookups, but cannot support range queries or easy archival.
Composite (range + hash) combines both. The critical design rule:
never apply functions to the partition key in WHERE clauses
(DATE(col) defeats pruning; use col >= '...' instead). Automation:
use a cron job to create next month's partitions at least 3 months
in advance, with an alert when the latest partition is within 30 days
of covering new data - missing partitions cause data loss."
