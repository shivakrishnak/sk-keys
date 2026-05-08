---
layout: default
title: "Cache-Aside"
parent: "Caching"
grand_parent: "Technical Dictionary"
nav_order: 6
permalink: /caching/cache-aside/
id: CCH-006
category: Caching
difficulty: ★★☆
depends_on: Caching, Redis Data Structures, Database Fundamentals
used_by: System Design, Microservices, API Caching
related: Read-Through, Write-Through, Cache Invalidation
tags:
  - caching
  - cache-aside
  - lazy-loading
  - redis
---

# CCH-006 - Cache-Aside

⚡ TL;DR - Cache-Aside (lazy loading) is the most common caching pattern: the **application** checks the cache first; on a miss, the application fetches from the database, populates the cache, and returns the result; the cache is **side-loaded** by the application, not by the cache infrastructure - giving the application full control over what gets cached and when.

| #476            | Category: Caching                                     | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------- | :-------------- |
| **Depends on:** | Caching, Redis Data Structures, Database Fundamentals |                 |
| **Used by:**    | System Design, Microservices, API Caching             |                 |
| **Related:**    | Read-Through, Write-Through, Cache Invalidation       |                 |

---

### 🔥 The Problem This Solves

**EVERY DATABASE READ IS EXPENSIVE:**
Without caching, every API call that reads data hits the database: network round trip, disk I/O, query execution, row serialization. A popular product page with 1,000 concurrent users = 1,000 database reads per second for identical data. The database becomes the bottleneck.

**CACHE-ASIDE MAKES READS CHEAP:**
Popular items are read once from the database and cached for hundreds of subsequent reads. The database only sees the initial miss and writes - not the 99% of reads that are cache hits.

---

### 📘 Textbook Definition

**Cache-Aside** (also called **Lazy Loading** or **Demand-Fill**) is a caching pattern where the application code is responsible for loading data into the cache on demand. The application first queries the cache; if the data is not present (cache miss), the application retrieves it from the primary data store, writes it to the cache (with a TTL), and returns it to the caller. On subsequent reads, the data is found in cache (cache hit) and returned without touching the database. On writes: most implementations update the database and **invalidate** (delete) the cached entry - so the next read re-populates the cache from the fresh database value. Cache-Aside is the most widely used caching pattern (implemented by Spring Cache `@Cacheable`, Django cache framework, Rails `Rails.cache.fetch`).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Look in cache first; if absent, fetch from DB, store in cache, return - the application writes to both cache and DB manually.

**One analogy:**

> You want to look up a phone number. First, check your own notebook (cache). Found? Great, use it. Not found? Look up the phone book (database), write the number in your notebook, and use it. Next time: notebook hit, no phone book needed.

- "Check notebook" → Redis GET
- "Not found" → cache miss → query database
- "Write in notebook" → Redis SET with TTL
- "Next time: notebook hit" → Redis GET returns value (cache hit)
- "Phone book" → primary database

**One insight:**
Cache-Aside means the cache is **populated on demand**, not proactively. Cold start problem: on server restart, the cache is empty - the first requests for every resource miss the cache and hit the database. This is especially problematic during traffic spikes after a deployment. Solution: **cache warming** (pre-populate on startup) or **graceful warm-up** (route traffic gradually after deploy).

---

### 🔩 First Principles Explanation

**THE THREE-STEP READ FLOW:**

