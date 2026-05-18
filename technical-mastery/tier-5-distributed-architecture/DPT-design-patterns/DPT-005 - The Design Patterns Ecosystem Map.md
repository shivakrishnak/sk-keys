---
id: DPT-005
title: The Design Patterns Ecosystem Map
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★☆☆
depends_on: DPT-001, DPT-002
used_by: DPT-006, DPT-007, DPT-061
related: DPT-001, DPT-002, DPT-004
tags:
  - pattern
  - architecture
  - foundational
  - mental-model
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 5
permalink: /technical-mastery/design-patterns/the-design-patterns-ecosystem-map/
---

⚡ TL;DR - The 23 GoF patterns organize into three families
by concern (creation, composition, communication), and relate
to each other through composition, refinement, and contrast
relationships that guide which pattern to reach for when.

| #5 | Category: Design Patterns | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-002 | |
| **Used by:** | DPT-006, DPT-007, DPT-061 | |
| **Related:** | DPT-001, DPT-002, DPT-004 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An engineer learns the 23 GoF pattern names but treats them as an
unstructured list. They encounter a design problem, try to recall
relevant patterns, and scan all 23 mentally - a slow, unreliable
process. More critically, they miss that Composite typically uses
Iterator, that Abstract Factory often creates Singletons, that
Decorator and Proxy are structurally identical but intentionally
opposite, and that Strategy and Template Method solve related
forces at different structural levels. Without a map of how the
patterns relate, learning them individually is like memorising
27 countries in Europe without knowing the geographic map.

**THE BREAKING POINT:**
Pattern knowledge without ecosystem understanding produces two
failure modes: missing the right pattern because the search space
is too large, and misapplying a pattern because a related pattern
would have been better. The patterns do not exist in isolation -
they compose, contrast, and complement each other. Knowing the
map enables faster recognition and avoids compositional errors.

**THE INVENTION MOMENT:**
This is exactly why an ecosystem map matters: patterns have
structural and intentional relationships that make the catalog
navigable and composable. The map is the index that makes the
catalog useful under time pressure.

**EVOLUTION:**
The GoF book includes "Related Patterns" sections for every entry,
making the relationships explicit. Wolfgang Pree (1994) and Mark
Grand (1998) organised patterns into relationship maps. Modern
pattern education increasingly teaches the relationships first
and the individual patterns second, because understanding where
a pattern sits in the ecosystem accelerates recognition of the
right pattern cluster.

---

### 📘 Textbook Definition

The **design patterns ecosystem** is the structured set of
relationships among the 23 GoF patterns across the three families
(Creational, Structural, Behavioral), including: composition
relationships (patterns that use other patterns in their
implementation), refinement relationships (simpler pattern
of the same kind), contrast relationships (same structure,
different intent), and problem domain relationships (patterns
that address adjacent forces). The ecosystem map is the
navigational reference that connects the catalog into a
unified, traversable knowledge structure.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The 23 GoF patterns are not a flat list - they form a structured
ecosystem where patterns compose, contrast, and complement each
other in predictable relationships.

**One analogy:**
> The pattern ecosystem is like a city map. Knowing that Main
> Street connects to the Market District and the Train Station
> does not tell you what those places look like, but it tells you
> how to navigate between them. The pattern map tells you that
> when you need Abstract Factory, Singleton often appears inside
> it; when you choose Decorator, Proxy is nearby with a different
> intent; when you consider Strategy, Template Method addresses
> the same problem at a different structural level.

**One insight:**
The five structurally or intentionally confusable pattern pairs
are the most important part of the ecosystem map to memorise:
Decorator vs Proxy, Strategy vs Template Method, Factory Method
vs Abstract Factory, Command vs Strategy, Composite vs Decorator.
These are where engineers most often misapply a pattern - knowing
the map prevents the confusion.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The three-family structure (Creational, Structural, Behavioral)
   is exhaustive for class-level OOP design concerns. Every OOP
   design problem belongs to exactly one family.
2. Patterns within the same family address related but distinct
   forces. Knowing the family narrows the search from 23 to 5-11.
3. Cross-family relationships (Composite uses Iterator, Observer
   uses Singleton for the subject) reflect that real systems
   combine patterns across families.

**DERIVED DESIGN:**
The ecosystem map has four types of edges between patterns:

