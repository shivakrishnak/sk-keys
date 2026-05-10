---
id: CSF-075
title: Formal Semantics (Denotational, Operational)
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
version: 2
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Dictionary"
nav_order: 75
permalink: /csf/formal-semantics-denotational-operational/
---

# CSF-075 - Formal Semantics (Denotational, Operational)

⚡ TL;DR - Formal semantics precisely define what a program means: operational semantics describe execution as state transitions; denotational semantics map programs to mathematical objects; axiomatic semantics reason about properties via assertions.

| CSF-075         | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | CSF-073, CSF-074                      |                 |
| **Used by:**    | CSF-076                               |                 |
| **Related:**    | CSF-073, CSF-074, CSF-076             |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A language spec says: "`x += 1` increments x by 1."
But what is "x"? What is "1"? What does "increment" mean
for overflow? What if `x` is not initialised? Natural
language specs are ambiguous; two compilers may implement
the same language differently for edge cases. Without
formal semantics, "correct" is undefined.

**THE BREAKING POINT:**
The Ada language (1980) was specified with formal
mathematics because imprecise specs had caused multiple
compiler incompatibilities in earlier DoD projects.
The C standard's use of "undefined behaviour" is precisely
a formal semantics choice: certain behaviours are outside
the spec, giving compilers freedom to optimise.

**THE INVENTION MOMENT:**
Christopher Strachey (1960s) and Dana Scott developed
denotational semantics: map programs to mathematical
objects (functions). Gordon Plotkin (1981) developed
operational semantics: define execution as state transitions
(evaluation rules). Robert Floyd (1967) and C.A.R. Hoare
(1969) developed axiomatic semantics: Hoare triples
`{P} C {Q}` specify what is true before and after execution.

**EVOLUTION:**
Practical applications: Coq, Lean, Isabelle prove program
properties using formal semantics. Java's JVM specification
uses operational semantics. WebAssembly has a formal
specification in reduction semantics. Rust's Stacked Borrows
model is a formal operational semantics for Rust's aliasing
rules. CompCert is a formally verified C compiler with
full denotational semantics proof.

---

### 📘 Textbook Definition

**Formal semantics** assigns mathematical meaning to
programming language constructs. Three main approaches:
**Operational semantics**: defines meaning by specifying
how a program executes step-by-step (state transitions).
Big-step (natural): maps program+state to final value.
Small-step (structural): defines single reduction steps.
**Denotational semantics**: maps each program to a
mathematical object (usually a function on domains).
**Axiomatic semantics**: defines meaning via logical
assertions. Hoare triple `{P} C {Q}`: if precondition `P`
holds, after executing `C`, postcondition `Q` holds.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Formal semantics precisely defines what programs mean: operational semantics as execution steps; denotational as mathematical functions; axiomatic as proof rules.

**One analogy:**

> Formal semantics is like a contract with three levels:
> Operational: "the procedure is: do step A, then step B, then..."
> Denotational: "the result is: the function f(x) = ..."
> Axiomatic: "the guarantee is: if X is true before, then Y is true after."
> Natural language contracts are ambiguous; formal semantics is law.

**One insight:**
For most programmers, the practical payoff is axiomatic
semantics: Hoare logic and its descendants (separation
logic, Dafny contracts, Java assertions) let you prove
program properties without executing the program.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Operational: meaning = execution trace; different execution strategies (CBV, CBN) give different semantics.
2. Denotational: meaning = mathematical function; compositional (meaning of a program = composition of sub-meanings).
3. Axiomatic: meaning = Hoare triple `{P} C {Q}`; strongest postcondition or weakest precondition calculus.
4. Full abstraction: denotational = operational (observationally); hard to achieve in general.
5. All three are equivalent for total, deterministic languages; differ for non-determinism, concurrency, effects.

**OPERATIONAL SEMANTICS (small-step):**

```
Evaluation rules for arithmetic expressions:
  n -> n  (number is a value; doesn't reduce)
  e1 -> e1'
  ----------  (reduce left operand first)
  e1 + e2 -> e1' + e2

  e2 -> e2'
  ----------  (reduce right operand if left is a value)
  v1 + e2 -> v1 + e2'

  n1 + n2 -> n1+n2  (arithmetic: add the numbers)

  Example: (1+2) + (3+4)
    -> 3 + (3+4)    [reduce left]
    -> 3 + 7        [reduce right]
    -> 10           [add]
```

