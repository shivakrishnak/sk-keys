---
id: SAP-070
title: "TOGAF ADM (Architecture Development Method)"
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★☆
depends_on: SAP-069, SAP-068
used_by: SAP-073, SAP-074
related: SAP-066, SAP-067, SAP-007
tags:
  - architecture
  - intermediate
  - pattern
  - bestpractice
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 70
permalink: /software-architecture/togaf-adm/
---

# SAP-070 - TOGAF ADM (Architecture Development Method)

⚡ TL;DR - The ADM is TOGAF''s iterative, phase-structured process for developing and governing enterprise architectures, covering business through technology domains in a cycle from vision to implementation governance.

| SAP-070 | Category: Software Architecture Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | SAP-069, SAP-068 | |
| **Used by:** | SAP-073, SAP-074 | |
| **Related:** | SAP-066, SAP-067, SAP-007 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An enterprise architect is asked to "do enterprise architecture" for a cloud transformation. Without a defined process, she asks: Where do I start? What do I produce first? When is business architecture done and technology architecture started? Who approves what? When do I hand off to delivery? Every EA practitioner answers these questions differently, making EA output incomparable and EA practice un-scalable.

**THE BREAKING POINT:**
Two architects in the same organisation, working on different transformation streams, produce incompatible architecture artefacts: different notation, different artefact types, different levels of detail, different governance processes. Their work cannot be combined into a coherent enterprise view. The CIO cannot compare or consolidate the two streams.

**THE INVENTION MOMENT:**
TOGAF''s ADM was designed to answer all of these sequencing questions in one place. Its key insight: enterprise architecture development is always iterative - you cannot complete business architecture and then "finish" with technology. The domains are interdependent and must be revisited as decisions cascade through the layers. The ADM''s phase structure makes the iteration explicit and manageable.

**EVOLUTION:**
TOGAF 9 formalised the ADM with strict phase definitions and mandatory artefacts per phase. TOGAF 9.2 added guidance for adapting the ADM to agile and cloud contexts. TOGAF 10 (2022) made the ADM modular, removing mandatory artefacts and emphasising tailoring - acknowledging that organisations using agile delivery need a faster, lighter ADM cycle.

---

### 📘 Textbook Definition

The **Architecture Development Method (ADM)** is TOGAF''s core process: an iterative cycle of phases that guides the creation, governance, and maintenance of enterprise architectures. It consists of a Preliminary Phase (establishing EA capability) and nine phases (A through H) covering architecture vision, BDAT domain development, solutions planning, migration planning, implementation governance, and architecture change management.

---

### ⏱️ Understand It in 30 Seconds

**One line:** The ADM is a cycle of 10 phases that tells you what to do (and in what order) to develop and govern enterprise architecture from vision to implementation.

> Think of the ADM as the construction project lifecycle. Phase A is the client brief (Architecture Vision). Phases B, C, D are the detailed design (Business, Data, Application, Technology architectures). Phase E is the cost estimate and bill of materials (Solutions). Phase F is the construction schedule (Migration Plan). Phase G is site supervision (Implementation Governance). Phase H is the snagging list and handback (Change Management). The whole cycle repeats for the next building.

**One insight:** The ADM is a CYCLE, not a linear process. After Phase H, the next iteration begins at Phase A (or wherever the trigger requires). Architecture is never "done."

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Architecture development must be driven by business requirements (Phase A before Phases B-D).
2. Architecture domains are developed in dependency order: Business drives Data needs; Data needs drive Application design; Applications drive Technology choices.
3. Implementation must be governed (Phase G) not just planned (Phase F).
4. Architecture must respond to change (Phase H) - every change is a potential trigger for a new ADM iteration.

**DERIVED DESIGN:**
The ADM wraps the BDAT dependency chain in governance phases:
```
Preliminary: Establish EA capability
     |
Phase A: Vision (scope + business case)
     |
Phase B: Business Architecture
     |
Phase C: Information Systems Architecture
         (Data + Application)
     |
Phase D: Technology Architecture
     |
Phase E: Opportunities and Solutions
     |
Phase F: Migration Planning
     |
Phase G: Implementation Governance
     |
Phase H: Architecture Change Management
     |
(loop back)
```

