---
id: SAP-073
title: Enterprise Architecture Maturity Models
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★★
depends_on: SAP-069, SAP-070, SAP-071, SAP-072
used_by: SAP-074
related: SAP-057, SAP-056, SAP-065
tags:
  - architecture
  - advanced
  - bestpractice
  - governance
status: complete
version: 3
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 73
permalink: /software-architecture/enterprise-architecture-maturity-models/
---

# SAP-073 - Enterprise Architecture Maturity Models

⚡ TL;DR - EA maturity models (Gartner ITScore, TOGAF Maturity, O-ACMM) measure how effectively an organisation practises EA, from ad-hoc architecture (Level 1) to enterprise-optimising architecture (Level 5), guiding investment and improvement priorities.

| SAP-073 | Category: Software Architecture Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | SAP-069, SAP-070, SAP-071, SAP-072 | |
| **Used by:** | SAP-074 | |
| **Related:** | SAP-057, SAP-056, SAP-065 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A CIO asks: "How mature is our EA practice?" The EA team says "very mature - we have 3 certified architects and produce 40 artefacts per year." The CIO asks: "Then why can''t we answer basic questions about our technology estate in less than 3 months?" Without a maturity model, there is no shared language for evaluating EA capability. "Mature" means different things to different stakeholders. The EA function cannot demonstrate progress or prioritise improvements because there is no agreed baseline measurement.

**THE BREAKING POINT:**
A competitor with a similar-sized EA team can answer cross-domain impact questions in hours, maintains a live application portfolio, and has EA input into every major technology decision. The difference is not the number of architects or artefacts - it is the maturity of the EA practice: the processes, tooling, governance, and organisational integration that make EA outputs actionable.

**THE INVENTION MOMENT:**
Gartner developed the first EA Maturity Model in the early 2000s, drawing on the Software Engineering Institute''s Capability Maturity Model (CMM). The Open Group Architecture Forum produced the Architecture Capability Maturity Model (ACMM) in 2004. The insight was the same as CMM: EA capability is not binary (have it / don''t have it) but progressive, with identifiable stages from reactive (fire-fighting) to proactive (strategic enablement).

**EVOLUTION:**
Gartner''s EA Maturity Model evolved into the "ITScore for Enterprise Architecture" product. The Open Group produced multiple EA maturity models, converging on the O-ACMM. The US Federal Government''s Office of Management and Budget developed the EA Assessment Framework (EAAF) for federal agencies. Modern maturity models have expanded beyond process maturity to include business value delivery, stakeholder engagement, and technology automation.

---

### 📘 Textbook Definition

An **EA Maturity Model** is a framework for assessing and improving an organisation''s enterprise architecture capability across multiple dimensions (governance, artefacts, processes, tooling, business engagement). Maturity levels typically range from 1 (ad-hoc, no formal EA) to 5 (optimising, EA continuously improves business outcomes). Different models (Gartner ITScore, O-ACMM, TOGAF Maturity) use different dimensions and level definitions, but share the same progression: reactive → defined → managed → optimising.

---

### ⏱️ Understand It in 30 Seconds

**One line:** EA maturity models answer "how good are we at EA?" with a structured five-level scale that maps current capability, identifies gaps, and prioritises improvements.

> Think of an EA maturity model as a driving test with five proficiency levels. Level 1 is knowing what a car is. Level 2 is being able to drive in a car park. Level 3 is being able to drive on public roads. Level 4 is being able to drive in complex traffic conditions. Level 5 is being able to teach others and adapt to any road condition. Most organisations assess themselves at Level 3 and discover they are actually Level 2 when assessed objectively.

**One insight:** Most organisations overestimate their EA maturity. The most common self-assessment error is rating process maturity (we have a process for X) without measuring outcome maturity (the process produces the business outcomes it was designed for).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. EA maturity is multidimensional: governance, artefacts, processes, tooling, and business engagement must ALL be measured; high maturity in one dimension cannot compensate for low maturity in another.
2. Maturity levels are cumulative: Level 4 requires all Level 3 capabilities to be in place. Attempting Level 4 practices without Level 3 foundations produces fragile, inconsistent results.
3. Maturity is measured by outcomes, not activities: producing architecture documents (activity) is not evidence of maturity; influencing architecture decisions (outcome) is.
4. EA maturity must be sustained: organisations that achieve Level 4 and reduce EA investment commonly regress to Level 2-3 within 2-3 years.

