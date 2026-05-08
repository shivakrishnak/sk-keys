---
layout: default
title: "Thundering Herd"
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 25
permalink: /system-design/thundering-herd-system/
id: SYD-025
category: System Design
difficulty: ★★★
depends_on: Load Balancing, Caching, Rate Limiting
used_by: Reliability Engineering, Infrastructure Design
related: Cascading Failures, Rate Limiting, Circuit Breakers
tags:
  - failure-modes
  - advanced
  - performance
  - reliability
  - scalability
---

# SYD-025 - Thundering Herd

⚡ TL;DR - When a backend becomes unavailable, all pending clients retry simultaneously, overwhelming the system when it recovers. Solved by exponential backoff, request queuing, and gradual traffic increase on recovery.

| #700            | Category: System Design                             | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------- | :-------------- |
| **Depends on:** | Load Balancing, Caching, Rate Limiting              |                 |
| **Used by:**    | Reliability Engineering, Infrastructure Design      |                 |
| **Related:**    | Cascading Failures, Rate Limiting, Circuit Breakers |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Database goes down for 5 minutes. 10,000 client connections queued, waiting for response. Database comes back up. All 10,000 clients retry simultaneously. Database immediately overwhelmed (thundering herd), collapses again.

**THE BREAKING POINT:**
Recovery from failure made worse by the volume of retries.

**THE INVENTION MOMENT:**
"When system recovers, don't let all clients retry at once. Stagger them. Gradually warm up the system."

---

### 📘 Textbook Definition

**Thundering Herd:** Problem occurring when a shared resource (cache, database, service) becomes unavailable, causing many pending clients to queue. When the resource recovers, all queued clients attempt to use it simultaneously, overwhelming the system and potentially causing cascading failure.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
System goes down → all clients retry at once → system gets overwhelmed again.

**One analogy:**

> Concert ends → 20,000 people rush to parking lot → traffic jam. When jam clears, don't let all 20,000 rush again; stagger the exit.

**One insight:**
Recovery from failure is fragile if not managed. Retries must be staggered.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Failures happen (network, database, service)
2. Clients queue requests while service unavailable
3. When service recovers, queued clients all retry
4. If all retry simultaneously, service again overwhelmed
5. Cascading failure can occur (worse than original)

**PREVENTION STRATEGIES:**

1. **Exponential Backoff**: Client waits 1s, then 2s, then 4s, then 8s before retrying (spreads retries)
2. **Jitter**: Add randomness to backoff (prevents synchronized retries)
3. **Gradual Warm-Up**: Accept only limited traffic on recovery, gradually increase
4. **Request Queue**: Drop low-priority requests during overload (circuit breaker)
5. **Connection Pooling**: Limit concurrent connections (prevents queue explosion)

**THE TRADE-OFFS:**
**Gain:** Graceful recovery. Prevent cascading failures. More predictable system behavior.

**Cost:** Delayed retry (client waits longer). Implementation complexity. Memory usage (queuing).

---

### 🧪 Thought Experiment

**SETUP:**
Cache layer (Redis) serves 10,000 requests/sec. Handles 100,000 concurrent connections.

**Without Thundering Herd Protection:**

- 14:00:00 - Redis crashes
- 14:00:01 - 100,000 queued requests waiting
- 14:00:05 - Redis comes back online
- 14:00:05.001 - All 100,000 clients retry SIMULTANEOUSLY
- Redis receives 100,000 requests in 1ms (1 billion req/s equivalent)
- Redis immediately crashes (overwhelmed)
- Cascading failure: backend services also fail (cache unavailable)
- System down for additional 5 minutes

**With Thundering Herd Protection:**

- 14:00:00 - Redis crashes
- 14:00:01 - 100,000 clients queued
- 14:00:05 - Redis comes back online
- 14:00:05.001 - Clients retry with exponential backoff + jitter:
  - 40,000 clients: wait 100ms before retry (staggered)
  - 40,000 clients: wait 200-300ms before retry (jitter)
  - 20,000 clients: wait 500-1000ms before retry (dropped/queued)
- 14:00:05.100 - 40,000 requests hit Redis (manageable load)
- 14:00:05.200 - Additional 20,000 requests
- 14:00:05.500 - Remaining requests
- 14:00:06.000 - System fully recovered
- Total downtime: ~1 second (vs. 5+ seconds with cascading failure)

**THE INSIGHT:**
Staggering retries costs latency (clients wait), but prevents cascading failures.

