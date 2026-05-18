---
id: CSF-051
title: Idempotency
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★☆
depends_on: CSF-013, CSF-038
used_by: API-015, DST-021, MSG-008
related: CSF-038, API-015, DST-021
tags: [idempotency, api-design, distributed-systems, http-methods, retry-safety]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 51
permalink: /technical-mastery/csf/idempotency/
---

⚡ TL;DR - An operation is idempotent if calling it once
produces the same result as calling it N times. `GET`,
`PUT`, `DELETE` are idempotent. `POST` is not. Critical
for safe retries in distributed systems: duplicate network
requests must not cause duplicate side effects (double
payments, double orders).

| #051 | Category: CS Fundamentals - Paradigms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | CSF-013 (OOP), CSF-038 (Pure Functions) | |
| **Used by:** | API-015 (REST Design), DST-021 (Distributed Patterns), MSG-008 (At-least-once Delivery) | |
| **Related:** | CSF-038 (Pure Functions), API-015 (REST), DST-021 (Idempotency in Distributed Systems) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

A payment service receives a charge request. The service
processes the payment and the database write succeeds.
But before the HTTP response is sent, the network drops.
The client (mobile app) never receives the 200 OK. The
client retries. The payment service receives the request
again and processes the charge AGAIN. The customer is
charged twice. The bank account shows two identical
$99.99 charges. Customer support tickets flood in.

This is the "double payment" problem - one of the most
common and damaging bugs in distributed payment systems.

**THE BREAKING POINT:**

In distributed systems, network failures are normal (not
exceptional). Requests can be lost, delayed, or duplicated
at every hop: client-to-load-balancer, load-balancer-to-service,
service-to-database. Retries are necessary for reliability
(without retries, transient failures cause permanent failures
for users). But retries without idempotency cause duplicate
side effects: double charges, duplicate emails, duplicate
orders, duplicate inventory decrements. The result:
retry = data corruption. No retry = poor reliability.
Both options are bad without idempotency.

**THE INVENTION MOMENT:**

HTTP defined idempotent methods (RFC 7231) as those where
"the intended effect on the server is the same as the first
request." REST API design builds on this: `GET`, `PUT`,
`DELETE` are idempotent by convention. `POST` is not.
Distributed systems add idempotency keys (Stripe popularized
this pattern): a client-generated unique ID included in
the request. The server stores the result keyed by this
ID. On retry (same key), the server returns the stored
result without re-executing the operation. Exactly-once
semantics become achievable: process at least once +
idempotent handler = effective exactly-once behavior.

---

### 📘 Textbook Definition

**Idempotency:** A property of an operation where applying
it multiple times produces the same result as applying
it once. Formally: `f(f(x)) = f(x)` for all valid inputs `x`.
In distributed systems and API design: an operation is
idempotent if sending the same request multiple times has
the same side effects as sending it once.

**Idempotent HTTP methods (RFC 7231):**
- `GET`: safe and idempotent (read-only, no side effects)
- `PUT`: idempotent (set resource to this state; second PUT
  of the same state = no change)
- `DELETE`: idempotent (deleting an already-deleted resource =
  same end state: resource does not exist)
- `PATCH`: NOT idempotent by definition (depends on semantics:
  `PATCH` with `{"increment": 1}` is not idempotent; `PATCH`
  with `{"set": 5}` is)
- `POST`: NOT idempotent (each POST creates a new resource)

**Idempotency key pattern:** A client-generated unique ID
(UUID) sent with non-idempotent requests. The server stores
the result for each key. Duplicate requests with the same
key return the stored result without re-executing.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Do it once or a thousand times - the result is the same.
Essential for safe retries in any distributed system.

**One analogy:**

> Elevator button: pressing the "floor 5" button once or
> five times - the elevator still goes to floor 5.
> Idempotent. Pressing it does not summon 5 elevators.

> Non-idempotent: ATM cash dispensing. Pressing "dispense $100"
> twice does NOT give you $100 - it gives you $200. Each
> press is a new operation with a new side effect. This is
> correct ATM behavior (not a bug) - cash dispensing SHOULD
> be non-idempotent. But payment processing that charges
> a card should be idempotent: retrying on network failure
> must not charge twice.

**One insight:**

