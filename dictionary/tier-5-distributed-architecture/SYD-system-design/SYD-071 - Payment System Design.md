---
id: SYD-071
title: Payment System Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-001, SYD-016, SYD-059
used_by: ""
related: SYD-001, SYD-016, SYD-059, SYD-058, SYD-017
tags:
  - architecture
  - payments
  - system-design
  - advanced
  - distributed
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 71
permalink: /syd/payment-system-design/
---

# SYD-071 - Payment System Design

⚡ TL;DR - Payment systems have the most severe
correctness requirements of any distributed system:
a double charge or lost payment is a legal, regulatory,
and customer trust catastrophe. Five design pillars:
(1) Idempotency keys - every payment request carries
a unique key, so retries never create duplicate charges;
(2) Exactly-once semantics - debit and credit must both
happen or neither (atomic transaction or saga with
compensating transactions); (3) Audit log / ledger -
every state change is immutable, append-only, forever;
(4) Strong consistency - financial balances require
serializable isolation, not eventual consistency;
(5) Reconciliation - automated daily reconciliation
against the payment processor to catch any discrepancies
between your records and theirs.

| #071 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | System Design - Core (Reliability), Distributed Transactions, Event Sourcing | |
| **Related:** | Core System Design, Distributed Transactions, Event Sourcing, CQRS, Database Internals | |

---

### 🔥 The Problem This Solves

User clicks "Pay $99." The request reaches your payment
service. The service calls Stripe to charge the card.
Stripe charges the card. The HTTP response times out
before your server receives "success." Your server
retries. Stripe charges the card AGAIN. User is charged
$198 for a $99 purchase. This is a double-charge: a
critical payment bug. The solution is idempotency keys:
a unique ID that tells Stripe "this is the same request
you already processed." Stripe returns the original
result instead of processing again.

---

### 📘 Textbook Definition

**Payment system:** A distributed system that transfers
monetary value between parties reliably, atomically,
and with exactly-once semantics and full audit trail.

**Idempotency key:** A unique client-generated token
attached to a payment request. If the same key is
submitted twice, the payment processor returns the
first result without charging again.

**Double-spend:** A bug where the same money is used
more than once: a debit that fails after a credit, or
a charge that succeeds but is not recorded.

**Distributed ledger:** An immutable, append-only
record of all financial events (debits, credits,
refunds). Each entry records: amount, parties,
timestamp, and resulting balance.

**Reconciliation:** The process of comparing your
internal payment records against external payment
processor records to detect discrepancies, missing
records, or unauthorized transactions.

**PCI DSS:** Payment Card Industry Data Security Standard.
Compliance requirements for systems that handle credit
card data. Relevant: never store raw card numbers;
use tokenization. Annual audits.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Payments = idempotency + atomicity + immutable ledger.
One charge, recorded once, auditable forever.

**One analogy:**
> A bank check system:
>
> Without idempotency: writing a check and accidentally
> sending it twice → bank cashes it twice.
> With idempotency: each check has a unique check number.
> Bank cashes a check number only once. Second
> presentment of same number: rejected.
>
> Audit log: the bank's ledger records every transaction
> permanently. "Show me all transactions for account X
> in March 2024": the ledger has it, immutably.
>
> Reconciliation: at end of day, compare your check
> register (internal records) against bank statement
> (external records). Any mismatch = investigate.

**One insight:**
In payment systems, **eventual consistency is almost
never acceptable for balances.** A bank account balance
showing $1,000 when the actual balance is $100 (due
to a replication lag) can cause catastrophic overcharges.
All read-modify-write operations on balances must use
serializable database transactions or optimistic locking
with conflict detection. The performance cost of
serializable isolation is acceptable for payments;
the correctness cost of eventual consistency is not.

---

### 🔩 First Principles Explanation

