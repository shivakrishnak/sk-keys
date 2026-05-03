---
layout: default
title: "Engineering Strategy"
parent: "Behavioral & Leadership"
nav_order: 1756
permalink: /leadership/engineering-strategy/
number: "1756"
category: Behavioral & Leadership
difficulty: ★★★
depends_on: Technical Roadmap, OKRs
used_by: Build vs Buy vs Outsource, Technical Roadmap, OKRs
related: Technical Roadmap, OKRs, Build vs Buy vs Outsource
tags:
  - leadership
  - strategy
  - advanced
  - engineering-strategy
  - staff-plus
---

# 1756 — Engineering Strategy

⚡ TL;DR — Engineering strategy is a durable written document that enables a team or organisation to make consistent, aligned technical decisions without requiring constant coordination — it consists of a diagnosis (what is actually true about our situation), guiding policies (rules that resolve recurring decision dilemmas), and coherent actions (specific investments and constraints that follow from the policies); its value is that it converts individual decisions into a system of decisions.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Engineering teams make hundreds of technical decisions per quarter. Without a shared strategy, each decision is relitigated from first principles: "Should we build this or buy it?" "Should we invest in the platform or ship features?" "Should we standardise on one language or allow polyglot?" Every decision requires gathering the same stakeholders, rehashing the same context, and making a judgment that contradicts or contradicts previous decisions. Decisions are inconsistent: in January the team chose to build; in April they chose to buy; neither choice reflected a coherent view of the organisation's situation.

**THE BREAKING POINT:**
At scale, the decision cost becomes prohibitive. Staff and principal engineers spend their time in decision meetings rather than building. New engineers can't make decisions independently because there are no decision principles — only case-by-case precedents that nobody has documented. The organisation is slow because decisions are expensive. Inconsistency creates technical fragmentation: six different approaches to the same problem.

**THE INVENTION MOMENT:**
Will Larson ("An Elegant Puzzle," 2019; "Staff Engineer," 2021) articulates the canonical engineering strategy framework. Larson defines strategy as: diagnosis → guiding policies → coherent actions. This structure comes from Richard Rumelt's "Good Strategy/Bad Strategy" (2011), which distinguishes genuine strategy (diagnosis + policies + coherent actions) from "strategy" that is actually a list of goals or wishes.

---

### 📘 Textbook Definition

**Engineering Strategy (Larson):** A written document that establishes the context for technical decisions in an organisation. Consists of: (1) diagnosis of the current situation — what is true, what constraints exist, what problems exist; (2) guiding policies — rules that determine how to resolve recurring decision types within the context; (3) coherent actions — specific investments, constraints, and commitments that follow from the policies.

**Strategy vs Roadmap:** A roadmap is an ordered list of initiatives planned for a time horizon. A strategy is the framework that explains why those initiatives are prioritised that way — and that enables new initiatives to be prioritised consistently in the future without revisiting first principles.

**Strategy vs Goals:** Goals (OKRs) define what you want to achieve (outcomes). Strategy defines the approach and constraints for how you will pursue those outcomes given your situation.

**Good strategy vs. bad strategy (Rumelt):**

- Good strategy: diagnosis + guiding policies + coherent actions
- Bad strategy: a list of goals, a vision statement, or a "strategy document" that contains no policies and no hard choices

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Engineering strategy is a written set of policies and priorities that enables consistent technical decisions at scale — without requiring the same people in every room for every decision.

**One analogy:**

> An engineering strategy is like a country's constitution compared to its case law. The constitution (strategy) contains the principles and constraints that govern all decisions: "free speech is protected," "property rights are defended," "powers are separated." Individual laws and judgments (technical decisions) are made within that framework. Without a constitution, each case requires starting from first principles — "what kind of society do we want?" — which is expensive and produces inconsistent outcomes. With a constitution, decisions are made within a framework that produces predictable, consistent results aligned to fundamental values. Engineering strategy is the constitution for technical decision-making in an organisation.

**One insight:**
The hardest part of writing an engineering strategy is the diagnosis: being honest about what is actually true about your situation, including uncomfortable truths ("we have significant technical debt that is slowing every initiative," "our team lacks expertise in X," "we are 3 months from running out of money"). A strategy built on a flattering but inaccurate diagnosis will produce policies and actions that don't address the real situation.

