---
layout: default
title: "State Pattern"
parent: "Design Patterns"
nav_order: 784
permalink: /design-patterns/state-pattern/
number: "784"
category: Design Patterns
difficulty: ★★★
depends_on: "Object-Oriented Programming, Strategy Pattern, Finite State Machine"
used_by: "Order lifecycle, Traffic lights, TCP connections, Game AI, UI components"
tags: #advanced, #design-patterns, #behavioral, #oop, #state-machine, #fsm
---

# 784 — State Pattern

`#advanced` `#design-patterns` `#behavioral` `#oop` `#state-machine` `#fsm`

⚡ TL;DR — **State** allows an object to alter its behavior when its internal state changes — eliminating large `if/switch` blocks by representing each state as a class, so the object appears to change its class as its state changes.

| #784 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming, Strategy Pattern, Finite State Machine | |
| **Used by:** | Order lifecycle, Traffic lights, TCP connections, Game AI, UI components | |

---

### 📘 Textbook Definition

**State** (GoF, 1994): a behavioral design pattern that allows an object to alter its behavior when its internal state changes. The object will appear to change its class. Implements a state machine where: each state is a class implementing a State interface; the Context (the object that changes behavior) holds a reference to the current state object and delegates behavior to it; state objects transition the context to new states. GoF intent: "Allow an object to alter its behavior when its internal state changes. The object will appear to change its class." Eliminates complex `if/switch` on state enum throughout the code. Distinguished from Strategy: Strategy's algorithm is injected from outside (policy). State transitions happen internally (state object sets context's state to the next state).

---

### 🟢 Simple Definition (Easy)

