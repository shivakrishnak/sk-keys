---
id: MSV-017
title: Retry Strategy
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★☆
depends_on: MSV-016, MSV-010, MSV-002
used_by: MSV-018, MSV-044
related: MSV-016, MSV-018, MSV-044, MSV-043, MSV-058
tags:
  - microservices
  - reliability
  - intermediate
  - resilience
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 17
permalink: /microservices/retry-strategy/
---

# MSV-017 - Retry Strategy

⚡ TL;DR - A Retry Strategy defines how a service
automatically reattempts a failed request, including
how many times, how long to wait between attempts,
and crucially - which failures are safe to retry.
The hidden danger: retrying a non-idempotent operation
or retrying during an overload amplifies the failure.

| #017 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Timeout Strategy, Inter-Service Communication, Microservices Architecture | |
| **Used by:** | Fallback Strategy, Circuit Breaker | |
| **Related:** | Timeout Strategy, Fallback Strategy, Circuit Breaker, Resilience4j, Idempotency in Microservices | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Order Service calls Payment Service. A transient network
glitch causes the request to fail with a SocketException.
Without retry, the order fails. The user sees an error
and has to manually retry in their browser. 70% of users
don't retry - they abandon the order. Revenue is lost
for a 2ms network hiccup that would have resolved itself
on the next attempt.

**THE SECONDARY PROBLEM:**
A developer adds naive retry: catch any exception, retry
3 times immediately. Payment Service is under load and
returning 503. Service A's retry logic fires instantly,
tripling the request rate to an already-overloaded service.
Other callers also retry. Payment Service is now receiving
3-10x normal traffic from retries on top of new requests.
Overload is amplified, not recovered. Retry storms are
one of the most common causes of cascading failure in
microservices.

**THE INVENTION MOMENT:**
A correctly designed retry strategy distinguishes:
1. Which errors are safe to retry (transient vs permanent)
2. When to retry (exponential backoff + jitter to spread
   the retry storm)
3. What to retry (only idempotent operations)
4. How many times (bounded, not infinite)

---

### 📘 Textbook Definition

**Retry Strategy** is the policy that governs automatic
reattempts of a failed operation, used to handle transient
failures (brief network glitches, temporary service
unavailability) without burdening the caller with manual
retry logic. A complete retry strategy specifies: (1)
retry-able exceptions (timeout, connection reset, 503;
NOT 400, 401, 500 with business error), (2) max retry
count, (3) backoff algorithm (fixed, linear, exponential)
with jitter (randomised delay to spread retry storms),
(4) the operations that are safe to retry (idempotent
only). Libraries: Resilience4j `Retry`, Spring Retry,
and gRPC's built-in retry policy.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Retry automatically reattempts a failed call, but only
for transient failures, only for safe (idempotent) operations,
and with exponential backoff + jitter to avoid amplifying
an already-overloaded downstream.

**One analogy:**
> You call a friend and get a busy signal (transient:
they're on another call). You wait 30 seconds and try
again. If you still get busy, you wait 1 minute, then 2
minutes. You don't call back 100 times per second (that
would be harassment). You don't call back if their phone
is disconnected (permanent failure). You only call back
if you can safely ask the same thing twice without
causing a problem (idempotent).

**One insight:**
The most dangerous retry is the immediate retry during
an overload. If a service is returning 503 because it is
capacity-limited, retrying immediately increases the
load further. Exponential backoff (with jitter) gives
the service time to recover between retries. This is
why HTTP 429 includes a `Retry-After` header - the server
tells you the minimum wait time.

---

### 🔩 First Principles Explanation

**WHAT TO RETRY - CLASSIFICATION:**

