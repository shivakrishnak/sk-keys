---
layout: default
title: "Sealed Classes (Java 17+)"
parent: "Java Language"
nav_order: 323
permalink: /java-language/sealed-classes/
number: "0323"
category: Java Language
difficulty: ★★★
depends_on: Inheritance, Records (Java 16+), Pattern Matching (Java 21+)
used_by: Pattern Matching (Java 21+), Records (Java 16+)
related: Records (Java 16+), Pattern Matching (Java 21+), Generics
tags:
  - java
  - sealed
  - type-safety
  - deep-dive
  - java17
---

# 0323 — Sealed Classes (Java 17+)

⚡ TL;DR — Sealed classes restrict which classes may extend them to an explicitly declared set, enabling exhaustive pattern matching over a closed type hierarchy — the Java equivalent of algebraic data types.

| #0323 | Category: Java Language | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Inheritance, Records (Java 16+), Pattern Matching (Java 21+) | |
| **Used by:** | Pattern Matching (Java 21+), Records (Java 16+) | |
| **Related:** | Records (Java 16+), Pattern Matching (Java 21+), Generics | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
A payment system models payment results as a class hierarchy: `PaymentResult`, extended by `Success`, `Failure`, `Pending`, `Refunded`. A method handling results uses `instanceof` chains. Without sealed classes, there is no compile-time guarantee that the chain is exhaustive. A new `Disputed` subtype is added — the handling code has been deployed to 12 microservices, none of which know about `Disputed`. All 12 silently fall through to a default case that throws `IllegalStateException("Unknown state")` or, worse, does nothing.

THE BREAKING POINT:
The `Disputed` branch is missing in the revenue recognition service. Disputed transactions are silently ignored. $2M in disputed payments is unrecognised in accounting for a quarter. The bug is found only during an audit.

THE INVENTION MOMENT:
This is exactly why **Sealed Classes** were created — to close a type hierarchy so the compiler knows all permitted subtypes and can verify that every `switch` expression handles every case, turning a runtime logic hole into a compile error in every consuming service.

---

### 📘 Textbook Definition

A **Sealed Class** (finalized in Java 17, JEP 409) is a class or interface declared with the `sealed` modifier and a `permits` clause that explicitly names all permitted direct subclasses. Each permitted subclass must be declared as `final`, `sealed`, or `non-sealed`. `final` closes the branch; `sealed` extends the sealed hierarchy; `non-sealed` opens the branch to arbitrary further extension. The compiler enforces: (1) all permitted subclasses must be in the same compilation unit or named module; (2) `switch` expressions over a sealed type are checked for exhaustiveness — a missing case is a compile error (not a warning).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Sealed classes say "only THESE types can extend me" — making the compiler's exhaustiveness checker know all possible cases.

**One analogy:**
> A sealed envelope comes with a printed list of who is allowed to open it: "Alice, Bob, or Carol only." If Dave tries to open it, the rule is broken. A sealed class is the same — only the listed subclasses are allowed. And because the list is finite and known, a sorter handling envelopes can be checked to ensure they handle every name on the list.

**One insight:**
The real value of sealed types is not inheritance control — it's exhaustive switching. When you `switch` on a sealed type in Java 17+, the compiler verifies you've handled every permitted subtype. Adding a new subtype automatically breaks every switch that doesn't handle it — turning a silent runtime bug into a visible compile error that propagates to every consumer.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. The set of permitted subclasses is finite and fully known at compile time.
2. Every direct permitted subclass must be in the same package (or named module) as the sealed class.
3. Every switch expression (not statement) over a sealed type is exhaustively checked by the compiler.

DERIVED DESIGN:
Given invariant 1, `switch` expressions can be proven exhaustive: if all `N` permitted subtypes have a case, the switch handles all possible values. The compiler rejects switches missing cases. This is the algebraic data type — a sum type whose variants are precisely enumerated.

Given invariant 3, adding a new permitted subtype (`case Disputed` to `PaymentResult`) forces every caller with a sealed switch to handle the new case or explicitly provide a default. This is safe change propagation by the type system.

