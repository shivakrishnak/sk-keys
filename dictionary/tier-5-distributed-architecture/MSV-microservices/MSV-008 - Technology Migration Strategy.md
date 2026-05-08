---
layout: default
title: "Technology Migration Strategy"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 8
permalink: /microservices/technology-migration-strategy/
id: MSV-008
category: Microservices
difficulty: ★★★
depends_on: On-Premises to Cloud Migration, Re-platforming vs Re-architecting, Strangler Fig, Proof of Concept (POC) in Architecture
used_by: Monolith to Microservices Migration, Re-platforming vs Re-architecting
related: Re-platforming vs Re-architecting, On-Premises to Cloud Migration, Architecture Decision Record (ADR), Proof of Concept (POC) in Architecture
tags:
  - architecture
  - advanced
  - microservices
  - pattern
  - bestpractice
  - tradeoff
---

# MSV-008 - Technology Migration Strategy

⚡ TL;DR - A technology migration strategy defines how an organisation moves from legacy to target architecture: scope, phasing, risk management, rollback, and success criteria.

| #2282 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | On-Premises to Cloud Migration, Re-platforming vs Re-architecting, Strangler Fig, Proof of Concept (POC) in Architecture | |
| **Used by:** | Monolith to Microservices Migration, Re-platforming vs Re-architecting | |
| **Related:** | Re-platforming vs Re-architecting, On-Premises to Cloud Migration, Architecture Decision Record (ADR), Proof of Concept (POC) in Architecture | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An organisation decides to migrate from a legacy monolith to microservices. Each team interprets the goal differently. Team A migrates their module to AWS. Team B redesigns APIs with a new versioning scheme. Team C rewrites the shared database schema. No unified plan exists for ordering, dependencies, or rollback. Six months in: three half-migrated modules, two broken integrations, one production incident. "The migration" has become a synonym for chaos.

**THE BREAKING POINT:**
Technology migrations without a coherent strategy become irreversible mid-state - the organisation is stuck between the old system (partially broken) and the new system (partially built). Neither can be fully operated. The cost of the broken intermediate state often exceeds the original problem's cost.

**THE INVENTION MOMENT:**
The discipline of Technology Migration Strategy emerged to prevent uncoordinated migrations. It provides a structured framework: define the current state, define the target state, identify migration paths, phase the work, manage dependencies, define rollback triggers, and measure progress with explicit success criteria.

---

### 📘 Textbook Definition

A **Technology Migration Strategy** is a structured plan for transitioning an organisation's technology stack, architecture, or platform from a current state (legacy system, on-premises infrastructure, monolithic codebase) to a target state (cloud-native, microservices, modernised platform). The strategy defines: migration scope (what moves), migration approach (Strangler Fig, Big Bang, parallel run), phasing (wave planning), risk management (rollback triggers), stakeholder communication, success metrics, and the governance model for executing migration work in parallel with normal product development.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A migration strategy answers: what moves, in what order, at what risk, with what rollback plan, and how you'll know it succeeded.

**One analogy:**
> A military campaign plan. The objective is clear (capture the city), but the plan defines: which units move first (phasing), what the communication lines are (dependencies), what triggers a retreat (rollback criteria), what intelligence is needed before advancing (POC/spike), and how "mission accomplished" is assessed. Technology migration without strategy is charging without a plan - occasionally works, usually catastrophic.

**One insight:**
The most critical element of a migration strategy is the rollback plan. A migration that cannot be reversed is a bet with no hedge. Defining rollback triggers before starting forces clarity on risk tolerance and acceptable intermediate states.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The current system must remain functional throughout the migration - no "black hole" transition states.
2. Migrations must be decomposed into independently reversible increments.
3. Risk is proportional to scope per increment - smaller increments mean smaller blast radius.
4. Success criteria must be defined before the migration begins - not after.
5. Dependencies between migration increments must be explicitly mapped and sequenced.

**DERIVED DESIGN:**
From invariant 2: every migration increment requires a defined rollback procedure. If increment N cannot be reversed without reversing increments N-1 through N-5, the increments are not independent - they must be merged or re-sequenced.

From invariant 5: dependency mapping reveals the critical path. The critical path determines the minimum migration timeline and identifies which increments block others. Parallel migration work is only possible on non-dependent paths.

**THE TRADE-OFFS:**
**Gain:** Controlled risk; clear progress metrics; stakeholder confidence; rollback capability; sustained product development alongside migration.
**Cost:** Migration planning requires upfront investment before any code is written; wave phasing creates intermediate states that require operating two systems simultaneously; dependencies constrain parallelism.

---

### 🧪 Thought Experiment

