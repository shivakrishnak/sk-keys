---
id: SAP-065
title: Business Capability Mapping
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★☆
depends_on: SAP-037, SAP-038
used_by: SAP-050, SAP-051
related: SAP-065, SAP-060, SAP-027
tags:
  - architecture
  - intermediate
  - bestpractice
  - mental-model
status: complete
version: 3
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 23
permalink: /software-architecture/business-capability-mapping/
---

# SAP-049 - Business Capability Mapping

⚡ TL;DR - A business capability map is a taxonomy of WHAT an organisation must be able to do, independent of HOW or by which system, making redundancy visible and strategic investment decisions rational.

| SAP-049 | Category: Software Architecture Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | SAP-037, SAP-038 | |
| **Used by:** | SAP-050, SAP-051 | |
| **Related:** | SAP-065, SAP-060, SAP-027 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A 3,000-person retail company has 47 applications managing various aspects of "customer management." No one knows what each system actually does vs what another system duplicates. A new "customer 360" initiative is proposed. Six teams immediately claim the project belongs to them, citing overlapping responsibilities. No one can map which of the 47 systems would need to change. The project takes 18 months just to define its scope.

**THE BREAKING POINT:**
The organisation spends $4M on a CRM upgrade. Six months later, it discovers that 3 other systems already implement the core capabilities the new CRM was purchased for - capabilities that were simply unknown because no taxonomy of capabilities existed.

**THE INVENTION MOMENT:**
Business Process Reengineering (1990s) gave organisations process maps, but processes change with org structure. The insight that transformed EA was: capabilities are more stable than processes or org structures. A capability ("Manage Customer") exists regardless of whether it is owned by Marketing or Sales, regardless of which system implements it, and regardless of how the process works this quarter. Capability maps became the stable backbone of enterprise architecture.

**EVOLUTION:**
Early capability maps were static PowerPoint slides used for strategy planning. Modern capability maps are dynamic, linked to application portfolio data, cost allocation, and investment decisions. Tools like LeanIX, Ardoq, and Alfabet maintain live capability maps that automatically show which applications implement each capability, their lifecycle status, and the cost associated with each.

---

### 📘 Textbook Definition

A **business capability map** is a hierarchical taxonomy that describes what an enterprise must be able to do in order to operate and compete, expressed in business terms independent of organisational structure, processes, or technology implementation. Each capability represents a distinct business ability that can be assessed for investment, gap, and redundancy.

---

### ⏱️ Understand It in 30 Seconds

**One line:** A capability map answers "what must we be able to do?" - the stable backbone that business strategy and IT investment both reference.

> Think of a capability map as a skills matrix for an organisation. Just as a skills matrix lists what competencies a team needs (without specifying who holds them or how they are exercised), a capability map lists what the business must be able to do (without specifying which team owns it or which system implements it).

**One insight:** Capabilities are stable; processes and systems are not. A retail company''s "Process Returns" capability existed before e-commerce and will exist after the next platform migration. Anchoring architecture to capabilities rather than systems or processes makes the map durable.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A capability is defined by WHAT it produces, not HOW or by whom.
2. Capabilities are hierarchical: L1 (e.g., "Customer Management") decomposes to L2 (e.g., "Customer Onboarding," "Customer Communication"), which decomposes to L3 operational capabilities.
3. One capability may be implemented by multiple systems (redundancy). One system may implement multiple capabilities.
4. Capabilities are assessed, not implemented. The map describes needs; the application portfolio describes fulfilment.

**DERIVED DESIGN:**
A three-level hierarchy is standard:
- **L1:** 8-15 strategic domains (e.g., Customer Management, Product Management, Finance)
- **L2:** 3-8 capabilities per L1 domain (e.g., Customer Onboarding, Customer Service, Customer Analytics)
- **L3:** 3-5 operational capabilities per L2 (e.g., KYC Verification, Account Creation, Welcome Communication)

**THE TRADE-OFFS:**
**Gain:** Redundancy visibility. Investment prioritisation. Technology-independent language for business-IT dialogue. Stable anchor for architecture roadmapping.
**Cost:** Significant initial effort to build (typically 3-6 months for a large enterprise). Requires ongoing maintenance as the business evolves. Requires business engagement - not purely an IT exercise.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** An organisation with 50+ systems genuinely cannot answer "what are we able to do and where are we doing it twice?" without a capability model.
**Accidental:** Capability maps that go to L4 or L5 granularity become process models, which are owned by operations, not EA. Three levels is almost always sufficient.

---

### 🧪 Thought Experiment

**SETUP:** Two companies of identical size plan to acquire a competitor. Company A has no capability map. Company B has a three-level capability map linked to its application portfolio.

