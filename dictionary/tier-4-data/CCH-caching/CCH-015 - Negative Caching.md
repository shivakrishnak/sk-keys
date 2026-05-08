---
layout: default
title: "Negative Caching"
parent: "Caching"
grand_parent: "Technical Dictionary"
nav_order: 15
permalink: /caching/negative-caching/
id: CCH-015
category: Caching
difficulty: ★★★
depends_on: Cache-Aside, TTL, Cache Stampede
used_by: System Design, Caching, Security
related: Cache-Aside, TTL, Cache Stampede
tags:
  - caching
  - negative-caching
  - null-cache
  - dos-prevention
  - deep-dive
---

# CCH-015 - Negative Caching

⚡ TL;DR - Negative caching stores **the fact that a key does NOT exist** in the database as a cache entry - a "null" or "not found" result; this prevents repeated cache misses for non-existent keys from hammering the database, stopping both accidental N+1 miss patterns and deliberate cache-busting attacks (requesting random non-existent keys to force DB queries).

| #485            | Category: Caching                | Difficulty: ★★★ |
| :-------------- | :------------------------------- | :-------------- |
| **Depends on:** | Cache-Aside, TTL, Cache Stampede |                 |
| **Used by:**    | System Design, Caching, Security |                 |
| **Related:**    | Cache-Aside, TTL, Cache Stampede |                 |

---

### 🔥 The Problem This Solves

**CACHE-ASIDE DOESN'T CACHE "NOT FOUND" BY DEFAULT:**
Classic Cache-Aside: check cache → miss → query DB → if found, cache and return → if NOT found, return null. The problem: the "NOT found" case is not cached! Every future request for the same non-existent key skips the cache and hits the database - defeating the purpose of caching for that key.

**MALICIOUS CACHE BYPASS:**
An attacker knows your caching pattern. They send requests for random non-existent IDs: `GET /products/99999999`, `GET /products/88888888`, etc. Each request misses the cache (nothing to cache for non-existent products), hits the database with a SELECT, gets 0 rows, returns 404. 10,000 such requests/second = 10,000 DB queries/second for zero-row results. DB CPU spikes. Legitimate users experience degraded performance. This is a **cache-bypass DoS attack**.

---

### 📘 Textbook Definition

**Negative Caching** is the practice of caching **negative results** - queries that return no data (null, empty, "not found") - so that subsequent requests for the same non-existent resource are served from cache without hitting the underlying data store. A **null cache entry** (also called a **sentinel value**) is stored with a short TTL to indicate "this resource does not exist." Implementations: (1) Cache a sentinel value: `redis.set("product:99999", "NULL", Duration.ofMinutes(5))` - read: if value is "NULL", return 404 without DB query. (2) Cache the `Optional.empty()` Java object or a dedicated `NotFoundResult`. (3) **Bloom Filter**: a probabilistic data structure that can answer "definitely not in DB" (no false negatives) - if Bloom filter says NO, return 404 without cache or DB check; if YES, check cache then DB. Bloom filter trades memory for zero false negatives: a key either has never been inserted (definite NO) or might exist (check DB). Used by: Cassandra (block cache), HBase, RocksDB, PostgreSQL's pg_prewarm - all use Bloom filters to skip disk reads for non-existent keys.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Cache the "not found" result too - store a null/sentinel value so repeated requests for non-existent data hit the cache, not the DB.

**One analogy:**

> A secretary answers calls for the CEO. Most callers ask for scheduled meetings. But some callers ask for people who never existed at the company. Without negative caching: every "is John Smith in?" → secretary checks HR database → no record → "no John Smith here." Same caller tomorrow: same DB check. With negative caching: "no John Smith here - I'll note that for the next 24 hours. If anyone calls asking for John Smith, I'll say no immediately without checking the database again."

- "Checking HR database for a non-existent person" → DB query for missing record
- "Noting John Smith doesn't exist for 24 hours" → null cache entry with TTL
- "Answer immediately without checking DB" → cache hit on null entry → fast 404

