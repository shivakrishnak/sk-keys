---
layout: default
title: "Architecture Decision Record (ADR)"
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 6
permalink: /software-architecture/architecture-decision-record/
id: SAP-006
category: Software Architecture Patterns
difficulty: ★★★
depends_on: Software Architecture Patterns, SOLID Principles, Proof of Concept (POC) in Architecture, Coupling, Cohesion
used_by: Architecture Review, Technology Roadmap, Engineering Strategy
related: Architecture Review, Technology Roadmap, Proof of Concept (POC), RFC Process, Technical Debt Management
tags:
  - architecture
  - advanced
  - pattern
  - bestpractice
  - documentation
  - mental-model
---

# SAP-006 - Architecture Decision Record (ADR)

⚡ TL;DR - An ADR is a short document that captures an architecture decision, its context, the options considered, and the rationale for the choice made.

| #2300 | Category: Software Architecture Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Software Architecture Patterns, SOLID Principles, Proof of Concept (POC) in Architecture, Coupling, Cohesion | |
| **Used by:** | Architecture Review, Technology Roadmap, Engineering Strategy | |
| **Related:** | Architecture Review, Technology Roadmap, Proof of Concept (POC), RFC Process, Technical Debt Management | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team joins an existing codebase. They find a seemingly strange architectural choice: all inter-service communication uses synchronous REST calls, even for operations that appear fire-and-forget. They wonder: was this deliberate? Did someone try async and hit problems? Is this just legacy habit? They spend three days investigating git history, Slack archives, and chasing down the five original engineers (two of whom left the company). Eventually they find a vague comment "async was tried, didn't work." They don't change it - too risky without understanding why.

**THE BREAKING POINT:**
Architecture decisions without documented rationale become **unmaintainable secrets**. The longer a system exists without ADRs, the larger the "archaeological knowledge" inaccessible except by institutional memory. When that knowledge leaves the company, decisions become immutable by fear: "no one knows why this was done, so we can't change it."

**THE INVENTION MOMENT:**
Michael Nygard formalised the ADR in 2011 as part of the Documenting Architecture Decisions practice. ADRs make architecture decisions **first-class artefacts** - stored alongside code, version-controlled, reviewed like code, and accessible to everyone who needs to understand or evolve the system.

---

### 📘 Textbook Definition

An **Architecture Decision Record (ADR)** is a short, structured document that captures one significant architecture decision - the context that required the decision, the options that were considered, the decision that was made, and the consequences (positive and negative) of that decision. ADRs are stored in the codebase or documentation repository (e.g., `docs/adr/`), are version-controlled, are numbered sequentially, and are treated as living documents - they can be superseded by newer ADRs when decisions are revised. The canonical ADR format was defined by Michael Nygard; the Markdown Architectural Decision Records (MADR) and Y-Statements are common variations.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A short document that records why a decision was made so future engineers don't have to reverse-engineer it.

**One analogy:**
> A ship's logbook. Every significant navigation decision - why the captain changed course, what weather prompted deviating from the original route, why a port was chosen over another - is logged with context and reasoning. Future captains inheriting the log can understand not just where the ship went but why, and can navigate confidently with that history.

**One insight:**
ADRs are primarily a communication tool for the future. The audience is not today's team who made the decision - it is the engineer 18 months from now facing a related decision with no context.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. One ADR per decision - not one ADR per sprint or per feature.
2. Context drives the decision - an ADR without context cannot be evaluated or revised.
3. ADRs are immutable once accepted - if the decision changes, a new ADR supersedes the old one (never edit the original).
4. ADRs live in the code repository - co-located with the code they affect.
5. Status clarity - every ADR has an explicit status: Proposed / Accepted / Deprecated / Superseded.

**DERIVED DESIGN:**
From invariant 3: this is the most important discipline of ADRs. When the synchronous REST decision is reversed to async, a new ADR is created: "ADR-042 supersedes ADR-015: switching from synchronous REST to event-driven messaging." ADR-015 remains, marked `Superseded by ADR-042`. The history of both choices - and both rationales - is preserved.

From invariant 2: "Context" is the single most important ADR section, more than the "Decision" itself. Context captures the constraints, forces, and requirements that existed at the time - constraints that may change, making the original decision revisable in future.

**THE TRADE-OFFS:**
**Gain:** Architecture rationale preserved; onboarding speed for new engineers; decisions reviewable and challengeable; historical context for technical debt; evidence-based architecture evolution.
**Cost:** Requires discipline to write ADRs consistently; stale ADRs without proper supersession are misleading; not all decisions warrant ADRs (risk of ADR inflation); ADR quality varies without standards.

---

### 🧪 Thought Experiment

**SETUP:**
Two codebases of similar age and complexity. Codebase A has 45 ADRs. Codebase B has none. A new engineer joins each team.

