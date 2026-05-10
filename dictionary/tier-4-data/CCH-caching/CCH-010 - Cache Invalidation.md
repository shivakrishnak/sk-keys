---
version: 2
layout: default
title: "Cache Invalidation"
parent: "Caching"
grand_parent: "Technical Dictionary"
nav_order: 10
permalink: /caching/cache-invalidation/
id: CCH-010
category: Caching
difficulty: ★★★
depends_on: Cache-Aside, Write-Through, TTL
used_by: System Design, Caching, Distributed Systems
related: Cache-Aside, TTL, Cache Stampede
tags:
  - caching
  - cache-invalidation
  - stale-data
  - consistency
  - deep-dive
---

# CCH-010 - Cache Invalidation

⚡ TL;DR - Cache invalidation is the process of removing or marking as stale cached data when the underlying source data changes; it is famously described as one of the "two hard things in computer science" because doing it correctly - with no stale reads and no unnecessary cache misses - requires solving the distributed consistency problem at application scale.

| #480            | Category: Caching                           | Difficulty: ★★★ |
| :-------------- | :------------------------------------------ | :-------------- |
| **Depends on:** | Cache-Aside, Write-Through, TTL             |                 |
| **Used by:**    | System Design, Caching, Distributed Systems |                 |
| **Related:**    | Cache-Aside, TTL, Cache Stampede            |                 |

---

### 🔥 The Problem This Solves

**STALE CACHE = INCORRECT USER EXPERIENCE:**
Without invalidation, a cached response stays in cache until TTL expires, regardless of whether the underlying data has changed. A product's price is updated from $9.99 to $29.99 in the database. Customers still see $9.99 for 10 minutes (the TTL). Some customers may order at the wrong price, creating refund issues, customer complaints, and revenue loss.

**OVER-INVALIDATION = CACHE BECOMES USELESS:**
Invalidate too aggressively (delete everything on any write) and the cache hit rate drops to near zero - every request misses the cache and hits the database. The cache provides no benefit, but adds latency (Redis RTT on every miss).

**CACHE INVALIDATION FINDS THE BALANCE:**
Invalidate exactly the data that has changed, at exactly the right time, so reads return correct data while the cache still serves the maximum number of requests from memory.

---

### 📘 Textbook Definition

**Cache Invalidation** is the mechanism by which cached data is removed, expired, or marked stale when the source data changes. Three primary approaches: **(1) Time-To-Live (TTL)**: data automatically expires after a fixed duration - simplest, always eventually consistent, but stale window = TTL duration. **(2) Event-based invalidation**: the writer explicitly signals the cache to remove or update the affected entry on every write - no stale window (zero or near-zero), but requires coordinating the write path and the invalidation step. **(3) Change Data Capture (CDC)-driven invalidation**: a CDC connector (Debezium) captures DB changes from the WAL and publishes invalidation events - the cache consumer removes or refreshes the affected keys; decoupled from the write path, reliable, millisecond propagation. Cache invalidation strategies vary in granularity: **key-level invalidation** (delete specific `product:42`), **tag-based invalidation** (delete all keys tagged with `category:electronics`), **wildcard invalidation** (delete all keys matching `product:*` - dangerous in Redis: use `SCAN` not `KEYS *`), **full cache flush** (emergency only - drops all cached data).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Cache invalidation = removing the right cache entries at the right time when source data changes - too early loses hit rate; too late returns stale data.

**One analogy:**

> A restaurant menu board (cache) shows today's specials. When the kitchen runs out of a dish (data change), the waiter should erase that item from the board (invalidation). If they forget: customers order the dish, only to be told "sorry, we're out" (stale data → bad UX). If the waiter erases everything on any kitchen change (over-invalidation): the board is always blank, and customers must ask the waiter for every item (cache miss → always hits the kitchen). Perfect invalidation: erase exactly the sold-out items, immediately.

- "Menu board" → Redis cache
- "Kitchen runs out" → DB data changes
- "Erase item" → `Redis.delete("special:42")`
- "Forget to erase" → stale cache → wrong data
- "Erase everything" → over-invalidation → 0% hit rate

