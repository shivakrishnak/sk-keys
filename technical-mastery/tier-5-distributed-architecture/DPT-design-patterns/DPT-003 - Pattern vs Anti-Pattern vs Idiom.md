---
id: DPT-003
title: Pattern vs Anti-Pattern vs Idiom
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★☆☆
depends_on: DPT-001, DPT-002
used_by: DPT-004, DPT-042
related: DPT-001, DPT-004, DPT-042
tags:
  - pattern
  - antipattern
  - foundational
  - mental-model
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 3
permalink: /technical-mastery/design-patterns/pattern-vs-anti-pattern-vs-idiom/
---

⚡ TL;DR - A pattern solves a recurring problem well, an anti-pattern
solves it badly in a named, recognizable way, and an idiom expresses
the same intent using a language's native features.

| #3 | Category: Design Patterns | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-002 | |
| **Used by:** | DPT-004, DPT-042 | |
| **Related:** | DPT-001, DPT-004, DPT-042 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A senior engineer reviews a pull request. They see a God Object -
a single class with 2,000 lines that handles authentication, caching,
database access, and business rules. They want to communicate this
is a well-known, named problem. But without vocabulary, they write
a long PR comment explaining that the class has too many
responsibilities, violates SRP, and should be decomposed - without
being able to point to the category of mistake. The author receives
the critique as personal and subjective, not structural and
categorical.

**THE BREAKING POINT:**
Engineering critique without shared vocabulary sounds like opinion.
"Your class is too big" invites debate. "This is the God Object
anti-pattern" does not invite debate - it names a documented
failure mode with known consequences and known remediation. Without
the three-way vocabulary (pattern / anti-pattern / idiom), every
design critique requires a full argument instead of a citation.

**THE INVENTION MOMENT:**
This is exactly why distinguishing patterns, anti-patterns, and
idioms matters: the vocabulary gives precise labels to three
fundamentally different design outcomes, enabling critique that
is precise, categorical, and defensible instead of subjective.

**EVOLUTION:**
The term "anti-pattern" was coined by Andrew Koenig in a 1995
article in the Journal of Object-Oriented Programming, adapting
the pattern concept to describe solutions that reliably cause
harm. The definitive catalog was published by Brown, Malveau,
McCormick, and Mowbray in "AntiPatterns: Refactoring Software,
Architectures, and Projects in Crisis" (1998). The term "idiom"
was formalised as the lowest level of pattern abstraction by
Wolfgang Pree (1994) and is included in the GoF's pattern
classification framework as language-specific implementation
patterns.

---

### 📘 Textbook Definition

A **pattern** is a named, context-independent solution template
for a recurring structural design problem - proven through
known uses in multiple independent systems, with documented
intent, applicability, and consequences.

An **anti-pattern** is a named, commonly applied solution that
appears to address a recurring problem but reliably produces
negative consequences - documented to enable recognition and
refactoring, with known refactoring paths to correct solutions.

An **idiom** is a language-specific, low-level implementation
pattern that expresses a general design intent using a particular
programming language's native features and conventions. Idioms
are not portable across languages; patterns and anti-patterns
are language-independent.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Pattern = the right solution, anti-pattern = the wrong solution
with a name, idiom = the right solution expressed in your
language's native way.

**One analogy:**
> In cooking: a recipe is a pattern (a proven method for chocolate
> cake). An anti-pattern is "adding salt when you mean sugar" -
> a named mistake that is easy to make, recognisable when seen,
> and has a known fix. An idiom is how a French chef executes
> the same chocolate cake using French technique - same intent,
> different native expression.

**One insight:**
The most important of the three is the anti-pattern vocabulary.
Patterns tell you what to DO. Anti-patterns tell you what to
STOP - and recognising a named failure mode in someone else's
code (or your own) without having to re-argue the case from
first principles is a high-leverage engineering skill.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. All three concepts address recurring situations - the situation
   type is not what distinguishes them. What distinguishes them
   is OUTCOME: patterns produce reliably positive outcomes,
   anti-patterns produce reliably negative outcomes, idioms are
   neutral implementation choices within a specific language.
