---
layout: default
title: "Fallback Strategy"
parent: "Microservices"
nav_order: 652
permalink: /microservices/fallback-strategy/
number: "652"
category: Microservices
difficulty: ★★☆
depends_on: "Circuit Breaker (Microservices), Retry Strategy, Resilience4j"
used_by: "Saga Pattern (Microservices)"
tags: #intermediate, #microservices, #reliability, #distributed, #pattern
---

# 652 — Fallback Strategy

`#intermediate` `#microservices` `#reliability` `#distributed` `#pattern`

⚡ TL;DR — A **Fallback Strategy** defines what a service does when a call to a downstream service fails (after retries and/or when the circuit breaker is open). Options: return cached data, return a default/empty response, queue for later processing, or fail gracefully. Fallbacks convert hard failures into degraded-but-functional experiences.

| #652            | Category: Microservices                                       | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------ | :-------------- |
| **Depends on:** | Circuit Breaker (Microservices), Retry Strategy, Resilience4j |                 |
| **Used by:**    | Saga Pattern (Microservices)                                  |                 |

---

### 📘 Textbook Definition

A **Fallback Strategy** is the response a service provides when a primary operation fails and cannot succeed through retries. It is the "plan B" activated by a Circuit Breaker (when open) or Retry (when maxAttempts exhausted). Fallback strategies exist on a spectrum of degradation: **Return cached data** — serve stale data from a local cache or read replica; **Return a default response** — a neutral, minimal response that allows the caller to continue with limited functionality; **Silent degradation** — omit the non-critical feature (e.g., don't show recommendations if recommendation service is down); **Queue for later processing** — accept the request and process it asynchronously when the dependent service recovers; **Fail fast with clear error** — return a clear error to the user rather than a timeout. The choice of fallback depends on the criticality of the data: a missing recommendation is acceptable; a missing account balance is not. Fallbacks must be designed at the same time as the feature — not as an afterthought.

---

### 🟢 Simple Definition (Easy)

A Fallback is a backup plan when a service call fails. Instead of crashing or showing an error to the user, the service uses an alternative: maybe it returns a cached older version of the data, returns an empty list ("no recommendations available"), or queues the request for later. The user gets a degraded but working experience instead of a 500 error.

---

### 🔵 Simple Definition (Elaborated)

A product detail page calls 5 services: `ProductService`, `PriceService`, `ReviewService`, `RecommendationService`, `InventoryService`. `RecommendationService` goes down. Without fallback: the whole page fails (500 error). With fallback per service: `RecommendationService` fallback returns an empty recommendations list → page loads normally, just without recommendations. The user doesn't know the recommendation service is down — they just don't see the "You might also like" section. Critical data (`ProductService`, `PriceService`) has a stricter fallback: return cached data or fail the page if cache is also stale.

---

### 🔩 First Principles Explanation

**Fallback options — spectrum from graceful to fail-fast:**

```
OPTION 1: Return Cached Data
  When: data can be slightly stale (recommendations, product descriptions, prices with TTL)
  Implementation:
    - Local cache (ConcurrentHashMap, Caffeine) with TTL
    - Distributed cache (Redis) shared across instances
    - Read replica (database fallback for write-heavy primary)
  Risk: stale data served (price changed, product out of stock — cache shows in-stock)
  Acceptable for: non-critical content, best-effort features

OPTION 2: Return Default/Empty Response
  When: feature is optional, absence is acceptable
  Examples:
    - Recommendations: [] (empty list) → no "You might also like" section
    - Notifications: [] → notification bell shows 0 (user rechecks later)
    - Search facets: [] → search still works, just no filter options
  Risk: user loses access to feature, but core flow works
  Acceptable for: optional/enhancement features

OPTION 3: Queue for Later Processing (async fallback)
  When: operation can be deferred (email, push notification, analytics event)
  Implementation:
    - Add to persistent queue (database table or message queue)
    - Background worker retries when dependency recovers
    - User sees: "Your request is being processed" (or nothing — fire-and-forget)
  Risk: eventual processing only — not immediately visible
  Acceptable for: notifications, emails, audit logs, analytics

OPTION 4: Fail Fast with Clear Error
  When: data is critical and cannot be approximated
  Examples:
    - Account balance: cannot show stale → show "Balance temporarily unavailable"
    - Payment processing: cannot guess → "Payment service unavailable, please retry"
    - Authentication: cannot continue without → 503 with clear message
  Risk: user sees error (better than wrong data)
  Acceptable for: financial, security-critical operations

OPTION 5: Static/Hardcoded Fallback
  When: completely static data is better than nothing
  Example:
    - Featured products: hardcoded list of always-available products
    - CMS content: last-known-good cached version
  Risk: outdated but not wrong
  Acceptable for: marketing content, static config-like data
```

**Fallback quality monitoring — the "fallback rate" metric:**

```
The danger of fallbacks: they hide problems.

  If RecommendationService is down for 2 days:
  → Circuit breaker OPEN → fallback returns []
  → Product pages load normally (to users and monitoring)
  → No alert fires: 200 OK responses
  → Engineers don't know recommendation service has been broken for 2 days!

MONITOR FALLBACK INVOCATION RATE:
  Metric: resilience4j_circuitbreaker_calls_total{kind="not_permitted"} > 0
  Alert: fallback_invocations > 5% of calls → page on-call
  Dashboard: show fallback rate alongside normal success rate

  Separate from error rate:
  success_rate = (successful_calls / total_calls)
  degraded_rate = (fallback_calls / total_calls)
  error_rate = (total_failures - fallback_calls) / total_calls

  A service can be 100% "available" (all requests return 200)
  but 30% degraded (30% of responses came from fallback).
  This is important operational intelligence.
```

---

### ❓ Why Does This Exist (Why Before What)

In a distributed system, some dependencies will be unavailable at any given time. The question is not "will a service call fail?" but "what should happen when it does?" Without a fallback strategy, failures in non-critical dependencies propagate into user-visible errors — even when the core functionality is unaffected. Fallbacks implement the resilience principle: "fail gracefully at the boundary of each dependency."

---

### 🧠 Mental Model / Analogy

> A Fallback Strategy is like a restaurant's plan when a supplier doesn't deliver. If the salmon supplier fails to deliver: (a) serve yesterday's salmon (cached data — may be slightly off); (b) remove salmon from the menu today (silent degradation — return empty); (c) offer a substitute dish (default response — serve a different product); (d) tell the customer "salmon unavailable today, recommend the chicken" (fail fast with clear message). The restaurant stays open; the customer gets a meal (or a clear explanation) rather than being locked out.

"Supplier fails to deliver" = downstream service unavailable
"Yesterday's salmon" = stale cached data
"Remove salmon from menu" = return empty/null response
"Substitute dish" = default fallback response
"Customer gets clear message" = fail fast with informative error

---

### ⚙️ How It Works (Mechanism)

**Multi-level fallback — cache first, then default:**

```java
@Service
class RecommendationService {

    @Autowired RecommendationCache cache;  // Redis cache

    @CircuitBreaker(name = "recommendation-service", fallbackMethod = "fallback1")
    @Retry(name = "recommendation-service")
    public List<Product> getRecommendations(Long userId) {
        return recommendationClient.getTopN(userId, 10);
    }

    // Level 1 fallback: try cache first:
    public List<Product> fallback1(Long userId, Exception ex) {
        List<Product> cached = cache.get(userId);
        if (cached != null && !cached.isEmpty()) {
            log.warn("Recommendation service down, serving cached data for user {}", userId);
            return cached;
        }
        // Cache miss — go to level 2:
        return fallback2(userId, ex);
    }

    // Level 2 fallback: return trending products (static/precomputed):
    public List<Product> fallback2(Long userId, Exception ex) {
        log.warn("Recommendation service down + no cache, returning trending products");
        metrics.counter("recommendations.fallback.trending").increment();
        return trendingProductsLoader.getTopTrending(10);
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Circuit Breaker (OPEN) / Retry (exhausted)
        │
        ▼
Fallback Strategy  ◄──── (you are here)
(what to do when primary call fails)
        │
        ├── Cached data → Redis, local cache
        ├── Default response → empty list, neutral value
        ├── Queue → async processing for deferrable operations
        └── Fail fast → clear error message (critical operations)
```

---

### 💻 Code Example

**Payment fallback — queue for async processing:**

```java
@Service
class PaymentProcessor {

    @CircuitBreaker(name = "payment-gateway", fallbackMethod = "queuePayment")
    @Retry(name = "payment-gateway")
    public PaymentResult processPayment(PaymentRequest request) {
        return externalGateway.charge(request);
    }

    // Fallback: persist to outbox for retry when gateway recovers:
    public PaymentResult queuePayment(PaymentRequest request, Exception ex) {
        log.error("Payment gateway unavailable, queuing payment for order {}",
            request.getOrderId());

        // Persist to database (durable, survives app restart):
        pendingPaymentRepository.save(PendingPayment.builder()
            .orderId(request.getOrderId())
            .amount(request.getAmount())
            .customerId(request.getCustomerId())
            .status(PendingPaymentStatus.QUEUED)
            .retryAfter(Instant.now().plus(Duration.ofMinutes(5)))
            .build());

        // Metric: track queued payments (alert if too many accumulate):
        meterRegistry.counter("payments.queued").increment();

        // Tell user: order accepted, payment processing deferred:
        return PaymentResult.pending(
            request.getOrderId(),
            "Your order is confirmed. Payment will be processed shortly."
        );
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                 | Reality                                                                                                                                                                                                                                                |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Fallbacks make a system more reliable by hiding errors        | Fallbacks hide failures from users (good) but must still generate alerts to engineers (required). A fallback rate of 30% while all requests return 200 OK is a serious operational problem that requires immediate attention                           |
| The fallback should try to do what the primary operation does | Fallbacks should be simpler and more reliable than the primary operation. A complex fallback that also fails provides no protection. Fallbacks must be designed to succeed: use local cache, hardcoded data, or simple queue operations                |
| All failures should have a fallback                           | Critical operations (authentication, financial transactions) should fail fast with a clear error rather than return degraded data. The appropriate fallback for "cannot verify user identity" is not "assume authenticated" — it is "401 Unauthorized" |

---

### 🔥 Pitfalls in Production

**Fallback rate not monitored → silent degradation for days**

```
SCENARIO:
  RecommendationService has been returning 503 for 3 days.
  @CircuitBreaker fallback returns []: product pages load normally.
  No alerts fire: all HTTP requests return 200.
  Revenue data shows drop in "recommended product" purchases.
  Only noticed on day 3 when data analyst queries the dashboard.

ROOT CAUSE: fallback success hides the underlying failure.

PREVENTION:
  1. Monitor fallback invocation rate as a separate metric:
     @Gauge(name="recommendation.fallback.rate")
     double fallbackRate() {
         CircuitBreaker cb = cbRegistry.circuitBreaker("recommendation-service");
         CircuitBreaker.Metrics m = cb.getMetrics();
         return m.getNumberOfNotPermittedCalls() / (double) m.getNumberOfBufferedCalls();
     }
     Alert: recommendation.fallback.rate > 0.01 (>1% in fallback)

  2. Structured logging with fallback context:
     MDC.put("fallback", "recommendation-service");
     log.warn("Serving recommendation fallback for user {}", userId);
     → Splunk/Datadog query: fallback=recommendation-service → count over time → alert

  3. Separate SLO for fallback rate:
     Primary SLO: 99.9% requests succeed (200/201)
     Secondary SLO: <1% requests served from fallback
     → Both SLOs must be GREEN for service to be "healthy"
```

---

### 🔗 Related Keywords

- `Circuit Breaker (Microservices)` — opens the circuit and triggers fallback invocation
- `Retry Strategy` — exhausts retries before invoking fallback
- `Resilience4j` — provides `fallbackMethod` on `@CircuitBreaker`, `@Retry`, `@Bulkhead`
- `Saga Pattern (Microservices)` — uses compensating transactions as fallbacks for distributed workflows

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ FALLBACK     │ Return cached data (stale OK)             │
│ OPTIONS      │ Return empty/default                      │
│              │ Queue for async processing                │
│              │ Fail fast with clear error (critical)     │
├──────────────┼───────────────────────────────────────────┤
│ DESIGN RULE  │ Fallback must be designed with the feature│
│              │ Not: "we'll handle that if it breaks"     │
├──────────────┼───────────────────────────────────────────┤
│ MONITORING   │ Track fallback rate as a separate metric  │
│              │ Alert on fallback rate > X%               │
│ MISTAKE      │ Fallback 200 OK hides failure from ops    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A financial dashboard service uses a cached fallback for account balance when `AccountService` is unavailable. The cache has a 5-minute TTL. A user logs in, sees their balance (from cache), and makes a transfer that relies on this balance — the actual balance was $10 (transaction went through after the cache was populated), but the cached balance shows $1,000 (pre-transfer). The user makes a second $500 transfer based on the stale cache. The `TransferService` checks the real balance at transfer time — the transfer is rejected. But the user was already shown $1,000. Design a fallback strategy for account balance that prevents showing stale financial data while still providing a useful degraded experience.

**Q2.** An e-commerce checkout flow has these service dependencies: `InventoryService` (critical — must validate stock), `PricingService` (critical — must show final price), `TaxService` (important — calculate tax), `LoyaltyService` (optional — apply points). Design the fallback strategy for each: for `TaxService` unavailability, should you (a) block checkout with an error, (b) apply the last cached tax rate, or (c) proceed without tax and reconcile later? What are the legal and business implications of each option? How does your answer change if the platform operates in multiple tax jurisdictions?
