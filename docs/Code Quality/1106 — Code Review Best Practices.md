---
layout: default
title: "Code Review Best Practices"
parent: "Code Quality"
nav_order: 1106
permalink: /code-quality/code-review-best-practices/
number: "1106"
category: Code Quality
difficulty: ★★☆
depends_on: Code Review, Code Standards, Version Control
used_by: Code Quality, Team Culture, Technical Debt
related: Code Review, Pair Programming, Style Guide
tags:
  - bestpractice
  - intermediate
  - cicd
  - devops
---

# 1106 — Code Review Best Practices

⚡ TL;DR — Code review best practices are the principles and techniques that make reviews effective, fast, and collaborative rather than slow, adversarial, or superficial.

| #1106 | Category: Code Quality | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Code Review, Code Standards, Version Control | |
| **Used by:** | Code Quality, Team Culture, Technical Debt | |
| **Related:** | Code Review, Pair Programming, Style Guide | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Code review exists on the team, but it's not working. PRs sit unreviewd for 3 days. Reviewers write vague comments like "this doesn't look right" without explaining why or suggesting a fix. Authors feel attacked; reviewers feel ignored. Senior developers approve everything in 30 seconds to avoid conflict. Some reviewers are nitpicky about whitespace while ignoring logic bugs. The review process creates friction without producing quality.

**THE BREAKING POINT:**
Code review without practices is code review theater. It consumes time, creates friction, and produces meetings about PR comments — but doesn't improve code quality or spread knowledge. Worse, bad review practices create cultural damage: authors stop trying because feedback is arbitrary; reviewers stop engaging because nothing changes.

**THE INVENTION MOMENT:**
This is exactly why **code review best practices** exist: to turn the mechanical review process into an effective collaboration — specific techniques that make reviews faster, deeper, fairer, and more educational.

---

### 📘 Textbook Definition

**Code review best practices** are evidence-based principles and techniques for conducting effective peer code evaluation. They cover four dimensions: **author practices** (preparing PRs for reviewability — small size, clear description, self-review before submission, context-setting), **reviewer practices** (commenting with empathy and precision, distinguishing blockers from suggestions, asking questions rather than demanding changes), **process practices** (SLAs for first review, PR size limits, review assignment rotation, automated checks before human review), and **culture practices** (separating code criticism from person criticism, framing reviews as collaboration not gatekeeping, celebrating thorough reviews). Core principles include: Google's code review guidelines (what warrants approval, how to comment, escalation paths), the "two-hat" model (wearing the "architecture hat" then the "detail hat" separately), and the 24-hour SLA standard for first review response.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The techniques that make code review actually improve code instead of just blocking it.

**One analogy:**
> Code review best practices are like the rules of constructive feedback in a writing workshop. In a good workshop, critiques begin with what works, identify specific issues with evidence, suggest alternatives rather than just complaining, and separate the work from the writer. Without these norms, workshops become personal attacks or empty praise. With them, writers improve their work and learn craft. The same principles applied to code review transform adversarial feedback into collaborative improvement.

**One insight:**
The most common code review failure is not that reviewers miss bugs — it's that review culture degrades to either rubber-stamping or micromanagement. Practices don't fix tools; they fix habits. The tool (PR workflow) is rarely the problem.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Review effectiveness is determined by (a) what the reviewer focuses on and (b) whether the author can act on feedback — not by the number of comments.
2. PR size is inversely proportional to review depth: reviewers who review > 400 lines provide fewer substantive corrections.
3. Review friction compounds: each slow review creates context-switch overhead; each vague comment creates a back-and-forth cycle.

**DERIVED DESIGN:**
To maximise review effectiveness: keep PRs small (reviewer capacity constraint), automate mechanical checks (style, linting) before human review (eliminate trivial comments), provide context in PR description (reduce time spent understanding), distinguish blocking comments from optional suggestions (reduce decision overhead), and respond quickly to reviews (minimise context-switch cost).

**THE TRADE-OFFS:**
Gain: Higher-quality reviews in less time; reduced review latency; positive team culture around quality.
Cost: Discipline required from authors (keeping PRs small is harder than one large PR); process overhead for review SLAs; cultural investment to shift from gatekeeping to collaboration.

---

### 🧪 Thought Experiment

**SETUP:**
The same developer submits the same PR (300 lines, one feature) to two different teams.

