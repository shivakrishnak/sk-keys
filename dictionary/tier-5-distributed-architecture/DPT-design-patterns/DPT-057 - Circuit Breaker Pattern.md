---
layout: default
title: "Circuit Breaker Pattern"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 57
permalink: /design-patterns/circuit-breaker-pattern/
id: DPT-057
category: Design Patterns
difficulty: ★★★
depends_on:
used_by:
related:
tags:
  - pattern
  - distributed
  - deep-dive
  - microservices
  - reliability
status: complete
version: 1
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
---

# DPT-057 - Circuit Breaker Pattern

⚡ TL;DR - The Circuit Breaker Pattern stops calling a failing service automatically, allows it time to recover, and resumes calls cautiously - preventing cascade failures and reducing load on a struggling service.

| DPT-057 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Design Patterns, Bulkhead Pattern, Retry Pattern, Resilience, Distributed Systems | |
| **Used by:** | Microservices, System Design, Resilience Engineering, Service Mesh | |
| **Related:** | Bulkhead Pattern, Retry Pattern, Timeout, Fallback Strategy, Resilience4j | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Service A calls Service B for every request. Service B becomes slow (10-second timeouts instead of 100ms). Every incoming request to Service A now blocks a thread for 10 seconds waiting for Service B. With 100 concurrent users, all threads are blocked within seconds. Service A's response time explodes from 100ms to 10+ seconds. The slowness of B cascades into a failure of A - and if other services depend on A, the cascade continues. This is the "cascading failure" problem that brought down major services including Netflix, Amazon, and Twitter historically.

**THE BREAKING POINT:**
Without intervention, every call to a failing service consumes resources (threads, connections) that could serve healthy requests. The service hammers the already-struggling B with more requests, potentially preventing B from recovering. The entire dependent graph fails.

**THE INVENTION MOMENT:**
Michael Nygard introduced the Circuit Breaker pattern in "Release It!" (2007), named after the electrical circuit breaker that trips (opens) when too much current flows, protecting the circuit from damage. The software circuit breaker stops sending requests to a failing dependency when failure rate exceeds a threshold, allowing the dependency to recover while protecting the caller.

**EVOLUTION:**
Circuit Breaker Pattern was named and popularised by Michael
Nygard in "Release It!" (2007), inspired by electrical circuit
breakers. Netflix Hystrix (2012) made it the default resiliency
pattern for Java microservices, with a dashboard for real-time
monitoring. Hystrix was deprecated in 2018 due to maintenance
burden, and Resilience4j became the successor. Service mesh
implementations (Istio, Linkerd) moved circuit breaking to the
infrastructure layer using Envoy proxy, making application-level
circuit breaker code less necessary in mesh-enabled environments.
AWS App Mesh and Azure Front Door embed circuit breaking in
managed load balancers.

---

### 📘 Textbook Definition

The Circuit Breaker Pattern is a resilience pattern that monitors calls to a remote service and tracks the success/failure rate over a time or count window. When the failure rate exceeds a configured threshold (e.g., 50% failures in the last 10 calls), the circuit "trips" to the **Open** state - subsequent calls immediately return a fallback or error without attempting to contact the remote service. After a configured wait period, the circuit transitions to **Half-Open**, allowing a limited number of probe requests through to check if the service has recovered. If probes succeed, the circuit closes and normal traffic resumes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Stop calling a broken service automatically, wait for it to recover, then cautiously resume.

**One analogy:**
> An electrical circuit breaker trips when too much current flows, cutting power to protect the circuit. You do not keep sending current through a broken wire - you wait, fix the problem, then reset the breaker and carefully restore power. The software Circuit Breaker does the same: when too many calls fail, it trips open, stops sending requests, waits, then probes with a few test calls before fully re-closing.

**One insight:**
A Circuit Breaker does two things simultaneously: it protects the caller (no threads blocked on a failing service) and it protects the callee (reduced load gives the failing service time to recover). Without the Circuit Breaker, callers bombard an already-struggling service with retries, potentially making recovery impossible.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The circuit has three states: Closed (normal), Open (tripped, failing fast), Half-Open (testing recovery).
2. The transition from Closed to Open is triggered by a failure threshold (e.g., failure rate > 50% in a sliding window).
3. The transition from Open to Half-Open is time-based (wait duration expires); from Half-Open to Closed is based on probe success (N consecutive successes close the circuit).

