---
layout: default
title: "Trunk-Based Development"
parent: "CI/CD"
nav_order: 1021
permalink: /ci-cd/trunk-based-development/
number: "1021"
category: CI/CD
difficulty: ★★☆
depends_on: CI/CD Pipeline, Git, Continuous Integration, Feature Flags
used_by: Continuous Deployment, DORA Metrics, Deployment Frequency
related: Feature Branch Workflow, GitFlow, Continuous Integration, Feature Flags
tags:
  - cicd
  - git
  - devops
  - intermediate
  - bestpractice
---

# 1021 — Trunk-Based Development

⚡ TL;DR — Trunk-based development is a Git branching strategy where all developers commit directly to (or merge frequently to) a single shared branch, enabling continuous integration without long-lived feature branches.

| #1021 | Category: CI/CD | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | CI/CD Pipeline, Git, Continuous Integration, Feature Flags | |
| **Used by:** | Continuous Deployment, DORA Metrics, Deployment Frequency | |
| **Related:** | Feature Branch Workflow, GitFlow, Continuous Integration, Feature Flags | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team uses long-lived feature branches. Developer A works on feature X for 3 weeks. Developer B works on feature Y for 3 weeks. Both are ready to merge. Developer A merges first. Developer B now has a 3-week divergence from main. The merge takes 2 days — it's a conflict battlefield. Every conflict must be resolved manually. Integrated tests fail because the combined changes interact in unexpected ways. This "merge hell" or "integration hell" is so painful that developers start delaying merges further. The problem compounds.

**THE BREAKING POINT:**
The longer a branch lives, the more it diverges. The more it diverges, the more painful the merge. The more painful the merge, the more teams avoid merging. This creates a feedback loop that ultimately means integration happens rarely — which is the death of Continuous Integration. Teams that merge daily have trivial merges; teams that merge monthly have catastrophic ones.

**THE INVENTION MOMENT:**
This is exactly why trunk-based development exists: eliminate the merge hell by making integration continuous. Every developer integrates with everyone else's work at least once per day, keeping divergence at hours not weeks.

---

### 📘 Textbook Definition

**Trunk-based development (TBD)** is a source control branching model where all developers integrate their changes into a single, shared branch (the "trunk" or `main`) at least once per day — or commit directly to trunk for small teams. Feature branches, if used, are short-lived (max 1–2 days) and merged back to trunk before they can diverge significantly. Trunk-based development is a prerequisite for true Continuous Integration (CI): CI requires that all code is integrated continuously, which cannot happen when developers maintain isolated feature branches for weeks. Feature flags (toggles) allow incomplete features to be merged to trunk without exposing them to users, decoupling deployment from release. TBD is identified in the DORA research as one of the technical practices most strongly correlating with high software delivery performance.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Everyone pushes to the same branch every day so integration problems surface immediately, not at merge time.

**One analogy:**
> Trunk-based development is like musicians rehearsing together daily vs having each musician practice their part alone for 3 weeks before a joint rehearsal. Daily practice reveals incompatibilities immediately — a tempo change in the piano part is noticed by the violinist the next day. Practice in isolation for 3 weeks, and the joint rehearsal is chaotic: tempos clash, keys were misunderstood, the arrangement must be redone.

**One insight:**
The key insight is that "integration" in Continuous Integration means integrating with other developers' code — not just running your own tests. A developer can have a green CI build on a feature branch for weeks while being completely disconnected from what their teammates are building. Trunk-based development restores the "continuous" in CI by forcing daily integration with the shared codebase.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Merge conflicts and integration failures grow superlinearly with branch lifetime — a 1-day branch has trivial merges; a 1-month branch has catastrophic ones.
2. The trunk must always be in a releasable state — every commit to trunk must pass CI, never break the build.
3. Incomplete features can be in trunk as long as they're not exposed — feature flags decouple code completeness from user-visible feature availability.

