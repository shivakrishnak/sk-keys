---
layout: default
title: "Idempotency (Distributed)"
parent: "Distributed Systems"
nav_order: 605
permalink: /distributed-systems/idempotency/
number: "605"
category: Distributed Systems
difficulty: ★★★
depends_on: "Retry with Backoff, Two-Phase Commit"
used_by: "Payment APIs, Stripe, AWS APIs, Message Queues"
tags: #advanced, #distributed, #safety, #retry, #exactly-once
---

# 605 — Idempotency (Distributed)

`#advanced` `#distributed` `#safety` `#retry` `#exactly-once`

⚡ TL;DR — **Idempotency** in distributed systems means an operation can be safely retried any number of times with the same result as a single execution — enabled by idempotency keys, deduplication state, and atomic conditional writes at the server side.

| #605 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Retry with Backoff, Two-Phase Commit | |
| **Used by:** | Payment APIs, Stripe, AWS APIs, Message Queues | |

---

### 📘 Textbook Definition

**Idempotency** (mathematics: f(f(x)) = f(x)) in distributed systems means applying an operation multiple times produces the same result as applying it once. Critical for retry safety: if a network failure occurs after server processes a request but before client receives the response, the client must be able to retry safely without side effects. **Idempotency key**: a client-generated unique identifier (UUID) attached to each logical operation; the server deduplicates on this key, storing the operation result and returning the cached result on repeated requests. **Exactly-once semantics**: achieved at-most-once (no deduplication) + at-least-once (retry) + idempotency key dedup → at-most-one execution per key. **At-least-once delivery** (message queues): consumers must handle duplicate messages. Kafka: consumer at-least-once; producer exactly-once (Kafka transactions). **Database patterns**: INSERT ... ON CONFLICT DO NOTHING (PostgreSQL); conditional writes (DynamoDB: ConditionExpression attribute_not_exists(id)); versioned optimistic locking. **Stripe**: every mutating API call accepts Idempotency-Key header; stores result for 24 hours. **AWS SQS**: standard queues at-least-once; FIFO queues with message group ID = exactly-once within group. HTTP methods: GET, HEAD, PUT, DELETE are inherently idempotent by specification; POST is not (but can be made idempotent via idempotency keys).

---

### 🟢 Simple Definition (Easy)

Idempotent: doing it twice is the same as doing it once. Elevator button: pressing "5" twice doesn't send you to floor 10. Payment without idempotency: charging a customer twice for the same order. Payment WITH idempotency: "charge for order ABC-123" → server checks "have I already charged for ABC-123?" → if yes: return "already done, here's the result" → if no: charge, store result, return. Now you can safely retry a failed payment request without double-charging.

---

### 🔵 Simple Definition (Elaborated)

Why distributed systems specifically need idempotency: in a distributed system, success doesn't mean the client received the success response. A server can process your request, commit the transaction, and then the network drops before sending the response back. Client: sees timeout → assumes failure → retries. Server: processes request again → double payment. The fix: client sends a unique idempotency key with every request. Server: checks if key was seen before. If yes: return stored result. If no: process and store result. Now timeout → retry is safe.

---

### 🔩 First Principles Explanation

**Idempotency key patterns, server-side deduplication, and message queue exactly-once:**

