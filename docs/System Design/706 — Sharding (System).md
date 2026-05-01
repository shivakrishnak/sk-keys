---
layout: default
title: "Sharding (System)"
parent: "System Design"
nav_order: 706
permalink: /system-design/sharding/
number: "706"
category: System Design
difficulty: ★★★
depends_on: "Horizontal Scaling, Consistent Hashing, Partitioning"
used_by: "Hot Shard, Data Partitioning Strategies, NoSQL"
tags: #advanced, #distributed, #database, #architecture, #scalability
---

# 706 — Sharding (System)

`#advanced` `#distributed` `#database` `#architecture` `#scalability`

⚡ TL;DR — **Sharding** is a horizontal database partitioning strategy where data is split across multiple independent database nodes (shards), each owning a subset of the total data, enabling linear storage and throughput scaling.

| #706            | Category: System Design                              | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------- | :-------------- |
| **Depends on:** | Horizontal Scaling, Consistent Hashing, Partitioning |                 |
| **Used by:**    | Hot Shard, Data Partitioning Strategies, NoSQL       |                 |

---

### 📘 Textbook Definition

**Sharding** (database sharding) is a horizontal scaling technique where a large dataset is partitioned across multiple separate database instances, each called a shard, such that each shard holds a distinct, non-overlapping subset of the data. Every shard has the same schema but different data. Queries are routed to the appropriate shard based on a **shard key** — a field (or hash of a field) in the data that determines which shard owns a given record. Sharding addresses the fundamental limitation of vertical scaling: beyond a certain size, no single machine can hold all data or handle all query throughput. Common sharding strategies: **range-based** (user IDs 0-999K → shard 1), **hash-based** (hash(user_id) % num_shards), and **directory-based** (lookup table maps key to shard). Sharding is a core feature of distributed databases (Cassandra, MongoDB, DynamoDB, Vitess/MySQL).

---

### 🟢 Simple Definition (Easy)

Sharding: instead of one enormous database, split the data across multiple smaller databases. User IDs 1-1M on shard 1, 1M-2M on shard 2, etc. Each shard is smaller and faster. You can add more shards as data grows. The trade-off: queries that need data from multiple shards (JOINs) are complex. But single-key lookups (user by ID) are fast and scalable.

---

### 🔵 Simple Definition (Elaborated)

Instagram has 1 billion users. A single PostgreSQL instance cannot store 1 billion user profiles (performance degrades, disk fills up). Sharding: split users across 1,000 database shards. User 123,456,789 → hash(123456789) % 1000 = shard 456 → query shard 456 only. Each shard: 1 million users, small and fast. Add another 1 billion users? Add 1,000 more shards. Sharding is how every large-scale internet company (Facebook, Twitter, Pinterest, Uber) scales their primary databases beyond what any single machine can handle.

---

### 🔩 First Principles Explanation

**Sharding strategies and their trade-offs:**

