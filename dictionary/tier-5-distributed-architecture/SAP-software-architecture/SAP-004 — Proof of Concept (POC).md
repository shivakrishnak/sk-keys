---
layout: default
title: "Proof of Concept (POC)"
parent: "Software Architecture Patterns"
nav_order: 4
permalink: /software-architecture/proof-of-concept-poc/
number: "SAP-004"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: Architecture Decision Record (ADR), Architecture Review, Technology Roadmap, SOLID Principles
used_by: Architecture Review, Technology Migration Strategy, Architecture Decision Record (ADR)
related: Architecture Decision Record (ADR), Architecture Review, Spike, Prototype, Technology Migration Strategy
tags:
  - architecture
  - advanced
  - pattern
  - bestpractice
  - mental-model
---

# SAP-004 — Proof of Concept (POC)

⚡ TL;DR — A POC is a time-boxed experiment that validates a specific uncertain architectural assumption before full commitment, producing throwaway code and a documented recommendation.

| #2303 | Category: Software Architecture Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Architecture Decision Record (ADR), Architecture Review, Technology Roadmap, SOLID Principles | |
| **Used by:** | Architecture Review, Technology Migration Strategy, Architecture Decision Record (ADR) | |
| **Related:** | Architecture Decision Record (ADR), Architecture Review, Spike, Prototype, Technology Migration Strategy | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An architecture team commits to a GraphQL federation layer connecting 15 microservices. No team has experience with federation at this scale. After 4 months of implementation: N+1 query problems cause 10× performance degradation under load. The federation resolver model doesn't work with the team's CQRS pattern. Both problems would have been detectable in a 2-week spike. The cost of discovery at month 4: migration rework plus a delayed product launch.

**THE BREAKING POINT:**
Architecture decisions are reversible in theory but extremely expensive in practice once implementation is underway. The "build first, validate later" approach treats the production system as the POC — at production cost and production risk. By the time the wrong assumption surfaces, the team is committed to the wrong direction.

**THE INVENTION MOMENT:**
The POC emerged as a disciplined technique for separating **assumption validation** from **implementation**. The core discipline: identify the most uncertain assumptions in the architecture *before* committing to implementation, then validate those assumptions with the minimum possible investment.

---

### 📘 Textbook Definition

A **Proof of Concept (POC)** in software architecture is a time-boxed investigation — typically 1–2 sprints — that validates a specific high-risk or uncertain architectural assumption before implementation begins. A POC has three defining characteristics: (1) it is **scope-limited** — it tests exactly one assumption, not the full design; (2) it produces **throwaway code** — not production-quality, not shippable; (3) it produces a **documented recommendation** (proceed / pivot / reject) backed by measurable evidence. A POC differs from a Prototype (higher fidelity, demonstrating solution) and a Spike (smaller, story-level time box).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Validate your riskiest architectural assumption in 2 weeks before you build for 6 months in the wrong direction.

**One analogy:**
> Before drilling an oil well, geologists run seismic surveys at significant but bounded cost to validate whether oil reserves are present. They don't drill a £50M well and discover there's no oil at depth 3,000m. The seismic survey is the POC — targeted validation of the critical assumption before the full commitment.

**One insight:**
The discipline is not the experiment itself — it's the question. A POC that answers the wrong question about the right technology is useless. The question must be: "Does [specific technology/pattern] meet [specific measurable requirement] under [specific production-realistic conditions]?"

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. One binary question per POC: "Will this approach work for our specific requirement?"
2. Success criteria are defined before the POC begins — not after results are seen.
3. POC code is explicitly throwaway — the expectation is set at initiation, not at completion.
4. A failed POC (assumption invalidated) is a success — it prevented a larger failure.
5. POC results are documented and linked from the subsequent ADR.

**DERIVED DESIGN:**
From invariant 2: pre-defined success criteria prevent post-hoc rationalisation. If the POC is run, then results are reviewed, and then success criteria are defined to match the results — the POC is meaningless. Success criteria frame: capability (can it do X?), performance (can it do X at Y scale with Z latency?), integration (can it integrate with our existing W system without breaking it?).

From invariant 5: every significant POC should result in an ADR that either cites the POC as evidence for proceeding or documents the pivot decision and its rationale.

**THE TRADE-OFFS:**
**Gain:** Architectural risk de-risked at minimal cost; evidence-based decisions; course-correct cheaply; team builds confidence or surfaces blockers early.
**Cost:** Sprint capacity consumed on throwaway code; risk of POC over-engineering ("productionising the spike"); risk of using POC results to confirm bias rather than challenge assumptions.

---

### 🧪 Thought Experiment

