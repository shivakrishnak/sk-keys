---
id: DST-013
title: Sharding / Horizontal Partitioning
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★☆☆
depends_on: DST-008, DST-011, DST-012
used_by: DST-030, DST-041, DST-042
related: DST-012, DST-014, DST-030, DST-065
tags:
  - distributed
  - data
  - scalability
  - foundational
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 13
permalink: /technical-mastery/distributed-systems/sharding/
---

⚡ TL;DR - Sharding splits a dataset across multiple nodes
by a partition key so that each node handles a subset of
the data; it solves write throughput limits and storage
limits that replication cannot, but introduces the complexity
of cross-shard operations and hotspot risk.

---

### 📋 Entry Metadata

| #013 | Category: Distributed Systems | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Node, Fault Tolerance, Replication | |
| **Used by:** | Consistent Hashing, Rebalancing, Range Queries on Shards | |
| **Related:** | Replication, Consistency, Consistent Hashing, Vertical Scaling | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An e-commerce platform stores all 500 million product records
on a single database node. Products can only be written by
one node. During a sale event, 100,000 writes per second
hit the single node. The node saturates. Storage is 40TB
on one server, requiring an increasingly expensive, ever-
larger server. Each new million products requires hardware
upgrades. This is vertical scaling: you are bounded by the
largest available machine.

**THE BREAKING POINT:**
Replication adds read capacity and fault tolerance, but all
writes still go to the primary. At high write rates, the
primary becomes the bottleneck. Adding 10 replicas does not
help with 100,000 writes per second. The only solution is
to split the data across multiple primary nodes, each
accepting writes for its portion of the data. That is sharding.

**THE INVENTION MOMENT:**
The term "shard" comes from online gaming - Ultima Online
(1997) used "shards" of the mystical gem to explain why
multiple server instances existed of the same game world.
Modern database sharding adopted the metaphor: each shard
is an independent fragment of the larger dataset.

---

### 📘 Textbook Definition

**Sharding** (also called **horizontal partitioning**) is the
practice of dividing a large dataset into smaller subsets
(shards) and distributing those shards across multiple
database nodes, each acting as the primary for its shard.
Unlike replication (which copies data), sharding splits data:
each record lives on exactly one shard. A **partition key**
(shard key) determines which shard a record belongs to.
Sharding enables write throughput and storage to scale
linearly with the number of shards. The challenges of sharding
include: cross-shard queries (no single node has all data),
shard rebalancing (redistributing data when shards are added),
hotspots (uneven distribution causing one shard to receive
disproportionate traffic), and the loss of ACID transactions
across shards.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Sharding cuts your database into pieces, each piece stored
on a different server, so you can write to multiple servers
at once.

**One analogy:**
> A library with one million books assigns each book to a
> shelf. A single-node database is a library with one
> librarian who handles all requests. A sharded database
> is a library with 10 rooms, each with its own librarian.
> Books A-C go to Room 1, D-G go to Room 2, and so on.
> Each librarian only handles requests for their room's
> books. To find a book, you first determine which room
> it is in, then ask that room's librarian.

**One insight:**
Sharding trades the simplicity of a single data store for
write scalability. The moment data is on multiple nodes,
any query that spans multiple shards requires coordination,
distributed joins, or scatter-gather across all shards.
The shard key choice is the most critical decision: the
wrong key creates hotspots; a good key distributes load evenly
and keeps related data co-located.

---

### 🔩 First Principles Explanation

**THE PARTITIONING STRATEGIES:**

**Range Partitioning:**
Data is partitioned by ranges of the shard key value.
Example: user IDs 1-1M on Shard 1, 1M-2M on Shard 2.
Pro: range queries are efficient (scan a single shard).
Con: hotspots if recent data is more frequently accessed
(e.g., all new users on the last shard).

```
┌────────────────────────────────────────────────────────┐
│  RANGE PARTITIONING by user_id:                        │
│                                                        │
│  Shard 1: user_id 1 - 1,000,000                       │
│  Shard 2: user_id 1,000,001 - 2,000,000               │
│  Shard 3: user_id 2,000,001 - 3,000,000               │
│                                                        │
│  Query: "Get user 1,500,050"                          │
│  → Route to Shard 2. Single shard query. Fast.        │
│                                                        │
│  Query: "Get all users ordered by signup date"         │
│  → All shards, merge results. Multi-shard. Slow.      │
└────────────────────────────────────────────────────────┘
```

**Hash Partitioning:**
A hash function is applied to the shard key. The hash
output determines the shard. Example: shard = hash(user_id)
% N. Pro: even distribution. Con: range queries hit all
shards (hash destroys order).

