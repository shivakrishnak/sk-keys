---
id: SYD-031
title: Sharding
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-008, SYD-011
used_by: SYD-032, SYD-034, SYD-035
related: SYD-008, SYD-011, SYD-032, SYD-033, SYD-034, SYD-042
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
nav_order: 31
permalink: /technical-mastery/syd/sharding/
---

⚡ TL;DR - Sharding (horizontal partitioning) splits
a dataset across multiple database nodes (shards)
where each shard holds a disjoint subset of the data.
Unlike replication (every node has all data), each
shard holds only a fraction. Reads and writes for a
given record are routed to exactly one shard based
on the shard key. Sharding is the primary technique
for scaling writes and storage beyond what a single
database node can handle.

| #031 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Horizontal vs Vertical Scaling, Database Replication | |
| **Used by:** | Hot Shard, Denormalization for Scale, Fan-Out | |
| **Related:** | Horizontal vs Vertical Scaling, DB Replication, Hot Shard, Read-Heavy vs Write-Heavy, Denormalization for Scale, Data Partitioning Strategies | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A social network stores user posts in a single MySQL
database. At 1 million users, performance is fine.
At 50 million users, the posts table has 2 billion
rows. A single primary server handles 10,000 writes/sec.
Adding read replicas helps with reads, but ALL writes
go to the single primary. The write bottleneck is
physical: one server's disk, CPU, and network cannot
handle 100,000 writes/sec. You cannot "add more RAM"
to solve this.

**THE WRITE SCALABILITY WALL:**
Replication distributes reads. But every replica must
process every write (to stay in sync with the primary).
Adding 10 replicas does not increase write capacity;
it increases read capacity. To scale writes, you must
split the write workload across multiple independent
primaries. Sharding does exactly this.

---

### 📘 Textbook Definition

**Sharding:** A database scaling technique that
horizontally partitions data across multiple nodes
(shards), where each shard is an independent database
holding a disjoint subset of the full dataset.

**Shard key:** The attribute used to determine which
shard a record belongs to. The shard key is the most
critical design decision in a sharded system.

**Shard function:** The function that maps a shard
key value to a shard number:
- **Hash sharding:** `shard = hash(key) % num_shards`
- **Range sharding:** `shard = lookup_range_table(key)`
- **Directory sharding:** `shard = lookup_directory(key)`

Each shard typically runs with its own replication
group (primary + replicas) for redundancy. The
application (or a routing layer) maps requests to
the correct shard.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Split the data into N independent partitions (shards);
each shard owns a fraction of the data and handles
its fraction of the write load.

**One analogy:**
> A library with 1 million books assigns each book
> to one of 10 floors based on the first letter of
> the title (A-C = floor 1, D-F = floor 2, ...).
> Each floor is its own independent section with its
> own librarian.
>
> To find a book: go to the correct floor (shard routing).
> To add a book: add it to the correct floor (shard write).
> No floor is overwhelmed by all 1 million books;
> each floor handles ~100,000 books.
>
> The problem: a "The..." title would put all books
> starting with "T" on one floor (hot shard).
> Shard key design is everything.

**One insight:**
Sharding trades query complexity for write scalability.
Queries that touch one shard are as fast as non-sharded
queries. Queries that span all shards (cross-shard joins,
aggregations) require scatter-gather and become O(shards)
more complex. This is the core tradeoff that all shard
key design decisions must navigate.

---

### 🔩 First Principles Explanation

**SHARD KEY STRATEGIES:**

**1. Hash Sharding:**
```
shard_id = hash(user_id) % num_shards

Example: user_id=12345
  hash(12345) = 2847293847
  2847293847 % 4 shards = shard 3

All data for user 12345 → shard 3
Consistent distribution (uniform hash function)
```
Pros: Even data distribution; simple.
Cons: Range queries require scatter-gather.
     Resharding requires data movement.

**2. Range Sharding:**
```
Shard 1: user_id 1 - 1,000,000
Shard 2: user_id 1,000,001 - 2,000,000
Shard 3: user_id 2,000,001 - 3,000,000

Range queries efficient: all users 100K-200K → Shard 1
New user signups skew to last shard (hotspot)
```
Pros: Range queries efficient; logical data locality.
Cons: Hotspots at boundaries (latest users, latest events).

**3. Directory Sharding:**
```
Lookup table:
  user_id → shard_id
  12345   → shard 3
  99999   → shard 1

Flexible reassignment without rehashing
Lookup table becomes single point of failure
```

