---
layout: default
title: "Situational Leadership"
parent: "Behavioral & Leadership"
nav_order: 1732
permalink: /leadership/situational-leadership/
number: "1732"
category: Behavioral & Leadership
difficulty: ★★☆
depends_on: []
used_by: Technical Leadership, Mentoring vs Coaching, Scope of Influence
related: Technical Leadership, Mentoring vs Coaching, Engineering Manager vs Tech Lead
tags:
  - leadership
  - management
  - intermediate
  - coaching
  - delegation
---

# 1732 — Situational Leadership

⚡ TL;DR — Situational Leadership (Hersey & Blanchard) is the model that says there is no single best leadership style — effective leaders match their style (directive vs. supportive) to the development level of the individual on the specific task, adapting their approach as people grow.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A senior engineer joins your team. You manage them the way you manage junior engineers: detailed instructions, constant check-ins, micro-review of their work. They feel insulted and disrespected; they start job hunting within 3 months. Conversely, you hire a new grad and give them the autonomy you give your senior engineers — they flounder, miss deadlines, and lose confidence. Same manager; two leadership styles applied to the wrong people; two different failures.

**THE BREAKING POINT:**
The instinct to find "your leadership style" and apply it consistently is wrong. Different people on different tasks at different stages of their development need different types of support. A single style optimised for your comfort fails the people who need a different approach.

**THE INVENTION MOMENT:**
Hersey and Blanchard developed Situational Leadership in the 1960s-70s as a model for adapting management style to the maturity (later: "development level") of the individual. The insight: leadership effectiveness is a function of matching style to situation, not of consistently applying any single style.

---

### 📘 Textbook Definition

**Situational Leadership** (Hersey & Blanchard, 1969; SL II model, Blanchard 1985) is a leadership model in which effective leadership requires adapting one's style to the **development level** of the individual on the specific task. Development level combines: **Competence** (the knowledge and skills required for the task) and **Commitment** (the motivation and confidence to do it). Four development levels (D1–D4) map to four leadership styles (S1–S4): **D1/S1** (Low Competence, High Commitment → Directing: high task behaviour, low relationship), **D2/S2** (Some Competence, Low Commitment → Coaching: high task, high relationship), **D3/S3** (High Competence, Variable Commitment → Supporting: low task, high relationship), **D4/S4** (High Competence, High Commitment → Delegating: low task, low relationship). Key principle: the goal is to move people through development levels; the leader's job is to make themselves progressively less necessary for a given task.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Adapt your leadership style to where each person is on each task — directing beginners, coaching those with growing skills but flagging motivation, supporting the capable-but-uncertain, delegating to the expert.

**One analogy:**

> Learning to drive a car goes through four stages: at first, the instructor tells you exactly what to do (Directing). As you improve, they explain the why and encourage you through challenges (Coaching). As you become skilled but lack confidence on the motorway, they sit with you for support without directing (Supporting). Once you're fully competent and confident, they hand you the keys and stay home (Delegating). Situational Leadership says: the instructor's error is to keep Directing when you need Delegating — or to Delegate when you still need Coaching.

**One insight:**
Development level is always task-specific, never person-specific. Your most senior engineer is D4 on the systems they built but D1 on a new language they've never used. Situational Leadership adapts to the task, not just the person.

---

### 🔩 First Principles Explanation

**THE FOUR DEVELOPMENT LEVELS:**

```
D1 — ENTHUSIASTIC BEGINNER
  Competence: Low (new to task)
  Commitment: High (excited, motivated to learn)
  Example: New grad on first sprint task
           Senior engineer learning new tech stack
  Inner experience: "I don't know what I don't know.
                     I need to be shown."

D2 — DISILLUSIONED LEARNER
  Competence: Some (knows enough to know what's hard)
  Commitment: Low (confidence dropped with complexity)
  Example: Junior engineer 6 months in;
           knows more but feels behind expectations
  Inner experience: "This is harder than I thought.
                     I need guidance AND encouragement."

D3 — CAPABLE BUT CAUTIOUS CONTRIBUTOR
  Competence: High (technically capable)
  Commitment: Variable (doubts own judgment)
  Example: Mid-level engineer who can do the work
           but second-guesses decisions
  Inner experience: "I know HOW to do this, but am I
                     making the right choice?"

D4 — SELF-RELIANT ACHIEVER
  Competence: High
  Commitment: High (confident; proactive)
  Example: Senior/staff engineer owning a domain
  Inner experience: "I own this. I just need you
                     to trust me and stay out of the way."
```