**One insight:**
Negative caching must use a **shorter TTL** than positive caching. If a product (ID=42) is deleted from the database and cached as "exists" (positive cache), the TTL controls the stale window. If ID=99999 is created _after_ being cached as "not found" (negative cache), the negative cache entry must expire before the next lookup reveals the newly created item. Typical split: positive TTL = 10-60 minutes, negative TTL = 1-5 minutes. The negative TTL bounds how long a newly created item is invisible to the system.

---

### 🔩 First Principles Explanation

**IMPLEMENTATION - SENTINEL VALUE:**

```java
// Cache-Aside with negative caching using sentinel value
@Service
public class ProductService {

    private static final String NULL_SENTINEL = "NULL";
    private static final Duration POSITIVE_TTL = Duration.ofMinutes(10);
    private static final Duration NEGATIVE_TTL = Duration.ofMinutes(2);  // shorter!

    public Optional<Product> getProduct(String productId) {
        String cacheKey = "product:" + productId;

        // Step 1: Check cache
        String cachedValue = redisTemplate.opsForValue().get(cacheKey);

        if (cachedValue != null) {
            if (NULL_SENTINEL.equals(cachedValue)) {
                // NEGATIVE CACHE HIT: we know this product doesn't exist
                return Optional.empty();  // Fast 404 - no DB query
            }
            // POSITIVE CACHE HIT: deserialize and return
            return Optional.of(objectMapper.readValue(cachedValue, Product.class));
        }

        // Step 2: Cache miss - query database
        Optional<Product> product = productRepository.findById(productId);

        if (product.isPresent()) {
            // POSITIVE RESULT: cache normally with longer TTL
            redisTemplate.opsForValue().set(cacheKey,
                objectMapper.writeValueAsString(product.get()),
                POSITIVE_TTL);
        } else {
            // NEGATIVE RESULT: cache "not found" with shorter TTL
            redisTemplate.opsForValue().set(cacheKey, NULL_SENTINEL, NEGATIVE_TTL);
        }

        return product;
    }

    // On product creation: invalidate negative cache entry (if any)
    @Transactional
    public Product createProduct(ProductCreateRequest req) {
        Product product = productRepository.save(new Product(req));

        // Invalidate any negative cache for this ID (now product exists)
        redisTemplate.delete("product:" + product.getId());

        return product;
    }
}
```

**BLOOM FILTER FOR NEGATIVE CACHING (REDIS):**

```java
// Bloom filter: space-efficient probabilistic set
// "Is this product ID definitely NOT in the database?"
// False positive possible: "might exist" → check DB/cache → actually doesn't
// False negative impossible: "definitely doesn't exist" is always correct

@Service
public class ProductServiceWithBloom {

    // Redisson provides Redis Bloom Filter support
    private final RBloomFilter<String> productBloomFilter;

    @PostConstruct
    public void initBloomFilter() {
        productBloomFilter = redissonClient.getBloomFilter("product:bloom");
        // Initialize: expected 1M items, 1% false positive rate
        productBloomFilter.tryInit(1_000_000, 0.01);

        // Pre-populate on startup with all existing product IDs
        // (or populate on first access - depends on dataset size)
        List<String> existingIds = productRepository.findAllIds();
        existingIds.forEach(id -> productBloomFilter.add(id));
    }

    public Optional<Product> getProduct(String productId) {
        // Step 1: Bloom filter check (in-memory, no network RTT)
        if (!productBloomFilter.contains(productId)) {
            // DEFINITELY NOT in DB: skip cache AND DB entirely
            return Optional.empty();  // 0ms - pure memory check
        }

        // Bloom filter says "might exist" → proceed with cache/DB lookup
        return getProductFromCacheOrDB(productId);
    }

    @Transactional
    public Product createProduct(ProductCreateRequest req) {
        Product product = productRepository.save(new Product(req));

        // Add to Bloom filter so future lookups find it
        productBloomFilter.add(product.getId());

        return product;
    }

    // NOTE: Bloom filters don't support deletion
    // For deletions: use Counting Bloom Filter, or rebuild the filter periodically
    // Alternative: use Cuckoo filter (supports deletion)
}
// Bloom filter size for 1M items at 1% FPR: ~9.6 bits/item = ~1.2MB
// vs. HashSet of 1M UUIDs: ~32MB
// Bloom filter is 26× more memory-efficient with 1% false positive rate
```

