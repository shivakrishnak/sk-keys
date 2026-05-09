---
id: SAP-008
title: Architecture Review
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★★
depends_on: SAP-006, SAP-007, SAP-043, SAP-050, SAP-051
used_by: SAP-006, SAP-007
related: SAP-053, SAP-054, SAP-056, SAP-064
tags:
  - architecture
  - advanced
  - pattern
  - bestpractice
  - production
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 8
permalink: /software-architecture/architecture-review/
---

# SAP-008 - Architecture Review

⚡ TL;DR - An architecture review is a structured evaluation of a system's design decisions to verify alignment with standards, identify risks, and guide future evolution.

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| **Depends on** | SAP-006, SAP-007, SAP-043, SAP-050, SAP-051 |
| **Used by**    | SAP-006, SAP-007                            |
| **Related**    | SAP-053, SAP-054, SAP-056, SAP-064          |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A system grows for 3 years with no architectural oversight. Teams add services, introduce new databases, and create integrations driven by local delivery pressures. Eighteen months in: one service uses three different database technologies; a circular dependency exists between Service A and Service B; a critical security boundary has been gradually eroded by convenient but insecure shortcuts. No one has a complete picture of the system as a whole. By year 3, making any significant change requires archaeology and carries high risk of cascading failures.

**THE BREAKING POINT:**
Architectural decay is not dramatic - it is gradual. Each local decision is rational in isolation. Collectively, individually sensible shortcuts accumulate into structural problems that cost orders of magnitude more to fix than they would have cost to prevent. The moment the organisation realises it needs an architecture review is usually the moment the accumulated debt makes significant change prohibitively expensive.

**THE INVENTION MOMENT:**
Architecture reviews formalised the practice of periodic architectural assessment - separate from sprint delivery - that examines system structure holistically, identifies drift from intended architecture, surfaces emerging anti-patterns, and creates a shared architectural understanding across teams.

**EVOLUTION:**
Architecture reviews began as heavyweight ARB (Architecture Review Board) gating processes in large enterprises. These created bottlenecks in agile environments. Practice evolved toward lightweight RFC-based peer reviews, continuous automated checks (fitness functions), and periodic health reviews decoupled from change gating. Today, the best practice is a tiered model: automated gates for measurable constraints + periodic human review for strategic decisions, calibrated by risk and novelty rather than applied uniformly.

---

### 📘 Textbook Definition

An **Architecture Review** is a structured evaluation process in which an architecture or system design is examined by a review panel (architects, senior engineers, potentially external reviewers) against defined criteria: alignment with architectural principles, compliance with technology roadmap, fitness for stated non-functional requirements (NFRs), risk identification, and long-term sustainability. Architecture reviews are conducted at two levels: **system-level reviews** (periodic reviews of the full system architecture - typically quarterly) and **proposal reviews** (evaluation of a specific significant change before implementation).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A structured assessment of system design against principles, risks, and standards - before problems accumulate to become unmanageable.

**One analogy:**

> A building structural inspection. Periodically, a structural engineer examines the building: have the foundations shifted? Are any load-bearing elements compromised? Do any recent additions violate building codes? The inspection doesn't fix everything immediately - it produces a report of findings, priorities, and remediation timelines. The building remains occupied throughout.

**One insight:**
Architecture reviews are most valuable when conducted regularly and preventively - not reactively after an outage or a failed audit. By the time problems are visible as outages, they typically require far more effort to fix than if identified during a review.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Architecture review is separate from delivery - it requires stepping back from feature pressure to examine system structure.
2. A review produces findings, prioritised risks, and recommendations - not project approvals or blame.
3. Reviews cover both current state (what exists) and direction (is the system evolving correctly?).
4. The review panel must include people with system-wide context - not only the team that owns the system being reviewed.
5. Findings must be actioned - a review that produces a report never acted upon has negative value (false confidence).

**DERIVED DESIGN:**
From invariant 4: cross-team reviewers prevent local blind spots. The team that introduced a circular dependency is often unaware of its architectural significance because they optimised locally. An external reviewer with system context identifies the structural problem.

From invariant 5: an architecture review generates an action register. Each finding has an owner, priority, and resolution deadline. The review is only complete when findings are addressed or explicitly accepted as known risk.

