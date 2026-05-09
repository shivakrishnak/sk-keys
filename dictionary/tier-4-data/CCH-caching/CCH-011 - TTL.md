---
version: 1
layout: default
title: "TTL"
parent: "Caching"
grand_parent: "Technical Dictionary"
nav_order: 11
permalink: /caching/ttl/
id: CCH-011
category: Caching
difficulty: ★☆☆
depends_on: Caching, Cache-Aside
used_by: Caching, System Design, Distributed Systems
related: Cache Invalidation, Eviction Policies, Cache-Aside
tags:
  - caching
  - ttl
  - expiration
  - redis
---

# CCH-011 - TTL

⚡ TL;DR - TTL (Time-To-Live) is a duration assigned to a cached entry after which it is automatically deleted or treated as expired - the simplest form of cache invalidation: no explicit delete needed, the cache self-heals after the TTL, trading a bounded staleness window for zero invalidation complexity.

| #481            | Category: Caching                                  | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------------------- | :-------------- |
| **Depends on:** | Caching, Cache-Aside                               |                 |
| **Used by:**    | Caching, System Design, Distributed Systems        |                 |
| **Related:**    | Cache Invalidation, Eviction Policies, Cache-Aside |                 |

---

### 🔥 The Problem This Solves

**CACHE NEVER EXPIRES WITHOUT TTL:**
Without TTL, a cached value lives until explicitly deleted. If the source data changes and no code path triggers a cache delete, the cache silently serves stale data indefinitely. TTL provides a last-resort expiry: even if explicit invalidation is missed (bug, direct DB write, forgotten code path), the entry automatically expires after the TTL.

---

### 📘 Textbook Definition

**TTL (Time-To-Live)** is a duration (in seconds or milliseconds) associated with a cache entry, defining how long the entry lives in the cache before automatic expiration. When a cache entry's TTL expires, the cache marks it as invalid and either deletes it immediately or on next access. Two variants: **TTL-on-write** (timer starts when entry is written - `EXPIRE` in Redis); **TTL-on-access** (`EXPIREATAT` / Caffeine `expireAfterAccess` - timer resets on every read, entry expires only if not accessed for the duration). Redis commands: `SET key value EX seconds`, `EXPIRE key seconds`, `TTL key` (returns remaining TTL), `PERSIST key` (remove TTL, make persistent). HTTP caching uses TTL via `Cache-Control: max-age=300` (300 seconds). DNS TTL controls how long resolvers cache DNS records. JWT `exp` claim is a TTL for authentication tokens.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
TTL = automatic expiry timer on a cache entry - after X seconds, the entry is deleted and the next read re-fetches from the source.

**One analogy:**

> A parking meter. You park (cache entry), set the meter for 2 hours (TTL). After 2 hours, your spot is automatically freed (entry deleted) - the parking enforcement officer (Redis) removes you without you having to do anything. Set too short: you're moved constantly even when still shopping. Set too long: spot is blocked long after you've left.

- "Set meter for 2 hours" → `SET product:42 {data} EX 7200`
- "Spot freed automatically" → Redis auto-deletes on TTL expiry
- "Set too short" → frequent cache misses → high DB load
- "Set too long" → stale data for too long → consistency issues

**One insight:**
TTL is a staleness-freshness dial. Short TTL (10s) → near-real-time accuracy, high DB load. Long TTL (1 hour) → low DB load, potentially stale data. The right TTL is the shortest duration your business can tolerate for stale reads. For product prices: 5 minutes (max $X revenue risk per stale window). For DNS records: 300 seconds (5 minutes to propagate a DNS change). For static assets: 1 year (filenames include content hash, no stale risk).

---

### 🔩 First Principles Explanation

**REDIS TTL COMMANDS:**

```bash
# Set with TTL on write (most common)
SET product:42 '{"id":42,"price":9.99}' EX 600    # expires in 600 seconds (10 min)
SET product:42 '{"id":42,"price":9.99}' PX 60000   # expires in 60000 ms (1 min)
SET product:42 '{"id":42,"price":9.99}' EXAT 1735689600  # expires at Unix timestamp

# Add TTL to existing key
EXPIRE product:42 600       # set/reset TTL to 600 seconds
EXPIREAT product:42 1735689600  # expire at specific Unix timestamp
PERSIST product:42          # remove TTL, make entry permanent

# Check remaining TTL
TTL product:42   # returns: 547 (seconds remaining), -1 (no TTL), -2 (key doesn't exist)
PTTL product:42  # returns remaining TTL in milliseconds

# TTL on access (Caffeine - not natively in Redis):
# Caffeine: expireAfterAccess(5, MINUTES) - resets timer on every read
# Useful for session data: keep alive while user is active, expire when idle
```

