---
layout: default
title: "Polymorphism"
parent: "CS Fundamentals — Paradigms"
nav_order: 18
permalink: /clean-code/polymorphism/
number: "18"
category: CS Fundamentals — Paradigms
difficulty: ★★☆
depends_on: Inheritance, Encapsulation, Abstraction, Interfaces
used_by: Design Patterns, Strategy Pattern, Open-Closed Principle, Refactoring
tags: #architecture, #pattern, #intermediate, #java
---

# 18 — Polymorphism

`#architecture` `#pattern` `#intermediate` `#java`

⚡ TL;DR — The ability of different types to respond to the same interface in their own way, eliminating type-checking conditionals and enabling open/closed extensibility.

| #18 | category: CS Fundamentals — Paradigms
|:---|:---|:---|
| **Depends on:** | Inheritance, Encapsulation, Abstraction, Interfaces | |
| **Used by:** | Design Patterns, Strategy Pattern, Open-Closed Principle, Refactoring | |

---

### 📘 Textbook Definition

**Polymorphism** (Greek: "many forms") is the OOP principle by which objects of different types can be treated uniformly through a shared interface, with each type providing its own specific implementation of the interface's operations. In Java, polymorphism is achieved through **subtype polymorphism** (method overriding via inheritance or interface implementation) and **parametric polymorphism** (generics). At runtime, the JVM dispatches method calls to the correct implementation via virtual dispatch, enabling code that operates on abstractions to work correctly with any concrete subtype — now and in the future.

---

### 🟢 Simple Definition (Easy)

Polymorphism means different objects respond to the same message in their own way. You send "speak" to a Dog and a Cat — both respond, but differently. You don't need to check which type it is.

---

### 🔵 Simple Definition (Elaborated)

Without polymorphism, you write `if (animal instanceof Dog) ... else if (animal instanceof Cat) ...` every time you want type-specific behaviour. With polymorphism, you call `animal.speak()` and the right implementation runs automatically — determined at runtime based on the actual type. This makes code open to extension: add a `Parrot` class and all existing `animal.speak()` call sites work automatically, without touching them. Polymorphism is the mechanism behind almost every design pattern in the Gang of Four catalogue.

---

### 🔩 First Principles Explanation

**Problem — type-checking explosion:**

Without polymorphism, every operation that varies by type requires an `if-instanceof` chain:

```java
// WITHOUT polymorphism — adds a new type? Add to every switch
void processPayment(Payment p) {
  if (p instanceof CreditCardPayment) {
    processCreditCard((CreditCardPayment) p);
  } else if (p instanceof BankTransferPayment) {
    processBankTransfer((BankTransferPayment) p);
  } else if (p instanceof CryptoPayment) {
    processCrypto((CryptoPayment) p);
    // Adding PayPalPayment? → touch this method + 11 others
  }
}
```

**With polymorphism — the type dispatches itself:**

```java
// WITH polymorphism — adding a new type adds zero changes
interface Payment {
  void process();
}
class CreditCardPayment implements Payment {
  public void process() { /* CC logic */ }
}
class CryptoPayment implements Payment {
  public void process() { /* crypto logic */ }
}

void processPayment(Payment p) {
  p.process(); // ONE line — works for all types
}
// Add PayPalPayment: implement Payment, done
// processPayment() is untouched
```

**Open/Closed Principle is enabled by polymorphism:**

Systems should be open for extension but closed for modification. Polymorphism is *how* you implement OCP — adding new types extends behaviour without modifying existing code.

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT polymorphism:**

```
Without polymorphism:

  Adding a new type:
  → Find every switch/if-instanceof in the codebase
  → Modify each one
  → Miss one → runtime bug

  Real-world cost:
  A payments system with 8 payment methods and
  15 places where type is checked:
  8 × 15 = 120 methods to update for new method
  → 1 engineer × 2 days + QA risk

  "Feature Envy" anti-pattern everywhere:
  External code reaches in to check type and
  perform type-specific operations
```

**WITH polymorphism:**

```
→ Add new type = create new class, implement interface
→ Zero existing code modified
→ New behaviour picked up automatically at all call sites
→ Tests: only write tests for the new type
→ Encapsulation of type-specific behaviour
  in the type itself (high cohesion)
```

---