2. Anti-patterns are NOT simply bad code. A specific structural
   shape must recur across multiple independent codebases for it
   to be catalogued as an anti-pattern. Random messiness is not
   a pattern or an anti-pattern - it is just mess.
3. Idioms are portable within a language version, not across
   languages. The Java-idiomatic way to express Strategy (lambda
   with a functional interface) is an idiom; it does not apply
   to Java 7 or to C++.

**DERIVED DESIGN:**
The three-way classification creates a complete taxonomy for
categorising any named design element:
- Does it solve the problem well? - Pattern
- Does it appear to solve the problem but cause harm? - Anti-pattern
- Is it a language-specific expression of a pattern? - Idiom

**THE TRADE-OFFS:**

**Gain:** Precise vocabulary enables faster, less contentious
design critique and architectural communication.

**Cost:** The vocabulary must be shared; using "anti-pattern" with
engineers who do not know the catalog invites the explanation
that shared vocabulary was supposed to avoid.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Distinguishing good solutions from harmful ones is
a genuine intellectual problem that no tool automates. It requires
judgment, context, and pattern recognition.

**Accidental:** Much of what engineers call "anti-patterns" in
day-to-day use are actually local team conventions or personal
preferences, not catalogued, empirically-validated failure modes.
The precision the vocabulary promises is only delivered when it
is used rigorously.

---

### 🧪 Thought Experiment

**SETUP:**
Three engineers discuss the same codebase problem: a single
`OrderService` class that is 3,000 lines long and handles
authentication, inventory checking, payment processing, order
persistence, and email notification.

**WHAT HAPPENS WITHOUT THE VOCABULARY:**
Engineer A says: "This class is too big." Engineer B says: "It's
not that big, I've seen bigger." Engineer C says: "It works, why
change it?" The debate is about size (subjective) instead of
structure (objective). The discussion goes 45 minutes with no
resolution because there is no shared reference.

**WHAT HAPPENS WITH THE VOCABULARY:**
Engineer A says: "This is the God Object anti-pattern. The
documented refactoring is decomposition into SRP-aligned
services: AuthService, InventoryService, PaymentService,
OrderRepository, NotificationService." Engineers B and C can
look up the anti-pattern. The documented consequences (untestable
code, merge conflicts, hidden coupling) match what the team
experiences. The debate becomes: "How do we decompose it?" -
not "Is it a problem?"

**THE INSIGHT:**
Naming the failure mode shifts the debate from opinion to
documentation. The vocabulary is a citation tool - it moves
engineering critique from personal to institutional.

---

### 🧠 Mental Model / Analogy

> In law, the distinction between pattern, anti-pattern, and
> idiom maps to precedent, legal trap, and jurisdiction-specific
> procedure. A precedent (pattern) is a proven approach validated
> by courts. A legal trap (anti-pattern) is a commonly attempted
> approach that reliably fails - named by lawyers so juniors
> avoid it. A jurisdiction-specific procedure (idiom) is the
> correct way to file in this specific court, which differs from
> other courts but achieves the same end.

- "Precedent" - design pattern (proven, transferable)
- "Legal trap" - anti-pattern (common, named, harmful)
- "Jurisdiction procedure" - idiom (local, effective, not portable)
- "Citing precedent in a brief" - saying "this is Observer" in a PR
- "Warning a junior" - saying "this is God Object" in a review

**Where this analogy breaks down:** Legal precedent is binding.
Design patterns are advisory. An engineer can choose not to follow
a pattern; a lawyer cannot choose to ignore binding precedent.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
In design vocabulary, a pattern is the right way to solve a
recurring problem. An anti-pattern is a wrong way that looks right
until the consequences arrive. An idiom is the way your specific
programming language natively expresses a design concept.