1. **Composition**: Pattern A typically uses Pattern B in its
   implementation. Example: Composite uses Iterator; Abstract
   Factory may create Singletons; Command uses Memento for undo.

2. **Refinement**: Pattern A is a simpler version of Pattern B.
   Example: Factory Method is a simpler refinement of Abstract
   Factory.

3. **Contrast**: Pattern A and Pattern B have the same structure
   but different intent. Example: Decorator vs Proxy (both wrap
   an interface); Strategy vs Command (both encapsulate behavior).

4. **Problem Domain**: Pattern A and Pattern B solve adjacent
   forces. Example: Strategy and Template Method both address
   algorithm variation - Strategy at the object level,
   Template Method at the inheritance level.

**THE TRADE-OFFS:**

**Gain:** Faster pattern navigation, avoidance of structurally-
similar-but-intentionally-different confusion, awareness of
compositional patterns.

**Cost:** The map adds cognitive overhead if memorised as a table;
it becomes valuable only when internalised as a navigational
heuristic.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** The relationships between patterns are real and
structural - they derive from the underlying forces and
implementations. Composite genuinely uses Iterator in most
implementations.

**Accidental:** Memorising every relationship in the map is
unnecessary and counterproductive. The five confusable pairs
and the top three composition relationships are the high-value
subset.

---

### 🧪 Thought Experiment

**SETUP:**
You are designing a graphics editor. Objects can be simple shapes
(Circle, Rectangle) or groups (a selection that contains other
shapes, including other groups). The editor must support
operations applied uniformly to both simple shapes and groups.

**NAVIGATING THE ECOSYSTEM:**
Family: STRUCTURAL (composition of objects into tree structures).
Candidates: Composite, Decorator, Bridge.
Composite's intent: "Compose objects into tree structures and
let clients treat individual objects and compositions uniformly."
This matches exactly. But Composite typically uses Iterator for
traversal. When you implement traversal of the shape tree,
reach for Iterator - the ecosystem map told you what comes next.

**WHAT THE MAP PREVENTED:**
Without the map, an engineer might reach for Decorator (also
Structural, also deals with wrapping objects) and spend two
hours discovering that Decorator does not model tree containment -
it models single-object behavioral layering. The map's
Contrast edge between Composite and Decorator prevents this.

**THE INSIGHT:**
The ecosystem map reduces the search space and pre-empts
compositional errors. Knowing "Composite uses Iterator" saves
the design work of re-discovering the relationship independently.

---

### 🧠 Mental Model / Analogy

> The GoF pattern ecosystem is like the periodic table of
> elements, but with visible chemical bonds drawn in. The
> elements are the 23 patterns; the bonds are the four
> relationship types. Just as knowing that Carbon bonds with
> Hydrogen to form hydrocarbons speeds up organic chemistry,
> knowing that Composite bonds with Iterator speeds up
> tree-based design.

- "Elements" - the 23 patterns
- "Chemical families" - the three GoF families
- "Covalent bonds" - composition relationships
- "Isotopes" - refinement relationships (Factory Method / Abstract Factory)
- "Structural isomers" - contrast relationships (Decorator / Proxy)

**Where this analogy breaks down:** Chemical bonds have fixed
energies and geometries. Pattern relationships are guidelines,
not laws - you can implement Composite without Iterator if your
traversal needs are simple enough. The map describes what
commonly occurs, not what must occur.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
The 23 GoF patterns are organised into three groups by the type
of problem they solve: how to create objects (Creational),
how to connect objects (Structural), and how objects communicate
(Behavioral). Within each group, patterns relate to each other
as simpler/more complex, same-structure/different-intent, or
used-together.

**Level 2 - How to use it (junior developer):**
When facing a design problem, first identify the family (creation,
composition, or communication), then look at the 5-11 patterns in
that family. The Related Patterns section of any GoF entry will
point you to adjacent patterns when the first candidate does not
quite fit. Follow the map, do not scan all 23.

**Level 3 - How it works (mid-level engineer):**
The five most important contrast pairs to memorise:
- Decorator vs Proxy: same structure, add-behavior vs control-access
- Strategy vs Template Method: pluggable algorithm vs fixed-skeleton
- Factory Method vs Abstract Factory: single type vs family of types
- Command vs Strategy: execute once vs vary algorithm
- Composite vs Decorator: tree containment vs behavioral wrapping
These five pairs are where misapplication is most common.

