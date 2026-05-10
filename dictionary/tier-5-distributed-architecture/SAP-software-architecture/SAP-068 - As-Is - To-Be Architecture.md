---
id: SAP-068
title: "As-Is / To-Be Architecture (Current State vs Target State)"
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★☆
depends_on: SAP-065, SAP-066, SAP-067
used_by: SAP-069, SAP-070, SAP-055
related: SAP-007, SAP-053, SAP-056
tags:
  - architecture
  - intermediate
  - bestpractice
  - pattern
status: complete
version: 3
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 68
permalink: /software-architecture/as-is-to-be-architecture/
---

# SAP-068 - As-Is / To-Be Architecture (Current State vs Target State)

⚡ TL;DR - As-Is/To-Be is the fundamental EA planning technique that maps the current technology estate, defines the desired target state, performs gap analysis, and produces a roadmap to close the gap.

| SAP-068 | Category: Software Architecture Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | SAP-065, SAP-066, SAP-067 | |
| **Used by:** | SAP-069, SAP-070, SAP-055 | |
| **Related:** | SAP-007, SAP-053, SAP-056 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An organisation wants to "move to the cloud." Without a structured current-state inventory, every team estimates its own migration scope. Without a defined target state, "cloud" means different things to different teams. Without gap analysis, no one knows what the migration actually entails. The programme launches with 40 workstreams, each defining their own scope. After 2 years: 60% of systems migrated, no two in the same way, 30% of integrations broken, no measurable business outcome achieved.

**THE BREAKING POINT:**
The CEO asks: "Where are we on the cloud migration?" No one can answer accurately because the scope was never formally defined. The current state was not documented, so no one knows what "100% migrated" means. The target state was a slide in a presentation, not an architecture.

**THE INVENTION MOMENT:**
TOGAF''s Architecture Development Method codified As-Is/To-Be as a systematic practice: document the current architecture (Phase B/C/D), define the target architecture (same phases), perform gap analysis (Phase E), produce a migration plan (Phase F). This phased approach - still the standard today - ensures that the distance between current and target is explicitly known before committing to a programme.

**EVOLUTION:**
Early As-Is/To-Be was a document-heavy, waterfall process: months spent documenting the current state before defining the future. Modern practice uses a "thin slice" approach: capture the minimum current-state information needed to answer the gap question for the specific initiative, rather than a complete inventory. This makes As-Is/To-Be viable in agile organisations.

---

### 📘 Textbook Definition

**As-Is architecture** (current state) is a structured description of the enterprise''s existing business capabilities, data assets, applications, and technology components. **To-Be architecture** (target state) is the desired future architecture that supports the business strategy. The **gap analysis** identifies the delta between them, and the **architecture roadmap** is the time-phased plan to close that gap.

---

### ⏱️ Understand It in 30 Seconds

**One line:** As-Is shows where you are; To-Be shows where you need to be; gap analysis shows what has to change; the roadmap shows how to get there.

> Think of navigation. As-Is is your current GPS location. To-Be is your destination. Gap analysis is the calculated route. The roadmap is the turn-by-turn directions. You cannot plot a route without knowing both your current location and your destination. The mistake most organisations make is jumping straight to "turn-by-turn directions" (individual projects) without first establishing either the current location or the destination.

**One insight:** The most valuable part of As-Is/To-Be is not the documentation - it is the conversations that happen when current-state reality confronts target-state ambition and someone has to reconcile them.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. You cannot plan a journey without knowing your starting point. Organisations that skip As-Is discovery consistently underestimate migration scope.
2. A target state without a gap analysis is a wish, not a plan.
3. The gap analysis should produce a prioritised list of changes, not just a diff. Not all gaps are equally important or equally feasible.
4. The roadmap must be realistic about sequencing - some changes are prerequisites for others (infrastructure before applications; data migration before application retirement).

**DERIVED DESIGN:**
Standard four-artefact structure:
1. **As-Is Architecture** - current state across BDAT domains
2. **To-Be Architecture** - target state across BDAT domains
3. **Gap Analysis** - delta between As-Is and To-Be, with prioritisation
4. **Architecture Roadmap** - time-phased sequence of transitions

