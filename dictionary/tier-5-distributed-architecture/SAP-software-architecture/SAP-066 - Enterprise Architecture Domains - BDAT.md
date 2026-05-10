---
id: SAP-066
title: Enterprise Architecture Domains - BDAT
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★☆☆
depends_on: SAP-065
used_by: SAP-067, SAP-069, SAP-070
related: SAP-010, SAP-058, SAP-071
tags:
  - architecture
  - foundational
  - mental-model
  - bestpractice
status: complete
version: 3
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 66
permalink: /software-architecture/enterprise-architecture-domains-bdat/
---

# SAP-066 - Enterprise Architecture Domains - BDAT

⚡ TL;DR - BDAT (Business, Data, Application, Technology) is the universal four-domain model used by all major EA frameworks to decompose an enterprise into four coherent layers, each owned by different stakeholders.

| SAP-066 | Category: Software Architecture Patterns | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | SAP-065 | |
| **Used by:** | SAP-067, SAP-069, SAP-070 | |
| **Related:** | SAP-010, SAP-058, SAP-071 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An enterprise tries to plan a digital transformation. The business strategy team talks about "customer experience." The IT team talks about "microservices migration." The data team talks about "data lake." The infrastructure team talks about "cloud-first." No one is speaking the same language. Projects are launched from each perspective, all in parallel, with no shared model connecting them. Three years later: a microservices migration that does not support the customer experience initiative because no one mapped which services own which customer data.

**THE BREAKING POINT:**
The transformation post-mortem finds that each team had a correct plan for their domain, but no one had mapped the dependencies between domains. The business capability change required a data model change that required an application change that required an infrastructure change - and all four were planned independently on different timelines.

**THE INVENTION MOMENT:**
TOGAF and Zachman independently converged on the same insight: every enterprise can be described using exactly four domains that form a dependency chain. Business drives Data needs; Data needs drive Application design; Applications drive Technology choices. This four-layer model (BDAT) became the universal shared language for EA.

**EVOLUTION:**
Early EA frameworks listed these domains in isolation. Modern EA adds cross-domain mapping as the primary value: a capability map that shows which applications implement which capabilities, which data objects those applications own, and which technology components host those applications. The cross-domain map - not any individual domain - is EA''s core artefact.

---

### 📘 Textbook Definition

The **BDAT domains** (Business, Data, Application, Technology) are the four fundamental layers of an enterprise architecture, forming a dependency hierarchy: Business needs drive Data requirements; Data requirements inform Application design; Applications determine Technology choices. Each domain has distinct stakeholders, artefacts, and governance concerns.

---

### ⏱️ Understand It in 30 Seconds

**One line:** BDAT is the four-layer model that gives every enterprise conversation a shared vocabulary: Business - Data - Application - Technology.

> Think of a restaurant. The menu (Business) determines what ingredients (Data) are needed. Ingredients determine what kitchen equipment (Application) is required. Equipment determines what utilities and space (Technology) must be provisioned. Change the menu and everything downstream must adapt - in the right order.

**One insight:** The BDAT dependency direction is always Business → Data → Application → Technology. Strategic decisions cascade downward. Technology constraints escalate upward as trade-offs.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Business needs are the ultimate source of all IT requirements. No IT investment is justified except as an expression of business need.
2. Data is the enterprise''s most durable asset. Applications come and go; the data they generate must outlast them.
3. Applications implement capabilities, not business processes. One application may implement multiple capabilities; one capability may span multiple applications.
4. Technology is a constraint and enabler, not a strategy. It should be chosen to serve the three layers above it.

**DERIVED DESIGN:**
Each domain has a primary owner:
- **Business:** Business owners, process owners, capability owners
- **Data:** Data owners, Chief Data Officer, data stewards
- **Application:** Product owners, enterprise architects, solution architects
- **Technology:** Infrastructure teams, platform engineers, cloud architects

**THE TRADE-OFFS:**
**Gain:** Common language. Clear ownership. Dependency traceability. Cross-domain impact assessment.
**Cost:** Maintaining cross-domain mappings is ongoing work. Boundary disputes between domains are common (who owns a data pipeline - Application or Data?).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** An enterprise genuinely has these four different concerns that must be governed differently.
**Accidental:** Rigid frameworks that require every artefact to be classified in exactly one domain, when most real artefacts span domains.

---

### 🧪 Thought Experiment

