---
layout: default
title: "Fallback"
parent: "Distributed Systems"
nav_order: 607
permalink: /distributed-systems/fallback/
number: "607"
category: Distributed Systems
difficulty: ★★☆
depends_on: "Circuit Breaker, Timeout"
used_by: "Resilience4j, Hystrix, Spring Cloud Gateway, CDN Edge"
tags: #intermediate, #distributed, #resilience, #graceful-degradation, #availability
---

# 607 — Fallback

`#intermediate` `#distributed` `#resilience` `#graceful-degradation` `#availability`

⚡ TL;DR — **Fallback** is an alternative response returned when a primary operation fails — from cached data to default values to a simplified computation — keeping the system available and partially functional when dependencies fail.

| #607 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Circuit Breaker, Timeout | |
| **Used by:** | Resilience4j, Hystrix, Spring Cloud Gateway, CDN Edge | |

---

### 📘 Textbook Definition

**Fallback** is a resilience pattern that defines alternative behaviour when a primary operation fails, times out, or when a circuit breaker is open. Fallback strategies range from returning stale cached data (most seamless), to returning a degraded/simplified response, to returning a static default, to returning an explicit error (least seamless). The goal is **graceful degradation**: the system remains partially functional and available rather than completely failing. Fallback is not a substitute for fixing the underlying failure — it's a temporary safeguard that reduces user impact while recovery occurs. **Fallback types**: (1) Cache: return last known value; (2) Default: return a pre-defined safe default (empty list, 0, "N/A"); (3) Stub/static: return a hardcoded response for development or feature flagging; (4) Fail silent: for non-critical operations, simply omit the feature (no error); (5) Fail loudly: return a clear error message with context (last resort). **Design consideration**: fallback must be carefully designed to avoid giving users stale, incorrect, or misleading data — a wrong fallback can be worse than an honest error. Fallback is paired with circuit breaker (CB triggers fallback on open) and timeout (timeout triggers fallback on slow response).

---

### 🟢 Simple Definition (Easy)

Fallback: "Plan B if Plan A fails." Netflix example: recommendation service is down → instead of showing an error page → show "Top 20 Popular Movies" (cached/static list). User: sees content, doesn't notice the recommendation engine was down. Better user experience than blank page. The fallback is "good enough" — not perfect, but keeps the user engaged. The critical decision: what's good enough vs. what would be misleading?

---

### 🔵 Simple Definition (Elaborated)

Fallback chain (multiple levels): try primary → if fails, try cache → if cache stale/empty, try default → if default inappropriate, return graceful error. Example: product recommendations: Primary: personalized ML model recommendations (best). Fallback 1: user's recently viewed items (from local cache). Fallback 2: category bestsellers (static, always available). Fallback 3: hide "Recommendations" section entirely (fail silent). Never: show an error in the recommendations widget (bad UX; non-critical feature shouldn't crash the page).

---

### 🔩 First Principles Explanation

**Fallback strategies, caching patterns, and graceful degradation:**

