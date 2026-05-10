---
version: 2
layout: default
title: "Cache Warming"
parent: "Caching"
grand_parent: "Technical Dictionary"
nav_order: 19
permalink: /caching/cache-warming/
id: CCH-019
category: Caching
difficulty: ★★★
depends_on: Cache-Aside, Multi-Level Cache, TTL
used_by: System Design, Caching, CI-CD
related: Multi-Level Cache, Cache Invalidation, Thundering Herd
tags:
  - caching
  - cache-warming
  - cold-start
  - preloading
  - deep-dive
---

# CCH-019 - Cache Warming

⚡ TL;DR - Cache warming (pre-warming) is the practice of **proactively loading cache entries before traffic arrives**, preventing the "cold start" problem where all requests after a deployment miss the cache and hit the database simultaneously; strategies range from startup pre-loading to gradual traffic ramp-up to event-driven proactive fill.

| #489            | Category: Caching                                      | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | Cache-Aside, Multi-Level Cache, TTL                    |                 |
| **Used by:**    | System Design, Caching, CI-CD                          |                 |
| **Related:**    | Multi-Level Cache, Cache Invalidation, Thundering Herd |                 |

---

### 🔥 The Problem This Solves

**COLD START AFTER DEPLOYMENT:**
A new version deploys across all 50 instances simultaneously. All caches are empty (new JVM, new Redis keyspace, or TTL-expired entries). The first minute of traffic after deployment: 100% cache miss rate. If the deployment causes a thundering herd (all 50 instances start simultaneously), the database receives 50× normal write load from cache population queries. API latency spikes from 20ms (cached) to 150ms (uncached DB query) for the first minute. Visible to users as a performance degradation spike after every deployment.

**SCHEDULED PEAK EVENTS:**
A flash sale starts at 12:00 noon. 10,000 users will request the same 500 sale products simultaneously. Without cache warming: at 11:59, the last request to product X might have expired its cache entry. At 12:00: 10,000 requests for product X → cache miss → DB overload (stampede). With cache warming: at 11:50, a batch job pre-loads all 500 sale products into cache. At 12:00: all 10,000 requests → cache hit → no DB queries.

---

### 📘 Textbook Definition

**Cache Warming** (also **cache pre-warming**, **cache pre-loading**, or **cache priming**) is the process of populating cache entries with frequently accessed data **before** production traffic begins, ensuring high cache hit rates from the start rather than building up over time. Cold cache = empty cache = 0% hit rate = all requests fall through to the database. Warm cache = pre-populated cache = high hit rate = database shielded from load spike.

**Warming strategies:**