```
┌────────────────────────────────────────────────────────┐
│  HASH PARTITIONING:                                    │
│                                                        │
│  user_id=1001 → hash(1001) % 4 = 1 → Shard 1         │
│  user_id=1002 → hash(1002) % 4 = 2 → Shard 2         │
│  user_id=1003 → hash(1003) % 4 = 3 → Shard 3         │
│  user_id=1004 → hash(1004) % 4 = 0 → Shard 0         │
│                                                        │
│  Evenly distributed: each shard gets ~25% of data     │
│  Range query: ALL shards must be queried. Expensive.  │
└────────────────────────────────────────────────────────┘
```

**Directory-Based Partitioning:**
A lookup table maps each record (or record range) to a
specific shard. Maximum flexibility: any record can be
moved to any shard by updating the lookup table. Cost:
the lookup table itself must be highly available and fast.

**THE HOTSPOT PROBLEM:**
A poor shard key concentrates traffic on a small number of
shards.

```
BAD shard key: event_date for a time-series database
  All today's events → Shard with today's partition
  → One shard handles 100% of writes
  → Other shards are idle
  → No benefit from sharding

GOOD shard key: user_id (hash) for the same events
  Events spread across all shards by user
  → Each shard handles ~1/N of writes
  → Full benefit from sharding
```

The "celebrity problem" in social media: if shard key is
user_id and one shard has Beyonce (100M followers) whose
data is read by millions simultaneously, that shard is a
hotspot regardless of overall hash distribution. Mitigation:
further split hotspot shards; use application-level caching.

---

### 🧠 Mental Model / Analogy

> Sharding is like dividing a country's citizens across
> multiple government offices, each responsible for a
> geographic region. If you live in the North, you go to
> the Northern office. If you live in the South, you go
> to the Southern office. Each office handles all
> government services for their region. This distributes
> the load across offices. But if you need a record that
> involves people from both North and South (cross-shard
> join), the two offices must coordinate - which is
> slower and more complex.

Mapping:
- "Citizens" - data records
- "Government offices" - database shards
- "Geographic region" - shard key range
- "Cross-shard join" - multi-shard query requiring scatter-gather

**Where this analogy breaks down:** Government offices can
refer you to another office. Database shards cannot
automatically coordinate a query that spans multiple shards
- the application must explicitly route to all relevant shards
and merge the results.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Sharding splits your database across multiple servers. Instead
of all data on one server, you put 1/N of the data on each
of N servers. Each server handles its portion independently.
More servers = more storage and write capacity.

**Level 2 - How to use it (junior developer):**
Choose a shard key (the field used to determine which shard
a record goes to). Route every database request through a
shard router that computes which shard(s) to query. MongoDB,
Cassandra, DynamoDB, and Redis Cluster handle sharding
automatically with their own routing layers.

**Level 3 - How it works (mid-level engineer):**
The shard router maintains a mapping: for each shard key
range or hash bucket, which physical node is responsible.
When a query arrives, the router extracts the shard key
from the query, looks up the responsible shard, and routes
the query there. For cross-shard queries (no shard key in
the WHERE clause), the router fans out the query to all
shards and merges the results.

**Level 4 - Why it was designed this way (senior/staff):**
Consistent hashing (covered in DST-030) was introduced to
solve the rebalancing problem: with simple hash-mod-N, adding
or removing a shard requires remapping almost every record.
Consistent hashing arranges shards on a ring and only moves
data from/to the affected shard - approximately 1/N of
data moves when adding a new shard. This made dynamic
sharding practically viable.

**Level 5 - Mastery (distinguished engineer):**
The choice between sharding strategies has second-order
effects: hash partitioning loses data locality (related
records spread across shards), making joins across records
impossible within a single shard. Application-level
denormalization (copying data into each shard that needs it)
or co-location (ensuring related records hash to the same
shard using compound shard keys) is required. Google
Spanner solves this with "interleaved tables": child records
are physically co-located with parent records on the same
shard by storing them in key-order, combining range and
hash partitioning.

---

### ⚙️ Mechanism - How Sharding Works

