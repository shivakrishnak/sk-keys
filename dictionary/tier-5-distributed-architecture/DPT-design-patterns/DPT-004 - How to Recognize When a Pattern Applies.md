---
id: DPT-004
title: How to Recognize When a Pattern Applies
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★☆☆
depends_on:
used_by:
related:
tags:
  - dpt
  - foundational
  - mental-model
status: complete
version: 1
layout: default
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 4
permalink: /dpt/how-to-recognize-when-a-pattern-applies/
---

# DPT-004 - How to Recognize When a Pattern Applies

⚡ TL;DR - Pattern recognition is the skill of matching a design problem's shape to a pattern's applicability statement — the right question is not "what pattern can I use here?" but "do the forces of this problem match a known pattern?"

| DPT-004         | Category: Design Patterns | Difficulty: ★☆☆ |
| :-------------- | :------------------------ | :-------------- |
| **Depends on:** | DPT-001, DPT-002, DPT-003 |                 |
| **Used by:**    | DPT-005, DPT-061          |                 |
| **Related:**    | DPT-001, DPT-061, DPT-070 |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Engineers know pattern names but not when to apply
them. They ask "which pattern should I use?" rather
than "does a known pattern fit this problem?" The
result: patterns applied incorrectly (wrong problem);
patterns forced onto problems they don't fit; or
patterns missed entirely (reinventing the wheel).

**THE BREAKING POINT:**
A junior engineer, having just read the GoF book,
applies Factory Method to a simple object creation
that requires no variation. Three classes and an
interface for a problem a constructor would solve.
The code is harder to understand than the problem
required. Pattern recognition failed in both directions:
forcing a pattern where none is needed.

**THE INVENTION MOMENT:**
GoF's pattern format includes "Applicability" as a
first-class section: explicit conditions under which
the pattern applies. Eric Freeman's "Head First Design
Patterns" (2004) focused on pattern recognition as
a teachable skill. DDD's "strategic design" formalized
the context analysis that precedes pattern selection.

**EVOLUTION:**
Modern: pattern selection frameworks (DPT-061) provide
systematic decision trees. IDEs (IntelliJ) suggest
refactorings (e.g., "convert to Strategy") based on
code structure detection. AI code assistants can
recognise pattern shapes in existing code.

---

### 📘 Textbook Definition

**Pattern recognition** in software design is the
process of identifying that a current design problem
matches the forces and applicability conditions
described in a known pattern. The GoF's "Applicability"
section for each pattern provides the matching criteria:
the specific problem shapes, structural tensions, and
context conditions that the pattern is designed to
resolve. Recognition precedes application; incorrect
recognition leads to misapplication.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Pattern recognition = reading a problem's forces and matching them to a known pattern's applicability statement, not applying a pattern then finding a justification.

**One analogy:**

> Recognising a pattern is like diagnosing an illness.
> A doctor doesn't pick a treatment then find symptoms
> to justify it. They observe symptoms first, then
> match to known conditions. Pattern application works
> the same: observe the forces in your design problem;
> then match to a pattern's applicability conditions.

**One insight:**
The most important GoF section is "Applicability." It
lists the specific conditions under which the pattern
applies. Read this section before applying any pattern.
If the conditions are not present, the pattern will
be a forced fit.

---

### 🔩 First Principles Explanation

**FOUR-STEP PATTERN RECOGNITION PROCESS:**

```
Step 1: IDENTIFY THE FORCES
  Forces = tensions in the design problem that need
  to be balanced. Common forces:
    - Need for flexibility vs simplicity
    - Need to decouple caller from implementation
    - Need to add behaviour without modifying code
    - Need to notify multiple parties on state change
    - Need to create objects without specifying exact type

Step 2: MATCH FORCES TO PATTERN APPLICABILITY
  GoF Applicability examples:
    Strategy: "several classes differ only in their
    behaviour... need to use different variants of
    an algorithm... algorithm has data clients
    shouldn't know about"

    Observer: "change to one object requires changing
    others and you don't know how many objects need
    to change"

    Factory Method: "a class can't anticipate the
    class of objects it must create"

Step 3: CHECK THE CONSEQUENCES
  Each pattern's consequences tell you what you gain
  and lose. Are these trade-offs acceptable for this
  context?

Step 4: SIMPLEST SOLUTION FIRST
  If a simpler solution (a single class, a direct
  implementation) meets the forces, prefer it over
  the pattern. Apply the pattern only when its
  forces are genuinely present.
```

