---
id: MSV-083
title: Distributed Caching in Microservices
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-001, MSV-010, MSV-020, MSV-030
used_by: MSV-010, MSV-030
related: MSV-001, MSV-010, MSV-020, MSV-030, MSV-025, MSV-042
tags:
  - microservices
  - caching
  - deep-dive
  - performance
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 83
permalink: /microservices/distributed-caching-in-microservices/
---

# MSV-083 - Distributed Caching in Microservices

⚡ TL;DR - Distributed Caching in Microservices:
shared cache (Redis, Memcached, Hazelcast)
accessible across multiple service instances
and multiple services. Patterns: Cache-Aside
(most common - app loads cache on miss),
Write-Through (cache updated on write),
Write-Behind (async write to DB), Read-Through
(cache loads on miss transparently). In
microservices: critical for (1) reducing
DB load at scale, (2) sharing session state
across service instances (stateless services),
(3) caching inter-service call results (reduce
latency chains). Key failure modes: cache
stampede (thundering herd), cache poisoning,
stale data, and split-brain (Redis replication
lag). Redis Cluster vs single Redis node:
critical decision at scale.

| #083 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | What are Microservices, API Gateway, Service Mesh, Database Per Service | |
| **Used by:** | API Gateway, Database Per Service | |
| **Related:** | What are Microservices, API Gateway, Service Mesh, Database Per Service, Circuit Breaker Pattern, Eventual Consistency | |

---

### 🔥 The Problem This Solves

**DB OVERLOAD AT MICROSERVICES SCALE:**
E-commerce platform. Product catalog:
500,000 products. 50 product-service instances.
Each request: queries the product DB. Peak
traffic: 50,000 requests/second. DB: 50,000
queries/second. DB connection pool: exhausted.
Latency: spikes to 5 seconds. Scale-up DB:
but the product data rarely changes (catalog
updated twice per day). 99.9% of DB reads:
same data, over and over. Solution: cache
product data in Redis. DB queries: drop from
50,000/s to < 100/s (cache misses only).
Response time: < 10ms (Redis) vs 200ms (DB).

---

### 📘 Textbook Definition

**Distributed Caching** in microservices: a
cache (in-memory data store) shared across
multiple service instances, enabling fast data
access without hitting primary data stores
(DB, external APIs) on every request.

**Common distributed caches:**
- **Redis**: most popular. Supports: strings,
  hashes, lists, sorted sets, HyperLogLog,
  pub/sub, Lua scripting. Persistence options:
  RDB snapshots, AOF. Redis Cluster: horizontal
  sharding. Redis Sentinel: high availability
  (failover). Used by: Spring Boot with
  `spring-boot-starter-data-redis`.
- **Memcached**: simpler, faster for pure
  string cache. No persistence, no replication.
  Horizontally scalable by client-side hashing.
  Use when: simple key-value, maximum throughput.
- **Hazelcast**: Java-native distributed cache
  + computation. Embedded in JVM (no separate
  process). Used for: distributed locking,
  compute-near-data patterns.

**Caching patterns:**
1. **Cache-Aside (Lazy Loading)**: application
   checks cache first. Miss: loads from DB,
   stores in cache, returns. Most common in
   microservices. App manages the cache.
2. **Write-Through**: on data write, update
   cache AND DB synchronously. Cache always
   consistent with DB. Tradeoff: write latency
   (both cache + DB on each write).
3. **Write-Behind (Write-Back)**: on write:
   update cache immediately, write to DB
   asynchronously. Lower write latency. Risk:
   data loss if cache fails before async write.
4. **Read-Through**: cache sits in front of
   DB; app always reads from cache; cache
   loads from DB on miss (transparent to app).
   Example: Redis as read-through cache.

**TTL (Time-To-Live)**: cache entries expire
after a set duration. Essential: prevents
stale data. Must be calibrated: too short =
frequent cache misses; too long = stale data.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Distributed cache (Redis): shared in-memory
store for all service instances. Hit rate > 95%
= dramatic DB load reduction and latency
improvement.

