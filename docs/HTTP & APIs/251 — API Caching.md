---
layout: default
title: "API Caching"
parent: "HTTP & APIs"
nav_order: 251
permalink: /http-apis/api-caching/
number: "0251"
category: HTTP & APIs
difficulty: ★★☆
depends_on: HTTP, REST, HTTP Caching Headers
used_by: REST APIs, CDN, Browser Caching, Microservices
related: ETag/Cache-Control, API Rate Limiting, CDN, Redis
tags:
  - api
  - caching
  - cache-control
  - etag
  - cdn
  - intermediate
---

# 251 — API Caching

⚡ TL;DR — API caching stores the responses to API requests so that subsequent identical requests are served from the cache (faster, cheaper) rather than re-executing the full backend logic; the primary mechanism is HTTP's `Cache-Control` directive, which tells clients, CDNs, and proxies how long to cache a response and when to revalidate with the server.

┌──────────────────────────────────────────────────────────────────────────┐
│ #251 │ Category: HTTP & APIs │ Difficulty: ★★☆ │
├──────────────┼────────────────────────────────────┼──────────────────────┤
│ Depends on: │ HTTP, REST, HTTP Caching Headers │ │
│ Used by: │ REST APIs, CDN, Browser Caching, │ │
│ │ Microservices │ │
│ Related: │ ETag/Cache-Control, API Rate Limit,│ │
│ │ CDN, Redis │ │
└──────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A product catalog API returns 10,000 products. The catalog changes once per day.
Every time any user loads the catalog page: the web server queries the database,
serializes 10,000 JSON objects, and sends 2MB of JSON over the wire. Thousands of
requests per second, all hitting the database, all serializing the same data that
hasn't changed since yesterday. Without caching: the database is hammered with
identical read queries; latency for users is consistently high; serving costs scale
linearly with traffic.

**THE INVENTION MOMENT:**
HTTP caching was designed into HTTP/1.0 (1996) with the `Expires` header and
formalized comprehensively in HTTP/1.1 (RFC 2068, 1997) with `Cache-Control`.
The design intent: reduce bandwidth, reduce latency, reduce server load by enabling
network intermediaries (proxies, CDNs) and clients to store and reuse responses.
The key insight: for GET requests, the response can be cached at MULTIPLE LEVELS —
browser, CDN, reverse proxy, server-side cache — each serving different latency/
cost tradeoffs.

---

### 📘 Textbook Definition

**API Caching** is the practice of storing HTTP responses at one or more cache layers
(client, proxy, CDN, server-side) to serve subsequent requests from cache rather than
re-executing backend logic. HTTP defines caching semantics via `Cache-Control` (primary
directive), `ETag`/`Last-Modified` (conditional request validation), and `Vary`
(cache key dimension control). **Cache-Control** directives: `max-age=N` (cache for N seconds),
`no-cache` (must revalidate each use), `no-store` (never cache), `private` (browser-only,
not CDN), `public` (CDN-cacheable), `s-maxage=N` (shared cache TTL). **Conditional
requests** use `If-None-Match` (ETag) or `If-Modified-Since` to revalidate: if the
resource hasn't changed, server returns `304 Not Modified` (empty body, zero bandwidth).
**Server-side caching**: Redis/caffeine cache the result of backend computations;
transparent to HTTP clients.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
API caching stores responses for reuse — clients and CDNs return cached responses
directly; server-side caches skip database queries — reducing latency, bandwidth, and backend load.

**One analogy:**

> API caching is like a library book reservation system.
> Instead of going to the publisher (database) every time someone wants the same book
> (API response), the library (cache) keeps copies on its shelves (cache storage).
> The publisher says "this edition is valid for 30 days" (Cache-Control: max-age=2592000).
> After 30 days, the library checks if a new edition is available (conditional request),
> and only orders a new copy if one exists (304 Not Modified otherwise).

**One insight:**
`Cache-Control: no-cache` is the most misunderstood directive: it does NOT mean "don't
cache." It means "cache the response but revalidate with the server before each use."
`Cache-Control: no-store` is what actually prevents caching. Always be precise.

---

### 🔩 First Principles Explanation

**HTTP CACHE CONTROL DIRECTIVES:**