**THE FOUR LEADERSHIP STYLES:**

```
S1 — DIRECTING (High Task, Low Relationship)
  Behaviour: Tell. Instruct. Supervise.
  "Here is exactly what to do and how."
  Appropriate for D1
  Mistake: Using S1 on D4 → feels micro-managed

S2 — COACHING (High Task, High Relationship)
  Behaviour: Explain. Demonstrate. Encourage.
  "Here is how, and here is why. What questions do you have?"
  Appropriate for D2
  Mistake: Using S1 on D2 → ignores motivation dip

S3 — SUPPORTING (Low Task, High Relationship)
  Behaviour: Facilitate. Affirm. Involve.
  "What do you think you should do? I think you've got this."
  Appropriate for D3
  Mistake: Using S1 or S2 on D3 → signals distrust

S4 — DELEGATING (Low Task, Low Relationship)
  Behaviour: Empower. Observe. Trust.
  "Own this completely. Bring me decisions that need
   executive alignment or budget approval."
  Appropriate for D4
  Mistake: Using S4 on D1 → abandonment
```

---

### 🧪 Thought Experiment

**SETUP:**
You manage a full-stack team. Consider three engineers on the same task: "Build a new service using our new infrastructure stack (Kubernetes, Terraform, Datadog)."

**Engineer A — Recently joined; 2 years exp. total, 0 on this stack.**
Development level: D1 — enthusiastic but no competence on this stack.
Correct style: S1 Directing. Give explicit task breakdown, pair them with a senior for day 1, review work daily, unblock immediately.

**Engineer B — 4 years exp., has used Kubernetes before, but new to your specific Terraform patterns. Started confidently, hit complexity, now questions everything and misses standups.**
Development level: D2 — growing competence, dropped commitment.
Correct style: S2 Coaching. Pair programming sessions; explain the why of your Terraform patterns; frequent 1:1 check-ins; acknowledge difficulty + reaffirm confidence: "The first service is always the hardest with a new stack."

**Engineer C — 6 years exp., strong on all these tools. Brings decisions to you that they clearly already know the answers to.**
Development level: D3 — high competence, low commitment (self-doubt or habit of seeking validation).
Correct style: S3 Supporting. Ask "What do you think?" before answering. When they're right, affirm it: "That's exactly what I'd do." Your job is to build their decision-making confidence, not to give them decisions.

**THE INSIGHT:**
Three engineers, same task, three different development levels, three different required styles. Applying S1 to Engineer C is insulting and demotivating. Applying S4 to Engineer A is abandonment.

---

### 🧠 Mental Model / Analogy

> Situational Leadership is like adjusting the training wheels on a bicycle: you start with full support (both wheels touching the ground), then progressively raise them as the rider's confidence and competence grow, until you remove them entirely. The error is removing the training wheels before the rider is ready (S4 on D1), or leaving them on after the rider no longer needs them (S1 on D4). The goal is to move the rider to D4 on this bicycle, on this terrain, so that they own their own riding — and you spend your energy teaching the next rider.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Situational Leadership says match your management style to where each person is on each task: new and excited → tell them what to do; growing but struggling → coach with explanation; capable but uncertain → support and encourage; expert → get out of their way.

**Level 2 — How to use it (junior developer/new TL):**
In your 1:1s: (1) Identify the task you are discussing. (2) Assess development level for THAT task (not the person overall). (3) Choose your style accordingly. Ask yourself: "Is this person able AND willing on this specific task right now?" Able+Willing → Delegate. Able+Uncertain → Support. Growing Able, Flagging Will → Coach. Not Yet Able → Direct.

**Level 3 — How it works (engineering manager):**
The most common failure in technical leadership is misreading D3 as D4. D3 engineers are highly competent — they do the work correctly — but they over-check with you, ask for validation on decisions they know the answer to, or avoid accountability for outcomes. The leader misreads this as genuine competence (D4) and delegates fully, leading to the engineer feeling unsupported. The correct intervention for D3 is targeted affirmation: "What's your recommendation?" → when they answer correctly → "That's right. Make that call." Over several weeks, D3 shifts to D4 as the engineer builds confidence in their own judgment.