**SETUP:** An enterprise plans to replace its order management system (OMS). The project team defines it as an "Application" domain project. A BDAT-aware architect reviews the plan.

**WHAT HAPPENS WITHOUT BDAT FRAMING:** The project delivers a new OMS. Three months post-go-live: the data team discovers the new OMS uses a different order data model, breaking 14 downstream reports. The infrastructure team discovers the new OMS requires a new data centre zone, changing network topology. The business discovers the new OMS does not support a capability they assumed would be included.

**WHAT HAPPENS WITH BDAT FRAMING:** Before the project starts, the architect maps: Business - what capabilities does OMS implement? Data - what data objects does OMS own, consume, and produce? Application - what systems does OMS integrate with? Technology - what infrastructure does OMS require? Each domain''s requirements are captured and signed off by the relevant owner. The project delivers to all four domains'' requirements simultaneously.

**THE INSIGHT:** An OMS replacement is not an Application domain project. It is a BDAT project. All four domains have requirements and all four must be governed through the change.

---

### 🧠 Mental Model / Analogy

> Think of BDAT as the four layers of a city''s infrastructure planning. Business = the economic plan (what industries will operate here). Data = the information infrastructure (postal system, telecommunications, public records). Application = the buildings and facilities (offices, hospitals, schools). Technology = the physical utilities (roads, electricity, water, sewage). Every city planning decision must consider all four layers. Building a hospital (Application) requires an economic justification (Business), patient data systems (Data), and utility capacity (Technology).

- **Economic plan** = Business architecture
- **Information infrastructure** = Data architecture
- **Buildings and facilities** = Application architecture
- **Physical utilities** = Technology architecture

Where this analogy breaks down: in software, all four layers are simultaneously malleable; in city planning, physical infrastructure changes on a 20-50 year cycle.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
BDAT is four categories that describe an enterprise completely: what the business does, what data it uses, what applications it runs, and what technology it runs them on. Together, they give a complete picture.

**Level 2 - How to use it (junior developer):**
Every system you build lives in all four BDAT domains. Your application (Application) implements a business capability (Business), owns certain data objects (Data), and runs on specific infrastructure (Technology). When you make a design decision, ask: which domain does this affect? Who owns that domain? Have they reviewed this?

**Level 3 - How it works (mid-level engineer):**
The value of BDAT is cross-domain traceability. An application portfolio links Application to Business (which capabilities does this system implement?). A data lineage map links Data to Application (which systems produce and consume which data?). An infrastructure map links Technology to Application (where does each system run?). Together, these maps answer impact questions: "If we retire system X, what capabilities are affected? What data flows break? What technology can be decommissioned?"

**Level 4 - Why it was designed this way (senior/staff):**
BDAT emerged from the observation that enterprise failures are almost always cross-domain failures: a business decision was made without considering data implications, or an application was retired without considering technology dependencies. The four-domain model forces organisations to make cross-domain dependencies explicit. TOGAF''s ADM structures every phase around BDAT - Phase B (Business), Phase C (Data + Application, called Information Systems), Phase D (Technology) - deliberately mapping each domain before combining them.

**Expert Thinking Cues:**
- When a project encounters unexpected scope, it almost always represents an unmapped cross-domain dependency.
- "Data migration" projects that fail are usually Application → Data mapping failures: the application was changed without capturing the data model change.
- Governance conflicts (who owns the API contract?) are usually Application-Data or Application-Business boundary disputes.

---

### ⚙️ How It Works (Mechanism)

**Domain 1 - Business Architecture:**
Describes what the enterprise does and why. Primary artefacts: business capability map, value stream map, business process model, organisation map. Primary question: "What must the business be able to do?"

**Domain 2 - Data Architecture:**
Describes what information the enterprise manages, where it lives, and how it flows. Primary artefacts: canonical data model, data dictionary, data flow diagram, data ownership matrix. Primary question: "What does the business need to know, and who is responsible for it?"

**Domain 3 - Application Architecture:**
Describes the applications that implement business capabilities and manage data. Primary artefacts: application portfolio, integration map, application-to-capability mapping, application lifecycle register. Primary question: "What systems implement which capabilities and manage which data?"

**Domain 4 - Technology Architecture:**
Describes the infrastructure, platforms, and standards that host applications. Primary artefacts: technology portfolio, infrastructure diagram, technology standards catalogue, cloud architecture diagram. Primary question: "What infrastructure runs which applications, to what standards?"