**Level 2 - How to use it (junior developer):**
When you recognise a structural solution, ask: is this a named
pattern? Look it up. When you identify something harmful in a
codebase, ask: is this a named anti-pattern? Naming it gives you
a citation in code review. When implementing a pattern in a
specific language, look for the idiomatic expression first - do
not copy-paste Java class hierarchies into Python.

**Level 3 - How it works (mid-level engineer):**
The practical power is in anti-patterns. Pattern recognition tells
you what to build. Anti-pattern recognition tells you what to
stop building and how to refactor it. The anti-pattern catalog
(Spaghetti Code, God Object, Golden Hammer, Lava Flow, Boat
Anchor) maps harmful structures to documented refactoring paths.
Recognising an anti-pattern in a PR saves hours of bespoke
critique per review.

**Level 4 - Why it was designed this way (senior/staff):**
The distinction between anti-pattern and bad code is subtle but
critical. Bad code is a local accident. An anti-pattern is a
structural failure mode that recurs across independent teams -
it has enough gravity to pull engineers toward it repeatedly.
God Object is an anti-pattern not because large classes are bad
(that is a code smell) but because the specific structural
pattern - a single class accumulating all system responsibility -
appears independently in team after team, under pressure, with
predictable consequences. The recurrence and predictability are
what justify the name.

**Level 5 - Mastery (distinguished engineer):**
A staff engineer uses all three categories simultaneously in
architecture review. They identify which structural patterns are
in use, which anti-patterns are emerging (often under deadline
pressure or with legacy constraints), and which idioms are
appropriate for the team's language version. They also recognise
when a pattern is being applied as an anti-pattern: a Singleton
used for mutable global state is a Singleton (structural pattern)
applied in a way that produces anti-pattern consequences. The
line between pattern and anti-pattern is not always the structure
- it is the context and the consequence.

---

### ⚙️ Why It Holds True (Formal Basis)

The three-way classification holds because it reflects three
genuinely distinct categories of recurring design element:

**1. Positive Recurrence (Pattern)**
A pattern is validated by Known Uses: the same structure appears
independently in two or more unrelated systems with positive
outcomes. The recurrence is the evidence. Without recurrence,
there is no pattern - just a solution.

**2. Negative Recurrence (Anti-Pattern)**
An anti-pattern is validated by the same criterion but with
negative outcomes: the same structure appears independently in
multiple systems, and its consequences are reliably harmful.
The recurrence of harm is the evidence. "God Object" qualifies
because it appears in virtually every large Java codebase under
deadline pressure - independently, without instruction, with
predictable consequences.

**3. Language Specificity (Idiom)**
An idiom cannot exist at the language-independent level because
it is defined by a specific language's native constructs.
The Java idiom for Strategy is a lambda with a functional
interface. The Python idiom for the same intent is a callable.
These are not the same implementation, but they express the
same pattern intent. Language-specific expression is the
defining property.

**What violating the distinction produces:**
Calling everything a "pattern" dilutes the vocabulary and
invites the same re-argument from first principles that shared
vocabulary was supposed to prevent. Calling idiomatic code
"a pattern" conflates intent with implementation. The precision
of the three-way distinction is what makes the vocabulary useful.

---

### 🔄 System Design Implications

The three-way classification applies at every level of the
system design stack:

| Level        | Pattern Example     | Anti-Pattern Example    | Idiom Example           |
| ------------ | ------------------- | ----------------------- | ----------------------- |
| Class        | Observer            | God Object              | Java lambda as Strategy |
| Module       | Repository Pattern  | Shotgun Surgery         | Python context manager  |
| Service      | Circuit Breaker     | Distributed Monolith    | AWS Lambda per event    |
| Architecture | Event Sourcing      | Big Ball of Mud         | Kubernetes Helm chart   |

