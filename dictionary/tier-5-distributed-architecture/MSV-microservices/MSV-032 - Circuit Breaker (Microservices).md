---
layout: default
title: "Circuit Breaker (Microservices)"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 32
permalink: /microservices/circuit-breaker/
id: MSV-032
category: Microservices
difficulty: ★★★
depends_on: Inter-Service Communication, Resilience4j, Distributed Systems
used_by: Bulkhead Pattern, Fallback Strategy, Service Mesh
related: Resilience4j, Bulkhead Pattern, Retry Strategy
tags:
  - microservices
  - distributed
  - pattern
  - deep-dive
  - reliability
---

# MSV-032 - Circuit Breaker (Microservices)

⚡ TL;DR - The Circuit Breaker pattern stops a failing service from being called repeatedly, enabling fast failure and recovery time by opening a protective switch that bypasses the broken downstream.

| #647 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Inter-Service Communication, Resilience4j, Distributed Systems | |
| **Used by:** | Bulkhead Pattern, Fallback Strategy, Service Mesh | |
| **Related:** | Resilience4j, Bulkhead Pattern, Retry Strategy | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A user's checkout request triggers calls to Payments, Inventory, and Tax services. Tax service is suffering a database deadlock - every call takes 30 seconds before timing out. The checkout service's thread waits 30 seconds per call. With 200 concurrent checkouts, 200 threads are blocked on a dead Tax service. No threads remain for calls to Payments and Inventory (which are healthy). The entire checkout fails - not because Tax is essential for authorising payment, but because the system cannot stop calling it.

**THE BREAKING POINT:**
Without the ability to stop calling a known-dead service, a slow/failing dependency holds threads indefinitely, exhausting the calling service's resources and causing cascading failures to unrelated dependencies. The system needs a way to "give up on X" quickly and consistently.

**THE INVENTION MOMENT:**
This is exactly why the Circuit Breaker pattern was introduced by Michael Nygard in "Release It!" (2007) - to provide a switch that automatically opens when a service is failing, enabling fast rejection and system recovery without human intervention.

---

### 📘 Textbook Definition

The **Circuit Breaker** pattern is a resilience design pattern that wraps calls to a remote service with a state machine. The state machine has three states: **CLOSED** (normal - calls pass through), **OPEN** (failure threshold exceeded - calls are rejected immediately without attempting the remote call), and **HALF-OPEN** (recovery probe - a limited number of calls are attempted to test if the downstream has recovered). The circuit "opens" when failure rate exceeds a threshold, preventing further calls to the failed service and allowing it time to recover.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A circuit breaker is an automatic switch that cuts off a failing service call before it can bring down the caller.

**One analogy:**
> An electrical circuit breaker in your home's fuse box works exactly the same way. Normally, electricity flows freely (CLOSED). When a dangerous overload is detected, the breaker trips (OPEN) - electricity stops flowing immediately to protect the wiring. After you investigate and reset the breaker (HALF-OPEN), it allows a controlled test to confirm safety. The circuit breaker doesn't fix the problem - it prevents it from spreading.

**One insight:**
The circuit breaker's value is not in preventing failures - failures will happen. Its value is in *containing failure* by turning a slow, resource-consuming failure (30-second timeout) into a fast, cheap failure (<1ms rejection).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A known-failing service should not be called repeatedly - each attempt wastes resources and adds latency.
2. Recovery should be automatic - the circuit should attempt to close after the downstream has had time to recover.
3. Failure detection must be tuned to distinguish transient errors (retry-worthy) from persistent failures (circuit-open-worthy).

**DERIVED DESIGN:**
The three-state machine arises from Invariants 1 and 2:
- State CLOSED satisfies normal operation (calls pass through).
- State OPEN satisfies Invariant 1 (reject calls immediately after persistence failure detected).
- State HALF-OPEN satisfies Invariant 2 (probe the downstream; if healthy, restore normal flow; if still failing, extend open period).