**One analogy:**
> Distributed cache is like a shared whiteboard
> in an office. Before whiteboard: every time
> someone needs the "Q3 sales figures," they
> walk to the filing room, pull the folder, read
> it, return. 100 people doing this: 100 trips
> to filing room. With a shared whiteboard:
> first person writes Q3 figures on the whiteboard
> (cache). Next 99 people: glance at the whiteboard
> (cache hit). Filing room (DB): gets 1 request
> instead of 100. When Q4 starts: erase the board
> (TTL expiry). Distributed cache = shared whiteboard
> for all service instances.

**One insight:**
The hardest part of caching is NOT the cache
read/write logic - it's deciding WHAT to cache
and for HOW LONG. A cache with TTL too long:
serves stale product prices, resulting in
undercharging customers. A cache with TTL too
short: provides no benefit (misses 60% of the
time). The art: matching TTL to data volatility.
Product descriptions: 24h TTL. Exchange rates:
5 second TTL. User session: 30 minute TTL.
User cart (modified frequently): cache-aside
with immediate invalidation on cart update.

---

### 🔩 First Principles Explanation

**CACHE-ASIDE PATTERN: THE STANDARD APPROACH**

```
Cache-Aside flow:

  REQUEST
    |
    v
  Service checks Redis for key
    |
    +---[HIT]---> Return cached data
    |                 (fast, ~1ms)
    |
    +---[MISS]--> Query database
                  Store in Redis (with TTL)
                  Return data
                  (slow, ~50-200ms, but
                   next request: HIT)
                   
Redis key design:
  product:{productId} -> product JSON
  user:session:{sessionId} -> session JSON
  rate-limit:user:{userId} -> request count
  
TTL strategy:
  Product data: 1 hour (rarely changes)
  User session: 30 minutes (security)
  Exchange rate: 60 seconds (frequently changes)
  Rate limit counter: 60 seconds (sliding window)
```

**CACHE STAMPEDE (THUNDERING HERD): THE CRITICAL FAILURE MODE**

```
Scenario:
  Redis: product:{1234} expires simultaneously
  Traffic: 1000 requests/second
  
Without protection:
  All 1000 concurrent requests: cache miss
  All 1000: query the database simultaneously
  DB: receives 1000 queries at once (overload)
  DB: slows or crashes
  Cache: repopulated 1000 times (wasted)
  
Fix 1: Probabilistic Early Expiration
  Recompute cache BEFORE it expires (when
  remaining TTL < random threshold)
  One request: recomputes early
  Others: still see valid (soon-to-expire) cache
  
Fix 2: Locking (distributed lock)
  On cache miss: acquire distributed lock
  Only ONE request: queries DB and repopulates
  Others: wait for lock, then get cache hit
  
  Redis SET NX (set if not exists):
    SETNX product:1234:lock 1 EX 5
    (acquire lock; expires in 5s)
    If 0 (already set): another request has lock
    Wait briefly, retry -> cache HIT
    If 1 (acquired): load from DB, set cache,
    release lock (DEL product:1234:lock)
```

---

### 🧪 Thought Experiment

**SESSION STATE: STATELESS SERVICES NEED A CACHE**

```
Problem:
  User logs in to order-service instance A
  Session stored: in instance A memory
  Next request: load balanced to instance B
  Instance B: no session -> user logged out!
  
Solution: Redis session store
  All service instances: share Redis session
  User login: store session in Redis
    SET user:session:{sessionId} {userDataJson}
        EX 1800  # 30 minute TTL
  Every request: instance checks Redis
    GET user:session:{sessionId}
    -> session data regardless of which
       instance handles the request
  
  Services: now truly stateless
  Horizontal scaling: trivial
  (add instances; all share Redis session)
  
  Redis Cluster: for high availability
    Multiple shards: session data distributed
    If one shard fails: sessions on that shard
    lost (users logged out). Mitigation:
    Redis Sentinel (failover) or
    Redis Cluster with replication (primary +
    replica per shard; failover auto)
```

