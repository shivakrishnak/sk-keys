---
version: 2
layout: default
title: "Cache Stampede"
parent: "Caching"
grand_parent: "Technical Dictionary"
nav_order: 23
permalink: /caching/cache-stampede/
id: CCH-041
category: Caching
difficulty: ★★★
depends_on: Cache-Aside, TTL, Cache Invalidation
used_by: System Design, Caching, Distributed Systems
related: Thundering Herd, Cache Invalidation, Cache-Aside
tags:
  - caching
  - cache-stampede
  - dogpile
  - database-overload
  - deep-dive
---

# CCH-033 - Cache Stampede

⚡ TL;DR - A cache stampede (dogpile effect) occurs when a popular cache entry expires (or is invalidated) and **many concurrent requests all miss the cache simultaneously**, each independently triggering a database query for the same data - the DB receives an instant spike of N identical queries, potentially causing overload; prevention requires ensuring only **one request** regenerates the cache entry while others wait or serve slightly stale data.

| #483            | Category: Caching                                | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------- | :-------------- |
| **Depends on:** | Cache-Aside, TTL, Cache Invalidation             |                 |
| **Used by:**    | System Design, Caching, Distributed Systems      |                 |
| **Related:**    | Thundering Herd, Cache Invalidation, Cache-Aside |                 |

---

### 🔥 The Problem This Solves

**CACHE EXPIRY CREATES A VULNERABILITY WINDOW:**
A popular endpoint (`GET /products/best-sellers`) is cached. At exactly T=0 (TTL expires), 5,000 concurrent users hit this endpoint. All 5,000 find the cache empty. All 5,000 independently query the database. The database receives 5,000 identical queries in under 1 second. This spike saturates the DB, causing: slow queries, connection pool exhaustion, cascading timeouts, potential full outage. Without the cache, this endpoint serves 5,000 qps fine - but only because the cache absorbed the load. Without protection, cache expiry is a periodic self-inflicted DDoS.

---

### 📘 Textbook Definition

A **Cache Stampede** (also **dogpile effect** or **thundering herd for caches**) is a failure pattern where a high-traffic cache miss causes an immediate burst of concurrent database requests for identical data. Conditions: (1) a highly-trafficked cache key expires or is invalidated; (2) many concurrent requests observe the cache miss simultaneously; (3) each request independently initiates a database query without coordination. The database receives a burst equal to the number of concurrent requests, often many times its normal per-request load for that data. Prevention strategies: **(1) Mutex/lock**: only one request re-populates the cache; others wait (coordination overhead, risk of lock timeout). **(2) Probabilistic early expiry (PER)**: occasionally re-populate cache before TTL expires while the key is still cached - prevents the TTL cliff. **(3) Stale-while-revalidate**: return slightly stale cached data to all requests; re-populate in background - best UX (no wait). **(4) External cache lock**: Redis `SET nx` (distributed lock) to serialize re-population. **(5) TTL jitter**: stagger expiry times to prevent synchronized mass expiry.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Stampede = cache key expires + many concurrent requests all miss → all hit DB simultaneously → DB spike.

**One analogy:**

> A popular TV show ends. 10,000 viewers immediately search for the next episode streaming link (hot cache key expires). All 10,000 land on Google (database) simultaneously. Google's search results for "next episode XYZ" were cached (for performance), but the cache just expired. All 10,000 trigger the same search index query simultaneously - search infrastructure spikes.

- "10,000 viewers searching simultaneously" → concurrent cache misses
- "Cached search results just expired" → TTL expiry
- "All trigger same search query" → stampede → DB overload

