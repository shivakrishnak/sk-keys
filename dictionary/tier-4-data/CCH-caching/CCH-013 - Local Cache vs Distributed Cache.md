---
version: 2
layout: default
title: "Local Cache vs Distributed Cache"
parent: "Caching"
grand_parent: "Technical Dictionary"
nav_order: 13
permalink: /caching/local-vs-distributed/
id: CCH-033
category: Caching
difficulty: ★★☆
depends_on: Distributed Cache, Multi-Level Cache, Cache Coherence
used_by: System Design, Caching, Microservices
related: Distributed Cache, Multi-Level Cache, Cache Coherence
tags:
  - caching
  - local-cache
  - distributed-cache
  - caffeine
  - redis
  - deep-dive
---

# CCH-023 - Local Cache vs Distributed Cache

⚡ TL;DR - Local cache (Caffeine, in-process) = zero network latency, JVM heap, per-instance (not shared across app instances - each instance has its own copy, potentially inconsistent); Distributed cache (Redis) = shared across all instances (consistent), network RTT ~1ms, scales beyond one JVM; use **local for hottest keys** (L1), **distributed for shared state** (L2), or **distributed-only for simplicity** in most multi-instance deployments.

| #495            | Category: Caching                                     | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Cache, Multi-Level Cache, Cache Coherence |                 |
| **Used by:**    | System Design, Caching, Microservices                 |                 |
| **Related:**    | Distributed Cache, Multi-Level Cache, Cache Coherence |                 |

---

### 🔥 The Problem This Solves

**THE CONSISTENCY-LATENCY TRADEOFF:**
A developer wants to cache user profile data. Local Caffeine cache: 0.01ms reads - perfect performance. But the application runs with 20 replicas. Instance 1 caches user 42's profile. Instance 2 hasn't cached it yet. User 42 updates their email (request hits Instance 5). Instance 5 evicts its local cache. Instances 1-4, 6-20: still have old email. Users see different emails depending on which instance handles their request. This is the **local cache consistency problem** in multi-instance deployments.

**REDIS LATENCY CONCERN:**
A developer uses Redis for everything. A single page load triggers 30 cache lookups for related data. 30 × 1ms Redis RTT = 30ms added latency. This is acceptable; but for a page with 100 cache lookups: 100ms from cache alone - a significant contributor.

---

### 📘 Textbook Definition

**Local Cache** (in-process cache): The cache lives in the same JVM/process as the application. Implementations: Caffeine (Java, best-in-class, Window TinyLFU eviction), Guava Cache (older, succeeded by Caffeine), ConcurrentHashMap (simple, no eviction), Ehcache (older, more feature-rich). Key properties: zero-latency reads (in-memory, no network), bounded by JVM heap, **not shared across application instances** - each instance maintains its own independent cache. On write to one instance: other instances are unaware unless explicitly notified (pub/sub).

**Distributed Cache** (remote cache): The cache is an external service shared by all application instances. Implementations: Redis (dominant), Memcached, Hazelcast, Apache Ignite. Key properties: network RTT per operation (~1ms local network), capacity scales beyond one JVM (TBs possible), **shared across all instances** - all instances read/write the same keyspace, ensuring consistency. Cache invalidation on any instance propagates to all instances automatically (by design - the key is deleted from the shared store).

**Hybrid (L1 Local + L2 Distributed)**: Both tiers. Reads: L1 first → L2 on L1 miss → DB on L2 miss. Writes: update DB → update L2 → broadcast L1 invalidation via pub/sub. Best of both: L1 speed for hot keys, L2 consistency across instances.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Local = fastest but per-instance (inconsistent across instances). Distributed = ~1ms but shared (consistent). Hybrid = best of both.

**One analogy:**

> Local cache = sticky note on your monitor. Distributed cache = whiteboard in the team meeting room. Your sticky note is private and instant - only you see it. If the team decides on a new policy (write/update), your sticky note still shows the old info unless someone tells you (pub/sub notification). The whiteboard is shared - everyone sees the same current state, but you have to walk to the meeting room to read it (network RTT).

- "Sticky note" → Caffeine local cache (per-instance, instant, private)
- "Whiteboard" → Redis distributed cache (shared, 1ms walk)
- "Team policy change" → write/update operation
- "Still shows old info" → cache coherence problem with local cache
- "Someone tells you to erase sticky note" → pub/sub L1 invalidation

