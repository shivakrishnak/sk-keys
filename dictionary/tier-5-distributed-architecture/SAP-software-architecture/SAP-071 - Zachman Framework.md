---
id: SAP-071
title: Zachman Framework
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★☆
depends_on: SAP-065, SAP-066
used_by: SAP-073, SAP-074
related: SAP-069, SAP-070, SAP-072
tags:
  - architecture
  - intermediate
  - mental-model
  - pattern
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 71
permalink: /software-architecture/zachman-framework/
---

# SAP-071 - Zachman Framework

⚡ TL;DR - The Zachman Framework is a 6x6 classification matrix that provides a complete taxonomy for describing any enterprise from six stakeholder perspectives across six interrogatives (What, How, Where, Who, When, Why).

| SAP-071 | Category: Software Architecture Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | SAP-065, SAP-066 | |
| **Used by:** | SAP-073, SAP-074 | |
| **Related:** | SAP-069, SAP-070, SAP-072 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An enterprise architecture review concludes. Three weeks later, a business analyst asks: "Where is the data flow diagram showing how customer data moves from our CRM to the analytics platform?" No one knows. The EA team has business process diagrams (HOW), organisation charts (WHO), and system diagrams (WHAT), but the WHERE (data flow), WHEN (event timing), and WHY (business rules) were never captured. The question cannot be answered because the enterprise''s architecture was never described completely - only the parts each team thought to capture.

**THE BREAKING POINT:**
A regulatory audit requires the organisation to demonstrate exactly who has access to what data, when, and under what business rules. The EA team can answer WHO (from org charts) and WHAT (from data dictionaries) but not WHEN (from process models) or WHY (from policy documents) in a structured, cross-referenced way. The audit takes 6 months because the six dimensions of the enterprise were never mapped to each other.

**THE INVENTION MOMENT:**
John Zachman, working at IBM in the 1980s, observed that every complex artefact (a building, an aircraft, an enterprise) can be described by answering six questions (What, How, Where, Who, When, Why) from six different perspectives (Planner, Owner, Designer, Builder, Contractor, User). Combining these two dimensions produces a 36-cell matrix that is provably complete - any artefact of any enterprise can be placed in exactly one cell. Published in 1987 in IBM Systems Journal, the Zachman Framework became the foundational classification taxonomy for enterprise architecture.

**EVOLUTION:**
Zachman published the original framework in 1987 and refined it in 1992 (adding the WHY column). The framework has remained structurally unchanged since then - a testament to its claim to completeness. Zachman co-founded Zachman International to license and train on the framework. The 2011 Zachman Framework v3 updated terminology but preserved the 6x6 structure. Unlike TOGAF, Zachman is not a process; it is a taxonomy - it tells you WHAT to describe, not HOW to create the architecture.

---

### 📘 Textbook Definition

The **Zachman Framework** is a two-dimensional classification schema for enterprise architecture artefacts. Its rows represent six stakeholder perspectives (Planner, Owner, Designer, Builder, Contractor, User/Operator), and its columns represent six interrogatives (What/Data, How/Function, Where/Network, Who/People, When/Time, Why/Motivation). Each of its 36 cells represents a unique type of architecture artefact. The framework is prescriptive about completeness (all 36 cells exist for any enterprise) but not prescriptive about process (it does not specify how to fill them).

---

### ⏱️ Understand It in 30 Seconds

**One line:** Zachman is a 36-cell matrix that ensures you describe an enterprise from every perspective and every angle - a completeness guarantee for architecture.

> Think of Zachman as an X-ray, MRI, and CT scan for an enterprise. An X-ray (WHAT/structure) shows one view. An MRI (HOW/function) shows another. A CT scan (WHERE/location) shows another. No single scan is complete. A radiologist reviewing all three has a complete picture. Zachman is the protocol that specifies exactly which scans are needed and who interprets each one.

