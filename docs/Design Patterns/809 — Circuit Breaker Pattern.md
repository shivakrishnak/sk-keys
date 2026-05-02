---
layout: default
title: "Circuit Breaker Pattern"
parent: "Design Patterns"
nav_order: 809
permalink: /design-patterns/circuit-breaker-pattern/
number: "809"
category: Design Patterns
difficulty: ★★★
depends_on: "Bulkhead Pattern, Microservices, Resilience4j, Distributed Systems"
used_by: "Microservices resilience, API gateway, service mesh, fault tolerance"
tags: #advanced, #design-patterns, #resilience, #microservices, #fault-tolerance, #distributed-systems
---

# 809 — Circuit Breaker Pattern

`#advanced` `#design-patterns` `#resilience` `#microservices` `#fault-tolerance` `#distributed-systems`

⚡ TL;DR — **Circuit Breaker** monitors calls to a downstream service and automatically "opens" (stops calls) when failures exceed a threshold — protecting the caller from slow/failed dependencies and giving the downstream time to recover.

| #809            | Category: Design Patterns                                            | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Bulkhead Pattern, Microservices, Resilience4j, Distributed Systems   |                 |
| **Used by:**    | Microservices resilience, API gateway, service mesh, fault tolerance |                 |

---

### 📘 Textbook Definition

**Circuit Breaker Pattern** (Michael Nygard, "Release It!", 2007; named after electrical circuit breakers): a resilience pattern for distributed systems that wraps a function call to a remote service and monitors for failures. When failures exceed a configured threshold within a time window, the circuit "opens" — subsequent calls immediately return a failure (or fallback) without attempting the remote call. After a configurable wait period, the circuit transitions to "half-open": allows a limited number of test calls through. If test calls succeed, the circuit "closes" (normal operation resumes). If test calls fail, the circuit returns to "open." Three states: CLOSED (normal), OPEN (fast-fail), HALF-OPEN (testing recovery).

---

### 🟢 Simple Definition (Easy)

A light switch with memory: if you flip it on 5 times and get a shock each time, the switch says "I'll stop letting you flip me for 30 seconds — you're clearly going to keep getting shocked." After 30 seconds: "I'll let you try once. If it works: I'm back to normal. If not: another 30 seconds." Circuit Breaker: stop hammering a failing service; give it time to recover; test recovery before resuming full traffic.

---

### 🔵 Simple Definition (Elaborated)

Inventory service is down (returning 500s). Order service calls it on every request. Each call: 30-second timeout. 100 requests/second × 30-second timeout = 3,000 threads waiting. Application collapses. Circuit Breaker on inventory calls: after 5 failures in a 10-second window → OPEN. All subsequent inventory calls: immediately return "inventory unavailable" (no network call, no 30-second wait). After 60 seconds: HALF-OPEN — 3 test calls. Inventory recovered: CLOSE, normal operation. Not recovered: back to OPEN for another 60 seconds. Application serves partial functionality instead of collapsing.

---

### 🔩 First Principles Explanation

**Circuit Breaker state machine and production configuration:**