**Level 4 - Why it was designed this way (senior/staff):**
The three-family taxonomy was not the only possible organisation.
The GoF considered organizing by scope (class-level vs object-level)
and by variability (what the pattern allows to vary). The three-
family approach won because it corresponds to the three phases of
object lifecycle: creation, structural assembly, and behavioral
interaction. This mapping to lifecycle makes the taxonomy
intuitive to navigate once the lifecycle is understood.

**Level 5 - Mastery (distinguished engineer):**
An expert uses the ecosystem map in reverse: given a pattern that
fits, immediately ask what other patterns are typically co-present
in the same system. A system that uses Composite for its data model
will likely need Iterator for traversal, Visitor for operations
across the tree, and possibly Command for user operations on the
tree. This compositional reasoning predicts the full pattern
architecture of a system from a single identified pattern -
the map enables design pattern coherence, not just individual
pattern selection.

---

### ⚙️ Why It Holds True (Formal Basis)

The ecosystem relationships are empirically derived from the
GoF's Known Uses survey. Abstract Factory was found to typically
involve Singleton because factories are often created once and
shared. Composite was found to use Iterator because any tree
structure needs a traversal mechanism. These are co-occurrence
observations from production code, not theoretical derivations.

The map is therefore descriptive (what typically co-occurs)
rather than prescriptive (what must co-occur). This is the
same empirical methodology that validated the patterns
individually: observation of recurring structural co-occurrence
in independent systems.

**What violating the ecosystem understanding produces:**
Teams that apply patterns individually without awareness of
composition relationships repeatedly discover the same secondary
patterns through independent trial and error. The cost is paid
in design iteration time. The ecosystem map converts others'
trial-and-error into the team's starting point.

---

### 🔄 System Design Implications

The ecosystem map scales directly to distributed system pattern
relationships. The same four relationship types apply:

```
Distributed System Ecosystem:

COMPOSITION:
  Circuit Breaker uses Retry (retry before tripping)
  Saga uses Outbox (reliable event publishing)
  Outbox uses Polling or CDC (delivery mechanism)

REFINEMENT:
  Retry is a simpler refinement of Circuit Breaker
  Bulkhead is a simpler refinement of full isolation

CONTRAST:
  Outbox vs Inbox: producer-side vs consumer-side guarantee
  Saga (choreography) vs Saga (orchestration): same
    problem,
    different coordination mechanism

PROBLEM DOMAIN:
  Circuit Breaker + Bulkhead + Retry = resilience cluster
  Saga + Outbox + Idempotency = eventual consistency
    cluster
```

**At scale:**
Pattern ecosystems at the distributed level have the same
co-occurrence property as class-level patterns. A system
that needs Saga for distributed transactions will also need
Outbox for reliable event publishing and Idempotency for
safe retries. Knowing the distributed ecosystem map predicts
the full pattern set needed for a given reliability requirement.

---

### 💻 Code Example

**Example - Following the ecosystem map in implementation:**

```java
// CONTEXT: Building a UI component tree (Composite pattern)
// ECOSYSTEM MAP says: Composite uses Iterator for traversal

// Step 1: Composite pattern for the tree
interface UIComponent {
    void render();
    // Composite adds:
    void add(UIComponent c);
    Iterator<UIComponent> children();
}

class Panel implements UIComponent {
    private List<UIComponent> children = new ArrayList<>();

    @Override
    public void render() {
        // Render self, then traverse children
        renderBackground();
        // Step 2: Use Iterator (ecosystem map said so)
        Iterator<UIComponent> it = children();
        while (it.hasNext()) {
            it.next().render();  // uniform interface
        }
    }

    @Override
    public Iterator<UIComponent> children() {
        return children.iterator();
    }

    @Override
    public void add(UIComponent c) { children.add(c); }
}

// Step 3: Ecosystem map says Composite + Visitor for operations
interface ComponentVisitor {
    void visit(Button b);
    void visit(Panel p);
    void visit(TextLabel t);
}
// Visitor applies operations (validate, export, measure)
// across the Composite tree without modifying components
```

