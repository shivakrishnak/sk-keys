---
layout: default
title: "Career Laddering"
parent: "Behavioral & Leadership"
nav_order: 1769
permalink: /leadership/career-laddering/
number: "1769"
category: Behavioral & Leadership
difficulty: ★★★
depends_on: OKRs, Feedback (Giving and Receiving)
used_by: Personal Brand (Engineering)
related: Personal Brand (Engineering), Feedback (Giving and Receiving), Influence Without Authority
tags:
  - leadership
  - advanced
  - career
  - promotion
  - staff-engineering
---

# 1769 — Career Laddering

⚡ TL;DR — Career laddering is the structured framework that defines what engineering seniority means at each level (L3 → L6+), how promotions actually work (scope of impact, not years of service), and what differentiates IC (individual contributor) from management tracks — understanding the levelling system lets engineers intentionally work at the next level before the promotion, identify gaps in their promotion case, and navigate the sponsor-vs-mentor distinction that determines whether a promotion actually happens.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An engineer at a mid-size tech company has been a senior engineer (L5) for three years. They work hard, their code quality is excellent, their team respects them. Every year at review time, their manager says "keep up the good work — I think you're making progress." The engineer believes they are being promoted methodically. After year 3, they are passed over for promotion again. The explanation: "You haven't demonstrated impact at the staff level." The engineer doesn't know what "staff level impact" means. Nobody explained it to them. They leave for a company that will give them a staff title.

**THE HIDDEN SYSTEM:**
Career laddering is not a meritocracy in the intuitive sense. It is a scope-and-influence game. Impact at each level is defined in terms of scope — the radius of problems you solve. Getting promoted requires not just doing excellent work at your current level but demonstrating consistent, sustained work at the next level before the promotion happens. Most engineers don't know this. They optimise for the current level rather than investing in the next level's scope.

**THE INVENTION MOMENT:**
Modern career laddering frameworks were formalised by companies like Google, Microsoft, and Amazon in the 2000s as they scaled past the point where promotion decisions could be made by individual managers. The public discourse on staff+ engineering was systematised by Will Larson's "Staff Engineer" (2021) and his concept of staff+ archetypes.

---

### 📘 Textbook Definition

**Individual Contributor (IC) track:** The engineering career path where advancement is based on technical scope and impact without people management responsibilities. Typical progression: Junior → Mid → Senior → Staff → Principal → Distinguished → Fellow.

**Management track:** The engineering career path that transitions from coding to people management: Senior → Engineering Manager → Senior EM → Director → VP → SVP → CTO.

**Scope of impact:** The radius of problems an engineer is expected to solve and influence. Junior: task. Senior: team. Staff: cross-team. Principal: organisation. Distinguished/Fellow: industry.

**Staff+ engineering:** The levels above Senior IC (Staff, Principal, Distinguished, Fellow) where the primary contribution shifts from individual technical execution to enabling other engineers, shaping technical direction, and solving organisation-scale problems.

**Sponsor vs. mentor:** A mentor gives you advice. A sponsor advocates for you in rooms you're not in — at promo committees, in calibration discussions, in conversations with senior leaders. Promotions require sponsors; mentors alone are insufficient.

**Promotion packet:** The written document assembled by the engineer and manager summarising the case for promotion: evidence of work at the next level, impact, scope, cross-functional influence, and technical contribution. The artefact on which the promo committee makes their decision.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Career laddering is the system by which engineering seniority is defined and advancement is earned — promotions go to engineers who have already been operating at the next level for 6–12 months and who have sponsors advocating for them, not just managers who agree they deserve it.

**One analogy:**

> Career advancement in engineering is like a job interview where the interview is the last 12 months of your work. The promo committee is not asking "is this person good?" They're asking "has this person already been doing the work of the next level?" You don't get promoted and then do the next-level work. You do the next-level work and then get recognised for it. The promotion is retroactive, not prospective. Engineers who treat the promotion as the starting gun — "I'll start doing staff work after I get the staff title" — never get promoted. Engineers who treat the current level as the floor — "I'll be operating at staff before I ask for the title" — almost always get promoted eventually.

