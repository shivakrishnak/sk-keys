---
id: MSV-043
title: Resilience4j
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-044, MSV-045
used_by: MSV-044, MSV-045
related: MSV-044, MSV-045, MSV-040, MSV-041, MSV-025
tags:
  - microservices
  - reliability
  - deep-dive
  - resilience
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 43
permalink: /microservices/resilience4j/
---

# MSV-043 - Resilience4j

⚡ TL;DR - Resilience4j is a lightweight, modular
fault-tolerance library for Java, designed as the
Netflix Hystrix successor. Modules: CircuitBreaker
(stop calling a failing service), RateLimiter (control
call rate), Retry (automatic retry with backoff),
Bulkhead (limit concurrent calls), TimeLimiter (timeout
wrapper). Spring Boot integration: `@CircuitBreaker`,
`@Retry`, `@Bulkhead` annotations or programmatic API.
Key differences from Hystrix: non-blocking (uses
Vavr/Project Reactor), no thread pool per command
(more efficient), actively maintained (Hystrix is
in maintenance mode).

| #043 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Circuit Breaker, Bulkhead Pattern | |
| **Used by:** | Circuit Breaker, Bulkhead Pattern | |
| **Related:** | Circuit Breaker, Bulkhead Pattern, Service Mesh, Istio, Timeout and Retry Patterns | |

---

### 🔥 The Problem This Solves

**CASCADING FAILURE:**
Order-service calls payment-service. Payment-service
is slow (database overloaded, GC pause, third-party
API latency). Order-service threads block waiting for
payment-service responses. Thread pool exhausted.
Order-service stops serving all requests - not just
payment-related ones. Checkout, order history, and
catalog all fail. The payment-service slowdown
cascaded to full order-service failure.

Resilience4j CircuitBreaker: after N failures, trips.
Subsequent calls: immediately return fallback (error/
cached data) without calling payment-service. Order-service
threads are not blocked. Non-payment features continue
working. When payment-service recovers: circuit closes,
normal traffic resumes.

---

### 📘 Textbook Definition

**Resilience4j** is a lightweight, functional
fault-tolerance library for Java 17+, designed as the
successor to Netflix Hystrix. It provides: (1) CircuitBreaker
- stops requests to a failing service after threshold.
(2) Retry - retries failed calls with configurable
backoff. (3) RateLimiter - limits the rate of requests.
(4) Bulkhead - limits concurrent requests (thread pool
or semaphore-based). (5) TimeLimiter - wraps calls
with a timeout. Designed for composability: multiple
decorators can be stacked (CircuitBreaker wrapping
Retry wrapping call). Spring Boot integration:
auto-configuration + annotation-driven (`@CircuitBreaker`,
`@Retry`, `@Bulkhead`).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Resilience4j = fault-tolerance patterns for Java:
circuit breaker, retry, bulkhead, rate limiter,
timeout - composable, annotation-driven, Spring Boot
native.

**One analogy:**
> A restaurant has 20 tables (Bulkhead: 20 concurrent
> diners). The kitchen (downstream service) sometimes
> takes too long. A table waiter waits max 30 minutes
> (TimeLimiter). If the kitchen fails 5 times in a row:
the waiter stops sending orders and tells diners
"Kitchen is temporarily unavailable, try the salad
bar" (CircuitBreaker + fallback). After 30 minutes:
the waiter tries one order (HALF-OPEN state). If it
works: kitchen opens again (CLOSED state). Meanwhile,
new diners: retried kitchen after 5 minutes (Retry
with backoff). The restaurant doesn't collapse just
because the kitchen is slow.

**One insight:**
Hystrix used a thread pool per command (ThreadPoolBulkhead).
Resilience4j uses semaphores by default (SemaphoreBulkhead)
and supports reactive streams (Project Reactor, RxJava).
This means Resilience4j works correctly in reactive
(non-blocking) applications where thread-pool-based
circuit breakers would incorrectly count reactive
threads as blocked.

---

### 🔩 First Principles Explanation

**CIRCUIT BREAKER STATE MACHINE:**

```
         failure rate >= threshold
CLOSED ---------------------------------> OPEN
  |                                         |
  | all calls pass through                  | all calls fail fast
  |                                         | (no upstream call)
  |         wait callNotPermittedWhenOpen   |
  |         Duration                        |
  |         wait (60s)                      |
  |                                    HALF_OPEN
  |                                         |
  |        permit limited calls (probe)     |
  |        success rate >= threshold        |
  | <--------------------------------------- |
  |                                         |
  |        failure rate >= threshold        |
  |       --------------------------------> OPEN (again)

CLOSED: Normal operation. All calls pass through.
        Count failures/slowness in sliding window.
        Failure rate >= 50% -> OPEN.

OPEN:   Fail fast. No calls to upstream.
        After waitDuration (e.g., 60s): -> HALF_OPEN.
        Fallback method called if configured.

HALF_OPEN: Allow N probe calls.
           Success rate >= threshold: -> CLOSED (recovered).
           Failure rate >= threshold: -> OPEN (still broken).
```

