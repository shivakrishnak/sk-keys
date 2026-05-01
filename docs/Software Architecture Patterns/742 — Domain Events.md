---
layout: default
title: "Domain Events"
parent: "Software Architecture Patterns"
nav_order: 742
permalink: /software-architecture/domain-events/
number: "742"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: "Domain Model, Event Sourcing Pattern, Aggregate Root"
used_by: "Spring ApplicationEvents, Kafka, Saga Pattern, CQRS"
tags: #advanced, #architecture, #ddd, #events, #decoupling
---

# 742 — Domain Events

`#advanced` `#architecture` `#ddd` `#events` `#decoupling`

⚡ TL;DR — **Domain Events** are immutable records of significant things that happened in the business domain — capturing the business fact, decoupling the publisher from downstream reactions, and enabling event-driven architectures within or across bounded contexts.

| #742            | Category: Software Architecture Patterns             | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------- | :-------------- |
| **Depends on:** | Domain Model, Event Sourcing Pattern, Aggregate Root |                 |
| **Used by:**    | Spring ApplicationEvents, Kafka, Saga Pattern, CQRS  |                 |

---

### 📘 Textbook Definition

**Domain Events** (Eric Evans, "Domain-Driven Design"; Vaughn Vernon, "Implementing Domain-Driven Design") represent something meaningful that happened in the business domain. A domain event: (1) **Occurred in the past**: named in past tense — `OrderPlaced`, `PaymentFailed`, `CustomerUpgraded`. (2) **Immutable fact**: happened and cannot be changed. (3) **Carries sufficient context**: includes all data consumers need to react without further queries. (4) **Published by aggregate**: the aggregate that caused the state change registers and publishes the event. (5) **Decouples publisher from subscribers**: `Order` publishes `OrderPlaced`; it doesn't know or care who listens (email service, analytics, loyalty points). Domain Events serve two purposes: (A) Within a bounded context: communicate state changes between aggregates without direct coupling. (B) Across bounded contexts: integrate bounded contexts via published integration events (often serialized to Kafka or RabbitMQ).

---

### 🟢 Simple Definition (Easy)

A newspaper vs. one-to-one phone calls. When something important happens (a company IPOs), the newspaper publishes the event once — anyone interested can read it. Without domain events: Order must directly call EmailService, AnalyticsService, LoyaltyService — tight coupling, Order knows about everything downstream. With domain events: Order publishes "Order Placed." EmailService reads it. AnalyticsService reads it. LoyaltyService reads it. Order doesn't know any of them. Add a new subscriber tomorrow: Order doesn't change.

---

### 🔵 Simple Definition (Elaborated)

A customer upgrades to Premium. Without domain events: `CustomerService.upgradeToPremium()` calls `emailService.sendWelcomeEmail()`, `loyaltyService.grantBonusPoints()`, `analyticsService.trackUpgrade()`, `billingService.activatePremiumFeatures()` — four direct calls, four tight couplings. Add a fifth service next month: change this method. With domain events: `customer.upgradeToPremium()` registers a `CustomerUpgradedToPremiumEvent`. After save, the event is published. Four handlers react. Next month: add a fifth handler. CustomerService and Customer: unchanged. The event is the contract; publishers and subscribers are decoupled.

---

### 🔩 First Principles Explanation

**Domain Event structure, lifecycle, and two types (domain vs. integration):**

