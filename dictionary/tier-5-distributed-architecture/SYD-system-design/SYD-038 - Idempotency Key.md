---
id: SYD-038
title: Idempotency Key
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-008
used_by: ""
related: SYD-008, SYD-037, SYD-039, SYD-062
tags:
  - architecture
  - reliability
  - distributed-systems
  - payments
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 38
permalink: /syd/idempotency-key/
---

# SYD-038 - Idempotency Key

⚡ TL;DR - An idempotency key is a unique client-
generated token sent with a mutating request. The
server records the key with the result of the first
execution. If the same request arrives again (retry),
the server returns the stored result without re-
executing. This makes non-idempotent operations (charge
a credit card, send an email, place an order) safe
to retry without causing duplicate side effects. The
pattern is the foundation of reliable distributed
operations where network failures require retries.

| #038 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Horizontal vs Vertical Scaling | |
| **Used by:** | (Saga Pattern) | |
| **Related:** | Horizontal Scaling, Polling vs Webhooks, Distributed Locks, Saga Pattern | |

---

### 🔥 The Problem This Solves

**THE RETRY PROBLEM:**
A mobile app submits a payment of $99. The network
request is sent. The payment processor charges the
card successfully. But the response is lost in transit
(network timeout). The app sees a "network error" and
retries. The payment processor charges the card again:
$198 total. The customer calls support. The company
refunds $99 and apologizes.

This scenario is not a theoretical edge case. At scale:
- 0.1% of API calls result in network timeouts
- 1 million payment calls/day × 0.1% = 1,000 potential
  duplicate charges per day
- Without idempotency: real money lost, customer trust damaged

**THE SOLUTION:**
Client generates a unique idempotency key per payment
intent (e.g., UUID). Sends the key in the request header.
Server records key → result after first execution.
On retry with same key: return stored result. Customer
is charged exactly once.

---

### 📘 Textbook Definition

**Idempotency key:** A unique, client-generated identifier
attached to a mutating API request (POST, PUT, DELETE).
The server uses this key to detect duplicate requests
and return the same response without re-executing the
operation. This makes the operation safe to retry any
number of times with the same key, achieving "exactly-once"
semantics over "at-most-once" or "at-least-once" delivery.

**Idempotent operation:** An operation where executing
it multiple times produces the same result as executing
it once. GET is inherently idempotent. PUT (replace
entire resource) is idempotent. POST (create) is NOT
inherently idempotent - idempotency keys make it so.

**Exactly-once semantics:** The guarantee that an
operation is executed exactly once, even if the
request is sent multiple times. Implemented by
combining at-least-once delivery (retries on failure)
with idempotency (skip re-execution on duplicate).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Client stamps each request with a unique ID. Server
remembers: "I've seen this ID before; return the
cached result." Retry without re-execution.

**One analogy:**
> Idempotency key is like a check's memo line:
> - You write check #1042 to the landlord for $1,500
> - If the landlord deposits it twice, the bank blocks
>   the second deposit ("check #1042 already cashed")
> - The check number is the idempotency key
> - The bank's "already processed" database is the
>   idempotency store
>
> Without check numbers (no idempotency keys):
> the landlord gets paid twice and you bounce your
> other checks.

**One insight:**
Network failures are guaranteed to happen at scale.
"At-least-once" delivery (retry on failure) is the
only reliable way to ensure delivery. But at-least-once
delivery without idempotency causes duplicate operations.
Idempotency keys bridge the gap: retry freely, execute once.

---

### 🔩 First Principles Explanation

**THE IDEMPOTENCY KEY LIFECYCLE:**