**SETUP:**
Two teams migrating the same legacy CRM system to cloud microservices. Team A has a migration strategy. Team B does not.

**WHAT HAPPENS without Migration Strategy (Team B):**
Developers start with the "most interesting" modules. Three engineers rewrite the reporting engine. Two engineers migrate the user auth. No one owns the shared database migration. After 4 months: reporting is done but cannot be deployed because auth migration broke the shared DB schema. Both are stuck. Product feature development has stopped entirely. Estimate to complete: unknown.

**WHAT HAPPENS with Migration Strategy (Team A):**
Phase 1: Auth service extracted (week 1–6). Rollback: revert routing rule. Phase 2: User profile service extracted using Auth. Phase 3: Reporting service extracted using both. Database migration happens within each phase. Product development receives 20% of capacity throughout. Month 6: 3 services in production, monolith handles only legacy admin panel.

**THE INSIGHT:**
The critical variable is not the speed of individual migration work but the sequencing of dependencies. A migration strategy that maps dependencies correctly can complete faster than an uncoordinated migration that starts faster but stalls.

---

### 🧠 Mental Model / Analogy

> A migration strategy is like the choreography for a stage production with live actors performing while the set is changed around them. The set changes (migration increments) are scheduled between acts. Each set change has a clear "this scene must end before we can swap" dependency. Actors (users) experience an unbroken show. The stage manager (migration lead) coordinates everything so the next act can begin exactly when the previous ends - never leaving a partially configured stage visible to the audience.

- "Actors performing" → production system serving users continuously
- "Set changes between acts" → migration increments executed one at a time
- "Scene dependencies" → migration increment ordering constraints
- "Stage manager" → migration lead / architect
- "Audience sees unbroken show" → users experience no service degradation

Where this analogy breaks down: a theatre production's set changes are time-bounded rehearsals. Technology migrations often encounter unexpected complexity that extends planned phases - a real-world migration strategy must include explicit scope change management procedures.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A technology migration strategy is the overall game plan for changing your company's technology without breaking what currently works. It answers: what changes first, what changes last, what happens if something goes wrong, and how you'll know when you're done.

**Level 2 - How to use it (junior developer):**
Define: current state → target state. Decompose into milestones. For each milestone: define scope, define pre-conditions (what must be true before starting), define rollback procedure, define success criteria. Sequence milestones by dependency order. Assign ownership per milestone. Define the % of team capacity spent on migration vs. product features.

**Level 3 - How it works (mid-level engineer):**
A migration strategy document contains five components: (1) **Portfolio analysis** - current systems catalogued by migration R (Rehost, Replatform, Re-architect, Retire). (2) **Wave plan** - batches of applications migrated together, sized to fit available capacity and acceptable risk. (3) **Dependency map** - directed graph of migration increment prerequisites. (4) **Risk register** - top risks (data loss, service downtime, integration failure) with mitigation and rollback triggers. (5) **Progress tracking** - weekly metrics (applications migrated, rollback incidents, integration test coverage). ADRs (Architecture Decision Records) document key decisions made during migration.

**Level 4 - Why it was designed this way (senior/staff):**
Technology migrations are the highest-risk class of engineering work because they involve changing foundational systems under production load. The migration strategy framework exists to transform migration from a "project" into a "process" - a sustained, continuous improvement programme with bounded risk per increment. The key insight at this level: the governance model matters as much as the technical plan. Who has the authority to delay a wave? Who approves rollback? Who owns migration velocity vs. feature velocity trade-offs? These decisions, made explicit upfront, prevent the political paralysis that kills more migrations than technical problems do.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│  MIGRATION STRATEGY FRAMEWORK                          │
│                                                        │
│  1. ASSESS          Current → Target state mapping     │
│     Portfolio analysis: 6Rs per application            │
│                                                        │
│  2. PLAN            Wave planning + dependency map     │
│     Wave 1: [App A, App B] (no dependencies)           │
│     Wave 2: [App C] (depends on Wave 1 complete)       │
│     Wave 3: [App D, App E, App F]                      │
│                                                        │
│  3. EXECUTE         Increment by increment             │
│     Per increment: spike → build → test → cutover      │
│     Parallel: 20% capacity for migration, 80% product  │
│                                                        │
│  4. VALIDATE        Success criteria per wave          │
│     Metrics: latency, error rate, cost, team velocity  │
│                                                        │
│  5. OPTIMISE        Post-wave retrospective            │
│     Adjust next wave based on learnings               │
└────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Migration programme kick-off:
  → Portfolio assessment: 200 apps categorised by 6R
    [← YOU ARE HERE: strategy definition phase]
  → Wave 1 planned: 30 Rehost candidates (low risk)
  → Wave 1 executed: 30 apps rehosted in 3 months
  → Wave 1 validated: cost ✓, latency ✓, errors ✓
  → Wave 2 planned: 50 Replatform candidates
  → Wave 2 execution: managed services + containerisation
  → Continue until target state achieved