**One insight:**
The most common promotion failure pattern is operating in the **IC trap**: doing excellent individual work, solving complex technical problems, writing great code — at your current level. This makes you a reliable, valued engineer at your current level. It does not make you a candidate for the next level. The next level requires a wider scope: influencing decisions across teams, enabling other engineers to be more effective, or solving problems that no individual could solve alone. The scope expansion is the promotion, not the title.

---

### 🔩 First Principles Explanation

**THE IC LEVELLING FRAMEWORK:**

```
LEVEL OVERVIEW (common industry mapping):

L3 / Junior:
  Scope: assigned tasks; well-defined problems
  Autonomy: supervised; frequent check-ins
  Technical: implements solutions designed by others;
             grows proficiency
  Communication: within immediate team
  Promotion bar: consistent delivery; growing independence

L4 / Mid-level:
  Scope: features; small projects; well-defined problems
  Autonomy: works independently with occasional guidance
  Technical: designs solutions for well-scoped problems;
             reviews code of junior engineers
  Communication: within team; interfaces with PM, design
  Promotion bar: delivers features independently; mentors L3s;
                identifies problems without being told

L5 / Senior:
  Scope: complex features; team-level projects;
         multi-sprint deliverables
  Autonomy: fully independent; helps define what to build
  Technical: leads technical design; handles ambiguous problems;
             raises codebase quality
  Communication: cross-team; influences technical decisions
  Promotion bar: consistent cross-team impact; technical
                leadership; drives the team's technical direction

L6 / Staff:
  THE HARDEST TRANSITION:
  Scope: cross-team / multi-team; company-level technical problems
  Autonomy: creates their own work; identifies the right problems
  Technical: shapes technical strategy; enables other teams;
             solves problems that require coordinating multiple teams
  Communication: department-wide; VP+ visibility; external
  Key shift: FROM "does the right thing" TO "identifies what the
             right thing is" at the organisational level
  Promotion bar: clear cross-team impact; multiplies others;
                operates without a manager defining their work

L7 / Principal:
  Scope: organisation-wide; multi-year technical direction
  Key shift: "what should our technical strategy be in 2 years?"
  Often: technical equivalent of Director-level scope
  Promotion bar: organisation-shaping technical decisions;
                mentors staff engineers; drives multi-year vision

L8+ / Distinguished / Fellow:
  Scope: industry-wide; company-defining technical work
  Rare; typically < 20 people at any major tech company
  Promotion: more like winning an award than a review process
```

**THE STAFF+ ARCHETYPES (Will Larson):**

```
Most staff engineers are not the same. Larson identifies 4 archetypes:

TECH LEAD (most common):
  Context: embedded in a team; leads technical direction
  Focus: team's technical quality; design decisions; execution
  Work: RFC authorship; design review; architectural decisions
  Influence: within the team; immediate collaborators

ARCHITECT:
  Context: responsible for a domain / platform
  Focus: technical direction across many teams for a specific area
  Work: technical strategy documents; standards; platform design
  Influence: many teams; often horizontal (platform) not vertical

SOLVER (rarest):
  Context: floats between teams; attacks hard problems
  Focus: the most difficult technical problems in the organisation
  Work: deep technical investigation; fixes problems others can't
  Influence: follows the problem; not tied to a specific team

RIGHT HAND:
  Context: amplifies an executive (VP or C-level)
  Focus: execution of technical strategy at the org level
  Work: represents VP; identifies cross-cutting problems; drives
        org-level technical decisions
  Influence: through the executive they support; wide and indirect

WHY ARCHETYPES MATTER:
  Your manager may be comparing your staff case against the
  "tech lead" archetype (most common) when you are operating
  as a "solver". Understanding your archetype helps you articulate
  your impact in the language your promo committee expects.
```

**HOW PROMOTIONS ACTUALLY WORK:**

