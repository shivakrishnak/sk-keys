---
id: DST-044
title: "Retry with Backoff"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-046, DST-045
used_by: DST-042
related: DST-042, DST-045, DST-046, DST-043
tags:
  - distributed
  - reliability
  - pattern
  - resilience
  - foundational
status: complete
version: 1
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 44
permalink: /distributed-systems/retry-with-backoff/
---

# DST-044 - Retry with Backoff

⚡ TL;DR - Retry with backoff automatically repeats a failed operation after a growing delay, converting transient network failures and temporary service overloads into eventual success — without hammering the failing service or causing a retry storm.

| Metadata        |                                    |     |
| :-------------- | :--------------------------------- | :-- |
| **Depends on:** | DST-046, DST-045                   |     |
| **Used by:**    | DST-042                            |     |
| **Related:**    | DST-042, DST-045, DST-046, DST-043 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A microservice calls another service. The call fails with a transient network hiccup (50ms packet loss). Without retry: the operation fails permanently and the user gets an error — for a problem that would have resolved itself in 50ms. Engineers add manual retry logic: `if fail: try again immediately`. This creates a new problem: if 1,000 clients all hit a failing service simultaneously and all retry immediately: the service (already struggling) gets 3,000 requests in 1 second (initial + 2 retries × 1,000 clients). The retry storm makes the outage worse.

**THE BREAKING POINT:**
Immediate retry amplifies load at the worst possible moment. A service with 5% error rate under normal load: if every caller retries twice immediately, effective load jumps 3× — potentially pushing error rate to 50%. The more clients retry, the worse the service performs, the more clients retry: a positive feedback loop. The insight: retries must be spaced out (backoff) and randomized (jitter) to prevent synchronized hammering.

**THE INVENTION MOMENT:**
Exponential backoff was used in Ethernet collision detection (CSMA/CD) since 1970s: when a collision occurs, each device waits a random exponential time before retrying. Aloha Protocol (1970): first use of backoff in a distributed network. Applied to service retries: exponential backoff + jitter prevents the "thundering herd" — 1,000 synchronized retriers become 1,000 retriers spread across a window, reducing peak load from 3,000 req/s to ~150 req/s.

**EVOLUTION:**
1970s: Ethernet CSMA/CD exponential backoff. 2007: AWS clients adopt exponential backoff (recommended in AWS docs). 2015: Marc Brooker's AWS blog post on "Exponential Backoff and Jitter" — introduces "full jitter" and "decorrelated jitter" formulas. 2018: AWS SDK v2 ships with built-in exponential backoff + full jitter. Today: all major SDKs (AWS, GCP, Azure, gRPC) include retry with backoff by default.

---

### 📘 Textbook Definition

**Retry with backoff** is a resilience pattern where a failed operation is automatically retried after a delay that increases between attempts. **Exponential backoff formula:** `delay = min(cap, base × 2^attempt)`. **Jitter variants:** (1) Full jitter: `sleep = random(0, min(cap, base × 2^attempt))` — uniform random in [0, cap]. (2) Equal jitter: `sleep = cap/2 + random(0, cap/2)`. (3) Decorrelated jitter: `sleep = min(cap, random(base, sleep × 3))` (Marc Brooker). (4) No jitter: `sleep = min(cap, base × 2^attempt)` — worst for thundering herd. **Key parameters:** `base` (initial delay, e.g., 100ms), `cap` (max delay, e.g., 30s), `maxAttempts` (e.g., 3-5), `retryOn` (which exceptions trigger retry). **Idempotency requirement:** retried operations MUST be idempotent (DST-045). Retrying a non-idempotent operation (e.g., charge payment) twice may cause double-processing. **Composability:** retry + circuit breaker + bulkhead form the standard resilience stack.

---

### ⏱️ Understand It in 30 Seconds

**One line:** On failure, wait a bit, then try again — wait longer each time to avoid overwhelming the recovering service.

> Retry with backoff is like pushing a stalled car. You push once (attempt 1). Nothing. You rest for 1 second, then push again (attempt 2). Rest 2 seconds, push again (attempt 3). You're not pushing 3 times simultaneously — you space them out. If 100 people push at once, randomly spaced (jitter), the car doesn't get crushed by simultaneous force.

