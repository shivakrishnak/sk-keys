---
layout: default
title: "Read-Through"
parent: "Caching"
grand_parent: "Technical Dictionary"
nav_order: 7
permalink: /caching/read-through/
id: CCH-007
category: Caching
difficulty: ★★☆
depends_on: Cache-Aside, Caching, Redis Data Structures
used_by: System Design, Microservices
related: Cache-Aside, Write-Through, Cache Invalidation
tags:
  - caching
  - read-through
  - transparent-cache
  - redis
---

# CCH-007 - Read-Through

⚡ TL;DR - Read-Through is a caching pattern where the **cache itself** sits between the application and the database - the app only ever queries the cache; on a miss, the **cache library/proxy** fetches from the database, populates itself, and returns the result; the application has zero database awareness and zero explicit cache-population code.

| #477            | Category: Caching                              | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------- | :-------------- |
| **Depends on:** | Cache-Aside, Caching, Redis Data Structures    |                 |
| **Used by:**    | System Design, Microservices                   |                 |
| **Related:**    | Cache-Aside, Write-Through, Cache Invalidation |                 |

---

### 🔥 The Problem This Solves

**CACHE-ASIDE REQUIRES EXPLICIT CACHE MANAGEMENT:**
With Cache-Aside, every service that reads data must implement: check cache → miss → fetch DB → populate cache → return. This boilerplate is repeated across every service. If a developer forgets the cache check, that endpoint bypasses the cache silently. If the cache population logic is inconsistent (different TTLs, serialization formats), the cache becomes unreliable.

**READ-THROUGH CENTRALIZES CACHE LOGIC:**
The cache is the only entity the application talks to. The cache's internal loader handles DB fetching. Application code is just: `cache.get(key)` - no cache-miss handling, no DB calls, no population logic. Consistent TTL and serialization are enforced by the cache configuration, not by each developer.

---

### 📘 Textbook Definition

**Read-Through** is a caching pattern where the cache acts as a **transparent intermediary** between the application and the database. When the application requests data, it always queries the cache. On a **cache hit**, the cache returns the data immediately. On a **cache miss**, the cache automatically loads the data from the primary data store (using a configured **CacheLoader** or **CacheEntryReader**), stores it, and returns it to the application. The application never directly queries the database - it only sees the cache. Implementations: **Caffeine** (Java in-process cache with `CacheLoader`), **Spring Cache** with `@Cacheable` (acts as read-through), **Ehcache** with configured read-through loaders, **AWS ElastiCache** with custom loaders, **JCache (JSR-107)** `CacheLoader` interface. Read-Through is commonly combined with **Write-Through** for a fully cache-managed data access layer.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
App calls cache.get(key) - always. On miss, the cache itself fetches from DB, stores, and returns - the app never knows about the DB.

**One analogy:**

> A personal assistant (cache) handles all your information lookups. You ask: "What's the weather in Berlin?" (cache.get). If they know (hit), they tell you instantly. If they don't know (miss), they look it up on their own (DB fetch), write it in their notes (cache population), and tell you. You never open a browser yourself - the assistant handles all lookups and remembers results.

- "You ask the assistant" → app calls `cache.get(key)`
- "They know" → cache hit → return immediately
- "They look it up" → CacheLoader → DB fetch
- "Write in notes" → cache populate
- "You never open a browser" → application has zero direct DB code

**One insight:**
Read-Through's key advantage over Cache-Aside is **transparency** - application code has no cache awareness. This is powerful for retrofitting caching onto existing codebases: add a read-through cache in front of the repository layer, and every read is cached without touching service logic. The tradeoff: the first caller still waits for the DB fetch on a miss - Read-Through doesn't eliminate miss latency, it just moves the miss-handling responsibility to the cache layer.

---

### 🔩 First Principles Explanation

**CAFFEINE READ-THROUGH (IN-PROCESS CACHE):**

