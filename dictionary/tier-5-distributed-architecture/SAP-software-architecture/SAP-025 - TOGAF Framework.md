---
id: SAP-022
title: TOGAF Framework
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★☆
depends_on: SAP-037, SAP-038, SAP-049, SAP-050
used_by: SAP-013, SAP-084, SAP-085
related: SAP-014, SAP-015, SAP-027
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
nav_order: 25
permalink: /software-architecture/togaf-framework/
---

# SAP-051 - TOGAF Framework

⚡ TL;DR - TOGAF (The Open Group Architecture Framework) is the world''s most widely adopted enterprise architecture framework, providing a process (ADM), vocabulary, governance model, and artefact library for practising EA consistently across an organisation.

| SAP-051 | Category: Software Architecture Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | SAP-037, SAP-038, SAP-049, SAP-050 | |
| **Used by:** | SAP-013, SAP-084, SAP-085 | |
| **Related:** | SAP-014, SAP-015, SAP-027 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every enterprise architect at every organisation invents their own EA process. Organisation A calls their capability model a "function map." Organisation B calls the same thing a "service catalogue." Organisation C calls it a "value chain." No one can compare approaches, share artefacts, or move between organisations without starting from scratch. Vendors cannot build tooling that works across organisations. Training cannot be standardised. EA becomes a bespoke craft that dies with the practitioner who invented it.

**THE BREAKING POINT:**
A CIO at a large bank tries to hire an experienced EA practitioner. The candidate has 10 years of EA experience at another bank, but their entire method is incompatible with the current organisation''s approach. There is no shared vocabulary, no shared artefact format, no shared governance model. The practitioner''s experience is only partially transferable.

**THE INVENTION MOMENT:**
The Open Group, a vendor-neutral standards consortium, published TOGAF in 1995 based on the US Department of Defense Technical Architecture Framework for Information Management (TAFIM). The goal was to create a vendor-neutral, organisation-neutral framework that any enterprise could adopt, giving EA a common language, common process, and common artefact vocabulary that practitioners could carry from organisation to organisation.

**EVOLUTION:**
TOGAF has evolved through major versions: TOGAF 7 (technical architecture focus), TOGAF 8 (business architecture added), TOGAF 9 (full BDAT coverage, Architecture Content Framework), TOGAF 9.2 (2018, simplified and cloud-aware), TOGAF Standard Version 10 (2022, modular, agile-compatible, simplified content framework). Each version increased flexibility and reduced mandatory prescription, responding to criticism that earlier versions were too heavyweight for modern organisations.

---

### 📘 Textbook Definition

**TOGAF (The Open Group Architecture Framework)** is a framework for enterprise architecture providing: (1) the Architecture Development Method (ADM) - a process for creating and managing enterprise architectures, (2) the Architecture Content Framework - a model for structuring EA artefacts, (3) the Enterprise Continuum - a repository of reusable architecture assets, (4) Architecture Capability Framework - a model for establishing an EA function. TOGAF is maintained by The Open Group and is freely available to member organisations.

---

### ⏱️ Understand It in 30 Seconds

**One line:** TOGAF gives EA practitioners a shared language, a repeatable process, and a governance model that works across organisations and industries.

> Think of TOGAF as ISO 9001 for enterprise architecture. ISO 9001 does not tell you exactly how to run your factory, but it gives you a standard quality management process, vocabulary, and audit criteria that any certified practitioner can apply. TOGAF does the same for EA: a standard process, vocabulary, and governance model that any TOGAF-certified practitioner can apply in any organisation.

**One insight:** TOGAF is not a methodology to be implemented completely - it is a framework to be adapted. No organisation uses 100% of TOGAF. The value is in the parts you adopt, not the parts you skip.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. TOGAF is a process framework, not a prescriptive method. It says WHAT to do at each stage, not exactly HOW.
2. TOGAF is designed to be tailored. Its documents explicitly encourage organisations to adapt, subset, and extend it.
3. TOGAF''s primary value is its common vocabulary. The ability to say "we are in ADM Phase C" and have any TOGAF practitioner understand the context is worth more than any specific process step.
4. TOGAF works at the programme level, not the project level. It structures multi-year architecture programmes, not individual project deliveries.

