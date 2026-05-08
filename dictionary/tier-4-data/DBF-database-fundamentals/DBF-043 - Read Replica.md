---
layout: default
title: "Read Replica"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 43
permalink: /databases/read-replica/
id: DBF-043
category: Database Fundamentals
difficulty: ★★☆
depends_on: Database Replication, WAL, Transaction
used_by: Database Replication, CQRS, Connection Pooling
related: Database Replication, Master-Slave Replication, Write Amplification
tags:
  - database
  - replication
  - scalability
  - intermediate
---

# DBF-043 - Read Replica

⚡ TL;DR - A read replica is a continuously updated copy of the primary database that handles read queries, offloading the primary and scaling read throughput horizontally - at the cost of replication lag (eventual consistency for reads).

| #438            | Category: Database Fundamentals                                     | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------ | :-------------- |
| **Depends on:** | Database Replication, WAL, Transaction                              |                 |
| **Used by:**    | Database Replication, CQRS, Connection Pooling                      |                 |
| **Related:**    | Database Replication, Master-Slave Replication, Write Amplification |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
All reads and writes go to a single database. A report query scanning 100M rows ties up the primary database for 30 seconds - during which write latency spikes because the same CPU/IO is shared. Analytics, dashboards, and batch jobs compete with OLTP writes for the same database resources.

**THE BREAKING POINT:**
Read:Write ratio is typically 80:20 to 95:5 for most applications. Scaling a single database vertically (bigger hardware) is expensive and has an upper limit. The bottleneck is read throughput on the primary - adding more application servers just creates more read pressure on the same DB.

**THE INVENTION MOMENT:**
"Reads don't need the authoritative copy - they just need a recent copy. Run N replicas of the database for reads; keep the primary for writes only."

---

### 📘 Textbook Definition

A **read replica** (also called a **standby replica**, **hot standby**, or **secondary**) is a database instance that continuously receives and applies changes from the **primary** (write) database via **replication**. The replica accepts **SELECT queries** and routes them away from the primary, distributing read load across multiple instances. The replica is **eventually consistent** - it applies changes after the primary commits them, introducing **replication lag** (typically milliseconds to seconds). Read replicas are used for: read scalability (multiple replicas for N× read throughput), analytics isolation (run heavy reports on a replica without impacting OLTP primary), geographic distribution (replica in another region for local read latency), and failover (replica promoted to primary if primary fails).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A read replica is a live copy of your database that handles reads - your writes go to the primary, reads can go anywhere, and replicas stay up-to-date with a small lag.

**One analogy:**