A traffic light. Three states: Red, Yellow, Green. Each state knows: (1) what to display (the state's behavior), and (2) what state comes next when the timer fires. You don't need: `if (currentState == RED) { display = "STOP"; nextState = GREEN; }` etc. Instead: `RedState.display()` → shows "STOP". `RedState.timerFired()` → transitions to GreenState. `GreenState.timerFired()` → transitions to YellowState. The traffic light just calls `currentState.timerFired()` — the state decides what happens.

---

### 🔵 Simple Definition (Elaborated)

An order lifecycle: PENDING → CONFIRMED → SHIPPED → DELIVERED or CANCELLED. Without State: `if (order.getStatus() == PENDING) { confirmOrder(); } else if (status == CONFIRMED) { shipOrder(); }` — scattered throughout the codebase. With State: each status is a state class. `PendingState.confirm()` → sets state to ConfirmedState, validates. `PendingState.cancel()` → sets state to CancelledState. `ShippedState.confirm()` → throws: "Can't confirm a shipped order." All state-specific behavior encapsulated in state classes. Context (`Order`) just delegates to current state.

---

### 🔩 First Principles Explanation

**How state classes eliminate switch/if and enforce valid transitions:**

```
WITHOUT STATE PATTERN — SCATTERED IF/SWITCH:

  class Order {
      OrderStatus status;
      
      void confirm() {
          if (status == PENDING) {
              status = CONFIRMED;
          } else if (status == CONFIRMED) {
              throw new IllegalStateException("Already confirmed");
          } else if (status == SHIPPED) {
              throw new IllegalStateException("Cannot confirm shipped order");
          } else if (status == CANCELLED) {
              throw new IllegalStateException("Cannot confirm cancelled order");
          }
      }
      
      void ship() {
          if (status == CONFIRMED) { status = SHIPPED; }
          else if (status == PENDING) { throw new ISE("Must confirm first"); }
          // ... same switch for every method
      }
      
      void cancel() { ... same switch again ... }
  }
  
  // 4 states × 3 operations = 12 cases to handle.
  // Add a new state (REFUNDED) → modify ALL methods.
  
WITH STATE PATTERN:

  // STATE INTERFACE:
  interface OrderState {
      void confirm(Order order);
      void ship(Order order);
      void cancel(Order order);
      String getDescription();
  }
  
  // CONCRETE STATES:
  class PendingState implements OrderState {
      @Override
      void confirm(Order order) {
          // Validation:
          if (order.getTotal().compareTo(BigDecimal.ZERO) == 0)
              throw new IllegalStateException("Cannot confirm empty order");
          
          order.setState(new ConfirmedState());    // transition!
          order.setConfirmedAt(Instant.now());
      }
      
      @Override
      void ship(Order order) {
          throw new IllegalStateException("Must confirm before shipping");
      }
      
      @Override
      void cancel(Order order) {
          order.setState(new CancelledState());    // cancel is valid from Pending
          order.setCancelledAt(Instant.now());
      }
      
      @Override
      String getDescription() { return "PENDING: awaiting confirmation"; }
  }
  
  class ConfirmedState implements OrderState {
      @Override
      void confirm(Order order) {
          throw new IllegalStateException("Already confirmed");
      }
      
      @Override
      void ship(Order order) {
          order.setState(new ShippedState());    // transition
          order.setShippedAt(Instant.now());
      }
      
      @Override
      void cancel(Order order) {
          order.setState(new CancelledState());    // cancel still valid from Confirmed
          // May need to refund payment
      }
      
      @Override
      String getDescription() { return "CONFIRMED: processing"; }
  }
  
  class ShippedState implements OrderState {
      @Override
      void confirm(Order order) {
          throw new IllegalStateException("Order already shipped");
      }
      
      @Override
      void ship(Order order) {
          throw new IllegalStateException("Order already shipped");
      }
      
      @Override
      void cancel(Order order) {
          throw new IllegalStateException("Cannot cancel shipped order — contact support");
      }
      
      @Override
      String getDescription() { return "SHIPPED: in transit"; }
  }
  
  class CancelledState implements OrderState {
      @Override
      void confirm(Order order) {
          throw new IllegalStateException("Order was cancelled");
      }
      @Override
      void ship(Order order) {
          throw new IllegalStateException("Order was cancelled");
      }
      @Override
      void cancel(Order order) {
          // no-op or throw — already cancelled
      }
      @Override
      String getDescription() { return "CANCELLED"; }
  }
  
  // CONTEXT:
  class Order {
      private OrderState state;
      private BigDecimal total;
      
      Order(BigDecimal total) {
          this.state = new PendingState();   // initial state
          this.total = total;
      }
      
      void confirm() { state.confirm(this); }   // delegate to current state
      void ship()    { state.ship(this); }
      void cancel()  { state.cancel(this); }
      
      void setState(OrderState state) { this.state = state; }
      String getDescription()         { return state.getDescription(); }
  }
  
  // Client:
  Order order = new Order(new BigDecimal("99.00"));
  order.confirm();  // PendingState.confirm() → transitions to ConfirmedState
  order.ship();     // ConfirmedState.ship()  → transitions to ShippedState
  order.cancel();   // ShippedState.cancel()  → throws (invalid transition)
  
  // Add new state (REFUNDED):
  // 1. Create RefundedState class
  // 2. Add transition in DeliveredState.refund() → sets to RefundedState
  // Order, other state classes: minimal or zero changes.
  
STATE vs STRATEGY:

  STRATEGY:
  - Algorithm injected from OUTSIDE the context.
  - Context doesn't change its own strategy.
  - Client or DI selects which strategy to use.
  - No notion of "transitioning between strategies."
  
  STATE:
  - State transitions happen INSIDE (state objects or context trigger transitions).
  - States know about transitions to other states.
  - Context's behavior varies based on internal state evolution.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT State:
- `if/switch (status)` scattered in every method — 4 states × 10 methods = 40 conditional blocks
- Add new state: modify all methods (OCP violation)

WITH State:
→ Each state is a class. Add new state: add one class, add transitions from existing states. Other states/context: minimal changes.
→ Invalid transitions: throw in state class — impossible to forget to check state in a method.

---

### 🧠 Mental Model / Analogy

> A vending machine. States: Idle, HasCoin, Dispensing, OutOfStock. Each state knows which button presses are valid: Idle state: "insert coin" → transitions to HasCoin. HasCoin state: "select product" → transitions to Dispensing, OR "return coin" → back to Idle. Dispensing state: dispenses product → transitions to Idle (or OutOfStock). Pressing "select product" in Idle state: vending machine says "Please insert a coin first" — invalid operation in this state. No master if/switch. Each state defines valid operations.

"Vending machine" = Context (delegates to current state)
"Idle / HasCoin / Dispensing" = concrete State classes
"Insert coin in Idle → transitions to HasCoin" = state object changes context's state
"Select product in Idle → error" = state class throws/returns error for invalid transition

---

### ⚙️ How It Works (Mechanism)

```
STATE PATTERN FLOW:

  Context.operation()
  → currentState.operation(context)
     ├── If valid: perform work, then transition: context.setState(new NextState())
     └── If invalid: throw IllegalStateException or return error
     
  Context stores current state as a field.
  State objects can set context.setState() to trigger transitions.
  Client calls Context methods — never interacts with State directly.
```

---

### 🔄 How It Connects (Mini-Map)

```
Object changes behavior based on internal state (valid/invalid transitions)
        │
        ▼
State Pattern ◄──── (you are here)
(each state = class; context delegates; state objects trigger transitions)
        │
        ├── Strategy: externally injected algorithm (vs State: internal, self-transitioning)
        ├── Finite State Machine: State pattern IS the OOP implementation of FSM
        ├── Command: commands trigger state transitions
        └── Observer: notify observers when state transitions occur
```

---

### 💻 Code Example

```java
// TCP Connection as State Machine (classic textbook example):
interface TcpState {
    void open(TcpConnection conn);
    void close(TcpConnection conn);
    void acknowledge(TcpConnection conn);
    String getName();
}

class ClosedState implements TcpState {
    public void open(TcpConnection conn) {
        System.out.println("Sending SYN...");
        conn.setState(new SynSentState());
    }
    public void close(TcpConnection conn) { System.out.println("Already closed"); }
    public void acknowledge(TcpConnection conn) { throw new IllegalStateException("Not open"); }
    public String getName() { return "CLOSED"; }
}

class SynSentState implements TcpState {
    public void open(TcpConnection conn) { throw new ISE("Already opening"); }
    public void close(TcpConnection conn) {
        conn.setState(new ClosedState());
    }
    public void acknowledge(TcpConnection conn) {
        System.out.println("SYN-ACK received, sending ACK...");
        conn.setState(new EstablishedState());
    }
    public String getName() { return "SYN_SENT"; }
}

class EstablishedState implements TcpState {
    public void open(TcpConnection conn) { throw new ISE("Already established"); }
    public void close(TcpConnection conn) {
        System.out.println("Sending FIN...");
        conn.setState(new ClosedState());
    }
    public void acknowledge(TcpConnection conn) { System.out.println("ACK sent"); }
    public String getName() { return "ESTABLISHED"; }
}

class TcpConnection {
    private TcpState state = new ClosedState();
    
    void open()        { state.open(this); }
    void close()       { state.close(this); }
    void acknowledge() { state.acknowledge(this); }
    void setState(TcpState s) { this.state = s; }
    String getState()  { return state.getName(); }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| State and Strategy patterns are the same | Structurally similar (both use a strategy/state reference in context). Key difference: WHO initiates change. Strategy: client/DI selects algorithm; context doesn't change it during execution. State: the state objects themselves (or context's operations) trigger transitions — state evolves internally. State has semantics of "I am currently in this mode and I'll change based on what happens." |
| State pattern requires a separate class per state | That's the most common implementation and enables OCP. But simple state machines can be implemented with enum + switch (acceptable for simple, stable, few-state machines). The pattern adds value when state-specific behavior is complex, when new states are frequently added, or when transitions need validation. |
| All invalid transitions should throw exceptions | The right behavior depends on the domain. Some invalid operations should throw (programming error — shouldn't happen). Others should be silently ignored (user pressed "confirm" on an already-confirmed order — idempotent). Others should return a validation result. State class decides the appropriate response for each invalid operation. |

---

### 🔥 Pitfalls in Production

**State objects having references to each other causing coupling:**

```java
// ANTI-PATTERN: State objects directly reference each other — tight coupling:
class PendingState implements OrderState {
    void confirm(Order order) {
        order.setState(new ConfirmedState(
            new ShippedState(new DeliveredState())  // ← chain of references!
        ));
    }
}
// PendingState needs to know about ConfirmedState, ShippedState, DeliveredState.
// Change ShippedState constructor → update PendingState.

// FIX: State objects reference only their IMMEDIATE next states:
class PendingState implements OrderState {
    void confirm(Order order) {
        order.setState(new ConfirmedState());  // only knows ConfirmedState
    }
}

class ConfirmedState implements OrderState {
    void ship(Order order) {
        order.setState(new ShippedState());  // only knows ShippedState
    }
}
// Each state knows only its direct successors. Minimal coupling.

// ALSO: state-specific data that doesn't belong in context:
// BAD: stowing state-specific data in context for state to access:
class Order { String trackingNumber; ... }  // only meaningful in SHIPPED state
// FIX: carry state-specific data in the state object itself:
class ShippedState implements OrderState {
    private final String trackingNumber;  // belongs here, not in Order
    ShippedState(String trackingNumber) { this.trackingNumber = trackingNumber; }
}
```

---

### 🔗 Related Keywords

- `Strategy Pattern` — externally injected algorithm (vs State: internal, self-transitioning)
- `Finite State Machine` — State pattern IS the OOP implementation of an FSM
- `Command Pattern` — commands can trigger state transitions in the State pattern
- `Observer Pattern` — observers can be notified on state transitions
- `Spring State Machine` — Spring's library implementing the State pattern for complex workflows

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Each state = class. Context delegates to  │
│              │ current state. State objects trigger     │
│              │ transitions. Eliminates if/switch on state│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Object changes behavior based on state;   │
│              │ many if/switch on state enum; adding new │
│              │ states should not modify existing code   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple 2-3 state machine with rare       │
│              │ changes — enum + switch is cleaner;      │
│              │ state logic is trivial                    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Traffic light: each color IS a state    │
│              │  class that knows what to show and what  │
│              │  comes next — no master if/switch."       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Strategy Pattern → Finite State Machine → │
│              │ Spring State Machine → Command Pattern    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring State Machine (`org.springframework.statemachine`) is a framework implementation of the State pattern. It allows declaring states and transitions declaratively, with guards (conditions) and actions (callbacks on transition). How does a declarative state machine (Spring State Machine) differ from the manual State pattern implementation above? When would you use Spring State Machine vs. handcoding state classes? Consider: complexity of transition rules, persistence of state (state survives server restarts), and the need to visualize the state machine as a diagram.

**Q2.** The State pattern is the OOP implementation of a Finite State Machine (FSM). A simple order lifecycle has 5 states and 8 transitions. A complex one might have 20 states and 50 transitions. At what point does the State pattern become unmanageable compared to a table-driven FSM (where transitions are stored in a Map<State, Map<Event, State>>)? How does a table-driven FSM compare to the State pattern in terms of: extensibility, readability, and ability to add guards/actions on transitions?