**THE TRADE-OFFS:**
**Gain:** Explicit scope. Realistic programme planning. Shared understanding between business and IT.
**Cost:** Time to document current state accurately. Risk of over-engineering the future state (target state becomes a wish list). Difficulty keeping the roadmap current as the business changes.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Any significant technology change requires knowing what exists and what is needed.
**Accidental:** Documenting every aspect of the current state before starting. Full As-Is documentation is almost never needed; just enough to understand the gap.

---

### 🧪 Thought Experiment

**SETUP:** An organisation decides to consolidate 5 customer databases into 1 canonical customer data store. Two approaches: Approach A (no As-Is/To-Be) and Approach B (full As-Is/To-Be for the data domain only).

**WHAT HAPPENS WITHOUT As-Is/To-Be (Approach A):** The consolidation project starts. Six months in, the team discovers: one database uses Social Security Numbers as primary keys (cannot change without affecting 12 downstream systems), one database has 4M records with no email field (assumed present), one database is written to by a batch job that no one currently maintains. Programme scope triples. Budget exhausted before consolidation complete.

**WHAT HAPPENS WITH As-Is/To-Be (Approach B):** Before the project starts: As-Is maps all 5 databases, their schemas, their upstream writers, and their downstream readers. Gap analysis finds the SSN primary key issue and the missing email field. To-Be defines the canonical schema and migration strategy. The programme plan includes specific projects for SSN re-keying and email enrichment before consolidation. Delivered on time and budget.

**THE INSIGHT:** The As-Is/To-Be exercise did not eliminate complexity - it found the complexity before it hit the programme. Discovery during planning costs days; discovery during delivery costs months.

---

### 🧠 Mental Model / Analogy

> Think of a building renovation. As-Is is the structural survey: what walls are load-bearing, where are the pipes, what is the wiring layout. To-Be is the architect''s new floor plan: open plan living, new kitchen, extended bedroom. Gap analysis is the structural engineer''s assessment: which changes are feasible given the survey, which are not, what must be done first (remove load-bearing wall = steel beam first). The roadmap is the construction schedule. A renovation without a structural survey is how walls collapse.

- **Structural survey** = As-Is architecture documentation
- **Architect''s floor plan** = To-Be architecture
- **Structural engineer''s assessment** = Gap analysis
- **Construction schedule** = Architecture roadmap
- **Hidden pipes and wiring** = Legacy system dependencies that only appear on inspection

Where this analogy breaks down: buildings are physical and fully inspectable; IT systems are often undocumented and their dependencies are discovered only during change.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
As-Is/To-Be is the process of documenting where you are today (current architecture), deciding where you need to be (target architecture), understanding what needs to change (gap analysis), and planning how to get there (roadmap).

**Level 2 - How to use it (junior developer):**
When you join a migration or modernisation project, ask for the As-Is and To-Be documents before writing a line of code. As-Is tells you what systems you are working with and what their constraints are. To-Be tells you what the final state should look like. Gap analysis tells you what your project is specifically responsible for. Without these, you may solve the wrong problem.

**Level 3 - How it works (mid-level engineer):**
As-Is/To-Be in practice is scoped to the relevant BDAT domains for the initiative. A data migration project requires As-Is and To-Be only for the Data and Application domains. A cloud migration requires As-Is and To-Be primarily for the Technology and Application domains. The gap analysis produces a list of changes categorised as: eliminate (retire), add (create), modify (transform), and retain (keep as-is). The roadmap sequences these changes respecting dependencies.

**Level 4 - Why it was designed this way (senior/staff):**
The formal As-Is/To-Be structure was designed to make the cost of change legible before commitment. Waterfall projects failed partly because scope discovery happened during delivery. The As-Is/To-Be technique moves discovery to the planning phase, where scope changes cost time, not rework. Modern adaptations (thin-slice As-Is, rolling 90-day To-Be) preserve this benefit while reducing the overhead of comprehensive documentation.

