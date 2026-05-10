---
id: DPT-071
title: Pattern Trade-off Framing
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-070, DPT-061, DPT-003
used_by:
related: DPT-072, SAP-062, DPT-064
tags:
  - pattern
  - advanced
  - tradeoff
  - architecture
  - mental-model
status: complete
version: 2
layout: default
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 71
permalink: /dpt/pattern-trade-off-framing/
---

# DPT-071 - Pattern Trade-off Framing

⚡ TL;DR - Pattern trade-off framing is the structured analysis of a pattern's costs, benefits, and constraints relative to specific context — enabling rational pattern selection and rejection, not just pattern recognition.

| DPT-071 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-070, DPT-061, DPT-003 | |
| **Related:** | DPT-072, SAP-062, DPT-064 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Engineers select patterns based on recognition alone — "this looks like Observer" — without evaluating whether the Observer pattern's specific trade-offs are acceptable in this context. A team adopts CQRS for a low-traffic internal tool because they recognise the read/write separation concern, without evaluating whether the two-model maintenance overhead is justified by the actual traffic shape. The pattern is correct in principle and wrong in practice — because the trade-offs were never evaluated against the specific context.

**THE BREAKING POINT:**
A team implements Event Sourcing for a user profile service. The pattern fits functionally — the Forces are present (immutable history required, temporal queries needed). But the trade-off evaluation was never done: the read model must be derived from event replay across a potentially large event store. Six months in, the event store has 2M events per user. Read performance degrades. Rebuilding a user's current state requires replaying all events. A simple relational model with an audit log table would have satisfied all the original forces at 5% of the operational complexity.

**THE INVENTION MOMENT:**
The GoF "Consequences" section was designed for exactly this purpose: to document what each pattern enables and what it costs, so engineers can evaluate fit before applying. Architecture Tradeoff Analysis Method (ATAM) by the SEI formalised this at system level: for each architectural pattern, enumerate quality attribute scenarios (what does this enable?) and risks (what does this cost?). The trade-off framing brings this rigour to individual pattern decisions.

**EVOLUTION:**
Modern pattern trade-off framing has evolved to include: operational costs (deployment complexity, monitoring overhead), team capability costs (the team must understand the pattern to maintain systems that use it), and evolution costs (how hard is it to change or remove this pattern if requirements change?). Pure structural trade-offs are necessary but not sufficient — a pattern with high team understanding cost may be wrong even when its structural trade-offs are positive.

---

### 📘 Textbook Definition

**Pattern trade-off framing** is the structured evaluation of a pattern's trade-offs — benefits, costs, constraints, and risks — against the specific forces, team capabilities, and context of a design decision. It transforms "does this pattern fit?" from a binary yes/no into a multi-dimensional evaluation: do the benefits outweigh the costs given these forces, this team, this operational context, and this expected evolution trajectory? A well-framed trade-off analysis produces a decision that is documented, defensible, and revisable as context changes.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Every pattern has a price — the trade-off framing ensures you know what you are paying and whether it is worth it.

> Think of buying insurance. You could buy every available insurance policy (all applicable patterns), but the premium cost would be excessive relative to the risk you are insuring against. Pattern trade-off framing is actuarial analysis for design patterns: which risks are real in this context, what is the premium (complexity cost), and does the risk reduction justify the premium?

**One insight:** A pattern can be structurally correct (forces match) and economically wrong (costs exceed benefits in this specific context). Trade-off framing catches the latter, which pure pattern recognition does not.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every pattern has trade-offs — no pattern provides benefits without costs. Trade-off framing makes costs explicit before commitment.
2. Trade-offs are context-dependent — the same pattern costs more in some contexts than others (CQRS at 10K requests/day vs. 10M requests/day has different economic justification).
3. The cost of a pattern includes: structural complexity (more classes, more abstraction layers), operational complexity (more infrastructure, more monitoring), and team complexity (more knowledge required to maintain correctly).
4. Reversibility is a trade-off dimension: some patterns are easy to add later; others are easy to add but hard to remove once implemented.

