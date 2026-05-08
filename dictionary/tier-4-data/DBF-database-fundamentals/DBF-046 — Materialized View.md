---
layout: default
title: "Materialized View"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 46
permalink: /databases/materialized-view/
id: DBF-046
category: Database Fundamentals
difficulty: ★★★
depends_on: Query Planner, Denormalization, Partitioning
used_by: CQRS, Denormalization, Analytics
related: View, Denormalization, Read Replica, CQRS
tags:
  - database
  - performance
  - caching
  - deep-dive
---

# DBF-046 — Materialized View

⚡ TL;DR — A materialized view is a pre-computed query result stored on disk — reads are instant (no recomputation), but the data is stale until refreshed, either on a schedule or on demand.

| #441            | Category: Database Fundamentals              | Difficulty: ★★★ |
| :-------------- | :------------------------------------------- | :-------------- |
| **Depends on:** | Query Planner, Denormalization, Partitioning |                 |
| **Used by:**    | CQRS, Denormalization, Analytics             |                 |
| **Related:**    | View, Denormalization, Read Replica, CQRS    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A dashboard query: `SELECT category, SUM(revenue), COUNT(orders), AVG(order_value) FROM orders JOIN products USING(product_id) WHERE created_at >= DATE_TRUNC('month', NOW()) GROUP BY category`. This query scans 10 million rows, performs a hash join, and takes 8 seconds. The dashboard loads 8 seconds. 100 users open the dashboard simultaneously: 100 × 8-second queries against the primary — the database falls over.

**THE BREAKING POINT:**
Expensive analytical queries on large tables run too slowly for interactive use. Running them on a read replica helps isolate load but doesn't reduce execution time. Caching at the application level loses query composability (you cache a specific result, not a reusable view).

**THE INVENTION MOMENT:**
"Compute the expensive query once and store the result as a real table. Subsequent queries read the stored result — no recomputation. Refresh the stored result periodically as the underlying data changes."

---

### 📘 Textbook Definition

A **materialized view** (or **materialized query table**, MQT) is a database object that stores the pre-computed result of a query as a physical table. Unlike a **regular view** (which re-executes the query on every access), a materialized view stores the result set on disk and returns it directly — query execution is O(1) for the read, not O(n) for the scan. The trade-off: the stored result can be **stale** — it reflects the state of the underlying tables at the last **REFRESH** time, not the current state. **REFRESH MATERIALIZED VIEW** recomputes the result from the current underlying data. PostgreSQL supports **CONCURRENTLY** refresh (reads can proceed during refresh) and scheduled refresh via `pg_cron` or application scheduling.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A materialized view is a cached query result stored as a real table — instant to read, but stale until refreshed.

**One analogy:**

> A newspaper vs. a live news website. The newspaper (materialized view) was printed this morning (last refresh): reading it is instant — all articles pre-arranged, no computing. But it's 6 hours old (stale). The live website (regular view) shows the latest news in real time — but every visit re-fetches all articles from the server. Materialized views are the newspaper: batch-printed, instantly readable, with known staleness.

- "Newspaper printing" → REFRESH MATERIALIZED VIEW (expensive, periodic)
- "Reading the newspaper" → SELECT from materialized view (instant, O(1))
- "6 hours old" → replication lag / staleness since last refresh
- "Live website" → regular view (re-executes query on every SELECT)

**One insight:**
The decision between regular view, materialized view, and application cache is about staleness tolerance: regular view = zero staleness (always current), high query cost; materialized view = configurable staleness, zero query cost; application cache = configurable staleness, zero query cost, but managed outside the database (can get out of sync with DB schema changes).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Stale by design:** A materialized view is a snapshot — not automatically updated when underlying tables change.
2. **REFRESH is expensive** (re-executes the full query) — schedule appropriately.
3. **CONCURRENTLY refresh** requires a unique index on the materialized view and blocks nothing — but takes longer.
4. **Non-CONCURRENTLY refresh** (default) acquires an exclusive lock — blocks reads during refresh.

