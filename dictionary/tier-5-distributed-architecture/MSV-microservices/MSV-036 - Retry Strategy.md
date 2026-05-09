---
layout: default
title: "Retry Strategy"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 36
permalink: /microservices/retry-strategy/
id: MSV-036
category: Microservices
difficulty: ★★☆
depends_on: Timeout Strategy, Inter-Service Communication, HTTP & APIs
used_by: Circuit Breaker (Microservices), Resilience4j, Exponential Backoff (Task)
related: Fallback Strategy, Rate Limiting (Microservices), Idempotency (Distributed)
tags:
  - microservices
  - reliability
  - networking
  - intermediate
  - pattern
status: complete
---

# MSV-036 - Retry Strategy

⚡ TL;DR - A retry strategy automatically re-attempts a failed call a limited number of times, with backoff, turning transient faults into transparent recoveries.

| #651            | Category: Microservices                                                     | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Timeout Strategy, Inter-Service Communication, HTTP & APIs                  |                 |
| **Used by:**    | Circuit Breaker (Microservices), Resilience4j, Exponential Backoff (Task)   |                 |
| **Related:**    | Fallback Strategy, Rate Limiting (Microservices), Idempotency (Distributed) |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Network packets are occasionally dropped. DNS lookups briefly fail. A service restarts and misses a 200ms window. Without retries, every transient fault becomes a user-visible failure - a failed payment, a missing search result, an error page. Engineers add `try/catch` everywhere, sometimes retrying manually, inconsistently. Some services retry infinitely. Others never retry at all. A retry storm during an outage brings down already-struggling services.

**THE BREAKING POINT:**
The inconsistency is the problem. Ad-hoc retry logic lacks backoff, lacks limits, lacks awareness of whether the operation is safe to retry. The result: either too fragile (no retries, every transient fault surfaces) or too aggressive (unlimited retries amplify load during real outages).

**THE INVENTION MOMENT:**
This is exactly why retry strategy was created - a principled, configurable, bounded approach to retrying failed calls that handles transient faults without making real failures worse.


**EVOLUTION:**
Retry strategies evolved from simple 'try again on failure' (1990s) to configurable policies with exponential backoff and jitter. The initial approach was synchronous retry: catch exception, wait, retry immediately. This caused retry storms: all callers retrying simultaneously overwhelmed the downstream service. 'Full Jitter' (Marc Brooker, AWS, 2015) added randomness to the backoff period, solving synchronized retry storms. gRPC's built-in retry policy (2019) standardised retry configuration at the protocol level. The discipline evolved from 'retry on any exception' to 'retry only idempotent operations, with jitter, within a deadline budget.'
---

### 📘 Textbook Definition

A **retry strategy** is a resilience pattern that re-executes a failed remote call up to a maximum number of attempts, applying a wait interval (often with exponential backoff and jitter) between attempts. Retries are applied only to _retryable_ errors - typically transient network faults or 5xx responses - never to client errors (4xx) or non-idempotent operations without idempotency keys. The strategy is bounded to prevent retry storms and combined with circuit breakers to stop retrying already-failing services.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
When a call fails due to a temporary glitch, try again - but not forever, and not all at once.

**One analogy:**

> If your first knock on a door gets no answer, you knock again - maybe twice more - waiting a few seconds between each. But you don't hammer the door a hundred times, and you don't knock again if a sign says "DO NOT DISTURB."

**One insight:**
The most dangerous retry is an unbounded one without backoff. A service with 10,000 clients all retrying at the same fixed interval amplifies load by 3–5× at exactly the moment the service is most struggling to recover.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Some failures are transient (network blip, momentary overload) and will self-heal.
2. Some failures are permanent (bug, missing resource) and retrying wastes resources.
3. Retrying non-idempotent operations (POST /order) without safeguards causes duplicate side effects.

**DERIVED DESIGN:**
Given these invariants, a correct retry strategy must:

1. **Classify the error**: only retry retryable errors (network timeouts, 503, 429).
2. **Back off**: wait longer after each failure to avoid amplifying load.
3. **Add jitter**: randomise wait times so all clients don't retry at the same instant.
4. **Limit attempts**: stop after N retries to prevent infinite loops.
5. **Check idempotency**: only retry safely-retryable operations.

