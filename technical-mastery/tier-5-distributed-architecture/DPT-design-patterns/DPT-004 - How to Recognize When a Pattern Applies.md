---
id: DPT-004
title: How to Recognize When a Pattern Applies
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-002, DPT-003
used_by: DPT-005, DPT-061
related: DPT-003, DPT-005, DPT-061
tags:
  - pattern
  - architecture
  - intermediate
  - mental-model
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 4
permalink: /technical-mastery/design-patterns/how-to-recognize-when-a-pattern-applies/
---

⚡ TL;DR - A pattern applies when you feel tension between two
valid forces - like "I need to add new behaviour without modifying
existing code" - and a named pattern resolves exactly that tension.

| #4 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-002, DPT-003 | |
| **Used by:** | DPT-005, DPT-061 | |
| **Related:** | DPT-003, DPT-005, DPT-061 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An engineer reads the GoF book, learns all 23 pattern names, and
confidently joins their first architecture review. The senior
engineer describes a notification problem. The junior engineer
immediately says "Observer!" The senior says "no, this is different
- the consumers need to transform the data before reacting" and
the junior is lost. Pattern knowledge without pattern recognition
is a vocabulary test, not a design skill.

**THE BREAKING POINT:**
Knowing that 23 patterns exist is useless if you cannot identify
which one a given design problem activates. Most engineers can
describe what a Decorator is; far fewer can look at a design
requirement and reliably conclude "this is a Decorator situation."
The gap between knowledge and recognition is the most common
failure in pattern education, and no amount of reading the
catalog closes it without a recognition framework.

**THE INVENTION MOMENT:**
This is exactly why pattern recognition skill matters: the pattern
catalog is a reference, but engineering judgment is applied in
real time, under constraint, while reading code. You need a fast
way to match problem symptoms to pattern solutions.

**EVOLUTION:**
Christopher Alexander's original pattern language concept included
"forces" - the competing tensions a pattern must resolve - as the
core of pattern description. The GoF simplified this in their
catalog but retained Applicability sections. Modern pattern
education has rediscovered forces-based recognition as the most
reliable method: identify the competing tensions first, then look
for the pattern that resolves them both.

---

### 📘 Textbook Definition

**Pattern recognition** in software design is the cognitive skill
of matching a set of design constraints and tensions in a specific
context to the intent, applicability, and known forces of a named
pattern. It operates by identifying the structural problem class
the requirement belongs to (Creational / Structural / Behavioral),
identifying the competing forces the design must balance, and
selecting the pattern whose forces-resolution matches the
requirement - before examining specific implementations.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Pattern recognition is not "I've seen this code before" -
it is "these two forces are in tension, and one pattern resolves
exactly this tension."

**One analogy:**
> A doctor does not diagnose by recognising a patient they've seen
> before. They diagnose by pattern-matching symptoms to a disease
> profile: fever + rash + location of rash. The disease is the
> pattern; the symptoms are the forces. You recognise the disease
> when the symptom cluster matches the profile, not when you've
> seen that exact patient.

**One insight:**
The fastest path to pattern recognition is through the GoF
Applicability section of each pattern - not the Structure section.
The Structure tells you what it looks like; the Applicability tells
you WHEN to apply it. Learning the "when" before the "what"
inverts the standard teaching order but produces recognition faster.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every pattern resolves a specific set of competing forces.
   The forces are the recognisable signature of the pattern - not
   the class diagram.