**THE TRADE-OFFS:**
**Gain:** Architectural drift detected early; cross-team knowledge sharing; risk inventory; ADR quality validation; strategic evolution visibility.
**Cost:** Review process consumes senior engineering time; findings can create conflict if framed as blame; incomplete or infrequent reviews create false confidence; over-prescriptive reviews inhibit team velocity.

---

### 🧪 Thought Experiment

**SETUP:**
A platform with 20 services. Quarterly architecture reviews have been running for 18 months. Compare: what the team would have discovered organically (via outages) vs. what reviews surfaced proactively.

**WHAT HAPPENS WITHOUT Reviews:**
Month 8: data consistency bug caused by undocumented circular dependency - 6-hour incident. Month 14: database credentials rotating in 6 services but not 14 - security audit finding. Month 18: scaling ceiling hit because a single service is a bottleneck - not visible until peak load. Each discovery is expensive: outage, audit finding, or emergency refactoring.

**WHAT HAPPENS WITH Reviews:**
Q3 review: circular dependency in Architecture Diagram identified - remediated before it causes a consistency bug. Q5 review: credential rotation inconsistency flagged in security section - patched before audit. Q6 review: Service X identified as emerging bottleneck - scaling strategy planned proactively.

**THE INSIGHT:**
Quarterly reviews found 3 architectural risks and remediated them before they became incidents. The cost of the reviews (3 days/quarter × 5 people) was less than the cost of one production incident.

---

### 🧠 Mental Model / Analogy

> An architecture review is like a financial audit. Annual financial audits don't just check if a company made money this year - they verify the financial controls, highlight compliance risks, and assess whether financial practices are sustainable. The audit doesn't halt business operations; the company keeps running. But the audit's findings must be addressed - unresolved audit findings accumulate into liability. Architecture reviews function identically for technical systems.

- "Financial audit" → architecture review
- "Financial controls" → architectural principles (separation of concerns, coupling, security boundaries)
- "Compliance risks" → technology roadmap violations, security architecture gaps
- "Unresolved audit findings" → deferred architectural debt
- "External auditor" → external reviewer bringing cross-system perspective

Where this analogy breaks down: a financial audit has regulatory force - findings must be addressed. Architecture review findings are recommendations rather than mandates. The governance model must create incentives to act on findings without regulatory enforcement.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
An architecture review is a periodic "health check" for a software system. A team of experienced engineers examines the system's overall structure, identifies problems before they cause crises, and produces a prioritised list of improvements. It's like getting a doctor's check-up - you don't wait until you're sick to find out if something is wrong.

**Level 2 - How to use it (junior developer):**
Architecture reviews happen at two times: (1) before building a significant new feature or system, to validate the proposed design; and (2) periodically (quarterly/annually) to assess the existing system. You participate by: providing documentation of your service's architecture, attending the review session, answering questions about design decisions, and implementing any findings assigned to your team.

**Level 3 - How it works (mid-level engineer):**
A review has five phases: (1) **Preparation** - architecture documentation gathered (service diagram, data flow, ADR index, non-functional requirements). (2) **Panel composition** - 3–6 reviewers with relevant expertise and cross-system context. (3) **Assessment** - reviewers examine: coupling/cohesion, technology roadmap alignment, security boundary integrity, scalability constraints, data consistency patterns, deployment independence. (4) **Findings** - prioritised list: Critical (must fix before next release), High (fix within quarter), Medium (plan for next 6 months), Low (accept or defer). (5) **Follow-up** - findings assigned with owners and deadlines; reviewed at next check-in.

