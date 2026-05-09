---
id: SAP-054
title: Architecture Review Process Design
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★★
depends_on: SAP-008, SAP-053, SAP-006
used_by: SAP-057, SAP-056
related: SAP-008, SAP-053, SAP-062
tags:
  - architecture
  - advanced
  - governance
  - bestpractice
  - pattern
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 54
permalink: /software-architecture/architecture-review-process-design/
---

# SAP-054 - Architecture Review Process Design

⚡ TL;DR - Architecture review process design is the systematic approach to evaluating architectural decisions before implementation, balancing rigour with delivery speed.

| SAP-054 | Category: Software Architecture Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | SAP-008, SAP-053, SAP-006 | |
| **Used by:** | SAP-057, SAP-056 | |
| **Related:** | SAP-008, SAP-053, SAP-062 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Architecture reviews happen informally, inconsistently, or not at all. Some decisions get extensive scrutiny based on the seniority of the proposer; others with equal impact get none. The process is opaque: engineers do not know when to trigger a review, who is involved, or how long it takes. Innovation slows because engineers fear "the architecture police."

**THE BREAKING POINT:**
A cross-team API contract is proposed. One team reviews it internally and ships it. Eight months later, three other teams built integrations on the contract. A security flaw is discovered. Fixing the flaw requires coordinated breaking changes across all three integrations plus a migration plan. A proper architecture review process would have caught the security flaw in two hours rather than eight months.

**THE INVENTION MOMENT:**
The Software Architecture Review and Assessment (SARA) framework and later the Architecture Tradeoff Analysis Method (ATAM) by the SEI formalised what practitioners had been doing informally. The key insight was that reviews achieve value only when they are structured around quality attribute scenarios, not around free-form feedback.

**EVOLUTION:**
Modern architecture review processes have evolved from heavyweight committee reviews (days of work) to lightweight "architectural fitness checks" that are integrated into the delivery workflow. The goal is maximum risk coverage at minimum delivery friction.

---

### 📘 Textbook Definition

**Architecture review process design** is the definition of: (1) triggers (when a review is required), (2) scope (what is reviewed), (3) participants (who reviews), (4) evaluation criteria (quality attribute scenarios and fitness functions), (5) formats (lightweight async vs synchronous workshop), and (6) outputs (ADR, risk register update, approved/deferred/rejected).

---

### ⏱️ Understand It in 30 Seconds

**One line:** Architecture review process design defines who reviews what, when, how, and with what criteria - before a costly decision becomes irreversible.

> Think of a building permit review: before construction begins, inspectors check the plans against safety codes. The review is triggered by construction intent, uses standardised criteria, involves qualified reviewers, and produces a clear decision. The value is catching problems before concrete is poured.

**One insight:** A review process that engineers fear or avoid provides no value. The design goal is maximum quality improvement at minimum delivery disruption.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Reviews are valuable only before a decision is implemented. Post-implementation reviews are audits, not gates.
2. Review quality is determined by the clarity of evaluation criteria, not by the seniority of reviewers.
3. Reviews must be proportional: heavyweight for high-risk decisions, lightweight for medium-risk, none for low-risk.
4. A review process that blocks delivery creates adversarial dynamics and is eventually bypassed.

**DERIVED DESIGN:**
A tiered review process matches review intensity to decision risk. Tier 1 (low risk): self-review against a checklist. Tier 2 (medium risk): async peer review with ADR. Tier 3 (high risk): synchronous structured review with quality attribute scenario evaluation.

**THE TRADE-OFFS:**
**Gain:** Early detection of architectural flaws before implementation compounds costs. Shared architectural knowledge. Clear accountability for architectural decisions.
**Cost:** Review process time. Risk of bottleneck if not designed well. Cultural overhead if process is not trusted.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** High-risk decisions genuinely need evaluation from multiple perspectives to surface blind spots.
**Accidental:** Bureaucratic approval chains, unclear criteria, and mandatory reviews for all decisions regardless of risk.

---

### 🧪 Thought Experiment

