---
id: CSF-039
title: Generics and Parametric Polymorphism
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
version: 1
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Dictionary"
nav_order: 39
permalink: /csf/generics-and-parametric-polymorphism/
---

# CSF-039 - Generics and Parametric Polymorphism

⚡ TL;DR - Generics let you write code that works for any type while retaining type safety; parametric polymorphism is the formal name for this ability to parameterise code over types.

| CSF-039         | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | CSF-012, CSF-038, CSF-019             |                 |
| **Used by:**    | CSF-046, CSF-047, CSF-051             |                 |
| **Related:**    | CSF-038, CSF-046, CSF-051, CSF-052    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without generics, a `List` holds `Object`. To get an element,
you must cast: `String s = (String) list.get(0)`. If the list
contains an `Integer`, the cast throws `ClassCastException` at
runtime — not at compile time. The type system offers no help.
Java before Java 5 (generics) was full of this pattern.

**THE BREAKING POINT:**
A large Java codebase with raw collections has `ClassCastException`
in production. Developers insert casts everywhere. A `List`
passed to three methods: each assumes different contents.
No compiler tells you they're wrong.

**THE INVENTION MOMENT:**
ML (1973) introduced parametric polymorphism: a function can
work over _any_ type `α`, written `α list → α`. The function
`reverse` doesn't need to know the element type; it works for
all types. Java 5 (2004) added generics: `List<T>`, `Optional<T>`.
Type parameters make the type system powerful enough to express
"container of T" without losing type information.

**EVOLUTION:**
Java uses type erasure (generics removed at compile time).
C# uses reification (generics kept at runtime). Kotlin improves
on Java with `reified` type parameters. Rust uses monomorphisation
(a separate copy of the function for each concrete type).
Haskell and Scala have higher-kinded types (type parameters
that are themselves parameterised). Each is a point in the
trade-off space of expressiveness vs runtime cost.

---

### 📘 Textbook Definition

**Generics** (or **parametric polymorphism**) is the ability
to write code that is parameterised over one or more _type
parameters_ (`T`, `E`, `K`, `V`). A generic class or method
works for any type that satisfies the constraints (bounds).
At compile time, the type checker verifies type safety; no
runtime casts are needed. Formally, a generic function of
type `∀T. T list → T list` can be applied to any type `T`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Generics let you write one `List<T>` that works for any type `T` while catching type errors at compile time.

**One analogy:**

> A generic container is like a labelled box with a window:
> "Box<Books>" or "Box<Electronics>". You know exactly what's
> inside from the label. A raw (non-generic) container is an
> unlabelled cardboard box: you have to open it and guess,
> and if you're wrong, things break.