**SPRING CACHE WITH NEGATIVE CACHING:**

```java
// Spring @Cacheable doesn't cache null by default
// unless="#result == null" condition PREVENTS caching nulls
// To enable negative caching: remove the unless condition

@Cacheable(
    value = "products",
    key = "#productId"
    // NO unless="#result == null" → null IS cached
)
public Product getProductNullable(String productId) {
    return productRepository.findById(productId).orElse(null);
    // Returns null for non-existent products
    // Spring Cache WILL cache this null value
    // Next call for same ID: returns null from cache (no DB query) ✓
}

// For @Cacheable null caching to work in Redis:
// Must configure serializer to handle nulls:
// RedisTemplate: use Jackson2JsonRedisSerializer with allowNullValues=true

// Recommended: use Optional<> and cache the empty Optional
@Cacheable(value = "products", key = "#productId")
public Optional<Product> getProduct(String productId) {
    return productRepository.findById(productId);
    // Optional.empty() is serializable and safely represents "not found"
    // Spring Cache: caches both Optional.of(product) and Optional.empty()
}
```

---

### 🧪 Thought Experiment

**CACHE-BYPASS ATTACK WITH SEQUENTIAL PRODUCT IDs:**

E-commerce site with sequential product IDs (1, 2, 3, ..., 10,000). Attacker sends: `GET /products/10001`, `GET /products/10002`, ..., `GET /products/99999` (90,000 non-existent IDs at 10,000/second). Without negative caching: 10,000 DB queries/second, all returning 0 rows. DB CPU at 100%. Legitimate users experience 5-second latency spikes.

**With negative caching:** After the first request for each non-existent ID (1 DB query each), the result is cached. Subsequent requests for the same ID: cache hit (sentinel value), 0 DB queries. After 90,000 distinct IDs are cached: attacker exhausts the "unique IDs" pool. If they cycle back to already-cached IDs: 0 DB queries.

**Additional protection:**

1. Rate limiting (nginx, API gateway): limit to 100 requests/second per IP
2. Bloom filter: all 90,000 non-existent IDs filtered in memory (0 cache/DB hits)
3. UUID product IDs: attacker can't guess valid IDs
4. WAF: detect sequential ID scanning pattern

Negative caching alone reduces DB load significantly but doesn't eliminate all attack vectors. Defense-in-depth is required.

---

### 🧠 Mental Model / Analogy

> Negative caching is like a bouncer with a "do not admit" list. A person tries to enter. If their name is on the "banned" list (negative cache): instant rejection, no background check (DB query). If their name isn't on the banned list: run the background check (cache/DB lookup). Without the banned list: every banned person requires a full background check every visit - expensive. Negative caching builds the list and keeps it current (TTL = how long the ban is remembered).

- "Banned list" → null/sentinel entries in Redis
- "Instant rejection" → negative cache hit → fast 404
- "Background check" → DB query
- "How long ban is remembered" → negative TTL (shorter than positive TTL)
- "New person joins" → product created → remove from negative cache list

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Negative caching = cache "not found" results with a short TTL. Next request for the same non-existent key hits the cache (null result), not the database. Prevents repeated DB queries for non-existent resources.

**Level 2:** Use a sentinel value (`"NULL"`) or `Optional.empty()` as the cached not-found value. Set a shorter TTL for negative entries (1-5 minutes) than positive entries (10-60 minutes). On resource creation, delete the negative cache entry immediately. For Spring `@Cacheable`, remove `unless="#result == null"` to enable null caching.

**Level 3:** For security-critical applications: combine negative caching with a Bloom filter. Bloom filter handles "definitely not in DB" at memory speed (no Redis RTT). Negative cache handles recently-queried keys. Together: near-zero DB impact for non-existent resource attacks. Bloom filter memory: ~10 bits/item at 1% FPR. For 10M products: ~12.5MB in RAM. Use Redis Bloom (RedisBloom module) for distributed Bloom filter. Note: Bloom filters don't support deletions - use Cuckoo filters if product deletion is common.

