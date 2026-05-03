---
layout: default
title: "Scrum"
parent: "Behavioral & Leadership"
nav_order: 1751
permalink: /leadership/scrum/
number: "1751"
category: Behavioral & Leadership
difficulty: ★☆☆
depends_on: Agile Principles, Sprint Planning
used_by: Sprint Planning, Retrospective, Agile Principles
related: Agile Principles, Kanban, Sprint Planning
tags:
  - leadership
  - agile
  - beginner
  - scrum
  - process
---

# 1751 — Scrum

⚡ TL;DR — Scrum is an agile framework for developing complex products through iterative, time-boxed sprints (1–4 weeks) with three roles (Product Owner, Scrum Master, Development Team), five events (Sprint, Sprint Planning, Daily Scrum, Sprint Review, Sprint Retrospective), and three artefacts (Product Backlog, Sprint Backlog, Increment) — providing a lightweight structure for empirical process control based on transparency, inspection, and adaptation.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without a shared delivery framework, teams fall into one of two traps: (1) no process — ad-hoc task assignment, unclear priorities, no rhythm, no reflection; or (2) waterfall — plan everything upfront, build for months, integrate at the end, discover all the problems at once. Scrum provides a middle path: enough structure to create predictability and coordination, not so much that it eliminates flexibility and learning.

**THE BREAKING POINT:**
Teams building complex, novel products cannot know everything upfront. They need a framework that allows them to: make commitments short enough to be reliable (sprints), inspect progress with enough frequency to course-correct (reviews), and improve their process continuously (retrospectives). Scrum is the operationalisation of these needs.

**THE INVENTION MOMENT:**
Ken Schwaber and Jeff Sutherland presented Scrum at OOPSLA 1995, drawing on earlier work by Takeuchi and Nonaka (1986) who described rugby-style team product development. The Scrum Guide (maintained by Schwaber and Sutherland) is the official reference, most recently updated in 2020.

---

### 📘 Textbook Definition

**Three Roles (2020 Scrum Guide: "Scrum Team"):**

- **Product Owner (PO):** Accountable for maximising value of the product. Owns and manages the Product Backlog — ordering items by value, ensuring clarity.
- **Scrum Master (SM):** Accountable for establishing Scrum as defined in the Scrum Guide. Serves the team, PO, and organisation by removing impediments, facilitating events, and promoting Scrum understanding.
- **Developers:** Accountable for creating a usable Increment each Sprint. Self-organising; cross-functional.

**Five Events:**

- **The Sprint:** Time-box of up to 4 weeks; a consistent cadence during which Scrum events occur and a Done Increment is created
- **Sprint Planning:** Plan the Sprint — what can be Done and how
- **Daily Scrum:** 15-minute daily inspection of progress toward Sprint Goal; adapt Sprint Backlog as needed
- **Sprint Review:** Inspect the Sprint Increment; adapt Product Backlog
- **Sprint Retrospective:** Plan improvements to quality and effectiveness

**Three Artefacts:**

- **Product Backlog:** Ordered list of everything that might be needed to improve the product; sole source of work; owned by PO
- **Sprint Backlog:** Sprint Goal + selected Product Backlog items + plan for delivering the Increment
- **Increment:** Concrete step toward the Product Goal; must be Done; usable; potentially releasable

**Definition of Done (DoD):** Formal description of the state of the Increment when it meets the quality measures required. Creates shared understanding of completion.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Scrum is a time-boxed iterative framework — plan a sprint, build it, review it with users, reflect on the process, repeat — creating a regular cadence of delivery, inspection, and improvement.

**One analogy:**

> Scrum is like a sports season compressed into 2-week cycles. Each game (sprint) has preparation (planning), gameplay (development), post-game analysis (review), and coaching session (retrospective). The team gets better with each game because they review what worked and what didn't. The schedule is fixed (2 weeks); the play selection within each game adapts to what the opponent (the user problem) does.

**One insight:**
The Sprint Goal — a single objective that gives the Sprint coherence — is the most underused element of Scrum. Teams that plan a sprint as a list of disconnected stories without a Sprint Goal have no basis for making trade-off decisions mid-sprint. "Does this help us achieve the Sprint Goal?" is the question that allows teams to drop a story, add a story, or pivot when something unexpected happens.

---

### 🔩 First Principles Explanation

**EMPIRICAL PROCESS CONTROL — 3 PILLARS:**

