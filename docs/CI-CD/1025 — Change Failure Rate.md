---
layout: default
title: "Change Failure Rate"
parent: "CI/CD"
nav_order: 1025
permalink: /ci-cd/change-failure-rate/
number: "1025"
category: CI/CD
difficulty: ★★★
depends_on: DORA Metrics, Deployment Frequency, Lead Time for Changes, CI/CD Pipeline
used_by: DORA Metrics, MTTR, Rollback Strategy
related: MTTR, Deployment Frequency, DORA Metrics, Progressive Delivery
tags:
  - cicd
  - devops
  - deep-dive
  - metrics
  - reliability
---

# 1025 — Change Failure Rate

⚡ TL;DR — Change failure rate measures the percentage of production deployments that cause a degradation requiring a hotfix or rollback, revealing the quality of the delivery process.

| #1025 | Category: CI/CD | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DORA Metrics, Deployment Frequency, Lead Time for Changes, CI/CD Pipeline | |
| **Used by:** | DORA Metrics, MTTR, Rollback Strategy | |
| **Related:** | MTTR, Deployment Frequency, DORA Metrics, Progressive Delivery | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team deploys to production 5 times per week and is proud of their high deployment frequency. What they don't know: 2 of those 5 deployments cause incidents (customer-reported bugs, performance degradations, or service outages). Without measuring change failure rate, the team celebrates their deployment velocity while half of their deployments are degrading the user experience. They're deploying fast — but making things worse on average.

**THE BREAKING POINT:**
Deployment frequency without quality measurement incentivises the wrong behaviour. A team can hit Elite DORA band for deployment frequency (multiple per day) while systematically breaking production. The frequency metric alone rewards a team for deploying garbage quickly.

**THE INVENTION MOMENT:**
This is exactly why change failure rate exists: balance speed metrics (deployment frequency, lead time) with a quality metric that detects when "deploying fast" actually means "breaking things fast."

---

### 📘 Textbook Definition

**Change failure rate (CFR)** is a DORA metric defined as the percentage of deployments to production that result in a degraded service requiring remediation — either a hotfix deployment, rollback, or forward fix. DORA formula: `CFR = (failed deployments / total deployments) × 100%`. DORA bands: **Elite** (0–5%), **High** (5–15%), **Medium** (16–30%), **Low** (> 30%). A "failure" is operationally defined as any deployment that causes a user-visible degradation: increased error rate, latency spike, feature regression, or outage. CFR is the primary quality counterbalance to the speed metrics — high-frequency, low-CFR teams are the true high performers; high-frequency, high-CFR teams are fast-failure teams.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
What percentage of your deployments break production — the quality measure that keeps deployment frequency honest.

**One analogy:**
> Change failure rate is like a surgeon's complication rate. A surgeon who performs 50 operations per month (high frequency) but has a 40% complication rate is not a high performer. A surgeon who performs 50 operations per month with a 2% complication rate is exceptional. Volume without quality is dangerous. The complication rate keeps the operation count meaningful.

**One insight:**
The DORA research finding is that elite performers have BOTH the highest deployment frequency AND the lowest change failure rate. This disproves the intuitive trade-off assumption: "if you want stability, deploy less often." Elite teams deploy many small changes (each of low risk) rather than infrequent large changes (each of high risk). More frequent, smaller changes means lower individual change risk — the opposite of the naive intuition.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every production change carries risk proportional to its size and test coverage.
2. Risk can be reduced but not eliminated — the goal is to detect failures fast (MTTR) and keep changes small.
3. CFR and deployment frequency have an inverse risk relationship: the same total change delivered as 10 small deployments has lower risk per deployment than 1 large deployment.

**DERIVED DESIGN:**
Reducing CFR requires two complementary strategies:
1. **Pre-deployment quality gates** — automated tests, SAST, dependency scanning, type checking that block bad changes before they reach production.
2. **Progressive delivery** — deploying to a fraction of traffic first (canary, feature flags) so failures affect few users before full rollout.

High CFR (> 15%) is a signal of one or more:
- Inadequate automated test suite (changes untested before deployment)
- Deploys too large (complex changes with multiple interacting failure points)
- Insufficient pre-production environment simulation
- No canary or progressive delivery (all-or-nothing deployments)

