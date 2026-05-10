---
version: 2
layout: default
title: "Key-Value Store"
parent: "NoSQL & Distributed Databases"
grand_parent: "Technical Dictionary"
nav_order: 8
permalink: /nosql/key-value-store/
id: NDB-013
category: NoSQL & Distributed Databases
difficulty: ★★☆
depends_on: Hashing, Database Fundamentals, Caching
used_by: Redis Data Structures, Redis Persistence, Caching
related: Document Store, Column Family, Redis Data Structures
tags:
  - nosql
  - key-value
  - redis
  - intermediate
---

# NDB-008 - Key-Value Store

⚡ TL;DR - A key-value store is the simplest NoSQL database: every value is addressed by a unique key, retrieved with O(1) key lookup, and the store has no knowledge of the value's structure - making it the fastest data store for cache, session, and simple counters, but useless for querying by value content.

| #452            | Category: NoSQL & Distributed Databases              | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------- | :-------------- |
| **Depends on:** | Hashing, Database Fundamentals, Caching              |                 |
| **Used by:**    | Redis Data Structures, Redis Persistence, Caching    |                 |
| **Related:**    | Document Store, Column Family, Redis Data Structures |                 |

---

### 🔥 The Problem This Solves

**SESSION STORAGE IN RELATIONAL DB:**
Every HTTP request: `SELECT * FROM sessions WHERE session_id = 'abc123'`. For 100,000 requests/second: 100,000 SQL queries to a relational database. Index lookup on the session table - fast, but still disk I/O, SQL parsing, B-tree traversal. Relational schema: one row per session with typed columns. Sessions are unstructured blobs. You're using a complex relational engine to do a simple hash table lookup.

**KEY-VALUE STORE:**
`GET session:abc123` → hash function → in-memory bucket → value. Microseconds. 100,000 requests/second: trivial. No schema. No SQL parser. No B-tree. Just a distributed hash table with persistence.

---

### 📘 Textbook Definition

A **key-value store** is a database that stores data as a collection of (key, value) pairs, where the key is a unique identifier and the value is an opaque binary blob (or typed structure in advanced implementations). The fundamental operations: **GET(key)**, **SET(key, value)**, **DELETE(key)**. The store typically treats the value as opaque - it doesn't understand or index the value's contents. Key-value stores are optimized for single-key lookup (O(1) hash-based access) and are the highest-throughput, lowest-latency database type. Persistence ranges from none (pure cache) to disk-based with durability guarantees. Leading implementations: **Redis** (in-memory with persistence, rich data structures), **Memcached** (pure cache, no persistence, simpler), **DynamoDB** (distributed, fully managed, hybrid KV/document), **etcd** (distributed configuration store; Raft consensus; used in Kubernetes), **RocksDB** (embedded, LSM-tree, used inside Cassandra, TiKV, etc.).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A key-value store is a hash map at database scale - put a value in with a key, get it back instantly with the same key, but you can't search by value.

**One analogy:**

> A coat check at a restaurant. You hand in your coat, they give you a numbered ticket (the key). You return with the ticket - they return your coat instantly (O(1) lookup). The coat check has no idea what's inside the bags they're storing (opaque values). They cannot say "find me all coats with a blue lining" - they only know about tickets, not coat contents.

- "Numbered ticket" → key
- "Coat" → value (opaque to the store)
- "Return with ticket → instant retrieval" → O(1) GET
- "Can't search by coat contents" → no value-based querying
- "Multiple coat checks in the same building" → distributed key-value store (partitioned by key hash)

**One insight:**
Key-value stores are the foundation of everything fast in modern infrastructure. Session stores, feature flags, rate limit counters, distributed locks, pub/sub messaging, leaderboards - all implemented on Redis. The "simplicity" of the key-value model (no schema, no joins) isn't a limitation - it's the source of its performance. By not knowing what the value is, the store doesn't need to parse, index, or validate it - it just moves bytes.

---

### 🔩 First Principles Explanation

**REDIS CORE OPERATIONS:**