```java
sealed interface PaymentResult
    permits Success, Failure, Pending, Refunded {}

record Success(BigDecimal amount) implements PaymentResult {}
record Failure(String reason) implements PaymentResult {}
record Pending(String reference) implements PaymentResult {}
record Refunded(BigDecimal amount) implements PaymentResult {}

// Exhaustive switch — compiler verifies all cases covered:
String describe(PaymentResult result) {
    return switch (result) {
        case Success s   -> "Paid: " + s.amount();
        case Failure f   -> "Failed: " + f.reason();
        case Pending p   -> "Pending: " + p.reference();
        case Refunded r  -> "Refunded: " + r.amount();
        // No default needed — all cases covered!
    };
}
// Add Disputed to permits → compile error here until handled
```

THE TRADE-OFFS:
Gain: Compiler-enforced exhaustive handling; closed type hierarchy for clear domain modeling; enables pattern matching; documents all valid states in one place.
Cost: Requires Java 17+; all permitted subclasses must be in same compilation unit (module limitation); `non-sealed` escape hatch weakens the guarantee; breaks "open-closed principle" — adding a new variant forces all consumers to update.

---

### 🧪 Thought Experiment

SETUP:
A shape rendering engine: `Shape` can be `Circle`, `Rectangle`, or `Triangle`. The `render()` function must handle all three.

WITHOUT SEALED CLASSES:
```java
void render(Shape s) {
    if (s instanceof Circle c) { drawCircle(c.r()); }
    else if (s instanceof Rectangle r) { drawRect(r); }
    // Triangle forgotten silently
    // New Polygon subtype added: nothing enforces handling
    // Bug: Polygon renders nothing, visible in production
}
```

WITH SEALED CLASSES:
```java
sealed interface Shape permits Circle, Rectangle, Triangle {}
// ...
String render(Shape s) {
    return switch (s) {
        case Circle c   -> drawCircle(c.r());
        case Rectangle r -> drawRect(r.w(), r.h());
        // COMPILE ERROR: Triangle case is missing!
    };
}
// After Triangle added to permits:
// Every switch MUST add case or default — no silent bugs
```

THE INSIGHT:
Without sealing, the type hierarchy is open — new subtypes can appear silently. With sealing, the hierarchy is closed — the compiler knows every possible type and can verify that every switch handles them all. The shift from runtime surprises to compile-time errors is the entire value.

---

### 🧠 Mental Model / Analogy

> A sealed type is like a formal menu at a restaurant. The kitchen makes exactly these 5 dishes — no substitutions. When a waiter takes orders, the restaurant can verify at order time (compile time) that every order is for a listed dish. No order can arrive for an unlisted dish. A regular class hierarchy is an open menu where new dishes can appear any time — the waiter can only check at serving time (runtime).

"Listed dishes only" → permitted subclasses only.
"Order verification at order time" → exhaustiveness check at compile time.
"New dish added: waiter must be retrained" → new subtype: all switch expressions must be updated or won't compile.

Where this analogy breaks down: `non-sealed` is like putting "other items available" at the bottom of the menu — it re-opens that branch. A `non-sealed` permitted subclass breaks the exhaustiveness guarantee for anything that extends it.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A sealed class declares "only these specific classes can extend me." If you try to create a new subclass not on the list, the compiler refuses. This lets you write code that handles every possible type without a default fallback, and the compiler checks you haven't missed anything.

**Level 2 — How to use it (junior developer):**
Declare `sealed interface Shape permits Circle, Rectangle {}`. Each permitted class must be in the same file or package. Make permit subclasses `final` (closed), `sealed` (further controlled), or `non-sealed` (reopened). Use with `switch` expressions using pattern matching: `switch(shape) { case Circle c -> ...; case Rectangle r -> ...; }` — no `default` needed if all cases covered.

**Level 3 — How it works (mid-level engineer):**
The `permits` clause is stored in the class file (`PermittedSubclasses` attribute). The compiler reads this attribute when checking `switch` expressions to determine if coverage is exhaustive. The JVM also validates at class loading time that actual subclasses are in the permitted list — `UnsupportedClassVersionError` or `IncompatibleClassChangeError` otherwise. Sealed types pair with records to form pattern-matchable algebraic data types: `record Circle(double r) implements Shape implements Serializable`.

**Level 4 — Why it was designed this way (senior/staff):**
Sealed types were designed together with pattern matching (JEP 406, 441, 441) as a unified feature for algebraic data type modeling. Haskell's data types, Scala's sealed traits, Rust's enums, and Swift's enums are all variants of this concept. Java's design explicitly allows `non-sealed` as an escape hatch — a compromise between strict algebraic types and Java's tradition of open extensibility. The "same compilation unit" restriction ensures that the full set of permitted types is visible to the compiler and can be verified statically. Future enhancements (Project Amber) will extend the pattern matching and deconstruction to work even more naturally with sealed hierarchies.