```
TRANSPARENCY:
  All aspects of Scrum visible to those responsible
  for outcomes. Product Backlog, Sprint Backlog, Increment,
  Definition of Done — all visible and understood.

INSPECTION:
  Scrum artefacts and progress inspected at the right
  frequency to detect problems. Daily Scrum: daily inspection
  of Sprint progress. Sprint Review: inspection of Increment.
  Retrospective: inspection of process.

ADAPTATION:
  When inspection reveals deviation: adjust as soon as
  possible. Sprint Backlog adapted daily. Product Backlog
  adapted after Sprint Review. Process adapted after
  Retrospective.
```

**THE SPRINT:**

```
Sprint boundary     Sprint boundary
|                                  |
|←─────────── 1–4 weeks ──────────→|
|                                  |
Sprint Planning ──→ Daily Scrum (×14) ──→ Sprint Review
                                     ──→ Sprint Retrospective

KEY RULES:
  - Sprint length is fixed and consistent
  - No changes that endanger Sprint Goal
  - Quality (DoD) does not decrease
  - Backlog refined as needed
  - Sprint can be cancelled if Sprint Goal becomes obsolete
    (PO authority only)
```

**PRODUCT BACKLOG MANAGEMENT:**

```
Product Goal
  └─ Epic
       └─ Feature
            └─ User Story / PBI (Product Backlog Item)
                 └─ Task (Sprint Backlog level)

PBI characteristics (INVEST):
  I ndependent
  N egotiable
  V aluable
  E stimable
  S mall
  T estable

Backlog refinement (not a Scrum event, but needed):
  Ongoing activity; typically 10% of sprint capacity
  Purpose: ensure top items are small, clear, estimated
           before Sprint Planning
```

---

### 🧪 Thought Experiment

**SETUP:**
A team has been "doing Scrum" for 6 months. Velocity averages 42 points. The Sprint Review is attended by the PO and Scrum Master; no users. The Retrospective produces 5 action items per sprint; 0 are completed. The Definition of Done says "code merged" but not "tested in staging." Sprint Goals are written as "complete the stories in the sprint backlog."

**Diagnosis against Scrum principles:**

1. No real Sprint Goal: "complete the stories" is not a goal — it's a task list. The team has no basis for trade-off decisions mid-sprint.

2. Sprint Review without users: the event's purpose is to inspect the Increment and get feedback. Without users or stakeholders, it's a demo to people already involved. Value: near zero.

3. Retrospective action items not completed: the adaptation pillar is broken. The team inspects (retrospective) but never adapts (action items). The ceremony exists; the improvement loop does not.

4. Definition of Done: "code merged" is not Done. An Increment that isn't tested is not a usable Increment. The transparency pillar is broken — the team believes they're done when they're not.

**What this team actually has:** A sprint cadence. Not Scrum. They have the ceremonies without the empirical process control pillars.

**The fix:** Start with one thing — a real Sprint Goal for the next sprint. "Reduce checkout abandonment by 10%" is a Sprint Goal. Select stories that serve it. During the sprint: "Does this work help us reduce checkout abandonment?" becomes the decision criterion.

---

### 🧠 Mental Model / Analogy

> Scrum's three pillars (Transparency, Inspection, Adaptation) are the control loop of a thermostat. Transparency: the thermostat has a visible current temperature reading (= the team has a visible Increment and backlog). Inspection: the thermostat compares current temperature to target (= the team reviews their Increment against the Product Goal). Adaptation: the thermostat adjusts the heating/cooling system (= the team adapts their backlog and process). A thermostat without a visible temperature readout (no transparency) cannot inspect. A thermostat that doesn't adjust output (no adaptation) wastes energy inspecting. Scrum is only functional when all three pillars are intact.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Scrum is a way of organising a software team's work into 2-week cycles (sprints). Each sprint: plan what you'll do, do it, show it to stakeholders, and discuss how to improve. Then repeat. It creates a steady rhythm of delivery and improvement.

**Level 2 — How to use it (engineer):**
In Daily Scrum: share what you did since last Scrum, what you'll do before the next, and any impediments. Update the Sprint Backlog with the actual state (not what you committed; what you actually have). In Sprint Planning: understand the Sprint Goal, not just the story list — the Goal is what you optimise for if the sprint goes sideways. In Retrospective: propose one specific process change, not a vague "communicate better."

**Level 3 — How it works (tech lead or Scrum Master):**
The Scrum Master's highest-leverage actions: (1) protect the Sprint Goal from mid-sprint scope creep — new requests go to the Product Backlog, not into the current sprint; (2) facilitate retrospectives that produce completed action items, not just lists; (3) coach the PO on backlog ordering by value, not by requester seniority. The most common Scrum failure mode is the PO ordering the backlog by stakeholder priority rather than user value.