```
THE DISTRIBUTED IDEMPOTENCY PROBLEM:

  Client sends: POST /payments { amount: 100, card: "4111..." }
  
  Timeline:
    T=0:   Client sends request.
    T=50ms: Server receives request.
    T=55ms: Server processes payment (Stripe API call: card charged).
    T=60ms: Server commits to DB: "payment_id=X, status=completed."
    T=65ms: Server sends HTTP 200 response.
    T=65ms: NETWORK DROPS. Response lost.
    T=5000ms: Client: read timeout. Assumes request failed.
    T=5001ms: Client retries: POST /payments { amount: 100, card: "4111..." }.
    T=5060ms: Server: no idempotency check → processes AGAIN → charges card TWICE.
    T=5065ms: Server: HTTP 200.
    T=5065ms: Customer: charged $100 twice for one order. Fraud complaint.
    
  RESULT WITHOUT IDEMPOTENCY: client-side retry → server-side double execution.

IDEMPOTENCY KEY SOLUTION:

  Client: generates UUID once per logical operation.
    idempotencyKey = UUID.randomUUID() = "a1b2c3d4-e5f6-..."
    Stores key locally for this operation (in memory or persistent if needed).
    
  Client sends: POST /payments
    Headers: Idempotency-Key: a1b2c3d4-e5f6-...
    Body: { amount: 100, card: "4111..." }
    
  Server (first request):
    1. Check DB: "SELECT * FROM idempotency_keys WHERE key = 'a1b2c3d4-...' ".
       Not found. Proceed.
    2. Process payment: charge card. Payment ID = X. Result = { success: true, paymentId: X }.
    3. ATOMICALLY: begin transaction.
       a. Commit payment to payments table.
       b. INSERT INTO idempotency_keys (key, result, expires_at) 
          VALUES ('a1b2c3d4-...', '{"success":true,"paymentId":"X"}', NOW() + INTERVAL '24h').
       Commit transaction.
    4. Return: 200 OK { success: true, paymentId: X }.
    
  Network drops. Client retries.
  
  Server (retry request):
    1. Check DB: "SELECT * FROM idempotency_keys WHERE key = 'a1b2c3d4-...' ".
       FOUND. result = { success: true, paymentId: X }.
    2. Return cached result: 200 OK { success: true, paymentId: X }.
    3. Payment NOT re-processed.
    
  Client: receives success response. Proceeds as if first attempt succeeded.
  Customer: charged exactly once.
  
ATOMICITY REQUIREMENT (CRITICAL):

  Server must atomically commit both the operation AND the idempotency key record.
  
  WRONG (non-atomic):
    1. Process payment (charge card). ← Card charged.
    2. Commit payment to DB. ← DB updated.
    3. Server crashes here. ←←←← 
    4. INSERT idempotency key. ← NEVER HAPPENS.
    
    Retry: idempotency key not in DB → server processes again → double charge.
    
  CORRECT (atomic):
    BEGIN TRANSACTION:
      1. Check idempotency key: not found.
      2. INSERT idempotency key (pending).
      3. Process payment (call Stripe API — outside transaction! See note below).
      4. UPDATE idempotency key: status=completed, result=...
    COMMIT.
    
  NOTE: External API calls (Stripe, bank) cannot be part of a DB transaction.
        Pattern: two-step atomic write:
        Step 1 (before external call): INSERT idempotency_key WHERE NOT EXISTS (atomic).
                If INSERT fails (key exists): return cached result.
                If INSERT succeeds: proceed to external call.
        Step 2 (after external call): UPDATE idempotency_key with result.
        
        Edge case: server crashes between step 1 and step 2.
          Retry: step 1 → INSERT fails (key in pending state).
          Server: idempotency key found but status=pending.
          Decision: 
            Option A: return 409 Conflict ("request in progress, wait and retry").
            Option B: check if external operation completed (query Stripe for idempotency key).
            
        Stripe solves this: Stripe itself is idempotent (each Stripe request has idempotency key).
        Step 3: query Stripe with same idempotency key → Stripe returns original result.
        Server: completes step 2 with Stripe result. Returns to client.

DATABASE-LEVEL IDEMPOTENCY:

  INSERT ... ON CONFLICT DO NOTHING (PostgreSQL):
    -- Idempotent: create event record.
    INSERT INTO events (id, type, payload, created_at)
    VALUES (:id, :type, :payload, NOW())
    ON CONFLICT (id) DO NOTHING;
    -- If record already exists (same id): silent no-op. No error. Returns 0 rows affected.
    -- Caller: check rows_affected. 0 = duplicate (already processed).
    
  DynamoDB conditional write:
    PutItemRequest.builder()
      .tableName("orders")
      .item(item)
      .conditionExpression("attribute_not_exists(orderId)")  // Only create if not exists.
      .build();
    // If orderId already exists: throws ConditionalCheckFailedException.
    // Caller: catch ConditionalCheckFailed → idempotent (already processed, safe to ignore).
    
  Optimistic locking (version-based):
    UPDATE orders SET status='processing', version=version+1
    WHERE order_id=:id AND version=:expected_version;
    -- Only succeeds if version matches. Prevents duplicate updates.
    -- On retry: version already incremented by first success → UPDATE returns 0 rows.

MESSAGE QUEUE IDEMPOTENCY:

  At-least-once delivery: message may be delivered multiple times.
  Consumer MUST be idempotent.
  
  Consumer idempotency patterns:
  
  1. Message ID deduplication:
     -- Consumer: check if message already processed.
     IF NOT EXISTS (SELECT 1 FROM processed_messages WHERE message_id = :msg_id):
         process message
         INSERT INTO processed_messages (message_id, processed_at) VALUES (:msg_id, NOW())
     -- DB constraint: UNIQUE (message_id).
     -- Duplicate message: INSERT fails → harmless duplicate message ignored.
     
  2. Kafka idempotent producer:
     properties.put("enable.idempotence", "true");
     // Producer: assigns sequence numbers to each message per partition.
     // Broker: tracks sequence numbers. Duplicate message (same sequence): silently discarded.
     // At-most-once: combined with acks=all → exactly-once at producer level.
     
  3. Kafka transactions (exactly-once end-to-end):
     // Producer: atomic: consume from topic A + produce to topic B.
     // If consumer commits offset and producer commits atomically: no duplicates.
     properties.put("transactional.id", "my-transactional-id");
     producer.initTransactions();
     producer.beginTransaction();
     producer.send(new ProducerRecord<>("output-topic", ...));
     consumer.commitSync(offsets, consumerGroupMetadata);
     producer.commitTransaction();
     // If crash mid-transaction: transaction rolled back. Message not in output-topic.
     // Exactly-once: consumer exactly once + producer exactly once.

STRIPE IDEMPOTENCY KEY BEHAVIOR:

  Stripe API:
    POST /v1/charges
    Idempotency-Key: <your-uuid>
    
    First request: processes charge. Stores result for 24 hours.
    Same key, same params: returns stored result. No re-processing.
    Same key, DIFFERENT params: 400 Bad Request. (Key reuse with different request = error.)
    
    Key expiry: 24 hours. After 24h: same key treated as new request.
    
  Best practice: derive key deterministically:
    idempotencyKey = "charge-" + orderId + "-" + orderVersion;
    // Always the same key for the same logical operation.
    // Survives client restarts (UUID in memory wouldn't).
    
  Store key in request table:
    payment_requests(order_id, idempotency_key, status, payment_id, created_at)
    -- Before sending to Stripe: INSERT or SELECT payment_requests.
    -- On success: UPDATE payment_requests SET status='completed', payment_id=...
    -- On retry: SELECT payment_requests → already 'completed' → return stored payment_id.

HTTP IDEMPOTENCY BY METHOD:

  GET: idempotent. Multiple GETs: same result.
  HEAD: idempotent.
  PUT: idempotent by spec. PUT /users/123 { name: "Alice" } twice: same result.
  DELETE: idempotent by spec. DELETE /users/123 twice: user deleted on first; second = 404 (or 200 for cached result). Functionally idempotent (user is deleted either way).
  PATCH: NOT idempotent. PATCH "increment counter by 1" twice: increments twice.
  POST: NOT idempotent by spec. Use idempotency keys for POST mutations.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT idempotency:
- Client retry on timeout: double payment, duplicate email, double inventory decrement
- Message redelivery: consumer processes same event twice → duplicate records
- Network timeouts: can't distinguish "not received" from "failed" → unsafe to retry

WITH idempotency:
→ Safe retries: client can always retry on timeout without fear of double-execution
→ Exactly-once semantics: at-least-once delivery + idempotent consumer = exactly-once effect
→ System reliability: retries become a first-class recovery mechanism, not a danger

---

### 🧠 Mental Model / Analogy

> A stamped form for a government office. The clerk stamps the form with a unique serial number when first processed. If you come back the next day with the same form ("I never received confirmation"): clerk sees the stamp, looks up the result, hands you the copy. No re-processing. Without the stamp: clerk processes the form again → you receive two benefits, wrong records, duplicate payments.

"Unique serial stamp" = idempotency key
"Clerk looking up the stamp" = server checking idempotency key table
"Handing you the copy of original result" = returning cached response without reprocessing

---

### ⚙️ How It Works (Mechanism)

```
SERVER-SIDE IDEMPOTENCY HANDLER:

  On request received:
    1. Extract Idempotency-Key header.
    2. Atomically try to INSERT pending record:
       INSERT INTO idempotency (key, status) VALUES (?, 'pending')
       ON CONFLICT (key) DO UPDATE SET last_checked = NOW()
       RETURNING status, result.
    3a. If INSERT succeeded (new key): process operation → store result → return result.
    3b. If INSERT conflicted (existing key):
        - If status='completed': return stored result.
        - If status='pending': return 409 (operation in progress).