**DERIVED DESIGN:**
The sliding window is the detection mechanism. It tracks calls (count-based window: last N calls) or time (time-based window: last T seconds). The circuit calculates failure rate within the window. When failure rate crosses the threshold, the circuit opens. This is more nuanced than a simple binary up/down check - it handles degraded services (some successes, some failures) by setting threshold (e.g., trip if > 50% of last 100 calls fail).

Half-Open state is the recovery probe. Rather than abruptly switching from full rejection to full traffic, Half-Open allows a small number of test requests to confirm the service has actually recovered. This prevents oscillation (circuit rapidly opening/closing if the service is flapping).

**THE TRADE-OFFS:**
**Gain:** Cascade failure prevention; reduced load on failing service; fast failure (no waiting for timeout); self-healing via state transitions.
**Cost:** False tripping (circuit opens when service is actually healthy during a traffic spike); configuration complexity (thresholds, windows, wait durations); requires fallback implementation.

---

### 🧪 Thought Experiment

**SETUP:**
Service A calls Payment B for every order. Payment B has a 500ms SLA. A network issue causes 80% of calls to B to fail with connection errors.

**WHAT HAPPENS without Circuit Breaker:**
80% of order requests fail at B after the 500ms timeout. The failing 80% hold threads for 500ms each. At 100 req/sec, 80 threads are blocked for 500ms each. Thread pool fills. Remaining 20% of successful calls also queue behind the failing threads. Healthy order placements slow down due to thread contention. Service A appears degraded even for orders that would have succeeded. B continues to receive all 100 req/sec, maintaining its overload.

**WHAT HAPPENS with Circuit Breaker:**
First 10 calls to B: 8 fail (80%). Failure rate = 80%, threshold = 50%. Circuit opens. Calls 11-100: immediate error responses (no calling B). Fallback invoked. B receives 0 req/sec - it gets breathing room to recover. After 10s wait (half-open), probe requests are sent: 3 of 5 succeed. Circuit closes. Normal traffic resumes (B has recovered).

**THE INSIGHT:**
The Circuit Breaker is a self-healing mechanism. It monitors, trips, waits, probes, and re-closes - all automatically. The service recovers without operator intervention because the Circuit Breaker reduced the load during the recovery window.

---

### 🧠 Mental Model / Analogy

> Think of a dam's overflow gate. Normally, the gate is closed (circuit closed) and water flows normally through controlled channels. When the river level rises too fast (failure rate increases), the gate opens automatically (circuit trips open), diverting water to a safe outlet (fallback). The main channel gets no water and recovers. After the flood subsides (wait period), the gate slowly closes to test if the river is safe again (half-open probe). If stable, the gate fully closes and normal flow resumes.

- "Gate closed" → circuit Closed (normal operation)
- "River level rises" → failure rate increases in the window
- "Gate opens (overflow)" → circuit Opens (trips)
- "Safe outlet" → fallback method
- "Wait for flood to subside" → wait duration before half-open
- "Slowly testing flow" → half-open probe calls

Where this analogy breaks down: a dam gate manages water volume. A circuit breaker manages call *rate* and *failure rate*, not raw volume. High call volume with low failure rate does not trip the circuit.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A circuit breaker monitors whether calls to a service are failing. When too many fail, it stops making calls and returns an immediate error instead of waiting. After waiting a bit, it tests if the service has recovered. It's like a fuse that blows when something is wrong, then resets automatically.

**Level 2 - How to use it (junior developer):**
In Spring with Resilience4j: annotate the method calling the remote service with `@CircuitBreaker(name="payment", fallbackMethod="paymentFallback")`. Implement `paymentFallback` to return a user-friendly error or cached value. Configure the thresholds in `application.yml`. The Circuit Breaker handles state transitions automatically. Test with integration tests that simulate failures to confirm the circuit trips at the configured threshold.

