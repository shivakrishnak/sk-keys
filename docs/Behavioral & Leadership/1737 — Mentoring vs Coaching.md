---
layout: default
title: "Mentoring vs Coaching"
parent: "Behavioral & Leadership"
nav_order: 1737
permalink: /leadership/mentoring-vs-coaching/
number: "1737"
category: Behavioral & Leadership
difficulty: ★★☆
depends_on: Situational Leadership, Feedback (Giving and Receiving)
used_by: Technical Leadership, Engineering Manager vs Tech Lead, Situational Leadership
related: Situational Leadership, Feedback (Giving and Receiving), Psychological Safety
tags:
  - leadership
  - development
  - intermediate
  - coaching
  - mentoring
---

# 1737 — Mentoring vs Coaching

⚡ TL;DR — Mentoring transfers the mentor's experience and expertise to the mentee ("I've been there; here's what I learned"), while coaching unlocks the coachee's own capabilities and insights ("You already know this; let me help you discover it") — and knowing which mode to use, and when, is a core skill for any technical leader.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A manager has a talented engineer who is stuck on a career decision. The manager immediately launches into advice: "I did X when I was at that stage; you should do Y; here's how I approached it." The engineer nods but leaves feeling unheard — the advice was technically correct but didn't account for the engineer's specific context, values, or what they actually needed to work through. The manager gave a solution to a problem the engineer needed to solve for themselves.

**THE BREAKING POINT:**
Defaulting to advice-giving (mentoring mode) when someone needs discovery (coaching mode) is ineffective because: (1) generic advice from your experience may not apply to their context; (2) they become dependent on your answers rather than building their own judgment; (3) they feel heard less — advice says "I have your answer" while coaching says "I trust you to find your answer."