**WHAT HAPPENS - Codebase B (no ADRs):**
Engineer discovers Redis used for both caching and session storage. Proposes splitting into separate Redis instances for isolation. Team debates for 2 hours about whether this is safe, who tried it before, and what the implications are. Result: "let's not change it" - no one knows the full picture.

**WHAT HAPPENS - Codebase A (45 ADRs):**
Engineer reads ADR-022: "Decision: use Redis for both caching and session storage. Context: in 2023, separate Redis instances were considered but rejected due to GDPR session data proximity requirement and operational cost. Consequence: Redis must be treated as stateful and backed up. Superseded when GDPR review completes in 2025." Engineer understands the constraint, checks whether the GDPR review happened, finds it did, proposes the split with proper justification.

**THE INSIGHT:**
ADRs convert architecture history from institutional memory (lossy, leaves with engineers) into organisational memory (persistent, searchable, version-controlled). The ADR from 2023 informed a correct decision in 2025.

---

### 🧠 Mental Model / Analogy

> An ADR is like a medical case note in a patient's record. When a new doctor treats a patient, the case notes explain: what symptoms led to the diagnosis, what treatments were considered, what was prescribed and why, what side effects appeared, and what follow-up is needed. Without case notes, each new doctor starts from scratch, risks repeating failed treatments, and cannot understand why current medications were chosen.

- "Patient" → the software system
- "Treating doctor" → engineer making architecture decisions
- "Case notes" → ADRs
- "Diagnosis" → architecture problem being solved
- "Prescribed treatment" → architecture decision made
- "Side effects" → consequences (positive and negative)
- "Follow-up needed" → conditions under which the decision should be revisited

Where this analogy breaks down: a doctor's case notes are about a specific patient's health. ADRs must be written generically enough to be understood by engineers who were not present when the decision was made - requiring more background context than a case note needs.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
An ADR is a short written record explaining why a specific architecture decision was made. It captures the problem, what options were considered, and why this particular option was chosen. It's a note for future engineers that says: "here's why we built it this way."

**Level 2 - How to use it (junior developer):**
Create a `docs/adr/` folder in your repository. Whenever a significant architecture decision is made - choosing a database, selecting a framework, defining a communication pattern - write an ADR using the standard template. Number them sequentially (ADR-001, ADR-002…). Include: title, date, status, context, decision, consequences. Commit it alongside the code changes that implement the decision.

**Level 3 - How it works (mid-level engineer):**
The canonical Nygard ADR template has five sections: **Title** (short noun phrase describing the decision), **Status** (Proposed / Accepted / Deprecated / Superseded), **Context** (forces and constraints that led to this decision - the "why now?"), **Decision** (the chosen response, stated actively: "We will use PostgreSQL"), **Consequences** (what becomes easier, what becomes harder, what is now required). Store as `docs/adr/0001-use-postgresql.md`. Link ADRs to related RFCs, POC results, and spike stories. Review ADRs during architecture reviews to identify any that need updating.

**Level 4 - Why it was designed this way (senior/staff):**
ADRs are a tool for sustainable architecture governance. The alternative - centralised architecture committees approving every decision - creates bottlenecks and disconnects decision authority from implementation knowledge. ADRs enable **federated architecture governance**: teams make their own decisions, record them in ADRs, and architecture reviews audit the quality of the ADR rather than the decision itself. This scales architecture governance as organisation size grows. At staff/principal level, ADRs also serve as the primary mechanism for architectural alignment across teams - shared ADR patterns become the de facto technology standards, more persuasive than mandates because they carry the rationale.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│  ADR LIFECYCLE                                         │
│                                                        │
│  Architecture question identified                      │
│  → Draft ADR (Status: Proposed)                        │
│  → Options analysis added                             │
│  → Review by relevant engineers                        │
│  → Decision made → Status: Accepted                    │
│  → Stored in codebase: docs/adr/NNNN-title.md          │
│  → Linked from relevant code/infrastructure            │
│                                                        │
│  Later: decision revisited                             │
│  → Write new ADR: "ADR-042 supersedes ADR-015"         │
│  → Update ADR-015 status: Superseded by ADR-042        │
│  → Both records preserved; history intact              │
│                                                        │
│  Architecture review:                                  │
│  → Audit: are significant decisions covered by ADRs?   │
│  → Check: are ADRs consistent with current code?       │
└────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Architecture decision point:
  "Should we use gRPC or REST for internal services?"
  → Context documented: team size 8, polyglot services
    [← YOU ARE HERE: ADR being drafted]
  → Options enumerated: REST, gRPC, GraphQL, Thrift
  → Decision made: gRPC (strong typing, streaming support)
  → Consequences recorded: team needs gRPC training
  → ADR accepted, committed: docs/adr/0021-grpc-internal.md
  → Implementation guided by ADR
  → 18 months later: new engineer reads ADR-021,
    understands why gRPC was chosen (not REST),
    makes informed extension decision
