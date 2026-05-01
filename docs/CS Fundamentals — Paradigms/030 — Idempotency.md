---
layout: default
title: "Idempotency"
parent: "CS Fundamentals — Paradigms"
nav_order: 30
permalink: /cs-fundamentals/idempotency/
number: "030"
category: CS Fundamentals — Paradigms
difficulty: ★★☆
depends_on: Side Effects, HTTP & APIs, Distributed Systems
used_by: REST APIs, Microservices, Message Queues, Distributed Systems
tags: #intermediate, #distributed, #reliability, #architecture
---

# 030 — Idempotency

`#intermediate` `#distributed` `#reliability` `#architecture`

⚡ TL;DR — An operation is **idempotent** when applying it multiple times produces the same result as applying it once — making retries and duplicate deliveries safe in distributed systems.

| #030            | Category: CS Fundamentals — Paradigms                         | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------ | :-------------- |
| **Depends on:** | Side Effects, HTTP & APIs, Distributed Systems                |                 |
| **Used by:**    | REST APIs, Microservices, Message Queues, Distributed Systems |                 |

---

### 📘 Textbook Definition

An operation is **idempotent** if applying it one or more times produces the same result as applying it exactly once: `f(f(x)) = f(x)`. In mathematics, this property is held by operations such as absolute value (`||-x|| = ||x||`) and set union with the same set (`A ∪ A = A`). In computing, an idempotent operation is one whose observable side effects are the same regardless of how many times it is executed with the same input. HTTP defines `GET`, `PUT`, `DELETE`, and `HEAD` as idempotent; `POST` is not. In distributed systems, idempotency is a critical reliability guarantee: because networks can deliver messages multiple times (at-least-once delivery), any operation that processes messages must either be idempotent or implement deduplication to avoid processing the same message twice and producing double writes, double charges, or duplicate notifications.

---

### 🟢 Simple Definition (Easy)

An idempotent operation is one you can safely repeat any number of times and always get the same result — doing it twice is the same as doing it once.

---

### 🔵 Simple Definition (Elaborated)

Idempotency matters because networks and distributed systems are unreliable: a request might time out after the server processed it, the client retries, and now the server receives the same request twice. If the operation is idempotent, the second call does nothing extra — the final state is the same as if it ran once. Setting a light switch to "on" is idempotent: flipping it to "on" when it is already on does nothing new. Pushing it with a toggle switch is NOT idempotent: a second push changes the state. In APIs, `PUT /users/123 { name: "Alice" }` is idempotent — calling it ten times leaves the user with name "Alice" exactly as if called once. `POST /payments { amount: 100 }` is NOT idempotent by default — ten calls might create ten payments. Making it idempotent requires an idempotency key so the server can detect and ignore duplicates.

---

### 🔩 First Principles Explanation

**The problem: networks cause duplicate delivery.**

In any distributed system, message delivery follows one of three guarantees:

- **At-most-once**: message delivered zero or one time — may be lost.
- **Exactly-once**: message delivered exactly once — theoretically achievable with high cost.
- **At-least-once**: message delivered one or more times — duplicates possible.

Most practical systems choose at-least-once because it is simpler and more reliable than exactly-once. This means consumers WILL receive duplicate messages. The burden of handling duplicates moves to the receiver.

**If the operation is NOT idempotent:**

```
Client sends: POST /payments { amount: 100 }
Server processes: charges card for $100
Network times out before response reaches client
Client retries: POST /payments { amount: 100 }
Server processes AGAIN: charges card for another $100
Result: customer charged $200 for a $100 order
```

**Making the operation idempotent with an idempotency key:**

```
Client generates UUID: idempotency-key = "a3f1e9b2"
Client sends: POST /payments { amount: 100 }
             Header: Idempotency-Key: a3f1e9b2
Server processes: charges card for $100
                  stores: key="a3f1e9b2" → result=SUCCESS
Network times out before response reaches client
Client retries: POST /payments { amount: 100 }
               Header: Idempotency-Key: a3f1e9b2
Server looks up: key="a3f1e9b2" → found: SUCCESS
Server returns cached response — NO second charge
Result: customer charged $100 once, as intended
```

**The mathematical foundation:**