---

### 🔩 First Principles Explanation

**STRATEGY STRUCTURE (Larson/Rumelt):**

```
COMPONENT 1: DIAGNOSIS
  What is actually true about our situation?
  What constraints exist (time, money, team size, skills)?
  What technical problems are blocking us?
  What is the competitive context?
  What risks exist?

  EXAMPLE DIAGNOSIS (platform team):
  "Our service has 500k requests/day and is growing 40%/quarter.
   The monolith has 6 years of accumulated technical debt.
   The team has 8 engineers with strong Python skills but
   limited distributed systems expertise. At 2x current load,
   the database will become the bottleneck. We have 6 months
   at current growth rate before this becomes critical."

COMPONENT 2: GUIDING POLICIES
  Given the diagnosis: what rules resolve recurring decisions?
  What will we always do? Never do?
  How will we trade off competing concerns?

  EXAMPLE GUIDING POLICIES (same team):
  "1. We optimise for reliability over new features when
      they conflict. SLA > feature velocity.
   2. We do not introduce new technology without a
      production-ready team member — minimum 1 person with
      3 months production experience before adoption.
   3. We build internally when: (a) it is core to competitive
      differentiation; (b) no available vendor meets
      our reliability requirements. We buy/use OSS otherwise.
   4. We prefer incremental extraction over big-bang rewrites.
      No migration that requires > 2 weeks feature freeze."

COMPONENT 3: COHERENT ACTIONS
  Given the policies: what specific investments/decisions follow?
  What do we start? Stop? Deprioritise?

  EXAMPLE COHERENT ACTIONS:
  "1. Database read replica and query optimisation: Q1 priority.
   2. No new service extraction until database bottleneck resolved.
   3. Dedicate 20% of engineering capacity to debt reduction
      in affected services (permanent allocation, not sprint-by-sprint).
   4. New distributed systems training programme: 2 engineers
      complete course by end Q2.
   5. Evaluate managed PostgreSQL (RDS/Cloud SQL) vs self-managed:
      buy/build decision per guiding policy 3."
```

**WHAT MAKES A POLICY A POLICY (vs a goal):**

```
GOAL (not a policy):
  "We will improve reliability."
  → This says WHAT but not HOW to decide. Not a policy.

POLICY:
  "When reliability and feature velocity conflict,
   reliability wins."
  → This resolves the decision. When an engineer faces
    this tradeoff, the policy answers it.

GOAL (not a policy):
  "We will reduce technical debt."
  → What is technical debt? Which debt? When?

POLICY:
  "Every sprint allocates 20% capacity to debt work
   identified by the team. This is not negotiable
   with product. The team owns this decision."
  → This resolves future capacity decisions without
    requiring a meeting.

TEST: "If an engineer faces decision X tomorrow,
      does our strategy tell them what to do?"
  Yes → it's a policy
  No  → it's a goal, not a strategy
```

---

### 🧪 Thought Experiment

**SETUP:**
Two engineering organisations at comparable companies. Both are growing 50% YoY. Both have similar team sizes (30 engineers).

**Org A — No Strategy:**
Q1: Product asks for new payment integration. Infra builds a bespoke integration. Q2: Product asks for another integration. Different team builds it differently. Q3: 3 engineers are separately evaluating whether to adopt Kafka, each without knowing the others are investigating. Q4: 4 different data persistence patterns in production; no standard. Staff engineers spend 60% of time in decision meetings.

**Org B — Engineering Strategy:**
Q1: Engineering strategy exists. Guiding policy: "Integrations use the standard integration framework from Platform team — no bespoke implementations without VP approval." "New technology adoption requires RFC + proof of concept + team champion with 3 months prod experience." Q1: Payment integration built using standard framework. Q2: Second integration: same framework, half the time. Q3: Kafka RFC process begins — one cross-functional investigation with shared outcome. Q4: One data persistence standard applied to 80% of services. Staff engineers spend 60% of time on technical work.

**The insight:** The strategy in Org B didn't prevent any work. It prevented the same work from happening four different ways simultaneously — and it did so without a meeting. The guiding policy resolved the decision before the decision had to be made.

---

### 🧠 Mental Model / Analogy

