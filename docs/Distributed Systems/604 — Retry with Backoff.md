---
layout: default
title: "Retry with Backoff"
parent: "Distributed Systems"
nav_order: 604
permalink: /distributed-systems/retry-with-backoff/
number: "604"
category: Distributed Systems
difficulty: ★★☆
depends_on: "Circuit Breaker, Idempotency"
used_by: "Resilience4j, Spring Retry, AWS SDK, gRPC, HTTP clients"
tags: #intermediate, #distributed, #resilience, #fault-tolerance, #idempotency
---

# 604 — Retry with Backoff

`#intermediate` `#distributed` `#resilience` `#fault-tolerance` `#idempotency`

⚡ TL;DR — **Retry with Backoff** re-attempts failed transient calls after increasing wait intervals (exponential backoff + jitter), avoiding the retry storm that fixed-interval retries cause on recovering services.

| #604            | Category: Distributed Systems                           | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------ | :-------------- |
| **Depends on:** | Circuit Breaker, Idempotency                            |                 |
| **Used by:**    | Resilience4j, Spring Retry, AWS SDK, gRPC, HTTP clients |                 |

---

### 📘 Textbook Definition

**Retry with Backoff** is a fault-tolerance pattern where failed operations are retried after a wait period, with the wait period growing (typically exponentially) between attempts to reduce load on a recovering service. Simple retry (immediate or fixed-interval) on a service under load amplifies the problem: 100 clients each retry 3 times immediately → 400 simultaneous requests on a recovering service that could handle 100. **Exponential backoff**: wait = base × 2^attempt. Attempt 1: 1s. Attempt 2: 2s. Attempt 3: 4s. Attempt 4: 8s. **Jitter**: adds random noise to prevent thundering herd (all clients synchronized on same backoff → all retry simultaneously). Full jitter: wait = random(0, base × 2^attempt). Equal jitter: wait = base × 2^attempt / 2 + random(0, base × 2^attempt / 2). AWS recommends "full jitter" for highest de-synchronization. **Retry budget**: maximum total wait time or maximum retry count. Beyond budget: fail permanently. **Idempotency requirement**: retrying a non-idempotent operation (e.g., charge payment) causes double-execution. Retries should only be applied to idempotent operations OR operations protected by idempotency keys.

---

### 🟢 Simple Definition (Easy)

Your app calls a service. Fails (network hiccup). Don't give up immediately — wait a little, try again. Wait longer, try again. Wait even longer. If still failing after N tries: give up. Without increasing wait: 100 clients all retry every second → 100× traffic on recovering service → re-overloads it. With exponential backoff: first retry after 1s, then 2s, then 4s. Service has time to breathe. Add jitter: not everyone retries at exactly the same second. Spread the load.

---

### 🔵 Simple Definition (Elaborated)

Retry without backoff: dangerous. Thundering herd: transient overload takes service down. 100 clients: each request fails → each immediately retries → 200 requests → service still overloaded → all retry again → 200 more → spiral. Exponential backoff breaks the spiral: first retry after 1s, second after 2s, third after 4s. Each doubling gives the service more recovery time. Jitter: add random 0-50% to each wait. Now 100 clients don't all retry at T=1.0s exactly — they retry at T=0.5s, T=0.8s, T=1.3s... spread across the window. Recovering service sees smooth load instead of synchronized bursts.

---

### 🔩 First Principles Explanation

**Backoff algorithms, jitter strategies, and retry budgets:**