The ecosystem map told the engineer: use Composite for tree
structure, use Iterator for traversal, use Visitor for
operations. Three patterns in a predicted co-occurrence cluster.

---

### ⚖️ Comparison Table

| Relationship Type | Description                          | Example                         |
| ----------------- | ------------------------------------ | ------------------------------- |
| **Composition**   | Pattern A uses Pattern B internally  | Composite uses Iterator         |
| Refinement        | Pattern A is simpler version of B    | Factory Method < Abstract Factory|
| Contrast          | Same structure, different intent     | Decorator vs Proxy              |
| Problem Domain    | Adjacent forces, adjacent solutions  | Strategy vs Template Method     |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| The 23 patterns are an unstructured flat list | They form a structured ecosystem with four types of relationships that guide navigation |
| Learning patterns one-by-one is sufficient | Understanding the ecosystem relationships is what enables rapid recognition and avoids misapplication |
| All patterns within a family are interchangeable | Patterns within a family address different forces; Composite and Decorator are both Structural but cannot substitute for each other |
| Newer patterns (cloud, distributed) are separate from GoF | They extend the same ecosystem concept; the four relationship types apply identically at the distributed level |
| The ecosystem map must be memorised completely | Only the five confusable contrast pairs and the top composition relationships need to be memorised; the rest is reference material |

---

### 🚨 Failure Modes & Diagnosis

**Decorator-Proxy Confusion**

**Symptom:**
A codebase has classes named "XyzProxy" that add logging or
caching behavior rather than controlling access. Code reviews
frequently debate whether a wrapper class "is a Proxy or
Decorator" without a framework for resolution.

**Root Cause:**
Decorator and Proxy are structurally identical - both wrap an
interface. Without the contrast relationship from the ecosystem
map, engineers cannot distinguish them by code inspection alone.

**Diagnostic Signal:**
Ask: "Does this wrapper ADD behavior to the subject, or does
it CONTROL access to the subject?" Adding behavior (logging,
caching, retry) = Decorator. Controlling access (auth check,
rate limit, remote delegation) = Proxy.

**Fix:**
Rename wrappers to reflect correct intent: XyzCachingDecorator,
XyzLoggingDecorator, XyzAuthorizationProxy. This prevents future
confusion and makes the intent self-documenting.

**Prevention:**
Add the contrast relationship (Decorator vs Proxy) to team
engineering standards as a named, canonical pattern pair.
Enforce naming conventions that embed the correct pattern name.

---

**Missing Composite Companions**

**Symptom:**
A Composite-based data model has been implemented but traversal
requires ad-hoc recursion in every caller rather than a shared
Iterator or Visitor. Operations on the tree are duplicated
across callers.

**Root Cause:**
The team implemented Composite correctly but did not know the
ecosystem map predicts that Composite needs Iterator for
traversal and Visitor for operations. Both were re-discovered
independently, implemented inconsistently, and duplicated.

**Diagnostic Signal:**
Find places in the codebase where recursive tree traversal is
re-implemented: multiple methods with `if (node instanceof Group)
{ for (child : node.children) { ... } }`. This is Iterator
behavior re-implemented without the Iterator name.

**Fix:**
Introduce a standard Iterator or tree traversal mechanism for
the Composite. Introduce Visitor if multiple operation types
are applied to the tree. Replace all ad-hoc recursion with
the canonical companions.

**Prevention:**
When implementing Composite, immediately ask: "What is the
traversal mechanism?" and "What operations will be applied
to the tree?" The answers lead to Iterator and Visitor.
The ecosystem map is a checklist, not just a reference.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `What Are Design Patterns and Why They Exist` - the vocabulary
  context the ecosystem map organises
- `The Gang of Four - Origin and Philosophy` - the catalog the
  ecosystem map is built from

**Builds On This (learn these next):**
- `Singleton` through `Visitor` - the 23 individual patterns,
  whose ecosystem relationships are now navigable
- `Pattern Selection Framework` - the decision process that
  uses the ecosystem map as its reference

