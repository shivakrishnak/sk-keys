---
layout: default
title: "Object-Oriented Programming (OOP)"
parent: "CS Fundamentals — Paradigms"
nav_order: 3
permalink: /cs-fundamentals/object-oriented-programming-oop/
number: "3"
category: CS Fundamentals — Paradigms
difficulty: ★☆☆
depends_on: Imperative Programming, Procedural Programming, Variables, Functions
used_by: Encapsulation, Inheritance, Polymorphism, Abstraction, Design Patterns
tags: #foundational, #architecture, #pattern, #java
---

# 3 — Object-Oriented Programming (OOP)

`#foundational` `#architecture` `#pattern` `#java`

⚡ TL;DR — Organise code into objects that bundle state (fields) and behaviour (methods), modelling the world as interacting entities with identity.

| #3 | Category: CS Fundamentals — Paradigms | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Imperative Programming, Procedural Programming, Variables, Functions | |
| **Used by:** | Encapsulation, Inheritance, Polymorphism, Abstraction, Design Patterns | |

---

### 📘 Textbook Definition

**Object-oriented programming (OOP)** is a programming paradigm that organises software around objects — instances of classes that encapsulate data (fields/attributes) and the operations on that data (methods). The four core pillars are: **encapsulation** (bundling data with behaviour and hiding implementation details), **abstraction** (exposing only relevant interfaces), **inheritance** (deriving new types from existing ones), and **polymorphism** (treating different types uniformly through a common interface). Languages like Java, C++, Python, and C# are primarily OOP languages. OOP models systems as a network of cooperating objects, each responsible for its own state.

---

### 🟢 Simple Definition (Easy)

OOP means modelling your program as a collection of "things" — like a `Car`, a `User`, or an `Order` — where each thing knows its own data and what it can do. A `BankAccount` knows its balance and knows how to deposit and withdraw.

---

### 🔵 Simple Definition (Elaborated)

Before OOP, large programs were tangled webs of global variables and functions. Any function could read or modify any data, making it extremely hard to reason about what changed a value and when. OOP introduced the idea that data and the functions that operate on it should live together in a single unit — the object. A `BankAccount` object owns its `balance` and is the only thing that should change it. Other objects interact with `BankAccount` through a published interface (`deposit()`, `withdraw()`), not by reaching into raw memory. This encapsulation boundary makes large systems manageable because each object is a clear contract: here's what I do, here's what I expose, here's what I hide.

---

### 🔩 First Principles Explanation

**The problem: procedural programs at scale become unmanageable.**

A procedural C program for a banking system might look like:

```c
double balance = 0.0;  // global state
double interestRate = 0.05;
char accountHolder[50] = "Alice";

void deposit(double amount) { balance += amount; }
void applyInterest() { balance *= (1 + interestRate); }
```

This works for one account. For 10,000 accounts, you need 10,000 separate variables — or arrays. Any function can accidentally reach into `balance` of the wrong account. When a bug corrupts a balance, you have no idea which function caused it.

**The OOP insight: bundle state + behaviour + identity together.**

```java
class BankAccount {
    private double balance;       // state — private, protected
    private String owner;

    public void deposit(double amount) {
        if (amount <= 0) throw new IllegalArgumentException();
        this.balance += amount;   // only this class mutates balance
    }

    public double getBalance() { return balance; }
}
```

Now you can have millions of `BankAccount` objects, each with its own independent `balance`. The mutation of `balance` is controlled: only `deposit()` and `withdraw()` can change it. A bug corrupting a balance → blame these two methods, not 500 global functions.

**The four pillars map directly to four problems:**