```
RETRY ALGORITHMS:

  1. FIXED RETRY (no backoff):
     wait = constant (e.g., 1s between retries).
     Simple. Works for very brief, rare failures (100ms network glitch).
     DANGER: under systemic failure → retries synchronize → thundering herd.

  2. LINEAR BACKOFF:
     wait = base × attempt.
     Attempt 1: 1s. Attempt 2: 2s. Attempt 3: 3s.
     Better than fixed. Still somewhat synchronized if many clients start simultaneously.

  3. EXPONENTIAL BACKOFF:
     wait = base × 2^attempt.
     Attempt 1: 1s. Attempt 2: 2s. Attempt 3: 4s. Attempt 4: 8s.
     Quickly reduces retry rate. Standard in cloud SDKs (AWS, GCP, Azure).

  4. EXPONENTIAL BACKOFF WITH FULL JITTER (AWS recommendation):
     wait = random(0, min(cap, base × 2^attempt)).
     cap: max wait (e.g., 30s).
     random(0, X): uniform random in [0, X].

     Attempt 1: random(0, 1s). Could be 0.3s.
     Attempt 2: random(0, 2s). Could be 1.7s.
     Attempt 3: random(0, 4s). Could be 0.4s.
     Attempt 4: random(0, 8s). Could be 5.1s.

     KEY PROPERTY: when N clients all start retrying simultaneously (e.g., after server restart),
                   their retry times spread uniformly across [0, cap] instead of clustering.
                   Server sees smooth load increase.

  5. EXPONENTIAL BACKOFF WITH EQUAL JITTER:
     wait = base × 2^attempt / 2 + random(0, base × 2^attempt / 2).
     Minimum guaranteed wait = half the exponential backoff.
     Prevents client from retrying too aggressively (wait can be near 0 with full jitter).

THUNDERING HERD (no jitter):

  500 clients. All receive 503 at T=0.
  All apply backoff: wait 1s, retry at T=1. → 500 simultaneous requests at T=1.
  Server: still recovering. → 500 more 503s.
  All retry: wait 2s → 500 simultaneous at T=3. Same problem.
  Synchronized retries amplify load at every backoff interval.

  With full jitter: at T=1, retries spread from T=0 to T=1 uniformly.
  ~500 / 1s = 500 RPS vs 500 simultaneous. Same total, but smoothed.
  At T=3 (second retry): spread from T=1 to T=3 → 250 RPS. Service handles it.

RETRY BUDGET AND MAX ATTEMPTS:

  Without budget: infinite retries on permanent failure (memory/thread leak, log spam).

  Budget types:
    maxAttempts: 3 (total 4 attempts including original).
    maxDuration: 30s total time across all retries.

  After budget exhausted: permanent failure → propagate exception to caller.

  Combined: maxAttempts=3, maxDuration=30s.
    Whichever limit hits first: stop retrying.
    Prevents: long backoff sequences (e.g., 1s+2s+4s+8s=15s) exceeding SLA.

WHAT TO RETRY:

  RETRY:
    Transient network errors (connection timeout, connection reset).
    503 Service Unavailable (server overloaded — retry after backoff).
    429 Too Many Requests (rate limited — wait and retry; use Retry-After header if provided).
    408 Request Timeout.
    500 Internal Server Error (if idempotent).

  DO NOT RETRY:
    400 Bad Request (client error — retrying won't fix invalid input).
    401 Unauthorized, 403 Forbidden (auth error — retrying won't grant permission).
    404 Not Found (resource doesn't exist — retrying won't create it).
    409 Conflict (business logic conflict — retrying likely conflicts again).
    Non-idempotent operations (POST /payments without idempotency key).

  GREY AREA (retry only if idempotent):
    500 Internal Server Error (server may have partially processed request).
    Requires idempotency key to safely retry POST/PUT.

IDEMPOTENCY + RETRY:

  Problem: POST /payments retried → payment charged twice.

  Solution: idempotency key (unique request ID per logical operation).
    Client: generate UUID: idempotency_key = UUID.randomUUID().
    Attach to request: X-Idempotency-Key: <uuid>.
    Server: if already processed this key → return cached response (don't re-process).

  Retry with idempotency key:
    Attempt 1: POST /payments, X-Idempotency-Key: abc-123. → Timeout.
    Attempt 2 (retry): POST /payments, X-Idempotency-Key: abc-123.
    Server: "I already processed abc-123 (even though client didn't receive response).
            Returning cached result." → No double charge.

  SAME idempotency key across ALL retries of the same logical operation.
  NEW idempotency key only for intentionally new operations.

RETRY IN DISTRIBUTED SYSTEMS:

  HTTP retry: straightforward. Status code → decide retry/no-retry.

  Message queue retry (Kafka, SQS):
    Consumer fails to process message → don't commit offset (Kafka) → message re-delivered.
    Exponential backoff before re-consuming: use dead letter queue (DLQ) after N attempts.

  Database retry (transient deadlock):
    SQL state "40001" (serialization failure) → retry transaction.
    Backoff prevents tight retry loop on hot rows.

  gRPC retry policy (service config):
  {
    "methodConfig": [{
      "name": [{"service": "payment.PaymentService"}],
      "retryPolicy": {
        "maxAttempts": 4,
        "initialBackoff": "1s",
        "maxBackoff": "30s",
        "backoffMultiplier": 2,
        "retryableStatusCodes": ["UNAVAILABLE", "DEADLINE_EXCEEDED"]
      }
    }]
  }
  gRPC: built-in retry with backoff at the framework level. No application code needed.

RETRY AMPLIFICATION (RETRY STORMS AT SCALE):

  100-service microservice graph. Each service: 3 retries.
  One downstream service fails → leaf service: 3 retries.
  Each intermediate service also retries: 3^depth retries at each hop.
  At depth 3: 3^3 = 27 retries per original request.
  100 RPS × 27 = 2,700 requests to failing service.

  FIX 1: Circuit breaker at each service: after threshold → no more retries.
  FIX 2: Retry only at one layer (e.g., only at ingress, not at every service).
  FIX 3: Pass "retry-attempt" header: if already a retry → don't retry again.
    X-Retry-Attempt: 2 → this service: don't retry further.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT retry with backoff:

- Transient failures (brief network hiccup, GC pause): immediate failure propagated to user
- No backoff: retries synchronize → thundering herd amplifies the failure
- No budget: infinite retries on permanent failure → resource leak

WITH retry with backoff:
→ Transient resilience: brief blips recovered without user-visible impact
→ Load smoothing: jitter prevents synchronized retry waves re-overloading recovering services
→ Bounded recovery: budget ensures predictable failure time on permanent failures

---

### 🧠 Mental Model / Analogy

> Calling a busy restaurant for a reservation. First call: "We're full right now." Wait 1 minute. Try again. "Still full." Wait 2 minutes. "Still full." Wait 4 minutes. Eventually: "We have a table!" Without waiting: you call every second — the receptionist spends all time answering your calls. With increasing waits: you give them breathing room to serve actual customers. And you add random seconds to your wait so you and a hundred other callers don't all redial at the same moment.

"Waiting between calls" = backoff interval
"Doubling the wait each time" = exponential backoff
"Adding random seconds" = jitter (prevents synchronized retry storms)

---

### ⚙️ How It Works (Mechanism)

```
Exponential backoff with full jitter:

  attempt = 0
  while attempt < maxAttempts:
      try: execute operation → SUCCESS
      except RetriableException:
          backoffTime = min(cap, base * 2^attempt)
          sleepTime = random(0, backoffTime)          # Full jitter
          sleep(sleepTime)
          attempt++
  fail permanently (raise exception to caller)
