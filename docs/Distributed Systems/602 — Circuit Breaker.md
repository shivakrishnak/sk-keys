---
layout: default
title: "Circuit Breaker"
parent: "Distributed Systems"
nav_order: 602
permalink: /distributed-systems/circuit-breaker/
number: "602"
category: Distributed Systems
difficulty: ★★★
depends_on: "Heartbeat, Failure Modes"
used_by: "Resilience4j, Hystrix, Istio, Spring Cloud"
tags: #advanced, #distributed, #resilience, #fault-tolerance, #microservices
---

# 602 — Circuit Breaker

`#advanced` `#distributed` `#resilience` `#fault-tolerance` `#microservices`

⚡ TL;DR — **Circuit Breaker** is a stability pattern that wraps remote calls in a state machine (Closed → Open → Half-Open): it stops cascading failures by short-circuiting calls to a failing service, allowing it to recover before traffic resumes.

| #602            | Category: Distributed Systems              | Difficulty: ★★★ |
| :-------------- | :----------------------------------------- | :-------------- |
| **Depends on:** | Heartbeat, Failure Modes                   |                 |
| **Used by:**    | Resilience4j, Hystrix, Istio, Spring Cloud |                 |

---

### 📘 Textbook Definition

**Circuit Breaker** (Michael Nygard, "Release It!" 2007) is a fault-tolerance design pattern that wraps remote service calls in a proxy tracking the failure rate. The circuit breaker has three states: **Closed** (normal operation — calls pass through; failures increment a counter); **Open** (failure threshold exceeded — all calls immediately fail without hitting the remote service, usually returning a fallback or error after a configurable timeout window); **Half-Open** (after the sleep window expires — a limited number of test calls are sent; if successful: transition back to Closed; if failing: back to Open). This pattern prevents **cascading failures**: if Service A depends on Service B, and B is slow/failing, A's threads block waiting for B until A's thread pool is exhausted → A fails → all of A's callers fail → cascade. By opening the circuit, A's calls to B fail fast → A's threads freed → A remains responsive → cascade stopped. Implementations: Resilience4j (Java), Hystrix (Netflix, now in maintenance), Polly (.NET), Istio/Envoy service mesh (infrastructure-level circuit breaking). Metrics tracked: failure rate (%), slow call rate (%), number of calls in sliding window.

---

### 🟢 Simple Definition (Easy)

Circuit breaker = electrical circuit breaker for software. Normal: current flows (calls go through). Overload (too many failures): breaker OPENS (current stops — no more calls to failing service). Fails fast instead of waiting. After a recovery period: breaker goes HALF-OPEN (lets one test call through). If test succeeds: CLOSED again (normal traffic). If test fails: OPEN again. Prevents your service from drowning while waiting for a broken dependency.

---

### 🔵 Simple Definition (Elaborated)

Why circuit breakers prevent cascades: without CB, Service A → B (B is slow). A's thread pool: 50 threads. All 50 waiting on slow B. New request arrives: no threads → A returns 503 to its caller. A's caller (C) has same problem. Entire dependency tree fails. With CB on A→B: first 10 failures → CB opens. Next requests: immediate failure (no thread consumed). A's thread pool: 50 threads still available for healthy operations. A: degrades gracefully (returns cached data or 503) instead of complete thread exhaustion.

---

### 🔩 First Principles Explanation

**Circuit breaker state machine and sliding window mechanics:**

