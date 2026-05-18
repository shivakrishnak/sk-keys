---
id: DPT-023
title: Mediator
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-005, DPT-019
used_by: DPT-064, DPT-065
related: DPT-019, DPT-025, DPT-037, DPT-016
tags:
  - pattern
  - behavioral
  - advanced
  - decoupling
  - event-driven
  - chat
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 23
permalink: /technical-mastery/design-patterns/mediator/
---

⚡ TL;DR - Mediator centralizes communication between
objects that would otherwise reference each other directly,
reducing the web of N×(N-1) direct dependencies to N
single mediator dependencies.

| #23 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-019 | |
| **Used by:** | DPT-064, DPT-065 | |
| **Related:** | DPT-019, DPT-025, DPT-037, DPT-016 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A chat room application: 10 users can message any other
user or broadcast to all. Without Mediator: each User
object holds references to all 9 other User objects. When
User A sends a message, it directly calls
`userB.receive()`, `userC.receive()`, etc. 10 users =
10 × 9 = 90 direct object-to-object dependencies. Adding
User 11: update ALL existing users to hold a reference
to the newcomer.

**THE BREAKING POINT:**
The dependency graph is a fully-connected mesh. Any change
to one user's interface potentially breaks all 9 other
users. Testing User A in isolation requires mocking all
9 others. The system is unmanageable.

**THE INVENTION MOMENT:**
Mediator: create a `ChatRoom` object that all users know.
User A sends message to `ChatRoom`. `ChatRoom` distributes
to all (or specific) users. Now each User knows only the
`ChatRoom` (1 dependency). Adding User 11: register with
`ChatRoom` - no other user changes. 10 users, 10 dependencies
(vs 90). The `ChatRoom` IS the Mediator.

**EVOLUTION:**
Spring's `ApplicationEventPublisher`, Java Message Service
(JMS), and AMQP message brokers are Mediator implementations.
The Event Bus pattern is Mediator at the architecture level.
Kubernetes API server is a Mediator: all components
(controllers, schedulers, kubelet) communicate through
the API server, not directly with each other.

---

### 📘 Textbook Definition

The **Mediator** pattern is a Behavioral design pattern
that defines an object that encapsulates how a set of
objects interact. Mediator promotes loose coupling by
keeping objects from referring to each other explicitly,
and it allows you to vary their interaction independently.
The Mediator centralizes complex communications and control
logic between related objects (Colleagues). Colleagues
communicate only through the Mediator; they do not know
about each other.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Mediator replaces a tangle of direct object-to-object
dependencies with a star topology - all objects talk
to the mediator, not to each other.

**One analogy:**
> Air Traffic Control (Mediator). Planes (Colleagues) do
> not communicate directly with each other. Every plane
> talks only to ATC. ATC coordinates: "Flight 101, hold
> at 10,000ft. Flight 202, you are clear to land." Without
> ATC: planes would need to coordinate directly with every
> other plane in the airspace (N² communication).

**One insight:**
Mediator trades N² dependencies for N single dependencies.
The trade-off: the mediator becomes the most complex object
in the system because it knows all the coordination rules.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Colleagues never reference each other directly - only
   the Mediator.
2. All communication goes through the Mediator.
3. The Mediator knows all Colleagues; each Colleague
   knows only the Mediator.

**DERIVED DESIGN:**
Two participants:
- **Mediator**: interface for communicating with Colleague objects
- **ConcreteMediator**: implements coordination behavior;
  knows and maintains its Colleagues
- **Colleague**: knows only its Mediator; notifies the
  Mediator of state changes; receives notifications from
  the Mediator

**DEPENDENCIES:**
```
Without Mediator: A→B, A→C, B→A, B→C, C→A, C→B (6 deps, 3
  objects)
With Mediator:    A→M, B→M, C→M, M→A, M→B, M→C (6 deps
  total but star topology)
At N=10: N(N-1)=90 without vs 2N=20 with Mediator
```

**TRADE-OFFS:**

**Gain:** Reduced object coupling. Centralized coordination
logic. Independent testing of colleagues. Easy to add/remove
colleagues.

**Cost:** Mediator becomes a "God Object" if coordination
logic grows uncontrolled. All coupling is concentrated in
the mediator - can be harder to understand. Single point
of failure.

---

### 🧪 Thought Experiment

**SETUP:**
A UI form with interdependent fields: a "Discount Code"
input, a "Price" display, and a "Submit" button. Business
rules: if a valid discount code is entered, the price
updates; the Submit button is enabled only if the price
is valid and a product is selected.

