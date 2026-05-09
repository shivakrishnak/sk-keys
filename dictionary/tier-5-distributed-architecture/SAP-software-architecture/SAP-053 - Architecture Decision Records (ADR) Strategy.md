---
id: SAP-053
title: Architecture Decision Records (ADR) Strategy
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★★
depends_on: SAP-006, SAP-002, SAP-004
used_by: SAP-054, SAP-057, SAP-062
related: SAP-006, SAP-008, SAP-056
tags:
  - architecture
  - advanced
  - bestpractice
  - documentation
  - governance
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 53
permalink: /software-architecture/adr-strategy/
---

# SAP-053 - Architecture Decision Records (ADR) Strategy

⚡ TL;DR - An ADR strategy defines how a team consistently captures, reviews, evolves, and leverages architectural decisions as organisational knowledge rather than individual memory.

| SAP-053 | Category: Software Architecture Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | SAP-006, SAP-002, SAP-004 | |
| **Used by:** | SAP-054, SAP-057, SAP-062 | |
| **Related:** | SAP-006, SAP-008, SAP-056 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team writes individual ADRs but they are inconsistent in format, scattered across wikis and repos, frequently out of date, and never referenced when making new decisions. The ADR practice exists nominally but provides no actual value beyond compliance theatre.

**THE BREAKING POINT:**
Two years after a critical architectural decision was made, the original decision-maker leaves. The ADR exists but lacks the context of what alternatives were rejected and why. A new engineer, unaware of the constraints, proposes re-adopting the rejected alternative. The team spends two weeks re-litigating the same debate without reaching the same quality of decision, because the historical reasoning is lost.

**THE INVENTION MOMENT:**
Building on Michael Nygard's 2011 ADR format and subsequent work by Nat Pryce and others, teams gradually recognised that the format was only a third of the solution. The other two thirds were: a consistent strategy for when to write ADRs, and a process for maintaining and referencing them as living artefacts.

**EVOLUTION:**
ADR strategy has evolved from "we write ADRs in Markdown in our repo" to a multi-dimensional practice that includes decision classification, lightweight review ceremonies, superseding and deprecating old decisions, linking ADRs to fitness functions, and integrating ADRs into onboarding materials.

---

### 📘 Textbook Definition

An **ADR strategy** is the team's or organisation's systematic approach to: (1) classifying which decisions warrant ADRs, (2) defining a consistent ADR format, (3) governing the ADR lifecycle (draft → accepted → superseded → deprecated), (4) making ADRs discoverable and searchable, and (5) regularly reviewing ADRs for accuracy and relevance.

---

### ⏱️ Understand It in 30 Seconds

**One line:** An ADR strategy turns individual decision documents into an organisational knowledge system.

> Think of ADRs like building permits. A single permit documents one construction decision. A permit registry with consistent formats, superseding records, and annual audits is a building safety system. The individual permit is necessary but not sufficient - the registry strategy is what makes it valuable.

**One insight:** An ADR strategy is not about writing more documentation - it is about building a searchable, current, organisationally navigable memory of architectural reasoning.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. An ADR is valuable only if it is read. Unread ADRs are overhead, not knowledge.
2. An ADR's value is in its context (why the decision was made, what was rejected and why) - not just the decision itself.
3. ADRs must be maintained: a deprecated ADR that still appears as current is worse than no ADR (it misleads).
4. ADR strategy must be proportional: heavyweight process for architectural decisions, not for all decisions.

**DERIVED DESIGN:**
The strategy must address: classification (which decisions), format (what to capture), lifecycle (draft → accepted → superseded), location (where to store), discovery (how to find), and review (how to audit).

**THE TRADE-OFFS:**
**Gain:** Long-lived organisational memory. Faster onboarding. Reduced decision re-litigation. Foundation for architecture governance.
**Cost:** Initial investment in process design. Maintenance overhead. Risk of compliance theatre if not embedded in team culture.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Decisions have context that must be preserved and context decays. Preserving it requires intentional process.
**Accidental:** Complex ADR formats with 15 fields that nobody fills in. Tools that require sign-off workflows for trivial decisions.

---

### 🧪 Thought Experiment

**SETUP:** Two companies have the same nominal ADR practice ("we document architectural decisions"). Company A uses a consistent strategy. Company B uses ad-hoc individual ADRs.

**WHAT HAPPENS WITHOUT THE STRATEGY (Company B):** After 3 years, the ADR folder has 47 documents in 4 different formats. Some reference technologies that no longer exist. New engineers see 3 conflicting ADRs about the same decision area. There is no canonical answer. The ADRs create confusion rather than reducing it.