```
Cache-Control response header — server tells caches how to handle this response:

  max-age=3600       → cache is valid for 3600 seconds (client + CDN)
  s-maxage=3600      → shared cache (CDN) TTL; overrides max-age for CDNs
  public             → any cache (CDN, proxy) can cache this
  private            → only browser cache; CDN must not cache (personalized responses)
  no-cache           → cache allowed, but MUST revalidate before serving (fresh check)
  no-store           → never cache (sensitive data: bank transactions, medical records)
  must-revalidate    → once stale, must revalidate; cannot serve stale response
  stale-while-revalidate=60 → serve stale for up to 60s while fetching fresh in background
  stale-if-error=86400 → serve stale for up to 1 day if origin returns 5xx

Examples by use case:
  Static asset (image, JS):    Cache-Control: public, max-age=31536000, immutable
  Product catalog (changes daily): Cache-Control: public, max-age=3600, s-maxage=86400
  User profile (personalized): Cache-Control: private, max-age=300
  Auth token response:         Cache-Control: no-store
  Real-time data (live prices):Cache-Control: no-cache (or short max-age=1)
```

**CACHE HIERARCHY:**

```
Request flow with multiple cache layers:

  Browser Cache     CDN (Cloudflare/Fastly)     Origin Server (your API)
       │                     │                         │
  GET /catalog         GET /catalog               computes response
       │                     │                         │
  Cache hit? ─YES──→ return cached (0ms)
       │
  Cache miss? ─NO──→ ask CDN
                     Cache hit? ─YES──→ return cached (10ms, no origin call)
                     Cache miss? ─NO──→ ask origin
                                       → 150ms + DB query + serialization
                                       ← 200 OK + Cache-Control headers
                     CDN caches response
                     ← return to browser
                     Browser caches response
```

**CONDITIONAL REQUESTS — REVALIDATION:**

```
First request (cache cold):
  GET /api/catalog
  ← 200 OK
     ETag: "abc123"
     Cache-Control: max-age=3600

After 3600 seconds (cache expired):
  GET /api/catalog
  If-None-Match: "abc123"    ← include ETag from previous response

  If catalog unchanged:
  ← 304 Not Modified          ← NO BODY, just headers; use cached body
     ETag: "abc123"           ← zero data transfer

  If catalog changed:
  ← 200 OK                    ← new full response
     ETag: "def456"
     (new body)
```

---

### 🧪 Thought Experiment

**SCENARIO:** Cache strategy for a product catalog API.

```
PRODUCT CATALOG FACTS:
  - 50,000 SKUs
  - Updated by merchandising team max 5 times per day
  - Read by 100,000 users daily
  - Database query: 80ms
  - Serialization: 20ms

STRATEGY ANALYSIS:

  Cache-Control: no-cache (no caching):
  → 100,000 × (80ms + 20ms) = 100,000 DB queries/day
  → Database load: maximum
  → User latency: 100ms+ per request

  Cache-Control: max-age=300 (5 minutes cache):
  → Cache hit ratio: very high during 5 min window
  → Worst staleness: 5 minutes (2 human hours worth of updates, missed)
  → For product catalog: 5-min staleness acceptable

  Cache-Control: max-age=3600, s-maxage=86400 + cache invalidation on update:
  → CDN caches for 24 hours
  → Browser caches for 1 hour
  → On catalog update: call CDN purge API (Cloudflare: PUT /zones/{id}/purge_cache)
  → Zero staleness (CDN purged on change), zero extra database load
  → Best of both: freshness + performance

  ETag-based (catalog hash as ETag):
  → Compute MD5 of full catalog list as ETag
  → Client revalidates: 304 if ETag matches (zero bandwidth)
  → Origin still queried for revalidation (reduced bandwidth, not DB load)
```

---

### 🧠 Mental Model / Analogy

> API caching is like a newspaper delivery cycle.
> The printing press (database/server) runs once per issue (data change).
> Newsstands (CDN edge nodes) stock copies and sell them all day without
> going back to the press (origin) for each customer.
> Your subscription copy (browser cache) is available instantly at home.
> When tomorrow's edition is ready, the newsstand replaces yesterday's stock.
> No paper is printed twice for the same edition.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
API caching means saving the answer to a question so you don't have to calculate it
again every time someone asks. Like memorizing that "Paris is the capital of France"
rather than looking it up in an encyclopedia every single time.

**Level 2 — How to use it (junior developer):**
In Spring Boot: add `@Cacheable("users")` to a service method — uses Caffeine in-memory
cache. For HTTP: set `Cache-Control: max-age=300` on GET responses. For user-specific
responses: add `Cache-Control: private` to prevent CDN from sharing personalized data.
Never cache responses with sensitive data — use `no-store` for auth endpoints.

**Level 3 — How it works (mid-level engineer):**
Spring's `@Cacheable` creates a cache entry keyed by method parameters; returns from
cache on subsequent calls with same key; `@CacheEvict` removes entries on mutation.
For distributed systems: Redis as cache store (spring-data-redis + `@EnableCaching +
RedisCacheManager`). Cache aside pattern: application checks cache before DB query;
on miss, loads from DB + populates cache. HTTP layers: `Cache-Control` + `Vary`
headers control CDN behavior; `ETag`/`Last-Modified` enable conditional requests
reducing bandwidth. Key decision: cache TTL (freshness vs. staleness balance) and
cache invalidation strategy (time-based expiry vs. event-driven purge).