**Exponential backoff formula:**

```
wait = min(max_wait, base_wait × 2^attempt)
with_jitter = wait × random(0.5, 1.0)
```

Example: base=100ms, attempt 1=100ms, 2=200ms, 3=400ms, 4=800ms, cap at 1s.

**THE TRADE-OFFS:**
**Gain:** Transient faults become invisible to users; resilience to brief downstream instability.
**Cost:** Increased latency when retries are needed; amplified load on struggling services; complexity in tracking retry state; risk of double-execution without idempotency.

---

### 🧪 Thought Experiment

**SETUP:**
1,000 clients call a payment service. The payment service restarts and is unavailable for 2 seconds. All clients fail simultaneously.

**WHAT HAPPENS WITHOUT PROPER RETRY:**

- No retry: 1,000 users see failure.
- Naive fixed-interval retry (all retry after 500ms): service restarts and immediately receives 3,000 requests (original + 2 retries), overwhelming it and extending the outage.

**WHAT HAPPENS WITH EXPONENTIAL BACKOFF + JITTER:**
Clients retry with random delays spread across 0–2 seconds. When the service comes back, it receives a trickle of requests that grows as healthy responses return confidence. The service recovers smoothly. Within 3–5 seconds, all 1,000 clients have succeeded.

**THE INSIGHT:**
Jitter is not an optimisation - it's essential for correctness. Without it, all retrying clients synchronise into a thundering herd that can prevent recovery entirely.

---

### 🧠 Mental Model / Analogy

> Imagine 100 people trying to get through a revolving door that's temporarily stuck. Without backoff: they all push harder at the same time, jamming it further. With backoff + jitter: each person waits a slightly different random interval before pushing again, allowing the door to clear.

- "People trying to get through" → client requests retrying
- "Revolving door stuck" → service temporarily overloaded
- "Everyone pushing at once" → retry storm
- "Random wait intervals" → jitter
- "Growing wait time" → exponential backoff
- "Giving up after 5 tries" → max retry limit

Where this analogy breaks down: in software, idempotency matters - if pushing the door twice charges you twice, you need a different approach (idempotency key) before you can safely push again.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
If something fails, try again - but be polite about it. Wait a bit before retrying, try only a few times, and know when to give up.

**Level 2 - How to use it (junior developer):**
Only retry on transient errors: `IOException`, `SocketTimeoutException`, HTTP 502/503/504, and HTTP 429 (with Retry-After). Never retry on 400, 401, 403, 404 - those won't get better. Always set a maximum retry count (3–5 is typical). Use exponential backoff with jitter. Never retry `POST` or `DELETE` calls that aren't idempotent without an idempotency key.

**Level 3 - How it works (mid-level engineer):**
Resilience4j's `Retry` wraps a supplier in a loop: on exception, check if it matches the retry predicate, wait the calculated interval (exponential + jitter), and re-invoke. State machine: IDLE → RETRY_ATTEMPT → SUCCESS | RETRY_EXHAUSTED. Circuit breaker integration: after N failures, circuit opens and retries are skipped entirely. Retry budgets: at the infrastructure level, set a global retry budget - e.g., total retries across all instances cannot exceed 10% of traffic, preventing a widespread failure from amplifying 10×.

**Level 4 - Why it was designed this way (senior/staff):**
The interaction between retries, timeouts, and concurrency is the hard problem. If you set timeout=500ms and max_retries=3, the worst-case latency is 1500ms (3 × 500ms) before any backoff. With exponential backoff up to 1s, worst case is 500 + 500 + 1000 + 1000ms = 3s. This determines your SLA ceiling. At Google scale, distributed retry logic is replaced by deadline propagation - a global budget per request that all hops share, preventing the N-layer retry multiplication problem (if each of 5 hops retries 3×, a single failure can cause 3⁵=243 upstream calls).

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│           Retry Strategy - Attempt Flow                 │
└─────────────────────────────────────────────────────────┘

