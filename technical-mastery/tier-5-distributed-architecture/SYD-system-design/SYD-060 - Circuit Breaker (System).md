---
id: SYD-060
title: "Circuit Breaker (System)"
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-001, SYD-008
used_by: ""
related: SYD-001, SYD-008, SYD-056, SYD-061
tags:
  - architecture
  - resilience
  - fault-tolerance
  - design
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 60
permalink: /technical-mastery/syd/circuit-breaker-system/
---

⚡ TL;DR - A circuit breaker is a resilience pattern
that stops sending requests to a service that is failing,
giving it time to recover. Three states: CLOSED (normal,
requests pass through), OPEN (service is failing, requests
fail fast with 503), HALF-OPEN (probe state, one test
request gets through to check recovery). Without a circuit
breaker, a slow/failing downstream service causes thread
exhaustion in the caller - the caller's thread pool fills
up waiting for timeouts, making the caller unresponsive.
The circuit breaker prevents cascading failure.

| #060 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Load Balancing, Microservices Architecture | |
| **Related:** | Load Balancing, Microservices Architecture, API Gateway Design, Bulkhead Pattern | |

---

### 🔥 The Problem This Solves

Your payment service calls an external card processor.
The card processor starts returning errors (500 responses,
taking 30 seconds to timeout). Your service threads are
blocked for 30 seconds each, waiting for the timeout.
You have 100 thread pool slots. With 5 concurrent requests
per second, they fill up in 20 seconds. New payment
requests queue up, then timeout too. Your payment service
is now unresponsive to all users - not because it is
broken, but because it is waiting for an external service
that has already failed. This is cascading failure.

---

### 📘 Textbook Definition

**Circuit breaker:** A design pattern (Michael Nygard,
"Release It!" 2007) that wraps calls to external services
with a state machine. Monitors call failures; "trips" the
circuit (goes OPEN) when failures exceed a threshold,
causing subsequent calls to fail immediately without
contacting the external service. Returns to normal
(CLOSED) after the service recovers.

**Cascading failure:** When one service's failure causes
its callers to fail, which in turn causes THEIR callers
to fail. The failure propagates through the service graph.
Circuit breakers prevent this by isolating failed services.

**Fail fast:** Returning an error immediately (without
waiting for a timeout) when a circuit is open. This
releases threads quickly, allowing the caller to handle
the failure or use a fallback instead of blocking.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Track failures. If too many: fail fast. After a pause:
test recovery. If recovered: resume normal traffic.

**One analogy:**
> An electrical circuit breaker in a house:
> Normal state (CLOSED): electricity flows through.
> Short circuit (too many failures): breaker trips (OPEN).
> No electricity flows - prevents the house from burning.
> After a few minutes: reset the breaker (HALF-OPEN).
> Try turning on the light. If it works (one test request
> succeeds): the problem is gone, breaker stays closed.
> If it trips again: leave it open, wait longer.

**One insight:**
The key insight is: when a service is down, blocking
threads waiting for timeouts is far more damaging than
failing fast. A 30-second timeout with 10 concurrent
requests = 300 thread-seconds wasted. Fail fast in
< 1ms = no thread waste. The circuit breaker converts
"timeout-based failure" into "fail-fast failure" once
it detects the service is unhealthy.

---

### 🔩 First Principles Explanation

**STATE MACHINE:**
```
                  failures > threshold
         ┌──────────────────────────────────────┐
         │                                       ▼
    ┌────────┐    timeout expires         ┌──────────┐
    │ CLOSED │ ─────────────────────────► │   OPEN   │
    │        │                            │          │
    │ Requests│ ◄── success              │ Fail fast│
    │ pass   │                            │ (503)    │
    └────────┘                            └──────────┘
         ▲                                       │
         │                                       │ timeout
           expires
         │ success                               ▼
         │                               ┌─────────────┐
         └────────────────────────────── │  HALF-OPEN  │
                                         │             │
                                         │ 1 test req  │
                                         │ passes thru │
                                         └─────────────┘
                                          If test fails:
                                          back to OPEN

States:
  CLOSED: service healthy. All requests pass through.
    Count failures. If failure_rate > threshold in
    window: trip to OPEN.
  
  OPEN: service unhealthy. All requests fail fast.
    Return 503 without calling the service.
    No threads blocked. Caller can use fallback.
    After open_timeout (e.g., 30 seconds): go to
    HALF-OPEN.
  
  HALF-OPEN: service possibly recovering.
    Allow ONE request through.
    If success: close circuit (back to CLOSED).
    If failure: back to OPEN (reset open_timeout).
```

