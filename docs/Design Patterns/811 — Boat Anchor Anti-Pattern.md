---
layout: default
title: "Boat Anchor Anti-Pattern"
parent: "Design Patterns"
nav_order: 811
permalink: /design-patterns/boat-anchor-anti-pattern/
number: "0811"
category: Design Patterns
difficulty: ★★☆
depends_on: Anti-Patterns Overview, YAGNI, Technical Debt, Refactoring
used_by: Code Quality, Technical Debt, Code Review Best Practices
related: Lava Flow Anti-Pattern, Anti-Patterns Overview, Dead Code, Premature Optimization
tags:
  - antipattern
  - pattern
  - intermediate
  - bestpractice
---

# 811 — Boat Anchor Anti-Pattern

⚡ TL;DR — A boat anchor is code or a component kept in the codebase "just in case it's useful someday" — it adds weight without providing value, dragging the codebase down like an anchor overboard.

| #811 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Anti-Patterns Overview, YAGNI, Technical Debt, Refactoring | |
| **Used by:** | Code Quality, Technical Debt, Code Review Best Practices | |
| **Related:** | Lava Flow Anti-Pattern, Anti-Patterns Overview, Dead Code, Premature Optimization | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A developer finishes a large feature refactoring. The old implementation is well-tested and thoroughly understood. "We might need it again," they think, so they keep it. They rename the class `LegacyOrderProcessor` and leave it in the codebase. Next month, a new team member sees it and spends an afternoon understanding it. Three months later it is imported in a new feature "just to compare approaches." Six months later nobody is sure if it is still needed.

**THE BREAKING POINT:**
The "just in case" justification never has an expiry date. The component grows stale while remaining visible. Every developer touching adjacent code must understand whether the boat anchor is part of the system or not. Removing it later becomes more expensive because it has accumulated implied context and implied callers.

**THE INVENTION MOMENT:**
This is exactly why the Boat Anchor Anti-Pattern was named — a boat anchor at sea drags a ship down without providing navigation, propulsion, or any active value. Code kept "just in case" does the same: it consumes attention, slows development, and provides no current value.

---

### 📘 Textbook Definition

The Boat Anchor anti-pattern describes the practice of keeping a component, class, module, or library in a project even though it serves no current purpose, on the rationale that it may become useful in the future. Unlike the Lava Flow anti-pattern (where code is kept due to fear of removing unknown code), Boat Anchors are kept by conscious decision. The "just in case" justification is the defining characteristic. The result is a growing collection of inactive components that increase cognitive and maintenance overhead without providing any value while active.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Code kept "just in case it's useful someday" — adding weight with no current value.

**One analogy:**
> A fisherman keeps an old engine on his boat because "it might be useful someday." The engine takes up half the deck. Every trip, he navigates around it. The engine has not run in two years. It requires maintenance to prevent deterioration. It blocks the space needed for the equipment he actually uses. That engine is the boat anchor. Its presence costs more than its potential future value.

**One insight:**
The boat anchor's justification is always future value, never present value. The correct question is not "might we need this?" but "do we need it now?" If no: version control preserves it forever. You can always retrieve it from git history. The codebase does not need to carry it while it is unused.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A boat anchor has no current callers and provides no current value — it is retained solely for hypothetical future use.
2. The "just in case" justification is subjective and open-ended — unlike a formal deprecation timeline, "might be useful" has no expiry.
3. Boat anchors accumulate — once the pattern is established, every developer adds their own "just in case" components, compounding the problem.

**DERIVED DESIGN:**
The root cause is the sunk cost fallacy applied to code: "I spent effort writing this, so I should not delete it." Combined with version control FOMO: "If I delete it, I'll lose it forever." Both are false: (1) the future value of the boat anchor is at best equal to the re-implementation cost, not the original development cost; (2) git history preserves deleted code indefinitely — `git log -- path/to/deleted/file.java` retrieves the last version instantly.

The refactored solution is the YAGNI principle: "You Aren't Gonna Need It." If the component is not needed today, it does not belong in the codebase today. Delete it. Retrieve it from git if the hypothetical future actually arrives.

**THE TRADE-OFFS:**
**Gain of keeping:** Potential faster future implementation if the use case arrives.
**Cost of keeping:** Cognitive load on every developer; maintenance overhead; risk of accidental activation; signal-to-noise ratio reduced.

---

### 🧪 Thought Experiment

**SETUP:**
A team ships a new recommendation engine that replaces the old one. The old engine is working code — well-tested, well-documented. They decide to keep it "just in case."

**WHAT HAPPENS keeping the boat anchor:**
Month 1: New developers see two recommendation engines. They spend a day understanding which one is active. Month 3: A bug in the new engine triggers the question "should we fall back to the old one?" — three hours of discussion about whether the old engine is still production-ready. Month 6: A junior developer mistakenly wires the new feature to the old engine. Production serves suboptimal recommendations for two weeks undetected.

