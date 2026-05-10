---
id: DST-047
title: "Fallback"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-042, DST-046
related: DST-042, DST-048, DST-043, DST-044, DST-046
tags:
  - distributed
  - reliability
  - pattern
  - architecture
  - foundational
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 47
permalink: /distributed-systems/fallback/
---

# DST-047 - Fallback

⚡ TL;DR - A fallback is an alternative response strategy invoked when a primary operation fails — providing degraded but useful output instead of propagating errors, so the system remains partially functional under dependency failures.

| Metadata        |                                             |     |
| :-------------- | :------------------------------------------ | :-- |
| **Depends on:** | DST-042, DST-046                            |     |
| **Related:**    | DST-042, DST-048, DST-043, DST-044, DST-046 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An e-commerce product page calls a Recommendations service to display "You may also like..." items. The Recommendations service is down. Without a fallback: the entire product page returns an error. The user cannot view the product they came to buy — because a NON-CRITICAL feature (recommendations) failed. A critical user journey is blocked by a non-critical dependency.

**THE BREAKING POINT:**
Every feature on a page has different criticality. "Add to Cart" is critical. "Recommendations" is nice-to-have. "Live inventory count" is important but not blocking. Without fallbacks: all features have the same reliability tier (the lowest one — the least reliable dependency). With fallbacks: features can fail independently and gracefully, each with a defined "reduced mode" that is still useful to the user.

**THE INVENTION MOMENT:**
Netflix Hystrix (2012) popularized the fallback as a first-class pattern: every `HystrixCommand` had a `getFallback()` method. Netflix's architecture insight: their recommendation engine failure should not prevent customers from watching movies they already know about. The fallback: return a cached list of popular movies. Degraded but functional — 80% of user value preserved with 0 dependency on the Recommendations service.

**EVOLUTION:**
2012: Netflix Hystrix — `getFallback()` as core API. 2014: Hystrix with cache-based fallback (Hystrix Request Cache). 2016: Istio fault injection + fallback via retry/timeout policies. 2018: Resilience4j `Fallback` decorator — functional, non-opinionated. 2020+: Service mesh (Istio, Linkerd) with local response injection as fallback for failed upstreams. Today: fallback is standard in any resilience library, often combined with circuit breaker (DST-042) to trigger fallback automatically when circuit opens.

---

### 📘 Textbook Definition

**Fallback** is a resilience pattern where a secondary response strategy is defined for use when the primary operation fails (due to timeout, error, or circuit breaker trip). Types of fallback: (1) **Static fallback:** return a hardcoded default value. `getUser(id)` → if fails: return `User.ANONYMOUS`. (2) **Cached fallback:** return the last-known good response from cache. (3) **Degraded mode:** return a reduced-functionality response. Recommendations: return generic popular items instead of personalized. (4) **Fail-open:** allow the operation to proceed with a permissive default. Authorization check fails → allow by default (risk: bypasses security). (5) **Stubbed response:** return a response that signals to the UI to hide the component entirely. The critical invariant: a fallback should NEVER call the same failing dependency again. It must be an independent path that works when the primary path doesn't.

---

### ⏱️ Understand It in 30 Seconds

**One line:** When the primary call fails, run this alternative code instead of propagating the error.

> Fallback is like a co-pilot. If the pilot (primary service) becomes incapacitated, the co-pilot (fallback) takes control and lands the plane — not perfectly (the co-pilot might be less experienced), but safely. A crash (propagated error) is avoided. The passengers (users) may experience a rougher landing, but they arrive.

**One insight:** The value of a fallback is entirely determined by the quality of the fallback response. A fallback that returns garbage degrades the user experience more than the original error. Design the fallback before choosing it: what is the minimum useful response for this operation?

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Fallback must not call the failing dependency.** A fallback that calls the same service that just failed is not a fallback — it's a retry. Fallback must be an INDEPENDENT response path.
2. **Fallback should never throw.** If the fallback itself fails: you now have no response and you've hidden the original error. Fallback must be maximally simple and reliable.
3. **Fallback degrades functionality, not correctness.** A fallback that returns incorrect data (stale, wrong, misleading) is worse than an honest error. If no useful fallback exists: propagate the error rather than return incorrect data.
4. **Fallback scope = the circuit boundary.** Fallback is defined for a specific dependency interaction, not for the whole service. Recommendations fallback ≠ Shopping Cart fallback.