```
┌─────────────────────────────────────────────────┐
│  OOP Pillar         Problem it solves           │
├─────────────────────────────────────────────────┤
│  Encapsulation    → Uncontrolled state mutation │
│  Abstraction      → Exposing irrelevant detail  │
│  Inheritance      → Code duplication across     │
│                     related types               │
│  Polymorphism     → if-else chains based on type│
└─────────────────────────────────────────────────┘
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT OOP (or other organising principles):**

Large procedural programs suffer from:
- Global state accessible by any function → phantom mutations, impossible-to-track bugs
- No natural way to group related functions and data → spaghetti code
- Code duplication for every new "type" of entity (Car, Truck, Motorcycle all have separate function families)
- No polymorphism → every caller needs to know the exact type being operated on

What breaks without it:
1. Adding a new type of `Payment` (CreditCard vs Crypto) requires adding if-else in every payment-handling function
2. Any function can modify any global variable — debugging requires reading every function in the codebase
3. Scaling to multiple instances of the same conceptual entity (1000 bank accounts) requires complex array indexing

**WITH OOP:**
→ State is localised to objects — a `BankAccount` mutation only happens through `BankAccount` methods
→ New types extend existing behaviour via inheritance or interface implementation
→ Polymorphism lets the same `processPayment(Payment p)` call handle credit cards, crypto, and cash without modification
→ Design Patterns (Strategy, Factory, Observer) provide reusable solutions to recurring OOP design problems

---

### 🧠 Mental Model / Analogy

> OOP is like a **company of employees**, each with a job title, private knowledge, and a published job description. You call the `Accountant` to process your expense report — you don't reach into their filing cabinet yourself. The `SoftwareEngineer` knows how to fix bugs — you don't read their code directly, you create a ticket (call a method). Each employee has a role (class), a specific identity (object instance), and a contract (interface/public API).

"Employee's filing cabinet" = private fields
"Job description / contract" = public interface / methods
"Calling the accountant" = method invocation
"A specific employee" = an object instance
"Job title category" = class

This breaks down at inheritance — real employees are not is-a subtypes of each other. Use the analogy for encapsulation and interface, not for deep inheritance hierarchies.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────┐
│  CLASS vs OBJECT                                │
│                                                 │
│  Class (blueprint):                             │
│    BankAccount { balance, deposit(), withdraw() }│
│                                                 │
│  Objects (instances in heap memory):            │
│    alice: BankAccount { balance=1000.0 }        │
│    bob:   BankAccount { balance=500.0  }        │
│    corp:  BankAccount { balance=99999.0}        │
│                                                 │
│  Each instance has its OWN copy of fields,      │
│  shares the class's method bytecode.            │
└─────────────────────────────────────────────────┘
```

**Method dispatch in Java:**

```java
// Static dispatch (compile-time) — method overloading
class Printer {
    void print(String s) { ... }
    void print(int n) { ... }  // compiler chooses by arg type
}

// Dynamic dispatch (runtime) — polymorphism
abstract class Shape { abstract double area(); }
class Circle extends Shape { double area() { return PI*r*r; } }
class Square extends Shape { double area() { return side*side; } }

Shape s = new Circle(5.0);
s.area(); // JVM looks up Circle's vtable → calls Circle.area()
          // even though s is declared as Shape
```

The JVM uses a **virtual dispatch table (vtable)** per class. When `s.area()` is called, the JVM loads the actual type of `s` at runtime, looks up `area()` in that type's vtable, and jumps to the implementing method. This is the mechanism that makes polymorphism work.

---

### 🔄 How It Connects (Mini-Map)

```
Procedural Programming (functions + data structures)
        ↓
Object-Oriented Programming  ← you are here
        ↓
   ┌────┴────────────────┐
   ↓                     ↓
Four Pillars:        SOLID Principles
  Encapsulation       Design Patterns
  Abstraction         (Strategy, Factory,
  Inheritance          Observer, Decorator...)
  Polymorphism
        ↓
Frameworks: Spring (IoC container manages objects)
            JPA (entities are objects mapped to DB)
```

---

### 💻 Code Example

**Example 1 — Encapsulation: controlled state mutation**
```java
public class BankAccount {
    private double balance;  // private — only this class writes it

    public void deposit(double amount) {
        if (amount <= 0) throw new IllegalArgumentException(
            "Deposit must be positive"
        );
        this.balance += amount;  // class controls own mutation
    }

    public void withdraw(double amount) {
        if (amount > balance) throw new InsufficientFundsException();
        this.balance -= amount;
    }

    public double getBalance() { return balance; }  // read-only access
}
```

**Example 2 — Polymorphism eliminating if-else chains**
```java
// BAD: procedural if-else — must modify every time a new shape is added
double totalArea(List<Object> shapes) {
    double total = 0;
    for (Object s : shapes) {
        if (s instanceof Circle c) total += Math.PI * c.radius * c.radius;
        else if (s instanceof Square sq) total += sq.side * sq.side;
        // Add Triangle? Add Rectangle? Edit this function.
    }
    return total;
}

// GOOD: polymorphism — adding Triangle doesn't touch totalArea
interface Shape { double area(); }

class Circle  implements Shape { double area() { return PI*r*r; } }
class Square  implements Shape { double area() { return side*side; } }
class Triangle implements Shape { double area() { return 0.5*b*h; } }

double totalArea(List<Shape> shapes) {
    return shapes.stream().mapToDouble(Shape::area).sum();
}
```