```
Idempotent: f(f(x)) = f(x)

Examples:
  Math.abs(-5) = 5;  Math.abs(5)  = 5  ✓ idempotent
  Collections.sort(sortedList)        ✓ idempotent (already sorted → no change)
  setStatus("CANCELLED")              ✓ idempotent (calling twice: still CANCELLED)
  increment(counter)                  ✗ NOT idempotent: 5 → 6 → 7

HTTP methods by specification:
  GET, HEAD, OPTIONS: safe + idempotent (no state change)
  PUT, DELETE:        idempotent (not necessarily safe)
  POST, PATCH:        NOT idempotent by default
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Idempotency:

What breaks without it:

1. Network timeouts after partial processing cause duplicated charges, orders, or notifications with no way to detect or correct.
2. Message queue at-least-once delivery creates duplicate records in the database.
3. Retry logic in HTTP clients (Spring's `@Retryable`, AWS SDK's built-in retry) causes silent data corruption on non-idempotent endpoints.
4. Distributed transactions that fail halfway leave the system in an inconsistent state with no safe recovery path.
5. Kafka consumer restarts re-process already-committed offsets if the consumer's action was not idempotent.

WITH Idempotency:
→ Retries are safe: clients can always retry on timeout or 5xx without risk of double-processing.
→ Message consumers handle broker redelivery without side effects.
→ Distributed systems achieve "effectively exactly-once" by combining at-least-once delivery with idempotent consumers.
→ Recovery from partial failures is straightforward: re-run the failed operation.

---

### 🧠 Mental Model / Analogy

> Think of a hotel check-in. Handing your key card to the door sensor is idempotent: swipe it once, the door opens; swipe it again, the door is already open — no second door appears. By contrast, putting a coin in a vending machine is NOT idempotent: each coin inserts more credit. The vending machine must handle "I accidentally inserted the same coin twice" specially (coin return), because the operation itself is not idempotent. Designing APIs and message handlers to be idempotent is choosing to build hotel door sensors — the system handles repeated operations gracefully without special-case logic at the caller.

"Hotel door sensor" = idempotent operation (repeated input → same state)
"Vending machine coin slot" = non-idempotent operation
"Accidentally inserting the same coin twice" = duplicate message / retry
"Coin return mechanism" = deduplication logic required for non-idempotent ops
"The door just being open" = cached/idempotent response returned on retry

---

### ⚙️ How It Works (Mechanism)

**Pattern 1 — Idempotency key (API-level deduplication):**

```
┌────────────────────────────────────────────┐
│  Idempotency Key Pattern                   │
│                                            │
│  Client                    Server          │
│    │                         │             │
│    │─── POST /payments ─────►│             │
│    │    Idempotency-Key: K1  │             │
│    │                         │─► process  │
│    │                         │─► store K1 │
│    │◄── 200 OK ──────────────│             │
│                                            │
│    │─── POST /payments ─────►│  (retry)   │
│    │    Idempotency-Key: K1  │             │
│    │                         │─► lookup K1│
│    │                         │─► found!   │
│    │◄── 200 OK (cached) ─────│            │
│          (no re-charge)                    │
└────────────────────────────────────────────┘
```

**Pattern 2 — Natural key / upsert (database-level idempotency):**

```sql
-- Non-idempotent: INSERT creates a new row every time
INSERT INTO orders (user_id, product_id, amount)
VALUES (123, 456, 100.0);

-- Idempotent: UPSERT (INSERT … ON CONFLICT DO NOTHING / UPDATE)
INSERT INTO orders (order_id, user_id, product_id, amount)
VALUES ('ord-uuid-abc', 123, 456, 100.0)
ON CONFLICT (order_id) DO NOTHING;
-- Duplicate call with same order_id → silently ignored → idempotent
```

**Pattern 3 — Conditional update (optimistic locking):**

```java
// Idempotent status update: only update if current state allows it
int rowsUpdated = jdbcTemplate.update(
    "UPDATE orders SET status = ? WHERE id = ? AND status != ?",
    "CANCELLED", orderId, "CANCELLED"
);
// If already CANCELLED: rowsUpdated = 0 — idempotent (no-op on repeat)
// If PLACED: rowsUpdated = 1 — transitions to CANCELLED once
```

**HTTP idempotency by method:**

```
Method   Idempotent   Safe    Typical use
GET      YES          YES     Fetch resource
HEAD     YES          YES     Fetch headers
OPTIONS  YES          YES     Discover capabilities
PUT      YES          NO      Replace resource entirely
DELETE   YES          NO      Remove resource
POST     NO           NO      Create resource / trigger action
PATCH    NO           NO      Partial update (usually non-idempotent)
```

---

### 🔄 How It Connects (Mini-Map)

```
Side Effects
(idempotency manages repeated side effects)
        │
        ▼
