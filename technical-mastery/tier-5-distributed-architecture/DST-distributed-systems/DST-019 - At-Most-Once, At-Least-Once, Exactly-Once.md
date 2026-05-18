---
id: DST-019
title: "At-Most-Once, At-Least-Once, Exactly-Once"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★☆☆
depends_on: DST-003, DST-009, DST-018
used_by: DST-035, DST-055
related: DST-009, DST-018, DST-035
tags:
  - distributed
  - messaging
  - reliability
  - foundational
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 19
permalink: /technical-mastery/distributed-systems/delivery-semantics/
---

⚡ TL;DR - These three delivery semantics define how many
times a message is guaranteed to be delivered: at-most-once
may lose messages, at-least-once may duplicate them, and
exactly-once is expensive to implement and requires
idempotency; most production systems use at-least-once
delivery with idempotent consumers.

---

### 📋 Entry Metadata

| #019 | Category: Distributed Systems | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Network Is Unreliable, Message Passing, Idempotency | |
| **Used by:** | Retry Logic, Saga Pattern, Message Brokers | |
| **Related:** | Message Passing, Idempotency, Retry Logic | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A developer implements an order processing queue. Messages
are sent from the order service to the payment service.
The developer does not consider delivery semantics. When
the payment service is briefly unavailable, the queue
drops messages (at-most-once). Orders are silently lost.
Alternatively, the developer adds retry logic without
idempotency - messages are processed multiple times
(implicit at-least-once without idempotency). Customers
are charged twice. Neither outcome is acceptable. Delivery
semantics make the trade-offs explicit so the right
solution can be designed upfront.

---

### 📘 Textbook Definition

**Delivery semantics** define the guarantee a messaging
system makes about how many times a consumer will process
a given message:

- **At-most-once (AMO)**: Each message is delivered zero
  or one times. The system will never deliver a duplicate,
  but may lose messages. Fire-and-forget.

- **At-least-once (ALO)**: Each message is delivered one
  or more times. The system guarantees delivery, but the
  consumer may process the same message multiple times.
  Requires idempotent consumers.

- **Exactly-once (EO)**: Each message is delivered and
  processed exactly one time. Requires distributed
  coordination between the message broker and the consumer.
  The most expensive guarantee; achieved via transactional
  messaging or idempotent producers + idempotent consumers.

These semantics apply to any message-passing system:
HTTP APIs, message queues (Kafka, RabbitMQ, SQS), event
streams, and RPC frameworks.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Messages can be lost (at-most-once), duplicated (at-least-
once), or guaranteed to arrive exactly once - pick the
trade-off that fits your use case.

**One analogy:**
> Three ways to deliver a letter:
> **At-most-once**: Drop it in the mailbox and walk away.
> It usually arrives. If the mailbox is full, it is lost.
> No acknowledgment from recipient.
> **At-least-once**: Send via certified mail. Sender waits
> for delivery confirmation. If no confirmation, resend.
> The recipient might get two copies if the first
> confirmation was lost.
> **Exactly-once**: Use a notary who holds the letter until
> both sender and recipient sign confirming exactly one
> exchange. Correct but expensive and slow.

**One insight:**
Exactly-once delivery cannot be achieved at the transport
layer alone without application cooperation. Even "exactly-
once" Kafka transactions only guarantee exactly-once at
the Kafka layer - if the consumer crashes after reading
but before processing, the message must be redelivered
(back to at-least-once). True end-to-end exactly-once
requires idempotent consumers combined with broker-level
guarantees.

---

### 🔩 First Principles Explanation

**AT-MOST-ONCE - HOW IT WORKS:**

```
Producer → Broker → Consumer

Protocol:
1. Producer sends message to broker
2. Broker delivers to consumer (no ACK tracking)
3. Consumer processes (or doesn't)

Failure scenarios:
  IF network drops between producer and broker:
    Message is lost. Producer does not retry.
  IF consumer crashes before processing:
    Message is not redelivered.

Result: Some messages may be lost. No duplicates.
```

**AT-LEAST-ONCE - HOW IT WORKS:**

```
Producer → Broker → Consumer → ACK

Protocol:
1. Producer sends message to broker
2. Broker delivers to consumer
3. Consumer sends ACK after processing
4. Broker removes message from queue on ACK

IF consumer crashes before ACK:
  Broker does not receive ACK.
  Broker redelivers message to another consumer.
  Consumer processes message AGAIN (duplicate).

IF network drops ACK (message was processed):
  Broker times out, assumes consumer failed.
  Broker redelivers.
  Consumer processes again (duplicate).

Result: Every message processed at least once.
        May be processed multiple times.
        Requires: idempotent consumer.
```

**EXACTLY-ONCE - HOW IT WORKS:**