**One insight:** The jitter is just as important as the backoff. Without jitter: 1,000 clients all back off to exactly the same delay — and retry simultaneously. Jitter converts synchronized hammering into spread-out probing.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Backoff prevents retry storms:** immediate retry = N callers all retry at T+0ms = N× load spike. Exponential backoff = N callers retry at different times spread across [0, cap] seconds = 1/N the peak load.
2. **Jitter breaks synchronization:** without jitter, clients with the same backoff formula retry at the same time (synchronized). Jitter adds randomness: `random(0, delay)` instead of `delay`. Unsynchronized = lower peak load.
3. **Retries only for transient failures:** idempotent, retriable errors: timeout, 503 (service unavailable), 429 (rate limited). Non-retriable: 400 (bad request), 401 (auth failure), 409 (conflict). Retrying non-retriable errors wastes time.
4. **Max attempts bound total delay:** with base=100ms, cap=30s, maxAttempts=5: worst-case delay before giving up = 100 + 200 + 400 + 800 + 1600 + cap = ~3.1s (without jitter). User can wait this long.

**DERIVED DESIGN:**

```
Full jitter implementation:
  attempt = 0
  while attempt < maxAttempts:
    try: return call()
    catch retriable error:
      delay = random(0, min(cap, base × 2^attempt))
      sleep(delay)
      attempt++
  throw MaxRetriesExceededException
```

**THE TRADE-OFFS:**
**Gain:** Converts transient failures to eventual success. Prevents retry storms (backoff + jitter). Transparent to caller.
**Cost:** Added latency (sum of backoff delays). Requires idempotent operations. May mask persistent failures (retrying a bug 5 times). Complexity in retry policy configuration.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Retrying inherently adds latency (wait between attempts). The optimal wait time depends on the service's recovery time distribution — unknown without observability.
**Accidental:** Which jitter formula is best (full jitter vs decorrelated). Marc Brooker's analysis (2015) shows: for spreading load, full jitter is nearly optimal. Decorrelated jitter has slightly better average performance but is harder to implement correctly.

---

### 🧪 Thought Experiment

**SETUP:** 1,000 clients call Service B simultaneously. Service B has a 5-second overload event (temporarily returns 503). Each client retries up to 3 times.

**NO JITTER (exponential backoff, base=100ms):**

