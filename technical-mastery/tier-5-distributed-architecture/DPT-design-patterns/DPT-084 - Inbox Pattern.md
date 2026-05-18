---
id: DPT-084
title: Inbox Pattern
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-038, DPT-065
used_by: []
related: DPT-038, DPT-039, DPT-040, DPT-085, DPT-065
tags:
  - pattern
  - messaging
  - advanced
  - idempotency
  - at-least-once
  - microservices
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 84
permalink: /technical-mastery/design-patterns/inbox-pattern/
---

⚡ TL;DR - The Inbox Pattern ensures exactly-once processing
of incoming messages by storing each received message
in a local "inbox" table before processing it. Duplicate
messages (from at-least-once delivery) are detected
by checking the message ID against the inbox table
and rejected before business logic runs.

| #84 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-038, DPT-065 | |
| **Used by:** | N/A | |
| **Related:** | DPT-038, DPT-039, DPT-040, DPT-085, DPT-065 | |

---

### 🔥 The Problem This Solves

**THE AT-LEAST-ONCE DELIVERY PROBLEM:**
Message brokers (Kafka, RabbitMQ, SQS) guarantee AT-LEAST-ONCE
delivery. A message may be delivered multiple times:
- Consumer crashes after processing but before ack: redelivery.
- Network timeout during ack: broker delivers again.
- Consumer restart: unacked messages redelivered.

An "OrderPlaced" event is processed twice:
- Warehouse picks items twice.
- Customer is charged twice.
- Two shipments are dispatched.

The consumer has no defense against redelivery. At-least-once
becomes "process multiple times" with data corruption.

**THE INBOX SOLUTION:**
Before processing any message: write its ID to an inbox table.
If the ID already exists: the message is a duplicate - skip.
If the ID is new: process the message and record the result.
The inbox acts as a deduplication mechanism.

---

### 📘 Textbook Definition

The **Inbox Pattern** (also known as the Transactional
Inbox or Idempotent Consumer) is a messaging reliability
pattern:

> Incoming messages are written to a local "inbox" (database
> table) as the FIRST step of processing. Duplicate
> detection is performed against the inbox. Only novel
> messages proceed to business logic processing.

**Key properties:**
- **Idempotent consumption**: any message can be received
  and processed N times with the same effect as processing
  it once.
- **Transactional deduplication**: message storage and
  business logic run in the SAME database transaction.
  If the transaction rolls back: the message ID is not
  recorded; the next delivery will be treated as new.
- **At-least-once becomes effectively-once**: the Inbox
  Pattern converts broker-level at-least-once delivery
  into application-level exactly-once processing.

**Inbox vs Outbox:**
Inbox Pattern: ensures incoming messages are processed
exactly once (consumer side).
Outbox Pattern (DPT-038): ensures outgoing messages
are sent exactly once (publisher side).
They are complementary: Outbox on the sender, Inbox
on the receiver.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Check if you've seen this message ID before. If yes: skip.
If no: record it and process. The check-and-record is
atomic with the business transaction.

**One analogy:**
> A mail room that stamps incoming packages with a
> unique tracking number. If the same package arrives
> twice (delivered twice by mistake), the mail room
> checks the log: "we already stamped #TRK-9281."
> The duplicate is returned without being processed.
>
> The tracking log = the inbox table.
> The stamp = recording the message ID.
> The duplicate check = idempotency enforcement.
> The package content = the business event (order placed,
> payment received, etc.).

---

### 🔩 First Principles Explanation

**THE CORE INVARIANT:**
For any message with ID M:
- First delivery: ID not in inbox → process → save ID in inbox
- Subsequent deliveries: ID in inbox → skip (already processed)

The invariant: "message ID exists in inbox" = "message
has been processed exactly once."

**ATOMICITY REQUIREMENT:**
The inbox write and the business logic must be atomic.
If they are not:
- Insert into inbox THEN process business logic: if
  business logic fails, message ID is recorded but
  processing never happened. Next delivery: duplicate
  check passes, processing skipped. Data lost.
- Process business logic THEN insert into inbox: if
  the insert fails or the consumer crashes between
  processing and insert, next delivery processes again.
  Data processed twice.

**The solution: both operations in ONE database transaction.**
```
BEGIN TRANSACTION
  INSERT INTO inbox (message_id, received_at) --
    idempotency key
  [if duplicate: ROLLBACK, return]
  -- business logic runs here (in same transaction)
  UPDATE orders SET status = 'CONFIRMED' WHERE ...
COMMIT
```
If the transaction commits: inbox has the ID AND business
logic has been applied. If it rolls back: neither happened.
Clean retry on next delivery.

