---
layout: default
title: "Cache-Aside vs Read-Through Comparison"
parent: "Caching"
nav_order: 16
permalink: /caching/cache-aside-vs-read-through/
number: "CCH-016"
category: Caching
difficulty: ★★★
depends_on: Cache-Aside, Read-Through, Write-Through, Write-Around
used_by: System Design, Caching
related: Cache-Aside, Read-Through, Write-Through
tags:
  - caching
  - cache-aside
  - read-through
  - comparison
  - deep-dive
---

# CCH-016 — Cache-Aside vs Read-Through Comparison

⚡ TL;DR — Cache-Aside puts the **application in control**: the app checks the cache, loads from DB on miss, and populates the cache — flexible but verbose; Read-Through delegates cache loading to the **cache layer itself** (CacheLoader/LoadingCache): the app just calls `cache.get(key)` and the cache auto-loads from DB on miss — cleaner but less flexible for complex fallback logic.

| #491            | Category: Caching                                      | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | Cache-Aside, Read-Through, Write-Through, Write-Around |                 |
| **Used by:**    | System Design, Caching                                 |                 |
| **Related:**    | Cache-Aside, Read-Through, Write-Through               |                 |

---

### 🔥 The Problem This Solves

**WHICH PATTERN TO USE — AND WHEN:**
Most caching resources describe Cache-Aside and Read-Through separately. In practice, the choice between them affects: how much boilerplate is in the application code, where fallback and error handling lives, whether Spring `@Cacheable` is sufficient, and how cold start behavior is handled. Without a clear comparison, engineers default to whichever pattern they first learned — often Cache-Aside — even when Read-Through would simplify their codebase.

---

### 📘 Textbook Definition

**Cache-Aside (Lazy Loading)**: The application is responsible for all cache interactions. On read: check cache → if miss, load from DB → put in cache → return. On write: update DB → delete (or update) cache. The cache is unaware of the data source.

**Read-Through**: The cache is configured with a `CacheLoader` — a function/callback that knows how to load data from the source. On read: `cache.get(key)` → if miss, cache calls the loader → loads from DB → stores in cache → returns value. The application only calls `cache.get(key)` — it never directly queries the database for cached reads.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Cache-Aside: app does the DB lookup on cache miss. Read-Through: cache does the DB lookup on cache miss (via configured loader). Same outcome; different responsibility placement.

**One analogy:**

> Two ways to order food: (Cache-Aside) You check the fridge yourself. If empty, you drive to the store, buy groceries, bring them home, put in fridge, then eat. (Read-Through) You tell your kitchen assistant: "I want eggs." The assistant checks the fridge. If empty, the assistant goes to the store, buys eggs, puts them in the fridge, and brings them to you. You only said "I want eggs" — the fetch logic is the assistant's responsibility.

- "Check fridge yourself" → app checks cache
- "Drive to store yourself" → app queries DB directly on cache miss
- "Kitchen assistant fetches" → CacheLoader fetches DB on cache miss
- "Just say 'I want eggs'" → just call `cache.get(key)` in app code

**One insight:**
Spring `@Cacheable` is **Read-Through semantics** — the developer only declares which method is cacheable; Spring AOP intercepts the call, checks the cache, and if missing, invokes the method (the DB call) and caches the result. The developer doesn't write cache-check-or-load code. Pure Cache-Aside requires the developer to write that logic manually (or use a template like `computeIfAbsent`). For most Spring Boot applications, `@Cacheable` (Read-Through) is the appropriate choice. Manual Cache-Aside is needed when the cache check and DB load have complex conditional logic that annotation-based caching can't express.

---

### 🔩 First Principles Explanation

**CACHE-ASIDE — MANUAL IMPLEMENTATION:**

