---
id: DPT-057
title: Circuit Breaker Pattern
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-005, DPT-056
used_by: DPT-064, DPT-065
related: DPT-056, DPT-060, DPT-086, DPT-089
tags:
  - pattern
  - resilience
  - advanced
  - fault-tolerance
  - distributed-systems
  - fail-fast
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 57
permalink: /technical-mastery/design-patterns/circuit-breaker/
---

⚡ TL;DR - The Circuit Breaker Pattern stops making calls
to a failing downstream service by "opening" the circuit
after a threshold of failures, preventing cascading failures
and allowing the downstream service time to recover.

| #57 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-056 | |
| **Used by:** | DPT-064, DPT-065 | |
| **Related:** | DPT-056, DPT-060, DPT-086, DPT-089 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT CIRCUIT BREAKER:**
Payment Service is down. Every incoming order request:
1. Calls Payment Service → waits for timeout (30s)
2. Timeout fires → returns error
3. User gets error after 30s

At 1,000 req/sec: 1,000 × 30s wait = every thread in
the service is waiting for Payment Service to time out.
The service is effectively down for ALL operations.

**COST OF FAILING SLOWLY:**
- Users wait 30 seconds for an error (terrible UX)
- Threads are held for 30 seconds (resource exhaustion)
- The failing downstream is hammered with 1,000 req/sec
  that it cannot handle (making recovery harder)
- Cascading failure: Service A blocks, its callers block,
  their callers block

**THE INVENTION MOMENT:**
After enough failures, stop trying. Return an error
IMMEDIATELY. Let the downstream rest. Try again
periodically. This is "fail fast" applied systematically.

---

### 📘 Textbook Definition

The **Circuit Breaker Pattern** (popularized by Michael
Nygard in "Release It!", 2007) is a resilience pattern
that wraps a function call in a circuit breaker object
that monitors for failures. The circuit breaker has
three states:

**CLOSED (normal operation):**
Calls pass through to the downstream service.
Failures are counted. While failure rate < threshold:
circuit stays closed.

**OPEN (failing downstream):**
When failure rate exceeds threshold: circuit opens.
All calls immediately return an error (no downstream
call made). The downstream is not called. Callers get
fast failure. The downstream gets a rest.

**HALF-OPEN (recovery probe):**
After a configured wait period: the circuit enters
half-open. A limited number of test calls are allowed
through to probe the downstream. If they succeed:
circuit closes. If they fail: circuit opens again.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Circuit Breaker = after N failures, stop calling the
failing service until it recovers.

**One analogy:**
> An electrical circuit breaker: when current exceeds
> the limit (too much load, short circuit), the breaker
> trips. Power stops. The electrical system is protected
> from overload. After the problem is fixed, reset the
> breaker; power resumes.
>
> Software circuit breaker: when errors exceed the
> threshold (downstream is failing), the breaker opens.
> Calls stop. The downstream gets rest. After a wait
> period, a test call probes recovery. If successful:
> circuit closes; calls resume.

**One insight:**
Circuit Breaker + Bulkhead are the two core resilience
patterns. Bulkhead: isolates SLOW services (containment).
Circuit Breaker: stops calling FAILING services (fail fast).
Combined: complete resilience strategy. Without both:
one upstream slowdown or failure can take down an entire
service mesh.

---

### 🔩 First Principles Explanation

**STATE MACHINE:**
```
CLOSED → (error rate > threshold) → OPEN
OPEN   → (wait duration elapsed)  → HALF-OPEN
HALF-OPEN → (probe succeeds)      → CLOSED
HALF-OPEN → (probe fails)         → OPEN
```

**FAILURE COUNTING:**
Modern circuit breakers (Resilience4j) use a sliding
window approach:
- **Count-based window**: last N calls. If X% failed: open.
- **Time-based window**: last N seconds. If X% failed: open.

Example: "In the last 10 calls, if 50% failed: open."
or: "In the last 60 seconds, if 50% failed: open."

**SLOW CALL DETECTION:**
Circuit breakers also count slow calls (calls exceeding
a duration threshold) as failures. A call that takes
30s and eventually succeeds may be as damaging as a
call that fails immediately.

**HALF-OPEN PROBING:**
After the wait period, the circuit allows a limited
number of calls through (e.g., 3 calls). If 2/3 succeed:
the circuit closes (downstream recovered). This prevents
immediately flooding a recovering downstream with full
traffic.

---

### 🧪 Thought Experiment

**CASCADING FAILURE PREVENTION:**

**Without Circuit Breaker:**
Payment Service fails. Service A continues calling it.
Service A threads block for 30s each. Service A's
callers (API Gateway) time out waiting for Service A.
API Gateway threads exhaust. All user-facing endpoints
fail. Total outage.

**With Circuit Breaker:**
Payment Service fails. Service A calls it 10 times.
50% fail. Circuit opens. Service A's payment calls
immediately return an error (no wait). Order flow fails
fast (good UX: user gets error in 10ms, not 30s).
Service A's threads are not blocked. Inventory and
other services: unaffected. Partial degradation only
(payment is down, rest works).