**WHAT HAPPENS applying YAGNI:**
The old engine is deleted at the time of replacement. Its implementation is preserved in git (tag: `rec-engine-v1`). Month 1: New developers see one recommendation engine. Month 3: Bug in new engine → decision: fix or retrieve v1 from git (5 minutes to retrieve). Month 6: No accidental wiring possible — old engine does not exist in the live codebase.

**THE INSIGHT:**
Git history is the archive. The codebase is the active working set. Components not in the active working set belong in the archive, not the codebase.

---

### 🧠 Mental Model / Analogy

> Think of your IDE in terms of open tabs. A developer with 47 open tabs that they "might need later" spends more time navigating tabs than coding. The useful tabs are buried among the "just in case" ones. The mental model for Boat Anchors is the same: every unused component in the codebase is an open tab that clutters the workspace, obscures the active files, and demands occasional attention without contributing to the current task.

- "47 open tabs" → the accumulation of boat anchor components
- "Useful tab buried in the list" → active code obscured by boat anchor noise
- "Closing a tab you'll never need again" → deleting a boat anchor (knowing git preserves it)
- "Reopening a closed tab if needed" → `git log -- path/to/deleted` + `git checkout`

Where this analogy breaks down: closing a browser tab is reversible in seconds. In very large codebases, deleted code may be harder to re-integrate due to dependency drift. This is a reason to delete boat anchors sooner rather than later, not a reason to keep them.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A boat anchor is code nobody uses kept in the project "just in case." Every developer who reads the code must understand it exists and figure out it is unused. It takes up time and attention without giving anything back.

**Level 2 — How to use it (junior developer):**
Before keeping old code "just in case," ask: what specific future scenario would require this code? If you can describe it concretely, creates a ticket for the future scenario and delete the code; the ticket ensures it won't be forgotten. If you cannot describe the scenario concretely — delete it unconditionally. Remember: `git log --all -- src/OldEngine.java` retrieves deleted files. You are not losing the code, just removing it from active view.

**Level 3 — How it works (mid-level engineer):**
Boat anchors are distinct from Lava Flow (Lava Flow: unknown, feared code; Boat Anchor: known, consciously kept code). Both produce the same outcome — inactive code in the active codebase — but the remediation differs. Boat Anchors require a cultural norm: "if it is not needed today, it goes to git history." The mechanical fix is: create a deletion checklist in code review. When deleting a component, also check: docs referencing it, tests importing it, configuration files mentioning it, and ADRs that assume it exists.

**Level 4 — Why it was designed this way (senior/staff):**
At the organisational level, boat anchors indicate an engineering culture that does not trust its version control. When developers do not believe they can safely retrieve deleted code from git, they compensate by keeping everything in the active codebase as insurance. The systemic fix is twofold: (1) improve git literacy so developers know how to retrieve deleted code; (2) establish a formal "deletion as code maintenance" practice — planned sprints where dead, superseded, or anchor code is identified and removed with the same rigour as new feature work. Healthy codebases have deletion velocity close to addition velocity over time. An always-growing codebase is an unhealthy signal.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────┐
│  BOAT ANCHOR ACCUMULATION PATTERN                │
│                                                  │
│  Quarter 1: Old feature superseded              │
│    Developer keeps old code "just in case"       │
│         ↓                                        │
│  Quarter 2: Another feature superseded          │
│    Another developer does the same              │
│         ↓                                        │
│  Quarter 3: New developer joins                  │
│    "Why are there two recommendation engines?"   │
│    "What is PaymentProcessorV1 for?"             │
│    Onboarding takes 1.5x expected time.          │
│         ↓                                        │
│  Quarter 4-8: Boat anchors accumulate           │
│    20% of codebase is inactive components        │
│    Code reviews must verify: is this active?    │
│    New features add workarounds "just in case"  │
└──────────────────────────────────────────────────┘
```

**Finding and removing boat anchors:**

```bash
# Step 1: Find unused classes (Java — no callers)
# IntelliJ: Analyze → Run Inspection By Name...
# → "Unused declaration" → scope: Whole project

# Step 2: Check coverage (JaCoCo)
mvn jacoco:report
# Classes with 0% line coverage = candidates

# Step 3: Check git recency
git log --since="12 months ago" -- src/LegacyEngine/ \
  | wc -l
# Zero commits in 12 months + zero coverage = anchor

# Step 4: Archive in git (create a tag before deletion)
git tag legacy/recommendation-engine-v1
git push origin legacy/recommendation-engine-v1

