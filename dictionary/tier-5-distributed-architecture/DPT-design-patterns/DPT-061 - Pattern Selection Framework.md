---
id: DPT-061
title: Pattern Selection Framework
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-003, DPT-004
used_by: DPT-064, DPT-070, DPT-071
related: DPT-042, DPT-072, SAP-062
tags:
  - pattern
  - advanced
  - architecture
  - bestpractice
  - mental-model
status: complete
version: 3
layout: default
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 61
permalink: /dpt/pattern-selection-framework/
---

# DPT-061 - Pattern Selection Framework

⚡ TL;DR - A structured approach for selecting the right design pattern by matching the problem's forces, constraints, and context to pattern applicability conditions.

| DPT-061 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-003, DPT-004 | |
| **Used by:** | DPT-064, DPT-070, DPT-071 | |
| **Related:** | DPT-042, DPT-072, SAP-062 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every engineer picks patterns based on familiarity or what they learned last. Team A uses Strategy for everything. Team B defaults to Singleton everywhere. Team C applies Observer where Command would be cleaner. The codebase becomes a museum of pattern misuse, shaped by individual preferences rather than problem fit.

**THE BREAKING POINT:**
A senior engineer reviews a PR and says "why did you use Decorator here?" The responding engineer says "because I know Decorator." The resulting design has indirection layers for no benefit, adding complexity that confuses every subsequent contributor. The correct answer — a single composable function — applies no pattern at all.

**THE INVENTION MOMENT:**
The GoF book itself included selection guidance in the "How to Select a Design Pattern" chapter, but it was largely ignored in favour of the pattern catalogue. The real framework emerged from practitioner experience: patterns are solutions to recurring problems in contexts; they exist to resolve conflicting forces. Selecting a pattern requires understanding which forces are present, not just which name matches the surface structure.

**EVOLUTION:**
Modern selection frameworks now account for language features that obsolete certain patterns (Strategy is often just a function in languages with first-class functions), architectural context (container-based patterns differ from in-process patterns), and the cost of indirection (a pattern that adds 2 layers and 3 classes for a problem solvable with 10 lines is the wrong pattern).

---

### 📘 Textbook Definition

A **Pattern Selection Framework** is a systematic approach to choosing a design pattern by: (1) stating the problem in terms of forces and constraints, (2) identifying candidate patterns whose problem statement matches, (3) evaluating fit against the specific context (language, team size, change frequency, performance requirements), and (4) confirming that the pattern's known trade-offs are acceptable given the problem. A pattern is correctly selected when it resolves the primary design tension with the least indirection necessary.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Choosing a design pattern by matching the problem's core forces to the pattern's stated applicability conditions.

> Think of a pattern as a prescription drug. Prescribing it correctly requires matching symptoms to the drug's indicated uses, checking for contraindications, and confirming the dosage fits the patient's context. Prescribing based on name familiarity alone leads to wrong treatment. Pattern selection requires the same diagnostic rigour.

**One insight:** A pattern is never selected by name. It is selected because the forces it resolves are the forces present in your problem. If you cannot name the forces, you are guessing.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every problem has forces: conflicting constraints that must be balanced. Patterns resolve forces — they are not aesthetic choices.
2. Context determines applicability: a pattern that is correct in one language/runtime may be overkill or obsolete in another.
3. No pattern is universally correct. The question is always "what is the cheapest resolution of the forces present?"
4. Applying no pattern is a valid selection when the forces can be resolved with direct code.

**DERIVED DESIGN:**
The selection process: (1) State the problem. (2) Identify the forces (What must vary? What must be stable? What crosses boundaries?). (3) List patterns that address those forces. (4) Select the simplest one whose trade-offs are acceptable. (5) Confirm the pattern adds less complexity than the problem it solves.

**THE TRADE-OFFS:**

**Gain:** Principled selection prevents pattern misuse, reduces unnecessary indirection, and produces designs that are understandable to other engineers who know pattern vocabulary.

**Cost:** Requires upfront analysis of forces — slower than "apply what I know." May produce no pattern selection at all (sometimes the right answer is simple direct code).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Correctly identifying which forces are present in a problem is genuinely hard — it requires experience and domain understanding.

