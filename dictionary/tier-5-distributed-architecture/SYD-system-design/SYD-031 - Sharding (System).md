---
id: SYD-031
title: "Sharding (System)"
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-007, SYD-042
used_by: SYD-032, SYD-042
related: SYD-011, SYD-032, SYD-042
tags:
  - database
  - distributed
  - scaling
  - advanced
  - architecture
status: complete
version: 3
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 31
permalink: /syd/sharding-system/
---

# SYD-031 - Sharding (System)

⚡ TL;DR - Horizontal database partitioning that splits data across multiple independent database instances by a shard key, enabling linear read/write scaling beyond single-node limits.

| SYD-031         | Category: System Design     | Difficulty: ★★★ |
| :-------------- | :-------------------------- | :-------------- |
| **Depends on:** | SYD-007, SYD-042            |                 |
| **Used by:**    | SYD-032, SYD-042            |                 |
| **Related:**    | SYD-011, SYD-032, SYD-042   |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your single PostgreSQL server holds 500GB of user data and handles 8,000 writes/second at peak. You add memory, upgrade to the fastest NVMe SSDs, tune every index - and still hit the ceiling. A single database node has a hard physical limit: one CPU, one disk I/O bus, one network interface. You cannot serve 50,000 writes/second on one machine regardless of hardware cost.

**THE BREAKING POINT:**
Vertical scaling (bigger machine) has a ceiling. Read replicas help with reads but not with writes - the primary is still the single writer. When write throughput exceeds a single node's capacity, you must split the data across multiple write-capable nodes. This is sharding.

**THE INVENTION MOMENT:**
Early social networks (Friendster, MySpace, early Facebook) hit MySQL write limits with millions of users. Their engineers invented database sharding: partition user data by user ID across N separate MySQL instances. Each instance owns 1/N of the users and handles 1/N of the write load. Write capacity scales linearly with shard count.

**EVOLUTION:**
Manual sharding (application-level routing) was the dominant approach in the 2000s. The 2010s brought distributed databases with built-in sharding: Cassandra, MongoDB, CockroachDB, Vitess (MySQL sharding layer). Today, sharding is a design decision you make at the data model level - whether you implement it manually or whether a distributed DB does it for you.

---

### 📘 Textbook Definition

**Sharding** is a horizontal database partitioning technique that splits data across multiple independent database instances (shards) based on a shard key. Each shard is a full, independent database that owns an exclusive subset of the data. The application (or a routing layer) determines which shard to query by applying a routing function to the shard key (e.g., `shard_id = hash(user_id) % N`). Sharding enables both read and write capacity to scale linearly with the number of shards.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Split the database into N independent pieces; route each request to the right piece using a key.

**One analogy:**
> A post office with 26 staff members. Last names A-E go to desk 1, F-J to desk 2, etc. Each desk handles all operations (read, write) for its letter range. Adding a 27th desk splits an existing range. No desk can handle requests for another desk's letters.

**One insight:**
Sharding trades query flexibility for scale. Queries within one shard are fast; queries spanning multiple shards require scatter-gather across all shards and are expensive.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Each shard is an independent write unit - no shared write path means no write bottleneck.
2. The shard key determines data locality - all data with the same key always lands on the same shard.
3. Cross-shard queries require fan-out - you must query all N shards and merge results.
4. Transactions are shard-local by default - distributed transactions across shards are expensive and complex.
5. Resharding (changing N) requires data migration - this is the most painful operation in a sharded system.

**DERIVED DESIGN:**
The shard key choice is the most critical design decision. It determines: (a) data distribution uniformity (prevents hot shards), (b) query locality (prevents cross-shard scatter), and (c) resharding complexity. There is almost always tension between (a) and (b).

