---
layout: default
title: "Retry with Backoff"
parent: "Distributed Systems"
nav_order: 604
permalink: /distributed-systems/retry-with-backoff/
number: "0604"
category: Distributed Systems
difficulty: ★★☆
depends_on: Circuit Breaker, Timeout, Idempotency (Distributed), Failure Modes
used_by: HTTP Clients, gRPC, AWS SDK, Spring Retry, Resilience4j
related: Circuit Breaker, Idempotency (Distributed), Timeout, Jitter, Bulkhead
tags:
  - distributed
  - reliability
  - resilience
  - pattern
---

# 604 — Retry with Backoff

⚡ TL;DR — Retry automatically re-attempts failed calls; backoff increases the wait between attempts exponentially; jitter randomizes the backoff to prevent thundering herd; and idempotency ensures that retried calls don't produce duplicate side-effects.

| #604            | Category: Distributed Systems                                         | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Circuit Breaker, Timeout, Idempotency (Distributed), Failure Modes    |                 |
| **Used by:**    | HTTP Clients, gRPC, AWS SDK, Spring Retry, Resilience4j               |                 |
| **Related:**    | Circuit Breaker, Idempotency (Distributed), Timeout, Jitter, Bulkhead |                 |

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An HTTP call to a payment gateway fails with a `503 Service Unavailable`. The gateway was restarting — it will be back in 200ms. Without retry, the user gets an error page. With a simple retry (immediate): all 10,000 concurrent users retry at the same millisecond → thundering herd → gateway melts under the coordinated load spike → every retry also fails → users see errors and keep retrying manually → even worse. With retry + exponential backoff + jitter: retries spread out over time, load is diffused, gateway recovers, requests succeed.

**THE INVENTION MOMENT:**
Ethernet's CSMA/CD collision detection (1970s) first formalized exponential backoff: after a collision, wait `rand(0, 2^n) × slot_time` before retrying. This randomized backoff prevents all stations from retrying simultaneously after a collision. The same principle generalizes to distributed service calls.

---

### 📘 Textbook Definition

**Retry with backoff** consists of three components:

1. **Retry**: re-attempt a failed operation automatically, up to `max_attempts` times.
2. **Backoff**: wait between attempts; prevents hammering a struggling service. **Exponential backoff**: `wait = base_delay × 2^attempt_number`. **Linear backoff**: `wait = base_delay × attempt_number`. Fixed delay: `wait = constant`.
3. **Jitter**: randomize the backoff to prevent synchronized retries across many clients. **Full jitter**: `wait = rand(0, base_delay × 2^attempt)`. **Decorrelated jitter** (AWS recommended): `wait = min(cap, rand(base, prev_wait × 3))`.

**Retry-only conditions**: only retry on **transient** errors — `503`, `429`, network timeouts. Never retry on **permanent** errors — `400 Bad Request`, `404 Not Found`, business logic errors (insufficient funds). Never retry non-idempotent operations without idempotency keys.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
When a call fails transiently, wait a bit and try again — but wait progressively longer each time, and add randomness so all clients don't retry at the same moment.

**One analogy:**

> Retry with backoff is like redialing after a busy signal. First attempt: wait 1 second. Second: wait 2 seconds. Third: wait 4 seconds. If everyone in the city is calling the same number and they all redial at the exact same second (no jitter), the line is still busy. If each person adds a random 0-10 seconds to their wait, calls stagger — most eventually get through.

**One insight:**
**Jitter is not optional**. Without jitter, all clients synchronize their retries — they all backed off for `2^3 = 8` seconds and all retry at t=8s. The result is a coordinated load spike (thundering herd) at t=8s, t=16s, t=32s. Jitter breaks this synchronization. The recovery is only possible because retries are spread out in time.

---

### 🔩 First Principles Explanation

**EXPONENTIAL BACKOFF FORMULA:**

```
attempt 0 (first try): immediate
attempt 1 (first retry): wait = base × 2^1 = 100ms × 2 = 200ms
attempt 2 (second retry): wait = base × 2^2 = 100ms × 4 = 400ms
attempt 3: wait = base × 2^3 = 100ms × 8 = 800ms
attempt 4: wait = min(cap, base × 2^4) = min(30000ms, 1600ms) = 1600ms
...
wait is capped at max_delay (e.g., 30 seconds) to prevent indefinite growth
```

**JITTER VARIANTS:**

```python
import random
import time

def retry_with_full_jitter(fn, max_attempts=5, base_delay=0.1, cap=30.0):
    for attempt in range(max_attempts):
        try:
            return fn()
        except TransientException as e:
            if attempt == max_attempts - 1:
                raise  # Last attempt — propagate error
            # Full jitter: random between 0 and exponential cap
            wait = random.uniform(0, min(cap, base_delay * (2 ** attempt)))
            time.sleep(wait)

def decorrelated_jitter(base=0.1, cap=30.0):
    """AWS recommended: harder to reverse-engineer, better spread"""
    sleep = base
    while True:
        sleep = min(cap, random.uniform(base, sleep * 3))
        yield sleep
```

