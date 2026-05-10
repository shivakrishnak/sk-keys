---
id: DPT-003
title: Pattern vs Anti-Pattern vs Idiom
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
version: 2
layout: default
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 3
permalink: /dpt/pattern-vs-anti-pattern-vs-idiom/
---

# DPT-003 - Pattern vs Anti-Pattern vs Idiom

⚡ TL;DR - A pattern is a proven solution; an anti-pattern is a commonly used solution that causes more harm than good; an idiom is a language-specific low-level pattern — all three are named, recurring structures, but with opposite value judgements.

| DPT-003         | Category: Design Patterns | Difficulty: ★☆☆ |
| :-------------- | :------------------------ | :-------------- |
| **Depends on:** | DPT-001, DPT-002          |                 |
| **Used by:**    | DPT-004, DPT-005, DPT-042 |                 |
| **Related:**    | DPT-001, DPT-042, DPT-063 |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Engineers encounter a familiar-looking solution in code
review: "I've seen this before — is it good or bad?"
Without a taxonomy, every solution is evaluated from
scratch. "Looks like a pattern" and "is a pattern"
are conflated. Anti-patterns get cargo-culted because
they are recognisable, not because they are correct.

**THE BREAKING POINT:**
A team adopts Service Locator because it's in every
example they've found online. It looks like a pattern
(it solves a recurring problem). It's actually an
anti-pattern: it hides dependencies, makes testing
hard, and creates implicit coupling. The team spends
months debugging test interference before realising
the solution is the problem.

**THE INVENTION MOMENT:**
Andrew Koenig coined "anti-pattern" in 1995, inspired
by the GoF. William Brown et al. formalised it in
"AntiPatterns" (1998): a pattern that appears beneficial
but causes more harm than good when applied.
Kent Beck introduced "code smells" (1999) and "idioms"
as lower-level language-specific patterns.

**EVOLUTION:**
The taxonomy expanded: architectural patterns (high-level
structure), design patterns (class/object level), idioms
(language-specific), code smells (symptoms of anti-patterns).
Modern additions: dark patterns (UX anti-patterns),
cloud anti-patterns (lift-and-shift), security anti-patterns
(MD5 for passwords).

---

### 📘 Textbook Definition

**Pattern:** A proven, reusable solution to a recurring
problem; applying it produces a net positive.

**Anti-pattern:** A commonly used solution to a
recurring problem that causes more harm than good;
it looks like a pattern but has negative consequences
when applied. An anti-pattern entry describes the
problem, the bad solution, and the refactored solution.

**Idiom:** A low-level, language-specific solution to
a common problem in that language; not transferable
to other languages. Idioms use language features
naturally and efficiently.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Pattern = use this; anti-pattern = avoid this; idiom = do this in this specific language — all three are named recurring structures.

**One analogy:**

> Patterns, anti-patterns, and idioms are like cooking
> instructions marked "do this," "never do this,"
> and "in French cooking, do it this way." All three
> describe recurring techniques; the label tells you
> the value judgement and applicability.

**One insight:**
Anti-patterns were once patterns, or at least thought
to be. They were popularised before their consequences
were understood. This means today's patterns may
become tomorrow's anti-patterns as context changes.
Singleton was a GoF pattern; it is now widely considered
an anti-pattern in modern DI-centric architectures.

---

### 🔩 First Principles Explanation

**THREE-AXIS TAXONOMY:**

```
            +-------------------+
            |     RECURRING     |
            |     STRUCTURE     |
            +-------------------+
                    |
        +-----------+-----------+
        |                       |
   NET POSITIVE             NET NEGATIVE
        |                       |
    PATTERN               ANTI-PATTERN
        |
   LANGUAGE-SPECIFIC
        |
     IDIOM
```

**ANTI-PATTERN STRUCTURE (Brown et al. format):**

```
Anti-pattern entry requires:
1. Name            (e.g., God Object)
2. Also known as   (Blob, Monolith class)
3. Most frequent   (Java enterprise code)
   scale
4. Refactored      (Single Responsibility Principle;
   solution        Extract Class refactoring)
5. Root causes     (ignorance, sloth, haste)
6. Unbalanced      (conflicting forces that led
   forces          to the anti-pattern)
7. Evidence        (symptoms visible in code)
```