Idempotency  ◄──── (you are here)
        │
        ├──────────────────────────────────────────┐
        ▼                                          ▼
REST APIs / HTTP                        Message Queues
(PUT, DELETE are idempotent)            (at-least-once → need idempotent consumers)
        │                                          │
        ▼                                          ▼
Distributed Systems                     Microservices
(retry safety, partial failure)         (saga pattern, compensating txn)
```

---

### 💻 Code Example

**Example 1 — Idempotency key implementation in a payment service:**

```java
@Service
class PaymentService {
    private final PaymentGateway gateway;
    private final IdempotencyStore store;   // Redis or DB

    PaymentResult charge(PaymentRequest request, String idempotencyKey) {
        // 1. Check if this key was already processed
        Optional<PaymentResult> cached = store.get(idempotencyKey);
        if (cached.isPresent()) {
            return cached.get(); // return previous result — no re-charge
        }

        // 2. Process the payment
        PaymentResult result = gateway.charge(request);

        // 3. Store result against the key (TTL: 24 hours)
        store.put(idempotencyKey, result, Duration.ofHours(24));
        return result;
    }
}
// Client generates UUID per payment attempt and sends as X-Idempotency-Key header
// Safe to retry on timeout: same key → cached result returned
```

**Example 2 — Idempotent Kafka consumer:**

```java
@KafkaListener(topics = "order-created")
void onOrderCreated(OrderCreatedEvent event) {
    // Idempotent: only process if not already processed
    if (orderRepo.existsById(event.getOrderId())) {
        log.info("Duplicate event for {}, skipping", event.getOrderId());
        return; // at-least-once delivery: skip duplicates
    }

    // Process (create order) — runs exactly once per order ID
    Order order = new Order(event);
    orderRepo.save(order);
    notificationService.sendConfirmation(order);
}
```

**Example 3 — Idempotent REST API with proper HTTP semantics:**

```java
// PUT is idempotent by HTTP spec — implement accordingly
@PutMapping("/users/{id}")
ResponseEntity<User> updateUser(@PathVariable String id,
                                 @RequestBody UserDto dto) {
    // Full replacement — idempotent: same body → same result
    User user = userRepo.findById(id)
        .orElse(new User(id)); // create if not exists
    user.setName(dto.getName());
    user.setEmail(dto.getEmail());
    userRepo.save(user);
    return ResponseEntity.ok(user);
}
// PUT /users/123 { name: "Alice" } called 100 times → user has name "Alice"
// Same as calling it once — idempotent ✓