**SETUP:** Two engineering organisations of equal size. Organisation A has no formal review process. Organisation B has a tiered review process (self-review → peer review → structured review based on risk tier).

**WHAT HAPPENS WITHOUT THE PROCESS (Org A):** In year 1, release velocity is high. By year 2, several major architectural inconsistencies have accumulated (three different authentication approaches, two incompatible event formats). Fixing them requires a 6-month "architecture normalisation" programme. Feature delivery halts.

**WHAT HAPPENS WITH THE PROCESS (Org B):** Tier 3 reviews (major decisions) average 2 days of elapsed time. Tier 1 reviews (routine decisions) are self-completed in 30 minutes. Year 2 architectural consistency is high. Feature velocity remains stable because refactoring work is minimal.

**THE INSIGHT:** The cost of the review process is paid once. The cost of not having it is paid continuously as compounding inconsistency debt.

---

### 🧠 Mental Model / Analogy

> Think of quality gates in manufacturing. Every part passes through inspection at multiple stages: raw material, sub-assembly, final assembly, shipping. The stage at which a defect is caught determines the remediation cost. A defect in raw material costs pennies to fix. The same defect found at shipping costs thousands.

- **Manufacturing QA stages** = review tiers (self, peer, structured)
- **Defect catching cost curve** = architectural flaw cost curve (cheap early, expensive late)
- **Inspection criteria** = quality attribute scenarios
- **Rejected part** = deferred/rejected architectural decision
- **Approved part** = accepted architecture with documented rationale

Where this analogy breaks down: software decisions have subjective dimensions (team fit, strategic alignment) that manufacturing QA does not. Some "defects" are contextual - the same architectural choice that fails one QA criterion may excel on another.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Before making a big decision in software, a good team gets the right people to check it against the right criteria. Architecture review process design is the system that makes those checks happen consistently.

**Level 2 - How to use it (junior developer):**
Know your team's review process triggers. When your work touches a service boundary, cross-team contract, or data model, check whether a review is required. Follow the appropriate template. A good review is not about getting permission - it is about getting feedback that makes your design better.

**Level 3 - How it works (mid-level engineer):**
A well-designed review process has tiered triggers. Tier classification: (a) does this cross service or team boundaries? (b) does this change a public API, DB schema, or authentication mechanism? (c) does this affect multiple quality attributes? Each "yes" adds to the risk tier. Higher tier = more structured review.

**Level 4 - Why it was designed this way (senior/staff):**
The architecture review process is a risk management mechanism. Its design must balance two failure modes: too heavy (blocked delivery, engineers route around it) and too light (architectural inconsistencies slip through). The correct balance is context-dependent: early-stage startups need a 30-minute tiered check; enterprise platforms deploying across 50 services need structured reviews with external reviewers. The process must be designed, not defaulted.

**Expert Thinking Cues:**
- The review process is working when engineers initiate reviews proactively rather than avoiding them.
- If review outputs are ignored, the process is broken. Every review output must generate either implementation action or documented rationale for non-action.
- Review criteria should be quality attribute scenarios, not personal preferences.

---

### ⚙️ How It Works (Mechanism)

**Tiered Architecture Review Process:**

```
RISK SIGNALS → TIER → FORMAT → SLA
─────────────────────────────────────────────
No cross-boundary impact  → T1 → Self-check  → Same day
Service/API/schema change → T2 → Async peer  → 2 days
Security/cross-org/irreversible → T3 → Workshop → 5 days
```

**Risk escalation multipliers:**

| Signal | Tier bump |
|---|---|
| Cross-service API contract | +1 |
| Database schema change | +1 |
| Authentication/security impact | +2 |
| Cross-org or public API boundary | +2 |
| High irreversibility | +1 |
| Compliance or regulatory scope | +2 |

**Review meeting structure (Tier 3 only):**
1. Proposer presents context and constraints (15 min)
2. Quality attribute scenarios enumerated (20 min)
3. Design walk-through against each QA scenario (30 min)
4. Risk identification and trade-off discussion (20 min)
5. Decision: approve / approve-with-conditions / defer / reject (5 min)

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Engineer identifies decision
        │
        ▼
   Risk Triage
   (apply signals)
        │
   ┌────┴────┐
  T1        T2/T3
   │         │
