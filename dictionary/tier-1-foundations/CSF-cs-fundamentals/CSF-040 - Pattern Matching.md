---
id: CSF-040
title: Pattern Matching
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★☆
depends_on:
used_by:
related:
tags:
  - csf
  - intermediate
  - pattern
status: draft
version: 2
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Dictionary"
nav_order: 40
permalink: /csf/pattern-matching/
---

# CSF-040 - Pattern Matching

⚡ TL;DR - Pattern matching is a control flow mechanism that simultaneously tests the shape of a value and binds its components to variables, replacing chains of `instanceof` checks and casts with expressive, exhaustive branching.

| CSF-040         | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | CSF-020, CSF-038, CSF-046             |                 |
| **Used by:**    | CSF-046, CSF-047, CSF-048             |                 |
| **Related:**    | CSF-020, CSF-038, CSF-046, CSF-047    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Working with heterogeneous data (a value that might be one of
several types or shapes) requires chains of `instanceof` checks
and manual casts:

```java
if (expr instanceof Literal) {
    Literal lit = (Literal) expr; // manual cast after check
    ...
} else if (expr instanceof BinaryOp) {
    BinaryOp op = (BinaryOp) expr;
    ...
} // what if you forget a case? No compiler warning!
```

This is verbose, repetitive, and non-exhaustive.

**THE BREAKING POINT:**
Any code that processes algebraic data types (ASTs, events,
messages, sum types) degenerates into verbose cast-ladders
without pattern matching. Each new shape added to the type
must be manually discovered and added to every switch chain.
Compilers can't warn you about missing cases.

**THE INVENTION MOMENT:**
ML (1973) introduced pattern matching as a core language
feature: a `match` expression tests the structure of a value
and binds its components simultaneously, with exhaustiveness
checking. Haskell, OCaml, Rust, Scala all built on this.
Java added pattern matching for `instanceof` in Java 16 and
sealed classes + switch expressions in Java 17+.

**EVOLUTION:**
Pattern matching evolved from simple case discrimination to
deep structural decomposition (nested patterns), guard
clauses (`when` conditions), and exhaustiveness checking.
Rust's `match` is the most rigorous: it is an expression,
must be exhaustive, and uses RAII for resource management
along with matched bindings.

---

### 📘 Textbook Definition

**Pattern matching** is a mechanism for inspecting the structure
of a value against one or more _patterns_ and, upon a match,
binding components of the value to local names. A pattern can
test: the type of a value (`instanceof` patterns), the shape
of an algebraic data type (constructor patterns), literal values,
or structural properties (destructuring). Exhaustiveness
checking ensures all possible shapes are handled, eliminating
unhandled cases at compile time.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Pattern matching tests what a value looks like and unpacks it in one step, with compiler-enforced exhaustiveness.

**One analogy:**

> Pattern matching is like a postal sorting machine. Each parcel
> (value) is tested against shapes (patterns): small box? medium
> envelope? oversized? The machine routes it to the right chute
> and simultaneously reads the label (binds variables). If no
> chute handles the parcel, the machine flags an error (non-exhaustive).

**One insight:**
Exhaustiveness checking is the key feature. When you add a new
shape to a sum type, the compiler tells you every match expression
that must be updated. This is a type-safe "open for extension"
mechanism.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A match expression tests all cases of a value's shape.
2. Exhaustiveness: the compiler requires all possible shapes to be handled.
3. Each arm binds the matched components to local names (destructuring).
4. Patterns can be nested: match inside a match is the same as a deep structural test.
5. The first matching arm wins; patterns are tested in order.

**DERIVED DESIGN:**

- **Literal patterns** — `case 0:`, `case "hello":`
- **Type patterns** — `case String s:` (Java 21), `case Literal(val):`
- **Deconstruct patterns** — `case Point(x, y):` binds `x` and `y`
- **Guard clauses** — `case Point(x, y) when x > 0:`
- **Wildcard** — `_` matches anything, discards it

