---
layout: default
title: "Event Bus Pattern"
parent: "Design Patterns"
nav_order: 795
permalink: /design-patterns/event-bus-pattern/
number: "795"
category: Design Patterns
difficulty: ★★☆
depends_on: "Observer Pattern, Producer-Consumer Pattern, Command Pattern"
used_by: "Microservices integration, domain events, UI frameworks, plugin systems"
tags: #intermediate, #design-patterns, #event-driven, #messaging, #decoupling, #pub-sub
---

# 795 — Event Bus Pattern

`#intermediate` `#design-patterns` `#event-driven` `#messaging` `#decoupling` `#pub-sub`

⚡ TL;DR — **Event Bus** provides a centralized channel where publishers post events and subscribers receive events — decoupling publishers from subscribers completely: neither knows about the other; the bus routes events to all registered handlers.

| #795 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Observer Pattern, Producer-Consumer Pattern, Command Pattern | |
| **Used by:** | Microservices integration, domain events, UI frameworks, plugin systems | |

---

### 📘 Textbook Definition

**Event Bus**: a messaging pattern where publishers post events to a shared bus, and subscribers register to receive events of specific types. The bus decouples publishers and subscribers: publishers don't know who handles their events; subscribers don't know who produced them. Unlike Observer (subject holds direct references to observers), Event Bus introduces a broker/mediator layer. Implementations: Guava `EventBus`; Spring `ApplicationEventPublisher`; Vert.x `EventBus`; Android's `LiveData`; messaging infrastructure (Kafka, RabbitMQ) at system level. Variants: synchronous (handlers called in publisher thread), asynchronous (handlers on separate threads), distributed (events cross process boundaries).

---

### 🟢 Simple Definition (Easy)

A radio station. The station (event bus) broadcasts on frequencies (event types). Listeners (subscribers) tune in to specific frequencies. When the station plays music (event posted), all tuned-in radios receive it. The DJ doesn't know who's listening. Listeners don't know who's broadcasting. New radio: just tune in — station unchanged. Event Bus: station is the bus, DJ is publisher, radio owners are subscribers.

---

### 🔵 Simple Definition (Elaborated)

Spring `ApplicationEventPublisher` as Event Bus: `OrderService` publishes `OrderPlacedEvent`. `EmailService`, `InventoryService`, `AnalyticsService` each subscribe. When an order is placed: `OrderService` calls `eventPublisher.publishEvent(event)`. All three services receive it and handle it independently. `OrderService` doesn't import `EmailService` — zero compile-time coupling. New service (`SmsService`): add `@EventListener` method — zero changes to `OrderService`. The Event Bus (Spring's event infrastructure) routes the event to all registered listeners.

---

### 🔩 First Principles Explanation

**Event Bus vs Observer vs Mediator — and how routing and filtering work:**

