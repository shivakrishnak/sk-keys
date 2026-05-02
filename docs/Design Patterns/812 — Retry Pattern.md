---
layout: default
title: "Retry Pattern"
parent: "Design Patterns"
nav_order: 812
permalink: /design-patterns/retry-pattern/
number: "812"
category: Design Patterns
difficulty: ★★☆
depends_on: "Circuit Breaker Pattern, Bulkhead Pattern, Resilience4j, Distributed Systems"
used_by: "Microservices, HTTP clients, message consumers, distributed system clients"
tags: #intermediate, #design-patterns, #resilience, #distributed-systems, #fault-tolerance, #microservices
---

# 812 — Retry Pattern

`#intermediate` `#design-patterns` `#resilience` `#distributed-systems` `#fault-tolerance` `#microservices`

⚡ TL;DR — **Retry Pattern** automatically retries failed transient operations — with configurable backoff, jitter, and max attempts — preventing the need for manual retry logic in every client while handling temporary network glitches and transient service failures.

| #812            | Category: Design Patterns                                                    | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Circuit Breaker Pattern, Bulkhead Pattern, Resilience4j, Distributed Systems |                 |
| **Used by:**    | Microservices, HTTP clients, message consumers, distributed system clients   |                 |

---

### 📘 Textbook Definition

**Retry Pattern** (Microsoft Cloud Design Patterns; Michael Nygard, "Release It!", 2007): a resilience pattern where a failed operation is automatically attempted again a configurable number of times before returning a failure to the caller. Essential in distributed systems where transient failures (network glitches, brief unavailability, throttling responses) are expected and temporary. Key design considerations: which exceptions are retryable (transient vs. non-transient); backoff strategy (fixed, linear, exponential); jitter (randomized delay to prevent thundering herd); max attempts; interaction with circuit breaker (retry only in CLOSED state). Incorrect retry design (retrying non-transient errors, no backoff, no jitter) amplifies load on already-struggling downstream services.

---

### 🟢 Simple Definition (Easy)

Your HTTP call to an external API fails with a 503 (Service Unavailable — temporary). Without retry: the request fails and the user sees an error. With retry: automatically wait 1 second, try again. Still 503: wait 2 seconds, try again. Third attempt: succeeds. User never saw an error. Retry Pattern: automatically handle temporary failures that would self-resolve if tried again a moment later.

---

### 🔵 Simple Definition (Elaborated)

A notification service calls an SMS gateway. The gateway occasionally returns 429 (Too Many Requests) or 503 (Unavailable) for <1% of requests due to brief load spikes. Without retry: 1% of notifications silently fail. With naive retry (immediate, unlimited): if the gateway is truly down, 100 microservices × 100 threads × unlimited retries = gateway DDOS by your own system. With proper retry (exponential backoff + jitter + max 3 attempts + retry only on 429/503, not on 400/401): transient failures self-heal, non-transient failures fast-fail, no retry storm.

---

### 🔩 First Principles Explanation

**Retry strategies and the critical details that make retry safe:**