1. **Startup pre-loading**: on application start, load a set of known-important keys from the database and populate the cache. Risk: may delay startup time; may not know which keys to load.
2. **Traffic replay / shadow warming**: replay recent production traffic against the new instance to populate its cache before taking live traffic (Kubernetes readiness probe gates live traffic).
3. **Scheduled batch warming**: a cron job or scheduled task periodically refreshes the most popular cache entries before they expire (prevents cold miss on expiry).
4. **Event-driven warming**: on data creation/update, proactively cache the new value (push into cache, don't wait for first read). Common with CDC (Change Data Capture) → cache refresh pipeline.
5. **Gradual traffic ramp-up**: route 1% of traffic to a new instance, let it warm up naturally, then increase to 100%. Kubernetes readiness probes and HPA can gate traffic until hit rate reaches a threshold.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Cache warming = load the cache before traffic arrives so the first user gets a fast response, not a cold miss.

**One analogy:**

> A restaurant opens for lunch service at noon. Without warming: chefs arrive at noon and start cooking each dish from scratch as customers order. First 30 minutes: slow, customers wait. With warming: chefs arrive at 11am, pre-cook the 20 most popular dishes. At noon: 20 most common orders are fulfilled immediately. The kitchen only needs to cook the unusual orders from scratch.

- "Opening at noon with empty kitchen" → deployment with cold cache
- "Pre-cooking popular dishes" → cache warming: pre-load popular keys
- "20 most popular dishes" → top N most-accessed cache entries
- "Unusual orders from scratch" → cache misses for long-tail keys (acceptable)

**One insight:**
You don't need to warm the ENTIRE cache - only the **working set** (the keys that will be accessed in the first N minutes of traffic). Pareto principle: 20% of keys handle 80% of requests. Identifying and pre-warming those 20% achieves 80% hit rate immediately after deployment. Source of the working set: (1) query most-read records from the DB (e.g., `SELECT id FROM products ORDER BY view_count DESC LIMIT 1000`), (2) export hot keys from the OLD Redis instance before deploying the new one, (3) use Redis `OBJECT FREQ` (LFU policy) to identify the most-frequently-accessed keys in the current cache.

---

### 🔩 First Principles Explanation

**STARTUP PRE-LOADING:**

```java
// Spring: warm cache on ApplicationReadyEvent
// (fired AFTER the application is fully started, before accepting traffic
//  IF a readinessProbe is configured to delay traffic until ready)

@Component
public class CacheWarmer implements ApplicationListener<ApplicationReadyEvent> {

    @Autowired private ProductRepository productRepository;
    @Autowired private CacheManager cacheManager;

    @Override
    public void onApplicationEvent(ApplicationReadyEvent event) {
        // Run cache warming asynchronously to not block startup
        CompletableFuture.runAsync(this::warmCache);
    }

    private void warmCache() {
        log.info("Starting cache warming...");
        Instant start = Instant.now();

        // Strategy: top 1000 most-viewed products
        List<String> topProductIds = productRepository.findTopViewedProductIds(1000);

        Cache productsCache = cacheManager.getCache("products");

        // Batch load from DB (one query, not N)
        List<Product> topProducts = productRepository.findAllById(topProductIds);

        int count = 0;
        for (Product product : topProducts) {
            productsCache.put("product:" + product.getId(), product);
            count++;

            // Rate limit: don't hammer DB during startup
            if (count % 100 == 0) {
                Thread.sleep(100);  // 100ms pause every 100 entries
                log.debug("Warmed {} entries", count);
            }
        }

        Duration elapsed = Duration.between(start, Instant.now());
        log.info("Cache warming complete: {} entries in {}ms", count, elapsed.toMillis());
        // Emit metric: cache warming duration, count
        meterRegistry.counter("cache.warming.count").increment(count);
        meterRegistry.timer("cache.warming.duration").record(elapsed);
    }
}
```

**KUBERNETES READINESS PROBE WITH WARMING:**

```java
// HealthIndicator: signal not-ready until cache is warmed
@Component
public class CacheWarmingHealthIndicator implements HealthIndicator {

    private volatile boolean warmed = false;

    @EventListener(ApplicationReadyEvent.class)
    public void warmAndSignalReady() {
        try {
            warmCache();  // Blocking warm
            warmed = true;
            log.info("Cache warmed - signaling readiness");
        } catch (Exception e) {
            log.error("Cache warming failed - instance will not receive traffic", e);
        }
    }

    @Override
    public Health health() {
        return warmed ? Health.up().build() : Health.down()
            .withDetail("reason", "cache not yet warmed")
            .build();
    }
}
// Kubernetes readinessProbe:
// httpGet:
//   path: /actuator/health/readiness
//   port: 8080
// initialDelaySeconds: 10
// periodSeconds: 5
//
// Pod does NOT receive traffic until readiness probe passes (warmed=true)
// Traffic is held by Kubernetes Service until this instance signals ready
```

**SCHEDULED BATCH WARMING (PREVENT COLD MISS ON EXPIRY):**

```java
// Problem: top 1000 products have TTL=15min. At 15min mark: all expire simultaneously.
// All next requests miss → cache stampede → DB spike.
// Fix: scheduled task refreshes before TTL expires.

@Service
public class ScheduledCacheRefresher {

    // Run every 12 minutes (refresh before 15min TTL expires)
    @Scheduled(fixedDelay = 12 * 60 * 1000)
    public void refreshTopProducts() {
        log.info("Refreshing top products cache...");

        // Fetch and re-cache top products before TTL expires
        List<Product> topProducts = productRepository.findTopViewedProducts(1000);

        for (Product product : topProducts) {
            String key = "product:" + product.getId();
            // This SETS the key even if it's still in cache (overwrite = refresh)
            redisTemplate.opsForValue().set(key, product, Duration.ofMinutes(15));
        }

        log.info("Refreshed {} top products in cache", topProducts.size());
    }
}
// TTL=15min, refresh every 12min → cache always has 3min headroom before expiry
// No cold miss for top 1000 products - cache is proactively refreshed
```

**EVENT-DRIVEN WARMING VIA CDC:**

```java
// When a product is updated: don't wait for next read miss
// Proactively push the new value to cache (CDC event → cache push)

@KafkaListener(topics = "product-changes", groupId = "cache-warmer")
public void onProductChange(ProductChangeEvent event) {
    if (event.getType() == EventType.CREATED || event.getType() == EventType.UPDATED) {
        // Immediately cache the new/updated product
        Product product = productRepository.findById(event.getProductId()).orElse(null);
        if (product != null) {
            redisTemplate.opsForValue().set(
                "product:" + product.getId(), product, Duration.ofMinutes(15));
            // No cache miss for this product - it's already warm
        }
    } else if (event.getType() == EventType.DELETED) {
        redisTemplate.delete("product:" + event.getProductId());
    }
}
// Result: any product updated via the write path is instantly available in cache
// READ path: almost never hits DB for recently modified products
// Proactive warming: write → cache immediately; not lazy (read → miss → DB → cache)
```

---

### 🧪 Thought Experiment

**DEPLOYMENT WITHOUT WARMING: DATABASE OVERLOAD**

Production: 30 instances, each with Caffeine L1 (1000 entries) and Redis L2. All instances run for 3 hours - caches are fully warm, hit rate = 90%.

New deployment at 2pm: rolling restart (Kubernetes maxSurge=5). As each batch of 5 instances restarts, their L1 caches are empty. The L2 Redis is shared (not restarted) - still has warm data. So for a Redis-backed deployment: L1 is cold but L2 is warm. L2 hit rate is 90%. The cold start problem is limited to the L1 miss rate (~10% requests now hit L2 instead of L1 during warm-up).

For a full Redis flush (cluster upgrade, keyspace clear): 100% cold start. All 30 instances, all cache levels empty. First 5 minutes: all 100,000 req/min are cache misses → 100,000 DB queries/min (vs. normal 10,000). Database overloaded. Warming plan: before the Redis flush, export top-10,000 keys to a file → after flush, import and re-SET them all via a warm-up job → then start instances.

---

### 🧠 Mental Model / Analogy

> Cache warming is like a new store opening. A cold store has empty shelves (no cache). When customers arrive, staff must run to the back warehouse (database) for every item (100% miss rate). A warmed store: before opening, staff stock the shelves with the 500 most popular items (pre-loading top keys). When customers arrive: most items are right there (cache hit). Staff only need to go to the warehouse for unusual requests (long-tail cache misses). The difference: opening prep time (warm-up duration) vs. customer experience (cache hit rate from minute one).

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Cache warming = pre-load important cache entries before traffic arrives. On startup: load top N records from DB. Cold cache = poor latency + DB overload for first minutes after deployment.

**Level 2:** Use `ApplicationReadyEvent` for startup pre-loading. Use Kubernetes readiness probe to hold traffic until warming is complete. Use scheduled refresh to prevent TTL-expiry cold miss. Identify the "working set" via `SELECT ... ORDER BY view_count DESC LIMIT N`.

**Level 3:** Gradual traffic ramp-up: route 1% of traffic to new instance first (Kubernetes canary, AWS CodeDeploy linear10PercentEvery1Minute). Monitor cache hit rate: when > threshold (e.g., 70%), scale up traffic. L1 warming is per-instance; L2 Redis warming is shared (survives deployments). For full cache invalidations (Redis flush needed during upgrade): export hot keys before flush, re-import after - "cache migration" pattern.

**Level 4:** Cache warming intersects with traffic shaping and progressive delivery. Tools like Flagger (Kubernetes) + Prometheus metrics allow automatic canary promotion based on cache hit rate: if a new canary instance's hit rate drops below threshold, block promotion. This makes cache warming part of the CI/CD pipeline: "deploy → warm → verify hit rate → promote." The risk of **over-warming**: loading 10M records at startup delays readiness by 10 minutes and generates a massive DB read load - all other instances are still running, so this startup read causes contention. Solution: batch with rate limiting (100 records/second warm-up pace), or only warm the hottest 1% of keys (not all keys).

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ CACHE WARMING: TIMELINE                              │
├──────────────────────────────────────────────────────┤
│                                                      │
│ T=0:00  Deployment starts. Old instances still serve │
│         traffic. New instance starts.                │
│                                                      │
│ T=0:30  New instance: Spring ApplicationReadyEvent   │
│         CacheWarmer.warmCache() begins               │
│         Loads top 1000 products from DB              │
│         Redis populated: product:1 ... product:1000  │
│         [WARMING ← YOU ARE HERE: loading hot keys]   │
│                                                      │
│ T=1:30  Warming complete (1000 keys, rate-limited)   │
│         HealthIndicator: warmed=true                  │
│         Kubernetes readiness probe: PASS             │
│         Traffic starts routing to new instance       │
│                                                      │
│ T=1:31  First request: GET /products/42              │
│         L1 (Caffeine): HIT (warmed at T=0:30)        │
│         Response: 0.01ms - no DB query ✓             │
│         Hit rate: ~80% immediately (not gradual)     │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
FLASH SALE PREPARATION: Sale at 12:00pm for 500 products

T=11:45am: ScheduledSaleWarmer.warmSaleProducts() triggers
→ SELECT id FROM products WHERE in_flash_sale=true (→ 500 IDs)
→ Batch load: SELECT * FROM products WHERE id IN (...500...)
→ For each: Redis SET product:{id} {data} EX 3600
→ 500 keys loaded into L2 Redis

T=11:55am: Verify warming
→ redis-cli DBSIZE (should include 500+ keys)
→ redis-cli GET product:42 (verify data present)
→ Cache hit rate pre-check: 100% for all 500 sale products ✓

T=12:00pm: Flash sale begins
→ 10,000 simultaneous requests for sale products
→ [WARMING ← YOU ARE HERE: all keys warm]
→ Redis GET product:{any_sale_id} → HIT (1ms)
→ 10,000 requests served from cache: 0 DB queries ✓
→ DB load: normal (not hammered by stampede)
```

---

### ⚖️ Comparison Table

| Strategy             | When              | Benefit                     | Risk                             |
| -------------------- | ----------------- | --------------------------- | -------------------------------- |
| Startup pre-load     | App start         | Warm before first traffic   | Delays startup, DB load on start |
| Readiness probe gate | App start         | No traffic until warm       | Delayed rollout                  |
| Scheduled refresh    | Before TTL expiry | No cold miss on expiry      | Extra DB reads (scheduled)       |
| Event-driven fill    | On create/update  | Always fresh in cache       | Kafka lag = warming lag          |
| Gradual ramp-up      | Canary deployment | Natural warming with safety | Slower rollout                   |

---

### ⚠️ Common Misconceptions

| Misconception                                                 | Reality                                                                                                                                                                                                                                         |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Cache warming is only needed for new deployments"            | Cache warming is needed after any cache clear: Redis flush, cluster migration, eviction under memory pressure, or scheduled TTL expiry stampede. Scheduled warming prevents the last case proactively                                           |
| "Full DB scan is needed to warm the cache"                    | Only the working set (hot keys) needs warming. For a 100M product catalog, warming the top 1,000 products covers 80% of traffic. A full scan for warming wastes DB resources and delays startup                                                 |
| "Kubernetes rolling deployments solve the cold start problem" | Rolling deployments ensure old instances serve traffic while new ones start, but new instances still have cold caches. Without readiness probe + cache warming, new instances receive traffic immediately after startup, with 0% cache hit rate |

---

### 🚨 Failure Modes & Diagnosis

**1. Startup Cache Warming Overwhelms Database**

**Symptom:** During rolling deployment, database CPU spikes to 100%. Existing instances experience query latency increases. New instances take 3 minutes to become ready.

**Root Cause:** CacheWarmer loads 50,000 records at startup with no rate limiting. `productRepository.findAllById(50000IDs)` executes a massive IN query. Multiple instances starting simultaneously all execute this query.

**Diagnosis:**

```bash
# Check DB slow query log during deployment
# PostgreSQL:
SELECT query, calls, mean_exec_time FROM pg_stat_statements
WHERE query LIKE '%findAllById%' ORDER BY mean_exec_time DESC LIMIT 5;
# If mean_exec_time > 5000ms → query is too large

# Check application startup time
grep "Cache warming complete" app.log
# Should be < 60 seconds; if > 2 minutes → too many records
```

**Fix:**

```java
// Limit warm-up to top 1000 (not all 50K), with rate limiting
private void warmCache() {
    // Limit to actual hot keys only
    List<String> hotKeys = productRepository.findTopViewedProductIds(1000);  // Not all

    // Batch in smaller chunks
    Lists.partition(hotKeys, 100).forEach(batch -> {
        List<Product> products = productRepository.findAllById(batch);
        products.forEach(p -> cache.put("product:" + p.getId(), p));

        // Rate limit: 100 entries every 500ms = 200/second max warm-up rate
        Thread.sleep(500);
    });
}
```

---

### 🔗 Related Keywords

**Prerequisites:** Cache-Aside, Multi-Level Cache, TTL
**Builds On This:** System Design, CI-CD
**Related:** Multi-Level Cache, Cache Invalidation, Thundering Herd

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT         │ Pre-load cache before traffic arrives      │
│ COLD START   │ Empty cache → 100% miss → DB overload      │
│ STARTUP      │ ApplicationReadyEvent → load top N keys    │
│ GATE TRAFFIC │ Readiness probe: not ready until warmed    │
│ SCHEDULE     │ Refresh before TTL expiry (proactive)      │
│ EVENT-DRIVEN │ Create/update → cache immediately (push)   │
│ WORKING SET  │ Top 1-5% keys = 80% of traffic (Pareto)   │
│ RATE LIMIT   │ 100-200 entries/second during startup      │
│ ONE-LINER    │ "Pre-load hot keys before traffic; gate   │
│              │  traffic with readiness probe until warm"  │
│ NEXT EXPLORE │ Write-Around → Cache Aside vs Read-Through │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Question) Design a cache warming strategy for a multi-region (US/EU/APAC) deployment where each region has 20 application instances and a shared Redis Cluster per region. Every night at 3am UTC, a full cache flush is required (new product catalog version). Users in APAC will be awake at that time (3am UTC = 11am Tokyo). Design a warming pipeline that minimizes user-visible latency during the cache flush.

**Q2.** (TYPE D - Failure Scenario) Your cache warming on startup loads 5,000 products. This takes 45 seconds. The Kubernetes readiness probe `initialDelaySeconds: 60` (too long) and `timeoutSeconds: 1` (too short). The warm-up completes in 45 seconds but the readiness probe first fires at 60 seconds. 10 seconds after the pod starts, Kubernetes kills the pod (liveness probe failure due to startup overhead). Walk through: what configuration changes fix this, and how do you tune probe timing in production?
