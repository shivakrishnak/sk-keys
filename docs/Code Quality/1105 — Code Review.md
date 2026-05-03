---
layout: default
title: "Code Review"
parent: "Code Quality"
nav_order: 1105
permalink: /code-quality/code-review/
number: "1105"
category: Code Quality
difficulty: ★★☆
depends_on: Version Control, Code Standards, Linting
used_by: Code Quality, CI/CD Pipeline, Technical Debt, Pair Programming
related: Code Review Best Practices, Pair Programming, Static Analysis
tags:
  - bestpractice
  - intermediate
  - cicd
  - devops
---

# 1105 — Code Review

⚡ TL;DR — Code review is the structured process of having one or more developers examine another developer's code changes before they are merged, to catch bugs, improve quality, and share knowledge.

| #1105 | Category: Code Quality | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Version Control, Code Standards, Linting | |
| **Used by:** | Code Quality, CI/CD Pipeline, Technical Debt, Pair Programming | |
| **Related:** | Code Review Best Practices, Pair Programming, Static Analysis | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A developer writes a feature. They understand the feature completely — the context, the constraints, the business rule. They commit directly to `main`. The code works as they understood it. Four months later, a different developer needs to modify the feature and discovers that the original implementation made an assumption that is no longer valid. The assumption was never challenged — because no one other than the original author ever read the code. The bug was always there, implicit and invisible.

**THE BREAKING POINT:**
Writing code is inherently egocentric: the author understands their own context so deeply that they cannot see what they've omitted or assumed. Every developer has blind spots in their own code. These blind spots are bugs, missing edge cases, and undocumented assumptions. Without an external reviewer, these blind spots live in production.

**THE INVENTION MOMENT:**
This is exactly why **code review** was formalised: to introduce a second (and third) perspective that can see what the author cannot — not as adversarial criticism, but as a collaborative quality gate that improves the code and spreads knowledge simultaneously.

---

### 📘 Textbook Definition

**Code review** (also called **peer review** or **pull request review**) is the systematic examination of source code by one or more developers other than the author, prior to merging into a shared branch. Code review checks for: **correctness** (does the code do what it claims? are edge cases handled?), **design** (is the approach appropriate? does it fit the existing architecture? are abstractions correct?), **readability** (can a new developer understand this code in 5 minutes?), **security** (are there injection risks? sensitive data exposed?), **performance** (are there N+1 queries? unnecessary loops?), and **test coverage** (are the tests meaningful? do they test what matters?). Modern code review operates via **pull requests** (GitHub, GitLab, Bitbucket) that display diffs, allow inline comments, and record approvals. Code review is the primary mechanism for knowledge transfer, consistency enforcement, and bug prevention in collaborative development teams. It complements but does not replace automated checks (linting, static analysis, testing).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A second pair of eyes on every change before it goes to production.

**One analogy:**
> Code review is like aircraft pre-flight checks. A pilot may be highly experienced, but still runs a checklist before every flight with a co-pilot confirming each item. Not because the pilot is incompetent — but because under cognitive load, experienced people miss things. The co-pilot's "confirmed" on each item provides the independent verification that no single person can reliably give themselves. Code review is your co-pilot: a second check before the software "takes flight."

**One insight:**
Studies consistently show that code review catches 60–90% of defects — more than unit testing alone. The author of code is the worst person to review it: they mentally "fill in" gaps and read what they intended to write rather than what they wrote. A reviewer reads what is actually there.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The author of code cannot effectively review their own code — they carry the same mental context that produced the error.
2. A second perspective with no prior context will encounter every assumption the author made implicitly, making those assumptions explicit and challengeable.
3. Code that a qualified reviewer cannot understand in 10 minutes will cause future maintenance problems — review is also a readability check.

**DERIVED DESIGN:**
Because author self-review is ineffective, external review is required. Because review provides knowledge transfer, all team members benefit from reviewing each other's code (not just senior reviewing junior). Because reviewers' time is valuable, reviews must be appropriately scoped — PRs should be small enough to review in 30–60 minutes (typically < 400 lines of meaningful code changes).

**THE TRADE-OFFS:**
Gain: Bug detection, knowledge transfer, architecture consistency, team standards enforcement, shared ownership.
Cost: Latency (PRs wait for reviewers), reviewer time (reviewing is doing work), potential for review as gatekeeping/politics rather than collaboration.

---

### 🧪 Thought Experiment

**SETUP:**
A developer implements a payment processing feature. The implementation looks correct. The developer tests the happy path. It works.