**HOARE LOGIC (axiomatic):**

```
Assignment axiom:
  {P[E/x]} x := E {P}
  (substitute E for x in postcondition to get precondition)

Sequence rule:
  {P} C1 {Q}  {Q} C2 {R}
  ----------------------
    {P} C1; C2 {R}

While rule:
  {P ∧ B} C {P}
  -------------------------  (loop invariant)
  {P} while B do C {P ∧ ¬B}

Example: {x >= 0} y := x + 1 {y > 0}
  Precondition: x >= 0
  Assignment: substitute x+1 for y in {y > 0}
  Get: {x+1 > 0}, i.e., {x > -1}, i.e., {x >= 0} ✓
```

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Programs have precise meanings that natural language cannot fully capture.
**Accidental:** Different semantic frameworks required for different properties (safety vs liveness vs concurrency).

---

### 🧪 Thought Experiment

**SETUP:**
What does `x := x + 1` mean? Operationally vs denotationally
vs axiomatically.

**OPERATIONALLY (big-step):**

```
<x := x+1, σ> → σ[x ↦ σ(x)+1]
(state σ updated: x mapped to its old value plus 1)
```

**DENOTATIONALLY:**

```
⟦x := x+1⟧ = λσ. σ[x ↦ σ(x)+1]
(maps a state σ to a new state where x = old x + 1)
```

**AXIOMATICALLY (Hoare):**

```
{x = n} x := x+1 {x = n+1}
(if x equals n before execution, then x equals n+1 after)
```

**THE INSIGHT:**
All three agree for this simple case. They diverge for:

- Non-determinism: operational can model it; classical denotational is harder.
- Concurrency: interleaving operational semantics; denotational requires powerdomains.
- Infinite loops: denotational uses domain theory (⊥ for divergence); operational has infinite reduction.

---

### 🧠 Mental Model / Analogy

> Formal semantics is like three ways to describe a recipe:
> Operational: "Step 1: mix flour and water. Step 2: knead.
> Step 3: bake at 200°C for 30 minutes." — defines how.
> Denotational: "This recipe is a function: ingredients →
> bread." — defines what the result is.
> Axiomatic: "If you start with flour, water, and yeast,
> and follow the steps, you will have leavened bread." —
> defines the guarantee.

**Element mapping:**

- Recipe = program
- Steps = operational reduction rules
- Ingredients → bread function = denotational meaning
- Guarantee = Hoare triple
- Ambiguous ingredient amount = undefined behaviour

Where this analogy breaks down: recipes are sequential;
formal semantics handles non-determinism, concurrency,
and infinite loops that recipes don't.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Formal semantics is a precise mathematical description
of what a program does. Instead of saying "x += 1 adds 1
to x," formal semantics says exactly what state changes
occur, what happens at boundaries, and what is guaranteed.

**Level 2 - How to use it (junior developer):**
Practical: use Hoare-style assertions in code. Java's
`assert` statement, JML (Java Modeling Language), Dafny,
and DbC (Design by Contract) all use Hoare-logic-inspired
assertion systems. A Dafny `requires` / `ensures` pair
is a Hoare triple. Writing these is applied axiomatic
semantics.

**Level 3 - How it works (mid-level engineer):**
Weak precondition calculus (Dijkstra, 1975): given a
postcondition Q and command C, compute the weakest
precondition wp(C, Q) that guarantees Q after C.
For assignment: `wp(x := E, Q) = Q[E/x]`
(substitute E for x in Q). For sequence:
`wp(C1; C2, Q) = wp(C1, wp(C2, Q))`.
This calculus can be automated (Dafny, Why3).

**Level 4 - Why it was designed this way (senior/staff):**
Denotational semantics requires mathematical foundations
(domain theory, Scott continuity) to handle recursive
definitions and infinite loops. A recursive program
`f(x) = f(x+1)` has denotational semantics: `⊥` (bottom,
denoting non-termination). The fixed-point theorem
(Tarski, Kleene) provides the mathematical basis: the
meaning of a recursive program is the least fixed point
of a functional. This gives denotational semantics
a clean mathematical characterisation even for
non-terminating programs.

**Expert Thinking Cues:**

