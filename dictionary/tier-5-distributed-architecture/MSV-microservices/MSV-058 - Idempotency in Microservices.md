---
id: MSV-058
title: Idempotency in Microservices
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-048, MSV-054, MSV-057
used_by: MSV-054, MSV-057, MSV-046
related: MSV-054, MSV-057, MSV-046, MSV-049, MSV-055, MSV-063
tags:
  - microservices
  - reliability
  - deep-dive
  - patterns
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 58
permalink: /microservices/idempotency-in-microservices/
---

# MSV-058 - Idempotency in Microservices

⚡ TL;DR - Idempotency: performing an operation
N times produces the same result as performing
it once. Critical in microservices because: networks
retry failed requests (client can't tell if the
first attempt succeeded); Kafka delivers messages
at-least-once (consumers may receive duplicates);
Saga compensations are retried until successful.
Implementation: idempotency key (client-provided
UUID stored with the result) or natural idempotency
(PUT with full state, not POST with partial). At-
least-once + idempotent consumer = effectively
exactly-once behavior.

| #058 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Event-Driven Microservices, Outbox Pattern, Compensating Transaction | |
| **Used by:** | Outbox Pattern, Compensating Transaction, Saga Pattern | |
| **Related:** | Outbox Pattern, Compensating Transaction, Saga Pattern, Eventual Consistency in Microservices, Change Data Capture, Cross-Cutting Concerns | |

---

### 🔥 The Problem This Solves

**DUPLICATE PROCESSING IN DISTRIBUTED SYSTEMS:**
Client sends `POST /orders` (create order). Network
times out after 5 seconds. Client retries. First
request: DID it reach the server? Maybe. Maybe
not. Without idempotency: second request creates
a SECOND order -> customer has two orders, two
charges. Kafka consumer: processes `OrderCreated`
event, sends confirmation email. Consumer crashes
before committing offset. Kafka: redelivers the
event. Consumer: sends a SECOND confirmation email.
Idempotency prevents both problems.

---

### 📘 Textbook Definition

**Idempotency** (mathematics: Henri Poincare, 1901;
HTTP: Fielding, 2000) in distributed systems means:
an operation that produces the same result
regardless of how many times it is executed with
the same input. In HTTP: GET, PUT, DELETE are
idempotent (RFC 7231); POST is NOT idempotent by
default. In microservices: operations must be
designed to be idempotent because: (1) Kafka delivers
at-least-once (duplicates on consumer restart);
(2) HTTP clients retry on timeout (duplicate requests);
(3) Saga compensations retry until successful;
(4) Message relay (Outbox) retries on broker failure.
**Idempotency Key**: a client-provided unique ID
(UUID) stored with the operation's result. On
duplicate request: server returns the stored result
without re-executing. Enables safe retry everywhere.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Idempotency: calling an operation multiple times
with the same input = same result as calling once.
Safe to retry; no duplicate side effects.

**One analogy:**
> The elevator call button. Press once: elevator
called. Press again and again: elevator still called
once; no effect from additional presses. The button
is idempotent. Compare: an ATM "withdraw $100"
button that is NOT idempotent: press it 3 times
= $300 withdrawn. For ATM: you want idempotency
(duplicate network requests should not cause
duplicate withdrawals). An idempotent ATM:
remembers the transaction ID; duplicate request
for same transaction = show same result, no new
withdrawal.

**One insight:**
Idempotency is what transforms "at-least-once"
delivery into "effectively exactly-once" behavior.
Kafka guarantees at-least-once: an event will be
delivered, possibly multiple times. If the consumer
is idempotent: duplicate delivery has no extra
effect. The result: the business operation happens
exactly once, even if the event was delivered
twice. This is the fundamental pattern that makes
Kafka-based microservices reliable.

---

### 🔩 First Principles Explanation

**IDEMPOTENCY IMPLEMENTATION PATTERNS:**

