---
layout: default
title: "Database Sharding"
parent: "Database Fundamentals"
nav_order: 53
permalink: /databases/database-sharding/
id: DBF-053
category: Database Fundamentals
difficulty: ★★★
depends_on: Partitioning (DB), Consistent Hashing, Distributed Systems
used_by: NoSQL & Distributed Databases, System Design, Microservices
related: Partitioning (DB), Multi-Master Replication, Consistent Hashing
tags:
  - database
  - sharding
  - distributed-systems
  - deep-dive
---

# DBF-053 — Database Sharding

⚡ TL;DR — Sharding horizontally splits a database across multiple independent servers (shards), each owning a subset of the data, enabling write throughput and storage to scale beyond what any single server can handle — but at the cost of cross-shard query complexity and resharding pain.

| #448            | Category: Database Fundamentals                                 | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------- | :-------------- |
| **Depends on:** | Partitioning (DB), Consistent Hashing, Distributed Systems      |                 |
| **Used by:**    | NoSQL & Distributed Databases, System Design, Microservices     |                 |
| **Related:**    | Partitioning (DB), Multi-Master Replication, Consistent Hashing |                 |

---

### 🔥 The Problem This Solves

**SINGLE-SERVER CEILING:**
1 billion users. Each with a profile, posts, messages. A single PostgreSQL server: 64 cores, 512 GB RAM, 100TB NVMe. It's the biggest server money can buy. Still insufficient: 500,000 writes/second saturates the I/O. 500TB of data exceeds storage. Query latency degrades because the B-tree index spans 500TB. Vertical scaling has physically ended.

**PARTITIONING (SAME SERVER) IS NOT ENOUGH:**
Partitioning splits data across multiple tables on the same server. Reduces query scope. But still one server: one CPU, one I/O bus, one network card. The ceiling is still the single machine.

**SHARDING (DIFFERENT SERVERS):**
Split the data across N independent servers. User 1–250M → Shard 1 (its own server, its own disk, its own CPU). User 250M–500M → Shard 2. Etc. Now write throughput = N × per-server throughput. Storage = N × per-server storage. This is horizontal scale-out — the approach used by Google, Facebook, Amazon, and every internet-scale database.

---

### 📘 Textbook Definition

**Database sharding** (also called **horizontal partitioning** across servers) is the practice of distributing rows of a table across multiple independent database instances (shards), where each shard holds a distinct subset of the data determined by the **shard key** (also called partition key). Unlike database partitioning (which splits data across tables/tablespaces on one server), sharding physically distributes data across multiple servers — each with its own CPU, memory, storage, and network. A **shard routing layer** (sometimes called a proxy or middleware) receives queries, determines which shard(s) hold the relevant data from the shard key, and routes accordingly. Sharding strategies: **range-based** (shard by ID ranges: 0–1M → Shard 1, 1M–2M → Shard 2); **hash-based** (shard = hash(key) % N); **directory-based** (a lookup table maps key → shard). Used by: **MongoDB** (built-in sharding), **Vitess** (MySQL sharding at scale — used by YouTube), **Cassandra** (consistent hashing), **HBase**, **CockroachDB** (automatic range-based sharding).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Sharding distributes different rows to different servers — enabling write and storage scale-out beyond any single machine's limits — but joins and cross-shard transactions become painful.

**One analogy:**

> A library decides to split its collection across five branch libraries. Books A-E → Branch 1. Books F-J → Branch 2. And so on. Any patron asking for a book in Branch 1's range goes to Branch 1 — fast, because Branch 1's index is much smaller. If a patron needs books from two branches: they must visit both (cross-shard query). If the library grows and branches become full: adding a sixth branch requires moving half the books from some branches to the new one (resharding).

- "Five branch libraries" → five shards
- "Books A-E in Branch 1" → rows with key prefix A-E in Shard 1
- "Patron goes directly to Branch 1" → shard routing
- "Visit two branches" → cross-shard query (expensive)
- "Adding a sixth branch + moving books" → resharding (operationally painful)

