---
id: DPT-068
title: Pattern Mining and Discovery Research
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-066, DPT-067
used_by: DPT-069
related: DPT-066, DPT-067, DPT-069
tags:
  - concept
  - research
  - advanced
  - pattern-discovery
  - empirical
  - software-engineering-research
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 68
permalink: /technical-mastery/design-patterns/pattern-mining-discovery/
---

⚡ TL;DR - Pattern mining is the empirical research method
of discovering new design patterns by observing recurring
solutions in existing successful software systems and
abstracting the common structure - producing candidate
patterns that can be validated as genuine recurring solutions.

| #68 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-066, DPT-067 | |
| **Used by:** | DPT-069 | |
| **Related:** | DPT-066, DPT-067, DPT-069 | |

---

### 🔥 The Problem This Solves

**WHERE DO PATTERNS COME FROM?**
Engineers learn patterns from books. They apply them.
But who DISCOVERED those patterns? And how can new
patterns be discovered for emerging domains (microservices,
event-driven, serverless) where no book exists yet?

**THE INVENTION ILLUSION:**
Patterns are not invented. Alexander's insight: patterns
are DISCOVERED. They already exist in successful designs
before they are named. The GoF did not invent Decorator
or Observer. They observed Decorator and Observer existing
in many successful designs, abstracted the common structure,
and gave it a name.

**THE PRACTICAL QUESTION:**
"We have a recurring design challenge in our event-driven
microservices. How do we know if we've found a genuine
new pattern or just a local solution?"

Pattern mining provides the methodology: study multiple
successful solutions to the same problem, abstract
the common structure, validate across different systems,
document in formal specification format.

---

### 📘 Textbook Definition

**Pattern Mining and Discovery** is the empirical research
method for identifying new design patterns. It involves:

1. **Observation**: identifying a recurring design challenge
   that appears across multiple independent systems.
2. **Collection**: gathering multiple successful solutions
   to the same challenge from different contexts and
   teams that independently arrived at similar solutions.
3. **Abstraction**: extracting the common structural
   elements from the collected solutions - the parts that
   appear across all successful solutions regardless of
   the implementation details.
