---
layout: default
title: "ElastiCache"
parent: "NoSQL & Distributed Databases"
nav_order: 2168
permalink: /nosql/elasticache/
number: "2168"
category: NoSQL & Distributed Databases
difficulty: ★★★
depends_on: Caching, Redis, AWS
used_by: Caching, Cloud — AWS, Spring Core
related: Redis, Memcached, Caching Strategies
tags:
  - database
  - caching
  - aws
  - cloud
  - advanced
---

# 2168 — ElastiCache

⚡ TL;DR — ElastiCache is AWS's managed in-memory caching service for Redis and Memcached; cluster mode, replication, eviction policies, and connection pooling are the four levers that determine production behavior.

| Relation | Keywords |
|---|---|
| Depends on | Caching, Redis, AWS |
| Used by | Caching, Cloud — AWS, Spring Core |
| Related | Redis, Memcached, Caching Strategies |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Every database read for frequently accessed data (user sessions, product catalog, rate limit counters) hits the primary database. At 10 000 requests/second, the database processes 10 000 identical queries for the same product catalog that changes once per hour. Database CPU is 80% utilized serving reads that could have been served from memory. Adding database replicas helps briefly, then costs compound.

**THE BREAKING POINT:** During a product launch, traffic spikes to 50 000 requests/second. The RDS cluster falls over. The caching layer exists as a local in-process cache per application server — 20 servers each holding a private copy of the cache, each with different staleness levels, each consuming 2 GB of application heap. A restart of any server coldstarts its cache, causing a thundering herd of database queries. The lack of a shared, durable external cache creates a single failure mode that expands with scale.

**THE INVENTION MOMENT:** ElastiCache provides a fully managed, clustered in-memory cache that is external to application servers, shared across all application instances, durable (AOF/RDB persistence in Redis), highly available (Multi-AZ replica promotion), and operable without managing OS patches, failover, or shard rebalancing. It removes the operational complexity of running Redis or Memcached clusters so engineering teams can focus on application behavior.

---

### 📘 Textbook Definition

**Amazon ElastiCache** is a fully managed in-memory data store and caching service for Redis and Memcached on AWS. For **Redis**, ElastiCache provides: **Cluster Mode Disabled** (single shard with optional read replicas) and **Cluster Mode Enabled** (up to 500 shards for horizontal scaling); Multi-AZ with automatic failover; persistence (RDB snapshots and AOF); pub/sub, Lua scripting, and sorted sets. For **Memcached**, ElastiCache provides multi-threaded horizontal scaling across nodes but no persistence, replication, or data structures beyond key-value strings. Both options are deployed into a VPC, secured via security groups and TLS, and integrated with IAM and Secrets Manager for credential management.

---

### ⏱️ Understand It in 30 Seconds

**One line:** ElastiCache is managed Redis or Memcached on AWS — you configure shard count, replica count, and eviction policy; AWS handles failover, patching, and backups.

> Think of ElastiCache like a managed loading dock at a warehouse. Your workers (application servers) no longer carry stock directly from the deep storage room (database) — instead, there's a staffed loading dock (ElastiCache) that pre-stages the 20% of SKUs that are 80% of the orders. When the dock is full, the oldest stock is moved out (eviction policy). If the dock manager goes home sick (node failure), the shift manager takes over (replica promotion).

**One insight:** The most dangerous ElastiCache configuration mistake is not choosing Redis vs Memcached — it is misconfiguring the eviction policy. `noeviction` on a cache full of non-expiring keys causes write failures under memory pressure; `allkeys-lru` silently evicts important data that was expected to persist.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. All ElastiCache data is stored in RAM (plus optional AOF/RDB persistence on disk for Redis). RAM capacity is the primary cost driver and the primary operational constraint.
2. A Redis **Cluster Mode Enabled** setup shards keys across multiple primaries using consistent hashing of the key slot space (0–16 383 slots). Each primary owns a slice of the slot space.
3. In **Cluster Mode Disabled**, a single primary holds all data; read replicas serve reads but cannot be written to; primary failure triggers replica promotion (typically 30–60 seconds for automatic failover).
4. ElastiCache for Redis is a single-threaded command executor (for data operations) — a single slow command (e.g., `KEYS *`, `SMEMBERS` on a large set) blocks all other clients for its duration.
5. TCP connection establishment to Redis is not free — each new connection consumes memory on the Redis server (~20 KB per connection). Connection pooling is required in production.

