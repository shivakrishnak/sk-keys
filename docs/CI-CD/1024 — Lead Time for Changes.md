---
layout: default
title: "Lead Time for Changes"
parent: "CI/CD"
nav_order: 1024
permalink: /ci-cd/lead-time-for-changes/
number: "1024"
category: CI/CD
difficulty: ★★☆
depends_on: CI/CD Pipeline, Deployment Frequency, DORA Metrics
used_by: DORA Metrics, Deployment Frequency, Change Failure Rate
related: Deployment Frequency, Change Failure Rate, DORA Metrics, MTTR
tags:
  - cicd
  - devops
  - intermediate
  - metrics
  - observability
---

# 1024 — Lead Time for Changes

⚡ TL;DR — Lead time for changes measures how long it takes from code commit to production deployment, quantifying the speed of the entire software delivery pipeline end-to-end.

| #1024 | Category: CI/CD | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | CI/CD Pipeline, Deployment Frequency, DORA Metrics | |
| **Used by:** | DORA Metrics, Deployment Frequency, Change Failure Rate | |
| **Related:** | Deployment Frequency, Change Failure Rate, DORA Metrics, MTTR | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A product manager asks: "We merged the fix 3 weeks ago — why isn't it live yet?" The engineering manager doesn't know. There's no systematic tracking of where code spends time between merge and production. "It's in the release queue" means it could ship tomorrow or in 2 months. The team can't predict when features will reach customers, making roadmap commitments unreliable. Worse, a security patch merged urgently last week is still not live — it's waiting in the same release queue as feature work.

**THE BREAKING POINT:**
Without measuring lead time, engineering teams cannot diagnose where time is being lost in the delivery process. Code may sit in "ready to deploy" queues for days without anyone knowing. Approval processes add days. Manual environments add hours. The bottleneck is invisible.

**THE INVENTION MOMENT:**
This is exactly why lead time for changes was established as a DORA metric: make the full pipeline duration visible, from the moment code is committed to the moment it serves users, so bottlenecks can be identified and eliminated.

---

### 📘 Textbook Definition

**Lead time for changes** is a DORA metric that measures the elapsed time from a code commit (or PR merge) reaching the production deployment that contains that commit. It represents the total duration of the software delivery pipeline: code review time + CI duration + approval wait times + deployment queue time + deployment execution time. DORA classifies teams into Elite (< 1 hour), High (1 day to 1 week), Medium (1 week to 1 month), and Low (1 month to 6 months). Lead time differs from **cycle time** (developer perspective: from starting work to completing PR) and **deployment frequency** (how often deploys happen, independent of how long they take). Together, deployment frequency and lead time measure the speed dimension of DORA's four key metrics.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The stopwatch from your commit hitting the repo to your code serving real users.

**One analogy:**
> Lead time is like a package delivery SLA. When you ship a package, the courier's lead time is from when they pick it up to when it's delivered. The package moving through sorting facilities, customs, and local delivery is all measured time. Lead time for changes measures your code's journey: from commit (picked up) through CI, staging, approval, and production deployment (delivered to users). A short lead time means a reliable, fast delivery service.

**One insight:**
Lead time and deployment frequency appear to measure the same thing but they're independent. A team can deploy once per day (high frequency) but with a 3-day lead time (medium quality) if commits accumulate for 3 days before being batched into a release. Conversely, a team can commit and deploy in 30 minutes (elite lead time) but only when forced to (monthly deployments — low frequency). Both metrics together describe the full delivery picture.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Lead time is the sum of all wait times and processing times between commit and production.
2. Reducing lead time requires identifying which stage is the bottleneck — not just speeding up already-fast stages.
3. Long lead times directly delay value delivery to users and slow feedback loops for developers.

**DERIVED DESIGN:**
Lead time has two components: **process time** (work actually being done: CI running, deployment executing) and **wait time** (code sitting idle: in a review queue, in a release queue, waiting for manual approval). In most engineering organisations, wait time dominates—CI take 15 minutes, but code waits 2 days for review and 3 days for the next deployment window.

