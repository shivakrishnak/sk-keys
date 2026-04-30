---
layout: default
title: "Records (Java 16+)"
parent: "Java Language"
nav_order: 62
permalink: /java-language/records-java-16/
number: "062"
category: Java Language
difficulty: ★★☆
depends_on: Classes, Immutability, equals/hashCode
used_by: DTOs, Value Objects, Pattern Matching, Domain Models
tags: #java #intermediate #records #immutability #java16
---

# 062 — Records (Java 16+)

`#java` `#intermediate` `#records` `#immutability` `#java16`

⚡ TL;DR — Transparent, immutable data carriers: `record Point(int x, int y) {}` gives you a canonical constructor, accessors `x()` and `y()`, plus `equals`, `hashCode`, and `toString` — all generated.

| #062 | Category: Java Language | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Classes, Immutability, equals/hashCode | |
| **Used by:** | DTOs, Value Objects, Pattern Matching, Domain Models | |

---

### 📘 Textbook Definition

A **record** (Java 16, finalised from preview in Java 14/15) is a special kind of class — an immutable, transparent aggregate of its **components** (the declared fields). The compiler automatically generates: a public canonical constructor, private `final` fields, a public accessor method per component (named after the component), and implementations of `equals()`, `hashCode()`, and `toString()` based on all components.

---

### 🟢 Simple Definition (Easy)

Records replace verbose POJOs for data-only classes. Instead of writing 40 lines of getters, setters, equals, hashCode, and toString, you write:
```java
record Point(int x, int y) {}
```
Done. All the methods are generated.

---

### 🔵 Simple Definition (Elaborated)

Records enforce **immutability**: all fields are `private final`. You get accessors but no setters. This models **value semantics** — two `Point(1, 2)` are equal regardless of whether they're the same object. Records are ideal for DTOs, command/event objects, value objects, and method return values where immutability is desirable.

---

### 🔩 First Principles Explanation

**What the compiler generates:**
```java
record Point(int x, int y) {}

// Equivalent to:
final class Point {
    private final int x;
    private final int y;

    // Canonical constructor
    Point(int x, int y) { this.x = x; this.y = y; }

    // Accessors (NOT getX() — just x())
    public int x() { return x; }
    public int y() { return y; }

    // equals: all components compared
    public boolean equals(Object o) { ... }

    // hashCode: all components hashed
    public int hashCode() { ... }

    // toString: "Point[x=1, y=2]"
    public String toString() { ... }
}
```

---

### ❓ Why Does This Exist (Why Before What)

Java has always been verbose for data classes. Lombok's `@Data` was the community workaround. Records are the language-level answer — not via code generation, but as a first-class Java feature. They also integrate with **sealed classes** and **pattern matching** (Java 21+ switch patterns).

---

### 🧠 Mental Model / Analogy

> A record is a **named tuple** in Java. In Python you'd write `Point = namedtuple('Point', ['x', 'y'])`. In Java 16+, `record Point(int x, int y) {}` does the same — a named container for a fixed set of values, where the values define identity and equality.

---

### ⚙️ How It Works (Mechanism)

```
Record restrictions:
  1. All components are implicitly private final
  2. Cannot explicitly declare instance fields (beyond components)
  3. Cannot extend any class (implicitly extends Record)
  4. CAN implement interfaces
  5. CAN have static fields and static methods
  6. CAN define custom constructors, instance methods
  7. CAN override generated equals/hashCode/toString

Compact canonical constructor (for validation):
  record Range(int lo, int hi) {
      Range {   // compact constructor — params are the components
          if (lo > hi) throw new IllegalArgumentException();
          // fields are assigned after this block automatically
      }
  }

Custom methods allowed:
  record Point(double x, double y) {
      double distanceTo(Point other) {
          double dx = this.x - other.x, dy = this.y - other.y;
          return Math.sqrt(dx*dx + dy*dy);
      }
  }

Serialization: Records implement Serializable if specified
  record Point(int x, int y) implements Serializable {}
```

---

### 🔄 How It Connects (Mini-Map)