```

**FAILURE PATH:**
```
Wave 3 (Re-architect) stalls:
  → Scope creep: team redesigning unrelated modules
  → Rollback trigger hit: error rate > 0.5% on new service
  → Rollback executed: route traffic back to monolith
  → Post-mortem: insufficient load testing pre-cutover
  → Strategy update: add load testing gate to runbook
  → Wave 3 restarted with updated runbook
```

**WHAT CHANGES AT SCALE:**
5 applications: informal migration plan in a doc. 50 applications: dedicated migration workstream, wave plan, ADRs. 500 applications: migration programme office, automated portfolio tracking (Apptio/ServiceNow), governance board, dedicated migration engineers. Success metric at scale: number of applications decommissioned per quarter.

---

### 💻 Code Example

**Example 1 - Migration dependency map (Mermaid diagram):**

```
graph TD
  A[Auth Service Migration] --> B[User Service Migration]
  A --> C[Session Migration]
  B --> D[Orders Service Migration]
  C --> D
  D --> E[Reporting Service Migration]
  F[Infrastructure Setup] --> A
  F --> G[Catalog Service Migration]
  G --> D
```

**Example 2 - Wave plan template (YAML):**

```yaml
# migration-wave-plan.yaml
programme: legacy-to-cloud
waves:
  - wave: 1
    objective: "Rehost stateless web apps, exit DC1"
    capacity_pct: 30     # 30% team capacity on migration
    applications:
      - name: portal-web
        strategy: rehost
        dependencies: []
        rollback_trigger: "error_rate > 1% for 5 min"
        success_criteria:
          - latency_p99_ms: 200
          - cost_usd_monthly: 500
    duration_weeks: 6

  - wave: 2
    objective: "Replatform databases to managed RDS"
    capacity_pct: 25
    applications:
      - name: orders-db
        strategy: replatform
        dependencies:
          - wave: 1
            name: portal-web   # must complete first
        rollback_trigger: "replication_lag_sec > 30"
        success_criteria:
          - availability_pct: 99.9
    duration_weeks: 8
```

**Example 3 - Migration metrics dashboard query (SQL):**

```sql
-- Track migration progress per wave
SELECT
  wave_number,
  COUNT(CASE WHEN status = 'migrated' THEN 1 END)
    AS apps_migrated,
  COUNT(CASE WHEN status = 'in_progress' THEN 1 END)
    AS apps_in_progress,
  COUNT(CASE WHEN status = 'blocked' THEN 1 END)
    AS apps_blocked,
  COUNT(*) AS apps_total,
  ROUND(
    100.0 * COUNT(CASE WHEN status = 'migrated' THEN 1 END)
    / COUNT(*), 1
  ) AS completion_pct
FROM migration_portfolio
GROUP BY wave_number
ORDER BY wave_number;
```

---

### ⚖️ Comparison Table

| Approach | Risk | Speed | Reversibility | Best For |
|---|---|---|---|---|
| **Strangler Fig (incremental)** | Low | Slow | High | Live production systems |
| **Big Bang** | Very high | Fast | None | Greenfield / small systems only |
| **Parallel Run** | Medium | Medium | High | High-risk, regulatory-sensitive migrations |
| **Wave Migration** | Low-Medium | Moderate | Medium | Large portfolios (50+ apps) |
| **No Strategy (ad hoc)** | Very high | Variable | None | Never recommended |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| A migration strategy is a one-time document | Migration strategies require continuous updates as waves complete, risks materialise, and business priorities change. A static strategy becomes incorrect within weeks |
| The fastest migration is the best migration | Migration speed without rollback capability is a liability. A migration strategy optimises for controlled risk, not speed - though speed matters where hardware refresh or contractual deadlines create urgency |
| Developers can migrate while delivering full product velocity | Migration work consumes 20–40% of team capacity. Stakeholders must accept reduced product feature delivery during migration - this is a business decision, not an engineering decision |
| Success = 100% of apps migrated | Success is when the target state delivers the expected business outcomes (cost reduction, scaling, velocity). Sometimes 80% migration achieving 100% of the business goals is the right success criteria |

---

### 🚨 Failure Modes & Diagnosis

**1. Scope Creep - Migration Expands Uncontrollably**

**Symptom:** Originally 50-app migration grows to 200 apps. Timeline has tripled. No clear completion date.

**Root Cause:** No migration scope governance. Teams adding "while we're at it" work items. No change control process.

**Diagnostic:**
```bash
# Count migration tickets vs. original scope:
jira-cli issue list \
  --project MIGRATION \
  --jql "labels = migration-scope" \
  | wc -l
