---
layout: default
title: "Mediator Pattern"
parent: "Design Patterns"
nav_order: 781
permalink: /design-patterns/mediator-pattern/
number: "781"
category: Design Patterns
difficulty: ★★★
depends_on: "Object-Oriented Programming, Observer Pattern, Event-Driven Pattern"
used_by: "Chat rooms, Air traffic control, UI component coordination, Event buses"
tags: #advanced, #design-patterns, #behavioral, #oop, #decoupling, #coordination
---

# 781 — Mediator Pattern

`#advanced` `#design-patterns` `#behavioral` `#oop` `#decoupling` `#coordination`

⚡ TL;DR — **Mediator** centralizes complex communications between multiple objects — instead of components communicating directly with each other (O(n²) connections), they all communicate through one mediator (O(n) connections), reducing coupling and making it easy to change coordination logic.

| #781            | Category: Design Patterns                                               | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Object-Oriented Programming, Observer Pattern, Event-Driven Pattern     |                 |
| **Used by:**    | Chat rooms, Air traffic control, UI component coordination, Event buses |                 |

---

### 📘 Textbook Definition

**Mediator** (GoF, 1994): a behavioral design pattern that defines an object that encapsulates how a set of objects interact. Mediator promotes loose coupling by keeping objects from referring to each other explicitly, and lets you vary their interaction independently. Without Mediator: each object in a set knows about all others — O(n²) direct connections. With Mediator: each object knows only the mediator — O(n) connections. The Mediator centralizes complex communication and control logic. GoF intent: "Define an object that encapsulates how a set of objects interact. Mediator promotes loose coupling by keeping objects from referring to each other explicitly, and it lets you vary their interaction independently."

---

### 🟢 Simple Definition (Easy)

Air traffic control tower. 50 planes want to land. Without the tower: each plane communicates with all 49 others to coordinate — 50×49/2 = 1,225 communication channels. Chaos. With the tower (mediator): each plane only communicates with the tower. Tower decides: "Flight 123, you're cleared to land on runway 3." Tower coordinates all interactions. 50 planes × 1 tower = 50 communication channels. The planes don't talk to each other — they talk to the mediator.

---

### 🔵 Simple Definition (Elaborated)

A GUI dialog with multiple components: a checkbox, dropdown, and submit button. When the checkbox is checked, the dropdown should enable. When the dropdown has a value, the submit button should enable. Without Mediator: checkbox has reference to dropdown and button. Dropdown has reference to button. 3-way coupling. With Mediator (`DialogMediator`): checkbox sends event to mediator. Mediator decides: "dropdown should now enable." All coordination logic in one place.

---

### 🔩 First Principles Explanation

**O(n²) → O(n) connection reduction and centralized coordination:**