**IDEMPOTENCY IMPLEMENTATION:**
```
Problem: network retries may replay the same request.
At-most-once: the payment may be lost.
At-least-once: the payment may be duplicated.
Exactly-once: the payment executes precisely once.

HOW TO IMPLEMENT:

1. Client generates a UUID before making the request.
   This is the idempotency key.

2. Client sends: POST /payments
   Headers: Idempotency-Key: 550e8400-e29b-41d4-a716-...
   Body: {amount: 99.00, currency: "USD", ...}

3. Server: look up the idempotency key in DB.
   Not found: process payment, store result with key.
   Found: return stored result (skip processing).
   
4. Client retry (same key): server returns stored result.
   Stripe never sees duplicate request.

DB Schema:
  idempotency_keys (
    key           VARCHAR(255) PRIMARY KEY,
    response_code INT,
    response_body JSONB,
    expires_at    TIMESTAMP
  )
  
Race condition: two concurrent requests with same key.
  Fix: INSERT ... ON CONFLICT DO NOTHING (PostgreSQL)
  or SELECT FOR UPDATE to serialize.
  Only one thread processes; other gets stored result.
```

**PAYMENT STATE MACHINE:**
```
Payments are not boolean (success/fail).
They have a lifecycle that must be tracked:

CREATED → PENDING → PROCESSING → COMPLETED
                              → FAILED
                              → CANCELLED
COMPLETED → REFUNDING → REFUNDED
                     → REFUND_FAILED

Rules:
  CREATED: idempotency key stored. Not yet sent to processor.
  PENDING: sent to processor. Awaiting response.
  PROCESSING: processor is working on it (async).
  COMPLETED: processor confirmed success.
  FAILED: processor declined or error occurred.
  
Outbox pattern (PENDING → PROCESSING):
  Problem: save to DB and send to Stripe. If DB succeeds
  and Stripe call times out: PENDING forever. Must retry.
  
  Solution (Transactional Outbox):
    1. BEGIN TRANSACTION
    2. INSERT payment (status=CREATED)
    3. INSERT outbox_events (type=INITIATE_PAYMENT, ...)
    4. COMMIT
    5. Background worker: poll outbox_events, call Stripe.
    6. On Stripe success: UPDATE payment status=COMPLETED,
       DELETE from outbox_events (or mark processed).
    
    If worker crashes between 5 and 6: restart replays
    the Stripe call. With idempotency key: safe to retry.
    
Webhook from Stripe (async confirmation):
  Stripe sends POST /webhooks/stripe on success/failure.
  Store the raw webhook event (for replay/debugging).
  Validate signature: HMAC-SHA256 using webhook secret.
  Process idempotently: same event_id → skip if processed.
  Update payment status based on event type.
```

**DOUBLE-ENTRY BOOKKEEPING (LEDGER):**
```
Every financial transaction involves two ledger entries:
  A debit (money leaving an account) and
  A credit (money entering an account).
  
Sum of all debits = sum of all credits (always).
This is the invariant. If it breaks: bug.

Schema (simplified):
  ledger_entries (
    id          BIGINT PRIMARY KEY (snowflake ID),
    account_id  BIGINT,
    amount      NUMERIC(18,2),  -- positive=credit, negative=debit
    currency    CHAR(3),
    type        VARCHAR(50),    -- PAYMENT, REFUND, FEE
    reference   VARCHAR(255),   -- payment_id foreign key
    created_at  TIMESTAMP,
    -- No update or delete on this table. Ever.
  )
  
Balance = SUM(amount) WHERE account_id = X

Why immutable entries (no update/delete)?
  Audit trail: every change is traceable.
  Debugging: "show me the state at any point in time."
  Fraud detection: catch unauthorized changes.
  Regulatory: financial records must be immutable
  (SOX, PCI DSS). Delete = compliance violation.

Account balance query:
  SELECT SUM(amount) FROM ledger_entries
  WHERE account_id = 123 AND currency = 'USD';
  
  Or: maintain a materialized balance (separate table),
  updated atomically with each ledger entry insertion.
  More efficient for frequent balance reads.
```

