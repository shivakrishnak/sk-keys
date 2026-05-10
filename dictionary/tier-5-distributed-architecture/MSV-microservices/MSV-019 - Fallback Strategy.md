---
layout: default
title: "Fallback Strategy"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 19
permalink: /microservices/fallback-strategy/
id: MSV-017
category: Microservices
difficulty: ★★☆
depends_on: Retry Strategy, Timeout Strategy, Circuit Breaker (Microservices)
used_by: Resilience4j, Graceful Degradation, Bulkhead Pattern
related: Rate Limiting (Microservices), Saga Pattern (Microservices), Feature Flags (Microservices)
tags:
  - microservices
  - reliability
  - pattern
  - intermediate
  - architecture
status: complete
version: 2
---

# MSV-035 - Fallback Strategy

⚡ TL;DR - A fallback strategy defines what a service returns when a dependency fails, allowing partial functionality instead of a total error.

| #652            | Category: Microservices                                                                    | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Retry Strategy, Timeout Strategy, Circuit Breaker (Microservices)                          |                 |
| **Used by:**    | Resilience4j, Graceful Degradation, Bulkhead Pattern                                       |                 |
| **Related:**    | Rate Limiting (Microservices), Saga Pattern (Microservices), Feature Flags (Microservices) |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your e-commerce homepage shows personalised recommendations from a recommendation service. That service goes down. Without a fallback, every homepage request fails with a 500 error - your entire store front is broken because of one non-critical feature. Alternatively, the page renders with a blank section and a stack trace in the browser console.

**THE BREAKING POINT:**
In a microservices system, any non-critical dependency can take down the entire user experience if failures propagate upward as hard errors. A search result that can't load personalised rankings doesn't need to destroy the whole search page.

**THE INVENTION MOMENT:**
This is exactly why fallback strategy was created - to define graceful degraded behaviour so that partial failure in a dependency yields partial functionality, not zero functionality.


**EVOLUTION:**
The Fallback pattern was popularised by Netflix Hystrix (2012) as the companion to circuit breaking: when the circuit opens, what should happen instead of a 500 error? Netflix classified fallback responses as Static (hardcoded default), Cached (last-known-good response), Degraded (simpler computation without the failed dependency), and Fail-silent (return null, handled by caller). The discipline evolved from 'catch exception, throw default response' to 'design fallback for each dependency as part of system design upfront - before failures occur.'
---

### 📘 Textbook Definition

A **fallback strategy** is a resilience pattern that provides an alternative response when a primary dependency is unavailable or exceeds its acceptable response time. Fallbacks range from cached data, static defaults, empty but structurally valid responses, to degraded-mode processing. The fallback is invoked after retries are exhausted or a circuit breaker opens, ensuring the calling service always returns a useful response even under dependency failure.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
When plan A fails, return plan B instead of an error.

**One analogy:**

> When your GPS loses signal, it doesn't stop navigating - it switches to dead reckoning using your last known position and speed. A fallback is the dead reckoning of your service: not perfect, but functional until the primary recovers.

**One insight:**
The key design question for fallbacks is: "What is the least information the user needs to proceed?" That determines your fallback quality. Returning an empty list is better than an error; returning popular items is better than an empty list; returning cached personalised items is better than popular items.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. In distributed systems, any dependency can fail at any time.
2. Some features are critical (checkout must work); some are optional (recommendations).
3. Returning a degraded response is almost always better than returning an error.

**DERIVED DESIGN:**
Given these invariants, every call to an external dependency should have a defined answer to: "If this call fails after retries, what do I return?" The fallback must be:

- **Fast**: no additional network calls (defeats the purpose)
- **Valid**: structurally correct response the caller can use
- **Transparent** (optionally): the caller can detect degraded mode

**Fallback hierarchy (best to worst):**