```
Two-phase mechanism:
1. Producer sends with a unique sequence number (producer
  ID)
2. Broker deduplicates: if same sequence already stored,
   discard (idempotent producer)
3. Consumer reads message
4. Consumer processes AND commits offset atomically
   (using a transaction)
5. If consumer crashes after process but before commit:
   Message is redelivered on restart.
   Consumer must be idempotent to handle this case.

Kafka implementation:
  Producer: enable.idempotence=true (unique sequence per
    msg)
  Consumer: isolation.level=read_committed (only see
    committed)
  Consumer-to-database: use Kafka transactions or outbox
```

**THE FUNDAMENTAL IMPOSSIBILITY:**

True end-to-end exactly-once across arbitrary systems is
impossible without application-level coordination.
Consider: consumer reads message from Kafka, updates database,
commits Kafka offset. The steps are not atomic. If the
database update succeeds but offset commit fails (or vice
versa), the message is either lost or duplicated on the
next poll. The only solution: make the database update
idempotent (store the Kafka offset in the same database
transaction - an idempotent consumer).

---

### 🧠 Mental Model / Analogy

> Imagine three checkout systems at a store:
>
> **At-most-once**: Cashier swipes your card once. If the
> terminal is slow and times out, nothing is retried.
> Sometimes the payment goes through, sometimes it doesn't.
> No double charges, but sometimes no charge at all.
>
> **At-least-once**: Cashier keeps swiping until the
> terminal confirms. You might see multiple pending charges
> on your statement temporarily. Without idempotency,
> multiple charges stick.
>
> **Exactly-once**: Cashier and the bank coordinate through
> a 2-phase process - reserve funds, confirm, release.
> One charge, always. Slow and requires both parties to
> be available simultaneously.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
When sending a message between systems, three things can
happen: the message is lost, it arrives once, or it arrives
multiple times. Delivery semantics tell you which of these
is possible in a given system, and what you need to do
about it.

**Level 2 - How to use it (junior developer):**
Most message queues (RabbitMQ, SQS, Kafka) use at-least-once
delivery. Assume every message may be delivered more than
once. Design consumers to be idempotent: processing the
same message twice should produce the same result as
processing it once. Track which messages have been processed
using a message ID.

**Level 3 - How it works (mid-level engineer):**
At-least-once works via acknowledgment: the broker holds
a message until the consumer sends an ACK. If the consumer
crashes before ACKing, the broker redelivers. At-most-once
works by sending without ACK tracking - fire and forget.
Exactly-once in Kafka requires: idempotent producer (no
duplicate broker ingestion) + transactional producer (atomic
multi-partition writes) + consumer with committed offset
inside the same transaction as the processed output.

**Level 4 - Why it was designed this way (senior/staff):**
The two generals problem (1975) proves that perfectly
reliable message delivery over an unreliable network is
impossible. At-least-once is the practical choice: guarantee
delivery at the cost of possible duplication, then handle
duplicates at the application layer. This separates concerns:
transport guarantees delivery; application handles semantics.
Exactly-once at the transport layer requires distributed
coordination that adds latency and limits scalability.

**Level 5 - Mastery (distinguished engineer):**
Kafka's "exactly-once semantics" (EOS), introduced in 0.11,
provides idempotent producers and transactional writes at
the broker level. But it is "exactly once within Kafka."
If your consumer reads from Kafka and writes to a PostgreSQL
database, EOS does not cover the Kafka-to-PostgreSQL step.
For true end-to-end exactly-once: use the transactional
outbox pattern (write to database + commit to Kafka in the
same database transaction using the Debezium CDC connector,
which reads the database WAL and produces to Kafka). This
achieves exactly-once semantics at the cost of architectural
complexity and the latency of CDC propagation.

---

### ⚙️ Mechanism - The Three Semantics

**COMPARISON FLOW DIAGRAM:**

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  AT-MOST-ONCE:                                         │
│  Producer → Broker → Consumer                          │
│  (no ACK, no retry)                                    │
│  Risk: message dropped = lost forever                  │
│                                                        │
│  AT-LEAST-ONCE:                                        │
│  Producer → Broker → Consumer → ACK                    │
│  (Broker holds until ACK received)                     │
│  Risk: crash before ACK = redelivery = duplicate       │
│                                                        │
│  EXACTLY-ONCE:                                         │
│  Producer → Broker (idempotent, seq check)             │
│  Broker → Consumer (transactional read)                │
│  Consumer → DB (atomic: process + commit offset)       │
│  Risk: no duplication, but much higher complexity      │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**KAFKA EXACTLY-ONCE CONFIGURATION:**

