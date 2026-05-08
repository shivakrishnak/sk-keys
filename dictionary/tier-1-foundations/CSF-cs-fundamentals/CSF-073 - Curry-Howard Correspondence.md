---
id: CSF-073
title: Curry-Howard Correspondence
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★★
depends_on:
used_by:
related:
tags:
  - csf
  - advanced
  - deep-dive
  - first-principles
status: draft
version: 1
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Dictionary"
nav_order: 73
permalink: /csf/curry-howard-correspondence/
---

# CSF-073 - Curry-Howard Correspondence

⚡ TL;DR - The Curry-Howard Correspondence is the deep isomorphism between logic and type theory: propositions correspond to types, proofs correspond to programs, and logical connectives correspond to type constructors.

| CSF-073         | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | CSF-071, CSF-072                      |                 |
| **Used by:**    | CSF-074, CSF-076                      |                 |
| **Related:**    | CSF-071, CSF-072, CSF-074, CSF-076    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Logic and programming are taught as separate disciplines.
Mathematicians prove theorems; programmers write code.
The intuition that writing a well-typed program is
analogous to writing a mathematical proof is informal.
No systematic bridge exists between the two worlds.

**THE BREAKING POINT:**
Haskell Curry (1934) and William Howard (1969) independently
discovered the same structure: the rules for constructing
proofs in intuitionistic logic are syntactically identical
to the typing rules of lambda calculus. A proof of
"A and B" is a pair of proofs; a pair type `(A, B)`
is structurally the same. The correspondence is exact,
not metaphorical.

**THE INVENTION MOMENT:**
Howard's 1969 paper (circulated informally; published 1980)
"The formulae-as-types notion of construction" made the
correspondence explicit: propositions = types, proofs = terms,
normalisation = computation. Per Martin-Löf extended this
into dependent type theory, enabling types to depend on
values ("the array has length N").

**EVOLUTION:**
Coq, Agda, Lean: proof assistants based on Curry-Howard.
Rust's lifetime system: ownership types encode memory
safety proofs. Haskell's type class system and GADTs.
Dependent types in Idris. Curry-Howard is the theoretical
foundation for using types as formal verification.

---

### 📘 Textbook Definition

The **Curry-Howard Correspondence** (also: propositions-as-types,
proofs-as-programs) is an isomorphism between intuitionistic
logic and typed lambda calculus:

| Logic               | Type Theory                 |
| ------------------- | --------------------------- |
| Proposition         | Type                        |
| Proof of A          | Term of type A              |
| A ∧ B (conjunction) | A × B (product type / pair) |
| A ∨ B (disjunction) | A + B (sum type / Either)   |
| A ⊃ B (implication) | A → B (function type)       |
| ⊥ (falsehood)       | Empty type (no inhabitants) |
| ∀x. P(x)            | Dependent product type Π    |
| ∃x. P(x)            | Dependent sum type Σ        |

A type is inhabited (has a term) if and only if the
corresponding proposition is provable.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Types are propositions; programs are proofs; if a type is inhabited by a value, the proposition it represents is proven.

**One analogy:**

> Writing a function of type `A -> B` is proving the
> logical theorem "if A then B." The function body is
> the proof: it takes evidence of A and produces evidence
> of B. A function that can never be implemented corresponds
> to a theorem that can never be proved. If you can write
> the function, you've proved the theorem.

**One insight:**
The reason Rust's type system prevents certain memory bugs
is exactly Curry-Howard: the ownership type system is a
logic for memory safety, and a well-typed Rust program is
a proof that memory access is safe.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Propositions-as-types: a type `A` represents the proposition "A is provable."
2. Proofs-as-programs: a term `t : A` is a proof (evidence) that `A` holds.
3. Conjunction = product type: to prove `A ∧ B`, provide a pair `(a, b)` where `a : A` and `b : B`.
4. Implication = function: to prove `A ⊃ B`, provide a function `f : A -> B`.
5. Inhabited type = provable proposition: if a type has no terms (empty type), the proposition is false/unprovable.

**CONCRETE EXAMPLES:**

