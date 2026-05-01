---
layout: default
title: "Idempotency Key"
parent: "System Design"
nav_order: 713
permalink: /system-design/idempotency-key/
number: "713"
category: System Design
difficulty: ★★★
depends_on: "Polling vs Webhooks, Distributed Locks, HTTP and APIs"
used_by: "Polling vs Webhooks, Rate Limiter Design, Distributed Locking"
tags: #advanced, #distributed, #reliability, #api, #consistency
---

# 713 — Idempotency Key

`#advanced` `#distributed` `#reliability` `#api` `#consistency`

⚡ TL;DR — **Idempotency Key** is a unique identifier sent with a request that allows the server to detect and safely ignore duplicate requests, ensuring that retried operations produce the same result as the first successful execution.

| #713            | Category: System Design                                       | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------ | :-------------- |
| **Depends on:** | Polling vs Webhooks, Distributed Locks, HTTP and APIs         |                 |
| **Used by:**    | Polling vs Webhooks, Rate Limiter Design, Distributed Locking |                 |

---

### 📘 Textbook Definition

An **Idempotency Key** is a client-generated unique identifier included in an HTTP request (typically as a header: `Idempotency-Key: <uuid>`) that enables the server to identify and deduplicate retried requests. When a server receives a request with an idempotency key, it: (1) checks a key-value store for a prior response to that key; (2) if found, returns the cached response without reprocessing; (3) if not found, processes the request and stores the response indexed by the key for future deduplication. An operation is **idempotent** if executing it multiple times produces the same outcome as executing it once. GET, HEAD, PUT, DELETE are inherently idempotent; POST is not (each POST creates a new resource). Idempotency keys make non-idempotent POST operations safe to retry. This is critical in distributed systems where network failures make retry necessary but duplicate processing must be prevented.

---

### 🟢 Simple Definition (Easy)

Idempotency Key: a unique ID you attach to a request. If the server processes it successfully, it remembers "I've done #ABC123 — don't do it again." If the same request is retried (due to network failure), the server returns the cached result instead of executing again. Prevents: paying twice for one order, creating two accounts, sending two emails.

---

### 🔵 Simple Definition (Elaborated)

You submit a payment: `POST /payments {amount: 100}`. Network drops. Did the server receive it? You don't know. If you retry and it WAS processed → double charge. If you don't retry and it WASN'T → payment lost. Idempotency key solves this: `POST /payments {amount: 100}` with header `Idempotency-Key: order-789-pay-attempt-1`. Server processes payment, stores result indexed by `order-789-pay-attempt-1`. You retry (not knowing if it succeeded). Server: "seen `order-789-pay-attempt-1` — returning cached result." One payment executed, regardless of how many retries.

---

### 🔩 First Principles Explanation

**Implementation and storage strategy:**

