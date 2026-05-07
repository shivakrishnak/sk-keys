---
layout: default
title: "Spring Cloud Circuit Breaker"
parent: "Spring Core"
nav_order: 10
permalink: /spring/spring-cloud-circuit-breaker/
number: "SPR-010"
category: Spring Core
difficulty: ★★★
depends_on: Circuit Breaker Pattern, Spring Cloud Overview, Resilience4j
used_by: Spring Cloud Gateway, Microservices
related: Resilience4j, Hystrix (deprecated), Bulkhead Pattern
tags:
  - java
  - spring
  - microservices
  - reliability
  - advanced
---

# SPR-010 — Spring Cloud Circuit Breaker

⚡ TL;DR — Spring Cloud Circuit Breaker wraps inter-service calls with a state machine that stops cascading failures by fast-failing when downstream services degrade.

| Field | Value |
|---|---|
| **Depends on** | Circuit Breaker Pattern, Spring Cloud Overview, Resilience4j |
| **Used by** | Spring Cloud Gateway, Microservices |
| **Related** | Resilience4j, Hystrix (deprecated), Bulkhead Pattern |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** `order-service` calls `inventory-service`. `inventory-service` slows to 10 s response time due to a database issue. `order-service` opens 200 concurrent connections waiting for responses. Its thread pool exhausts. It starts timing out too. `checkout-service` calls `order-service` — same story. Within 90 seconds, a single slow database query has cascaded into a full-platform outage across 12 services.

**THE BREAKING POINT:** Microservices amplify failure through network calls. A 1% error rate in a dependency, called by 50 services, becomes a 50% degradation at the platform level if callers blindly retry or block on slow responses. Services need a way to *detect* downstream failure and *stop* sending traffic — automatically, without human intervention.

**THE INVENTION MOMENT:** Michael Nygard described the Circuit Breaker pattern in *Release It!* (2007) as an analogy to household electrical circuits: when load exceeds safe levels, the breaker opens to prevent damage. Netflix's Hystrix (2012) was the first widely adopted implementation. When Hystrix entered maintenance mode in 2018, the Spring Cloud team built the **Spring Cloud Circuit Breaker** abstraction — a thin facade over Resilience4j, Sentinel, or Spring Retry — so teams could swap implementations without changing business code.

---

### 📘 Textbook Definition

**Spring Cloud Circuit Breaker** is a resilience abstraction in Spring Cloud Commons that wraps calls to external services with a fault-tolerance state machine. It monitors call outcomes (success, failure, slow call, timeout), transitions between CLOSED, OPEN, and HALF-OPEN states based on configurable thresholds, and invokes a **fallback** function when the circuit is OPEN. The primary implementation backend is **Resilience4j**. The API is provider-agnostic via the `CircuitBreakerFactory` and `ReactiveCircuitBreakerFactory` interfaces.

---

### ⏱️ Understand It in 30 Seconds

**One line:** A state machine around every remote call that stops hitting a failing service and returns a safe fallback instead.

> "A circuit breaker is the fuse box of microservices: when a circuit overloads (too many errors), the fuse blows to protect the whole house, then resets itself after a cooling-off period."

**One insight:** The HALF-OPEN state is the critical innovation — it allows the circuit to *probe* recovery with a small traffic sample rather than forcing a human to manually reset it. This makes recovery automatic and gradual.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A failing service takes time to recover; continued calls during recovery worsen the situation.
2. Fast failure (return fallback immediately) is better than slow failure (wait for timeout).
3. Any protection mechanism must self-heal — manual resets do not scale across hundreds of services.
4. The circuit must observe real traffic outcomes, not just synthetic pings, to make accurate decisions.

**DERIVED DESIGN:**
- **CLOSED state:** calls pass through; successes and failures are counted in a sliding window.
- **OPEN state:** calls are rejected immediately; fallback executes without touching the downstream service.
- **HALF-OPEN state:** a configurable number of probe calls pass through; outcomes determine whether to close or re-open.
- Window types: **count-based** (last N calls) or **time-based** (last N seconds).

**THE TRADE-OFFS:**

**Gain:** Cascade prevention; fast-fail reduces latency under failure; allows downstream recovery time; provides fallback UX instead of hard errors.

**Cost:** Adds configuration complexity (thresholds must be tuned); risk of "flapping" (circuit opens and closes repeatedly on borderline failure rates); fallbacks must be carefully designed to provide correct degraded behaviour.

---

### 🧪 Thought Experiment