```
FALLBACK TRIGGER SOURCES:

  1. Circuit Breaker OPEN: primary service known to be down.
     Best fallback: cached result (maybe 5 minutes stale). User gets data.
     
  2. Timeout: primary call exceeded time limit.
     Best fallback: cached result or default. Don't retry (slow response may mean overloaded).
     
  3. Exception (non-transient): primary call failed with known error.
     Best fallback: depends on error type.
       404: "item not found" → probably accurate, return 404 (not a stale result).
       500: server error → fallback appropriate.
       
  4. Rate limit (429): service is throttling you.
     Best fallback: cached result + schedule refresh for when rate limit resets.

FALLBACK STRATEGY HIERARCHY:

  Strategy 1: STALE CACHE (most seamless):
    Store last successful response in local cache (in-memory, Redis).
    On failure: return cached value.
    Risk: stale data may be incorrect (price changed, item out of stock).
    Acceptable for: read-heavy, slowly-changing data (catalog, user profile, config).
    Unacceptable for: real-time data (inventory count, pricing, account balance).
    
    CACHE-ASIDE with TTL:
      cache_key = "recommendations:user:" + userId
      cached = redisCache.get(cache_key)
      if cached not null and not expired: return cached  // HAPPY PATH
      
      try:
          result = recommendationService.get(userId)   // PRIMARY
          redisCache.set(cache_key, result, ttl=300s)  // Refresh cache
          return result
      except ServiceException:
          if cached not null:  // stale cache (expired but still present)
              log.warn("Recommendation service down. Returning stale data for user {}", userId)
              return cached    // FALLBACK 1: stale cache
          return defaultRecommendations()              // FALLBACK 2: default list
          
    EXTENDED TTL TRICK:
      Store two copies: one with normal TTL (for "is it fresh?"), one with longer TTL (for fallback).
      Fresh TTL: 5 minutes. Fallback TTL: 2 hours.
      On failure: check 2-hour cache → return stale but not ancient data.
      
  Strategy 2: DEFAULT VALUE:
    Return a safe, hardcoded value.
    Product price: service down → return null/0? NO. Return last known price? YES.
    Feature flag: service down → default to "feature disabled" (safe conservative default).
    User preferences: service down → return default settings (light mode, English).
    
    DESIGN: choose defaults that are conservative and safe, not optimistic.
      Circuit breaker: default to CLOSED? No. Default to OPEN (block traffic to protect downstream).
      Rate limit: default to 0 allowed? Yes (conservative). Or cached last rate? Yes.
      Permissions: default to deny (safest). Never default to allow.
      
  Strategy 3: SIMPLIFIED COMPUTATION:
    Primary: full personalized ML recommendation.
    Fallback: simpler rule-based recommendation (trending this week + user's top category).
    Result: less personalized, but still contextually relevant.
    Cost: fallback runs locally, no external service dependency.
    
  Strategy 4: FAIL SILENT (omit feature):
    Non-critical UI feature: hide it when service is down.
    "Related products" widget: recommended service down → don't show widget.
    "You saved X%" banner: pricing service down → hide banner.
    Analytics event: analytics service down → drop event (non-critical).
    
    RISK: silent failures can mask bugs if the feature is ASSUMED to be present.
    Use: only for truly non-critical features. Add monitoring/alerting for "feature silently dropped."
    
  Strategy 5: EXPLICIT GRACEFUL ERROR:
    Return a clear, user-friendly error message.
    "We're having trouble loading your recommendations right now. Try refreshing."
    Better than: blank section, cryptic error, infinite spinner.
    Best for: critical features where stale data would be misleading.
    Payment: can't process → "Payment service temporarily unavailable. Please try again."
    Don't return: technical stack traces, "null pointer exception," "500 Internal Server Error."
    
FALLBACK ANTI-PATTERNS:

  1. FALLBACK THAT CALLS ANOTHER SLOW SERVICE:
     Primary fails. Fallback: call backup service.
     Backup service: also slow → fallback also blocks → thread exhaustion.
     FIX: fallback should be local computation or cache (no external call) OR
          fallback external call must also have its own timeout + CB.
          
  2. CACHED STALE DATA FOR FINANCIAL OPERATIONS:
     Payment: primary down → return cached "last successful payment" result.
     This is WRONG: stale payment result doesn't mean current charge succeeded.
     FIX: payments must fail explicitly, not return stale data.
     Use fallback for reads, not for writes with side effects.
     
  3. FALLBACK WITHOUT ALERTING:
     Fallback silently returns cached data for hours.
     Engineers: don't know primary is down (no alert, no metric).
     Cache expires. Service still down. Users now see errors.
     FIX: increment "fallback_used" counter. Alert if fallback used for > 5 minutes.
     
  4. FALLBACK THAT MASKS A BROADER OUTAGE:
     Fallback: returns cached data.
     50% of users: getting stale recommendations. Nobody notices.
     Actual problem: database replication failure. Data diverging.
     FIX: monitor fallback usage rate. High rate = signal to investigate, not ignore.

RESILIENCE4J FALLBACK MECHANICS:

  Fallback method signature: same return type, same params + Throwable parameter.
  Fallback called on: ANY exception from the primary (including CB's CallNotPermittedException).
  
  Multiple exceptions: different fallback logic per exception type:
  
  @CircuitBreaker(name="rec-service", fallbackMethod="recFallback")
  public List<Product> getRecommendations(String userId) {
      return recServiceClient.get(userId);
  }
  
  // Resilience4j picks most specific matching fallback method:
  
  // Handles: CallNotPermittedException (CB open):
  private List<Product> recFallback(String userId, CallNotPermittedException e) {
      return getCachedOrDefault(userId); // CB is open → use cache/default
  }
  
  // Handles: any other exception (timeout, network error):
  private List<Product> recFallback(String userId, Exception e) {
      log.warn("Rec service error for {}: {}", userId, e.getMessage());
      return getCachedOrDefault(userId);
  }
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT fallback:
- Dependency failure → direct user-visible error for every request touching that dependency
- Non-critical features (recommendations, ads, suggestions) can crash the entire page
- No graceful degradation: all-or-nothing availability

WITH fallback:
→ Partial functionality: core features work even when non-critical dependencies fail
→ Better UX: user sees degraded but usable content instead of error pages
→ Blast radius containment: one service down doesn't equal one feature section fails, not whole app

---

### 🧠 Mental Model / Analogy

> A GPS navigation app. Primary: live real-time traffic data. GPS service down: app falls back to cached offline maps (downloaded last week). User: still gets directions — maybe not the most current road closures, but gets to the destination. Alternative: return "Navigation unavailable — can't reach server" (fail loudly). The cached map fallback is better for the user (can still navigate) while being clearly suboptimal (may not have latest road changes).

"Live traffic data" = primary service call
"Downloaded offline maps" = cached fallback data
"Navigation unavailable" = fail loudly fallback (last resort)
"Maybe not latest road closures" = trade-off: stale data vs. no data

---

### ⚙️ How It Works (Mechanism)

```
Resilience4j Fallback invocation:

  Decorated method executes.
  Exception thrown OR CB's CallNotPermittedException:
    → Resilience4j catches exception.
    → Finds matching fallback method via reflection (same return type, same params + Throwable).
    → Invokes fallback method with original params + the exception.
    → Returns fallback's result to caller.
    
  Fallback itself can throw:
    → Original exception re-thrown (not the fallback's exception) to caller.
    → Or wrapped exception, depending on configuration.
```

---

### 🔄 How It Connects (Mini-Map)

```
Circuit Breaker (OPEN → stop calls; need alternative response)
        │
        ▼
Fallback ◄──── (you are here)
(alternative response when primary fails; graceful degradation)
        │
        ├── Timeout: timeout exception → triggers fallback
        ├── Graceful Degradation: broader pattern that fallback implements
        └── Cache: most useful fallback source (stale-while-revalidate pattern)
```

---

### 💻 Code Example

**Fallback with Resilience4j + Redis cache:**

```java
@Service
public class RecommendationService {
    
    private final RecommendationClient client;
    private final RedisTemplate<String, List<Product>> cache;
    private final MeterRegistry metrics;
    
    @CircuitBreaker(name = "rec-service", fallbackMethod = "cachedFallback")
    @TimeLimiter(name = "rec-service", fallbackMethod = "cachedFallback")
    public CompletableFuture<List<Product>> getRecommendations(String userId) {
        return CompletableFuture.supplyAsync(() -> client.getRecommendations(userId))
            .thenApply(recs -> {
                // Cache successful result (with 10min TTL):
                cache.opsForValue().set("recs:" + userId, recs, Duration.ofMinutes(10));
                // Also store with extended TTL for fallback use (2h):
                cache.opsForValue().set("recs:fallback:" + userId, recs, Duration.ofHours(2));
                return recs;
            });
    }
    
    // Fallback: called when CB open, timeout, or any exception.
    public CompletableFuture<List<Product>> cachedFallback(String userId, Throwable e) {
        metrics.counter("recommendations.fallback.used",
            "reason", e.getClass().getSimpleName()).increment();
        
        // Try 2-hour stale cache first:
        List<Product> stale = cache.opsForValue().get("recs:fallback:" + userId);
        if (stale != null && !stale.isEmpty()) {
            log.warn("Rec service unavailable. Using stale cache for user {}", userId);
            return CompletableFuture.completedFuture(stale);
        }
        
        // No cache: return generic trending items (always available, locally computed):
        log.warn("Rec service unavailable and no cache for user {}. Using trending.", userId);
        return CompletableFuture.completedFuture(getTrendingItems());
    }
    
    private List<Product> getTrendingItems() {
        // Local computation: no external service dependency.
        // Pre-computed and stored locally every hour by a background job.
        return trendingCache.getTopN(20);
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Fallback means the system is working normally | Fallback means the primary is FAILING and you are providing a degraded alternative. Fallback usage should trigger monitoring and alerting. Engineers must know when fallbacks are active (continuous fallback = undetected outage). Treat high fallback rate as an incident requiring investigation, not as "working as designed" |
| A fallback should always return data (never an error) | Some operations should NOT have data fallbacks — they should fail explicitly. Payment processing: returning stale data is dangerous (suggests payment succeeded when it didn't). Account balance: returning cached balance could enable fraud (balance appears higher than actual). Rule: use data fallback for read-only, slowly-changing data. For writes or real-time financial data: fallback should be an explicit error with a user-friendly message |
| Fallback is only needed for microservices | Fallback applies to any dependency: third-party APIs (payment providers, email services, geolocation), internal services, databases (read from replica when primary is down), CDN (serve stale cached version when origin is down). Single-service monoliths also benefit from fallback when calling external APIs |
| The fallback method can be as complex as the primary | Fallback should be simpler and more reliable than the primary. If fallback calls another external service: fallback itself can fail, causing double failure. Prefer fallback to be: (1) local cache lookup, (2) local computation, (3) hardcoded default. If fallback MUST call an external service: wrap fallback call with its own separate circuit breaker and timeout |

---

### 🔥 Pitfalls in Production

**Fallback silently serving stale data during extended outage:**

```
SCENARIO: E-commerce site. Product pricing service down for 6 hours.
  Fallback: return cached price (10-minute TTL for fresh, 2-hour for stale).
  After 2 hours: stale cache expires. No more cached prices.
  Fallback tier 2: return price=0 (development default left in production).
  Users: can checkout items for FREE (price=0). Revenue loss.
  
BAD: Fallback chain with unsafe default:
  public Price getFallback(String productId, Exception e) {
      Price cached = cache.get("price:" + productId);
      if (cached != null) return cached;
      return new Price(0, "USD");  // WRONG: price=0 is not a safe default!
  }
  
FIX 1: Never use a numeric 0 as a price fallback:
  public Price getFallback(String productId, Exception e) {
      Price cached = cache.get("price:" + productId);
      if (cached != null) return cached;
      // No cache: pricing unknown. Disable checkout for this product.
      // Return a marker that UI understands as "price unavailable":
      return Price.UNAVAILABLE; // UI: shows "Temporarily unavailable" and disables "Add to Cart."
  }
  
FIX 2: Alert when fallback active > threshold:
  @Scheduled(fixedRate = 60000)
  public void checkFallbackRate() {
      double rate = metrics.counter("pricing.fallback.used").count() /
                    metrics.counter("pricing.requests.total").count();
      if (rate > 0.05) { // > 5% of requests using fallback
          alertManager.fire("pricing-fallback-rate-high",
              "Pricing service fallback active for " + formatDuration(fallbackSince) +
              ". " + (rate * 100) + "% of requests degraded.");
      }
  }
  
FIX 3: Fallback timeouts — don't let stale data last too long:
  // If pricing service down > 15 minutes AND no valid cache exists:
  // Return "price temporarily unavailable" to user.
  // Better to show "unavailable" than to show potentially wrong price.
  if (fallbackActiveSince.elapsed() > Duration.ofMinutes(15) && cached == null) {
      return Price.UNAVAILABLE; // Honest about uncertainty.
  }
```

---

### 🔗 Related Keywords

- `Circuit Breaker` — CB OPEN state triggers fallback invocation
- `Timeout` — timeout exception triggers fallback (slow dependency same as failed dependency)
- `Graceful Degradation` — broader design principle of which fallback is the implementation
- `Cache` — most useful source of fallback data (stale-while-revalidate)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Plan B when Plan A fails: cache > default│
│              │ > simplified > fail silent > fail loudly.│
│              │ Keep system partially available.         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Non-critical features can degrade; read  │
│              │ data can be slightly stale; user         │
│              │ experience better with partial data      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Real-time financial data (don't return   │
│              │ stale balance/price); write operations   │
│              │ with side effects must fail explicitly   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "GPS offline maps: still gets you there  │
│              │  without today's traffic jams."          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Circuit Breaker → Graceful Degradation → │
│              │ Cache → Resilience4j → CDN Edge Caching  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You design a fallback for a product recommendation service: return the user's most recently viewed items (stored in a separate user-activity service). The recommendation service goes down. Your fallback calls the user-activity service. The user-activity service is also slow (sharing the same underlying database that's under load). What happens to your fallback? How do you design a fallback that is truly resilient (doesn't have its own dependencies that can fail)?

**Q2.** Stale-while-revalidate: return cached data immediately and refresh in the background. Compare this to: return cached data if fresh, else call primary synchronously. Which provides lower latency? Which provides more up-to-date data? Which is safer during a primary outage that lasts hours? Describe when you'd choose each approach and what "stale" tolerance is acceptable for different data types (product catalog, inventory count, user preferences, financial balance).
