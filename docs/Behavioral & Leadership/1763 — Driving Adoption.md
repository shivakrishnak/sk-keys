---
layout: default
title: "Driving Adoption"
parent: "Behavioral & Leadership"
nav_order: 1763
permalink: /leadership/driving-adoption/
number: "1763"
category: Behavioral & Leadership
difficulty: ★★★
depends_on: Project Leadership, Influence Without Authority
used_by: Engineering Strategy, Project Leadership
related: Influence Without Authority, Project Leadership, Documentation Culture
tags:
  - leadership
  - advanced
  - adoption
  - change-management
  - staff-plus
---

# 1763 — Driving Adoption

⚡ TL;DR — Driving adoption is the work of getting engineers, teams, or users to actually use a new tool, platform, pattern, or practice that has been built or decided upon — the central insight is that shipping a solution is 50% of the work, and the adoption process (the other 50%) requires: making the right path the easy path, reducing friction to zero, building social proof, finding early adopters, and sustaining engagement long enough for habits to form; without deliberate adoption work, good solutions fail silently.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A platform team spends 6 months building a new internal developer platform — better CI, better logging, better deployment. They write documentation, send a Slack announcement, and wait. Adoption: 15% after 6 months. The other 85% of teams are still using the old system — because switching is work, and nobody has given them a compelling reason to switch now.

**THE BREAKING POINT:**
The pattern repeats across every type of technical change: new frameworks, new processes, new tools, new architectural patterns. The technical merit of the solution is insufficient to drive adoption on its own. Engineers are busy; switching has a cost; the old way works (even if imperfectly). Without deliberate adoption work, the path of least resistance is staying with what you have.

**THE INVENTION MOMENT:**
Everett Rogers' "Diffusion of Innovations" (1962) identified the adoption curve: innovators (2.5%), early adopters (13.5%), early majority (34%), late majority (34%), laggards (16%). The insight: you don't need to convince everyone at once — you need to convince the innovators and early adopters, who then provide social proof for the early majority. Technology adoption follows the same curve.

---

### 📘 Textbook Definition

**Adoption:** The process by which individuals or teams change their behaviour to use a new tool, pattern, process, or practice. Adoption is not awareness — awareness is knowing something exists; adoption is actually using it consistently.

**Diffusion of Innovations (Rogers):** A theory explaining how new ideas and technologies spread through a population over time. The five adopter categories (Innovators, Early Adopters, Early Majority, Late Majority, Laggards) have different risk tolerances and require different persuasion strategies.

**Making the right path the easy path:** The principle that adoption is maximised when using the new thing requires less effort than using the old thing — achieved by reducing friction (setup, integration, learning curve), providing good defaults, and making the new path the default, not the opt-in.

**Social proof:** The influence that the adoption behaviour of others has on one's own adoption decision. "If Team X is using this and it's working for them" is a more powerful argument for adoption than technical documentation.

**Early adopter:** A person or team who adopts early (before the majority), is willing to deal with rough edges, and provides feedback and social proof. Early adopters are the critical bridge between the innovators who build the solution and the early majority who represent mass adoption.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Adoption doesn't happen from an announcement and documentation — it requires making the new thing easier than the old thing, finding early adopters who create social proof, reducing friction to zero, and sustaining the effort until habits form.

**One analogy:**

> Driving adoption is like changing which side of the road a country drives on. Sweden did this in 1967 (Dagen H). The announcement alone would have failed catastrophically — people's existing habits (driving on the left) were deeply ingrained, infrastructure was built around it, and the risk of non-compliance was death. Sweden's strategy: change every road sign, paint all lanes, change all traffic lights, run a massive public education campaign, and choose a single switch date. The right path (right-side driving) was made literally impossible to avoid — infrastructure changes made the wrong path (left-side driving) physically harder. Adoption was 100% within days. The lesson: declarations don't drive adoption; changing the infrastructure of behaviour drives adoption.

