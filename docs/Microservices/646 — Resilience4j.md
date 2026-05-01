---
layout: default
title: "Resilience4j"
parent: "Microservices"
nav_order: 646
permalink: /microservices/resilience4j/
number: "646"
category: Microservices
difficulty: ★★★
depends_on: "Inter-Service Communication, Circuit Breaker (Microservices)"
used_by: "Circuit Breaker (Microservices), Retry Strategy, Bulkhead Pattern, Rate Limiting (Microservices)"
tags: #advanced, #microservices, #reliability, #java, #spring
---

# 646 — Resilience4j

`#advanced` `#microservices` `#reliability` `#java` `#spring`

⚡ TL;DR — **Resilience4j** is a lightweight, functional-style Java resilience library (Netflix Hystrix successor) providing **Circuit Breaker**, **Retry**, **Rate Limiter**, **Bulkhead**, **TimeLimiter**, and **Cache** decorators. Designed for Java 8+ functional interfaces, works natively with Spring Boot Actuator and Micrometer metrics.

| #646            | Category: Microservices                                                                          | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Inter-Service Communication, Circuit Breaker (Microservices)                                     |                 |
| **Used by:**    | Circuit Breaker (Microservices), Retry Strategy, Bulkhead Pattern, Rate Limiting (Microservices) |                 |

---

### 📘 Textbook Definition

**Resilience4j** is a lightweight, functional Java library for building resilient microservices. It was developed as a replacement for Netflix Hystrix (now in maintenance mode) and is the primary resilience library for Spring Boot applications. Resilience4j provides six core modules, each implemented as a function decorator: **CircuitBreaker** — protects calls to downstream services from cascade failures using a CLOSED/OPEN/HALF-OPEN state machine; **Retry** — retries failed calls with configurable backoff strategies; **RateLimiter** — limits the number of calls to a service per time period; **Bulkhead** — limits concurrent calls to prevent thread pool exhaustion (Semaphore-based or ThreadPoolBulkhead); **TimeLimiter** — limits execution time of async calls; **Cache** — decorates calls with caching. All modules integrate with Spring Boot 2/3 via the `resilience4j-spring-boot3` starter, expose Actuator health endpoints, and emit Micrometer metrics for monitoring. The library is designed around Java functional interfaces (`Supplier`, `Function`, `Callable`) and supports reactive programming (Reactor, RxJava).

---

### 🟢 Simple Definition (Easy)

Resilience4j is a Java toolkit for protecting your application when services it calls fail or become slow. It provides ready-made Circuit Breakers (stop calling a broken service), Retry (try again on failure), Rate Limiters (don't overwhelm a service), and Bulkheads (don't let slow calls exhaust your thread pool). Each module wraps your service call with a protective layer.

---

### 🔵 Simple Definition (Elaborated)

`OrderService` calls `PaymentService`. Without resilience: if `PaymentService` is slow, every call blocks a thread. 100 concurrent orders → 100 blocked threads → `OrderService` thread pool exhausted → `OrderService` stops responding. With Resilience4j: Circuit Breaker detects 60% failure rate → opens circuit → fast-fails new calls (no blocking). TimeLimiter ensures each call times out in 2 seconds. Bulkhead limits only 20 concurrent calls to `PaymentService`. Retry retries transient failures with exponential backoff. All metrics flow to Prometheus/Grafana automatically.

---

### 🔩 First Principles Explanation

**Circuit Breaker state machine:**