**One insight:** Zachman''s power is not in filling all 36 cells - it is in using the matrix to identify which cells are missing. Most EA failures happen because certain cells were never populated: the WHY column (business rules), the WHEN column (events and timing), or the WHERE column (network and data flows) are chronically under-described.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Any complex artefact can be described completely by answering: What (material), How (process), Where (location), Who (people), When (time), Why (motivation).
2. Different stakeholders need different levels of abstraction of the same answers. A CEO''s "What" is a business concept; an engineer''s "What" is a data schema.
3. The matrix is complete: any architecture artefact belongs in exactly one cell.
4. Cells are independent: the WHAT at the Owner row is not derived from the WHAT at the Planner row - they are different artefacts for different audiences.

**DERIVED DESIGN:**
The 6x6 matrix:

ROWS (Perspectives):
- Row 1 - Planner / Executive: context and scope
- Row 2 - Owner / Business: business model
- Row 3 - Designer / Architect: system model
- Row 4 - Builder / Engineer: technology model
- Row 5 - Subcontractor / Developer: detailed model
- Row 6 - User / Operator: actual instantiation

COLUMNS (Interrogatives):
- Col 1 - WHAT (Data): entities, relationships
- Col 2 - HOW (Function): processes, activities
- Col 3 - WHERE (Network): locations, connectivity
- Col 4 - WHO (People): organisations, roles
- Col 5 - WHEN (Time): events, cycles, schedules
- Col 6 - WHY (Motivation): goals, rules, constraints

**THE TRADE-OFFS:**
**Gain:** Guaranteed completeness. Common language for all stakeholders. Excellent for gap analysis and audit.
**Cost:** 36 cells is overwhelming if attempted completely. No process guidance. Does not scale to continuous delivery without significant adaptation.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Every enterprise genuinely has 36 types of architecture artefacts that different stakeholders need.
**Accidental:** Attempting to populate all 36 cells in equal depth before making any decision.

---

### 🧪 Thought Experiment

**SETUP:** An organisation needs to demonstrate GDPR compliance for its customer data processing. It has extensive HOW documentation (process maps), WHAT documentation (data dictionaries), and WHO documentation (org charts). Using the Zachman matrix, identify which cells are missing.

**ANALYSIS USING ZACHMAN:**
- WHAT (Data) - Row 3: Data model exists (partially satisfies)
- HOW (Function) - Row 3: Process maps exist (satisfies)
- WHERE (Network) - Row 3: MISSING. No data flow diagram showing WHERE customer data moves between systems
- WHO (People) - Rows 2-4: Access control lists exist (partially satisfies)
- WHEN (Time) - Row 3: MISSING. No retention schedule showing WHEN data is deleted or archived
- WHY (Motivation) - Row 2: MISSING. Business rules for data processing consent not formalised in an artefact

**THE INSIGHT:** The Zachman matrix made the compliance gaps structurally visible. Three of the six columns (WHERE, WHEN, WHY) are under-represented. The specific artefacts needed for GDPR compliance can be mapped directly to the missing Zachman cells: data flow map (WHERE), retention schedule (WHEN), consent processing rules (WHY).

---

### 🧠 Mental Model / Analogy

> Think of Zachman as the floor plan of a museum, where each room contains one type of knowledge about the enterprise. The museum has 6 wings (the 6 interrogatives: What, How, Where, Who, When, Why). Each wing has 6 floors (the 6 stakeholder perspectives: Planner to User). The artefact in each room is unique: the CEO''s view of what entities exist (Room: What/Planner) is a different artefact from the engineer''s view (Room: What/Builder). A complete enterprise architecture means every room has an artefact in it. A gap analysis finds the empty rooms.

- **Museum wings (What, How, Where, Who, When, Why)** = interrogatives
- **Museum floors (Planner to User)** = stakeholder perspectives
- **Each room** = one type of architecture artefact
- **Empty rooms** = architecture gaps
- **Museum tour** = architecture review

Where this analogy breaks down: a physical museum has fixed-size rooms; Zachman cells vary enormously in the volume and complexity of content they represent.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Zachman is a table with 6 rows (different types of people who need to understand the enterprise) and 6 columns (6 questions: what, how, where, who, when, why). The table tells you what type of documentation an enterprise needs to be completely described.

**Level 2 - How to use it (junior developer):**
Use the Zachman matrix as a checklist. When documenting a system, check: do you have artefacts for all six questions at your row (Row 4 - Builder)? You need: a data schema (WHAT), a component diagram (HOW), a deployment diagram (WHERE), a team ownership diagram (WHO), a sequence diagram (WHEN), and a business rules document (WHY). If any are missing, your documentation has a gap that will cause problems for whoever needs to understand your system later.

