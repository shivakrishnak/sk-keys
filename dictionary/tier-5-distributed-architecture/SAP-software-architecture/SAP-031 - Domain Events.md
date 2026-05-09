---
id: SAP-031
title: Domain Events
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★★
depends_on: SAP-023, SAP-030
used_by: SAP-018, SAP-019
related: SAP-018, SAP-019, SAP-030
tags:
  - architecture
  - ddd
  - pattern
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 31
permalink: /software-architecture/domain-events/
  - deep-dive
  - events
  - advanced
---

# SAP-031 - Domain Events

⚡ TL;DR - Domain Events capture something significant that happened in the business domain - they are the authoritative record of a state change, expressed in the language of the business, and are the mechanism for decoupled, cross-aggregate coordination.

| Field          | Value                     |
| -------------- | ------------------------- |
| **Depends on** | SAP-023, SAP-030          |
| **Used by**    | SAP-018, SAP-019          |
| **Related**    | SAP-018, SAP-019, SAP-030 |

---

### 🔥 The Problem This Solves

**THE COUPLING PROBLEM:**
An order is cancelled. The inventory service needs to know (to return stock). The billing service needs to know (to issue a refund). The notification service needs to know (to send a customer email). The analytics service needs to know (to record the cancellation).

Without Domain Events, `OrderService.cancel()` directly calls `InventoryService`, `BillingService`, `NotificationService`, and `AnalyticsService`. Four direct dependencies. Adding a fifth consumer requires changing `OrderService`. The order domain knows too much about its consumers.

**THE DOMAIN EVENT SOLUTION:**
`Order.cancel()` raises an `OrderCancelledEvent`. The order knows nothing about who needs to react. Each downstream service subscribes to `OrderCancelledEvent` and reacts independently. Adding a new consumer doesn't touch the order domain. The order is decoupled from its reactions.

**EVOLUTION:**
Eric Evans introduced Domain Events in later editions of DDD (the concept was refined in the DDD community after the 2003 book, with Evans retroactively embracing it as a first-class pattern). Udi Dahan and Greg Young popularized the pattern in the 2006-2010 period through their work on CQRS and Event Sourcing. The term "Domain Event" distinguishes business-significant occurrences from technical messaging (which predates DDD). The pattern became mainstream with the rise of microservices (2014+), where loose coupling between services required event-driven communication. Today, Domain Events drive event-driven architecture at cloud scale, with Apache Kafka providing the infrastructure for publishing and subscribing to events across services.

---

### 📘 Textbook Definition

A Domain Event, as described by Eric Evans in "Domain-Driven Design" and elaborated by Vaughn Vernon in "Implementing Domain-Driven Design," represents something that happened in the domain that domain experts care about. A Domain Event is a value object that describes something that happened in the past - it is named in past tense (OrderPlaced, PaymentReceived, ShipmentDispatched), is immutable, and carries all the data needed to understand what happened and when. Domain Events are raised by Aggregate Roots when a significant state transition occurs and are used to coordinate reactions across aggregates and bounded contexts without direct coupling.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Immutable records of significant things that happened - expressed in business language, used to decouple reactions.

**One analogy:**

> A newspaper publishes news events - "Prime Minister Resigned at 3pm Today." The newspaper doesn't know who will read it or what they'll do with the information. Some readers will vote differently. Some will invest differently. Some will write commentary. The newspaper (aggregate root) raises the event; the readers (other aggregates, services) react independently. Adding a new reader doesn't require the newspaper to change.

**One insight:**
Domain Events move coordination from "tell everyone what to do" (imperative) to "tell everyone what happened" (declarative). Each consumer decides independently how to react. This is the core of decoupled architecture.

---

### 🔩 First Principles Explanation

**DOMAIN EVENT PROPERTIES:**

