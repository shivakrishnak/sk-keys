---
layout: default
title: "Kanban"
parent: "Behavioral & Leadership"
nav_order: 1752
permalink: /leadership/kanban/
number: "1752"
category: Behavioral & Leadership
difficulty: ★☆☆
depends_on: Agile Principles, Scrum
used_by: Agile Principles, Sprint Planning
related: Scrum, Agile Principles, Sprint Planning
tags:
  - leadership
  - agile
  - beginner
  - kanban
  - flow
---

# 1752 — Kanban

⚡ TL;DR — Kanban is a flow-based work management system that limits work-in-progress (WIP), visualises workflow, and measures cycle time and throughput to optimise the continuous delivery of value — without fixed sprints or prescribed roles — making it especially suited to operational, maintenance, and support work where demand is unpredictable and continuous rather than project-based.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A platform team handles a mix of feature work, bug fixes, infrastructure requests, and on-call escalations. The team tries to use Scrum sprints. Every sprint planning is a negotiation between the planned feature work and the flood of unplanned requests. Every sprint ends with incomplete work rolled over into the next sprint. Velocity is meaningless. Sprint commitments are fiction. The team is context-switching constantly because 15 items are "in progress" simultaneously, none of them finishing.

**THE BREAKING POINT:**
Scrum's time-box works when work is predictable and discrete. When work is continuous (operations, bug fixing, support, infrastructure) and unpredictable (incidents, urgent escalations), the sprint model creates artificial urgency and commitments that cannot be kept. Kanban addresses the actual problem: too much work started, not enough finished.

**THE INVENTION MOMENT:**
Kanban originates in Toyota's production system (1940s–1950s) — "kanban" (看板) means "signboard" or "visual card" in Japanese. David Anderson adapted it for software development ("Kanban: Successful Evolutionary Change for Your Technology Business," 2010), introducing WIP limits, flow metrics, and the "start with what you do now" principle.

---

### 📘 Textbook Definition

**Kanban board:** Visual representation of workflow states (columns) and work items (cards). Typical columns: Backlog → Ready → In Progress → Review → Done. Work items flow left to right; columns represent workflow stages.

**WIP Limit (Work In Progress Limit):** Maximum number of items allowed in a workflow stage simultaneously. When a column is at its WIP limit, team members cannot start new work in that stage — they must help finish existing items before starting new ones. This is the core mechanism that prevents multitasking overload.

**Cycle time:** Time from when a work item is started (moved to In Progress) to when it is Done. The primary metric for flow efficiency.

**Throughput:** Number of items completed per time unit (e.g., items/week). Throughput and cycle time are inversely related under Little's Law: WIP = Throughput × Cycle Time.

**Little's Law:** `WIP = Throughput × Cycle Time`. If WIP increases while throughput stays constant, cycle time increases. Reducing WIP is the lever for reducing cycle time (faster delivery).

**Pull system:** Work is "pulled" from the previous stage when there is capacity, rather than "pushed" by managers. When the In Progress column has space (under WIP limit), the team pulls the next Ready item.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Kanban limits how much work is started at once, visualises the flow of work, and measures cycle time — so the team finishes things faster by starting fewer things at a time.

**One analogy:**

> Kanban WIP limits are like a restaurant kitchen. A kitchen that takes all orders simultaneously and starts cooking all of them produces chaos: 40 half-finished dishes, cold food, wrong orders. A kitchen that limits active orders (WIP limit: 8 tickets) finishes dishes quickly, in order, at consistent quality. When a table of food is delivered (item Done), the kitchen pulls the next ticket. The WIP limit is not a constraint on the kitchen's capacity — it is the mechanism that makes the kitchen deliver finished food rather than started food.

**One insight:**
The counterintuitive power of Kanban is that doing less simultaneously produces more. Teams that limit WIP initially feel slower — fewer items "in progress" feels like less output. But they finish items faster (lower cycle time) and context-switch less, producing higher throughput. The items they "aren't starting" are the ones that would otherwise sit half-finished for weeks, blocking other work.

---

### 🔩 First Principles Explanation

**WIP LIMITS AND LITTLE'S LAW:**

```
Little's Law: WIP = Throughput × Cycle Time
  Rearranged: Cycle Time = WIP / Throughput

SCENARIO A (high WIP):
  WIP = 20 items
  Throughput = 5 items/week
  Cycle Time = 20/5 = 4 weeks per item

SCENARIO B (low WIP — Kanban):
  WIP = 8 items
  Throughput = 5 items/week (same team!)
  Cycle Time = 8/5 = 1.6 weeks per item

RESULT:
  Same team; same throughput; same capacity.
  Cutting WIP from 20 to 8 reduces cycle time
  from 4 weeks to 1.6 weeks.

  Items are delivered 2.5× faster by doing fewer things
  at once. This is the mathematical basis for Kanban.
```