```bash
# String (most basic)
SET user:42:name "Alice"          # store
GET user:42:name                  # "Alice"
SET user:42:loginCount 0
INCR user:42:loginCount           # atomic increment → 1
INCRBY user:42:loginCount 5       # → 6
EXPIRE user:42:name 3600          # TTL: expire in 1 hour
TTL user:42:name                  # seconds remaining

# Atomic SET only if not exists (distributed lock / idempotency key)
SET lock:resource1 "worker-A" NX EX 30  # NX = only if not exists; EX = 30s TTL
# Returns OK (lock acquired) or nil (lock held by someone else)

# Bulk ops
MSET k1 v1 k2 v2 k3 v3
MGET k1 k2 k3
```

**KEY DESIGN PATTERNS:**

```
# Namespacing with colons (Redis convention - not enforced, just convention)
user:42:profile         → user profile blob
user:42:session         → session token
product:123:price       → product price
order:456:status        → order status
rate:192.168.1.1:api    → rate limit counter for this IP + endpoint

# Benefits:
# - Key collision avoidance across domains
# - Pattern matching: SCAN 0 MATCH "user:42:*" COUNT 100
# - Namespace-level TTL strategies (all session keys expire in 24h)
```

**REDIS vs MEMCACHED:**

```
Redis:
  - Data structures: String, Hash, List, Set, Sorted Set, Stream, Bitmap, HyperLogLog
  - Persistence: RDB snapshots + AOF (append-only file)
  - Replication: master-replica + Sentinel / Redis Cluster
  - Pub/Sub: yes (but use Kafka/RabbitMQ for reliable messaging)
  - Scripting: Lua scripts (atomic multi-op)
  - Use when: you need any of the above features

Memcached:
  - Data structures: String only
  - Persistence: none (pure cache)
  - Replication: none (consistent hashing at client level)
  - Multi-threading: yes (Redis is single-threaded event loop*)
  - Use when: simple cache, need multi-core CPU utilization, simplest possible setup
  * Redis 6+ has multi-threaded I/O; commands still single-threaded for atomic semantics
```

**PARTITIONING IN KEY-VALUE STORES:**

```
Hash-based partitioning: shard = hash(key) % N
  DynamoDB: murmur3(partition_key) % num_partitions
  Memcached: consistent hashing ring (client-side)
  Redis Cluster: 16384 hash slots; each node owns a range of slots
    slot = CRC16(key) % 16384
    Node A: slots 0-5460
    Node B: slots 5461-10922
    Node C: slots 10923-16383

  Key tags (Redis Cluster): force keys to same slot for multi-key ops
    MSET {user:42}:profile data {user:42}:session token
    Both hash on "user:42" → same slot → same node → MSET works
```

**DISTRIBUTED LOCK WITH REDIS (Redlock):**

```python
# Simple single-node lock:
result = redis.set("lock:resource", "unique-token-xyz", nx=True, ex=30)
if result:
    try:
        # critical section
    finally:
        # Release only if we still own it (Lua script for atomicity)
        lua = """
        if redis.call('get', KEYS[1]) == ARGV[1] then
            return redis.call('del', KEYS[1])
        else
            return 0
        end
        """
        redis.eval(lua, 1, "lock:resource", "unique-token-xyz")
```

---

### 🧪 Thought Experiment

**RATE LIMITING WITH REDIS (SLIDING WINDOW)**

Goal: allow max 100 API requests per minute per user. Simple counter:

```
INCR rate:user42:2024010112      # key = user + minute bucket
EXPIRE rate:user42:2024010112 60 # auto-cleanup after 60s
# If > 100: reject request
```

**PROBLEM:** At minute boundary (59.9s to 60.1s): counter resets → user can burst 200 requests across the boundary. Sliding window:

```python
# Sorted Set for sliding window (score = timestamp)
now = time.time()
window = 60  # 1 minute
key = f"rate:user42"

with redis.pipeline() as pipe:
    # Remove entries older than 1 window
    pipe.zremrangebyscore(key, 0, now - window)
    # Add current request (score = timestamp, member = unique request id)
    pipe.zadd(key, {str(uuid.uuid4()): now})
    # Count requests in window
    pipe.zcard(key)
    # Reset TTL
    pipe.expire(key, window)
    results = pipe.execute()

request_count = results[2]
if request_count > 100:
    return 429  # Too Many Requests
```

This is a precise sliding window rate limiter with O(log N) Redis operations. N = requests in window per user. The key-value model (specifically Redis Sorted Sets) is the perfect data structure for this pattern - no SQL, no locks, just atomic Redis commands.

---

### 🧠 Mental Model / Analogy