**DERIVED DESIGN:**
Pattern trade-off evaluation framework:
```
1. Structural benefit: what does this pattern enable?
2. Structural cost: what indirection/complexity does it add?
3. Operational benefit: what operational capability does it provide?
4. Operational cost: what runtime/infrastructure overhead?
5. Team benefit: what does knowing this pattern enable?
6. Team cost: what does this pattern require teams to understand?
7. Evolution benefit: how easy does this make future changes?
8. Evolution cost: how hard is this pattern to change or remove?
```

**THE TRADE-OFFS:**

**Gain:** Rational selection decisions that account for the full cost of a pattern, not just its structural correctness. Documented rationale that enables future review when context changes.

**Cost:** Trade-off framing adds 30-60 minutes to a design decision. For decisions already clearly correct or clearly wrong, this overhead provides no benefit.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** The question "is the benefit of this pattern worth its cost in this specific context?" is genuinely hard and requires domain-specific judgement. No framework eliminates this.

**Accidental:** Multi-spreadsheet trade-off analysis, formal weighting of multiple quality attributes, and committee-level sign-off processes add ceremony that exceeds the value of the analysis for most design decisions.

---

### 🧪 Thought Experiment

**SETUP:** A 5-person team is building a new internal reporting tool. Traffic: 500 queries/day. The team lead proposes CQRS + Event Sourcing because "we need an audit log and the data model will evolve."

**WITHOUT TRADE-OFF FRAMING:**
Team implements CQRS + Event Sourcing. Separate command and query models. Kafka for event streaming. Event store with snapshot strategy for performance. 3 months to implement instead of 3 weeks. Service has 4 infrastructure components (DB, event store, Kafka, read replica). 5 engineers must now understand Event Sourcing to maintain it. For 500 queries/day.

**WITH TRADE-OFF FRAMING:**
Forces evaluation: audit log needed (YES), temporal queries needed (NO), read >3x write (NO: 500 queries/day read ≈ write frequency), team familiar with ES (NO: 2 of 5 engineers know it).

Trade-off calculation: Event Sourcing benefit = audit log, potential temporal queries. Cost = 3-month implementation vs. 3 weeks, 4 infrastructure components, team knowledge requirement. Alternative: relational DB with event log table + CRUD API gets 80% of the benefit at 10% of the cost.

Decision: Simple CRUD + audit log table. Document the forces and the reason ES was rejected. Revisit if temporal query requirement materialises or read traffic reaches 100K/day.

**THE INSIGHT:** The forces were partially present. Trade-off framing revealed the cost exceeded the benefit in this specific context. The forces analysis (pattern recognition) and the trade-off analysis are complementary, not substitutable.

---

### 🧠 Mental Model / Analogy

> Pattern trade-off framing is like cost-benefit analysis in engineering. When designing a bridge, an engineer does not specify the maximum-strength steel for all components by default — they calculate the loads, specify minimum acceptable strength with appropriate safety factors, and choose the material whose cost/performance profile matches the actual load profile. Over-specifying materials for a footbridge using Olympic-arena specifications is waste. Under-specifying them for a highway bridge is danger. Trade-off framing applies the same engineering judgement to pattern selection: match the specification to the actual load.

- **Bridge load** = actual forces present in the design problem
- **Material specification** = pattern selection (each pattern has a cost-performance profile)
- **Over-specifying materials** = applying heavyweight patterns (CQRS, ES) to low-load problems
- **Under-specifying materials** = applying no pattern to high-load problems (no resilience patterns on critical paths)
- **Safety factor** = reversibility margin (how easy is it to upgrade or downgrade the pattern later?)

Where this analogy breaks down: bridge loads can be precisely calculated. Design problem forces are often ambiguous and evolving — trade-off analysis must account for uncertainty in the forces themselves.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Every design pattern is a tool, and every tool comes with costs: complexity, required knowledge, maintenance overhead. Pattern trade-off framing is asking "is this tool the right one for this job?" rather than "is this the right hammer category?" You might need a hammer — but do you need a framing nailer or a finish nailer? The trade-off framing helps you choose the right scale.