**Level 4 — Why it was designed this way (principal/staff):**
Scrum's design reflects a core epistemological principle: complex problems cannot be fully understood upfront, so the framework must create frequent opportunities for learning and adaptation. The sprint boundary is the forcing function: it requires the team to produce a Done Increment on a fixed cadence, which creates the discipline of finishing rather than starting. The roles are minimal by design — three roles is enough to separate the what (PO), the how-we-work (SM), and the how-we-build (developers). More roles create organisational complexity that slows adaptation. At the staff level, the question is not "are we doing Scrum correctly" but "is Scrum serving our goals?" For some contexts (mature product, stable requirements, operations work), Scrum is the wrong framework. Knowing when to apply Scrum vs. Kanban vs. no framework requires understanding the problem the framework solves.

---

### ⚙️ How It Works (Mechanism)

```
SCRUM CADENCE:

Sprint Planning (up to 8h/4-week sprint)
  → Topic 1: Why is this Sprint valuable? (Sprint Goal)
  → Topic 2: What can be Done this Sprint? (PBI selection)
  → Topic 3: How will the work be done? (tasks created)
  OUTPUT: Sprint Backlog + Sprint Goal
    ↓
Daily Scrum (15 min, same time, same place)
  → Progress toward Sprint Goal?
  → Plan for next 24h
  → Impediments?
  OUTPUT: Adapted Sprint Backlog
    ↓
Sprint Review (up to 4h/4-week sprint)
  → Demonstrate Increment to stakeholders + users
  → Discuss progress toward Product Goal
  → Adapt Product Backlog
  OUTPUT: Adapted Product Backlog
    ↓
Sprint Retrospective (up to 3h/4-week sprint)
  → What went well?
  → What could be improved?
  → Commit to 1–3 improvements
  OUTPUT: Sprint improvements; possibly updated DoD
    ↓
[NEXT SPRINT BEGINS]
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Product Goal established
    ↓
Product Backlog created and refined
    ↓
Sprint Planning → Sprint Goal + Sprint Backlog
    ↓
[SCRUM ← YOU ARE HERE]
Daily: inspect + adapt Sprint Backlog
    ↓
Sprint end: Done Increment
    ↓
Sprint Review: stakeholder feedback → Product Backlog updated
    ↓
Sprint Retrospective: process improvement committed
    ↓
Repeat until Product Goal met or product discontinued
```

---

### 💻 Code Example

**Sprint tracker (minimal Scrum artefact model):**

```python
from dataclasses import dataclass, field
from enum import Enum

class Status(Enum):
    TODO       = "To Do"
    IN_PROGRESS = "In Progress"
    DONE       = "Done"

@dataclass
class BacklogItem:
    title: str
    points: int
    status: Status = Status.TODO

@dataclass
class Sprint:
    number: int
    goal: str
    items: list[BacklogItem] = field(default_factory=list)

    @property
    def velocity(self) -> int:
        return sum(i.points for i in self.items
                   if i.status == Status.DONE)

    @property
    def committed_points(self) -> int:
        return sum(i.points for i in self.items)

    @property
    def completion_pct(self) -> float:
        if not self.committed_points:
            return 0.0
        return round(self.velocity / self.committed_points * 100, 1)

    def summary(self) -> str:
        return (
            f"Sprint {self.number}: {self.goal}\n"
            f"  Committed: {self.committed_points}pt | "
            f"  Done: {self.velocity}pt | "
            f"  Complete: {self.completion_pct}%"
        )

sprint = Sprint(
    number=12,
    goal="Reduce checkout abandonment by 10%",
    items=[
        BacklogItem("One-page checkout flow", 5, Status.DONE),
        BacklogItem("Payment latency optimisation", 3, Status.DONE),
        BacklogItem("Guest checkout option", 5, Status.IN_PROGRESS),
        BacklogItem("Analytics instrumentation", 2, Status.TODO),
    ]
)
print(sprint.summary())
```

---

### ⚖️ Comparison Table

