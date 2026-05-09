---
id: SYD-042
title: Data Partitioning Strategies
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-031, SYD-041
used_by: SYD-043, SYD-044, SYD-051
related: SYD-031, SYD-032, SYD-011
tags:
  - distributed
  - database
  - architecture
  - deep-dive
  - scalability
status: complete
version: 1
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 42
permalink: /syd/data-partitioning-strategies/
---

# SYD-042 - Data Partitioning Strategies

⚡ TL;DR - Data partitioning splits a dataset across multiple nodes so no single node holds or processes all of it - enabling horizontal scale of storage and throughput beyond what any one machine can provide.

| SYD-042         | Category: System Design          | Difficulty: ★★★ |
| :-------------- | :------------------------------- | :-------------- |
| **Depends on:** | SYD-031, SYD-041                 |                 |
| **Used by:**    | SYD-043, SYD-044, SYD-051       |                 |
| **Related:**    | SYD-031, SYD-032, SYD-011       |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A single database server stores all 10TB of user data. Storage is full. CPU is maxed. You cannot add more RAM. Queries take minutes. You cannot vertically scale any further - the biggest server available is not big enough.

**THE BREAKING POINT:**
Every database has a hard ceiling: max RAM, max disk I/O, max CPU. These ceilings are physical. When you hit them, no amount of tuning or caching helps. The only solution is to distribute the data across multiple machines.

**THE INVENTION MOMENT:**
Split the data set into partitions based on a partition key. Each partition lives on a separate node. Queries are routed to the node(s) holding the relevant partition. Scale is now linear: double the nodes, roughly double the capacity and throughput.

**EVOLUTION:**
Early sharding was manual (application-level routing). Google's Bigtable introduced automatic range partitioning with tablet splitting. Cassandra popularized consistent hash-based partitioning (no central routing table). Modern distributed databases (CockroachDB, Spanner, DynamoDB) implement automatic partition rebalancing. The challenge shifted from "how to partition" to "how to rebalance without downtime."

---

### 📘 Textbook Definition

**Data partitioning** (also called sharding) is the process of dividing a data set into disjoint subsets (partitions/shards), each stored on a separate storage node. A partition key determines which shard holds a given record. Partitioning enables throughput, storage, and query load to scale horizontally by distributing work across many nodes. The trade-off is increased complexity in routing, joins, and cross-partition transactions.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Split your huge table into N smaller tables on N separate servers, each handling their slice.

**One analogy:**

> Data partitioning is like organizing a library by the first letter of the author's last name. Each librarian (server) handles only their section (A-F, G-M, N-Z). No single librarian is overwhelmed; any specific book is always found in exactly one section.

**One insight:**
The partition key is the most consequential decision in sharding. The wrong key creates hot shards that negate all benefits; the right key distributes load evenly across all partitions.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Each record belongs to exactly one partition (no duplicates except for replication).
2. The routing function must be deterministic: same key always maps to the same partition.
3. Partitions must be approximately equal in size and load (balanced).
4. The partition scheme must accommodate data growth without full reshuffle.

**DERIVED DESIGN:**
Choose a partition key. Apply a routing function (range, hash, directory). Each node owns a partition range or set of hash buckets. A routing layer (shard map, consistent hash ring, or central coordinator) directs queries to the correct node. Rebalancing: split hot/large partitions, migrate partition ownership.

**THE TRADE-OFFS:**
**Gain:** Linear storage and throughput scaling; fault isolation (one shard failure does not affect others).
**Cost:** Cross-shard queries and transactions are expensive; joins across shards require scatter-gather or denormalization; partition key changes require data migration.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** You must decide which records go to which node and how to route queries to the right node.
**Accidental:** Rebalancing algorithms, cross-shard transaction coordination, hot shard detection and remediation.

---

### 🧪 Thought Experiment

**SETUP:** A social network stores 1 billion user profiles in a single PostgreSQL instance. Storage is 2TB. Read QPS is 500K. Single instance limit reached.

**WHAT HAPPENS WITHOUT PARTITIONING:**
Vertical scale: buy a 256-core, 4TB RAM server. Cost: $50K/month. But the next doubling costs $200K/month - cost grows exponentially while capacity grows linearly. You hit a hard ceiling at the largest available machine.

**WHAT HAPPENS WITH PARTITIONING:**
Hash partition by `user_id % 10` = 10 shards. Each shard holds 100M profiles, serves 50K QPS. Adding 10 more shards: 20 total, each now serves 25K QPS. Cost scales linearly with data. The ceiling is now "how many commodity servers can you coordinate" not "what's the biggest single machine."

**THE INSIGHT:**
Partitioning converts a capacity problem (bounded by one machine) into a coordination problem (distributing across many). Coordination problems are solvable with software; physical machine limits are not. The question becomes: how complex a coordination layer are you willing to build and operate?

