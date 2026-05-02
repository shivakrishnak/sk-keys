---
layout: default
title: "Conflict Resolution"
parent: "Behavioral & Leadership"
nav_order: 1749
permalink: /leadership/conflict-resolution/
number: "1749"
category: Behavioral & Leadership
difficulty: ★★☆
depends_on: Feedback (Giving and Receiving), Psychological Safety
used_by: Cross-Functional Collaboration, Stakeholder Communication
related: Feedback (Giving and Receiving), Psychological Safety, Cross-Functional Collaboration
tags:
  - leadership
  - communication
  - intermediate
  - conflict
  - negotiation
---

# 1749 — Conflict Resolution

⚡ TL;DR — Conflict resolution in engineering is the structured practice of addressing disagreements — using the Thomas-Kilmann framework to choose the right conflict style, distinguishing task conflict (disagreement about the work) from relationship conflict (personal friction), and applying principled negotiation (Fisher/Ury) to find solutions that address the underlying interests of both parties rather than their stated positions — turning conflict from a team dysfunction into a source of better decisions.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Two senior engineers disagree on architecture. Neither surfaces it in the design review — the disagreement is visible in passive-aggressive code review comments and in separate conversations with the EM, each lobbying for their approach. The design proceeds with unresolved ambiguity. At implementation, the two interpretations collide. The sprint fails. Three weeks later, the conflict surfaces as a formal complaint. The EM has to intervene in what could have been a 20-minute conversation.

**THE BREAKING POINT:**
Conflict is inevitable in engineering: engineers with different technical philosophies, product managers with different priority judgements, teams with competing roadmap requests. Unresolved conflict does not disappear — it goes underground and surfaces as passive resistance, decision avoidance, reduced psychological safety, and team attrition. The cost of avoided conflict is much higher than the cost of addressed conflict.

**THE INVENTION MOMENT:**
The Thomas-Kilmann Conflict Mode Instrument (1974) provided a framework for categorising conflict styles. Fisher and Ury's "Getting to Yes" (1981) introduced principled negotiation — separating positions from interests — as an alternative to positional bargaining. Amy Edmondson's research on psychological safety (1999) established that high-performing teams do not avoid conflict; they resolve it earlier and more openly.

---

### 📘 Textbook Definition

**Task conflict:** Disagreement about the work itself — technical approaches, priorities, requirements, timelines. Task conflict, when resolved well, improves decision quality: it surfaces assumptions, exposes trade-offs, and tests ideas. Some task conflict is healthy and desirable.

**Relationship conflict:** Personal friction — dislike, distrust, perceived disrespect. Relationship conflict consistently degrades team performance. It often originates from mishandled task conflict or from patterns of communication that feel dismissive or aggressive.

**Thomas-Kilmann Conflict Modes (5 styles):** Competing (high assertive, low cooperative), Collaborating (high assertive, high cooperative), Compromising (medium on both), Avoiding (low assertive, low cooperative), Accommodating (low assertive, high cooperative). Each mode is appropriate in specific circumstances.

**Principled Negotiation (Fisher/Ury):** Negotiation focused on interests (underlying needs and concerns) rather than positions (stated demands). Four principles: separate people from the problem; focus on interests, not positions; invent options for mutual gain; insist on objective criteria.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Effective conflict resolution distinguishes the person from the problem, focuses on underlying interests rather than stated positions, and chooses the appropriate response style for the situation — turning disagreement into better outcomes rather than relationship damage.

**One analogy:**
> Unresolved conflict is like a silent memory leak. The process appears to run fine; the team ships work; standups are calm. But underneath, resentment accumulates — in code review comments, in passive agreement that doesn't convert to action, in engineers who stop raising disagreements because it hasn't been safe to disagree. Eventually the leak triggers an incident: a resignation, a public disagreement, a team split that requires EM intervention. Like a memory leak, the right fix is proactive detection and resolution — not waiting for the process to crash. Task conflict that surfaces early and resolves in 20 minutes is the proactive fix. Relationship conflict that surfaces 6 months later as a formal HR process is the crash.