> Engineering strategy is like a chess opening theory. A chess grandmaster doesn't invent every opening from scratch in tournament play — they know deep theory about why certain opening moves are strong, what positions they create, and what follows from them. When facing a known position, the grandmaster doesn't deliberate: the theory resolves it. Strategy is the theory that resolves known classes of engineering decisions. Without it, every decision is a tournament game played from scratch — expensive, slow, inconsistent. With it, known decision classes are resolved by policy, and engineering judgment is reserved for genuinely novel situations where theory doesn't apply.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Engineering strategy is a written document that says: "Here is what is true about our situation, here are the rules we'll follow to make decisions given that situation, and here are the specific things we're going to invest in as a result." Its purpose: so that teams can make consistent, aligned technical decisions without a meeting for every decision.

**Level 2 — How to use it (engineer):**
When you're making a technical decision: check if the engineering strategy addresses it. If it does: follow the policy. If it doesn't: this may be a gap in the strategy — document the decision you made, the reasoning, and propose adding a policy. Strategy grows incrementally as gaps are discovered. When you disagree with a policy: the right response is to propose a change to the strategy document, not to ignore it.

**Level 3 — How it works (tech lead):**
Writing an engineering strategy for your team: start with the diagnosis. Spend more time on the diagnosis than you expect to — the policies only work if the diagnosis is accurate. Then derive policies from the diagnosis: "Given that we have X constraint, we should always/never do Y." Policies should resolve real dilemmas the team faces repeatedly. Coherent actions are the immediate investment backlog that follows from the policies. Share the draft broadly; collect disagreement; revise. Publish and reference it: "Per the engineering strategy..." when making decisions. Update it when the diagnosis changes (technology changes, team grows, competitive context shifts).

**Level 4 — Why it was designed this way (principal/staff):**
At the principal/staff level, the engineering strategy is your primary deliverable. Staff engineers multiply their impact by establishing the framework within which other engineers make decisions — not by making all the decisions themselves. A staff engineer who writes a strong engineering strategy for their organisation enables 30 engineers to make consistently good decisions for 12 months; a staff engineer who joins every decision meeting enables slightly better decisions in the 50 decisions they can attend. The leverage ratio is not close. Strategy documents also create institutional memory: when staff engineers leave, the strategy persists. Without written strategy, organisational engineering wisdom leaves with each departure. Strategy is the mechanism by which individual expertise becomes institutional knowledge.

---

### ⚙️ How It Works (Mechanism)

```
STRATEGY WRITING PROCESS:

STEP 1: GATHER INPUTS
  Current state of systems
  Team capabilities and gaps
  Business constraints (time, money, competitive)
  Known recurring decision dilemmas
  Stakeholder input (product, infra, security)
    ↓
STEP 2: WRITE DIAGNOSIS (most important step)
  What is true? (not: what do we wish were true?)
  What are the constraints?
  What problems are blocking us?
  What risks exist?
    ↓
STEP 3: DERIVE GUIDING POLICIES
  For each recurring decision type: what rule resolves it?
  Policies should create hard tradeoffs — they must
  say "X over Y when they conflict"
    ↓
STEP 4: DERIVE COHERENT ACTIONS
  What specific investments follow from the policies?
  These become Q1 roadmap commitments
    ↓
STEP 5: REVIEW AND PUBLISH
  Share with team; collect disagreement
  Update based on feedback
  Publish in shared location (wiki, eng handbook)
  Reference in future decisions: "per strategy..."
    ↓
STEP 6: MAINTAIN
  Review quarterly or when significant context changes
  Update diagnosis when situation changes
  Policies should change when diagnosis changes
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Business context: goals, constraints, competitive situation
    ↓
Diagnosis: what is actually true about our engineering situation
    ↓
[ENGINEERING STRATEGY ← YOU ARE HERE]
Guiding policies: rules that resolve recurring decisions
    ↓
Coherent actions: specific investments that follow from policies
    ↓
Technical roadmap: ordered list of initiatives from coherent actions
    ↓
OKRs: quarterly outcome goals aligned to strategy
    ↓
Sprint planning: feature work + strategy-driven investment
    ↓
[Decision encountered by engineer]
→ Strategy provides policy: decision made without meeting
→ Strategy silent: RFC process; outcome updates strategy
```

