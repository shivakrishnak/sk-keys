---
layout: default
title: "Encapsulation"
parent: "CS Fundamentals — Paradigms"
nav_order: 17
permalink: /cs-fundamentals/encapsulation/
number: "17"
category: CS Fundamentals — Paradigms
difficulty: ★☆☆
depends_on: Object-Oriented Programming (OOP), Abstraction
used_by: Polymorphism, Inheritance, Design Patterns, Information Hiding
tags: #foundational, #architecture, #pattern
---

# 17 — Encapsulation

`#foundational` `#architecture` `#pattern`

⚡ TL;DR — Bundling data and the methods that operate on it into one unit, and restricting direct access to internal state through access modifiers.

| #17             | Category: CS Fundamentals — Paradigms                          | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------------------------------- | :-------------- |
| **Depends on:** | Object-Oriented Programming (OOP), Abstraction                 |                 |
| **Used by:**    | Polymorphism, Inheritance, Design Patterns, Information Hiding |                 |

---

### 📘 Textbook Definition

**Encapsulation** is an OOP principle in which an object's internal state (fields) and implementation details are bundled within the class and shielded from direct external access via access modifiers (`private`, `protected`, `public`). External code interacts with the object only through its public interface (methods). This enforces _information hiding_: callers cannot depend on internal representation details, allowing the implementation to change without breaking callers, and protecting invariants that the object must maintain.

---

### 🟢 Simple Definition (Easy)

Encapsulation means an object keeps its data private and only allows the outside world to interact with it through controlled methods — like a bank that holds your money but only lets you access it through a teller or ATM.

---

### 🔵 Simple Definition (Elaborated)

Without encapsulation, any code anywhere could read and modify an object's internal data directly — breaking any rules the object tries to maintain. Encapsulation solves this by making fields `private` and exposing only controlled methods. A `BankAccount` that exposes a public `balance` field can have its balance set to -1 billion by any code at any time. A properly encapsulated account exposes only `deposit()` and `withdraw()` — both of which enforce the rule that balance cannot go negative. The data and the rules governing it live together in the same class, protected from outside interference.

---

### 🔩 First Principles Explanation

**The problem: unrestricted access to shared data leads to broken invariants.**

Imagine a `User` class storing an email address as a plain `String` field. Without encapsulation:

```java
// No encapsulation — public field
class User {
    public String email; // anyone can set anything
}

// Anywhere in the codebase:
user.email = "not-an-email"; // invalid, but nothing stops it
user.email = null;           // breaks all downstream null checks
user.email = "";             // passes through to the DB
```

Every piece of code that _touches_ the email field must independently validate it. Change the validation rule — update it in 50 places.

**The constraint:** an object's data and the rules governing it belong together.

**The insight:** if data can only be changed through _methods_, those methods are the single enforcement point for all rules.

```java
// Encapsulated — private field, controlled access
class User {
    private String email;

    public void setEmail(String email) {
        // Rules enforced once, here, for all callers
        if (email == null || !email.contains("@")) {
            throw new IllegalArgumentException("Invalid email");
        }
        this.email = email.toLowerCase().trim();
    }

    public String getEmail() {
        return email; // callers read but cannot directly mutate
    }
}
```

Now, changing the email validation rule (e.g., adding domain whitelist) requires editing exactly one method.

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Encapsulation:

```java
// Public fields — anyone can corrupt state
class BankAccount {
    public double balance;
    public String owner;
    public List<Transaction> history;
}

// Anywhere:
account.balance = -50000.0; // negative balance — no protection
account.history.clear();    // audit trail deleted — no protection
account.owner = null;       // invariant broken — no protection
```

What breaks without it:

1. Object invariants cannot be enforced — invalid states are reachable.
2. Changing the internal representation (e.g., `balance` from `double` to `BigDecimal`) breaks every direct field access across the codebase.
3. Adding a rule (e.g., "log all balance changes") requires touching every assignment site.
4. Thread safety is impossible — concurrent writes to public fields cause race conditions.

WITH Encapsulation:
→ Invariants are enforced in one place — the class's own methods.
→ Implementation changes are local — callers use the public interface unchanged.
→ Behaviour is predictable — the object controls its own state transitions.
→ Thread safety is achievable — synchronisation applied to methods, not callers.

---

### 🧠 Mental Model / Analogy

