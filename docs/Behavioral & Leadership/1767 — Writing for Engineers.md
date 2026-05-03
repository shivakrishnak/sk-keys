---
layout: default
title: "Writing for Engineers"
parent: "Behavioral & Leadership"
nav_order: 1767
permalink: /leadership/writing-for-engineers/
number: "1767"
category: Behavioral & Leadership
difficulty: ★★☆
depends_on: Documentation Culture
used_by: Documentation Culture, Presentations for Technical Audiences, Engineering Strategy
related: Documentation Culture, Presentations for Technical Audiences, Engineering Strategy
tags:
  - leadership
  - intermediate
  - writing
  - communication
  - technical-writing
---

# 1767 — Writing for Engineers

⚡ TL;DR — Technical writing is a high-leverage engineering skill that most engineers underinvest in — the ability to write a clear RFC, a persuasive design document, or a precise incident postmortem multiplies engineering impact far beyond what code alone can achieve; the key principles are: lead with the conclusion (BLUF), write for the busiest possible reader, make structure do the work, and ruthlessly edit for clarity over completeness.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An engineer with a great technical idea writes a 4,000-word RFC. Paragraph 3 has the key insight. Paragraph 25 has the recommendation. The document is comprehensive but impenetrable. Reviewers skim it and miss the key insight. The RFC goes through 3 rounds of review because people keep discovering things they misunderstood. The decision takes 6 weeks. The engineer is frustrated: "Nobody reads my RFCs carefully."

**THE BROKEN PATTERN:**
Most engineers are trained to think like scientists — build the full argument bottom-up before stating the conclusion. This is the correct scientific method. It is the wrong writing method for engineering contexts, where the reader is busy, the audience is heterogeneous (some technical, some not), and the goal is a decision, not comprehension of a complete argument. Engineering writing rewards top-down communication: conclusion first, then evidence.

**THE INVENTION MOMENT:**
The BLUF (Bottom Line Up Front) principle comes from military communications, where orders must be understood instantly under pressure. Jeff Bezos's ban on PowerPoint at Amazon (replacing with 6-page "narratives") is the canonical modern example: written communication forces clearer thinking than bullet slides.

---

### 📘 Textbook Definition

**BLUF (Bottom Line Up Front):** A communication structure where the most important point — the conclusion, recommendation, or decision — appears at the beginning, not the end. The reader knows what you want them to do or believe before they read the evidence.

**RFC (Request for Comments):** A technical document proposing a change, design, or decision, shared for review and feedback before implementation. The canonical format for engineering design communication.

**Narrative document:** A prose document (as opposed to bullet slides) that presents a complete argument with context, options, reasoning, and recommendation. Jeff Bezos's preference for 6-page narratives over PowerPoint at Amazon leadership meetings.

**Pyramid principle (Barbara Minto):** A writing structure where the main point appears at the top, supported by key arguments, which are in turn supported by data — the same structure as a pyramid. The reader can stop at any level and still understand the most important content.

**Signal-to-noise ratio:** In writing, signal is the information the reader needs; noise is everything else. High-signal writing: every sentence earns its place. Low-signal writing: verbose, repetitive, full of context the reader doesn't need.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Engineering writing means: lead with your conclusion, structure for the busiest possible reader, write only what the reader needs to make the decision, and edit until every sentence earns its place.

**One analogy:**

> A newspaper article and an academic paper present the same information in opposite order. An academic paper: introduction → literature review → methodology → results → conclusion. A newspaper: headline (conclusion) → most important facts → supporting context → background. If you stop reading the newspaper at any point, you still have the most important information. If you stop reading the academic paper at any point before the conclusion, you have nothing useful. Engineering documents should be written like newspapers, not academic papers. Your busy VP who reads the first paragraph should have the key information. Your detail-oriented peer who reads every footnote should have the complete argument.

**One insight:**
The best test for an engineering document is the "stop reading" test: if a reader stops after the first paragraph, do they have the most important information? After the first section? After the summary? If yes — the document is well-structured. If stopping at any point leaves the reader without the essential content — the structure is bottom-up (academic) rather than top-down (engineering).