**Level 4 - Why it was designed this way (senior/staff):**
Architecture reviews address the inherent tension between local delivery optimisation and global architectural integrity. Individual teams optimise for their delivery velocity and local concerns - rationally. But architecture is an emergent property of many local decisions. Without a mechanism for global oversight, locally rational choices accumulate into globally suboptimal structures. Reviews create the feedback loop from global structure → local decision constraints. At the principal/staff level, architecture reviews are the primary mechanism for cross-team architectural alignment - not mandates or blueprints, but collaborative assessment that builds shared architectural understanding across team boundaries.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│  ARCHITECTURE REVIEW PROCESS                           │
│                                                        │
│  PREPARATION (1 week before)                           │
│  → Architecture documentation collected               │
│  → Service diagrams, data flows, ADR index             │
│  → NFR targets vs. actual metrics                      │
│                                                        │
│  REVIEW SESSION (half-day to 1 day)                    │
│  → Panel: 3-6 engineers with cross-system context      │
│  → Structured assessment: coupling, security,          │
│    performance, roadmap alignment                      │
│  → Finding log maintained in real time                 │
│                                                        │
│  POST-REVIEW (1 week after)                            │
│  → Findings prioritised: Critical/High/Medium/Low     │
│  → Each finding: owner, deadline, acceptance status    │
│  → Summary published to engineering leadership         │
│  → Next review scheduled                              │
└────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (Proposal Review):**

```
New system design proposed by Team A
  → Architecture documentation prepared
    [← YOU ARE HERE: proposal submitted for review]
  → Review panel convened (3 architects)
  → Assessment: proposed design uses synchronous REST
    for operations needing eventual consistency → risk
  → Finding: Critical - replace with async events
  → Team A updates design before implementation begins
  → Review approved with findings resolved
  → ADR created: "ADR-056: event-driven for X"
```

**FAILURE PATH:**

```
Review findings not actioned:
  → Q3 review: 3 critical findings assigned
  → Q4 review: same 3 findings reappear
  → Action register: findings marked "in backlog"
  → Q5 review: first finding caused production incident
  → Pattern: findings without SLA have no urgency
  [Fix: critical findings block next major release]
```

**WHAT CHANGES AT SCALE:**
5-team organisation: informal review, senior engineer facilitating. 20 teams: formal review process, Architecture Review Board (ARB). 100 teams: automated architecture fitness functions replace manual reviews for measurable constraints; manual reviews focus on novel patterns and strategic decisions.

---

### 💻 Code Example

**Example 1 - Architecture fitness function (ArchUnit):**

```java
// Automated architecture review via ArchUnit
// Detects architectural violations in CI
@AnalyzeClasses(packages = "com.company")
public class ArchitectureTest {

  // Finding: no package-level circular dependencies
  @ArchTest
  static final ArchRule noCircularDependencies =
    slices().matching("com.company.(*)..")
      .should().beFreeOfCycles();

  // Finding: domain must not depend on infrastructure
  @ArchTest
  static final ArchRule domainIndependence =
    noClasses().that()
      .resideInAPackage("..domain..")
      .should()
      .dependOnClassesThat()
      .resideInAPackage("..infrastructure..");

  // Finding: controllers only in presentation layer
  @ArchTest
  static final ArchRule controllersLocation =
    classes().that()
      .haveNameMatching(".*Controller")
      .should()
      .resideInAPackage("..presentation..");
}
```

**Example 2 - Architecture review checklist (YAML template):**

```yaml
# architecture-review-checklist.yaml
review:
  service: order-service
  date: 2026-05-06
  reviewers: [alice, bob, charlie]

checks:
  coupling:
    - question: "Circular dependencies present?"
      finding: "None detected"
      severity: passed

    - question: "Shared database with other services?"
      finding: "order-db shared with legacy-billing"
      severity: critical
      owner: alice
      deadline: "2026-Q3"
      remediation: "Migrate legacy-billing to own DB"

  roadmap_alignment:
    - technology: "Docker Swarm"
      status: "Retire (roadmap)"
      finding: "3 services still using Swarm"
      severity: high
```

---

### ⚖️ Comparison Table

| Type                            | Trigger                  | Scope                  | Duration | Best For                            |
| ------------------------------- | ------------------------ | ---------------------- | -------- | ----------------------------------- |
| **Proposal Review**             | Before implementation    | Single design          | Half-day | New systems, significant changes    |
| **Periodic Review**             | Quarterly/Annually       | Full system            | 1 day    | Ongoing architectural health        |
| **Security Review**             | Before launch / annually | Security architecture  | 1 day    | Risk posture, compliance            |
| **Automated Fitness Functions** | Every CI build           | Measurable constraints | Minutes  | Continuous architectural validation |

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                                                                                    |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Architecture reviews are approval gates                  | Reviews are quality and risk assessments - not approvals. The team retains decision authority; the review informs decisions and surfaces risks they may not have fully considered          |
| Architecture reviews slow down delivery                  | Reviews conducted regularly and proportionally add minimal delay. Reviews that are infrequent, high-stakes, and blocking create the overhead problem                                       |
| Only architects conduct architecture reviews             | The best reviews include senior engineers who understand implementation constraints, security engineers, and sometimes product engineers. Architect-only reviews miss operational context  |
| Automated fitness functions replace architecture reviews | Fitness functions validate measurable constraints (coupling metrics, dependency rules). They cannot assess strategic direction, novel patterns, or soft qualities like team cognitive load |