1. **Cached response**: last known good data for this specific request
2. **Stale data**: cached response older than normal TTL
3. **Default value**: sensible neutral content (popular items, empty but valid list)
4. **Degraded feature**: feature disabled cleanly (no recommendations section shown)
5. **Error response**: structured error with clear message (last resort)

**THE TRADE-OFFS:**
**Gain:** Resilience to non-critical dependency failure; better user experience under partial outages; allows circuit breaker to stay open without propagating errors.
**Cost:** Stale or default data may mislead users; fallback code adds complexity; every dependency needs a defined fallback; testing fallback paths is often neglected.

---

### 🧪 Thought Experiment

**SETUP:**
An e-commerce product page calls three services: inventory (critical - must show stock), pricing (critical - must show price), recommendations (optional).

**WHAT HAPPENS WITHOUT FALLBACK:**
Recommendations service times out. Product page handler catches the error and returns HTTP 500. User sees a broken page - can't buy the product at all, even though inventory and pricing are fine.

**WHAT HAPPENS WITH FALLBACK:**
Recommendations service times out. Fallback returns `[]` (empty array, or pre-configured popular items). Product page renders without the recommendations section (or with generic popular items). User sees a complete, functional product page. Inventory and pricing work normally. The degradation of one feature doesn't touch the critical path.

**THE INSIGHT:**
Fallbacks require categorising your features into critical and optional _before_ an outage, not during one. The architectural decision is made at design time: define fallback for every non-critical dependency call.

---

### 🧠 Mental Model / Analogy

> A hospital has a primary MRI machine and a backup ultrasound. If the MRI breaks, patients aren't turned away - they get an ultrasound. It's less detailed, but it keeps the hospital functioning and patients safe.

- "Primary MRI" → primary service call
- "Backup ultrasound" → fallback response
- "Less detailed scan" → degraded but valid response
- "Patient turned away" → returning HTTP 500 to user
- "Decision to use backup" → circuit breaker opening, triggering fallback

Where this analogy breaks down: in software, the "backup" is often a cached snapshot of the primary's previous output - not a genuinely different data source - so freshness degrades over time.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A fallback is a backup plan. When the main service call fails, instead of showing the user an error, you show them something useful - even if it's not perfect.

**Level 2 - How to use it (junior developer):**
After every `try` block that calls an external service, define a `catch` or `recover` block that returns a safe default. Use `@HystrixCommand(fallbackMethod=...)` or Resilience4j's `recover()`. Return the same response type as the success path - callers shouldn't need to know a fallback was used. Log the fallback invocation with the failure cause for monitoring.

**Level 3 - How it works (mid-level engineer):**
Fallbacks integrate with circuit breakers: when the breaker opens, all calls immediately route to the fallback without attempting the real call. Cache-based fallbacks use a separate TTL for "stale-ok" reads - the cache entry's normal TTL might be 60s, but during failure mode it's served for up to 300s. Fallback chains: primary → cache → static default → empty response. Each step degrades gracefully. Fallback execution must be fast - a fallback that itself makes a network call can cascade.

**Level 4 - Why it was designed this way (senior/staff):**
The Netflix Hystrix paper that popularised this pattern estimated that with 30 dependencies each at 99.9% availability, a service with no fallbacks has only 97% availability (0.999^30). With fallbacks for non-critical dependencies, availability approaches 99.9%. The key insight from Hystrix was separating _isolation_ (circuit breaker stops calls) from _fallback_ (what to return when isolated) - they're different concerns. Modern teams using Resilience4j or service meshes apply the same principle but with better async support and lower overhead.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│           Fallback Strategy - Decision Tree             │
└─────────────────────────────────────────────────────────┘

Service Call
     │
     ▼
Circuit Breaker OPEN?
  ├── YES → Skip call, go directly to fallback
  └── NO  → Attempt call
               │
               ▼
         Success? ──YES──► Return response
               │
               NO (timeout / error / retries exhausted)
               │
               ▼
         ┌─────────────────────────┐
         │    Fallback Chain       │
         │  1. Check local cache   │
         │  2. Return stale data   │
         │  3. Return static default│
         │  4. Return empty valid   │
         │  5. Return error struct  │
         └─────────────────────────┘
               │
               ▼
         Record: fallback_invocations++
         Log: "Fallback activated: [reason]"
         Return fallback response