**One insight:**
Generics move type errors from runtime (ClassCastException
at 3am) to compile time (red squiggles before commit). The
investment in type annotations pays dividends in reduced
production incidents.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A generic type is parameterised by one or more type variables.
2. Type variables can be bounded: `T extends Comparable<T>` (upper bound).
3. The type checker verifies all usages of type parameters are consistent.
4. Java type erasure: `List<String>` becomes `List` at runtime (JVM doesn't know `String`).
5. Wildcard `? extends T` (covariant) vs `? super T` (contravariant) — the PECS rule.

**DERIVED DESIGN:**

- `List<T>` — homogeneous container: all elements are type `T`
- `Map<K, V>` — two type parameters: key type and value type
- `Comparable<T>` — generic interface: constrains implementing types
- `<T extends Comparable<T>>` — bounded type parameter: T must be self-comparable
- `Optional<T>` — generic container for possibly-absent value

**THE TRADE-OFFS:**
**Gain:** Type safety, no casts, reusable algorithms.
**Cost:** Java: type erasure limits runtime reflection.
C++/Rust monomorphisation: faster but larger binary.
Higher-kinded types: very expressive but complex.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Reusable type-safe containers require type parameters.
**Accidental:** Java's wildcard hell (`? extends ? super T`), type
erasure surprises, raw type warnings.

---

### 🧪 Thought Experiment

**SETUP:**
You write a utility to find the max element in a list.

**WITHOUT GENERICS:**

```java
public Object findMax(List list) {
    Object max = list.get(0);
    for (Object item : list) {
        if (((Comparable) item).compareTo(max) > 0) {
            max = item;
        }
    }
    return max; // caller must cast: (Integer) findMax(ints)
} // ClassCastException if list contains mixed types
```

**WITH GENERICS:**

```java
public <T extends Comparable<T>> T findMax(List<T> list) {
    T max = list.get(0);
    for (T item : list) {
        if (item.compareTo(max) > 0) {
            max = item;
        }
    }
    return max; // returns T; no cast needed by caller
} // compiler verifies: list must be List of Comparable elements
```

**THE INSIGHT:**
The generic version is not just safer; it's _more informative_.
The signature `<T extends Comparable<T>> T findMax(List<T>)`
tells you exactly what it requires and what it returns.
The non-generic version says almost nothing.

---

### 🧠 Mental Model / Analogy

> Generics are like a template on a rubber stamp factory.
> You design the template once ("stamp with NAME = \_\_\_"). You
> then stamp "stamp with NAME = Alice", "stamp with NAME = Bob".
> Each stamped item is type-specific. Without generics, you
> have one stamp that says "NAME" but delivers an `Object` —
> you must squint to figure out what it stamped.

**Element mapping:**

- Stamp template = generic class/method definition
- Filling in NAME = supplying the type parameter
- Each stamped item = instantiated generic (e.g., `List<String>`)
- Squinting to identify content = runtime cast

Where this analogy breaks down: Java type erasure means the
stamped item's type is forgotten at runtime; the stamp template
is the only place the name appears.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Generics let you say "a list of Strings" instead of just
"a list". The computer then checks that you only put Strings
in and only take Strings out. No surprises when you take
something out.

**Level 2 - How to use it (junior developer):**
Use type parameters when your class holds or processes values
whose type isn't fixed. Prefer `<T extends SomeInterface>`
bounds over raw `T` when you need to call methods on T.
Never use raw types (`List` instead of `List<T>`) — it bypasses
type safety.

**Level 3 - How it works (mid-level engineer):**
Java generics use _type erasure_: the compiler checks types,
then strips the type parameters from bytecode. At runtime,
`List<String>` is just `List`. The JVM inserts casts for you.
This is why you can't do `new T()` or `instanceof T` in Java:
the JVM doesn't know `T` at runtime. The compiler does the
type-checking; the JVM just executes cast-laden bytecode.

**Level 4 - Why it was designed this way (senior/staff):**
Java chose type erasure for backward compatibility: pre-generics
`List` and post-generics `List<String>` share the same bytecode.
C# chose reification: `List<int>` and `List<string>` are genuinely
different types at runtime. Rust chose monomorphisation:
`Vec<i32>` and `Vec<String>` generate separate machine code.
Each choice trades binary size (monomorphisation), runtime
reflection (reification), or backward compatibility (erasure).

**Expert Thinking Cues:**

- When a method returns `Object`: should it be `T` instead?
- When you see a cast: was a type parameter missed?
- PECS: producer `? extends T` (reading), consumer `? super T` (writing).

---

### ⚙️ How It Works (Mechanism)

**Type erasure (Java):**

```java
// Source
List<String> strings = new ArrayList<>();
strings.add("hello");
String s = strings.get(0);

// After erasure (what bytecode looks like)
List strings = new ArrayList();
strings.add("hello");
String s = (String) strings.get(0); // compiler-inserted cast
```

**Monomorphisation (Rust/C++ templates):**

```rust
fn print<T: Display>(v: T) { println!("{}", v); }
// Compiler generates:
fn print_i32(v: i32) { println!("{}", v); }  // for i32
fn print_str(v: &str) { println!("{}", v); } // for &str
// No runtime overhead; no type erasure; larger binary
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (Java):**

```
List<String> list = new ArrayList<>();
list.add("Alice");  ← YOU ARE HERE
  -> compiler: T=String; "Alice" is String: OK
list.add(42);        // compile error: int is not String
String s = list.get(0); // no cast needed; type known

At runtime: List (erased); cast inserted by compiler
```

**FAILURE PATH:**

- Raw types (`List list`): bypass type checking; ClassCastException at runtime
- Heap pollution: `List<String> strings = (List<String>) rawList` — unsafe cast
- Type erasure surprises: `instanceof List<String>` is a compile error

---

### ⚖️ Comparison Table

| Feature                 | Java (erasure) | C# (reification) | Rust (monomorphism) | Haskell (HKT) |
| ----------------------- | -------------- | ---------------- | ------------------- | ------------- |
| Runtime type info       | No (erased)    | Yes              | No (specialised)    | No            |
| Binary size             | Small          | Medium           | Larger (per type)   | Small         |
| `instanceof Generic<T>` | No             | Yes              | N/A                 | N/A           |
| Higher-kinded types     | No             | Partial          | Partial             | Yes           |
| Backward compatibility  | Yes            | N/A              | N/A                 | N/A           |

---

### ⚠️ Common Misconceptions

| Misconception                              | Reality                                                                                                  |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------- |
| "Generics are only for collections"        | Any reusable type-safe container or algorithm benefits: `Optional<T>`, `Future<T>`, `Result<T, E>`       |
| "Type erasure makes Java generics useless" | Erasure only limits runtime reflection; compile-time safety (the main benefit) is fully preserved        |
| "? and T are the same"                     | `?` is an unknown type; `T` is a named type parameter. `List<?>` accepts any List; `List<T>` is specific |
| "Raw types are fine for legacy code"       | Raw types bypass type safety; use `@SuppressWarnings("unchecked")` carefully and plan to fix             |
| "Bounded wildcards are too complex"        | PECS rule: Producer=`extends`, Consumer=`super`. Once understood, they enable flexible APIs              |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Heap Pollution**
**Symptom:** `ClassCastException` in code that doesn't call cast explicitly.
**Root Cause:** Unsafe unchecked cast of raw type to parameterised type.
**Diagnostic:**

```bash
javac -Xlint:unchecked YourFile.java
# Shows: warning: [unchecked] unchecked cast
```

**Fix:** Eliminate raw types; use properly parameterised types.

**Mode 2: Cannot Create Generic Array**
**Symptom:** `generic array creation` compile error.
**Root Cause:** Java type erasure: `new T[10]` is illegal because T is unknown at runtime.
**Fix:**

```java
// BAD
T[] array = new T[10]; // compile error

// GOOD
@SuppressWarnings("unchecked")
T[] array = (T[]) new Object[10]; // acceptable workaround
// Or: use List<T> instead of T[]
```

**Mode 3: PECS Violation**
**Symptom:** Compiler error on `addAll` or `copy` with wildcard types.
**Root Cause:** Using `? extends T` where `? super T` needed (or vice versa).
**Fix:** PECS: `extends` for reading (producer), `super` for writing (consumer).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CSF-012 - Type Systems (Static vs Dynamic)]]
- [[CSF-038 - Interfaces vs Abstract Classes]]

**Builds On This (learn these next):**

- [[CSF-046 - Algebraic Data Types (ADTs)]]
- [[CSF-051 - Type Inference]]
- [[CSF-052 - Structural vs Nominal Typing]]

**Alternatives / Comparisons:**

- C++ templates (structural duck typing, monomorphisation)
- Python type hints (structural, optional)
- TypeScript generics (structural, erased)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ WHAT IT IS      Code parameterised over types; type-  │
│                 safe reuse without casting            │
│ PROBLEM         Raw collections: ClassCastException   │
│ IT SOLVES       at runtime; no compile-time checks    │
│ KEY INSIGHT     Generics move type errors from        │
│                 runtime to compile time              │
│ USE WHEN        Reusable containers or algorithms      │
│ AVOID WHEN      Raw types; over-wildcarding           │
│ TRADE-OFF       Java: erasure for compat vs reif for  │
│                 runtime type info (C#)               │
│ ONE-LINER       One List<T> instead of many           │
│                 ListOfStrings, ListOfInts...         │
│ NEXT EXPLORE    CSF-046, CSF-051, PECS rule           │
└─────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Generics let you write one `List<T>` that works for any type `T` with compile-time type safety.
2. Java uses type erasure: type parameters are compile-time only; bytecode uses `Object` + casts.
3. PECS: `extends` for reading (producer), `super` for writing (consumer).

**Interview one-liner:**
"Generics parameterise code over types, providing type safety without casting; Java uses type erasure (compile-time only) while Rust uses monomorphisation (separate copy per type) and C# uses reification (types known at runtime)."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Parametric polymorphism is the principle of writing code that
works for _any_ input satisfying a constraint. Whenever you
find yourself writing near-identical code for different types,
a type parameter is probably the right abstraction.

**Where else this pattern appears:**

- **TypeScript generics** — `Promise<T>`, `Array<T>` for type-safe async and collections
- **Go generics** (1.18) — `func Map[T, U any](s []T, f func(T) U) []U`
- **Database query builders** — `QueryBuilder<User>` ensures result type matches entity

---

### 💡 The Surprising Truth

Java's type erasure was a deliberate compromise to enable
backward compatibility with pre-generics code (Java 1.4 and
earlier). This meant `ArrayList<String>` and `ArrayList<Integer>`
are the same class at runtime. But this decision has a
surprising positive side effect: a `List<String>` can be
passed to a pre-generics library expecting `List` (raw type)
without any conversion. C# reification, while more powerful,
breaks this backward compatibility. Java's pragmatic decision
enabled generics to be adopted without rewriting every library.

---

### 🧠 Think About This Before We Continue

**Q1 (First Principles):** Java's `List<String>` and `List<Integer>`
are both `List` at runtime due to erasure. Yet `ArrayList<String>`
cannot be assigned to `ArrayList<Integer>`. Why isn't `ArrayList<String>`
a subtype of `ArrayList<Object>`? What would break if it were?

_Hint:_ Research covariance and why mutable containers cannot be
covariant. What would `((List<Object>) stringList).add(42)` do
to a `List<String>`?

**Q2 (Scale):** Rust's monomorphisation creates a separate copy
of a generic function for each concrete type. A generic function
called with 20 different types creates 20 machine-code versions.
What is the impact on binary size and instruction cache performance
in a large Rust codebase?

_Hint:_ Research Rust's binary size problem and strategies like
`dyn Trait` (dynamic dispatch) as an alternative to monomorphisation.

**Q3 (Design Trade-off):** Haskell has higher-kinded types (HKT):
you can write `Functor f` where `f` is itself a type constructor
(`Maybe`, `List`, `IO`). Java and Go do not have HKT. What kinds
of abstractions are expressible in Haskell but not in Java,
and is this a fundamental limitation or just ergonomic?

_Hint:_ Research why Haskell's `Monad` type class cannot be
directly expressed in Java, and what "emulated HKT" looks like
in Scala or Java (hint: `Kind<F, A>` encoding).
