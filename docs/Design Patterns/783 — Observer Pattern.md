---
layout: default
title: "Observer Pattern"
parent: "Design Patterns"
nav_order: 783
permalink: /design-patterns/observer-pattern/
number: "783"
category: Design Patterns
difficulty: ★★☆
depends_on: "Object-Oriented Programming, Event-Driven Pattern, Publish-Subscribe"
used_by: "Event systems, GUI listeners, Spring events, ReactiveX, MVC pattern"
tags: #intermediate, #design-patterns, #behavioral, #oop, #event-driven, #pub-sub
---

# 783 — Observer Pattern

`#intermediate` `#design-patterns` `#behavioral` `#oop` `#event-driven` `#pub-sub`

⚡ TL;DR — **Observer** defines a one-to-many dependency so that when a subject changes state, all registered observers are notified automatically — decoupling publishers from subscribers so that the subject doesn't know who is listening or what they do with the notification.

| #783 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming, Event-Driven Pattern, Publish-Subscribe | |
| **Used by:** | Event systems, GUI listeners, Spring events, ReactiveX, MVC pattern | |

---

### 📘 Textbook Definition

**Observer** (GoF, 1994): a behavioral design pattern that defines a one-to-many dependency between objects so that when one object changes state, all its dependents are notified and updated automatically. Also known as Publish-Subscribe (though Pub/Sub typically involves a broker; Observer is direct). Components: **Subject** (publisher/observable) — maintains list of observers, notifies on state change. **Observer** (subscriber) — interface with `update()` method, receives state change notifications. GoF intent: "Define a one-to-many dependency between objects so that when one object changes state, all its dependents are notified and updated automatically." Java: `java.util.Observable` (deprecated in Java 9), `PropertyChangeListener`, Spring `ApplicationEvent`, ReactiveX `Observable`, Java 9 `Flow` (Reactive Streams).

---

### 🟢 Simple Definition (Easy)

A newspaper subscription. The newspaper (subject) publishes new editions. All subscribers (observers) get notified whenever a new edition is published. The newspaper doesn't know each subscriber personally — it just iterates through the subscriber list and delivers. Adding or removing a subscriber doesn't change how the newspaper works. Subscribers are notified automatically — they don't have to keep checking "is there a new edition?"

---

### 🔵 Simple Definition (Elaborated)

Spring `@EventListener`: `applicationEventPublisher.publishEvent(new OrderPlacedEvent(order))`. Multiple listeners: `EmailListener` sends confirmation email, `InventoryListener` reserves stock, `AnalyticsListener` logs the event. All registered with Spring's event system. OrderService doesn't know about any of them. Adding a new listener (`SmsListener`): zero changes to OrderService. Observer enables loose coupling between event producers and event consumers.

---

### 🔩 First Principles Explanation

**Push vs pull notification and thread-safety concerns:**

