---
layout: default
title: "Data Partitioning Strategies"
parent: "System Design"
nav_order: 717
permalink: /system-design/data-partitioning-strategies/
number: "717"
category: System Design
difficulty: ★★★
depends_on: "Sharding (System), Consistent Hashing"
used_by: "Sharding (System), NoSQL Databases"
tags: #advanced, #distributed, #scalability, #databases, #partitioning
---

# 717 — Data Partitioning Strategies

`#advanced` `#distributed` `#scalability` `#databases` `#partitioning`

⚡ TL;DR — **Data Partitioning** splits a large dataset across multiple nodes using a partitioning key and strategy (range, hash, directory), enabling horizontal scale-out while controlling how queries are routed and where hot spots form.

| #717            | Category: System Design               | Difficulty: ★★★ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | Sharding (System), Consistent Hashing |                 |
| **Used by:**    | Sharding (System), NoSQL Databases    |                 |

---

### 📘 Textbook Definition

**Data Partitioning** is the process of splitting a large dataset into smaller, manageable subsets (partitions or shards) that are distributed across multiple nodes or storage units. The partitioning strategy determines how records are assigned to partitions based on a partitioning key. The three primary strategies are: (1) **Range partitioning** — assign records based on ranges of key values; (2) **Hash partitioning** — assign records based on a hash of the key; (3) **Directory/List partitioning** — explicit lookup table maps keys to partitions. Composite strategies (e.g., range-then-hash) address limitations of single strategies. Key challenges include: partition key selection (hot spots), re-partitioning (resharding), cross-partition queries, and maintaining referential integrity across partitions. Partitioning is implemented at the application layer (application-level sharding), database middleware (ProxySQL, Vitess), or natively in the database (PostgreSQL declarative partitioning, Cassandra, DynamoDB).

---

### 🟢 Simple Definition (Easy)

Data Partitioning: instead of one giant filing cabinet (slow, full), use many smaller cabinets. Each cabinet stores a specific range of files (A-H, I-P, Q-Z) or a hashed assignment. To find a file: first figure out which cabinet it's in (routing), then look inside that cabinet. Spreading files across cabinets = faster searches (parallel), more total storage (scale-out).

---

### 🔵 Simple Definition (Elaborated)

Twitter's user data: 500 million users. One database can't hold or serve all 500M users. Partition by user_id: users 1–100M go to shard 1, 100M–200M to shard 2, etc. Write for user 50M → shard 1. Read for user 150M → shard 2. Each shard handles 1/5 of the traffic and stores 1/5 of the data. Add shard 6 → each existing shard shrinks to 1/6. Challenge: choosing the partitioning key and strategy so no single shard becomes a bottleneck (hot shard).

---

### 🔩 First Principles Explanation

**Partitioning strategies: trade-offs and hot spot analysis:**