**Level 4:** Negative caching is part of a broader security concept: **input validation at the cache layer**. By caching "impossible" responses (null, 404), the system creates a self-reinforcing protection: the cache absorbs invalid requests without ever reaching the database. This is the foundation of **cache poisoning defense** - the system never caches incorrect positive results, but aggressively caches correct negative results. At scale (Cloudflare, Akamai), negative caching is built into the CDN layer: a 404 response for a non-existent URL is cached at the edge for minutes, protecting the origin server from repeated enumeration attacks. The TTL on negative caches must be short enough to allow for newly created resources to become visible within a SLA-bounded latency (typically 5 minutes is standard for product catalog lookups).

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ WITH AND WITHOUT NEGATIVE CACHING                    │
├──────────────────────────────────────────────────────┤
│                                                      │
│ WITHOUT negative caching:                            │
│   GET /products/99999                                │
│   Redis GET product:99999 → nil (MISS)               │
│   DB SELECT ... WHERE id=99999 → 0 rows              │
│   Return 404                                         │
│   (no cache entry created - MISS every time!)        │
│                                                      │
│ Second request for same ID:                          │
│   Redis GET product:99999 → nil (MISS again!)        │
│   DB SELECT ... WHERE id=99999 → 0 rows again        │
│   EVERY request for ID 99999 hits the DB ← problem  │
│                                                      │
│ WITH negative caching:                               │
│   1st request: Miss → DB → 0 rows                   │
│   Redis SET product:99999 "NULL" EX 120 (2 min TTL) │
│   Return 404                                         │
│                                                      │
│   [NEG CACHE ← YOU ARE HERE: null cached]            │
│   2nd-Nth requests within 2 min:                     │
│   Redis GET product:99999 → "NULL"                   │
│   Return 404 immediately - NO DB query ✓             │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**USER LOOKUP API WITH NEGATIVE CACHING + BLOOM FILTER:**

```
API: GET /users/unknown-uuid-12345
→ UserService.getUser("unknown-uuid-12345")
→ [NEGATIVE CACHE ← YOU ARE HERE]

1. Bloom filter check (in-process, ~0.01ms):
   bloomFilter.contains("unknown-uuid-12345") → false
   → "DEFINITELY not in DB" - return Optional.empty() (fast 404) ✓
   No Redis query, no DB query

For a recently-created user (Bloom filter updated on create):
1. Bloom filter: contains("new-user-456") → true (might exist)
2. Redis GET user:new-user-456 → "NULL" (negative cache hit, TTL 2 min)
   → return Optional.empty() (404) - TTL expires in 2 min

Why? User was created 30 seconds ago - within the 2-minute negative TTL:
→ The user isn't found because negative cache hasn't expired yet!

Fix: on user creation → immediately delete negative cache:
POST /users → create user → Redis DEL user:new-user-456
→ Next GET: Redis MISS → DB query → found → positive cache → 200 OK ✓

Attack scenario (random UUID requests):
10,000 random UUIDs/second:
→ Bloom filter: all 10,000 → false (not in DB) → all fast-rejected in memory
→ Redis queries: 0, DB queries: 0
→ Attacker gets 10,000 × 0.01ms responses = 10ms CPU cost vs. 10,000 DB queries avoided
```

---

### ⚖️ Comparison Table

| Approach                  | Performance                               | Security                      | Complexity | Correctness                          |
| ------------------------- | ----------------------------------------- | ----------------------------- | ---------- | ------------------------------------ |
| No negative caching       | DB hit every miss                         | Vulnerable to scan attacks    | Low        | Correct (DB is truth)                |
| Sentinel value            | Redis hit after 1st miss                  | Partially protected           | Low        | Correct (short TTL)                  |
| Bloom filter              | In-memory, zero Redis/DB for non-existent | Strong (scan attacks blocked) | Medium     | ~1% false positives (extra DB check) |
| Redis Bloom (distributed) | Redis check per request                   | Strong                        | Medium     | ~1% false positives                  |