**Level 3 - How it works (mid-level engineer):**
Resilience4j's count-based window counts the last N calls and calculates failure rate. Time-based window counts failures in the last T seconds (sliding window in 1-second buckets). Key configurations: `failureRateThreshold` (50%: trip if > 50% fail), `slidingWindowSize` (N calls or T seconds), `waitDurationInOpenState` (how long to stay open), `permittedNumberOfCallsInHalfOpenState` (probe call count), `minimumNumberOfCalls` (don't trip until at least N calls have been made - prevents false tripping on startup). Metrics exposed: `resilience4j.circuitbreaker.state` (CLOSED/OPEN/HALF_OPEN), `resilience4j.circuitbreaker.failure.rate`.

**Level 4 - Why it was designed this way (senior/staff):**
The Circuit Breaker is a feedback loop. It observes the system, changes its behaviour when the system degrades, and observes the effect of that change - automatically. This is the same principle as a proportional-integral controller. The state machine (Closed → Open → Half-Open → Closed) is carefully designed to prevent common failure modes: minimum call count prevents false tripping; wait duration prevents retry storms; Half-Open prevents oscillation. At the service mesh level (Istio, Envoy), Circuit Breakers are implemented in the proxy sidecar rather than in application code (Resilience4j). This is architecturally cleaner - the application code is not polluted with resilience logic - but it removes fine-grained control from the application developer. The correct level of implementation is a team and architectural decision.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│  CIRCUIT BREAKER STATE MACHINE                       │
│                                                      │
│          normal operation                            │
│     ┌──────────────────────────┐                     │
│     │        CLOSED            │                     │
│     │  (calls pass through)    │                     │
│     └───────────┬──────────────┘                     │
│                 │ failure rate > threshold             │
│                 ▼                                     │
│     ┌──────────────────────────┐                     │
│     │         OPEN             │                     │
│     │  (calls fail fast)       │                     │
│     │  (fallback invoked)      │                     │
│     └───────────┬──────────────┘                     │
│                 │ wait duration expires               │
│                 ▼                                     │
│     ┌──────────────────────────┐                     │
│     │       HALF-OPEN          │◄──────── probes fail│
│     │  (N probe calls allowed) │         → OPEN      │
│     │  (test if service healed)│                     │
│     └───────────┬──────────────┘                     │
│                 │ probes succeed                      │
│                 │ (N consecutive successes)           │
│                 ▼                                     │
│                CLOSED (resume normal)                 │
└──────────────────────────────────────────────────────┘
```

**State transitions summarised:**
- CLOSED → OPEN: failure rate in sliding window > threshold
- OPEN → HALF-OPEN: wait duration expires (automatic)
- HALF-OPEN → CLOSED: probe calls succeed
- HALF-OPEN → OPEN: probe calls fail

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (CLOSED):**
```
Client → Service A → CircuitBreaker(CLOSED) [← YOU ARE HERE]
  → Service B (payment)
  → Payment success
  → CircuitBreaker records success
  → Return result to client
```

**FAILURE FLOW (circuit opens):**
```
Client → Service A → CircuitBreaker(CLOSED→OPEN)
  Failure rate exceeds threshold
  Circuit OPENS
Client → Service A → CircuitBreaker(OPEN)
  [← YOU ARE HERE: short circuit]
  → BulkheadFullException bypassed (no call to B)
  → paymentFallback() invoked
  → Return: "Payment unavailable - try later"
  (B receives 0 calls - gets recovery time)
```

**RECOVERY FLOW (half-open to closed):**
```
WaitDuration expires
  → Circuit → HALF-OPEN
  → 5 probe calls sent to B
    → 4/5 succeed (80% success)
    → healthRateThreshold met
  → Circuit → CLOSED
  → Normal traffic resumes
```

**WHAT CHANGES AT SCALE:**
At 100 req/sec, a circuit breaker with a 10-call window trips within 100ms of exceeding the threshold. At 100,000 req/sec, a 10-call window may trip on a 1ms blip. Use time-based windows (30s sliding window) for high-volume services. At the service mesh level, Circuit Breakers at the Envoy proxy level protect entire service-to-service traffic without application code changes.

---

### 💻 Code Example

**Example 1 - Basic Circuit Breaker with Resilience4j:**

```java
@Service
public class PaymentService {
    private final PaymentGateway gateway;

