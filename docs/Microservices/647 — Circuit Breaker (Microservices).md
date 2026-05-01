---
layout: default
title: "Circuit Breaker (Microservices)"
parent: "Microservices"
nav_order: 647
permalink: /microservices/circuit-breaker-microservices/
number: "647"
category: Microservices
difficulty: ★★★
depends_on: "Inter-Service Communication, Resilience4j"
used_by: "Fallback Strategy, Saga Pattern (Microservices)"
tags: #advanced, #microservices, #reliability, #distributed, #pattern
---

# 647 — Circuit Breaker (Microservices)

`#advanced` `#microservices` `#reliability` `#distributed` `#pattern`

⚡ TL;DR — The **Circuit Breaker** pattern prevents a failing downstream service from causing cascade failures. It monitors call outcomes (success/failure/slow). When the failure rate crosses a threshold, the circuit **OPENS** — further calls fast-fail immediately (no actual call made). After a wait period, it **HALF-OPENS** to test recovery. Implemented in Java via Resilience4j.

| #647            | Category: Microservices                         | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------- | :-------------- |
| **Depends on:** | Inter-Service Communication, Resilience4j       |                 |
| **Used by:**    | Fallback Strategy, Saga Pattern (Microservices) |                 |

---

### 📘 Textbook Definition

The **Circuit Breaker** pattern, named by Michael Nygard in "Release It!", is a resilience design pattern that prevents a microservice from making calls to a failing downstream service, allowing the failing service time to recover and preventing cascade failures. The pattern is modelled after an electrical circuit breaker: a CLOSED circuit (normal operation) allows current (requests) to flow; when conditions become dangerous (failure rate crosses threshold), the circuit OPENS (requests are blocked); the circuit periodically attempts to CLOSE again (HALF-OPEN state) to detect recovery. Three states: **CLOSED** — requests pass through, outcomes tracked in a sliding window; when failure rate ≥ threshold, transition to OPEN. **OPEN** — requests immediately rejected with `CallNotPermittedException`, no actual call to downstream service; after `waitDurationInOpenState`, transition to HALF-OPEN. **HALF-OPEN** — a limited number of test requests allowed through; if they succeed, transition to CLOSED; if they fail, back to OPEN. Circuit Breakers also handle **slow calls** — calls that complete successfully but take too long are treated as failures for the failure rate calculation.

---

### 🟢 Simple Definition (Easy)

A Circuit Breaker watches how often calls to a service succeed or fail. When too many calls fail, it "trips" (opens) and immediately rejects new calls without even trying — like an electrical fuse that stops current flow to protect the circuit. After a waiting period, it allows a few test calls through. If those succeed, it resets to normal operation.

---

### 🔵 Simple Definition (Elaborated)

OrderService calls PaymentService for every checkout. PaymentService has a database problem and starts failing 80% of calls. Without a Circuit Breaker: every checkout attempt blocks a thread waiting for PaymentService to time out (3 seconds each). With 100 concurrent checkouts: 100 blocked threads → OrderService is unresponsive. WITH a Circuit Breaker: after the first 60 failures (60% failure rate threshold), the circuit OPENS. Subsequent checkout calls immediately get a "payment service unavailable" response in <1ms — no thread blocking, OrderService stays responsive. After 30 seconds, the breaker HALF-OPENS, tries 10 test calls, sees PaymentService recovered, CLOSES. Normal operation resumes.

---

### 🔩 First Principles Explanation

**Why cascade failures happen and how Circuit Breaker stops them:**

```
SCENARIO: Chain of synchronous calls A → B → C → D
  D has a database issue → D responds in 10 seconds instead of 100ms
  C calls D → C's thread blocks for 10 seconds
  B calls C → B's thread blocks for 10+ seconds
  A calls B → A's thread blocks for 10+ seconds

  A's thread pool: 200 threads
  50 requests/second × 10 seconds = 500 blocked threads needed
  → After 4 seconds: thread pool exhausted
  → New A requests rejected → A appears "down"
  → D caused A to fail — cascade failure

  Without circuit breaker: D's 10s latency kills ALL services in the chain
  With circuit breaker in A→B:
    - First N calls to B slow → circuit OPENS
    - Subsequent A calls to B: IMMEDIATE fast-fail (1ms)
    - A's threads NOT blocked → A stays responsive
    - A returns degraded response (fallback) → user sees partial results, not timeout

CIRCUIT BREAKER PLACEMENT:
  Each service wraps its downstream calls with a circuit breaker:
  A has CB for B | B has CB for C | C has CB for D
  → Any link failure is isolated — doesn't propagate up the chain
```

**Sliding window and failure detection:**