```
IDEMPOTENCY KEY LIFECYCLE:

  CLIENT SIDE:
    1. Generate idempotency key (UUID v4) BEFORE sending request.
       Key: must be unique per intended operation (not per retry attempt).
       Store: persist key locally until you receive a definitive response.

  SERVER SIDE (on receiving request with Idempotency-Key header):
    1. Check key-value store: EXISTS idempotency-key-store[key]?
    2. If EXISTS:
       a. Retrieve stored response.
       b. Return stored response (cache hit).
       c. Log: "Duplicate request detected, returning cached result."
    3. If NOT EXISTS:
       a. Acquire distributed lock on key (prevent concurrent processing of same key).
       b. Process request.
       c. Store result: key → {status, response_body, expires_at}
       d. Release lock.
       e. Return result.

  IDEMPOTENCY KEY STORAGE:
    Redis (recommended):
    SET idempotency:{key} {response_json} EX 86400  // TTL: 24 hours

    TTL selection:
    - Too short: expired key → duplicate processing on late retry
    - Too long: wasted memory
    - Rule: TTL >> client's maximum retry window
    - Stripe: 24 hours. Most systems: 24 hours to 7 days.

CONCURRENT REQUEST HANDLING:

  Problem: client sends same idempotency key simultaneously (two retries at once).

  Thread A → check key: NOT EXISTS → start processing
  Thread B → check key: NOT EXISTS → start processing (race condition!)
  Both threads process → double execution!

  FIX: Distributed lock on idempotency key during processing.

  REDIS SETNX (SET if Not eXists) — atomic check-and-lock:

  // Lua script (atomic): check-and-reserve
  local existing = redis.call("GET", KEYS[1])
  if existing then
    return existing  -- return cached response
  end

  -- Mark as IN_PROGRESS (lock):
  local locked = redis.call("SET", KEYS[1], "PROCESSING", "NX", "EX", 30)
  if not locked then
    return "LOCKED"  -- another request is processing
  end
  return "NEW"  -- proceed to process

  Application logic:
    result = executeAtomicCheckAndLock(idempotencyKey)
    if result == "LOCKED":
      // Concurrent duplicate: wait and retry get
      Thread.sleep(100)
      return getFromCache(idempotencyKey)
    if result != "NEW":
      return parseExistingResponse(result)
    // Proceed with processing...
    storeResult(idempotencyKey, response)

IDEMPOTENCY KEY FORMAT (best practices):

  GOOD:
    UUID v4: "550e8400-e29b-41d4-a716-446655440000"
    → Random, globally unique, no coordination needed.
    → Client generates. Include user_id prefix to namespace.
    → "user_123:550e8400-e29b-41d4-a716-446655440000"

  ALSO GOOD (semantic keys):
    "order_789:payment:attempt_1"
    → Human-readable. Deterministic (retry uses same key).
    → Namespace collision possible: add service prefix.

  BAD:
    Timestamp only: "1672531261"  → two requests same second = collision
    Sequential ID: "12345"  → sequential keys = predictable, forgeable
    Request body hash: SHA256(payload) → different amount = different key
                       → same amount = same key (wrong! distinct operations can have same amount)

IDEMPOTENCY IN DIFFERENT CONTEXTS:

  HTTP APIs (Stripe, Braintree, PayPal):
    Header: Idempotency-Key: <uuid>

  Database operations:
    INSERT IGNORE / ON CONFLICT DO NOTHING (natural idempotency via unique key):

    // PostgreSQL: idempotent insert (no duplicate on retry)
    INSERT INTO orders (order_id, user_id, amount)
    VALUES ('order_789', 123, 100)
    ON CONFLICT (order_id) DO NOTHING;

    -- Retried: order_id already exists → no-op (idempotent)

  Message queue consumers (Kafka, SQS):
    // At-least-once delivery → consumer may process message twice.
    // Idempotent consumer: store processed message IDs.

    processedMessages: Set<String>

    onMessage(message):
      if processedMessages.contains(message.id): return  // duplicate
      processedMessages.add(message.id)
      actuallyProcess(message)

  Email/notification sending:
    // Send email with idempotency key = email_id (not message_id)
    if (redis.SETNX("email:sent:" + email_id, "1", EX=604800)) {
      emailService.send(...)  // only first execution
    }
    // Retries: key exists → SETNX fails → no duplicate send
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Idempotency Keys:

- Network failure during POST → client doesn't know if request was processed
- Retry → duplicate: double charge, double shipment, double account
- No safe retry → clients either accept data loss or accept duplicates

WITH Idempotency Keys:
→ Retry is always safe: first execution counts, retries return cached result
→ Distributed systems can implement at-least-once delivery safely
→ Payment and critical APIs can be retried without business impact

---

### 🧠 Mental Model / Analogy

> A bank teller receives a check with a serial number. She stamps it "PROCESSED" in her log. If the same check is presented again (customer re-submitted by mistake), she looks up the serial number: "already processed on Monday — here's the receipt from Monday." The serial number on the check = the idempotency key. The stamped log = the server's idempotency key store. The teller never processes the same check twice, regardless of how many times it's presented.

"Check serial number" = idempotency key (unique identifier per intended operation)
"Teller's stamp log" = server-side key-value store (Redis) mapping key → cached response
"Same check presented again" = retried HTTP request (with same Idempotency-Key header)
"Returns Monday's receipt" = returns cached response without reprocessing
"Processes new check (different serial)" = new idempotency key → fresh processing

---

### ⚙️ How It Works (Mechanism)

**End-to-end sequence diagram:**

```
Client              API Gateway            Service            Redis
  │                      │                    │                 │
  │──POST /payment──────►│                    │                 │
  │  Idempotency-Key: K1  │                    │                 │
  │                      │──check key K1─────────────────────►│
  │                      │                    │  NOT EXISTS ◄──│
  │                      │──process────────►  │                 │
  │                      │                    │──store K1:resp─►│
  │                      │◄───────────────────│                 │
  │◄───200 OK────────────│                    │                 │
  │  {payment_id: P1}     │                    │                 │
  │                      │                    │                 │
  [Network timeout on client - retries]        │                 │
  │                      │                    │                 │
  │──POST /payment──────►│                    │                 │
  │  Idempotency-Key: K1  │                    │                 │
  │  (same key — retry)   │──check key K1─────────────────────►│
  │                      │                    │  {payment_id: P1} ◄─│
  │◄───200 OK────────────│                    │                 │
  │  {payment_id: P1}     │                    │                 │
  │  (same result, no     │                    │                 │
  │   double charge)      │                    │                 │
