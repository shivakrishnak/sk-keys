---
layout: default
title: "Resilience4j"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 31
permalink: /microservices/resilience4j/
id: MSV-031
category: Microservices
difficulty: ★★★
depends_on: Circuit Breaker, Java Language, Spring Core
used_by: Circuit Breaker, Bulkhead Pattern, Rate Limiting
related: Hystrix, Circuit Breaker, Bulkhead Pattern
tags:
  - microservices
  - java
  - distributed
  - deep-dive
  - pattern
---

# MSV-031 - Resilience4j

⚡ TL;DR - Resilience4j is a lightweight, modular Java resilience library providing Circuit Breaker, Retry, Rate Limiter, Bulkhead, and TimeLimiter patterns for fault-tolerant microservice calls.

| #646 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Circuit Breaker, Java Language, Spring Core | |
| **Used by:** | Circuit Breaker, Bulkhead Pattern, Rate Limiting | |
| **Related:** | Hystrix, Circuit Breaker, Bulkhead Pattern | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A Spring Boot microservice calls 5 downstream services. One service (inventory) starts responding slowly - 4-second timeouts. The calling service's HTTP client blocks a thread for 4 seconds per call. Under 500 concurrent users, all threads wait on inventory. The service runs out of threads. Other calls - to payment service (which is fast) - also start failing because there are no threads left to process them. One slow service has cascaded a failure to the entire application.

**THE BREAKING POINT:**
Netflix open-sourced Hystrix as their resilience library. By 2018, Hystrix entered maintenance mode and was no longer updated for Java 8+. Teams needed a modern, lightweight, non-blocking alternative. Resilience4j was that replacement.

**THE INVENTION MOMENT:**
This is exactly why Resilience4j was created - a functional, modular Java library that provides all the resilience patterns (circuit breaker, retry, bulkhead, rate limiting, timeout) as composable decorators, built for modern Java (8+) with no required framework dependencies.

---

### 📘 Textbook Definition

**Resilience4j** is an open-source fault tolerance library designed for Java 8+. It is inspired by Netflix Hystrix but is fully functional (uses Java 8 lambdas and functional interfaces), lightweight (no external library dependencies beyond SLF4J and Vavr), and modular (use only the modules you need). Its core modules are: `CircuitBreaker`, `Retry`, `RateLimiter`, `Bulkhead`, `TimeLimiter`, and `Cache`. Each module wraps a function call (lambda) with resilience behaviour and emits metrics via the Micrometer framework.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Resilience4j wraps service calls with safety nets - circuit breakers, retries, and rate limiters - as a pure Java library.

**One analogy:**
> Resilience4j is a set of rubber bumpers for your microservice calls. The circuit breaker bumper stops you from repeatedly slamming into a broken wall (crashed service). The retry bumper gives you a few more polite bounces before giving up. The rate limiter bumper keeps you from going too fast. Each bumper is independent - attach only the ones you need.

**One insight:**
Resilience4j's design philosophy is composition over configuration: each pattern wraps a function. You can stack patterns (circuit breaker around retry around rate limiter) using standard Java `Function.compose()`. This makes it testable in complete isolation from any framework.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Each resilience module wraps a single function call - it does not require subclassing or annotation processing.
2. Modules are composable - any number of patterns can be stacked in any order.
3. Metrics are emitted as events - consuming services can react to state changes (circuit opened, retry attempted).

**DERIVED DESIGN:**
Resilience4j uses the decorator pattern: a `CircuitBreaker` decorates a `Supplier<T>`, wrapping its execution with circuit state checking. A `Retry` decorates the already-decorated supplier. The result is a composed `Supplier<T>` that applies all policies transparently.

**Core modules:**

| Module | Protects Against | Mechanism |
|---|---|---|
| CircuitBreaker | Cascading failure from failing services | State machine: CLOSED → OPEN → HALF-OPEN |
| Retry | Transient failures (network hiccup) | Re-execute N times with backoff |
| RateLimiter | Overwhelming downstream or being overwhelmed | Token bucket / semaphore |
| Bulkhead | Thread pool exhaustion | Semaphore or thread-pool isolation |
| TimeLimiter | Indefinitely blocking calls | ScheduledExecutorService timeout |

