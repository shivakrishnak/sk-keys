---
layout: default
title: "Memcached vs Redis"
parent: "Caching"
nav_order: 494
permalink: /caching/memcached-vs-redis/
number: "0494"
category: Caching
difficulty: ★★☆
depends_on: Distributed Cache, Redis Cluster
used_by: System Design, Caching
related: Redis Cluster, Local Cache vs Distributed Cache, Distributed Cache
tags:
  - caching
  - memcached
  - redis
  - comparison
  - deep-dive
---

# 494 — Memcached vs Redis

⚡ TL;DR — Memcached is a **pure, simple key-value cache** (string values only, no persistence, no pub/sub, multithreaded); Redis is a **multi-purpose data structure server** (strings, lists, sets, sorted sets, hashes, streams, pub/sub, Lua scripting, persistence, clustering); choose Memcached for pure caching with the highest raw throughput on simple key-value workloads; choose Redis for everything else.

| #494            | Category: Caching                                                  | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Cache, Redis Cluster                                   |                 |
| **Used by:**    | System Design, Caching                                             |                 |
| **Related:**    | Redis Cluster, Local Cache vs Distributed Cache, Distributed Cache |                 |

---

### 🔥 The Problem This Solves

**CHOOSING THE RIGHT CACHING TOOL:**
Engineers often default to Redis without considering Memcached's advantages for pure caching workloads, or vice versa. Understanding the tradeoffs prevents over-engineering (using Redis for pure key-value caching when Memcached would be simpler and faster) and under-engineering (using Memcached when Redis's data structures or persistence are needed).

---

### 📘 Textbook Definition

**Memcached**: A high-performance, distributed memory object caching system designed specifically for caching. Single data type: string (arbitrary bytes). Multi-threaded: can utilize all CPU cores for maximum throughput. No persistence: data is lost on restart. No replication: no built-in failover. Clients handle sharding (consistent hashing). No pub/sub, no scripting, no transactions. Simple protocol (GET/SET/DELETE/INCR). Maximum value size: 1MB. **Strengths**: simplest possible cache, highest raw throughput for SET/GET on simple values.

**Redis**: An in-memory data structure server. Data types: string, list, hash, set, sorted set, bitmap, HyperLogLog, geospatial, stream. Single-threaded command processing (I/O is multi-threaded from Redis 6+). Persistence: RDB snapshots + AOF (append-only file) for durability. Replication: built-in async replication. Redis Cluster: native horizontal scaling. Pub/Sub, Lua scripting, transactions (MULTI/EXEC), atomic operations. Modules: RedisSearch, RedisJSON, RedisBloom (Bloom filters), RedisTimeSeries. **Strengths**: multi-purpose, persistent option, rich operations, ecosystem.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Memcached = pure cache, fastest for simple GET/SET, no frills. Redis = Swiss army knife for caching + data structures + pub/sub + persistence.

**One analogy:**

> Memcached is a whiteboard — fast to write on, fast to read, can be erased, nothing survives a power outage, and it only stores text. Redis is a filing cabinet with a whiteboard: you can put plain text on the whiteboard (strings), but also folders with labeled sections (hashes), ordered stacks (lists), unique collections (sets), ranked scoreboards (sorted sets), and the contents survive a power outage (persistence).

**One insight:**
The performance gap between Memcached and Redis has narrowed significantly. Redis 6.0+ uses multi-threaded I/O (though command processing is still single-threaded). In practice, for most workloads, Redis's throughput is sufficient and the additional features justify the choice. The main remaining advantage of Memcached is **multi-threaded command processing** — for extremely high-throughput, CPU-bound GET/SET workloads on a single large server, Memcached can use all cores while Redis uses one. For distributed workloads across multiple Redis instances, this advantage disappears.

---

### 🔩 First Principles Explanation

**DATA TYPES — THE DECISIVE DIFFERENCE:**

```
Memcached:
  SET key value (max 1MB)
  GET key
  DELETE key
  INCR/DECR (atomic counter on string)
  Nothing else.

Redis:
  STRING: SET/GET/INCR/APPEND/STRLEN
  LIST:   LPUSH/RPUSH/LRANGE/LLEN (deque, queue, stack)
  HASH:   HSET/HGET/HGETALL (object fields, like a mini document)
  SET:    SADD/SMEMBERS/SINTERSTORE (unique values, set operations)
  SORTED SET: ZADD/ZRANGE/ZRANGEBYSCORE (leaderboards, ranges)
  STREAM: XADD/XREAD (event stream, like Kafka lightweight)
  BITMAP: SETBIT/BITCOUNT (compact boolean flags per user/day)
  GEO:    GEOADD/GEODIST (geospatial proximity)
  HyperLogLog: PFADD/PFCOUNT (approximate cardinality counting)

Use cases requiring Redis data types (Memcached can't do these):
  - Session: HASH (multiple fields per session) + TTL
  - Leaderboard: SORTED SET (ZADD user score; ZRANK user; ZRANGE 0 9 WITHSCORES)
  - Rate limiting: INCR + EXPIRE (counter per user per minute)
  - Pub/Sub: PUBLISH/SUBSCRIBE (real-time notifications)
  - Queue: LPUSH/BRPOP (blocking pop — background job queue)
  - Bloom filter: RedisBloom module (BLOOM.ADD / BLOOM.EXISTS)
  - Distributed lock: SET NX EX (mutex)
```

