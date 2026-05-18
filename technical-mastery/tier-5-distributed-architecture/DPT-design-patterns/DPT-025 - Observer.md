---
id: DPT-025
title: Observer
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-005, DPT-023
used_by: DPT-037, DPT-064, DPT-065
related: DPT-023, DPT-027, DPT-037, DPT-032
tags:
  - pattern
  - behavioral
  - intermediate
  - event-driven
  - reactive
  - publish-subscribe
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 25
permalink: /technical-mastery/design-patterns/observer/
---

⚡ TL;DR - Observer defines a one-to-many dependency so
that when one object (Subject) changes state, all its
dependents (Observers) are notified and updated automatically
- the foundation of event-driven and reactive programming.

| #25 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-023 | |
| **Used by:** | DPT-037, DPT-064, DPT-065 | |
| **Related:** | DPT-023, DPT-027, DPT-037, DPT-032 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A stock price data source is used by a display widget,
an alert system, and a trading algorithm. Without Observer:
each consumer polls the data source every second. Three
polling loops, high CPU usage, updates may lag up to 1
second, and adding a fourth consumer requires modifying
the polling infrastructure.

**THE BREAKING POINT:**
With 100 consumers, 100 polling threads hit the data
source simultaneously. The data source is overloaded.
Adding consumers means adding more load. Removing a
consumer means finding and stopping its polling thread.

**THE INVENTION MOMENT:**
Observer: consumers register as "listeners" on the data
source. When the price changes, the data source calls
`listener.onPriceChanged(newPrice)` on all registered
listeners. No polling. Updates are instant. Adding a
new consumer: call `dataSource.subscribe(newConsumer)`.
Removing: call `dataSource.unsubscribe(consumer)`.

**EVOLUTION:**
Observer is the foundation of:
- Java's event model (`ActionListener`, `PropertyChangeListener`)
- Reactive programming (RxJava, Project Reactor - `Flux`/`Mono`)
- GUI frameworks (Swing, JavaFX, React's useState)
- Browser DOM events (`addEventListener`)
- Spring application events (`@EventListener`)
- Pub/Sub messaging (Kafka topics, Redis pub/sub)

---

### 📘 Textbook Definition

The **Observer** pattern is a Behavioral design pattern
that defines a one-to-many dependency between objects so
that when one object (Subject/Publisher) changes state,
all its dependents (Observers/Subscribers) are notified
and updated automatically. The pattern promotes loose
coupling: the Subject knows only that its observers
implement the Observer interface; it does not know their
concrete types or count.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Observer is the "subscribe and be notified" mechanism -
one subject, many listeners, automatic push on change.

**One analogy:**
> A YouTube channel (Subject). Subscribers (Observers)
> hit the notification bell. When a new video (state change)
> is posted, YouTube (Subject) notifies all subscribers.
> The channel has no idea who is subscribed or what they
> do with the notification. Subscribers can join (subscribe)
> or leave (unsubscribe) at any time.

**One insight:**
Observer inverts control: instead of consumers PULLING
data, the Subject PUSHES updates. This push model eliminates
polling, reduces latency, and decouples the Subject from
all consumer implementations.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Subject maintains a list of observers; it does not
   know their concrete types.
2. All observers implement the same interface (update method).
3. When Subject state changes: iterate observer list,
   call `update()` on each.
4. Observers can subscribe/unsubscribe dynamically.

**DERIVED DESIGN:**
Two key participants:
- **Subject (Observable)**: maintains observer list;
  `subscribe(observer)`, `unsubscribe(observer)`,
  `notifyObservers()`.
- **Observer**: the `update(event)` interface that all
  observers implement.

**PUSH vs PULL MODEL:**
- **Push**: Subject passes the changed data in `update(data)`.
  Observer receives everything the subject decides to send.
- **Pull**: Subject passes `update(subject)` - itself as
  reference. Observer calls `subject.getData()` to fetch
  what it needs. More flexible; observer decides what data
  to extract.

**TRADE-OFFS:**

**Gain:** Subject is decoupled from observers. Observers
can be added/removed dynamically. Update is instantaneous
(no polling). New observer types require no Subject changes.

**Cost:** Notification order is non-deterministic if
observers are stored in unordered collections. A slow
observer blocks all subsequent notifications in synchronous
notification. Memory leaks if observers forget to unsubscribe
(Subject holds reference, preventing GC). Cascading updates
(observer A notifies observer B which notifies observer A)
can cause infinite loops.

---

### 🧪 Thought Experiment

**SETUP:**
An order management system: when an Order is placed,
three things happen: (1) send confirmation email, (2)
deduct from inventory, (3) log to analytics. Without
Observer: `OrderService.placeOrder()` calls all three
services directly - coupled to all three.

**WITH OBSERVER:**
`OrderService` (Subject) publishes `OrderPlaced` event.
`EmailService` (Observer) subscribes, sends email.
`InventoryService` (Observer) subscribes, deducts stock.
`AnalyticsService` (Observer) subscribes, logs event.

Adding `FraudDetectionService`: subscribe to `OrderPlaced`.
Zero changes to `OrderService`. The Subject has no knowledge
of what happens when an order is placed.

---

### 🧠 Mental Model / Analogy

> Observer is a NEWSPAPER SUBSCRIPTION. The newspaper
> (Subject) is published whenever there is news (state change).
> Each subscriber (Observer) receives a copy. The newspaper
> company does not know what subscribers do with their
> copy - read it, throw it away, share it. Subscribers
> can sign up (subscribe) or cancel (unsubscribe) any time.
> The newspaper doesn't change; subscriptions change.

- "Newspaper" = Subject + event
- "Subscriber" = Observer
- "Subscribe/cancel" = register/unregister
- "Publishing" = notifyObservers()

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Observer is the notification system: sign up to be told
when something changes. When it does, you are automatically
informed without having to keep checking.

**Level 2 - How to use it (junior developer):**
Create an `Observer` interface with `update(event)`.
Subject holds a `List<Observer>`. `notifyObservers()` iterates
the list calling `update(event)` on each. Observers
call `subject.subscribe(this)` to register.

**Level 3 - How it works (mid-level engineer):**
Java's `java.util.Observable` and `Observer` (deprecated
in Java 9) are the original built-in implementation.
Modern Java uses `PropertyChangeSupport` for bean property
change notification (JavaBeans spec). `PropertyChangeListener
.propertyChange(PropertyChangeEvent e)` is the Observer
interface. Spring's `@EventListener` is Observer: spring
beans annotated with `@EventListener` auto-register for
application events. Project Reactor's `Flux.subscribe()`
is Observer pattern extended with backpressure.

