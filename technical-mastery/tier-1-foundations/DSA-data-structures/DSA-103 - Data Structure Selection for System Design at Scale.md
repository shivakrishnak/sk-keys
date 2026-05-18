---
id: DSA-103
title: Data Structure Selection for System Design at Scale
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-012, DSA-013, DSA-036, DSA-083
used_by: DSA-107, DSA-110
related: DSA-072, DSA-073, DSA-104
tags:
  - system-design
  - selection
  - scale
  - decision-framework
  - trade-offs
  - architecture
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 103
permalink: /technical-mastery/dsa/data-structure-selection/
---

## TL;DR

Choosing the wrong data structure for a distributed
system is a multi-year architectural mistake. This
entry provides the decision framework: match data
structure to access pattern, consistency requirement,
and scale tier.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-103 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | system design, selection, scale, decision framework |
| **Prerequisites** | DSA-012, DSA-013, DSA-036, DSA-083 |

---

### The Problem This Solves

System design interviews ask "how would you design
Twitter's timeline?" or "design a URL shortener at
1B requests/day." The answer is not a single data
structure - it's matching the right structure to
each access pattern. This entry is the decision map.

---

### The Selection Decision Tree

```
What is the primary operation?

Exact key lookup (O(1)):
  → HashMap/HashSet (in-process)
  → Redis Hash/Set (distributed)
  → DynamoDB (global, persistent)

Range queries or sorted iteration:
  → TreeMap (in-process, small dataset)
  → B+ Tree index (database, large dataset)
  → Redis Sorted Set (distributed, real-time leaderboard)

Existence check with size constraint:
  → Bloom Filter (probabilistic, space-efficient)
  → HashSet (exact, small dataset)
  → HyperLogLog (approximate count only)

Priority or scheduling:
  → PriorityQueue/Heap (in-process)
  → Redis Sorted Set (distributed priority queue)
  → Kafka (durable message queue with ordering)

Graph traversal:
  → Adjacency List + BFS/DFS (in-process)
  → Graph databases (Neo4j) for complex traversals
  → Distributed: sharded adjacency list + batch processing

Prefix search / autocomplete:
  → Trie (in-process)
  → Elasticsearch (distributed full-text)
  → Redis + prefix scan (distributed, simple)

Sliding window / time-series:
  → Deque (in-process)
  → Redis ZSET with score=timestamp (distributed)
  → TimescaleDB / InfluxDB (persistent time-series)
```

---

### Scale Tiers and Structure Mapping

**Tier 1 - Single JVM (< 1M entries, single process):**

```java
// User session store (< 100K active sessions)
Map<String, UserSession> sessions =
    new ConcurrentHashMap<>(100_000);

// Product catalog (< 500K products, read-heavy)
Map<String, Product> catalog =
    Collections.unmodifiableMap(
        new HashMap<>((int)(500_000 / 0.75) + 1)
    );

// Active order priorities
PriorityQueue<Order> orderQueue = new PriorityQueue<>(
    Comparator.comparing(Order::getPriority).reversed()
);

// Feature flags (always-present, lookup-only)
Set<String> enabledFeatures = Set.of("feature-a", "feature-b");
// Java 9+ Set.of: immutable, optimized for small sets
```

**Tier 2 - Redis Layer (1M-1B items, distributed):**

```
User sessions (Redis Hash):
  HSET session:<id> userId <u> lastActive <t>
  TTL session:<id> 3600 (auto-expire)

Rate limiting (Redis ZSET):
  ZADD rate:<userId> <timestamp> <requestId>
  ZREMRANGEBYSCORE rate:<userId> 0 <now-60000>
  ZCARD rate:<userId>  → count in last 60s

Leaderboard (Redis ZSET):
  ZADD leaderboard <score> <userId>
  ZREVRANGE leaderboard 0 9  → top 10
  ZREVRANK leaderboard <userId>  → user's rank

Distributed Bloom Filter (Redisson):
  BloomFilter<String> filter = ...
  filter.tryAdd(url)  → deduplicate crawled URLs
```

**Tier 3 - Database Layer (1B+ items, durable):**