**One insight:**
The shard key is the most important architectural decision in a sharded system. A poor shard key creates a **hot shard** (one shard receives all the writes because most queries use the same shard key value). This is worse than no sharding: you've added all the complexity of sharding with none of the write scale benefits.

---

### 🔩 First Principles Explanation

**SHARD KEY CHOICE:**

```
GOOD SHARD KEY PROPERTIES:
  1. High cardinality: many distinct values (user_id: millions; country: 200 values is low)
  2. Even distribution: queries/writes spread evenly across shards
  3. Query co-location: queries for a user's data almost always include the shard key
     → user_id as shard key: "get all posts by user 42" → single shard
     → timestamp as shard key: "get posts from 2024" → all shards (scatter-gather)
  4. Immutable: if you change the shard key value, you must move the row to a different shard

BAD SHARD KEY EXAMPLES:
  - created_at (timestamp): new data always hits the latest shard → hot shard
  - status (enum): "active/inactive" → all active users hit one shard
  - sequential auto-increment: 1,2,3... always go to shard 1 until full → sequential hotspot
```

**HASH-BASED SHARDING:**

```
shard = hash(user_id) % num_shards

user_id=42:  hash(42)=3476923781; 3476923781 % 4 = 1 → Shard 1
user_id=43:  hash(43)=2841927384; 2841927384 % 4 = 0 → Shard 0
user_id=44:  hash(44)=9182736459; 9182736459 % 4 = 3 → Shard 3

Problem: if num_shards changes from 4 to 5:
hash(42) % 5 = ?  → DIFFERENT shard! Must rehash/move ALL data.
Solution: Consistent Hashing — only ~1/N keys move when a shard is added
```

**CONSISTENT HASHING:**

```
Virtual ring: 0 to 2^32
Each shard: assigned multiple virtual nodes (vnodes) on the ring
Key: hash(key) → position on ring → nearest clockwise vnode → shard

Add a new shard: insert new vnodes; some keys previously belonging
                 to their neighbors now belong to the new shard
Move: ~1/N data moves (vs. rehashing all data in simple modulo)
Used by: Cassandra, Amazon DynamoDB, Riak
```

**VITESS (MySQL SHARDING):**

```
Vitess is a middleware layer for MySQL horizontal sharding at scale.
Used by: YouTube (billions of rows in MySQL, sharded via Vitess)

Components:
  - VTTablet: runs alongside each MySQL instance; handles query rewriting
  - VTGate: routes queries to the correct shard(s); handles scatter-gather
  - VTCtld: topology management; shard config; resharding orchestration

Example:
  User query: SELECT * FROM users WHERE user_id = 42
  VTGate: hash(42) → shard 3 → routes to shard 3's MySQL instance
  Result: returned as if from a single database

Resharding (with Vitess):
  - Start new shard(s)
  - VReplication: copy data from source shards to new shards while live
  - Dual-write period: writes go to old + new shards
  - Cutover: switch VTGate routing; old shards become dormant
  - Cleanup: old shards retired after validation
```

**CROSS-SHARD QUERIES (THE PAIN):**

```
Scatter-gather query: "get all users who signed up today"
  → query broadcast to ALL shards
  → each shard returns its results
  → merge at application layer or VTGate
  → latency = max(all shard response times) + merge overhead

Cross-shard JOIN:
  "get all orders with their user profiles"
  If orders shard key = order_id, user profiles shard key = user_id
  → These are on different shards by definition
  → JOIN is impossible at DB level
  → Application must: fetch orders from orders shards,
                      collect user_ids,
                      fetch profiles from user shards,
                      merge in application code
  → This is the "cross-shard join problem"
  Design principle: data accessed together should be sharded together
                   (users + user_orders on same shard key = user_id → co-located)
```

**CROSS-SHARD TRANSACTIONS (2PC):**