**What changes at scale:**
Anti-patterns become more harmful at scale, not less. A God Object
in a solo project is manageable. A God Service in a 50-engineer
microservices architecture - a single service that has accumulated
all business logic - produces merge conflicts, deployment
bottlenecks, and testing failures that compound with team size.
The anti-pattern vocabulary must be applied at the system level,
not just the class level.

**What engineers ignore and what breaks:**
Most engineers learn anti-patterns at the class level (God Object,
Spaghetti Code) but do not apply the vocabulary at the system level
(Distributed Monolith, Chatty Service, Shared Database).
The most expensive anti-patterns in modern systems are
architectural, not class-level.

---

### 💻 Code Example

**Example 1 - Recognising a Pattern:**

```java
// This IS a Strategy pattern - recognisable by:
// 1. An interface defining the algorithm contract
// 2. Multiple concrete implementations
// 3. The algorithm injected, not hardcoded

interface PricingStrategy {
    BigDecimal calculate(Order order);
}
// Concrete strategies: StandardPricing, VIPPricing, PromoPricing
// Context: CheckoutService receives strategy via constructor
```

**Example 2 - Recognising an Anti-Pattern:**

```java
// BAD: This is God Object anti-pattern
// Single class with 5 unrelated responsibilities
class OrderService {
    // Authentication
    public boolean authenticate(String token) { ... }
    // Inventory
    public boolean checkStock(String sku) { ... }
    // Payment
    public boolean chargeCard(CreditCard card) { ... }
    // Persistence
    public void saveOrder(Order order) { ... }
    // Notification
    public void sendConfirmationEmail(Order order) { ... }
}

// GOOD: Decomposed to SRP-aligned classes
class AuthService       { boolean authenticate(String t){..} }
class InventoryService  { boolean checkStock(String s)  {...} }
class PaymentService    { boolean charge(CreditCard c)  {...} }
class OrderRepository   { void save(Order o)            {...} }
class NotificationService{ void sendConfirmEmail(Order o){..} }
```

**Example 3 - Recognising an Idiom (Java 8+):**

```java
// IDIOM: Java 8+ expresses Strategy intent with a lambda
// Same intent as the full Strategy class hierarchy,
// no interface or concrete class required

// Java 7 - full Strategy pattern ceremony
Comparator<Order> byTotal = new Comparator<Order>() {
    @Override
    public int compare(Order a, Order b) {
        return a.getTotal().compareTo(b.getTotal());
    }
};

// Java 8 idiom - lambda IS the strategy
Comparator<Order> byTotal = (a, b) ->
    a.getTotal().compareTo(b.getTotal());
// The vocabulary "Strategy" still applies - the idiom
// is the language-native expression of the same intent
```

---

### ⚖️ Comparison Table

| Concept      | Outcome   | Portability  | Validated By        | Action       |
| ------------ | --------- | ------------ | ------------------- | ------------ |
| **Pattern**  | Positive  | Language-ind.| Known Uses (2+)     | Apply it     |
| Anti-Pattern | Negative  | Language-ind.| Known Harm (2+)     | Refactor it  |
| Idiom        | Positive  | Language-dep.| Community consensus | Use natively |
| Code smell   | Negative  | Language-dep.| Heuristic           | Investigate  |
| Bad code     | Negative  | N/A          | Local accident      | Fix it       |

**How to choose what term to use:** If a named catalog entry
exists - use that name. If no catalog entry exists, use "code
smell" for a suspicious local pattern and "bad code" for an
obvious local mistake. Reserve "anti-pattern" for catalogued,
recurring, named failure modes.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Anti-pattern" means any bad code | Anti-pattern is a catalogued, recurring, named failure mode; not every bad code choice is an anti-pattern |
| Idioms are just code style preferences | Idioms are language-canonical expressions of design intent; ignoring them produces correct but unidiomatic code that confuses native readers |
| A pattern used in the wrong context is still a pattern | A pattern applied where it causes net harm has become an anti-pattern in that context - context determines the category |
| Patterns and anti-patterns only apply to class-level code | Both exist at every level: class, module, service, architecture, organisation |
| If it has a name, it must be a pattern | Names can be applied to anti-patterns and idioms too; the name does not determine the category - the outcome does |