Self-check  Draft ADR
Checklist   & notify
   │         │
  ADR        │
Created  Async/Workshop
   │     Review
   │         │
   └────┬────┘
        │
   Decision recorded
   in ADR + risk register    ← YOU ARE HERE
        │
   Implementation
   (fitness function gates)
```

**FAILURE PATH:**
Engineer skips triage → decision implemented without review → architectural flaw discovered late → emergency rework under production pressure → post-mortem reveals review was bypassed.

**WHAT CHANGES AT SCALE:**
At 10 engineers: informal review works. At 50 engineers: Tier 2 async reviews become essential. At 200+ engineers: Tier 3 structured reviews need a dedicated architecture guild with rotation membership to prevent bottlenecks and knowledge hoarding.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Multiple teams may submit Tier 3 reviews simultaneously. The review calendar becomes a shared resource. Design review queues with explicit SLAs and escalation paths. A review that exceeds its SLA blocks delivery - enforce the SLA or escalate automatically.

---

### 💻 Code Example

**Architecture fitness function - enforcing no direct DAO→Controller calls:**

```java
// BAD: No automated enforcement - violation discovered
// only in manual review or production
@RestController
public class UserController {
    @Autowired
    private UserDao userDao; // Direct DAO - bypass service layer
    
    public User getUser(Long id) {
        return userDao.findById(id); // Layering violation
    }
}
```

```java
// GOOD: Fitness function in test suite catches violation
// before it reaches review or production
@Test
void noControllerShouldImportDao() {
    JavaClasses classes = new ClassFileImporter()
        .importPackages("com.example");

    ArchRule rule = noClasses()
        .that().resideInAPackage("..controller..")
        .should().dependOnClassesThat()
        .resideInAPackage("..dao..");

    rule.check(classes); // Fails CI if violated
}
```

```java
// GOOD: Correct layered access
@RestController
public class UserController {
    @Autowired
    private UserService userService; // Service layer only

    public User getUser(Long id) {
        return userService.findUser(id);
    }
}
```

**How to test / verify correctness:**
Run `mvn test` - the ArchUnit test fails immediately if any controller directly imports a DAO class. This automates the layer boundary check from Architecture Review Tier 1 into CI, preventing violations before they ever reach human review.

---

### ⚖️ Comparison Table

| Method | Rigor | Speed | Best Fit |
|---|---|---|---|
| ATAM (SEI) | ★★★ | Days | Safety-critical, regulated |
| RFC Process | ★★ | 3-5 days | Open-source, platform teams |
| ADR + Async Review | ★★ | 1-2 days | Product engineering teams |
| Architecture Fitness Functions | ★★ | Hours | Well-defined quality attributes |
| Informal Peer Review | ★ | Hours | Early-stage, low-risk |
| No Review | ✗ | Instant | Prototypes only |

---

### 🔁 Flow / Lifecycle

```
1. TRIGGER
   Engineer identifies decision
   matching review signals
          │
          ▼
2. TRIAGE
   Risk signals scored → tier assigned
   ADR template selected for tier
          │
          ▼
3. REVIEW
   T1: Self-checklist
   T2: Async peer review (48h window)
   T3: Structured workshop session
          │
          ▼
4. DECISION
   Approve / Approve-with-conditions
   / Defer / Reject
   Decision recorded in ADR
          │
          ▼
5. IMPLEMENTATION
   Fitness functions guard boundaries
   Conditions tracked to completion
          │
          ▼
