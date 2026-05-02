---
layout: default
title: "Idempotency (Distributed)"
parent: "Distributed Systems"
nav_order: 605
permalink: /distributed-systems/idempotency/
number: "0605"
category: Distributed Systems
difficulty: ★★☆
depends_on: Retry with Backoff, Distributed Locking, HTTP Semantics, Database Fundamentals
used_by: Payment APIs, Saga Pattern, Outbox Pattern, Event Sourcing, Retry with Backoff
related: Retry with Backoff, Outbox Pattern, Two-Phase Commit, Distributed Locking, CAS
tags:
  - distributed
  - reliability
  - data-integrity
  - pattern
---

# 605 — Idempotency (Distributed)

⚡ TL;DR — An idempotent operation produces the same result whether executed once or many times; in distributed systems, idempotency keys (unique per-request IDs) stored in a deduplication table allow safe retries of state-changing operations without duplicating side-effects.

| #605            | Category: Distributed Systems                                                  | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Retry with Backoff, Distributed Locking, HTTP Semantics, Database Fundamentals |                 |
| **Used by:**    | Payment APIs, Saga Pattern, Outbox Pattern, Event Sourcing, Retry with Backoff |                 |
| **Related:**    | Retry with Backoff, Outbox Pattern, Two-Phase Commit, Distributed Locking, CAS |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Stripe processes millions of payments. A client submits a `POST /charge` for $100. Network blip — the client receives no response. Was the charge processed? The client retries. Stripe processes the charge again. Customer is charged $200. This is the fundamental problem with distributed systems: the response can be lost even when the operation succeeded. Without idempotency, the client faces an impossible choice: retry and risk duplicates, or don't retry and risk data loss.

**THE INVENTION MOMENT:**
Stripe's solution (widely adopted): clients generate a UUID before making a request and include it as an `Idempotency-Key` header. Stripe stores `{key → result}` in a database. If the same key arrives again, Stripe returns the stored result without re-processing. Client can safely retry any number of times — it always gets the correct result.

---

### 📘 Textbook Definition

**Idempotency** in distributed systems means that an operation can be safely applied multiple times without changing the result beyond the initial application. **Mathematical definition:** f(f(x)) = f(x). **HTTP idempotency:** GET, HEAD, PUT, DELETE are semantically idempotent (specification); POST is not. **Practical mechanism:** an `idempotency key` (client-generated UUID) is included in every state-changing request. The server stores `{idempotency_key → response}` in a **deduplication store**; subsequent requests with the same key return the cached response without re-executing. **Scope:** idempotency key must be scoped to the correct resource to prevent cross-customer key collision (e.g., store by `{account_id, idempotency_key}`). **TTL:** keys are typically retained for 24 hours to 30 days; older keys may be purged.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Send a unique ID with every request that changes state; the server uses it to detect duplicates and return the original result instead of processing again.

**One analogy:**

> Idempotency key is like a check number on a paper check. If you lose the check and write a new one for the same amount, the replacement has a different check number and the bank processes it as a new payment. But if you somehow void the original and re-present it, the bank sees the original check number and knows it was already processed. The check number is the idempotency key.

**One insight:**
The check (idempotency key) must be generated **before** sending the request and **stored on the client** before the network call. If the client generates the key after the call and the network fails, the client doesn't know what key it sent (or if it ever sent one). The key must be durable on the client side first, then included in the request.

---

### 🔩 First Principles Explanation

**SERVER-SIDE IDEMPOTENCY KEY IMPLEMENTATION:**

```sql
-- Deduplication table:
CREATE TABLE idempotency_keys (
    account_id      BIGINT NOT NULL,
    idempotency_key VARCHAR(255) NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    locked_at       TIMESTAMP,           -- prevents concurrent processing of same key
    response_status INT,                 -- stored HTTP status
    response_body   JSONB,               -- stored response
    PRIMARY KEY (account_id, idempotency_key)
);

-- Processing logic (pseudo-code):
BEGIN TRANSACTION;

-- Atomic check-and-insert:
INSERT INTO idempotency_keys (account_id, idempotency_key, locked_at)
VALUES ($account_id, $key, NOW())
ON CONFLICT (account_id, idempotency_key) DO NOTHING;

-- Check if newly inserted (we "own" this key) or pre-existing:
SELECT locked_at, response_status, response_body
FROM idempotency_keys
WHERE account_id = $account_id AND idempotency_key = $key;

IF locked_at IS NOT NULL AND response_status IS NOT NULL:
    -- Key already processed: return stored response
    RETURN stored_response;
ELSE IF we inserted with locked_at (no response yet):
    -- Process the operation:
    result = process_payment(amount, to_account);
    -- Store the result:
    UPDATE idempotency_keys
    SET response_status = 200, response_body = result
    WHERE account_id = $account_id AND idempotency_key = $key;
    COMMIT;
    RETURN result;
ELSE:
    -- Another request is currently processing same key (locked_at is recent):
    RETURN 409 CONFLICT ("Request in progress, retry");
```