---

### 🧠 Mental Model / Analogy

> Distributed caching in microservices is like
> a server farm's shared RAM. Each service
> instance has its own local memory (L1 cache:
> fast, small, private). Redis: is the shared
> L3 cache (slower than local but much faster
> than disk/DB, and SHARED across all instances).
> DB: is the disk (slowest, persistent, authoritative).
> Cache-aside: app decides what to promote to
> L3 (Redis). TTL: like cache line invalidation.
> Cache stampede: like L3 cache coherence
> problem (all CPUs invalidate simultaneously).
> The cache hierarchy: applies at every level
> of modern computing, including distributed
> microservices.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Distributed cache (Redis): fast in-memory
storage shared by all service copies. Reduces
DB load and speeds up responses.

**Level 2 - Cache-Aside with Spring (junior developer):**
```java
@Cacheable(value = "products", key = "#productId")
public Product getProduct(String productId) {
    return productRepository.findById(productId)
        .orElseThrow();
}
// Spring: checks Redis before calling getProduct
// Cache miss: calls method, stores result in Redis
// Cache hit: returns from Redis directly (method skipped)
```

**Level 3 - Eviction policies (mid-level):**
Redis eviction policies when memory full:
- `allkeys-lru`: evict least recently used
  (most common for caches)
- `volatile-lru`: evict LRU keys that have TTL
- `allkeys-lfu`: evict least frequently used
- `noeviction`: return error when full (for
  persistent data, NOT for cache)
For pure cache: use `allkeys-lru`. For mixed
use (cache + persistent): `volatile-lru`.

**Level 4 - Redis Cluster sharding (senior):**
Redis Cluster: hash slots (0-16383) divided
among shards (3 primaries minimum). Each key:
hashed to a slot, routed to the right shard.
Multi-key operations: require same hash slot.
Hash tags: `{user:1}:session` and `{user:1}:cart`
both hash to same slot (enables atomic multi-key
ops for same user). Resharding: online (no
downtime) but CPU-intensive.

**Level 5 - Cache consistency in distributed transactions (principal):**
The hardest problem: cache consistency across
services in a distributed transaction. Order
service: updates order status, invalidates
cache. But: cache invalidation fails (Redis
timeout). Read-your-writes: user sees stale
order status. Solutions: (1) cache invalidation
with retry + dead-letter queue; (2) event-
driven cache invalidation (Kafka event ->
all services listening invalidate their cache);
(3) write-through with saga (update cache
and DB in same saga step, with compensation).
There is no perfect solution: this is the
fundamental cache consistency vs availability
tradeoff (CAP theorem at the cache layer).

---

### ⚙️ How It Works (Mechanism)