```
DOMAIN EVENT STRUCTURE:

  A domain event contains the FACTS of what happened:

  record OrderPlacedEvent(
      OrderId orderId,             // Which order?
      CustomerId customerId,       // Who placed it?
      Money total,                 // For how much?
      List<OrderItemSummary> items, // What was ordered?
      Instant occurredAt            // When?
  ) implements DomainEvent {}

  NAMING CONVENTIONS:
    ✓ Past tense: OrderPlaced, PaymentFailed, AccountFrozen, InventoryReserved.
    ✗ Present/command: PlaceOrder, ProcessPayment, FreezeAccount (those are Commands).

  SELF-CONTAINED:
    Include all context handlers need WITHOUT them querying back:
    ✓ OrderPlacedEvent(orderId, customerId, total, items, deliveryAddress, occurredAt)
    ✗ OrderPlacedEvent(orderId)  // Handlers must query Order to get details — coupling back

  IMMUTABLE:
    Events are historical facts. Immutable record: cannot be changed after creation.

DOMAIN EVENT LIFECYCLE:

  Step 1: REGISTER (aggregate records event during state change):

    class Order {
        private final List<DomainEvent> events = new ArrayList<>();

        public void place(Customer customer, Cart cart) {
            // State transition:
            this.status = OrderStatus.PENDING;
            this.placedAt = Instant.now();

            // Register event (not published yet):
            events.add(new OrderPlacedEvent(
                id, customer.id(), cart.total(), cart.itemSummaries(), placedAt
            ));
        }

        public List<DomainEvent> domainEvents() { return Collections.unmodifiableList(events); }
        public void clearEvents() { events.clear(); }
    }

  Step 2: PUBLISH (application service publishes after saving):

    @Transactional
    void placeOrder(PlaceOrderCommand cmd) {
        Customer customer = customerRepo.findById(cmd.customerId())...;
        Cart cart = cartRepo.findById(cmd.cartId())...;

        // Domain operation — events registered inside:
        Order order = Order.place(customer, cart);

        // Persist first (domain events are facts about persisted state):
        orderRepo.save(order);

        // Publish AFTER successful save:
        order.domainEvents().forEach(eventBus::publish);
        order.clearEvents();
    }

  IMPORTANT: Publish AFTER save, not during domain operation.
  Reason: event states a fact. Fact not true until saved.
  If event published before save, save fails → subscribers act on a fact that didn't happen.

  Step 3: HANDLE (subscribers react):

    @EventHandler
    class OrderPlacedEmailHandler {
        void on(OrderPlacedEvent event) {
            emailService.sendOrderConfirmation(
                event.customerId(),
                event.orderId(),
                event.total()
            );
        }
    }

    @EventHandler
    class LoyaltyPointsHandler {
        void on(OrderPlacedEvent event) {
            loyaltyService.grantPoints(event.customerId(), event.total());
        }
    }

    // Order: knows nothing about EmailHandler or LoyaltyHandler.

TWO TYPES OF EVENTS:

  1. DOMAIN EVENT (internal to one bounded context):

     - Published within the same JVM or same service.
     - Synchronous or in-memory async.
     - Spring: @ApplicationEventPublisher, @TransactionalEventListener.
     - Payload: rich domain types (OrderId, Money, CustomerId).
     - No serialization needed (same JVM).

     Use: decouple modules WITHIN a service.

     OrderService publishes OrderPlacedEvent.
     InventoryService (same bounded context) handles it.

  2. INTEGRATION EVENT (across bounded contexts or services):

     - Published to message broker (Kafka, RabbitMQ, SNS).
     - Serialized (JSON, Avro, Protobuf).
     - Asynchronous. At-least-once delivery.
     - Payload: primitive types (strings, numbers) — no domain-specific types.
     - Must include version or schema (consumers may run on different versions).

     Use: communicate business facts across service boundaries.

     OrderService publishes OrderPlacedIntegrationEvent to Kafka.
     ShippingService (different service) consumes it.
     NotificationService (different service) consumes it.

     // Integration event: serializable, versionable:
     record OrderPlacedIntegrationEvent(
         String orderId,         // String, not OrderId (cross-service)
         String customerId,
         String amount,
         String currency,
         List<Map<String, Object>> items,
         String occurredAt,      // ISO-8601 string
         int eventVersion        // For schema evolution
     ) {}

TRANSACTIONAL OUTBOX (publishing guarantee):

  Problem: Publish event AND save order in same transaction.
  If save succeeds but publish fails: order saved, event not published — inconsistency.

  Solution: Outbox pattern — save event TO DATABASE in same transaction as save:

    @Transactional
    void placeOrder(PlaceOrderCommand cmd) {
        Order order = Order.place(customer, cart);
        orderRepo.save(order);

        // Save event to outbox table in SAME transaction:
        outboxRepo.save(new OutboxEvent(
            "OrderPlaced",
            objectMapper.writeValueAsString(new OrderPlacedEvent(...))
        ));
        // Transaction commits: both order and event saved atomically.
        // Outbox publisher (separate process) reads outbox and publishes to Kafka.
    }
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Domain Events:

- `OrderService.placeOrder()` directly calls `EmailService`, `InventoryService`, `LoyaltyService`, `AnalyticsService`
- Order module coupled to 4+ other modules: change any one of them, risk breaking OrderService
- Adding a new reaction: modify `placeOrder()` — core business use case affected by unrelated concerns

WITH Domain Events:
→ `Order.place()` registers `OrderPlacedEvent`: knows nothing about who handles it
→ Add new handler (FraudDetectionHandler): Order and OrderService unchanged
→ Test Order.place() independently: no email, no loyalty, no analytics dependencies

---

### 🧠 Mental Model / Analogy

> A smoke detector vs. one-to-one calls. When fire is detected, the smoke detector publishes a signal (alarm event). The fire station responds. The sprinklers activate. The building PA announces evacuation. The elevator stops at the nearest floor. The smoke detector doesn't call each of these separately — it publishes the fact. Each responder is configured to react. Add building security camera recording next month: wire it to the smoke detector signal; the detector is unchanged. Domain events work the same way.

"Smoke detector alarm" = domain event (fact published)
"Fire station responds" = event handler reacting
"Detector doesn't know who responds" = publisher-subscriber decoupling
"Add camera recording without changing detector" = add handler without changing publisher

---

### ⚙️ How It Works (Mechanism)

```
DOMAIN EVENT FLOW (Spring @TransactionalEventListener):

  HTTP Request → PlaceOrderService.placeOrder()
      │
      ├─ Cart.checkout() → Order (event registered inside)
      ├─ orderRepo.save(order)           [TRANSACTION commits]
      └─ eventPublisher.publish(events)  [after transaction]
                │
                ├─ @TransactionalEventListener AFTER_COMMIT
                ├─ OrderConfirmationEmailHandler.on(event)
                ├─ InventoryReservationHandler.on(event)
                └─ LoyaltyPointsHandler.on(event)