**PERSISTENCE — DURABILITY:**

```
Memcached:
  No persistence. Server restart = complete data loss.
  For CACHING only: this is acceptable (cache miss → DB reload).
  For anything durable: not suitable.

Redis persistence options:
  1. RDB (Redis Database Dump):
     - Point-in-time snapshot saved to disk every N seconds (configurable)
     - Fast startup, compact file, not suitable for zero-data-loss
     - Config: save 900 1 (if 1 key changed in 900s, save)

  2. AOF (Append-Only File):
     - Every write command appended to log file
     - appendfsync: always (sync every write, safe, slowest)
                    everysec (sync every second, up to 1s data loss, default)
                    no (OS flushes when it wants, fastest, risky)
     - AOF rewrite: periodically compacted to remove redundant commands

  3. RDB + AOF (hybrid, recommended for durability):
     - AOF for durability, RDB for fast startup

  For CACHING: persistence is optional (data loss = cache miss, acceptable).
  For RATE LIMITING, SESSIONS, QUEUES: AOF with everysec provides acceptable durability.
  For DURABLE DATASTORE: AOF with always (but significant performance cost).

  Amazon ElastiCache (Redis): persistence is opt-in.
                  (Memcached): no persistence at all.
```

**HORIZONTAL SCALING:**

```
Memcached clustering:
  No built-in cluster. Clients handle sharding.
  Client library (Xmemcached, SpyMemcached): consistent hashing across nodes.
  Failure: no automatic failover. Failed node = cache miss for its keys.
  Adding nodes: consistent hashing minimizes remapping (K/N keys remap).

Redis Cluster:
  Built-in. 16,384 hash slots. Automatic failover.
  Requires minimum 3 primaries.
  Client: Lettuce/Jedis with cluster awareness.
  Multi-key operations: need hash tags.

Redis Sentinel (HA without sharding):
  Single primary, multiple replicas, Sentinel processes monitor health.
  Auto-failover: Sentinel promotes replica on primary failure.
  No sharding: single node capacity limit.
  Good for: HA on a single Redis dataset (not too large).

AWS managed:
  ElastiCache for Memcached: auto-discovery, no cross-AZ replication.
  ElastiCache for Redis: Redis Cluster mode, multi-AZ, read replicas.
  → For new deployments: ElastiCache Redis is usually chosen.
```

**SPRING BOOT CONFIGURATION — BOTH:**

```java
// Redis (Spring Boot auto-configuration):
// application.yml:
// spring.data.redis.host: localhost
// spring.data.redis.port: 6379
// → Auto-configures RedisTemplate and CacheManager (if spring-boot-starter-data-redis)

// @Cacheable with Redis:
@Cacheable("products")
public Product getProduct(String id) { return db.findById(id).orElseThrow(); }
// → Uses configured CacheManager (RedisCacheManager by default)

// Memcached (no Spring Boot auto-configuration — manual setup):
@Bean
public MemcachedClient memcachedClient() throws Exception {
    return new XMemcachedClientBuilder(
        AddrUtil.getAddresses("localhost:11211")
    ).build();
}

@Service
public class ProductServiceMemcached {
    @Autowired private MemcachedClient memcached;

    public Product getProduct(String id) throws Exception {
        Product cached = (Product) memcached.get("product:" + id);
        if (cached != null) return cached;

        Product product = db.findById(id).orElseThrow();
        memcached.set("product:" + id, 900, product);  // 900s TTL
        return product;
    }
}
// Memcached: no @Cacheable integration without custom adapters.
// → Spring Cache (JSR-107) has no official Memcached implementation.
// → One reason Redis is preferred in Spring Boot applications.
```

---

### 🧪 Thought Experiment

**WHEN DOES MEMCACHED'S MULTITHREADING MATTER?**

Scenario: a single cache node, 48-core server, receiving 5 million GET/SET/second for small string values (~100 bytes each).

Redis (single command thread): all 5M operations serialized through one thread. ~600K-1M ops/second for single-node Redis (theoretical). Even with multithreaded I/O in Redis 6+, command processing bottleneck.