> A key-value store is a vending machine. You press a button code (key) and get the item (value). The machine is perfectly optimized for one operation: code → item. It doesn't matter what's inside the item - the machine just stores and dispenses it. You can't ask the machine "give me all items containing chocolate" - it only understands button codes. But for "give me item B4," it's instantaneous and can serve thousands of customers simultaneously.

- "Button code" → key (e.g., `product:123:price`)
- "Item dispensed" → value (whatever bytes are stored)
- "Machine doesn't know what's inside" → opaque values (no schema)
- "Can't search for chocolate" → no value-based querying
- "Thousands of customers simultaneously" → high throughput (Redis: 1M+ ops/sec)

---

### 📶 Gradual Depth - Four Levels

**Level 1:** A key-value store is like a dictionary or hash map in memory, but persistent and accessible over the network. You store any data under a name (key) and get it back by that same name instantly. It's the fastest type of database because it only needs to do one thing: key lookup.

**Level 2:** Use Redis for: session storage (SET session:TOKEN data EX 3600), rate limiting (INCR + EXPIRE), distributed locks (SET NX EX), feature flags (HSET features flag1 true), simple counters (INCR). Design keys with `:` namespacing for organization. Always set TTLs on transient data to prevent unbounded memory growth. Use `SCAN` for iteration (never `KEYS *` in production - it blocks the single-threaded Redis).

**Level 3:** Redis's single-threaded event loop guarantees atomicity of individual commands without locks. `INCR` is atomic: read-increment-write as one operation, even with thousands of concurrent clients. For multi-command atomicity: use `MULTI/EXEC` (transaction) or Lua scripts (`EVAL`). Lua scripts execute atomically - no other Redis commands run between script statements. Redis Cluster's hash slot design: all keys in `{}` tags hash on the tag, enabling multi-key operations across nodes only if the keys share the same hash tag. RDB vs. AOF persistence: RDB = point-in-time snapshots (small, fast, some data loss); AOF = every write command logged (full durability, larger file). fsync=always for AOF gives PostgreSQL-level durability at ~2× Redis throughput cost.

**Level 4:** The key-value store is the purest embodiment of the CAP theorem's CP vs. AP choice. **etcd** (used in Kubernetes for cluster state): Raft consensus → CP (consistent, partition-tolerant, but writes unavailable during leader election). Used for: distributed configuration, service discovery, Kubernetes etcd. **DynamoDB** (Amazon): consistent hashing → AP (available, partition-tolerant, eventually consistent by default). Read consistency tunable (eventually consistent vs. strongly consistent reads). **Redis Cluster**: AP by default (async replication; may lose last writes on failover); can be configured for stronger durability (wait=1,1 for sync replication to one replica). The key insight: the same conceptual data model (key → value) can implement radically different consistency models depending on the replication and consensus strategy. Your choice of key-value store IS your choice of consistency model.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ REDIS CLUSTER KEY ROUTING                            │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Client: SET user:42:session "token-abc"             │
│     ↓                                                │
│  Client library: slot = CRC16("user:42:session")     │
│                           % 16384 = slot 5432        │
│     ↓                                                │
│  Route to Node B (owns slots 5461-10922)             │
│  Node B: hash slot 5432 is NOT mine (5432 < 5461)    │
│  → Returns MOVED 5432 redis-node-A:6379              │
│     ↓                                                │
│  Client: redirects to Node A                         │
│  Node A: slot 5432 → store value                     │
│  → Returns OK                                        │
│                                                      │
│  Client library caches slot→node mapping             │
│  Next SET to same slot: goes directly to Node A      │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**SESSION STORE FLOW:**

```
User login → authenticate → generate session token
→ Redis: SET session:{token} {userId:42, role:admin, ...} EX 3600
→ Return session token to client (cookie or Bearer)

Subsequent request with token:
→ [KEY-VALUE STORE ← YOU ARE HERE: O(1) session lookup]
→ Redis: GET session:{token}
→ Microseconds → user context loaded
→ No DB query needed for every request
→ Session expires automatically after 1 hour (TTL)
```

---

### ⚖️ Comparison Table