```
States:
  CLOSED: normal operation — calls pass through
    → tracks failure/slow call rate in a sliding window (count-based or time-based)
    → if failure rate ≥ failureRateThreshold → transitions to OPEN

  OPEN: circuit is open — calls are REJECTED immediately (no actual call made)
    → fast-fail with CallNotPermittedException
    → after waitDurationInOpenState → transitions to HALF-OPEN

  HALF-OPEN: testing if service recovered
    → allows permittedNumberOfCallsInHalfOpenState calls through
    → if failure rate in test calls ≥ failureRateThreshold → back to OPEN
    → if failure rate < threshold → transitions back to CLOSED

STATE MACHINE:
  CLOSED --[failure rate ≥ threshold]--> OPEN
  OPEN --[wait duration elapsed]--------> HALF-OPEN
  HALF-OPEN --[test calls succeed]------> CLOSED
  HALF-OPEN --[test calls fail]---------> OPEN

SLIDING WINDOW:
  COUNT_BASED: last N calls (e.g., last 100 calls)
  TIME_BASED: calls in last N seconds (e.g., last 60 seconds)
  → Failure rate = (failed calls) / (total calls in window)
```

**All six Resilience4j modules — configuration and behaviour:**

```java
// Application.yml configuration for all modules:
resilience4j:
  circuitbreaker:
    instances:
      payment-service:
        slidingWindowType: COUNT_BASED
        slidingWindowSize: 100              # last 100 calls
        failureRateThreshold: 60            # open if 60%+ fail
        slowCallRateThreshold: 80           # treat call as slow if >2s
        slowCallDurationThreshold: 2000ms
        waitDurationInOpenState: 30s
        permittedNumberOfCallsInHalfOpenState: 10
        minimumNumberOfCalls: 20            # don't open before 20 calls

  retry:
    instances:
      payment-service:
        maxAttempts: 3
        waitDuration: 500ms
        enableExponentialBackoff: true
        exponentialBackoffMultiplier: 2.0   # 500ms, 1000ms, 2000ms
        retryExceptions:                    # only retry these:
          - java.io.IOException
          - org.springframework.web.client.HttpServerErrorException
        ignoreExceptions:                   # never retry these:
          - com.example.ValidationException
          - org.springframework.web.client.HttpClientErrorException

  bulkhead:
    instances:
      payment-service:
        maxConcurrentCalls: 20             # max 20 concurrent calls
        maxWaitDuration: 100ms             # wait up to 100ms for a slot

  ratelimiter:
    instances:
      payment-service:
        limitForPeriod: 100               # 100 calls per period
        limitRefreshPeriod: 1s            # period = 1 second
        timeoutDuration: 500ms            # wait up to 500ms for permission

  timelimiter:
    instances:
      payment-service:
        timeoutDuration: 3s               # cancel after 3s
        cancelRunningFuture: true
```

**Combining all modules (decorator order matters):**

```java
@Service
class PaymentServiceClient {

    // Decorator order (outer to inner):
    // CircuitBreaker → Bulkhead → RateLimiter → TimeLimiter → Retry
    // Outer decorators see all failures including inner ones

    private final CircuitBreaker circuitBreaker;
    private final Bulkhead bulkhead;
    private final RateLimiter rateLimiter;
    private final TimeLimiter timeLimiter;
    private final Retry retry;

    public PaymentServiceClient(CircuitBreakerRegistry cbRegistry,
                                 BulkheadRegistry bulkheadRegistry,
                                 RateLimiterRegistry rlRegistry,
                                 TimeLimiterRegistry tlRegistry,
                                 RetryRegistry retryRegistry) {
        this.circuitBreaker = cbRegistry.circuitBreaker("payment-service");
        this.bulkhead = bulkheadRegistry.bulkhead("payment-service");
        this.rateLimiter = rlRegistry.rateLimiter("payment-service");
        this.timeLimiter = tlRegistry.timeLimiter("payment-service");
        this.retry = retryRegistry.retry("payment-service");
    }

    public PaymentResponse charge(ChargeRequest request) {
        Supplier<CompletableFuture<PaymentResponse>> asyncCall =
            () -> CompletableFuture.supplyAsync(() -> paymentHttpClient.charge(request));

        Supplier<CompletableFuture<PaymentResponse>> decorated =
            Decorators.ofSupplier(asyncCall)
                .withCircuitBreaker(circuitBreaker)
                .withBulkhead(bulkhead)
                .withRateLimiter(rateLimiter)
                .withTimeLimiter(timeLimiter, scheduledExecutor)
                .withRetry(retry, scheduledExecutor)
                .decorate();

        try {
            return decorated.get().get();
        } catch (CallNotPermittedException e) {
            return PaymentResponse.circuitOpen();  // fast-fail fallback
        } catch (BulkheadFullException e) {
            return PaymentResponse.tooManyRequests();
        }
    }
}
```