**DERIVED DESIGN:**
For trunk to always be releasable, two practices are required: (1) **feature flags** — incomplete features are behind a flag (`if (featureEnabled("new-checkout"))`) that is off in production until ready; (2) **branch by abstraction** — large refactors are done by creating an abstraction layer (interface), implementing the new code behind it, and switching the implementation when complete. Both techniques allow partial work to live in trunk without breaking production.

Short-lived feature branches (the "scaled trunk-based development" variant) are branches that live for at most 1–2 days and are merged to trunk via PR review. PRs are small (< 400 lines), fast to review (< 1 hour), and merged the same day they're opened.

**THE TRADE-OFFS:**
**Gain:** No merge hell; true continuous integration; fast feedback on integration failures; deployable at any time.
**Cost:** Requires disciplined feature flag management. Requires team culture of small, complete commits. Requires robust CI that can validate trunk is always green. Incomplete work in trunk can create confusion without clear feature flag ownership.

---

### 🧪 Thought Experiment

**SETUP:**
Two developers, Alice and Bob, are building interrelated features: Alice adds a new user authentication system; Bob adds a new checkout flow that relies on the authentication system. 3-week timeline. Compare long-lived branches vs trunk-based.

**WHAT HAPPENS WITH LONG-LIVED BRANCHES:**
Alice and Bob each branch off main. Alice modifies the `User` model and auth logic for 3 weeks. Bob integrates with the old `User` model for 3 weeks. On merge day: Bob's code calls methods that Alice has deleted. Bob's entire feature must be partially rewritten. Combined 2 days of merge conflict resolution. Tests needed to be redone. Deadline missed.

**WHAT HAPPENS WITH TRUNK-BASED:**
Alice commits the first auth changes to trunk on day 1. Bob immediately sees the new `User` interface. Bob adapts his feature to the new interface on day 2 — a tiny change, not a 2-day rewrite. Alice adds more auth logic on day 3. Bob integrates again — another trivial merge. Throughout the 3 weeks, both are continuously reviewing each other's progress. The final integration is a non-event.

**THE INSIGHT:**
The 2-day merge conflict resolution at the end of a 3-week branch is the deferred cost of 3 weeks of accumulated divergence. Trunk-based development front-loads the cost — paying it daily in small increments instead of weekly in a painful lump sum.

---

### 🧠 Mental Model / Analogy

> Trunk-based development is like a shared document in Google Docs versus emailing Word attachments. In Google Docs, everyone edits the single document and conflicts are visible in real-time. In email, everyone edits their own copy and the merge happens when one person tries to combine all the different versions received on Friday afternoon. Real-time editing eliminates the email-merge problem by making integration continuous.

- "Google Doc" → the trunk branch
- "Everyone editing the same document" → daily commits to trunk
- "Conflict visible in real-time" → CI immediately catches integration failures
- "Email attachment version" → long-lived feature branch
- "Friday afternoon merge" → painful end-of-sprint merge
- "Track changes" → git history / PR reviews for trunk commits

Where this analogy breaks down: Google Docs conflicts are trivial (two people changed the same word). Code merges are semantic — two independent changes that don't textually conflict can still logically break the system. CI tests are the semantic conflict detector; git merge resolution is only the syntactic layer.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Instead of every developer working on their own isolated copy of the code for weeks before combining, trunk-based development means everyone's changes go into the shared codebase at least once a day. Problems are found the same day, not weeks later.

**Level 2 — How to use it (junior developer):**
Make small, complete commits to trunk (or very short-lived branches). Every commit should pass all tests. Use feature flags to hide incomplete features: wrap new code in `if (isFeatureEnabled("feature-x"))`. Configure CI to run on every push to trunk. Never push code that breaks the build. If you break it, fix it immediately — the trunk is everyone's foundation.