# Step 5: Delete
git rm -r src/LegacyRecommendationEngine/
git commit -m "chore: remove legacy-recommendation-engine
# Now safely archived as tag: legacy/rec-engine-v1
# Retrieve with: git show legacy/rec-engine-v1:...
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (boat anchor present):**
```
Developer opens codebase [← EXTRA COGNITIVE LOAD HERE]
  → Sees two implementations of same concept
  → Must determine which is active
  → Reads boat anchor to understand context
  → Concludes it is inactive
  → Moves on — 30 minutes spent
  → Next developer: same 30 minutes
```

**NORMAL FLOW (boat anchor removed):**
```
Developer opens codebase
  → Sees one implementation of each concept
  → No disambiguation needed
  → Productive immediately
  → Legacy code accessible via: git show legacy/engine-v1
```

**FAILURE PATH:**
```
Boat anchor accidentally activated
  (misconfiguration, reflection lookup, spring scan)
  → Two implementations both active
  → Undefined behaviour for shared state
  → Incident: which implementation "won"?
  → Root cause: "we didn't know it was still there"
```

**WHAT CHANGES AT SCALE:**
At 5 engineers, boat anchors are annoying but visible. At 50 engineers, they accumulate to 15-20% of the codebase being inactive. At 500 engineers, boat anchors span entire services — "shadow services" that run but serve no users. Audit sprints to identify and retire shadow services are a regular cost at large organisations.

---

### 💻 Code Example

**Example 1 — BAD: Boat anchor kept "just in case":**

```java
// BAD: LegacyRecommendationEngine kept "just in case"
// Last used: 14 months ago. No callers. Tests pass
// because they test the class in isolation — not because
// it is integrated anywhere.

/**
 * @deprecated - superseded by MLRecommendationEngine
 * Keeping for potential fallback use.
 * TODO: evaluate before deleting (added 14 months ago)
 */
public class LegacyRecommendationEngine
        implements RecommendationEngine {
    // 340 lines of logic nobody calls
}
```

**Example 2 — GOOD: Archive in git, delete from codebase:**

```bash
# Before deletion: create a permanent git reference
git tag archive/legacy-rec-engine-v1 HEAD
git push origin archive/legacy-rec-engine-v1
echo "LegacyRecommendationEngine archived as \
  tag: archive/legacy-rec-engine-v1" >> docs/ADR-108-rec-engine.md

# Delete from active codebase
git rm src/recommendation/LegacyRecommendationEngine.java
git commit -m \
  "chore: remove LegacyRecommendationEngine (archived in \
  tag archive/legacy-rec-engine-v1)"
```

**Example 3 — Prevention: Code review checklist item:**

```markdown
# Pull Request Checklist (Code Review)

## When replacing an existing implementation:
- [ ] Old implementation is no longer referenced from
      any active code path (check Analyze → Find Usages)
- [ ] Old implementation is archived in a git tag
      if there is any chance of future reference:
      `git tag archive/<component>-<date>`
- [ ] Old implementation is DELETED from the codebase
      (`git rm`)
- [ ] Documentation/ADR updated to note the replacement
- [ ] "Just in case" comments in PR are not accepted —
      either archive + delete, or add a concrete ticket
```

---

### ⚖️ Comparison Table

| Code State | Intent for Keeping | Removal Risk | Recommended Action |
|---|---|---|---|
| **Boat Anchor** | "Might be useful" (hypothetical) | Low | Archive in git tag → delete |
| Lava Flow | Fear (unknown purpose) | Medium | Investigate → trace → delete |
| Deprecated with date | Scheduled for removal | Low | Remove on date |
| Active with low usage | Serves edge case users | Medium | Keep, document, monitor |

How to choose: if the justification for keeping is hypothetical ("might be useful"), treat as boat anchor. If the justification is documented uncertainty ("might be called by X"), treat as lava flow. Both are candidates for removal — the process differs.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Deleting code means losing it forever | Git history preserves deleted code indefinitely. `git log --diff-filter=D --name-only` lists deleted files. `git checkout <commit> -- file` restores them |
| Boat anchor and lava flow are the same | Boat anchor: consciously kept "just in case." Lava flow: kept because of fear of unknown consequences. Different motivation, slightly different removal approach |
| Deprecated annotation means it's scheduled for deletion | `@Deprecated` with no timeline and no active deletion effort is itself a boat anchor |
| Keeping the old implementation is a safety net | The safety net is your test suite and version control. Dead code in the active codebase is not a safety net — it is a distraction |

---

### 🚨 Failure Modes & Diagnosis

**1. Boat Anchor Accidentally Activated via Component Scan**

**Symptom:** Two implementations of the same interface both register as Spring beans; `NoUniqueBeanDefinitionException` or unexpected behaviour as the wrong bean is injected.

**Root Cause:** Boat anchor class is a Spring-annotated component still within the component scan path. When kept "just in case," its annotations were not removed.