---

### ⚠️ Common Misconceptions

| Misconception                                                           | Reality                                                                                                                                                                                                                                                                                    |
| ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Caching null is a bug"                                                 | Caching null is a deliberate optimization (negative caching). However, it must use a SHORTER TTL than positive caches to ensure newly created resources become visible quickly                                                                                                             |
| "Spring @Cacheable unless='#result==null' is always the right approach" | `unless="#result == null"` DISABLES negative caching (prevents null from being cached). For high-traffic systems with many non-existent key requests, removing this condition (enabling null caching) is the correct choice                                                                |
| "Bloom filters have false negatives"                                    | Bloom filters have FALSE POSITIVES (may say "might exist" when the key doesn't), but NO FALSE NEGATIVES (never says "doesn't exist" when the key does exist). This is the safe direction for caching: you might do an extra DB check, but you never return a 404 for something that exists |
| "Negative TTL can be the same as positive TTL"                          | Negative TTL should be shorter (1-5 minutes). If a new product is created and the negative TTL is 1 hour, the product is invisible for up to 1 hour after creation                                                                                                                         |

---

### 🚨 Failure Modes & Diagnosis

**1. New Resource Invisible Due to Negative Cache Stale Entry**

**Symptom:** User creates a product (POST /products → 201 Created). Immediately queries it (GET /products/42 → 404 Not Found). This inconsistency is reported as a bug.

**Root Cause:** A previous failed request for `/products/42` created a negative cache entry with a 5-minute TTL. The product was just created (ID happened to be 42 - sequential IDs). The negative cache entry hasn't expired.

**Diagnosis:**

```bash
redis-cli GET product:42
# Returns: "NULL" (negative cache entry still active)

redis-cli TTL product:42
# Returns: 284 (284 seconds remaining on negative TTL)
```

**Fix:**

```java
// On product creation: always delete the potential negative cache entry
@Transactional
public Product createProduct(ProductCreateRequest req) {
    Product product = productRepository.save(new Product(req));

    // Invalidate negative cache (if any) for this new product's ID
    redisTemplate.delete("product:" + product.getId());

    return product;
}
// Prevention: use UUID product IDs (not sequential) - impossible to pre-cache negative for ID not yet known
```

---

### 🔗 Related Keywords

**Prerequisites:** Cache-Aside, TTL, Cache Stampede
**Builds On This:** System Design, Security
**Related:** Cache-Aside, TTL, Cache Stampede

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT        │ Cache "not found" as a sentinel value      │
│ PREVENTS    │ Repeated DB miss queries; scan attacks     │
│ TTL         │ SHORTER than positive TTL (1-5 min)        │
│ ON CREATE   │ DEL negative cache for new resource ID     │
│ SPRING      │ Remove unless="#result==null" to enable    │
│ BLOOM       │ In-memory "definitely not in DB" check     │
│ FALSE POS   │ Bloom: 1% extra DB check (safe)            │
│ FALSE NEG   │ Bloom: NEVER (safe - won't miss existing)  │
│ ONE-LINER   │ "Cache the 404 too - next miss hits cache  │
│             │  not DB; short TTL to allow creation"      │
│ NEXT EXPLORE│ Distributed Cache → Cache Coherence        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Security Question) Your API uses sequential integer IDs for products. A threat model analysis identifies that an attacker can enumerate all product IDs from 1 to 10M using 10,000 requests/second. Design a defense-in-depth strategy using: negative caching, Bloom filter, rate limiting, and ID design change. For each layer, explain what it prevents and what it doesn't.

**Q2.** (TYPE D - Failure Scenario) A Bloom filter is initialized with 1M existing product IDs on application startup. After 6 months, the product catalog has grown to 5M products (4M new products were added via API). A Bloom filter for 1M items at 1% FPR is now holding 5M items. Walk through: (a) what happens to the false positive rate, (b) how this affects application correctness, (c) how you detect this condition in production, (d) how you remediate without service downtime.