**THE TRADE-OFFS:**
**Gain:** Fine-grained per-call resilience, testable without framework, JVM-native metrics with Micrometer, composable patterns.
**Cost:** Application code must explicitly decorate calls (vs service mesh which is transparent), Java-only (polyglot services need separate solutions).

---

### 🧪 Thought Experiment

**SETUP:**
Order service calls inventory service. Inventory starts returning errors.

**WITHOUT RESILIENCE4J:**
10 consecutive errors. Order service continues calling inventory on every request. Each call waits 2 seconds timeout. Order latency spikes to 2+ seconds for all users. Thread pool fills. Order service fails completely.

**WITH RESILIENCE4J (CircuitBreaker + Retry):**
- First 10 calls: fail, retry once each (max 2 attempts per call)
- CircuitBreaker threshold: open after 50% failure rate in last 10 calls
- Call 11: CircuitBreaker is OPEN → immediately returns `CallNotPermittedException` → order service returns fallback (cached inventory data or "inventory unknown")
- No threads blocked on inventory
- After 30 seconds: HALF-OPEN → 5 probe calls → if successful: CLOSED again
- Order service continues at normal latency for all other calls

**THE INSIGHT:**
The circuit breaker eliminates the latency tail - instead of waiting 2s for each failed call, callers get an immediate rejection (<1ms) until the downstream recovers. This protects all other service operations from the single failing dependency.

---

### 🧠 Mental Model / Analogy

> Resilience4j is a layered protective shield for an API call. From outside in: Rate Limiter (gate - only N requests through per second) → Circuit Breaker (fuse - cuts power if too many failures) → Retry (spring - bounces back a few times before giving up) → TimeLimiter (egg timer - kills the call if it takes too long) → the actual call (the things being protected).

- "Gate (Rate Limiter)" → RateLimiter module
- "Fuse (Circuit Breaker)" → CircuitBreaker module
- "Spring (Retry)" → Retry module
- "Egg timer (TimeLimiter)" → TimeLimiter module

Where this analogy breaks down: in the analogy, layers are rigid and independent. Resilience4j layers are composable in any order - the order matters for semantics: Retry inside CircuitBreaker means each retry attempt counts as a circuit breaker failure; Retry outside means a full retry chain counts as one CB attempt.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Resilience4j adds safety features to service calls: stop calling a broken service automatically, retry once after a failure, and limit how fast you call another service. All via Java code.

**Level 2 - How to use it (junior developer):**
Add `resilience4j-spring-boot3` dependency. Configure in `application.yml` with `resilience4j.circuitbreaker` settings. Annotate your method with `@CircuitBreaker(name = "inventoryService", fallbackMethod = "inventoryFallback")`. Define `inventoryFallback(Exception e)` to return a safe default.

**Level 3 - How it works (mid-level engineer):**
The `@CircuitBreaker` annotation uses Spring AOP to intercept the method call. The actual CircuitBreaker state machine tracks call results in a `SlidingWindow` (either count-based or time-based). Count-based: last N calls tracked as ring buffer. Failure rate = failures / total in window. When failure rate > threshold → OPEN. OPEN state: all calls rejected with `CallNotPermittedException`. After `waitDurationInOpenState` → HALF-OPEN: allows `permittedNumberOfCallsInHalfOpenState` probe calls. If probe success rate ≥ threshold → CLOSED. For Retry: after each failure, waits `waitDuration` (with optional exponential backoff) before re-executing. Retries respect `retryExceptions` list (which exceptions qualify for retry vs which are non-retryable).

**Level 4 - Why it was designed this way (senior/staff):**
Hystrix used a thread-pool-per-dependency model for isolation - each dependency had its own thread pool. Resilience4j chose semaphore-based bulkhead as default because thread-pool-per-dependency doesn't work well with reactive programming (WebFlux/Reactor). A semaphore blocking a reactive flow blocks the event loop thread, which is worse than blocking a dedicated thread. Resilience4j's default semaphore bulkhead uses a concurrent counter - the call is rejected immediately when the limit is reached, not queued. This matches reactive semantics: fast fail rather than queue and delay.

---

### ⚙️ How It Works (Mechanism)

**CircuitBreaker state machine:**