**CONCURRENT DUPLICATE REQUESTS:**

```
Client A sends request with key "abc123" at T=0.
Server starts processing. Sets locked_at = T=0, response = NULL.

Client A retries at T=0.1 (before original completes):
  Server sees key "abc123" exists with locked_at=T=0, response=NULL.
  Server returns 409: "Request in progress, retry later."
  Client A waits 500ms and retries again.

Original request completes at T=0.5. Stores response.

Client A retries at T=0.6:
  Server sees key "abc123" with stored response.
  Returns stored 200 response.
  No re-processing. ✓

Race condition prevention: the INSERT ... ON CONFLICT ensures atomicity.
Only one request gets to "own" the key; others see the conflict.
```

**CLIENT-SIDE PATTERN:**

```python
import uuid
import time

class PaymentClient:
    def __init__(self):
        self.pending_requests = {}  # local durable storage

    def charge(self, customer_id, amount):
        # Generate and PERSIST key BEFORE making network call:
        key = str(uuid.uuid4())
        self.pending_requests[key] = {"customer_id": customer_id, "amount": amount}
        # (In production: persist to database, not memory)

        for attempt in range(5):
            try:
                response = http.post('/charge',
                    headers={'Idempotency-Key': key},
                    json={"customer_id": customer_id, "amount": amount})

                if response.status_code in (200, 201):
                    del self.pending_requests[key]  # cleanup
                    return response.json()
                elif response.status_code == 409:
                    time.sleep(0.5)  # in-progress, wait and retry
                    continue
                elif response.status_code >= 400 and response.status_code < 500:
                    raise PermanentError(response)  # don't retry 4xx

            except NetworkError:
                time.sleep(exponential_backoff(attempt))
                # Retry with SAME key — this is the critical part
```

---

### 🧪 Thought Experiment

**WHAT HAPPENS IF THE CLIENT GENERATES A NEW KEY ON RETRY?**

Client sends charge with key "key-1". Server processes. Network drops response.
Client generates NEW key "key-2" for retry. Server processes AGAIN.
Result: two charges. The entire purpose of idempotency keys is defeated.

**Lesson:** The idempotency key must be:

1. Generated BEFORE the network call
2. Durable (survives process restart — stored in DB, not just RAM)
3. Consistent across all retries of the same logical operation

**IDEMPOTENCY SCOPE MISTAKE:**

Two customers share the same idempotency key format. Customer A uses key "order-001". Customer B uses key "order-001". Server stores keys in a global table (no account_id scoping). Customer B's request with key "order-001" hits the deduplicated response from Customer A's order. Customer B's request is silently dropped; Customer B's order is never created.

**Lesson:** Idempotency keys MUST include a namespace/account scope. Never use global idempotency key namespaces.

---

### 🧠 Mental Model / Analogy

> Idempotency key is like a postal tracking number. If the mail carrier misdelivers a package and the sender believes it was lost (no confirmation), they can re-ship with the SAME tracking number (idempotency). When the package arrives at the destination twice (both the original and the re-shipped copy), the recipient sees two packages with the same tracking number and returns the duplicate — only accepting the first one their system registered. The tracking number is the deduplication mechanism; the client must have it before sending.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Add a unique ID (UUID) to every request that changes state. Server stores "I already processed this ID" and returns the same result on duplicates. Safe to retry anything.

**Level 2:** Server-side deduplication table: `{account_id, idempotency_key} → response`. Concurrent duplicate handling: INSERT ON CONFLICT (PostgreSQL) / conditional writes (DynamoDB). Key TTL: 24h–30 days. Client must generate key before network call and store durably.

**Level 3:** Idempotency at message level: Kafka consumer processes messages at-least-once semantics. Consumer stores `{message_offset → processed}` in a transactional outbox alongside the business state change (same DB transaction) — ensures exactly-once semantics even with consumer restarts. Stripe's idempotency endpoint returns 200 with stored response (not 204 No Content) to allow clients to recover the response.

**Level 4:** Idempotency for distributed sagas: each saga step has its own idempotency key (composite of `{saga_id, step_id}`). If a saga orchestrator crashes mid-execution, it re-runs all steps with their original idempotency keys. Already-completed steps return their cached results instantly. The saga effectively resumes from where it left off without re-executing completed steps. This is a form of **exactly-once saga execution** built on top of at-least-once delivery plus idempotent steps.

