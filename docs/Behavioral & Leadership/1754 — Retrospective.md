---
layout: default
title: "Retrospective"
parent: "Behavioral & Leadership"
nav_order: 1754
permalink: /leadership/retrospective/
number: "1754"
category: Behavioral & Leadership
difficulty: ★☆☆
depends_on: Scrum, Agile Principles
used_by: Scrum, Blameless Culture, Psychological Safety
related: Scrum, Blameless Culture, Sprint Planning
tags:
  - leadership
  - agile
  - beginner
  - retrospective
  - continuous-improvement
---

# 1754 — Retrospective

⚡ TL;DR — The retrospective is a regular team event (end of sprint in Scrum; any cadence in other contexts) where the team reflects on how they worked together and makes a commitment to one or more specific, actionable improvements — its purpose is continuous process improvement, and its value is proportional to whether those improvements are actually implemented rather than just listed.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Teams repeat the same process problems sprint after sprint. Communication gaps, unclear handoffs, slow code review, unclear requirements — each complained about in one-on-one conversations but never formally addressed. Without a forum for process reflection, the only mechanism for change is individual initiative or management dictation — neither of which is reliable or sustainable. Teams plateau at their current effectiveness and stay there.

**THE BREAKING POINT:**
The Agile Manifesto's 12th principle: "At regular intervals, the team reflects on how to become more effective, then tunes and adjusts its behaviour accordingly." This principle identifies a fundamental truth: teams do not automatically improve — improvement requires deliberate reflection and action. The retrospective is the operationalisation of this principle.

**THE INVENTION MOMENT:**
Retrospectives have roots in after-action reviews (AAR) used by the US Army (1970s), which asked: What was supposed to happen? What actually happened? What will we do differently? The Agile software retrospective was formalised by Norm Kerth ("Project Retrospectives," 2001) and adapted into Scrum by Schwaber and Sutherland.

---

### 📘 Textbook Definition

**Retrospective (Scrum Guide):** An event for the Scrum Team to inspect how the last Sprint went (people, interactions, processes, tools, Definition of Done) and to plan improvements. Max 3 hours for a 4-week sprint. The most significant improvements addressed: added to Sprint Backlog for the next Sprint.

**Retrospective Prime Directive (Norm Kerth):** "Regardless of what we discover, we understand and truly believe that everyone did the best job they could, given what they knew at the time, their skills and abilities, the resources available, and the situation at hand." This establishes psychological safety for honest reflection.

**"What Went Well / What Didn't / What to Improve" (WWW):** The most common retrospective format. Simple, effective, widely used. Risk: becomes rote if used every sprint without variation.

**Action items:** Specific, owner-assigned commitments that come out of the retrospective. The output of the retrospective. Without action items: the retrospective is venting, not improvement.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The retrospective is the team's regular practice of asking "how did we work this sprint?" and committing to one improvement — its value is measured not in what is discussed but in what is changed.

**One analogy:**

> A retrospective is like the half-time talk in football. The coach doesn't review game tape to feel bad about the first half — they review it to make specific tactical adjustments for the second half. "Their left flank is consistently open — we'll attack there." "Our marking on set pieces is breaking down — here's the fix." The talk is only valuable if the second half is different. A retrospective where nothing changes is a half-time talk that produces no tactical change.

**One insight:**
The most common retrospective failure is generating a long list of issues and no action items. The second most common failure is generating action items that nobody completes. The retrospective's value is entirely in the improvements that are implemented — not in the insights generated. One completed improvement per sprint compounds into dramatically better process over a year; twelve listed-but-unimplemented improvements do not.

---

### 🔩 First Principles Explanation

**COMMON RETROSPECTIVE FORMATS:**

```
FORMAT 1: WWW (What Went Well / What Didn't / What to Improve)
  Strengths: simple; fast; widely understood
  Weakness: becomes rote; teams stop thinking critically
  When to use: new teams; time-constrained

FORMAT 2: 4Ls (Liked, Learned, Lacked, Longed For)
  Liked: what did you appreciate?
  Learned: what did you discover?
  Lacked: what was missing or unclear?
  Longed For: what did you wish you had?
  Strengths: more nuanced; surfaces positive learning
  When to use: teams wanting more depth than WWW

FORMAT 3: Start/Stop/Continue
  Start: what should we begin doing?
  Stop: what should we cease?
  Continue: what is working — keep doing it?
  Strengths: directly actionable; clear framing
  When to use: teams ready for direct process commitments

FORMAT 4: Five Whys (for deep-dive on one issue)
  Select one recurring problem
  Ask "Why?" five times
  Each answer leads to the next why
  Goal: find root cause, not symptom
  When to use: retrospective within a retrospective;
               recurring issues that WWW hasn't fixed

FORMAT 5: Sailboat / Speedboat
  Visual metaphor: wind = helps; rocks = risks; anchors = slow
  Strengths: engaging; surfaces non-obvious patterns
  When to use: teams with low engagement; change of pace
```