**DERIVED DESIGN:**

- Use Cluster Mode Enabled when data exceeds single-node RAM capacity or when write throughput requires horizontal scaling.
- Use Cluster Mode Disabled when data fits in one node and read scaling is the priority (add replicas for read throughput).
- Set `maxmemory-policy: volatile-lru` for caches where some keys have TTLs and must survive eviction pressure. Use `allkeys-lru` for pure caches where all data is replaceable.
- Always use `pipelining` or `multi-exec` for batched operations; never loop `HSET` inside application code.

**THE TRADE-OFFS:**

**Gain:** Microsecond latency (sub-millisecond `GET`/`SET`); eliminates database read load for hot data; shared external cache survives application server restarts; AWS handles failover, backups, and patches.

**Cost:** RAM is expensive (r6g.xlarge = 13.07 GB RAM at ~$0.23/hour); Redis single-threaded model means a slow scan command blocks all clients; Cluster Mode Enabled adds complexity — multi-key operations (MGET, MSET, Lua scripts, transactions) across multiple slots require hash tags `{tag}` to co-locate keys on the same shard; ElastiCache is not directly accessible from outside the VPC without a bastion or VPC peering.

---

### 🧪 Thought Experiment

**SETUP:** An API serves product data from RDS PostgreSQL. Product catalog has 50 000 products. Each product read takes 5 ms from RDS. The API handles 20 000 requests/second. 80% of requests hit the top 1 000 products.

**WHAT HAPPENS WITHOUT ELASTICACHE:**
20 000 requests/second × 5 ms each = 100 000 concurrent database operations needed. RDS max_connections = 1 000. Connection pool at 500 connections provides 500 / 0.005s = 100 000 ops/second theoretical throughput — barely enough. Any query slowdown causes cascading connection exhaustion. A deployment restart causes all 20 application servers to simultaneously re-query the database (thundering herd). RDS CPU: 90%.

**WHAT HAPPENS WITH ELASTICACHE:**
Top 1 000 products are cached with a 5-minute TTL. 80% of 20 000 requests (16 000/second) are served from ElastiCache at 0.1 ms — 50× faster than RDS and consuming zero database connections. RDS serves only the remaining 4 000 requests/second for cache misses and less-popular products. RDS CPU: 18%. Application restart thundering herd: all 20 servers miss cache simultaneously, but 50× fewer queries hit RDS since only 1 000 products need to be loaded.

**THE INSIGHT:** The cache hit ratio is the most important operational metric. At 80% hit rate, the database sees 20% of original traffic. At 95% hit rate, the database sees 5% — a 20× reduction. Improving cache hit rate from 80% to 95% is worth more than doubling the database cluster size.

---

### 🧠 Mental Model / Analogy

> ElastiCache is like a fast-food restaurant's warming shelf. The full kitchen (RDS database) can produce any item but takes time. The warming shelf (ElastiCache) holds the 20 most popular items ready instantly. When a customer orders a popular item, the warming shelf delivers it in seconds. When the item is gone (cache miss), the kitchen makes it fresh and restocks the shelf. If the warming shelf catches fire (node failure), the backup shelf (replica) takes over immediately.

- **Warming shelf** = ElastiCache primary node (RAM)
- **Kitchen** = RDS/database (source of truth)
- **Most popular items** = hot keys cached with TTL
- **Item expiry and restock** = TTL expiration and cache-aside pattern
- **Backup shelf** = Redis replica (read-only copy for failover)
- **Shelf capacity limit** = `maxmemory` setting; eviction policy determines what to remove when full

