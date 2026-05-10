---
id: SAP-042
title: "ArchiMate (EA Modelling Language)"
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★☆
depends_on: SAP-038, SAP-051
used_by: SAP-084, SAP-085
related: SAP-028, SAP-014, SAP-013
tags:
  - architecture
  - intermediate
  - pattern
  - bestpractice
status: complete
version: 3
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 28
permalink: /software-architecture/archimate-ea-modelling-language/
---

# SAP-015 - ArchiMate (EA Modelling Language)

⚡ TL;DR - ArchiMate is The Open Group''s open standard modelling language for enterprise architecture, providing a precise, cross-domain notation that allows BDAT relationships to be expressed in a single, consistent visual language.

| SAP-015 | Category: Software Architecture Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | SAP-038, SAP-051 | |
| **Used by:** | SAP-084, SAP-085 | |
| **Related:** | SAP-028, SAP-014, SAP-013 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An enterprise architecture team produces 14 architecture diagrams for a transformation programme. Each diagram uses a different notation: UML for data models, BPMN for processes, ad-hoc boxes-and-arrows for application diagrams, and Visio shapes for infrastructure. A stakeholder asks: "Show me how the customer onboarding business process relates to the systems that implement it and the data it creates." No diagram shows all three. The information exists but in incompatible notations that cannot be combined into a single view.

**THE BREAKING POINT:**
The architecture review board receives diagrams from 6 different teams. Each diagram is technically correct within its own notation, but the team cannot assess cross-domain dependencies because the notations are incompatible. Two teams have drawn the same system with different names in different diagrams - a duplication that no one can detect without side-by-side manual comparison.

**THE INVENTION MOMENT:**
ArchiMate was developed by a consortium of Dutch organisations (including Telematica Instituut) in 2002-2004 and published as an open standard by The Open Group in 2009. The design insight: enterprise architecture needs a SINGLE modelling language that covers all three EA layers (Business, Application, Technology) with consistent notation and explicit cross-layer relationship types. No existing language (UML, BPMN, E/R) covers all three layers simultaneously.

**EVOLUTION:**
ArchiMate 1.0 (2009) covered the three core layers. ArchiMate 2.0 (2012) added Motivation (Goals, Drivers, Principles) and Implementation & Migration aspects. ArchiMate 3.0 (2016) added the Strategy layer (Capabilities, Resources, Value Streams) above Business, and Physical layer below Technology. ArchiMate 3.2 (2022, current) maintains backwards compatibility while refining cross-layer notation. The language is now officially aligned with TOGAF ADM phases.

---

### 📘 Textbook Definition

**ArchiMate** is an open, independent enterprise architecture modelling language developed by The Open Group. It defines: (1) three core layers (Business, Application, Technology) with explicit structural, behavioural, and motivational elements in each, (2) cross-layer relationships (realisation, serving, association), (3) five aspects (Active Structure, Behaviour, Passive Structure, Motivation, and Composite), and (4) standard viewpoints for specific stakeholder audiences. ArchiMate is designed to complement (not replace) specialised notations like UML and BPMN.

---

### ⏱️ Understand It in 30 Seconds

**One line:** ArchiMate is a single notation that draws all four EA domains in one diagram, with standard symbols for every EA concept and explicit arrows showing how layers relate.

> Think of ArchiMate as a universal adapter for EA diagrams. UML speaks the language of developers, BPMN speaks the language of process analysts, E/R speaks the language of database designers. ArchiMate speaks the language of enterprise architects - able to show a business process, the application that implements it, and the server it runs on all in a single, consistent diagram with standard notation.

**One insight:** ArchiMate''s most powerful feature is not the individual element types - it is the cross-layer relationship arrows. An "Association" from a Business Process to an Application Function to an Application Component to a Technology Service makes the entire business-to-infrastructure chain traceable in a single model.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every EA element belongs to one of three core layers: Business, Application, or Technology.
2. Every EA element is one of three aspect types: Active Structure (who/what does something), Behaviour (what is done), or Passive Structure (what is acted upon).
3. Cross-layer relationships must be typed: Serving (lower layer serves upper), Realisation (lower layer implements upper), Composition, Association.
4. Any viewpoint (a specific stakeholder''s perspective) is a filtered subset of the full ArchiMate model - the underlying model is consistent even when different viewpoints show different subsets.

**DERIVED DESIGN:**
The ArchiMate element taxonomy:

```
STRATEGY LAYER (Strategic Capabilities)
    Capability | Resource | Course of Action
BUSINESS LAYER
  Active:   Actor | Role | Business Interface
  Behaviour: Business Process | Business Function
  Passive:  Business Object | Contract | Product
APPLICATION LAYER
  Active:   Application Component | Application Interface
  Behaviour: Application Function | Application Service
  Passive:  Data Object
TECHNOLOGY LAYER
  Active:   Node | System Software | Technology Interface
  Behaviour: Technology Function | Technology Service
  Passive:  Artifact
PHYSICAL LAYER
  Equipment | Facility | Distribution Network
MOTIVATION ASPECT (cross-layer)
  Stakeholder | Driver | Assessment | Goal |
  Requirement | Constraint | Principle
```

**THE TRADE-OFFS:**
**Gain:** Single consistent notation. Cross-layer traceability. Standard viewpoints. Tooling ecosystem.
**Cost:** Steep learning curve (40+ element types). Requires dedicated tooling (Archi, BiZZdesign, Sparx EA). Risk of over-modelling: creating complete ArchiMate models that are too complex to read.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Cross-domain EA genuinely needs a notation that spans all domains with explicit cross-layer relationships.
**Accidental:** Modelling every element at every level of detail in ArchiMate before any decision is made.

---

### 🧪 Thought Experiment

**SETUP:** An enterprise needs to answer: "If the Customer Database server fails, which business capabilities are affected and which customers are impacted?" Two teams: Team A uses ad-hoc diagrams; Team B uses ArchiMate.

**WHAT HAPPENS WITHOUT ARCHIMATE (Team A):** The DBA has a database diagram. The application team has a system diagram. The business team has a capability map. None are in the same notation or cross-referenced. Answering the question requires 3 people, 3 diagrams, and 2 hours of correlation. Result: partial answer, high uncertainty.

**WHAT HAPPENS WITH ARCHIMATE (Team B):** The ArchiMate model has: Technology Node (Customer Database Server) → realises → Application Component (Customer Service) → realises → Business Function (Customer Management) → supports → Business Capability (Customer Management). The impact chain is a single query in the EA tooling: "which business elements are transitively served by the Customer Database node?" Result: complete answer in 30 seconds.

**THE INSIGHT:** ArchiMate''s explicit cross-layer relationships transform impact analysis from a manual correlation exercise to a model query. The cross-layer arrows are the language''s primary value.

---

### 🧠 Mental Model / Analogy

> Think of ArchiMate as the wiring diagram of a building. An architect has floor plans (Business layer), electrical schematics (Application layer), and structural drawings (Technology layer). Each diagram is in its own notation. A building information model (BIM) - like Revit - integrates all three in a single 3D model where you can click any element and trace its connections through all three layers: "this light switch connects to this circuit, which runs through this conduit in this wall." ArchiMate is BIM for enterprise architecture.

- **Floor plans** = Business layer (what happens in the building)
- **Electrical schematics** = Application layer (what systems run the building)
- **Structural drawings** = Technology layer (what infrastructure holds it up)
- **BIM model** = ArchiMate model (all layers in one, cross-referenced)
- **Click-to-trace** = ArchiMate cross-layer relationship traversal

Where this analogy breaks down: a building''s layers are physically separate; in an enterprise, business, application, and technology change at different rates and are governed by different teams.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
ArchiMate is a standard diagramming language for enterprise architecture, like UML is for software. It has symbols for every type of EA element (business processes, applications, servers) and standard arrows for how they connect across layers.

**Level 2 - How to use it (junior developer):**
Start by recognising ArchiMate''s three-layer structure: yellow (Business), blue (Application), green (Technology). When you see an ArchiMate diagram, trace the arrows upward from a Technology element to understand what application it serves, and what business function that application supports. When creating component diagrams, use ArchiMate''s Application Component and Application Interface elements to be consistent with the organisation''s EA model.

**Level 3 - How it works (mid-level engineer):**
ArchiMate models are stored in EA repositories (Archi, BiZZdesign) and queried to answer cross-domain questions. Standard viewpoints define which elements and relationships to show for specific audiences: the "Application Co-operation" viewpoint shows application-to-application integration; the "Technology Infrastructure" viewpoint shows deployment topology; the "Motivation" viewpoint shows business goals and their relationship to architecture decisions. Each viewpoint is a filtered query against the same underlying model.

**Level 4 - Why it was designed this way (senior/staff):**
ArchiMate was designed to fill the gap between UML (precise but developer-centric) and informal boxes-and-arrows (flexible but imprecise). Its aspect structure (Active Structure, Behaviour, Passive Structure) mirrors the fundamental structure of all systems: agents (who), actions (what), objects (on what). The decision to make it a modelling language rather than a process or classification framework was deliberate: ArchiMate pairs with TOGAF (process) and Zachman (classification) rather than competing with them.