**Level 4 — Why it was designed this way (senior/staff):**
Cache invalidation is widely known as one of the two hard problems in computer science
("There are only two hard things in Computer Science: cache invalidation and naming things"
— Phil Karlton). HTTP cache design addresses this by separating concerns:
(1) cache storage and freshness (Cache-Control + max-age) — simple, stateless, requires
no server coordination; (2) revalidation (ETag, If-None-Match) — bandwidth optimization
at the cost of a round trip; (3) explicit invalidation (CDN purge, cache-busted URLs) —
immediate correctness at the cost of infrastructure management. The right strategy depends
on staleness tolerance: financial data (seconds), product catalog (minutes to hours),
static assets (weeks with cache-busting on deploy). The `stale-while-revalidate` directive
(RFC 5861) represents the pragmatic middle ground: serve slightly stale data immediately
while refreshing in the background — great for non-critical data where freshness matters
but latency matters more.

---

### ⚙️ How It Works (Mechanism)

```
SPRING BOOT — MULTI-LAYER CACHING:

  @Service
  public class CatalogService {

      @Cacheable(value = "catalog", key = "#categoryId",
                 unless = "#result == null")  ← don't cache nulls
      public List<Product> getProducts(String categoryId) {
          return productRepository.findByCategoryId(categoryId);  // DB query on miss only
      }

      @CacheEvict(value = "catalog", key = "#categoryId")
      public void updateCategory(String categoryId, List<Product> products) {
          productRepository.saveAll(products);  // (evicts cache after DB update)
      }
  }

  SPRING CACHE FLOW:
  1. getProducts("electronics") called
  2. Spring AOP interceptor: check cache "catalog" key "electronics"
  3. Cache hit? → return cached List<Product>    (no DB call)
  4. Cache miss? → invoke real method → DB query → cache result → return

REDIS CACHE CONFIGURATION:
  @Bean
  public RedisCacheManager cacheManager(RedisConnectionFactory factory) {
      RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
          .entryTtl(Duration.ofMinutes(10))          // 10-min TTL
          .serializeValuesWith(                      // JSON serialization
              RedisSerializationContext.SerializationPair.fromSerializer(
                  new GenericJackson2JsonRedisSerializer()));
      return RedisCacheManager.builder(factory)
          .cacheDefaults(config)
          .build();
  }
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
HTTP CACHING FULL LIFECYCLE:

  1. First request:
     Client: GET /api/products/electronics
     CDN: miss → forward to origin
     Origin: DB query 80ms + serialize 20ms = 100ms
     Response: 200 OK
               Cache-Control: public, max-age=300, s-maxage=3600
               ETag: "a1b2c3"
               Vary: Accept-Language
     CDN: caches for 3600s
     Client: caches for 300s

  2. Second request (within 300s):
     Client: served from browser cache (0ms, no network)

  3. Request after 300s (browser cache stale):
     Client: GET /api/products/electronics
             If-None-Match: "a1b2c3"
     CDN: hit (still within 3600s) → 200 OK with cached body
          (CDN doesn't forward to origin)

  4. Request after 3600s (CDN cache stale):
     CDN: GET /api/products/electronics + If-None-Match: "a1b2c3" → origin
     Origin: catalog unchanged → 304 Not Modified (no body transfer)
     CDN: re-caches same body with fresh TTL

  5. After product update:
     POST /api/admin/products/electronics/update → origin
     Origin: invalidates cache (Redis @CacheEvict, CDN purge API call)
     Next request: cache miss → fresh DB query
```

---

### 💻 Code Example

```java
// HTTP caching headers in Spring MVC controller
@RestController
@RequestMapping("/api/v1")
public class CatalogController {

    @Autowired
    private CatalogService catalogService;

    @GetMapping("/products/{categoryId}")
    public ResponseEntity<List<ProductDto>> getProducts(
            @PathVariable String categoryId,
            WebRequest webRequest) {

        List<ProductDto> products = catalogService.getProducts(categoryId);

        // Compute ETag from content
        String etag = computeEtag(products);

        // Conditional request: if client has same ETag, return 304
        if (webRequest.checkNotModified(etag)) {
            return null;  // Spring MVC returns 304 automatically
        }

        return ResponseEntity.ok()
            .eTag(etag)
            .cacheControl(CacheControl.maxAge(5, TimeUnit.MINUTES)
                .cachePublic()
                .sMaxAge(1, TimeUnit.HOURS))
            .body(products);
    }

    private String computeEtag(List<ProductDto> products) {
        // Stable hash of content as ETag
        return Integer.toHexString(
            products.stream()
                .mapToInt(p -> Objects.hash(p.getId(), p.getPrice(), p.getUpdatedAt()))
                .sum()
        );
    }

    // Cache invalidation on update
    @PostMapping("/admin/products/{categoryId}/refresh")
    @CacheEvict(value = "products", key = "#categoryId")
    public ResponseEntity<Void> refreshCategory(@PathVariable String categoryId) {
        return ResponseEntity.noContent().build();
    }
}
```

