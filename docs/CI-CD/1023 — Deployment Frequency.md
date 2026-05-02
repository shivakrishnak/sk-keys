---
layout: default
title: "Deployment Frequency"
parent: "CI/CD"
nav_order: 1023
permalink: /ci-cd/deployment-frequency/
number: "1023"
category: CI/CD
difficulty: ★★☆
depends_on: CI/CD Pipeline, Continuous Deployment, DORA Metrics
used_by: DORA Metrics, Lead Time for Changes, Change Failure Rate
related: Lead Time for Changes, Change Failure Rate, MTTR, DORA Metrics
tags:
  - cicd
  - devops
  - intermediate
  - metrics
  - observability
---

# 1023 — Deployment Frequency

⚡ TL;DR — Deployment frequency measures how often a team successfully releases to production, and DORA research shows it correlates with — not compromises — stability and quality.

| #1023 | Category: CI/CD | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | CI/CD Pipeline, Continuous Deployment, DORA Metrics | |
| **Used by:** | DORA Metrics, Lead Time for Changes, Change Failure Rate | |
| **Related:** | Lead Time for Changes, Change Failure Rate, MTTR, DORA Metrics | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A VP asks "how's our engineering team performing?" The engineering manager shows the number of story points delivered per sprint. But story points completed don't tell you whether customers are getting value. A team can deliver 100 story points per sprint while deploying to production every 6 months. In those 6 months, no customer sees the features. Bugs accumulate. Technical debt grows. The team feels productive; users see nothing changing.

**THE BREAKING POINT:**
Without a production-focused metric, teams optimise for the wrong thing. Story points reward completion of work, not delivery to users. Before DORA metrics were established, software delivery performance was measured by proxy metrics (code coverage, velocity) that didn't correlate with actual business outcomes.

**THE INVENTION MOMENT:**
This is exactly why deployment frequency was established as a software delivery metric: it measures actual delivery to users — the outcome the business cares about — and DORA research proved it correlates with both organisational performance and stability.

---

### 📘 Textbook Definition

**Deployment frequency** is a DORA (DevOps Research and Assessment) metric measuring how often an organisation successfully deploys code to production — typically calculated as deployments per day, week, or month. DORA research (Accelerate, 2018) classifies teams into four performance bands: **Elite** (multiple deploys per day), **High** (once per day to once per week), **Medium** (once per month to once every 6 months), and **Low** (less than once every 6 months). High deployment frequency is consistently associated with higher reliability, lower change failure rates, and better business outcomes — contradicting the intuition that rapid deployment compromises stability. High-frequency deployment is enabled by automated CI/CD pipelines, trunk-based development, comprehensive automated testing, and feature flags.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
How many times per day (or week) does working code reach your users — the most direct measurement of delivery pace.

**One analogy:**
> Deployment frequency is like a restaurant's table turnover rate. A restaurant that turns tables 4 times a night serves 4x as many customers as one that turns once. But high turnover requires efficient kitchen processes — taking shortcuts gives poor food quality and the restaurant fails. High deployment frequency requires good engineering processes — taking shortcuts gives production incidents and the platform fails. Both metrics reveal process quality, not just activity.

**One insight:**
The counter-intuitive DORA finding: elite performers deploy hundreds of times per day AND have lower change failure rates and faster recovery than low performers who deploy once per month. Frequent deployment is not the cause of instability — it's the cure. Each deployment is small, tested, and reversible. Monthly deployments are large, risky, and hard to roll back.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Value is only delivered when code reaches production — code completed but not deployed has zero user impact.
2. Small, frequent changes are lower risk than large, infrequent changes — smaller blast radius and easier rollback.
3. Deployment frequency is a lagging indicator of pipeline automation quality — you can't deploy frequently without invested automation.

**DERIVED DESIGN:**
High deployment frequency requires resolving the bottlenecks that impede deployment: manual testing (replaced by automated), manual approval gates (reduced for routine changes), long build times (optimised), flaky tests (fixed). Each improvement to the pipeline increases deployment frequency. Conversely, measuring deployment frequency surfaces which bottlenecks actually limit delivery pace.

DORA defines "successful deployment to production" as the trigger event — failed deployments or deployments that were immediately reverted don't count. This forces precision: it's not "number of PRs merged" or "number of CI runs" — it's reaching production successfully.

**THE TRADE-OFFS:**
**Gain:** Direct measure of value delivery; reveals pipeline bottlenecks; forces automation investment.
**Cost:** Raw frequency can be gamed (deploy trivial changes frequently). Must be measured alongside change failure rate to avoid optimising for frequency at expense of quality.

---

### 🧪 Thought Experiment