**Level 3 — How it works (mid-level engineer):**
In scaled TBD (teams of 10+), use short-lived feature branches (max 1–2 days, < 400 lines per PR). PRs are reviewed and merged the same day. CI on the PR branch must pass before merge. Merge strategy: squash merge preserves clean linear history. Feature flags managed in a feature flag service (LaunchDarkly, Unleash) with lifecycle: created → development → testing → production rollout → permanent removal. Branch by abstraction: create `interface AuthService`, implement `LegacyAuthService` and `NewAuthService`, use feature flag to switch at runtime, remove `LegacyAuthService` when migration is complete.

**Level 4 — Why it was designed this way (senior/staff):**
TBD was a de-facto practice at Google, Facebook, and Netflix before it was theorised — these organisations had large codebases and large teams where branch management overhead was prohibitive. The DORA State of DevOps report (2016–2023) consistently identifies TBD as one of the strongest predictors of software delivery performance because it directly enables two other high-performance practices: continuous integration and continuous deployment. The alternative, GitFlow (Vincent Driessen, 2010), was designed for release-based software (apps that ship new versions periodically) — it has `develop`, `feature/*`, `release/*`, and `hotfix/*` branches. GitFlow is correct for monthly-release software; it's counterproductive for continuously-deployed web services.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│  TRUNK-BASED DEVELOPMENT WORKFLOW           │
├─────────────────────────────────────────────┤
│                                             │
│  SMALL TEAM (< 5 devs):                     │
│  Developer → commit → push → main (trunk)   │
│  CI runs immediately on every push          │
│                                             │
│  SCALED TBD (5+ devs):                      │
│                                             │
│  main (trunk)                               │
│  ├── feature/JIRA-123 [< 2 days, < 400 LOC]│
│  │   └── CI passes → PR opened             │
│  │   └── Review → same day                 │
│  │   └── Merge (squash) → trunk            │
│  │                                         │
│  ├── feature/JIRA-456 [< 2 days]           │
│  │   └── CI passes → PR opened             │
│  │   └── Merge → trunk                     │
│                                             │
│  TRUNK ALWAYS GREEN:                        │
│  Every commit to trunk must pass CI         │
│  Any failing commit → immediately reverted  │
│  "broken window" rule: fix before adding   │
│                                             │
│  FEATURE FLAG PATTERN:                      │
│  if (flags.isEnabled("new-checkout")) {    │
│    // new incomplete feature (in trunk,    │
│    // disabled in prod)                    │
│  } else {                                  │
│    // old, working feature                 │
│  }                                         │
└─────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer starts ticket JIRA-123
  → Branch: feature/JIRA-123 from trunk [← YOU ARE HERE]
  → 4 hours of work, 150 lines changed
  → CI green on feature branch
  → PR opened: small, self-reviewable
  → Peer reviews (1 hour max wait)
  → Merge to trunk (squash)
  → Feature flag: new-checkout = off in prod
  → CI on trunk passes
  → Trunk deployed to production
  → new-checkout feature not visible to users yet
  → More tickets → same cycle → feature complete
  → Feature flag enabled for 1% of users (canary)
  → Full rollout → flag removed
```

**FAILURE PATH:**
```
Developer pushes to trunk → CI FAILS
  → Trunk is broken
  → Alert: build is red
  → All team CI blocked (new pushes will also fail)
  → Developer IMMEDIATELY:
     Option A: fix forward in next commit
     Option B: git revert HEAD → push the revert
  → Trunk green within 15 minutes (policy)
  → CI restored
```

**WHAT CHANGES AT SCALE:**
At Google scale (tens of thousands of developers on a monorepo), TBD is practised via submit queues: commits are not pushed directly to trunk but queued, merged serially, and re-tested as a group before landing. This prevents concurrent commits from both "passing" CI on their branch but conflicting when merged. The submit queue is trunk-based development's scaling mechanism for extreme team sizes.

---

### 💻 Code Example

**Example 1 — Feature flag integration:**
```java
// FeatureFlagService.java
// BAD: Long-lived feature branch (weeks of divergence)
// No pattern needed — just don't do it