---

### 💻 Code Example

**Engineering strategy template (Markdown):**

```markdown
# Engineering Strategy — Platform Team — Q1 2025

## Diagnosis

### What is True

- Service handles 500k req/day, growing 40% QoQ
- Database (PostgreSQL) is primary bottleneck at current load
- Team: 8 engineers; strong Python; limited distributed systems expertise
- 6+ years of monolith code; architectural debt concentrated in auth
  and payments modules
- No on-call runbooks for >60% of production services
- Current: p99 API latency = 2.1s; target: <500ms

### Constraints

- Team headcount: no new hires planned Q1
- At current growth: DB bottleneck becomes critical by August
- 2 engineers unavailable weeks 6–8 (PTO + parental leave)

### Key Risks

- Database capacity failure before mitigation complete: HIGH
- Auth module instability during payment migration: MEDIUM
- Knowledge concentration (2 engineers own auth context): HIGH

---

## Guiding Policies

1. **Reliability over velocity**: When SLA and feature work conflict,
   reliability work takes priority. No exceptions without VP sign-off.

2. **No new technology without a team champion**:
   New technology (new language, framework, infrastructure) requires:
   (a) RFC reviewed by tech lead, (b) one team member with ≥3 months
   production experience, (c) rollback plan. No exceptions.

3. **Build vs Buy**:
   Build internally ONLY when: (a) core to competitive differentiation,
   OR (b) no vendor meets p99 < 500ms latency requirement.
   Default: evaluate OSS/vendor first.

4. **Incremental over big-bang**:
   No migration that requires >2-week feature freeze.
   All migrations must support rollback.

5. **20% debt allocation**:
   Every sprint allocates 20% capacity to tech debt identified by the team.
   Product backlog does not override this allocation.

---

## Coherent Actions — Q1

1. **Database read replica** (Weeks 1–4):
   Implement read replica for reporting queries. Owner: Alice.

2. **Auth module knowledge transfer** (Weeks 2–8):
   Pairing sessions; written runbooks for auth service. Owner: Bob.

3. **Evaluate managed DB (buy decision per policy 3)** (Weeks 3–6):
   RDS vs Cloud SQL vs self-managed. Decision memo by week 6. Owner: Carlos.

4. **No new service extractions** until DB bottleneck resolved.
   Exception process: tech lead approval required.
```

---

### ⚖️ Comparison Table

|                      | Engineering Strategy           | Technical Roadmap           | OKRs                        |
| -------------------- | ------------------------------ | --------------------------- | --------------------------- |
| **Time horizon**     | 1–2 years                      | 6–12 months                 | Quarterly                   |
| **What it contains** | Diagnosis + policies + actions | Ordered list of initiatives | Objectives + measurable KRs |
| **Primary output**   | Decision framework             | Delivery plan               | Outcome commitments         |
| **When to update**   | When diagnosis changes         | Quarterly planning          | Quarterly                   |
| **Who owns it**      | Staff engineer / EM            | Product + engineering       | Team                        |
| **Stabilises**       | Decisions                      | Delivery plan               | Goals                       |

---

### ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                                                                                                                             |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Strategy = list of goals"                | A list of goals is not a strategy. Strategy contains policies that resolve decision dilemmas. Goals say what you want; strategy says how you'll decide.                             |
| "Strategy is only for senior leadership"  | Team-level engineering strategies are valuable for any team > 5 engineers facing recurring decision dilemmas.                                                                       |
| "Strategy is fixed for the year"          | Strategy should be updated when the diagnosis changes significantly. A strategy built on an outdated diagnosis is worse than no strategy.                                           |
| "Good strategy avoids hard tradeoffs"     | Good strategy requires hard tradeoffs. "We prioritise reliability over velocity" is a hard tradeoff. "We value both reliability and velocity" is not a strategy — it's a platitude. |
| "Engineers don't need strategy documents" | Without written strategy, inconsistency is inevitable at scale. Written strategy is how engineering organisations grow beyond "everyone in the same room" coordination.             |

---

### 🚨 Failure Modes & Diagnosis

**"Strategy" Documents That Are Lists of Goals**

