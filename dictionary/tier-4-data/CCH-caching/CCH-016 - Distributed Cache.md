---
version: 2
layout: default
title: "Distributed Cache"
parent: "Caching"
grand_parent: "Technical Dictionary"
nav_order: 16
permalink: /caching/distributed-cache/
id: CCH-016
category: Caching
difficulty: ★★★
depends_on: Caching, Redis Data Structures, Consistent Hashing in Cache
used_by: System Design, Microservices, Distributed Systems
related: Redis Cluster, Local Cache vs Distributed Cache, Cache Coherence
tags:
  - caching
  - distributed-cache
  - redis-cluster
  - scalability
  - deep-dive
---

# CCH-016 - Distributed Cache

⚡ TL;DR - A distributed cache is a cache shared across multiple application instances and deployed on multiple nodes - all instances read from and write to the same cache pool; it solves the **consistency problem** of per-instance local caches (where Instance A's cache update isn't visible to Instance B) and provides **horizontal scalability** beyond what a single cache node can hold.

| #486            | Category: Caching                                                | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------- | :-------------- |
| **Depends on:** | Caching, Redis Data Structures, Consistent Hashing in Cache      |                 |
| **Used by:**    | System Design, Microservices, Distributed Systems                |                 |
| **Related:**    | Redis Cluster, Local Cache vs Distributed Cache, Cache Coherence |                 |

---

### 🔥 The Problem This Solves

**LOCAL CACHE INCONSISTENCY IN MULTI-INSTANCE DEPLOYMENTS:**
With 20 instances of a service, each instance has its own local Caffeine cache. Instance A updates product:42 (price changed) and invalidates its local cache. Instances B through T still have the old cached price. Users load-balanced to Instance A see the new price; users load-balanced to Instances B-T see the old price. Inconsistency - different users see different prices from the same API.

**SINGLE CACHE NODE MEMORY LIMIT:**
A single Redis node has a practical limit of ~50-100GB RAM. For a product catalog with 50 million products (1KB each = 50GB), a single node is tight. For user sessions of 100 million users: impossible on one node. Distributed cache (Redis Cluster) shards the keyspace across multiple nodes - effectively unlimited capacity.

---

### 📘 Textbook Definition

A **Distributed Cache** is a cache system deployed across multiple nodes, where the cache data is **shared by all application instances** in the cluster. All instances read from and write to the same cache pool, ensuring cache consistency across the application. Two deployment modes: **(1) Client-side sharding** (consistent hashing): clients (or a smart library like Jedis with cluster support) hash keys to determine which cache node to contact - no central coordinator. **(2) Proxy-based sharding**: a proxy (Twemproxy, Redis Cluster Proxy) routes requests to the appropriate node - simpler clients. **Redis Cluster**: the standard distributed cache for Redis - 16,384 hash slots distributed across N nodes, clients map key → hash slot → node. **Memcached cluster**: client-side consistent hashing, no server-side coordination. **Hazelcast**: distributed in-memory data grid, peer-to-peer (no primary/replica distinction), supports data distribution + computation co-location. **AWS ElastiCache**: managed Redis Cluster or Memcached, auto-scaling, automatic node replacement. Key properties: **Partition tolerance** (CAP - distributed cache is typically AP or CP depending on configuration), **replication** (each primary node has replicas for failover), **resharding** (rebalancing key distribution when nodes are added/removed).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Distributed cache = shared cache across all app instances and across multiple cache nodes - all instances see the same data, and capacity scales by adding nodes.

**One analogy:**

> A public library system with multiple branches (cache nodes). All branches share the same catalog (distributed keyspace). Any branch can answer any patron's query about any book (any app instance can query any key). Compare to private libraries in each person's home (local cache): your library has your books, your neighbor's has theirs - different answers for the same question.

- "Multiple branches" → Redis Cluster nodes
- "Shared catalog" → distributed keyspace
- "Any branch answers any query" → any app instance queries any cache key consistently
- "Private home library" → local Caffeine cache (per-instance, inconsistent)

**One insight:**
A distributed cache introduces a **network hop** for every cache operation (Redis: ~1ms local network RTT) - whereas a local cache is an in-memory lookup (~0.01ms). For high-frequency, low-latency operations, this 100× latency difference matters. The typical architecture: **L1 (local Caffeine, 1-5 seconds TTL)** for the hottest keys → **L2 (Redis Cluster, 5-60 minutes TTL)** for the broader cache. This multi-level cache combines consistency (L2 is shared, all instances see the same) with speed (L1 has zero network RTT for the hottest keys).

---

### 🔩 First Principles Explanation

**REDIS CLUSTER KEY ROUTING:**