```java
// Cache-Aside: the application owns the entire read path
@Service
public class ProductServiceCacheAside {

    @Autowired private RedisTemplate<String, Product> redis;
    @Autowired private ProductRepository db;

    public Product getProduct(String id) {
        String key = "product:" + id;

        // Step 1: App checks cache
        Product cached = redis.opsForValue().get(key);
        if (cached != null) {
            return cached;  // Cache HIT
        }

        // Step 2: App loads from DB (app is responsible for this)
        Product product = db.findById(id)
            .orElseThrow(() -> new ProductNotFoundException(id));

        // Step 3: App populates cache
        redis.opsForValue().set(key, product, Duration.ofMinutes(15));

        return product;  // Cache MISS → DB → cache populated
    }

    // WRITE: app explicitly invalidates cache
    @Transactional
    public Product updateProduct(String id, ProductUpdateRequest req) {
        Product updated = db.save(/* ... */);
        redis.delete("product:" + id);  // App controls invalidation
        return updated;
    }

    // Complex conditional caching — Cache-Aside is more flexible here:
    public Product getProductWithFallback(String id) {
        String key = "product:" + id;
        Product cached = redis.opsForValue().get(key);
        if (cached != null) return cached;

        // Complex fallback: try primary DB, then replica, then default
        Product product;
        try {
            product = db.findById(id).orElse(null);
        } catch (DataAccessException e) {
            product = replicaDb.findById(id).orElse(defaultProductService.getDefault());
        }

        // Cache with different TTL based on source
        Duration ttl = (product != null) ? Duration.ofMinutes(15) : Duration.ofMinutes(1);
        redis.opsForValue().set(key, product, ttl);

        return product;
        // This complex logic is NOT expressible with @Cacheable alone
    }
}
```

**READ-THROUGH — CAFFEINE LOADING CACHE:**

```java
// Read-Through: cache configured with a loader; app only calls cache.get(key)
@Configuration
public class CacheConfig {

    @Bean
    public LoadingCache<String, Product> productReadThroughCache(
        ProductRepository db) {

        return Caffeine.newBuilder()
            .maximumSize(10_000)
            .expireAfterWrite(15, TimeUnit.MINUTES)
            .build(key -> {
                // This IS the CacheLoader: invoked automatically on cache miss
                String id = key.replace("product:", "");
                return db.findById(id)
                    .orElseThrow(() -> new ProductNotFoundException(id));
            });
    }
}

@Service
public class ProductServiceReadThrough {

    @Autowired private LoadingCache<String, Product> productCache;

    public Product getProduct(String id) {
        // App only calls this — no DB code here at all
        return productCache.get("product:" + id);
        // If miss: CacheLoader automatically fetches from DB and caches result
        // App is unaware of whether this was a cache hit or miss
    }

    // READ-THROUGH is CLEANER — no if/else, no DB code in service

    // LIMITATION: write invalidation still needs explicit code
    @Transactional
    public Product updateProduct(String id, ProductUpdateRequest req) {
        Product updated = db.save(/* ... */);
        productCache.invalidate("product:" + id);  // Still need explicit eviction
        return updated;
    }
}
```

**READ-THROUGH — SPRING @CACHEABLE (MOST COMMON):**

```java
// Spring @Cacheable = Read-Through semantics via AOP proxy
@Service
public class ProductServiceSpringCacheable {

    @Autowired private ProductRepository db;

    @Cacheable(
        value = "products",
        key = "#id",
        unless = "#result == null"  // Don't cache null (optional; remove for negative caching)
    )
    public Product getProduct(String id) {
        // Spring AOP: before this method runs, checks cache for "products::id"
        // Cache HIT: method BODY IS NOT EXECUTED, cached result returned
        // Cache MISS: method body runs, result is cached, then returned
        // App code has NO cache logic — just the business logic
        return db.findById(id).orElseThrow();
    }

    @CacheEvict(value = "products", key = "#result.id")
    @Transactional
    public Product updateProduct(String id, ProductUpdateRequest req) {
        return db.save(/* ... */);
        // @CacheEvict: after method returns, evict "products::result.id" from cache
    }

    // Async Read-Through (Caffeine AsyncLoadingCache):
    @Bean
    public AsyncLoadingCache<String, Product> asyncProductCache(ProductRepository db) {
        return Caffeine.newBuilder()
            .maximumSize(10_000)
            .expireAfterWrite(15, TimeUnit.MINUTES)
            .buildAsync(id -> db.findById(id).orElseThrow());
            // Returns CompletableFuture<Product> — non-blocking on cache miss
    }

    public CompletableFuture<Product> getProductAsync(String id) {
        return asyncProductCache.get(id);
        // Non-blocking: on miss, DB fetch happens async; caller gets a Future
        // During the fetch: calling thread is not blocked
    }
}
```