**One insight:**
The most common adoption failure is treating adoption as a communication problem ("we just need to announce it better") rather than a friction problem ("using the new thing is harder than using the old thing"). Communication is necessary but never sufficient. If the new path has more friction than the old path: adoption will fail regardless of how good the announcement is.

---

### 🔩 First Principles Explanation

**ADOPTION STRATEGY FRAMEWORK:**

```
PHASE 1: EARLY ADOPTERS (Innovators + Early Adopters)

WHO TO TARGET:
  Teams or individuals who:
  - Experience the pain the new solution solves most acutely
  - Have enough slack to absorb a rough initial experience
  - Are respected by peers (their adoption creates social proof)
  - Will give honest, direct feedback

HOW TO ENGAGE:
  Personal outreach (not mass announcement)
  "We're looking for 2–3 teams to try this early. You'd be
   ideal because [specific reason]. We'll support you closely.
   Your feedback will shape the final product."

  Co-create the early experience:
  Pair with them during setup; fix friction points immediately
  Their rough spots become your polish list

GOAL:
  3–5 successful early adopters with testimonials
  Fix the top 5 friction points before broad launch

PHASE 2: REDUCING FRICTION TO ZERO

FRICTION AUDIT:
  Walk through the adoption process yourself as a new user
  Time every step; count every decision
  "Where would someone give up?"

  Common friction types:
  - Setup: "It takes 3 hours to get started"
  - Learning curve: "I have to learn X, Y, Z concepts"
  - Integration: "I have to change 15 files in my repo"
  - Unclear benefit: "I don't know why I should switch"
  - Risk: "I don't know what breaks if I try this"

FRICTION REDUCTION TACTICS:
  □ Getting started in < 5 minutes (zero-friction onboarding)
  □ Migration scripts for existing users
  □ Feature parity with old system (no regression)
  □ Fallback / rollback path clearly documented
  □ FAQ: "What happens to my [X] when I switch?"
  □ One-click setup or CLI tooling

PHASE 3: MAKING THE RIGHT PATH THE EASY PATH

MAKE NEW = DEFAULT:
  New repositories: scaffold uses the new pattern
  New services: template includes the new tool
  CI templates: include the new linting/testing approach
  "Opting out requires a decision; opting in is automatic"

DEPRECATE THE OLD PATH:
  Put the old path on a deprecation schedule
  "Old system: supported until [date]; security patches only"
  "Migration tool available at [link]; support available"
  Deadlines create urgency that announcements don't

PHASE 4: SOCIAL PROOF + COMMUNITY

TESTIMONIALS:
  Ask early adopters: "What's your experience been?"
  Document their answers; share widely
  "Team X migrated in 3 days. Here's their migration story."

METRICS THAT DEMONSTRATE VALUE:
  "Teams using the new CI see 40% faster build times"
  "Services on the new platform had 0 deployment incidents vs
   avg 2.3 incidents/quarter on the old system"
  Quantified value > promises

COMMUNITY:
  Slack channel for users of the new thing
  Regular office hours / Q&A sessions
  Share tips + learnings; build community ownership
  "Champions" in each team who know it well + can help peers

PHASE 5: MEASUREMENT + ITERATION

ADOPTION METRICS:
  % of eligible teams/users actively using it
  Time-to-adopt for new users (decreasing?)
  Support requests per adopter (decreasing = less friction)
  Net Promoter Score for early adopters

FEEDBACK LOOP:
  Regular feedback collection (Slack, survey, 1:1s)
  Fix friction points within sprint of identification
  Communicate fixes: "Based on your feedback, we've fixed X"
```

---

### 🧪 Thought Experiment

**SETUP:**
A platform team has built a new internal observability platform (better than the old one: faster, cheaper, better alerts). They announce it via email, write docs, and wait.

**Month 1:** 8% adoption. Team says "engineers are resistant to change."

**Month 3:** 12% adoption. Team adds more docs and runs another announcement.