```
┌─────────────────────────────────────────────────┐
│         CircuitBreaker State Machine            │
│                                                 │
│  ┌────────┐  failure rate > threshold           │
│  │ CLOSED │─────────────────────────────────►   │
│  │(normal)│                                     │
│  └────────┘                                     │
│      ▲               ┌──────┐                  │
│      │  all probes  │ OPEN │  waitDuration     │
│      │  succeed      │      │  expires          │
│                      └──────┘                  │
│              ┌───────────────────────┐          │
│              │    HALF-OPEN          │          │
│              │ (N probe calls)       │          │
│              │ success → CLOSED      │          │
│              │ failure → OPEN again  │          │
│              └───────────────────────┘          │
└─────────────────────────────────────────────────┘
```

**application.yml configuration:**

```yaml
resilience4j:
  circuitbreaker:
    instances:
      inventoryService:
        sliding-window-type: COUNT_BASED
        sliding-window-size: 10      # track last 10 calls
        failure-rate-threshold: 50   # open at 50% failures
        wait-duration-in-open-state: 30s
        permitted-number-of-calls-in-half-open-state: 5
        register-health-indicator: true

  retry:
    instances:
      inventoryService:
        max-attempts: 3
        wait-duration: 500ms
        exponential-backoff-multiplier: 2
        retry-exceptions:
          - java.net.ConnectException
          - java.util.concurrent.TimeoutException
        ignore-exceptions:
          - com.example.NotFoundException

  timelimiter:
    instances:
      inventoryService:
        timeout-duration: 2s
        cancel-running-future: true
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (CLOSED state):**
Order Service → TimeLimiter starts timer → RateLimiter checks quota → CircuitBreaker checks state (CLOSED) ← YOU ARE HERE → Actual HTTP call to Inventory → Response within timeout → CB records success → Response returned

**OPEN STATE FLOW:**
Order Service → CircuitBreaker checks state (OPEN) ← YOU ARE HERE → `CallNotPermittedException` thrown immediately (<1ms) → Fallback method called → Cached/default inventory returned → Thread freed instantly

**WHAT CHANGES AT SCALE:**
At 10,000 req/s, a circuit breaker blocking calls during the OPEN state eliminates the latency spike that would otherwise propagate. The rejection itself must be fast: Resilience4j's semaphore-based check is an atomic counter comparison - nanoseconds. At extreme scale, the Micrometer metrics emission (counter increments per call) adds ~0.1ms per call - use sampling if needed.

---

### 💻 Code Example

**Example 1 - Spring Boot annotation-based:**

```java
@Service
public class OrderService {

    @CircuitBreaker(
        name = "inventoryService",
        fallbackMethod = "inventoryFallback"
    )
    @Retry(name = "inventoryService")
    @TimeLimiter(name = "inventoryService")
    public CompletableFuture<StockStatus> checkStock(String sku) {
        return CompletableFuture.supplyAsync(
            () -> inventoryClient.getStock(sku)
        );
    }

    // Fallback must have same return type + Exception param
    public CompletableFuture<StockStatus> inventoryFallback(
            String sku, Exception e) {
        log.warn("Inventory unavailable for {}: {}", sku, e.getMessage());
        return CompletableFuture.completedFuture(
            StockStatus.unknown(sku) // safe default
        );
    }
}
```

**Example 2 - Programmatic API (no Spring, testable):**

```java
CircuitBreakerConfig config = CircuitBreakerConfig.custom()
    .failureRateThreshold(50)
    .waitDurationInOpenState(Duration.ofSeconds(30))
    .slidingWindowSize(10)
    .build();

CircuitBreakerRegistry registry =
    CircuitBreakerRegistry.of(config);

CircuitBreaker cb = registry.circuitBreaker("inventory");

// Decorate the call
Supplier<StockStatus> decoratedSupplier = CircuitBreaker
    .decorateSupplier(cb, () -> inventoryClient.getStock(sku));

// Add retry on top of circuit breaker
Retry retry = Retry.ofDefaults("inventory");
Supplier<StockStatus> withRetry =
    Retry.decorateSupplier(retry, decoratedSupplier);

// Execute with fallback
StockStatus status = Try.ofSupplier(withRetry)
    .recover(CallNotPermittedException.class,
        e -> StockStatus.unknown(sku))
    .get();
