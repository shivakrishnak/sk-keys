---
layout: default
title: "Polymorphism"
parent: "CS Fundamentals — Paradigms"
nav_order: 18
permalink: /cs-fundamentals/polymorphism/
number: "18"
category: CS Fundamentals — Paradigms
difficulty: ★☆☆
depends_on: Object-Oriented Programming (OOP), Abstraction, Encapsulation, Inheritance
used_by: Design Patterns, Dependency Injection, Interfaces, Functional Programming
tags: #foundational, #architecture, #pattern
---

# 18 — Polymorphism

`#foundational` `#architecture` `#pattern`

⚡ TL;DR — One interface, many forms: the same method call behaves differently depending on the actual runtime type of the object it is invoked on.

| #18             | Category: CS Fundamentals — Paradigms                                      | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Object-Oriented Programming (OOP), Abstraction, Encapsulation, Inheritance |                 |
| **Used by:**    | Design Patterns, Dependency Injection, Interfaces, Functional Programming  |                 |

---

### 📘 Textbook Definition

**Polymorphism** (from Greek: _poly_ = many, _morphē_ = form) is the ability of a single interface to represent different underlying types, with the correct behaviour selected at runtime or compile time. In object-oriented programming there are three primary forms: **subtype polymorphism** (runtime dispatch — a supertype reference holds a subtype object, and the subtype's method is invoked via virtual dispatch), **parametric polymorphism** (generics — code written for a type parameter `T` works for any concrete type), and **ad-hoc polymorphism** (method overloading — the same method name with different parameter types, resolved at compile time).

---

### 🟢 Simple Definition (Easy)

Polymorphism means the same instruction does different things depending on what kind of object it's applied to. `animal.speak()` says "Woof" if the animal is a dog, "Meow" if it's a cat — one call, many behaviours.

---

### 🔵 Simple Definition (Elaborated)

In a polymorphic system, you write code against a general type (e.g., `Shape`) without knowing — or caring — which specific subtype (Circle, Square, Triangle) is actually used. When you call `shape.area()`, the runtime looks at the actual object and calls the correct implementation. This frees you to add new shapes without changing any existing code that works with shapes — the Open/Closed Principle in action. Polymorphism is what makes frameworks possible: Spring calls `handle(request)` on your controller without knowing its specific class; JDBC calls `executeQuery()` on your driver without knowing whether it's MySQL or PostgreSQL.

---

### 🔩 First Principles Explanation

**The problem: branching on type.**

Without polymorphism, handling different types requires explicit `if`/`switch` chains:

```java
// Without polymorphism: type-switching in every method
double calculateArea(Object shape) {
    if (shape instanceof Circle c) {
        return Math.PI * c.radius * c.radius;
    } else if (shape instanceof Square s) {
        return s.side * s.side;
    } else if (shape instanceof Triangle t) {
        return 0.5 * t.base * t.height;
    }
    throw new IllegalArgumentException("Unknown shape");
}
// Adding Triangle required changing THIS method AND every other method
// that switches on type (perimeter, draw, serialize, ...)
```

**The constraint:** every time you add a new type, you must find and update every `instanceof` chain in the codebase.

**The insight:** instead of the caller switching on type, let each type decide its own behaviour. Push the "what do I do?" logic into the object itself.

**The solution — virtual dispatch:**

```java
interface Shape {
    double area(); // single method, many implementations
}

class Circle   implements Shape { double area() { return Math.PI * r * r; } }
class Square   implements Shape { double area() { return side * side; } }
class Triangle implements Shape { double area() { return 0.5 * b * h; } }

// Caller: no type-switching, ever
for (Shape shape : shapes) {
    System.out.println(shape.area()); // correct method chosen at runtime
}
```

Adding a `Pentagon` requires zero changes to the loop — only a new class.

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Polymorphism (type-switching everywhere):

```java
// Every feature requires a type switch — Open/Closed violated
void renderShape(Object shape) {
    if (shape instanceof Circle c)   drawCircle(c);
    else if (shape instanceof Square s) drawSquare(s);
    // Adding Hexagon: must find and update THIS and every other switch
}

void exportShape(Object shape) {
    if (shape instanceof Circle c)   exportCircle(c);
    else if (shape instanceof Square s) exportSquare(s);
    // Same change, different place — missed = bug
}
```

What breaks without it:

1. Adding a new type requires locating every switch/if-instanceof chain.
2. Each switch is a separate failure mode — one missed = runtime exception.
3. The caller must know about all possible types — tight coupling.
4. Testing requires exercising every branch of every switch separately.

WITH Polymorphism:
→ Adding a new type: add one class implementing the interface. Zero existing code changes.
→ Callers are immune to type proliferation.
→ Each type is independently testable.
→ Frameworks (Spring, JUnit) can work with your types without knowing them in advance.

---

### 🧠 Mental Model / Analogy

> Think of a universal remote control that has a "Play" button. Point it at a DVD player — it plays a disc. Point it at a Blu-ray player — it plays a Blu-ray. Point it at a streaming box — it plays a stream. The remote's "Play" button is the interface. The specific device is the implementation. The user sends the same signal every time; the device chooses its own appropriate response. Swapping in a new device (Apple TV, Chromecast) requires no change to the remote.

"Play button on the remote" = polymorphic method call (`device.play()`)
"Different devices" = different implementations (Circle, Square, etc.)
"Device responding appropriately" = virtual dispatch invoking the subtype's method
"Swapping devices without changing remote" = Open/Closed Principle

---

### ⚙️ How It Works (Mechanism)

**Subtype Polymorphism — Virtual Dispatch (Java):**

```
┌──────────────────────────────────────────────────────┐
│               Virtual Dispatch Table                 │
│                                                      │
│  Shape reference → points to → Circle object        │
│                                     │               │
│                             vtable (method table)   │
│                                     │               │
│                              Circle.area() ──►  π*r²│
│                                                      │
│  shape.area() → JVM looks up vtable → calls π*r²    │
│  (resolved at RUNTIME, not compile time)             │
└──────────────────────────────────────────────────────┘
```

**Three forms of polymorphism:**

```java
// 1. SUBTYPE (Runtime) — method chosen based on actual object type
Shape s = new Circle(5);
s.area(); // → Circle.area() chosen at runtime

// 2. PARAMETRIC (Generics) — same code works for any type T
List<Integer> ints    = new ArrayList<>();
List<String>  strings = new ArrayList<>();
// One ArrayList implementation works for all type parameters

// 3. AD-HOC (Overloading) — method chosen based on argument types
class Printer {
    void print(int n)    { System.out.println(n); }
    void print(String s) { System.out.println(s); }
    void print(double d) { System.out.println(d); }
}
// Resolved at COMPILE time — not true runtime polymorphism
```

**`@Override` and the Liskov Substitution Principle:**

```java
// Subtype must honour the supertype's contract
class Shape {
    double area() { return 0.0; }
}

class Square extends Shape {
    @Override
    double area() { return side * side; } // @Override: compiler verifies
}

// LSP: wherever Shape is expected, Square must work correctly
void processShape(Shape shape) {
    double a = shape.area(); // Square must return a valid area — not -1, not throw
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Abstraction → Interface definition
        │
        ▼
Polymorphism  ◄──── (you are here)
        │
        ├─────────────────────────────────────────┐
        ▼                                         ▼
Inheritance                               Composition over Inheritance
(subtype polymorphism via extends)       (polymorphism via delegation)
        │                                         │
        ▼                                         ▼
Design Patterns                         Dependency Injection
(Strategy, Command, Visitor — all        (inject polymorphic abstractions)
 exploit polymorphism)
```

---

### 💻 Code Example

**Example 1 — Open/Closed via subtype polymorphism:**

```java
interface Notification {
    void send(String message, String recipient);
}

class EmailNotification implements Notification {
    public void send(String msg, String to) {
        smtpClient.send(to, msg); // email implementation
    }
}

class SmsNotification implements Notification {
    public void send(String msg, String to) {
        smsGateway.send(to, msg); // SMS implementation
    }
}

class PushNotification implements Notification {
    public void send(String msg, String to) {
        pushService.notify(to, msg); // push implementation
    }
}

// Caller — zero changes when new notification types are added
class OrderService {
    private final Notification notifier;
    OrderService(Notification notifier) { this.notifier = notifier; }

    void placeOrder(Order order) {
        // process...
        notifier.send("Order confirmed: " + order.getId(),
            order.getUser().getContact());
    }
}
```

**Example 2 — Generics (parametric polymorphism):**

```java
// One sort method works for any Comparable type
public static <T extends Comparable<T>> void sort(List<T> list) {
    // implementation...
}

sort(List.of(3, 1, 2));          // works for Integer
sort(List.of("c", "a", "b"));   // works for String
sort(List.of(new BigDecimal("1.5"))); // works for BigDecimal
```

**Example 3 — Visitor pattern (double dispatch):**

```java
// Complex polymorphism: dispatch on BOTH the element type and visitor type
interface ShapeVisitor {
    void visit(Circle c);
    void visit(Square s);
}

interface Shape {
    void accept(ShapeVisitor visitor); // call back into the visitor
}

class Circle implements Shape {
    public void accept(ShapeVisitor v) { v.visit(this); }
}

class AreaCalculator implements ShapeVisitor {
    double total;
    public void visit(Circle c)  { total += Math.PI * c.r * c.r; }
    public void visit(Square s)  { total += s.side * s.side; }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                         |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Polymorphism requires inheritance                     | Interface-based polymorphism (implementing an interface) is preferred over class inheritance in modern Java; inheritance is one mechanism, not the definition   |
| Method overloading is runtime polymorphism            | Overloading is resolved at compile time based on static types — it is ad-hoc (compile-time) polymorphism, not subtype (runtime) polymorphism                    |
| Polymorphism always has a performance cost            | Virtual dispatch adds one pointer indirection — negligible in practice; JIT compilers inline devirtualised calls for monomorphic call sites                     |
| `instanceof` checks are always a polymorphism failure | Pattern matching `instanceof` in sealed class hierarchies (Java 17+) is legitimate; anti-pattern is using `instanceof` as a substitute for overriding behaviour |

---

### 🔥 Pitfalls in Production

**Violating the Liskov Substitution Principle**

```java
// BAD: subtype breaks the supertype's contract
class Rectangle {
    int width, height;
    void setWidth(int w)  { this.width = w; }
    void setHeight(int h) { this.height = h; }
    int area()            { return width * height; }
}

class Square extends Rectangle {
    @Override void setWidth(int w)  { width = height = w; } // LSP violation!
    @Override void setHeight(int h) { width = height = h; } // side effect
}

// Breaks when caller uses polymorphically:
Rectangle r = new Square();
r.setWidth(5); r.setHeight(3);
assert r.area() == 15; // fails — Square sets both to 3, area = 9
```

LSP-violating subtypes cause subtle bugs that appear only when the object is used polymorphically.

---

**Overuse of `instanceof` indicating missing polymorphism**

```java
// BAD: switch-on-type pattern — add a type, forget to update this
void process(Payment payment) {
    if (payment instanceof CreditCard cc) {
        processCreditCard(cc);
    } else if (payment instanceof BankTransfer bt) {
        processBankTransfer(bt);
    }
    // Adding Crypto? Must find every instanceof chain
}

// GOOD: polymorphism — each type processes itself
interface Payment {
    void process(PaymentProcessor processor);
}
// Zero changes here when new payment types are added
```

---

### 🔗 Related Keywords

- `Abstraction` — defines the interface that polymorphism makes flexible
- `Inheritance` — one mechanism for achieving subtype polymorphism
- `Composition over Inheritance` — preferred over inheritance for polymorphism in complex hierarchies
- `Encapsulation` — protects the distinct state of each polymorphic type
- `Liskov Substitution Principle` — the correctness rule for subtype polymorphism
- `Strategy Pattern` — encapsulates interchangeable algorithms using polymorphism
- `Dependency Injection` — injects polymorphic abstractions to decouple callers from implementations
- `Generics` — Java's parametric polymorphism mechanism

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Same interface → different behaviours     │
│              │ at runtime, based on actual object type   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple types share a common operation;  │
│              │ new types may be added without code change│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Forced inheritance hierarchies just for   │
│              │ polymorphism — prefer interfaces          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Polymorphism is the promise that new     │
│              │ types obey old contracts — and that old   │
│              │ code never needs to know their names."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Liskov Substitution → Strategy Pattern →  │
│              │ Dependency Injection → Generics           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Java 17 introduced sealed classes (`sealed interface Shape permits Circle, Square, Triangle`). Pattern matching `switch` over a sealed hierarchy is exhaustive at compile time — no default case needed. Compare this to traditional runtime polymorphism via `interface Shape { double area(); }`. Identify two scenarios where sealed+switch is _preferable_ to virtual dispatch, and two scenarios where virtual dispatch is strictly necessary, explaining the trade-off in terms of the Open/Closed Principle.

**Q2.** A JVM JIT compiler applies "devirtualisation" — optimising a polymorphic call site into a direct call when it detects only one concrete type has ever been seen at that site. A benchmark shows a method runs 3× faster after JIT warmup. Then a second implementation of the interface is loaded at runtime (via a plugin system). Describe what happens to performance at that call site, why, and what architectural implication this has for plugin-based systems that rely on polymorphism for extensibility.
