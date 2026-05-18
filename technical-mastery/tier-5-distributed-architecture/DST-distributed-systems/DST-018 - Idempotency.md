---
id: DST-018
title: Idempotency
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★☆☆
depends_on: DST-003, DST-009, DST-011
used_by: DST-019, DST-035, DST-055
related: DST-009, DST-019, DST-035
tags:
  - distributed
  - reliability
  - foundational
  - messaging
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 18
permalink: /technical-mastery/distributed-systems/idempotency/
---

⚡ TL;DR - An operation is idempotent if performing it
multiple times produces the same result as performing it
once; this property is essential for safe retry logic in
distributed systems where operations may be executed,
lost, or acknowledged multiple times due to network
unreliability.

---

### 📋 Entry Metadata

| #018 | Category: Distributed Systems | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Network Is Unreliable, Message Passing, Fault Tolerance | |
| **Used by:** | At-Most/At-Least/Exactly-Once Delivery, Retry Logic, Saga Pattern | |
| **Related:** | Message Passing, Delivery Semantics, Retry Logic | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An e-commerce service receives a payment request from a
customer for $100. The service processes the payment with
the bank and sends the confirmation response. The network
drops the response. The customer's browser retries after
a timeout. The service receives the payment request again
and processes it - charging the customer $200. The service
"succeeded" twice. The customer was charged twice. This is
a double-charge bug caused by non-idempotent payment
processing with retry logic.

**THE CORE TENSION:**
Network unreliability makes retries necessary. But without
idempotency, retries cause duplicate operations. With
idempotency, any number of retries produces the same
final state as one successful operation. The choice:
live with the risk of losing operations (no retry) or
the risk of duplicating operations (retry without
idempotency). Idempotency provides the third option:
retry safely.

---

### 📘 Textbook Definition

An operation is **idempotent** if applying it multiple
times produces the same result as applying it once:
`f(f(x)) = f(x)`. In mathematics: `|x|` (absolute value)
is idempotent because `||x|| = |x|`. In distributed systems:
setting a value is idempotent (`SET x=5` performed twice
leaves x=5); incrementing a value is not idempotent
(`INCREMENT x` performed twice doubles the increment).
Idempotency is the property that makes **at-least-once
delivery** (with retries) produce the same result as
**exactly-once delivery** (no retries possible). Achieving
idempotency typically requires: (1) generating a unique
**idempotency key** per operation, (2) storing a record
of completed operations, and (3) rejecting duplicate
requests by returning the cached result of the first
successful execution.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An idempotent operation can be safely retried any number
of times without causing duplicate effects.

**One analogy:**
> Setting a light switch to "ON" is idempotent: if the
> light is already on and you flip it to ON again, nothing
> changes. Clicking "Add to cart" in many e-commerce
> systems is NOT idempotent: each click adds another copy
> of the item. "Pay invoice" must be idempotent: paying
> the same invoice twice should result in one payment.

**One insight:**
In a distributed system with at-least-once delivery
guarantees (the most common case), every consumer must
handle duplicate messages. The consumer can either:
(1) design its operations to be naturally idempotent,
or (2) implement idempotency by tracking which operations
have already been processed. Option (2) is more general
and required for operations that are not naturally
idempotent (payments, counter increments, etc.).

---

### 🔩 First Principles Explanation

**NATURALLY IDEMPOTENT vs REQUIRES IMPLEMENTATION:**

```
NATURALLY IDEMPOTENT:
  SET x = 5        → x is always 5 regardless of
    repetitions
  DELETE WHERE id=1 → row is absent after first execution
  PUT /users/1 {...} → resource is replaced to same state
  INSERT ... ON CONFLICT DO NOTHING → safe to retry

NOT NATURALLY IDEMPOTENT:
  INCREMENT x by 1  → each execution adds 1 more
  INSERT INTO orders VALUES (...)
    → each execution adds a duplicate row
  POST /payments    → each execution charges again
  SEND EMAIL        → each execution sends another email
```