```
PATTERN 1: IDEMPOTENCY KEY (for HTTP APIs)
  Client: generates UUID per request
  Sends: POST /orders with Idempotency-Key: uuid-123
  Server: 
    - Check: processed_requests table for uuid-123
    - If found: return cached response (no re-execute)
    - If not found: process, store result + uuid-123
    - Return: result
  
  First request:  uuid-123 not found -> process -> store
  Retry (same): uuid-123 found -> return cached
  Different op: uuid-456 not found -> process new
  
  Storage: processed_requests (key, response, expires_at)
  TTL: 24 hours (enough for client retry window)
  Thread safety: DB unique constraint on key prevents
                 concurrent duplicate processing

PATTERN 2: NATURAL IDEMPOTENCY (PUT semantics)
  PUT /orders/{id}/status with body: {status: CONFIRMED}
  Idempotent: set status to CONFIRMED regardless of
  current state. N calls: status is CONFIRMED.
  POST /orders/{id}/confirm -> not naturally idempotent
  ("confirm this order" applied twice: what happens?)
  Design APIs with PUT semantics when possible:
  "set state to X" is idempotent
  "add/apply/process" requires idempotency key

PATTERN 3: KAFKA CONSUMER DEDUPLICATION
  Consumer maintains: processed_events table
  On receive: check if event_id already processed
  If yes: acknowledge (skip processing)
  If no: process, insert event_id, acknowledge
  event_id: Kafka record key + partition + offset
           or application-level event ID in payload
  Storage: Redis (fast, TTL-based expiry)
           or DB (durable, joins possible)
```

**NATURAL IDEMPOTENCY BY HTTP METHOD:**

```
IDEMPOTENT HTTP METHODS (RFC 7231):
  GET: same result (read, no state change)
  PUT: set full state (same input = same result)
  DELETE: delete same resource = still deleted
  HEAD: like GET but headers only

NOT IDEMPOTENT:
  POST: create new resource = new resource each call
  PATCH: partial update - depends on semantics
    PATCH {increment_points: 10} -> NOT idempotent
    PATCH {total_points: 150}    -> idempotent (set)

DESIGN ADVICE:
  Prefer PUT over POST for resource creation
  when client can determine the resource ID:
  PUT /orders/{client-generated-uuid}
  body: { customerId, items, total }
  -> idempotent: same UUID = same order
  POST /orders with Idempotency-Key header:
  -> idempotent via server-side key tracking
```

---

### 🧪 Thought Experiment

**THE DOUBLE PAYMENT SCENARIO:**

```
SCENARIO:
  User clicks "Pay Now" on checkout page
  Request: POST /payments {orderId, amount: $99.99}
  Network: 30-second timeout (slow payment gateway)
  Result: 504 Gateway Timeout
  
  Browser: shows error "Payment failed"
  User: clicks "Pay Now" again (impatient)
  Second request sent
  
  Reality: BOTH requests reached the payment service
  First: charged $99.99 (processed but response lost)
  Second: charged $99.99 again = double charge!
  
  Customer: charged $199.98 for one order
  Support ticket: created
  Refund: required
  Trust: damaged

FIX WITH IDEMPOTENCY KEY:
  Browser: generates UUID before first click
  Stores: idempotencyKey = crypto.randomUUID()
  Sends: POST /payments
         Idempotency-Key: uuid-abc123
  First request: processed, stored with uuid-abc123
  Second request: uuid-abc123 found
                  return cached: {success, chargeId}
  Result: ONE charge; no double payment
  
  Browser: can retry safely as many times as needed
  Server: exactly one charge per idempotency key
```

---

### 🧠 Mental Model / Analogy

> Idempotency is like a light switch in a bright
> room. Pressing the switch ON when it's already
> ON: no change (light stays on). Pressing ON 10
> times: still just one light turned on. Compare
> to an elevator floor button: press 3 multiple
> times - floor 3 is already queued, pressing more
> doesn't add more floor-3 stops. The operation
> ("turn light on", "go to floor 3") is idempotent:
> applying it repeatedly has the same effect as
> applying it once. Design your microservice
> operations to behave the same way: applying the
> same request twice = same outcome.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Idempotency: if you do the same action twice, nothing
extra happens the second time. Like pressing an
elevator button that's already lit - no extra stop
is added. In microservices: important because networks
retry failed requests, so your service might see
the same request more than once.

**Level 2 - How to implement (junior developer):**
For REST APIs: `Idempotency-Key` header (UUID from
client). Store: `Map<UUID, ResponseBody>` in Redis
with 24h TTL. On request: check Redis; if hit,
return cached response; if miss, process and cache.
For Kafka consumers: maintain a `processed_events`
table; check before processing each event.

**Level 3 - How it works at scale (mid-level):**
Race condition: two concurrent requests with the
same idempotency key. Solution: database-level
unique constraint on idempotency key. First INSERT:
succeeds; second: constraint violation -> return
the first result. Use `INSERT ... ON CONFLICT DO
NOTHING` in PostgreSQL. Or: Redis SET NX (set if
not exists) with transaction.