**RECONCILIATION:**
```
Nightly reconciliation job:

1. Pull all payments from Stripe (CSV export or API).
2. Pull all payments from your DB for same date range.
3. Match by: stripe_payment_id / external_reference.
4. Identify discrepancies:
   - In Stripe but not in your DB: potential data loss.
   - In your DB but not in Stripe: phantom payment.
   - Amount mismatch: error or rounding issue.
   - Status mismatch: your DB shows COMPLETED,
     Stripe shows FAILED → refund may be needed.
5. Alert on any discrepancy.
6. Human review + automated compensation transactions.

Frequency:
  Full reconciliation: daily (previous day's payments).
  Real-time reconciliation: Stripe webhooks update DB
  immediately. Daily reconciliation catches any misses.
```

---

### 🧪 Thought Experiment

**The Saga Pattern for Payment**

Scenario: Order placement involving 3 services.
  1. Payment Service: charge $99 from customer card.
  2. Inventory Service: reserve 1 unit of product.
  3. Order Service: create order record.

Local transaction per service. No distributed transaction.

Saga (choreography):
  1. OrderService publishes OrderCreated event.
  2. PaymentService: charges card. Publishes PaymentCompleted.
  3. InventoryService: reserves item. Publishes ItemReserved.
  4. OrderService: marks order as CONFIRMED.

On failure at step 3 (item out of stock):
  InventoryService publishes ReservationFailed.
  PaymentService listens: compensates by refunding card.
  OrderService: marks order CANCELLED.

Key: compensating transactions must be idempotent.
If PaymentService crashes after refunding but before
marking the saga as done: the refund replay must be safe
(refund already processed → return existing result).

---

### 🧠 Mental Model / Analogy

> A payment system is like an armored car service:
>
> Idempotency key: each shipment has a unique manifest
> number. If the manifest is submitted twice, the second
> is rejected (already shipped).
>
> Ledger: every transfer is logged in an immutable
> manifest book. No entries are erased - ever.
> Corrections are new entries, not overwrites.
>
> Reconciliation: end-of-day: armored car company
> compares their pickup/delivery log against your
> shipping manifest. Any mismatch investigated.
>
> State machine: package is either RECEIVED, IN_TRANSIT,
> DELIVERED, or RETURNED. Never in an undefined state.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A payment system handles money transfers. The most
important thing: make sure payments happen exactly
once (not zero times, not twice). Every payment is
recorded permanently. The system can prove every
dollar that moved, when, and why.

**Level 2 - How to use it (junior developer):**
Use Stripe/Braintree/PayPal SDKs; don't handle raw
credit cards (PCI DSS is complex). Send an idempotency
key with every payment request. On timeout: retry with
the same idempotency key. Store the payment ID returned
by the processor. Handle webhooks for async status
updates. Never store raw card numbers.

**Level 3 - How it works (mid-level engineer):**
Idempotency key: UUID generated client-side, sent in
header, stored in DB. If same key received twice:
return stored result, skip processing. State machine:
CREATED → PENDING → COMPLETED/FAILED. Transactional
outbox: write payment + outbox event in same DB
transaction; background worker calls Stripe; webhook
updates status. Ledger: immutable append-only table
(double-entry). Nightly reconciliation against Stripe.

**Level 4 - Why it was designed this way (senior/staff):**
The core tension in payment systems: reliability
(availability) vs. correctness (consistency). CAP
theorem says you can't have both during a partition.
Payment systems choose consistency: during a network
partition, reject the transaction rather than risk
double-charging. This is CP, not AP. Strong consistency
(serializable isolation) on balance reads prevents
TOCTOU (time-of-check-time-of-use) race conditions.
The Transactional Outbox pattern solves the "dual write
problem" (write to DB AND external API atomically): by
making the external call a DB write first (outbox event),
both operations participate in the same ACID transaction.