---

### 🧠 Mental Model / Analogy

> Data partitioning is like a post office sorting system. Letters (records) are routed to different regional distribution centers (shards) based on zip code (partition key). Each center handles only letters for its region. Adding more centers handles more mail volume. Cross-region coordination (cross-shard queries) requires a separate coordination layer.

- **Letters** = records
- **Zip code** = partition key
- **Distribution center** = shard/partition node
- **Routing rules** = partition function (range, hash)
- **Cross-region package** = cross-shard query
- **Expanding to new region** = adding a new shard

Where this analogy breaks down: post offices don't need to rebalance when a zip code grows disproportionately large; databases must split hot partitions dynamically.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Instead of storing all your data in one big pile (one server), you split it into labeled buckets (shards), each stored on a different server. When you need something, you go to the right bucket. No single bucket gets too big.

**Level 2 - How to use it (junior developer):**
Choose a partition key (usually the primary entity's ID). Decide on range vs hash partitioning. Build or use a routing layer. Never do `SELECT * FROM users` across all shards without a partition key - that becomes N queries to N shards (scatter-gather).

**Level 3 - How it works (mid-level engineer):**
Range: partition 0 holds user_id 1-1M, partition 1 holds 1M-2M. Hot for sequential access patterns. Hash: `shard = hash(user_id) % N`. Even distribution for random access. Directory: explicit lookup table maps key to shard. Flexible but requires a highly available directory service. Consistent hashing: distributes keys on a ring; adding nodes minimizes remapping.

**Level 4 - Why it was designed this way (senior/staff):**
The fundamental tension: range partitioning enables range scans but creates hotspots on sequential inserts. Hash partitioning distributes evenly but makes range scans scatter-gather (expensive). Most systems choose one and live with the trade-off. Hybrid approaches (Cassandra: hash on partition key, range within partition) allow both at the cost of schema design complexity. Automatic rebalancing (Spanner, CockroachDB) adds consensus overhead but eliminates operational burden.

**Expert Thinking Cues:**
- Ask: "Will queries ever need to scan a range of partition keys?"
- Ask: "What is the expected cardinality of the partition key? Low cardinality = uneven shards."
- Red flag: partitioning on a column with low cardinality (e.g., status: active/inactive = 2 shards)
- Red flag: no rebalancing strategy - initial even distribution drifts over time

---

### ⚙️ How It Works (Mechanism)

**Range partitioning:**
```
Partition key: user_id
  Shard 0: user_id  1 - 1,000,000
  Shard 1: user_id  1,000,001 - 2,000,000
  Shard 2: user_id  2,000,001 - 3,000,000
  ...
Route: find shard where range contains user_id
```

**Hash partitioning:**
```
Partition key: user_id
  shard_index = hash(user_id) % num_shards
  Shard 0: hashes [0, 25%)
  Shard 1: hashes [25%, 50%)
  ...
Route: compute hash, find shard
Problem: adding shard changes N, remaps ~50% of keys
```

**Consistent hashing:**
```
Hash space: 0 to 2^32 (ring)
Each shard: owns arc of the ring
user_id hashed -> position on ring
  -> clockwise to nearest shard node
Adding shard: only ~1/N keys remapped
Removing shard: keys go to next shard on ring
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
[Client: SELECT * FROM users WHERE id=42]
         |
         v
[Router: shard = hash(42) % 10 = 2]   <- YOU ARE HERE
         |
         v
[Query sent to Shard 2]
         |
         v
[Shard 2 executes query locally]
         |
         v
[Result returned to client]
```

**FAILURE PATH:**
```
[Query: SELECT * WHERE country='US']
(No partition key in filter)
         |
         v
[Router: scatter to ALL 10 shards]
         |
         v
[Gather results from 10 shards]
         |
[Increased latency, N-fold load on all shards]
```

**WHAT CHANGES AT SCALE:**
Hot shards emerge as data access patterns evolve. Monitor per-shard QPS and storage. Split hot shards (double shard count for hot range). Use consistent hashing to minimize key remapping on split. At extreme scale (>100 shards), routing table updates become a coordination challenge.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Cross-shard transactions require distributed coordination (2-phase commit or saga). These are expensive: 2PC adds network round trips for every participating shard. Design to avoid cross-shard transactions by choosing partition keys that co-locate related data.

---

### 💻 Code Example

**BAD - hardcoded shard count (inflexible):**
```python
# BAD: fixed shard count, no resizing support
NUM_SHARDS = 4

def get_shard(user_id):
    return user_id % NUM_SHARDS  # breaks on resize

def query_user(user_id):
    shard = get_shard(user_id)
    conn = shard_connections[shard]
    return conn.execute(
        "SELECT * FROM users WHERE id = ?", user_id
    )
```

**GOOD - consistent hashing with virtual nodes:**
```python
import hashlib, bisect

class ConsistentHashRouter:
    def __init__(self, nodes, replicas=150):
        self.replicas = replicas
        self.ring = {}
        self.sorted_keys = []
        for node in nodes:
            self.add_node(node)

    def _hash(self, key):
        return int(
            hashlib.md5(str(key).encode()).hexdigest(),
            16
        )

    def add_node(self, node):
        for i in range(self.replicas):
            vkey = self._hash(f"{node}:{i}")
            self.ring[vkey] = node
            bisect.insort(self.sorted_keys, vkey)

    def remove_node(self, node):
        for i in range(self.replicas):
            vkey = self._hash(f"{node}:{i}")
            del self.ring[vkey]
            self.sorted_keys.remove(vkey)

    def get_node(self, key):
        if not self.ring:
            return None
        hk = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, hk)
        if idx == len(self.sorted_keys):
            idx = 0
        return self.ring[self.sorted_keys[idx]]

# Usage
router = ConsistentHashRouter(
    ["shard-0", "shard-1", "shard-2"]
)
shard = router.get_node(user_id=42)
# Adding a shard remaps only ~1/N keys
router.add_node("shard-3")
```

**How to test / verify correctness:**
- Generate 1M keys, verify even distribution (standard dev < 5% of mean per shard).
- Add a shard, verify only ~1/N keys remapped.
- Remove a shard, verify all its keys now route to adjacent shard.

---

### ⚖️ Comparison Table

| Strategy        | Distribution | Range scan | Add shard  | Hot spot risk  |
| --------------- | ------------ | ---------- | ---------- | -------------- |
| Range           | Uneven       | Efficient  | Split range | Sequential insert hotspot |
| Hash (modulo)   | Even         | Scatter-gather | Rehash all | Low         |
| Consistent hash | Even         | Scatter-gather | Remap 1/N | Low          |
| Directory       | Flexible     | Flexible   | Update table | Low          |
| Composite       | Flexible     | Partial    | Complex    | Managed       |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
| ------------- | ------- |
| "Hash partitioning eliminates hot shards" | Hash partitioning distributes keys evenly across shards, but if one key generates disproportionate traffic (celebrity user), that shard is still hot. The hot key, not the key distribution, causes the issue. |
| "More shards = better performance" | More shards = more coordination overhead. Cross-shard queries become more expensive. Optimal shard count balances partition size vs coordination cost. |
| "Consistent hashing solves all rebalancing" | Consistent hashing minimizes key remapping but still requires data migration when adding nodes. Migration can impact performance during the migration window. |
| "Partition key choice is reversible" | Changing a partition key requires migrating all data. It is one of the most operationally expensive changes in a sharded system. Choose carefully upfront. |
| "Global secondary indexes are free on sharded systems" | A global secondary index on a sharded table requires either scatter-gather queries on reads or fan-out writes on every write. Neither is free. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Hot shard from monotonically increasing partition key**

**Symptom:** One shard has 10x the write rate of others; its CPU/disk is maxed. Other shards are underutilized.

**Root Cause:** Using a timestamp or auto-increment ID as partition key: all new writes go to the shard owning the latest range.

**Diagnostic:**
```bash
# Check per-shard write QPS
# In a monitoring tool: sum(writes) by shard_id
# Heavy skew = hot shard
```

**Fix:** Switch to hash-based partitioning on a random-ish key (UUID, user_id hash). Or use composite key: `(user_id, timestamp)` where user_id provides distribution.

**Prevention:** Never use auto-increment or timestamp as the sole partition key in range-partitioned systems.

---

**Failure Mode 2: Cross-shard scatter-gather query timeout**

**Symptom:** Queries without partition key in filter take 10x longer and time out under load.

**Root Cause:** `SELECT * WHERE country='US'` fans out to all 100 shards, each executing the query. 100x load on the cluster.

**Diagnostic:**
```sql
-- Check query plans for shard fan-out
EXPLAIN SELECT * FROM users WHERE country = 'US';
-- Look for "Distributed scan across all shards"
```

**Fix:** Denormalize: maintain a secondary index table `country_users` co-partitioned by country. Or accept scatter-gather with async parallel execution and result merging.

**Prevention:** Document "partition key required" for all primary entity queries.

---

**Failure Mode 3: Uneven shard sizes after data deletion**

**Symptom:** Shard 3 holds 5TB, other shards hold 500GB each. Shard 3 is almost full.

**Root Cause:** Data deletion concentrated on some shards (users deleted accounts in a specific ID range). Surviving high-value users clustered in one range.

**Diagnostic:**
```bash
# Check per-shard storage (varies by DB system)
SELECT shard_id, sum(table_size) as total_gb
FROM information_schema.shard_stats
GROUP BY shard_id ORDER BY total_gb DESC;
```

**Fix:** Split the oversized shard, migrating its data to a new shard. Use consistent hashing for future-proof rebalancing.

**Prevention:** Implement automated shard size monitoring and automatic split triggers.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-031 - Sharding (System)]] - the concept; this entry covers the strategies
- [[SYD-041 - Write-Ahead Logging (System)]] - WAL enables per-shard recovery