After 60 seconds: circuit enters half-open. 3 probe
calls succeed. Circuit closes. Payment calls resume.

---

### 🧠 Mental Model / Analogy

> Circuit Breaker = "self-service checkout" model.
> A store has 10 self-service checkouts.
> Checkout #3 malfunctions: every customer who tries
> it gets stuck. Checkout #3 has a red light (open circuit).
> Manager notices: "Don't use #3." Customers immediately
> redirect to working checkouts. After repair, manager
> tests #3 with one customer (half-open). If it works:
> "All clear" (closed). If it fails again: light stays red.
>
> Without the red light: every customer tries #3,
> gets stuck, and slows the entire store.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
Circuit Breaker watches how many times a service call
fails. If too many fail in a row (or within a time window),
it stops calling the service and immediately returns
an error instead. After some time, it tries again.

**Level 2 - How to use Resilience4j:**
```java
@CircuitBreaker(name = "payment-service",
                fallbackMethod = "paymentFallback")
PaymentResult charge(PaymentRequest req) { ... }
```
Configure in application.yml: failure rate threshold,
wait duration, sliding window size.

**Level 3 - Fallback strategies:**
When the circuit is open, what should the caller do?
Options:
- Return a default value (neutral response)
- Return a cached previous result
- Queue the request for retry when circuit closes
- Return an informative error (fail gracefully)
The right fallback depends on the operation's criticality.

**Level 4 - Circuit Breaker in distributed systems:**
In a service mesh (Istio, Linkerd), circuit breaking
can be implemented at the infrastructure level without
code changes. Envoy proxy detects outlier instances
and removes them from the load balancer pool (passive
health checking). This is circuit breaking at the instance
level. Application-level circuit breakers (Resilience4j)
complement this with per-service semantic circuit breaking.

**Level 5 - Metrics and alerting:**
A circuit breaker that opens in production is a critical
signal. Alert on circuit breaker state transitions:
```
CLOSED → OPEN: page the on-call engineer
OPEN → HALF-OPEN: log informational
HALF-OPEN → OPEN: re-alert (recovery attempt failed)
```
Circuit breaker metrics in dashboards: state, failure
rate, slow call rate, calls per second. A circuit breaker
that oscillates between OPEN and HALF-OPEN indicates
a flapping downstream: investigate root cause.

---

### ⚙️ How It Works (Mechanism)

```
Circuit Breaker State Machine
┌─────────────────────────────────────────────────────────┐
│                                                         │
│         ┌──────────────────────────────────┐           │
│         │         CLOSED                   │           │
│         │  (calls pass through normally)   │           │
│         │  Count failures in window        │           │
│         └──────────────┬───────────────────┘           │
│                        │ failure_rate > 50%             │
│                        ▼                                │
│         ┌──────────────────────────────────┐           │
│         │          OPEN                    │           │
│         │  (calls REJECTED immediately)    │           │
│         │  Downstream gets rest            │           │
│         │  Wait 60 seconds...              │           │
│         └──────────────┬───────────────────┘           │
│                        │ 60s elapsed                    │
│                        ▼                                │
│         ┌──────────────────────────────────┐           │
│         │        HALF-OPEN                 │           │
│         │  Allow 3 probe calls through     │           │
│         └──────┬───────────────────┬───────┘           │
│                │ 2/3 succeed       │ 2/3 fail           │
│                ▼                   ▼                    │
│            CLOSED              OPEN again               │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Without Circuit Breaker (fails slowly):**

```java
// BAD: No circuit breaker
// When payment service is down: 30s timeout per call
// Threads exhausted → entire service down

@Service
class PaymentClient {
    @Autowired RestTemplate restTemplate;

    public PaymentResult charge(PaymentRequest req) {
        // If payment service is down: waits 30s then fails
        return restTemplate.postForObject(
            "http://payment-service/charge",
            req, PaymentResult.class);
    }
}
```

**Example 2 - Resilience4j Circuit Breaker:**

```java
// GOOD: Circuit Breaker with Resilience4j

// application.yml:
/*
resilience4j:
  circuitbreaker:
    instances:
      payment-service:
        failureRateThreshold: 50        # Open if 50%+ fail
        slowCallRateThreshold: 80       # Also count slow calls
        slowCallDurationThreshold: 5s   # Calls >5s are "slow"
        slidingWindowSize: 10           # Last 10 calls
        minimumNumberOfCalls: 5         # Min calls before evaluation
        waitDurationInOpenState: 60s    # Wait 60s before HALF-OPEN
        permittedNumberOfCallsInHalfOpenState: 3 # Probe calls
        registerHealthIndicator: true
*/

@Service
class PaymentClient {