**DERIVED DESIGN:**
TOGAF has four main components:
- **ADM** (Architecture Development Method): the iterative process for doing EA
- **Architecture Content Framework**: taxonomy of EA artefacts (deliverables, artefacts, building blocks)
- **Enterprise Continuum**: repository of reusable architecture assets from generic to specific
- **Architecture Capability Framework**: how to establish and run the EA function

**THE TRADE-OFFS:**
**Gain:** Standard vocabulary. Certified practitioner community. Tooling ecosystem. Training and certification infrastructure. Adaptable to context.
**Cost:** Risk of "TOGAF theatre" - producing all the mandated artefacts without any of the business outcomes. Heavy if implemented without tailoring. The certification (TOGAF Part 1 and Part 2) tests knowledge of the framework, not ability to do EA.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** A large enterprise genuinely benefits from a standard EA process and vocabulary.
**Accidental:** TOGAF''s full document set, implemented without tailoring, for a 200-person organisation.

---

### 🧪 Thought Experiment

**SETUP:** Two organisations of the same size adopt TOGAF for their cloud transformation programme. Organisation A implements "full TOGAF" - all phases, all artefacts, all governance. Organisation B implements "TOGAF Lite" - ADM phases adapted to 2-week sprints, five core artefacts, lightweight governance.

**WHAT HAPPENS WITH FULL TOGAF (Organisation A):** The EA team spends 18 months in Phases A through D producing comprehensive architecture documents. The delivery team, waiting for architecture sign-off, begins the migration anyway using their own judgement. When the EA artefacts are published, they describe what has already been built - not a forward plan. The EA function is bypassed for future decisions because it is too slow.

**WHAT HAPPENS WITH TOGAF LITE (Organisation B):** The EA team runs Phase A and Phase B in a 4-week sprint, producing a capability gap analysis and business requirements. Phase C and D are done in parallel with delivery, informing decisions in real-time. The EA team participates in sprint reviews. Architecture decisions are made with EA input at the sprint level. The cloud migration is delivered with coherent architecture across all workstreams.

**THE INSIGHT:** TOGAF''s value is not in its completeness but in its structure. The ADM''s phase sequence remains valid even when accelerated. The artefacts remain useful even when simplified. The governance model remains relevant even when made lightweight.

---

### 🧠 Mental Model / Analogy

> Think of TOGAF as a recipe book for enterprise architecture. A recipe book does not tell you exactly what to cook or how much to scale. It gives you a set of tried-and-tested recipes (ADM phases), a vocabulary (terms like "mise en place," "reduction," "deglaze"), and a method (prepare ingredients before cooking, not during). A trained chef (TOGAF-certified EA) can adapt any recipe to the ingredients available and the number of guests. The recipe book''s value is in the structure, not in following it exactly.

- **Recipe book** = TOGAF framework
- **Individual recipe** = ADM phase
- **Cooking vocabulary** = TOGAF terminology (deliverable, artefact, building block)
- **Trained chef** = TOGAF-certified enterprise architect
- **Adapting for dietary requirements** = Tailoring TOGAF for your organisation

Where this analogy breaks down: recipes are for single dishes; TOGAF is for multi-year architecture programmes that must adapt to changing conditions.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
TOGAF is a widely used standard that tells organisations how to do enterprise architecture - what steps to follow, what documents to produce, and what vocabulary to use. Like a standard project management framework (PRINCE2, PMP), it gives EA a common language that practitioners can use across organisations.

**Level 2 - How to use it (junior developer):**
As a developer, you encounter TOGAF through: architecture reviews (the organisation may follow TOGAF''s Phase G governance), artefacts (architecture diagrams produced in TOGAF''s notation), and vocabulary (architects may reference "ADM phases" in planning meetings). Understanding TOGAF''s four domains (BDAT) helps you understand why architecture decisions are made. You are not expected to practise TOGAF, but knowing its vocabulary makes EA conversations clearer.