**SETUP:**
Two teams, both building features of similar complexity. Team A deploys every 2 weeks (sprint cadence). Team B deploys multiple times per day.

**WHAT HAPPENS WHEN A CRITICAL BUG IS DISCOVERED IN PRODUCTION:**
Team A discovers a security vulnerability on Monday. It must be patched urgently. But the next planned deployment is Friday. The team must create an emergency hotfix process — a special pipeline, special approval, special deployment procedure. They execute it under stress. The hotfix contains an error. Another emergency. 48 hours to fully resolve.

Team B discovers the same vulnerability on Monday. They fix it, push to CI, CI passes in 8 minutes. They deploy via the same pipeline they use 20 times a day. The fix is live in 30 minutes. Zero special process needed.

**THE INSIGHT:**
High deployment frequency means the deployment process itself is so reliable and routine that emergency fixes don't require emergency processes. The deployment muscle is exercised constantly. Teams that rarely deploy are out of shape — emergencies reveal the weakness.

---

### 🧠 Mental Model / Analogy

> Deployment frequency is like flight hours logged by a pilot. A pilot who flies daily is more proficient and safer than one who flies once a month. Daily flying keeps skills sharp, procedures automatic, and responses to unexpected situations fast. Monthly flying means a rusty checklist, uncertain procedure memory, and longer reaction times to problems. High deployment frequency means the deployment procedure is second nature; rollback is reflexive; pipeline failures are diagnosed instantly.

- "Daily flight hours" → daily deployments
- "Pilot proficiency" → team deployment capability
- "Emergency procedure fluency" → rollback speed and ease
- "Rusty monthly pilot" → team that deploys monthly struggles with hotfixes

Where this analogy breaks down: pilots can review procedures before flying even after a gap. Software deployments happen under pressure with less preparation time. The muscle memory metaphor holds — the team that deploys daily acts automatically; the monthly team acts deliberatively and is slower under pressure.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Deployment frequency simply counts how often your team puts new code live for users. Deploying many times a day means users see improvements constantly and bugs get fixed faster. Deploying once a month means users wait and problems accumulate while waiting for the next release.

**Level 2 — How to use it (junior developer):**
Track deployments using your CI/CD platform: count successful `helm upgrade` / `kubectl apply` / Terraform apply events in your production environment per day. GitHub Actions deployments: Events → Deployments. Calculate 7-day rolling average. Target the next DORA band up from where you are. If you're at once/week, target once/day — identify the bottleneck (manual approval? slow tests? risky large PRs?) and address it.

**Level 3 — How it works (mid-level engineer):**
Deployment frequency is measured precisely as: number of successful deployments to production per unit time (day/week). Distinguish "deployment" (code reaches production) from "release" (feature available to users) — feature flags decouple these. A team might deploy 20 times/day but release features weekly (flags control visibility). This is the correct model: frequent deployment (risk management) with controlled release (business management). Track via: (1) CD pipeline success events (GitHub Actions environment events), (2) deployment tracking tools (LinearB, Sleuth, DORA4), (3) DORA4 API if using Google Cloud Deploy.

**Level 4 — Why it was designed this way (senior/staff):**
The DORA research (Nicole Forsgren, Jez Humble, Gene Kim — "Accelerate", 2018) used a 4-year longitudinal study of 23,000+ survey respondents to prove that deployment frequency, lead time, change failure rate, and MTTR form a cluster of capabilities that predict organisation performance. The key finding was that high performers excelled at BOTH speed (frequency, lead time) AND stability (change failure rate, MTTR) — disproving the commonly believed trade-off. The 2023 DORA report added a fifth metric: "reliability" (meeting SLOs). Industry has also extended to "deployment frequency by service" — microservice architectures allow each service to deploy independently, so aggregate frequency is misleading; per-service frequency reveals bottleneck services.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│  DEPLOYMENT FREQUENCY MEASUREMENT           │
├─────────────────────────────────────────────┤
│                                             │
│  MEASURE: successful deploys to PRODUCTION  │
│  (not staging, not dev, not failed deploys) │
│                                             │
│  DORA BANDS:                                │
│  ┌────────────────────────────────────────┐ │
│  │ ELITE  │ > 1 deploy/day                │ │
│  │ HIGH   │ 1/day to 1/week               │ │
│  │ MEDIUM │ 1/month to 1/6mo              │ │
│  │ LOW    │ < 1/6mo                       │ │
│  └────────────────────────────────────────┘ │
│                                             │
│  CALCULATION:                               │
│  7-day rolling average:                     │
│  (deploys in last 7 days) / 7 = per-day    │
│                                             │
│  WHAT COUNTS:                               │
│  ✓ Successful prod deployment               │
│  ✗ Deployment that was reverted immediately │
│  ✗ Staging/pre-prod deployment              │
│  ✗ Infrastructure-only changes (optional)  │
│                                             │
│  TOOLS:                                     │
│  GitHub Deployments API                     │
│  DORA4 / LinearB / Sleuth                   │
│  Custom: grep CI logs for "deploy success" │
└─────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Code merged to main
  → CI: build + test (5 min)
  → CD: deploy to prod [← YOU ARE HERE]
     Deployment event logged:
     {service, version, timestamp, status}
  → Deployment frequency counter += 1
  → 7-day rolling average updated
  → DORA dashboard: 2.3 deploys/day (HIGH band)
