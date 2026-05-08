---
layout: default
title: "Multi-Level Cache"
parent: "Caching"
grand_parent: "Technical Dictionary"
nav_order: 18
permalink: /caching/multi-level-cache/
id: CCH-018
category: Caching
difficulty: ★★★
depends_on: Cache-Aside, Distributed Cache, Cache Coherence, TTL
used_by: System Design, Caching, Performance Engineering
related: Cache Coherence, Local Cache vs Distributed Cache, Cache Warming
tags:
  - caching
  - multi-level-cache
  - l1-l2
  - caffeine
  - redis
  - deep-dive
---

# CCH-018 - Multi-Level Cache

⚡ TL;DR - A multi-level (L1/L2/L3) cache mirrors the CPU cache hierarchy in software: **L1 = in-process Caffeine** (zero network, JVM heap, sub-millisecond, per-instance), **L2 = distributed Redis** (shared across instances, ~1ms, larger), **L3 = database** (durable, ~10-20ms); reads check L1 → L2 → DB; cache coherence (all instances seeing the same data) is the hardest challenge.

| #488            | Category: Caching                                                | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------- | :-------------- |
| **Depends on:** | Cache-Aside, Distributed Cache, Cache Coherence, TTL             |                 |
| **Used by:**    | System Design, Caching, Performance Engineering                  |                 |
| **Related:**    | Cache Coherence, Local Cache vs Distributed Cache, Cache Warming |                 |

---

### 🔥 The Problem This Solves

**REDIS LATENCY UNDER EXTREME LOAD:**
Even Redis at 1ms per GET feels significant when: (1) a single user request triggers 50+ cache lookups; (2) the application processes 100K requests/second (100K × 1ms = 100% CPU time on just cache requests, never mind actual processing). A 1ms Redis RTT × 50 lookups = 50ms added to every request from caching alone. Local L1 cache at 0.01ms × 50 = 0.5ms - 100× faster.

**REDIS CLUSTER COST AT HIGH THROUGHPUT:**
A Redis Cluster handling 500K ops/second requires significant infrastructure (memory, compute, network bandwidth). The hottest 5% of keys (Zipf distribution: a small fraction of keys get the majority of traffic) can be served from L1 cache, reducing Redis load by 50-80% for those hot keys.

---

### 📘 Textbook Definition

A **Multi-Level Cache** (also **cache hierarchy** or **L1/L2 cache**) is a caching architecture with multiple tiers, each offering different tradeoffs between speed, capacity, and consistency:

| Level | Implementation                 | Latency  | Capacity          | Scope         | Coherence       |
| ----- | ------------------------------ | -------- | ----------------- | ------------- | --------------- |
| L1    | In-process (Caffeine, Guava)   | ~0.01ms  | JVM heap (MBs)    | Per-instance  | Per-instance    |
| L2    | Distributed (Redis, Hazelcast) | ~1ms     | Cluster (GBs-TBs) | All instances | Shared          |
| L3    | Database (PostgreSQL, MySQL)   | ~10-20ms | Disk              | All instances | Source of truth |

**Read strategy**: check L1 → if miss, check L2 → if miss, check L3 (DB) → populate L2 → populate L1.
**Write strategy**: write to L3 (DB) → invalidate/update L2 (Redis) → invalidate L1 on all instances (via pub/sub) → OR: allow L1 to expire naturally within its short TTL.
Key challenge: **L1 coherence across instances**. L2 (Redis) is shared and thus inherently consistent. L1 (Caffeine, per-instance) diverges after writes unless actively invalidated via pub/sub.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Multi-level cache = L1 in-process (fast, small, per-instance) → L2 Redis (shared, larger) → L3 DB (durable, slowest); read traverses the chain; coherence between L1 instances is the design challenge.

**One analogy:**

> Like finding a file at work: (1) Check your desk (L1 Caffeine - instant, your personal copy). (2) Check the shared office filing cabinet (L2 Redis - quick, shared with colleagues). (3) Order from the central archive (L3 DB - slow, canonical source). You put recently used files on your desk (L1 populate on cache hit). If someone updates the canonical document (DB write), they must tell you (pub/sub) to discard your desk copy (L1 eviction) and pull from the filing cabinet (L2 hit) or archive (L3 miss path).

