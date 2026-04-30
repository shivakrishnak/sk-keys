---
layout: default
title: "Refactoring"
parent: "Code Quality"
nav_order: 1121
permalink: /clean-code/refactoring/
number: "1121"
category: Code Quality
difficulty: ★★☆
depends_on: Technical Debt, Unit Tests, Code Smells, Cohesion, Coupling
used_by: Technical Debt, CI-CD Pipeline, Code Review, Clean Architecture
tags: #architecture, #pattern, #intermediate, #testing
---

# 1121 — Refactoring

`#architecture` `#pattern` `#intermediate` `#testing`

⚡ TL;DR — Restructuring existing code to improve its internal design without changing its observable external behaviour — each transformation is small, safe, and backed by a green test suite.

| #1121 | category: Code Quality
|:---|:---|:---|
| **Depends on:** | Technical Debt, Unit Tests, Code Smells, Cohesion, Coupling | |
| **Used by:** | Technical Debt, CI-CD Pipeline, Code Review, Clean Architecture | |

---

### 📘 Textbook Definition

**Refactoring** (Martin Fowler, 1999) is the disciplined technique of restructuring existing code by applying a series of small, behaviour-preserving transformations called **refactorings**, each of which leaves the external observable behaviour identical while improving the internal structure. The cardinal rule: all tests remain green after every individual refactoring step. Refactoring is distinct from rewriting (changing observable behaviour), performance optimisation (changing resource usage), and bug fixing (changing incorrect behaviour). The catalogue of named refactorings (Extract Method, Move Method, Rename Variable, Replace Conditional with Polymorphism) transforms code systematically and safely.

---

### 🟢 Simple Definition (Easy)

Refactoring is tidying up code that works. You don't change what it does — you improve how it does it. Like reorganising a messy desk drawers without throwing anything away.

---

### 🔵 Simple Definition (Elaborated)

Refactoring is the ongoing activity of improving code structure as you work. After making something work, you make it clean. The discipline: do it in tiny, safe steps with tests passing after each one — not in one giant risky rewrite. The most important tools are named refactorings (Extract Method, Rename Variable, Introduce Parameter Object) — each has a clear recipe that transforms code safely. IDEs automate many of them. Without refactoring, code accumulates design problems until they're too expensive to fix — that's how technical debt compounds into an unworkable system.

---

### 🔩 First Principles Explanation

**The two-hat model (Kent Beck):**

```
Adding functionality:
  → You may add code
  → You do NOT restructure existing code
  → One "hat" at a time

Refactoring:
  → You restructure existing code
  → You do NOT add functionality
  → Tests are ALWAYS green

Never wear both hats at once.
If both mixed: "Am I done? Did I break anything?
               Did I add more than I intended?"
→ confusion, bugs, untestable progress
```

**The rhythm of software development:**

```
┌─────────────────────────────────────────────┐
│  RED-GREEN-REFACTOR CYCLE (TDD rhythm)      │
│                                             │
│  1. RED: Write failing test for new feature │
│  2. GREEN: Write simplest code to pass test │
│            (may be ugly/naive)              │
│  3. REFACTOR: Clean up code                 │
│               Tests still green throughout  │
│  4. Repeat                                  │
│                                             │
│  Refactoring = step 3; happens every cycle  │
│  Not a big-bang activity, a daily habit     │
└─────────────────────────────────────────────┘
```

**Why tests are the prerequisite:**

Refactoring without tests is just editing. You have no safety net — you can't know you haven't broken anything. The test suite is the behaviour specification that makes refactoring safe.

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT refactoring:**

```
Without ongoing refactoring:

  Cycle 1: Feature A written quickly
  Cycle 5: Feature E needed, but A, B, C, D are messy
    → takes 3× as long as Cycle 1
  
  Cycle 20: Codebase is "legacy" — feared, untouched
    → new features layered on top of messiness
    → "working" code nobody dares change
    → every change breaks something unrelated

  Developers report:
  "I'm spending 70% of time understanding existing code"
  "I'm afraid to touch that class"
  "We can't ship because of these bugs"
  All symptoms of insufficient refactoring
```

**WITH ongoing refactoring:**

```
→ Code stays clean sprint to sprint
→ Adding new features doesn't get progressively harder
→ Debt is paid down as it's created
→ Engineers understand the codebase fully
→ Onboarding is fast — code is readable
→ Velocity stays stable or improves over time
```

---

### 🧠 Mental Model / Analogy