**One insight:**
"There are only two hard things in Computer Science: cache invalidation and naming things." - Phil Karlton. The difficulty isn't implementing delete (trivial). The difficulty is: (1) **knowing what to invalidate** - which cache keys depend on the changed data? (a single DB row might affect dozens of cached views, lists, and aggregate queries); (2) **when to invalidate** - before, during, or after the DB write? Race conditions lurk in each choice; (3) **atomicity** - invalidating the cache and writing the DB as a single atomic operation is impossible without 2PC.

---

### 🔩 First Principles Explanation

**INVALIDATION STRATEGIES WITH CODE:**

```java
// STRATEGY 1: TTL-BASED (simplest, always eventually consistent)
redisTemplate.opsForValue().set("product:42", product, Duration.ofMinutes(10));
// product:42 auto-expires after 10 minutes regardless of DB changes
// Stale window: up to 10 minutes
// Implementation effort: zero (just set TTL on cache write)
// When to use: tolerable stale window; read-heavy; rarely-changing data

// STRATEGY 2: EXPLICIT INVALIDATION ON WRITE (event-based)
@Transactional
public Product updateProductPrice(String productId, BigDecimal newPrice) {
    Product product = productRepository.findById(productId).orElseThrow();
    product.setPrice(newPrice);
    product = productRepository.save(product);

    // Invalidate specific key after DB commit
    redisTemplate.delete("product:" + productId);

    // Also invalidate derived/aggregate caches:
    redisTemplate.delete("category:" + product.getCategoryId() + ":products");  // product list
    redisTemplate.delete("featured:products");  // if this product was in featured list

    return product;
}
// Zero stale window after successful invalidation
// Challenge: must know all dependent cache keys at write time

// STRATEGY 3: TAG-BASED INVALIDATION (group-level invalidation)
// Problem: product:42 affects multiple cache keys - hard to track all of them
// Solution: tag-based grouping

// On cache write: store key → tags mapping
public void cacheProductWithTags(Product product) {
    String key = "product:" + product.getId();
    redisTemplate.opsForValue().set(key, product, Duration.ofHours(1));

    // Register this key under relevant tags
    redisTemplate.opsForSet().add("tag:category:" + product.getCategoryId(), key);
    redisTemplate.opsForSet().add("tag:brand:" + product.getBrandId(), key);
    redisTemplate.opsForSet().add("tag:featured", key);  // if featured
}

// On category update: invalidate all keys tagged with this category
public void invalidateByCategoryTag(String categoryId) {
    String tagKey = "tag:category:" + categoryId;
    Set<String> keysToInvalidate = redisTemplate.opsForSet().members(tagKey);
    if (keysToInvalidate != null && !keysToInvalidate.isEmpty()) {
        redisTemplate.delete(keysToInvalidate);  // batch delete
    }
    redisTemplate.delete(tagKey);  // clean up tag index too
}
// Tag-based: O(1) to find all keys to invalidate for a given category/brand/tag

// STRATEGY 4: CDC-DRIVEN INVALIDATION (decoupled, reliable)
@Component
public class ProductCacheInvalidator {

    @KafkaListener(topics = "ecommerce.public.products")  // Debezium CDC topic
    public void handleProductChange(ProductCdcEvent event) {
        String productId = event.getAfter() != null
            ? event.getAfter().getId()
            : event.getBefore().getId();

        // Invalidate all affected cache keys
        List<String> keysToInvalidate = new ArrayList<>();
        keysToInvalidate.add("product:" + productId);

        if (event.getBefore() != null) {
            // Also invalidate old category (if category changed)
            keysToInvalidate.add("category:" + event.getBefore().getCategoryId() + ":products");
        }
        if (event.getAfter() != null) {
            keysToInvalidate.add("category:" + event.getAfter().getCategoryId() + ":products");
        }

        redisTemplate.delete(keysToInvalidate);

        log.info("CDC-driven cache invalidation: {} keys cleared for product {}",
            keysToInvalidate.size(), productId);
    }
}
// CDC-driven: application write path doesn't handle invalidation
// Invalidation happens asynchronously via Kafka CDC events
// Latency: 50-200ms (Debezium + Kafka + consumer)
// Benefit: decoupled, reliable (Kafka retains events), handles all write paths (direct DB writes too)
```

**THE RACE CONDITION IN INVALIDATION:**