```
Order placement touches: orders table (shard by order_id),
                         inventory table (shard by product_id),
                         user_balance table (shard by user_id)
Three different shards.

Two-Phase Commit (2PC):
  Phase 1 (Prepare): coordinator sends PREPARE to all 3 shards; each locks and prepares
  Phase 2 (Commit): coordinator sends COMMIT if all replied OK; ROLLBACK if any failed

Problems with 2PC:
  - Coordinator failure during Phase 2 → shards stuck in "prepared" state (locks held)
  - Latency: 2× RTT per transaction
  - Blocking: prepared shards hold locks until Phase 2

Alternative: Saga pattern (compensating transactions) — see Microservices keyword
         : Application-level transaction management avoiding cross-shard atomicity
```

---

### 🧪 Thought Experiment

**SHARD KEY DISASTER: Timestamp-Based Sharding**

Timeline system. Sharded by `created_at` (month):

- Jan 2024 → Shard 1
- Feb 2024 → Shard 2
- Mar 2024 → Shard 3
- Apr 2024 → Shard 4 (current month)

**PROBLEM:**

- All new writes → Shard 4 (always the current month's shard)
- Shard 4: 100% of write load
- Shards 1-3: 0% of write load (all historical, read-only)
- Shard 4: overloaded; Shards 1-3: idle

**THIS IS A HOT SHARD:**
The shard key (timestamp/month) creates a hotspot on the most recent shard. Adding more shards doesn't help — they all sit idle until they become the "current" shard.

**FIX:**
Add a random hash component: shard_key = hash(user_id) — not time. Or composite key: `shard = hash(user_id) XOR hash(created_at_day)` — distributes writes by user across all shards while still enabling co-location of a user's timeline entries.

**LESSON:** Never use monotonically increasing values (timestamps, auto-increment IDs) as shard keys. They always create hot shards. Use high-cardinality, uniformly distributed keys (user_id hash, UUID hash).

---

### 🧠 Mental Model / Analogy

> Database sharding is like splitting a filing cabinet (the database) into N filing cabinets across N offices. Each office handles a specific set of folders (rows). Finding a specific folder: go directly to the responsible office. Looking for folders meeting a criteria that span offices: visit all offices (scatter-gather, expensive). Moving a folder from one category to another category handled by a different office: carry the folder to the new office (resharding, expensive). The assignment rule for "which office handles which folder" is the shard key.

- "Filing cabinet split into N offices" → horizontal partitioning across N servers
- "Go directly to the responsible office" → shard routing (no broadcast needed)
- "Visit all offices" → scatter-gather query (crosses all shards)
- "Carrying folders to new office" → resharding (data movement)
- "Assignment rule" → shard key (the most critical design decision)

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Sharding splits your database across multiple computers. Each computer owns a portion of the data. Queries for a specific user go to one computer (fast). Queries for all users go to all computers (slow). Adding computers (shards) lets you store more data and handle more writes.

**Level 2:** Choose the shard key carefully: it must distribute writes evenly (no hot shards) and match your query patterns (queries should include the shard key to avoid scatter-gather). Use hash-based sharding for even distribution. Use Vitess for MySQL sharding at scale, or MongoDB's built-in sharding. Minimize cross-shard transactions — if you need them, accept the complexity or redesign your data model.

**Level 3:** Hot shard prevention: use composite shard keys (user_id || created_month), use consistent hashing with virtual nodes (vnodes) for even physical distribution, and monitor per-shard query rates and storage (alert on imbalance > 20%). Resharding is a critical operational challenge: Vitess VReplication supports live resharding (copy while serving traffic). Plan for resharding during design: initial over-sharding (more shards than needed) allows routing more shards to more servers as you grow, rather than full resharding. Facebook uses TAO (data access layer) for sharding social graph data: graph edges co-located with their source node on the same shard for efficient `get_friends(user_id)` queries. Cross-shard edges are fetched via async graph traversal.

**Level 4:** Sharding is fundamentally an application of the "share-nothing" architecture: each shard is independent with its own CPU, RAM, disk. No shared state between shards (contrast: SMP shared-memory — one server many CPUs; NUMA — shared memory with latency tiers). Share-nothing scales linearly in theory but requires the application to handle data distribution (shard key selection, routing). CockroachDB and Google Spanner take an opposite approach: they appear as a single database but internally shard data into "ranges" (CockroachDB) or "tablets" (Spanner), with automatic rebalancing and global Raft consensus for consistency. The application sees a standard SQL interface; sharding is transparent. The trade-off: cross-range transactions still incur 2PC overhead; TrueTime (Spanner) or HLC timestamps (CockroachDB) add protocol complexity. The fundamental tension: manual sharding (Vitess) gives maximum control at operational cost; automatic sharding (Spanner, CockroachDB) gives operational simplicity at the cost of opaque internals and potentially surprising latency for cross-shard transactions.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│ VITESS SHARDING ARCHITECTURE                             │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Application                                            │
│     ↓ SQL (standard)                                    │
│  ┌──────────────────────────────────────────────┐       │
│  │  VTGate (shard router)                       │       │
│  │  Parses SQL → extracts shard key → routes    │       │
│  └──────┬────────────────────────┬──────────────┘       │
│         │                        │                      │
│  ┌──────┴──────┐          ┌──────┴──────┐               │
│  │  Shard 0   │          │  Shard 1   │                 │
│  │  user 0-49%│          │  user 50-99│                 │
│  │  VTTablet  │          │  VTTablet  │                 │
│  │  MySQL     │          │  MySQL     │                 │
│  │  Primary   │          │  Primary   │                 │
│  │  +Replicas │          │  +Replicas │                 │
│  └────────────┘          └────────────┘                 │
│                                                          │
│  Each shard is independently replicated (master-slave)   │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**SINGLE-SHARD QUERY:**

```
Application: SELECT * FROM orders WHERE user_id = 42 AND order_id = 123
→ VTGate: shard key = user_id=42 → hash(42) % 4 = 2 → Shard 2
→ [SHARDING ← YOU ARE HERE: single shard routing]
→ Shard 2 MySQL: SELECT * FROM orders WHERE user_id=42 AND order_id=123
→ Result: 1 row returned → VTGate → Application
→ Latency: single shard query time (no scatter)
```

**CROSS-SHARD QUERY:**

```
Application: SELECT COUNT(*) FROM orders WHERE created_at > '2024-01-01'
→ VTGate: no shard key in WHERE → scatter-gather
→ Broadcasts to all shards: SELECT COUNT(*) FROM orders WHERE created_at > '2024-01-01'
→ Each shard returns its count: Shard0=50M, Shard1=48M, Shard2=51M, Shard3=49M
→ VTGate merges: SUM = 198M
→ Latency: MAX(all shard response times) + merge
```

---

### ⚖️ Comparison Table

| Approach                          | Write Scale       | Cross-Shard                      | Consistency      | Operational Cost |
| --------------------------------- | ----------------- | -------------------------------- | ---------------- | ---------------- |
| **Single server**                 | Vertical only     | N/A (all local)                  | Strong           | Lowest           |
| **Partitioning (same server)**    | Vertical only     | Easy (same server)               | Strong           | Low              |
| **Sharding (multiple servers)**   | Horizontal        | Expensive (scatter-gather / 2PC) | Per-shard strong | High             |
| **CockroachDB/Spanner**           | Horizontal (auto) | Transparent (2PC)                | Global strong    | Medium (managed) |
| **Cassandra (sharding via ring)** | Horizontal (auto) | Expensive                        | Eventual         | Medium           |

---

### ⚠️ Common Misconceptions

| Misconception                                      | Reality                                                                                                                                                                                                     |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Sharding automatically scales all queries          | Only queries that include the shard key scale (go to one shard). Queries without the shard key scatter-gather to all shards — often SLOWER than a single server                                             |
| You can always add more shards to handle more load | Resharding (re-distributing existing data across new shard count) is extremely operationally complex; it requires live data migration and careful cutover. Plan shard count overprovisioning at design time |
| Sharding replaces replication                      | Each shard should still be replicated (master + replicas) for HA. Sharding handles write scale; replication handles HA and read scale                                                                       |
| NoSQL databases solve sharding automatically       | MongoDB, Cassandra, etc. provide automatic sharding, but you still choose the shard key. A bad shard key creates hot shards regardless of the database being used                                           |

---

### 🚨 Failure Modes & Diagnosis

**1. Hot Shard: One Shard Receiving All Writes**

**Symptom:** One database server at 95% CPU/disk I/O while all others are near-idle. Write latency increasing. Scatter-gather queries to other shards: fast. Queries to hot shard: slow.

**Root Cause:** Shard key creates uneven distribution. Most writes have the same shard key value (e.g., timestamp-based sharding, sequential IDs, or small-cardinality keys like country with 90% of traffic from one country).

**Diagnostic:**

```
Monitor: per-shard query rate, CPU, disk I/O (Prometheus + Grafana)
Query: SELECT shard_id, COUNT(*) FROM routing_log
       WHERE ts > NOW() - INTERVAL '1 hour'
       GROUP BY shard_id ORDER BY COUNT(*) DESC;
Alert: if max_shard_qps > 2× avg_shard_qps
```

**Fix (short term):** Split the hot shard into 2-4 sub-shards (partial resharding). Add read replicas to the hot shard to offload read traffic while you fix the write distribution.

**Fix (long term):** Redesign the shard key. If using timestamp: add a random suffix (user_id_hash). If using country: use user_id instead. Live resharding with Vitess VReplication or MongoDB's chunk migration.

**Prevention:** Before production: simulate write distribution against the chosen shard key with realistic traffic patterns. Monitor `max_shard_rate / avg_shard_rate` in staging.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Partitioning (DB)` — sharding is partitioning across servers; understand same-server partitioning first
- `Consistent Hashing` — the standard algorithm for shard key → shard mapping
- `Distributed Systems` — cross-shard transactions, consensus, distributed state

**Builds On This (learn these next):**

- `NoSQL & Distributed Databases` — Cassandra, MongoDB, DynamoDB all shard automatically
- `System Design` — sharding is a core system design pattern
- `CAP Theorem` — sharding distributes data; partitions affect consistency guarantees

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Rows distributed across multiple servers; │
│              │ each server = 1 shard; independent        │
├──────────────┼───────────────────────────────────────────┤
│ SHARD KEY    │ The column used to determine which shard  │
│              │ a row belongs to — MOST CRITICAL DECISION │
├──────────────┼───────────────────────────────────────────┤
│ HOT SHARD    │ Uneven distribution → one overloaded shard│
│ CAUSE        │ Timestamp, sequential ID, low-cardinality │
├──────────────┼───────────────────────────────────────────┤
│ CROSS-SHARD  │ Scatter-gather (expensive reads)          │
│ PAIN         │ 2PC transactions (complex writes)         │
│              │ No cross-shard JOINs at DB layer          │
├──────────────┼───────────────────────────────────────────┤
│ TOOLS        │ Vitess (MySQL), MongoDB (built-in)        │
│              │ Cassandra (consistent hashing)            │
│              │ CockroachDB (automatic/transparent)       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Horizontal scale-out for writes +        │
│              │  storage — shard key choice is destiny"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Database Migration → Schema Evolution     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C — Design Question) Design the sharding strategy for a social media platform: users table (1B users), posts table (500B posts, each post belongs to one user), and follows table (graph edges: user follows user). Choose a shard key for each table. What co-location decisions do you make? What queries become cross-shard, and how do you handle them? What is your resharding strategy as you grow from 8 to 32 shards?

**Q2.** (TYPE D — Failure Scenario) Your Vitess MySQL cluster has 4 shards. User complaint: "I can see my post from 2 minutes ago, but my friend says it doesn't appear in their feed." You check: the user's post is on Shard 2. The friend's feed query is a scatter-gather across all shards. Shard 2 is currently experiencing high write load. What is the likely cause? How does a read replica for Shard 2 help? What query routing change would you make?
