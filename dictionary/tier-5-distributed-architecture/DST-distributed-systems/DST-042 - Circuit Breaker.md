---
id: DST-042
title: "Circuit Breaker"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-041, DST-046
used_by: DST-043, DST-047, DST-048
related: DST-044, DST-043, DST-047, DST-046
tags:
  - distributed
  - reliability
  - pattern
  - resilience
  - advanced
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 42
permalink: /distributed-systems/circuit-breaker/
---

# DST-042 - Circuit Breaker

⚡ TL;DR - Circuit breaker wraps remote calls in a three-state machine (CLOSED → OPEN → HALF-OPEN) that automatically stops calling a failing dependency when the failure rate crosses a threshold, preventing cascade failures across service boundaries.

| Metadata        |                                    |     |
| :-------------- | :--------------------------------- | :-- |
| **Depends on:** | DST-041, DST-046                   |     |
| **Used by:**    | DST-043, DST-047, DST-048          |     |
| **Related:**    | DST-044, DST-043, DST-047, DST-046 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Service A calls Service B. Service B starts failing (DB overload, GC pause, memory leak). Service A retries, with 30-second socket timeouts. Each thread in Service A is now blocked for 30 seconds waiting for Service B. Service A has 200 thread-pool threads. All 200 are now waiting on Service B. No threads available for other requests. Service A is now effectively dead — even for operations that don't touch Service B. Service C calls Service A and gets no response. Service C's threads block. Cascade failure.

**THE BREAKING POINT:**
Michael Nygard documented the "thread pool death spiral" in _Release It!_ (2007): a cascade failure that took down an entire airline booking system because one third-party credit card processor started timing out. The fix was clear in retrospect: stop calling the failing service. But no automated mechanism existed to do this — engineers had to manually intervene to break the cascade.

**THE INVENTION MOMENT:**
Michael Nygard coined the Circuit Breaker pattern (2007) in _Release It!_, directly inspired by electrical circuit breakers: when current (requests) exceeds a safe threshold (failure rate too high), break the circuit (stop sending requests). The analogy is exact: an electrical circuit breaker protects wiring from overload; a software circuit breaker protects a service from overloading a failing dependency.

**EVOLUTION:**
2007: Nygard's _Release It!_ introduces the pattern. 2011: Netflix Hystrix — first major production circuit breaker library. 2018: Resilience4j replaces Hystrix (Hystrix deprecated 2018). 2019+: Service meshes (Istio, Linkerd) implement circuit breaking at the infrastructure layer (Envoy proxy). 2020: AWS App Mesh circuit breaking (outlier detection). Today: circuit breaker is standard in any multi-service architecture.

---

### 📘 Textbook Definition

**Circuit Breaker** is a stability pattern that wraps a protected function call with a state machine having three states: **CLOSED** (normal operation — all requests pass through), **OPEN** (all requests fail fast — dependency is presumed failed), **HALF-OPEN** (probe state — limited requests pass through to test if dependency recovered). **Transitions:** CLOSED → OPEN: failure rate exceeds threshold (e.g., > 50% failure in last 10 calls, or in sliding 10-second window). OPEN → HALF-OPEN: after a configurable wait time (e.g., 30 seconds). HALF-OPEN → CLOSED: probe requests succeed within threshold. HALF-OPEN → OPEN: probe requests fail. **Key metrics:** failure rate threshold (percentage), minimum call count to activate (avoid opening on 1 of 1 failures), sliding window type (count-based or time-based), wait duration in OPEN state.

---

### ⏱️ Understand It in 30 Seconds

**One line:** When a dependency fails too often, stop calling it and fail fast — then periodically probe to see if it recovered.

> A circuit breaker in software works exactly like one in your home's electrical panel. When too much current flows (too many failures): the breaker trips (OPEN state), cutting the circuit. No more current flows (no more requests) — protecting the wiring (your thread pool) from overheating. After a cooldown (wait_duration): you test the circuit (HALF-OPEN). If it holds: flip it back on (CLOSED).

