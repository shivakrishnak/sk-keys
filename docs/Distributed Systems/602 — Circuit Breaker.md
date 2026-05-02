---
layout: default
title: "Circuit Breaker"
parent: "Distributed Systems"
nav_order: 602
permalink: /distributed-systems/circuit-breaker/
number: "0602"
category: Distributed Systems
difficulty: ★★☆
depends_on: Timeout, Heartbeat, Failure Modes, Retry with Backoff
used_by: Service Mesh, Bulkhead, Fallback, Graceful Degradation, Hystrix, Resilience4j
related: Retry with Backoff, Bulkhead, Fallback, Timeout, Graceful Degradation
tags:
  - distributed
  - reliability
  - resilience
  - pattern
---

# 602 — Circuit Breaker

⚡ TL;DR — A circuit breaker wraps remote calls; when failure rate exceeds a threshold it "opens" and immediately rejects calls (without hitting the failing service), allowing it time to recover; it periodically tests recovery with a half-open state before fully closing again.

| #602            | Category: Distributed Systems                                                 | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Timeout, Heartbeat, Failure Modes, Retry with Backoff                         |                 |
| **Used by:**    | Service Mesh, Bulkhead, Fallback, Graceful Degradation, Hystrix, Resilience4j |                 |
| **Related:**    | Retry with Backoff, Bulkhead, Fallback, Timeout, Graceful Degradation         |                 |

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Service A calls Service B for every user request. Service B goes down. Service A's threads are now blocked waiting for B's timeouts (30 seconds each). Service A has 200 thread pool slots. All 200 fill up with blocked B-calls. New requests to Service A queue up. Service A runs out of connection pool — timeouts in Service A. Service C depends on A — same cascade. Three services are now down because one service went down. This is a **cascading failure**, and it is the single most common cause of major distributed system outages.

**THE INVENTION MOMENT:**
Michael Nygard's "Release It!" (2007) described the circuit breaker pattern named after electrical circuit breakers: when current exceeds a threshold, the breaker trips (opens), protecting downstream components. Apply this to service calls: when error rate exceeds threshold, the circuit "trips" (opens) and immediately rejects calls with a fast failure, preserving thread pool capacity and preventing cascade.

---

### 📘 Textbook Definition

A **circuit breaker** is a stability pattern that wraps remote calls and transitions between three states based on observed failure metrics:

- **CLOSED** (normal): calls pass through; failure counts are tracked; if failure rate exceeds threshold → OPEN.
- **OPEN** (tripped): all calls fail immediately with `CircuitBreakerOpenException` (no actual call to remote); after a timeout (recovery window) → HALF-OPEN.
- **HALF-OPEN** (testing): a limited number of probe calls are allowed through; if they succeed → CLOSED; if they fail → OPEN again.

**Key metrics:** `failure_rate_threshold` (e.g., 50%), `slow_call_rate_threshold` (e.g., 80% of calls > 2s), `minimum_number_of_calls` (sliding window before evaluating), `wait_duration_in_open_state`, `permitted_calls_in_half_open_state`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Circuit breaker: keep score of how often a service fails — if it fails too often, stop calling it immediately and wait for it to recover.

**One analogy:**

> A circuit breaker is like a fuse in your home's electrical panel. When the microwave's wiring shorts out (failure), the fuse blows (circuit OPENS) instantly, cutting power before the overload burns down the house (cascade failure). After you fix the wiring, you reset the fuse (HALF-OPEN test), and if it holds, power is restored (CLOSED). Without the fuse, one faulty appliance would fry your entire home.

**One insight:**
The circuit breaker's most important contribution is **fail fast**: instead of 30-second timeouts consuming thread pool slots, a tripped circuit breaker returns in microseconds. This is what prevents cascade failure — not the recovery mechanism, but the immediate cut-off that preserves the calling service's resources.

---

### 🔩 First Principles Explanation

**STATE MACHINE:**

```
        ┌────────────┐
        │   CLOSED   │◄──── success probe ────┐
        └────────────┘                         │
               │                               │
   failure_rate > threshold               ┌────────────┐
               │                          │ HALF-OPEN  │
               ▼                          └────────────┘
        ┌────────────┐                         │
        │    OPEN    │──── wait timeout ───────┘
        └────────────┘

CLOSED: counter = 10, failures = 6 → 60% > 50% threshold → OPEN
OPEN:   all calls return CircuitBreakerOpenException immediately (0ms latency)
        after wait_duration (e.g., 30s) → HALF-OPEN
HALF-OPEN: 3 probe calls allowed
  3/3 succeed → CLOSED
  1+ fail → OPEN (restart wait_duration)
```

**RESILIENCE4J CONFIGURATION:**