```

**FAILURE PATH:**
```
Deploy triggers → production deployment fails
  → Rollback executed
  → Status: "failed" — NOT counted in frequency
  → Change failure rate counter += 1
  → Deployment frequency: unchanged (failed deploy)
  → Both metrics updated accurately
```

**WHAT CHANGES AT SCALE:**
At scale (100+ services), per-service deployment frequency is the actionable metric. A monolith might deploy once per week (medium performer). The same organisation post-microservices decomposition might have 50 services each deploying 5 times/week = 250 deploy events/week. The "organisation deployment frequency" is 250/week, but the metric that matters is per-service frequency — which services are slow to deploy and why?

---

### 💻 Code Example

**Example 1 — Tracking deployments via GitHub Deployments API:**
```yaml
# .github/workflows/deploy.yml
jobs:
  deploy-production:
    steps:
      - name: Create GitHub Deployment
        uses: chrnorm/deployment-action@v2
        id: deployment
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          environment: production
          ref: ${{ github.sha }}

      - name: Deploy
        run: |
          helm upgrade myapp ./helm \
            --set image.tag=${{ github.sha }}

      - name: Update Deployment Status (success)
        if: success()
        uses: chrnorm/deployment-status@v2
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          state: success
          deployment-id: ${{ steps.deployment.outputs.deployment_id }}

      - name: Update Deployment Status (failure)
        if: failure()
        uses: chrnorm/deployment-status@v2
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          state: failure
          deployment-id: ${{ steps.deployment.outputs.deployment_id }}
```

**Example 2 — Querying deployment frequency from GitHub API:**
```bash
# Count successful production deployments in last 7 days
gh api /repos/{owner}/{repo}/deployments \
  --jq '.[] |
  select(.environment == "production") |
  select(.created_at > "2026-04-25T00:00:00Z")' | \
  jq -s 'length'

# Get deployment frequency per service
for repo in service1 service2 service3; do
  count=$(gh api /repos/myorg/$repo/deployments \
    --jq '[.[] | select(.environment == "production")] |
    length')
  echo "$repo: $count deploys (last 30 days)"
done
```

---

### ⚖️ Comparison Table

| DORA Band | Frequency | Typical Team Profile | Typical Blockers |
|---|---|---|---|
| **Elite** | Multiple/day | >50 devs, microservices, fully automated | None significant |
| High | Daily to weekly | 10–50 devs, mostly automated | Some manual gates |
| Medium | Monthly to 6-monthly | <20 devs, semi-automated | Manual testing, large PRs |
| Low | <6-monthly | Any size, manual processes | No CI/CD, fear of deployment |

How to choose your target: Identify which DORA band you're currently in. Identify the bottleneck preventing moving to the next band (use value stream mapping). Address one bottleneck at a time. Measure improvement with 7-day rolling average. Don't optimise frequency in isolation — monitor change failure rate simultaneously.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| High frequency deployments cause more incidents | DORA research shows the opposite: elite performers (multiple deploys/day) have lower change failure rates than low performers (monthly). Small, frequent changes are lower risk than large, infrequent ones. |
| Deployment frequency = PR merge frequency | PRs merged != production deployments. A PR might merge but take hours to pass CD pipeline, or require manual approval. Measure at the production deployment event, not at merge. |
| Higher is always better | Frequency must be measured alongside quality (change failure rate, MTTR). Deploying 100 changes/day with a 30% failure rate is not good performance — it's 30 incidents per day. |
| Measurement requires specialized tooling | Deployment frequency can be measured with a single line: count production deployment events in your CD pipeline or GitHub Deployments API. No specialised tooling required to start measuring. |

---

### 🚨 Failure Modes & Diagnosis

**1. Deployment Frequency Metrics Inflated by Trivial Deploys**

**Symptom:** Team reports 10 deploys/day. Security review reveals 8 of those are automated dependency bumps (Dependabot PRs auto-merged). Actual feature deployments: 2/day.

**Root Cause:** Deployment frequency counter doesn't distinguish feature deployments from dependency updates or config changes. Metric is technically correct but misleading.

**Diagnostic:**
```bash
# List production deployments with context
gh api /repos/{owner}/{repo}/deployments \
  --jq '.[] |
  select(.environment == "production") |
  {id, ref: .ref[0:8], description, created_at}' | \
  jq -s 'sort_by(.created_at) | reverse | .[0:20]'

# Group by commit type
git log main --oneline --since="7 days ago" | \
  grep -E "(feat|fix|chore)" | \
  sort | uniq -c | sort -rn
```

**Fix:** Define what a "deployment" means for your DORA measurement. Options: (1) all production deployments (including dependency updates — these are valid risk-reducing changes); (2) only user-facing changes. Document the definition. Apply consistently. Compare month-over-month trends rather than absolute numbers.

**Prevention:** Document measurement criteria. Use deploy description or labels to categorise (`deployment_type: feature/dependency/config`). Report segmented metrics to management.

---

**2. Long-Running Test Suite Caps Deployment Frequency**

**Symptom:** Team wants to deploy 5x/day but CI takes 45 minutes. Max possible frequency: 2–3 deploys/day per engineer. Team can't move to elite band.

**Root Cause:** Test suite not parallelised. Integration tests run sequentially. 45 min × 2+ deploys = entire day consumed by CI.

**Diagnostic:**
```bash
# Profile CI step durations (GitHub Actions)
gh api /repos/{owner}/{repo}/actions/runs \
  --jq '.workflow_runs[0:5] | .[] | .id' | \
  while read runId; do
    gh api /repos/{owner}/{repo}/actions/runs/$runId/jobs \
      --jq '.jobs[] | {name, duration_ms:
      ((.completed_at | fromdate) -
       (.started_at | fromdate)) * 1000}'
  done

