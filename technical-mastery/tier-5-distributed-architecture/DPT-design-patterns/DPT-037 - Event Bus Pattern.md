---
id: DPT-037
title: Event Bus Pattern
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-005, DPT-025, DPT-032, DPT-036
used_by: DPT-064
related: DPT-025, DPT-032, DPT-036, DPT-039, DPT-053
tags:
  - pattern
  - event-driven
  - advanced
  - publish-subscribe
  - decoupling
  - spring-events
  - guava
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 37
permalink: /technical-mastery/design-patterns/event-bus/
---

⚡ TL;DR - Event Bus decouples publishers from subscribers
by providing a central channel: publishers emit named
events; any registered subscribers receive them without
the publisher knowing who is listening or how many.

| #37 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-025, DPT-032, DPT-036 | |
| **Used by:** | DPT-064 | |
| **Related:** | DPT-025, DPT-032, DPT-036, DPT-039, DPT-053 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An order service needs to notify: (1) inventory service
(reduce stock), (2) notification service (send email),
(3) analytics service (record event), (4) shipping service
(prepare fulfillment) when an order is placed.

**DIRECT COUPLING:**
```java
class OrderService {
    @Autowired InventoryService inv;
    @Autowired NotificationService notif;
    @Autowired AnalyticsService analytics;
    @Autowired ShippingService shipping;

    void placeOrder(Order o) {
        order.save(o);
        inv.reduceStock(o.items());         // direct call #1
        notif.sendConfirmation(o);          // direct call #2
        analytics.recordOrderEvent(o);      // direct call #3
        shipping.prepareFulfillment(o);     // direct call #4
    }
}
```

**THE PROBLEMS:**
1. Adding a loyalty points service: modify `OrderService`.
2. If `NotificationService` is slow: `placeOrder` blocks.
3. If `ShippingService` is down: the whole order fails.
4. Testing `OrderService`: must mock 4 dependencies.
5. `OrderService` knows about downstream implementation details.

**THE INVENTION MOMENT:**
Event Bus: `OrderService` publishes `OrderPlacedEvent` to
the bus. All interested services subscribe to
`OrderPlacedEvent`. `OrderService` knows nothing about
its subscribers. Adding loyalty points: register a new
subscriber. Slow notification service: async subscriber,
does not block order service. Zero changes to OrderService
for each new consumer.

**EVOLUTION:**
Spring's `ApplicationEventPublisher` + `@EventListener`.
Guava's `EventBus`. Google's protocol: Android `EventBus`
(deprecated). Kafka, RabbitMQ: Event Bus at the distributed/
persistent layer. AWS EventBridge: managed Event Bus.

---

### 📘 Textbook Definition

The **Event Bus** pattern is a publish-subscribe messaging
pattern that provides a central communication channel
(the Bus) between publishers and subscribers. Publishers
emit events to the Bus without knowing who subscribes.
Subscribers register interest in specific event types
and receive callbacks when those events are published.
The Bus handles routing: matching events to registered
handlers. The pattern decouples publishers and subscribers
in both time (async buses) and identity (neither knows
the other). Event Bus is an in-process (or in-cluster)
generalization of the Observer pattern to a multi-publisher,
multi-subscriber, named-event architecture.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Event Bus is a shared channel where anyone can publish
events and anyone can subscribe to them - no direct
connections between publisher and subscriber.

**One analogy:**
> A public radio broadcast tower (Event Bus). Radio
> stations (publishers) broadcast on frequencies (event
> types). Any radio (subscriber) tuned to that frequency
> hears the broadcast. The broadcaster does not know
> how many radios are tuned in. A radio can tune to
> multiple frequencies. A frequency can have multiple
> broadcasters. Complete decoupling.

**One insight:**
Event Bus vs Observer pattern: Observer requires the
publisher to explicitly know its subscribers (`list.add(listener)`).
Event Bus: publisher and subscriber do NOT reference
each other - they only reference the Bus. This is the
key architectural difference: Event Bus adds a level
of indirection that eliminates the circular dependency
between publisher and subscriber.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Publisher calls `bus.publish(event)` - does NOT call
   subscribers directly.
2. Subscriber calls `bus.subscribe(EventType, handler)` -
   does NOT reference the publisher.
