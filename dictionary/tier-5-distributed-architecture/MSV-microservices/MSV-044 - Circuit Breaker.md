---
id: MSV-044
title: Circuit Breaker
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-043, MSV-025
used_by: MSV-043, MSV-045
related: MSV-043, MSV-045, MSV-025, MSV-040, MSV-041
tags:
  - microservices
  - pattern
  - deep-dive
  - resilience
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 44
permalink: /microservices/circuit-breaker/
---

# MSV-044 - Circuit Breaker

⚡ TL;DR - Circuit Breaker is a resilience pattern that
prevents cascading failures by "tripping" (opening)
when a downstream service fails repeatedly. Three
states: CLOSED (normal - all calls pass through),
OPEN (tripped - all calls fail immediately with no
downstream call), HALF-OPEN (probe - limited calls to
test if service recovered). The electrical circuit
breaker metaphor: just as a home circuit breaker
protects wiring by cutting power during a short circuit,
the software pattern protects the calling service
by cutting calls during a downstream failure.
Implementations: Resilience4j (Java), Istio outlierDetection
(network-level), AWS SDK built-in retries.

| #044 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Resilience4j, Timeout and Retry Patterns | |
| **Used by:** | Resilience4j, Bulkhead Pattern | |
| **Related:** | Resilience4j, Bulkhead Pattern, Timeout and Retry Patterns, Service Mesh, Istio | |

---

### 🔥 The Problem This Solves

**CASCADING FAILURE WITHOUT CIRCUIT BREAKER:**

```
SCENARIO: E-commerce site, Black Friday
  Order-service -> Payment-service -> Stripe API
  Stripe API: experiencing DDoS, 30s response time
  
  WITHOUT Circuit Breaker:
  Order-service: each request waits up to 30s
  Thread pool: 200 threads, all blocked on Stripe
  New requests: queue up, then timeout
  Order-service: UNAVAILABLE for ALL operations
  Including: order status, order history (no payment)
  Result: full outage because of third-party API issue
  
  WITH Circuit Breaker:
  After 10 failures: circuit trips (OPEN)
  All subsequent payment calls: fail in <1ms
  Order-service threads: free immediately
  Non-payment operations: continue working
  Graceful degradation: "Payment delayed, order placed"
  When Stripe recovers: circuit closes, payments resume
```

---

### 📘 Textbook Definition

**Circuit Breaker** (Michael Nygard, "Release It!", 2007)
is a resilience pattern that wraps calls to external
services and monitors failure rates. When the failure
rate exceeds a threshold: the circuit "trips" (opens),
and subsequent calls fail immediately without attempting
the actual call. After a timeout period: a limited
number of probe calls are allowed (HALF-OPEN state).
If probes succeed: the circuit closes and normal
operation resumes. The pattern prevents: (1) thread
pool exhaustion from blocked calls to failed services,
(2) resource waste on calls that will certainly fail,
(3) cascading failures across service dependencies.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Circuit Breaker: stop calling a broken service;
fail fast; check periodically if it recovered.

**One analogy:**
> Your home's circuit breaker. When wiring short-circuits:
circuit breaker trips (OPEN). The house still has
power everywhere else. The short circuit doesn't
burn down the wiring. After you fix the short:
reset the breaker (HALF-OPEN probe). If OK: breaker
stays on (CLOSED). If still shorted: trips again.
Software Circuit Breaker: same pattern, prevents
one failing service from short-circuiting everything
else.

**One insight:**
The Circuit Breaker pattern converts a SLOW failure
(30-second timeout blocking threads) into a FAST
failure (<1ms fail-fast). This is critical: slow
failures exhaust thread pools and propagate. Fast
failures are contained - the caller can immediately
fall back, free the thread, and serve the next request.
Speed of failure matters as much as whether you fail.

---

### 🔩 First Principles Explanation

**THE THREE STATES IN DETAIL:**