**Cross-domain mapping (the high-value artefact):**
```
Business Capability Map
        |  (which apps implement which capabilities?)
        v
Application Portfolio
        |  (which apps own which data?)
        v
Data Dictionary / Ownership Matrix
        |  (which infrastructure hosts which apps?)
        v
Technology Portfolio
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Business Strategy
      |
      v
Business Architecture    <- Business owners
  (Capabilities, Processes, Organisation)
      |
      v
Data Architecture        <- Data owners
  (What data is needed, owned, governed)     <- YOU ARE HERE
      |
      v
Application Architecture <- Product / EA
  (What systems implement capabilities)
      |
      v
Technology Architecture  <- Platform / Infra
  (What infrastructure hosts systems)
```

**FAILURE PATH:**
Technology-led strategy → technology is chosen before business needs are defined → applications built to technology constraints rather than business requirements → business requirements cannot be met by the chosen technology.

**WHAT CHANGES AT SCALE:**
At small scale, one team governs all four domains informally. At medium scale, different teams own different domains and need explicit cross-domain mapping. At large scale, each domain has dedicated governance (Chief Data Officer for Data, Platform team for Technology, EA function for Application), and cross-domain coordination is a formal process.

---

### ⚖️ Comparison Table

| Domain | Primary Owner | Key Question | Primary Artefact | Stability |
|:-------|:-------------|:-------------|:-----------------|:---------|
| **Business** | Business units / CEO | What must the business do? | Capability map | Stable (changes over years) |
| **Data** | CDO / Data stewards | What must we know and govern? | Data dictionary | Moderate (changes with business) |
| **Application** | CIO / EA / Product | What systems implement capabilities? | Application portfolio | Dynamic (changes with projects) |
| **Technology** | CTO / Platform / Infra | What infrastructure do we run? | Technology portfolio | Moderate (changes with platforms) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:--------------|:--------|
| "BDAT is a TOGAF-specific concept" | BDAT appears in all major EA frameworks; TOGAF, Zachman, FEAF, and Gartner EA all use this four-domain structure |
| "Data is part of Application architecture" | Data is a separate domain because data outlasts applications; data governance requires different ownership than application governance |
| "Technology architecture means cloud architecture" | Technology architecture covers all infrastructure: on-premises, cloud, networking, hardware, and operations platforms |
| "The four domains are independent" | They are interdependent with a clear dependency direction; changes in Business cascade down; constraints in Technology escalate up |
| "BDAT is only relevant at large scale" | Any organisation running more than 10 systems benefits from explicit BDAT mapping to understand cross-domain dependencies |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Application-first strategy**
**Symptom:** IT strategy is defined as "migrate to microservices" without a Business domain rationale.
**Root Cause:** Technology or Application domain driving strategy instead of Business domain.
**Diagnostic:**
```
Ask: "What business capability improvement
does this migration deliver?"
If no clear answer: Application-first failure.
```
**Fix:**
- BAD: IT strategy = technology choices
- GOOD: IT strategy = capability improvements enabled by technology choices
**Prevention:** Require every IT strategy initiative to have a mapped Business capability as its justification.

**Failure Mode 2: Data domain orphaned**
**Symptom:** Applications are migrated or retired, but data migration is treated as an afterthought. Post-migration reports break; analytics cannot access historical data.
**Root Cause:** Application domain planning did not include Data domain mapping.
**Diagnostic:**
```bash
# After application migration, query data lineage:
# Check which downstream consumers reference
# the old application's data store.
# Any active consumer = data domain impact
# that was not planned.
```
**Fix:** Require Data domain sign-off on all Application domain change plans.
**Prevention:** Maintain a data ownership matrix that links every data object to its producing and consuming applications.

**Security Failure Mode: Technology domain without security domain**
**Symptom:** New cloud technology is provisioned without security review because it is classified as "Technology domain" and the security team is not a Technology domain stakeholder.
**Root Cause:** Security is cross-cutting; assigning it to a single BDAT domain causes it to be missed in others.
**Fix:**
- BAD: Security is a Technology domain concern
- GOOD: Security is a cross-cutting concern with mandatory review in all four BDAT domains
**Prevention:** Add security as an explicit cross-cutting concern in the EA governance model, with security sign-off required at each domain for any change above a risk threshold.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- SAP-065 - Enterprise Architecture - What It Is and Why It Exists
- SAP-001 - What Is Software Architecture

