---
layout: default
title: "Prioritization (MoSCoW, RICE)"
parent: "Behavioral & Leadership"
nav_order: 1741
permalink: /leadership/prioritization/
number: "1741"
category: Behavioral & Leadership
difficulty: ★★☆
depends_on: Technical Roadmap, Stakeholder Communication
used_by: Technical Roadmap, Technical Debt Management, Sprint Planning
related: Technical Roadmap, Estimation Techniques, Technical Debt Management
tags:
  - leadership
  - planning
  - intermediate
  - prioritization
  - product
---

# 1741 — Prioritization (MoSCoW, RICE)

⚡ TL;DR — Prioritization frameworks like MoSCoW and RICE are structured methods for deciding what to work on next — MoSCoW classifies items by necessity (Must/Should/Could/Won't), RICE scores them by expected impact (Reach × Impact × Confidence ÷ Effort) — making trade-off decisions visible, defensible, and communicable to stakeholders.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every stakeholder believes their request is the most important. The engineering team has 40 backlog items and capacity for 6 this quarter. Without a framework, prioritisation is determined by who shouts loudest, who has the most seniority, or who made the request most recently. Work gets selected that is not actually the highest value, and the team cannot explain why one thing was done before another. Stakeholders feel their requests are arbitrarily ignored.

**THE BREAKING POINT:**
In a resource-constrained environment (every engineering environment), every "yes" to one thing is a "no" to everything else. Without a prioritisation framework, these trade-off decisions are made implicitly and inconsistently. Explicit frameworks make the trade-offs visible, discussable, and defensible.

**THE INVENTION MOMENT:**
MoSCoW (Dai Clegg, 1994) was developed for RAD (Rapid Application Development) to help teams make fast, clear decisions about feature scope. RICE (Intercom, 2016) was developed as a product management framework for scoring and comparing initiatives across multiple dimensions, reducing the influence of HiPPO (Highest-Paid Person's Opinion) in prioritisation decisions.

---

### 📘 Textbook Definition

**MoSCoW prioritisation:** Classifies work items into four categories: **Must have** (non-negotiable; project fails without these), **Should have** (important but not critical; significant pain if absent), **Could have** (desirable but low impact if absent; "nice to have"), **Won't have this time** (explicitly deprioritised for this period — not permanently rejected). MoSCoW is most useful for scoping releases and MVP definitions.

**RICE scoring:** Scores each initiative on four dimensions: **Reach** (how many users/customers affected in a period), **Impact** (how much does it move the key metric, scored 0.25–3), **Confidence** (certainty in the estimates, expressed as %, capped at 100%), **Effort** (engineer-months to complete). **RICE score = (Reach × Impact × Confidence) / Effort**. Higher score = higher priority. RICE is most useful for comparing initiatives with different sizes and types of impact.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
MoSCoW asks "do we need this?" RICE asks "is this worth the effort?" Together they help you decide what to build next based on value, not volume or politics.

**One analogy:**
> Prioritisation frameworks are like a hospital triage system. Without triage, patients are treated in arrival order — the first person with a bruise gets care before the last person with a heart attack. Triage imposes a rational ordering: severity (must treat) → significant benefit from early treatment (should treat) → manageable to wait (could treat). MoSCoW is the triage classification; RICE is the severity quantification. Both make the ordering rational rather than arbitrary.

**One insight:**
The most important function of a prioritisation framework is not the output (the ranked list) but the conversation it forces. When a team debates RICE scores, they are explicitly negotiating the assumptions underlying the estimates — and those assumptions reveal misaligned expectations before they become expensive surprises.

---

### 🔩 First Principles Explanation

**MoSCoW IN PRACTICE:**

```
MUST HAVE (M):
  Non-negotiable; scope is fixed
  Questions to ask:
    "If this is not in the release, will the product work?"
    "Is there a legal/compliance requirement?"
    "Will customers refuse to use the product without it?"
  Warning: if everything is Must Have, the framework fails
  Target: ≤ 60% of total scope

SHOULD HAVE (S):
  Important; high pain if absent; but there is a workaround
  "Users would be significantly inconvenienced without this,
   but they could complete the task another way."
  Target: ~20% of total scope

COULD HAVE (C):
  Desirable; lower pain if absent; natural candidates for cuts
  "Would be nice; users would appreciate it; fine to cut"
  Target: ~20% of total scope

WON'T HAVE (W):
  Explicitly out of scope FOR THIS PERIOD
  Critical: document these; they are not "rejected" —
            they are deferred, with a record of why
  This prevents scope re-introduction mid-sprint
```

**RICE SCORING:**

```
REACH:
  How many users/customers does this affect
  in the given period (e.g., per quarter)?
  Use real data where possible: MAUs, segment size
  Example: 10,000 users/quarter

IMPACT:
  How much does it move the key metric per user affected?
  Scale: 3 = massive impact; 2 = high; 1 = medium;
         0.5 = low; 0.25 = minimal
  Example: 2 (high impact per affected user)

CONFIDENCE:
  How confident are you in the estimates?
  80% = solid evidence; 50% = educated guess; 20% = untested
  Example: 80%

EFFORT:
  Total engineer-months to design, build, and ship
  Include PM, design, QA time if applicable
  Example: 2 engineer-months

RICE SCORE = (10,000 × 2 × 0.80) / 2 = 8,000
```

**COMMON TRAPS:**

```
MoSCoW traps:
  "Must Have inflation" — too much in M bucket
    → Challenge: "What happens if we ship without this?"
  No Won't Have list — re-opened debates every sprint
    → Maintain Won't Have as a committed list
  MoSCoW as one-person decision
    → Needs stakeholder negotiation, not unilateral assignment

RICE traps:
  Gaming confidence — setting confidence at 100% to
  inflate scores
    → Cap confidence at 80% unless you have hard data
  Effort underestimation bias
    → Add 30–50% buffer to team estimates for RICE
  Reach inflation — counting all users, not affected users
    → "How many of our users will actually encounter this?"
```

---

### 🧪 Thought Experiment

**SETUP:**
You are a product tech lead with 20 engineer-weeks for Q3. Three major initiatives are proposed:

**Initiative A:** New search feature (user-requested, high engagement)
Reach: 50,000/quarter, Impact: 2, Confidence: 70%, Effort: 5 engineer-weeks
RICE = (50,000 × 2 × 0.70) / 5 = 14,000

**Initiative B:** Performance optimisation (reduces P95 latency from 4s to 1s)
Reach: 100,000/quarter, Impact: 2, Confidence: 90%, Effort: 3 engineer-weeks
RICE = (100,000 × 2 × 0.90) / 3 = 60,000

**Initiative C:** Dashboard redesign (requested by CEO)
Reach: 5,000/quarter, Impact: 1, Confidence: 50%, Effort: 8 engineer-weeks
RICE = (5,000 × 1 × 0.50) / 8 = 313

**RICE-BASED RANKING:**
1. Initiative B: RICE 60,000 — do this first (20w × 15%)
2. Initiative A: RICE 14,000 — do this (20w × 25%)
3. Initiative C: RICE 313 — defer (low score; CEO request)

**THE HARD CONVERSATION:**
Initiative C was requested by the CEO — but RICE shows it has a dramatically lower return than B and A. The framework gives you a defensible basis for the conversation: "The CEO's dashboard redesign reaches 5,000 users with lower confidence; the performance work reaches 100,000 users with high confidence. Can we discuss deferring the dashboard?"

**THE INSIGHT:**
Without RICE, the CEO's request wins by authority. With RICE, you have a data-supported argument for a different priority order — and the conversation is about the numbers, not about who has more power.

---

### 🧠 Mental Model / Analogy

> RICE prioritisation is like a portfolio manager deciding which investments to make. Each initiative is an investment: you put in effort, you get back value. The portfolio manager doesn't choose the most expensive investment or the one the CEO is most excited about — they choose the one with the best expected return per dollar invested (return × probability ÷ cost). RICE is exactly that calculation for engineering work: expected value (Reach × Impact × Confidence) per unit of investment (Effort). The highest RICE score wins unless there is a compelling reason to override it — and "the CEO asked for it" is not a compelling reason without evidence that the reach and impact are higher than the model says.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
MoSCoW and RICE are structured ways to decide what to work on first. MoSCoW says "must have, should have, could have, won't have this time." RICE scores each item based on how many people it affects, how much it helps, how confident you are, and how long it takes.

**Level 2 — How to use it (engineer or PM):**
For sprint planning: use MoSCoW to classify backlog items — if you can't fit everything, Coulds are first to cut. For quarterly planning with multiple initiatives: score each with RICE. Be honest about confidence — if you've never shipped a feature like this before, confidence should be ≤ 50%. Present the ranking to stakeholders with the scores shown — this moves the conversation from "I want X" to "the data says Y has 10x the expected impact."

**Level 3 — How it works (tech lead or PM):**
The real power of RICE is in the Confidence parameter. Confidence is the most subjective component — and it is the most important check on Reach × Impact optimism. A team that consistently rates confidence at 80–100% without data has gameable scores; a team that honestly calibrates confidence produces scores that differentiate between validated ideas and untested hypotheses. Track: after the quarter, did the initiative achieve the Reach and Impact estimated? This retrospective calibration improves future estimates and accountability for prioritisation decisions.

**Level 4 — Why it was designed this way (principal/staff):**
Prioritisation frameworks are fundamentally political tools disguised as analytical ones. Their value is not the precision of the scores — RICE scores are not precise — but the social and political function they serve: making trade-off assumptions explicit, creating a shared scoring language, and providing a basis for structured disagreement. A team that disagrees about RICE scores is having a productive conversation about business assumptions; a team that prioritises by intuition or authority is having no conversation at all. At the principal/staff level, the more important skill is not scoring but constructing the right prioritisation question: "Are we scoring against the right metric?" "Is Reach the right dimension, or should we weight for strategic alignment?" "Are we missing a whole category of work (technical debt, compliance) in our RICE model?" The framework is a starting point; the judgment is in knowing when to follow the scores and when to override them.

---

### ⚙️ How It Works (Mechanism)

```
PRIORITISATION PROCESS:

1. GATHER ITEMS
   Backlog tickets, proposals, stakeholder requests
    ↓
2. APPLY MoSCoW (scope decision)
   Must / Should / Could / Won't for this period
   Outcome: is this item in scope or not?
    ↓
3. APPLY RICE (ranking within scope)
   Score: Reach × Impact × Confidence / Effort
   Rank by score
    ↓
4. REVIEW + CHALLENGE
   Does the ranking match intuition?
   If not: which assumption is wrong?
   Adjust assumptions with evidence; re-score
    ↓
5. COMMUNICATE
   Share ranked list with stakeholders
   Show scores + assumptions (transparency)
   Invite challenge on specific parameters
    ↓
6. COMMIT
   Final prioritised list for period
   "Won't Have" documented
    ↓
7. RETROSPECT
   Did high-RICE items deliver expected value?
   Calibrate for next period
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Quarterly planning begins
    ↓
Backlog compiled from all sources
    ↓
MoSCoW classification:
  Must / Should / Could / Won't
    ↓
RICE scoring of in-scope items
    ↓
[PRIORITIZATION ← YOU ARE HERE]
  Ranked list by RICE score
  Stakeholder review: challenge assumptions
    ↓
Final commitments for quarter
    ↓
Sprint planning: MoSCoW within each sprint
    ↓
End of quarter: retrospect on RICE accuracy
    ↓
Update assumptions for next cycle
```

---

### 💻 Code Example

**RICE scoring calculator:**
```python
from dataclasses import dataclass

@dataclass
class Initiative:
    name: str
    reach: float          # users/quarter
    impact: float         # 0.25 | 0.5 | 1 | 2 | 3
    confidence: float     # 0.0–1.0 (cap at 0.8 for estimates)
    effort: float         # engineer-months

    @property
    def rice_score(self) -> float:
        if self.confidence > 0.8:
            print(f"Warning: {self.name} — confidence > 80% "
                  f"requires strong evidence")
        return (self.reach * self.impact * self.confidence) \
               / self.effort

def rank_initiatives(initiatives: list[Initiative]) -> None:
    ranked = sorted(initiatives,
                    key=lambda x: x.rice_score,
                    reverse=True)
    print(f"{'Initiative':<30} {'RICE Score':>10}")
    print("-" * 42)
    for item in ranked:
        print(f"{item.name:<30} {item.rice_score:>10,.0f}")

# Example usage
rank_initiatives([
    Initiative("Search Feature",
               reach=50000, impact=2.0,
               confidence=0.70, effort=5),
    Initiative("Performance Optimisation",
               reach=100000, impact=2.0,
               confidence=0.90, effort=3),
    Initiative("Dashboard Redesign",
               reach=5000, impact=1.0,
               confidence=0.50, effort=8),
])
```

---

### ⚖️ Comparison Table

| Framework | Best For | Key Question | Weakness |
|---|---|---|---|
| **MoSCoW** | Release scoping; MVP definition | Must we have this to ship? | "Must Have" inflation; binary classification |
| **RICE** | Comparing multiple initiatives | What has highest expected return? | Estimates can be gamed; scores appear precise but aren't |
| **ICE** (Impact, Confidence, Ease) | Quick scoring; early-stage | Simpler than RICE; faster | No reach dimension; easier to game |
| **Kano Model** | Feature categorisation | What delights vs. dissatisfies users? | Complex; requires user research |
| **Opportunity Scoring** | Feature gaps | Where do users have unmet needs? | Requires survey data |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "RICE scores are precise" | RICE uses rough estimates; precision beyond ±50% is false — use scores for relative ranking, not absolute value |
| "MoSCoW Must = do it no matter what" | Must Have means "must have for this release to work" — if constraints change, Must Haves can be re-evaluated |
| "The CEO's request overrides RICE" | Authority-based overrides are valid but should be explicit: "We are overriding the RICE ranking for strategic reasons: X." This makes the trade-off transparent. |
| "Prioritisation is a PM task only" | Technical feasibility (effort) and technical risk (confidence) are engineering inputs that engineering must own |
| "Once prioritised, the list is fixed" | Priorities change as new information arrives; the framework should be re-run when significant new information changes key assumptions |

---

### 🚨 Failure Modes & Diagnosis

**HiPPO Override (Highest-Paid Person's Opinion)**

**Symptom:** RICE scoring is done, a ranked list is produced, and then a senior stakeholder overrides the top items because they want a different initiative prioritised. The team goes along with it. After the quarter, the RICE process is seen as political theatre.

**Root Cause:** The framework was applied after the decision was already made, not before. Stakeholders were not engaged in the scoring process, so they don't own the outputs.

**Fix:**
```
PROCESS CHANGE:
1. Run scoring session WITH stakeholders, not just for them
   → Stakeholders who contribute to scores own the outputs

2. When an override is requested:
   → Ask stakeholder to update the assumptions: "You want X
      to score higher — what is your estimate of Reach/
      Impact/Confidence? Let's update the score together."
   → If override stands despite updated score: document
      explicitly: "We are prioritising X above the RICE
      ranking for reason Y — accepted by [names]."
   
3. Retrospect on overrides: "We overrode RICE to choose X.
   Did X deliver the expected value? Was the override correct?"
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Technical Roadmap` — prioritisation determines what goes on the roadmap
- `Stakeholder Communication` — prioritisation decisions must be communicated with rationale

**Builds On This (learn these next):**
- `Technical Roadmap` — the roadmap is the output of prioritisation
- `Technical Debt Management` — debt items need prioritisation using these frameworks
- `Sprint Planning` — prioritisation is applied at sprint level as well as quarterly

**Alternatives / Comparisons:**
- `Estimation Techniques` — provides the Effort input to RICE scoring
- `Technical Debt Management` — debt items are prioritised using MoSCoW/RICE alongside features
- `Technical Roadmap` — the medium-term output that prioritisation feeds into

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ MoSCoW       │ Must / Should / Could / Won't             │
│              │ For: release scoping, MVP definition      │
├──────────────┼───────────────────────────────────────────┤
│ RICE         │ (Reach × Impact × Confidence) / Effort    │
│              │ For: comparing initiatives; quarterly plan│
├──────────────┼───────────────────────────────────────────┤
│ RICE IMPACT  │ 3=massive, 2=high, 1=medium,              │
│ SCALE        │ 0.5=low, 0.25=minimal                     │
├──────────────┼───────────────────────────────────────────┤
│ CONFIDENCE   │ Cap at 80% unless you have hard data      │
│              │ 50% = educated guess; 20% = untested idea │
├──────────────┼───────────────────────────────────────────┤
│ CAUTION      │ RICE scores look precise; they are rough  │
│              │ Use for relative ranking, not absolutes   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Prioritisation makes trade-offs visible  │
│              │ — so you choose deliberately, not         │
│              │ accidentally."                            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Estimation Techniques →                   │
│              │ Sprint Planning                           │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** RICE scoring includes a Confidence parameter that is intended to discount uncertain estimates. In practice, teams often inflate confidence because: (a) it feels like admitting ignorance to score confidence below 70%, and (b) low-confidence items are less likely to get funded, creating an incentive to game the score. Design a process for calibrating confidence scores more honestly — specifically: how do you prevent gaming, how do you teach teams to estimate confidence objectively, and how do you use retrospective data to improve future confidence calibration?

**Q2.** MoSCoW's "Must Have" category is consistently abused — everything ends up as Must Have, making the classification useless. Propose a concrete mechanism (a question, a process, a rule) that forces honest Must Have classification. Apply your mechanism to a real scenario: a team is building a new payment checkout. List 8 plausible features and use your mechanism to rigorously classify each as Must/Should/Could/Won't for a first release. Show your work.