**Level 4 — Why it was designed this way (senior/staff):**
Situational Leadership is a prescriptive model with significant empirical support for its core claim (style matching improves outcomes) but contested evidence for the specific D-S mapping. The model's durable value is its framing of leadership as adaptive and developmental rather than stylistic. For senior/staff engineers who informally lead without managerial authority, the model translates directly: your informal influence is most effective when you correctly diagnose where your colleague is on a task and meet them there. Directing a D4 colleague is a political error (signals distrust); delegating to a D1 colleague is negligence. The implicit contract of situational leadership: the leader's job is to make themselves progressively unnecessary — moving people from D1 to D4 is the measure of leadership effectiveness.

---

### ⚙️ How It Works (Mechanism)

```
FOR EACH INDIVIDUAL + TASK:

1. DIAGNOSE DEVELOPMENT LEVEL
   Question 1: Competence — do they have the skills
               for this specific task?
   Question 2: Commitment — are they motivated/confident?

         Competence: Low  Medium  High
   Commitment:
   High              D1   →      D4
   Low/Variable      D2   D3

2. MATCH LEADERSHIP STYLE
   D1 → S1: Direct (tell, supervise, check frequently)
   D2 → S2: Coach (explain why, encourage, pair)
   D3 → S3: Support (ask their view, affirm, involve)
   D4 → S4: Delegate (set outcome, trust, stay available)

3. DEVELOP TOWARD D4
   Goal: move each person to D4 on this task
   Review regularly: has their D level changed?
   Adjust style as they develop
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
New assignment / task assigned
    ↓
Leader diagnoses development level
  for this person on this task
    ↓
[STYLE SELECTION ← YOU ARE HERE]
  D1 → S1: provide structure, check daily
  D2 → S2: explain, pair, encourage, check often
  D3 → S3: ask, affirm, involve, check occasionally
  D4 → S4: set context, delegate fully, check on milestones
    ↓
Monitor: is development level changing?
    ↓
Adjust style to match new level
    ↓
Goal achieved: person is D4 on this task
    ↓
Leader redirects attention to other tasks / team members
```

---

### 💻 Code Example

**Team leadership diagnostic:**

```python
from enum import Enum

class DevelopmentLevel(Enum):
    D1 = "Enthusiastic Beginner"
    D2 = "Disillusioned Learner"
    D3 = "Capable but Cautious"
    D4 = "Self-Reliant Achiever"

class LeadershipStyle(Enum):
    S1 = "Directing: tell, instruct, supervise"
    S2 = "Coaching: explain why, encourage, pair"
    S3 = "Supporting: ask, affirm, involve"
    S4 = "Delegating: set outcome, trust, stand by"

def diagnose_and_prescribe(
    competence_high: bool,
    commitment_high: bool
) -> tuple[DevelopmentLevel, LeadershipStyle]:
    """
    Map competence/commitment to development level
    and prescribe appropriate leadership style.
    """
    if not competence_high and commitment_high:
        return DevelopmentLevel.D1, LeadershipStyle.S1
    if not competence_high and not commitment_high:
        return DevelopmentLevel.D2, LeadershipStyle.S2
    if competence_high and not commitment_high:
        return DevelopmentLevel.D3, LeadershipStyle.S3
    return DevelopmentLevel.D4, LeadershipStyle.S4

# Weekly 1:1 check
level, style = diagnose_and_prescribe(
    competence_high=True,
    commitment_high=False   # D3: able but second-guessing
)
print(f"Development Level: {level.value}")
print(f"Recommended Style: {style.value}")
# → D3: Capable but Cautious
# → S3: Supporting — ask their view, affirm decisions
```

---

### ⚖️ Comparison Table

| Model                       | Key Concept               | Adaptive? | Focus                      | Best For                         |
| --------------------------- | ------------------------- | --------- | -------------------------- | -------------------------------- |
| **Situational Leadership**  | Match style to D level    | Yes       | Individual task competence | Day-to-day team leadership       |
| Servant Leadership          | Leader serves the team    | No        | Team needs overall         | Culture and psychological safety |
| Transformational Leadership | Inspire vision and change | Partially | Organisational change      | Culture shifts, company strategy |
| Transactional Leadership    | Reward/punish outcomes    | No        | Performance management     | Clear process environments       |
| Coaching Leadership         | Ask, don't tell           | No        | Development focus          | High D3/D4 teams                 |

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                              |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| "Situational Leadership means being inconsistent" | It means being adaptive — deliberately varying style based on what each person needs on each task                                    |
| "D4 means the person needs no support ever"       | D4 is task-specific. The same person is D1 on a new task; the leader re-diagnoses for each task                                      |
| "S1 (Directing) is controlling/authoritarian"     | S1 is appropriate and respectful for D1; it gives beginners the structure they need to succeed and builds confidence, not dependency |
| "Good leaders are always supportive/coaching"     | Defaulting to S3/S4 with a D1 person is negligence, not respect; it sets them up to fail                                             |
| "Move people from D1 to D4 is always linear"      | Development can regress (D4 → D3) with stress, role change, or new complexity; leaders re-diagnose continuously                      |