`PUT /users/123 {"name": "Alice"}` is idempotent: sending
it three times still results in user 123 having name "Alice."
`POST /users {"name": "Alice"}` is NOT idempotent: sending
it three times creates three users named "Alice" with IDs
123, 124, 125. The difference: `PUT` specifies the final
state (idempotent). `POST` requests a NEW operation (not
idempotent). This is why payment APIs use idempotency keys
on their POST endpoints - to add idempotency to an
inherently non-idempotent operation.

---

### 🔩 First Principles Explanation

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

The essential property: apply the operation, get the result.
Apply again, get the same result. No additional side effects.
The accidental complexity: distributed systems cannot guarantee
exactly-once delivery. Clients must retry. Servers must
handle duplicate requests. Idempotency moves duplicate-request
handling INTO the server (essential complexity location),
removing it from each client (avoiding duplicated accidental
complexity).

**MATHEMATICAL BASIS:**

Idempotent function: `f(f(x)) = f(x)`.
Examples of idempotent operations:
- Absolute value: `abs(abs(-5)) = abs(5) = 5`
- Setting a value: `set(5); set(5)` - result: 5 (not 10)
- SQL `UPSERT`: `INSERT ... ON CONFLICT DO UPDATE` -
  same row, same values on conflict
- Setting a flag: `active = true; active = true` - still true

Non-idempotent:
- `count += 1` - each call changes state
- `INSERT INTO orders` without conflict check - each call
  creates a new row
- `send email` - each call sends a new email

---

### 🧪 Thought Experiment

**THE KAFKA CONSUMER DEDUPLICATION PROBLEM:**

A Kafka consumer reads messages from a topic and writes
them to a database. Kafka guarantees at-least-once delivery:
a message may be delivered more than once (if the consumer
crashes between processing the message and committing the
offset). Without idempotency: duplicate message = duplicate
database row = data corruption.

Solutions:
1. Exactly-once semantics (Kafka transactions): works within
   Kafka ecosystem; complex, lower throughput.
2. Idempotent consumer: include a unique message ID in the
   message. In the database write: `INSERT ... ON CONFLICT (message_id)
   DO NOTHING`. The duplicate write silently does nothing.
   The handler is idempotent: processing the message twice
   has the same effect as processing it once.

**THE LESSON:**

"At least once + idempotent handler = effectively exactly once."
This is cheaper and more reliable than true exactly-once
delivery (which requires distributed coordination).
Idempotency is the tool that makes "at least once" delivery
safe.

---

### 🎯 Mental Model / Analogy

**PAINTING A WALL WHITE:**

Painting a white wall white again = same result (white wall).
Idempotent.

Painting a white wall blue = blue wall. Painting a blue wall
blue again = same result (blue wall). The second blue paint
is idempotent (same color, same result). But blue-on-white
(the first application) is a DIFFERENT operation from
blue-on-blue (the second application), even though the
command "paint blue" is the same.

This is why HTTP `PUT` is idempotent: `PUT /wall {"color": "blue"}`
- first PUT: white wall becomes blue. Second PUT: blue wall
stays blue. Same end state regardless of how many times
applied. `POST /wall-painting {"color": "blue"}` creates
a new painting record each time (N calls = N records).

**MEMORY HOOK:**

"Idempotent = same result, applied once or many times.
HTTP: GET/PUT/DELETE = idempotent. POST/PATCH = not.
Retry-safe = idempotent. Stripe idempotency-key pattern.
At-least-once + idempotent = effectively exactly-once.
Database: INSERT ... ON CONFLICT DO NOTHING = idempotent insert.
PUT = set state. POST = create new. DELETE = remove (already-gone = fine)."

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
Light switch: flicking it up once or five times - the light
is on (if it was off). Idempotent action: the final state
is the same regardless of repetitions. Not idempotent:
a doorbell. Pressing it five times = five rings.

**Level 2 - Student:**
```java
// Idempotent: setting, not incrementing
void setUserActive(String userId) {
    userRepository.updateStatus(userId, "ACTIVE"); // same result each call
}

// NOT idempotent: incrementing
void incrementLoginCount(String userId) {
    userRepository.incrementField(userId, "loginCount", 1); // +1 each call
}
```

**Level 3 - Professional:**
Idempotency key implementation:
```java
@PostMapping("/payments")
ResponseEntity<PaymentResult> charge(
    @RequestHeader("Idempotency-Key") String key,
    @RequestBody PaymentRequest req) {

    // Check if we've seen this key before
    Optional<PaymentResult> cached = idempotencyStore.get(key);
    if (cached.isPresent()) {
        return ResponseEntity.ok(cached.get()); // Return stored result
    }

    // Process the payment (first time only)
    PaymentResult result = paymentService.charge(req);

    // Store result for future duplicate requests
    idempotencyStore.put(key, result, Duration.ofDays(1));
    return ResponseEntity.ok(result);
}
```