**TTL DESIGN GUIDELINES:**

```
Data Type                    | Recommended TTL     | Rationale
-----------------------------|---------------------|----------------------------------
User session                 | 30 minutes          | Balance security vs. UX
Product catalog              | 5-15 minutes        | Occasional price/stock changes
User profile                 | 30-60 minutes       | Rarely changes
Search autocomplete          | 5 minutes           | May reflect recent content
Homepage recommendations     | 1-5 minutes         | Frequently updated
Real-time stock price        | 5-30 seconds        | Accuracy critical
Static reference data (countries, currencies) | 24 hours  | Changes rarely
JWT access token             | 15 minutes          | Security: short-lived
Refresh token                | 7-30 days           | UX: don't re-login daily
DNS A records                | 300-3600 seconds    | Change propagation speed
CDN edge cache               | 1 year (immutable files) | Content-hashed filenames

TTL TOO SHORT → symptoms:
  - High cache miss rate (> 20%)
  - Database CPU elevated
  - p99 latency high (many requests hit DB)

TTL TOO LONG → symptoms:
  - Users see stale data after writes
  - Customer support tickets about "old prices"
  - Post-deploy: old API responses cached for hours
```

**JITTER ON TTL (PREVENT MASS EXPIRY):**

```java
// Without jitter: all products cached at the same time have the same TTL
// At TTL expiry: all products expire simultaneously → all concurrent reads miss → stampede

// BAD: no jitter
redisTemplate.opsForValue().set("product:" + id, product, Duration.ofMinutes(10));
// If 10,000 products were cached 10 minutes ago → all expire at the same moment

// GOOD: TTL jitter (randomize within ±20% of base TTL)
int baseTtlSeconds = 600;  // 10 minutes
int jitter = (int)(baseTtlSeconds * 0.2 * Math.random());  // 0-120 seconds random
int finalTtl = baseTtlSeconds + jitter;  // 600-720 seconds

redisTemplate.opsForValue().set("product:" + id, product, Duration.ofSeconds(finalTtl));
// 10,000 products now expire spread over 2 minutes, not all at once
// No stampede - expirations are distributed in time
```

---

### 🧪 Thought Experiment

**TTL for an authentication token:** a JWT access token with `exp` claim 15 minutes. User opens the app at T=0, token issued. At T=14:58, user clicks a button that triggers an API call. Token is valid (2 seconds before expiry). The API call takes 3 seconds. By the time the server validates the token: T=15:01 - expired. Request fails with 401 despite the user just being authenticated.

**Solution:** Client-side token refresh: refresh the access token when less than 2 minutes remain (check before API calls). This demonstrates that TTL choices affect user experience design, not just caching - any TTL system needs a renewal/refresh strategy to avoid sharp "cliff" expirations that interrupt user workflows.

---

### 🧠 Mental Model / Analogy

> TTL is the expiration date on food in your fridge. A carton of milk (cache entry) expires in 7 days (TTL). You don't have to remember to throw it out - the date tells you when it's no longer fresh. Short expiry (1 day): always fresh but you throw away a lot of usable milk (frequent cache misses). Long expiry (30 days): lower waste but you might drink bad milk (stale data). The right expiry matches when the milk actually goes bad (how quickly your source data changes).

---

### 📶 Gradual Depth - Four Levels

**Level 1:** TTL = automatic cache expiry. Set with `SET key value EX seconds`. Expired entries are deleted automatically by Redis. Use as a safety net for stale data.

**Level 2:** Combine TTL with explicit invalidation: explicit `DEL` on write for immediate freshness, TTL as a backup. Apply jitter (±20% random) to prevent synchronized mass expiry. Use `expireAfterAccess` for session-like data (evict idle entries).