**Level 3 - How it works (mid-level engineer):**
Zachman is used primarily for two purposes: gap analysis (which cells are empty in the current architecture?) and stakeholder communication (which cells does this stakeholder need?). Each row''s artefacts are written for a different audience: Row 2 (Owner) artefacts are for business stakeholders; Row 4 (Builder) artefacts are for engineers. The same question (WHERE) gets a different answer for each audience: a business owner needs a geographic location diagram; an engineer needs a network topology diagram.

**Level 4 - Why it was designed this way (senior/staff):**
Zachman''s matrix was designed to be provably complete - every artefact a complex enterprise needs maps to exactly one cell. This mathematical completeness is the framework''s distinguishing property and its primary claim to uniqueness. Unlike TOGAF (which tells you how to do EA) or ArchiMate (which tells you how to draw EA), Zachman tells you what MUST exist in a complete architecture description. This makes it uniquely suited for compliance and audit contexts where completeness is legally required, not just organisationally convenient.

**Expert Thinking Cues:**
- When a project encounters unexpected scope, check which Zachman column was under-documented. The WHEN column (events and timing) is the most common source of integration surprises.
- The WHY column (business rules and motivation) is chronically under-described in most enterprise architectures; it is the first casualty of schedule pressure.
- The Zachman Framework is most valuable for what it finds MISSING, not for what it certifies as present.

---

### ⚙️ How It Works (Mechanism)

**The 6x6 Matrix - Key Cells:**

```
         WHAT         HOW          WHERE
         (Data)      (Function)   (Network)
PLANNER  Business     Business     Business
         Scope        Scope        Locations
OWNER    Business     Business     Business
         Entities     Processes    Logistics
DESIGNER Logical      Application  Distributed
         Data Model   Architecture System
BUILDER  Physical     Program      Technology
         Data Model   Code         Architecture
SUBCON   Data         Detail       Network
         Definitions  Programs     Addresses
USER     Actual       Executable   Real
         Data         Functions    Networks

         WHO          WHEN         WHY
         (People)    (Time)       (Motivation)
PLANNER  Business     Business     Business
         Org          Events       Goals
OWNER    Work Units   Business     Business
         and Roles    Process      Rules
DESIGNER Human        Control      Rules
         Interface    Structure    Specification
BUILDER  Presentation Processing  Rule
         Architecture Structure    Specification
SUBCON   Security     Timing       Rule
         Roles        Definitions  Conditions
USER     Real         Real         Real
         People       Schedules    Strategies
```

**How to use the matrix:**
1. Identify the stakeholder perspective (which row)
2. Identify the interrogative (which column)
3. The cell defines what artefact is needed
4. Populate that cell with the specific enterprise artefact
5. Trace dependencies between cells across rows (vertical) and columns (horizontal)

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (gap analysis use):**
```
Architecture Review Triggered
          |
          v
Map Existing Artefacts to Zachman Cells
  Which cells have artefacts?
  Which cells are empty?
          |
          v
Identify Empty Cells by Priority     <- YOU ARE HERE
  Regulatory requirements: WHERE, WHEN, WHY
  Integration planning: WHERE, WHEN
  Business alignment: WHY, HOW
          |
          v
Commission Missing Artefacts
  Assign owner for each empty cell
  Define required artefact type
          |
          v
Populate Cells
  Validate against business requirements
          |
          v
Complete Architecture Baseline
  Fully populated Zachman matrix
```

**FAILURE PATH:**
Focus on rows 3-4 (Designer, Builder) only → rows 1-2 (Planner, Owner) under-documented → business stakeholders cannot verify that architecture meets strategic requirements → Phase G governance fails because there is no business-level artefact to measure implementation against.

**WHAT CHANGES AT SCALE:**
At small scale: Zachman used as a checklist; 8-12 cells populated. At medium scale: explicit cell ownership assigned to teams; tooling maps artefacts to cells. At large scale: dedicated governance process ensures all 36 cells are populated and maintained for critical systems; automated tooling validates cell coverage.

---

### ⚖️ Comparison Table