```
STATE MACHINE:

  CLOSED (normal operation):
  ├── Calls pass through to downstream
  ├── Failures recorded in sliding window
  └── Failure rate > threshold → transition to OPEN

  OPEN (fast-fail):
  ├── All calls immediately rejected (CallNotPermittedException)
  ├── Fallback invoked (if configured)
  ├── Wait duration timer starts
  └── Wait duration expires → transition to HALF-OPEN

  HALF-OPEN (testing recovery):
  ├── Limited calls permitted (permittedNumberOfCallsInHalfOpenState)
  ├── If all test calls succeed → transition to CLOSED
  └── If any test call fails → transition to OPEN

SLIDING WINDOW TYPES:

  COUNT_BASED:
  Last N calls recorded. If failure rate in last N > threshold: open.
  Example: last 10 calls, 50% failure threshold → open if 5+ fail.

  TIME_BASED:
  All calls in last N seconds recorded. If failure rate > threshold: open.
  Example: last 60 seconds, 50% failure threshold → open if >50% fail.

  TIME_BASED is more appropriate for latency-sensitive services.
  COUNT_BASED is simpler and predictable for low-traffic services.

RESILIENCE4J CIRCUIT BREAKER CONFIGURATION:

  resilience4j:
    circuitbreaker:
      instances:
        inventoryService:
          # Sliding window:
          slidingWindowType: COUNT_BASED
          slidingWindowSize: 10          # last 10 calls

          # Thresholds:
          failureRateThreshold: 50       # open if 50%+ calls fail
          slowCallRateThreshold: 80      # open if 80%+ calls are slow
          slowCallDurationThreshold: 2s  # "slow" = > 2 seconds

          # Recovery:
          waitDurationInOpenState: 30s   # wait 30s before HALF-OPEN
          permittedNumberOfCallsInHalfOpenState: 5   # test with 5 calls

          # Minimum calls before evaluating:
          minimumNumberOfCalls: 5        # don't open on first failure

          # Which exceptions count as failures:
          recordExceptions:
            - java.io.IOException
            - java.util.concurrent.TimeoutException
          ignoreExceptions:
            - com.app.exceptions.BusinessValidationException  # not an infra failure

WHAT COUNTS AS FAILURE:

  ✓ Remote call throws exception (IOException, TimeoutException)
  ✓ Remote call takes longer than slowCallDurationThreshold
  ✗ Business validation exception (not a downstream failure)
  ✗ User not found (not a downstream failure — downstream responded correctly)

  Configure recordExceptions and ignoreExceptions precisely.
  Misconfiguration: business exceptions incorrectly opening the circuit.

METRICS TO MONITOR:

  resilience4j_circuitbreaker_state        (0=CLOSED, 1=OPEN, 2=HALF_OPEN)
  resilience4j_circuitbreaker_calls_total  (by kind: successful, failed, not_permitted)
  resilience4j_circuitbreaker_failure_rate
  resilience4j_circuitbreaker_slow_call_rate

  Alert on: circuit breaker state = OPEN for > N minutes
  Alert on: failure rate > 30% (early warning before circuit opens)
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Circuit Breaker:

- Callers keep hammering a failing service → threads fill up waiting → cascading failure
- One downstream service failure cascades to total application failure

WITH Circuit Breaker:
→ Fast-fail on known-bad downstream. Threads freed immediately. Application degrades gracefully. Downstream gets breathing room to recover. Automatic recovery when downstream comes back.

---

### 🧠 Mental Model / Analogy

> An electrical circuit breaker in a house: when a power surge or short circuit occurs, the breaker trips (OPEN) — cutting power to that circuit. The house still has power on other circuits. After you fix the underlying problem, you flip the breaker back (HALF-OPEN: the breaker resets). If the problem is still there: the breaker trips again immediately (back to OPEN). The circuit breaker protects the wiring from fire — and the rest of the house from the bad circuit's fault.

"Breaker trips (OPEN) on power surge" = circuit breaker opens when downstream failure rate exceeds threshold
"House still has power on other circuits" = other downstream services unaffected (Bulkhead + Circuit Breaker)
"Fix the problem, flip breaker back (HALF-OPEN)" = wait duration expires, test calls permitted
- "Breaker trips again if problem persists" = test calls fail in HALF-OPEN → back to OPEN
"Protects wiring from fire" = protects thread pool from exhaustion; prevents cascading failure

---

### ⚙️ How It Works (Mechanism)

```
CIRCUIT BREAKER TIMING DIAGRAM:

  Time →

  Normal traffic:    [OK][OK][OK][OK][OK][OK][OK]
  Downstream fails:  [OK][OK][FAIL][FAIL][FAIL][FAIL][FAIL]
                                   ↑ 5 failures in 10-call window
                                   → OPEN

  Open state:        [REJECT][REJECT][REJECT]  ← fast-fail, no network calls
  (30-second wait)

  Half-open:         [OK][OK][OK][OK][OK]     ← 5 test calls, all succeed
                                              → CLOSE

  Normal resumed:    [OK][OK][OK][OK][OK]

