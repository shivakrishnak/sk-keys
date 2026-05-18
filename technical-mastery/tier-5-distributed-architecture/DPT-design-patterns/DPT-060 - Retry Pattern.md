---
id: DPT-060
title: Retry Pattern
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-005
used_by: DPT-059, DPT-064, DPT-065
related: DPT-057, DPT-059, DPT-086, DPT-085
tags:
  - pattern
  - resilience
  - intermediate
  - fault-tolerance
  - distributed-systems
  - transient-failure
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 60
permalink: /technical-mastery/design-patterns/retry/
---

⚡ TL;DR - The Retry Pattern automatically re-attempts
a failed operation when the failure is likely transient,
using backoff strategies (fixed, exponential, jitter) to
avoid overwhelming a recovering service.

| #60 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005 | |
| **Used by:** | DPT-059, DPT-064, DPT-065 | |
| **Related:** | DPT-057, DPT-059, DPT-086, DPT-085 | |

---

### 🔥 The Problem This Solves

**TRANSIENT FAILURES ARE REAL:**
In distributed systems, calls fail transiently for reasons
unrelated to correctness:
- Network packet loss: the connection dropped for 50ms
- Pod restart: the target pod was restarting (Kubernetes
  rolling deploy), another instance handles the request
- GC pause: the target JVM paused for 200ms (GC)
- Load spike: the target is momentarily overloaded,
  the request was rejected with 503

**THE PROBLEM:**
Without retry: these transient failures become user-visible
errors. The user gets a failure for a request that would
have succeeded if tried 500ms later.

**THE NAÏVE FIX AND ITS FAILURE:**
"Just retry immediately."
50,000 clients all hit the same service. The service
hiccups for 100ms (GC pause). 50,000 × 3 retries =
150,000 requests hit the service in the next 100ms.
The service is now ACTUALLY overwhelmed (thundering herd).
Retries caused what they tried to prevent.

**THE REAL SOLUTION:**
Retry + exponential backoff + jitter. Not just retry.

---

### 📘 Textbook Definition

The **Retry Pattern** is a resilience pattern that
transparently re-attempts a failed operation a configured
number of times before propagating the failure to the
caller. It applies only to transient failures (network
glitches, service restarts, temporary overload) and uses
a backoff strategy to space out retry attempts.

**Backoff strategies:**
- **Fixed delay**: retry after exactly N milliseconds each time.
  Problem: all clients retry at the same intervals
  (synchronized thundering herd).
- **Exponential backoff**: retry after N, 2N, 4N, 8N
  milliseconds. Spreads retries over time as the interval grows.
- **Exponential backoff + jitter**: retry after
  `(N × 2^attempt) + random(0, N)`. Jitter randomizes
  the retry timing across clients, preventing synchronized
  retries (de-synchronized thundering herd).

**When to retry vs NOT to retry:**
- **Retry**: 5xx errors (500, 502, 503), connection timeouts,
  network errors, 429 Too Many Requests (with backoff)
- **Do NOT retry**: 4xx errors (except 429) - 400 Bad Request,
  401 Unauthorized, 404 Not Found. These are not transient.
  Retrying a 400 never succeeds and wastes resources.
- **Never retry**: non-idempotent operations (POST /payment/charge)
  unless you have idempotency keys (DPT-085).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Retry = try again on transient failure, wait longer
each time, add randomness to avoid synchronized storms.

**One analogy:**
> Calling a busy restaurant to make a reservation.
> First attempt: line is busy. Wait 1 minute, try again.
> Still busy. Wait 2 minutes. Still busy. Wait 4 minutes.
> Each wait is longer (exponential). If you and 100 friends
> all call at exactly the same intervals: you all hit
> redial at the same second (thundering herd). If you
> each wait a random 0-30 seconds extra: your calls
> are spread out and the restaurant's phone is never
> overwhelmed.
>
> Exponential backoff + jitter = spread out retry storms.

**One insight:**
The most common mistake with retries: forgetting jitter.
Exponential backoff without jitter synchronizes clients
(they all backoff to 2s, then all retry at 2s). With
jitter: clients retry at 2.1s, 1.8s, 2.4s, 2.0s, etc.
The recovering service sees a gradual ramp-up, not a spike.

---

### 🔩 First Principles Explanation

**RETRY BUDGET:**
Total retries across all clients should not exceed the
capacity the service can handle. If a service handles
1,000 req/sec at capacity and has 50,000 clients:
- Each client making 1 call at normal rate: 50,000 req/sec
  (already over capacity - this is why the service failed)
- Each client retrying 3 times immediately: 150,000 req/sec
  (catastrophic)
- Each client retrying with exponential backoff + jitter:
  retries spread over 10-60 seconds, effective peak:
  ~55,000 req/sec initially, decaying to normal over time

**IDEMPOTENCY REQUIREMENT:**
Retry assumes the operation is safe to repeat
(idempotent). GET requests: always safe to retry.
POST /payment/charge: NOT safe to retry without idempotency
keys. Without idempotency keys: a "payment that succeeded
but the response was lost" retried = double-charge.

