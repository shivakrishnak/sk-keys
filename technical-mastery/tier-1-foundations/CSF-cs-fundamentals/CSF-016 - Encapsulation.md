---
id: CSF-016
title: Encapsulation
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★☆☆
depends_on: CSF-003
used_by: CSF-010, CSF-019
related: CSF-003, CSF-008, CSF-010
tags:
  - foundational
  - first-principles
  - mental-model
  - design-principle
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 16
permalink: /technical-mastery/csf/encapsulation/
---

⚡ TL;DR - Encapsulation bundles data and behavior into
a single unit and restricts direct access to the data.
It protects an object's internal state so only its own
methods can change it - preserving the object's invariants
regardless of how callers behave.

| #009 | Category: CS Fundamentals - Paradigms | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming (OOP) (CSF-003) | |
| **Used by:** | Polymorphism (CSF-010), Composition over Inheritance (CSF-019) | |
| **Related:** | OOP (CSF-003), Abstraction (CSF-008), Polymorphism (CSF-010) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Early C programs used `struct` types to group related
data, but anyone with a pointer to the struct could
read or write any field directly. A `BankAccount` struct
with a `balance` field could be modified by any function
in any file. There was no way to enforce that balance
only changed through valid deposit/withdraw operations.
If you needed to add a "negative balance triggers alert"
rule, you had to find every place in the codebase that
wrote to `account.balance` and add the check - there
was no single place to put it.

**THE BREAKING POINT:**

As programs grew, global state modified from arbitrary
code locations made programs impossible to reason about.
A bug that set a negative balance could originate from
any of 50 functions. There was no concept of "this data
belongs to this component and only this component
manages it." State was globally visible and globally
mutable.

**THE INVENTION MOMENT:**

Encapsulation was developed to solve this. By bundling
data and the operations on that data into a single class,
and restricting direct access to the data (`private`
fields), the class becomes the single, authoritative
owner of its internal state. Callers can only interact
through the class's public methods - methods that can
enforce whatever rules the class needs to maintain its
consistency.

**EVOLUTION:**

Encapsulation in OOP (Simula, 1967; Smalltalk, 1972)
introduced `private` as a language keyword. Later, the
principle was extended: Bertrand Meyer's Command-Query
Separation (CQS) formalized that methods should either
change state (commands) or return data (queries) but
not both. The "Tell, Don't Ask" principle emerged from
recognizing that getters-plus-external-logic defeated
encapsulation's purpose. Modern applications of
encapsulation: microservices own their databases
(no direct DB access from other services), modules
hide their implementation packages, bounded contexts
expose only domain events.

---

### 📘 Textbook Definition

Encapsulation is the OOP principle of bundling data
(fields/attributes) and the behavior that operates on
that data (methods) into a single unit (a class), and
restricting access to the internal data so that it can
only be modified through the class's defined methods.
The access modifiers `private`, `protected`, and `public`
are the language mechanisms that enforce encapsulation.
A well-encapsulated class maintains its invariants
(consistency rules) because only its own methods can
change its state, and those methods enforce the rules.
Encapsulation is distinct from abstraction: abstraction
hides complexity behind an interface; encapsulation
protects internal state from unauthorized modification.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Encapsulation means an object's internal data is its
own business - outsiders must use the door (methods),
not break the window (direct field access).

**One analogy:**

> Think of a vending machine's cash drawer. Customers
> cannot reach into the drawer directly - they interact
> only through the coin slot (method) and change
> dispenser (method). The machine controls all changes
> to the cash balance and ensures it is always consistent.
> If customers could open the drawer freely, the balance
> would be untrustworthy and the machine would be broken.

**One insight:**

The difference between encapsulation and just having
private fields with getters and setters is the same as
the difference between a vault and a transparent box
with a door. A getter/setter pair that directly exposes
every field is not encapsulation - it is a private field
with public access. True encapsulation means behavior
lives with data, and the class enforces rules about how
the data can change.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **An object owns its state** - no external code
   can modify an object's internal fields directly;
   only the object's methods can change them.