    // @CircuitBreaker applies CB to this method
    // fallbackMethod invoked when CB is OPEN or call fails
    @CircuitBreaker(name = "payment",
                    fallbackMethod = "paymentFallback")
    public PaymentResult processPayment(Order order) {
        return gateway.charge(
            order.total(), order.paymentToken());
    }

    // Fallback: invoked when circuit is open or call fails
    private PaymentResult paymentFallback(
            Order order,
            Exception ex) {
        log.warn("Payment circuit open for order {}",
            order.id(), ex);
        // Option 1: Queue for later processing
        paymentQueue.enqueue(order);
        return PaymentResult.deferred(order.id());
    }
}
```

**Example 2 - Configuration (application.yml):**

```yaml
resilience4j:
  circuitbreaker:
    instances:
      payment:
        # Trip if > 50% of calls fail
        failureRateThreshold: 50
        # Count-based sliding window of 10 calls
        slidingWindowType: COUNT_BASED
        slidingWindowSize: 10
        # Wait 10s in OPEN before moving to HALF-OPEN
        waitDurationInOpenState: 10s
        # Send 5 probes in HALF-OPEN state
        permittedNumberOfCallsInHalfOpenState: 5
        # Don't trip until at least 5 calls made
        minimumNumberOfCalls: 5
        # Also trip on slow calls > 2s (slowCallDuration)
        slowCallDurationThreshold: 2000
        slowCallRateThreshold: 80
```

**Example 3 - Monitoring circuit state:**

```bash
# Check circuit breaker state via Spring Actuator:
curl -s http://localhost:8080/actuator/health \
  | jq '.components.circuitBreakers.details'
# Or metrics:
curl -s http://localhost:8080/actuator/metrics \
  /resilience4j.circuitbreaker.state \
  | jq '.measurements[].value'
# 0 = CLOSED, 1 = OPEN, 2 = HALF_OPEN

# Prometheus query for alerting:
# Alert when circuit is OPEN > 30s:
# resilience4j_circuitbreaker_state{name="payment"} == 1
```

---

### ⚖️ Comparison Table

| Pattern | when it acts | What it does | State | Best For |
|---|---|---|---|---|
| **Circuit Breaker** | After failure threshold | Stops calling failing service | Stateful (3 states) | Service recovery protection |
| Bulkhead | Always | Limits concurrent calls | Resource pool | Blast radius limitation |
| Retry | After each failure | Retries the call | Stateless | Transient failures |
| Timeout | Per call | Limits call duration | Stateless | Bounding individual call time |
| Rate Limiter | Always | Limits call rate | Stateful (quota) | Overload prevention |

How to choose: use Circuit Breaker + Bulkhead + Retry as a combination. Circuit Breaker detects and trips. Bulkhead limits resource exhaustion during the detection window. Retry handles individual transient failures before the circuit trips. Don't use Retry without a Circuit Breaker - retries on a tripped circuit make the failing service worse.

---

### 🔁 Flow / Lifecycle

```
┌──────────────────────────────────────────────────────┐
│  SLIDING WINDOW CALCULATION                          │
│                                                      │
│  Count-based window (size=10):                       │
│  [S S S S S F F F F F] = 50% failure → trip          │
│   ↑ oldest         ↑ newest                          │
│                                                      │
│  Time-based window (30s):                            │
│  [30s period: 100 calls, 60 failures] = 60% → trip   │
│                                                      │
│  SLOW CALL tracking (also triggers trip):            │
│  Call duration > slowCallDurationThreshold AND       │
│  slowCallRateThreshold % of calls are slow → trip    │
└──────────────────────────────────────────────────────┘
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Circuit Breaker prevents failures | Circuit Breaker prevents cascading failures - the original failure still occurs. It protects the caller and the callee from amplified damage |
| Open circuit = service is down | Open circuit = failure rate threshold exceeded. The service may be partially degraded (some calls succeed), not fully down |
| Circuit Breaker and retry are redundant | They solve different problems: Retry handles transient individual failures; Circuit Breaker handles sustained failure patterns. Use both |
| Circuit Breaker should trip on any failure | Set `minimumNumberOfCalls` to prevent tripping on startup or low-traffic periods. A single failure should not trip the circuit |
| Half-Open sends full traffic | Half-Open sends only `permittedNumberOfCallsInHalfOpenState` probes. Full traffic only resumes after successful probes close the circuit |