    @CircuitBreaker(name = "payment-service",
                    fallbackMethod = "paymentFallback")
    public PaymentResult charge(PaymentRequest req) {
        return restTemplate.postForObject(
            "http://payment-service/charge",
            req, PaymentResult.class);
    }

    // Fallback: called when circuit is OPEN or when call fails
    public PaymentResult paymentFallback(
            PaymentRequest req, Throwable ex) {
        log.warn("Payment circuit open or failed: {}",
            ex.getMessage());
        // Graceful degradation: queue for retry or return "pending"
        pendingPaymentQueue.enqueue(req);
        return PaymentResult.pending(req.getOrderId());
    }
}
```

**Example 3 - Monitoring circuit breaker state:**

```java
// Listen to circuit breaker events (for alerting)
@Component
class CircuitBreakerEventListener {

    @Autowired CircuitBreakerRegistry registry;
    @Autowired AlertService alerts;

    @PostConstruct
    void registerListeners() {
        registry.circuitBreaker("payment-service")
            .getEventPublisher()
            .onStateTransition(event -> {
                CircuitBreakerTransitionEvent transition =
                    (CircuitBreakerTransitionEvent) event;
                if (transition.getStateTransition().getToState()
                        == CircuitBreaker.State.OPEN) {
                    // Circuit opened: page on-call
                    alerts.critical("Payment circuit OPEN: " +
                        transition.getCircuitBreakerName());
                }
            });
    }
}
```

---

### ⚖️ Circuit Breaker Configuration Guide

| Parameter | Too Low | Too High | Suggested |
|---|---|---|---|
| failureRateThreshold | Opens on normal noise | Misses real failures | 50% |
| slidingWindowSize | Opens too quickly | Slow to detect | 10-20 |
| waitDurationInOpenState | No rest for downstream | Long outage window | 30-120s |
| minimumNumberOfCalls | Opens on 1 failure | Needs too many calls to trigger | 5-10 |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Circuit Breaker prevents failures | Circuit Breaker prevents cascading failures. It does not fix the underlying issue. The payment service is still down. Circuit Breaker just stops spreading the damage |
| Half-open state is automatic | In Resilience4j and most libraries, HALF-OPEN transition happens automatically after the configured wait duration. No manual intervention needed |
| One circuit breaker per application | One circuit breaker per DOWNSTREAM DEPENDENCY. An application calling 5 services should have 5 circuit breakers, each independently configured for that service's characteristics |
| Retry + Circuit Breaker are redundant | They are complementary. Retry: retry a transient failure on the SAME call (short-term, fast). Circuit Breaker: stop calling a service that is persistently failing (medium-term, preserve resources). Use both with the rule: retry WITHIN the circuit breaker |

---

### 🚨 Failure Modes & Diagnosis

**Circuit Oscillating (Open/Half-Open/Open Repeatedly)**

**Symptom:**
Circuit breaker for the payment service alternates between
OPEN and HALF-OPEN every minute. Payment service appears
to recover briefly, then fail again.

**Root Cause:**
The payment service is overloaded. When the circuit opens,
the downstream load drops, it partially recovers. When
half-open probe calls succeed, the circuit closes and
full traffic hits the downstream, overwhelming it again.

**Diagnosis:**
Check payment service CPU/memory during half-open
transitions. Check error rate as traffic resumes.
The circuit closes → error rate jumps → circuit re-opens
indicates capacity issue.

**Fix:**
Introduce gradual traffic restoration (half-open should
send 5% of traffic, not 100%). Add rate limiting at
the payment service. Scale the payment service horizontally.

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ STATES       │ CLOSED (calls pass) → OPEN (calls        │
│              │ rejected) → HALF-OPEN (probe) → CLOSED   │
├──────────────┼──────────────────────────────────────────┤
│ OPENS WHEN   │ Failure rate > threshold in window       │
│              │ OR slow call rate > threshold            │
├──────────────┼──────────────────────────────────────────┤
│ LIBRARY      │ Resilience4j: @CircuitBreaker annotation │
│              │ Configure thresholds in application.yml  │
├──────────────┼──────────────────────────────────────────┤
│ FALLBACK     │ Default value / cached result / queue    │
│              │ for retry / graceful error               │
├──────────────┼──────────────────────────────────────────┤
│ WITH BULKHEAD│ Circuit Breaker: stop calling failing svc│
│              │ Bulkhead: isolate slow service resources │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-058: Sidecar Pattern                 │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Circuit Breaker: CLOSED → OPEN (after N% failures)
   → HALF-OPEN (probe) → CLOSED or OPEN again. When
   OPEN: calls fail immediately (no downstream call).
   Fast failure, not slow timeout. Downstream gets rest.
2. Resilience4j: `@CircuitBreaker(name="payment-service",
   fallbackMethod="paymentFallback")`. Configure threshold,
   window, and wait duration per downstream.
3. Circuit Breaker + Bulkhead = complete resilience.
   Circuit Breaker stops failed-service calls. Bulkhead
   isolates slow-service resources. Use both.