**Symptom:** The engineering team publishes an "Engineering Strategy" for H2 that contains: a vision statement ("be the most reliable platform in the industry"), 5 goal statements ("improve reliability," "reduce technical debt," "accelerate developer velocity," "invest in security," "improve observability"), and a roadmap. There are no guiding policies. There are no tradeoff statements. Engineers can't use the "strategy" to resolve any specific decision — because it doesn't resolve any decisions.

**Root Cause:** The document is aspirational, not prescriptive. It says what the team wants to achieve but not how decisions will be made to achieve it. Rumelt calls this "bad strategy" — a list of goals dressed up as a strategy document.

**Fix:**

```
CONVERT GOALS TO POLICIES:

Goal: "Improve reliability"
  → What decisions would a reliability-first policy resolve?
  → Policy: "When reliability and feature velocity conflict,
             reliability work takes priority. SLA < 99.9%:
             all feature work pauses until SLA restored."

Goal: "Reduce technical debt"
  → What specific debt? How much investment? Who decides?
  → Policy: "20% of sprint capacity allocated to tech debt
             in services with quality score < 3 (as rated quarterly
             by the team). Product backlog does not override this."

Goal: "Accelerate developer velocity"
  → Velocity of what? Measured how? What tradeoffs?
  → Policy: "We standardise on [language/framework] for all new
             services. Exceptions require tech lead approval and
             a documented rationale in the RFC."

TEST EVERY LINE IN YOUR STRATEGY:
  "Does this line resolve a real decision engineers will face?"
  No? → It's a goal. Rewrite as a policy or remove.
  Yes? → It's a policy. Keep it.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Technical Roadmap` — the roadmap is the delivery plan; strategy is the framework behind the roadmap
- `OKRs` — OKRs are the quarterly outcome commitments; strategy is the framework that shapes them

**Builds On This (learn these next):**

- `Build vs Buy vs Outsource` — the build/buy/outsource decision is one of the most important recurring decisions that engineering strategy should resolve
- `Technical Roadmap` — coherent actions from strategy become roadmap items
- `OKRs` — strategy provides the context in which OKRs are set

**Alternatives / Comparisons:**

- `OKRs` — outcome goals for a quarter; complementary to strategy but not a substitute
- `Technical Roadmap` — the delivery plan derived from strategy

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ COMPONENT 1 │ Diagnosis: what is actually true?          │
│             │ (constraints, risks, problems)             │
├─────────────┼──────────────────────────────────────────-─┤
│ COMPONENT 2 │ Guiding Policies: rules that resolve       │
│             │ recurring decision dilemmas                │
├─────────────┼──────────────────────────────────────────-─┤
│ COMPONENT 3 │ Coherent Actions: specific investments     │
│             │ that follow from the policies              │
├─────────────┼──────────────────────────────────────────-─┤
│ KEY TEST    │ "Does this line resolve a real decision?"  │
│             │ No → it's a goal. Yes → it's a policy.    │
├─────────────┼──────────────────────────────────────────-─┤
│ HARD CHOICES│ "When X and Y conflict: X wins" is a      │
│             │ policy. "We value both X and Y" is not.   │
├─────────────┼──────────────────────────────────────────-─┤
│ NEXT EXPLORE│ Build vs Buy vs Outsource →               │
│             │ Technical Roadmap                         │
└─────────────┴────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A new VP of Engineering joins a 60-person engineering organisation. She discovers: no written engineering strategy exists; the team has 12 different technologies in production; each team has made independent architectural decisions for 3 years; there are 4 different approaches to data persistence and 3 different approaches to service-to-service communication. She wants to write an engineering strategy in her first 90 days. Design the process she should follow: who to interview, what questions to ask, how to structure the diagnosis, and how to write policies that will actually be adopted by teams who've been operating autonomously. What is the single biggest risk in this situation, and how does the strategy writing process mitigate it?

**Q2.** Good strategy requires hard tradeoffs — policies that explicitly choose X over Y when they conflict. Articulate three specific engineering tradeoffs that most engineering organisations face, and for each: (a) write a guiding policy that resolves the tradeoff, (b) explain what organisational context would make this policy appropriate, and (c) explain what different context would make the opposite policy appropriate. This exercise demonstrates that strategy is context-dependent — the right policy depends on the right diagnosis.