**One insight:**
Task conflict is not the same as relationship conflict — and conflating them is the most common conflict management mistake. When engineers disagree about the right architecture, that is a productive disagreement about the work. The mistake is when one party (or an observer) experiences the task disagreement as a personal attack — at which point the task conflict becomes a relationship conflict and is much harder to resolve. The skill is in managing the transition: keeping task conflict as task conflict, and noticing when the dynamic is shifting toward personal friction.

---

### 🔩 First Principles Explanation

**THOMAS-KILMANN MODES:**

```
                HIGH COOPERATIVE
                        |
        Accommodating   |   Collaborating
                        |
LOW ─────────────────────────────────── HIGH
ASSERTIVE               |              ASSERTIVE
                        |
          Avoiding      |   Competing
                        |
                LOW COOPERATIVE

5 MODES AND WHEN TO USE THEM:

COMPETING (Win-Lose):
  Use when: emergency; quick decision needed; you're right
            and delay has cost; protecting someone who can't
            protect themselves
  Avoid when: relationship is long-term; buy-in matters

COLLABORATING (Win-Win):
  Use when: the problem is important enough to invest time;
            both parties' perspectives are needed; you want
            long-term alignment and commitment
  Avoid when: time pressure is high; stakes are low

COMPROMISING (Partial-Win/Partial-Win):
  Use when: both parties have equal power; solution needs
            to be temporary; collaborating has failed
  Avoid when: a better solution exists; one party has
              much stronger position

ACCOMMODATING (Yield):
  Use when: the issue matters more to the other party;
            you want to build goodwill; you've been wrong
  Avoid when: the issue is important; accommodating will
              be seen as weakness

AVOIDING (Lose-Lose):
  Use when: the conflict is trivial; you need time to
            gather information or cool down
  Avoid when: important decision needs to be made;
              avoiding will make things worse
```

**PRINCIPLED NEGOTIATION:**

```
POSITION vs INTEREST:

Position (what they say they want):
  Engineer A: "We must use Kafka for the event pipeline."
  Engineer B: "We should use SQS — we already use AWS."

If we negotiate positions: A pushes Kafka, B pushes SQS.
Compromise: pick one; the other person is unsatisfied.

Interest (why they want it):
  A's interests: high throughput; replay capability; 
                 Kafka expertise already on team
  B's interests: operational simplicity; consistent AWS stack;
                 no new infrastructure to manage

Now we can ask: "What solution addresses both sets of interests?"
  → Option 1: Kinesis (AWS-native; replay capability; high throughput)
  → Option 2: SQS + SNS for fan-out; implement replay in application layer
  → Option 3: Use Kafka but with managed MSK to reduce ops overhead

The positions were fixed; the interests generate multiple options.
```

---

### 🧪 Thought Experiment

**SETUP:**
Two tech leads — Alice (backend) and Bob (platform) — are in conflict over who owns the rate-limiting logic. Alice believes it belongs in the API gateway (platform's responsibility). Bob believes it belongs in the individual microservices (each service team's responsibility). They've had three meetings that produced no agreement. The conflict is now affecting sprint planning.

**Positional negotiation (what typically happens):**
Alice: "Rate limiting belongs at the gateway — that's architecture policy."
Bob: "Services own their own behaviour — gateway coupling is an antipattern."
[Escalates to architecture review board. Takes 3 weeks. Decision is a compromise nobody is satisfied with.]

**Principled negotiation:**
Step 1: Separate people from problem. "We both want reliable rate limiting. The question is: where does it live and who maintains it?"

Step 2: Surface interests.
Alice's interests: consistent policy enforcement; no per-service duplication; centralised observability
Bob's interests: service autonomy; no tight coupling to gateway; each team can configure their own limits