**SETUP:**
Architecture team proposes event sourcing with Axon Framework for a financial transaction system. Core assumption: Axon can replay 5 years of transaction events (50M events) in under 2 hours for historical reporting.

**WHAT HAPPENS WITHOUT POC:**
System built with Axon, event store design, 6 months of implementation. At go-live load test: replay of historical events takes 14 hours. Historical reporting SLA: 2 hours. Complete architectural rethink required post-launch. Customer promises broken.

**WHAT HAPPENS WITH POC:**
Week 1: Axon event store + 50M synthetic events generated. Week 2: replay tested, time measured: 14 hours. Assumption invalidated. Week 3: pivot to CQRS with pre-materialised read models (no full replay). Week 4: POC validates materialised view approach: 4-minute refresh. Architecture decision made with evidence. Implementation begins correctly.

**THE INSIGHT:**
2-week POC prevented a 6-month architectural mistake. The cost of the POC (2 weeks × 1 engineer) was less than 1% of the cost of discovering the same problem post-launch.

---

### 🧠 Mental Model / Analogy

> A POC is like a climber's pilot rope. Before committing to a difficult pitch, the lead climber throws a lightweight rope to test anchor points and route feasibility. If the pilot rope reveals a weak anchor, a different approach is chosen before exposing the full team to risk. The pilot rope is cheap, quick to deploy, and deliberately disposable. But it saves lives.

- "Lead climber" → architect/senior engineer running the POC
- "Pilot rope" → POC code
- "Anchor points" → key assumptions being tested
- "Weak anchor" → invalidated assumption
- "Different approach" → architectural pivot
- "Committing the full team" → full implementation commitment

Where this analogy breaks down: a climber tests physical constraints that are objective. POC assumptions involve technology performance, integration complexity, and team capability — factors with more variability. A POC result is probabilistic, not deterministic — it validates under the tested conditions, not necessarily all production conditions.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A POC is a quick experiment you run before building something big. Instead of spending 6 months building something that might not work, you spend 2 weeks running a small test to check if the key idea is sound. If the test passes, you proceed with confidence. If it fails, you change plans cheaply.

**Level 2 — How to use it (junior developer):**
When planning a significant architecture decision with uncertain elements: (1) Identify the one assumption most likely to invalidate the design if wrong. (2) Write the minimum code to test that assumption. (3) Set a maximum time limit (1–2 sprints). (4) Write down the success criteria before you start. (5) Run it. (6) Document the result and recommendation. (7) Delete or clearly label the code "POC — NOT FOR PRODUCTION."

**Level 3 — How it works (mid-level engineer):**
POC planning follows the ATAM (Architecture Trade-off Analysis Method) influence: identify architectural drivers → identify utility tree (quality attribute scenarios) → identify risks → select highest-risk scenarios as POC targets. A well-structured POC has: a hypothesis ("we believe Kafka can deliver exactly-once at 5k events/second"), a test plan (generate 5k events/second for 60 minutes, measure consumer lag and duplicate rate), measurable criteria (consumer lag < 1,000 messages, 0 duplicates), and a time box (2 sprints). The POC output is a 1-page recommendation: hypothesis, method, result, recommendation, related ADR.

**Level 4 — Why it was designed this way (senior/staff):**
At senior/staff level, POC governance is a risk management discipline. The key design tension: POCs consume sprint capacity that could deliver features. The ROI calculation: `POC cost = N engineer-sprints`. `If assumption wrong, rework cost = M engineer-months`. If M/N > 2 and there is any uncertainty about the assumption, the POC has positive expected value. The failure mode to avoid at this level: "institutionalising POCs" — requiring POCs for decisions that don't have genuine uncertainty. Mandatory POCs for well-understood patterns create overhead without risk reduction. POCs should be triggered by genuine uncertainty, not compliance.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│  POC DECISION & EXECUTION FLOW                         │
│                                                        │
│  Architecture decision identified                      │
│  → Risk register: identify most uncertain assumption   │
│  → Estimate: cost-of-wrong × probability-of-wrong      │
│  → If > POC cost: RUN POC                              │
│                                                        │
│  POC EXECUTION:                                        │
│  [1] Define question + success criteria               │
│  [2] Build minimum code to test assumption            │
│  [3] Time-box: 1–2 sprints only                       │
│  [4] Run experiment                                    │
│  [5] Measure against success criteria                  │
│  [6] Document: question, method, result, recommendation│
│  [7] Create ADR referencing POC                       │
│  [8] Discard POC code (or label clearly)               │
└────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Architecture proposal: event sourcing with Axon
  → Risk register: "Can Axon replay 50M events in 2h?"
    [← YOU ARE HERE: assumption requiring validation]
  → POC defined: replay test with synthetic 50M events
  → Success criteria: replay < 2h, read model up-to-date
  → Sprint 1: Axon + event generator
  → Sprint 2: load test, measure replay time
  → Result: 14h replay — FAILS success criteria
  → Recommendation: REJECT Axon full-replay model
  → ADR-039 created: "pivot to materialised CQRS"
  → New POC: materialised view approach → SUCCESS
  → ADR-040: "materialised view pattern adopted"
  → Implementation begins on validated architecture