```

---

### 🔄 How It Connects (Mini-Map)

```
Retry with Backoff (re-attempts failed calls — unsafe without idempotency)
        │
        ▼
Idempotency (Distributed) ◄──── (you are here)
(deduplication key: same operation → same result regardless of retry count)
        │
        ├── Outbox Pattern: stores events with idempotency guarantees
        ├── Saga Pattern: compensating transactions rely on idempotent steps
        └── Message Queues: at-least-once + idempotent consumer = exactly-once effect
```

---

### 💻 Code Example

**Server-side idempotency with PostgreSQL:**

```java
@RestController
public class PaymentController {
    
    @PostMapping("/payments")
    public ResponseEntity<PaymentResult> createPayment(
            @RequestHeader("Idempotency-Key") String idempotencyKey,
            @RequestBody PaymentRequest request) {
        
        // Step 1: Atomic check-and-insert (prevents race condition on concurrent retries).
        Optional<IdempotencyRecord> existing = idempotencyRepo.findByKey(idempotencyKey);
        
        if (existing.isPresent()) {
            IdempotencyRecord record = existing.get();
            if ("completed".equals(record.getStatus())) {
                // Already processed: return cached result.
                return ResponseEntity.ok(record.getResultAs(PaymentResult.class));
            }
            if ("pending".equals(record.getStatus())) {
                // Still processing (concurrent request): ask client to wait and retry.
                return ResponseEntity.status(409).build();
            }
        }
        
        // Step 2: Reserve the key (atomic insert).
        try {
            idempotencyRepo.insertPending(idempotencyKey, request);
        } catch (DuplicateKeyException e) {
            // Race condition: another thread just inserted. Re-fetch.
            return createPayment(idempotencyKey, request); // Recursive retry to get result.
        }
        
        // Step 3: Execute the operation.
        PaymentResult result;
        try {
            result = stripeService.charge(
                request.getAmount(),
                request.getCardToken(),
                idempotencyKey  // Also pass to Stripe: they deduplicate too.
            );
        } catch (Exception e) {
            idempotencyRepo.markFailed(idempotencyKey, e.getMessage());
            throw e;
        }
        
        // Step 4: Atomically mark complete and store result.
        idempotencyRepo.markCompleted(idempotencyKey, result);
        
        return ResponseEntity.ok(result);
    }
}