COMBINED WITH FALLBACK:

  @CircuitBreaker(name = "inventory", fallbackMethod = "inventoryFallback")
  public InventoryStatus checkInventory(Long productId) {
      return inventoryService.check(productId);
  }

  // Called in BOTH: OPEN state AND when exception occurs in CLOSED state
  public InventoryStatus inventoryFallback(Long productId, Exception ex) {
      if (ex instanceof CallNotPermittedException) {
          // Circuit is open — known degradation
          return InventoryStatus.UNKNOWN;
      }
      // Actual downstream failure
      log.warn("Inventory check failed for product {}: {}", productId, ex.getMessage());
      return InventoryStatus.ASSUME_AVAILABLE;   // optimistic fallback
  }
```

---

### 🔄 How It Connects (Mini-Map)

```
Failing downstream service → threads blocked → cascading failure
        │
        ▼
Circuit Breaker Pattern ◄──── (you are here)
(CLOSED → OPEN on failures; OPEN → HALF-OPEN after wait; HALF-OPEN → CLOSED on recovery)
        │
        ├── Bulkhead Pattern: pair with Circuit Breaker — limit concurrency AND stop bad calls
        ├── Retry Pattern: retry within a CLOSED circuit (not while OPEN)
        ├── Resilience4j: Spring Boot library implementing the state machine
        └── Service Mesh (Istio): circuit breaker at network proxy level (no code changes)
```

---

### 💻 Code Example

```java
// Circuit Breaker with event listeners for observability:

@Configuration
public class CircuitBreakerConfig {

    @Bean
    public RegistryEventConsumer<CircuitBreaker> circuitBreakerEventConsumer(
            MeterRegistry registry, ApplicationEventPublisher events) {
        return new RegistryEventConsumer<>() {
            @Override
            public void onEntryAddedEvent(EntryAddedEvent<CircuitBreaker> event) {
                CircuitBreaker cb = event.getAddedEntry();

                // State transition events (for alerting):
                cb.getEventPublisher()
                    .onStateTransition(e -> {
                        log.warn("Circuit breaker '{}' transitioned: {} → {}",
                                 cb.getName(),
                                 e.getStateTransition().getFromState(),
                                 e.getStateTransition().getToState());

                        // Alert when circuit opens:
                        if (e.getStateTransition().getToState() == CircuitBreaker.State.OPEN) {
                            alertingService.sendAlert(
                                "Circuit breaker OPEN: " + cb.getName());
                        }
                    });
            }
        };
    }
}

@Service @RequiredArgsConstructor @Slf4j
public class InventoryFacade {
    private final ExternalInventoryService inventoryService;

    @CircuitBreaker(name = "inventoryService", fallbackMethod = "fallback")
    @TimeLimiter(name = "inventoryService")   // 2s timeout
    @Retry(name = "inventoryService")         // 2 retries before circuit records failure
    public CompletableFuture<InventoryStatus> checkStock(Long productId) {
        return CompletableFuture.supplyAsync(() -> inventoryService.getStock(productId));
    }

