---
layout: default
title: "Event Bus Pattern"
parent: "Design Patterns"
nav_order: 37
permalink: /design-patterns/event-bus-pattern/
id: DPT-037
category: Design Patterns
difficulty: ★★★
depends_on: Observer, Pub-Sub, Event-Driven Architecture, Interface, Decoupling
used_by: GUI Frameworks, Microservices, Spring ApplicationEvents, Domain Events, Plugin Systems
related: Observer, Mediator, Publisher-Subscriber, Spring ApplicationEvent, Domain Events
tags:
  - pattern
  - deep-dive
  - architecture
  - java
  - distributed
---

# DPT-037 — Event Bus Pattern

⚡ TL;DR — Event Bus routes events from publishers to subscribers through a central hub, eliminating direct dependencies between components entirely.

| #797 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Observer, Pub-Sub, Event-Driven Architecture, Interface, Decoupling | |
| **Used by:** | GUI Frameworks, Microservices, Spring ApplicationEvents, Domain Events, Plugin Systems | |
| **Related:** | Observer, Mediator, Publisher-Subscriber, Spring ApplicationEvent, Domain Events | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An e-commerce application processes an order. `OrderService` must: update inventory, send confirmation email, update CRM, create an analytics event, and sync to a warehouse system. Without an Event Bus, `OrderService` directly calls all five services: `inventoryService.decrementStock()`, `emailService.sendConfirmation()`, `crmService.updateCustomer()`, etc. `OrderService` now depends on five services — adding a sixth (fraud detection) requires modifying `OrderService`.

**THE BREAKING POINT:**
After 18 months, `OrderService` has 12 direct service dependencies. Adding "send a push notification on iOS" requires a code change in the core business logic class. A failure in `crmService` causes `OrderService` to fail even though CRM is not critical to the order's success. Business logic and integration plumbing are tangled.

**THE INVENTION MOMENT:**
This is exactly why the Event Bus was created. `OrderService` publishes `OrderPlacedEvent`. The 12 downstream systems independently subscribe to this event. `OrderService` doesn't know who subscribes. Adding a 13th consumer is zero-change to `OrderService`.

---

### 📘 Textbook Definition

The **Event Bus** pattern is a communication infrastructure where **Publishers** emit typed events to a central bus without knowledge of **Subscribers**. The bus routes each event to all registered subscribers for that event type. Unlike Observer, where subjects know their observers, Event Bus achieves complete decoupling: publishers and subscribers know only the Event Bus interface (or event type). Subscribers register interest in specific event types; the bus dispatches events on registration match. Event Bus is the intra-process application of the Publish-Subscribe pattern.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A blackboard where anyone posts events and anyone registered for that type automatically receives them — no direct wiring.

**One analogy:**
> A radio broadcast tower. A radio station (Publisher) broadcasts on frequency 105.5 FM (event type). Anyone with a radio tuned to 105.5 FM (Subscribers) can hear it. The station doesn't know how many radios are tuned in. Listeners tune in and out freely. Adding a new listener requires no change to the station.

**One insight:**
Event Bus's key advance over Observer is that publishers do not reference subscribers even indirectly. In Observer, the Subject maintains a list of Observers. In Event Bus, neither side knows the other. The bus is the only shared knowledge — publishers know event types, subscribers declare event type interest.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Publishers must not know who consumes their events (zero coupling to subscribers).
2. Subscribers must not know who produces the events (zero coupling to publishers).
3. The event type is the shared contract — the type defines the message, not the sender or receiver.

**DERIVED DESIGN:**
Given invariants 1+2: a central registry (the Bus) maintains a multi-map: `Map<EventType, List<Subscriber>>`. Publishers call `bus.publish(event)`. Bus looks up subscribers for `event.getClass()` and dispatches to each. Subscribers call `bus.subscribe(EventType.class, handler)` to register. Neither publisher nor subscriber holds a reference to the other.

Given invariant 3: events are value objects — immutable, with no behaviour. They carry data about what happened: `OrderPlacedEvent {orderId, customerId, amount, timestamp}`. The bus routes by event type.