2. **Methods enforce invariants** - any rule about
   valid states (balance >= 0, order must have items
   before confirmation, user must be active to log in)
   is enforced in methods, so it applies universally,
   not just when developers remember to check.

3. **Behavior belongs with data** - operations that
   modify state should be on the class that owns the
   state, not scattered in external classes that
   acquire the data and modify it.

**DERIVED DESIGN:**

A `BankAccount` class with `private double balance`
can enforce: balance never goes below zero; deposits
are positive; withdrawals require sufficient funds.
These rules live in `deposit()` and `withdraw()` methods.
Every caller goes through those methods; the rules
apply universally. An external class cannot write
`account.balance = -9999` because `balance` is `private`.

Without encapsulation: the same check would need to
appear in every line of code that modified `balance`.
Forget one place, and the invariant is broken. With
encapsulation: the check lives in one place, and all
modification paths enforce it automatically.

**THE TRADE-OFFS:**

**Gain:** Object invariants are guaranteed by the class
itself, not by caller discipline. The class is internally
consistent regardless of how it is used. Bugs related
to invalid state are localized to the class that owns
the state.

**Cost:** Callers must go through methods. In simple
data-transfer contexts (DTOs), this feels like unnecessary
verbosity. Deeply encapsulated objects can be harder
to serialize (Jackson, JPA need access to fields or
require annotations).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** The need to protect invariants is essential.
Every class with business rules needs to prevent callers
from bypassing those rules.

**Accidental:** Java's getter/setter pattern is accidental
complexity. It arose from JavaBeans conventions and tool
compatibility (JPA, Jackson), not from the encapsulation
principle. A class with 15 getters and setters that
expose every field with no logic is not encapsulated;
it is syntactic overhead.

---

### 🧪 Thought Experiment

**SETUP:**

A `UserAccount` class tracks login attempts and locks
the account after 5 failures.

**WITHOUT ENCAPSULATION:**

```java
// Internal state exposed as public fields
public class UserAccount {
    public int failedAttempts;
    public boolean locked;
}

// Any caller can break the invariant:
account.failedAttempts = 0;  // reset lock bypass
account.locked = false;       // manual unlock
account.failedAttempts = 100; // whatever
```

The lock-after-5-failures rule exists only as a convention.
Any caller can bypass it by writing to `failedAttempts`
directly. A security bug is one missed check away.

**WITH ENCAPSULATION:**

```java
public class UserAccount {
    private int failedAttempts = 0;
    private boolean locked = false;

    // The rule lives here, enforced universally
    public void recordFailedLogin() {
        failedAttempts++;
        if (failedAttempts >= 5) {
            locked = true;
        }
    }

    public boolean isLocked() {
        return locked;
    }

    // Only admins can unlock (business rule enforced)
    public void adminUnlock() {
        failedAttempts = 0;
        locked = false;
    }
}
```

The rule "lock after 5 failures" cannot be bypassed.
No caller can increment `failedAttempts` to 6 without
triggering the lock. No caller can reset `failedAttempts`
without going through `adminUnlock()`.

**THE INSIGHT:**

Security-sensitive state especially needs encapsulation.
"Private by default" is not just a style preference -
it is a security boundary. Public fields on sensitive
state are potential security vulnerabilities.

---

### 🧠 Mental Model / Analogy

> Encapsulation is like a bank account at a reputable
> bank. Your money is yours - but you cannot walk into
> the vault and take it directly. You submit a withdrawal
> request (call a method). The bank checks your balance,
> verifies your identity, applies regulatory rules, and
> updates the balance. The bank is the single authority
> over the balance. It can introduce new rules (fraud
> detection, minimum balance fees) without requiring
> you to change how you interact with your account.

- Your money (balance) → private field
- Vault → private access (no direct field access)
- Withdrawal request form → public method
- Bank's rules → invariant enforcement in methods
- Bank introducing fraud detection → adding logic to
  a method without breaking caller code

