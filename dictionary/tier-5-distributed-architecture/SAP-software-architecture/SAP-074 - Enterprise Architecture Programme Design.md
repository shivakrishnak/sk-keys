---
id: SAP-074
title: Enterprise Architecture Programme Design
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★★
depends_on: SAP-065, SAP-069, SAP-070, SAP-073
used_by: SAP-075
related: SAP-057, SAP-054, SAP-007
tags:
  - architecture
  - advanced
  - governance
  - bestpractice
status: complete
version: 3
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 74
permalink: /software-architecture/enterprise-architecture-programme-design/
---

# SAP-074 - Enterprise Architecture Programme Design

⚡ TL;DR - EA programme design is the L4.5 discipline of establishing, structuring, and governing an enterprise architecture function from scratch: defining operating model, team structure, governance, tooling, and the maturity roadmap.

| SAP-074 | Category: Software Architecture Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | SAP-065, SAP-069, SAP-070, SAP-073 | |
| **Used by:** | SAP-075 | |
| **Related:** | SAP-057, SAP-054, SAP-007 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A CIO decides the organisation needs enterprise architecture. She hires 3 TOGAF-certified architects and tells them to "establish EA." After 12 months: 3 architects have produced 120 documents, attended 200 meetings, and have influenced exactly zero delivery decisions. The CEO asks for the EA function''s ROI. No one can answer.

**THE BREAKING POINT:**
Without deliberate programme design, EA functions default to one of two failure modes: (1) documentation factories that produce artefacts no one uses, or (2) approval bottlenecks that slow delivery without adding value. Both modes result in EA budget cuts within 3 years.

**THE INVENTION MOMENT:**
The insight that transformed EA programme design is that an EA function is a change management programme, not a technical function. Its primary output is decisions made differently - not artefacts produced. Successful EA programmes are designed as organisational change initiatives with clear value hypotheses, stakeholder engagement plans, and measurable outcomes.

**EVOLUTION:**
Early EA programmes were designed as IT governance functions: centrally controlled, process-heavy, approval-gated. The agile transformation (2010s) challenged this model. Modern EA programme design draws from: platform engineering (make the right thing easy), design thinking (understand stakeholder needs), organisational change management (change behaviour, not just process), and product management (measure outcomes, not outputs).

---

### 📘 Textbook Definition

**EA Programme Design** is the architectural practice of establishing an enterprise architecture function, including: defining the EA operating model (centralized, federated, or hybrid), designing the EA team structure, selecting and adapting an EA framework (TOGAF, Zachman), implementing EA tooling and governance, establishing stakeholder engagement models, defining EA success metrics, and building a maturity roadmap from the organisation''s current state to its target EA capability.

---

### ⏱️ Understand It in 30 Seconds

**One line:** EA programme design is the blueprint for building an EA function - not what EA produces, but how the EA function itself is structured to produce business value.

> Think of EA programme design as the architecture of the architecture team. Just as a system architect designs the structure of a software system to meet its quality attributes, an EA programme designer structures the EA function to meet its quality attributes: speed, relevance, stakeholder trust, and business impact.

**One insight:** The most important design decision in EA programme design is not the framework choice (TOGAF vs Zachman) but the operating model choice (centralised vs federated) - because the operating model determines whether EA can scale with the organisation without becoming a bottleneck.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. An EA function exists to change decisions, not to produce documents. Design for decision impact, not artefact production.
2. EA must be closer to the business than to IT. Functions that report only to the CTO rarely influence business strategy.
3. Governance that slows delivery is governance that will be bypassed. Design for fast, lightweight governance that scales with delivery velocity.
4. EA must demonstrate value within 90 days of establishment or lose organisational credibility.