6. RETROSPECTIVE
   Quarterly: did reviews catch issues?
   Were any bypassed? Calibrate tiers.
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Review = approval gate, not quality improvement" | Reviews exist to improve design through challenge, not to grant permission. A review that only approves without improving provides near-zero value. |
| "More senior reviewers = better review" | Review quality depends on the clarity of evaluation criteria (QA scenarios), not reviewer seniority. A junior with a checklist beats a principal without one. |
| "Post-implementation review catches the same issues" | Once concrete is poured, the real cost of fixing problems escalates 10-100x. Post-hoc reviews are audits - they diagnose, not prevent. |
| "A universal process works for all team sizes" | A startup with 5 engineers needs a 30-minute check. An enterprise with 500 engineers needs structured multi-team reviews with external validation. Process must be designed per context. |
| "Fitness functions replace human review" | Fitness functions automate what can be measured (layer boundaries, coupling metrics). Human review addresses what cannot be automated: strategic fit, long-term trade-offs, team capacity. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Review process bypassed**

**Symptom:** ADRs are created retroactively after implementation, or not at all.

**Root Cause:** Process is too heavy for the perceived risk level. Engineers rationally avoid it.

**Diagnostic:**
```bash
# Count ADRs created before vs after implementation
# (check ADR date vs first commit date for that feature)
git log --follow --diff-filter=A -- "docs/adr/*.md" \
  | grep "Date:" | head -20
```

**Fix:**
- BAD: Add enforcement gate that blocks PRs without ADR.
- GOOD: Reduce Tier 1 to a 5-field self-check. Make the process take less time than the bypass takes.

**Prevention:** Calibrate tier thresholds quarterly. If >30% of decisions skip review, thresholds are too low.

---

**Failure Mode 2: Reviews produce no action**

**Symptom:** Reviews happen but decisions are not changed. Reviewers stop engaging seriously.

**Root Cause:** Review outputs are treated as advisory only. No one tracks whether conditions are met.

**Diagnostic:**
```bash
# Check ADR status field across all ADRs
grep -r "status:" docs/adr/*.md | \
  grep -v "Accepted\|Rejected" | head -20
# Many "Proposed" ADRs that never closed = review theater
```

**Fix:**
- BAD: Review produces a Slack message with feedback.
- GOOD: Every review produces a formal ADR with status tracking. Conditions-to-approve are tracked in the issue tracker.

**Prevention:** Assign owner to every approval condition. Review retrospective quarterly checks closure rate.

---

**Failure Mode 3: Review bottleneck blocks delivery**

**Symptom:** Tier 3 review queue exceeds 10 days. Teams route decisions through Tier 1/2 to avoid the queue.

**Root Cause:** Too few qualified reviewers. Tier 3 criteria are too broad (too many T3 triggers).

**Diagnostic:**
```bash
# Check lead time for Tier 3 reviews
# Query issue tracker for "architecture-review" label
# Calculate create→close time distribution
```

**Fix:**
- BAD: Add more items to the review checklist to correct for past mistakes.
- GOOD: Narrow T3 triggers to irreversible/cross-org/security. Implement reviewer rotation across senior engineers. Time-box sessions to 90 minutes max.

**Prevention:** Track review cycle time as an engineering metric. SLA breach triggers automatic escalation.

---

**Failure Mode 4: Security blind spot (no security in review criteria)**

**Symptom:** Security vulnerabilities discovered in production that a review would have caught.

**Root Cause:** Review criteria do not include security quality attribute scenarios. Review participants exclude security engineering.

**Diagnostic:**
```bash
# Audit recent CVEs for your services
# Check whether the affected component ever
# went through architecture review with security scope
```

**Fix:**
- BAD: Security review is a separate process called only for "security features."
- GOOD: Every Tier 2+ review includes a security quality attribute scenario. Security team is in the reviewer rotation.

**Prevention:** Embed security QA scenarios in Tier 2 and Tier 3 review templates by default.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SAP-008 - Architecture Review]] - the informal/ad-hoc predecessor
- [[SAP-006 - Architecture Decision Record (ADR)]] - the output artifact of every review
- [[SAP-053 - Architecture Decision Records (ADR) Strategy]] - the strategy layer above individual ADRs

**Builds On This (learn these next):**
- [[SAP-056 - Architecture Fitness Functions]] - automated review gates
- [[SAP-057 - Architecture Governance at Scale]] - scaling review across many teams
- [[SAP-062 - Architecture Trade-off Framing]] - the criteria used inside reviews