**One insight:**
The economic argument for L1: a Redis GET at 1ms costs ~0.01ms of CPU (network wait dominates). A Caffeine GET at 0.01ms costs ~0.01ms CPU (pure computation). For the hottest 5% of keys (accessed thousands of times/second), the L1 cache absorbs 95% of the cache traffic without any network. Even if the L1 cache holds only 1,000 product records (say, the top 1,000 most-viewed products), it can serve 10,000 requests/second to those products at 0.01ms each - without touching Redis at all.

---

### 🔩 First Principles Explanation

**CAFFEINE L1 CONFIGURATION:**

```java
// L1: in-process Caffeine cache
// Window TinyLFU: best-in-class eviction policy (scan-resistant, adapts to access patterns)
@Bean("l1Cache")
public Cache<String, Object> l1Cache() {
    return Caffeine.newBuilder()
        .maximumSize(10_000)            // Max 10K entries (not bytes - entries)
        .expireAfterWrite(30, TimeUnit.SECONDS)  // L1 TTL: short for coherence
        .expireAfterAccess(10, TimeUnit.SECONDS) // Evict idle entries even sooner
        .recordStats()                  // Enable hit rate metrics
        .build();
}

// Sizing guidance:
// - 10K entries × avg 1KB each = ~10MB heap (very reasonable)
// - For product service: 10K most popular products in L1
// - If top 10K products get 80% of traffic → L1 hit rate ~80%
// - Only 20% of requests reach Redis (L2)
```

**MULTI-LEVEL CACHE SERVICE:**

```java
@Service
public class MultiLevelCacheService {

    @Autowired @Qualifier("l1Cache") private Cache<String, Object> l1Cache;  // Caffeine
    @Autowired private RedisTemplate<String, Object> redis;                  // L2 Redis

    private static final Duration L1_TTL = Duration.ofSeconds(30);
    private static final Duration L2_TTL = Duration.ofMinutes(15);
    private static final String INVALIDATION_CHANNEL = "cache:invalidations";

    // ============================
    // READ: L1 → L2 → DB
    // ============================

    @SuppressWarnings("unchecked")
    public <T> T get(String key, Supplier<T> dbLoader, Class<T> type) {
        // Level 1: local Caffeine cache
        Object l1Value = l1Cache.getIfPresent(key);
        if (l1Value != null) {
            return type.cast(l1Value);  // L1 HIT: ~0.01ms
        }

        // Level 2: shared Redis cache
        Object l2Value = redis.opsForValue().get(key);
        if (l2Value != null) {
            // L2 HIT: promote to L1 for next access
            l1Cache.put(key, l2Value);  // L1 populated
            return type.cast(l2Value);  // L2 HIT: ~1ms
        }

        // Level 3: database (cache miss)
        T dbValue = dbLoader.get();     // DB QUERY: ~10-20ms

        if (dbValue != null) {
            redis.opsForValue().set(key, dbValue, L2_TTL);  // Populate L2
            l1Cache.put(key, dbValue);                       // Populate L1
        }

        return dbValue;
    }

    // ============================
    // WRITE: DB → invalidate L2 → invalidate all L1 via pub/sub
    // ============================

    @Transactional
    public <T> T writeThrough(String key, T value, Supplier<T> dbWriter) {
        // 1. Write to DB (source of truth)
        T saved = dbWriter.get();

        // 2. AFTER commit: update L2 Redis and invalidate all L1 instances
        TransactionSynchronizationManager.registerSynchronization(
            new TransactionSynchronization() {
                @Override public void afterCommit() {
                    // Update L2 (shared, all instances read new value from L2)
                    redis.opsForValue().set(key, saved, L2_TTL);

                    // Update THIS instance's L1
                    l1Cache.put(key, saved);

                    // Broadcast invalidation: all OTHER instances evict their L1
                    redis.convertAndSend(INVALIDATION_CHANNEL, key);
                    // Each instance receives: localL1Cache.invalidate(key)
                    // Then their next read: L1 miss → L2 HIT (new value) ✓
                }
            }
        );

        return saved;
    }

    // ============================
    // EVICT: DB delete → L2 delete → broadcast L1 invalidation
    // ============================

    @Transactional
    public void evict(String key) {
        // DB write happens in caller's @Transactional scope
        TransactionSynchronizationManager.registerSynchronization(
            new TransactionSynchronization() {
                @Override public void afterCommit() {
                    redis.delete(key);                            // L2 evict
                    l1Cache.invalidate(key);                     // L1 evict (this instance)
                    redis.convertAndSend(INVALIDATION_CHANNEL, key);  // L1 evict (all instances)
                }
            }
        );
    }
}
```