**SETUP:** `payment-service` is returning 503 for 60% of requests due to an upstream bank API outage. Your `checkout-service` calls `payment-service` on every checkout attempt.

**WHAT HAPPENS WITHOUT A CIRCUIT BREAKER:** Every checkout attempt waits the full timeout (5 s) before failing. 60% of checkouts fail after 5 s. Thread pool fills with waiting threads. New checkout requests queue behind them. Customers see a spinning wheel for 5 s then an error. `checkout-service` CPU spikes from threads waiting on I/O.

**WHAT HAPPENS WITH A CIRCUIT BREAKER:** After the failure rate exceeds 50% over a sliding window of 20 calls, the circuit OPENS. Subsequent calls skip `payment-service` entirely and immediately return the fallback: "Payment temporarily unavailable — your order is saved, we'll retry." Customers get an instant degraded experience instead of a 5 s timeout. `checkout-service` threads are free. When the bank API recovers, the circuit enters HALF-OPEN, probes with 5 calls, confirms success, and CLOSES — automatically.

**THE INSIGHT:** The circuit breaker converts "unbounded failure amplification" into "bounded, fast-failing degraded service." The fallback is the key design challenge — you must decide what "degraded but correct" means for your domain.

---

### 🧠 Mental Model / Analogy

> "A circuit breaker is an immune system white blood cell: it patrols the blood (monitors call outcomes), detects infection (rising error rate), quarantines the affected area (opens the circuit), and sends probe cells to test recovery (HALF-OPEN) before declaring the area clean again."

- **White blood cell = CircuitBreaker bean** — monitors and responds to failure signals.
- **Bloodstream = inter-service call path** — normal traffic flows freely when healthy.
- **Infection detection threshold = failureRateThreshold** — how much failure triggers isolation.
- **Quarantine = OPEN state** — infected calls blocked; fallback activated.
- **Probe cells = HALF-OPEN permitted calls** — small number test if recovery is real.
- **Re-opening blood vessel = CLOSED state** — normal traffic resumes after confirmed recovery.

Where this analogy breaks down: the immune system has memory and builds antibodies; a circuit breaker has no memory of past failure patterns — it resets to CLOSED state cleanly each time.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Imagine your app calls a payment API. If the payment API starts failing, instead of your app also failing, the circuit breaker steps in and returns a polite "sorry, try later" message immediately — without even calling the payment API. It tries again later to see if it's recovered. This protects your app.

**Level 2 — How to use it (junior developer):**
Add `spring-cloud-starter-circuitbreaker-resilience4j` to `pom.xml`. Inject `CircuitBreakerFactory`. Wrap your call: `cb.create("payment").run(() -> paymentClient.charge(order), throwable -> fallbackPayment())`. Configure thresholds in `application.yml` under `resilience4j.circuitbreaker.instances.payment`.

**Level 3 — How it works (mid-level engineer):**
`CircuitBreakerFactory.create("payment")` returns a Resilience4j `CircuitBreaker` (or `ReactiveCircuitBreaker` for reactive). Each circuit breaker maintains a `SlidingWindowBased` metrics accumulator. On each call outcome (success/failure/slow/timeout), metrics update. When `failureRateThreshold` is breached, state transitions to OPEN and `CallNotPermittedException` is thrown — the `run()` method catches this and invokes the fallback. After `waitDurationInOpenState` (default 60 s), the circuit transitions to HALF-OPEN, allows `permittedNumberOfCallsInHalfOpenState` (default 10) probe calls, and transitions back to CLOSED or OPEN based on probe results.

**Level 4 — Why it was designed this way (senior/staff):**
The abstraction layer (`CircuitBreakerFactory`) is intentional. Netflix's Hystrix proved that circuit breaking becomes embedded in every service; if the implementation is coupled to business code, migrating away is painful (Hystrix → Resilience4j migrations took teams months). By decoupling through `CircuitBreakerFactory`, Spring Cloud ensures the fallback logic and business code are implementation-agnostic. Resilience4j was chosen as the default over Hystrix because it is: decorator-based (no thread pool overhead), non-blocking (works with Reactor/Virtual Threads), and actively maintained. The bulkhead integration (separate `ThreadPoolBulkhead` or `SemaphoreBulkhead`) was kept orthogonal — a bulkhead limits concurrency; a circuit breaker tracks error rates. Mixing them in one concept was Hystrix's design mistake.

---

### ⚙️ How It Works (Mechanism)