**Alternatives / Comparisons:**
- [[SAP-053 - Architecture Decision Records (ADR) Strategy]] - ADR-only (no review gate)
- [[SAP-061 - Evolutionary Architecture Design]] - fitness-function-only approach
- ATAM (SEI) - heavyweight formal review for safety-critical systems

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ WHAT IT IS    │ System for consistent arch       │
│               │ decision evaluation              │
├───────────────┼──────────────────────────────────┤
│ PROBLEM       │ Inconsistent/missing reviews =   │
│               │ compounding architectural debt   │
├───────────────┼──────────────────────────────────┤
│ KEY INSIGHT   │ Review intensity must match      │
│               │ decision risk — not seniority    │
├───────────────┼──────────────────────────────────┤
│ USE WHEN      │ Cross-boundary, security, or     │
│               │ irreversible decisions           │
├───────────────┼──────────────────────────────────┤
│ AVOID WHEN    │ Routine internal decisions with  │
│               │ no cross-team impact             │
├───────────────┼──────────────────────────────────┤
│ TRADE-OFF     │ Review cost (time) vs rework     │
│               │ cost (10-100x later)             │
├───────────────┼──────────────────────────────────┤
│ ONE-LINER     │ Catch flaws before concrete      │
│               │ is poured                       │
├───────────────┼──────────────────────────────────┤
│ NEXT EXPLORE  │ SAP-056 Fitness Functions        │
└─────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Tier the process: self-check → async peer → structured workshop.
2. Review criteria must be quality attribute scenarios, not personal preferences.
3. A review process engineers bypass provides exactly zero value.

**Interview one-liner:** "Architecture review process design matches review intensity to decision risk using tiered triggers, quality attribute evaluation criteria, and documented outputs — making architectural knowledge explicit and catching flaws before implementation multiplies their cost."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** The value of any quality gate is determined by the gap between detection cost and remediation cost. Gates that are cheap to pass and catch expensive mistakes are worth any overhead; gates that are costly to execute but catch cheap mistakes should be removed.

**Where else this pattern appears:**
- **Code review process design** - PR reviews are tiered: small PRs get quick approvals, large architectural changes require synchronous design discussion.
- **Security threat modelling** - tiered by attack surface area; major data stores require full threat modelling, minor utilities get self-check.
- **Financial investment committees** - small capital expenditures are manager-approved; above a threshold require committee review; above another threshold require board approval.

---

### 💡 The Surprising Truth

The SEI's Architecture Tradeoff Analysis Method (ATAM), the gold standard of structured architecture review, typically finds 40-70 architectural risks per engagement - even in systems engineered by experienced teams. This is not evidence of poor engineering. It is evidence that architecture quality attributes (performance, security, reliability) are genuinely in tension with each other, and no single engineer can hold all the trade-offs in mind simultaneously. Structured review with multiple perspectives is not a check on competence; it is the mechanism by which complex trade-offs become visible at all.

---

### 🧠 Think About This Before We Continue

**Question 1 (System Interaction):** Your organisation moves from a monolith to microservices. Your current review process was designed for monolith changes. What signals and criteria in the tiered process would need to change — and why?

*Hint:* Think about what changes when a decision boundary becomes a network boundary. What new quality attributes become relevant?

**Question 2 (Scale):** A platform team serves 20 product teams. Each product team submits 3-5 Tier 2 reviews per week. The platform architecture guild has 6 members. How would you redesign the process to prevent bottlenecks without reducing review quality?

*Hint:* Consider reviewer rotation, delegation criteria, and what "quality" means when a reviewer spends 4 hours per day in reviews.

**Question 3 (Design Trade-off):** Two engineers argue: "We should require an ADR for every design decision (consistency)" vs "ADRs should only be required for high-risk decisions (speed)." How would you design the trigger criteria to satisfy both engineers' underlying concerns?

*Hint:* What does "high-risk" actually mean in terms of observable signals? Can you make the criteria objective enough that engineers agree on tier assignment without escalation?