3. The Bus routes events: for each published event,
   call all handlers registered for that event type.
4. Synchronous bus: handlers run on publisher's thread
   (blocking). Asynchronous bus: handlers run on worker
   threads (non-blocking for publisher).

**EVENT TYPE ROUTING:**
The Bus maintains a `Map<Class<? extends Event>, List<EventHandler>>`.
When `publish(event)` is called: look up handlers for
`event.getClass()` and invoke each.

**SYNC VS ASYNC:**
- **Synchronous** (Spring's default `ApplicationEventPublisher`):
  handlers run on the publisher's thread. If any handler
  throws: exception propagates to publisher. If any handler
  is slow: publisher is blocked.
- **Asynchronous** (`@Async @EventListener` in Spring):
  handlers run on separate threads. Publisher is not
  blocked. Exceptions are not propagated to publisher
  (must use error handlers).

**TRADE-OFFS:**

**Gain:** Publisher-subscriber decoupling. Easy extensibility
(add subscribers without publisher changes). Natural
cross-cutting concerns (audit, metrics, notifications).

**Cost:** Debugging is harder (control flow is invisible:
who handles this event?). Ordering is not guaranteed
(unless explicitly configured). Circular event loops
(A publishes event X, handler for X publishes event Y,
handler for Y publishes event X: infinite loop). Event
schema evolution: subscribers break if event fields change.
Memory leaks: subscribers not unregistered hold references.

---

### 🧪 Thought Experiment

**SETUP:**
User registration flow. After user is created: send welcome
email, create default settings, update user count metric,
send to marketing platform, start onboarding workflow.

**WITHOUT EVENT BUS:**
`UserService.createUser()` calls 5 services directly.
Adding "send to CRM": modify `UserService`.

**WITH EVENT BUS:**
`UserService.createUser()` publishes `UserCreatedEvent`.
5 subscribers each handle independently.
Adding CRM integration: register a 6th subscriber.
`UserService`: UNCHANGED.

---

### 🧠 Mental Model / Analogy

> Event Bus is a POST OFFICE SORTING ROOM. Senders
> (publishers) drop letters (events) in the inbox with
> a category (event type) written on the envelope.
> The sorting room (bus) routes each letter to all mailboxes
> (subscribers) registered for that category. Senders
> don't know how many people get the letter. Recipients
> don't know who sent it. The sorting room is the only
> shared reference.

- "Sender drops letter" = publisher.publish(event)
- "Category on envelope" = event.getClass()
- "Sorting room routes" = bus's handler registry
- "Mailboxes" = subscriber handler lists
- "Reading the letter" = handler.handle(event)

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Event Bus is a "town crier" system. Instead of one service
calling another directly, services shout events into
the air ("Order placed!"). Any service that wants to
know about orders can listen. The shouter never knows
who is listening; the listeners never know who shouted.

**Level 2 - How to use it (junior developer):**
In Spring: `@EventListener` on a method to subscribe.
`ApplicationEventPublisher.publishEvent(event)` to publish.
Create a POJO event class. Use `@Async @EventListener`
for non-blocking handlers. Mark event class as extending
`ApplicationEvent` (optional in Spring 4.2+).

**Level 3 - How it works (mid-level engineer):**
Spring's `ApplicationEventMulticaster` is the bus.
When `publisher.publishEvent(event)` is called:
`SimpleApplicationEventMulticaster.multicastEvent()` looks
up all `ApplicationListener` beans registered for the
event type (via `GenericApplicationListener.supportsEventType`).
For synchronous: calls each listener's `onApplicationEvent(event)`
on the calling thread. For `@Async`: submits to the
task executor. Ordering: use `@Order(1)` on listeners
to control invocation sequence.
Spring's built-in events (`ContextRefreshedEvent`,
`ContextClosedEvent`, `ApplicationStartedEvent`) are
published via the same mechanism - the Event Bus is
not just for application events.