```
EVENT BUS STRUCTURE:

  interface EventBus {
      <T extends Event> void publish(T event);
      <T extends Event> void subscribe(Class<T> eventType, EventHandler<T> handler);
      <T extends Event> void unsubscribe(Class<T> eventType, EventHandler<T> handler);
  }
  
  class SimpleEventBus implements EventBus {
      // Map: event type → list of handlers registered for that type
      private final Map<Class<?>, List<EventHandler<?>>> handlers = new ConcurrentHashMap<>();
      
      @Override
      public <T extends Event> void publish(T event) {
          List<EventHandler<?>> eventHandlers = handlers.getOrDefault(event.getClass(), List.of());
          for (EventHandler<?> handler : eventHandlers) {
              @SuppressWarnings("unchecked")
              EventHandler<T> typedHandler = (EventHandler<T>) handler;
              typedHandler.handle(event);
          }
          // Also notify handlers registered for superclasses/interfaces:
          // (production buses handle type hierarchy)
      }
      
      @Override
      public <T extends Event> void subscribe(Class<T> type, EventHandler<T> handler) {
          handlers.computeIfAbsent(type, k -> new CopyOnWriteArrayList<>()).add(handler);
      }
      
      @Override
      public <T extends Event> void unsubscribe(Class<T> type, EventHandler<T> handler) {
          handlers.getOrDefault(type, List.of()).remove(handler);
      }
  }
  
EVENT BUS vs OBSERVER vs MEDIATOR:

  OBSERVER:
  Subject holds direct List<Observer> references.
  Subject knows observers (implicit coupling).
  Observers receive subject's state change.
  In-process only.
  
  EVENT BUS:
  Bus is a third-party intermediary.
  Publishers and subscribers know ONLY the bus (and event types).
  Multiple publishers can publish the same event type.
  Multiple subscribers can handle the same event type.
  Can be async, persistent, distributed (Kafka).
  
  MEDIATOR:
  Mediator coordinates INTERACTIONS between components.
  Components know about mediator (not each other).
  Mediator can contain business logic to decide who to route to.
  Event Bus: typically routes all events to all registered handlers (no routing logic in bus).
  
GUAVA EventBus:

  // Guava EventBus — simple synchronous in-process event bus:
  EventBus eventBus = new EventBus("order-events");
  
  // Subscriber — annotate with @Subscribe:
  class EmailNotificationListener {
      @Subscribe
      void onOrderPlaced(OrderPlacedEvent event) {
          emailService.sendConfirmation(event.getOrderId());
      }
      
      @Subscribe
      void onOrderCancelled(OrderCancelledEvent event) {
          emailService.sendCancellation(event.getOrderId());
      }
  }
  
  // Register subscriber:
  EmailNotificationListener listener = new EmailNotificationListener();
  eventBus.register(listener);
  
  // Publisher:
  eventBus.post(new OrderPlacedEvent(order));    // synchronous: all @Subscribe methods called
  
  // Async EventBus (handles on separate thread):
  AsyncEventBus asyncBus = new AsyncEventBus("async-orders", Executors.newFixedThreadPool(4));
  asyncBus.post(new OrderPlacedEvent(order));    // returns immediately; handlers run on pool
  
SPRING APPLICATION EVENT BUS:

  // Spring: ApplicationContext IS the Event Bus.
  
  // EVENT:
  record OrderPlacedEvent(String orderId, BigDecimal total) implements ApplicationEvent {
      OrderPlacedEvent(String orderId, BigDecimal total) { super(orderId); ... }
  }
  
  // PUBLISHER (injected ApplicationEventPublisher):
  @Service
  class OrderService {
      @Autowired ApplicationEventPublisher eventBus;
      
      @Transactional
      void placeOrder(Order order) {
          orderRepo.save(order);
          eventBus.publishEvent(new OrderPlacedEvent(order.getId(), order.getTotal()));
          // No coupling to any listener
      }
  }
  
  // SUBSCRIBERS:
  @Component
  class EmailHandler {
      @EventListener
      void handle(OrderPlacedEvent e) { emailService.sendConfirmation(e.orderId()); }
  }
  
  @Component
  class InventoryHandler {
      @EventListener
      @Async  // handle on separate thread pool
      void handle(OrderPlacedEvent e) { inventoryService.reserve(e.orderId()); }
  }
  
  // Conditional handling:
  @Component
  class LargeOrderHandler {
      @EventListener(condition = "#event.total > 1000")  // SpEL condition
      void handle(OrderPlacedEvent e) { vipTeam.notify(e.orderId()); }
  }
  
TRANSACTIONAL EVENT HANDLING:

  // Problem: event published inside transaction; handler runs before commit;
  // handler reads DB → sees uncommitted order → data not there yet!
  
  @Transactional
  void placeOrder(Order order) {
      orderRepo.save(order);
      eventBus.publishEvent(new OrderPlacedEvent(order.getId()));
      // Event published HERE — inside transaction — order not yet committed!
      // If EmailHandler queries orderRepo → might not find the order
  }
  
  // FIX: @TransactionalEventListener — handler runs AFTER transaction commits:
  @Component
  class EmailHandler {
      @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
      void handle(OrderPlacedEvent e) {
          // Runs AFTER outer transaction commits → order IS in DB
          emailService.sendConfirmation(e.orderId());
      }
  }
  
DISTRIBUTED EVENT BUS (KAFKA):

  // In-process EventBus: events shared within one JVM
  // Distributed EventBus: events shared across services/JVMs (Kafka, RabbitMQ)
  
  // Kafka as distributed Event Bus:
  // Publisher = Kafka Producer
  // Bus = Kafka broker + topics (event types)
  // Subscribers = Kafka Consumer Groups
  
  // Key difference from in-process EventBus:
  // ✓ Persistence: events stored, can replay
  // ✓ Multiple services (cross-JVM)
  // ✓ Scale: millions of events/sec
  // ✗ At-least-once delivery: handlers must be idempotent
  // ✗ Eventual consistency: handler sees event asynchronously
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Event Bus:
- `OrderService` directly calls `EmailService`, `InventoryService`, `AnalyticsService` — tightly coupled
- Adding new reaction to order: modify OrderService

WITH Event Bus:
→ `OrderService` publishes to bus. Zero coupling. New service subscribes to bus — OrderService unchanged.

---

### 🧠 Mental Model / Analogy

> A corporate announcement board (bus). Managers (publishers) post notices on the board. Departments (subscribers) read notices relevant to them. HR posts "New employee" notice → Payroll, IT, Facilities all read it. Manager doesn't call each department individually. Departments don't need to know who posted. New department: subscribe to the board. Event Bus: the announcement board routes notices to all interested departments.

"Announcement board" = Event Bus (central broker/mediator)
"Manager posts notice" = publisher.publishEvent(event)
"Departments read relevant notices" = @EventListener handler methods
"New department subscribes" = register new @EventListener — zero change to publisher
"HR doesn't know who reads" = publishers fully decoupled from subscribers

---

### ⚙️ How It Works (Mechanism)

```
EVENT BUS DISPATCH:

  publish(event):
  1. Look up handlers registered for event.getClass()
  2. Also check superclasses/interfaces (type hierarchy routing)
  3. Dispatch to each handler:
     - Synchronous: call handler in publisher's thread, in registration order
     - Asynchronous: submit handler invocations to thread pool
  
  subscribe(type, handler):
  Add handler to Map<EventType, List<Handler>>
  
  unsubscribe:
  Remove handler from map
  
  Dead events (no handler registered):
  Guava: posts DeadEvent; Spring: silently ignored