```
Redis Cluster: 16,384 hash slots distributed across nodes

Key → hash slot mapping:
  HASH_SLOT = CRC16(key) % 16384

Example 3-node cluster:
  Node 1: slots 0-5460      (33% of keyspace)
  Node 2: slots 5461-10922  (33% of keyspace)
  Node 3: slots 10923-16383 (33% of keyspace)

SET product:42 "data":
  CRC16("product:42") % 16384 = 7842
  Slot 7842 → Node 2
  Client sends SET to Node 2

GET product:42:
  CRC16("product:42") % 16384 = 7842
  Client sends GET to Node 2 directly

Key hashing with tags (co-location):
  {user}:profile:42 and {user}:orders:42
  Same hash slot: computed on "user" (the {tag}) not the full key
  → Both keys always on same node
  → MGET, transactions, Lua scripts work across these keys

  Important: without tags, user:profile:42 and user:orders:42 may be on different nodes
  Multi-key commands across different nodes = CROSSSLOT error
```

**SPRING BOOT + REDIS CLUSTER:**

```yaml
# application.yml
spring:
  data:
    redis:
      cluster:
        nodes:
          - redis-node-1:6379
          - redis-node-2:6379
          - redis-node-3:6379
        max-redirects: 3 # Follow MOVED/ASK redirects (node failover)
      lettuce:
        cluster:
          refresh:
            adaptive: true # Auto-discover new nodes
            period: 30s # Refresh topology every 30s
        pool:
          max-active: 50 # Max connections per node
          max-idle: 10
          min-idle: 2
```

```java
// Spring RedisTemplate with cluster: transparent, same API as single-node Redis
@Service
public class ProductCacheService {

    @Autowired private RedisTemplate<String, Product> redisTemplate;

    public void cacheProduct(Product product) {
        // Lettuce client automatically routes to correct cluster node
        redisTemplate.opsForValue().set(
            "product:" + product.getId(),
            product,
            Duration.ofMinutes(10)
        );
    }

    public Optional<Product> getCachedProduct(String productId) {
        Product cached = redisTemplate.opsForValue()
            .get("product:" + productId, Product.class);
        return Optional.ofNullable(cached);
    }

    // Multi-key operation: requires keys to be in same hash slot (use tags)
    public Map<String, Product> getMultipleProducts(List<String> productIds) {
        // PROBLEM: productIds have different hash slots → CROSSSLOT error if using pipeline
        // SOLUTION: use individual GETs or ensure keys have same hash tag

        List<Object> results = redisTemplate.executePipelined(
            (RedisCallback<Object>) connection -> {
                productIds.forEach(id ->
                    connection.get(("product:" + id).getBytes())
                );
                return null;
            }
        );
        // Note: pipeline with Lettuce cluster may still issue N individual commands
        // across different nodes - not a single round-trip when keys span nodes

        return IntStream.range(0, productIds.size())
            .filter(i -> results.get(i) != null)
            .boxed()
            .collect(Collectors.toMap(
                productIds::get,
                i -> (Product) results.get(i)
            ));
    }
}
```

**NODE FAILURE AND FAILOVER:**

```
Redis Cluster failover:
  Each primary node has 1+ replicas (slaves)
  Normal operation: primary handles reads/writes

  Primary fails (network partition, hardware):
  1. Replicas detect: no PING response for cluster-node-timeout (default 15s)
  2. Replica initiates election: requests votes from other master nodes
  3. Majority of masters vote for replica → replica promoted to new primary
  4. Cluster reconfigured: new primary owns the hash slots
  5. Client reconnects: MOVED redirect to new primary

  Timeline: ~15-30 seconds downtime for affected hash slots during failover

  During failover: keys on failed node → CLUSTERDOWN error or timeout
  Application must handle:
    @Retryable with backoff (30-60s retry for cluster failover)
    OR: circuit breaker that opens for 30s then retries
    OR: fallback to database (cache miss on cluster error)

  Monitor cluster health:
  redis-cli -c -h redis-node-1 CLUSTER INFO
  redis-cli -c -h redis-node-1 CLUSTER NODES  # see node status and slot assignments
```

**HORIZONTAL SCALING: ADD NODE:**

```
Initial: 3 nodes → 16,384 slots / 3 = ~5,461 slots each

Add Node 4:
  redis-cli --cluster add-node redis-node-4:6379 redis-node-1:6379
  redis-cli --cluster reshard redis-node-1:6379
  # Move some slots from each existing node to Node 4
  # Example: move 1,365 slots from each of nodes 1,2,3 → 4,096 slots on Node 4
  # After reshard: 4 nodes × ~4,096 slots each

Keys that were on slots moved to Node 4:
  Migrated live (no downtime): Redis migrates keys slot by slot
  During migration: ASKING redirect for keys in mid-migration slots
  Client Lettuce: handles ASK redirects transparently (max-redirects: 3)

  Typical reshard time: 10-60 minutes for a large cluster with millions of keys
  No downtime during reshard (rolling migration)
```