**Level 4 - Why it was designed this way (senior/staff):**
Observer implements the "Dependency Inversion" at the
event level: high-level modules (OrderService) do not
depend on low-level details (EmailService). Instead,
both depend on the event abstraction (OrderPlacedEvent).
This is the Dependency Inversion Principle applied to
runtime coupling. Observable/Observer separates WHAT
changes (the domain object) from HOW changes are reacted
to (the observers). This separation is why the Observer
pattern is the conceptual foundation of all reactive
programming: `Flux` is an Observable, `subscribe()` registers
an Observer, backpressure is observer flow control.

**Level 5 - Mastery (distinguished engineer):**
RxJava/Project Reactor extends Observer with:
1. **Completion**: observer is notified when the observable
   is done emitting (no more events).
2. **Error propagation**: observer is notified of errors
   on the observable pipeline.
3. **Backpressure**: observer can signal to the observable
   "slow down" if it cannot keep up - preventing OutOfMemoryError
   from a fast publisher overwhelming a slow subscriber.
The reactive `Publisher<T>` (Reactor) implements Observer
with these three channels: `onNext(T)`, `onError(Throwable)`,
`onComplete()`. This is Observer with lifecycle management
added - a critical extension for production streaming systems.

---

### ⚙️ How It Works (Mechanism)

```
Observer Pattern Structure
┌─────────────────────────────────────────────────────────┐
│ <<interface>> Observer<T>                               │
│   + update(event: T): void                              │
│                                                         │
│ Subject<T> (Observable)                                 │
│   - observers: List<Observer<T>>                        │
│   - state: T                                            │
│   + subscribe(obs: Observer<T>): void                   │
│       observers.add(obs)                                │
│   + unsubscribe(obs: Observer<T>): void                 │
│       observers.remove(obs)                             │
│   + setState(newState: T): void                         │
│       this.state = newState                             │
│       notifyObservers(newState) ← trigger notification  │
│   + notifyObservers(event: T): void                     │
│       for (Observer obs : observers):                   │
│           obs.update(event)                             │
│                                                         │
│ ConcreteObserver implements Observer<T>                 │
│   + update(event: T): void                              │
│       // react to the event                             │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
StockPriceSubject has: [DisplayWidget, AlertSystem,
  TradingBot]

New price arrives: AAPL = $185.50
subject.setState(new Price("AAPL", 185.50)):
  notifyObservers(price):
    DisplayWidget.update(price): updates price label
    AlertSystem.update(price):
      if price > threshold: send SMS alert
    TradingBot.update(price):
      if price < buyLimit: execute buy order
```