```

**Example 3 - Monitor CircuitBreaker events:**

```java
circuitBreaker.getEventPublisher()
    .onStateTransition(event ->
        log.info("CB '{}' state: {} → {}",
            event.getCircuitBreakerName(),
            event.getStateTransition().getFromState(),
            event.getStateTransition().getToState()
        )
    )
    .onCallNotPermitted(event ->
        metrics.counter("cb.rejected").increment()
    );
```

**Example 4 - Testing without the real service:**

```java
@Test
void circuitBreakerOpensAfterFailures() {
    CircuitBreaker cb = CircuitBreaker.ofDefaults("test");
    AtomicInteger callCount = new AtomicInteger();

    Supplier<String> failingSupplier = () -> {
        callCount.incrementAndGet();
        throw new RuntimeException("service down");
    };
    Supplier<String> decorated =
        CircuitBreaker.decorateSupplier(cb, failingSupplier);

    // Make 10 failing calls - pure unit test, no mocks
    IntStream.range(0, 10).forEach(i -> {
        try { decorated.get(); }
        catch (Exception ignored) {}
    });

    assertThat(cb.getState()).isEqualTo(State.OPEN);
    // 11th call rejected without calling failing service
    assertThrows(CallNotPermittedException.class,
        () -> decorated.get());
    assertThat(callCount.get()).isEqualTo(10); // not 11
}
```

---

### ⚖️ Comparison Table

| Library | Language | Paradigm | Overhead | Best For |
|---|---|---|---|---|
| **Resilience4j** | Java 8+ | Functional | Low | Modern Spring Boot services |
| Hystrix | Java 7+ | Thread-pool | High | Legacy Spring services (deprecated) |
| Envoy (CB feature) | Language-agnostic | Proxy | Medium | Polyglot, service mesh environments |
| Polly | .NET | Functional | Low | .NET microservices |
| Failsafe | Java 8+ | Functional | Low | Alternative to Resilience4j |

How to choose: use Resilience4j for new JVM microservices; use Istio/Envoy circuit breaking for polyglot environments or when you want zero application code changes.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| CircuitBreaker prevents all downstream call failures | CB prevents cascading failure by fast-rejecting calls when the downstream is known-bad. It does not prevent initial failures - the window of failures must occur first |
| Higher retry count always improves reliability | More retries amplify load on an already-struggling service. Use exponential backoff and jitter to prevent retry storms |
| Resilience4j handles distributed circuit breaker state | By default, each JVM instance has its own CB state. If you have 5 instances, each instance has its own CB - a service can be OPEN in one instance and CLOSED in another |
| TimeLimiter and timeout in RestTemplate are the same | TimeLimiter wraps the CompletableFuture execution; HTTP client timeout controls the socket read timeout. Both should be set, with TimeLimiter slightly higher than HTTP timeout |

---

### 🚨 Failure Modes & Diagnosis

**1. CircuitBreaker Never Opens - Wrong Exception Type**

**Symptom:** Downstream service is clearly failing (500 errors for 60 seconds) but circuit breaker stays CLOSED. Calls continue with full latency.

**Root Cause:** The exception thrown by the HTTP client is not on the `recordExceptions` list. Feign wraps exceptions in `FeignException` - not `IOException` - and the CB only records `IOException`.

**Diagnostic:**
```bash
# Check actual exception type in logs
grep "Exception\|Error" application.log | grep inventory | \
  tail -20
# Then verify CB config
grep "record-exceptions" application.yml
```

**Fix:**
```yaml
resilience4j:
  circuitbreaker:
    instances:
      inventoryService:
        record-exceptions:
          - feign.FeignException  # match actual exception type
          - java.net.ConnectException
          - java.util.concurrent.TimeoutException
```

**Prevention:** Test the circuit breaker configuration with actual failure scenarios in integration tests - don't assume the exception type.

**2. Retry Storm - Retries Amplify Load**

**Symptom:** Inventory service is degraded at 500ms response. Retry config is `maxAttempts=3, waitDuration=100ms`. Under 1000 req/s, inventory receives 3000 req/s (3× amplification) which causes it to fully fail.

**Root Cause:** Retry without backoff or jitter multiplies the load on the struggling downstream.

**Diagnostic:**
```bash
# Check retry count metrics
curl http://api/actuator/metrics/resilience4j.retry.calls \
  | python3 -m json.tool | grep "count"
