---
id: DPT-083
title: "Anti-Pattern: Circular Dependencies"
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-074, DPT-078
used_by: []
related: DPT-074, DPT-078, DPT-081, DPT-082, DPT-063
tags:
  - anti-pattern
  - advanced
  - dependency-cycle
  - coupling
  - modularity
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 83
permalink: /technical-mastery/design-patterns/circular-dependencies/
---

⚡ TL;DR - Circular dependencies (dependency cycles) occur
when A depends on B and B depends on A (directly or
transitively). They prevent independent compilation,
testing, and deployment of modules; prevent clear
layered architecture; and are a sign that two modules
share a responsibility that belongs in a single module
or a third shared module.

| #83 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-074, DPT-078 | |
| **Used by:** | N/A | |
| **Related:** | DPT-074, DPT-078, DPT-081, DPT-082, DPT-063 | |

---

### 🔥 The Problem This Solves

**THE MODULE THAT CANNOT BE ISOLATED:**
Package A: `com.example.user` (User management)
Package B: `com.example.order` (Order management)

```
com.example.user.User
    → references → com.example.order.Order (user's recent
      orders)

com.example.order.Order
    → references → com.example.user.User (order's customer)
```

**THE CONSEQUENCES:**
1. `user` package cannot compile without `order` package.
   `order` package cannot compile without `user` package.
   They MUST be built together. The cycle removes the
   ability to build one independently.