```
Timeline of a race between a write + invalidation and a concurrent read:

T=0ms  Writer: DB UPDATE (new price = $29.99)
T=1ms  Concurrent Reader A: cache MISS (TTL expired at T=0)
T=2ms  Reader A: DB SELECT → gets NEW value ($29.99) - correct
T=3ms  Writer: Redis DEL product:42 (invalidation)
T=4ms  Reader A: Redis SET product:42 {price: $29.99} (re-populates with new value) ✓

OK: reader re-populates with new value - no stale data

PROBLEMATIC SCENARIO:
T=0ms  Reader B: cache MISS (TTL expired)
T=1ms  Reader B: DB SELECT → gets OLD value ($9.99) - DB read happens BEFORE UPDATE
T=2ms  Writer: DB UPDATE (new price = $29.99)
T=3ms  Writer: Redis DEL product:42 (invalidation)
T=4ms  Reader B: Redis SET product:42 {price: $9.99} (re-populates with OLD DB value)
Result: cache has $9.99 but DB has $29.99 → STALE CACHE UNTIL TTL

Duration of stale: depends on next invalidation or TTL
Probability: low (requires exact interleaving) but non-zero under load

Fix: Write-Through (update cache atomically with DB write, not just delete)
Or: accept brief stale window (bounded by TTL) as a practical tradeoff
```

---

### 🧪 Thought Experiment

**WHAT CACHE KEYS ARE AFFECTED BY ONE DB ROW CHANGE?**

`products` table row (id=42, name="Widget", price=9.99, category_id=5, brand_id=3, featured=true) is updated: price → $29.99.

**Potentially affected cache keys:**

1. `product:42` - direct product key
2. `category:5:products` - list of all products in category 5
3. `brand:3:products` - list of products by brand 3
4. `featured:products` - list of featured products (price may affect featured ranking)
5. `search:results:{any query that returned product 42}` - search result caches
6. `homepage:recommendations` - if product 42 is in recommendations
7. `user:*:cart` - any user with product 42 in cart (cart shows price)
8. `user:*:wishlist` - any user with product 42 in wishlist
9. `price:alert:42` - price alert check cache

**Conclusion:** A single DB row change can invalidate dozens to hundreds of cache keys. This is the "hard" part of cache invalidation - not deleting a single key, but knowing _all_ the derived views, lists, and aggregates that depended on that row. Tag-based invalidation, event-driven invalidation, and short TTLs all address this complexity differently.

---

### 🧠 Mental Model / Analogy

> Cache invalidation is like managing a library's card catalog (cache) when books are moved, relabeled, or checked out (data changes). When one book's location changes, the simple approach: update that one card (key-level invalidation - efficient). But if the book appears in 10 subject category indexes (derived views), you must update all 10. If you don't know all the indexes it appears in: use a TTL (the cards automatically expire after 30 days - eventually correct). The hard case: a book reclassified to a new genre must be removed from ALL old-genre indexes and added to the new one - which indexes had it? That's the cache invalidation problem.

- "Card catalog" → Redis cache
- "Books moved/relabeled" → DB data changes
- "Update that one card" → key-level invalidation (`Redis.delete("product:42")`)
- "10 subject category indexes" → derived cache views (category list, brand list, featured)
- "Cards auto-expire after 30 days" → TTL-based invalidation
- "Which indexes had it?" → the hard problem of tracking all dependent cache keys

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Cache invalidation: delete cache key when source data changes. Two strategies: (1) TTL - expires automatically (simple, some stale risk); (2) explicit delete on write (no stale, must track all affected keys). The hard part: knowing which keys to delete.

**Level 2:** Use `@CacheEvict` for Spring Cache invalidation. For multi-key invalidation (one write affects many views), consider tag-based invalidation or version-stamped keys. Set TTL as a safety net even when using explicit invalidation. Monitor cache hit rate after invalidation changes - over-invalidation shows as a drop in hit rate.

**Level 3:** Event-driven invalidation via CDC (Debezium → Kafka → cache invalidator service) decouples the write path from invalidation. This handles ALL writes to the database, including direct DB modifications, migration scripts, and writes from other services - not just writes through your application. Use SCAN (not KEYS _) for pattern-based invalidation in Redis: `SCAN 0 MATCH product:_ COUNT 100`iterates incrementally without blocking Redis. Delete keys in batches (pipeline or multi-delete):`redis.delete(keyList)` is more efficient than N individual deletes.