- When writing loop invariants: you're doing Hoare logic
- When a compiler optimisation changes observable behaviour: it violates the language's operational semantics
- When proving an API contract: think in Hoare triples (`{requires}` function `{ensures}`)

---

### ⚙️ How It Works (Mechanism)

**Dafny (applied axiomatic semantics):**

```dafny
// Dafny: verifier checks Hoare triples automatically
method Increment(x: int) returns (y: int)
    requires x >= 0       // precondition P
    ensures y == x + 1    // postcondition Q
    ensures y > 0         // stronger postcondition
{
    y := x + 1;
    // Dafny verifies: y = x+1 and x >= 0 implies y > 0
}
// If verification fails: Dafny reports the failing triple
```

**Java JML-style assertion:**

```java
// Informal Hoare triple as code comments + assert
void processPayment(int amount) {
    // PRE: amount > 0 && balance >= amount
    assert amount > 0 : "amount must be positive";
    assert balance >= amount : "insufficient balance";

    balance -= amount; // C

    // POST: balance == old(balance) - amount && amount > 0
    assert balance >= 0 : "balance invariant violated";
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**FORMAL VERIFICATION FLOW:**

```
Program specification (Hoare triples)    <- YOU ARE HERE
  |-> {requires} precondition defined
  |-> {ensures} postcondition defined
  |-> Loop invariants specified
  |
Verification condition generation:
  |-> wp calculus computes VCs
  |-> VCs = logical formulae to prove
  |
SMT solver (Z3, CVC5):
  |-> Checks if VCs are valid (tautologies)
  |-> If yes: program is correct for the spec
  |-> If no: counterexample provided
  |
Result:
  |-> Verified: no runtime assertion violation possible
  |-> Failed: concrete input that violates postcondition