---

### 🚨 Failure Modes & Diagnosis

**Using "Anti-Pattern" as a Synonym for "Bad Code"**

**Symptom:**
Code review comments say "this is an anti-pattern" for any code
the reviewer dislikes, without citing a named catalog entry or
explaining which anti-pattern is meant.

**Root Cause:**
"Anti-pattern" has become a pejorative in some teams, losing its
precision. Engineers use it to mean "I don't like this" rather
than "this matches a documented failure mode."

**Diagnostic Signal:**
Ask the reviewer: "Which anti-pattern? Is it in the catalog?"
If the answer is "well it's just bad" or naming a non-catalogued
pattern, the vocabulary is being misused.

**Fix:**
Establish a team norm: "anti-pattern" requires a citation - a
catalog name or a reference. Without a citation, use "code smell"
for a heuristic concern or name the specific technical problem
(tight coupling, hidden dependency, etc.).

**Prevention:**
Include the precise distinction in team engineering principles.
Reserve "anti-pattern" for catalogued entries: God Object,
Spaghetti Code, Golden Hammer, Boat Anchor, Lava Flow.

---

**Applying a GoF Pattern Where an Idiom Suffices**

**Symptom:**
A Java 17 codebase has full Strategy interface hierarchies -
single-method interface + multiple implementing classes - for
cases that a lambda expression handles completely.

**Root Cause:**
Engineers learned GoF in an older Java version and did not
update their implementation vocabulary when lambdas became
available. The pattern intent is correct; the ceremony is
unnecessary.

**Diagnostic Signal:**
Search for single-abstract-method interfaces (SAM interfaces)
in the codebase. If they have only one or two implementations
and the implementations contain only a lambda-expressible body,
the full class hierarchy is a Java-7-era idiom applied in a
Java-17 codebase.

**Fix:**
Replace SAM interface + implementing class with a functional
interface + lambda where the interface has no additional API.
Document the pattern name in a comment to preserve vocabulary.

**Prevention:**
Conduct an annual "idiom review" when the team's language version
upgrades: identify which GoF implementation patterns have become
language idioms in the new version.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `What Are Design Patterns and Why They Exist` - the foundational
  motivation for the entire three-way vocabulary
- `The Gang of Four - Origin and Philosophy` - the catalog that
  defines which patterns are GoF-canonical

**Builds On This (learn these next):**
- `How to Recognize When a Pattern Applies` - the decision
  framework for identifying which category a design element
  belongs to in a specific context
- `Anti-Patterns Overview` - the anti-pattern catalog: named
  failure modes with refactoring paths

**Alternatives / Comparisons:**
- `Code Smell` - a heuristic signal that a design problem may
  exist, without the recurrence validation that makes something
  a catalogued anti-pattern; less precise, earlier warning
- `SOLID Principles` - design principles that, when violated,
  often produce catalogued anti-patterns (SRP violation produces
  God Object, OCP violation produces shotgun surgery)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Three-way vocabulary: pattern (good),    │
│              │ anti-pattern (named bad), idiom (local)  │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ "Bad code" is subjective; named failure  │
│ SOLVES       │ modes enable objective, citable critique │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ Anti-pattern is NOT bad code - it is a  │
│              │ RECURRING bad solution that needs a name │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Critiquing a structural design decision  │
│              │ in code review or architecture discussion│
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ Using "anti-pattern" for any code you    │
│              │ dislike without a catalog citation       │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Calling every bad code choice an         │
│              │ "anti-pattern" - dilutes the vocabulary  │
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Precision of citation vs cost of         │
│              │ teaching the vocabulary to the team      │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Pattern = right, anti-pattern = named   │
│              │  wrong, idiom = language-right"          │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Anti-Patterns Overview → God Object →   │
│              │ How to Recognize When a Pattern Applies  │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Anti-pattern is NOT bad code - it is a catalogued, recurring,
   named failure mode; without recurrence across independent
   teams, it is just a local mistake
