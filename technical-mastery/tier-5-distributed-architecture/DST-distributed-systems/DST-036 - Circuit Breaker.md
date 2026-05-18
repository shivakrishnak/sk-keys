---
id: DST-036
title: Circuit Breaker
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-011, DST-034, DST-035
used_by: DST-039, DST-058
related: DST-011, DST-034, DST-035, DST-039
tags:
  - distributed
  - resilience
  - fault-tolerance
  - pattern
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 36
permalink: /technical-mastery/distributed-systems/circuit-breaker/
---

⚡ TL;DR - A circuit breaker monitors failures to a
downstream dependency and temporarily stops sending
requests when failures exceed a threshold (OPEN state),
allowing the dependency time to recover and preventing
the caller from wasting resources on a failing target;
it transitions through CLOSED (normal), OPEN (blocking),
and HALF-OPEN (testing recovery) states.

---

### 📋 Entry Metadata

| #036 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Fault Tolerance, Failure Detector, Retry Logic | |
| **Used by:** | Timeout Design, Service Mesh | |
| **Related:** | Fault Tolerance, Failure Detector, Retry Logic, Timeout Design | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Service A calls Service B for every incoming request.
B fails (deployment error, database down). All requests
to A now fail at the point where they call B. But the
requests still attempt to call B, wait for the timeout
(30 seconds each), then fail. Service A has 1000
concurrent requests, each holding a thread while waiting
for B to time out. A's thread pool exhausts. A stops
responding to all requests - even requests that don't
need B at all. B's failure has cascaded into a complete
failure of A.

This is **cascading failure**: a downstream failure
propagates upstream by exhausting the upstream's
resources through slow failures (timeouts).