Call attempt 1 ─────────────────────────► [Service]
                                             │
                              SocketTimeout ◄┘  (transient)
                                 │
                         Wait: 100ms + jitter
                                 │
Call attempt 2 ─────────────────────────► [Service]
                                             │
                                   HTTP 503 ◄┘  (transient)
                                 │
                         Wait: 200ms + jitter
                                 │
Call attempt 3 ─────────────────────────► [Service]
                                             │
                                   HTTP 200 ◄┘  ✓ SUCCESS
```

**Retry decision matrix:**

```
HTTP 200 → success, stop
HTTP 400 → client error, DON'T retry
HTTP 401 → auth error, DON'T retry
HTTP 404 → not found, DON'T retry
HTTP 429 → rate limited, retry after Retry-After header
HTTP 500 → server error, retry (transient)
HTTP 502 → bad gateway, retry
HTTP 503 → service unavailable, retry
HTTP 504 → timeout, retry
IOException → retry
SocketTimeoutException → retry
```

**Happy path:** Attempt 1 succeeds; no retry needed; user sees normal latency.
**Error path:** All retries exhausted → throw final exception → fallback strategy activates.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
[Request] → [Service A]
  → [Retry wrapper ← YOU ARE HERE]
  → [Attempt 1 → B responds 200ms]
  → [Response back to caller]
```

**FAILURE PATH:**

```
[B fails] → [Retry: wait 100ms → attempt 2]
  → [B still fails] → [Retry: wait 200ms → attempt 3]
  → [B still fails] → [RetryExhaustedException]
  → [Fallback: return cached result or error]
  → [Circuit breaker records 3 failures]
```

**WHAT CHANGES AT SCALE:**
At 10k RPS, a 1% failure rate means 100 failures/sec - each retried up to 3× adds 300 extra calls. If backoff brings them 500ms later, that's still 600 retries/sec above normal load. At 100k RPS, retry amplification can double or triple load on a struggling service. Teams introduce retry budgets (max total retries ≤ X% of traffic) and shift to hedging (parallel speculative requests, first response wins) for latency-sensitive paths.

---

### 💻 Code Example

**Example 1 - Wrong: unlimited retry with no backoff:**

```java
while (true) {  // DANGEROUS - infinite loop
  try {
    return paymentClient.charge(request);
  } catch (Exception e) {
    // Retries immediately, hammers downstream
    log.warn("Retrying...");
  }
}
```

**Example 2 - Right: Resilience4j retry with backoff:**

```java
RetryConfig config = RetryConfig.custom()
  .maxAttempts(3)
  .waitDuration(Duration.ofMillis(100))
  .intervalFunction(
    IntervalFunction.ofExponentialRandomBackoff(
      100, 2.0, 0.5, 1000))  // base, mult, jitter, max
  .retryExceptions(
    SocketTimeoutException.class,
    ServiceUnavailableException.class)
  .ignoreExceptions(
    ClientErrorException.class)  // don't retry 4xx
  .build();

Retry retry = Retry.of("payment", config);

CheckedFunction0<PaymentResult> decorated =
  Retry.decorateCheckedSupplier(retry,
    () -> paymentClient.charge(request));

return Try.of(decorated)
  .recover(Exception.class, e -> PaymentResult.failed(e))
  .get();
```

**Example 3 - Production: idempotent retry with key:**

```java
// Generate idempotency key BEFORE the retry loop
// so all attempts use the SAME key
String idempotencyKey = UUID.randomUUID().toString();

RetryConfig config = RetryConfig.custom()
  .maxAttempts(3)
  .intervalFunction(
    IntervalFunction.ofExponentialRandomBackoff(
      200, 2.0, 0.5, 2000))
  .retryOnException(e ->
    e instanceof IOException ||
    (e instanceof HttpException &&
      ((HttpException) e).status() >= 500))
  .build();

return Retry.decorateSupplier(
  Retry.of("payment", config),
  () -> paymentClient.charge(
    request.withIdempotencyKey(idempotencyKey))
).get();
```

---

### ⚖️ Comparison Table