---

### 🔩 First Principles Explanation

**ENGINEERING WRITING PATTERNS:**

```
PATTERN 1: BLUF STRUCTURE (for recommendations and proposals)

BAD (bottom-up):
  [2 pages of context]
  [1 page of problem statement]
  [2 pages of options analysis]
  [Final paragraph]: "Therefore, I recommend Option B."

  Result: reader who stopped at page 3 doesn't know what to do.

GOOD (BLUF):
  Recommendation: We should adopt Option B (use DynamoDB for
  session storage).

  Context: [1 paragraph of why this decision is needed]
  Options: [table of options with pros/cons]
  Recommendation rationale: [2 paragraphs on why Option B]
  Appendix: [full analysis for detail-oriented readers]

  Result: reader who reads one sentence knows the recommendation.
  Reader who reads the full document has the complete argument.

PATTERN 2: THE EXECUTIVE SUMMARY (for status updates, project docs)

  Executive Summary (3–5 sentences):
    What is happening? What is the key decision/status?
    What do you need from the reader?

  Body:
    Section 1: [detail for those who want to understand]
    Section 2: [additional detail]

  Appendix:
    [Technical details for those who want to go deeper]

  Rule: Every stakeholder finds their level. The VP reads
  the summary. The tech lead reads body + appendix.

PATTERN 3: RFC STRUCTURE

  Overview (1 paragraph):
    "This RFC proposes X to solve Y."

  Problem Statement:
    What is the problem? Why does it matter? What happens if
    we don't solve it?

  Proposal:
    What are we proposing? How does it work?

  Alternatives Considered:
    What else did we evaluate? Why is the proposal better?

  Trade-offs:
    What are we giving up? What risks does this create?

  Implementation Plan:
    How would this be implemented? What does the rollout look like?

  Open Questions:
    What remains unresolved? What feedback are we specifically seeking?
```

**WRITING QUALITY PRINCIPLES:**

```
PRINCIPLE 1: ONE IDEA PER SENTENCE
  BAD: "The service is experiencing high latency which is causing
       user-visible failures, which in turn is increasing support
       ticket volume, leading to engineer burnout on the support team."
  GOOD: "The service has high latency. This causes user-visible failures.
         Support ticket volume has increased 40% this week."

  Short sentences are readable. Long sentences bury information.

PRINCIPLE 2: ACTIVE VOICE
  BAD: "The deployment was triggered by the CI system."
  GOOD: "The CI system triggered the deployment."

  Active voice: subject does the action.
  Passive voice: subject receives the action (often vague).

PRINCIPLE 3: CONCRETE OVER ABSTRACT
  BAD: "There were significant performance improvements."
  GOOD: "P95 latency dropped from 2.1s to 340ms."

  Quantify whenever possible.
  Replace adjectives with data.

PRINCIPLE 4: REMOVE THE THROAT-CLEARING
  BAD: "In this document, we will be discussing the background of
       the problem and then presenting our analysis of the various
       options we considered before arriving at our final recommendation."
  GOOD: Delete this sentence. Start with the content.

  "In this document" — the reader knows this is a document.
  "We will be discussing" — just discuss it.
  First sentences should contain information, not announcements.

PRINCIPLE 5: THE READER'S QUESTION IS "SO WHAT?"
  Every paragraph: ask "so what?" If there's no clear "so what":
  either state it explicitly or cut the paragraph.

  BAD: "The current session store uses Redis on a single node
       with 16GB of RAM."
  GOOD: "The current session store uses Redis on a single node (16GB),
        which will reach capacity in Q2 at current growth — this is
        the trigger for this proposal."

  The first version presents a fact.
  The second version connects the fact to a "so what."
```

**EDITING PROCESS:**