---

### 🚨 Failure Modes & Diagnosis

**1. Circuit Trips Too Aggressively (False Positives)**

**Symptom:** Circuit opens frequently during traffic spikes or deployment restarts. Downstream service is healthy, but the circuit is oscillating between CLOSED and OPEN.

**Root Cause:** `slidingWindowSize` too small, `minimumNumberOfCalls` too low, or `failureRateThreshold` too sensitive.

**Diagnostic:**
```bash
# Monitor circuit state changes:
kubectl logs deployment/order-service \
  | grep "circuitbreaker\|OPEN\|CLOSED\|HALF_OPEN" \
  | tail -50
# Frequent state changes = misconfiguration

# Check failure rate metric:
curl http://localhost:8080/actuator/metrics \
  /resilience4j.circuitbreaker.failure.rate
```

**Fix:** Increase `slidingWindowSize` (100 rather than 10); increase `minimumNumberOfCalls` (20-30); consider time-based window for high-volume services.

**Prevention:** Load test the Circuit Breaker configuration at expected peak traffic before production deployment.

---

**2. Circuit Stays Open After Service Recovery**

**Symptom:** Downstream service has recovered (direct health check passes), but Circuit Breaker stays OPEN and client cannot reach it.

**Root Cause:** `waitDurationInOpenState` is too long, or Half-Open probes are failing due to a transient error during the probe window.

**Diagnostic:**
```bash
# Check current circuit state and time in state:
curl http://localhost:8080/actuator/metrics \
  /resilience4j.circuitbreaker.not.permitted.calls
# High not-permitted count = circuit still open

# Force transition to HALF-OPEN (emergency, dev only):
curl -X POST http://localhost:8080/actuator \
  /circuitbreakers/payment/transitionToHalfOpenState
```

**Fix:** Reduce `waitDurationInOpenState`. Ensure `permittedNumberOfCallsInHalfOpenState` probes represent a reliable sample.

**Prevention:** Tune `waitDurationInOpenState` based on the downstream service's median recovery time. Too long = extended unnecessary outage.

---

**3. Retry + Circuit Breaker Causing Retry Storms**

**Symptom:** Circuit closes briefly, traffic surges (backed-up retried requests), circuit immediately re-opens. System oscillates.

**Root Cause:** Retry logic fires on circuit close, simultaneously sending all backed-up requests. The burst exceeds the downstream's capacity, causing immediate re-failure.

**Diagnostic:**
```bash
# Check retry attempt count vs. success:
curl http://localhost:8080/actuator/metrics \
  /resilience4j.retry.calls
# High retry count immediately after circuit close = storm
```

**Fix:** Add exponential backoff + jitter to retry logic. Ensure retry count is bounded. Put Circuit Breaker outside the Retry in the decorator chain - Circuit Breaker trips after N retried failures, not N individual failures.