```
STRATEGY 1: RANGE-BASED SHARDING

  Shard key: user_id (integer)
  Shards:
    Shard A: user_id [0, 1,000,000)
    Shard B: user_id [1,000,000, 2,000,000)
    Shard C: user_id [2,000,000, 3,000,000)

  Routing:
    user_id = 1,500,000 → Shard B
    user_id = 2,750,000 → Shard C

  ADVANTAGE: Range queries efficient (all users 1M-2M on same shard).
  PROBLEM: Hot shard (uneven load).
    All new users (highest IDs) → written to last shard.
    Shard C gets 100% of new user writes while A, B are idle.
    This is the "hot shard" problem (see keyword #707).

STRATEGY 2: HASH-BASED SHARDING

  Shard key: user_id
  Routing: shard_id = hash(user_id) % num_shards

  Example (4 shards):
    user_id=1: hash(1) % 4 = 1 → Shard 1
    user_id=2: hash(2) % 4 = 2 → Shard 2
    user_id=100: hash(100) % 4 = 0 → Shard 0
    user_id=101: hash(101) % 4 = 1 → Shard 1

  ADVANTAGE: Even distribution. No hot shards from sequential keys.
  PROBLEM: Range queries require all shards (scatter-gather).
    "Users registered between Jan 1-Jan 7" → must query all 4 shards.
    Adding/removing shards: requires resharding (all data remapped).

  SOLUTION to resharding: Consistent Hashing (see Distributed Systems category).

STRATEGY 3: DIRECTORY-BASED SHARDING (Lookup Table)

  Maintain a separate shard directory service:
  Shard directory:
    user_id range 0-999K → Shard A (Europe)
    user_id range 1M-2M → Shard B (US)
    user_id range 2M+ → Shard C (Asia)
    VIP users → Shard VIP (high-performance tier)

  ADVANTAGE: Flexible. Can move individual users between shards.
  PROBLEM: Directory service is a single point of failure and bottleneck.
    Solution: replicate directory, cache it aggressively.

SHARD KEY SELECTION CRITERIA:

  GOOD shard key:
    1. HIGH CARDINALITY: many possible values (not boolean "active/inactive")
    2. EVENLY DISTRIBUTED: hash or natural distribution (not "country_code" — US dominates)
    3. FREQUENTLY QUERIED: most queries filter by shard key (no cross-shard)
    4. IMMUTABLE: shard key should never change (changing = re-routing = data migration)

  COMMON SHARD KEYS:
    user_id: high cardinality, usually immutable, most queries are per-user ✓
    tenant_id: multi-tenant SaaS — one shard per customer/tenant ✓
    timestamp: high cardinality but sequential → hot shard problem ✗
    country_code: low cardinality (200 countries), US dominates ✗
    email: high cardinality, immutable, but alphabetical → range hot shard ✗

CROSS-SHARD QUERIES (the hard problem):

  Query: "Find all users who posted in the last 24 hours"
  Problem: users are on different shards.

  OPTION A: Scatter-Gather
    Send query to ALL shards simultaneously.
    Collect and merge results in application.

    // Application: scatter query
    List<Future<List<User>>> futures = shards.stream()
      .map(shard -> executor.submit(() -> shard.query("SELECT * FROM users WHERE ..."))
      .collect(toList());
    List<User> allUsers = futures.stream()
      .flatMap(f -> f.get().stream())
      .sorted(comparingByTime())
      .collect(toList());

    PROBLEM: Latency = slowest shard (not average).
             With 100 shards: if 1 shard is slow → entire query slow.

  OPTION B: Denormalisation + secondary index
    Maintain a separate "recent_activity" table (not sharded, or sharded by time).
    Write to both user shard (for per-user queries) AND activity table (for global queries).
    Trade: write complexity for read simplicity.

  OPTION C: Avoid cross-shard queries in design
    Rethink data model: if cross-shard queries are frequent, shard key is wrong.
    Resharding is expensive but sometimes necessary.

RESHARDING (adding/removing shards):

  PROBLEM: hash(user_id) % 4 → add 1 shard → hash(user_id) % 5
  75% of all data maps to a different shard → must migrate 75% of data.

  SOLUTIONS:
  1. CONSISTENT HASHING: only ~1/N fraction of data moves when adding shard N+1.
  2. VIRTUAL NODES: pre-assign many virtual shards (1,000) to physical shards (10).
     Add physical shard: reassign some virtual shards. Only virtual shard data moves.
  3. DOUBLE WRITE PERIOD: write to both old and new shards during migration.
     Backfill: copy old shard data to new shard.
     Cutover: switch reads to new shard after backfill complete.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Sharding:

- Single DB: storage limit reached → can't add more data
- Single DB: write throughput ceiling → all writes queue on one server
- Single DB: one hardware failure → full database unavailable

WITH Sharding:
→ Linear storage scaling: add shards = add storage capacity
→ Linear throughput scaling: add shards = add write/read throughput
→ Fault isolation: one shard fails → only its portion of data affected

---

### 🧠 Mental Model / Analogy

> A library with one room (single database) runs out of shelf space. Solution: build multiple rooms (shards), each housing a different section: Room A = authors A-F, Room B = authors G-M, Room C = authors N-Z. Each room has its own librarian (database server). Looking up a book by author: go to the correct room directly. Looking up all books published in 1990: visit all rooms (cross-shard query — expensive). Adding more books: add more rooms, or add more shelves to existing rooms.

"Library rooms" = database shards (independent storage nodes)
"Authors A-F in Room A" = range-based sharding (shard key = author name)
"Librarian per room" = dedicated CPU/memory per shard (parallelism)
"Direct room lookup by author" = single-shard query (fast, O(1))
"Visit all rooms for 1990 books" = cross-shard scatter-gather query (slow, O(N shards))

---

### ⚙️ How It Works (Mechanism)

**Hash-based sharding with shard routing:**

```java
public class ShardRouter {
    private final List<DataSource> shards;
    private final int numShards;