The sliding window (last N calls or last N seconds) provides the failure rate measurement. Threshold calibration is critical: too sensitive (opens on normal transients) vs too resistant (doesn't protect under real failures).

**THE TRADE-OFFS:**
**Gain:** Fast failure instead of slow timeout cascade, resource protection (threads/connections freed immediately), automatic recovery.
**Cost:** Adds a brief window of "false opens" (circuit opens during transient spike), state management complexity in distributed environments (per-instance vs shared state), fallback design required.

---

### 🧪 Thought Experiment

**SETUP:**
Checkout service calls Tax service. Tax service is down for 5 minutes.

**WITHOUT CIRCUIT BREAKER:**
Every checkout attempt: waits 30 seconds (timeout), fails. 5 minutes = 300 seconds = 10 timeouts (sequential) or 10 concurrent calls holding 300 total thread-seconds. Thread pool of 50 fills up in 50 × 30s = users experience no service for 25 minutes of that 5-minute outage window (queue builds up).

**WITH CIRCUIT BREAKER (threshold: 5 failures, 30s wait):**
1. Calls 1–5: fail (timeout), recorded
2. Call 6: circuit OPENS
3. Calls 7–N: instant rejection (<1ms), fallback returns "tax calculation unavailable"
4. After 30s: HALF-OPEN, 3 probe calls sent
5. Still failing: back to OPEN for another 30s
6. Tax service recovers at minute 3: probes succeed
7. Circuit CLOSES: normal operation resumes at minute 3 + probe window

Thread pool never fills. Other services (Payments, Inventory) continue unaffected throughout.

**THE INSIGHT:**
The circuit breaker converts a 30-second blocking failure into a <1ms rejection. The difference in resource consumption is 30,000× (30,000ms vs 1ms).

---

### 🧠 Mental Model / Analogy

> The circuit breaker in microservices is exactly the same as the circuit breaker in your home - with one addition. After the breaker trips (OPEN), a timer runs. When the timer expires, the breaker does a controlled test (HALF-OPEN): it lets a small amount of current flow. If the test passes, the breaker resets (CLOSED). If not, it trips again and delays longer.

- "Breaker trips" → CLOSED → OPEN transition (failure threshold reached)
- "Timer expires" → `waitDurationInOpenState` elapses → HALF-OPEN
- "Controlled test" → probe calls in HALF-OPEN state
- "Breaker resets" → HALF-OPEN → CLOSED (success rate above threshold)
- "Trips again" → HALF-OPEN → OPEN (probes fail)

Where this analogy breaks down: a house circuit breaker requires manual reset. A software circuit breaker automatically attempts recovery - it is more like a self-resetting thermal breaker than a manual fuse.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A circuit breaker watches how often a service call fails. When it fails too often, the circuit breaker stops making the call and immediately returns an error or a default value. After some time, it tries again to see if the problem is fixed.

**Level 2 - How to use it (junior developer):**
Use Resilience4j `@CircuitBreaker` annotation in Spring Boot. Configure thresholds in `application.yml`. Define a fallback method with the same signature plus an `Exception` parameter. The fallback runs when the circuit is open or the call fails.

**Level 3 - How it works (mid-level engineer):**
Resilience4j's CircuitBreaker uses a ring buffer (sliding window) to track the last N calls. For each call, the result (success/failure/slow-call) is stored. After the window is filled, failure rate = (failures + slow calls) / total calls. If failure rate ≥ threshold: state transitions to OPEN. All calls in OPEN state receive `CallNotPermittedException` immediately (no downstream call made). A scheduled thread waits `waitDuration`, then transitions to HALF-OPEN. In HALF-OPEN: exactly `permittedCallsInHalfOpenState` calls are allowed through. If their success rate ≥ threshold: CLOSED. Otherwise: OPEN again.

**Level 4 - Why it was designed this way (senior/staff):**
The circuit breaker pattern predates microservices - Michael Nygard described it for SOA systems in "Release It!" (2007). Netflix popularised it for microservices via Hystrix (2012). The key design decision in Hystrix was to use a separate thread pool per dependency - this provided complete isolation at the cost of thread overhead. Resilience4j chose semaphore isolation as the default: the calling thread is the one being permitted/rejected, not a separate pool thread. This is more efficient but means circuit breaker rejection is synchronous - reactive/async architectures need to handle `CallNotPermittedException` asynchronously. At cloud scale, the outstanding challenge is shared circuit breaker state across multiple instances of the same service - each instance maintains its own state independently unless using a shared store (Redis).

---

### ⚙️ How It Works (Mechanism)

**State transition logic:**

```
┌──────────────────────────────────────────────────────┐
│           Circuit Breaker State Machine              │
├──────────────────────────────────────────────────────┤
│                                                      │
│  CLOSED                                              │
│  ┌─────────────────────────────────┐                 │
│  │ Call allowed through            │                 │
│  │ Results recorded in ring buffer │                 │
│  │ Failure rate calculated         │                 │
│  └────────────────┬────────────────┘                 │
│                   │                                  │
│  failure rate ≥ threshold (e.g., 50% of last 10)    │
│                   ▼                                  │
│  OPEN                                                │
│  ┌─────────────────────────────────┐                 │
│  │ All calls rejected instantly    │                 │
│  │ CallNotPermittedException       │                 │
│  │ waitDurationInOpenState timer   │                 │
│  └────────────────┬────────────────┘                 │
│                   │                                  │
│  timer expires                                       │
│                   ▼                                  │
│  HALF-OPEN                                           │
│  ┌─────────────────────────────────┐                 │
│  │ N probe calls allowed through   │                 │
│  │ Success rate ≥ threshold         │                 │
│  │    → transition to CLOSED       │                 │
│  │ Any failure                     │                 │
│  │    → back to OPEN               │                 │
│  └─────────────────────────────────┘                 │
└──────────────────────────────────────────────────────┘
```

**Resilience4j full configuration:**

```java
CircuitBreakerConfig config = CircuitBreakerConfig.custom()
    .slidingWindowType(COUNT_BASED)
    .slidingWindowSize(10)
    .minimumNumberOfCalls(5)          // min calls before evaluating
    .failureRateThreshold(50.0f)      // % failures to open
    .slowCallRateThreshold(80.0f)     // % slow calls to open
    .slowCallDurationThreshold(
        Duration.ofSeconds(2))        // what counts as slow
    .waitDurationInOpenState(
        Duration.ofSeconds(30))       // how long to stay open
    .permittedNumberOfCallsInHalfOpenState(5)
    .automaticTransitionFromOpenToHalfOpenEnabled(true)
    .recordExceptions(
        IOException.class,
        TimeoutException.class,
        FeignException.class
    )
    .ignoreExceptions(
        NotFoundException.class       // 404s are not failures
    )
    .build();
```

---

### 🔄 The Complete Picture - End-to-End Flow

**CLOSED STATE FLOW:**
Request → CircuitBreaker checks state (CLOSED) ← YOU ARE HERE → Records call → Makes HTTP call → Records result (success/failure) → Updates ring buffer → Returns result

**OPEN STATE FLOW:**
Request → CircuitBreaker checks state (OPEN) ← YOU ARE HERE → Immediately throws CallNotPermittedException → Fallback called → Returns default/cached result - zero network calls made

**FAILURE PATH:**
10 consecutive failures → ring buffer: 10/10 failures = 100% → 100% > 50% threshold → OPEN → timer starts (30s) → after 30s: HALF-OPEN → 5 probe calls → all succeed → CLOSED

**WHAT CHANGES AT SCALE:**
At 100,000 req/s, the circuit breaker's ring buffer operations must be thread-safe and lock-free. Resilience4j uses lock-free `AtomicInteger` operations for the ring buffer. The bottleneck at extreme scale is contention on the state variable - mitigated by using many small circuit breakers (one per instance pair) rather than one shared CB.

---

### 💻 Code Example

**Example 1 - Full Spring Boot + Resilience4j CB with fallback:**

```java
@Service
public class TaxService {
    private final TaxClient taxClient;

    @CircuitBreaker(
        name = "taxService",
        fallbackMethod = "taxFallback"
    )
    public TaxAmount calculateTax(Order order) {
        return taxClient.calculate(order.total(), order.country());
    }

    // Fallback: called when CB is OPEN or call fails
    private TaxAmount taxFallback(Order order, Exception ex) {
        log.warn("Tax service unavailable: {}", ex.getMessage());
        // Return estimated tax (business decision: always something)
        return TaxAmount.estimated(order.total());
    }
}
```

**Example 2 - Monitor CB state transitions:**

```java
@Configuration
public class CircuitBreakerMetrics {
    @Bean
    public CircuitBreakerRegistry circuitBreakerRegistry(
            MeterRegistry meterRegistry) {
        CircuitBreakerRegistry registry =
            CircuitBreakerRegistry.ofDefaults();
        // Bind all circuit breakers to Prometheus metrics
        TaggedCircuitBreakerMetrics
            .ofCircuitBreakerRegistry(registry)
            .bindTo(meterRegistry);
        return registry;
    }
}
// Exposes: resilience4j_circuitbreaker_state{name="taxService"}
// Values: 0=CLOSED, 1=OPEN, 2=HALF_OPEN
```

**Example 3 - Forcing CB to OPEN for testing:**

```java
@Test
@DisplayName("Returns estimated tax when CB is open")
void returnsEstimatedTaxWhenCircuitIsOpen() {
    CircuitBreaker cb = circuitBreakerRegistry.circuitBreaker("taxService");
    // Force open state without simulating failures
    cb.transitionToOpenState();

    Order order = Order.of(Money.of(100, "USD"), "US");
    TaxAmount result = taxService.calculateTax(order);

    assertThat(result.isEstimate()).isTrue();
    assertThat(result.amount()).isEqualTo(Money.of(8, "USD")); // estimated
    verify(taxClient, never()).calculate(any(), any()); // no downstream call
}
```

---

### ⚖️ Comparison Table

| Implementation | State Management | Language | Config | Best For |
|---|---|---|---|---|
| **Resilience4j (CB)** | Per-JVM-instance | Java 8+ | application.yml | Spring Boot services |
| Istio OutlierDetection | Per-Envoy | Any | VirtualService YAML | Polyglot, no code change |
| AWS App Mesh | Per-proxy | Any | Console/Terraform | AWS-native services |
| Polly | Per-.NET-instance | .NET | Code/policy | .NET services |

How to choose: use Resilience4j for JVM services where you need application-level fallback logic. Use Istio/Envoy for polyglot environments or where zero code changes are required.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Circuit breaker prevents service failures | CB does not fix the downstream service. It prevents the caller from being overwhelmed while the downstream recovers |
| CB opens on the first failure | By design, there is a minimum call window before CB opens. Single transient failures do not open the circuit |
| CB state is shared across all service instances | Default Resilience4j CB is per-JVM-instance. 5 instances of your service = 5 independent circuit breakers |
| HALF-OPEN means 50% of traffic flows | HALF-OPEN means exactly N probe calls are allowed (e.g., `permittedCallsInHalfOpenState=5`), not 50% of all calls |
| You should retry when the circuit is OPEN | Never. If CB is OPEN, the downstream is known-bad. Retrying wastes resources. Use fallback instead |

---

### 🚨 Failure Modes & Diagnosis

**1. Circuit Opens on Transient Spikes (False Positive)**

**Symptom:** During brief traffic spikes, the circuit breaker opens even though downstream is healthy. Users briefly see fallback responses.

**Root Cause:** `slidingWindowSize` too small. With 5-call window, two timeouts = 40% failure rate, one more = 60% → opens at 50% threshold.

**Diagnostic:**
```bash
# Check CB metrics over time
curl http://service:8080/actuator/metrics/\
resilience4j.circuitbreaker.calls | python3 -m json.tool
# Also check: state_transitions metric for how often it opens
```

**Fix:** Increase `slidingWindowSize` (try 20–50 calls) and `minimumNumberOfCalls` so the failure rate is calculated over a larger, more stable window.

**Prevention:** Tune CB thresholds based on production traffic patterns. A window of 3 calls is dangerously sensitive; most production services use 20–50.

**2. CB Open But Fallback Returns Stale Data**

**Symptom:** CB is open and fallback returns cached tax rates from 6 months ago. Customer is being charged incorrect tax.

**Root Cause:** Fallback returns stale data without TTL management. Tax rates have changed but cache was not updated.

**Diagnostic:**
```bash
# Check cache TTL configuration
grep "expiry\|ttl\|maxAge" src/ -r --include="*.java" --include="*.yml"
```

**Fix:** Add TTL to fallback cache. If cache is stale (e.g., > 1 hour), fail the fallback too (let the order fail gracefully) rather than return wrong data.

**Prevention:** Fallback data must have explicit TTL. Design fallbacks for the "safe default" case - never silently return wrong data.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Inter-Service Communication` - circuit breaker wraps inter-service calls; understanding call semantics is prerequisite
- `Resilience4j` - the primary Java implementation of the circuit breaker pattern for Spring Boot services

**Builds On This (learn these next):**
- `Bulkhead Pattern` - the complementary isolation pattern that prevents thread exhaustion independent of circuit breaking
- `Fallback Strategy` - defines what happens when the circuit is open - the circuit breaker is only as useful as its fallback

**Alternatives / Comparisons:**
- `Retry Strategy` - the complementary pattern: retry for transient failures; circuit break for persistent failures
- `Bulkhead Pattern` - while CB protects callers from a specific failing service, Bulkhead limits how much of the thread pool any one service can consume

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ State machine that fast-rejects calls to  │
│              │ a failing service, enabling automatic     │
│              │ recovery                                  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Slow/failing downstream holds threads,    │
│ SOLVES       │ cascading failure to unrelated services   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The value is converting slow failure      │
│              │ (30s timeout) to fast failure (<1ms)      │
│              │ - 30,000x resource difference             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Synchronous calls to services that can    │
│              │ fail, especially under sustained load     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Don't use CB for calls where the fallback │
│              │ would produce incorrect business results  │
│              │ (e.g., payment auth - fail properly)      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Fast failure + resource protection vs     │
│              │ brief "false opens" + fallback complexity │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Don't keep calling a broken phone -      │
│              │  hang up and try again in 30 seconds."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Bulkhead Pattern → Fallback Strategy →    │
│              │ Retry Strategy                            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your checkout service calls 5 downstream services: Payments (critical), Inventory (critical), Tax (non-critical), Recommendations (non-critical), Fraud Detection (critical). Design the fallback strategy for each circuit breaker. For the critical services, the circuit breaker should fail the entire checkout. For non-critical, it should degrade gracefully. How do you design the fallback to distinguish between "CB open - use cached data" and "CB open - this is a critical service, reject the request"?

**Q2.** You run 20 instances of your order service, each with an independent Resilience4j circuit breaker for the inventory service. Inventory is having an intermittent issue: 10% of calls fail sporadically. With a 10-call window and 50% threshold, your circuit breakers almost never open (10% × 10 calls = 1 failure per window → 10%, well below 50%). Users experience 10% of requests failing with errors. Design the detection and response strategy that correctly protects users from this 10% failure rate without requiring each instance to see enough failures to individually trip their circuit breakers.