> Refactoring is like **editing a book**. Writing a first draft is getting the ideas down — it's messy, but it exists. Editing improves clarity, structure, and flow without changing the story. You wouldn't publish the first draft; you wouldn't write the book backwards either — edit as you go, chapter by chapter. Code is the same: the first version that works is a draft. Refactoring is the editing pass that makes it publishable.

"First draft" = working but messy code
"Editing" = refactoring — improve structure, not story
"Published book" = clean, maintainable production code
"Never changing the story" = external behaviour unchanged
"Edit as you go" = continuous refactoring, not big-bang cleanup

---

### ⚙️ How It Works (Mechanism)

**The refactoring catalogue — key examples:**

```
┌──────────────────────────────────────────────────────┐
│  NAMED REFACTORINGS (Fowler's catalogue)             │
├──────────────────────────────────────────────────────┤
│  Extract Method   → pull code into named method      │
│  Extract Class    → split low-cohesion class         │
│  Move Method      → method belongs on another class  │
│  Rename Variable  → express intent in name           │
│  Introduce Parameter Object → replace long param list│
│  Replace Conditional with Polymorphism               │
│              → eliminate instanceof chains           │
│  Inline Method    → remove unnecessary indirection   │
│  Introduce Null Object → remove null checks          │
│  Decompose Conditional → extract complex if branches │
└──────────────────────────────────────────────────────┘
```

**Mechanics of a safe refactoring:**

```
1. Ensure tests are green (mandatory starting point)
2. Apply ONE refactoring step (smallest possible)
3. Run tests → must be green
4. Commit (optional but recommended at each step)
5. Repeat for next refactoring
```

**Code smells that indicate refactoring needs:**

```
Long Method       → Extract Method
Large Class       → Extract Class
Duplicate Code    → Extract + DRY
Long Param List   → Introduce Param Object
Feature Envy      → Move Method to the object it uses
Data Clumps       → Extract Class for the cluster
Switch by type    → Replace Conditional with Polymorphism
Dead Code         → Delete It
```

---

### 🔄 How It Connects (Mini-Map)

```
Code Smells (detected)
        ↓
  REFACTORING  ← you are here
  (small, safe, behaviour-preserving steps)
  ↑ requires: test suite (safety net)
  ↑ addresses: Technical Debt
        ↓
  Catalogue:
  Extract Method, Extract Class, Move Method,
  Rename, Replace Conditional, Introduce PO
        ↓
  IDE Support: IntelliJ, VS Code automate
  many refactorings safely
        ↓
  Result: Higher Cohesion, Lower Coupling,
          Paid Technical Debt
```

---

### 💻 Code Example

**Example 1 — Extract Method:**

```java
// BEFORE: Long method, hard to understand purpose
void printOwing(double amount) {
  // print banner
  System.out.println("*****");
  System.out.println("** Customer Owes **");
  System.out.println("*****");

  // calculate outstanding
  double outstanding = 0.0;
  for (Order o : orders) outstanding += o.getAmount();

  // print details
  System.out.println("name: " + name);
  System.out.println("amount: " + outstanding);
}

// AFTER: Extract Method — three clear purposes
void printOwing(double amount) {
  printBanner();
  double outstanding = calculateOutstanding();
  printDetails(outstanding);
}

void printBanner() {
  System.out.println("*****");
  System.out.println("** Customer Owes **");
  System.out.println("*****");
}

double calculateOutstanding() {
  return orders.stream().mapToDouble(Order::getAmount).sum();
}

void printDetails(double outstanding) {
  System.out.println("name: " + name);
  System.out.println("amount: " + outstanding);
}
```

**Example 2 — Replace Conditional with Polymorphism:**

```java
// BEFORE: type-based switch (code smell: switch by type)
double getSpeed() {
  switch (type) {
    case EUROPEAN: return baseSpeed();
    case AFRICAN:  return baseSpeed() - loadFactor() * 3;
    case NORWEGIAN_BLUE: return isNailed ? 0 : baseSpeed();
  }
  throw new RuntimeException("Unknown type");
}

// AFTER: polymorphic dispatch
// Step 1: Create abstract base + subclasses
abstract class Bird {
  abstract double getSpeed();
  double baseSpeed() { return 10.0; }
}
class EuropeanBird extends Bird {
  double getSpeed() { return baseSpeed(); }
}
class AfricanBird extends Bird {
  double getSpeed() { return baseSpeed() - loadFactor() * 3; }
}
class NorwegianBlue extends Bird {
  double getSpeed() { return isNailed ? 0 : baseSpeed(); }
}
// Caller: bird.getSpeed() — no switch, extensible
```