**Level 4 - Why it was designed this way (senior/staff):**
Event Bus solves the LAYERING violation in enterprise
architectures. A `UserService` in the domain layer should
not know about `EmailService` (infrastructure layer) or
`MarketingPlatformService` (external integration). Calling
them directly creates dependencies from domain to infrastructure.
Event Bus inverts this: `UserService` publishes a domain
event (`UserCreatedEvent`). Infrastructure adapters subscribe
to the event. The domain layer is pure: it only publishes
events; it never calls infrastructure services. This
is the foundation of Hexagonal Architecture: domain
events are the domain's "output"; adapters translate
these events into external calls. Domain does not import
infrastructure; infrastructure imports domain. Clean
dependency graph.

**Level 5 - Mastery (distinguished engineer):**
Event Bus's scope: in-process (Spring `ApplicationEventPublisher`),
in-cluster (Kafka, RabbitMQ), cloud-wide (AWS EventBridge,
Google Eventarc). The architectural principle is the same:
publish once, many subscribers receive. The challenge
scales with scope:
- In-process: event loss on crash (events in memory).
  Solution: transactional outbox (DPT-053) + external
  message broker.
- In-cluster: message broker provides durability (disk)
  and ordering (per partition in Kafka). Consumer groups
  allow horizontal scaling of handlers.
- Cloud-wide: EventBridge routes events between AWS
  services based on event patterns (event filtering rules).
  Each service subscribes with a filter; the bus only
  delivers matching events.
The central challenge across all scopes: event schema evolution.
When `UserCreatedEvent` adds a new field: consumers must
handle both old and new versions. Solutions: versioned
events (`UserCreatedV2Event`), schema registry (Confluent),
or consumer-driven contracts (Pact).

---

### ⚙️ How It Works (Mechanism)

```
Event Bus Routing
┌─────────────────────────────────────────────────────────┐
│                                                         │
│ Bus internal state:                                     │
│ Map<Type, List<Handler>>:                               │
│   OrderPlacedEvent → [invHandler, notifHandler,         │
│                        analyticsHandler, shippingHandler│
│   UserCreatedEvent → [emailHandler, settingsHandler]    │
│                                                         │
│ publish(new OrderPlacedEvent(order)):                   │
│   type = OrderPlacedEvent.class                         │
│   handlers = map.get(type)                              │
│   for handler in handlers:                              │
│     if (async): executor.submit(() -> handler.handle(e))│
│     if (sync):  handler.handle(e) // on caller's thread │
│                                                         │
│ subscribe(OrderPlacedEvent.class, h):                   │
│   map.computeIfAbsent(OrderPlacedEvent.class, ...).add(h│
│                                                         │
│ Adding a 5th subscriber (loyalty points):               │
│   loyaltyHandler registered → map updated               │
│   OrderService code: UNCHANGED                          │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Order placement with Spring Event Bus:

1. POST /orders → OrderController →
  OrderService.placeOrder(order)

2. OrderService:
   order.save(order);
   publisher.publishEvent(new OrderPlacedEvent(order));
   return "202 Accepted";  // fast return

3. Spring ApplicationEventMulticaster routes
  OrderPlacedEvent:
   @EventListener InventoryHandler.handle(event) → reduce
     stock
   @Async @EventListener EmailHandler.handle(event) → send
     email
   @Async @EventListener AnalyticsHandler.handle(event) →
     record

4. Adding LoyaltyPointsService:
   @EventListener LoyaltyHandler.handle(OrderPlacedEvent
     e) {
       loyaltyService.awardPoints(e.customer(), e.total());
   }
   // OrderService: UNCHANGED. Zero modification.

Failure isolation:
   EmailHandler throws EmailException → only that handler
     fails
   OrderService and other handlers: unaffected (@Async)
```

---

### 💻 Code Example

**Example 1 - Direct coupling (tight dependencies):**

```java
// BAD: OrderService knows about all downstream services
@Service
class OrderService {
    @Autowired private InventoryService inventory;
    @Autowired private EmailService email;
    @Autowired private AnalyticsService analytics;
    @Autowired private ShippingService shipping;
    // Adding loyalty: add another dependency here

    @Transactional
    void placeOrder(Order order) {
        orderRepo.save(order);
        inventory.reduceStock(order.items());   // if slow: blocks
        email.sendConfirmation(order);          // if down: fails
        analytics.record(order);               // unrelated concern
        shipping.prepare(order);               // unrelated concern
        // OrderService: knows too much
    }
}
```

**Example 2 - Spring Event Bus:**