```

---

### ⚖️ Comparison Table

| Approach     | Meaning Defined As                  | Strength                            | Weakness                                       |
| ------------ | ----------------------------------- | ----------------------------------- | ---------------------------------------------- |
| Operational  | Execution rules (state transitions) | Intuitive; close to implementation  | Doesn't abstract over implementation           |
| Denotational | Mathematical functions (domains)    | Compositional; mathematically clean | Hard for concurrency/effects                   |
| Axiomatic    | Hoare triples / assertions          | Directly relates to correctness     | Requires loop invariants; not always decidable |

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                        |
| ------------------------------------------------------ | ---------------------------------------------------------------------------------------------- |
| "Formal semantics is only for researchers"             | Java JVM spec, WebAssembly spec, Rust Stacked Borrows are all formal semantics                 |
| "Testing replaces formal verification"                 | Testing finds bugs in tested paths; formal verification proves all paths                       |
| "Operational semantics is just 'how the program runs'" | Operational semantics is a mathematical abstraction of execution; not an actual implementation |
| "Hoare logic requires a proof assistant"               | Dafny, Why3, and SPARK Ada perform automated Hoare-logic verification with SMT solvers         |
| "Undefined behaviour is a spec omission"               | Undefined behaviour is a deliberate formal semantics choice to leave certain cases unspecified |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Missing Loop Invariant**
**Symptom:** Dafny/Frama-C verification fails at loop.
**Root Cause:** Invariant not specified; verifier can't prove postcondition.
**Fix:** Identify what is preserved by each loop iteration;
state it as `invariant I`.

**Mode 2: Spec Too Weak**
**Symptom:** Verification passes but implementation is wrong for some input.
**Root Cause:** Postcondition doesn't fully characterise correct behaviour.
**Fix:** Strengthen postcondition; add more properties.

**Mode 3: Compiler Violates Operational Semantics**
**Symptom:** Optimised program behaves differently than un-optimised.
**Root Cause:** Compiler exploited UB (C semantics); or relies on unspecified evaluation order.
**Fix:** Use `-fsanitize=undefined`; review language spec for undefined evaluation order.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CSF-073 - Curry-Howard Correspondence]]
- [[CSF-074 - Category Theory for Programmers]]

**Builds On This (learn these next):**

- [[CSF-076 - Type Theory (System F, HM Inference)]]

**Alternatives / Comparisons:**

- Model checking (SPIN, TLA+): alternative to Hoare logic for temporal properties
- Abstract interpretation (Astrée): automated static analysis based on abstract semantics

---

### 📌 Quick Reference Card

```
+-----------------------------------------------------+
| WHAT IT IS      Precise math definition of program  |
|                 meaning (execution, functions, proof)|
| PROBLEM         Natural language specs are ambiguous;|
| IT SOLVES       compilers implement things differently|
| KEY INSIGHT     Operational: how; Denotational: what;|
|                 Axiomatic: why (correctness guarantee)|
| USE WHEN        Language spec; formal verification;  |
|                 safety-critical code (Dafny, SPARK) |
| AVOID           Over-formalising non-critical code   |
| TRADE-OFF       Precision vs specification effort    |
| ONE-LINER       Hoare triple: {P} code {Q} = spec   |
| NEXT EXPLORE    CSF-076, Dafny, TLA+, Coq            |
+-----------------------------------------------------+
```

**If you remember only 3 things:**

1. Operational: program meaning = execution steps (reduction rules); used in JVM spec, WebAssembly.
2. Axiomatic: `{P} C {Q}` Hoare triple = precondition/postcondition; foundation for Dafny/SPARK verification.
3. Formal semantics makes "undefined behaviour" precise: it's a deliberate choice to leave some cases unspecified.

**Interview one-liner:**
"Formal semantics precisely defines program meaning: operational semantics as state-transition execution rules (used in the JVM and WebAssembly specs), denotational semantics as mathematical domain functions, and axiomatic semantics via Hoare triples — the foundation for automated program verification tools like Dafny and SPARK."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Precision eliminates ambiguity; ambiguity is the root of
most software specification bugs. Hoare-style
preconditions and postconditions (requires/ensures)
applied to critical APIs are practical formal semantics:
they make the contract explicit, machine-checkable, and
document the developer's intent permanently.

**Where else this pattern appears:**

- **API contracts** — OpenAPI schemas are operational specs; response postconditions are axiomatic
- **Database stored procedures** — assertions before/after are axiomatic contracts
- **Protocol specifications** — TCP state machine (RFC 793) is operational semantics for the TCP protocol

---

### 💡 The Surprising Truth

The CompCert project (INRIA, 2006-present) built a formally
verified C compiler using Coq: every compilation step has
a machine-checked proof that it preserves the operational
semantics of the C source. This means CompCert-compiled
code is provably correct — the compiler cannot introduce
bugs. In testing across 180+ C programs, CompCert found
0 bugs introduced by compilation; all other tested compilers
(GCC, LLVM) introduced at least some wrong-code bugs.
The CompCert experience showed that formal semantics for
practical compilers is not only possible but provides
tangible correctness benefits — at roughly 10x the
development cost of an unverified compiler.

---

### 🧠 Think About This Before We Continue

**Q1 (First Principles):** Operational semantics defines
program meaning as execution. But two different execution
strategies (call-by-value vs call-by-name) give different
operational semantics for the same language. How does
Haskell's lazy evaluation (call-by-need) change the
operational semantics of `let x = error "boom" in 1`
vs strict evaluation?

_Hint:_ Call-by-value: evaluates `error "boom"` immediately;
result = error. Call-by-need (Haskell): `x` is never
used in `1`; `error` is never evaluated; result = 1.
Same syntax; different operational semantics; different
result.

**Q2 (Design Trade-off):** Dafny verifies Hoare triples
automatically using SMT solvers. But verification can
timeout for complex loop invariants. In a safety-critical
payment processing service, which code should be Dafny-verified
and which should be tested only?

_Hint:_ Verify: arithmetic on financial amounts (overflow,
correctness), state machine transitions, critical algorithms.
Test-only: I/O paths, integration, UI. The 20% of code
with the highest consequence-of-bug is worth formal verification;
the 80% I/O glue code is not.

**Q3 (System Interaction):** Rust's Stacked Borrows model
is an operational semantics for Rust's aliasing rules.
When a Rust program invokes `unsafe`, it steps outside
the formally verified operational semantics. What does
this mean for the safety guarantees of a Rust library
that uses `unsafe` internally?

_Hint:_ The library's public API may be safe (no UB visible
to callers) even if the implementation uses `unsafe`.
This is "sound unsafe": the unsafe code is an implementation
detail that doesn't expose UB through the safe API.
Research the Rust unsafe code guidelines for what
"soundness" means for unsafe Rust libraries.