**Accidental:** Over-applying pattern vocabulary ("this needs a Facade") without analysing the forces leads to complexity that the host problem never justified.

---

### 🧪 Thought Experiment

**SETUP:** An engineer needs to implement notification dispatch: one user action triggers multiple handlers (email, Slack, audit log). Two options are debated: Observer vs. Command.

**WHAT HAPPENS WITHOUT A FRAMEWORK:** The engineer picks Observer because "one event, multiple listeners" matches the surface description. The resulting design has a Subject, multiple ConcreteObservers, and registration management. When requirements change (retry logic, rollback), modifying Observer to support it requires significant redesign.

**WHAT HAPPENS WITH A FRAMEWORK:** The engineer uses force analysis. Forces: (a) handlers must be independently replaceable, (b) dispatch must support retry and ordering, (c) dispatch will need audit logging. Command + Queue is a better fit — commands are first-class objects that can be serialised, retried, and logged. Observer is better for synchronous, simple fan-out without state. The Command approach requires less refactoring when requirements evolve.

**THE INSIGHT:** Force analysis reveals that two patterns solving "different handlers respond to one event" have completely different trade-offs. Surface similarity masks structural differences. The framework makes those differences visible before implementation.

---

### 🧠 Mental Model / Analogy

> Pattern selection is like choosing a data structure. You don't pick HashMap because you like it — you pick it because your forces are: O(1) lookup, key-based access, unordered. ArrayList fits different forces: ordered, index-based, fast iteration. Applying the same rigour to patterns — define the access pattern, then select the structure — prevents HashMap-everywhere mistakes.

- **Access pattern** = forces in the problem (what must vary, what must be stable, what must be independent)
- **Data structure choice** = pattern selection (the structure that fits the access pattern best)
- **O(1) lookup requirement** = a specific force that narrows the candidate set
- **Wrong structure = wrong pattern** = when the forces don't match selection criteria

Where this analogy breaks down: data structure selection is more precisely defined (asymptotic complexity is measurable). Pattern trade-offs are contextual and cannot always be reduced to a single dimension.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When choosing how to organise code for a problem, use a framework that asks: "What exactly is the problem? What must be flexible and what must stay the same? What are the best options?" Then pick the simplest option that fits — or none if the problem is simple enough.

**Level 2 - How to use it (junior developer):**
For each design decision: (1) write a single sentence stating the problem ("I need different algorithms selectable at runtime"), (2) list the candidate patterns (Strategy, Command, Factory Method), (3) check the GoF applicability conditions for each against your specific requirements, (4) pick the one with the fewest unneeded trade-offs.

**Level 3 - How it works (mid-level engineer):**
Every pattern resolves a tension between forces. Strategy resolves: algorithms must vary independently of clients, but clients must work uniformly. If that tension isn't present, Strategy adds indirection without benefit. A selection framework makes forces explicit, making it clear which patterns address which tensions.

**Level 4 - Why it was designed this way (senior/staff):**
Modern languages have changed the pattern landscape. In Java 8+, Strategy is often a `Function<T, R>`. In Kotlin/Scala, many structural patterns collapse to data classes and sealed hierarchies. A senior engineer's selection framework includes a "language feature first" check — can this be expressed naturally in the language without a named pattern? If yes, the pattern is unnecessary. The framework exists to prevent over-engineering as much as under-engineering.

**Expert Thinking Cues:**
- If you cannot articulate the forces your pattern resolves, you have not selected it — you have named it.
- The cheapest pattern is always "no pattern" — direct code. Justify every indirection layer.
- Check: does this pattern make the code harder to DELETE when requirements change? If yes, reconsider.

---

### ⚙️ How It Works (Mechanism)

**Pattern Selection Decision Process:**

```
1. STATE THE PROBLEM
   "I need [capability] where [constraint]."
          │
2. IDENTIFY FORCES
   What must vary?
   What must stay stable?
   What crosses a boundary?
          │
3. CANDIDATE PATTERNS
   Filter GoF catalogue by
   matching force descriptions
          │
4. FIT CHECK
   Language features cover this?
   → Use language, not pattern
   Simplest pattern adequate?
   → Select it
   Multiple patterns fit?
   → Select by trade-off priority
          │
5. CONFIRM
   Does this add less complexity
   than the problem has?
   → YES: apply
   → NO: simplify or skip
```