```
Producer config:
  enable.idempotence=true       ← prevents duplicate sends
  acks=all                      ← all replicas confirm
  transactional.id=my-producer  ← enables transactions

Consumer config:
  isolation.level=read_committed ← only reads committed
    msgs

Consumer-to-DB pattern (atomic):
  Within single Kafka transaction:
  1. Read messages (poll)
  2. Process (compute output)
  3. Write output to DB
  4. Commit Kafka offset
  All steps succeed or all roll back
```

---

### 💻 Code Example

**Implementing At-Least-Once with Idempotent Consumer**

```python
# BAD: Process message without idempotency
def process_payment_message(msg: dict) -> None:
    # No duplicate check
    user_id = msg["user_id"]
    amount = msg["amount"]
    payment_service.charge(user_id, amount)
    # If this consumer crashes after charge but before
    # committing the Kafka offset, the message is
    # redelivered and the user is charged again.
```

```python
# GOOD: Idempotent consumer with message ID tracking
import json
from confluent_kafka import Consumer, KafkaError

def build_consumer():
    return Consumer({
        'bootstrap.servers': 'kafka:9092',
        'group.id': 'payment-processor',
        # Disable auto-commit: control offsets manually
        'enable.auto.commit': False,
    })

def process_payment_message(
    consumer: Consumer,
    msg
) -> None:
    message_id = msg.headers().get('message-id')
    if not message_id:
        # Reject messages without idempotency key
        logger.error(
            f"Message at {msg.offset()} has no message-id"
        )
        return

    payload = json.loads(msg.value())

    with db.begin() as txn:
        # Check for duplicate
        already_processed = txn.execute(
            text(
                "SELECT 1 FROM processed_messages "
                "WHERE message_id = :id"
            ),
            {"id": message_id}
        ).one_or_none()

        if already_processed:
            # Safe to skip: already done
            logger.info(f"Skipping duplicate: {message_id}")
        else:
            # Process the payment
            payment_service.charge(
                user_id=payload["user_id"],
                amount=payload["amount"],
                idempotency_key=message_id
            )
            # Mark as processed IN THE SAME TRANSACTION
            txn.execute(
                text(
                    "INSERT INTO processed_messages "
                    "(message_id, processed_at) "
                    "VALUES (:id, now())"
                ),
                {"id": message_id}
            )

    # Commit Kafka offset AFTER successful DB transaction
    consumer.commit(message=msg, asynchronous=False)
```

**At-Most-Once Use Case (Metrics)**

```python
# At-most-once is appropriate for metrics/telemetry:
# A dropped metrics point is acceptable.
# A duplicate metrics point causes incorrect aggregation.
# Fire-and-forget is the right model.

import socket

def emit_metric_udp(
    name: str,
    value: float,
    tags: dict
) -> None:
    """
    UDP stat emission: at-most-once by design.
    UDP has no delivery guarantee. Acceptable for metrics.
    Missing a datapoint in a time series is tolerable.
    """
    payload =
        f"{name}:{value}|g|#{','.join(f'{k}:{v}' for k,
            v in tags.items())}"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Fire and forget - no error handling needed
    sock.sendto(
        payload.encode('utf-8'),
        ('statsd.internal', 8125)
    )
```

---

### ⚖️ Comparison Table

| Semantic | Delivery | Duplicates | Use When |
|---|---|---|---|
| **At-Most-Once** | Not guaranteed | None | Metrics, logs, telemetry (losing data is OK) |
| **At-Least-Once** | Guaranteed | Possible | Most systems with idempotent consumers |
| **Exactly-Once** | Guaranteed | None | Financial, critical operations, high complexity cost |

| System | Default Semantic | Exactly-Once Support |
|---|---|---|
| **Kafka** | At-least-once | Yes (EOS, since 0.11) |
| **RabbitMQ** | At-least-once | No (application-level only) |
| **Amazon SQS** | At-least-once | No (use idempotent consumers) |
| **SQS FIFO** | At-least-once | Content-based dedup window |
| **HTTP** | None | Application-level with idempotency keys |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Exactly-once is always the best option" | Exactly-once has real cost: higher latency (distributed coordination), reduced throughput, and architectural complexity. For many workloads, at-least-once + idempotent consumer achieves the same result more efficiently. |
| "At-least-once is fine without idempotency" | Without idempotency, at-least-once is at-least-once-and-sometimes-twice (or more). Every consumer using at-least-once delivery must be idempotent. |
| "Kafka guarantees exactly-once end-to-end" | Kafka EOS guarantees exactly-once within Kafka. External consumers (databases, APIs) are outside Kafka's transaction boundary. End-to-end exactly-once requires application-level idempotency. |
| "HTTP is at-most-once" | HTTP has no inherent delivery semantics - it depends on the client. A client that retries on timeout makes HTTP at-least-once. The server's idempotency design determines the effective semantics. |