**DERIVED DESIGN:**
Standard five-level progression:
- **Level 1 - Initial / Ad-hoc:** Architecture exists but is not formalised. Depends on individual heroics. No consistent process or vocabulary.
- **Level 2 - Under Development:** EA processes are being defined. Some artefacts exist. Limited tooling. Inconsistent governance.
- **Level 3 - Defined:** EA processes are documented and followed. Core artefacts maintained. Governance board exists. EA has regular business engagement.
- **Level 4 - Managed:** EA is quantitatively measured. Automated enforcement of standards. EA drives IT investment decisions. Application portfolio current and accurate.
- **Level 5 - Optimising:** EA continuously improves based on feedback. Business outcomes measured against EA decisions. EA is a strategic function with board-level visibility.

**THE TRADE-OFFS:**
**Gain:** Common language for EA capability discussion. Clear improvement roadmap. Ability to benchmark against peers.
**Cost:** Self-assessment is unreliable; requires external assessment for accuracy. Maturity model can become a compliance target rather than an improvement tool. Different models produce different assessments of the same organisation.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** An organisation that cannot measure its EA capability cannot improve it systematically.
**Accidental:** Pursuing a specific maturity level score as the goal rather than using the model as a diagnostic for prioritising improvements.

---

### 🧪 Thought Experiment

**SETUP:** Two organisations each claim to be at "Level 3 EA Maturity." Organisation A self-assessed. Organisation B used a third-party Gartner ITScore assessment.

**ORGANISATION A SELF-ASSESSMENT:** Claims Level 3 because it has: a TOGAF-based EA process (process dimension), 50 ArchiMate diagrams (artefact dimension), and an Architecture Review Board (governance dimension). Business engagement dimension and tooling dimension were not assessed.

**ORGANISATION B THIRD-PARTY ASSESSMENT:** Scored Level 2 overall because: process dimension = Level 3 (documented), artefact dimension = Level 2 (incomplete, stale), governance dimension = Level 3, business engagement dimension = Level 1 (EA reports to CTO, never to business), tooling dimension = Level 2 (no integrated EA tooling). The lowest dimension limits overall maturity.

**THE INSIGHT:** Self-assessment systematically overestimates maturity. Business engagement is the most commonly underestimated dimension: organisations focus on process and artefact maturity while their EA function has no direct relationship with business decision-making.

---

### 🧠 Mental Model / Analogy

> Think of EA maturity levels as the stages of a medical practice. Level 1: a practitioner with no formal training treats patients based on intuition. Level 2: formal medical training is being acquired; some diagnoses are correct. Level 3: licensed physician with consistent diagnostic process and evidence-based treatments. Level 4: specialist physician using quantitative outcomes data to optimise treatment protocols. Level 5: researcher-physician designing new treatment methodologies based on population-level outcomes. An organisation at Level 2 EA maturity that attempts Level 4 practices (quantitative measurement without defined processes) produces noise, not insight.

- **Medical training** = EA process definition (Level 2-3)
- **Diagnostic protocol** = EA methodology (Level 3)
- **Evidence-based treatment** = EA decision-making with data (Level 4)
- **Outcomes research** = EA continuous improvement cycle (Level 5)

Where this analogy breaks down: medical maturity is individual; EA maturity is organisational. An organisation can have a Level 5 EA practitioner in a Level 2 EA organisation, producing Level 2 outcomes.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
An EA maturity model is a scale from 1 to 5 that measures how well an organisation does enterprise architecture. Level 1 means no formal EA. Level 5 means EA is central to strategic business decisions. Most organisations are at Level 2-3.

**Level 2 - How to use it (junior developer):**
When joining an organisation, you can infer its EA maturity from observable signals: Are architecture standards documented and enforced? Does EA have input into your team''s design decisions? Is there a maintained application portfolio? Are architecture decisions made ad-hoc or through a defined process? These signals indicate Level 2-3 vs Level 4+ maturity.