2. Idioms are language-specific; patterns are language-independent;
   the same pattern intent can be expressed as different idioms
   in different languages
3. Using "anti-pattern" without a catalog citation is the
   vocabulary equivalent of an anti-pattern: looks like precision,
   does not deliver it

**Interview one-liner:**
"A pattern is a named recurring solution with positive outcomes,
an anti-pattern is a named recurring solution with documented
negative outcomes, and an idiom is a language-specific
implementation of a pattern intent. The distinctions matter
because they enable precise, citable design critique rather than
subjective opinion."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Naming failure modes is as valuable as naming success modes.
In any field where the same mistakes recur across practitioners,
cataloguing and naming those mistakes converts individual hard
experience into collective preventable knowledge. The anti-pattern
catalog is a curriculum of expensive lessons paid once.

**Where else this pattern appears:**
- **Aviation** - The NTSB accident report system names failure
  patterns (controlled flight into terrain, loss of situational
  awareness) so that new pilots learn from past accidents;
  the recurring name is the learning vehicle
- **Finance** - Behavioral economics names cognitive biases
  (anchoring, loss aversion, recency bias) as anti-patterns
  in investor decision-making; naming makes them avoidable
- **Medicine** - Diagnostic errors are categorised by type
  (premature closure, anchoring, availability heuristic) rather
  than treated as random mistakes; the taxonomy enables
  systematic prevention

**Industry applications:**
- **Enterprise architecture** - Anti-pattern vocabulary (Big Ball
  of Mud, Distributed Monolith, Chatty Service) is used in
  architecture reviews to quickly identify and document systemic
  failure modes in large codebases
- **Code review culture** - Teams that use anti-pattern vocabulary
  in reviews produce less contentious feedback; "God Object" is a
  technical observation, not a personal criticism

---

### 💡 The Surprising Truth

The concept of "anti-pattern" was created accidentally. Andrew
Koenig invented the term in 1995 while writing a magazine column
about common OOP mistakes. He borrowed the prefix from "anti" +
"pattern" as a rhetorical device, not expecting the term to be
taken seriously. The full anti-pattern catalog (Brown et al. 1998)
took the offhand term and turned it into a rigorous methodology
with the same validation requirements as the GoF catalog: known
uses (of the failure mode), refactored solution, and documented
consequences. A term invented as a throwaway rhetorical device
became a 300-page book that shaped how the industry talks about
failure. The lesson: naming something well enough makes it real.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [EXPLAIN] Explain to a non-technical colleague why distinguishing
   "anti-pattern" from "bad code" matters for team communication,
   using one concrete example from a code review context
2. [DEBUG] Given a code review comment that uses "anti-pattern"
   without a citation, identify that it is using the term
   imprecisely and rewrite the comment with either a catalog
   citation or the more appropriate term "code smell"
3. [DECIDE] Given a specific structural problem in three different
   languages (Java, Python, Kotlin), identify which solution is
   a pattern, which is an idiom, and explain why the same intent
   produces different category labels across languages
4. [BUILD] For the God Object anti-pattern, write a one-paragraph
   refactoring prescription: what to decompose, on what criterion
   (SRP), to what target structure, in what order
5. [EXTEND] Apply the pattern/anti-pattern/idiom vocabulary to a
   non-OOP domain - for example, infrastructure as code, SQL
   query design, or API design - and name one pattern, one
   anti-pattern, and one idiom in that domain

---

### 🧠 Think About This Before We Continue