```
RETRYABLE vs. NON-RETRYABLE ERRORS:

  RETRYABLE (transient — may succeed on retry):
  ✓ 503 Service Unavailable (temporary overload)
  ✓ 429 Too Many Requests (rate limiting — back off and retry)
  ✓ 500 Internal Server Error (may be transient — retry with caution)
  ✓ Network timeout (transient connectivity issue)
  ✓ Connection reset (transient network issue)

  NON-RETRYABLE (permanent — retry wastes time and amplifies problems):
  ✗ 400 Bad Request (your request is malformed — retrying sends the same bad request)
  ✗ 401 Unauthorized (wrong credentials — retrying fails the same way)
  ✗ 403 Forbidden (access denied — retrying doesn't grant access)
  ✗ 404 Not Found (resource doesn't exist — retrying finds nothing)
  ✗ 422 Unprocessable Entity (business validation failure)

  CRITICAL: only retry on retryable errors.
  Retrying a 400: wastes time. Retrying a 401: wastes time + may trigger account lockout.

BACKOFF STRATEGIES:

  1. FIXED DELAY:
  Attempt 1 → FAIL → wait 1s → Attempt 2 → FAIL → wait 1s → Attempt 3
  Simple. Predictable. Problem: synchronized clients → thundering herd.

  2. EXPONENTIAL BACKOFF:
  Attempt 1 → FAIL → wait 1s → Attempt 2 → FAIL → wait 2s → Attempt 3 → FAIL → wait 4s
  Wait = baseDelay × 2^attempt
  Progressively backs off → gives downstream more recovery time.
  Problem: all clients still retry at the same time if they start simultaneously.

  3. EXPONENTIAL BACKOFF WITH JITTER (correct production approach):
  Wait = random(0, min(cap, baseDelay × 2^attempt))
  "Full Jitter" (AWS best practice): wait = random(0, min(cap, baseDelay × 2^attempt))
  "Equal Jitter": wait = (min(cap, baseDelay × 2^attempt) / 2) + random(0, same/2)

  WHY JITTER IS CRITICAL:
  100 microservice instances all fail at t=0.
  Fixed backoff: all retry at t=1s, t=2s, t=4s simultaneously.
  Each retry wave: 100 requests simultaneously hitting the recovering service.
  Service re-fails on each wave: recovery never happens.

  Jitter: each instance picks a random delay.
  Instead of 100 simultaneous retries: ~1 retry per 10ms → smooth recovery load.
  Service recovers gradually instead of being overwhelmed by retry storms.

RESILIENCE4J RETRY CONFIGURATION:

  resilience4j:
    retry:
      instances:
        smsGateway:
          maxAttempts: 3
          waitDuration: 500ms                  # base delay
          enableExponentialBackoff: true
          exponentialBackoffMultiplier: 2.0    # 500ms → 1000ms → 2000ms
          exponentialMaxWaitDuration: 10s      # cap at 10 seconds
          enableRandomizedWait: true           # jitter
          randomizedWaitFactor: 0.5            # ±50% jitter
          retryExceptions:
            - java.io.IOException
            - java.net.SocketTimeoutException
            - org.springframework.web.client.HttpServerErrorException$ServiceUnavailable
            - org.springframework.web.client.HttpServerErrorException$TooManyRequests
          ignoreExceptions:
            - com.app.exceptions.BusinessValidationException
            - org.springframework.web.client.HttpClientErrorException$BadRequest
            - org.springframework.web.client.HttpClientErrorException$Unauthorized
            - org.springframework.web.client.HttpClientErrorException$NotFound

RETRY + CIRCUIT BREAKER ORDERING:

  Correct order: CircuitBreaker(Retry(operation))

  Why: Retry retries the operation.
       CircuitBreaker counts the final result (after all retries).
       If 3 retries all fail → CircuitBreaker records 1 failure (the final failure).

  Incorrect order: Retry(CircuitBreaker(operation))
  Why wrong: CircuitBreaker counts each retry attempt as a separate failure.
             3 retries → 3 failures recorded → circuit opens prematurely.

  Resilience4j decorator order (outermost to innermost):
  Bulkhead → CircuitBreaker → RateLimiter → TimeLimiter → Retry → operation
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Retry:

- Transient failures (network glitches, brief service unavailability) surface as errors to users
- Manual retry logic in every client: repeated code, inconsistent behavior, no backoff strategy

WITH Retry:
→ Transient failures self-heal transparently. Consistent backoff + jitter strategy across all services. Non-transient errors fast-fail without retry overhead.

---

### 🧠 Mental Model / Analogy

> Calling a friend on a busy phone line. The line is briefly busy (transient — they're on another call). Strategy A: give up immediately — you'll never reach them. Strategy B: redial once per second forever — the line stays busy, you exhaust your patience (and annoy them). Strategy C: wait a random short delay, try again; if still busy, wait a little longer; try once more; if still busy after 3 attempts, leave a message. Retry with exponential backoff + jitter = Strategy C.

"Phone line briefly busy" = transient 503/network timeout
"Give up immediately" = no retry — user sees error for a self-resolving issue
"Redial once per second forever" = naive unlimited retry — thundering herd, no backoff
"Wait random short delay, then longer, then give up" = exponential backoff + jitter + max attempts
"Wrong number / disconnected phone" = non-retryable 400/401 — don't retry

---

### ⚙️ How It Works (Mechanism)

```
RETRY EXECUTION FLOW:

  Attempt 1 → FAIL (503) → Is retryable? YES → wait 500ms + jitter
  Attempt 2 → FAIL (503) → Is retryable? YES → wait 1000ms + jitter
  Attempt 3 → SUCCESS    → return result

  OR:

  Attempt 1 → FAIL (400) → Is retryable? NO → throw immediately (no retry)

  OR:

  Attempt 1 → FAIL (503) → Is retryable? YES → wait 500ms + jitter
  Attempt 2 → FAIL (503) → Is retryable? YES → wait 1000ms + jitter
  Attempt 3 → FAIL (503) → maxAttempts reached → throw MaxRetriesExceededException
  (→ Circuit Breaker records failure)
  (→ Fallback invoked if configured)