```
PASS 1: STRUCTURE
  Does the document lead with the conclusion?
  Can a reader stop after each section and still have
  the most important content?
  Is the hierarchy of headings logical?

PASS 2: CLARITY
  Is every sentence clear without re-reading?
  Are all terms defined? (No jargon without explanation)
  Is the logic explicit? (No "therefore" that isn't obvious)

PASS 3: CONCISENESS
  Is every sentence necessary?
  Can any sentence be cut without losing information?
  Target: cut 20% from the first draft

PASS 4: SIGNAL-TO-NOISE
  Does every section earn its place?
  Is any context included that the reader doesn't need
  to make the decision?
  Move non-essential context to appendix.

RULE: The first draft is for you (to think through the problem).
      The final draft is for the reader (to act on the information).
      The editing passes convert one to the other.
```

---

### 🧪 Thought Experiment

**SETUP:**
Two engineers write a status update for the same project (2 weeks behind, auth dependency is the blocker).

**Engineer A:**
"Hi team, I wanted to give everyone an update on the Project Phoenix status. Over the past two weeks, we have been making good progress on the core functionality, with the team completing the data model design, the API layer implementation, and the first version of the UI components. However, we have encountered some challenges related to our dependency on the authentication service provided by Team Y, which has been experiencing their own delays due to capacity constraints and a competing priority that was added to their backlog last week by their product team. As a result, we are currently tracking approximately two weeks behind our original timeline. We are working to resolve this situation and will keep everyone updated as the situation develops."

**Engineer B:**
"Project Phoenix — Status Yellow 🟡

**Summary:** 2 weeks behind schedule due to auth dependency delay.

**Blocker:** Team Y's auth service is delayed (capacity constraints). Without auth: we can't complete integration testing.

**Impact:** Current estimate: delivery March 28 (was March 14).

**Request:** VP to escalate auth priority with Team Y by EOD tomorrow — this is on the critical path.

**What's proceeding:** Data model, API layer, UI components are on track."

**Analysis:** Engineer A's update is 150 words; conveys the essential information, but you have to read the whole thing to understand it. Engineer B's update is 90 words; the reader knows the status (yellow), the blocker, the impact, and the required action in the first 3 lines. A VP reading 40 status updates per week chooses Engineer B's format every time.

---

### 🧠 Mental Model / Analogy

> Writing for engineers is like writing a commit message vs. writing a novel. A novel rewards the reader who reaches the end — the climax, the revelation, the resolution — after investing time in the journey. A commit message must answer "what and why" in 72 characters because nobody reads commit novels. Engineering writing is closer to commit messages than novels: the reader is busy; the information is for making a decision or taking action; the journey is irrelevant. "Lead with the conclusion" is the commit message discipline applied to longer-form technical writing.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Good engineering writing means: put the most important thing first, use short sentences, replace vague words with numbers, and cut everything that doesn't help the reader make a decision or take action. Most engineers write like they're teaching — building context bottom-up before the conclusion. Better to write like a journalist — headline first, then supporting details.

**Level 2 — How to use it (engineer):**
Apply BLUF to every document you write: what do I want the reader to do or know? State that first. Apply the "stop reading" test: would a reader who stops after the first paragraph have the most important information? Write a first draft, then edit aggressively — cut 20% from the first draft in a second pass. Replace every adjective with a number where possible. Remove the first paragraph from every draft (it is almost always throat-clearing).

**Level 3 — How it works (tech lead):**
At the tech lead level, writing quality multiplies your influence. A well-written RFC that leads with the recommendation and presents clear trade-offs produces faster, better decisions. A poorly-written RFC delays decisions and creates misalignment. Invest in writing quality as seriously as code quality. Review your writing as a reader: "If I were the busiest person on this distribution list, would I get what I need from the first 3 sentences?" Run writing retrospectives: "What would make this doc clearer?"

**Level 4 — Why it was designed this way (principal/staff):**
At the principal/staff level, writing is thinking made visible. The clarity of a written proposal is often a direct reflection of the clarity of the thinking behind it. A vague, bottom-up proposal often signals vague, incompletely-developed thinking. The act of writing a clear BLUF forces precision: "What exactly am I recommending? Why?" When a principal engineer writes a persuasive technical narrative that shifts the organisation's direction, they are demonstrating the highest form of technical leadership — influence through the quality of their reasoning, made precise and accessible through the quality of their writing.