```
WITHOUT MEDIATOR — N×(N-1)/2 CONNECTIONS:

  Component A ←─────── Component B
      │   ↑           ↑    │
      │   └──── C ────┘    │
      └──────────────── Component D

  4 components → 6 direct connections.
  10 components → 45 connections.
  Each component knows about others — tightly coupled.
  Change component A's interface → update all that depend on A.

WITH MEDIATOR — N CONNECTIONS:

  Component A ←──── Mediator ────→ Component B
  Component C ←──────────────────→ Component D

  4 components → 4 connections to mediator.
  10 components → 10 connections.
  Each component knows only mediator. Components are independent.

CHAT ROOM MEDIATOR:

  // WITHOUT MEDIATOR: each user knows all other users:
  class User {
      List<User> otherUsers;
      void send(String message) {
          for (User u : otherUsers) u.receive(message);  // knows all others
      }
  }

  // WITH MEDIATOR:
  interface ChatMediator {
      void sendMessage(String message, User sender);
      void addUser(User user);
  }

  class ChatRoom implements ChatMediator {
      private final List<User> users = new ArrayList<>();

      void addUser(User user) { users.add(user); }

      void sendMessage(String message, User sender) {
          for (User user : users) {
              if (user != sender) {             // don't send to self
                  user.receive(sender.getName() + ": " + message);
              }
          }
      }
  }

  class User {
      private final String name;
      private final ChatMediator mediator;     // knows ONLY mediator — not other users

      User(String name, ChatMediator mediator) {
          this.name = name;
          this.mediator = mediator;
          mediator.addUser(this);
      }

      void send(String message) {
          mediator.sendMessage(message, this);   // sends via mediator
      }

      void receive(String message) {
          System.out.println(name + " received: " + message);
      }
  }

  // Usage:
  ChatRoom room = new ChatRoom();
  User alice = new User("Alice", room);
  User bob   = new User("Bob",   room);
  User carol = new User("Carol", room);

  alice.send("Hello everyone!");
  // Alice → mediator → Bob receives "Alice: Hello everyone!"
  //                  → Carol receives "Alice: Hello everyone!"

  // Adding Dave: one new User. No changes to Alice, Bob, or Carol.
  User dave = new User("Dave", room);

GUI COMPONENT COORDINATION — CLASSIC MEDIATOR USE CASE:

  interface DialogMediator {
      void notify(Component component, String event);
  }

  class LoginDialog implements DialogMediator {
      private final Checkbox rememberMe;
      private final TextField daysField;  // "remember for N days"
      private final Button loginButton;

      @Override
      public void notify(Component component, String event) {
          if (component == rememberMe && event.equals("CHECK")) {
              // When checkbox checked: enable daysField:
              daysField.setEnabled(rememberMe.isChecked());
          }
          if (component == daysField && event.equals("CHANGE")) {
              // When days field changes: validate and enable/disable loginButton:
              loginButton.setEnabled(isValidForm());
          }
      }

      private boolean isValidForm() { ... }
  }

  // Each component sends events to mediator — doesn't know what else to do:
  class Checkbox extends Component {
      private final DialogMediator mediator;

      void setChecked(boolean checked) {
          this.checked = checked;
          mediator.notify(this, "CHECK");   // tell mediator; let mediator decide consequences
      }
  }

  // All component interaction logic: centralized in LoginDialog.
  // Change "when checkbox checked → what happens": only change LoginDialog.

MEDIATOR vs FACADE:

  FACADE:
  - External client uses simplified interface to access a subsystem.
  - Unidirectional: client → facade → subsystem.
  - Subsystem components don't know about facade.

  MEDIATOR:
  - INTERNAL components use mediator to communicate with EACH OTHER.
  - Bidirectional: components → mediator → other components.
  - Components know about mediator; mediator knows about all components.
  - "Air traffic controller" — coordinates between equals, not simplifies from outside.

MEDIATOR vs OBSERVER:

  OBSERVER:
  - Subject broadcasts to subscribers.
  - Subject doesn't know who the subscribers are.
  - Subscribers decide what to do with the notification.

  MEDIATOR:
  - Components send events to mediator.
  - Mediator decides which other components to notify and HOW to react.
  - Centralized coordination logic; the mediator IS the orchestration.

  EVENT BUS = Observer + Mediator concepts combined:
  Components publish events. Event bus routes to subscribers.
  Coordination logic: in subscribers (Observer-style) or in the bus routing rules (Mediator-style).
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Mediator:

- N components × N-1 references = O(n²) connections; change one interface → update N-1 others
- Coordination logic scattered across all components

WITH Mediator:
→ Each component: 1 reference (mediator). N connections total. Change component → only mediator changes.
→ All coordination logic centralized in mediator — one place to understand and change interaction rules.

---

### 🧠 Mental Model / Analogy

> Air traffic control tower. 50 planes approach the airport. Without a tower, each plane would need to coordinate with all 49 others — impossible. The tower (mediator) receives all planes' positions and intentions, and issues clearances: "flight 123 land runway 2, flight 456 hold pattern, flight 789 land runway 3." Each plane obeys the tower. Planes don't talk to each other. Tower has the full picture and makes all coordination decisions.

"50 planes" = N components (User, UI Component, microservice)
"Tower (ATC)" = Mediator (centralized coordinator)
"Plane sends position + request" = component.notify(mediator, event)
"Tower issues clearance" = mediator.notify(component, instruction)
"Planes don't talk to each other" = components only know the mediator

---

### ⚙️ How It Works (Mechanism)

```
MEDIATOR STRUCTURE:

  Component A       Mediator          Component B
  ───────────       ────────          ───────────
  +notify(event) ──►+notify(C, event)
                    ──────────────────► B.receive(event)

  Each component holds reference to Mediator only.
  Mediator holds references to all components.
  Mediator decides who to notify and how.
```

---

### 🔄 How It Connects (Mini-Map)

```
Multiple components with complex direct cross-dependencies
        │
        ▼
Mediator Pattern ◄──── (you are here)
(centralize coordination; O(n²) → O(n); components know only mediator)
        │
        ├── Observer: subject notifies subscribers (vs Mediator: component notifies mediator)
        ├── Facade: simplifies subsystem access (vs Mediator: coordinates internal interaction)
        ├── Event Bus: distributed Mediator (components publish events; bus routes)
        └── Command: commands passed through mediator can trigger coordinated responses
```

---

### 💻 Code Example

```java
// Microservice coordination via Mediator (orchestration pattern):

interface WorkflowMediator {
    void handle(WorkflowEvent event);
}

// Components (microservice interfaces):
interface InventoryService  { void reserve(String orderId, List<OrderItem> items); }
interface PaymentService    { void charge(String orderId, BigDecimal amount); }
interface ShippingService   { void schedule(String orderId, Address address); }
interface NotificationService { void notify(String customerId, String message); }

// Mediator — orchestrates the order fulfillment workflow:
class OrderFulfillmentMediator implements WorkflowMediator {
    @Autowired InventoryService inventory;
    @Autowired PaymentService payment;
    @Autowired ShippingService shipping;
    @Autowired NotificationService notification;