**WHAT HAPPENS WITHOUT CAPABILITY MAP (Company A):** The integration team identifies 340 applications across the two companies. Assessing overlap takes 14 months because each application must be individually evaluated. 3 years post-acquisition, 60 systems have been retired; 80 redundant capabilities are still implemented twice.

**WHAT HAPPENS WITH CAPABILITY MAP (Company B):** The integration team maps the acquired company''s applications to Company B''s capability map. In 3 months, they have identified: 23 capabilities implemented in both companies, 12 unique capabilities in the acquisition worth retaining, 8 capabilities the acquisition is stronger in (reverse adoption). Integration plan is data-driven and starts from capability overlap, not system overlap.

**THE INSIGHT:** The capability map shifts the conversation from "which of 340 systems do we keep?" to "which of 35 capabilities do we keep, and which systems best implement each?" That is a tractable question.

---

### 🧠 Mental Model / Analogy

> Think of a capability map as a restaurant''s competency list. A Michelin-starred restaurant must be able to: source premium ingredients (Supply Capability), develop menus (Menu Capability), execute recipes consistently (Preparation Capability), manage reservations (Booking Capability), and deliver exceptional service (Service Capability). These capabilities exist whether the restaurant has 5 staff or 50, whether it uses paper bookings or an app, whether the head chef is French or Japanese. The capabilities are stable; the implementation changes.

- **Restaurant competency list** = Business capability map
- **Individual dishes** = Specific processes (unstable; the menu changes)
- **Kitchen equipment** = Applications (change to serve the capabilities)
- **Head chef''s team** = Organisation structure (changes with staffing)

Where this analogy breaks down: a restaurant''s capabilities are narrow and stable; a large enterprise''s capabilities evolve with market strategy, making the map a living artefact, not a one-time document.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A capability map is a list of everything an organisation must be able to do, organised into a hierarchy. It is a shared vocabulary so business and IT can talk about the same things without confusion.

**Level 2 - How to use it (junior developer):**
When you are assigned to build a feature, check the capability map: which L2 capability does this feature implement? Is there an existing system that already implements this capability? Could you extend it rather than build a new one? Are there multiple systems that already implement fragments of this capability (redundancy risk)? The capability map is your first reference before starting design.

**Level 3 - How it works (mid-level engineer):**
Capability maps are used for three main purposes: (1) redundancy analysis - find capabilities implemented by 2+ systems, plan consolidation; (2) gap analysis - find capabilities required by strategy that no system implements, identify investment needs; (3) investment heat mapping - overlay cost data on capabilities to reveal where the budget is going vs where it should go.

**Level 4 - Why it was designed this way (senior/staff):**
The capability model was designed as a stable anchor because both business strategy and IT systems change faster than capabilities. A "Customer Onboarding" capability existed before digital banking and will exist after the next technology disruption. Anchoring architecture to capabilities creates a durable map that strategy and technology both reference, rather than mapping to either directly (which would require the map to be rebuilt whenever strategy or technology changes).

**Expert Thinking Cues:**
- A "buy vs build" decision is actually a capability decision: should this capability be sourced from a vendor or built internally?
- "Organisational silos" are usually symptom of unmapped capability overlaps: multiple teams own the same capability.
- A capability map without application portfolio linkage is decoration; the value is in the cross-domain mapping.

---

### ⚙️ How It Works (Mechanism)

**Step 1 - Define the L1 domains (1-2 weeks):**
Identify 8-15 top-level capability groups from business strategy documents and operating model. Validate with C-level stakeholders that these represent the complete set of what the business must do.

**Step 2 - Decompose to L2 capabilities (4-8 weeks):**
For each L1 domain, define 3-8 distinct capabilities. Each capability should produce a distinct outcome. Test: "If this capability were absent, what business outcome would be impossible?" If no clear answer, the capability is not distinct.

**Step 3 - Map applications to capabilities (4-8 weeks):**
For each L2 capability, identify which applications implement it. Record the completeness (does the system fully or partially implement the capability?), quality (is the implementation adequate?), and lifecycle status (is the system modern, ageing, or planned for retirement?).

**Step 4 - Apply investment assessment (2-4 weeks):**
For each capability, assess: Gap (is it under-supported?), Redundancy (is it over-implemented?), Priority (is it strategic, differentiating, or commodity?). The result is a heat map that guides IT investment decisions.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Business Strategy
      |
      v
L1 Capability Domains       <- Board / C-Level
  (Customer, Product, Finance...)
      |
      v
L2 Capability Breakdown     <- Business owners
  (Customer Onboarding,
   Customer Service...)
      |
      v
L3 Operational Capabilities <- Process owners  <- YOU ARE HERE
  (KYC, Account Opening...)
      |
      v
Application Portfolio Mapping
  (Which systems implement which L3?)
      |
      v
Investment Heat Map
  (Gap / Redundancy / Priority by capability)