```
STRATEGY 1: RANGE PARTITIONING

  Assign records to partitions based on key value ranges.

  Example: orders table partitioned by created_at:

  Partition 1: created_at < 2023-01-01
  Partition 2: created_at 2023-01-01 to 2023-07-01
  Partition 3: created_at > 2023-07-01

  Query: SELECT * FROM orders WHERE created_at BETWEEN '2023-03-01' AND '2023-04-01'
  → Queries only partition 2 (partition pruning — ignore other partitions)
  → Efficient range scans on same partition

  Hot Spot Problem: time-series data
    All new orders: always written to partition 3 (latest range).
    Partitions 1 and 2: read-only (old data). Partition 3: all writes.
    → Partition 3 is a WRITE HOT SPOT.

  Fix: Pre-split partition 3 regularly. Cassandra: use time-based partition keys
       but distribute within month-level buckets.

  PostgreSQL declarative range partitioning:

  CREATE TABLE orders (
      id BIGSERIAL,
      created_at TIMESTAMP,
      amount DECIMAL
  ) PARTITION BY RANGE (created_at);

  CREATE TABLE orders_2023_h1
      PARTITION OF orders
      FOR VALUES FROM ('2023-01-01') TO ('2023-07-01');

  CREATE TABLE orders_2023_h2
      PARTITION OF orders
      FOR VALUES FROM ('2023-07-01') TO ('2024-01-01');

  INSERT INTO orders (created_at, amount) VALUES ('2023-03-15', 100);
  -- Automatically routed to orders_2023_h1

STRATEGY 2: HASH PARTITIONING

  Assign records based on hash(partition_key) % num_partitions.

  Example: users table, 8 partitions, partition by user_id:

  user_id=100: hash(100) % 8 = 4 → partition 4
  user_id=101: hash(101) % 8 = 5 → partition 5
  user_id=200: hash(200) % 8 = 0 → partition 0

  Even distribution: hash functions distribute uniformly.
  No hot spots from access patterns: popular keys hash to random partitions.

  Problem: range queries are expensive
    SELECT * FROM users WHERE user_id BETWEEN 100 AND 200
    → Must query ALL 8 partitions (key range spans multiple hash partitions)
    → Scatter-gather: send to all, merge results

  Problem: resharding requires remapping ALL keys
    8 partitions → 9 partitions: hash(key) % 9 ≠ hash(key) % 8
    Almost all records need to move! (solution: consistent hashing)

  Consistent Hashing (fix for resharding):
    Keys placed on a ring (0 to 2^32).
    Partitions placed at points on the ring.
    Key belongs to first partition clockwise from key's ring position.
    Adding partition: only keys in one segment remapped (not all keys).

    BEFORE (3 nodes):
    Ring: [Node A: 0-333, Node B: 334-666, Node C: 667-999]

    AFTER (add Node D):
    Ring: [Node A: 0-250, Node D: 251-333, Node B: 334-666, Node C: 667-999]
    → Only keys 251-333 moved (from Node A to Node D)
    → All other keys unchanged

STRATEGY 3: DIRECTORY/LIST PARTITIONING

  Explicit mapping table: key value → partition.

  Example: multi-tenant SaaS, partition by tenant_id:

  Directory (stored in config service or cache):
  Tenant A → Shard 1 (EU-West datacenter)
  Tenant B → Shard 3 (US-East datacenter)
  Tenant C → Shard 1 (EU-West datacenter)

  Flexibility: Tenant B can be migrated from Shard 3 to Shard 5 by updating directory.
               No data movement lookup change needed.
  Hot Spot Control: large tenants can be given dedicated shards.
                    small tenants can share shards.

  Lookup cost: every request must consult directory.
  Fix: cache directory aggressively (rarely changes).
  Fix: encode shard ID in customer-facing IDs (no lookup needed).
       e.g., customer_id = "SHARD2-789034" → directly route to shard 2

COMPOSITE PARTITIONING (real-world):

  Cassandra: partition key + clustering columns

  Table: user_activity
  Partition key: (user_id, month)  ← hash partitioned by this composite key
  Clustering columns: timestamp    ← sorted within partition

  Partition (user_id=123, month=2023-03): contains all of user 123's activity in March.
    → All related data co-located in one partition (no scatter-gather for user's monthly activity)
    → Within partition: sorted by timestamp (efficient range scans within partition)
    → Across partitions: distributed by hash of (user_id, month) → even distribution

  DynamoDB:
  Partition key (hash key): user_id  ← determines physical partition
  Sort key: timestamp                ← sorted within partition

  → Identical concept to Cassandra composite key.

CHOOSING A PARTITIONING KEY:

  BAD keys:
  - Low cardinality: status (ACTIVE/INACTIVE) → 2 partitions max, 90% in ACTIVE
  - Monotonically increasing: created_at → all writes to latest partition (hot spot)
  - Sequential ID from single sequence: id=1,2,3... → partition 0 gets 1-10M first

  GOOD keys:
  - High cardinality: user_id, order_id (UUIDs) → even distribution
  - Evenly distributed: hash-based keys, UUIDs
  - Query access patterns: partition key matches most common query filter

  RULE: If most queries filter by X, partition by X (avoids scatter-gather).
        If X creates hot spots: hash(X) as partition key (sacrifices range queries).

CROSS-PARTITION QUERIES (the main trade-off):

  Single-partition query (fast):
    SELECT * FROM orders WHERE user_id = 123  -- partition key = user_id
    → Route to 1 partition → O(1) routing → fast

  Cross-partition query (slow):
    SELECT COUNT(*) FROM orders WHERE amount > 1000  -- amount is NOT partition key
    → Must query ALL partitions → scatter-gather → merge results → slow

  Solutions:
  1. Denormalise: store precomputed aggregates in a separate table
  2. Secondary index: maintained per-partition (Cassandra local secondary index)
     or globally across partitions (DynamoDB GSI — expensive: double writes)
  3. CQRS: separate read store optimised for cross-partition queries (ElasticSearch)
  4. Accept: analytical queries hit all partitions; use columnar store for analytics
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Data Partitioning:

- Single database node: bounded by disk, CPU, memory of one machine
- All writes serialised through one node: throughput ceiling ~50K ops/sec
- Table scans on 1 billion rows: minutes per query even with indexes

WITH Data Partitioning:
→ Horizontal scale: N nodes = N× storage, N× write throughput
→ Partition pruning: range queries scan only relevant partitions
→ Parallel processing: scatter-gather queries executed in parallel across shards

---

### 🧠 Mental Model / Analogy

> A library organised by Dewey Decimal System (range partitioning): books 000-299 are in Wing A, 300-599 in Wing B, 600-999 in Wing C. Find a book: go straight to the correct wing (fast lookup by known range). But all new science books (900s) always go to Wing C → Wing C is crowded (hot spot). Alternatively, shelve books alphabetically by ISBN last 3 digits (hash partitioning): books are spread evenly, no hot spots, but all books by the same author are scattered across all wings (poor range scan for related data).

"Library wings" = partitions/shards
"Dewey Decimal ranges" = range partitioning (fast range queries, hot spot risk)
"ISBN last-3-digit hash" = hash partitioning (even distribution, poor range queries)
"Go straight to correct wing" = partition pruning (routing to exactly one shard)
- "All new science books → Wing C is crowded" = time-series write hot spot

---

### ⚙️ How It Works (Mechanism)

**Application-level hash partitioning with consistent hashing:**

```java
public class ConsistentHashRouter {