**Where this breaks down:** Banks can also refuse
legitimate transactions (overly strict enforcement).
Classes can be over-encapsulated: requiring a method
call to read a simple calculated value is unnecessary
friction. Not everything needs to be encapsulated;
simple value objects and DTOs may expose fields freely.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Encapsulation means the data inside an object is private
- like a locked box. To change it, you use the object's
own tools (methods), which enforce the rules. You cannot
just reach in and change the data directly.

**Level 2 - How to use it (junior developer):**
Make fields `private`. Provide `public` methods for
the operations callers need. Do NOT provide a getter
and setter for every field - that defeats the purpose.
Ask: "What operations does the caller actually need to
perform?" and provide exactly those. If a field should
never change after construction, provide no setter.

**Level 3 - How it works (mid-level engineer):**
`private` is enforced by the compiler (Java, C++) or
by convention (`_field` in Python, `#field` in modern
JavaScript). At the JVM level, access control is verified
at bytecode loading: a `getfield` or `putfield` bytecode
instruction referencing a private field from outside
the class causes an `IllegalAccessError`. Encapsulation
is not just a style rule - it is enforced by the runtime.

**Level 4 - Why it was designed this way (senior/staff):**
The "Tell, Don't Ask" principle (Martin Fowler) captures
the real purpose of encapsulation: instead of asking
an object for its data and then deciding what to do
with it (which puts behavior in the wrong place),
tell the object what to do. `if (account.getBalance()
>= amount) { account.setBalance(account.getBalance()
- amount); }` is Ask. `account.withdraw(amount)` is
Tell. The difference: in the Ask version, the caller
"owns" the withdrawal logic; in 10 different places,
10 different withdrawal implementations exist.
In the Tell version, the class owns the logic - once,
in one place, consistent everywhere.

**Level 5 - Mastery (distinguished engineer):**
Encapsulation at scale is a service design principle.
A microservice that owns its database is practicing
encapsulation: no other service queries the database
directly; all access goes through the service's API.
This is the same principle as `private` fields, applied
at service boundaries. The failure mode of breaking
this encapsulation - shared databases in microservice
architectures - is one of the most common distributed
systems architecture mistakes. When two services share
a database table, they share state without a method
interface. Schema changes break both services; neither
can enforce its invariants independently.

---

### ⚙️ Why It Holds True (Formal Basis)

Encapsulation is formalized in type theory through
information hiding: a module's type signature exposes
only the public interface; the internal representation
is hidden. John Reynolds' "Types, Abstraction, and
Parametric Polymorphism" (1983) established that
abstract data types - types whose representation is
hidden and whose operations are the only interface -
are the formal basis of encapsulation.

Invariant preservation is formally provable: if all
state-modifying operations enforce the invariant, then
the invariant holds for all reachable states. This is
the class invariant in Hoare logic. Languages like Eiffel
make invariants explicit with `class invariant` blocks
and verify them at runtime after every public method call.

---

### 🔄 System Design Implications

Encapsulation is a boundary-drawing principle that
applies at every level of system design.

**Aggregate design (DDD).** In Domain-Driven Design,
an Aggregate is an encapsulation boundary: external code
accesses aggregate members only through the aggregate
root. `order.addItem(item)` is correct; retrieving
`order.getItems().add(item)` bypasses the aggregate's
encapsulation and can leave the order in an invalid state.

**API encapsulation.** A microservice's REST API is
its public interface; the database is its private state.
A "golden rule of microservices" is: never let external
services query another service's database directly.
The service's API methods are the only valid operations
on its state.

**What changes at scale:** At 10x team size, classes
without encapsulation become a coordination problem:
every change to a data structure requires auditing
all callers. Encapsulation reduces coordination to
"who changed the class's public interface?" At 100x,
services without API encapsulation require coordinating
schema changes across all consumer teams simultaneously.
Proper encapsulation reduces this to a single service's
responsibility.

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Getter/Setter Anti-Pattern**