**POSTGRESQL SYNTAX:**

```sql
-- Create a materialized view
CREATE MATERIALIZED VIEW monthly_revenue AS
SELECT
    DATE_TRUNC('month', o.created_at) AS month,
    p.category,
    COUNT(*) AS order_count,
    SUM(o.amount) AS total_revenue,
    AVG(o.amount) AS avg_order_value
FROM orders o
JOIN products p ON o.product_id = p.id
WHERE o.status = 'completed'
GROUP BY 1, 2
WITH DATA;  -- compute immediately on creation

-- Read (instant — no recomputation):
SELECT * FROM monthly_revenue WHERE month = '2024-06-01';

-- Refresh (recomputes from underlying tables):
REFRESH MATERIALIZED VIEW monthly_revenue;  -- exclusive lock; blocks reads
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue;  -- no lock; needs unique index

-- Add unique index (required for CONCURRENTLY refresh):
CREATE UNIQUE INDEX ON monthly_revenue (month, category);

-- Partial refresh via view structure (only viable if query is designed for it):
-- Cannot refresh individual rows of a materialized view in PostgreSQL
-- → Must refresh the whole view or use incremental approaches (triggers/CDC)
```

**SCHEDULING REFRESH (pg_cron):**

```sql
-- Install pg_cron extension, then schedule:
SELECT cron.schedule(
    'refresh_monthly_revenue',
    '0 * * * *',               -- every hour
    'REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue'
);
```

**INCREMENTAL MATERIALIZED VIEWS (workaround):**
PostgreSQL doesn't natively support incremental refresh (only full recompute). Workarounds: (1) view per recent period (refresh only recent month's partition); (2) application-managed summary tables updated via triggers; (3) use a streaming pipeline (Kafka → ksqlDB) to maintain materialized views incrementally; (4) TimescaleDB continuous aggregates (incremental materialized views built on hypertables).

**THE TRADE-OFFS:**
**Gain:** Instant reads for expensive aggregates; read load isolation; enables interactive dashboards on large datasets.
**Cost:** Stale data (staleness = time since last refresh); REFRESH overhead (full recompute); non-CONCURRENTLY blocks reads; storage overhead for the result.

---

### 🧪 Thought Experiment

**SETUP:**
E-commerce platform. 50 million orders. Dashboard: "top 10 categories by revenue this month". Query takes 12 seconds without materialization.

**WITHOUT MATERIALIZED VIEW:**
100 dashboard users → 100 × 12-second queries = 1,200 CPU-seconds/minute on the database.
Impact on OLTP: order inserts competing for same I/O → latency spikes.
Dashboard: unusable (12-second load time).

**WITH MATERIALIZED VIEW (refresh every 5 minutes):**
`CREATE MATERIALIZED VIEW top_categories AS SELECT ... GROUP BY category;`

- Dashboard reads: 100 × <1ms (scan of 10-row materialized view)
- OLTP impact: zero (dashboard reads pre-computed result)
- Dashboard load time: <100ms
- Staleness: up to 5 minutes

**REFRESH DURING PEAK TRAFFIC (non-CONCURRENTLY):**
`REFRESH MATERIALIZED VIEW top_categories` at 14:00 UTC
→ Acquires exclusive lock on `top_categories`
→ All 100 concurrent dashboard reads blocked for 12 seconds (refresh duration)
→ Users see loading spinner; requests queue

**FIX:**
Add unique index: `CREATE UNIQUE INDEX ON top_categories (category_id);`
Use: `REFRESH MATERIALIZED VIEW CONCURRENTLY top_categories`
→ No lock; refresh takes ~12 seconds
→ During refresh: dashboard reads old data (reads proceed unblocked)
→ After refresh: new data available atomically

---

### 🧠 Mental Model / Analogy