**DERIVED DESIGN:**

```
Primary:  try { return recommendationService.get(userId) }
Fallback: catch { return cache.getLastKnown(userId)
                    .orElse(popularItems.getTop10()) }
```

**THE TRADE-OFFS:**
**Gain:** Partial availability (service works at reduced capacity). User experience (partial functionality > total failure). Isolation (dependency failure doesn't kill the whole flow).
**Cost:** Stale data (cache fallback returns yesterday's data). Complexity (every call needs a defined fallback). False confidence (system "works" but silently degraded). Alert fatigue if fallback activates frequently without investigation.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Determining what a useful degraded response IS for each operation — this requires domain knowledge and cannot be automated. Different operations have different fallback semantics (recommendations vs authorization vs pricing).
**Accidental:** Hystrix command wrapping vs Resilience4j `Fallback.ofSupplier()` vs Spring `@CircuitBreaker(fallbackMethod="myFallback")`. Different APIs, same pattern.

---

### 🧪 Thought Experiment

**SETUP:** A product search service calls three dependencies: Product Database (critical), Inventory Service (important), Recommendations Service (nice-to-have). All three are independent.

**WITHOUT FALLBACKS:**

- Inventory Service has 30s outage.
- Product page: calls Product DB (succeeds) → calls Inventory (fails) → ERROR returned to user.
- User cannot view the product page. Product DB (working) returns no value.
- Conversion impact: 100% of product page views fail during Inventory outage.

**WITH FALLBACKS:**

- Product DB: no fallback needed (it's critical — if it fails, error is appropriate).
- Inventory: fallback = show "Check availability in cart" (don't show exact count). User can still see product, add to cart.
- Recommendations: fallback = show popular items from last-hour cache.
- Product page: Product DB succeeds → Inventory fails → Inventory FALLBACK activates → "Check availability in cart" shown → Recommendations FALLBACK activates → popular items shown.
- Result: product page is 90% functional. Conversion impact: minimal.

**THE INSIGHT:** A fallback converts a hard dependency (must succeed for user to get value) into a soft dependency (can fail gracefully). The key design decision: is THIS dependency critical (no fallback, propagate error) or non-critical (fallback = degraded mode)?

---

### 🧠 Mental Model / Analogy

> Fallback is like a generator that kicks in when the power grid fails. The building (your service) continues to function — lights are on, critical systems run. But some features are disabled: air conditioning, high-power appliances. You have electricity (service responds), but at reduced capacity (some features unavailable). The generator (fallback) is simpler and less powerful than the grid (primary dependency) but reliable.

**Mapping:**

- **Main power grid** → primary dependency (Recommendations Service)
- **Generator** → fallback (static popular items list)
- **Building with power** → service responding to users
- **Critical systems (lights, server room)** → core features that fallback preserves
- **Non-critical systems (AC)** → features not available in degraded mode

Where this analogy breaks down: a generator runs continuously when the grid is down. A software fallback is invoked per-request — the primary is retried on the next request (unless circuit breaker holds the circuit open). Fallback is not a permanent replacement — it's a request-level alternative while the primary recovers.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A fallback is a backup plan for when the main plan fails. "If the restaurant is full: go to the backup restaurant." "If the main road is closed: take the alternate route." In software: "If the Recommendations service is down: show popular items instead." The user still gets SOMETHING useful, rather than an error page.

**Level 2 - How to use it (junior developer):**
Resilience4j Fallback:

```java
Fallback<List<Product>> fallback = Fallback.ofSupplier(
    () -> popularItemsCache.getTop10(),  // fallback supplier
    SocketTimeoutException.class,
    CircuitBreakerOpenException.class);
// Wrap primary call:
Supplier<List<Product>> decorated =
    Fallback.decorateSupplier(fallback,
        () -> recommendationService.get(userId));
List<Product> result = Try.ofSupplier(decorated)
    .getOrElseGet(throwable -> popularItemsCache.getTop10());
```

Spring `@CircuitBreaker`: `@CircuitBreaker(name="recommendations", fallbackMethod="defaultRecommendations")` on service method.

**Level 3 - How it works (mid-level engineer):**
Resilience4j `Fallback` checks the exception type. If it matches the configured list: runs the fallback supplier. If not: rethrows (don't swallow unexpected exceptions). Key: fallback is registered by exception TYPE. `CircuitBreakerOpenException` should always be in the fallback exception list — otherwise circuit breaker trips but no fallback runs, and the user still gets an error. Fallback + circuit breaker integration: circuit breaker opens → throws `CallNotPermittedException` → fallback catches → returns degraded response. Seamless user experience during circuit open state.

**Level 4 - Why it was designed this way (senior/staff):**
Netflix's original Hystrix design separated fallback into three tiers: (1) In-memory fallback: no I/O, no network, no failure risk. Returns a constant or lightweight computation. (2) Fallback with network call: calls a different, simpler service. Risky — the fallback itself can fail. Hystrix discouraged this unless the fallback service was extremely reliable. (3) No fallback: propagate the error to the caller. For Hystrix: the rule was "if you can't implement tier 1 (in-memory), default to tier 3 (propagate error)." Tier 2 (network fallback) was actively discouraged because it introduces a second failure domain. Modern recommendation: fallback hierarchy: (1) in-memory constant → (2) local cache → (3) degraded/empty response → (4) error propagation. Never: (4) call another external service.

**Expert Thinking Cues:**

- "Circuit breaker trips but users still see errors" → Fallback is not registered for `CallNotPermittedException` (Resilience4j) or `HystrixCircuitBreakerOpenException` (Hystrix). The circuit breaker trips (correct) but the fallback doesn't activate. Fix: add `CallNotPermittedException.class` to fallback exception list.
- "Fallback cache is returning data from last week" → Fallback cache TTL is too long. Fallback should be recent enough to be useful but not stale enough to mislead. Rule: cache TTL should reflect the acceptable staleness of the data. For inventory count: 5 minutes. For product name: 24 hours. For pricing: 1 hour (don't let users see outdated prices that differ at checkout — causes trust issues).
- "Fallback is masking real errors — on-call never knows the dependency is down" → Fallback should always LOG at WARN level and increment a metric: `fallback.activations.count{service="recommendations"}`. Fallback is not transparent — the dependency is failing. Alert when fallback activation rate exceeds X% (e.g., 5%). This separates "fallback working as designed" from "fallback masking a persistent outage."

---

### ⚙️ How It Works (Mechanism)

**Fallback in circuit breaker context:**

```
Request
  │
  ▼
[Circuit Breaker: OPEN?]
  │ YES                    NO
  ▼                        ▼
[Throw CallNot-       [Call Primary Service]
 PermittedException]       │
  │                    Success: return response
  │                    Failure: throw exception
  ▼                        │
[Fallback Handler] ◀────────┘
  │
  ├── Exception is in fallback list?
  │   YES: run fallback supplier
  │   NO:  rethrow exception
  │
  ▼
[Return fallback response]
  (log WARN + increment metric)
```

**Fallback hierarchy (priority order):**

```
1. In-memory constant (most reliable, always works)
   return List.of(POPULAR_1, POPULAR_2, POPULAR_3)
2. Local in-process cache (very reliable, no I/O)
   return localCache.getIfPresent(cacheKey)
3. Degraded response (return less data, still valid)
   return ResponseEntity.ok().header("X-Degraded","true")
4. Empty valid response (signal "nothing" cleanly)
   return Collections.emptyList()
5. Error propagation (last resort: honest failure)
   throw new ServiceUnavailableException()
```

---

### 🔄 The Complete Picture - End-to-End Flow

**PRODUCT PAGE WITH MULTIPLE FALLBACKS:**

```
Browser  Product Page  RecoService  InventoryService
   │          │              │              │
   │─GET /p/1─▶              │              │
   │          │─getProduct──▶DB             │
   │          │◀─product────────────────────│
   │          │─getReco(1)──▶│              │
   │          │              │ [DOWN - timeout]
   │          │◀─timeout─────│              │
   │          │ [fallback: popular items]   │
   │          │─getInventory(1)────────────▶│
   │          │              │ ← YOU ARE HERE
   │          │◀─503─────────────────────────│ [overloaded]
   │          │ [fallback: "check in cart"] │
   │          │                             │
   │◀─200 HTML│ (product + popular reco +   │
   │  [partial]  "check in cart" message)
```

**WHAT CHANGES AT SCALE:**
At scale: the fallback cache must be populated independently of the primary call. If the cache is only populated by the primary (on success), and the primary has been failing for 2 hours: the cache is cold → fallback returns empty → no better than an error. Solution: a separate "cache warmer" job that populates fallback caches independently. Decouples cache population from request-time failures.

---

### 💻 Code Example

**BAD - No fallback (error propagates, page fails):**

```java
// BAD: no fallback — one dependency brings down the page
@GetMapping("/products/{id}")
public ProductPage getProductPage(@PathVariable String id) {
    Product product = productDb.get(id);
    // If recommendations service is down: throws exception
    // User gets 500 — can't view the product
    List<Product> recommendations =
        recommendationService.get(id);
    Inventory inventory = inventoryService.get(id);
    return new ProductPage(product, recommendations, inventory);
}
```

**GOOD - Layered fallbacks per dependency:**

```java
@GetMapping("/products/{id}")
public ProductPage getProductPage(@PathVariable String id) {
    Product product = productDb.get(id); // Critical: no fallback

    // Non-critical: fallback to popular items
    List<Product> recommendations =
        getRecommendationsWithFallback(id);

    // Important: fallback to "check in cart" message
    InventoryStatus inventory =
        getInventoryWithFallback(id);

    return new ProductPage(product, recommendations, inventory);
}

@CircuitBreaker(name = "recommendations",
    fallbackMethod = "popularItemsFallback")
public List<Product> getRecommendations(String productId) {
    return recommendationService.get(productId);
}

// Fallback method signature must match primary + exception:
public List<Product> popularItemsFallback(
    String productId, Exception ex) {
    log.warn("Recommendations fallback for {}: {}",
        productId, ex.getClass().getSimpleName());
    fallbackCounter.increment(); // Metric: alert if sustained
    return popularItemsCache.getTop10(); // In-memory: no I/O
}

@CircuitBreaker(name = "inventory",
    fallbackMethod = "inventoryCheckInCartFallback")
public InventoryStatus getInventory(String productId) {
    return inventoryService.get(productId);
}

public InventoryStatus inventoryCheckInCartFallback(
    String productId, Exception ex) {
    log.warn("Inventory fallback for {}: {}",
        productId, ex.getClass().getSimpleName());
    return InventoryStatus.CHECK_IN_CART; // Signal to UI
}
```

---

### ⚖️ Comparison Table

| Fallback type             | I/O required     | Failure risk | Freshness             | Best for                 |
| :------------------------ | :--------------- | :----------- | :-------------------- | :----------------------- |
| In-memory constant        | None             | Zero         | Stale (code-deployed) | Rarely-changing defaults |
| Local cache               | None (in-memory) | Near-zero    | Minutes to hours      | Personalized data        |
| Degraded response         | None             | Zero         | N/A                   | Partial data acceptable  |
| Empty list / null object  | None             | Zero         | N/A                   | Lists, optional features |
| External fallback service | Yes (network)    | High         | Fresh                 | Almost never (risky)     |

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                                                                                                                                                                                                                                                   |
| :------------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Fallback = retry"                                      | Retry calls the SAME failing dependency again. Fallback uses a DIFFERENT response path that doesn't depend on the failing service. Retry is appropriate for transient failures (network blip). Fallback is appropriate for sustained failures (service down). The correct sequence: retry first (1-3 times with backoff), then fallback.                  |
| "Returning null is a valid fallback"                    | Returning null transfers the burden of handling failure to every downstream consumer of the null. A null recommendation list → NPE in the template renderer → page fails. A valid fallback returns an EMPTY LIST (null object pattern), a default object, or an explicit "degraded" indicator that the UI knows how to handle.                            |
| "Fallback hides the problem — I shouldn't use it"       | Fallback hides the problem FROM THE USER (correct — user gets partial functionality). It must NOT hide the problem from OPERATIONS. Every fallback activation must log at WARN level and increment a metric. Alert when fallback activation rate > 5%. Fallback + observability = user protection without operational blindness.                          |
| "Fallback should try a different API for the same data" | This creates a second point of failure in the fallback path. If the fallback calls another external API that is also slow or unavailable: the fallback itself can be slow or fail. The entire point of a fallback is to be MORE reliable than the primary. External API calls in fallback violate this invariant. Use in-memory or local cache fallbacks. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Fallback Masks Persistent Outage — No Alert**

**Symptom:** Recommendations service has been down for 3 hours. Users see popular items (fallback). Engineers are unaware — no alert fired. Product team discovers the outage in a weekly metrics review. 3 hours of degraded recommendations with no incident response.
**Root Cause:** Fallback activated correctly, but no alert on sustained fallback activation. No metric for fallback rate. The outage was invisible to on-call.
**Diagnostic:**

```bash
# Check if fallback metrics are emitted:
curl http://service/actuator/metrics/resilience4j.fallback.calls
# Should show: count{outcome=success,fallback=recommendations}

# If no metric: fallback is not instrumented
# Check logs for fallback WARN messages:
grep "Recommendations fallback" app.log | \
  awk '{print $1}' | cut -c1-13 | sort | uniq -c
# If count is high and sustained: fallback masking outage

# Check alerting rules for fallback rate:
cat prometheus-alerts.yaml | grep fallback
# If no alert rule: add one
```

**Fix:**
BAD: Fallback activates, returns cached data, logs DEBUG message.
GOOD: Every fallback activation: log WARN, increment metric `fallback_activations_total{service="recommendations"}`. Prometheus alert: `rate(fallback_activations_total[5m]) > 0.05` → PagerDuty. This ensures fallback protects users AND alerts engineers.
**Prevention:** Code review rule: every fallback must log WARN and increment a named counter. Integration test: verify metrics are emitted when fallback activates.

**Failure Mode 2: Stale Fallback Cache Causes Incorrect Data**

**Symptom:** Inventory service outage lasting 4 hours. Fallback: return last-known inventory from Redis cache with 6-hour TTL. After inventory service restores: users see correct inventory. But during outage: some users saw "In Stock" for items that were actually sold out 5 hours before the outage. Users added to cart, proceeded to checkout, then received "Out of Stock" error at payment.
**Root Cause:** Fallback cache TTL (6 hours) is too long relative to inventory change frequency. An item sold out 5 hours before outage: cache shows stale "In Stock" state for the duration of the outage.
**Diagnostic:**

```bash
# Check cache TTL for inventory fallback:
redis-cli ttl "inventory:fallback:*"
# If TTL > acceptable_staleness: adjust

# Check how frequently inventory data changes:
SELECT COUNT(*), date_trunc('hour', updated_at)
FROM inventory WHERE updated_at > NOW() - INTERVAL '7 days'
GROUP BY 2 ORDER BY 2;
# Frequency of updates = required cache refresh rate
```

**Fix:**
BAD: Cache TTL = 6h for inventory data that changes every 30 minutes.
GOOD: Align TTL with acceptable staleness per data type: inventory: 5m. Product names: 24h. Pricing: 30m. Also: show "availability may be outdated" warning in UI when fallback is active.
**Prevention:** Classify data by change frequency and set TTL accordingly. Show user-visible staleness warning when fallback data is beyond a freshness threshold.

**Failure Mode 3: Security - Fail-Open Fallback Bypasses Authorization**

**Symptom:** A permissions service falls under high load. The calling service has a "fail-open" fallback: if permissions check fails (timeout or error), allow the operation to proceed (avoid disrupting users). An attacker discovers this: sends a burst of requests that trigger circuit breaker on the permissions service, then proceeds to access resources they shouldn't have access to. Permissions fallback = authorization bypass.
**Root Cause:** Fail-open fallback on a SECURITY boundary. For non-critical features: fail-open is acceptable. For security controls: fail-open is a vulnerability. The fallback inverted the security requirement: "deny on failure" became "allow on failure."
**Diagnostic:**

```bash
# Check what fallback is configured for auth/permissions calls:
grep -r "fallback\|getFallback\|@CircuitBreaker" \
  src/main/java/security/ src/main/java/auth/
# If fallback returns 'true' or 'ALLOWED': fail-open = vulnerability

# Check access logs during permissions service outage:
grep "permissions_fallback=true" access.log | \
  awk '{print $3}' | sort | uniq -c | sort -rn
# Any access via fallback to sensitive resources: incident
```

**Fix:**
BAD: `return true` (allow) as fallback for permissions check.
GOOD: `return false` (deny) — fail-closed for security boundaries. Or: use local cache of recent permissions decisions with short TTL (5-60 seconds), never fail-open. For critical auth: if the auth service is down, deny access and show "service temporarily unavailable."
**Prevention:** Code review rule: any fallback on a security-sensitive method must be fail-CLOSED (deny). Never use fail-open for authentication, authorization, fraud detection, or rate limiting.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-042 - Circuit Breaker (fallback is typically triggered when circuit breaker opens — understand circuit breaker first)
- DST-046 - Timeout (timeout triggers the exception that triggers the fallback — timeout before fallback)

**Builds On This (learn these next):**

- DST-048 - Graceful Degradation (broader pattern of which fallback is a mechanism)

**Alternatives / Comparisons:**

- DST-042 - Circuit Breaker (complementary — circuit breaker trips the fallback)
- DST-044 - Retry with Backoff (retry first, then fallback if retries exhausted)
- DST-043 - Bulkhead (bulkhead prevents resource exhaustion; fallback handles the rejected calls)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Alternative response strategy  |
|                  | invoked when the primary call  |
|                  | fails (timeout, error, circuit)|
+------------------+--------------------------------+
| PROBLEM SOLVED   | Hard dependency on non-critical|
|                  | services causes total page/    |
|                  | request failure                |
+------------------+--------------------------------+
| KEY INSIGHT      | Classify dependencies: critical|
|                  | (no fallback) vs non-critical  |
|                  | (fallback to degraded mode)    |
+------------------+--------------------------------+
| USE WHEN         | Dependency failure should give |
|                  | partial functionality, not     |
|                  | total failure                  |
+------------------+--------------------------------+
| AVOID WHEN       | Operation is security-critical |
|                  | or no meaningful degraded mode |
|                  | exists (propagate error instead)|
+------------------+--------------------------------+
| TRADE-OFF        | Partial availability vs        |
|                  | stale/incorrect data risk      |
+------------------+--------------------------------+
| ONE-LINER        | If primary fails, run this     |
|                  | simpler independent backup code|
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-048 Graceful Degradation,  |
|                  | DST-042 Circuit Breaker        |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. Fallback must NOT call the failing dependency — it is an independent response path. A fallback that calls the same service that just failed is a retry, not a fallback.
2. Every fallback activation must log WARN and increment a metric. Fallback protects users — but must not hide outages from operators. Alert when sustained fallback rate > 5%.
3. Security controls must be fail-CLOSED (deny on failure), never fail-open. A fail-open fallback on an authorization check is a security vulnerability — attackers can trigger the fallback intentionally.

**Interview one-liner:**
"A fallback provides an alternative response when a primary call fails — so the system returns degraded but useful output rather than propagating an error. Implemented with Resilience4j `@CircuitBreaker(fallbackMethod=...)` or Netflix Hystrix `getFallback()`. Key design rules: fallback must not call the failing dependency (it's a different path), must log WARN + emit metrics (so outages are visible), and security controls must be fail-closed (deny, not allow, on failure). Fallback converts hard dependencies into soft dependencies — the product page works even when the Recommendations service is down."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Design systems with explicit failure modes, not just success modes. For every external dependency: ask "if this fails, what should the user experience?" The answer determines whether to use: error propagation (this is critical), fallback (this is degraded but useful), or silent omission (this is optional). This principle — explicit failure design — applies to UI components (skeleton loaders vs error states vs empty states), database queries (default values when row missing), and infrastructure (multi-region failover when primary region unavailable).

**Where else this pattern appears:**

- **UI progressive enhancement:** A web page is designed to work without JavaScript (fallback: HTML form submission). With JavaScript: enhanced with client-side validation, auto-complete, real-time updates. If JavaScript fails to load: the page still works (degraded mode). Same fallback principle: progressive enhancement = "if primary enhancement fails, fall back to the baseline that still works."
- **DNS failover:** Primary DNS record points to the primary data center. Health checks run continuously. If primary data center is unhealthy: DNS updates (TTL-based failover) to point to the secondary data center. The secondary is a geographic fallback: degraded (higher latency, possibly fewer features) but functional. DNS-level fallback is the infrastructure equivalent of software-level circuit breaker + fallback.
- **CDN cache serving stale content (stale-while-revalidate):** When an origin server is unavailable: the CDN serves the cached (potentially stale) version of the content rather than returning a 503 error. `Cache-Control: stale-while-revalidate=60, stale-if-error=86400` tells CDNs: serve stale content for up to 24 hours if the origin errors. The CDN's error fallback = serve last-known-good cached content. Same pattern: cached fallback preserving user experience during origin failures.

---

### 💡 The Surprising Truth

The most dangerous fallback is the one that looks like it's working. Netflix's Chaos Engineering team discovered that when a personalization service failed, their fallback (show popular content) was so good that monitoring dashboards showed "normal" engagement metrics — because users watched popular content at nearly the same rate as personalized content. The outage was invisible in business metrics. The surprising truth: a high-quality fallback can make a production incident undetectable in business metrics. Engineers celebrating "no user impact" during an outage may actually be celebrating a good fallback, not the absence of failure. This is why fallback activation metrics MUST be separate from business metrics — they measure the health of the system, not the behavior of the users.

---

### 🧠 Think About This Before We Continue

**Q1 (A - System Interaction):** Service A has a circuit breaker + fallback for calls to Service B. The fallback returns a cached value with a 1-hour TTL. Service B goes down at 9:00 AM. The cache was last populated at 8:30 AM. By 9:45 AM (45 minutes after outage start): the product team notices recommendations are "wrong." By 10:30 AM (1 hour): the cache TTL expires. What happens at 10:30 AM, and what is the correct design?
_Hint:_ At 10:30 AM: cache TTL expires. Fallback's in-memory cache is now empty. Fallback has no data to return. Options: (1) Fall through to empty list (probably the next level in the fallback hierarchy — valid if empty list is acceptable). (2) Return `null` — dangerous if callers don't handle null. (3) Throw exception — now the fallback itself fails, which is as bad as no fallback. Correct design: fallback hierarchy with multiple levels: (1) in-memory cache (up to 1h TTL) → (2) hardcoded popular items list (constant, always works) → (3) empty list (signal "nothing available"). Never let the last fallback fail. The deepest level must be infallible (in-memory constant).

**Q2 (C - Design Trade-off):** A team proposes using another external service as the fallback for their primary recommendations service. The argument: the backup service is more reliable (99.9% vs 99%) and less loaded. What are the arguments for and against this design? Under what specific condition would it be appropriate?
_Hint:_ Against: (1) Two failure domains — if both primary AND backup fail (correlated outage, shared infrastructure, vendor dependency): fallback fails too. (2) Network call in fallback path — adds latency and failure risk to the fallback. (3) Circuit breaker on backup? Now you need fallback-of-fallback. (4) Increased complexity — two external dependencies to manage, monitor, contract with. For: (1) Backup service provides meaningfully better data than a local cache (personalized vs generic). (2) Backup service is on genuinely independent infrastructure (different cloud provider, different region, different vendor). Appropriate condition: the backup is truly independent (different vendor, different network, different deployment), the cost of a static/cached fallback is high (personalization drives significant revenue), and the latency budget allows for a second network call. For most cases: local cache fallback is simpler and more reliable. External fallback only when independence is guaranteed.

**Q3 (D - Root Cause):** After deploying a new fallback for the pricing service (fallback: return last-cached price with 30-minute TTL), the team receives complaints that some users see "wrong prices" at checkout. Investigation reveals: the pricing service was never actually down. What is the likely root cause?
_Hint:_ Pricing service was never down — so the fallback should not have activated. Possible causes: (1) Circuit breaker is too sensitive — opening on very few failures (e.g., `failureRateThreshold=10%` with minimum calls=5 → 1 failure triggers circuit open). The circuit opens spuriously → fallback activates → users see cached (stale) prices → incorrect at checkout. Fix: tune circuit breaker (higher failure threshold, longer slow call duration threshold). (2) Fallback is registered for exceptions that aren't dependency failures — e.g., `IllegalArgumentException` (application bug) triggers fallback, returning stale price instead of surfacing the bug. Fix: only register `SocketTimeoutException`, `ConnectException`, `CallNotPermittedException` — not generic `Exception` or `RuntimeException`. (3) The pricing service IS occasionally returning errors (transient), circuit opens, fallback serves stale prices. Hidden partial failure. Fix: dashboard for fallback activation rate — investigate root cause.