**Level 3 - How it works (mid-level engineer):**
TOGAF structures EA through the ADM (see SAP-013). Beyond the ADM, TOGAF provides: the Architecture Content Framework (what artefacts exist and what they describe), the Architecture Repository (where artefacts are stored and classified), the Enterprise Continuum (a spectrum from generic architectures to organisation-specific solutions), and the Architecture Capability Framework (how to build and run an EA team). In practice, most organisations use the ADM and selected parts of the Content Framework, discarding the rest.

**Level 4 - Why it was designed this way (senior/staff):**
TOGAF was designed to be comprehensive enough to apply to any enterprise in any industry, which required it to be generic and flexible. This generality is both its strength (wide applicability) and its weakness (requires significant tailoring for any specific context). TOGAF Version 10 made modularity explicit: organisations can adopt only the modules relevant to their context. The certification programme was designed to create a portable practitioner skill set, but critics argue it tests framework knowledge rather than architectural thinking ability.

**Expert Thinking Cues:**
- When an organisation says "we use TOGAF," ask what they actually mean: full ADM? Just the vocabulary? Just the governance model? Most use a subset.
- TOGAF certification (Part 1, Part 2) is a baseline; producing real EA outcomes requires experience that no certification validates.
- The most useful TOGAF concept for most senior engineers is the Architecture Content Framework''s distinction between deliverables (contractual), artefacts (work products), and building blocks (reusable components).

---

### ⚙️ How It Works (Mechanism)

**TOGAF''s four components:**

**1. Architecture Development Method (ADM):**
The iterative cycle of phases (see SAP-013) that guides the development of enterprise architecture from a business vision through to implementation governance. The ADM is the core of TOGAF.

**2. Architecture Content Framework:**
A taxonomy of EA artefacts grouped into:
- **Deliverables** - contractual work products (e.g., Architecture Vision document)
- **Artefacts** - specific models within deliverables (e.g., capability map, application diagram)
- **Architecture Building Blocks (ABBs)** - generic reusable components (e.g., "Authentication Service" as an abstract capability)
- **Solution Building Blocks (SBBs)** - specific implementations (e.g., "Azure Active Directory" as an SBB implementing Authentication Service)

**3. Enterprise Continuum:**
A spectrum from generic to specific:
```
Foundation Architectures (most generic)
        |
Common Systems Architectures
        |
Industry Architectures (e.g., BIAN for banking)
        |
Organisation-Specific Architectures (most specific)
```
Encourages reuse: an organisation-specific architecture should build on industry architectures, which build on common systems architectures.

**4. Architecture Capability Framework:**
Guidance for establishing and operating an EA function: roles, responsibilities, processes, governance, and maturity model.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Business Strategy Input
      |
      v
[Phase A: Architecture Vision]
  Scope, stakeholders, business case
      |
      v
[Phase B/C/D: Architecture Development]     <- YOU ARE HERE
  Business / Data / Application / Technology
      |
      v
[Phase E/F: Solutions and Migration Planning]
  Gap analysis, roadmap, project portfolio
      |
      v
[Phase G: Implementation Governance]
  Architecture review, compliance
      |
      v
[Phase H: Architecture Change Management]
  Trigger for next ADM iteration
      |
      v (loop back to Phase A)