**One insight:** The circuit breaker's value is not just protecting the failing service — it's protecting YOUR service. By failing fast instead of blocking, threads are released immediately for other work. You lose one capability but preserve all others.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Fail fast, not slow:** in OPEN state, requests must fail immediately (no timeout wait). The latency of a failed request goes from T_timeout (30s) to ~0ms (immediate exception).
2. **Self-healing:** circuit breaker must automatically attempt recovery (HALF-OPEN probe) after wait_duration. Manual intervention for every failure doesn't scale.
3. **Threshold-based, not all-or-nothing:** a single failure should not open the circuit. Minimum call count + failure rate threshold separates noise from genuine outage.
4. **State isolation:** circuit breaker state must be per-dependency (not global). Service A calling B and C should have separate circuit breakers — B failing should not affect C.

**DERIVED DESIGN:**

```
State machine:
  CLOSED: pass requests → track success/failure
    if failure_rate > threshold AND calls >= min_count:
      → OPEN
  OPEN: reject immediately (CallNotPermittedException)
    after wait_duration:
      → HALF-OPEN
  HALF-OPEN: allow max_test_calls through
    if success_rate > threshold: → CLOSED
    if failure_rate > threshold: → OPEN
```

**THE TRADE-OFFS:**
**Gain:** Thread pool protection (fail fast vs blocking). Cascade failure prevention. Automatic recovery (self-healing). Observability (state changes are measurable events).
**Cost:** Availability reduction when OPEN (even if dependency partially recovered). False OPEN (transient spike → circuit opens → healthy dependency marked as failed). Configuration complexity (which thresholds? which window?).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Any threshold-based state machine has the false positive problem — a brief traffic spike with high failure rate can trigger OPEN on a healthy service. This is fundamental to probabilistic failure detection.
**Accidental:** Hystrix's thread-pool-per-command model (heavyweight) vs Resilience4j's semaphore model (lightweight, virtual threads compatible). Implementation-level trade-off, not conceptual.

---

### 🧪 Thought Experiment

**SETUP:** Microservice Order API calls Inventory Service. Inventory Service database has a 2-minute outage. Order API has 100 threads, 30-second socket timeout.

**WITHOUT CIRCUIT BREAKER:**

- T=0: DB outage. Inventory Service starts timing out.
- T=0-30s: Each Order API thread blocks for 30 seconds on Inventory calls.
- T=30s: All 100 threads exhausted waiting. Order API hangs for ALL operations.
- T=2min: DB recovers. But now: 100 requests queued up. Thread pool depleted.
- User impact: ALL operations fail for 2+ minutes (cascade).

**WITH CIRCUIT BREAKER (failure_threshold=50%, min_calls=5, wait=30s):**

- T=0: DB outage. Inventory Service starts timing out.
- T=0-5 calls: 5 failures tracked. Circuit opens after failure_rate=100% (5/5 > 50%).
- T=5-35s: All Inventory calls fail immediately (0ms). No thread blocking.
- T=35s: HALF-OPEN. One probe call to Inventory. Still failing. → OPEN again.
- T=2min: DB recovers. T=2min+30s: probe succeeds. Circuit CLOSED.
- User impact: Inventory-dependent operations fail for 2 minutes. ALL OTHER operations continue (threads available). Massive improvement vs cascade.

**THE INSIGHT:** Circuit breaker converts a cascading total failure into an isolated partial failure. Users lose inventory operations — but they keep all other operations during the outage.

---

### 🧠 Mental Model / Analogy

> A circuit breaker is like a hospital triage system. During a mass casualty event: the triage nurse stops sending patients to an overwhelmed surgical team and diverts them to a fallback (other hospitals, field medics). She doesn't wait for each patient to be turned away — she proactively routes around the bottleneck. Every 30 minutes: she sends one patient to check if surgical capacity has recovered.

**Mapping:**

- **Triage nurse** → circuit breaker state machine
- **Surgical team overwhelmed** → dependency failing (OPEN state)
- **Diverting patients** → fail fast / fallback response
- **Sending one patient every 30 min** → HALF-OPEN probe
- **Surgical team recovers** → dependency recovers, circuit CLOSES