**WITHOUT MEDIATOR:**
Each UI component knows the others. DiscountCodeInput
knows PriceDisplay and calls `price.update()`. PriceDisplay
knows SubmitButton and calls `submit.enable()`. Adding
a new component (PromoLabel) that also shows the discount:
modify DiscountCodeInput to also call `promoLabel.show()`.

**WITH MEDIATOR:**
FormMediator knows all components. Each component notifies
the mediator on change. `mediator.onDiscountCodeChanged(code)`:
validates code, updates price display, checks all conditions,
enables/disables submit. Adding PromoLabel: one new line
in the mediator. No component changes.

---

### 🧠 Mental Model / Analogy

> Mediator is an AIR TRAFFIC CONTROL TOWER. Each plane
> (Colleague) communicates only with the tower (Mediator).
> The tower maintains awareness of all planes and coordinates
> their movements. No plane needs to know where every
> other plane is or what they are doing. The tower is the
> single point of coordination - which makes it complex,
> but makes each plane simple.

- "Tower" = Mediator
- "Plane" = Colleague
- "Radio to tower" = Colleague.notifyMediator()
- "Tower to planes" = Mediator.notify(colleague, event)

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Mediator is a coordinator that all objects talk to instead
of talking to each other directly. Like a group chat vs
direct messages between everyone: one conversation thread
(mediator) instead of N×N private threads.

**Level 2 - How to use it (junior developer):**
Create a `Mediator` interface with `notify(sender, event)`.
Have each Colleague hold a reference to the Mediator.
When a Colleague changes state, it calls `mediator.notify(this, "CHANGED")`.
The ConcreteMediator knows all colleagues and reacts to
events by calling appropriate colleague methods.

**Level 3 - How it works (mid-level engineer):**
Spring's `ApplicationEventPublisher` is Mediator: beans
publish events via `applicationEventPublisher.publishEvent(event)`.
Other beans annotated with `@EventListener` receive the event.
The publisher and listeners do not know each other.
`ApplicationEventPublisher` (the Mediator) decouples them.
Kafka topics are Mediator implementations at service level:
producer (Colleague) sends to a topic (Mediator); consumer
(Colleague) receives from the topic; producer and consumer
do not know about each other.

**Level 4 - Why it was designed this way (senior/staff):**
Mediator solves the Demeter Law violation at the object
graph level. The Law of Demeter says objects should talk
only to their direct collaborators. A fully-connected
mesh violates this: every object is a direct collaborator
of every other. Mediator enforces Demeter by design: each
object's only collaborator IS the mediator. This is also
why microservice event buses follow the pattern: services
should not call each other directly (creating service
mesh spaghetti) but communicate through a bus (Mediator).

**Level 5 - Mastery (distinguished engineer):**
The Mediator pattern connects to the CQRS architecture:
the Command Bus IS a Mediator. Commands from multiple
sources (API controllers, scheduled jobs, event-driven
triggers) are dispatched to the bus. The bus routes each
command to its handler. No source needs to know which
handler exists. In Axon Framework: `commandGateway.send(command)`
dispatches to the bus (Mediator); the command handler
is the Colleague. Axon's `EventBus` is another Mediator:
domain events published by aggregate handlers are distributed
to event handler components. The entire Axon architecture
is Mediator-based.

---

### ⚙️ How It Works (Mechanism)

```
Mediator Pattern Structure
┌─────────────────────────────────────────────────────────┐
│ <<interface>> Mediator                                  │
│   + notify(sender: Colleague, event: String): void      │
│                                                         │
│ ConcreteMediator implements Mediator                    │
│   - colleagueA: ColleagueA                              │
│   - colleagueB: ColleagueB                              │
│   + notify(sender, event):                              │
│       if sender is A and event is "CHANGED":            │
│           colleagueB.reactToAChange()                   │
│       if sender is B and event is "SELECTED":           │
│           colleagueA.update()                           │
│                                                         │
│ Colleague (abstract)                                    │
│   - mediator: Mediator                                  │
│   + Colleague(mediator): mediator = mediator            │
│                                                         │
│ ColleagueA extends Colleague                            │
│   + doSomething():                                      │
│       // ... own logic                                  │
│       mediator.notify(this, "CHANGED")                  │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Chat room: Alice, Bob, Carol are colleagues; ChatRoom is
  mediator.

Alice sends "Hello":
  alice.sendMessage("Hello")
    → chatRoom.broadcast(alice, "Hello")  ← mediator
        → bob.receive("Alice: Hello")
        → carol.receive("Alice: Hello")
Alice does not know Bob or Carol exist.

Bob leaves:
  chatRoom.unregister(bob)  ← mediator updates list
Alice sends "Hello again":
  chatRoom.broadcast(alice, "Hello again")
    → carol.receive("Alice: Hello again")
    // Bob is no longer in chatRoom's list - no change to
      Alice
```