```

**FAILURE PATH:**
TOGAF adopted without tailoring → full artefact suite required → EA team produces documents for months → delivery begins without EA input → artefacts describe what was built rather than informing what to build → EA function loses credibility.

**WHAT CHANGES AT SCALE:**
At small scale (< 200 employees): TOGAF is overkill; select vocabulary and lightweight governance only. At medium scale (200-5,000): ADM adapted to agile cadence; 5-10 core artefacts; lightweight Architecture Review Board. At large scale (5,000+): full ADM with dedicated EA team, tooling, formal governance, and TOGAF-aligned Architecture Repository.

---

### ⚖️ Comparison Table

| Framework | Type | Strength | Weakness | Best For |
|:----------|:-----|:---------|:---------|:---------|
| **TOGAF** | Process framework | Comprehensive, widely adopted, certified community | Heavy without tailoring; certification tests knowledge not skill | Large enterprises needing standard EA process |
| **Zachman** | Classification framework | Complete taxonomy; excellent for gap analysis | No process guidance; overwhelming to implement fully | Auditing EA completeness; legacy analysis |
| **Gartner EA** | Outcome framework | Business-outcome focus; lighter than TOGAF | Proprietary; requires Gartner relationship | Organisations prioritising business agility |
| **FEAF** | Government framework | Compliance-aligned; inter-agency coordination | US government specific | US federal agencies |
| **ArchiMate** | Modelling language | Precise notation; integrates with TOGAF | Steep learning curve; requires tooling | EA diagramming and cross-domain modelling |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:--------------|:--------|
| "TOGAF must be implemented completely to be useful" | TOGAF explicitly encourages tailoring; partial adoption of ADM phases and selected artefacts is the norm |
| "TOGAF certification means the person can do EA" | Certification tests knowledge of the framework; practical EA ability requires experience |
| "TOGAF is only for large enterprises" | The framework scales; the tailoring determines the complexity of implementation |
| "TOGAF and Zachman are competitors" | They complement each other; TOGAF is a process, Zachman is a classification system; many organisations use both |
| "TOGAF Version 10 replaced everything before it" | Version 10 is modular; earlier TOGAF 9.2 knowledge remains valid for organisations using that version |
| "ArchiMate is part of TOGAF" | ArchiMate is a separate standard (also from The Open Group) that pairs well with TOGAF but is not part of it |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: TOGAF theatre**
**Symptom:** The organisation has TOGAF-certified architects producing all required artefacts, but no EA input influences any actual delivery decision.
**Root Cause:** TOGAF implemented as compliance, not as decision support. Artefacts produced because they are required, not because they answer questions.
**Diagnostic:**
```
Ask delivery leads:
"Name the last 3 architecture decisions
that were influenced by the EA team''s
TOGAF artefacts."
If no clear answer: TOGAF theatre.
```
**Fix:** Redefine EA success as decisions influenced, not artefacts produced. Retire artefacts that no stakeholder references.
**Prevention:** Before starting any TOGAF phase, identify the specific decisions the phase output must support and the stakeholders who will use it.

**Failure Mode 2: ADM treated as waterfall**
**Symptom:** The EA team completes Phase A through D in sequence over 12 months before any delivery begins. By the time delivery starts, business requirements have changed and the architecture is outdated.
**Root Cause:** ADM phases treated as strict sequential stages rather than iterative cycles.
**Diagnostic:**
```
Check: has any delivery decision been made
using EA artefacts from the current ADM cycle?
If not in 90 days: ADM is running too slow.
```
**Fix:** Run ADM phases in parallel with delivery; use 90-day rolling architecture horizons. TOGAF explicitly allows iterating within and between phases.
**Prevention:** Time-box each ADM phase to the delivery cadence of the programme it supports.

**Security Failure Mode: Security not modelled in Architecture Content Framework**
**Symptom:** TOGAF artefacts cover Business, Data, Application, and Technology domains but do not include security controls or threat models. Security is added as an afterthought in Phase G.
**Root Cause:** TOGAF''s standard artefact catalogue does not mandate security artefacts; they must be explicitly added by the EA team.
**Fix:**
- BAD: Security addressed only in Phase G (Implementation Governance) as compliance checklist
- GOOD: Security architecture added as explicit layer in Phases B, C, and D; threat model is a Phase C deliverable
**Prevention:** Adopt SABSA (Sherwood Applied Business Security Architecture) as the security-specific companion to TOGAF.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- SAP-037 - Enterprise Architecture - What It Is and Why It Exists
- SAP-038 - Enterprise Architecture Domains - BDAT
- SAP-049 - Business Capability Mapping
- SAP-050 - As-Is / To-Be Architecture

**Builds On This (learn these next):**
- SAP-013 - TOGAF ADM (Architecture Development Method)
- SAP-084 - Enterprise Architecture Maturity Models
- SAP-085 - Enterprise Architecture Programme Design

**Alternatives / Comparisons:**
- SAP-014 - Zachman Framework (classification vs process)
- SAP-015 - ArchiMate (modelling language that pairs with TOGAF)

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════════════╗
║ WHAT IT IS    The world''s most adopted EA        ║
║               framework: process + vocabulary    ║
║ PROBLEM       EA invented independently at every ║
║               org; no shared language or process ║
║ KEY INSIGHT   TOGAF''s value is in the vocab and  ║
║               structure, not in completeness     ║
║ USE WHEN      Building an EA function; large-    ║
║               scale transformation programme     ║
║ AVOID WHEN    Small teams; single-product scope; ║
║               agile without tailoring            ║
║ TRADE-OFF     Standard process and vocab vs      ║
║               heavyweight if not tailored        ║
║ ONE-LINER     "ISO 9001 for enterprise           ║
║                architecture"                     ║
║ NEXT EXPLORE  SAP-013 ADM, SAP-014 Zachman       ║
╚══════════════════════════════════════════════════╝
```