**WHAT HAPPENS WITH THE STRATEGY (Company A):** After 3 years, ADRs are in a single consistent format. Superseded ADRs are marked and link to the replacement. A quarterly ADR review removes outdated entries. New engineers are assigned the 10 "foundational ADRs" as onboarding reading. Architecture reviews reference ADRs explicitly. The ADRs have become the narrative of the system's evolution.

**THE INSIGHT:** The value of ADRs is not proportional to the number written - it is proportional to the quality of the strategy governing them.

---

### 🧠 Mental Model / Analogy

> Think of ADRs as case law in a legal system. Individual court rulings exist (individual ADRs). But the legal system's value comes from a consistent structure (format strategy), a hierarchy of authority (classification - which ADRs are binding), references to precedent (linking related ADRs), and formal superseding (overturning old rulings). Without the system, individual rulings are just opinions.

- **Individual court ruling** = individual ADR
- **Consistent legal format** = ADR template strategy
- **Hierarchy of precedent** = ADR classification by architectural significance
- **Overturning a ruling** = superseding an ADR with a new one
- **Legal research** = ADR discovery and search

Where this analogy breaks down: legal systems are adversarial; ADR strategies are collaborative. Also, legal systems have external enforcement; ADR strategies require cultural buy-in.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
An ADR strategy is the system that makes architectural notes useful: a consistent format, a place to store them, a process to keep them current, and a habit of referencing them.

**Level 2 - How to use it (junior developer):**
When you join a team with an ADR strategy, read the foundational ADRs first. When you make an architectural decision (or are part of making one), follow the team's ADR template. Reference existing ADRs when they are relevant to your change. Ping the team if you find an ADR that appears outdated.

**Level 3 - How it works (mid-level engineer):**
An ADR strategy has six components: (1) a classification trigger ("when do we write an ADR?"), (2) a standard template, (3) a lifecycle model (draft, proposed, accepted, superseded, deprecated), (4) a canonical storage location (usually /docs/decisions/ in the repo), (5) a discovery mechanism (searchable, tagged), and (6) a review cadence (quarterly or after major changes).

**Level 4 - Why it was designed this way (senior/staff):**
ADR strategy is architecture governance made lightweight. Heavy governance (architecture review boards, mandatory sign-offs) creates bottlenecks. Light governance (no process) creates decision amnesia. ADR strategy is the minimum viable governance that preserves reasoning, enables re-use of prior analysis, and creates a shared architectural vocabulary without blocking delivery. In organisations with multiple teams, a federated ADR strategy (team-level ADRs + org-level ADRs) is necessary to balance local autonomy with global consistency.

**Expert Thinking Cues:**
- An ADR strategy must survive leadership turnover. If it depends on one person to work, it is fragile.
- The hardest part is not format - it is the review discipline. Any ADR strategy without a review cadence will decay.
- ADRs should be linked to fitness functions wherever possible, turning narrative ("we chose X for Y reason") into executable specifications.

---

### ⚙️ How It Works (Mechanism)

**The six components of an ADR strategy:**

**1. Classification trigger**
Define the heuristic: when does a decision require an ADR? A simple 2x2: high blast radius + high reversal cost = ADR required. Medium blast radius or reversal cost = ADR recommended. Low on both = no ADR needed.

**2. Standard template**
Use Michael Nygard's format as the base: `# ADR-NNN: Title`, `## Status`, `## Context`, `## Decision`, `## Consequences`. Add `## Alternatives Considered` and `## Rejected Options` for high-stakes decisions. Keep it under 2 pages.

**3. Lifecycle model**
States: `Draft` (being written) → `Proposed` (under review) → `Accepted` (in force) → `Superseded` by ADR-XXX → `Deprecated` (no longer applicable). Each transition has a clear trigger.

**4. Canonical storage**
Store in version control alongside code: `/docs/decisions/ADR-NNN-title.md`. Proximity to code ensures decisions version with implementation changes.

**5. Discovery mechanism**
A readable index in `/docs/decisions/README.md` with ID, title, status, and one-line summary. Tag ADRs by domain (`data`, `security`, `structuring`) for filtered discovery.

**6. Review cadence**
Quarterly review: scan all `Accepted` ADRs. Mark stale ones for update. Supersede ones invalidated by new decisions. Link new fitness functions where relevant.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Decision trigger (new requirement, incident,
  architecture review finding)
          |
          v
Classify: is this ADR-worthy?
  (blast radius x reversal cost matrix)
          |
       Yes|  No
          |     \
          v      v
  Draft ADR     Proceed
  template      directly
          |
          v
Propose for team review           <- YOU ARE HERE
          |
          v