---

### 🚨 Failure Modes & Diagnosis

**1. Review Theatre - Findings Never Actioned**

**Symptom:** Quarterly architecture reviews produce reports. The same findings appear in Q1, Q2, Q3, and Q4. Engineers attend reviews reluctantly. Reviews consume significant time but nothing changes.

**Root Cause:** No consequence for unresolved findings. Reviews are informational, not actionable.

**Diagnostic:**

```bash
# Count recurring findings across reviews:
grep "finding" docs/reviews/*.md | \
  awk '{print $NF}' | sort | uniq -c | sort -rn
# Findings appearing >2 reviews: systemic resolution failure
```

**Fix:** Implement finding SLAs: Critical findings block next major release. High findings require quarterly resolution commitment. Findings tracked in the same issue tracker as features.

**Prevention:** Every finding must have: owner, priority, resolution date. Next review agenda starts with "previous findings resolution status."

---

**2. Rubber-stamp Review - No Critical Challenge**

**Symptom:** Reviews always conclude "looks good." Significant architectural problems are discovered later via incidents, not reviews.

**Root Cause:** Review panel either lacks cross-system context or social dynamics prevent critical challenge of senior engineers' decisions.

**Diagnostic:**

```bash
# Count Critical/High findings per review:
grep -c "critical\|high" docs/reviews/202*.md
# If consistently 0: review is not finding real problems
```

**Fix:** Introduce external reviewers (from other teams, or external consultants) who have no social obligation to approve. Adopt adversarial review format: reviewers assigned to "find what could go wrong" rather than "validate the design."

**Prevention:** Define minimum finding expectations per review based on system complexity. A review of a 20-service system that finds zero Medium+ issues is statistically improbable.

---

**3. Over-Governance - Every Change Requires Review**

**Symptom:** Teams must submit every significant PR to an Architecture Review Board, creating a queue of pending reviews. Feature delivery velocity drops 40%. Teams work around the review process.

**Root Cause:** Review process applied without categorisation. All changes treated as equal regardless of risk or novelty.

**Diagnostic:**

```bash
# Measure average time from review submission to decision:
jira-cli issue list --jql \
  "issuetype = 'Architecture Review' AND status != Done" \
  --format '{{.Created}}\t{{.Status}}'
# If median > 5 days: review bottleneck exists
```

**Fix:** Implement tiered review: changes conforming to established patterns (no review required), changes using approved technologies in new ways (lightweight async review), novel patterns or cross-system changes (full synchronous review). Teams self-classify with random audit.

**Prevention:** Define "review-required" criteria objectively. Publish the rubric so teams can self-assess before submission.

---

### � Transferable Wisdom

**Reusable Engineering Principle:** Governance mechanisms are most effective when proportional to risk. A gate that treats every change as high-risk creates both bottlenecks and avoidance behaviour. Calibrating review depth to decision reversibility (Type 1 vs. Type 2 decisions) is a general principle applicable to any quality process.

**Where else this pattern appears:**

- **Clinical governance:** the medical system separates routine clinical decisions from high-risk interventions requiring peer review - mortality and morbidity conferences and case reviews mirror the architecture review's periodic health assessment model.
- **Financial risk management:** risk frameworks distinguish between standard transactions handled by automated controls and unusual transactions requiring manual review, calibrated by exposure amount and novelty - exactly the tiered review model.
- **Aviation:** flight operations apply proportional review - routine routes use standard checklists; new routes or unusual conditions trigger full safety review - the same principle of risk-proportionate governance depth.

---

### 💡 The Surprising Truth