**DERIVED DESIGN:**
Four operating model choices, from centralized to federated:
- **Centralized EA:** Central team owns all architecture standards and reviews. Scales poorly; becomes bottleneck at scale.
- **Federated EA:** Domain architects own their domain; central EA sets standards. Scales well; coordination overhead.
- **Platform EA:** Central team builds architecture platforms and golden paths; delivery teams self-serve. Most scalable.
- **Hybrid:** Central EA for standards and strategic programmes; federated for domain execution.

**THE TRADE-OFFS:**
**Gain (centralised):** Consistent standards. Single point of governance.
**Cost (centralised):** Review bottleneck. Disconnected from delivery reality.
**Gain (federated):** Delivery-speed compatible. Domain expertise.
**Cost (federated):** Standards drift. Coordination overhead.
**Gain (platform EA):** Scalable. Makes right thing easy.
**Cost (platform EA):** High initial investment in platform. Requires platform engineering capability.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Establishing an EA function requires decisions about team structure, governance, framework, tooling, and stakeholder engagement that cannot be avoided.
**Accidental:** Attempting to implement a full TOGAF framework from day 1 rather than building minimal viable EA practices and growing from there.

---

### 🧪 Thought Experiment

**SETUP:** Two organisations establish EA functions simultaneously. Organisation A implements "Full EA from Day 1" (TOGAF ADM, Architecture Review Board, full ArchiMate tooling). Organisation B implements "Minimal Viable EA" (3 architecture principles, capability map, weekly architecture office hours).

**YEAR 1 OUTCOME:**
- Org A: 200 artefacts produced. 0 delivery decisions changed. EA budget under review.
- Org B: 12 decisions influenced. 3 systems consolidated. Redundancy eliminated saving $2M. EA budget increased.

**YEAR 2:**
- Org A: EA team disbanded. "EA failed."
- Org B: EA team expanded to 6. ArchiMate adopted based on demand. Governance formalised.

**THE INSIGHT:** The minimal viable EA approach succeeds because it prioritises business value over framework compliance. Framework and tooling complexity is added when demand demonstrates it is needed, not because the framework specifies it.

---

### 🧠 Mental Model / Analogy

> Think of EA programme design as designing a hospital. A hospital''s quality is not measured by the number of doctors or the sophistication of equipment - it is measured by patient outcomes. An EA function''s quality is not measured by the number of architects or the sophistication of tooling - it is measured by architecture outcomes (decisions improved, rework avoided, investment aligned). Design the EA function around its patient (the organisation''s decision-making), not around its instruments (frameworks and tools).

- **Hospital mission = patient outcomes** = EA mission = better decisions
- **Hospital organisational design** = EA operating model
- **Clinical protocols** = EA governance and review processes
- **Medical equipment** = EA tooling (ArchiMate, TOGAF tooling)
- **Patient intake and triage** = EA demand management (prioritising which decisions EA supports)

Where this analogy breaks down: a hospital''s patients come to the hospital; an EA function must go to its "patients" (business stakeholders), who will not come to it.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
EA programme design is the plan for how the EA team is set up, what it does, how it works with other teams, and how success is measured. It is the management and organisational design of the architecture function itself.

**Level 2 - How to use it (junior developer):**
Understanding the EA programme design of your organisation tells you: who to go to for architecture decisions, what types of decisions require EA review, how fast you can expect a review response, and what the EA team''s published principles and standards are. A well-designed EA programme has answers to all of these questions. A poorly designed one has none.

**Level 3 - How it works (mid-level engineer):**
EA programme design produces: an EA charter (scope, purpose, authority), an operating model (team structure, governance model), an EA framework selection and tailoring plan, a tooling architecture, a stakeholder engagement model (which business and IT stakeholders are EA''s primary customers), a value measurement framework (what metrics demonstrate EA impact), and a maturity roadmap (from current to target EA capability). These are the "architecture of the architecture function."

**Level 4 - Why it was designed this way (senior/staff):**
The federated EA operating model dominates modern programme design because centralised EA cannot scale with continuous delivery. The shift from centralised to federated mirrors the shift from monolithic to microservices architecture: the same trade-off (consistency vs scalability) applies in both domains. Platform EA - where the EA function''s primary product is a platform (golden paths, standards enforcement, architecture templates) rather than a review service - represents the same insight that platform engineering brought to developer tooling: make the right thing easy rather than policing the wrong thing.