```
COUNT_BASED WINDOW (slidingWindowSize=10):
  Calls: [✓, ✓, ✗, ✗, ✗, ✗, ✓, ✗, ✗, ✗]
  Failures: 7/10 = 70%
  failureRateThreshold=60%: 70% > 60% → OPEN

TIME_BASED WINDOW (slidingWindowSize=60, i.e., last 60 seconds):
  Track all calls in last 60 seconds
  If failure rate ≥ threshold in that window → OPEN
  Benefits: naturally handles traffic spikes
    (10 failures in 60s with 100 total calls = 10% — stays closed)
    (10 failures in 60s with 11 total calls = 91% — opens!)

SLOW CALL DETECTION:
  slowCallDurationThreshold: 2000ms
  slowCallRateThreshold: 80%
  → Calls completing in >2 seconds counted as "slow"
  → If 80%+ of calls are slow → circuit opens
  → Prevents blocking threads even when HTTP 200 is eventually returned
  → Critical: slow calls are as dangerous as failed calls (both block threads)
```

**Circuit Breaker vs Timeout vs Retry — the interaction:**

```
LAYERING:
  Timeout: limit individual call duration (e.g., 3s)
  Retry: retry on transient failures (e.g., 3 attempts)
  Circuit Breaker: detect pattern of failures, stop calling

CALL LIFECYCLE WITH ALL THREE:
  Attempt 1: [call] → timeout at 3s (IOException)
  Retry: attempt 2: [call] → timeout at 3s
  Retry: attempt 3: [call] → timeout at 3s
  → Total: 9 seconds blocked, 3 failed calls recorded in circuit breaker window

  After enough retried failures → circuit OPENS:
  Next call: IMMEDIATE rejection (<1ms) — no 9-second ordeal

  KEY: Circuit Breaker operates OUTSIDE Retry.
  Each retry attempt is a separate "call" from the Circuit Breaker's perspective.
  Retrying on OPEN circuit is pointless — configure retryExceptions to not retry
  CallNotPermittedException:
    retry:
      ignoreExceptions:
        - io.github.resilience4j.circuitbreaker.CallNotPermittedException
```

---

### ❓ Why Does This Exist (Why Before What)

Microservices systems have many synchronous dependencies. When one service degrades, the standard timeout mechanism prevents calls from waiting forever, but during the timeout window, every call blocks a thread. In high-traffic systems, a single slow downstream service can exhaust thread pools of every upstream service within seconds — causing a total system outage that started from a single service problem. The Circuit Breaker pattern converts "blocking on slow service" into "fast-fail" — the system degrades gracefully instead of collapsing.

---

### 🧠 Mental Model / Analogy

> A Circuit Breaker in software mirrors an electrical circuit breaker. An electrical circuit breaker monitors current flow. When too much current flows (short circuit — dangerous), it trips (OPENS) and stops current flow completely — protecting downstream devices. An electrician inspects, fixes the issue, and resets the breaker (CLOSES). The software equivalent: when too many calls fail (overloaded/broken service — dangerous), the circuit trips (OPENS) and stops call flow — protecting thread pools. After a wait period, a few test calls are tried (HALF-OPEN). If they succeed: reset (CLOSE). Unlike an electrical breaker, the software version resets automatically.

---

### ⚙️ How It Works (Mechanism)

**Resilience4j Circuit Breaker — event listening for monitoring:**

```java
@Component
class CircuitBreakerMonitor implements ApplicationListener<CircuitBreakerOnStateTransitionEvent> {

    @Autowired CircuitBreakerRegistry registry;
    @Autowired ApplicationEventPublisher eventPublisher;

    @PostConstruct
    void registerListeners() {
        registry.circuitBreaker("payment-service")
            .getEventPublisher()
            .onStateTransition(event -> {
                CircuitBreaker.StateTransition transition = event.getStateTransition();
                log.warn("Circuit breaker '{}' transition: {} → {}",
                    "payment-service",
                    transition.getFromState(),
                    transition.getToState());

                if (transition.getToState() == CircuitBreaker.State.OPEN) {
                    // Alert on-call engineer:
                    alertingService.critical("Payment circuit breaker OPENED",
                        "payment-service failure rate exceeded threshold");
                }
            })
            .onFailureRateExceeded(event ->
                log.error("Failure rate: {}%", event.getFailureRate()))
            .onSlowCallRateExceeded(event ->
                log.warn("Slow call rate: {}%", event.getSlowCallRate()));
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Inter-Service Communication
(synchronous calls that can fail or be slow)
        │
        ▼
Circuit Breaker (Microservices)  ◄──── (you are here)
(CLOSED/OPEN/HALF-OPEN state machine)
        │
        ├── Resilience4j → Java implementation of circuit breaker pattern
        ├── Fallback Strategy → what to do when circuit is OPEN
        ├── Bulkhead Pattern → prevents thread exhaustion upstream
        └── Service Mesh → provides circuit breaking at infrastructure level (Envoy)
```

---

### 💻 Code Example

**Circuit breaker with async fallback queue:**