---

### ⚙️ How It Works (Mechanism)

**Sealed hierarchy declaration:**
```java
// Top-level sealed interface
sealed interface Expr
    permits Num, Add, Mul, Neg {}

// Leaf nodes: final
record Num(int value)   implements Expr {}
record Add(Expr l, Expr r) implements Expr {}
record Mul(Expr l, Expr r) implements Expr {}
record Neg(Expr expr)    implements Expr {}
```

**Exhaustive pattern matching (Java 21):**
```java
int eval(Expr expr) {
    return switch (expr) {
        case Num(int v)         -> v;
        case Add(var l, var r)  -> eval(l) + eval(r);
        case Mul(var l, var r)  -> eval(l) * eval(r);
        case Neg(var e)         -> -eval(e);
        // No default: compiler verifies exhaustiveness
    };
}
```

**Hierarchical sealing (sealed → sealed):**
```java
sealed interface Vehicle
    permits Car, Truck, Motorcycle {}

sealed interface Car
    permits Sedan, SUV, Hatchback
    extends Vehicle {}

final class Sedan implements Car {}
final class SUV   implements Car {}
final class Hatchback implements Car {}
```

**non-sealed escape hatch:**
```java
sealed interface Plugin permits CorePlugin, ExtPlugin {}
final class CorePlugin implements Plugin {}
// non-sealed: anyone can extend ExtPlugin
// Switch over Plugin loses exhaustiveness for ExtPlugin subtypes
non-sealed class ExtPlugin implements Plugin {}
class ThirdPartyPlugin extends ExtPlugin {} // now allowed
```

**Class file inspection:**
```bash
javap -verbose PaymentResult.class | grep -A5 "PermittedSubclasses"
# PermittedSubclasses:
#   Success
#   Failure
#   Pending
#   Refunded
```

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
[Developer adds Disputed to PaymentResult permits]
    → [javac compiles PaymentResult.java]
    → [Compiler updates PermittedSubclasses attr]  ← YOU ARE HERE
    → [All callers with switch(paymentResult) compile]
    → [Missing Disputed case → compile error per caller]
    → [Each caller updates their switch]
    → [All callers deployed: Disputed handled everywhere]
    → [No silent fallthrough — $2M bug prevented]
```

FAILURE PATH:
```
[switch with default added to suppress compile error]
    → [Disputed falls to default: "Unknown case" logged]
    → [Silent skip — same runtime problem as before]
    → [Fix: remove default, handle Disputed explicitly]
```

WHAT CHANGES AT SCALE:
In a large monorepo with many services, a sealed type change propagates compile errors to every consumer immediately — forcing all teams to update before the new code ships. This is the "Strangler Fig" pattern's compile-time equivalent: the type system itself prevents gradual, uncontrolled migration. Balancing safety (no default) with change velocity (teams need time to update) leads to the transitional helper pattern: keep a default that throws with a deprecation warning, remove it in the next API version.

---

### 💻 Code Example

Example 1 — Sealed hierarchy for event modeling:
```java
// Sealed event hierarchy for an order system
sealed interface OrderEvent
    permits OrderPlaced, OrderConfirmed,
            OrderShipped, OrderCancelled {}

record OrderPlaced(Long orderId, BigDecimal total)
    implements OrderEvent {}
record OrderConfirmed(Long orderId, String confirmCode)
    implements OrderEvent {}
record OrderShipped(Long orderId, String trackingId)
    implements OrderEvent {}
record OrderCancelled(Long orderId, String reason)
    implements OrderEvent {}
```

Example 2 — Exhaustive handler (no default needed):
```java
// Compiler verifies ALL cases handled — no default needed
String summarize(OrderEvent event) {
    return switch (event) {
        case OrderPlaced(var id, var total) ->
            "Order #" + id + " placed for " + total;
        case OrderConfirmed(var id, var code) ->
            "Order #" + id + " confirmed: " + code;
        case OrderShipped(var id, var tracking) ->
            "Order #" + id + " shipped: " + tracking;
        case OrderCancelled(var id, var reason) ->
            "Order #" + id + " cancelled: " + reason;
    };
}
```

Example 3 — JSON deserialization with sealed types (Jackson):
```java
@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    property = "type"
)
@JsonSubTypes({
    @JsonSubTypes.Type(value = Success.class, name="success"),
    @JsonSubTypes.Type(value = Failure.class, name="failure")
})
sealed interface PaymentResult
    permits Success, Failure {}