4. **Validation**: verifying that the abstracted pattern
   is genuinely recurring (appears in at least 3 different
   independent systems - Alexander's "Rule of Three").
5. **Documentation**: specifying the discovered pattern
   in formal format (GoF or equivalent), ready for
   publication and reuse.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Pattern mining = observe recurring solutions in real
systems, abstract the common structure, validate across
3+ independent systems, document as a named pattern.

**One analogy:**
> Scientific taxonomy (biology) vs software pattern mining.
> Carl Linnaeus classified organisms by observing specimens
> from nature - not by designing new organisms. He identified
> structural similarities across independent specimens
> and abstracted the classification system.
>
> Pattern mining: observe software "specimens" (successful
> codebases) from nature (production systems). Identify
> structural similarities across independent specimens
> (the recurring solution structure). Abstract the taxonomy
> (the pattern specification). Validate with more specimens.
>
> Patterns are discovered in the wild, not invented at a desk.

---

### 🔩 First Principles Explanation

**ALEXANDER'S RULE OF THREE:**
Alexander's original criterion for a pattern: the solution
must appear in at least three independent, successful
systems. "Three" establishes that the pattern is not a
coincidence (one system might solve a problem any way),
not a preference (two systems from the same team might
copy each other), but a genuinely recurring solution
(three independent teams solving the same problem arrived
at the same structure).

This "Rule of Three" is the validation criterion that
distinguishes a pattern from a "clever hack" or "our
team's idiom."

**HOW THE GoF DISCOVERED THEIR PATTERNS:**
The GoF (Gamma, Helm, Johnson, Vlissides) did not sit
in a room and invent patterns. They studied:
- Smalltalk's class library and how it was used
- ET++ (a large Smalltalk application framework)
- HotDraw (a drawing application framework)
- NEXTSTEP frameworks
- Their own design experience

They noticed that the SAME STRUCTURAL SOLUTIONS appeared
independently in multiple frameworks. They abstracted
the common structure and named it. The GoF is a mining
result, not a theoretical invention.

**MODERN PATTERN MINING METHODS:**

**Manual mining (traditional):**
- Read source code of multiple successful systems
- Interview the engineers who designed them
- Abstract the common structure

**Automated mining (emerging):**
- Static analysis tools that detect structural patterns
  in code (AST analysis, dependency graphs)
- Machine learning models trained on successful codebases
  that detect recurring structural motifs
- These tools can identify CANDIDATE patterns that humans
  then validate and specify

---

### 🧪 Thought Experiment

**MINING THE OUTBOX PATTERN:**

Suppose it's 2015. Several engineering teams independently
solving the same problem: "atomic write to DB + guaranteed
delivery of a message to another service."

Team A (Uber): writes to a `pending_events` table in
the same transaction as the business object. A poller
reads and sends events.

Team B (Shopify): writes an `outgoing_messages` table
atomically. A background job processes and delivers them.

Team C (Netflix): writes a `notification_queue` table
as part of each order transaction. An async worker
delivers the notifications.

**The mining researcher observes:**
All three teams independently arrived at the SAME structure:
1. A table in the same DB as the business object
2. Atomically written in the same transaction
3. Processed by a background relay process

The mining abstraction: "Write the message to a local
table atomically. A relay delivers the message asynchronously."

**Validation:** 3+ independent systems. Same structure.
Same forces being resolved (atomicity + delivery guarantee
across service boundary). → Rule of Three satisfied.

**Result:** The Outbox Pattern - a genuine discovered pattern.

---

### 🧠 Mental Model / Analogy

> Pattern mining = the "fossil record" model.
> Paleontologists discover species by studying fossils.
> They don't design new species. They observe what exists
> (fossils), compare specimens from different locations,
> abstract the common structure (species definition),
> and name the species.
>
> Pattern miners observe the "fossil record" of successful
> software systems (open-source code, production codebases,
> published case studies). They compare specimens from
> different teams and contexts. They abstract the common
> structure. They name the pattern.
>
> The pattern existed in the software ecosystem before
> it was named. Naming it makes it teachable, discussable,
> and reusable.

---

### 📶 Gradual Depth - Three Levels

**Level 1 - Recognizing that patterns are discovered:**
Every named pattern was once an unnamed recurring solution.
When your team uses the same design solution repeatedly
across different modules: you may have discovered an
internal pattern. Name it. Document it minimally.
Check if 3+ independent uses exist.

**Level 2 - The Rule of Three in practice:**
A new architectural decision that your team applies once
is a design choice. Applied to two similar problems:
possibly a pattern. Applied to three independent problems
that independently lead to the same structure: candidate
pattern. This heuristic prevents over-generalization
(calling a one-time solution a "pattern").

**Level 3 - Automated pattern detection:**
Research tools like JDeodorant and CodeCity detect
design pattern instances in Java codebases using AST
analysis. These tools detect structural matches against
known pattern templates. They find WHERE patterns are
used, not new patterns. For new pattern discovery,
human abstraction is still required to extract the
invariant structure across multiple candidate instances.

---

### ⚙️ How It Works (Mechanism)

```
Pattern Mining Process
┌─────────────────────────────────────────────────────────┐
│ PHASE 1: OBSERVE                                        │
│   Study multiple successful systems.                   │
│   Identify recurring design challenges and solutions.  │
│                                                         │
│ PHASE 2: COLLECT                                        │
│   Gather 3+ independent systems solving the same       │
│   problem. Document each solution specifically:        │
│   components, interactions, context.                   │
│                                                         │
│ PHASE 3: ABSTRACT                                       │
│   Identify the common structure:                       │
│   - What roles are present in ALL instances?           │
│   - What interactions are present in ALL instances?    │
│   - What context (forces) is present in ALL instances? │
│                                                         │
│ PHASE 4: VALIDATE (Rule of Three)                      │
│   Are 3+ genuinely independent solutions present?      │
│   Does the abstract structure match all instances?     │
│   Are the forces consistently present across instances?│
│                                                         │
│ PHASE 5: DOCUMENT                                       │
│   Write formal pattern specification (GoF format).    │
│   Include: Intent, Applicability, Structure,           │
│   Consequences, Known Uses (the mined instances).     │
│                                                         │
│ PHASE 6: PUBLISH + COMMUNITY VALIDATION                │
│   PLoP (Pattern Languages of Programs) conferences.   │
│   Review by other practitioners.                       │
│   Community applies and provides feedback.             │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Identifying a candidate internal pattern:**

```
OBSERVATION: In a Spring Boot application, three different
  services use a similar structure when handling
  external API calls:

  Service A (PaymentService):
    - Caches the API response for 5 minutes
    - Falls back to a stale cached response if API fails
    - Logs cache hit/miss metrics

  Service B (CurrencyRateService):
    - Caches rates for 1 hour
    - Falls back to last known rates if API fails
    - Logs cache hit/miss metrics

  Service C (AddressValidationService):
    - Caches validation results for 24 hours
    - Falls back to "assumed valid" if API fails
    - Logs cache hit/miss metrics

ABSTRACTION: Common structure across all three:
  1. External API call wrapped in a cache check
  2. Cache miss → call API → store in cache
  3. API failure → return stale cached value (fallback)
  4. Cache metrics instrumentation

CANDIDATE PATTERN: "Resilient Cache"
  Intent: Cache an external API's response;
    serve stale data on failure (availability over
      freshness).
  Forces:
    - External API may be unavailable (resilience need)
    - Fresh data preferred but not critical (availability
      > consistency)
    - Performance: repeated API calls are expensive
  Solution: Cache-aside with stale-on-failure fallback.

RULE OF THREE: 3 independent services independently arrived
  at this same structure. → Validate for Rule of Three.

NEXT STEP: Document as a formal pattern.
  Check PLoP proceedings: is this pattern already named?
  ("Cache-Aside" Pattern exists in cloud patterns catalog)
  → This is a variation of an existing pattern (stale
    fallback).
  Document as "Cache-Aside with Stale Fallback" variant.
```

---

### ⚖️ Pattern Discovery vs Pattern Invention

| Aspect | Discovery (correct) | Invention (incorrect) |
|---|---|---|
| Basis | Observing existing solutions | Designing a new solution |
| Validation | Rule of Three (independent occurrences) | Theoretical justification |
| Risk | May not find patterns where none exist | May create patterns nobody needs |
| Output | Catalog of proven, reusable solutions | Theoretical pattern taxonomy |
| GoF approach | Discovery | N/A (GoF used discovery) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Patterns are invented by clever engineers | Patterns are DISCOVERED by observing what already works in successful systems. The GoF, Alexander, and every pattern author was primarily an observer, not an inventor |
| Any recurring solution is a pattern | A recurring solution in ONE team's codebase is a convention, not a pattern. Rule of Three: 3+ INDEPENDENT teams/systems that independently arrived at the same solution. The independence is essential |
| Pattern mining is only for academics | Practical engineering teams can mine internal patterns. When 3+ modules independently use the same design structure: name it, document it minimally, use it intentionally. Internal pattern libraries reduce design inconsistency |
| Automated tools can fully replace human pattern mining | Automated tools detect STRUCTURAL matches against known patterns. They cannot discover NEW patterns because they cannot abstract beyond their training data. Human observation and abstraction are required for genuinely new patterns |

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ CORE INSIGHT │ Patterns are DISCOVERED (observed in     │
│              │ real systems), not INVENTED (designed    │
│              │ from theory)                            │
├──────────────┼──────────────────────────────────────────┤
│ RULE OF THREE│ 3+ INDEPENDENT systems with the same    │
│              │ structure → valid candidate pattern      │
├──────────────┼──────────────────────────────────────────┤
│ PROCESS      │ Observe → Collect → Abstract → Validate  │
│              │ → Document → Publish                    │
├──────────────┼──────────────────────────────────────────┤
│ CONFERENCE   │ PLoP (Pattern Languages of Programs):    │
│              │ the primary venue for pattern research   │
├──────────────┼──────────────────────────────────────────┤
│ INTERNAL USE │ 3+ modules with the same structure =     │
│              │ name it, document it, use it as a team  │
│              │ pattern vocabulary                      │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-069: Meta-Pattern Design             │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Patterns are discovered, not invented. The GoF observed
   the same structural solutions appearing independently
   in multiple frameworks, abstracted the common structure,
   and named it. This is discovery, not invention.
2. Rule of Three: a pattern requires 3+ INDEPENDENT
   occurrences in different systems (not 3 uses in the
   same team's codebase). Independence validates that
   the pattern is genuinely recurring, not a team idiom.
3. Internal pattern mining: when your team independently
   uses the same structure in 3+ modules - name it,
   document it minimally (Intent + Applicability +
   Structure). Internal pattern vocabulary reduces
   design inconsistency as the team grows.