```
┌──────────────────────────────────────────────────────────┐
│             DOMAIN EVENT CHARACTERISTICS                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ✅ Named in past tense:                                 │
│     OrderPlaced, PaymentReceived, ShipmentDispatched     │
│     NOT: PlaceOrder, ReceivePayment, DispatchShipment    │
│                                                          │
│  ✅ Immutable - what happened cannot be undone:          │
│     No setters. Final fields. Created once.              │
│                                                          │
│  ✅ Self-contained - carries all needed context:         │
│     OrderCancelledEvent(orderId, customerId,             │
│                          items, reason, cancelledAt)     │
│     Consumer shouldn't need to load the aggregate again  │
│                                                          │
│  ✅ Business vocabulary - not technical:                 │
│     CustomerUpgraded (not CustomerStatusChanged)         │
│                                                          │
│  ✅ Raised by Aggregate Root, not service:               │
│     order.cancel() → raises event (inside domain)        │
│     NOT: orderService raises event after calling cancel()│
└──────────────────────────────────────────────────────────┘
```

**DOMAIN EVENTS vs INTEGRATION EVENTS:**

```
┌──────────────────────────────────────────────────────────┐
│      DOMAIN EVENT vs INTEGRATION EVENT                   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Domain Event:                                           │
│    Scope: within one Bounded Context                     │
│    Transport: in-memory (same process)                   │
│    Schema: rich domain types (Money, OrderId, etc.)      │
│    Timing: raised during aggregate operation             │
│    Usage: cross-aggregate coordination within BC         │
│                                                          │
│  Integration Event:                                      │
│    Scope: across Bounded Contexts / microservices        │
│    Transport: message broker (Kafka, RabbitMQ)           │
│    Schema: simple primitive types (UUID, String, int)    │
│    Timing: published after successful commit             │
│    Usage: cross-service coordination                     │
│                                                          │
│  Domain Event → (Outbox Pattern) → Integration Event     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**ADDING A NEW REACTION WITHOUT CHANGING THE DOMAIN:**

Scenario: Order is placed. Currently: warehouse gets a pick task, billing charges the customer.

New requirement: When an order is placed, send the customer a confirmation email.

**Without Domain Events (direct coupling):**

```java
// OrderService.placeOrder() must change:
public void placeOrder(PlaceOrderCommand cmd) {
    Order order = Order.place(...);
    orderRepo.save(order);
    warehouseService.createPickTask(order);  // existing
    billingService.chargeCustomer(order);    // existing
    emailService.sendConfirmation(order);    // NEW: OrderService must be modified
}
```

**With Domain Events (decoupled):**

```java
// OrderService.placeOrder() unchanged:
public void placeOrder(PlaceOrderCommand cmd) {
    Order order = Order.place(...);  // raises OrderPlacedEvent
    orderRepo.save(order);
    eventPublisher.publish(order.domainEvents());
    // OrderService doesn't know or care who reacts
}

// NEW: Just add a new event handler - no other changes
@Component
public class OrderConfirmationEmailHandler {
    @EventListener
    public void handle(OrderPlacedEvent event) {
        emailService.sendConfirmation(
            event.customerId(), event.orderId());
    }
}
```

**The insight:** Domain Events allow the system to grow (new reactions) without changing the domain code that raises the events.

---

### 🧠 Mental Model / Analogy

> Domain Events are the business's audit log made actionable. Every significant business event - "loan approved," "shipment sent," "payment failed" - is captured as a named, immutable record at the moment it occurs. Anyone who needs to react to that event subscribes to it. The audit trail and the coordination mechanism are the same thing. You get both observability and decoupling from the same pattern.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone):**
Records of important things that happened in your business: "Order placed," "Payment received," "Account closed." Other parts of the system listen for these records and react.

**Level 2 - How to use it (junior):**

1. Name the event in past tense: `OrderShippedEvent`. 2. Create an immutable class with all relevant data. 3. In the aggregate root's operation method, add the event to a collection: `events.add(new OrderShippedEvent(...))`. 4. After the repository saves the aggregate, publish the events to an event bus. 5. Write event handlers that react to the events.

**Level 3 - Transactional guarantees (mid-level):**
Domain Events raised in-memory are only meaningful after the aggregate is successfully committed. The sequence must be: 1) domain operation + raise event, 2) save to database, 3) publish events. If step 3 fails (process crash), the events are lost. The Outbox Pattern solves this: store events in the same transaction as the aggregate, publish them from the outbox reliably. This guarantees at-least-once delivery.

**Level 4 - Event design (senior/staff):**
Domain Events reveal the true language of the domain. Events that are hard to name are usually symptoms of unclear domain boundaries. `SomethingChanged` is not a domain event - it's a technical notification. `CustomerUpgradedToPremium` is a domain event - it names a specific business concept. Event design is a design activity in itself: what events does the business care about? What do domain experts track in their heads? Those are your domain events. Event schema evolution is critical for long-lived systems - use schema versioning, forward/backward compatibility, and avoid breaking changes. Upcasters transform old event versions to new versions for event-sourced aggregates.

---

### ⚙️ How It Works (Mechanism)

**Three-phase lifecycle:**

```
┌──────────────────────────────────────────────────────────┐
│           DOMAIN EVENT LIFECYCLE                         │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Phase 1 - RAISING (in aggregate operation):             │
│    order.cancel(reason)                                  │
│      → validates: can cancel?                            │
│      → changes status to CANCELLED                       │
│      → events.add(new OrderCancelledEvent(               │
│            id, customerId, items, reason, now()))        │
│    Event is in-memory, NOT yet published                 │
│                                                          │
│  Phase 2 - STORING (in repository save):                 │
│    orderRepo.save(order)                                  │
│      → persists Order state change to DB                 │
│      → (with Outbox) persists events to outbox table     │
│      → both in SAME transaction                          │
│                                                          │
│  Phase 3 - PUBLISHING (after commit):                    │
│    eventPublisher.publish(order.domainEvents())          │
│    OR: Outbox relay publishes from outbox table          │
│      → event dispatched to handlers                      │
│      → handlers run (same process or via message broker) │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture

```
┌──────────────────────────────────────────────────────────┐
│         DOMAIN EVENTS - CROSS-AGGREGATE FLOW             │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Order Aggregate            Inventory Aggregate          │
│  ─────────────              ────────────────────         │
│  order.cancel()                                          │
│  → raises OrderCancelledEvent                            │
│  → saved to DB (tx 1)                                    │
│         │                                                │
│         ↓ published to event bus                         │
│         │                                                │
│         └──────────────────────────────────────────────→│
│                              InventoryEventHandler       │
│                              receives OrderCancelledEvent│
│                              → inventory.returnStock()   │
│                              → saved to DB (tx 2)        │
│                                                          │
│  Two separate transactions - eventual consistency        │
│  Order consistency is immediate; inventory is eventual   │
└──────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Domain Event definition - immutable value object:**

```java
// Domain Event - past tense, immutable, self-contained
public final class OrderCancelledEvent implements DomainEvent {
    private final OrderId orderId;
    private final CustomerId customerId;
    private final List<OrderItemSnapshot> items;
    private final String reason;
    private final Instant cancelledAt;
    private final UUID eventId;

    public OrderCancelledEvent(OrderId orderId,
                                CustomerId customerId,
                                List<OrderItem> items,
                                String reason) {
        this.orderId = orderId;
        this.customerId = customerId;
        // Snapshot items - event is self-contained
        this.items = items.stream()
            .map(OrderItemSnapshot::of)
            .collect(Collectors.toUnmodifiableList());
        this.reason = reason;
        this.cancelledAt = Instant.now();
        this.eventId = UUID.randomUUID();
    }

    // Only getters - no setters, no mutations
    public OrderId orderId() { return orderId; }
    public CustomerId customerId() { return customerId; }
    public List<OrderItemSnapshot> items() { return items; }
    public String reason() { return reason; }
    public Instant cancelledAt() { return cancelledAt; }
    public UUID eventId() { return eventId; }
}
```

**Event handler - decoupled reactor:**

```java
// Inventory reaction - completely decoupled from Order domain
@Component
@RequiredArgsConstructor
public class InventoryReturnHandler {

    private final InventoryRepository inventoryRepo;

    @TransactionalEventListener(
        phase = TransactionPhase.AFTER_COMMIT)
    public void handle(OrderCancelledEvent event) {
        event.items().forEach(item -> {
            Inventory inv = inventoryRepo
                .findByProduct(item.productId());
            inv.returnStock(item.quantity());
            inventoryRepo.save(inv);
        });
    }
}

// Notification reaction - independent subscriber
@Component
@RequiredArgsConstructor
public class CancellationEmailHandler {

    private final EmailService emailService;