```

**Happy path:** Primary call succeeds; fallback never invoked; user gets fresh data.
**Error path:** All attempts fail → fallback chain executes → user gets degraded but valid response; circuit breaker tracks failures.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
[User] → [Product Page Service]
  → [Recommendation Service call ← YOU ARE HERE]
  → [Returns 200 personalized items]
  → [Page renders with personalized recommendations]
```

**FAILURE PATH:**

```
[Recommendation Service DOWN]
  → [Timeout after 200ms]
  → [Fallback: return cached popular items]
  → [Page renders with popular items (degraded)]
  → [Metric: recommendation_fallback_count++]
  → [Alert if sustained > 5min]
```

**WHAT CHANGES AT SCALE:**
At 10k RPS, a fallback that serves cached data is essentially free (in-memory). At 100k RPS, if the cache layer itself needs a network call (Redis), the fallback can also fail - always have an in-process last-resort fallback (static data, empty list). At 1M RPS, teams pre-compute and store fallback payloads as static files (CDN-served JSON) to ensure zero-latency fallbacks regardless of infrastructure state.

---

### 💻 Code Example

**Example 1 - Wrong: propagating dependency failure:**

```java
@GetMapping("/products/{id}")
public ProductPage getProductPage(@PathVariable String id) {
  Product product = productService.getProduct(id);
  // No fallback - this exception propagates to 500
  List<Product> recs = recommendationService
    .getRecommendations(id);
  return new ProductPage(product, recs);
}
```

**Example 2 - Right: explicit fallback:**

```java
@GetMapping("/products/{id}")
public ProductPage getProductPage(@PathVariable String id) {
  Product product = productService.getProduct(id);
  List<Product> recs = getRecommendationsWithFallback(id);
  return new ProductPage(product, recs);
}

private List<Product> getRecommendationsWithFallback(
    String productId) {
  try {
    return recommendationService
      .getRecommendations(productId);
  } catch (Exception e) {
    log.warn("Rec service failed, using fallback: {}",
             e.getMessage());
    meterRegistry.counter("fallback.recommendations")
                 .increment();
    return recommendationCache
      .getCachedOrDefault(productId, POPULAR_ITEMS);
  }
}
```

**Example 3 - Production: Resilience4j with fallback chain:**

```java
CircuitBreakerConfig cbConfig = CircuitBreakerConfig
  .ofDefaults();
CircuitBreaker cb = CircuitBreaker.of("recs", cbConfig);

Supplier<List<Product>> recSupplier = CircuitBreaker
  .decorateSupplier(cb,
    () -> recommendationService.getRecommendations(id));

return Try.ofSupplier(recSupplier)
  .recover(CallNotPermittedException.class,
    e -> getFromCache(id))          // circuit open
  .recover(TimeoutException.class,
    e -> getFromCache(id))          // timeout
  .recover(Exception.class,
    e -> POPULAR_ITEMS_FALLBACK)    // any other failure
  .get();

private List<Product> getFromCache(String id) {
  List<Product> cached = cache.get("recs:" + id);
  return cached != null ? cached : POPULAR_ITEMS_FALLBACK;
}
```

---

### ⚖️ Comparison Table

| Fallback Type                   | Freshness             | User Impact | Complexity | Best For                        |
| ------------------------------- | --------------------- | ----------- | ---------- | ------------------------------- |
| **Cached response**             | Seconds-minutes stale | Minimal     | Medium     | Reads with short TTL            |
| Stale cache (extended TTL)      | Minutes-hours stale   | Low-medium  | Low        | Non-time-sensitive data         |
| Static default                  | Permanent (hardcoded) | Noticeable  | Very Low   | Generic content (popular items) |
| Degraded feature (hide section) | N/A                   | Noticeable  | Low        | Optional UI features            |
| Error response                  | N/A                   | High        | None       | Critical-path failures only     |