**COLD START BEHAVIOR COMPARISON:**

```java
// Cache-Aside cold start:
// First N requests for any key: all cache miss → all hit DB
// Cache populates gradually as different keys are accessed
// Hit rate starts at 0%, grows over time as hot keys are cached

// Read-Through cold start:
// Same as Cache-Aside — first access is always a cache miss
// (CacheLoader is invoked, DB is queried)
// BUT: Read-Through easily pairs with bulk pre-loading:

LoadingCache<String, Product> cache = Caffeine.newBuilder()
    .maximumSize(10_000)
    .expireAfterWrite(15, TimeUnit.MINUTES)
    .build(id -> db.findById(id).orElseThrow());

// Pre-warm: load all top-1000 products before accepting traffic
@PostConstruct
void warmUp() {
    List<String> topIds = db.findTopViewedIds(1000);
    Map<String, Product> warmEntries = db.findAllById(topIds).stream()
        .collect(Collectors.toMap(p -> p.getId(), p -> p));
    cache.putAll(warmEntries);  // Direct putAll — bypasses CacheLoader (efficient warm-up)
}
// After putAll: cache is warm; getProduct() calls will HIT immediately ✓
```

---

### 🧪 Thought Experiment

**CACHE FAILURE: DIFFERENT BEHAVIOR**

The cache (Redis) goes down. What does each pattern do?

**Cache-Aside:** The app's `getProduct()` does `redis.get(key)` → throws `RedisConnectionFailureException`. Unless the app catches this and falls back to DB, the request fails. Cache-Aside gives the app explicit control — including the ability to add a try/catch around the cache check:

```java
try {
    cached = redis.get(key);
} catch (RedisException e) {
    log.warn("Cache unavailable, falling back to DB: {}", e.getMessage());
}
if (cached == null) { return db.findById(id).get(); }
```

Cache-Aside: easier to add resilient fallback because the DB call is already in the code path.

**Read-Through (Caffeine LoadingCache):** Cache is in-process (Caffeine), so "cache goes down" isn't applicable — in-process cache can't fail independently. If using Redis as Read-Through (Spring `@Cacheable` + RedisCacheManager): same issue — Redis failure causes `@Cacheable` to throw. Adding Redis fallback requires custom `CacheErrorHandler` in Spring.

**Winner for resilience:** Cache-Aside — explicit DB fallback is natural. Read-Through — requires cache framework error handling configuration.

---

### 🧠 Mental Model / Analogy

> Cache-Aside = DIY mechanic. You know how your car works. When the part breaks (cache miss), you source and install it yourself (DB query + cache write). Full control. More work. Read-Through = dealership service. You just say "my car needs a part" (cache.get(key)). They handle sourcing and installation (cache loader → DB). Less work. Less control. Best for standard repairs. For unusual situations (multi-source fallback, conditional caching), DIY is better.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Cache-Aside: app writes cache check + DB load code. Read-Through: cache does the DB load via a configured loader; app just calls `cache.get(key)`. Spring `@Cacheable` = Read-Through. Choose Read-Through for simplicity; Cache-Aside for complex fallback logic.

