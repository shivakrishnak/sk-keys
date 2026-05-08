---
layout: default
title: "State"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 26
permalink: /design-patterns/state/
id: DPT-026
category: Design Patterns
difficulty: ★★☆
depends_on: Object-Oriented Programming (OOP), Polymorphism, Interface, Finite State Machine
used_by: Workflow Engines, Game AI, Order Processing, UI Component Lifecycle
related: Strategy, Command, Memento, Finite State Machine
tags:
  - pattern
  - intermediate
  - architecture
  - java
  - bestpractice
---

# DPT-026 - State

⚡ TL;DR - State lets an object change its behaviour completely based on its internal state, as if the object changed its class.

| #786 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming (OOP), Polymorphism, Interface, Finite State Machine | |
| **Used by:** | Workflow Engines, Game AI, Order Processing, UI Component Lifecycle | |
| **Related:** | Strategy, Command, Memento, Finite State Machine | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An `Order` class handles the events `pay()`, `ship()`, `deliver()`, and `cancel()`. Without state-aware design, every method has a massive `if/switch` block: `if (status == PENDING) { ... } else if (status == PAID) { ... } else if (status == SHIPPED) { ...}`. Every new status requires modifying every method. With 6 statuses and 5 operations, that's 30 branches scattered across 5 methods - and every developer must mentally track which operations are valid in which status.

**THE BREAKING POINT:**
When a new `HELD_FOR_FRAUD_REVIEW` status is added, the developer must find and modify every `if` branch in every method. Missing one causes a silent logic bug: fraud-held orders might still be shipped or cancelled through the wrong code path. The state transition rules live nowhere explicitly - they're implied by the if-statement structure.

**THE INVENTION MOMENT:**
This is exactly why the State pattern was created. Each state is an object. State-specific behaviour lives in the state object, not in the context. Adding a new state means adding a new class - not modifying existing ones.

---

### 📘 Textbook Definition

The **State** pattern is a behavioural design pattern that allows an object (the **Context**) to alter its behaviour when its internal state changes. The context delegates state-specific behaviour to a **State** object that represents the current state. Each concrete state class implements the same `State` interface and defines the behaviour for every context operation in that state. Transitions between states occur by replacing the context's current state object with another concrete state instance.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An object that acts differently depending on what "mode" it is in - and each mode is its own object.

**One analogy:**
> A traffic light has three states - Red, Yellow, Green. In each state, it accepts the "next" command but does something completely different: Red → Green, Green → Yellow, Yellow → Red. The light itself (Context) doesn't change; the state object changes, and with it, the behaviour.

**One insight:**
State externalises the `if/switch` logic about "what should I do in each state?" into separate state classes. Each state class is self-contained: it knows what is valid in its state and where to transition. This makes each state independently testable and independently modifiable.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The context's behaviour must vary based on its current state.
2. State transition rules must be explicit, not implied by scattered conditionals.
3. Adding a new state must not require modifying existing states.

**DERIVED DESIGN:**
Given invariant 1+2: extract each state as an object implementing a `State` interface. Each method on the interface corresponds to an event/operation the context can receive. In `PendingState.pay()`, the logic is "transition to paid state." In `PaidState.pay()`, the logic is "throw IllegalStateException - already paid."

Given invariant 3: the Open/Closed Principle drives the design. New states are new classes; existing states need no modification as long as the interface doesn't change.

The context holds a `State currentState` field. All client calls to `context.pay()` delegate to `currentState.pay(context)`. The context itself becomes thin - it only routes calls to the current state.

**THE TRADE-OFFS:**
**Gain:** Eliminates conditional complexity; state transition rules centralised in each state class; each state independently testable; adding states without modifying context.
**Cost:** More classes (one per state); transitions expressed across multiple classes (harder to see the full state machine in one place); context and state must have a reference relationship.

---

### 🧪 Thought Experiment

**SETUP:**
An ATM card reader has states: Idle, CardInserted, PINEntered, TransactionComplete. When `insertCard()` is called in Idle state it's valid; when called in CardInserted state it's invalid (card already in).

**WHAT HAPPENS WITHOUT STATE:**
`ATM.insertCard()` checks `if (state == IDLE) { accept card } else { reject }`. `ATM.enterPIN()` checks `if (state == CARD_INSERTED) { verify } else if (state == IDLE) { reject } else ...`. Every method has all state branches. With 6 operations and 4 states, that's 24 branches - and devs must keep all combinations in their heads.

**WHAT HAPPENS WITH STATE:**
`IdleState.insertCard(atm)` → transitions context to `CardInsertedState`. `CardInsertedState.insertCard(atm)` → "Card already inserted - reject." Each state handles only what's valid for it. Invalid operations in a state either throw or are no-ops - one small method, one clear path.

