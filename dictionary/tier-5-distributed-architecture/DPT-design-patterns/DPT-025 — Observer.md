---
layout: default
title: "Observer"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 25
permalink: /design-patterns/observer/
id: DPT-025
category: Design Patterns
difficulty: ★★☆
depends_on: Object-Oriented Programming (OOP), Interface, Events, Coupling
used_by: Event-Driven Architecture, GUI Frameworks, MVC Pattern, Reactive Programming
related: Mediator, Event Bus Pattern, Publisher-Subscriber, Command, Strategy
tags:
  - pattern
  - intermediate
  - architecture
  - java
  - bestpractice
---

# DPT-025 — Observer

⚡ TL;DR — Observer lets multiple objects react to state changes in another object without tightly coupling them together.

| #785 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming (OOP), Interface, Events, Coupling | |
| **Used by:** | Event-Driven Architecture, GUI Frameworks, MVC Pattern, Reactive Programming | |
| **Related:** | Mediator, Event Bus Pattern, Publisher-Subscriber, Command, Strategy | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A stock-market dashboard displays prices in a table, a chart, and a mobile alert widget. When a price changes, the `StockPriceService` must explicitly call `priceTable.update()`, `chart.repaint()`, and `alertWidget.notify()`. Every new consumer of price changes requires modifying the core service. After six months, the service has twenty direct calls to unrelated components — it knows about tables, charts, alerts, audit logs, and analytics engines. Every UI or reporting decision bleeds into business logic.

**THE BREAKING POINT:**
The coupling is two-way disaster: the service cannot be tested without all consumers, consumers cannot be added without modifying the service, and removing a display component requires a service change. A team adding a new mobile notification widget must touch production business logic — violating the Open/Closed Principle in the most expensive way possible.

**THE INVENTION MOMENT:**
This is exactly why the Observer pattern was created. The service knows nothing about its consumers — it just fires a notification. Any object can subscribe or unsubscribe at runtime without touching the service.

---

### 📘 Textbook Definition

The **Observer** pattern is a behavioural design pattern that defines a one-to-many dependency between objects: when the **Subject** (Observable) changes state, all registered **Observers** are notified and updated automatically. The subject maintains a list of observers and provides `attach(observer)` and `detach(observer)` methods. Observers implement a common interface (`update(event)`) so the subject can notify them uniformly without knowing their concrete types.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
One object signals "something changed" and many objects react — without any of them knowing each other.

**One analogy:**
> A newspaper subscription works like this. The newspaper (Subject) prints a new edition. All subscribers (Observers) receive it automatically. Subscribers can join or cancel at will. The newspaper never calls subscribers by name — it just delivers to whoever has subscribed.

**One insight:**
Observer's real power is the decoupling of timing. The subject publishes when IT is ready; observers react when THEY are notified. Neither controls the other's lifecycle. This makes the system extensible by addition, not modification.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The subject must not know the concrete type of its observers — only their interface.
2. Observers must be independently addable and removable at runtime.
3. Notification must be automatic — observers do not poll the subject.

**DERIVED DESIGN:**
Given invariant 1: observers share a common `Observer` interface with an `update()` method. The subject holds `List<Observer>` — not `List<PriceTable>` or `List<Chart>`. Given invariant 2: `attach()` and `detach()` manage the list dynamically. Given invariant 3: when the subject state changes, it calls `notifyObservers()` which iterates the list and calls `update()` on each.

The subject decides WHEN to notify (after every change, or batched). The observer decides WHAT to do on notification. This separation of concerns is the pattern's core value.