```java
// BAD: All fields exposed via getters and setters.
// This is NOT encapsulation - it's public fields with
// extra indirection. The "balance" can be set to any
// value; no invariant is enforced.
public class Order {
    private List<OrderItem> items;
    private OrderStatus status;
    private double total;

    // Caller does: order.getItems().add(item) - bypasses logic
    public List<OrderItem> getItems() { return items; }
    public void setItems(List<OrderItem> items) {
        this.items = items; // no validation, no total update
    }
    public OrderStatus getStatus() { return status; }
    public void setStatus(OrderStatus s) {
        this.status = s; // no state machine enforcement
    }
    public double getTotal() { return total; }
    public void setTotal(double total) {
        this.total = total; // caller computes total: bug risk
    }
}

// GOOD: Encapsulate the business operations.
// Internal state changes only through meaningful methods.
// Total is always consistent; status machine is enforced.
public class Order {
    private final List<OrderItem> items = new ArrayList<>();
    private OrderStatus status = OrderStatus.DRAFT;

    public void addItem(Product p, int qty) {
        if (status != OrderStatus.DRAFT) {
            throw new IllegalStateException(
                "Cannot add items to a submitted order"
            );
        }
        items.add(new OrderItem(p, qty));
    }

    // Total computed from items - always consistent
    public Money total() {
        return items.stream()
            .map(OrderItem::subtotal)
            .reduce(Money.ZERO, Money::add);
    }

    public void submit() {
        if (items.isEmpty()) {
            throw new IllegalStateException(
                "Cannot submit an empty order"
            );
        }
        this.status = OrderStatus.SUBMITTED;
    }

    // Read-only view - callers cannot add to returned list
    public List<OrderItem> items() {
        return Collections.unmodifiableList(items);
    }
}
```

**Example 2 - Failure: Leaking Mutable Internal State**

```java
// BAD: Returns the internal mutable list.
// Caller can bypass addItem() and add items directly.
public List<OrderItem> getItems() {
    return items; // MUTABLE reference returned!
}

// Caller's code:
order.getItems().add(new OrderItem(product, qty));
// No validation, no status check, items added in
// any state including CONFIRMED or CANCELLED.

// GOOD: Return defensive copy or unmodifiable view.
public List<OrderItem> items() {
    return Collections.unmodifiableList(items);
    // Or: return List.copyOf(items); (Java 10+)
}
// Now: order.items().add(...) throws UnsupportedOp
```

---

### ⚖️ Comparison Table

| Concept | What It Does | Key Mechanism | Goal |
|---|---|---|---|
| Encapsulation | Bundles data + behavior; hides state | `private` fields | Protect invariants |
| Abstraction | Hides complexity behind interface | Interfaces, abstract classes | Decouple interface from impl |
| Access Control | Restricts visibility of members | `private/protected/public` | Enforce encapsulation |
| Information Hiding | Hides implementation decisions | Module boundaries | Enable independent change |

**Relation:** Encapsulation and abstraction are related
but different. Abstraction says "expose what, hide how."
Encapsulation says "this object owns this data; others
ask through methods." A class can be abstract (hides
algorithm complexity) without encapsulating state (public
fields). A class can encapsulate state (private fields,
methods) without being abstract (single concrete class,
no interface). In practice, OOP classes typically do
both.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Getters and setters = encapsulation | Getter/setter pairs that expose every field with no logic are "anemic" objects - just public fields with ceremony. True encapsulation provides meaningful operations, not data access. |
| `private` makes it impossible to access the field | Java reflection can access private fields at runtime. `@SpringBootTest` and JPA do this. `private` enforces the encapsulation contract at compile time; it is not a security boundary at runtime. |
| Encapsulation and abstraction are the same | Abstraction hides complexity behind interfaces (what vs how). Encapsulation protects internal state (who can change this). A class can abstract without encapsulating, and encapsulate without abstracting. |
| You should always encapsulate all state | Value objects and DTOs often should expose all fields. `record Point(int x, int y) {}` in Java is fully public - it is a data carrier, not an entity with invariants. Encapsulate entities with invariants; expose simple data freely. |
| Encapsulation makes code harder to test | The opposite: encapsulation makes code easier to test because you can test the class's behavior (methods) without knowing its internal state. Testing the contract, not the implementation, produces more resilient tests. |