**Diagnostic:**
```bash
# Spring: list all beans registered:
curl -s http://localhost:8080/actuator/beans \
  | jq '.contexts[].beans | keys[]' \
  | grep -i "legacy\|old\|v1\|backup"
# Any legacy bean appearing = boat anchor activated
```

**Fix:** Immediately disable the boat anchor (`@Profile("disabled")` or remove `@Component`). Then delete it.

**Prevention:** Before deleting a Spring component, remove all Spring annotations (`@Service`, `@Component`, `@Bean`) first. Component scan does not care about "just in case" intent.

---

**2. Boat Anchor Consumed by New Developer as Canonical Implementation**

**Symptom:** A new developer builds a feature using the boat anchor class, not realising it is inactive. Feature ships with incorrect integration.

**Root Cause:** Boat anchor is visible, documented, and looks like production code. Without "active/inactive" signals, new developers cannot distinguish it.

**Diagnostic:**
```bash
# Find imports of the anchor class:
grep -r "import.*LegacyEngine\|import.*OldProcessor" \
  src/ --include="*.java"
# Recent additions (last 2 months) to this list = 
# new developers using the anchor
```

**Fix:** Remove the feature integration with the anchor class. Migrate it to the active implementation. Delete the anchor immediately — delay increases the cost.

**Prevention:** Boat anchors are visible — they attract developers. The only reliable prevention is deletion.

---

**3. "TODO: evaluate before removing" Comments Persist Indefinitely**

**Symptom:** Code has `// TODO: remove if not needed` comments that are 12+ months old. The TODOs are never acted upon.

**Root Cause:** TODOs without ownership or expiry dates are never actioned. They are boat anchors with an additional layer of pretend-intention.

**Diagnostic:**
```bash
# Find old TODOs about removal:
git log --format="%ai %H" -- src/ \
  | while read date hash; do
    git show $hash | grep -l "TODO.*remove\|TODO.*delete" \
    && echo $date $hash
  done 2>/dev/null | head -20
# TODOs from > 6 months ago = boat anchor with dead TODO
```

**Fix:** Convert every "TODO: remove" to either: (a) a concrete ticket with owner and deadline, or (b) immediate deletion.

**Prevention:** Ban "TODO: remove/delete/evaluate" comments without an attached ticket number. Code review rejects undated removal TODOs.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Anti-Patterns Overview` — boat anchor is a specific named anti-pattern; the general catalogue provides context for why naming it matters
- `YAGNI (You Aren't Gonna Need It)` — the design principle that directly prevents boat anchors: only build and keep what is needed now

**Builds On This (learn these next):**
- `Technical Debt` — boat anchors are deliberate technical debt: a conscious choice to keep inactive code that accumulates interest with every developer hour spent on it
- `Dead Code` — the broader category that includes boat anchors, lava flow, and other forms of inactive code

**Alternatives / Comparisons:**
- `Lava Flow Anti-Pattern` — the closely related pattern; both describe inactive code in the codebase, but lava flow arises from fear of the unknown, boat anchor from conscious "just in case" retention
- `Premature Optimization` — a related pattern of adding complexity (in performance code) for hypothetical future needs; boat anchor does the same for unused features

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Code kept "just in case" with no current  │
│              │ callers or active purpose                 │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Every developer must understand and route │
│ SOLVES       │ around inactive components; may activate  │
│              │ accidentally                              │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Git history IS the archive. The codebase  │
│              │ is the active working set. Dead code      │
│              │ belongs in history, not both.             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Never — delete unused code;               │
│              │ archive in git tag if uncertain           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Deleting without archiving when there is  │
│              │ genuine (non-hypothetical) future need    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ "Might need it" hypothetical gain vs.     │
│              │ definite ongoing cognitive and maintenance│
│              │ cost                                      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A boat anchor on a boat provides no      │
│              │  propulsion — only drag."                 │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ YAGNI → Lava Flow → Dead Code →           │
│              │ Git Tags for archiving                    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A developer argues: "We're replacing our PostgreSQL-backed session store with a Redis-backed one. I want to keep the PostgreSQL implementation for 90 days as a fallback in case Redis has issues." A tech lead says: "This is a boat anchor — delete it, we have git." The developer counters: "A real fallback mechanism is different from a boat anchor — it is actively planned for use." What criteria distinguish a legitimate fallback implementation (that should remain in code) from a boat anchor? Design the conditions under which the PostgreSQL implementation should be kept vs. deleted.

**Q2.** Your team has a rule: "All code kept 'just in case' must be in a git tag, not in the active codebase." A manager says: "This creates risk — what if we need to roll back quickly and the git tag retrieval takes time?" Evaluate this risk. How does retrieval time from a git tag compare practically to the debugging cost of a production incident caused by a boat anchor accidentally activating? What process would make tag retrieval fast enough to be a reliable operational fallback?