**CONFIGURATION:**
```
failure_threshold: 50%  # Trip if 50% of last N
                        # requests failed
window_size: 20         # Track last 20 requests
open_timeout: 30s       # Wait 30s before testing
half_open_max_calls: 1  # Allow 1 test call

Tuning:
  Too aggressive (low threshold, small window):
    Circuit trips on temporary blips.
    Causes false positives → poor availability.
    
  Too lenient (high threshold, large window):
    Circuit trips too late.
    Many threads exhausted before protection.
    
  Recommendation: 50% failure rate, 20-request window,
  30-second open timeout for most services.
  Adjust based on acceptable failure rate and SLA.
```

**FALLBACK STRATEGIES:**
```
When circuit is OPEN: what do you return to the caller?

1. Return cached response:
   User profile call fails → return cached profile
   from 5 minutes ago. User sees slightly stale data.
   Better than: error page.

2. Return default response:
   Product recommendations fail → return empty list
   or "top 10 most popular" static list.
   
3. Return error (explicit degradation):
   Payment fails → return "payment service unavailable,
   please try again in a few minutes."
   Honest with the user; no misleading success.

4. Queue the request for retry:
   Non-critical operations (analytics, logging):
   Queue the event; process when service recovers.

Choice depends on business criticality:
  Payment: explicit error (cannot fake success)
  Recommendations: cached or default (user unaffected)
  Analytics: queue for retry (silent degradation)
```

---

### 🧪 Thought Experiment

**SIZING: Thread exhaustion without circuit breaker**

Service: 100 thread pool slots.
Downstream service: times out after 30 seconds.
Incoming request rate: 10 requests/second.

Without circuit breaker:
- Second 0: first failure. Threads start waiting.
- Second 10: 100 threads blocked (10/sec × 10sec).
- Thread pool full. New requests queue or fail with
  "thread pool exhausted."
- Second 30: first batch of timeouts release threads.
- But 10 new requests per second arrive. Queue grows.
- Service appears unresponsive. Cascades to callers.
- Recovery: only when downstream recovers. All queued
  requests timeout one by one over many minutes.

With circuit breaker:
- Second 0: first failure.
- Second 2: 10 failures in the window (50% rate).
  Circuit OPENS.
- Second 2 onward: all requests fail fast (< 1ms).
  Zero threads blocked. Thread pool stays empty.
  Fallback served immediately.
- Second 32 (after 30s open timeout): one test request.
  If downstream recovered: circuit closes. Normal traffic.
- Total impact: 2 seconds of partial failures vs.
  minutes of complete unresponsiveness.

---

### 🧠 Mental Model / Analogy

> The circuit breaker is like a doctor triaging patients:
>
> If a hospital's operating room is overwhelmed
> (downstream service is down), a good triage system
> (circuit breaker) redirects patients to other hospitals
> (fallback) or asks them to wait outside (queue).
>
> A bad triage system (no circuit breaker) keeps sending
> patients to the overwhelmed operating room, where they
> wait in the hallway. The hallway fills up (thread pool),
> blocking the entrance. Now new patients cannot even
> reach the building.
>
> Fail fast = divert patients early. The hallway stays clear.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A circuit breaker watches calls to another service.
If that service starts failing a lot, the circuit breaker
stops sending requests and immediately returns an error.
After a while, it tries one request to see if the service
has recovered. If yes, normal traffic resumes.

**Level 2 - How to use it (junior developer):**
Wrap external service calls with a circuit breaker library
(Resilience4j for Java, pybreaker for Python, Polly for
.NET). Configure: failure threshold (50%), window size
(20 requests), open timeout (30 seconds). Implement a
fallback: what to return when the circuit is open.