**Level 3 - How it works (mid-level engineer):**
EA maturity assessments evaluate multiple dimensions: Process (is the EA process defined and followed?), Artefacts (are architecture artefacts current and complete?), Governance (does the ARB function effectively?), Tooling (is there an EA repository with live data?), Business Engagement (does EA influence business strategy?). Each dimension is scored independently; overall maturity is typically the median or minimum dimension score. The assessment produces a gap analysis and improvement roadmap for each dimension.

**Level 4 - Why it was designed this way (senior/staff):**
EA maturity models were designed on the CMM/CMMI principle that capability improvement is predictable and progressive - that organisations do not jump from Level 2 to Level 5 without developing Level 3 and 4 capabilities first. This implies that improvement investment should target the next level''s requirements rather than attempting to leapfrog. In practice, organisations often try to implement Level 4 tooling (automated EA repositories) without Level 3 processes (defined EA processes for maintaining them), producing expensive tooling that is immediately abandoned.

**Expert Thinking Cues:**
- Business engagement maturity is almost always the hardest to improve: it requires organisational change, not technical investment.
- EA tooling maturity lags process maturity in high-performing EA functions: tooling should follow process definition, not precede it.
- A sudden increase in self-assessed maturity (without external assessment) is usually a sign that the maturity model has been adopted as a compliance target rather than an improvement tool.

---

### ⚙️ How It Works (Mechanism)

**Key EA Maturity Models:**

**Gartner ITScore for EA:**
Five levels across six dimensions: Scope, Business Alignment, Governance, Methods, Information, Organisation. Known for: business alignment emphasis. Limitation: requires Gartner engagement for formal assessment.

**O-ACMM (Open Group Architecture Capability Maturity Model):**
Nine dimensions: Architecture Process, Architecture Development, Business Linkage, Senior Management Involvement, Operating Unit Participation, Architecture Communication, IT Security, Architecture Governance, IT Investment and Acquisition Strategy. Five levels (0-4).

**TOGAF Architecture Capability Maturity Model:**
Six dimensions aligned to TOGAF ADM: Architecture Governance, Architecture Skills, Architecture Process, Architecture Information, Architecture Business Value, IT Investment. Five levels.

**Assessment process:**
```
Step 1: Select model (Gartner / O-ACMM / TOGAF)
Step 2: Define assessment scope
  (full EA function or specific dimensions)
Step 3: Gather evidence per dimension
  (process documentation, artefacts, governance logs)
Step 4: Interview stakeholders
  (EA team, business stakeholders, delivery leads)
Step 5: Score each dimension
Step 6: Calculate overall maturity level
Step 7: Identify dimension gaps and improvement priorities
Step 8: Produce maturity roadmap (current to target level)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
EA Function Established (or Existing)
          |
          v
[Baseline Assessment]
  Select model, assess all dimensions
  Produce current maturity score
          |
          v
[Target Maturity Definition]           <- YOU ARE HERE
  Define target level (typically +1 level
  over 12-18 months)
  Identify dimension gaps
          |
          v
[Improvement Roadmap]
  Sequence dimension improvements
  Prioritise business engagement first
          |
          v
[Execution: Process before Tooling]
  Define processes → Implement tooling
  that supports defined processes
          |
          v
[Progress Review (quarterly)]
  Re-assess dimensions
  Adjust roadmap
          |
          v
[Target Level Achieved]
  Validate with external assessment
  Set next target level
```

**FAILURE PATH:**
Maturity model adopted → organisation sets Level 4 target → implements Level 4 tooling without Level 3 processes → tooling unused → EA budget cut → regression to Level 1.

**WHAT CHANGES AT SCALE:**
At small scale (< 200 employees): Level 3 is the practical maximum; full Level 4/5 requires more EA investment than the business value justifies. At medium scale: Level 3-4 is appropriate; tooling investment becomes cost-effective. At large scale (5,000+ employees): Level 4-5 is required; un-managed complexity at this scale creates costs that exceed EA investment.

---

### ⚖️ Comparison Table