```
THE PROMOTION MECHANISM (calibration-based):

STEP 1: MANAGER SUBMITS PROMO PACKET
  Manager assembles evidence of your work at the next level.
  Typically includes: project descriptions, impact statements,
  cross-functional praise, technical leadership examples.
  YOU should be the primary contributor to this document.

STEP 2: CALIBRATION MEETING (you are not in the room)
  A committee of senior engineers and managers reviews
  promotion cases across the organisation.
  They compare candidates against:
    - The level rubric (scope, impact, technical complexity)
    - Other candidates at the same level
    - Available "slots" (in some companies, promotions are
      constrained by headcount ratios)

STEP 3: SPONSOR ADVOCACY (critical)
  Your case is evaluated by people who may not know you personally.
  Your sponsor — typically your manager + 1–2 senior engineers
  who know your work — must actively advocate for you.
  "Alice is a clear yes — she's been doing staff work for 8 months"
  is the statement that wins promotions.
  Absence of a sponsor = "nice person, not sure" = no promotion.

STEP 4: DECISION + TIMING
  Even strong cases may be timed to budget cycles.
  "Not this cycle" does not always mean "not ready."

WHAT THE COMMITTEE IS NOT DOING:
  Not: evaluating whether you are a good person
  Not: deciding if you deserve it based on loyalty or time served
  Not: comparing your code quality to a standard

WHAT THE COMMITTEE IS DOING:
  Comparing your scope of impact to the rubric for the next level
  Evaluating whether you have sponsors advocating for you
  Assessing whether this is the right moment (budget, timing)
```

**PROMOTION ANTI-PATTERNS:**

```
ANTI-PATTERN 1: DOING THE WORK WITHOUT VISIBILITY
  Problem: You are doing staff-level work but only your manager
           knows about it. The calibration committee has never
           heard your name.
  Fix: Write RFCs. Present in all-hands. Get credit for your impact
       in writing. Build relationships with senior leaders who will
       be in the calibration room.

ANTI-PATTERN 2: WAITING FOR PERMISSION
  Problem: "My manager knows I want to be promoted. I'm waiting
           for them to tell me I'm ready."
  Fix: Have an explicit conversation: "I want to be at L6 in 18
       months. What does my gap look like? What would 'ready' look
       like?" Then build a plan and drive it — don't wait.

ANTI-PATTERN 3: SCOPE CREEP CONFUSION
  Problem: "I'm doing work at the next level" but the work is
           more complex individual-contributor work, not wider-scope
           work. A senior engineer who writes a very complex
           algorithm is not doing staff work — they're doing excellent
           senior work.
  Fix: Scope means radius (team → cross-team → org), not complexity.
       Explicitly track: which problems you've solved that required
       coordinating across teams, influencing decisions outside your
       org, or enabling other engineers to be more effective.

ANTI-PATTERN 4: CONFUSION BETWEEN MENTOR AND SPONSOR
  Problem: "I have great relationships with [senior engineer] and
           [principal engineer] — they mentor me regularly."
  Reality: Mentors give advice. Sponsors advocate in rooms you're
           not in. Having 5 mentors who don't attend calibration
           is worth less than having 1 sponsor who says "Alice is
           a clear yes" in the calibration room.
  Fix: Identify who will be in the calibration room. Build
       relationships with those people. Do work they can see.
       Ask explicitly: "Would you be willing to advocate for my
       case at calibration?"
```

---

### 🧪 Thought Experiment

**SETUP:**
Two senior engineers at a tech company. Both strong engineers. Both want to reach staff level. Both have been senior for 2 years.

**Engineer A:** Does excellent senior work. Reviews code carefully, delivers complex features, is well-liked. Mentored by a principal engineer. Assumes their manager will submit a promo packet when the time is right.

**Engineer B:** Explicitly asks their manager: "What does my staff case look like? What is missing?" Learns the answer: "You need cross-team impact. You need to be visible to [VP of Engineering]." Volunteers to lead a cross-team RFC on a shared platform problem. Presents the RFC at a tech talk attended by 40 engineers including 3 staff engineers and 1 VP. Gets invited to the architectural review board as a result. Builds a direct relationship with the Staff engineer who will be in calibration. Has an explicit conversation: "I'd appreciate your advocacy when my case comes up."

**Outcome 18 months later:**

- Engineer A: not promoted ("not enough cross-team visibility; waiting for a stronger case")
- Engineer B: promoted to Staff ("clear cross-team impact; consistent advocacy from [Staff engineer]")

The delta: Engineer B treated promotion as a project with deliverables, sponsors, and an explicit timeline — not a passive outcome of doing good work.