**THE IDEMPOTENCY KEY PATTERN:**

For non-idempotent operations, make them idempotent by
attaching a unique **idempotency key** to each request.
The server tracks which keys have been processed. On
duplicate requests (same key), return the stored result
instead of re-executing.

```
┌──────────────────────────────────────────────────────┐
│  REQUEST 1 (original):                               │
│  POST /payments                                      │
│  Idempotency-Key: key-abc-123                        │
│  Body: {user: 1, amount: 100, currency: "USD"}       │
│                                                      │
│  Server: key-abc-123 not seen before. Process.       │
│  Store: {key: "key-abc-123", result: {charge_id: X}} │
│  Charge card. Return 200 {charge_id: X}              │
│                                                      │
│  REQUEST 2 (retry, same key):                        │
│  POST /payments                                      │
│  Idempotency-Key: key-abc-123                        │
│  Body: {user: 1, amount: 100, currency: "USD"}       │
│                                                      │
│  Server: key-abc-123 SEEN. Return cached result.     │
│  Return 200 {charge_id: X} (same response as first)  │
│  Card NOT charged again.                             │
└──────────────────────────────────────────────────────┘
```

**WHERE IDEMPOTENCY KEYS COME FROM:**
- Client-generated UUID per operation (most common)
- Hash of the request payload (for truly identical retries)
- Transaction ID from a parent system
- Message ID from a message broker (Kafka offset, SQS
  MessageId)

**IDEMPOTENCY KEY STORAGE:**
Keys must be stored durably (database, not in-memory cache)
with the result. Storage duration: long enough to cover
the retry window (minutes to hours for most systems;
days for financial reconciliation).

---

### 🧠 Mental Model / Analogy

> Idempotency is the postal service's acknowledgment system.
> A customer sends a registered letter. The postal service
> acknowledges receipt with a tracking number. If the
> customer's copy of the acknowledgment is lost (network
> issue), they can inquire again using the tracking number.
> The postal service checks its records: "Yes, we received
> this letter, here is the receipt" - without receiving
> and processing the letter twice.

**Mapping:**
- "Registered letter" - request with idempotency key
- "Tracking number" - idempotency key value
- "Inquiry using tracking number" - retry with same key
- "Checking records" - server lookup of processed keys
- "Receipt without re-processing" - returning cached result

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
An idempotent operation can be done many times but only
"takes effect" once. Like pressing an elevator button -
pressing it 10 times still only calls the elevator once.

**Level 2 - How to use it (junior developer):**
When building an API endpoint that processes payments,
sends emails, or creates orders: require a unique
idempotency key in the request header. Store the key and
the response after the first successful execution. If the
same key arrives again, return the stored response without
re-executing.

**Level 3 - How it works (mid-level engineer):**
Implement idempotency with a database table: `(idempotency_key,
result, created_at)`. Before processing a request, check
if the key exists. If yes: return cached result. If no:
execute, then store key + result atomically. Use a database
transaction to ensure the key is stored atomically with the
operation's effect. If the operation fails mid-way, the key
should not be stored (so it can be retried).

**Level 4 - Why it was designed this way (senior/staff):**
The idempotency key pattern is the standard way to achieve
effectively-once semantics over at-least-once delivery
infrastructure. The alternative - building exactly-once
delivery into the transport layer - is orders of magnitude
harder (requires distributed transactions across all
intermediate nodes). The insight: delegate the "exactly-once"
concern to the application layer using an idempotency key,
and keep the transport layer simple (at-least-once). This
is how Stripe, PayPal, and most payment APIs work.