```

**FAILURE PATH:**
Capability map built → not linked to application portfolio → useful as a communication tool but cannot answer "which systems change?" → reverts to being a slide deck that no one references for decisions.

**WHAT CHANGES AT SCALE:**
For a 50-person company: a single L1/L2 capability map on a shared document is sufficient. For a 5,000-person company: the map requires dedicated EA tooling with automated application linkage, version control, and governance workflows. For a 50,000-person company: capability maps are maintained per business unit with cross-BU dependency mapping at the L1 level.

---

### 💻 Code Example

A capability map is a business artefact, but its linkage to the application portfolio can be represented in structured data used by EA tooling:

```yaml
# BAD - application-centric portfolio (no capability link)
applications:
  - name: Salesforce CRM
    owner: Marketing
    tech: SaaS
    # No capability mapping - impossible to
    # answer "what can we do?"

  - name: HubSpot
    owner: Sales
    tech: SaaS
    # Possibly duplicates Salesforce capabilities
    # but no way to know
```

```yaml
# GOOD - capability-linked application portfolio

capabilities:
  - id: CAP-L2-001
    name: Customer Onboarding
    level: L2
    parent: CAP-L1-001  # Customer Management
    implemented_by:
      - app: salesforce-crm
        completeness: partial  # Only new customers
        quality: adequate
        lifecycle: strategic
      - app: legacy-onboarding-portal
        completeness: full
        quality: poor
        lifecycle: retire-2025
    gap_assessment: yes   # Portal retiring; gap incoming
    redundancy: no        # Different scope; not duplicate

  - id: CAP-L2-002
    name: Customer Communication
    level: L2
    parent: CAP-L1-001
    implemented_by:
      - app: salesforce-crm
        completeness: full
      - app: hubspot
        completeness: full  # REDUNDANCY DETECTED
    gap_assessment: no
    redundancy: yes  # Two systems, same capability
```

**How to test / verify correctness:**
A capability map is validated through stakeholder workshops, not code. Validation criteria:
- Each capability has a clear, named business owner
- No two capabilities produce the same outcome
- Every current IT investment maps to at least one capability
- All strategic initiatives map to capability gaps or improvements

---

### ⚖️ Comparison Table

| Approach | Stability | IT Link | Primary Use | Limitation |
|:---------|:----------|:--------|:------------|:-----------|
| **Capability Map** | High (years) | Via portfolio | Investment strategy, redundancy | Abstract; needs portfolio link for IT decisions |
| **Process Map** | Low (months) | Weak | Operations improvement | Changes with org structure; not stable for IT planning |
| **Value Stream Map** | Medium | Indirect | Lean / agile transformation | Flow-focused; misses non-flow capabilities |
| **Org Chart** | Low (months) | None | Reporting structure | Says who does what; not what must be done |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:--------------|:--------|
| "A capability map is a process model" | Process maps describe HOW a capability is executed; capability maps describe WHAT must be achievable |
| "Each capability maps to one system" | One capability typically spans multiple systems; one system typically implements multiple capabilities |
| "Capability maps are IT artefacts" | They are business artefacts maintained by EA; building them without business ownership produces IT-centric models that the business does not recognise |
| "A capability map is done once" | Capabilities evolve with business strategy; the map requires annual review and update |
| "L3 capability = system feature" | L3 capabilities are still business abilities; system features are implementation details below the map''s scope |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Process map masquerading as capability map**
**Symptom:** The capability map is invalidated every time a reorganisation occurs.
**Root Cause:** Capabilities defined around current processes or org units rather than business outcomes.
**Diagnostic:**
```
Ask for each capability: "If the org restructured
tomorrow, would this capability still exist?"
If NO: it is a process or org unit, not a capability.
```
**Fix:**
- BAD: Capability = "Sales Team''s Customer Outreach Process"
- GOOD: Capability = "Customer Acquisition" (exists regardless of org structure)
**Prevention:** Define each capability as a business ABILITY (what the organisation must be able to do), not as a process or team responsibility.

**Failure Mode 2: Map without application linkage**
**Symptom:** The capability map is used in strategy conversations but has no influence on IT investment decisions because no one has linked it to the application portfolio.
**Root Cause:** EA team treats the map as a communication artefact, not a governance tool.
**Diagnostic:**
```
Ask: "Which applications implement
Capability X?"
If no one can answer: the map is not linked
to the application portfolio.
```
**Fix:** Spend 4-8 weeks mapping all L2 capabilities to the application portfolio, including completeness and quality scores.
**Prevention:** Make capability-application linkage a requirement for any entry in the application portfolio.

**Security Failure Mode: Security capabilities not in map**
**Symptom:** Security initiatives are funded ad hoc, with no visibility into whether security capabilities (Identity Management, Threat Detection, Vulnerability Management) are adequately implemented.
**Root Cause:** Security treated as a technology concern rather than a business capability.
**Fix:**
- BAD: Security absent from capability map
- GOOD: Security capabilities (Identity & Access Management, Threat Intelligence, Compliance Monitoring) at L2 in an "Enterprise Risk" L1 domain
**Prevention:** Include security as a named L1 or L2 capability group in the initial map build.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- SAP-037 - Enterprise Architecture - What It Is and Why It Exists
- SAP-038 - Enterprise Architecture Domains - BDAT

**Builds On This (learn these next):**
- SAP-050 - As-Is / To-Be Architecture (Current State vs Target State)
- SAP-051 - TOGAF Framework
- SAP-013 - TOGAF ADM (Architecture Development Method)

**Alternatives / Comparisons:**
- SAP-065 - Domain Model (DDD-level capability modelling)
- SAP-060 - Enterprise Application Architecture

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════════════╗
║ WHAT IT IS    Taxonomy of what the enterprise    ║
║               must be able to do                 ║
║ PROBLEM       Redundant systems, invisible gaps, ║
║               irrational IT investment           ║
║ KEY INSIGHT   Capabilities stable; processes and ║
║               systems change - anchor to capabs  ║
║ USE WHEN      M&A integration, IT strategy,      ║
║               legacy modernisation planning      ║
║ AVOID WHEN    Single-product teams; capability   ║
║               scope is too narrow to justify     ║
║ TRADE-OFF     Stable strategic anchor vs effort  ║
║               to build and maintain              ║
║ ONE-LINER     "Skills matrix for the enterprise" ║
║ NEXT EXPLORE  SAP-050 As-Is/To-Be, SAP-051 TOGAF ║
╚══════════════════════════════════════════════════╝
```