```java
// GOOD: OrderService publishes, doesn't call subscribers

// EVENT: plain POJO (no ApplicationEvent base required in Spring
// 4.2+)
class OrderPlacedEvent {
    private final Order order;
    private final Instant occurredAt;

    OrderPlacedEvent(Order order) {
        this.order = order;
        this.occurredAt = Instant.now();
    }

    Order getOrder() { return order; }
    Instant getOccurredAt() { return occurredAt; }
}

// PUBLISHER: OrderService knows only the bus
@Service
class OrderService {
    @Autowired private OrderRepository orderRepo;
    @Autowired private ApplicationEventPublisher eventBus;

    @Transactional
    void placeOrder(Order order) {
        orderRepo.save(order);
        // Publish event: no knowledge of subscribers
        eventBus.publishEvent(new OrderPlacedEvent(order));
        // Returns immediately (synchronous handlers run here)
    }
}

// SUBSCRIBERS: completely decoupled from OrderService

@Service
class InventoryEventHandler {
    @EventListener
    // Runs synchronously on OrderService's thread
    // Participates in the same transaction (if any)
    void handleOrderPlaced(OrderPlacedEvent event) {
        inventoryService.reduceStock(event.getOrder().items());
    }
}

@Service
class EmailEventHandler {
    @Async              // Runs on async thread pool
    @EventListener      // Non-blocking for publisher
    void handleOrderPlaced(OrderPlacedEvent event) {
        try {
            emailService.sendOrderConfirmation(event.getOrder());
        } catch (Exception e) {
            log.error("Email send failed for order {}",
                event.getOrder().id(), e);
            // Do NOT rethrow in @Async: publisher won't see it anyway
        }
    }
}

// Adding loyalty service: new class, no changes to OrderService
@Service
class LoyaltyEventHandler {
    @Async
    @EventListener
    void handleOrderPlaced(OrderPlacedEvent event) {
        loyaltyService.awardPoints(
            event.getOrder().customerId(),
            event.getOrder().total());
    }
}
```

**Example 3 - Ordered handlers + Condition-based filtering:**

```java
// Control handler execution order
@EventListener
@Order(1) // runs first
void validateInventory(OrderPlacedEvent event) {
    // Runs before all other handlers
    inventory.validateStock(event.getOrder().items());
}

@EventListener
@Order(2) // runs after validation
void updateInventory(OrderPlacedEvent event) {
    inventory.reduceStock(event.getOrder().items());
}

// Conditional handler: only runs for premium orders
@EventListener(condition = "#event.order.total > 100")
void sendPremiumGift(OrderPlacedEvent event) {
    giftService.sendPremiumWelcome(event.getOrder().customerId());
}
```

**Example 4 - Guava EventBus (non-Spring):**

```java
// Guava EventBus for non-Spring applications

import com.google.common.eventbus.*;

EventBus bus = new EventBus("order-events");
// Async: AsyncEventBus bus = new AsyncEventBus(executor);

// Subscriber: annotate method with @Subscribe
class InventorySubscriber {
    @Subscribe
    public void handleOrder(OrderPlacedEvent event) {
        inventory.reduceStock(event.getOrder().items());
    }
}

bus.register(new InventorySubscriber());
bus.register(new EmailSubscriber());

// Publisher: post event to bus
bus.post(new OrderPlacedEvent(order));
// Routes to all @Subscribe methods for OrderPlacedEvent
```

---

### ⚖️ Comparison Table

| Pattern | Publisher awareness of subscribers | Async | Persistent | Scope |
|---|---|---|---|---|
| Observer | Yes (explicit list) | Optional | No | In-object |
| **Event Bus** | No (via Bus) | Optional | No | In-process |
| Guava EventBus | No (via Bus) | Optional | No | In-process |
| Kafka topic | No (via Kafka) | Yes | Yes | Distributed |
| AWS EventBridge | No (via AWS) | Yes | Yes | Cloud-wide |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Event Bus replaces direct service calls | For critical path operations (reducing inventory during checkout), synchronous direct calls with clear transaction semantics may be more appropriate. Event Bus is best for cross-cutting concerns (email, analytics, audit) that can fail independently of the main transaction |
| Synchronous event listeners are safe to use for all cases | Synchronous listeners run on the publisher's thread and participate in the same transaction. If a listener throws, it rolls back the PUBLISHER'S transaction. Use @Async for non-critical handlers |
| Events are guaranteed to be delivered | In-process Event Bus: events are lost if the process crashes during processing. For guaranteed delivery: use the Transactional Outbox Pattern (DPT-053) to persist the event in the same transaction as the business data, then deliver to an external broker |
| Guava's EventBus is equivalent to Spring's ApplicationEventPublisher | Guava EventBus requires explicit register/unregister and does NOT integrate with Spring's transaction context. Spring's publisher participates in transactions (synchronous listeners), handles ordered dispatching, and integrates with Spring's async executor |

