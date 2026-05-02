---
layout: default
title: "Agile Principles"
parent: "Behavioral & Leadership"
nav_order: 1750
permalink: /leadership/agile-principles/
number: "1750"
category: Behavioral & Leadership
difficulty: ★★☆
depends_on: Sprint Planning, Scrum, Kanban
used_by: Sprint Planning, Scrum, Retrospective
related: Scrum, Kanban, Sprint Planning
tags:
  - leadership
  - agile
  - intermediate
  - manifesto
  - process
---

# 1750 — Agile Principles

⚡ TL;DR — The Agile Manifesto (2001) defines 4 values and 12 principles that prioritise working software over documentation, customer collaboration over contracts, responding to change over plans, and individuals over processes — the practical implication is iterative delivery, close customer collaboration, and teams empowered to self-organise; understanding the principles (not just the ceremonies) is what separates effective agile practice from "agile theatre."

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Software projects in the 1980s–1990s follow waterfall: requirements locked for 12 months, design for 6 months, implementation for 12 months, testing for 6 months. A typical 3-year project delivers something to users who have changed their minds entirely, whose operating environment has changed, and who were inadequately consulted during requirements. CHAOS report (Standish Group) found: 31% of software projects cancelled before completion; 53% cost nearly double their original estimates; only 16% delivered on time and on budget. The methodology was the problem, not the people.

**THE BREAKING POINT:**
The fundamental failure of waterfall for software is that it treats software development like manufacturing — as if you can design a complete, correct blueprint and then build exactly to specification. Software development is inherently a discovery process: requirements that seem clear at year 0 are wrong or incomplete at year 2. The environment, technology, user behaviour, and business context change faster than the project cycle. Waterfall optimises for predictability; software requires adaptability.

**THE INVENTION MOMENT:**
February 2001: 17 software practitioners meet at the Snowbird ski resort, Utah. They produce a single page document — the Agile Manifesto — that articulates 4 values and 12 principles summarising what had worked in their practice against waterfall's failures. The signatories include Kent Beck (XP), Ken Schwaber (Scrum), and others who had been independently developing iterative methods throughout the 1990s.

---

### 📘 Textbook Definition

**The Agile Manifesto — 4 Values:**
> "We are uncovering better ways of developing software by doing it and helping others do it. Through this work we have come to value:
> - **Individuals and interactions** over processes and tools
> - **Working software** over comprehensive documentation
> - **Customer collaboration** over contract negotiation
> - **Responding to change** over following a plan
> That is, while there is value in the items on the right, we value the items on the left more."

**The 12 Principles** (key examples):
- Highest priority: satisfy the customer through early and continuous delivery of valuable software
- Welcome changing requirements, even late in development
- Deliver working software frequently, from a couple of weeks to a couple of months
- Business people and developers must work together daily throughout the project
- Build projects around motivated individuals; give them the environment and support they need; trust them
- The most efficient and effective method of conveying information is face-to-face conversation
- Working software is the primary measure of progress
- Agile processes promote sustainable development
- Continuous attention to technical excellence and good design enhances agility
- Simplicity — the art of maximising the amount of work not done — is essential
- The best architectures, requirements, and designs emerge from self-organising teams
- At regular intervals, the team reflects on how to become more effective, then tunes and adjusts its behaviour accordingly

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The Agile Manifesto says: ship working software early and often, collaborate with the customer continuously, embrace change, and trust the team — as opposed to: plan exhaustively, document everything, negotiate rigidly, and control the process.

**One analogy:**
> Agile vs. waterfall is like GPS navigation vs. a fixed paper map. A paper map (waterfall) is planned and complete before the journey starts. If a road closes, you pull over, find an alternative on the map, and re-plan manually. GPS navigation (agile) calculates a route based on current conditions, updates continuously as conditions change, and re-routes in real time. The GPS doesn't eliminate planning — it continuously plans. Agile doesn't eliminate requirements — it continuously refines them. The difference is the cycle time of adaptation.