**THE CORE INSIGHT:**
Once you know a downstream service is failing (it has
failed 10 times in a row), stop sending requests to
it immediately (don't wait for the 11th timeout). Save
the resources. Return a fast failure to the caller.
Periodically test if the service has recovered (HALF-OPEN
state). This is the circuit breaker pattern - borrowed
directly from electrical engineering.

---

### 📘 Textbook Definition

A **circuit breaker** wraps calls to a remote service
and tracks the failure rate. It operates in three states:

**CLOSED (normal operation):**
- All requests pass through to the dependency
- Failure counter is maintained
- If failures exceed threshold within a time window:
  transition to OPEN

**OPEN (failing fast):**
- All requests are immediately rejected without calling
  the dependency
- Returns a fast error (or cached fallback) to callers
- After a recovery timeout: transition to HALF-OPEN

**HALF-OPEN (testing recovery):**
- A limited number of requests are allowed through
- If they succeed: transition to CLOSED
- If any fail: transition back to OPEN

---

### ⏱️ Understand It in 30 Seconds

**The state machine:**
```
                 failure threshold exceeded
  ┌────────┐    ─────────────────────────►   ┌──────┐
  │CLOSED  │                                 │ OPEN │
  │(normal)│  ◄─────────────────────────    │      │
  └────────┘    success in HALF-OPEN         └──┬───┘
       ▲                                        │
       │                                  timeout elapsed
       │                                        │
       │         ┌───────────┐                  │
       └─────────┤ HALF-OPEN │◄─────────────────┘
     success     │ (1 probe) │
                 └───────────┘
                 failure → OPEN
```

**Effect on cascading failure:**
```
WITHOUT circuit breaker:
  B fails → A threads block on timeout (30s each)
  → A thread pool exhausts → A fails completely
  → Any service calling A also fails → cascade

WITH circuit breaker:
  B fails → circuit opens after 10 failures
  → A returns 503 immediately (no timeout wait)
  → A's threads are released
  → A continues serving requests that don't need B
  → B has time to recover
  → Circuit tests recovery via HALF-OPEN
  → Circuit closes → normal operation resumes
```

---

### 🔩 First Principles Explanation

**THE CASCADING FAILURE MECHANISM:**

A synchronous call to a failing service has two costs:
1. **Response cost:** the caller blocks for the full
   timeout duration waiting for the failure response
2. **Resource cost:** threads, connections, memory
   are held during the timeout window

If the timeout is 30 seconds and 100 requests/second
arrive, and all calls fail at 30s, the in-flight requests
at any moment = 100 × 30 = 3000 requests. If the thread
pool has 200 threads, it exhausts after 2 seconds of
the downstream failure. At that point, new requests
queue indefinitely. The queue fills. The service
becomes unavailable.

The circuit breaker eliminates the resource cost:
once OPEN, failures are returned in microseconds
(not 30 seconds). In-flight requests drop to near zero.

**FAILURE RATE THRESHOLD:**

The trigger condition defines the sensitivity:
- **Count-based:** fail N consecutive times → open
  (simple, sensitive to bursts)
- **Rate-based:** fail more than X% in last N seconds
  → open (smoothed, typical for production)

Resilience4j uses rate-based thresholds with a sliding
window. Hystrix used both count-based and rate-based.

**THE FALLBACK:**

When a circuit is OPEN, the caller can:
1. Return a cached last-known value (read operations)
2. Return a default/degraded response
3. Return an explicit error (503 Service Unavailable)

The best fallback depends on the operation:
- User profile service OPEN: return cached profile (stale OK)
- Payment service OPEN: return error (no cached payment OK)
- Recommendation service OPEN: return popular items (default)

---

### 🧠 Mental Model / Analogy

> An electrical circuit breaker trips (opens) when
> current exceeds safe levels - protecting the wiring
> from a sustained fault. It does not prevent all power
> from flowing; it isolates the fault. Once the fault
> is cleared, you reset (close) the breaker.
>
> A software circuit breaker does the same: when a
> dependency has too many failures (current overload),
> it "trips" (opens) and isolates the fault. The
> dependent service is no longer bombarded with requests
> it cannot handle. The circuit tests recovery (HALF-OPEN)
> and restores flow when the fault clears.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
A circuit breaker wraps calls to another service. If
the service fails repeatedly, the circuit breaker
"opens" and stops trying - returning instant failures
instead of timeouts. After a while, it tries one
request to test if the service recovered. If yes, it
"closes" and resumes normal operation.

**Level 2 - When to use it:**
Whenever service A synchronously depends on service B
and A's availability should not be directly coupled to
B's availability. Use for: external API calls, database
calls from services where the DB is optional, downstream
microservice calls. Do NOT use for: the primary data
store of a service (you can't serve any data without it).

**Level 3 - Configuration parameters:**

```
CLOSED state:
  failure_rate_threshold: 50%    # open if 50%+ fail
  minimum_calls: 5               # sample before deciding
  sliding_window: 10 seconds     # rate measured over 10s

OPEN state:
  wait_duration_open: 30 seconds # stay open for 30s

HALF-OPEN state:
  permitted_calls: 3             # allow 3 test calls
  success_threshold: 2           # need 2/3 success to
    close
```

**Level 4 - Bulkhead pattern (companion):**
Circuit breakers prevent cascading failures by stopping
requests to a failing service. Bulkheads prevent
cascading failures by isolating the thread pools:
instead of all callers sharing one thread pool, each
downstream dependency gets its own pool. If B's pool
exhausts, only B's calls are affected - not A's entire
thread pool. Circuit breakers + bulkheads = layered
defense against cascade failure.

**Level 5 - Adaptive circuit breakers:**
Standard circuit breakers use static thresholds. Adaptive
variants (like Netflix's Concurrency Limiter) measure
actual latency and in-flight request count to detect
degradation before failures spike. If latency is 2x
normal, start shedding load (even without errors). This
detects soft failures (slowdown before crash) that
standard thresholds miss. Netflix Concurrency Limiter
uses gradient descent on observed RTT to find the
optimal concurrent request limit.

---

### ⚙️ Circuit Breaker State Transitions

```
CLOSED state:
  ─── request ──────► downstream service ───► response
  (success) → failure_count = 0
  (failure) → failure_count += 1
              failure_count >= threshold → OPEN

OPEN state:
  ─── request ──────► [circuit breaker] ──► immediate fail
                         (no call to downstream)
  timer elapsed → HALF-OPEN

HALF-OPEN state:
  ─── first request ─► downstream service ───► response
  (success) → CLOSED
  (failure) → OPEN (immediately, reset timer)

All states log state changes for monitoring.
```

---

### 💻 Code Example

**Circuit Breaker: Wrong vs Right**

```python
# BAD: No circuit breaker - cascading failure risk

import requests

class PaymentClient:
    def charge(self, customer_id: str, amount: float):
        # Every request blocks until timeout (30s)
        # If payment service is down: threads pile up
        response = requests.post(
            "https://payment-service/charge",
            json={"customer_id": customer_id,
                  "amount": amount},
            timeout=30  # Thread held for 30s on failure
        )
        return response.json()
```

```python
# GOOD: Circuit breaker with Resilience4j-style pattern

import time
import threading
from enum import Enum
from collections import deque

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    def __init__(
        self,
        failure_rate_threshold: float = 0.5,
        sliding_window_size: int = 10,
        open_timeout_s: float = 30.0,
        half_open_max_calls: int = 3,
        half_open_success_threshold: int = 2
    ):
        self.threshold = failure_rate_threshold
        self.window = deque(maxlen=sliding_window_size)
        self.open_timeout = open_timeout_s
        self.half_open_max = half_open_max_calls
        self.half_open_success_needed = half_open_success_threshold

        self.state = CircuitState.CLOSED
        self.open_since: float = 0
        self.half_open_calls = 0
        self.half_open_successes = 0
        self._lock = threading.Lock()

    def call(self, fn, *args, fallback=None, **kwargs):
        """Execute fn, applying circuit breaker logic."""
        with self._lock:
            state = self._current_state()
            if state == CircuitState.OPEN:
                if fallback is not None:
                    return fallback()
                raise CircuitOpenError(
                    "Circuit is OPEN - service unavailable"
                )
            if state == CircuitState.HALF_OPEN:
                if self.half_open_calls >= self.half_open_max:
                    raise CircuitOpenError(
                        "Circuit HALF_OPEN - max probes reached"
                    )
                self.half_open_calls += 1

        try:
            result = fn(*args, **kwargs)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure()
            if fallback is not None:
                return fallback()
            raise

    def _current_state(self) -> CircuitState:
        if self.state == CircuitState.OPEN:
            if time.monotonic(
                ) - self.open_since >= self.open_timeout:
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                self.half_open_successes = 0
        return self.state

    def _record_success(self) -> None:
        with self._lock:
            self.window.append(True)
            if self.state == CircuitState.HALF_OPEN:
                self.half_open_successes += 1
                if self.half_open_successes >= self.half_open_success_needed:
                    self.state = CircuitState.CLOSED
                    self.window.clear()

    def _record_failure(self) -> None:
        with self._lock:
            self.window.append(False)
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                self.open_since = time.monotonic()
                return
            if len(self.window) >= 5:
                failure_rate = (
                    self.window.count(False) / len(self.window)
                )
                if failure_rate >= self.threshold:
                    self.state = CircuitState.OPEN
                    self.open_since = time.monotonic()

class CircuitOpenError(Exception):
    pass

# Production usage:
payment_cb = CircuitBreaker(
    failure_rate_threshold=0.5,
    open_timeout_s=30.0
)

def cached_payment_fallback():
    return {"status": "queued", "message":
            "Payment service unavailable, queued for retry"}

def charge_customer(customer_id: str, amount: float):
    return payment_cb.call(
        payment_client.charge,
        customer_id, amount,
        fallback=None  # No fallback for payments: fail fast
    )
```

---

### ⚖️ Comparison Table

| State | Behavior | Resource Use | When |
|---|---|---|---|
| **CLOSED** | Normal - all requests pass | Normal | Service is healthy |
| **OPEN** | Fail fast - no downstream calls | Minimal | Service is failing |
| **HALF-OPEN** | Limited probe - 1-3 test requests | Minimal + probe | After open_timeout |

| Pattern | What It Prevents | Granularity |
|---|---|---|
| **Circuit Breaker** | Timeout cascade, thread exhaustion | Per dependency |
| **Retry + Backoff** | Transient failure loss | Per request |
| **Bulkhead** | Thread pool exhaustion from one dependency | Per pool |
| **Timeout** | Indefinite blocking | Per request |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Circuit breaker is the same as retry" | They are complementary opposites. Retry tries again after failure (optimistic: will succeed next time). Circuit breaker stops trying after repeated failures (pessimistic: service is down). They are used together. |
| "Circuit breaker prevents all failures" | It prevents cascading failures by failing fast. The caller still fails - it just fails in microseconds instead of 30 seconds. |
| "OPEN = the downstream service is definitely down" | OPEN = the circuit breaker suspects the service is down based on observed failures. The service might be recovering. HALF-OPEN tests this assumption. |
| "One circuit breaker per application" | One circuit breaker per downstream dependency per calling service. Sharing a circuit breaker across different dependencies causes false positives and incorrect isolation. |

---

### 🚨 Failure Modes & Diagnosis

**Circuit Stuck in OPEN (Never Recovers)**

**Symptom:** Service recovered from outage. Alerts
still firing. Circuit breaker never transitions to
HALF-OPEN or CLOSED. All requests returning 503 circuit-
open errors.

**Root Cause:** Circuit breaker's `open_timeout` is
set to 5 minutes. The service recovered in 2 minutes,
but the circuit waits the full 5 minutes before probing.

**Diagnosis:**
```bash
# Check circuit breaker state metrics (Actuator):
curl http://service/actuator/circuitbreakers

# Resilience4j Prometheus metrics:
resilience4j_circuitbreaker_state{name="payment"} 1.0
# 0=CLOSED, 1=OPEN, 2=HALF_OPEN

# Log state transitions:
grep "CircuitBreaker" service.log | \
  grep "State transition" | tail -20
```

**Fix:**
```yaml
# Reduce open_timeout for faster recovery testing:
resilience4j:
  circuitbreaker:
    instances:
      payment:
        wait-duration-in-open-state: 10s  # was 5min
        permitted-number-of-calls-in-half-open-state: 3
        sliding-window-size: 10
        failure-rate-threshold: 50
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Fault Tolerance` (DST-011), `Failure Detector` (DST-034)
- `Retry Logic` (DST-035)

**Builds On This:**
- `Timeout Design` (DST-039)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ STATES     │ CLOSED → OPEN → HALF-OPEN → CLOSED         │
│ CLOSED     │ Normal operation; count failures           │
│ OPEN       │ Fail fast; no downstream calls             │
│ HALF-OPEN  │ Probe 1-3 requests; success=close          │
├────────────┼────────────────────────────────────────────┤
│ CONFIG     │ failure_rate (50%), open_timeout (30s),    │
│            │ half_open_calls (3), window_size (10)      │
├────────────┼────────────────────────────────────────────┤
│ PREVENTS   │ Thread exhaustion, timeout cascade         │
│ DOES NOT   │ Prevent individual request failures        │
├────────────┼────────────────────────────────────────────┤
│ FALLBACK   │ Cached data / default / 503 error          │
│ MONITOR    │ State transitions, failure rate, open count│
├────────────┼────────────────────────────────────────────┤
│ ONE-LINER  │ "Stop calling a failing service fast;      │
│            │  give it time to recover."                 │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

The circuit breaker addresses a universal engineering
principle: when a dependency fails, a system should
"fail fast" at that boundary rather than propagating
the failure. This appears in many forms: operating
system watchdog timers (kill unresponsive processes),
TCP keepalive probes (detect dead connections), browser
connection limits per origin (prevent resource exhaustion
from slow servers), and service mesh traffic policies.
In all cases, the pattern is: detect a failing component,
isolate it quickly, test for recovery. The circuit
breaker is the application-layer implementation of
this isolation pattern.

---

### 💡 The Surprising Truth

Netflix's Hystrix (the original circuit breaker library
for microservices) was deprecated in 2018. Not because
circuit breakers are bad - but because the implementation
model changed. Hystrix ran every command in a separate
thread pool (Hystrix thread pool isolation = bulkhead).
When Netflix moved to reactive programming (Project
Reactor, RxJava 2), thread isolation became incompatible
with the non-blocking execution model. Resilience4j
replaced Hystrix because it works with reactive streams.
But the core circuit breaker concept is unchanged.
Hystrix's retirement taught the industry that resilience
patterns must be compatible with the threading model
of the application - a bulkhead that uses thread isolation
is useless (or harmful) in a reactive/non-blocking
application that intentionally uses few threads.

---

### ✅ Mastery Checklist

1. [IMPLEMENT] Write a CircuitBreaker class with all
   three state transitions. Unit test the CLOSED→OPEN
   and HALF-OPEN→CLOSED paths with simulated failures
   and successes.
2. [CONFIGURE] For a payment service calling an external
   payment gateway with P99 latency 500ms and occasional
   30-second outages, specify all circuit breaker
   parameters with justification.
3. [FALLBACK] For each: user profile service, payment
   service, recommendation service - specify the
   appropriate fallback behavior when the circuit is OPEN.
4. [DIAGNOSE] Given the symptom "circuit breaker is OPEN
   but downstream service is healthy," enumerate three
   possible root causes and how to diagnose each.
5. [COMBINE] Draw the interaction between circuit breaker,
   retry with backoff, timeout, and bulkhead for a single
   service call. Specify which layer handles which type
   of failure.