**Expert Thinking Cues:**
- ArchiMate''s "Serving" relationship (lower layer serves upper) is the most important cross-layer relationship for impact analysis.
- The Motivation aspect is underused; it is the bridge between business strategy (Goals, Drivers) and architecture decisions (Principles, Requirements).
- Over-modelling is the primary failure mode; a 500-element ArchiMate model that no one can read is less useful than a 20-element diagram that answers one specific question.

---

### ⚙️ How It Works (Mechanism)

**Core Relationships:**
```
SERVING:     Lower element provides service to upper
             Technology Service serves Application Function
REALISATION: Lower element implements upper element
             Application Component realises Business Function
ASSOCIATION: General link between elements
COMPOSITION: Element is composed of sub-elements
AGGREGATION: Element is part of larger element
TRIGGERING:  Behavioural element initiates another
FLOW:        Transfer of information/resources
```

**Key Viewpoints (pre-defined stakeholder views):**

| Viewpoint | Purpose | Primary Audience |
|:----------|:--------|:----------------|
| Application Co-operation | Application integration patterns | Solution architects |
| Technology Infrastructure | Deployment topology | Infrastructure teams |
| Capability Map | Business capability hierarchy | Business stakeholders |
| Motivation | Goals and principles driving decisions | Executives |
| Migration | Transition from As-Is to To-Be | Programme managers |
| Stakeholder | Who cares about what concerns | Governance |

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
EA Programme Start
      |
      v
[Build Motivation View]
 Business Goals, Drivers, Principles
      |
      v
[Build Business Layer]
 Actors, Roles, Processes, Functions
 Business Objects
      |
      v
[Build Application Layer]           <- YOU ARE HERE
 Application Components, Interfaces
 Data Objects
      |
      v
[Build Technology Layer]
 Nodes, Software, Technology Services
 Artifacts
      |
      v
[Draw Cross-Layer Relationships]
 Serving / Realisation arrows linking
 Tech → App → Business
      |
      v
[Create Stakeholder Viewpoints]
 Filter model for each audience
      |
      v
[Query Model for Impact Analysis]
 "If X fails, what Business is affected?"
```

**FAILURE PATH:**
ArchiMate adopted → team models every element at full detail → model becomes a 500-element graph → no stakeholder can read any view → model abandoned → team reverts to ad-hoc diagrams → same cross-layer traceability problem as before ArchiMate.

**WHAT CHANGES AT SCALE:**
At small scale: Archi (free, open source) sufficient; 50-100 elements. At medium scale: BiZZdesign or Sparx Enterprise Architect with shared repository; 200-500 elements; viewpoints per team. At large scale: cloud-hosted EA platform; automated model updates from CI/CD and CMDB integrations; 1,000+ elements with query API for impact analysis.

---

### 💻 Code Example

ArchiMate models can be exported as XML and parsed programmatically. The Archi tool''s XML format:

```xml
<!-- BAD: Ad-hoc diagram with no cross-layer traceability -->
<!-- A Visio diagram has boxes and arrows but no semantics:
     There is no way to know if "CRM" is a business function,
     an application component, or a server name. -->

<!-- "CRM" ----> "Customer DB" : what is this? -->
```

```xml
<!-- GOOD: ArchiMate model with typed elements
     and explicit cross-layer relationships -->

<model xmlns="http://www.archimatetool.com/archimate"
       name="Customer Management Architecture">

  <!-- Business Layer -->
  <element xsi:type="archimate:BusinessProcess"
           id="bp-001"
           name="Customer Onboarding Process"/>

  <!-- Application Layer -->
  <element xsi:type="archimate:ApplicationComponent"
           id="ac-001"
           name="CRM Application"/>
  <element xsi:type="archimate:DataObject"
           id="do-001"
           name="Customer Record"/>

  <!-- Technology Layer -->
  <element xsi:type="archimate:Node"
           id="nd-001"
           name="CRM Database Server"/>

  <!-- Cross-layer relationships (THE KEY VALUE) -->
  <!-- App Component REALISES Business Process -->
  <relationship xsi:type="archimate:RealisationRelationship"
                source="ac-001"
                target="bp-001"/>

  <!-- Tech Node SERVES App Component -->
  <relationship xsi:type="archimate:ServingRelationship"
                source="nd-001"
                target="ac-001"/>

  <!-- Impact chain now traceable:
       nd-001 (server) -> serves -> ac-001 (CRM) ->
       realises -> bp-001 (Onboarding Process) -->