---

### 💻 Code Example

**Example 1 - Without Mediator (object mesh):**

```java
// BAD: each user knows all other users
class User {
    private String name;
    private List<User> others = new ArrayList<>();

    void addContact(User u) { others.add(u); }

    void sendMessage(String msg) {
        // Must know all others directly
        for (User u : others) {
            u.receive(name + ": " + msg);
        }
    }
    // Adding new user: update ALL existing users' others list
}
```

**Example 2 - Mediator solution:**

```java
// GOOD: colleagues communicate only through mediator

interface ChatMediator {
    void sendMessage(String msg, ChatUser sender);
    void register(ChatUser user);
}

class ChatRoom implements ChatMediator {
    private final List<ChatUser> users = new ArrayList<>();

    @Override
    public void register(ChatUser user) {
        users.add(user);
    }

    @Override
    public void sendMessage(String msg, ChatUser sender) {
        users.stream()
            .filter(u -> u != sender) // don't send to self
            .forEach(u -> u.receive(sender.getName(), msg));
    }
}

class ChatUser {
    private final String name;
    private final ChatMediator mediator;

    ChatUser(String name, ChatMediator mediator) {
        this.name = name;
        this.mediator = mediator;
        mediator.register(this); // register with mediator
    }

    void send(String msg) {
        System.out.println(name + " sends: " + msg);
        mediator.sendMessage(msg, this); // only talks to mediator
    }

    void receive(String fromName, String msg) {
        System.out.println(
            name + " received from " + fromName + ": " + msg);
    }

    String getName() { return name; }
}

// Usage: users know nothing about each other
ChatMediator chatRoom = new ChatRoom();
ChatUser alice = new ChatUser("Alice", chatRoom);
ChatUser bob = new ChatUser("Bob", chatRoom);
ChatUser carol = new ChatUser("Carol", chatRoom);

alice.send("Hello everyone!"); // ChatRoom routes to Bob and Carol
// Adding Dave: new ChatUser("Dave", chatRoom) - nothing else changes
```

**Example 3 - Spring ApplicationEventPublisher as Mediator:**

```java
// RECOGNITION: Spring events ARE Mediator pattern

// Publisher (Colleague A): knows only ApplicationEventPublisher
@Service
class OrderService {
    @Autowired
    private ApplicationEventPublisher publisher; // the mediator

    public void placeOrder(Order order) {
        // actual order logic
        orderRepo.save(order);
        // publish event - does not know who listens
        publisher.publishEvent(new OrderPlacedEvent(order));
    }
}

// Listener (Colleague B): also knows only ApplicationEventPublisher
@Service
class NotificationService {
    // @EventListener is how this Colleague registers with Mediator
    @EventListener
    public void onOrderPlaced(OrderPlacedEvent event) {
        emailService.sendConfirmation(event.getOrder());
    }
}

// OrderService and NotificationService do NOT know each other.
// ApplicationEventPublisher (Mediator) routes the event.
// Adding new listener (AuditService): zero changes to OrderService
```

**How to test/verify correctness:**
Test the Mediator independently: verify that `notify(sender,
event)` triggers the correct responses on other colleagues.
Test each Colleague independently: mock the Mediator;
verify the Colleague sends the correct notification when
it changes state. Integration test: build the full mediator
+ colleagues setup and verify end-to-end event flow.

---

### ⚖️ Comparison Table

| Pattern | All notified? | Routing? | Direction | Hub type |
|---|---|---|---|---|
| **Mediator** | Selective (hub decides) | Yes | Bidirectional | Active (smart) |
| Observer | All subscribers | No | Unidirectional | Passive (relay) |
| Facade | N/A | N/A | One-way (simplified) | Simplifies access |
| Event Bus | All subscribers | Topic-based | Unidirectional | Passive (relay) |

**Mediator vs Observer:**
- Observer: publisher doesn't care who listens; ALL observers
  notified; passive relay