---

### 🧠 Mental Model / Analogy

> Career laddering is like earning a graduate degree where you're the professor. You can't take a test to get promoted. The advancement happens when the institution recognises that you have already been operating at the next level of scope and impact — consistently, visibly, with the endorsement of people who have credibility in the room where the decision is made. The graduation ceremony is the recognition; the education is the 12 months of work you did before anyone started your "case." Engineers who want to be promoted and then do the next-level work have the sequence backwards. Engineers who do the next-level work and then ask for recognition have the sequence right.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Career laddering is the system that defines what each level of engineer means and how you move between levels. Getting promoted doesn't happen because you've been at a company a long time or because you're a good person. It happens when you've been doing the work of the next level — a wider scope of problems, more independence, more influence across teams — for long enough that the organisation recognises it.

**Level 2 — How to use it (engineer):**
Understand your company's levelling rubric for the next level — if you don't have it, ask your manager to share it. Map your current work against the rubric: where are the gaps? Then explicitly work to fill them. Have a direct conversation with your manager: "What would a compelling case for [next level] look like from me? What do I need to demonstrate that I'm not demonstrating today?" Identify who will advocate for you in the calibration room — that is your sponsor, and building that relationship is as important as the work itself.

**Level 3 — How it works (tech lead):**
At the tech lead level, you are likely approaching the senior-to-staff transition — the hardest one in the IC track. The key insight: staff is not "better senior." It is a different job. Senior: you solve the hard technical problems your team has. Staff: you identify the right problems across teams for the organisation to solve. This requires working on cross-cutting concerns, writing RFC proposals that span multiple teams, influencing technical direction you don't own, and making other engineers more effective. If your work in the last 6 months could have been done by a very capable senior engineer without anyone outside your team noticing a difference — you haven't been doing staff work yet.

**Level 4 — Why it was designed this way (principal/staff):**
At the principal/staff level, you are often involved in calibration for others. The calibration experience teaches you how the system actually works: it is a semi-quantitative comparison across a pool of candidates against a shared rubric, mediated by advocacy. Two equal candidates with equal work: the one with the sponsor who says "I can personally vouch for this person's impact on Project X" wins. This is not political — it is the system using the distributed knowledge of senior engineers (who saw the work) to supplement the rubric (which can only capture what was written down). As a staff engineer, your job in calibration is to be the honest advocate for the engineers you've worked with — not to champion everyone, but to provide specific, grounded evidence for the candidates you've actually observed.

---

### ⚙️ How It Works (Mechanism)

```
THE PROMOTION READINESS ASSESSMENT:

FOR EACH CRITERION IN THE NEXT LEVEL RUBRIC:
  1. Do you have a concrete example of meeting this criterion?
  2. Is the example visible? (Written up? Presented? Known to sponsors?)
  3. Is it at the right scope? (Team vs. cross-team vs. org)
  4. Is it consistent? (One example is not sufficient; pattern is required)

GAP ANALYSIS:
  "I have examples for 7 of 10 criteria."
  "Gap areas: cross-team influence; org-level technical vision"
  "Project to fill gap: lead the shared observability platform RFC"

SPONSOR IDENTIFICATION:
  Who attends calibration for my level?
  Who has seen my work at the next-level scope?
  Who has credibility with the calibration committee?
  Do I have an explicit conversation with them about sponsorship?

TIMELINE:
  Typical: 6–12 months of consistent next-level operation before
           a strong promo case can be assembled.
  Early conversations with manager: 12 months before target promo
  Promo packet draft: 3 months before target promo
  Sponsor conversations: ongoing; explicit ask 2 months before
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Current level — working effectively
    ↓
[CAREER LADDERING ← YOU ARE HERE]
Obtain + review next-level rubric
    ↓
Gap analysis: which criteria am I not yet meeting?
    ↓
Identify scope-expanding opportunities (cross-team projects,
RFCs, platform work)
    ↓
Operate at next-level scope for 6–12 months
    ↓
Build visibility: RFCs, tech talks, external engineering writing
    ↓
Identify + cultivate sponsors (not just mentors)
    ↓
Explicit conversation with manager: "Am I ready?"
    ↓
Manager assembles promo packet (you contribute primary content)
    ↓
Calibration — sponsor advocacy — decision
    ↓
Promotion → repeat at next level
```