**SLIDING WINDOW:**

```
COUNT_BASED (default):
  Last N calls (e.g., 100)
  If failure rate in last 100 calls >= 50% -> OPEN
  Simple ring buffer of outcomes

TIME_BASED:
  Failures in last N seconds (e.g., 60s)
  Metric: failures per second
  Better for bursty traffic patterns

SLOWNESS COUNTING:
  Calls that exceed slowCallDurationThreshold (e.g., 2s)
  counted as failures even if they succeed
  Prevents slow-call degradation from appearing as success
```

---

### 🧪 Thought Experiment

**RETRY + CIRCUIT BREAKER INTERACTION:**

```
SCENARIO: Retry wraps CircuitBreaker
  Retry retries on any exception
  CircuitBreaker trips after 5 failures
  
  Call 1 fails -> Retry retries 3 times = 3 failures
                  CircuitBreaker: 3/5 failures
  Call 2 fails -> Retry retries 3 times = 3 failures
                  CircuitBreaker: 5/5 failures -> OPEN
  Call 3 -> CircuitBreaker OPEN -> CallNotPermittedException
  Retry: retries on this exception too (3 more)
         -> 3 more fast fails (no upstream call)
         -> unnecessary retries on open circuit
  
CORRECT ORDER: CircuitBreaker wraps Retry
  Call 1 -> CircuitBreaker CLOSED -> pass through
         -> call fails -> Retry: retry 3 times
         -> CircuitBreaker: counts 3 failures
  Circuit trips after threshold failures
  Call N -> CircuitBreaker OPEN -> fast fail
         -> DOES NOT reach Retry (no unnecessary retries)
  
RULE: CircuitBreaker is outermost decorator.
      Retry is inner. CircuitBreaker gates the retries.
      If circuit is open, no retries attempted.
```

---

### 🧠 Mental Model / Analogy

> Resilience4j is a set of quality control checkpoints
> for outbound service calls. CircuitBreaker: "is the
> destination reachable?" (stops sending if not).
> RateLimiter: "am I overwhelming the destination?"
> (slows down if yes). Retry: "try again if it failed
> transiently?" (exponential backoff). Bulkhead: "how
> many concurrent calls are running?" (caps concurrency).
> TimeLimiter: "did the call take too long?" (cancel it).
> These patterns are defense mechanisms: each prevents
> a different class of distributed system failure.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Resilience4j is a Java library that makes your service
messages (calls) to other services more resilient:
if a service is down, stop calling it and return an
error immediately instead of waiting. Automatically
try again on temporary failures. Limit how many
calls you make concurrently.

**Level 2 - How to use it (junior developer):**
Add `spring-boot-starter-resilience4j`. Configure in
`application.yml`. Use `@CircuitBreaker(name="payment",
fallbackMethod="paymentFallback")` on the method that
calls an external service. The fallback method must
have the same signature + a `Throwable` parameter.

**Level 3 - How it works (mid-level engineer):**
Resilience4j uses AOP (aspect-oriented programming)
with Spring Boot's annotation processing. `@CircuitBreaker`
generates a Spring AOP proxy around the annotated method.
Every call goes through `CircuitBreakerAspect`: checks
state, calls method, records outcome (success/failure/
slow). Sliding window: `SlidingWindowAggregation` counts
outcomes. State transitions: `CircuitBreakerStateMachine`.
Events: `CircuitBreaker.getEventPublisher()` allows
listening to state changes for alerting.

**Level 4 - Why it was designed this way (senior/staff):**
Resilience4j's design philosophy is functional decoration
vs Hystrix's command pattern. Hystrix: create a
`HystrixCommand` subclass - tight coupling, framework
ideology. Resilience4j: `CircuitBreaker.decorateSupplier(
() -> call())` - pure function wrapping. This works
naturally with lambdas, reactive streams (Mono/Flux),
and Java completableFutures. The decorators are
composable: `Decorators.ofSupplier(() -> call())
.withCircuitBreaker(cb)
.withRetry(retry)
.withBulkhead(bh)
.get()`. Order matters (outermost = first check).

