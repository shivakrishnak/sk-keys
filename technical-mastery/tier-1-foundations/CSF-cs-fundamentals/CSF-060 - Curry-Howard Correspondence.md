---
id: CSF-060
title: Curry-Howard Correspondence
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★★
depends_on: CSF-064, CSF-035
used_by: CSF-068
related: CSF-064, CSF-035, CSF-068
tags: [curry-howard, propositions-as-types, proofs-as-programs, type-theory, dependent-types]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 60
permalink: /technical-mastery/csf/curry-howard-correspondence/
---

⚡ TL;DR - Propositions = Types. Proofs = Programs.
Conjunction (A AND B) = Product type (Pair). Disjunction
(A OR B) = Sum type (Either). Implication (A implies B)
= Function type (A -> B). Universal quantifier = Generic type.
False proposition = Empty type (Void). Writing a well-typed
program IS proving a theorem. Foundation of Coq, Agda, Lean
proof assistants and dependent type systems.

| #060 | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | CSF-064 (Type Theory), CSF-035 (Immutability) | |
| **Used by:** | CSF-068 (Category Theory for Programmers) | |
| **Related:** | CSF-064 (Type Theory), CSF-035 (Immutability), CSF-068 (Category Theory) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

A developer writes a type system for a new language. They
add features: generics, union types, intersection types,
type aliases. But they cannot systematically reason about:
Is this type system consistent? Can it express contradictions?
If I add feature X, does the type system remain sound?
Without the mathematical foundation (Curry-Howard), type
system design is ad hoc - add features that seem useful,
fix soundness holes as they appear. TypeScript's type system
has deliberate unsoundness (e.g., bivariant function parameters)
because the design was pragmatic rather than principled.

**THE BREAKING POINT:**

Logic and type theory were developed as separate fields
for decades. Logicians proved theorems. Computer scientists
wrote programs. But both fields had the same STRUCTURES:
logicians had "and," "or," "not," "implies," "forall."
Type theorists had "product types," "sum types," "function
types," "universal types." The CONNECTION between them
was not obvious until Curry noticed it (1934, combinatory
logic) and Howard formalized it (1969, unpublished correspondence
circulated as "The Formulae-as-Types Notion of Construction").

**THE INVENTION MOMENT:**

Haskell Curry (1958) observed that the types of combinators
in combinatory logic correspond to tautologies in propositional
logic. William Howard (1969) extended this: the typed lambda
calculus corresponds to natural deduction proofs in
intuitionistic logic. The correspondence is EXACT:
every proof in logic corresponds to a program in lambda calculus,
and every program corresponds to a proof. Computation
(normalizing the program) corresponds to proof simplification
(cut elimination). Martin-Lof type theory (1984) extended this
to dependent types, enabling proofs about programs within
the type system itself. This is the foundation of proof
assistants: Coq, Agda, Lean, Isabelle.

---

### 📘 Textbook Definition

**Curry-Howard Correspondence (Isomorphism):**
A structural correspondence between formal logic and type
theory (programming language types):

| Logic | Type Theory |
|---|---|
| Proposition P | Type P |
| Proof of P | Term of type P |
| A AND B (conjunction) | Product type A x B (Pair<A,B>) |
| A OR B (disjunction) | Sum type A + B (Either<A,B>) |
| A implies B | Function type A -> B |
| forall x. P(x) | Generic/parametric type forall A. F<A> |
| False (absurdity) | Empty type (Void, Never) |
| True (tautology) | Unit type () |

**Propositions-as-Types:** Every type corresponds to a logical
proposition. A type is inhabited (has a value) if and only
if the corresponding proposition is provable.

**Proofs-as-Programs:** Every program (value of a type)
corresponds to a proof of the corresponding proposition.
Writing a well-typed program = constructing a proof.

**Computation-as-Proof-Normalization:**
Executing a program (beta-reduction in lambda calculus)
corresponds to simplifying a proof (cut elimination in
natural deduction). A halting program = a normalizing proof.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Logic and type theory are two descriptions of the same thing.
Propositions ARE types. Proving a proposition IS writing a program.
A type with no values (like `Void`) is an unprovable proposition.

**One analogy:**