```haskell
-- Proposition: "if A is true and B is true, then A is true"
-- Type: (A, B) -> A
fst :: (A, B) -> A
fst (a, b) = a
-- This function IS the proof; it exists, so the theorem is proved.

-- Proposition: "if A then (if A then B) then B"
-- Type: A -> (A -> B) -> B
apply :: A -> (A -> B) -> B
apply a f = f a
-- This IS the proof of modus ponens.

-- Proposition: "false implies anything" (ex falso)
-- Type: Void -> A (Void = empty type = falsehood)
absurd :: Void -> A
absurd x = case x of {} -- impossible; Void is uninhabited
-- Cannot be called (no Void values exist);
-- the theorem is vacuously true.
```

**DERIVED DESIGN:**

- `Either a b` (Haskell) = disjunction (A ∨ B)
- `Maybe a` (Haskell) = A ∨ ⊤ (A or trivially true)
- Rust `Option<T>` = same
- Dependent type: `Vec n a` = "a list of exactly n elements"
  (the type encodes the length as a proof)

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Proofs and programs are the same mathematical object in intuitionistic logic.
**Accidental:** Different notation between logic textbooks and programming language theory.

---

### 🧪 Thought Experiment

**SETUP:**
Can you write a function of type `A -> B` for arbitrary A and B?

**ATTEMPT:**

```haskell
-- Can you implement this?
impossible :: A -> B
impossible a = ???  -- no way to produce a B from an A
                    -- (without knowing what A and B are)
```

**LOGICAL INTERPRETATION:**
The type `A -> B` is the proposition "A implies B."
For arbitrary `A` and `B`, this is not provable.
There is no term of this type (no implementation).
`impossible` cannot be written in a well-typed, total language.

**WHAT YOU CAN WRITE:**

```haskell
-- A -> A is "A implies A" (trivially true)
identity :: A -> A
identity a = a  -- the proof is trivial

-- (A, B) -> A is "A and B implies A"
fst :: (A, B) -> A
fst (a, _) = a  -- the proof is extracting the first component
```

**THE INSIGHT:**
The functions you can't implement correspond to theorems
that are false. The functions you can implement correspond
to theorems that are provable. The type system is a
logic system; type checking is proof checking.

---

### 🧠 Mental Model / Analogy

> Writing a well-typed function is completing a jigsaw
> puzzle where the types are the shapes of the pieces.
> The type signature tells you what pieces you have (inputs)
> and what picture you must produce (output). If there's
> no valid puzzle configuration (no valid proof), no
> implementation exists. If there is, the implementation
> IS the solved puzzle.

**Element mapping:**

- Puzzle pieces = input types (available evidence)
- Required picture = output type (conclusion to prove)
- Valid configuration = correct implementation
- No valid configuration = theorem is false; function is unimplementable
- Jigsaw rules = type system rules

Where this analogy breaks down: some theorems have multiple
proofs; some functions have multiple correct implementations.
The analogy works for constructive proof existence, not uniqueness.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
There's a surprising mathematical connection: every logical
proposition corresponds to a programming type. Proving
the proposition is the same as writing a function of that
type. If you can write the function, you've proved the
logical statement.

**Level 2 - How to use it (junior developer):**
In practice: types encode guarantees. `Option<T>` says
"T may not be present; the caller must handle both cases."
`Result<T, E>` says "either success or failure; handle both."
Sealed classes with exhaustive pattern matching say
"every case is handled; the proof is complete."

**Level 3 - How it works (mid-level engineer):**
In Haskell, `undefined :: A` (bottom) inhabits every type.
This means Haskell's type system is not logically consistent:
`undefined :: False` is a proof of falsehood. Total
languages (Agda, Idris) forbid `undefined` to preserve
consistency. Rust's type system is total for safe code
(no undefined), making it logically sound for memory safety.

**Level 4 - Why it was designed this way (senior/staff):**
Dependenttype theory (Per Martin-Löf, 1975) extends Curry-Howard:
types can depend on values. `Vec (n : Nat) A` is the type
of vectors of exactly `n` elements. The type system can
prove array bounds are safe at compile time (no runtime
bounds check needed). This is the foundation of Agda,
Idris, Coq, and Lean. Rust's lifetime system is a limited
form of dependent typing: the type of a reference carries
the lifetime (a value-dependent constraint).

**Expert Thinking Cues:**