**One insight:**
For **stateless, read-heavy microservices**, local cache is often sufficient IF data is relatively stable (configuration, feature flags, reference data). One key lookup of a feature flag 10,000 times/second per instance benefits enormously from local caching (0.01ms × 10,000 = 0.1 CPU seconds vs. 1ms × 10,000 = 10 CPU seconds for Redis). The consistency cost: feature flag updates take up to TTL (seconds) to propagate to all instances - acceptable for configuration, not acceptable for user balances.

---

### 🔩 First Principles Explanation

**LOCAL CACHE - CAFFEINE:**

```java
// Caffeine: best Java local cache library
// Window TinyLFU: scan-resistant, adapts to changing access patterns

@Configuration
public class LocalCacheConfig {

    @Bean("featureFlagCache")
    public Cache<String, Boolean> featureFlagCache() {
        return Caffeine.newBuilder()
            .maximumSize(500)                        // 500 feature flags
            .expireAfterWrite(30, TimeUnit.SECONDS)  // Refresh every 30s (short TTL for config)
            .refreshAfterWrite(20, TimeUnit.SECONDS) // Stale-while-revalidate: serve stale,
                                                     // refresh asynchronously after 20s
            .buildAsync(key -> featureFlagRepository.load(key))  // Async reloader
            .synchronous();                          // Return sync LoadingCache
    }

    @Bean("userPreferencesCache")
    public Cache<String, UserPreferences> userPreferencesCache() {
        return Caffeine.newBuilder()
            .maximumSize(1000)                       // Top 1000 users' preferences
            .expireAfterWrite(5, TimeUnit.MINUTES)   // User preferences: 5-min stale OK
            .expireAfterAccess(1, TimeUnit.MINUTES)  // Evict if not accessed in 1 min
            .recordStats()
            .build();
    }
}

// Usage: zero-network-latency reads
@Service
public class FeatureFlagService {

    @Autowired @Qualifier("featureFlagCache") private Cache<String, Boolean> flagCache;

    public boolean isFeatureEnabled(String flag, String userId) {
        // In-process: no Redis, no network, ~0.01ms
        return flagCache.get(flag, k -> featureFlagRepository.load(k));
    }
}
// 100,000 flag checks/second: 100,000 × 0.01ms = 1 CPU second (manageable)
// Same with Redis: 100,000 × 1ms = 100 CPU seconds (unacceptable)
// Local cache: 100× faster for high-frequency reads
```

**DISTRIBUTED CACHE - REDIS (SHARED ACROSS ALL INSTANCES):**

```java
// Redis: shared by all 20 application instances
// Write to Redis from Instance 5 → all 20 instances can read fresh value on next access

@Service
public class UserService {

    @Cacheable(
        value = "users",
        key = "#userId",
        condition = "#userId != null"
    )
    public User getUser(String userId) {
        // Spring @Cacheable with RedisCacheManager:
        // All 20 instances share this cache
        // If Instance 5 caches user:42 → all other instances get cache HIT on next read
        return userRepository.findById(userId).orElseThrow();
    }

    @CacheEvict(value = "users", key = "#userId")
    @Transactional
    public User updateUser(String userId, UserUpdateRequest req) {
        // @CacheEvict: deletes from Redis (shared) → ALL 20 instances now get MISS
        // → all instances re-fetch from DB → get fresh data ✓
        return userRepository.save(/* updated user */);
    }
}
// Distributed cache consistency: automatic.
// Any instance updates → DEL in shared Redis → all see fresh data next request.
// Cost: every read = 1ms Redis network RTT (vs 0.01ms local)
```

**SIDE-BY-SIDE CONSISTENCY COMPARISON:**

```java
// SCENARIO: Update user email from Instance 5 (of 20 instances)

// ---- LOCAL CACHE ONLY ----
// Instance 5: updates DB + evicts local Caffeine
// Instances 1-4, 6-20: still have old email in local cache
// User B (routed to Instance 7): sees OLD email for up to 5 minutes (TTL)
// INCONSISTENCY: same user, different answers from different instances ✗

// ---- DISTRIBUTED CACHE ONLY ----
// Instance 5: updates DB + Redis DEL "user:42" (shared Redis)
// All instances: next GET "user:42" → Redis MISS → DB → Redis SET → cached
// User B (routed to any instance): sees NEW email on next request ✓
// CONSISTENT: all instances serve same cached data (from shared Redis)

// ---- LOCAL + DISTRIBUTED (with pub/sub) ----
// Instance 5: updates DB
// afterCommit:
//   Redis DEL "user:42" (L2 evict)
//   Caffeine invalidate("user:42") (L1 evict on Instance 5)
//   Redis PUBLISH "cache:invalidations" "user:42"
// All instances: receive pub/sub → Caffeine invalidate("user:42")
// All instances: L1 = empty, L2 = empty → next read: L1 miss → L2 miss → DB → fresh ✓
// CONSISTENT: within pub/sub latency (~2ms) ✓
// FAST: subsequent reads go through L1 (0.01ms) ✓
```