**THE TRADE-OFFS:**
**Gain:** Exhaustiveness checking; no casts; readable.
**Cost:** Can produce large `match` blocks for wide types.
Mutable state in arms can make exhaustiveness analysis complex.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Discriminated unions / sum types require exhaustive dispatch.
**Accidental:** `instanceof` chains (pre-Java 16), manual cast after check,
non-exhaustive switch with silent fall-through.

---

### 🧪 Thought Experiment

**SETUP:**
You process AST nodes: `Num(int)`, `Add(Expr, Expr)`, `Mul(Expr, Expr)`.

**WITHOUT PATTERN MATCHING (Java <17):**

```java
public int eval(Expr expr) {
    if (expr instanceof Num) {
        return ((Num) expr).value;
    } else if (expr instanceof Add) {
        Add add = (Add) expr;
        return eval(add.left) + eval(add.right);
    } else if (expr instanceof Mul) {
        Mul mul = (Mul) expr;
        return eval(mul.left) * eval(mul.right);
    }
    throw new IllegalStateException(); // missing case: no compile check!
}
```

**WITH PATTERN MATCHING (Java 21 switch):**

```java
public int eval(Expr expr) {
    return switch (expr) {
        case Num(int v)       -> v;
        case Add(var l, var r) -> eval(l) + eval(r);
        case Mul(var l, var r) -> eval(l) * eval(r);
    }; // compiler: exhaustive for sealed Expr
}
```

**THE INSIGHT:**
The pattern-matching version is not just shorter; it's _safer_.
If you add `Neg(Expr)` to the sealed `Expr` hierarchy, the
compiler finds every non-exhaustive match. No `IllegalStateException`
at runtime.

---

### 🧠 Mental Model / Analogy

> Pattern matching is like a switchboard operator in a hotel.
> Each call (value) is tested against extensions (patterns).
> "Room 101?" — test type. "A call for Alice in room 203?" —
> deep structural test. The operator simultaneously routes
> (control flow) and announces who called (binds variables).
> If no extension matches, the switchboard must handle the
> unrouted call (wildcard / exhaustive default).

**Element mapping:**

- Incoming call = value being matched
- Extension test = pattern
- Routing to room = executing match arm
- Announcing who called = binding matched components to names
- "Unknown extension" error = non-exhaustive match

Where this analogy breaks down: pattern matching in functional
languages is used for values, not just objects with type hierarchies.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Pattern matching is a smarter `switch`: it checks what something
is, opens it up, and gives you its parts — all in one step.
And if you forget a case, the compiler tells you.

**Level 2 - How to use it (junior developer):**
In Rust: use `match` instead of chained `if let`. In Java 21:
use `switch` expressions with sealed classes. Prefer pattern
matching over `instanceof` + cast chains. Always handle the
wildcard `_` case last (or remove it if the match is exhaustive).

**Level 3 - How it works (mid-level engineer):**
Pattern matching compiles to optimised decision trees. For
a sealed class with 5 variants, the compiler generates an
optimal sequence of type tests (possibly a jump table or
binary tree). In Rust, exhaustiveness is checked using a
match coverage algorithm: each pattern is a set of value
descriptions; all cases must be covered.

**Level 4 - Why it was designed this way (senior/staff):**
Pattern matching is the canonical way to consume algebraic data
types (ADTs). A function `eval: Expr -> Int` must handle every
case of `Expr`. The compiler enforces this via exhaustiveness.
This is the _algebraic_ property: a product type (struct) is
unpacked by construction; a sum type (sealed class/enum) is
unpacked by pattern matching. The two operations are exact
inverses, and the type system can prove totality.

**Expert Thinking Cues:**

- When adding a new variant to a sealed type: pattern matching finds all affected match sites
- When seeing `instanceof` chains: could this be a sealed interface + pattern match?
- When reviewing a `switch`: is the default meaningful, or is it hiding a missing case?

---

### ⚙️ How It Works (Mechanism)