**Expert Thinking Cues:**
- If every significant architecture decision passes through a central review board, the EA function will fail at scale. Design the review board out of the critical path.
- The first 90 days of an EA function determine its organisational reputation for the next 5 years. Choose the first problems to solve for maximum visible impact.
- EA functions that succeed embed EA practitioners in business and delivery teams, not in a separate EA tower.

---

### ⚙️ How It Works (Mechanism)

**EA Programme Design - Seven Components:**

**1. EA Charter:**
Define: EA''s mandate (what decisions it influences), authority (advisory, mandatory review, veto), scope (which systems, which initiatives), and relationship to existing governance bodies (Portfolio Management, Change Advisory Board).

**2. Operating Model Selection:**
Centralised (< 20 teams), Federated (20-100 teams), Platform EA (> 100 teams), or Hybrid. Define: central EA team roles, domain architect roles, governance touchpoints.

**3. Framework and Method Tailoring:**
Select foundation framework (typically TOGAF). Identify which ADM phases to implement in year 1 (typically Phase A, B, G). Define organisation-specific tailoring. Plan which additional phases to add in years 2-3.

**4. Tooling Architecture:**
Start: Archi (free, open source) + SharePoint/Confluence for artefact repository. Scale to: commercial EA platform (LeanIX, BiZZdesign) when Volume and CMDB integration justify cost. Sequence: define processes first, then select tooling.

**5. Stakeholder Engagement Model:**
Identify: C-level sponsor (CIO/CTO), business unit champions, delivery team leads. Define: engagement cadence (Architecture Forum monthly, ad-hoc reviews), communication channels, EA output formats by stakeholder.

**6. Value Measurement Framework:**
Measure: decisions influenced (count and estimated value), rework avoided (estimated cost), redundancy eliminated (actual cost), investment redirected (actual dollars). Avoid measuring: artefact counts, review throughput, compliance percentages.

**7. Maturity Roadmap:**
Baseline current maturity (O-ACMM or Gartner ITScore). Define target for year 1 (typically +1 level overall, +2 in business engagement). Sequence improvement investments by dimension priority.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
CIO/CTO Decision: Establish EA Function
          |
          v
[90-Day Discovery]
  Stakeholder interviews
  Current maturity assessment
  Critical decision pain points
          |
          v
[EA Programme Design]          <- YOU ARE HERE
  Charter, Operating Model,
  Framework, Tooling, Metrics
          |
          v
[Minimal Viable EA Launch]
  3 Architecture Principles
  First capability map
  First architecture office hours
          |
          v
[First 90-Day Value Demo]
  1-3 decisions influenced
  1 redundancy identified
  1 quick win delivered
          |
          v
[EA Maturity Level 2 → 3]
  Process formalisation
  Governance board established
  EA tooling adopted
          |
          v
[Sustained Level 3+ Practice]
  Quarterly maturity reviews
  Tooling expanded as needed
  EA embedded in delivery