```java
// Caffeine: high-performance in-process cache with CacheLoader
@Configuration
public class CacheConfig {

    @Bean
    public LoadingCache<String, Product> productCache(ProductRepository repo) {
        return Caffeine.newBuilder()
            .maximumSize(10_000)           // max entries in memory
            .expireAfterWrite(10, MINUTES) // TTL: evict after 10 min from write
            .expireAfterAccess(5, MINUTES) // also evict if not accessed for 5 min
            .recordStats()                  // enable hit/miss stats
            .build(key -> {                // CacheLoader: automatically called on miss
                // This is the Read-Through loader:
                // cache calls this when key is not found
                return repo.findById(key)
                    .orElseThrow(() -> new ProductNotFoundException(key));
            });
    }
}

@Service
public class ProductService {
    private final LoadingCache<String, Product> productCache;

    // Application code: NO cache-miss handling, NO DB calls
    public Product getProduct(String productId) {
        return productCache.get(productId);
        // On hit: returns instantly from Caffeine in-memory cache (< 0.1ms)
        // On miss: Caffeine calls CacheLoader → repo.findById → stores → returns
        // App doesn't know if it was a hit or miss
    }

    // Monitoring cache stats
    @Scheduled(fixedDelay = 60_000)
    public void logCacheStats() {
        CacheStats stats = productCache.stats();
        log.info("Product cache: hitRate={}, missRate={}, loadCount={}, avgLoadTime={}ms",
            stats.hitRate(), stats.missRate(),
            stats.loadCount(), stats.averageLoadPenalty() / 1_000_000);
    }
}
// Caffeine.stats: hitRate should be > 0.90 for effective caching
// avgLoadPenalty: average DB fetch time on cache miss (should match DB query latency)
```

**SPRING CACHE + REDIS (READ-THROUGH PATTERN):**

```java
// Spring @Cacheable acts as read-through when combined with Redis
@Service
public class UserService {

    @Cacheable(
        value = "users",              // cache name (maps to Redis key prefix)
        key = "#userId",              // cache key
        unless = "#result == null"    // don't cache null results
    )
    public User getUser(Long userId) {
        // Spring: checks Redis first
        // Cache hit: returns from Redis, method body NOT called
        // Cache miss: method body IS called → result stored in Redis → returned
        return userRepository.findById(userId)
            .orElse(null);
    }

    @CacheEvict(value = "users", key = "#userId")
    public void deleteUser(Long userId) {
        userRepository.deleteById(userId);
        // @CacheEvict: removes users:{userId} from Redis after method
    }

    @CachePut(value = "users", key = "#result.id")
    public User updateUser(Long userId, UserUpdateRequest req) {
        // @CachePut: ALWAYS executes method AND updates cache
        // Useful for write-through (keep cache updated on every write)
        User user = userRepository.findById(userId).orElseThrow();
        user.setEmail(req.getEmail());
        return userRepository.save(user);
    }
}
```

**REDIS AS READ-THROUGH PROXY (EXTERNAL CACHE):**

```
When Redis is used as an external distributed cache with a sidecar or proxy
that auto-loads on miss:

Application → Redis GET user:42
  HIT: Redis returns data directly
  MISS: Redis proxy → DB query → Redis SET user:42 {data} EX 600 → return to app

This architecture (Redis + DB loader) is what managed services like:
- AWS DAX (DynamoDB Accelerator): Read-Through + Write-Through for DynamoDB
- AWS ElastiCache (Cluster Mode): application configures client-side read-through
  (ElastiCache itself doesn't auto-load - that's the CacheLoader in app code)

True infrastructure-level read-through:
- DAX: DynamoDB requests go to DAX; on miss, DAX fetches DynamoDB, caches, returns
- App never knows about DynamoDB - only DAX endpoint
- API identical to DynamoDB → zero code change needed
```

---

### 🧪 Thought Experiment

**WHAT HAPPENS IF THE CACHELOADER THROWS AN EXCEPTION?**

Scenario: CacheLoader calls `repo.findById(key)`, but the database is temporarily unavailable (connection timeout). CacheLoader throws `DataAccessException`.

**Caffeine behavior:** Caffeine propagates the exception to the caller. The key is NOT stored in the cache (failed loads don't cache the failure). On the next `cache.get(key)` call, Caffeine tries the CacheLoader again.

**Implication:** If the database is down, every `cache.get(key)` for a cold key will attempt the DB and fail - no fallback. For systems where availability > consistency, you'd want to: (1) catch exceptions in the CacheLoader and return a fallback value (stale value from a secondary cache?), or (2) use `cache.getIfPresent(key)` first (doesn't trigger CacheLoader) and fall back to DB call in app code - which is Cache-Aside again.

**The tradeoff:** Read-Through's transparency comes at the cost of control over fallback behavior. Cache-Aside gives explicit control over what happens on miss and on loader failure.

---