    private final TreeMap<Integer, String> ring = new TreeMap<>();
    private static final int VIRTUAL_NODES = 150;  // virtual nodes per physical shard

    public void addShard(String shardId) {
        for (int i = 0; i < VIRTUAL_NODES; i++) {
            int hash = hash(shardId + "-virtual-" + i);
            ring.put(hash, shardId);
        }
    }

    public void removeShard(String shardId) {
        for (int i = 0; i < VIRTUAL_NODES; i++) {
            int hash = hash(shardId + "-virtual-" + i);
            ring.remove(hash);
        }
    }

    public String getShardForKey(String key) {
        if (ring.isEmpty()) throw new IllegalStateException("No shards available");
        int hash = hash(key);
        // Find first shard clockwise from key's hash position:
        Map.Entry<Integer, String> entry = ring.ceilingEntry(hash);
        if (entry == null) {
            entry = ring.firstEntry();  // wrap around the ring
        }
        return entry.getValue();
    }

    private int hash(String key) {
        // MurmurHash3 — non-cryptographic, fast, excellent distribution:
        return Math.abs(key.hashCode());  // simplified; use MurmurHash in production
    }

    // Example:
    public static void main(String[] args) {
        ConsistentHashRouter router = new ConsistentHashRouter();
        router.addShard("shard-1");
        router.addShard("shard-2");
        router.addShard("shard-3");

        System.out.println(router.getShardForKey("user:123"));  // → shard-2
        System.out.println(router.getShardForKey("user:456"));  // → shard-1

        // Add shard-4 → only ~25% of keys remapped (not all!)
        router.addShard("shard-4");
        System.out.println(router.getShardForKey("user:123"));  // may still be shard-2
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Scalability requirement (data too large for single node)
        │
        ▼
Data Partitioning Strategies ◄──── (you are here)
(range / hash / directory)
        │
        ├── Consistent Hashing (hash partitioning without full resharding)
        ├── Hot Shard (failure mode: uneven partitioning key)
        └── Cross-Partition Queries (cost of scatter-gather queries)
```

---

### 💻 Code Example

**PostgreSQL list partitioning for multi-tenant SaaS:**

```sql
-- Multi-tenant SaaS: partition orders by region for data sovereignty
CREATE TABLE orders (
    id BIGSERIAL,
    tenant_id BIGINT,
    region VARCHAR(10),  -- 'EU', 'US', 'APAC'
    amount DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW()
) PARTITION BY LIST (region);

-- Each partition stores a specific region's data:
CREATE TABLE orders_eu   PARTITION OF orders FOR VALUES IN ('EU');
CREATE TABLE orders_us   PARTITION OF orders FOR VALUES IN ('US');
CREATE TABLE orders_apac PARTITION OF orders FOR VALUES IN ('APAC');

-- INSERT automatically routes to correct partition:
INSERT INTO orders (tenant_id, region, amount) VALUES (1, 'EU', 99.99);
-- → stored in orders_eu

-- Query with partition key in WHERE: only scans orders_eu (pruning):
EXPLAIN SELECT * FROM orders WHERE region = 'EU' AND amount > 50;
-- Seq Scan on orders_eu (NOT orders_us or orders_apac)

-- Verify partition routing:
SELECT tableoid::regclass, * FROM orders WHERE tenant_id = 1;
-- tableoid = orders_eu
```

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                                                                                                                                                                                                                                                                             |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Hash partitioning eliminates all hot spots        | Hash partitioning eliminates hot spots caused by skewed key distribution. It does NOT eliminate hot spots caused by skewed access frequency: if 90% of requests are for user_id=1 (a celebrity), that partition is still hot even though the data is "evenly" distributed by hash. Solution: caching, application-level fan-out, or separate celebrity-tier handling                                                |
| More partitions always means better performance   | Each partition has overhead: metadata, connections, replication lag tracking. Too many partitions (10,000+) cause: query planner overhead (PostgreSQL evaluates all partitions), connection pool exhaustion (each shard = separate connection pool), coordination overhead. Rule of thumb: partition count should match expected parallelism (number of nodes × cores), typically 8–256 partitions for most systems |
| Partitioning solves write hot spots automatically | Partitioning only redistributes load if the partition key is chosen correctly. Using `user_id` as partition key: good if load is evenly distributed across users. Using `status` (ACTIVE/INACTIVE): bad — 95% of active records in one partition. The key must have high cardinality AND roughly uniform access frequency                                                                                           |
| You can always add partitions without downtime    | With simple `hash % N` partitioning: changing N requires remapping all records (major migration). With consistent hashing: adding nodes remaps only ~1/N of records. With range/list partitioning: adding a new partition for future ranges is online with no data migration, but re-partitioning existing ranges requires online table reorganisation                                                              |

---

### 🔥 Pitfalls in Production

**Hot shard from monotonically increasing partition key:**

```
PROBLEM: Time-series table partitioned by created_at (range partition)

  Partition 1: orders Jan 2023  → 10M rows (COLD: read-only after month ends)
  Partition 2: orders Feb 2023  → 10M rows (COLD: read-only after month ends)
  Partition 3: orders Mar 2024  → 5M rows (HOT: all writes land here)

  All application writes go to partition 3 (current month).
  CPU on node hosting partition 3: 95%. Other nodes: 5%.

  This is ALWAYS the case with time-ordered write workloads + range partitioning!

BAD: Single partition for current time period:
  CREATE TABLE orders_2024_03 PARTITION OF orders
    FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');
  -- All March writes: hot partition. Shards 1-2: idle.

FIX 1: Composite partition key (time + hash bucket):
  Partition key: (created_at_month, user_id_bucket)
  user_id_bucket = user_id % 8  -- 8 buckets per month

  March 2024, bucket 0: user_id % 8 = 0
  March 2024, bucket 1: user_id % 8 = 1
  ...
  → 8 equal-sized current-month partitions → 8× distributed write load

FIX 2: Cassandra-style time bucketing:
  partition_key = (user_id, year_month)
  → Each user's data for each month = one partition
  → Current-month data: distributed across user_id hash (uniform)
  → No single hot partition for all new writes

FIX 3: Accept hot spot + vertical scale for write node:
  If resharding isn't feasible: upsize write node.
  Use read replicas to offload read queries from hot write shard.
  Archive old partitions to cheaper storage (move cold partitions to S3 via pg_partman).
```

---

### 🔗 Related Keywords

- `Sharding (System)` — data partitioning across separate database servers (nodes)
- `Consistent Hashing` — hash partitioning algorithm that minimises key remapping on resharding
- `Hot Shard` — failure mode where one partition receives disproportionate load
- `Cross-Partition Query` — scatter-gather queries that must fan out to multiple partitions

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Range: good range queries, hot spot risk; │
│              │ Hash: even dist., poor range queries      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Table > 100M rows; multi-tenant isolation;│
│              │ horizontal write scale-out needed         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Low-cardinality partition key; monotonic  │
│              │ write key without composite bucketing     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Library wings by Dewey Decimal — fast    │
│              │  lookup, but new science books crowd      │
│              │  one wing."                               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Consistent Hashing → Hot Shard            │
│              │ → Cross-Partition Queries                 │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Design the partitioning strategy for a ride-sharing app's `trips` table with 2 billion rows. The most common queries are: (a) "get all trips for user X in the last 30 days," (b) "get all active trips in city Y right now," (c) "get total revenue for date range D1–D2." Choose a partition key for each query pattern. Can a single partition key serve all three efficiently? What trade-offs would you accept, and how would you handle the queries that don't match the chosen partition key?

**Q2.** Your system uses `hash(user_id) % 8` to route to 8 shards. Traffic has grown and you need to add 4 more shards (total 12). Describe the migration process: how do you re-partition data with minimal downtime? What is the relationship between the old partition assignment and new assignment — what fraction of records need to move? Compare this to consistent hashing: what fraction of records would move when adding the same 4 shards using consistent hashing?
