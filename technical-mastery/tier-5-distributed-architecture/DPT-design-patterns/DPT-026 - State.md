---
id: DPT-026
title: State
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-005, DPT-027
used_by: DPT-064, DPT-065
related: DPT-027, DPT-025, DPT-024
tags:
  - pattern
  - behavioral
  - intermediate
  - state-machine
  - workflow
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 26
permalink: /technical-mastery/design-patterns/state/
---

⚡ TL;DR - State allows an object to alter its behavior
when its internal state changes by representing each
state as a class - replacing monolithic if/else chains
with polymorphic state transitions.

| #26 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-027 | |
| **Used by:** | DPT-064, DPT-065 | |
| **Related:** | DPT-027, DPT-025, DPT-024 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An order has states: `NEW`, `PAID`, `SHIPPED`, `DELIVERED`,
`CANCELLED`. Every method (`cancel()`, `ship()`, `return()`)
has a giant if/else:

```java
void cancel() {
    if (state == NEW) { ... }
    else if (state == PAID) { refund(); state = CANCELLED; }
    else if (state == SHIPPED) { ... }
    else if (state == DELIVERED)
        throw new IllegalStateException("Cannot cancel delivered");
    else if (state == CANCELLED)
        throw new IllegalStateException("Already cancelled");
}
```

**THE BREAKING POINT:**
5 states × 5 methods = 25 if/else blocks. Adding a new
state (`PARTIALLY_SHIPPED`) requires modifying all 5
methods. A bug where `SHIPPED` → `PAID` transition is
accidentally allowed is buried inside 250 lines of
if/else. The state machine logic is unreadable.

**THE INVENTION MOMENT:**
State: each state becomes a class implementing an `OrderState`
interface with `cancel()`, `ship()`, `deliver()`.
`PaidState.cancel()` refunds and transitions to Cancelled.
`ShippedState.cancel()` throws. `Order.cancel()` delegates
to `currentState.cancel(this)`. Each state class handles
its own valid transitions. Adding a new state: add a class;
do not modify existing states.

**EVOLUTION:**
Spring State Machine, Akka FSM, XState (JavaScript) are
all State pattern implementations. TCP protocol states,
vending machine behavior, traffic light logic, and
workflow engines all use the State pattern. Every process
with distinct phases (lifecycle states) where valid
operations depend on the current phase is a State pattern
candidate.

---

### 📘 Textbook Definition

The **State** pattern is a Behavioral design pattern that
allows an object (Context) to alter its behavior when its
internal state changes - the object will appear to change
its class. Each state is represented as a class implementing
a common State interface. The Context delegates all state-
dependent behavior to the current State object. State
transitions are triggered either by the Context or by the
State objects themselves.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
State replaces "if (state == X) do A else if (state == Y)
do B" with polymorphic state objects that each know what
they can do.

**One analogy:**
> A traffic light has three states: RED, YELLOW, GREEN.
> Each state knows one thing: what comes next and how long
> to wait. `RedState.next()` returns `GreenState`. No
> traffic controller needs to check "if currently red then
> switch to green" - each state manages its own transition.

**One insight:**
State and Strategy have identical structure: a context
with a swappable behavior object. The INTENT differs:
Strategy selects an algorithm that DOESN'T change the
context's identity. State manages transitions that
DEFINE the context's current identity.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The Context delegates all state-specific operations
   to the current State object.
2. State transitions are explicit: a state sets the
   Context's current state in response to events.
3. Each state knows what transitions are valid from it;
   invalid transitions throw or are ignored.

**DERIVED DESIGN:**
Two key participants:
- **Context**: holds a reference to the current State.
  Forwards requests to the State. Provides a `setState()`
  method for transitions.
- **State interface**: defines all state-dependent operations.
  One method per event/action.
- **ConcreteState**: implements State; each state class
  handles the events that are valid in that state; transitions
  to the next state by calling `context.setState(nextState)`.

**STATE TRANSITION:**
```
Transition authority options:
1. State transitions itself: PaidState.ship() →
  context.setState(new ShippedState())
2. Context transitions based on state return value
Both are valid; option 1 is more common in GoF
```

**TRADE-OFFS:**

**Gain:** Each state class is small and single-responsibility.
Valid transitions are explicit. Adding states is closed
(does not require changing existing states in most cases).
State logic is testable in isolation.

**Cost:** Class proliferation (one class per state).
Transitions distributed across state classes can be harder
to see the full state machine at a glance. State objects
that need to share data from the Context can create
coupling.

---

### 🧪 Thought Experiment

