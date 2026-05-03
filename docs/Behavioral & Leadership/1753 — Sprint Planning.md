---
layout: default
title: "Sprint Planning"
parent: "Behavioral & Leadership"
nav_order: 1753
permalink: /leadership/sprint-planning/
number: "1753"
category: Behavioral & Leadership
difficulty: ★☆☆
depends_on: Scrum, Agile Principles
used_by: Scrum, Estimation Techniques, Prioritization (MoSCoW, RICE)
related: Scrum, Estimation Techniques, Retrospective
tags:
  - leadership
  - agile
  - beginner
  - scrum
  - planning
---

# 1753 — Sprint Planning

⚡ TL;DR — Sprint Planning is the Scrum event that opens each sprint — answering three questions: Why is this sprint valuable (Sprint Goal)? What can be Done this sprint (PBI selection)? How will the work be done (task breakdown)? — producing a Sprint Backlog that the development team owns and a Sprint Goal that gives the sprint coherence and provides a decision framework when the unexpected happens.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Teams start a new work cycle by picking items from a backlog with no shared objective. Engineers work independently on disconnected tasks. When a new request arrives mid-sprint, there is no framework for deciding whether to include it. At the end of the cycle, there is no coherent narrative for what was accomplished — just a list of completed tickets. Stakeholders ask "what did we ship?" and the answer is "some things from the backlog."

**THE BREAKING POINT:**
Without a planning event, work is ad-hoc and direction is unclear. Without a Sprint Goal, there is no decision criterion for trade-offs. Without capacity planning, teams consistently over-commit and under-deliver, eroding trust.

**THE INVENTION MOMENT:**
Sprint Planning was defined in the original Scrum framework by Schwaber and Sutherland (1995), formalized in the Scrum Guide (first edition 2010, updated 2011, 2013, 2016, 2017, 2020). The 2020 update simplified Sprint Planning around three questions and moved away from prescribing specific estimation techniques.

---

### 📘 Textbook Definition

**Sprint Planning (Scrum Guide 2020):** A time-boxed event (maximum 8 hours for a 4-week sprint, proportionally less for shorter sprints) that initiates the Sprint by defining: (1) the Sprint Goal (why this sprint has value), (2) the Sprint Backlog items (what can be Done), and (3) a plan for delivering the Increment (how the work will be done).

**Sprint Goal:** A single objective for the Sprint that creates coherence and focus. The Sprint Goal can be met even if some planned Product Backlog Items are not included — it is the commitment for the Sprint, not the story list.

**Sprint Backlog:** The set of Product Backlog Items selected for the Sprint plus a plan for delivering them. Owned by the development team. The Sprint Goal is fixed; the Sprint Backlog is adaptive.

**Velocity:** The team's historical average of story points (or other units) completed per sprint. Used to calibrate how much to pull into the sprint.

**Definition of Done (DoD):** The shared quality standard that defines when a PBI is complete. Sprint Planning must account for DoD requirements in the work estimate.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Sprint Planning defines what the team will accomplish this sprint (the Goal), which items serve that goal (the backlog selection), and how they'll approach the work (task breakdown).

**One analogy:**

> Sprint Planning is like planning a road trip before getting in the car. You define: where you're going (Sprint Goal), which route you'll take (selected backlog items), and what you need for the journey (task breakdown). Without planning: you get in the car, start driving, and make decisions at every junction without knowing the destination. Sprint Planning is the 1–2 hour investment that prevents 2 weeks of directionless driving.

**One insight:**
The most valuable output of Sprint Planning is not the sprint backlog — it is the Sprint Goal. A team that cannot state in one sentence what they are trying to achieve this sprint has not done Sprint Planning; they have done sprint loading. The Sprint Goal is the test at the Sprint Review: "Did we achieve the goal?" is more important than "Did we complete all the stories?"

---

### 🔩 First Principles Explanation

**THE THREE SPRINT PLANNING QUESTIONS:**