    @Override
    public void handle(WorkflowEvent event) {
        switch (event.getType()) {
            case ORDER_PLACED:
                Order order = event.getPayload(Order.class);
                inventory.reserve(order.getId(), order.getItems());
                break;
            case INVENTORY_RESERVED:
                order = event.getPayload(Order.class);
                payment.charge(order.getId(), order.getTotal());
                break;
            case PAYMENT_CHARGED:
                order = event.getPayload(Order.class);
                shipping.schedule(order.getId(), order.getShippingAddress());
                notification.notify(order.getCustomerId(), "Payment confirmed!");
                break;
            case SHIPPING_SCHEDULED:
                order = event.getPayload(Order.class);
                notification.notify(order.getCustomerId(), "Your order is on the way!");
                break;
        }
    }
}

// Each service only knows about the mediator — not each other:
class InventoryServiceImpl implements InventoryService {
    @Autowired WorkflowMediator mediator;

    public void reserve(String orderId, List<OrderItem> items) {
        // ... reserve stock ...
        mediator.handle(new WorkflowEvent(INVENTORY_RESERVED, loadOrder(orderId)));
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                                                                                                                                                                                                                     |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Mediator is the same as Facade                   | Key difference: Facade is used by EXTERNAL clients to simplify access to a subsystem. Mediator is used by INTERNAL components to communicate with each other through a central coordinator. Facade: one-directional (client → facade → subsystem). Mediator: bidirectional (component A → mediator → component B → mediator → component A). |
| Mediator and Observer are interchangeable        | Both reduce coupling between communicating objects. Observer: publisher broadcasts; subscribers are decoupled from publisher; subscribers decide what to do. Mediator: central coordinator knows all components and orchestrates specific interactions. Observer: multiple independent reactions. Mediator: one coordinated response.       |
| Mediator prevents direct component communication | Mediator REDUCES the need for direct communication — it doesn't prevent it. If two components have a simple, stable relationship with no coordination complexity, direct communication may still be appropriate. Mediator addresses the "O(n²) connections" problem — don't apply it where there's no such complexity.                      |

---

### 🔥 Pitfalls in Production

**Mediator becomes a God Object — absorbs all business logic:**

```java
// ANTI-PATTERN: Mediator grows into a massive God Object:
class OrderProcessingMediator {
    void handle(Event event) {
        switch (event.getType()) {
            case ORDER_PLACED:
                // 50 lines of validation logic
                // 30 lines of inventory logic
                // 20 lines of pricing logic
                // 40 lines of fraud detection
                // 30 lines of payment orchestration
                break;
            case PAYMENT_FAILED:
                // 40 lines of retry logic
                // 20 lines of cancellation logic
                // 15 lines of notification logic
                break;
            // 20 more event types...
        }
    }
}
// Mediator now contains ALL business logic. Untestable. Single point of failure.
// Every change touches the mediator. Opposite of what the pattern should achieve.

// FIX: Mediator should COORDINATE, not IMPLEMENT:
class OrderProcessingMediator {
    void handle(Event event) {
        switch (event.getType()) {
            case ORDER_PLACED:
                Order order = event.getPayload(Order.class);
                // Delegate to specialist services — don't implement here:
                inventoryService.reserve(order);     // logic IN inventoryService
                fraudDetector.check(order);          // logic IN fraudDetector
                break;
        }
    }
}
// Mediator ROUTES and COORDINATES. Services IMPLEMENT the logic.
// Mediator becomes thin, clear, easy to understand.
```

---

### 🔗 Related Keywords

- `Observer Pattern` — subscriber model; Mediator centralizes what Observer distributes
- `Facade Pattern` — external access simplification (vs Mediator: internal coordination)
- `Event Bus Pattern` — distributed Mediator with publish/subscribe routing
- `Saga Pattern` — distributed transaction coordination using Mediator/Choreography concepts
- `CQRS` — command/event routing through mediator in distributed systems

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Central coordinator for multi-component  │
│              │ interactions. O(n²) → O(n) connections.  │
│              │ Components know only the mediator.        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Many components with complex interactions;│
│              │ GUI with tightly coordinated components;│
│              │ workflow orchestration between services  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Mediator grows into God Object;           │
│              │ simple 1-1 or 1-N relationships are fine│
│              │ without central coordinator              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Air traffic control: 50 planes → 1 tower│
│              │  instead of 1,225 plane-to-plane radio  │
│              │  channels — tower coordinates all."      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Observer Pattern → Event Bus Pattern →    │
│              │ Saga Pattern → CQRS                       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** In microservices, the "orchestration" pattern uses a central orchestrator (like a Mediator) to coordinate multi-step workflows: OrderService → orchestrator calls InventoryService → PaymentService → ShippingService. The alternative is "choreography" where services react to events without a central coordinator. Map these to patterns: orchestration = Mediator, choreography = Observer/Event-Driven. What are the tradeoffs? When does centralizing coordination (Mediator/orchestration) become a bottleneck or single point of failure?

**Q2.** MediatR is a popular .NET library that implements the Mediator pattern with in-process request/response and event notification. In Java, similar patterns appear in Spring's `ApplicationEventPublisher` and frameworks like Axon. How does the `ApplicationEventPublisher.publishEvent()` + `@EventListener` in Spring compare to the GoF Mediator pattern? Is Spring's event system more like Mediator or Observer? What's missing compared to a full Mediator implementation?
