---
layout: default
title: "Retry Strategy"
parent: "Microservices"
nav_order: 651
permalink: /microservices/retry-strategy/
number: "651"
category: Microservices
difficulty: ★★☆
depends_on: "Timeout Strategy, Resilience4j"
used_by: "Fallback Strategy, Circuit Breaker (Microservices)"
tags: #intermediate, #microservices, #reliability, #distributed
---

# 651 — Retry Strategy

`#intermediate` `#microservices` `#reliability` `#distributed`

⚡ TL;DR — A **Retry Strategy** automatically retries a failed call a limited number of times with a backoff delay. Best for **transient failures** (momentary network blip, service restart). Key rules: only retry **idempotent** operations; always use **exponential backoff with jitter**; stop retrying when the **circuit breaker is open**. Implemented via Resilience4j `@Retry`.

| #651            | Category: Microservices                            | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------- | :-------------- |
| **Depends on:** | Timeout Strategy, Resilience4j                     |                 |
| **Used by:**    | Fallback Strategy, Circuit Breaker (Microservices) |                 |

---

### 📘 Textbook Definition

A **Retry Strategy** is a resilience pattern that re-executes a failed operation automatically, under the assumption that the failure is transient and will not persist across repeated attempts. Retries are most effective against: temporary network disruptions (packet loss, TCP reset), service instances being briefly unavailable during rolling deployments, and transient resource contention (database connection pool momentarily exhausted). Retry is dangerous when applied to: non-idempotent operations (e.g., payment processing — retrying may cause double charges), systemic failures (e.g., database is down for 1 hour — retrying wastes resources), and 4xx errors (client errors that will not resolve with retrying). Key configuration dimensions: `maxAttempts` (total attempts including first try); `waitDuration` (delay between attempts); `backoffStrategy` — fixed, linear, or exponential; `jitter` — random variation added to prevent retry storms (thundering herd); `retryExceptions` — which exceptions to retry on; `ignoreExceptions` — which exceptions to never retry. Resilience4j's `@Retry` annotation with `@CircuitBreaker` is the standard Spring Boot combination, where retries are the inner decorator and circuit breaker is the outer (so the circuit breaker accumulates all failed attempts including retried ones).

---

### 🟢 Simple Definition (Easy)

Retry means: if a call fails, wait a moment and try again — a limited number of times. Good for "maybe the service just restarted" situations. Bad for "the service has been down for an hour" or "I just tried to charge a card and got an error." Always add a delay between retries to avoid overwhelming a struggling service.

---

### 🔵 Simple Definition (Elaborated)

`OrderService` calls `InventoryService`. During a Kubernetes rolling deployment, a new pod is starting while an old pod terminates. For 2 seconds, the load balancer occasionally routes to the terminating pod — connection refused. Without retry: order fails. With retry: first attempt fails (connection refused to terminating pod), wait 500ms, second attempt hits a healthy pod — succeeds. The transient failure is invisible to the user. Key: the retry picked a different pod (load balancer round-robins), and the 500ms delay gave the deployment time to progress.

---

### 🔩 First Principles Explanation

**Backoff strategies — why jitter is essential:**

```
FIXED DELAY (bad for distributed systems):
  attempt 1: fails → wait 1000ms
  attempt 2: fails → wait 1000ms
  attempt 3: fails → wait 1000ms

  PROBLEM (Thundering Herd):
  100 services all get a timeout at T=0 (e.g., database restart)
  All retry at T=1000ms simultaneously → 100 concurrent requests hit recovering DB
  DB gets overwhelmed → many fail again → all retry at T=2000ms together → ...
  Synchronised retries sustain the overload

EXPONENTIAL BACKOFF (better, still has synchronisation problem):
  attempt 1: fails → wait 500ms
  attempt 2: fails → wait 1000ms
  attempt 3: fails → wait 2000ms
  → reduces retry frequency over time, but still synchronised across clients

EXPONENTIAL BACKOFF + JITTER (correct):
  attempt 1: fails → wait random(250, 750)ms    ← 500ms ± 50% jitter
  attempt 2: fails → wait random(750, 1250)ms
  attempt 3: fails → wait random(1500, 2500)ms
  → different clients retry at different times → load spread over time
  → recovering service sees gradual load increase, not spike

  FULL JITTER (AWS recommendation):
  waitMs = random(0, min(capacity, baseDelay × 2^attempt))
  → truly random within exponential cap
  → better distribution but sometimes very short wait (acceptable)

  DECORRELATED JITTER:
  waitMs = random(baseDelay, prev_wait × 3)
  → wait grows but with randomness

  FOR MOST SERVICES: ExponentialBackoff ± 50% jitter is sufficient
```

**What to retry vs what NOT to retry:**

