---
id: CSF-046
title: Algebraic Data Types (ADTs)
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
  - deep-dive
  - tradeoff
status: draft
version: 1
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Dictionary"
nav_order: 46
permalink: /csf/algebraic-data-types-adts/
---

# CSF-046 - Algebraic Data Types (ADTs)

⚡ TL;DR - Algebraic Data Types are composite types formed by two operations: product ("and") and sum ("or"), giving you a type algebra that can model all domain data precisely.

| CSF-046         | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | CSF-012, CSF-039, CSF-040             |                 |
| **Used by:**    | CSF-047, CSF-048, CSF-075, CSF-076    |                 |
| **Related:**    | CSF-039, CSF-040, CSF-047, CSF-035    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without ADTs, modelling "a shape that is either a circle or a
rectangle" requires an inheritance hierarchy, a type field,
or a tagged union. The type system can't express mutual exclusion.
You can accidentally create a `Shape` with both `radius` and
`width` set — a nonsense value that the type allows but the
business doesn't.

**THE BREAKING POINT:**
Every class-based domain model accumulates nullable fields:
`private Double radius; // null if not a circle`. `// null if
not a rectangle`. The model represents the union of all
possible shapes in one object. Invalid states are representable.
Bugs emerge from forgotten null checks.

**THE INVENTION MOMENT:**
ML (1973) introduced algebraic data types: sum types (`A | B`)
and product types (`A * B`). Together, they form a _type
algebra_ where types have cardinalities: `A * B` has `|A| * |B|`
values; `A | B` has `|A| + |B|` values. This algebra lets you
model exactly the valid states of your domain — no more, no less.

**EVOLUTION:**
Haskell, OCaml, Rust, Scala, F#, Kotlin (sealed classes), and
Java 17+ (sealed classes + records) all support ADTs. The
catchphrase: "make illegal states unrepresentable." ADTs are
the foundation of type-driven design.

---

### 📘 Textbook Definition

An **algebraic data type** is a composite type formed by
combining other types using two operators:

- **Product type** (AND): `A * B` — a value of both A and B (struct/record/tuple)
- **Sum type** (OR): `A | B` — a value of exactly one of A or B (enum/union/sealed)

Product types have `|A| * |B|` possible values; sum types have
`|A| + |B|`. The algebra gives sum types their name. Pattern
matching (CSF-040) is the canonical way to consume sum types.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
ADTs are types built from "has both" (product) and "is one of" (sum), making illegal states unrepresentable.

**One analogy:**

> Product types are like a form with multiple fields: you fill
> in all of them. Sum types are like a multiple-choice question:
> you pick exactly one answer. Together they describe every
> possible shape of your data with mathematical precision.

**One insight:**
The goal of ADTs is to make invalid state unrepresentable in the
type system. If your type can only hold valid combinations,
you eliminate an entire class of runtime checks — the type
already guarantees validity.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Product type: value contains ALL fields simultaneously (struct, record, tuple).
2. Sum type: value contains EXACTLY ONE variant (enum with data, sealed class).
3. Sum types have `|A| + |B|` possible values: sum of the variants' sizes.
4. Product types have `|A| * |B|` possible values: cross product of field values.
5. Pattern matching on sum types must be exhaustive (all variants handled).

**DERIVED DESIGN:**

- `Option<T>` = `Some(T) | None` — a sum type for optional values
- `Result<T, E>` = `Ok(T) | Err(E)` — a sum type for fallible computation
- `List<T>` = `Nil | Cons(T, List<T>)` — recursive sum type
- `Point` = `{ x: f64, y: f64 }` — product type (both x and y)
- `Shape` = `Circle(f64) | Rect(f64, f64)` — sum of product types

**THE TRADE-OFFS:**
**Gain:** Illegal states unrepresentable. Exhaustive dispatch.
Self-documenting types.
**Cost:** Requires language support. Heavyweight for simple cases.
Pattern match boilerplate for many variants.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Real domains have values that are one-of-many.
**Accidental:** Nullable fields in classes simulating sum types;
type-tags in maps (`{"type": "circle", "radius": 5}`).

---

### 🧪 Thought Experiment

**SETUP:**
Model a payment: it's either `Pending`, `Completed(transactionId)`,
or `Failed(errorMessage)`.

**CLASS-BASED (invalid states representable):**

```java
class Payment {
    Status status; // PENDING, COMPLETED, FAILED
    String transactionId; // null if not COMPLETED
    String errorMessage; // null if not FAILED
    // Nothing prevents: status=COMPLETED, transactionId=null
    // Or: status=PENDING with both fields set
}
```

**ADT (sealed class, Java 17+):**

```java
sealed interface Payment {}
record Pending() implements Payment {}
record Completed(String transactionId) implements Payment {}
record Failed(String errorMessage) implements Payment {}
// Impossible to create Completed without transactionId
// Impossible to create Pending with transactionId
// Type makes valid states = all states
```