**KANBAN BOARD DESIGN:**

```
Backlog | Ready | In Progress (WIP:4) | Review (WIP:2) | Done
─────────────────────────────────────────────────────────────
[card]   [card]    [card]               [card]
[card]   [card]    [card]               [card]
[card]   [card]    [card]             ← WIP limit: 2
         [card]    [card]             ← Column full!
                 ← WIP limit: 4       Team cannot start
                   Column full!       new review until
                   Team cannot        a done item clears
                   start new work
                   until a slot opens

BLOCKED STATE:
  If In Progress is full and nobody can pull from Ready:
  → Team identifies bottleneck (Review is full)
  → Help review existing items rather than starting new work
  → This is the "stop starting; start finishing" principle
```

**KANBAN METRICS:**

```
CYCLE TIME (delivery speed):
  Definition: time from In Progress → Done
  Target: as low as possible; consistent
  Tool: cumulative flow diagram; scatter plot

THROUGHPUT (delivery volume):
  Definition: items completed per time unit
  Use: forecasting: "How many items can we complete in 4 weeks?"
  More reliable than story points for forecasting

WIP (current load):
  Definition: items currently in flight
  High WIP + slow cycle time = bottleneck

FLOW EFFICIENCY:
  % of cycle time the item is actively worked on (vs. waiting)
  Most teams: 15–25% flow efficiency
  Kanban target: maximise by reducing wait states
```

---

### 🧪 Thought Experiment

**SETUP:**
A team is working on 12 items simultaneously. Average cycle time: 6 weeks. Throughput: 2 items/week. The team implements Kanban with WIP limit of 5.

**Week 1:** Team is uncomfortable. Only 5 items in progress. Some engineers feel idle.
**Engineers' response:** The "idle" engineers help pull blocked items through review. Items that were waiting 2 weeks for review now clear in 2 days.
**Week 3:** First 5 items are Done. Cycle time: 3 weeks. Throughput: 2 items/week (same!).
**Week 6:** Cycle time stable at 2–3 weeks. Stakeholders notice: requests are being completed in 3 weeks, not 6.
**Week 8:** Team identifies a bottleneck: Review column reaches its WIP limit frequently. Root cause: only one engineer doing review. Solution: pair-review; second engineer learns the domain.
**Week 12:** Cycle time: 1.5 weeks. Throughput: 3 items/week (improved — less context switching).

**The insight:** The WIP limit revealed the bottleneck (review). The bottleneck was invisible before because work was spreading across 12 items and nobody noticed that review was the constraint. Little's Law confirmed: lower WIP → lower cycle time → faster delivery of each item.

---

### 🧠 Mental Model / Analogy

> Kanban manages work flow the way a highway manages traffic. A highway with no speed limit or lane controls has maximum "cars started" — everyone enters at full speed. At high density, all cars slow to a crawl; nobody arrives quickly. Traffic management (speed limits, ramp metering — the WIP limit) reduces the number of cars on the highway simultaneously. Each car moves at highway speed; total throughput increases even though fewer cars are "in the system" at once. Ramp metering is the pull system: cars enter the highway only when there is capacity, rather than flooding in when there is not. The result: faster average delivery per car, even with fewer cars in motion simultaneously.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Kanban is a way of managing work where you: put your tasks on a board (visual), limit how many tasks you work on at once (WIP limits), and measure how fast work moves from start to finish (cycle time). The key idea: finish things faster by starting fewer things at once.

**Level 2 — How to use it (engineer):**
When a column on your Kanban board is at its WIP limit: don't start new work. Look at what is in that column and what's blocking it. Can you help move it to Done? When you have a choice between two tasks: choose the one closest to Done. "Stop starting; start finishing." Your personal WIP limit for In Progress should probably be 1–2 items.

**Level 3 — How it works (tech lead):**
Set WIP limits based on observation: start with team size × 1.5 for In Progress. Watch where work piles up — that column's WIP limit is hitting a real bottleneck. The bottleneck is the constraint: fix the bottleneck (by adding capacity, improving the process, or removing blockers) rather than speeding up non-bottleneck steps. Use throughput (items/week) for forecasting, not story points. "At current throughput, this 30-item roadmap takes 10 weeks."