**Level 2 - How to use it (junior developer):**
Before applying a pattern, ask four questions: (1) What does this pattern enable that I cannot get more simply? (2) What complexity does it add? (3) Can my team maintain it long-term? (4) If requirements change, how easy is it to remove or replace? If you cannot answer all four positively, reconsider.

**Level 3 - How it works (mid-level engineer):**
Trade-off framing evaluates three cost categories: (a) Structural costs — additional classes, indirection layers, abstractions that every engineer must understand to contribute to the codebase. (b) Operational costs — additional infrastructure components, monitoring requirements, failure modes introduced by the pattern. (c) Team knowledge costs — the pattern is only maintained correctly if all team members understand it; team turnover causes capability gaps.

**Level 4 - Why it was designed this way (senior/staff):**
Trade-off framing operationalises the principle that design decisions are economic decisions. A pattern that costs 2 weeks to implement and 2 hours/week to maintain is worth 104 hours per engineer per year in carry cost. If the benefit of the pattern is 30 minutes/week of saved debugging, the trade-off is negative. Staff engineers evaluate patterns this way: "what is the carrying cost, what is the ongoing benefit, and when does the benefit exceed the carrying cost?" For patterns with negative near-term trade-offs, the justification must come from future context (expected traffic, expected team growth, expected audit requirements).

**Expert Thinking Cues:**
- Trade-off framing prevents "we might need it" arguments: the only valid forward-looking justification is when the force is expected to materialise and the cost of retrofitting is higher than the cost of proactive implementation.
- Reversibility is underweighted in most trade-off analyses. A pattern that is cheap to add but expensive to remove (Event Sourcing) requires a higher benefit threshold than a pattern that is cheap to add and cheap to remove.
- Team knowledge cost scales with team turnover. A pattern that requires deep expertise and has a 30% annual turnover rate will have its knowledge continuously degraded without deliberate maintenance.

---

### ⚙️ How It Works (Mechanism)

**Trade-off Evaluation Matrix:**

```
DIMENSION         BENEFIT          COST
─────────────────────────────────────────
Structural        [what it enables] [indirection added]
Operational       [runtime benefit] [infra overhead]
Team              [design clarity]  [knowledge required]
Evolution         [change ease]     [removal cost]
─────────────────────────────────────────
Context factors:
  Expected traffic scale?
  Team familiarity with pattern?
  Probability force will grow?
  Reversibility if wrong?
```

**Trade-off breakeven analysis:**

```
Implementation Cost (hours):    [I]
Carrying Cost (hours/month):    [C]
Benefit (hours saved/month):    [B]

Monthly ROI = B - C
Payback Period = I / (B - C)

If payback period > expected system lifetime:
  → trade-off is negative, do not apply
If B < C:
  → carrying cost exceeds benefit, do not apply
If B > C and payback period < system lifetime:
  → trade-off is positive, apply with documentation
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Pattern recognised as applicable
          │
Trade-off framing initiated:
  List structural benefits
  List structural costs
  Assess operational impact
  Assess team capability match
          │
Context-specific calibration ← YOU ARE HERE
  (traffic, team size, turnover,
   evolution probability)
          │
Breakeven analysis
  (implementation cost vs. net benefit)
          │
   ┌──────┴──────┐
POSITIVE       NEGATIVE
ROI            ROI
   │              │
Apply with     Reject with
ADR documenting documented rationale
rationale      (and trigger for reconsideration)
          │
Periodic review
  (forces changed? recalibrate)
```

**FAILURE PATH:**
Pattern recognised → applied immediately → trade-off never framed → operational costs unexpected → team cannot maintain correctly → pattern becomes technical debt → removal requires major refactoring.

**WHAT CHANGES AT SCALE:**
At component level: individual engineer's trade-off judgement. At service level: trade-off framing is part of ADR documentation. At organisation level: architectural fitness functions detect whether the pattern is delivering its expected benefits (monitoring trade-off ROI, not just conformance).

---

### 💻 Code Example

**CQRS trade-off framing decision:**