| Model | Dimensions | Levels | Best For | Limitation |
|:------|:-----------|:-------|:---------|:-----------|
| **Gartner ITScore** | 6 (business-focused) | 5 | Business-outcome focus | Requires Gartner engagement |
| **O-ACMM** | 9 (comprehensive) | 5 (0-4) | Comprehensive assessment | Complex; 9 dimensions to assess |
| **TOGAF Maturity** | 6 (TOGAF-aligned) | 5 | TOGAF-adopting organisations | Biased toward TOGAF practices |
| **CMMI-like EA** | Variable | 5 | Organisations using CMMI for software | Not standard; varies by consultant |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:--------------|:--------|
| "Higher maturity level is always better" | Level 3 may be optimal for a 200-person company; Level 5 requires investment that only ROIs at scale |
| "Maturity is measured by artefact count" | Artefact count is a process input metric; outcomes (decisions influenced, rework avoided) are the maturity indicators |
| "Self-assessment is sufficient" | Self-assessment systematically overestimates by 0.5-1.0 levels; third-party assessment is required for investment decisions |
| "Maturity model compliance = effective EA" | Compliance with a maturity model is not evidence of business value; some Level 4 EA functions have zero business impact |
| "Tool sophistication = maturity" | Advanced EA tooling at Level 4/5 requires Level 3 processes to be effective; tooling before process is a common investment failure |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Maturity level as compliance target**
**Symptom:** The EA team reports achieving Level 3 maturity; business stakeholders report no improvement in EA value. The maturity score is accurate; the business impact is absent.
**Root Cause:** Maturity model used to report progress to management rather than to drive EA improvement. Activities are optimised for scoring, not outcomes.
**Diagnostic:**
```
Ask business stakeholders:
"Has the EA team''s input changed any
significant technology decision in the
last 12 months?"
Low positive response rate: maturity
label without business impact.
```
**Fix:** Redefine maturity success criteria as business outcomes (decisions influenced, rework avoided, investment redirected) rather than process compliance metrics.

**Failure Mode 2: Tooling before process**
**Symptom:** Organisation buys a premium EA tool (LeanIX, BiZZdesign) at Level 4 maturity expectation. Tool is sparsely populated and rarely used. EA team reverts to PowerPoint.
**Root Cause:** Level 4 tooling acquired before Level 3 processes are defined. The tool has no defined use cases because the processes that would use it do not exist.
**Diagnostic:**
```
Assess: Are there documented EA processes
that specify: who updates the EA tool,
when, triggered by what events,
and reviewed by whom?
No documented processes: tooling-before-process failure.
```
**Fix:** Define EA processes first. Only acquire tooling that explicitly supports those defined processes. Start with a free tool (Archi) until Level 3 processes are established.

**Security Failure Mode: Security maturity not assessed**
**Symptom:** EA maturity assessment scores high on Business, Application, and Technology dimensions but the organisation suffers a data breach that was architecturally preventable.
**Root Cause:** EA maturity assessment did not include security architecture as a dimension. Security capability exists but is not governed through EA.
**Diagnostic:**
```bash
# Check: Is security architecture
# represented in EA governance?
# Ask: When was the last architecture
# review that included a security
# architecture assessment?
# > 6 months: security dimension absent.
```
**Fix:** Add "Security Architecture Maturity" as an explicit dimension in the EA maturity assessment, with specific indicators at each level.
**Prevention:** Align EA maturity assessment with SABSA maturity model (security architecture); require security maturity to be at most one level below the overall EA maturity target.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- SAP-069 - TOGAF Framework
- SAP-070 - TOGAF ADM (Architecture Development Method)
- SAP-065 - Enterprise Architecture - What It Is and Why It Exists

**Builds On This (learn these next):**
- SAP-074 - Enterprise Architecture Programme Design
- SAP-057 - Architecture Governance at Scale