> Imagine a bilingual dictionary where every word in French
> has an exact equivalent in English. "Maison" = "House."
> They mean the same thing in different languages.
> Curry-Howard is that dictionary between Logic and Type Theory:
> "A and B" in logic = "Pair(A, B)" in programming.
> "A implies B" in logic = "Function A -> B" in programming.
> A PROOF in logic = a PROGRAM in programming.
> They are the same concept, in different languages.

**One insight:**

If `Void` (the empty type) corresponds to `False` in logic,
then a function of type `Void -> A` (for any A) corresponds
to the logical statement "False implies A" - which is
trivially TRUE in logic (ex falso quodlibet: from false,
anything follows). In programming: a function `Void -> A`
can never be called (there's no value of type Void to pass).
So you can write the SIGNATURE but never need to implement it.
This is exactly "ex falso quodlibet" encoded in a type signature.
Rust's `!` (Never type) and Java's `throw` expression (which
has any type) are direct applications of this principle.

---

### 🔩 First Principles Explanation

**THE DICTIONARY:**

```
┌──────────────────────────────────────────────────────┐
│ Logic             | Type Theory (Java/Haskell/Scala) │
│───────────────────|─────────────────────────────────│
│ Proposition A     | Type A                           │
│ Proof of A        | Value of type A                  │
│                   |                                  │
│ A AND B           | Pair<A, B> / record {a: A, b: B}│
│ Prove A AND B:    | Construct Pair(proofA, proofB)   │
│   prove A, prove B|                                  │
│                   |                                  │
│ A OR B            | Either<A, B>                     │
│ Prove A OR B:     | Left(proofA) or Right(proofB)    │
│   prove A, or     |                                  │
│   prove B         |                                  │
│                   |                                  │
│ A implies B       | Function A -> B                  │
│ Proof of A->B:    | Function that takes proof of A   │
│   assume A, prove B|  and returns proof of B         │
│                   |                                  │
│ False (absurdity) | Void (empty type, no values)     │
│ Nothing proves it | No values of type Void           │
│                   |                                  │
│ True (tautology)  | Unit (one value: ())             │
│ Trivially proved  | () has exactly one value         │
│                   |                                  │
│ forall x. P(x)    | Generic type: forall A. F<A>     │
│ Proof for any x   | Function that works for any type │
└──────────────────────────────────────────────────────┘
```

**COMPUTATION AS PROOF SIMPLIFICATION:**

```
┌──────────────────────────────────────────────────────┐
│ In logic: cut elimination.                           │
│ If you prove B from A, and prove A, you can          │
│ simplify to just: proof of B.                        │
│                                                      │
│ In type theory (lambda calculus):                    │
│ (\x -> f(x))(a) -> f(a)  (beta reduction)            │
│ Apply a function to an argument: reduces to result.  │
│                                                      │
│ Execution IS proof simplification:                   │
│ Running a program = simplifying a proof.             │
│ A terminated program = a fully simplified proof.     │
│ An infinite loop = a proof that never terminates     │
│   (non-normalizing term) = logical inconsistency.    │
└──────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**VOID AND THE EX FALSO PRINCIPLE:**

In Haskell:
```haskell
-- Void: a type with NO values (no constructors)
data Void  -- empty data declaration

-- "From False, anything follows" (ex falso quodlibet):
absurd :: Void -> a
absurd x = case x of {}  -- empty case: Void has no constructors
                          -- so this is exhaustive despite being empty!
```

You can write `absurd` with a valid type signature and
implementation (the empty case is exhaustive because Void
has no constructors). You can NEVER CALL it (there's no
value of type Void). This is "False implies anything" in
the type system. Rust's `!` (Never type) serves the same role:
`fn absurd(x: !) -> T` - can never be called. Used in match
arms for exhaustiveness: if you match on an unreachable branch,
the "result" is `!` (Never = False = impossible).

---

### 🎯 Mental Model / Analogy

**TYPES AS SPECIFICATIONS:**

In traditional programming: a type like `List<String>` says
"a list of strings." The type is documentation about the structure.

In Curry-Howard: a type is a PROPOSITION. `A -> B` says
"given a proof of A, I can produce a proof of B." If you
can write a total function of type `A -> B`, you have PROVED
the proposition "A implies B." The TYPE is the theorem.
The PROGRAM is the proof.

Corollary: if a type is uninhabited (no values), the corresponding
proposition is false (unprovable). `Void` cannot be constructed
= "False" cannot be proved. The type system is a theorem prover.

**MEMORY HOOK:**

"Propositions = Types. Proofs = Programs.
AND = Pair (constructor: (a, b)). OR = Either (Left or Right).
IMPLIES = Function A -> B. FORALL = Generic <A>.
FALSE = Void/Never (no values). TRUE = Unit (one value: ()).
Run program = simplify proof. Halt = terminating proof.
Loop = inconsistent proof (can prove anything from non-termination).
Dependent types: types that DEPEND on values = propositions about values.
Proof assistant (Coq/Agda/Lean) = type checker for proofs."

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
In math, to prove "A and B," you prove A separately AND
prove B separately, then combine. In programming, to construct
a Pair(A, B), you provide a value of type A AND a value
of type B. They're the same: both need "evidence" for both parts.
Curry-Howard says: math proofs and computer programs are the same thing.

**Level 2 - Student:**
```haskell
-- "A implies B implies A" is a tautology in logic.
-- As a type: a -> b -> a
-- Proof/Program:
const :: a -> b -> a
const x _ = x  -- given a and b, return a. Simple!
-- The existence of this total function PROVES the proposition.

-- "A and B implies A" (projection):
fst :: (a, b) -> a
fst (x, _) = x  -- from a pair (proof of A AND B), extract proof of A

-- "A implies A OR B" (injection):
Left :: a -> Either a b  -- given proof of A, construct proof of A OR B
```

**Level 3 - Professional:**
In Scala (with Shapeless or native for Scala 3):
```scala
// Encoding propositions as types:

// Product type = AND
case class And[A, B](left: A, right: B)

// Sum type = OR
sealed trait Or[A, B]
case class Left[A, B](value: A) extends Or[A, B]
case class Right[A, B](value: B) extends Or[A, B]

// Function type = IMPLICATION
type Implies[A, B] = A => B

// Commutativity of AND (a logical tautology):
// A AND B implies B AND A
def commute[A, B](p: And[A, B]): And[B, A] =
  And(p.right, p.left)
// This function compiles = the proposition is "proved"
// by the existence of this total function.
```

**Level 4 - Senior Engineer:**
Dependent types: propositions ABOUT VALUES.
```agda
-- Agda (dependently typed language):
-- Vector: a list where the type includes the LENGTH
data Vec (A : Set) : Nat -> Set where
  []  : Vec A 0
  _::_ : A -> Vec A n -> Vec A (suc n)

-- Safe head: only callable on non-empty vectors
-- The type PROVES the vector is non-empty (n+1 > 0)
head : Vec A (suc n) -> A
head (x :: _) = x
-- head [] is a TYPE ERROR: Vec A 0 doesn't match Vec A (suc n)
-- The proof of non-emptiness IS the type parameter.
```
In Java: we approximate this with preconditions and runtime
checks. Dependent types shift this to compile-time.
Rust's const generics (`[T; N]` for arrays of known length)
are a limited form of dependent types.

**Level 5 - Expert:**
The Calculus of Constructions (CoC, Coquand and Huet, 1988)
is the foundation of Coq. It is simultaneously:
- A strongly typed lambda calculus (programming language)
- A proof system for higher-order predicate logic
via the Curry-Howard isomorphism extended to dependent types.
In CoC: types can DEPEND on values (dependent function types),
creating the most expressive type system that remains consistent
(Girard's System F, System F-omega). Consistency (no Void proofs)
requires termination checking: ALL functions must terminate
(no infinite loops - which would prove False). Coq's kernel
is a type checker for CoC programs = a proof checker for
constructive mathematics.

---

### ⚙️ How It Works (Formal Basis)

**NATURAL DEDUCTION AND LAMBDA CALCULUS:**

```
┌──────────────────────────────────────────────────────┐
│ Natural Deduction (Logic):                           │
│                                                      │
│ [A]   B     (A implies B)  AND  A           B       │
│ ─────────── ->-elim              ─── AND-intro       │
│     B        (modus ponens)     A AND B              │
│                                                      │
│ Typed Lambda Calculus (Programs):                    │
│                                                      │
│ f : A -> B    a : A                                  │
│ ─────────────────── App                              │
│       f(a) : B                                       │
│                                                      │
│ [x : A] ... e : B                                    │
│ ──────────────────── Abs                             │
│  (\x -> e) : A -> B                                  │
│                                                      │
│ AND-intro    = pair construction: (a, b)             │
│ AND-elim L/R = pair projection:  fst, snd            │
│ OR-intro L/R = Either:           Left, Right         │
│ OR-elim      = case analysis:    match               │
│ ->-intro     = lambda:           \x -> e             │
│ ->-elim      = application:      f(x)                │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Void vs Exception for Impossible Cases**

```java
// BAD: Claiming a method returns T but actually throwing
// (lies to the type system - breaks Curry-Howard)
public static <T> T impossible(String reason) {
    throw new AssertionError("Impossible: " + reason);
    // Signature says: returns T. But it never does.
    // Java compiler allows this (runtime exception).
    // This is logically unsound: proves anything from nothing.
}

// GOOD: Use the type system to encode impossibility
// (Curry-Howard compliant: false = no values possible)

// Option 1: Java throws syntax in switch expression
// (Java 14+ switch expression)
String result = switch(status) {
    case ACTIVE -> "active";
    case INACTIVE -> "inactive";
    // Exhaustive: no default needed if enum is sealed
};

// Option 2: Rust's Never type (exact Curry-Howard model)
// fn to_string(status: Status) -> &str {
//   match status {
//     Status::Active => "active",
//     Status::Inactive => "inactive",
//     // Rust: exhaustive match, no unreachable arms needed
//   }
// }

// Option 3: Kotlin's Nothing type (equivalent to Void/Never)
// fun impossible(): Nothing = error("Impossible case")
// Return type Nothing: Kotlin knows this always throws
// Eliminates unreachable code warnings without lying to type system
```

**Example 2 - Curry-Howard in Haskell Type Classes**

```haskell
-- Curry-Howard: type classes as axiom schemas

-- The proposition "A implies A" is trivially true.
-- In Haskell: identity function exists for all types:
id :: a -> a
id x = x

-- The proposition "If A implies B implies C,
--                  AND A implies B,
--                  THEN A implies C" (S combinator)
s :: (a -> b -> c) -> (a -> b) -> a -> c
s f g x = f x (g x)

-- Curry-Howard: product type = proof of AND
data Pair a b = Pair a b  -- both a AND b must exist

-- Curry-Howard: sum type = proof of OR
data Either a b = Left a | Right b  -- proof of a OR b

-- The function `fst` proves "A AND B implies A":
fst :: Pair a b -> a
fst (Pair a _) = a

-- The function `inl` (Left) proves "A implies A OR B":
-- Left :: a -> Either a b  (built in)

-- If the TYPE exists and the FUNCTION is total: the proof exists.
-- Non-total function (pattern match failure) = incomplete proof.
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Curry-Howard is just an academic curiosity with no practical relevance" | Curry-Howard is the theoretical foundation of: (1) Proof assistants (Coq, Agda, Lean, Isabelle) used to verify: the seL4 microkernel (no bugs in 10,000 lines of C), CompCert (formally verified C compiler), CryptoVerif (cryptographic protocol proofs). (2) Haskell's type system design (QuickCheck properties, type classes, GADTs, type families). (3) Rust's ownership/borrowing type system (linear types track resource usage, directly from linear logic). (4) Scala's type system (implicits as proof search, types as propositions). (5) TypeScript's conditional types. The correspondence drives EVERY advanced type system feature in modern languages. |
| "If propositions are types, then all Java types are propositions" | All Java types ARE propositions, but in a WEAK logic (every Java type is provable = every Java type is inhabited). In Java: you can always construct a null, throw an exception, or loop infinitely. These break the logical consistency. A logically consistent type system (like Coq) requires: no null (null proves ANY type = logical inconsistency), no runtime exceptions (exception proves any type = inconsistency), and termination guarantee (infinite loops prove any type). Java's type system is logically inconsistent under Curry-Howard. Coq's type system is logically consistent (it rejects non-terminating programs). The practical implication: Coq proves are correct proofs. Java programs type-checking doesn't mean anything proved. |
| "Dependent types are only for proof assistants" | Dependent types appear in practical programming languages: Idris (general-purpose dependently typed language). Agda (ML-like with dependent types). F* (Microsoft, for security verification). Rust const generics: `[T; N]` is a type that depends on the value N (a limited form). TypeScript's template literal types: `type EventName<T extends string> = ${T}Changed` (type depends on string value). Liquid Haskell: refinement types (Haskell type + predicate, verified by SMT solver). Scala 3's match types. The trend: dependent types moving from proof assistants into production languages. |
| "You need to understand Curry-Howard to write good software" | You don't need to explicitly know Curry-Howard to benefit from it. Every time you: (1) use generics for type-safe code, (2) use Either<Error, Success> instead of exceptions, (3) use sealed class hierarchies for exhaustive matching, (4) use `Optional` instead of null, or (5) express invariants in types instead of runtime checks - you are intuitively applying Curry-Howard principles. The isomorphism explains WHY these practices work: you are encoding propositions (invariants) as types and proving them (writing programs that construct values of those types). Knowing the theory helps you go further: express MORE invariants in types, catch MORE bugs at compile time. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Breaking Logical Soundness with Null**

**Symptom:** NullPointerException at runtime in code that
"should have been caught by the type system."

**Root Cause:** In Java, null is a value of EVERY reference
type. `String s = null` is allowed. This means every type
in Java is inhabitable by null - logically, this is like
every proposition being provable by a trivial null proof.
The type system CANNOT encode "this value is non-null"
as a type constraint (without annotations).

**Curry-Howard diagnosis:** If null can inhabit type A,
then A corresponds to a proposition that is "trivially
provable by null" = meaningless as a logic proposition.
Java's type system is logically inconsistent due to null.

**Fix:** Use null-safe types: `Optional<T>` (Java), `T?` (Kotlin),
`Option<T>` (Scala/Rust). These encode the proposition
"T may or may not be present" - a logically meaningful
distinction. Kotlin's type system distinguishes `String`
(non-null, logically meaningful) from `String?` (nullable,
Optional semantics). Kotlin is closer to Curry-Howard
consistency than Java.

**Failure Mode 2: Exception Breaks Exhaustiveness**

**Symptom:** A `switch` expression covers all cases but
an exception is thrown for a case that "should not happen."

**Root Cause:** Throwing an exception inside a branch
that should return a value gives the branch ANY type
(exception's type is logically Bottom/Void). This fools
the compiler into thinking the match is exhaustive when
the developer is actually encoding an impossible case
as a runtime error.

**Fix:** Use sealed types/enums exhaustively. If the compiler
requires a case that "cannot happen" by your design invariant,
encode that invariant in the TYPE SYSTEM rather than throwing.
Scala sealed traits + `@unchecked` match, or Kotlin `when`
with an `else -> error("unreachable")` using `Nothing`
type. The Kotlin `Nothing` type is the correct Curry-Howard
encoding: returning Nothing (= Void = False) for an impossible case.

---

**Security Note:**

Curry-Howard has a direct security application: formal
verification of security properties. When security properties
are expressed as TYPES, the type checker verifies them:
- No SQL injection: model user input as type `Untrusted<String>`
  and database queries as requiring `Sanitized<String>`.
  A function `Untrusted<String> -> SQL` that skips sanitization
  = TYPE ERROR (the proposition "Untrusted implies SQL-safe" is false).
- No unauthorized access: `Admin -> AdminPage` exists as a function.
  `Regular -> AdminPage` = no such function (the type is uninhabited).
  The proposition "Regular users can access admin pages" is false,
  proved by the absence of the function.

This is "type-driven security": security invariants are propositions,
types are the propositions, programs are the proofs that invariants hold.
Languages like F* (Microsoft Research) formalize this for cryptographic
protocol verification.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Type Theory` (CSF-064) - Curry-Howard is an application
  of type theory; understanding basic type theory first is essential
- `Immutability` (CSF-035) - immutable values are the "proofs"
  that types correspond to; mutation breaks the logical correspondence

**Builds On This (learn these next):**
- `Category Theory for Programmers` (CSF-068) - category theory
  is the mathematical framework that unifies Curry-Howard with
  other computational structures

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ PROPOSITIONS │ ARE types in type theory                │
│ PROOFS       │ ARE programs (values of types)          │
├──────────────┼─────────────────────────────────────────┤
│ A AND B      │ Pair<A, B> - need both to construct     │
│ A OR B       │ Either<A,B> - need one to construct     │
│ A implies B  │ Function A -> B                        │
│ forall A     │ Generic type parameter <A>              │
│ FALSE        │ Void/Never - no values possible         │
│ TRUE         │ Unit - one trivial value ()             │
├──────────────┼─────────────────────────────────────────┤
│ COMPUTATION  │ IS proof normalization (beta reduction) │
│ HALTING PROG │ IS a terminating proof                  │
│ INFINITE LOOP│ IS logical inconsistency (proves False) │
├──────────────┼─────────────────────────────────────────┤
│ COROLLARY    │ Null = logically inconsistent (Java)    │
│              │ Sealed types = logically consistent     │
├──────────────┼─────────────────────────────────────────┤
│ PRACTICE     │ Proof assistants: Coq, Agda, Lean       │
│              │ Dependently typed: Idris, F*             │
├──────────────┼─────────────────────────────────────────┤
│ SECURITY     │ Type-driven security: invariants = types│
│              │ No value of type = impossible operation │
├──────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE │ CSF-068 (Category Theory), CSF-064       │
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Propositions = Types, Proofs = Programs. A type corresponds
   to a logical proposition. A program (value of that type)
   corresponds to a proof of the proposition. A type with no
   values (`Void`/`Never`) = a false proposition (unprovable).
   Writing a well-typed total function = proving a theorem.
   This is not a metaphor - it is a mathematical isomorphism
   (Curry-Howard correspondence).
2. The logical connectives map directly to type constructors:
   AND = Product type (Pair - need both A and B to construct).
   OR = Sum type (Either - need one of A or B to construct).
   IMPLIES = Function type (A -> B: given proof of A, produce proof of B).
   FORALL = Generic type (works for all type arguments).
   FALSE = Void/Never (no values possible = unprovable).
   Whenever you write a generic function that compiles, you are
   proving a universally quantified theorem.
3. Null and exceptions break the Curry-Howard correspondence:
   null can inhabit any type (making every type "trivially provable"),
   and throwing an exception from any function gives it any return type
   (logically unsound). Logically consistent languages (Coq, Agda)
   reject null and require termination. Practical languages (Kotlin,
   Rust, Scala) approximate consistency via `Option`/`Maybe`/`Result`
   types that encode absence as a TYPE DISTINCTION rather than a runtime null.

**Interview one-liner:**
"Curry-Howard: propositions = types, proofs = programs. AND = Pair type,
OR = Either type, implies = function type, forall = generic, False = Void.
Writing a total function that type-checks IS proving the corresponding theorem.
Foundation of Coq/Agda/Lean proof assistants. In practice: sealed types,
Either, Optional = more logically correct type design than null/exceptions."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
If you can encode an invariant as a TYPE, the compiler proves
it holds. If you encode it as a runtime check, YOU must
ensure it holds. The more invariants you can push from
runtime to compile-time (from documentation to type),
the fewer bugs escape to production. Curry-Howard tells
you HOW to encode invariants as types: use the logical
connective that matches the invariant structure. "Either
this succeeds or it fails" = `Either<Error, Success>` (OR type).
"Both the user and the session must exist" = `Pair<User, Session>`
(AND type). "An authorization token implies access" = `Token -> Access`
(implication type). This discipline is the difference between
"hope the invariant holds" and "the compiler proves it holds."

**Where else this pattern appears:**

- **Rust's ownership system and linear logic** - Linear logic
  (Girard, 1987) extends intuitionistic logic with a "use exactly
  once" connective. Via Curry-Howard, linear logic corresponds
  to linear types: a value can be used EXACTLY ONCE. Rust's
  ownership system is essentially linear types: an owned value
  can be consumed exactly once (moved, not copied). This eliminates
  use-after-free (using a value twice) and double-free (freeing
  twice) - both linear logic violations. Rust's borrow checker
  is a linear type system enforcing a linear logic invariant.
  Curry-Howard makes this connection precise: the borrow checker
  is a proof checker for linear logic propositions about resources.
- **Session types and protocol verification** - Session types
  (Honda, 1993) use Curry-Howard to encode COMMUNICATION PROTOCOLS
  as types. A session type describes the sequence of messages
  in a protocol: "first send an Int, then receive a String,
  then close." A program that implements the protocol must have
  a type that matches the session type. MISUSING the protocol
  (sending a String when an Int is expected) = TYPE ERROR.
  Session types are a Curry-Howard encoding of temporal logic
  propositions about protocols. Research languages (Session
  Types in Haskell, Rust session types via typed channels)
  bring this to practical systems. The vision: formal protocol
  correctness at compile time, not at integration test time.
- **Smart contracts and formal verification** - Ethereum smart
  contracts hold billions of dollars. The DAO hack (2016, $60M stolen)
  was a reentrancy bug. Formal verification applies Curry-Howard:
  encode safety properties as types, verify by type checking.
  Move language (Facebook/Aptos blockchain): uses linear types
  (Curry-Howard / linear logic) to ensure tokens cannot be created
  from nothing (no counterfeiting) or duplicated (no double-spending).
  The linear type system makes it a TYPE ERROR to copy a resource
  representing a token. The theorem "tokens are conserved" is proved
  by the type system, not by the smart contract code's correctness.
  This is Curry-Howard applied to financial invariants.

---

### 💡 The Surprising Truth

The formal correspondence between programs and proofs was
discovered INDEPENDENTLY by Haskell Curry (1934, for
combinatory logic) and William Howard (1969, for lambda calculus)
without either knowing the other was working on the same
thing. Howard's paper was never officially published - it
circulated as a private letter for over a decade before
being included in a 1980 book. The Curry-Howard correspondence
is therefore named after two researchers who never collaborated
and one of whom never published the work. The truly surprising
implication: every time you write a correctly typed program,
you are constructing a mathematical proof in intuitionistic
logic - whether you know it or not. Every Java generic method
`<T> List<T> filter(List<T> list, Predicate<T> pred)` is a proof
of the theorem "for all types T, given a list of T and a predicate
on T, there exists a list of T." The programmer is a theorem
prover. The type checker is the proof verifier. The program
is the proof certificate. Most developers write thousands of
theorem proofs over their career without ever realizing it.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[TRANSLATE]** Translate these propositions to Java/Kotlin types:
   (a) "A and B and C," (b) "A or B," (c) "A implies (B implies A),"
   (d) "For all types A, A implies A," (e) "False implies anything."
   For each, write the FUNCTION that corresponds to the proof.

2. **[ANALYZE]** Why is `null` in Java logically unsound under
   Curry-Howard? What Java/Kotlin/Rust mechanisms restore logical
   soundness for the "possibly absent value" case?

3. **[IDENTIFY]** Given the Haskell function `either :: (a -> c) -> (b -> c) -> Either a b -> c`,
   identify the corresponding logical proposition. What does this
   function PROVE?

4. **[CONNECT]** Rust's `!` (Never) type is used in `match` arms
   that are unreachable. Explain why this is Curry-Howard consistent:
   what does returning `!` mean logically?

5. **[DESIGN]** Using Curry-Howard principles, design a type-safe
   user permission system in Kotlin where: an `Admin` token can
   access admin endpoints, a `User` token can access user endpoints,
   neither can access the other's endpoints, and the compiler
   enforces these constraints (no runtime authorization checks needed).
   What types do you define? What functions?

---

### 🧠 Think About This Before We Continue

**Q1.** If writing a total function proves a theorem, what does
writing a PARTIAL function (one that throws exceptions or loops)
correspond to logically?

*Hint: Partial functions break the Curry-Howard correspondence in specific ways:
(1) EXCEPTIONS: throwing an exception from a function of type A -> B
    means the function can "prove" B without a proof of A (if A is given
    but exception thrown before using it) or "prove" B without A at all
    (if the function always throws). This is logical inconsistency:
    you can "prove" anything from nothing by throwing.
    In a logically consistent system (Coq), ALL functions must be total.
    No exceptions allowed (they would make the system inconsistent).
    Haskell's `error` function has type `String -> a`: proves anything
    given a string message. This IS a logical inconsistency.
    Haskell lives with it because: `error` only affects programs
    that evaluate the "proof" (the value). It's "lazy inconsistency."
(2) INFINITE LOOPS: an infinite loop in a function body can also
    "prove" anything (give it any type) because it never returns.
    In Coq: all functions must be PROVABLY TERMINATING (via structural
    recursion or fuel parameters). Non-termination = inconsistency.
    Haskell allows non-termination (lazy evaluation defers it).
    Proof assistants reject it.
(3) IMPLICATIONS: partial functions correspond to partial proofs
    (proofs that work for SOME inputs but fail for others). In logic,
    partial proofs are incomplete (not valid proofs).
Summary: total function = valid proof. Partial function = partial/invalid proof.
Logically consistent languages (Coq) require total functions.
Production languages accept partial functions for pragmatism.*

**Q2.** In Rust, the `match` statement must be exhaustive for sealed enums.
Is this Curry-Howard? What logical principle does exhaustive pattern matching enforce?

*Hint: Yes, exhaustive pattern matching is directly Curry-Howard.
An exhaustive match on a sum type (`Either<A, B>`) corresponds to
OR-elimination in logic:
```
Logic (OR-elimination):
  If A OR B,
  AND if A implies C,
  AND if B implies C,
  THEN C.

Programming (match):
  match e {
    Left(a) => f(a),   // A -> C
    Right(b) => g(b),  // B -> C
  }
  // e: Either<A, B>
  // f: A -> C
  // g: B -> C
  // result: C
```
Rust's compiler requires the match to be exhaustive because:
if a branch is missing, the OR-elimination rule is incomplete
(you handle "A" but not "B" = incomplete proof of "OR implies C").
The compiler is checking PROOF COMPLETENESS.
Non-exhaustive match = incomplete proof = type checker rejects it.
Sealed types (Rust enums, Kotlin sealed classes, Scala sealed traits):
the compiler KNOWS all cases of the sum type because the type is sealed.
This enables exhaustiveness checking (= completeness checking for proofs).
Open (non-sealed) types cannot have exhaustive match: there may be
future cases (subclasses) not known at compile time.
Exhaustiveness is one of the most practically valuable applications
of Curry-Howard: the type checker prevents forgetting to handle cases.*

---

### 🎯 Interview Deep-Dive

**Q1: "What is the Curry-Howard correspondence and why should a Java developer care?"**

*Why they ask:* Tests theoretical depth. Shows staff-level thinking.

*Strong answer includes:*
- Core: Propositions = Types, Proofs = Programs.
- Practical applications:
  1. `Either<Error, Success>` vs exceptions: Either encodes
     "may fail" as a TYPE. Caller must handle both branches
     (exhaustive match). Exception encoding is logically impure
     (can throw from any type). Either is closer to Curry-Howard.
  2. `Optional<T>` vs null: Optional encodes "may be absent"
     in the type. Null makes every type logically inconsistent.
  3. Sealed classes + exhaustive when/switch: the compiler
     proves you handled all cases (OR-elimination completeness).
  4. Generics: `<T> T identity(T t)` proves "for all types T, T -> T."
     This is the universal quantifier in code.
  5. Rust's ownership: linear types (linear logic via Curry-Howard)
     ensure each resource used exactly once = no use-after-free.
- You don't need to know the theory to apply it, but knowing it
  tells you WHY these patterns work: they encode propositions as types.
  More invariants in types = more bugs caught at compile time.

**Q2: "How do proof assistants like Coq use Curry-Howard in practice?"**

*Why they ask:* Tests awareness of formal methods.

*Strong answer includes:*
- Coq is simultaneously a programming language (Gallina, functional)
  and a proof assistant for intuitionistic logic.
- In Coq, you write PROGRAMS (terms in Gallina). The type of the
  program is the PROPOSITION being proved. The program IS the proof.
- The Coq kernel is a TYPE CHECKER: it verifies the proof is correct
  by type-checking the program.
- EXTRACTION: Coq proofs can be extracted to working Haskell,
  OCaml, or Scheme programs. A Coq proof of an algorithm's correctness
  gives you a provably correct implementation.
- Real applications:
  1. seL4 microkernel: formally verified in Isabelle/HOL (similar
     foundation). Every security property proved. Used in critical
     systems (autonomous vehicles, aerospace).
  2. CompCert: formally verified C compiler in Coq. Every compilation
     step preserves semantics. No miscompilations.
  3. CryptoVerif: cryptographic protocol proofs.
- Limitation: formal verification requires significant effort.
  Practical for safety-critical code; economic for most software.
  Property-based testing (QuickCheck) is the practical approximation.
