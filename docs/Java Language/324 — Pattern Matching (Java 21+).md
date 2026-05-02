---
layout: default
title: "Pattern Matching (Java 21+)"
parent: "Java Language"
nav_order: 324
permalink: /java-language/pattern-matching/
number: "0324"
category: Java Language
difficulty: ★★★
depends_on: Sealed Classes (Java 17+), Records (Java 16+), Generics, Inheritance
used_by: Sealed Classes (Java 17+), Records (Java 16+)
related: Sealed Classes (Java 17+), Records (Java 16+), invokedynamic
tags:
  - java
  - pattern-matching
  - type-safety
  - deep-dive
  - java21
---

# 0324 — Pattern Matching (Java 21+)

⚡ TL;DR — Pattern matching combines type testing and binding into a single expression, and when used with sealed types enables exhaustive, compiler-verified dispatch that replaces error-prone `instanceof` chains and explicit casts.

| #0324 | Category: Java Language | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Sealed Classes (Java 17+), Records (Java 16+), Generics, Inheritance | |
| **Used by:** | Sealed Classes (Java 21+), Records (Java 16+) | |
| **Related:** | Sealed Classes (Java 17+), Records (Java 16+), invokedynamic | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before pattern matching, type-based dispatch in Java required a verbose, error-prone pattern:
```java
if (shape instanceof Circle) {
    Circle c = (Circle) shape; // redundant cast
    return Math.PI * c.getRadius() * c.getRadius();
} else if (shape instanceof Rectangle) {
    Rectangle r = (Rectangle) shape;
    return r.getWidth() * r.getHeight();
}
```
Three problems: (1) the `instanceof` test is immediately followed by a cast that the compiler knows is safe — yet requires explicit syntax; (2) no exhaustiveness checking — if a new `Triangle` subtype is added, silence; (3) verbose nesting bloat for deeply structured data.

**THE BREAKING POINT:**
An AST interpreter processes 20 node types. The evaluation function chains 20 `instanceof` checks and 20 casts. Every new node type requires adding to 8 different functions, each with the same cast pattern. One function is missed — a `NullPointerException` in production when the new node type is encountered.

**THE INVENTION MOMENT:**
This is exactly why **Pattern Matching** was created — to combine the type test and binding into one expression, and to pair with sealed types for compile-enforced exhaustiveness that catches missing cases before deployment.

---

### 📘 Textbook Definition

**Pattern Matching** in Java is a family of language features (JEP 305 preview in Java 14, finalized in Java 16 for `instanceof`; JEP 441 for `switch` finalized in Java 21) that allow matching a value against a pattern — a combination of a type test and a binding — in a single expression. `instanceof` patterns bind the matched variable: `if (obj instanceof String s)` tests and binds in one step. `switch` expressions support type patterns, guarded patterns (`case String s when s.length() > 0`), and record deconstruction patterns (`case Point(int x, int y)` — directly destructuring record components). Combined with sealed types, switch expressions are verified exhaustive by the compiler.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Pattern matching tests a type AND binds a variable in one expression — no separate cast needed.

**One analogy:**
> Airport security at a customs booth: the officer checks your passport (type test), and if valid, immediately addresses you by name on the passport (variable binding) — one action, not two separate steps. Pattern matching is the same: `if (person instanceof Passenger p)` checks and names in one expression.

**One insight:**
Pattern matching is most powerful when combined with sealed types and `switch` expressions. The three-way combination — sealed hierarchy (closed types) + records (structured data) + pattern switch (exhaustive dispatch) — gives Java algebraic data type power comparable to Haskell or Rust, with compile-time correctness guarantees previously impossible in Java.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A pattern matches a value if the value satisfies the test AND binds any declared variables.
2. `switch` pattern expressions over sealed types are exhaustive — all permitted subtypes must have a case.
3. Pattern variables are only in scope where the compiler can prove the match succeeded.

**DERIVED DESIGN:**
Given invariant 1: `instanceof String s` tests `obj != null && obj instanceof String`, then binds `s` for use within the scope where the match is proven. Flow-typing ensures `s` is only accessible where the test was provably true.

Given invariant 2: the combination of sealed types + switch expressions creates sum-type dispatch — the compiler verifies the switch covers all permitted subtypes. Adding a new type to the sealed hierarchy breaks every exhaustive switch.

Given invariant 3: `if (obj instanceof String s && s.length() > 0) { use(s); }` — `s` is in scope in the body. But `if (!(obj instanceof String s)) { use(s); }` — compile error: `s` not in scope in the else branch.

```
Pattern types:
  Type pattern:     case Circle c
  Guarded pattern:  case Circle c when c.radius() > 0
  Record pattern:   case Point(int x, int y)
  Nested record:    case Rect(Point(int x1,int y1), ...)
```