**THE TRADE-OFFS:**
**Gain:** Structured, repeatable, governable process. Shared understanding of what phase the programme is in. Clear input/output contracts between phases.
**Cost:** Heavyweight if followed completely. Sequential appearance can lead to waterfall implementation if not explicitly adapted.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Enterprise architecture development requires a sequenced process that respects domain dependencies and includes governance.
**Accidental:** All artefacts mandated by classic TOGAF 9 for phases that may not be relevant to the specific initiative.

---

### 🧪 Thought Experiment

**SETUP:** An organisation runs an ADM cycle for a data platform modernisation programme. Consider what happens if Phase E (Opportunities and Solutions) is done BEFORE Phase B (Business Architecture).

**WHAT HAPPENS WITHOUT PHASE ORDER:** The EA team jumps straight to Phase E and identifies a technology solution (Databricks on Azure). They proceed to Phase F (migration plan). 6 months into delivery, business stakeholders ask why the new platform does not support a business intelligence capability that was a strategic priority. The capability was never captured in Phase B. The gap costs 3 months of rework.

**WHAT HAPPENS WITH CORRECT PHASE ORDER:** Phase A establishes that the business priority is self-service BI for business units. Phase B maps the "Business Intelligence" capability and its requirements. Phase C identifies the data objects and applications that feed the BI capability. Phase D identifies the technology constraints. Phase E now selects Databricks because it demonstrably satisfies the Phase B capability requirements. No rework.

**THE INSIGHT:** The ADM''s phase order is not bureaucratic - it encodes the dependency chain between domains. Skipping phases skips the discovery that prevents rework.

---

### 🧠 Mental Model / Analogy

> Think of the ADM as a chef''s mise en place followed by cooking service. Preliminary phase: set up the kitchen (EA capability). Phase A: review tonight''s menu (Architecture Vision). Phases B-D: prepare all ingredients in order - protein, vegetables, sauces (Business, Application, Technology). Phase E: plan the service order (Solutions). Phase F: set up the pass and timing (Migration Plan). Phase G: manage service (Implementation Governance). Phase H: post-service debrief and menu adjustment for next service (Change Management). The cycle repeats every service. A restaurant that skips ingredient prep and goes straight to plating fails service every time.

- **Tonight''s menu** = Architecture Vision (Phase A)
- **Ingredient preparation** = BDAT architecture development (Phases B-D)
- **Service order** = Solutions and Migration Plan (Phases E-F)
- **Service management** = Implementation Governance (Phase G)
- **Post-service review** = Architecture Change Management (Phase H)

Where this analogy breaks down: a restaurant serves the same menu repeatedly; each ADM cycle produces a different architecture for a different strategic context.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
The ADM is a step-by-step guide for doing enterprise architecture. It tells you what to work on first (the business vision), what to work on next (the business processes and data), and how to make sure what you design actually gets built (governance). It repeats in cycles because business needs keep changing.

**Level 2 - How to use it (junior developer):**
If you are on a project that has EA involvement, the ADM explains why architects ask certain questions at certain times. In Phase B, they are mapping business capabilities (not yet technology). In Phase D, they are defining technology standards. In Phase G, they are reviewing your delivery against those standards. Understanding which ADM phase is current tells you what type of EA input to expect and what questions are appropriate to ask.

**Level 3 - How it works (mid-level engineer):**
Each ADM phase has defined inputs, steps, outputs (artefacts), and success criteria. Phases are iterative within and between cycles. An organisation may run multiple ADM cycles in parallel: one for a long-term transformation programme, one for a specific platform initiative, one for a compliance programme. Each cycle may be at a different phase simultaneously. Phase G is continuous - it does not end when a programme ends.

**Level 4 - Why it was designed this way (senior/staff):**
The ADM was designed to be comprehensive enough to govern any scale of architecture programme, which made it heavy. The original design assumed a waterfall-style programme where phases complete sequentially. Modern organisations run ADM cycles in sprints: a 2-week Phase A sprint to establish scope, 4-week Phase B/C/D sprints iterating with delivery teams, continuous Phase G through the programme. This requires explicit adaptation guidance, which TOGAF 10 now provides.