```

**FAILURE PATH:**
```
POC code used in production:
  → Spring Boot app created as POC for API design
  → No error handling, no test coverage
  → "It already works" — team skips reimplementation
  → 3 months later: POC-quality code in production
  → Missing error cases cause silent data corruption
  [Never use POC code in production — always rebuild]
```

**WHAT CHANGES AT SCALE:**
1 team: POC documented in a doc, linked from ADR. 10 teams: POC library — a catalogue of previous POC results preventing duplicate work. 100+ teams: POC policy — which assumptions require a POC before architecture approval; automated POC discovery to surface relevant past results.

---

### 💻 Code Example

**Example 1 — POC: GraphQL federation N+1 validation:**

```javascript
// POC — NOT FOR PRODUCTION
// Question: Does Apollo Federation cause N+1 queries
// for our User→Orders relationship at 1,000 req/sec?
// Success: No N+1; response < 100ms P99 at 1k RPS

// Minimal federation setup — no error handling,
// no auth, no logging (by design for POC)
const { ApolloServer } = require('@apollo/server');
const { buildSubgraphSchema } = require(
  '@apollo/subgraph'
);

const typeDefs = `#graphql
  type User @key(fields: "id") {
    id: ID!
    orders: [Order]      # POC tests this resolver
  }
`;

// POC measures: does each User resolver trigger
// a separate Orders DB query?
const resolvers = {
  User: {
    orders: async (user) => {
      // POC instrument: log calls per user
      console.log(`Orders query for user ${user.id}`);
      return ordersDB.findByUserId(user.id);
    },
  },
};
// Record: how many DB queries per 100 users requested?
// If 100 queries: N+1 confirmed -> REJECT federation
// If 1 query (DataLoader batching works): proceed
```

**Example 2 — POC result document:**

```markdown
# POC-007: GraphQL Federation N+1 at Scale

**Question:** Does Apollo Federation cause N+1 DB
queries for User→Orders at 1,000 requests/second?

**Success criteria:** No N+1 at 1k RPS; P99 < 100ms

**Method:** Apollo Gateway + 2 subgraphs (Users, Orders)
Load: 1,000 user-with-orders queries/second, 5 minutes

**Result:**
- Without DataLoader: 1,000 queries per 1,000 requests (N+1)
- With DataLoader: 8 batched queries per 1,000 requests ✓
- P99 with DataLoader: 45ms ✓

**Recommendation:** PROCEED, with mandatory DataLoader
**ADR reference:** ADR-052
**Code:** /poc/poc-007-graphql-federation (DELETE after ADR)
```

---

### ⚖️ Comparison Table

| Activity | Question Type | Code Quality | Time | Output |
|---|---|---|---|---|
| **POC** | "Will this specific approach work?" | Throwaway | 1–2 sprints | Binary recommendation + evidence |
| **Spike** | "How long will this story take?" | Throwaway | 1–3 days | Estimate/approach |
| **Prototype** | "Does this user experience work?" | Low | 1–4 weeks | Demo/mockup |
| **Pilot** | "Does this work in production with real users?" | Production | Weeks | Go/no-go |
| **MVP** | "Is there user demand for this product?" | Production | Weeks–months | Shippable increment |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| POC answers all architecture questions | A POC answers exactly one question. Multiple assumptions require multiple sequential POCs — or accepting that unanswered assumptions carry risk |
| A successful POC means full implementation will also succeed | A POC validates specific conditions. Production may introduce additional variables (scale, failure modes, concurrent users, team skill gaps) not present in the POC |
| POCs are only technical experiments | POCs can validate process assumptions ("can our CI/CD pipeline support this deployment pattern?"), team capability assumptions ("can the team learn Rust in 3 months?"), and integration assumptions ("does vendor X's API support our use case?") |
| POC results require a new tool or framework | Many valuable POCs use existing production systems with modified configuration or synthetic data. The question determines the method — not a preference for novelty |

---

### 🚨 Failure Modes & Diagnosis

**1. Productionising the POC**

**Symptom:** POC code deployed to production unchanged. Production errors appear in code that has no error handling, no monitoring, no test coverage.

**Root Cause:** "It already works" — sunk-cost psychology + delivery pressure. The POC passed the assumption test; the team mistakenly treats it as "the implementation."

**Diagnostic:**
```bash
# Check POC code for production quality markers:
find . -name "poc-*" -newer PRODUCTION_DEPLOY_DATE
# If POC-labelled code appears in production: problem
```

**Fix:** Enforce "POC → reimplementation" as a policy. Treat the POC as a design reference, not a code artefact. Rebuild with production quality, guided by what the POC validated.

**Prevention:** POC code must be labelled `POC — NOT FOR PRODUCTION` in the first file and in the PR title. Production PRs that include POC-labelled code are automatically blocked by CI.

---

**2. Confirmation-Bias POC — Designed to Succeed**

**Symptom:** POC tests technology X, which the tech lead already prefers. Success criteria are written after results are known. POC results always confirm the preferred choice.

**Root Cause:** POC framed as "demonstrate that X works" rather than "determine if X meets requirement." The question is wrong.

**Diagnostic:**
```bash
# Check: were success criteria defined before or after results?
# Review git history of POC design document:
git log --follow -p docs/poc/poc-012.md \
  | grep "success_criteria"