```

**FAILURE PATH:**
EA programme established → full TOGAF ADM from Day 1 → 6 months of process design before any delivery engagement → delivery teams build without EA input → EA review board rejects work already done → conflict → EA bypassed → programme fails.

**WHAT CHANGES AT SCALE:**
At small scale: 1 EA practitioner, informal process, 3 principles, shared document. At medium scale: 3-5 EA practitioners, defined process, ARB, EA tooling. At large scale: 10-50 EA practitioners, federated model, automated enforcement, platform engineering aligned.

---

### ⚖️ Comparison Table

| Operating Model | Governance | Scalability | Consistency | Best For |
|:----------------|:-----------|:------------|:------------|:---------|
| **Centralised** | Central ARB | Low | High | < 20 delivery teams |
| **Federated** | Domain ARBs + Central | Medium | Medium | 20-100 teams |
| **Platform EA** | Automated + Lightweight review | High | Medium-High | > 100 teams |
| **Hybrid** | Central standards + Domain execution | Medium-High | Medium | Most large enterprises |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:--------------|:--------|
| "EA programme success = framework implementation" | Success = decisions made better; framework is a means, not an end |
| "Start with the full TOGAF ADM" | Start with the minimum needed to influence the next 3 decisions; grow from demonstrated value |
| "EA reports to the CTO" | EA reporting structure determines its stakeholder access; reporting only to CTO limits business engagement |
| "EA programme design is a one-time activity" | EA programme design evolves with the organisation; the operating model that works at 50 teams fails at 500 |
| "More architects = better EA" | EA impact scales with stakeholder trust and business integration, not headcount |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: No quick wins in first 90 days**
**Symptom:** EA function has been running for 6 months with no visible business impact. Leadership confidence is declining.
**Root Cause:** EA team focused on building comprehensive artefacts (capability map, full portfolio) before engaging with business decisions.
**Diagnostic:**
```
Ask: "What specific business decision
was changed because of EA input
in the last 90 days?"
No clear answer: quick win failure.
```
**Fix:** Immediately pivot to identifying 2-3 high-visibility problems EA can contribute to in the next 30 days.
**Prevention:** Design the first 90-day plan around demonstrable impact, not artefact production. Pick 3 specific problems to solve visibly.

**Failure Mode 2: Wrong reporting structure**
**Symptom:** EA function produces excellent technology architecture but has no access to business strategy discussions. Technology strategy diverges from business strategy.
**Root Cause:** EA function reports to CTO or VP Engineering only; no visibility into or relationship with business strategy.
**Diagnostic:**
```
Ask: "Does the EA lead attend business
strategy reviews or planning sessions?"
Never: reporting structure failure.
Ask: "Which business stakeholders does
EA have a regular engagement with?"
< 3: business engagement failure.
```
**Fix:** Establish EA reporting to CIO (not CTO) and create a direct relationship with CFO and COO for investment decisions.
**Prevention:** Define EA''s stakeholder map at programme design stage with explicit business stakeholder relationships.

**Security Failure Mode: Security not designed into EA programme**
**Symptom:** The EA programme is established but has no relationship with the CISO function. Security architecture is practiced separately from EA, creating blind spots in both functions.
**Root Cause:** EA programme designed without security as an explicit dimension of the operating model.
**Fix:**
- BAD: EA and security architecture are separate functions with no shared governance
- GOOD: EA programme includes CISO as a mandatory stakeholder; security architecture reviews are a component of EA Architecture Review Board agenda; security principles are included in the EA principles catalogue
**Prevention:** Include CISO in the EA programme''s stakeholder map from day 1. Define security architecture as a cross-cutting concern in the EA operating model.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- SAP-065 - Enterprise Architecture - What It Is and Why It Exists
- SAP-069 - TOGAF Framework
- SAP-073 - Enterprise Architecture Maturity Models

**Builds On This (learn these next):**
- SAP-075 - EA Tool Selection and Vendor Landscape
- SAP-057 - Architecture Governance at Scale

**Alternatives / Comparisons:**
- SAP-054 - Architecture Review Process Design (governance component of EA programme)
- SAP-055 - Legacy Modernization Strategy (common EA programme use case)

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════════════╗
║ WHAT IT IS    Blueprint for building the EA      ║
║               function: model, team, governance  ║
║ PROBLEM       EA functions fail without design;  ║
║               default to doc factory or blocker  ║
║ KEY INSIGHT   EA programme = change management   ║
║               programme, not a tech function     ║
║ USE WHEN      Establishing EA from scratch;      ║
║               redesigning failing EA function    ║
║ AVOID WHEN    Single-project context; EA already ║
║               well-established and performing    ║
║ TRADE-OFF     Centralised (consistent/bottleneck)║
║               vs Federated (scalable/complex)    ║
║ ONE-LINER     "Architecture of the architecture  ║
║                team"                             ║
║ NEXT EXPLORE  SAP-075 EA Tool Selection          ║
╚══════════════════════════════════════════════════╝
```

