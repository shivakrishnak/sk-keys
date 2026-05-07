---
layout: default
title: "Retry Pattern"
parent: "Design Patterns"
nav_order: 55
permalink: /design-patterns/retry-pattern/
number: "DPT-055"
category: Design Patterns
difficulty: ★★☆
depends_on: Circuit Breaker Pattern, Idempotency, Distributed Systems, Timeout, HTTP Status Codes
used_by: Ambassador Pattern, Service Mesh, Resilience4j, API Gateway
related: Circuit Breaker Pattern, Bulkhead Pattern, Timeout, Idempotency, Exponential Backoff
tags:
  - pattern
  - distributed
  - reliability
  - architecture
  - bestpractice
  - production
---

# DPT-055 — Retry Pattern

⚡ TL;DR — The Retry Pattern automatically re-attempts a failed operation after a delay, handling transient failures while avoiding overwhelming already-degraded downstream systems.

| #820 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Circuit Breaker Pattern, Idempotency, Distributed Systems, Timeout, HTTP Status Codes | |
| **Used by:** | Ambassador Pattern, Service Mesh, Resilience4j, API Gateway | |
| **Related:** | Circuit Breaker Pattern, Bulkhead Pattern, Timeout, Idempotency, Exponential Backoff | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A microservice calls a downstream payment API. The payment API is experiencing a brief spike — one of its database connections timed out. The response returns `503 Service Unavailable`. Without a Retry Pattern, the calling service immediately returns an error to the user: "Payment failed." The actual payment infrastructure was healthy again 150ms later. The user makes a support ticket. The support team investigates. The payment was never actually broken.

**THE BREAKING POINT:**
In distributed systems, transient failures are not exceptional — they are normal. Network jitter causes packet loss. GC pauses cause momentarily slow responses. Database connection pools become briefly exhausted. Load balancers shed connections during rolling restarts. A system that treats every transient failure as a permanent error will appear unreliable even when the underlying infrastructure is healthy. The **call failure rate** will always be higher than the **actual infrastructure failure rate**.

**THE INVENTION MOMENT:**
The Retry Pattern was designed to bridge this gap. If a transient failure resolves within seconds, the caller should retry the operation before surfacing an error. The retry is invisible to the end user; the transient failure is absorbed at the infrastructure level. The principle: **tolerate transiency; escalate only persistence**.

---

### 📘 Textbook Definition

The **Retry Pattern** is a resilience pattern in which a failing operation is automatically re-attempted one or more times before propagating the failure to the caller. Each retry may be separated by a delay (fixed, linear, or exponential). The pattern is typically combined with a maximum retry count, a timeout per attempt, and a jitter strategy to prevent retry thundering herd. Retries are only safe when the target operation is **idempotent** — retrying a non-idempotent operation (e.g., charging a credit card twice) can cause correctness problems.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
If a call fails transiently, wait a moment and try again — automatically, without surfacing the error to the user.

**One analogy:**
> When you dial a phone number and get a busy tone, you don't immediately conclude the person no longer exists. You wait a few seconds and try again. After a few attempts, if you still cannot connect, you conclude there is a real problem. The Retry Pattern is that behaviour — automated patience before declaring failure.

**One insight:**
A retry without backoff is as dangerous as no retry at all. Immediate retry under system stress amplifies load, causing the degraded service to degrade further. The delay between retries — and how that delay grows — is as important as the retry itself.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. **Retry only transient errors.** Permanent errors (400 Bad Request, 404 Not Found) must not be retried — they will never succeed.
2. **Retry only idempotent operations.** Retrying a `POST /charge` that has no idempotency key can charge a customer twice.
3. **Limit retry count.** Infinite retries make callers hang indefinitely and prevent fail-fast behaviour.
4. **Add delay between retries.** Immediate re-attempt hits the same overloaded system; delay gives it time to recover.

**DERIVED DESIGN:**
From invariant 1: retry only on `5xx` server errors and network errors (connection reset, timeout). Never retry `4xx` client errors (except `429 Too Many Requests` with `Retry-After` header).

From invariant 4: the delay strategy matters. Fixed delay (always 100ms) does not prevent synchronised retry bursts. Exponential backoff (100ms, 200ms, 400ms…) grows the delay on repeated failure. Jitter (randomise delay within ±25% of calculated backoff) desynchronises retries from concurrent callers.