```
RETRY ON (transient failures):
  ✓ java.io.IOException (network error, connection reset)
  ✓ java.net.SocketTimeoutException (read timeout)
  ✓ HTTP 503 Service Unavailable
  ✓ HTTP 429 Too Many Requests (with Retry-After respect)
  ✓ HTTP 502 Bad Gateway (load balancer got no response)
  ✓ gRPC UNAVAILABLE, DEADLINE_EXCEEDED

DO NOT RETRY (permanent failures):
  ✗ HTTP 400 Bad Request (request is malformed — won't succeed on retry)
  ✗ HTTP 401 Unauthorized (credentials are wrong — retry won't fix)
  ✗ HTTP 403 Forbidden (no permission — retry won't fix)
  ✗ HTTP 404 Not Found (resource doesn't exist — retry won't fix)
  ✗ HTTP 409 Conflict (duplicate — retrying duplicates the conflict)
  ✗ com.example.ValidationException (business rule violation)
  ✗ CallNotPermittedException (circuit breaker open — DO NOT RETRY!)

IDEMPOTENCY REQUIREMENT:
  Only retry operations that are safe to repeat:
  SAFE: GET (read), PUT (overwrite with same data), DELETE (idempotent)
  UNSAFE by default: POST (creates new resource each time)
  SAFE if idempotency key used: POST with X-Idempotency-Key header
    → server returns same result for duplicate key → safe to retry
```

**Retry interaction with Circuit Breaker — decorator order:**

```
OUTER: CircuitBreaker
INNER: Retry

Call → CircuitBreaker check (OPEN? fast-fail) → Retry(attempt 1) → actual call
                                              → fail → Retry(attempt 2) → actual call
                                              → fail → Retry(attempt 3) → actual call
                                              → fail (maxAttempts exhausted)
                                              → CircuitBreaker records ONE FAILURE
                                              (the overall retried call counts as 1 failure)

Wait... is this right?
  YES: CircuitBreaker is outer → it sees the FINAL result of the retried call
  The 3 individual attempts inside Retry are transparent to CircuitBreaker
  → Circuit breaker failure rate based on retried-call outcomes (not individual attempts)

ALTERNATIVE ORDER (Retry outer, CircuitBreaker inner):
  → CircuitBreaker records each individual retry attempt as a failure
  → Circuit opens faster (after fewer user-visible failures)
  → BUT: if circuit opens mid-retry, Retry may retry into an OPEN circuit
  → Configure: retryExceptions does NOT include CallNotPermittedException
```

---

### ❓ Why Does This Exist (Why Before What)

Networks are inherently unreliable. TCP connections drop. Containers restart. Load balancers temporarily route to unhealthy instances. In a distributed system, a fraction of all network calls will fail for reasons completely unrelated to the caller or callee logic. Without retry: transient failures become user-visible failures. With retry: transient failures are invisible to the user. Retry is the simplest mechanism to handle the inherent unreliability of distributed systems.

---

### 🧠 Mental Model / Analogy