**PATTERN RECOGNITION CUES BY SYMPTOM:**

```
Symptom: "I need to create objects but don't know
  the exact type at compile time"
  -> Candidate: Factory Method / Abstract Factory

Symptom: "I need to add behaviour to an object
  without modifying its class"
  -> Candidate: Decorator / Strategy

Symptom: "When this object changes, many others
  need to know about it"
  -> Candidate: Observer

Symptom: "The same algorithm but with different
  implementations, switchable at runtime"
  -> Candidate: Strategy

Symptom: "A complex subsystem should be hidden
  behind a simple interface"
  -> Candidate: Facade

Symptom: "I need to queue, log, undo operations"
  -> Candidate: Command

Symptom: "A tree of objects where each node
  and leaf should be treated uniformly"
  -> Candidate: Composite
```

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Identifying that a design problem has a known solution is necessary to avoid reinventing.
**Accidental:** Forcing a pattern onto a problem that has a simpler direct solution.

---

### 🧪 Thought Experiment

**SETUP:**
You have three design problems. Apply the recognition
process to each.

**Problem A:**
Your `ReportGenerator` creates PDF, CSV, or Excel
reports. The format is selected at runtime based on
user preference. Adding a new format requires
modifying `ReportGenerator`.

Forces:

- Multiple interchangeable behaviours (format types)
- Selection at runtime
- Adding new formats without modifying caller

Pattern match: Strategy (multiple interchangeable
algorithms, switchable at runtime).

**Problem B:**
You need to provide a unified interface to a set of
interfaces in a payment processing library (3 different
provider SDKs with different APIs).

Forces:

- Incompatible interface needs to be compatible
- Client should call one interface regardless of provider

Pattern match: Adapter (converts one interface to another).

**Problem C:**
You want to add logging and caching to your
`UserService` without modifying it.

Forces:

- Add behaviour to an existing object without modification
- Behaviours should be composable (logging AND caching)

Pattern match: Decorator (adds responsibilities to
individual objects dynamically).

---

### 🧠 Mental Model / Analogy

> Pattern recognition is a lock-and-key model. The
> problem has a keyhole shape (forces, applicability
> conditions). Each pattern is a key with a specific
> shape (its Applicability section). Recognition is
> trying the key against the lock: does the key shape
> match the lock shape? If yes, the key opens the door
> (pattern applies). If no, trying to force the key
> damages the lock (misapplied pattern makes code worse).

**Element mapping:**

- Lock = design problem with specific forces
- Key = pattern with specific applicability conditions
- Lock shape = problem's applicability conditions
- Key shape = pattern's Applicability section
- Wrong key = forced pattern fit

Where this analogy breaks down: multiple patterns may
fit the same problem (lock has multiple keys); the
choice between them requires evaluating consequences,
not just applicability.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Before applying a design pattern, check: does my
problem actually match this pattern's description?
If it does, apply it. If it doesn't, don't force it.

**Level 2 - How to use it (junior developer):**
Read the GoF's "Applicability" section for any pattern
before applying it. Can you find your problem's forces
expressed in the Applicability section? If yes: apply.
If no: stop and consider whether you need the pattern.

**Level 3 - How it works (mid-level engineer):**
Pattern recognition is a skill built by reading code,
not just patterns. Reading production frameworks
(Spring, React, Angular) with the question "what
pattern is this?" accelerates recognition. Spring
AOP = Proxy. React Hooks = Strategy/Observer. Angular
DI = Abstract Factory.

**Level 4 - Why it was designed this way (senior/staff):**
The GoF included Applicability specifically because
premature pattern application is a failure mode. Their
experience: engineers who learned patterns over-applied
them. The Applicability section is a gate: you must
check it before proceeding. The pattern structure
forces the question: "does my context satisfy these
conditions?"

**Expert Thinking Cues:**

- Start with the problem, not the pattern. Never ask "where can I apply Factory Method?"
- The simplest solution that resolves the forces is the right solution, pattern or not.
- Over-time, experienced engineers recognise patterns in problem descriptions before touching the code.

---

### ⚙️ How It Works (Mechanism)

**Observer applicability check example:**