---

### 💻 Code Example

**Promotion packet structure:**

```markdown
# Promotion Packet: Alice Chen — L5 → L6 (Senior → Staff)

**Prepared by:** Alice Chen + Manager Bob Lee
**Review cycle:** H1 2025
**Time at L5:** 2 years 4 months

## Summary Paragraph (2–3 sentences)

Alice has been operating at the L6 scope for 8 months, leading
the cross-team Observability Platform initiative (4 teams, 20+
engineers), driving the company's migration to OpenTelemetry, and
establishing the technical direction for platform services across
the infrastructure organisation. Her impact is consistently
acknowledged at the Director level and above.

## Impact at Next Level (L6 Criteria)

### Criterion: Cross-team technical leadership

**Rubric:** Leads technical direction across multiple teams; creates
alignment on complex cross-cutting decisions.

**Evidence:**

- Led RFC-0047 (Observability Platform): co-authored with 3 other
  senior engineers, aligned 4 teams on a unified approach, approved
  by VP Engineering in Feb 2025.
- Drove 2-quarter migration to OpenTelemetry across 12 services;
  reduced observability toil by ~40% team-wide (quantified in
  Q1 OKR report).
- Created and facilitates weekly Platform Review meeting (8 engineers
  across 3 teams); resolves cross-team architectural conflicts without
  escalation.

### Criterion: Multiplies other engineers

**Rubric:** Makes the team around them meaningfully more effective.

**Evidence:**

- Designed observability library used by 12 services; reduced
  instrumentation time from ~1 day to ~2 hours (measured over
  Q4 rollout).
- Authored "Observability Standards Guide" (1,400 views on
  internal wiki); cited as resource in 3 other teams' onboarding docs.

## External Feedback (peer/cross-functional)

[Quotes from 3–5 engineers who worked with Alice cross-functionally]
"Alice's RFC unblocked a 6-month-stalled decision in our team..."
"She was the reason the observability migration actually happened..."

## Summary of Gaps + How Addressed

[Honest assessment of where Alice was 12 months ago and what changed]
```

---

### ⚖️ Comparison Table

| Level              | Scope          | Autonomy         | Key shift                      |
| ------------------ | -------------- | ---------------- | ------------------------------ |
| **Junior (L3)**    | Task           | Supervised       | Learning the craft             |
| **Mid (L4)**       | Feature        | Independent      | Owns delivery                  |
| **Senior (L5)**    | Team           | Self-directed    | Leads technical quality        |
| **Staff (L6)**     | Cross-team     | Creates own work | Identifies the right problems  |
| **Principal (L7)** | Org            | Strategic        | Shapes multi-year direction    |
| **EM**             | People + team  | Manages          | Output through others          |
| **Director**       | Multiple teams | Org strategy     | Business + technical alignment |

---

### ⚠️ Common Misconceptions

| Misconception                            | Reality                                                                                                                                                        |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Promotion is based on years of service" | Promotion is based on demonstrated scope at the next level. An engineer at L5 for 5 years has not earned promotion by waiting.                                 |
| "Staff is just very good senior"         | Staff is a different job: identifying and solving cross-team problems vs. solving complex team problems. The scope expands, not just the difficulty.           |
| "My manager will tell me when I'm ready" | Managers are often unclear about readiness and reluctant to have the direct conversation. Ask explicitly and repeatedly: "What is missing from my staff case?" |
| "Having a mentor = having a sponsor"     | Mentors give advice. Sponsors advocate in rooms you're not in. Promotions require sponsors.                                                                    |
| "Working hard and being good is enough"  | Visibility + advocacy + scope are necessary alongside strong work. Invisible excellent work does not promote.                                                  |

---

### 🚨 Failure Modes & Diagnosis

**The Invisible Excellent Engineer — Excellent Work, No Promotion**

**Symptom:** An engineer writes excellent code, delivers complex features on time, is well-respected by their immediate team, and has been at senior level for 3+ years. At every calibration, the feedback is: "Not enough cross-team visibility. Needs more organisational impact." The engineer is frustrated: "I do better work than the people who are getting promoted."