**Level 2:** Cache-Aside advantages: (1) works with any data source without configuration; (2) easy to add try/catch DB fallback on cache failure; (3) can implement conditional caching logic not expressible in annotations. Read-Through advantages: (1) no cache logic in service code — cleaner separation; (2) Caffeine LoadingCache prevents stampede (one load per key, others wait); (3) `@Cacheable` + `@CacheEvict` annotations = declarative, testable.

**Level 3:** Stampede prevention: Caffeine's `LoadingCache.get(key)` guarantees only ONE in-flight load per key — other concurrent requests wait for the first to complete. Cache-Aside with plain Redis does NOT provide this — all concurrent misses for the same key hit the DB simultaneously (stampede). For stampede prevention without Caffeine: add Redis SETNX mutex around the load. Or use Caffeine as L1 (which prevents stampede at the L1 level).

**Level 4:** The fundamental difference is **where the orchestration logic lives**: in the application (Cache-Aside) or in the cache layer (Read-Through). This is a separation of concerns decision. Read-Through follows the **Open/Closed Principle** for the application: the application is open to new data sources (different CacheLoaders) without modification, and closed to cache internals. Cache-Aside is more **transparent** — a developer reading the code can see exactly when and how the cache is checked and populated. For large teams: Read-Through (`@Cacheable`) is preferred because junior developers can't accidentally write incorrect cache logic (it's hidden from them). For performance-critical systems: Cache-Aside is preferred because the developer can see and optimize every cache operation in the hot path.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│ CACHE-ASIDE vs READ-THROUGH: RESPONSIBILITY MAP          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ CACHE-ASIDE:                                             │
│  App → cache.get(key) → null (miss)                     │
│  App → db.load(key) → value                             │
│  App → cache.set(key, value, ttl)                        │
│  App → return value                                      │
│  [APP owns all three steps]                              │
│                                                          │
│ READ-THROUGH:                                            │
│  App → cache.get(key) → cache checks internally         │
│  [READ-THROUGH ← YOU ARE HERE: cache owns the load]     │
│  if miss: cache → loader.load(key) → db.load(key)       │
│           cache → cache.set(key, result, ttl)            │
│           cache → return result                          │
│  App receives value directly                             │
│  [APP is unaware of cache hit vs miss]                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
USER REQUEST: GET /products/42

CACHE-ASIDE:
→ ProductService.getProduct("42")
→ redis.get("product:42") → nil (MISS)
→ productRepository.findById("42") → Product{...} (DB query)
→ redis.set("product:42", product, 15min)
→ return product
[App wrote all 4 lines of cache logic]

READ-THROUGH (@Cacheable):
→ Spring AOP intercepts getProduct("42")
→ cacheManager.get("products", "42") → null (MISS)
→ [COMPARISON ← YOU ARE HERE: Spring calls method on miss]
→ Spring invokes: productRepository.findById("42") → Product{...}
→ Spring: cacheManager.put("products", "42", product)
→ Spring returns: product
[App wrote 0 lines of cache logic — just @Cacheable annotation]
```

---

### ⚖️ Comparison Table

| Dimension                 | Cache-Aside                        | Read-Through (@Cacheable)                  |
| ------------------------- | ---------------------------------- | ------------------------------------------ |
| Where is DB call?         | In service code                    | In service code (invoked by cache on miss) |
| Cache logic in app?       | Yes (explicit get/set)             | No (annotation/loader)                     |
| Fallback on cache failure | Easy (try/catch around cache call) | Requires custom CacheErrorHandler          |
| Stampede prevention       | Manual (Redis SETNX)               | Caffeine: built-in (one load per key)      |
| Conditional caching       | Full control                       | Limited (@Cacheable conditions)            |
| Code readability          | Verbose (cache logic visible)      | Clean (cache logic hidden)                 |
| Spring integration        | Manual or via templates            | Native @Cacheable, @CacheEvict             |
| Cold start behavior       | Same (first access misses)         | Same; but putAll() easy pre-warm           |

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                                                     |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Read-Through always means better performance"    | They perform identically on a cache miss — both call the DB. The difference is code organization, not performance                                                                           |
| "Spring @Cacheable is always sufficient"          | @Cacheable can't handle: (1) caching partial results, (2) complex key conditions, (3) multi-source fallbacks, (4) conditional TTLs. In these cases, Cache-Aside provides needed flexibility |
| "Cache-Aside is 'legacy'; Read-Through is modern" | Neither is deprecated or legacy. Spring applications predominantly use @Cacheable (Read-Through) for simplicity, but Cache-Aside is the correct choice for complex scenarios                |

---

### 🚨 Failure Modes & Diagnosis

**1. @Cacheable Not Caching — Self-Invocation Problem**

**Symptom:** `@Cacheable` on `getProduct()` is ignored. Every call hits the database.

**Root Cause:** The method is called from within the same class (self-invocation). Spring AOP proxies don't intercept self-calls. `this.getProduct(id)` bypasses the AOP proxy → bypasses `@Cacheable`.

**Diagnosis + Fix:**

```java
// PROBLEM:
@Service
public class ProductService {
    public List<Product> getProductsByCategory(String category) {
        return categoryIds.stream()
            .map(id -> this.getProduct(id))  // SELF-CALL: AOP bypassed
            .collect(Collectors.toList());
    }