**Example 3 — Inheritance and the is-a contract**
```java
abstract class Animal {
    String name;
    abstract String speak();
    void introduce() {
        System.out.println("I am " + name + " and I say " + speak());
    }
}

class Dog extends Animal {
    String speak() { return "Woof"; }
}

class Cat extends Animal {
    String speak() { return "Meow"; }
}

// Works for any Animal subtype — open for extension
Animal a = new Dog();
a.introduce(); // "I am ... and I say Woof"
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| OOP means using classes everywhere | OOP is about meaningful encapsulation of state and behaviour; creating a class `StringHelper` with one static method is not OOP |
| Inheritance is the most important OOP pillar | Inheritance creates tight coupling; composition is usually preferred for flexibility (favour composition over inheritance) |
| Private fields make code safe | Private fields prevent accidental external mutation but don't prevent bugs inside the class; thread safety still requires synchronisation |
| OOP and functional programming are mutually exclusive | Scala, Kotlin, and Java 8+ combine both; a class can have immutable fields and pure methods |
| More classes = better OOP design | Anemic domain model anti-pattern: classes with only getters/setters and logic in service classes is procedural code with class syntax |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Anemic domain model — OOP in name only**

```java
// BAD: "OOP" but all logic is in the service, not the entity
class Order {
    private List<Item> items;
    private double total;
    // getters and setters only — no behaviour
}

class OrderService {
    void applyDiscount(Order o, double pct) {
        o.setTotal(o.getTotal() * (1 - pct)); // reaches into Order's state
    }
}
```

```java
// GOOD: rich domain model — behaviour belongs in the object
class Order {
    private final List<Item> items;
    private double total;

    public void applyDiscount(double percentage) {
        if (percentage < 0 || percentage > 1) throw new IllegalArgumentException();
        this.total *= (1 - percentage);
    }
}
```

Anemic models give you OOP syntax with procedural semantics, losing all encapsulation benefits.

**Pitfall 2: Deep inheritance hierarchies creating fragile base class**

```java
// BAD: 5-level hierarchy — changing Animal breaks all subclasses
Animal → Vertebrate → Mammal → DomesticAnimal → Dog
// Adding a new field to Animal requires testing every subclass
```

```java
// GOOD: shallow hierarchy + composition
class Dog {
    private final SoundBehavior sound = new BarkBehavior();
    private final MovementBehavior move = new WalkBehavior();
    // Behaviour injected, not inherited
}
```

Deep inheritance creates the "fragile base class" problem: changing a parent class breaks all children in unexpected ways.

**Pitfall 3: Exposing mutable internals via getters**

```java
// BAD: returning internal mutable list — caller can corrupt state
class Team {
    private List<Player> players = new ArrayList<>();
    public List<Player> getPlayers() { return players; } // reference!
}
// Caller does: team.getPlayers().clear(); → Team's state corrupted
```

```java
// GOOD: return defensive copy or unmodifiable view
public List<Player> getPlayers() {
    return Collections.unmodifiableList(players);
}
```

---

### 🔗 Related Keywords

- `Encapsulation` — hiding implementation details within an object boundary
- `Abstraction` — exposing only the relevant interface, hiding complexity
- `Inheritance` — deriving new classes from existing ones to reuse behaviour
- `Polymorphism` — treating different types uniformly through a shared interface
- `Composition over Inheritance` — preferred OOP design choice; build behaviour by composing objects
- `Design Patterns` — reusable OOP solutions (Strategy, Factory, Observer, Decorator)
- `SOLID Principles` — five design principles for maintainable OOP code

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Bundle state + behaviour in objects with  │
│              │ clear boundaries and controlled access    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Modelling real-world entities; managing   │
│              │ complex state machines; large codebases   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple data transformations (use FP);     │
│              │ avoid deep inheritance hierarchies        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Each object owns its state and publishes │
│              │  a contract — not a window into its guts."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Encapsulation → Polymorphism → SOLID →    │
│              │ Design Patterns → Composition over Inherit│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Java's `ArrayList` extends `AbstractList` which extends `AbstractCollection`. This 3-level inheritance hierarchy means that when the `ArrayList.iterator()` method returns a `ListItr` (a private inner class), the iterator's behaviour is partly defined in `AbstractList`. If Sun/Oracle wanted to optimise `ArrayList.remove()` in a way that invalidates the iterator contract defined in `AbstractList`, what would break and how? What does this reveal about the "fragile base class" problem at the scale of the Java standard library?

**Q2.** Spring's IoC container manages object lifecycles and dependencies, treating objects as beans. Spring itself is an OOP framework managing OOP objects. But Spring encourages using interfaces heavily, keeping beans stateless where possible, and injecting dependencies rather than inheriting them. Is this "good OOP" or is it a reaction against OOP's limitations? Identify two specific OOP anti-patterns that Spring's design explicitly works around.

