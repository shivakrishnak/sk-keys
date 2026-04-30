---
number: "427"
category: Clean Code
difficulty: ★☆☆
depends_on: Abstraction, Class Design
used_by: Cohesion, Information Hiding, Invariants
tags: #cleancode #oop #foundational
---

# 427 — Encapsulation

`#cleancode` `#oop` `#foundational`

⚡ TL;DR — Bundling data and the methods that operate on it together, while restricting direct access to the internal state.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #427         │ Category: Clean Code                 │ Difficulty: ★☆☆           │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Depends on:  │ Abstraction, Class Design                                         │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Used by:     │ Cohesion, Information Hiding, Invariants                          │
└─────────────────────────────────────────────────────────────────────────────────┘

---

## 📘 Textbook Definition

Encapsulation is the OOP principle of bundling data (fields) and the behavior that operates on it (methods) into a single unit (class), and controlling access to the internal state through visibility modifiers. It enforces invariants by ensuring state can only be changed through controlled methods that validate preconditions.

---

## 🟢 Simple Definition (Easy)

Encapsulation means **keeping the inside of a class private and only allowing access through defined doors (methods)**. It prevents external code from putting the object into an invalid state.

---

## 🔵 Simple Definition (Elaborated)

Without encapsulation, any code anywhere can read and modify an object's fields directly — creating invalid states, hard-to-find bugs, and fragile code. Encapsulation enforces invariants by putting all state changes through methods that validate preconditions before mutating data.

---

## 🔩 First Principles Explanation

**The core problem:**
If fields are public, anyone can set `name = null`, `age = -5`, `balance = -1000000`. Invariants cannot be enforced from outside.

**The insight:**
> "An object should be responsible for maintaining its own invariants. External code should not be able to put it into an invalid state."

```
// No encapsulation: anyone can corrupt state
public int balance;   // balance = -999999 is valid from outside

// Encapsulated: invariants enforced inside
private int balance;
public void withdraw(int amount) {
    if (amount > balance) throw new InsufficientFundsException();
    balance -= amount;
}
```

---

## ❓ Why Does This Exist (Why Before What)

Without encapsulation, objects cannot enforce the rules about what values they hold. Every caller must remember to validate — and eventually someone will forget, leading to data corruption and production incidents.

---

## 🧠 Mental Model / Analogy

> Think of a vending machine. You interact with it through buttons and a coin slot — the internal mechanism is completely hidden. You cannot directly grab items from the shelf or reach into the cash box. The machine controls its own state and enforces its own rules.

---

## ⚙️ How It Works (Mechanism)

```
Visibility levels in Java (most restrictive to least):

  private    --> only this class can access
  (package)  --> this class + same package
  protected  --> this class + package + subclasses
  public     --> anyone

The rule of thumb: make everything as private as possible.
Only expose what callers strictly need via public methods.
```

---

## 🔄 How It Connects (Mini-Map)

```
     [External Code]
           ↓ only via public methods
   [Setter/Getter with Validation]
           ↓ controls access to
     [private fields]  <-- invariants enforced here
```

---

## 💻 Code Example

```java
// BAD — no encapsulation, state can be corrupted externally
class BankAccount {
    public int balance;  // anyone can write: account.balance = -999
    public String owner;
}

// GOOD — encapsulated; state protected by invariants
class BankAccount {
    private int balance;          // hidden
    private final String owner;   // immutable

    public BankAccount(String owner, int initialBalance) {
        if (initialBalance < 0) throw new IllegalArgumentException("Negative balance");
        if (owner == null || owner.isBlank()) throw new IllegalArgumentException("Owner required");
        this.owner = owner;
        this.balance = initialBalance;
    }

    public void deposit(int amount) {
        if (amount <= 0) throw new IllegalArgumentException("Amount must be positive");
        balance += amount;
    }

    public void withdraw(int amount) {
        if (amount <= 0) throw new IllegalArgumentException("Amount must be positive");
        if (amount > balance) throw new IllegalStateException("Insufficient funds");
        balance -= amount;
    }

    // Read-only access — no mutation exposed
    public int getBalance() { return balance; }
    public String getOwner() { return owner; }
}
```

---

## 🔁 Flow / Lifecycle

```
1. Define object's invariants (rules that must always hold)
        ↓
2. Make all fields private
        ↓
3. Validate all inputs in constructors and setters
        ↓
4. Provide controlled access via public methods
        ↓
5. Object can never be put into an invalid state from outside
```

---

## ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Encapsulation = just adding getters/setters | Getter/setter on every field breaks encapsulation |
| private fields = secure | private is about design boundaries, not security |
| Encapsulation = hiding everything | Expose what callers need; hide what they shouldn't change |
| Java Records violate encapsulation | Records are immutable — exposure of immutable data is safe |

---

## 🔥 Pitfalls in Production

**Pitfall 1: Anemic Domain Model**
Classes with all-public getters/setters and no behavior. Any caller can build invalid state externally.
Fix: push behavior INTO the class; remove setters where possible and use constructors with validation.

**Pitfall 2: Returning Mutable Internals**
```java
// Dangerous: caller can add/remove items from the internal collection
public List<Item> getItems() { return items; }

// Safe: return unmodifiable view
public List<Item> getItems() { return Collections.unmodifiableList(items); }
```

**Pitfall 3: Exposing Internal Types in Public API**
Returning a private nested class or a raw internal type exposes implementation details.
Fix: wrap in a DTO, record, or interface that represents the caller's view.

---

## 🔗 Related Keywords

- **Abstraction** — encapsulation implements abstraction for state management
- **Cohesion** — encapsulated classes tend to be more cohesive
- **Immutability** — extreme encapsulation: state is never exposed or changed
- **Information Hiding** — the broader Parnas principle; encapsulation is one mechanism
- **Anemic Domain Model** — the anti-pattern that breaks encapsulation in domain logic

---

## 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Bundle data + behavior; protect state via     │
│              │ controlled access and invariant enforcement   │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Always in OOP — make fields private by default│
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ DTOs / value objects: expose all, change none │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "An object owns its state; callers interact   │
│              │  through methods that enforce the rules"       │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Abstraction → Polymorphism → Immutability     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 Think About This Before We Continue

**Q1.** Why is a class with only public getters/setters considered to have broken encapsulation?  
**Q2.** How do Java Records handle encapsulation differently from regular mutable classes?  
**Q3.** What is the difference between encapsulation and information hiding?