> Think of a vending machine. Money and products are inside, inaccessible to you. You interact only through the coin slot, product selection buttons, and the retrieval door. You cannot reach in and take a product without paying, set the machine's internal price, or add coins directly to the register. The machine's rules (pay first, then dispense) are enforced by its physical enclosure — not by trusting users to behave. The internal mechanism can be completely redesigned as long as the interface (coins in, product out) stays the same.

"Coins slot and product buttons" = public methods
"Products and coin register inside the machine" = private fields
"Reaching directly into the machine" = direct field access (prevented)
"Redesigning the internal mechanism" = refactoring private implementation
"The machine's pricing rule" = invariant enforced by methods

---

### ⚙️ How It Works (Mechanism)

**Java access modifiers — four levels of visibility:**

```
┌──────────────────────────────────────────────────────┐
│         Java Access Modifiers                        │
│                                                      │
│  private   │ Same class only                         │
│  (default) │ Same package                            │
│  protected │ Same package + subclasses               │
│  public    │ Anywhere                                │
└──────────────────────────────────────────────────────┘
```

**Canonical encapsulated class:**

```java
public class Temperature {
    private final double celsius; // immutable — no setter needed

    public Temperature(double celsius) {
        if (celsius < -273.15) {
            throw new IllegalArgumentException(
                "Below absolute zero: " + celsius);
        }
        this.celsius = celsius;
    }

    public double getCelsius() { return celsius; }

    public double getFahrenheit() {
        return celsius * 9.0 / 5.0 + 32; // derived — no stored state
    }

    // Implementation can add Kelvin support without changing the contract
}
```

**Encapsulation + immutability (stronger guarantee):**

```java
// Immutable classes: all fields final, no setters
// No synchronisation needed — state cannot change after construction
public final class Money {
    private final long cents;        // final: immutable after construction
    private final Currency currency;

    public Money(long cents, Currency currency) {
        this.cents    = requireNonNull(cents);
        this.currency = requireNonNull(currency);
    }

    public Money add(Money other) {
        if (!currency.equals(other.currency))
            throw new CurrencyMismatchException();
        return new Money(cents + other.cents, currency); // new object
    }
    // No setters — state never changes
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Object-Oriented Programming
        │
        ▼
Encapsulation  ◄──── (you are here)
        │
        ├─────────────────────────────────────────┐
        ▼                                         ▼
Abstraction                               Information Hiding
(hides complexity via interface)          (hides representation)
        │                                         │
        ▼                                         ▼
Polymorphism                              Immutability
(multiple implementations per interface)  (fields final → no mutation)
        │
        ▼
Design Patterns
(Decorator, Proxy — wrap and protect state)
```

---

### 💻 Code Example

**Example 1 — Enforcing invariants through encapsulation:**

```java
// BAD: public fields allow broken state
class Order {
    public List<Item> items;
    public double total;
}
// Caller can set total = 0.0 without changing items — broken

// GOOD: encapsulate state, derive values from methods
class Order {
    private final List<Item> items = new ArrayList<>();

    public void addItem(Item item) {
        Objects.requireNonNull(item, "item cannot be null");
        items.add(item);
    }

    public double getTotal() {
        // Always computed from items — cannot be wrong
        return items.stream().mapToDouble(Item::getPrice).sum();
    }

    public List<Item> getItems() {
        return Collections.unmodifiableList(items); // prevent external mutation
    }
}
```

**Example 2 — Refactoring internal representation without breaking callers:**

```java
// Version 1: balance stored as double
class Account {
    private double balance;
    public double getBalance() { return balance; }
}

// Version 2: internal representation changes to BigDecimal for precision
// Callers using getBalance() are UNAFFECTED
class Account {
    private BigDecimal balance; // changed internally
    public double getBalance() {
        return balance.doubleValue(); // same public return type
    }
}
// Zero breaking changes — encapsulation protected the callers
```

**Example 3 — Builder pattern for complex encapsulated construction:**