**SPRING BOOT @CACHEABLE - SWAPPABLE BACKENDS:**

```java
// The same @Cacheable annotation works with EITHER backend
// Change only the CacheManager configuration

// Option 1: Local Caffeine backend
@Bean
public CacheManager caffeineCacheManager() {
    CaffeineCacheManager manager = new CaffeineCacheManager();
    manager.setCaffeine(Caffeine.newBuilder()
        .maximumSize(1000)
        .expireAfterWrite(5, TimeUnit.MINUTES));
    return manager;
}
// @Cacheable("users") → uses Caffeine (local, per-instance)

// Option 2: Distributed Redis backend
@Bean
public CacheManager redisCacheManager(RedisConnectionFactory factory) {
    RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
        .entryTtl(Duration.ofMinutes(5))
        .disableCachingNullValues();
    return RedisCacheManager.builder(factory)
        .cacheDefaults(config)
        .build();
}
// @Cacheable("users") → uses Redis (distributed, shared)

// Service code: IDENTICAL for both
@Cacheable("users")
public User getUser(String userId) {
    return db.findById(userId).orElseThrow();
}
// The @Cacheable abstraction hides local vs. distributed choice
```

---

### 🧪 Thought Experiment

**SINGLE-INSTANCE vs. MULTI-INSTANCE: WHERE LOCAL CACHE IS SAFE**

**Safe to use local cache:**

- Single-instance deployment (no other instances to be inconsistent with)
- Data that is read-only or changes extremely rarely (country list, currency codes, feature flags with >1 minute tolerance)
- Data where staleness for up to the TTL period is acceptable (e.g., "is this product in stock" - 1-minute stale OK)
- Performance-critical path where 1ms per lookup × 100K calls = 100 seconds CPU (unacceptable Redis cost)

**Unsafe to use local cache (use distributed):**

- User account data (email, password, roles) - must be consistent after update
- Session tokens - must be revocable across all instances instantly
- Rate limiting counters - must be shared across all instances (otherwise each instance has its own counter: 20 instances × individual limits = effectively no rate limiting)
- Inventory/stock counts - must reflect real availability, not per-instance stale count

---

### 🧠 Mental Model / Analogy