**Level 4:** The fundamental challenge of cache invalidation is the **distributed cache invalidation problem**: in a system with multiple cache nodes (Redis Cluster) and multiple application instances, invalidating all relevant caches consistently and atomically is equivalent to a distributed consensus problem. When Application A invalidates cache for product:42, Application B on a different node may have already cached a stale version and won't know to invalidate it unless the invalidation is broadcast to all nodes. Solutions: (1) Redis keyspace notifications - publish to all subscribers when a key is deleted; (2) pub/sub broadcast - invalidation event goes to all app instances; (3) tag-based invalidation with a shared tag index in Redis - all instances share the same tag-to-key mapping. Version-stamped cache keys (`product:v7:42`) solve stale data elegantly: instead of invalidating, increment the version counter; old keys become unreachable (they'll expire by TTL), new reads use the new version key - no invalidation race conditions, but TTL waste on old version entries.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ CACHE INVALIDATION TIMING OPTIONS                    │
├──────────────────────────────────────────────────────┤
│                                                      │
│ OPTION 1: Invalidate BEFORE DB write                 │
│   Redis DEL product:42                               │
│   DB UPDATE product SET price=29.99 WHERE id=42      │
│   Risk: concurrent reader sees miss, queries DB      │
│     during UPDATE → gets old value → repopulates     │
│     cache with stale data (race condition!)          │
│                                                      │
│ OPTION 2: Invalidate AFTER DB write (recommended)    │
│   DB UPDATE product SET price=29.99 WHERE id=42      │
│   Redis DEL product:42                               │
│   Risk: brief window where cache has old value       │
│     (between DB commit and Redis DEL)               │
│   [INVALIDATION ← YOU ARE HERE: after DB commit]    │
│                                                      │
│ OPTION 3: Invalidate in DB post-commit hook          │
│   @Transactional + TransactionSynchronization        │
│   .afterCommit() → Redis DEL product:42              │
│   Risk: Redis failure after DB commit (accept it;    │
│     next TTL expiry → stale resolved)                │
│                                                      │
│ OPTION 4: CDC-driven (decoupled, async)              │
│   DB write → WAL → Debezium → Kafka → consumer       │
│     → Redis DEL product:42                          │
│   Latency: 50-200ms                                  │
│   Benefit: zero impact on write path, handles all    │
│     DB writes regardless of source                   │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**E-COMMERCE PRICE UPDATE WITH FULL INVALIDATION:**

```
Admin: PUT /admin/products/42 {price: 29.99}
→ ProductAdminService.updatePrice(42, 29.99)
→ [INVALIDATION ← YOU ARE HERE: what needs to be cleared?]

1. @Transactional:
   UPDATE products SET price=29.99 WHERE id=42
   COMMIT

2. afterCommit() hook fires:
   Redis pipeline (batch delete):
   → DEL product:42          (direct product cache)
   → DEL product:42:details  (detailed product view)
   → DEL category:5:products (product list for category 5 - includes product 42)
   → DEL featured:products   (if product 42 was in featured list)
   → DEL search:cache:electronics (search result that may have included product 42)
   Redis pipeline executed in one RTT (efficient)

3. CDN: if product page is CDN-cached:
   → Invalidate CDN edge cache via CloudFront API:
   createInvalidation("/products/42*")

4. Next read: GET /products/42
   → Redis HIT? NO (just deleted)
   → DB: SELECT * FROM products WHERE id=42 → {price: 29.99}
   → Redis: SET product:42 {price:29.99} EX 600
   → Response: {price: 29.99} ✓

5. Reads 2-∞ (cache warm):
   → Redis HIT → {price: 29.99} ✓

Result: zero stale reads after invalidation completes (~2ms after DB commit)
```

---

### ⚖️ Comparison Table