**Expert Thinking Cues:**
- The As-Is that surprises you most is the most valuable: the undocumented system, the informal integration, the data flow no one knew about.
- The To-Be that is hardest to agree on reveals the deepest organisational conflict: two business units with incompatible views of the future.
- The gap analysis items that are hardest to prioritise are the most important to escalate: they represent strategic choices that only leadership can make.

---

### ⚙️ How It Works (Mechanism)

**Phase 1 - As-Is Discovery (days to weeks):**
Scope to the relevant BDAT domains. Use: existing documentation (unreliable - always verify), system inventories, network maps, interviews with system owners, automated discovery tools (ServiceNow CMDB, cloud asset inventories). Output: structured description of current capabilities, applications, data flows, and technology. Flag every undocumented dependency.

**Phase 2 - To-Be Definition (days to weeks):**
Start from business strategy and capability gaps (SAP-067). Define the target across the same BDAT domains. The To-Be should be specific enough to be actionable but not so detailed that it becomes a design specification (design is done during implementation).

**Phase 3 - Gap Analysis:**
For each element in As-Is and To-Be:
```
RETIRE: Exists in As-Is; not in To-Be
ADD:    Exists in To-Be; not in As-Is
MODIFY: Exists in both; transformation required
RETAIN: Exists in both; no change required
```
Prioritise gaps by: business impact, dependency order, feasibility, and risk.

**Phase 4 - Architecture Roadmap:**
Sequence the gap-closing changes into time-phased workstreams. Respect prerequisites. Identify programme boundaries (which changes belong to which projects). Include decision points where the roadmap may need to be revised based on outcomes.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Business Strategy + Capability Map
          |
          v
    [As-Is Discovery]
    Current Capabilities
    Current Applications
    Current Data Flows
    Current Technology         <- YOU ARE HERE
          |
          v
    [To-Be Definition]
    Target Capabilities
    Target Applications
    Target Data Model
    Target Technology
          |
          v
    [Gap Analysis]
    RETIRE / ADD / MODIFY / RETAIN list
          |
          v
    [Architecture Roadmap]
    Workstream 1 --> Workstream 2 --> ...
          |
          v
    Project Portfolio (Delivery)
```

**FAILURE PATH:**
Skip As-Is → define ambitious To-Be → gap analysis reveals As-Is was more complex than assumed → roadmap is revised repeatedly during delivery → programme loses credibility → business confidence in EA collapses.

**WHAT CHANGES AT SCALE:**
At small scale: As-Is is a whiteboard diagram; To-Be is a design doc; gap analysis is a bullet list. At medium scale: formal documents in EA tooling, stakeholder sign-off required. At large scale: As-Is discovery is a dedicated workstream using automated tooling; To-Be is ratified by Architecture Board; roadmap is a programme of programmes with dependencies managed across dozens of workstreams.

---

### 💻 Code Example

```yaml
# BAD - To-Be defined without As-Is
# (missing discovery; scope unknown)
to_be:
  target: "Cloud-native microservices platform"
  timeline: "18 months"
  # No As-Is, no gap analysis - this is a wish,
  # not an architecture plan
```

```yaml
# GOOD - structured As-Is / To-Be / Gap analysis

as_is:
  applications:
    - id: APP-001
      name: Legacy Order Management System
      tech: Java 8, Oracle DB on-premises
      capabilities: [CAP-001, CAP-003]
      data_owns: [order, order-line-item]
      integrations: [APP-002, APP-005, APP-009]
      lifecycle: retire
      risk: high  # No vendor support post-2025

    - id: APP-002
      name: Customer Portal
      tech: AngularJS, Node.js, PostgreSQL
      capabilities: [CAP-002]
      data_owns: [customer-profile]
      integrations: [APP-001, APP-007]
      lifecycle: retain-and-modernise

to_be:
  applications:
    - id: APP-010
      name: Order Management Service
      tech: Java 21, PostgreSQL, Kubernetes
      capabilities: [CAP-001, CAP-003]
      data_owns: [order, order-line-item]
      replaces: APP-001

    - id: APP-002-v2
      name: Customer Portal (Modernised)
      tech: React, Node.js, PostgreSQL
      capabilities: [CAP-002]
      data_owns: [customer-profile]
      replaces: APP-002