**SLOW OBSERVER BLOCKING:**
```
notifyObservers() - SYNCHRONOUS (BAD):
  DisplayWidget.update() - 1ms
  AlertSystem.update() - sends SMS - 200ms BLOCKING
  TradingBot.update() - blocked for 200ms!
  // Price updates are delayed by the slowest observer

FIX: async notification
  executor.submit(() -> observer.update(event));
  // each observer runs in its own thread
```

---

### 💻 Code Example

**Example 1 - Core Observer implementation:**

```java
// BAD: polling model
class PriceDashboard {
    private StockService stockService;

    void start() {
        // Polling: CPU waste, latency, N thread problem
        ScheduledExecutorService sched =
            Executors.newScheduledThreadPool(1);
        sched.scheduleAtFixedRate(() -> {
            Price price = stockService.getPrice("AAPL");
            display.updatePrice(price);
        }, 0, 1, TimeUnit.SECONDS);
    }
}

// GOOD: Observer push model
interface PriceObserver {
    void onPriceChanged(Price newPrice);
}

class StockPriceSource {
    private final List<PriceObserver> observers
        = new CopyOnWriteArrayList<>(); // thread-safe

    public void subscribe(PriceObserver obs) {
        observers.add(obs);
    }

    public void unsubscribe(PriceObserver obs) {
        observers.remove(obs);
    }

    // Called when new price arrives (e.g., from feed)
    public void publishPrice(Price price) {
        observers.forEach(obs -> obs.onPriceChanged(price));
    }
}

// Observers: each does its own thing
class DisplayWidget implements PriceObserver {
    @Override
    public void onPriceChanged(Price price) {
        label.setText(price.symbol() + ": $" + price.value());
    }
}

class PriceAlertSystem implements PriceObserver {
    @Override
    public void onPriceChanged(Price price) {
        if (price.value() > threshold) {
            smsService.send("AAPL above threshold: " + price);
        }
    }
}

// Setup: no coupling between observers
StockPriceSource source = new StockPriceSource();
source.subscribe(new DisplayWidget());
source.subscribe(new PriceAlertSystem());
// Adding TradingBot: source.subscribe(new TradingBot())
// No changes to source or other observers
```

**Example 2 - Spring @EventListener (Observer built-in):**

```java
// RECOGNITION: Spring's event system IS Observer pattern

// Subject (publishes events):
@Service
class OrderService {
    @Autowired
    private ApplicationEventPublisher publisher;  // Subject

    public void placeOrder(Order order) {
        orderRepo.save(order);
        // Notify all observers
        publisher.publishEvent(new OrderPlacedEvent(order));
    }
}

// Observer 1: email notification
@Service
class EmailObserver {
    @EventListener  // registers as observer
    public void onOrderPlaced(OrderPlacedEvent event) {
        emailService.send(event.getOrder().customerEmail(),
            "Your order has been placed");
    }
}

// Observer 2: inventory update
@Service
class InventoryObserver {
    @Async          // async observer: doesn't block other observers
    @EventListener
    public void onOrderPlaced(OrderPlacedEvent event) {
        inventoryService.deduct(event.getOrder().items());
    }
}
// OrderService does NOT know EmailObserver or InventoryObserver exist
```

**Example 3 - Memory leak: observer not unsubscribed:**

```java
// BAD: observer holds reference; subject holds observer
class UserDashboard {
    private StockPriceSource source;

    void initialize() {
        // Creates anonymous observer - holds strong reference
        source.subscribe(price -> display.update(price));
        // LEAK: 'source' holds lambda until source is GC'd
        // If UserDashboard is recreated many times,
        // old dashboards never GC'd because source holds them
    }
    // No unsubscribe on destroy!
}

// GOOD: store reference for unsubscription
class UserDashboard {
    private StockPriceSource source;
    private PriceObserver observer;

    void initialize() {
        observer = price -> display.update(price);
        source.subscribe(observer);
    }

    void destroy() {
        source.unsubscribe(observer); // prevent leak
        observer = null;
    }
}
```

**How to test/verify correctness:**
Test that `subscribe()` adds the observer to the notification
list. Test that `notifyObservers()` calls `update()` on
ALL registered observers. Test that `unsubscribe()` stops
further notifications. Test thread safety: subscribe/unsubscribe
concurrent with notification.

---

### ⚖️ Comparison Table