From invariant 2: systems must propagate **idempotency keys** with retried requests so the downstream can deduplicate.

**THE TRADE-OFFS:**
**Gain:** Transient failures absorbed transparently; improved user-perceived reliability; reduced false-positive error rates.
**Cost:** Increased latency on retry paths (total wait = sum of all delays); risk of amplifying load on degraded systems if backoff is too aggressive; risk of data corruption if idempotency is not guaranteed; masking persistent failures if retry count is too high.

---

### 🧪 Thought Experiment

**SETUP:**
A checkout service calls an inventory service to reserve stock. The inventory service's database connection pool is temporarily exhausted under high Black Friday load, causing 503 responses for 300ms.

**WHAT HAPPENS WITHOUT Retry:**
Every checkout attempt during those 300ms fails. "Sorry, checkout unavailable" messages appear to users. 5,000 users who could have successfully checked out 300ms later abandon their carts. Revenue loss: significant.

**WHAT HAPPENS WITH Retry (exponential backoff + jitter):**
Checkout service retries after 50ms, then 100ms, then 200ms. The 300ms outage window is covered by the backoff sequence. Users see ~300ms additional latency on the checkout button. No error messages. The inventory service pool recovers; retried calls succeed. Revenue loss: zero.

**THE INSIGHT:**
The Retry Pattern converts a 300ms infrastructure blip into a 300ms latency addition — invisible to users. Without it, the same 300ms blip appears as an "outage" to every user who hit the window.

---

### 🧠 Mental Model / Analogy

> Imagine a tollbooth with an electronic payment reader. If the reader fails to scan your card on the first pass (brief signal interference), the system retries automatically two more times with a 1-second pause. If it fails three times, it escalates to a human operator. You don't need to leave your car, find an ATM, and return. The retry absorbed a transient signal failure invisibly.

- "Electronic reader" → the calling service's HTTP client
- "First pass failing" → first request returning 503
- "1-second pause + retry" → exponential backoff between attempts
- "Third failure → human operator" → retry exhaustion → Circuit Breaker opens / fallback activates
- "Brief signal interference" → transient failure (network jitter, GC pause, connection pool exhaustion)

Where this analogy breaks down: a tollbooth reader reads a card (idempotent — reading the same card twice has no side effect). Retry is only safe for idempotent operations. "Charging the toll" (the payment) must have an idempotency guarantee to avoid double-charging.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When your service tries to call another service and gets a temporary error, the Retry Pattern makes your service automatically try again after a short wait. If the call eventually succeeds, the temporary error was invisible. Only if all retries fail does the error reach the user.

**Level 2 — How to use it (junior developer):**
Use a library like Resilience4j (Java), `tenacity` (Python), or `retry` (Go). Configure: maximum attempts (e.g., 3), wait duration (e.g., 50ms, 100ms, 200ms), retry-on predicates (retry on 503 and IOException; do not retry on 400 or 404). Always include an idempotency key in the request so the downstream can detect and deduplicate retried calls.

**Level 3 — How it works (mid-level engineer):**
A retry decorator wraps the operation. On each attempt: execute the call; if response matches a retryable predicate (status in [500, 502, 503, 504] or network exception), check if `max_attempts` is reached; if not, calculate next delay using the backoff formula (`base_delay * (2 ^ attempt_num) + jitter(0..base_delay*0.25)`); sleep; re-execute. If all attempts fail, throw `MaxRetriesExceededException`. The idempotency key is generated once before the first attempt and included in every retry, allowing the downstream to detect duplicate requests via a distributed key-value store (Redis, database `unique` constraint).