**ACTION ITEM QUALITY:**

```
BAD ACTION ITEMS:
  "Improve communication" — who? what specifically? by when?
  "Be more careful with code reviews" — not actionable
  "Consider updating the runbooks" — no commitment

GOOD ACTION ITEMS:
  "Alice will update the deploy runbook for service X by end of Sprint 16"
  "From Sprint 15: all PRs require 2 approvals (update branch policy)"
  "Bob will schedule a 30-minute API contract review with Team Y in week 1 of Sprint 15"

PROPERTIES OF GOOD ACTION ITEMS:
  □ Specific: exactly what will be done?
  □ Owner: one named person accountable
  □ Time-bound: by when? (not "eventually")
  □ Testable: how will we know it's done?
  □ Small enough to complete in one sprint
```

---

### 🧪 Thought Experiment

**SETUP:**
A team's last retrospective produced 8 action items. Sprint 16 begins. The Scrum Master opens the retrospective with: "Let's look at last sprint's action items before we start."

Results:

- 2 action items: completed
- 3 action items: not started ("we forgot")
- 3 action items: "in progress" (meaning: not done)

Team starts discussing Sprint 16 issues and generates 7 new action items.

**The problem:** The retrospective is a backlog of unimplemented improvements. The team has 14 retrospective action items open. None of them will be done because none of them are in the sprint backlog.

**Root causes:**

1. Action items are not tracked in the sprint backlog — they're in a retrospective doc nobody reads
2. Too many action items per retrospective — 8 is too many; focus is diffused
3. No retrospective account: "Did we improve?"

**Better process:**

1. Start every retrospective by reviewing last sprint's action items: done/not done
2. Limit to 1–2 action items per retrospective; add them to the sprint backlog
3. Pick the highest-impact one if constrained: "What single change would most improve this sprint?"
4. At sprint review: "Did we implement last sprint's retrospective action item?"

---

### 🧠 Mental Model / Analogy

> Retrospectives are compound interest for team performance. A team that implements one 5% improvement per sprint will, after 20 sprints (10 months), be 165% as effective as at the start (1.05^20 ≈ 2.65 — a 165% improvement). A team that generates excellent retrospective insights but implements nothing compounds at 0% — they are exactly as effective after 20 sprints as at the start. The retrospective is not the insight — the insight has zero value. The value is the change in behaviour. Compound interest requires execution, not reflection.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A retrospective is a team meeting at the end of every sprint where you discuss: what worked well, what didn't work, and what you'll do differently next time. The most important part: committing to one specific change and actually making it.

**Level 2 — How to use it (engineer):**
Bring one specific observation: "In this sprint, code reviews averaged 3 days — I had two stories blocked for 3 days each waiting for review. That's the thing I'd most like to fix." Be specific; be solution-oriented. If you disagree with a proposed action item: say so with a reason. If the team is generating 8 action items: ask "Which one of these would have the biggest impact if we actually did it? Let's do that one."

**Level 3 — How it works (Scrum Master / tech lead):**
Facilitate with structure: choose a format appropriate to the team's current needs; time-box each section; ensure the output is 1–3 specific, owner-assigned action items. Start every retrospective by reviewing the previous sprint's action items — this creates accountability and demonstrates that the retrospective has real consequences. If the team is in a "venting" pattern (long list of complaints, no action): redirect: "What is one thing we could change in the next sprint that would improve this?" Vary the format every 2–3 sprints to prevent staleness.

**Level 4 — Why it was designed this way (principal/staff):**
The retrospective is an institutionalised learning loop. Its design reflects a key insight: teams do not automatically learn from experience — they learn from reflection on experience followed by deliberate behavioural change. Unprocessed experience is not learning; it is just experience. The retrospective forces processing. At the staff level, the retrospective is also a cultural signal: a team whose retrospectives produce completed improvements is a team that takes continuous improvement seriously. A team whose retrospectives produce unimplemented lists is a team that performs continuous improvement without practising it. The culture of the retrospective reflects and shapes the culture of the team. When retrospectives produce no change, engineers learn: "Nothing we say here matters." That is a damaging signal.

---

### ⚙️ How It Works (Mechanism)