| Framework | Type | Tells You | Does Not Tell You | Best Used For |
|:----------|:-----|:----------|:------------------|:--------------|
| **Zachman** | Classification | WHAT to describe | HOW to develop it | Completeness checks, audits |
| **TOGAF** | Process | HOW to develop EA | WHAT to describe in each artefact | EA programme governance |
| **ArchiMate** | Modelling language | HOW to draw artefacts | WHAT artefacts to produce | EA diagramming |
| **BDAT (TOGAF)** | Domain model | WHICH domains to cover | How to decompose each domain | Domain ownership and governance |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:--------------|:--------|
| "Zachman requires populating all 36 cells" | Zachman defines what exists; organisations choose which cells to populate based on their context and priorities |
| "Zachman is outdated (published 1987)" | The 6x6 structure is unchanged because it is complete - nothing has emerged in 35 years that requires a new row or column |
| "Zachman and TOGAF do the same thing" | They are complementary: TOGAF = process for developing EA; Zachman = classification for what an EA must contain |
| "Row 6 (User) is just documentation" | Row 6 represents the actual instantiation - the running system, real data, real people; it is the ultimate validation of all other rows |
| "The columns represent data, process, and IT only" | The WHEN and WHY columns are purely business concerns; the WHERE column spans both business (locations) and technical (network topology) |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Zachman used as a documentation mandate**
**Symptom:** The EA team requires all 36 cells to be populated for every system. The overhead is enormous; teams spend more time on Zachman documentation than on actual design.
**Root Cause:** Framework used as a completeness requirement rather than a gap analysis tool.
**Diagnostic:**
```
Ask: "Which cell of the Zachman matrix
is this artefact enabling?"
If the team cannot answer, the artefact
may be produced for compliance,
not for decision support.
```
**Fix:** Use Zachman as a gap analysis tool, not a documentation mandate. Populate only the cells needed for the current initiative''s questions.
**Prevention:** Define a "minimum viable Zachman" for each system type: which cells are mandatory, which are optional.

**Failure Mode 2: WHEN column absent**
**Symptom:** Integration projects fail because event sequences, timing constraints, and retry patterns are not documented. Each team makes different timing assumptions.
**Root Cause:** WHEN column (events, cycles, schedules) never populated; omitted as "too detailed" for EA.
**Diagnostic:**
```
Check: Does any architecture artefact
describe WHEN events occur, their
ordering, and timing constraints
for key integration flows?
No: WHEN column is absent.
```
**Fix:** Add sequence diagrams and event flow documentation (Row 3, WHEN) for all critical integration points.
**Prevention:** Include WHEN column artefacts as mandatory for integration-heavy systems.

**Security Failure Mode: WHY column missing security rules**
**Symptom:** Systems implement authentication and authorisation but without reference to business rules that define who is authorised for what and under which conditions.
**Root Cause:** WHY column (motivation, rules) not populated with security policy and business rules.
**Diagnostic:**
```
Check: Is there an artefact mapping
business rules (WHY) to access control
rules (WHO) to system implementations
(HOW) for sensitive data operations?
No: security governance gap.
```
**Fix:** Populate Zachman cells for WHY (business rules) and WHO (roles/responsibilities) explicitly referencing security policies.
**Prevention:** Include security policy as a WHY column artefact requirement for all systems handling sensitive data.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- SAP-065 - Enterprise Architecture - What It Is and Why It Exists
- SAP-066 - Enterprise Architecture Domains - BDAT

**Builds On This (learn these next):**
- SAP-073 - Enterprise Architecture Maturity Models
- SAP-072 - ArchiMate (the modelling language for filling Zachman cells)