**Level 4 — Why it was designed this way (senior/staff):**
The Retry Pattern is a probabilistic solution to the Two Generals Problem — you cannot guarantee delivery in a distributed system, but you can increase the probability of success in the presence of transient faults. The backoff + jitter strategy solves the **retry thundering herd**: if 1,000 callers all receive a 503 simultaneously and all retry with the same fixed delay, they produce a synchronised retry burst — a second spike on the already-struggling service. Exponential backoff distributes retries over time; jitter desynchronises them mathematically (uniformly random offset). The combination reduces the probability of synchronised retry collisions from near-100% (fixed delay, no jitter) to near-0% (full jitter). The Circuit Breaker Pattern is the Retry Pattern's essential partner: retries handle transiency; circuit breakers handle persistence. Retrying into an open circuit wastes both caller and callee resources.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│  RETRY PATTERN — ATTEMPT FLOW                          │
│                                                        │
│  Attempt 1                                             │
│  ─────────►  Downstream  ─ 503 ──────────► Fail 1     │
│              Wait: 50ms + jitter                       │
│                                                        │
│  Attempt 2                                             │
│  ─────────►  Downstream  ─ 503 ──────────► Fail 2     │
│              Wait: 100ms + jitter                      │
│                                                        │
│  Attempt 3                                             │
│  ─────────►  Downstream  ─ 200 ──────────► SUCCESS    │
│             (service recovered)                        │
│                                                        │
│  EXPONENTIAL BACKOFF + FULL JITTER FORMULA:            │
│  delay = random(0, min(cap, base * 2^attempt))         │
│  cap   = 10,000ms  base = 50ms                         │
│  Attempt 1: random(0, 50ms)                            │
│  Attempt 2: random(0, 100ms)                           │
│  Attempt 3: random(0, 200ms)                           │
└────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Client: POST /checkout (idempotency-key: abc-123)
  → Checkout service
  → Inventory service call: attempt 1
    [← YOU ARE HERE: retry logic evaluates response]
  → 503 response — retryable; wait 50ms
  → Inventory service call: attempt 2
  → 200 OK — SUCCESS
  → Inventory service deduplicates via idempotency-key
  → Checkout service: continue with successful reservation
  → Client: 200 OK (user saw ~50ms extra latency)
```

**FAILURE PATH:**
```
All 3 attempts return 503 (persistent degradation)
  → MaxRetriesExceededException raised
  → Retry count increments circuit breaker failure counter
  → If breaker threshold reached: circuit OPENS
  → Future calls fail-fast (no more retry attempts)
  → Fallback activates: queue order for async processing
  → Client: 202 Accepted with retry-later message
```

**WHAT CHANGES AT SCALE:**
At 100 requests/second with 3 retries and no backoff: a 100ms outage triggers 300 additional calls. With exponential backoff and jitter: the same outage distributes the 300 additional calls over 300ms, keeping per-second arrival rate steady. At high scale (10,000 RPS), retry amplification without backoff can collapse an already-degraded service; pure retry budgets (max 10% of total requests can be retries) enforce fleet-wide retry discipline.

---

### 💻 Code Example

**Example 1 — Java with Resilience4j:**

```java
// BAD: retry immediately, no backoff, retry all errors
public PaymentResult chargeWithRetry(ChargeRequest req) {
    for (int i = 0; i < 5; i++) {
        try {
            return paymentClient.charge(req);
        } catch (Exception e) {
            // retrying 4xx errors too — dangerous
            // no delay — amplifies load on degraded service
        }
    }
    throw new PaymentException("5 retries failed");
}

// GOOD: Resilience4j RetryConfig with backoff + predicates
RetryConfig config = RetryConfig.custom()
    .maxAttempts(3)
    .waitDuration(Duration.ofMillis(50))
    .intervalFunction(
        IntervalFunction.ofExponentialRandomBackoff(
            50,    // base (ms)
            2.0,   // multiplier
            0.25,  // randomisation factor
            2000   // max interval (ms)
        )
    )
    // Retry only on 5xx server errors
    .retryOnResult(response ->
        response.getStatus() >= 500)
    // Retry on network errors
    .retryExceptions(IOException.class,
                     ConnectTimeoutException.class)
    // Do NOT retry on client errors
    .ignoreExceptions(BadRequestException.class)
    .build();

Retry retry = Retry.of("payment", config);

// Always set idempotency key BEFORE retry wrapping
String idempotencyKey = UUID.randomUUID().toString();
CheckedFunction0<PaymentResult> decorated =
    Retry.decorateCheckedSupplier(retry, () ->
        paymentClient.charge(req
            .withHeader("Idempotency-Key", idempotencyKey))
    );
```

**Example 2 — Kubernetes Envoy retry policy:**

```yaml
# Envoy VirtualService retry config (Istio)
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: payment-api
spec:
  hosts:
  - payment-api
  http:
  - route:
    - destination:
        host: payment-api
        port:
          number: 443
    retries:
      attempts: 3          # max 3 attempts  
      perTryTimeout: 2s    # 2s per attempt
      # Retry only on 5xx and reset (not 4xx)
      retryOn: "5xx,reset,connect-failure"
    timeout: 10s           # total operation timeout