---

### 🚨 Failure Modes & Diagnosis

**Silent Message Loss (At-Most-Once Without Awareness)**

**Symptom:** A queue-based system processes orders but some
orders are silently not processed. No errors appear in logs.
Revenue is lower than expected. The problem is intermittent.

**Root Cause:** The consumer is configured with at-most-once
delivery (auto-commit offset before processing). If the
consumer crashes after committing the offset but before
processing, the message is considered "consumed" and is
never redelivered.

**Diagnosis:**
```bash
# Kafka: Check consumer group lag
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --describe --group payment-processor

# Look for:
# LAG = 0 (offset committed) but no DB record for that order
# This indicates message was committed but not processed

# Compare:
# Messages published in Kafka topic between time T1 and T2
# Orders created in database between T1 and T2
# If count(kafka_msgs) > count(db_orders): messages were lost
```

**Fix:** Change to manual offset commit. Only commit offset
after successful processing. Accept the risk of at-least-once
(duplicates) and implement idempotent consumers.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `The Network Is Unreliable` - Why delivery guarantees
  are needed
- `Message Passing` - The communication layer where these
  semantics apply
- `Idempotency` - The consumer-side property that makes
  at-least-once equivalent to exactly-once

**Builds On This (learn these next):**
- `Retry Logic with Exponential Backoff` - How to implement
  safe retries using at-least-once delivery
- `Saga Pattern` - Distributed transactions using at-least-
  once messaging with idempotent compensating transactions

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ AT-MOST-ONCE │ Fast, may lose messages. Use: metrics    │
├──────────────┼──────────────────────────────────────────┤
│ AT-LEAST-ONCE│ Reliable, may duplicate. Use: most cases │
│              │ REQUIRES idempotent consumers            │
├──────────────┼──────────────────────────────────────────┤
│ EXACTLY-ONCE │ No loss, no duplicate. High cost.        │
│              │ Use: financial, critical operations      │
├──────────────┼──────────────────────────────────────────┤
│ PRODUCTION   │ Default: at-least-once + idempotency.    │
│ DEFAULT      │ It achieves the same result as           │
│              │ exactly-once with lower complexity.      │
├──────────────┼──────────────────────────────────────────┤
│ KAFKA EOS    │ Exactly-once in Kafka only. External     │
│              │ systems still need idempotent consumers. │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ At-least-once without idempotency =      │
│              │ random duplicates in production          │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Use at-least-once, make consumers       │
│              │  idempotent, get exactly-once behavior." │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Idempotency → Retry Logic →              │
│              │ Kafka EOS → Saga Pattern                 │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
The "at-least-once + idempotent consumer" pattern is the
canonical solution for reliable distributed processing.
It separates concerns correctly: the transport layer
guarantees delivery (at-least-once), and the application
layer guarantees correctness (idempotency). This produces
exactly-once business semantics from at-least-once
infrastructure - cheaper and simpler than end-to-end
exactly-once coordination.

This same pattern appears in:
- **REST APIs**: client retries + server idempotency keys
- **Kafka consumers**: at-least-once + message ID tracking
- **Scheduled jobs**: cron retries + job execution records
- **Database triggers**: retry-on-failure + idempotent logic

---

### 💡 The Surprising Truth

Amazon SQS's "standard queues" are at-least-once AND
"out-of-order" - messages may be delivered more than
once and in a different order than they were sent. Amazon
explicitly states: "Your application needs to be
idempotent to handle multiple deliveries of the same message."
Amazon SQS FIFO queues provide at-least-once with ordering,
and content-based deduplication (a 5-minute window). But
not truly exactly-once - within a consumer's visibility
timeout, the same message can be processed twice if the
consumer fails. The practical lesson from Amazon's own
infrastructure: even the cloud provider with the most
experience in distributed systems defaults to at-least-once
and requires application idempotency. Exactly-once is so
hard that even Amazon doesn't provide it as a default.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. [CLASSIFY] Given a messaging system and configuration,
   identify which delivery semantic applies and what
   failure scenarios can cause duplication or loss.
2. [IMPLEMENT] Build an at-least-once consumer for Kafka
   with manual offset commit and idempotency key tracking,
   handling concurrent duplicate messages.
3. [CHOOSE] Given a use case (payment processing, metrics
   collection, order confirmation email, inventory update),
   select the appropriate delivery semantic and justify
   the trade-off.
4. [DEBUG] An order processing system has occasional
   duplicate orders. Determine whether the root cause
   is at-least-once delivery without idempotency, and
   trace the exact failure scenario that caused it.
5. [EXPLAIN] Why Kafka's "exactly-once semantics" does not
   provide exactly-once behavior for a consumer that writes
   to an external database, and what additional mechanism
   is required.
