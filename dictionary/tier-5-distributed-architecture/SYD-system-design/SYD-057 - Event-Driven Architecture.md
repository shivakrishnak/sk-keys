---
id: SYD-057
title: Event-Driven Architecture
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-036
used_by: ""
related: SYD-036, SYD-058, SYD-059, SYD-056
tags:
  - architecture
  - events
  - messaging
  - design
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 57
permalink: /syd/event-driven-architecture/
---

# SYD-057 - Event-Driven Architecture

⚡ TL;DR - Event-Driven Architecture (EDA) is a design
style where components communicate by publishing and
consuming events rather than calling each other directly.
An "event" is a record of something that happened (OrderPlaced,
PaymentProcessed, UserRegistered). The publisher does not know
who consumes the event. This achieves loose coupling:
add a new consumer without changing the producer. Key
tradeoff: strong decoupling comes at the cost of
eventual consistency and harder debugging (the chain of
cause-and-effect is non-obvious and spans service boundaries).

| #057 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Message Queues | |
| **Related:** | Message Queues, CQRS, Event Sourcing, API Gateway Design | |

---

### 🔥 The Problem This Solves

An e-commerce service must, after an order is placed:
- Deduct inventory
- Send a confirmation email
- Award loyalty points
- Update analytics dashboards
- Notify the warehouse

**Synchronous approach:** Order service calls all 5 services
sequentially. Total latency: 5× average service call time.
If any service is down: the order fails. If inventory
deduction takes 3 seconds: the user waits 3 seconds.
Tight coupling: adding "notify fraud detection service" requires
changing Order service code.

**EDA approach:** Order service publishes one event
(OrderPlaced). Each downstream service consumes it
independently. Order service returns to the user in
< 100ms. Downstream processing happens asynchronously.
Adding fraud detection: subscribe to OrderPlaced - zero
changes to Order service.

---

### 📘 Textbook Definition

**Event-Driven Architecture (EDA):** A software
architecture pattern where system components communicate
through the production, detection, consumption, and
reaction to events. Components are decoupled: producers
do not know consumers, consumers do not know producers.

**Event:** An immutable record of something that happened
in the past. Described by a name (past tense: OrderPlaced,
not PlaceOrder) and a payload (the data describing the
event). Once published, events are not modified.

**Event broker:** A middleware layer (Kafka, RabbitMQ,
AWS SNS/SQS) that receives events from producers and
delivers them to consumers. Provides durability (persist
events even if consumers are temporarily down) and
fan-out (deliver one event to many consumers).

**Consumer group:** A set of service instances that
share the work of consuming events from a topic. Each
event is delivered to only one instance in the group.
Multiple consumer groups can each receive all events
from the same topic independently.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Producer publishes event. Broker stores and routes it.
Consumers react independently. No direct coupling.

**One analogy:**
> A newspaper (event broker):
> The journalist (producer) writes an article (event) once.
> Millions of subscribers (consumers) each read it on their
> own time, independently. The journalist does not know who
> reads it. A new subscriber does not affect the journalist.
> Back issues available if a subscriber missed one (durable log).

**One insight:**
EDA trades synchronous consistency for scalability and
decoupling. In a direct-call architecture, the order
service "knows" about inventory, email, and loyalty.
In EDA, it "knows" about nothing - it only knows about
an event schema. The event schema is the contract; it
must be versioned carefully because breaking it breaks
all consumers silently.

---

### 🔩 First Principles Explanation

**CORE COMPONENTS:**
```
Producer (Publisher):
  Service that creates events.
  Does NOT know who consumes them.
  Does NOT wait for consumers to finish.
  
  Good: OrderService publishes OrderPlaced.
  Bad: OrderService calls InventoryService directly.

Event Broker (Message Bus):
  Kafka, RabbitMQ, AWS EventBridge, Google Pub/Sub
  Responsibilities:
    - Accept events from producers
    - Persist events durably (survive consumer downtime)
    - Deliver events to consumers (push or pull)
    - Fan-out: one event → many consumer groups
    - Ordering guarantee (Kafka: per-partition order)
    - Replay: consumers can re-read past events

Consumer (Subscriber):
  Service that reacts to events.
  Pull-based (Kafka) or push-based (SNS, EventBridge).
  Process event, update own state, publish new events.
  Must be idempotent (event may be delivered twice).
```