# Compare to original planned scope: N tickets
# Delta > 20%: scope creep in progress
```

**Fix:** Freeze migration scope per wave. Any additions require explicit governance approval (migration architect + product owner). New scope enters the backlog for a future wave.

**Prevention:** Define explicit wave scope in a signed-off document before wave execution begins. Any scope changes to a live wave require written change request.

---

**2. Missing Rollback - Stuck in Broken State**

**Symptom:** Migration increment fails in production. Teams cannot roll back because the rollback procedure was never defined.

**Root Cause:** Rollback procedures treated as secondary concern. "We'll figure it out if we need to."

**Diagnostic:**
```bash
# Check migration runbook for rollback section:
grep -c "rollback" migration-runbook.md
# If 0: no rollback procedure defined
```

**Fix:** Immediately define rollback procedures for all in-flight increments. Execute rollback drill in staging before production cutover.

**Prevention:** Gate cutover approval on: rollback procedure documented + rollback tested in staging within 72 hours of cutover.

---

**3. Integration Breakage - Dependencies Not Mapped**

**Symptom:** After migrating Service A, Service B starts failing with connection errors. Service B's dependency on Service A was not captured in the migration plan.

**Root Cause:** Dependency discovery was done by team self-reporting rather than automated discovery. Service B's team was not involved in the migration planning.

**Diagnostic:**
```bash
# Discover actual service dependencies via network traces:
kubectl exec -n monitoring \
  deployment/kiali -- \
  curl localhost:20001/api/graph?namespaces=prod
# Graph reveals undocumented service dependencies
```

**Fix:** Use automated dependency discovery (AWS Application Discovery Service, Kiali, network flow analysis) rather than self-reporting. Pause migration of Service A until Service B's migration plan is updated.

**Prevention:** Mandatory automated dependency scan as Wave planning gate. No wave begins without dependency map validated by discovery tooling.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `On-Premises to Cloud Migration` - the most common technology migration use case; the 6Rs framework and wave planning concepts are introduced there
- `Strangler Fig Pattern` - the primary technical execution pattern for incremental migration; the migration strategy orchestrates multiple Strangler Fig extractions

**Builds On This (learn these next):**
- `Architecture Decision Record (ADR)` - the documentation mechanism for recording key migration decisions; ADRs created during migration form a historical record of architectural evolution
- `Re-platforming vs Re-architecting` - the detailed per-application strategy selection decision; migration strategy at program scope orchestrates many individual re-platform/re-architect decisions

**Alternatives / Comparisons:**
- `Re-platforming vs Re-architecting` - the per-application decision; technology migration strategy is the programme-level orchestration of many such decisions
- `Proof of Concept (POC) in Architecture` - often used at the start of a technology migration strategy to validate the target architecture before committing to full migration

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ A structured plan for moving from legacy  │
│              │ to target architecture with phasing,      │
│              │ risk management, and rollback             │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Uncoordinated migrations create broken    │
│ SOLVES       │ intermediate states, stalled projects,    │
│              │ and production incidents                  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Define rollback triggers before starting; │
│              │ scope, sequence, and measure each wave   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any significant technology Platform or    │
│              │ architecture change affecting production  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Greenfield projects (no migration needed) │
│              │ or trivial library upgrades              │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Controlled risk + rollback capability vs. │
│              │ planning overhead and extended timeline   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Know what moves, in what order, with     │
│              │  what rollback - before the first commit."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ADR → Strangler Fig → Re-platforming vs   │
│              │ Re-architecting → Wave Planning           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A 200-app migration has been underway for 18 months. 80 apps are migrated, 120 remain. A new CTO is appointed who wants to accelerate - proposing increasing migration capacity from 30% to 80% of all engineering teams. Evaluate the risks of this acceleration. What happens to product feature delivery, team morale, and migration quality? What is the right capacity model, and how would you negotiate it with the CTO?

**Q2.** Your migration strategy specifies a rollback trigger of "P99 latency > 500ms for 5 consecutive minutes on the new service." During Wave 3 execution, the new service hits P99 = 480ms - below the trigger. Teams argue over whether to roll back or continue. What governance process prevents this ambiguity? How do you set rollback triggers that are unambiguous, and who has authority to override a trigger?

**Q3.** Compare two migration governance models: (A) centralised migration programme office with a chief architect approving all migration decisions, (B) federated model where each team owns their migration with loose coordination via shared standards. For an organisation of 500 engineers and 300 applications, evaluate both models on: decision speed, standards consistency, team autonomy, risk management, and scalability.