```java
// REDIS CACHE WITH STAMPEDE PROTECTION
// (distributed lock on cache miss)

@Service
public class ProductCacheService {
    private final StringRedisTemplate redis;
    private final ProductRepository productRepo;
    private static final Duration TTL =
        Duration.ofHours(1);
    private static final Duration LOCK_TTL =
        Duration.ofSeconds(5);
    
    public Product getProduct(String productId) {
        String cacheKey = "product:" + productId;
        String lockKey = cacheKey + ":lock";
        
        // Step 1: Try cache hit
        String cached = redis.opsForValue().get(cacheKey);
        if (cached != null) {
            return deserialize(cached, Product.class);
        }
        
        // Step 2: Cache miss - acquire lock
        // SETNX (set if not exists) + TTL
        Boolean locked = redis.opsForValue()
            .setIfAbsent(lockKey, "1", LOCK_TTL);
        
        if (Boolean.TRUE.equals(locked)) {
            try {
                // Step 3: We hold the lock, load from DB
                Product product = productRepo
                    .findById(productId)
                    .orElseThrow();
                // Step 4: Populate cache
                redis.opsForValue().set(
                    cacheKey,
                    serialize(product),
                    TTL);
                return product;
            } finally {
                // Step 5: Release lock
                redis.delete(lockKey);
            }
        } else {
            // Step 6: Another thread holds lock
            // Brief wait + retry (exponential backoff)
            // After lock released: next attempt = HIT
            try { Thread.sleep(50); }
            catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            // Recursive retry (1 level deep max)
            return getProduct(productId);
        }
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
CACHING STRATEGY ACROSS MICROSERVICES:

  Client Request (GET /products/1234)
      |
      v
  API Gateway (checks rate limit via Redis)
    INCR rate-limit:user:abc:window:1700000
    -> allow or 429
      |
      v
  product-service (checks product cache)
    GET product:1234
    -> HIT: return from Redis (1ms)
    -> MISS: query DB, cache result (200ms)
    
    During processing: checks inventory cache
    GET inventory:1234
    -> HIT: use cached stock count
    (TTL: 60s - acceptable staleness for display)
    
      |
      v
  Response: product data + estimated stock
  Total latency: 5ms (all cache hits)
  vs 400ms (all DB queries)
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: No cache vs Cache-Aside**

```java
// BAD: DB query on every request
// 1000 requests/second -> 1000 DB queries/second
// DB connection pool: exhausted under load
@RestController
public class ProductController {
    
    @GetMapping("/products/{id}")
    public Product getProduct(@PathVariable String id) {
        // Direct DB query every request
        // No caching consideration
        // Fine at 10 req/s; breaks at 1000 req/s
        return productRepository.findById(id)
            .orElseThrow();
    }
}
```

```java
// GOOD: Cache-Aside with Spring Cache + Redis
@Service
public class ProductService {
    
    // Spring @Cacheable:
    //   1. Check Redis for "products::" + id
    //   2. Cache HIT: return cached value (skip method)
    //   3. Cache MISS: execute method, cache result
    @Cacheable(value = "products", key = "#id")
    public Product getProduct(String id) {
        return productRepository.findById(id)
            .orElseThrow();
    }
    
    // @CacheEvict: invalidate on update
    // Prevents stale data after update
    @CacheEvict(value = "products", key = "#id")
    @Transactional
    public Product updateProduct(
            String id, Product update) {
        // Cache invalidated AFTER successful update
        return productRepository.save(update);
    }
}

// application.yaml:
//spring:
//  cache:
//    type: redis
//  data:
//    redis:
//      host: redis-cluster
//      port: 6379
//  cache:
//    redis:
//      time-to-live: 3600000  # 1 hour in ms

