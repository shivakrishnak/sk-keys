---
layout: default
title: "Inheritance"
parent: "CS Fundamentals — Paradigms"
nav_order: 19
permalink: /cs-fundamentals/inheritance/
number: "19"
category: CS Fundamentals — Paradigms
difficulty: ★☆☆
depends_on: Object-Oriented Programming (OOP), Encapsulation, Polymorphism
used_by: Composition over Inheritance, Design Patterns, Liskov Substitution Principle
tags: #foundational, #architecture, #pattern
---

# 19 — Inheritance

`#foundational` `#architecture` `#pattern`

⚡ TL;DR — A mechanism where a class acquires the fields and methods of a parent class, enabling code reuse and subtype relationships — but coupling parent and child tightly.

| #19             | Category: CS Fundamentals — Paradigms                                        | Difficulty: ★☆☆ |
| :-------------- | :--------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Object-Oriented Programming (OOP), Encapsulation, Polymorphism               |                 |
| **Used by:**    | Composition over Inheritance, Design Patterns, Liskov Substitution Principle |                 |

---

### 📘 Textbook Definition

**Inheritance** is an OOP mechanism in which a class (the _subclass_ or _child_) derives from another class (the _superclass_ or _parent_), inheriting its non-private fields and methods. The subclass extends the parent's behaviour by adding new members or overriding existing methods. Inheritance establishes an _is-a_ relationship (a `Dog` is an `Animal`) and enables subtype polymorphism — a supertype reference can hold a subtype instance and dispatch to overridden methods. Java supports single inheritance for classes and multiple inheritance for interfaces.

---

### 🟢 Simple Definition (Easy)

Inheritance lets a class "take" all the properties and methods from a parent class automatically — like a child who inherits traits and skills from their parents, then adds their own.

---

### 🔵 Simple Definition (Elaborated)