**Month 6:** 15% adoption. Team considers mandating adoption.

**Root cause analysis:**

- Setup time: 2 hours (vs. 0 hours for the old system — which is already set up)
- Migration: requires rewriting alert configs (no migration tool)
- Benefit: unclear unless you dig into docs
- Social proof: none (nobody talks about their experience)
- Default: old system is default; new system is opt-in

**What the team should have done:**

1. Week 1: Personal outreach to 3 high-visibility teams with acute pain
2. Week 2: Co-migration with those teams; fix top friction points
3. Week 3: Migration script (automates 80% of config rewriting)
4. Week 4: New service template defaults to new platform
5. Week 6: Case study blog post from early adopters
6. Week 8: Old platform deprecated; migration support available
7. Month 3: 60% adoption

The difference is not communication volume — it's friction reduction + defaults + social proof + deprecation.

---

### 🧠 Mental Model / Analogy

> Adoption strategy follows the physics of water flowing downhill. Water always takes the path of least resistance — it doesn't need to be convinced; it responds to the shape of the terrain. Your job in driving adoption is to reshape the terrain so the path of least resistance leads toward the new solution. Every step you remove from setup, every migration script you write, every default you change, every deprecation deadline you set — these reshape the terrain. The announcement is just telling people the water flows this way now. The adoption happens because you've changed the landscape, not because you've made a compelling argument.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Driving adoption means making sure people actually use the new tool or process you've built — not just knowing it exists. This requires making the new thing easy to use, showing that others are using it successfully, and sometimes making the old way harder (or deprecated) to give people a reason to switch.

**Level 2 — How to use it (engineer):**
When you build something that others need to adopt: don't rely on an announcement. Personally reach out to 2–3 teams who would benefit most. Help them migrate. Use their experience to fix the top friction points. Then write a migration guide that reflects real difficulties. Get their testimonials. Make the new thing the default for new projects. Only then announce broadly.

**Level 3 — How it works (tech lead):**
Adoption work is often underestimated as "just communication." The reality: it requires a product mindset applied to the adoption experience. Define adoption metrics. Run friction audits. Build migration tooling. Create a deprecation schedule. Build a community. Treat the adoption experience like a product — with iterations and improvements based on user feedback.

**Level 4 — Why it was designed this way (principal/staff):**
At the principal/staff level, driving adoption of architectural standards, new platforms, or strategic technical directions is one of the highest-leverage activities available. A well-adopted engineering standard multiplies its value across every team and every project it touches. A poorly-adopted standard wastes the investment and leaves the ecosystem fragmented. The principal engineer who can drive adoption at scale — across teams, across org boundaries, sometimes across companies (open source) — is creating organisational leverage that dwarfs individual technical contributions.

---

### ⚙️ How It Works (Mechanism)

```
ADOPTION LIFECYCLE:

EARLY (0–20% adoption):
  Focus: find early adopters; remove critical friction
  Tactics: personal outreach; co-migration; rapid iteration
  Success metric: 3–5 successful adoptions; top 5 friction fixed
    ↓
GROWTH (20–60% adoption):
  Focus: social proof; defaults; migration tooling
  Tactics: case studies; new project defaults; deprecation schedule
  Success metric: adoption accelerating; support requests decreasing
    ↓
MAJORITY (60–80% adoption):
  Focus: remove the old path; support laggards
  Tactics: enforce deprecation; offer migration support; community
  Success metric: adoption continuing; old path declining
    ↓
COMPLETION (80%+ adoption):
  Focus: decommission old path; normalise new as standard
  Tactics: complete decommission; celebrate milestone
  Success metric: old path gone; new path is "how we do things"
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
New tool/platform/pattern built and ready
    ↓
[DRIVING ADOPTION ← YOU ARE HERE]
Identify early adopters (personal outreach)
    ↓
Co-migrate early adopters; fix friction
    ↓
Build migration tooling + documentation
    ↓
Make new = default for new projects
    ↓
Collect + share social proof (case studies, metrics)
    ↓
Set deprecation schedule for old path
    ↓
Broad announcement (with evidence + social proof)
    ↓
Track adoption metrics; iterate on friction points
    ↓
Old path decommissioned; new path is standard
```