- Mediator: hub decides WHO gets notified; can suppress,
  transform, route; hub has business logic

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Mediator and Observer are the same | Observer: "all subscribers get the event, no routing logic." Mediator: "the hub decides who gets what based on logic." Observer is passive; Mediator is active (has coordination rules). Spring's @EventListener is closer to Observer; a conditional dispatch system is closer to Mediator |
| Mediator solves the God Object problem | Mediator CREATES a God Object (the mediator knows everything). It is a trade-off: distribute complexity to many objects (mesh) vs concentrate it in one (mediator). Choose based on whether centralized coordination is cleaner than distributed |
| Facade and Mediator are the same | Facade: simplifies a SUBSYSTEM for CLIENTS (one-way). Mediator: coordinates COLLEAGUES with EACH OTHER (bidirectional). Facade is about simplifying access; Mediator is about decoupling mutual dependencies |
| Kafka is just a message queue, not a pattern | Kafka topics implement the Mediator pattern at the service level: producers and consumers do not know each other; the topic (Mediator) routes messages; producers and consumers are Colleagues |

---

### 🚨 Failure Modes & Diagnosis

**Mediator Becomes God Object**

**Symptom:**
The ConcreteMediator class grows to 1,200 lines. It handles
chat, authentication, file transfers, group management,
and presence tracking. Every new feature requires modifying
the mediator. New developers are afraid to touch it.

**Root Cause:**
The Mediator pattern concentrates coordination logic by
design. Without discipline, all coordination for the
entire application lands in one class.

**Diagnostic Signal:**
Mediator class > 500 lines, > 10 colleague types, methods
with complex if/else chains switching on colleague type.

**Fix:**
Decompose the mediator by concern: `ChatMediator`,
`PresenceMediator`, `FileTransferMediator`. Use a message
bus pattern for broader coordination: `EventBus.publish(event)`.

**Prevention:**
Each mediator should have a clear, bounded responsibility.
Name it specifically: `CheckoutFormMediator`, not
`FormMediator`. When responsibility expands beyond the
name: create a new, focused mediator.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Observer` - DPT-025; the contrast between Observer
  (passive broadcast) and Mediator (active coordination)
  is the key conceptual distinction

**Builds On This (learn these next):**
- `Event Bus Pattern` - DPT-037; Mediator at the architecture
  level; message brokers (Kafka, RabbitMQ) as Mediators

**Alternatives / Comparisons:**
- `Observer` - broadcast to all; Mediator routes selectively
- `Facade` - simplifies subsystem access; Mediator decouples
  peers from knowing each other

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Centralized hub replacing N×(N-1) direct │
│              │ dependencies with N single mediator deps │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ Colleagues know only the mediator;       │
│              │ mediator has routing/coordination logic  │
├──────────────┼──────────────────────────────────────────┤
│ REAL EXAMPLE │ Air Traffic Control, chat room,          │
│              │ Spring ApplicationEventPublisher, Kafka  │
├──────────────┼──────────────────────────────────────────┤
│ FAILURE MODE │ Mediator grows into God Object - split   │
│              │ by responsibility when this happens      │
├──────────────┼──────────────────────────────────────────┤
│ VS OBSERVER  │ Observer: passive relay, all notified    │
│              │ Mediator: active hub, routes selectively │
├──────────────┼──────────────────────────────────────────┤
│ MATH         │ Without: N(N-1) deps; With: N deps       │
│              │ N=10: 90 vs 10 dependencies              │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Memento → Observer → State → Strategy    │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Mediator replaces N×(N-1) direct dependencies with N
   single-mediator dependencies - this is the core mathematical
   trade-off (N=10: 90 deps vs 10)
2. Spring's `ApplicationEventPublisher` is Mediator: publisher
   knows only the publisher; listener registers with
   `@EventListener`; they never reference each other
3. Mediator vs Observer: Mediator has routing/coordination
   logic (smart hub); Observer is a passive relay to all
   subscribers (dumb hub)

**Interview one-liner:**
"Mediator centralizes communication between objects, replacing
N×N direct dependencies with N single-mediator dependencies.
Spring's ApplicationEventPublisher is a Mediator: publishers
and listeners don't know each other. The risk: the mediator
can become a God Object if coordination logic grows unchecked."

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [CALCULATE] For a system with 15 objects that all
   communicate with each other, calculate the number of
   dependencies without Mediator vs with Mediator
2. [DISTINGUISH] Explain the structural and behavioral
   difference between Observer and Mediator, with one
   concrete example where Mediator is more appropriate
   than Observer
3. [IMPLEMENT] Build a form mediator for a checkout form
   with interdependent discount code, price display, and
   submit button components
4. [IDENTIFY] Explain how Spring's ApplicationEventPublisher
   maps to the Mediator pattern participants