Where this analogy breaks down: a warming shelf serves one restaurant; ElastiCache is shared by all application servers simultaneously and can serve millions of requests per second — concurrency at a scale that no physical shelf analogy captures.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
ElastiCache is a super-fast storage system that keeps your most-used data in memory instead of making your database look it up every time. AWS manages the servers, backups, and automatic recovery so you don't have to.

**Level 2 — How to use it (junior developer):**
In your application, before querying the database, check ElastiCache first (`GET key`). If the value is there (cache hit), return it immediately. If not (cache miss), query the database, store the result in ElastiCache with a TTL (`SET key value EX 300`), and return it. This pattern is called cache-aside. Use `redis-cli` to inspect keys and `INFO stats` to monitor hit rate.

**Level 3 — How it works (mid-level engineer):**
In Cluster Mode Enabled, keys are distributed across shards using CRC16(key) mod 16383 to compute a hash slot. Each shard (primary + replicas) owns a contiguous range of slots. Commands that operate on multiple keys in different slots fail unless keys share the same hash tag `{tag}` — this forces them to the same slot. Failover: ElastiCache monitors primaries via AWS-internal health checks; when a primary fails, a replica is promoted within 30–60 seconds (configurable). During failover, writes to the failing primary are unavailable — `TCP connection refused` or `READONLY` errors. Applications must implement retry logic with exponential backoff.

**Level 4 — Why it was designed this way (senior/staff):**
ElastiCache's architectural choices closely mirror the upstream Redis design decisions. Redis's single-threaded event loop is not a limitation — it is a feature: absence of mutex contention means command latency is deterministic and predictable (sub-millisecond at P99 for simple commands). Multi-threading was added in Redis 6 for I/O only (network read/write), not for command execution. The Cluster Mode Disabled vs Enabled distinction reflects two fundamentally different scaling strategies: vertical (bigger node) vs horizontal (more shards). Horizontal sharding (Cluster Mode Enabled) requires the application to be shard-aware, which adds complexity but enables linear scaling of both capacity and throughput. AWS manages the operational complexity of slot migration during resharding, but the application must handle multi-key operations with hash tags — a cost that must be planned at schema design time, not retrofitted.

---

### ⚙️ How It Works (Mechanism)

**Cluster Mode Enabled — Sharding:**

```
16384 key slots partitioned across shards:

  Shard 0 (Primary + 2 Replicas):
    slots 0–5460

  Shard 1 (Primary + 2 Replicas):
    slots 5461–10922

  Shard 2 (Primary + 2 Replicas):
    slots 10923–16383

Key routing:
  slot = CRC16("user:123") % 16384 = 7823
  → routes to Shard 1 primary
```

**Eviction Policies (maxmemory-policy):**

| Policy | Evicts From | Use Case |
|---|---|---|
| `noeviction` | Nothing; writes fail | Persistent data store |
| `allkeys-lru` | All keys, LRU | Pure cache, all data replaceable |
| `volatile-lru` | Keys with TTL, LRU | Mixed persistent+cache data |
| `allkeys-lfu` | All keys, LFU | Skewed access (hot keys) |
| `volatile-ttl` | Keys with TTL, soonest expiry | Prefer expiring soon |
| `allkeys-random` | Random key | Uniform access patterns |

**Multi-AZ Failover Timeline:**
```
t=0s:  Primary node becomes unreachable
t=5s:  ElastiCache health check detects failure
t=30s: Replica promoted to primary
t=60s: DNS endpoint updated (clients reconnect)
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (Cache-Aside Pattern):**

```
HTTP request: GET /products/123
          │
          ▼
App: cache.get("product:123")
  HIT → return cached JSON (0.1 ms)  ← YOU ARE HERE
  MISS ↓
          │
          ▼