// Result:
// First request for product "abc": DB query (200ms)
// Next 1000 requests: Redis HIT (1ms)
// Update product "abc": cache evicted
// Next request: DB query again (fresh data)
```

---

### ⚖️ Comparison Table

| Caching Pattern | Consistency | Write Latency | Read Latency | Use Case |
|---|---|---|---|---|
| **Cache-Aside** | Eventually consistent (on TTL) | DB only | Low (HIT) / High (MISS) | Read-heavy, tolerate staleness |
| **Write-Through** | Strong (cache = DB always) | High (cache + DB) | Always low | Read/write balance; must be consistent |
| **Write-Behind** | Eventual (async DB) | Lowest (cache only) | Always low | Write-heavy; tolerate brief inconsistency |
| **Read-Through** | Eventually consistent | DB only | Low (HIT) | Transparent to app |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| A high cache hit rate (95%) means the caching strategy is optimal | Hit rate measures the cache is working, not that it's optimal. A cache with TTL of 24 hours on exchange rates will have a high hit rate but serve wrong data (financial risk). A cache on user carts (updated every minute by the user) with 1-hour TTL: serves stale cart totals. Hit rate and data correctness are independent metrics. Optimize both: high hit rate AND acceptable data freshness. |
| Redis is just a cache | Redis is a multi-purpose in-memory data structure store. Use cases: caching (most common), session store, pub/sub message broker, rate limiter (atomic INCR), leaderboard (sorted sets), distributed lock (SETNX), geospatial queries (GEO commands), time series (TSDB module). Understanding Redis's data structures and commands is more important than knowing it's "just a cache." |
| Cache invalidation on update is simple | Cache invalidation in microservices is hard. Simple case: one service owns the data, invalidates cache on update. Hard case: product-service updates a product, but order-service caches product data too. How does order-service's cache get invalidated? Options: (1) TTL-based (eventual consistency), (2) event-driven (product-service publishes `ProductUpdated` event; order-service subscribes and invalidates), (3) short TTL (accept staleness). Each has trade-offs; there's no perfect answer. |

---

### 🚨 Failure Modes & Diagnosis

**Cache stampede: thundering herd on Redis TTL expiry**

**Symptom:**
Every hour (product cache TTL = 1 hour):
DB spikes to 10,000 queries/second for
60 seconds. During this period: API latency
spikes from 10ms to 4 seconds. After 60s:
latency returns to normal. Cycle repeats
exactly every hour. DB CPU: hits 90% during
spike.

**Root Cause:**
All product cache keys: same TTL (set at
service startup). All expire simultaneously
every hour. 10,000 concurrent requests:
all miss cache at same time. All query DB
simultaneously. Cache stampede.

**Diagnosis:**
```bash
# Check Redis TTL distribution:
redis-cli DEBUG SLEEP 0  # check responsiveness
redis-cli INFO keyspace
# Look for: db0:keys=50000,expires=50000
# (all keys have TTL = synchronized expiry)

# Check DB slow query log during spike:
# PostgreSQL:
SELECT query, calls, mean_exec_time
FROM pg_stat_statements
WHERE calls > 1000
ORDER BY calls DESC;
# During spike: product queries spike in "calls"
```

**Fix:**
```java
// Add TTL jitter: randomize expiry per key
// Prevents synchronized stampede

long baseTtlSeconds = 3600;  // 1 hour
long jitterSeconds = (long)(Math.random() * 300);
// Each key: expires between 60min and 65min
long ttl = baseTtlSeconds + jitterSeconds;

redis.opsForValue().set(
    cacheKey,
    serialize(product),
    Duration.ofSeconds(ttl));
