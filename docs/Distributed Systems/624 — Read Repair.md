---
layout: default
title: "Read Repair"
parent: "Distributed Systems"
nav_order: 624
permalink: /distributed-systems/read-repair/
number: "0624"
category: Distributed Systems
difficulty: ★★☆
depends_on: Quorum, Replication Strategies, Eventual Consistency
used_by: Cassandra, Riak, DynamoDB, ScyllaDB
related: Anti-Entropy, Hinted Handoff, Quorum, Eventual Consistency, Merkle Tree
tags:
  - distributed
  - consistency
  - repair
  - replication
  - intermediate
---

# 624 — Read Repair

⚡ TL;DR — Read Repair is an opportunistic consistency mechanism where the coordinator, after sending a read to multiple replicas, compares their responses and asynchronously (or synchronously) updates any replica that returned stale data — piggybacking repair onto normal read traffic.

| #624            | Category: Distributed Systems                                           | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Quorum, Replication Strategies, Eventual Consistency                    |                 |
| **Used by:**    | Cassandra, Riak, DynamoDB, ScyllaDB                                     |                 |
| **Related:**    | Anti-Entropy, Hinted Handoff, Quorum, Eventual Consistency, Merkle Tree |                 |

---

### 🔥 The Problem This Solves

**THE COVERAGE PROBLEM WITH QUORUM READS:**
When a client reads with R < N (partial quorum), the coordinator queries all N replicas but waits for only R responses. The unreached replicas might be stale. Even in R=N reads, if one replica is stale, it's repaired only if something detects and corrects it.

Read repair harnesses the data already fetched during a quorum read to repair stale replicas at no extra cost — the coordinator already has the "correct" version (the one with the highest timestamp among responding replicas). Why not use it to fix the stale replica right now?

---

### 📘 Textbook Definition

**Read Repair** is a consistency mechanism in which the coordinator of a read request, after collecting responses from replicas, compares the data versions and asynchronously (or synchronously) writes the latest version back to any replica that returned outdated data. **Two modes**: (1) **Background (asynchronous) read repair**: the coordinator sends the update to stale replicas after returning the result to the client — no latency impact; (2) **Blocking (synchronous) read repair**: the coordinator waits until stale replicas are updated before returning to the client — adds latency but provides read-your-writes consistency for the updated key. **read_repair_chance**: in Cassandra, probability (0.0–1.0) that a read will trigger background repair of non-quorum-read replicas (default 0.1 = 10% of reads trigger background repair). **dclocal_read_repair_chance**: same, but only repairs replicas within the local datacenter. **Used in**: Cassandra (configurable), Amazon Dynamo (described in the Dynamo paper), Riak, ScyllaDB.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
When a quorum read finds that one replica has stale data, read repair takes the fresh data already fetched and pushes it to the stale replica — fixing consistency as a side effect of normal reads.

**One analogy:**

> You ask three librarians for the same book's latest edition. Two return "2024 edition" and one returns "2023 edition." You take the 2024 edition (quorum answer). While you walk out, a helpful coordinator whispers to the librarian who gave the 2023 edition: "Hey, you need to update your copy — here's the 2024 edition." That's read repair. No extra trip to find the discrepancy; it was already visible during the normal request.

**One insight:**
Read repair only repairs keys that are actually read. A cold key that is never read will never be repaired by read repair — that's why anti-entropy exists (it repairs everything, whether accessed or not). Read repair is the opportunistic layer; anti-entropy is the comprehensive layer.

---

### 🔩 First Principles Explanation

**HOW READ REPAIR WORKS IN CASSANDRA:**

```
Read flow with quorum and read repair (RF=3, R=QUORUM=2):

Client → Coordinator:
  SELECT * FROM orders WHERE id = 42;

Coordinator sends digest requests to ALL 3 replicas:
  Replica 1 → full data request (called the "data request")
  Replica 2 → digest request (returns only hash of data)
  Replica 3 → digest request (returns only hash of data)

Coordinator receives:
  Replica 1: {id:42, status:"shipped", ts:100} ← full data
  Replica 2: digest_hash=ABCD1234 ← matches Replica 1 ← quorum achieved
  Replica 3: digest_hash=XXXX5678 ← MISMATCH

Quorum achieved with R1+R2; coordinator returns data to client.

Background Read Repair (async, probability-based):
  Coordinator sends full data request to Replica 3:
    Replica 3 returns: {id:42, status:"processing", ts:50} ← stale!
  Coordinator sends repair write to Replica 3:
    WRITE: {id:42, status:"shipped", ts:100} USING TIMESTAMP 100
  Replica 3 updates: {id:42, status:"shipped", ts:100}

Total: client reads in 1 round trip. Repair happens in background.
Latency impact: READ → none. Background write → minor I/O on Replica 3.
```

**CASSANDRA CONFIGURATION:**