```
GoF Observer - Applicability:
  "Use the Observer pattern in any of the following
  situations:
  - When an abstraction has two aspects, one dependent
    on the other. Encapsulating these aspects in
    separate objects lets you vary and reuse them
    independently.
  - When a change to one object requires changing
    others, and you don't know how many objects need
    to change.
  - When an object should be able to notify other
    objects without making assumptions about who
    those objects are."

My problem: OrderService notifies
  EmailNotifier, AnalyticsTracker, InventoryReserver.
  New notifiers will be added.
  OrderService should not depend on concrete notifiers.

Applicability check:
  "change to one object requires changing others"
  -> YES (order placed -> notify all)
  "don't know how many objects need to change"
  -> YES (future notifiers unknown)
  "shouldn't make assumptions about who those objects are"
  -> YES (want to add notifiers without modifying OrderService)

Result: Forces match. Observer applies.
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Pattern recognition decision flow:**

```
Design problem identified:           <- YOU ARE HERE
  e.g., "need to notify multiple
  components when an order is placed"
  |
Identify forces:
  - Unknown number of listeners
  - Listeners should be independent
  - Caller should not depend on listeners
  |
Scan pattern applicability sections:
  Observer: "notifying unknown number of objects"
  -> Matches
  |
Check consequences:
  + Open/closed: add listeners without changing caller
  - Unexpected updates: listeners may receive unexpected
    notifications -> document contract carefully
  |
Simplest solution test:
  Could I do this without Observer?
  -> Would require modifying caller for each new listener
  -> Pattern is justified
  |