**INBOX CLEANUP:**
Inbox records cannot grow forever. Clean up with a
retention policy: delete inbox records older than the
message broker's maximum redelivery window + buffer.
If the broker will redeliver for at most 7 days:
keep inbox records for 14 days. After 14 days: a duplicate
cannot arrive (broker has given up redelivery).

---

### 🧪 Thought Experiment

**PAYMENT PROCESSED TWICE:**
Event: "PaymentProcessed { id: PMT-789, orderId: 42, amount: 99.99 }"
Consumer: `OrderService` marks order as paid.

Broker delivers PMT-789 at T=0:
1. Check inbox: not found. (New message.)
2. BEGIN TX. Insert PMT-789 into inbox. Mark order 42 as paid. COMMIT.
3. Ack to broker. ✓

Broker redelivers PMT-789 at T=5 (network issue at ack):
1. Check inbox: PMT-789 found! Duplicate detected.
2. Skip processing.
3. Ack to broker. (Acknowledge to prevent further redelivery.)

Order 42 is marked paid exactly once. No double-processing.
Without Inbox Pattern: Order 42 would be marked paid twice
(or trigger a second payment flow).

---

### 🧠 Mental Model / Analogy

> Inbox Pattern = the "seen IDs" set in a distributed system.
>
> Imagine a team receiving work tickets. Each ticket has
> a unique ID. Before a team member starts working on a
> ticket: they check the "in progress" board for that ID.
> If found: someone already handled it - skip.
> If not found: add it to the board, then do the work.
>
> The "in progress" board = the inbox table.
> Adding the ticket ID = the inbox INSERT.
> Doing the work = the business logic.
> The check-and-add = atomic operation (only one person
> can add the ID; others see it and skip).
>
> The database transaction enforces the atomicity.
> Without it: two team members might both check,
> both see "not found," and both start working.

---

### 📶 Gradual Depth - Three Levels

**Level 1 - Basic inbox check:**
For every incoming message: check the `inbox` table for
the message ID. If found: return (already processed).
If not found: process and insert. Both operations in
one transaction. This handles duplicate delivery.

**Level 2 - Transactional inbox:**
Use the same database as business logic. The inbox table
and business table updates are in the SAME transaction.
If business logic throws: inbox record not committed.
Next delivery: treated as new. Safe retry.

**Level 3 - Inbox + Status tracking:**
An enhanced inbox records not just "received" but also
the processing result:
```
inbox_messages (
    message_id     VARCHAR(255) PRIMARY KEY,
    received_at    TIMESTAMP,
    processed_at   TIMESTAMP,
    status         ENUM('RECEIVED', 'PROCESSING',
      'PROCESSED', 'FAILED'),
    error_message  TEXT
)
```
This allows:
- Distinguishing "received but processing failed" from "not received"
- Monitoring: how many messages are in FAILED state?
- Retry dead-letter processing by changing status to RECEIVED
- Audit: proof that message M was processed at time T

---

### ⚙️ How It Works (Mechanism)

```
Inbox Pattern: Message Flow
┌─────────────────────────────────────────────────────────┐
│  BROKER                    CONSUMER                     │
│  (Kafka/RabbitMQ)          (OrderService)               │
│       │                         │                       │
│       │  deliver PMT-789         │                      │
│       │──────────────────────►  │                       │
│       │                         │                       │
│                          ┌──────▼──────────────────┐    │
│                          │ BEGIN TRANSACTION        │   │
│                          │   INSERT inbox(PMT-789)  │   │
│                          │   [IF DUPLICATE: SKIP]   │   │
│                          │   UPDATE order SET paid=T│   │
│                          │ COMMIT                   │   │
│                          └──────┬──────────────────-┘   │
│       │                         │                       │
│       │  ◄── ACK ───────────────┘                       │
│       │                                                 │
│       │  redeliver PMT-789 (network hiccup)             │
│       │──────────────────────►  │                       │
│                          ┌──────▼──────────────────┐    │
│                          │ Check inbox: PMT-789 ✓   │   │
│                          │ DUPLICATE → SKIP         │   │
│                          └──────┬──────────────────-┘   │
│       │  ◄── ACK ───────────────┘  (ack to stop retry)  │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Inbox Pattern with Spring and JPA:**

```java
// Inbox table entity:
@Entity
@Table(name = "inbox_messages")
class InboxMessage {
    @Id
    private String messageId;
    private Instant receivedAt;
    private String status; // PROCESSED or FAILED

    // Constructors, getters omitted for brevity
}

// Repository:
interface InboxMessageRepository
    extends JpaRepository<InboxMessage, String> {
    boolean existsByMessageId(String messageId);
}
```

```java
// Inbox-aware message consumer:
@Service
class OrderEventConsumer {

    private final InboxMessageRepository inboxRepo;
    private final OrderRepository orderRepo;