**METRICS AND MONITORING:**

```java
// Spring Boot Actuator + Micrometer: expose Caffeine cache stats
@Configuration
public class CacheMetricsConfig {

    @Bean
    public CaffeineCache metricsEnabledProductCache(MeterRegistry registry) {
        com.github.benmanes.caffeine.cache.Cache<Object, Object> caffeine = Caffeine.newBuilder()
            .maximumSize(10_000)
            .expireAfterWrite(30, TimeUnit.SECONDS)
            .recordStats()
            .build();

        // Register with Micrometer: exposes cache.gets, cache.evictions, etc.
        CaffeineStatsCounter.registerWith(registry, "products.l1", caffeine);

        return new CaffeineCache("products", caffeine);
    }
}
// Grafana dashboard metrics:
// cache_gets_total{name="products.l1",result="hit"} / total → hit rate
// Expected L1 hit rate for hot keys: 60-80%
// If L1 hit rate < 20%: L1 not adding value (keys not hot enough, TTL too short)

// Alert: if L2 (Redis) hit rate drops below 80% → DB load increasing → scale or tune TTLs
```

---

### 🧪 Thought Experiment

**L1 COHERENCE: THE 30-SECOND STALE WINDOW**

Setup: L1 TTL = 30 seconds, L2 TTL = 15 minutes. No pub/sub. 20 instances.

Product 42 price is updated at T=0. Instance 5 (the writer) evicts L1 and L2. Instances 1-4, 6-20: L1 still has old price.

At T=15s: a user routed to Instance 7 sees old price. Fine for many use cases.
At T=30s: all L1 entries for product:42 have expired across all instances. All instances hit L2 - but L2 was deleted too! All hit DB (fresh price). All repopulate L1 and L2.

**Cost of no pub/sub:** 30-second stale window. 20 instances × 1 DB query at T=30s = 20 simultaneous DB queries (mini stampede). Acceptable for low-traffic services; not for high-traffic hot keys.

**With pub/sub:** Stale window = ~2ms. All instances evict L1 immediately. Next reads populate from DB/L2 within 10ms. Zero stampede (only 1 DB query per key per instance at staggered times).

---

### 🧠 Mental Model / Analogy

> A multi-level cache IS the CPU cache hierarchy applied to distributed software. Your CPU has: registers (immediate), L1 cache (4MB, ~1ns), L2 cache (8MB, ~4ns), L3 cache (shared, 32MB, ~10ns), RAM (100ns), NVMe SSD (~100μs), HDD (~10ms). Software multi-level cache: L1 Caffeine (10K entries, ~0.01ms), L2 Redis (10M entries, ~1ms), L3 DB (unlimited, ~10ms). The CPU solves coherence with hardware (MESI). Software must solve it manually (pub/sub). The cost profile is the same: each level is 10-100× slower but larger.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Multi-level cache = L1 (in-process, fast, small) → L2 (distributed Redis, slower, larger) → L3 (DB, slowest, largest). Read: check each level in order. Write: update lowest level (DB), propagate up.

**Level 2:** L1 (Caffeine): `maximumSize(10_000)`, `expireAfterWrite(30s)`, `recordStats()`. L2 (Redis): `expireAfterWrite(15min)`. On write: update Redis → publish invalidation to Caffeine on all instances. Handle coherence with short L1 TTL as safety net.