```
QUESTION 1: WHY IS THIS SPRINT VALUABLE?
  Responsibility: Product Owner proposes Sprint Goal
  Team: may negotiate to adjust
  Output: Sprint Goal — one sentence

  GOOD Sprint Goals:
    "Reduce checkout abandonment by 15%"
    "Enable enterprise SSO for the top 3 paying customers"
    "Eliminate the P0 performance regression on the mobile app"

  BAD Sprint Goals:
    "Complete all planned stories"
    "Continue feature development"
    "Implement user stories 47, 48, 49, 50, 51"

QUESTION 2: WHAT CAN BE DONE THIS SPRINT?
  Team: selects PBIs from the Product Backlog
  Guidance: velocity as historical forecast; DoD as quality floor
  Output: sprint backlog items

  CAPACITY CALCULATION:
    Sprint: 10 working days
    Team: 5 developers
    Average availability: 80% (meetings, reviews, ops)
    Effective capacity: 5 × 10 × 0.8 = 40 developer-days

    Translate to story points using historical velocity:
    If velocity = 40pt/sprint: select ~40pt of PBIs
    Buffer: don't commit 100% of capacity
    → Realistic: 35pt (leave buffer for unknowns)

QUESTION 3: HOW WILL THE WORK BE DONE?
  Developers: break selected PBIs into tasks
  Tasks: sized to ≤1 day (ideally 2–4h)
  Purpose: surface dependencies; enable daily inspection

  Note: tasks are a planning tool; they are not mandatory
        in modern Scrum. Some teams task-break; others don't.
```

**BACKLOG REFINEMENT vs SPRINT PLANNING:**

```
BACKLOG REFINEMENT (not a Scrum event; ongoing):
  Done: throughout the sprint (typically 10% of capacity)
  Purpose: ensure top-of-backlog items are:
    - Small enough to fit in a sprint
    - Clear enough to estimate
    - Estimated (story points or relative size)

  Sprint Planning breaks down if items are not refined:
    "Let's plan the sprint" → items are too large / unclear
    → Planning devolves into discovery / refinement
    → Sprint Planning runs 5h instead of 2h

  RULE: If Sprint Planning regularly takes too long,
        the team is not doing enough backlog refinement.
```

---

### 🧪 Thought Experiment

**SETUP:**
A team is starting Sprint 15. The Product Owner presents the Sprint backlog candidates. No Sprint Goal is proposed. The team picks 42 points of work. On Day 4, a critical production issue arrives requiring 8 points of work. The team has two options: (a) add it to the sprint (drop something); (b) reject it for the next sprint.

**WITHOUT A SPRINT GOAL:**
The team has no decision framework. Is the production issue more important than any of the 42 planned points? Who decides? The engineers ask the PO; the PO asks the EM; the EM makes a call; the team feels micromanaged. 1 hour spent in Slack deciding.

**WITH A SPRINT GOAL:** "Reduce checkout abandonment by 15%"
The production issue is about payment service stability — which directly affects checkout completion rate.
Team decision: "Does fixing this production issue help us achieve the Sprint Goal?" Answer: yes.
Decision: pull in the fix; drop the lowest-value story (one that was tangentially related to the goal).
Team makes the decision in 5 minutes without escalation.

**The insight:** The Sprint Goal gives the team decision authority for mid-sprint changes. It is not just a planning output — it is a mid-sprint governance mechanism.

---

### 🧠 Mental Model / Analogy

> Sprint Planning is like a pre-flight briefing for a pilot crew. Before takeoff: the crew agrees on the destination (Sprint Goal), reviews the planned route (backlog items), identifies known weather and risks (dependencies, blockers), and assigns specific roles (task ownership). The pre-flight briefing takes 20 minutes; the flight takes 8 hours. Without the briefing, the crew boards with different assumptions about the destination. Mid-flight, when ATC asks for a route change, there is no shared framework for deciding whether to accept it. The briefing is the investment that makes the flight — and mid-flight decisions — coherent.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Sprint Planning is the team meeting at the start of every sprint where you decide: what you're trying to achieve (the Sprint Goal), which tasks you'll work on (the selected backlog), and roughly how you'll approach each task. It sets up the sprint so everyone knows what success looks like.

**Level 2 — How to use it (engineer):**
Come to Sprint Planning having read the top backlog items so you can give informed estimates. Ask about the Sprint Goal if it isn't clear — "What is the one thing we're trying to achieve this sprint?" Ask about dependencies: "Does this story depend on the API contract from Team X? Is that ready?" Push back on unclear stories: if you cannot estimate it, it's not ready for the sprint. That goes back to backlog refinement.

**Level 3 — How it works (tech lead/Scrum Master):**
Your job in Sprint Planning: (1) ensure a real Sprint Goal is defined before any story selection; (2) facilitate capacity calculation — don't let the team commit to more than ~85% of velocity; (3) surface dependencies during task breakdown: "This story depends on the auth service — who is the contact? Is the API ready?"; (4) time-box the event — if you're 4h in and still refining stories, stop and move unrefined stories back to the backlog. Sprint Planning is not the time for discovery.