```
CIRCUIT BREAKER STATE MACHINE:

  States: CLOSED | OPEN | HALF_OPEN

  ┌─────────────┐    failure_rate > threshold    ┌──────────────┐
  │   CLOSED    │ ──────────────────────────────► │     OPEN     │
  │  (normal)   │                                 │ (fail fast)  │
  └─────────────┘                                 └──────────────┘
         ▲                                               │
         │ n successful calls                            │ wait_duration_in_open_state
         │                                               ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                       HALF_OPEN                             │
  │   (let permitted_number_of_calls_in_half_open_state = 5)   │
  │   through → if pass rate OK → CLOSED, else → OPEN           │
  └─────────────────────────────────────────────────────────────┘

CLOSED STATE:
  All calls pass through to remote service.
  Metrics tracked in sliding window (count-based or time-based).

  COUNT-BASED window (Resilience4j default):
    slidingWindowSize=100 (last 100 calls tracked).
    Each call: either SUCCESS or FAILURE (timeout, exception, returned error).
    failure_rate = failures / total_calls.
    slow_call_rate = slow_calls (> slowCallDurationThreshold) / total_calls.

  TIME-BASED window (alternative):
    Counts calls in last N seconds.
    More responsive to sudden spikes (count-based can be slow to detect if call rate is low).

  TRIGGER TO OPEN:
    failure_rate >= failureRateThreshold (e.g., 50%) AND calls >= minimumNumberOfCalls (e.g., 10).
    OR slow_call_rate >= slowCallRateThreshold (e.g., 90%).

    minimumNumberOfCalls: prevents opening on 1 failure out of 1 call (100% failure rate).
    Need statistical significance: require at least N calls before evaluating.

OPEN STATE:
  No calls reach remote service.
  All calls: immediately throw CallNotPermittedException (fail fast).
  Caller handles with fallback (cached response, default value, error response).

  Benefits: remote service gets breathing room to recover.
  Benefits: caller's threads freed immediately (no blocking).

  waitDurationInOpenState (sleep window): 60 seconds.
  After 60s: transition to HALF_OPEN.

HALF_OPEN STATE:
  Allows N test calls through (permittedNumberOfCallsInHalfOpenState=5).
  Additional calls: fail fast (CallNotPermittedException) while test calls are in flight.

  After N test calls complete:
    If failure rate of test calls < failureRateThreshold: → CLOSED. Full traffic resumed.
    If failure rate ≥ threshold: → OPEN again. Another waitDurationInOpenState period.

  Design: prevents thundering herd on recovery.
    Without Half-Open: when OPEN → CLOSED: all backed-up requests rush in simultaneously.
    With Half-Open: only 5 test calls → validates recovery → gradual re-enablement.

THREAD ISOLATION (HYSTRIX MODEL — BULKHEAD PATTERN):

  Hystrix added thread pool isolation alongside circuit breaking.

  Without thread pool isolation:
    All calls (to different downstream services) share one thread pool.
    B goes slow → 50/50 threads waiting on B → C also has no threads.

  With thread pool isolation (Hystrix):
    Each downstream service: separate bounded thread pool.
    Service B: 10-thread pool. B goes slow: 10 threads exhausted.
    Service C: 10 separate threads. Unaffected.

  Resilience4j: uses rate limiting + bulkhead (SemaphoreBulkhead or ThreadPoolBulkhead)
                 instead of per-dependency thread pools (lighter weight).

CIRCUIT BREAKER VS. RETRY:

  Retry: assume transient failures. Retry 3 times. Exponential backoff.
    Good for: brief blips (GC pause, brief network hiccup).
    Bad for: systemic failures (service down, cascade). 3 retries = 3× load on failing service.

  Circuit Breaker: detect systemic failure pattern. Stop calling after threshold.
    Good for: systemic failures (service down, overloaded, cascade).
    Bad for: transient single failures (CB opens on 1 failure if threshold is too low).

  COMBINATION (correct approach):
    Wrap retries inside circuit breaker:
      CB CLOSED: retry 3 times with backoff on failure.
      If 3 retries all fail: count as 1 failure for CB metrics.
      After 50 such failures (50% failure rate): CB OPENS.
      CB OPEN: no retries attempted (fail fast immediately).

  Order in Resilience4j chain:
    Retry → CircuitBreaker → RateLimiter → Bulkhead → TimeLimiter → remote call.
    (Resilience4j decorates in this order by default.)
    Retry wraps CB: if CB is open, retry immediately sees CallNotPermittedException,
    doesn't retry (short-circuits retry logic too).
    Alternatively: CB wraps retry: CB counts all retry attempts.
    Choose based on semantics.

CIRCUIT BREAKER METRICS AND MONITORING:

  Key metrics to expose (Resilience4j → Micrometer → Prometheus/Grafana):

  resilience4j_circuitbreaker_state{name="payment-service"}:
    0=CLOSED, 1=OPEN, 2=HALF_OPEN.
    Alert: state > 0 for > 60s → "Payment service circuit open."

  resilience4j_circuitbreaker_failure_rate{name="payment-service"}:
    Percentage. Alert: > 25% for > 5m → "Payment service degraded."

  resilience4j_circuitbreaker_calls_total{name, kind}:
    kind=successful|failed|not_permitted|ignored.
    not_permitted: calls rejected because CB is OPEN.
    Spike in not_permitted: CB is open → cascade stopped or cascade happening.

  Dashboard:
    Graph failure_rate over time.
    Correlate CB state transitions with upstream error rates.
    Alert on: sustained OPEN state, high not_permitted rate.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT circuit breaker:

- Service A calls failing Service B: threads block until timeout (30s by default)
- Thread pool saturation: all of A's threads wait on B → A can't serve other requests → cascade
- Recovery amplification: when B recovers → all queued requests hit simultaneously → re-crash

WITH circuit breaker:
→ Cascade prevention: OPEN circuit stops thread exhaustion in A
→ Fast failure: callers get immediate error (not 30s timeout) → better UX
→ Recovery protection: Half-Open state tests recovery gradually (no thundering herd)

---

### 🧠 Mental Model / Analogy

> The circuit breaker on a power outlet. Normal: electricity flows. Overload (short circuit → too many failures): breaker trips OPEN (electricity stops — prevents fire = cascade). Wait for appliance to cool down. Try again (half-open): plug something small in. If OK: reset breaker (closed). If sparks again: trips open immediately.

"Electricity flowing" = normal service calls passing through
"Breaker tripping open" = CB transitioning to OPEN after failure threshold
"Plugging in small appliance as test" = Half-Open test calls

---

### ⚙️ How It Works (Mechanism)

```
Resilience4j Circuit Breaker in Java:

  Every call to remote service goes through the CB proxy.
  CB proxy: records outcome → updates sliding window → checks threshold → transitions state.

  CLOSED:
    Call → remote service → record outcome → check threshold.
  OPEN:
    Call → throw CallNotPermittedException immediately.
  HALF_OPEN:
    If test slot available: call → remote service → record outcome → check threshold.
    If no test slot: throw CallNotPermittedException.