**One insight:**
The 4 values say "we value X over Y" — not "Y has no value." Many organisations implement agile as: "We have Scrum ceremonies, so we are agile." But if those ceremonies are used to lock requirements, punish change, and measure process compliance rather than working software, the organisation has the ceremonies without the values — which is "agile theatre." The ceremonies are implementations of the principles; the principles are what matter.

---

### 🔩 First Principles Explanation

**THE 4 VALUES UNPACKED:**

```
VALUE 1: INDIVIDUALS AND INTERACTIONS > PROCESSES AND TOOLS
  What it means: great people using bad tools outperform
                 mediocre people using great tools.
                 No process compensates for unmotivated
                 or poorly supported people.
  Anti-pattern: "We have Jira, so we're agile."
                 Jira is a tool; it is not agile.
  Practice: psychological safety; autonomy; trust; 
            direct communication over ticket culture

VALUE 2: WORKING SOFTWARE > COMPREHENSIVE DOCUMENTATION
  What it means: the purpose of software development is
                 to deliver working software. Documentation
                 is valuable when it serves that goal.
  Anti-pattern: 40-page design documents that nobody reads;
                architecture diagrams that are 2 years out of date
  Practice: Lightweight design docs; working code as the
            ground truth; documentation updated when it
            serves future working software

VALUE 3: CUSTOMER COLLABORATION > CONTRACT NEGOTIATION
  What it means: the customer understands the problem better
                 than you do. The contract cannot capture all
                 their needs. Working with them continuously
                 produces better outcomes than arguing about
                 the contract when the output is wrong.
  Anti-pattern: "That wasn't in the spec" as a response to
                customer feedback
  Practice: embedded product managers; regular demos;
            user research in the iteration loop

VALUE 4: RESPONDING TO CHANGE > FOLLOWING A PLAN
  What it means: in a dynamic environment, the plan is
                 out of date by the time it's written.
                 The ability to adapt is more valuable than
                 the ability to follow a plan precisely.
  Anti-pattern: "We can't change the scope — it was committed
                 in January." (Spoken in September.)
  Practice: short iterations; backlog as a living document;
            planning at multiple timeframes (quarterly roadmap +
            sprint backlog) with different fidelity
```

**THE 12 PRINCIPLES — KEY ONES FOR ENGINEERS:**

```
"Continuous attention to technical excellence and good design
 enhances agility."
 → Technical debt reduction is an agile value, not a blocker
 → Agility requires a clean codebase; not despite it

"Simplicity — the art of maximising the amount of work
 not done — is essential."
 → Don't build what you don't need yet
 → YAGNI (You Aren't Gonna Need It) is an agile principle

"The best architectures, requirements, and designs emerge
 from self-organising teams."
 → Top-down architecture mandate is anti-agile
 → Teams closest to the work make the best technical decisions

"At regular intervals, the team reflects on how to become
 more effective, then tunes and adjusts its behaviour."
 → Retrospectives are not optional ceremonies — they are
   the mechanism by which the team improves its process
```

**COMMON AGILE ANTI-PATTERNS:**

```
AGILE THEATRE:
  Ceremonies without principles
  → Standups where engineers read status from Jira
  → Sprint planning where backlog is not prioritised by value
  → Retrospectives that produce no action items
  → "Agile" with a 12-month fixed-scope commitment

MINI-WATERFALL IN SPRINTS:
  Design → Develop → Test within each sprint
  with each phase handed off
  → Anti-pattern: breaks continuous collaboration
  → Agile: engineers + QA + design working simultaneously

VELOCITY AS A METRIC:
  Using story points velocity as a performance measure
  → Incentivises inflation; removes forecasting accuracy
  → Agile principle: working software is the measure

PLANNING FALLACY AT SCALE:
  Treating SAFe or LeSS as a replacement for
  doing the hard work of cross-team collaboration
  → Scaling frameworks are scaffolding, not solutions
```

---

### 🧪 Thought Experiment

**SETUP:**
Two teams building the same product. Team A is "doing Scrum" — 2-week sprints, daily standups, backlog, retrospectives. Team B is following Agile principles without strict Scrum.

