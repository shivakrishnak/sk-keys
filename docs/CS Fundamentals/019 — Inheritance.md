---
layout: default
title: "Inheritance"
parent: "Clean Code"
nav_order: 429
permalink: /clean-code/inheritance/
number: "429"
category: Clean Code
difficulty: ★★☆
depends_on: Encapsulation, Abstraction, Polymorphism, Classes
used_by: Polymorphism, Design Patterns, Liskov Substitution Principle, Composition
tags: #architecture, #pattern, #intermediate, #java
---

# 429 — Inheritance

`#architecture` `#pattern` `#intermediate` `#java`

⚡ TL;DR — A mechanism for creating a subtype that reuses and extends a parent type's implementation — powerful but overused; prefer composition when behaviour reuse is the goal.

| #429 | Category: Clean Code | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Encapsulation, Abstraction, Polymorphism, Classes | |
| **Used by:** | Polymorphism, Design Patterns, Liskov Substitution Principle, Composition | |

---

### 📘 Textbook Definition

**Inheritance** is the object-oriented mechanism by which a class (subclass, derived class, child class) acquires the fields and methods of another class (superclass, base class, parent class). Beyond code reuse, inheritance establishes an **is-a subtype relationship** governed by the Liskov Substitution Principle: a subclass must be substitutable for its superclass everywhere without breaking programme correctness. Java supports single class inheritance and multiple interface inheritance. Inheritance is one of three mechanisms for achieving polymorphism (alongside interface implementation) and is often contrasted with composition as a means of code reuse.

---

### 🟢 Simple Definition (Easy)

Inheritance lets a new class take everything from an existing class and add or change specific parts. A `Dog` class inherits from `Animal` — it gets all animal behaviour and adds dog-specific stuff.

---

### 🔵 Simple Definition (Elaborated)

When you extend a class, you get its fields and methods without rewriting them. More importantly, your class becomes a subtype — anywhere the parent is expected, you can use the child. This enables polymorphism: a list of `Animal` objects could hold `Dog`, `Cat`, and `Bird` instances, and calling `speak()` on each responds correctly. But inheritance is often misused for code reuse when the subclass doesn't truly represent a subtype. The guideline is simple: if B is-a A (a Dog IS-AN Animal) — inherit. If B uses-a A — compose instead.

---

### 🔩 First Principles Explanation

**Two distinct uses — and why they shouldn't be conflated:**

```
USE 1: SUBTYPE RELATIONSHIP (correct use)
  Dog is-a Animal → Dog extends Animal
  Guarantees LSP substitutability
  Enables polymorphism — right call dispatched

USE 2: CODE REUSE (often misuse)
  EmailService extends DatabaseConnection
  → "I need DB-connection methods in EmailService"
  → NOT a subtype relationship
  → EmailService IS-A DatabaseConnection? No!
  → Inheritance for convenience = wrong tool
```

**The fragile base class problem:**

```java
// Base class change breaks subclass unexpectedly
class Stack<T> extends ArrayList<T> {
  // "reusing" ArrayList — not truly a subtype
  private int pushCount = 0;
  
  @Override
  public boolean add(T t) { // ArrayList add()
    pushCount++; return super.add(t);
  }
  
  @Override
  public boolean addAll(Collection<? extends T> c) {
    pushCount += c.size(); return super.addAll(c);
  }
}
// But ArrayList.addAll() calls add() internally
// → pushCount incremented twice per element!
// Base class changed internal behaviour → subclass breaks
```

This is the definitive argument for "favour composition over inheritance."

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT inheritance:**

```
Without inheritance (subtyping):

  Polymorphism impossible:
    Can't write List<Animal> containing Dogs and Cats
    → must write separate list per type
    → code duplicated per type

  Template Method Pattern impossible:
    Can't define skeleton algorithm in base class
    and fill in steps in subclass

  Framework extension impossible:
    Spring's HttpServletRequest, JUnit's TestCase
    all require extending base types to hook into
    framework lifecycle
```

**WITH inheritance (used correctly):**

