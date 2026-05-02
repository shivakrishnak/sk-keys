---
layout: default
title: "Fallback"
parent: "Distributed Systems"
nav_order: 607
permalink: /distributed-systems/fallback/
number: "0607"
category: Distributed Systems
difficulty: ★★☆
depends_on: Circuit Breaker, Timeout, Graceful Degradation, Bulkhead
used_by: Graceful Degradation, Service Mesh, Resilience4j, Hystrix
related: Circuit Breaker, Graceful Degradation, Bulkhead, Retry with Backoff, Timeout
tags:
  - distributed
  - reliability
  - resilience
  - pattern
---

# 607 — Fallback

⚡ TL;DR — A fallback provides an alternative response when the primary service call fails — typically a cached value, a default, a simplified computation, or a degraded-but-functional response — so that the user gets something useful instead of an error.

| #607            | Category: Distributed Systems                                                | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Circuit Breaker, Timeout, Graceful Degradation, Bulkhead                     |                 |
| **Used by:**    | Graceful Degradation, Service Mesh, Resilience4j, Hystrix                    |                 |
| **Related:**    | Circuit Breaker, Graceful Degradation, Bulkhead, Retry with Backoff, Timeout |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Netflix Recommendation service goes down at 9 PM on a Friday. Every request to the homepage includes a call to recommendations. Recommendations fail → homepage fails → 200 million subscribers get a blank page. Netflix engineers get paged. Engineers scramble to restore the service. 30 minutes of complete outage.

**WITH FALLBACK:**
Recommendations fail. The fallback runs: return the user's "My List" from a local cache. If that's empty, return the global "Top 10 in Your Country" list (pre-computed, stored in Redis). Homepage renders — slower, less personalized, but functional. No user sees an error. Engineers still get alerted but it's P2 (degraded), not P0 (outage).

**THE INVENTION MOMENT:**
Hystrix (Netflix OSS, 2012) popularized fallback as a first-class citizen alongside circuit breakers. Fallback is the answer to: "If the circuit is open, what should we return?" Without a fallback, an open circuit = user-visible error. With a fallback, an open circuit = degraded-but-functional experience.

---

### 📘 Textbook Definition

A **fallback** is an alternative code path executed when the primary operation fails (exception, timeout, circuit open, bulkhead rejection). Fallback types by value quality:

1. **Static default**: hardcoded value (e.g., empty list, default icon). Always available, zero cost, zero freshness.
2. **Cached value**: last successful response, stored in local/Redis cache. TTL determines staleness; acceptable for non-critical updates (product prices, recommendations).
3. **Degraded computation**: simpler logic that works without the failing dependency (e.g., rule-based recommendations instead of ML model).
4. **Stubbed response**: indicates the feature is unavailable without being an error (e.g., "Recommendations unavailable — try My List").
5. **Queue-for-later**: record the operation; complete it asynchronously when dependency recovers (e.g., analytics events — drop if analytics service is down, or buffer locally).

**Fallback quality hierarchy**: live data > cached data > degraded computation > stub response > error (last resort only).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
When a call fails, run plan B — cached data, a simpler result, or a safe default — instead of propagating the failure to the user.

**One analogy:**

> Fallback is like a backup generator. When the power grid fails (primary service down), the generator kicks in automatically. The office runs at reduced capacity (some non-essential systems off), but core functions continue. Employees (users) experience a slight degradation but don't evacuate the building.

**One insight:**
The fallback must be designed before the primary service is written, not after a production incident. A fallback that queries another database or makes another network call can itself fail — and now you have a fallback that cascades. The safest fallbacks are **entirely local and dependency-free**: cached values already in memory, or static defaults hardcoded in the binary.

---

### 🔩 First Principles Explanation

**RESILIENCE4J FALLBACK:**

```java
@Service
public class ProductService {

    @Autowired
    private RecommendationClient client;

    @Autowired
    private RedisTemplate<String, List<Product>> redis;

    public List<Product> getRecommendations(String userId) {
        return CircuitBreaker.decorateSupplier(
            circuitBreaker("recommendation"),
            () -> client.fetchRecommendations(userId)  // primary call
        ).apply()
        .recover(exception -> fallbackRecommendations(userId, exception))  // fallback
        .get();
    }

    private List<Product> fallbackRecommendations(String userId, Throwable ex) {
        log.warn("Recommendation service unavailable, using fallback. User={}, Error={}",
            userId, ex.getMessage());

        // Tier 1: try per-user cached recommendations:
        List<Product> cached = redis.opsForValue().get("recs:" + userId);
        if (cached != null && !cached.isEmpty()) {
            return cached;
        }

        // Tier 2: global trending (always available, pre-computed):
        List<Product> trending = redis.opsForValue().get("trending:global");
        if (trending != null) {
            return trending;
        }

        // Tier 3: static default (always available, never fails):
        return List.of(
            new Product("popular-1", "Bestseller", ProductStatus.DEFAULT),
            new Product("popular-2", "New Arrival", ProductStatus.DEFAULT)
        );
    }
}
```