> Local vs. distributed cache = photocopying vs. shared Google Doc. Local: each person photocopies the document. Fast to read (it's right in front of you). But if the original changes, every person's photocopy is outdated until they recopy. Distributed: everyone reads from the same Google Doc. One edit → everyone sees it instantly. Slightly slower (must "open" the doc over the network). For highly collaborative data (changes visible to all): Google Doc (distributed). For reference data read 10,000 times with rare updates: photocopy (local cache with short TTL).

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Local (Caffeine): 0.01ms, per-instance, not shared - can be inconsistent across instances. Distributed (Redis): 1ms, shared, consistent. Single-instance: either works. Multi-instance: use distributed (or local with short TTL + pub/sub).

**Level 2:** Use local for: feature flags, static reference data, configuration, read-only data with tolerance for staleness. Use distributed for: user sessions, rate limits, user-specific data, anything requiring immediate consistency across instances. Spring @Cacheable: swap CacheManager (Caffeine vs. RedisCacheManager) - service code identical.

**Level 3:** Hybrid L1+L2: short L1 TTL (30-60s) + pub/sub invalidation. L1 absorbs hot reads. L2 provides consistency guarantee. Coherence window = pub/sub latency (~2ms). Safety net: even if pub/sub fails, L1 TTL bounds inconsistency to 60s max. Monitor both layers: `cache_gets_total{result="hit"}` for each tier. If L1 hit rate < 20%: L1 isn't adding value; simplify to L2 only.

**Level 4:** The consistency vs. latency tradeoff in caching is a microcosm of the larger distributed systems challenge. Local cache sacrifices consistency for latency; distributed cache sacrifices latency for consistency. The CAP theorem analogy: local cache is like an AP system (Available + Partition Tolerant - works independently of other instances, may be inconsistent). Distributed cache is like a CP system (Consistent + Partition Tolerant - all nodes see same state, but requires network connectivity). Hybrid L1+L2 is like AP with "eventual consistency" bounded by TTL or pub/sub. The right choice depends on the **consistency requirements** of the specific data: rate limit counters MUST be consistent (use distributed only); feature flags CAN be eventually consistent (local with short TTL or hybrid).

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│ LOCAL vs DISTRIBUTED: READ/WRITE FLOW                   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ LOCAL CACHE (Caffeine, 20 instances):                   │
│  Write (Instance 5):                                     │
│    DB UPDATE + Caffeine.invalidate(key) on Instance 5   │
│    Instances 1-4,6-20: cache unchanged ← INCONSISTENT  │
│  Read (Instance 7, before TTL):                          │
│    Caffeine.getIfPresent(key) → old value ✗             │
│                                                          │
│ DISTRIBUTED CACHE (Redis, 20 instances):                │
│  Write (Instance 5):                                     │
│    DB UPDATE + Redis DEL key (shared) ✓                 │
│  [LOCAL vs DIST ← YOU ARE HERE: shared DEL]             │
│  Read (Instance 7, right after write):                   │
│    Redis GET key → nil (MISS) → DB → fresh value ✓     │
│    CONSISTENT: same fresh data for all instances        │
│                                                          │
│ HYBRID (L1 Caffeine + L2 Redis):                        │
│  Write: DB + Redis DEL + pub/sub → all Caffeine evict   │
│  Read L1 HIT: 0.01ms (hot keys)                         │
│  Read L2 HIT: 1ms (warm keys)                           │
│  Read MISS: DB: 10-20ms                                 │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
DECISION TREE: Which cache to use?

Start → "Is this a single-instance deployment?"
  YES → Local cache is fine (Caffeine, no consistency concern)
  NO  → Multi-instance deployment → continue:

→ "Does the data change during the session/request window?"
  NO (static: country codes, feature flags rarely changed) →
    Local cache with short TTL (30-60s) is acceptable
  YES (user data, pricing, inventory, sessions) → continue:

→ "Is immediate consistency required (< 5 seconds)?"
  NO (aggregated reports, view counts, recommendations) →
    Local cache with short TTL (1-5 minutes) OK
  YES → continue:

→ "Is latency critical (hundreds of thousands of reads/second)?"
  NO → Distributed cache (Redis) only - simplest, consistent
  YES → Hybrid L1+L2:
    L1 Caffeine (0.01ms, 30-60s TTL, pub/sub invalidation)
    L2 Redis (1ms, 15min TTL, shared)

Examples:
  Feature flags: single-instance OR local TTL 30s ← OK
  User profile:  distributed Redis ← consistent across 20 instances
  Rate limits:   distributed Redis ONLY ← must be shared
  Product catalog (50M products, 80% top-1K): hybrid L1+L2
  Session tokens: distributed Redis ← must be revocable globally
```

---

### ⚖️ Comparison Table

| Dimension                    | Local Cache (Caffeine)   | Distributed Cache (Redis)         | Hybrid L1+L2                  |
| ---------------------------- | ------------------------ | --------------------------------- | ----------------------------- |
| Latency                      | ~0.01ms                  | ~1ms                              | ~0.01ms (L1 hit)              |
| Shared across instances      | No                       | Yes                               | Yes (L2)                      |
| Consistency (multi-instance) | Eventual (TTL-bounded)   | Immediate (after invalidation)    | ~2ms (pub/sub)                |
| Capacity                     | JVM heap (~100s MB)      | Cluster (GBs-TBs)                 | Both                          |
| Cache coherence              | None (per-TTL)           | Automatic (shared keyspace)       | Pub/sub L1 eviction           |
| Use case                     | Config, flags, read-only | Sessions, user data, shared state | Hot read-heavy workloads      |
| Failure mode                 | JVM OOM if too large     | Redis outage → all miss           | L2 failure → L1 fallback      |
| Spring @Cacheable            | CaffeineCacheManager     | RedisCacheManager                 | Custom (or use L1+L2 manager) |

---

### ⚠️ Common Misconceptions

| Misconception                          | Reality                                                                                                                                                                                                                    |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Local cache is always faster"         | For a single instance: yes. For multi-instance: local cache may serve stale data → incorrect behavior → apparent "bug", not a performance win. Consistency first, then optimize with L1 if needed                          |
| "Redis is required for all caching"    | Redis is required for shared/consistent state. For single-instance apps or data with tolerable staleness: local cache (Caffeine) is simpler, faster, and has zero operational cost                                         |
| "Rate limiting works with local cache" | Rate limiting counters MUST be shared across all instances. Local cache rate limiting: each of 20 instances tracks its own counter → 20 instances × individual limit = 20× the intended limit (no effective rate limiting) |

---

### 🚨 Failure Modes & Diagnosis

**1. Rate Limiting Ineffective Due to Local Cache**

**Symptom:** Rate limit is set to 100 requests/minute per user. In production (20 instances), a user successfully makes 2,000 requests/minute without being rate limited.

**Root Cause:** Rate limit counter stored in local Caffeine cache (per-instance). 20 instances × 100 req/min each = 2,000 req/min before any instance triggers the limit.

**Diagnosis + Fix:**

```java
// WRONG: local Caffeine counter (each instance has its own count)
@Service
public class RateLimiter {
    private final Cache<String, AtomicLong> counters = Caffeine.newBuilder()
        .expireAfterWrite(1, TimeUnit.MINUTES)
        .build();

    public boolean isAllowed(String userId) {
        AtomicLong count = counters.get(userId, k -> new AtomicLong(0));
        return count.incrementAndGet() <= 100;  // Only counts on THIS instance!
    }
}

// CORRECT: Redis INCR (shared across all instances)
@Service
public class DistributedRateLimiter {
    @Autowired private RedisTemplate<String, Long> redis;

    public boolean isAllowed(String userId) {
        String key = "rate:" + userId + ":" + minuteBucket();  // e.g., "rate:42:1234567"
        Long count = redis.opsForValue().increment("rate-limit:" + key);
        if (count == 1) {
            // First increment: set expiry (1 minute window)
            redis.expire("rate-limit:" + key, Duration.ofMinutes(1));
        }
        return count <= 100;  // Shared counter across ALL 20 instances ✓
    }

    private String minuteBucket() {
        return String.valueOf(System.currentTimeMillis() / 60000);
    }
}
```

---

### 🔗 Related Keywords

**Prerequisites:** Distributed Cache, Multi-Level Cache, Cache Coherence
**Builds On This:** System Design, Microservices
**Related:** Distributed Cache, Multi-Level Cache, Cache Coherence

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ LOCAL       │ Caffeine; 0.01ms; JVM heap; per-instance   │
│ DISTRIBUTED │ Redis; 1ms; shared across all instances    │
│ LOCAL OK    │ Config, flags, single-instance, stale OK   │
│ DIST NEEDED │ Sessions, user data, rate limits, shared   │
│ HYBRID      │ L1 Caffeine (hot) + L2 Redis (consistent)  │
│ CONSISTENCY │ Local: TTL-bounded; Distributed: immediate │
│ RATE LIMIT  │ MUST use distributed (shared counter)      │
│ SPRING      │ @Cacheable: swap CacheManager (both work)  │
│ FAILURE     │ Redis down: fall to DB; Local: no fallback │
│ ONE-LINER   │ "Local = fast + private; Distributed =    │
│             │  slightly slower + shared + consistent"    │
│ NEXT EXPLORE│ System Design → Distributed Systems        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Question) A microservices platform has 50 services, each running 10-50 instances. Each service needs: (a) service-specific configuration (rarely updated, 30-min staleness OK), (b) user permission checks (changes must propagate within 10 seconds), (c) a rate limiter (per-user API limits). Design a unified caching strategy that: minimizes operational overhead (ideally one caching infrastructure for all 50 services), achieves appropriate consistency for each data type, and can be configured per-use-case.

**Q2.** (TYPE D - Failure Scenario) Redis goes down. Your Spring Boot application has: (a) product catalog cached with `@Cacheable` + RedisCacheManager, (b) session tokens stored in Redis, (c) rate limiters using Redis INCR. Walk through what happens to each use case when Redis is unavailable for 3 minutes, and how you'd design each for graceful degradation (not total failure).