---

### 🧠 Mental Model / Analogy

> After earthquake, water pressure drops. (1) Without staggering: all residents turn on faucets (system pressure zero, no water). (2) With staggering: only some residents use water initially, pressure recovers gradually, more people can use water over time.

- "Earthquake" → service failure
- "Water pressure drops" → system recovery takes time
- "All residents turn on faucets" → thundering herd (all retries at once)
- "System pressure zero" → cascading failure
- "Stagger usage" → exponential backoff, gradual warm-up

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
System goes down. Everyone retries at once. System gets overwhelmed again. Solution: stagger retries so system isn't re-flooded.

**Level 2 - How to use it (junior developer):**
When request fails: wait 1-10 seconds before retry (not immediately). Add randomness (jitter) so not all clients retry at same time.

**Level 3 - How it works (mid-level engineer):**
Client-side: exponential backoff (wait 1s, 2s, 4s, 8s) + jitter (randomize between retries). Server-side: accept only limited connections on recovery (gradual warm-up), reject excess with backpressure. Queue low-priority requests, serve high-priority. Monitor: track retry spike, trigger alerts.

**Level 4 - Why it was designed this way (senior/staff):**
Thundering herd emerged from observation: failures often cause bigger problems than original. Queuing theory shows: synchronized retries = request storm. Solution: randomize, stagger, warm up gradually. Google SRE book details this extensively. Key: exponential backoff + jitter is proven algorithm (used in TCP, AWS SDKs, etc.). Gradual warm-up on server: capacity planning-only accept X% of normal load initially.

---

### ⚙️ How It Works (Mechanism)

Thundering herd protection:

```
SCENARIO 1: NAIVE (Without Protection)
──────────────────────────────────────
Service up: Capacity = 1000 req/sec
  ↓
Service fails (14:00:00)
  ↓
Clients queued: 5,000 pending requests
  ↓
Service recovers (14:00:05)
  ↓
ALL 5,000 clients retry immediately
  ↓
Request flood: 5,000 req in 1ms
  ↓
Service can't handle (capacity 1000 req/sec)
  ↓
Service crashes again (cascading failure)
  ↓
Overall downtime: 10-15 minutes (worse than original)

SCENARIO 2: WITH PROTECTION
────────────────────────────
Service fails (14:00:00)
  ↓
Clients queue with exponential backoff:
  Client 1: will retry in 1 sec (+ 50ms jitter)
  Client 2: will retry in 2 sec (+ 50ms jitter)
  Client 3: will retry in 3 sec (+ 50ms jitter)
  ...
  Client 5000: will retry in max_backoff sec
  ↓
Service recovers (14:00:05)
  ↓
Server: "I'm back, accept only 10% of normal load"
  → Accept 100 req/sec (gradual warm-up)
  ↓
Clients retry with jitter:
  14:00:05.050 - 50 requests hit (within 10% limit, OK)
  14:00:05.100 - 80 requests hit (bumping to 15% limit)
  14:00:05.200 - 120 requests hit (bumping to 20% limit)
  14:00:05.500 - 300 requests hit (bumping to 40% limit)
  14:00:06.000 - 1000 requests hit (normal capacity)
  ↓
System recovered, no cascading failure
  ↓
Overall downtime: 5-6 seconds (minimal cascade)

MECHANISM: EXPONENTIAL BACKOFF + JITTER
────────────────────────────────────────
retry_attempt = 0
max_backoff = 60  # 1 minute

while request_fails:
    retry_attempt += 1
    backoff = min(2^retry_attempt, max_backoff)
    jitter = random(0, backoff * 0.1)  # 10% jitter
    wait_time = backoff + jitter

    print(f"Retry {retry_attempt}: wait {wait_time}s")

    sleep(wait_time)
    result = send_request()

Example backoff sequence:
  Attempt 1: 2^1 = 2s + 0.2s = 2.2s
  Attempt 2: 2^2 = 4s + 0.4s = 4.4s
  Attempt 3: 2^3 = 8s + 0.8s = 8.8s
  Attempt 4: 2^4 = 16s + 1.6s = 17.6s
  Attempt 5: 2^5 = 32s + 3.2s = 35.2s
  Attempt 6: 2^6 = 64s → capped at 60s + 6s = 66s → fail/give up

MECHANISM: GRADUAL WARM-UP (Server Side)
─────────────────────────────────────────
current_load_capacity = 10%  # Start at 10% of normal

while requests_coming_in:
    if request_count < current_load_capacity:
        process_request()
    else:
        reject_request("503 Service Unavailable, retry later")

    # Gradually increase capacity as recovery progresses
    time_since_recovery = now() - recovery_time
    if time_since_recovery < 60sec:
        current_load_capacity += 0.5%  # Increase 0.5% per second
```