**THE INSIGHT:**
State makes invalid transitions explicit at compile time (sort of) and runtime certainly - each state class only implements what it allows. You can read a single state class and understand everything about that state.

---

### 🧠 Mental Model / Analogy

> State is like a water molecule. Water (the Context) is always the same molecule - H₂O. But in Ice state it's rigid and solid; in Liquid state it flows; in Gas state it expands freely. The same molecule behaves completely differently based on its state. You don't change the molecule; you change the state object attached to it.

- "Water molecule" → Context object
- "Ice / Liquid / Gas" → concrete State objects (IceState, LiquidState, GasState)
- "Temperature change" → event that triggers a state transition
- "Rigid / flowing / expanding" → state-specific behaviour in each State class
- "Transition: liquid to gas" → context.setState(new GasState())

Where this analogy breaks down: in chemistry, state transitions are immediate. In software, a state transition can be deferred, conditional, or triggered by the state itself after completing its work - adding logic the water analogy doesn't capture.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
State is a pattern where an object's behaviour is completely different depending on what "mode" it's in. Instead of writing `if (mode == X) do A else if (mode == Y) do B`, each mode is a separate class with its own implementation.

**Level 2 - How to use it (junior developer):**
Create a `State` interface with methods for each event the context can receive. Create one concrete state class per state - each implements the interface. In each method: do the state-specific logic, then potentially call `context.setState(new NextState())` to transition. The `Context` class holds `private State currentState` and delegates each operation to `currentState.method(this)`. Pass `this` (context) to state methods so states can transition the context.

**Level 3 - How it works (mid-level engineer):**
The state-context coupling is bidirectional: the context holds the state (`context.setState(state)`), and state methods receive the context to trigger transitions (`state.pay(context)`). Avoid storing state in both the context and the state - single source of truth. State objects can be shared (stateless state objects) if they hold no mutable data: a single `PaidState` instance can be reused by thousands of `Order` contexts simultaneously. Spring's state machine (`spring-statemachine`) provides a framework-level implementation with event-driven transitions, guards, and actions mapped to the State pattern.

**Level 4 - Why it was designed this way (senior/staff):**
State is the OOP encoding of a Finite State Machine (FSM). FSMs formalise state, transitions, guards, and actions - State implements this in class hierarchies. The GoF pattern does not enforce that all states are reachable from initial state or that the state graph has no dead ends - these are correctness properties the designer must ensure. In production state machines (order processing, payment workflows), illegal state transitions are often the most critical bugs: an order that reaches Shipped without being Paid. The State pattern makes this visible at the class level - `ShippedState.pay()` can throw `IllegalStateException("Cannot pay a shipped order")` - but only if all callers route through the context's delegate methods and no one keeps a direct reference to the state.

---

### ⚙️ How It Works (Mechanism)

```
┌───────────────────────────────────────────────┐
│  STATE PATTERN - ORDER LIFECYCLE              │
│                                               │
│  Context: Order                               │
│  ┌─────────────────────────────┐              │
│  │ currentState: OrderState    │              │
│  │                             │              │
│  │ pay()   → state.pay(this)   │              │
│  │ ship()  → state.ship(this)  │              │
│  │ cancel()→ state.cancel(this)│              │
│  └─────────────────────────────┘              │
│                                               │
│  State Transitions:                           │
│                                               │
│  [PENDING] ──pay()──→ [PAID]                 │
│     │                    │                   │
│  cancel()            ship()                  │
│     ↓                    ↓                   │
│  [CANCELLED]         [SHIPPED]               │
│                          │                   │
│                      deliver()               │
│                          ↓                   │
│                      [DELIVERED]             │
└───────────────────────────────────────────────┘
```

**State method call flow:**
1. Client calls `order.pay()`
2. Context delegates: `currentState.pay(this)`
3. `PendingState.pay(order)`:
   - validates (e.g., payment confirmed)
   - calls `order.setState(new PaidState())`
4. `order.currentState` is now `PaidState`
5. Next call to `order.pay()` → `PaidState.pay(order)` → throws "Already paid"
6. `order.ship()` → `PaidState.ship(order)` → transitions to ShippedState

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
HTTP POST /orders/{id}/pay
  → OrderController.payOrder(id)
  → orderService.pay(order)
  → order.pay()
       ← YOU ARE HERE (State pattern)
  → currentState.pay(order)
       if PendingState: transitions → PaidState
       if PaidState: throws AlreadyPaidException
  → order saved with new state
  → HTTP 200 returned