**Force vocabulary quick reference:**

| Force | Suggests |
|---|---|
| Algorithm must vary independently | Strategy |
| Object creation logic must vary | Factory Method / Abstract Factory |
| One-to-many notification | Observer |
| Command-as-object (undo, logging) | Command |
| Reduce interface complexity | Facade |
| Add behaviour without inheritance | Decorator |
| Shared state across instances | Singleton (use sparingly) |
| Handle requests without coupling sender to receiver | Chain of Responsibility |

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Problem statement articulated
          │
Forces identified
(vary/stable/boundary analysis)
          │
Pattern candidate list generated
          │
Language feature check  ← YOU ARE HERE
(does stdlib/language solve this?)
          │
   ┌──────┴──────┐
  YES            NO
   │              │
Use language    Pattern application
   │              │
   └──────┬───────┘
          │
Code review validates
force/pattern alignment
          │
Fitness test: delete test
(is the design easier to change
 because of the pattern?)
```

**FAILURE PATH:**
Pattern applied by recognition ("looks like Observer") → forces not verified → pattern adds indirection that the specific problem does not require → future maintainers confused by unnecessary abstractions → "why is this an AbstractSubjectFactory?" question in every code review.

**WHAT CHANGES AT SCALE:**
Individual pattern decisions scale to architectural conventions. At team level: establish pattern guidelines ("we prefer Composition over Decorator for behaviour extension in this codebase"). At organisation level: pattern misuse becomes a build-time fitness function (ArchUnit rules that prevent known misapplication patterns).

---

### 💻 Code Example

**Prior to framework: pattern chosen by name, forces unverified:**

```java
// BAD: Strategy pattern applied without verifying forces
// Only ONE algorithm ever used in practice - no variation
// needed. Pattern adds three classes for no benefit.
public interface SortStrategy {
    void sort(List<Integer> data);
}
public class BubbleSortStrategy implements SortStrategy {
    @Override
    public void sort(List<Integer> data) {
        Collections.sort(data); // Never changes!
    }
}
public class DataProcessor {
    private SortStrategy strategy;
    public DataProcessor(SortStrategy s) {
        this.strategy = s;
    }
    public void process(List<Integer> data) {
        strategy.sort(data);
    }
}
// Caller: new DataProcessor(new BubbleSortStrategy())
// Why? No other strategy ever exists.
```

```java
// GOOD: Force check first.
// Force: algorithm does NOT vary - one implementation.
// Selection: no pattern needed. Direct call.
public class DataProcessor {
    public void process(List<Integer> data) {
        Collections.sort(data);
    }
}

// GOOD: If the force WAS "algorithm must vary at runtime"
// Java 8+ lambda collapses Strategy to Consumer<List<T>>
public class DataProcessor {
    public void process(
            List<Integer> data,
            Consumer<List<Integer>> sortAlgorithm) {
        sortAlgorithm.accept(data);
    }
}
// Caller:
// processor.process(data, Collections::sort);
// processor.process(data, myCustomSort::apply);
```

**How to test / verify correctness:**
Ask: "If I add a second algorithm variant, which change is smaller — the direct version or the pattern version?" If the answer is "both are trivially easy," the pattern was not justified. Correct pattern selection means the pattern makes the expected change significantly cheaper.

---

### ⚖️ Comparison Table

| Selection Approach | Rigor | Speed | Risk |
|---|---|---|---|
| Force analysis (this framework) | High | Slower | Low |
| GoF intent matching | Medium | Medium | Medium |
| Pattern name recognition | Low | Fast | High (misapplication) |
| No pattern (direct code) | N/A | Fastest | Low if forces are simple |
| Team convention lookup | Medium | Fast | Low if conventions are well-calibrated |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "More patterns = better design" | More patterns = more indirection. The goal is minimum indirection that resolves the forces. Patterns are a cost, justified by the benefit they provide. |
| "I recognise this structure, so that pattern applies" | Pattern recognition from surface structure is the most common source of misuse. Two problems can look structurally similar and require completely different patterns. |
| "Patterns are language-agnostic" | Many GoF patterns encode workarounds for language limitations (Strategy = lack of first-class functions, Singleton = no module-level state). Modern languages make many of them unnecessary. |
| "Using a named pattern makes code self-documenting" | Only if the pattern is correctly applied and the forces are present. A misapplied Observer is harder to understand than no pattern at all. |
| "If in doubt, use the most flexible pattern" | Flexibility has a cost: indirection. Selecting a flexible pattern for a problem that will never flex pays the indirection cost forever. YAGNI applies to patterns too. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Force-blind selection**

**Symptom:** New contributors spend hours understanding "why is there an AbstractHandlerFactory here?" The pattern seems arbitrary.

**Root Cause:** Pattern applied by name recognition, not force analysis. Forces that would justify the pattern are absent.

**Diagnostic:**
```bash
# Code review signal: count "why is this a X?" comments
git log --oneline --all | xargs -I {} \
  git show {}:COMMIT_EDITMSG 2>/dev/null | \
  grep -i "why\|unnecessary\|over-engineered" | wc -l