**Level 4 — Why it was designed this way (principal/staff):**
Sprint Planning is a coordination mechanism for aligning the team around a shared objective with minimal management overhead. The Sprint Goal is designed to give the team sufficient autonomy to make mid-sprint decisions without escalation — a team with a clear Sprint Goal can self-manage trade-offs; a team without one requires constant management intervention. The time-box (8 hours max) is designed to create pressure to arrive prepared (refined backlog) rather than using planning time for discovery. At the staff level, the key insight is that the quality of Sprint Planning is a lagging indicator of backlog health: teams with well-refined backlogs have fast, clear Sprint Planning; teams with poor backlogs have long, chaotic Sprint Planning. Invest in backlog refinement; Sprint Planning will follow.

---

### ⚙️ How It Works (Mechanism)

```
PRE-REQUISITES (before Sprint Planning):
  □ Top backlog items refined, estimated, and ordered
  □ Previous sprint retrospective complete
  □ Team knows their velocity (3-sprint average)
  □ PO has prepared Sprint Goal draft
    ↓
SPRINT PLANNING (time-boxed):

Part 1: WHY (15–30 min)
  PO presents: "Here is the proposed Sprint Goal: [X]"
  Team discusses; refines; agrees on Sprint Goal
    ↓
Part 2: WHAT (1–2h)
  Team selects PBIs that serve the Sprint Goal
  Team uses velocity to calibrate quantity
  Team clarifies any unclear items (not full refinement)
    ↓
Part 3: HOW (remaining time)
  Developers break selected PBIs into tasks
  Surface dependencies; assign initial owners
  Identify known risks or blockers
    ↓
OUTPUT:
  Sprint Goal (fixed)
  Sprint Backlog (PBIs + tasks)
  Shared plan for the sprint
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Sprint N ends
    ↓
Sprint Retrospective (Sprint N)
    ↓
[SPRINT PLANNING ← YOU ARE HERE]
Sprint Goal defined
PBIs selected from refined backlog
Tasks created; dependencies mapped
    ↓
Sprint N+1 begins
    ↓
Daily Scrum: adapt Sprint Backlog
    ↓
Sprint Review: inspect Increment; get feedback
    ↓
Sprint Retrospective: plan process improvements
    ↓
Backlog refined during sprint
    ↓
[Next Sprint Planning begins]
```

---

### 💻 Code Example

**Sprint Planning capacity calculator:**

```python
from dataclasses import dataclass

@dataclass
class SprintCapacity:
    team_size: int
    sprint_days: int
    availability_pct: float   # 0.0–1.0; accounts for meetings/ops
    velocity_history: list[int]  # last N sprints

    @property
    def effective_dev_days(self) -> float:
        return self.team_size * self.sprint_days * self.availability_pct

    @property
    def avg_velocity(self) -> float:
        return sum(self.velocity_history) / len(self.velocity_history)

    @property
    def recommended_commitment(self) -> int:
        # Commit to 85% of average velocity to leave buffer
        return int(self.avg_velocity * 0.85)

    def plan_summary(self) -> str:
        return (
            f"Team: {self.team_size} devs × {self.sprint_days} days "
            f"× {self.availability_pct:.0%} = "
            f"{self.effective_dev_days:.0f} dev-days\n"
            f"Avg velocity: {self.avg_velocity:.0f}pt "
            f"(over {len(self.velocity_history)} sprints)\n"
            f"Recommended commitment: {self.recommended_commitment}pt "
            f"(85% of velocity)"
        )

capacity = SprintCapacity(
    team_size=5,
    sprint_days=10,
    availability_pct=0.80,
    velocity_history=[40, 38, 42, 36, 44],
)
print(capacity.plan_summary())
```

---

### ⚖️ Comparison Table

| Element          | Sprint Planning              | Backlog Refinement               |
| ---------------- | ---------------------------- | -------------------------------- |
| **When**         | Start of sprint              | Ongoing throughout sprint        |
| **Duration**     | Time-boxed (max 8h/4-week)   | Typically 10% of sprint capacity |
| **Output**       | Sprint Goal + Sprint Backlog | Refined, estimated, ordered PBIs |
| **Participants** | Full Scrum team              | PO + part of dev team            |
| **Focus**        | Commitment for this sprint   | Readiness for future sprints     |

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                                      |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Sprint Planning is where we discover what stories mean"    | Discovery should happen in backlog refinement. If Sprint Planning is being used for discovery, the backlog is not refined.                                   |
| "Commit to 100% of velocity every sprint"                   | Teams should commit to 80–85% of velocity. 100% commitment leaves no buffer for unexpected work, which always exists.                                        |
| "The Sprint Backlog cannot change after Planning"           | The Sprint Goal cannot change. The Sprint Backlog can and should change daily as the team learns.                                                            |
| "Sprint Planning is the PO telling the team what to do"     | Sprint Planning is collaborative. The PO proposes the Goal; the team negotiates the scope. The team has full authority over the plan for achieving the Goal. |
| "Longer sprints need proportionally longer Sprint Planning" | A 4-week sprint's Sprint Planning is 8h max; a 2-week sprint's is 4h max. Sprint Planning duration scales with sprint length.                                |

