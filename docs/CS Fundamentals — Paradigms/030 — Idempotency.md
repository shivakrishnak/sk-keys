---
layout: default
title: "Idempotency"
parent: "CS Fundamentals — Paradigms"
nav_order: 30
permalink: /cs-fundamentals/idempotency/
number: "0030"
category: CS Fundamentals — Paradigms
difficulty: ★★☆
depends_on: Side Effects, Referential Transparency
used_by: Distributed Systems, HTTP & APIs, Microservices
related: Side Effects, Referential Transparency, Distributed Systems, HTTP Methods
tags:
  - intermediate
  - distributed-systems
  - correctness
  - first-principles
  - mental-model
---

# 030 — Idempotency

⚡ TL;DR — An operation is idempotent if applying it multiple times produces the same result as applying it once — making retries and deduplication safe.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #030         │ Category: CS Fundamentals — Paradigms │ Difficulty: ★★☆        │
├──────────────┼───────────────────────────────────────┼────────────────────────┤
│ Depends on:  │ Side Effects, Referential Transparency│                        │
│ Used by:     │ Distributed Systems, HTTP & APIs,     │                        │
│              │ Microservices                         │                        │
│ Related:     │ Side Effects, Referential Transparency,│                        │
│              │ Distributed Systems, HTTP Methods     │                        │
└─────────────────────────────────────────────────────────────────────────────────┘

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:

In distributed systems, network calls can fail, time out, or succeed but have their response lost in transit. The caller cannot distinguish between "the operation never happened" and "the operation happened but I didn't get a response." If the caller retries, and the operation already completed, it might execute twice. Charging a customer twice, creating a duplicate order, sending two emails — these are the consequences of non-idempotent operations in unreliable networks.

THE BREAKING POINT:

A payment processing service receives a charge request. It processes the charge and sends a success response — but the network drops the response. The caller, seeing a timeout, retries. The payment processor doesn't know this is a retry and charges the customer again. The customer is charged twice. This is the most common class of data corruption bug in distributed systems.

THE INVENTION MOMENT:

Idempotency is the property that prevents this: design operations so that executing them multiple times has the same effect as executing them once. Then retries are safe — the second execution is a no-op (or verifies the first succeeded). Idempotency keys, database unique constraints, and at-most-once/exactly-once semantics in messaging systems are all implementations of this principle.

---

### 📘 Textbook Definition

An operation `f` is **idempotent** if applying it multiple times produces the same result as applying it once: `f(f(x)) = f(x)` for all valid inputs `x`. In distributed systems, an operation is idempotent if executing it multiple times with the same input has the same observable effect on the system as executing it exactly once. HTTP defines `GET`, `PUT`, `DELETE`, and `HEAD` as idempotent — calling them multiple times produces the same server state as calling them once. `POST` is explicitly not idempotent. Idempotency is a design property, not a mathematical guarantee — it must be engineered into operations. The primary mechanism is the **idempotency key**: a unique token per logical operation that servers use to detect and deduplicate retries.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Idempotent operations are safe to retry — running them twice is the same as running them once.