2. Forces are more stable than implementations. The Observer forces
   ("I need to notify multiple consumers without coupling to
   their types") have been present in software for 40 years.
   The Java implementation has changed three times.
3. Misapplication always comes from matching on the wrong signal -
   usually "this looks structurally similar to Observer" rather
   than "these forces match what Observer resolves."

**DERIVED DESIGN:**
The recognition framework has four steps:
1. Identify the structural category: is the problem about
   CREATION, COMPOSITION, or COMMUNICATION?
2. Identify the competing forces: what two valid engineering
   goals are in tension?
3. Find the pattern whose Applicability section matches the
   force pair.
4. Confirm with the Consequences: are the trade-offs acceptable
   in this context?

**THE TRADE-OFFS:**

**Gain:** Reliable pattern identification with less experience,
faster design decisions, reduced misapplication.

**Cost:** Forces-based analysis takes more time upfront than
intuitive pattern matching; novices find it mechanical before
it becomes natural.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Design problems have genuine competing forces that
cannot be eliminated - adding a new type both "requires a new
class" AND "should not require editing existing code." The tension
is real.

**Accidental:** Much of what engineers call "recognising a pattern"
is actually recognising a familiar code structure - which is
fast but fragile. The forces-based approach is slower initially
but produces correct matches in novel contexts.

---

### 🧪 Thought Experiment

**SETUP:**
A team builds a payment system. The requirement says: "Support
credit card, PayPal, and crypto payment. New payment methods
will be added regularly. The checkout process should not be
modified when a new payment method is added."

**IDENTIFYING THE FORCES:**
Force 1: The checkout process must invoke payment behavior.
Force 2: New payment types must be added without modifying the
checkout process.
These two forces are in tension: invoking behavior requires
knowing the type; avoiding modification requires not knowing it.

**FINDING THE PATTERN:**
Which pattern resolves "invoke behavior without knowing the
concrete type"? Strategy: define an interface (PaymentStrategy),
inject the concrete implementation, invoke through the interface.
The checkout process only knows PaymentStrategy - not the
concrete type. New payment methods add a new concrete class,
zero checkout modifications.

**THE INSIGHT:**
You found Strategy not by recognising a familiar class diagram
but by identifying the exact forces that Strategy exists to
resolve. This generalises: the force pair "invoke behavior
without coupling to type" always points to Strategy. Learn
the force signatures, not the class diagrams.

---

### 🧠 Mental Model / Analogy

> Pattern recognition is like learning chess openings. A chess
> player does not recognise the Sicilian Defense by looking at
> the board and thinking "I've seen this exact board position
> before." They recognise it by the specific pawn tension: e4
> responded to with c5 creates specific weaknesses and strengths
> that define the opening's character. The position is the
> pattern; the pawn tension is the forces.

- "Chess opening" - design pattern name
- "Pawn tension" - competing design forces the pattern resolves
- "Board position" - the actual class/code structure
- "Recognising the opening" - pattern recognition
- "Playing the opening correctly" - applying the pattern

**Where this analogy breaks down:** Chess openings are exactly
reproducible. Design pattern forces have fuzzy matches - two
situations may have partially overlapping forces and both be
partially addressed by the same pattern. Judgment is required.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Pattern recognition is the skill of looking at a design problem
and knowing which named solution fits it. Like knowing which
recipe to follow when you want to feed 20 people in 30 minutes:
the recipe is the pattern, the constraints (20 people, 30 minutes)
are the forces.

**Level 2 - How to use it (junior developer):**
When you face a design problem, ask: Is it about how objects are
created (Creational), how they are assembled (Structural), or how
they communicate (Behavioral)? This narrows 23 patterns to 7 or
fewer. Then read the Applicability section of each candidate
pattern and find the one that matches your specific constraint.
Do NOT start by looking at the class diagram.

**Level 3 - How it works (mid-level engineer):**
Forces-based recognition: identify the two or three competing
design goals that feel in tension. Each GoF pattern has a
canonical force pair:
- Observer: "notify many consumers" vs "don't couple to consumer types"
- Strategy: "vary the algorithm" vs "don't alter the host class"
- Decorator: "add behavior dynamically" vs "don't use inheritance"
- Facade: "simplify a complex subsystem" vs "keep subsystem usable"
The force pair is the pattern's fingerprint. Match the forces,
find the pattern.

**Level 4 - Why it was designed this way (senior/staff):**
Structural matching (recognising a class diagram) fails when
two patterns share the same structure but differ in intent:
Decorator and Proxy are structurally identical - both wrap
an interface. They are distinguished entirely by intent:
Decorator adds behavior, Proxy controls access. If you
recognise by structure, you will confuse them. If you recognise
by forces ("I need to add behavior dynamically" = Decorator;
"I need to control or log access" = Proxy), you will not.
Intent-based recognition is the only reliable method for
the structurally-similar pattern pairs.

**Level 5 - Mastery (distinguished engineer):**
Expert pattern recognition includes knowing when NO pattern
applies - when the design problem is unique or simple enough
that a named pattern would add unnecessary structure. The
signal is: if you cannot articulate two competing forces that
the pattern resolves, the pattern does not fit. A feature
with one concrete implementation and no planned extension does
not have the forces that Strategy resolves. Applying Strategy
anyway is over-engineering. The absence of recognisable forces
is itself a recognition signal: stop before the pattern.

---

### ⚙️ Why It Holds True (Formal Basis)

Forces-based recognition works because forces are the invariant
property of each pattern - they are what the pattern was designed
to resolve, and they persist regardless of language, framework,
or implementation style.

**The Four-Step Recognition Framework:**

```
Step 1: Classify the problem domain
  Is it about CREATION?   → Creational family (5 patterns)
  Is it about COMPOSITION?→ Structural family (7 patterns)
  Is it about BEHAVIOR?   → Behavioral family (11 patterns)

Step 2: Identify the competing forces
  "I need X AND I need Y, but X and Y pull in opposite
   directions in my current design."
  Write out both forces explicitly.

Step 3: Match forces to pattern Applicability
  Find the pattern whose Applicability section describes
  your exact tension. The match should feel inevitable,
  not forced.

Step 4: Validate with Consequences
  Are the trade-offs this pattern introduces acceptable
  in your specific context? If the Consequences list
  costs you cannot accept, the pattern does not fit
  even if the forces match.
```

**Force signatures for the most-used patterns:**

| Pattern     | Force 1                      | Force 2                           |
| ----------- | ---------------------------- | --------------------------------- |
| Strategy    | Vary the algorithm           | Don't modify the host class       |
| Observer    | Notify multiple consumers    | Don't couple to consumer types    |
| Decorator   | Add behavior dynamically     | Don't use subclass inheritance    |
| Factory M.  | Create objects               | Don't couple to concrete class    |
| Facade      | Simplify a complex API       | Keep the subsystem accessible     |
| Proxy       | Control access to an object  | Don't modify the real subject     |
| Command     | Parameterize an operation    | Support undo / log / queue it     |
| Template M. | Define algorithm skeleton    | Let subclasses fill in steps      |

---

### 🔄 System Design Implications

Pattern recognition operates at multiple levels simultaneously.
The same force pairs that identify class-level patterns also
identify architectural patterns:

| Force Pair                                    | Class Pattern   | Arch Pattern           |
| --------------------------------------------- | --------------- | ---------------------- |
| Vary behavior, don't modify invoker           | Strategy        | Feature flag / A-B test|
| Notify many, don't couple to consumer type    | Observer        | Event bus / Pub-sub    |
| Simplify a complex subsystem API              | Facade          | API Gateway / BFF      |
| Control access, add cross-cutting behavior    | Proxy           | Service mesh sidecar   |
| Create objects, don't couple to concrete type | Factory Method  | Service discovery      |

**At scale (100+ engineers):**
Pattern recognition becomes a team skill, not just an individual
one. Teams that share force-pair vocabulary can write PR comments
like "the forces here are X and Y - which patterns resolve this
tension?" and receive productive responses. Teams without this
shared vocabulary spend the same discussion time arguing about
what the correct structure should be.

**What engineers ignore and what breaks:**
Engineers commonly recognise patterns by structure when reviewing
code, causing Decorator-vs-Proxy confusion and Strategy-vs-Template-
Method confusion. Force-pair analysis resolves these ambiguous
cases immediately but is rarely taught in pattern education.

---

### 💻 Code Example

**Example 1 - Force identification leading to pattern selection:**

```java
// REQUIREMENT:
// "Add logging, caching, and retry behavior to any service
//  call without modifying the service implementations."

// FORCE 1: Need to add behavior to an existing object
// FORCE 2: Cannot modify the existing object's code
// FORCE PAIR -> Decorator pattern (add behavior without
//              modification, wrapping the original interface)

interface UserService {
    User findById(long id);
}

// Decorator adds caching - no modification to original
class CachingUserService implements UserService {
    private final UserService delegate;
    private final Cache cache;

    CachingUserService(UserService delegate, Cache cache) {
        this.delegate = delegate;
        this.cache = cache;
    }

    @Override
    public User findById(long id) {
        return cache.computeIfAbsent(
            id, k -> delegate.findById(k)
        );
    }
}
// Stack decorators: logging -> caching -> retry -> real
```

**Example 2 - Force analysis distinguishing Decorator from Proxy:**

```java
// BAD: Using Proxy structure for Decorator intent
// - correct structure, wrong intent label
class LoggingProxy implements UserService {
    // This IS Decorator (adds behavior),
    // NOT Proxy (controls access)
    // Correct: name it LoggingUserService (a Decorator)
}

// GOOD: Force-based naming confirms the right pattern
// FORCE: "Add logging behavior to UserService"
// FORCE: "Without modifying UserService implementation"
// -> Decorator intent confirmed
// -> Name: LoggingUserServiceDecorator

// Proxy would apply if:
// FORCE: "Control who can call UserService"
// FORCE: "Add authentication check before every call"
// -> Proxy intent: AuthenticatingUserServiceProxy
```

---

### ⚖️ Comparison Table

| Recognition Method | Speed  | Accuracy | Fails When                        |
| ------------------ | ------ | -------- | --------------------------------- |
| **Forces-based**   | Medium | High     | Forces are weakly defined         |
| Structure-matching | High   | Medium   | Two patterns share same structure |
| Intuitive / gut    | High   | Low      | Novel context or complex forces   |
| Catalog scanning   | Low    | High     | Time pressure, 23 candidates      |

**How to choose:** Use forces-based recognition as the primary
method for any non-trivial design decision. Use structure-matching
for quick sanity checks on familiar patterns. Fall back to catalog
scanning when forces are unclear or the problem is novel.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| You recognise patterns by looking at class diagrams | Decorator and Proxy are structurally identical - only force analysis distinguishes them |
| If it looks like Observer, it is Observer | Observer requires the forces: notify multiple consumers, decouple from consumer types; structure without forces is not sufficient for recognition |
| Pattern recognition is a talent | It is a learnable framework - forces analysis is a skill, not intuition, and improves with deliberate practice |
| Reading the GoF book produces pattern recognition | Reading catalogs builds vocabulary; forces-based analysis practiced on real code builds recognition |
| More patterns known = better recognition | Fewer patterns understood deeply (forces + consequences) outperforms many patterns known shallowly (name + class diagram) |

---

### 🚨 Failure Modes & Diagnosis

**Structure-Based Recognition Confusion**

**Symptom:**
Team calls a wrapper class a "Proxy" when its intent is to add
caching behavior to an existing interface - which is Decorator.
Code review debates whether the wrapper is "really a Proxy or
a Decorator" without resolution.

**Root Cause:**
Both Decorator and Proxy wrap an interface. Team is matching on
structure, not intent or forces. The structural approach cannot
distinguish them.

**Diagnostic Signal:**
Ask: "What is the PURPOSE of this wrapper?" If the answer is
"to add behavior" = Decorator. If the answer is "to control
or intercept access" = Proxy. The force distinction is instant.

**Fix:**
Rename the class to reflect the correct pattern name. Document
the forces it resolves in the class Javadoc. This makes future
recognition easier and the intent explicit.

**Prevention:**
Add the forces (not just the pattern name) to class-level
documentation: "Decorator - adds caching behavior to UserService
without modification."

---

**Forced Pattern Application (Premature Pattern Use)**

**Symptom:**
Engineer says "this needs Strategy" before the design even has
two concrete implementations, then builds a full Strategy
interface hierarchy for a payment processor with exactly
one payment method.

**Root Cause:**
Force 2 of Strategy ("vary the algorithm without modifying the
host class") does not yet exist. There is only one algorithm.
The engineer is applying the pattern speculatively.

**Diagnostic Signal:**
Count the concrete implementations of the Strategy. If there
is exactly one, Force 2 does not yet exist. The pattern is
premature.

**Fix:**
Implement the single concrete algorithm directly, without the
Strategy interface. When the second concrete implementation
appears, introduce Strategy then. The refactoring is trivial;
the speculative complexity is real.

**Prevention:**
Before applying any Creational, Structural, or Behavioral
pattern, explicitly state both forces in writing. If you
cannot articulate Force 2 with a concrete example from the
current requirements, the pattern is premature.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `What Are Design Patterns and Why They Exist` - why patterns
  exist and what problem the recognition skill solves
- `Pattern vs Anti-Pattern vs Idiom` - the vocabulary for
  distinguishing correct pattern identification from misuse
- `The Gang of Four - Origin and Philosophy` - the catalog whose
  Applicability sections are the recognition reference

**Builds On This (learn these next):**
- `The Design Patterns Ecosystem Map` - the complete map of
  all 23 patterns and their relationships, essential for
  navigating the catalog under recognition pressure
- `Pattern Selection Framework` - the formal decision framework
  for choosing between patterns with overlapping applicability

**Alternatives / Comparisons:**
- `SOLID Principles` - an alternative recognition heuristic:
  SOLID violation often signals which pattern resolves it;
  OCP violation often signals Strategy or Decorator

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Framework for matching design tensions   │
│              │ to pattern solutions before coding       │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Pattern vocabulary without recognition   │
│ SOLVES       │ skill is useless under design pressure   │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ Match forces (tensions) not structures   │
│              │ (class diagrams) - forces are the signal │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Facing a design constraint with two      │
│              │ competing valid engineering goals        │
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ Recognising a familiar structure and     │
│              │ assuming the pattern without forces check│
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Applying a pattern because the structure │
│              │ looks familiar - structure without forces│
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Recognition accuracy vs analysis speed   │
│              │ (forces analysis is slower but correct)  │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Patterns match forces, not class shapes;│
│              │  learn the tension, find the resolution" │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Ecosystem Map → Strategy → Observer      │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Identify the TWO competing forces before naming any pattern -
   the force pair is the pattern's recognisable signature
2. Decorator and Proxy are structurally identical - only force
   analysis distinguishes them reliably
3. If you cannot articulate Force 2 from current requirements,
   the pattern is premature - implement directly first

**Interview one-liner:**
"I recognise a pattern by identifying the competing forces first:
what two valid engineering goals are in tension? Each pattern
resolves a specific force pair. Strategy resolves 'vary the
algorithm without modifying the invoker.' Observer resolves
'notify many consumers without coupling to their types.' The
force pair points to the pattern; the structure confirms it."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
The most reliable way to recognise a solution is to precisely
identify the problem it solves - not to recognise a familiar
solution shape. This principle applies in diagnosis, law,
engineering, and any field where template solutions are applied
to instance problems.

**Where else this pattern appears:**
- **Legal precedent** - Lawyers argue that a case should follow
  a specific precedent by demonstrating that the underlying
  legal tensions match those the precedent resolved; structural
  similarity alone is insufficient - the forces must match
- **Medical diagnosis** - Differential diagnosis works by
  identifying symptom forces (which symptoms are present AND
  which are absent) and finding the disease profile that resolves
  the differential; pattern-matching on appearance alone produces
  misdiagnosis
- **Financial engineering** - Options strategies are selected
  by identifying market forces (direction + volatility +
  time horizon) and finding the strategy that resolves them;
  the strategy name alone does not determine applicability

**Industry applications:**
- **Architecture review boards** - Using forces vocabulary
  ("these forces suggest Circuit Breaker, but the Consequences
  include latency; do we accept that?") produces faster, more
  productive architecture decisions than structure-based debates
- **Technical hiring** - Forces-based pattern recognition
  questions ("what competing goals are in tension here?")
  distinguish candidates who understand design from candidates
  who have memorised catalog entries

---

### 💡 The Surprising Truth

The GoF book describes 23 patterns, but only about 7 appear
regularly in the average production codebase. The other 16 are
valuable to know for recognition purposes - you need them to
avoid reinventing them - but most engineers implement only
Strategy, Observer, Factory Method, Decorator, Singleton,
Template Method, and Command in a typical career. The implication
is counterintuitive: learning to recognise ALL 23 deeply is less
valuable than learning to apply the top 7 correctly AND knowing
when none of the 23 fits. The "when none fits" case - resisting
the urge to apply a pattern to a problem that does not warrant
one - is what separates a good pattern user from a pattern abuser.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [EXPLAIN] Given any of the top-7 patterns, articulate the
   exact force pair it resolves in one sentence each, without
   consulting the catalog
2. [DEBUG] Given a codebase where Decorator and Proxy are confused
   (wrapper classes with inconsistent intent labels), identify
   the correct pattern for each wrapper using force analysis in
   under 5 minutes
3. [DECIDE] Given a new requirement, apply the four-step
   recognition framework (classify domain, identify forces,
   match Applicability, validate Consequences) and arrive at
   a pattern recommendation with explicit justification
4. [BUILD] Given a description with force pair "add behavior
   dynamically without inheritance," implement the Decorator
   pattern from memory for a given interface in under 10 minutes
5. [EXTEND] Apply forces-based recognition to identify architectural
   patterns: given a distributed system design requirement with
   two competing goals, identify which architectural pattern
   (Circuit Breaker, Saga, Outbox, Strangler Fig) resolves
   the forces and explain the mapping

---

### 🧠 Think About This Before We Continue

**Q1.** The forces for Observer are "notify multiple consumers"
AND "decouple the producer from consumer types." In a reactive
stream (RxJava, Project Reactor), the same two forces are present.
But the implementation is entirely different. What does this tell
you about the relationship between force-pair recognition and
implementation patterns? When does the "same pattern, different
implementation" stop being true and become a different pattern?

*Hint: Compare the Consequences of GoF Observer (pull vs push,
memory leak risk with forgotten deregistration) to the Consequences
of reactive streams (backpressure, lazy evaluation, operator
chains). If the Consequences diverge significantly, the patterns
may share forces but differ enough to warrant separate names.*

**Q2.** A team is building a document processing pipeline that
must apply transformations in a fixed sequence but allow each
transformation to be swapped out. Two engineers argue: one says
Template Method (fixed skeleton with pluggable steps), the other
says Strategy (pluggable algorithm). Both arguments have merit.
Apply the force-pair analysis to both patterns and determine
which forces are present, which are absent, and which pattern
better matches. Is there a scenario where BOTH patterns apply
at different levels?

*Hint: Template Method resolves "fixed algorithm skeleton with
variable steps." Strategy resolves "variable algorithm, fixed
invocation." If the sequence is fixed, Template Method matches
one force. If the sequence itself can vary, Strategy matches
better. What if you need BOTH a fixed sequence AND pluggable
algorithms within each step?*

**Q3.** You are reviewing a 10,000-line service that processes
insurance claims. The service has no discernible patterns; every
business rule is expressed as nested if-else chains. Identify
the three most likely force pairs that are present but
unresolved, and name the patterns that would resolve each.
Then prioritise: which pattern, if applied first, would produce
the most reduction in code complexity?

*Hint: Look for repeated conditional logic on the same type
(State), repeated algorithm variations on similar data
(Strategy), and repeated instantiation logic tied to
conditional type selection (Factory Method). Which force
pair appears most frequently in the code would be the
highest-leverage first refactoring.*

---

### 🎯 Interview Deep-Dive

**Q1: Walk me through how you would determine whether a design
problem calls for Strategy, Template Method, or Decorator.
What questions do you ask to distinguish them?**

*Why they ask:* These three patterns are frequently confused;
distinguishing them tests forces-based recognition skill.

*Strong answer includes:*
- Strategy: varies the entire algorithm; caller injects the
  algorithm as a dependency; no inheritance required
- Template Method: the algorithm's skeleton is fixed in a base
  class; only specific steps vary in subclasses; requires
  inheritance
- Decorator: adds behavior to an existing object by wrapping it;
  no algorithm variation - just behavioral layering
- The distinguishing question: "Do you need the algorithm skeleton
  to be fixed? If yes, Template Method. Do you need to add
  behavior to an existing object without modifying it? Decorator.
  Do you need to vary the whole algorithm at runtime? Strategy."

**Q2: You are reviewing a PR where a developer has applied
the Factory Method pattern to a class that has exactly one
concrete subclass. Is this a correct use of the pattern?
How do you evaluate this in code review?**

*Why they ask:* Tests forces-based recognition vs speculative
abstraction - the most common pattern misapplication.

*Strong answer includes:*
- Factory Method resolves "create objects without coupling to
  concrete type" - Force 2 requires at least two concrete types
  to be meaningful
- With one subclass, Force 2 is hypothetical; the pattern is
  premature
- Code review approach: ask "what is the second concrete type?"
  If the answer is hypothetical ("we might add another"), apply
  YAGNI; if concrete ("we add a TestDataFactory in tests"),
  the pattern is justified
- The cost of premature pattern: added indirection, extra
  file, onboarding confusion, all for a case that may never
  extend

**Q3: Describe a case where you applied forces-based analysis
and concluded that NO existing pattern fits. What did you do?**

*Why they ask:* Tests whether the candidate knows when to
stop pattern-matching and implement directly.

*Strong answer includes:*
- A specific design problem where the force pair was unique
  enough that no catalog pattern matched without distortion
- The decision: implement the custom solution directly with
  clear naming rather than forcing a pattern
- What was preserved: the naming principle (descriptive class
  and method names that communicate intent) even without a
  catalog name
- What was monitored: watching for the second occurrence of
  the same force pair - the trigger for abstracting it into
  a named pattern for the team's local catalog

