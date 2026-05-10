---
layout: default
title: "Mediator"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 23
permalink: /design-patterns/mediator/
id: DPT-023
category: Design Patterns
difficulty: ★★★
depends_on:
used_by:
related:
tags:
  - pattern
  - deep-dive
  - architecture
  - java
  - distributed
status: complete
version: 2
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
---

# DPT-023 - Mediator

⚡ TL;DR - Mediator centralises complex communication between many objects so they communicate through a shared mediator instead of directly with each other.

| DPT-023 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming (OOP), Interface, Coupling, Observer | |
| **Used by:** | Chat Systems, Air Traffic Control, UI Component Coordination, Event Bus | |
| **Related:** | Observer, Facade, Command, Event Bus Pattern | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A complex form has 10 UI components: a `CountryDropdown`, `StateDropdown`, `ZipCodeField`, `PhoneField`, `SubmitButton`, a `SaveDraftButton`, and several validation labels. When the country changes, the state dropdown must be repopulated with the correct states, the zip code field must change its validation regex, the phone field must update its country code, and the submit button must disable while the data reloads. Without a mediator, each component holds direct references to the other 9 components it must notify. Adding an 11th component requires updating many existing components to connect to it.

**THE BREAKING POINT:**
With 10 components each potentially connected to 9 others, the connections form a fully-connected graph: up to 45 direct bidirectional references. The codebase becomes a spaghetti of cross-references. Testing one component requires constructing all the others. A bug in how `CountryDropdown` updates `ZipCodeField` means touching both classes. Adding a new component means combing every existing component for connections to add.

**THE INVENTION MOMENT:**
This is exactly why the Mediator pattern was created. Each component knows only the Mediator. When `CountryDropdown` changes, it tells the Mediator: `mediator.notify(this, "countryChanged", "US")`. The Mediator contains all the coordination logic: update state dropdown, reset zip validation, update phone code, disable submit. Components are decoupled from each other - they only know the Mediator. Adding a new component: register it with the Mediator, add its coordination logic there. Zero changes to existing components.

**EVOLUTION:**
Mediator's classical form -- centralising interactions between
UI components -- declined as reactive and data-binding frameworks
(Angular, React) provided declarative state management. The
pattern's core concept migrated to: message brokers (Kafka,
RabbitMQ as infrastructure mediators), CQRS command buses
(Spring's `CommandGateway`), and event buses. Redux (React
state management) is a Mediator: the store mediates between
actions and reducers, ensuring all state changes go through
one central point. Spring's `ApplicationEventPublisher` is
a built-in Mediator for intra-application events.

---

### 📘 Textbook Definition

The **Mediator** pattern is a behavioural design pattern that defines an object (the Mediator) that encapsulates how a set of objects interact. Objects (Colleagues) communicate only through the Mediator, not directly with each other. The Mediator promotes loose coupling by preventing objects from referencing each other explicitly and allowing coordination logic to be varied and reused independently. The pattern converts a many-to-many communication mesh into a many-to-one-to-many hub-and-spoke structure.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A hub where all components send messages so nothing talks directly to anything else.

**One analogy:**
> An air traffic control (ATC) tower. Dozens of aircraft in the airspace all communicate through the tower - not directly with each other. The tower (mediator) knows where all aircraft are, resolves conflicts, and coordinates takeoff/landing sequences. Aircraft just report their status to the tower and receive instructions. Removing one aircraft doesn't affect how others communicate.

**One insight:**
The Mediator doesn't simplify the total complexity - it centralises it. The same coordination logic exists whether you use Mediator or not. Mediator moves that logic from being scattered across N components (each component knows parts of the coordination) to being concentrated in one place. This is the correct trade-off when coordination logic changes frequently.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Many objects need to coordinate their behaviour based on each other's state changes.
2. The coupling between objects grows as O(n²) with direct communication; this becomes unmanageable.
3. The coordination logic is a first-class concern that must be isolated, tested, and changed as a unit.

**DERIVED DESIGN:**
Given invariant 1+2: replace direct references with mediated communication. Each `Colleague` holds only a reference to the `Mediator`. Given invariant 3: all coordination logic lives in the Mediator - when A notifies mediator of event E, the Mediator decides which colleagues to notify and how.