---

### 🚨 Failure Modes & Diagnosis

**Chronic Over-Commitment — Sprint Goal Missed Every Sprint**

**Symptom:** The team consistently commits to 45+ points when velocity is 38. Every sprint ends with 5–10 points rolled over. The PO is frustrated. The team feels like they're always behind. Sprint velocity calculations include rolled-over stories from last sprint, inflating apparent progress.

**Root Cause:** Velocity is not used as a ceiling; it is used as a target to beat. The team (or PO) believes committing to more will produce more. Social pressure to appear productive overrides realistic planning.

**Fix:**

```
1. EXPOSE THE PATTERN:
   → Show the last 6 sprints: committed vs. completed
   → "We've missed our Sprint Goal 5 of 6 sprints."
   → "Over-commitment is the consistent cause."

2. ENFORCE THE 85% RULE:
   → Next Sprint Planning: commit = 85% × 3-sprint velocity
   → If PO pushes back: "More commitment hasn't produced
     more delivery — let's try committing less and
     delivering it reliably for 3 sprints."

3. COUNT ONLY COMPLETED STORIES IN VELOCITY:
   → Rolled-over stories: count only in the sprint they complete
   → This reveals true velocity; prevents false-high planning

4. CELEBRATE COMPLETION:
   → If sprint ends with all stories Done AND buffer remaining:
     that is SUCCESS, not laziness
   → Recognise reliable delivery as a team achievement
   → Reinforces: committing to complete > committing to impress
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Scrum` — Sprint Planning is one of Scrum's five events
- `Agile Principles` — iterative planning implements the agile manifesto's planning principles

**Builds On This (learn these next):**

- `Scrum` — the full Scrum framework Sprint Planning lives within
- `Estimation Techniques` — the techniques used to size PBIs during Sprint Planning
- `Retrospective` — the event that informs how the next Sprint Planning should change

**Alternatives / Comparisons:**

- `Estimation Techniques` — the toolset for story point estimation in Sprint Planning
- `Kanban` — an alternative approach that doesn't use sprint-based planning

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ 3 QUESTIONS │ Why? (Sprint Goal)                         │
│             │ What? (selected PBIs)                      │
│             │ How? (task breakdown)                      │
├─────────────┼──────────────────────────────────────────-─┤
│ SPRINT GOAL │ One sentence. "Reduce abandonment by 15%"  │
│             │ NOT "complete all planned stories"         │
├─────────────┼──────────────────────────────────────────-─┤
│ CAPACITY    │ Team × sprint days × availability × 0.85   │
│ COMMIT      │ Target ~85% of avg velocity, not 100%     │
├─────────────┼──────────────────────────────────────────-─┤
│ TIME-BOX    │ 2-week sprint: 4h max                     │
│             │ 4-week sprint: 8h max                      │
├─────────────┼──────────────────────────────────────────-─┤
│ PRE-CONDITION│ Backlog must be refined BEFORE planning   │
│             │ If not: sprint planning becomes refinement │
├─────────────┼──────────────────────────────────────────-─┤
│ NEXT EXPLORE│ Retrospective →                           │
│             │ Estimation Techniques                     │
└─────────────┴────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The 2020 Scrum Guide says the Sprint Goal "creates coherence and focus, encouraging the Scrum Team to work together rather than on separate initiatives." Yet most teams write Sprint Goals as summaries of the stories ("Complete auth, payments, and reporting features"). Design a Sprint Goal writing workshop for a team that consistently writes poor Sprint Goals. What prompts, exercises, and examples would you use? How would you evaluate whether the resulting Sprint Goals are good quality?

**Q2.** Your team's Sprint Planning consistently runs 5–6 hours for 2-week sprints (should be ≤4h). You observe: the first 2 hours are spent debating whether items are ready; the next 2 hours are estimates discussion; the last 1–2 hours are task breakdown. The PO says "we have to plan well." Engineers are exhausted by Sprint Planning. Diagnose the root causes and design a process change that reduces Sprint Planning to 3h without sacrificing quality. What would you change in the week before Sprint Planning? What would you change in the Sprint Planning format itself?