---

### ⚙️ How It Works (Mechanism)

**Stripe-style Idempotency Key in Spring:**

```java
@Service
@Transactional
public class PaymentService {

    @Autowired
    private IdempotencyKeyRepository keyRepo;
    @Autowired
    private PaymentRepository paymentRepo;

    public PaymentResponse charge(ChargeRequest request, String idempotencyKey,
                                   long accountId) {
        // Attempt atomic insert-or-find:
        Optional<IdempotencyKey> existing = keyRepo
            .insertOrFind(accountId, idempotencyKey);

        if (existing.isPresent() && existing.get().getResponse() != null) {
            // Already processed: return stored response
            return existing.get().deserializeResponse(PaymentResponse.class);
        }

        if (existing.isPresent() && existing.get().getResponse() == null) {
            // In-progress: another thread is processing same key
            throw new ConflictException("Request in progress for idempotency key");
        }

        // Process payment:
        Payment payment = paymentRepo.save(new Payment(
            request.getAmount(), request.getToAccountId()
        ));
        PaymentResponse response = PaymentResponse.from(payment);

        // Store result against idempotency key:
        keyRepo.storeResponse(accountId, idempotencyKey, response);

        return response;
    }
}
```

---

### ⚖️ Comparison Table

| HTTP Method | Idempotent (spec)   | Safe Retry in Practice                    |
| ----------- | ------------------- | ----------------------------------------- |
| GET         | Yes                 | Yes (read-only)                           |
| PUT         | Yes                 | Yes (replace semantics)                   |
| DELETE      | Yes                 | Yes (second delete is 404, same effect)   |
| POST        | No                  | Only with idempotency key                 |
| PATCH       | No (partial update) | Only with idempotency key + version check |

---

### ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                                                                                                                                       |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PUT is always safe to retry             | PUT is idempotent for the same payload. But if two clients PUT different payloads, the "last write wins" without optimistic locking — idempotency doesn't mean conflict-free                  |
| Idempotency key expiry = data loss risk | Expired keys just allow future requests with that key to be re-processed. This is safe as long as the key is unique enough (UUID) that the same key won't be reused for a different operation |
| Every endpoint needs an idempotency key | Only state-changing endpoints (POST, PATCH). GETs are naturally idempotent. DELETEs are naturally idempotent (second delete = 404, same logical result)                                       |

---

### 🚨 Failure Modes & Diagnosis

**In-Progress Limbo (locked_at but never completed)**

**Symptom:** Clients receive 409 "Request in progress" indefinitely for a specific
idempotency key. The original request never completed (server crashed mid-operation).

Cause: locked_at is set but response_body is never stored (crash between processing
and response storage). Subsequent requests see "in progress" and refuse to proceed.

**Fix:** Add a lock timeout. If locked_at > 30 seconds ago and response is still NULL →
assume the original request crashed → mark key as "failed" → allow reprocessing.
Implement a background sweeper that cleans up stale locked-but-never-completed keys.

---

### 🔗 Related Keywords

- `Retry with Backoff` — requires idempotency for safe retries of state-changing ops
- `Outbox Pattern` — uses message-level idempotency for exactly-once delivery
- `Saga Pattern` — each saga step needs its own idempotency key for crash recovery
- `Two-Phase Commit` — alternative for atomic multi-resource operations without idempotency
- `Event Sourcing` — events are inherently idempotent (replaying same event list = same state)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  IDEMPOTENCY KEY: client-generated UUID per operation    │
│  Server stores: {account_id, key} → response             │
│  Duplicate request: return stored response, no re-exec   │
│  Client: generate key BEFORE call, persist durably       │
│  Scope: always namespace by account/tenant               │
│  TTL: 24h minimum, 30 days preferred                     │
│  Concurrent dupe: INSERT ON CONFLICT → 409 retry later   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A client sends a payment request with `Idempotency-Key: order-789`. The request reaches the server, completes successfully (payment charged), and the response is stored. Then the server crashes. The client receives a network error and retries. But before the retry arrives, the idempotency key table's data is ALSO lost (the crash was a storage failure — a rare scenario). The retry creates a second payment. How would you prevent this double-charge? (Hint: think about where the idempotency state could be stored redundantly to survive storage node crashes.)

**Q2.** You're building a Kafka consumer that processes `OrderPlaced` events to create inventory reservations. Each event must be processed exactly once. Your consumer uses at-least-once delivery semantics. Without idempotency, re-processing a message would double-reserve inventory. Design a complete exactly-once processing mechanism using only: (a) the Kafka message offset, (b) a PostgreSQL table for idempotency keys, and (c) the same database transaction for the inventory reservation. What must be in the same transaction?