**CONSISTENT HASHING (alternative to modulo):**
```
Problem with hash % N:
  N=4 shards, add 1 (N=5): most keys reassign
  (hash(key) % 4 vs hash(key) % 5 = different shard)
  → Requires migrating ~75% of data

Consistent hashing:
  Hash space is a ring (0 to 2^32)
  Each shard "owns" a segment of the ring
  Adding a shard: only reassign ~1/N of data
  Used by: Cassandra, DynamoDB, Redis Cluster
```

**THE CARDINAL RULE OF SHARD KEY SELECTION:**
```
A good shard key:
  1. Even distribution: no single shard gets >>1/N data
  2. Query locality: most queries access 1 shard
     (avoid cross-shard queries)
  3. Stable: does not change after record creation
  4. High cardinality: many distinct values
  5. Not a "hot key": no single value accounts
     for a large fraction of traffic

Classic mistake:
  Shard by user.country → US shard gets 40% of data
  Shard by created_at (timestamp) → newest shard hot
  Shard by user.plan (free/paid) → free shard gets 99%
```

---

### 🧪 Thought Experiment

**SCENARIO: Designing a sharding strategy for Twitter-like posts**

Requirements: 500M users, 500M posts/day, read-heavy

**Option A: Shard by user_id (hash)**
- All posts for a user → same shard
- User timeline queries: single shard (efficient)
- "What are the latest 100 posts globally?" 
  → scatter to all shards, gather + merge (expensive)
- Celebrity user (50M followers) → their shard
  receives all reads for that user's posts
  (manageable if routing is correct)

**Option B: Shard by post_id (hash)**
- Post lookups: single shard (efficient)
- User timeline ("all posts by user_id=X"):
  → scatter to all shards (every post could be anywhere)
- Wrong choice for query patterns that need user data

**Option C: Shard by post_id (range: by time)**
- Latest posts: all on newest shard (hotspot)
- Dead shards for old data; one hot shard for new
- Wrong choice for write-heavy time-series data

**WINNER: Option A (user_id hash)**
Twitter's actual approach: shard by user_id. Most
reads are "give me user X's timeline" which resolves
to one shard. Follower feed assembly (fan-out) is
handled at the application layer, not at the database.

---

### 🧠 Mental Model / Analogy

> Sharding is like dividing a phone book into volumes
> (A-E, F-L, M-R, S-Z). Each volume is an independent
> physical book stored in a different location.
>
> To look up "Smith, John": go directly to volume 3
> (S-Z). One lookup. Fast.
>
> To find "everyone named after a city": check all
> 4 volumes (scatter-gather). O(4) work.
>
> Volume assignment is based on last name (shard key).
> Having all "Smiths" (a common name) creates a fat
> volume (hot shard) if not handled.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Sharding splits a large database table across multiple
servers. Each server holds a piece of the data.
Requests are routed to the right server based on the
data being requested.

**Level 2 - How to use it (junior developer):**
Application sharding: compute `shard_id = user_id % 4`
and connect to the right database. Middleware sharding:
use a proxy (Vitess, ProxySQL) that handles routing
transparently. Managed sharding: use DynamoDB or
MongoDB Atlas where sharding is handled for you.

**Level 3 - How it works (mid-level engineer):**
Choose a shard key based on the most common query
pattern. For user-centric apps: user_id. For
time-series: consider time + entity. Implement a
routing layer (application code or proxy) that maps
shard key → connection pool. Handle the "shard
routing config" as a versioned, replicated config
rather than a hardcoded constant.

**Level 4 - Why it was designed this way (senior/staff):**
Sharding pushes distributed systems complexity to the
application layer. Cross-shard joins are expensive
because there is no server that has all the data.
Instead of a join, you do two separate queries and
join them in application code. This is why data
modeling for sharded systems must be "shard-local":
design tables so that related data that is queried
together lives in the same shard.

**Level 5 - Mastery (distinguished engineer):**
The key insight missed by most: sharding multiplies
operational complexity. N shards = N databases to
monitor, backup, fail over, and tune independently.
Resharding (adding shards) requires data migration
which is live-dangerous. Vitess (YouTube's sharding
middleware) was built specifically to handle MySQL
resharding transparently. Most startups should use
a managed distributed DB (DynamoDB, CockroachDB,
Spanner) that handles sharding internally rather than
implementing application-level sharding, unless they
have extreme customization requirements.