```
OBSERVER STRUCTURE:

  interface Observer {
      void update(Subject subject, Object data);  // notified when subject changes
  }
  
  interface Subject {
      void addObserver(Observer o);
      void removeObserver(Observer o);
      void notifyObservers();
  }
  
  class StockPrice implements Subject {
      private double price;
      private final List<Observer> observers = new CopyOnWriteArrayList<>();
      // CopyOnWriteArrayList: thread-safe; allows observers to deregister during notification
      
      void setPrice(double newPrice) {
          this.price = newPrice;
          notifyObservers();                  // automatically notify on change
      }
      
      void addObserver(Observer o)    { observers.add(o); }
      void removeObserver(Observer o) { observers.remove(o); }
      
      void notifyObservers() {
          for (Observer o : observers) {
              o.update(this, price);          // push: send new price directly
          }
      }
  }
  
  class PriceAlert implements Observer {
      private final double threshold;
      
      PriceAlert(double threshold) { this.threshold = threshold; }
      
      @Override
      public void update(Subject subject, Object data) {
          double currentPrice = (double) data;
          if (currentPrice > threshold) {
              sendAlert("Price exceeded " + threshold + "! Current: " + currentPrice);
          }
      }
  }
  
  // Usage:
  StockPrice apple = new StockPrice("AAPL", 150.0);
  apple.addObserver(new PriceAlert(160.0));
  apple.addObserver(new PriceAlert(170.0));
  apple.addObserver(new PortfolioTracker());
  
  apple.setPrice(165.0);  // notifies all 3 observers automatically
  
PUSH vs PULL MODELS:

  PUSH MODEL:
  Subject sends the changed data in the notification:
    observer.update(this, newPrice);  // data pushed to observer
  ✓ Observer gets data immediately without querying subject.
  ✗ Subject may push data observers don't need — wasted data.
  ✗ Less flexible: all observers get the same pushed data.
  
  PULL MODEL:
  Subject notifies that something changed; observer pulls what it needs:
    observer.update(this);  // only reference to subject; no data
    // Observer: double price = ((StockPrice) subject).getPrice();
  ✓ Observer queries only what it needs.
  ✓ More flexible: observers can query different aspects.
  ✗ Multiple query calls needed; subject must expose getter methods.
  
SPRING APPLICATION EVENTS:

  // Event (the "state change" payload):
  record OrderPlacedEvent(Order order) implements ApplicationEvent {
      OrderPlacedEvent(Order order) {
          super(order);
          this.order = order;
      }
  }
  
  // Subject (publisher):
  @Service
  class OrderService {
      @Autowired ApplicationEventPublisher eventPublisher;
      
      @Transactional
      void placeOrder(Order order) {
          orderRepository.save(order);
          eventPublisher.publishEvent(new OrderPlacedEvent(order));
          // OrderService doesn't know who listens — observers are decoupled
      }
  }
  
  // Observers (multiple, independent, zero coupling to each other):
  @Component
  class EmailNotificationListener {
      @EventListener
      void onOrderPlaced(OrderPlacedEvent event) {
          emailService.sendConfirmation(event.order());
      }
  }
  
  @Component
  class InventoryReservationListener {
      @EventListener
      void onOrderPlaced(OrderPlacedEvent event) {
          inventoryService.reserve(event.order());
      }
  }
  
  // ASYNC observers (non-blocking):
  @Component
  class AnalyticsListener {
      @EventListener
      @Async  // runs in separate thread — doesn't block order placement
      void onOrderPlaced(OrderPlacedEvent event) {
          analyticsService.track(event.order());
      }
  }
  
REACTIVE OBSERVER (Java 9 Flow / RxJava / Project Reactor):

  // Observable: stream of price updates (backpressure-aware):
  Flux<Double> priceStream = priceService.subscribe("AAPL");
  
  priceStream
      .filter(price -> price > 160.0)         // observer 1: alert on threshold
      .subscribe(price -> sendAlert(price));
      
  priceStream
      .scan(0.0, (sum, price) -> sum + price) // observer 2: running total
      .subscribe(total -> updatePortfolio(total));
  
  // Reactive: composable, lazy, backpressure-capable, async-native Observer.
  
COMMON PATTERNS WITH OBSERVER:

  MVC: Model = Subject. View = Observer.
  Model changes → notifies View. View calls getters to update display.
  
  Event Sourcing: events = state changes. Projections = observers.
  
  Database triggers: trigger = observer on table change.
  
OBSERVER MEMORY LEAK:

  // Classic bug: observers added to subject but never removed:
  class PriceWidget {
      PriceWidget(StockPrice stock) {
          stock.addObserver(this::updateDisplay);  // ← adds observer
      }
      // PriceWidget removed from UI but still referenced by stock!
      // stock holds strong reference to PriceWidget → GC can't collect it.
  }
  
  // Fix: deregister when widget is destroyed:
  class PriceWidget {
      private final StockPrice stock;
      private final Observer listener = this::updateDisplay;
      
      PriceWidget(StockPrice stock) {
          this.stock = stock;
          stock.addObserver(listener);
      }
      
      void destroy() {
          stock.removeObserver(listener);  // explicit deregistration
      }
  }
  // Or use WeakReference observers (if GC'd, auto-removed from observer list).
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Observer:
- Subject knows all dependents: `if (uiListener != null) uiListener.update()...` — tightly coupled
- Adding new listener: modify subject code (OCP violation)

WITH Observer:
→ Subject calls `notifyObservers()` — doesn't know who is listening. New listener: just register with subject. Zero changes to subject.

---

### 🧠 Mental Model / Analogy

> A weather station and weather apps. The weather station (subject) measures temperature, humidity, wind. Multiple apps (observers): a phone weather app, a smart thermostat, a ski resort app, a farming app. Each app registered with the station. When the station gets new data, it broadcasts to all registered apps. The station doesn't know what each app does with the data. New app (crop irrigation system): registers with station — station unchanged, irrigation app gets weather data.

"Weather station" = Subject (maintains observer list, broadcasts changes)
"Each app" = Observer (implements update())
"New measurement → broadcast" = notifyObservers()
"Apps register with station" = subject.addObserver()
"Station doesn't know what apps do" = decoupled; observers act independently

---

### ⚙️ How It Works (Mechanism)

```
OBSERVER FLOW:

  1. Observers register: subject.addObserver(observer)
  2. Subject state changes: subject.setState(newValue)
  3. Subject iterates observer list: for each o: o.update(this, data)
  4. Each observer reacts independently: handler logic in update()
  
  Adding observer: O(1). Removing: O(n) typically.
  Notification: O(n) — calls every registered observer.