**THE TRADE-OFFS:**
**Gain:** Eliminates redundant casts; exhaustive checking with sealed types; enables algebraic data processing; cleaner visitor-pattern replacement.
**Cost:** Requires Java 21+; record deconstruction patterns require Java 21 (record patterns in switch); nested patterns can become complex; `default` suppresses exhaustiveness checking.

---

### 🧪 Thought Experiment

**SETUP:**
An expression evaluator for a sealed `Expr` hierarchy: `Num(int)`, `Add(Expr, Expr)`, `Mul(Expr, Expr)`.

WITHOUT PATTERN MATCHING:
```java
int eval(Expr e) {
    if (e instanceof Num) {
        return ((Num) e).value();  // redundant cast
    } else if (e instanceof Add) {
        Add a = (Add) e;           // redundant cast
        return eval(a.left()) + eval(a.right());
    }
    throw new RuntimeException("Unknown: " + e); // non-exhaustive
}
```

WITH PATTERN MATCHING (Java 21):
```java
int eval(Expr e) {
    return switch (e) {
        case Num(int v)       -> v;
        case Add(var l, var r) -> eval(l) + eval(r);
        case Mul(var l, var r) -> eval(l) * eval(r);
        // Compiler verifies exhaustiveness — no throw needed
    };
}
```

**THE INSIGHT:**
Pattern matching with sealed types turns the visitor pattern's boilerplate into a single expression. The compiler proves the switch is exhaustive at compile time. Adding `Sub` to the `Expr` hierarchy breaks the `eval` switch — a compile error, not a runtime exception.

---

### 🧠 Mental Model / Analogy

> Pattern matching is like a sorting machine with shape-specific slots. A coin goes through the first slot that matches its shape — round slot for pennies, rectangular for cards. Each slot not only sorts but also labels the item for what to do next. You know the machine handles all shapes because the manufacturer listed all slot shapes explicitly.

- "Shape-specific slot" → type pattern (`case Circle c`).
- "Labels the item" → binds the variable (`c` is typed as `Circle`).
- "Manufacturer's list" → sealed type `permits` clause.
- "Machine handles all shapes" → exhaustiveness check.

Where this analogy breaks down: The sorting machine processes each item once. Java's pattern switch tries cases in order — the first matching case wins, unlike a machine that might try all slots simultaneously.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Instead of checking "is this a Dog?" and then separately "name the dog", pattern matching does both at once: "if this is a Dog, call it `fido`." It's a shortened syntax that also enables the compiler to warn you when you miss a case.

**Level 2 — How to use it (junior developer):**
Use `instanceof` patterns: `if (obj instanceof String s)` — no explicit cast. Use `switch` with type patterns: `case Circle c ->`. Add `when` guards for conditions: `case String s when s.isBlank()`. These require Java 21+; `instanceof` pattern only needs Java 16+. Always use `switch` expressions (not statements) to get exhaustiveness checking.

**Level 3 — How it works (mid-level engineer):**
`instanceof` with a pattern uses flow-typing: the compiler tracks which branches have proven a type, making the variable available in scope. In `switch`, the JVM uses `invokedynamic` with a bootstrap method that performs type checks and binding efficiently. Record deconstruction patterns call the record's accessor methods and bind the result — `case Point(int x, int y)` calls `p.x()` and `p.y()`. Guarded patterns (`when`) evaluate the guard only after the type test succeeds.

**Level 4 — Why it was designed this way (senior/staff):**
Java's pattern matching is use-site — you write patterns where dispatch happens. Haskell uses pattern matching as the primary function definition syntax (declaration-site). Java's approach integrates into the existing method body syntax without restructuring how methods are defined. The JEP evolution (305→394→441) was careful to build up from simple `instanceof` patterns to complete `switch` patterns over sealed types, ensuring each step was independently useful and backward-compatible with existing code. The phased rollout as "preview" features allowed the community to provide feedback before finalization.

---

### ⚙️ How It Works (Mechanism)

**instanceof pattern (Java 16+):**
```java
// Old style: test + cast
if (obj instanceof String) {
    String s = (String) obj;
    System.out.println(s.length());
}

// Pattern matching style:
if (obj instanceof String s) {
    System.out.println(s.length()); // s is String, no cast
}

// With negation (note: s NOT in scope here):
if (!(obj instanceof String s)) {
    // s not available
} else {
    System.out.println(s.length()); // s in scope!
}
```

**Switch with type patterns (Java 21):**
```java
sealed interface Shape permits Circle, Rect, Triangle {}
record Circle(double r) implements Shape {}
record Rect(double w, double h) implements Shape {}
record Triangle(double b, double h) implements Shape {}

double area(Shape s) {
    return switch (s) {
        case Circle(double r)      -> Math.PI * r * r;
        case Rect(double w, double h) -> w * h;
        case Triangle(double b, double h) -> 0.5 * b * h;
    };
}
```