App: db.query("SELECT * FROM products
  WHERE id = 123")  → 5 ms
          │
          ▼
App: cache.set("product:123", json,
  ex=300)  → write to ElastiCache
          │
          ▼
Return JSON response
  Next request for product 123: cache hit
```

**FAILURE PATH:**
- Cache stampede: cache expires → all app servers simultaneously query the database → database overloaded → write new cache entry → brief storm
- Redis primary failure → 30–60s failover → `READONLY` errors from old connections to now-replica
- `maxmemory` reached with `noeviction` → `OOM command not allowed when used memory > maxmemory` → all writes rejected
- Hot key: 100 000 requests/second for one key → single Redis shard CPU maxed → all requests queue

**WHAT CHANGES AT SCALE:**
- Connection count: 1 000 application server pods × 50 connections/pod = 50 000 connections → Redis memory: 50 000 × 20 KB = 1 GB RAM for connections alone → connection pooling is mandatory
- Cluster resharding: adding a shard triggers live slot migration (keyspace moves from existing shards to new shard) — brief latency spikes during migration
- Large values: `SET key value` where value is 1 MB → network transfer dominates; compress values before caching at this scale

---

### 💻 Code Example

**BAD — no connection pooling, blocking commands in production:**
```python
import redis

# BAD: new connection per request
def get_product(product_id):
    r = redis.Redis(host='elasticache-host', port=6379)
    data = r.get(f"product:{product_id}")
    r.close()  # connection created and destroyed each time
    return data

# BAD: KEYS command blocks all other clients
def list_all_cached_products():
    r = redis.Redis(host='elasticache-host')
    return r.keys("product:*")  # NEVER in production
```

**GOOD — connection pool, proper cache-aside, scan instead of KEYS:**
```python
import redis
import json
from redis.connection import ConnectionPool

# GOOD: shared connection pool at module level
_pool = ConnectionPool(
    host=os.environ['ELASTICACHE_HOST'],
    port=6379,
    max_connections=50,
    decode_responses=True,
    socket_connect_timeout=0.5,
    socket_timeout=0.5,
    ssl=True   # TLS in transit
)

def get_redis():
    return redis.Redis(connection_pool=_pool)

PRODUCT_TTL_SECONDS = 300

def get_product_cached(product_id: str):
    r = get_redis()
    cache_key = f"product:{product_id}"

    # Cache-aside: check cache first
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)  # cache hit

    # Cache miss: query database
    product = db.query_product(product_id)
    if product:
        r.setex(
            cache_key,
            PRODUCT_TTL_SECONDS,
            json.dumps(product)
        )
    return product

def invalidate_product(product_id: str):
    r = get_redis()
    r.delete(f"product:{product_id}")

# GOOD: use SCAN instead of KEYS for iteration
def list_cached_product_ids():
    r = get_redis()
    product_ids = []
    cursor = 0
    while True:
        cursor, keys = r.scan(
            cursor, match="product:*", count=100
        )
        product_ids.extend(keys)
        if cursor == 0:
            break
    return product_ids
```

**Cluster Mode Enabled — hash tags for multi-key operations:**
```python
# BAD: MGET across different slots fails in cluster mode
keys = ["user:1:profile", "session:1:data"]
r.mget(keys)  # ClusterCrossSlotError if keys on diff shards