# Also check inventory logs: request rate spike = retry storm
```

**Fix:**
```yaml
resilience4j:
  retry:
    instances:
      inventoryService:
        max-attempts: 2          # fewer retries
        wait-duration: 500ms     # longer wait
        exponential-backoff-multiplier: 2
        randomized-wait-factor: 0.5  # jitter prevents thundering herd
```

**Prevention:** Always use exponential backoff with jitter for retries. Limit `max-attempts` to 2-3 for synchronous service calls.

**3. Distributed CB State - Open on One Instance, Closed on Another**

**Symptom:** Some requests succeed and some fail for the same downstream service. Error rate is approximately 1/N where N = service instance count.

**Root Cause:** Resilience4j's default CB state is per-JVM-instance. Instance A has opened its CB (inventory failed for its requests), Instance B's CB is still CLOSED (happened to get different requests).

**Diagnostic:**
```bash
# Check CB state per instance
for INSTANCE in $(kubectl get pods -l app=order-service \
  -o name -n production); do
  echo "$INSTANCE:"
  kubectl exec $INSTANCE \
    -- curl -s http://localhost:8080/actuator/circuitbreakers \
    | python3 -m json.tool | grep state
done
```

**Fix options:** (1) Use Redis-backed distributed CB state (custom implementation), (2) Accept per-instance state as acceptable (usually fine - each instance protects itself), (3) Use Envoy/Istio service mesh CB (shared state via xDS).

**Prevention:** Design for per-instance CB state as the expected behaviour. Fallbacks must work regardless of CB state.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Circuit Breaker (Microservices)` - the pattern that Resilience4j implements; understand the concept before the library
- `Java Language` - Resilience4j uses Java 8 functional interfaces (Supplier, Function, Consumer) heavily
- `Spring Core` - Spring Boot auto-configuration makes Resilience4j declarative via annotations

**Builds On This (learn these next):**
- `Bulkhead Pattern` - Resilience4j includes both Semaphore and ThreadPool Bulkhead implementations
- `Rate Limiting (Microservices)` - Resilience4j's RateLimiter module implements token-bucket rate limiting
- `Distributed Logging` - CB state transitions and retry events should be observable via Micrometer metrics

**Alternatives / Comparisons:**
- `Hystrix` - Netflix's predecessor; deprecated since 2018; Resilience4j is the direct successor
- `Envoy Proxy` - language-agnostic circuit breaking at the proxy layer; complementary to Resilience4j for cross-language platforms

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Java library providing composable         │
│              │ resilience patterns: CB, Retry, Bulkhead, │
│              │ RateLimiter, TimeLimiter                  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ One slow service cascades to take down    │
│ SOLVES       │ all services that depend on it            │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Stack patterns in the right order: CB     │
│              │ outside Retry (each retry attempt counts  │
│              │ as a separate CB call) vs Retry inside CB │
│              │ (entire retry chain = one CB attempt)     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ JVM services need per-call resilience with │
│              │ application-level metrics and fallbacks   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Polyglot platform - use service mesh CB   │
│              │ (Envoy/Istio) for language-agnostic CB    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Fine-grained app-level control vs code    │
│              │ instrumentation required in each service  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Wrap every risky call in a safety net - │
│              │  and compose your nets."                  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Circuit Breaker → Bulkhead → Retry        │
│              │ Strategy                                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your order service uses Resilience4j CircuitBreaker for calls to the inventory service. The CB is configured: `slidingWindowSize=10, failureRateThreshold=50%`. Under normal load (100 req/s), this works perfectly. However, during a 2-minute traffic spike to 1000 req/s, the inventory service handles the load fine (0% failure) but the CB opens anyway. Explain the statistical reason why a 10-call sliding window can produce false positives at high throughput, and design a CB configuration that remains stable under varying traffic volumes.

**Q2.** Your architecture has both Resilience4j circuit breakers (application layer) and Istio OutlierDetection (mesh layer) protecting the same service-to-service calls. During an incident, the application layer CB opens (Resilience4j) but the mesh layer CB has not yet opened (Istio). Your fallback returns stale cache. Meanwhile, calls from a different service that has no Resilience4j CB still reach inventory - and the mesh layer should protect those. Describe the exact interaction between application-layer and mesh-layer circuit breakers, including which layer fires first, how they interact, and whether running both on the same call path is beneficial or harmful.