**THE INSIGHT:**
The class model allows 2^2 = 4 status/field combinations,
but only 3 are valid. The ADT model allows exactly 3.
The type eliminates the need to check for invalid combinations
at runtime.

---

### 🧠 Mental Model / Analogy

> Sum types are sealed boxes: each box is clearly labelled and
> contains the appropriate items. "Circle box" contains only
> a radius. "Rectangle box" contains only width and height.
> You can't put a radius in a rectangle box or a width in a
> circle box. Product types are trays with compartments: every
> compartment must be filled.

**Element mapping:**

- Labelled sealed box = sum type variant
- Items inside = fields of the variant (product)
- Opening the correct box = pattern matching
- Can't mix boxes = compile-time guarantee

Where this analogy breaks down: ADTs can be recursive (a box
can contain another box of the same type — like `List`).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
ADTs are types with precise shape. A sum type says "exactly
one of these options." A product type says "all of these fields."
Together, they model your data so that wrong combinations
can't exist.

**Level 2 - How to use it (junior developer):**
In Kotlin: use sealed classes for sum types. In Java 17+: use
sealed interfaces + records. Use the sum type wherever you
have "this could be one of several states." Remove nullable
fields that exist only for some states.

**Level 3 - How it works (mid-level engineer):**
At the JVM level, a sealed interface with record implementations
is just an interface + classes. The compiler enforces the seal:
no classes outside the same compilation unit can implement it.
Pattern matching in switch expressions checks all variants via
`invokeinterface` + `checkcast` in bytecode.

**Level 4 - Why it was designed this way (senior/staff):**
The algebraic structure (sum/product) is provably complete:
every type can be expressed as a combination of products and
sums. This is the Curry-Howard correspondence: sum types are
logical disjunction (OR), product types are logical conjunction
(AND). Proof-assistants like Coq and Lean use exactly this
type theory to represent mathematical proofs as programs.

**Expert Thinking Cues:**

- When reviewing a class with nullable fields: which fields belong to which sum variant?
- When seeing a type field (`status: String`): should this be a sealed interface?
- When adding a new variant: does pattern matching give compile-time exhaustiveness?

---

### ⚙️ How It Works (Mechanism)

**Cardinality calculation:**

```
bool: 2 values (true, false)
int: 2^32 values
bool * int: 2 * 2^32 values (product)
bool + int: 2 + 2^32 values (sum)

Option<bool>: Some(true) | Some(false) | None = 3 values
Result<bool, String>: Ok(true) | Ok(false) | Err(String) = 2 + |String| values
```

**Rust enum (sum type):**

```rust
enum Shape {
    Circle(f64),             // sum variant with f64 payload
    Rect(f64, f64),          // sum variant with two f64s
    Triangle(f64, f64, f64), // 3 sides
}
// sizeof(Shape) = tag (discriminant) + max(sizeof each variant)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Payment created: Completed("txn_123")  ← YOU ARE HERE
  -> type: Completed, field: transactionId="txn_123"
  -> no other fields possible (sealed record)
Pattern match:
  case Completed(id) -> process(id) -- only arm that matches
  case Pending -> ... -- not reached
  case Failed(err) -> ... -- not reached
Compiler: exhaustive (all 3 variants handled)
```

**FAILURE PATH:**

- Non-exhaustive match: compile error (Rust) or `MatchError` (Scala)
- Using a class with nullable fields: invalid states representable
- Adding variant without updating matches: compiler finds all match sites

---

### ⚖️ Comparison Table

| Language   | Product Type                  | Sum Type               | Exhaustiveness             |
| ---------- | ----------------------------- | ---------------------- | -------------------------- |
| Rust       | struct / tuple                | enum                   | Compile-time (required)    |
| Haskell    | record / tuple                | data ADT               | Compile-time (warning)     |
| Java 17+   | record                        | sealed interface/class | Compile-time (switch expr) |
| Kotlin     | data class                    | sealed class           | Compile-time (when expr)   |
| Scala      | case class                    | sealed trait           | Compile-time (warning)     |
| TypeScript | interface / type intersection | union type             | Partial (type narrowing)   |

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                  |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| "ADTs are only for functional languages"              | Java 17+ sealed classes + records; Kotlin sealed classes are mainstream ADTs                             |
| "Enums and sum types are the same"                    | Java enums have no data payload per variant; sum types carry different data per variant                  |
| "Product types are the same as classes"               | Classes have methods and identity; product types are pure data structures (values)                       |
| "ADTs are complex"                                    | The concept is simple: AND (product) and OR (sum); complexity comes from advanced type theory extensions |
| "Nullable fields are equivalent to Optional variants" | Nullable fields allow invalid combinations; Optional/sealed variants don't                               |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Invalid State via Null Fields**
**Symptom:** Business logic bug when nullable field used for wrong state.
**Root Cause:** Sum type modelled as class with nullable fields.
**Fix:** Convert to sealed interface with one record per state. Move data to the variant that owns it.