**Builds On This (learn these next):**
- SAP-067 - Business Capability Mapping
- SAP-069 - TOGAF Framework
- SAP-071 - Zachman Framework

**Alternatives / Comparisons:**
- SAP-058 - Formal Architecture Specification (C4, ADL, UML) (application-level decomposition)
- SAP-010 - Enterprise Application Architecture (application-domain focus)

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════════════╗
║ WHAT IT IS    Four-domain model for describing   ║
║               any enterprise completely          ║
║ PROBLEM       Cross-domain blind spots cause     ║
║               failed projects and integrations   ║
║ KEY INSIGHT   Dependency goes one way: Business  ║
║               → Data → Application → Technology  ║
║ USE WHEN      Planning cross-team or cross-system║
║               changes; any EA artefact creation  ║
║ AVOID WHEN    Single-system design; no need for  ║
║               enterprise-level coordination      ║
║ TRADE-OFF     Complete cross-domain picture vs   ║
║               overhead of maintaining 4 views    ║
║ ONE-LINER     "The four lenses every enterprise  ║
║                must see itself through"          ║
║ NEXT EXPLORE  SAP-069 TOGAF, SAP-071 Zachman     ║
╚══════════════════════════════════════════════════╝
```

**If you remember only 3 things:**
1. The four domains are Business, Data, Application, Technology - in dependency order.
2. Cross-domain mapping (which apps implement which capabilities, own which data) is the highest-value EA artefact.
3. Data outlasts applications - always plan data governance independently of application lifecycle.

**Interview one-liner:** "BDAT structures enterprise architecture across four domains - Business defines what the enterprise must do, Data what it must know, Application what systems implement, and Technology what infrastructure hosts them - with a strict dependency chain flowing from business needs down to technology choices."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Complex systems can always be decomposed into a set of stable domains with clear dependency directions. Mapping those dependencies explicitly is the foundation of governance at scale.

**Where else this pattern appears:**
- **OSI networking model** - seven layers with strict dependency direction, each with distinct ownership and governance.
- **Clean Architecture** - Entities → Use Cases → Interface Adapters → Infrastructure follows the same "business need drives technology choice" dependency direction as BDAT.
- **Supply chain design** - Customer demand (Business) drives inventory requirements (Data), which drive warehouse systems (Application), which drive logistics infrastructure (Technology).

---

### 💡 The Surprising Truth

Despite BDAT being the universal four-domain model used by TOGAF, Zachman, FEAF, and Gartner EA, organisations consistently treat Data as the hardest domain to govern - not Technology. A Forrester survey (2021) found that 68% of EA practitioners rated "data ownership disputes" as their most common governance failure, compared to only 22% citing technology standardisation failures. The reason: technology is owned by teams with clear mandates (infrastructure, cloud platform); data ownership is structurally ambiguous because data flows across application and organisational boundaries, and no single team naturally owns a data object that multiple applications produce and consume.

---

### 🧠 Think About This Before We Continue

**Question 1 (System Interaction):** An organisation''s Business domain defines a new capability: "Real-time personalised recommendations." Trace what this capability requires through the Data, Application, and Technology domains. What cross-domain dependencies must be mapped before the project starts?

*Hint:* Investigate how Amazon''s engineering blog describes the cross-domain dependency chain for their recommendation engine, particularly the data freshness requirements that drove infrastructure choices.

**Question 2 (Scale):** As an enterprise grows from 50 to 500 applications, the Application-to-Business capability mapping becomes increasingly stale because it is maintained manually. What approaches exist to automate or continuously maintain cross-domain mappings at scale, and what are the trade-offs of each?

*Hint:* Research how EA tooling vendors (LeanIX, Ardoq, Alfabet) approach automated capability mapping through integrations with CI/CD systems, CMDBs, and cloud provider APIs.

**Question 3 (Design Trade-off):** The BDAT model places Data as a separate domain from Application. Some architects argue Data should be a property of the Application domain. What are the strongest arguments for keeping Data as an independent domain, and under what organisational circumstances might collapsing it into Application be justified?

*Hint:* Compare how organisations with a strong Chief Data Officer function govern data differently from organisations where data is treated as an application concern, and examine what governance failures each model is prone to.