**Alternatives / Comparisons:**
- `Software Architecture Patterns` - the SAP category, which
  extends the same ecosystem concept to the system architecture
  level; the relationship types are identical

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Structured map of 23 GoF pattern         │
│              │ relationships across 3 families          │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Patterns learned as a flat list produce  │
│ SOLVES       │ slow recognition and composition errors  │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ Five contrast pairs cause most confusion:│
│              │ Decorator/Proxy, Strategy/Template, etc. │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Navigating the catalog under time pressur│
│              │ or identifying companion patterns        │
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ Treating the map as a prescription;      │
│              │ not every Composite needs Iterator       │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Learning all 23 individually without     │
│              │ understanding the relationship structure │
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Navigation speed vs map memorisation cost│
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Composite comes with Iterator; Proxy is │
│              │  not Decorator - know the map, skip the  │
│              │  rediscovery"                            │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Singleton → Factory Method → Observer    │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Three families organize the 23 patterns: Creational (5),
   Structural (7), Behavioral (11) - identify the family first
   to narrow your search
2. Five contrast pairs cause the most confusion: Decorator/Proxy,
   Strategy/Template Method, Factory Method/Abstract Factory,
   Command/Strategy, Composite/Decorator
3. Composite uses Iterator; Composite uses Visitor; Abstract
   Factory often contains Singletons - these composition
   relationships are pre-computed design knowledge

**Interview one-liner:**
"The GoF ecosystem organises 23 patterns into Creational,
Structural, and Behavioral families with four types of
relationships: composition (Composite uses Iterator), refinement
(Factory Method is simpler than Abstract Factory), contrast
(Decorator vs Proxy - same structure, different intent), and
problem domain (Strategy vs Template Method - same force pair,
different structural level). Knowing the map enables faster
recognition and avoids the most common misapplications."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
In any domain where a catalog of named solutions exists, the
relationships between solutions are as important as the solutions
themselves. Navigation requires a map; application requires
understanding which solutions compose, which contrast, and which
compete. A catalog without a map is a library without an index.

**Where else this pattern appears:**
- **Musical theory** - Chords relate to each other in functional
  harmony (tonic, dominant, subdominant); knowing the chord
  relationship map allows composers to predict what sound
  comes next; knowing just individual chord structures is
  insufficient for composition
- **Statistical tests** - Statistical test selection involves
  an ecosystem map: parametric vs non-parametric, paired vs
  independent, single vs multiple comparisons; knowing which
  test "comes after" another (ANOVA leads to post-hoc tests)
  is essential to correct analysis
- **Legal reasoning** - Common law doctrines form an ecosystem:
  contract law, tort law, and equity relate through precedent,
  exception, and contrast; knowing the relationships between
  doctrines prevents misapplication of one doctrine where
  another governs

**Industry applications:**
- **Framework design** - Spring's pattern ecosystem (Proxy for
  AOP, Factory for bean creation, Observer for application
  events, Template Method for JdbcTemplate) mirrors the GoF
  ecosystem; understanding the GoF relationships explains
  Spring's internal architecture
- **Architecture review** - Using the distributed pattern
  ecosystem map in architecture reviews predicts the full
  pattern set a reliability requirement implies

---

### 💡 The Surprising Truth

The GoF book was designed so that learning one pattern well
gives partial understanding of several others - this was
intentional. The authors structured the catalog so that reading
Decorator in full depth automatically teaches you the Proxy
contrast, the Composite boundary, and the Chain of Responsibility
relationship. This compositional learning design was embedded
in the Related Patterns sections of each entry. Most engineers
skip Related Patterns entirely, using the catalog as a standalone
reference rather than a networked knowledge system. The engineers
who read every Related Patterns section absorb the ecosystem map
implicitly; those who skip it must learn every pattern cold.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [EXPLAIN] Without reference, name the five contrast pairs
   and articulate the single key distinction between each pair
   in one sentence each
2. [DEBUG] Given a codebase using "Proxy" for objects that add
   caching behavior, identify the misapplication using the
   contrast relationship (Decorator not Proxy) and propose
   correct naming
3. [DECIDE] Given a Composite-based design requirement, predict
   which two companion patterns from the ecosystem map you
   will need before starting implementation, and explain the
   prediction
4. [BUILD] Sketch the class diagram for a Composite + Iterator
   co-occurrence from memory, showing how the Iterator interface
   is implemented by the Composite's container element
5. [EXTEND] Map three GoF ecosystem relationships to the
   distributed pattern ecosystem: identify one composition
   (A uses B), one contrast (same forces, different mechanism),
   and one refinement (simpler version of the same pattern)
   in distributed system patterns