**Rust match (simplified):**

```rust
enum Shape { Circle(f64), Rect(f64, f64) }

let area = match shape {
    Shape::Circle(r)    => std::f64::consts::PI * r * r,
    Shape::Rect(w, h)   => w * h,
    // No wildcard needed: compiler verifies exhaustive
};
```

**Java 21 sealed + switch:**

```java
sealed interface Expr permits Num, Add, Mul {}
record Num(int val) implements Expr {}
record Add(Expr l, Expr r) implements Expr {}
record Mul(Expr l, Expr r) implements Expr {}

int eval(Expr e) {
    return switch (e) {
        case Num(int v)        -> v;
        case Add(var l, var r) -> eval(l) + eval(r);
        case Mul(var l, var r) -> eval(l) * eval(r);
    };
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
eval(Add(Num(2), Num(3)))     ← YOU ARE HERE
  match: is Add(var l, var r)? YES
    l = Num(2), r = Num(3) bound
    eval(l) called:
      match Num(int v): v=2 -> return 2
    eval(r) called:
      match Num(int v): v=3 -> return 3
    return 2 + 3 = 5
```

**FAILURE PATH:**

- Non-exhaustive match: compiler error (Rust, Haskell), `MatchError` at runtime (Erlang)
- Incorrect pattern order: earlier arms shadow later ones
- Missing guard: arm matches more broadly than intended

---

### ⚖️ Comparison Table

| Language   | Pattern Types                      | Exhaustiveness          | First-Class?       |
| ---------- | ---------------------------------- | ----------------------- | ------------------ |
| Rust       | Type, structural, literals, guards | Compile-time enforced   | Yes                |
| Haskell    | Constructor, literals, as-patterns | Compile-time (warning)  | Yes                |
| Scala      | Constructor, unapply, guards       | Compile-time warning    | Yes                |
| Java 21    | Type, deconstruct, guards          | Compile-time (sealed)   | Partial            |
| Python     | Structural (`match`/`case`, 3.10+) | No exhaustiveness check | Partial            |
| JavaScript | No native pattern matching         | No                      | No (TC39 proposal) |

---

### ⚠️ Common Misconceptions

| Misconception                              | Reality                                                                                            |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| "Pattern matching is just a fancy switch"  | It adds exhaustiveness checking, destructuring, and type testing simultaneously                    |
| "Wildcard `_` is always needed"            | For sealed types, the compiler proves exhaustiveness without `_`; adding it hides future cases     |
| "Pattern matching is slow"                 | Compilers generate optimal decision trees; usually faster than chained `instanceof`                |
| "Java had pattern matching before Java 16" | `switch` on strings/ints was not pattern matching; no type testing, binding, or exhaustiveness     |
| "Pattern matching replaces all if/else"    | It replaces type-discriminated branching; simple boolean conditions are still cleaner as `if/else` |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Non-Exhaustive Match at Runtime**
**Symptom:** `MatchError` / `IllegalStateException` on a new variant.
**Root Cause:** Match doesn't handle all variants; new variant added without updating match.
**Prevention:**

- Rust: compile-time error
- Java: use sealed classes/interfaces; compiler warns on switch expressions
- Test: add a test for each variant in your match

**Mode 2: Pattern Shadowing**
**Symptom:** Later pattern never matches; arm is dead code.
**Root Cause:** Earlier pattern is broader than intended.
**Diagnostic:**

```rust
match value {
    _ => println!("catch-all"), // always matches!
    42 => println!("42"), // unreachable -- compiler warns
}
```

**Fix:** Put specific patterns before broad ones.

**Mode 3: Forgetting Guard Clauses**
**Symptom:** Pattern matches when it shouldn't; incorrect arm executed.
**Root Cause:** Pattern matches shape but guard on value not specified.
**Fix:**