### 🧠 Mental Model / Analogy

> Read-Through is like a librarian who manages your book requests. You ask for any book by title. The librarian checks their desk shelf (cache). If found, they hand it over. If not, they go to the back storeroom (database), bring it back, put it on the desk shelf for next time, and hand it to you. You never go to the storeroom - you always just ask the librarian. The librarian owns the fetching and caching logic; you just make requests.

- "Librarian" → CacheLoader / cache layer
- "Desk shelf" → in-process cache (Caffeine) or Redis
- "Storeroom" → database
- "You never go to storeroom" → application never calls DB directly
- "Librarian owns logic" → Read-Through centralizes cache management

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Read-Through: app queries cache only. Cache fetches from DB on miss, stores, returns. App has no DB code. Compare to Cache-Aside: app queries cache, then DB on miss, then populates cache manually.

**Level 2:** Use Caffeine for in-process read-through (JVM-local, zero network latency, bounded by JVM heap). Use Spring `@Cacheable` with Redis for distributed read-through (multi-instance apps need shared cache). Configure `recordStats()` on Caffeine and monitor hit rate. For Spring Redis: configure `RedisCacheManager` with per-cache TTL configuration.

**Level 3:** Caffeine CacheLoader vs. AsyncCacheLoader: synchronous loader blocks the calling thread during DB fetch; async loader uses a separate thread pool, returning `CompletableFuture`. For high-concurrency applications, `AsyncLoadingCache` prevents thread starvation during cache misses: all callers for the same key wait for the same future (de-duplication), and the calling threads are not blocked (they can serve other requests). `cache.getAll(keys)` with `CacheLoader.loadAll()` for bulk loading - more efficient than N individual `get()` calls (single DB query for multiple keys).

**Level 4:** Read-Through is the implementation pattern for what database researchers call a "look-aside cache with auto-fill." The key systems property: the cache becomes the authoritative read path - the application's perception of the data is determined by what the cache returns, not directly by the database. This means: (1) Stale-while-revalidate semantics become possible (return slightly stale data while reloading asynchronously - Caffeine `refreshAfterWrite`). (2) The cache can implement read-repair (detect stale reads by comparing cache TTL to DB `updated_at` timestamp). (3) Circuit breaker pattern on the CacheLoader: if DB is failing, return cached (possibly stale) data instead of propagating errors - a controlled degradation strategy. The combination of Read-Through + `refreshAfterWrite` + circuit breaker forms a resilient read path that tolerates DB unavailability without application-layer changes.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ READ-THROUGH vs CACHE-ASIDE                          │
├──────────────────────────────────────────────────────┤
│                                                      │
│ CACHE-ASIDE:                                         │
│   App → Redis GET → miss                             │
│   App → DB SELECT → result                           │
│   App → Redis SET (populate)                         │
│   App returns result                                 │
│   (App touches both Redis and DB)                    │
│                                                      │
│ READ-THROUGH:                                        │
│   App → CacheLoader.get(key) → miss                  │
│   CacheLoader → DB SELECT → result   [internal]      │
│   CacheLoader → cache.set (populate) [internal]      │
│   App ← CacheLoader returns result                   │
│   (App only touches cache - DB is invisible)         │
│                                                      │
│ [READ-THROUGH ← YOU ARE HERE: CacheLoader abstraction]
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**ORDER SERVICE WITH CAFFEINE READ-THROUGH:**

```
Request: GET /orders/98765
→ OrderService.getOrder("98765")
→ [READ-THROUGH ← YOU ARE HERE: orderCache.get("98765")]

1st call (cold cache):
→ Caffeine: key "98765" not in cache → trigger CacheLoader
→ CacheLoader: orderRepository.findById("98765")
→ PostgreSQL: SELECT * FROM orders WHERE id = 98765 → {order data}
→ CacheLoader: stores in Caffeine (TTL 10 min) → returns to app
→ App returns {order data} - 22ms (DB read time)

Calls 2–50,000 within 10 minutes:
→ Caffeine: key "98765" in cache → return immediately
→ App returns {order data} - 0.05ms (in-process memory, no Redis needed)

After 10 minutes (TTL expires):
→ Next call: Caffeine: "98765" expired → CacheLoader triggered again
→ DB fetch: gets current order state (handles any background updates)
→ Cache refreshed with fresh data

Order status updated (to SHIPPED):
→ Application: orderCache.invalidate("98765")
   OR: use refreshAfterWrite - next access auto-reloads
→ Next call: CacheLoader fetches SHIPPED status from DB ✓
```