**SHARD ROUTING FLOW:**

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  Client → Shard Router                                 │
│              │                                         │
│              ├─ Extract shard key from query           │
│              │  (e.g., user_id=12345)                  │
│              │                                         │
│              ├─ Compute shard: hash(12345) % 4 = 1     │
│              │                                         │
│              ├─ Lookup shard-to-node mapping:          │
│              │  Shard 1 → database-node-1.internal     │
│              │                                         │
│              └─ Forward query to node-1                │
│                                                        │
│  Result: query executed on exactly one node.           │
│  Scales: add more nodes → more shards → more capacity  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**REBALANCING WHEN ADDING A SHARD:**
```
Before: 4 shards. Hash key = user_id % 4

Shard 0: user_ids where id % 4 = 0
Shard 1: user_ids where id % 4 = 1
Shard 2: user_ids where id % 4 = 2
Shard 3: user_ids where id % 4 = 3

Add Shard 4. New hash key = user_id % 5

All existing data must be re-evaluated:
  Some of Shard 0's data now belongs to Shard 4
  Some of Shard 1's data now belongs to Shard 4
  Some of Shard 2's data now belongs to Shard 4
  Some of Shard 3's data now belongs to Shard 4

80% of all data must move to a different shard.
This is why consistent hashing (DST-030) was invented.
```

---

### 💻 Code Example

**Shard Key Selection (Wrong vs Right)**

```python
# BAD: Use timestamp as shard key for event data
class EventRepository:
    def store_event(self, event: Event) -> None:
        # Shard key = event date
        shard_id = hash(event.date) % NUM_SHARDS
        shard = self.shards[shard_id]
        shard.insert(event)

# Problem: All events today go to the same shard.
# That shard receives 100% of write traffic.
# Yesterday's shard is idle.
# Sharding provides zero benefit.
```

```python
# GOOD: Use user_id (or composite key) as shard key
class EventRepository:
    def store_event(self, event: Event) -> None:
        # Shard key = user_id: distributes by user
        shard_id = hash(event.user_id) % NUM_SHARDS
        shard = self.shards[shard_id]
        shard.insert(event)

    def get_user_events(
        self,
        user_id: str,
        start_date: datetime
    ) -> list[Event]:
        # Single-shard query: all user's events
        # are on the same shard
        shard_id = hash(user_id) % NUM_SHARDS
        shard = self.shards[shard_id]
        return shard.query(
            "SELECT * FROM events "
            "WHERE user_id=%s AND date>=%s",
            [user_id, start_date]
        )

    def get_events_for_date(
        self,
        date: datetime
    ) -> list[Event]:
        # Multi-shard (scatter-gather): no shard key in query
        results = []
        for shard in self.shards:
            results.extend(
                shard.query(
                    "SELECT * FROM events WHERE date=%s",
                    [date]
                )
            )
        return sorted(results, key=lambda e: e.timestamp)
```

**Cross-Shard Transaction Handling (Failure Example)**

```python
# FAILURE SCENARIO: Transfer between users on different shards
# user_1 is on Shard 0; user_2 is on Shard 3

def transfer_credits(
    from_user_id: str,
    to_user_id: str,
    amount: int
) -> None:
    shard_from = get_shard(from_user_id)  # Shard 0
    shard_to = get_shard(to_user_id)      # Shard 3

    # BAD: Two separate transactions, no atomicity
    shard_from.execute(
        "UPDATE users SET credits=credits-%s WHERE id=%s",
        [amount, from_user_id]
    )  # Succeeds

    # CRASH HERE: credits deducted but not added to recipient
    raise SystemError("unexpected failure")

    shard_to.execute(   # Never executed
        "UPDATE users SET credits=credits+%s WHERE id=%s",
        [amount, to_user_id]
    )

# GOOD: Use application-level 2PC or saga pattern
# for cross-shard transactions (see DST-047 Two-Phase Commit)
```

---

### ⚖️ Comparison Table

| Aspect | Replication | Sharding | Both |
|---|---|---|---|
| **Purpose** | Fault tolerance, read scaling | Write scaling, storage scaling | Full scalability |
| **Data per node** | Full dataset per replica | 1/N of dataset | 1/N replicated |
| **Write throughput** | Single leader ceiling | Scales with N | Scales with N |
| **Cross-node queries** | Any replica | Scatter-gather | Scatter-gather |
| **Complexity** | Medium | High | Very High |
| **Used by** | PostgreSQL, MySQL replicas | Cassandra, MongoDB, HBase | All at scale |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Sharding is just for big companies" | Any database that approaches its single-node storage or write limit needs sharding. That can happen at 100GB or 100TB depending on query patterns. |
| "Sharding is automatic in cloud databases" | Managed databases (RDS, Cloud SQL) are typically single-node. You need specific distributed databases (DynamoDB, Cassandra, Spanner) for automatic sharding. |
| "Sharding and partitioning are different things" | Sharding is horizontal partitioning distributed across multiple physical nodes. They are the same concept; "sharding" typically implies multiple physical machines while "partitioning" can be within one database. |
| "Any field can be a shard key" | The shard key determines data distribution and query routing. A poor shard key creates hotspots or scatter-gather on all queries. Shard key selection is the most important design decision. |