Where this analogy breaks down: a triage nurse makes qualitative decisions per patient (severity). A circuit breaker applies the same rule (fail fast) to ALL requests regardless of importance — there's no priority mechanism within the basic circuit breaker pattern (Bulkhead handles that).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A circuit breaker counts how often a remote service fails. When it fails too often: the circuit breaker "trips" — stops sending requests to that service and immediately says "service unavailable" without waiting. Every 30 seconds: it tries again. If the service recovered: back to normal. If still failing: back to tripped state.

**Level 2 - How to use it (junior developer):**
Resilience4j example:

```java
CircuitBreakerConfig config = CircuitBreakerConfig.custom()
  .failureRateThreshold(50)       // Open if ≥50% fail
  .slidingWindowSize(10)          // Count last 10 calls
  .waitDurationInOpenState(       // Wait 30s before probe
    Duration.ofSeconds(30))
  .permittedNumberOfCallsInHalfOpenState(3)
  .build();
CircuitBreaker cb = CircuitBreakerRegistry
  .of(config).circuitBreaker("inventory");
Callable<Inventory> decorated = CircuitBreaker
  .decorateCallable(cb, () -> inventoryService.get(id));
```

Monitor state: `cb.getState()`, `cb.getMetrics()`.

**Level 3 - How it works (mid-level engineer):**
Resilience4j uses a sliding window (count-based or time-based) to track failures. Count-based: last N calls. Time-based: calls in last N seconds. For each call: record success (exception=false) or failure (exception=true, or slow call exceeding slowCallDurationThreshold). When minimum calls met: calculate failure rate. If above threshold: transition to OPEN. OPEN state: calls throw `CallNotPermittedException` immediately (nanosecond latency). After wait_duration: transition to HALF-OPEN. In HALF-OPEN: permit `permittedNumberOfCallsInHalfOpenState` calls. Evaluate their results. Transition to CLOSED or OPEN.

**Level 4 - Why it was designed this way (senior/staff):**
The sliding window choice (count vs time) reveals a subtle design decision. Count-based: easy to reason about (last 10 calls). But under LOW TRAFFIC: 10 calls may span 10 minutes — a failure at T=0 keeps influencing the failure rate until T=10 minutes. Time-based window: more operationally accurate (last 10 seconds of calls). But under HIGH TRAFFIC: 10 seconds may include 10,000 calls — the window is computationally more expensive and the sample is more statistically robust. For APIs: time-based is usually better. For background tasks: count-based avoids false positives from sparse calls. The `minCallsThreshold` is equally important: without it, a cold start (1 failure out of 1 call = 100% failure rate) would immediately trip the circuit on ANY service at startup.

**Expert Thinking Cues:**

- "Circuit breaker OPEN even though service is healthy" → Check: is `minCallsThreshold` set? If not set (default=5): 3 failures out of 3 calls = 100% → OPEN. Under low traffic: spikes cause false opens. Increase minCalls or switch to time-based window with minimum call count. Also: check `slowCallRateThreshold` and `slowCallDurationThreshold` — slow calls (not exceptions) can also trigger OPEN.
- "Circuit breaker never opens even though service is failing" → Metric: `cb.getMetrics().getFailureRate()`. If < threshold: not enough failures. Check: are exceptions being recorded? Resilience4j only records exceptions that match the `recordExceptions` list. If service returns HTTP 503 as a successful response body (not an exception): failure not detected. Use `recordResultPredicate` to record HTTP-status-based failures.
- "Choosing between Resilience4j and Istio circuit breaking" → Resilience4j: application-level (per instance), configurable per method, works for non-HTTP protocols. Istio: infrastructure-level (per service), requires service mesh, works transparently without code changes. Use Istio for coarse-grained protection (all calls to a service). Use Resilience4j for fine-grained (per-method, per-tenant) circuit breaking.

---

### ⚙️ How It Works (Mechanism)

**State machine transitions:**

```
┌─────────────────────────────────────────────────┐
│  CLOSED (normal)                                │
│  Track calls in sliding window                  │
│  failure_rate ≥ threshold AND calls ≥ min?      │
│         │  YES                                  │
└─────────┼───────────────────────────────────────┘
          ▼
┌─────────────────────────────────────────────────┐
│  OPEN (fail fast)                               │
│  Reject all calls: CallNotPermittedException    │
│  After wait_duration:                           │
│         │                                       │
└─────────┼───────────────────────────────────────┘
          ▼
┌─────────────────────────────────────────────────┐
│  HALF-OPEN (probe)                              │
│  Allow max N test calls through                 │
│  success_rate ≥ threshold? → CLOSED             │
│  failure_rate ≥ threshold? → OPEN               │
└─────────────────────────────────────────────────┘
```