---

### ❓ Why Does This Exist (Why Before What)

Netflix built Hystrix to handle the cascade failure problem in their microservices system (hundreds of services). Hystrix used a thread-pool-per-command model (each service call runs in a dedicated thread pool). This worked but consumed many threads. Resilience4j replaced Hystrix with a more memory-efficient semaphore-based approach and Java 8 functional APIs. When Netflix deprecated Hystrix, Spring Boot adopted Resilience4j as the standard.

---

### 🧠 Mental Model / Analogy

> Resilience4j modules are like safety systems in a factory: Circuit Breaker = emergency stop switch (trips when machine breaks down, prevents further damage until inspection); Retry = automatic restart attempt (try to restart the machine 3 times before stopping); Bulkhead = flood compartments in a ship (isolate one production line failure, don't let it flood all lines); Rate Limiter = production quota (only process 100 orders per second — don't overwhelm the shipping department); TimeLimiter = workstation time-out alarm (if a task takes more than 2 minutes, abort and move to the next).

---

### ⚙️ How It Works (Mechanism)

**Spring Boot annotation-based usage:**

```java
// @CircuitBreaker, @Retry, @Bulkhead annotations (spring-aop):
@Service
class OrderService {

    @CircuitBreaker(name = "payment-service", fallbackMethod = "paymentFallback")
    @Retry(name = "payment-service")
    @Bulkhead(name = "payment-service", type = Bulkhead.Type.SEMAPHORE)
    public PaymentResponse processPayment(ChargeRequest request) {
        return paymentClient.charge(request);
    }

    // Fallback: called when circuit is OPEN or all retries exhausted:
    public PaymentResponse paymentFallback(ChargeRequest request, Exception ex) {
        log.warn("Payment service unavailable, using fallback: {}", ex.getMessage());
        return PaymentResponse.deferred(request.getOrderId());
        // Queue for retry, mark order as pending payment
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Inter-Service Communication
(synchronous HTTP/gRPC calls that can fail)
        │
        ▼
Resilience4j  ◄──── (you are here)
(resilience toolkit for Java services)
        │
        ├── Circuit Breaker → primary use case: detect + stop calling broken services
        ├── Retry Strategy → automatic retry with backoff for transient failures
        ├── Bulkhead Pattern → limit concurrent calls per downstream service
        └── Rate Limiting (Microservices) → protect downstream from overload
```

---

### 💻 Code Example

**Monitoring circuit breaker state with Actuator:**

```yaml
# application.yml: expose circuit breaker health in Actuator:
management:
  health:
    circuitbreakers:
      enabled: true
  endpoints:
    web:
      exposure:
        include: health,metrics,prometheus

# GET /actuator/health:
# {
#   "components": {
#     "circuitBreakers": {
#       "details": {
#         "payment-service": {
#           "failureRate": "65.0%",
#           "slowCallRate": "0.0%",
#           "state": "OPEN",         ← visible to ops teams
#           "bufferedCalls": 100,
#           "failedCalls": 65
#         }
#       }
#     }
#   }
# }
```

---

### ⚠️ Common Misconceptions