---

### 🧪 Thought Experiment

**WHAT HAPPENS WHEN A USER'S SESSION KEY CROSSES NODES?**

Without hash tags: `session:alice:data` (hash slot 3000, Node 1) and `session:alice:cart` (hash slot 8000, Node 2).

A transaction tries: `MULTI / GET session:alice:data / GET session:alice:cart / EXEC` - Redis returns `CROSSSLOT: Keys in request don't hash to the same slot`.

**With hash tags:** `{session:alice}:data` and `{session:alice}:cart` - both hash on `session:alice` → same slot → same node → MULTI/EXEC works.

**Lesson:** In Redis Cluster, design key naming to co-locate related keys using hash tags when multi-key operations are needed.

---

### 🧠 Mental Model / Analogy

> Redis Cluster is like a city's public transit card system (distributed cache) vs. each neighborhood running its own fare system (local cache). With the transit card: tap anywhere in the city, the central system tracks your balance. If you tap your card at Station A (node 1), the deduction is immediately visible at Station B (node 2). Consistent. The "city map" (hash slot assignment) tells each station which trips to handle - no one station handles all trips (distributed). If one station's system fails (node failure), nearby backup stations cover its routes (replica failover).

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Distributed cache = shared across all instances. All instances see same data. Multiple nodes share the keyspace. Redis Cluster: 16,384 hash slots distributed across N nodes. Add nodes → more capacity + more throughput.

**Level 2:** Use Lettuce (Spring Boot default) with cluster topology auto-refresh. Design cache keys with hash tags for co-located keys (`{user:42}:profile`, `{user:42}:orders`). Handle CROSSSLOT errors (redesign keys). Configure circuit breaker for cluster failover period (15-30s).

**Level 3:** Cluster topology: Redis Cluster uses gossip protocol for node discovery and health checking (PING/PONG every second). Each node knows about all other nodes and their slot assignments. `CLUSTER INFO`: check `cluster_state:ok`, `cluster_slots_assigned:16384`. If any `cluster_state:fail` - node has failed and cluster may be degraded. Horizontal Read Scaling: by default, Redis Cluster only routes reads to primary nodes. To read from replicas: `READONLY` command before GET on a replica connection - allows reading slightly stale data from replicas, increasing read throughput 2-3× (one primary + 2 replicas = 3× read capacity per shard).