**Q1.** The God Object anti-pattern was first catalogued in 1998
for object-oriented code. Today, in microservices architectures,
teams create "God Services" - a single service that accumulates
all business logic under deadline pressure. Is a God Service
the same anti-pattern at a different abstraction level, or is it
a different anti-pattern with different causes and consequences?
What evidence would help you decide?

*Hint: Compare the root cause (deadline pressure, lack of
ownership boundaries, fear of network calls) and consequences
(deployment coupling, testing difficulty, team bottleneck) of
God Object vs God Service. Do the same structural forces produce
the same structural result at a higher level?*

**Q2.** A team uses the Singleton pattern for a cache that should
be shared across all requests in a web server. In a single-process
deployment, this works correctly. In a horizontally-scaled
deployment with 10 server instances, each instance has its own
Singleton, producing inconsistent cache state. At what point did
the pattern become an anti-pattern, and what structural property
of Singleton makes this transition inevitable?

*Hint: The Singleton guarantees uniqueness within a JVM process
- a scope that is not the deployment unit in distributed
systems. The pattern's invariant guarantee and the system's
actual requirements diverged. What does this teach about
the role of context in the pattern/anti-pattern boundary?*

**Q3.** You are writing engineering standards for a 30-engineer
team. Design a one-page reference guide that distinguishes
pattern, anti-pattern, and idiom, provides the 5 most important
GoF patterns your team uses, the 3 most common anti-patterns
you see in your codebase, and the 3 idioms relevant to your
language version. What makes each choice defensible?

*Hint: Prioritise patterns that appear in your team's code reviews
most frequently; anti-patterns that caused actual production
incidents or major refactors; idioms that new engineers get wrong
because they learned from older-language tutorials.*

---

### 🎯 Interview Deep-Dive

**Q1: What is the difference between a code smell, an
anti-pattern, and bad code? Give an example of each.**

*Why they ask:* Tests precision of design vocabulary - many
candidates confuse these three categories.

*Strong answer includes:*
- Code smell: a heuristic indicator that something may be wrong
  without certainty - example: long method, feature envy
  (these require investigation, not immediate refactoring)
- Anti-pattern: a catalogued, named, recurring failure mode
  with documented consequences and refactoring path - example:
  God Object (the recurrence across independent codebases is
  what makes it a catalogued anti-pattern, not just a smell)
- Bad code: a local, non-recurring mistake with no structural
  significance beyond the specific instance - example: wrong
  variable name, missing null check, incorrect loop condition

**Q2: Give an example of a time you identified an anti-pattern
in production code. What were the symptoms, how did you
recognise it, and what was the refactoring path?**

*Why they ask:* Tests whether anti-pattern vocabulary is
practical experience rather than textbook knowledge.

*Strong answer includes:*
- A specific anti-pattern by name (God Object, Lava Flow,
  Spaghetti Code, Golden Hammer)
- Concrete symptoms: class size, coupling metrics, test failure
  patterns, deployment frequency problems
- Recognition mechanism: pattern matching against the catalog
  description, not just "it felt wrong"
- Refactoring path: what was decomposed, what principle guided
  decomposition (SRP, separation of concerns), what the
  result looked like

**Q3: How do you identify the correct idiom for expressing a
design pattern in a specific language or framework?**

*Why they ask:* Tests whether the candidate adapts pattern
knowledge to language context rather than applying Java-era
class hierarchies uniformly.

*Strong answer includes:*
- The question to ask: "What does this language provide natively
  that expresses this intent without a custom class hierarchy?"
- Examples: Java 8+ lambdas for Strategy/Command, Python
  context managers for Resource Acquisition Is Initialization,
  Kotlin data class copy() for Builder
- The validation: does the idiomatic version preserve the
  pattern's intent? If yes, prefer the idiom. If the idiom
  loses important guarantees (validation in build(), lifecycle
  hooks), the full pattern class is warranted.