```

**Example 3 — Python with tenacity:**

```python
from tenacity import (
    retry, stop_after_attempt,
    wait_exponential, retry_if_exception_type,
    retry_if_result
)
import requests

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(
        multiplier=0.05,  # 50ms base
        min=0.05, max=2.0
    ),
    retry=(
        retry_if_exception_type(
            requests.exceptions.ConnectionError
        ) |
        retry_if_result(
            lambda r: r.status_code >= 500
        )
    ),
    reraise=True,
)
def charge_payment(idempotency_key: str, amount: int):
    # Idempotency key generated once by caller
    return requests.post(
        "http://localhost:9900/charge",
        json={"amount": amount},
        headers={"Idempotency-Key": idempotency_key},
        timeout=2.0,
    )
```

---

### ⚖️ Comparison Table

| Retry Strategy | Burst Risk | Recovery Speed | Implementation Complexity | Best For |
|---|---|---|---|---|
| **No retry** | None | None — every transient = error | None | Idempotency-unsafe operations only |
| Fixed delay | High (synchronised burst) | Slow | Low | Simple low-traffic scenarios |
| Exponential backoff | Medium | Moderate | Medium | Standard API clients |
| Exponential + jitter | Low | Moderate | Medium | High-concurrency distributed systems |
| Retry with circuit breaker | Very low | Fast (fail-fast after threshold) | Higher | Production distributed systems |
| Retry budget (fleet-wide cap) | None | N/A — rate-limited | High | High-scale service meshes |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Retry is always safe | Retrying a non-idempotent operation (credit card charge, file creation) without an idempotency key can cause data duplication. Safety requires idempotent targets or idempotency keys |
| More retries = more reliability | Beyond 2–3 retries, additional retries add latency without meaningfully improving success rates for genuinely degraded services. They also amplify load, potentially deepening the outage |
| Retry replaces the Circuit Breaker | Retry handles transiency (brief failures). Circuit Breaker handles persistence (sustained failures). Used alone, retry can hammer a persistently failed service; the Circuit Breaker prevents this by failing fast after a threshold |
| Retry should be implemented at the application layer only | Retries can be implemented at multiple layers: application code, HTTP client library, service mesh proxy, cloud load balancer. Avoid implementing retries at multiple layers simultaneously — double retries multiply amplification: 3 retries × 3 retries = up to 9 actual calls |

---

### 🚨 Failure Modes & Diagnosis

**1. Retry Amplification — Cascading Failure**

**Symptom:** A downstream service reports sudden 10× traffic spike during an incident. The service was already degraded; the spike worsens the degradation. Multiple services are now impacted.

**Root Cause:** Multiple callers are retrying with no or minimal backoff. N callers × 3 retries = 3N requests hitting an already degraded service within a short window.

**Diagnostic:**
```bash
# Check retry-to-total request ratio per service:
kubectl exec my-pod -c ambassador -- \
  curl -s localhost:9901/stats \
  | grep "upstream_rq_retry\|upstream_rq_total"

# Or check Circuit Breaker metrics in Prometheus:
curl -s http://prometheus:9090/api/v1/query \
  ?query=resilience4j_retry_calls_total
# If retried >> total → amplification risk
```

**Fix:** Reduce `maxAttempts` to 2–3. Add exponential backoff with full jitter. Add Circuit Breaker to fail-fast when failure rate exceeds threshold. Implement retry budget at the service mesh level.

**Prevention:** Load test retry behaviour under degraded upstream conditions using Chaos Mesh `HTTPChaos` to inject 503 responses and observe retry amplification before production.

---

**2. Retrying Non-Idempotent Operations — Duplicate Data**

**Symptom:** Duplicate orders, double-charged payments, duplicate emails sent. Often reported by users as "I clicked once but was charged twice."

**Root Cause:** Retry was applied to a `POST` endpoint that creates resources, without idempotency key. The first request succeeded but the response was lost (network timeout before response delivery). The retry created a second resource.

**Diagnostic:**
```bash
# Find duplicate orders by correlation ID in DB:
psql -c "SELECT idempotency_key, COUNT(*)
         FROM orders
         GROUP BY idempotency_key
         HAVING COUNT(*) > 1
         LIMIT 20;"