Memcached (multithreaded): can leverage all 48 cores. 48 threads × ~100K ops/second per thread = ~4.8M ops/second theoretical. Memcached scales linearly with core count for pure GET/SET.

**Practical verdict:** At 5M ops/second on a single node, Memcached wins. But: at that scale, use 5 Redis nodes (Redis Cluster) each handling 1M ops/second. Total: 5M ops/second with Redis Cluster — same throughput, plus failover, richer operations, Spring integration. Memcached's multithreading advantage is real but rarely decisive in distributed architectures.

---

### 🧠 Mental Model / Analogy

> Memcached = a specialized power tool (drill). It does one thing (drills holes = caches key-value data) faster and more simply than any multi-tool. Redis = a multi-tool (Leatherman). It drills holes (string caching), cuts wire (pub/sub), opens bottles (Lua scripting), measures distances (geospatial). For most jobs: the multi-tool is more convenient. For a dedicated task requiring maximum speed with no other needs: the specialized drill is faster.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Memcached: pure cache, strings only, no persistence, multi-threaded. Redis: rich data types, optional persistence, pub/sub, clustering built-in. Choose Redis for modern applications — richer features, better ecosystem.

**Level 2:** Memcached wins: pure GET/SET throughput on single node (multi-core CPU); memory efficiency for simple string values (less overhead than Redis). Redis wins: data structures (hashes, sets, sorted sets); persistence (sessions, rate limits); Spring @Cacheable integration; pub/sub; Lua scripting; distributed lock; horizontal scaling (Redis Cluster).