**Guarded patterns:**
```java
String classify(Object obj) {
    return switch (obj) {
        case Integer i when i < 0   -> "negative int";
        case Integer i when i == 0  -> "zero";
        case Integer i              -> "positive int: " + i;
        case String s when s.isEmpty() -> "empty string";
        case String s               -> "string: " + s;
        case null                   -> "null";
        default                     -> "other: " + obj;
    };
}
```

**Nested record deconstruction:**
```java
record Point(int x, int y) {}
record Line(Point start, Point end) {}

String describeOriginLine(Line line) {
    return switch (line) {
        case Line(Point(int 0, int 0), var end) ->
            "Line from origin to " + end;
        case Line(var start, Point(int 0, int 0)) ->
            "Line from " + start + " to origin";
        default -> "Ordinary line";
    };
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
[switch (paymentResult) {...]
    → [JVM: invokedynamic bootstrap for pattern switch]
    → [Types tested in case order]             ← YOU ARE HERE
    → [case Success(var amount): test + bind]
    → [Guard evaluated if present]
    → [Matching case executes]
    → [Compiler: verified all permits covered]
    → [Runtime: no unchecked fallthrough]
```

**FAILURE PATH:**
```
[New sealed subtype Disputed added to PaymentResult]
    → [Compiler: switch is no longer exhaustive]
    → [Compile error: switch with result type not exhaustive]
    → [Fix: add case Disputed in all switches]
    → [All services must be updated before compilation]
```

**WHAT CHANGES AT SCALE:**
In large codebases, pattern matching with sealed types makes type-based dispatch refactor-safe. When a domain type evolves, all dispatch points are found immediately by the compiler. The transition from `instanceof` chains to pattern switches is safe incrementally: `instanceof` patterns are backward-compatible additions; sealed + switch exhaustiveness is opt-in per type hierarchy.

---

### 💻 Code Example

Example 1 — Replacing instanceof chain:
```java
// BAD: old instanceof + cast pattern
String format(Object value) {
    if (value instanceof Integer) {
        return "Integer: " + ((Integer) value).intValue();
    } else if (value instanceof Double) {
        return "Double: " + ((Double) value).doubleValue();
    } else if (value instanceof String) {
        return "String: " + ((String) value).toUpperCase();
    }
    return "Unknown";
}

// GOOD: pattern matching switch
String format(Object value) {
    return switch (value) {
        case Integer i -> "Integer: " + i;
        case Double d  -> "Double: " + d;
        case String s  -> "String: " + s.toUpperCase();
        case null      -> "null";
        default        -> "Unknown: " + value;
    };
}
```

Example 2 — JSON value dispatch:
```java
sealed interface JsonValue
    permits JsonNull, JsonBool, JsonNumber, JsonString,
            JsonArray, JsonObject {}

String toDisplay(JsonValue v) {
    return switch (v) {
        case JsonNull()            -> "null";
        case JsonBool(boolean b)   -> String.valueOf(b);
        case JsonNumber(Number n)  -> n.toString();
        case JsonString(String s)  -> "\"" + s + "\"";
        case JsonArray(var items)  ->
            "[" + items.size() + " items]";
        case JsonObject(var fields)->
            "{" + fields.size() + " fields}";
    };
}
```

---

### ⚖️ Comparison Table

| Approach | Exhaustiveness | Type Safety | Java Version | Boilerplate | Best For |
|---|---|---|---|---|---|
| **Pattern matching switch** | Compiler-checked (sealed) | Compile-time | 21+ | Minimal | Sealed hierarchies, ADTs |
| instanceof + cast | None (open hierarchy) | Runtime cast | All | High | Simple type checks |
| Visitor pattern | Manual | Compile-time | All | Very high | Pre-Java-21 open hierarchies |
| Enum switch | Compiler-checked | Compile-time | All | Low | Constants without data |

How to choose: Use pattern switch over sealed types for any domain where the set of types is closed and known. Use `instanceof` patterns for simple individual type checks. Use Visitor for pre-Java-21 code or open hierarchies.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Pattern matching only works with sealed types | Pattern matching works with ANY type. The exhaustiveness benefit only applies to sealed types. Over `Object` you still need `default` |
| Record deconstruction patterns modify fields | Record patterns only bind values extracted via accessor methods — they are read-only. The `Point(int x, int y)` pattern extracts `p.x()` and `p.y()` without modifying the record |
| Guarded patterns (`when`) are evaluated first | Guards are only evaluated AFTER the type test succeeds. `case String s when s.length() > 0` first tests `instanceof String`, then evaluates `s.length() > 0`. The order matters for NPE safety |
| A default in switch always loses exhaustiveness | A `default` silences the exhaustiveness check. However, `default -> throw new AssertionError()` is a safe transitional pattern — it restores the runtime error but loses the compile-time check |
| Pattern matching is only a switch feature | `instanceof` pattern matching was finalized in Java 16. You can use `if (x instanceof Foo f)` without switch expressions in any Java 16+ code |

