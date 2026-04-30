---
layout: default
title: "Sealed Classes"
parent: "Java Language"
nav_order: 323
permalink: /java-language/sealed-classes/
---
# 323 — Sealed Classes (Java 17+)

`#java` `#java17` `#oop` `#type-system`

⚡ TL;DR — Sealed classes let you explicitly list which classes are permitted to extend or implement a type, closing the inheritance hierarchy and enabling exhaustive pattern matching.

| #323 | category: Java Language
|:---|:---|:---|
| **Depends on:** | Inheritance, Abstract Classes, Interfaces, Pattern Matching | |
| **Used by:** | Pattern Matching, Switch Expressions, Domain Modelling | |

---

### 📘 Textbook Definition

A **sealed class** (or interface) in Java 17+ restricts which other classes or interfaces may directly extend or implement it. The `sealed` modifier is paired with a `permits` clause listing every allowed subtype. Each permitted subtype must be declared `final`, `sealed`, or `non-sealed`. This gives the compiler a closed, exhaustive view of the type hierarchy.

---

### 🟢 Simple Definition (Easy)

Normally, any class anywhere can extend your class. Sealed classes say: "Only THESE specific classes are allowed to extend me — and I know the complete list at compile time."

---

### 🔵 Simple Definition (Elaborated)

Sealed classes solve a specific problem: you sometimes want inheritance (for polymorphism) but NOT unlimited extension. For example, a `Shape` class should only have `Circle`, `Rectangle`, and `Triangle` — nothing else. Sealed classes enforce that. And because the compiler knows the complete list of subtypes, switch expressions over them can be exhaustive without a default case.

---

### 🔩 First Principles Explanation

**The problem:** Unconstrained inheritance is powerful but uncontrollable.

```
// Pre-Java 17: anyone can extend Shape
public abstract class Shape { }

// In some other package, anyone can do:
public class HexagonalPrism extends Shape { }  // you didn't intend this
public class MysteryShape extends Shape { }    // completely unknown

// Result: switch over Shape can NEVER be exhaustive
// You can never be sure you've handled all cases
```

**The insight:** Sometimes you want a CLOSED hierarchy — all variants known at compile time.

```
Without sealed:             With sealed:
Shape (abstract)            Shape (sealed)
├─ Circle (external OK)     ├─ Circle (permitted)
├─ Rectangle (external OK)  ├─ Rectangle (permitted)
├─ Triangle (external OK)   └─ Triangle (permitted)
└─ ???Anything???           (no other subtypes possible)
```

**The solution:** `sealed` + `permits` + enforcement on subclasses.

---

### ❓ Why Does This Exist — Why Before What

**Without sealed classes:**

```
Problem 1: Open hierarchies break exhaustive switch
  switch (shape) {
      case Circle c -> ...
      case Rectangle r -> ...
      // Must have default → compiler can't verify completeness
  }

Problem 2: Library types can be subclassed externally
  Users of your API can add unauthorized subtypes
  → your internal logic breaks silently

Problem 3: Domain model leaks
  An HTTP Response should be exactly: OK, Error, Redirect
  Nothing else — but without sealed, anyone can add subtypes
```

**With sealed classes:**

```
✅ Compiler knows all subtypes → switch can be exhaustive (no default needed)
✅ Hierarchy is documented and enforced in the class declaration itself
✅ Works with Records for concise, immutable data hierarchies
✅ Enables algebraic data types (like Rust enums/Haskell ADTs) in Java
```

---

### 🧠 Mental Model / Analogy

> Think of sealed classes as a **membership club with a fixed guest list**. The club exists (`sealed Shape`), and only pre-approved members (`Circle`, `Rectangle`, `Triangle`) can join. The bouncer (compiler) rejects anyone not on the list. Because the list is fixed, the club organiser can plan for exactly those members — no surprises.

---

### ⚙️ How It Works

```
sealed class/interface
    └─ declares: permits A, B, C

Each permitted type MUST be:
   final      → no further subclassing
   sealed     → can restrict further (own permits clause)
   non-sealed → re-opens to unrestricted subclassing

All permitted types must:
   → Be in the same compilation unit (same package or module)
   → Directly extend/implement the sealed type
```

**Hierarchy example:**

```
sealed interface Shape permits Circle, Rectangle, Triangle

final class Circle    implements Shape { double radius; }
final class Rectangle implements Shape { double w, h; }
sealed class Triangle implements Shape permits RightTriangle
final class RightTriangle extends Triangle { }
```

---

### 🔄 How It Connects

```
Sealed Class
      │
      ├─ permits ──→ final class     (closed leaf)
      ├─ permits ──→ sealed class    (restricted sub-hierarchy)
      └─ permits ──→ non-sealed      (re-opens, no restriction)
            │
            └─ Enables ──→ Pattern Matching Switch
                              (exhaustive, no default needed)
                         ──→ Records (sealed + record = ADT)
                         ──→ Visitor Pattern (compiler-verified)
```