```java
CircuitBreakerConfig config = CircuitBreakerConfig.custom()
    .failureRateThreshold(50)              // 50% failure rate → OPEN
    .slowCallRateThreshold(80)             // 80% slow calls (>2s) → OPEN
    .slowCallDurationThreshold(Duration.ofSeconds(2))
    .waitDurationInOpenState(Duration.ofSeconds(30))  // OPEN → HALF-OPEN after 30s
    .minimumNumberOfCalls(10)              // need at least 10 calls before evaluating
    .slidingWindowSize(20)                 // evaluate last 20 calls
    .slidingWindowType(COUNT_BASED)        // or TIME_BASED (last N seconds)
    .permittedNumberOfCallsInHalfOpenState(3)
    .build();

CircuitBreaker breaker = CircuitBreakerRegistry.of(config)
    .circuitBreaker("payment-service");

// Wrap call:
Supplier<String> decoratedCall = CircuitBreaker.decorateSupplier(
    breaker, () -> paymentService.processPayment(request));

Try.ofSupplier(decoratedCall)
    .recover(CallNotPermittedException.class, ex -> fallbackResponse());
```

**FAILURE VS EXCEPTION SLIDING WINDOW:**

```
COUNT_BASED window of 20:
  Tracks last 20 calls regardless of time.
  Good for: steady-flow services.
  Problem: if calls are rare (1 per minute), window spans 20 minutes — slow detection.

TIME_BASED window of 60 seconds:
  Tracks all calls in last 60 seconds.
  Good for: services with variable call rates.
  Problem: in a thundering herd, evaluation based on 10,000 calls/60s (not 20).

Best practice: use TIME_BASED with minimumNumberOfCalls to avoid premature tripping.
```

---

### 🧪 Thought Experiment

**CIRCUIT BREAKER WITHOUT FALLBACK IS A HALF-SOLUTION:**

Payment service calls fraud-detection service. Circuit breaker trips.

- Without fallback: payment service throws `CircuitBreakerOpenException` → user sees 500 error.
- With fallback: payment service falls back to "allow payment, flag for manual review" → degraded but functional.

The circuit breaker **stops the cascade**; the fallback **preserves business function**. Neither alone is sufficient. The correct pattern is:

```
try {
    result = circuitBreaker.execute(() -> fraudService.check(payment));
} catch (CallNotPermittedException | FraudServiceException e) {
    result = FraudResult.ALLOW_WITH_MANUAL_REVIEW; // fallback
    metrics.increment("fraud.circuit_open.fallback");
}
```

---

### 🧠 Mental Model / Analogy

> Think of a call center with 100 agents. Service B is like a supplier that answers calls but takes 30 seconds to respond (due to their system being down). Without a circuit breaker: all 100 agents are stuck on hold waiting for the supplier. No one can take new calls. The whole call center is paralyzed by one slow supplier. With a circuit breaker: after 10 agents get stuck, the supervisor (circuit breaker) says "everyone stop calling that supplier — they're clearly down — use the backup process." 90 agents stay productive.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Circuit breaker watches how often a service call fails. Too many failures → stops calling it ("OPEN"), returns an error immediately. After a timeout, tries again carefully ("HALF-OPEN"). If recovered → back to normal ("CLOSED").

**Level 2:** Three states: CLOSED (normal), OPEN (fail fast), HALF-OPEN (probe). Sliding window: count-based or time-based. Metrics: failure rate + slow call rate. Resilience4j, Hystrix. Must combine with fallback for meaningful degradation.

**Level 3:** Bulkhead pattern is complementary: circuit breaker prevents cascade; bulkhead isolates thread pools so one downstream service's failures don't exhaust the calling service's thread pool. Together: bulkhead limits blast radius of individual calls; circuit breaker limits how long failures persist. Istio/Envoy implement circuit breaking at the sidecar proxy level (outlier detection) without code changes.

**Level 4:** Circuit breaker state is per-instance, not cluster-wide. In a 100-pod microservice, each pod has its own circuit breaker. Pod A may open its circuit (its failures exceed threshold) while Pod B remains CLOSED (it had fewer failures). This is correct and intentional: each pod independently decides to stop calling based on its own observed failures. For cluster-wide state, Istio's outlier detection uses a shared control plane; per-pod circuit breakers are the application-level pattern. Tuning: `waitDurationInOpenState` should equal the expected recovery time of the downstream service. Too short → circuit flaps between OPEN and HALF-OPEN. Too long → extended period of unavailability that outlasts the actual outage.

---

### ⚙️ How It Works (Mechanism)

**Minimal Circuit Breaker Implementation:**