```
CLOSED STATE:
  "Normal operation"
  All calls pass through to upstream service
  Monitor: count successes and failures
  Metric: failure rate in sliding window
  Threshold: failureRateThreshold (default 50%)
  When threshold exceeded: -> OPEN
  
  Key: minimum calls must be reached before evaluating
  (prevents tripping on startup or low traffic)

OPEN STATE:
  "Fail fast"
  No calls to upstream service
  All calls: immediately throw CallNotPermittedException
  Fallback: called if configured
  Timer: waitDurationInOpenState (e.g., 60s)
  When timer expires: -> HALF_OPEN
  
  Key benefit: threads not blocked; fast failure
  Key benefit: upstream not overwhelmed during recovery

HALF_OPEN STATE:
  "Probe / recovery test"
  Allow N calls through (permittedCallsInHalfOpenState)
  Monitor these probe calls
  If success rate >= threshold: -> CLOSED (recovered)
  If failure rate >= threshold: -> OPEN (still broken)
  
  Key: N probe calls - not all traffic
  Prevents thundering herd on recovery
  (if all traffic hit a recovering service at once:
   it might fail again immediately)
```

**SLIDING WINDOW:**

```
COUNT_BASED (last N calls):
  Ring buffer of N call outcomes
  Failure rate = failures / N
  Simple; not sensitive to time

TIME_BASED (last N seconds):
  Count outcomes in the last N seconds
  Failure rate = failures per second / total per second
  Better for bursty traffic
  Handles: "100% failure but only 5 calls" correctly
  (if volume is too low, time window helps)

SLOW CALL COUNTING:
  Calls that exceed slowCallDurationThreshold:
  counted as failures even if response was 200 OK
  Prevents: "service technically responds but is
  degraded - all calls take 10s" from being invisible
  to the circuit breaker
```

---

### 🧪 Thought Experiment

**CIRCUIT BREAKER TUNING:**

```
SCENARIO: API Gateway -> Pricing-service
  Traffic: 10,000 req/min
  Acceptable downtime: < 5 seconds auto-recovery
  Acceptable false positive: < 1 per day

TOO SENSITIVE:
  failureRateThreshold: 10%, slidingWindowSize: 10
  Problem: network blip (3 failures) = 30% failure rate
  Circuit trips; 10 minutes of outage
  Every transient network issue = circuit trip
  Result: unnecessary outages; false positives

TOO INSENSITIVE:
  failureRateThreshold: 90%, slidingWindowSize: 10000
  Problem: 8999 calls fail before circuit trips
  Thread pool: exhausted in seconds
  Cascading failure not prevented

BALANCED:
  failureRateThreshold: 50%
  minimumNumberOfCalls: 50    (reasonable sample)
  slidingWindowSize: 100      (last 100 calls)
  waitDurationInOpenState: 30s (auto-recover probe)
  permittedCallsInHalfOpen: 5  (5 probe calls)
  Result: trip when HALF of 100 calls fail
  Not triggered by network blips (< 50 calls baseline)
  Auto-recover in 30s
```

---

### 🧠 Mental Model / Analogy