**Team A (ceremony without principles):**
- Sprint planning: PM hands list of 15 items; team estimates; committed
- Standups: "I did X yesterday, I'll do Y today, no blockers" (rote)
- Sprint demo: features demoed to PM who approves
- Retrospective: "Standups run long. Let's timebox them." Action item added; ignored.
- Sprint 3: requirements change from business. PM says: "Not in scope this sprint."
- Sprint 8: product is 80% of what was planned 4 months ago. Users haven't seen it.
- Result: 6-month waterfall in sprint clothing.

**Team B (principles without rigid ceremony):**
- Weekly iteration: small, shippable increment. Users see it.
- Daily conversation (async): "I'm blocked on the auth API — anyone know the contract?" → resolved in 20 minutes
- User feedback loop: every 2 weeks, 3 users try the latest version. Findings feed next week's work.
- Sprint 3 change: "Business changed priorities — let's adjust the backlog." Done.
- Technical excellence: no sprint completes without tests and a refactor task in scope
- Result: 6 months in, 60% of planned features, all of them high-value and validated by users.

**The insight:** Team A has better metrics (velocity, sprint commitment) but worse outcomes (users haven't seen the product; requirements have drifted). Team B has worse "agile hygiene" but better outcomes (continuous user validation, adaptability). Agile principles produced better software; Scrum ceremonies produced better process metrics.

---

### 🧠 Mental Model / Analogy

> Agile principles are like the laws of aerodynamics; Scrum is one specific aircraft design. The laws of aerodynamics (the principles) tell you what you must achieve for flight: lift > weight, thrust > drag, stability, control. Scrum is a Boeing 737 — one design that implements those laws effectively. But there are other valid aircraft designs (Kanban is a glider — different performance profile; XP is a fighter jet — different speed and manoeuvrability). The mistake is confusing the aircraft design for the laws of aerodynamics. If your Boeing 737 isn't flying (if your Scrum isn't working), the question is: are you violating the underlying principles? Not: are you doing standups correctly?

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
The Agile Manifesto says software teams should: ship working software often; work closely with customers; adapt to change; and trust the team. These 4 values, expanded into 12 principles, are what "being agile" actually means — not Jira boards or Scrum ceremonies.

**Level 2 — How to use it (engineer):**
Use the principles as a compass when process feels wrong. If a ceremony adds no value: "Is this retrospective producing action items? If not, we're violating the principle of continuous improvement." If a change is being resisted: "The manifesto says to welcome change — why are we treating this business change as a problem?" If documentation is ballooning: "Working software is the measure — does this document serve that goal?"

**Level 3 — How it works (tech lead):**
Your role is to distinguish agile practice from agile theatre. Inspect the principles against your team's reality: Are we delivering working software to users frequently? Are we welcoming change, or treating it as a failure? Is the retrospective producing improvements? Are engineers self-organising, or waiting for instructions? Identify the one principle that, if improved, would have the most impact this quarter. Make it a focus.

**Level 4 — Why it was designed this way (principal/staff):**
At the staff/principal level, the key question is: what is the right level of agility for this team and this product? The manifesto was written for small, co-located teams building web applications where requirements were highly uncertain. Agile at scale (SAFe, LeSS, Spotify model) addresses the coordination problem of many agile teams working on shared systems. But scaling frameworks are not a substitution for the underlying principles — they are structural solutions to the coordination problem. The principal engineer's responsibility is to ensure that scaling structure does not kill the agility it was designed to preserve: that cross-team coordination ceremonies don't become the new waterfall; that large-scale planning doesn't become the 12-month fixed-scope commitment that agile was invented to replace.

---

### ⚙️ How It Works (Mechanism)

```
AGILE FEEDBACK LOOP:

Understand the user problem
    ↓
Build the smallest thing that tests the hypothesis
    ↓
Ship to users (frequently; in weeks, not months)
    ↓
Learn: did this solve the problem?
  Did it move the metric we cared about?
    ↓
Adapt: reprioritise based on learning
    ↓
Repeat

KEY PROPERTIES:
  Cycle time: 1–4 weeks (not 6–12 months)
  User touchpoints: every iteration (not at project end)
  Plan: living document (not locked at project start)
  Team: self-organising (not top-down directed)
  Measure: working software (not process compliance)
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Business problem / user need identified
    ↓
Discovery: understand the problem (don't build yet)
    ↓
Minimum hypothesis defined
    ↓
[AGILE PRINCIPLES ← YOU ARE HERE]
Short iteration: build → ship → measure
    ↓
User feedback; metric review
    ↓
Retrospect: what did we learn? What do we do next?
    ↓
Backlog reprioritised based on learning
    ↓
Next iteration: refined understanding → better solution
    ↓
[Cycle repeats until the user problem is solved or
 we decide the problem is not worth solving]
```