</model>
```

**How to test / verify correctness:**
Use the Archi tool''s built-in relationship analysis:
```
In Archi: right-click element >
  "Show in Visualiser" > set depth=3
  This traverses all relationships 3 hops
  from the selected element, showing
  the full impact chain.

Validate cross-layer coverage:
  Check that every Application Component
  has at least one Realisation relationship
  to a Business element (coverage check)
  and at least one Serving relationship
  FROM a Technology element (deployment check).
```

---

### ⚖️ Comparison Table

| Language | Layers | Precision | Learning Curve | Best For |
|:---------|:-------|:----------|:---------------|:---------|
| **ArchiMate** | Business + App + Technology | High | High (40+ types) | Cross-domain EA traceability |
| **UML** | Application (component, class) | Very High | High | Software design and specification |
| **BPMN** | Business (process only) | Very High | Medium | Business process modelling |
| **C4 Model** | Application (4 levels) | Medium | Low | Software architecture communication |
| **Informal** | Anything | Low | None | Quick communication; no traceability |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:--------------|:--------|
| "ArchiMate replaces UML" | They are complementary: ArchiMate for cross-domain EA; UML for detailed software design within the Application layer |
| "ArchiMate is part of TOGAF" | Both are Open Group standards, but separate; ArchiMate is commonly used WITH TOGAF, not as part of it |
| "You need to model everything in ArchiMate" | Model only what is needed to answer specific architecture questions; over-modelling is a common failure mode |
| "ArchiMate is only for diagrams" | ArchiMate models are queryable data models; their value is in analysis (impact, gap, dependency) as much as in visual communication |
| "ArchiMate and Zachman serve the same purpose" | Zachman classifies what artefacts exist; ArchiMate provides notation to draw those artefacts |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Model entropy**
**Symptom:** The ArchiMate model, built during architecture design, is 18 months out of date by the time it is needed for an impact assessment.
**Root Cause:** No process to update the model as systems change. Model maintained as a snapshot, not as a living artefact.
**Diagnostic:**
```
Check last-modified date on Architecture Repository
models against last deployment date for same systems.
Gap > 3 months: model entropy has set in.
```
**Fix:** Integrate model updates into the change management process: any approved architecture change triggers a model update as a mandatory task.
**Prevention:** Automate model population from authoritative sources (CMDB, cloud inventory APIs, CI/CD metadata) where possible.

**Failure Mode 2: Over-modelled, unreadable views**
**Symptom:** ArchiMate views have 100+ elements and are illegible. Stakeholders stop using them.
**Root Cause:** Architects model everything into a single view instead of creating purpose-specific viewpoints.
**Diagnostic:**
```
Count elements per view in the EA repository.
> 40 elements per view: viewpoints are
not being used correctly.
```
**Fix:** Create one viewpoint per stakeholder question. An "Application Co-operation" viewpoint should show only the applications relevant to a specific integration question.
**Prevention:** Define a viewpoint catalogue with maximum element counts and intended audience for each standard viewpoint.

**Security Failure Mode: Security elements absent from ArchiMate model**
**Symptom:** The ArchiMate model cannot answer "which systems store personal data and who has access to them?" because security roles, access controls, and data classification are not modelled.
**Root Cause:** Security team not included in ArchiMate model scope; model covers functional architecture only.
**Fix:**
- BAD: ArchiMate model limited to Business + Application + Technology functional elements
- GOOD: ArchiMate model includes: Security Roles (Business Actor with security stereotype), Data Classification (annotation on Data Objects), Access Control (Association with access-type annotation), Compliance Requirements (Constraint in Motivation aspect)
**Prevention:** Define security architecture as a required ArchiMate model layer with mandatory elements for systems handling sensitive data.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- SAP-038 - Enterprise Architecture Domains - BDAT
- SAP-051 - TOGAF Framework

**Builds On This (learn these next):**
- SAP-084 - Enterprise Architecture Maturity Models
- SAP-028 - Formal Architecture Specification (C4, ADL, UML)

**Alternatives / Comparisons:**
- SAP-014 - Zachman Framework (classification vs notation)
- SAP-051 - TOGAF Framework (process that ArchiMate supports)

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════════════╗
║ WHAT IT IS    Open standard EA modelling         ║
║               language covering BDAT in one      ║
║ PROBLEM       Cross-domain EA diagrams in        ║
║               incompatible notations; no         ║
║               cross-layer traceability           ║
║ KEY INSIGHT   Cross-layer relationship arrows    ║
║               (Serving, Realisation) are the     ║
║               primary source of value            ║
║ USE WHEN      Building EA repository; cross-     ║
║               domain impact analysis; TOGAF ADM  ║
║ AVOID WHEN    Simple system design; audience is  ║
║               developers only (use C4 or UML)    ║
║ TRADE-OFF     Precise, queryable cross-domain    ║
║               model vs steep learning curve      ║
║ ONE-LINER     "BIM for enterprise architecture"  ║
║ NEXT EXPLORE  SAP-084 EA Maturity, SAP-085 EA    ║
║               Programme Design                  ║
╚══════════════════════════════════════════════════╝
```

