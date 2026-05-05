---
layout: default
title: "Redis Data Structures"
parent: "NoSQL & Distributed Databases"
nav_order: 462
permalink: /nosql/redis-data-structures/
number: "0462"
category: NoSQL & Distributed Databases
difficulty: ★★☆
depends_on: Key-Value Store, Caching, Data Structures & Algorithms
used_by: Redis Persistence, Caching, Session Management
related: Key-Value Store, Redis Persistence, Caching
tags:
  - nosql
  - redis
  - data-structures
  - intermediate
---

# 462 — Redis Data Structures

⚡ TL;DR — Redis is not "just a cache" — it's a data structure server with native support for strings, lists, hashes, sets, sorted sets, streams, bitmaps, and HyperLogLog; each structure enables specific use cases (leaderboards, rate limiting, pub/sub, stream processing) that would require complex application code without Redis.

| #462            | Category: NoSQL & Distributed Databases                | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | Key-Value Store, Caching, Data Structures & Algorithms |                 |
| **Used by:**    | Redis Persistence, Caching, Session Management         |                 |
| **Related:**    | Key-Value Store, Redis Persistence, Caching            |                 |

---

### 🔥 The Problem This Solves

**SIMPLE KEY-VALUE ISN'T ENOUGH:**
A cache that does `GET key` / `SET key value` handles simple scenarios. But real applications need: "add to a list (but limit to last 100 items)", "increment a counter atomically", "store user session fields individually", "compute a real-time leaderboard sorted by score", "track distinct visitors without storing all user IDs". Each of these requires application-level logic + multiple round trips if your cache only supports GET/SET.

**REDIS DATA STRUCTURES:**
Redis provides server-side data structures with atomic operations: push to a list, add to a sorted set with a score, increment a hash field, track cardinality with HyperLogLog. These operations run on the Redis server (in memory, single-threaded model), atomically, with O(1) or O(log N) complexity. Applications describe WHAT to do; Redis does it server-side — no race conditions, no round trips for computation.

---

### 📘 Textbook Definition

Redis supports multiple **native data structure types**, each with specialized commands. **String**: the fundamental type; stores text, serialized objects, or numbers (supports `INCR` for atomic integer increment). **List**: ordered sequence with O(1) push/pop at both ends (LPUSH/RPOP); used for queues and recent activity logs. **Hash**: map of field-value pairs within a key (HSET/HGET/HINCRBY); used for objects/records. **Set**: unordered collection of unique strings (SADD/SMEMBERS/SINTER/SUNION); used for unique tags, relationships. **Sorted Set (ZSet)**: set where each member has a floating-point score (ZADD/ZRANGE/ZRANGEBYSCORE/ZRANK); used for leaderboards, time-ordered queues. **Stream** (Redis 5.0+): append-only log with consumer groups (XADD/XREAD/XREADGROUP); used for message queues, event logs. **Bitmap**: bit operations on string values (SETBIT/GETBIT/BITCOUNT); used for efficient boolean flag storage per user ID. **HyperLogLog**: probabilistic cardinality estimation with fixed memory (PFADD/PFCOUNT, ~0.81% error, 12KB memory regardless of cardinality); used for unique visitor counting.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Redis is a data structure server: instead of storing bytes and computing in your application, you store the right structure (sorted set, stream, bitmap) and Redis provides the right atomic operations — server-side, fast, safe from race conditions.

**One analogy:**

> A Swiss Army knife vs. a plain kitchen knife. A plain knife (simple GET/SET cache) can cut food, but requires application logic for everything else. A Swiss Army knife (Redis) has a blade, screwdriver, scissors, corkscrew — each tool optimized for its task. Using a sorted set for leaderboards (the scissors) is better than building leaderboard logic on top of plain string values (cutting with the knife handle).

- "Plain knife" → GET/SET key-value store (Memcached)
- "Swiss Army knife" → Redis (multiple purpose-built data structures)
- "Scissors" → sorted set (leaderboards, scored ranking)
- "Screwdriver" → HyperLogLog (cardinality estimation)
- "Using the right tool" → choosing the right Redis data structure for the use case

**One insight:**
Redis's single-threaded execution model is not a bug — it's what makes all Redis operations implicitly atomic. `INCR counter` is atomic because Redis processes commands one at a time. No need for distributed locks to increment a counter. This turns Redis into a "distributed atomic operation server" — a role it plays far more efficiently than any application-level mutex.