**THE TRADE-OFFS:**
**Gain:** Linear write and read scale, data isolation between shards (one shard's failure does not affect others), predictable per-shard performance.
**Cost:** No cross-shard joins, no cross-shard transactions, complex resharding, application-level routing complexity.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Splitting data inherently complicates cross-entity operations - this is math, not poor design.
**Accidental:** Application-level routing code that duplicates shard routing logic in multiple services. Vitess, ProxySQL, and distributed databases handle this transparently.

---

### 🧪 Thought Experiment

**SETUP:**
A social network with 100M users. Each user generates 10 writes/day. Total: 1B writes/day = approx 11,600 writes/second peak. PostgreSQL max: ~10,000 writes/second on high-end hardware.

**WHAT HAPPENS WITHOUT SHARDING:**
One PostgreSQL primary, 3 read replicas. Read replicas absorb read load. But ALL writes go to the primary. At peak, the primary queue backs up. Writes start failing. Response times spike. The system degrades under the weight of a single write endpoint.

**WHAT HAPPENS WITH SHARDING (10 shards):**
Each shard owns 10M users. Each shard receives 1,160 writes/second - well within PostgreSQL's capacity. A failed shard affects only 10M users, not 100M. You can independently scale each shard's hardware based on its actual load.

**THE INSIGHT:**
Sharding is not about making individual operations faster - it is about making the system's total write capacity proportional to the number of database nodes.

---

### 🧠 Mental Model / Analogy

> Sharding is like a filing cabinet system in a large office. Instead of one cabinet holding all files, you have 10 cabinets. Files are assigned to a cabinet based on the first letter of the surname (A-C in cabinet 1, D-F in cabinet 2, etc.). Each cabinet has its own lock and clerk. Multiple clerks work simultaneously. Finding one person's file means going to exactly one cabinet instantly. Finding all clients with a specific job title means checking all 10 cabinets.

**Mapping:**
- Filing cabinets → database shards
- First letter of surname → shard key
- Cabinet assignment rule → shard routing function
- Clerk per cabinet → database process per shard
- All cabinets open simultaneously → parallel writes to different shards
- Searching all cabinets → cross-shard scatter-gather

Where this analogy breaks down: filing cabinets don't replicate their contents for fault tolerance; shards should have replicas within their shard for availability.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Instead of one database holding everything, you have 10 databases. Each database stores 1/10 of the data. When you look up a user, you calculate which database has their data and go there directly. It is like sharding a phone book into 26 books by first letter.

**Level 2 - How to use it (junior developer):**
Choose a shard key (user_id is typical). Choose a routing function: `shard = hash(user_id) % num_shards`. Store each shard as a separate database connection pool. In application code: `db = shard_router.get_db(user_id)`. All operations for a user always go to the same shard. Cross-user queries (analytics, admin) must query all shards and merge.

**Level 3 - How it works (mid-level engineer):**
Shard key selection involves three concerns: (1) cardinality - high cardinality keys (user_id) distribute evenly; low cardinality (country) causes hot shards; (2) query locality - the most frequent queries should use the shard key to avoid scatter; (3) immutability - changing a row's shard key means migrating it to a different shard, which is a complex operation. Hash-based routing gives even distribution but makes range queries cross-shard. Range-based routing enables sequential scans but creates hot spots at the high end.

**Level 4 - Why it was designed this way (senior/staff):**
Sharding is a data model decision that trades query expressiveness for scale. At senior level, the design questions are: What is the primary entity of concern? (User-centric systems shard by user_id; order systems by order_id.) What queries are latency-critical and must be shard-local? What queries can tolerate scatter-gather with higher latency? When will resharding be needed and how will it be done with zero downtime? Modern distributed databases (CockroachDB, Vitess) automate resharding but not the query model decisions.

**Expert Thinking Cues:**
- "Which queries are in the critical path and must be served by a single shard?"
- "What is the expected data skew - will any shard key value concentrate disproportionate data?"
- "What is the resharding trigger (shard count doubles when average shard size exceeds X GB)?"
- "How does the team handle cross-shard transactions today?"

---

### ⚙️ How It Works (Mechanism)

```
SHARDING ARCHITECTURE
═════════════════════

Client Request (user_id=12345)
    │
    ▼
Router Layer          ← YOU ARE HERE
  shard_id = hash(12345) % 10
  shard_id = 5
    │
    ▼
Shard 5 (DB Instance)
  SELECT * FROM users WHERE id=12345
    │
    ▼
Response to Client

Sharding Strategies:
  Hash:    shard = hash(key) % N
           Even distribution; no range queries
  Range:   shard = lookup(key range → shard)
           Range queries easy; hot-spots possible
  Consistent Hash: key on ring → nearest shard
           Minimal resharding; complex setup
  Directory: metadata_db.lookup(key → shard)
           Flexible; metadata DB is bottleneck
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Write Request: user_id=99999, data={...}
    │
    ▼
Application Layer
  shard = hash(99999) % 10 = 3
    │
    ▼
Shard 3 Primary (Write)  ← YOU ARE HERE
    │
    ▼
Shard 3 Replicas (Read)
    │ (replication lag ~10ms)
    ▼
Read Request served from
nearest Shard 3 replica
```

**FAILURE PATH:**
Shard 3 primary fails → Shard 3 replica promoted → Shard 3 serves reads from new primary → Users on shards 1,2,4-10 unaffected. Cross-shard queries that touched shard 3 fail until promotion completes (~30 seconds typical).

**WHAT CHANGES AT SCALE:**
At high shard count (100+), the routing layer becomes complex. Virtual shards (consistent hashing with many virtual nodes per physical shard) enable smoother resharding. Scatter-gather queries degrade linearly with shard count - a query touching all N shards is N× slower than a single-shard query.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Cross-shard transactions require 2PC (two-phase commit) or saga patterns, adding latency and complexity. Most sharded systems avoid cross-shard transactions by designing data models where the critical operations are shard-local. Financial systems that need global consistency often use Spanner-style distributed transactions.

---

### 💻 Code Example

```python
import hashlib

# BAD: Modulo-based routing - breaks on reshard
class SimpleShardRouter:
    def __init__(self, num_shards: int):
        self.num_shards = num_shards
        self.shards = [
            connect_db(f"shard_{i}")
            for i in range(num_shards)
        ]

    def get_db(self, key: str):
        # PROBLEM: changing num_shards remaps
        # all keys → requires full data migration
        shard_id = hash(key) % self.num_shards
        return self.shards[shard_id]

# GOOD: Consistent hashing minimises resharding
class ConsistentHashRouter:
    def __init__(self, shards: list,
                 virtual_nodes: int = 150):
        self.ring = {}
        self.sorted_keys = []
        for shard in shards:
            for i in range(virtual_nodes):
                vnode = f"{shard}:{i}"
                h = self._hash(vnode)
                self.ring[h] = shard
                self.sorted_keys.append(h)
        self.sorted_keys.sort()

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(
            key.encode()).hexdigest(), 16)

    def get_shard(self, key: str) -> str:
        h = self._hash(key)
        for node_hash in self.sorted_keys:
            if h <= node_hash:
                return self.ring[node_hash]
        return self.ring[self.sorted_keys[0]]
```

**How to test / verify correctness:**
- Distribution test: route 1M random keys; verify each shard receives 10% +/- 5%.
- Locality test: same key always routes to same shard across multiple calls.
- Resharding test: add one shard; verify only ~10% of keys reroute (consistent hashing) vs ~90% (simple modulo).

---

### ⚖️ Comparison Table

| Strategy | Distribution | Range Queries | Resharding | Best For |
|---|---|---|---|---|
| **Hash-based** | Even | Cross-shard only | Hard - full remapping | User-centric reads by ID |
| **Range-based** | Uneven (hot end) | Efficient | Easy - split ranges | Time-series, sequential IDs |
| **Consistent Hash** | Even | Cross-shard only | Easy - ~1/N remapping | Caches, dynamic node counts |
| **Directory-based** | Flexible | Flexible | Easy | Complex domains, migrations |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Sharding = replication" | No. Sharding splits data (different rows on different nodes). Replication copies data (same rows on multiple nodes). |
| "Any column can be a shard key" | Low-cardinality keys (country, status) cause hot shards. High-cardinality, evenly distributed keys are required. |
| "Sharding solves all scaling" | Sharding scales writes. Cross-shard queries, transactions, and joins remain expensive and complex. |
| "Resharding is simple" | Resharding requires migrating data between shards with zero downtime, which is one of the hardest database operations. |
| "More shards = always better" | Each shard adds operational overhead. Over-sharding (100 shards for 10K users) wastes resources and complicates operations. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Hot Shard (Uneven Distribution)**
**Symptom:** One shard has 70% of the load; others are idle. See SYD-032 for full analysis.
**Root Cause:** Shard key with skewed distribution (e.g., celebrity user with millions of followers sharded by user_id).
**Diagnostic:**
```bash
# Compare shard sizes (PostgreSQL example)
psql -h shard-1 -c "SELECT count(*) FROM users;"
psql -h shard-2 -c "SELECT count(*) FROM users;"
# Large difference = key skew
```
**Fix:** Add a secondary sharding level or use consistent hashing with virtual nodes to spread hot keys.
**Prevention:** Analyse key distribution before choosing shard key; test with real data distributions.

**Mode 2: Cross-Shard Query Performance**
**Symptom:** Analytics queries take 10x longer than expected; scatter-gather fanout is too wide.
**Root Cause:** Design required queries that do not include the shard key; all shards must be queried.
**Diagnostic:**
```bash
# Measure per-shard query time vs total query time
# total_time / avg_shard_time ≈ num_shards
# Confirms scatter-gather
```
**Fix:** Add a secondary index table on a separate store (Elasticsearch, Redshift) that is not sharded and handles non-key queries.
**Prevention:** At design time, list all critical queries and verify each uses the shard key.

**Mode 3: Resharding Downtime**
**Symptom:** Planned shard count increase causes downtime or data inconsistency during migration.
**Root Cause:** No live migration strategy designed upfront; modulo routing requires remapping all keys.
**Diagnostic:**
```bash
# Check migration progress
SELECT count(*) FROM users WHERE migrated = false;
# Ensure dual-write is active
grep "dual_write" /etc/app/sharding.yml
```
**Fix:** Use double-write during migration (write to old and new shard simultaneously); migrate reads last.
**Prevention:** Choose consistent hashing at design time; build resharding tooling before you need it.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-007 - Horizontal Scaling]] - Sharding is horizontal scaling applied to databases
- [[SYD-042 - Data Partitioning Strategies]] - Sharding is one form of data partitioning

