---
layout: default
title: "Coupling"
parent: "Clean Code"
nav_order: 425
permalink: /clean-code/coupling/
number: "425"
category: Clean Code
difficulty: ★★☆
depends_on: Cohesion, Module Design
used_by: Dependency Injection, DIP, Refactoring
tags: #cleancode #architecture #foundational
---

# 425 — Coupling

`#cleancode` `#architecture` `#foundational`

⚡ TL;DR — The degree to which one module depends on the internals of another.

| #425 | Category: Clean Code | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Cohesion, Module Design | |
| **Used by:** | Dependency Injection, DIP, Refactoring | |

---

### 📘 Textbook Definition

Coupling is the measure of interdependence between software modules. Tight (high) coupling means modules depend heavily on each other's internal details, making changes risky. Loose (low) coupling means modules interact through stable interfaces, making them independently changeable and testable.

---

### 🟢 Simple Definition (Easy)

Coupling is about **how much modules know about each other**. Tight coupling = change one thing, break another. Loose coupling = change freely without fear.

---

### 🔵 Simple Definition (Elaborated)

When modules are tightly coupled, a change in one ripples through many others. Loose coupling is achieved by depending on abstractions (interfaces) rather than concrete implementations, minimizing the number of dependencies, and keeping what each module exposes to a minimum. The goal is that modules can evolve independently.

---

### 🔩 First Principles Explanation

**The core problem:**
Systems where classes directly instantiate and call other concrete classes become rigid. You cannot change one module without changing all its callers.

**The insight:**
> "Depend on abstractions, not concretions." (DIP)

```
Tight coupling:
  class OrderService {
      PayPalGateway gateway = new PayPalGateway();  // concrete dependency
  }

Loose coupling:
  class OrderService {
      PaymentGateway gateway;  // depends on interface
      OrderService(PaymentGateway gw) { this.gateway = gw; }
  }
```

---

### ❓ Why Does This Exist (Why Before What)

Without loose coupling, you cannot unit test in isolation (can't mock), cannot swap implementations (PayPal to Stripe), and cannot reuse modules independently. Every change becomes a system-wide risk.

---

### 🧠 Mental Model / Analogy

> Think of electrical outlets and plugs. The outlet (module) doesn't know what device is plugged in — it only exposes a standard interface (socket). Any device with the right plug works. That's loose coupling via a stable interface.

---

### ⚙️ How It Works (Mechanism)

Coupling types (loosest to tightest):

```
Message       — communicate via messages only                   (loosest)
Data          — share only primitive parameters
Stamp         — share composite data structures
Control       — one module controls another's flow (flag passing)
External      — both depend on same external format or tool
Common        — both access shared global data
Content       — one directly modifies another's internals       (tightest)
```

---

### 🔄 How It Connects (Mini-Map)

```
        [DIP]
           ↓
[Concrete Dep] --> [Interface] --> [Loose Coupling]
                                         ↑
                                    [Cohesion ↑]
```

---

### 💻 Code Example

```java
// TIGHT coupling — OrderService depends on concrete PayPalGateway
class OrderService {
    private PayPalGateway gateway = new PayPalGateway(); // hard dependency

    void placeOrder(Order order) {
        gateway.charge(order.total()); // cannot swap, cannot mock in tests
    }
}

// LOOSE coupling — depends on interface, injected externally
interface PaymentGateway {
    void charge(double amount);
}

class OrderService {
    private final PaymentGateway gateway;

    OrderService(PaymentGateway gateway) {  // DI = loose coupling
        this.gateway = gateway;
    }

    void placeOrder(Order order) {
        gateway.charge(order.total()); // works with any PaymentGateway impl
    }
}

// In tests: inject a mock
OrderService svc = new OrderService(mock(PaymentGateway.class));
// In prod: inject the real impl
OrderService svc = new OrderService(new StripeGateway());
```

---

### 🔁 Flow / Lifecycle

```
1. Module A needs Module B
        ↓
2. Option A: A directly instantiates B (tight coupling)
   Option B: A depends on interface I; B implements I (loose coupling)
        ↓
3. With loose coupling: A never imports B; B can be swapped freely
        ↓
4. Testing A: inject a mock of I — no real B needed
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| All coupling is bad | Some coupling is unavoidable; goal is to minimize it |
| Use interfaces everywhere | Interfaces for external boundaries; pragmatic for internals |
| Coupling = number of imports | Coupling = dependency on internals, not just import count |
| DI frameworks eliminate coupling | They manage coupling — you still design where it lives |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Circular Dependencies**
A depends on B, B depends on A — even through interfaces. The build or wiring fails.
Fix: introduce a third module/event to break the cycle; redesign responsibilities.

**Pitfall 2: Leaking Implementation Details**
Returning `ArrayList<User>` instead of `List<User>` from a public API couples callers to the implementation.
Fix: always return the most abstract type that satisfies the caller's needs.

**Pitfall 3: God Object as Hub**
One class that everything else imports creates star-topology coupling. Any change to it breaks everything.
Fix: split the god object; route communication through interfaces or events.

---

### 🔗 Related Keywords

- **Cohesion** — the twin dimension; aim for high cohesion + low coupling
- **DIP (Dependency Inversion Principle)** — the principle that enforces loose coupling
- **Dependency Injection** — the technique that implements loose coupling at runtime
- **SOLID** — coupling and cohesion underpin all 5 SOLID principles
- **Interface** — the primary mechanism for decoupling in OOP

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Modules should know as little as possible     │
│              │ about each other's internals                   │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Always — loose coupling is the constant goal  │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Over-engineering tiny scripts with interfaces  │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Depend on interfaces, not implementations"    │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Cohesion → DIP → Dependency Injection         │
└─────────────────────────────────────────────────────────────┘
```

### 🧠 Think About This Before We Continue

**Q1.** What is the difference between afferent coupling (Ca) and efferent coupling (Ce)?  
**Q2.** How does event-driven architecture reduce coupling compared to direct method calls?  
**Q3.** Can you have zero coupling in a real system? Why or why not?