---

### 🔩 First Principles Explanation

**STRING (the foundation):**

```redis
SET user:1001:token "eyJhbGciOiJI..." EX 3600   # with 1-hour TTL
GET user:1001:token                               # returns token or nil
INCR page:homepage:views                          # atomic increment (integer as string)
GETEX user:1001:token EX 3600                     # get + reset TTL (sliding expiry)
SETNX lock:payment:1001 "worker-3" EX 30          # set only if not exists (distributed lock basis)

# Atomic increment: no race condition
# Two requests simultaneously: INCR page:homepage:views
# Redis single-threaded → one command runs, then the other
# Both correctly get 1 then 2; NOT both getting 1 (race condition in naive DB logic)
```

**LIST (queue / recent activity):**

```redis
LPUSH activity:user:1001 "login"      # push to head
LPUSH activity:user:1001 "view:p123"
LPUSH activity:user:1001 "add_to_cart:p456"
LTRIM activity:user:1001 0 99         # keep only last 100 items
LRANGE activity:user:1001 0 9         # get 10 most recent

# Use as queue (producer/consumer)
LPUSH email:queue '{"to":"alice@..","subject":"Welcome"}'  # producer
BRPOP email:queue 5                                         # consumer: blocking pop, 5s timeout

# LRANGE is O(N) - only fast for small ranges from head/tail
# For large lists, use Stream instead
```

**HASH (object storage):**

```redis
HSET user:1001 name "Alice" email "alice@example.com" age 30
HGET user:1001 name          # → "Alice"
HMGET user:1001 name email   # → ["Alice", "alice@example.com"]
HINCRBY user:1001 login_count 1   # atomically increment a field
HGETALL user:1001             # → all fields and values

# Better than: SET user:1001 '{"name":"Alice","email":"..."}' (serialized JSON)
# Why: individual field updates without deserialization/reserialization
#      HINCRBY is atomic; JSON approach requires GET → decode → increment → encode → SET
```

**SET (unique membership):**

```redis
SADD tags:post:42 "redis" "database" "caching"
SMEMBERS tags:post:42              # → {"redis", "database", "caching"}
SISMEMBER tags:post:42 "redis"     # → 1 (true)
SADD tags:post:99 "redis" "nosql"
SINTER tags:post:42 tags:post:99   # → {"redis"} (common tags)
SUNION tags:post:42 tags:post:99   # → {"redis","database","caching","nosql"}
SCARD tags:post:42                 # → 3 (cardinality)

# Online friends: store connected user IDs in a Set
# SISMEMBER user:42:online "user-99" → is user-99 online?
# SMEMBERS user:42:friends → all friend IDs (use SCAN for large sets)
```

**SORTED SET (leaderboard, rate limiting):**

```redis
# Leaderboard: game scores
ZADD leaderboard 98500 "player:alice"
ZADD leaderboard 102000 "player:bob"
ZADD leaderboard 87200 "player:charlie"
ZRANGE leaderboard 0 9 REV WITHSCORES  # top 10, descending
# → ["player:bob", 102000, "player:alice", 98500, "player:charlie", 87200]
ZRANK leaderboard "player:alice" REV    # → 1 (0-indexed rank)
ZINCRBY leaderboard 500 "player:alice"  # atomic score increment

# Rate limiting: sliding window (sorted set of timestamps)
function isRateLimited(userId, limit=100, windowSec=60):
  now = current_timestamp_ms()
  key = f"rate:{userId}"
  pipe.zremrangebyscore(key, 0, now - windowSec*1000)  # remove old
  pipe.zadd(key, {now: now})                           # add current
  pipe.expire(key, windowSec)
  pipe.zcard(key)                                      # count in window
  results = pipe.execute()
  return results[-1] > limit
```

**STREAM (event log / message queue):**

```redis
# Producer: append to stream
XADD events:orders * order_id 42 user_id 1001 total 99.99
# * = auto-generated ID (timestamp-sequence, e.g., 1700000000000-0)
# Returns: "1700000000000-0"

# Consumer group: multiple consumers process events
XGROUP CREATE events:orders order-processors $ MKSTREAM

# Consumer 1 reads from its group (exclusive ownership)
XREADGROUP GROUP order-processors worker-1 COUNT 5 BLOCK 1000 STREAMS events:orders >
# > = read only new messages not delivered to this group

# Acknowledge processed messages
XACK events:orders order-processors 1700000000000-0

# Pending messages (unacked, for crash recovery)
XPENDING events:orders order-processors - + 10
```