**TEAM A (no review practices):**
- PR description: "Added payment feature"
- No reviewer assigned automatically
- After 48 hours, a senior dev reviews it in 10 minutes: "Looks fine, LGTM"
- PR merges with 2 security issues that a focused review would have caught.

**TEAM B (code review best practices):**
- PR description: "Add payment retry mechanism with idempotency key — see ticket PAY-142. Handles: 503 retry (3x with backoff), 400 no-retry, 202 async poll. Edge case: idempotency key prevents double-charge on retry."
- Reviewer assigned via CODEOWNERS within 2 hours
- CI already ran lint/SpotBugs (no style comments needed)
- Reviewer reads description first, then diff
- Reviewer comments: 2 blocking (potential NPE, idempotency key not logged for debugging), 1 suggestion (non-blocking: "consider extracting retry logic to RetryTemplate")
- Author fixes 2 blocking issues within an hour
- Reviewer approves: total review cycle: 4 hours, 2 real bugs caught

**THE INSIGHT:**
The PR content was identical. The practices determined whether the review was useful or theatrical.

---

### 🧠 Mental Model / Analogy

> Code review best practices are like surgical protocols in an operating room. Surgery has a set of protocols: hand-washing procedure, instrument count before and after, "time-out" before incision for team alignment. These protocols exist not because surgeons are careless, but because high-stakes procedures benefit from explicit checks even for experienced practitioners. Deviation from protocol (skipping the instrument count) leads to surgical errors that are preventable. Code review best practices are the operating room protocol for code changes: explicit steps that reduce preventable errors even for experienced teams.

- "Hand-washing" → running automated checks before human review
- "Instrument count" → checking PR description is complete before reviewing
- "Time-out for team alignment" → reviewer reading the PR description first, not jumping to the diff
- "Surgical error" → ship bug that review should have caught

Where this analogy breaks down: surgical protocols are uniform globally; code review practices vary by team, technology, and context. Teams adapt practices to their situation.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Code review best practices are the "right way to do code reviews" — specific habits that make reviews faster and more useful. Examples: write a clear description in your PR, keep PRs small (< 400 lines), review within 24 hours of being assigned, comment with specific suggestions not just criticism. These habits turn reviews from bureaucratic obstacles into real quality improvements.

**Level 2 — How to use it (junior developer):**
**As author:** Write a PR description that answers: what does this do? why did you do it this way? what edge cases did you consider? Self-review your diff before assigning a reviewer — remove debug logs, check for typos in comments. Keep PRs under 400 lines when possible. Respond to reviewer comments within a day.

**As reviewer:** Start with the PR description — understand intent before reading code. Check correctness first (does it work?), then readability, then style (last — if not automated). Frame comments as questions or suggestions, not demands: "What happens if X is null?" not "This is wrong." Mark comments as blocking ("must change before merge") vs. optional ("consider this for later"). Don't be the last person to stop reviewing — approve when the PR is good enough, even if imperfect.

**Level 3 — How it works (mid-level engineer):**
Effective teams operationalise practices into process: **PR template** (mandatory fields: description, edge cases, test coverage notes), **PR size limits** (automated warning if > 400 LOC changed), **review SLA** (first review within 4 business hours, defined in team working agreement), **CODEOWNERS** (automatic reviewer assignment for each code area), **mandatory CI passing** before review (no human reviews code that fails linting), **comment labels** (teams use explicit labels: `blocking:`, `nit:`, `question:`, `suggestion:` to reduce ambiguity). Google's code review guidelines formalise when to approve: "approve when the code definitely improves the overall code health of the system, even if it's not perfect."