**One analogy:**
> An idempotent operation is like a **light switch going to ON**. Flipping it once: light is on. Flipping it again (it's already ON → no change): light is still on. The result is the same regardless of how many times you flip it *to ON*. Contrast with "toggle" (non-idempotent): the result depends on how many times you toggle — once is ON, twice is OFF, three times is ON again. In unreliable networks, idempotent operations are the switches, not the toggles.

**One insight:**
Idempotency is critical at every network boundary in a distributed system. Any operation that can be retried (which is any operation over a network — all of them) must be idempotent, or duplicates must be explicitly handled. The Stripe API, the AWS SDK, Kubernetes API server — all use idempotency keys. If your service doesn't, you're one network glitch away from duplicate data.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:

1. `f(f(x)) = f(x)` — applying the operation twice gives the same result as once
2. Idempotency is about *observable effects*, not just return values. `DELETE /orders/123` should produce "order 123 is deleted" whether called once or five times
3. Idempotency is scoped: an operation may be idempotent for a given idempotency key but not globally (idempotency key "abc123" maps to one specific charge)
4. Idempotency does not mean the operation is a no-op on retry — it means the *net observable effect* is the same

DERIVED DESIGN:

```
IDEMPOTENT OPERATIONS:
  DELETE /orders/123
    1st call: deletes order → 200 OK or 204 No Content
    2nd call: order already deleted → 200 OK or 404 Not Found
    Net effect: order 123 is deleted. Same after 1 or 5 calls.

  PUT /users/456 {"name": "Alice"}
    1st call: creates/replaces user → 201 Created or 200 OK
    2nd call: same user → 200 OK
    Net effect: user 456 = {"name": "Alice"}. Same after 1 or 5 calls.

  SET key=value (database)
    1st call: key set to value
    2nd call: key already = value, no change
    Net effect: key = value. Same after 1 or 5 calls.

NON-IDEMPOTENT OPERATIONS:
  POST /orders (create new order)
    1st call: creates order #1001
    2nd call: creates order #1002  ← different effect!
    Net effect: varies with number of calls.

  INCREMENT counter
    1st call: counter = 1
    2nd call: counter = 2  ← different effect!
```

THE TRADE-OFFS:

Gain: safe retries without duplicates; simplifies distributed systems error handling; eliminates a whole class of "double-charge" / "double-create" bugs.  
Cost: idempotency keys require storage (idempotency key DB/cache); key management adds complexity; choosing the right idempotency scope requires design; "exactly-once" messaging is expensive (requires distributed coordination — most systems settle for "at-least-once" + idempotent consumers).

---

### 🧪 Thought Experiment

SETUP:
Design the payment API for a payment processor. Clients might experience network timeouts and retry. How do you prevent double-charges?

NAIVE DESIGN (no idempotency):
```
POST /charges { amount: 100, customer: "cust_123" }
  → charges $100, creates charge_001, returns { id: "charge_001" }

Network timeout — client doesn't receive response.
Client retries:
POST /charges { amount: 100, customer: "cust_123" }
  → charges $100 AGAIN, creates charge_002, returns { id: "charge_002" }

Customer is charged $200. BUG.
```

IDEMPOTENCY KEY DESIGN:
```
Client generates a unique idempotency key before first attempt:
  idempotency_key = "order_5555_payment_attempt_1"  (UUID or business ID)

POST /charges
  { amount: 100, customer: "cust_123", idempotency_key: "order_5555_payment_attempt_1" }
  → Server records key in idempotency store: key → { status: processing }
  → Charges $100, creates charge_001
  → Stores in idempotency store: key → { status: complete, charge_id: "charge_001" }
  → Returns charge_001

Network timeout — client doesn't receive response.
Client retries:
POST /charges
  { amount: 100, customer: "cust_123", idempotency_key: "order_5555_payment_attempt_1" }
  → Server looks up key in idempotency store
  → Finds: key → { status: complete, charge_id: "charge_001" }
  → Returns charge_001 WITHOUT charging again

Customer is charged $100 exactly once. CORRECT.
```

THE INSIGHT:
The idempotency key converts a non-idempotent `POST` (create charge) into an idempotent operation (create charge OR return existing charge for this key). This is the production-grade solution used by Stripe, Braintree, and every serious payment API.

---

### 🧠 Mental Model / Analogy

> Idempotency is like **pressing an elevator button that's already lit**. You press the button once — it's pressed. You press it again — it's already pressed, nothing changes. The elevator still comes once. Non-idempotent would be: every press sends a new request, and the elevator comes once per press — causing traffic jams. In distributed systems, the "elevator button" is an idempotency key, and "already lit" is the server's idempotency store saying "I already processed this request."

**Mapping:**
- "Pressing an elevator button" → making an API call
- "Button already lit" → idempotency key already exists in server's store
- "Nothing changes" → server returns the same result as the first call (no duplicate processing)
- "Every press summons a new elevator" → non-idempotent POST creating duplicate records per retry

**Where this analogy breaks down:** An elevator button cancels itself (turns off) once the elevator arrives. Idempotency keys have an expiry time — after which the key is cleared and a new request with the same key might create a new charge. Also, elevator buttons don't have network timeouts.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
An idempotent operation can be done again and again without causing problems. Pressing "save" once or 10 times has the same result — the file is saved. Deleting an email once or 10 times — it's deleted. Creating a new email 10 times — you have 10 emails! Creation is usually not idempotent; deletion and updates usually are (when designed carefully).

**Level 2 — How to use it (junior developer):**
HTTP methods and idempotency: `GET` (read, no change), `PUT` (replace entirely), `DELETE` (remove), `HEAD` — all idempotent. `POST` (create new) — not idempotent. `PATCH` (partial update) — depends on implementation. Design REST APIs: use `PUT` for updates when possible (idempotent); use `POST` only for creation; add idempotency keys to `POST` endpoints where retry safety matters. Database operations: `INSERT OR IGNORE`, `UPSERT`, `SET column=value WHERE id=X` — idempotent. `INSERT` without conflict handling — not idempotent.

**Level 3 — How it works (mid-level engineer):**
Three mechanisms for implementing idempotency: (1) **Database unique constraints + upsert**: `INSERT INTO charges (idempotency_key, ...) ON CONFLICT DO UPDATE ...` — the DB enforces deduplication. (2) **Idempotency key store**: check Redis/DB for the key before processing; if present, return cached result. Requires choosing an expiry (24–48 hours is common for payment APIs). (3) **Natural idempotency**: `SET user.status='ACTIVE'` is naturally idempotent — running it twice is identical to once. Design data model mutations to be SET-style (absolute state) rather than INCREMENT-style (relative change). `message_processing` topic: at-least-once delivery (Kafka default) + idempotent consumers = effectively-exactly-once semantics without expensive distributed transactions.

**Level 4 — Why it was designed this way (senior/staff):**
Idempotency is the engineering response to the **Two Generals' Problem** and the **Exactly-Once problem** in distributed systems. In a distributed network, it's impossible to guarantee that a message was delivered exactly once — you can only guarantee at-most-once (fire and forget) or at-least-once (retry until acknowledged). Exactly-once requires either: (a) idempotent consumer with at-least-once delivery (most practical), or (b) 2-phase commit / distributed transactions (expensive, reduces availability). Kafka's producer has optional exactly-once semantics (producer `enable.idempotence=true` + transactional API) which uses sequence numbers and an epoch to deduplicate: the broker tracks the producer's sequence number and rejects duplicates. This is implemented entirely through idempotency logic, not distributed locking. Stripe's idempotency key implementation stores keys in a database with the full request and response — this also enables retrying in-progress requests safely (the second caller waits for the first to complete, then returns its result). This is the production-grade reference implementation.

---

### ⚙️ How It Works (Mechanism)

**Idempotency key flow:**

```
┌────────────────────────────────────────────────────────────┐
│              IDEMPOTENCY KEY FLOW                          │
│                                                            │
│  CLIENT                        SERVER                      │
│  ──────                        ──────                      │
│  Generate key: uuid-123                                    │
│       │                                                    │
│       │──── POST /charges ─────────────────────────────►  │
│       │     Idempotency-Key: uuid-123                      │
│       │                                                    │
│       │            Look up uuid-123 in store               │
│       │            Not found → process charge              │
│       │            Store: uuid-123 → {status: processing}  │
│       │            Execute charge                          │
│       │            Store: uuid-123 → {status: done,        │
│       │                               result: charge_001}  │
│       │◄───── 201 { id: charge_001 } ──────────────────── │
│                                                            │
│  [Network failure — client didn't receive response]        │
│                                                            │
│       │──── POST /charges ─────────────────────────────►  │
│       │     Idempotency-Key: uuid-123  (same key)          │
│       │                                                    │
│       │            Look up uuid-123 in store               │
│       │            Found: {status: done, result: charge_001}│
│       │            DO NOT re-charge                        │
│       │◄───── 200 { id: charge_001 } ──────────────────── │
│                                                            │
│  ✓ One charge, two requests — customer charged once       │
└────────────────────────────────────────────────────────────┘
```

**HTTP method idempotency:**

```
┌──────────┬──────────────┬───────────────────────────────────┐
│ Method   │ Idempotent?  │ Safe?   │ Typical Use             │
├──────────┼──────────────┼─────────┼─────────────────────────┤
│ GET      │ Yes          │ Yes     │ Read resource            │
│ HEAD     │ Yes          │ Yes     │ Read headers only        │
│ PUT      │ Yes          │ No      │ Replace entire resource  │
│ DELETE   │ Yes          │ No      │ Remove resource          │
│ POST     │ No           │ No      │ Create / arbitrary action│
│ PATCH    │ Depends*     │ No      │ Partial update           │
│ OPTIONS  │ Yes          │ Yes     │ Discover capabilities    │
└──────────┴──────────────┴─────────┴─────────────────────────┘
* PATCH is idempotent if setting absolute values: {"status": "active"}
  NOT idempotent if incremental: {"increment_views": 1}
Safe = no server state changed; Idempotent = same effect on retry
```

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:

```
Client calls CREATE PAYMENT (POST) with idempotency key "key-abc"
      ↓
Server: check idempotency store for "key-abc"
      ↓
Not found → begin processing
      ↓
Store: "key-abc" → { status: in_progress }
      ↓
Process payment (DB write, payment gateway call)
      ↓
Store: "key-abc" → { status: complete, payment_id: "pay_123", response: {...} }
      ↓
Return response
```

FAILURE PATH — RETRY SCENARIO:

```
Scenario A: First request timed out, payment not processed
  Client retries with same key
  Server: key not found (or status: pending) → process normally
  Result: payment processed once ✓

Scenario B: Payment processed, response lost
  Client retries with same key
  Server: key found, status: complete
  Return cached response WITHOUT reprocessing
  Result: payment counted once, client gets response ✓

Scenario C: Two simultaneous retries (race condition)
  Both requests arrive simultaneously
  Server: check + lock: "key-abc" → { status: in_progress }
  Second request: key found, status: in_progress → wait for completion
  First completes: status: complete
  Second receives: complete result
  Result: payment processed once ✓ (requires optimistic locking or DB constraint)
```

WHAT CHANGES AT SCALE:

At scale (millions of API calls/hour), idempotency stores must be fast and consistent. Redis is commonly used (set with NX flag: `SET key value NX EX 86400` — set only if not exists, expire in 24h). At Stripe's scale, the idempotency key store must handle millions of keys with sub-millisecond lookup, survive node failures (Redis cluster/sentinel), and have atomic check-and-set (no race conditions between key lookup and key creation). The idempotency key also becomes an audit trail: every payment attempt is recorded. This doubles as a fraud detection data source — patterns of retries with the same key may indicate network issues; patterns of retries with different keys may indicate fraud.

---

### 💻 Code Example

**Example 1 — Idempotency key in a payment service (Spring Boot):**
```java
@Service
public class PaymentService {
    @Autowired private IdempotencyStore idempotencyStore;
    @Autowired private PaymentGateway paymentGateway;
    @Autowired private PaymentRepository paymentRepository;

    public PaymentResponse processPayment(PaymentRequest request, String idempotencyKey) {
        // Check if this request was already processed
        Optional<PaymentResponse> cached = idempotencyStore.get(idempotencyKey);
        if (cached.isPresent()) {
            log.info("Idempotent request: key={} returning cached result", idempotencyKey);
            return cached.get();  // return same result, no re-processing
        }

        // Mark as in-progress (optimistic lock — prevents concurrent duplicates)
        idempotencyStore.setInProgress(idempotencyKey);

        try {
            // Process the payment
            ChargeResult charge = paymentGateway.charge(
                request.getCustomerId(), request.getAmount()
            );
            Payment payment = new Payment(charge.getId(), request.getAmount());
            paymentRepository.save(payment);

            PaymentResponse response = new PaymentResponse(payment.getId(), "success");

            // Cache the successful result (expire after 24 hours)
            idempotencyStore.setComplete(idempotencyKey, response, Duration.ofHours(24));
            return response;

        } catch (Exception e) {
            idempotencyStore.setFailed(idempotencyKey);
            throw e;
        }
    }
}
```

**Example 2 — Database-level idempotency (upsert pattern):**
```java
// NON-IDEMPOTENT: INSERT creates duplicate on retry
jdbcTemplate.update(
    "INSERT INTO user_preferences (user_id, theme, language) VALUES (?, ?, ?)",
    userId, theme, language
);
// Retry: creates second row with same user_id

// IDEMPOTENT: UPSERT replaces or ignores on retry
jdbcTemplate.update(
    """
    INSERT INTO user_preferences (user_id, theme, language)
    VALUES (?, ?, ?)
    ON CONFLICT (user_id)
    DO UPDATE SET theme = EXCLUDED.theme, language = EXCLUDED.language
    """,
    userId, theme, language
);
// Retry: updates to same values → net effect identical to first call

// IDEMPOTENT: conditional update (only if not already done)
jdbcTemplate.update(
    "UPDATE orders SET status='SHIPPED' WHERE id=? AND status='PROCESSING'",
    orderId
);
// Retry: status already 'SHIPPED' → WHERE clause fails → 0 rows updated → no change
```

**Example 3 — Idempotent message consumer (Kafka + Spring):**
```java
@KafkaListener(topics = "payment-events")
public void handlePaymentEvent(PaymentEvent event) {
    String eventId = event.getEventId();

    // Check if already processed (Redis or DB)
    if (processedEventStore.contains(eventId)) {
        log.debug("Duplicate event skipped: {}", eventId);
        return;  // idempotent: skip re-processing
    }

    // Process the event
    try {
        paymentService.applyPayment(event.getPaymentId(), event.getAmount());

        // Mark as processed — AFTER successful processing
        processedEventStore.mark(eventId, Duration.ofDays(7));

    } catch (Exception e) {
        // Don't mark as processed: allow retry
        log.error("Failed to process event: {}", eventId, e);
        throw e;  // re-throw to trigger Kafka retry
    }
}
// Kafka at-least-once delivery + idempotent consumer = effectively exactly-once
```

---

### ⚖️ Comparison Table

| Operation | Idempotent? | Why | Safe to Retry? |
|---|---|---|---|
| `GET /user/123` | Yes | No state change | Yes |
| `PUT /user/123 { name: Alice }` | Yes | Same state on repeat | Yes |
| `DELETE /user/123` | Yes | Deleted is deleted | Yes |
| `POST /orders` (create new) | No | Creates new each time | Requires key |
| `PATCH /counter/1 {increment: 1}` | No | Increments each time | Requires key |
| `PATCH /user/1 {status: ACTIVE}` | Yes | SET is idempotent | Yes |
| `INSERT INTO table` | No | Duplicates each time | Requires ON CONFLICT |
| `INSERT ... ON CONFLICT DO UPDATE` | Yes | Upsert is idempotent | Yes |

**How to choose:** Design mutations as absolute-state SET operations (`SET status = 'active'`) rather than relative-change operations (`INCREMENT views by 1`) whenever possible. Add idempotency keys to any `POST` endpoint that performs important state changes. Use `ON CONFLICT DO UPDATE` (upsert) for database inserts where duplicates must be handled.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Idempotency = the operation does nothing on retry | No — the operation may DO work on retry (e.g., update a field to the same value). Idempotency means the NET OBSERVABLE EFFECT is the same. The operation can re-execute fully or return a cached result — both are valid. |
| DELETE is always idempotent | By standard, `DELETE /resource/123` should return 2xx on second call (resource already gone). Some APIs return 404 on second call — which is technically a different response, but the net state (resource is deleted) is the same. Whether 404 violates idempotency is debated; the important thing is that the *resource* is gone either way. |
| Idempotency and safety are the same thing | Different properties. Safe = no server state change (GET is safe). Idempotent = same effect on multiple calls (DELETE is idempotent but not safe — it changes state). A GET that logs every read is safe (no business state change) but technically not pure; a DELETE that sends one email is idempotent for state but not for email. |
| PUT is always idempotent | `PUT` replaces the full resource — idempotent when the payload is the same. But if the server derives values from other state (e.g., `updatedAt = now()`), `PUT` may produce different state on repeated calls. Design PUT handlers carefully. |
| Idempotency keys must be UUIDs | UUIDs are common but any unique identifier works. Stripe recommends business-meaningful keys when possible (e.g., "order_1234_payment_1") — better for debugging and audit trails than random UUIDs. |

---

### 🚨 Failure Modes & Diagnosis

**Double-Charge from Missing Idempotency Key**

Symptom:
Customer support receives complaint: "I was charged twice." Database shows two charges with identical amounts at timestamps seconds apart. Payment gateway shows two successful transactions.

Root Cause:
`POST /payments` endpoint is not idempotent. Client experienced a network timeout, retried with a new request (no idempotency key), and the payment processor created a second charge.

Diagnostic Command / Tool:
```sql
-- Find duplicate charges within 60 seconds from the same customer:
SELECT customer_id, amount, COUNT(*) as charge_count,
       MIN(created_at) as first_charge, MAX(created_at) as last_charge
FROM charges
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY customer_id, amount
HAVING COUNT(*) > 1
ORDER BY charge_count DESC;

-- Check API request logs for same customer, same amount, same minute:
-- grep "POST /payments" access.log | awk '{print $5, $8, $10}' | sort | uniq -d
```

Fix (immediate): refund the duplicate charge.  
Fix (permanent): add idempotency key support to `POST /payments`. Require clients to send an `Idempotency-Key` header. Store keys in Redis with 24-hour TTL. Return the original response on duplicate key.

Prevention:
API contract: all mutating endpoints that clients might retry MUST support idempotency keys. Document this in the API spec. Add server-side validation: reject `POST /payments` requests without `Idempotency-Key` header (or generate one from request hash as fallback). Review retry logic in all API clients — ensure they reuse the same idempotency key on retries of the same logical operation.

---

**Idempotency Store Race Condition (Two Simultaneous Retries)**

Symptom:
Despite idempotency key implementation, occasional duplicate records in database. Race condition under load.

Root Cause:
Check-then-act is not atomic: two threads check for the key simultaneously, both find it absent, both proceed to process, both create records.

Diagnostic Command / Tool:
```java
// BUGGY: non-atomic check-then-act
if (!idempotencyStore.contains(key)) {     // thread A and B both read: absent
    processPayment(request);                // thread A and B both execute!
    idempotencyStore.mark(key);            // both mark — too late
}

// FIX: atomic set-if-absent (Redis SETNX or DB unique constraint)
boolean isNew = idempotencyStore.setIfAbsent(key, "processing", Duration.ofHours(24));
if (!isNew) {
    return idempotencyStore.getResult(key);  // return cached result
}
// Only one thread proceeds (the one that won the SETNX race)
processPayment(request);
idempotencyStore.update(key, result);
```

Fix:
Use atomic `SET NX` (Redis: `SET key value NX EX seconds`) or database unique constraint (`INSERT ... ON CONFLICT DO NOTHING`) to make the key creation atomic. The winner processes; the loser polls for the result.

Prevention:
Idempotency store operations must always be atomic. Never use read-then-write patterns. Redis NX flag, `SELECT FOR UPDATE`, or unique DB constraint are the correct primitives.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Side Effects` — idempotency is a property of *effectful* operations; understanding side effects explains what idempotency is protecting against
- `Referential Transparency` — RT (pure functions, no effects) is the stronger property; idempotency is the practical safety property for effectful operations that can't be pure

**Builds On This (learn these next):**
- `Distributed Systems` — idempotency is a critical distributed systems design pattern; retry logic, message queues, and eventual consistency all rely on it
- `HTTP & APIs` — idempotency is codified in HTTP method semantics; REST API design applies it throughout
- `Microservices` — inter-service calls over the network must be idempotent for reliability; idempotency keys are a core microservices design pattern

**Alternatives / Comparisons:**
- `Exactly-Once Processing` — the alternative to idempotency; achieved via distributed transactions (2PC) or Kafka's transactional API; more expensive but eliminates need for idempotent consumers
- `At-Least-Once Delivery` — the common messaging guarantee (Kafka, SQS); requires idempotent consumers to prevent duplicate processing
- `Distributed Transactions (Saga pattern)` — an alternative approach to distributed consistency; uses compensating transactions instead of idempotency for rollback

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ f(f(x)) = f(x): applying an operation     │
│              │ multiple times = same as applying once    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Network retries create duplicates         │
│ SOLVES       │ (double charges, duplicate records)       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Idempotency key = "have you seen this     │
│              │ request before?" → return same result     │
├──────────────┼───────────────────────────────────────────┤
│ HTTP METHODS │ Idempotent: GET, PUT, DELETE, HEAD        │
│              │ NOT idempotent: POST                      │
│              │ Depends: PATCH                            │
├──────────────┼───────────────────────────────────────────┤
│ DB PATTERN   │ INSERT ... ON CONFLICT DO UPDATE (upsert) │
│              │ UPDATE ... WHERE status = old_status      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Safety (no duplicates) vs complexity      │
│              │ (idempotency store management + TTL)      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Idempotency: the difference between      │
│              │  charging once and charging twice when    │
│              │  the network hiccups."                    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Distributed Systems → Event-Driven Arch   │
│              │ → Exactly-Once Processing                 │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Kafka's exactly-once semantics (EOS) were introduced in Kafka 0.11 with the transactional producer API. EOS uses a combination of idempotent producers (each message has a sequence number; broker deduplicates), transactional IDs (producer can commit/abort atomically across partitions), and read-committed consumers (only read committed messages). This achieves exactly-once end-to-end. But EOS has a performance cost: 3–5% throughput reduction compared to at-least-once delivery. Under what production conditions is the performance cost of EOS worth it vs. designing idempotent consumers and accepting at-least-once delivery? What data characteristics make EOS necessary rather than optional?

**Q2.** Stripe's idempotency keys have a 24-hour expiry by default. After 24 hours, a request with the same key will be treated as a new request (potentially creating a new charge). The 24-hour window is a trade-off. Consider two failure scenarios: (a) a client's request is processing for 25 hours due to an extreme server-side delay (batch processing, manual review), then the client retries — what happens? (b) A client has a bug and generates the same idempotency key for two different charges within 24 hours — what happens? What does this reveal about the design constraints on idempotency key generation and expiry, and how does Stripe's documentation address both scenarios?