**Expert Thinking Cues:**
- When a programme is in crisis, check which ADM phase was skipped. Almost all programme failures trace to a skipped phase (usually Phase B - business architecture was assumed, not discovered).
- Phase H is the most undervalued phase. Organisations that skip it accumulate undocumented architecture drift until the next crisis.
- The ADM''s "Requirements Management" is not a phase - it is a continuous process that runs through all phases. Requirements changes at any phase can trigger rework in earlier phases.

---

### ⚙️ How It Works (Mechanism)

**Preliminary Phase - Establish EA Capability:**
Scope the EA function. Define organisation-specific tailoring of TOGAF. Establish Architecture Repository. Define governance framework. Output: EA capability and tailored framework.

**Phase A - Architecture Vision:**
Develop a high-level vision of the capability change and value delivery. Define scope, constraints, stakeholders. Produce Architecture Vision document and Statement of Architecture Work. Output: approved scope and business case for the architecture programme.

**Phase B - Business Architecture:**
Develop the Business Architecture. Map current and target business capabilities, value streams, and organisation model. Output: Business Architecture document, capability map, gap analysis.

**Phase C - Information Systems Architecture:**
Two sub-phases: Data Architecture (data assets, data ownership model, data migration approach) and Application Architecture (application portfolio, integration map, application lifecycle). Output: Data and Application Architecture documents.

**Phase D - Technology Architecture:**
Map the technology infrastructure required to support the Information Systems Architecture. Output: Technology Architecture document, technology standards catalogue.

**Phase E - Opportunities and Solutions:**
Identify and group change activity. Define work packages. Perform build-vs-buy analysis. Output: Architecture Roadmap (initial), transition architecture definitions.

**Phase F - Migration Planning:**
Prioritise projects. Assess costs, benefits, risks. Produce detailed Implementation and Migration Plan. Output: Implementation and Migration Plan.

**Phase G - Implementation Governance:**
Provide architecture oversight for each implementation project. Architecture compliance reviews. Update architecture baselines as implementations complete. Output: Architecture Contract, Compliance Assessment.

**Phase H - Architecture Change Management:**
Monitor for technology and business changes that require architecture update. Manage change requests. Decide whether to trigger a new ADM cycle. Output: Architecture Updates, ADM Cycle trigger.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Business Strategy Change / Programme Start
          |
          v
  [Preliminary] EA Capability Set Up
          |
          v
  [Phase A] Architecture Vision        <- YOU ARE HERE
    Scope: "Cloud migration for EU region"
    Stakeholders: CIO, CFO, BU Heads
          |
          v
  [Phase B] Business Architecture
    Capabilities: Customer Mgmt, Logistics
    Gap: Self-service BI missing
          |
          v
  [Phase C] Data + Application Architecture
    Data: Canonical customer schema
    Apps: Retire 4, Modernise 2, Add 1
          |
          v
  [Phase D] Technology Architecture
    Tech: Azure, AKS, Databricks, Kafka
          |
          v
  [Phase E] Solutions: 8 work packages
          |
          v
  [Phase F] Migration Plan: 3 wave roadmap
          |
          v
  [Phase G] Governance: per-project reviews
          |
          v
  [Phase H] Change Mgmt: 2 change requests
               triggers partial Phase B re-do
```

**FAILURE PATH:**
Phase A approved with unclear scope → Phase B business architecture missed → Phase C assumes business requirements that were not captured → Phase D technology chosen without business justification → Phase E produces a plan that cannot be validated against Phase A → programme fails governance review.

**WHAT CHANGES AT SCALE:**
At single-team scale: ADM phases collapse to sprint-level artefacts (Phase A = story mapping; Phase B = user journey mapping; Phase E = sprint backlog). At enterprise scale: dedicated EA team per phase; formal phase gate reviews; tooling integrations between phases; Architecture Repository as single source of truth for all phases.

---

### 🔁 Flow / Lifecycle

The ADM operates as an iterative lifecycle with three iteration types:

```
ITERATION TYPE 1: Full ADM Cycle
(for major transformation programmes)
Prelim → A → B → C → D → E → F → G → H
Timeline: 6-18 months per full cycle