The `Mediator` interface declares a communication endpoint, e.g., `notify(Colleague sender, String event)`. Each concrete `Mediator` implements the coordination logic for a specific set of colleagues. Colleagues call `mediator.notify(this, event)` to signal changes. The Mediator calls specific methods on specific colleagues in response.

**THE TRADE-OFFS:**
**Gain:** Decoupled colleagues (each knows only the Mediator); coordination logic in one testable place; adding new colleagues requires updating only the Mediator; colleagues are independently reusable; O(n+1) connections instead of O(n²).
**Cost:** Mediator can become a God Object concentrating all business logic; coordination logic in one place can become difficult to navigate; the Mediator may need to evolve frequently as coordination rules change; using events (Observer/Event Bus) instead of direct Mediator calls is often cleaner for distributed systems.

---

### 🧪 Thought Experiment

**SETUP:**
A chat room has 100 users. Each user can send messages that all other users receive. Without Mediator: each User would need references to all 99 others to send messages - 9,900 bidirectional user-to-user references. When User 50 sends a message, it calls `user1.receive()`, `user2.receive()`, ..., `user99.receive()` - knowing and calling all 99 others explicitly.

**WHAT HAPPENS WITHOUT MEDIATOR:**
Adding User 101: User 101 must be registered with all 100 existing users, AND all 100 users must get a reference to User 101. Adding one user touches 100 objects. A user leaving requires purging the reference from all 100 remaining users. The system is impractical beyond a handful of users.

**WHAT HAPPENS WITH MEDIATOR:**
`ChatRoom` (the Mediator) maintains the list of users. User 50 calls `chatRoom.broadcast(this, "Hello everyone!")`. `ChatRoom.broadcast()` iterates over all registered users and calls `user.receive()`. Adding User 101: `chatRoom.register(user101)` - one line, zero existing user changes. User 50 leaving: `chatRoom.deregister(user50)` - one operation.

**THE INSIGHT:**
The Mediator converts a distributed coordination problem into a centralised registration + notification problem. The total coordination work is the same; where the logic lives is the difference.

---

### 🧠 Mental Model / Analogy

> Mediator is like a company's HR department. Departments (colleagues) don't communicate directly for policy matters - they go through HR (mediator). Engineering says "we need 3 new hires." HR coordinates with Finance (budget approval), Facilities (desk allocation), and IT (equipment). Engineering doesn't call Finance or Facilities directly. Each department knows HR; HR knows everyone. Adding a new department: register it with HR. HR's coordination logic grows by the new department's rules.

- "HR department" → Mediator object
- "Departments" → Colleague objects
- "Engineering notifying HR" → `mediator.notify(this, "hiringRequest", 3)`
- "HR coordinating Finance, Facilities, IT" → Mediator's coordination logic
- "Each department knowing HR" → colleagues hold mediator reference
- "Adding a new department" → update Mediator's coordination, not existing departments

Where this analogy breaks down: in a real company, departments can also communicate directly when appropriate. Strict Mediator enforces ALL communication through the hub - sometimes impractically rigid.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Mediator is a "switchboard" between components. Instead of every component knowing every other component, every component knows only the switchboard. When one component wants to tell others something, it tells the switchboard. The switchboard knows who needs to know and tells them. New components just connect to the switchboard - nothing else changes.

**Level 2 - How to use it (junior developer):**
Create a `Mediator` interface with `notify(Colleague sender, String event)`. Implement a concrete `FormMediator` that has references to all form components. In the mediator's `notify()`: check which component sent the event and react by updating the relevant other components. Each `Colleague` has a `setMediator(Mediator m)` method. In their event handlers, colleagues call `mediator.notify(this, "eventName")`.