```

**FAILURE PATH:**
```
order.ship() called on CANCELLED order
  → CancelledState.ship(order)
  → throw IllegalStateOrderTransitionException(
      "Cannot ship a cancelled order")
  → OrderController catches → 409 Conflict
  → client receives: 
      {"error": "Invalid state transition"}
```

**WHAT CHANGES AT SCALE:**
In distributed systems, the Order's state may be stored in a database. Two concurrent requests to pay the same order (double-click scenario) can both read `PENDING` and both attempt to transition to `PAID`. The State pattern alone does not prevent this - an optimistic locking or distributed lock mechanism must guard the state transition at the persistence layer.

---

### 💻 Code Example

**Example 1 - Order state machine:**
```java
// State interface
public interface OrderState {
    void pay(Order order);
    void ship(Order order);
    void deliver(Order order);
    void cancel(Order order);
}

// Concrete states
public class PendingState implements OrderState {
    @Override
    public void pay(Order order) {
        System.out.println("Payment received");
        order.setState(new PaidState());
    }
    @Override
    public void ship(Order order) {
        throw new IllegalStateException(
            "Cannot ship unpaid order");
    }
    @Override
    public void deliver(Order order) {
        throw new IllegalStateException(
            "Cannot deliver unpaid order");
    }
    @Override
    public void cancel(Order order) {
        order.setState(new CancelledState());
    }
}

public class PaidState implements OrderState {
    @Override
    public void pay(Order order) {
        throw new IllegalStateException("Already paid");
    }
    @Override
    public void ship(Order order) {
        System.out.println("Order shipped");
        order.setState(new ShippedState());
    }
    @Override
    public void deliver(Order order) {
        throw new IllegalStateException(
            "Cannot deliver - not yet shipped");
    }
    @Override
    public void cancel(Order order) {
        System.out.println("Refund initiated");
        order.setState(new CancelledState());
    }
}

// Context
public class Order {
    private OrderState currentState = new PendingState();

    public void setState(OrderState state) {
        this.currentState = state;
    }

    public void pay()    { currentState.pay(this); }
    public void ship()   { currentState.ship(this); }
    public void deliver(){ currentState.deliver(this); }
    public void cancel() { currentState.cancel(this); }
}

// Usage
Order order = new Order();
order.pay();     // "Payment received"
order.ship();    // "Order shipped"
order.pay();     // throws: "Already paid"
```

---

### ⚖️ Comparison Table

| Approach | Transition Logic Lives In | New State Requires | Complexity |
|---|---|---|---|
| **State Pattern** | Each state class | New class | Medium |
| if/switch in context | Context methods | Modify all methods | Low initially, high later |
| Enum + switch | Enum constants | Extend enum | Low |
| Spring State Machine | Config / DSL | Config changes | High setup, low runtime |
| Workflow engine (Camunda) | BPMN diagram | Model change | High |

How to choose: use State pattern when states are few (3–10) and transitions are complex. Use a workflow engine when transitions involve external approvals, timers, or human tasks.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| State and Strategy are the same | State manages object lifecycle transitions with implicit switching; Strategy selects algorithm at creation time with no switching. State transitions itself; Strategy is replaced by external code |
| State pattern eliminates all conditionals | It relocates them. Each state class may still have conditionals inside its methods; the pattern eliminates the top-level state-dispatch switch |
| State objects must be stateless | State objects CAN hold data relevant to their state phase (e.g., payment retry count in PendingState). They don't have to be singletons |
| State transitions must happen only in state classes | Transitions can also happen in the Context or in a separate TransitionManager - but centralising them in state classes is the canonical approach |
| Every method must throw an exception for invalid operations | Invalid operations can be no-ops instead of exceptions; the right choice depends on whether the caller can detect and handle the invalid call |

---

### 🚨 Failure Modes & Diagnosis

**1. Concurrent State Transition Race Condition**

**Symptom:** An order appears in both PAID and CANCELLED state simultaneously. Database has a row with status=CANCELLED but payment gateway recorded a successful charge.

**Root Cause:** Two threads read `PendingState`, both call `pay()`, both transition to `PaidState`, then one cancels. The in-memory State pattern has no atomicity guarantee across threads.

**Diagnostic:**
```sql
-- Detect inconsistent state in DB
SELECT id, status, payment_status, updated_at
FROM orders
WHERE status = 'CANCELLED'
  AND payment_status = 'CHARGED';
-- Any results = race condition occurred
```

**Fix:**
```java
// Add optimistic locking at persistence layer
@Entity
public class Order {
    @Version
    private Long version; // DB-level optimistic lock