> A materialized view is like a printed report vs. an ad-hoc query. An ad-hoc query (regular view) is like asking an analyst to compute a number fresh — takes 12 minutes every time you ask. A materialized view is a pre-printed report sitting on your desk: glance at it (instant), but it was printed at 9am and it's now 3pm (stale). REFRESH is asking the analyst to reprint the report — expensive, but you only do it periodically. CONCURRENTLY refresh is asking the analyst to print the new report while you're still reading the old one — no interruption.

- "Ad-hoc analyst query" → regular view (always current, always expensive)
- "Pre-printed report" → materialized view (instant read, stale by print time)
- "Report printed at 9am" → REFRESH timestamp
- "3pm staleness" → data age since last refresh
- "Reprinting" → REFRESH (expensive full recompute)
- "Reprint while reading old one" → CONCURRENTLY refresh

Where this analogy breaks down: Printed reports can be annotated and modified; materialized views are read-only snapshots and cannot be directly updated (only via REFRESH from source data).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A materialized view is a pre-computed database result saved to disk. Instead of the database computing a complex calculation every time someone asks for it, it computes it once and saves the answer. When you query it, you get the saved answer instantly. It's like a report that was calculated earlier — fast to read, but not always up-to-the-minute current.

**Level 2 — How to use it (junior developer):**
Use materialized views for: expensive aggregate queries run many times per minute, dashboard data that can tolerate minutes of staleness, analytics queries that hurt OLTP performance when run on the primary. Key settings: create a unique index (required for CONCURRENTLY refresh). Schedule refresh with `pg_cron` at appropriate intervals (hourly, daily — based on staleness tolerance). Always use CONCURRENTLY refresh in production to avoid blocking reads.

**Level 3 — How it works (mid-level engineer):**
PostgreSQL stores a materialized view as a heap table (same physical structure as a regular table). On creation (`WITH DATA`), the query executes and rows are written to the heap. On `REFRESH`: the existing data is replaced atomically (non-CONCURRENTLY: exclusive lock + full replace; CONCURRENTLY: computes new data alongside, then diffs and updates, using the unique index to identify changed rows). CONCURRENTLY refresh requires a unique index because it needs to match new rows to existing rows for the diff operation. Monitoring: `pg_matviews.last_refresh` tracks the last refresh time — query it to detect stale views. `pg_stat_user_tables` monitors the materialized view as a regular table (it is one).