**THE TRADE-OFFS:**
**Gain:** Balances speed metrics to prevent "garbage fast" optimisation; reveals test suite quality; creates incentive structure aligned with user experience.
**Cost:** Requires precise definition of "failure" — subjective definitions cause inconsistent measurement. False positives (infrastructure blips causing spurious failures) inflate CFR if not excluded.

---

### 🧪 Thought Experiment

**SETUP:**
Two delivery strategies for the same feature set:

Strategy A: Deploy one large monthly release (4 weeks of work in one deployment).
Strategy B: Deploy each small change as it's ready (20 small deployments per month).

**CFR ANALYSIS:**
Strategy A: 1 deployment. High probability of failure — 4 weeks of changes interact in untested ways. When it fails, the root cause is hard to isolate. CFR denominator: 1. If it fails: CFR = 100%.

Strategy B: 20 deployments. Each deployment is 1–5 small changes. Each deployment is small — single point of failure. When one fails, root cause is obvious (changed only 3 files). Remainder of features deploy successfully. If 1 of 20 fails: CFR = 5%.

**THE INSIGHT:**
Strategy A has lower absolute deployment count but higher per-deployment risk. Strategy B has higher count but lower per-deployment risk. DORA research proves Strategy B produces better outcomes for organisations: lower overall CFR, better user experience, and faster hotfix deployments when failures occur.

---

### 🧠 Mental Model / Analogy

> Change failure rate is an airline's incident-per-flight rate. Airlines track incidents per 100,000 flights. Airlines with higher flight volume (more routes, more planes) are not more dangerous — in fact, more experienced airlines with mature safety systems have lower incident rates. The metric normalises risk by volume, making comparison meaningful. CFR does the same: normalises deployment quality by deployment volume.

- "Incident per 100k flights" → CFR % (failures/total deployments)
- "More experienced airline with mature systems" → elite tech team with comprehensive CI/CD
- "Newer airline, less rigorous checks" → team with manual testing, no automated gates
- "Aircraft type / route / conditions" → kind of change / service complexity / test coverage

Where this analogy breaks down: airline incidents are publicly reported events with clear definitions. "Failed deployment" requires a team-agreed definition — some failures are obvious (outage), others are subjective (5% latency increase). Precise CFR measurement requires a defined and consistently applied failure taxonomy.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Change failure rate counts how often deploying new code breaks something for users, as a percentage of all deployments. If you deploy 10 times and 2 of those deployments cause complaints or outages, your CFR is 20%. Lower is better.

**Level 2 — How to use it (junior developer):**
Count: failed deployments in last 30 days / total deployments × 100 = CFR. Track what types of changes fail: untested code paths? Integration failures? Performance regressions? The failure taxonomy reveals where to invest in quality gates. Target: move into the next DORA band. If CFR is 30% (Medium), investigate the root cause of failures and add automated tests for those scenarios.

**Level 3 — How it works (mid-level engineer):**
CFR requires precise failure definition. Common criteria: (1) any deployment followed by an incident incident ticket within 1 hour; (2) any deployment followed by an automated rollback; (3) any deployment that triggers a PagerDuty alert within 2 hours. Automated tracking: CI/CD platform tags each deployment; incident management system (PagerDuty, Opsgenie) links incidents to deployments by timestamp correlation. Tooling: Sleuth, LinearB, DORA4, Google Cloud Deploy all automate CFR calculation from deployment + incident feeds. Manual calculation is error-prone; automated measurement is essential for reliable trend data.