```
STATE MACHINE
─────────────────────────────────────────────────
        threshold exceeded
CLOSED ─────────────────────► OPEN
  ▲                             │
  │  probe results OK           │ waitDuration
  │                             ▼
  └──────────────────── HALF-OPEN
        probe results fail → OPEN

SLIDING WINDOW (count-based, size=20)
┌────────────────────────────────────────────┐
│ Ring buffer: [✓✓✗✓✗✗✗✓✓✗✗✗✗✓✓✗✓✓✗✗] │
│ Failure count: 11 / 20 = 55%               │
│ Threshold: 50%  →  TRIP TO OPEN            │
└────────────────────────────────────────────┘

SLOW CALL TRACKING
┌────────────────────────────────────────────┐
│ slowCallDurationThreshold: 2000ms          │
│ slowCallRateThreshold: 80%                 │
│ Calls > 2000ms: 17/20 = 85% → also trips  │
└────────────────────────────────────────────┘
```

**Thread model:** Resilience4j's `CircuitBreaker` is a semaphore-based decorator — it does not create threads. The call executes on the caller's thread. This is fundamentally different from Hystrix's thread pool isolation model and is why it works with reactive pipelines without blocking.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (CLOSED):**
```
checkout-service handles checkout
  │
  ├─► CircuitBreaker("payment") state: CLOSED
  │     │
  │     ├─► call: paymentClient.charge(order)  ← YOU ARE HERE
  │     ├─► Success: metrics record ✓
  │     └─► Return PaymentResult to caller
  │
  └─► checkout completes normally
```

**FAILURE PATH (OPEN → HALF-OPEN → CLOSED):**
```
After 12/20 calls fail (60% > 50% threshold):
  │
  ├─► State: CLOSED → OPEN
  ├─► timer: waitDurationInOpenState = 30s
  │
During OPEN state:
  ├─► call: CircuitBreaker rejects immediately
  ├─► throws: CallNotPermittedException
  └─► fallback: return FallbackPaymentResult

After 30s:
  ├─► State: OPEN → HALF-OPEN
  ├─► Allow 5 probe calls through
  │     3 succeed, 2 fail → 40% failure < 50%
  └─► State: HALF-OPEN → CLOSED
```

**WHAT CHANGES AT SCALE:**
- Per-service circuit breakers with independent thresholds are critical — a shared circuit breaker would trip on behalf of an unrelated service.
- Circuit breaker events must be published to metrics (`CircuitBreakerEvent`) for observability — otherwise you're blind to state transitions.
- In high-concurrency environments, time-based sliding windows (10 s) are more stable than count-based windows under variable request rates.

---

### 💻 Code Example

**BAD — no circuit breaker; cascade failure on slow downstream:**
```java
@Service
public class CheckoutService {
    private final PaymentClient paymentClient;

    public Order checkout(Cart cart) {
        // No protection — one slow payment API
        // stalls all checkout threads
        Payment payment = paymentClient.charge(cart);
        return fulfillOrder(cart, payment);
    }
}
```

**GOOD — circuit breaker with fallback and Resilience4j config:**
```java
// Reactive circuit breaker wrapping WebClient
@Service
public class CheckoutService {
    private final ReactiveCircuitBreakerFactory cbFactory;
    private final WebClient.Builder webClientBuilder;

    public Mono<Order> checkout(Cart cart) {
        ReactiveCircuitBreaker cb =
            cbFactory.create("payment-service");

        Mono<Payment> paymentCall = webClientBuilder.build()
            .post()
            .uri("http://payment-service/charge")
            .bodyValue(cart)
            .retrieve()
            .bodyToMono(Payment.class);

        return cb.run(paymentCall, throwable -> {
            log.warn("Payment CB open: {}", throwable.getMessage());
            return Mono.just(Payment.pending("CB_FALLBACK"));
        }).flatMap(payment -> fulfillOrder(cart, payment));
    }
}
```
```yaml
# application.yml — Resilience4j circuit breaker config
resilience4j:
  circuitbreaker:
    instances:
      payment-service:
        sliding-window-type: COUNT_BASED
        sliding-window-size: 20
        failure-rate-threshold: 50
        slow-call-rate-threshold: 80
        slow-call-duration-threshold: 2000ms
        wait-duration-in-open-state: 30s
        permitted-number-of-calls-in-half-open-state: 5
        automatic-transition-from-open-to-half-open-enabled: true
        register-health-indicator: true
        event-consumer-buffer-size: 50
    metrics:
      enabled: true
      legacy:
        enabled: false
```
```java
// Expose circuit breaker events to Micrometer
@Bean
public Customizer<ReactiveResilience4JCircuitBreakerFactory>
        circuitBreakerCustomizer() {
    return factory -> {
        factory.configureDefault(id ->
            new Resilience4JConfigBuilder(id)
                .circuitBreakerConfig(CircuitBreakerConfig.custom()
                    .slidingWindowSize(20)
                    .failureRateThreshold(50)
                    .waitDurationInOpenState(Duration.ofSeconds(30))
                    .build())
                .timeLimiterConfig(TimeLimiterConfig.custom()
                    .timeoutDuration(Duration.ofSeconds(3))
                    .build())
                .build());
    };
}
```