# GOOD: use hash tags to co-locate related keys
user_id = "12345"
keys = [
    f"{{user:{user_id}}}:profile",  # hash tag: user:12345
    f"{{user:{user_id}}}:session",  # same hash tag → same shard
    f"{{user:{user_id}}}:cart"
]
r.mget(keys)  # works: all keys on same shard
```

---

### ⚖️ Comparison Table

| Feature | ElastiCache Redis | ElastiCache Memcached | DynamoDB DAX | In-process Cache |
|---|---|---|---|---|
| Data structures | Rich (hashes, sets, sorted sets, streams) | String only | N/A (DynamoDB-specific) | Language-native |
| Persistence | RDB + AOF optional | None | None | None (process memory) |
| Replication | Multi-AZ replicas | None | Multi-AZ | None |
| Cluster sharding | Cluster Mode Enabled (500 shards) | Multi-node (auto) | Managed by DAX | None |
| Multi-key ops | Yes (hash tags for cluster) | Yes (native) | Yes (batch) | Yes |
| Pub/Sub | Yes | No | No | No |
| Failover | Automatic (30–60s) | None (no replicas) | Automatic | None |
| Best for | Session, rate limiting, leaderboards, pub/sub | Simple distributed cache | DynamoDB read scaling only | Single-server apps |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "`noeviction` is the safest eviction policy" | `noeviction` causes write failures under memory pressure — the cache stops accepting new data; safer is `volatile-lru` or `allkeys-lru` |
| "ElastiCache Cluster Mode Enabled is always better" | Cluster Mode Enabled adds complexity (hash tags, no cross-slot multi-key ops, cross-slot scripting limitations); only use it when single-node capacity or write throughput is insufficient |
| "Redis is multi-threaded in ElastiCache" | Redis command execution is single-threaded; only network I/O is multi-threaded (Redis 6+). A single slow command (SMEMBERS on 100k elements) blocks all other clients |
| "TTL-based expiry is instant" | Redis TTL expiry uses lazy + periodic eviction; an expired key occupies memory until accessed (lazy) or until the background eviction thread processes it (periodic, every 100ms) |
| "ElastiCache is accessible from the internet for testing" | ElastiCache runs inside a VPC and has no public endpoint; access requires being within the VPC, VPC peering, or an SSH tunnel through a bastion host |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Cache Stampede (Thundering Herd)**

**Symptom:** Every N minutes (equal to TTL), database CPU spikes to 100% for 2–3 seconds; latency spikes affect all users simultaneously; pattern repeats on exactly the TTL boundary.
**Root Cause:** A popular cache key expires; all application servers simultaneously experience a cache miss and simultaneously query the database for the same data.
**Diagnostic:**
```bash
# Monitor cache hit rate
redis-cli -h $ELASTICACHE_ENDPOINT \
  INFO stats | grep keyspace_hits
# Watch the ratio: keyspace_hits / (keyspace_hits + keyspace_misses)
# A periodic dip to 0% on popular keys = stampede

# Check for synchronized expiry
redis-cli -h $ELASTICACHE_ENDPOINT \
  DEBUG SLEEP 0  # test connectivity
redis-cli TTL "product:hot_product_id"
```
**Fix:** Use probabilistic early rehydration — refresh the cache before the TTL expires (when TTL drops below a threshold, one request re-fetches from the database while others still get the cached value). Alternatively, use a distributed lock (Redis `SET key NX EX`) to ensure only one request populates the cache on a miss.
**Prevention:** Add a randomized TTL jitter (e.g., TTL = 300 ± 30 seconds) so all keys for the same resource do not expire simultaneously.

---

**Failure Mode 2: Hot Key — Single Shard CPU Maxed**

**Symptom:** One ElastiCache shard node at 100% CPU while others are idle; `redis-cli --hotkeys` shows one key receiving 80% of all traffic; requests queue on that shard.
**Root Cause:** A single cache key (e.g., a viral product, a global rate limit counter, or a shared leaderboard) receives disproportionate read or write traffic that exceeds one shard's capacity.
**Diagnostic:**
```bash
# Identify hot keys (Redis 4.0+)
redis-cli -h $ELASTICACHE_ENDPOINT \
  --hotkeys --scan

# Check per-node CPU in CloudWatch
aws cloudwatch get-metric-statistics \
  --namespace AWS/ElastiCache \
  --metric-name EngineCPUUtilization \
  --dimensions Name=CacheClusterId,Value=my-cluster-0001
```
**Fix:** For read hot keys, use **local in-process caching** (L1 cache in the application) to absorb repeated reads before they reach ElastiCache. For write hot keys (e.g., counters), shard the counter across N keys (`counter:{key}:1` through `counter:{key}:N`), increment a random shard, and sum all shards for reads.
**Prevention:** Design keys so that no single key can receive traffic proportional to total user base. Use `{hashTag}` to co-locate related keys, not hot keys.

---

**Failure Mode 3: Connection Exhaustion**

**Symptom:** Application errors: `redis.exceptions.ConnectionError: Error 111 connecting`; ElastiCache metric `CurrConnections` near `maxclients` (default 65 000); new connection attempts are rejected.
**Root Cause:** Application creates a new Redis connection per request (no connection pool); at high concurrency, connection count reaches the Redis `maxclients` limit.
**Diagnostic:**
```bash
# Check current connection count
redis-cli -h $ELASTICACHE_ENDPOINT \
  INFO clients | grep connected_clients