```

**FAILURE PATH:**
```
Missing ADR:
  → Team switches from REST to gRPC with no ADR
  → 6 months later: new engineer proposes switching to GraphQL
  → No record of what was evaluated before gRPC was chosen
  → GraphQL debate repeats the original 3-day analysis
  → Or: decision reversed without knowing it was deliberate
  [Cost: repeated analysis + risk of undoing correct decisions]
```

**WHAT CHANGES AT SCALE:**
5 engineers: decisions informal, 5–10 ADRs sufficient. 50 engineers: ADR index required; architectural fitness functions check ADR coverage. 500 engineers: ADR governance process; ADRs linked from API contracts and service docs; architectural patterns library derived from accepted ADRs.

---

### 💻 Code Example

**Example 1 - MADR format ADR:**

```markdown
# ADR-021: Use gRPC for Internal Service Communication

**Date:** 2026-05-06
**Status:** Accepted
**Deciders:** [Architecture Team]
**Supersedes:** ADR-009 (REST for internal services)

## Context and Problem Statement

We have 12 internal microservices communicating
synchronously. REST/JSON has insufficient type safety
across polyglot services (Java, Python, Go). Schema drift
causes integration bugs discovered in production.

## Decision Drivers

* Strong typing requirement (prevent integration bugs)
* Support for streaming (3 services need bidirectional)
* Performance (current REST calls: P99 = 45ms target: 20ms)

## Considered Options

* REST/JSON (current) - weak typing, flexible
* gRPC/Protobuf - strong typing, streaming, binary
* GraphQL - federation support, complex tooling
* Thrift - strong typing, legacy tooling

## Decision Outcome

**Chosen option: gRPC/Protobuf**

Reason: strong typing prevents the schema drift bug class
that caused 3 production incidents in Q1 2026. Streaming
requirement met. P99 in POC: 8ms (vs. REST 45ms).

## Pros and Cons

* ✅ Strong typing via .proto schema
* ✅ P99 8ms (POC-013 validated)
* ❌ Team requires gRPC training (budget allocated)
* ❌ HTTP/2 requirement complicates some service mesh config

## More Information

POC result: docs/poc/poc-013-grpc-performance.md
```

**Example 2 - ADR index (docs/adr/README.md):**

```markdown
# Architecture Decision Records