**EVENT SCHEMA AND VERSIONING:**
```
Good event schema:
{
  "event_id": "uuid4",        # Unique ID (idempotency)
  "event_type": "OrderPlaced", # Past tense
  "event_version": "1.0",     # Schema version
  "timestamp": "ISO8601",      # When it happened
  "payload": {                 # Event data
    "order_id": "...",
    "user_id": "...",
    "items": [...],
    "total_amount": 99.99
  }
}

BAD event naming: PlaceOrder, CreateOrder (commands, not events)
GOOD event naming: OrderPlaced, OrderConfirmed (facts that happened)

Schema evolution:
  Adding a field: backward-compatible (consumers ignore
    unknown fields). Safe.
  Removing a field: breaking change. Consumers that read
    the field will fail.
  Renaming a field: breaking change.
  
Strategy: bump event_version. Run two versions in parallel
during migration. Deprecate old version after all consumers
are updated.
```

**PATTERNS IN EDA:**
```
1. Event Notification:
   Producer publishes lightweight event.
   Consumer fetches full data from producer's API.
   
   OrderPlaced → {order_id: "123"}
   Inventory service fetches: GET /orders/123
   
   Pro: event payload small.
   Con: extra API call; harder to replay.

2. Event-Carried State Transfer:
   Producer embeds full data in event.
   Consumer does not need to call back.
   
   OrderPlaced → {order_id, user_id, items, total}
   
   Pro: consumer is self-contained; replay works.
   Con: larger payloads; consumer stores stale data
       if it only reads event data (not live queries).

3. Event Sourcing (related, not same as EDA):
   ALL state changes stored as events.
   Current state = replay of all events.
   (Covered separately in SYD-059)
```

---

### 🧪 Thought Experiment

**SIZING: 10,000 events/second from order service**

Order service publishes OrderPlaced at 10K events/sec.
3 consumers: Inventory, Email, Loyalty.

**Without Kafka (direct HTTP callbacks):**
Order service calls 3 endpoints on every order.
Each call: 10ms average. 3 calls: 30ms total.
Order service thread blocked for 30ms.
At 10K events/sec: 10K × 30ms = 300K thread-ms/sec.
Need 300 concurrent threads to keep up.
If Email service goes down: order creation fails.

**With Kafka:**
Order service: PRODUCE → Kafka. Returns in < 1ms.
At 10K events/sec, Kafka throughput: trivial for Kafka
(handles millions of messages/second).
3 consumer groups, each consuming independently.
Email service down for 2 hours: messages pile up in Kafka.
On restart: Email service catches up by consuming backlog.
Order service was never affected.

**Partitioning for ordering:**
Key the event by order_id (or user_id).
Events for the same order always go to the same partition.
Within a partition: events are strictly ordered.
Inventory: receives OrderPlaced before OrderCancelled
for the same order. Correct deduction/restoration.

---

### 🧠 Mental Model / Analogy

> EDA is like a radio broadcast:
>
> A radio station (producer) broadcasts a signal (event).
> Anyone with a radio (consumer) can tune in and react.
> The station does not know who is listening.
> A new listener does not require the station to change.
> Listeners can record (Kafka retention) and replay later.
>
> Direct HTTP calls are like phone calls: 1-to-1, both
> parties must be available at the same time. EDA is
> broadcast: 1-to-many, producer and consumer run
> on their own schedules.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Services publish announcements (events) when something
happens. Other services listen and react. They do not
talk to each other directly - they talk through a
shared announcement board. Adding a new listener does
not require changing the announcer.