```

---

### 🔄 How It Connects (Mini-Map)

```
Central broker routes events from publishers to all registered subscribers
        │
        ▼
Event Bus Pattern ◄──── (you are here)
(bus = broker; publishers post; subscribers register; zero coupling between them)
        │
        ├── Observer Pattern: Observer without centralized broker (subject holds observer refs)
        ├── Mediator Pattern: Mediator coordinates behavior (Event Bus just routes — no logic)
        ├── Producer-Consumer: async Event Bus uses P-C internally (event queue + handler threads)
        └── Kafka/RabbitMQ: distributed, persistent, scalable Event Bus at system level
```

---

### 💻 Code Example

```java
// Custom typed event bus with async dispatch:
@Component
public class DomainEventBus {
    @Autowired ApplicationEventPublisher delegate;

    public void publish(DomainEvent event) {
        delegate.publishEvent(event);
    }
}

// Domain events:
sealed interface DomainEvent permits OrderPlaced, OrderShipped, OrderCancelled {}
record OrderPlaced(String orderId, BigDecimal total, Instant at) implements DomainEvent {}
record OrderShipped(String orderId, String trackingId, Instant at) implements DomainEvent {}

// Publisher:
@Service
class OrderService {
    @Autowired DomainEventBus eventBus;

    @Transactional
    public Order placeOrder(PlaceOrderCommand cmd) {
        Order order = orderRepository.save(Order.from(cmd));
        eventBus.publish(new OrderPlaced(order.getId(), order.getTotal(), Instant.now()));
        return order;
    }
}

// Subscribers — completely independent, zero coupling to OrderService:
@Component @Slf4j
class EmailSubscriber {
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    void on(OrderPlaced e) { emailService.sendOrderConfirmation(e.orderId()); }
}

@Component
class InventorySubscriber {
    @EventListener @Async
    void on(OrderPlaced e) { inventoryService.reserve(e.orderId()); }
    
    @EventListener @Async
    void on(OrderCancelled e) { inventoryService.release(e.orderId()); }
}