**Real-World Timeline:**

```
13:59:00 - Database healthy, 1000 req/sec capacity
14:00:00 - Database disk fills up, stops responding
14:00:05 - 1000 pending requests queue, backoff timers start
14:00:10 - Database repairs disk, comes back online
14:00:10.050 - First batch of retries hit (50 req, 5% of capacity)
14:00:10.100 - Second batch (100 req, 10% of capacity)
14:00:10.200 - Third batch (200 req, 20% of capacity)
14:00:10.500 - Larger batch (500 req, 50% of capacity)
14:00:11.000 - Full capacity (1000 req/sec)
14:00:15 - System fully stable
Total recovery time: ~5 seconds (without cascade, would be 10+ seconds)
```

---

### 💻 Code Example

**Example 1 - Exponential Backoff + Jitter (Python):**

```python
import time
import random

class RetryStrategy:
    def __init__(self, max_backoff=60, base_delay=1):
        self.max_backoff = max_backoff
        self.base_delay = base_delay

    def calculate_backoff(self, attempt):
        """Calculate wait time with exponential backoff + jitter"""
        # Exponential: 2^attempt
        exp_backoff = self.base_delay * (2 ** attempt)

        # Cap at max_backoff
        backoff = min(exp_backoff, self.max_backoff)

        # Add jitter (randomness: ±10%)
        jitter = random.uniform(backoff * 0.9, backoff * 1.1)

        return jitter

    def retry_with_backoff(self, func, *args, max_attempts=5):
        """Retry function with exponential backoff"""
        for attempt in range(max_attempts):
            try:
                return func(*args)
            except Exception as e:
                if attempt >= max_attempts - 1:
                    raise  # Give up after max attempts

                wait_time = self.calculate_backoff(attempt)
                print(f"Attempt {attempt + 1} failed: {e}")
                print(f"Waiting {wait_time:.2f}s before retry...")
                time.sleep(wait_time)

        raise Exception("Max retries exceeded")

# Usage
retry = RetryStrategy(max_backoff=30, base_delay=1)

def fetch_from_cache():
    # Simulate cache failure initially, then recovery
    if time.time() % 10 < 5:
        raise Exception("Cache unavailable")
    return "data"

try:
    result = retry.retry_with_backoff(fetch_from_cache)
    print(f"Success: {result}")
except Exception as e:
    print(f"Failed: {e}")
```

**Example 2 - Gradual Warm-Up (Server-Side):**

```python
from datetime import datetime, timedelta

class GradualWarmup:
    def __init__(self, normal_capacity=1000):
        self.normal_capacity = normal_capacity
        self.recovery_time = None
        self.current_request_count = 0

    def on_service_recovery(self):
        """Call when service comes back online"""
        self.recovery_time = datetime.now()
        print("[RECOVERY] Service online, warming up...")

    def get_acceptable_load(self):
        """Calculate current acceptable load as % of normal"""
        if self.recovery_time is None:
            return 1.0  # Normal capacity

        time_since_recovery = (datetime.now() - self.recovery_time).total_seconds()

        # Warm up over 60 seconds: 10% → 100%
        warmup_duration = 60
        if time_since_recovery >= warmup_duration:
            return 1.0  # Full capacity

        # Linear warmup: 10% + (time / warmup_duration) * 90%
        load_pct = 0.1 + (time_since_recovery / warmup_duration) * 0.9
        return load_pct

    def can_accept_request(self):
        """Check if should accept incoming request"""
        acceptable_load = self.get_acceptable_load()
        acceptable_count = int(self.normal_capacity * acceptable_load)

        if self.current_request_count < acceptable_count:
            self.current_request_count += 1
            return True
        else:
            return False

    def process_request(self):
        """Handle incoming request"""
        if self.can_accept_request():
            # Process
            return 200, "OK"
        else:
            # Reject (trigger client backoff)
            return 503, "Service Unavailable, retry later"

# Usage
warmup = GradualWarmup(normal_capacity=1000)
warmup.on_service_recovery()

for i in range(1500):
    status, msg = warmup.process_request()
    if i % 100 == 0:
        print(f"Request {i}: {status} {msg}")
```

