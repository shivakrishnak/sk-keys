---
id: MSV-059
title: Event-Carried State Transfer
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-048, MSV-050, MSV-051
used_by: MSV-048, MSV-050, MSV-051
related: MSV-048, MSV-050, MSV-051, MSV-054, MSV-049, MSV-060
tags:
  - microservices
  - messaging
  - deep-dive
  - events
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 59
permalink: /microservices/event-carried-state-transfer/
---

# MSV-059 - Event-Carried State Transfer

⚡ TL;DR - Event-Carried State Transfer (ECST): events
carry enough data for consumers to process WITHOUT
additional API calls back to the producer. Instead
of `OrderCreated {orderId: 123}` (thin event, requires
lookup), use `OrderCreated {orderId, customerId,
customerName, customerEmail, items, total, address}`
(fat event, self-contained). Benefit: consumer
independence (no runtime coupling to producer's API);
high availability (reads local data even if producer
is down). Trade-off: larger event size; producer
must include data it may not "own" (denormalized
data in event).

| #059 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Event-Driven Microservices, CQRS in Microservices, Event Sourcing in Microservices | |
| **Used by:** | Event-Driven Microservices, CQRS in Microservices, Event Sourcing in Microservices | |
| **Related:** | Event-Driven Microservices, CQRS in Microservices, Event Sourcing in Microservices, Outbox Pattern, Eventual Consistency in Microservices, Data Isolation per Service | |

---

### 🔥 The Problem This Solves

**THIN EVENTS CAUSE CHATTY COUPLING:**
Order-service publishes `OrderCreated {orderId: 123}`.
Notification-service receives the event. To send
a confirmation email: notification-service needs
customer name, email, and order details. Must call:
order-service API and customer-service API. These
APIs must be up when notification-service processes
the event. If either is down: notification delayed.
Notification-service has runtime coupling to 2
APIs it shouldn't depend on. ECST: events carry
the data; no API calls needed.

---

### 📘 Textbook Definition

**Event-Carried State Transfer (ECST)** (Martin Fowler,
"Patterns of Enterprise Application Architecture",
extended in microservices context) is an event
design pattern where events contain sufficient data
for consumers to fulfill their responsibility without
making synchronous calls back to the event producer
or other services. The event is "self-contained":
a consumer can perform its business function
(send email, award points, update projection)
using only the event's payload. This decouples
consumers from producer availability at processing
time. Contrasted with: thin events (event notifications
that trigger consumers to query the source).
ECST enables: consumer independence, better resilience
(producer down = consumer still processes),
naturally feeds CQRS projections without additional
lookup calls.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
ECST: events are "fat" - carry all data consumers
need. No API calls back to producer. Consumer is
truly independent.

**One analogy:**
> A newspaper article vs. a news alert. A news
> alert (thin event): "Breaking: earthquake in
> Tokyo." The reader must go find the full story
> elsewhere. A newspaper article (ECST event):
> includes who, what, where, when, why, casualty
> count, response actions. The reader has everything
> needed without going elsewhere. In microservices:
> design events like newspaper articles (self-contained),
> not news alerts (require follow-up lookup).

**One insight:**
ECST is the design pattern that makes CQRS projections
possible at scale. If events only contain IDs:
bulding a CQRS projection requires an API call
for each event to fetch the referenced data. At
10K events/sec: that's 10K API calls/sec just for
projections. With ECST: events carry all projection
data; no API calls needed. Projection throughput
= Kafka consumer throughput (very high), not API
call throughput (rate-limited).

---

### 🔩 First Principles Explanation

**THIN EVENT VS ECST:**

```
THIN EVENT (Event Notification pattern):
  OrderCreated {
    orderId: "order-001"
  }
  
  Consumer needs: customer name, email, items, total
  Must call:
    GET /orders/order-001  -> {orderId, customerId, items}
    GET /customers/{customerId} -> {name, email, tier}
  
  Problems:
  - 2 API calls per event
  - At 10K events/sec: 20K API calls/sec to 2 services
  - order-service down: consumer cannot process
  - customer-service down: consumer cannot process
  - Network failure: consumer processing delayed
  - Consumer RUNTIME COUPLED to 2 other services

ECST (Event-Carried State Transfer):
  OrderCreated {
    orderId: "order-001",
    customerId: "cust-123",
    customerName: "Alice Smith",
    customerEmail: "alice@example.com",
    customerTier: "GOLD",
    items: [
      {productId: "p-001", productName: "Widget A",
       qty: 2, unitPrice: 49.99}
    ],
    total: 99.98,
    currency: "USD",
    shippingAddress: {line1, city, country}
  }
  
  Consumer: has everything in the event payload
  API calls: ZERO at processing time
  
  order-service down: consumer still processes
  customer-service down: consumer still processes
  Consumer: truly independent

TRADE-OFFS:
  Event size: ECST events are larger (hundreds of bytes
  vs. tens of bytes for thin events)
  Data ownership: OrderCreated event contains
  customerName (owned by customer-service)
  Denormalization: customer name duplicated in event
  + in customer-service's DB
  Schema evolution: customer name format changes;
  events already in Kafka have old format
  
  Worth it for: high-throughput consumers,
  resilience-critical processing, CQRS projections
  Not worth it for: low-volume, latency-sensitive,
  when data changes frequently (stale in event)
```

---

### 🧪 Thought Experiment

**WHAT DATA TO INCLUDE IN ECST EVENTS:**

```
DECISION FRAMEWORK:
  For each potential event consumer:
  1. What data does it need to do its job?
  2. Is that data available at event production time?
  3. How likely is that data to change after event
     was produced?
  
  NOTIFICATIONS (send email):
  Needs: customerEmail, orderSummary
  Available at production: yes
  Stability: email rarely changes
  Include: yes
  
  ANALYTICS (record revenue):
  Needs: total, currency, productIds, customerId
  Available: yes
  Stability: stable
  Include: yes
  
  FRAUD DETECTION (check patterns):
  Needs: customerId, device fingerprint, IP address,
         items, total
  Available: device/IP known at order time
  Stability: snapshot (point in time)
  Include: yes (snapshot data)
  
  LOYALTY (award points based on tier):
  Needs: customerId, total, customerTier
  Available: tier known at order time
  Stability: tier changes occasionally
  Critical: use tier AT TIME OF ORDER (not current)
  Include: yes (snapshot semantics: lock in value)
  
  SHIPPING (create shipment):
  Needs: shippingAddress, items, weight
  Available: yes
  Stability: address for THIS order (point in time)
  Include: yes
```

---

### 🧠 Mental Model / Analogy

> ECST is like the difference between a check
> and cash. A check (thin event): "The bearer is
> owed $100." The bearer must go to the bank to
> VERIFY and COLLECT the money. If the bank is
> closed: no money today. Cash (ECST event):
> the $100 IS in the envelope. No bank visit needed.
> The bearer can use it immediately and independently.
> Events should be cash, not checks. Include the
> value in the event itself. Don't make consumers
> "cash the check" by calling back to verify.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Fat events: include all the data the receiver
needs. Don't make them call back for more info.
Like a meeting invitation that includes the agenda:
attendees don't need to call you to find out what
the meeting is about.

**Level 2 - How to apply (junior developer):**
For each event type: list every consumer and what
data they need. Include the union of all consumers'
requirements in the event payload. Use Jackson/Avro
for serialization. Accept larger payload size as
the trade-off for consumer independence.

**Level 3 - How it enables CQRS (mid-level):**
CQRS read projections: built by consuming events.
With thin events: projection builder must call APIs
for each event to get projection data. At 10K events/
sec: 10K API calls/sec. With ECST: projection builder
has all data in the event. Throughput: limited only
by Kafka consumer processing speed (much higher).

**Level 4 - Design tensions (senior engineer):**
ECST creates a data ownership tension: OrderCreated
event carries `customerName` (owned by customer-
service). If customer changes their name: events
already in Kafka have old name. Consumers' projections:
build on old name. Is this correct? For an order
that was placed with the name "Alice": yes, the
order SHOULD record the name at time of placement.
For a customer profile view: needs current name.
ECST is correct when snapshot semantics (state at
time of event) are the business requirement.

**Level 5 - Mastery (principal engineer):**
ECST at scale creates a schema versioning challenge.
An event from 3 years ago has the full state
including customer name in old format. A consumer
built today expects new format. Unlike a thin event
(which fetches current data from a live API that
always returns current format): ECST events are
immutable historical records. Schema evolution
requires backward-compatible additions, upcasting,
or schema registry enforcement. This is why ECST
and Event Sourcing are deeply related: both store
immutable snapshots and face the same schema
evolution challenge.

---

### ⚙️ How It Works (Mechanism)

```java
// ECST: self-contained event with all consumer data
public class OrderCreatedEvent {
    // Core identity
    private final String eventId;   // UUID for idempotency
    private final String orderId;
    private final Instant occurredAt;

    // Customer data (snapshot at time of order)
    // Owned by customer-service, but copied here
    private final String customerId;
    private final String customerName;    // Snapshot
    private final String customerEmail;   // Snapshot
    private final String customerTier;    // Snapshot: GOLD/SILVER

    // Order data (owned by order-service)
    private final List<OrderLineItem> items;
    private final Money total;
    private final String currency;
    private final Address shippingAddress;  // Snapshot

    // Computed fields useful to many consumers
    private final boolean isGiftOrder;
    private final String promoCode;  // If applicable
}

// Producer: enriches event at creation time
@Service
public class OrderService {
    @Transactional
    public Order createOrder(OrderRequest req) {
        // Fetch customer data synchronously (at creation)
        Customer customer = customerService
            .getCustomer(req.getCustomerId());

        Order order = orderRepo.save(Order.from(req));

        // Build ECST event: snapshot all consumer-needed data
        OrderCreatedEvent event = OrderCreatedEvent.builder()
            .eventId(UUID.randomUUID().toString())
            .orderId(order.getId())
            .customerId(customer.getId())
            .customerName(customer.getName())      // Snapshot
            .customerEmail(customer.getEmail())    // Snapshot
            .customerTier(customer.getTier())      // Snapshot
            .items(order.getItems())
            .total(order.getTotal())
            .shippingAddress(req.getShippingAddress())
            .occurredAt(Instant.now())
            .build();

        outboxRepo.save(OutboxEvent.from(event));
        return order;
    }
}

// CONSUMER: no API calls needed
@KafkaListener(topics = "order-events")
public void onOrderCreated(OrderCreatedEvent event) {
    // All data available from event payload:
    notificationService.sendEmail(
        event.getCustomerEmail(),  // From event (no API call)
        event.getCustomerName(),   // From event
        event.getOrderId(),
        event.getItems(),
        event.getTotal());
    // order-service: could be down -> we don't care
    // customer-service: could be down -> we don't care
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
ECST FLOW:

Event produced at T=0:
  order-service: creates order
  Fetches: customer name, email, tier from
           customer-service (sync, at creation time)
  Builds: fat OrderCreatedEvent with all data
  Publishes: to order-events Kafka topic

Consumers (all independent, no API calls):
  T=10ms: notification-service receives event
    Has: customerEmail, customerName, items, total
    Sends: confirmation email immediately
    customer-service: not called

  T=20ms: loyalty-service receives event
    Has: customerId, customerTier, total
    Awards: GOLD tier bonus points (2x)
    No call needed to customer-service

  T=30ms: analytics-service receives event
    Has: total, currency, productIds
    Records: revenue event
    No call needed to order-service

  T=40ms: fraud-service receives event
    Has: customerId, items, total, address
    Evaluates: fraud risk score
    No additional calls

Total API calls at consumer processing: 0
Vs. thin events: 8 API calls (2 per consumer x 4)
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: thin vs fat event**

```java
// BAD: Thin event - consumers must query back
public class OrderCreatedEvent {
    private String orderId;  // Only the ID!
}
// Consumer: must call order-service for details
// AND customer-service for customer info
// Chatty, tightly coupled, unavailability cascades
```

```java
// GOOD: ECST fat event - consumer-independent
public class OrderCreatedEvent {
    private String orderId;
    private String customerEmail;  // Consumer needs
    private String customerName;   // Consumer needs
    private List<OrderItem> items; // Consumer needs
    private BigDecimal total;      // Consumer needs
    private String currency;
    // Consumer: sends email with all data from event
    // No API calls to order-service or customer-service
    // Consumer works even when both services are down
}
```

---

### ⚖️ Comparison Table

| Aspect | Thin Event | ECST (Fat Event) |
|---|---|---|
| **Event size** | Small (<100 bytes) | Large (hundreds to KB) |
| **Consumer API calls** | Multiple (N per consumer) | Zero |
| **Consumer availability** | Depends on producer API | Fully independent |
| **Data freshness** | Always current (API fetch) | Snapshot at event time |
| **Schema coupling** | Consumer couples to producer API | Consumer couples to event schema |
| **CQRS projection** | Needs API calls (slow) | Direct from event (fast) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| ECST events should contain ALL data about every entity | No. Include data that consumers NEED to process the event, not everything the producer knows. Determine: what does each consumer need? Take the union. Don't include highly sensitive data (passwords, payment card numbers) in events that go to many consumers. Apply data minimization. |
| Customer name in an order event is wrong (data ownership) | Customer name in an OrderCreated event is a SNAPSHOT: the name at the time of the order. This is a legitimate business requirement (order history should reflect the name as it was). Data ownership means: customer-service is the system of record for the current customer name. The event snapshot is a historical record. Both are valid and serve different purposes. |
| ECST means events should never include just IDs | ECST is not binary (all data or just ID). Include the data that consumers need to avoid API calls for COMMON use cases. A product ID may be included for lookup in a local catalog cache rather than included in full detail. Design based on consumer needs analysis, not a blanket rule. |

---

### 🚨 Failure Modes & Diagnosis

**CQRS projection builder making 5000 API calls/sec**

**Symptom:**
order-service API getting 5000 GET requests/second
from loyalty-service. loyalty-service processing
Kafka events. order-service rate-limiting loyalty-
service requests (429 Too Many Requests). Loyalty
projection: falling behind.

**Root Cause:**
OrderCreated events are thin: `{orderId, customerId,
amount}`. Loyalty-service's projection builder:
for each event, calls `GET /orders/{orderId}` to
get product details needed for loyalty category
bonuses. At 5000 events/sec: 5000 API calls/sec.

**Fix:**
1. Add product category data to OrderCreated event
   (ECST): include `items[]{productId, categoryId,
   categoryName}`. Loyalty-service: uses category
   from event; no API call.
2. Immediate: add Redis cache in loyalty-service
   for product category lookups. Reduces API calls
   from 5000/sec to cache miss rate (~50/sec).
3. Long-term: apply ECST to all event types consumed
   by loyalty-service. Target: zero API calls during
   event processing.

---

### 🔗 Related Keywords

**Enables:**
- `CQRS in Microservices` - ECST events carry data
  needed to build projections without API calls
- `Event Sourcing in Microservices` - event store
  events should be ECST for replay correctness

**Requires:**
- `Event-Driven Microservices` - the event-driven
  architecture that ECST optimizes
- `Outbox Pattern` - ensures ECST events are
  reliably published after the producer's DB write

**Related data:**
- `Data Isolation per Service` - ECST carries
  cross-service data in events rather than
  requiring cross-service DB access or API calls

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PATTERN      │ Fat events carry all consumer-needed data │
│              │ No API calls back to producer at runtime  │
├──────────────┼───────────────────────────────────────────┤
│ BENEFIT      │ Consumer independence; resilience;        │
│              │ enables CQRS projections at scale         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Larger event size; snapshot semantics;    │
│              │ schema evolution complexity               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Fat events = self-contained; consumer    │
│              │  processes without calling back to producer"│
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. ECST = fat events: carry all data consumers need
   to process. Zero API calls at consumer processing
   time.
2. Enables consumer independence: producer can be
   down; consumer still processes from event data.
3. Trade-off: larger event size, snapshot semantics
   (data may be stale by the time consumer processes).
   Use ECST when: snapshot is correct, consumers
   are high-throughput, or resilience is critical.

**Interview one-liner:**
"ECST (Event-Carried State Transfer): events carry
enough data for consumers to process WITHOUT calling
back to the producer. OrderCreated includes customerName,
customerEmail, items, total (not just orderId). Benefits:
consumer independence (producer can be down), zero
API calls at processing time, enables CQRS projections
at high throughput. Trade-offs: larger event size,
snapshot semantics (data captured at event creation;
not updated later). Decide what to include by
analyzing each consumer's data requirements."

---

### 💡 The Surprising Truth

ECST violates data ownership principles on the
surface: an OrderCreated event contains customerName,
which is "owned" by customer-service. Isn't this
wrong? No. The event captures a SNAPSHOT of customer
name at the time of the order. This snapshot is
part of the order's historical record. Data ownership
means: customer-service controls updates to the
current customer name. It does NOT mean that historical
events cannot record what the customer's name was
at a specific point in time. This is fundamental
to understanding immutable event stores: events
record what was true when they occurred. Cross-
service data in events is not a violation - it's
a snapshot that preserves historical accuracy.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DESIGN** For an OrderCreated event with 4
   downstream consumers (notification, loyalty,
   analytics, fraud): perform a consumer data
   requirements analysis. Specify exactly which
   fields to include in the ECST event and why.
2. **TRADE-OFF** A customer's shipping address is
   included in OrderCreated (ECST). The customer
   updates their address 1 hour after placing the
   order. What happens to in-flight event processing?
   Is the snapshot correct? What if the consumer
   processes the event after the address update?
3. **SCALE** ECST events average 2KB each. Kafka
   throughput: 100K events/sec. Calculate daily
   Kafka storage. Compare to thin events (200 bytes
   each). At what throughput does event size become
   a significant cost/performance factor?
4. **CQRS** Without ECST: a CQRS projection builder
   makes 3 API calls per event. With ECST: zero.
   At 10K events/sec: calculate the reduction in
   API calls and the impact on order-service capacity.
5. **EVOLUTION** You need to add a `giftMessage`
   field to an existing ECST OrderCreated event.
   Walk through: schema registry registration,
   backward compatibility check, how old consumers
   handle the new field, how new consumers handle
   old events without the field.

---

### 🧠 Think About This Before We Continue

**Q1.** An OrderCreated ECST event includes
`customerTier: GOLD`. 6 months after the order,
the customer is downgraded to SILVER due to inactivity.
The loyalty-service rebuilds its projection (schema
change): replays all OrderCreated events. The
replay uses `customerTier: GOLD` from old events
-> awards GOLD loyalty points for old orders again.
Is this correct? Should projection rebuilds use
snapshot tier or current tier? How do you design
the projection to handle this?

**Q2.** Your ECST events include `customerEmail`.
A customer's email is changed (or the customer is
deleted under GDPR right to erasure). The email
is captured in ECST events in Kafka (immutable logs).
How do you comply with GDPR while maintaining event
immutability? This is the same crypto-shredding
problem as Event Sourcing.

**Q3.** Design the decision framework for choosing
between ECST (fat events) and thin events for a
new microservices system. Give 3 specific criteria
that favor ECST and 3 that favor thin events. For
a real-world example (e.g., payment processing,
e-commerce orders, content management): apply
your framework.