| Feature        | Key-Value (Redis)       | Document (MongoDB) | Relational (PostgreSQL) |
| -------------- | ----------------------- | ------------------ | ----------------------- |
| Query by value | ❌ None                 | ✅ Rich            | ✅ Full SQL             |
| Lookup by key  | ✅ O(1)                 | ✅ O(log N)        | ✅ O(log N) index       |
| Latency        | Sub-millisecond         | 1–10ms             | 1–50ms                  |
| Throughput     | 1M+ ops/sec             | 100K/sec           | 10K–100K/sec            |
| Persistence    | Optional (RDB/AOF)      | Always             | Always (WAL)            |
| Best for       | Cache, session, counter | Profile, catalog   | Financial, relational   |

---

### ⚠️ Common Misconceptions

| Misconception                            | Reality                                                                                                                                                                                      |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Redis is just a cache                    | Redis is a full data structure server with optional persistence (RDB/AOF), replication, clustering, and Lua scripting. It's used as a primary database for appropriate use cases             |
| Key-value stores have no structure       | Redis has rich data structures (strings, hashes, lists, sets, sorted sets, streams). "Key-value" describes the access model; the value itself can be structured                              |
| `KEYS *` is a quick way to list all keys | `KEYS *` blocks the single-threaded Redis event loop for the duration of the scan - it can take seconds on large datasets, blocking all other operations. Use `SCAN` instead                 |
| Key-value stores are always in-memory    | Memcached is always in-memory. Redis persists to disk (RDB/AOF). DynamoDB is disk-based (SSD). RocksDB is LSM-tree on disk. "In-memory" is a property of some implementations, not the model |

---

### 🚨 Failure Modes & Diagnosis

**1. Memory Exhaustion - Redis OOM (Out of Memory)**

**Symptom:** Redis starts evicting keys you didn't expect to evict (or crashes with OOM if eviction is disabled). Application receives nil responses for previously set keys.

**Root Cause:** Data grew beyond configured `maxmemory`. Common cause: TTLs not set on keys that should be transient; or unbounded set/list growth (e.g., `RPUSH` without ever trimming).

**Diagnostic:**

```bash
redis-cli INFO memory
# used_memory_human: how much memory is used
# maxmemory_human: configured limit
# mem_fragmentation_ratio: > 1.5 = significant fragmentation
# evicted_keys: non-zero = eviction is happening

redis-cli INFO keyspace
# db0: keys=5000000,expires=100000
# 5M keys, only 100K with TTLs → millions of keys never expire!
```

**Fix:** Set `maxmemory-policy allkeys-lru` (evict least recently used across all keys) for cache use cases. Or `volatile-lru` (only evict keys with TTLs). For sessions: always set TTL. For persistent data: increase memory or move to a persistent database.

**Prevention:** Every `SET` that stores transient data must include `EX` or `PX`. Monitor `evicted_keys` metric. Alert when `used_memory > 80% of maxmemory`.

---

### 🔗 Related Keywords

**Prerequisites:** Hashing, Database Fundamentals, Caching
**Builds On This:** Redis Data Structures, Redis Persistence, Caching
**Related:** Document Store, Column Family

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ MODEL        │ GET/SET/DEL by key; opaque value          │
│ LATENCY      │ Sub-millisecond (Redis in-memory)         │
│ USE CASES    │ Session, cache, counter, lock, pub/sub    │
│ NEVER DO     │ KEYS * in production; no TTL on sessions  │
│ REDIS OPS    │ SET/GET/INCR/EXPIRE/HSET/ZADD/SCAN        │
│ KEY FORMAT   │ namespace:id:field  (e.g., user:42:sess)  │
│ ONE-LINER    │ "Hash table at database scale -           │
│              │  O(1) by key, blind to value contents"   │
│ NEXT EXPLORE │ Redis Data Structures → Redis Persistence │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Question) Design a feature flag system using Redis for a SaaS application with 50,000 tenants. Each tenant can have different flags enabled/disabled. Flags change infrequently (updated by admins). Every API request (100K/sec) must check if a feature is enabled for the requesting tenant. Design the key schema, data structure, caching strategy, and cache invalidation approach.

**Q2.** (TYPE D - Failure Scenario) Your Redis Cluster has 6 nodes (3 primary + 3 replica). Primary node B fails. Before failover completes (30 seconds), what happens to requests that should go to Shard B? After failover: Replica B is promoted. When Primary B recovers and rejoins as a replica - it has 30 seconds of writes it never received (async replication). What happens to those writes? How do you configure Redis to minimize data loss in this scenario?