### 🧠 Mental Model / Analogy

> Polymorphism is like a **universal remote control standard**. Every TV brand (Sony, Samsung, LG) implements the standard: power, volume, channel. Your universal remote sends the same "volume up" command to all of them. Each TV responds in its own way (different IR codes, internal logic). The remote doesn't need to know which TV brand it's talking to — it uses the contract. Add a new TV brand? It implements the standard and works immediately.

"Universal remote" = the calling code (operates on the interface)
"TV standard" = the interface or abstract class
"Each TV brand" = concrete implementation (subclass)
"Volume up command" = polymorphic method call
"New TV brand works immediately" = Open/Closed Principle via polymorphism

---

### ⚙️ How It Works (Mechanism)

**Virtual method dispatch (JVM):**

When a polymorphic method is called on a reference, the JVM looks up the actual type at runtime and dispatches to the correct implementation via the vtable (virtual method table):

```
┌──────────────────────────────────────────────┐
│  JVM VIRTUAL DISPATCH                        │
│                                             │
│  Payment p = new CryptoPayment();           │
│  p.process();                               │
│                                             │
│  1. JVM looks at p's actual type at runtime │
│     → CryptoPayment                         │
│  2. Looks up CryptoPayment's vtable         │
│  3. Calls CryptoPayment.process()           │
│                                             │
│  NOT: Payment.process() (reference type)    │
│  ALWAYS: actual object's type               │
└──────────────────────────────────────────────┘
```

**Three forms in Java:**

```java
// 1. Subtype polymorphism via interface
interface Shape { double area(); }
class Circle implements Shape {
  double area() { return Math.PI * r * r; }
}
class Square implements Shape {
  double area() { return side * side; }
}
// List<Shape> — iterate and call area() on any mix

// 2. Subtype polymorphism via inheritance + override
class Animal { String speak() { return "..."; } }
class Dog extends Animal {
  @Override String speak() { return "Woof"; }
}

// 3. Parametric polymorphism (generics)
<T extends Comparable<T>> T max(T a, T b) {
  return a.compareTo(b) >= 0 ? a : b;
}
// Works for Integer, String, Date, any Comparable
```

---

### 🔄 How It Connects (Mini-Map)

```
Abstraction (interface / abstract class)
        ↓
  POLYMORPHISM  ← you are here
  (many implementations, one interface)
        ↓
  ├── Strategy Pattern: swap algorithms at runtime
  ├── Template Method: define skeleton, vary steps
  ├── Command Pattern: encapsulate actions as objects
  ├── Observer Pattern: multiple receivers, one sender
  └── Factory Pattern: create correct type dynamically
        ↓
  Implements: Open/Closed Principle
  Replaces: instanceof + if-else type dispatch chains
  Enabled by: virtual dispatch (JVM vtable)
```

---

### 💻 Code Example

**Example 1 — Replacing instanceof chain with polymorphism:**

```java
// BAD: type-checking dispatch — fragile, closed for extension
double calculateShipping(Delivery delivery) {
  if (delivery instanceof StandardDelivery) {
    return 5.99;
  } else if (delivery instanceof ExpressDelivery) {
    return 14.99;
  } else if (delivery instanceof DroneDelivery) {
    return 24.99;
  }
  throw new UnsupportedOperationException();
  // Adding new type: modify this method + maybe 10 others
}

// GOOD: polymorphic dispatch
interface Delivery {
  double shippingCost();
}
class StandardDelivery implements Delivery {
  public double shippingCost() { return 5.99; }
}
class ExpressDelivery implements Delivery {
  public double shippingCost() { return 14.99; }
}
class DroneDelivery implements Delivery {
  public double shippingCost() { return 24.99; }
}

double calculateShipping(Delivery delivery) {
  return delivery.shippingCost(); // extensible, no switch
}
```

**Example 2 — Strategy Pattern (polymorphism in action):**