    @Cacheable(value = "products", key = "#id")
    public Product getProduct(String id) {
        return db.findById(id).orElseThrow();
    }
}

// FIX: inject self-reference or use Cache-Aside instead
@Service
public class ProductService {
    @Autowired private ProductService self;  // Inject own proxy

    public List<Product> getProductsByCategory(String category) {
        return categoryIds.stream()
            .map(id -> self.getProduct(id))  // Calls through proxy ✓
            .collect(Collectors.toList());
    }

    @Cacheable(value = "products", key = "#id")
    public Product getProduct(String id) {
        return db.findById(id).orElseThrow();
    }
}
// OR: switch to Cache-Aside for this use case — no AOP limitation
```

---

### 🔗 Related Keywords

**Prerequisites:** Cache-Aside, Read-Through, Write-Through, Write-Around
**Builds On This:** System Design, Caching
**Related:** Cache-Aside, Read-Through, Write-Through

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CACHE-ASIDE  │ App does: check → miss → load → set        │
│ READ-THROUGH │ App: cache.get(); Cache: checks+loads      │
│ SPRING RT    │ @Cacheable = Read-Through via AOP          │
│ FLEXIBILITY  │ Cache-Aside: higher (conditional, fallback)│
│ SIMPLICITY   │ Read-Through: higher (no cache code)       │
│ STAMPEDE     │ Cache-Aside: needs mutex; Caffeine: built-in│
│ SELF-INVOKE  │ @Cacheable fails on self-call; inject proxy│
│ CHOOSE RT    │ Standard entity reads; Spring @Cacheable   │
│ CHOOSE CA    │ Complex fallback; conditional TTL; perf    │
│ ONE-LINER    │ "Same outcome; CA = app controls load;    │
│              │  RT = cache controls load via loader"      │
│ NEXT EXPLORE │ Consistent Hashing in Cache → Redis Cluster│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C — Design Question) You're building a multi-tenant SaaS application where each tenant has custom business rules affecting how data is cached (tenant A has 5-minute TTL; tenant B has 60-minute TTL; tenant C's data must NEVER be cached due to compliance). Can Spring `@Cacheable` handle this? If not, how would you implement this with Cache-Aside? What would the code look like?

**Q2.** (TYPE A — Spring Deep Dive) Explain the Spring `@Cacheable` AOP proxy lifecycle: when is the proxy created? What happens when the cache manager is Redis vs. Caffeine? What does `unless="#result == null"` do at the proxy level? Why does `@Cacheable` on a `@Transactional` method have potential ordering issues (cache populated before transaction commits)?