---

### 🚨 Failure Modes & Diagnosis

**Missing case after sealed hierarchy extension**

**Symptom:** Compile error: "switch expression does not cover all possible input values".

**Root Cause:** New permitted type added to sealed interface; not handled in exhaustive switch.

**Diagnostic:**
```bash
javac -source 21 MyHandler.java
# error: the switch expression does not cover all possible
# input values
```

**Fix:** Add the missing case to the switch, or add `default -> throw new AssertionError("Unhandled: " + value)` as a transitional measure.

**Prevention:** Run `javac` with full `-source 21` in CI. Treat "switch not exhaustive" as a build-blocking error.

---

**Variable Out of Scope (Flow Typing)**

**Symptom:** Compile error "cannot find symbol: variable s" after a negated `instanceof`.

**Root Cause:** Pattern variable scope follows flow typing — variable only in scope where compiler proves match succeeded.

**Diagnostic:**
```bash
javac MyClass.java
# error: cannot find symbol: s
# method: boolean isLong(Object obj)
```

**Fix:**
```java
// BAD: s not in scope after negated instanceof
if (!(obj instanceof String s)) return false;
// s is in scope here — flow-typed!
return s.length() > 100;

// Counter-intuitive but correct: s IS in scope after
// the negated check because we returned for non-String
```

**Prevention:** Understand flow-typing rules: pattern variable is in scope in the branch where the match is provably true.

---

**NullPointerException in Pattern Switch**

**Symptom:** `NullPointerException` thrown from `switch` expression at runtime.

**Root Cause:** Pre-Java-21, `switch` throws NPE when the selector is `null`. Java 21 allows `case null` explicitly.

**Diagnostic:**
```bash
# Stack trace: NullPointerException at switch ...
# The switch selector is null
```

**Fix:**
```java
// Java 21+: handle null explicitly in case
String result = switch (obj) {
    case null   -> "null value";
    case String s -> s.toUpperCase();
    default     -> obj.toString();
};
```

**Prevention:** Always add `case null` in pattern switches when the selector can be null.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Sealed Classes (Java 17+)` — sealed types enable exhaustive pattern matching; the combination is the primary value proposition
- `Records (Java 16+)` — record deconstruction patterns require records; understanding records is prerequisite for the most powerful patterns

**Builds On This (learn these next):**
- `invokedynamic` — the JVM mechanism underlying `switch` pattern dispatch at the bytecode level

**Alternatives / Comparisons:**
- `Sealed Classes (Java 17+)` — the type declaration counterpart; pattern matching is the consumption mechanism, sealed types are the declaration mechanism
- `Records (Java 16+)` — combined with patterns for algebraic data type deconstruction

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Type test + variable binding in one expr; │
│              │ switch dispatch over sealed hierarchies   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ instanceof + explicit cast is verbose and │
│ SOLVES       │ non-exhaustive; type dispatch bugs are    │
│              │ silent runtime errors                     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ With sealed types + pattern switch, the   │
│              │ compiler verifies all cases are handled   │
│              │ — new types cause compile errors, not bugs│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Type-based dispatch over sealed/closed    │
│              │ hierarchies; processing structured data   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple single-type test — plain           │
│              │ instanceof still fine; Java < 21          │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Compile-time safety vs Java 21+ required; │
│              │ sealed API changes are breaking           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Check the type AND name it — one step"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ invokedynamic → Sealed Classes →          │
│              │ Records                                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a sealed hierarchy: `sealed interface Notification permits Email, SMS, Push, InApp`. A method uses an exhaustive `switch` with no `default`. In a microservices deployment, Service A generates `Notification` objects and Service B pattern-matches them. Service A ships a update adding `Slack extends Notification` to the sealed hierarchy. Service B uses library v1 (old). Trace what happens at each layer: at compile time in Service B, at class loading time when B's code loads A's new class, and at `switch` dispatch time — and explain at exactly which point the JVM enforces the sealed contract.

**Q2.** Consider the "expression problem": you have a sealed hierarchy of types and a set of operations over them. Adding a new operation is easy (new function using pattern matching). Adding a new type is hard (all existing operations must be updated). Explain why the expression problem is "solved" differently by pattern matching (easy to add operations) versus the visitor pattern (easy to add types), and design a hybrid approach using sealed types with a default-throwing `switch` that provides compile-time safety for known operations while allowing new types to be added gradually without immediately breaking all operation implementations.