> A library with one librarian who checks out books (write: authoritative record). But thousands of people want to READ the card catalog (read: the list of what's available). Instead of everyone lining up at the librarian's desk, the library makes photocopies of the card catalog and distributes them to 10 reading stations. People read the catalog at reading stations. New books are added at the librarian's desk, and the catalog copies are updated shortly after. The copies might be a few minutes behind - "this book was just checked in, it's not in the copy catalog yet."

- "Librarian's desk" → primary database (single authoritative write path)
- "Card catalog copy" → read replica
- "Reading stations" → replica connections in application
- "New book not in copy yet" → replication lag

**One insight:**
Replication lag is unavoidable with asynchronous replication. It means reads from replicas can return stale data. "Read your own writes" - a user writes data and then immediately reads it - may fail if the read goes to a replica that hasn't received the write yet. Applications must be designed to handle this: either route "read my own write" to the primary, or accept eventual consistency.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Writes go to primary only.** Read replicas are read-only (write attempts are rejected).
2. **Replication lag is always > 0** with async replication. Synchronous replication (no lag) reduces primary write throughput.
3. **Replica applies changes in commit order** - it never shows a partial transaction.
4. **Promoting a replica to primary is a distinct operation** - it requires redirect of write traffic.

**REPLICATION MECHANISMS:**

```
PRIMARY DATABASE
│
│ WAL (Write-Ahead Log) stream
│  → WAL records sent to replica continuously
│
REPLICA DATABASE
│ Applies WAL records as received
│ Maintains its own data files
│ Accepts SELECT queries against its data
```

**POSTGRESQL: STREAMING REPLICATION:**

```sql
-- Primary: configure wal_level and replication slot
-- postgresql.conf (primary)
wal_level = replica          -- required for replication
max_wal_senders = 5          -- max concurrent replica connections
synchronous_commit = off     -- async (default) for read replicas

-- On replica:
-- pg_basebackup: creates initial copy
-- recovery.conf / postgresql.conf (replica):
-- primary_conninfo = 'host=primary port=5432 ...'
-- hot_standby = on  -- allow SELECT queries on replica

-- Check replication lag (on primary)
SELECT
  client_addr,
  state,
  sent_lsn - replay_lsn AS lag_bytes,
  replay_lag
FROM pg_stat_replication;
```

**SYNCHRONOUS vs. ASYNCHRONOUS REPLICATION:**
| Mode | Lag | Durability | Write Throughput Impact |
|---|---|---|---|
| Async (default) | Milliseconds to seconds | Replica can be behind | None |
| Sync (one replica) | Adds network RTT | Zero data loss on primary failure | RTT added to every write commit |
| Sync (quorum) | Adds network RTT | Quorum guarantees | RTT on every write |

**THE TRADE-OFFS:**
**Gain:** Read throughput scales horizontally (N replicas = N× read capacity); heavy read queries isolated from primary; geographic read locality.
**Cost:** Replication lag (stale reads); operational complexity (connection routing logic); replica capacity cost; "read your own writes" consistency challenges; replica falling behind under heavy write load.

---

### 🧪 Thought Experiment

**SETUP:**
An e-commerce platform: 10,000 product reads/second, 100 order writes/second. Single database primary is CPU-saturated at 90%.

**ANALYSIS:**

- Reads: 10,000/s → dominate load
- Writes: 100/s → minor

**WITH ONE READ REPLICA:**

- Product reads → replica
- Order writes → primary
- Primary load: 100 writes/s (from 10,100 ops/s) → drops to ~1% CPU
- Replica handles 10,000 reads/s
- Primary has headroom for write spikes

**REPLICATION LAG SCENARIO:**
User adds a product to cart (write → primary). Application immediately shows cart (read → replica). Replica is 200ms behind. Product appears missing from cart for 200ms - then visible.

**SOLUTION: "Read Your Own Writes":**

```python
# Route writes to primary; route user's own reads to primary too
# (or use sticky session / primary for the same user's reads after write)
def add_to_cart(user_id, product_id):
    primary_db.execute("INSERT INTO cart ...")  # write → primary
    return primary_db.execute("SELECT * FROM cart ...")  # read same user's cart from primary
    # NOT replica_db.execute(...) - would show stale cart
```

**WITH THREE REPLICAS:**

- Round-robin reads across 3 replicas: 10,000/3 ≈ 3,333/s per replica
- Each replica on smaller hardware than primary
- If one replica fails: 2 remaining handle load
- If primary fails: promote one replica (manual or automated with Patroni/etc.)

---

### 🧠 Mental Model / Analogy

> A read replica is like a synchronized mirror that's slightly behind. Your makeup mirror (primary) shows the absolute truth - every hair in real time (writes). Your bathroom mirror across the room (replica) shows you the same thing, with a half-second delay - the light travels slightly slower to that mirror. For most grooming decisions (reads), the slightly-delayed mirror is perfectly fine. For the instant you make a change (write) and need to see it immediately (read your own write) - check the primary mirror, not the replica.

- "Primary mirror" → primary database (authoritative, real-time)
- "Replica mirror" → read replica (slightly delayed)
- "Half-second delay" → replication lag
- "Light traveling slower" → WAL records in transit
- "Grooming decisions" → read queries (tolerant of slight staleness)
- "See change immediately" → read-your-own-write (use primary)

Where this analogy breaks down: Mirrors reflect passively; replicas actively apply WAL records and can fall behind under heavy write load or network congestion - the "mirror" can become significantly outdated (minutes, not milliseconds) if the replica can't keep up with the write rate.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A read replica is a copy of your database that stays up to date automatically. Instead of all database requests going to one server, read-only requests (like showing products, user profiles, dashboards) can go to a copy. The original database focuses on accepting new data and updates. If you have 1 million users reading your site, you can add more copies to handle the load.

**Level 2 - How to use it (junior developer):**
In your application, configure two data sources: one for the primary (all writes + reads that need fresh data), one for the replica (read-only, tolerant of slight staleness). Use Spring's `@Transactional(readOnly=true)` to route to replica. Never send writes to a replica - it will reject them. Be aware of the "read your own writes" problem: after writing something, don't immediately read from a replica - read from the primary for a brief window after the write.

**Level 3 - How it works (mid-level engineer):**
PostgreSQL streaming replication: the primary sends WAL (Write-Ahead Log) records to the replica as they are generated. The replica's `walreceiver` process receives WAL records and writes them to its local WAL. The `startup` process applies these records to the replica's data files. The replica runs in hot standby mode: accepts read-only queries against data files that are being continuously updated. `pg_stat_replication` on the primary shows `replay_lag` - the time difference between when the primary committed and when the replica applied the change. Lag drivers: network latency, replica disk I/O speed, WAL record volume (high write rate → higher lag). AWS RDS read replicas use the same mechanism; AWS Aurora uses a shared storage architecture where replicas share the same storage as the primary - replication lag is much lower (< 100ms typically) because no data copying occurs.

**Level 4 - Why it was designed this way (senior/staff):**
Asynchronous replication (the default) is a deliberate trade-off: zero impact on primary write latency vs. replication lag risk. Synchronous replication (`synchronous_commit = on`) adds network round-trip time to every write commit - in a cross-region setup, this means 100ms RTT for every write. For most OLTP workloads, this is unacceptable. The result: async replication with potential data loss on primary failure (up to the lag window). The "read your own writes" consistency level is a well-defined consistency model from distributed systems: it guarantees that after a write, subsequent reads by the SAME client see that write. Implementing it correctly requires: routing the same user's reads to the primary for a time window after their write, OR using session-level primary routing (sticky), OR using synchronous replication for the specific write and then routing reads anywhere. Aurora's shared storage model largely eliminates this problem by making all replicas share the same storage (lag is sub-second because it's metadata synchronization, not data copying) - at the cost of being tied to Aurora's proprietary storage architecture.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ READ REPLICA: WAL STREAMING REPLICATION              │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Primary DB                                           │
│ ┌────────────────────┐                               │
│ │ Commit transaction │                               │
│ │ Write to WAL       │──── WAL stream ──────────┐   │
│ │ Apply to data page │                           │   │
│ └────────────────────┘                           ↓   │
│                                            Replica DB │
│ App writes ──→ Primary only               ┌─────────┐│
│                                           │Receives ││
│ App reads ──→ Primary (fresh)             │WAL recs ││
│            ──→ Replica (slight lag)       │Applies  ││
│                                           │to pages ││
│ pg_stat_replication.replay_lag:           │Serves   ││
│ = time WAL committed - time applied       │SELECTs  ││
│                                           └─────────┘│
│ Typical lag: 1ms-100ms (LAN)                         │
│              10ms-500ms (cross-datacenter)           │
│              minutes (replica falling behind)        │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
User requests product listing (read)
→ Application routes to replica connection pool
→ [READ REPLICA ← YOU ARE HERE: serve from replica]
→ Replica executes SELECT (no impact on primary)
→ Returns data (up to replay_lag behind primary)
→ Primary: free for writes, low read load
```

**FAILURE PATH - Stale Read:**

```
User posts a comment (write → primary: committed)
App redirects to "view post" page
App reads comments from replica
Replica lag = 300ms; comment not yet applied
User's own comment doesn't appear
→ User thinks "my comment was lost" → rage refresh
→ Multiple duplicate comment submissions

Solution: After write, route user's next reads to primary
          for 1 second (read-your-own-writes window)
          OR use synchronous replication for this write
```

**WHAT CHANGES AT SCALE:**
AWS RDS: add up to 5 read replicas. Aurora: up to 15 replicas, sub-second lag via shared storage. Google Cloud Spanner: horizontally scalable reads with strong consistency (uses Paxos-based replication - no lag for reads within a region). For global-scale reads: DNS-based routing to regional read replicas; acknowledge eventual consistency across regions.

---

### ⚖️ Comparison Table

| Feature                 | Async Read Replica   | Sync Read Replica     | Aurora Replica | Standby (Failover)  |
| ----------------------- | -------------------- | --------------------- | -------------- | ------------------- |
| Replication Lag         | Milliseconds–seconds | ~0 (RTT)              | < 100ms        | Milliseconds        |
| Write Throughput Impact | None                 | High (RTT per commit) | Minimal        | None                |
| Serves Read Traffic     | Yes                  | Yes                   | Yes            | No (until promoted) |
| Automatic Failover      | Manual or tool       | Possible              | Yes (Aurora)   | Yes (with Patroni)  |

How to choose: Async read replicas for read scaling + analytics isolation. Aurora replicas for low-lag with managed failover. Synchronous only when zero data loss is required (financial systems).

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                   |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Read replicas are always consistent                   | Async replication means replicas can be behind by milliseconds to seconds - reads may return stale data; design the application accordingly                               |
| Adding more read replicas always improves performance | Each replica consumes primary resources to stream WAL; too many replicas can increase primary I/O; diminishing returns beyond a certain count                             |
| Read replica failover is instantaneous                | Promoting a replica to primary requires: stopping replication, promoting, redirecting application connection strings - typically 30–120 seconds without automated tooling |
| Replica reads have no latency cost                    | Replica reads have the same execution cost as primary reads, plus replication lag risk; a replica's query plan and indexes are identical to the primary's                 |

---

### 🚨 Failure Modes & Diagnosis

**1. Read Replica Falling Behind (Growing Replication Lag)**

**Symptom:** `replay_lag` on primary increasing; replica serving increasingly stale data; alerts on lag > threshold.

**Root Cause:** Replica's apply rate can't keep up with primary's write rate. Common causes: replica on slower disk than primary; heavy write workload on primary; replica running long-running queries that conflict with WAL apply.

**Diagnostic:**

```sql
-- Primary: check replica lag
SELECT client_addr, state, write_lag, flush_lag, replay_lag
FROM pg_stat_replication;

-- Replica: check if WAL receiver is running
SELECT * FROM pg_stat_wal_receiver;

-- Replica: check if long queries are blocking WAL apply
-- (hot_standby_feedback = on means queries on replica delay cleanup on primary)
SHOW hot_standby_feedback;
```

**Fix:** Upgrade replica disk I/O. Reduce `hot_standby_feedback` if enabled (allows primary to VACUUM aggressively). Terminate long-running queries on replica (`SELECT pg_terminate_backend`). For persistent lag: add a second replica to share read load; reduce write rate on primary (better write patterns, batching).

---

**2. Read-Your-Own-Writes Violation**

**Symptom:** User submits form → sees previous data (as if their save was lost); intermittent, hard to reproduce; correlates with recent deployment that routed all reads to replica.

**Root Cause:** Writes go to primary; reads immediately after the write go to replica (which hasn't received the write yet).

**Diagnostic:**

```
Timeline:
T=0ms: User submits form → write committed on primary
T=1ms: App redirects to "view" page
T=2ms: App reads from replica
T=50ms: Replica applies the write (lag=50ms)
T=2ms < T=50ms → user sees old data
```

**Fix:**

```python
# Option 1: Route to primary immediately after write
# Option 2: Use primary for the same user's reads for 1s after write
# Option 3: Sticky routing: same user always reads from primary

# Spring AbstractRoutingDataSource pattern:
class ReadWriteRoutingDataSource(AbstractRoutingDataSource):
    def determineCurrentLookupKey(self):
        if TransactionSynchronizationManager.isCurrentTransactionReadOnly():
            return "replica"
        return "primary"
```

**Prevention:** Document read consistency requirements per endpoint. Writes + immediate reads of same data → primary. Analytics, reports, listings → replica. Use feature flags to roll out replica routing gradually.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `WAL (Write-Ahead Log)` - replication streams WAL records from primary to replica
- `Database Replication` - the overarching concept; read replicas are one form of replication
- `Transaction` - replica guarantees transaction-level consistency (no partial transaction visible)

**Builds On This (learn these next):**

- `Database Replication` - full picture of replication topologies (master-slave, multi-master)
- `Master-Slave Replication` - read replica is the "slave" in master-slave terminology
- `CQRS` - read replicas are a natural fit for the Query side of Command-Query Responsibility Segregation

**Alternatives / Comparisons:**

- `Database Sharding` - alternative horizontal scaling strategy for writes (not just reads)
- `Caching` - Redis/Memcached as an alternative read offloading strategy (faster but requires cache invalidation)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Live copy of primary that serves reads;   │
│              │ writes go to primary only                 │
├──────────────┼───────────────────────────────────────────┤
│ REPLICATION  │ WAL streaming (PostgreSQL), binlog (MySQL)│
│ MECHANISM    │ Lag: ms to seconds (async)                │
├──────────────┼───────────────────────────────────────────┤
│ MONITOR      │ pg_stat_replication.replay_lag            │
│              │ Alert: lag > 30s (configurable threshold) │
├──────────────┼───────────────────────────────────────────┤
│ KEY PITFALL  │ Read-your-own-writes: route post-write    │
│              │ reads to primary for consistency          │
├──────────────┼───────────────────────────────────────────┤
│ AURORA BONUS │ Shared storage: lag < 100ms; up to 15     │
│              │ replicas with automated failover          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Scale reads horizontally; accept lag     │
│              │  for async consistency"                   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Database Replication → CQRS → Sharding    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Question) Design a read routing strategy for a social media feed application that: (a) supports read-your-own-writes consistency for a user's own posts and profile edits; (b) routes timeline reads (other users' posts) to replicas; (c) handles a replica falling behind by more than 5 seconds. What would your routing layer look like? How does it interact with the connection pool?

**Q2.** (TYPE B - Scale Thought Experiment) A financial trading platform has a primary PostgreSQL with 50,000 price update writes/second. They add 3 read replicas to serve market data reads. Calculate: if each WAL record is 200 bytes, what is the bandwidth each replica needs to receive? At what replication lag (in ms) would traders be making decisions on stale price data? Is an async read replica appropriate for this use case, or should they use synchronous replication or a different architecture?