**WHAT TO RETRY (DECISION TABLE):**

```
HTTP Status → Retry?
  503 Service Unavailable       → YES (transient, service restarting)
  429 Too Many Requests         → YES (transient, but respect Retry-After header)
  408 Request Timeout           → YES (transient)
  500 Internal Server Error     → DEPENDS (could be transient or permanent; limit retries)
  502 Bad Gateway               → YES (transient, upstream proxy issue)
  400 Bad Request               → NO (permanent, request is malformed)
  401 Unauthorized              → NO (permanent, check credentials)
  403 Forbidden                 → NO (permanent, permission issue)
  404 Not Found                 → NO (permanent, resource doesn't exist)

Network Errors:
  ConnectionRefused             → YES (transient if service restarting)
  ConnectionTimeout             → YES (transient)
  SocketTimeout (mid-request)   → DEPENDS (did the server process partially? needs idempotency key)
```

**IDEMPOTENCY KEY REQUIREMENT:**

```
Non-idempotent without idempotency key:
  POST /api/payments  {"amount": 100, "to": "alice"}

  1. Client sends request.
  2. Server processes payment. Charges $100.
  3. Server crashes before responding.
  4. Client times out. Retries.
  5. Server processes payment AGAIN. Charges $100 again!
  6. User charged $200.

Idempotent with idempotency key:
  POST /api/payments  {"amount": 100, "to": "alice"}
  Headers: Idempotency-Key: client-generated-uuid-abc123

  1. Client sends with idempotency key.
  2. Server processes payment. Stores: {key: "abc123", result: "success"}.
  3. Server crashes before responding.
  4. Client retries with SAME idempotency key.
  5. Server sees key "abc123" already in DB → returns stored result.
  6. User charged $100 exactly once.
```

---

### 🧪 Thought Experiment

**RETRY AMPLIFICATION (THE THUNDERING HERD):**

10,000 users simultaneously request a resource. Service goes down for 30 seconds.
All 10,000 requests fail simultaneously. Without jitter, they all retry at t=2s.
Service is back up but now gets 10,000 simultaneous requests. Service may struggle.

With full jitter (`rand(0, 2s)`): retries spread across 0–2 second window.
Average ~5,000 requests/second instead of 10,000/second peak.
Service handles it. Most retries succeed.

**Retry amplification factor**: if each of the 10,000 clients does `max_attempts=3` retries, and if all fail each time, the service receives `10,000 × 3 = 30,000` requests during the recovery window instead of 10,000. Jitter reduces the peak rate; circuit breaker (opens after threshold) stops the amplification entirely once failure rate is confirmed to be persistent.

---

### 🧠 Mental Model / Analogy

> Retry with backoff is like trying to merge onto a highway during rush hour. You wait for a gap. If no gap: don't immediately try again (you'd crash). Wait a bit. Try again — wait a bit longer. Wait even longer. Eventually, you merge. Jitter: you and the car next to you both have the same destination and want to merge. If you both try at the same identical moment every time, neither gets in. If you each independently randomize your timing, you stagger your attempts and both eventually merge.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Retry: try again if it fails. Backoff: wait longer between retries. Jitter: randomize the wait to spread out retries. Only retry on transient errors, not permanent ones.

**Level 2:** Exponential backoff formula. Full jitter vs. decorrelated jitter (AWS recommended). Idempotency keys required for non-idempotent operations. Distinguish: transient (503, timeout) vs. permanent (400, 404) errors. Cap maximum backoff to bound worst-case latency.

**Level 3:** Retry budget: limit total retries per second across the cluster (not per request). Retry amplification: if 1% of calls fail and each is retried 3×, overall load increases by 3% for the 1% — generally acceptable. But if 50% fail simultaneously, retries add 150% load. Circuit breaker should open before retry amplification becomes catastrophic. gRPC retry policy: defined in service config; `retryPolicy.maxAttempts`, `retryableStatusCodes`.

**Level 4:** Retry loops can inadvertently implement distributed deadlocks. When Service A retries Service B which retries Service C which retries Service A: each service's retry logic extends the call while holding a lock or connection. The retry chain forms a cycle. Solution: propagate deadline (context deadline in Go, `timeout` in gRPC), not just per-hop timeout. If the original call's deadline is 5 seconds, all retries and sub-calls must complete within those 5 seconds. Each hop decrements from the same budget. This is called **deadline propagation** and is why gRPC context deadlines are passed through every RPC call.