```java
// BAD: CQRS applied without trade-off framing
// Low-traffic internal tool, 500 queries/day
// Two separate models maintained for no operational benefit

// Write model
@Entity
public class UserProfile {
    private Long id;
    private String email;
    private String displayName;
    // ... DDD aggregate with command handling
}

// Read model (separate - CQRS requirement)
@Entity
public class UserProfileView {
    private Long id;
    private String email;
    private String displayName;
    // Exact duplicate - zero read/write asymmetry benefit
    // Maintenance cost: 2 models for identical data
}
// Trade-off framing result: negative ROI
// Cost: 2 entities, sync logic, eventual consistency
// Benefit: zero (read ≈ write traffic, no complex queries)
```

```java
// GOOD: Trade-off framing applied
// Decision: CRUD + read/write in same model
// Rationale documented in ADR-023:
//   "CQRS evaluated. Forces for CQRS:
//    Read/write asymmetry > 3:1 - NOT PRESENT (500 qpd)
//    Complex read projections - NOT PRESENT
//    Independent read/write scaling - NOT REQUIRED
//    CQRS cost: 2 models + sync + eventual consistency.
//    CQRS benefit: none applicable at this scale.
//    Decision: CRUD with read/write path in one model.
//    Trigger to revisit: read traffic > 50K qpd
//    or complex aggregation queries required."

@Service
public class UserProfileService {
    // Unified model: simple CRUD
    public UserProfile findById(Long id) {...}
    public UserProfile update(UpdateRequest req) {...}
}
```

**How to test / verify correctness:**
Document the trigger conditions for revisiting the rejected pattern. When those conditions are met (traffic reaches 50K qpd), re-run the trade-off framing against the new context. If the new framing produces positive ROI, implement CQRS at that point. If not, update the trigger threshold.

---

### ⚖️ Comparison Table

| Trade-off Dimension | Observable Metric | High-cost Signal | Low-cost Signal |
|---|---|---|---|
| Structural complexity | Classes/abstractions added | >5 new classes for one behaviour | 1-2 classes or lambda |
| Operational complexity | Infrastructure components | New queue/store/cache required | In-process only |
| Team knowledge cost | % team familiar with pattern | <50% team knows pattern | >90% team knows pattern |
| Evolution cost | Ease of removal/replacement | Pervasive (touches all services) | Localised (one class + tests) |
| Reversibility | Hours to remove if wrong | >40 hours distributed across teams | <4 hours in one service |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "If forces are present, the pattern should be applied" | Forces being present is necessary but not sufficient. The pattern's costs must be justified by the magnitude of the forces and the context. Weak forces justify simple solutions; strong forces justify complex patterns. |
| "Trade-off framing is only for complex patterns" | Simple patterns (Singleton, Facade) also have trade-offs (Singleton: testability, Facade: abstraction leakage). The framing is lighter for simpler patterns but still relevant. |
| "Document the trade-off once and it's done" | Trade-off justifications are context-dependent. Context changes (traffic grows, team changes, forces strengthen). ADRs documenting trade-off rationale must be revisited when context changes. |
| "Negative trade-off framing means the pattern is bad" | Negative trade-off in this context means the costs exceed benefits here. The same pattern may have positive trade-offs in a different context. Pattern quality and contextual fit are independent dimensions. |
| "Economic analysis is too formal for design decisions" | The economic framing does not require formal calculation. It requires acknowledging that patterns have costs and evaluating whether benefits exceed costs in the specific context — a two-minute reasoning process, not a spreadsheet. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Gold-plating — over-engineered pattern selection**

**Symptom:** Complex patterns applied to low-complexity problems. Metrics: implementation takes 3x as long as planned. New engineers spend weeks understanding the pattern before contributing.

**Root Cause:** Trade-off framing not performed. Patterns selected based on forces alone, ignoring whether operational and team costs are justified at this scale.

**Diagnostic:**
```bash
# Cyclomatic complexity and class count
# for components using complex patterns
find src -name "*.java" | xargs \
  grep -l "EventStore\|CQRS\|Outbox" | \
  while read f; do
    echo "$f: $(wc -l < $f) lines"
  done | sort -t: -k2 -rn | head -10
# High line counts on simple business logic
# = pattern overhead exceeding business complexity
```