```

---

### 🔄 How It Connects (Mini-Map)

```
Heartbeat / Failure Modes (failure detection — individual call failures)
        │
        ▼
Circuit Breaker ◄──── (you are here)
(aggregate failure detection → stop cascades via state machine)
        │
        ├── Bulkhead: limits concurrent calls (thread pool isolation)
        ├── Retry with Backoff: retries individual calls (combined with CB)
        └── Fallback: what to return when CB is OPEN
```

---

### 💻 Code Example

**Resilience4j Circuit Breaker with Spring Boot:**

```java
// application.yaml:
resilience4j:
  circuitbreaker:
    instances:
      payment-service:
        slidingWindowSize: 100
        minimumNumberOfCalls: 10
        failureRateThreshold: 50          # Open if 50% of last 100 calls fail
        slowCallDurationThreshold: 3000   # Calls > 3s are "slow"
        slowCallRateThreshold: 80         # Open if 80% of calls are slow
        waitDurationInOpenState: 60s      # Stay open 60s before half-open
        permittedNumberOfCallsInHalfOpenState: 5
        automaticTransitionFromOpenToHalfOpenEnabled: true

// PaymentService.java:
@Service
public class PaymentService {

    private final CircuitBreakerRegistry registry;
    private final PaymentApiClient client;

    @CircuitBreaker(name = "payment-service", fallbackMethod = "paymentFallback")
    public PaymentResult processPayment(PaymentRequest request) {
        // This call is wrapped: if CB is OPEN → throws CallNotPermittedException → fallback.
        return client.post("/payments", request, PaymentResult.class);
    }

    // Fallback: called when CB is OPEN or when actual exception occurs.
    // Signature: same return type, same params + Throwable.
    public PaymentResult paymentFallback(PaymentRequest request, Throwable e) {
        if (e instanceof CallNotPermittedException) {
            // CB is OPEN — payment service known to be down.
            log.warn("Payment service circuit OPEN. Returning queued response.");
            return PaymentResult.queued(request.getId());
        }
        // Actual call failed:
        log.error("Payment call failed: {}", e.getMessage());
        return PaymentResult.failed(request.getId(), "Payment service temporarily unavailable.");
    }