**Level 5 - Mastery (distinguished engineer):**
True exactly-once processing with idempotency requires
atomic storage of the idempotency key and the operation's
side effects. If they are stored separately, there is a
window where the operation executes but the key is not
yet stored (the server crashes). On retry, the operation
executes again. The solution: use the same database
transaction for both: `BEGIN; EXECUTE OPERATION; INSERT
idempotency_key; COMMIT;`. If the server crashes between
BEGIN and COMMIT, the transaction is rolled back. The next
retry finds no stored key and re-executes. Critically: the
operation must be re-executable (its effect must be in the
same transaction). For external side effects (email send,
bank transfer), this is impossible - you need an outbox
pattern to defer the external call until after the
transaction commits.

---

### ⚙️ Mechanism - Idempotency Implementation

**DATABASE-BACKED IDEMPOTENCY (Full Flow):**

```
┌────────────────────────────────────────────────────────┐
│  RECEIVE request with Idempotency-Key: uuid-123        │
│              │                                         │
│  CHECK: SELECT * FROM idempotency_keys                 │
│         WHERE key = 'uuid-123'                         │
│              │                                         │
│    ┌─────────┴──────────────────┐                     │
│    │ FOUND                      │ NOT FOUND           │
│    │                            │                     │
│    │ Return cached response.    │ Acquire lock on     │
│    │ Do NOT re-execute.         │ key (advisory lock  │
│    └────────────────────────────│ or DB row lock)     │
│                                 │                     │
│                              Execute operation         │
│                              (charge card, send msg)  │
│                                 │                     │
│                              Store result:             │
│                              BEGIN TRANSACTION         │
│                              INSERT idempotency_keys  │
│                              (key, response, expires) │
│                              + apply side effects     │
│                              COMMIT                    │
│                                 │                     │
│                              Return response          │
└────────────────────────────────────────────────────────┘
```

**CONCURRENT DUPLICATE HANDLING:**
Two requests with the same key can arrive simultaneously
(network retry storm). Use a database unique constraint
on the idempotency key to prevent duplicate inserts.
The second concurrent request gets a unique constraint
violation - it should wait briefly and retry the lookup
to find the first request's result.

---

### 💻 Code Example

**Idempotent Payment Service (Wrong vs Right)**

```python
# BAD: Non-idempotent payment processing
@app.post("/payments")
def create_payment(
    user_id: int,
    amount: Decimal,
    currency: str
):
    # No idempotency key check
    charge = stripe.Charge.create(
        amount=int(amount * 100),
        currency=currency,
        customer=user_id
    )
    return {"charge_id": charge.id}
# If client retries after network timeout:
# → Two charges created. Customer billed twice.
```

```python
# GOOD: Idempotent payment with idempotency key
from fastapi import FastAPI, Header, HTTPException
from sqlalchemy.exc import IntegrityError

@app.post("/payments")
def create_payment(
    user_id: int,
    amount: Decimal,
    currency: str,
    idempotency_key: str = Header(
        ...,
        alias="Idempotency-Key"
    )
):
    with db.begin():
        # Check for existing processed request
        existing = db.execute(
            text(
                "SELECT response FROM idempotency_keys "
                "WHERE key = :key"
            ),
            {"key": idempotency_key}
        ).one_or_none()

        if existing:
            # Return cached response - do NOT charge again
            return existing.response

        # Not seen before: process and store atomically
        try:
            charge = stripe.Charge.create(
                amount=int(amount * 100),
                currency=currency,
                customer=user_id,
                # Also pass key to Stripe for idempotency
                # at the Stripe API level:
                idempotency_key=idempotency_key
            )
            result = {"charge_id": charge.id, "status": "ok"}

            # Store result atomically with operation
            db.execute(
                text(
                    "INSERT INTO idempotency_keys "
                    "(key, response, expires_at) "
                    "VALUES (:key, :resp, now() + interval "
                    "'24 hours')"
                ),
                {
                    "key": idempotency_key,
                    "resp": json.dumps(result)
                }
            )
            return result

        except IntegrityError:
            # Race: another request with same key is processing
            # Wait and retry lookup
            db.rollback()
            time.sleep(0.1)
            existing = db.execute(
                text(
                    "SELECT response FROM idempotency_keys "
                    "WHERE key = :key"
                ),
                {"key": idempotency_key}
            ).one_or_none()
            if existing:
                return existing.response
            raise HTTPException(
                status_code=503,
                detail="Concurrent request in progress"
            )
```