@Component
class MetricsSubscriber {
    @EventListener
    void on(OrderPlaced e) { meterRegistry.counter("orders.placed").increment(); }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Event Bus and Observer are the same | Observer: subject holds direct references to observers. Adding an observer requires the subject to expose a registration method. Subjects and observers are aware of each other. Event Bus: third-party broker. Publishers and subscribers know only the bus (and event types). Publisher has zero reference to subscribers. Event Bus scales to many publishers and subscribers; Observer is one-to-many per subject. |
| Synchronous Event Bus is safer | Depends on semantics. Synchronous: handler exception propagates to publisher (potentially aborting the publishing transaction). Async: handler exception doesn't affect publisher (but must be handled separately). `@TransactionalEventListener` is synchronous but deferred — handler runs after commit. Each model has different failure semantics. Choose based on required coupling between publishing and handling outcome. |
| Event Bus eliminates all coupling | Event Bus eliminates structural coupling (imports, method calls) but introduces behavioral coupling (shared event types). Publisher and subscribers must agree on: event schema (what fields, what types), event semantics (what does OrderPlaced mean), and ordering guarantees. Changing an event type's schema requires coordinating all subscribers. Schema registry (Avro, Protobuf) helps for distributed buses. |

---

### 🔥 Pitfalls in Production

**Event handlers not idempotent — duplicate events cause data corruption:**

```java
// ANTI-PATTERN: non-idempotent handler fails on duplicate event delivery:
@Component
class InventoryHandler {
    @KafkaListener(topics = "orders.placed")
    void onOrderPlaced(OrderPlacedEvent event) {
        // Network glitch: event delivered twice (Kafka at-least-once delivery)
        inventoryService.decrementStock(event.getProductId(), event.getQuantity());
        // Called twice → stock decremented twice → inventory goes negative!
    }
}

// FIX: idempotent handler — check if already processed:
@Component
class InventoryHandler {
    @Autowired ProcessedEventRepository processedEvents;
    
    @KafkaListener(topics = "orders.placed")
    @Transactional
    void onOrderPlaced(OrderPlacedEvent event) {
        // Check if already processed:
        if (processedEvents.existsByEventId(event.getEventId())) {
            log.warn("Duplicate event {}, skipping", event.getEventId());
            return;  // idempotent: ignore duplicate
        }
        
        inventoryService.decrementStock(event.getProductId(), event.getQuantity());
        processedEvents.save(new ProcessedEvent(event.getEventId(), Instant.now()));
    }
}
// Idempotency key (event ID) prevents duplicate processing.
// Also: use database unique constraint on event_id for additional safety.
```

---

### 🔗 Related Keywords

- `Observer Pattern` — direct publisher→subscriber; Event Bus adds third-party broker layer
- `Mediator Pattern` — mediator coordinates components; Event Bus purely routes (no coordination logic)
- `Domain Events` — events representing meaningful things that happened; published to Event Bus
- `Spring ApplicationEvent` — Spring's built-in Event Bus (`@EventListener`, `@TransactionalEventListener`)
- `Kafka` — distributed, persistent, scalable Event Bus at system level

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Central broker routes events: publishers │
│              │ post; subscribers register by type.      │
│              │ Neither knows the other. Pure decoupling.│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple services react to same event;   │
│              │ publisher must not know subscribers;     │
│              │ extensible event handling; domain events │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Need synchronous request-response;       │
│              │ event ordering is critical and hard to   │
│              │ guarantee; debugging async flows is hard │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Announcement board: manager posts once; │
│              │  all interested departments read it —    │
│              │  manager doesn't know who reads it."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Domain Events → Spring @EventListener →  │
│              │ Kafka → Observer Pattern → Outbox Pattern│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring's `@TransactionalEventListener` with `phase = AFTER_COMMIT` solves the "handler sees uncommitted data" problem. But it introduces a subtle failure scenario: what happens if the application crashes AFTER the transaction commits but BEFORE the event handler runs? The order IS saved to DB, but the email was never sent. This is the "dual-write problem" — you've committed to one system (DB) and need to commit to another (email/event). How does the Transactional Outbox pattern solve this? What is the Outbox pattern and how does it guarantee exactly-once event delivery even in the face of crashes?

**Q2.** In Guava's `EventBus`, events are dispatched based on the event object's type, including its type hierarchy. If `OrderPlacedEvent extends OrderEvent extends DomainEvent`, a subscriber registered for `DomainEvent` will receive ALL domain events, including `OrderPlacedEvent`. This is type-hierarchy routing. Is this a feature or a footgun? Give a scenario where type-hierarchy routing is extremely useful (catching all events of a category). Give a scenario where it causes a bug (unintentionally catching too many events).