---

### 💻 Code Example

**Adoption metrics tracker:**

```python
from dataclasses import dataclass

@dataclass
class AdoptionMetrics:
    tool_name: str
    eligible_teams: int
    adopted_teams: int
    avg_setup_hours: float
    support_tickets_per_team: float
    nps_score: float  # -100 to 100

    @property
    def adoption_rate(self) -> float:
        return round(self.adopted_teams / self.eligible_teams * 100, 1)

    @property
    def adoption_phase(self) -> str:
        rate = self.adoption_rate
        if rate < 20:
            return "Early — focus on friction reduction + early adopters"
        elif rate < 60:
            return "Growth — focus on social proof + defaults"
        elif rate < 80:
            return "Majority — focus on deprecation + laggard support"
        return "Complete — decommission old path"

    def friction_score(self) -> str:
        # lower setup time + lower support tickets = lower friction
        score = self.avg_setup_hours + (self.support_tickets_per_team * 10)
        if score < 2:
            return "Low ✓"
        elif score < 5:
            return "Medium — investigate friction points"
        return "High 🔴 — friction blocking adoption"

    def report(self) -> None:
        print(f"\n=== Adoption Report: {self.tool_name} ===")
        print(f"  Adoption:     {self.adoption_rate}% "
              f"({self.adopted_teams}/{self.eligible_teams} teams)")
        print(f"  Phase:        {self.adoption_phase}")
        print(f"  Friction:     {self.friction_score()} "
              f"(avg setup: {self.avg_setup_hours}h)")
        print(f"  NPS:          {self.nps_score}")

AdoptionMetrics(
    tool_name="Internal Observability Platform v2",
    eligible_teams=40,
    adopted_teams=7,
    avg_setup_hours=2.5,
    support_tickets_per_team=3.2,
    nps_score=22,
).report()
```

---

### ⚖️ Comparison Table

| Adoption strategy                   | Works for                                  | Risk                                               |
| ----------------------------------- | ------------------------------------------ | -------------------------------------------------- |
| **Announcement only**               | Almost never                               | 5–15% adoption ceiling                             |
| **Documentation + announcement**    | Low-friction tools; highly motivated users | Still limited without social proof                 |
| **Early adopters → social proof**   | Medium-friction tools                      | Requires patient iteration phase                   |
| **Defaults + early adopters**       | All tools                                  | Requires build effort for defaults/tooling         |
| **Defaults + deprecation schedule** | Platform-level changes                     | Requires organisational authority to set deadlines |

---

### ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                                                                                             |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Engineers are resistant to change"       | Engineers are resistant to friction. Remove friction: adoption follows.                                                                             |
| "Better documentation will fix adoption"  | Documentation reduces one type of friction (knowledge). If the main friction is setup time, documentation doesn't help.                             |
| "If we mandate it, they'll adopt it"      | Mandates without support create resentment and workarounds. Mandates work only when paired with migration support and reduced friction.             |
| "Social proof is a marketing technique"   | Social proof is how engineers make decisions under uncertainty. "My colleague says it's good" is often the most trusted adoption signal.            |
| "Adoption is the platform team's problem" | Any engineer who builds something others need to use is responsible for driving adoption. It's a product problem, not a communication team problem. |

---

### 🚨 Failure Modes & Diagnosis

**"Announce and Pray" — Passive Adoption Strategy**

**Symptom:** Team builds a great internal tool. Sends one Slack announcement with a link to the docs. Adoption: 8%. Team sends another announcement 3 months later. Adoption: 11%. Team considers "making it mandatory." Engineers who are forced to use it spend the minimum time on it, complain, and look for workarounds.