```
SAFE TO RETRY (transient, idempotent):
───────────────────────────────
Network errors: SocketException, ConnectException
  (usually transient - brief network glitch)
Timeout: TimeoutException
  (may be transient - downstream temporarily slow)
HTTP 503: Service Unavailable
  (transient - service restarting or overloaded)
HTTP 429: Too Many Requests
  (transient - rate limit, retry after header)

NOT SAFE TO RETRY:
────────────────────────
HTTP 400: Bad Request
  (permanent - request is malformed, retry won't help)
HTTP 401/403: Unauthorized/Forbidden
  (permanent - auth failure, retry wastes resources)
HTTP 404: Not Found
  (permanent - resource doesn't exist)
HTTP 500: Internal Server Error
  (ambiguous - may be transient or permanent)
  Rule: only retry 500 if you know the operation
  is idempotent AND the server confirmed no side effects

NOT IDEMPOTENT - UNSAFE TO RETRY:
───────────────────────────────────
POST /payments (without idempotency key)
  Retry = double charge
POST /emails/send
  Retry = duplicate email
DELETE /orders/{id} with side effects
  May delete different resource on retry
  (only safe if first DELETE confirmed NOT to execute)
```

**BACKOFF ALGORITHMS:**

```
FIXED BACKOFF: retry every 1 second
  Attempt 1: immediate
  Attempt 2: +1s
  Attempt 3: +1s
  Problem: all callers retry in sync -> spike at T+1s

EXPONENTIAL BACKOFF: retry delay doubles each attempt
  Attempt 1: immediate
  Attempt 2: +1s
  Attempt 3: +2s
  Attempt 4: +4s (capped at max, e.g., 30s)
  Better: callers spread out over time after initial burst
  Problem: if all callers start at same time (e.g., deploy),
  retries still spike at the same times (1s, 2s, 4s)

EXPONENTIAL BACKOFF + JITTER: add randomness
  Attempt 2: +1s + random(0, 1s) -> 0.3s to 2s
  Attempt 3: +2s + random(0, 2s) -> 1.5s to 4s
  BEST: decorrelates retry attempts across callers
  Spike at T+1s broken into spread over T+0.3s to T+2s
```

---

### 🧪 Thought Experiment

**RETRY STORM MATH:**

```
Setup:
  Order Service: 10 instances, each sending 100 req/s
  Payment Service: capacity = 1000 req/s
  Normal load: 1000 req/s (exactly at capacity)

Payment Service hiccup: 5% of requests return 503
  50 requests/second are failing

WITHOUT JITTER (immediate retry, 3 attempts):
  Failed requests retry immediately
  Load at Payment Service:
    Original 1000 + 50 retries = 1050 req/s
    More 503s... more retries... 1150 req/s
    Exponential: service quickly overloaded
    A 5% error rate becomes 100% failure

WITH EXPONENTIAL BACKOFF + JITTER (max 3 retries):
  50 failures at T=0
  Retries spread: T+0.3s to T+2s (25 requests)
  T+1s to T+4s (another 25 requests)
  Load spike: 1050 at peak, quickly drops
  Payment Service recovers during backoff window
  Error rate: brief spike, then returns to 0%
```

---

### 🧠 Mental Model / Analogy

> Retry with jitter is like a traffic light at a busy
> intersection turning green. Without jitter: every car
> accelerates at exactly the same moment - the intersection
> is gridlocked for 2 seconds, then clear. With jitter:
> cars accelerate with slight random delays - traffic
> flows smoothly from the start. The total number of cars
> is the same; the distribution over time is different.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Retry tries the request again if it fails. Good retry
waits longer each time (exponential backoff) and adds
a random delay (jitter) so all callers don't retry
at the same instant.

**Level 2 - How to use it (junior developer):**
With Resilience4j:
```java
@Retry(name = "payment-retry",
    fallbackMethod = "paymentFallback")
public Payment charge(PaymentRequest req) {
    return paymentClient.charge(req);
}
```
Configure in application.yml: max-attempts, wait-duration,
enableExponentialBackoff, exponentialBackoffMultiplier.

**Level 3 - How it works (mid-level engineer):**
Resilience4j Retry wraps the method call in a decorator.
On exception: checks if exception type is in `retryExceptions`
list, increments attempt counter, computes wait duration
(with optional jitter: wait * random(0.5, 1.5)), sleeps,
retries. Records metrics (retry.calls with outcome=
success_with_retry, failed_with_retry, failed_after_retry).
On max-attempts exceeded: re-throws last exception or
calls fallbackMethod.