**FALLBACK THAT ITSELF FAILS (ANTI-PATTERN):**

```java
// BAD - fallback makes another network call:
private List<Product> badFallback(String userId) {
    // If recommendation service is down, try the catalog service:
    return catalogService.getTopProducts();  // ← also a network call that can fail!
    // If catalog is also down: NullPointerException or second failure
    // The fallback can fail, and now you have a cascade in the fallback
}

// GOOD - fallback uses local data only:
private List<Product> goodFallback(String userId) {
    // Pre-warmed in-memory cache: never makes a network call
    return LOCAL_CACHE.getOrDefault(userId, STATIC_DEFAULTS);
}
```

**BULKHEAD REJECTION FALLBACK:**

```java
// Circuit breaker isn't the only trigger for fallback.
// Bulkhead rejection also needs fallback:

Bulkhead.decorateSupplier(bulkhead, () -> expensiveService.call())
    .apply()
    .recover(BulkheadFullException.class, ex -> {
        metrics.increment("bulkhead.rejection.fallback");
        return CachedResponse.getRecent(); // fallback when bulkhead full
    });
```

---

### 🧪 Thought Experiment

**THE CASCADING FALLBACK PROBLEM:**

Service A's fallback calls Service B. Service B is down. Service A's fallback fails.
Service A now has NO fallback for its fallback.

Solution: **fallback chain** with terminal static fallback:

```
Primary → fails → Tier 1 fallback (cache lookup) → fails (cache cold)
                → Tier 2 fallback (simpler computation) → fails (service also down)
                → Tier 3 fallback (static default) → ✓ always succeeds

The terminal fallback (Tier 3) must NEVER fail. It must:
  - Use only local data (no network, no DB)
  - Return a valid (possibly empty/minimal) response
  - Be tested as a standalone unit
```

**WHEN TO NOT FALLBACK (STRICT DATA CONSISTENCY):**

Financial balance inquiry: user requests account balance.
Primary service (authoritative balance DB) is down.

Fallback options:

1. Return cached balance from 1 hour ago → NOT acceptable (stale balance could cause overdraft decisions)
2. Return "balance unavailable, try again" → correct behavior (inform user of degradation)
3. Return $0 (static default) → NEVER (user might not make a payment they can afford)

**Lesson:** Fallback is appropriate when **staleness is acceptable** (recommendations, product catalog, user preferences). Fallback is inappropriate when **exact current value is required** (balances, inventory counts, flight seats). For the latter, return a clear "service unavailable" message rather than a potentially incorrect value.

---

### 🧠 Mental Model / Analogy

> Fallback is like a restaurant's "86" system. When a dish is unavailable (primary service down), the waiter doesn't crash the meal — they offer: "We're out of the salmon. Can I offer the trout instead?" (cached alternative). If the kitchen has limited capacity tonight (bulkhead): "We can offer a set menu" (degraded computation). If nothing is available from the section: "Here's bread and soup to start" (static default). The dinner continues — degraded, but not failed.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Fallback = plan B when primary fails. Types: cached data, static default, simplified response. Always return something useful to the user instead of an error.

**Level 2:** Triggered by: exception, timeout, circuit open, bulkhead rejection. Fallback quality hierarchy: live > cache > degraded computation > stub. Terminal fallback must always succeed (local, dependency-free). Don't put network calls in fallbacks.

**Level 3:** Fallback chain (tiered): try per-user cache → try global cache → try simplified computation → use static default. Monitor fallback invocation rate separately from primary failure rate (high fallback rate = hidden dependency issues). Fallback should emit a metric/log to enable alerting even when user experience is maintained.