**Level 5 - Mastery (distinguished engineer):**
Stripe's payment architecture (2012-2023) evolved around
one core insight: external payment processing is the
only truly external dependency, and it must be treated
as unreliable (timeouts, retries, duplicate detection).
Their public API's idempotency key spec became the
industry standard. Internally, Stripe uses MySQL with
strong consistency for payment records, supplemented
by Redis for idempotency key storage (fast lookup).
Uber's payment system uses a distributed ledger with
optimistic concurrency control on driver/rider accounts:
each balance update carries a version number; a concurrent
update fails with a conflict error and must retry. This
eliminates the need for database-level serializable
isolation (which is expensive at scale) while maintaining
correctness for most cases.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ PAYMENT REQUEST FLOW                                │
│                                                      │
│ 1. Client: generate UUID idempotency key           │
│ 2. POST /payments {amount} + Idempotency-Key: UUID │
│ 3. API: check idempotency_keys DB                 │
│    Found: return cached response                  │
│    Not found: continue                            │
│ 4. BEGIN TRANSACTION                              │
│    INSERT payment (status=CREATED)               │
│    INSERT outbox_event (INITIATE_PAYMENT)        │
│    INSERT idempotency_key (UUID, PENDING)        │
│    COMMIT                                         │
│ 5. Background worker polls outbox_events:        │
│    Call Stripe API (with same UUID as ref)       │
│ 6. Stripe: charge card.                          │
│    Stripe sends webhook: payment.succeeded       │
│ 7. Webhook handler:                              │
│    UPDATE payment status=COMPLETED              │
│    INSERT ledger_entry (debit)                  │
│    INSERT ledger_entry (credit)                 │
│    UPDATE idempotency_key = COMPLETED           │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Idempotency key implementation (Python)**
```python
import uuid
import hashlib
from datetime import datetime, timedelta
import json

def create_payment(
        user_id: int,
        amount_cents: int,
        currency: str,
        idempotency_key: str) -> dict:
    """
    Process a payment with idempotency guarantee.
    Safe to retry: same key returns same result.
    """
    # 1. Look up existing result for this idempotency key
    existing = db.query_one(
        "SELECT response_code, response_body "
        "FROM idempotency_keys "
        "WHERE key = %s AND user_id = %s "
        "AND expires_at > NOW()",
        [idempotency_key, user_id]
    )
    if existing:
        # Already processed: return cached result
        return json.loads(existing['response_body'])
    
    # 2. Process payment (with optimistic lock on key)
    try:
        # Atomic insert: fails if key already exists
        db.execute(
            "INSERT INTO idempotency_keys "
            "(key, user_id, status, expires_at) "
            "VALUES (%s, %s, 'processing', %s) "
            "ON CONFLICT (key) DO NOTHING",
            [idempotency_key, user_id,
             datetime.utcnow() + timedelta(days=1)]
        )
        
        # 3. Call payment processor
        stripe_result = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency,
            # Use our idempotency key for Stripe too:
            idempotency_key=idempotency_key,
        )
        
        # 4. Record payment
        payment_id = db.execute(
            "INSERT INTO payments "
            "(user_id, amount, currency, "
            " stripe_id, status) "
            "VALUES (%s, %s, %s, %s, 'completed') "
            "RETURNING id",
            [user_id, amount_cents, currency,
             stripe_result['id']]
        )
        
        result = {
            "payment_id": payment_id,
            "status": "completed",
            "stripe_id": stripe_result['id']
        }
        
        # 5. Store result for future idempotency checks
        db.execute(
            "UPDATE idempotency_keys "
            "SET status='completed', "
            "response_code=200, "
            "response_body=%s "
            "WHERE key=%s",
            [json.dumps(result), idempotency_key]
        )
        return result
        
    except stripe.error.CardError as e:
        result = {"status": "failed", "error": str(e)}
        db.execute(
            "UPDATE idempotency_keys "
            "SET status='failed', response_code=402, "
            "response_body=%s WHERE key=%s",
            [json.dumps(result), idempotency_key]
        )
        return result

# Client usage: always generate key before attempting.
def place_order(user_id: int, cart: dict) -> dict:
    # Generate idempotency key once per order attempt
    idempotency_key = str(uuid.uuid4())
    
    for attempt in range(3):
        try:
            # Same key on retry: no double charge
            result = create_payment(
                user_id=user_id,
                amount_cents=cart['total_cents'],
                currency="USD",
                idempotency_key=idempotency_key
            )
            return result
        except TimeoutError:
            # Retry with SAME idempotency key
            continue  # Loop retries with same key
    
    raise Exception("Payment failed after 3 attempts")
```