**Level 4 - Why it's foundational (senior engineer):**
Idempotency is the bridge between "at-least-once"
delivery (what Kafka, HTTP retries, and Sagas provide)
and "effectively exactly-once" semantics (what the
business requires). Without idempotency: at-least-once
delivery = data corruption (duplicates). With
idempotency: at-least-once delivery = safe. The
combination of idempotency + at-least-once delivery
is the pragmatic alternative to exactly-once delivery
(which requires distributed transactions and has
high performance cost).

**Level 5 - Mastery (principal engineer):**
Idempotency key storage at scale: 1M requests/day
= 1M idempotency keys stored per day. With 24h
TTL: 1M active keys * average response size (~1KB)
= 1GB Redis storage per day just for idempotency.
For high-frequency, small-payload operations: use
compressed storage. For long-lived idempotency
(e.g., wire transfers that must not be duplicated
for months): use persistent DB with archiving.
Also: Kafka's Idempotent Producer (Kafka >=0.11):
automatically deduplicates messages at the broker
level using producer ID + sequence number. Use
`enable.idempotence=true` for at-least-once-safe
Kafka producers.

---

### ⚙️ How It Works (Mechanism)

```java
// IDEMPOTENCY KEY PATTERN for HTTP API
@RestController
public class PaymentController {

    @PostMapping("/payments")
    public ResponseEntity<PaymentResult> processPayment(
            @RequestHeader("Idempotency-Key") String key,
            @RequestBody PaymentRequest request) {

        // Check idempotency key in Redis
        String cached = redis.get("idem:" + key);
        if (cached != null) {
            // Already processed: return cached result
            return ResponseEntity.ok(
                objectMapper.readValue(cached,
                    PaymentResult.class));
        }

        // Process payment
        PaymentResult result = paymentService
            .charge(request);

        // Cache result with TTL
        redis.setex(
            "idem:" + key,
            Duration.ofHours(24).getSeconds(),
            objectMapper.writeValueAsString(result));

        return ResponseEntity.status(201).body(result);
    }
}

// KAFKA CONSUMER DEDUPLICATION
@Component
public class PaymentEventConsumer {

    @KafkaListener(topics = "payment-events")
    @Transactional
    public void onPaymentEvent(
            @Payload PaymentEvent event,
            Acknowledgment ack) {

        String eventId = event.getEventId();

        // Idempotency check
        if (processedEventRepo.existsById(eventId)) {
            log.debug("Duplicate event: {}", eventId);
            ack.acknowledge();
            return;
        }

        // Process: award loyalty points
        loyaltyService.awardPoints(
            event.getCustomerId(), event.getAmount());

        // Mark as processed (same transaction)
        processedEventRepo.save(
            new ProcessedEvent(eventId, Instant.now()));

        ack.acknowledge();  // Commit Kafka offset
        // If crash between processing and ack:
        // Kafka redelivers; idempotency check skips
    }
}

// CONCURRENT DUPLICATE PROTECTION
// Race: two requests with same key arrive simultaneously
// Solution: DB unique constraint
@Entity
@Table(name = "processed_requests",
       uniqueConstraints = @UniqueConstraint(
           columnNames = "idempotency_key"))
public class ProcessedRequest {
    @Id private String idempotencyKey;
    private String responseBody;  // JSON
    private Instant createdAt;
    // DB unique constraint: only one INSERT wins
    // Second INSERT: ConstraintViolationException
    // -> return the first result
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
IDEMPOTENT PAYMENT FLOW:

  Client: generates idempotencyKey = UUID-abc123
  
  Attempt 1:
    POST /payments, Idempotency-Key: UUID-abc123
    Server: checks Redis -> NOT FOUND
    Server: charges card -> charge-xyz success
    Server: stores {UUID-abc123: {chargeId: charge-xyz}}
    Network: timeout (response lost)
    Client: receives 504 (thinks it failed)
  
  Attempt 2 (retry):
    POST /payments, Idempotency-Key: UUID-abc123
    Server: checks Redis -> FOUND
    Server: returns {chargeId: charge-xyz} (cached)
    Client: receives 200 {chargeId: charge-xyz}
    
  Result: ONE charge (charge-xyz)
  Client: sees success on retry
  Customer: charged exactly once
  
  KEY: same idempotency key -> same result
  NEW payment: client generates new UUID -> new charge
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: non-idempotent Kafka consumer**

```java
// BAD: non-idempotent consumer - duplicates on restart
@KafkaListener(topics = "order-events")
public void onOrderCreated(OrderCreatedEvent event) {
    // If consumer crashes after processing but before
    // committing offset: event redelivered on restart
    notificationService.sendEmail(
        event.getCustomerId(), "Order confirmed!");
    // Duplicate email sent on redelivery!
    // kafka offset not committed = at-least-once
    // = email sent multiple times per order
}
```

```java
// GOOD: idempotent consumer with deduplication
@KafkaListener(topics = "order-events")
@Transactional
public void onOrderCreated(OrderCreatedEvent event,
                           Acknowledgment ack) {
    String eventId = event.getEventId();
    if (processedEventRepo.existsById(eventId)) {
        ack.acknowledge();  // Already done; skip
        return;
    }
    notificationService.sendEmail(
        event.getCustomerId(), "Order confirmed!");
    processedEventRepo.save(
        new ProcessedEvent(eventId, Instant.now()));
    ack.acknowledge();
    // First delivery: email sent + event recorded
    // Duplicate delivery: event found -> skip email
    // Customer receives exactly one email per order
}
```

---

### ⚖️ Comparison Table

| HTTP Method | Idempotent? | Example | Safe to Retry? |
|---|---|---|---|
| **GET** | Yes | GET /orders/123 | Yes |
| **PUT** | Yes | PUT /orders/123 {status: CONFIRMED} | Yes |
| **DELETE** | Yes | DELETE /orders/123 | Yes (already deleted = OK) |
| **POST** | No (by default) | POST /orders (create) | No (without idempotency key) |
| **PATCH** | Depends | PATCH {status: CONFIRMED} = Yes; PATCH {increment: 1} = No | Depends |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Idempotency means the response is always identical | Not exactly. The response should convey the same business result, but status codes may differ: first call returns 201 (Created), duplicate call may return 200 (OK) with the same body, or 201 again. The KEY requirement: the BUSINESS EFFECT (one order created, one payment charged) is identical. The HTTP semantics may acknowledge "already processed" differently. |
| DELETE is always idempotent | DELETE is idempotent in effect (resource is deleted after N calls) but not necessarily in status code. First DELETE: 200. Second DELETE: 404 (already gone). The resource management is idempotent; the response code is not. Design your clients to treat both 200 and 404 for a DELETE as "success". |
| Redis is sufficient for idempotency key storage | Redis is fast but volatile (memory, risk of eviction under pressure). For critical idempotency (financial transactions, Saga compensations): use a durable database (PostgreSQL) as the idempotency store. Use Redis for low-stakes idempotency (notification deduplication) where occasional duplicates are acceptable. Match storage durability to business criticality. |

---

### 🚨 Failure Modes & Diagnosis

**Double charge: client retry without idempotency key**

**Symptom:**
Customer support receives 50 complaints in one day:
customers charged twice for a single order. Payment
service logs show: some orders have 2 `PaymentProcessed`
events. All duplicates: 60-90 seconds apart (browser
retry timeout).

**Root Cause:**
Frontend code sends `POST /payments` WITHOUT an
Idempotency-Key header. Payment gateway has high
latency (>30s) during peak. Browser timeout:
retries after 30s. Both requests reach payment-service;
both process independently; double charge.

**Diagnostic:**
```sql
-- Find double charges
SELECT order_id, COUNT(*) AS charge_count
FROM payments
GROUP BY order_id
HAVING COUNT(*) > 1;
-- Returns: 50 orders with 2 charges each
```

**Fix:**
1. Frontend: generate `idempotencyKey = crypto
   .randomUUID()` before payment button click.
   Store in session. Send as `Idempotency-Key`
   header on every attempt.
2. Backend: implement idempotency key check
   (Redis or DB) before processing payment.
3. Refund affected customers immediately.
4. Add integration test: send same request twice
   with same idempotency key; assert only one
   charge created.

---

### 🔗 Related Keywords

**Why idempotency is needed:**
- `Event-Driven Microservices` - Kafka at-least-once
  delivery requires idempotent consumers
- `Outbox Pattern` - relay may republish events;
  consumers must be idempotent
- `Compensating Transaction` - Sagas retry compensations;
  compensations must be idempotent

**Complementary:**
- `Eventual Consistency in Microservices` - idempotency
  enables safe retry in eventually consistent systems
- `Cross-Cutting Concerns` - idempotency is a
  cross-cutting reliability concern

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DEFINITION   │ N identical calls = 1 call in effect      │
│              │ Safe to retry; no duplicate side effects  │
├──────────────┼───────────────────────────────────────────┤
│ IMPL.        │ Idempotency key (UUID) in header/payload  │
│              │ Check processed_events before consuming   │
├──────────────┼───────────────────────────────────────────┤
│ WHY NEEDED   │ At-least-once (Kafka, retries, Sagas)     │
│              │ -> idempotent consumer = effectively-once  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "At-least-once + idempotent = effectively  │
│              │  exactly-once without distributed txn"     │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Idempotency: same operation N times = same result
   as once. Essential in distributed systems where
   retries are unavoidable.
2. Implementation: Idempotency-Key header (UUID per
   request) on HTTP APIs; processed_events table
   for Kafka consumers.
3. Formula: at-least-once delivery + idempotent
   consumer = effectively exactly-once behavior.
   No distributed transaction required.

**Interview one-liner:**
"Idempotency: an operation that produces the same
result N times as it does once. Critical in microservices
because Kafka delivers at-least-once (consumer
restart = duplicate delivery), HTTP clients retry
on timeout, and Sagas retry compensating transactions.
Implementation: Idempotency-Key header (client-
generated UUID) stored with the response; duplicate
requests return cached result without re-executing.
For Kafka: processed_events table; check before
processing each event. Formula: at-least-once +
idempotent consumer = effectively exactly-once."

---

### 💡 The Surprising Truth

Idempotency is not just about preventing duplicates -
it enables a fundamentally different retry strategy.
Without idempotency: retries are dangerous (may
cause duplicates). With idempotency: retries are
FREE. You can retry aggressively (short timeouts,
many retries) knowing that duplicates are harmless.
This changes how you design resilience: instead of
one long-timeout request (to avoid needing a retry),
you make many short-timeout requests with idempotent
behavior. This aligns with the Hystrix/Resilience4j
philosophy: fail fast, retry smart. Idempotency is
the foundation that makes aggressive retry strategies
safe.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **IDENTIFY** Given a payment processing flow:
identify all the places where duplicate processing
could occur (client retry, Kafka redelivery, Saga
compensation retry). For each: specify the
idempotency mechanism needed.
2. **IMPLEMENT** Implement an idempotent HTTP endpoint
with: Redis-based idempotency key check, TTL
(24 hours), concurrent duplicate protection (SETNX
or DB unique constraint), and correct HTTP
status codes for first call vs duplicate call.
3. **KAFKA** Implement an idempotent Kafka consumer:
processed_events table, transactional check + process
+ record, correct behavior on: first delivery,
duplicate delivery, and delivery after partial
processing (crash between processing and ack).
4. **RACE CONDITION** Two HTTP requests with the
same idempotency key arrive simultaneously (within
1ms). How does your implementation ensure only one
processes the request? Walk through the exact race
condition and the DB constraint that prevents it.
5. **KAFKA PRODUCER** Configure `enable.idempotence
= true` on Kafka producer. What does this do at
the broker level? How does it differ from application-
level consumer idempotency?

---

### 🧠 Think About This Before We Continue

**Q1.** A payment service processes 100K payments
per day. Each payment has an idempotency key stored
in Redis with 24-hour TTL. Calculate: daily storage
requirement (assume 200 byte key + 500 byte response
= 700 bytes per entry). What is the Redis memory
requirement? At what scale would you need to switch
from Redis to PostgreSQL for idempotency key storage?

**Q2.** An idempotency key is used for a payment
request. The payment is processed successfully
but the response is cached in Redis as a success.
30 minutes later: the payment gateway reports the
charge was reversed (chargeback). The idempotency
key is still valid in Redis (23.5 hours left). If
the user retries: they get a cached "success"
response, but the payment is actually reversed.
How do you handle this case? Should idempotency
keys be invalidated on chargeback?

**Q3.** Your service receives Kafka events with
an event_id field. You store processed event_ids
in a `processed_events` table to ensure idempotency.
After 1 year: the table has 365M rows. Query
performance for idempotency check starts to
degrade. Design the data retention strategy:
how long do you need to keep processed event IDs?
How do you archive old entries without affecting
current idempotency checks?