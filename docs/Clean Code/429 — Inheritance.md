---
layout: default
title: "Inheritance"
parent: "Clean Code"
nav_order: 429
permalink: /clean-code/inheritance/
number: "429"
category: Clean Code
difficulty: ★★☆
depends_on: Polymorphism, Abstraction
used_by: LSP, Composition over Inheritance, Subtype Polymorphism
tags: #cleancode #oop #foundational
---

# 429 — Inheritance

`#cleancode` `#oop` `#foundational`

⚡ TL;DR — A mechanism where a class acquires the properties and behavior of a parent class, establishing an IS-A relationship.

| #429 | Category: Clean Code | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Polymorphism, Abstraction | |
| **Used by:** | LSP, Composition over Inheritance, Subtype Polymorphism | |

---

### 📘 Textbook Definition

Inheritance is the OOP mechanism by which a class (subclass/child) extends another class (superclass/parent), inheriting its fields and methods. It establishes an IS-A relationship and enables subtype polymorphism. Java supports single class inheritance and multiple interface inheritance.

---

### 🟢 Simple Definition (Easy)

Inheritance means **one class gets the capabilities of its parent for free**, then adds to or customizes them. It's how you say "a Dog IS-A Animal."

---

### 🔵 Simple Definition (Elaborated)

Inheritance creates a compile-time relationship between classes. The subclass IS-A superclass — it can be used anywhere the superclass is expected (Liskov Substitution). However, inheritance is a strong coupling: changing the superclass can break all subclasses. Modern practice: "Favor composition over inheritance" — use inheritance only for genuine, stable IS-A relationships.

---

### 🔩 First Principles Explanation

**The core problem:**
Duplicating methods across multiple similar classes leads to maintenance pain — fix a bug in one, forget the others.

**The insight:**
> "Extract shared behavior into a parent class. Subclasses inherit and specialize."

**But — the trap:**
Inheritance couples the subclass to the superclass's internals forever. Any change to the superclass is risky.

**Modern wisdom:**
- Use **inheritance** when the IS-A relationship is genuine, behavioral, and stable.
- Use **composition** when you just want code reuse without the coupling.

---

### ❓ Why Does This Exist (Why Before What)

Without inheritance, you'd duplicate code across every similar class. But overusing inheritance creates fragile hierarchies where a superclass change silently breaks every subclass below it.

---

### 🧠 Mental Model / Analogy

> Think of an employee hierarchy: Manager IS-A Employee — every Manager IS genuinely an Employee with all Employee capabilities. But a ContractEmployee IS-A Employee only for payroll — it should NOT inherit "apply for promotion" behavior. The IS-A must hold for ALL behavior, not just some.

---

### ⚙️ How It Works (Mechanism)

```
Class hierarchy and method resolution:

  Animal                (superclass)
  ├── Dog extends Animal (subclass — inherits speak(), move())
  │   └── Poodle extends Dog (sub-subclass — overrides speak())
  └── Cat extends Animal  (subclass — overrides speak())

Method Resolution Order (MRO):
  ref.speak() where ref is Poodle:
    1. Does Poodle have speak()? Yes -> use it
    2. No? Check Dog.speak()
    3. No? Check Animal.speak()
    4. No? Check Object methods
```

---

### 🔄 How It Connects (Mini-Map)

```
     [Animal]  <-- superclass
        ↓ extends
     [Dog]  <-- inherits Animal methods; can override
        ↓ extends
     [Poodle]  <-- inherits + overrides; IS-A Dog IS-A Animal
```

---

### 💻 Code Example

```java
// Superclass
class Vehicle {
    protected int speedKph;

    void accelerate(int delta) { speedKph += delta; }
    void brake(int delta)      { speedKph = Math.max(0, speedKph - delta); }

    String status() {
        return "Speed: " + speedKph + " kph";
    }
}

// Subclass — IS-A Vehicle
class ElectricCar extends Vehicle {
    private int batteryPercent = 100;

    void charge(int percent) {
        batteryPercent = Math.min(100, batteryPercent + percent);
    }

    @Override
    String status() {                              // override
        return super.status() + " | Battery: " + batteryPercent + "%";
    }
}

// Polymorphism via inheritance
Vehicle v = new ElectricCar();
v.accelerate(60);
System.out.println(v.status());  // ElectricCar.status() called — "Speed: 60 kph | Battery: 100%"
```

---

### 🔁 Flow / Lifecycle

```
1. Subclass declared: class Dog extends Animal
        ↓
2. Subclass gets all non-private fields and methods of Animal
        ↓
3. Subclass can OVERRIDE methods (runtime polymorphism)
        ↓
4. Subclass can EXTEND with new methods unique to it
        ↓
5. super.method() accesses parent's implementation when needed
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Use inheritance for code reuse | Prefer composition for reuse; inheritance is for IS-A |
| Deep hierarchies = good OOP | Deep hierarchies = fragile, hard-to-understand code |
| Override anything you want | Obey LSP or you silently break polymorphism for callers |
| Java has no multiple inheritance | No multi-class inheritance; but interfaces with default methods allow multiple behavior sources |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Fragile Base Class**
Changing a protected or public method in a superclass silently breaks all subclasses.
Fix: minimize protected methods; favor composition; design superclasses explicitly for extension.

**Pitfall 2: Overriding for Convenience, Not Behavior**
Overriding a method just to change a side effect or remove behavior violates LSP.
Fix: if the subclass cannot satisfy the parent's full contract, it should not extend it — use composition instead.

**Pitfall 3: Deep Hierarchy (> 3 levels)**
More than 2-3 levels of inheritance becomes very hard to trace and debug.
Fix: flatten hierarchies; use interfaces + composition to share behavior without deep coupling.

---

### 🔗 Related Keywords

- **Polymorphism** — inheritance enables subtype (runtime) polymorphism
- **LSP (Liskov Substitution Principle)** — defines the correct use of inheritance
- **Composition over Inheritance** — preferred modern alternative for code reuse
- **Abstract Class** — partially implemented superclass designed specifically for extension
- **Fragile Base Class** — the primary pitfall of deep or carelessly designed inheritance
- **super keyword** — access to the parent's implementation from within a subclass

---

### 📌 Quick Reference Card

| #429 | Category: Clean Code | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Polymorphism, Abstraction | |
| **Used by:** | LSP, Composition over Inheritance, Subtype Polymorphism | |

---

### 🧠 Think About This Before We Continue

**Q1.** What is the Fragile Base Class problem and how does marking a class `final` partially address it?  
**Q2.** Why does Java disallow multiple class inheritance, and how do interface default methods partially address this?  
**Q3.** When is it correct to choose composition over inheritance even when a genuine IS-A relationship exists?