ITERATION TYPE 2: Architecture Phase Iteration
(within a single phase)
e.g., Phase B: Baseline → Validate → Refine
Timeline: 2-4 weeks per iteration within phase

ITERATION TYPE 3: Cross-Phase Iteration
(triggered by downstream discovery)
e.g., Phase D finding triggers Phase C rework
"Tracing the impacted phases upward"
```

**ADM Phase Gate Criteria:**
Each phase must produce defined outputs before the next phase begins. Key gate checks:
- Phase A complete: Architecture Vision approved by sponsor
- Phase B complete: Business Architecture signed off by business owners
- Phase C complete: Data and Application architectures approved by data and application owners
- Phase D complete: Technology Architecture approved by infrastructure/platform owners
- Phase E complete: Roadmap approved, work packages defined
- Phase G ongoing: Compliance certificates issued per implementation project

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:--------------|:--------|
| "ADM phases must be completed sequentially and completely" | TOGAF explicitly allows parallel phases, phase iteration, and phase omission for specific contexts |
| "ADM is only relevant for large enterprises" | The ADM''s phase structure scales; the artefact depth does not |
| "Phase G ends when implementation ends" | Phase G is ongoing - it governs all architecture changes throughout the system''s lifecycle |
| "Requirements Management is a phase" | It is a continuous process running through all phases, not a phase itself |
| "ADM replaces project management" | ADM is an architecture process; it works alongside, not instead of, project management frameworks |
| "Phase H means the architecture is done" | Phase H is a trigger for the next ADM cycle - architecture is never done in a living enterprise |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Phase B (Business Architecture) skipped**
**Symptom:** Technology architecture is complete and delivery is underway, but business stakeholders report that the solution does not support key business capabilities.
**Root Cause:** Phase B was replaced by assumptions about business requirements.
**Diagnostic:**
```
Check: Is there a signed Phase B artefact
(Business Architecture document / Capability map)
with business owner sign-off?
No signed artefact = Phase B was skipped.
```
**Fix:** Retrospectively complete Phase B; assess gap against Phase C/D decisions already made; plan rework where Phase B requirements are not met.
**Prevention:** Make Phase B business owner sign-off a mandatory gate before Phase C begins.

**Failure Mode 2: Phase G absent**
**Symptom:** Implemented systems diverge from the Architecture Vision. Technical debt accumulates rapidly. The architecture baseline is out of date and no one knows the current state.
**Root Cause:** EA involvement ended at Phase F (Migration Planning); no governance during delivery.
**Diagnostic:**
```
Ask: When was the last Architecture Compliance
Assessment produced for an active project?
> 6 months ago: Phase G is not running.
```
**Fix:** Establish lightweight Phase G process: architecture review at project start, design review at midpoint, compliance assessment at close.
**Prevention:** Make Phase G a contractual requirement for all projects above a complexity threshold.

**Security Failure Mode: Security compliance not included in Phase G**
**Symptom:** Projects pass Phase G architecture compliance review but introduce security vulnerabilities because the compliance assessment does not include security controls.
**Root Cause:** Phase G compliance checklist does not include security architecture requirements.
**Fix:**
- BAD: Phase G compliance = functional architecture only
- GOOD: Phase G compliance includes: security control mapping, threat model review, data classification compliance, and regulatory compliance check
**Prevention:** Embed security architecture as a required component of Phase G compliance assessment template.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- SAP-069 - TOGAF Framework
- SAP-068 - As-Is / To-Be Architecture
- SAP-066 - Enterprise Architecture Domains - BDAT

**Builds On This (learn these next):**
- SAP-073 - Enterprise Architecture Maturity Models
- SAP-074 - Enterprise Architecture Programme Design

**Alternatives / Comparisons:**
- SAP-071 - Zachman Framework (what to describe, not how to develop)
- SAP-055 - Legacy Modernization Strategy (applies ADM to legacy context)

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════════════╗
║ WHAT IT IS    TOGAF''s iterative 10-phase process ║
║               for developing enterprise arch     ║
║ PROBLEM       No shared process for EA; every    ║
║               architect invents their own        ║
║ KEY INSIGHT   ADM is a CYCLE, not a sequence;    ║
║               Phase H triggers the next A        ║
║ USE WHEN      Planning or running an EA          ║
║               programme; multi-domain initiative  ║
║ AVOID WHEN    Single-system design; agile sprint ║
║               without explicit ADM tailoring     ║
║ TRADE-OFF     Structured process and governance  ║
║               vs heavyweight if not tailored     ║
║ ONE-LINER     "The 10-phase recipe for           ║
║                enterprise architecture"          ║
║ NEXT EXPLORE  SAP-071 Zachman, SAP-073 EA Maturity║
╚══════════════════════════════════════════════════╝
```