    // Fallback signature must match (+ Exception param):
    public CompletableFuture<InventoryStatus> fallback(Long productId, Exception ex) {
        log.warn("Inventory fallback for product {}: {}", productId, ex.getClass().getSimpleName());
        // Optimistic assumption: assume in-stock; order confirmation may fail later
        return CompletableFuture.completedFuture(InventoryStatus.ASSUMED_AVAILABLE);
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Circuit Breaker prevents all failures                 | Circuit Breaker prevents failure amplification (cascading). It does not prevent the underlying failure. When the circuit is OPEN, the downstream is still failing — the circuit breaker just stops your callers from waiting for failures. The underlying issue must be fixed independently; Circuit Breaker gives the system breathing room while repairs happen.                                                         |
| Circuit Breaker replaces timeouts                     | Both are needed. Without a timeout: a slow response never triggers the circuit breaker's failure detection (it's waiting, not failing). Timeout makes slow responses into failures that the circuit breaker can count. Without a circuit breaker: each request still waits for the timeout. Together: timeout converts slow responses to failures; circuit breaker detects the pattern and fast-fails subsequent requests. |
| Circuit Breaker in every service is always beneficial | Adding a circuit breaker adds complexity: configuration, tuning, monitoring, fallback behavior. For a simple internal service call with a fast SLA and low consequence of failure: a circuit breaker may add more complexity than benefit. Apply circuit breakers to: downstream dependencies that are slow, unreliable, or critical enough to cause cascading failure. Don't add to every method call indiscriminately.   |

---

### 🔥 Pitfalls in Production

**Circuit breaker opening on business exceptions — incorrect configuration:**

```java
// ANTI-PATTERN — business exceptions misconfigured as circuit breaker failures:

// application.yml:
resilience4j:
  circuitbreaker:
    instances:
      orderService:
        failureRateThreshold: 50
        # No recordExceptions or ignoreExceptions configured!
        # DEFAULT: ALL exceptions count as failures

// Service:
@CircuitBreaker(name = "orderService", fallbackMethod = "fallback")
public OrderResult placeOrder(OrderRequest req) {
    validateInventory(req);   // throws InsufficientInventoryException (business rule)
    validatePayment(req);     // throws PaymentDeclinedException (business rule)
    return orderRepository.save(new Order(req));
}

// PROBLEM:
// During a flash sale: 60% of orders fail with InsufficientInventoryException
// (out of stock — correct business behavior, NOT an infrastructure failure)
// Circuit breaker counts these as failures.
// After 5 business exceptions: circuit OPENS.
// ALL orders rejected, including those for in-stock items.
// Business impact: circuit opens due to expected business behavior.

// FIX — configure ignoreExceptions for business exceptions:
resilience4j:
  circuitbreaker:
    instances:
      orderService:
        failureRateThreshold: 50
        recordExceptions:
          - java.io.IOException
          - java.util.concurrent.TimeoutException
          - org.springframework.dao.DataAccessException
        ignoreExceptions:
          - com.app.exceptions.InsufficientInventoryException   # business rule
          - com.app.exceptions.PaymentDeclinedException          # business rule
          - com.app.exceptions.ValidationException               # business rule
// Now: infrastructure failures open the circuit; business exceptions pass through normally.
```

---

### 🔗 Related Keywords

- `Bulkhead Pattern` — complementary: Bulkhead limits concurrency; Circuit Breaker fast-fails bad calls
- `Retry Pattern` — pair with care: retry in CLOSED state; never retry when circuit OPEN
- `Resilience4j` — Spring Boot library: Bulkhead + Circuit Breaker + Retry + TimeLimiter
- `Service Mesh (Istio)` — circuit breaking at the network layer (no code changes required)
- `Fallback` — the response strategy when the circuit is OPEN or the call fails

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ 3-state FSM: CLOSED (normal), OPEN        │
│              │ (fast-fail), HALF-OPEN (test recovery).  │
│              │ Opens on failure threshold; auto-heals.  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Downstream service may be slow/down;     │
│              │ cascading failure risk; caller must not  │
│              │ wait 30s per request on known-bad service │
├──────────────┼───────────────────────────────────────────┤
│ CONFIG       │ failureRateThreshold; slidingWindowSize; │
│              │ waitDurationInOpenState;                  │
│              │ ignoreExceptions (business rules!)        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Electrical breaker: surge trips it OPEN. │
│              │  Flip back: HALF-OPEN. All clear: CLOSED.│
│              │  Problem persists: trips OPEN again."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Bulkhead → Retry → TimeLimiter →          │
│              │ Resilience4j → Service Mesh (Istio)       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The Circuit Breaker pattern was implemented at the library level (Hystrix, then Resilience4j) in the Netflix microservices era. Service meshes (Istio, Linkerd) implement circuit breaking at the infrastructure level — in the sidecar proxy (Envoy), not in application code. This means circuit breaking works across ALL languages without code changes. What are the tradeoffs between application-level circuit breaking (Resilience4j) and infrastructure-level circuit breaking (Istio/Envoy)? When would you choose one over the other?

**Q2.** The Circuit Breaker's HALF-OPEN state is designed for "cautious recovery": allow a small number of test calls, then decide. But if the downstream service recovers under low load (HALF-OPEN test traffic) but fails under full load (CLOSED normal traffic), the circuit will close and then immediately re-open under full traffic — creating a "flapping" circuit. How do progressive traffic-shaping (gradual restore) and circuit breaker configuration (larger half-open test window, slower full-open confirmation) mitigate circuit breaker flapping in practice?