---

### 🚨 Failure Modes & Diagnosis

**Anemic Domain Model: No Behavior in Objects**

**Symptom:**
Classes in the domain layer contain only fields and
getters/setters. All business logic lives in `Service`
classes that get data from objects, compute something,
and set it back. The domain classes are data containers
with no behavior.

**Root Cause:**
The codebase split data (DTOs/entities) from behavior
(services), defeating encapsulation. Every business rule
is replicated across multiple service methods. Invariants
are enforced (or not) by caller discipline.

**Diagnostic Signal:**

```java
// Anemic model - all fields, no rules:
public class Order {
    private List<OrderItem> items;
    private BigDecimal total;
    private OrderStatus status;
    // 12 getters + 12 setters, no business methods
}

// Service doing the work the class should do:
public class OrderService {
    public void addItemToOrder(Order order,
            OrderItem item) {
        if (order.getStatus() == OrderStatus.DRAFT) {
            order.getItems().add(item);
            // Recalculate total manually:
            BigDecimal newTotal = order.getItems()
                .stream()
                .map(OrderItem::getPrice)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
            order.setTotal(newTotal);
        }
    }
}
// If there's a second place that adds items,
// total recalculation may be missing or inconsistent.
```

**Fix:** Move behavior to the object that owns the data.
`order.addItem(item)` encapsulates validation and total
recalculation. The service orchestrates, the object
enforces invariants.

---

**Returning Mutable Collections Breaking Encapsulation**

**Symptom:**
An object's internal list is modified by callers without
going through the object's methods. Subsequent method
calls find the object in an unexpected state. Difficult
to find where the unexpected modification happened.

**Root Cause:**
A getter returned the actual `List` object (not a copy
or unmodifiable view). Callers called `.add()` or
`.remove()` on the returned reference, bypassing
the owning object's logic.

**Diagnostic Signal:**

```java
// Check every method that returns a collection:
public List<OrderItem> getItems() {
    return items; // Bug: mutable reference exposed
}

// To diagnose: add an assertion in your method that
// validates the invariant is still satisfied:
public void addItem(OrderItem item) {
    assert items.size() < MAX_ITEMS
        : "Item limit exceeded"; // will fire if bypass
    // ...
}
```

**Fix:** Return `Collections.unmodifiableList(items)` or
`List.copyOf(items)`. Accept the collection as a parameter
to methods rather than having callers get and mutate.
For entities with mutable collections, return a defensive
copy: `return new ArrayList<>(items)`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Object-Oriented Programming (OOP)` - encapsulation
  is one of OOP's four pillars; understanding OOP's
  class/object model provides context

**Builds On This (learn these next):**
- `Abstraction` - encapsulation and abstraction are
  complementary; abstraction hides what; encapsulation
  protects the internal state
- `Polymorphism` - encapsulated behavior expressed
  through interfaces enables polymorphic dispatch
- `Composition over Inheritance` - uses encapsulated
  components rather than exposed state chains to build
  flexible designs

**Alternatives / Comparisons:**
- `Immutability` - a stronger form: if state cannot
  change after construction, no encapsulation is needed
  for modification; Java records and immutable value
  objects trade encapsulation for simplicity
- `Tell, Don't Ask` - the behavioral principle behind
  encapsulation: tell objects what to do rather than
  asking for their data to compute externally

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Bundling data + behavior; restricting     │
│              │ direct state access to protect invariants │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Global mutable state with no single owner │
│ SOLVES       │ makes invariant enforcement impossible    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ True encapsulation = behavior on the class│
│              │ not just private fields + getters/setters │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Entity with business rules and invariants  │
│              │ that must be consistently enforced        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple value objects / DTOs with no rules │
│              │ - unnecessary encapsulation adds friction │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Anemic domain model: all logic in services│
│              │ objects are just data bags with getters   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Invariant safety + single responsibility  │
│              │ vs more ceremony than simple struct access│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "An object owns its state; callers        │
│              │ interact through behavior, not fields"    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Tell Don't Ask -> DDD Aggregate -> CQRS   │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Encapsulation = private data + public behavior.
   The class is the single authority over its state.
   Only its methods change its fields.