**Level 4 — Why it was designed this way (principal/staff):**
Kanban's design reflects the Theory of Constraints (Goldratt, "The Goal"): every system has exactly one bottleneck that constrains throughput. Optimising non-bottleneck steps does not improve system throughput — it just increases WIP at the bottleneck. The WIP limit makes the bottleneck visible (the clogged column). The pull system prevents overloading non-bottleneck steps. At the staff level, Kanban's most important insight is not the board — it is the discipline of flow management: making work visible, measuring cycle time and throughput, and systematically addressing bottlenecks. These principles apply whether you are running a formal Kanban system or just thinking about how work flows through an organisation.

---

### ⚙️ How It Works (Mechanism)

```
KANBAN FLOW:

New work arrives → Backlog
    ↓
Team pull-ready item when capacity exists
  (Ready column — items refined and estimated)
    ↓
Item starts → In Progress (WIP limit enforced)
    ↓
Item completed → Review (WIP limit enforced)
    ↓
Review complete → Done
    ↓
Cycle time measured: In Progress start → Done

BOTTLENECK IDENTIFICATION:
  Column that is consistently full at WIP limit
  = the bottleneck

  Fix: reduce WIP in upstream stages;
       add capacity or improve process at bottleneck;
       do NOT add more work to non-bottleneck stages
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Work request arrives
    ↓
Added to Backlog; prioritised
    ↓
Refined (ready to start); moved to Ready column
    ↓
Team pulls item when In Progress has capacity
    ↓
[KANBAN ← YOU ARE HERE]
Work flows through stages with WIP limits enforced
    ↓
Bottlenecks visible as full columns
    ↓
Team addresses bottleneck (helps unblock)
    ↓
Item Done; cycle time recorded
    ↓
Throughput and cycle time reviewed at cadence
    ↓
WIP limits adjusted; process improved
```

---

### 💻 Code Example

**Kanban flow simulator:**

```python
from collections import defaultdict
from dataclasses import dataclass, field

@dataclass
class KanbanItem:
    id: str
    title: str

@dataclass
class KanbanColumn:
    name: str
    wip_limit: int
    items: list[KanbanItem] = field(default_factory=list)

    @property
    def is_full(self) -> bool:
        return len(self.items) >= self.wip_limit

    def can_accept(self) -> bool:
        return not self.is_full

    def pull_from(self, source: "KanbanColumn") -> bool:
        """Pull one item from source column if capacity exists."""
        if self.can_accept() and source.items:
            item = source.items.pop(0)
            self.items.append(item)
            print(f"  Pulled '{item.title}' → {self.name}")
            return True
        elif self.is_full:
            print(f"  ⚠  {self.name} at WIP limit "
                  f"({self.wip_limit}) — bottleneck!")
        return False

class KanbanBoard:
    def __init__(self) -> None:
        self.columns: list[KanbanColumn] = [
            KanbanColumn("Backlog", wip_limit=100),
            KanbanColumn("Ready",   wip_limit=5),
            KanbanColumn("In Progress", wip_limit=4),
            KanbanColumn("Review",  wip_limit=2),
            KanbanColumn("Done",    wip_limit=100),
        ]

    def status(self) -> None:
        for col in self.columns:
            limit = ("∞" if col.wip_limit == 100
                     else str(col.wip_limit))
            full = "🔴" if col.is_full else "🟢"
            print(f"{full} {col.name} [{len(col.items)}/{limit}]: "
                  f"{[i.id for i in col.items]}")
```

---

### ⚖️ Comparison Table

|                   | Kanban                                     | Scrum                                    |
| ----------------- | ------------------------------------------ | ---------------------------------------- |
| **Cadence**       | Continuous flow; no sprints                | Fixed-length sprints                     |
| **Roles**         | No prescribed roles                        | PO / SM / Developers                     |
| **Commitment**    | No sprint commitment                       | Sprint Goal commitment                   |
| **Change policy** | Change anytime; pull when ready            | Sprint Goal protected during sprint      |
| **WIP control**   | Explicit WIP limits per column             | Implicit (sprint capacity)               |
| **Best for**      | Ops, support, maintenance, continuous work | Feature delivery; predictable increments |
| **Metrics**       | Cycle time, throughput, flow efficiency    | Velocity, sprint burndown                |

---

### ⚠️ Common Misconceptions