**Fix:**
- BAD: Add more documentation to explain the complexity.
- GOOD: Run retroactive trade-off framing. If trade-off is negative, roll back the pattern to a simpler equivalent. Document the removal rationale and the trigger for reconsideration.

**Prevention:** All pattern-based design decisions require trade-off framing ADR before implementation. Review checkpoint: "Is the expected benefit proportional to the expected cost?"

---

**Failure Mode 2: Trade-off document stale — context changed**

**Symptom:** CQRS was applied and documented 3 years ago when traffic was high. Service was retired and now handles 100 requests/day. The two-model overhead is unnecessary but maintained due to "architecture conventions."

**Root Cause:** Trade-off framing was a one-time act, not a recurring review. Context changed; documentation did not.

**Diagnostic:**
```bash
# Find ADRs older than 2 years
find docs/adr -name "*.md" \
  -mtime +730 2>/dev/null | head -10
# These need context review against current system
# characteristics and team state
```

**Fix:**
- BAD: Keep the pattern because changing architecture is risky.
- GOOD: Schedule architecture review. Re-run trade-off framing against current context. If negative: remove pattern. Document the removal decision and the lessons learned.

**Prevention:** Architecture ADRs have explicit "review by" dates. Context-change triggers (significant traffic change, team change, force change) automatically queue ADR for review.

---

**Failure Mode 3: Team knowledge gap — pattern maintained incorrectly**

**Symptom:** Pattern was implemented correctly by original team. After team turnover, new engineers extend the pattern incorrectly (miss idempotency, bypass outbox, perform direct DB writes alongside event sourcing).

**Root Cause:** Team knowledge cost not evaluated in trade-off framing. Pattern requires expertise that depleted with team turnover.

**Diagnostic:**
```bash
# Signs of pattern misuse after team turnover
# Example: direct DB writes in ES system
grep -rn "entityManager.persist\|save(.*)" \
  src/main/java/com/example/command/ | \
  grep -v "EventStore\|OutboxRepository"
# Direct DB writes in command side = ES pattern broken
```

**Fix:**
- BAD: Write documentation explaining the pattern correctly.
- GOOD: Add ArchUnit fitness function that enforces the pattern boundary. Prevent misuse from accumulating silently.

**Prevention:** Trade-off framing must include "what breaks if someone unfamiliar with this pattern modifies it?" If the answer is "many things," add automated enforcement (tests, ArchUnit, linters).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[DPT-070 - Pattern-Recognition Mental Model]] - recognising patterns before framing their trade-offs
- [[DPT-061 - Pattern Selection Framework]] - the selection process that trade-off framing supplements
- [[DPT-003 - Pattern vs Anti-Pattern vs Idiom]] - trade-off framing applies to patterns, not idioms

**Builds On This (learn these next):**
- [[DPT-072 - Over-Engineering Risk Thinking]] - trade-off framing applied specifically to over-engineering decisions

**Alternatives / Comparisons:**
- [[SAP-062 - Architecture Trade-off Framing]] - the same concept at architectural level
- [[DPT-064 - Pattern-Driven Architecture Design]] - pattern trade-offs at system composition level

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ WHAT IT IS    │ Structured evaluation of a       │
│               │ pattern's costs vs. benefits in  │
│               │ a specific context               │
├───────────────┼──────────────────────────────────┤
│ PROBLEM       │ Force-correct patterns can be    │
│               │ economically wrong -- trade-offs  │
│               │ unchecked produce over-engineering│
├───────────────┼──────────────────────────────────┤
│ KEY INSIGHT   │ Forces match = necessary but not │
│               │ sufficient; costs must justify   │
│               │ benefits in this specific context│
├───────────────┼──────────────────────────────────┤
│ USE WHEN      │ Evaluating a specific pattern    │
│               │ application for a specific context│
├───────────────┼──────────────────────────────────┤
│ AVOID WHEN    │ Trivially correct/incorrect       │
│               │ decisions (overhead excessive)   │
├───────────────┼──────────────────────────────────┤
│ TRADE-OFF     │ Analysis time vs. avoidance of   │
│               │ costly pattern misapplication    │
├───────────────┼──────────────────────────────────┤
│ ONE-LINER     │ Benefits - Costs > 0 in THIS     │
│               │ context = apply; else reject     │
├───────────────┼──────────────────────────────────┤
│ NEXT EXPLORE  │ DPT-072 Over-Engineering Risk    │
└─────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Forces present = pattern applicable in principle. Trade-off positive = pattern justified in this context. Both conditions must be met.
2. Evaluate four cost dimensions: structural, operational, team knowledge, and reversibility.
3. Document the context assumptions that made the trade-off positive — when those assumptions change, the trade-off must be re-evaluated.

