---
layout: default
title: "Pattern Matching"
parent: "Java Language"
nav_order: 324
permalink: /java-language/pattern-matching/
---
# 324 — Pattern Matching (Java 16+)

`#java` `#java16` `#java21` `#oop` `#type-system`

⚡ TL;DR — Pattern matching combines type testing, casting, and binding into a single expression, eliminating the verbose test-cast-use idiom and enabling powerful exhaustive switch dispatch over sealed hierarchies.

| #324 | category: Java Language
|:---|:---|:---|
| **Depends on:** | Generics, Sealed Classes, instanceof, Switch Expressions | |
| **Used by:** | Sealed Classes, Domain Modelling, Type-safe Dispatch | |

---

### 📘 Textbook Definition

**Pattern matching** in Java allows a conditional check and type-correct variable binding in a single operation. Two primary forms:

1. **`instanceof` patterns (Java 16):** `if (obj instanceof String s)` — tests the type AND introduces a bound variable `s` scoped to the true branch.
2. **Switch patterns (Java 21):** `switch (obj) { case String s -> ... }` — dispatches on type patterns, guarded patterns, and record deconstruction patterns.

---

### 🟢 Simple Definition (Easy)

Before pattern matching, every `instanceof` required three lines: check type, cast, use. Pattern matching collapses all three into one: `if (obj instanceof String s)` — if true, `s` is already the correctly-typed String, ready to use.

---

### 🔵 Simple Definition (Elaborated)

Pattern matching is Java's answer to "I know what type this is — don't make me say it three times." The compiler proves that inside the true branch, the object IS that type, so it introduces the typed variable automatically. Switch patterns extend this: instead of a chain of `if-instanceof-cast`, you write a clean switch that dispatches to the right branch based on what the object actually is — and with sealed classes, the compiler verifies you've handled every possible case.

---

### 🔩 First Principles Explanation

**The old idiom — type test + cast + use:**

```
Every instanceof in Java pre-16 forced a 3-step ritual:

Step 1: Test
   if (obj instanceof String) { ... }

Step 2: Cast (unsafe if you got the type wrong, but you just tested it!)
   String s = (String) obj;

Step 3: Use
   System.out.println(s.toUpperCase());

The cast on step 2 is REDUNDANT — you just proved the type.
The compiler knows it, but forces you to repeat yourself.
```

**The insight — let the compiler bind the variable:**

```
If: obj instanceof String
Then: inside the true branch, obj IS a String.
      The compiler can introduce a typed binding for you.

obj instanceof String s
         ↑               ↑
    type test         NEW: bound variable 's' of type String
                     scoped to the true branch. No cast needed.
```

**Switch patterns — dispatch by type:**

```
Pre-21 type dispatch:
   if (shape instanceof Circle c) { area = PI * c.radius() * c.radius(); }
   else if (shape instanceof Rectangle r) { area = r.width() * r.height(); }
   else throw new IllegalArgumentException();

Post-21 switch pattern:
   double area = switch (shape) {
       case Circle c    -> PI * c.radius() * c.radius();
       case Rectangle r -> r.width() * r.height();
       // With sealed Shape: no default needed — compiler verifies exhaustiveness
   };
```

---

### ❓ Why Does This Exist — Why Before What

```
Without pattern matching:
   1. Redundant casts scattered everywhere
   2. Risk: test one type, cast to another → ClassCastException at runtime
   3. Can't write exhaustive type dispatch without default fallthrough
   4. Records can't be easily deconstructed inline

With pattern matching:
   ✅ Type test + binding in one step — no redundant cast
   ✅ Compile-time proof: can't use bound var outside true branch
   ✅ Guarded patterns: case String s when s.length() > 5 -> ...
   ✅ Record deconstruction: case Point(int x, int y) -> x + y
   ✅ Combined with sealed: exhaustive dispatch, no default needed
```

---

### 🧠 Mental Model / Analogy

> Pattern matching is like a **customs officer with a filing system**. The old way: officer checks passport (instanceof), makes a photocopy (cast), then hands you the copy to use. New way: officer checks passport and hands you the filed copy in one motion — if you pass the check, you already have what you need.

---

### ⚙️ How It Works

```
instanceof pattern:
   obj instanceof Type varName
      │                │
   type test      if true: varName bound to obj as Type
                  scope: true branch only

Switch pattern (Java 21):
   switch (obj) {
       case Type1 t1 -> ...       // type pattern
       case Type2 t2 when guard   // guarded pattern
            -> ...
       case null -> ...            // null pattern (Java 21)
       default   -> ...
   }

Deconstruction pattern (Records):
   if (point instanceof Point(int x, int y)) {
       // x and y bound directly — no .x() / .y() calls
   }
```

---

### 🔄 How It Connects