**WITHOUT CODE REVIEW:**
The developer pushes to `main`. The code ships. A reviewer would have noticed: the code deducts payment balance but doesn't handle the case where the payment gateway returns HTTP 202 (accepted but not confirmed — an async response). The developer assumed all non-error responses meant confirmed payment. In production, 0.1% of payment gateway responses are 202. For 0.1% of users, payment is deducted but not confirmed. Data corruption for months before discovered.

**WITH CODE REVIEW:**
Reviewer reads the code: "What happens if the gateway returns 202?" Developer: "That means success, right?" Reviewer: "Actually, 202 means accepted for later processing — not confirmed. We need to poll for status." Developer adds async handling. Bug never ships.

**THE INSIGHT:**
The reviewer asked one question in 2 minutes that would have saved months of incident investigation. The reviewer knew the edge case not because they're smarter, but because they weren't in the author's mental context — they saw the code fresh and asked the question a newcomer would ask.

---

### 🧠 Mental Model / Analogy

> Code review is like editing a manuscript. An author writes with total immersion — they see the story they *intended* to write. An editor reads what *is actually written*, finding gaps in logic the author assumed would be obvious, plot holes the author forgot to close, and passages that make sense to the author but confuse a first-time reader. The best editor combines respect for the author's vision with clear-eyed assessment of what the manuscript actually says. Code review is manuscript editing: the author sees intent; the reviewer sees reality.

- "Author's immersion" → developer's contextual blindspot
- "Editor reads what is actually there" → reviewer encounters the code fresh
- "Logic gaps the author assumed were obvious" → missing edge cases
- "Plot holes" → missing null checks, unhandled error paths
- "Best editor respects the vision" → constructive, not destructive review

Where this analogy breaks down: an editor works on finished manuscripts; code reviewers work on in-progress changes. Code review feedback is incorporated before "publication" (merge) — making it a collaborative draft revision process, not a post-publication critique.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Code review is when another developer reads your code before it goes into the shared codebase and gives you feedback. They might find bugs you missed, suggest simpler approaches, or ask questions about parts they don't understand. This process makes the code better and spreads knowledge across the team.

**Level 2 — How to use it (junior developer):**
When you open a PR, assign a reviewer and write a description: what does this change do? Why does it do it this way? What edge cases did you consider? This context helps the reviewer go deep on logic rather than spending time understanding what the code does. As a reviewer: read for correctness first (does this do what it says?), then readability (can I understand this in 10 minutes?), then style (if no automated linting, check style). Ask questions rather than making demands: "What happens when this is null?" not "This will NPE, fix it."

**Level 3 — How it works (mid-level engineer):**
Effective code review requires a **review contract**: the PR author prepares the PR for review (small, focused, description, self-review first); the reviewer has a clear checklist (correctness, security, readability, test coverage); reviewer and author agree that style feedback is the last priority (automated checks cover style). **PR size** is the single biggest determinant of review quality: research shows that reviews of > 400 lines of code receive significantly less thoughtful feedback because reviewer cognitive load exceeds threshold. Most teams enforce PR size limits or strongly advise < 300 lines. **Review latency** is the second factor: PRs that sit unreviewed for > 24 hours create flow disruption as authors context-switch away and must context-switch back.

**Level 4 — Why it was designed this way (senior/staff):**
The formalization of code review correlates with the rise of distributed version control (Git) and pull request workflows (GitHub, 2008). Before PR workflows, code review was ad-hoc (email patches, in-person walkthroughs). The PR-based workflow made review asynchronous, persistent (comments attached to diffs), and auditable (who approved what, when). The deeper purpose of code review is **collective code ownership** — the cultural norm that every developer is responsible for the entire codebase, not just their files. Without review, code becomes siloed: developer A owns `PaymentService`, developer B owns `OrderService`, and neither understands the other's code. With review: every change is seen by at least one other developer, spreading knowledge and ownership. Modern practices push toward smaller, more frequent PRs (continuous review) rather than large, infrequent reviews — aligning with trunk-based development and continuous integration principles.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────┐
│  CODE REVIEW LIFECYCLE                          │
├─────────────────────────────────────────────────┤
│                                                 │
│  Developer writes feature on branch             │
│         │                                       │
│         ▼                                       │
│  Developer self-reviews the diff (removes noise)│
│         │                                       │
│         ▼                                       │
│  Opens Pull Request:                            │
│  - Description: what, why, edge cases           │
│  - Links: ticket, related PRs                   │
│  - Reviewer assigned                            │
│         │                                       │
│         ▼                                       │
│  CI runs: lint, tests, static analysis          │
│         │                                       │
│         ▼                                       │
│  Reviewer reads PR:                             │
│  1. Correctness (bugs, edge cases)              │
│  2. Security (injection, data exposure)         │
│  3. Design (abstractions, fit to architecture)  │
│  4. Readability (can I understand this?)        │
│  5. Test quality (do tests cover what matters?) │
│         │                                       │
│         ▼                                       │
│  Reviewer comments: questions / change requests │
│  Author responds / updates code                 │
│         │                                       │
│         ▼                                       │
│  Reviewer approves                              │
│         │                                       │
│         ▼                                       │
│  Merge to main                                  │
└─────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Feature branch: 280 lines changed
  → Developer self-reviews, removes 20 debug logs
  → PR opened, reviewer assigned
  → CI passes: lint ✓, tests ✓, SpotBugs ✓
  → Reviewer: 3 comments (missing null check,
    clarify method name, add test for edge case)
  [← YOU ARE HERE: reviewer reads, author responds]
  → Author: 2 hours, fixes all 3
  → Reviewer: "LGTM" (Looks Good To Me)
  → Merge: feature ships with 3 fewer bugs