| Approach                         | Transient Fault Handling | Load Impact            | Safe for Non-Idempotent?   |
| -------------------------------- | ------------------------ | ---------------------- | -------------------------- |
| **Exponential Backoff + Jitter** | Excellent                | Low (spread)           | Yes (with idempotency key) |
| Fixed Interval Retry             | Good                     | High (thundering herd) | Yes (with idempotency key) |
| Immediate Retry                  | Good for fast transients | Very High              | Risky                      |
| No Retry                         | None                     | None                   | N/A                        |
| Hedging (parallel)               | Excellent for latency    | Higher (2× calls)      | Yes                        |

**How to choose:** Use **exponential backoff with jitter** for all retry strategies. Add **hedging** only for read paths where latency is more important than cost.

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                        |
| ------------------------------------------- | ------------------------------------------------------------------------------ |
| Retrying always helps recover from failures | Retrying during a real outage amplifies load and delays recovery               |
| All 5xx errors should be retried            | 500 Internal Server Error from a bug won't be fixed by retrying                |
| Retry is safe for POST requests             | POST creates resources - retry without idempotency key creates duplicates      |
| More retries = more resilient               | Past 3 retries, you're likely hitting a real failure, not a transient one      |
| Backoff means waiting fixed intervals       | Backoff must be exponential AND randomised (jitter) to prevent thundering herd |

---

### 🚨 Failure Modes & Diagnosis

**Retry Storm**

**Symptom:** Service gets 5× normal traffic during an outage; CPU spikes; outage extends far longer than it should.

**Root Cause:** All clients retry simultaneously without jitter; exponential backoff not applied; or retry limit too high.

**Diagnostic Command:**

```bash
# Count retry attempts in logs
grep "retrying" /var/log/service/*.log | \
  awk '{print $1}' | uniq -c | sort -rn | head -10
```

**Fix:** Add jitter to backoff; reduce max retries; introduce circuit breaker.

**Prevention:** Design with retry budget: total retries ≤ 5–10% of normal traffic volume.

---

**Silent Data Duplication**

**Symptom:** Customers report duplicate charges; orders doubled; emails sent twice.

**Root Cause:** Non-idempotent POST retried without idempotency key; network timed out after server committed but before client received response.

**Diagnostic Command:**

```bash
# Find duplicate idempotency keys (should be 0)
grep "idempotency_key" payment-service.log | \
  awk '{print $NF}' | sort | uniq -d
```

**Fix:** Add idempotency key to all mutating operations before enabling retry.

**Prevention:** Code review requirement: no retry on POST/PUT/DELETE without idempotency key.

---

**Retrying on Non-Retryable Errors**

**Symptom:** 400 Bad Request errors adding 3× latency; users see slow error responses.

**Root Cause:** Retry predicate too broad - retrying on all exceptions including client errors that will never succeed.

**Diagnostic Command:**

```bash
# Check which HTTP status codes are being retried
grep "Retry attempt" service.log | grep "HTTP 4" | wc -l
```

**Fix:** Explicitly whitelist retryable exceptions/status codes (5xx, network errors, 429). Never retry 4xx.