**Level 4 - Why it was designed this way (senior/staff):**
The decision of WHAT to retry is harder than HOW to retry.
The HTTP 500 ambiguity: a 500 from a payment service means
"something went wrong". Was the charge applied before
the error? If yes, retry = double charge. The production
solution: payment services return 500 with a body:
`{"charged": false, "code": "db_error"}` vs `{"charged":
true, "error": "receipt_send_failed"}`. Only retry if
`charged: false`. This requires API design co-ordination
between teams. Simpler: use idempotency keys and let the
payment service deduplicate.

**Level 5 - Mastery (distinguished engineer):**
The interaction between retry and circuit breaker is subtle.
Circuit breaker should wrap the TOTAL attempt (including
retries), not each individual attempt. If circuit breaker
wraps individual attempts, each retry trip-count is
independent and the circuit never opens. If circuit breaker
wraps the outer call, N retries count as N failures.
Design: Retry is inner, Circuit Breaker is outer. Order:
retry handles transient single-call failures; circuit
breaker detects sustained failure patterns across all
calls (including retried ones) and opens the circuit
to stop all calls (not just failed ones).

---

### ⚙️ How It Works (Mechanism)

**RESILIENCE4J RETRY CONFIGURATION:**

```yaml
# application.yml
resilience4j:
  retry:
    instances:
      payment-service:
        max-attempts: 3
        wait-duration: 500ms
        enable-exponential-backoff: true
        exponential-backoff-multiplier: 2
        # Jitter: +/- 50% of wait duration
        exponential-max-wait-duration: 10s
        retry-exceptions:
          - java.net.ConnectException
          - java.net.SocketTimeoutException
          - feign.RetryableException
        ignore-exceptions:
          - com.example.PaymentDeclinedException
          - com.example.InvalidCardException
```

```java
// Manual retry with jitter (when no library available)
public <T> T withRetry(
    Supplier<T> operation,
    int maxAttempts,
    long baseDelayMs) throws Exception {

    int attempts = 0;
    while (true) {
        try {
            return operation.get();
        } catch (TransientException e) {
            attempts++;
            if (attempts >= maxAttempts) throw e;

            // Exponential backoff with full jitter
            long delay = baseDelayMs *
                (long) Math.pow(2, attempts - 1);
            long maxDelay = Math.min(delay, 30_000);
            // Full jitter: random between 0 and maxDelay
            long jitter = (long)
                (Math.random() * maxDelay);
            Thread.sleep(jitter);
        }
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**RETRY + CIRCUIT BREAKER LAYERING:**

```
Order Service calls Payment Service:

Call attempt 1:  T=0
  Result: SocketTimeoutException (transient)
  Retry: wait 500ms + jitter(200ms) = 700ms

Call attempt 2:  T=700ms
  Result: SocketTimeoutException (still slow)
  Retry: wait 1000ms + jitter(400ms) = 1400ms

Call attempt 3:  T=2100ms
  Result: SocketTimeoutException (still failing)
  Max attempts reached: throw PaymentException
  Circuit Breaker records 1 FAILURE

After 10 failures in 1 minute:
  Circuit Breaker OPENS
  All calls to Payment Service: immediate fallback
  No more retries attempted (circuit is open)
  Payment Service gets 0 load -> can recover

After 30s half-open check:
  1 test call allowed
  If succeeds: circuit CLOSES, normal retries resume
  If fails: circuit stays OPEN for another 30s
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: immediate retry causes storm**

```java
// BAD: immediate retry on any exception
// Retries during overload amplify the problem
for (int i = 0; i < 3; i++) {
    try {
        return paymentService.charge(request);
    } catch (Exception e) {
        // Retry immediately - no backoff, no jitter
        // If payment service is overloaded (503),
        // we just tripled our request rate to it
        if (i == 2) throw e;
    }
}
```