**THE KEY DIFFERENCE:**

```
Pattern:      Problem -> Solution -> Net positive
Anti-pattern: Problem -> Solution -> Net negative
              (solution appears to work short-term;
               consequences materialise long-term)

Example:
  God Object:
    Problem: many responsibilities needed in one place
    Solution: one class handles everything
    Short-term: simpler than splitting into many classes
    Long-term: untestable; unmodifiable; violates SRP
    -> Anti-pattern
```

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** A taxonomy distinguishing good and bad recurring solutions is necessary for systematic code quality.
**Accidental:** Memorising anti-pattern names without understanding the forces that make them harmful.

---

### 🧪 Thought Experiment

**SETUP:**
A team faces the problem: "how do our services find
other services they depend on?"

**SOLUTION A (Service Locator -- anti-pattern):**

```java
class OrderService {
  void placeOrder(Order o) {
    // Find dependency at runtime
    PaymentService ps =
      ServiceLocator.get(PaymentService.class);
    ps.charge(o.amount());
  }
}
// Looks like a pattern (solves dependency lookup)
// Anti-pattern consequences:
//   - PaymentService dependency is hidden (invisible
//     from constructor; only found by reading body)
//   - Testing: must configure ServiceLocator;
//     easy to forget; tests interfere
//   - Coupling: OrderService coupled to ServiceLocator
```

**SOLUTION B (Dependency Injection -- pattern):**

```java
class OrderService {
  private final PaymentService paymentService;
  // Dependency explicit in constructor
  OrderService(PaymentService ps) {
    this.paymentService = ps;
  }
  void placeOrder(Order o) {
    paymentService.charge(o.amount());
  }
}
// Dependencies visible; testable; no hidden coupling
```

**THE INSIGHT:**
Both solutions solve the same problem. One has negative
long-term consequences; one has positive consequences.
The taxonomy (pattern vs anti-pattern) captures the
value judgement.

---

### 🧠 Mental Model / Analogy

> Pattern/anti-pattern/idiom is a traffic light system
> for recurring code structures.
> Green (pattern): apply this; it has known positive consequences.
> Red (anti-pattern): avoid this; it has known negative consequences.
> Blue/contextual (idiom): in Python, do it this way;
> in Java, do it that way.
> The light doesn't change the structure; it tells
> you the value judgement.

**Element mapping:**

- Green = pattern
- Red = anti-pattern
- Blue = idiom (language-specific)
- Traffic rules = forces and consequences

Where this analogy breaks down: green/red are not
absolute — context matters. Singleton is red in
application code, green in a DI container implementation.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Patterns are solutions that work. Anti-patterns are
solutions that look like they work but cause problems.
Idioms are the natural way to write code in a
specific programming language.

**Level 2 - How to use it (junior developer):**
When reviewing code: is this a pattern (use it) or
an anti-pattern (refactor it)? Key anti-patterns to
learn: God Object, Spaghetti Code, Golden Hammer,
Service Locator, Lava Flow. Knowing the name lets
you name the problem in code review.

**Level 3 - How it works (mid-level engineer):**
Anti-pattern entries have "refactored solution"
column. When you identify an anti-pattern, the
catalogued refactored solution tells you how to fix
it. The anti-pattern taxonomy is a systematic
refactoring guide.

**Level 4 - Why it was designed this way (senior/staff):**
Anti-patterns exist because the forces that make them
appealing are real. God Object is tempting because
it reduces the cognitive overhead of finding
functionality. Service Locator is tempting because
it defers wiring decisions. The anti-pattern entry
explains which forces make the bad solution appealing;
understanding this lets you explain why to stop using
it convincingly, not just assert it.

**Expert Thinking Cues:**

- Ask "what are the long-term consequences?" when evaluating a recurring solution.
- Today's pattern can become tomorrow's anti-pattern as technology context shifts.
- Code smell = symptom of an anti-pattern; anti-pattern = the root cause.

---

### ⚙️ How It Works (Mechanism)

**Idiom examples across languages:**

```python
# Python idiom: list comprehension
# Anti-idiom:
evens = []
for i in range(10):
    if i % 2 == 0:
        evens.append(i)

# Pythonic idiom:
evens = [i for i in range(10) if i % 2 == 0]
```