**Root Cause:** The engineer is optimising for depth (excellent individual contribution) rather than breadth (scope expansion). The engineers getting promoted are doing work that is visible across the organisation — RFCs, tech talks, cross-team projects — even if their individual code quality is comparable or lower.

**Fix:**

```
VISIBILITY STRATEGY FOR THE INVISIBLE ENGINEER:

STEP 1: IDENTIFY A CROSS-TEAM PROBLEM
  Look for: shared pain across multiple teams;
            a coordination problem nobody is solving;
            a platform opportunity that multiple teams need
  Ask: "What problem, if solved, would make 3+ teams more effective?"

STEP 2: WRITE THE RFC
  Propose the solution. Circulate it. Get feedback.
  The RFC is the visibility artefact — it puts your thinking
  in front of people who don't work with you daily.

STEP 3: PRESENT TO A BROAD AUDIENCE
  Tech talk: internal; 30 minutes; open to all engineers
  All-hands: brief update on the initiative
  Email summary to VP when the project lands
  Goal: senior engineers and managers who don't know you
        should know your name and work.

STEP 4: ASK FOR FEEDBACK FROM SENIOR ENGINEERS
  "I'm working toward staff level. I'd value 30 minutes to
   get your perspective on what my case looks like and what's
   missing." Senior engineers are usually happy to help;
   the conversation often leads to sponsorship.

STEP 5: BUILD THE EXPLICIT SPONSOR RELATIONSHIP
  "When my case comes up in calibration, would you be willing
   to advocate for it? I'd like to make sure you have the
   context you need to do that."

TIMELINE: 6–12 months of this, consistently, before calibration.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `OKRs` — career advancement requires defining goals with measurable outcomes
- `Feedback (Giving and Receiving)` — promotion requires clear feedback loops with your manager

**Builds On This (learn these next):**

- `Personal Brand (Engineering)` — the external visibility dimension of career advancement

**Alternatives / Comparisons:**

- `Personal Brand (Engineering)` — external brand vs. internal levelling; complementary
- `Influence Without Authority` — the cross-team influence that drives staff-level scope

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ LEVELS      │ Junior → Mid → Senior → Staff →            │
│             │ Principal → Distinguished → Fellow         │
├─────────────┼──────────────────────────────────────────-─┤
│ SCOPE       │ Task → Feature → Team → Cross-team → Org   │
│             │ Scope expansion = level advancement        │
├─────────────┼──────────────────────────────────────────-─┤
│ PROMO LAW   │ Do next-level work FIRST; title comes after │
│             │ 6–12 months consistent next-level scope    │
├─────────────┼──────────────────────────────────────────-─┤
│ SPONSOR     │ Mentor = advice. Sponsor = advocates in     │
│             │ rooms you're not in. Need SPONSORS.        │
├─────────────┼──────────────────────────────────────────-─┤
│ STAFF       │ Staff ≠ better senior. Different job:       │
│             │ identify org-level problems; multiply teams │
├─────────────┼──────────────────────────────────────────-─┤
│ NEXT EXPLORE│ Personal Brand (Engineering) →             │
│             │ Influence Without Authority              │
└─────────────┴────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The Staff Engineer promotion is widely considered the hardest transition in the IC track — harder than all subsequent promotions. Most senior engineers plateau here for 3–5 years or never make it. Based on the scope and archetype framework: what specifically makes the senior-to-staff transition harder than junior-to-mid or mid-to-senior? Is it a skill acquisition problem (engineers need different skills) or a system problem (the promotion mechanism is harder), or both? Design a structured 12-month plan for a strong senior engineer to build a staff-level promotion case.

**Q2.** Many engineering organisations have a "dual-track" career ladder (IC and management) where both paths converge at the Director/VP level. Critics argue this creates a glass ceiling for ICs (Staff/Principal are paid less than equivalent-seniority managers and have less organisational influence), while proponents argue it allows excellent engineers to stay technical without taking on people management. Evaluate both sides: does the dual-track system actually work for ICs, or is it a retention mechanism that underpays technical leadership? What would a well-designed career ladder look like for ICs at the staff+ level?