2. Getters + setters on every field is NOT encapsulation.
   It is a public field with extra ceremony. Real
   encapsulation means methods that encode business rules.

3. Returning a mutable collection reference from a getter
   breaks encapsulation - callers can modify the list
   without going through the object. Return unmodifiable
   views or defensive copies.

**Interview one-liner:**
"Encapsulation means an object bundles its data and
behavior and prevents external code from directly
modifying its internal state. The object enforces its
own invariants through its methods. A class with getters
and setters for every field is not truly encapsulated -
that is anemic domain model."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Own your state; protect your invariants. This is as
true for a class as it is for a microservice. Any
component that lets external parties modify its state
directly cannot enforce its own consistency. The "owner"
of state must be the single authority that validates
and applies changes. This eliminates the class of bugs
where state is valid everywhere but inconsistent.

**Where else this pattern appears:**

- **Microservice database isolation** - each service
  owns its database exclusively; no cross-service
  database queries. The service API is the only valid
  path to the service's data. This IS encapsulation at
  the service level.
- **Redux/Vuex state stores** - state is private to the
  store; components dispatch actions (methods) to change
  state. Components cannot mutate the store directly.
  The store enforces state transition rules.
- **Event sourcing** - the event log is the authoritative
  state; projections are derived. No one writes to the
  projection directly; they append events (methods),
  and the projection updates itself. The event store
  is the encapsulated state owner.

---

### 💡 The Surprising Truth