The most common failure of architecture reviews is not that they are too strict - it is that they are too late. The most effective review happens before a design is complete, when changes cost nothing. Reviews done after a complete design is presented find real problems but trigger sunk-cost pressure to accept them anyway. A 30-minute review of a design sketch prevents more architectural debt than a 3-day review of a finished specification.

---

### �🔗 Related Keywords

**Prerequisites (understand these first):**

- `Architecture Decision Record (ADR)` - ADRs are both an input to architecture reviews (showing what decisions were made) and an output (reviews create new ADRs for findings)
- `Coupling` - one of the primary assessment dimensions in any architecture review; high coupling is the most common architectural risk identified

**Builds On This (learn these next):**

- `Architecture Fitness Functions` - automated, continuous architectural validation that complements periodic manual reviews
- `Technology Roadmap` - the strategic reference against which architecture reviews assess technology choices

**Prerequisites (understand these first):**

- SAP-006 - Architecture Decision Record (ADR) (the primary input to reviews; understanding ADRs is required to evaluate review quality)
- SAP-050 - Cohesion and SAP-051 - Coupling (the metrics most frequently assessed during architecture review)

**Builds On This (learn these next):**

- SAP-054 - Architecture Review Process Design (how to design an effective review process at scale)
- SAP-056 - Architecture Fitness Functions (the automated continuous complement to periodic human reviews)
- SAP-057 - Architecture Governance at Scale (how reviews fit into the broader governance model)

**Alternatives / Comparisons:**

- SAP-056 - Architecture Fitness Functions (automated continuous variant; complements reviews for measurable constraints but cannot replace judgment for strategic assessment)
- RFC Process - the proposal-oriented complement; RFCs propose changes, reviews assess health

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Structured evaluation of system design    │
│              │ against principles, risks, and standards  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Architectural drift accumulates silently  │
│ SOLVES       │ into structural debt that becomes costly  │
│              │ to fix                                    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Reviews are most valuable when periodic   │
│              │ and preventive - not reactive post-outage │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Significant design proposals; periodic    │
│              │ system health; pre-launch security; prior │
│              │ to major migrations                       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ As a blocking gate for every change -     │
│              │ apply proportionally to risk and novelty  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Architectural drift prevention vs. senior │
│              │ engineer time + risk of over-governance   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The annual check-up that finds the       │
│              │  problem before it becomes the crisis."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ADR → Architecture Fitness Functions →    │
│              │ Technology Roadmap → ArchUnit             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An organisation runs quarterly architecture reviews with a 5-person Architecture Review Board (ARB). The ARB reviews 40 proposals per quarter. The average proposal takes 3 days from submission to decision. Senior engineers complain the ARB is a bottleneck. Design a tiered review system that reduces ARB involvement to the 20% of proposals that genuinely require board-level judgment, while maintaining architectural quality for the remaining 80%.

_Hint:_ Research how Google's design review process and Netflix's architecture council operate - both use a tiered model where the threshold for escalation to senior review is explicitly defined by decision type (reversal cost, blast radius, cross-team impact), not by team preference.

**Q2.** Your architecture review finds that 8 of 20 services violate the "Database per Service" principle - they all write to a shared database owned by Service A. Service A's team argues this is the practical reality of their domain and that isolation would create distributed transaction complexity they cannot manage. Evaluate both positions and describe how you would document this as an "accepted architectural debt" in a way that: records the risk, captures the rationale, and creates a future trigger for remediation.

_Hint:_ Look at how architectural debt is formally managed in ISO/IEC 25010 quality model and how SAP-006 ADR format handles "accepted debt" with explicit revisit triggers - combining both gives you the documentation framework needed.

**Q3.** Compare a manual quarterly architecture review with continuous automated architecture fitness functions (e.g., ArchUnit running in CI). Identify at least four categories of architectural concern where each approach is strictly superior to the other, and design a combined governance model that uses each where it excels - specifying what is automated, what is manual, and the handoff between the two.

_Hint:_ Study the ArchUnit documentation explicitly - it defines which constraints can be automated (cyclic dependencies, layer violations, naming) and which cannot (fitness for purpose, strategic appropriateness). The boundary between automatable and non-automatable is the exact boundary you need to design around.