**Example 3 - Circuit Breaker (Prevent Thundering Herd):**

```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.last_failure_time = None

    def call(self, func, *args):
        """Call function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout passed
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout):
                self.state = CircuitState.HALF_OPEN
                print("[CB] Attempting recovery (HALF_OPEN)...")
            else:
                raise Exception("Circuit breaker OPEN, service unavailable")

        try:
            result = func(*args)

            # Success: reset on HALF_OPEN
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                print("[CB] Service recovered (CLOSED)")

            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                print(f"[CB] Too many failures, OPEN circuit")

            raise

# Usage
breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=5)

def api_call():
    raise Exception("Service error")

for i in range(10):
    try:
        result = breaker.call(api_call)
        print(f"Request {i}: Success")
    except Exception as e:
        print(f"Request {i}: Rejected ({breaker.state.value})")
    time.sleep(0.5)
```

---

### ⚖️ Comparison Table

| Strategy                | Mechanism                           | Pros                          | Cons                           |
| ----------------------- | ----------------------------------- | ----------------------------- | ------------------------------ |
| **Exponential Backoff** | Wait 1s, 2s, 4s before retry        | Simple, spreads retries       | Delays user                    |
| **Jitter**              | Randomize backoff                   | Prevents synchronized retries | More unpredictable             |
| **Gradual Warm-Up**     | Accept % of normal load             | Smooth recovery               | Transient rejections           |
| **Circuit Breaker**     | Reject if failures exceed threshold | Prevents cascades             | May reject valid requests      |
| **Request Queue**       | Queue requests, process gradually   | Fair ordering                 | Uses memory, increases latency |

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| "All clients should retry immediately"                  | No. Immediate retries cause thundering herd. Exponential backoff + jitter is proven algorithm.         |
| "Circuit breaker prevents all cascading failures"       | No. Circuit breaker triggers on failures; thundering herd can still occur if not coupled with backoff. |
| "Gradual warm-up is only for database recovery"         | No. Any resource recovery benefits: cache, API, message queue.                                         |
| "We don't need retry logic if we have circuit breakers" | No. Retry logic (backoff) complements circuit breakers. Together they're robust.                       |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Retries Overwhelming After Circuit Breaker Opens**

**Symptom:**
Circuit breaker opens (rejects requests). Clients retry aggressively. When circuit half-opens, all queued retries hit at once. Service overwhelmed again.

**Prevention:**
Couple circuit breaker with exponential backoff. Clients stop retrying aggressively once breaker open.

---

**Failure Mode 2: Warm-Up Takes Too Long**

**Symptom:**
Service comes back online. Warm-up gradually increasing load, but clients still seeing timeouts (warming up too slowly).

**Prevention:**
Balance: 10-60 second warm-up windows (depends on service complexity). Too fast = cascade risk. Too slow = users suffer.

---

### 🔗 Related Keywords

**Prerequisites:**

- `Load Balancing`, `Caching`, `Reliability`

**Builds On This:**

- `Circuit Breakers`, `Rate Limiting`, `Resilience Patterns`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS   │ When system recovers, all clients     │
│              │ retry at once → cascade failure        │
├──────────────┼────────────────────────────────────────┤
│ PROBLEM IT   │ Failures cause bigger problems due    │
│ SOLVES       │ to synchronized retries               │
├──────────────┼────────────────────────────────────────┤
│ KEY INSIGHT  │ Stagger retries (backoff + jitter)   │
│              │ and warm-up server gradually          │
├──────────────┼────────────────────────────────────────┤
│ USE WHEN     │ Distributed systems, recovery from    │
│              │ failures, high-traffic services       │
├──────────────┼────────────────────────────────────────┤
│ AVOID WHEN   │ Single-threaded, low-traffic systems  │
├──────────────┼────────────────────────────────────────┤
│ ONE-LINER    │ "Stagger retries, gradual recovery,   │
│              │ prevent cascading failures."          │
├──────────────┼────────────────────────────────────────┤
│ NEXT EXPLORE │ Circuit Breakers → Resilience →       │
│              │ Chaos Engineering                     │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your service has 10,000 pending requests queued. It comes back online. Without backoff, all retry at once (10K req/sec spike). With exponential backoff, retries spread over 30 seconds. Which causes better user experience?

**Q2.** You're implementing gradual warm-up. Acceptable load: 10% → 100% over 60 seconds. But if load increases to 50% capacity midway, do you speed up warm-up or keep the pace?