**Idempotent Message Consumer (Kafka)**

```python
# Idempotent Kafka consumer using message offset as key
from confluent_kafka import Consumer

def process_message(msg) -> None:
    # Use Kafka offset as idempotency key
    idempotency_key =
        f"kafka-{msg.topic()}-{msg.partition()}-{msg.offset()}"

    with db.begin():
        # Check if this message was already processed
        processed = db.execute(
            text(
                "SELECT 1 FROM processed_messages "
                "WHERE message_id = :id"
            ),
            {"id": idempotency_key}
        ).one_or_none()

        if processed:
            return  # Already handled, skip

        # Process the business logic
        payload = json.loads(msg.value())
        apply_business_logic(payload)

        # Mark as processed
        db.execute(
            text(
                "INSERT INTO processed_messages "
                "(message_id, processed_at) "
                "VALUES (:id, now())"
            ),
            {"id": idempotency_key}
        )
```

---

### ⚖️ Comparison Table

| HTTP Method | Idempotent? | Why |
|---|---|---|
| **GET** | Yes (RFC) | Read-only, no state change |
| **PUT** | Yes (RFC) | Replace resource: same result each time |
| **DELETE** | Yes (RFC) | Resource absent after first call |
| **POST** | No | Creates new resource; retry = new resource |
| **PATCH** | No (usually) | Depends: `set=5` yes; `increment=1` no |

| Database Operation | Idempotent? | Note |
|---|---|---|
| `SET x = 5` | Yes | Same result every time |
| `INSERT ... ON CONFLICT DO NOTHING` | Yes | No duplicate insert |
| `DELETE WHERE id=1` | Yes | Row absent after first run |
| `INSERT INTO` | No | Duplicate row on retry |
| `UPDATE x = x + 1` | No | Each run adds 1 more |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "GET requests are always idempotent" | GET is safe AND idempotent by HTTP spec. But some APIs use GET with side effects (bad practice: `GET /send-email?to=x`). Safe != idempotent, though GET should be both. |
| "PUT is always idempotent" | PUT replacing a full resource is idempotent. But if PUT appends (non-standard), it is not. Idempotency depends on implementation, not just HTTP method. |
| "Adding a unique constraint makes operations idempotent" | A unique constraint on idempotency key prevents duplicate storage. But if the operation succeeds and the key storage fails, the operation ran without a key stored. The operation must be in the same transaction as the key storage. |
| "Idempotency only matters for payments" | Idempotency matters for any operation with real-world effects: sending emails, provisioning infrastructure, creating records, updating inventory. Any operation executed at-least-once needs idempotency. |

---

### 🚨 Failure Modes & Diagnosis

**Double-Charge from Non-Idempotent Retry**

**Symptom:** Customer support reports customers being
charged twice. Both charges appear in Stripe with different
charge IDs. The second charge is always about 30 seconds
after the first - matching the HTTP client timeout.

**Root Cause:** Payment API does not implement idempotency
keys. HTTP client retries on timeout. First request
succeeded (charge created). Response lost in transit.
Client retried. Second charge created.

**Diagnosis:**
```python
# Audit charges for duplicates:
charges = stripe.Charge.list(limit=100)
seen_amounts = {}
for charge in charges:
    key = (charge.customer, charge.amount, charge.currency)
    if key in seen_amounts:
        created_diff = charge.created - seen_amounts[key].created
        if created_diff < 120:  # within 2 minutes
            print(
                f"POTENTIAL DUPLICATE: {seen_amounts[key].id}"
                f" and {charge.id}, "
                f"{created_diff}s apart"
            )
    seen_amounts[key] = charge
```