---

### 🚨 Failure Modes & Diagnosis

**Style Lock (Using One Style Regardless of D Level)**

**Symptom:** Manager always directs (micromanager) OR always delegates (absentee manager). Either team members feel controlled or unsupported, depending on the direction.

**Root Cause:** Manager applies their natural or preferred style rather than diagnosing the individual's development level.

**Diagnostic Questions for Manager Self-Assessment:**

```
1. In the last week, did you give detailed instructions to
   someone who already knows how to do the task?
   → Signs of S1 lock with D3/D4 people.

2. Did you delegate a task fully to someone who asked
   a lot of clarifying questions / seemed uncertain?
   → Signs of S4 lock with D1/D2 people.

3. For each direct report: when did you last explicitly
   change your approach based on what they needed?
   → If the answer is "I treat everyone the same,"
     that is style lock.
```

**Fix:** In next 1:1 for each direct report, ask yourself before the meeting: "Where is this person on their current main task? Am I planning to use the right style?"

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- No prerequisites; Situational Leadership is a foundational framework

**Builds On This (learn these next):**

- `Technical Leadership` — applies situational leadership within a technical team context
- `Mentoring vs Coaching` — the S2/S3 styles connect directly to coaching and mentoring approaches
- `Scope of Influence` — as a leader, your situational leadership approach builds the scope of your influence

**Alternatives / Comparisons:**

- `Technical Leadership` — the domain (technical teams) where situational leadership is most applied by engineers
- `Mentoring vs Coaching` — situational coaching style (S2/S3) overlaps with the mentoring and coaching distinction
- `Engineering Manager vs Tech Lead` — both roles require situational leadership, with different primary emphases

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Adapt leadership style to development     │
│              │ level of individual on specific task      │
├──────────────┼───────────────────────────────────────────┤
│ D LEVELS     │ D1: enthusiastic beginner                 │
│              │ D2: disillusioned learner                 │
│              │ D3: capable but cautious                  │
│              │ D4: self-reliant achiever                 │
├──────────────┼───────────────────────────────────────────┤
│ S STYLES     │ S1 Directing  → D1                        │
│              │ S2 Coaching   → D2                        │
│              │ S3 Supporting → D3                        │
│              │ S4 Delegating → D4                        │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULE     │ D level is task-specific, not person-     │
│              │ specific; re-diagnose for each new task   │
├──────────────┼───────────────────────────────────────────┤
│ GOAL         │ Move each person from D1 → D4 on each     │
│              │ task; make yourself progressively         │
│              │ unnecessary                               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Effective leadership is not a style —    │
│              │ it is an accurate diagnosis and a         │
│              │ matching response."                       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Technical Leadership →                    │
│              │ Mentoring vs Coaching                     │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You are an engineering manager with a team of five. One of your senior engineers (7 years exp.) has just been assigned as the technical lead for a new project using a technology stack she has never worked with before. Using the Situational Leadership framework, (a) diagnose her development level for this task, (b) describe the leadership style you would use with her for the first four weeks, (c) describe the signal that would tell you it is time to shift to a different style, and (d) describe the specific conversation you would have with her in week 1 to set expectations and establish the right working relationship for her development level.

**Q2.** A common criticism of Situational Leadership is that it places all of the diagnostic and adaptive responsibility on the leader, with no role for the person being led in the process. An alternative view is that leaders should be transparent about the Situational Leadership model with their team — explicitly discussing development levels and agreed leadership styles. What are the benefits and risks of making the Situational Leadership model explicit and collaborative (telling team members "I think you're at D2 on this task; here is how I plan to lead you")? Under what circumstances would transparency help, and under what circumstances would it be counterproductive?