```java
interface SortStrategy<T> {
  List<T> sort(List<T> items);
}

class QuickSort<T extends Comparable<T>>
    implements SortStrategy<T> {
  public List<T> sort(List<T> items) { /* quicksort */ }
}

class MergeSort<T extends Comparable<T>>
    implements SortStrategy<T> {
  public List<T> sort(List<T> items) { /* mergesort */ }
}

class DataProcessor<T extends Comparable<T>> {
  private final SortStrategy<T> strategy;

  public DataProcessor(SortStrategy<T> strategy) {
    this.strategy = strategy; // inject any strategy
  }

  public List<T> process(List<T> data) {
    return strategy.sort(data);
  }
}

// Runtime: swap strategy without changing DataProcessor
DataProcessor<Integer> fast =
    new DataProcessor<>(new QuickSort<>());
DataProcessor<Integer> stable =
    new DataProcessor<>(new MergeSort<>());
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Polymorphism requires inheritance | Interface-based polymorphism (Java interfaces, Go interfaces) requires no inheritance — just shared contract implementation |
| Polymorphism is always resolved at runtime | Compile-time polymorphism (overloading, generics) is resolved at compile time; runtime polymorphism (virtual dispatch) is resolved at call time |
| The Liskov Substitution Principle is just about inheritance | LSP defines when polymorphism is *correct*: a subtype must be substitutable for its base type without breaking programme correctness |
| instanceof checks always mean bad code | Sometimes type inspection is necessary (serialisation, logging, generic framework code). The smell is type-checking to vary *behaviour* — polymorphism replaces that |

---

### 🔥 Pitfalls in Production

**1. Violating Liskov Substitution — broken polymorphism**

```java
// BAD: subclass violates LSP — can't be substituted
class Rectangle {
  protected int width, height;
  public void setWidth(int w)  { this.width  = w; }
  public void setHeight(int h) { this.height = h; }
  public int area() { return width * height; }
}

class Square extends Rectangle {
  // Square must keep sides equal — violates Rectangle contract
  @Override public void setWidth(int w) {
    this.width = this.height = w; // breaks caller assumption
  }
}

Rectangle r = new Square();
r.setWidth(5); r.setHeight(3);
r.area(); // caller expects 15, gets 9 → LSP violated
// Fix: Square should NOT extend Rectangle
```

**2. Overusing inheritance for polymorphism — prefer composition**

```java
// BAD: deep inheritance for variation
class BaseReport {
  void generate() { fetchData(); format(); output(); }
}
class PdfReport extends BaseReport { /* ... */ }
class ExcelReport extends PdfReport { /* wrong */ }

// GOOD: compose behaviours via interfaces
interface DataFetcher  { ReportData fetch(); }
interface ReportFormatter { String format(ReportData d); }
interface ReportOutput  { void output(String content); }

class ReportGenerator {
  ReportGenerator(DataFetcher f, ReportFormatter fmt,
                  ReportOutput out) { ... }
}
```

---

### 🔗 Related Keywords

- `Inheritance` — one mechanism for achieving subtype polymorphism
- `Abstraction` — the interface that makes polymorphic dispatch possible
- `Encapsulation` — type-specific state stays hidden; polymorphism exposes only behaviour
- `Strategy Pattern` — the classic design pattern that uses polymorphism to parameterise algorithms
- `Open-Closed Principle` — "open for extension, closed for modification" — enabled by polymorphism
- `Liskov Substitution Principle` — defines correctness of polymorphic hierarchies

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ One interface, many implementations;      │
│              │ caller code never needs to know the type  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Varying behaviour by type; replacing      │
│              │ instanceof chains; enabling new types     │
│              │ without modifying existing code           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Forced to use instanceof after anyway     │
│              │ → the abstraction is probably wrong       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Talk to the interface, not the type —    │
│              │  the right code runs itself."             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Strategy Pattern → OCP → Liskov           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** V8 (JavaScript) and HotSpot (JVM) both use **inline caching** to optimise polymorphic call sites. Explain what an inline cache is, how it makes monomorphic calls fast and what happens to performance when a call site becomes **megamorphic** (> 4 types). Describe the specific code pattern in a large-scale system that accidentally turns a hot polymorphic call site megamorphic — and how a profiler would reveal this deoptimisation.

**Q2.** The Visitor pattern is often described as "double dispatch" — a way to achieve polymorphic behaviour when Java's single dispatch isn't enough. Explain what single dispatch means, give a concrete example where it forces you back to instanceof checks despite having polymorphism, and trace through how the Visitor pattern uses two levels of virtual dispatch to restore type safety without a single instanceof — including the trade-off that makes Visitor unsuitable when new types are added frequently.