**THE TRADE-OFFS:**
**Gain:** Publisher-subscriber zero coupling; adding consumers requires zero changes to publishers; plugin-like extensibility; centralised event routing simplifies cross-cutting concerns (logging, tracing, retry).
**Cost:** Implicit communication — hard to trace "what consumes this event?" without IDE tooling or documentation; event types proliferate (many small events for many situations); error in one subscriber usually silently fails without affecting others (good for resilience, bad for debugging); ordering not guaranteed across subscribers; synchronous event buses can block publishers if subscribers are slow.

---

### 🧪 Thought Experiment

**SETUP:**
User registration triggers: email confirmation, CRM record creation, analytics, and welcome coupon generation.

**WITHOUT EVENT BUS:**
`UserService.register()` calls 4 services directly. Adding 5th (partner reward) = modify `UserService`. CRM failure = registration failure (even though CRM is non-critical). Test: must mock all 4 dependencies.

**WITH EVENT BUS:**
`UserService.register()` publishes `UserRegisteredEvent`. 4 handlers subscribed independently. Adding 5th handler = new subscriber class registered to bus (zero `UserService` changes). CRM handler failure → logged; other handlers continue; registration succeeds. Test: publish event, assert bus received it — no mock of downstream services needed.

**THE INSIGHT:**
Event Bus transforms "who to notify" from the publisher's problem into the bus's concern. The publisher's only obligation is to publish a meaningful event. The consumers' only obligation is to handle it correctly.

---

### 🧠 Mental Model / Analogy

> Event Bus is like a company-wide announcement board. When HR announces "New hire starts Monday" (publishes `NewHireEvent`), every department that cares (IT provisioning, payroll, buddy assignment, parking, office manager) reads the announcement and acts on it. HR doesn't call each department. Departments check the board and act when relevant notices appear. The board is the Event Bus.

- "Announcement board" → Event Bus
- "HR posts an announcement" → publisher calls `bus.publish(event)`
- "Departments subscribed to 'New Hire' notices" → subscribers registered for `NewHireEvent`
- "Each department handles independently" → separate subscriber handlers
- "New department joining process" → new subscriber registered; HR unchanged

Where this analogy breaks down: a bulletin board is passive — readers check it when they want. An Event Bus actively dispatches to subscribers the moment an event is published. Subscribers don't poll; they're pushed to.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Event Bus is a messaging hub inside your application. Components broadcast announcements to the hub without knowing who listens. Other components register to hear specific announcements. The hub connects them without them knowing each other.

**Level 2 — How to use it (junior developer):**
Google Guava provides `EventBus`. Spring provides `ApplicationEventPublisher`. Define event classes (POJOs). Publisher: `eventBus.post(new OrderPlacedEvent(orderId))`. Subscriber: annotate a method with `@Subscribe` (Guava) or `@EventListener` (Spring). The bus dispatches to all methods with matching parameter types. In Spring, `@EventListener` methods are discovered automatically — no explicit subscription, just the annotation.

**Level 3 — How it works (mid-level engineer):**
Internally, an Event Bus maintains a `Multimap<Class<?>, Subscriber>`. On publish, the bus looks up all subscribers for the event class AND all supertypes (inheritance hierarchy). Google Guava's `EventBus` uses reflection to find `@Subscribe` methods at registration time; it caches them in a `SubscriberRegistry`. Dispatch is synchronous by default (`EventBus`) or asynchronous (`AsyncEventBus` with an `Executor`). Spring `ApplicationEventPublisher` dispatches synchronously by default; `@Async` on `@EventListener` makes it asynchronous with Spring's task executor. Ordering of subscribers within the same event type: Spring supports `@Order` annotation; Guava provides no ordering guarantee.