| Strategy                 | Stale Window                  | Complexity | Miss Rate Impact                    | Best For                             |
| ------------------------ | ----------------------------- | ---------- | ----------------------------------- | ------------------------------------ |
| TTL only                 | 0 to TTL duration             | Minimal    | None (gradual)                      | Tolerable stale; rarely changing     |
| Explicit delete on write | Near-zero (ms)                | Medium     | Minimal (1 miss per write)          | Frequently read after write          |
| Tag-based invalidation   | Near-zero                     | High       | Potential stampede on bulk          | Complex object graphs                |
| CDC-driven               | 50-200ms                      | High       | None (async)                        | Decoupled, multi-writer environments |
| Version-stamp key        | Zero (no invalidation needed) | Medium     | Low (old version TTL wastes memory) | High-read, schema-stable keys        |

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                                                                                                                    |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Short TTL = good cache invalidation strategy"      | Short TTL reduces stale window but increases DB load (more cache misses = more DB reads). TTL is a safety net, not a substitute for explicit invalidation                                                                                  |
| "Invalidating before the DB write is safer"         | Invalidating before the DB write creates a window where the cache is empty AND the DB has the old value. Concurrent readers will re-populate the cache with the old value just as the write commits. Invalidate AFTER the DB write commits |
| "KEYS \* in Redis is fine for pattern invalidation" | `KEYS *` is an O(N) blocking operation that freezes Redis for all other clients during execution. Always use `SCAN` for pattern-based invalidation. `KEYS *` is only safe for development/debugging                                        |
| "Cache invalidation is only a cache layer concern"  | Cache invalidation is an application design concern. What you cache, how you key it, and what writes trigger invalidation must be planned at the service design level - not afterthought                                                   |

---

### 🚨 Failure Modes & Diagnosis

**1. Stale Data After Write (Invalidation Missed)**

**Symptom:** Product price was updated in the admin panel at 2pm. Users still see the old price in the storefront at 2:15pm. DB shows new price. Cache shows old price.

**Root Cause Checklist:**

```bash
# 1. Check if key is in Redis
redis-cli GET product:42
# If still returns old price → invalidation failed (delete never executed)

# 2. Check Redis TTL
redis-cli TTL product:42
# Returns seconds until expiry; if 500+ seconds, TTL too long AND delete wasn't executed

# 3. Check if the application instance that ran the write is the same
# as the one that holds the cache (only relevant for in-process caches like Caffeine)
# For Redis (shared cache): this doesn't apply

# 4. Check if @CacheEvict fired
# Add logging in @CacheEvict method:
@CacheEvict(value = "products", key = "#productId")
public Product updatePrice(String productId, BigDecimal price) {
    log.info("CACHE EVICT: products:{}", productId);
    // ...
}
# Check logs for the eviction log line at 2pm

# 5. Check if the write went through a code path that skips invalidation
# (e.g., batch update via SQL, admin DB script, migration)
# → Solution: use CDC-driven invalidation (catches all writes regardless of path)
```

**Fix:** Add CDC-driven invalidation as a safety net in addition to explicit invalidation. CDC catches all write paths including direct DB modifications.

---

### 🔗 Related Keywords

**Prerequisites:** Cache-Aside, Write-Through, TTL
**Builds On This:** System Design, Distributed Systems
**Related:** Cache-Aside, TTL, Cache Stampede

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STRATEGIES  │ TTL | Explicit DEL | Tag-based | CDC       │
│ TIMING      │ Invalidate AFTER DB commit (not before)    │
│ REDIS DEL   │ Use pipeline for multi-key batch delete    │
│ PATTERN DEL │ Use SCAN (not KEYS *) - non-blocking       │
│ SPRING      │ @CacheEvict for key-level invalidation     │
│ FALLBACK    │ TTL is always a safety net (set it)        │
│ CDC BENEFIT │ Catches ALL write paths incl. direct SQL   │
│ HARD PART   │ Knowing ALL cache keys affected by 1 write │
│ ONE-LINER   │ "Delete the right cache keys at the right  │
│             │  time - TTL as safety net, explicit for now"│
│ NEXT EXPLORE│ TTL → Eviction Policies                    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Question) A user's shopping cart is cached. The cart contains: item IDs, quantities, computed subtotals, and applied discounts. Multiple write paths can modify cart-relevant data: (a) user adds item to cart, (b) product price changes (admin update), (c) discount expires (scheduled job), (d) inventory depletes (concurrent order by another user). Design the cache invalidation strategy for each write path. For each, specify: what cache keys to invalidate, when to invalidate, and what the stale window risk is.

**Q2.** (TYPE D - Failure Scenario) A social media post shows a like count. The like count is cached for 5 minutes (TTL). After a viral post gets 1 million likes in 2 minutes, users complain that the count is wildly out of date. The product team wants "near-real-time" like counts (< 5 second stale). Evaluate: (a) reducing TTL to 5 seconds - impact on DB load and Redis hit rate; (b) event-driven invalidation on every like - impact on Redis writes and concurrency; (c) a hybrid approach using Write-Behind for like counts with 5-second flush. Which approach do you recommend and why?