Value Stream Mapping (VSM) is the technique for decomposing lead time:
```
Commit → [Wait: PR review queue] → [Work: Review]
→ [Wait: CI queue] → [Work: CI execution]
→ [Wait: Staging deploy queue] → [Work: Stage deploy]
→ [Wait: Approval] → [Work: Prod deploy]
→ Deployed
```
For most teams, eliminating wait times (not speeding up work times) is the highest-ROI improvement.

**THE TRADE-OFFS:**
**Gain:** Reveals the actual delivery pipeline bottleneck; enables data-driven pipeline optimisation; creates shared understanding between engineering and business of delivery pace.
**Cost:** Accurate measurement requires precise event tracking (commit timestamps, deployment timestamps correlated to commit). Tricky for batched deployments or multi-commit merges.

---

### 🧪 Thought Experiment

**SETUP:**
A team commits a feature at 9am Monday. It enters production at 3pm Thursday — 3.25 days later. Trace the timeline.

**WHAT HAPPENS WITH LEAD TIME MEASUREMENT:**
Value stream mapping reveals:
- 9am Mon: Commit pushed, PR opened
- 9am–3pm Mon: CI running → 6 hours (flaky tests, retries)
- 3pm Mon–10am Tue: PR waiting for review → 19 hours (queue)
- 10am–11am Tue: Review in progress → 1 hour
- 11am Tue: PR merged
- 11am–2pm Tue: CD pipeline queued → 3 hours (deploy slot not available)
- 2pm–3pm Tue: Staging deployment + test
- 3pm Tue–9am Thu: Waiting for release window → 42 hours (weekly releases on Thu)
- 9am–3pm Thu: Release process + prod deployment → 6 hours

Wait time: 19 (review queue) + 3 (CD queue) + 42 (release window) = 64 hours
Process time: 6 (CI) + 1 (review) + 1 (staging) + 6 (release) = 14 hours

**THE INSIGHT:**
The 3.25-day lead time is dominated 82% by wait time (waiting for review, release window, CI queue), not work time. Eliminating the weekly release window and the review queue bottleneck would reduce lead time from 3.25 days to < 4 hours. CI optimization (from 6 hours to 15 minutes) only helps ~5% of the total time.

---

### 🧠 Mental Model / Analogy

> Lead time is like the hospital patient journey metric. A patient arrives at the ER and the hospital tracks "door-to-doctor time." The metric reveals whether the bottleneck is registration (admin), triage (clinical assessment), or room availability (capacity). Without the metric, the ER director guesses. With it, they see: 2 minutes at registration, 25 minutes waiting for triage, 8 minutes triage, 90 minutes waiting for a room. The wait times reveal where to invest.

- "Patient arrival" → code commit / PR merge
- "Leaving hospital treated" → code live in production
- "Door-to-doctor time" → lead time for changes
- "Waiting for triage, room, doctor" → wait times in pipeline stages
- "Hospital director improving process" → engineering manager reducing lead time

Where this analogy breaks down: hospital throughput is limited by physical capacity (beds, doctors). Software pipelines have soft constraints (approval policies, deployment windows) that can be modified much more quickly than building new hospital wings.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Lead time for changes times how long it takes from when a developer finishes writing code to when users can actually use it. If a developer writes a bug fix on Monday and users can use it Monday afternoon, that's elite lead time. If they wait until next Friday's release, that's slow.

**Level 2 — How to use it (junior developer):**
Track lead time by recording two timestamps per change: when the commit was merged to main (T1) and when a successful production deployment containing that commit completed (T2). Lead time = T2 - T1. Calculate median and 95th percentile (median for typical performance, P95 for worst-case). Use tooling: LinearB, Sleuth, or DORA4 calculate this automatically from GitHub + deployment events. Target the next DORA band: if you're at 1 week (Medium), target 1 day (High).