**RETRY BUDGET (circuit breaker integration):**
Retry indefinitely = never give up = cascading failure.
Retry budget: limit total retries. After N retries: give
up and let the circuit breaker (DPT-057) open. Retry
and Circuit Breaker are complementary:
- Retry: handles transient single failures (short-term)
- Circuit Breaker: handles sustained failures (medium-term)

---

### 🧪 Thought Experiment

**THUNDERING HERD WITHOUT JITTER:**
100 services all call the same Payment Service.
Payment Service GC pause: 200ms.
All 100 services: connection refused for 200ms.
All 100 services: first retry after 1 second.
All 100 services simultaneously retry at T+1000ms.
Payment Service has just recovered and is hit with 100×
its normal traffic in a burst.
Result: Payment Service becomes overloaded again.

**WITH JITTER:**
Each service retries after `1000ms + random(0, 500)ms`.
Retries spread over 500ms window (1000-1500ms).
Payment Service sees: ~200 retries/sec for 500ms.
Normal load resumes. Payment Service recovers cleanly.

---

### 🧠 Mental Model / Analogy

> Retry Pattern = "polite caller" protocol.
> When you call someone and get voicemail, you don't
> call back every second (fixed immediate retry = rude).
> You wait a few minutes, then try again (fixed delay).
> Better: wait progressively longer if they keep not answering
> (exponential backoff - they might be in a meeting).
> If you're calling with a group, you don't all call back
> at the exact same minute (thundering herd); you each
> wait a slightly different amount of time (jitter).
>
> Most retry implementations get "wait longer" right.
> Almost all forget "wait a slightly different amount."
> Jitter is the difference between polite retry and herd.

---

### 📶 Gradual Depth - Three Levels

**Level 1 - Basic retry:**
Try the call. If it fails: wait 1 second, try again.
Wait 2 seconds, try again. Wait 4 seconds, try again.
After 3 retries: give up and return the error.

**Level 2 - Resilience4j Retry configuration:**
Configure which exceptions trigger retry, how many
attempts, what backoff to use. Add the `@Retry` annotation
on the method. Add a fallback method for when all retries
are exhausted.

**Level 3 - Retry + Circuit Breaker composition:**
The correct order: Retry INSIDE Circuit Breaker.
`CircuitBreaker(Retry(operation))` - not the reverse.
If Retry is outside Circuit Breaker, retries continue
even when the circuit is OPEN (wasting retries on a
known-failed downstream). Retry inside Circuit Breaker:
each retry attempt is counted by the Circuit Breaker.
When failure rate exceeds threshold: Circuit Breaker opens,
blocking further retries automatically.

---

### ⚙️ How It Works (Mechanism)

```
Retry with Exponential Backoff + Jitter
┌─────────────────────────────────────────────────────────┐
│ T=0     → Call Payment Service → FAIL (503)             │
│ T=1.1s  → Retry 1 (1s + 100ms jitter) → FAIL (503)     │
│ T=3.2s  → Retry 2 (2s + 200ms jitter) → FAIL (503)     │
│ T=7.4s  → Retry 3 (4s + 400ms jitter) → SUCCESS        │
│                                                         │
│ Backoff formula:                                        │
│   delay = min(max_delay, base × 2^attempt + jitter)    │
│   jitter = random(0, base × 2^attempt × jitter_factor) │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Immediate retry (no backoff - dangerous):**

```java
// BAD: Immediate retry with no backoff or jitter
// Under failure: 50,000 clients all retry instantly
// Thundering herd: service overloaded

public PaymentResult chargeWithBadRetry(PaymentRequest req) {
    int attempts = 0;
    while (attempts < 3) {
        try {
            return paymentService.charge(req);
        } catch (ServiceUnavailableException e) {
            attempts++;
            // NO SLEEP. Retry immediately.
        }
    }
    throw new PaymentException("Failed after 3 retries");
}
```

**Example 2 - Resilience4j Retry (correct):**

```java
// GOOD: Resilience4j Retry with exponential backoff + jitter

// application.yml:
/*
resilience4j:
  retry:
    instances:
      payment-service:
        maxAttempts: 3              # 1 initial + 2 retries
        waitDuration: 1s            # Base wait duration
        enableExponentialBackoff: true
        exponentialBackoffMultiplier: 2
        enableRandomizedWait: true  # Jitter
        randomizedWaitFactor: 0.5   # Random 0-50% of wait
        retryExceptions:
          - java.net.ConnectException
          - resilience4j.circuitbreaker.CallNotPermittedException
        ignoreExceptions:
          - com.example.PaymentDeclinedException  # Don't retry 4xx
          - java.lang.IllegalArgumentException
          # Don't retry bad input
*/

@Service
class PaymentClient {

    @Retry(name = "payment-service",
           fallbackMethod = "retryExhaustedFallback")
    public PaymentResult charge(PaymentRequest req) {
        return paymentService.charge(req);
    }