```java
// Encapsulate a multi-field object with validation at construction
class ConnectionConfig {
    private final String host;
    private final int port;
    private final int timeoutMs;
    private final boolean tlsEnabled;

    private ConnectionConfig(Builder b) {
        this.host       = requireNonNull(b.host, "host required");
        this.port       = b.port > 0 ? b.port : 5432;
        this.timeoutMs  = b.timeoutMs > 0 ? b.timeoutMs : 5000;
        this.tlsEnabled = b.tlsEnabled;
    }

    public static class Builder {
        private String host;
        private int port = 5432;
        private int timeoutMs = 5000;
        private boolean tlsEnabled = true;
        // setters for builder fields...
        public ConnectionConfig build() { return new ConnectionConfig(this); }
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                                                                                                        |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Encapsulation = getters and setters          | A class with a private field and a trivial getter+setter achieves nothing — external code still effectively controls the field. Real encapsulation means methods enforce rules                                 |
| Encapsulation is only about access modifiers | Access modifiers are the mechanism; information hiding and invariant protection are the goal. A `public` method that returns a mutable internal collection breaks encapsulation despite using `private` fields |
| Encapsulation and abstraction are the same   | Abstraction defines the interface (what is visible); encapsulation hides implementation (what is invisible). They work together but address different concerns                                                 |
| Returning a List from a getter is safe       | Returning a mutable internal `List` from a getter allows callers to mutate it directly — use `Collections.unmodifiableList()` or return a copy                                                                 |

---

### 🔥 Pitfalls in Production

**Returning mutable internal collections from getters**

```java
// BAD: internal list exposed — callers mutate it directly
class OrderService {
    private List<Order> pendingOrders = new ArrayList<>();

    public List<Order> getPendingOrders() {
        return pendingOrders; // caller can: getPendingOrders().clear()!
    }
}

// GOOD: return a defensive copy or unmodifiable view
public List<Order> getPendingOrders() {
    return Collections.unmodifiableList(pendingOrders);
}
```

---

**Anemic domain model — all data, no behaviour**

```java
// BAD: plain data holder with no encapsulated rules
class Account {
    private double balance;
    public double getBalance() { return balance; }
    public void setBalance(double balance) { this.balance = balance; } // no rules!
}
// Business logic scattered across services:
if (account.getBalance() >= amount) {
    account.setBalance(account.getBalance() - amount); // duplicated everywhere
}

// GOOD: behaviour lives inside the class
class Account {
    private double balance;
    public void withdraw(double amount) {
        if (amount > balance) throw new InsufficientFundsException();
        balance -= amount; // rule enforced here, once
    }
}
```

---

**Thread-safety gap from unsynchronised compound operations**

```java
// BAD: two-step read-modify-write is not atomic
class Counter {
    private int count = 0;
    public int getCount() { return count; }
    public void increment() { count++; } // not thread-safe!
}

// GOOD: encapsulate the operation atomically
class Counter {
    private final AtomicInteger count = new AtomicInteger(0);
    public int getCount() { return count.get(); }
    public int increment() { return count.incrementAndGet(); }
}
```

---

### 🔗 Related Keywords

- `Abstraction` — defines what is visible (the interface); encapsulation hides what is not
- `Object-Oriented Programming (OOP)` — the paradigm in which encapsulation is a foundational pillar
- `Polymorphism` — relies on encapsulated implementations behind a shared interface
- `Immutability` — the strongest form of encapsulation: final fields, no setters, no mutation possible
- `Information Hiding` — the design principle encapsulation implements: hide what callers do not need to know
- `Anemic Domain Model` — the anti-pattern where classes have no behaviour, breaking encapsulation
- `Builder Pattern` — enables encapsulated, validated object construction without telescoping constructors

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Bundle data and behaviour together;       │
│              │ expose only what callers need, hide the   │
│              │ rest behind access modifiers.             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — every class should encapsulate   │
│              │ its state and enforce its own invariants  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Trivial getters/setters that add no rules │
│              │ are not encapsulation — they are noise    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "An object owns its state. If anyone can  │
│              │ change it, nobody can trust it."          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Abstraction → Information Hiding →        │
│              │ Immutability → Design Patterns →          │
│              │ Domain-Driven Design                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A `User` entity in a Spring Boot application has `@Getter @Setter` Lombok annotations on all fields, including `passwordHash`, `roles`, and `accountLocked`. The `UserService` class enforces business rules (password complexity, role assignment approval) before setting these fields. Identify exactly what encapsulation principle this design violates, and describe a refactoring that preserves the business rules without relying on the service layer to police the entity's state.

**Q2.** Java records (`record Point(int x, int y) {}`) are often described as "encapsulated." A record's fields are private and final, and getters are generated automatically with no setters. However, if the record contains a `List<String>` field, encapsulation has a critical weakness. Describe exactly what the weakness is, demonstrate the exploit, and explain whether Java records can achieve true encapsulation for mutable component types.