Step 3: Options that address both:
- Option A: Gateway enforces global rate limits; services enforce per-resource fine-grained limits
- Option B: Shared rate-limiting library that each service includes; gateway enforces only global DDoS protection
- Option C: Policy-as-code: rate limits defined centrally, enforced by gateway, but service teams can override for their service via config

Step 4: Objective criteria: "Which option best satisfies: operational simplicity, service autonomy, and consistent enforcement?"
→ Both evaluate against criteria → Option C is selected.

**Outcome:** 45-minute conversation; decision with genuine buy-in from both parties. No escalation.

---

### 🧠 Mental Model / Analogy

> Conflict resolution using principled negotiation is like debugging a system with two root causes that appear to conflict. If you observe "CPU maxes out" and "memory never reaches limit," fixing only the CPU (taking one side) doesn't solve the root cause — the system is poorly balanced. The right fix is to understand what each symptom is telling you about the underlying system state, and to find a configuration that addresses both. When two engineers are in conflict, their positions are the symptoms. Their interests are the root causes. The solution is a configuration that addresses both root causes — not one that privileges one symptom over the other.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Conflict resolution is the practice of addressing disagreements at work in a way that resolves the underlying problem rather than just ending the argument. The key insight is that most conflicts are about different underlying concerns — and finding solutions that address both sides' concerns is almost always possible.

**Level 2 — How to use it (engineer):**
When you're in a technical disagreement: name the underlying interest, not just the position. "I'm advocating for Kafka because of the replay capability — we've had production issues where we needed to re-process events. Is there a way to address that with your preferred approach?" This moves the conversation from "which camp wins" to "what does the solution need to do." If direct resolution isn't working: ask for a time-boxed evaluation — "let's both write up the trade-offs and review tomorrow."

**Level 3 — How it works (tech lead):**
When facilitating a conflict between team members: separate task conflict from relationship conflict immediately. If task conflict: "Let's define the criteria for the decision, then evaluate both approaches against those criteria." If relationship conflict: this needs a different intervention — 1:1 conversations with each party first; identify what specific behaviours are creating friction; use SBI feedback to address the specific behaviours. Never facilitate relationship conflict in a group setting — it escalates rather than resolves. Know when to escalate to your EM.

**Level 4 — Why it was designed this way (principal/staff):**
At the staff/principal level, the key insight is that conflict is an information signal, not just a management problem. Task conflict among strong engineers is often a signal that the decision space has not been well-explored — that there are real trade-offs worth understanding, or that architectural assumptions are unclear. The principal engineer's role in conflict resolution is partly facilitative (help the parties resolve it) and partly analytical (what does this conflict tell us about our architecture, our principles, or our decision-making process?). A conflict that recurs repeatedly around the same boundary (e.g., who owns the rate-limiting logic) is a signal about an architectural or organisational ambiguity that needs a structural fix, not just a one-time mediated resolution.

---

### ⚙️ How It Works (Mechanism)

```
CONFLICT RESOLUTION PROCESS:

1. IDENTIFY TYPE
   Task conflict (about the work) vs.
   Relationship conflict (about people)
    ↓
2. FOR TASK CONFLICT:
   a. Surface positions: "What does each party want?"
   b. Surface interests: "Why do they want it?"
   c. Agree on criteria: "What does the solution need to do?"
   d. Generate options against interests
   e. Evaluate options against criteria
   f. Decide + commit
    ↓
   FOR RELATIONSHIP CONFLICT:
   a. Separate parties; 1:1 conversations first
   b. Understand specific behaviours causing friction (SBI)
   c. Mediated conversation with ground rules
   d. Agree on specific behavioural changes
   e. Follow-up at 2–4 weeks
    ↓
3. DOCUMENT DECISION
   Why this decision; what was considered; what was not
   → Prevents re-opening resolved conflicts
    ↓
4. MONITOR
   Did the resolution hold?
   If the same conflict recurs: what structural change is needed?
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Disagreement surfaces (in meeting, code review, planning)
    ↓
Classify: task or relationship conflict?
    ↓
[CONFLICT RESOLUTION ← YOU ARE HERE]
Task conflict: principled negotiation
  → Interests → options → criteria → decision
Relationship conflict: separate → 1:1 → SBI → mediate
    ↓
Decision documented; both parties commit
    ↓
Monitor: does resolution hold?
    ↓
If recurring: structural analysis — what is the root cause
of this recurring conflict? (Architectural ambiguity? Role
clarity? Misaligned incentives?)
    ↓
Fix the structural cause; conflict doesn't recur
```

