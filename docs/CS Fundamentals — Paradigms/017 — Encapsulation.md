---
layout: default
title: "Encapsulation"
parent: "CS Fundamentals — Paradigms"
nav_order: 17
permalink: /cs-fundamentals/encapsulation/
number: "17"
category: CS Fundamentals — Paradigms
difficulty: ★★☆
depends_on: Abstraction, Access Modifiers, Cohesion, Classes
used_by: Polymorphism, Coupling, Refactoring, Immutability
tags: #architecture, #pattern, #intermediate, #java
---

# 17 — Encapsulation

`#architecture` `#pattern` `#intermediate` `#java`

⚡ TL;DR — Bundling data and behaviour together while restricting direct access to internal state, forcing interaction through a controlled public interface.

| #17 | category: CS Fundamentals — Paradigms
|:---|:---|:---|
| **Depends on:** | Abstraction, Access Modifiers, Cohesion, Classes | |
| **Used by:** | Polymorphism, Coupling, Refactoring, Immutability | |

---

### 📘 Textbook Definition

**Encapsulation** is the object-oriented principle of bundling related data (fields) and the operations that act on that data (methods) into a single unit (class), while restricting external access to the object's internal state. External code interacts with the object only through its public interface, not by reaching in and manipulating fields directly. This ensures that the object's internal invariants are always preserved — state can only change through controlled, validated mutations. Encapsulation is distinct from data hiding (the mechanism) — encapsulation is the design principle; access modifiers (`private`, `protected`, `public`) are the implementation tool.

---

### 🟢 Simple Definition (Easy)

Encapsulation means keeping your data private and only letting other code access or change it through methods you control. It's like a bank vault — you don't hand over the vault key, you go through the teller.

---

### 🔵 Simple Definition (Elaborated)

Without encapsulation, any part of the code can reach into an object and change its data — often breaking the rules the object is supposed to enforce. Encapsulation says: the object owns its data, and all changes must go through the object's methods. This way, the object can validate, transform, or react whenever its state changes. A `BankAccount` that exposes its `balance` field directly can have `balance = -99999` set from anywhere — ignoring overdraft rules. Encapsulating it behind `deposit()` and `withdraw()` methods ensures the rules are always enforced.

---

### 🔩 First Principles Explanation

**Problem — invariant violation through direct field access:**

An object represents a domain concept that has rules. Direct field access bypasses those rules:

```java
// No encapsulation — anyone can break the invariant
public class Order {
  public List<Item> items;
  public OrderStatus status;
  public double total;
}

// Somewhere in caller code:
order.status = OrderStatus.SHIPPED; // bypasses payment check!
order.items.add(item);              // bypasses stock validation!
order.total = -50.0;                // negative total — illegal!
```

**Constraint — external code must collaborate, but cannot corrupt:**

Other objects need to interact with an Order (read its status, add items, calculate total). But they must never be able to leave the Order in an invalid state.

**Solution — public interface as the only mutation path:**

```java
// WITH encapsulation
public class Order {
  private List<Item> items = new ArrayList<>();
  private OrderStatus status = PENDING;
  private double total = 0.0;

  public void addItem(Item item) {
    if (status != PENDING)
      throw new IllegalStateException("Cannot modify shipped order");
    items.add(item);
    total += item.getPrice(); // consistent with invariant
  }

  public void ship() {
    if (!isPaid())
      throw new IllegalStateException("Cannot ship unpaid order");
    this.status = SHIPPED;
  }

  // Read-only view — no mutation path exposed
  public List<Item> getItems() {
    return Collections.unmodifiableList(items);
  }
}
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT encapsulation:**

```
Without encapsulation (public fields):

  Invariant violation: status = SHIPPED before payment
  → order shipped without payment clearing
  → financial loss

  Shotgun surgery: change internal representation
    items: List → Set (dedup items)
    → must update every caller that touches `order.items`
    → 47 call sites to update

  No-op validation: caller must validate before mutation
    if (order.items != null && order.status == PENDING)
      order.items.add(item);
    → validation duplicated at every call site
    → one missed copy → corrupted state
    → AddressTotalMismatch incident pattern
```

**WITH encapsulation:**

```
→ Invariants enforced in one place — inside the object
→ Implementation can change freely (List → Set)
  without touching any caller
→ Validation is the object's responsibility
  → callers stay clean