**Level 4 — Why it was designed this way (senior/staff):**
DORA's four-year research (2014–2018) initially identified deployment frequency and lead time as the key speed metrics. They then asked: "Could high-frequency teams be gaming the metrics by deploying frequently but also breaking things frequently?" The addition of CFR and MTTR closed this loop — the four metrics together form a system of checks. Elite performers cannot have high-frequency deployment AND high CFR — they're defined in opposition. The 2023 DORA report refined CFR to distinguish "change-related failures" (directly caused by a deployment) from "operational failures" (infrastructure issues). This distinction affects measurement: a database disk fill that happens to coincide with a deployment is an operational failure, not a change failure. Precise categorisation is required for actionable CFR data.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│  CHANGE FAILURE RATE CALCULATION            │
├─────────────────────────────────────────────┤
│                                             │
│  Events:                                    │
│  Mon: Deploy v1.2.3 → no incident           │
│  Tue: Deploy v1.2.4 → incident (P1 alert)  │
│  Wed: Deploy v1.2.5 → no incident           │
│  Thu: Deploy v1.2.6 → rollback executed    │
│  Fri: Deploy v1.2.7 → no incident           │
│                                             │
│  Classification:                            │
│  v1.2.3: ✓ success                         │
│  v1.2.4: ✗ failure (P1 incident)           │
│  v1.2.5: ✓ success                         │
│  v1.2.6: ✗ failure (rollback)              │
│  v1.2.7: ✓ success                         │
│                                             │
│  CFR = 2 failures / 5 deploys × 100 = 40%  │
│  DORA Band: LOW (> 30%)                     │
│                                             │
│  FAILURE DETECTION SOURCES:                 │
│  • Automated rollback (CD system)           │
│  • PagerDuty / Opsgenie incident created   │
│  • Error rate alert in monitoring           │
│  • Latency SLO breach alert               │
│  • Manual incident report                  │
└─────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Deploy v1.2.4 to production
  → Deployment event recorded: {sha, timestamp, env}
  → Post-deploy monitoring active
  → 45 min: error rate 12% (baseline 0.5%)
  → Alert fires → incident created [← YOU ARE HERE]
  → CFR event: v1.2.4 deployment = FAILURE
  → Rollback: deploy v1.2.3
  → MTTR clock starts
  → Root cause: missing DB index from migration
  → Fix in v1.2.5, re-deploy
  → CFR calculation updated for this period
```

**FAILURE PATH (measurement):**
```
Infrastructure failure coincides with deploy v1.2.8
  → Disk fills on database (unrelated to code)
  → Incident created, linked to v1.2.8 by timestamp
  → Naive CFR calculation: v1.2.8 = FAILURE
  → Correct classification: operational failure
  → CFR analyst reviews root cause
  → Re-classifies: NOT change-related failure
  → CFR adjusted: v1.2.8 not counted
```

**WHAT CHANGES AT SCALE:**
At 100+ services, aggregate CFR is a portfolio metric. Per-service CFR reveals which services have inadequate test coverage or are in a high-churn state. A payment service with 15% CFR is a critical risk; a marketing website with 15% CFR is less critical. Risk-weighted CFR (failure rate × service criticality) gives a more actionable metric for prioritisation.

---

### 💻 Code Example

**Example 1 — Post-deploy monitoring for automated CFR detection:**
```yaml
# GitHub Actions: post-deploy monitoring job
  monitor-post-deploy:
    needs: deploy-production
    runs-on: ubuntu-latest
    steps:
      - name: Wait for deployment to stabilise
        run: sleep 120  # 2 minutes

      - name: Check error rate
        id: error-check
        run: |
          ERROR_RATE=$(curl -s \
            "https://metrics/api/v1/query?query=\
            rate(http_errors_total[5m])" | \
            jq '.data.result[0].value[1]')
          echo "error_rate=$ERROR_RATE" >> $GITHUB_OUTPUT

          BASELINE=0.005  # 0.5% baseline
          THRESHOLD=0.02  # 2% threshold
          if (( $(echo "$ERROR_RATE > $THRESHOLD" | bc -l) ));
          then
            echo "ERROR RATE TOO HIGH: $ERROR_RATE"
            exit 1
          fi

      - name: Mark deployment as failed
        if: failure()
        run: |
          # Auto-trigger rollback
          helm rollback myapp 0
          # Notify incident management
          curl -X POST $PAGERDUTY_URL \
            -d '{"incident": {"type": "incident", 
            "title": "Deploy '$GITHUB_SHA' caused error spike"}}'
```

**Example 2 — CFR calculation from deployment + incident data:**
```bash
#!/bin/bash
# calculate_cfr.sh
START_DATE="2026-04-01"
END_DATE="2026-04-30"

# Count total deployments
TOTAL=$(gh api /repos/{owner}/{repo}/deployments \
  --jq '[.[] |
  select(.environment == "production") |
  select(.created_at >= "'$START_DATE'") |
  select(.created_at <= "'$END_DATE'")] | length')