// GOOD: Feature flag enables incomplete feature in trunk
@Service
public class CheckoutService {

  private final FeatureFlagClient flags;

  public CheckoutResponse checkout(Cart cart) {
    if (flags.isEnabled("new-checkout-v2", userId)) {
      // New, incomplete flow — safely in trunk
      // Flag is OFF in production
      return newCheckoutV2(cart);
    } else {
      // Existing, working flow
      return legacyCheckout(cart);
    }
  }
}
```

**Example 2 — Branch by abstraction:**
```java
// Phase 1: Create abstraction BEFORE new impl
public interface AuthService {
  User authenticate(String token);
}

// Phase 2: Keep old implementation
public class LegacyJwtAuthService implements AuthService { ... }

// Phase 3: Build new impl in trunk (flag-gated)
public class OAuthAuthService implements AuthService { ... }

// Phase 4: Switch via feature flag
@Bean
public AuthService authService(FeatureFlagClient flags) {
  return flags.isEnabled("oauth-auth")
    ? new OAuthAuthService()
    : new LegacyJwtAuthService();
}

// Phase 5: Flag on globally → remove LegacyJwtAuthService
```

---

### ⚖️ Comparison Table

| Strategy | Branch Lifetime | Merge Complexity | CI Quality | Release Model | Best For |
|---|---|---|---|---|---|
| **Trunk-Based Dev** | Hours / days | Very low | Continuous | Any time | Continuous deployment |
| Feature Branch (TBD-scaled) | 1–2 days | Low | Per branch | Any time | Team-based TBD |
| GitFlow | Weeks | High | Per branch | Scheduled | Versioned releases |
| GitHub Flow | Days | Low | Per PR | Any time | Simplified TBD variant |
| Release branches | Until release | Medium | Per branch | Scheduled | Release management |

How to choose: Use **trunk-based development** for teams practicing continuous deployment to production (multiple deploys per day). Use **GitHub Flow** as a simplified alternative (short-lived branches + PR + merge to main). Use **GitFlow** only for software with scheduled monthly/quarterly release cycles (e.g., mobile apps, packaged software) — never for continuously-deployed web services.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| TBD means no code review | TBD is compatible with pull requests — the PR must be small (< 400 LOC) and reviewed the same day. What TBD prohibits is PRs sitting open for a week. Code review and TBD are not in conflict. |
| Feature flags are optional in TBD | Feature flags are a prerequisite for TBD at any meaningful scale. Without them, merging incomplete code to trunk breaks production. They are not optional — they are the mechanism that makes partial work safe in trunk. |
| TBD is only for small teams | Google, Facebook, and Netflix practice TBD at extreme scale (submit queues, monorepos). TBD scales — the mechanism changes (submit queues), but the principle (daily integration) does not. |
| TBD requires everyone to commit perfect code | TBD requires everyone to commit code that doesn't break the build. "Perfect" is not required — working tests are. The build is the bar, not perfection. |

---

### 🚨 Failure Modes & Diagnosis

**1. Trunk Stays Broken for Hours**

**Symptom:** CI is red on main for 3 hours. Three new PRs are blocked from merging. Team productivity stops.

**Root Cause:** Developer broke the build, noticed, started debugging on a new branch instead of immediately reverting or fixing forward in the next commit.

**Diagnostic:**
```bash
# Identify the breaking commit
git bisect start
git bisect bad HEAD
git bisect good <last-known-green-sha>
# git bisect identifies the culprit commit automatically

# Or: check recent commits
git log --oneline -10
gh run list --branch main --limit 5
```

**Fix:**
```bash
# Option A: Revert immediately
git revert HEAD --no-edit
git push origin main
# CI will re-run and pass with old code restored