---

### 🚨 Failure Modes & Diagnosis

**Hotspot Shard Overload**

**Symptom:** One shard's CPU and I/O are at 100% while
other shards are at 10% utilization. Write latency for
users on the hotspot shard is high; other users are fine.

**Root Cause:** Shard key creates uneven distribution.
Common cause: shard key is a sequential ID (all new records
go to the last shard), or a celebrity user drives massive
traffic to their shard.

**Diagnosis:**
```bash
# MongoDB: Check chunk distribution
mongosh --eval "sh.status()" | grep -A 5 "chunks"
# Look for shards with many more chunks than others

# Check write throughput per shard:
mongosh --eval "db.serverStatus().opcounters" \
  --host shard0-primary
# Compare across all shards
```

**Fix:**
1. Add a random suffix to the shard key (salt) to spread
   a celebrity record across multiple shards.
2. Split the hotspot shard into smaller shards.
3. Cache read-heavy hotspot data above the shard layer.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Node` - The units across which shards are distributed
- `Fault Tolerance` - Motivation for sharding alongside
  redundancy
- `Replication` - Complementary mechanism (shards are
  typically replicated)

**Builds On This (learn these next):**
- `Consistent Hashing` - The algorithm that makes shard
  rebalancing practical
- `Rebalancing` - How shards are redistributed when
  nodes are added or removed

**Alternatives / Comparisons:**
- `Vertical Scaling` - The alternative to sharding: buying
  bigger hardware. Simpler but has a hard ceiling and is
  expensive at scale.

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Split dataset across multiple nodes      │
│              │ by shard key; each node owns its subset  │
├──────────────┼──────────────────────────────────────────┤
│ SOLVES       │ Write throughput limits, storage limits  │
│              │ that replication cannot address          │
├──────────────┼──────────────────────────────────────────┤
│ KEY DECISION │ Shard key selection: determines          │
│              │ distribution uniformity and query routing│
├──────────────┼──────────────────────────────────────────┤
│ STRATEGIES   │ Range, Hash, Directory-based             │
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFFS   │ Gained: write scale, storage scale       │
│              │ Lost: cross-shard ACID, join efficiency  │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Sequential shard key (timestamp, auto-ID)│
│              │ → all writes hit latest shard            │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Replication copies data for resilience; │
│              │  sharding splits data for scale."        │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Consistent Hashing → Rebalancing         │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
The shard key decision in a database is the same class of
decision as the partition key in Kafka, the primary key in
DynamoDB, or the hash key in a distributed cache. In every
case, the key determines which "partition" of the system
handles the data, and a poor choice creates hotspots.
The pattern: choose a partition key that (1) distributes
data uniformly, (2) keeps related data co-located to minimize
cross-partition operations, and (3) does not create hotspots
for predictably popular data.

---

### 💡 The Surprising Truth

Instagram stored photos on a sharded PostgreSQL cluster
for years with 12 shards, each handling a physical range
of user IDs. When a shard's disk filled up, they could not
easily add a 13th shard due to the rebalancing cost. Their
solution: they pre-split each logical shard (range of user
IDs) across 4096 logical shards but mapped all 4096 to just
12 physical shards. When a physical shard fills up, they
move some logical shards (already self-contained) to a new
physical server. Only the data in those logical shards moves,
not all data. This pattern - many logical shards mapped to
few physical shards - is the best practice for managing
growth without full rebalancing. It is now codified in
PostgreSQL's declarative partitioning feature.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. [SELECT] Given a dataset (social media posts, financial
   transactions, product catalog), select and justify a
   shard key that avoids hotspots and supports the most
   common query patterns.
2. [IDENTIFY] Given a slow query that touches all shards,
   determine whether it can be converted to a single-shard
   query by changing the shard key or schema.
3. [DEBUG] A sharded database has uneven distribution.
   Using chunk count and throughput metrics, identify the
   hotspot shard and propose a mitigation strategy.
4. [DESIGN] Design a sharding scheme for a ride-sharing
   app's trip history: 1 billion trips, 50 million users,
   primary query is "trips by user", secondary query is
   "trips in a city on a date."
5. [EXPLAIN] Explain to a product manager why moving to
   a sharded database means you can no longer easily run
   "report queries" across all user data.