---

### 💻 Code Example

**Agile principles compliance checklist:**
```python
from dataclasses import dataclass

@dataclass
class AgileHealthCheck:
    question: str
    principle: str
    anti_pattern: str

AGILE_CHECKS = [
    AgileHealthCheck(
        question="Did users see working software in the last 2 weeks?",
        principle="Deliver working software frequently",
        anti_pattern="6-month projects with no user touchpoints",
    ),
    AgileHealthCheck(
        question="Did the team change direction based on new information?",
        principle="Welcome changing requirements, even late in development",
        anti_pattern="'Not in scope this sprint' as a reflexive response",
    ),
    AgileHealthCheck(
        question="Did the retrospective produce completed action items?",
        principle="Team regularly reflects and adjusts",
        anti_pattern="Retrospectives that produce lists nobody acts on",
    ),
    AgileHealthCheck(
        question="Did engineers have autonomy in technical decisions?",
        principle="Best architectures emerge from self-organising teams",
        anti_pattern="Architecture mandated top-down before teams engage",
    ),
    AgileHealthCheck(
        question="Was technical debt addressed in the sprint?",
        principle="Continuous attention to technical excellence",
        anti_pattern="'We'll fix it later' as a permanent deferral",
    ),
]

def run_health_check(
    team_answers: dict[str, bool]
) -> None:
    print("Agile Health Check Results:\n")
    for check in AGILE_CHECKS:
        answer = team_answers.get(check.question, None)
        status = "✓" if answer else "✗" if answer is False else "?"
        print(f"{status} {check.question}")
        if answer is False:
            print(f"   Principle: {check.principle}")
            print(f"   Anti-pattern detected: {check.anti_pattern}\n")

# Example
run_health_check({
    "Did users see working software in the last 2 weeks?": True,
    "Did the team change direction based on new information?": False,
    "Did the retrospective produce completed action items?": False,
    "Did engineers have autonomy in technical decisions?": True,
    "Was technical debt addressed in the sprint?": True,
})
```

---

### ⚖️ Comparison Table

| Framework | Basis | Cadence | Best For |
|---|---|---|---|
| **Agile Manifesto** | Values + principles | n/a (not a framework) | Guiding philosophy; evaluating practices |
| **Scrum** | Sprint-based; defined ceremonies | 1–4 week sprints | Teams with discrete feature work |
| **Kanban** | Flow-based; WIP limits | Continuous | Ops work; unpredictable demand; support |
| **XP (Extreme Programming)** | Engineering practices (TDD, pairing, CI) | Weekly iterations | Teams wanting strong technical practices |
| **SAFe** | Large-scale agile coordination | PI Planning (quarterly) | Multiple agile teams on shared programme |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Agile means no planning" | Agile means continuous planning, at appropriate levels of detail. Short-term plans are detailed; long-term plans are light. Planning is never eliminated. |
| "Agile means no documentation" | Agile values working software MORE than comprehensive documentation. Documentation that serves the team and the product is valued. Documentation for its own sake is not. |
| "We do Scrum, so we're agile" | Scrum is one implementation of agile principles. Scrum without the principles (e.g., fixed scope in sprints, no retrospective improvement) is not agile. |
| "Agile doesn't work at scale" | Agile works at scale when the underlying principles (short cycles, customer collaboration, adaptability) are preserved. Scaling frameworks that replace the principles with heavy process are not agile. |
| "Agile is anti-architecture" | Agile is anti-big-upfront-design. Continuous attention to technical excellence (a core principle) includes architecture evolution. Emergent architecture from self-organising teams is a principle, not an excuse for no architecture. |

---