When `Dog extends Animal`, the `Dog` class automatically has everything `Animal` has (fields and methods), plus anything it adds itself. `Animal` might define a `name` field and a `breathe()` method. `Dog` inherits both and adds a `bark()` method. `Dog` can also override `Animal.speak()` to print "Woof" instead of a generic sound. Inheritance is primarily useful for two things: code reuse (don't copy shared behaviour) and subtype polymorphism (a `Dog` can be used wherever an `Animal` is expected). The risk is tight coupling: changes to the parent class cascade to all children, making deep hierarchies fragile.

---

### 🔩 First Principles Explanation

**The problem: code duplication across similar types.**

Without inheritance, related classes repeat the same fields and methods:

```java
class Dog {
    private String name;
    private int age;
    public String getName() { return name; }
    public int    getAge()  { return age; }
    public void breathe() { System.out.println("inhale/exhale"); }
    public void bark()    { System.out.println("Woof!"); }
}

class Cat {
    private String name;     // DUPLICATE
    private int age;         // DUPLICATE
    public String getName() { return name; }  // DUPLICATE
    public int    getAge()  { return age; }   // DUPLICATE
    public void breathe() { System.out.println("inhale/exhale"); } // DUPLICATE
    public void meow()    { System.out.println("Meow!"); }
}
```

**The solution — extract common behaviour to a parent:**

```java
class Animal {
    private String name;  // defined once
    private int age;
    public String getName() { return name; }
    public int    getAge()  { return age; }
    public void breathe() { System.out.println("inhale/exhale"); }
    public void speak()   { /* default */ }
}

class Dog extends Animal {
    @Override public void speak() { System.out.println("Woof!"); }
}

class Cat extends Animal {
    @Override public void speak() { System.out.println("Meow!"); }
}
```

`name`, `age`, `getName()`, `breathe()` are defined once. Dog and Cat only define what is different.

**The risk — fragile base class problem:**

Any change to `Animal` potentially breaks `Dog` and `Cat`. In deep hierarchies (A → B → C → D), a change at A propagates through all children. This is why the industry guidance evolved: _prefer composition over inheritance_ for complex relationships.

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Inheritance:

```java
// 10 vehicle types × 20 shared methods = 200 duplicated method bodies
// Fix a shared bug (e.g., speed calculation) → update 10 files
// Add a shared feature (e.g., GPS) → update 10 files
```

What breaks without it:

1. Shared behaviour is copy-pasted — bug in one copy is not in others.
2. Adding a shared feature requires touching every duplicate class.
3. Subtype polymorphism requires separate interfaces and manual wiring.
4. Testing shared behaviour requires testing it separately in every class.

WITH Inheritance:
→ Shared behaviour defined once in the parent — fix once, fixed everywhere.
→ `is-a` subtype polymorphism is automatic — subclass usable as parent type.
→ Template method pattern works naturally — parent defines the algorithm skeleton.

---

### 🧠 Mental Model / Analogy

> Think of a company's standard employment contract. Every employee (Software Engineer, Designer, Manager) starts from the same base contract: salary, holidays, non-compete clause. Then each role adds specific terms. The company doesn't write 20 unique full contracts for 20 employees — they write one base contract and extend it per role. Inheritance works the same way: the base class is the standard contract; subclasses extend it with role-specific terms.

"Standard employment contract" = parent / superclass
"Role-specific contract addendum" = subclass additions
"Employee receiving the full contract" = inheriting all parent members
"Changing a term in the base contract" = changing the parent class (affects all)

---

### ⚙️ How It Works (Mechanism)

**Java inheritance mechanics:**

```java
class Vehicle {
    protected int speed;        // accessible to subclasses
    private String serialNo;    // NOT accessible to subclasses

    public void accelerate(int delta) { speed += delta; }
    public int  getSpeed() { return speed; }
}

class Car extends Vehicle {
    private int doors;

    public Car(int doors) {
        super();       // calls Vehicle() constructor — required
        this.doors = doors;
    }

    @Override
    public void accelerate(int delta) {
        super.accelerate(delta); // call parent's implementation
        checkEngineLight();      // add car-specific behaviour
    }
}
```

**Method Resolution Order (MRO):**

```
┌──────────────────────────────────────────────────────┐
│          Method Resolution: car.accelerate(10)       │
│                                                      │
│  1. JVM checks Car's vtable: override present? ──►   │
│     YES → call Car.accelerate()                      │
│                                                      │
│  2. Car.accelerate() calls super.accelerate()  ──►   │
│     Calls Vehicle.accelerate()                       │
│                                                      │
│  3. Returns — Car's checkEngineLight() runs          │
└──────────────────────────────────────────────────────┘
```

**Inheritance vs Interface Implementation:**

|                          | extends (class)             | implements (interface) |
| ------------------------ | --------------------------- | ---------------------- |
| Can inherit multiple?    | No (single inheritance)     | Yes                    |
| Gets implementation?     | Yes                         | Default methods only   |
| Couples to parent state? | Yes (protected fields)      | No                     |
| Use for                  | true is-a, shared behaviour | capability/contract    |

---

### 🔄 How It Connects (Mini-Map)

```
Object-Oriented Programming
        │
        ▼
Inheritance  ◄──── (you are here)
        │
        ├─────────────────────────────────────────┐
        ▼                                         ▼
Polymorphism                     Composition over Inheritance
(subtype polymorphism via extends) (preferred alternative)
        │                                         │
        ▼                                         ▼
Liskov Substitution Principle         Design Patterns
(correctness rule for inheritance)    (Template Method uses inheritance;
        │                              Strategy replaces it)
        ▼
Deep class hierarchies → Fragile Base Class Problem
```

---

### 💻 Code Example

**Example 1 — Template Method Pattern (inheritance for controlled extension):**

```java
// Abstract class defines the algorithm skeleton
abstract class DataImporter {
    // Template method: final — subclasses cannot change the flow
    public final void importData(String source) {
        String raw  = readData(source);   // step 1: defined in subclass
        String clean = validate(raw);      // step 2: shared logic here
        store(clean);                      // step 3: defined in subclass
    }

    protected abstract String readData(String source);
    protected abstract void   store(String data);

    private String validate(String raw) {
        // shared validation logic — not overridable
        return raw.trim().replace("\r\n", "\n");
    }
}

class CsvImporter extends DataImporter {
    protected String readData(String source) { /* parse CSV */ return ""; }
    protected void   store(String data)      { /* save to DB */ }
}
```

**Example 2 — Fragile base class problem:**

```java
class Counter {
    int count = 0;
    void add(int n)    { count += n; }
    void addAll(int[] ns) {
        for (int n : ns) add(n); // calls add() — virtual dispatch!
    }
}

class LoggingCounter extends Counter {
    @Override void add(int n) {
        System.out.println("adding " + n);
        count += n;
    }
}

// addAll calls the overridden add() — each element logged once
LoggingCounter lc = new LoggingCounter();
lc.addAll(new int[]{1, 2, 3}); // logs "adding 1", "adding 2", "adding 3"

// If parent changes addAll() to not call add() (inlines the loop),
// LoggingCounter silently stops logging — fragile!
```

**Example 3 — Prefer composition when the is-a relationship is questionable:**

```java
// BAD: Stack extends Vector — "is-a Vector" is wrong; exposes all Vector methods
// A Stack shouldn't allow arbitrary index-based insertion
Stack<String> stack = new Stack<>();
stack.add(0, "bottom"); // should be invalid for a stack!

// GOOD: compose instead
class Stack<T> {
    private final Deque<T> storage = new ArrayDeque<>();
    public void push(T item) { storage.push(item); }
    public T    pop()        { return storage.pop(); }
    public T    peek()       { return storage.peek(); }
    // Exposes ONLY stack operations — no spurious Vector methods
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                                              |
| --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Inheritance is primarily for code reuse             | The primary benefit of inheritance is subtype polymorphism (`is-a`); code reuse is a side effect. Reuse without a genuine `is-a` relationship should use composition |
| Deep inheritance hierarchies are a sign of good OOP | Deep hierarchies are a code smell — the Fragile Base Class Problem worsens with depth; most well-designed frameworks have hierarchies of 2–3 levels maximum          |
| `protected` fields are safely encapsulated          | Protected fields are accessible to all subclasses — in a large hierarchy, any subclass can corrupt them; prefer `private` with protected accessor methods            |
| Java's single inheritance is a limitation           | Single inheritance for classes prevents the diamond problem; multiple inheritance for interfaces (default methods) provides the flexibility of mixins where needed   |

---

### 🔥 Pitfalls in Production

**Inheriting for code reuse when there is no is-a relationship**

```java
// BAD: UserController "extends" BaseController just for shared logging
// UserController IS-NOT-A BaseController in a meaningful sense
class UserController extends BaseController {
    // inherits createAuditLog(), parseHeaders(), etc. it doesn't need
}

// GOOD: inject shared behaviour as a dependency (composition)
class UserController {
    private final AuditLogger auditLogger;     // composed
    private final RequestParser requestParser; // composed

    UserController(AuditLogger a, RequestParser r) {
        this.auditLogger = a;
        this.requestParser = r;
    }
}
```

---

**Calling overridable methods from constructors**

```java
// BAD: constructor calls overridable method
class Parent {
    Parent() {
        init(); // virtual dispatch during construction!
    }
    void init() { System.out.println("Parent init"); }
}

class Child extends Parent {
    String value;
    @Override void init() {
        value = "initialized"; // value might be null when called from Parent()!
    }
}

new Child(); // Parent() runs first, calls Child.init()
             // Child's fields not yet initialised → value is null
```

---

### 🔗 Related Keywords

- `Object-Oriented Programming (OOP)` — the paradigm in which inheritance is a core mechanism
- `Polymorphism` — inheritance enables subtype polymorphism: child usable as parent type
- `Composition over Inheritance` — the modern preference for combining behaviour via delegation rather than extending
- `Liskov Substitution Principle` — the rule every subclass must obey: it must be usable as its parent type without breaking callers
- `Template Method Pattern` — a design pattern that uses inheritance intentionally: parent defines the skeleton, subclasses fill in the steps
- `Encapsulation` — inheritance risks breaking encapsulation via `protected` fields and the fragile base class problem
- `Abstract Class` — a parent class with abstract methods, intended specifically to be extended

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Child gets parent's members automatically; │
│              │ establishes is-a subtype relationship     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Genuine is-a relationship; shared default │
│              │ behaviour; Template Method pattern        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Reusing code without a true is-a link;   │
│              │ deep hierarchies; overriding most methods │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Inheritance is a contract: the child     │
│              │ promises to behave like the parent —      │
│              │ everywhere the parent is expected."       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Composition over Inheritance → Liskov     │
│              │ Substitution → Template Method → Strategy │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Java's `java.util.Properties` extends `Hashtable<Object, Object>`. This means a `Properties` object can store non-String keys and values via inherited `put()` and `get()` methods, even though `Properties` was designed for String key-value pairs. Identify the specific consequence of this inheritance relationship that makes `Properties` a broken API, which design principle it violates, and what the correct design would have been.

**Q2.** The Template Method Pattern and the Strategy Pattern both allow customising steps within an algorithm. Template Method uses inheritance; Strategy uses composition and delegation. Describe a concrete scenario where switching from Template Method to Strategy would eliminate a specific production problem (not just "tight coupling"), and explain how the change affects testability, the number of classes, and the ability to change behaviour at runtime.