**Level 3:** Redis lazy expiration: Redis doesn't actively scan all keys for expiry (too expensive). On `GET`: if key has expired, Redis deletes it and returns nil. Background job: Redis runs a periodic job every 100ms, sampling 20 random keys with TTL, deleting expired ones. If > 25% of sample is expired, repeat immediately. This means a key might persist a few hundred milliseconds past its TTL before being sampled. Don't design systems that require exact TTL expiry timing.

**Level 4:** TTL-based invalidation trades staleness for simplicity. The key systems insight: TTL converts "when was data last updated?" (event-driven, requires explicit invalidation) into "how old is this data?" (time-based, automatic). For many use cases, "data less than 10 minutes old is good enough" is a simpler and more robust invariant than "data matches the DB at this instant." The tradeoff is the bounded staleness window - acceptable for read-heavy systems where the cost of occasional stale reads is lower than the complexity of explicit invalidation. At scale, TTL-based caching is the foundation of CDN content delivery (Cache-Control headers), DNS (DNS TTL), and HTTP client caches.

---

### ⚙️ How It Works (Mechanism)

```
Redis TTL Expiry Mechanism:
  Lazy expiry: checked on access (GET returns nil if expired)
  Active expiry: background job samples random keys every 100ms

  No guarantee: key may persist a few ms past TTL (lazy expiry timing)

  maxmemory + eviction: separate from TTL
  TTL expiry ≠ eviction policy - both can remove keys but for different reasons
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
T=0:   Cache: SET product:42 {price:9.99} EX 600
T=100: Cache: GET product:42 → {price:9.99} ✓ (TTL: 500 remaining)
T=400: DB: UPDATE products SET price=29.99 WHERE id=42
       (No explicit invalidation - relying on TTL)
T=401: Cache: GET product:42 → {price:9.99} (STALE - TTL: 199 remaining)
T=600: TTL expires → Redis deletes product:42
T=601: Cache: GET product:42 → nil (MISS)
       DB: SELECT → {price:29.99}
       Cache: SET product:42 {price:29.99} EX 600
T=602: Cache: GET product:42 → {price:29.99} ✓ (FRESH)

Total stale window: 200 seconds (T=400 to T=600)
With explicit invalidation at T=400: stale window = 0
```

---

### ⚖️ Comparison Table

| Aspect    | Short TTL (10s)         | Medium TTL (5min)              | Long TTL (1hr)    |
| --------- | ----------------------- | ------------------------------ | ----------------- |
| Freshness | Near real-time          | Acceptable for most use cases  | Potentially stale |
| DB load   | High (frequent misses)  | Moderate                       | Low               |
| Miss rate | High                    | Moderate                       | Low               |
| Use for   | Real-time prices, stock | Product catalog, user profiles | Reference data    |

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                            |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| "TTL expires keys at exactly the specified time" | Redis may delay expiry by up to a few hundred milliseconds due to lazy + sampled active expiry. Don't design systems requiring exact-second expiry |
| "Shorter TTL is always safer"                    | Shorter TTL increases DB load proportionally. Very short TTLs can cause cache stampede and database overload                                       |
| "TTL = cache eviction"                           | TTL is time-based expiry. Eviction is memory-pressure-based removal. They are independent mechanisms in Redis                                      |

---

### 🔗 Related Keywords

**Prerequisites:** Caching, Cache-Aside
**Builds On This:** Caching, System Design
**Related:** Cache Invalidation, Eviction Policies, Cache-Aside

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ SET TTL     │ SET key val EX 600 (seconds)               │
│ CHECK TTL   │ TTL key → seconds remaining (-1=no TTL)    │
│ REMOVE TTL  │ PERSIST key                                │
│ JITTER      │ ±20% random to prevent mass expiry         │
│ SAFETY NET  │ Always set TTL even with explicit del       │
│ EXPIRY LAG  │ Up to ~200ms past TTL (lazy expiry)        │
│ ONE-LINER   │ "Automatic cache cleanup: expire after X   │
│             │  seconds, re-fetch on next access"          │
│ NEXT EXPLORE│ Eviction Policies → Cache Stampede          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This

**Q1.** (TYPE B - Application Question) Your application caches user session data (userId, roles, cart) with a 30-minute TTL using `expireAfterAccess`. A user is actively using the app for 2 hours. How does `expireAfterAccess` behave differently from `expireAfterWrite` for this use case? Which is more appropriate, and why?