# Identify slowest test suites
# Look at CI job timelines in GitHub Actions UI
```

**Fix:**
- Parallelise test suite into shards (4 parallel jobs × 45min → 12min)
- Separate fast (unit) from slow (integration) test suites
- Run integration tests only when affected code changes
- Cache build artifacts and test dependencies aggressively

**Prevention:** Set CI duration SLA (< 10 minutes for unit tests, < 20 minutes total). Profile and optimise when SLA is breached. Track CI duration as a team metric alongside deployment frequency.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `CI/CD Pipeline` — deployment frequency measures pipeline output; understanding pipeline architecture is required
- `DORA Metrics` — deployment frequency is one of the four DORA metrics; understanding the full framework provides context

**Builds On This (learn these next):**
- `Lead Time for Changes` — the companion DORA metric measuring how long it takes for code to reach production from commit
- `Change Failure Rate` — the quality metric that must be tracked alongside frequency to avoid gaming
- `MTTR` — the recovery speed metric that completes the DORA picture

**Alternatives / Comparisons:**
- `Lead Time for Changes` — frequency (how often) vs lead time (how fast); related but different: you can deploy frequently with slow lead time if you batch commits
- `Deployment throughput` — throughput includes failed deployments; frequency counts only successful ones

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Count of successful production deploys    │
│              │ per unit time (day/week/month)            │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Teams appear productive but delivery to   │
│ SOLVES       │ users is invisible without this metric    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ High frequency = lower risk per deploy,   │
│              │ not higher. DORA proves it empirically.   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always track — it reveals pipeline        │
│              │ maturity and delivery capability          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never track in isolation — pair with      │
│              │ change failure rate to avoid gaming       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Reveals delivery speed vs requires        │
│              │ automation investment to improve          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Pilot flight hours: the more you deploy, │
│              │  the better and safer you get at it."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Lead Time for Changes → Change Failure    │
│              │ Rate → MTTR → DORA Metrics                │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your team's deployment frequency is 3 per week (Medium performer). You're asked to improve to Elite (multiple per day). Your investigation reveals three bottlenecks: (1) manual QA sign-off required before each production deploy — takes 1 day average, (2) integration test suite takes 40 minutes, (3) PRs average 350 lines of code changed. Prioritise the bottlenecks: which one delivers the most improvement per unit of investment to fix, and what is the minimum viable change to each that would move you to High performer (daily frequency)?

**Q2.** A startup deploys to production 15 times per day (Elite band). Their change failure rate is 25% — 3–4 production incidents per day. A traditional enterprise deploys once per month but has a 2% change failure rate. The startup CTO argues their approach is better because they "fix fast" (MTTR < 1 hour). The enterprise VP argues their approach is better because they "break less." Using DORA's research, which team has a healthier software delivery system, and what would each need to change to genuinely improve?