```
Pattern Matching
     │
     ├─ instanceof pattern ──→ eliminates redundant cast
     │
     ├─ switch patterns    ──→ type-based dispatch
     │        │
     │        └─ + Sealed Classes ──→ exhaustive (no default)
     │        └─ + Records        ──→ deconstruction patterns
     │        └─ + Guarded        ──→ `case X x when predicate`
     │
     └─ Record Patterns    ──→ nested deconstruction
              (Java 21)         case Pair(Point(int x, int y), _) -> x
```

---

### 💻 Code Example

```java
// instanceof pattern — Java 16
Object obj = "Hello, patterns!";

// Before (3 steps, cast is redundant but required):
if (obj instanceof String) {
    String s = (String) obj;   // redundant cast
    System.out.println(s.toUpperCase());
}

// After (1 step — obj tested AND bound):
if (obj instanceof String s) {
    System.out.println(s.toUpperCase()); // s is String — guaranteed
}

// Negation works too:
if (!(obj instanceof String s)) {
    throw new IllegalArgumentException("Expected String");
}
// s not in scope here — compiler enforces this
```

```java
// Switch patterns — Java 21
sealed interface Shape permits Circle, Rectangle, Triangle {}
record Circle(double radius)         implements Shape {}
record Rectangle(double w, double h) implements Shape {}
record Triangle(double base, double h) implements Shape {}

double area(Shape shape) {
    return switch (shape) {
        case Circle c    -> Math.PI * c.radius() * c.radius();
        case Rectangle r -> r.w() * r.h();
        case Triangle t  -> 0.5 * t.base() * t.h();
        // No default — sealed Shape, all cases covered → compile error if any missing
    };
}
```

```java
// Guarded patterns
String classify(Object obj) {
    return switch (obj) {
        case Integer i when i < 0    -> "negative";
        case Integer i when i == 0   -> "zero";
        case Integer i               -> "positive";
        case String s when s.isEmpty() -> "empty string";
        case String s                -> "string: " + s;
        case null                    -> "null value";
        default                      -> "unknown: " + obj;
    };
}
```

```java
// Record deconstruction patterns — Java 21
record Point(int x, int y) {}
record Segment(Point start, Point end) {}

void printSegment(Object obj) {
    if (obj instanceof Segment(Point(int x1, int y1), Point(int x2, int y2))) {
        System.out.printf("(%d,%d) → (%d,%d)%n", x1, y1, x2, y2);
        // All four coordinates bound directly — no .start().x() chains
    }
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Pattern matching is just syntactic sugar for casting | It's a new language feature with scoping rules and exhaustiveness checking |
| Bound variable `s` is available everywhere after `instanceof` | Scoped to the true branch only — compiler enforces this |
| You need a sealed class for switch patterns | Any type works; sealed gives exhaustiveness (no default needed) |
| Guarded patterns use `&&` inside case | Use `when` keyword: `case String s when s.length() > 5` |
| Pattern matching replaces all `instanceof` usage | Still use bare `instanceof` for simple boolean checks without binding |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Using bound variable outside true branch**

```java
if (obj instanceof String s) {
    System.out.println(s); // ✅ fine
}
System.out.println(s); // ❌ compile error — s not in scope here
```

**Pitfall 2: Ordering matters in switch — more specific before general**

```java
// ❌ Wrong — Integer case unreachable; Number catches it first
switch (obj) {
    case Number n  -> "number: "324"integer: " + i; // Compile error: dominated by prior pattern
}

// ✅ Correct — specific first
switch (obj) {
    case Integer i -> "integer: " + i;
    case Number n  -> "number: "324"null";
    case String s -> "string: " + s;
    default       -> "other";
}
```

---

### 🔗 Related Keywords

- **[Sealed Classes (Java 17+)](./063 — Sealed Classes (Java 17+).md)** — enables exhaustive switch without default
- **Records (Java 16+)** — deconstruction patterns work on records
- **Switch Expressions (Java 14+)** — pattern matching runs inside switch expressions
- **Generics** — generic types can appear in type patterns
- **instanceof** — pattern matching extends this operator

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Combine type-test + cast + binding into one   │
│              │ expression; enables exhaustive type dispatch  │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Any instanceof-cast-use chain; type dispatch  │
│              │ over a sealed hierarchy; record deconstruction│
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Simple boolean type check with no variable    │
│              │ binding needed — bare instanceof is clearer   │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Test + cast + bind in one step —             │
│              │  the compiler does the work you repeat"       │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ Sealed Classes → Records → Switch Expressions │
│              │ → Guarded Patterns → Deconstruction Patterns  │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A switch expression over a sealed interface with 4 permitted types has no default. You add a 5th permitted type. What happens at compile time across all switch expressions in the codebase? Why is this better than a runtime exception?

**Q2.** Can you use pattern matching in a regular `if` condition combined with `&&`? What scoping rules apply when you do `if (obj instanceof String s && s.length() > 0)`?

**Q3.** How do guarded patterns differ from a case with an `if` inside the arrow body? Is there a difference in exhaustiveness checking?