> Retry is like trying to call someone who might be temporarily unavailable. If you call and get no answer (network busy, person stepped away briefly), you try again after a short wait — not immediately (phone still busy), and not 100 times in a row (that would be annoying and overwhelming). You try 3 times with increasing delays. If still no answer after 3 tries, you give up and leave a voicemail (fallback). You don't call back on every ring if you're getting a "number disconnected" message (404/403 — don't retry permanent errors).

---

### ⚙️ How It Works (Mechanism)

**Resilience4j Retry — configuration and annotation:**

```java
// application.yml:
resilience4j:
  retry:
    instances:
      inventory-service:
        maxAttempts: 3
        waitDuration: 500ms
        enableExponentialBackoff: true
        exponentialBackoffMultiplier: 2.0       # 500ms, 1s, 2s
        randomizedWaitFactor: 0.5               # ±50% jitter
        retryExceptions:
          - java.io.IOException
          - java.net.SocketTimeoutException
          - org.springframework.web.client.HttpServerErrorException$ServiceUnavailable
        ignoreExceptions:
          - java.lang.IllegalArgumentException
          - com.example.ValidationException
          - io.github.resilience4j.circuitbreaker.CallNotPermittedException

// Java:
@Service
class InventoryClient {

    @Retry(name = "inventory-service", fallbackMethod = "inventoryFallback")
    @CircuitBreaker(name = "inventory-service")  // outer
    public InventoryResponse checkInventory(Long productId) {
        return httpClient.get("/api/inventory/" + productId, InventoryResponse.class);
    }

    public InventoryResponse inventoryFallback(Long productId, Exception ex) {
        log.error("Inventory check failed after retries for product {}: {}",
            productId, ex.getMessage());
        // Return optimistic "in stock" or cached value:
        return inventoryCache.getOrDefault(productId, InventoryResponse.unknown());
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Timeout Strategy
(bounds individual call duration)
        │
        ▼
Retry Strategy  ◄──── (you are here)
(retries failed calls on transient failures)
        │
        ├── Circuit Breaker → outer decorator; stops retrying when systemic failure
        ├── Fallback Strategy → called when all retry attempts exhausted
        └── Rate Limiting → Retry can amplify request rate; rate limit controls this
```

---

### 💻 Code Example

**Custom retry condition — retry on specific HTTP status codes:**

```java
@Bean
RetryRegistry retryRegistry() {
    RetryConfig config = RetryConfig.custom()
        .maxAttempts(3)
        .waitDuration(Duration.ofMillis(500))
        .intervalBiFunction(IntervalBiFunction.ofExponentialRandomBackoff(
            Duration.ofMillis(500),   // initial delay
            2.0,                      // multiplier
            0.5,                      // jitter factor (50%)
            Duration.ofSeconds(10)    // max delay
        ))
        // Retry based on HTTP response status (not just exceptions):
        .retryOnResult(response -> {
            if (response instanceof ResponseEntity<?> r) {
                return r.getStatusCode().is5xxServerError()
                    || r.getStatusCode() == HttpStatus.TOO_MANY_REQUESTS;
            }
            return false;
        })
        .retryExceptions(IOException.class, SocketTimeoutException.class)
        .ignoreExceptions(
            HttpClientErrorException.class,  // 4xx — never retry
            CallNotPermittedException.class  // circuit open — never retry
        )
        .build();

    return RetryRegistry.of(Map.of("payment-service", config));
}
```

---

### ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                                                                                                                                                                     |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Always use retry to improve reliability | Retry is only appropriate for idempotent operations and transient failures. Retrying a payment POST without an idempotency key causes double charges. Retrying database writes without idempotency causes duplicate records |
| More retries = more reliable            | Too many retries amplify load on a struggling service. 3 clients × 3 retries = 9 calls per operation. 100 clients × 3 retries = 300 calls. Excessive retries contribute to cascade failures instead of preventing them      |
| Retry and circuit breaker are redundant | Retry handles transient failures (first or second attempt succeeds). Circuit Breaker handles systemic failures (all retries fail for an extended period). They work together: retry first, circuit breaker as backstop      |

---

### 🔥 Pitfalls in Production

**Retry amplifies load during a slow service restart**

```
SCENARIO:
  PaymentService restarts (normal deployment) → 20 seconds of unavailability.
  100 clients each have @Retry(maxAttempts=5, waitDuration=1s).

  T=0-20s: each client tries 5 times (5 seconds of retrying)
  Total attempts: 100 clients × 5 attempts = 500 calls hitting a restarting service
  → PaymentService gets 500 calls during startup → slow to initialise
  → Instead of 20s restart: takes 40s because of retry overload

  With jitter and exponential backoff:
  → Retries spread: T=0, T=0.4, T=1.2, T=2.8, T=5.6s (exponential + jitter)
  → 500 calls spread over 0-6 seconds per client, randomised
  → Peak concurrent retries: much lower

  Also add: maxAttempts=3 (not 5) for 20s window
  Consider: maxAttempts × maxWait < expected restart time
  If restart takes 20s: 3 attempts × (1+2+4)s = 7s → most clients give up before restart
  → Fallback invoked → user sees degraded response → service restarts → normal
  → BETTER than retry storm delaying restart further
```

---

### 🔗 Related Keywords

- `Timeout Strategy` — timeout triggers the `IOException`/`TimeoutException` that retry catches
- `Circuit Breaker (Microservices)` — outer decorator that stops all retries when systemic failure detected
- `Fallback Strategy` — the handler when all retry attempts are exhausted
- `Resilience4j` — provides `@Retry` and `RetryRegistry` for Java implementation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ USE WHEN     │ Transient failures (network blip, restart) │
│ DON'T USE    │ Business errors (4xx), circuit OPEN        │
│ DON'T USE    │ Non-idempotent ops without idempotency key │
├──────────────┼───────────────────────────────────────────┤
│ BACKOFF      │ Exponential + jitter (prevents storm)      │
│ MAX ATTEMPTS │ 3 (not more without good reason)           │
├──────────────┼───────────────────────────────────────────┤
│ ORDER        │ @CircuitBreaker (outer) @Retry (inner)     │
│ JAVA IMPL    │ Resilience4j @Retry, waitDuration,        │
│              │ enableExponentialBackoff=true              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A payment service has `@Retry(maxAttempts=3)` without an idempotency key. A user clicks "Pay" which triggers a `POST /api/payments` to the payment gateway. The first attempt takes 3 seconds (near timeout) and succeeds, but the response is lost due to a network error between the gateway and the service. The retry sends the request again. The payment gateway processes it again — the customer is charged twice. Design the complete idempotency solution: what does the `X-Idempotency-Key` header contain, where is it generated (client? gateway?), where is it stored (Redis? DB?), and what query/check happens before processing the second request?

**Q2.** In Kubernetes, during a rolling deployment of `PaymentService`, Kubernetes terminates old pods with SIGTERM. After SIGTERM, the pod continues serving in-flight requests for `terminationGracePeriodSeconds`. However, new connections are rejected. A Retry in the caller may hit the terminating pod on attempt 1 (connection refused), then hit a healthy pod on attempt 2. Describe how load balancer endpoint removal timing interacts with this: if Kubernetes removes the pod from `Endpoints` before SIGTERM is sent, will retries always hit healthy pods? What is the actual sequence of events, and why is there still a race condition?
