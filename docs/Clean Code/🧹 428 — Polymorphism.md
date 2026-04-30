---
number: "428"
category: Clean Code
difficulty: ★★☆
depends_on: Abstraction, Inheritance, Interface
used_by: Strategy Pattern, OCP, Runtime Dispatch
tags: #cleancode #oop #foundational #pattern
---

# 🧹 428 — Polymorphism

`#cleancode` `#oop` `#foundational` `#pattern`

⚡ TL;DR — The ability of different types to be treated uniformly through a shared interface, each responding differently to the same call.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #428         │ Category: Clean Code                 │ Difficulty: ★★☆           │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Depends on:  │ Abstraction, Inheritance, Interface                               │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Used by:     │ Strategy Pattern, OCP, Runtime Dispatch                           │
└─────────────────────────────────────────────────────────────────────────────────┘

---

## 📘 Textbook Definition

Polymorphism allows objects of different classes to be treated uniformly through a shared supertype (interface or abstract class). At runtime, the JVM selects the correct implementation dynamically via virtual dispatch — enabling extensibility without modifying existing code.

---

## 🟢 Simple Definition (Easy)

Polymorphism means **one interface, many implementations**. You call the same method on different objects and each responds in its own way — the right behavior is selected automatically at runtime.

---

## 🔵 Simple Definition (Elaborated)

Polymorphism enables replacing `if-else` / `switch` type-checking chains with a clean type hierarchy. Instead of asking what type something is, you call the same method and let each class decide what to do. This is the mechanism that makes the Open/Closed Principle possible: you extend behavior by adding new types, not by modifying existing code.

---

## 🔩 First Principles Explanation

**The core problem:**
Code littered with type-checking breaks whenever a new type is added — every `if-else` must be found and updated.

**The insight:**
> "Don't ask what type something is — just call the method. Each type knows what to do."

```
// WITHOUT polymorphism: every new type breaks caller code
if (shape instanceof Circle)    drawCircle((Circle) shape);
else if (shape instanceof Square) drawSquare((Square) shape);
// Add Triangle? Must update this everywhere.

// WITH polymorphism: new types added without touching caller
shape.draw();  // each type handles it via override
```

---

## ❓ Why Does This Exist (Why Before What)

Without polymorphism, adding a new type means finding and updating every `if-else` chain that checks for types — a maintenance burden that grows linearly with new types. Polymorphism makes extensions additive (open/closed).

---

## 🧠 Mental Model / Analogy

> Think of a power outlet. A phone charger, laptop charger, or lamp — they all plug into the same outlet (same interface). The outlet just delivers power; each device handles it differently. The outlet code never changes when new devices are invented.

---

## ⚙️ How It Works (Mechanism)

```
Types of polymorphism:

  Subtype (runtime)   -- method overriding; JVM uses vtable dispatch
  Parametric          -- generics: List<T> works uniformly for any T
  Ad-hoc              -- method overloading: same name, different param types

Runtime dispatch (vtable):
  Shape ref = new Circle();
  ref.draw();
  // JVM: look up Circle's vtable -> find Circle.draw() -> execute it
  // Not Shape.draw() — the runtime type wins
```

---

## 🔄 How It Connects (Mini-Map)

```
[Interface / Abstract Class]  <-- contract
           ↓ implemented by
   [ClassA]  [ClassB]  [ClassC]  <-- each provides own behavior
           ↓ called uniformly as
   shape.draw()  --> JVM picks right implementation at runtime
```

---

## 💻 Code Example

```java
// Define the abstraction
interface Shape {
    double area();
    void draw();
}

// Multiple implementations
class Circle implements Shape {
    private final double radius;
    Circle(double r) { this.radius = r; }

    @Override public double area() { return Math.PI * radius * radius; }
    @Override public void draw()   { System.out.println("O  (circle r=" + radius + ")"); }
}

class Rectangle implements Shape {
    private final double w, h;
    Rectangle(double w, double h) { this.w = w; this.h = h; }

    @Override public double area() { return w * h; }
    @Override public void draw()   { System.out.println("[] (rectangle " + w + "x" + h + ")"); }
}

// Polymorphic usage — caller doesn't know or care about concrete types
List<Shape> canvas = List.of(new Circle(5), new Rectangle(4, 6), new Circle(2));
for (Shape shape : canvas) {
    shape.draw();                  // runtime dispatch
    System.out.println("Area: " + shape.area());
}

// Adding Triangle? Just implement Shape — zero changes to the loop above.
class Triangle implements Shape { /* ... */ }
```

---

## 🔁 Flow / Lifecycle

```
1. Define interface / abstract class with method contract
        ↓
2. Create concrete classes that implement/override the method
        ↓
3. Caller holds a reference to the interface type
        ↓
4. At runtime: JVM consults vtable, dispatches to actual implementation
        ↓
5. New type added: implement interface — no existing callers change
```

---

## ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Polymorphism requires inheritance | Interfaces (no shared implementation) also give polymorphism |
| Useful only in large systems | Eliminates if-else type chains even in small code |
| Overloading is the main form | Subtype polymorphism (overriding) is the powerful extensibility form |
| It has significant runtime overhead | JVM vtable dispatch is near-zero cost after JIT warmup |

---

## 🔥 Pitfalls in Production

**Pitfall 1: `instanceof` checks defeat polymorphism**
```java
// Bad: caller checking type manually — defeats the purpose
if (shape instanceof Circle) { doCircleThing(circle); }
```
Fix: move the behavior into the class itself via method override; the caller just calls the method.

**Pitfall 2: Fragile Base Class**
When a superclass changes, all subclasses may break in subtle ways.
Fix: favor interfaces over inheritance; design superclasses for extension (`sealed`, `final`, or careful `abstract` design).

**Pitfall 3: Violating LSP**
Overriding a method with behavior inconsistent with the parent contract breaks polymorphism for callers.
Fix: follow the Liskov Substitution Principle — a subtype must be substitutable for its supertype.

---

## 🔗 Related Keywords

- **Abstraction** — polymorphism is how abstraction is fulfilled at runtime
- **Inheritance** — one mechanism for achieving subtype polymorphism
- **Interface** — the cleanest mechanism for polymorphism in Java
- **Strategy Pattern** — classic design pattern built entirely on polymorphism
- **OCP (Open/Closed Principle)** — polymorphism is the primary enabler
- **LSP (Liskov Substitution Principle)** — defines the contract for valid polymorphic substitution

---

## 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ One interface, many implementations; runtime  │
│              │ dispatch selects the right behavior           │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Multiple types share behavior, or type-check  │
│              │ if-else chains are growing                    │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Only 1 implementation exists (no benefit yet) │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Same call, different behavior: the type      │
│              │  decides at runtime, not the caller"          │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Strategy Pattern → OCP → LSP                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 Think About This Before We Continue

**Q1.** What is the difference between compile-time (static) and runtime (dynamic) polymorphism?  
**Q2.** How does the Strategy pattern use polymorphism to replace conditional logic?  
**Q3.** Why does using `instanceof` in a method indicate a missing polymorphism opportunity?