| Framework    | Cadence                                   | Roles                | Best For                                               |
| ------------ | ----------------------------------------- | -------------------- | ------------------------------------------------------ |
| **Scrum**    | Fixed sprints (1–4 weeks)                 | PO / SM / Developers | Predictable delivery; teams with discrete feature work |
| **Kanban**   | Continuous flow                           | No defined roles     | Ops, support, unpredictable work; mature teams         |
| **XP**       | Weekly iterations + engineering practices | No specific roles    | High-tech quality emphasis; TDD, pairing               |
| **SAFe**     | PI (10–14 weeks) + sprint cadence         | Many roles           | Large-scale multi-team coordination                    |
| **Scrumban** | Hybrid: sprint cadence + Kanban WIP       | Hybrid               | Transitioning from Scrum; maintenance + feature        |

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                   |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Daily Scrum is a status meeting for the manager" | Daily Scrum is a planning event for the Developers. Managers do not facilitate or direct it. The SM ensures it happens, not that they run it.             |
| "Velocity is a performance metric"                | Velocity is a forecasting tool. Using it as a performance metric incentivises story point inflation and destroys its utility.                             |
| "Scrum Master is a project manager"               | The SM is a servant-leader for the team and PO. They remove impediments; they do not assign tasks, own the schedule, or report status to management.      |
| "The Sprint backlog is fixed once planning ends"  | The Sprint Backlog is owned by the Developers and adapted daily. Only the Sprint Goal is fixed; the plan for achieving it evolves.                        |
| "Scrum requires co-location"                      | Scrum works with distributed teams. The Daily Scrum can be async; events can be run remotely. The 2020 Scrum Guide removed all references to co-location. |

---

### 🚨 Failure Modes & Diagnosis

**Sprint Goal Absence — The Story-List Sprint**

**Symptom:** Sprint Planning produces a list of stories totalling ~40 points. The "Sprint Goal" is written as "Complete all planned stories." Mid-sprint, a new urgent request arrives. The team has no framework for deciding whether to include it — they either refuse all change (rigid) or accept all change (chaotic). At Review, the team demos each story independently; there is no coherent narrative of what the sprint achieved.

**Root Cause:** The Sprint Goal is treated as a box to check, not as the organising objective of the sprint. Without a real goal, the sprint is a bag of tasks rather than a coherent unit of value.

**Fix:**

```
NEXT SPRINT PLANNING:
  Step 1 (before selecting stories):
  "What is the one thing we want to achieve this sprint
   that is valuable to the product goal?"
  → PO answers; team refines

  Step 2: Select stories that serve the Sprint Goal
  → "Does this story help us achieve [the Goal]?"
  → Stories that don't serve the Goal: move to backlog

  Step 3: Sprint Goal test at Review:
  "Did we achieve the Sprint Goal?"
  This is the primary Review question — not "did we complete
  all the stories?"

  Mid-sprint change evaluation:
  "Does this new request help us achieve the Sprint Goal?
   More than what we'd have to drop to add it?"
  → This is the decision framework the goal provides
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Agile Principles` — Scrum implements agile principles; understanding the principles explains the design choices
- `Sprint Planning` — Scrum's most important planning event

**Builds On This (learn these next):**

- `Sprint Planning` — detailed mechanics of the Sprint Planning event
- `Retrospective` — the Scrum event for process improvement
- `Kanban` — the primary alternative to sprint-based agile

**Alternatives / Comparisons:**

- `Kanban` — continuous flow vs. sprint cadence
- `Agile Principles` — the underlying values that Scrum operationalises

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ROLES       │ Product Owner | Scrum Master | Developers  │
├─────────────┼───────────────────────────────────────────-┤
│ EVENTS      │ Sprint | Planning | Daily | Review | Retro │
├─────────────┼──────────────────────────────────────────-─┤
│ ARTEFACTS   │ Product Backlog | Sprint Backlog | Increment│
├─────────────┼──────────────────────────────────────────-─┤
│ 3 PILLARS   │ Transparency | Inspection | Adaptation     │
├─────────────┼──────────────────────────────────────────-─┤
│ SPRINT GOAL │ The ONE objective giving the sprint        │
│             │ coherence. "Complete all stories" ≠ goal.  │
├─────────────┼──────────────────────────────────────────-─┤
│ DOD         │ Formal shared definition of "Done"         │
│             │ "Merged" alone is NOT done.                │
├─────────────┼──────────────────────────────────────────-─┤
│ NEXT EXPLORE│ Kanban → Sprint Planning                   │
└─────────────┴────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The 2020 Scrum Guide removed the specific "three questions" from the Daily Scrum (what did I do yesterday, what will I do today, what are my blockers). Why might this change have been made? What is the risk of the three-question format? Design an alternative Daily Scrum structure that better serves the stated purpose ("inspect progress toward the Sprint Goal and adapt the Sprint Backlog as needed").

**Q2.** Your team's velocity has been stable at 40 points/sprint for 4 months. The PO wants to commit to an external delivery date 8 sprints from now. The current backlog for this commitment contains 360 points. Assume velocity variance of ±20%. (a) Calculate the probability that 360 points will be completed in 8 sprints. (b) What backlog size would give you 80% confidence of delivery in 8 sprints? (c) How do you communicate the schedule risk to the PO, and what options do you present?