```java
@Service
class PaymentService {

    @CircuitBreaker(name = "payment-gateway", fallbackMethod = "queuePaymentFallback")
    public PaymentResult processPayment(PaymentRequest request) {
        return paymentGatewayClient.process(request);
    }

    // When circuit is OPEN: queue payment for async processing:
    public PaymentResult queuePaymentFallback(PaymentRequest request,
                                               CallNotPermittedException ex) {
        // Queue to retry when payment gateway recovers:
        pendingPaymentQueue.add(PendingPayment.builder()
            .orderId(request.getOrderId())
            .amount(request.getAmount())
            .createdAt(Instant.now())
            .maxRetryUntil(Instant.now().plus(Duration.ofMinutes(15)))
            .build());

        // Tell user order is received but payment pending:
        return PaymentResult.pending(
            request.getOrderId(),
            "Payment will be processed shortly"
        );
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                   | Reality                                                                                                                                                                                                                                                                                                                               |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Circuit Breaker and Retry serve the same purpose                | Retry handles transient failures in individual calls (retries the same call). Circuit Breaker handles systemic failures (detects a pattern and stops making calls entirely). Retry + Circuit Breaker are layered together                                                                                                             |
| An OPEN circuit means the downstream service is definitely down | The circuit opens when the _failure rate_ exceeds the threshold — this could be caused by a temporary deployment, network blip, or misconfigured timeout. The service may recover by the time the circuit HALF-OPENs. Self-preservation: circuit breaker protects the caller, not necessarily indicating permanent downstream failure |
| Circuit Breaker should be configured the same for all services  | Different services have different reliability requirements, traffic volumes, and acceptable degradation. A payment service circuit breaker should be more conservative (open quickly, wide fallback) than an analytics service (open slowly, retry more aggressively)                                                                 |

---

### 🔥 Pitfalls in Production

**Circuit breaker opens during scheduled maintenance → alert storm**

```
SCENARIO:
  PaymentGateway scheduled maintenance: 2 AM – 3 AM.
  Circuit breaker opens at 2:00:05 AM (5 seconds of failures).
  PagerDuty alert fires: "CRITICAL: payment circuit breaker OPENED".
  On-call engineer woken up at 2 AM for a planned maintenance window.

IMPROVEMENT:
  1. Maintenance-aware circuit breakers:
     → Subscribe to maintenance window events
     → Temporarily increase failureRateThreshold during known window
     → Or disable circuit breaker health alert during window (silence in PagerDuty)

  2. Differentiate alert severity:
     INFO: circuit opened (expected during deployments/maintenance)
     CRITICAL: circuit has been open for > X minutes (unexpected outage)

  3. Deployment-safe retry configuration:
     During rolling deployments: some pods terminate → connection refused
     → retryOnConnectionFailure in RetryConfig → retry picks different pod
     → Circuit breaker doesn't see these as failures (retried successfully)
```

---

### 🔗 Related Keywords

- `Resilience4j` — the Java library providing Circuit Breaker implementation
- `Bulkhead Pattern` — prevents thread exhaustion, complements circuit breaker
- `Fallback Strategy` — defines what happens when circuit is OPEN
- `Retry Strategy` — layered with circuit breaker for transient failure handling

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CLOSED       │ Normal. Calls pass. Outcomes tracked.     │
│ OPEN         │ Fast-fail. No actual calls. Wait period.  │
│ HALF-OPEN    │ N test calls. Success→CLOSED. Fail→OPEN.  │
├──────────────┼───────────────────────────────────────────┤
│ OPENS WHEN   │ failure rate ≥ failureRateThreshold       │
│              │ OR slow call rate ≥ slowCallRateThreshold │
├──────────────┼───────────────────────────────────────────┤
│ PROTECTS     │ Caller thread pool (prevents exhaustion)  │
│ SOLVES       │ Cascade failure in synchronous call chains│
├──────────────┼───────────────────────────────────────────┤
│ JAVA IMPL    │ Resilience4j CircuitBreaker               │
│ MESH IMPL    │ Istio outlierDetection (pod-level)        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** In a microservices system, `CheckoutService` has circuit breakers for both `InventoryService` and `PaymentService`. During a Black Friday sale, `InventoryService` is slow but operational (p99 latency: 8 seconds). The circuit breaker's `slowCallDurationThreshold=2s` opens the circuit. CheckoutService now fast-fails all inventory checks. Customers can't check out because inventory can't be validated. Design the fallback strategy: (a) what does a "graceful degradation" fallback look like for inventory checking (optimistic reservation, last-known stock, stale cache)? (b) what are the business risks of each fallback option (overselling, order cancellations)? (c) how would you communicate to customers that their order is subject to inventory confirmation?

**Q2.** The Circuit Breaker pattern has an important limitation: it is **per-instance**. If OrderService has 5 instances, each has its own circuit breaker with its own state. If 3 out of 5 instances have their circuit breaker OPEN and 2 have it CLOSED, the load balancer will preferentially route to the 2 CLOSED instances, potentially overloading them. Describe a **distributed circuit breaker** approach (using Redis or shared state) that allows all instances of a service to share circuit breaker state. What are the trade-offs of distributed circuit breakers vs per-instance circuit breakers?