IDEMPOTENCY REQUIREMENT:

  SAFE TO RETRY: idempotent operations
  ✓ GET /products/123           — same result every time
  ✓ PUT /orders/123/status      — setting status to CONFIRMED is idempotent
  ✓ DELETE /sessions/abc        — deleting already-deleted session: 404 (idempotent)

  UNSAFE TO RETRY WITHOUT IDEMPOTENCY KEY:
  ✗ POST /orders                — may create duplicate orders
  ✗ POST /payments              — may double-charge

  SOLUTION for non-idempotent operations:
  Include idempotency key in request:
  POST /payments
  Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000

  Server: on retry with same key → return same response (not process again).
  Stripe, PayPal, Twilio all support Idempotency-Key header.
```

---

### 🔄 How It Connects (Mini-Map)

```
Transient failures surface as user errors without retry mechanism
        │
        ▼
Retry Pattern ◄──── (you are here)
(max attempts + exponential backoff + jitter + retryable exception list)
        │
        ├── Circuit Breaker: outer wrapper — CB fast-fails when retry fails repeatedly
        ├── Bulkhead: outer wrapper — limits concurrent retrying threads
        ├── Idempotent Consumer: required for safe retry of non-idempotent operations
        └── Throttling Pattern: 429 responses require retry-after header respecting retry
```

---

### 💻 Code Example

```java
// Spring Boot Retry with Resilience4j + Spring Retry fallback:

@Service @RequiredArgsConstructor @Slf4j
public class SmsNotificationService {

    private final SmsGatewayClient gateway;

    // Resilience4j: Circuit Breaker wraps Retry (correct order)
    @CircuitBreaker(name = "smsGateway", fallbackMethod = "smsFallback")
    @Retry(name = "smsGateway", fallbackMethod = "smsFallback")
    public NotificationResult sendSms(String phoneNumber, String message) {
        log.debug("Sending SMS to {}", phoneNumber);
        return gateway.send(new SmsRequest(phoneNumber, message));
    }

    public NotificationResult smsFallback(String phoneNumber, String message, Exception ex) {
        if (ex instanceof MaxRetriesExceededException) {
            log.error("SMS delivery failed after all retries for {}: {}", phoneNumber, ex.getMessage());
            // Queue for async retry via job scheduler:
            failedSmsQueue.enqueue(new FailedSms(phoneNumber, message));
            return NotificationResult.queued(phoneNumber);
        }
        if (ex instanceof CallNotPermittedException) {
            log.warn("SMS circuit breaker OPEN — queuing notification for {}", phoneNumber);
            failedSmsQueue.enqueue(new FailedSms(phoneNumber, message));
            return NotificationResult.queued(phoneNumber);
        }
        return NotificationResult.failed(phoneNumber, ex.getMessage());
    }
}

// application.yml — Retry configuration with exponential backoff + jitter:
resilience4j:
  retry:
    instances:
      smsGateway:
        maxAttempts: 3
        waitDuration: 300ms
        enableExponentialBackoff: true
        exponentialBackoffMultiplier: 2
        exponentialMaxWaitDuration: 5s
        enableRandomizedWait: true
        randomizedWaitFactor: 0.3             # ±30% jitter
        retryExceptions:
          - java.io.IOException
          - org.springframework.web.client.HttpServerErrorException
        ignoreExceptions:
          - org.springframework.web.client.HttpClientErrorException