```

---

### 🔄 How It Connects (Mini-Map)

```
Failure Modes (transient vs. permanent failures — only retry transient)
        │
        ▼
Retry with Backoff ◄──── (you are here)
(re-attempt transient failures with exponential backoff + jitter)
        │
        ├── Idempotency: prerequisite for safe retries of write operations
        ├── Circuit Breaker: stops retries when failure is systemic (not transient)
        └── Timeout: defines when a "slow call" is considered a failure worth retrying
```

---

### 💻 Code Example

**Resilience4j Retry with exponential backoff:**

```java
// application.yaml:
resilience4j:
  retry:
    instances:
      payment-service:
        maxAttempts: 4                    # 1 original + 3 retries
        waitDuration: 1s                  # Initial wait
        enableExponentialBackoff: true
        exponentialBackoffMultiplier: 2.0 # Wait doubles each retry: 1s, 2s, 4s
        exponentialMaxWaitDuration: 30s   # Cap backoff at 30s
        randomizedWaitFactor: 0.5         # ±50% jitter on wait time
        retryExceptions:
          - java.net.ConnectException
          - java.net.SocketTimeoutException
          - feign.RetryableException
        ignoreExceptions:
          - com.example.PaymentValidationException  # Don't retry 400 errors
          - com.example.InsufficientFundsException

// Service:
@Service
public class PaymentService {

    @Retry(name = "payment-service", fallbackMethod = "paymentRetryExhausted")
    @CircuitBreaker(name = "payment-service")
    public PaymentResult processPayment(PaymentRequest request) {
        // Idempotency key: same key on retries → server won't double-charge.
        return paymentClient.charge(
            request,
            request.getIdempotencyKey()  // Client-generated UUID, stable across retries.
        );
    }

    public PaymentResult paymentRetryExhausted(PaymentRequest request, Exception e) {
        log.error("Payment failed after all retries for request {}: {}",
                  request.getId(), e.getMessage());
        // All retries exhausted + CB open: queue for async processing.
        return paymentQueue.enqueue(request);
    }
}

// Generate and store idempotency key (client side):
public class PaymentRequest {
    private final String idempotencyKey;