Apply Observer
Document: "Observer pattern -- rationale: unknown
number of future listeners; loose coupling required"
```

---

### ⚖️ Comparison Table

| Recognition Quality | Approach                        | Outcome                           |
| ------------------- | ------------------------------- | --------------------------------- |
| Correct             | Problem forces -> pattern match | Pattern solves the problem        |
| Over-application    | Pattern first -> justify        | Added complexity, no benefit      |
| Under-application   | No pattern recognised           | Reinvented wheel; no shared vocab |
| Misapplication      | Wrong pattern for forces        | Pattern makes problem worse       |

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                      |
| ------------------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| "I can find a pattern for any problem"                       | Not every problem has a named pattern; novel problems need novel solutions                   |
| "Reading about patterns = pattern recognition skill"         | Recognition is built by reading code and asking "what pattern is this?" not from books alone |
| "Patterns are applied at design time only"                   | Patterns can be introduced during refactoring when forces become clear in existing code      |
| "If the code compiles with the pattern, the pattern applies" | A forced fit compiles; it doesn't mean the forces matched                                    |
| "The most complex pattern is the most correct"               | Simplest solution that resolves the forces is correct; complexity is a cost, not a virtue    |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Forced Fit (Wrong Pattern for Forces)**
**Symptom:** Complex class hierarchy for a problem a direct call would solve.
**Root Cause:** Pattern selected by name recognition, not force matching.
**Diagnostic:** Ask: "what forces does this pattern resolve?" If you can't name the forces in your codebase, the pattern is a forced fit.
**Fix:** Remove the pattern; implement directly; re-introduce a pattern when genuine forces appear.

**Mode 2: Pattern Blindness (Reinventing the Wheel)**
**Symptom:** Custom notification system in 300 lines that is architecturally Observer.
**Root Cause:** Forces present; pattern not recognised; custom solution written.
**Fix:** Learn the GoF applicability conditions; read the 300-line system's forces; recognise Observer; name it; refactor to match the canonical structure.

**Mode 3: Pattern Applied Too Early**
**Symptom:** Abstract Factory for object creation when only one concrete type exists and no more are planned.
**Root Cause:** "We might need multiple types" justifies the pattern speculatively.
**Fix:** Implement directly; introduce Abstract Factory when a second concrete type is actually needed.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[DPT-001 - What Are Design Patterns and Why They Exist]]
- [[DPT-002 - The Gang of Four -- Origin and Philosophy]]

**Builds On This (learn these next):**

- [[DPT-005 - The Design Patterns Ecosystem Map]]
- [[DPT-061 - Pattern Selection Framework]]
- [[DPT-070 - Pattern-Recognition Mental Model]]

**Alternatives / Comparisons:**

- [[DPT-071 - Pattern Trade-off Framing]]

---

### 📌 Quick Reference Card

```
+-----------------------------------------------------+
| WHAT IT IS      Matching a problem's forces to a    |
|                 pattern's applicability conditions  |
| PROBLEM         Patterns applied wrong (forced fit) |
| IT SOLVES       or missed entirely (reinvention)    |
| KEY INSIGHT     Start with problem forces; not with |
|                 the pattern name                    |
| USE WHEN        Before applying any pattern         |
| AVOID WHEN      Forcing forces to match; speculative|
|                 application                         |
| TRADE-OFF       Recognition time vs direct coding   |
| ONE-LINER       Forces first; then pattern          |
| NEXT EXPLORE    DPT-005, DPT-061, DPT-070           |
+-----------------------------------------------------+
```

**If you remember only 3 things:**

1. Read the Applicability section before applying any pattern; if the conditions are not present, don't apply it.
2. Symptoms-to-pattern mapping: unknown number of notified parties = Observer; interchangeable algorithms = Strategy; hiding complex subsystem = Facade.
3. Simplest solution first; introduce the pattern when the forces that justify it actually appear in the code.

**Interview one-liner:**
"Pattern recognition starts with the problem's forces, not the pattern name; read the GoF Applicability section to check if your context matches; if forces match, apply it; if not, a simpler direct solution is better."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Matching a problem to a known solution requires
identifying what the problem fundamentally IS, not
just what it looks like. This principle of
problem-first, solution-second applies in every
discipline: a doctor observes symptoms before
prescribing; a lawyer identifies the legal question
before citing precedent; an engineer identifies
the forces before applying a pattern.

**Where else this pattern appears:**

- **Algorithm selection** -- time/space constraints + input properties -> algorithm (use binary search when sorted; use hashtable when key lookup needed)
- **Database indexing** -- query access pattern -> index type (B-tree for range; hash for equality)
- **Cloud architecture** -- traffic pattern, fault tolerance requirement -> architecture (event-driven for async; CQRS for high-read)

---

### 💡 The Surprising Truth

The GoF authors found that experienced object-oriented
designers do NOT think in patterns when designing;
they think in terms of forces and constraints. The
patterns emerge from resolving those forces. Pattern
recognition, for experts, is retrospective: "oh, this
solution I just derived is actually Observer." Novices
think pattern-first ("I'll use Strategy here") because
they don't yet have the fluency to derive solutions
from forces. The goal of learning design patterns is
not to apply them consciously; it is to internalise
the design principles so that good solutions are
derived naturally and patterns are recognised afterwards.

---

### 🧠 Think About This Before We Continue

**Q1 (First Principles):** The Composite pattern's
Applicability says: "you want clients to be able to
ignore the difference between compositions of objects
and individual objects." Map this to a concrete file
system problem and explain why the force (ignoring
the difference) is essential.

*Hint:_ File system: file and directory should respond
to the same interface (`size()`, `list()`). A directory's
`size()` recursively sums children. A file's `size()`
returns its own size. Client code: `getSize(item)` works
for both file and directory. If client had to distinguish,
every operation would need a type check. Composite
eliminates the type-check.

**Q2 (System Interaction):** In Spring Framework,
`JdbcTemplate` follows Template Method. Identify the
template method (invariant algorithm steps) and the
hook methods (variant steps the caller provides).
Why is this a better design than giving callers raw
`Connection` and `PreparedStatement` access?

*Hint:_ Template (invariant): get connection, create
statement, execute, handle exceptions, release connection.
Hook (variant): the SQL string, parameter binding,
result mapping. Without Template Method: callers must
implement the invariant parts (connection lifecycle)
correctly. Every caller gets it slightly wrong.
JdbcTemplate centralises the invariant; callers provide
only the variant.

**Q3 (Design Trade-off):** You need to log method
calls on all service classes. You have three options:
(A) add logging to each method manually; (B) use
Decorator pattern; (C) use AOP (Proxy pattern). Apply
pattern recognition: what forces determine which
option to choose?

*Hint:_ Force: cross-cutting concern (logging across many
classes). Force: do not modify each class. Force: number
of classes. (A): violates DRY; maintenance burden.
(B) Decorator: add logging to specific classes; manual
wrapping. Forces: small number of classes; specific
behaviour. (C) AOP/Proxy: add logging to all matching
methods by convention; no manual wrapping. Forces:
logging needed across all service layer methods.
Forces drive the choice.