# Attempt 1: immediate
# Attempt 2: wait 300ms ± 90ms (270-390ms)
# Attempt 3: wait 600ms ± 180ms (420-780ms)
# Total max wait: ~1.2 seconds before surfacing error
```

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| More retries = better resilience                 | Aggressive retries amplify load on already-struggling services. If 1,000 clients each retry 10 times: one failure event generates 10,000 requests against the recovering service. The recovering service is overwhelmed by retry traffic and can never recover. The right number of retries depends on the operation's typical transient failure duration and the system's tolerance for latency. For most cases: 3 attempts is sufficient. More retries: only with longer, properly jittered backoff. |
| Retry applies to all failed operations           | Retry is only appropriate for IDEMPOTENT or SAFE operations. POST /payments without an idempotency key: retrying on timeout may charge the user twice (the first request may have succeeded before timing out). For non-idempotent operations: use idempotency keys (Stripe model), or accept that retry is unsafe and only retry at the job/queue level with exactly-once semantics.                                                                                                                  |
| Retry and Circuit Breaker solve the same problem | They're complementary and solve different problems. Retry: handles transient failures by trying again. Circuit Breaker: detects sustained failure patterns and stops trying. Without Circuit Breaker: a permanently-failing service triggers retries on every request indefinitely. Without Retry: transient failures surface as errors. Together: retry handles transient; circuit breaker handles sustained failure.                                                                                 |

---

### 🔥 Pitfalls in Production

**Retry storm amplifying a partial outage into a full outage:**

```java
// ANTI-PATTERN — naive unlimited retry with no backoff:
public Response callInventory(Long productId) {
    int attempts = 0;
    while (true) {
        try {
            attempts++;
            return inventoryClient.get(productId);
        } catch (Exception e) {
            log.warn("Inventory call failed, attempt {}", attempts);
            // NO backoff. NO max attempts. NO jitter.
            // Immediately retries in a tight loop.
        }
    }
}

// Scenario:
// Inventory service: brief 5-second slowdown (GC pause)
// 100 service instances × 100 threads × tight retry loop
// = 10,000 requests/second hammering inventory during its GC pause
// Inventory cannot complete GC → stays paused → services keep retrying
// What was a 5-second GC pause becomes a 5-minute outage from retry amplification.

// FIX — proper retry with Resilience4j:
@Retry(name = "inventoryService")    // maxAttempts=3, exponential backoff, jitter
public Response callInventory(Long productId) {
    return inventoryClient.get(productId);
}
// During a 5-second GC pause:
// Attempt 1 fails → wait 500ms (with jitter) → Attempt 2 fails → wait 1000ms
// GC pause resolved → Attempt 3 succeeds.
// Only 3 requests per caller instead of thousands.
// Inventory recovers normally. No outage amplification.
```

---

### 🔗 Related Keywords

- `Circuit Breaker Pattern` — pair with Retry: Circuit Breaker wraps Retry (outer/inner)
- `Bulkhead Pattern` — outermost wrapper: limits concurrent retrying threads
- `Throttling Pattern` — 429 responses indicate throttling: respect Retry-After header
- `Idempotent Consumer` — required for safe retry of non-idempotent operations
- `Resilience4j` — Spring Boot library providing Retry + Circuit Breaker + Bulkhead

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Auto-retry transient failures. Exponential│
│              │ backoff + jitter prevents retry storms.  │
│              │ Only retry retryable (transient) errors. │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Transient failures expected (503, 429,   │
│              │ network timeout); idempotent operations; │
│              │ short-lived availability issues          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Non-transient errors (400/401/404);      │
│              │ non-idempotent ops without idempotency   │
│              │ keys; circuit is already OPEN            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Busy phone line: wait a random short    │
│              │  moment, try again; longer next time;   │
│              │  give up after 3 attempts."              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Circuit Breaker → Bulkhead → Idempotency │
│              │ Keys → Throttling → Resilience4j          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** AWS's "Building for the Cloud" documentation identifies "exponential backoff with full jitter" as superior to "exponential backoff without jitter" for preventing thundering herd problems. The difference: without jitter, all clients synchronized by a failure event retry at the same time intervals; with full jitter, retries are distributed randomly across the backoff window. Marc Brooker (AWS) proved mathematically that "equal jitter" provides better throughput than "full jitter" in some scenarios. Describe the three jitter strategies (none, equal jitter, full jitter) and their tradeoffs in terms of total work done vs. throughput.

**Q2.** Idempotency keys (the Stripe model: `Idempotency-Key: <UUID>` request header) enable safe retry of non-idempotent operations like payment processing. The server stores the idempotency key → response mapping for a window (Stripe: 24 hours). On retry with the same key: return the cached response instead of processing again. How do you implement idempotency key handling on the server side in Spring Boot? Describe the storage mechanism, the race condition when two requests arrive simultaneously with the same key (exactly-once semantics), and the appropriate TTL for the idempotency key cache.