```

**Fix:**
- BAD: Add a comment "this uses AbstractHandlerFactory for extensibility."
- GOOD: Verify the forces. If algorithm variety is never needed, replace with a direct function. Document the removal ADR.

**Prevention:** Code review checklist item: "Name the force this pattern resolves. If you cannot, question the pattern."

---

**Failure Mode 2: Language-obsolete pattern**

**Symptom:** Java 8+ codebase full of `ConcreteStrategy implements Strategy` single-implementation classes. Build time inflated. IDE navigation confused.

**Root Cause:** Pattern catalogue adopted pre-Java 8. Not revisited after lambdas and method references were introduced.

**Diagnostic:**
```bash
# Find single-implementation interfaces
# (proxy for obsolete patterns)
find src -name "*.java" | xargs grep -l "implements" | \
  while read f; do
    iface=$(grep "implements " $f | \
      sed 's/.*implements //' | tr -d '{')
    count=$(find src -name "*.java" | \
      xargs grep -l "implements $iface" | wc -l)
    [ "$count" -eq 1 ] && echo "$iface: $f"
done
```

**Fix:**
- BAD: Keep the pattern as documentation of intent.
- GOOD: Replace `SortStrategy` interface + single impl with `Consumer<List<T>>`. Remove the dead abstraction.

**Prevention:** Quarterly pattern audit: identify classes that implement interfaces with exactly one implementation. Evaluate whether the interface adds value.

---

**Failure Mode 3: Pattern over-application in distributed context**

**Symptom:** Service-to-service communication wraps every call in a Command object serialised to JSON. Latency overhead is significant. The services are never retried or rolled back.

**Root Cause:** In-process Command pattern applied to network calls without verifying that serialisation/retry/rollback forces are present.

**Diagnostic:**
```bash
# Measure network call overhead before/after
# Compare: direct HTTP call vs Command-wrapped call
curl -w "@curl-format.txt" -s -o /dev/null \
  http://service/endpoint