**SETUP:**
A document has states: `DRAFT`, `REVIEW`, `APPROVED`,
`PUBLISHED`. A `publish()` method should: work from
APPROVED, do nothing from PUBLISHED, and throw from
DRAFT and REVIEW.

**WITHOUT STATE PATTERN:**
```java
void publish() {
    switch (state) {
        case DRAFT: throw new IllegalStateException();
        case REVIEW: throw new IllegalStateException();
        case APPROVED: state = PUBLISHED; notifyAll(); break;
        case PUBLISHED: /* do nothing */ break;
    }
}
```

**WITH STATE PATTERN:**
- `DraftState.publish()` → throws `IllegalStateException`
- `ReviewState.publish()` → throws `IllegalStateException`
- `ApprovedState.publish()` → transitions to PublishedState,
  calls notifyAll()
- `PublishedState.publish()` → no-op

Each state class is 3-5 lines. The full state machine
behavior is distributed but explicit.

---

### 🧠 Mental Model / Analogy

> State is a VENDING MACHINE. The machine has states:
> IDLE, HAS_MONEY, DISPENSING. In IDLE: "select product"
> is ignored; "insert coin" moves to HAS_MONEY.
> In HAS_MONEY: "insert more coin" increases balance;
> "select product" → if balance sufficient → DISPENSING.
> In DISPENSING: dispense item, return change, go back to IDLE.
> Each state knows its own valid actions and next states.
> The machine's `handleCoin()` and `selectProduct()` just
> delegate to `currentState.handleCoin()` and
> `currentState.selectProduct()`.

- "Vending machine" = Context
- "IDLE / HAS_MONEY / DISPENSING" = ConcreteState classes
- "currentState" = state reference in Context
- "Transition to next state" = state calls context.setState()

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
State makes each "phase" of an object's life a separate
class. The object's behavior changes automatically when
it moves to a different phase, because it is now using
a different state class.

**Level 2 - How to use it (junior developer):**
Enumerate all states. Create a `State` interface with
all event-handling methods. Create one class per state.
In the Context: delegate all state-dependent methods to
`currentState.method(this)`. Each state handles events
valid in that state, transitions the context for valid
next states, and throws for invalid events.

**Level 3 - How it works (mid-level engineer):**
Java's `Thread` lifecycle is a State machine: NEW,
RUNNABLE, BLOCKED, WAITING, TIMED_WAITING, TERMINATED.
`Thread.start()` is valid only from NEW; calling it
from RUNNABLE throws `IllegalThreadStateException`.
Java's internal thread state management uses if/else
(not the GoF pattern), but the STATE machine design
is the same conceptual model. Spring's StateMachine
project implements the GoF State pattern for enterprise
workflows.

**Level 4 - Why it was designed this way (senior/staff):**
State pattern implements the Open/Closed Principle for
state machines: adding a new state adds a new class;
existing state classes are CLOSED for modification
(unless the new state requires transitions from existing
states). This is powerful for evolving domain models:
an order that adds `PARTIALLY_SHIPPED` state requires
only adding `PartiallyShippedState` and updating the
states that can transition to it (PAID, NEW). The
monolithic if/else approach requires modifying every
method in the Order class.

**Level 5 - Mastery (distinguished engineer):**
Event-sourced domain models combine State pattern with
event sourcing. Each domain event triggers a state
transition: `OrderPlacedEvent` → `PaidState`. The aggregate
root maintains a `State` reference; events call `apply(event)`
which calls `currentState.apply(event, this)`. The state
handles the event and transitions. To reconstruct current
state: replay all events from the event log; each event
re-applies its state transition. State and Event Sourcing
create a fully auditable, replayable state machine -
the ideal model for financial and regulatory domain objects.

---

### ⚙️ How It Works (Mechanism)