---

### ⚙️ How It Works (Mechanism)

```
ENGINEERING DOCUMENT WRITING PROCESS:

STEP 1: AUDIENCE + PURPOSE
  Who will read this? (Technical peer? VP? Cross-functional team?)
  What do I want them to do after reading?
  What is the minimum they need to know to do that?

STEP 2: OUTLINE (BLUF structure)
  Write the conclusion first
  List the 3–5 key points that support it
  Identify what context is needed (minimum)

STEP 3: FIRST DRAFT
  Write for understanding (your understanding)
  Don't edit; just write

STEP 4: EDIT (4 passes)
  Pass 1: Structure (BLUF? stop-reading test?)
  Pass 2: Clarity (clear sentences? defined terms?)
  Pass 3: Conciseness (cut 20%)
  Pass 4: Signal-to-noise (earn every section)

STEP 5: READER TEST
  Find the busiest person who will read this
  Ask: "What would you do after reading the first paragraph?"
  If wrong answer: revise structure
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Technical decision / problem / proposal identified
    ↓
[WRITING FOR ENGINEERS ← YOU ARE HERE]
Audience + purpose defined
    ↓
BLUF structure: conclusion → evidence → appendix
    ↓
First draft: write for understanding
    ↓
Edit: structure → clarity → conciseness → signal/noise
    ↓
Reader test: stop-reading test passes?
    ↓
Published: RFC / status update / postmortem / ADR
    ↓
Decision reached faster with less misalignment
```

---

### 💻 Code Example

**RFC template:**

```markdown
# RFC: [Title]

**Status:** Proposed
**Author:** [Name]
**Date:** [Date]
**Reviewers:** [Names or teams]

## Recommendation (BLUF)

[One sentence: what you are proposing and the key reason why.]

## Problem Statement

[2–4 sentences: what problem exists, what happens if unresolved,
why this matters now.]

## Proposal

[Description of the proposed solution. Include a diagram if helpful.
Keep focused; defer details to appendix.]

## Alternatives Considered

| Option          | Pros | Cons | Decision              |
| --------------- | ---- | ---- | --------------------- |
| Proposed option | ...  | ...  | ✅ Recommended        |
| Alternative A   | ...  | ...  | ❌ Rejected: [reason] |
| Alternative B   | ...  | ...  | ❌ Rejected: [reason] |

## Trade-offs

[What are we giving up? What risks does this create?
Be honest — this section builds trust.]

## Implementation Plan

[High-level steps and timeline. Not a full project plan.]

## Open Questions

[What remains unresolved? What specific feedback are you seeking?]

---

## Appendix (for detail-oriented readers)

[Technical details, data, analysis — not required to understand
the recommendation]
```

---

### ⚖️ Comparison Table

| Audience                | Depth             | Format                          | Key need                |
| ----------------------- | ----------------- | ------------------------------- | ----------------------- |
| **VP / Director**       | Summary only      | 3-sentence BLUF + bullet status | Decision / action       |
| **Engineering Manager** | Summary + options | BLUF + options table            | Trade-off understanding |
| **Tech Lead / Peer**    | Full RFC          | BLUF + full argument + appendix | Technical evaluation    |
| **Implementation team** | Specs + details   | Appendix + technical details    | Implementation clarity  |

---

### ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                                                                                                                                    |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Longer = more thorough = better"         | Longer = more noise. The best documents are as short as possible while containing everything the reader needs to make the decision.                                                        |
| "Context before conclusion is respectful" | Context before conclusion wastes busy readers' time. Lead with the conclusion; provide context for those who need it.                                                                      |
| "Technical accuracy is what matters most" | Technical accuracy is necessary. Clarity is also necessary. An accurate document that nobody understands produces the same outcome as an inaccurate one: a bad or delayed decision.        |
| "Good engineers don't need to write well" | Writing quality is a force multiplier. A principal engineer who writes clearly and persuasively influences 100 engineers. One who writes poorly influences 5 (the ones who already agree). |
| "First draft is close to final"           | First drafts are rarely good. The editing is where clarity emerges. Plan for 30–50% of total document time to be editing.                                                                  |