→ No "null check before direct field access" noise
→ State transitions are auditable — all go via methods
```

---

### 🧠 Mental Model / Analogy

> Encapsulation is the difference between a **vending machine** and an **open pantry**. An open pantry: anyone reaches in, takes what they want, leaves it in whatever state, puts items back wrong. A vending machine: you interact only through the interface (buttons, slot), the machine enforces its rules (no free snacks), and you never touch the internal mechanism. The machine owns its internal state entirely.

"Open pantry" = public fields — uncontrolled access
"Vending machine" = encapsulated object — controlled interface
"Buttons and slots" = public methods (the interface)
"Internal mechanism" = private fields (hidden state)
"No free snacks rule" = invariants enforced by the object

---

### ⚙️ How It Works (Mechanism)

**Access modifier levels (Java):**

```
┌────────────────────────────────────────────────────────┐
│  ACCESS MODIFIERS                                      │
├────────────────────────────────────────────────────────┤
│  private   → only THIS class                           │
│  (default) → this class + same package                 │
│  protected → this class + package + subclasses         │
│  public    → everywhere                                │
│                                                        │
│  Rule of thumb: start with private, widen only when    │
│  there is a specific, justified reason                 │
└────────────────────────────────────────────────────────┘
```

**Tell, don't ask — the encapsulation behaviour principle:**

```java
// BAD: asking for data, then acting on it externally
// Violates: "don't talk to strangers" (Law of Demeter)
double discount = priceCalculator.getBasePrice()
    * customer.getMembershipTier().getDiscountRate();

// GOOD: tell the object to execute behaviour
double finalPrice = priceCalculator
    .calculateFinalPrice(order, customer);
// Object coordinates internally — caller stays ignorant
```

**Immutable encapsulation — the strongest form:**

```java
// Fully encapsulated, immutable value object
public final class Money {
  private final BigDecimal amount;
  private final Currency currency;

  public Money(BigDecimal amount, Currency currency) {
    if (amount.scale() > 2)
      throw new IllegalArgumentException("Max 2 decimal places");
    this.amount   = amount;
    this.currency = currency;
  }

  // Returns new object — never mutates this
  public Money add(Money other) {
    if (!this.currency.equals(other.currency))
      throw new IllegalArgumentException("Currency mismatch");
    return new Money(this.amount.add(other.amount), currency);
  }

  // Read-only accessors only
  public BigDecimal getAmount()  { return amount; }
  public Currency getCurrency()  { return currency; }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Access Modifiers (private, protected, public)
(the tool)
        ↓
  ENCAPSULATION  ← you are here
  (the principle: own your state, control mutations)
        ↓
  Enables:
  ├── Invariant enforcement (rules always upheld)
  ├── Implementation freedom (change internals freely)
  ├── Cohesion (data + behaviour in one unit)
  └── Polymorphism (subclasses override behaviour,
        not fields — because fields are private)
        ↓
  Violated by:
  Public fields, getters for mutable state,
  anemic domain model, Law of Demeter violations
```

---

### 💻 Code Example

**Example 1 — Anemic model vs rich encapsulated model:**

```java
// BAD: anemic domain model — data bag with no behaviour
public class Account {
  public double balance;       // public — anyone can set
  public boolean locked;
  public List<Transaction> transactions;
}

// Caller: must know rules → duplicated everywhere
if (!account.locked && amount > 0) {
  account.balance -= amount;
  account.transactions.add(new Transaction(-amount));
}

// GOOD: rich encapsulated model
public class Account {
  private double balance;
  private boolean locked;
  private final List<Transaction> transactions = new ArrayList<>();

  public void withdraw(double amount) {
    if (locked) throw new AccountLockedException();
    if (amount <= 0) throw new IllegalArgumentException();
    if (balance < amount) throw new InsufficientFundsException();
    balance -= amount;
    transactions.add(Transaction.debit(amount));
  }