**Level 4:** Fallback and data consistency tension: for write paths, fallback is dangerous (write fallbacks risk data loss or duplication). For read paths, fallback is usually safe if staleness is acceptable. Queue-for-later pattern: for non-critical writes (analytics, audit events), enqueue locally and replay when dependency recovers. With exactly-once semantics, this requires a local WAL (write-ahead log) with idempotent replay. Service meshes (Istio) can implement response fallbacks at the proxy level via `VirtualService.fault.abort` (for testing) and response caching — but complex fallback logic still requires application-level implementation.

---

### ⚙️ How It Works (Mechanism)

**Spring Cloud Feign + Hystrix Fallback:**

```java
@FeignClient(name = "recommendation-service", fallback = RecommendationFallback.class)
public interface RecommendationClient {
    @GetMapping("/recommendations/{userId}")
    List<Product> getRecommendations(@PathVariable String userId);
}

@Component
public class RecommendationFallback implements RecommendationClient {

    @Autowired
    private ProductCache cache;

    @Override
    public List<Product> getRecommendations(String userId) {
        // Fallback implementation — must be dependency-light:
        return cache.getGlobalTrending()           // Redis pre-computed
            .orElse(STATIC_DEFAULT_PRODUCTS);       // Never fails
    }
}
```

---

### ⚖️ Comparison Table

| Fallback Type        | Data Freshness         | Complexity | Failure Risk      | Best For                      |
| -------------------- | ---------------------- | ---------- | ----------------- | ----------------------------- |
| Static default       | Stale (hardcoded)      | None       | Zero              | Non-critical UI elements      |
| Cached value         | Recent (TTL-dependent) | Low        | If cache is cold  | Recommendations, catalog      |
| Degraded computation | Current but simplified | Medium     | Low               | ML → rule-based               |
| Queue-for-later      | N/A (async)            | High       | Risk of data loss | Analytics, audit              |
| Error message        | N/A                    | None       | Zero              | Financial data, sensitive ops |

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                 |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Fallback hides failures from operators              | Correct fallback STILL emits metrics/alerts. Fallback = user doesn't see error; operators DO get alerted                |
| Any fallback is better than an error                | A fallback with wrong data (stale account balance) is worse than a clear error. Match fallback type to data sensitivity |
| Fallback is only needed when using circuit breakers | Fallback should handle ANY failure: exception, timeout, thread rejection, circuit open — all need graceful handling     |

---

### 🚨 Failure Modes & Diagnosis

**Silent Fallback — Failures Hidden from Operators**

Symptom: Users experience degraded (not broken) homepage. Recommendations are stale.
Operators are unaware — no alerts firing. The issue persists for hours undetected.

Cause: Fallback is working correctly (serving cached data) but no metrics are emitted
for fallback invocations. Operators have no visibility into how often fallback runs.

Fix: Every fallback MUST increment a metric:
`metrics.counter("fallback.invocations", "service", "recommendation").increment()`
Create alert: if `fallback.invocations > 0` for more than 5 minutes → alert (P2/warning).
Only when `fallback.invocations > 10%` of requests → escalate to P1.

---

### 🔗 Related Keywords

- `Circuit Breaker` — the trigger mechanism that invokes the fallback when circuit opens
- `Graceful Degradation` — the higher-level strategy; fallback is the implementation detail
- `Bulkhead` — can also trigger fallback when pool is exhausted
- `Retry with Backoff` — complements fallback: retry first for transient; fallback for persistent
- `Timeout` — triggers fallback when response takes too long

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  FALLBACK: plan B when primary fails                     │
│  Triggers: exception / timeout / circuit open / bulkhead │
│  Hierarchy: live > cached > degraded > stub              │
│  Terminal fallback: dependency-free, always succeeds     │
│  Never: put network calls inside fallback logic          │
│  Always: emit fallback metrics for observability         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An e-commerce product page calls a pricing service to get real-time prices. The pricing service is down. Your fallback returns the price from a Redis cache (cached 30 minutes ago). The actual price has changed from $49.99 to $39.99 (sale started 20 minutes ago). A user sees $49.99, adds to cart, and proceeds to checkout. During checkout, the pricing service has recovered and shows $39.99. What is the user experience impact? What is the business impact? How would you design the checkout flow to handle this price discrepancy gracefully?

**Q2.** Design a multi-tier fallback strategy for a flight search service. The primary service returns real-time availability and pricing from all airlines. Design 3 fallback tiers that progressively degrade but still provide useful results, ensuring the terminal fallback never fails. For each tier, specify: what data it returns, where that data comes from, TTL assumptions, and what the user experience impact is.