**Builds On This (learn these next):**
- [[SYD-032 - Hot Shard]] - The primary failure mode of sharding
- [[SYD-011 - Consistent Hashing (Load Balancing)]] - The hashing algorithm that makes resharding tractable

**Alternatives / Comparisons:**
- [[SYD-006 - Vertical Scaling]] - The alternative that fails first
- [[SYD-042 - Data Partitioning Strategies]] - Broader partitioning context

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════╗
║ WHAT IT IS    Horizontal DB partitioning  ║
║               across N independent        ║
║               database instances          ║
╠══════════════════════════════════════════╣
║ PROBLEM       Single DB write ceiling     ║
║ IT SOLVES     limits scale                ║
╠══════════════════════════════════════════╣
║ KEY INSIGHT   Shard key choice is the     ║
║               most critical decision -    ║
║               wrong key = hot shards      ║
╠══════════════════════════════════════════╣
║ USE WHEN      Write throughput exceeds    ║
║               single node capacity        ║
╠══════════════════════════════════════════╣
║ AVOID WHEN    Workload has frequent        ║
║               cross-shard queries or      ║
║               multi-entity transactions   ║
╠══════════════════════════════════════════╣
║ TRADE-OFF     Write scale vs query        ║
║               flexibility                 ║
╠══════════════════════════════════════════╣
║ ONE-LINER     shard = hash(key) % N;      ║
║               each shard is independent   ║
╠══════════════════════════════════════════╣
║ NEXT EXPLORE  SYD-032: Hot Shard          ║
╚══════════════════════════════════════════╝
```

**If you remember only 3 things:**
1. Shard key choice is everything - high cardinality, evenly distributed keys prevent hot shards.
2. Cross-shard queries and transactions are expensive - design your data model so critical queries are shard-local.
3. Use consistent hashing over simple modulo routing - it reduces data migration when resharding by 10x.

**Interview one-liner:**
"Sharding partitions a database horizontally across N independent instances by a shard key, enabling write capacity to scale linearly - at the cost of cross-shard query complexity."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Design for the read/write pattern, not the data model. Database sharding forces you to pick one dimension of locality (the shard key). Every design that works well in isolation becomes hard at scale if it ignores the primary access pattern. The shard key is a bet on which dimension of your data will be most accessed - choose it by studying query patterns, not data structure.

**Where else this pattern appears:**
- **Microservices database-per-service:** Each service owns its schema - this is functional sharding by domain.
- **CDN edge caching:** Content is sharded across PoPs by geographic proximity - the shard key is the client's location.
- **Kafka partitions:** Topics are sharded across brokers by partition key - consumers only read their assigned partitions.

---

### 💡 The Surprising Truth

The most painful sharding failure mode is not performance - it is the gradual accumulation of cross-shard queries that were "acceptable" at launch but become progressively slower as shard count grows. A scatter-gather query that took 50ms across 4 shards takes 200ms across 16 shards and 800ms across 64 shards. Teams often do not discover this until they are multiple sharding generations deep, by which time fixing the query model requires rewriting application logic while the system is under production load.

---

### 🧠 Think About This Before We Continue

**Q1 (First Principles):** You choose user_id as your shard key. A celebrity user with 50M followers has all their data on shard 3. 10M users view their profile on the same day. What is the problem, and what alternative shard key strategies address it?
*Hint:* Explore the hot shard problem (SYD-032) and strategies like celebrity exception handling, cell-based sharding, and application-level load balancing above the database tier.

**Q2 (Scale):** Your system starts with 4 shards using simple modulo routing (key % 4). You need to scale to 8 shards. What percentage of data must be migrated, and how does consistent hashing change this number?
*Hint:* Work out the mathematics for modulo resharding (all keys where key%8 != key%4, which is roughly 50% of all keys) then contrast with consistent hashing (approximately 1/N migration), and explore how Cassandra's token ring handles this.

**Q3 (Design Trade-off):** You are designing an e-commerce system. You could shard by user_id (keeping all a user's orders together) or by order_id (even distribution). The most frequent query is "get all orders for user X." Which do you choose and why?
*Hint:* Trace each query through both shard key choices and count the number of shards touched, then explore how the "get all orders by date range" query behaves under each approach - look into the tension between query locality and write hot spots.