// Keys expire at different times -> DB load
// spread over 5-minute window, not all at once
```

---

### 🔗 Related Keywords

**Core caching context:**
- `API Gateway` - gateway uses Redis for
  rate limiting and response caching
- `Database Per Service` - caching reduces
  cross-service DB load concerns

**Distributed systems context:**
- `Circuit Breaker Pattern` - circuit breaker
  protects against Redis unavailability
- `Eventual Consistency` - cache-aside is
  eventually consistent with TTL

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| PATTERN     | Cache-Aside: most common          |
|             | app manages cache miss/evict      |
+-------------+-----------------------------------+
| FAILURE     | Stampede: TTL jitter to fix       |
| MODES       | Stale data: shorter TTL / evict   |
|             | Poisoning: validate before cache  |
+-------------+-----------------------------------+
| REDIS TYPES | String: JSON objects, counters   |
|             | Hash: partial updates (user obj)  |
|             | Sorted Set: leaderboards, TTL PQ  |
+-------------+-----------------------------------+
| ONE-LINER   | "Cache-Aside + TTL jitter.        |
|             |  Hit rate 95%+ = DB relief.       |
|             |  Invalidate on write."            |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. Cache-Aside: app checks cache first, loads
   from DB on miss, stores in cache with TTL.
   Most common pattern. Spring `@Cacheable`
   handles this automatically.
2. Cache stampede: happens when many keys expire
   simultaneously. Fix: TTL jitter (randomize
   expiry per key by +/- 10%).
3. Cache invalidation: hardest part. On write:
   use `@CacheEvict`. For cross-service stale
   data: event-driven invalidation (Kafka
   `ProductUpdated` event) or accept TTL-based
   eventual consistency.

**Interview one-liner:**
"Distributed caching in microservices: shared
cache (Redis) accessible by all service instances.
Key patterns: Cache-Aside (app checks cache, loads
DB on miss, stores with TTL - most common), Write-
Through (update cache + DB on write - strong
consistency). Critical failures: cache stampede
(all keys expire simultaneously -> thundering
herd on DB; fix: TTL jitter), stale data (TTL too
long; fix: shorter TTL or event-driven invalidation).
Key uses: session state for stateless services,
rate limiting (Redis INCR), DB query result caching,
inter-service call result caching."

---

### 💡 The Surprising Truth

The most common caching mistake is not a technical
one - it's a monitoring gap. Teams add Redis caching
and see response time improve. They stop thinking
about the cache. Two months later: Redis memory
is full (eviction policy: `noeviction`), Redis
starts returning errors, service falls back to DB,
DB is now handling traffic it hasn't handled in
2 months (not provisioned for it), and the service
goes down. The fix: set `maxmemory-policy allkeys-lru`
(for cache use cases) and monitor:
`redis_memory_used_bytes / redis_memory_max_bytes`.
Alert at 80% memory usage. Also: monitor cache
hit rate (`keyspace_hits / (keyspace_hits +
keyspace_misses)`). A hit rate < 80% means the
cache isn't helping - either TTL is too short
or cached keys don't match actual access patterns.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **CACHE-ASIDE** Implement cache-aside for
   product-service using Spring `@Cacheable` and
   Redis. Add `@CacheEvict` on update. Configure
   TTL of 1 hour with 5-minute jitter. Write
   a unit test that verifies cache is called
   on first request, cache hit on second, and
   cache evicted after update.
2. **STAMPEDE FIX** Given a stampede scenario:
   implement distributed locking with Redis
   SETNX. Test: simulate 100 concurrent requests
   when cache is empty; verify DB called exactly
   once (not 100 times).
3. **REDIS DATA STRUCTURES** Implement rate
   limiting using Redis sorted sets (sliding
   window algorithm): ZADD, ZRANGEBYSCORE,
   ZREMRANGEBYSCORE. Handle 100 requests/60s
   per user. Test with concurrent users.
4. **CACHE INVALIDATION** Design cross-service
   cache invalidation: product-service publishes
   `ProductUpdated` Kafka event; order-service
   subscribes and evicts its product cache.
   What happens if the Kafka event is lost
   (at-most-once delivery)? How do you handle this?
5. **REDIS CLUSTER** Design the Redis Cluster
   configuration for a 10,000 req/s service:
   how many shards, how many replicas per shard,
   what failover time? Calculate memory needed
   for 500,000 product objects (average 2KB).

---

### 🧠 Think About This Before We Continue

**Q1.** Your microservice uses cache-aside with
Redis, TTL 1 hour, for product data. The pricing
team runs a flash sale: all prices reduced by
30% for 15 minutes. They update prices in
the DB. But: some users see old prices (cached
values) for up to 1 hour. The pricing team:
complains. What are your options? List at least
4 strategies, with the trade-off of each
(performance vs consistency vs operational
complexity).

**Q2.** You have 3 services (order-service,
cart-service, product-service) that all cache
product data independently in Redis (each with
their own cache keys and TTLs). A product is
updated. How many cache entries need to be
invalidated? How do you coordinate invalidation
across 3 services? Is event-driven invalidation
(Kafka `ProductUpdated`) the right approach?
What's the failure scenario if the Kafka consumer
for cache invalidation is down for 30 minutes?

**Q3.** Redis is down (network partition). Your
payment-service uses Redis for: (1) session
store, (2) rate limiting, (3) product cache.
For each of the 3 use cases: what is the
behavior when Redis is unavailable? What
should the fallback be? Which failure is
critical (payment must be blocked) vs tolerable
(degrade gracefully)?