**Prevention:** Use Resilience4j decorator chain: Retry(CircuitBreaker(Bulkhead(function))). Circuit Breaker detects patterns across retried calls.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Bulkhead Pattern` - the complementary isolation pattern; Bulkhead limits resource exhaustion while the Circuit Breaker detects failure patterns; both are needed for full resilience
- `Retry Pattern` - the pattern used alongside Circuit Breaker; Retries handle individual transient failures; Circuit Breaker handles sustained failure patterns

**Builds On This (learn these next):**
- `Resilience4j` - the Java implementation library for Circuit Breaker, Bulkhead, Retry, and Timeout; understanding the library is required to configure Circuit Breaker correctly
- `Service Mesh (Istio/Envoy)` - mesh-level circuit breaking implemented in the proxy sidecar, removing the need for application-level circuit breaker code

**Alternatives / Comparisons:**
- `Timeout` - the simpler alternative: timeout every call to bound its duration. Less sophisticated than Circuit Breaker - does not detect patterns or stop traffic proactively
- `Rate Limiting` - limits call rate to prevent overload; complementary to Circuit Breaker but does not respond to failure rate

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ State machine that stops calling a        │
│              │ failing service and resumes cautiously    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Slow/failing service blocks threads and   │
│ SOLVES       │ cascades failure to all dependents        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ 3 states: CLOSED (normal) → OPEN (fail    │
│              │ fast) → HALF-OPEN (probe) → CLOSED.       │
│              │ Automatic and self-healing.               │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Calling any remote service that can fail  │
│              │ slowly (timeout rather than immediate err)│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Calls are to local in-process resources   │
│              │ (no network boundary)                     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Cascade failure prevention + recovery     │
│              │ aid vs. false tripping + fallback         │
│              │ implementation required                   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A circuit breaker trips to protect the   │
│              │  circuit - then resets when it's safe."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Resilience4j → Bulkhead → Retry Pattern   │
│              │ → Service Mesh → Timeout Strategy         │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Fail fast when a dependency is known to be unavailable. Do
not allow slow or failing dependencies to consume resource
threads. Periodically probe the dependency for recovery and
restore traffic when healthy.

**Where else this pattern appears:**
- **Electrical circuit breakers:** The naming origin. An
  electrical fault causes high current; the breaker trips
  (OPEN), protecting the circuit. Manually reset (HALF-OPEN)
  to test if fault is cleared.
- **TCP connection timeout tuning:** OS TCP stack fast-detects
  broken connections and fails subsequent sends immediately
  rather than waiting for full TCP timeout -- a protocol-level
  circuit breaker.
- **Browser resource loading:** Browsers stop loading assets
  from a host that has returned errors for recent requests
  and switch to a "fail silently" mode -- a browser-level
  circuit breaker for CDN failures.

---

### 💡 The Surprising Truth

Netflix Hystrix, which popularised Circuit Breaker in Java
microservices and was used in production at Netflix for years,
was deprecated by Netflix in 2018 with this explanation: "Hystrix
is no longer in active development, and we are not accepting new
feature requests." The Netflix engineering blog stated they had
moved to "adaptive concurrency limits" (using TCP-congestion-
control-inspired algorithms) rather than static timeout and error
rate thresholds. The key insight: fixed thresholds require careful
tuning for every deployment environment; adaptive algorithms
self-tune based on observed latency. Circuit Breaker with fixed
thresholds is now considered a first-generation resiliency pattern.
---

### 🧠 Think About This Before We Continue

**Q1.** A payment service Circuit Breaker is configured with: `failureRateThreshold=50`, `slidingWindowSize=100`, `waitDurationInOpenState=30s`. It is Sunday at 2am - traffic is 5 req/min. The payment gateway has a 2-minute outage. Calculate: how many calls must be made before the circuit can trip? How long does it take to accumulate 100 calls at 5/min? Does the circuit trip during the 2-minute outage at 5 req/min? What configuration change would allow the circuit to protect the service at low-traffic periods?

*Hint: Look at the First Principles section for the core invariants and the Failure Modes section for where this scenario appears as a documented issue.*

**Q2.** A senior engineer proposes: "We should implement Circuit Breakers at the service mesh layer (Istio) rather than in application code (Resilience4j). This removes resilience logic from business code and standardises it across all services." A principal engineer counters: "Application-level circuit breaking is more granular - you can set different thresholds per method, not just per service, and you have access to application-specific context for fallback logic." Design a hybrid approach that gets the benefits of both: specify exactly which circuit breaking concerns belong at the mesh layer and which belong in application code.



*Hint: The Comparison Table and Level 3-4 explanations contain the mechanism that determines which approach wins in this scenario.*

**Q3 (Design Trade-off):** A Circuit Breaker has a threshold
of "50% errors in 10 seconds opens the circuit." A downstream
service is experiencing intermittent 5xx errors affecting 30%
of requests (below threshold). The service is degraded but not
circuit-breaking. Describe what is happening to the 30% failing
requests, the impact on user experience, and how to add partial
degradation handling for the period before the circuit opens.

*Hint: The Failure Modes section covers the "33% error rate
does not trip circuit" scenario. The combination of Circuit
Breaker + Retry + Fallback addresses the "degraded but not
open" state.*