```java
public class CircuitBreaker {
    enum State { CLOSED, OPEN, HALF_OPEN }

    private State state = State.CLOSED;
    private int failureCount = 0;
    private long openedAt = 0;
    private static final int THRESHOLD = 5;
    private static final long RECOVERY_MS = 30_000;

    public <T> T execute(Supplier<T> call) throws Exception {
        if (state == State.OPEN) {
            if (System.currentTimeMillis() - openedAt > RECOVERY_MS) {
                state = State.HALF_OPEN;
            } else {
                throw new CircuitOpenException("Circuit OPEN — fail fast");
            }
        }
        try {
            T result = call.get();
            onSuccess();
            return result;
        } catch (Exception e) {
            onFailure();
            throw e;
        }
    }

    private void onSuccess() {
        failureCount = 0;
        state = State.CLOSED;
    }

    private void onFailure() {
        failureCount++;
        if (failureCount >= THRESHOLD || state == State.HALF_OPEN) {
            state = State.OPEN;
            openedAt = System.currentTimeMillis();
        }
    }
}
```

---

### ⚖️ Comparison Table

| Pattern         | Prevents Cascade       | Fast Recovery               | User Impact     | Where Applied              |
| --------------- | ---------------------- | --------------------------- | --------------- | -------------------------- |
| Circuit Breaker | Yes (fast fail)        | Via HALF-OPEN probe         | Error on open   | Application code / sidecar |
| Retry           | No                     | Yes (eventual)              | Delayed success | Application code           |
| Timeout         | Partially              | No (must timeout each call) | Delay           | Application code           |
| Bulkhead        | Yes (thread isolation) | No                          | Queue/rejection | Thread pool config         |

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                                                               |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Circuit breaker heals the downstream service         | It only stops flooding the failing service. Recovery is the downstream service's responsibility                                       |
| An open circuit means the service is definitely down | The service may have recovered after the circuit opened. HALF-OPEN tests for this                                                     |
| Circuit breaker eliminates need for timeouts         | No — timeouts are still needed for calls in CLOSED/HALF-OPEN state; breaker only short-circuits in OPEN state                         |
| Using circuit breaker means you don't need fallbacks | Open circuit returns fast failure to caller. Without fallback, the caller still propagates the error. Fallback = graceful degradation |

---

### 🚨 Failure Modes & Diagnosis

**Circuit Breaker Flapping (Oscillating OPEN ↔ HALF-OPEN)**

Symptom: Logs show circuit rapidly cycling between OPEN and HALF-OPEN every 30
seconds; downstream service appears to be recovering but breaker keeps re-opening.

Cause: `waitDurationInOpenState` (30s) is shorter than downstream recovery time (5-10
minutes). Half-open probe fires before service is stable; probe fails; circuit re-opens
immediately.

Fix: Increase `waitDurationInOpenState` to match downstream recovery profile. Use
exponential backoff for OPEN-to-HALF-OPEN transition. Alert when circuit flaps more
than 3× in 10 minutes — indicates systemic downstream issue requiring human escalation.

---

### 🔗 Related Keywords

- `Retry with Backoff` — complements circuit breaker: retry on transient failures; circuit breaker on persistent failures
- `Bulkhead` — isolates thread pools to prevent one service grinding others
- `Fallback` — provides degraded response when circuit is open
- `Timeout` — needed even with circuit breaker for calls in CLOSED/HALF-OPEN states
- `Graceful Degradation` — the overall strategy circuit breaker enables

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  CIRCUIT BREAKER: fail fast, recover gracefully          │
│  CLOSED → OPEN: failure_rate > threshold                 │
│  OPEN → HALF-OPEN: after waitDurationInOpenState         │
│  HALF-OPEN → CLOSED: probe calls succeed                 │
│  HALF-OPEN → OPEN: probe call fails                      │
│  Always pair with: fallback + bulkhead + timeout         │
│  Resilience4j / Istio outlier detection                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your order service calls an inventory service. The inventory service is working but extremely slow (p99 = 20 seconds) due to a bad query. You have a circuit breaker with `failureRateThreshold=50%` and `slowCallRateThreshold=80%` with `slowCallDurationThreshold=2s`. Neither the failure rate nor the slow call rate threshold are met (p50 = 200ms, p99 = 20s). The inventory service is not "failing" in the traditional sense — it's just very slow. Why might the circuit breaker NOT trip in this scenario? How would you configure it to protect against slow (but not failing) dependencies?

**Q2.** A microservice has a circuit breaker for calls to a payment gateway. During Black Friday, call volume increases 100×. The circuit breaker `minimumNumberOfCalls=10` is breached in milliseconds. During a 2-second blip in payment gateway connectivity, the circuit trips open. With 100× volume, the 30-second OPEN window means how many requests fail fast (rough estimate)? Design a configuration that reduces user impact during brief connectivity blips at high volume, without increasing false positive risk during actual outages.