**Level 4 — Why it was designed this way (senior/staff):**
Event Bus and Domain Events (DDD) are designed together. In Domain-Driven Design, a domain event represents something significant that happened in the domain (`OrderPlacedEvent`, `PaymentFailedEvent`). Publishing domain events from the domain model via an Event Bus allows the domain model to remain pure (no cross-context dependencies) while triggering downstream effects in other bounded contexts via event handlers. The critical production challenge: transactional consistency. If `OrderService` publishes `OrderPlacedEvent` inside a database transaction, and the transaction rolls back after publishing, the event was already dispatched — downstream consumers acted on it. Solutions: (1) Publish after transaction commit (`@TransactionalEventListener(phase=AFTER_COMMIT)`); (2) Transactional Outbox Pattern — persist the event to the database atomically with the business operation, then relay asynchronously.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│  EVENT BUS — DISPATCH MECHANISM                      │
│                                                      │
│  Publisher (OrderService):                           │
│    bus.publish(new OrderPlacedEvent(orderId))        │
│         ↓                                            │
│  Event Bus:                                          │
│    subscriberMap.get(OrderPlacedEvent.class)         │
│    → [InventorySub, EmailSub, AnalyticsSub]          │
│         ↓ dispatch to each                          │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐  │
│  │ Inventory   │ │ Email        │ │ Analytics    │  │
│  │ Subscriber  │ │ Subscriber   │ │ Subscriber   │  │
│  │ onOrder()   │ │ onOrder()    │ │ onOrder()    │  │
│  └─────────────┘ └──────────────┘ └──────────────┘  │
│  (synchronous: all before publish() returns)        │
│  (async: each on separate thread — non-blocking)    │
└──────────────────────────────────────────────────────┘
```

**Synchronous vs Asynchronous dispatch:**
```
Synchronous: publisher blocks until all subscribers complete
  - Simple; immediate consistency
  - Slow subscriber slows publisher
  - Subscriber exception affects publisher's transaction

Asynchronous (@Async / AsyncEventBus):
  - Publisher returns immediately
  - Subscribers on separate threads
  - Subscriber failures do not propagate to publisher
  - No ordering guarantee
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (Spring with @Async):**
```
POST /orders → OrderController
  → orderService.placeOrder(request)
  → order saved to DB
  → eventPublisher.publishEvent(
      new OrderPlacedEvent(order.id()))
              ← YOU ARE HERE (event published)
  → Spring dispatches to 4 @EventListeners
  → InventoryListener.onOrderPlaced() [async thread 1]
  → EmailListener.onOrderPlaced() [async thread 2]
  → CrmListener.onOrderPlaced() [async thread 3]
  → AnalyticsListener.onOrderPlaced() [async thread 4]
  → HTTP 201 Created returned to client
```

**FAILURE PATH:**
```
EmailListener.onOrderPlaced() throws Exception
  → With @Async: exception logged; other listeners unaffected
  → With sync: exception propagates to publisher
              → transaction may roll back
              → order NOT saved despite email failure
Fix: use @TransactionalEventListener + @Async for critical
     events requiring transactional safety
```

**WHAT CHANGES AT SCALE:**
In-process Event Bus is single-JVM. At 10 service instances, each instance dispatches events in-process independently — no cross-instance delivery. For cross-instance (cross-process) event propagation, replace in-process Event Bus with an external message broker (Kafka, RabbitMQ), retaining the same publisher/subscriber mental model but with network transport and durability.

---

### 💻 Code Example

**Example 1 — Spring ApplicationEvent:**
```java
// Event (value object)
public record OrderPlacedEvent(
    Long orderId,
    Long customerId,
    BigDecimal amount
) {}

// Publisher
@Service
public class OrderService {
    private final ApplicationEventPublisher bus;
    private final OrderRepository repo;

    public Order placeOrder(OrderRequest request) {
        Order order = repo.save(new Order(request));
        // Publish AFTER save — event carries saved order id
        bus.publishEvent(
            new OrderPlacedEvent(
                order.id(), order.customerId(), order.total()));
        return order;
    }
}

// Subscriber 1 — inventory (sync, must succeed)
@Component
public class InventoryHandler {
    @EventListener
    public void onOrderPlaced(OrderPlacedEvent event) {
        inventoryService.reserve(event.orderId());
    }
}

// Subscriber 2 — email (async, non-critical)
@Component
public class EmailHandler {
    @Async
    @EventListener
    public void onOrderPlaced(OrderPlacedEvent event) {
        emailService.sendConfirmation(event.customerId());
    }
}

// Subscriber 3 — transactional: only fires after TX commit
@Component
public class AnalyticsHandler {
    @TransactionalEventListener(
        phase = TransactionPhase.AFTER_COMMIT)
    public void onOrderPlaced(OrderPlacedEvent event) {
        // Only fires if the DB transaction successfully committed
        analyticsService.recordOrder(event);
    }
}
```