**Level 3 - How it works (mid-level engineer):**
The Mediator and Observer patterns overlap. The key difference: Observer broadcasts to all subscribers (they self-register for specific events). Mediator controls all communication centrally (it decides who receives what). For complex coordination with business rules (if A changes, sometimes update B and C, sometimes only B based on A's state), Mediator's centralised logic is cleaner than distributed subscription management. In Spring: `ApplicationEventPublisher` is a Mediator - components publish events; the application context routes them to the appropriate `@EventListener` methods. This is the "Mediator via event bus" hybrid - decoupled senders from receivers with centralised routing.

**Level 4 - Why it was designed this way (senior/staff):**
Mediator is the pattern behind nearly all message-oriented middleware. Kafka, RabbitMQ, and NATS are Mediators: producers send messages to the broker (Mediator); the broker routes them to consumers (colleagues). The pattern's centralisation trade-off is visible here: in a distributed system, the Mediator (broker) is the single point of coordination - and potentially single point of failure and bottleneck. This is why distributed systems use partitioned mediators (Kafka partitions). The Mediator can also be designed with a hierarchical structure for scalability - multiple sub-mediators coordinating locally, a master mediator coordinating sub-mediators. In UI frameworks, MediatR (C#) and similar libraries implement Mediator for CQRS command dispatch - a command is sent to the Mediator, which routes it to the appropriate handler.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│  MEDIATOR - HUB-AND-SPOKE COMMUNICATION              │
│                                                      │
│  WITHOUT MEDIATOR (mesh, n=5):                       │
│  A ←→ B ←→ C ←→ D ←→ E ←→ A  (10 connections)      │
│                                                      │
│  WITH MEDIATOR:                                      │
│                                                      │
│      A ─────────────────────── E                    │
│       \                       /                      │
│        B ─── [MEDIATOR] ─── D                       │
│       /                       \                      │
│      C ─────────────────────── (5 connections)       │
│                                                      │
│  Each colleague: knows ONLY the Mediator             │
│  Mediator: knows ALL colleagues                      │
└──────────────────────────────────────────────────────┘
```

**Coordination flow for country change:**
```
CountryDropdown.onChange("US"):
  mediator.notify(this, "countryChanged", "US")

FormMediator.notify(sender=CountryDD, event="countryChanged"):
  if (sender == countryDropdown):
    String newCountry = (String) data
    stateDropdown.loadStates(newCountry)
    zipField.setValidationPattern(
        ZipPatterns.forCountry(newCountry))
    phoneField.setCountryCode(
        CountryCodes.forCountry(newCountry))
    submitButton.setEnabled(false)
    loadStatesAsync(newCountry, () -> submitButton.setEnabled(true))
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
User selects "France" in CountryDropdown
  → CountryDropdown.onChange()
  → mediator.notify(countryDD, "countryChanged", "FR")
                              ← YOU ARE HERE
  → FormMediator coordinates:
      stateDropdown.loadDepartments("FR") (async)
      zipField.setPattern("[0-9]{5}")
      phoneField.setCode("+33")
      submitButton.disable()
  → loadDepartments callback fires:
      stateDropdown.populated
      submitButton.enable()
  → Form is consistent and ready
```

**FAILURE PATH:**
```
loadDepartments("FR") throws NetworkException
  → Mediator catches exception in async callback
  → Mediator notifies errorLabel.show("Failed to load")
  → submitButton remains disabled
  → User sees error message; form is in recoverable state
  → Mediator centralised the error handling - no component
    manages its own error state independently
```

**WHAT CHANGES AT SCALE:**
At microservice scale, the Mediator becomes a message broker (Kafka, RabbitMQ). Services publish events to the broker; the broker routes to subscribers based on topic/routing key. At 1M messages/second, the broker is partitioned for parallel throughput. The Mediator's centralisation trade-off now appears as broker availability - the entire communication fabric fails if the broker fails. Redundancy (replicated brokers) and partitioning are the scale-level responses.

---

### 💻 Code Example

**Example 1 - BAD: Direct colleague cross-references:**
```java
// BAD: CountryDropdown knows about all other components
public class CountryDropdown {
    private StateDropdown stateDropdown;  // direct ref!
    private ZipCodeField  zipField;       // direct ref!
    private PhoneField    phoneField;     // direct ref!
    private SubmitButton  submitButton;   // direct ref!

    public void onChange(String country) {
        stateDropdown.loadStates(country);  // coupled!
        zipField.setPattern(country);
        phoneField.setCode(country);
        submitButton.disable();
        // Adding a new field: MODIFY THIS CLASS
    }
}
```

**Example 2 - GOOD: Mediator pattern:**
```java
// Mediator interface
public interface FormMediator {
    void notify(FormComponent sender,
                String event, Object data);
}

// Abstract colleague
public abstract class FormComponent {
    protected FormMediator mediator;

    public void setMediator(FormMediator m) {
        this.mediator = m;
    }
}

// Concrete colleague - knows only mediator
public class CountryDropdown extends FormComponent {
    private String selectedCountry;

    public void selectCountry(String country) {
        this.selectedCountry = country;
        // Tell mediator - don't know WHO will react
        mediator.notify(this, "countryChanged", country);
    }
}

public class StateDropdown extends FormComponent {
    private List<String> states;

    public void loadStates(String country) {
        this.states = lookupStates(country);
        repaint();
    }
}

public class SubmitButton extends FormComponent {
    private boolean enabled = true;

    public void setEnabled(boolean on) {
        this.enabled = on;
        setClickable(on);
    }
}

// Concrete Mediator - ALL coordination logic here
public class SignupFormMediator implements FormMediator {
    private final CountryDropdown countries;
    private final StateDropdown   states;
    private final ZipCodeField    zip;
    private final PhoneField      phone;
    private final SubmitButton    submit;

    public SignupFormMediator(
            CountryDropdown c, StateDropdown s,
            ZipCodeField z, PhoneField p,
            SubmitButton b) {
        this.countries = c;
        this.states    = s;
        this.zip       = z;
        this.phone     = p;
        this.submit    = b;
        // Register mediator with all components:
        c.setMediator(this); s.setMediator(this);
        z.setMediator(this); p.setMediator(this);
        b.setMediator(this);
    }

    @Override
    public void notify(FormComponent sender,
                       String event, Object data) {
        if (sender == countries
                && "countryChanged".equals(event)) {
            String country = (String) data;
            states.loadStates(country);
            zip.setPattern(
                ZipPatterns.forCountry(country));
            phone.setCountryCode(
                CountryCodes.forCountry(country));
            submit.setEnabled(false);
            // After async state load: re-enable
        }
        // Other event handlers...
    }
}
```

**Example 3 - Spring ApplicationEventPublisher (event-based Mediator):**
```java
// Spring's event system IS a Mediator
@Service
public class OrderService {
    private final ApplicationEventPublisher publisher;
    // publisher IS the Mediator

    public void placeOrder(Order order) {
        repository.save(order);
        // Publish via Mediator - no direct dep on consumers
        publisher.publishEvent(
            new OrderPlacedEvent(this, order));
    }
}

// Independent listener - no reference to OrderService
@Component
public class InventoryReservationListener {
    @EventListener
    public void onOrderPlaced(OrderPlacedEvent event) {
        inventory.reserve(event.getOrder().getItems());
    }
}

@Component
public class OrderConfirmationEmailListener {
    @EventListener
    public void onOrderPlaced(OrderPlacedEvent event) {
        emailService.sendConfirmation(
            event.getOrder().getCustomerEmail());
    }
}
// OrderService never knows about inventory or email services
// They connect via the Spring ApplicationContext (Mediator)
```

---

### ⚖️ Comparison Table

| Pattern | Communication | Direction | Coordination | Best For |
|---|---|---|---|---|
| **Mediator** | Via central hub | Many→1→Many | Hub contains logic | UI forms, chat rooms, workflows |
| Observer | Direct broadcast | 1→Many | Distributed in subscribers | Event notifications, reactive updates |
| Event Bus | Via bus | Many→Many (async) | Bus routes by type | Microservice events, loose coupling |
| Facade | Simplified access | N→1 (simplify) | Facade hides subsystem | API simplification, not communication |
| Command | Encapsulated action | 1→1 (deferred) | Command contains logic | Undo, queue, distributed actions |

How to choose: use Mediator when coordination logic between colleagues is complex and centralisation is desirable for testability. Use Observer when publishers just need to notify - without coordinating a response. Use Event Bus (async Mediator) when components live in different services or threads and direct method calls are not possible.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Mediator and Observer are the same | Observer: each subscriber decides independently what to do with an event. Mediator: the central object coordinates the response - it tells colleagues what to DO, not just notifies them |
| Mediator reduces total complexity | Mediator CONCENTRATES complexity - the total coordination logic is the same. It just moves from being distributed across N colleagues to being in one Mediator. It can become a God Object |
| All inter-component communication must go through the Mediator | Only coordination benefits from mediation. Simple data retrieval (`componentA.getValue()`) can remain direct if there is no coordination aspect |
| Using a Mediator guarantees loose coupling | Components are decoupled from each other but tightly coupled to the Mediator. If the Mediator changes (new event, new component), many coordinator interactions must be updated |
| Mediator and Facade solve the same problem | Facade simplifies access to a subsystem (reduces interface complexity). Mediator coordinates between peers (reduces coupling complexity). Different dimensions |

---

### 🚨 Failure Modes & Diagnosis

**1. Mediator Becomes a God Object**

**Symptom:** The `FormMediator` class has 1,500 lines, 40 event handlers, and coordinates 20 different UI components. A bug in button enabling requires reading through hundreds of unrelated event handlers to understand the full coordination graph.

**Root Cause:** All coordination logic accumulated in one Mediator without cohesive structure. The Mediator has become a God Object with no single responsibility.

**Diagnostic:**
```bash
wc -l src/FormMediator.java
# If > 300 lines: likely too many responsibilities
grep "if (sender ==" src/FormMediator.java | wc -l
# Each sender check = one responsibility in the mediator
# If > 10: split into specialised sub-mediators
```

**Fix:**
Split the Mediator into focused sub-mediators: `LocationMediator` (handles country/state/zip coordination), `PaymentMediator` (handles payment field coordination), `ValidationMediator` (handles validation messages). A root `FormMediator` delegates to sub-mediators.

**Prevention:** Design rule: one Mediator per cohesive group of colleagues. A form with 20 fields is likely 4–5 logical groups, each deserving its own Mediator.

---

**2. Infinite Mediation Loop**

**Symptom:** After the country changes, the form freezes. Stack overflow eventually occurs.

**Root Cause:** Mediator updates `StateDropdown` in response to country change. `StateDropdown.loadStates()` notifies the Mediator of `"statesLoaded"` event, which triggers further coordination that causes another country change notification - infinite loop.

**Diagnostic:**
```java
// Add event trace logging to find the cycle:
public void notify(FormComponent sender,
                   String event, Object data) {
    log.trace("Mediator: {} sent '{}'",
        sender.getClass().getSimpleName(), event);
    // ...
}
// Cyclic events appear in log as rapid repeating sequences
```

**Fix:**
Design coordination logic with clear directionality. Mark programmatic updates (from Mediator) to distinguish them from user-initiated updates, preventing re-notification:
```java
stateDropdown.loadStates(country); // sets a flag
// StateDropdown only notifies mediator on USER selection
// not on programmatic loadStates() call
```

**Prevention:** Document coordination event flow as a directed acyclic graph. If a cycle exists at design time, it must be explicitly broken with a direction flag.

---

**3. Mediator Holds Stale Component References**

**Symptom:** After a UI component is replaced (e.g., country dropdown swapped for a region selector in a modal), events from the old component still reach the Mediator, which calls methods on the old (possibly garbage-collected) component.

**Root Cause:** Mediator holds strong references to components. When a component is replaced, the Mediator is not updated.

**Diagnostic:**
```java
// Check if mediator references are stale:
for (FormComponent c : mediator.getComponents()) {
    if (c.isDetached()) { // UI component removed from DOM/scene
        log.warn("Stale mediator reference: {}",
            c.getClass().getSimpleName());
    }
}
```

**Fix:**
Add `mediator.deregister(oldComponent)` when replacing components. Use weak references in the Mediator if components have shorter lifetimes than the Mediator.

**Prevention:** Define explicit lifecycle events for components: on creation, call `mediator.register(this)`; on destruction, call `mediator.deregister(this)`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Coupling` - Mediator exists to reduce coupling; understanding tight vs loose coupling motivates the pattern
- `Observer` - frequently confused with Mediator; understanding Observer first clarifies the key difference (distributed vs centralised coordination)
- `Interface` - Mediator and Colleague interfaces are the contracts that enable decoupling

**Builds On This (learn these next):**
- `Event Bus Pattern` - asynchronous Mediator; events are broadcast through a bus; components subscribe to event types
- `CQRS Pattern` - command dispatch via a Mediator is a core CQRS implementation technique (MediatR in .NET, similar libraries in Java)
- `Message Broker` - Mediator at infrastructure scale; Kafka and RabbitMQ are Mediators for microservice communication

**Alternatives / Comparisons:**
- `Observer` - distributed coordination (each subscriber self-manages); use when coordination is simple and subscribers are independent
- `Facade` - simplifies access to a subsystem; does not coordinate between peers
- `Event Bus Pattern` - async/decoupled variation of Mediator; better when components are distributed or loosely timed

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Central hub that all components talk to   │
│              │ instead of talking to each other directly │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ N components communicating directly creates│
│ SOLVES       │ O(n²) coupling and spaghetti references   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Total coordination logic is unchanged;    │
│              │ Mediator concentrates it in one place     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Many objects communicate with complex      │
│              │ interdependencies hard to manage directly │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Communication is simple (use Observer);   │
│              │ the Mediator would become a God Object    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Decoupled colleagues + testable logic vs  │
│              │ Mediator God Object risk                  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Talk to the tower, not to              │
│              │  the other planes."                       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Event Bus Pattern → CQRS →                │
│              │ Message Broker                            │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When components or services need to communicate in complex
many-to-many patterns, introduce a central coordinator that
owns the communication logic. Components speak only to the
mediator; the mediator knows the routing.

**Where else this pattern appears:**
- **Air traffic control (ATC):** Aircraft communicate only with
  ATC, not with each other -- the controller mediates all
  routing decisions, preventing collision from uncoordinated
  direct communication.
- **Message brokers (Kafka):** Producers and consumers don't
  know about each other -- the broker mediates asynchronous
  delivery, partitioning, and offset management.
- **Redux store:** React components dispatch actions to the
  store (mediator); the store calls reducers and notifies
  subscribers -- no component communicates directly with another.

---

### 💡 The Surprising Truth

The Mediator pattern and the Service Bus / Message Broker
are architecturally identical -- the difference is purely one
of scale. A Mediator is a class-level coordinator inside a
process; a Service Bus is a network-level coordinator between
processes. This means teams that adopt an ESB (Enterprise
Service Bus) or message broker have, knowingly or not, scaled
the Mediator pattern to infrastructure. The well-known problem
with enterprise ESBs ("the ESB becomes a God Object") is
the distributed version of Mediator's own failure mode:
the mediator accumulates too much logic and becomes a
bottleneck.
---

### 🧠 Think About This Before We Continue

**Q1.** A gaming lobby system uses Mediator: a `LobbyMediator` coordinates `PlayerSlot` components. When a player joins, the Mediator marks a slot as taken, checks if the lobby is full, starts a countdown, and notifies the host. With 100 lobbies active simultaneously, each with its own `LobbyMediator` instance, and 10,000 join/leave events per second, profile the coordination overhead. Then describe an architecture where the Mediator's coordination logic is stateless and shared across all lobby instances - reducing memory from N mediator instances to 1, without compromising per-lobby state isolation.

*Hint: Look at the First Principles section for the core invariants, and the Failure Modes section for where this scenario appears as a documented issue.*

**Q2.** A checkout form uses Mediator for component coordination. The product team wants to A/B test two coordination behaviours: Variant A (standard flow) vs Variant B (coupon code field triggers early price recalculation). Without the Mediator pattern, this requires conditional code in each affected component. With Mediator, describe exactly which files change, what the minimum code change is, and how the A/B test flag would be propagated into the Mediator to switch between coordination strategies at runtime.



*Hint: The Comparison Table and the Level 3-4 explanations contain the mechanism that determines which approach wins in this scenario.*

**Q3 (Design Trade-off):** A monolith uses an in-process
`EventBus` (Mediator) for all inter-module communication.
The team is splitting the monolith into microservices. They
must decide: (1) keep the event bus in-process within each
service, (2) use Kafka as an inter-service event bus, or
(3) use direct REST calls. State the decision criteria and
map each approach to the correct interaction pattern.

*Hint: The WHAT CHANGES AT SCALE section addresses this
directly. Consider what happens to the Mediator when the
"colleagues" are on different servers with network partitions
between them.*