```sql
-- Check current read repair settings for a table:
SELECT read_repair_chance, dclocal_read_repair_chance
FROM system_schema.tables
WHERE keyspace_name = 'myapp' AND table_name = 'orders';

-- Create table with tuned read repair:
CREATE TABLE orders (
    order_id UUID PRIMARY KEY,
    status TEXT,
    total DECIMAL
) WITH read_repair_chance = 0.1        -- 10% of reads trigger background repair
  AND dclocal_read_repair_chance = 0.1; -- 10% trigger local-DC-only repair

-- Disable read repair for high-throughput tables
-- (use anti-entropy / nodetool repair instead):
ALTER TABLE high_volume_events
    WITH read_repair_chance = 0.0
    AND dclocal_read_repair_chance = 0.0;

-- Note: In Cassandra 4.0, read_repair_chance was removed (always 0).
-- Background read repair is now replaced by a newer "read repair" option
-- controlled at the feature level.
```

**WHEN READ REPAIR DOESN'T HELP:**

```
Cold keys (keys never read):
  Example: deleted user accounts (rarely read after deletion).
  A tombstone for user 9999 exists on Replica 1 but not Replica 3
  (Replica 3 was down during the delete).
  If no one reads user 9999, read repair never fires.
  → Zombie row: anti-entropy (nodetool repair) must fix this.

Read with R=1 (local quorum, single replica):
  Coordinator sends request to only 1 replica.
  No comparison possible → no read repair triggered.
  → Must rely on anti-entropy for this replica's consistency.

Reads in AP mode (availability priority):
  Some systems use read-from-any-replica for low-latency reads.
  Read repair disabled in this mode (no comparison across replicas).
```

---

### 🧪 Thought Experiment

**READ REPAIR VS. ANTI-ENTROPY — COVERAGE:**

In a 1 billion key Cassandra table:

- read_repair_chance = 0.1 (10%)
- 1% of keys (10 million) are "hot" (read 1000 times/day)
- 99% of keys (990 million) are "cold" (never read after initial write)

How many keys does read repair cover per day?

- Hot keys: 10M × 1000 reads × 10% = 1 billion repair checks per day (excellent coverage)
- Cold keys: 0 reads × 10% = 0 repair checks (ZERO coverage)

How many keys does anti-entropy (weekly repair) cover?

- All 1 billion keys, regardless of access pattern

Conclusion: Read repair provides excellent coverage for hot keys, zero coverage for cold keys. Anti-entropy covers everything but runs less frequently and at higher cost. Use BOTH.

---

### 🧠 Mental Model / Analogy

> Read repair is like a quality inspector on an assembly line. As products (reads) go past, the inspector checks each one and corrects defects (stale replicas) on the spot. The inspector doesn't go looking for defects — they only see defects as the normal flow passes by. For products that never go down the assembly line (cold keys), the inspector never helps. Anti-entropy is separately like the overnight shut-down inspection where a team inspects every unit in storage, not just those that moved during the day.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** During a quorum read, the coordinator compares data from multiple replicas. If one is stale, it asynchronously sends the correct data back to that replica. This is read repair — it fixes diverged replicas as a side effect of normal reads.

**Level 2:** Cassandra's read repair uses digest requests (hash-only) to compare replicas with low bandwidth. Only if digests diverge does it fetch the full data from the stale replica and repair it. `read_repair_chance = 0.1` means only 10% of reads trigger this repair (higher values increase read latency). Read repair only fires on coordinated reads (QUORUM or higher). R=1 local reads bypass it.

**Level 3:** Blocking vs. background read repair trade-off: blocking repair adds latency but guarantees read-your-writes consistency for the repaired key in the same session. Background repair (default) avoids latency impact but provides only eventual repair. In Cassandra 4.x, `read_repair_chance` was deprecated — a new `read_repair = 'BLOCKING'` option was added per-table for tables that need strong consistency guarantees on reads. ScyllaDB enhances read repair with a scoring system that prioritizes repair of replicas that are most behind.

**Level 4:** Read repair is probabilistic in its coverage. For hot keys (read frequently), R=QUORUM + read_repair_chance creates a near-continuous repair feedback loop. For cold keys, it provides zero coverage. This creates an interesting pathological case: a Cassandra cluster where cold keys have accumulated divergence for months. If suddenly a marketing campaign accesses all those cold keys, the first reads are stale (wrong data), and subsequent reads trigger repair (correct data). The application must be designed to tolerate a brief window of stale reads. Production hardening: for critical data (inventory, financial balances), use R=ALL (every read from all replicas) + LWT (lightweight transactions) to avoid depending on read repair for correctness.

---

### ⚙️ How It Works (Mechanism)

**Read Repair Flow in Production (Detailed):**