| Pattern | All notified? | Ordering? | Observer knows subject? | Push/Pull |
|---|---|---|---|---|
| **Observer** | All registered | Non-deterministic | Optional (pull model) | Push |
| Mediator | Selective | Mediator decides | No (via mediator) | Hybrid |
| Chain of Resp. | One processes | Ordered chain | No | Pull (passes) |
| Event Bus | All subscribed | Non-deterministic | No | Push |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Observer and Event Bus are the same | Observer (GoF) is object-to-object within a JVM. Event Bus extends Observer to decouple via a message broker (Kafka, RabbitMQ); the broker enables cross-service, cross-JVM notifications. Event Bus is Observer at the infrastructure level |
| Observer guarantees delivery order | The GoF Observer notification order depends on the order observers were added. No ordering guarantee exists unless explicitly enforced. For ordered processing: use a list-based observer set with defined insertion order |
| Unsubscribing is optional | Not unsubscribing causes memory leaks: the Subject holds a strong reference to the Observer, preventing garbage collection. In GUI applications with many subscriber/lifecycle pairs, this is a major source of memory leaks |
| Observer and Reactive Streams are different paradigms | Reactive Streams (RxJava, Project Reactor) IS Observer with three additions: (1) completion notification (onComplete), (2) error notification (onError), (3) backpressure (slow down if overwhelmed). The conceptual model is identical |
| Observer means all observers get the same notification | Observers all receive the same event object - but what they DO with it is completely independent. Each observer processes the event in its own context |

---

### 🚨 Failure Modes & Diagnosis

**Observer Memory Leak - Forgotten Unsubscription**

**Symptom:**
Heap grows continuously. After 24 hours of operation with
many user sessions, `OutOfMemoryError`. Heap dump shows
thousands of observer instances that should have been
garbage collected with their parent objects.

**Root Cause:**
Short-lived objects (user dashboard, request-scoped
components) subscribe to a long-lived Subject (stock
price source, event bus). The Subject holds strong
references to all observers. Short-lived objects are
never garbage collected because the Subject still holds
them.

**Diagnostic Signal:**
Heap dump: many instances of `UserDashboard` or equivalent
that have been destroyed logically but not GC'd.
Reference chain: `StockPriceSource.observers →
  List → UserDashboard$lambda → UserDashboard`