---

### ⚙️ How It Works (Mechanism)

**Sharded architecture:**

```
┌────────────────────────────────────────────────────────┐
│ SHARDED WRITE PATH                                    │
│                                                        │
│  Write: user_id=12345, post="Hello World"             │
│                                                        │
│  Application:                                          │
│    shard_id = hash(12345) % 4 = shard 2               │
│    connect to shard 2 primary                          │
│    INSERT post WHERE user_id=12345                     │
│                                                        │
│  Shard topology:                                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ Shard 0  │ │ Shard 1  │ │ Shard 2  │ │ Shard 3  │ │
│  │ Primary  │ │ Primary  │ │ Primary  │ │ Primary  │ │
│  │ + 2 reps │ │ + 2 reps │ │ + 2 reps │ │ + 2 reps │ │
│  │users:    │ │users:    │ │users:    │ │users:    │ │
│  │0,4,8...  │ │1,5,9...  │ │2,6,10... │ │3,7,11... │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│                                                        │
│  Write capacity: 4x a single node                     │
│  Storage: 4x a single node (if even distribution)     │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Application-level shard routing**
```python
# Simple hash-based shard routing
import hashlib
from typing import Dict
import psycopg2  # PostgreSQL driver

class ShardRouter:
    """Routes database operations to correct shard."""

    def __init__(self, shard_configs: Dict[int, dict]):
        """
        shard_configs: {shard_id: {host, port, dbname, ...}}
        """
        self.num_shards = len(shard_configs)
        self.connections = {}
        for shard_id, config in shard_configs.items():
            self.connections[shard_id] = (
                psycopg2.connect(**config)
            )

    def get_shard_for_user(self, user_id: int) -> int:
        """Deterministic: same user_id always → same shard."""
        # Use hash for better distribution than modulo
        hash_value = int(
            hashlib.md5(str(user_id).encode()).hexdigest(),
            16
        )
        return hash_value % self.num_shards

    def get_connection(self, user_id: int):
        """Get database connection for user's shard."""
        shard_id = self.get_shard_for_user(user_id)
        return self.connections[shard_id]

router = ShardRouter({
    0: {"host": "shard0.db", "dbname": "users", ...},
    1: {"host": "shard1.db", "dbname": "users", ...},
    2: {"host": "shard2.db", "dbname": "users", ...},
    3: {"host": "shard3.db", "dbname": "users", ...},
})

def create_post(user_id: int, content: str):
    conn = router.get_connection(user_id)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO posts (user_id, content, created_at)"
        " VALUES (%s, %s, NOW())",
        (user_id, content)
    )
    conn.commit()

def get_user_posts(user_id: int, limit: int = 20):
    conn = router.get_connection(user_id)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM posts WHERE user_id = %s"
        " ORDER BY created_at DESC LIMIT %s",
        (user_id, limit)
    )
    return cursor.fetchall()
```

**Example 2 - BAD: Shard key that creates hotspot**
```python
# BAD: Shard by country → uneven distribution
# US users = 40% of all users → shard 0 is 4x larger

COUNTRY_SHARD_MAP = {
    "US": 0, "CA": 0, "UK": 1, "AU": 1,
    "IN": 2, "CN": 2, "JP": 3, ...
}

def get_shard_for_user_BAD(user_id: int, country: str) -> int:
    return COUNTRY_SHARD_MAP.get(country, 0)
    # US traffic → all to shard 0
    # Shard 0 becomes 4x more loaded
    # Shard 0 fills up faster → requires resharding sooner

# GOOD: Hash by user_id for even distribution
def get_shard_for_user_GOOD(user_id: int) -> int:
    return user_id % NUM_SHARDS
    # Even distribution regardless of user country
    # All shards grow at the same rate
    # Resharding can be planned predictably