```java
// Java idiom: try-with-resources
// Anti-idiom: manual resource management
try {
    Connection c = db.getConnection();
    // ... use c ...
} finally {
    if (c != null) c.close(); // easy to forget
}

// Java idiom (since Java 7):
try (Connection c = db.getConnection()) {
    // c auto-closed on exit
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Using the taxonomy in code review:**

```
Code review encounter:               <- YOU ARE HERE
  "I've seen this structure before"
  |
Classify:
  Does this solve a recurring problem? yes
  Is the solution proven net-positive? -> PATTERN
  Is the solution known net-negative? -> ANTI-PATTERN
  Is it language-specific shorthand? -> IDIOM
  |
For ANTI-PATTERN:
  -> Name it ("this is Service Locator")
  -> Reference the consequences ("hides dependencies")
  -> Provide refactored solution ("use DI instead")
  |
For PATTERN:
  -> Name it ("this is Strategy")
  -> Confirm forces match (multiple algorithms?)
  -> Confirm consequences are acceptable
  |
Document in review comment with pattern/anti-pattern name
```

---

### ⚖️ Comparison Table

| Concept               | Level        | Value    | Transferable?          | Examples                    |
| --------------------- | ------------ | -------- | ---------------------- | --------------------------- |
| Architectural pattern | System       | Positive | Yes                    | Layered, Event-driven       |
| Design pattern        | Class/object | Positive | Yes (OOP)              | Observer, Strategy          |
| Idiom                 | Line/method  | Positive | No (language-specific) | List comprehension (Python) |
| Anti-pattern          | Any          | Negative | Yes                    | God Object, Service Locator |
| Code smell            | Line/method  | Warning  | Yes                    | Long method, duplicate code |

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                              |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| "Anti-patterns are simply bad code"            | Anti-patterns are specifically recurring, named structures with documented negative consequences     |
| "A pattern is always good"                     | Patterns applied in wrong context are harmful; Singleton is a pattern that became an anti-pattern    |
| "Idioms are just style preferences"            | Idioms often have performance and readability implications; non-idiomatic code is harder to maintain |
| "Anti-patterns should be forbidden by linters" | Many anti-patterns require context to identify; automated tools catch code smells, not anti-patterns |
| "Code smells = anti-patterns"                  | Code smells are symptoms; anti-patterns are the diagnosed cause                                      |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Cargo-Culted Anti-Pattern**
**Symptom:** Service Locator used throughout codebase; tests fail intermittently; hard to understand which services exist.
**Root Cause:** Anti-pattern cargo-culted from examples without understanding the forces.
**Fix:** Identify all Service Locator usages; replace with constructor injection; let DI container wire dependencies.

**Mode 2: Pattern Turned Anti-Pattern (Context Shift)**
**Symptom:** Singleton used for DB connection pool; tests interfere; pool state persists between tests.
**Root Cause:** Singleton pattern applied to a context (test-heavy, multiple instances needed) where it causes harm.
**Fix:** Replace with DI-managed singleton scope; reset state between tests.

**Mode 3: Idiom Mismatch (Wrong Language Style)**
**Symptom:** Java developer writes Python in Java style; Python code with explicit type-tagged variable names, no comprehensions, no context managers.
**Root Cause:** Language idioms not learned; writing in language X using language Y mental model.
**Fix:** Read PEP 8 (Python); Effective Java (Java); learn the idiomatic patterns for each language.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[DPT-001 - What Are Design Patterns and Why They Exist]]
- [[DPT-002 - The Gang of Four -- Origin and Philosophy]]

**Builds On This (learn these next):**

- [[DPT-042 - Anti-Patterns Overview]]
- [[DPT-043 - God Object Anti-Pattern]]
- [[DPT-063 - Anti-Pattern Recognition and Refactoring]]

**Alternatives / Comparisons:**

- Code smells (symptoms vs the pattern itself)

---

### 📌 Quick Reference Card

```
+-----------------------------------------------------+
| WHAT IT IS      Taxonomy: pattern (good) vs         |
|                 anti-pattern (bad) vs idiom (lang)  |
| PROBLEM         Recurring structures without        |
| IT SOLVES       value classification; cargo-culting |
| KEY INSIGHT     Anti-patterns were once thought good|
|                 context shifts make patterns bad    |
| USE WHEN        Classifying recurring structures in |
|                 code review and design              |
| AVOID WHEN      Over-classifying; not every bad     |
|                 code is an anti-pattern             |
| TRADE-OFF       Vocabulary clarity vs taxonomic     |
|                 over-precision                      |
| ONE-LINER       Named good vs named bad solutions   |
| NEXT EXPLORE    DPT-042, DPT-043, DPT-063           |
+-----------------------------------------------------+
```

**If you remember only 3 things:**

1. Pattern = proven positive; anti-pattern = commonly used but net-negative; idiom = language-specific positive.
2. Anti-patterns are appealing because the short-term forces that make them attractive are real; understanding those forces explains why they spread.
3. Code smell = symptom; anti-pattern = diagnosis; refactored solution = cure.

**Interview one-liner:**
"A pattern is a proven solution; an anti-pattern is a commonly applied solution with net-negative consequences (short-term appealing, long-term harmful); an idiom is a language-specific low-level pattern; all three are recurring named structures but with different value judgements."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Every recurring practice needs a value label, not just
a name. Naming a practice without labelling its value
(positive or negative) leads to cargo-culting: teams
adopt it because it's recognisable, not because it's
good. This applies beyond code: management anti-patterns
(death march, heroic culture), security anti-patterns
(security-by-obscurity), DevOps anti-patterns (manual
approvals on every deploy).

**Where else this pattern appears:**

- **UX design** -- dark patterns (anti-patterns in UX: deceptive UI patterns) have their own catalogue
- **Security** -- OWASP Top 10 is a security anti-pattern catalogue with refactored solutions
- **Agile practice** -- "scrumfall" (anti-pattern: Scrum ceremonies with waterfall mindset) is a documented process anti-pattern

---

### 💡 The Surprising Truth

The term "anti-pattern" was coined before "refactoring"
became mainstream. When William Brown et al. published
"AntiPatterns" (1998), every anti-pattern entry included
a "refactored solution" section, essentially making
it a refactoring guide. The book anticipated
Martin Fowler's "Refactoring" (1999) by one year.
Anti-patterns and refactorings are two sides of the
same coin: anti-patterns name the problem; refactoring
catalogues name the transformation to fix it. The
best engineers know both: they recognise the pattern
and know the transformation.

---

### 🧠 Think About This Before We Continue

**Q1 (First Principles):** Singleton was a GoF pattern
in 1994 and is now widely considered an anti-pattern.
Apply the pattern/anti-pattern taxonomy formally: what
changed between 1994 and now that inverted the value
label?

*Hint:_ 1994 context: no DI containers; explicit global
access was the only way to share a single instance.
Forces for Singleton: controlled access to single
instance; saves initialisation cost. Modern context:
DI containers manage singleton scope without global
state. The forces changed: DI removes the need for
Singleton. The implementation's consequences
(global state, test interference) remained; the benefit
disappeared. Net value went negative -> anti-pattern.

**Q2 (System Interaction):** In Python, the "request"
object in Flask is a thread-local proxy -- accessible
globally as `flask.request`. Is this an implementation
of the Service Locator anti-pattern, an idiom, or a
pattern? Justify your answer.

*Hint:_ Flask's `request` is a thread-local, not a true
global. The forces are different from Service Locator:
the context (HTTP request handling) makes the thread-local
request a natural, safe idiom in that framework. Testing:
Flask provides `app.test_request_context()` to push a
test request context -- the testability anti-pattern
criticism of Service Locator is addressed. Verdict:
framework idiom, not anti-pattern in this specific context.

**Q3 (Design Trade-off):** A team writes Python code
using `class MyList(list): pass` and then `my_list = MyList()`
for a list that needs custom sorting. An idiom-aware
review suggests using composition instead (holding a
`list` internally). Analyse the forces: when is
inheritance from a built-in type an idiom vs an anti-pattern?

*Hint:_ Inheriting from `list` is a Python idiom for
extending list behaviour (IS-A relationship). Forces:
if the custom list adds methods and IS-A list (used
everywhere a list is used), inheritance is correct.
If it only needs custom sorting (HAS-A list, not IS-A),
composition is cleaner. The GoF principle applies:
inheritance for IS-A; composition for HAS-A.