---

### ⚖️ Comparison Table

| Feature | Resilience4j CB | Hystrix (deprecated) | Sentinel | Spring Retry |
|---|---|---|---|---|
| **Threading model** | Semaphore (no threads) | Thread pool per command | Semaphore/thread | Caller thread |
| **Reactive** | Yes (Reactor) | Limited | Limited | No |
| **State machine** | CLOSED/OPEN/HALF-OPEN | CLOSED/OPEN | CLOSED/OPEN | No state |
| **Slow-call detection** | Yes | No | Yes | No |
| **Bulkhead** | Semaphore + ThreadPool | ThreadPool | Semaphore | No |
| **Rate limiter** | Yes (built-in) | No | Yes | No |
| **Maintenance** | Active | Abandoned (2018) | Active (Alibaba) | Active |
| **Spring Boot autoconfiguration** | Yes | Partially | Yes | Yes |
| **Best for** | Spring/reactive apps | Legacy Netflix apps | High-traffic China | Simple retry |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Circuit breaker replaces timeouts" | They are complementary. A circuit breaker needs timeouts to detect slow calls. Without `TimeLimiter`, slow calls never register as failures — the circuit never trips. |
| "Fallback should always return cached data" | Fallback design is domain-specific. A stale cache is correct for a product catalog; it is dangerous for a payment status check where stale data could cause double-charging. |
| "Circuit breaker protects the caller" | It protects both. By stopping traffic to a struggling downstream service, the circuit breaker also protects that service from the thundering-herd of retries that would prevent its recovery. |
| "HALF-OPEN means normal operation" | HALF-OPEN is a controlled probe — only `permittedNumberOfCallsInHalfOpenState` calls pass through. All others still hit the fallback until the circuit fully CLOSES. |
| "One circuit breaker per service is enough" | Circuit breakers should be per service-endpoint pair, not per service. A slow `GET /catalog` should not trip the breaker for `POST /orders` on the same service. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1 — Circuit never trips (silent degradation)**

**Symptom:** Downstream is returning 503 at 70% rate. Thread pool is exhausted. Circuit remains CLOSED. No fallback is served.

**Root Cause:** `TimeLimiter` is not configured. The `WebClient` has no timeout. Calls to the slow service sit in-flight indefinitely — they do not register as failures in the circuit breaker's sliding window until the thread itself dies.

**Diagnostic:**
```bash
# Check if TimeLimiter is configured
curl -s http://order-service:8080/actuator/health \
  | jq '.components.circuitBreakers.details'

# Check Resilience4j event stream for failure recording
curl -s http://order-service:8080/actuator/\
circuitbreakerevents/payment-service
```

**Fix:**
```yaml
# BAD — no time limiter; slow calls never count as failures
resilience4j:
  circuitbreaker:
    instances:
      payment-service:
        failure-rate-threshold: 50

# GOOD — time limiter ensures slow calls register
resilience4j:
  timelimiter:
    instances:
      payment-service:
        timeout-duration: 2s
        cancel-running-future: true
  circuitbreaker:
    instances:
      payment-service:
        slow-call-duration-threshold: 2000ms
        slow-call-rate-threshold: 60
```

**Prevention:** Always co-configure `TimeLimiter` with `CircuitBreaker`. Treat them as a unit.

---

**Mode 2 — Circuit flapping (open/close oscillation)**

**Symptom:** Circuit breaker transitions OPEN → HALF-OPEN → OPEN every 30 s. Metrics show alternating error spikes. Downstream service appears healthy in monitoring.

**Root Cause:** `permittedNumberOfCallsInHalfOpenState` is set too low (e.g., 3). Sporadic failures in 1 out of 3 probe calls (33%) exceed the failure threshold. True failure rate is 5%, but the small sample causes a false positive.

**Diagnostic:**
```bash
# Watch state transition events in real-time
curl -s http://svc:8080/actuator/circuitbreakerevents \
  | jq '.circuitBreakerEvents[]
    | select(.type == "STATE_TRANSITION")
    | {time:.creationTime, transition:.stateTransition}'
```