```
RETROSPECTIVE STRUCTURE:

SET THE STAGE (5–10 min)
  Prime Directive; check-in activity
  Establishes psychological safety
    ↓
GATHER DATA (15–20 min)
  Team generates observations (sticky notes / digital)
  WWW / 4Ls / Start-Stop-Continue format
  No discussion yet; just generation
    ↓
GENERATE INSIGHTS (15–20 min)
  Group and theme observations
  Discuss patterns: "These three items are all about handoffs"
  Vote on top themes to address
    ↓
DECIDE WHAT TO DO (15–20 min)
  Select 1–3 themes to address
  Generate specific action items (SMART)
  Assign owners; set deadlines
    ↓
CLOSE (5 min)
  Confirm action items; read them aloud
  Add to Sprint Backlog
  Brief check-out: "Rate this retrospective 1–5"
    ↓
NEXT RETROSPECTIVE OPENS:
  Review previous action items (done/not done)
  If not done: why? Is it still worth doing?
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Sprint ends
    ↓
Sprint Review (inspect Increment)
    ↓
[RETROSPECTIVE ← YOU ARE HERE]
Review previous action items
    ↓
Gather data: observations on the sprint
    ↓
Theme and prioritise: top 1–2 issues
    ↓
Action items created: specific, owned, timed
    ↓
Added to Sprint Backlog for next sprint
    ↓
Sprint Planning begins
    ↓
Action items worked alongside sprint stories
    ↓
[At next Retrospective: review completion]
```

---

### 💻 Code Example

**Retrospective action item tracker:**

```python
from dataclasses import dataclass
from enum import Enum
from datetime import date

class Status(Enum):
    OPEN        = "Open"
    IN_PROGRESS = "In Progress"
    DONE        = "Done"
    DROPPED     = "Dropped (no longer relevant)"

@dataclass
class ActionItem:
    sprint: int
    description: str
    owner: str
    due_sprint: int
    status: Status = Status.OPEN

    def is_overdue(self, current_sprint: int) -> bool:
        return (self.status not in (Status.DONE, Status.DROPPED)
                and current_sprint > self.due_sprint)

def retrospective_review(
    items: list[ActionItem],
    current_sprint: int
) -> None:
    print(f"=== Retrospective Review — Sprint {current_sprint} ===\n")
    overdue = [i for i in items if i.is_overdue(current_sprint)]
    done = [i for i in items if i.status == Status.DONE]
    open_ = [i for i in items
             if i.status == Status.OPEN and not i.is_overdue(current_sprint)]

    print(f"✓  Done ({len(done)}):")
    for i in done:
        print(f"   [Sprint {i.sprint}] {i.description} — {i.owner}")

    if overdue:
        print(f"\n⚠  Overdue ({len(overdue)}):")
        for i in overdue:
            print(f"   [Sprint {i.sprint}] {i.description} — {i.owner}")

    print(f"\n○  Open ({len(open_)}):")
    for i in open_:
        print(f"   [Sprint {i.sprint}] {i.description} — {i.owner} "
              f"(due Sprint {i.due_sprint})")

retrospective_review(
    items=[
        ActionItem(14, "Update deploy runbook for service X",
                   "Alice", 15, Status.DONE),
        ActionItem(14, "Add 2-approver rule to branch policy",
                   "Bob", 15, Status.OPEN),
        ActionItem(13, "Schedule API contract review with Team Y",
                   "Carlos", 14, Status.OPEN),
    ],
    current_sprint=15,
)
```

---

### ⚖️ Comparison Table

| Format                  | Best For                                   | Risk                                      |
| ----------------------- | ------------------------------------------ | ----------------------------------------- |
| **WWW**                 | New teams; quick structure                 | Becomes rote after 3–4 sprints            |
| **4Ls**                 | Depth of reflection; surfacing learning    | Takes longer; needs facilitation          |
| **Start/Stop/Continue** | Direct commitment to change                | Can skip root cause analysis              |
| **Five Whys**           | Recurring problems with unknown root cause | Can feel like interrogation; needs safety |
| **Sailboat**            | Engagement; visual thinkers                | Less precise; harder to action            |

---

### ⚠️ Common Misconceptions

| Misconception                              | Reality                                                                                                                                                                                     |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "The retrospective is a venting session"   | Venting without action is not a retrospective. It is a complaint session. Retrospectives produce specific, trackable improvements.                                                          |
| "More action items = better retrospective" | Fewer, completed action items > many unimplemented ones. One completed improvement per sprint compounds dramatically over time.                                                             |
| "Retrospectives are only for Scrum teams"  | Any team can hold retrospectives. Project end, quarter end, post-incident — the reflection format applies whenever continuous improvement is desired.                                       |
| "The Scrum Master always facilitates"      | The SM facilitates by default. But any team member can facilitate. Rotating the facilitator builds facilitation skills across the team.                                                     |
| "Retrospectives should feel comfortable"   | Effective retrospectives surface real problems, which is uncomfortable. Psychological safety doesn't mean avoiding discomfort — it means the discomfort is productive rather than punitive. |