```
Step 1: Client generates a UUID before the request
  idempotency_key = uuid4()  # e.g., "a1b2c3d4-..."
  Persist locally: store(request_data, idempotency_key)
  
Step 2: Client sends request with key in header
  POST /payments HTTP/1.1
  Idempotency-Key: a1b2c3d4-...
  {"amount": 9900, "currency": "usd"}

Step 3: Server checks idempotency store
  SELECT result FROM idempotency_store
  WHERE key = 'a1b2c3d4-...'
  
  If found: return stored result (no re-execution)
  If not found: proceed to execute

Step 4: Server executes and stores result atomically
  BEGIN TRANSACTION:
    execute operation (charge card)
    INSERT INTO idempotency_store
      (key, result, expires_at)
      VALUES ('a1b2c3d4-...', '{"charge_id": "ch_XYZ"}', ...)
  COMMIT

Step 5: Response sent to client
  {"charge_id": "ch_XYZ", "status": "succeeded"}

Retry with same key:
  Step 3 finds the key: return stored result
  No second charge. Same response as original.
```

**KEY DESIGN DECISIONS:**

**1. Who generates the key?**
Always the client (not the server). The client generates
the key before sending the request. This is critical:
if the client generates the key AFTER a failed response,
it might generate a different key for the same logical
operation, causing duplication.

```python
# GOOD: Generate key BEFORE sending request
def charge_customer(customer_id: str, amount: int):
    idempotency_key = str(uuid4())
    # Store key locally BEFORE sending
    save_pending_request(idempotency_key,
                          customer_id, amount)
    response = call_payment_api(
        customer_id, amount, idempotency_key)
    return response

# BAD: Generate key AFTER failure
def charge_customer_BAD(customer_id: str, amount: int):
    try:
        response = call_payment_api(customer_id, amount)
    except NetworkError:
        # Generate new key for retry → different key
        # → server treats it as a NEW request → duplicate!
        new_key = str(uuid4())
        response = call_payment_api(
            customer_id, amount, new_key)
```

**2. TTL for the idempotency store:**
```
Idempotency records should not live forever.
Common TTL: 24 hours (Stripe) or 7 days.
After TTL: duplicate detection no longer applies.
The assumption: if a client retries after 7 days,
it is probably a legitimately new operation.

Implementation:
  Redis: SET key result EX 86400  (24h TTL)
  PostgreSQL: expires_at TIMESTAMP + cron job to delete
```

**3. Request fingerprinting:**
```
What if client reuses the same idempotency key
with DIFFERENT request bodies?

Bad scenario:
  POST /payments, key=KEY1, amount=9900
  POST /payments, key=KEY1, amount=50000  (different amount!)

Secure implementation: store a fingerprint of the
original request body with the key. On duplicate:
compare fingerprints. If different → return 422
("idempotency key mismatch, original request was
for different params").

This prevents key reuse across different operations.
```

---

### 🧪 Thought Experiment

**SCENARIO: Stripe's at-least-once webhook + idempotency**