**Builds On This (learn these next):**
- [[SYD-032 - Hot Shard]] - the primary failure mode of poor partition strategy
- [[SYD-043 - URL Shortener Design]] - practical example using hash partitioning
- [[SYD-051 - System Design at Hyperscale]] - how partitioning strategies apply at FAANG scale

**Alternatives / Comparisons:**
- [[SYD-011 - Consistent Hashing (Load Balancing)]] - the algorithm underpinning hash partitioning

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ WHAT IT IS   │ Splitting data across N nodes    │
│              │ based on a partition key         │
├──────────────┼──────────────────────────────────┤
│ PROBLEM      │ Single-node storage and          │
│ IT SOLVES    │ throughput limits                │
├──────────────┼──────────────────────────────────┤
│ KEY INSIGHT  │ Partition key choice determines  │
│              │ distribution quality forever     │
├──────────────┼──────────────────────────────────┤
│ USE WHEN     │ Dataset exceeds single-node      │
│              │ capacity or throughput           │
├──────────────┼──────────────────────────────────┤
│ AVOID WHEN   │ Dataset fits on one node - adds  │
│              │ coordination complexity for free │
├──────────────┼──────────────────────────────────┤
│ TRADE-OFF    │ Horizontal scale vs cross-shard  │
│              │ query complexity                 │
├──────────────┼──────────────────────────────────┤
│ ONE-LINER    │ "Hash for distribution;          │
│              │ range for ordered scans."        │
├──────────────┼──────────────────────────────────┤
│ NEXT EXPLORE │ SYD-032 Hot Shard                │
└─────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. The partition key is your most consequential decision - wrong key = permanent hot shards.
2. Hash partitioning for even distribution; range partitioning for efficient range scans, not both.
3. Design to avoid cross-shard transactions - co-locate related data in the same shard.