- T=0: 1,000 initial requests → all fail.
- T=100ms: 1,000 first retries → all fail (service still struggling, 1,000 extra requests don't help).
- T=300ms: 1,000 second retries → service recovering but gets 1,000 simultaneous requests → re-overwhelmed.
- Peak load: 1,000 req/s synchronized waves → service recovery impeded.

**WITH FULL JITTER (random(0, min(cap, base × 2^attempt))):**

- T=0: 1,000 initial requests → all fail.
- T=0-100ms: first retries spread uniformly → ~10 req/s average. Service still recovering.
- T=100-400ms: second retries spread uniformly → ~3 req/s average.
- Service recovers at T=5s without additional overload.
- All 1,000 clients eventually succeed.
- Peak retry load: ~10-15 req/s vs 1,000 req/s without jitter.

**THE INSIGHT:** Jitter reduces peak retry load by N× (where N = number of synchronized clients). 1,000 clients with jitter ≈ 1 client without jitter. This is the thundering herd prevention.

---

### 🧠 Mental Model / Analogy

> Retry with backoff is like students raising their hands in class when the teacher asks a question everyone knows. Without protocol: all 30 students raise hands simultaneously — chaos. With protocol: each student waits a random delay before raising their hand. The teacher can call on students one at a time. The room doesn't erupt into simultaneous shouting (retry storm).

**Mapping:**

- **Students raising hands** → clients retrying
- **Simultaneous hand-raising** → no jitter (synchronized retries)
- **Random delay before raising** → jitter (desynchronized retries)
- **Teacher getting overwhelmed** → service overloaded by retry storm
- **Orderly Q&A** → jittered retries, manageable service load

Where this analogy breaks down: in class, the teacher controls who speaks. In distributed systems: there's no coordinator controlling retry timing — jitter provides decentralized coordination via randomness.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When a network call fails: try again. But don't try immediately — wait a little. And each time it fails again: wait a bit longer. And add some randomness so you don't retry at exactly the same time as everyone else. After 3-5 attempts: give up and report failure.

**Level 2 - How to use it (junior developer):**
Spring Retry:

```java
@Retryable(
  value = {IOException.class, HttpServerErrorException.class},
  maxAttempts = 3,
  backoff = @Backoff(
    delay = 100,       // initial delay ms
    multiplier = 2.0,  // 100ms, 200ms, 400ms
    random = true      // add jitter
  )
)
public Inventory getInventory(String id) {
  return inventoryClient.get(id);
}
```

Resilience4j: `RetryConfig.custom().maxAttempts(3).waitDuration(Duration.ofMillis(100)).retryExceptions(IOException.class).build()`.

**Level 3 - How it works (mid-level engineer):**
AWS SDK retry (v2) uses "full jitter" by default. Implementation: `sleep = random.nextDouble() × min(cap, base × Math.pow(2, attempt))`. Cap = 20,000ms. Base = 25ms. Max attempts: 3 (default, configurable). Retriable errors: `ThrottlingException`, `ServiceUnavailableException`, `RequestTimeoutException`. Non-retriable: `ValidationException`, `AccessDeniedException`. The SDK distinguishes "retriable" vs "non-retriable" by HTTP status and error code. gRPC retry policy (service config JSON): `"retryPolicy": {"maxAttempts": 5, "initialBackoff": "0.1s", "maxBackoff": "1s", "backoffMultiplier": 2, "retryableStatusCodes": ["UNAVAILABLE"]}`.

**Level 4 - Why it was designed this way (senior/staff):**
Marc Brooker's 2015 analysis compared four jitter strategies mathematically. Key finding: "full jitter" (uniform random in [0, cap]) produces the LOWEST mean call completion time under load, because it spreads retries most uniformly. "No jitter" is optimal for a single isolated client (no wasted delay), but terrible for N synchronized clients (all retry at T+delay simultaneously). "Decorrelated jitter" (`sleep = random(base, prev_sleep × 3)`) produces slightly lower mean completion time than full jitter for very high N, but is harder to implement correctly and maintain in code. The production recommendation: full jitter is the best balance of performance, simplicity, and correctness. The deeper insight: jitter is a form of load distribution in time — the same principle as hash-based sharding distributes load in space. Both use randomness to prevent hot spots.

**Expert Thinking Cues:**

- "Service is getting retry storms even with backoff" → Check if `random=true` (jitter enabled). No jitter = synchronized retries = storm. Also: check if multiple services are retrying to the same dependency — each service's retry amplifies the others. Add circuit breaker (DST-042) so circuit opens after threshold failures, stopping retries entirely rather than continuing to hammer.
- "Retry is making things worse — should I disable it?" → Only disable retries if: (1) the operation is non-idempotent (double-processing risk), or (2) the failure is not transient (a bug, not a temporary overload). For non-idempotent: fix the operation to be idempotent (DST-045) then re-enable retry. For persistent failures: circuit breaker + retry — circuit opens and stops retrying after threshold, preventing wasted retries.
- "Choosing between maxAttempts=3 and maxAttempts=10" → More attempts = more latency tolerance for recovery. But: user-visible operations (API calls from a UI) should have maxAttempts=2-3 (max total latency ~1-3s). Background jobs: maxAttempts=10-20 with large cap (30s). Never retry more than 5 times in a user-visible path — P99 latency becomes unacceptable.

---

### ⚙️ How It Works (Mechanism)

**Full jitter formula:**

```
base = 100ms, cap = 30000ms
Attempt 0: sleep = random(0, min(30000, 100×2^0))
                 = random(0, 100ms) → e.g., 47ms
Attempt 1: sleep = random(0, min(30000, 100×2^1))
                 = random(0, 200ms) → e.g., 163ms
Attempt 2: sleep = random(0, min(30000, 100×2^2))
                 = random(0, 400ms) → e.g., 312ms
Attempt 3: sleep = random(0, min(30000, 100×2^3))
                 = random(0, 800ms) → e.g., 544ms
Attempt 4: sleep = random(0, min(30000, 100×2^4))
                 = random(0, 1600ms) → e.g., 891ms

Without jitter (comparison):
Attempt 0: 100ms (deterministic, all clients same)
Attempt 1: 200ms (all clients retry at exactly T+300ms)
Attempt 2: 400ms (all clients retry at exactly T+700ms)
→ Thundering herd: synchronized waves

With full jitter:
1000 clients spread uniformly across [0, cap] interval
→ ~1000/cap req/ms average retry rate (no spikes)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**RETRY FLOW WITH CIRCUIT BREAKER COMPOSITION:**

```
Client  RetryWrapper  CircuitBreaker  ServiceB
  │          │               │            │
  │─call()──▶│               │            │
  │          │─check(CB)────▶│            │
  │          │ state=CLOSED  │            │
  │          │───────────────────────────▶│
  │          │◀──503 (error)──────────────│
  │          │ record failure (CB window) │
  │          │ attempt=0, sleep=47ms     │
  │          │ [wait 47ms]               │
  │          │─check(CB)────▶│            │
  │          │ state=CLOSED  │            │
  │          │───────────────────────────▶│ ← YOU ARE HERE
  │          │◀──200 OK───────────────────│
  │◀─result──│
```

**FAILURE PATH (circuit opens during retries):**

- After 5 failures: circuit opens.
- Retry wrapper checks circuit: OPEN → `CallNotPermittedException`.
- Retry wrapper: is `CallNotPermittedException` retriable? If no: give up immediately.
- Correct composition: circuit breaker opens → stops ALL retries. Don't retry when circuit is OPEN.

**WHAT CHANGES AT SCALE:**
At scale: coordinated retry storms are a latent risk. All clients retry when a dependency has an outage. Use exponential backoff + jitter as baseline. Add circuit breaker: after N failures, circuit opens across all clients (each client independently). This stops retries from clients whose circuit opened — reducing load on recovering service. Circuit opens at different times per client (different sample windows) → retries taper off organically.

---

### 💻 Code Example

**BAD - Immediate retry, no jitter, retries non-retriable errors:**

```java
// BAD: causes retry storms, retries non-retriable errors
public Payment processPayment(PaymentRequest req) {
    for (int i = 0; i < 10; i++) {
        try {
            return paymentClient.charge(req);
        } catch (Exception e) {
            // BAD: retries on ALL exceptions including
            // 400 Bad Request (bug, never succeed)
            // BAD: no sleep (immediate retry = storm)
            // BAD: retrying non-idempotent payment twice!
        }
    }
    throw new RuntimeException("Failed after 10 retries");
}
```

**GOOD - Resilience4j retry with full jitter, retriable errors only:**

```java
// GOOD: idempotent operation with correct retry config
@Service
public class InventoryService {
    private final Retry retry;
    private final InventoryClient client;

    public InventoryService(InventoryClient client) {
        this.client = client;
        this.retry = Retry.of("inventory",
            RetryConfig.custom()
                .maxAttempts(3)
                // Exponential backoff with full jitter:
                .intervalFunction(
                    IntervalFunction.ofExponentialRandomBackoff(
                        100,   // base delay ms
                        2.0,   // multiplier
                        30_000 // cap ms
                    ))
                // ONLY retry transient errors:
                .retryExceptions(
                    IOException.class,
                    HttpServerErrorException.class)
                // Do NOT retry:
                .ignoreExceptions(
                    HttpClientErrorException.class, // 4xx
                    IllegalArgumentException.class)  // bugs
                .build());

        // Log retry events:
        retry.getEventPublisher()
            .onRetry(e -> log.warn(
                "Retry attempt {} for inventory: {}",
                e.getNumberOfRetryAttempts(),
                e.getLastThrowable().getMessage()));
    }

    // This call is idempotent (GET = read-only)
    // Safe to retry
    public Inventory getInventory(String itemId) {
        return retry.executeSupplier(
            () -> client.get(itemId));
    }

    // For non-idempotent operations: add idempotency key
    // (see DST-045) before retrying
}
```

**Full jitter implementation (manual):**

```java
public static long fullJitter(int attempt,
                              long baseMs, long capMs) {
    long backoff = Math.min(capMs,
        (long)(baseMs * Math.pow(2, attempt)));
    return ThreadLocalRandom.current().nextLong(0, backoff);
}
// Usage: Thread.sleep(fullJitter(attempt, 100, 30_000));
```

---

### ⚖️ Comparison Table

| Strategy     | Formula                     | Thundering herd      | Mean latency           | Complexity |
| :----------- | :-------------------------- | :------------------- | :--------------------- | :--------- |
| No jitter    | base × 2^n                  | Worst (synchronized) | Lowest (single client) | Low        |
| Equal jitter | cap/2 + rand(0, cap/2)      | Good                 | Medium                 | Medium     |
| Full jitter  | rand(0, min(cap, base×2^n)) | Best                 | Medium                 | Low        |
| Decorrelated | rand(base, prev×3)          | Good                 | Slightly better        | High       |

---

### 🔁 Flow / Lifecycle

**Retry attempt lifecycle:**

1. **Attempt 0:** Call service. If success: return result. If retriable error: record failure.
2. **Backoff calculation:** `delay = fullJitter(0, base, cap)`. Sleep for delay.
3. **Attempt 1:** Call service. If success: return result. If retriable error: increment attempt count.
4. **Backoff calculation:** `delay = fullJitter(1, base, cap)`. Sleep for delay (longer range).
5. **Attempt N (maxAttempts-1):** Final attempt. If success: return. If failure: throw `MaxRetriesExceededException`.
6. **Non-retriable error at any attempt:** throw immediately, no further retry.
7. **Circuit opens during retry:** `CallNotPermittedException` thrown (non-retriable) → fail immediately.

---

### ⚠️ Common Misconceptions

| Misconception                                                   | Reality                                                                                                                                                                                                                                                                                                                     |
| :-------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Retry is always safe"                                          | Retrying non-idempotent operations (POST /payment, POST /order) can cause double-processing. Only retry when: (1) operation is idempotent (GET, PUT, DELETE with unique ID), or (2) idempotency key is used (DST-045). Never blindly retry write operations without idempotency guarantees.                                 |
| "More retries = more reliable"                                  | More retries = more latency before giving up + more load on failing service. For user-visible paths: maxAttempts=3 is usually the limit (beyond 3 retries × growing delays = unacceptable user wait time). More retries are appropriate for background jobs, async processing, or when the operation is cheap and critical. |
| "Exponential backoff without jitter is fine for single clients" | True for single clients. False for any system with multiple clients hitting the same service. Even 2 clients with identical backoff formulas retry at the same time (T, T+100ms, T+300ms). At N clients: N× synchronized load spike. Always add jitter in microservice architectures.                                       |
| "Retrying after circuit opens is useful"                        | When the circuit is OPEN: retrying against it does nothing (immediate rejection). The retry should recognize `CallNotPermittedException` as non-retriable — stop retrying immediately. Retrying against an OPEN circuit wastes latency (sleeping between retries) with no benefit.                                          |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Retry Storm Despite Backoff**

**Symptom:** Service B has a 30-second outage. All clients retry with exponential backoff. Service B metrics show load spikes every 30 seconds (exactly at the max backoff cap). Engineers added backoff correctly but forgot jitter.
**Root Cause:** Exponential backoff without jitter: all clients with the same base/cap/multiplier back off to exactly `cap=30s` by the 5th attempt. All 10,000 clients retry at T=30s simultaneously. Load spike: 10,000 × 3 attempts = 30,000 simultaneous requests at T=30s. Service B re-overwhelmed.
**Diagnostic:**

```bash
# Check if retries are synchronized:
# Service B access log: requests per second
grep "POST /api" service-b-access.log | \
  awk '{print $4}' | cut -d: -f1-4 | \
  sort | uniq -c | sort -k2 | tail -20
# Pattern: quiet for 29s, then spike at X:30 = synchronized

# Check client retry config for jitter:
grep "random\|jitter\|Jitter" src/**/*.java
grep "IntervalFunction\|backoff" src/**/*.java
# If no jitter in config: missing jitter
```

**Fix:**
BAD: `Backoff(delay=100, multiplier=2.0, maxDelay=30000)` — no jitter.
GOOD: `IntervalFunction.ofExponentialRandomBackoff(100, 2.0, 30000)` — full jitter.
**Prevention:** Always verify `random=true` or equivalent jitter in retry config before production deployment. Load test with N concurrent clients to verify no synchronized retry spikes.

**Failure Mode 2: Retry Amplifies Non-Retriable Errors**

**Symptom:** A code bug causes all payment requests to return 400 Bad Request. Instead of failing immediately: each request retries 5 times with backoff. Request latency: 30+ seconds. Payment service logs show 5× the expected request volume. The bug is masked by retries masking the error (it looks like a "slow service" not a "buggy client").
**Root Cause:** Retry policy configured to retry ALL exceptions including `HttpClientErrorException` (4xx). A 400 means the request is invalid — retrying will never succeed (same request, same response). Retrying amplifies load by maxAttempts× and adds unnecessary latency.
**Diagnostic:**

```bash
# Check error rates by HTTP status code:
grep "400\|HttpClientError" service-a-app.log | wc -l
grep "retry.*attempt" service-a-app.log | wc -l
# If retry count ≈ 5× error count: retrying 4xx

# Resilience4j: check retry event types:
curl /actuator/metrics/resilience4j.retry.calls?\
  tag=name:payment&tag=kind:failed_with_retry
# High count + 4xx errors = misconfigured retry
```

**Fix:**
BAD: `retryExceptions(Exception.class)` — retries everything.
GOOD: Explicitly list retriable exceptions: `retryExceptions(IOException.class, HttpServerErrorException.class)` AND `ignoreExceptions(HttpClientErrorException.class)`.
**Prevention:** Treat 4xx as non-retriable by default. Treat 5xx and network exceptions as retriable by default. Review the list of retried exceptions in code review.

**Failure Mode 3: Security - Retry Used for Credential Stuffing**

**Symptom:** Authentication service receives millions of login attempts. Each failed login attempt triggers a retry (403 → retry with same credentials → 403 → retry...). The retry mechanism in the client SDK is abused by a malicious actor to cycle through credential lists at 3× the speed.
**Root Cause:** Retry configured to retry 403 Forbidden (authentication failure). 403 is not a transient error — retrying it just means trying the same invalid credentials multiple times. Attackers exploit this: send invalid credentials → client retries automatically → effective brute-force speed multiplied by maxAttempts.
**Diagnostic:**

```bash
# Check if 403s are being retried:
grep "403.*retry\|retry.*403" app.log | head -20
# Should be zero (403 is not retriable)

# Check rate of authentication attempts:
grep "POST /auth/login" access.log | \
  awk '{print $1}' | sort | uniq -c | sort -rn | head
# Spike = potential attack
```

**Fix:**
BAD: `retryExceptions(Exception.class)` includes 403.
GOOD: `ignoreExceptions(HttpClientErrorException.class)` — explicitly don't retry 4xx including 403.
**Prevention:** Authentication endpoints should never be subject to automatic retry. Add explicit `ignoreExceptions` list. Rate limit auth endpoints at API gateway (5 attempts per IP per minute).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-046 - Timeout (timeout is what triggers retry — understand timeouts before retries)
- DST-045 - Idempotency (retry requires idempotent operations — understand idempotency before enabling retry on writes)

**Builds On This (learn these next):**

- DST-042 - Circuit Breaker (compose with retry — circuit breaker stops retrying when failure rate is too high)

**Alternatives / Comparisons:**

- DST-042 - Circuit Breaker (complementary: retry = transient, circuit breaker = sustained failures)
- DST-043 - Bulkhead (limit concurrent retries via bulkhead to prevent retry storms)
- DST-046 - Timeout (timeout triggers retry; timeout per attempt × maxAttempts = max total wait)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Automatic re-attempt of failed |
|                  | calls with exponential delay   |
|                  | and random jitter              |
+------------------+--------------------------------+
| PROBLEM SOLVED   | Transient failures (network    |
|                  | hiccup, brief overload) look   |
|                  | like permanent failures        |
+------------------+--------------------------------+
| KEY INSIGHT      | Jitter > backoff in importance:|
|                  | backoff spreads attempts over  |
|                  | time; jitter desynchronizes N  |
|                  | clients (prevents storm)       |
+------------------+--------------------------------+
| USE WHEN         | Idempotent operations, network |
|                  | calls to external services,    |
|                  | known transient failure modes  |
+------------------+--------------------------------+
| AVOID WHEN       | Non-idempotent writes without  |
|                  | idempotency key; 4xx errors    |
+------------------+--------------------------------+
| TRADE-OFF        | Resilience to transient fails  |
|                  | vs added latency per retry     |
+------------------+--------------------------------+
| ONE-LINER        | Wait longer each time, add     |
|                  | randomness, stop on 4xx        |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-042 Circuit Breaker,       |
|                  | DST-045 Idempotency            |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. Always add jitter (not just backoff). Jitter desynchronizes N clients — without it, they all retry simultaneously, creating a retry storm worse than the original failure.
2. Only retry retriable errors: network exceptions, 5xx. Never retry 4xx (bad request) — retrying won't fix a bug. Never retry non-idempotent operations without an idempotency key.
3. Compose retry + circuit breaker: retry handles transient failures (within a window). Circuit breaker handles sustained failures (stops retrying when failure rate too high). Together: resilient to transient AND persistent failures.

**Interview one-liner:**
"Retry with backoff automatically re-attempts failed operations after an increasing delay: `sleep = random(0, min(cap, base × 2^attempt))` — exponential backoff plus full jitter. The jitter is critical: without it, all N clients retry at the same time, creating a retry storm that can re-overwhelm a recovering service. Only retry retriable errors (network exceptions, 5xx — not 4xx or non-idempotent operations). Compose with circuit breaker: retry handles brief transient failures, circuit breaker stops retrying when sustained failure rate exceeds threshold."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When multiple agents react to the same failure event simultaneously, randomized timing prevents coordinated action (thundering herd). This principle appears wherever N agents respond to a shared signal: TCP collision detection (Ethernet CSMA/CD), leader election (Raft's randomized election timeout), cache stampede prevention (random cache TTL jitter), and retry logic. The common thread: randomness is a decentralized coordination mechanism. No coordinator needed — each agent independently randomizes, and statistical averaging ensures spread-out behavior across all agents.

**Where else this pattern appears:**

- **Raft election timeout randomization:** In Raft (DST-030), each follower's election timeout is randomized (150-300ms) rather than fixed. If all followers had the same timeout: they'd all start elections simultaneously after a leader failure → split vote → no winner → repeat. Randomization ensures one follower starts election first and wins. Same principle: N agents with synchronized timers = coordination failure. N agents with randomized timers = natural leader emergence.
- **CDN cache staggering (cache stampede prevention):** When a cached item expires: thousands of requests simultaneously miss the cache and all hit the origin server. Solution: add random jitter to cache TTL: `expire_at = now + ttl + random(0, ttl × 0.1)`. Different items expire at different times. Same item: first miss regenerates, others wait (lock). The jitter principle applied to cache expiry prevents the coordinated cache-miss thundering herd.
- **AWS SQS visibility timeout + message processing retry:** When a message fails processing: SQS makes it visible again after visibility_timeout. If all consumers process at the same rate: they all retry the message simultaneously (thundering herd on one message). Solution: dead-letter queue + exponential backoff retry policy per message. Message retried after base × 2^attempt delay. If 10 consumers process the same failed message: jitter ensures they don't all retry at T+30s simultaneously.

---

### 💡 The Surprising Truth

Marc Brooker's 2015 AWS blog post "Exponential Backoff and Jitter" is one of the most impactful distributed systems engineering posts ever written — but its main finding surprised the engineers who wrote it. The naive assumption was: "decorrelated jitter is best because it produces lower mean latency than full jitter." The post shows this is TRUE for average latency per request. But the real-world impact goes the other way: full jitter produces LOWER load on the server during recovery compared to decorrelated jitter, because full jitter spreads retries more uniformly in time. When total load on the recovering server matters more than individual request latency (which is almost always true during an outage): full jitter is the superior choice. The surprising truth: optimizing for INDIVIDUAL client latency (decorrelated jitter) makes the SYSTEM worse during recovery (more load spikes). Optimizing for SYSTEM behavior (full jitter) makes every individual client slightly slower on average — but the system recovers faster. This is the classic individual optimum vs collective optimum trade-off, embedded in a backoff formula.

---

### 🧠 Think About This Before We Continue

**Q1 (B - Scale):** 10,000 clients call Service B simultaneously. Service B handles 5,000 req/s normally. An outage occurs at T=0. Each client retries up to 3 times with full jitter (base=100ms, cap=30s). Service B recovers at T=5s (can now handle 5,000 req/s). Estimate: (a) the retry load on Service B at T=5s (when it recovers), and (b) how long until all clients have successfully completed their operation. How does maxAttempts affect these numbers?
_Hint:_ (a) At T=5s: clients are on attempt 0-3 depending on how long their initial call took + jitter delays. With full jitter: retries are spread across [0, 30s]. Load distribution is roughly uniform (by full jitter property). Load at T=5s: (10,000 clients × 3 attempts total) / 30s window = ~1,000 req/s. Service B capacity: 5,000 req/s. Easily absorbed. Without jitter: all 10,000 clients retry at T=5s simultaneously (after reaching cap=30s... or some other synchronized point) → 10,000 req/s spike. (b) With full jitter: last retry happens at T ≈ 0s (initial) + 30s (max cap between attempt 2 and 3) = T=35s approximately. But most clients succeed earlier as service recovers at T=5s. Estimate: 80%+ succeed by T=10s, all by T=35s. maxAttempts=5: more attempts but also more likely to catch recovery — reduces failure rate but increases T_max.

**Q2 (A - System Interaction):** Service A retries calls to Service B with 3 attempts, full jitter. Service B uses a circuit breaker for Service C. When Service B's circuit for C opens (during a retry from A): describe what happens to A's retry flow. Does A retry? Does B's circuit breaker affect A's circuit breaker (if A has one for B)?
_Hint:_ Sequence: A calls B (attempt 1) → B's circuit for C opens → B returns 503 to A → A's retry fires (503 is retriable) → A retries B (attempt 2) → B still has circuit OPEN for C → B returns 503 again → A retries attempt 3 → B circuit OPEN → 503 → A exhausts maxAttempts. A's own circuit breaker for B (if it has one): records 3 consecutive failures → may open its own circuit for B. Result: A's circuit opens for B, B's circuit opens for C. Cascading circuit breaks. Key insight: a circuit breaker failure at depth N propagates up as failures to depth N-1's circuit breaker. Design mitigation: fallback at each level so circuit open → fallback response → caller gets degraded (not error) response → caller's circuit doesn't see failures.

**Q3 (C - Design Trade-off):** A payment processing service uses retry with backoff on payment charge API calls. A security review flags this as a risk: retrying payment charges could cause double charges. The operations team wants to disable retry for payments entirely. Is disabling retry the right answer? What alternative design preserves both retry resilience AND prevents double charges?
_Hint:_ Disabling retry: eliminates double-charge risk but also eliminates resilience. Transient network failure = permanent payment failure. Users must manually retry (worse UX, higher support load). Alternative: idempotency key (DST-045). Client generates UUID per payment attempt. Sends UUID as `Idempotency-Key: <uuid>` header. Payment service stores (key → result) in DB with UNIQUE constraint. First request: process payment, store result. Retry with same UUID: DB constraint detects duplicate → return stored result → no double charge. This allows unlimited retries (of the same operation) without double processing. Stripe, PayPal, Square all implement this pattern. The answer: don't disable retry — make the operation idempotent, then retry freely.