**Level 3 — How it works (mid-level engineer):**
Value stream mapping reveals lead time composition. For a monolithic CI/CD pipeline: Stage 1 wait + Stage 1 work + Stage 2 wait + ... + Production deployment = total lead time. The bottleneck is the stage with highest wait time, not the stage with longest work time. For microservices with independent deployments: each service has its own lead time — the slowest service blocks dependent services from being fully released. Feature flags decouple lead time from release time: code can have 30-minute lead time while the feature has a 2-week "release time" (time from commit to user-visible availability).

**Level 4 — Why it was designed this way (senior/staff):**
DORA's research chose "commit-to-production" as the lead time measurement boundary because it captures the full value stream visible to engineering — from developer action to user-visible outcome. Earlier definitions used "code-complete-to-release," which obscured pipeline efficiency. Commit-to-production exposes CI wait times and deployment window bottlenecks that "code-complete" hides. The distinction between lead time and cycle time is critical for different audiences: cycle time (start-of-work to PR ready) is a developer productivity metric; lead time (commit to production) is a delivery system metric. Engineering leaders should track lead time; developers should track cycle time.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│  LEAD TIME COMPOSITION                      │
├─────────────────────────────────────────────┤
│                                             │
│  T0: Commit merged to main (start clock)   │
│                                             │
│  [CI wait]        0–30 min  (CI queue)      │
│  [CI run]         5–45 min  (build+tests)   │
│  [PR wait]        0–48 hrs  (review queue)  │
│  [PR review]      0.5–4 hrs (work)          │
│  [Deploy wait]    0–72 hrs  (release window)│
│  [Staging deploy] 5–30 min  (work)          │
│  [Approval wait]  0–24 hrs  (sign-off)      │
│  [Prod deploy]    5–20 min  (work)          │
│                                             │
│  T1: Production deployment completes        │
│                                             │
│  LEAD TIME = T1 - T0                        │
│                                             │
│  DORA BANDS:                                │
│  ELITE:  < 1 hour                          │
│  HIGH:   1 day to 1 week                   │
│  MEDIUM: 1 week to 1 month                 │
│  LOW:    > 1 month                         │
│                                             │
│  TYPICAL BOTTLENECK:                        │
│  80% of lead time = wait times              │
│  20% of lead time = actual work             │
└─────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer merges PR at T0 = 10:00am
  → CI triggers: T0+2min (queue wait)
  → CI runs: T0+2min to T0+12min (10 min CI)
  → CD triggers: T0+12min
  → Staging: T0+12min to T0+25min
  → Production: T0+25min to T0+35min
  → T1 = T0+35min
  → LEAD TIME = 35 minutes [← YOU ARE HERE]
  → ELITE performer band
  → Recorded: {commit_sha, T0, T1, lead_time_min}
```

**FAILURE PATH:**
```
Production deployment fails
  → T1 not recorded (deployment failed)
  → Lead time measurement paused
  → Rollback executed
  → Bug fixed in new commit T0'
  → New deployment succeeds at T1'
  → Lead time for fix = T1' - T0'
  → Original commit lead time: T1' - T0 (extended)
```

**WHAT CHANGES AT SCALE:**
At 50+ services, lead time varies dramatically per service. Service A (new feature, actively maintained, automated tests): 20-minute lead time. Service B (legacy, manual QA required, infrequent deploys): 3-week lead time. Aggregate lead time is misleading. Per-service lead time reveals which services are delivery bottlenecks for dependent product features.

---

### 💻 Code Example

**Example 1 — Recording lead time events:**
```bash
# Record T0 (commit merged to main)
# This happens automatically via GitHub webhook
# or via CI trigger time

# Record T1 (production deployment complete)
# In GitHub Actions:
echo "DEPLOYMENT_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  >> $GITHUB_ENV

# Calculate lead time (example in bash)
T0=$(git log -1 --format="%cI" HEAD)  # commit time
T1=$(date -u +%Y-%m-%dT%H:%M:%SZ)    # deploy time