---

### ⚖️ Comparison Table

| Caching Layer           | Location            | Who Controls               | Latency Saved     | When to Use                       |
| ----------------------- | ------------------- | -------------------------- | ----------------- | --------------------------------- |
| **Browser cache**       | Client machine      | `Cache-Control` headers    | ~100ms round trip | Static + semi-static resources    |
| **CDN cache**           | Edge node (global)  | `Cache-Control`, CDN rules | ~50-150ms RTT     | Public read-heavy APIs            |
| **Reverse proxy cache** | Your datacenter     | Nginx/Varnish config       | ~10-50ms          | Internal traffic                  |
| **Application cache**   | JVM heap (Caffeine) | `@Cacheable`               | ~5-20ms (DB skip) | Computed/aggregated data          |
| **Distributed cache**   | Redis cluster       | `@Cacheable` + Redis       | ~1-5ms            | Multi-instance APIs, shared state |

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                              |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Cache-Control: no-cache` means don't cache | It means "cache it but revalidate before use." Use `no-store` to truly prevent caching                                                               |
| POST responses can't be cached              | HTTP spec does not prohibit it, but POST responses are generally not cached by browsers/CDNs unless explicitly configured                            |
| High cache hit rate = always good           | Stale-while-revalidate can serve outdated critical data. Always evaluate caching against staleness tolerance for the specific data type              |
| ETag prevents all extra work                | ETag revalidation still hits the origin server (round trip), you just skip the response body transfer. Server still needs to compute if ETag changed |

---

### 🚨 Failure Modes & Diagnosis

**Stale Data Served After Update**

Symptom:
Price updated in admin UI. Customers still see old price for 5 minutes. CDN is serving
stale cached response.

Diagnostic:

```bash
# Check CDN cache status header:
curl -I "https://api.store.com/products/ABC123"
# Look for: X-Cache: HIT (CDN serving cached) vs MISS (origin hit)
# Check: Cache-Control response header TTL

# Purge CDN cache for specific URL:
# Cloudflare:
curl -X POST "https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/purge_cache" \
  -H "Authorization: Bearer ${CF_TOKEN}" \
  -d '{"files": ["https://api.store.com/products/ABC123"]}'

# Fix in code — after price update, trigger cache invalidation:
@Transactional
public void updatePrice(String productId, BigDecimal price) {
    productRepository.updatePrice(productId, price);
    cacheManager.getCache("products").evict(productId);  // local cache
    cdnPurgeService.purge("/api/products/" + productId);  // CDN
}
```

---

### 🔗 Related Keywords

- `ETag / Cache-Control` — the specific HTTP headers mechanism for caching
- `CDN` — content delivery network: the CDN layer of API caching
- `Redis` — most common distributed cache backing for server-side API caching
- `API Rate Limiting` — caching reduces the load that rate limiting needs to handle

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Store HTTP responses at multiple layers  │
│              │ to reduce latency, load, bandwidth       │
├──────────────┼───────────────────────────────────────────┤
│ KEY HEADER   │ Cache-Control: public, max-age=300,      │
│              │ s-maxage=3600                            │
├──────────────┼───────────────────────────────────────────┤
│ PRIVATE      │ Cache-Control: private → browser only,  │
│ DATA         │ CDN must not cache                       │
├──────────────┼───────────────────────────────────────────┤
│ NEVER CACHE  │ Cache-Control: no-store                  │
│              │ (auth tokens, sensitive data)            │
├──────────────┼───────────────────────────────────────────┤
│ SPRING       │ @Cacheable + Redis or Caffeine           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Serve stored responses; skip the work" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ETag/Cache-Control → CDN → Redis        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** A user's shopping cart page loads data from three APIs: product details (changes rarely),
inventory levels (changes every minute), and personalized recommendations (unique per user,
recalculated hourly). Design a cache strategy for each component, justify a different TTL
and cache scope (public/private) for each, and explain how you handle the case where a
product goes out of stock but is still showing as "Available" due to inventory caching.