```

---

### ⚖️ Comparison Table

| Approach | Write Scale | Read Scale | Complexity | Cross-shard Queries |
|---|---|---|---|---|
| **Single DB** | Single node limit | Read replicas | Low | N/A (all local) |
| **Replication only** | Primary limit | Scales with replicas | Medium | N/A |
| **Sharding (hash)** | Linear with shards | Per-shard replicas | High | Expensive (scatter-gather) |
| **Managed distributed DB** | Auto-scaled | Auto-scaled | Low (operationally) | Transparent (internal) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Sharding and replication are the same | Replication copies ALL data to multiple nodes for availability. Sharding splits data so each node has a SUBSET. They are complementary: each shard typically has its own replication group for HA. |
| You must shard from day one | Premature sharding is expensive. Most applications do not need sharding until they exceed a single node's capacity. A well-indexed single primary + read replicas can handle significant scale. Shard when a concrete bottleneck is hit, not preemptively. |
| Cross-shard queries can be efficient | They fundamentally require scatter-gather (query all shards, merge results). This is O(N-shards) overhead on every cross-shard query. Shard key design must minimize cross-shard query frequency for the most common queries. |

---

### 🚨 Failure Modes & Diagnosis

**Hot Shard (Uneven Data Distribution)**

**Symptom:**
One shard (shard 3) handles 60% of all write traffic.
Its CPU is at 95% while other shards are at 15%. The
shard 3 primary's disk fills up 4x faster than others.

**Root Cause:**
Shard key has a hot key pattern. Common causes:
1. Range sharding with time-based key: newest time
   range is always the hottest
2. A viral user: celebrity with 100M followers, all
   their traffic → 1 shard
3. Low-cardinality shard key: 4 shards keyed by
   subscription_plan (free/basic/pro/enterprise) where
   99% of users are "free"

**Fix:**
```sql
-- Diagnose: check shard row counts and QPS
SELECT shard_id, COUNT(*) as row_count
FROM shard_metadata GROUP BY shard_id;
-- If one shard has 4x more rows → bad key

-- Solutions:
-- 1. Change shard key (requires data migration)
-- 2. Add a "shard salt": shard by (user_id + random(1,4))
--    This spreads 1 user across 4 sub-shards
--    But requires querying 4 shards for 1 user (tradeoff)
-- 3. Application-level mitigation: cache celebrity
--    user data aggressively at the CDN layer to reduce
--    DB hit rate for the hottest shard
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Horizontal vs Vertical Scaling` - sharding is
  the execution of horizontal scaling for databases
- `Database Replication` - each shard runs with
  replication internally

**Builds On This (learn these next):**
- `Hot Shard` - the primary failure mode of sharding
- `Denormalization for Scale` - data modeling to avoid
  cross-shard joins
- `Data Partitioning Strategies` - deeper dive into
  partitioning approaches

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Splits dataset across N independent DB  │
│               │ nodes; each shard owns a disjoint subset│
├───────────────┼─────────────────────────────────────────┤
│ SHARD KEY     │ Must be: high cardinality, even dist,   │
│               │ query-local, stable, not a hot key      │
├───────────────┼─────────────────────────────────────────┤
│ STRATEGIES    │ Hash (even dist, no range queries)      │
│               │ Range (range queries, hotspot risk)     │
│               │ Directory (flexible, lookup overhead)   │
│               │ Consistent hash (online resharding)     │
├───────────────┼─────────────────────────────────────────┤
│ SCALES        │ Writes: linear with shard count         │
│               │ Storage: linear with shard count        │
│               │ Reads: per-shard replicas               │
├───────────────┼─────────────────────────────────────────┤
│ COST          │ Cross-shard joins = scatter-gather      │
│               │ Resharding = live data migration        │
│               │ Operational complexity = N x single DB  │
├───────────────┼─────────────────────────────────────────┤
│ RULE          │ Design tables so common queries are     │
│               │ shard-local (same shard for related data│
├───────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE  │ Hot Shard → Denormalization for Scale   │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Sharding splits data (not copies it). Each shard
   has a disjoint subset. Writes scale linearly.
   Replication copies; sharding splits.
2. Shard key design is everything. A bad shard key
   creates a hot shard and defeats the purpose. Choose
   a high-cardinality key with query locality.
3. Cross-shard queries require scatter-gather: query
   all shards, merge in application. Design data to
   minimize cross-shard query frequency.

**Interview one-liner:**
"Sharding horizontally partitions data across N independent
database nodes (shards), each owning a disjoint subset of the
data. Unlike replication (all nodes have all data), each shard
holds only 1/N of the data. Writes scale linearly: each shard
handles 1/N of the write load. The critical design decision is
the shard key - it must distribute data evenly and minimize
cross-shard queries. Hash sharding gives even distribution;
range sharding enables range queries. The main costs: cross-shard
joins require scatter-gather (O(shards) overhead), and resharding
requires live data migration. Most applications should prefer
managed distributed databases (DynamoDB, CockroachDB) that handle
sharding transparently rather than implementing application-level
sharding."