**One insight:**
The stampede problem is caused by the combination of: (1) a single shared cache key (all concurrent readers miss the same key), and (2) each reader independently re-populating (no coordination). The fix is either: introduce coordination (mutex - one reader re-populates, others wait), or eliminate the cliff (probabilistic expiry - re-populate before TTL expires), or serve stale (stale-while-revalidate - don't let requests wait at all). Each fix has different tradeoffs in latency, complexity, and staleness.

---

### 🔩 First Principles Explanation

**STRATEGY 1: DISTRIBUTED MUTEX (REDIS SET NX):**

```java
// Only ONE request re-populates; others wait for it
public Product getProduct(String productId) {
    String cacheKey = "product:" + productId;
    String lockKey = "lock:product:" + productId;

    // Step 1: Check cache
    Product cached = redisTemplate.opsForValue().get(cacheKey, Product.class);
    if (cached != null) return cached;

    // Step 2: Cache miss - try to acquire lock
    Boolean acquired = redisTemplate.opsForValue()
        .setIfAbsent(lockKey, "1", Duration.ofSeconds(5));  // SET NX EX 5

    if (Boolean.TRUE.equals(acquired)) {
        // WINNER: re-populate the cache
        try {
            // Double-check: another request may have populated while we waited for lock
            cached = redisTemplate.opsForValue().get(cacheKey, Product.class);
            if (cached != null) return cached;

            // Fetch from DB
            Product product = productRepository.findById(productId).orElseThrow();
            redisTemplate.opsForValue().set(cacheKey, product, Duration.ofMinutes(10));
            return product;
        } finally {
            redisTemplate.delete(lockKey);  // Always release lock
        }
    } else {
        // LOSER: wait briefly, then retry (winner is populating cache)
        try { Thread.sleep(50); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
        return getProduct(productId);  // Retry - should be cache hit now
    }
}
// Tradeoff: loser threads are blocked 50ms (lock hold time)
// Risk: if winner crashes: lock held for 5 seconds (TTL on lock key)
// DB queries: 1 (winner only)  vs. N (stampede) - dramatic improvement
```

**STRATEGY 2: STALE-WHILE-REVALIDATE (BEST UX):**

```java
// Return stale data immediately; re-populate in background
// Uses two TTLs: "soft TTL" (data is fresh), "hard TTL" (data is expired)
public Product getProductStaleWhileRevalidate(String productId) {
    String cacheKey = "product:" + productId;
    String staleFlagKey = "stale:" + productId;

    // Step 1: Get from cache (may be stale, but present)
    Product cached = redisTemplate.opsForValue().get(cacheKey, Product.class);

    if (cached == null) {
        // Hard miss (beyond hard TTL): must fetch synchronously
        return fetchAndCache(productId, cacheKey);
    }

    // Step 2: Check if within soft TTL (fresh) or needs background refresh
    Boolean isFresh = redisTemplate.opsForValue().get(staleFlagKey, Boolean.class);

    if (isFresh == null || !isFresh) {
        // Soft TTL expired: data is stale - trigger background refresh
        // But return stale data immediately to this request (no wait!)

        // Acquire refresh lock to ensure only one background refresh
        String refreshLock = "refreshlock:" + productId;
        Boolean lockAcquired = redisTemplate.opsForValue()
            .setIfAbsent(refreshLock, "1", Duration.ofSeconds(30));

        if (Boolean.TRUE.equals(lockAcquired)) {
            // Trigger background refresh (non-blocking)
            CompletableFuture.runAsync(() -> {
                try {
                    fetchAndCache(productId, cacheKey);
                    redisTemplate.delete(refreshLock);
                } catch (Exception e) {
                    log.error("Background cache refresh failed for {}", productId, e);
                    redisTemplate.delete(refreshLock);
                }
            });
        }
        // Return stale data - zero wait for the caller!
    }

    return cached;  // Fresh OR stale - always returns immediately
}

private Product fetchAndCache(String productId, String cacheKey) {
    Product product = productRepository.findById(productId).orElseThrow();
    // Set hard TTL (20 min) and soft TTL indicator (10 min)
    redisTemplate.opsForValue().set(cacheKey, product, Duration.ofMinutes(20));
    redisTemplate.opsForValue().set("stale:" + productId, true, Duration.ofMinutes(10));
    return product;
}
// Caller latency: always < 5ms (cache hit - stale or fresh)
// DB queries: 1 per refresh cycle (background, doesn't block callers)
// Stale window: up to soft TTL (10 minutes) after data changes
```

**STRATEGY 3: PROBABILISTIC EARLY RE-EXPIRY (PER):**

```java
// XFetch algorithm (Vattani, Chierichetti, Veness 2015)
// Probabilistically re-populate before TTL expires
// Higher traffic → earlier re-population probability

public Product getProductWithPER(String productId) {
    String cacheKey = "product:" + productId;
    CacheEntry entry = redisTemplate.opsForValue().get(cacheKey, CacheEntry.class);

    if (entry == null) {
        // Hard miss: populate synchronously
        return fetchAndCachePER(productId, cacheKey);
    }

    // PER algorithm: should we early-expire?
    long ttlSeconds = redisTemplate.getExpire(cacheKey, TimeUnit.SECONDS);
    double beta = 1.0;  // higher = more eager re-population (tune based on fetch cost)
    double delta = entry.getFetchDurationMs() / 1000.0;  // last fetch time in seconds

    // Probability formula: current_time - (delta * beta * log(random(0,1))) > expiry_time
    double xFetchValue = Instant.now().getEpochSecond() - delta * beta * Math.log(Math.random());
    long expiryTime = Instant.now().getEpochSecond() + ttlSeconds;

    if (xFetchValue > expiryTime) {
        // Probabilistic early re-population (occurs more often near expiry)
        return fetchAndCachePER(productId, cacheKey);
    }

    return entry.getValue();
}
// Result: cache is re-populated by a single request BEFORE TTL cliff
// By the time the TTL actually expires, the cache is already fresh
// No stampede possible: the cliff is eliminated, not just mitigated
```

**TTL JITTER (SIMPLEST PREVENTION):**

```java
// Prevent synchronized mass expiry of multiple hot keys
// Add random jitter to TTL on each cache write

private static final int BASE_TTL_SECONDS = 600;  // 10 minutes
private static final double JITTER_FACTOR = 0.2;  // ±20%

public Duration getJitteredTTL() {
    int jitterRange = (int)(BASE_TTL_SECONDS * JITTER_FACTOR);
    int jitter = (int)(Math.random() * jitterRange * 2) - jitterRange;  // -120 to +120
    return Duration.ofSeconds(BASE_TTL_SECONDS + jitter);  // 480 to 720 seconds
}

// All 10,000 products cached at the same time will now expire over a 4-minute window
// instead of all at exactly T=600s → stampede spread out over 4 minutes
// Each individual expiry causes a small number of misses, not a massive spike
```

---

### 🧪 Thought Experiment

**WHAT IF THE MUTEX HOLDER CRASHES?**

Scenario: Request A acquires the lock (`lock:product:42`, TTL=5s) and begins DB fetch. Mid-fetch (2 seconds in), the JVM instance running Request A crashes (OOM, hardware failure). The lock remains in Redis with 3 seconds TTL.

**For 3 seconds:** all concurrent requests see the lock, spin-wait (50ms retries), and wait. They're all blocked.

**After 3 seconds:** Redis auto-expires the lock. The next request to retry acquires the lock, fetches from DB, populates cache. All other waiting requests then get cache hits on their next retry.

**The 3-second window:** blocked requests in spin-wait. If their timeout (HikariCP 30s) is longer than the lock TTL (5s), they'll recover automatically. If the lock TTL is too long (60s), the 60-second wait may cause HTTP timeouts and error responses to users.

**Best practice:** lock TTL = realistic max DB fetch time × 2. For a 2-second DB query: lock TTL = 4-5 seconds. Never set very long lock TTLs for stampede prevention.

---

### 🧠 Mental Model / Analogy

> Cache stampede is like a popular café closing briefly to restock (cache expires). When it reopens, 200 customers who were waiting all rush in simultaneously (concurrent cache misses). The kitchen (database) gets 200 simultaneous coffee orders instead of its normal 2/minute. The kitchen chokes. Prevention: stale-while-revalidate = keep serving yesterday's coffee while restocking; mutex = only the first customer waits inside while others wait outside; probabilistic early restock = café restocks just before running out (no closure needed).

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Stampede = popular cache key expires + many requests all miss → DB spike. Prevention: mutex (one re-populates, others wait), stale-while-revalidate (return stale immediately, refresh background), TTL jitter (spread expiry times).

**Level 2:** Use stale-while-revalidate for best UX (no blocking). Use Redis `SET NX` mutex for correctness-critical data. Apply TTL jitter (±20%) always. Spring's `@Cacheable` doesn't protect against stampede out-of-the-box - add a cache-aside pattern with mutex for high-traffic keys.

**Level 3:** Caffeine `refreshAfterWrite` implements stale-while-revalidate natively: after write TTL, subsequent access triggers async refresh but returns stale data; only `expireAfterWrite` causes a synchronous miss. For Redis-based caches: implement stale-while-revalidate with dual TTL (soft TTL flag + hard TTL on the value). HTTP `stale-while-revalidate` Cache-Control directive implements the same pattern at the CDN/browser level: `Cache-Control: max-age=60, stale-while-revalidate=30` - serve for 60s fresh, then serve stale for up to 30s while refreshing in background.

**Level 4:** The cache stampede is a form of **coordination failure** - many independent agents (request threads) making locally optimal decisions (re-populate the cache) that collectively produce a globally harmful outcome (DB overload). This is a classic tragedy-of-the-commons problem. The solutions all introduce some form of coordination: mutex (explicit lock), stale-while-revalidate (implicit coordination via returning stale data), probabilistic early expiry (implicit coordination via probabilistic single-winner). The XFetch/PER algorithm is particularly elegant: it's probabilistically calibrated so that the expected time of the first re-population attempt is proportional to the fetch cost (expensive fetches trigger earlier re-population to spread load). At large scale, Facebook's cache layer (Memcache) uses a "leasing" mechanism: on cache miss, the cache issues a lease token to one client; subsequent clients for the same key are told to retry after a delay - effectively a distributed mutex built into the cache protocol.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ WITHOUT PROTECTION - STAMPEDE                        │
├──────────────────────────────────────────────────────┤
│ T=0:  product:42 TTL expires                         │
│ T=1:  1000 concurrent requests                       │
│        → ALL: Redis GET product:42 → nil (MISS)      │
│        → ALL: DB SELECT product 42 (1000 queries!)   │
│ T=200ms: DB returns, all 1000 set cache              │
│   DB: 1000 connections spike → possible overload     │
│                                                      │
│ WITH MUTEX - SERIALIZED RE-POPULATION                │
├──────────────────────────────────────────────────────┤
│ T=0:  product:42 TTL expires                         │
│ T=1:  1000 concurrent requests miss cache            │
│        → Request #1: acquires lock (SET NX)          │
│        → Requests #2-1000: see lock → spin-wait      │
│        → Request #1: DB SELECT → sets cache          │
│        → Requests #2-1000 retry: HIT → return        │
│   DB: 1 query (not 1000) - [STAMPEDE ← YOU ARE HERE]│
│                                                      │
│ WITH STALE-WHILE-REVALIDATE                          │
├──────────────────────────────────────────────────────┤
│ T=0:  product:42 soft TTL expires (hard TTL=20min)   │
│ T=1:  1000 concurrent requests                       │
│        → ALL: Redis GET product:42 → stale data ✓    │
│        → 1 background refresh triggered (lock)       │
│        → ALL 1000: return stale data immediately     │
│   DB: 1 background query                             │
│   Latency: < 5ms for all 1000 requests ✓             │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**E-COMMERCE HOMEPAGE (HIGH-TRAFFIC KEY) WITH STALE-WHILE-REVALIDATE:**

```
GET /api/homepage/featured-products (10,000 req/sec)
Cache key: "homepage:featured" - updated by editorial team once/hour

Minute 0: Product team updates featured products
→ Cache invalidated: Redis DEL homepage:featured

Minute 0, second 0: 10,000 requests hit simultaneously
→ [STAMPEDE ← YOU ARE HERE: stale-while-revalidate protection]

→ ALL 10,000: Redis GET homepage:featured → nil (hard miss - just invalidated)
→ Thread #1: acquires SET NX "lock:homepage:featured" EX 10
→ Thread #1: DB SELECT featured_products → {data}
→ Thread #1: Redis SET "homepage:featured" {data} EX 3600 (hard TTL: 1hr)
→ Thread #1: Redis SET "fresh:homepage:featured" true EX 1800 (soft TTL: 30min)
→ Thread #1: releases lock
→ Threads #2-10,000 (spin-wait, 50ms): retry → Redis HIT → return ✓

After 30 minutes (soft TTL expires):
→ Next request: gets "homepage:featured" (cache HIT - hard TTL still valid)
→ Detects: "fresh:homepage:featured" = nil (soft TTL expired)
→ Acquires background refresh lock
→ Returns stale data IMMEDIATELY to this request (< 5ms)
→ Background: DB query → refresh cache
→ All subsequent requests: fresh data within seconds ✓

DB queries in 1 hour: ~2 (one per 30-minute soft TTL)
Without caching: 10,000 req/s × 3600s = 36 million DB queries/hr
```

---

### ⚖️ Comparison Table

| Strategy               | DB Impact                    | Latency Impact              | Stale Risk        | Complexity |
| ---------------------- | ---------------------------- | --------------------------- | ----------------- | ---------- |
| No protection          | N queries (stampede)         | Spike → timeout             | N/A (no caching)  | Low        |
| TTL jitter             | Spread over jitter window    | Normal (distributed misses) | TTL duration      | Very Low   |
| Mutex (Redis SET NX)   | 1 query                      | Losers wait 50ms+           | Near-zero         | Medium     |
| Stale-while-revalidate | 1 background query           | None (always cache hit)     | Soft TTL duration | High       |
| XFetch/PER             | 1 early query (before cliff) | None                        | None (no cliff)   | High       |

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                                                                                                                                                                |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "TTL jitter prevents stampede"                  | Jitter spreads expiry times to prevent synchronized mass expiry across multiple keys - it doesn't prevent stampede for a single key with many concurrent requests. Jitter + mutex or stale-while-revalidate are needed for single-key high-concurrency |
| "Cache stampede is the same as thundering herd" | Thundering herd is the broader pattern (many waiting entities wake up simultaneously). Cache stampede is the specific form where the "wake up" is a cache miss. A thundering herd can also happen with lock releases, process restart, etc.            |
| "Stale-while-revalidate serves incorrect data"  | Stale-while-revalidate serves slightly outdated data (bounded by soft TTL). For most applications, serving 30-minute-old featured products is acceptable. The freshness requirement must be evaluated per use case                                     |

---

### 🚨 Failure Modes & Diagnosis

**1. Mutex Lock Holder OOM - Extended Blocking**

**Symptom:** After a deployment, p99 latency spikes from 50ms to 5+ seconds for 10 seconds. All requests for the same endpoint are blocked. Then latency recovers. Repeat pattern on each deploy.

**Root Cause:** On deploy, old instances die and all cache entries for that instance expire simultaneously. New instances have empty caches. First request for each hot key acquires mutex. If the mutex TTL is 60 seconds (overly long), all other requests block for up to 60 seconds. On app startup, hundreds of hot keys miss simultaneously, each with a 60s mutex lock - compounded blocking.

**Fix:**

```java
// Short mutex TTL (match realistic DB fetch time)
Boolean acquired = redisTemplate.opsForValue()
    .setIfAbsent(lockKey, "1", Duration.ofSeconds(5));  // NOT 60 seconds

// Pre-warm cache on startup
@EventListener(ApplicationReadyEvent.class)
public void warmCache() {
    List<String> hotProductIds = productRepository.findHotProductIds(100);
    hotProductIds.parallelStream().forEach(id ->
        getProduct(id)  // triggers cache load on startup, not on first user request
    );
    log.info("Cache warmed with {} hot products", hotProductIds.size());
}
```

---

### 🔗 Related Keywords

**Prerequisites:** Cache-Aside, TTL, Cache Invalidation
**Builds On This:** System Design, Distributed Systems
**Related:** Thundering Herd, Cache Invalidation, Cache-Aside

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ TRIGGER     │ Popular key expires + many concurrent miss │
│ EFFECT      │ N concurrent DB queries (spike = outage)   │
│ FIX 1       │ Mutex: Redis SET NX (1 repopulates, N wait)│
│ FIX 2       │ Stale-while-revalidate (best UX)           │
│ FIX 3       │ TTL jitter (spread multi-key expiry)       │
│ FIX 4       │ PER/XFetch (probabilistic early refresh)   │
│ DETECT      │ DB query spike on TTL-aligned intervals    │
│ SPRING NOTE │ @Cacheable does NOT protect stampede        │
│ ONE-LINER   │ "Many miss same key → all hit DB → spike  │
│             │  → one repopulates, rest wait or get stale" │
│ NEXT EXPLORE│ Thundering Herd → Negative Caching         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Question) A product listing page (`GET /category/electronics`) is cached for 1 hour. During a Black Friday sale, 100,000 concurrent users hit this page at 9:00 AM (the official sale start time - the product team invalidated the cache at 8:59 AM to show sale prices). Describe: (a) what happens at 9:00 AM without protection, (b) which prevention strategy you would use and exactly how you'd implement it, (c) what happens if the database is also under high load from order processing at the same time.

**Q2.** (TYPE D - Failure Scenario) A distributed cache (Redis Cluster) has 3 nodes. Node 2 fails at 2 PM (hardware fault). 30% of cache keys were on Node 2. Immediately after, DB query rate increases by 40% and API latency rises from 50ms to 300ms p99. Is this a cache stampede? How does it differ from a classic TTL-expiry stampede? What mitigation works here that doesn't work for TTL-expiry stampede?