```

---

### 🔄 How It Connects (Mini-Map)

```
Network failures / retries (distributed systems reality)
        │
        ▼
Idempotency Key ◄──── (you are here)
(makes retries safe)
        │
        ├── Polling vs Webhooks (webhook retries require idempotent handlers)
        ├── Distributed Locks (prevent concurrent processing of same key)
        └── Outbox Pattern (at-least-once delivery → idempotent consumers)
```

---

### 💻 Code Example

**Spring Boot: idempotency key middleware:**

```java
@Component
public class IdempotencyFilter implements OncePerRequestFilter {

    @Autowired private RedisTemplate<String, String> redisTemplate;

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain) throws IOException, ServletException {

        // Only apply to POST/PATCH requests:
        if (!isNonIdempotentMethod(request.getMethod())) {
            filterChain.doFilter(request, response);
            return;
        }

        String idempotencyKey = request.getHeader("Idempotency-Key");
        if (idempotencyKey == null) {
            filterChain.doFilter(request, response);  // no key: proceed normally
            return;
        }

        String cacheKey = "idem:" + idempotencyKey;

        // Check for existing response:
        String cached = redisTemplate.opsForValue().get(cacheKey);
        if (cached != null) {
            // Serve cached response:
            IdempotencyResponse cachedResponse = deserialize(cached);
            response.setStatus(cachedResponse.getStatus());
            response.setContentType("application/json");
            response.getWriter().write(cachedResponse.getBody());
            return;
        }

        // Capture the actual response:
        ContentCachingResponseWrapper responseWrapper =
            new ContentCachingResponseWrapper(response);

        filterChain.doFilter(request, responseWrapper);
        responseWrapper.copyBodyToResponse();

        // Cache the response for future retries (24 hours TTL):
        if (responseWrapper.getStatus() < 500) {  // don't cache server errors
            String responseBody = new String(responseWrapper.getContentAsByteArray());
            redisTemplate.opsForValue().set(
                cacheKey,
                serialize(responseWrapper.getStatus(), responseBody),
                Duration.ofHours(24)
            );
        }
    }
}