**How to choose:** Start with cached response; if cache is empty, serve static default; only return error for critical paths where no degradation is acceptable.

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                 |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Fallback means returning an error with a nice message | A true fallback returns a usable response - not an error                                |
| All dependencies need fallbacks                       | Only non-critical dependencies benefit; critical ones (auth, payments) should fail hard |
| Fallback data is "good enough" for monitoring         | Fallback invocations must be tracked and alerted - they indicate dependency problems    |
| The fallback can call another service                 | Fallback must be fast and local - a slow fallback defeats its purpose                   |
| Returning empty list is always a safe fallback        | An empty list may cause UI crashes if the consumer doesn't handle empty state           |

---

### 🚨 Failure Modes & Diagnosis

**Fallback Masking a Real Outage**

**Symptom:** Fallback works so well that engineers don't notice the primary service has been down for hours; cache serves stale data indefinitely.

**Root Cause:** No alert on fallback invocation rate; stale cache TTL too generous.

**Diagnostic Command:**

```bash
# Check fallback invocation rate
curl -s http://localhost:8080/actuator/metrics/\
  fallback.invocations | jq '.measurements[0].value'
```

**Fix:** Alert when fallback rate exceeds threshold (e.g., >5% for >5 minutes).

**Prevention:** Define SLO for fallback duration: fallback acceptable for <15 minutes; beyond that, page on-call.

---

**Fallback Itself Fails**

**Symptom:** Both the primary and the fallback fail; users get errors even during degraded mode.

**Root Cause:** Fallback made a network call (Redis, secondary API) that is also unavailable.

**Diagnostic Command:**

```bash
# Check Redis connectivity from the service
redis-cli -h redis-host ping
```

**Fix:** Always have a truly local fallback at the end of the chain: an in-memory static value or empty collection.

**Prevention:** Fallback chain rule: last element must be zero-network (in-process constant).

---

**Stale Fallback Data Causing Incorrect Behaviour**

**Symptom:** Users see outdated prices or out-of-stock items shown as available during outage.

**Root Cause:** Stale cache used as fallback without indicating data age; critical data treated as optional.

**Diagnostic Command:**

```bash
# Check cache entry age
redis-cli TTL "fallback:product:12345"
# TTL remaining tells you how old the data is
```

**Fix:** Mark response with `X-Data-Freshness: stale` header; show "prices may not be current" notice in UI.