**Level 4 — Why it was designed this way (senior/staff):**
The fundamental tension in code review is between **author flow** (authors want fast merges; context-switching from code to review-response is costly) and **reviewer depth** (thorough reviews take time). Best practices resolve this tension by: (1) reducing the raw volume of reviewer work via automation (linting, SpotBugs), (2) increasing per-minute review effectiveness by scoping PRs appropriately, and (3) reducing back-and-forth cycles by making author context explicit in the description. The empirical research (see SmartBear's "Best Kept Secrets of Peer Code Review") shows: reviews of > 400 LOC see defect detection rates drop significantly (reviewer cognitive overload); reviews faster than 60 minutes per 400 LOC tend to miss more defects (rushing); the optimal inspection rate is ~200 LOC/hour for deep review. These numbers drive the quantitative practices (size limits, time boxes) that the best teams follow.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────┐
│  REVIEW BEST PRACTICE CHECKLIST                 │
├─────────────────────────────────────────────────┤
│  AUTHOR BEFORE SUBMITTING:                      │
│  □ PR description: what, why, edge cases        │
│  □ PR size: < 400 lines (or justified)          │
│  □ Self-reviewed the diff                       │
│  □ CI green: lint, tests, static analysis       │
│  □ Reviewer assigned (CODEOWNERS or manual)     │
│                                                 │
│  REVIEWER WHEN REVIEWING:                       │
│  □ Read description first (5 min)               │
│  □ Correctness: does it do what it claims?      │
│  □ Edge cases: what happens at boundaries?      │
│  □ Security: injection, data exposure?          │
│  □ Readability: can I understand in 10 min?     │
│  □ Tests: are they testing what matters?        │
│  □ Label comments: blocking / nit / suggestion  │
│                                                 │
│  AUTHOR AFTER REVIEW:                           │
│  □ Respond within 24h (acknowledge all)         │
│  □ Fix blocking comments                        │
│  □ Document non-fixes with reason               │
│  □ Request re-review (don't just RE-assign)     │
└─────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (best practices applied):**
```
Author: writes feature, self-reviews, writes description
  → CI passes (lint, tests, SpotBugs all green)
  → PR opened: < 300 lines, clear description
  → CODEOWNERS auto-assigns reviewer
  → Reviewer: within 4 hours, 30-40 min review
  → 3 blocking comments, 2 nits
  [← YOU ARE HERE: reviewer comments, author acts]
  → Author fixes blocking in 2 hours
  → Re-review: 10 minutes, LGTM, approve
  → Merge: total cycle 6–8 hours
  → 3 bugs caught before production
```

**FAILURE PATH (practices absent):**
```
Author: submits 1,200-line PR, description: "fixes"
  → CI not required before review
  → No reviewer assigned: author pings 3 people
  → 3 days pass: no review
  → Reviewer 3 reviews in 10 minutes: "LGTM"
  → Merge: bugs ship
  → Postmortem: "review didn't catch it"
→ Root cause: no practices, not wrong people
```

**WHAT CHANGES AT SCALE:**
At 100+ engineers, review practices must be institutionalised: CODEOWNERS files for every directory, automated PR size checks via CI, review SLAs tracked per team in engineering metrics dashboards, mandatory review training for new joiners.

---

### 💻 Code Example

**Example 1 — Effective PR template (.github/pull_request_template.md):**
```markdown
## What
<!-- What does this PR do? 1-2 sentences. -->


## Why
<!-- Why is this change needed? Link to issue/ticket. -->


## Edge cases considered
<!-- What inputs or states could break this? -->
<!-- How did you handle them? -->


## Test coverage
<!-- What new tests were added? What existing tests -->
<!-- cover this change? -->


## Reviewer notes
<!-- Anything specific you want the reviewer to focus on? -->
<!-- Anything you're unsure about? -->

---
**Checklist:**
- [ ] Self-reviewed my diff
- [ ] CI passing (lint, tests, static analysis)
- [ ] PR size < 400 lines (or justified below)
- [ ] No debug logs, TODOs, commented-out code
```

**Example 2 — Comment label conventions:**
```
// blocking: must fix before merge
blocking: The idempotency key is not included in the 
retry request. Without it, concurrent retries can 
cause double-charges. See PaymentService.java:122.

// nit: optional style suggestion
nit: Could rename this variable from 'x' to 'retryCount'
for clarity. Not blocking.

// question: genuine question, may be fine
question: What happens when the gateway returns HTTP 202?
Is that an error or success? I don't see it handled.

// suggestion: consider this improvement, not blocking
suggestion: The retry logic in lines 45-67 could be 
extracted to a RetryTemplate. Not needed now, but a 
follow-up ticket? @author happy to discuss.
```

---

### ⚖️ Comparison Table

| Practice | Impact | Cost | Blocking? | Best For |
|---|---|---|---|---|
| PR size limit < 400 lines | High | Low | No (warning) | All teams |
| Clear PR description template | High | Low | Yes (required) | All teams |
| CI must pass before review | High | Low | Yes (automated) | All teams |
| **Review SLA (4h first review)** | High | Medium | No (cultural) | Active teams |
| Comment labelling (blocking/nit) | Medium | Low | No (cultural) | Ambiguity-prone teams |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Longer review = better review | Thorough review of a 200-line PR (30–45 min) catches more defects than fast review of a 2,000-line PR (15 min). Time per LOC matters, not total time. |
| The reviewer is responsible for the code after approval | The author is always responsible for the code they write. The reviewer's role is to provide a second perspective, not to become the owner. |
| Comments should always be resolved before merge | Non-blocking/nit comments can be tracked as follow-up items. Not every comment needs to block merge. Teams create tech debt tickets for suggestions that don't block the PR. |
| PR approval means reviewer checked everything | Approval means the reviewer believes the code is good enough to merge, not that every line was verified. Reviewers have limited time and may not check areas outside their scope. |

---

### 🚨 Failure Modes & Diagnosis

**1. Review Paralysis — PRs Never Merge Cleanly**

**Symptom:** PRs have 50+ comments. Authors and reviewers go 5+ rounds of revisions. PRs take 2 weeks to merge.

**Root Cause:** No distinction between blocking and non-blocking comments. Every "nit" creates the same resolution pressure as a critical bug. No agreed definition of "good enough to merge."

**Diagnostic:**
```bash
# Count average comment-per-review and rounds
gh pr list --state merged --json number,comments \
  --limit 50 | \
  jq '[.[] | .comments] | add / length'
# High comment count + slow merge = paralysis risk
```

**Fix:** Adopt blocking/nit/suggestion labelling. Define "approved" explicitly: "I believe this code improves the codebase, even if imperfect. Non-blocking items tracked separately."

**Prevention:** Train reviewers on distinguishing blocking from non-blocking. Set team norm: approve with nit-comments rather than requesting changes for suggestions.

---

**2. Review Culture Deteriorates — Personal Not Code**

**Symptom:** Authors dread submitting PRs. Comments say "this is terrible" not "here's a specific issue." Defensive responses. Team morale declining. Junior developers stop asking for review.

**Root Cause:** Review comments conflate code quality with personal quality. "This is wrong" activates personal defensiveness. "This method might NPE when input is null — here's how to fix it" activates problem-solving.

**Diagnostic:**
```bash
# Review recent PR comments manually
# Red flags: "you should", "this is bad", 
# "why would you", imperative demands without explanation
```

**Fix:** Engineering manager reviews a sample of PR comments monthly. Feedback to reviewers on comment quality. Model kind, specific, actionable comments publicly.

**Prevention:** Include "commenting with respect" in new employee onboarding. Tech leads model excellent review comments, especially when commenting on their own past mistakes.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Code Review` — understanding the review process itself is prerequisite to optimising it
- `Code Standards` — best practices assume standards exist to reduce style debates

**Builds On This (learn these next):**
- `Pair Programming` — synchronous alternative/complement to async code review
- `Technical Debt` — review best practices prevent debt from accumulating; understanding debt clarifies what review is protecting

**Alternatives / Comparisons:**
- `Pair Programming` — real-time alternative; eliminates async latency but requires more schedule coordination
- `Mob Programming` — extreme collaboration; highest quality, highest time cost

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Techniques making reviews fast, deep,     │
│              │ and collaborative rather than theatrical  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Code review exists but doesn't improve    │
│ SOLVES       │ quality — creates friction without benefit│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Review quality is determined by habits,   │
│              │ not tools. Bad practices corrupt the      │
│              │ best review tool.                         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Every team doing code review — practices  │
│              │ are not optional accessories              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never skip; adapt practices to team size  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Higher-quality reviews vs. discipline     │
│              │ overhead to keep PRs small and described  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Surgical protocol for code: specific     │
│              │  steps that prevent preventable errors."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Pair Programming → Technical Debt →       │
│              │ Code Coverage                             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A senior engineer on your team reviews every PR thoroughly and produces detailed, technically accurate feedback. However, they take 3–4 days to review, have a backlog of 10+ PRs, and often review PRs that are outside their domain just to maintain quality control. This creates a bottleneck: nothing merges without their approval. Design a systematic approach to redistribute review load without losing the quality bar this engineer maintains.

**Q2.** Google's code review culture famously encourages reviewers to approve code "when it's better than before" rather than holding out for perfection. Amazon's culture values raising the bar and has reviewers who ask for significant changes before approval. Each culture produces different outcomes. What are the specific conditions (product stage, team size, codebase maturity, risk tolerance) under which each approach is better? Can a team implement both simultaneously?