// Jackson uses name registry: safe, enumerable, no RCE risk
```

Example 4 — guard clauses in sealed switches (Java 21):
```java
sealed interface Response
    permits OkResponse, ErrorResponse {}
record OkResponse(int status, String body)
    implements Response {}
record ErrorResponse(int status, String message)
    implements Response {}

String format(Response r) {
    return switch (r) {
        case OkResponse(var s, var b) when s == 200 ->
            "OK: " + b;
        case OkResponse(var s, var b) ->
            "Non-200 OK " + s + ": " + b;
        case ErrorResponse(var s, var m) when s >= 500 ->
            "Server error " + s + ": " + m;
        case ErrorResponse(var s, var m) ->
            "Client error " + s + ": " + m;
    };
}
```

---

### ⚖️ Comparison Table

| Mechanism | Type Safety | Exhaustiveness | Java Version | Extensible | Best For |
|---|---|---|---|---|---|
| **Sealed classes** | Compile-time | Compiler-checked | 17+ | No (by design) | Closed domain models, ADTs |
| Enum | Compile-time | Compiler-checked | All | No | Fixed constants with no data |
| Abstract class + instanceof | Runtime only | Not checked | All | Yes | Open hierarchies |
| Visitor pattern | Runtime | Manual/convention | All | Complex | Open hierarchies with dispatch |

How to choose: Use sealed interfaces with records when modeling a closed domain with data (payment states, AST nodes, HTTP responses). Use enums when variants carry no data. Use abstract classes for open hierarchies designed for extension.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `sealed` prevents inheritance everywhere | `sealed` restricts direct subclasses only to the listed `permits`. A `non-sealed` permitted subclass can be extended arbitrarily. And final permitted subclasses are completely closed |
| You always need a `default` in switch with sealed types | For switch EXPRESSIONS over sealed types where all permits are handled, no `default` is needed — and adding one suppresses the exhaustiveness check, making it less safe |
| Sealed classes are the same as enums | Enums are constants with no per-value data fields (only shared static data). Sealed classes with record subtypes can carry different data per variant. `record Success(BigDecimal amount)` cannot be an enum variant |
| Adding a subtype to sealed is backward compatible | It is NOT backward compatible for any consumer that uses exhaustive switch without `default`. Adding a new permitted type is a breaking API change that forces all exhaustive switches to be updated |
| `permits` must list classes in the same file | Classes in the same PACKAGE or named module can be permitted even if in separate files. In unnamed modules (most apps), they must be in the same package |

---

### 🚨 Failure Modes & Diagnosis

**IncompatibleClassChangeError at Runtime (Subclass Violation)**

Symptom:
`java.lang.IncompatibleClassChangeError: class FraudResult is not a permitted subtype`.

Root Cause:
A class compiled against an older version of a sealed interface (before sealing was added, or with a different permits list) is loaded at runtime after the sealed interface was updated.

Diagnostic:
```bash
# Check sealed class bytecode:
javap -verbose PaymentResult.class \
  | grep -A10 PermittedSubclasses

# Check subclass claims:
javap -verbose FraudResult.class | grep "implements"
```

Fix:
Ensure all classes and sealed interfaces are compiled together and deployed together. Never allow binary-incompatible versions of sealed hierarchies to coexist at runtime. Use module versions to enforce compatibility.

Prevention: Treat sealed hierarchy changes as breaking API changes requiring coordinated deployment.

---

**Missing Case Causes default to Silently Handle New Variant**

Symptom:
New variant added to sealed hierarchy. No compile error because switch has `default`. New variant handled by generic default case — behaviour is wrong but no exception.

Root Cause:
`default` in a switch over a sealed type acts as a catch-all that suppresses the exhaustiveness benefit. The new case falls to the default silently.

Diagnostic:
```bash
# Search for switch on sealed types with a default:
grep -rn "switch.*PaymentResult\|default ->" \
    --include="*.java" .
# Any switch with 'default' over a sealed type is suspect
```

Fix:
```java
// BAD: default suppresses exhaustiveness check
String handle(PaymentResult r) {
    return switch (r) {
        case Success s -> "paid";
        case Failure f -> "failed";
        default -> "unknown"; // silently handles new cases
    };
}