```java
// GOOD: Resilience4j with exponential backoff + jitter
// Only retries on transient exceptions
// Ignores permanent failures (no retry)
@Retry(name = "payment-service",
    fallbackMethod = "chargeFallback")
@CircuitBreaker(name = "payment-service",
    fallbackMethod = "chargeFallback")
public PaymentResult charge(PaymentRequest req) {
    return paymentClient.charge(req);
}

public PaymentResult chargeFallback(
    PaymentRequest req, Exception ex) {
    // Log for investigation, return pending state
    log.warn("Payment failed after retries: {}",
        ex.getMessage());
    return PaymentResult.pending(
        req.getIdempotencyKey());
}
// Note: @CircuitBreaker is outer (wraps retry attempts)
// @Retry is inner (handles single-call transient failure)
```

**Example 2 - Idempotency key for safe retry**

```java
// Without idempotency: retry = double charge
PaymentRequest request = new PaymentRequest(
    orderId, amount);
paymentClient.charge(request); // Timeout fires
paymentClient.charge(request); // Retry -> DOUBLE CHARGE

// With idempotency key: retry = safe deduplication
String idempotencyKey = UUID.randomUUID().toString();
PaymentRequest request = new PaymentRequest(
    orderId, amount, idempotencyKey);
// On retry: payment service checks idempotencyKey
// If seen before: return cached response
// If not seen: process and cache response
// Result: exactly once charge guaranteed
```

---

### ⚖️ Comparison Table

| Backoff Strategy | Retry Timing | Storm Risk | Best For |
|---|---|---|---|
| **Immediate** | No wait | High | Rare single-call transient glitches |
| **Fixed backoff** | Equal intervals | Medium | Predictable recovery time |
| **Exponential** | Doubling intervals | Low | General-purpose, well-known pattern |
| **Exponential + Jitter** | Randomised doubling | Minimal | Production default - prevents storms |
| **Retry-After from server** | Server-specified | None | Rate limited APIs (429) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Retry all exceptions | Only retry transient errors. Retrying 400 (bad request) wastes CPU - the request will never succeed with the same payload. Retrying 500 (server error) may cause double-execution. Classify exceptions before retrying. |
| More retries = more resilient | More retries = more load on an already-struggling service. 3 retries with exponential backoff is more resilient than 10 immediate retries that amplify the overload. Max attempts should be 3-5 for most services. |
| Retry is sufficient for resilience | Retry handles TRANSIENT failures (brief glitches). Sustained failures require circuit breaker (stops retries when downstream is consistently failing) and fallback (alternative response). Retry alone without circuit breaker can cause infinite retry storms. |

---

### 🚨 Failure Modes & Diagnosis

**Retry storm amplifying overload**

**Symptom:**
Payment Service starts returning 503 for 10% of requests.
Order Service retry logic (3 immediate retries) kicks in.
Payment Service starts receiving 130% of normal load.
503 rate increases to 30%. 3x retries = 390% load.
Payment Service completely overwhelmed.

**Diagnostic Indicators:**
```bash
# Resilience4j retry metrics
curl http://order-service:8080/actuator/prometheus | \
  grep resilience4j_retry
# resilience4j_retry_calls_total{name="payment-service",
#   kind="successful_with_retry"} - retries that succeeded
# resilience4j_retry_calls_total{...kind="failed_with_retry"}
#   - retries that exhausted max attempts

# If retry rate is very high: backoff is too short
# or downstream is consistently failing (circuit breaker
# should have opened but isn't configured)

# Check if circuit breaker is closed during overload
curl http://order-service:8080/actuator/health | \
  jq '.components.circuitBreakers.details
       ."payment-service".details.state'
# Should be OPEN during sustained failure
# If CLOSED: circuit breaker threshold not configured
```

**Fix:**
1. Add exponential backoff with jitter (immediate->fixed)
2. Add circuit breaker to stop retrying during sustained
   failure