**If you remember only 3 things:**
1. TOGAF provides process (ADM), vocabulary (BDAT), and governance model - adapt all three to your context.
2. TOGAF is a framework, not a method; tailoring is not optional, it is expected.
3. TOGAF and Zachman complement each other: TOGAF = how to do EA; Zachman = what to describe.

**Interview one-liner:** "TOGAF is the world''s most widely adopted EA framework, providing a structured iterative process (ADM), a common vocabulary across the four BDAT domains, an artefact taxonomy, and a governance model - designed to be tailored to organisational context rather than implemented completely."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** A shared framework''s primary value is the common vocabulary it creates - not the specific process steps. Teams that share vocabulary can collaborate without translation overhead, regardless of whether they follow the same process exactly.

**Where else this pattern appears:**
- **Scrum / Agile frameworks** - Scrum''s value is partly in its shared vocabulary (Sprint, Backlog, Retrospective) that allows any Scrum practitioner to understand any Scrum team''s process.
- **ITIL (IT Service Management)** - Same pattern: a standard vocabulary and process framework for IT service delivery that enables practitioners to move between organisations.
- **HL7 FHIR (Healthcare)** - A standard framework for healthcare data interoperability that gives healthcare IT practitioners a shared vocabulary and data model.

---

### 💡 The Surprising Truth

TOGAF is free but the certification is not. The Open Group makes TOGAF documentation publicly available at no cost, yet the TOGAF certification programme generates significant revenue and has certified over 100,000 practitioners globally - making it one of the most economically successful IT standards in history. More surprisingly, independent studies (including a Capgemini survey, 2019) found that TOGAF-certified architects rated their own framework knowledge highly but rated their ability to demonstrate business outcomes from EA significantly lower. The framework is well-understood; its translation into business value remains the hard problem - and it is one that no certification addresses.

---

### 🧠 Think About This Before We Continue

**Question 1 (System Interaction):** An organisation uses TOGAF''s ADM to plan a microservices migration. The ADM Phase E (Opportunities and Solutions) identifies 47 individual migration projects. How should Phase F (Migration Planning) sequence these 47 projects, and what information from Phases B, C, and D is required to produce a valid dependency-ordered roadmap?

*Hint:* Investigate how TOGAF''s "Architecture Roadmap" artefact uses the capability-to-application mapping (from Phase B/C) to identify which migrations are prerequisites for others, and how the Technology Architecture (Phase D) constrains what can be migrated in parallel.

**Question 2 (Scale):** TOGAF''s Architecture Governance framework includes an Architecture Review Board (ARB). At what organisational scale does a centralised ARB become a bottleneck, and how should the ARB''s role evolve as the organisation scales from 10 to 100 to 1,000 delivery teams?

*Hint:* Compare how Spotify''s architecture guild model and Amazon''s "two-pizza team" architecture principle each represent alternatives to centralised ARB governance, and what TOGAF Version 10 says about federated architecture governance.

**Question 3 (Design Trade-off):** TOGAF Version 10 introduced a modular structure, allowing organisations to adopt only the modules relevant to their context. If you were establishing an EA function in a 500-person fintech company, which TOGAF modules would you adopt in the first year, and what criteria would you use to decide what to defer?

*Hint:* Evaluate each TOGAF component (ADM, Content Framework, Enterprise Continuum, Capability Framework) against the specific pain points of a growth-stage fintech: rapid product iteration, regulatory compliance requirements, cloud-native architecture, and a predominantly agile engineering culture.