Accept or Reject with reasoning
          |
          v
Implement + link fitness function
          |
          v
Review quarterly, supersede when
  decision changes
```

**FAILURE PATH:**
ADRs written but never referenced. New decisions made without checking existing ADRs. 18 months later, a new ADR contradicts an existing one. Nobody notices. The system evolves inconsistently.

**WHAT CHANGES AT SCALE:**
At small scale (1 team), a single ADR folder with a shared template is sufficient. At large scale (multiple teams), a federated model is required: team ADRs in team repos + org-level ADRs in a central architecture repo. Cross-team decisions go through the organisation-level ADR process.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
In distributed team contexts, the ADR strategy must address decision authority: who can approve an ADR that affects multiple teams? A clear RACI model (who is Responsible, Accountable, Consulted, Informed) for each ADR classification level prevents decision gridlock.

---

### 💻 Code Example

**ADR template - standard format:**

**BAD - unstructured narrative (hard to scan and supersede):**
```markdown
# Why we use PostgreSQL

We discussed the database options and decided on PostgreSQL.
It seemed like the best choice for our use case. Redis was
also considered but we didn't go with it.
```

**GOOD - structured ADR (complete context, discoverable, supersedeable):**
```markdown
# ADR-012: Primary Database - PostgreSQL

## Status
Accepted (2025-03-15)

## Context
We need a primary persistence store for the order management
service. Requirements:
- ACID transactions (order + payment atomicity)
- Complex relational queries (reporting)
- 10,000 writes/day, 100,000 reads/day (current)
- Team has strong SQL expertise

## Decision
Use PostgreSQL as the primary database.

## Alternatives Considered
- **MongoDB**: Rejected. Flexible schema not needed; ACID
  requirements favour relational model.
- **MySQL**: Considered. PostgreSQL chosen for richer JSON
  support and better window function performance.

## Consequences
- Positive: Strong consistency, mature tooling, team fluency.
- Negative: Vertical scaling ceiling; horizontal sharding
  complex if writes exceed 50,000/day.
- If writes exceed threshold: revisit with ADR-XXX.

## Related
- Fitness function: DB integration test suite in CI
- See also: ADR-008 (Data Ownership Strategy)
```

**How to test / verify correctness:**
- Run `grep -r "Accepted" docs/decisions/` to list active ADRs.
- Quarterly review script flags any `Accepted` ADR older than 18 months without a review date.

---

### ⚖️ Comparison Table

| ADR Approach | Pros | Cons | Best For |
|---|---|---|---|
| Ad-hoc individual ADRs | No overhead | Inconsistent, no lifecycle | Solo projects |
| Stratified ADR strategy | Consistent, discoverable | Setup investment | Teams of 3+ |
| Federated org + team ADRs | Team autonomy + consistency | More coordination | Multi-team orgs |
| RFC process (no ADRs) | Broader input | Heavy overhead | Public APIs |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "More ADRs = better architecture governance" | More ADRs with no review strategy = more noise. Quality, currency, and discoverability matter more than volume. |
| "ADRs are only for big decisions" | The classification strategy defines scope. Many medium decisions benefit from a 1-page ADR. The strategy defines the threshold, not a bias toward volume or minimalism. |
| "Once accepted, ADRs never change" | ADRs have a lifecycle. Superseding and deprecating are as important as writing. A strategy without lifecycle management decays into misinformation. |
| "ADRs replace architecture documentation" | ADRs document decisions and reasoning. They complement (not replace) system context diagrams, sequence diagrams, and living architecture documents. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: ADR Decay**
**Symptom:** ADRs exist but describe the system as it was 2 years ago, not as it is today.
**Root Cause:** No review cadence. ADRs accepted and forgotten.
**Diagnostic:**
```bash
# Find ADRs not reviewed in 18 months (check git log)
git log --since="18 months ago" -- docs/decisions/ \
  | grep "ADR" | sort | uniq -c | sort -rn