  public double getBalance() { return balance; }
  public List<Transaction> getTransactions() {
    return List.copyOf(transactions); // defensive copy
  }
}
```

**Example 2 — Defensive copy for mutable return:**

```java
// BAD: exposes internal mutable list — callers can corrupt state
public List<Item> getItems() {
  return this.items; // returned reference IS the internal list
}
// Caller: order.getItems().clear(); → corrupts order!

// GOOD: return unmodifiable view or copy
public List<Item> getItems() {
  return Collections.unmodifiableList(items);
  // or: return List.copyOf(items); // Java 10+
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Encapsulation = having private fields and getters/setters | Getters/setters that directly expose private fields break encapsulation just as much as public fields. Encapsulation means behaviour, not just visibility modifiers |
| Encapsulation is only about data hiding | Encapsulation bundles *behaviour* with data — the behaviour enforces invariants. Data hiding alone (without behaviour) is just access control |
| Records/DTOs should be encapsulated | Data-transfer objects are intentionally anemic — they carry data, not behaviour. Encapsulation applies to domain objects, not data carriers |
| Encapsulation makes code harder to use | Poorly designed encapsulation does. Well-designed encapsulation makes code *easier* — callers just call `withdraw()`, no bookkeeping needed |

---

### 🔥 Pitfalls in Production

**1. The "getter trap" — public getters expose mutable internals**

```java
// BAD: getter returns internal mutable list → leaked reference
public List<LineItem> getLineItems() {
  return lineItems; // caller can call .add(), .clear(), .sort()
}

// BAD: setter lets anyone overwrite entire collection
public void setLineItems(List<LineItem> items) {
  this.lineItems = items; // caller may pass the same list ref
}

// GOOD: controlled mutation through behaviour methods
public void addLineItem(LineItem item) { lineItems.add(item); }
public void removeLineItem(long itemId) { ... }
public List<LineItem> getLineItems() {
  return List.copyOf(lineItems); // immutable snapshot
}
```

**2. Law of Demeter violation uncovering encapsulation breach**

```java
// BAD: talking to strangers — reaches 3 levels deep
double charge = order.getCustomer()
                     .getSubscription()
                     .getMonthlyFee();
// Couples caller to Order, Customer, Subscription internals

// GOOD: ask the object to compute what you need
double charge = order.getMonthlyChargeForCustomer();
// Order delegates internally — caller isolated
```

**3. Mutable aggregate root with exposed child references**

```java
// BAD: cart exposes internal item list directly
@Entity
public class ShoppingCart {
  @OneToMany(cascade = ALL)
  public List<CartItem> items = new ArrayList<>();
  // JPA requires this public? No — use protected
}
// HTTP layer: cartDto.items.clear() → bypasses invariants

// GOOD: use package-private/protected for JPA
@Entity
public class ShoppingCart {
  @OneToMany(cascade = ALL, orphanRemoval = true)
  private List<CartItem> items = new ArrayList<>();

  // JPA protected default constructor only
  protected ShoppingCart() {}

  public void addItem(Product p, int qty) {
    validateQty(qty);
    items.add(new CartItem(p, qty));
  }
}
```

---

### 🔗 Related Keywords

- `Abstraction` — abstraction defines the interface; encapsulation hides the implementation behind it
- `Cohesion` — encapsulation keeps data and the behaviour that operates on it together
- `Coupling` — encapsulation reduces coupling by hiding internal state behind stable interfaces
- `Immutability` — the strongest form of encapsulation; state never changes after construction
- `Polymorphism` — works because subclasses override methods, not fields (which are private)
- `Domain-Driven Design` — rich domain model relies on strong encapsulation of business invariants

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Own your data; expose behaviour not state;│
│              │ enforce invariants inside the object      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ All domain objects; anything that has     │
│              │ rules about how its state can change      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ DTOs / value carriers — these ARE data-   │
│              │ focused; use records or structs instead    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Your data is your business —             │
│              │  don't let the outside world touch it."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Immutability → Value Objects → DDD        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** JPA/Hibernate requires a no-argument constructor and often needs fields to be accessible for lazy-loading proxies. This seems to directly conflict with encapsulation — an ORM framework breaks into your private state. Describe the specific technical mechanisms JPA uses to access private fields (hint: reflection and bytecode enhancement), whether the `@Entity` class itself needs to be aware of this, and how you use access-type configuration and domain-model patterns (Aggregate Root) to maintain *effective* encapsulation while satisfying JPA's requirements.

**Q2.** The "Tell, Don't Ask" principle is the behavioural complement to encapsulation. Yet REST APIs by definition are "ask-heavy" — clients fetch data, then make decisions. Explain the tension between encapsulation-driven OOP design and REST resource design, how the CQRS pattern resolves it architecturally, and describe a specific scenario where violating Tell-Don't-Ask in a REST API layer causes a production race condition or consistency bug.