    // Constructor injection (DIP - DPT-078)
    OrderEventConsumer(InboxMessageRepository inboxRepo,
                       OrderRepository orderRepo) {
        this.inboxRepo = inboxRepo;
        this.orderRepo = orderRepo;
    }

    @KafkaListener(topics = "payment-events")
    @Transactional  // CRITICAL: entire method = one transaction
    public void handlePaymentProcessed(
            PaymentProcessedEvent event) {

        String msgId = event.getMessageId();

        // Step 1: Check inbox for duplicate.
        if (inboxRepo.existsByMessageId(msgId)) {
            log.info("Duplicate message: {}. Skipping.", msgId);
            return; // ack will still be sent; skip processing
        }

        // Step 2: Record in inbox (within same transaction).
        inboxRepo.save(new InboxMessage(
            msgId, Instant.now(), "PROCESSING"));

        // Step 3: Business logic (same transaction).
        Order order = orderRepo.findById(event.getOrderId())
            .orElseThrow();
        order.markAsPaid(event.getAmount());
        orderRepo.save(order);

        // Step 4: Update inbox to PROCESSED.
        inboxRepo.updateStatus(msgId, "PROCESSED");
        // If anything above throws: entire tx rolls back.
        // inbox record NOT committed. Next delivery = fresh attempt.
    }
}
```

---

### 🔥 Failure Scenarios

**INBOX TABLE NOT IN SAME DATABASE:**
```java
// BAD: Inbox in Redis, business logic in MySQL.
if (redis.exists(messageId)) return; // duplicate check
redis.set(messageId, "processed");   // not atomic with below
database.updateOrder(orderId);       // MySQL: different data store

// Failure mode: Redis write succeeds, MySQL write fails.
// Redis says "processed"; MySQL never updated.
// Next delivery: duplicate check in Redis passes. Skip.
// Order: never marked paid. Data lost silently.
```
Fix: both inbox and business logic in the SAME database,
in the SAME transaction.

**MISSING INBOX CLEANUP:**
```
SELECT COUNT(*) FROM inbox_messages;
→ 847,293,401 rows (3 years of messages accumulated)
→ inbox check: 8-second table scan
→ consumer lag: 2 hours behind
```
Fix: add a retention job:
```sql
DELETE FROM inbox_messages
WHERE received_at < NOW() - INTERVAL 14 DAY;
```
Run daily. Keep only within redelivery window + buffer.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Inbox Pattern requires a separate service | The inbox table lives in the SAME database as the consuming service's business data. It is a table, not a service. The entire point is transactional atomicity with business logic |
| Idempotent business logic replaces the Inbox Pattern | Idempotent business logic (DPT-085) is good practice but requires all business operations to be naturally idempotent. Real business logic often is not (triggering a payment, sending a shipment). The Inbox Pattern provides idempotency at the consumer level without requiring each operation to be individually idempotent |
| Inbox Pattern guarantees exactly-once | Inbox Pattern provides exactly-once PROCESSING semantics at the application level. It does not guarantee exactly-once DELIVERY at the broker level. The distinction: the broker delivers at-least-once; the Inbox Pattern ensures the business logic runs at-most-once per unique message ID |
| ACKing after duplicate detection wastes ack | ACKing duplicates is correct. If you NACK a duplicate: the broker will redeliver it. You will check again, find it's a duplicate, NACK again. Infinite loop. Always ACK (or commit offset) for duplicates |

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DEFINITION   │ Store message ID in inbox before         │
│              │ processing. Duplicate = skip.           │
├──────────────┼──────────────────────────────────────────┤
│ ATOMICITY    │ Inbox INSERT + business logic in ONE     │
│              │ database transaction. Non-negotiable.   │
├──────────────┼──────────────────────────────────────────┤
│ SAME DB      │ Inbox table MUST be in same DB as       │
│              │ business data. Different stores: broken. │
├──────────────┼──────────────────────────────────────────┤
│ CLEANUP      │ Delete inbox records outside redelivery │
│              │ window. Daily retention job.            │
├──────────────┼──────────────────────────────────────────┤
│ COMPLEMENTS  │ Outbox Pattern (DPT-038) on sender side │
│              │ Idempotency Pattern (DPT-085) in logic  │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-085: Idempotency Pattern            │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Inbox Pattern = deduplication table for incoming messages.
   Before processing: check if message ID seen before.
   If yes: skip and ack. If no: process + record. The
   check-record-process must be ONE atomic transaction.
2. Same-database atomicity is non-negotiable. Inbox in
   Redis + business logic in MySQL = not atomic = not
   safe. Both must be in the same transactional database.
3. Always ACK duplicates. Sending NACK on a duplicate
   causes infinite redelivery. Acknowledge the message
   (signal "received and handled") even when processing
   is skipped. The broker does not need to know about
   deduplication logic.