# Count failed deployments (those linked to incidents)
# This requires mapping between deployment timestamps
# and PagerDuty incident creation times
FAILED=$(curl -H "Authorization: Token $PD_TOKEN" \
  "https://api.pagerduty.com/incidents?created_at[from]=$START_DATE&services[]=YOUR_SVC_ID" | \
  jq '[.incidents[] |
  select(.first_trigger_log_entry.created_at >= "'$START_DATE'")] | length')

CFR=$(echo "scale=2; $FAILED / $TOTAL * 100" | bc)
echo "CFR: ${CFR}%  (${FAILED} failures / ${TOTAL} deploys)"

# DORA band classification
if (( $(echo "$CFR <= 5" | bc -l) )); then
  echo "DORA Band: ELITE"
elif (( $(echo "$CFR <= 15" | bc -l) )); then
  echo "DORA Band: HIGH"
elif (( $(echo "$CFR <= 30" | bc -l) )); then
  echo "DORA Band: MEDIUM"
else
  echo "DORA Band: LOW"
fi
```

---

### ⚖️ Comparison Table

| Metric | Measures | Quality or Speed | DORA |
|---|---|---|---|
| **Change Failure Rate** | % deploys causing incidents | Quality | Yes |
| Deployment Frequency | Deploys per time unit | Speed | Yes |
| Lead Time | Commit to production time | Speed | Yes |
| MTTR | Recovery time from failure | Quality/Speed | Yes |
| Test Coverage | % code tested | Proxy quality | No |
| Bug Escape Rate | Bugs found in production | Quality | No |

How to choose metric focus: All four DORA metrics together. CFR specifically when: (A) high deployment frequency but poor reliability; (B) investigating why incidents are frequent; (C) validating that quality improvements are having impact. Track test coverage and code quality metrics as leading indicators of future CFR improvement.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Low CFR means no incidents | CFR measures change-related failures. Operational failures (hardware, network, database capacity) are not captured in CFR. A team can have 0% CFR while having frequent operational incidents. |
| CFR and deployment frequency are in trade-off | DORA research proves elite performers have both high frequency AND low CFR. The trade-off is an assumption that doesn't hold for high-performing teams using small changes and automation. |
| A hotfix deployment should be counted in CFR denominator but not as failure | The hotfix is a separate deployment event; the original deployment that caused the incident is the failure. Count the hotfix as a successful deployment (if it succeeds). |
| High CFR is always a developer quality problem | CFR can be high due to: inadequate test environments (environment parity problem), insufficient automated tests (test investment problem), or large batch deployments (process problem). Root cause analysis is required before assigning blame. |

---

### 🚨 Failure Modes & Diagnosis

**1. CFR Measurement Inconsistency Due to Vague Failure Definition**

**Symptom:** Team reports CFR of 8% one month, 22% the next, without apparent change in quality. Management distrusts the metric.

**Root Cause:** "Failure" definition is not codified. Different engineers classify the same incidents differently. One engineer counts "any PagerDuty alert after deploy." Another counts only "customer-impacting incidents requiring hotfix."

**Diagnostic:**
```bash
# Review recent failure classifications
# List all failures logged this month:
curl -H "Auth: $METRICS_TOKEN" \
  "$METRICS_URL/cfr/failures?month=2026-04" | \
  jq '.[] | {deploy_sha, reason, classified_by, incident_id}'

# Check if same incident type is classified differently
# across two engineers or two months
```

**Fix:** Write a one-page CFR failure taxonomy:
- COUNTED: Rollback executed (automated or manual)
- COUNTED: P1/P2 incident opened within 2 hours of deploy
- COUNTED: Hotfix deploy required within 24 hours
- NOT COUNTED: Infrastructure failures (disk, network)
- NOT COUNTED: Incidents clearly unrelated to deploy (third-party API down)

Automate classification where possible (rollbacks = automatic failure). Review edge cases in weekly team meeting.

**Prevention:** Document the failure definition before starting measurement. Review classifications quarterly.

---

**2. High CFR Caused by Large Batch Deployments**

**Symptom:** CFR = 28%. Analysis shows failures cluster on large releases (> 20 changed files). Small deployments almost never fail.

**Root Cause:** Team deploys in weekly batches. Each batch contains 15–20 PRs worth of changes. Complex interactions between multiple changes create failure modes not present in individual changes.

**Diagnostic:**
```bash
# Correlate change size with failure rate
git log --oneline --stat main | \
  grep -E "^\w{7}|files changed" | \
  paste -d: - - | \
  awk -F: '{print $1, $2}' > deploys_with_size.txt