**BITMAP:**

```redis
# Daily active users: bit per user ID (bit[userId] = 1 if active)
SETBIT daily:active:2024-01-15 1001 1   # user 1001 was active today
SETBIT daily:active:2024-01-15 2005 1   # user 2005 was active today
GETBIT daily:active:2024-01-15 1001     # → 1 (was active)
BITCOUNT daily:active:2024-01-15        # → 2 (total active users)

# 10 million users = 10MB bitmap (vs. Set with user IDs = hundreds of MB)
# BITOP AND/OR/XOR: intersection of active users across multiple days
BITOP AND wau daily:active:2024-01-15 daily:active:2024-01-14 daily:active:2024-01-13
# → 7-day active users bitmap (1 bit per user)
```

**HYPERLOGLOG:**

```redis
# Count distinct visitors without storing all IDs
PFADD visitors:page:homepage "user-1001" "user-2005" "user-3000"
PFADD visitors:page:homepage "user-1001"  # duplicate - not counted again
PFCOUNT visitors:page:homepage             # → 3 (±0.81% error)

# Multiple pages:
PFMERGE total_visitors visitors:page:homepage visitors:page:checkout
PFCOUNT total_visitors  # approximate distinct visitors across pages

# Memory: fixed ~12KB per key regardless of cardinality
# vs. Set: 10 million unique IDs ≈ 400MB
```

---

### 🧪 Thought Experiment

**REAL-TIME LEADERBOARD: SORTED SET VS. APPLICATION CODE**

Game server: 1 million concurrent players; score updates every 30 seconds per player; leaderboard page shows top 100 players with ranks; any player can view their rank.

**NAIVE APPROACH (application-level):**
Store scores in PostgreSQL. On leaderboard view: `SELECT user_id, score FROM scores ORDER BY score DESC LIMIT 100`. Under load: 1 million rows; full sort needed; no index helps for arbitrary rank lookup. Caching the result: top 100 is stale immediately (1 million score updates/minute). Paginating leaderboard: requires offset scans (O(offset) performance).

**REDIS SORTED SET APPROACH:**
Every score update: `ZINCRBY game:leaderboard [delta] [user_id]` — O(log N), instant. Top 100: `ZRANGE game:leaderboard 0 99 REV WITHSCORES` — O(log N + K) where K=100, instant. Player's rank: `ZRANK game:leaderboard user_id REV` — O(log N), instant. Paginate: `ZRANGE leaderboard 0 99 REV` ... `ZRANGE leaderboard 100 199 REV` — each O(log N + K).

With 1 million players: ZINCRBY for 1 million updates/minute → ~17,000 ops/sec. Redis handles ~100,000 ops/sec on a single instance. No scaling needed. This is a problem that Redis solves inherently well; PostgreSQL would require significant engineering to handle at this scale.

---

### 🧠 Mental Model / Analogy

> Redis data structures are like specialized containers in a warehouse. A generic cardboard box (String) holds anything. A conveyor belt with two ends (List) is efficient for queues. A labeled filing cabinet with named drawers (Hash) lets you access individual fields without pulling out the whole box. A set of uniquely-labeled sticky notes (Set) tracks membership with no duplicates. A scoreboard with sorted rankings (Sorted Set) provides instant rank lookups. A FIFO event log with multiple reading stations (Stream) distributes work. The warehouse manager (Redis single-threaded model) ensures only one worker accesses a container at a time — no collisions.

- "Generic cardboard box" → String (universal, serialized JSON)
- "Conveyor belt" → List (LPUSH/RPOP queue)
- "Filing cabinet with named drawers" → Hash (HSET/HGET fields)
- "Sorted scoreboard" → Sorted Set (ZADD/ZRANGE/ZRANK)
- "Event log with stations" → Stream (XADD/XREADGROUP)
- "One worker at a time" → Redis single-threaded atomicity

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Redis has 8 data structure types. Each is used for different problems: Strings for caching and counters. Lists for recent activity and simple queues. Hashes for user profile fields. Sets for unique tags and friend lists. Sorted Sets for leaderboards and rate limiting. Streams for message queues. Bitmaps for active user tracking. HyperLogLog for approximate unique counts.