**Example 2 - Immutable ledger entries**
```python
from decimal import Decimal

def record_payment_in_ledger(
        payment_id: int,
        payer_account_id: int,
        payee_account_id: int,
        amount: Decimal,
        currency: str):
    """
    Double-entry bookkeeping.
    Every payment creates two ledger entries.
    Entries are NEVER updated or deleted.
    """
    with db.transaction():
        # Debit: money leaves payer
        db.execute(
            "INSERT INTO ledger_entries "
            "(account_id, amount, currency, "
            " type, reference_id) "
            "VALUES (%s, %s, %s, 'PAYMENT_DEBIT', %s)",
            [payer_account_id, -amount, currency,
             payment_id]
        )
        # Credit: money enters payee
        db.execute(
            "INSERT INTO ledger_entries "
            "(account_id, amount, currency, "
            " type, reference_id) "
            "VALUES (%s, %s, %s, 'PAYMENT_CREDIT', %s)",
            [payee_account_id, amount, currency,
             payment_id]
        )
        # Update materialized balance (atomic with entries)
        db.execute(
            "UPDATE accounts "
            "SET balance = balance - %s "
            "WHERE id = %s AND balance >= %s",
            [amount, payer_account_id, amount]
        )
        db.execute(
            "UPDATE accounts SET balance = balance + %s "
            "WHERE id = %s",
            [amount, payee_account_id]
        )
    
    # Verify invariant: sum of all ledger entries = 0
    # (debit + credit cancel out) -- run as audit
```

---

### ⚖️ Comparison Table

| Consistency Model | Payment Use | Risk | Example |
|---|---|---|---|
| **Eventual consistency** | NOT suitable for balances | Double-spend, incorrect balance | NoSQL-only balance store |
| **Serializable isolation** | Required for balances | Performance cost, but safe | PostgreSQL SERIALIZABLE txn |
| **Optimistic locking** | Suitable for high-throughput | Conflict retries under contention | Version field on accounts |
| **Distributed saga** | For cross-service operations | Requires compensating transactions | Order + Payment + Inventory |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Idempotency key prevents all duplicate payments | An idempotency key prevents duplicates for the same key. If the client generates a new key on retry (e.g., a bug where `uuid.uuid4()` is called inside the retry loop), the duplicate charge occurs. The key must be generated ONCE before the first attempt and reused on all retries. Store it in the order record before making the first payment attempt. |
| Stripe webhooks are delivered exactly once | Stripe delivers webhooks at-least-once. The same webhook event may arrive multiple times (retry on timeout). Your webhook handler must be idempotent: check if `event.id` has already been processed before processing again. Use `INSERT ... ON CONFLICT DO NOTHING` with the Stripe event ID as the unique key. |
| Strong consistency is too slow for payments | PostgreSQL with serializable isolation handles 10,000+ transactions per second on modern hardware. Payment systems at Stripe, PayPal, and Square all use SQL databases with strong consistency at scale. The bottleneck is rarely the database isolation level; it's network round-trips to the payment processor and card network. Proper connection pooling and read replicas for non-balance queries are far more impactful optimizations. |

---

### 🚨 Failure Modes & Diagnosis

**Ghost Payments: Charged but Not Recorded**

**Symptom:**
Reconciliation job finds payments in Stripe that are
not in the database. Users are charged but receive
no confirmation. Support tickets: "I was charged but
no order was created."

**Root Cause:**
Classic dual-write problem:
  1. Service calls Stripe. Stripe charges card. Returns success.
  2. Service attempts to insert payment to DB.
  3. DB INSERT fails (timeout, network error, disk full).
  4. Payment is in Stripe; not in DB. Ghost payment.