**Level 5 - Mastery (distinguished engineer):**
Resilience4j vs Service Mesh circuit breaker: both
patterns serve the same purpose but at different levels.
Resilience4j: application-level, can implement smart
fallbacks (return stale cache, degraded response, queue
for later). Service Mesh (Istio outlierDetection): 
network-level, passive, no fallback logic. In production:
both are used together. Istio outlierDetection catches
network-level failures quickly (connection refused, timeout).
Resilience4j handles business-level degradation: slow
endpoints (slowCallDurationThreshold), custom fallback
strategies, retry with idempotency keys. The two are
complements, not substitutes: Istio for infrastructure
failures, Resilience4j for application-level resilience.

---

### ⚙️ How It Works (Mechanism)

**SPRING BOOT CONFIGURATION:**

```yaml
# application.yml
resilience4j:
  circuitbreaker:
    instances:
      payment-service:
        slidingWindowType: COUNT_BASED
        slidingWindowSize: 100
        failureRateThreshold: 50       # 50% failure -> OPEN
        slowCallDurationThreshold: 2s  # > 2s = slow call
        slowCallRateThreshold: 80      # 80% slow -> OPEN
        waitDurationInOpenState: 60s   # wait before HALF_OPEN
        permittedNumberOfCallsInHalfOpenState: 10
        minimumNumberOfCalls: 20       # Min calls before evaluating
  retry:
    instances:
      payment-service:
        maxAttempts: 3
        waitDuration: 500ms
        enableExponentialBackoff: true
        exponentialBackoffMultiplier: 2  # 500ms, 1s, 2s
        retryExceptions:
          - java.io.IOException
          - java.util.concurrent.TimeoutException
        ignoreExceptions:
          - com.example.BusinessException  # Don't retry
  bulkhead:
    instances:
      payment-service:
        maxConcurrentCalls: 20     # Max concurrent calls
        maxWaitDuration: 100ms     # Wait before rejecting
  timelimiter:
    instances:
      payment-service:
        timeoutDuration: 3s
```

**PROGRAMMATIC API (decorator composition):**

```java
@Service
public class PaymentService {

    private final CircuitBreakerRegistry cbRegistry;
    private final RetryRegistry retryRegistry;
    private final BulkheadRegistry bulkheadRegistry;

    public PaymentResult processPayment(PaymentRequest req) {
        CircuitBreaker cb = cbRegistry.circuitBreaker(
            "payment-service");
        Retry retry = retryRegistry.retry("payment-service");
        Bulkhead bulkhead = bulkheadRegistry.bulkhead(
            "payment-service");

        // Compose: CB outer, Bulkhead middle, Retry inner
        Supplier<PaymentResult> supplier = Decorators
            .ofSupplier(() -> callPaymentApi(req))
            .withCircuitBreaker(cb)  // outermost
            .withBulkhead(bulkhead)
            .withRetry(retry)        // innermost
            .withFallback(
                Arrays.asList(
                    CallNotPermittedException.class,
                    BulkheadFullException.class),
                ex -> getCachedOrDefaultResult(req)
            )
            .decorate();

        return supplier.get();
    }

    private PaymentResult getCachedOrDefaultResult(
            PaymentRequest req) {
        // Fallback: return pending status; retry async
        log.warn("Payment service unavailable; queuing");
        asyncQueue.enqueue(req);
        return PaymentResult.pending(req.getOrderId());
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
SYSTEM: Order-service calls Payment-service
PATTERN: CircuitBreaker + Retry + Bulkhead + TimeLimiter

NORMAL OPERATION:
  Circuit: CLOSED
  Bulkhead: 3/20 concurrent calls active
  Call: payment API -> 200 OK in 300ms
  Outcome: SUCCESS recorded in sliding window

DEGRADATION START (payment DB overloaded):
  Calls: start returning 503 or timing out
  Retry: retries 3 times with backoff (500ms, 1s, 2s)
         exhausts retries -> CallException thrown
  CircuitBreaker: records failures
  After 50 failures in window: failure rate = 50%
  CircuitBreaker: OPEN

CIRCUIT OPEN (60 seconds):
  All calls: CallNotPermittedException immediately
  Fallback: return PaymentResult.pending(orderId)
            + enqueue for async retry
  Order-service: continues serving (non-payment features)
  Thread pool: NOT exhausted (no blocked threads)

HALF-OPEN PROBE (after 60s):
  10 probe calls allowed
  Payment-service: recovered
  9/10 succeed: success rate 90% >= threshold
  CircuitBreaker: CLOSED (recovered)
  Normal operation resumes

METRICS TO MONITOR:
  resilience4j.circuitbreaker.state (0=CLOSED, 1=OPEN)
  resilience4j.circuitbreaker.failure.rate
  resilience4j.retry.calls (success/error/retry count)
  resilience4j.bulkhead.available.concurrent.calls
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: no fallback**

```java
// BAD: No circuit breaker, no fallback
@Service
public class OrderService {
    public Order checkout(CartId cartId) {
        // If payment-service is down:
        // - thread blocks for 30s (TCP timeout)
        // - thread pool exhausted
        // - ALL checkout attempts block
        // - checkout, catalog, order history all fail
        PaymentResult payment = paymentClient.charge(
            cartId, amount);
        return Order.from(payment);
    }
}
```

```java
// GOOD: Circuit breaker + meaningful fallback
@Service
public class OrderService {