**If you remember only 3 things:**
1. ArchiMate has three layers: Business (yellow), Application (blue), Technology (green) - with explicit cross-layer relationships.
2. The Serving and Realisation relationships are the language''s primary value: they make cross-domain impact analysis a model query.
3. ArchiMate pairs with TOGAF (process) and Zachman (classification); all three together give a complete EA practice.

**Interview one-liner:** "ArchiMate is The Open Group''s open standard EA modelling language that spans Business, Application, and Technology layers with consistent notation and typed cross-layer relationships, enabling cross-domain impact analysis as a model query rather than a manual correlation exercise."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** When multiple domains need to communicate about the same system, a shared notation with typed relationships is more valuable than any single diagram. The notation''s value is not in what it draws but in what it makes queryable.

**Where else this pattern appears:**
- **OpenAPI for APIs** - a typed, standard notation for API contracts that makes API behaviour queryable and comparable across teams.
- **Terraform for infrastructure** - a typed notation (resource, provider, module) that makes infrastructure queryable, comparable, and impact-analysable before application.
- **ER diagrams for databases** - a typed notation (entity, relationship, cardinality) that makes database schema queryable and cross-referenced before creation.

---

### 💡 The Surprising Truth

ArchiMate was originally designed as an academic research project, not a commercial product - and it remains one of the few enterprise IT standards that is genuinely free to use. The Open Group publishes the full ArchiMate specification at no cost, and the Archi tool (the reference implementation) is open source and free. Despite this, ArchiMate''s commercial tooling market is worth hundreds of millions in annual revenue (BiZZdesign, Sparx Enterprise Architect). The paradox is that the standard itself is free, but the tooling, training, and consulting required to implement it effectively represents a significant investment. This pattern - free specification, costly ecosystem - is characteristic of Open Group standards and explains why TOGAF certification (not free) and ArchiMate certification (not free) exist alongside entirely free framework specifications.

---

### 🧠 Think About This Before We Continue

**Question 1 (System Interaction):** A cloud migration is modelled in ArchiMate with an As-Is layer and a To-Be layer. The migration involves retiring 6 on-premises servers, deploying 12 cloud services, and modifying 4 applications. How would you use ArchiMate''s Migration viewpoint and the "Transition Architecture" concept from TOGAF ADM Phase E to model the intermediate states during migration, and what ArchiMate relationship types would you use to show which elements move from As-Is to Transition to To-Be?

*Hint:* Investigate ArchiMate''s "Plateau" element (introduced in ArchiMate 2.0 for the Implementation and Migration aspect) and how it represents a stable state during a migration, with "Gap" elements representing what changes between plateaus.

**Question 2 (Scale):** An organisation wants to automate the creation and maintenance of its ArchiMate model by integrating with: (1) AWS Resource Explorer for Technology layer elements, (2) ServiceNow CMDB for Application layer, and (3) a business capability register maintained in Confluence. What data transformation is required to express these three data sources as valid ArchiMate elements with cross-layer relationships, and what are the accuracy limitations of automated model generation?

*Hint:* Research how EA tooling vendors (LeanIX, BiZZdesign) implement "Smart Discovery" features that attempt to automate ArchiMate model population from infrastructure APIs and CMDB data, and what manual curation steps they still require.

**Question 3 (Design Trade-off):** Some EA practitioners argue that ArchiMate is being superseded by API-first architecture documentation tools (like Backstage by Spotify) that automatically generate and maintain architecture documentation from code and infrastructure metadata. What does ArchiMate offer that Backstage-style tools cannot provide, and for what organisation types is each approach more appropriate?

*Hint:* Compare the stakeholder audiences of each tool: Backstage is optimised for developer self-service and platform engineering; ArchiMate is optimised for executive and cross-domain stakeholder communication. Consider what governance questions each tool can and cannot answer.