```
State Pattern for Order
┌─────────────────────────────────────────────────────────┐
│ <<interface>> OrderState                                │
│   + cancel(Order ctx): void                             │
│   + ship(Order ctx): void                               │
│   + deliver(Order ctx): void                            │
│                                                         │
│ NewState implements OrderState                          │
│   + cancel(ctx): ctx.setState(CANCELLED); ctx.deleteItem│
│   + ship(ctx): throw InvalidTransition("pay first")     │
│   + deliver(ctx): throw InvalidTransition               │
│                                                         │
│ PaidState implements OrderState                         │
│   + cancel(ctx): ctx.refundPayment(); ctx.setState(CANCE│
│   + ship(ctx): ctx.notifyWarehouse(); ctx.setState(SHIPP│
│   + deliver(ctx): throw InvalidTransition               │
│                                                         │
│ ShippedState implements OrderState                      │
│   + cancel(ctx): throw InvalidTransition("already shippe│
│   + ship(ctx): throw InvalidTransition("already shipped"│
│   + deliver(ctx): ctx.notifyCustomer(); ctx.setState(DEL│
│                                                         │
│ Order (Context)                                         │
│   - state: OrderState = new NewState()                  │
│   + cancel(): state.cancel(this)                        │
│   + ship(): state.ship(this)                            │
│   + setState(s): this.state = s                         │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Order created: state = NewState
order.ship(): NewState.ship() → throw "Pay first"

Customer pays: state = PaidState
order.ship(): PaidState.ship()
  → ctx.notifyWarehouse()
  → ctx.setState(ShippedState)
  state = ShippedState

Customer receives: order.deliver()
  ShippedState.deliver()
  → ctx.notifyCustomer()
  → ctx.setState(DeliveredState)
  state = DeliveredState

order.cancel(): DeliveredState.cancel()
  → throw InvalidTransition("Cannot cancel delivered
    order")
```

---

### 💻 Code Example

**Example 1 - Without State (if/else explosion):**

```java
// BAD: monolithic state handling in every method
class Order {
    enum Status { NEW, PAID, SHIPPED, DELIVERED, CANCELLED }
    private Status status = Status.NEW;

    public void ship() {
        if (status == Status.PAID) {
            notifyWarehouse();
            status = Status.SHIPPED;
        } else if (status == Status.SHIPPED) {
            throw new IllegalStateException("Already shipped");
        } else if (status == Status.DELIVERED) {
            throw new IllegalStateException("Already delivered");
        } else {
            throw new IllegalStateException(
                "Cannot ship from: " + status);
        }
        // Same pattern in cancel(), deliver(), process()...
        // 5 states x 4 methods = 20 switch cases
    }
}
```

**Example 2 - State pattern:**

```java
// GOOD: each state handles its own transitions

interface OrderState {
    void pay(Order order);
    void ship(Order order);
    void deliver(Order order);
    void cancel(Order order);
}

class NewOrderState implements OrderState {
    @Override
    public void pay(Order order) {
        order.processPayment();
        order.setState(new PaidOrderState());
    }

    @Override
    public void ship(Order order) {
        throw new InvalidOrderTransitionException(
            "Must pay before shipping");
    }

    @Override
    public void deliver(Order order) {
        throw new InvalidOrderTransitionException(
            "Must ship before delivering");
    }

    @Override
    public void cancel(Order order) {
        order.setState(new CancelledOrderState());
    }
}

class PaidOrderState implements OrderState {
    @Override
    public void pay(Order order) {
        throw new InvalidOrderTransitionException(
            "Order already paid");
    }

    @Override
    public void ship(Order order) {
        order.notifyWarehouse();
        order.setState(new ShippedOrderState());
    }

    @Override
    public void deliver(Order order) {
        throw new InvalidOrderTransitionException(
            "Must ship before delivering");
    }

    @Override
    public void cancel(Order order) {
        order.refundPayment();
        order.setState(new CancelledOrderState());
    }
}

// Context: delegates all behavior to current state
class Order {
    private OrderState state = new NewOrderState();
    private String id;

    void pay() { state.pay(this); }
    void ship() { state.ship(this); }
    void deliver() { state.deliver(this); }
    void cancel() { state.cancel(this); }

    // Package-accessible for state transitions
    void setState(OrderState newState) {
        this.state = newState;
    }

    // Business actions called by states
    void processPayment() { /* ... */ }
    void notifyWarehouse() { /* ... */ }
    void refundPayment() { /* ... */ }
    void notifyCustomer() { /* ... */ }
}
```

**How to test/verify correctness:**
Test each State class independently: mock the Context,
verify the correct Context methods are called and the
correct `setState()` is triggered. Test invalid transition
throws. Integration test: walk a full state machine path
(NEW → PAID → SHIPPED → DELIVERED) and verify each transition.

---

### ⚖️ Comparison Table

| Pattern | Behavior changes | Algorithm selection | State transition | When to use |
|---|---|---|---|---|
| **State** | Based on lifecycle state | No | By state itself | Object has lifecycle phases |
| Strategy | Based on client choice | Yes | By client | Algorithm is interchangeable |
| Command | Per request | One per request | N/A | Request as object |

**State vs Strategy:**
Same structure (context + interchangeable behavior object).
Different intent:
- State: the object IS in a state; transitions happen as
  part of the domain lifecycle.