```

**FAILURE PATH:**
```
PR: 1,400 lines changed (too large)
  → Reviewer: too much context to hold
  → Reviewer skims: "looks fine, LGTM"
  → Missing: security issue at line 847
  → Merge accepted
  → Bug ships
→ Prevention: enforce PR size < 400 lines per
  team norm; split large features into sub-PRs
```

**WHAT CHANGES AT SCALE:**
At large scale (Google, Meta), **code review automation** augments human review: ML-based tools suggest reviewers based on file ownership, flag high-risk changes (database migrations, auth code) for mandatory senior review, and auto-approve low-risk changes (documentation, test additions).

---

### 💻 Code Example

**Example 1 — Effective PR description:**
```markdown
## PR: Add payment retry mechanism

### What
Adds exponential backoff retry for payment gateway 
timeouts. Maximum 3 retries with 1s / 2s / 4s delays.

### Why
Gateway returns HTTP 503 under high load (observed 
~0.2% of requests). Currently these fail immediately;
with retry, ~95% of these recover within 3 attempts.

### Edge cases considered
- Idempotency: payment request UUID used as idempotency
  key so retries are safe
- Non-retryable errors: 4xx errors are NOT retried
  (client errors = permanent failures)
- Timeout: total retry window < 10s to avoid starving
  the request thread pool

### Tests added
- Unit: PaymentServiceTest - retry on 503
- Unit: PaymentServiceTest - no retry on 400
- Integration: PaymentIntegrationTest - full flow
```

**Example 2 — Effective review comment styles:**
```
// ❌ BAD review comment (demands, no explanation)
"This is wrong. Use Optional."

// ✅ GOOD review comment (question + context)
"What happens when findById() returns null here? 
Looks like it would NPE on line 42. 
Could use Optional: return userRepo.findById(id)
  .orElseThrow(() -> new UserNotFoundException(id));
Happy to discuss if there's a reason null here is valid."

// ❌ BAD: style comment when linter should handle it
"Line 56 should be indented with 4 spaces not 2"

// ✅ GOOD: only if linter is misconfigured
"Checkstyle is passing but looks like the IDE formatter
isn't matching our config. See CONTRIBUTING.md §3."
```

---

### ⚖️ Comparison Table

| Review Approach | Speed | Depth | Knowledge Transfer | Best For |
|---|---|---|---|---|
| Async PR review | Medium | High | Medium | Standard team workflow |
| Pair programming | Slow | Very high | Very high | Complex features, onboarding |
| **Automated review (linting)** | Fast | Low (style only) | None | Style/quality gates |
| Mob programming | Slowest | Highest | Highest | Critical/complex decisions |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Code review is for catching bugs | Catching bugs is one purpose. Knowledge transfer, architecture consistency, and collective ownership are equally important long-term benefits. |
| Senior devs reviewing junior devs is code review | Effective code review is bidirectional. Junior developers review senior code and ask questions that reveal assumptions — highly valuable. |
| More reviewers = better review | Research shows review quality peaks at 2 reviewers. More than 3 reviewers produces diminishing returns and reduced individual accountability. |
| A passing CI pipeline means code review can be skipped | CI catches what machines can check. Code review catches what humans must check: design decisions, business logic correctness, implicit assumptions. These are different domains. |
| Approving a PR means you agree with every line | Approval means you believe the PR meets the standard for merge. Reviewers often approve with comments explaining what they'd improve in a follow-up. |

---

### 🚨 Failure Modes & Diagnosis

**1. Review Bottleneck — PRs Sitting > 24 Hours**

**Symptom:** PRs wait 2–3 days for first review. Developers context-switch. Authors must re-read their own code to respond to late feedback.

**Root Cause:** No review SLA; reviewers are also writing code and default to their own work; PR queue grows faster than reviewers can process.

**Diagnostic:**
```bash
# Measure average PR-to-first-review time
# Using GitHub API:
gh pr list --state all --json createdAt,reviews \
  --limit 100 | \
  jq '[.[] | {created: .createdAt, 
    first_review: (.reviews[0].submittedAt // null)}]'
# Calculate average delay
```

**Fix:** Define team SLA: first review within 4 hours during business hours. Rotate "review duty" — one developer per day responsible for reviewing incoming PRs within the hour.

**Prevention:** Make PR review visible: a Slack notification per new PR, with author ping after 4 hours if no review.

---

**2. Rubber-Stamp Reviews — No Real Feedback**

**Symptom:** Average PR receives LGTM within 5 minutes. Zero comments per PR. Bugs that code review should catch regularly ship to production.

**Root Cause:** Review culture values speed over quality; reviewers feel social pressure not to block colleagues; PR comments feel "negative"; no accountability for approving buggy code.

**Diagnostic:**
```bash
# Check average review time and comment count
# Short review time + 0 comments = rubber stamp
gh pr list --state merged --json 
  "number,comments,reviews" --limit 50 | \
  jq '[.[] | {pr: .number, 
    comments: .comments, 
    reviews: .reviews | length}]'