# Option B: Fix forward (if trivial)
# Fix the bug in next commit within 15 minutes
```

**Prevention:** Enforce "trunk must be green" culture. Set CI timeout: if broken > 30 min, auto-create Jira issue. Implement automated revert policy: if trunk CI fails for > 1 hour, auto-revert the last commit.

---

**2. Feature Flags Never Cleaned Up**

**Symptom:** Codebase has 200 feature flags. 150 are permanently `true` and never removed. Developers can't tell which flags are active. Code has nested `if (flag1 && flag2 && flag3)` blocks everywhere.

**Root Cause:** Feature flags were added but never had a defined lifecycle. No owner, no expiry date, no cleanup process.

**Diagnostic:**
```bash
# List all feature flags in codebase
grep -r "isEnabled\|featureFlag\|launchDarkly" src/ | \
  grep -oP '"[a-z-]+"' | sort | uniq

# Check LaunchDarkly for stale flags
ld-find-code-refs \
  --projKey myproject --repoName myrepo
# Identifies flags in code but archived in LaunchDarkly
```

**Fix:** Create a feature flag lifecycle policy:
1. Every flag must have a Jira ticket for cleanup
2. Flags have a maximum age (60 days) before mandatory removal
3. Flag removal = PR that removes the `if/else` and dead code path
4. LaunchDarkly / Unleash archives flags after removal from code

**Prevention:** Use LaunchDarkly's code references feature to detect stale flags automatically. Add to sprint planning: "feature flag cleanup" as a regular backlog item.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Continuous Integration` — TBD is the branching strategy that enables CI; understanding CI's requirement for integrating continuously is required
- `Git` — TBD is a Git branching model; understanding branches, merges, and commit history is required
- `Feature Flags` — feature flags are the mechanism that makes incomplete code safe in trunk; they're a prerequisite for TBD

**Builds On This (learn these next):**
- `Continuous Deployment` — TBD enables continuous deployment by ensuring trunk is always deployable
- `DORA Metrics` — TBD is identified as a key technical practice correlated with high deployment frequency and low change failure rate

**Alternatives / Comparisons:**
- `Feature Branch Workflow` — short-lived PR-based branching; a compatible variant (< 2 days) or an anti-pattern (> 1 week) depending on duration
- `GitFlow` — the long-lived branch alternative; correct for scheduled releases, counterproductive for continuous deployment
- `GitHub Flow` — a simplified TBD variant: branch → PR → merge to main; compatible with TBD principles

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Branching model: all devs integrate to    │
│              │ one shared branch at least once per day   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Long-lived branches causing merge hell    │
│ SOLVES       │ and delayed integration failures          │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Merge daily: trivial conflict. Merge      │
│              │ monthly: catastrophic conflict. Same code.│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Continuous deployment; web services;      │
│              │ teams wanting high deployment frequency   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Scheduled quarterly releases (GitFlow);   │
│              │ when feature flags can't be used          │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Continuous integration + fast feedback vs │
│              │ feature flag discipline and small commits  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Musicians rehearsing together daily —    │
│              │  not in isolation for weeks."             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Feature Flags → Continuous Deployment →   │
│              │ DORA Metrics → Deployment Frequency       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your team of 12 engineers wants to adopt TBD but has a weekly release cycle managed by a release manager who reviews what goes to production. Currently, features are isolated in feature branches until the weekly release review. Design the transition: which TBD practices can be adopted immediately, which require the release process to change, and what role does feature flagging play in allowing TBD without eliminating the weekly release gate?

**Q2.** A developer argues against TBD: "The trunk is shared by the entire team. If I push incomplete code with a feature flag and it has a bug that crashes the application even when the flag is off (e.g., a null pointer in the flag-checking code itself), I've broken everyone. Long-lived branches isolate my instability." Is this argument valid? Under what specific circumstances is it correct, and how would you design a TBD workflow that addresses this legitimate risk without reverting to long-lived branches?