**Level 3 - How it works (mid-level engineer):**
Track call results in a sliding window (last N requests).
If failure rate > threshold: trip to OPEN state.
In OPEN state: return error immediately (no network call).
After open_timeout: transition to HALF-OPEN.
Allow one test request. If success: CLOSE. If failure:
back to OPEN. Libraries: Resilience4j (Java), Hystrix
(deprecated), pybreaker (Python). In API gateways:
Kong, NGINX, Envoy support circuit breaking natively.

**Level 4 - Why it was designed this way (senior/staff):**
Circuit breakers exist because TCP timeouts are long (30+
seconds by default) and thread pools are small (100-200
threads). Waiting for timeouts on every request to a failed
service fills the thread pool in seconds, making the entire
caller unresponsive. The circuit breaker converts timeout-
based failure (slow) into fast failure (< 1ms), preserving
the caller's capacity. The half-open state prevents
thundering herd on recovery: instead of all callers rushing
back to a recovered service simultaneously (potentially
overwhelming it again), one test request verifies recovery.
After confirmation, traffic resumes gradually (or
immediately, depending on configuration). The fallback
strategy is as important as the breaker itself: a good
fallback makes failure invisible to users (cached data,
defaults). A bad fallback (returning 503 to users) is
better than cascading failure but should be a last resort.

**Level 5 - Mastery (distinguished engineer):**
Netflix's Hystrix (now deprecated in favor of Resilience4j)
processes hundreds of billions of circuit-breaker-wrapped
calls per day across their microservices. Key insights:
(1) Every downstream call should be wrapped in a circuit
breaker; there is no call that is "too small" to protect.
A single slow DNS lookup can cascade. (2) Hystrix used
a dedicated thread pool per dependency - not just a circuit
breaker. Each external service has its own thread pool.
This is the Bulkhead pattern combined with circuit breaking:
a slow service only exhausts its dedicated pool, not the
shared pool. (3) The circuit breaker is also an observability
tool: when a circuit trips, it emits a metric. Operations
teams monitor "circuit open" alerts as leading indicators
of service degradation, often before users notice.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ CIRCUIT BREAKER STATE MACHINE                       │
│                                                      │
│ Request → CircuitBreaker.call(fn)                  │
│                                                      │
│   if state == OPEN:                                │
│     if current_time > open_time + open_timeout:    │
│       state = HALF_OPEN                            │
│       allow ONE request through                    │
│     else:                                          │
│       raise CircuitOpenError  ← FAIL FAST          │
│                                                      │
│   if state == HALF_OPEN:                           │
│     try:                                           │
│       result = fn()                                │
│       state = CLOSED  ← Recovered                 │
│       reset failure window                         │
│       return result                                │
│     except:                                        │
│       state = OPEN    ← Still failing              │
│       open_time = now()                            │
│       raise                                        │
│                                                      │
│   if state == CLOSED:                              │
│     try:                                           │
│       result = fn()                                │
│       window.record_success()                      │
│       return result                                │
│     except:                                        │
│       window.record_failure()                      │
│       if window.failure_rate() > threshold:        │
│         state = OPEN                               │
│         open_time = now()                          │
│       raise                                        │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Circuit breaker implementation**
```python
import time
from collections import deque
from enum import Enum

class State(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: float = 0.5,  # 50%
        window_size: int = 20,
        open_timeout: float = 30.0,      # seconds
    ):
        self.failure_threshold = failure_threshold
        self.window_size = window_size
        self.open_timeout = open_timeout
        self.state = State.CLOSED
        self.window: deque = deque(maxlen=window_size)
        self.open_time: float = 0.0

    def _failure_rate(self) -> float:
        if not self.window:
            return 0.0
        return sum(1 for r in self.window if not r) / len(
            self.window)

    def _should_attempt_reset(self) -> bool:
        return (time.monotonic() - self.open_time
                >= self.open_timeout)

    def call(self, fn, *args, fallback=None, **kwargs):
        """
        Execute fn with circuit breaker protection.
        Returns fallback() if circuit is open.
        """
        if self.state == State.OPEN:
            if self._should_attempt_reset():
                self.state = State.HALF_OPEN
            else:
                if fallback:
                    return fallback()
                raise RuntimeError(
                    "Circuit is OPEN - service unavailable")

        try:
            result = fn(*args, **kwargs)

            if self.state == State.HALF_OPEN:
                # Probe succeeded: close circuit
                self.state = State.CLOSED
                self.window.clear()
            else:
                self.window.append(True)  # Success

            return result

        except Exception as e:
            if self.state == State.HALF_OPEN:
                # Probe failed: reopen
                self.state = State.OPEN
                self.open_time = time.monotonic()
            else:
                self.window.append(False)  # Failure
                if (len(self.window) == self.window_size
                        and self._failure_rate()
                        >= self.failure_threshold):
                    self.state = State.OPEN
                    self.open_time = time.monotonic()
            raise

# Usage:
import requests
cb = CircuitBreaker(failure_threshold=0.5, window_size=20)

def get_user_profile(user_id: str) -> dict:
    def call():
        resp = requests.get(
            f"http://user-service/users/{user_id}",
            timeout=5.0)
        resp.raise_for_status()
        return resp.json()

    def fallback():
        # Return cached profile from Redis
        cached = redis.get(f"profile:{user_id}")
        return cached if cached else {"name": "Unknown"}

    return cb.call(call, fallback=fallback)
```