// GOOD: no default — compiler tells you about new cases
String handle(PaymentResult r) {
    return switch (r) {
        case Success s  -> "paid";
        case Failure f  -> "failed";
        case Pending p  -> "pending";  // must add each case
        case Refunded r2 -> "refunded";
    };
}
```

Prevention: Never add `default` to switch expressions over sealed types unless you explicitly intend to handle future subtypes generically. Use `default -> throw new AssertionError("New sealed type not handled: " + r)` as a safety net during transition.

---

**non-sealed Escape Hatch Breaks Exhaustiveness**

Symptom:
`switch` over a sealed type reports "not exhaustive" even though all listed `permits` subclasses are handled.

Root Cause:
One of the permitted subclasses is `non-sealed`, meaning the compiler cannot guarantee it has no further subtypes. The switch can't be exhaustive if an unlisted type could appear.

Diagnostic:
```bash
javac MyService.java
# error: the switch expression does not cover all possible
# input values
# Check which permitted subclass is non-sealed:
javap -verbose Shape.class | grep "PermittedSubclasses" -A10
```

Fix:
```java
// Option 1: change non-sealed to final (if no extension needed)
final class ExtPlugin implements Plugin {}

// Option 2: add explicit default for the non-sealed branch
String describe(Plugin p) {
    return switch (p) {
        case CorePlugin c -> "core";
        // non-sealed ExtPlugin: exhaustiveness broken
        default -> "extension: " + p.getClass().getSimpleName();
    };
}
```

Prevention: Use `non-sealed` only when third-party extension is genuinely needed. Document the exhaustiveness tradeoff explicitly in the API contract.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Inheritance` — sealed classes restrict inheritance; understanding the Java inheritance model is prerequisite
- `Records (Java 16+)` — sealed interfaces pair with records as the most idiomatic combination for algebraic data types; understanding records is required

**Builds On This (learn these next):**
- `Pattern Matching (Java 21+)` — sealed types enable exhaustive pattern matching; the two features are designed together and most powerful in combination
- `invokedynamic` — the JVM mechanism underlying the latest switch expression implementations; understanding it explains the performance characteristics

**Alternatives / Comparisons:**
- `Records (Java 16+)` — the data declaration counterpart to sealed types' control declaration; together they form algebraic data types
- `Pattern Matching (Java 21+)` — the consumption mechanism that sealed types enable; sealed types declare the structure, pattern matching processes it

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Class or interface restricting its        │
│              │ subclasses to an explicitly named set     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Open hierarchies allow new subtypes to    │
│ SOLVES       │ appear silently, breaking switch handlers │
│              │ without any compile-time warning          │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Adding a new permitted subtype immediately│
│              │ causes compile errors in all exhaustive  │
│              │ switches — turning runtime bugs into      │
│              │ compile-time errors before deploy        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Modeling closed domain states (payment    │
│              │ results, HTTP responses, AST nodes) where │
│              │ all variants are known and enumerable     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Open extension points designed for third- │
│              │ party developers to extend (plugins, SPIs)│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Compile-time exhaustiveness vs breaking   │
│              │ API change when adding new variants       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A closed menu of types where the compiler│
│              │  checks you've handled every dish"        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Pattern Matching → Records →              │
│              │ invokedynamic                             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A payment processing library defines `sealed interface PaymentResult permits Success, Failure, Pending` and is published as a Maven dependency (version 1.0). A consuming service has an exhaustive `switch` over `PaymentResult` with no `default`. The library team releases version 2.0, adding `Disputed` to the `permits` clause. Trace exactly what happens in a Kubernetes deployment using rolling updates: some pods run with library v1.0, some with v2.0. What runtime errors occur? At which specific class-loading point does the JVM enforce the sealed contract? How does the `UnsupportedClassVersionError` vs `IncompatibleClassChangeError` differ in this scenario?

**Q2.** Haskell's `data` types and Rust's `enum` are both algebraic data types (ADTs). Java's sealed interfaces with records are a similar concept but implemented differently. Compare: in Rust, adding a new `enum` variant is a breaking change detected by the compiler in pattern matches that omit it. In Java, adding a new sealed subtype is also a compile error for exhaustive switches. However, Java's `default` escape hatch and Rust's `_` wildcard both "solve" the exhaustiveness problem. Explain the precise semantic difference between a Rust `_` in a `match` and a Java `default` in a `switch` expression — specifically, why one is considered a safe pattern and the other is considered a design smell in sealed type hierarchies.