**Level 2 - How to use it (junior developer):**
Producer publishes event to a topic in Kafka.
Consumers subscribe to the topic. Each consumer is in
a consumer group; Kafka delivers each message once per
group. Consumers must handle duplicate delivery (at-least-once).

**Level 3 - How it works (mid-level engineer):**
Events are partitioned in Kafka by a key (e.g., order_id).
Within a partition: strict ordering. Across partitions:
no ordering guarantee. Consumers commit offsets to track
progress. If consumer crashes and restarts, it resumes
from the last committed offset. Idempotency key in event
schema prevents double-processing on redelivery.

**Level 4 - Why it was designed this way (senior/staff):**
EDA trades consistency for availability and decoupling.
In a direct-call system: if Inventory service is down,
Orders cannot be placed. In EDA: Orders can be placed
(event persisted in Kafka), and Inventory processes it
when it comes back up. This is a conscious tradeoff:
the system is eventually consistent, not immediately
consistent. Use EDA when: (a) downstream processing
can be delayed without user impact, (b) adding new
consumers is likely (don't want to change producers),
(c) durability of the event log is valuable (can replay
to build new services from history). Do NOT use EDA
when: the result must be synchronously verified before
returning to the user (e.g., payment authorization).

**Level 5 - Mastery (distinguished engineer):**
LinkedIn's data infrastructure processes 7 trillion
events per day through Kafka. Key architectural insights:
(1) The event log is the source of truth in a true EDA
system - the database is a derived view. This is the
"database inside-out" insight (Martin Kleppmann's term):
instead of storing state in a database and streaming
changes as events, store events as the primary state and
derive the database as a materialized view. (2) Schema
Registry (Confluent) is essential at scale: all events
must be registered with a schema (Avro/Protobuf). Producers
and consumers validate against the registry. This prevents
schema drift - a silent killer in EDA where producers
change event shape and consumers silently fail with
deserialization errors. (3) Sagas (SYD-062): long-running
business processes (order placement, booking) orchestrate
multiple services through events with compensating events
(undo actions) for failure handling.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ EVENT-DRIVEN ORDER PROCESSING                       │
│                                                      │
│ [Order Service]                                     │
│   POST /orders → create order (PENDING)            │
│   publish to Kafka:                                │
│     topic: order.events                            │
│     key: order_id (ensures partition affinity)     │
│     event: OrderPlaced {order_id, user_id, items}  │
│   → return 202 Accepted to user                   │
│                                                      │
│ [Kafka: order.events topic]                        │
│   Partition 0: order_123, order_456 (same user)   │
│   Partition 1: order_789, order_101               │
│                                                      │
│ [Consumer Group: inventory-service]                │
│   Consumes from all partitions                     │
│   On OrderPlaced: DECR inventory                  │
│   On success: publish InventoryReserved            │
│   On failure: publish InventoryFailed              │
│                                                      │
│ [Consumer Group: email-service]                    │
│   Consumes from all partitions (independent)       │
│   On OrderPlaced: send confirmation email          │
│                                                      │
│ [Consumer Group: loyalty-service]                  │
│   On OrderPlaced: award loyalty points             │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Kafka producer and consumer (Python)**
```python
from kafka import KafkaProducer, KafkaConsumer
import json
import uuid
from datetime import datetime, timezone

# Producer (Order Service)
producer = KafkaProducer(
    bootstrap_servers=["kafka:9092"],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=lambda k: k.encode("utf-8"),
    # Idempotent producer: prevents duplicate messages
    # on producer retry
    enable_idempotence=True,
    acks="all",  # Wait for all replicas to acknowledge
)

def place_order(order: dict):
    """Place an order and publish event."""
    order_id = str(uuid.uuid4())
    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": "OrderPlaced",
        "event_version": "1.0",
        "timestamp": datetime.now(
            timezone.utc).isoformat(),
        "payload": {
            "order_id": order_id,
            "user_id": order["user_id"],
            "items": order["items"],
            "total_amount": order["total"]
        }
    }
    producer.send(
        topic="order.events",
        key=order_id,  # Partition key
        value=event
    )
    producer.flush()
    return order_id  # Return immediately (async)

# Consumer (Inventory Service)
consumer = KafkaConsumer(
    "order.events",
    bootstrap_servers=["kafka:9092"],
    group_id="inventory-service",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="earliest",
    # Manual commit: mark as processed only after
    # successful processing (prevent message loss)
    enable_auto_commit=False,
)

processed = set()  # Idempotency store (in production: DB)

for message in consumer:
    event = message.value
    event_id = event["event_id"]

    # Idempotency: skip if already processed
    if event_id in processed:
        consumer.commit()
        continue

    if event["event_type"] == "OrderPlaced":
        try:
            payload = event["payload"]
            deduct_inventory(payload["items"])
            processed.add(event_id)
            consumer.commit()  # Only commit after success
        except Exception as e:
            # Do NOT commit: message will be redelivered
            print(f"Error processing {event_id}: {e}")
```

**Example 2 - Tight coupling without EDA (BAD)**
```python
# BAD: Order service directly calls all downstream services
# Cascading failures, tight coupling, slow response

def place_order_bad(order: dict):
    order_id = create_order_in_db(order)
    
    # If any of these fail: entire order fails
    inventory_service.deduct(order["items"])   # 20ms
    email_service.send_confirmation(order)     # 50ms
    loyalty_service.award_points(order)        # 30ms
    analytics_service.record_sale(order)       # 40ms
    warehouse_service.notify_pickup(order)     # 35ms
    
    # Total: 175ms minimum
    # If email service is down: orders FAIL
    # Adding fraud detection: edit THIS file
    return order_id

# GOOD: Order service publishes ONE event.
# Each service consumes independently (async).
# Order confirmation returns in < 10ms.
# Services are fully decoupled.
```

---

### ⚖️ Comparison Table

| Aspect | Synchronous (Direct Call) | Event-Driven (EDA) |
|---|---|---|
| **Coupling** | Tight (producer knows consumers) | Loose (producer only knows event schema) |
| **Consistency** | Immediate | Eventual |
| **Latency to producer** | High (waits for all consumers) | Low (publish-and-forget) |
| **Failure isolation** | No (one consumer down → producer fails) | Yes (consumers fail independently) |
| **Add new consumer** | Modify producer code | New service subscribes to topic |
| **Debugging** | Easy (synchronous call chain) | Hard (async chains, distributed trace needed) |
| **Use when** | Result needed immediately (auth, payment) | Decoupled async workflows (email, analytics) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| EDA is always better than synchronous calls | EDA is better when: downstream processing can be asynchronous, adding new consumers is likely, fault tolerance is required. Use synchronous calls when: the result is needed before returning to the user (e.g., payment authorization - you cannot return "order confirmed" before the payment is authorized). Mixing EDA and synchronous calls is the correct approach. |
| Event names can use imperative tense (CreateOrder) | Events represent facts that have already happened. They must use past tense: OrderPlaced, PaymentProcessed. Imperative names (CreateOrder) suggest commands (request for action), which are a different pattern (CQRS). Mixing command and event naming leads to confusion about what the consumer should do (and whether failure is expected). |
| Consumers process each event exactly once | Kafka guarantees at-least-once delivery by default. Events may be redelivered on consumer crash and restart. Every consumer MUST be idempotent: processing the same event twice must produce the same result as processing it once. Include an event_id in every event; consumers track processed event IDs to skip duplicates. |

---

### 🚨 Failure Modes & Diagnosis

**Event Schema Change Breaks Consumer**

**Symptom:**
Consumer service starts throwing deserialization
errors after a producer deployment. Errors like
"KeyError: 'user_email'" or "TypeError: expected str,
got NoneType". Consumer dead-letter-queue fills up.
Consumers fall behind (lag increases in Kafka).

**Root Cause:**
Producer deployed a new version that changed the event
schema (renamed field, removed field, changed type).
Consumers still expect the old schema. Events are now
incompatible.

**Fix - Schema Registry + versioning:**
```python
# Fix 1: Use Schema Registry (Confluent)
# All events registered with Avro schema.
# Producers: validated before publish.
# Consumers: validated on deserialization.
# Breaking changes caught at registry level, not
# at runtime.

# Fix 2: Graceful field access with defaults
def process_event(event: dict):
    payload = event.get("payload", {})
    
    # Old: strict access (breaks on missing field)
    # user_email = payload["user_email"]  # KeyError!
    
    # Good: safe access with default
    user_email = payload.get(
        "user_email",
        payload.get("email", "")  # Fallback to old name
    )
    order_id = payload.get("order_id", "unknown")
    
    if not user_email:
        # Log warning but don't fail - continue processing
        log.warning(f"No email in event for {order_id}")
        return  # skip email step, process rest

# Fix 3: Event versioning in the event schema
# event_version: "1.0" → handle old format
# event_version: "2.0" → handle new format
def process_event_versioned(event: dict):
    version = event.get("event_version", "1.0")
    if version == "1.0":
        return process_v1(event)
    elif version == "2.0":
        return process_v2(event)
    else:
        log.error(f"Unknown version: {version}")
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Message Queues` - Kafka and RabbitMQ are the
  event brokers that make EDA possible; understanding
  message delivery semantics is essential

**Builds On This (learn these next):**
- `CQRS` - Command-Query Responsibility Segregation
  is often combined with EDA: commands produce events,
  queries read from projections built by consuming events
- `Event Sourcing` - stores ALL state changes as events;
  EDA is the delivery mechanism; event sourcing is the
  persistence pattern

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CORE IDEA   │ Publish event → broker stores → consumers │
│             │ react independently. No direct coupling.  │
├─────────────┼──────────────────────────────────────────  │
│ EVENT NAME  │ Past tense: OrderPlaced, PaymentFailed.  │
│             │ NOT imperative: CreateOrder, ProcessPay. │
├─────────────┼──────────────────────────────────────────  │
│ IDEMPOTENCY │ Include event_id. Consumers track processed│
│             │ IDs. At-least-once → must be idempotent. │
├─────────────┼──────────────────────────────────────────  │
│ SCHEMA      │ Version all events. Use Schema Registry  │
│             │ (Avro/Protobuf) to catch breaking changes.│
├─────────────┼──────────────────────────────────────────  │
│ WHEN TO USE │ Downstream processing can be async.      │
│             │ Adding consumers without producer changes.│
├─────────────┼──────────────────────────────────────────  │
│ WHEN NOT    │ Result needed before returning to user   │
│             │ (payment auth, inventory check in cart). │
├─────────────┼──────────────────────────────────────────  │
│ ONE-LINER   │ "Producer publishes → broker delivers →  │
│             │  consumers react. Loose coupling."      │
├─────────────┼──────────────────────────────────────────  │
│ NEXT        │ CQRS → Event Sourcing → Circuit Breaker  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Events are immutable facts in the past tense. Producers
   publish them without knowing consumers. This is the
   source of loose coupling in EDA.
2. Kafka guarantees at-least-once delivery. Every consumer
   must be idempotent (use event_id to deduplicate). Never
   assume you process each event exactly once.
3. EDA is not always better than synchronous calls. Use
   EDA for async workflows (email, analytics, fulfillment).
   Use synchronous calls when the response is needed before
   returning to the user (payment auth, inventory check at
   checkout).

**Interview one-liner:**
"EDA: producers publish immutable events (past tense: OrderPlaced) to a Kafka
topic. Multiple consumer groups each receive all events independently. Kafka
guarantees at-least-once delivery → consumers must be idempotent (event_id
dedup). Consumers commit offsets only after successful processing. Schema Registry
(Avro/Protobuf) prevents breaking changes. Use EDA when downstream processing
can be async and adding new consumers should not require producer changes. Use
synchronous calls when the result must be verified before returning to the user."