    @CircuitBreaker(
        name = "payment-service",
        fallbackMethod = "paymentFallback"
    )
    @TimeLimiter(name = "payment-service")
    @Bulkhead(name = "payment-service")
    public CompletableFuture<PaymentResult> checkout(
            CartId cartId, BigDecimal amount) {
        return CompletableFuture.supplyAsync(() ->
            paymentClient.charge(cartId, amount));
    }

    // Fallback: called when CB is OPEN or call fails
    public CompletableFuture<PaymentResult> paymentFallback(
            CartId cartId, BigDecimal amount, Throwable t) {
        log.warn("Payment service unavailable: {}",
            t.getMessage());
        // Enqueue for retry; return pending status
        paymentQueue.enqueue(new PendingPayment(cartId, amount));
        return CompletableFuture.completedFuture(
            PaymentResult.pending(cartId));
    }
}
```

---

### ⚖️ Comparison Table

| Pattern | Problem Solved | Resilience4j Component |
|---|---|---|
| Circuit Breaker | Stop calling a failing service | `CircuitBreaker` |
| Retry | Handle transient failures | `Retry` with backoff |
| Bulkhead | Limit concurrency, prevent saturation | `Bulkhead` |
| Timeout | Don't wait forever | `TimeLimiter` |
| Rate Limiter | Don't overwhelm downstream | `RateLimiter` |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Retry and CircuitBreaker are interchangeable | Retry handles transient failures (retry 3 times, success on 3rd). CircuitBreaker handles sustained failures (service down: stop retrying for 60s to prevent cascade). Both needed: Retry for transient, CircuitBreaker for sustained. Order: CB outer, Retry inner. |
| Circuit breaker should trip immediately on 1 failure | MinimumNumberOfCalls (default: 100) must be reached before rate is calculated. This prevents premature tripping on startup or low traffic. In low-traffic services: reduce minimumNumberOfCalls to match realistic traffic volumes, otherwise the circuit never trips even with 100% failure rate. |
| Fallback should always retry the same operation | Fallback should degrade gracefully, not retry. Retry is handled by the Retry decorator before the CircuitBreaker trips. Fallback = what to return when all else fails: cached data, default response, async queue for later. Retrying in the fallback bypasses the circuit breaker protection. |

---

### 🚨 Failure Modes & Diagnosis

**Circuit breaker never trips despite 100% failures**

**Symptom:**
Payment-service is returning 500 errors for 5 minutes.
Order-service logs show repeated 500 errors. Thread
pool is exhausted. But Prometheus shows
`resilience4j_circuitbreaker_state = 0` (CLOSED).
Circuit breaker is not tripping.

**Root Cause:**
`minimumNumberOfCalls: 100` (default). Traffic is low:
only 5 calls per minute. After 5 minutes: only 25
calls made. Circuit evaluates failure rate only after
100 calls. 25 < 100 -> rate not evaluated -> never trips.

**Diagnostic:**
```bash
# Check current circuit breaker state
curl http://order-service:8080/actuator/circuitbreakers
# Look for: bufferedCalls, failedCalls, failureRate, state
# bufferedCalls: 25 - only 25 calls made
# minimumNumberOfCalls: 100 - need 100 before evaluation

# Prometheus query
resilience4j_circuitbreaker_buffered_calls_total{kind="failed"}
# vs
resilience4j_circuitbreaker_buffered_calls_total{kind="successful"}
```

**Fix:**
Set `minimumNumberOfCalls` to match expected traffic
volume for the evaluation window:
```yaml
resilience4j:
  circuitbreaker:
    instances:
      payment-service:
        minimumNumberOfCalls: 5  # Low traffic service
        slidingWindowSize: 10    # Evaluate last 10 calls
        failureRateThreshold: 50