    @TransactionalEventListener(
        phase = TransactionPhase.AFTER_COMMIT)
    public void handle(OrderCancelledEvent event) {
        emailService.sendCancellationConfirmation(
            event.customerId(),
            event.orderId(),
            event.reason());
    }
}
```

**Publishing events after aggregate save:**

```java
@Service
@RequiredArgsConstructor
public class OrderApplicationService {

    private final OrderRepository orderRepo;
    private final ApplicationEventPublisher eventPublisher;

    @Transactional
    public void cancelOrder(CancelOrderCommand cmd) {
        Order order = orderRepo.findById(cmd.orderId())
            .orElseThrow();

        order.cancel(cmd.reason());  // raises event
        orderRepo.save(order);       // saves state

        // Publish AFTER save so events aren't lost on rollback
        // @TransactionalEventListener handles after-commit
        order.domainEvents().forEach(
            eventPublisher::publishEvent);
        order.clearEvents();
    }
}
```

---

### ⚖️ Comparison Table

| Aspect            | Domain Events                       | Direct Method Calls         | Integration Events               |
| ----------------- | ----------------------------------- | --------------------------- | -------------------------------- |
| Coupling          | Loose - publisher ignores consumers | Tight - caller knows callee | Loose - crosses service boundary |
| Consistency       | Eventual (for cross-aggregate)      | Immediate                   | Eventual                         |
| Transaction scope | Same tx or separate                 | Same tx (typically)         | Separate service tx              |
| Discoverability   | Events show what happened           | Calls show what was done    | Same as domain events            |
| Failure handling  | At-least-once via Outbox            | Rollback                    | Retry via message broker         |

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                               |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Domain Events are the same as integration events  | Domain Events are in-process and can use rich types; Integration Events cross services and use simple schemas                         |
| Raising an event = publishing it immediately      | Events should be published AFTER the transaction commits - not during the operation                                                   |
| Domain Events replace direct service calls always | For in-aggregate coordination, direct method calls are fine; domain events are for cross-aggregate or cross-context coordination      |
| Domain Events are just a pub/sub mechanism        | Domain Events are a domain design concept - they should represent meaningful business occurrences, not just data change notifications |

---

### 🚨 Failure Modes & Diagnosis

**Lost Events on Process Crash**

**Symptom:** Order is cancelled in the database but inventory is not updated. Inconsistency discovered by reconciliation job.

**Root Cause:** Event published in-memory after commit, but process crashed between commit and publish. Events were in a local list, not persisted.

**Fix:** Implement the Outbox Pattern - persist events to an outbox table in the same transaction as the aggregate state change. A relay process reads from the outbox and publishes reliably.

**Prevention:** Never rely on in-memory event dispatch for cross-service coordination. Use the Outbox Pattern or a transactional event bus.

---

**Event Handler Violating Aggregate Boundaries**

**Symptom:** `OrderCancelledEvent` handler directly queries order items from the database, bypassing the Order aggregate root.

**Root Cause:** Handler needs item data but tries to avoid loading the full aggregate.

**Fix:** Include all needed data in the event payload (snapshot pattern). If the event is self-contained, handlers don't need to query the source aggregate.

---

### � Transferable Wisdom

**Reusable Engineering Principle:** When significant state changes occur, record what happened rather than issuing direct commands to all interested parties. Let interested parties pull the information they need from the record rather than being pushed commands they must execute.

**Where else this pattern appears:**
- **Git commit history:** Each commit is a Domain Event - it records what changed, who changed it, when it changed, and why (commit message). No one "commands" git's history; it records facts, and tooling (CI/CD, code review, blame) reacts to those facts independently.
- **Double-entry bookkeeping:** Every financial transaction is recorded as an immutable event (journal entry). No financial entry is ever deleted or modified - only new entries are added. This is Domain Events applied to accounting, and it predates object-oriented programming by 500 years.
- **Medical records:** A patient record accumulates events (diagnoses, prescriptions, procedures) immutably. Medical history is never overwritten - new events extend the record. A doctor reads the history to understand the current state.

---

### 💡 The Surprising Truth

The hardest part of Domain Events is determining what constitutes a "significant business occurrence." Teams new to Domain Events create events for everything - `CustomerFirstNameUpdated`, `OrderItemQuantityChanged` - which produces an event flood of low-level state changes that nobody handles differently. Real Domain Events should be named in past-tense business language: `OrderPlaced`, `PaymentProcessed`, `ItemShipped`, `CustomerUpgraded`. The test: can a business analyst read the event name and immediately understand its business significance? If not, it is probably a database change notification dressed up as a Domain Event, not a real business event.

---

### �🔗 Related Keywords

**Prerequisites (understand these first):**
- SAP-023 - Domain Model (domain events express what happened in the domain model; understanding what domain objects are is required to understand what events they raise)
- SAP-030 - Aggregate Root (domain events are raised by aggregate roots during state transitions; understanding which object raises the event and why requires understanding aggregates)

**Builds On This (learn these next):**
- SAP-018 - CQRS Pattern (the command side raises domain events; the read side projects them into query models; CQRS is the architectural framework that makes Domain Events central)
- SAP-019 - Event Sourcing Pattern (stores aggregate state as a sequence of domain events; Event Sourcing takes Domain Events to their logical conclusion by making events the primary storage format)

**Alternatives / Comparisons:**
- SAP-019 - Event Sourcing (closely related; Domain Events raise and forget; Event Sourcing stores every raised event as the source of truth)
- SAP-030 - Aggregate Root (complementary; aggregates raise events; they are not alternatives but collaborators)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Immutable records of significant business │
│              │ occurrences; past-tense named             │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ "Tell what happened; let others react"    │
├──────────────┼───────────────────────────────────────────┤
│ RAISED BY    │ Aggregate Root during state transition    │
├──────────────┼───────────────────────────────────────────┤
│ PUBLISH WHEN │ AFTER transaction commit, never during    │
├──────────────┼───────────────────────────────────────────┤
│ RELIABILITY  │ Use Outbox Pattern for guaranteed delivery│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The newspaper: tells what happened;      │
│              │  readers decide what to do"               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a `PaymentProcessedEvent` that is raised when a payment succeeds. Multiple services subscribe to it: order fulfillment, billing, fraud detection, and analytics. The fraud detection handler is slow (external API call) and sometimes times out. Should all handlers run in the same transaction? Should the slow handler be moved to an asynchronous queue? What are the consistency implications of each approach?

*Hint:* Research the distinction between "in-process domain events" (handled synchronously in the same transaction) and "integration events" (published to a message broker for asynchronous processing). Specifically: in-process handlers that fail will rollback the entire transaction including the payment. Asynchronous handlers via Kafka/RabbitMQ decouple the payment from fraud detection but introduce eventual consistency. Research the "Outbox Pattern" for guaranteed delivery of integration events after the transaction commits.

**Q2.** Event schemas evolve over time. An `OrderPlacedEvent` initially has `customerId: UUID`. Six months later, a new field `customerTier: String` is added. There are thousands of historical events stored in the event store in the old format. You need to add a new event handler that uses `customerTier`. How do you handle schema evolution without breaking existing handlers or corrupting historical event data?

*Hint:* Research event schema evolution strategies: (1) Upcasting - a component that transforms old events into new format before they reach handlers; (2) Optional fields with defaults - the new `customerTier` field defaults to `STANDARD` when absent; (3) Event versioning with separate handler per version (`OrderPlacedEventV1`, `OrderPlacedEventV2`). Research how Axon Framework's `EventUpcaster` interface handles this in practice.

**Q3.** Two aggregate roots both need to react to the same domain event. An `OrderPlacedEvent` needs to trigger both an inventory reservation (updating `InventoryAggregate`) and a loyalty points award (updating `CustomerLoyaltyAggregate`). Both updates must eventually succeed, but they can't be in the same transaction (different aggregates). If the inventory reservation succeeds but the loyalty points update fails, how do you ensure eventual consistency?

*Hint:* Research the "Process Manager" (or "Saga") pattern - specifically how a Saga coordinates multiple aggregate updates in response to domain events. The Saga subscribes to `OrderPlacedEvent`, triggers the inventory reservation command, waits for `InventoryReservedEvent`, then triggers the loyalty points command. If any step fails, the Saga issues compensating commands. Research how Axon Framework's `@SagaEventHandler` implements this.