```

**Fix:** Add review checklist to PR template. Create post-incident practice: "Could code review have caught this? Why didn't it?" Celebrate thorough reviews publicly.

**Prevention:** Review quality is a cultural norm, not a tool problem. Leaders model thorough, detailed reviews. Make it safe to raise concerns.

---

**3. Large PRs Receiving Inadequate Review**

**Symptom:** 2,000-line PRs receive the same review comments as 100-line PRs. Critical changes at the end of the diff are rarely commented on.

**Root Cause:** PR is too large for thorough review. Reviewers' attention drops after 400 lines. Late parts of the diff receive less scrutiny.

**Diagnostic:**
```bash
# Measure average PR size
gh pr list --state merged --json number,additions,deletions \
  --limit 100 | \
  jq '[.[] | {pr: .number, 
    size: (.additions + .deletions)}] | 
    sort_by(.size) | reverse | .[0:10]'
# Large PRs with few comments = review quality issue
```

**Fix:** Enforce PR size limit: no PR > 400 lines without a justification in the description. Large features must be split into a sequence of smaller PRs, each reviewable independently.

**Prevention:** Add PR size check to CI: warn (not fail) when PR exceeds 400 lines of code change.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Version Control` — code review operates through pull requests in version control
- `Code Standards` — reviewers enforce standards; knowing what standards are enforced matters
- `Linting` — linting automates the mechanical checks so reviewers focus on logic

**Builds On This (learn these next):**
- `Code Review Best Practices` — the principles and techniques for effective reviews
- `Pair Programming` — synchronous collaboration alternative or complement to async review

**Alternatives / Comparisons:**
- `Pair Programming` — synchronous alternative: catches issues in real time vs. async
- `Static Analysis` — automated alternative for pattern-detectable issues; does not replace logic review

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Structured peer examination of code       │
│              │ changes before merging to shared branch   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Author blindspot: developers cannot       │
│ SOLVES       │ reliably review their own code            │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Review catches what machines cannot: logic│
│              │ errors, design flaws, implicit assumptions│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Every code change to shared/production    │
│              │ branches, always                          │
├──────────────┼───────────────────────────────----------------------------------------------------------------┤
│ AVOID WHEN   │ Never skip; but scope review to what      │
│              │ humans can check (not style — automate)   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Bug detection + knowledge transfer vs.    │
│              │ review latency and reviewer time cost     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Co-pilot check before every flight —     │
│              │  a second pair of eyes catches what one   │
│              │  cannot see alone."                       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Code Review Best Practices → Pair Prog   │
│              │ → Technical Debt                          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Research shows that a reviewer reading more than 400 lines of code change provides significantly lower defect detection rates — not because of competence, but because of cognitive overload. A team insists they cannot split a 2,000-line feature PR into smaller PRs because "the feature is not complete until all parts are present." Design a strategy for reviewing this PR effectively despite its size, and design a process change to prevent similar large PRs in the future.

**Q2.** Two schools of thought on who should review code: (A) Only developers as experienced or more experienced than the author should review — inexperienced reviewers miss bugs and waste time. (B) All team members should review all code, regardless of experience level. Evaluate both positions using evidence. What specific situations favour each approach? Design a review assignment strategy that captures the benefits of both.