**Interview one-liner:** "Data partitioning splits a dataset across nodes using a partition key - hash for even distribution, range for scan efficiency - but the partition key choice is essentially permanent and must match your query patterns."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** The key you choose to partition work determines the ceiling of your scalability. Choose a key that distributes work evenly and co-locates related work. If you get this wrong, no amount of infrastructure can compensate.

**Where else this pattern appears:**
- **Kafka topics:** Partitioned by message key; same key always goes to same partition, enabling per-key ordering.
- **Elasticsearch:** Index sharding distributes document storage and query load across nodes using the document ID.
- **DNS:** The global DNS namespace is range-partitioned by domain suffix, delegated to authoritative servers for each TLD.

---

### 💡 The Surprising Truth

The most common partitioning mistake is not choosing hash vs range - it is choosing a partition key with low cardinality. Partitioning a `users` table by `account_type` (free/paid) creates exactly 2 shards, with 95% of data on the "free" shard. The result is worse than no partitioning: you now have cross-shard overhead plus an extreme hot shard. The minimum cardinality for a partition key must exceed your target shard count by at least 10x.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** A user sends a message to another user in a sharded messaging system. The sender is on shard 3, the recipient is on shard 7. The message must be stored in both users' inboxes atomically. How do you implement this cross-shard atomic write without 2-phase commit overhead?

*Hint:* Explore the saga pattern (compensating transactions) vs 2PC trade-offs, then look at how systems like WhatsApp avoid cross-shard transactions by choosing partition keys that co-locate conversation participants.

**Q2 (Scale):** You shard your user table by `hash(user_id) % 16`. After 2 years, storage per shard is 80% full. You need to double shard count to 32. How many keys must be remapped, and how do you migrate data without downtime?

*Hint:* With modulo hashing: changing N from 16 to 32 remaps ~50% of keys (any key where hash % 32 maps to different shard than hash % 16). Then research consistent hashing which would only remap ~1/32 of keys. Explore the blue-green migration pattern for zero-downtime shard splits.

**Q3 (Design Trade-off):** A ride-sharing platform shards trips by `driver_id`. Queries like "show all active trips near lat/lng X" require scanning all shards. An alternative is to shard by geo-hash (location). What are the trade-offs of each, and what happens when a driver moves from one geo-hash area to another during a trip?

*Hint:* Evaluate driver-centric queries (where are my trips?) vs geo-centric queries (what's near me?) for each partition scheme. The trip-crossing-geo boundary problem is the crux - explore how Uber handles this with a separate geospatial index layer.