---

### 💻 Code Example

```java
// sealed interface with permits
public sealed interface Result<T> permits Result.Ok, Result.Err {

    record Ok<T>(T value) implements Result<T> { }
    record Err<T>(String message) implements Result<T> { }
}

// Exhaustive switch — no default needed
public static <T> String describe(Result<T> result) {
    return switch (result) {
        case Result.Ok<T> ok   -> "Success: " + ok.value();
        case Result.Err<T> err -> "Error: "   + err.message();
        // Compiler verifies ALL cases handled
        // Uncomment one case → compile error, not runtime NPE
    };
}
```

```java
// Domain model: sealed hierarchy for HTTP responses
public sealed interface HttpResponse
    permits HttpResponse.Ok, HttpResponse.Redirect, HttpResponse.ClientError, HttpResponse.ServerError {

    record Ok(String body)                     implements HttpResponse { }
    record Redirect(String location)           implements HttpResponse { }
    record ClientError(int status, String msg) implements HttpResponse { }
    record ServerError(int status, String msg) implements HttpResponse { }
}

// Pattern matching is exhaustive — no default branch
String handle(HttpResponse response) {
    return switch (response) {
        case HttpResponse.Ok ok               -> "200 OK: " + ok.body();
        case HttpResponse.Redirect r          -> "Redirect to: " + r.location();
        case HttpResponse.ClientError(var s, var m) -> "Client error " + s + ": " + m;
        case HttpResponse.ServerError(var s, var m) -> "Server error " + s + ": " + m;
    };
}
```

```java
// non-sealed re-opens hierarchy for extensibility
public sealed class Expression permits Literal, Add, Multiply, Unknown

final class Literal    extends Expression { int value; }
final class Add        extends Expression { Expression left, right; }
final class Multiply   extends Expression { Expression left, right; }
non-sealed class Unknown extends Expression { }  // anyone can extend Unknown
// trade-off: switch over Expression needs default again for Unknown subtypes
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Sealed = private inner classes only | Permitted subclasses can be in same package or module (not just inner) |
| `final` and `sealed` are the same | `final` forbids ALL subclasses; `sealed` allows a fixed set |
| `permits` list is optional | Required unless subclasses are in same source file, then inferred |
| Sealed classes replace enums | Enums work for constants; sealed classes work for types with different fields |
| `non-sealed` defeats the purpose | It's intentional — lets a specific branch re-open while the rest stays closed |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Forgetting to mark permitted subtype as final/sealed/non-sealed**

```java
// Compile error — permitted type must declare one of: final, sealed, non-sealed
public sealed interface Shape permits Circle { }
class Circle implements Shape { }  // ❌ ERROR: must be final, sealed, or non-sealed

// Fix:
final class Circle implements Shape { }  // ✅
```

**Pitfall 2: Permitted type in wrong package (without module)**

```java
// Shape.java in com.example.shapes
public sealed interface Shape permits com.other.Circle { }  // ❌ — different package, no module

// Fix: use Java modules (module-info.java) to allow cross-package sealed hierarchies
// or keep all permitted types in same package
```

---

### 🔗 Related Keywords

- **[Pattern Matching](./064 — Pattern Matching (Java 16+).md)** — switch exhaustiveness depends on sealed
- **Records (Java 16+)** — pair with sealed for concise algebraic data types
- **Inheritance** — sealed restricts inherit; non-sealed re-opens it
- **Generics** — sealed interfaces can be generic; each subtype can specialise
- **Switch Expressions** — exhaustive switch without default over sealed type

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Close the inheritance hierarchy — only listed │
│              │ subtypes may extend; compiler knows all cases │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Modelling closed domain types (Result, Shape, │
│              │ HttpResponse) + want exhaustive pattern match  │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Hierarchy genuinely open for user extension   │
│              │ (e.g. public API that users must subclass)    │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "sealed = I decide who can extend me; the     │
│              │  compiler enforces it and rewards you with    │
│              │  exhaustive pattern matching for free"        │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ Pattern Matching → Records → Switch           │
│              │ Expressions → Algebraic Data Types            │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A sealed interface has three permitted subtypes: `Ok`, `ClientError`, `ServerError`. You add a fourth subtype `Redirect` later. What happens to all existing exhaustive switch expressions in the codebase — and why is this actually a *feature*, not a bug?

**Q2.** Can a sealed class be abstract? Can a sealed interface have default methods? What restrictions apply?

**Q3.** How do sealed classes relate to the Visitor pattern? Does a sealed hierarchy eliminate the need for Visitor, or do they serve different purposes?