```

---

### 🔄 How It Connects (Mini-Map)

```
Aggregate Root (publishes domain events on state change)
        │
        ▼
Domain Events ◄──── (you are here)
(immutable fact; past tense; published after save; decouples publishers from handlers)
        │
        ├── Event Sourcing: domain events AS the source of truth (stored, replayed)
        ├── Saga Pattern: uses domain events to coordinate multi-step business processes
        ├── CQRS: domain events on write side trigger read model updates
        └── Outbox Pattern: guarantees domain events are published atomically with saves
```

---

### 💻 Code Example

```java
// Domain event (immutable, past tense, self-contained):
public record PaymentFailedEvent(
    OrderId orderId,
    CustomerId customerId,
    Money attemptedAmount,
    String failureReason,
    Instant occurredAt
) implements DomainEvent {}

// Aggregate registers event:
public class Order {
    private final List<DomainEvent> events = new ArrayList<>();

    public void recordPaymentFailure(PaymentResult result) {
        if (status != OrderStatus.AWAITING_PAYMENT)
            throw new InvalidOrderStateException(status, "recordPaymentFailure");
        this.status = OrderStatus.PAYMENT_FAILED;
        this.failureReason = result.errorCode();

        // Register: event stored in aggregate, published by service later.
        events.add(new PaymentFailedEvent(id, customerId, total, result.errorCode(), Instant.now()));
    }

    public List<DomainEvent> domainEvents() { return List.copyOf(events); }
    public void clearEvents() { events.clear(); }
}

// Spring @TransactionalEventListener (fires AFTER transaction commits):
@Component
class PaymentFailedRetryHandler {
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    void on(PaymentFailedEvent event) {
        // Safely retry: order IS saved (AFTER_COMMIT guarantees it).
        retryQueue.scheduleRetry(event.orderId(), event.customerId(), event.attemptedAmount());
    }
}