---

### 🚨 Failure Modes & Diagnosis

**The Action Item Graveyard — Retrospectives Without Change**

**Symptom:** Retrospective is held every sprint. Long lists of issues generated. Action items written. Next sprint: nobody acts on them. They are not in the sprint backlog. The Scrum Master mentions them at the next retrospective; team acknowledges them; generates new action items. After 10 sprints: 60 retrospective action items in a doc nobody opens. Team engagement in retrospectives drops. Engineers say "retrospectives are useless."

**Root Cause:** Action items are not treated as real work. They live outside the sprint backlog. They have no owners with accountability. There is no retrospective-on-retrospective: nobody asks "did we improve?"

**Fix:**

```
RULE 1: ONE OR TWO ACTION ITEMS MAX PER RETROSPECTIVE:
  → "Of everything on this list, what ONE change would most
    improve our next sprint?"
  → Do that. Just that. One thing done > ten things planned.

RULE 2: ACTION ITEMS IN THE SPRINT BACKLOG:
  → Every retrospective action item becomes a ticket
  → Added to the sprint backlog for the NEXT sprint
  → Has an owner; has acceptance criteria; is sized
  → It is real work, not a side commitment

RULE 3: ACCOUNTABILITY CHECK AT NEXT RETRO:
  → Every retrospective opens: "Last sprint's action items?"
  → Done: acknowledge, celebrate, move on
  → Not done: "Should we continue? Why didn't it happen?"
  → Dropped: that's OK — explicitly drop it; don't pretend it wasn't listed

RULE 4: MEASURE RETROSPECTIVE EFFECTIVENESS:
  → "What % of our retrospective action items get completed?"
  → Target: 80%+
  → If below 50%: the process for action items is broken
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Scrum` — the retrospective is Scrum's fifth event
- `Agile Principles` — the 12th Agile Principle mandates regular team reflection

**Builds On This (learn these next):**

- `Blameless Culture` — the retrospective is the regular expression of blameless practice
- `Psychological Safety` — required for honest retrospectives
- `Sprint Planning` — retrospective improvements feed into the next sprint's planning

**Alternatives / Comparisons:**

- `Blameless Culture` — applies blameless retrospective principles to incidents
- `Sprint Planning` — the forward-looking companion to the retrospective's backward look

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PURPOSE     │ Team reflects on process; commits to       │
│             │ specific, actionable improvements          │
├─────────────┼──────────────────────────────────────────-─┤
│ TIME-BOX    │ 3h max for 4-week sprint                   │
│             │ 1.5h for 2-week sprint                     │
├─────────────┼──────────────────────────────────────────-─┤
│ PRIME       │ "Everyone did the best job they could      │
│ DIRECTIVE   │ given what they knew at the time."        │
├─────────────┼──────────────────────────────────────────-─┤
│ FORMATS     │ WWW | 4Ls | Start/Stop/Continue           │
│             │ Five Whys | Sailboat                       │
├─────────────┼──────────────────────────────────────────-─┤
│ KEY RULE    │ 1–2 action items max; in sprint backlog;  │
│             │ owned; time-bound; reviewed next retro    │
├─────────────┼──────────────────────────────────────────-─┤
│ MEASURE     │ % of retro actions completed              │
│             │ Target: 80%+                              │
├─────────────┼──────────────────────────────────────────-─┤
│ NEXT EXPLORE│ OKRs →                                    │
│             │ Blameless Culture                         │
└─────────────┴────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The Prime Directive ("everyone did the best they could") is designed to create psychological safety in retrospectives. But it is also a statement that some people find logically problematic: "What if someone clearly didn't do the best they could?" Design an argument for why the Prime Directive is still valuable even in cases where an individual's contribution was genuinely below their best. Then design a process for when the Retrospective surfaces a concern that is actually an individual performance issue — how do you distinguish it from a process issue, and what do you do with it?

**Q2.** A team has been running weekly retrospectives for 6 months. Engineer engagement has dropped: two engineers don't speak; one checks their phone throughout. The Scrum Master has tried three different formats with no improvement. You suspect the team has lost faith that the retrospective produces real change. Design a "retrospective reset" — a specific plan for the next three retrospectives that diagnoses why engagement dropped, rebuilds confidence that change is possible, and establishes new habits. What would you measure to know if the reset worked?