# In JavaScript:
T0_EPOCH=$(date -d "$T0" +%s)
T1_EPOCH=$(date -d "$T1" +%s)
LEAD_TIME_MIN=$(( ($T1_EPOCH - $T0_EPOCH) / 60 ))
echo "Lead time: $LEAD_TIME_MIN minutes"
```

**Example 2 — GitHub Actions tracking with deployment events:**
```yaml
jobs:
  deploy-production:
    steps:
      - name: Get commit time (T0)
        id: t0
        run: |
          T0=$(git log -1 --format="%cI" ${{ github.sha }})
          echo "commit_time=$T0" >> $GITHUB_OUTPUT

      - name: Deploy to production
        run: helm upgrade myapp ./helm \
          --set image.tag=${{ github.sha }}

      - name: Record lead time
        if: success()
        run: |
          T0="${{ steps.t0.outputs.commit_time }}"
          T1=$(date -u +%Y-%m-%dT%H:%M:%SZ)
          T0_EPOCH=$(date -d "$T0" +%s)
          T1_EPOCH=$(date -d "$T1" +%s)
          LT=$(( ($T1_EPOCH - $T0_EPOCH) / 60 ))
          echo "Lead time: ${LT} minutes"
          # Send to monitoring system (Datadog, Grafana, etc.)
          curl -X POST $METRICS_URL \
            -d "{\"lead_time_minutes\": $LT,
                 \"service\": \"myapp\",
                 \"commit\": \"${{ github.sha }}\"}"
```

---

### ⚖️ Comparison Table

| Metric | Measures | Unit | DORA Band |
|---|---|---|---|
| **Lead Time for Changes** | Commit → production | Time | Elite < 1hr |
| Cycle Time | Work start → PR ready | Time | Not DORA |
| Deployment Frequency | Successful deploys | Count/time | Elite: multi/day |
| PR Review Time | PR open → approved | Time | Not DORA |
| CI Duration | CI start → CI complete | Time | Not DORA |

How to choose: Track lead time as your primary delivery speed metric (DORA standard). Track cycle time for developer productivity. Track CI duration and PR review time as leading indicators that predict lead time improvements. All four together give a complete picture of pipeline efficiency.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Lead time = time to write the code | Lead time starts when code is committed (development complete), not when development starts. The total cycle (start-to-production) is much longer; DORA's lead time measures only the pipeline stage. |
| Short lead time requires skipping testing | Elite teams achieve < 1 hour lead time WITH comprehensive automated testing. The key is automation, not shortcuts. The CI pipeline runs the same tests — just in 8 minutes instead of 45. |
| Lead time and deployment frequency are the same metric | Frequency (how often) and lead time (how fast) are Independent. You can deploy rarely with short lead times (each deploy is fast, but you batch changes for a weekly window). DORA uses both because they measure different aspects of delivery performance. |
| Long lead time is always caused by slow CI | Value stream mapping typically reveals 80%+ of lead time is wait time (in queues), not process time (work being done). Speeding up CI from 30 min to 10 min may have less impact than eliminating a 2-day deployment window. |

---

### 🚨 Failure Modes & Diagnosis

**1. Weekly Deployment Windows Dominate Lead Time**

**Symptom:** Lead time P50 = 4 days. CI takes 10 minutes. Every commit waits for the weekly Thursday deployment window.

**Root Cause:** Manual deployment scheduling — deployments only happen at scheduled windows, not continuously after CI passes.

**Diagnostic:**
```bash
# Visualise lead time distribution
# (show wait clustering around weekly windows)
gh api /repos/{owner}/{repo}/deployments \
  --jq '.[] |
  {created_at, environment}' | \
  jq -s 'map(select(.environment == "production")) |
  map(.created_at[0:10]) | group_by(.) |
  map({date: .[0], count: length})'