# ADRs with 0 commits in 18 months are candidates for review
```
**Fix:** Run a one-time ADR audit. Mark stale ones. Supersede or deprecate.
**Prevention:** Add quarterly ADR review to engineering calendar.

**Failure Mode 2: ADR Islands**
**Symptom:** ADRs exist in 4 different places (Confluence, repo, Google Docs, Notion). Nobody knows which is canonical.
**Root Cause:** No canonical storage decision was made (ironic for an ADR strategy).
**Diagnostic:**
```bash
find . -name "ADR*" -o -name "adr*" 2>/dev/null
# Multiple locations found = fragmented
```
**Fix:** Consolidate to git repo `/docs/decisions/`. Update index. Delete duplicates.
**Prevention:** The ADR strategy itself is an ADR. Document the storage decision formally.

**Failure Mode 3: Compliance Theatre**
**Symptom:** ADRs are written as a post-hoc justification for already-made decisions, not as deliberative tools.
**Root Cause:** ADR process required by mandate but not culturally valued.
**Fix:** Make ADR drafting part of the decision process (pre-decision), not a documentation step (post-decision). Demonstrate value: use ADRs in retrospectives to show how recorded context prevented re-litigation.
**Prevention:** Measure discoverability and reference rate, not ADR count.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- SAP-006 - Architecture Decision Record (ADR)
- SAP-002 - Why Architecture Decisions Matter
- SAP-004 - Architecture vs Design vs Implementation

**Builds On This (learn these next):**
- SAP-054 - Architecture Review Process Design
- SAP-056 - Architecture Fitness Functions
- SAP-057 - Architecture Governance at Scale

**Alternatives / Comparisons:**
- SAP-008 - Architecture Review (review process)
- SAP-062 - Architecture Trade-off Framing

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------+
| WHAT IT IS     | The system governing ADR classification,|
|                | format, lifecycle, and discovery.       |
+----------------------------------------------------------+
| PROBLEM SOLVED | Turns individual notes into navigable   |
|                | organisational architectural memory.    |
+----------------------------------------------------------+
| KEY INSIGHT    | ADR format is 33% of the value. The     |
|                | review strategy is the other 67%.       |
+----------------------------------------------------------+
| USE WHEN       | 2+ engineers, 3+ months of work, any    |
|                | architectural decisions being made.     |
+----------------------------------------------------------+
| AVOID WHEN     | Treating ADRs as compliance artefacts   |
|                | rather than deliberative tools.         |
+----------------------------------------------------------+
| TRADE-OFF      | Documentation overhead vs decision      |
|                | amnesia and re-litigation cost.         |
+----------------------------------------------------------+
| ONE-LINER      | ADR strategy = institutional memory.    |
+----------------------------------------------------------+
| NEXT EXPLORE   | SAP-054, SAP-056, SAP-057               |
+----------------------------------------------------------+
```

**If you remember only 3 things:**
1. The strategy has six components: classification, format, lifecycle, storage, discovery, review.
2. Without a review cadence, ADRs decay into misinformation.
3. ADRs are valuable in proportion to how often they are read and referenced, not how many exist.

**Interview one-liner:** "An ADR strategy turns individual decision documents into organisational memory by defining when to write, how to format, how to maintain lifecycle states, and where to store so every decision remains discoverable and current."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Documentation without a maintenance strategy becomes a liability. Any knowledge system (ADRs, runbooks, decision logs) must have an owner, a cadence, and a lifecycle model to remain valuable rather than misleading.

**Where else this pattern appears:**
- **Legal case law** - rulings are only valuable because they are consistently formatted, stored in searchable registries, and supersedeable by higher courts.
- **Medical clinical guidelines** - guidelines are reviewed and updated on defined cycles; outdated guidelines are explicitly retired, not left to accumulate alongside current ones.
- **Financial audit trails** - trade decision logs require consistent format, mandatory review, and lifecycle management to serve their regulatory purpose.

---

### 💡 The Surprising Truth

Teams that adopt ADR strategies consistently report that the highest-value ADRs are not the ones documenting what was chosen - they are the ones documenting what was rejected and why. The rejected-alternatives section prevents a specific pattern called "zombie option resurrection": a rejected approach that keeps being re-proposed by people unaware it was already evaluated. In organisations without ADR strategy, the average architectural decision is re-litigated 2.3 times over a 3-year period, consuming an average of 4-8 engineer-days per re-litigation cycle.

---

### 🧠 Think About This Before We Continue

1. **[A - System Interaction]** An ADR strategy says "store ADRs in the git repository." But when a decision spans multiple repositories (e.g. an inter-service API contract), where does the ADR live, and how do consuming teams discover it?
   *Hint:* Consider federated ADR models and the role of a central architecture repository.

2. **[B - Scale]** At 5 engineers, one person can review all ADRs quarterly. At 200 engineers across 20 teams, who reviews ADRs and how is consistency maintained across team-level and org-level ADRs?
   *Hint:* Think about ADR ownership, hierarchy, and architectural guild structures.

3. **[C - Design Trade-off]** ADRs capture reasoning at a point in time, but architectural context evolves. Where is the line between "this ADR should be superseded" and "this ADR's reasoning still holds even though the world has changed"?
   *Hint:* Consider what makes an ADR "stale" vs "still valid despite changed environment."