---

### 🚨 Failure Modes & Diagnosis

**The Buried Lede — Recommendation on Page 4**

**Symptom:** Engineer writes a 3,000-word RFC. The recommendation is in the penultimate paragraph. By the time reviewers reach it, they've already formed their own interpretation of what was being proposed based on the framing in the first 2,000 words. 60% of the review comments address questions that were answered in the document — the reviewers didn't read that far. The review cycle takes 3 weeks.

**Root Cause:** Bottom-up writing structure (context → analysis → conclusion) is the default academic/scientific writing pattern. It doesn't work for busy readers who have 20 documents to review.

**Fix:**

```
THE 2-MINUTE RFC REWRITE:

STEP 1: Find your recommendation paragraph
  (It's in the last quarter of the document)

STEP 2: Move it to position 1

STEP 3: Write a one-sentence version:
  "This RFC recommends [X] because [Y]."
  Put it at the very top.

STEP 4: Add an options table after the recommendation:
  | Option | Pros | Cons | Decision |
  This gives reviewers the comparison without reading prose.

STEP 5: Move all context and analysis to "Background" section
  after the recommendation.

STEP 6: Create an appendix for full technical details.

RESULT: Reviewer reads first 3 lines → knows the proposal.
        Reads options table → understands alternatives.
        Reads background → understands context.
        Reads appendix → understands technical depth.

Each reader self-selects their depth. Decision time: 1 week.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Documentation Culture` — the organisational context in which engineering writing is practised

**Builds On This (learn these next):**

- `Documentation Culture` — the team practice that engineering writing enables
- `Presentations for Technical Audiences` — the verbal/visual complement to written communication
- `Engineering Strategy` — engineering strategy is delivered through writing

**Alternatives / Comparisons:**

- `Presentations for Technical Audiences` — the oral/visual alternative to written communication
- `Documentation Culture` — the cultural context; writing skill is the individual capability

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ BLUF        │ Conclusion first; evidence after           │
│             │ "Recommend X because Y" in sentence 1     │
├─────────────┼──────────────────────────────────────────-─┤
│ STOP TEST   │ Reader stops after para 1 = still has key  │
│             │ info? If no: restructure.                  │
├─────────────┼──────────────────────────────────────────-─┤
│ EDIT PASSES │ 1: Structure 2: Clarity                   │
│             │ 3: Conciseness (cut 20%) 4: Signal/noise  │
├─────────────┼──────────────────────────────────────────-─┤
│ CONCRETE    │ Replace every adjective with a number     │
│             │ "significant" → "40%"; "slow" → "2.1s p99" │
├─────────────┼──────────────────────────────────────────-─┤
│ AUDIENCE    │ VP: 3 sentences. EM: options table.        │
│             │ Peer: full RFC. Team: appendix.           │
├─────────────┼──────────────────────────────────────────-─┤
│ NEXT EXPLORE│ Presentations for Technical Audiences →   │
│             │ Documentation Culture                    │
└─────────────┴────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Jeff Bezos banned PowerPoint at Amazon executive meetings, replacing them with 6-page written narratives read in silence at the start of each meeting. He argued that PowerPoint allows presenters to hide weak thinking behind polished slides, while written prose forces precision. Evaluate this claim: what specific cognitive advantages does written narrative have over slide decks for complex technical decisions? When might slides still be the better format? Design a decision framework for when to use prose vs. slides for engineering communication contexts.

**Q2.** A senior engineer on your team consistently writes technically accurate but impenetrable RFCs — dense, bottom-up, long-winded, with the recommendation buried on page 4. Reviews take 3 weeks; decisions are frequently delayed because reviewers misunderstand the proposal. You want to help this engineer improve their writing without being patronising about it. Design a feedback approach: what specific feedback do you give, in what format, and how do you help them develop writing skills without making the feedback feel like a personal criticism?