**Prevention:** Define and test retry predicate: `retryOn(IOException, 502, 503, 504, 429)` explicitly.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Timeout Strategy` - timeouts define when a call fails and needs to be retried
- `Inter-Service Communication` - the synchronous call patterns that need retry logic
- `Idempotency (Distributed)` - prerequisite for safe retry of mutating operations

**Builds On This (learn these next):**

- `Circuit Breaker (Microservices)` - stops retrying calls to services that are in hard failure
- `Fallback Strategy` - defines behaviour when all retries are exhausted
- `Exponential Backoff (Task)` - the backoff algorithm detail

**Alternatives / Comparisons:**

- `Fallback Strategy` - complementary: what to do when retries fail
- `Rate Limiting (Microservices)` - controls how many retries callers can make per window
- `Chaos Engineering` - tests retry logic under simulated failure conditions

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Bounded, backoff-delayed re-attempt of    │
│              │ failed remote calls                       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Transient faults surface as user-visible  │
│ SOLVES       │ errors; inconsistent ad-hoc retry code    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Jitter is mandatory - without it, retries │
│              │ form a thundering herd and amplify failure │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Calling any external service; transient   │
│              │ faults are expected (cloud environments)  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Responding to 4xx errors; non-idempotent  │
│              │ ops without idempotency keys; real outages│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Transparent recovery vs retry amplification│
│              │ and latency increase                      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Try again, but politely and not forever" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Circuit Breaker → Fallback Strategy →     │
│              │ Exponential Backoff                       │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Retries are not free. Each retry attempt adds latency, creates additional load on the downstream service, and can amplify a partial outage into a full one. The decision to retry must be based on three criteria: the idempotency of the operation (only retry idempotent operations), the retriability of the failure (network errors: retriable; business validation errors: not retriable), and the deadline budget (only retry if there is enough time for the retry to succeed within the caller's remaining deadline).

**Where else this pattern appears:**
- **Kafka producer retries:** A Kafka producer with `retries=5` and `retry.backoff.ms=100` applies retry strategy at the messaging layer - the same pattern as HTTP client retry, at a different protocol.
- **Database connection retry:** A connection pool that retries connecting to a database when the connection is refused is applying retry strategy at the infrastructure level.
- **DNS resolution retry:** A DNS client that retries resolution on SERVFAIL is applying retry strategy to infrastructure service discovery.

---

### 💡 The Surprising Truth

The 'idempotency key' pattern for retry safety has a subtle failure mode: idempotency keys are only effective if the server stores them in the same transaction as the operation. If the server processes the payment and commits it, then tries to store the idempotency key and fails (network timeout before the key write is acknowledged), the next retry arrives with the same key, finds no record of it, and processes the payment again. The idempotency key must be committed atomically with the business operation in a single database transaction - not written after the operation completes.
---

### 🧠 Think About This Before We Continue

**Q1.** You have Service A calling B with max 3 retries, exponential backoff (100ms base, 2× multiplier). B calls C with max 3 retries, same config. A user request triggers A→B→C. C fails with a transient error. Trace the exact worst-case call count from A to B, and from B to C. Calculate the maximum latency this request could take. Why is this called the "retry multiplication problem" and how does deadline propagation solve it?

*Hint:* Think about the multiplication: A tries B up to 4 times (1 original + 3 retries). Each B→C call can try C up to 4 times. Maximum B→C calls: 4 * 4 = 16. Worst-case latency: A's backoff ladder (100 + 200 + 400ms) plus B's backoff ladder for C (100 + 200 + 400ms). Deadline propagation solves this by passing the remaining deadline to B: if A's remaining deadline is 300ms, B can only attempt one C call (because 100ms backoff would exceed the 300ms budget), preventing the multiplication.

**Q2.** Your payment service processes `POST /charge`. The network between your gateway and payment service drops 0.5% of responses _after_ the payment was committed. You add a retry with 3 attempts and exponential backoff with an idempotency key. Six months later, your operations team reports that 0.3% of charges are duplicated. Diagnose what went wrong with the idempotency key implementation and describe the correct fix.

*Hint:* Think about what '0.3% duplicate charges' means in the idempotency key flow: the server committed the charge AND wrote the idempotency key. But the network dropped the response. Correct idempotency key implementation: store the idempotency key in the SAME transaction as the charge record. The bug is storing the key after the transaction commits (two separate writes). Fix: write both the charge record and the idempotency key in a single atomic transaction so that either both are committed or neither is.

**Q3 (Design Trade-off):** Your payment service accepts `POST /charge` with an idempotency key. It calls an external payment processor that does not support idempotency keys. Design the complete system so that `POST /charge` is safe to retry end-to-end, even though the external processor is not idempotent.

*Hint:* Think about where idempotency can be enforced before calling the external processor: check if this idempotency key already has a committed result in your local database before calling the external API. If a result exists, return it directly. If not, call the external API and store the result atomically with the idempotency key. Explore whether the Outbox pattern (write payment command to outbox table in same transaction as idempotency key check, a background relay calls the external API exactly once) provides stronger exactly-once guarantees than an inline synchronous approach.