**Fix - Transactional Outbox:**
```python
def initiate_payment_safe(payment_data: dict) -> int:
    """
    Transactional outbox: write to DB first.
    Background worker calls Stripe.
    If worker fails: retry. Stripe idempotency = safe.
    """
    with db.transaction():
        # 1. Insert payment (pending state)
        payment_id = db.execute(
            "INSERT INTO payments "
            "(user_id, amount, status) "
            "VALUES (%s, %s, 'PENDING') "
            "RETURNING id",
            [payment_data['user_id'],
             payment_data['amount']]
        )
        # 2. Insert outbox event in SAME transaction
        db.execute(
            "INSERT INTO outbox_events "
            "(type, payload, status) "
            "VALUES ('INITIATE_PAYMENT', %s, 'PENDING')",
            [json.dumps({
                "payment_id": payment_id,
                "amount": payment_data['amount'],
                "idempotency_key": payment_data['key']
            })]
        )
        # Both or neither: ACID guarantee.
        return payment_id
    # Background worker polls outbox_events,
    # calls Stripe, updates payment status.
    # If worker crashes: restart replays Stripe call.
    # Stripe idempotency key: no duplicate charge.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `System Design - Core` - reliability patterns,
  retries, idempotency at system level
- `Distributed Transactions` - saga pattern for
  cross-service payment flows
- `Event Sourcing` - append-only event log = ledger
  is event sourcing applied to financial data

**Builds On This (learn these next):**
- `CQRS` - separate read model (account balance view)
  from write model (ledger events)
- `Database Internals` - understanding serializable
  isolation, optimistic locking for correctness

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ IDEMPOTENCY │ UUID key generated once. Reuse on retry. │
│             │ Server returns stored result on replay.  │
├─────────────┼──────────────────────────────────────────  │
│ STATE MACH  │ CREATED→PENDING→COMPLETED/FAILED         │
│             │ Outbox: write DB event → worker→Stripe.  │
├─────────────┼──────────────────────────────────────────  │
│ LEDGER      │ Immutable append-only. No UPDATE/DELETE. │
│             │ Double-entry: debit + credit every txn.  │
├─────────────┼──────────────────────────────────────────  │
│ CONSISTENCY │ Serializable isolation for balances.    │
│             │ Eventual = double-spend risk.           │
├─────────────┼──────────────────────────────────────────  │
│ RECON       │ Daily: compare DB vs Stripe CSV.        │
│             │ Any mismatch = ghost payment / data loss│
├─────────────┼──────────────────────────────────────────  │
│ WEBHOOK     │ Stripe at-least-once delivery.          │
│             │ Handler: idempotent on event_id.        │
├─────────────┼──────────────────────────────────────────  │
│ ONE-LINER   │ "Idempotency key + outbox + immutable  │
│             │  ledger + daily reconciliation."        │
├─────────────┼──────────────────────────────────────────  │
│ NEXT        │ File Storage System Design               │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Generate one idempotency key per payment attempt
   BEFORE making the first call. Reuse the same key
   on all retries. Never generate a new key on retry.
   Pass the key to Stripe/Braintree as well so they
   de-duplicate on their side too.
2. Use the Transactional Outbox pattern: write the
   payment intent and the outbox event in the same DB
   transaction. Background worker calls Stripe. If it
   fails and restarts, idempotency key makes the retry safe.
   Eliminates ghost payments (charged but not recorded).
3. Immutable ledger (append-only). Balances = SUM of all
   entries. No UPDATE or DELETE ever on ledger records.
   Run nightly reconciliation against processor records
   to catch any discrepancy your code missed.

**Interview one-liner:**
"Payment design: idempotency key (UUID generated once, reused on retries) prevents
double charges; Transactional Outbox (write payment + outbox event in same DB txn;
worker calls Stripe) prevents ghost payments. State machine: CREATED→PENDING→COMPLETED.
Ledger: immutable append-only double-entry (debit+credit per transaction, never UPDATE
or DELETE). Strong consistency (serializable isolation): eventually-consistent balances
risk double-spend. Nightly reconciliation against Stripe CSV to catch discrepancies.
Webhooks: idempotent handler (check event_id before processing)."