**Level 3:** L1 sizing strategy: use Caffeine's `recordStats()` to measure hit rate. If hit rate < 30%, the `maximumSize` may need to be larger (more entries), or the data access pattern isn't hot enough to benefit from L1. Optimal: L1 holds the "working set" (keys accessed in the last 30 seconds). L1 eviction policy: Caffeine's Window TinyLFU is optimal - scan-resistant (won't pollute the cache with a single sequential scan). For write-heavy hot keys: L1 `expireAfterAccess` (evict if not accessed in N seconds) is better than `expireAfterWrite` (evict only based on write time).

**Level 4:** Multi-level cache is a manifestation of **locality of reference** in time and space. In time: the same data is accessed repeatedly within a short window. In space: data accessed together is stored together. L1 exploits temporal locality: recently accessed keys are kept in local memory for fast re-access. The **L1 hit ratio** depends entirely on the access pattern: for Zipf-distributed access (a few keys get most traffic), even a small L1 (1,000 entries) can have a 90% hit rate if those 1,000 entries are the top-1,000 keys. For uniform random access (each key accessed at the same rate), L1 is useless - no key is "hot" enough to benefit from in-process caching. Therefore, **profile your access pattern before adding L1** - if your access is uniform, skip L1 and just use Redis (L2 only). The engineering cost of L1 coherence (pub/sub, short TTL) is only worth paying when L1 has a materially higher hit rate than L2.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ MULTI-LEVEL CACHE READ PATH                          │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Request: GET product:42                             │
│                                                      │
│  1. L1: Caffeine.getIfPresent("product:42")          │
│     HIT: return in 0.01ms ← most common path        │
│     MISS: proceed to L2                              │
│         ↓                                            │
│  2. L2: Redis GET product:42                         │
│  [MULTI-LEVEL ← YOU ARE HERE: L2 lookup]             │
│     HIT: return in 1ms; put(key, val) in L1          │
│     MISS: proceed to L3                              │
│         ↓                                            │
│  3. L3: DB SELECT WHERE id=42                        │
│     HIT: return in 15ms; populate L2 + L1           │
│     MISS: return null (negative cache candidate)     │
│                                                      │
│  Hit rate targets:                                   │
│  L1: 60-80% of requests (hot keys)                   │
│  L2: 15-30% (cold but warm keys)                     │
│  L3: < 10% (cache miss = DB query)                   │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
WRITE PATH: PUT /products/42 {price: 29.99}
→ ProductService.updateProduct(42, 29.99)
→ @Transactional: DB UPDATE price=29.99 - COMMIT

→ afterCommit (TransactionSynchronization):
   Redis SET product:42 {price:29.99} EX 900  (L2 update, all instances can read)
   L1 Caffeine PUT product:42 {price:29.99}    (L1 update on THIS instance)
   Redis PUBLISH cache:invalidations product:42 (broadcast to other instances)

→ All other instances receive pub/sub message:
   L1 Caffeine INVALIDATE product:42           (evict old value from L1)

READ PATH (on any instance, any time after write):
→ GET /products/42
→ L1 CHECK: HIT (this instance) → {price:29.99} in 0.01ms ✓
   OR: L1 MISS (other instance, post-invalidation) → L2 CHECK
→ L2 CHECK: HIT → {price:29.99} in 1ms → populate L1 ✓
   (All instances serve correct price within pub/sub latency ~2ms)
