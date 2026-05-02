---
layout: default
title: "Estimation Techniques"
parent: "Behavioral & Leadership"
nav_order: 1742
permalink: /leadership/estimation-techniques/
number: "1742"
category: Behavioral & Leadership
difficulty: ★★☆
depends_on: Prioritization (MoSCoW, RICE), Sprint Planning
used_by: Sprint Planning, Technical Roadmap, Prioritization (MoSCoW, RICE)
related: Technical Roadmap, Risk Management, Sprint Planning
tags:
  - leadership
  - planning
  - intermediate
  - estimation
  - agile
---

# 1742 — Estimation Techniques

⚡ TL;DR — Estimation techniques (story points, t-shirt sizing, three-point/PERT, planning poker) are structured methods for forecasting how long software work will take — their purpose is not to produce precise predictions but to expose uncertainty, identify unknowns, and produce calibrated ranges that teams can plan around and stakeholders can act on.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A manager asks "how long will this feature take?" An engineer says "two weeks." Six weeks later the feature is not done. Trust erodes. The engineer wasn't lying — they genuinely believed two weeks. But they didn't think about the unknowns: the unfamiliar API, the required auth work, the design review cycle. Without a structured estimation process, engineers estimate only what they can see, not what they cannot yet see.

**THE BREAKING POINT:**
Software estimation is notoriously difficult because software work is novel — you are building something that has never been built before, using a process that introduces new unknown unknowns as you go. The "cone of uncertainty" formalises this: early in a project, effort estimates can be off by 4× in either direction. As scope is understood, the range narrows. The failure mode is not that estimation is inaccurate; it is that teams present point estimates as if they were accurate, hiding the uncertainty until it surfaces as a schedule miss.

**THE INVENTION MOMENT:**
Story points emerged from XP (Extreme Programming, late 1990s) as a way to estimate relative complexity rather than calendar time, removing the pressure of calendar commitments. Planning poker (James Grenning, 2002) added a structured elicitation mechanism to surface disagreement among estimators. Three-point estimation comes from PERT (Program Evaluation and Review Technique, US Navy, 1950s), originally for missile programme scheduling under uncertainty.

---

### 📘 Textbook Definition

**Story points:** Unitless relative measure of the effort, complexity, and uncertainty of a work item. Commonly uses a Fibonacci-like sequence (1, 2, 3, 5, 8, 13, 21) to reflect the non-linear increase in uncertainty with size. Teams calibrate story points against a reference item; velocity (points per sprint) is tracked over time and used to forecast future delivery.

**T-shirt sizing:** Categorical estimation (XS/S/M/L/XL) for coarse-grained planning before items are well-understood. Used for roadmap-level estimation where story points would imply false precision.

**Three-point estimation (PERT):** Estimates three values for each task: Optimistic (O), Most Likely (M), Pessimistic (P). Expected duration = (O + 4M + P) / 6. Standard deviation = (P - O) / 6. Produces a range and confidence interval rather than a point estimate.

**Planning poker:** Structured estimation exercise where each team member simultaneously reveals their estimate (using story point cards) to prevent anchoring bias. Disagreements among estimates are discussed and reconciled.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Estimation techniques are structured methods for making the uncertainty in software work visible — not for eliminating uncertainty, but for making it explicit so teams can plan around it.