**Level 2:** Choose by access pattern: leaderboard with rank = Sorted Set. Sliding-window rate limiter = Sorted Set (timestamp as score). User session with multiple fields = Hash (not serialized String). Task queue = List (BRPOP blocks efficiently) or Stream (for consumer groups). Daily active users across 10M users = Bitmap. Approximate unique visitors = HyperLogLog. Always pipeline multiple commands: `pipeline.zadd(); pipeline.expire(); pipeline.execute()` — batch round trips.

**Level 3:** Redis Sorted Set internals: skip list (O(log N) rank operations) + hash map (O(1) score lookup by member). Small ZSets use ziplist encoding (compact, up to 128 members by default). OBJECT ENCODING to check. ZADD NX (add only if not exists), XX (update only if exists), GT/LT (update only if new score > / < old score) — useful for idempotent updates from multiple workers. ZPOPMIN/ZPOPMAX (pop highest/lowest score) for priority queues. Redis Stream consumer groups: each consumer group has independent offset into the stream; multiple groups can read the same stream independently (fan-out). PEL (Pending Entry List): messages delivered but not ACKed; XCLAIM to reassign stuck messages; XAUTOCLAIM (Redis 6.2) to automatically reclaim stale pending messages.

**Level 4:** Redis's data structures are fast because they operate entirely in RAM with a single-threaded execution model — no locking, no disk I/O in the hot path. The design is reminiscent of Erlang actors or disruptor queues: serial execution eliminates synchronization overhead. The hidden cost: Redis's in-memory model means data size is bounded by RAM. The HyperLogLog is notable as a probabilistic data structure with fixed 12KB memory regardless of cardinality — a rare case of a data structure that deliberately sacrifices accuracy for bounded space. Redis 7.0 introduced Redis Functions (Lua-based, replicated, persistent scripts) as a successor to Redis Scripting for complex multi-command atomic operations. Redis Stack extended Redis with modules: RedisJSON (native JSON), RediSearch (full-text search), RedisTimeSeries (native time-series), RedisBloom (probabilistic structures), RedisGraph (property graph). These blur the line between Redis as cache and Redis as primary database.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ REDIS DATA STRUCTURE INTERNALS                       │
├──────────────────────────────────────────────────────┤
│                                                      │
│ All structures stored in RAM in a global hash table  │
│ (key → pointer to data structure)                    │
│                                                      │
│ String: Simple Dynamic String (SDS)                  │
│   small ints: shared integer pool (0-9999) → no alloc│
│                                                      │
│ List: quicklist (linked list of packed nodes)        │
│   small lists: listpack (contiguous, cache-friendly) │
│   large lists: doubly linked list of listpacks       │
│                                                      │
│ Hash: listpack (≤128 fields) → hashtable (>128)      │
│   [REDIS DATA STRUCTURES ← YOU ARE HERE]             │
│                                                      │
│ Set: intset (all integers) → listpack (small)        │
│      → hashtable (large/non-integer)                 │
│                                                      │
│ Sorted Set: listpack (≤128 members)                  │
│   → skip list + hashtable (>128)                     │
│   skip list: O(log N) rank / range ops               │
│   hashtable: O(1) score lookup by member name        │
│                                                      │
│ All commands: single-threaded → implicit atomicity   │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**RATE LIMITER + LEADERBOARD (sorted sets):**

```
API request arrives: POST /game/score from user:1001
→ [Rate Limiter] SORTED SET: rate:user:1001
   now = timestamp_ms()
   ZREMRANGEBYSCORE (remove old entries > 60s ago)
   ZADD rate:user:1001 now now
   EXPIRE rate:user:1001 60
   count = ZCARD rate:user:1001
   if count > 100: return 429 Too Many Requests
→ [Process Score] Parse score from request body
→ [Leaderboard] SORTED SET: game:leaderboard
   ZINCRBY game:leaderboard [delta] "user:1001"
   rank = ZRANK game:leaderboard "user:1001" REV
→ [Response] {newScore: X, rank: rank}
→ [Redis DATA STRUCTURES ← YOU ARE HERE: sorted sets for both]
All Redis operations: < 1ms, atomic, no application-level locking
```

---

### ⚖️ Comparison Table