gap_analysis:
  retire:
    - app: APP-001
      blocker: APP-002 integration must be
               re-pointed to APP-010 first
      sequence: 3
  add:
    - app: APP-010
      prerequisites: data migration from APP-001
      sequence: 2
  modify:
    - app: APP-002 -> APP-002-v2
      scope: UI framework migration only
      sequence: 1
```

---

### ⚖️ Comparison Table

| Approach | Scope | Detail | When to Use |
|:---------|:------|:-------|:------------|
| **Full As-Is/To-Be** | All BDAT domains | Comprehensive | Major transformation programme |
| **Thin-slice As-Is/To-Be** | Relevant domains only | Minimum viable | Specific initiative or project |
| **Rolling To-Be (90-day)** | Current sprint focus | Agile | Continuous architecture evolution |
| **Architecture Spike** | Single unknowns only | Experimental | When As-Is includes unknowns requiring prototyping |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:--------------|:--------|
| "As-Is documentation must be complete before To-Be can start" | As-Is and To-Be can be developed iteratively; just-enough As-Is for each domain |
| "To-Be is the final architecture" | To-Be is a planning horizon (typically 2-5 years); it will be revised as the business evolves |
| "Gap analysis is just a diff of two diagrams" | Gap analysis requires prioritisation, sequencing, and feasibility assessment - not just identification of differences |
| "As-Is/To-Be is a waterfall technique" | The technique is methodology-agnostic; it can be applied in agile contexts with thin slices and rolling horizons |
| "The roadmap produced is a commitment" | The roadmap is a plan; it should include explicit decision points where it may be revised based on changing business needs |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: As-Is documentation takes too long**
**Symptom:** The As-Is documentation exercise takes 6-12 months; by the time it is complete, it is already out of date. The To-Be is never reached.
**Root Cause:** Over-scoped As-Is; attempting to document everything rather than the minimum needed to answer the gap question.
**Diagnostic:**
```
Ask: "What specific decisions does
this As-Is documentation need to support?"
If the answer is vague: the scope is too large.
```
**Fix:**
- BAD: Document every system in every detail
- GOOD: Document only the systems and domains relevant to the initiative''s gap analysis
**Prevention:** Define the As-Is scope by working backwards from the gap questions that need answering.

**Failure Mode 2: To-Be is a technology wish list**
**Symptom:** The To-Be architecture includes every emerging technology the team wants to adopt, regardless of business justification. The gap analysis produces an impossibly large list of changes.
**Root Cause:** To-Be defined by IT aspirations rather than business capabilities and strategic requirements.
**Diagnostic:**
```
For each To-Be element, ask:
"Which business capability does this enable or improve?"
If no clear answer: it should not be in the To-Be.
```
**Fix:** Anchor every To-Be element to a capability requirement from the business capability map.
**Prevention:** Require business stakeholder sign-off on the To-Be; they will reject elements with no business justification.

**Security Failure Mode: Security not in gap analysis**
**Symptom:** The migration delivers the To-Be functional architecture but introduces security regressions because security requirements were not included in the gap analysis.
**Root Cause:** Gap analysis performed only for functional capabilities; security, compliance, and non-functional requirements not included.
**Fix:**
- BAD: Gap analysis limited to functional capabilities and applications
- GOOD: Gap analysis includes security capabilities, compliance requirements, and non-functional targets (availability, performance, data residency)
**Prevention:** Include a dedicated security architecture review as a mandatory step in gap analysis.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- SAP-065 - Enterprise Architecture - What It Is and Why It Exists
- SAP-066 - Enterprise Architecture Domains - BDAT
- SAP-067 - Business Capability Mapping

**Builds On This (learn these next):**
- SAP-069 - TOGAF Framework (formalises As-Is/To-Be as part of ADM)
- SAP-055 - Legacy Modernization Strategy (As-Is/To-Be applied to legacy)
- SAP-007 - Technology Roadmap

**Alternatives / Comparisons:**
- SAP-053 - Architecture Decision Records (ADR) Strategy (captures decisions, not states)
- SAP-056 - Architecture Fitness Functions (validates current state against target)

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════════════╗
║ WHAT IT IS    The four-artefact EA planning      ║
║               technique: As-Is, To-Be, Gap, Road ║
║ PROBLEM       Programmes fail because scope was  ║
║               not defined before commitment      ║
║ KEY INSIGHT   Discovery during planning costs    ║
║               days; during delivery, months      ║
║ USE WHEN      Any significant transformation,    ║
║               migration, or consolidation        ║
║ AVOID WHEN    Small isolated changes with no     ║
║               cross-system dependencies          ║
║ TRADE-OFF     Planning rigour vs speed to start  ║
║ ONE-LINER     "Where are we, where must we be,   ║
║                what must change, how do we get   ║
║                there?"                           ║
║ NEXT EXPLORE  SAP-069 TOGAF formalises this      ║
╚══════════════════════════════════════════════════╝
```