// SQL: idempotency table:
// CREATE TABLE idempotency (
//     key         VARCHAR(255) PRIMARY KEY,
//     status      VARCHAR(20) NOT NULL DEFAULT 'pending',
//     request     JSONB,
//     result      JSONB,
//     created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
//     expires_at  TIMESTAMP NOT NULL DEFAULT NOW() + INTERVAL '24 hours'
// );
// CREATE INDEX ON idempotency (expires_at); -- For cleanup job.
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| PUT and DELETE are automatically idempotent in practice | PUT and DELETE are idempotent by HTTP SPECIFICATION, but implementations can violate this. A poorly implemented DELETE that returns 404 on second call may trigger error handling in clients that breaks the idempotency contract. More critically: DELETE implemented as "soft delete with audit log" inserts a new audit record on each call — functionally idempotent (user deleted) but with side effects. Design matters |
| UUID idempotency keys must be random | Idempotency keys should be DETERMINISTIC (derived from the operation's logical identity), not random. Random UUID in memory: if client crashes and restarts: generates new UUID → no deduplication on retry → potential duplicate. Deterministic: idempotencyKey = hash("payment:" + orderId + ":" + attemptVersion). Same operation after restart: same key → server deduplicates. Store the key persistently with the order if it will survive client restarts |
| Idempotency is only needed for payment operations | Any operation with side effects that may be retried needs idempotency: creating database records, sending emails, pushing events to queues, incrementing counters, creating infrastructure (Terraform idempotent by design), updating inventory. Especially critical for: message consumers (at-least-once delivery), webhook handlers (third-party systems retry webhooks), any API with timeout-based retry |
| Idempotency keys can be short-lived (seconds) | Idempotency key TTL depends on the client's retry window. If a client retries for up to 1 hour (long timeout + many retries + circuit breaker recovery): key must live for at least 1 hour. If an async process may retry a day later: key must live for 1 day. Stripe stores keys for 24 hours. Set TTL = max(client_timeout_window, async_retry_window) + buffer |

---

### 🔥 Pitfalls in Production

**Idempotency key not stored persistently — client restart causes double execution:**

```
SCENARIO: E-commerce checkout. Client (mobile app) generates idempotency key as UUID in memory.
  User: initiates checkout. App: generates key=abc-123 (in memory).
  App sends POST /payments with key=abc-123.
  Server: processes payment. Commits. Response: network timeout.
  App: crashes (OOM, user force-quit, background kill by OS).
  App restarts. User: "My order didn't go through, let me try again."
  App: generatess new key: xyz-789 (NEW random UUID — old one lost in memory).
  App sends POST /payments with key=xyz-789.
  Server: new key → processes AGAIN → charges card TWICE.
  
BAD: Random UUID in memory as idempotency key:
  String idempotencyKey = UUID.randomUUID().toString(); // Lost on app crash.

FIX: Derive idempotency key from durable, persistent operation identity:
  // Cart/order has a stable ID (persisted locally or on server):
  String cartId = orderRepository.getCartId(); // Stable, persisted before payment attempt.
  String attemptVersion = "1"; // Increment only on explicit user retry (not system retry).
  String idempotencyKey = "pay-" + cartId + "-v" + attemptVersion;
  
  // This key is:
  //   - Deterministic: same cart → same key (survives app restarts)
  //   - Unique per logical operation: different carts → different keys
  //   - User-controlled versioning: increment "attemptVersion" only when user explicitly
  //     tries a different payment method ("try different card" → new attempt version → new key)
  
FIX 2: Server-side idempotency key storage on order creation:
  // When order is created: generate and store idempotency key SERVER-SIDE on the order.
  // Client: GET /orders/{id}/payment-key → returns stored idempotency key.
  // Always use this key for payment for this order. Stored in DB → survives restarts.
  // User changes payment method: POST /orders/{id}/new-payment-attempt → server generates new key.
```

---

### 🔗 Related Keywords

- `Retry with Backoff` — idempotency is the prerequisite: retries safe only on idempotent operations
- `Outbox Pattern` — uses message IDs as idempotency keys for exactly-once event delivery
- `Saga Pattern` — each saga step must be idempotent (saga orchestrator may replay steps)
- `Exactly-Once Semantics` — at-least-once delivery + idempotent processing = exactly-once effect

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Client sends unique key with request.    │
│              │ Server deduplicates: same key → cached   │
│              │ result returned, no re-execution.        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any mutation that may be retried: payment│
│              │ APIs, message consumers, webhook handlers│
│              │ infrastructure provisioning              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Read-only operations (GET) are inherently│
│              │ idempotent — no idempotency key needed   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Government stamp: same form, same       │
│              │  serial number = just give me the copy." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Retry with Backoff → Outbox Pattern →   │
│              │ Saga Pattern → Exactly-Once Semantics    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An e-commerce platform uses Kafka for order events. The consumer reads an "OrderPlaced" event, sends a confirmation email, and commits the Kafka offset. The consumer crashes AFTER sending the email but BEFORE committing the offset. On restart: Kafka re-delivers the "OrderPlaced" event. The consumer sends the email AGAIN. How do you design the consumer to be idempotent so the customer receives exactly one confirmation email? What exactly does the consumer need to store, and where?

**Q2.** You implement an idempotency key table in PostgreSQL. At scale: 10,000 unique operations per second × 24-hour TTL = 864,000,000 rows. Describe the cleanup strategy, index design, and partitioning approach needed to make this idempotency table performant. What is the trade-off between TTL duration (reliability for long retries) and table size (performance)?