```java
// Spring Boot: manual Cache-Aside (without @Cacheable annotation)
@Service
public class ProductService {

    private static final Duration TTL = Duration.ofMinutes(10);

    public Product getProduct(String productId) {
        // Step 1: Check cache
        String cacheKey = "product:" + productId;
        Product cached = redisTemplate.opsForValue()
            .get(cacheKey, Product.class);

        if (cached != null) {
            return cached;  // ← CACHE HIT: return immediately (1ms)
        }

        // Step 2: Cache miss → fetch from database (~20ms)
        Product product = productRepository.findById(productId)
            .orElseThrow(() -> new ProductNotFoundException(productId));

        // Step 3: Populate cache for future reads
        redisTemplate.opsForValue().set(cacheKey, product, TTL);

        return product;  // ← CACHE MISS: populated for next caller
    }

    // On write: update DB and invalidate cache
    @Transactional
    public Product updateProduct(String productId, ProductUpdateRequest req) {
        // Update DB first (source of truth)
        Product product = productRepository.findById(productId).orElseThrow();
        product.setPrice(req.getPrice());
        product.setDescription(req.getDescription());
        productRepository.save(product);  // DB commit

        // Invalidate cache (delete, not update - avoids race conditions)
        redisTemplate.delete("product:" + productId);

        return product;
    }
}

// With @Cacheable (Spring Cache abstraction):
@Service
public class ProductServiceAnnotated {

    @Cacheable(value = "products", key = "#productId",
               unless = "#result == null")
    public Product getProduct(String productId) {
        return productRepository.findById(productId).orElse(null);
        // Spring Cache: automatically check cache before calling method body
        //               automatically populate cache with result
    }

    @CacheEvict(value = "products", key = "#productId")
    @Transactional
    public Product updateProduct(String productId, ProductUpdateRequest req) {
        // @CacheEvict: automatically delete from cache after method executes
        Product product = productRepository.findById(productId).orElseThrow();
        product.setPrice(req.getPrice());
        return productRepository.save(product);
    }
}
```

**RACE CONDITION: STALE DATA WINDOW:**

```
Thread A: cache miss → fetching from DB...
Thread B: writes to DB → invalidates cache
Thread A: ...DB fetch returns OLD value → writes OLD value to cache
Result: stale cache entry (Thread B's update is not reflected)

Duration: seconds (between Thread B's write and Thread A's cache set)
Impact: low to medium (bounded by time between operations, not long-lived)

Fix 1: short TTL - stale entry expires quickly (accept brief inconsistency)
Fix 2: use "delete then re-fetch" on write (Thread B deletes; next GET re-fetches fresh)
Fix 3: distributed lock on cache key during re-population (prevents multiple simultaneous misses)

Most production systems accept the brief stale window (seconds) as a reasonable tradeoff
vs. the complexity of fully consistent cache invalidation.
```

---

### 🧪 Thought Experiment

**WHAT IF EVERY WRITE ALSO WRITES TO CACHE (INSTEAD OF INVALIDATING)?**

Scenario: instead of deleting the cache key on write, update it directly: `updateProduct(id, req)` → save to DB → `redis.set("product:id", updatedProduct)`.

**Problem:** Two writers update the same product concurrently:

- Writer A: writes version 2 to DB, then writes version 2 to cache
- Writer B: writes version 3 to DB, then writes version 3 to cache (but B's DB write happened after A's)

If there's a race between the cache writes (A's cache write happens AFTER B's), cache shows version 2 but DB has version 3. The cache is permanently incorrect until TTL expires.

**The "invalidate instead of update" rule:** deleting the cache entry is always safe - the next read re-fetches the current state from the database, which is always correct. Writing to the cache on update introduces a race between the DB commit order and the cache write order.

---

### 🧠 Mental Model / Analogy

> Cache-Aside is the "bring your own lunch" caching strategy. The cafeteria (database) always has food, but it's slow and expensive. Smart employees bring leftovers in their lunchbox (cache) from yesterday's meal. If the lunchbox is empty (miss), they go to the cafeteria, eat there, and pack tomorrow's lunch from the same meal (populate). If the meal recipe changes (data update), they throw out the old leftovers (invalidate) so tomorrow they fetch the fresh version.

- "Lunchbox" → Redis cache
- "Cafeteria" → database
- "Empty lunchbox" → cache miss
- "Pack tomorrow's lunch" → Redis SET with TTL
- "Recipe changes" → data update → `Redis.delete(key)` (invalidate)

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Cache-Aside: check cache → miss → read DB → write cache → return. On updates: write DB + delete from cache. Simple, app-controlled, and widely used.