**Sliding window mechanics (count-based, N=10):**

```
Call 1:  OK  → window [OK]
Call 5:  FAIL → window [OK,OK,OK,OK,FAIL]
Call 10: FAIL → window [OK,OK,OK,FAIL,FAIL,
                         OK,OK,FAIL,FAIL,FAIL]
         failure_rate = 5/10 = 50%
         if threshold=50%: OPEN
```

---

### 🔄 The Complete Picture - End-to-End Flow

**CIRCUIT BREAKER PROTECTING INVENTORY CALL:**

```
OrderAPI  CircuitBreaker  InventoryService  Client
   │           │                │              │
   │◀─req──────────────────────────────────────│
   │─call()───▶│                │              │
   │           │─GET /inventory▶│              │
   │           │◀─503(error)────│              │
   │           │ (count failure in window)     │
   │ [after 5 failures, circuit OPENS]         │
   │◀─req──────────────────────────────────────│
   │─call()───▶│                │  ← YOU ARE HERE
   │           │ CallNotPermittedException
   │◀─fallback(empty inventory) │              │
   │───────────────────────────────────────────▶│
   │           │ [wait_duration=30s expires]   │
   │           │─HALF-OPEN: 1 probe─▶          │
   │           │◀─200 OK────────│              │
   │           │ CLOSED                        │
```

**WHAT CHANGES AT SCALE:**
At scale: multiple instances of OrderAPI each have their own circuit breaker — state is NOT shared (by default). Each instance independently decides to OPEN/CLOSE. Instance A may CLOSE (recovered) while Instance B stays OPEN (still detecting failures). This is correct: each instance sees its own sample of traffic. For coordinated state: use shared circuit breaker state (Consul/Redis-backed) — but adds latency and new SPOF.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Concurrent calls in HALF-OPEN state must be coordinated: allow exactly N probes, not N+ (otherwise: overwhelming the recovering service). Resilience4j uses an AtomicInteger counter + compareAndSet to limit concurrent HALF-OPEN calls.

---

### 💻 Code Example

**BAD - No protection: cascade failure on timeout:**

```java
// BAD: no circuit breaker
public Inventory getInventory(String itemId) {
    // Each call can block for 30s if service fails
    // 100 threads × 30s = thread pool exhausted
    return inventoryClient.get(itemId);
    // No protection: one slow service kills entire API
}
```

**GOOD - Resilience4j circuit breaker with fallback:**

```java
@Service
public class InventoryService {
    private final CircuitBreaker cb;
    private final InventoryClient client;

    public InventoryService(InventoryClient client) {
        this.client = client;
        CircuitBreakerConfig config =
            CircuitBreakerConfig.custom()
                .slidingWindowType(COUNT_BASED)
                .slidingWindowSize(10)
                .minimumNumberOfCalls(5)
                .failureRateThreshold(50.0f)
                .slowCallRateThreshold(50.0f)
                .slowCallDurationThreshold(
                    Duration.ofSeconds(2))
                .waitDurationInOpenState(
                    Duration.ofSeconds(30))
                .permittedNumberOfCallsInHalfOpenState(3)
                .recordExceptions(
                    IOException.class,
                    TimeoutException.class)
                .build();
        this.cb = CircuitBreakerRegistry
            .ofDefaults()
            .circuitBreaker("inventory", config);

        // Log state transitions:
        cb.getEventPublisher()
            .onStateTransition(event -> log.warn(
                "Circuit [{}] state: {} -> {}",
                "inventory",
                event.getStateTransition().getFromState(),
                event.getStateTransition().getToState()));
    }

    public Inventory getInventory(String itemId) {
        Callable<Inventory> decorated =
            CircuitBreaker.decorateCallable(
                cb, () -> client.get(itemId));

        return Try.ofCallable(decorated)
            .recover(CallNotPermittedException.class,
                ex -> cachedFallback(itemId))
            .recover(Exception.class,
                ex -> emptyInventory(itemId))
            .get();
    }

    private Inventory cachedFallback(String itemId) {
        // Return stale cached value or default
        return cache.getOrDefault(itemId,
            Inventory.empty(itemId));
    }
}
```