**Alternatives / Comparisons:**
- SAP-056 - Architecture Fitness Functions (automated maturity measurement)
- SAP-054 - Architecture Review Process Design

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════════════╗
║ WHAT IT IS    Five-level scale measuring how     ║
║               effectively an org practises EA    ║
║ PROBLEM       No shared language for EA quality; ║
║               "mature" means different things    ║
║ KEY INSIGHT   Business engagement maturity is    ║
║               the hardest to improve and the     ║
║               most impactful                     ║
║ USE WHEN      Establishing EA function; making   ║
║               EA investment case; benchmarking   ║
║ AVOID WHEN    As compliance target divorced from ║
║               actual business outcome improvement║
║ TRADE-OFF     Measurement rigour vs risk of      ║
║               optimising for score not outcome   ║
║ ONE-LINER     "Driving test for enterprise       ║
║                architecture capability"          ║
║ NEXT EXPLORE  SAP-074 EA Programme Design        ║
╚══════════════════════════════════════════════════╝
```

**If you remember only 3 things:**
1. Five levels: Initial → Under Development → Defined → Managed → Optimising.
2. Business engagement is the hardest dimension to improve and the most commonly underrated.
3. Self-assessment overestimates by 0.5-1.0 levels; external assessment is required for investment decisions.

**Interview one-liner:** "EA maturity models provide a structured five-level assessment of an organisation''s EA capability across dimensions including process maturity, artefact quality, governance effectiveness, tooling, and business engagement - used to diagnose capability gaps and prioritise EA investment."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Capability improvement is progressive and cumulative - you cannot reliably skip levels. This applies to engineering team maturity (DevOps maturity models, agile maturity), product maturity (feature completeness models), and organisational maturity (CMM, CMMI). Invest in the next level''s requirements, not in leapfrogging to a distant target.

**Where else this pattern appears:**
- **DevOps Research and Assessment (DORA) metrics** - a capability maturity model for software delivery, measuring deployment frequency, lead time, change failure rate, and MTTR from low to elite performance bands.
- **Site Reliability Engineering maturity** - Google''s SRE maturity model progresses from reactive incident response to proactive reliability engineering through defined capability stages.
- **Data governance maturity (DCAM)** - the Data Management Association''s capability maturity model applies the same five-level progression to data governance capability.

---

### 💡 The Surprising Truth

The most consistent finding across EA maturity research is that the technology dimension (tooling, repository, automation) has the weakest correlation with business outcomes, while the business engagement dimension has the strongest. Organisations at Level 4 technology maturity with Level 2 business engagement produce less measurable business value than organisations at Level 3 technology maturity with Level 4 business engagement. This is counterintuitive because technology investment is visible and measurable, while business engagement investment is largely relationship-building and organisational change work. CIOs consistently over-invest in EA tooling and under-invest in embedding EA practitioners in business decision-making processes.

---

### 🧠 Think About This Before We Continue

**Question 1 (System Interaction):** An organisation at Level 2 EA maturity is planning a cloud migration that would typically require Level 4 EA capability to govern effectively. What specific EA capabilities must be established before the migration begins, and how long realistically does it take to move from Level 2 to Level 3 in the dimensions required for cloud migration governance?

*Hint:* Research how hyperscaler cloud providers (AWS, Azure) define the EA capabilities required for enterprise cloud adoption (e.g., AWS Cloud Adoption Framework, Azure Landing Zone model) and map those requirements to specific EA maturity dimensions.

**Question 2 (Scale):** A global financial services firm with 50 country operations wants to achieve consistent Level 3 EA maturity across all operations. Given that each country has its own technology stack, regulatory environment, and EA team, what governance model is required to measure and improve EA maturity consistently at a global level while respecting local variation?

*Hint:* Research how global enterprises implement "federated EA" governance - where group-level EA sets minimum maturity standards and dimensions, while local EA teams implement practices appropriate to their context - and what artefacts and governance processes the group level must maintain.

**Question 3 (Design Trade-off):** Some researchers argue that EA maturity models are inherently flawed because they assume a universal progression that does not account for different organisational strategies. A startup that ships daily may have a Level 1 EA maturity but be more strategically aligned than a Level 4 EA function at a slow-moving enterprise. Is EA maturity an absolute scale or a relative one, and how should the target maturity level vary by organisation type?

*Hint:* Compare how Gartner''s "pace-layered application strategy" implies different optimal EA maturity targets for systems of record (Level 4+), systems of differentiation (Level 3), and systems of innovation (Level 2) - suggesting that EA maturity optimisation should be layer-specific rather than organisation-wide.