**Interview one-liner:** "Pattern trade-off framing evaluates structural costs (indirection added), operational costs (infrastructure overhead), team knowledge costs, and reversibility against the magnitude of the beneficial forces — applying only when benefits exceed total costs in the specific context."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Every capability has a carrying cost. The engineering principle of proportionality demands that solutions be scaled to the problem's actual magnitude — not its hypothetical future magnitude. Over-specification is waste; under-specification is risk. Trade-off framing is the mechanism for finding the proportional solution.

**Where else this pattern appears:**
- **API versioning strategy** - adding API versioning (an architectural pattern) has structural and operational costs. Trade-off framing: is the API consumed by enough external clients with divergent upgrade schedules to justify the versioning overhead? If not, a simpler deprecation strategy costs less.
- **Infrastructure redundancy** - adding N+1 redundancy to every service has operational cost. Trade-off framing: what is the cost of downtime for this service, and does it exceed the redundancy carrying cost? For non-critical internal tools, single-instance deployment may have positive trade-offs.
- **Test pyramid selection** - the proportion of unit/integration/E2E tests is a trade-off decision. More E2E tests provide higher confidence at higher maintenance cost. Trade-off framing: for a UI-heavy consumer app, the E2E overhead may be justified; for a backend library with stable interfaces, unit tests dominate the optimal trade-off.

---

### 💡 The Surprising Truth

Martin Fowler catalogued CQRS as a pattern in 2011 with an explicit warning that has been consistently ignored: "CQRS is a significant mental leap for all concerned, so it shouldn't be tackled unless the benefit is worth that [considerable] jump." He further stated that CQRS "is applicable in a limited set of cases — usually involving high-performance, highly scalable systems." The pattern has since been applied to systems with 100 requests/day. The warning was in the original write-up; practitioners simply stopped reading after the "Intent" section. This is the most significant large-scale failure of pattern trade-off framing in modern software engineering — not a lack of documentation, but a systematic failure to read and apply the consequences section of a well-documented pattern.

---

### 🧠 Think About This Before We Continue

**Question 1 (Design Trade-off):** Event Sourcing makes some changes easier (adding new event handlers, temporal queries) and some changes harder (changing event schemas, rebuilding large event stores, initial learning curve). Under what product roadmap and team characteristics does the "easier" side outweigh the "harder" side — and how would you structure a trade-off analysis that captures the forward-looking uncertainty in those factors?

*Hint:* Think about which use cases are speculative ("we might need audit logs someday") vs. definite ("we must support temporal queries for regulatory compliance"). How do you weight a definite cost against a speculative benefit?

**Question 2 (Scale):** A platform team maintains shared libraries that are used by 60 product teams. They want to add a pattern-based decorator mechanism to their HTTP client library. Structural trade-offs are positive. What additional trade-off dimensions does team-scale usage introduce that would not exist in a single-team context?

*Hint:* Think about how knowledge-cost scales differently when the consumers are 60 teams with variable engineering expertise, vs. one team that directly controls the implementation.

**Question 3 (Comparison):** Pattern trade-off framing and YAGNI (You Aren't Gonna Need It) are both arguments against over-engineering. But they sometimes conflict: trade-off framing might justify a pattern for an anticipated future force, while YAGNI would reject it until the force materialises. How do you decide which principle takes precedence — and what information would move you from "apply YAGNI" to "apply trade-off framing with forward-looking justification"?

*Hint:* Think about the cost asymmetry: if the pattern is cheap to add now but very expensive to add later (after the force has materialised), YAGNI may be wrong. What makes a pattern cheap later vs. expensive later?