    // Fallback: all retries exhausted
    public PaymentResult retryExhaustedFallback(
            PaymentRequest req, Exception e) {
        log.error("All retries exhausted for order {}: {}",
            req.getOrderId(), e.getMessage());
        return PaymentResult.failed("Service unavailable");
    }
}
```

**Example 3 - Retry inside Circuit Breaker (correct composition):**

```java
// CORRECT order: Retry INSIDE Circuit Breaker
// Retry is the inner decorator; CircuitBreaker is outer.
// If the circuit OPENS: retries stop immediately.

@CircuitBreaker(name = "payment-service",
                fallbackMethod = "paymentFallback")
@Retry(name = "payment-service")   // Retry runs first (inner)
public PaymentResult charge(PaymentRequest req) {
    return paymentService.charge(req);
}

// Annotation order: Spring applies decorators in reverse order
// (outermost annotation applied last = outermost in call chain).
// Result: CircuitBreaker(Retry(charge)) - correct.
```

**Example 4 - Idempotency key for safe retry:**

```java
// Safe to retry POST /payment/charge with idempotency key.
// Even if retry succeeds after a "lost response":
// the server recognizes the idempotency key and returns
// the SAME result (no double-charge).

public PaymentResult charge(PaymentRequest req) {
    String idempotencyKey = UUID.randomUUID().toString();
    // Store this key with the order before calling payment
    orderRepo.saveIdempotencyKey(req.getOrderId(), idempotencyKey);

    return restTemplate.exchange(
        RequestEntity.post("/payment/charge")
            .header("Idempotency-Key", idempotencyKey)
            .body(req),
        PaymentResult.class
    ).getBody();
}
// Now this method is safe to retry: DPT-085 Idempotency Pattern.
```

---

### ⚖️ Retry Configuration Reference

| Parameter | Conservative | Aggressive | Recommended |
|---|---|---|---|
| Max attempts | 2 | 5 | 3 |
| Initial wait | 500ms | 100ms | 1s |
| Backoff multiplier | 3x | 1.5x | 2x |
| Max wait | 30s | 5s | 10s |
| Jitter factor | 25% | 10% | 50% |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Retry is always safe | Retry is only safe for IDEMPOTENT operations. Retrying non-idempotent operations (charge payment, send email, create order) causes duplicate side effects unless idempotency keys are used |
| More retries = more resilience | More retries = more load on a struggling downstream = potential amplification of the outage. Retry budget matters. Limit retries + use circuit breaker to stop retrying persistently failing services |
| Retry and Circuit Breaker are alternatives | They are complementary. Retry: handle transient single failure (milliseconds). Circuit Breaker: handle sustained failure (seconds-minutes). Use both, with Retry INSIDE Circuit Breaker |
| Exponential backoff without jitter is sufficient | Exponential backoff synchronizes clients at each power-of-2 interval. Jitter is REQUIRED to desynchronize clients and prevent thundering herd. Never use exponential backoff without jitter in a high-concurrency environment |

---

### 🚨 Failure Modes & Diagnosis

**Thundering Herd After Recovery**

**Symptom:**
Service B recovers from an outage. 30 seconds later,
it crashes again. Error logs show a burst of 50,000
requests at exactly the time of recovery.

**Root Cause:**
50,000 clients were retrying with the same exponential
backoff (2s, 4s, 8s, 16s). After the outage: all clients
were at the same retry interval. When the service
came back up, all 50,000 clients retried simultaneously.

**Diagnosis:**
Check retry configuration for `enableRandomizedWait` or
`jitterFactor`. If missing: add jitter. Plot client retry
timing: all clients retrying at T+16000ms indicates
no jitter.

**Fix:**
Add jitter to retry configuration. Consider also adding
a circuit breaker to limit retries entirely after
sustained failure.

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ RETRY WHEN   │ 503 Service Unavailable, connection      │
│              │ timeout, network errors, 429 (with backof│
├──────────────┼──────────────────────────────────────────┤
│ NEVER RETRY  │ 4xx (except 429), non-idempotent POST    │
│              │ without idempotency key                  │
├──────────────┼──────────────────────────────────────────┤
│ BACKOFF      │ Exponential ALWAYS + Jitter ALWAYS       │
│              │ Never: immediate or fixed retry          │
├──────────────┼──────────────────────────────────────────┤
│ COMPOSITION  │ CircuitBreaker(Retry(op)) - correct      │
│              │ Retry(CircuitBreaker(op)) - wrong        │
├──────────────┼──────────────────────────────────────────┤
│ LIBRARY      │ Resilience4j: @Retry(name="svc")         │
│              │ Configure backoff in application.yml     │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-061: Pattern Selection Framework     │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Retry transient failures (5xx, timeouts) with exponential
   backoff + JITTER (jitter is not optional). Never retry
   4xx errors. Never retry without an idempotency strategy
   for non-idempotent operations.
2. Retry INSIDE Circuit Breaker: `CircuitBreaker(Retry(op))`.
   Retry handles transient single failures (short-term).
   Circuit Breaker handles sustained failures (medium-term).
   They are complementary, not alternatives.
3. Thundering herd: the failure mode of retry without jitter.
   All clients retry at the same intervals. The recovering
   service is hit with a synchronized burst. Jitter prevents
   this by randomizing each client's retry timing.