**Example 2 — Google Guava EventBus:**
```java
EventBus bus = new EventBus();

// Subscriber registered manually
bus.register(new Object() {
    @Subscribe
    public void handleOrder(OrderPlacedEvent event) {
        System.out.println("Order: " + event.orderId());
    }
});

// Post event — dispatches synchronously
bus.post(new OrderPlacedEvent(42L, 99L, BigDecimal.TEN));

// Async bus: subscribers invoked on provided executor
EventBus asyncBus = new AsyncEventBus(
    Executors.newFixedThreadPool(4));
```

---

### ⚖️ Comparison Table

| Pattern | Publisher-Subscriber Coupling | Transport | Durability | Best For |
|---|---|---|---|---|
| **Event Bus** | None (via type only) | In-process | None | Intra-application decoupling |
| Observer | Subject knows observers | In-process | None | Known subscriber count |
| Message Broker (Kafka) | None | Network | Durable | Distributed, async, durable |
| Mediator | Via mediator only | In-process | None | Complex routing logic |

How to choose: use Event Bus for inter-module decoupling within a JVM. Use a Message Broker when events must cross service boundaries, survive restarts, or be delivered to subscribers not yet running.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Event Bus is the same as Observer | Observer: subject holds subscriber list; publisher knows something about observers. Event Bus: neither publisher nor subscriber holds a reference to the other; the bus is the only shared point |
| Events must be immutable | Not enforced by the bus, but strongly recommended. Mutable events shared across subscribers create concurrency bugs |
| Event Bus handles exactly-once delivery | In-process Event Bus provides at-most-once (synchronous: exactly once if no exception; async: at-most-once if subscriber crashes) |
| All subscribers are called in order | Subscriber invocation order is implementation-specific. Guava EventBus makes no ordering guarantee. Spring uses @Order but only for the same ApplicationListener priority level |
| Event Bus replaces dependency injection | They serve different purposes. DI manages object creation and collaboration. Event Bus manages runtime communication and decoupling |

---

### 🚨 Failure Modes & Diagnosis

**1. Ghost Events — Published Before Transaction Commits**

**Symptom:** Email confirmation sent to customer but order not found in database (customer received email for non-existent order). Intermittent, correlates with DB failures or rollbacks.

**Root Cause:** `@EventListener` fires synchronously inside the transaction. If the transaction rolls back after the event is dispatched, the email was already sent but the order was not saved.

**Diagnostic:**
```bash
grep "OrderPlacedEvent\|rollback" logs/app.log \
  | grep -A 2 "OrderPlacedEvent"
# If rollback follows shortly after event: ghost event
```

**Fix:**
```java
// Use AFTER_COMMIT phase — only fires on successful commit
@TransactionalEventListener(
    phase = TransactionPhase.AFTER_COMMIT)
public void onOrderPlaced(OrderPlacedEvent e) {
    emailService.sendConfirmation(e.customerId());
}
```

**Prevention:** All subscribers with external side effects MUST use `@TransactionalEventListener(AFTER_COMMIT)`.

---

**2. Subscriber Exception Causes Publisher Transaction Rollback**

**Symptom:** Order processing fails with `MailException: SMTP connection refused`. Order fails even though the order save succeeded. Inventory not reserved.

**Root Cause:** Synchronous `@EventListener` throws an exception. Spring propagates it to the publisher, causing the transaction to roll back. A non-critical downstream system failure aborts a critical business operation.

**Diagnostic:**
```bash
grep "MailException\|Rollback" logs/app.log
# If MailException precedes "Rollback" and no order in DB:
# synchronous event listener caused rollback
```