- Strategy: the client SELECTS an algorithm to apply;
  no lifecycle transitions; algorithm is interchangeable.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| State and Strategy are the same | Same structure, different intent. State: object transitions through lifecycle phases; each state causes the next. Strategy: client selects one algorithm from available options at any time; no lifecycle |
| State pattern is the same as a switch/case | Switch/case IS what State replaces. Switch/case scales poorly (all cases in one method, in one class). State distributes logic to individual classes - Open/Closed for adding states |
| All state changes need State pattern | For 2-3 simple states with only 1-2 state-dependent methods: a simple enum + switch is cleaner. State pattern is justified when: 4+ states OR 3+ methods vary by state OR state machine logic is complex |
| State objects should be singletons | State objects CAN be singletons (stateless state objects) or instantiated per-context. If state objects store per-context data (e.g., retry count), they must be per-context. If purely polymorphic behavior: singletons reduce allocation |

---

### 🚨 Failure Modes & Diagnosis

**Invalid State Transition Allowed (Missing Guard)**

**Symptom:**
An order is `DELIVERED` but `order.ship()` is called
and executes (re-ships an already delivered order).
Double shipping occurs.

**Root Cause:**
`DeliveredState.ship()` is not implemented or is silently
ignored (returns without action or throwing).

**Fix:**
Every state must explicitly handle every event:
either perform the valid transition, or throw
`InvalidOrderTransitionException`. Never silently ignore.

```java
// BAD: silent no-op in DeliveredState
class DeliveredState implements OrderState {
    @Override
    public void ship(Order order) {
        // empty - silently ignored - WRONG
    }
}

// GOOD: explicit rejection
class DeliveredState implements OrderState {
    @Override
    public void ship(Order order) {
        throw new InvalidOrderTransitionException(
            "Cannot ship an already delivered order");
    }
}
```

**Prevention:**
Use an abstract base state class that throws by default
for all events. Concrete states override only the events
they handle. Unhandled events automatically throw.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Strategy` - DPT-027; the structural twin of State;
  understanding Strategy first makes the intent distinction
  clear

**Builds On This (learn these next):**
- `Memento` - DPT-024; Memento can capture State machine
  snapshots for undo/rollback of state transitions

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Each lifecycle state = a class;          │
│              │ Context delegates to currentState        │
├──────────────┼──────────────────────────────────────────┤
│ KEY BENEFIT  │ Replacing if/else state chains with      │
│              │ polymorphic state classes (OCP)          │
├──────────────┼──────────────────────────────────────────┤
│ KEY RULE     │ Every state must handle every event:     │
│              │ valid transition OR explicit rejection   │
├──────────────┼──────────────────────────────────────────┤
│ VS STRATEGY  │ State: lifecycle transitions; object IS  │
│              │ in a state. Strategy: algorithm selected │
│              │ by client; no lifecycle progression     │
├──────────────┼──────────────────────────────────────────┤
│ FAILURE MODE │ Silent no-op on invalid transition       │
│              │ → invalid operations silently succeed    │
├──────────────┼──────────────────────────────────────────┤
│ WHEN TO USE  │ 4+ states with 3+ state-dependent methods│
│              │ (simpler cases: enum + switch is fine)   │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Strategy → Template Method → Visitor     │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. State replaces if/else chains with polymorphic state
   classes - each state handles what's valid in that state,
   throws for invalid transitions; adding a state = adding
   a class, not modifying existing methods
2. State vs Strategy: same structure, different intent.
   State = lifecycle phases (object TRANSITIONS). Strategy
   = algorithm selection (client CHOOSES). Ask: "does the
   context progress through states?" → State. "Does the
   client select an algorithm?" → Strategy.
3. Every state must handle every event explicitly (process
   or throw) - silent no-ops cause invalid transitions
   to silently succeed

**Interview one-liner:**
"State represents lifecycle phases as classes, replacing
if/else chains with polymorphic state objects. Each state
handles valid operations and throws on invalid transitions.
State and Strategy have the same structure but different
intent: State manages lifecycle progression; Strategy allows
algorithm selection. The rule: every state must handle
every event explicitly - silent no-ops allow invalid
state machine transitions."

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [DISTINGUISH] In one sentence, explain the difference
   between State and Strategy pattern intent - use a
   concrete example for each
2. [IMPLEMENT] Build a 3-state order machine (NEW, PAID,
   CANCELLED) using the State pattern - ensure invalid
   transitions throw explicitly
3. [DIAGNOSE] Given an order state machine where `ship()`
   on a DELIVERED order silently succeeds, identify the
   missing guard and fix it
4. [EVALUATE] Given a system with 2 states and 1 state-
   dependent method, decide whether State pattern or
   an enum + if/else is more appropriate and justify