```

---

### ⚖️ Comparison Table

| Pattern                   | Latency          | Consistency           | Complexity | When to Use                    |
| ------------------------- | ---------------- | --------------------- | ---------- | ------------------------------ |
| Only DB                   | High (10-20ms)   | Perfect               | Lowest     | No caching needed              |
| Only Redis (L2)           | ~1ms             | Shared (consistent)   | Low        | Most multi-instance apps       |
| L1+L2 (no coherence)      | ~0.01ms (L1 hit) | Stale up to L1 TTL    | Low        | OK for staleness tolerance     |
| L1+L2 (pub/sub coherence) | ~0.01ms (L1 hit) | ~2ms coherence window | Medium     | High-traffic hot keys          |
| L1+L2+L3 (full pyramid)   | ~0.01ms          | ~2ms coherence window | High       | Large-scale, hot key workloads |

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                                                                                                                                 |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "More cache levels always means better performance" | L1 only helps if keys are "hot" (accessed repeatedly in short windows). For uniform random access: L1 has zero benefit but adds coherence complexity and memory overhead                                                                                |
| "L1 hit rate of 30% is good enough to justify L1"   | Not necessarily. If L1 TTL is 30s, the coherence window is 30s for non-pub/sub updates. If your data requires < 30s consistency, pub/sub is required - adding latency to every write. The benefit (30% L1 hits) must outweigh the write path complexity |
| "L2 Redis is always shared (consistent)"            | Redis Cluster with replica reads enabled (`READONLY` on replica connections) is eventually consistent - replicas may lag 1-50ms behind the primary. For fully consistent reads: always route to primary nodes                                           |

---

### 🚨 Failure Modes & Diagnosis

**1. L1 Memory Pressure - JVM GC Pauses Increase**

**Symptom:** After deploying multi-level cache, p99 latency increases (GC pause: 200ms STW every 5 minutes). L1 cache hit rate is high (75%).

**Root Cause:** L1 cache `maximumSize` is too large. 50K entries × 5KB avg = 250MB Caffeine cache in heap. With 512MB JVM heap, GC is spending significant time collecting cached objects.

**Diagnosis:**

```bash
# JVM GC monitoring
jstat -gc <pid> 1000  # Every 1 second
# Look for: FGCT (full GC time) increasing

# Heap histogram (find largest allocations)
jmap -histo:live <pid> | head -20
# If Caffeine arrays appear large: reduce maximumSize

# Caffeine stats (Spring Boot Actuator)
curl http://localhost:8080/actuator/caches
# Check entry count vs maximumSize
```

**Fix:**

```java
// Reduce maximumSize to reasonable level relative to heap
// Rule of thumb: L1 cache should not exceed 20% of heap
// 512MB heap × 20% = 102MB for cache
// 10K entries × ~5KB = 50MB ← reasonable

Caffeine.newBuilder()
    .maximumSize(10_000)  // Not 50,000
    .expireAfterWrite(30, TimeUnit.SECONDS)
    // Also: add weigher if entries vary widely in size
    .weigher((String key, Object value) -> measureApproxBytes(value))
    .maximumWeight(50_000_000)  // 50MB max, not count-based
    .build();
```

---

### 🔗 Related Keywords

**Prerequisites:** Cache-Aside, Distributed Cache, Cache Coherence, TTL
**Builds On This:** System Design, Performance Engineering
**Related:** Cache Coherence, Local Cache vs Distributed Cache, Cache Warming

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ L1      │ Caffeine (in-process, ~0.01ms, JVM heap)       │
│ L2      │ Redis (distributed, ~1ms, shared)              │
│ L3      │ Database (~10-20ms, source of truth)           │
│ READ    │ L1 → L2 → DB; populate all levels on miss      │
│ WRITE   │ DB → update L2 → invalidate L1 (all instances) │
│ COHERENCE│ Pub/sub L1 invalidation; short L1 TTL backup  │
│ L1 SIZE │ ≤ 20% JVM heap; use weigher for variable sizes │
│ L1 TTL  │ 30-60s (short for coherence); L2 TTL = 15min   │
│ BENEFIT │ Only for hot keys (Zipf distribution)          │
│ ONE-LINER│ "L1 absorbs hot keys at 0.01ms; L2 shares    │
│          │  state; DB is truth; coherence = pub/sub"     │
│ NEXT     │ Cache Warming → Write-Around                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Question) An e-commerce platform has 100M products, 80% of daily traffic hitting the top 10,000 products (Zipf distribution). You have 50 Spring Boot instances with 2GB heap each. Design an optimal multi-level caching strategy: what goes in L1, what goes in L2, appropriate TTLs, coherence strategy, and how you'd verify the cache is performing correctly in production.

**Q2.** (TYPE D - Failure Scenario) An L1+L2 cache with pub/sub coherence is deployed. The Redis pub/sub broker experiences a 2-minute outage (all `PUBLISH` calls fail silently, but `GET/SET` still work). During those 2 minutes, 3 products have their prices updated. After Redis pub/sub recovers, describe: (a) the exact state of each layer, (b) which user requests return incorrect data and for how long, (c) how you'd detect this in production monitoring, (d) how you'd design the system to limit the blast radius of pub/sub failures.