---

### ⚙️ How It Works (Mechanism)

**Spring Retry + Resilience4j:**

```java
@Service
public class PaymentService {

    private final Retry retry;

    public PaymentService() {
        RetryConfig config = RetryConfig.custom()
            .maxAttempts(3)
            .waitDuration(Duration.ofMillis(100))
            .intervalFunction(IntervalFunction.ofExponentialRandomBackoff(
                100,    // base delay ms
                2.0,    // multiplier
                0.5,    // jitter factor (50% randomization)
                30_000  // max wait ms
            ))
            .retryExceptions(ConnectException.class, SocketTimeoutException.class)
            .ignoreExceptions(IllegalArgumentException.class, BusinessException.class)
            .build();
        this.retry = RetryRegistry.of(config).retry("payment");
    }

    public PaymentResult process(PaymentRequest req) {
        return Retry.decorateSupplier(retry, () -> {
            // Idempotency key must be in req to prevent double-charge on retry:
            return httpClient.post("/payments", req.withIdempotencyKey(req.getRequestId()));
        }).get();
    }
}
```

---

### ⚖️ Comparison Table

| Strategy             | Load on Retry          | Sync Prevention    | Use Case                                        |
| -------------------- | ---------------------- | ------------------ | ----------------------------------------------- |
| Immediate retry      | High (thundering herd) | None               | Almost never appropriate                        |
| Fixed backoff        | Medium                 | Partial            | Internal service retries (predictable recovery) |
| Exponential backoff  | Low (grows quickly)    | None               | General retries                                 |
| Exp backoff + jitter | Very low (randomized)  | Yes                | Production distributed systems                  |
| Decorrelated jitter  | Lowest                 | Yes (uncorrelated) | High-scale, AWS SDKs                            |

---

### ⚠️ Common Misconceptions

| Misconception                                              | Reality                                                                                                                                           |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Always retry on 500 errors                                 | Server errors can be permanent (e.g., unhandled NPE). Retry 500s conservatively (1-2 retries max). 503 is more clearly transient                  |
| Retrying a POST is safe because it's just a retry          | Non-idempotent POSTs can create duplicate records. Always require idempotency keys for state-changing retries                                     |
| More retries = better availability                         | Retries amplify load and extend failure duration. Use circuit breaker to stop retrying persistent failures; use retry only for transient failures |
| Backoff without jitter is fine for small number of clients | Even 10 clients with synchronized 8-second backoff create a load spike. Jitter is always correct                                                  |

---

### 🚨 Failure Modes & Diagnosis

**Retry Storm Overwhelming a Recovering Service**

Symptom: Service B goes down for 60 seconds. During recovery at t=60s, Service A's
retries create a load spike 10× normal. Service B immediately dies again under the
retry storm. Cycle repeats. Service B cannot stay recovered for more than a few seconds.

Cause: Service A has max_attempts=10, no circuit breaker, no jitter. All 1000 instances
of Service A retry simultaneously at t=60s.

Fix: (1) Add circuit breaker: after 50% failure rate, open circuit for 60s → Service B
gets 60s recovery time without bombardment. (2) Add decorrelated jitter to spread
remaining retries. (3) Reduce max_attempts to 3. (4) Add retry budget at cluster level:
limit total retries to 10% of successful calls via service mesh rate limiting.

---

### 🔗 Related Keywords

- `Idempotency (Distributed)` — critical for safe retries of state-changing operations
- `Circuit Breaker` — stops retrying when failures are persistent; prevents retry storms
- `Timeout` — bounds the duration of each retry attempt
- `Jitter` — the randomization component that prevents thundering herd
- `Bulkhead` — bounds how many concurrent retries can be in-flight

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  RETRY WITH BACKOFF                                      │
│  Only on: transient errors (503, timeout, network)       │
│  Never on: permanent errors (400, 401, 403, 404)         │
│  Formula: wait = min(cap, base × 2^attempt)              │
│  + JITTER: wait = rand(0, calculated_wait)               │
│  + IDEMPOTENCY KEY for non-idempotent operations         │
│  + CIRCUIT BREAKER to stop retrying persistent failures  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're implementing retry logic for a `DELETE /orders/{id}` endpoint. Is `DELETE` idempotent? If the first request reaches the server and succeeds but the response is lost in the network, is it safe to retry the DELETE? What about a `POST /orders/{id}/cancel`? Design the idempotency key strategy for each case.

**Q2.** AWS SDK for Java implements `decorrelated jitter` by default. Explain why decorrelated jitter is preferred over `full jitter` for a scenario where 1000 Lambda functions all start simultaneously after a cold start and all need to connect to DynamoDB. Sketch the retry timing distribution for both strategies and explain which produces a smoother load ramp-up on DynamoDB.