```

---

### 🔄 How It Connects (Mini-Map)

```
One-to-many state change notification; decoupled publishers and subscribers
        │
        ▼
Observer Pattern ◄──── (you are here)
(subject maintains observer list; notifies all on state change)
        │
        ├── Mediator: centralized coordination (vs Observer: subject doesn't coordinate — just broadcasts)
        ├── Event-Driven Pattern: architectural Observer at system level
        ├── Reactive Streams: backpressure-aware, async Observer (Flux, Observable)
        └── MVC: Model = Subject, View = Observer — classic Observer application
```

---

### 💻 Code Example

```java
// Domain event Observer with Spring:
@DomainEvent  // marker annotation
record UserRegisteredEvent(String userId, String email, Instant registeredAt) {}

@Service
class UserService {
    @Autowired ApplicationEventPublisher events;
    
    @Transactional
    public User register(RegisterUserCommand cmd) {
        User user = User.create(cmd.email(), cmd.password());
        userRepository.save(user);
        events.publishEvent(new UserRegisteredEvent(user.getId(), user.getEmail(), Instant.now()));
        return user;   // doesn't know who observes UserRegisteredEvent
    }
}

// Independent observers — zero coupling to each other:
@Component @Slf4j
class WelcomeEmailObserver {
    @EventListener
    void on(UserRegisteredEvent e) {
        emailService.sendWelcome(e.email());
        log.info("Sent welcome email to {}", e.email());
    }
}

@Component
class UserMetricsObserver {
    @Autowired MeterRegistry metrics;
    
    @EventListener
    void on(UserRegisteredEvent e) {
        metrics.counter("users.registered").increment();
    }
}

@Component
class OnboardingWorkflowObserver {
    @EventListener
    @Async  // non-blocking — workflow can take minutes
    void on(UserRegisteredEvent e) {
        workflowEngine.startOnboarding(e.userId());
    }
}

// Adding a new observer (GDPR compliance check): add new class, zero changes elsewhere.
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Observer and Pub/Sub are the same | Similar but different. Observer: subject holds direct references to observers; notifications are synchronous by default; no broker between them. Pub/Sub: typically involves a broker (message queue, event bus); publishers and subscribers are completely decoupled (may be in different processes/services). Observer = in-process, direct. Pub/Sub = usually cross-process, broker-mediated. |
| Observer notifications are always synchronous | Default GoF Observer is synchronous — subject calls each observer in the notification loop. This means: slow observers block the subject; exceptions in one observer may prevent others from being notified. Spring's `@Async @EventListener` makes observers asynchronous. Reactive Streams (Flux) are inherently async. |
| Subject should expose its internals to observers | The PULL model requires observers to call getters on the subject. The subject should expose a well-designed interface — not all internals. Or use the PUSH model: pass only the changed data to the observer update method. In Spring ApplicationEvent, the event object carries exactly what observers need. |

---

### 🔥 Pitfalls in Production

**Observer triggering events in cascading loops:**

```java
// ANTI-PATTERN: Observer modifies subject → triggers another notification → infinite loop:
class PriceAdjuster implements Observer {
    @Override
    void update(Subject subject, Object data) {
        StockPrice stock = (StockPrice) subject;
        double currentPrice = (double) data;
        
        if (currentPrice > 200.0) {
            stock.setPrice(195.0);  // MODIFIES the subject → triggers notifyObservers() again!
            // PriceAdjuster.update() → stock.setPrice() → notifyObservers() → PriceAdjuster.update() → ∞
        }
    }
}
// StackOverflowError or infinite notification loop.

// FIX: Never modify the subject from within an observer's update() method.
// If state adjustment is needed, defer it:
void update(Subject subject, Object data) {
    double price = (double) data;
    if (price > 200.0) {
        // Schedule adjustment AFTER current notification cycle completes:
        Platform.runLater(() -> stock.setPrice(195.0));  // JavaFX
        // Or: use a flag to apply adjustment in a separate call
    }
}

// ALSO: Exception in one observer silently breaks notification for subsequent observers:
void notifyObservers() {
    for (Observer o : observers) {
        try {
            o.update(this, data);     // if this throws, loop stops — remaining observers miss notification!
        } catch (Exception e) {
            log.error("Observer {} threw exception", o, e);
            // Continue to next observer
        }
    }
}
```

---

### 🔗 Related Keywords

- `Mediator Pattern` — centralized coordination (vs Observer: subject broadcasts, observers react independently)
- `Event-Driven Pattern` — architectural-level Observer with async message passing
- `Reactive Streams` — backpressure-aware asynchronous Observer (Project Reactor, RxJava)
- `MVC Pattern` — Model is Subject, View is Observer; classic Observer application
- `Spring ApplicationEvent` — Spring's built-in Observer mechanism with @EventListener

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Subject notifies all registered observers │
│              │ when state changes. Subject doesn't know  │
│              │ observers; observers don't know each other│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ One-to-many state dependency; decouple   │
│              │ event producer from consumers; multiple  │
│              │ reactions to same event                  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Unexpected update order causes bugs;      │
│              │ cascading updates possible; need to know │
│              │ exactly which observers handle what      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Newspaper subscription: new edition →   │
│              │  all subscribers notified automatically; │
│              │  paper doesn't know what they do with it."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Mediator Pattern → Event-Driven Pattern → │
│              │ Reactive Streams → Spring ApplicationEvent│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Java 9 introduced `java.util.concurrent.Flow` — the standard Reactive Streams API (`Publisher`, `Subscriber`, `Subscription`, `Processor`). This is fundamentally Observer pattern with backpressure: a `Subscriber` can request a specific number of items (`subscription.request(n)`) to prevent being overwhelmed. How does `Flow.Subscriber` compare to the classic GoF `Observer` interface? What problem does `subscription.request(n)` solve that the classic Observer pattern doesn't address?

**Q2.** In a heavily concurrent system, multiple threads may call `subject.notifyObservers()` simultaneously, and observers may call `subject.removeObserver()` during notification (common in garbage-collected systems). Java's `CopyOnWriteArrayList` is often recommended for the observer list. Why does `CopyOnWriteArrayList` solve the concurrent modification problem during iteration? What is the performance tradeoff of `CopyOnWriteArrayList` vs `ArrayList` for read-heavy vs. write-heavy observer registration patterns?