**One analogy:**
> Estimating software work is like estimating how long it takes to read a book you've never seen. You might estimate by spine thickness (t-shirt sizing: it looks like an XL). You might compare to books you've read before (story points: it's about as complex as that 700-page thriller I read last year). You might ask three people and take the average of their guesses, weighted by their uncertainty (three-point). None of these methods gives you an exact answer — they all give you a range to plan around. The mistake is pretending you have an exact answer when you don't.

**One insight:**
The value of planning poker is not the numbers produced — it is the conversations triggered by disagreement. When one person says "3 points" and another says "13 points," one of them knows something the other doesn't. That conversation surfaces the hidden assumption before it becomes a schedule surprise.

---

### 🔩 First Principles Explanation

**WHY POINT ESTIMATES FAIL:**

```
Engineer's mental model of a task:
  Task = [known work I can see]

Reality:
  Task = [known work]
       + [integration with system X, which has surprises]
       + [review cycle, which takes longer than expected]
       + [dependency on team Y, who is busy]
       + [unknown unknowns — things you don't know you don't know]

Point estimate captures: known work only
Actual time: known work + all the hidden terms

This is why "it's two weeks" becomes six weeks —
not because engineers are careless, but because
the estimate was made before the hidden terms were known.
```

**STORY POINTS vs HOURS:**

```
HOURS:
  + Intuitive: "I'll spend 8 hours on this"
  - Calendar-bound: a 4-hour task takes a day if meetings fill half the day
  - Anchors managers to specific dates
  - Different engineers have different velocity in hours

STORY POINTS:
  + Relative: "This is twice as complex as that 3-point item"
  + Velocity-normalised: team velocity handles individual speed differences
  + Stable across calendar time (vs. hours which drift with holidays etc.)
  - Requires calibration: teams must agree on a reference item
  - Meaningless across teams: team A's 5 ≠ team B's 5
  - Can be gamed: inflation of points inflates velocity artificially
```

**THREE-POINT / PERT:**

```
For a complex migration task:
  Optimistic (O) = 3 days (if everything is clean)
  Most Likely (M) = 7 days (based on similar past work)
  Pessimistic (P) = 20 days (if legacy code is as bad as feared)

Expected = (3 + 4×7 + 20) / 6 = (3 + 28 + 20) / 6 = 8.5 days
Std Dev  = (20 - 3) / 6 = 2.8 days

So: estimate 8–9 days, with a 2.8-day standard deviation
    → 68% confidence the task is in the range 6–12 days
    → 95% confidence range: 3–14 days

This is more honest than "it'll take a week."
```

---

### 🧪 Thought Experiment

**SETUP:**
A team is planning a migration of authentication from a monolith to an OAuth service. They've never worked with this OAuth service before. Story point planning poker results:

- Alice: 13 points
- Bob: 5 points
- Carlos: 8 points
- Diana: 21 points

**Standard process:** Average (ignore outliers), pick 8. Move on.

**Better process (planning poker as intended):** Ask Alice (13) and Diana (21) what they're seeing that Bob (5) is not.

Alice: "I've read the OAuth service docs — the token refresh flow is not well documented. I built 3 points of buffer for debugging."
Diana: "This service requires an infrastructure change to enable service-to-service auth. That's a separate track. I don't think anyone has counted that."

**The conversation reveals:**
1. The OAuth service docs are unclear — this is risk (more buffer needed)
2. There is an infrastructure dependency nobody scoped — this is a missing work item

**Revised plan:** Split into two stories: (a) infrastructure auth setup, (b) migration itself. Estimate separately. Total: 5 + 13 = 18 points — but now both stories have clearer scopes and the hidden dependency is visible.

**The insight:** The value was not the numbers. The value was the conversation that discovered the hidden infrastructure dependency before the sprint started.

---

### 🧠 Mental Model / Analogy

> Estimation techniques in software are analogous to weather forecasting. A good meteorologist doesn't say "it will rain exactly 2.7 mm on Thursday." They say "there is a 70% chance of moderate rain on Thursday, with uncertainty increasing toward the weekend." The probability and range are not weakness — they are the honest representation of the forecast. Bad meteorologists (and bad engineers) give point estimates under social pressure: "I'll say Thursday, 3mm" — and are wrong more often than the range-based forecast. The cone of uncertainty formalises this: software forecasts are ranges that narrow as you learn more. The professional move is to communicate those ranges, not to hide them behind a false point estimate.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Estimation techniques are structured ways for teams to guess how long work will take. Instead of one person saying "two weeks," the team uses processes like planning poker (everyone votes simultaneously) or story points (relative sizes) to surface hidden complexity and get more reliable estimates.

**Level 2 — How to use it (engineer):**
Use story points for sprint planning: pick a reference story (the team's agreed "3 pointer"), estimate relative to it using Fibonacci scale. Use t-shirt sizing for roadmap items you haven't refined yet. Use three-point estimation when a task has high uncertainty — state your optimistic, most likely, and pessimistic estimates explicitly. In planning poker, always explain your reasoning when you diverge significantly from the group.

**Level 3 — How it works (tech lead):**
Track velocity (story points completed per sprint) over 6+ sprints to get a stable average. Use velocity to forecast delivery: if backlog has 200 points and velocity is 40 points/sprint, forecast 5 sprints ± buffer. Watch for velocity inflation (team inflates story points to look productive) — cross-check against actual throughput and cycle time. Three-point estimation is most useful for work with external dependencies (third-party APIs, regulatory approvals) where the pessimistic case is genuinely catastrophic.

**Level 4 — Why it was designed this way (principal/staff):**
At the staff level, the key insight is that estimation is a communication problem, not a calculation problem. The purpose of estimation exercises is not to produce numbers — it is to surface the risk model that each engineer has for the work. Engineers who estimate high see risks that engineers who estimate low don't see. The planning poker reveal is designed to force simultaneous disclosure of risk models (avoiding anchoring) before the social negotiation of the estimate begins. This makes hidden risk visible before commitment, not after. Staff engineers understand that the estimate is less important than the estimation conversation — and invest in processes that maximise the information density of that conversation.

---

### ⚙️ How It Works (Mechanism)

```
PLANNING POKER:
  1. Scrum master reads a story
  2. Team members select their estimate card face down
  3. Reveal simultaneously (avoid anchoring)
  4. Discuss: high and low estimators explain their reasoning
  5. Re-vote if significant divergence
  6. Repeat until consensus or facilitator decides
  7. Record estimate

VELOCITY TRACKING:
  Sprint 1: planned 40pt, completed 32pt → velocity 32
  Sprint 2: planned 40pt, completed 38pt → velocity 38
  Sprint 3: planned 40pt, completed 36pt → velocity 36
  Rolling average: (32+38+36)/3 = 35pt/sprint

FORECAST:
  Backlog = 180pt
  Velocity = 35pt/sprint
  Sprints remaining = 180/35 ≈ 5.1 → ~5–6 sprints
  Add buffer for unknowns: +20% → 6–7 sprints
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Quarterly planning
    ↓
T-shirt sizing of all initiatives
    ↓
High-confidence items break into stories
    ↓
Sprint planning: planning poker per story
    ↓
[ESTIMATION ← YOU ARE HERE]
  Story points assigned; velocity tracked
    ↓
Sprint execution: track actual vs. estimated
    ↓
Retrospect: which estimates were furthest off? Why?
    ↓
Adjust estimation process for next sprint
    ↓
Forecast delivery with velocity-based ranges
```

---

### 💻 Code Example

**Three-point PERT estimation calculator:**
```python
import math

def pert_estimate(
    optimistic: float,
    most_likely: float,
    pessimistic: float
) -> dict:
    """
    PERT three-point estimation.
    Returns expected value, std dev, and confidence intervals.
    """
    expected = (optimistic + 4 * most_likely + pessimistic) / 6
    std_dev = (pessimistic - optimistic) / 6
    return {
        "expected_days": round(expected, 1),
        "std_dev": round(std_dev, 1),
        "68_pct_range": (
            round(expected - std_dev, 1),
            round(expected + std_dev, 1)
        ),
        "95_pct_range": (
            round(expected - 2 * std_dev, 1),
            round(expected + 2 * std_dev, 1)
        ),
    }

# Auth migration — high-uncertainty task
result = pert_estimate(
    optimistic=3,
    most_likely=7,
    pessimistic=20
)
print(f"Expected: {result['expected_days']} days")
print(f"68% range: {result['68_pct_range'][0]}–{result['68_pct_range'][1]} days")
print(f"95% range: {result['95_pct_range'][0]}–{result['95_pct_range'][1]} days")
```

---

### ⚖️ Comparison Table

| Technique | Scale | Best For | Key Weakness |
|---|---|---|---|
| **Story Points** | Relative (Fibonacci) | Sprint planning; velocity tracking | Meaningless cross-team; can be gamed |
| **T-Shirt Sizing** | XS/S/M/L/XL | Roadmap / coarse planning | Too imprecise for sprint commitment |
| **Three-Point / PERT** | Absolute (hours/days) | High-uncertainty tasks; dependencies | Requires discipline to set honest P |
| **#NoEstimates** | Count / cycle time | Continuous flow; Kanban | Needs historical cycle time data |
| **Planning Poker** | Story points | Team consensus; risk surfacing | Time-intensive; can become social pressure |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Story points are a better unit of time" | Story points are not time — they are relative complexity. Velocity converts them to a time forecast. |
| "We can estimate everything upfront precisely" | The cone of uncertainty is real. Early estimates can be 4× off. Build buffers; update estimates as scope is clarified. |
| "A 1-point story is easy" | 1 point means "trivially simple relative to our reference story" — not zero risk. Even 1-point stories can explode. |
| "Estimation accuracy means the team is good" | Estimate accuracy depends heavily on story clarity and stability. Unstable requirements make even good estimators inaccurate. |
| "Three-point means pessimistic always wins" | Three-point weights the most likely case 4×. A realistic most-likely estimate prevents pessimism from dominating. |

---

### 🚨 Failure Modes & Diagnosis

**Story Point Inflation / "Velocity Gaming"**

**Symptom:** Velocity increases sprint-over-sprint but actual throughput (features shipped) doesn't. The team appears to be accelerating on the chart but delivery dates keep slipping.

**Root Cause:** Engineers inflate story point estimates to hit velocity targets. Common causes: (a) velocity is used as a performance metric, incentivising inflation; (b) team learned that small estimates lead to scope-creep pressure; (c) estimates expanded to include everything (meetings, code review, etc.) rather than development effort only.

**Fix:**
```
1. Decouple velocity from performance measurement
   → Velocity is a forecasting tool, not a KPI
   
2. Track cycle time alongside story points:
   → If cycle time per point increases, inflation is occurring

3. Re-baseline periodically with fresh reference stories
   → Pick 3 recently completed stories; reset the scale

4. Separate estimates into dev effort vs. total work
   → "3 dev points + 2 days review cycle" is more honest
   → Don't embed review/meeting time in story points
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Prioritization (MoSCoW, RICE)` — RICE requires Effort estimates; estimation feeds prioritisation
- `Sprint Planning` — estimation is done during sprint planning

**Builds On This (learn these next):**
- `Sprint Planning` — uses story points and velocity directly
- `Technical Roadmap` — uses t-shirt sizing and velocity forecasts for roadmap timelines
- `Risk Management` — PERT three-point estimates are a key input to risk-based planning

**Alternatives / Comparisons:**
- `Risk Management` — PERT three-point estimation directly supports risk quantification
- `Technical Roadmap` — roadmap forecasts depend on reliable velocity data

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STORY POINTS │ Relative, Fibonacci. Use for sprints.     │
│ T-SHIRT      │ Categorical. Use for roadmap planning.    │
│ 3-POINT PERT │ (O + 4M + P) / 6. Use for high risk.     │
│ PLANNING     │ Simultaneous reveal → discuss outliers    │
│ POKER        │ → re-vote until consensus                 │
├──────────────┼───────────────────────────────────────────┤
│ FIBONACCI    │ 1, 2, 3, 5, 8, 13, 21 — each step > 2×   │
│              │ reflects uncertainty growth with size     │
├──────────────┼───────────────────────────────────────────┤
│ VELOCITY     │ Avg points/sprint over 6 sprints          │
│ FORECAST     │ Backlog pts / velocity = sprints to done  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Estimate value = conversation surfaced,   │
│              │ not number produced                       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Risk Management →                         │
│              │ Sprint Planning                           │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Planning poker is designed to prevent anchoring bias (the first estimate heard influences everyone else's). But in practice, even with simultaneous reveal, social pressure often causes the team to converge on the estimate of the most senior person or the most confident person — not necessarily the most accurate one. Design a modified estimation process that further reduces social pressure while still surfacing disagreement productively. How would you validate that your modification actually produces better estimates?

**Q2.** Your team has been tracking velocity for 8 sprints. You have been asked to forecast the delivery date for a 300-story-point roadmap item. Velocity data: [42, 38, 45, 41, 39, 44, 43, 40]. Calculate: (a) expected delivery in sprints with confidence interval, (b) what three assumptions in this forecast are most likely to be wrong, (c) how you would communicate this forecast to a non-technical VP who is expecting a specific delivery date.