    public PaymentRequest(Order order) {
        // Deterministic from order ID: same request always has same idempotency key.
        this.idempotencyKey = "payment-" + order.getId();
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Retry always improves reliability                            | Retrying non-idempotent operations causes double-execution. Retrying on permanent failures (400, 404) wastes resources and adds latency. Retrying without backoff causes thundering herds that worsen cascades. Retry improves reliability ONLY for: transient failures + idempotent operations + with backoff + within a circuit breaker. All four conditions together                                                                                              |
| Exponential backoff is sufficient without jitter             | Exponential backoff without jitter synchronizes clients. Imagine 1,000 clients all failing simultaneously (server restart). They all wait 1s, retry simultaneously. Wait 2s, retry simultaneously. The synchronized spikes can repeatedly overload the recovering server. Jitter (full or equal) distributes retry times across the interval, smoothing the load on recovery. AWS documented this finding in their "Exponential Backoff and Jitter" blog post (2015) |
| Retry should be implemented at every service in a call chain | Retry at every layer of a deep call chain causes exponential retry amplification. A 5-layer chain with 3 retries per layer: 3^5 = 243 requests per user request on failure. Instead: retry at the outermost layer (client or API gateway), or use circuit breakers at inner layers to prevent retry loops. gRPC transparent retries are an exception: framework-level retries before connection is established don't count as application-level retries              |
| The Retry-After header should always be respected            | Retry-After is a strong signal: if a 429 response includes Retry-After: 30, you SHOULD wait 30s before retrying (not your own backoff timer). AWS API returns Retry-After headers for rate limiting. Ignoring it and using your own shorter backoff will cause continued 429s. Built-in: Resilience4j doesn't automatically respect Retry-After by default — requires custom RetryOnResultPredicate                                                                  |

---

### 🔥 Pitfalls in Production

**Retry amplification in microservice chains:**

```
SCENARIO: 4-service chain: API Gateway → Order → Payment → Bank.
  Bank goes down (10 minutes).

  WITHOUT circuit breakers (just retries):
    Bank: returns connection timeout after 5s.
    Payment: 3 retries × 5s timeout = 15s per call to Bank.
    Order: 3 retries × 15s = 45s per call to Payment.
    API Gateway: 3 retries × 45s = 135s per request. API timeout at 60s → 504.

    Total calls to Bank per user request: 1×3×3×3 = 27.
    At 100 user RPS: 2,700 requests hitting dying Bank. Re-overloads recovery.

BAD: Retry at every layer, no circuit breaker:
  // Every service:
  @Retry(name = "downstream", maxAttempts = 3) // 3 retries everywhere.
  public Response callDownstream(Request req) { ... }

FIX: Circuit breaker stops retries when failure is systemic:
  // Payment service: CB wrapping Bank calls.
  // After 10 Bank timeouts: CB OPEN → no retries → fast fail to Order.
  // Order: sees fast fail (not timeout) → CB on Payment also opens after N fast fails.
  // API Gateway: sees fast fail → returns 503 to user immediately (not 135s later).

  @Retry(name = "bank", maxAttempts = 3,
         retryExceptions = { ConnectTimeoutException.class })
  @CircuitBreaker(name = "bank", fallbackMethod = "bankFallback")
  public BankResult callBank(PaymentRequest request) { ... }

FIX 2: Retry only at one layer:
  // API Gateway: retries (3×, with backoff + jitter).
  // Inner services: NO retry (or retry 0 times). Just circuit breakers.
  // API Gateway: short timeout (5s). Downstream: even shorter (2s per hop).
  // Retries at gateway: 3 × 5s = max 15s user-visible latency. Bounded.

FIX 3: Pass retry context header:
  // First attempt: X-Attempt: 1. Downstream: may retry.
  // Retry: X-Attempt: 2. Downstream: NO retry (pass-through only).
  if (Integer.parseInt(request.getHeader("X-Attempt")) > 1) {
      // This is already a retry. Don't retry again downstream.
      return callDirectly(request); // No Retry annotation.
  }
```

---

### 🔗 Related Keywords

- `Idempotency` — prerequisite for safe retrying of write operations (prevents double-execution)
- `Circuit Breaker` — stops retrying when failure rate indicates systemic (not transient) failure
- `Timeout` — defines when a slow call is considered failed (triggers retry)
- `Bulkhead` — limits concurrent retry attempts consuming thread pools

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Re-attempt failed transient calls.       │
│              │ Backoff: give service recovery time.     │
│              │ Jitter: prevent synchronized retry storm.│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Idempotent operations with transient     │
│              │ failure modes (network blips, brief      │
│              │ overload); inside circuit breaker        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Non-idempotent operations without        │
│              │ idempotency keys; permanent errors (4xx);│
│              │ every layer of deep call chains          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Redial the busy restaurant — but wait   │
│              │  longer each time, and randomize when."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Idempotency → Circuit Breaker → Timeout │
│              │ → Bulkhead → Resilience4j                │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A payment service uses POST /payments with an idempotency key (X-Idempotency-Key header). The client sends a request, receives a 500 error (server-side exception), and retries with the same idempotency key. The server has already processed the payment (it charged the card) but failed to return the response. What happens on retry? What must the server implement to handle this correctly? What is the exact sequence of operations the server must perform to guarantee idempotent payments?

**Q2.** AWS SDK uses "full jitter" exponential backoff. A sudden DynamoDB capacity spike causes 1,000 clients to all fail at T=0 with ProvisionedThroughputExceededException. Model the retry timing with: base=25ms, cap=1600ms, maxAttempts=10. What is the expected distribution of retry attempts at T=25ms? How does jitter distribute the load across the first 1600ms? Compare this to no-jitter exponential backoff where all 1,000 clients retry at T=25ms simultaneously.