**Prevention:** Classify data criticality at design time: pricing and inventory = critical (fail hard); recommendations = optional (fallback OK).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Circuit Breaker (Microservices)` - opens and triggers fallback when dependency is in hard failure
- `Retry Strategy` - retries are exhausted before fallback is activated
- `Timeout Strategy` - timeout fires, triggering the fallback

**Builds On This (learn these next):**

- `Graceful Degradation` (System Design) - higher-level concept of running in reduced-functionality mode
- `Feature Flags (Microservices)` - can disable features entirely (a form of fallback)
- `Saga Pattern (Microservices)` - compensation transactions are a form of fallback for distributed operations

**Alternatives / Comparisons:**

- `Circuit Breaker (Microservices)` - stops calls (isolation); fallback defines the response (behaviour)
- `Bulkhead Pattern` - isolates thread pools; fallback defines what isolated callers get
- `Rate Limiting (Microservices)` - rejects excess calls; fallback applies to dependency failures

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Alternative response when primary call    │
│              │ fails after retries are exhausted         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Non-critical dependency failure propagates│
│ SOLVES       │ upward as hard error, breaking everything │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Define fallback at DESIGN TIME for every  │
│              │ non-critical call - not during an outage  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Calling non-critical services where       │
│              │ degraded response > error response        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Critical paths (auth, payment, checkout)  │
│              │ where incorrect data is worse than error  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Better UX under partial failure vs risk   │
│              │ of silently serving stale/wrong data      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Plan B that keeps you moving             │
│              │  when Plan A stops answering"             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Circuit Breaker → Graceful Degradation →  │
│              │ Feature Flags                             │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Every external dependency has a fallback strategy, even if the fallback is 'fail gracefully with a clear error message.' The fallback is the planned behavior when a dependency is unavailable - not a safety net for exceptional cases. A system that has designed fallbacks for all dependencies has designed for failure, which is the correct resilience design posture.

**Where else this pattern appears:**
- **Cache with database fallback:** Cache hit returns cached value; cache miss falls back to the database. The cache is the primary source; the database is the fallback. Same fallback pattern.
- **CDN with origin fallback:** CDN hit returns cached content; cache miss falls back to origin server. Same pattern applied to content delivery.
- **Read replica with primary fallback:** Read replica serves reads; if unavailable, falls back to the primary. Same fallback pattern applied to database replication.

---

### 💡 The Surprising Truth

The most dangerous fallback is one that returns stale data without signaling that the data is stale. A product page showing a cached price from 4 hours ago with no indication it may have changed actively misleads users - and can cause business losses (oversold products, incorrect prices). A stale data fallback should show the data with a visual or semantic indicator that it may not be current, and should limit the stale TTL to a business-acceptable window. A fallback that silently returns arbitrarily old data is worse than a clear, honest error message.
---

### 🧠 Think About This Before We Continue

**Q1.** Your product page has three dependencies: inventory (must work), pricing (must work), recommendations (optional). You implement a fallback for recommendations that serves cached popular items. Six months later, the inventory service degrades but doesn't fail completely - it returns stale data 10% of the time. Should you add a fallback for inventory? Trace the exact trade-off: what does adding a "stale inventory fallback" give you, and what risk does it introduce?

*Hint:* Think about what 'stale inventory data' means for different types of decisions: showing 'in stock' when actually out of stock causes overselling (high business cost, requires compensation); showing 'out of stock' when actually in stock causes lost sales (recoverable). The fallback design must ask: what is the business cost of each type of stale data error? If overselling risk is high, the stale inventory fallback should show 'check availability' rather than a specific stock level that may be incorrect.

**Q2.** Your recommendation service has a 30-second cache TTL. Your cache serves as fallback when the service is down. The service has been down for 4 hours. Describe exactly what users are experiencing at the 1-hour mark vs the 5-hour mark. What circuit breaker + cache TTL combination would you design to give you: healthy service data when live, graceful degradation for up to 2 hours, and a clean error state after that?

*Hint:* Think about what happens at the 1-hour mark vs 5-hour mark with a 30-second TTL: the cache refreshes every 30 seconds from the live service. If the service goes down, the last cached value becomes stale after 30 seconds. At 1 hour: cache is 1 hour stale. At 5 hours: cache is 5 hours stale. Explore whether a two-TTL design (short TTL=30s for live-service freshness, long TTL=2h for fallback labeled as stale) combined with a circuit breaker that opens after N failures and returns the long-TTL cached value provides the specified 2-hour graceful degradation window before transitioning to a clear error state.

**Q3 (Design Trade-off):** Your system has a fallback chain: live service → short-TTL cache → long-TTL cache → static default. In production you discover the static default (set 2 years ago) contains incorrect data and cannot be updated without a code deployment. Redesign the fallback chain so static defaults can be updated without a code deployment.

*Hint:* Think about where static defaults could be stored instead of hardcoded in source code: a configuration service (LaunchDarkly, AWS AppConfig), a long-TTL cache pre-populated with authoritative defaults, or a static JSON file in S3 read at startup with a local copy cached. Explore whether 'defaults as configuration' (stored in a system that can be updated without deployment, cached locally so the fallback works even if the config service is unavailable) provides both operational flexibility and high availability.
