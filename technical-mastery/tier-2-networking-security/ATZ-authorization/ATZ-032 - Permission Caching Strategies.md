---
id: ATZ-032
title: "Permission Caching Strategies"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★☆
depends_on: ATZ-013, ATZ-015, ATZ-030
used_by: ATZ-039, ATZ-046, ATZ-049, ATZ-050
related: ATZ-030, ATZ-039, ATZ-046
tags:
  - security
  - authorization
  - caching
  - performance
  - intermediate
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 32
permalink: /technical-mastery/authorization/permission-caching-strategies/
---

⚡ **TL;DR** - Authorization checks on every request hit the
permission store (database, OPA, SpiceDB) - expensive at scale.
Caching permission decisions reduces latency from ~5ms to ~0.1ms.
The tradeoff: stale cache means revoked permissions still work.
Design principle: TTL must be shorter than the worst acceptable
revocation lag. For a 60-second TTL: a fired employee's access
persists for up to 60 seconds after revocation - acceptable for
most; unacceptable for financial trading systems.

---

### 📊 Entry Metadata

| #032 | Category: Authorization | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-013 RBAC, ATZ-015 ABAC, ATZ-030 Externalized Auth | |
| **Used by:** | ATZ-039, ATZ-046, ATZ-049, ATZ-050 | |
| **Related:** | ATZ-030 Externalized Auth, ATZ-039 Perf, ATZ-046 Authorization at Scale | |

---

### 📘 Textbook Definition

Permission caching stores authorization decisions or permission
data in fast memory (application-local cache, Redis) to avoid
repeated calls to the permission store (database, policy engine,
relationship database). Caching strategies range from caching
the raw decision (allow/deny for a specific request triple) to
caching the user's full permission set and re-evaluating locally.
The key design parameters are: TTL (time-to-live, controls
revocation lag), cache granularity (per-user vs per-request),
cache invalidation mechanism (TTL expiry vs event-driven
invalidation), and cache scope (local in-process vs shared Redis).

---

### ⚙️ How It Works (Mechanism)

**Cache granularity tradeoffs:**

```
┌────────────────────────────────────────────────────────┐
│       Permission Cache Strategies                      │
├────────────────────────────────────────────────────────┤
│                                                        │
│  STRATEGY 1: Cache full user permission set            │
│  Key: user_id                                          │
│  Value: {roles: [...], permissions: [...]}             │
│  TTL: 60 seconds                                       │
│  Pros: one DB query per user per minute                │
│  Cons: permissions evaluated in-process (not OPA)     │
│        large cache entries for many-role users         │
│                                                        │
│  STRATEGY 2: Cache decision per (user, resource, action│
│  Key: "allow:{user_id}:{action}:{resource_id}"         │
│  Value: true/false                                     │
│  TTL: 30 seconds                                       │
│  Pros: fine-grained, exact TTL per decision            │
│  Cons: huge cache (one entry per (u,r,a) combination)  │
│        resource-specific decisions flood cache         │
│                                                        │
│  STRATEGY 3: Event-driven invalidation                 │
│  Cache user permissions, TTL = 5 minutes               │
│  On permission change: publish event to message bus    │
│  All instances: invalidate that user's cache entry     │
│  Pros: shorter propagation delay than pure TTL        │
│  Cons: more complex, message bus dependency            │
│                                                        │
│  CHOOSE: TTL based on security requirement             │
│  Near-real-time revocation: 5-10s TTL (high DB load)  │
│  Normal enterprise: 30-60s TTL (acceptable tradeoff)   │
│  High-security (finance, admin): no cache (always DB)  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Spring Cache + event-driven invalidation**

```java
@Service
public class CachedPermissionService {

    @Cacheable(value = "user-permissions",
               key = "#userId",
               unless = "#result == null")
    public UserPermissions getPermissions(String userId) {
        // Cache miss: load from database
        return permissionRepo.findByUserId(userId);
    }

    @CacheEvict(value = "user-permissions",
                key = "#event.userId")
    @EventListener
    public void onPermissionChanged(
            PermissionChangedEvent event) {
        // Immediately invalidate cache when permissions change
        // Next request will load fresh permissions from DB
        log.info("Cache evicted for user: {}",
            event.getUserId());
    }
}

// Redis cache config with TTL fallback
@Bean
public RedisCacheConfiguration cacheConfiguration() {
    return RedisCacheConfiguration.defaultCacheConfig()
        .entryTtl(Duration.ofSeconds(60)) // max staleness
        .disableCachingNullValues()
        .serializeValuesWith(
            RedisSerializationContext.SerializationPair
                .fromSerializer(new GenericJackson2JsonRedisSerializer()));
}
```

**Example - BAD: no cache, synchronous permission DB query**

```java
// BAD: DB query on every request
// At 1000 req/s: 1000 permission queries per second
// Permission store becomes the bottleneck
@GetMapping("/documents/{id}")
public Document getDocument(@PathVariable String id,
                              Principal user) {
    // DB call on EVERY request
    if (!permissionRepo.hasPermission(
            user.getName(), "document:" + id, "read")) {
        throw new ForbiddenException();
    }
    return docRepo.findById(id).orElseThrow();
}
```

---

*Authorization category: ATZ | Entry: ATZ-032 | v5.0*