```

---

### 🔗 Related Keywords

**Patterns implemented by Resilience4j:**
- `Circuit Breaker` - the core pattern; Resilience4j
  is the Java implementation
- `Bulkhead Pattern` - semaphore and thread pool
  bulkhead; implemented by Resilience4j Bulkhead module

**Related infrastructure:**
- `Service Mesh` - Istio implements circuit breaking
  at network level; Resilience4j at application level
- `Istio` - complementary: Istio for network failures,
  Resilience4j for business-level resilience
- `Timeout and Retry Patterns` - implemented by
  Resilience4j TimeLimiter and Retry modules

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ MODULES      │ CircuitBreaker, Retry, Bulkhead,         │
│              │ RateLimiter, TimeLimiter                 │
├──────────────┼───────────────────────────────────────────┤
│ ORDER        │ CB outer -> Bulkhead -> Retry inner       │
├──────────────┼───────────────────────────────────────────┤
│ CB STATES    │ CLOSED (normal) -> OPEN (fail-fast)      │
│              │ -> HALF_OPEN (probe) -> CLOSED/OPEN      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Hystrix successor: non-blocking fault    │
│              │  tolerance with CB, retry, bulkhead"     │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. CircuitBreaker states: CLOSED (normal) -> OPEN
   (fail-fast after threshold) -> HALF_OPEN (probe)
   -> CLOSED or OPEN again.
2. Decorator order matters: CircuitBreaker OUTER,
   Retry INNER. CB gates retries - when CB is OPEN,
   no retries attempted.
3. Tune `minimumNumberOfCalls` to your traffic volume;
default (100) is too high for low-traffic services.

**Interview one-liner:**
"Resilience4j is the Hystrix successor for Java: provides
CircuitBreaker (CLOSED/OPEN/HALF_OPEN state machine,
fail-fast when upstream is down), Retry (exponential
backoff for transient failures), Bulkhead (semaphore
concurrency limit), and TimeLimiter (timeout wrapper).
Decorator order: CircuitBreaker outermost -> Bulkhead
-> Retry innermost. Spring Boot: `@CircuitBreaker` with
`fallbackMethod`. Complements Istio: Istio for network
failures, Resilience4j for application-level resilience
with smart fallbacks."

---

### 💡 The Surprising Truth

The most commonly misconfigured Resilience4j parameter:
`retryExceptions` vs `ignoreExceptions`. By default,
Resilience4j retries ALL exceptions. This means:
a `400 Bad Request` (malformed request: your bug)
will be retried 3 times. The downstream gets 3 invalid
requests. The user waits 500ms + 1s + 2s = 3.5 extra
seconds for a retry that will always fail. Fix: always
configure `ignoreExceptions` to include validation
errors (`ValidationException`, `IllegalArgumentException`,
`HttpClientErrorException` for 4xx responses). Only
retry on transient failures: `IOException`, `TimeoutException`,
`HttpServerErrorException` (5xx). The principle:
retry what MIGHT succeed on retry; never retry what
CAN'T succeed (invariant errors).

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **CONFIGURE** Write a complete `application.yml`
   configuration for a circuit breaker: window size,
   failure threshold, slow call threshold, wait duration,
   minimum calls.
2. **COMPOSE** Write Java code composing CircuitBreaker
   + Retry + Bulkhead decorators in the correct order
   with a fallback method.
3. **DEBUG** Given `state=CLOSED` despite 100% failures:
   identify the cause (minimumNumberOfCalls not reached)
   and fix it.
4. **RETRY** Configure Retry to NOT retry `4xx` responses
   but retry `5xx` and `IOException`. Write the
   `retryExceptions`/`ignoreExceptions` config.
5. **MONITOR** Set up Actuator + Prometheus metrics
   for CircuitBreaker. Write a Grafana alert for:
   `resilience4j_circuitbreaker_state > 0` (circuit
   is not CLOSED).

---

### 🧠 Think About This Before We Continue

**Q1.** Your order-service has Resilience4j configured
with failureRateThreshold=50%, slidingWindowSize=100,
minimumNumberOfCalls=100. The payment-service starts
returning 503s at 10pm. Traffic is 2 req/min. How
long before the circuit trips? What is the problem
with this configuration for a low-traffic service,
and how do you fix it?

**Q2.** You have CircuitBreaker + Retry configured:
CB threshold 50%, Retry 3 attempts. The downstream
fails 60% of the time transiently (succeeds on retry).
Calculate: how many calls actually reach the downstream
per user request? What happens after many such requests?
Should Retry be inside or outside CircuitBreaker?

**Q3.** Your company has both Istio (outlierDetection)
and Resilience4j (CircuitBreaker) on all services.
A colleague says: "It's redundant - remove one."
Make the case for keeping both. What does each handle
that the other doesn't?