@Component
class PaymentFailedNotificationHandler {
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    void on(PaymentFailedEvent event) {
        notificationService.notifyPaymentFailed(event.customerId(), event.orderId());
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Domain events and integration events are the same      | Different. Domain events: within one bounded context/service; may use rich domain types; often synchronous or in-memory; no versioning required. Integration events: cross service/context boundaries; must be serialized (JSON/Avro); primitive types; must include version for schema evolution. Often a domain event triggers creation of an integration event (via an anti-corruption layer) |
| Events should be published inside the domain operation | No. The pattern: aggregate REGISTERS events during state change; application service PUBLISHES events after persisting. If published during the domain operation: event fired before the state is durably saved — handlers react to a fact that may not be committed. Pattern: save first, then publish. `@TransactionalEventListener(AFTER_COMMIT)` in Spring guarantees this                   |
| Every state change needs a domain event                | Not every state change is a significant business fact. Adding a logging timestamp: not a domain event. But: `OrderPlaced`, `PaymentFailed`, `CustomerSuspended`, `InventoryDepleted` — these are significant business moments. Rule: if a domain expert would say "when X happens, we need to..." — X should be a domain event                                                                   |

---

### 🔥 Pitfalls in Production

**Event published before transaction commits — handlers see uncommitted state:**

```java
// BAD: Publishing event inside @Transactional before commit:
@Transactional
void placeOrder(PlaceOrderCommand cmd) {
    Order order = Order.place(customer, cart);
    orderRepo.save(order);

    // BAD: @EventListener fires SYNCHRONOUSLY inside the transaction:
    applicationEventPublisher.publishEvent(new OrderPlacedEvent(order.id(), ...));
    // Email handler: queries orderRepo.findById(order.id()) — might not be visible
    // if read happens in a different transaction (READ_COMMITTED).
    // If outer transaction rolls back after this: email already sent for non-existent order.
}

// FIX: Use @TransactionalEventListener with AFTER_COMMIT:
@Transactional
void placeOrder(PlaceOrderCommand cmd) {
    Order order = Order.place(customer, cart);
    orderRepo.save(order);
    applicationEventPublisher.publishEvent(new OrderPlacedEvent(order.id(), ...));
    // Publisher: stores event in Spring's event queue.
    // AFTER COMMIT: Spring fires handlers (email, etc.) — order IS committed.
}

@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
void onOrderPlaced(OrderPlacedEvent event) {
    // Order is guaranteed committed. Safe to query. Safe to notify.
    emailService.sendConfirmation(event.customerId(), event.orderId());
}
```

---

### 🔗 Related Keywords

- `Aggregate Root` — publishes domain events when its state changes
- `Event Sourcing Pattern` — domain events as the ONLY source of truth; replayed to rebuild state
- `Saga Pattern` — uses domain events to coordinate multi-step distributed transactions
- `CQRS Pattern` — domain events on write side update the read model projections
- `Outbox Pattern` — guarantees domain events are published atomically with DB saves

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Immutable past-tense business facts.      │
│              │ Published after state change. Decouple    │
│              │ publisher from reactions.                 │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple side effects from one business   │
│              │ operation; decoupling between modules;    │
│              │ audit trail; event-driven integration     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD with single side effect;      │
│              │ when synchronous response required;       │
│              │ team unfamiliar with eventual consistency │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Smoke detector: publishes the alarm;     │
│              │  fire station, sprinklers, and PA all     │
│              │  react — detector knows none of them."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Aggregate Root → Event Sourcing →         │
│              │ Saga Pattern → Outbox Pattern → CQRS      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A `CustomerDeletedEvent` is published when a customer is deleted. Three handlers react: `OrderArchivingHandler` archives all customer orders, `EmailSuppressHandler` adds the email to the suppression list, and `AnalyticsHandler` records the deletion. All three use `@TransactionalEventListener(AFTER_COMMIT)`. The `OrderArchivingHandler` takes 30 seconds for a customer with 10,000 orders. What are the implications for the HTTP request that triggered the delete? What happens if `EmailSuppressHandler` succeeds but `OrderArchivingHandler` fails? How should you design this for both performance and reliability?

**Q2.** You're designing an `OrderPlacedEvent`. The loyalty points handler needs the customer's tier (Bronze/Silver/Gold) to calculate points correctly. Option A: include `customerTier` in the event payload. Option B: handler queries `CustomerService.getCustomerTier(event.customerId())` when handling. Option C: the event includes only `orderId` and the handler queries everything it needs. Compare these options for: data consistency (tier could change between order placement and handling), event payload size, handler coupling, and what happens when the event is replayed months later for audit purposes.