Python has no `private` keyword that enforces access
control. A `_field` is a convention ("please don't
touch this") and `__field` is name-mangled to
`_ClassName__field` (making it slightly harder to access,
not impossible). Python's encapsulation is enforced
by convention, not the language. Yet well-written Python
code can be as well-encapsulated as Java code - because
encapsulation is a design discipline, not just a compiler
feature. The Python community's convention (`_internal`)
is respected in the same way that a "staff only" sign is
respected - not because it is a locked door but because
professional developers understand the contract it
signals. Java's `private` keyword is a locked door;
Python's `_field` convention is a sign. Both can be
effective; only one can be circumvented accidentally.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[EXPLAIN]** Explain why a `User` class with a
   `public List<Role> getRoles()` returning the internal
   mutable list breaks encapsulation, and provide two
   different fixes with their trade-offs.

2. **[DEBUG]** Given an `Order` class where total is
   sometimes wrong in production, identify whether the
   root cause is a getter-and-mutate pattern bypassing
   the `addItem()` method, and add an assertion or
   validation to detect it.

3. **[DECIDE]** In a design review, a Java record is
   proposed for a `Money` type: `record Money(long
   cents, String currency) {}`. Is this encapsulated
   enough for a financial service? What invariants (if
   any) does it fail to protect, and how would you
   improve it?

4. **[BUILD]** Refactor an anemic `Ticket` class
   (status, assignee, comments as public getters/setters)
   to a properly encapsulated class that enforces these
   rules: tickets can only be closed if resolved; a
   closed ticket cannot be commented on; only the
   assignee or admin can change status.

5. **[EXTEND]** Explain how the microservices "database
   per service" pattern is an application of the
   encapsulation principle, and describe the specific
   problems that arise when two microservices share a
   database table (the equivalent of making fields public).

---

### 🧠 Think About This Before We Continue

**Q1.** Hibernate's `@Entity` classes often have a
`no-arg constructor` and public setters because JPA
requires them for entity instantiation and hydration.
This seems to violate encapsulation - any caller can
call `setBalance(-1)` on an entity. How do real-world
DDD practitioners handle this tension between JPA's
requirements and domain model encapsulation? What
techniques allow JPA to hydrate entities without
exposing setters to domain code?

*Hint: Consider protected constructors, `@Access(FIELD)`,
and the difference between "JPA can access fields" and
"application code can call setters."*

**Q2.** A `User` class has this method:
```java
public void changePassword(String oldPass, String newPass)
```
A developer suggests adding a `getPasswordHash()` method
for admin users to view password hashes. What are
the encapsulation, security, and design implications
of this suggestion? When (if ever) should you expose
sensitive state through a getter?

*Hint: Consider who needs this data, for what purpose,
and whether there is a method that better captures the
admin's intent without exposing the raw hash.*

**Q3.** In functional programming, data is often
immutable and public - a `struct` with all fields
visible and no setters. Functional programs achieve
correctness through immutability, not encapsulation.
How does immutability provide the same guarantee that
encapsulation provides (state consistency), and what
does each approach give up that the other has?

*Hint: Consider what "invariant" means for an immutable
type. Can an immutable object be in an invalid state?
What does mutation-based encapsulation offer that
immutability cannot?*

---

### 🎯 Interview Deep-Dive

**Q1: What is the difference between encapsulation and
abstraction in OOP?**

*Why they ask:* These terms are commonly conflated.
The question distinguishes candidates who have thought
carefully about OOP fundamentals.

*Strong answer includes:*
- Abstraction: hiding complexity behind an interface;
  the focus is on what something does vs. how. Achieved
  via interfaces and abstract classes.
- Encapsulation: protecting internal state from direct
  external modification; the focus is on who can change
  this state. Achieved via access modifiers.
- They work together: an interface provides the abstraction
  (what); the implementing class's private fields
  provide the encapsulation (protected state)
- Example: `Collections.sort(list)` is an abstraction
  (hides Timsort implementation). `ArrayList`'s `private
  Object[] elementData` is encapsulation (the array
  can only be modified through ArrayList's methods).

**Q2: You're reviewing code where an `Order` class has
getters for all fields and a service that extracts data,
computes, and sets it back. What is the design problem,
and how would you fix it?**

*Why they ask:* Tests recognition of the anemic domain
model anti-pattern and ability to refactor toward
rich domain objects.

*Strong answer includes:*
- Identifies the anemic domain model: data and behavior
  are separated; objects are dumb data containers
- The problem: business logic scattered across multiple
  services; invariants not enforced by the object;
  service must know how to manipulate order's internals
- The fix: move behavior to `Order` - `order.addItem()`,
  `order.confirm()`, `order.calculateTotal()`.
  The service orchestrates (calls methods) but the
  object enforces rules
- Practical example: `if (order.getTotal().compareTo(
  THRESHOLD) > 0) order.setStatus(REVIEW)` becomes
  `order.submitForReview()` - the method encodes the
  business rule
- Testing improvement: tests can verify
  `order.submitForReview()` works without knowing how
  `status` is stored

**Q3: How does encapsulation apply to microservices?
What happens when two services share a database table?**

*Why they ask:* Tests ability to apply OOP principles
to distributed systems design - a common staff-level
interview question.

*Strong answer includes:*
- Encapsulation at service level: each service owns its
  database; others access data only through the service's
  API. The database schema is the private implementation.
- Shared database problem: the schema IS the interface.
  Both services depend on the schema's field names and
  types directly - they are calling `setField()` on
  a shared object with no enforcement
- Consequences: schema changes require coordinating
  deployments of both services simultaneously; no
  service can enforce business rules over "its" data
  independently; testing one service requires a shared
  database state
- Better pattern: Service A owns the table; Service B
  calls Service A's API or subscribes to Service A's
  events to get the data it needs
- Trade-off: API calls add latency; eventual consistency
  via events; but the services can evolve independently