**If you remember only 3 things:**
1. As-Is = current state; To-Be = target state; Gap = what must change; Roadmap = how.
2. Scope As-Is to just-enough: document only what is needed to answer the gap questions.
3. The gap analysis must include sequencing and prerequisites, not just a list of differences.

**Interview one-liner:** "As-Is/To-Be is the EA practice of explicitly mapping the current architecture, defining the target architecture, performing gap analysis to identify what must be retired, added, or modified, and producing a time-phased roadmap that respects change sequencing and dependencies."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Before committing to a change programme, make the scope explicit by comparing current state to desired state. This principle applies at every level: sprint planning (current backlog vs sprint goal), product roadmapping (current product vs vision), and strategic planning (current capabilities vs strategic requirements).

**Where else this pattern appears:**
- **DevOps maturity models** - DORA metrics establish As-Is (current deployment frequency, lead time) and To-Be (target metrics), with a gap analysis that produces the transformation plan.
- **Database migration** - schema comparison tools (Liquibase, Flyway) automate the As-Is/To-Be/Gap pattern for database schemas.
- **Cloud migration** - the 6 R''s framework (Rehost, Replatform, Refactor, Rearchitect, Rebuild, Retire) is a gap analysis vocabulary: each R represents a category of change from As-Is on-premises to To-Be cloud.

---

### 💡 The Surprising Truth

The single most valuable output of an As-Is/To-Be exercise is often not the gap analysis or the roadmap - it is the discovery that the As-Is is significantly different from what anyone assumed. Gartner research (2018) across 200 enterprise transformation programmes found that 73% of programmes had their scope revised upward after completing As-Is discovery, with an average scope increase of 40%. The programmes that revised scope during planning delivered on budget; the programmes that discovered scope during delivery overran by an average of 2.3x. The As-Is exercise''s cost is almost always recovered in avoided scope surprises.

---

### 🧠 Think About This Before We Continue

**Question 1 (System Interaction):** During As-Is discovery for a cloud migration, you find an undocumented integration between the legacy order management system and a third-party logistics provider via a batch file transfer process. This integration is not in any system documentation. The logistics provider''s contract is up for renewal in 6 months. How does this discovery change the cloud migration roadmap, and what process would prevent similar undocumented integrations from appearing mid-programme?

*Hint:* Investigate how network traffic analysis tools and API gateway logs are used to discover actual integration patterns (as opposed to documented integrations) in large enterprises.

**Question 2 (Scale):** An organisation wants to maintain a continuously up-to-date As-Is architecture across 300 applications, updated in near-real-time as systems change. What tooling and process architecture is required, and what are the accuracy trade-offs of automated vs manual discovery?

*Hint:* Research how enterprise architecture management tools (LeanIX, iServer) integrate with cloud provider APIs, CMDBs, and CI/CD pipelines to maintain live application inventories.

**Question 3 (Design Trade-off):** Some agile-at-scale frameworks (SAFe, LeSS) argue that maintaining a formal As-Is/To-Be is incompatible with agile''s emphasis on responding to change, since the To-Be becomes outdated before it is delivered. How would you design an As-Is/To-Be practice that provides planning rigour while remaining responsive to business change?

*Hint:* Compare the "rolling wave planning" approach used in programme management with TOGAF''s concept of "architecture iteration" and how each handles the tension between planning horizon and adaptability.