**Level 4 — Why it was designed this way (senior/staff):**
PostgreSQL's materialized views deliberately omit incremental refresh (only full recompute). This is a conscious simplicity choice: incremental refresh requires tracking which rows changed (CDC), differencing old and new computations, and handling complex aggregate semantics (e.g., COUNT(\*) decrement when rows are deleted — which requires knowing what was removed). These complexities are nontrivial for aggregate queries. Systems that implement incremental materialized views (Google Materialize, TimescaleDB continuous aggregates, Flink, Materialize.io) all require significant infrastructure: streaming change feeds, stateful operators, and careful handling of late-arriving data. PostgreSQL's choice to expose full-refresh-only is pragmatically correct: most analytics use cases can tolerate periodic full refresh. For true real-time materialized views (sub-second freshness), the right architecture is a streaming pipeline (Kafka → Flink/ksqlDB → serving layer), not a database materialized view. This is the CQRS pattern at scale: commands write to the transactional store, queries read from materialized projections maintained by a streaming pipeline.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ MATERIALIZED VIEW: READ vs REFRESH PATH              │
├──────────────────────────────────────────────────────┤
│                                                      │
│ REGULAR VIEW (re-executes every time):               │
│ SELECT * FROM monthly_revenue_view                   │
│ → Execute: JOIN orders × products → GROUP BY → 12s  │
│ → Scan 50M rows every time → expensive              │
│                                                      │
│ MATERIALIZED VIEW:                                   │
│                                                      │
│ [READ PATH - instant]                                │
│ SELECT * FROM monthly_revenue_mat                    │
│ → Read pre-stored 10KB result → <1ms                │
│ → No join, no scan, no computation                  │
│                                                      │
│ [REFRESH PATH - periodic]                            │
│ REFRESH MATERIALIZED VIEW CONCURRENTLY monthly...    │
│ → Execute original query: 12s to run                │
│ → Compute new result set                            │
│ → Diff with existing rows (using unique index)      │
│ → Apply changes atomically                          │
│ → Reads unblocked during refresh                    │
│                                                      │
│ Staleness window = time between refreshes           │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
User opens analytics dashboard
→ Application queries materialized view (instant)
→ [MATERIALIZED VIEW ← YOU ARE HERE: pre-computed result]
→ Returns 10 rows in < 1ms
→ No impact on underlying tables or OLTP
→ Staleness: up to 1 hour (last refresh)
```

**REFRESH FLOW:**

```
pg_cron fires every hour: 0 * * * *
→ REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue
→ Executes underlying query: scans orders + products (12s)
→ Computes new result in temp storage
→ Diffs new vs. existing (using unique index on month+category)
→ Applies changes atomically to materialized view
→ Users reading during refresh: see old data (no lock)
→ After refresh: users see new data
→ pg_matviews.last_refresh updated
```

**WHAT CHANGES AT SCALE:**
For dashboards with millions of users: materialized view serves all reads identically regardless of user count. For near-real-time requirements (< 1 minute staleness): combine materialized view (for historical data) with live query (for last N minutes). Use ClickHouse or Redshift instead for OLAP at scale — they use columnar storage designed for aggregate queries, eliminating the need for materialized views in many cases.

---

### ⚖️ Comparison Table

|               | Regular View        | Materialized View     | Application Cache        | Summary Table   |
| ------------- | ------------------- | --------------------- | ------------------------ | --------------- |
| Query cost    | Full recompute      | O(1)                  | O(1)                     | O(1)            |
| Staleness     | None (always fresh) | Since last REFRESH    | Since last invalidation  | Async update    |
| Storage       | None                | Size of result        | Memory (Redis etc.)      | Size of result  |
| Auto-updated  | Yes                 | No (manual/scheduled) | No (manual invalidation) | Via trigger/CDC |
| SQL queryable | Yes                 | Yes                   | No                       | Yes             |

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                                                 |
| --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Materialized views update automatically when data changes | They do NOT in standard PostgreSQL — you must explicitly REFRESH; data is stale until then                                                                                              |
| REFRESH MATERIALIZED VIEW is non-blocking                 | Non-CONCURRENTLY refresh acquires an exclusive lock and blocks ALL reads; only CONCURRENTLY is non-blocking (requires a unique index)                                                   |
| Materialized views are a replacement for indexes          | Completely different: indexes speed up queries against live data; materialized views precompute expensive query results                                                                 |
| Materialized views in all databases work the same         | Different DBMS handle them differently: Oracle supports fast (incremental) refresh; SQL Server has indexed views (auto-maintained by the engine); PostgreSQL only supports full refresh |

---

### 🚨 Failure Modes & Diagnosis

**1. Dashboard Blocked During Non-CONCURRENTLY Refresh**

**Symptom:** Dashboard goes dark for 10–15 seconds at exactly the refresh schedule time; users report intermittent unavailability.

**Root Cause:** `REFRESH MATERIALIZED VIEW` (without CONCURRENTLY) holds an exclusive lock, blocking all reads to the materialized view for the duration of the refresh.

**Diagnostic:**

```sql
-- Check if REFRESH is holding a lock
SELECT pid, query, wait_event_type, wait_event, state
FROM pg_stat_activity
WHERE query LIKE '%REFRESH MATERIALIZED VIEW%';

-- Check what's blocking queries on the MV
SELECT * FROM pg_locks
WHERE relation = 'monthly_revenue'::regclass
  AND granted = true;