### 🚨 Failure Modes & Diagnosis

**"Agile Theatre" — Ceremonies Without Principles**

**Symptom:** The team has standups, sprint planning, sprint reviews, and retrospectives. Velocity is tracked. Story points are estimated. Requirements are fixed at sprint start. Change is resisted. Retrospectives produce no action. Users see the product only at project end. The word "agile" is used frequently; working software is delivered infrequently.

**Root Cause:** The ceremonies were adopted; the values were not. The organisation measures process compliance (are we doing standups?) not principle adherence (are we delivering working software to users frequently?). Process measurement creates process optimisation — not software delivery improvement.

**Fix:**
```
INSPECT AGAINST PRINCIPLES:
  Pick one manifesto principle per month.
  Measure: is this team enacting this principle?
  If not: design one specific change to this sprint to improve it.

START WITH WORKING SOFTWARE:
  "When did a user last see working software from this team?"
  If > 4 weeks: that is the first problem to solve.
  Design a delivery mechanism that gets working software
  to real users in the next 2 weeks, no matter how small.

RETROSPECTIVE IMPROVEMENT:
  "What is one thing from last retrospective's action list
   that was completed this sprint?"
  If the answer is "nothing": the retrospective process
  is broken. Fix the retrospective before fixing anything else.

CHANGE WELCOME:
  When next requirement change arrives:
  → Don't ask "was this in the scope?"
  → Ask: "Is this more valuable than what we currently have planned?"
  → Reprioritise accordingly. Celebrate the team's ability to adapt.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Sprint Planning` — the primary ceremony that operationalises agile principles
- `Scrum` — the most widely used agile framework
- `Kanban` — the flow-based alternative to sprint-based agile

**Builds On This (learn these next):**
- `Sprint Planning` — agile planning in practice
- `Scrum` — the framework that implements many agile principles
- `Retrospective` — the principle of continuous improvement in action

**Alternatives / Comparisons:**
- `Scrum` — specific agile framework; ceremonies implement agile principles
- `Kanban` — alternative agile approach; no sprints; continuous flow
- `Sprint Planning` — where the planning principle is operationalised

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ 4 VALUES    │ Individuals > processes                    │
│             │ Working software > documentation           │
│             │ Customer collaboration > contracts         │
│             │ Responding to change > following plan      │
├─────────────┼──────────────────────────────────────────-─┤
│ KEY         │ "While we value items on the right,        │
│ QUALIFIER   │  we value items on the left more."        │
├─────────────┼──────────────────────────────────────────-─┤
│ MEASURE     │ Working software shipped to users          │
│             │ — not velocity, not story points           │
├─────────────┼──────────────────────────────────────────-─┤
│ AGILE       │ Ceremonies without principles              │
│ THEATRE     │ Fixed scope + agile process = waterfall   │
│ TEST        │ "When did users last see working software?"│
├─────────────┼──────────────────────────────────────────-─┤
│ TECHNICAL   │ "Continuous attention to technical         │
│ EXCELLENCE  │ excellence enhances agility" — a principle │
├─────────────┼──────────────────────────────────────────-─┤
│ NEXT EXPLORE│ Scrum →                                   │
│             │ Sprint Planning                           │
└─────────────┴────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The Agile Manifesto was written by 17 practitioners working on small, co-located, web application teams. Evaluate the applicability of each of the 4 values to: (a) a safety-critical embedded systems team building medical device firmware, (b) a 500-person enterprise software development department building a regulatory compliance platform, (c) a 3-person startup building a consumer mobile app. For each context: which values translate directly? Which require modification? Which might be actively harmful if applied uncritically?

**Q2.** Your team is 6 months into a "Scrum transformation." The coaches say the team is following Scrum correctly. You observe: sprint velocity has improved (from 30 to 45 points). Users have seen the product once, at month 5. The retrospective backlog has 22 items, 2 of which are closed. Code coverage has dropped from 78% to 61%. Technical debt complaints have increased. Using the 12 Agile Principles (not Scrum rules), diagnose: (a) which principles are being violated, (b) what the velocity improvement might be masking, and (c) what you would change in the next sprint to move toward principle adherence.