**How to verify circuit breaker behavior:**

```java
// Test: verify OPEN state under failures
@Test
void circuitBreakerOpensAfterThreshold() {
    // Arrange: mock service to fail
    when(client.get(any()))
        .thenThrow(new IOException("service down"));

    // Act: exceed minimum calls with 100% failure
    for (int i = 0; i < 5; i++) {
        service.getInventory("item-1");
    }

    // Assert: circuit is now OPEN
    assertThat(cb.getState())
        .isEqualTo(CircuitBreaker.State.OPEN);

    // Assert: next call uses fallback (not client)
    Inventory result = service.getInventory("item-1");
    assertThat(result).isEqualTo(Inventory.empty("item-1"));
    verify(client, times(5)).get("item-1");
    // Client not called on 6th+ attempt (fail fast)
}
```

---

### ⚖️ Comparison Table

| Pattern            | Purpose                      | Effect on caller     | Recovery                    |
| :----------------- | :--------------------------- | :------------------- | :-------------------------- |
| Circuit Breaker    | Stop calling failing service | Fail fast / fallback | Automatic (HALF-OPEN probe) |
| Retry (DST-044)    | Retry transient failures     | Increased latency    | Per-attempt                 |
| Timeout (DST-046)  | Bound wait time              | Fail after T_timeout | Per-call                    |
| Bulkhead (DST-043) | Isolate resource pools       | Reject excess        | Capacity-based              |
| Fallback (DST-047) | Alternative response         | Degraded response    | N/A (always active)         |

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                                                                                                                                                                                                           |
| :---------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Circuit breaker retries failed requests"             | Circuit breaker does NOT retry. It stops attempting to call the failing service. Retry (DST-044) is a separate pattern that retries immediately. They can be composed: retry 3 times within circuit breaker. If 3 retries all fail: counts as ONE failure against the circuit breaker's window.                                                                   |
| "Circuit breaker protects the downstream service"     | Circuit breaker primarily protects the CALLER's thread pool from exhaustion. Secondary benefit: fewer requests to the downstream service (giving it time to recover). Primary beneficiary: the calling service.                                                                                                                                                   |
| "Circuit breaker in OPEN state means service is down" | OPEN state means the CIRCUIT BREAKER has decided the service is likely failing — based on its local sample of calls. The service may have recovered but the circuit hasn't probed yet (wait_duration not elapsed). Or: the circuit opened due to a transient spike. OPEN != service_is_definitively_down.                                                         |
| "Hystrix and Resilience4j are equivalent"             | Hystrix (deprecated) uses thread-pool isolation per command — each remote call runs in a dedicated thread pool. Resilience4j uses semaphore-based or inline execution (same thread). Hystrix overhead: thread context switching per call. Resilience4j: minimal overhead, compatible with virtual threads (Project Loom). Resilience4j is the modern replacement. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Circuit Breaker Cascades Across Services**

**Symptom:** Service A calls B and C. Service B fails. Service A's circuit breaker for B opens. But the fallback for B involves calling Service D. Service D is healthy. Now Service A is calling D heavily (all traffic that used B is now going to D's fallback path). Service D becomes overloaded. D's circuit opens in Service A. Cascade through fallbacks.
**Root Cause:** Fallback paths can create hidden dependencies. A circuit breaker that opens and redirects to a fallback can create a load spike on the fallback path — overwhelming a previously healthy service.
**Diagnostic:**

```bash
# Check circuit breaker states across services:
# Actuator (Spring Boot + Resilience4j):
curl http://service-a/actuator/circuitbreakers
# If multiple circuits OPEN simultaneously: cascade

# Check load on fallback service (D):
curl http://service-d/actuator/metrics/http.server.requests
# Rising request rate + rising error rate = fallback overload

# Correlate timing:
# B's circuit opens at T=X → D's traffic spikes at T=X
grep "circuit.*OPEN\|circuit.*CLOSED" app.log | \
  grep "service-b\|service-d"
```