3. Respect `Retry-After` header in 429/503 responses
4. Set retryOnResult predicate: retry on 503 but
   not on 500 with business error body

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Timeout Strategy` - timeout is what fires that retry
  catches; without timeout, retry has nothing to catch

**Builds On This (learn these next):**
- `Fallback Strategy` - what to do when retries are
  exhausted: return cached data, default response, or error
- `Circuit Breaker` - wraps retry: opens to stop all calls
  (including retried ones) when downstream consistently fails

**Complements:**
- `Idempotency in Microservices` - without idempotency,
  retrying POST operations causes double-execution
- `Resilience4j` - library providing Retry, CircuitBreaker,
  Bulkhead, and RateLimiter in one package

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ RETRY ONLY   │ Transient errors: timeout, 503, conn reset│
│ ON           │ NOT: 400, 401, 403, 404, biz logic 500s  │
├──────────────┼───────────────────────────────────────────┤
│ BACKOFF      │ Exponential + jitter (production default) │
│              │ Full jitter: random(0, delay * 2^attempts) │
├──────────────┼───────────────────────────────────────────┤
│ LAYERING     │ Retry (inner) + Circuit Breaker (outer)  │
│              │ CB opens after N total failures incl. retries │
├──────────────┼───────────────────────────────────────────┤
│ IDEMPOTENCY  │ POST/mutations: add idempotency key      │
│              │ Server deduplicates: safe to retry       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Retry transient failures with exponential │
│              │  backoff+jitter; never retry during storm" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Fallback Strategy → Circuit Breaker      │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Only retry TRANSIENT errors (timeout, 503, conn reset).
   Retrying 400 wastes CPU; retrying 500 may double-execute.
2. Always use exponential backoff WITH jitter. Immediate
   retries during overload triple the load on an already-
   struggling service.
3. Retry is INNER, Circuit Breaker is OUTER. CB detects
   sustained failure across all attempts and stops retrying.

**Interview one-liner:**
"Retry Strategy automatically reattempts transient failures
with exponential backoff and jitter to avoid retry storms.
Only retry idempotent operations or use idempotency keys.
Never retry 400s or business-logic 500s. In production:
Retry wraps individual calls (inner), Circuit Breaker wraps
the entire operation (outer) and opens to stop all calls
including retried ones when downstream is consistently
failing."

---

### 💡 The Surprising Truth

AWS experienced the "thundering herd" problem in early
S3: all clients used the same backoff values (no jitter).
During an S3 outage, all clients retried at exactly the
same times: T+1s, T+2s, T+4s. Each retry wave hit S3
just as it was recovering, knocking it back down. The
solution (still published in the AWS Architecture Blog,
2015) was full jitter: add random delay from 0 to the
full exponential backoff value. This decorrelates clients
completely. The AWS team found that full jitter performs
better than "equal jitter" (adding jitter to each half
of the exponential) for systems with many independent
callers.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **CLASSIFY** Given a list of 10 exception types, classify
   each as retry-safe, not-safe, or depends-on-idempotency.
2. **IMPLEMENT** Resilience4j Retry + CircuitBreaker correctly
   layered, with exponential backoff + jitter, ignoring
   business exceptions, with proper fallback.
3. **DEBUG** Given high retry rate in Prometheus metrics,
   determine if the cause is transient failures (correct
   retry) or persistent failures (circuit breaker not open,
   fix the downstream first).
4. **CALCULATE** Given 100 simultaneous clients all starting
   retry at T=0 with exponential backoff, compare load
   profile at T=1s, T=2s, T=4s with vs without jitter.
5. **DESIGN** A retry strategy for a payment service that
   is safe from double-charges even during network partitions.

---

### 🧠 Think About This Before We Continue

**Q1.** Your retry strategy has max-attempts=3, backoff
starts at 1s, doubles each attempt. Payment Service is
down for 30 seconds. How many total requests does your
service send to Payment Service per original request
during the outage? If 1000 users try to pay per second,
how many requests per second does Payment Service receive
during its recovery?

**Q2.** You receive an HTTP 500 with body: `{"error":
"database_unavailable"}`. Is this safe to retry? Now
you receive HTTP 500 with body: `{"error": "insufficient_
funds"}`. Is this safe to retry? Design the API contract
that makes the retry classification unambiguous for all
callers.

**Q3.** gRPC has a built-in retry policy configurable
in the service config (not code). Compare: (a) gRPC
built-in retry, (b) Resilience4j retry in application
code, (c) Istio retry in the service mesh proxy. What
are the trade-offs in terms of visibility, control,
and operational complexity? When would you choose each?