**Level 2:** Use Spring `@Cacheable` / `@CacheEvict` to automate. Set appropriate TTL (too short = frequent DB hits; too long = stale data). Use namespaced keys (`entity:id`) for clarity. Warm the cache on startup for frequently accessed hot data. Monitor hit ratio (aim for > 90% for read-heavy endpoints).

**Level 3:** Key design matters for cache efficiency. Use structured keys: `product:{id}`, `user:{id}:profile`. Avoid wide cache keys that hold aggregated views (hard to invalidate granularly). For lists (`user:42:orders`): cache the full list, invalidate on any order change for user 42. Consider cache key versioning for schema changes: `product:v2:{id}` - increment version when product schema changes, avoids stale deserialization errors. Redis OBJECT ENCODING + OBJECT IDLETIME + OBJECT FREQ to audit cache usage per key.

**Level 4:** Cache-Aside is the dominant pattern in systems that favor simplicity over consistency. The core tradeoff: the cache is a best-effort read accelerator, not an authoritative data store. If Redis is down, the application degrades gracefully (falls through to the database) rather than failing - because the database remains the source of truth. Compare to Read-Through (where the cache is an authoritative intermediary and the app never talks to the DB directly): Cache-Aside gives the application more control and better error handling at the cost of more boilerplate. At extreme scale, Cache-Aside with Redis Cluster (consistent hashing, 16,384 hash slots) can serve millions of reads per second with sub-millisecond latency - the application never hits the database for hot data.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ CACHE-ASIDE READ FLOW                                │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Request: GET /products/42                            │
│     │                                                │
│     ▼                                                │
│ App: Redis GET product:42                            │
│     │                                                │
│     ├── HIT ──► return cached value (1-5ms)          │
│     │                                                │
│     └── MISS ──► DB: SELECT * FROM products          │
│                  WHERE id = 42 (~20ms)               │
│                      │                               │
│                      ▼                               │
│                  Redis SET product:42 {data}         │
│                  TTL = 10 minutes                    │
│                      │                               │
│                      ▼                               │
│                  return value to caller              │
│                                                      │
│ WRITE FLOW: PUT /products/42                         │
│     │                                                │
│     ▼                                                │
│ DB: UPDATE products SET ... WHERE id = 42            │
│     │                                                │
│     ▼                                                │
│ Redis: DEL product:42  (invalidate, don't update)    │
│     │                                                │
│     ▼                                                │
│ return updated product                               │
│ (next GET will re-populate cache from fresh DB read) │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**PRODUCT CATALOG API WITH CACHE-ASIDE:**

```
User: GET /api/products/12345 → Product Service

1st request (cache cold):
→ Redis: GET product:12345 → nil (MISS)
→ PostgreSQL: SELECT * FROM products WHERE id = 12345 → {id:12345, name:"Widget", price:9.99}
→ Redis: SET product:12345 '{"id":12345,...}' EX 600 (10 min TTL)
→ Response: 200 OK {product} - 22ms total

Requests 2-10000 (cache warm):
→ Redis: GET product:12345 → {id:12345,...} (HIT)
→ Response: 200 OK {product} - 2ms total (11× faster)

Admin update: PUT /api/products/12345 {price: 12.99}
→ PostgreSQL: UPDATE products SET price=12.99 WHERE id=12345 - COMMIT
→ Redis: DEL product:12345 (invalidate)
→ Response: 200 OK

Next request after update:
→ Redis: GET product:12345 → nil (MISS - just invalidated)
→ PostgreSQL: SELECT - returns price=12.99 (fresh)
→ Redis: SET product:12345 '{"price":12.99,...}' EX 600
→ Response: 200 OK {price: 12.99} ✓
```

---

### ⚖️ Comparison Table

| Aspect              | Cache-Aside                     | Read-Through                   | Write-Through                     |
| ------------------- | ------------------------------- | ------------------------------ | --------------------------------- |
| Who loads cache     | Application                     | Cache library                  | Cache library (on write)          |
| Cache miss handling | App fetches DB, populates cache | Cache fetches DB automatically | N/A (data pre-populated on write) |
| Application code    | Explicit cache check            | Transparent (no cache code)    | Explicit write to cache/DB        |
| Cold start          | Empty cache on restart          | Empty cache on restart         | Cache pre-populated on writes     |
| Consistency         | Eventual (invalidation delay)   | Eventual                       | Strong (cache = DB on writes)     |

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                                          |
| ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Cache-Aside and Read-Through are the same"       | Read-Through: cache sits between app and DB - app never queries DB directly. Cache-Aside: app queries cache OR DB directly. Cache-Aside is explicit; Read-Through is transparent |
| "Update cache on write (instead of invalidating)" | Write-to-cache on update risks stale cache due to race conditions between concurrent writers. Invalidation (delete) is safer: the next read always gets fresh DB data            |
| "Cache-Aside guarantees no stale reads"           | Cache-Aside does NOT guarantee freshness. Between a DB write and cache invalidation, other requests may get stale data. TTL is the fallback safety net                           |

---

### 🚨 Failure Modes & Diagnosis

**1. Cache Stampede on Miss (Thundering Herd)**

**Symptom:** After Redis cache eviction (or restart), 1,000 concurrent requests all miss the cache simultaneously and all hit the database. Database CPU spikes to 100%, requests time out.

**Fix:**

```java
// Mutex/lock: only one thread re-populates; others wait
String lockKey = "lock:product:" + productId;
Boolean locked = redisTemplate.opsForValue()
    .setIfAbsent(lockKey, "1", Duration.ofSeconds(5));

if (Boolean.TRUE.equals(locked)) {
    // Winner: fetch from DB and populate cache
    Product product = productRepository.findById(productId).orElseThrow();
    redisTemplate.opsForValue().set("product:" + productId, product, Duration.ofMinutes(10));
    redisTemplate.delete(lockKey);
    return product;
} else {
    // Loser: wait briefly and retry (cache should be populated by winner)
    Thread.sleep(50);
    return getProduct(productId);  // retry - should be cache hit now
}
```

---

### 🔗 Related Keywords

**Prerequisites:** Caching, Redis Data Structures, Database Fundamentals
**Builds On This:** System Design, Microservices
**Related:** Read-Through, Write-Through, Cache Invalidation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PATTERN     │ App checks cache → miss → DB → populate    │
│ WRITE       │ Update DB → DEL cache key (invalidate)     │
│ MISS RISK   │ Cold start → all requests miss → DB spike  │
│ STALE RISK  │ DB write → cache not yet invalidated       │
│ FIX STALE   │ Short TTL + immediate invalidation on write│
│ SPRING      │ @Cacheable + @CacheEvict annotations        │
│ HIT RATIO   │ Target > 90% for read-heavy endpoints      │
│ ONE-LINER   │ "Check cache first; miss → DB → fill cache"│
│ NEXT EXPLORE│ Read-Through → Write-Through → Write-Behind│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE D - Failure Scenario) Your Redis cluster unexpectedly evicts 30% of cached keys simultaneously (memory pressure, `maxmemory-policy allkeys-lru`). Your application uses Cache-Aside. Describe the cascade: what happens to database load, API latency, and user experience? What monitoring would catch this early? What mitigation strategies would you implement?

**Q2.** (TYPE F - Comparison) A search feature returns a list of 100 product IDs matching a query. You want to cache these search results. Design: (a) the cache key strategy, (b) what happens when any one of the 100 products in the list is updated, (c) how Cache-Aside handles this invalidation problem, (d) what alternative caching strategy would be more appropriate for search result lists.