---

### 💻 Code Example

**Conflict analysis worksheet:**
```python
from dataclasses import dataclass, field

@dataclass
class ConflictParty:
    name: str
    position: str          # what they say they want
    interests: list[str]   # why they want it

@dataclass
class ConflictAnalysis:
    description: str
    party_a: ConflictParty
    party_b: ConflictParty
    criteria: list[str]    # what the solution must do
    options: list[str] = field(default_factory=list)

    def print_analysis(self) -> None:
        print(f"Conflict: {self.description}\n")
        for party in [self.party_a, self.party_b]:
            print(f"{party.name}:")
            print(f"  Position: {party.position}")
            print(f"  Interests: {'; '.join(party.interests)}")
        print(f"\nDecision criteria:")
        for c in self.criteria:
            print(f"  • {c}")
        if self.options:
            print(f"\nOptions to evaluate:")
            for o in self.options:
                print(f"  → {o}")

ConflictAnalysis(
    description="Rate-limiting ownership: gateway vs. services",
    party_a=ConflictParty(
        name="Alice (API)",
        position="Rate limiting belongs at the gateway",
        interests=[
            "Consistent policy enforcement",
            "Centralised observability",
            "No per-service duplication",
        ],
    ),
    party_b=ConflictParty(
        name="Bob (Platform)",
        position="Services should own their own rate limits",
        interests=[
            "Service autonomy",
            "No tight coupling to gateway",
            "Teams can configure their own limits",
        ],
    ),
    criteria=[
        "Consistent enforcement of global policy",
        "Service teams can customise per-endpoint limits",
        "Centrally observable; no per-service tooling duplication",
    ],
    options=[
        "Gateway: global limits; Services: fine-grained per-resource",
        "Shared rate-limit library; gateway enforces DDoS protection only",
        "Policy-as-code: central definition, gateway enforcement, "
        "service override via config",
    ],
).print_analysis()
```

---

### ⚖️ Comparison Table

| TK Mode | Assertive | Cooperative | Best Used When |
|---|---|---|---|
| **Competing** | High | Low | Emergency; you're clearly right; protecting a principle |
| **Collaborating** | High | High | Complex problem; relationship matters; both views needed |
| **Compromising** | Medium | Medium | Equal power; time pressure; temporary solution |
| **Accommodating** | Low | High | Their concern is more important; building goodwill |
| **Avoiding** | Low | Low | Trivial issue; need to gather information; cool-down |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Avoiding conflict is peaceful" | Avoided conflict accumulates into relationship damage or forces late-stage escalation with much higher cost. |
| "Compromising is always fair" | Compromise often means both parties are partially satisfied — which may produce a suboptimal solution. Collaborating can produce a solution where both interests are fully addressed. |
| "Technical disagreements are objective — just evaluate the options" | Technical decisions involve values (simplicity vs. performance, consistency vs. availability). Two engineers can look at the same data and reach different conclusions because they weight the values differently. |
| "Strong opinions, weakly held" | "Weakly held" is often not practised. Engineers with strong technical convictions frequently do not update their views when challenged. This is a competing mode problem, not a collaborating one. |
| "Conflict resolution = HR process" | Most engineering conflicts should be resolved by the engineers themselves, with facilitation from the tech lead. EM/HR intervention is for relationship conflicts that have failed direct resolution. |

---

### 🚨 Failure Modes & Diagnosis

**The Recurring Conflict — Same Fight, Different Sprint**