**Example 3 — Safe refactoring with IntelliJ:**

```
IntelliJ IDEA refactoring shortcuts:
  Rename:               Shift+F6
  Extract Method:       Ctrl+Alt+M
  Extract Variable:     Ctrl+Alt+V
  Extract Constant:     Ctrl+Alt+C
  Inline:               Ctrl+Alt+N
  Move:                 F6
  Introduce Parameter:  Ctrl+Alt+P
  Extract Interface:    (Refactor menu)

Rule: Use IDE refactoring over manual edits
→ IDE updates ALL references automatically
→ No missed usages
→ Tests still green by construction
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Refactoring means rewriting | Refactoring preserves external behaviour. Rewriting changes it. You must never break a passing test during a refactoring |
| You refactor when you have time | Refactoring is part of the development cycle, not a separate activity. "When you have time" means never |
| Refactoring without tests is fine | Without tests you can't verify behaviour is preserved. Untested refactoring is just risky editing |
| Big-bang rewrites are better than incremental refactoring | The "second-system effect" and "Big Rewrite" are well-documented failure modes. Incremental refactoring with continuous delivery is vastly safer |
| Refactoring is only about clean code aesthetics | Refactoring directly reduces technical debt — it has measurable business impact on velocity and bug rates |

---

### 🔥 Pitfalls in Production

**1. Refactoring and adding features simultaneously**

```java
// DANGER: mixed refactoring + feature addition
// In one commit: renamed method + added new parameter
// + changed return type + added new field

// If this breaks: impossible to tell if refactoring
// or feature change caused the problem

// GOOD: strict separation in commits
// Commit 1: rename method (tests green)
// Commit 2: extract class (tests green)
// Commit 3: add new feature (on clean foundation)
// Small commits + CI → each step verified
```

**2. Refactoring public APIs without deprecation strategy**

```java
// BAD: refactoring internal + public API in one step
// Old: getUserData(long id)
// New: findUserById(long id) — simple rename internally

// If other services call getUserData:
// → breaking change deployed without warning

// GOOD: Expand-Contract (Parallel Change) pattern
// Step 1: Add new method, keep old
public User findUserById(long id) { ... } // new
@Deprecated
public User getUserData(long id) {         // kept for compat
  return findUserById(id);
}
// Step 2: Update all callers to new method
// Step 3 (next sprint): Remove deprecated method
```

**3. Breaking tests "to make them pass" during refactoring**

```java
// DANGEROUS: refactoring broke tests → edited the tests
// to match new behaviour
// "The tests were testing implementation details anyway"

// The red flag: if tests break during refactoring,
// either:
// a) The refactoring changed behaviour (revert!)
// b) Tests were testing implementation, not behaviour
//    (fix by rewriting the tests to test behaviour)
// c) You are also bug-fixing (two hats → stop)
```

---

### 🔗 Related Keywords

- `Technical Debt` — refactoring is the primary mechanism for paying down technical debt
- `Code Smells` — Long Method, Large Class, Feature Envy are the signals that trigger refactoring
- `Unit Tests` — the prerequisite safety net without which refactoring is just risky editing
- `Cohesion` — Extract Class is the key refactoring to improve cohesion
- `Coupling` — Move Method and Introduce Interface are the key refactorings to reduce coupling
- `Boy Scout Rule` — "leave the code better than you found it" — continuous micro-refactoring

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Improve design without changing behaviour;│
│              │ small steps, tests green after each step  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ After making something work (Red-Green-   │
│              │ Refactor); before adding to messy code    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ No test coverage — add tests first;       │
│              │ never refactor + add feature simultaneously│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Make it work. Make it right.             │
│              │  Make it fast. In that order."            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Code Smells → TDD → Boy Scout Rule        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Michael Feathers' book "Working Effectively with Legacy Code" defines legacy code as "code without tests." Before you can safely refactor a large legacy method, you need coverage, but the method is so entangled it's hard to test without running the entire application. Describe the sequence of techniques Feathers recommends for putting a legacy method "under test" — specifically: characterisation tests, seams, and the Sprout Method pattern — and explain why these techniques are themselves forms of refactoring even though they add tests.

**Q2.** Martin Fowler's "Expand and Contract" (Parallel Change) pattern is used to refactor across service boundaries without downtime. Describe the full three-phase lifecycle for renaming a REST API field from `user_id` to `userId` across a consumer-producer service pair — including exactly what the producer and consumer JSON look like in each phase, how long each phase must run before the next begins, and what contract test (e.g. a Pact test) would automatically detect a premature field removal.