| Misconception                                      | Reality                                                                                                                                                                                                                                                                 |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Resilience4j replaces the need for a Service Mesh  | Resilience4j handles application-level resilience (business error handling, fallbacks). A Service Mesh handles infrastructure-level resilience (pod-level circuit breaking, mTLS, load balancing). They are complementary                                               |
| All exceptions should be in retryExceptions        | Only retry idempotent operations and transient failures (IOExceptions, 5xx). Never retry business errors (404 Not Found, 400 Bad Request, 409 Conflict) — retrying these causes duplicate processing or wasted calls                                                    |
| The Circuit Breaker fallback should always succeed | Fallbacks should be designed to degrade gracefully, not to hide failures. If a fallback also fails (e.g., it reads from a cache that is also down), the exception will propagate. Always monitor fallback invocation rates — high fallback rates indicate real problems |
| Higher minimumNumberOfCalls = better accuracy      | Low `minimumNumberOfCalls` (e.g., 5) opens the circuit too eagerly on a handful of failures. High `minimumNumberOfCalls` (e.g., 1000) means the circuit stays CLOSED through many failures before opening. Balance based on traffic volume and failure impact           |

---

### 🔥 Pitfalls in Production

**Circuit breaker opens during legitimate high-error period (e.g., deployment)**

```
SCENARIO:
  PaymentService is being deployed (rolling update).
  For 60 seconds: 30% of pods are terminating → connection refused errors.
  CircuitBreaker sees 60% failure rate → opens → ALL payment calls rejected.
  Customers cannot checkout for 30 seconds (waitDurationInOpenState).

MITIGATIONS:
  1. Graceful shutdown: PaymentService sends Readiness=DOWN before terminating
     → LoadBalancer stops routing to terminating pod
     → Fewer errors reach CircuitBreaker during deployment

  2. Deployment-aware failureRateThreshold:
     Increase threshold during known deployment windows (risky — manual)

  3. Increase minimumNumberOfCalls:
     With minimumNumberOfCalls=50, 30 errors out of 50 calls (60%) opens circuit.
     With minimumNumberOfCalls=100, need 60 failures before opening.

  4. TIME_BASED sliding window:
     Use last 60 seconds window → deployment errors diluted by earlier success

  5. Shorter waitDurationInOpenState (15s instead of 30s):
     Circuit recovers faster after deployment completes
```

---

### 🔗 Related Keywords

- `Circuit Breaker (Microservices)` — the pattern; Resilience4j is the Java implementation
- `Retry Strategy` — one of Resilience4j's six core modules
- `Bulkhead Pattern` — one of Resilience4j's six core modules
- `Rate Limiting (Microservices)` — one of Resilience4j's six core modules

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CIRCUIT      │ CLOSED→OPEN→HALF-OPEN state machine       │
│ BREAKER      │ Opens when failure/slow rate ≥ threshold  │
├──────────────┼───────────────────────────────────────────┤
│ RETRY        │ maxAttempts, exponential backoff          │
│ BULKHEAD     │ maxConcurrentCalls (semaphore)            │
│ RATE LIMITER │ limitForPeriod / limitRefreshPeriod       │
│ TIME LIMITER │ timeoutDuration for async calls           │
├──────────────┼───────────────────────────────────────────┤
│ SPRING       │ @CircuitBreaker, @Retry, @Bulkhead        │
│ ANNOTATIONS  │ fallbackMethod for graceful degradation   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Resilience4j CircuitBreaker is configured with `slidingWindowType=COUNT_BASED`, `slidingWindowSize=100`, `failureRateThreshold=50`, `minimumNumberOfCalls=20`. A new microservice has just started and receives its first 20 calls — 11 fail (55%). The circuit breaker opens. Is this the desired behaviour? What is the risk of having a low `minimumNumberOfCalls` for high-traffic services vs low-traffic services? How would you configure the circuit breaker differently for a service that receives 10,000 requests/second vs one that receives 10 requests/second?

**Q2.** Resilience4j's Retry module retries calls on exceptions. However, retrying a non-idempotent operation (e.g., `POST /api/payments`) can cause double charges. Describe the full idempotency solution: (a) the client generates an `idempotency-key` (UUID) before the first attempt; (b) the `idempotency-key` is included in every retry attempt; (c) the server stores `{idempotency-key → result}` and returns cached result on duplicate. What is the server's storage strategy — where should the idempotency key be stored (memory vs database), what TTL should it have, and what database constraints enforce uniqueness?