// Usage (client side):
RestTemplate restTemplate = new RestTemplate();
HttpHeaders headers = new HttpHeaders();
headers.set("Idempotency-Key", UUID.randomUUID().toString());
// Store the idempotency key: if this request needs to be retried,
// use the SAME key (not a new UUID) so the server deduplicates.
```

---

### ⚠️ Common Misconceptions

| Misconception                                                 | Reality                                                                                                                                                                                                                                                                                                                                             |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Idempotency key is the same as a transaction ID or request ID | Transaction ID / correlation ID is used for tracing and logging. Idempotency key is used for deduplication. A transaction ID is often assigned by the SERVER after receiving the request; an idempotency key is generated by the CLIENT before sending, ensuring safe retries even before server acknowledgement                                    |
| PUT requests don't need idempotency keys                      | PUT is inherently idempotent by definition (PUT to the same resource with the same data produces the same state regardless of repetition). But in practice, a PUT that triggers side effects (sends email, charges payment) may not be idempotent — in those cases, an idempotency key is still needed for the side effects                         |
| Storing idempotency keys forever is required                  | Keys should expire after the maximum retry window + safety margin. Stripe uses 24 hours. Long-lived storage of idempotency keys wastes memory. Use TTL matching your retry policy: if retries stop after 1 hour, key TTL of 2 hours is sufficient                                                                                                   |
| Idempotency keys must be server-generated to be trusted       | Client-generated idempotency keys are the standard (Stripe, Braintree, PayPal all use client-generated keys). The client is in the best position to know "this is my intent to pay exactly once for order #789." Server-generated keys can't prevent the first duplicate (the server doesn't know the client's intent before receiving the request) |

---

### 🔥 Pitfalls in Production

**Generating new idempotency key on each retry (defeats the purpose):**

```
PROBLEM: Client generates new UUID on every attempt

  // WRONG:
  public PaymentResult charge(long amount) {
    for (int attempt = 0; attempt < 3; attempt++) {
      try {
        String idempotencyKey = UUID.randomUUID().toString();  // NEW key each time!
        return httpClient.post("/payments",
          Map.of("amount", amount),
          Map.of("Idempotency-Key", idempotencyKey));
      } catch (NetworkException e) {
        // retry...
      }
    }
  }

  RESULT:
    Attempt 1: key=abc123 → payment processed (P1 created)
    Network timeout → client doesn't get 200
    Attempt 2: key=def456 → NEW KEY → server processes AGAIN → P2 created
    Attempt 3: key=ghi789 → NEW KEY → server processes AGAIN → P3 created

    Customer charged 3× for one intended payment.
    Each attempt has a different key → no deduplication possible.

FIX: Generate key ONCE, store it, reuse on retries

  // CORRECT:
  public PaymentResult charge(String orderId, long amount) {
    // Generate idempotency key ONCE per order-payment intent:
    String idempotencyKey = "order-" + orderId + "-payment";  // deterministic!
    // OR: generate UUID once, persist with the order:
    // String idempotencyKey = order.getIdempotencyKey(); // stored in DB

    for (int attempt = 0; attempt < 3; attempt++) {
      try {
        return httpClient.post("/payments",
          Map.of("amount", amount),
          Map.of("Idempotency-Key", idempotencyKey));  // SAME key each attempt
      } catch (NetworkException e) {
        // retry with same key → server deduplicates if first attempt succeeded
      }
    }
  }

  RESULT:
    Attempt 1: key=order-789-payment → payment processed (P1)
    Attempt 2: key=order-789-payment → server returns cached P1 result → no duplicate
    Attempt 3: key=order-789-payment → server returns cached P1 result → no duplicate
    Customer charged exactly once.
```

---

### 🔗 Related Keywords

- `Polling vs Webhooks` — webhook retries from providers require idempotent handlers
- `Distributed Locks` — prevent concurrent processing of the same idempotency key
- `Outbox Pattern` — combines at-least-once delivery with idempotent consumers
- `Saga Pattern` — distributed transactions use idempotency for compensation steps

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Client-generated unique key enables       │
│              │ server to deduplicate retried requests    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ POST/mutation APIs; payment processing;   │
│              │ webhook handlers; at-least-once messaging │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Generating new key per retry attempt;     │
│              │ caching error responses (only 2xx/4xx)    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Check serial number prevents banker from │
│              │  cashing the same check twice."           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Distributed Locks → Outbox Pattern        │
│              │ → Saga Pattern                            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A payment API uses Redis to store idempotency keys with a 24-hour TTL. A client sends `POST /payments` with key `order-789`. The request takes 35 seconds (slow payment processor). The client's HTTP timeout is 30 seconds, so it gets a timeout error and retries with the SAME key. At the time of retry, the first request is still executing (hasn't finished yet). What race condition exists? How does the server handle this? Design the concurrency control mechanism to prevent double-charging in this scenario.

**Q2.** Your system processes Kafka messages to send transactional emails (order confirmations). Kafka provides at-least-once delivery, so messages may be delivered twice. Design an idempotent email consumer. Specifically: (a) what is the idempotency key for an "order_confirmed" email? (b) where do you store the "already sent" state — Redis, PostgreSQL, or Kafka itself? (c) what are the failure modes where your idempotency mechanism itself might fail, and how do you handle them?