**Level 4:** Distributed caches face the CAP theorem: Redis Cluster is typically CP (consistent + partition tolerant) during normal operation, but degrades to unavailable for affected hash slots during network partitions or primary failures. The `cluster-require-full-coverage yes` setting (default) makes the entire cluster reject commands if any slot is uncovered - prioritizing consistency over availability. `cluster-require-full-coverage no` allows the healthy portion to continue serving - prioritizing availability. For read-heavy systems: add read replicas per shard and use `READONLY` reads for eventual consistency (slightly stale) with high availability. The distributed cache is itself a distributed system subject to the same challenges as any distributed database: replication lag, split-brain (both primary and replica accept writes during partition), and coordination overhead. Redis Cluster's single-leader-per-shard design simplifies this at the cost of a higher write latency (writes always go to primary) and primary failure downtime.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ REDIS CLUSTER: KEY ROUTING                           │
├──────────────────────────────────────────────────────┤
│                                                      │
│ App Instance 1: GET product:42                       │
│   Lettuce: CRC16("product:42") % 16384 = 7842        │
│   Slot 7842 → Node 2 (slots 5461-10922)             │
│   Lettuce sends: GET product:42 to Node 2            │
│   Node 2 returns: {price:9.99, ...}                  │
│                                                      │
│ App Instance 2 (different pod): GET product:42       │
│   [DIST CACHE ← YOU ARE HERE: shared keyspace]       │
│   Same slot calculation: 7842 → Node 2               │
│   Same result: {price:9.99, ...}                     │
│   BOTH instances see the same cached data ✓          │
│                                                      │
│ Compare to local cache:                              │
│   Instance 1's Caffeine: product:42 → {price:9.99}   │
│   Instance 2's Caffeine: product:42 → {price:12.99}  │
│   (Instance 1 updated its cache; Instance 2 didn't)  │
│   INCONSISTENCY - different users see different data │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**PRODUCT SERVICE (50 INSTANCES) → REDIS CLUSTER:**

```
User updates product price: PUT /products/42 {price: 29.99}
→ Request hits Instance 7 (load balanced)
→ ProductService.updatePrice("42", 29.99)
→ DB: UPDATE products SET price=29.99 WHERE id=42 - COMMIT
→ afterCommit: Redis DEL product:42
   Lettuce: hash("product:42") → slot 7842 → Node 2
   Node 2: DEL product:42 ✓

Next request: GET /products/42 (hits Instance 23 - different instance)
→ [DIST CACHE ← YOU ARE HERE: shared cache, not local]
→ ProductService.getProduct("42")
→ Redis GET product:42 → nil (MISS - key was deleted by Instance 7)
→ DB: SELECT price=29.99 (fresh)
→ Redis SET product:42 {price:29.99} (on Node 2 via slot 7842)
→ Response: {price: 29.99} ✓

All 50 instances: subsequent GET product:42 → Redis HIT → {price:29.99}
No instance serves stale data after invalidation ✓ (distributed cache consistency)
```

---

### ⚖️ Comparison Table

| Aspect                        | Local Cache (Caffeine)                       | Distributed Cache (Redis Cluster)        |
| ----------------------------- | -------------------------------------------- | ---------------------------------------- |
| Latency                       | ~0.01ms (in-process memory)                  | ~1ms (network RTT)                       |
| Consistency                   | Per-instance (inconsistent across instances) | Shared (consistent across all instances) |
| Capacity                      | Limited to JVM heap                          | Scales with nodes (TB possible)          |
| Failover                      | None (cache is lost on restart)              | Automatic (replica promotion)            |
| Invalidation across instances | Manual (pub/sub, event)                      | Automatic (shared keyspace)              |
| Best for                      | Hottest keys, single-instance                | Multi-instance deployments               |

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                                                                      |
| ----------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Redis Cluster is always the right choice"            | For single-instance deployments, Redis standalone is simpler. Redis Cluster adds complexity (CROSSSLOT, hash tags, topology management) - only needed for multi-node capacity or multi-instance consistency                  |
| "All Redis commands work with Redis Cluster"          | Multi-key commands (MGET, MSET, KEYS, SCAN across keyspace) require keys in the same hash slot. KEYS \* on a cluster only returns keys for the connected node's slots - use `SCAN` on each node separately for full keyspace |
| "Distributed cache eliminates all consistency issues" | A distributed cache is shared, but it's still an eventually consistent layer relative to the database. TTL-based expiry and invalidation timing still mean brief stale windows exist                                         |

---

### 🚨 Failure Modes & Diagnosis

**1. CROSSSLOT Error on Multi-Key Operations**

**Symptom:** `io.lettuce.core.cluster.PartitionSelectorException: Keys in request don't hash to the same slot`.

**Root Cause:** Multi-key operation (MGET, transaction, pipeline) with keys on different hash slots (different nodes).

**Fix:**

```java
// Bad: keys may be on different nodes
redisTemplate.opsForValue().multiGet(List.of("user:42:profile", "user:42:orders"));
// → CROSSSLOT error

// Good: hash tags ensure same slot
// Rename keys to: {user:42}:profile and {user:42}:orders
// Both hash on "user:42" → same slot → same node
redisTemplate.opsForValue().multiGet(List.of("{user:42}:profile", "{user:42}:orders"));
// Works ✓ (both on same node)
```

---

### 🔗 Related Keywords

**Prerequisites:** Caching, Redis Data Structures, Consistent Hashing in Cache
**Builds On This:** System Design, Microservices
**Related:** Redis Cluster, Local Cache vs Distributed Cache, Cache Coherence

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT        │ Cache shared across all app instances      │
│ REDIS       │ Redis Cluster: 16384 hash slots / N nodes  │
│ ROUTING     │ CRC16(key) % 16384 → slot → node          │
│ CO-LOCATE   │ {tag}:key1 and {tag}:key2 → same slot     │
│ FAILOVER    │ ~15-30s replica promotion on primary fail  │
│ SCALE       │ Add nodes + reshard (live, no downtime)    │
│ CROSSSLOT   │ Multi-key ops require same hash slot       │
│ MONITORING  │ CLUSTER INFO → cluster_state: ok           │
│ ONE-LINER   │ "All instances share one cache pool -     │
│             │  keyspace sharded across N nodes"          │
│ NEXT EXPLORE│ Cache Coherence → Multi-Level Cache         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Question) Design the caching architecture for a global e-commerce site with: 100 application instances in 3 regions (US, EU, APAC), 50M products, 100M active users, 500K orders/day. Consider: which data should use local vs. distributed cache, how to handle cross-region cache consistency, and what happens when a Redis Cluster node fails in one region.

**Q2.** (TYPE D - Failure Scenario) A Redis Cluster (3 primary + 3 replica) has one primary node fail. The `cluster-node-timeout` is set to 15 seconds. During the 15-second failover, 33% of all cache keys are unavailable. Your application is configured to throw exceptions on Redis errors (no fallback). Walk through: what happens to API latency, DB load, and user experience? What configuration changes would make the application resilient to this common failure?