| Misconception                      | Reality                                                                                                                                                                |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Kanban means no planning"         | Kanban requires continuous backlog refinement and prioritisation. Work doesn't get into Ready without refinement. The planning is continuous, not sprint-batched.      |
| "WIP limits slow the team down"    | WIP limits slow the starting of new work; they speed up the finishing of existing work. Net effect: higher throughput, lower cycle time.                               |
| "Kanban works for any team"        | Kanban is best for continuous, unpredictable work. Teams with discrete, planned feature work often benefit from Scrum's sprint commitment structure.                   |
| "No roles means no accountability" | Kanban has no prescribed roles, but teams still need someone managing the backlog priority and someone facilitating flow improvement. These are functions, not titles. |
| "Kanban is simpler than Scrum"     | Kanban's ceremonies are simpler; its analytical demands (flow metrics, bottleneck analysis) are more sophisticated than Scrum's.                                       |

---

### 🚨 Failure Modes & Diagnosis

**WIP Limits Ignored — The Infinite In-Progress Column**

**Symptom:** The Kanban board shows 18 items in the "In Progress" column. The WIP limit says 5. Nobody enforces it. New items are added to In Progress whenever a new request arrives. Cycle time is 6+ weeks. Items sit untouched in In Progress for days. The board is a false comfort — it shows activity, not flow.

**Root Cause:** WIP limits are aspirational, not enforced. Team members feel productive when starting new work ("I'm busy"). Stopping to help finish someone else's item feels unproductive. Management asks "what are you working on" (activity) rather than "what did you finish" (flow).

**Fix:**

```
1. MAKE WIP VIOLATIONS VISIBLE:
   → Column headers show current count vs. limit
   → Colour the column red when over limit
   → Daily standup starts: "We are over WIP limit on
     In Progress. Who is going to help move something to Done?"

2. CHANGE THE QUESTION:
   → From: "What are you working on today?"
   → To:   "What will you finish this week?"
   → This reframes the team's attention from starting to finishing

3. SWARM ON BLOCKERS:
   → When a column is full, the team's job is to unblock it
   → "What is blocking the Review items?" → solve it together
   → Swarming (multiple people on one item) is legitimate in Kanban

4. RETROSPECT ON WIP:
   → Weekly: "How many items did we complete? What's our
     average cycle time?" Not "how many were in progress?"
   → The retrospective metric should be throughput and cycle time,
     not activity level
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Agile Principles` — Kanban implements agile principles in a flow-based framework
- `Scrum` — the primary alternative; understanding both clarifies when to use which

**Builds On This (learn these next):**

- `Agile Principles` — the foundational values Kanban operationalises
- `Sprint Planning` — if moving from Kanban to Scrum, Sprint Planning is the key new ceremony

**Alternatives / Comparisons:**

- `Scrum` — sprint-based alternative; better for feature teams with discrete delivery goals
- `Agile Principles` — the shared foundation of both Kanban and Scrum

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CORE RULE   │ Limit WIP. Pull, don't push.               │
│             │ "Stop starting; start finishing."          │
├─────────────┼──────────────────────────────────────────-─┤
│ LITTLE'S    │ WIP = Throughput × Cycle Time              │
│ LAW         │ ↓ WIP → ↓ Cycle Time (with same throughput)│
├─────────────┼──────────────────────────────────────────-─┤
│ METRICS     │ Cycle time (speed per item)                │
│             │ Throughput (items completed/week)          │
├─────────────┼──────────────────────────────────────────-─┤
│ BOTTLENECK  │ Column consistently full at WIP limit      │
│             │ → fix the bottleneck; don't bypass it     │
├─────────────┼──────────────────────────────────────────-─┤
│ BEST FOR    │ Ops, support, infra, maintenance work;     │
│             │ unpredictable demand; continuous delivery  │
├─────────────┼──────────────────────────────────────────-─┤
│ NEXT EXPLORE│ Sprint Planning →                          │
│             │ Retrospective                             │
└─────────────┴────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Little's Law states WIP = Throughput × Cycle Time. A team has WIP = 15, Throughput = 3 items/week, and Cycle Time = 5 weeks. They implement a WIP limit of 6 and after 8 weeks, WIP stabilises at 6 items. Throughput is now 4 items/week. Calculate: (a) new cycle time, (b) how much faster the average item is delivered, (c) what might explain the improvement in throughput (not just cycle time) from reducing WIP?

**Q2.** Your team supports both planned feature work and unplanned operational requests. Scrum doesn't work well because unplanned requests break sprint commitments. Kanban doesn't provide enough predictability for the roadmap feature work. Design a hybrid system (sometimes called "Scrumban") that: (a) handles unplanned operational work via Kanban WIP limits, (b) provides sprint-like predictability for planned features, (c) defines clear policies for when an urgent request can interrupt the planned work, and (d) specifies what metrics you'd track to know the hybrid is working.