// POST is NOT idempotent — use idempotency keys for safety
@PostMapping("/payments")
ResponseEntity<Payment> createPayment(
        @RequestBody PaymentRequest req,
        @RequestHeader("Idempotency-Key") String key) {
    return ResponseEntity.ok(paymentService.charge(req, key));
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                                   | Reality                                                                                                                                                                                                                                                                                   |
| ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DELETE` is not idempotent because the second call returns 404                  | HTTP's idempotency refers to server-side state, not the response code. After the first `DELETE`, the resource is gone. After the second, it is still gone. The state is identical — idempotent. Returning 404 on the second call is correct and does not violate idempotency              |
| `GET` is idempotent so it never changes state                                   | `GET` is defined as both safe (no intended state change) AND idempotent. But nothing prevents a poorly designed server from changing state on `GET` (e.g., incrementing a view counter). Safe + idempotent is what the spec says `GET` SHOULD be; enforcement is up to the implementation |
| Idempotency and referential transparency are the same concept                   | They address related but different concerns. RT is about expressions returning the same value (pure functions, no side effects). Idempotency is about operations producing the same _state_ when repeated — they may still have side effects, just the same effects each time             |
| Using a UUID as an idempotency key automatically makes the operation idempotent | The UUID is the key that allows the server to DETECT duplicates. The server still must implement the idempotency logic (store the result, return cached result on duplicate key). The UUID alone does nothing                                                                             |

---

### 🔥 Pitfalls in Production

**Retrying POST requests without idempotency keys — double charges**

```java
// BAD: @Retryable applied to a non-idempotent payment call
@Service
class OrderService {
    @Retryable(value = {SocketTimeoutException.class},
               maxAttempts = 3)
    void placeOrder(Order order) {
        paymentGateway.charge(order.getTotal()); // POST — NOT idempotent
        orderRepo.save(order);
    }
}
// Timeout after charge but before save → retry charges card again
// Customer charged twice; second orderRepo.save succeeds → corrupt state

// GOOD: use idempotency key for all non-idempotent external calls
void placeOrder(Order order) {
    String key = order.getIdempotencyKey(); // UUID generated when order created
    paymentGateway.charge(order.getTotal(), key); // server deduplicates
    orderRepo.save(order);
}
```

---

**Idempotency key with too-short TTL — duplicate processing after expiry**

```java
// BAD: idempotency key stored with 1-minute TTL
store.put(key, result, Duration.ofMinutes(1));
// If client's retry happens at minute 2 (slow network, long circuit-breaker):
// Key has expired → payment processed AGAIN
// Customer double-charged after seemingly safe retry

// GOOD: use a TTL that covers the maximum reasonable retry window
// Stripe uses 24 hours; for most APIs 1–7 days is appropriate
store.put(key, result, Duration.ofHours(24));
// Also: tie TTL to business semantics (e.g., expiry of the payment session)
```

---

**Kafka consumer not handling rebalance — duplicate processing**

```java
// BAD: consumer commits offset BEFORE processing — message may be lost
@KafkaListener(topics = "payments")
void process(ConsumerRecord<String, PaymentEvent> record) {
    // Kafka auto-commits offset after poll() — BEFORE this line runs
    // If the service crashes here: offset committed, message lost
    paymentService.process(record.value());
}

// BAD: consumer processes THEN crashes before commit — duplicate
// (opposite of above — at-least-once: message re-delivered on restart)

// GOOD: make the consumer idempotent to handle both cases safely
@KafkaListener(topics = "payments")
void process(ConsumerRecord<String, PaymentEvent> record) {
    String paymentId = record.value().getPaymentId();
    if (processedEventStore.contains(paymentId)) {
        return; // idempotent: skip already-processed events
    }
    paymentService.process(record.value());
    processedEventStore.record(paymentId, Duration.ofDays(7));
    // Now safe for both at-least-once AND at-most-once delivery
}
```

---

### 🔗 Related Keywords

- `Side Effects` — idempotency manages the consequence of repeated side effects in distributed execution
- `Referential Transparency` — idempotency is to distributed operations what RT is to pure functions: same repeated input → same outcome
- `REST APIs / HTTP` — HTTP defines idempotency semantics for each method (`GET`, `PUT`, `DELETE` are idempotent; `POST` is not)
- `Distributed Systems` — at-least-once message delivery makes idempotency essential for correct consumer design
- `Microservices` — the Saga pattern for distributed transactions requires idempotent compensating transactions
- `Message Queues` — Kafka, RabbitMQ, and SQS with at-least-once delivery require idempotent consumers
- `Optimistic Locking` — database mechanism for ensuring conditional updates are idempotent
- `Exactly-Once Semantics` — the combination of at-least-once delivery + idempotent consumers = effectively exactly-once processing

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ f(f(x)) = f(x): applying once or many     │
│              │ times produces the same observable state  │
├──────────────┼───────────────────────────────────────────┤
│ HTTP         │ Idempotent: GET, PUT, DELETE, HEAD         │
│              │ NOT idempotent: POST, PATCH (by default)  │
├──────────────┼───────────────────────────────────────────┤
│ PATTERNS     │ Idempotency key, upsert (ON CONFLICT),     │
│              │ conditional update, deduplication store   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Build hotel door sensors, not vending     │
│              │ machines: the same swipe never charges    │
│              │ twice."                                   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Distributed Systems → Saga Pattern →       │
│              │ Exactly-Once Semantics → Event Sourcing   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A payment microservice uses idempotency keys stored in Redis with a 24-hour TTL. A customer submits a payment at 11:58 PM; the server processes it and stores the idempotency key. At 12:01 AM the next day, the client retries with the same key. Exactly one scenario causes the Redis key to have expired between the original call and the retry. Describe the conditions under which this happens, explain the resulting double-charge, and propose a design that makes the idempotency guarantee durable across this boundary without requiring an infinitely long TTL or switching to a relational database.

**Q2.** Kafka's _transactional producer_ combined with Kafka Streams' _exactly-once processing_ claims to provide "exactly-once semantics." Yet idempotency is still required for consumers that write to external systems (databases, HTTP services) outside of Kafka. Explain precisely what Kafka's exactly-once guarantee covers and what it does NOT cover, describe the two-phase commit problem that arises when a Kafka consumer writes to both Kafka (produce to output topic) and a Postgres database in the same transaction, and identify the pattern (Outbox Pattern, CDC, or other) that achieves end-to-end exactly-once delivery from Kafka to Postgres.