# Compare against maxclients
redis-cli -h $ELASTICACHE_ENDPOINT \
  CONFIG GET maxclients

# CloudWatch metric: CurrConnections trending near limit
```
**Fix:** Implement a connection pool in the application (e.g., `redis-py` `ConnectionPool`, `Jedis` `JedisPool`, Spring Data Redis `LettuceConnectionFactory` with pool config). Set pool `max_connections` to 50–100 per application pod.
**Prevention:** Configure `maxclients` in the ElastiCache parameter group at 2× the expected peak connection count. Alert when `CurrConnections` exceeds 70% of `maxclients`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Caching — the general discipline of storing computed results for reuse; cache-aside, write-through, and invalidation strategies
- Redis — the underlying in-memory data store that ElastiCache for Redis wraps
- AWS — the cloud platform infrastructure (VPC, IAM, CloudWatch) that ElastiCache is integrated with

**Builds On This (learn these next):**
- Caching — ElastiCache implements caching strategies; understanding cache invalidation, TTL design, and hit rate optimization requires this foundation
- Cloud — AWS — ElastiCache integrates with VPC security groups, IAM authentication, Secrets Manager, and CloudWatch metrics
- Spring Core — Spring Data Redis uses ElastiCache as the backing store for `@Cacheable` annotations in Spring Boot applications

**Alternatives / Comparisons:**
- Redis — the open-source version; self-managed alternative to ElastiCache
- Memcached — the simpler alternative; available in ElastiCache but lacks persistence and rich data structures
- Caching Strategies — cache-aside, write-through, write-behind, and read-through patterns applicable to ElastiCache

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ WHAT IT IS    AWS managed Redis or Memcached;   │
│               in-memory cache with HA           │
│ PROBLEM       Database read overload at scale;  │
│               operational burden of Redis mgmt  │
│ KEY INSIGHT   Hit rate is the primary KPI;      │
│               eviction policy determines safety │
│ USE WHEN      Session storage, rate limiting,   │
│               hot read caching, pub/sub on AWS  │
│ AVOID WHEN    Data must be durable (use RDS);   │
│               cross-VPC access needed           │
│ TRADE-OFF     Memory cost + eviction risk vs    │
│               database load reduction           │
│ ONE-LINER     Connection pool + volatile-lru +  │
│               TTL jitter = production-safe cache│
│ NEXT EXPLORE  DynamoDB Data Modeling Patterns   │
└─────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(C — Design Trade-off)** Your application uses ElastiCache Cluster Mode Enabled with 3 shards. A new feature requires an atomic Lua script that reads and writes 5 keys belonging to the same user. The 5 keys are currently distributed across different shards. What are the exact two options for making this Lua script work in cluster mode, and what is the operational cost of each option?

2. **(B — Scale)** At 500 000 requests/second, your ElastiCache cluster serves 95% of reads from cache. A viral product causes the single cache key `product:viral` to receive 400 000 reads/second — all on the same shard. The shard node handles 200 000 ops/second maximum. Describe the exact technical mechanism of the failure, the local L1 cache mitigation approach, and why this pattern does not require a Cluster Mode Enabled change.

3. **(A — System Interaction)** ElastiCache Multi-AZ is enabled with automatic failover. During an AZ outage, the primary in `us-east-1a` fails and a replica in `us-east-1b` is promoted. Application servers are using the primary endpoint DNS name. Describe the sequence of events: how long until DNS propagates, what errors applications see during the failover window, and what application-level retry strategy is required to survive this gracefully.