    // State transitions go through repository.save()
    // If two threads save simultaneously: one gets
    // OptimisticLockingFailureException
}
```

**Prevention:** State transitions persisted to a database must use optimistic or pessimistic locking. In-memory State pattern alone is not sufficient for concurrent state management.

---

**2. State Transition Without Persisting**

**Symptom:** After a server restart, orders return to their previous state. State changes appeared to work but were not saved.

**Root Cause:** State objects are in-memory. `order.pay()` transitions to `PaidState` but `orderRepository.save(order)` is not called after the transition in the service layer.

**Diagnostic:**
```bash
# Check if state transitions appear in DB audit log
SELECT * FROM order_audit_log
WHERE order_id = 12345
ORDER BY created_at DESC LIMIT 10;
# If no record for pay() transition: save was missing
```

**Fix:**
```java
// Service method must save after transition
public void payOrder(Long orderId) {
    Order order = orderRepo.findById(orderId);
    order.pay();               // transitions state
    orderRepo.save(order);     // MUST persist new state
    // or use @Transactional + JPA dirty checking
}
```

**Prevention:** Wrap all state transition service methods in `@Transactional`. Use database-persisted state that maps directly to the domain's `currentState`.

---

**3. Invalid State Reached - Missing Guard on Transition**

**Symptom:** A DELIVERED order transitions to SHIPPED (backwards). Display shows contradictory history.

**Root Cause:** `DeliveredState.ship()` was not implemented (or defaults to no-op) instead of throwing an exception. Code path executed the ship request on a delivered order silently.

**Diagnostic:**
```bash
# Find orders in inconsistent state sequence
SELECT id FROM order_status_history
WHERE 1=1
GROUP BY order_id
HAVING MAX(CASE WHEN status='SHIPPED' THEN created_at END) >
       MAX(CASE WHEN status='DELIVERED' THEN created_at END);
```

**Fix:**
```java
// Default implementation that guards all operations:
public class DeliveredState implements OrderState {
    @Override
    public void ship(Order order) {
        // Terminal state: no transitions allowed
        throw new IllegalStateException(
            "Order already delivered - terminal state");
    }
    // Similar for pay(), cancel()
}
```

**Prevention:** Terminal states should throw on all transition attempts. Add unit tests for every invalid transition in every state.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Polymorphism` - State leverages polymorphism to dispatch behaviour to the current state object automatically via the common interface
- `Interface` - the State interface is the contract that all concrete states implement; without it the Context cannot delegate uniformly
- `Finite State Machine` - State pattern is the OOP encoding of an FSM; understanding FSM theory helps design correct state graphs

**Builds On This (learn these next):**
- `Workflow Engines (Camunda, Temporal)` - production-grade state machines for long-running business processes with persistence, timers, and human tasks
- `Spring State Machine` - Spring's framework for State pattern with event-driven transitions, guards, and actions
- `Event Sourcing Pattern` - stores every state transition as an event; the current state is derived by replaying events

**Alternatives / Comparisons:**
- `Strategy` - both use polymorphism to change behaviour, but Strategy is chosen externally and doesn't manage transitions; State manages its own transitions
- `Command` - encapsulates an operation as an object; can trigger state transitions when combined with State
- `Memento` - captures state for rollback; can be combined with State to undo transitions

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Behaviour-switching via swappable state   │
│              │ objects instead of if/switch chains       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Behaviour differs per state; if/switch    │
│ SOLVES       │ chains grow unboundedly with new states   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Each state IS a class - transitions are   │
│              │ method calls that swap the state object   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Object behaviour changes significantly    │
│              │ based on its current state (3+ states)    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Only 2 boolean states - simpler           │
│              │ conditionals or a flag suffice            │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Elimination of if/switch vs more classes  │
│              │ and distributed transition logic          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Each state owns its own behaviour -      │
│              │  the context just passes through."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Spring State Machine → Workflow Engine →  │
│              │ Event Sourcing Pattern                    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An `Order` starts in PENDING state. Five concurrent HTTP requests all call `order.pay()` simultaneously on the same order in a Spring application. The State pattern is implemented correctly in memory with `CopyOnWriteArrayList` for thread safety. Describe exactly what can happen, why the State pattern alone is insufficient, and what exactly needs to happen at the database layer to make this correct.

**Q2.** The State pattern distributes state transition logic across many classes - `PendingState` knows it transitions to `PaidState`, and `PaidState` knows it transitions to `ShippedState`. A product manager asks: "Can I see the entire state machine in one diagram from reading the code?" Currently the answer is no. Design an alternative State pattern variant (using a different structure, not a different pattern) that makes the full state machine visible in one place, while keeping each state's behaviour in its own class.