    public ShardRouter(List<DataSource> shards) {
        this.shards = shards;
        this.numShards = shards.size();
    }

    // Get the shard for a given user ID:
    public DataSource getShardForUser(long userId) {
        int shardIndex = (int)(Math.abs(userId) % numShards);
        return shards.get(shardIndex);
    }

    // Single-shard query (efficient):
    public User findUserById(long userId) {
        DataSource shard = getShardForUser(userId);
        return jdbcTemplate(shard).queryForObject(
            "SELECT * FROM users WHERE user_id = ?",
            userRowMapper, userId
        );
    }

    // Cross-shard query (scatter-gather, expensive):
    public List<User> findActiveUsersGlobal() {
        List<Future<List<User>>> futures = shards.stream()
            .map(shard -> CompletableFuture.supplyAsync(() ->
                jdbcTemplate(shard).query(
                    "SELECT * FROM users WHERE active = true",
                    userRowMapper
                )
            ))
            .collect(Collectors.toList());

        return futures.stream()
            .map(CompletableFuture::join)
            .flatMap(List::stream)
            .collect(Collectors.toList());
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Vertical Scaling (single-node limit reached)
        │ (exceeded: need multi-node)
        ▼
Sharding (System) ◄──── (you are here)
(horizontal data partitioning)
        │
        ├── Hot Shard (problem: uneven distribution)
        ├── Consistent Hashing (solution: resharding minimization)
        └── Data Partitioning Strategies (broader category)
```

---

### 💻 Code Example

**MongoDB: shard configuration for user collection:**

```javascript
// Enable sharding on database:
sh.enableSharding("myapp");

// Shard the users collection by hashed user_id:
sh.shardCollection("myapp.users", { user_id: "hashed" });
// "hashed" = hash-based sharding → even distribution, no hot shard from sequential IDs

// Range-based sharding (alternative, for range queries):
sh.shardCollection("myapp.orders", { order_date: 1 });
// Range-based = efficient range queries, but risks hot shard on recent dates

// Add shards (horizontal scaling):
sh.addShard("mongodb://shard1:27017");
sh.addShard("mongodb://shard2:27017");
sh.addShard("mongodb://shard3:27017");

// MongoDB automatic: mongos router handles shard routing transparently
// Application queries mongos → mongos routes to correct shard(s)
db.users.findOne({ user_id: 12345 });
// → mongos: hash(12345) → shard2 → query shard2 only

db.orders.find({ order_date: { $gte: ISODate("2024-01-01") } });
// → mongos: range query on order_date → may hit multiple shards (scatter-gather)
```

---

### ⚠️ Common Misconceptions

| Misconception                                              | Reality                                                                                                                                                                                                                                                                       |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Sharding is for very large companies only                  | Any database that grows beyond ~500GB-1TB may benefit from sharding. Many mid-sized SaaS companies (10M+ users) need sharding. The question is not company size but data size, write throughput, and query patterns                                                           |
| Sharding eliminates the need for database replication      | Sharding (for scale) and replication (for availability) solve different problems and are used together. Each shard typically has primary-replica replication for high availability. Sharding without replication: if one shard goes down, that portion of data is unavailable |
| You can freely change the shard key after deployment       | Changing the shard key requires migrating all data to new shards — a complex, expensive, disruptive operation. The shard key must be chosen carefully before initial data ingestion. This is one of the hardest decisions in database design                                  |
| Hash-based sharding guarantees perfectly even distribution | Hash-based sharding distributes well on average but can be slightly uneven depending on the hash function and key distribution. Consistent hashing with virtual nodes provides more even distribution and simpler rebalancing                                                 |

---

### 🔥 Pitfalls in Production

**Choosing timestamp as shard key:**

```
PROBLEM: Sequential shard key creates hot shard

  Design: order_service shards orders by created_at (timestamp)
  Shard routing: shard_id = year_month(created_at)
    Jan 2024 orders → Shard_2024_01
    Feb 2024 orders → Shard_2024_02
    ...

  RESULT:
    All writes ALWAYS go to the current month's shard.
    All other shards: READ-ONLY (just serving historical queries).
    New shard (current month): handles 100% of write load.

  This is not sharding — it's archiving with extra steps.
  The "hot shard" problem: one shard overwhelmed while others idle.

FIX: Use user_id or tenant_id as shard key, partition by time within each shard

  // Orders table: sharded by user_id (even distribution of writes)
  // Within each user's shard: indexed by created_at for time range queries

  sh.shardCollection("myapp.orders", { "user_id": "hashed" })

  // "Get all orders for user 12345 in January 2024":
  db.orders.find({
    user_id: 12345,
    created_at: { $gte: ISODate("2024-01-01"), $lt: ISODate("2024-02-01") }
  })
  // → Routes to shard(hash(12345)), indexed by created_at there
  // Single shard, fast range query on that shard.

  // "Get all orders in January 2024 (global)":
  // Still requires scatter-gather. Accept this as a trade-off for write distribution.
  // If this query is critical, maintain separate analytics table (OLAP).
```

---

### 🔗 Related Keywords

- `Hot Shard` — when one shard receives disproportionate load (poor shard key choice)
- `Consistent Hashing` — minimises data movement when adding/removing shards
- `Horizontal Scaling` — sharding is the primary form of horizontal database scaling
- `Data Partitioning Strategies` — broader category covering sharding, range partitioning, etc.
- `NoSQL` — Cassandra, DynamoDB, MongoDB all use sharding as core architecture

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Split data across independent DB nodes;   │
│              │ each shard owns a subset of the data      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ DB storage >500GB–1TB; write throughput   │
│              │ ceiling reached on single node            │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Sequential shard key (hot shard);         │
│              │ frequent cross-shard JOINs in queries     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Library with many rooms — each room      │
│              │  holds a different section of books."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Hot Shard → Consistent Hashing            │
│              │ → Data Partitioning Strategies            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're designing a sharding strategy for a social network's posts table (5 billion posts, growing at 50M/day). Evaluate three candidate shard keys: (a) `post_id` (UUID), (b) `user_id`, (c) `created_at` timestamp. For each: explain whether it creates a hot shard problem, whether it supports efficient single-user feed queries, and whether it supports efficient global trending content queries. Which would you choose as primary shard key? How would you handle the global trending query for the key you chose?

**Q2.** Your application currently uses hash-based sharding with 8 shards: `shard = hash(user_id) % 8`. You need to scale to 16 shards. Calculate what percentage of existing data must be migrated in a naive modulo-based approach. Then explain how Consistent Hashing with 160 virtual nodes (20 per physical shard) would handle the same expansion from 8 to 16 physical nodes, and what percentage of data would need to migrate in that approach.