**Level 4 - Senior Engineer:**
`INSERT ... ON CONFLICT DO NOTHING` vs idempotency key:
- `ON CONFLICT DO NOTHING`: database-level idempotency for
  the insert operation only. Requires a unique constraint
  (on message_id, order_id, etc.). Works for simple write
  operations. Does NOT deduplicate reads or complex multi-step
  operations.
- Idempotency key with stored result: works for any operation
  (including multi-step transactions). Returns the EXACT
  same response as the original (not just "no-op" - the
  original result including error codes). Required for payment
  APIs where the client needs to know what happened.
- Idempotency store: must be an atomic check-and-set to
  prevent races (two concurrent duplicate requests both
  checking before either stores the result). Use Redis
  `SET key value NX EX ttl` (set if not exists, with expiry).

**Level 5 - Expert:**
Idempotency and distributed sagas: a saga is a sequence of
local transactions, each with a compensating transaction.
For a saga to be safe with retries: each step must be
idempotent (retry won't double-apply) AND each compensating
step must be idempotent (compensation retry won't double-undo).
In Choreography-based sagas (event-driven): the event consumer
must be idempotent. In Orchestration-based sagas: the
orchestrator must check if a step was already completed
(idempotency tracking). Saga idempotency is tracked via
a "saga log" (append-only log of which steps completed,
keyed by saga ID + step number).

---

### ⚙️ How It Works (Formal Basis)

**IDEMPOTENCY KEY RACE CONDITION AND FIX:**

```
┌──────────────────────────────────────────────────────┐
│ CLIENT (mobile app) sends payment request:           │
│   POST /payments                                     │
│   Idempotency-Key: 550e8400-e29b-41d4-a716-...      │
│                                                      │
│ RACE: two concurrent retries arrive simultaneously:  │
│   Thread 1: check store -> NOT FOUND                 │
│   Thread 2: check store -> NOT FOUND                 │
│   Thread 1: process payment -> charges card          │
│   Thread 2: process payment -> charges card AGAIN!   │
│   Thread 1: store result                             │
│   Thread 2: store result (overwrites)                │
│                                                      │
│ FIX: atomic set-if-absent:                           │
│   Redis: SET key "PROCESSING" NX EX 60               │
│   Thread 1: SET -> OK (acquired)                     │
│   Thread 2: SET -> FAIL (key exists)                 │
│   Thread 2: return 409 Conflict / wait and retry     │
│   Thread 1: processes, stores final result           │
│   Thread 2 retry: finds FINAL result, returns it     │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Non-Idempotent vs Idempotent Payment**

```java
// BAD: non-idempotent payment (retry = double charge)
@PostMapping("/payments")
PaymentResult charge(@RequestBody PaymentRequest req) {
    // No idempotency check: every request triggers a new charge
    return stripeService.createCharge(
        req.getAmountCents(),
        req.getCustomerId(),
        req.getPaymentMethodId()
    );
}
// Retry on network failure: customer charged twice.

// GOOD: idempotent payment with Redis-backed key store
@PostMapping("/payments")
ResponseEntity<PaymentResult> charge(
    @RequestHeader(name = "Idempotency-Key", required = true) String key,
    @RequestBody PaymentRequest req) {

    String lockKey = "idem:lock:" + key;
    String resultKey = "idem:result:" + key;

    // Check for cached result first (fast path)
    String cached = redis.get(resultKey);
    if (cached != null) {
        return ResponseEntity.ok(objectMapper.readValue(
            cached, PaymentResult.class));
    }

    // Atomic acquire: only one request processes the payment
    boolean acquired = redis.setIfAbsent(lockKey, "PROCESSING",
        Duration.ofSeconds(30));
    if (!acquired) {
        // Another request is processing; tell client to retry
        return ResponseEntity.status(409)
            .header("Retry-After", "2").build();
    }

    try {
        PaymentResult result = stripeService.createCharge(
            req.getAmountCents(), req.getCustomerId(),
            req.getPaymentMethodId());

        // Store result for future duplicates (24h TTL)
        redis.set(resultKey,
            objectMapper.writeValueAsString(result),
            Duration.ofDays(1));
        return ResponseEntity.ok(result);
    } catch (Exception e) {
        redis.delete(lockKey); // allow retry on failure
        throw e;
    }
}
```

**Example 2 - Database-Level Idempotency**

```java
// Idempotent message consumer (Kafka at-least-once)
@KafkaListener(topics = "order.created")
void handleOrderCreated(OrderCreatedEvent event) {
    // message_id is unique per event (Kafka offset or event UUID)
    String messageId = event.getMessageId();

    try {
        // INSERT IGNORE = idempotent insert
        // If already processed: SQL silently skips, no exception
        int inserted = jdbcTemplate.update("""
            INSERT INTO processed_orders
                (message_id, order_id, processed_at)
            VALUES (?, ?, NOW())
            ON CONFLICT (message_id) DO NOTHING
            """, messageId, event.getOrderId());

        if (inserted == 0) {
            log.debug("Duplicate message ignored: {}", messageId);
            return; // already processed; idempotent skip
        }

        // Only execute business logic for first-time processing
        orderService.fulfillOrder(event.getOrderId());

    } catch (Exception e) {
        log.error("Failed to process order event: {}", messageId, e);
        throw e; // rethrow to trigger Kafka retry
    }
}
```

---

### ⚖️ Comparison Table

| HTTP Method | Idempotent? | Why | Safe Retry? |
|---|---|---|---|
| GET | Yes | Read-only, no state change | Yes |
| PUT | Yes | Sets resource to specified state | Yes |
| DELETE | Yes | Resource ends in "does not exist" | Yes |
| HEAD | Yes | Read-only | Yes |
| OPTIONS | Yes | Read-only | Yes |
| POST | No | Creates new resource each call | No (use idempotency-key) |
| PATCH | No (usually) | Incremental changes are not idempotent | Only if PATCH sets absolute state |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "DELETE is idempotent so a 404 on second call is a bug" | HTTP `DELETE` is idempotent in EFFECT: the resource does not exist after the operation, whether it existed before or not. The RESPONSE may differ: first DELETE returns 200 (deleted), second DELETE returns 404 (not found). Idempotency is about the STATE result, not the HTTP status code. A client should treat both 200 and 404 as "resource is gone" (successful idempotent outcome). |
| "`PUT` is always idempotent" | `PUT` is idempotent only if the request body specifies the COMPLETE resource state (set to this exact state). If `PUT` uses relative values (e.g., `{"increment_count": 1}`), it is NOT idempotent. Standard REST convention defines PUT as "replace the entire resource with this representation" - which is idempotent. But non-standard PUT implementations can be non-idempotent. |
| "Idempotency key is just a request ID for logging" | An idempotency key is a CLIENT-GENERATED key (UUID) that the server uses to DEDUPLICATE requests. It must be stored on the server with the result. On duplicate requests (same key), the server returns the stored result without re-executing the operation. It is NOT just a trace ID - it has semantic significance: same key = same logical request = return same result. The client MUST generate a new key for genuinely new requests. |
| "Retrying idempotent operations is always safe" | Retrying is safe from the OPERATION side. But retrying has costs: additional load on the server, potential rate limiting, and client-side complexity (timeout + retry logic). Retries with exponential backoff and jitter are needed to avoid thundering herd (all clients retrying simultaneously). Idempotency makes retries SAFE; backoff makes retries SMART. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Duplicate Charges from Missing Idempotency**

**Symptom:** Payment service logs show two `StripeService.charge()`
calls with identical parameters within seconds of each other.
Customer support receives duplicate charge complaints.

**Root Cause:** Mobile client retried a payment after a
network timeout. The first request completed but the response
was not received. No idempotency key was used. The server
processed both requests as new charges.

**Diagnosis:** Grep payment logs for duplicate `customerId`
+ `amount` + `paymentMethodId` within a 30-second window.

**Fix:** Implement idempotency keys on the POST /payments
endpoint. Client: generate UUID per payment attempt, include
in `Idempotency-Key` header. Server: check + store result
by key before charging.

**Failure Mode 2: Saga Duplicate Step Execution**

**Symptom:** Inventory is decremented twice for the same
order. Database shows `inventory_transactions` table has
two rows for the same `order_id` + `product_id`.

**Root Cause:** A saga step failed after the inventory
decrement succeeded but before the saga coordinator acknowledged
completion. On retry, the coordinator re-executed the
inventory step.

**Fix:** Include `order_id` as a unique key on `inventory_transactions`.
Use `INSERT ... ON CONFLICT (order_id, product_id) DO NOTHING`
for the inventory decrement. The step is now idempotent:
retry does nothing if the record already exists.

---

**Security Note:**

Idempotency keys must be validated to prevent abuse. Security
considerations:
1. Key must be tied to the authenticated user: `Idempotency-Key`
   alone should not allow one user to retrieve another user's
   result. Store as `(user_id, idempotency_key) -> result`.
   Do NOT store as `idempotency_key -> result` (a user could
   guess another user's key and retrieve their payment result).
2. Key format validation: validate the key is a valid UUID
   to prevent injection attacks on the cache/store key.
3. TTL: idempotency results must have an expiry. Keep for
   the retry window (24h is standard for payments). Do NOT
   store indefinitely (key space grows unbounded; old keys
   may become collisions for new requests after a long period).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `OOP` (CSF-013) - service design context
- `Pure Functions` (CSF-038) - pure functions are inherently
  idempotent; understanding the distinction helps

**Builds On This (learn these next):**
- `REST API Design` (API-015) - idempotent HTTP methods
  and REST conventions
- `Distributed Systems Patterns` (DST-021) - idempotency
  at distributed scale (sagas, at-least-once)
- `Messaging Delivery Guarantees` (MSG-008) - at-least-once
  delivery and idempotent consumers

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ DEFINITION   │ f(f(x)) = f(x). Same result, N applies │
├──────────────┼─────────────────────────────────────────┤
│ HTTP         │ GET/PUT/DELETE/HEAD = idempotent         │
│              │ POST/PATCH = NOT idempotent              │
├──────────────┼─────────────────────────────────────────┤
│ IDEM KEY     │ Client UUID per request                  │
│              │ Server: store result, return on dup      │
│              │ Redis: SET key result NX EX 86400        │
├──────────────┼─────────────────────────────────────────┤
│ DB PATTERN   │ INSERT ... ON CONFLICT (unique_col)      │
│              │ DO NOTHING (idempotent insert)           │
├──────────────┼─────────────────────────────────────────┤
│ RETRY SAFE   │ At-least-once + idempotent = safe        │
│              │ Effectively exactly-once semantics        │
├──────────────┼─────────────────────────────────────────┤
│ SAGA         │ Each step must be idempotent             │
│              │ Compensating steps must also be idem.    │
├──────────────┼─────────────────────────────────────────┤
│ SECURITY     │ Tie key to user_id (not key alone)       │
│              │ Set TTL on stored results                │
├──────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE │ API-015 (REST), DST-021, MSG-008         │
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Idempotent = same result regardless of how many times applied.
   Critical for distributed systems because network failures
   require retries, and retries must be safe (no duplicate
   side effects). HTTP GET/PUT/DELETE are idempotent by convention.
   POST is not. Stripe's idempotency-key pattern adds idempotency
   to POST requests via client-generated UUIDs + server-side
   result caching.
2. Implementation: for database writes, use `INSERT ... ON CONFLICT
   DO NOTHING` (unique constraint on the business ID ensures
   duplicate inserts are silently ignored). For API endpoints,
   store the result keyed by the idempotency key; on duplicate
   requests (same key), return the stored result. For concurrent
   duplicate requests, use atomic set-if-absent (Redis `SET NX`)
   to prevent race conditions.
3. "At-least-once delivery + idempotent consumer = effectively
   exactly-once semantics." This is the distributed systems
   pattern: Kafka, SQS, and most message queues guarantee
   at-least-once. Idempotent consumers (deduplication via
   message ID + unique constraint or idempotency key store)
   make at-least-once safe. This is cheaper and more reliable
   than trying to achieve true exactly-once delivery in a
   distributed system.

**Interview one-liner:**
"Idempotent: applying an operation N times has the same
effect as applying it once. Critical for retry safety in
distributed systems. HTTP GET/PUT/DELETE are idempotent;
POST is not. Implementation: client-generated idempotency
keys + server-side result caching (Redis) for API endpoints;
`INSERT ... ON CONFLICT DO NOTHING` for database consumers.
At-least-once delivery + idempotent handler = effectively
exactly-once semantics."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Idempotency is the bridge between "at-least-once" (reliable)
and "exactly-once" (safe). In any distributed system where
operations must be reliable (retries needed) and correct
(no duplicate effects), idempotency is the required property.
The implementation always involves: a unique key (business ID,
message ID, or client-generated UUID), a storage mechanism
(database unique constraint, Redis key), and a check-before-act
pattern (with atomic set-if-absent for concurrent requests).
This pattern recurs in: payment APIs, message consumers,
saga steps, webhook handlers, scheduled jobs, and any
network-facing operation that must be retry-safe.

**Where else this pattern appears:**

- **Kubernetes controllers (reconciliation loop)** - Kubernetes
  controllers implement the "reconciliation loop": compare
  desired state (spec) with actual state, apply changes to
  reconcile. The reconcile function MUST be idempotent: if
  called multiple times (Kubernetes calls it repeatedly),
  the result must be the same (the actual state converges
  to desired state). Creating a Pod that already exists:
  `ON CONFLICT DO NOTHING` equivalent. Deleting a resource
  that's already gone: no error. This is why Kubernetes
  operators are robust to crashes and network partitions:
  idempotent reconciliation + retry = eventual consistency.
- **Terraform apply (infrastructure as code)** - Terraform's
  `apply` is idempotent: running `terraform apply` when
  the infrastructure is already in the desired state = no
  changes. Each resource has a unique identifier; Terraform
  checks if the resource exists before creating it.
  "Plan" shows the diff. "Apply" performs the minimal changes
  needed to reach desired state. Idempotency enables safe
  re-runs: CI/CD pipelines can run `terraform apply` on
  every deployment without fear of creating duplicate
  infrastructure.
- **Email/notification deduplication** - Sending a confirmation
  email: if the operation fails after the email is sent
  (before the database record is updated), retry sends
  a duplicate email. Fix: store a "confirmation_email_sent"
  flag per order; check before sending; `UPDATE orders SET
  email_sent = true WHERE id = ? AND email_sent = false`
  (atomic conditional update; affected rows 0 = already sent).
  The update is idempotent; the email send only happens
  once. This is why transactional outbox pattern (store
  intent to send in the same transaction as the business
  operation) is preferred over direct send.

---

### 💡 The Surprising Truth

Stripe's public API documentation for idempotency keys
states: "Stripe's idempotency works by saving the resulting
status code and body of the first request made for any
given idempotency key, regardless of whether it succeeded
or failed. Subsequent requests with the same key return
the same result." The critical word: "regardless of whether
it SUCCEEDED or FAILED." If the first request FAILS (e.g.,
the card is declined with a 402 Payment Required), the
FAILURE RESULT is stored as the idempotent response. A
retry with the same idempotency key returns the SAME 402
decline - it does NOT retry the charge. This is correct:
the client must generate a NEW idempotency key to attempt
the charge again after a card decline. Many developers
who implement idempotency only store successful results
(and retry on failures). This creates a subtle bug: if
the first request returns a timeout (from Stripe's perspective,
the charge was declined internally, but the client never
received the response), the client retries with the same
key, expects a new attempt, but receives the old decline.
True idempotency stores ALL results (success and failure).
The client must inspect the result to determine whether
to generate a new key (logical failure: card declined)
vs retry with the same key (network failure: response not received).

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[IDENTIFY]** Review an HTTP API and classify each endpoint
   as idempotent or not. For non-idempotent endpoints,
   propose an idempotency key mechanism.

2. **[IMPLEMENT]** Write a Spring Boot `POST /orders` endpoint
   that accepts an `Idempotency-Key` header. Use Redis to
   store results and return stored results for duplicate
   keys. Handle concurrent duplicate requests without race conditions.

3. **[DATABASE]** Write a Kafka consumer that persists order
   events to a database. Make it idempotent using
   `INSERT ... ON CONFLICT DO NOTHING` with a `message_id`
   unique constraint. Handle the case where the conflict
   is detected and log it appropriately.

4. **[DESIGN]** Design a saga for a hotel booking system with
   steps: (1) charge card, (2) reserve room, (3) send confirmation
   email. Make each step idempotent. Define the compensating
   transactions (rollback) and make those idempotent too.

5. **[EXPLAIN]** Explain why "at-least-once + idempotent consumer
   = effectively exactly-once." Give a concrete example of
   how a duplicate Kafka message is handled safely by an
   idempotent consumer.

---

### 🧠 Think About This Before We Continue

**Q1.** Stripe stores idempotency results including failures.
A payment fails (card declined). Client retries with the
same idempotency key. What does the client receive?
What should the client do next?

*Hint: The client receives the same 402 Card Declined response
as the first attempt (the stored result). The idempotency
key "locked in" the failure result. Stripe will not retry
the charge with the same key.
What should the client do:
(1) If the client wants to retry the charge (maybe with a
different card or after the user updates payment method):
generate a NEW idempotency key (UUID). The new key starts
fresh: the charge will be attempted again.
(2) If the client suspects the first response was a network
error (not a true card decline): the client should look at
the error code in the 402 response. A real decline has
a specific Stripe error code (card_declined). A network
timeout the client experienced would result in no response
at all, and the retry with the same key would show the
actual Stripe result. The same-key retry tells the client:
"this is what Stripe actually decided the first time."
Key insight: generate a new UUID only for a new logical
payment attempt. Keep the same UUID for network-failure retries.*

**Q2.** HTTP `PATCH` is technically not idempotent. But a
`PATCH` that SETS an absolute value (not increments) IS
idempotent in practice. Design a `PATCH /users/{id}`
endpoint that is idempotent for setting the email address,
but NOT idempotent for incrementing login count. Show the
request body for each case.

*Hint:
Idempotent PATCH (set absolute value):
```json
PATCH /users/123
{"email": "alice@example.com"}
```
Sending this 10 times: user 123 always has email alice@example.com.
Idempotent because the body specifies a state, not a delta.

Non-idempotent PATCH (increment/delta):
```json
PATCH /users/123
{"increment_login_count": 1}
```
Sending this 10 times: login_count increases by 10.
Not idempotent because the body specifies a relative change.

The REST spec says PATCH is NOT guaranteed idempotent because
the spec allows both forms. If your PATCH only accepts absolute
state (not deltas), you can document it as idempotent and
treat it like PUT for retry purposes. The Stripe API convention:
use PUT for full replacement (idempotent), PATCH for partial
update (client should use an idempotency key for non-idempotent
partial updates).*

---

### 🎯 Interview Deep-Dive

**Q1: "Why is POST not idempotent? How do you make a POST endpoint retry-safe?"**

*Why they ask:* Tests REST + distributed systems knowledge.
Common question at fintech and e-commerce companies.

*Strong answer includes:*
- POST is not idempotent: each POST creates a new resource.
  `POST /payments` twice creates two charges. This is correct
  HTTP semantics (POST = "process this, creating something new").
- Idempotency-key pattern: the client generates a UUID for
  each logical operation. Sends it as `Idempotency-Key: <uuid>`
  header. Server: check if key exists in store. If yes, return
  stored result. If no, process, store result, return result.
  Duplicate requests return identical results without re-processing.
- Redis implementation: `SET idem:<key> <result> NX EX 86400`.
  `NX` = set only if not exists (atomic check-and-set).
  Prevents race condition where two concurrent duplicate requests
  both process.

**Q2: "Explain how a Kafka consumer can be made idempotent."**

*Why they ask:* Tests messaging and distributed system design knowledge.

*Strong answer includes:*
- Kafka guarantees at-least-once delivery (may deliver same
  message twice on consumer crash/rebalance).
- Problem: duplicate processing = duplicate side effects
  (double inventory update, double email).
- Solution: unique constraint on the business key in the
  database. `INSERT INTO orders (message_id, ...) VALUES (...)
  ON CONFLICT (message_id) DO NOTHING`.
- If the operation is more complex: check if `message_id`
  already exists before executing business logic. Skip if found.
- At-least-once + idempotent consumer = effectively exactly-once.
- Alternative: Kafka's transactional API (exactly-once)
  - higher overhead, Kafka-internal consumers only.

**Q3: "What is the difference between idempotency and safety in HTTP?"**

*Why they ask:* Tests precise HTTP protocol knowledge.

*Strong answer includes:*
- Safe method: has NO side effects on the server. Read-only.
  `GET`, `HEAD`, `OPTIONS` are safe. A safe method may be
  called freely by caches, proxies, link prefetchers.
- Idempotent method: calling it multiple times produces the
  same SERVER STATE as calling it once. May have side effects,
  but repeating produces the same result. `PUT`, `DELETE`
  are idempotent but NOT safe (they DO have side effects -
  updating or deleting resources).
- All safe methods are idempotent (read-only = no state change = idempotent).
  Not all idempotent methods are safe (DELETE is idempotent
  but has a side effect: deleting the resource).
- `POST`: NOT safe (has side effects), NOT idempotent (each
  call creates new resource).