**If you remember only 3 things:**
1. ADM has 10 phases: Preliminary + A through H - Business architecture (Phase B) before technology (Phase D).
2. The ADM is a cycle: Phase H triggers the next iteration; architecture is never finished.
3. Phase G (Implementation Governance) is the most commonly skipped and most consequential phase.

**Interview one-liner:** "The TOGAF ADM is a 10-phase iterative cycle for enterprise architecture development: Preliminary sets up EA capability; Phase A establishes vision; Phases B-D develop architecture across the BDAT domains; Phases E-F plan solutions and migration; Phase G governs implementation; Phase H manages change and triggers the next cycle."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Any complex change process benefits from phase gates that ensure upstream decisions are validated before committing to downstream work. This prevents discovery of upstream gaps during downstream delivery, where the cost of change is highest.

**Where else this pattern appears:**
- **Software SDLC** - Requirements before design, design before code, code before test - the same dependency chain as ADM''s phase order.
- **Clinical trials (Phase 1-4)** - Each phase gate validates safety and efficacy before committing to the next, more expensive, phase - the same principle as ADM phase gates.
- **Infrastructure provisioning (Terraform plan before apply)** - The plan phase (analogous to ADM E/F) must complete before the apply phase (analogous to Phase G delivery), ensuring the change is understood before being committed.

---

### 💡 The Surprising Truth

The single most impactful ADM phase for programme success is Phase B (Business Architecture) - yet it is consistently the most poorly executed. A study of TOGAF implementations by The Open Group (2016) found that organisations that skipped or abbreviated Phase B had a 3.4x higher rate of programme rework than those that executed it fully. The reason is counterintuitive: Phase B feels like it produces the least technical content (business capability maps are not code), but it captures the assumptions that all subsequent phases depend on. When Phase B assumptions are wrong or unstated, the errors compound through Phase C, D, E, and F, becoming most expensive to fix during Phase G delivery governance.

---

### 🧠 Think About This Before We Continue

**Question 1 (System Interaction):** During Phase G (Implementation Governance) of a cloud migration, a delivery team discovers that the technology chosen in Phase D cannot support the performance requirements from Phase C (Information Systems Architecture). The team is 6 months into delivery. How should Phase G handle this discovery, and what does the ADM say about cross-phase rework triggered during governance?

*Hint:* Investigate TOGAF''s concept of "Architecture Contracts" and how they establish the agreed-upon architecture that Phase G governs against, and what the process is for raising an Architecture Change Request when delivery reveals a design flaw.

**Question 2 (Scale):** An organisation runs 12 concurrent ADM cycles at different stages - 3 major transformation programmes and 9 smaller platform initiatives. How should the Architecture Repository be structured to manage the artefacts from 12 concurrent cycles without creating conflicts or inconsistencies between them?

*Hint:* Research TOGAF''s Architecture Repository structure (Solutions Landscape, Architecture Landscape, Standards Library, Governance Log) and how the Enterprise Continuum classifies artefacts from generic to organisation-specific to resolve conflicts between concurrent cycles.

**Question 3 (Design Trade-off):** TOGAF ADM''s iterative cycle assumes that architecture work precedes delivery work. In a continuous delivery environment where code ships daily, how would you adapt the ADM so that architecture governance and delivery are truly continuous rather than phase-gated?

*Hint:* Compare how Architecture Fitness Functions (SAP-056) provide a continuous automated form of Phase G governance, and how "Architecture as Code" practices enable Phase D Technology Architecture to be expressed as infrastructure code that delivery teams use directly.