**THE INVENTION MOMENT:**
The distinction between mentoring and coaching emerged from the coaching psychology field (building on Whitmore's GROW model, 1992) which formalised that skilled development conversations are predominantly facilitative — asking questions that help the other person discover their own insights — rather than advice-giving. Most technical leaders default to mentoring (advice); the distinction teaches when to use which mode.

---

### 📘 Textbook Definition

**Mentoring** is a development relationship in which the mentor shares their own experience, expertise, and knowledge to guide the mentee. It is predominantly directive: "Based on my experience, I recommend..." It is most effective when the mentee lacks specific experience or knowledge that the mentor has, and where the mentor's path is a relevant model for the mentee's situation. Mentoring is experience-transfer.

**Coaching** is a development relationship in which the coach uses questions and reflection to help the coachee discover their own insights, solutions, and capabilities. It is predominantly non-directive: "What do you think?" It is most effective when the coachee already has the knowledge or capability but needs help clarifying thinking, overcoming limiting beliefs, or committing to a path. Coaching is capability-unlocking.

**Key distinction:** Mentoring says "here is what I did / what you should do." Coaching says "what do you think? what have you tried? what's stopping you?"

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Mentoring gives answers from your experience; coaching unlocks the other person's own answers — use mentoring when they lack knowledge, coaching when they lack confidence or clarity.

**One analogy:**

> A swimming instructor who demonstrates the butterfly stroke and corrects your arm position is mentoring — they have knowledge you don't and they're transferring it. A swimming coach watching you in the Olympics is coaching — you already know how to swim; they ask "what felt different in that last 50 meters?" to help you access your own awareness. Most technical leaders are swim instructors; the best ones learn when to put on the coaching hat.

**One insight:**
The instinct to give advice is strong in technical leaders — we became leaders by having good answers. The coaching mindset requires suppressing that instinct and trusting that the other person can find their own answer, which is often a better answer for their specific situation than yours would be.

---

### 🔩 First Principles Explanation

**WHEN TO MENTOR:**

```
USE MENTORING WHEN:
  The person genuinely lacks knowledge or experience
    → "I've never done a system design interview before"
    → Give specific advice, examples, frameworks

  They need concrete guidance, not reflection
    → "What should I include in this ADR?"
    → Share your template, walk through it

  They are blocked by missing information
    → "I don't know what our deployment pipeline supports"
    → Tell them (don't ask "what do you think it supports?")

  They explicitly ask for advice
    → "What would you do in my situation?"
    → If asked, give your view (with appropriate caveats)
```

**WHEN TO COACH:**

```
USE COACHING WHEN:
  They have the knowledge but lack confidence
    → "I know what I should do but I'm afraid to..."
    → Coaching unlocks what's blocking them, not more info

  They need to make a decision only they can make
    → "Should I take this job offer?"
    → Your experience doesn't answer this; theirs does

  They are ruminating or stuck in their own head
    → "I keep going back and forth on this"
    → Coaching helps them clarify their own thinking

  You want them to develop independent judgment
    → D3 level (capable, needs confidence boost)
    → Ask "what do you think?" before offering your view
```

**THE GROW COACHING MODEL:**

```
GOAL
  "What do you want to achieve from this conversation?"
  "What outcome would be most useful today?"

REALITY
  "Where are you with this right now?"
  "What have you tried so far?"
  "What's happening that you're not happy with?"

OPTIONS
  "What options have you considered?"
  "What else could you do?"
  "What would you do if there were no constraints?"

WILL (commitment)
  "What will you do and by when?"
  "What support do you need?"
  "What might get in the way?"
```

**THE FAILURE MODE:**
Advice-giving when coaching is needed: the person leaves with your answer, not their own. They call you again next time instead of solving it themselves. You become the bottleneck.

Coaching when mentoring is needed: the person leaves frustrated and without the information they needed. "I just wanted to know what tech stack to use — why is my manager asking me what I think?"

---

### 🧪 Thought Experiment

**SETUP:**
Engineer: "I've been offered a Tech Lead role on the platform team. I'm not sure whether to take it. I've always wanted to lead, but I like the deep technical work I do now. What would you do?"

**THE MENTORING RESPONSE (advice-giving):**
"I faced the same decision at your stage. I took the TL role and it was the right call — the leadership experience was invaluable. I'd recommend taking it. You can always go back to IC work, but leadership experience opens more doors. Go for it."

**THE COACHING RESPONSE (facilitative):**
"That sounds like a meaningful decision. Before I share any view, tell me — what is it about the platform team TL role that appeals to you? ... And what is it about the deep IC work that you're worried about giving up? ... When you imagine yourself 2 years into the TL role, what do you see? ... And in the IC path? ... What is the real thing holding you back right now — is it uncertainty about the role, or uncertainty about yourself? ... So given all of that, what do you think you want to do?"

**THE DIFFERENCE:**
The mentoring answer might be right — but it's based on your experience, not theirs. The coaching answer helps them access what they already know about themselves. They own the decision they make from coaching; they're implementing your recommendation from mentoring.

**THE CAVEAT:**
Coaching doesn't mean never sharing your view. After coaching, if they ask "what would you do?" — you can answer. And if they are genuinely blocked and need information you have, give it. The skill is knowing which mode to lead with.

---

### 🧠 Mental Model / Analogy

> Mentoring is a map. Coaching is GPS. A map is invaluable when you don't know the terrain — it gives you someone else's knowledge of the routes. GPS is more useful when you already know roughly where you're going but need help navigating your specific real-time situation. Most early career engineers need maps (mentoring). Most senior engineers need GPS (coaching). Using a map with someone who knows the terrain and just needs to commit to a route is unhelpful; using GPS with someone who has no idea what city they're in leaves them stranded.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Mentoring = sharing your experience and advice. Coaching = asking questions that help the other person find their own answers. Both are valuable; the skill is choosing which one the situation calls for.

**Level 2 — How to use it (new tech lead or manager):**
In your next 1:1 where a team member brings a problem: before defaulting to advice, ask one question first: "What do you think you should do?" If they have an answer, probe further: "What's stopping you from doing that?" This takes 2 minutes and often produces a better outcome than your advice because it's based on their actual context. Save your advice for: when they genuinely don't know, when they explicitly ask for your experience, when you have specific information they lack.

**Level 3 — How it works (experienced manager/TL):**
The coaching vs. mentoring decision maps directly to Situational Leadership: D1 people (new to the task) need mentoring — they genuinely lack knowledge. D3 people (capable but uncertain) need coaching — they have the knowledge but lack confidence in their judgment. D2 people typically need both: coaching for motivation, mentoring for the knowledge gaps. D4 people need neither — they need delegation and trust, not development conversations. An experienced leader reads the development level and leads the conversation accordingly: GROW model for D3, direct advice for D1, mix for D2.

**Level 4 — Why it was designed this way (senior/principal):**
The coaching movement in professional development emerged from empirical evidence that directive advice-giving, while efficient in the short term, produces dependency and shallow learning. The person who receives advice learns one solution to one problem; the person who is coached learns how to think about a class of problems. For engineers growing toward senior and staff levels, coaching-style development is essential because the problems they face become increasingly novel — their manager's specific experience becomes less relevant than their ability to develop sound judgment independently. The best technical leaders develop both capabilities and know when to deploy each: mentor when transferring domain knowledge; coach when developing reasoning and decision-making capability. This distinction also prevents a common management failure: managers who over-mentor produce dependent teams; managers who over-coach produce frustrated teams when people genuinely need information and guidance.

---

### ⚙️ How It Works (Mechanism)

```
CONVERSATION DIAGNOSTIC:

Engineer brings a problem/question
    ↓
Ask: Does this person lack knowledge/information?
    ↓
YES → Mentoring mode
  Share your experience
  Give concrete advice
  Provide frameworks, examples
  Check: "Does that help? / Does that apply to your situation?"

NO → Coaching mode
  GROW: Goal → Reality → Options → Will
  Lead with questions: "What do you think?"
  Reflect back: "It sounds like..."
  Invite: "What's stopping you?"
  Close: "What will you do by when?"

HYBRID (most common):
  Lead with coaching (test if they have the answer)
  If genuinely blocked on knowledge → shift to mentoring
  Return to coaching to help them own the decision
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Development conversation requested
    ↓
Diagnose: knowledge gap vs. decision/confidence gap
    ↓
[SELECT MODE ← YOU ARE HERE]
  Knowledge gap → Mentoring: share experience, advise
  Decision gap → Coaching: GROW, ask, reflect
    ↓
Conversation
    ↓
Close:
  Mentoring: "Does that answer your question? What will you do?"
  Coaching: "What will you do? By when?"
    ↓
Follow up:
  Did they act on the outcome?
  What support do they need next?
    ↓
Adjust mode based on their development progress
```

---

### 💻 Code Example

**Coaching conversation framework:**

```python
GROW_PROMPTS = {
    "GOAL": [
        "What do you want to get out of this conversation?",
        "What outcome would be most useful today?",
        "What does success look like at the end of this?"
    ],
    "REALITY": [
        "Where are you with this right now?",
        "What have you already tried?",
        "What's the impact of this situation on you?"
    ],
    "OPTIONS": [
        "What options have you considered?",
        "What else could you do? What if there were no constraints?",
        "What do you think would work best?"
    ],
    "WILL": [
        "What will you do and by when?",
        "What support do you need from me?",
        "What might get in the way of doing that?"
    ]
}

# Self-check for 1:1s
def choose_mode(has_knowledge_gap: bool,
                has_confidence_gap: bool) -> str:
    if has_knowledge_gap and not has_confidence_gap:
        return "MENTOR: Share your experience and advise directly"
    if has_confidence_gap and not has_knowledge_gap:
        return "COACH: GROW model; lead with questions"
    if has_knowledge_gap and has_confidence_gap:
        return "HYBRID: Start coaching; fill knowledge gaps where needed"
    return "DELEGATE: They're capable and confident; trust them"
```

---

### ⚖️ Comparison Table

| Dimension         | Mentoring                      | Coaching                            |
| ----------------- | ------------------------------ | ----------------------------------- |
| **Direction**     | Directive (I advise you)       | Non-directive (I help you discover) |
| **Primary tool**  | Experience sharing, advice     | Questions, reflection               |
| **Leader speaks** | ~60–70% of time                | ~30–40% of time                     |
| **Best for**      | Knowledge gaps, early career   | Decision gaps, capable but stuck    |
| **Risk**          | Creates dependency if overused | Frustrating if person lacks info    |
| **Outcome**       | Person has your answer         | Person has their own answer         |
| **Long-term**     | Efficient for known situations | Builds independent judgment         |

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                                                           |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Coaching means never giving advice"        | Coaching means leading with questions; you can and should share your view when directly helpful or when asked                                                                     |
| "Mentoring is better for junior engineers"  | Junior engineers need mentoring AND coaching — mentoring for knowledge, coaching for building judgment and ownership                                                              |
| "Coaching is only for career conversations" | Coaching applies in technical conversations: "What do you think the root cause is?" before offering your diagnosis                                                                |
| "You must pick one mode and stick with it"  | The best development conversations move between modes fluidly: start with coaching, shift to mentoring when genuine knowledge gaps appear, return to coaching to own the solution |
| "Coaching means asking endless questions"   | Effective coaching is purposeful: 4–6 well-chosen GROW questions are more effective than 20 unfocused ones                                                                        |

---

### 🚨 Failure Modes & Diagnosis

**The Advice Machine (Over-Mentoring)**

**Symptom:** Team members bring every decision to you, however small. They rarely act independently. When they make decisions without consulting you, their confidence is low. They describe their growth as "waiting for more experience." The team can't function when you're on PTO.

**Root Cause:** You have answered every question with advice. They have learned that your answers are available and reliable, so they stop developing their own. You have inadvertently trained dependency.

**Diagnostic:**

```
In your last 5 development conversations, count:
  How many times did you say "you should..."?
  How many times did you say "what do you think?"?

Target ratio: at least 1 coaching question per advice given.
If your advice:question ratio is > 3:1, you are over-mentoring.
```

**Fix:** For 4 weeks, respond to every question with a question first: "What have you already thought about?" "What options have you considered?" Share your view after they share theirs — and only when your view adds genuine value beyond what they already identified.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Situational Leadership` — mentoring vs coaching maps directly to the D-level diagnosis
- `Feedback (Giving and Receiving)` — both mentoring and coaching involve structured feedback

**Builds On This (learn these next):**

- `Technical Leadership` — technical leaders must develop both mentoring and coaching capabilities
- `Engineering Manager vs Tech Lead` — both roles require effective development conversations
- `Psychological Safety` — coaching requires psychological safety; the coachee must feel safe to explore without judgment

**Alternatives / Comparisons:**

- `Situational Leadership` — the framework that tells you when to mentor (S1/S2) vs. coach (S3) vs. delegate (S4)
- `Feedback (Giving and Receiving)` — specific technique for both mentoring and coaching conversations
- `Psychological Safety` — the cultural prerequisite for effective coaching

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Mentoring: share your experience (tell)   │
│              │ Coaching: unlock their capability (ask)   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Mentoring: knowledge gap, early career,   │
│              │ they need information                     │
│              │ Coaching: confidence gap, capable but     │
│              │ stuck, decision only they can make        │
├──────────────┼───────────────────────────────────────────┤
│ GROW MODEL   │ Goal → Reality → Options → Will           │
│              │ 4–6 purposeful questions per conversation │
├──────────────┼───────────────────────────────────────────┤
│ KEY SKILL    │ Ask "what do you think?" before advising. │
│              │ If they have an answer, coach further.    │
│              │ If they don't, mentor.                    │
├──────────────┼───────────────────────────────────────────┤
│ CAUTION      │ Over-mentoring creates dependency;        │
│              │ over-coaching frustrates people who need  │
│              │ information, not more questions           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Mentoring gives them a fish. Coaching    │
│              │ teaches them to fish. Know which they     │
│              │ actually need."                           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Psychological Safety →                    │
│              │ Feedback (Giving and Receiving)           │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A senior engineer on your team is technically excellent (D4) but has applied for a Staff Engineer role and been rejected twice. After each rejection, you gave them feedback on the specific gaps (scope of influence, cross-team leadership). They acknowledge the feedback but nothing changes. Using the mentoring vs. coaching distinction: diagnose what mode you have been using and why it hasn't worked. What mode should you switch to? Design a coaching conversation using the GROW model for this situation — write out the specific questions you would ask at each stage.

**Q2.** The coaching approach asks leaders to suppress their instinct to give advice and instead ask questions. For a technical problem (e.g., a junior engineer asking "should I use Redis or Memcached?"), is it always appropriate to use the coaching mode before answering? At what point does asking "what do you think?" become a waste of time or even condescending, and when does it develop genuine engineering judgment? Design a decision rule for technical 1:1 conversations that specifies when to coach and when to simply answer.