**Mode 2: Missing Variant in Match**
**Symptom:** `MatchError` / `IllegalStateException` when new variant added.
**Root Cause:** Non-exhaustive pattern match on unsealed type.
**Fix:** Use sealed types; exhaustive match; add `// EXHAUSTIVE` comment only when intentional wildcard.

**Mode 3: Variant Data in Wrong Place**
**Symptom:** `transactionId` accessible on `Pending` payment (returns null).
**Root Cause:** Field belongs to `Completed` variant but is on parent class.
**Fix:** Move field to `Completed` record; use pattern matching to access it.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CSF-039 - Generics and Parametric Polymorphism]]
- [[CSF-040 - Pattern Matching]]

**Builds On This (learn these next):**

- [[CSF-047 - Monads and Functors]]
- [[CSF-048 - Continuation-Passing Style (CPS)]]

**Alternatives / Comparisons:**

- Class hierarchy + type field (OOP approximation)
- Nullable fields (anti-pattern alternative)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ WHAT IT IS      Sum (OR) + Product (AND) type algebra   │
│ PROBLEM         Nullable fields let invalid states      │
│ IT SOLVES       exist; missing checks cause bugs       │
│ KEY INSIGHT     Make illegal states unrepresentable;   │
│                 type = only valid states              │
│ USE WHEN        Domain has "one of several" states      │
│ AVOID WHEN      Simple flat data; no variants          │
│ TRADE-OFF       Expressiveness vs boilerplate          │
│ ONE-LINER       AND (product) + OR (sum) = precise     │
│                 modelling of domain state             │
│ NEXT EXPLORE    CSF-047, CSF-040, sealed classes       │
└─────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Sum types = "exactly one of"; product types = "all fields together".
2. Make illegal states unrepresentable: if your type only allows valid combinations, you don't need runtime checks.
3. Pattern matching on sealed sum types is exhaustive: the compiler finds every missing case.

**Interview one-liner:**
"Algebraic data types combine product types (AND: all fields present) and sum types (OR: exactly one variant), enabling type systems to make illegal states unrepresentable and dispatch exhaustive."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Make illegal states unrepresentable. Every time you add a
nullable field because "it only applies in some states," you've
found a sum type waiting to be extracted. The type system
is your first line of defence against invalid state.

**Where else this pattern appears:**

- **HTTP status codes** — 2xx, 4xx, 5xx are disjoint sums; each has different data
- **Event sourcing** — each event type is a sum variant with its own payload
- **API response envelope** — `{"type": "success", "data": ...}` vs `{"type": "error", "code": ...}`

---

### 💡 The Surprising Truth

The "algebraic" in algebraic data types refers to actual
algebra: the cardinality (number of possible values) of a
product type is the _product_ of its components' cardinalities,
and of a sum type is the _sum_. `bool * bool` has 4 values;
`bool + bool` has 4 values too (coincidence). But `int * bool`
has 2^33 values while `int + bool` has 2^32 + 2 values.
This counting reveals the precision of the type: modelling
a Payment with 4 nullable fields has 2^4 = 16 possible
combinations, but only 3 are valid. The ADT has exactly 3.

---

### 🧠 Think About This Before We Continue

**Q1 (First Principles):** The `Option<T>` type can be defined
as `None | Some(T)`. What is the cardinality of `Option<bool>`?
Of `Option<Option<bool>>`? What does this tell you about
nested optionality, and why is `Option<Option<T>>` a design smell?

_Hint:_ Count the values of `Option<bool>`: None, Some(true),
Some(false) = 3. Then count `Option<Option<bool>>`: None,
Some(None), Some(Some(true)), Some(Some(false)) = 4. Are `None`
and `Some(None)` meaningfully different?

**Q2 (Scale):** A REST API for orders has a JSON body that
contains fields `confirmedAt`, `cancelledAt`, `shippedAt` —
all nullable. What are the valid and invalid state combinations?
How would you model this as ADTs, and what happens to the
API contract?

_Hint:_ An order should be in exactly one of: placed, confirmed,
shipped, cancelled. Model as a sealed ADT and see how many
fields become non-nullable.

**Q3 (Design Trade-off):** Rust's `enum` is a sum type where each
variant can have different data. Java's `enum` is just a set of
constants with shared fields. For a codebase migrating from
Java enum + null fields to sealed classes + records, what is
the migration strategy and what refactorings are needed?

_Hint:_ Consider the callers of each enum constant: they all
get the same API today. With sealed classes, each caller gets
a different type. What changes?