Stripe sends a webhook for event `payment.succeeded`.
Your server processes it and sends a confirmation email.
Stripe retries (didn't receive 200 in time). Your server
receives the same event again.

**Without idempotency:**
Email sent twice. Customer confused. Support ticket opened.

**With idempotency:**
```python
def process_webhook(event: dict):
    event_id = event["id"]  # "evt_abc123"
    
    # Check idempotency store (Redis)
    if redis.sismember("processed_events", event_id):
        return  # Already processed; skip
    
    # Process: send email
    send_confirmation_email(event["data"])
    
    # Mark as processed (atomic with processing ideally)
    redis.sadd("processed_events", event_id)
    redis.expire("processed_events", 7 * 86400)  # 7 days
```

**The dual use:**
Idempotency keys are both for client-initiated retries
(safe payment retries) AND server-side deduplication
(safe webhook processing). Same pattern; different
context. In both cases: unique ID + "have I seen this
before?" check + skip re-execution on duplicate.

---

### 🧠 Mental Model / Analogy

> Idempotency key is like a voting booth's ballot stub:
> - Each voter receives a unique numbered stub
> - When you vote, your stub number is recorded
> - If you try to vote again: "stub #4521 already used"
> - Your second attempt is rejected (not re-processed)
>
> The stub number is the idempotency key.
> The "already voted" record is the idempotency store.
> The election (outcome) is not affected by your retry.
>
> Without stubs: could vote twice → election corrupted.
> With stubs: retry is safe → election is correct.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Send a unique token with each important request.
The server remembers "I've processed this token" and
won't do it again if you retry.

**Level 2 - How to use it (junior developer):**
Generate a UUID before making a payment/order/email
request. Pass it in the `Idempotency-Key` header.
Stripe, Braintree, PayPal all support this natively.
Store the UUID in your database before sending so
you can retry with the same key if needed.

**Level 3 - How it works (mid-level engineer):**
The server's idempotency store must be checked and
updated atomically with the operation execution.
If the check and execution are separate transactions,
two concurrent requests with the same key can both
"not find the key" and both execute - defeating the
purpose. Use a database unique constraint on the key
to enforce atomicity.

**Level 4 - Why it was designed this way (senior/staff):**
Idempotency keys implement exactly-once semantics over
an at-least-once delivery network. This is the CAP
theorem in practice: to achieve strong consistency
(exactly-once) over an unreliable network, you must
store state (the processed key). The state storage
IS the consistency mechanism. It is not optional -
"I'll implement retries without idempotency and hope
for the best" is not an acceptable design for any
operation with financial or irreversible side effects.

**Level 5 - Mastery (distinguished engineer):**
Distributed databases (Kafka, Cassandra) face the same
problem at the storage layer. Kafka's idempotent producer
(enable.idempotence=true) works exactly the same way:
the producer assigns a sequence number (idempotency key)
to each message. The broker records the highest sequence
number per producer partition. If a message arrives
with a sequence number ≤ the stored value, it is a
duplicate and is silently discarded. Kafka's transactional
producers extend this to cross-partition exactly-once
semantics. The key insight: exactly-once anywhere in
a distributed system requires idempotency at both
the network and storage layers.

---

### ⚙️ How It Works (Mechanism)

**Idempotency store with atomic check-and-execute:**

```
┌──────────────────────────────────────────────────────┐
│ IDEMPOTENCY STORE FLOW                              │
│                                                      │
│  Request: POST /payments                            │
│  Header: Idempotency-Key: a1b2-c3d4-e5f6           │
│                                                      │
│  1. SELECT * FROM idempotency_store                 │
│     WHERE key = 'a1b2-c3d4-e5f6'                  │
│                                                      │
│     Found → Return stored response (no execution)   │
│                                                      │
│     Not found → BEGIN TRANSACTION:                  │
│       INSERT INTO idempotency_store                 │
│         (key, status) = (key, 'in_progress')        │
│       Execute operation (charge card)               │
│       UPDATE idempotency_store                      │
│         SET status='done', result=<response>        │
│         WHERE key=...                               │
│       COMMIT                                        │
│                                                      │
│  2. Return response to client                       │
│                                                      │
│  If concurrent request with same key arrives        │
│  during execution:                                  │
│  → See 'in_progress' status → wait, then return    │
│    completed result when done                       │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Idempotency key implementation (server-side)**
```python
import uuid
import json
from dataclasses import dataclass
from typing import Optional
import redis
import psycopg2

r = redis.Redis(host="redis", port=6379)

@dataclass
class IdempotencyResult:
    found: bool
    response: Optional[dict] = None

def check_idempotency(key: str,
                       request_fingerprint: str) -> IdempotencyResult:
    """Check if this key has been processed before."""
    data = r.hgetall(f"idem:{key}")
    if not data:
        return IdempotencyResult(found=False)

    # Verify request fingerprint matches original
    stored_fp = data.get(b"fingerprint", b"").decode()
    if stored_fp != request_fingerprint:
        raise ValueError(
            "Idempotency key reused with different request body"
        )

    response = json.loads(data[b"response"])
    return IdempotencyResult(found=True, response=response)

def store_idempotency_result(
        key: str,
        request_fingerprint: str,
        response: dict,
        ttl_seconds: int = 86400):
    """Store result for future duplicate detection."""
    r.hset(f"idem:{key}", mapping={
        "fingerprint": request_fingerprint,
        "response": json.dumps(response)
    })
    r.expire(f"idem:{key}", ttl_seconds)

# Usage in payment endpoint:
from flask import Flask, request, jsonify
import hashlib

app = Flask(__name__)

@app.route("/payments", methods=["POST"])
def create_payment():
    idempotency_key = request.headers.get("Idempotency-Key")
    if not idempotency_key:
        return jsonify({"error": "Idempotency-Key required"}), 400

    # Request fingerprint: hash of body + method + endpoint
    body = request.get_data()
    fingerprint = hashlib.sha256(body).hexdigest()

    # Check for duplicate
    result = check_idempotency(idempotency_key, fingerprint)
    if result.found:
        return jsonify(result.response), 200  # Return cached result

    # Execute new payment
    payment_data = request.json
    charge = charge_stripe(
        amount=payment_data["amount"],
        currency=payment_data["currency"]
    )
    response = {
        "charge_id": charge.id,
        "status": charge.status,
        "amount": charge.amount
    }

    # Store result before returning
    store_idempotency_result(idempotency_key, fingerprint, response)
    return jsonify(response), 201
```

**Example 2 - Client-side idempotency key management**
```python
import uuid
import time
import requests
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class PendingPayment:
    """Tracks an in-flight payment for retry safety."""
    idempotency_key: str = field(
        default_factory=lambda: str(uuid.uuid4()))
    customer_id: str = ""
    amount: int = 0
    status: str = "pending"
    response: Optional[dict] = None

def submit_payment_safely(
        customer_id: str, amount: int) -> dict:
    """
    Safe payment submission with retry.
    Generate idempotency key BEFORE first attempt.
    Retry with SAME key on failure.
    """
    payment = PendingPayment(
        customer_id=customer_id, amount=amount)

    # Persist before sending (survives client crash/restart)
    save_pending_payment(payment)

    max_retries = 3
    backoff = 1.0

    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://api.payment.com/payments",
                json={"customer_id": customer_id,
                       "amount": amount},
                headers={
                    "Idempotency-Key": payment.idempotency_key
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            # Mark payment as complete
            payment.status = "complete"
            payment.response = result
            save_pending_payment(payment)
            return result

        except (requests.Timeout, requests.ConnectionError):
            if attempt == max_retries - 1:
                raise
            # Retry with SAME idempotency key - safe
            time.sleep(backoff)
            backoff *= 2  # exponential backoff
```

---

### ⚖️ Comparison Table

| Guarantee | Mechanism | Use Case | Idempotency Needed |
|---|---|---|---|
| **At-most-once** | No retry on failure | Fire-and-forget logs | No |
| **At-least-once** | Retry on failure | Email delivery, webhooks | Yes (server deduplicates) |
| **Exactly-once** | At-least-once + idempotency | Payments, order submission | Yes (required) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| GET requests need idempotency keys | GET is inherently idempotent (same response for same request). Idempotency keys are for non-idempotent operations (POST, sometimes PATCH). |
| Idempotency means you can retry forever | The idempotency store has a TTL (24 hours or 7 days). After the TTL, a retry with the same key will be treated as a new request. Clients should not retry indefinitely; use exponential backoff with a reasonable max retry window. |
| Storing the key in the DB is enough | The idempotency check AND the operation execution must be atomic. If the check and execution happen in separate transactions, two concurrent requests with the same key can both pass the check and both execute. Use a database unique constraint or Redis SET NX (set-if-not-exists) for atomicity. |

---

### 🚨 Failure Modes & Diagnosis

**Race Condition: Concurrent Duplicate Requests**

**Symptom:**
Two API servers receive the same request (with same
idempotency key) at the exact same time. Both check
the idempotency store at t=0: neither finds the key.
Both execute the operation. Two charges occur.

**Root Cause:**
The idempotency check and execution were not atomic.
Two concurrent requests passed the "not found" check
before either had stored its result.

**Fix:**
```python
# Use Redis SETNX (set-if-not-exists) for atomicity
# SETNX is atomic: only one caller succeeds

def process_with_idempotency_atomic(
        key: str, execute_fn) -> dict:
    """
    SETNX ensures only one execution happens,
    even under concurrent duplicate requests.
    """
    lock_key = f"idem_lock:{key}"
    result_key = f"idem_result:{key}"

    # Check if result already exists
    existing = r.get(result_key)
    if existing:
        return json.loads(existing)

    # Try to acquire lock (atomic)
    # NX = only set if not exists
    # EX = expire in 60 seconds (prevent deadlock)
    acquired = r.set(lock_key, "1", nx=True, ex=60)
    if not acquired:
        # Another thread is executing; wait and return result
        for _ in range(60):  # wait up to 60s
            time.sleep(1)
            result = r.get(result_key)
            if result:
                return json.loads(result)
        raise TimeoutError("Concurrent execution timeout")

    # Only ONE caller reaches here
    try:
        result = execute_fn()
        r.setex(result_key, 86400, json.dumps(result))
        return result
    finally:
        r.delete(lock_key)

# Pattern: SETNX for distributed lock +
# separate result key for caching response
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Horizontal vs Vertical Scaling` - idempotency keys
  are necessary once requests are load-balanced across
  multiple servers (any server may receive the retry)

**Builds On This (learn these next):**
- `Distributed Locks` - used to implement atomic
  idempotency checks under concurrency
- `Saga Pattern` - uses idempotency keys for each step
  in a distributed transaction

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Unique client-generated UUID per         │
│               │ request. Server returns cached result    │
│               │ on duplicate (same key). Execute once.  │
├───────────────┼──────────────────────────────────────────┤
│ RULE          │ Generate key BEFORE sending request.     │
│               │ Retry with SAME key (not a new UUID).   │
├───────────────┼──────────────────────────────────────────┤
│ SERVER-SIDE   │ Check key → store → execute → store     │
│               │ result. Atomic: DB unique constraint     │
│               │ or Redis SETNX.                          │
├───────────────┼──────────────────────────────────────────┤
│ TTL           │ 24 hours (Stripe) to 7 days.            │
│               │ After TTL: new execution on same key.   │
├───────────────┼──────────────────────────────────────────┤
│ FINGERPRINT   │ Hash request body with key.              │
│               │ Reject key reuse with different body.   │
├───────────────┼──────────────────────────────────────────┤
│ KAFKA         │ Producer sequence number = idempotency   │
│               │ key. enable.idempotence=true            │
├───────────────┼──────────────────────────────────────────┤
│ ONE-LINER     │ "At-least-once delivery +               │
│               │  idempotency = exactly-once semantics." │
├───────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE  │ Distributed Locks → Saga Pattern        │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Client generates UUID before request; retries use
   the SAME key. Server checks "seen this key?" before
   executing. Found = return cached result. Not found
   = execute and store result.
2. The check + execute must be atomic. Two concurrent
   requests with the same key must not both execute.
   Use DB unique constraint or Redis SETNX.
3. Idempotency keys apply everywhere operations have
   side effects: payments, order submission, email
   sends, webhook processing. Any at-least-once
   delivery channel requires idempotency at the consumer.

**Interview one-liner:**
"An idempotency key is a unique UUID generated by the client before
sending a mutating request. The server stores key → result after
first execution. On retry with the same key, the server returns
the stored result without re-executing. This makes any operation
safe to retry - critical for payments, order submission, or any
irreversible action over an unreliable network. Implementation
requirements: (1) client generates key before sending, (2) server
stores key atomically with execution (DB unique constraint or Redis
SETNX to handle concurrent duplicates), (3) TTL on stored results
(24h-7 days), (4) request fingerprinting to reject key reuse with
different request bodies. This is how exactly-once semantics are
achieved over at-least-once delivery infrastructure."