**Symptom:** The same conflict (e.g., "who owns the shared data model") surfaces in every planning cycle. Each time, the team reaches a temporary agreement. By next sprint, the conflict has re-emerged. Both parties have stopped engaging productively; the conflict is now also a relationship conflict.

**Root Cause:** The resolution was positional (picked a winner for this sprint) not principled (identified the interests and addressed them). The underlying structural ambiguity (ownership, authority, API boundary) was never addressed. The conflict will recur until the structure is fixed.

**Fix:**
```
1. NAME THE PATTERN:
   "This is the third sprint we've resolved this same conflict.
    Resolving it again the same way will produce the same result.
    I want to understand the root cause."

2. STRUCTURAL ANALYSIS:
   "This conflict recurs at the boundary between service A and
    service B. What is ambiguous about that boundary?"
   → Possible root causes:
     - The API contract is undefined or contested
     - The ownership of shared data is unclear
     - Two teams have incentives that conflict structurally

3. STRUCTURAL FIX:
   → Define and document the API contract (ADR)
   → Assign RACI/DRI for the shared component
   → If incentive conflict: escalate to EM/PM — this is
     a prioritisation or organisational design problem

4. PREVENTIVE:
   → "What is the rule that prevents this conflict from
      arising again?" — document it in an ADR or team norm
   → Review in 30 days: has the conflict recurred?
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Feedback (Giving and Receiving)` — conflict resolution requires giving specific feedback about behaviour
- `Psychological Safety` — conflict can only be surfaced early in a psychologically safe environment

**Builds On This (learn these next):**
- `Cross-Functional Collaboration` — cross-function conflicts are the most common and most complex
- `Stakeholder Communication` — communicating conflict decisions across stakeholder groups

**Alternatives / Comparisons:**
- `Feedback (Giving and Receiving)` — feedback is the proactive, early intervention; conflict resolution is what happens when feedback is absent or inadequate
- `Cross-Functional Collaboration` — cross-function collaboration failures often present as interpersonal conflict but have structural root causes

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ TASK vs     │ Task: about the work → resolve together    │
│ RELATIONSHIP│ Relationship: about people → 1:1 first     │
├─────────────┼───────────────────────────────────────────-┤
│ POSITIONS   │ "We must use Kafka"                        │
│ vs INTERESTS│ vs "We need replay + throughput"           │
│             │ → Interests generate multiple solutions    │
├─────────────┼───────────────────────────────────────────-┤
│ TK MODES    │ Collaborating = ideal for complex disputes │
│             │ Competing = emergencies only               │
│             │ Avoiding = never for important decisions   │
├─────────────┼───────────────────────────────────────────-┤
│ CRITERIA    │ Agree on what the solution must achieve    │
│             │ before evaluating options                  │
├─────────────┼───────────────────────────────────────────-┤
│ RECURRING   │ Structural problem → structural fix (ADR,  │
│ CONFLICT    │ RACI, API contract) — not re-mediation     │
├─────────────┼───────────────────────────────────────────-┤
│ NEXT EXPLORE│ Cross-Functional Collaboration →           │
│             │ Agile Principles                          │
└─────────────┴────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The Thomas-Kilmann model argues that all five conflict styles have appropriate uses. But many engineering cultures implicitly value only "Competing" and "Compromising" — engineers who accommodate or avoid are seen as passive; engineers who collaborate are seen as slow. Design a team norm document that explicitly legitimises all five TK modes for specific situations. For each mode: name a specific engineering situation where it is the optimal choice, and name one situation where it would be the wrong choice.

**Q2.** Two senior engineers on your team have been in conflict for 4 months. The conflict started as task conflict (disagreement on service architecture) but has become relationship conflict (they now avoid each other; other team members are aware of the tension; one has privately said they are considering leaving). You are their tech lead. As EM, what is the order of your interventions? Who do you speak to first? What specifically do you say in each conversation? At what point (and under what conditions) do you escalate to HR? What outcome would constitute successful resolution — and how would you measure it?