```
[Records] ──immutable data carriers──► [Value Objects / DTOs]
     │
     ├── works with ──────────────────► [Pattern Matching #064]
     │   (switch/instanceof destructuring)
     │
     ├── compared to ─────────────────► [Kotlin data class]
     │                                  [Scala case class]
     │
     └── enables ─────────────────────► [Sealed Classes #063]
                                        (sealed + record = ADTs)
```

---

### 💻 Code Example

```java
// 1. Basic record
record Point(int x, int y) {}
Point p = new Point(3, 4);
System.out.println(p.x());          // 3  (accessor, NOT getX)
System.out.println(p.y());          // 4
System.out.println(p);              // Point[x=3, y=4]
System.out.println(p.equals(new Point(3, 4)));  // true (value equality)

// 2. Record with validation (compact constructor)
record Range(int lo, int hi) {
    Range {
        if (lo > hi)
            throw new IllegalArgumentException(lo + " > " + hi);
    }
}
new Range(1, 5);   //  ok
new Range(5, 1);   //  IllegalArgumentException

// 3. Record implementing interface
interface Shape { double area(); }

record Circle(double radius) implements Shape {
    public double area() { return Math.PI * radius * radius; }
}

// 4. Record with static factory
record Money(BigDecimal amount, String currency) {
    static Money usd(BigDecimal amount) { return new Money(amount, "USD"); }
    static Money eur(BigDecimal amount) { return new Money(amount, "EUR"); }
}
Money price = Money.usd(new BigDecimal("9.99"));

// 5. Records in Pattern Matching (Java 21)
sealed interface Shape permits Circle, Rectangle {}
record Circle(double radius) implements Shape {}
record Rectangle(double w, double h) implements Shape {}

double area(Shape s) {
    return switch (s) {
        case Circle(double r)       -> Math.PI * r * r;
        case Rectangle(double w, double h) -> w * h;
    };
}

// 6. Serializable record
record Transfer(String from, String to, BigDecimal amount)
        implements Serializable {}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Accessors are `getX()` | Accessors are named after the component: `x()`, not `getX()` |
| Records can extend classes | Records implicitly extend `java.lang.Record` — can't extend anything else |
| Records are mutable by default | All components are `private final` — immutable |
| Records can't have methods | Can have instance + static methods, just no extra instance fields |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Mutable components create mutable records**
```java
record Container(List<String> items) {}
Container c = new Container(new ArrayList<>(List.of("a", "b")));
c.items().add("c");  // MUTATES the list — record is not deep-immutable!
// Fix: use unmodifiable list:
record Container(List<String> items) {
    Container { items = List.copyOf(items); }  // defensive copy
}
```

**Pitfall 2: Jackson compatibility (older versions)**
Jackson < 2.12 doesn't deserialize records without `@JsonCreator`. Fix: upgrade to Jackson 2.12+ with `jackson-modules-java-base`.

**Pitfall 3: Lombok @Data conflict**
Records and Lombok `@Data` on the same class causes compilation issues. Pick one — records for new code.

---

### 🔗 Related Keywords

- **Sealed Classes (#063)** — combine with records to create algebraic data types (ADTs)
- **Pattern Matching (#064)** — deconstruct record components in `switch`/`instanceof`
- **Immutability** — records enforce it for simple fields; guard mutable components
- **Kotlin data class** — similar concept with `copy()` method additionally
- **Lombok @Data** — pre-Java-16 workaround that records replace

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Immutable data carrier: components → final    │
│              │ fields + canonical ctor + equals/hash/toString│
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ DTOs, return values, value objects, simple    │
│              │ domain aggregates, ADT leaf nodes             │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Need mutability; need OOP hierarchy;          │
│              │ Hibernate entities (mutable, need no-arg ctor)│
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Named tuple: data defines identity;          │
│              │  all boilerplate is generated"                │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Sealed Classes → Pattern Matching → ADTs      │
└─────────────────────────────────────────────────────────────┘
```

### 🧠 Think About This Before We Continue

**Q1.** Why are records unsuitable as JPA/Hibernate `@Entity` classes?
**Q2.** If a record component is a `List`, why is the record not deeply immutable, and how do you fix it?
**Q3.** How do records combine with sealed classes to create algebraic data types (ADTs) in Java?