# Cross-reference with failures list
# Do large deploys correlate with CFR spikes?
```

**Fix:** Move from weekly batch releases to continuous deployment. Deploy each PR as soon as CI passes. Use feature flags for incomplete features. Change from "batch risk" (many changes = many potential interactions) to "individual change risk" (one change = one potential failure mode).

**Prevention:** Track deployment batch size alongside CFR. Create a visual showing batch size vs CFR correlation. Use this data to justify investment in continuous deployment.

---

**3. CFR Inflated by Flaky Infrastructure (Not Change-Related)**

**Symptom:** CFR = 22% but post-mortems show 12 of last 15 "failures" were caused by third-party service timeouts, database capacity issues, or network events — not by the deployed code.

**Root Cause:** Failure classification doesn't distinguish change-caused vs environment-caused failures. All incidents linked to recent deployments are counted as CFR failures.

**Diagnostic:**
```bash
# Review incident root causes
curl -H "Auth: $PD_TOKEN" \
  "https://api.pagerduty.com/incidents?statuses[]=resolved" | \
  jq '.incidents[] |
  {id, title,
   root_cause: .last_status_change_on}'

# Tag incidents by root cause category:
# change_related / infrastructure / third_party
```

**Fix:** Implement incident root cause tagging: every resolved incident is tagged as `change_related: true/false`. Modify CFR calculation to exclude `change_related: false` incidents. Present both "total incident rate" and "change failure rate" as separate metrics.

**Prevention:** Create incident root cause taxonomy during incident postmortem process. Require root cause tag before incident closure. Alert on repeated third-party failures as a separate reliability metric.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `DORA Metrics` — CFR is one of the four DORA metrics; the full framework provides context for why this metric exists alongside the others
- `Deployment Frequency` — CFR is meaningless without knowing how often you deploy — the quality counterpart to quantity
- `CI/CD Pipeline` — the pipeline is the mechanism for change delivery; its quality determines CFR

**Builds On This (learn these next):**
- `MTTR` — the recovery speed metric that completes the DORA quality picture alongside CFR
- `Rollback Strategy` — the primary response mechanism when CFR events occur; fast rollback limits the impact of each CFR event
- `Progressive Delivery` — canary and feature flags are the primary technical strategies for reducing CFR

**Alternatives / Comparisons:**
- `MTTR` — CFR measures frequency of failures; MTTR measures duration/impact; both are quality metrics that must be optimised together
- `Error Budget` — SRE's related concept: the percentage of time/requests the service is allowed to fail; CFR is the delivery-focused version

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ % of production deployments that cause    │
│              │ a degradation requiring rollback/hotfix   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ High deployment frequency can mask        │
│ SOLVES       │ "fast-breaking" anti-pattern without CFR  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Elite teams have BOTH high frequency AND  │
│              │ low CFR — they're not in trade-off        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — pair with deployment frequency   │
│              │ to measure speed with quality together    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never skip — but define "failure" clearly │
│              │ before starting to measure it             │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Accurate quality signal vs classification │
│              │ effort for change vs operational failures │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Surgeon complication rate — volume means │
│              │  nothing without quality."                │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ MTTR → Rollback Strategy →                │
│              │ Progressive Delivery → DORA Metrics       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your team's change failure rate is 18% (Medium band). Root cause analysis reveals: 40% of failures are caused by database migration scripts that break under production data volumes not present in staging, 35% are caused by API contract changes that break consuming services, and 25% are "mystery failures" where the deployed code appears identical to a previous successful deploy. Design specific technical interventions for each failure category — not generic best practices, but precise changes to your testing, staging, and deployment process that would address each category's root cause.

**Q2.** Two DORA metrics are meant to balance each other: deployment frequency (speed) and change failure rate (quality). A VP suggests simplifying reporting to "deployments per week without incidents" as a single combined metric. Analyse this proposed metric: what information does it preserve from each DORA metric, what information does it lose, and under what circumstances would a team achieve a high "incident-free deployments per week" number while genuinely having poor engineering practices?