**Fix:**
BAD: Unbounded fallback calls (fallback has no circuit breaker or rate limit).
GOOD: (1) Add a separate circuit breaker for the fallback path (circuit breaker for D). (2) Rate-limit the fallback path (Bulkhead DST-043 on D's caller). (3) Make fallback truly local (cached data, static response) — no additional remote call.
**Prevention:** For every fallback that involves a remote call: add a circuit breaker for that path too. Prefer local/static fallbacks over remote fallbacks.

**Failure Mode 2: Half-Open Probe Overwhelms Recovering Service**

**Symptom:** Downstream service recovers from overload. Circuit breaker transitions to HALF-OPEN. All circuit breakers across 20 instances of Service A simultaneously send their HALF-OPEN probes to the recovering service. The 20 simultaneous probes re-overload the service. It fails again. All circuits re-open. Recovery loop.
**Root Cause:** `permittedNumberOfCallsInHalfOpenState` is PER INSTANCE of Service A. With 20 instances × 3 permitted probe calls = 60 simultaneous probes on a service that can only handle 10/second during recovery.
**Diagnostic:**

```bash
# Check state transitions across all instances:
# If all instances transition to HALF-OPEN simultaneously:
# timestamp of OPEN → count instances → multiply by probe calls
grep "HALF_OPEN" service-a-*.log | \
  awk '{print $1}' | sort | uniq -c | sort -rn | head
# High count at same timestamp = simultaneous probes
```

**Fix:**
BAD: `permittedNumberOfCallsInHalfOpenState(3)` × 20 instances = 60 probes.
GOOD: (1) Set `permittedNumberOfCallsInHalfOpenState(1)` — 1 probe per instance. (2) Stagger `waitDurationInOpenState` per instance via jitter: `Duration.ofSeconds(30 + random.nextInt(30))`. (3) Use centralized circuit breaker state (Redis-backed) — one HALF-OPEN probe attempt for the entire cluster.
**Prevention:** Always calculate: probes_per_recovery = instances × permittedCalls. Ensure probes_per_recovery << downstream_recovery_capacity.

**Failure Mode 3: Security - Malicious Input Triggers Circuit Breaker (Denial of Service)**

**Symptom:** An attacker sends malformed requests to Service A that cause Service A's calls to Service B to timeout (crafted to trigger the slow code path). After enough malformed requests: Service A's circuit breaker for B opens. Legitimate users get "service unavailable" for all B-dependent operations.
**Root Cause:** Circuit breaker opens based on CALL outcomes, not request source. An attacker who can cause failures in the call path (by crafting inputs that trigger timeouts or errors) can intentionally trip the circuit breaker — a denial-of-service attack on the circuit breaker state itself.
**Diagnostic:**

```bash
# Detect coordinated circuit-tripping:
# Check if circuit open events correlate with specific
# IP/user patterns:
grep "circuit.*OPEN" app.log | head -5
# Note timestamp, then check access logs at same time:
grep "2024-01-15T10:23" access.log | \
  awk '{print $1}' | sort | uniq -c | sort -rn | head
# Specific IP with high rate = potential attack

# Check if failure type is timeout vs exception:
# cb.getMetrics().getNumberOfSlowCalls()
# High slow call count = timeout-based tripping
```

**Fix:**
BAD: Circuit breaker trips on all failure types equally, no source attribution.
GOOD: (1) Rate limit per user/IP BEFORE reaching the circuit breaker — malicious requests throttled before they can affect circuit state. (2) Distinguish failure types: timeout from malformed input (user error → don't count against circuit) vs timeout from service error (infrastructure → count against circuit). (3) Input validation before expensive remote calls — reject malformed input before calling B.
**Prevention:** Rate limiting (Bulkhead DST-043) + input validation at the API gateway before requests reach circuit-breaker-protected paths.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-041 - Heartbeat (circuit breaker HALF-OPEN probe is conceptually a heartbeat to the dependency)
- DST-046 - Timeout (timeouts are the primary trigger for circuit breaker failures)

**Builds On This (learn these next):**

- DST-043 - Bulkhead (bulkhead + circuit breaker = standard resilience combination)
- DST-047 - Fallback (circuit breaker in OPEN state needs a fallback strategy)
- DST-048 - Graceful Degradation (circuit breaker is the mechanism; graceful degradation is the strategy)

**Alternatives / Comparisons:**

- DST-044 - Retry with Backoff (complementary — retry handles transient, circuit breaker handles sustained failures)
- DST-046 - Timeout (simpler primitive; circuit breaker adds state machine on top of timeouts)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Three-state wrapper (CLOSED/   |
|                  | OPEN/HALF-OPEN) around remote  |
|                  | calls that trips on failures   |
+------------------+--------------------------------+
| PROBLEM SOLVED   | Cascade failure: one failing   |
|                  | dependency exhausts callers'   |
|                  | thread pools                   |
+------------------+--------------------------------+
| KEY INSIGHT      | Fail fast (0ms) is better than |
|                  | fail slow (30s timeout) —      |
|                  | releases threads immediately   |
+------------------+--------------------------------+
| USE WHEN         | Any call to external service   |
|                  | (HTTP, DB, queue, 3rd-party)   |
+------------------+--------------------------------+
| AVOID WHEN       | In-process calls (no network   |
|                  | latency risk) — overhead only  |
+------------------+--------------------------------+
| TRADE-OFF        | Availability during outage     |
|                  | (OPEN) vs cascade prevention   |
+------------------+--------------------------------+
| ONE-LINER        | Count failures, trip on        |
|                  | threshold, probe for recovery  |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-043 Bulkhead,              |
|                  | DST-044 Retry, DST-047 Fallback|
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. CLOSED → OPEN when failure_rate > threshold; OPEN → HALF-OPEN after wait_duration; HALF-OPEN → CLOSED or OPEN based on probe results. Three states, automatic transitions.
2. The benefit is protecting the CALLER's thread pool, not the failing service. Fail fast (0ms) vs fail slow (T_timeout) = thread pool availability during outages.
3. Compose with: Retry (transient failures within CLOSED state), Bulkhead (limit concurrent calls), Fallback (what to return when OPEN). These four patterns form the standard resilience stack.

**Interview one-liner:**
"Circuit breaker wraps remote calls in a three-state machine. CLOSED: normal operation, track failure rate. OPEN (trips when failure rate > threshold): fail all calls immediately (fail fast, release threads). HALF-OPEN (after wait_duration): allow probe calls through. Probe succeeds → CLOSED; fails → OPEN. Prevents cascade failures by converting blocking thread exhaustion into fast failures, preserving thread pool capacity for healthy service operations."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When a resource becomes unhealthy, stop demanding more of it — protect your own capacity by failing fast. This principle appears in every system that must remain partially available when a dependency fails. The key insight: the cost of a blocked/waiting call (thread held, memory consumed, latency accumulated) is often worse than the cost of a fast failure (small exception, quick fallback). Stop trying; fail fast; preserve capacity for what works.

**Where else this pattern appears:**

- **TCP slow start and congestion control:** When TCP detects packet loss (analogous to service failure): it immediately halves the congestion window (stops sending as many packets) — circuit breaker at the network protocol level. After recovery (RTT without loss): slowly increases window size (HALF-OPEN recovery). Same principle: detected failure → reduce load → probe for recovery → restore.
- **Database connection pool exhaustion handling:** When a database becomes overloaded: connection pool `maxWait` timeout fires. Modern pools (HikariCP) can "trip" — reject new connection requests immediately if the pool has been failing for N consecutive timeouts (`connectionTimeout` + pool exhaustion). Circuit breaker pattern applied to DB connection acquisition.
- **Rate limiting at API gateways (circuit breaker for clients):** When a client's request rate triggers rate limiting: the API gateway rejects their requests with 429 (Too Many Requests) — an OPEN state. After a cooldown: the client can retry (HALF-OPEN). If they continue violating: stay rate limited. This is circuit breaker logic applied to client behavior rather than dependency health.

---

### 💡 The Surprising Truth

Netflix's Hystrix — the circuit breaker library that popularized the pattern and was used in production at Netflix for years — was deprecated in 2018. The Netflix team's reasoning was unexpected: Hystrix's thread-pool-per-command isolation model (each remote call runs in a dedicated thread) was designed to work around JVM thread blocking constraints. With the rise of reactive programming (Project Reactor, RxJava) and now virtual threads (Java 21 Project Loom): the fundamental problem Hystrix was solving (threads are expensive, can't block them) is largely mitigated. Resilience4j uses semaphore-based isolation — far less overhead. The deeper surprise: the thread-pool isolation in Hystrix consumed more CPU/memory than the latency it was preventing in many cases. Some Netflix teams found that Hystrix's overhead was measurable — the cure had non-trivial costs. The lesson: circuit breaker logic (state machine, failure counting) is essential; specific implementation choices (thread-pool vs semaphore) have significant operational costs that must be measured, not assumed.

---

### 🧠 Think About This Before We Continue

**Q1 (B - Scale):** Service A runs 50 instances. Each instance has a circuit breaker for Service B with `slidingWindowSize=10, failureRateThreshold=50%, waitDurationInOpenState=30s`. Service B has a 1-minute complete outage. After recovery: how many probe calls does Service B receive in the first second? How does this compare to Service B's normal request rate, and what happens if Service B can only handle 100 requests/second during early recovery?
_Hint:_ After wait_duration (30s) elapses: all 50 instances simultaneously transition to HALF-OPEN. Default `permittedNumberOfCallsInHalfOpenState=1` (unless configured differently). 50 instances × 1 probe = 50 simultaneous probes. At 1 probe/instance/30s: this is a 50× burst above the steady-state probe rate. If Service B handles 1000 req/s normally but only 100 req/s during early recovery: 50 simultaneous probes fit within recovery capacity. But if `permittedCalls=3`: 50 × 3 = 150 probes > 100 recovery capacity → re-triggers failure → back to OPEN. Solution: permittedCalls=1 per instance + ensure 50 probes << recovery_capacity.

**Q2 (D - Root Cause):** A production circuit breaker shows this pattern: opens briefly at T=0:00, closes at T=0:30 (HALF-OPEN probe succeeds), opens again at T=0:31, closes at T=1:01, opens again at T=1:02. This pattern repeats every ~30 seconds. What is the likely root cause, and how would you diagnose and fix it?
_Hint:_ Pattern: OPEN → HALF-OPEN probe succeeds (1 probe OK) → CLOSED → immediately fails → OPEN again. The service appears to handle exactly 1 request fine but then fails. Root causes: (1) The service is at 100% capacity — it can handle the probe (1 req) but any real traffic immediately triggers failures. (2) The service has a "cache warmup" issue — first request after restart succeeds (returns cached/default value), subsequent requests fail. (3) The service has a connection pool size of 1 — probe uses the 1 connection, real traffic saturates it. Diagnosis: check the service's own metrics at T=0:30 (when probe succeeds): CPU, memory, active connections. Check if real traffic immediately follows the probe — probe succeeds but N simultaneous real requests fail. Fix: `permittedNumberOfCallsInHalfOpenState` should be higher to properly validate recovery capacity, not just 1 probe.

**Q3 (C - Design Trade-off):** An architect proposes implementing circuit breaking at the service mesh layer (Istio outlier detection) instead of in application code (Resilience4j). What are the trade-offs of each approach? When would you choose one over the other, and is it appropriate to use BOTH simultaneously?
_Hint:_ Istio outlier detection: infrastructure-level, no code changes, works for all services automatically, based on consecutive 5xx errors (simpler failure model), no access to business-level failures (e.g., HTTP 200 with error in body). Resilience4j: application-level, per-method granularity, can use business-logic failure criteria (status code in body), adds code complexity. Using both: Istio circuit breaker for coarse-grained infrastructure failures (service crashes, hard 500s). Resilience4j for business-level circuit breaking (soft failures, custom exceptions). Potential conflict: Istio opens circuit BEFORE application circuit breaker reaches threshold — requests rejected by Istio also count as failures in Resilience4j window. Double-counting. Recommendation: use one per layer. Production choice: Istio for HTTP 5xx infrastructure failures, Resilience4j for application-specific failures.