> Circuit Breaker is triage medicine for distributed
> systems. In an emergency room: a patient with a
> minor issue gets immediate care. A patient with a
> critical, unsolvable issue (beyond current capacity)
> is stabilized and moved to a holding area rather
> than consuming all resources indefinitely. The ER
> can continue treating other patients. Circuit
> Breaker: OPEN state = "stabilize and hold" - no
> resources consumed on the unsolvable issue. HALF_OPEN
> = "check if situation improved". CLOSED = normal
> ER operation.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
If a service you're calling keeps failing: stop calling
it for a while (don't waste time/resources). After a
pause: try a test call. If it works: resume. This
prevents one failing service from causing your entire
application to fail.

**Level 2 - How to use it (junior developer):**
With Resilience4j + Spring Boot: `@CircuitBreaker(
name="payment-service", fallbackMethod="paymentFallback")`
on a method. Define thresholds in `application.yml`.
Write a fallback method that returns a degraded response.
The annotation handles the rest automatically.

**Level 3 - How it works (mid-level engineer):**
CircuitBreaker uses a sliding window (ring buffer of
last N outcomes). Each call: outcome recorded (success,
failure, slow). When failure rate >= threshold AND
minimum calls reached: state transitions to OPEN.
In OPEN: any call -> immediate CallNotPermittedException.
After waitDuration: -> HALF_OPEN. N probe calls allowed.
Based on probe results: -> CLOSED or OPEN.

**Level 4 - Why it was designed this way (senior/staff):**
The three-state design solves the "thundering herd on
recovery" problem. Without HALF_OPEN: the circuit goes
directly from OPEN to CLOSED when the timer expires.
All queued traffic floods the recovering service immediately
-> it fails again. HALF_OPEN: only N calls allowed as
probes. This gives the recovering service a chance
to warm up before full traffic returns. HALF_OPEN
also enables automatic recovery monitoring: the probe
calls determine whether the service is truly recovered,
not just whether the timer expired.

**Level 5 - Mastery (distinguished engineer):**
Circuit Breaker placement in a microservices call graph
matters. Each service should have a circuit breaker
for EACH downstream dependency (not one per service).
Example: order-service -> payment-service AND shipping-service.
Two circuit breakers: `payment-cb` and `shipping-cb`.
If payment fails: `payment-cb` opens. Shipping still
works. Orders can be placed (payment deferred) but
shipping can be assigned. One global circuit breaker
per service is wrong: all downstream failures would
trip the same breaker, affecting unrelated functionality.
Dependency-level circuit breakers give fine-grained
failure isolation.

---

### ⚙️ How It Works (Mechanism)

**RESILIENCE4J IMPLEMENTATION OVERVIEW:**

```java
@Configuration
public class CircuitBreakerConfig {

    @Bean
    public CircuitBreaker paymentCircuitBreaker(
            CircuitBreakerRegistry registry) {

        // Create or get from registry
        CircuitBreaker cb = registry.circuitBreaker(
            "payment-service",
            CircuitBreakerConfig.custom()
                .slidingWindowType(
                    SlidingWindowType.COUNT_BASED)
                .slidingWindowSize(100)
                .failureRateThreshold(50.0f)
                .slowCallDurationThreshold(
                    Duration.ofSeconds(2))
                .slowCallRateThreshold(80.0f)
                .waitDurationInOpenState(
                    Duration.ofSeconds(60))
                .permittedNumberOfCallsInHalfOpenState(10)
                .minimumNumberOfCalls(20)
                .recordExceptions(
                    IOException.class,
                    TimeoutException.class)
                .ignoreExceptions(
                    BusinessValidationException.class)
                .build());

        // Event monitoring
        cb.getEventPublisher()
            .onStateTransition(event -> {
                log.warn("Circuit breaker state: {} -> {}",
                    event.getStateTransition()
                         .getFromState(),
                    event.getStateTransition()
                         .getToState());
                // Alert: PagerDuty/Slack
                alertService.circuitBreakerTripped(
                    "payment-service",
                    event.getStateTransition());
            });

        return cb;
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
CIRCUIT BREAKER LIFECYCLE:

T=0: Circuit CLOSED. Normal operation.
     Sliding window: [SUCCESS, SUCCESS, ...]

T=5min: Payment-service starts failing (DB issue)
     Calls return 503 or timeout
     Sliding window: [S, S, F, F, F, F, F, F, F, F]
     After 50 failures in window: failure rate = 60%
     60% > 50% threshold: -> OPEN
     Alert: "payment-cb CLOSED -> OPEN"

T=5min to T=6min: Circuit OPEN
     All calls: CallNotPermittedException (< 1ms)
     Fallback: PaymentResult.pending(orderId)
     Order-service: threads free, non-payment ops OK
     Payment-service: NOT receiving traffic (allows recovery)

T=6min: waitDurationInOpenState (60s) expires
     -> HALF_OPEN
     Allow 10 probe calls

T=6min: Probe calls:
     Payment-service: DB recovered, responding normally
     8/10 probes succeed: success rate 80% > threshold
     -> CLOSED
     Alert: "payment-cb HALF_OPEN -> CLOSED"
     Normal operation resumes
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: one CB for all dependencies**

```java
// BAD: Single circuit breaker for the entire service
// If payment fails: CB opens
// All calls to ALL downstream services fail-fast
// Including: catalog lookup, order history
// (which don't depend on payment at all)
@CircuitBreaker(name = "order-service")  // Too broad!
public OrderResponse processRequest(Request req) {
    // Uses payment, catalog, shipping - all or nothing
}
```

```java
// GOOD: Per-dependency circuit breakers
@Service
public class OrderService {

    // Each dependency has its own circuit breaker
    @CircuitBreaker(
        name = "payment-service",
        fallbackMethod = "paymentFallback"
    )
    public PaymentResult chargePayment(
            OrderId orderId, BigDecimal amount) {
        return paymentClient.charge(orderId, amount);
    }

    @CircuitBreaker(
        name = "shipping-service",
        fallbackMethod = "shippingFallback"
    )
    public ShipmentId createShipment(Order order) {
        return shippingClient.createShipment(order);
    }

    // Payment fallback: defer payment, don't fail order
    public PaymentResult paymentFallback(
            OrderId orderId, BigDecimal amount,
            Throwable t) {
        return PaymentResult.deferred(orderId);
    }

    // Shipping fallback: create order, ship manually later
    public ShipmentId shippingFallback(
            Order order, Throwable t) {
        manualShipmentQueue.add(order);
        return ShipmentId.pending();
    }
}
// Result: payment-service failure -> payment CB opens
// Shipping still works; catalog still works
// Partial degradation, not full outage
```

---

### ⚖️ Comparison Table

| Aspect | Application CB (Resilience4j) | Network CB (Istio outlierDetection) |
|---|---|---|
| **Level** | Application code | Network proxy (Envoy) |
| **Failure detection** | Configurable: exceptions, slow calls | HTTP 5xx, connection errors |
| **Fallback** | Full application fallback logic | None (just fails fast) |
| **Language** | JVM only | Language-agnostic |
| **Business logic** | Can use cached data, queue for retry | Cannot |
| **Best for** | Business-level resilience | Network-level resilience |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Circuit Breaker replaces retry | No. Retry handles transient failures (retry and it works). Circuit Breaker handles sustained failures (service is down: stop retrying and fail fast). Both needed. Order: Circuit Breaker outermost, Retry innermost. |
| OPEN circuit means the downstream is definitely down | OPEN means: failure rate exceeded threshold. The downstream might have recovered while the circuit is still OPEN. That's why HALF_OPEN exists: probe to verify. The circuit breaker is an approximation based on recent history. |
| You should set a very short waitDurationInOpenState for fast recovery | If you set waitDuration=5s: the circuit opens and closes frequently. This "flapping" causes thundering herds: on every HALF_OPEN, full traffic floods the still-recovering service -> fails again -> OPEN again. Use waitDuration=30-60s for stability. |

---

### 🚨 Failure Modes & Diagnosis

**Circuit flapping: rapidly oscillating OPEN/CLOSED**

**Symptom:**
Alerts show: circuit breaker state changing every
30 seconds: CLOSED -> OPEN -> HALF_OPEN -> CLOSED ->
OPEN. Payment-service is partially degraded (50% of
requests succeed). Users see intermittent failures
throughout the day.

**Root Cause:**
1. `waitDurationInOpenState` is too short (e.g., 10s)
2. Payment-service is running at ~50% failure rate
   (database connection pool insufficient)
3. Probe calls succeed 50% of the time -> sometimes
   closes, sometimes stays open

**Diagnostic:**
```bash
# Prometheus query: circuit breaker state over time
resilience4j_circuitbreaker_state{name="payment-service"}
# See: 0, 0, 1, 0, 1, 0, 1 = flapping

# Check actual failure rate of payment-service
resilience4j_circuitbreaker_failure_rate{
  name="payment-service"}
# 48%, 51%, 49%, 52% = right at the threshold

# Root cause: payment-service DB connection pool
kubectl logs -l app=payment-service | \
  grep -c 'HikariPool.*timeout'
# 847 connection timeout errors in last hour
```

**Fix:**
1. Fix root cause: increase payment-service DB connection
   pool (HikariCP `maximumPoolSize`).
2. Increase `waitDurationInOpenState` to 60s to
   stabilize the flapping.
3. Adjust `failureRateThreshold` to 70%: don't trip
   at 50% (some failures acceptable).
4. Monitor: alert when circuit opens for > 2 minutes
   (flapping detection).

---

### 🔗 Related Keywords

**Implementations:**
- `Resilience4j` - primary Java implementation
  of the Circuit Breaker pattern

**Related patterns:**
- `Bulkhead Pattern` - complements Circuit Breaker:
  limits concurrency to prevent pool exhaustion
- `Timeout and Retry Patterns` - Circuit Breaker
  works alongside retries (CB outer, Retry inner)
- `Service Mesh` - Istio implements network-level
  circuit breaking via outlierDetection in DestinationRule
- `Istio` - `outlierDetection` in DestinationRule
  is the service-mesh circuit breaker equivalent

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STATES       │ CLOSED -> OPEN -> HALF_OPEN -> CLOSED   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Converts slow failure -> fast failure     │
│              │ Prevents thread pool exhaustion           │
├──────────────┼───────────────────────────────────────────┤
│ PER-DEPENDENCY│ One CB per downstream dependency        │
│              │ Not one per service                      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Stop calling a failing service;          │
│              │  fail fast; probe for recovery"          │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Three states: CLOSED (normal), OPEN (fail-fast),
   HALF_OPEN (probe). The cycle: CLOSED -> OPEN after
   threshold -> HALF_OPEN after waitDuration -> CLOSED
   if probes succeed.
2. Circuit Breaker converts slow failure into fast
   failure. Speed of failure is what prevents cascading.
3. One Circuit Breaker per downstream dependency,
   not one per service. Isolate failures at the
   dependency level.

**Interview one-liner:**
"Circuit Breaker prevents cascading failures: wraps
calls to downstream services; monitors failure rate
in a sliding window. When rate >= threshold (CLOSED ->
OPEN): all calls fail immediately (no downstream call).
After waitDuration: HALF_OPEN probe; if probes succeed:
CLOSED again. Key: converts slow failure (thread-blocking
timeout) to fast failure (<1ms). One CB per dependency.
Java: Resilience4j. Network-level: Istio outlierDetection."

---

### 💡 The Surprising Truth

The Circuit Breaker's most underappreciated benefit:
it protects the downstream service during recovery.
A common failure mode: payment-service is down (DB
overloaded). Circuit Breaker trips (OPEN). Payment-service
DB recovers. WITHOUT Circuit Breaker: all queued traffic
floors the payment-service immediately -> DB overwhelmed
again. WITH Circuit Breaker: only probe calls allowed
during HALF_OPEN. The service recovers gradually.
When Circuit Breaker closes: normal traffic resumes.
The Circuit Breaker doesn't just protect the caller;
it protects the downstream service's recovery window.
This is why `waitDurationInOpenState` should be long
enough for the downstream service to actually recover
(typically 30-120 seconds, not 5 seconds).

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **STATES** Draw the Circuit Breaker state machine
   with all transitions, triggers, and conditions.
2. **CONFIGURE** Write complete Resilience4j config
   for a circuit breaker: sliding window, thresholds,
   minimum calls, wait duration, probe calls.
3. **PLACEMENT** Design the circuit breaker topology
   for a service with 4 dependencies: which CB for
   each, what fallback for each.
4. **DEBUG** Diagnose circuit flapping: identify
   root cause, distinguish from genuine service failure,
   tune configuration to stabilize.
5. **COMPARE** Articulate the difference between
   Resilience4j CircuitBreaker and Istio outlierDetection:
   what each handles, why you might use both.

---

### 🧠 Think About This Before We Continue

**Q1.** Your order-service has 6 downstream dependencies:
payment, shipping, inventory, notification, fraud,
and loyalty. Which should have circuit breakers? What
fallback strategy would you use for each if its
circuit trips? Which services are "synchronous critical"
(order can't complete without them) vs "optional"
(order can complete in degraded mode)?

**Q2.** Your circuit breaker is configured with
`failureRateThreshold=50%` and `slidingWindowSize=100`.
The downstream service fails on ALL calls between
9:05am and 9:15am (10 minutes). But `minimumNumberOfCalls`
is 100, and only 40 calls were made in the window.
The circuit never trips. How do you detect this
scenario via monitoring? How do you fix the configuration?

**Q3.** A payment service is deployed in two regions
(us-east-1 and eu-west-1). Each region has its own
circuit breaker. The us-east-1 circuit is OPEN but
eu-west-1 is CLOSED. How does this affect: (a) traffic
routing strategy, (b) fallback behavior, (c) data
consistency (if payment writes happen in eu but reads
are expected in us)?