**Example 2 - No circuit breaker (BAD)**
```python
# BAD: Directly calling service without protection
# Thread pool exhaustion on downstream failure

import requests

def get_user_profile_bad(user_id: str) -> dict:
    # 30 second default timeout
    # If user-service is down: this blocks for 30 seconds
    # 100 concurrent calls = 100 threads blocked for 30s
    # Thread pool exhausted in seconds
    resp = requests.get(
        f"http://user-service/users/{user_id}")
    return resp.json()

# GOOD: Wrap with circuit breaker.
# If user-service is down: fail fast in < 1ms.
# Thread pool stays free. Fallback served to users.
```

---

### ⚖️ Comparison Table

| Approach | Failure Mode | Thread Impact | Recovery | Complexity |
|---|---|---|---|---|
| **No protection** | Cascading failure | Thread pool exhausted in seconds | Manual intervention | None |
| **Timeout only** | Slow failure (waits for timeout) | Threads blocked for timeout duration | Auto (after timeout) | Low |
| **Retry only** | Amplifies load on failing service | Wasted retries | Possible (if transient) | Low |
| **Circuit Breaker** | Fail fast, fallback served | Near-zero thread impact | Auto (half-open probe) | Medium |
| **Bulkhead + CB** | Isolated failure per service | Exhaustion per service (not global) | Auto | High |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Circuit breakers replace retries | Circuit breakers and retries serve different purposes. Retries handle transient failures (the service was momentarily unavailable for a few milliseconds). Circuit breakers handle sustained failures (the service is down for seconds to minutes). Combine both: retry up to 3 times with exponential backoff on transient failures; if the failure is sustained, the circuit breaker opens and stops further retries. |
| Once open, the circuit should stay open until manual intervention | The half-open state is designed for automatic recovery without human intervention. After the configured open_timeout, the circuit probes with one request. This allows the system to recover automatically when the downstream service comes back up. Manual reset is needed only for persistent issues (deployment problems, configuration errors) where automatic recovery is not expected. |
| Circuit breakers work only for HTTP calls | Circuit breakers apply to any unreliable dependency: database queries, cache lookups, message queue publishes, file system calls, DNS lookups. Any operation that can hang or fail repeatedly should be wrapped. A slow database query blocks a thread just as effectively as a slow HTTP call. |

---

### 🚨 Failure Modes & Diagnosis

**Thundering Herd on Circuit Recovery**

**Symptom:**
Downstream service recovers. Circuit transitions from
HALF-OPEN to CLOSED. All callers immediately resume
full traffic. The recovered service - still warming up
- gets hit with 10,000 requests/second. It falls over
again. Circuit opens again. The service never fully
recovers; it oscillates between recovering and failing.

**Root Cause:**
Full traffic resumed instantly on recovery. The recovering
service has not finished starting up (JVM warmup, cache
warming) and cannot handle full load immediately.