**If you remember only 3 things:**
1. Operating model choice (centralised vs federated vs platform) is the most consequential EA programme design decision.
2. Demonstrate value within 90 days or lose organisational credibility - start with visible problems, not comprehensive artefacts.
3. EA is a change management programme; measure it by decisions changed, not by documents produced.

**Interview one-liner:** "EA programme design is the practice of establishing an EA function with a deliberate operating model, governance structure, framework tailoring, tooling architecture, stakeholder engagement plan, and value measurement framework - focused on changing decisions, not producing artefacts."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Any enabling function (EA, platform engineering, DevOps, data engineering) succeeds by making the right thing easy for its customers, not by governing the wrong thing. Design for customer adoption, not for compliance.

**Where else this pattern appears:**
- **Platform Engineering** - the shift from central release engineering to internal developer platform uses the same design principles: make the right path the easy path; automate standards enforcement; measure adoption, not compliance.
- **Data mesh** - the distributed data ownership model applies the same federated EA operating model to data: domain teams own their data products; central governance sets standards.
- **FinOps function design** - establishing a FinOps function uses the same programme design pattern: operating model, stakeholder engagement, quick wins, maturity roadmap.

---

### 💡 The Surprising Truth

The single strongest predictor of EA programme success is not the framework chosen, the team size, or the tooling budget - it is the EA lead''s seniority and relationship with business leadership. Gartner research (2020) across 300 EA programmes found that EA functions where the chief architect reported directly to the CIO or had direct access to the CEO had a 3.8x higher rate of measured business value delivery than EA functions reporting below the CIO. The mechanism is not organisational hierarchy for its own sake - it is stakeholder access. An EA lead with business leadership access can attend strategy discussions where technology decisions originate; an EA lead reporting to a VP Engineering encounters those decisions only after they are made.

---

### 🧠 Think About This Before We Continue

**Question 1 (System Interaction):** A financial services firm establishes an EA function. After 6 months, the EA team has produced a comprehensive capability map and application portfolio, but the portfolio management office (PMO) continues to approve projects without consulting EA. What operating model change and governance integration is required to ensure EA input into portfolio investment decisions, and what TOGAF ADM phase does portfolio alignment map to?

*Hint:* Investigate how TOGAF ADM Phase E (Opportunities and Solutions) and Phase F (Migration Planning) are designed to integrate with portfolio management processes, and what governance changes are required to ensure EA artefacts from Phase E/F feed into the PMO''s investment decision gates.

**Question 2 (Scale):** An EA programme designed for a 1,000-person organisation is now operating in a 10,000-person organisation after rapid growth and acquisitions. The centralised ARB now processes 200 review requests per quarter and has an average 6-week review time. What operating model redesign is required, and how do you migrate from a centralised model to a federated model without losing architectural consistency during the transition?

*Hint:* Research how large technology companies (Zalando, Spotify, Netflix) describe their transition from centralised to federated architecture governance, specifically what standards they made non-negotiable at the centre and what they devolved to domain teams.

**Question 3 (Design Trade-off):** Some organisations argue that formal EA programmes are a legacy construct from the pre-cloud era, and that modern engineering organisations can achieve architectural coherence through: strong platform engineering, comprehensive API contracts, and well-defined domain ownership (Domain-Driven Design). When is a formal EA programme necessary, and when can these engineering practices substitute for it?

*Hint:* Consider the types of governance questions that engineering practices can answer (how does this service integrate?) vs the types that only EA can answer (which of 200 systems implements the regulatory reporting capability we need to change?), and map which organisational contexts generate each type of question at frequency.