**Fix:**
Always unsubscribe in destroy/close methods. Use
`WeakReference<Observer>` for optional weak observation
(Subject doesn't prevent GC). Use `CopyOnWriteArrayList`
and periodic cleanup of dead weak references.

---

**Slow Observer Blocking All Notifications**

**Symptom:**
When an order is placed, the confirmation email (SMS)
takes 500ms. During this time, the inventory update and
analytics log are blocked. Order processing throughput
is limited by the slowest observer.

**Root Cause:**
Synchronous `notifyObservers()` calls observers in sequence.
Each observer blocks the notification thread until it
completes.

**Fix:**
Make slow observers asynchronous:
```java
// FIX: async observer notification
public void publishPrice(Price price) {
    observers.forEach(obs ->
        asyncExecutor.submit(() -> obs.onPriceChanged(price)));
}
// Or: Spring @Async on @EventListener method
@Async
@EventListener
public void onOrderPlaced(OrderPlacedEvent e) { /* slow work */ }
```

**Prevention:**
Design invariant: observers should complete quickly (< 10ms).
Observers performing I/O or network calls MUST be async.
Document the expected observer execution time contract.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Mediator` - DPT-023; understand Mediator (active hub)
  first to clarify Observer's (passive relay) distinction

**Builds On This (learn these next):**
- `Event Bus Pattern` - DPT-037; Observer extended to
  cross-service, cross-JVM notification via message brokers

**Alternatives / Comparisons:**
- `Mediator` - active coordinator vs passive notifier
- `Event Bus` - Observer with infrastructure-level delivery

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ One-to-many push notification; Subject   │
│              │ notifies ALL observers on state change   │
├──────────────┼──────────────────────────────────────────┤
│ KEY INTERFACE│ Observer.update(event); Subject.subscribe│
│              │ / unsubscribe / notifyObservers          │
├──────────────┼──────────────────────────────────────────┤
│ REAL EXAMPLE │ Spring @EventListener, RxJava, Reactor   │
│              │ Flux, Java PropertyChangeListener        │
├──────────────┼──────────────────────────────────────────┤
│ LEAK RULE    │ ALWAYS unsubscribe in destroy(); Subject │
│              │ holds strong reference → prevents GC     │
├──────────────┼──────────────────────────────────────────┤
│ SLOW OBS.    │ Async observers prevent blocking; use    │
│              │ @Async or executor.submit() for slow ops │
├──────────────┼──────────────────────────────────────────┤
│ REACTIVE     │ Reactor Flux is Observer + completion +  │
│              │ error + backpressure channels            │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ State → Strategy → Template Method       │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Observer is push-notification: Subject calls `update()`
   on ALL registered observers when state changes -
   no polling, instant updates, unlimited observers
2. Always unsubscribe in `destroy()` - Subject holds
   strong reference to observer, preventing GC; this is
   a major source of memory leaks in Java applications
3. Spring's `@EventListener` is Observer built into the
   framework; `Flux.subscribe()` is Observer with completion,
   error, and backpressure added

**Interview one-liner:**
"Observer defines a one-to-many push dependency - Subject
notifies all registered Observers on state change. Spring
@EventListener and RxJava Flux are built on Observer. The
classic failure mode: forgetting to unsubscribe causes the
Subject to hold observer references, preventing GC and
causing memory leaks."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Whenever multiple independent components need to react
to the same state change, use Observer instead of direct
method calls. The Subject should be agnostic of its
observers: adding or removing a reaction to an event
should require ZERO changes to the event source.

**Where else this pattern appears:**
- **React's useState Hook** - when state is set via
  `setState()`, React re-renders all components that
  "subscribe" to that state (via hooks). `useState` is
  the Subject; components are Observers; re-render is
  the notification
- **Java NIO Selector** - `Selector.select()` blocks until
  one of the registered channels (Observers) has a I/O
  event ready. The NIO channel registrations are Observer
  subscriptions; `select()` triggers `update()` on ready
  channels
- **Database triggers** - a PostgreSQL TRIGGER fires when
  a table row is inserted/updated/deleted. The trigger
  function (Observer) runs for each change event. The table
  (Subject) does not know what the trigger does; the trigger
  registers interest in changes.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [IMPLEMENT] Build a stock price notification system
   with three observers (display, alert, trading bot) -
   including proper subscribe/unsubscribe and thread-safe
   CopyOnWriteArrayList for the observer list
2. [EXPLAIN] Why not unsubscribing an observer causes
   a memory leak - trace the reference chain from Subject
   to the undead observer object
3. [IDENTIFY] Explain how Spring's @EventListener maps
   to Observer: name the Subject, Observer interface,
   and notification mechanism
4. [COMPARE] Describe the three additions Reactor Flux
   adds to the basic Observer pattern and explain why
   each addition is necessary for production streaming

---

### 🎯 Interview Deep-Dive

**Q1: What is the Observer pattern? How does it relate
to reactive programming?**

*Why they ask:* Observer is foundational to event-driven
Java; tests whether the candidate understands the connection
to reactive programming.

*Strong answer includes:*
- Subject-Observer: one publishes, many subscribe; push model
- Spring ApplicationEventPublisher is built-in Observer
- Reactive Streams (RxJava, Reactor) extend Observer with:
  `onNext(T)` (update), `onComplete()` (done), `onError(Throwable)`
  (error), and backpressure (slow down when overwhelmed)
- `Flux.subscribe(consumer)` = `subject.subscribe(observer)`
- Backpressure is the critical reactive addition: prevents
  a fast publisher from overwhelming a slow subscriber
  (memory protection)

**Q2: What is the memory leak risk with Observer pattern
and how do you prevent it?**

*Why they ask:* Tests practical Java memory management
knowledge combined with the pattern.

*Strong answer includes:*
- Subject holds `List<Observer>` - strong references
- If Observer's parent object (UserDashboard) is destroyed
  without unsubscribing, Subject still holds the reference
- Observer cannot be GC'd; parent object cannot be GC'd;
  memory grows with each new subscriber that never unsubscribes
- Prevention: always call `unsubscribe()` in `destroy()/close()`
- Alternative: use `WeakReference<Observer>` in the Subject's
  list; GC removes the entry; Subject must clean up null weak refs
- In Android/Swing GUI: the most common memory leak source

**Q3: How would you make an Observer implementation
thread-safe for concurrent notification and subscription?**

*Why they ask:* Tests concurrent Java knowledge applied
to a real pattern scenario.

*Strong answer includes:*
- Problem: concurrent subscribe/unsubscribe + notifyObservers
  on `ArrayList` is not thread-safe (ConcurrentModificationException)
- Solution 1: `CopyOnWriteArrayList` - thread-safe reads,
  copy-on-write for modifications; no CME; good when
  reads (notifications) dominate over writes (subscribe/unsubscribe)
- Solution 2: Synchronized iteration with explicit lock:
  `synchronized(observers)` during iteration; notify
  with lock - but this can cause deadlock if an observer
  calls back into the Subject
- Solution 3: async notification via an executor - submit
  each `observer.update()` as an independent task; no
  lock needed on the notification loop; observers run
  concurrently
- Best practice: `CopyOnWriteArrayList` + async (executor)
  for high-throughput observer systems