# Any rows = duplicate creation occurred
```

**Fix (BAD):** Remove retry entirely.
**Fix (GOOD):** Add `Idempotency-Key` header to all mutating calls. Implement server-side deduplication: check if key exists in Redis with TTL=24h before processing; return cached response if found.

**Prevention:** Enforce idempotency key requirement for all `POST/PUT/PATCH` endpoints via API contract linting. Reject mutation requests that lack `Idempotency-Key` header with `400 Bad Request`.

---

**3. Hidden Persistent Failures — Masked by Retry**

**Symptom:** A downstream service is permanently down for 2 hours. Callers are not alerting. Users see high latency (multiple retry delays) instead of fast failures. The on-call engineer is not paged until manual investigation.

**Root Cause:** Retry count too high (e.g., 10 retries) and Circuit Breaker not configured. Every call takes up to 10× the timeout before failing. Retries mask the persistent failure from monitoring alert thresholds.

**Diagnostic:**
```bash
# Check P99 latency spike correlating with failure:
curl -s "http://prometheus:9090/api/v1/query?query=\
histogram_quantile(0.99,\
rate(http_request_duration_seconds_bucket[5m]))"
# P99 spike = retry exhaustion path being hit frequently
```

**Fix:** Reduce maxAttempts to 3. Add Circuit Breaker that opens after 50% error rate over 10 requests, providing fail-fast behaviour and triggering alerts faster.

**Prevention:** Instrument both `retry_attempts` and `circuit_breaker_state` metrics. Alert when circuit state transitions to OPEN.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Idempotency` — understanding idempotency is required before applying the Retry Pattern; retrying without idempotency guarantees causes duplicate operations
- `HTTP Status Codes` — understanding which status codes indicate transient failures (503, 429, 502) vs. permanent failures (400, 401, 404) is required to configure correct retry predicates

**Builds On This (learn these next):**
- `Circuit Breaker Pattern` — the essential partner to Retry; the Circuit Breaker prevents unlimited retries into a persistently failed service by failing fast after a threshold
- `Exponential Backoff` — the delay strategy used between retries; understanding how base delay, multiplier, cap, and jitter interact is required to implement retry safely at scale

**Alternatives / Comparisons:**
- `Circuit Breaker Pattern` — alternative strategy for the same problem class (resilience to downstream failures); where Retry handles transiency, Circuit Breaker handles persistence; production systems use both together
- `Fallback Strategy` — instead of retrying the failed operation, execute an alternative (cached result, default value, queue for async processing); Fallback is appropriate when retry latency is unacceptable

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Auto-reattempt a failed operation with    │
│              │ delay before surfacing error to caller    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Transient failures (network jitter, GC   │
│ SOLVES       │ pause, brief pool exhaustion) surfaced    │
│              │ as errors to end users                    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Retry only transient + idempotent ops;    │
│              │ always use exponential backoff + jitter   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Target operation is idempotent; failures  │
│              │ are expected to be transient (5xx, reset) │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Target is non-idempotent without          │
│              │ idempotency keys; error is permanent 4xx  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Transient failures absorbed invisibly vs. │
│              │ added latency on retry paths; amplified   │
│              │ load risk without backoff + circuit break │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Patience for transiency; circuit breaker │
│              │  for persistence."                        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Circuit Breaker → Exponential Backoff →   │
│              │ Idempotency → Bulkhead → Ambassador       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A payment service receives retried requests with an `Idempotency-Key` header. The service stores the idempotency key in Redis with a 24-hour TTL before processing the payment. If the first attempt committed the payment to the database successfully but the Redis write then failed, what happens on retry? Design a solution that guarantees correct deduplication even when the idempotency store itself is unreliable.

**Q2.** Your service mesh (Istio) is configured with `retries.attempts: 3`. Your application code (Resilience4j) is also configured with `maxAttempts: 3`. When a downstream service returns a 503, how many actual HTTP requests can the downstream receive from a single user request? What is the impact at scale (10,000 RPS)? How would you redesign the resilience layering to avoid retry amplification while preserving resilience?

**Q3.** The Retry Pattern, Circuit Breaker Pattern, and Timeout pattern are all resilience patterns for handling downstream failures. Compare all three on these dimensions: what failure type each handles (transient / persistent / slow), the effect on caller latency (increases / decreases / caps), and the operational risk if misconfigured. Explain the complementary relationship between all three and why production systems should implement them together rather than choosing one.