    // Monitor CB state:
    @Scheduled(fixedRate = 10000)
    public void logCbState() {
        CircuitBreaker cb = registry.circuitBreaker("payment-service");
        log.info("Payment CB state: {}, failure_rate: {}%",
            cb.getState(), cb.getMetrics().getFailureRate());
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                              | Reality                                                                                                                                                                                                                                                                                                                                                                                         |
| -------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Circuit breaker prevents all failures                                      | CB prevents cascading failures caused by thread exhaustion waiting on slow/failing dependencies. It does NOT prevent the initial failures — it contains them. First ~10 calls (minimumNumberOfCalls) to a failing service still go through before CB opens. After CB opens: callers get fast failure (fallback), which is better than timeout but still a failure from the caller's perspective |
| Opening the circuit means the service is definitely down                   | CB opens when the failure rate exceeds a threshold — which can happen due to network hiccup, temporary overload, or transient errors. The service may recover quickly. This is why Half-Open exists: to re-test periodically. Monitoring should alert on sustained OPEN state (> 5 minutes), not on every brief OPEN event                                                                      |
| Hystrix Circuit Breaker is still the standard                              | Hystrix entered maintenance mode in 2018. Netflix stopped developing it. Resilience4j is the modern replacement: lighter weight (no thread pool overhead per dependency), supports more patterns (retry, rate limiter, bulkhead, time limiter), integrates with Micrometer. Spring Cloud 2020+ uses Resilience4j by default. New projects should use Resilience4j                               |
| Circuit breaker at the application level is sufficient with a service mesh | Service mesh (Istio/Envoy) circuit breaking operates at the network layer — it sees L4/L7 traffic patterns. Application-level CB (Resilience4j) sees semantic failures (business errors, custom exception types) that may return HTTP 200 with error body. Both layers are complementary: mesh CB handles network-level failures; app CB handles business-level failures                        |

---

### 🔥 Pitfalls in Production

**Circuit breaker too aggressive — opens on normal traffic spikes:**

```
SCENARIO: Payment service. CB: failureRateThreshold=50%, minimumNumberOfCalls=10.
  Black Friday: 10× normal traffic. Payment service: 60s of 503 errors (overloaded).
  CB: opens. All payment calls fail fast.
  Payment service: load reduces (CB protecting it). Service recovers in 30s.
  CB waitDurationInOpenState=60s. But service recovered at 30s.
  Users: see "payment unavailable" for 30s longer than necessary.

  Worse: payment service recovered at T=30s. CB half-opens at T=60s.
         5 test calls succeed. CB closes.
         All queued requests rush in → payment service re-overloads → CB opens again.
         Loop: open → half-open → open → ... . Service never stabilizes.

BAD: CB without rate limiting after recovery:
  // CB closes → all backed-up requests hit service simultaneously.
  // Service was processing 1,000 req/s normally. 10,000 backed-up requests → crush.

FIX 1: Rate limiter after CB recovery:
  // Resilience4j RateLimiter: limit calls to payment service after CB re-closes.
  resilience4j:
    ratelimiter:
      instances:
        payment-service:
          limitForPeriod: 100         # Max 100 calls per period
          limitRefreshPeriod: 1s      # Reset every 1s = 100 req/s max
          timeoutDuration: 0          # Don't queue: fail fast if rate exceeded
  // Decorator order: RateLimiter(CircuitBreaker(call))
  // After CB re-closes: RateLimiter ensures gradual ramp-up (100/s → service not re-crushed).

FIX 2: Tune minimumNumberOfCalls and slidingWindowSize:
  // minimumNumberOfCalls=10 on 10,000 req/s traffic: 10 calls = 1ms of data. Too fast.
  // Use time-based sliding window instead:
  resilience4j:
    circuitbreaker:
      instances:
        payment-service:
          slidingWindowType: TIME_BASED
          slidingWindowSize: 60       # Look at last 60 seconds of calls
          minimumNumberOfCalls: 100   # Need 100 calls before evaluating
  // More stable: uses 60s window instead of just last 10 calls.
```

---

### 🔗 Related Keywords

- `Bulkhead` — thread pool isolation: prevents one slow service from exhausting all threads
- `Retry with Backoff` — retries transient failures (compose with CB: retry inside CB)
- `Fallback` — what to return when CB is OPEN (cached data, default response, error)
- `Timeout` — prevents threads from blocking indefinitely (precondition for CB effectiveness)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ State machine: CLOSED→OPEN on failure    │
│              │ threshold. OPEN: fail fast. HALF_OPEN:   │
│              │ test recovery. Prevents cascade.         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Calling unreliable downstream services;  │
│              │ preventing thread pool exhaustion from   │
│              │ slow/failing dependencies                │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Internal in-process calls (no network);  │
│              │ idempotent reads with instant fallback   │
│              │ (just use timeout + retry instead)       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Trips the breaker before the whole      │
│              │  house catches fire."                    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Bulkhead → Retry with Backoff →          │
│              │ Fallback → Resilience4j → Istio CB       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a circuit breaker (CB) on Service A's calls to Service B. B has a 30-second deployment window every night where it restarts. During restart: B returns connection refused for ~5 seconds. Your CB: slidingWindowSize=100, minimumNumberOfCalls=10, failureRateThreshold=50%, waitDurationInOpenState=60s. Does the CB open during B's 5-second restart? If it does: how long is the total disruption (CB open + recovery)? How would you tune the CB to NOT open for a 5-second predictable restart?

**Q2.** A service mesh (Istio) has circuit breaking configured at the proxy level (Envoy sidecar). Your Java application also has Resilience4j circuit breakers. When both are configured: which one fires first for a given failed request? Can they interfere with each other? Is there a scenario where having both causes the application-level CB to never open (because Envoy's CB removes the failing traffic before app-level sees enough failures)?