# If success_criteria added after first test run: bias risk
```

**Fix:** POC question, method, and success criteria must be written and committed before any experiment code is run. Peer-reviewed before execution begins.

**Prevention:** POC planning checklist: success criteria defined and reviewed by non-POC team member before code writing begins.

---

**3. Under-Scoped POC — Production Conditions Not Tested**

**Symptom:** POC validates technology X at 100 concurrent users. Production requires 10,000 concurrent users. POC result: proceed. Production: catastrophic performance failure.

**Root Cause:** POC tested simplified conditions that do not represent production constraints.

**Diagnostic:**
```bash
# Compare POC test conditions vs. production SLAs:
cat docs/poc/poc-012.md | grep -A3 "method:\|conditions:"
# Verify: does POC data volume/concurrency match
# production estimates?
```

**Fix:** Re-run POC at realistic scale with realistic data volumes and concurrent user patterns from production projections.

**Prevention:** POC method must explicitly state: "the test conditions represent estimated production scale." Reviewed by the team that owns production SLAs.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Architecture Decision Record (ADR)` — POC results are the primary evidence cited in ADRs; the POC validates the assumption, the ADR records the decision
- `Architecture Review` — the governance process that identifies which assumptions require a POC before architecture decisions are approved

**Builds On This (learn these next):**
- `Technology Migration Strategy` — POCs are used at the start of migration programmes to validate the target architecture before committing to the migration
- `Architecture Review` — the review process that evaluates POC results as part of proposal assessment

**Alternatives / Comparisons:**
- `Spike` — the agile story-level equivalent: a shorter, narrower time-boxed investigation for story-level uncertainty rather than architectural uncertainty
- `Prototype` — emphasises demonstrating solutions (often for UX validation) rather than testing technical assumptions; higher quality and not always throwaway

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Time-boxed experiment validating one      │
│              │ high-risk architectural assumption before  │
│              │ full implementation commitment            │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Architecture assumptions discovered wrong │
│ SOLVES       │ after months of implementation investment  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Define question AND success criteria      │
│              │ before writing any POC code               │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Architecture involves uncertain technology,│
│              │ scale assumptions, or novel integrations  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Assumption is already well-validated by   │
│              │ evidence or team production experience    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ 2-sprint investment de-risks 6-month      │
│              │ commitment; risk: over-engineering the    │
│              │ POC or using POC code in production       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Build the smallest possible experiment   │
│              │  to answer the most important question."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ADR → Architecture Review → Spike →       │
│              │ Technology Migration Strategy             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A team runs a POC to test whether Apache Kafka can sustain 50,000 events per second on their infrastructure. The POC runs for 30 minutes with synthetic load and meets the target. They proceed with full implementation. In production, after 72 hours of sustained 50,000 events/second, Kafka consumer lag grows exponentially and never recovers. What did the 30-minute POC fail to test, and what POC design change would have detected this production failure mode?

**Q2.** An organisation's architecture review board requires a POC for all proposals involving unfamiliar technology. An architect proposes adding a Redis cache layer (well-understood technology). The ARB mandates a POC anyway, citing "policy." Make the case for either: (A) the POC is justified and what it should specifically test for Redis, or (B) the POC requirement should be waived and under what governance conditions the waiver is appropriate.

**Q3.** A POC validates that Technology A meets all technical requirements. However, Technology A is produced by a company with recent financial instability, and only one engineer on the team has experience with it. The technical POC passed. Should the architecture decision proceed with Technology A? Design a decision framework that incorporates non-technical risk factors (vendor stability, team capability, long-term supportability) alongside technical POC evidence into the final architecture decision.