**THE TRADE-OFFS:**
**Gain:** Zero coupling between subject and concrete observers; new observers added without modifying subject; observers can be added/removed at runtime.
**Cost:** Notification order is undefined (subjects notify observers in list order, which is implementation-dependent); cascade updates possible (observer A's `update()` triggers subject B which notifies observer C — hard to trace); weak reference issues in Java if observers are garbage collected while subscribed.

---

### 🧪 Thought Experiment

**SETUP:**
A temperature sensor broadcasts readings. Three displays — Celsius, Fahrenheit, and a heatwave alarm — must all react to changes.

**WHAT HAPPENS WITHOUT OBSERVER:**
`TemperatureSensor.setTemperature(celsius)` explicitly calls `celsiusDisplay.update(celsius)`, `fahrenheitDisplay.update(celsius * 9/5 + 32)`, and `if (celsius > 40) heatAlarm.trigger()`. Adding a humidity-corrected feels-like display requires editing `TemperatureSensor` — a class that should only know about temperatures.

**WHAT HAPPENS WITH OBSERVER:**
`TemperatureSensor` calls `notifyObservers(newTemp)`. `CelsiusDisplay`, `FahrenheitDisplay`, and `HeatAlarm` are all registered as observers. Each implements `update(temp)` independently. Adding a `FeelsLikeDisplay` requires zero changes to `TemperatureSensor` — just create the display and call `sensor.attach(feelsLikeDisplay)`.

**THE INSIGHT:**
Observer moves the "who cares about changes" responsibility OUT of the thing that changes. The subject is closed for modification but open for extension.

---

### 🧠 Mental Model / Analogy

> Observer is like a YouTube channel subscription. The channel (Subject) posts new videos. Subscribers (Observers) get notified automatically. The channel never knows who its subscribers are individually — it just posts. Subscribers join and leave freely. New notification formats (email, push, SMS) need no change to the channel itself.

- "YouTube channel" → Subject / Observable
- "Subscribing to the channel" → `subject.attach(observer)`
- "Channel posts a video" → subject state change triggers `notifyObservers()`
- "Subscriber receives a notification" → `observer.update(event)`
- "Unsubscribing" → `subject.detach(observer)`

Where this analogy breaks down: YouTube uses asynchronous push notifications over an external infrastructure. Classic Observer is synchronous — `notifyObservers()` is a synchronous loop. For async observer behaviour, the Event Bus pattern is more appropriate.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Observer is a subscription system built into your objects. One object says "I've changed" and every other object that signed up to listen gets notified. The object that changed does not know who is listening.

**Level 2 — How to use it (junior developer):**
Create an `Observer` interface with `update(event)`. Create a `Subject` class with `attach(Observer)`, `detach(Observer)`, and `notifyObservers()`. When the subject's state changes, call `notifyObservers()` which loops through registered observers and calls `update()` on each. In Java, `java.util.Observable` existed (now deprecated) and `PropertyChangeListener` is a built-in observer mechanism used in JavaBeans.

**Level 3 — How it works (mid-level engineer):**
The core implementation challenge is concurrent modification: if an observer calls `subject.detach(this)` inside its own `update()` method, the iterator will throw `ConcurrentModificationException`. Fix: iterate a copy of the list during notification, or use `CopyOnWriteArrayList`. Java's `Flow` API (Java 9+) formalises the Observer pattern with backpressure: `Publisher`, `Subscriber`, `Subscription` — the subscriber controls how many items it receives via `request(n)`, preventing fast publishers from overwhelming slow observers.

**Level 4 — Why it was designed this way (senior/staff):**
The classic GoF Observer (1994) was designed for single-threaded GUI frameworks where all updates occurred on the event thread. The design assumed synchronous notification — observers complete before the next observer is notified. Modern reactive systems (RxJava, Project Reactor) evolve Observer into event streams with operators (map, filter, flatMap), backpressure, error channels, and completion signals. The `Observable` in RxJava is NOT the GoF Observer — it's a full pipeline abstraction. The GoF Observer's main weakness is that it cannot express "the sequence of events is done" or "an error occurred in publishing" — Reactive Streams solved this by adding `onComplete()` and `onError()` to the subscriber interface.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────┐
│  OBSERVER PATTERN — MECHANISM                │
│                                              │
│  Subject (Observable)                        │
│  ┌──────────────────────────────────┐        │
│  │ observers: List<Observer>        │        │
│  │                                  │        │
│  │ attach(o)   → observers.add(o)   │        │
│  │ detach(o)   → observers.remove(o)│        │
│  │                                  │        │
│  │ setState(newVal):                 │        │
│  │   this.state = newVal            │        │
│  │   notifyObservers()              │        │
│  │                                  │        │
│  │ notifyObservers():               │        │
│  │   for each o in observers:       │        │
│  │     o.update(this)               │        │
│  └──────────────────────────────────┘        │
│           │ notifies                         │
│    ┌──────┼──────────┬──────────────┐        │
│    ↓      ↓          ↓              ↓        │
│  ObsA   ObsB       ObsC           ObsD       │
│  update update     update         update     │
└──────────────────────────────────────────────┘
```

**Push vs Pull notification:**

*Push model:* Subject passes its new state in `update(newState)`. Observers get the data directly. Simpler for observers; but subject must decide what data to push.

*Pull model:* Subject passes itself in `update(Subject source)`. Observers call `source.getState()` to pull what they need. More flexible — observers select only the data they care about. Avoids passing unnecessary data to every observer.

**Notification sequence:**
1. Caller modifies subject state: `subject.setPrice(150.0)`
2. Subject stores new state internally
3. Subject calls `notifyObservers()`
4. Subject iterates registered observer list
5. For each observer: `observer.update(this)` or `observer.update(newState)`
6. Each observer reacts independently to the notification

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Client calls subject.setState(newValue)
  → subject stores state
  → subject.notifyObservers()
                 ← YOU ARE HERE
  → for each observer in list:
       observer.update(subject or newValue)
  → ObserverA.update() → re-renders chart
  → ObserverB.update() → sends alert email
  → ObserverC.update() → logs to audit trail
  → all observers updated, call returns
```

**FAILURE PATH:**
```
ObserverB.update() throws RuntimeException
  → exception propagates up through notifyObservers()
  → ObserverC never gets notified (observers after B skipped)
Fix: wrap each observer call in try/catch so one
     failing observer doesn't stop others
```

**WHAT CHANGES AT SCALE:**
With 10,000 observers subscribed to a high-frequency trading signal (1,000 updates/second), synchronous notification becomes the bottleneck — 10 million `update()` calls per second on a single thread. The solution is async notification: observers are placed in a message queue and processed by separate threads, but this introduces out-of-order delivery risks.

---

### 💻 Code Example

**Example 1 — Classic Observer implementation:**
```java
// Observer interface
public interface PriceObserver {
    void onPriceChange(String symbol, double newPrice);
}

// Subject (Observable)
public class StockPriceService {
    private final List<PriceObserver> observers =
        new CopyOnWriteArrayList<>(); // thread-safe
    private final Map<String, Double> prices =
        new ConcurrentHashMap<>();

    public void attach(PriceObserver o) {
        observers.add(o);
    }

    public void detach(PriceObserver o) {
        observers.remove(o);
    }

    public void setPrice(String symbol, double price) {
        prices.put(symbol, price);
        notifyObservers(symbol, price); // notify all
    }

    private void notifyObservers(String symbol, double price) {
        for (PriceObserver o : observers) {
            try {
                o.onPriceChange(symbol, price);
            } catch (Exception e) {
                // don't let one broken observer stop others
                log.error("Observer failed: {}", e.getMessage());
            }
        }
    }
}

// Concrete observers
public class PriceDisplayWidget implements PriceObserver {
    @Override
    public void onPriceChange(String symbol, double price) {
        System.out.printf("%s: %.2f%n", symbol, price);
    }
}

public class PriceAlertService implements PriceObserver {
    private final double threshold;

    public PriceAlertService(double threshold) {
        this.threshold = threshold;
    }

    @Override
    public void onPriceChange(String symbol, double price) {
        if (price > threshold) {
            System.out.printf("ALERT: %s above %.2f!%n",
                symbol, threshold);
        }
    }
}

// Usage
StockPriceService service = new StockPriceService();
service.attach(new PriceDisplayWidget());
service.attach(new PriceAlertService(200.0));
service.setPrice("AAPL", 175.0); // displays: AAPL: 175.00
service.setPrice("AAPL", 210.0); // displays + alerts
```

**Example 2 — Java PropertyChangeListener (built-in Observer):**
```java
import java.beans.PropertyChangeSupport;
import java.beans.PropertyChangeListener;

public class UserProfile {
    private final PropertyChangeSupport pcs =
        new PropertyChangeSupport(this);
    private String email;

    public void addListener(PropertyChangeListener l) {
        pcs.addPropertyChangeListener(l);
    }

    public void setEmail(String newEmail) {
        String old = this.email;
        this.email = newEmail;
        pcs.firePropertyChange("email", old, newEmail);
    }
}

// Usage with lambda observer
UserProfile profile = new UserProfile();
profile.addListener(evt ->
    System.out.println("Email changed: "
        + evt.getOldValue() + " → " + evt.getNewValue()));
profile.setEmail("alice@example.com");
// Output: Email changed: null → alice@example.com
```

**Example 3 — Spring ApplicationEvent (framework-level Observer):**
```java
// Event
public record PriceChangedEvent(String symbol, double price) {}

// Publisher (Subject)
@Service
public class TradingService {
    private final ApplicationEventPublisher publisher;

    public TradingService(ApplicationEventPublisher p) {
        this.publisher = p;
    }

    public void updatePrice(String symbol, double price) {
        // business logic...
        publisher.publishEvent(
            new PriceChangedEvent(symbol, price));
    }
}

// Observer (registered automatically via @EventListener)
@Component
public class AuditLogger {
    @EventListener
    public void onPriceChange(PriceChangedEvent event) {
        log.info("Price updated: {} = {}",
            event.symbol(), event.price());
    }
}
// Zero coupling between TradingService and AuditLogger
```

---

### ⚖️ Comparison Table

| Mechanism | Coupling | Delivery | Order | Best For |
|---|---|---|---|---|
| **Observer (GoF)** | Low (interface) | Synchronous | Deterministic | In-process, simple events |
| Event Bus | Very low | Async optional | Non-deterministic | Loose cross-module events |
| Mediator | None (via hub) | Synchronous | Hub-controlled | Complex many-to-many comm |
| Pub-Sub (message broker) | None | Async | Non-deterministic | Distributed systems |
| Reactive Streams (RxJava) | Low | Push + backpressure | Stream order | High-throughput pipelines |

How to choose: use Observer (GoF) for in-process event notification where order matters and observers are few. Use Event Bus or Pub-Sub when crossing process boundaries or when observers are many and independently deployed.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Observer and Pub-Sub are the same | Observer involves direct subject-to-observer notification; Pub-Sub uses an intermediary broker. Observers know the subject; Pub-Sub subscribers do not know the publisher |
| Observer notifications are asynchronous by default | Classic Observer is synchronous — `update()` completes before the next observer is notified. Async requires explicit threading or event queues |
| Removing an observer during notification is safe | Without `CopyOnWriteArrayList` or iteration copy, removing during `notifyObservers()` causes `ConcurrentModificationException` |
| Observer guarantees notification order | Notification order is the list-insertion order, which is implementation-specific and subject to change |
| All reactive libraries are just the Observer pattern | Reactive Streams (RxJava, Reactor) add backpressure, completion, and error semantics that the GoF Observer pattern does not have |

---

### 🚨 Failure Modes & Diagnosis

**1. Memory Leak — Observers Not Detached**

**Symptom:** Heap grows over time. Objects expected to be garbage collected remain live. Memory profiler shows thousands of instances of observer classes still referencing stale subjects.

**Root Cause:** Observer is attached but `detach()` is never called when the observer is no longer needed. The subject holds a strong reference, preventing GC.

**Diagnostic:**
```bash
# Heap dump and look for observer instances
jmap -histo:live <PID> | grep -i observer
# If count grows over time: leak confirmed
```

**Fix:**
```java
// BAD: attach without lifecycle management
service.attach(displayWidget);
// displayWidget may be GC'd by caller but still
// referenced by service

// GOOD: store reference + detach on disposal
this.observer = new PriceDisplayWidget();
service.attach(observer);
// in cleanup/close:
service.detach(observer);

// ALTERNATIVE: Use WeakReference in subject's list
// Java's WeakReference allows GC without explicit detach
```

**Prevention:** Always detach observers in `close()`, `destroy()`, or lifecycle destroy methods. Prefer WeakReference-based observer lists for UI components.

---

**2. ConcurrentModificationException During Notification**

**Symptom:** `java.util.ConcurrentModificationException` thrown from `notifyObservers()`. Occurs when an observer modifies the subscription list during notification.

**Root Cause:** `ArrayList` iterator detects structural modification (add/remove) during iteration and throws.

**Diagnostic:**
```java
// Reproduce: observer that unsubscribes itself
service.attach(obs -> {
    service.detach(this); // modifies list during iteration!
    process(event);
});
```

**Fix:**
```java
// BAD: regular ArrayList — concurrent modification
private final List<Observer> observers = new ArrayList<>();

// GOOD: CopyOnWriteArrayList — iteration uses snapshot
private final List<Observer> observers =
    new CopyOnWriteArrayList<>();
// Or: iterate a copy
new ArrayList<>(observers).forEach(o -> o.update(state));
```

**Prevention:** Always use `CopyOnWriteArrayList` for subject observer lists in any multi-threaded or self-modifying context.

---

**3. Cascading Update Loops**

**Symptom:** `StackOverflowError` or application hangs. `notifyObservers()` seems to run indefinitely.

**Root Cause:** Observer A's `update()` changes Subject B, which notifies Observer C, which changes Subject A — creating a notification cycle.

**Diagnostic:**
```bash
# Thread dump to see the call stack
jstack <PID> | grep -A 30 "notifyObservers"
# Look for alternating subject/observer calls in the stack
```

**Fix:**
```java
// Add a guard flag in the subject:
private boolean notifying = false;

public void setState(T newState) {
    this.state = newState;
    if (!notifying) {
        notifying = true;
        try { notifyObservers(); }
        finally { notifying = false; }
    }
}
```

**Prevention:** Design observer graphs as DAGs (no cycles). If subjects can observe each other, use a changed-flag pattern or event deduplication.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Interface` — observers share a common interface; the subject holds a list of the interface type, not concrete classes
- `Coupling` — Observer exists to reduce coupling; understanding tight coupling vs loose coupling drives its justification
- `Object-Oriented Programming (OOP)` — polymorphism is the mechanism that allows diverse observer types to be notified uniformly

**Builds On This (learn these next):**
- `Event Bus Pattern` — generalises Observer by routing events through a central bus instead of direct subject-to-observer notification
- `Reactive Programming` — extends Observer with streams, backpressure, operators, and completion/error semantics (RxJava, Project Reactor)
- `Event-Driven Architecture` — architectural application of Observer at the system level using message brokers

**Alternatives / Comparisons:**
- `Mediator` — also decouples objects, but via a central hub that explicitly routes messages between them; Observer subjects manage their own lists
- `Command` — encapsulates an action as an object; can be combined with Observer to queue actions triggered by notifications
- `Publisher-Subscriber` — similar intent but uses a broker intermediary; subscribers do not reference the publisher

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ One-to-many subscription: subject         │
│              │ notifies all registered observers         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Subject must not know its consumers;      │
│ SOLVES       │ consumers must react to state changes     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Observer inverts the notification:        │
│              │ the subject never calls observers by name │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple components must react to one     │
│              │ source of state changes independently     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Notification must be async (use Event     │
│              │ Bus); observers are very many (use Pub-Sub)│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Decoupling gain vs cascade/leak risk      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Don't call us — we'll notify you."       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Event Bus → Reactive Programming →        │
│              │ Event-Driven Architecture                 │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A financial trading platform uses Observer: a `MarketDataService` notifies 500 `TradingAlgorithm` observers on every tick (500 ticks/second). Each algorithm's `update()` takes ~10 ms to process. Calculate the total notification time per tick. Trace what the next tick does while the first tick's notifications are still processing, and describe exactly what breaks. What architectural change resolves this without switching to a broker?

**Q2.** A user session manager (Subject) fires `SessionExpiredEvent`. An `AuditLogger` observer logs the event. An `AuthTokenRevocationService` observer invalidates JWT tokens — and in doing so calls `sessionManager.invalidate(sessionId)`, which changes the session manager's state and fires another event. Trace the exact cascade that results, identify the failure mode category, and describe two different design-level fixes that prevent the cycle without adding a `notifying` flag to the session manager.