**Fix - Gradual traffic ramp on recovery:**
```python
class CircuitBreakerWithRamp:
    def __init__(self, *args, ramp_up_calls: int = 10):
        super().__init__(*args)
        self.ramp_up_calls = ramp_up_calls
        self.half_open_success_count = 0

    def call(self, fn, *args, fallback=None, **kwargs):
        if self.state == State.HALF_OPEN:
            # Allow increasing traffic during ramp-up
            # Not just one test request - gradually
            # increase: 1, 2, 4, 8... until full
            ramp_ratio = min(
                1.0,
                2 ** self.half_open_success_count
                / self.window_size
            )
            import random
            if random.random() > ramp_ratio:
                if fallback:
                    return fallback()
                raise RuntimeError("Circuit ramping up")

        try:
            result = fn(*args, **kwargs)
            if self.state == State.HALF_OPEN:
                self.half_open_success_count += 1
                if (self.half_open_success_count
                        >= self.ramp_up_calls):
                    # Enough successes: fully close circuit
                    self.state = State.CLOSED
                    self.half_open_success_count = 0
                    self.window.clear()
            return result
        except Exception:
            # Single failure during ramp: reopen
            self.half_open_success_count = 0
            self.state = State.OPEN
            self.open_time = time.monotonic()
            raise
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Load Balancing` - circuit breaker works alongside
  load balancing; unhealthy instances are removed
  from the pool; circuit breaker prevents calls to
  all instances of a failing service
- `Microservices Architecture` - circuit breakers are
  essential in microservices where every service has
  multiple downstream dependencies

**Builds On This (learn these next):**
- `API Gateway Design` - gateways implement circuit
  breakers for all upstream services
- `Bulkhead Pattern` - pairs with circuit breaker:
  dedicated thread pools per dependency to contain
  failure blast radius

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ THREE STATES │ CLOSED: normal. OPEN: fail fast.         │
│              │ HALF-OPEN: test recovery with 1 request. │
├──────────────┼─────────────────────────────────────────┤
  │
│ TRIP         │ failure_rate > threshold (50%) in window │
│              │ (20 requests). Configurable.             │
├──────────────┼─────────────────────────────────────────┤
  │
│ OPEN         │ Fail fast (< 1ms). No network call.      │
│              │ Serve fallback (cache, default, 503).    │
├──────────────┼─────────────────────────────────────────┤
  │
│ RECOVERY     │ open_timeout (30s) → HALF-OPEN.          │
│              │ 1 probe request. Success → CLOSED.       │
├──────────────┼─────────────────────────────────────────┤
  │
│ FALLBACK     │ Cache, default value, or explicit error. │
│              │ Never fake success on critical paths.    │
├──────────────┼─────────────────────────────────────────┤
  │
│ PROBLEM      │ Thread pool exhaustion → cascading fail. │
│              │ CB converts timeout → fail fast.        │
├──────────────┼─────────────────────────────────────────┤
  │
│ ONE-LINER    │ "Track failures. Too many: fail fast.    │
│              │  After pause: test recovery."           │
├──────────────┼─────────────────────────────────────────┤
  │
│ NEXT         │ Bulkhead Pattern → Saga Pattern          │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Three states: CLOSED (normal), OPEN (fail fast - no
   network call, serve fallback), HALF-OPEN (one probe
   request to test recovery). The OPEN state is what
   prevents thread exhaustion and cascading failures.
2. The circuit breaker converts timeout-based failure
   (30 seconds × N threads = thread pool exhausted) into
   fail-fast failure (< 1ms, thread immediately free).
   This preserves the caller's capacity to serve other
   requests even when a downstream service is down.
3. Always implement a fallback: what to return when the
   circuit is open. Cached data, a default response, or
   an explicit "service unavailable" message are all
   better than silently waiting for a timeout. Choose
   based on business criticality (payment: explicit error;
   recommendations: cached/default).

**Interview one-liner:**
"Circuit breaker: three states - CLOSED (all requests pass through, track failure
rate), OPEN (fail fast < 1ms with fallback, no network call; prevents thread
exhaustion and cascading failures), HALF-OPEN (after 30s open timeout, allow one
probe request; if success: CLOSED; if failure: back to OPEN). Trips when failure
rate > 50% in a 20-request window. Combine with fallback strategy: cache for
non-critical (recommendations), explicit error for critical (payment). Libraries:
Resilience4j (Java), pybreaker (Python)."