- When a function has `undefined` or `???` as its body: that's a gap in the proof.
- When a sealed class has an `else` branch: the proof has a "trust me" case.
- When a dependent type encodes array length: bounds checks are compile-time theorems.

---

### ⚙️ How It Works (Mechanism)

**Product and sum types as logic:**

```haskell
-- Product type (A ∧ B): both A and B are true
data Pair a b = Pair a b  -- (a : A) and (b : B)

-- Sum type (A ∨ B): at least one of A or B is true
data Either a b = Left a | Right b  -- a : A, or b : B

-- Function type (A ⊃ B): A implies B
-- A function that transforms evidence of A into evidence of B

-- Empty type (⊥ false): nothing inhabits False
data Void  -- no constructors -> no inhabitants

-- ex falso: from False, anything follows
absurd :: Void -> a
absurd v = case v of {}  -- unreachable: no Void values
```

---

### 🔄 The Complete Picture - End-to-End Flow

**PROOF BY IMPLEMENTATION:**

```
Logical theorem: "if A then B then A"  <- YOU ARE HERE
  Propositions-as-types:
  |-> Type: A -> B -> A
  Write the implementation:
  |-> const :: A -> B -> A
  |-> const a _ = a
  Type checker verifies:
  |-> a : A, _ : B; return a : A -> valid
  Result:
  |-> Type checks -> proof is valid
  |-> Theorem is proved by the existence of `const`
  |-> The function IS the proof
```

**FAILURE PATH:**

- Haskell `undefined`: introduces ⊥ (bottom); breaks logical consistency
- Unsound type systems (TypeScript `any`): proposition proved by "trust me"
- Partial functions: function doesn't terminate for some inputs; proof has gaps

---

### ⚖️ Comparison Table

| Logic     | Type            | Language Example                        |
| --------- | --------------- | --------------------------------------- |
| A ∧ B     | (A, B) product  | Kotlin `Pair<A,B>`, Haskell `(a,b)`     |
| A ∨ B     | A + B sum       | Kotlin `sealed class`, Haskell `Either` |
| A ⊃ B     | A -> B function | All typed languages                     |
| ⊤ (true)  | Unit / ()       | `Unit` (Kotlin), `()` (Haskell)         |
| ⊥ (false) | `Void` / Never  | `Nothing` (Kotlin), `Void` (Haskell)    |
| ∀x.P(x)   | `∀ a. f a`      | Polymorphic type in Haskell/Scala       |

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                   |
| -------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| "Curry-Howard is abstract theory with no practical use"  | Rust's ownership types, Haskell's type classes, Coq proofs are all built on Curry-Howard                  |
| "Type checking and theorem proving are different things" | Type checking in a dependently-typed language is theorem proving                                          |
| "Haskell's type system is logically consistent"          | Haskell has ⊥ (undefined) which inhabits every type; it's logically inconsistent (but practically useful) |
| "You need dependent types for Curry-Howard"              | Simple Curry-Howard works for STLC (Simply Typed Lambda Calculus); dependent types extend it              |
| "Proofs are different from programs"                     | In a total language, they are the same; a proof IS a program; a program IS a proof                        |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Logical Inconsistency via Partial Functions**
**Symptom:** Haskell type checks but throws at runtime.
**Root Cause:** `head []` is a partial function (undefined on empty list); it inhabits any type falsely.
**Fix:** Use `headMay :: [a] -> Maybe a`; total function; honest about failure.

**Mode 2: TypeScript `any` Breaking the Logic**
**Symptom:** TypeScript type-checks but NPE/wrong-type at runtime.
**Root Cause:** `any` bypasses type system; "proof" contains unjustified assertion.
**Fix:** `unknown` + type narrowing instead of `any`; `strict: true` in tsconfig.

**Mode 3: Exhaustiveness Missing (unsealed hierarchy)**
**Symptom:** `when` expression with `else` branch; silent wrong-case.
**Fix:** Use sealed classes + remove `else`; compiler enforces exhaustiveness.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CSF-071 - Church-Turing Thesis]]
- [[CSF-072 - Lambda Calculus]]

**Builds On This (learn these next):**

- [[CSF-074 - Category Theory for Programmers]]
- [[CSF-076 - Type Theory (System F, HM Inference)]]