2. Testing `User` requires loading `Order` (and all of
   Order's dependencies). Tests for `User` are heavier
   than they need to be.
3. Deploying `user` module independently is impossible.
   Any change to `order` potentially requires redeploying
   `user`.
4. The cycle reveals a missing abstraction: who is
   responsible for the user-order relationship?

---

### 📘 Textbook Definition

A **Circular Dependency** (dependency cycle) exists when
two or more modules depend on each other, directly or
transitively:

- **Direct cycle:** A → B and B → A
- **Transitive cycle:** A → B → C → A

**Acyclic Dependencies Principle (ADP):**
Robert C. Martin formalized the rule:
> "The dependency structure between packages must be
> a Directed Acyclic Graph (DAG). There must be no
> cycles in the package dependency structure."

**Why it matters:**
In a DAG dependency structure:
- Each package can be built and tested independently
- Changes propagate DOWNWARD (from dependents to dependencies),
  never UPWARD (which would be a cycle)
- Clear architectural layers emerge

In a cyclic structure:
- Packages form a "strongly connected component" that
  must be treated as a single monolithic unit
- Architectural layers collapse (no clear "up" or "down")

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A depends on B, B depends on A: neither can exist without
the other. The cycle makes them inseparable. Break it
by introducing a third abstraction both can depend on.

**One analogy:**
> Two employees who each refuse to do any work without
> first getting approval from the other.
> Employee A: "I can't write the report until B reviews
> the data." Employee B: "I can't review the data until
> A writes the summary." Deadlock.
>
> The fix: identify what both are waiting for. Extract
> a SHARED artifact (the data specification document)
> that both can independently reference, breaking the
> mutual dependency.
>
> Circular dependency fix: extract the shared abstraction
> (interface, shared library, shared type) that both
> modules need. Both depend on the shared abstraction.
> Neither depends on the other.

---

### 🔩 First Principles Explanation

**WHY CYCLES FORM:**
1. **Missing abstraction**: two modules need to share a
   concept. Instead of creating a third shared module
   for that concept, each module references the other
   directly to get the concept it needs.
2. **Convenience**: "I need just one method from that
   other package" is the seed of many cycles. One reference
   creates a soft cycle; over time more references accumulate.
3. **Layering violations**: a lower-layer module needs
   to call back into an upper-layer module (callback, event).
   This inverts the normal dependency direction and creates
   a cycle if not handled with the Dependency Inversion
   Principle (DPT-078).

**BREAKING CYCLES - THREE STRATEGIES:**

**Strategy 1: Extract Shared Module:**
If A and B both need concept X that lives in B,
extract X into new module C. Both A and B depend on C.
A ← C → B: no cycle.

**Strategy 2: Dependency Inversion:**
If the cycle is because B needs to call A's behavior
(callback): define an interface in A. B implements
or uses that interface. A now has no dependency on B
(it depends on the interface it defines). DIP (DPT-078)
applied at the module level.

**Strategy 3: Move Method/Class:**
If only ONE method in B causes the cycle (B is mostly
independent of A, but one method references A): move
that method to A (where it belongs). Cycle eliminated.

**DETECTING CYCLES:**
Build tools: Maven enforces through module structure.
ArchUnit (Java testing framework) can assert no cycles:
```java
noClasses().that().resideInPackage("..order..")
    .should().dependOnClassesThat()
    .resideInPackage("..user..");
```
JDepend, IntelliJ's Dependency Analysis, and SonarQube
can identify package-level cycles.

---

### 🧪 Thought Experiment

**THE NOTIFICATION CYCLE:**
`OrderService` sends notifications when an order is
placed: it calls `NotificationService.send(user, message)`.
`NotificationService` needs to look up user preferences:
it calls `UserService.getPreferences(userId)`.
`UserService` needs to send a welcome notification on
new user registration: it calls `NotificationService.send(...)`.

Cycle: `OrderService → NotificationService → UserService → NotificationService`

**BREAKING IT:**
`NotificationService` should not depend on `UserService`.
Solution: the `send()` method takes a `NotificationRequest`
containing all needed data (recipient, preferences) already
resolved. Callers resolve the data; `NotificationService`
just sends. `NotificationService` has zero dependencies
on domain services.

```
Before: OrderService → NotificationService → UserService →
  NotificationService
After:  OrderService → [UserService, NotificationService]
  (no cycle)
        OrderService resolves user preferences before
          calling NotificationService
```

---

### 🧠 Mental Model / Analogy

> Circular dependency = a knot in the dependency graph.
>
> Without cycles: the dependency graph is a DAG.
> You can walk from any node DOWNSTREAM to its dependencies.
> The direction is consistent. Upstream modules don't
> know about downstream modules.
>
> With a cycle: you can walk in circles. There is no
> "upstream" or "downstream" for the nodes in the cycle.
> They are all equally entangled. You cannot separate
> them without cutting the cycle.
>
> Breaking a cycle: untie the knot. Find WHAT the two
> modules share (why they reference each other). Extract
> that shared thing into a third module. Now both can
> point to the shared thing without pointing to each other.

---

### 📶 Gradual Depth - Three Levels

**Level 1 - Direct cycle detection:**
Look for two packages/classes where A imports B and
B imports A. This is a direct cycle. Also check:
if modifying class A requires modifying class B, and
modifying class B requires modifying class A - this
behavioral coupling may indicate a structural cycle.

**Level 2 - Transitive cycle analysis:**
A → B → C → A is a transitive cycle. Harder to spot
manually. Use static analysis tools (ArchUnit, SonarQube,
JDepend) to detect package-level cycles automatically.
In Maven: multi-module project structure enforces DAG
at the build level (you cannot have a cycle in Maven
module dependencies because Maven would fail to build).

**Level 3 - Architectural implications:**
Cycles at the PACKAGE level create "component coupling"
that undermines modular architecture. In microservices:
service A calling service B, service B calling service A
(synchronously) creates a runtime cycle. Under failure:
a circuit breaker in A prevents calls to B; B cannot
respond; A is also waiting for B. Distributed deadlock.
At the microservice level: circular synchronous calls
are equivalent to circular class dependencies - both
prevent independent deployment and create failure cascades.

---

### ⚙️ How It Works (Mechanism)

```
Cycle Breaking Strategies
┌─────────────────────────────────────────────────────────┐
│ STRATEGY 1: Extract Shared Module                       │
│   BEFORE:  A ──depends──► B ──depends──► A  (cycle!)   │
│   AFTER:   A ──depends──► C ◄──depends── B (no cycle)  │
│   C = extracted shared interface/class                 │
│                                                         │
│ STRATEGY 2: Dependency Inversion (Callback)            │
│   BEFORE:  A ──depends──► B                            │
│            B ──depends──► A  (to call back)            │
│   AFTER:   A defines interface I                       │
│            B depends on interface I (not A)            │
│            A provides implementation of I              │
│   Dependency: A ◄── B (B depends on A's interface)    │
│              no A → B dependency remains               │
│                                                         │
│ STRATEGY 3: Move the Offending Method                   │
│   BEFORE:  A ──depends──► B                            │
│            B.method() calls A (one method causes cycle)│
│   AFTER:   Move B.method() to A                        │
│            B dependency on A: eliminated               │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Circular dependency and fix:**

```java
// BAD: user and order packages have circular dependency.

// com.example.user:
class User {
    private List<Order> recentOrders; // imports order package!
    List<Order> getRecentOrders() { return recentOrders; }
}

// com.example.order:
class Order {
    private User customer; // imports user package!
    User getCustomer() { return customer; }
}
// Cycle: user → order → user
// Cannot build user without order, cannot build order without user.
```

```java
// GOOD: Strategy 1 - Extract shared types.
// New module: com.example.common

// com.example.common:
interface Identifiable { long getId(); }
// (or use IDs instead of direct object references)

// com.example.user - no import from order:
class User implements Identifiable {
    private long id;
    private List<Long> recentOrderIds; // IDs, not Order objects!
    public long getId() { return id; }
    List<Long> getRecentOrderIds() { return recentOrderIds; }
}

// com.example.order - no import from user:
class Order implements Identifiable {
    private long id;
    private long customerId; // ID, not User object!
    public long getId() { return id; }
    long getCustomerId() { return customerId; }
}
// No cycle. Resolved via IDs + a service that joins them.
// The joining service (orchestrator) can depend on both.
```

```java
// GOOD: Strategy 2 - Dependency Inversion for callback.

// com.example.order:
interface OrderEventListener {  // interface owned by order package
    void onOrderPlaced(long orderId, long userId);
}

class OrderService {
    private final OrderEventListener listener;
    OrderService(OrderEventListener listener) {
        this.listener = listener;
    }
    void placeOrder(Order order) {
        // ... place order logic ...
        listener.onOrderPlaced(order.getId(),
            order.getCustomerId()); // callback
    }
}

// com.example.notification - implements interface from order:
class NotificationService implements OrderEventListener {
    @Override
    public void onOrderPlaced(long orderId, long userId) {
        // sends notification
    }
}
// order package has no dependency on notification package.
// notification depends on order (to implement the interface).
// No cycle.
```

---

### 🔥 Failure Scenarios

**SPRING CIRCULAR BEAN DEPENDENCY:**
```
Exception: The dependencies of some of the beans in
the application context form a cycle:
  userService → orderService → userService
```
Spring detects dependency cycles in bean wiring.
This is a runtime manifestation of a design-time circular
dependency. The fix: refactor the design (extract interface,
use events/ApplicationEventPublisher, restructure dependencies).
Not: use `@Lazy` as a band-aid (hides the design problem).

**MICROSERVICE SYNCHRONOUS CALL CYCLE:**
```
UserService.getProfile() → calls →
  OrderService.getRecentOrders()
OrderService.processReturn() → calls →
  UserService.validateUser()
```
Under load: `UserService` is slow → `OrderService.processReturn()` blocks
→ `OrderService.getRecentOrders()` also fails → `UserService.getProfile()` fails.
A cascading failure that propagates around the cycle.
Fix: break the synchronous call with events (async decoupling).
`OrderService.processReturn()` emits an event; `UserService`
subscribes. No synchronous cycle.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Two classes using each other is always a cycle | Two classes in the SAME package/module using each other is fine (package-internal cohesion). Cycles are problematic at MODULE/PACKAGE level boundaries |
| Circular dependencies are always a design error | In some very tightly coupled systems (like a parser and an AST), a controlled internal cycle within a single module may be acceptable. The rule is: no cycles between PACKAGES/MODULES/SERVICES that should be independently deployable |
| @Lazy annotation fixes circular dependencies in Spring | @Lazy defers initialization to mask the symptom. The structural cycle remains. Use @Lazy only as a temporary workaround; the real fix is restructuring the dependency graph |
| Circular dependencies are rare in practice | They are surprisingly common, especially in "service layer hell" architectures where services freely call each other. Most non-trivial Spring projects have at least one cycle if not guarded against |

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DEFINITION   │ A depends on B, B depends on A           │
│              │ (directly or transitively). DAG violated.│
├──────────────┼──────────────────────────────────────────┤
│ CONSEQUENCES │ Cannot build/test/deploy independently. │
│              │ No clear layering. Failure cascades.    │
├──────────────┼──────────────────────────────────────────┤
│ FIX 1        │ Extract shared module (shared interface) │
│              │ that both A and B depend on.            │
├──────────────┼──────────────────────────────────────────┤
│ FIX 2        │ Dependency Inversion. A defines callback │
│              │ interface. B implements it. A ◄── B.    │
├──────────────┼──────────────────────────────────────────┤
│ FIX 3        │ Move the offending method to remove      │
│              │ the one reference causing the cycle.    │
├──────────────┼──────────────────────────────────────────┤
│ DETECT       │ ArchUnit, SonarQube, IntelliJ dep analysi│
│ NEXT EXPLORE │ DPT-084: Inbox Pattern                  │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Circular dependencies make modules inseparable. A and
   B in a cycle cannot be built, tested, or deployed
   independently. They are effectively one module.
   This defeats the purpose of modular design.
2. Three fixes: (1) Extract shared interface/module both
   can depend on. (2) Use Dependency Inversion (A defines
   interface; B implements it). (3) Move the offending
   method to eliminate the one reference causing the cycle.
3. Detection: ArchUnit's `noClasses().should().dependOn()`
   assertions in CI/CD. Catch cycles at commit time,
   not in production. Spring's cycle exception is a
   late (runtime) detection of a design-time problem.