**Fix:**
```yaml
# BAD — too few probe calls, high false-positive rate
resilience4j:
  circuitbreaker:
    instances:
      payment-service:
        permitted-number-of-calls-in-half-open-state: 3

# GOOD — statistically meaningful probe window
resilience4j:
  circuitbreaker:
    instances:
      payment-service:
        permitted-number-of-calls-in-half-open-state: 10
        failure-rate-threshold: 50
        # Also increase base window size
        sliding-window-size: 30
```

**Prevention:** Set probe call count to at least 10% of the sliding window size. Use time-based windows for services with variable request rates.

---

**Mode 3 — Fallback hides data corruption (silent wrong results)**

**Symptom:** No errors visible in production. Dashboards show healthy. But a batch job reveals 10,000 orders were saved with `paymentStatus=PENDING_CB_FALLBACK` — never actually charged.

**Root Cause:** The fallback for `payment-service` returns a `Payment.pending()` stub. The `checkout-service` saves the order as complete. The downstream payment was never attempted. The fallback was designed for display (show a message), but the order-save code treated it as a real payment.

**Diagnostic:**
```bash
# Query for orders with fallback payment status
# (via service's own audit endpoint)
curl -s http://order-svc:8080/admin/orders\
?paymentStatus=PENDING_CB_FALLBACK | jq '.total'
```

**Fix:**
```java
// BAD — fallback silently returns a fake payment
return cb.run(paymentCall,
    t -> Mono.just(Payment.pending("FALLBACK")));
// Order is saved as if paid — wrong!

// GOOD — fallback propagates a typed exception
return cb.run(paymentCall, t -> {
    if (t instanceof CallNotPermittedException) {
        return Mono.error(
          new PaymentServiceUnavailableException(
            "Payment circuit OPEN", t));
    }
    return Mono.error(t);
});
// Caller catches PaymentServiceUnavailableException
// and returns 503 to the user — correct degraded behaviour
```

**Prevention:** Establish a fallback contract review as part of service design. Distinguish between display fallbacks (safe to return stub) and transactional fallbacks (must propagate failure or guarantee idempotent retry).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Circuit Breaker Pattern — the underlying design pattern and state machine model
- Resilience4j — the primary implementation library behind the Spring abstraction
- Spring Cloud Overview — umbrella project context

**Builds On This (learn these next):**
- Bulkhead Pattern — complements circuit breaker by limiting concurrent calls, not just error rates
- Spring Cloud Gateway — applies circuit breaker at the API gateway layer for all inbound routes
- Observability & SRE — circuit breaker state transitions are critical SLI/SLO signals

**Alternatives / Comparisons:**
- Hystrix (deprecated) — predecessor; thread-pool isolation model; abandoned in 2018
- Resilience4j standalone — use directly when not in a Spring Cloud stack
- Sentinel — Alibaba's alternative; strong rate-limiting; better fit for high-traffic Chinese cloud environments

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════════════╗
║  WHAT IT IS      Fault-tolerance state machine   ║
║  PROBLEM         Cascading failures in services  ║
║  KEY INSIGHT     Fast-fail + fallback < timeout  ║
║  USE WHEN        Any synchronous service call    ║
║  AVOID WHEN      Internal in-process calls       ║
║  TRADE-OFF       Config complexity vs protection ║
║  ONE-LINER       "CLOSED→OPEN→HALF-OPEN→CLOSED"  ║
║  NEXT EXPLORE    Bulkhead Pattern, Resilience4j  ║
╚══════════════════════════════════════════════════╝
```

---

### 🧠 Think About This Before We Continue

1. **(D — Root Cause)** A circuit breaker for `inventory-service` is tripping repeatedly during business-hours peaks but remains CLOSED overnight. The `inventory-service` team reports no errors on their side. What are the three most likely root causes, and what specific metrics would distinguish between them?

2. **(C — Design Trade-off)** Your `checkout-service` has a circuit breaker around `payment-service`. The payment team deploys a new version with 3× higher latency but 0% error rate. The circuit breaker never trips because there are no HTTP errors. Design a monitoring and circuit-breaking strategy that would catch latency-based degradation before it cascades.

3. **(F — Comparison)** Compare the failure semantics of a circuit breaker with a retry mechanism. In what specific scenario would using *only* a retry (no circuit breaker) make a downstream service's outage recovery *slower*, and how does the circuit breaker's OPEN state solve this problem?