```

**Fix:**
- BAD: Keep Command objects "for future use" of retry logic.
- GOOD: Replace with direct REST call for synchronous fire-and-forget. Introduce Command/Queue pattern only when retry and ordering forces are confirmed.

**Prevention:** Network boundary is a force multiplier. Every pattern adds latency at the network level. Verify distributed forces separately from in-process forces.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[DPT-001 - What Are Design Patterns and Why They Exist]] - what patterns are
- [[DPT-003 - Pattern vs Anti-Pattern vs Idiom]] - vocabulary for pattern classification
- [[DPT-004 - How to Recognize When a Pattern Applies]] - precursor to systematic selection

**Builds On This (learn these next):**
- [[DPT-064 - Pattern-Driven Architecture Design]] - applying patterns at architectural level
- [[DPT-070 - Pattern-Recognition Mental Model]] - the cognitive model behind selection
- [[DPT-071 - Pattern Trade-off Framing]] - evaluating pattern trade-offs systematically

**Alternatives / Comparisons:**
- [[DPT-042 - Anti-Patterns Overview]] - what happens when selection fails
- [[DPT-072 - Over-Engineering Risk Thinking]] - the cost when patterns are over-applied
- [[SAP-046 - YAGNI (You Aren't Gonna Need It)]] - the principle governing pattern restraint

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ WHAT IT IS    │ Systematic method to match       │
│               │ problem forces to patterns       │
├───────────────┼──────────────────────────────────┤
│ PROBLEM       │ Pattern chosen by name, not fit  │
│               │ adds unjustified indirection     │
├───────────────┼──────────────────────────────────┤
│ KEY INSIGHT   │ Name the forces first.           │
│               │ Pattern names come second.       │
├───────────────┼──────────────────────────────────┤
│ USE WHEN      │ Evaluating which pattern (if any)│
│               │ to apply to a design decision    │
├───────────────┼──────────────────────────────────┤
│ AVOID WHEN    │ Simple problems with one obvious │
│               │ solution -- skip the framework   │
├───────────────┼──────────────────────────────────┤
│ TRADE-OFF     │ Analysis time now vs.            │
│               │ misapplication cost later        │
├───────────────┼──────────────────────────────────┤
│ ONE-LINER     │ Forces first, then pattern name; │
│               │ never the other way around       │
├───────────────┼──────────────────────────────────┤
│ NEXT EXPLORE  │ DPT-071 Pattern Trade-off        │
└─────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Identify the forces before naming the pattern. Forces are what varies, what stays stable, what crosses a boundary.
2. Check if the language itself solves the problem before applying a pattern.
3. "No pattern" is always a valid selection when the forces are simple.

**Interview one-liner:** "Pattern selection is force analysis first — identify what must vary, what must be stable, and what crosses a boundary, then choose the pattern (or no pattern) that resolves those forces with minimum indirection."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Every abstraction resolves a tension by separating what changes from what stays the same. The value of an abstraction is proportional to the frequency of change it hides and inversely proportional to the indirection it adds. This principle applies to design patterns, APIs, microservice boundaries, and database schemas alike.

**Where else this pattern appears:**
- **Data structure selection** - choosing HashMap vs. TreeMap vs. LinkedHashMap requires the same force analysis: access pattern, ordering requirement, insertion frequency.
- **Architecture pattern selection** - choosing event-driven vs. request-response requires force analysis: coupling tolerance, latency SLA, consistency requirements.
- **API design** - choosing REST vs. GraphQL vs. gRPC requires force analysis: client variety, bandwidth constraints, schema evolution frequency.

---

### 💡 The Surprising Truth

The GoF book itself contains a "How to Select a Design Pattern" section that most readers skip entirely. It recommends reading the "Intent" section of all 23 patterns, looking for patterns that address your problem area, and then checking the "Applicability" section for specific conditions. This is force analysis. The GoF authors knew that pattern names would be misapplied if the selection methodology was not explicit — and they were correct. The catalogue became famous; the selection framework remained obscure.

---

### 🧠 Think About This Before We Continue

**Question 1 (Comparison):** Java's `Comparator` functional interface obsoletes the Strategy pattern for comparison logic. But the Abstract Factory pattern has no equivalent language-level replacement in Java. What structural property of Abstract Factory makes it harder to replace with a language feature than Strategy?

*Hint:* Think about what Strategy varies (algorithms) versus what Abstract Factory varies (families of related objects). Does Java 8 have a native concept that represents "a family of related constructors"?

**Question 2 (Scale):** A team has 30 engineers who each independently select patterns for their service modules. After 2 years, the codebase has 12 different patterns being used for "dependency injection" scenarios. How would you establish a selection framework at team scale that reduces inconsistency without becoming a bottleneck?

*Hint:* Think about the difference between a selection framework as individual guidance vs. as team convention. What artifact makes a team convention durable and discoverable?

**Question 3 (Root Cause):** A codebase uses Decorator pattern extensively, but code reviews consistently flag the Decorators as hard to understand. The original forces were valid. Why might a correctly-selected pattern still produce maintainability problems?

*Hint:* Think about the gap between a pattern being technically correct and a pattern being understood by the team using it. What additional condition must be met beyond correctness?