**Level 3:** Memory efficiency: Redis has per-key overhead (~60-70 bytes vs. Memcached's ~50 bytes). For millions of tiny cached values (< 100 bytes), Memcached is 15-20% more memory-efficient. For typical application objects (user profiles, product data — 1KB-100KB), this difference is negligible. Redis also supports memory optimization: `hash-max-listpack-entries` (store small hashes as listpack, not hashtable) — can reduce memory usage 6-10× for small hashes (e.g., storing user session fields as Redis hash instead of JSON string).

**Level 4:** The historical context: Memcached was created in 2003 as a pure caching solution. Redis was created in 2009 with data structure richness as a primary design goal. By 2015, Redis had largely superseded Memcached for new applications. Today, Memcached is maintained but not actively enhanced. Redis has a vibrant ecosystem (RedisLabs/Redis Inc., Redis Modules, Redis Stack — JSON, Search, Time Series, Bloom). In 2024, the major cloud providers (AWS ElastiCache, Azure Cache for Redis, GCP Memorystore) all promote Redis as the primary managed cache. Memcached is available but increasingly less recommended. For greenfield projects in 2024+: Redis is the default. For legacy Memcached systems: migration to Redis is worthwhile for operational simplicity (one tool for caching + session + pub/sub + rate limiting).

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ MEMCACHED vs REDIS: ARCHITECTURE                     │
├──────────────────────────────────────────────────────┤
│                                                      │
│ MEMCACHED:                                           │
│  Client → [consistent hashing] → Node N             │
│  Node: multi-threaded, slab allocator, LRU eviction  │
│  SET key val → stored in slab class for val size    │
│  GET key → returned directly (no structure to parse) │
│  [MEMCACHED ← YOU ARE HERE: pure k-v, no structure]  │
│  No persistence. No pub/sub. No scripting.           │
│                                                      │
│ REDIS:                                               │
│  Client → [Lettuce, direct routing] → Node N        │
│  Node: single command thread + I/O threads (v6+)    │
│  SET user:42 serialized_json → STRING type          │
│  HSET user:42 name Alice email a@b.com → HASH type  │
│  ZADD leaderboard 9999 user:42 → SORTED SET          │
│  PUBLISH notifications "message" → PUB/SUB           │
│  Persistence: RDB/AOF to disk (optional)             │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
LEADERBOARD USE CASE:
Redis:
  User scores a game: POST /games/42/score {user:77, score:9999}
  → ZADD leaderboard:game:42 9999 user:77
  Get top 10: GET /games/42/leaderboard
  → ZREVRANGE leaderboard:game:42 0 9 WITHSCORES
  → [{user:77, 9999}, {user:23, 9850}, ...]
  → O(log N) insert + O(K log N) range read

Memcached:
  Can't. Memcached stores strings only.
  To use Memcached for leaderboard:
  → Get all scores from DB (sorted by score, LIMIT 10)
  → Serialize to JSON: "[{user:77, score:9999}, ...]"
  → Memcached SET leaderboard:game:42 {serialized JSON}
  → TTL-based invalidation (no atomic score update)
  → On any score change: must SET entire new JSON leaderboard string
  → Stale between SET operations; no atomic partial update

Redis is the only reasonable choice for leaderboards.
Same for: pub/sub, rate limiting, distributed locks, sessions with fields.
```

---

### ⚖️ Comparison Table

| Dimension          | Memcached                  | Redis                                                 |
| ------------------ | -------------------------- | ----------------------------------------------------- |
| Data types         | String only (bytes)        | String, List, Hash, Set, Sorted Set, Stream, Geo, HLL |
| Persistence        | None (volatile)            | RDB, AOF (optional)                                   |
| Replication        | None (client-side)         | Built-in async replication                            |
| Clustering         | Client-side (ketama)       | Redis Cluster (built-in)                              |
| Pub/Sub            | No                         | Yes (PUBLISH/SUBSCRIBE)                               |
| Scripting          | No                         | Lua (EVAL)                                            |
| Threading          | Multi-threaded             | Single cmd thread + multi I/O (v6+)                   |
| Max value size     | 1MB                        | 512MB (string)                                        |
| Spring integration | No auto-config             | Full auto-config + @Cacheable                         |
| Use case           | Pure caching, simplest     | Multi-purpose: cache + data store                     |
| Choose when        | Maximum GET/SET throughput | Any feature beyond simple caching                     |

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                                                                                                                            |
| ------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Redis is slower than Memcached"                       | For typical workloads: comparable. Redis's single command thread can process ~600K-1M simple ops/second. For CPU-bound workloads on many cores: Memcached scales better. For distributed workloads: Redis Cluster matches Memcached throughput     |
| "Memcached is more reliable (simpler = fewer bugs)"    | Simplicity doesn't equate to reliability. Redis has far more testing, monitoring tooling, and cloud management support. Memcached has no failover — a node failure causes immediate cache miss for its keys, potentially causing a thundering herd |
| "Use Redis for caching, Memcached for high throughput" | In practice, Redis is used for both. The throughput advantage of Memcached is meaningful only in specific edge cases (single-node, CPU-bound, pure GET/SET)                                                                                        |

---

### 🚨 Failure Modes & Diagnosis

**1. Memcached Node Failure — No Failover**

**Symptom:** One Memcached node goes offline. 33% of cache keys are now on a failed node. Cache miss rate spikes to 33%. Database load increases by 33%. Thundering herd follows.

**Root Cause:** Memcached has no built-in replication or failover. Client consistent hashing routes to next node — but that node doesn't have the data. Cache miss.

**Prevention:**

```java
// Option 1: Accept the miss; design DB to handle it
// (short-term thundering herd, resolves as cache repopulates)

// Option 2: Migrate to Redis Cluster (automatic failover in ~30s)
// After failover: slot's new primary has replica data; cache hit rate maintained

// Option 3: Application-level replica for Memcached (rare)
// Write to 2 Memcached nodes; read from primary; on failure, read from replica
// Very rare in practice — just migrate to Redis
```

---

### 🔗 Related Keywords

**Prerequisites:** Distributed Cache, Redis Cluster
**Builds On This:** System Design, Caching
**Related:** Redis Cluster, Local Cache vs Distributed Cache, Distributed Cache

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ MEMCACHED    │ Pure k-v cache; string only; no persistence│
│ REDIS        │ Data structures + cache + persistence      │
│ MEMCACHED ✓  │ Max raw GET/SET throughput; simplest       │
│ REDIS ✓      │ Everything else: sessions, leaderboards,   │
│              │ pub/sub, rate limits, distributed lock     │
│ THREADING    │ Memcached: multi-thread; Redis: single cmd  │
│ PERSISTENCE  │ Memcached: none; Redis: RDB+AOF optional   │
│ CLUSTER      │ Memcached: client-side; Redis: built-in    │
│ SPRING       │ Memcached: no auto-config; Redis: full     │
│ 2024 CHOICE  │ Redis (ecosystem, managed cloud support)   │
│ ONE-LINER    │ "Memcached = fastest pure cache;           │
│              │  Redis = cache + data platform"            │
│ NEXT EXPLORE │ Local Cache vs Distributed Cache           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C — Design Question) You're migrating a legacy Memcached cluster (500GB, 10 nodes) to Redis. The system uses Memcached for: (a) HTML fragment caching (string values, 10KB avg), (b) session data (string, 2KB avg), (c) product catalog (string, 1KB avg). Design a migration plan that maintains availability during migration, identifies which data types could benefit from Redis-native structures, and defines rollback criteria.

**Q2.** (TYPE B — Architecture Review) A startup is building a real-time multiplayer game. Requirements: (a) leaderboard (top 100 players), (b) player session (active game state, 10KB), (c) pub/sub for game events (player joined, score changed), (d) rate limiting (max 10 actions/second/player). Evaluate: can Memcached handle any of these? Which require Redis? What Redis data structures map to each requirement?