| Type            | Commands                    | Use Cases                     | Complexity                          |
| --------------- | --------------------------- | ----------------------------- | ----------------------------------- |
| **String**      | GET/SET/INCR/GETEX          | Cache, counters, sessions     | O(1)                                |
| **List**        | LPUSH/RPOP/BRPOP/LRANGE     | Queue, activity log           | O(1) push/pop, O(N) range           |
| **Hash**        | HSET/HGET/HINCRBY/HGETALL   | User profiles, config objects | O(1) per field                      |
| **Set**         | SADD/SMEMBERS/SINTER/SUNION | Tags, unique membership       | O(1) add/check, O(N) enumerate      |
| **Sorted Set**  | ZADD/ZRANGE/ZRANK/ZINCRBY   | Leaderboards, rate limiting   | O(log N) add/rank, O(log N+K) range |
| **Stream**      | XADD/XREADGROUP/XACK        | Message queues, event logs    | O(1) append, O(N) range             |
| **Bitmap**      | SETBIT/GETBIT/BITCOUNT      | Active user flags             | O(1) per bit, O(N) count            |
| **HyperLogLog** | PFADD/PFCOUNT/PFMERGE       | Unique visitor counting       | O(1) add/count                      |

---

### ⚠️ Common Misconceptions

| Misconception                       | Reality                                                                                                                                                                                        |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Redis is just a cache"             | Redis is a data structure server. Its persistence, Stream type, and consumer groups make it suitable as a primary database, message broker, and stream processor                               |
| "KEYS \* is fine for development"   | KEYS \* is O(N) and blocks Redis (single-threaded). Even in dev, use SCAN 0 COUNT 100 instead — same result, non-blocking, paginated                                                           |
| "SMEMBERS on large sets is fine"    | SMEMBERS is O(N) and returns all members. For large sets: use SSCAN (paginated). For cardinality only: SCARD. For counting arbitrary groups: HyperLogLog                                       |
| "Redis transactions guarantee ACID" | Redis MULTI/EXEC provides isolation (commands execute atomically without interleaving) but no rollback on error (errors are per-command, not transactional). It's serialization, not full ACID |

---

### 🚨 Failure Modes & Diagnosis

**1. Hot Key — O(N) Command on Large Structure**

**Symptom:** Redis latency spikes for specific keys. `redis-cli --hotkeys` shows one key handling disproportionate traffic. Operations on that key take milliseconds instead of microseconds.

**Root Cause:** SMEMBERS/HGETALL/LRANGE on a collection that has grown to millions of members. Or: many concurrent ZADD on the same leaderboard key.

**Fix:** Replace with SCAN/SSCAN/HSCAN (paginated, O(1) per page). For LRANGE: switch to Stream with consumer groups (better semantics for large lists). For ZSets with high write contention: split into multiple sub-leaderboards, merge at read time.

---

### 🔗 Related Keywords

**Prerequisites:** Key-Value Store, Caching, Data Structures & Algorithms
**Builds On This:** Redis Persistence, Caching
**Related:** Key-Value Store, Redis Persistence

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STRING    │ Cache, counters (INCR), sessions with TTL    │
│ LIST      │ Queue (BRPOP), recent activity (LTRIM)       │
│ HASH      │ User profile object (per-field ops)          │
│ SET       │ Tags, unique membership, intersection        │
│ ZSET      │ Leaderboards, rate limiting (score=time)     │
│ STREAM    │ Message queue with consumer groups + replay  │
│ BITMAP    │ Daily active users (1 bit per user ID)       │
│ HLL       │ Unique visitors (~0.81% error, fixed 12KB)  │
│ AVOID     │ KEYS *, SMEMBERS (large), HGETALL (large)   │
│ ONE-LINER │ "Choose the structure that makes your        │
│           │  query O(1) or O(log N) server-side"         │
│ NEXT      │ Redis Persistence → Cassandra Data Modeling  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C — Design Question) Design a real-time collaboration cursor system: 50,000 concurrent users editing shared documents; each user's cursor position (document ID, line, column) must be broadcast to all other users editing the same document with < 100ms latency; cursor positions expire when a user disconnects. Design using Redis data structures. Which structures? What TTLs? How do you detect disconnections?

**Q2.** (TYPE F — Comparison Depth) Compare Redis Sorted Set vs. Redis Stream for implementing a background job queue where: jobs have priorities (high/medium/low), workers process high-priority jobs first, failed jobs must be retried up to 3 times, you need visibility into pending job count per priority. Which structure better fits each requirement? What is the trade-off?