```
→ IS-A relationship expressed clearly in the type system
→ Polymorphism via virtual dispatch
→ Template Method: base defines structure, sub fills steps
→ Framework hooks: extend base class, override callbacks
→ Reuse proven implementations with specific variations
```

---

### 🧠 Mental Model / Analogy

> Inheritance is like a **legal will and estate**. A child inherits the parent's estate (fields, methods). The estate comes with obligations (invariants, LSP). The child can add their own property (new methods/fields) or change how they handle the estate (override). The problem: inheriting a business you don't truly understand — a hidden liability in the estate can bankrupt you (fragile base class problem). Composition is like hiring the expertise of another estate manager without inheriting their liabilities.

"Inheriting the estate" = inheriting fields and methods
"Estate obligations" = LSP — you must honour the parent contract
"Hidden liability" = fragile base class — base change breaks subclass
"Hiring expertise" = composition — use without inheriting liability

---

### ⚙️ How It Works (Mechanism)

**Java inheritance mechanics:**

```java
class Animal {
  protected String name;          // accessible in subclasses
  
  public Animal(String name) {
    this.name = name;
  }
  
  public String speak() { return "..."; }
  public String describe() {
    return name + " says: " + speak(); // virtual call
  }
}

class Dog extends Animal {
  private String breed;
  
  public Dog(String name, String breed) {
    super(name);     // MUST call parent constructor
    this.breed = breed;
  }
  
  @Override
  public String speak() { return "Woof"; }
  // describe() inherited — calls overridden speak()
}

Dog d = new Dog("Rex", "Labrador");
d.describe(); // "Rex says: Woof" — virtual dispatch
```

**Method resolution order:**

```
1. Check subclass for the method
2. Walk up superclass chain until found
3. If Object.toString() reached — use that
4. Interfaces checked after class chain
```

**What is NOT inherited:**

```
✗ Constructors (each class defines its own)
✗ static fields/methods (class-level, not instance)
✗ private fields/methods (encapsulated in parent)
```

---

### 🔄 How It Connects (Mini-Map)

```
Abstraction (interface or abstract class)
+ Encapsulation (private fields in parent)
        ↓
  INHERITANCE  ← you are here
  (extends keyword — subtype + implementation reuse)
        ↓
  Enables: Polymorphism (virtual dispatch)
           Template Method Pattern
           Framework extension points
        ↓
  Gated by: Liskov Substitution Principle
           (subtypes must be substitutable)
        ↓
  Often better replaced by:
  COMPOSITION + DELEGATION
  (has-a relationship, decoupled reuse)
```

---

### 💻 Code Example

**Example 1 — Correct use: is-a relationship:**

```java
// IS-A: SavingsAccount IS-AN Account
abstract class Account {
  protected BigDecimal balance;

  public abstract void applyMonthlyFee();

  public void deposit(BigDecimal amount) {
    validatePositive(amount);
    balance = balance.add(amount);
  }
}

class SavingsAccount extends Account {
  private static final BigDecimal NO_FEE = BigDecimal.ZERO;

  @Override
  public void applyMonthlyFee() {
    // Savings accounts have no fee
    balance = balance.subtract(NO_FEE);
  }
}

class PremiumAccount extends Account {
  @Override
  public void applyMonthlyFee() {
    balance = balance.subtract(new BigDecimal("9.99"));
  }
}
```

**Example 2 — Composition over inheritance for code reuse:**