**Root Cause:** The team treats adoption as a communication problem (we just need to tell people about it) rather than a product problem (we need to make using this better than not using it).

**Fix:**

```
ADOPTION SPRINT PLAN:

WEEK 1: FRICTION AUDIT
  Walk through adoption as a new user
  Document every friction point (time each step)
  Identify: what would make someone give up?

WEEK 2–3: EARLY ADOPTER ENGAGEMENT
  Personally reach out to 2–3 teams
  "We want your feedback. We'll help you migrate.
   Your experience shapes the product."
  Co-migrate with them; take notes on every friction

WEEK 4: FIX TOP 5 FRICTION POINTS
  Build migration tooling; improve getting started docs
  Reduce setup from 2h to 30min (target)
  Fix the most common support questions

WEEK 5: COLLECT SOCIAL PROOF
  "What was your experience? What improved for you?"
  Document as case study or quote

WEEK 6: CHANGE DEFAULTS
  New service template → uses new tool
  New repo scaffold → new pattern is default
  Opt-out requires a decision; opt-in is automatic

WEEK 8: ANNOUNCEMENT (NOW)
  Include: case study + metrics + 30-min setup guide
  Include: "Teams X, Y, Z are already using it; here's
           what they experienced"
  Include: migration support availability

MONTH 3: DEPRECATION NOTICE
  "Old system: maintenance mode from [date]"
  "Migration support available until [date]"
  This creates urgency. Urgency drives adoption.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Project Leadership` — building the thing is phase 1; driving adoption is phase 2
- `Influence Without Authority` — driving adoption across team boundaries requires influencing without authority

**Builds On This (learn these next):**

- `Documentation Culture` — good documentation is a prerequisite for self-serve adoption
- `Writing for Engineers` — the communication skills that make adoption materials effective

**Alternatives / Comparisons:**

- `Influence Without Authority` — the cross-team leadership skill that adoption work requires
- `Project Leadership` — the initiative delivery skill that produces the thing to be adopted

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PHASE 1     │ Early adopters: personal outreach;         │
│             │ co-migrate; fix top 5 friction points      │
├─────────────┼──────────────────────────────────────────-─┤
│ PHASE 2     │ Social proof + defaults + migration        │
│             │ tooling + deprecation schedule             │
├─────────────┼──────────────────────────────────────────-─┤
│ KEY RULE    │ Right path = easy path                     │
│             │ Old path = deprecated (not just unloved)  │
├─────────────┼──────────────────────────────────────────-─┤
│ ADOPTION    │ Adoption rate; setup time; support         │
│ METRICS     │ tickets/team; NPS score                   │
├─────────────┼──────────────────────────────────────────-─┤
│ ANTI-PATTERN│ "Announce and pray" — treating adoption    │
│             │ as communication not product problem       │
├─────────────┼──────────────────────────────────────────-─┤
│ NEXT EXPLORE│ Influence Without Authority →              │
│             │ Documentation Culture                    │
└─────────────┴────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Rogers' Diffusion of Innovations theory suggests that "laggards" (the last ~16% to adopt) are resistant not because of stubbornness but because of rational risk-aversion: they have the most to lose from a bad adoption experience and the least slack to recover from disruption. Design an adoption strategy specifically for the laggard segment in an internal platform migration — what do they need that early adopters didn't? How do you reduce their risk without giving them a veto over the migration timeline?

**Q2.** Platform teams often face a dilemma: if they set a deprecation deadline for an old system before the new system is fully polished, engineers get frustrated with a forced migration to a rough product. If they wait until the new system is perfect before setting a deadline, adoption stalls because there's no urgency. Design a "deprecation trigger" framework: what criteria should determine when to announce a deprecation deadline, and what minimum quality bar must the new system meet before a deadline is credible? Include: how to communicate the deprecation in a way that creates urgency without resentment.