**Alternatives / Comparisons:**

- Classical logic vs intuitionistic logic (classical logic breaks CH)
- Proof assistants: Coq, Lean, Agda (direct applications of CH)

---

### 📌 Quick Reference Card

```
+-----------------------------------------------------+
| WHAT IT IS      Propositions = types; proofs =      |
|                 programs; exact isomorphism         |
| PROBLEM         No bridge between logic and         |
| IT SOLVES       programming; type safety unexplained|
| KEY INSIGHT     Writing a well-typed function IS    |
|                 proving the corresponding theorem   |
| USE WHEN        Type-driven development; proof      |
|                 assistants; dependent types         |
| AVOID           Partial functions (break the logic) |
| TRADE-OFF       Expressiveness vs logical soundness |
| ONE-LINER       Type : Proposition :: Term : Proof  |
| NEXT EXPLORE    CSF-076, Agda, Coq, Lean             |
+-----------------------------------------------------+
```

**If you remember only 3 things:**

1. Types are propositions; terms are proofs; a type is inhabited iff the proposition is provable.
2. Function type `A -> B` = "A implies B"; product type `(A, B)` = "A and B"; sum type `A | B` = "A or B."
3. Rust's ownership system and Haskell's type classes are practical applications of Curry-Howard logic.

**Interview one-liner:**
"The Curry-Howard Correspondence is the isomorphism between typed lambda calculus and intuitionistic logic: types are propositions, programs are proofs, and a type is inhabitable iff the corresponding proposition is provable — the theoretical basis for type-safe languages and proof assistants like Coq and Lean."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Types are not just contracts between developer and compiler;
they are logical propositions that constrain what programs
can mean. Designing types to encode invariants (make invalid
state unrepresentable) is exactly designing a formal
specification that the compiler enforces as a proof checker.

**Where else this pattern appears:**

- **Database constraints** — `NOT NULL`, `CHECK` are propositions enforced by the DB engine
- **Protocol state machines** — type-safe state machines encode valid state transitions as types
- **Property-based testing** — QuickCheck generates counterexamples, like searching for proof gaps

---

### 💡 The Surprising Truth

The Curry-Howard Correspondence implies that every valid
logical proof has a corresponding program, and every
terminating, well-typed program is a valid logical proof.
This means that when Haskell infers the type of a polymorphic
function like `id :: a -> a`, the Hindley-Milner type
inference algorithm is not just computing a type — it is
finding a proof of the logical statement "for all A, A implies A."
Type inference is automated theorem proving. Every time
your IDE suggests a type annotation, it's completing a
mathematical proof on your behalf.

---

### 🧠 Think About This Before We Continue

**Q1 (First Principles):** Haskell's `undefined :: a`
inhabits every type, making Haskell's type system logically
inconsistent (every proposition is provable via `undefined`).
Why do language designers keep `undefined` in Haskell
despite this inconsistency, and what does this tell us
about the trade-off between practical programming and
logical consistency?

_Hint:_ Total languages (Agda) forbid `undefined` for consistency.
But Haskell needs `undefined` for: lazy evaluation,
bottom as error, and ergonomic development. Practical
consistency (works for most programs) vs logical consistency
(works for proof assistants). Research Haskell's Fast and
Loose Reasoning for the formal treatment.

**Q2 (Scale):** The Lean 4 proof assistant is being used
by mathematicians to formally verify mathematical theorems
(the Lean Mathlib project). How does this relate to using
type systems for software correctness, and what would it
mean to formally verify a Spring Boot application in Lean?

_Hint:_ Lean proofs are programs; Lean programs are proofs.
Formally verifying a Spring service means expressing its
correctness as a type and writing a proof (program) that
inhabits it. Research dependent types and their use in
practical software verification.

**Q3 (Design Trade-off):** Rust's type system is not
dependently typed (types can't depend on values) but still
provides memory safety guarantees. How does Rust achieve
memory safety without full dependent types, and what class
of safety properties remains unverifiable at compile time?

_Hint:_ Rust uses a restricted form of dependent types:
lifetimes are compile-time values that types depend on.
But Rust can't verify: algorithm correctness, arithmetic
properties (no overflow guarantee in release mode), or
business logic. These require runtime tests or formal
verification.