```

**Fix:** Add a unique index and switch to CONCURRENTLY:

```sql
CREATE UNIQUE INDEX ON monthly_revenue (month, category);
-- Now use CONCURRENTLY:
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue;
```

**Prevention:** Always create a unique index on materialized views and always use CONCURRENTLY for production refresh. CONCURRENTLY takes longer (requires a full diff) but never blocks reads.

---

**2. Materialized View Severely Stale After Database Restore**

**Symptom:** Analytics dashboard shows months-old data after a database restore or failover; `pg_matviews.last_refresh` shows old timestamp.

**Root Cause:** After a database restore, `last_refresh` reflects the time of the backup, not the current time — materialized views are not automatically refreshed on restore.

**Diagnostic:**

```sql
SELECT schemaname, matviewname, last_refresh, ispopulated
FROM pg_matviews;
-- If last_refresh is old or ispopulated is false: stale or empty
```

**Fix:** After any restore or failover, immediately refresh all materialized views:

```sql
-- Refresh all materialized views in schema
DO $$
DECLARE mv TEXT;
BEGIN
    FOR mv IN SELECT matviewname FROM pg_matviews WHERE schemaname = 'public'
    LOOP
        EXECUTE 'REFRESH MATERIALIZED VIEW CONCURRENTLY public.' || mv;
    END LOOP;
END $$;
```

**Prevention:** Include materialized view refresh in the runbook for database restore and failover procedures. Add `pg_matviews.last_refresh` monitoring — alert if any MV is more than 2× the expected refresh interval behind.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Query Planner / Execution Plan` — understanding why a query is slow is prerequisite to knowing when to materialize it
- `Denormalization` — materialized views are one form of pre-computed denormalization
- `Partitioning (DB)` — partitioned materialized views or building MVs on partitions

**Builds On This (learn these next):**

- `CQRS` — materialized views are the "read model" in CQRS architecture
- `Denormalization` — materialized views are the managed alternative to manual denormalization
- `Analytics (OLAP vs OLTP)` — materialized views bridge the OLTP-OLAP gap within a transactional database

**Alternatives / Comparisons:**

- `Read Replica` — read replicas scale reads without staleness; materialized views precompute expensive queries
- `Application Cache (Redis)` — application-layer caching with manual invalidation vs. DB-managed materialized views
- `Regular View` — always fresh, always expensive; materialized view trades freshness for performance

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Pre-computed query result stored on disk  │
│              │ Instant reads; stale until REFRESH        │
├──────────────┼───────────────────────────────────────────┤
│ REFRESH      │ CONCURRENTLY: non-blocking; needs unique  │
│ OPTIONS      │ index. Default: exclusive lock (blocks).  │
├──────────────┼───────────────────────────────────────────┤
│ SCHEDULING   │ pg_cron: SELECT cron.schedule(...)        │
│              │ Choose interval = staleness tolerance      │
├──────────────┼───────────────────────────────────────────┤
│ MONITOR      │ pg_matviews.last_refresh                  │
│              │ Alert if age > 2× expected interval       │
├──────────────┼───────────────────────────────────────────┤
│ PITFALL      │ Non-CONCURRENTLY blocks reads             │
│              │ No auto-update when source data changes   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Pre-print the report; read instantly;    │
│              │  reprint periodically on a schedule"      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CQRS → Denormalization → Partitioning     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C — Design Question) A SaaS billing system needs a dashboard showing: "total revenue per customer per month for the last 12 months" and "top 100 customers by lifetime value". The `invoices` table has 500M rows. The dashboard is viewed by 10,000 users per day. Design a materialized view strategy: (a) what queries to materialize, (b) refresh schedule and method, (c) how to handle the "freshness vs. availability" trade-off during refresh, (d) what to do when a new invoice is issued and the customer wants to see it immediately.

**Q2.** (TYPE F — Comparison Depth) Compare three approaches to pre-computing aggregates for a real-time analytics dashboard: (a) PostgreSQL materialized view with hourly refresh, (b) application-layer Redis cache with 5-minute TTL, (c) streaming materialized view using Kafka + Materialize.io. Compare: read latency, write complexity, staleness guarantee, failure recovery, and total cost of ownership. When would you choose each?