---

### ⚖️ Comparison Table

| Aspect                 | Read-Through                           | Cache-Aside                       |
| ---------------------- | -------------------------------------- | --------------------------------- |
| App code complexity    | Minimal (no explicit cache code)       | More verbose (check + populate)   |
| DB awareness in app    | None (transparent)                     | Explicit (app queries DB on miss) |
| Cache miss handling    | Automatic (CacheLoader)                | Manual (app handles)              |
| Fallback on DB failure | Depends on CacheLoader error handling  | App can implement custom fallback |
| Stale-while-revalidate | Supported (Caffeine refreshAfterWrite) | Requires manual implementation    |
| Cold start behavior    | First caller waits for DB              | First caller waits for DB (same)  |

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                                                                                                                  |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Read-Through eliminates cache misses"                   | Read-Through still experiences cache misses - it just handles them automatically inside the cache layer. The caller still waits for the DB fetch on a miss                                                               |
| "Read-Through and Cache-Aside have the same performance" | For single instances with in-process caches (Caffeine), Read-Through is faster per-hit (no Redis RTT). For distributed apps with Redis, performance is similar since both require a Redis call                           |
| "Spring @Cacheable is not Read-Through"                  | `@Cacheable` IS the Read-Through pattern: it intercepts method calls, checks Redis, and on miss, calls the method body (which fetches from DB), stores the result in Redis, and returns - exactly Read-Through semantics |

---

### 🚨 Failure Modes & Diagnosis

**1. CacheLoader Blocking Thread Pool Exhaustion**

**Symptom:** Under load, all application threads are stuck at `productCache.get(id)`. Thread dump shows: all threads waiting in Caffeine CacheLoader → JDBC driver → waiting for DB connection. Application is unresponsive.

**Root Cause:** Caffeine's synchronous `LoadingCache`: each cache miss blocks the calling thread. 100 concurrent misses = 100 threads blocked on DB. If all threads are blocked (thread pool saturated), new requests cannot be served.

**Fix:**

```java
// Use AsyncLoadingCache to avoid blocking:
AsyncLoadingCache<String, Product> cache = Caffeine.newBuilder()
    .maximumSize(10_000)
    .expireAfterWrite(10, MINUTES)
    .buildAsync(key -> {
        // Runs on ForkJoinPool.commonPool() or configurable Executor
        return productRepository.findById(key)
            .orElseThrow(() -> new ProductNotFoundException(key));
    });

// Calling code:
CompletableFuture<Product> future = cache.get(productId);
// Calling thread is NOT blocked - can serve other requests while DB loads
```

---

### 🔗 Related Keywords

**Prerequisites:** Cache-Aside, Caching, Redis Data Structures
**Builds On This:** System Design, Microservices
**Related:** Cache-Aside, Write-Through, Cache Invalidation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PATTERN     │ App → cache only; cache auto-loads from DB │
│ CODE        │ cache.get(key) - no DB calls in app code   │
│ MISS        │ CacheLoader: DB fetch → cache populate     │
│ IN-PROCESS  │ Caffeine LoadingCache (sub-millisecond hit) │
│ DISTRIBUTED │ Spring @Cacheable + Redis                  │
│ MONITOR     │ Caffeine.stats().hitRate() > 0.90          │
│ TRANSPARENT │ App has zero DB awareness (best for ORMs)  │
│ ONE-LINER   │ "Cache is the only data source - miss means │
│             │  cache fetches DB itself, not the app"      │
│ NEXT EXPLORE│ Write-Through → Write-Behind               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Question) You are adding caching to a product catalog service that serves 100,000 read requests/second for 500,000 unique products, with a long-tail access pattern (20% of products = 80% of reads). Design: (a) in-process vs. distributed cache trade-off, (b) cache size and TTL choices, (c) which Spring/Caffeine features to use, (d) what monitoring to add.

**Q2.** (TYPE D - Failure Scenario) A Caffeine `LoadingCache` is configured with `refreshAfterWrite(5, MINUTES)`. Production shows: DB query rate increases suddenly at exactly 5-minute intervals. Memory usage is stable. No cache misses in logs. Diagnose: what Caffeine behavior is causing this? Is this a bug or expected behavior? How do you tune it?