**If you remember only 3 things:**
1. A capability is WHAT the business must be able to do - independent of HOW or by whom.
2. Three levels: strategic domains → capabilities → operational capabilities.
3. The map has no value until it is linked to the application portfolio (which systems implement which capabilities).

**Interview one-liner:** "A business capability map is a stable taxonomy of what the organisation must be able to do, expressed in business terms and independent of systems or processes, used to identify investment gaps, redundancies, and the blast radius of any application change."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Separate stable "what" from volatile "how" and "who." The stable backbone (capabilities) enables governance that survives organisational and technical change. Applied to software: domain model (what) vs implementation (how).

**Where else this pattern appears:**
- **Domain-Driven Design** - a bounded context is a capability boundary; the domain model maps "what the system must know" independently of how it is stored or processed.
- **HR competency frameworks** - define what roles must be able to do, independent of who holds the role or how they acquired the skill.
- **Product strategy** - jobs-to-be-done (JTBD) theory defines customer capabilities (what the customer must be able to accomplish) independent of which product implements them.

---

### 💡 The Surprising Truth

Business capability maps are most valuable when they reveal what an organisation CANNOT do - not what it can. A 2020 McKinsey study of 40 large enterprise digital transformations found that the most common cause of programme failure was "capability gaps discovered mid-programme": capabilities required by the target state that were assumed to exist in the current state but did not. Organisations that built capability maps before starting their transformations discovered these gaps in the planning phase (low cost to fix) rather than the delivery phase (high cost to fix). The maps that looked most complete were the ones that surfaced the most gaps - because completeness forced honest gap assessment.

---

### 🧠 Think About This Before We Continue

**Question 1 (System Interaction):** A retail company''s "Customer Management" L1 capability is implemented by 5 different applications across 4 business units. When a GDPR data subject access request is received, which system is the system of record for customer data? How would a capability map with data ownership annotations change how this question is answered?

*Hint:* Investigate how GDPR''s concept of "data controller" maps to the EA concept of "data ownership" and how capability-to-data mappings make data controller identification tractable at scale.

**Question 2 (Scale):** At what point does a business capability map become more burden than benefit? Consider an organisation with 200 L3 capabilities each linked to an average of 4 applications - that is 800 capability-application links that must be kept current. What governance processes and tooling are required to prevent the map from becoming stale?

*Hint:* Research how EA tooling platforms (LeanIX, Alfabet) use integrations with CMDBs, cloud inventories, and CI/CD pipelines to automate capability-application link maintenance.

**Question 3 (Design Trade-off):** Some architects argue that Domain-Driven Design bounded contexts make business capability maps redundant, because a well-designed bounded context IS a business capability. What are the differences between a DDD bounded context and a business capability, and under what conditions would you use one framework vs the other?

*Hint:* Compare the stakeholder audience of each: a bounded context is designed for software engineers; a business capability map is designed for business stakeholders and C-level executives. Consider how the level of abstraction differs and what decisions each enables.