```
Cassandra Read Repair — Full Mechanism:

1. Coordinator picks data node and digest nodes based on token ring + snitch.
   Data node: returns full row.
   Digest nodes: return SHA-256 hash of their row version.

2. Coordinator waits for R (quorum) responses.
   If all digests == data node hash: return data to client. No repair triggered.
   If any digest differs:
     a. Fetch full data from the mismatched digest node(s).
     b. Compare timestamps cell-by-cell (in Cassandra, per-column timestamps).
     c. Determine the "merged" correct value (highest timestamp per column).
     d. Identify which column values are stale per replica.
     e. Asynchronously (or synchronously) write the correct value with the
        correct timestamp to the stale replica.
   Return the merged correct value to the client.

Key detail: repair is at the cell (column) granularity in Cassandra.
  Row with 5 columns: 4 might match across all replicas; 1 is stale on Replica 3.
  Repair writes only the 1 stale column to Replica 3. Efficient.

Monitoring in Cassandra:
  nodetool tpstats — ReadRepairStage: Pending / Active / Completed
  high pending ReadRepairStage → read repair queue backing up
    (cluster can't keep up with repairs triggered by reads)
  Fix: reduce read_repair_chance or increase repair thread capacity.
```

---

### ⚖️ Comparison Table

| Repair Mechanism   | Trigger              | Data Coverage        | Latency Impact        | Handles Cold Keys |
| ------------------ | -------------------- | -------------------- | --------------------- | ----------------- |
| Read Repair        | On read              | Only read keys       | Marginal (async)      | No                |
| Hinted Handoff     | On write (node down) | Recent missed writes | None                  | No                |
| Anti-Entropy       | Background schedule  | All keys             | High (background I/O) | Yes               |
| Write Quorum (W=N) | On every write       | Prevents divergence  | Yes (write latency)   | N/A               |

---

### ⚠️ Common Misconceptions

| Misconception                                                 | Reality                                                                                                                                                                                                              |
| ------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Read repair makes quorum reads strongly consistent            | Read repair improves eventual consistency but is probabilistic. With read_repair_chance=0.1, only 10% of reads trigger repair. For strong consistency, use LWT (Lightweight Transactions) or R=ALL + W=ALL           |
| Read repair is a Cassandra-only feature                       | Read repair was described in Amazon's Dynamo paper (2007) and is implemented in Riak, ScyllaDB, and many distributed KV stores                                                                                       |
| Disabling read repair improves read performance significantly | read_repair_chance triggers only on digests that DON'T match. If replicas are already in sync (common case), no repair fires. The performance overhead is proportional to how out-of-sync your replicas actually are |

---

### 🚨 Failure Modes & Diagnosis

**ReadRepairStage Queue Backup**

**Symptom:** Cassandra cluster read latency increasing over time. nodetool tpstats shows
ReadRepairStage: 5,000 pending, 0 completed/sec. Write errors on internal repair writes.
Reads are returning correct data but slowly.

Cause: read_repair_chance = 1.0 (100% of reads trigger repair). After a node outage
(missed 2 hours of writes), every read triggers repair on the recovered node. With 50K
reads/sec, 50K repair writes/sec are being submitted to the recovered node. The recovered
node is overwhelmed: it's processing catch-up compaction AND 50K repair writes.

**Fix:** (1) Immediately: `ALTER TABLE ... WITH read_repair_chance = 0.0` to stop triggering
more repair. (2) Let the recovered node catch up via anti-entropy (nodetool repair) at
a controlled rate (-seq flag for sequential, lower I/O). (3) Reduce read_repair_chance to
0.1 (10%) after cluster stabilizes. (4) Add ReadRepairStage queue depth to Prometheus
alerts: alert if > 1000 pending for > 5 minutes.

---

### 🔗 Related Keywords

- `Anti-Entropy` — comprehensive background repair for ALL keys (including cold ones)
- `Hinted Handoff` — repair mechanism for writes missed during node downtime
- `Quorum` — the consistency level that enables read repair (R > 1 needed)
- `Eventual Consistency` — the consistency model that read repair helps achieve
- `Merkle Tree` — the data structure used in anti-entropy (not read repair, which uses digests)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  READ REPAIR                                             │
│  Trigger: coordinator reads from multiple replicas       │
│  Detects: digest mismatch between replicas               │
│  Repairs: sends correct version to stale replica         │
│  Mode: async (default) or blocking (Cassandra 4.x)       │
│  Coverage: hot keys only (keys that are read)            │
│  Config: read_repair_chance (Cassandra, 0.0–1.0)         │
│  Pair with: anti-entropy for cold-key coverage           │
│  Don't rely on: for strong consistency (use LWT or R=ALL)│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Cassandra table has read_repair_chance = 0.0 (disabled) and a 3-month-old node failure that was repaired (nodetool repair) correctly. A new engineer disables anti-entropy scheduled jobs to save I/O. Six months later, a node is replaced (new node joins, streams data from other replicas). Under what conditions can read_repair_chance = 0.0 + no anti-entropy lead to the new replica being permanently inconsistent for some keys? What is the specific missing piece?

**Q2.** Read repair uses LWW (highest timestamp wins) at the cell level. If a stale replica has a column value with a higher timestamp than the "correct" replica (due to a clock skew event in the past), read repair will actually write the WRONG value to the "correct" replicas. Describe the sequence of events that causes this timestamp inversion bug, and what the correct operational response is when clock skew is detected in a Cassandra cluster.