---

### 🧠 Think About This Before We Continue

**Q1.** Strategy and Template Method both address the force pair
"vary the algorithm, keep the invoker stable." Strategy uses
object composition; Template Method uses inheritance. Modern
Java style guides strongly prefer composition over inheritance.
Does this mean Template Method is obsolete? Or are there
specific forces that make Template Method the correct choice
even in modern Java? What evidence would answer this question?

*Hint: Consider the case where the algorithm skeleton itself
must be enforced by the framework (e.g., sort algorithms, HTTP
request handling in a framework base class) - the skeleton
must not be re-implemented by each subclass, only specific
steps varied. Template Method enforces the skeleton at the
language level; Strategy requires the caller to assemble
the right sequence of strategies.*

**Q2.** Given that Composite typically co-occurs with Iterator
and Visitor, design a test: for a randomly selected production
codebase that uses Composite, what percentage do you predict
also uses Iterator in the tree traversal? What percentage use
Visitor for operations? What factors would cause a Composite
implementation to NOT need Iterator or Visitor?

*Hint: Small Composite trees with few operation types might
use simple recursion without formal Iterator; single-operation
Composite might not need Visitor. The ecosystem relationship
is probabilistic (co-occurrence), not mandatory.*

**Q3.** You are designing a rule engine that applies business
rules to loan applications. Rules can be combined: AND, OR, NOT,
and individual rules. The engine must support adding new rules
without modifying existing code. The ecosystem map points to
Composite (for rule trees), Strategy (for individual rule
algorithms), and Specification (for combining rules). Trace
how these three patterns compose in the design: which plays
which role, how they interface, and where the ecosystem map
predicted the composition.

*Hint: Composite handles the tree structure (AND/OR/NOT as
containers, individual rules as leaves). Strategy is implemented
by each leaf rule (the algorithm is "evaluate this rule").
Specification adds the boolean combination logic. The ecosystem
map's composition relationships connect all three.*

---

### 🎯 Interview Deep-Dive

**Q1: Name the three GoF pattern families, their pattern counts,
and give the two most important contrast pair relationships.**

*Why they ask:* Tests whether the candidate has structural
knowledge of the catalog, not just random pattern name recall.

*Strong answer includes:*
- Creational (5): Singleton, Factory Method, Abstract Factory,
  Builder, Prototype
- Structural (7): Adapter, Bridge, Composite, Decorator,
  Facade, Flyweight, Proxy
- Behavioral (11): Chain of Responsibility, Command, Interpreter,
  Iterator, Mediator, Memento, Observer, State, Strategy,
  Template Method, Visitor
- Top contrast pairs: Decorator vs Proxy (structure identical,
  intent opposite), Strategy vs Template Method (same forces,
  different structural level)

**Q2: You are adding a new operation to a Composite tree
structure. You can modify every class in the tree, or you can
add a single Visitor. What determines which approach you choose,
and what does this tell you about the tradeoff between Visitor
and modifying the Composite classes?**

*Why they ask:* Tests whether the candidate understands the
ecosystem relationship between Composite and Visitor and its
trade-off implication.

*Strong answer includes:*
- Visitor adds new operations without modifying existing classes
  (Open/Closed Principle for operations); trade-off: adding a
  new node type requires modifying every Visitor
- Modifying Composite classes adds a new node type easily;
  trade-off: adding a new operation requires modifying every
  class
- The selection criterion: if new operations are more likely
  than new node types, Visitor wins. If new node types are
  more likely than new operations, avoid Visitor.
- This is the fundamental Composite-Visitor trade-off that
  the ecosystem map predicts

**Q3: Give an example from a production system you've worked
on where two patterns from different GoF families were composed
together. How did they interact, and what did the composition
solve that neither pattern solved alone?**

*Why they ask:* Tests practical experience of cross-family
pattern composition rather than theoretical catalog knowledge.

*Strong answer includes:*
- A specific two-pattern composition with named patterns from
  different families: e.g., Factory Method (Creational) +
  Strategy (Behavioral), or Composite (Structural) + Command
  (Behavioral)
- The specific force each pattern addressed independently
- The compositional benefit: what the combined design achieved
  that neither pattern alone could address
- The concrete implementation: which interfaces, which classes,
  which injection points