```
User profiles (DynamoDB / Cassandra):
  Partition key: userId (hash distribution)
  Access: O(1) for single-user lookup
  Range queries: not supported (use secondary index)

Transaction history (PostgreSQL with B+ Tree index):
  Index on (userId, timestamp)
  Range query: WHERE userId=? AND timestamp BETWEEN ? AND ?
  O(log n + k) with index

Event sourcing (Kafka):
  Append-only log (array-like structure)
  Partition key: entityId (consistent routing)
  Retention: time-based or size-based
```

---

### System Design Scenario: Design a URL Shortener

```
Requirements:
  100M URLs stored, 10K shortening/sec, 100K reads/sec
  Short code lookup: O(1)
  URL deduplication (same URL = same short code)

Chosen structures:

1. Short code → Long URL mapping:
   - DynamoDB table (partition key: shortCode)
   - O(1) lookup globally
   - Why not Redis: 100M entries = ~20GB RAM; DynamoDB
     stores on disk, Redis stores in memory

2. URL deduplication:
   - Bloom Filter (100M URLs, 1% FPR = ~1GB memory)
   - Pre-check before DB write
   - If Bloom says "absent": definitely new URL, create
   - If Bloom says "present": check DB (1% false positive)

3. Counter for short code generation:
   - Redis INCR (atomic increment)
   - Base62 encode the counter = short code
   - Not UUID (too long), not random (collision risk)

4. Rate limiting (prevent abuse):
   - Redis ZSET sliding window per IP
   - 100 requests per minute limit

Selection summary:
  O(1) lookup: DynamoDB
  Deduplication: Bloom Filter
  ID generation: Redis atomic counter
  Rate limiting: Redis ZSET
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Always use HashMap for O(1) lookups" | HashMap is in-process only. At distributed scale, you need Redis, DynamoDB, or Cassandra. The "O(1)" in HashMap does not apply across network calls |
| "More complex data structure = better design" | The best design uses the simplest structure that satisfies the requirements. A HashMap + Redis can outperform a complex distributed graph database for simple lookup use cases |

---

### Quick Reference Card

| Access Pattern | In-Process | Distributed | Persistent |
|---------------|-----------|------------|-----------|
| Exact lookup | HashMap | Redis Hash | DynamoDB |
| Sorted/Range | TreeMap | Redis ZSET | PostgreSQL B-Tree |
| Prefix search | Trie | Elasticsearch | Elasticsearch |
| Existence check | Bloom Filter | Bloom Filter (Redis) | Bloom Filter (disk) |
| Priority queue | PriorityQueue | Redis ZSET | Kafka |
| Event stream | ArrayDeque | Kafka | Kafka (durable) |
| Time-series | Deque | Redis ZSET | TimescaleDB |

---

### Mastery Checklist

- [ ] Can map any system design requirement to the right structure
- [ ] Knows the boundary where in-process structures become insufficient
- [ ] Uses Bloom filters for pre-screening in distributed systems
- [ ] Explains Redis ZSET as the Swiss Army knife of distributed DSA

---

### Interview Deep-Dive

**Q1 (Hard):** Design the data layer for a Twitter-like
feed system at 500M users, 50M active/day, 100K tweets/sec.

> Access patterns:
> 1. Write tweet: author pushes to all followers' feeds
> 2. Read home timeline: last 100 tweets from followed accounts
> 3. Read user timeline: last 100 tweets by a specific user
> 
> Data structures:
> 
> Tweet storage (write):
> - DynamoDB: (tweetId → tweet data)
> - Partition key: tweetId (UUID)
> - O(1) write, O(1) read by tweet ID
> 
> Home timeline (fan-out on write):
> - Redis List per user: LPUSH timeline:<userId> <tweetId>
> - LTRIM timeline:<userId> 0 999 (keep last 1000)
> - O(1) read: LRANGE timeline:<userId> 0 99
> - Problem: celebrity with 100M followers = 100M Redis writes
>   per tweet. Solution: fan-out on read for celebrities
>   (hybrid approach)
> 
> User timeline:
> - Cassandra: (userId, timestamp) → tweetId
> - Partition key: userId, clustering key: timestamp DESC
> - Efficient range scan: latest 100 tweets per user
> 
> Hotspot mitigation (celebrity problem):
> - Maintain a celebrity list (users with >100K followers)
> - For celebrities: don't fan-out on write; merge their
>   recent tweets at read time (fan-out on read)
> - For regular users: fan-out on write (Redis lists)