# If all deploys happen on same day of week → deployment window
```

**Fix:** Eliminate scheduled deployment windows. Deploy continuously after CI passes and automated tests pass. For regulated environments: replace time-based windows with criteria-based promotion (CI green + security scan green + performance test green = auto-deploy). Reserve manual approval only for changes that genuinely require human judgment.

**Prevention:** Define deployment window policy as "automated whenever criteria are met" rather than calendar-based. Treat manual time-based windows as a risk indicator.

---

**2. PR Review Backlog Extends Lead Time to Days**

**Symptom:** Lead time P50 = 3 days. CI takes 10 minutes. Average PR waits 2.5 days before first review.

**Root Cause:** Insufficient reviewer bandwidth. Reviews not time-boxed. Complex PRs (800+ LOC) discourage reviewers.

**Diagnostic:**
```bash
# Calculate average time from PR open to first review
gh api /repos/{owner}/{repo}/pulls \
  --jq '.[] |
  {number,
   created_at,
   first_review_at: .reviews[0].submitted_at}' | \
  jq -s 'map(select(.first_review_at != null)) |
  map({
    number: .number,
    wait_hours: (
      (.first_review_at | fromdate) -
      (.created_at | fromdate)
    ) / 3600
  }) | sort_by(-.wait_hours)'
```

**Fix:**
- Set team SLA: first review within 4 business hours
- Break PRs into smaller units (< 200 LOC)
- Use CODEOWNERS to auto-assign relevant reviewers
- Implement "PR duty" rotation — one engineer per day focused on reviewing

**Prevention:** Track PR review time as a weekly team KPI. Alert when median first-review time exceeds 4 hours. Include review speed in team retrospectives.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `CI/CD Pipeline` — lead time is the duration through the pipeline; understanding each pipeline stage is required
- `DORA Metrics` — lead time is one of the four DORA metrics; the full framework provides context

**Builds On This (learn these next):**
- `Deployment Frequency` — the complementary speed metric; frequency (how often) + lead time (how fast) together describe delivery speed
- `Change Failure Rate` — the quality counterpart; reducing lead time must not increase change failure rate
- `Value Stream Mapping` — the technique for decomposing lead time into wait and process time stages

**Alternatives / Comparisons:**
- `Cycle Time` — developer-perspective metric (start of work → PR ready) vs lead time (commit → production); both measure speed but at different scopes
- `Deployment Frequency` — frequency (how often) vs lead time (how fast from commit); one deployment per day with 4-hour lead time is very different from one deployment per day with 4-week lead time

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Elapsed time from code commit to          │
│              │ production deployment of that commit      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ "Why isn't my fix live?" — pipeline       │
│ SOLVES       │ bottlenecks are invisible without this    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ 80% of lead time is wait time, not        │
│              │ work time — eliminate queues not work     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — track per service, not aggregate │
│              │ to find true bottleneck services          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never skip — but don't optimise alone:    │
│              │ pair with change failure rate             │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Faster delivery to users vs automation    │
│              │ investment needed to achieve it           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Package delivery SLA for your code —     │
│              │  from pickup to doorstep."                │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Change Failure Rate → MTTR →              │
│              │ DORA Metrics → Value Stream Mapping       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You value-stream-map your team's lead time and find the following: CI = 12 min, PR review wait = 18 hours, manual staging sign-off = 8 hours, deployment execution = 15 min. Total = ~26 hours (Medium DORA band). Your manager allocates 2 weeks of investment to improve lead time. Detail exactly how you would spend those 2 weeks — what you'd change in each stage — and what realistic lead time you'd expect to achieve, with justification.

**Q2.** Two competing definitions of "lead time" exist in your organisation: (A) from first commit on the feature branch to production deployment (captures all development time), and (B) from PR merge to main to production deployment (captures only pipeline time). Your product manager wants to use definition A to measure "feature delivery speed." Your engineering VP wants definition B to measure "pipeline efficiency." Neither is wrong. For each definition, describe what specific problems it helps diagnose and what problems it misidentifies — and explain which DORA recommends and why.