```rust
match point {
    Point { x, y } if x > 0 && y > 0 => { /* positive quadrant */ }
    Point { x, y } => { /* everything else */ }
}
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CSF-020 - Control Flow (if, loops, switch)]]
- [[CSF-038 - Interfaces vs Abstract Classes]]
- [[CSF-046 - Algebraic Data Types (ADTs)]]

**Builds On This (learn these next):**

- [[CSF-047 - Monads and Functors]]
- [[CSF-048 - Continuation-Passing Style (CPS)]]

**Alternatives / Comparisons:**

- Visitor pattern (OOP alternative to pattern matching)
- `instanceof` chains (pre-Java 16 workaround)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ WHAT IT IS      Tests value shape and binds components│
│                 in one step with exhaustiveness check │
│ PROBLEM         instanceof chains + manual casts +    │
│ IT SOLVES       missing cases at runtime              │
│ KEY INSIGHT     Exhaustiveness: compiler tells you     │
│                 every match when you add a new case   │
│ USE WHEN        Processing sum types / discriminated   │
│                 unions / ASTs                         │
│ AVOID WHEN      Simple boolean conditions; just use    │
│                 if/else for those                     │
│ TRADE-OFF       Expressive vs only available with      │
│                 sealed types for full safety          │
│ ONE-LINER       Switch that opens values and checks    │
│                 all cases at compile time             │
│ NEXT EXPLORE    CSF-046, CSF-047, Java sealed classes  │
└─────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Pattern matching tests structure and binds components simultaneously — no manual cast after `instanceof`.
2. Exhaustiveness checking: the compiler finds every non-exhaustive match when you add a new case.
3. In Rust and Haskell this is enforced at compile time; in Java 21 it requires sealed classes.

**Interview one-liner:**
"Pattern matching simultaneously tests the shape of a value, binds its components to names, and with sealed types, provides compiler-enforced exhaustiveness — making it type-safe ADT dispatch without cast chains."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When a value can be one of N shapes, the code that handles it
should declare all N cases explicitly. Anything less is a bet
that the unhandled cases never occur. Exhaustiveness checking
collects the debt from that bet at compile time, not production time.

**Where else this pattern appears:**

- **Redux reducers** (JavaScript) — switch on action type; each case handles one shape
- **Event sourcing handlers** — match on event type; each event has a handler
- **Protocol decoders** — match on message type byte; each byte has a decoder

---

### 💡 The Surprising Truth

The Visitor pattern in OOP — a standard GoF design pattern —
exists almost entirely to compensate for the absence of pattern
matching in languages like Java. Visitor double-dispatches
through a type hierarchy to achieve what pattern matching does
in a single expression. When Java 21 added sealed classes and
pattern matching, the Visitor pattern became largely obsolete
for new code. A design pattern that appeared in a 1994 book
was solved by a language feature 30 years later.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** Java's pattern matching for switch
(Java 21) only provides compiler-enforced exhaustiveness when
the switched type is a `sealed` interface or class. Why can't
the compiler enforce exhaustiveness for non-sealed types, and
what does this reveal about the relationship between closed
types and exhaustive dispatch?

_Hint:_ Consider what the compiler must know: the complete
set of possible subtypes. When can the compiler know this?
When can it not?

**Q2 (Scale):** A domain model has 30 event types in a sealed
hierarchy. All 50 service classes need to pattern-match on
events. You add 2 new event types. How many places must be
updated, and how does pattern matching exhaust help vs hinder
the migration?

_Hint:_ Consider the trade-off: exhaustiveness finds all places,
but forces you to handle each case (even with `default` arms).
Is this the right tool for a frequently-changing hierarchy?

**Q3 (First Principles):** In Haskell, a function on a sum type
created via pattern match is called a _fold_. A list fold
`foldr :: (a -> b -> b) -> b -> [a] -> b` is a pattern match
over `Nil` (base case) and `Cons` (recursive case). What does
this reveal about the relationship between pattern matching
and recursion?

_Hint:_ Research "catamorphism" and how every algebraic data
type has a canonical fold that corresponds exactly to
pattern matching over its cases.