| # | Title | Status | Date |
|---|-------|--------|------|
| 001 | Use PostgreSQL as primary database | Accepted | 2022-01 |
| 009 | REST for internal services | Superseded | 2023-06 |
| 021 | gRPC for internal services | Accepted | 2026-05 |
| 022 | Redis for caching and sessions | Accepted | 2023-03 |
| 023 | Event-driven async for notifications | Proposed | 2026-05 |
```

---

### ⚖️ Comparison Table

| Format | Sections | Verbosity | Best For |
|---|---|---|---|
| **Nygard ADR** | Title, Status, Context, Decision, Consequences | Minimal | Fast, simple decisions |
| **MADR** | Context, Problem, Options, Decision, Pros/Cons | Medium | Options analysis |
| **Y-Statements** | "In the context of X, facing Y, we decided Z, to achieve Q, accepting P" | Single sentence | Lightweight decisions |
| **RFC** | Full proposal with detailed alternatives | High | Major cross-team decisions |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Once an ADR is accepted, it cannot be changed | ADRs can be superseded by new ADRs. The original is preserved as historical record; the new ADR reflects the updated decision |
| Every decision needs an ADR | ADRs are for significant architectural decisions - choices that are difficult to reverse, that affect multiple teams, or that have long-term implications. Choosing a logging library does not need an ADR |
| ADRs need to be long and formal | The best ADRs are concise. The Nygard format fits on one page. The goal is capturing the "why" - not writing a thesis |
| ADRs are a documentation chore | ADRs are a communication tool that pays dividends at onboarding time, architecture review time, and when decisions need to be revisited. The return is disproportionate to the investment |

---

### 🚨 Failure Modes & Diagnosis

**1. ADR Inflation - ADRs for Trivial Decisions**

**Symptom:** 200 ADRs in the repository. Most are for trivial choices (logging format, test framework version). Engineers stop reading them.

**Root Cause:** No clear guidance on what warrants an ADR. Culture of "document everything" without quality threshold.

**Diagnostic:**
```bash
# Count ADRs; review a random 10%:
ls docs/adr/*.md | wc -l
# If > 3x team size: potential inflation
# Read 5 randomly selected ADRs:
# If trivial decisions documented: threshold too low
```

**Fix:** Define ADR-worthy decisions: "Decisions that are difficult to reverse, affect multiple services or teams, or establish patterns followed by other decisions." Exclude: dependency version choices, naming conventions, tool configurations.

**Prevention:** Include the ADR-worthiness test in team engineering guidelines.

---

**2. Stale ADRs - Code and ADR Diverged**

**Symptom:** ADR-021 says "we use gRPC for internal services" but 6 of 12 services still use REST. The ADR was never updated when the migration stalled.

**Root Cause:** ADR reflects intent, not reality. No process to validate ADRs against actual implementation.

**Diagnostic:**
```bash
# Compare ADR claims against actual code:
# ADR-021 claims gRPC → check proto files exist:
find . -name "*.proto" | wc -l
# find . -name "*Controller.java" | grep -c REST
# Discrepancy = ADR stale
```

**Fix:** Add ADR consistency check to architecture fitness function suite. During quarterly architecture review, verify top-10 ADRs against actual implementation.

**Prevention:** When a migration covered by an ADR stalls, create a new ADR documenting the partial state and revised plan.

---

**3. ADR Not Found - Not Discoverable**

**Symptom:** Engineers write duplicate ADRs because they didn't find the existing one. Or: ADRs exist but aren't referenced from the relevant code, so engineers never discover them when working on related code.

**Root Cause:** ADRs stored in a flat directory with no search, tagging, or cross-referencing to code.

**Diagnostic:**
```bash
# Check: do code comments reference ADRs?
grep -r "ADR-\|adr/" --include="*.java" . | wc -l
# If 0: ADRs not referenced from code
```

**Fix:** Add ADR references to code: `// See ADR-021 for gRPC choice rationale`. Maintain an ADR index with tags. Use Backstage or similar internal developer portal to surface ADRs alongside service docs.

**Prevention:** ADR review checklist includes: "Is this ADR referenced from all relevant code, config, and runbooks?"

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Software Architecture Patterns` - ADRs document decisions about which architectural patterns to use; understanding the pattern landscape is required to write meaningful context and options sections
- `Coupling` - many architecture decisions are trade-offs on coupling; ADRs that capture coupling implications help future engineers understand the full consequence of each choice

**Builds On This (learn these next):**
- `Architecture Review` - the governance process that reviews and approves ADRs; understanding how ADRs feed into architecture reviews contextualises their role in the governance process
- `Technology Roadmap` - ADRs are the granular decision record; the Technology Roadmap is the strategic direction that ADRs implement; together they form the architecture documentation system

**Alternatives / Comparisons:**
- `RFC (Request for Comments)` - a more formal, longer-form alternative to ADRs for major cross-team architectural proposals; RFCs are typically used for decisions requiring broader consensus
- `Technology Roadmap` - sets the strategic direction; ADRs document the specific decisions that implement the roadmap

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Short version-controlled document that    │
│              │ captures one architecture decision with   │
│              │ context, options, and rationale           │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Architecture rationale lost when engineers│
│ SOLVES       │ leave; decisions unmaintainable by fear   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ An ADR's primary audience is the engineer │
│              │ 18 months from now - write for them       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Significant, hard-to-reverse decisions;   │
│              │ cross-team impact; pattern-establishing   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Trivial, easily-reversed decisions with   │
│              │ no impact beyond a single service         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Architecture rationale preserved vs.      │
│              │ discipline required to write consistently │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Write ADRs for your future self - the    │
│              │  one who forgot why this was done."       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Architecture Review → RFC Process →       │
│              │ Technology Roadmap → Fitness Functions    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A team has 80 ADRs accumulated over 3 years. Many are for decisions that have since been reversed or evolved, but the ADR statuses were never updated - they all show "Accepted." A new engineer reads ADR-034 (which says "use MongoDB") but the system actually migrated to PostgreSQL 18 months ago. Design an ADR lifecycle governance process that prevents ADR staleness, including: who is responsible for ADR maintenance, what triggers an ADR review, and how "superseded" ADRs are handled without losing historical context.

**Q2.** Your organisation is considering moving from per-team ADRs (each team maintains their own ADR library) to a centralised ADR system where all teams contribute to a shared repository. Evaluate the trade-offs of both models on: discoverability, consistency, governance overhead, team autonomy, and architectural alignment. What hybrid approach would you recommend for an organisation with 20 teams and 400 engineers?

**Q3.** ADRs are typically written after a decision is made. An alternative approach - "pre-decision ADRs" - proposes writing ADRs as a decision-making tool: write the context and options before the decision is made, circulate for feedback, then record the final decision. Compare "post-decision" vs. "pre-decision" ADRs on: decision quality, stakeholder alignment, team velocity, and long-term documentation value. Under what conditions does each approach deliver more value?