```java
// BAD: using inheritance for implementation reuse
// EmailNotifier is NOT a LoggingService
class EmailNotifier extends LoggingService {
  public void notify(String msg) {
    log(msg);          // "borrowing" log()
    emailClient.send(msg);
  }
}

// GOOD: compose the dependency instead
class EmailNotifier {
  private final Logger logger; // has-a, not is-a

  public EmailNotifier(Logger logger,
                       EmailClient emailClient) {
    this.logger      = logger;
    this.emailClient = emailClient;
  }

  public void notify(String msg) {
    logger.log(msg);
    emailClient.send(msg);
  }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Inheritance is the primary reuse mechanism in OOP | Composition is generally preferred for reuse. Inheritance is for subtype relationships, not for borrowing useful methods |
| Deep inheritance hierarchies are a sign of good design | Deep hierarchies are fragile. 3+ levels of inheritance is a design smell — each level adds coupling to base class changes |
| Overriding a method fully replaces parent behaviour | The parent method may call other overridable methods internally — override can trigger unexpected parent logic (fragile base class) |
| abstract classes and interfaces serve the same purpose | abstract classes share partial implementation + define template structure; interfaces define pure contracts. Use abstract class for template method; interface for polymorphic type |

---

### 🔥 Pitfalls in Production

**1. The fragile base class in production systems**

```java
// BAD: CountingList extends ArrayList
// — reuse through inheritance, not subtyping
public class CountingList<E> extends ArrayList<E> {
  private int addCount = 0;

  @Override public boolean add(E e) {
    addCount++; return super.add(e);
  }
  @Override public boolean addAll(Collection<? extends E> c) {
    addCount += c.size(); return super.addAll(c);
  }
}

CountingList<Integer> cl = new CountingList<>();
cl.addAll(List.of(1, 2, 3));
cl.getAddCount(); // WRONG: returns 6, not 3
// ArrayList.addAll() internally calls add() 3×
// → addCount incremented 3 times in addAll override
// + 3 times from the internal add() calls = 6

// GOOD: use composition
public class CountingList<E> {
  private final List<E> delegate = new ArrayList<>();
  private int addCount = 0;
  public boolean add(E e) {
    addCount++; return delegate.add(e);
  }
  // delegate every other List method explicitly
}
```

**2. Liskov violation causing runtime polymorphism bugs**

```java
// BAD: ReadOnlyList extends ArrayList but throws on write
class ReadOnlyList<E> extends ArrayList<E> {
  @Override public boolean add(E e) {
    throw new UnsupportedOperationException();
  }
}
// Code that accepts List<E> and calls add() breaks
// → LSP violated: subtype not substitutable

// GOOD: implement List<E> interface only for read methods
// Or: use Collections.unmodifiableList() wrapper
List<Integer> ro = Collections.unmodifiableList(list);
```

---

### 🔗 Related Keywords

- `Polymorphism` — inheritance is one mechanism for achieving subtype polymorphism
- `Composition` — the preferred alternative to inheritance for code reuse
- `Encapsulation` — private fields in parent class are NOT accessible to subclasses
- `Liskov Substitution Principle` — the correctness constraint on inheritance hierarchies
- `Abstract Class` — partially-implemented superclass; defines template skeleton for subclasses
- `Template Method Pattern` — design pattern that makes valid use of inheritance (define skeleton, fill steps)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Use inheritance for IS-A subtype          │
│              │ relationships; use composition for reuse  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ B is truly a subtype of A (LSP holds);   │
│              │ Template Method; framework extension hooks│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Just reusing methods (use composition);  │
│              │ hierarchy deeper than 3 levels; when LSP │
│              │ can't be honoured by the subtype          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Inherit the relationship,                │
│              │  compose the behaviour."                  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Liskov → Composition → Strategy Pattern   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The `java.util.Properties extends Hashtable` and `java.util.Stack extends Vector` are two examples in the Java standard library itself that violate the "favour composition over inheritance" principle. For each, describe: (a) why the is-a claim is false, (b) what specific operations are inherited that should not be on the subtype, and (c) what the correctly designed API would look like using composition — and why the Java designers made the wrong choice historically.

**Q2.** Kotlin's `data class` generates `equals()`, `hashCode()`, `toString()`, and `copy()` automatically. If you extend a data class with another data class, the generated `equals()` breaks transitivity — `a.equals(b)` may be true but `b.equals(a)` false. Explain exactly why this happens at the JVM level (hint: `equals()` checks the runtime class), why this makes data class inheritance violate the equals contract, and what Kotlin forces you to do as a design consequence.