**Fix:**
```java
// GOOD: isolate non-critical handlers with @Async
@Async
@EventListener
public void onOrderPlaced(OrderPlacedEvent e) {
    try {
        emailService.sendConfirmation(e.customerId());
    } catch (MailException ex) {
        log.warn("Email failed for order {}", e.orderId(), ex);
        // Failure logged; order is unaffected
    }
}
```

**Prevention:** Non-critical side effects (email, analytics, CRM) must be `@Async`. Critical side effects (inventory, payment) may be synchronous but must be wrapped in try/catch with a compensating action.

---

**3. Memory Leak — Bus Holds Strong References to Subscribers**

**Symptom:** Heap grows after millions of operations. Memory profiler shows thousands of subscriber instances in the Guava EventBus registry.

**Root Cause:** Guava `EventBus.register(subscriber)` holds a strong reference. If subscriber objects are created per-session or per-request and `unregister()` is never called, they accumulate.

**Diagnostic:**
```bash
jmap -histo:live <PID> | grep "EventHandler\|Subscriber"
# Growing count: unregistered subscribers accumulating
```

**Fix:**
```java
// Always unregister when subscriber is no longer needed:
eventBus.unregister(handler);
// Or: use Spring's @EventListener (Spring manages lifecycle)
// Or: WeakReference-based bus (custom implementation)
```

**Prevention:** For Guava EventBus, always call `unregister()` in `destroy()` or `close()` methods. Prefer Spring's `@EventListener` which ties lifecycle to bean lifecycle automatically.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Observer` — Event Bus is a generalisation of Observer where the subject (publisher) does not hold subscriber references; understanding Observer's limitations motivates the Event Bus
- `Pub-Sub` — Event Bus is the intra-process implementation of the Pub-Sub pattern; understanding Pub-Sub's decoupling model drives Event Bus design
- `Event-Driven Architecture` — Event Bus is the in-process implementation of the event-driven principal; EDA applies the same decoupling at the distributed system level

**Builds On This (learn these next):**
- `Transactional Outbox Pattern` — solves the Event Bus's transactional ghost-event problem at scale by persisting events to the database atomically
- `Domain Events` — DDD's formalisation of events published from within domain model classes; Event Bus is the typical delivery mechanism
- `Message Broker (Kafka, RabbitMQ)` — distributed Event Bus with durability, cross-JVM delivery, and consumer groups

**Alternatives / Comparisons:**
- `Observer` — tighter coupling (subject knows observers); better when publishers need to control subscription
- `Mediator` — routes communication with explicit logic; Event Bus routes by type only, with no routing logic
- `Message Broker` — durable, cross-process events; Event Bus is in-process only

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Central hub routing typed events from     │
│              │ publishers to subscribers with no wiring  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Publisher accumulates direct dependencies │
│ SOLVES       │ on all consumers; adding consumers =      │
│              │ modifying publisher                       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The event TYPE is the only contract;      │
│              │ publisher and subscriber never reference  │
│              │ each other                                │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple independent consumers react to   │
│              │ one domain event; new consumers expected  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Strict delivery guarantees needed;        │
│              │ use Message Broker for durability         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Zero publisher-subscriber coupling vs     │
│              │ implicit dispatch (hard to trace)         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Broadcast it; whoever cares will hear."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Domain Events → Transactional Outbox →    │
│              │ Message Broker (Kafka)                    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An `OrderService` publishes `OrderPlacedEvent` using Spring's `ApplicationEventPublisher`. Four `@EventListener` methods handle it: `InventoryListener` (synchronous, reduces stock), `EmailListener` (@Async, sends email), `FraudDetector` (synchronous, must run BEFORE inventory), and `AnalyticsRecorder` (@TransactionalEventListener AFTER_COMMIT). Describe exactly in what order and on what threads these four handlers will execute, and identify which combinations of failures can leave the system in an inconsistent state.

**Q2.** A team migrates from an in-process Spring `ApplicationEventPublisher` to Kafka topics for cross-service event propagation. They find that `@TransactionalEventListener(AFTER_COMMIT)` no longer provides the same transactional guarantee — a Kafka publish can fail even after the DB transaction committed. Identify two distinct failure modes this creates that didn't exist with the in-process bus, and describe the Transactional Outbox Pattern as the complete solution to both.