**Fix:**
1. Add idempotency key to all payment requests
2. Implement server-side idempotency check
3. Pass idempotency key to Stripe (they support it natively)
4. Issue refunds for confirmed duplicates

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `The Network Is Unreliable` - Why retries are necessary
- `Message Passing` - The communication layer where
  duplicates occur
- `Fault Tolerance` - The motivation for retry logic

**Builds On This (learn these next):**
- `At-Most-Once, At-Least-Once, Exactly-Once` - The delivery
  semantics that idempotency makes equivalent from the
  application's perspective
- `Retry Logic with Exponential Backoff` - How to implement
  safe retries using idempotent operations

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Operation safe to repeat: f(f(x)) = f(x) │
├──────────────┼──────────────────────────────────────────┤
│ WHY IT MATTERS│ Network failures cause retries;         │
│              │ retries cause duplicates without it      │
├──────────────┼──────────────────────────────────────────┤
│ PATTERN      │ Client sends unique idempotency key;     │
│              │ server stores key+result after first run;│
│              │ duplicate requests return cached result  │
├──────────────┼──────────────────────────────────────────┤
│ NATURAL      │ SET x=5, DELETE, PUT, GET                │
├──────────────┼──────────────────────────────────────────┤
│ NOT NATURAL  │ INCREMENT, INSERT, POST /payments        │
│              │ → requires idempotency key implementation│
├──────────────┼──────────────────────────────────────────┤
│ KEY RULE     │ Store idempotency key and side effect    │
│              │ in the SAME transaction                  │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Using in-memory cache for idempotency    │
│              │ keys (lost on restart, race conditions)  │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Design operations so retrying is safe;  │
│              │  make exactly-once a client concern."    │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Delivery Semantics → Retry with Backoff  │
│              │ → Saga Pattern → Outbox Pattern          │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Any operation that may be retried must be designed for
idempotency. This applies beyond distributed systems:
database triggers that fire on UPDATE should be idempotent
(triggering twice should not double the effect). Scheduled
jobs that may run twice due to restart should be idempotent.
Infrastructure provisioning scripts (Terraform apply) are
idempotent by design: running them multiple times results
in the same infrastructure state.

**Stripe's public API** is a canonical example of production-
grade idempotency design: every mutating endpoint accepts
an `Idempotency-Key` header, stores results for 24 hours,
and returns the exact same response on duplicate keys.
Their implementation documentation is required reading for
anyone building financial APIs.

---

### 💡 The Surprising Truth

HTTP DELETE is specified as idempotent (RFC 7231), but many
APIs implement it as non-idempotent: deleting an already-
deleted resource returns 404 instead of 200. Technically,
both DELETE calls produce the same state (resource absent),
so the operation IS idempotent by the mathematical definition.
But if the caller treats a 404 response as an error and
retries, it loops forever on already-deleted resources.
The lesson: idempotency is a semantic guarantee, not just a
status code guarantee. An operation is idempotent if the
observable state is the same after N executions as after 1.
HTTP methods that return different status codes on retry
(200 then 404) may be idempotent in state but not in response
- and the caller must handle both cases.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. [CLASSIFY] Given a list of operations (INSERT, SET,
   DELETE, INCREMENT, SEND_EMAIL, PROVISION_VM), classify
   each as naturally idempotent or requiring an idempotency
   key implementation.
2. [BUILD] Implement a database-backed idempotency key
   handler for a payment service, including: key lookup,
   concurrent duplicate handling (race condition), and
   atomic key + operation storage.
3. [DEBUG] Given a payment system with occasional duplicate
   charges, use charge timestamps and idempotency key
   audit logs to identify which operations were retried
   without idempotency keys.
4. [DESIGN] Design the idempotency strategy for a complex
   multi-step operation: reserve seat, process payment,
   send confirmation email. Each step may fail. What are
   the idempotency keys, and how is exactly-once behavior
   achieved end-to-end?
5. [EXPLAIN] Why storing the idempotency key in the same
   database transaction as the operation's effect is
   required for correctness, and what failure scenario
   is introduced by storing them separately.