---

### 🚨 Failure Modes & Diagnosis

**Circular Event Loop**

**Symptom:**
`StackOverflowError` or infinite log output. A handler
publishes another event whose handler publishes the first
event: infinite recursion.

**Root Cause:**
Handler A processes `OrderPlacedEvent` and publishes
`InventoryUpdatedEvent`. Handler B processes
`InventoryUpdatedEvent` and re-publishes `OrderPlacedEvent`.
Infinite loop.

**Diagnosis:**
Enable event tracing. Look for the same event type appearing
multiple times in the call stack.

**Fix:**
Break the cycle: mark one event handler with a guard
flag. Or: redesign the event graph to be acyclic.
Use Spring's `@TransactionalEventListener(phase = AFTER_COMMIT)`
to publish downstream events only after the transaction
commits (prevents re-entrancy during the same unit of work).

---

**Subscriber Memory Leak (Classic with Guava EventBus)**

**Symptom:**
Memory grows over time. GC logs show increasing object
count. `EventBus` holds references to subscriber objects
that should have been garbage collected.

**Root Cause:**
Subscribers registered with `bus.register(subscriber)`
but never unregistered with `bus.unregister(subscriber)`.
The EventBus holds a strong reference, preventing GC.

**Fix:**
```java
// Lifecycle-aware subscriber management
class MySubscriber {
    private final EventBus bus;

    @PostConstruct // Spring lifecycle hook
    void init() { bus.register(this); }

    @PreDestroy // Spring lifecycle hook
    void destroy() { bus.unregister(this); }
}
// Spring's ApplicationEventPublisher manages this automatically
// Guava's EventBus requires manual register/unregister
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Observer` - DPT-025; Event Bus is Observer without
  direct publisher-subscriber coupling
- `Producer-Consumer` - DPT-032; the async Event Bus
  uses Producer-Consumer with the bus as the queue

**Builds On This (learn these next):**
- `Outbox Pattern` - DPT-053; guarantees event delivery
  across service boundaries via the transactional outbox
- `CQRS Pattern` - DPT-052; events from the command side
  update the query side via an event bus

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Central channel: publisher posts events; │
│              │ subscribers registered by event type     │
├──────────────┼──────────────────────────────────────────┤
│ SPRING API   │ ApplicationEventPublisher.publishEvent() │
│              │ @EventListener, @Async @EventListener    │
├──────────────┼──────────────────────────────────────────┤
│ SYNC RISK    │ Sync @EventListener participates in      │
│              │ publisher's transaction: exception rolls │
│              │ back publisher's work                    │
├──────────────┼──────────────────────────────────────────┤
│ ASYNC PREF   │ Use @Async for non-critical handlers     │
│              │ (email, analytics, audit)                │
├──────────────┼──────────────────────────────────────────┤
│ FAILURE MODE │ Circular event loop → StackOverflow;     │
│              │ subscriber not unregistered → memory leak│
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Service Locator → DI Pattern → Spec Pat. │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Event Bus decouples publisher from subscriber: publisher
   calls `bus.publish(event)` and never directly references
   subscribers. Adding subscribers does NOT change the
   publisher. This is the key advantage over direct calls.
2. Synchronous handlers run on the publisher's thread and
   participate in the same transaction. Exceptions in
   synchronous handlers propagate to the publisher. For
   non-critical handlers (email, analytics): use `@Async`.
3. In-process Event Bus loses events on crash. For guaranteed
   cross-service event delivery: combine with the Transactional
   Outbox Pattern (DPT-053) - write event to DB in the same
   transaction as the business data, then deliver to broker.