**Alternatives / Comparisons:**
- SAP-069 - TOGAF Framework (process vs classification)
- SAP-070 - TOGAF ADM (process that Zachman lacks)

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════════════╗
║ WHAT IT IS    36-cell matrix classifying all EA  ║
║               artefacts by perspective x question ║
║ PROBLEM       EA misses entire artefact types    ║
║               (WHEN, WHY columns chronically)    ║
║ KEY INSIGHT   Use Zachman to find GAPS, not to   ║
║               mandate all 36 cells               ║
║ USE WHEN      Compliance audits; architecture    ║
║               completeness reviews; gap analysis ║
║ AVOID WHEN    As a mandatory documentation       ║
║               framework for every system         ║
║ TRADE-OFF     Guaranteed completeness vs         ║
║               overwhelming if applied literally  ║
║ ONE-LINER     "X-ray for enterprise completeness"║
║ NEXT EXPLORE  SAP-069 TOGAF, SAP-072 ArchiMate   ║
╚══════════════════════════════════════════════════╝
```

**If you remember only 3 things:**
1. Zachman is a classification framework (what to describe), not a process (how to develop it) - use it with TOGAF, not instead of it.
2. The six interrogatives are: What, How, Where, Who, When, Why - the WHEN and WHY columns are almost always under-documented.
3. Use Zachman''s matrix for gap analysis: find the empty cells, not to fill all 36.

**Interview one-liner:** "The Zachman Framework is a 6x6 classification matrix that provides a complete taxonomy for enterprise architecture artefacts, organised by six stakeholder perspectives (Planner to User) and six interrogatives (What, How, Where, Who, When, Why) - used primarily for completeness auditing rather than as a development process."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Completeness in complex systems is achieved by enumerating all necessary perspectives and all necessary questions, then verifying every combination is covered. A framework that guarantees completeness by structure is more reliable than one that relies on the practitioner to remember everything.

**Where else this pattern appears:**
- **Requirements engineering (MoSCoW + stakeholder matrix)** - applying the same interrogatives across multiple stakeholder groups ensures completeness.
- **Incident post-mortems (5W1H)** - Who, What, When, Where, Why, How applied at the incident level is a subset of Zachman''s interrogatives applied to a single event.
- **API documentation (OpenAPI spec)** - an OpenAPI specification answers: What (schemas), How (operations), Where (servers), Who (security), When (lifecycle), Why (description) - a Zachman-like completeness check for API contracts.

---

### 💡 The Surprising Truth

The Zachman Framework''s 6x6 structure - published in 1987 - has survived unchanged for over 35 years, making it one of the most stable frameworks in enterprise IT. This stability is not inertia; Zachman has explicitly defended the structure against proposed extensions, arguing that any proposed seventh column or seventh row can be shown to already map to an existing cell. The framework''s claim to mathematical completeness - that it covers all possible artefacts for any complex artefact, not just enterprises - means it has been applied to describe buildings, aircraft, software systems, and even biological organisms using the same 36-cell taxonomy. No practitioner has yet published a counterexample showing an enterprise artefact that does not fit in exactly one cell.

---

### 🧠 Think About This Before We Continue

**Question 1 (System Interaction):** Map a microservices architecture to the Zachman Framework. Which cells at the Builder row (Row 4) correspond to: the service contract (API), the data schema, the deployment manifest, the team ownership, the event sequence, and the business rule driving the service? How does the Zachman mapping reveal what documentation your microservices architecture is missing?

*Hint:* Investigate how the C4 Model (Context, Container, Component, Code) maps to specific Zachman cells, and what Zachman cells the C4 Model does NOT cover (hint: WHO, WHEN, WHY at business levels).

**Question 2 (Scale):** At what scale does it become practically impossible to maintain a fully populated Zachman matrix, and what strategies exist to maintain Zachman-based governance without populating all 36 cells for every system?

*Hint:* Research how EA tooling platforms (Aris, Mega, Alfabet) use Zachman as an underlying classification model while surfacing only context-relevant cells to each stakeholder - and what metadata is required to enable cell-level navigation at scale.

**Question 3 (Design Trade-off):** The Zachman Framework claims to be complete and unchanging. Critics argue that it was designed for the siloed, waterfall-era enterprise and does not account for modern concerns: DevOps (continuous delivery), cloud (elastic infrastructure), and AI (emergent behaviour). Is the 6x6 structure genuinely complete for a modern cloud-native enterprise, or are there modern concerns that do not map to any existing cell?

*Hint:* Attempt to place the following modern artefacts in Zachman cells: a Terraform state file, a Kubernetes RBAC policy, a machine learning model, a GitOps pipeline, and a chaos engineering experiment. If each maps cleanly, the framework is complete; if any do not, examine what property of the artefact the framework fails to capture.