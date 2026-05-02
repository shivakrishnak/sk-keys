---
layout: default
title: "DORA Metrics"
parent: "CI/CD"
nav_order: 1027
permalink: /ci-cd/dora-metrics/
number: "1027"
category: CI/CD
difficulty: ★★★
depends_on: Deployment Frequency, Lead Time for Changes, Change Failure Rate, MTTR
used_by: Engineering Leadership, Platform Engineering, SRE
related: Deployment Frequency, Lead Time for Changes, Change Failure Rate, MTTR
tags:
  - cicd
  - devops
  - deep-dive
  - metrics
  - leadership
---

# 1027 — DORA Metrics

⚡ TL;DR — DORA Metrics are four research-validated measures (deployment frequency, lead time, change failure rate, MTTR) that predict both software delivery performance and overall organisational outcomes.

| #1027 | Category: CI/CD | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Deployment Frequency, Lead Time for Changes, Change Failure Rate, MTTR | |
| **Used by:** | Engineering Leadership, Platform Engineering, SRE | |
| **Related:** | Deployment Frequency, Lead Time for Changes, Change Failure Rate, MTTR | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An engineering VP must present to the CEO: "How is engineering performing?" She has data: 47 story points per sprint, 94% unit test coverage, 12 deployments this month, 3 P1 incidents. None of these numbers tell the CEO whether engineering is getting better or worse, whether investment is paying off, or how the organisation compares to industry peers. The VP can't answer: "Are we a high-performing engineering organisation?" — because there's no agreed-upon definition of what that means, and no research-validated way to measure it.

**THE BREAKING POINT:**
Before DORA, engineering performance was measured by proxy metrics (velocity, coverage, defect counts) with no evidence they correlated with actual outcomes (reliability, speed of value delivery, organisational competitiveness). Management invested in practices and tooling hoping to improve performance, but had no validated framework to confirm improvement was happening.

**THE INVENTION MOMENT:**
This is exactly why DORA (DevOps Research and Assessment) was created: a multi-year empirical study that identified which engineering practices actually correlate with both superior software delivery and better business outcomes — and produced four specific, measurable metrics that any team can use to locate themselves and measure improvement.

---

### 📘 Textbook Definition

**DORA Metrics** are four empirically-validated software delivery performance metrics developed by Nicole Forsgren, Jez Humble, and Gene Kim through the DORA research programme (2013–present), formalised in *Accelerate* (2018). The four metrics are: **Deployment Frequency** (how often code deploys successfully to production), **Lead Time for Changes** (time from commit to production), **Change Failure Rate** (percentage of deployments causing incidents), and **Mean Time to Recovery** (time to restore service after failure). Teams are classified into four performance bands (Elite, High, Medium, Low) for each metric. The research proves that Elite performers excel simultaneously on ALL four metrics — disproving the assumed speed/reliability trade-off. In 2021, a fifth metric was proposed: **Operational Reliability** (meeting SLOs). DORA metrics are the industry standard for engineering delivery performance measurement.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Four numbers that tell you whether your engineering team is a high performer — validated by research on 32,000+ professionals.

**One analogy:**
> DORA metrics are like the four vital signs doctors check first: heart rate, blood pressure, temperature, and oxygen saturation. Each measures a different dimension of health. Together, they give a quick, validated picture of whether a patient is stable, deteriorating, or recovering. A doctor who only checks heart rate is missing critical information. An engineering leader who only tracks velocity (speed) is missing the equivalent of ignoring blood pressure (quality).

**One insight:**
The most important DORA finding: speed and stability are not in trade-off. Elite teams deploy more often AND have fewer failures AND recover faster. This means a team's low deployment frequency is not conservative risk management — it's a symptom of poor automation, large batch sizes, and inadequate testing. The path to better reliability is more automation, smaller changes, and more frequent deployment — not less.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Software delivery performance has two dimensions: throughput (speed) and stability (reliability); both can and should be optimised simultaneously.
2. Practices, not organisation size or technology type, drive delivery performance — DORA research controls for industry, size, and tech stack.
3. Delivery performance predicts business outcomes; teams in Elite/High performance bands have higher profitability, market share, and employee engagement.

**DERIVED DESIGN:**
The four metrics form a 2×2 framework:

```
              SPEED                QUALITY
DEPLOYMENT ─  Deployment Freq   Change Failure Rate
LIFECYCLE  ─  Lead Time         MTTR
```

Speed metrics (frequency, lead time): how fast the team delivers value to users.
Quality metrics (CFR, MTTR): how reliably the team delivers value without breaking things.

The framework's power is in their correlation: teams that improve speed metrics also tend to improve quality metrics (and vice versa) because both are driven by the same underlying technical capabilities (automation, small batch sizes, comprehensive testing, fast feedback loops).

**DORA Performance Bands (2023 State of DevOps Report):**

| Metric | Elite | High | Medium | Low |
|---|---|---|---|---|
| Deployment Frequency | Multiple/day | Daily–Weekly | Monthly | < 6-monthly |
| Lead Time | < 1 hour | 1 day – 1 week | 1 week – 1 month | > 1 month |
| Change Failure Rate | 0–5% | 5–15% | 16–30% | > 30% |
| MTTR | < 1 hour | < 1 day | 1 day – 1 week | > 1 week |

**THE TRADE-OFFS:**
**Gain:** Research-validated, industry-benchmarkable metrics; creates shared language for engineering performance; aligns engineering investment with measurable outcomes.
**Cost:** Measurement requires instrumented deployment pipelines and incident management integration. Teams can game metrics (e.g., deploying trivial changes to inflate deployment frequency). Requires honest, consistent measurement discipline.

---

### 🧪 Thought Experiment

**SETUP:**
An engineering director manages two teams. Team A has been practicing continuous delivery for 2 years. Team B uses traditional sprint-based development with monthly releases. Compare via DORA.

**TEAM A MEASUREMENT:**
- Deployment Frequency: 8 deploys/day → **Elite**
- Lead Time: 25 minutes → **Elite**
- Change Failure Rate: 3% → **Elite**
- MTTR: 18 minutes → **Elite**
- Result: Elite performer across all 4 metrics

**TEAM B MEASUREMENT:**
- Deployment Frequency: 1/month → **Medium**
- Lead Time: 3 weeks → **Medium**
- Change Failure Rate: 22% → **Medium**
- MTTR: 36 hours → **Medium**
- Result: Medium performer across all 4 metrics

**THE INSIGHT:**
Team B's monthly releases are not conservative — they're creating risk. Each monthly deployment is a large batch with high CFR (22%). Team A's daily deployments are safer per-deployment (3% CFR) AND deliver value faster. This is the DORA finding in action: Team B's caution creates more problems than it prevents. The path to Team A's performance is more automation and smaller changes, not more caution.

---

### 🧠 Mental Model / Analogy

> The DORA four metrics are like a car's four key dashboard indicators: speedometer (deployment frequency), odometer reading per hour (lead time), check engine light frequency (change failure rate), and time in the repair shop (MTTR). A car that's fast but constantly breaking down is not a high-performance car. A car that never breaks down but only goes 20mph isn't either. A truly high-performing car is fast AND reliable — and that's exactly what DORA proves about elite engineering teams.

- "Speedometer" → deployment frequency (how fast you're going)
- "Distance per hour" → lead time (efficiency per unit time)
- "Check engine light frequency" → change failure rate (reliability)
- "Time in repair shop" → MTTR (recovery speed when it breaks)

Where this analogy breaks down: a car's speed and reliability are genuinely in trade-off at the extreme (race cars break more). DORA's research shows this trade-off doesn't hold for software delivery at typical organisational scales — the practices that enable high frequency also improve reliability.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
DORA metrics are four measurements that tell you how good your software delivery is: how often you deploy, how fast, how often you break things, and how fast you fix them. Researchers studied thousands of teams over years and proved that the best teams score well on all four — and those teams also tend to have more successful businesses.

**Level 2 — How to use it (junior developer):**
Start measuring all four DORA metrics today. Use your CD platform (GitHub Deployments, GitLab, Jenkins) to track deployment events. Use your incident management tool (PagerDuty, Opsgenie) to track incident start/end times and correlate with deployments. Calculate each metric monthly. Identify which DORA band you're in. Find the lowest-performing metric — it's your highest-leverage improvement opportunity. Tools like LinearB, Sleuth, DORA4, and Google Cloud Deploy automate DORA metric collection.

**Level 3 — How it works (mid-level engineer):**
Precise DORA measurement requires: (1) deployment events with timestamp, service, environment, and success/failure status from the CD pipeline; (2) incident events with start time, end time, link to causative deployment; (3) commit timestamps from VCS. The four metrics are then: Frequency = count(successful prod deploys) / time; Lead time = mean(deploy_time - commit_time) for production deploys; CFR = count(failed deploys) / count(all deploys) × 100; MTTR = mean(incident_end - incident_start). Baseline first month before trying to improve — without a baseline, improvement is unmeasurable.

**Level 4 — Why it was designed this way (senior/staff):**
The DORA research methodology is Structural Equation Modelling (SEM) — a statistical technique that identifies latent constructs and causal relationships in survey data. The research started as a state of DevOps survey (Puppet, 2013) and evolved into a rigorous longitudinal study (DORA + Google from 2018). The research found that delivery performance (DORA four metrics) mediates between technical practices (CI/CD, trunk-based development, architecture) and business outcomes (profitability, market share, employee satisfaction). The causal chain: better technical practices → better DORA metrics → better business outcomes. This gives engineering leaders a research-backed argument for platform investment. The 2023 DORA report added a fifth metric (reliability/SLO adherence) and found a new finding: documentation quality as a predictor of performance — teams with good technical documentation outperform those without, even controlling for other factors.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│  DORA METRICS MEASUREMENT ARCHITECTURE      │
├─────────────────────────────────────────────┤
│                                             │
│  DATA SOURCES:                              │
│  VCS (GitHub/GitLab): commit timestamps    │
│  CD Platform: deployment events + status   │
│  Incident Mgmt (PagerDuty): P1-P3 events   │
│                                             │
│  METRIC CALCULATION:                        │
│                                             │
│  Deployment Frequency:                      │
│  = count(prod deploys, status=success)      │
│    / days in period                         │
│                                             │
│  Lead Time:                                 │
│  = mean(deploy_timestamp - commit_timestamp)│
│     for each successful prod deploy         │
│                                             │
│  Change Failure Rate:                       │
│  = count(deploys causing incident)          │
│    / count(total prod deploys) × 100        │
│                                             │
│  MTTR:                                      │
│  = mean(incident_resolved - incident_start) │
│     for each production incident            │
│                                             │
│  TOOLING:                                   │
│  Manual: spreadsheet + CD logs + PagerDuty │
│  Automated: LinearB, Sleuth, DORA4,         │
│    Google Cloud Deploy, Harness             │
└─────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Month 1: Team establishes baseline
  → Deploy events collected: 8/month (Medium band)
  → Lead time calculated: 2 weeks (Medium band)
  → CFR measured: 18% (Medium band)
  → MTTR measured: 4 hours (Medium band)
  → Baseline established [← YOU ARE HERE]
  → Root cause analysis: longest lead time bottleneck
    = weekly deployment windows (50hrs wait time)
  → Month 2 investment: eliminate deployment window
  → Month 2 result: lead time → 2 hours (High band)
  → Month 3: same frequency, better lead time
  → (Frequency unchanged — next bottleneck to tackle)
```

**FAILURE PATH:**
```
Team begins gaming metrics:
  → Deploy Dependabot auto-merge PRs separately
  → Deployment frequency: 45/month (Elite!)
  → Lead time: 15 min (Elite!)
  → But: CFR rises to 25% (bad — real code quality worsening)
  → MTTR: 6 hours (bad — no observability investment)
  → DORA reveals: speed metrics gamed, quality falls
  → Engineering director: "Why is CFR going up?"
  → System works as designed — gaming is visible
```

**WHAT CHANGES AT SCALE:**
At 1000+ engineers, per-team DORA metrics enable portfolio analysis: which teams are elite, which are low, and what patterns distinguish them. Platform engineering teams build "DORA measurement as a service" — instruments automatically generate metrics from all pipelines. DORA benchmarks are included in engineering all-hands to show org-level trend. Individual team DORA band is discussed in engineering manager performance reviews.

---

### 💻 Code Example

**Example 1 — DORA metrics dashboard (GitHub + PagerDuty):**
```python
# dora_calculator.py
from datetime import datetime, timedelta
import requests

class DoraCalculator:
    def __init__(self, github_token, pd_token, repo):
        self.gh_headers = {"Authorization": f"token {github_token}"}
        self.pd_headers = {"Authorization": f"Token {pd_token}"}
        self.repo = repo
        self.since = (datetime.now() -
                      timedelta(days=30)).isoformat()

    def deployment_frequency(self):
        """Successful prod deploys per day (30-day window)"""
        resp = requests.get(
            f"https://api.github.com/repos/{self.repo}/deployments",
            headers=self.gh_headers,
            params={"environment": "production",
                    "per_page": 100}
        )
        deploys = [d for d in resp.json()
                   if d["created_at"] > self.since]
        return len(deploys) / 30  # per day

    def lead_time_hours(self):
        """Mean commit-to-deploy time in hours"""
        lead_times = []
        resp = requests.get(
            f"https://api.github.com/repos/{self.repo}/deployments",
            headers=self.gh_headers,
            params={"environment": "production"}
        )
        for deploy in resp.json()[:20]:
            sha = deploy["sha"]
            # Get commit timestamp
            commit_resp = requests.get(
                f"https://api.github.com/repos/{self.repo}/commits/{sha}",
                headers=self.gh_headers
            )
            commit_time = commit_resp.json()["commit"]["committer"]["date"]
            deploy_time = deploy["created_at"]

            t0 = datetime.fromisoformat(commit_time.replace("Z", "+00:00"))
            t1 = datetime.fromisoformat(deploy_time.replace("Z", "+00:00"))
            lead_times.append((t1 - t0).total_seconds() / 3600)

        return sum(lead_times) / len(lead_times) if lead_times else 0

    def band_classification(self):
        freq = self.deployment_frequency()
        lt = self.lead_time_hours()

        freq_band = ("Elite" if freq > 1 else
                     "High" if freq >= 1/7 else
                     "Medium" if freq >= 1/30 else "Low")
        lt_band = ("Elite" if lt < 1 else
                   "High" if lt < 24 * 7 else
                   "Medium" if lt < 24 * 30 else "Low")

        return {
            "deployment_frequency": f"{freq:.2f}/day ({freq_band})",
            "lead_time": f"{lt:.1f}h ({lt_band})"
        }
```

---

### ⚖️ Comparison Table

| Framework | Metrics | Research-backed | Business Link | Benchmarks |
|---|---|---|---|---|
| **DORA** | 4 (+ reliability) | Yes (32k respondents) | Proven | Yes (bands) |
| SPACE | 5 (satisfaction, performance, activity, communication, efficiency) | Moderate | Partial | No |
| Flow Metrics | 4 (velocity, time, load, efficiency) | Moderate | Partial | No |
| OKRs | Custom | No | Yes (goals) | No |
| Story Points | 1 (velocity) | No | No | No |

How to choose: Use **DORA Metrics** as the primary engineering delivery performance framework — it's the only one backed by years of research linking metrics to business outcomes. Use **SPACE** as a complementary framework for developer satisfaction and well-being dimensions that DORA doesn't cover. Use **Flow Metrics** at the product management/value stream level to understand feature delivery throughput.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| DORA metrics are only for large organisations | DORA research includes teams as small as 5 people. The metrics scale to any team size. Small teams benefit as much from measurement and improvement as large ones. |
| Higher deployment frequency always means better | Frequency must be paired with CFR. A team deploying 100x/day with 30% CFR has 30 incidents/day — that's worse than a team with 70%/day lower quality performance. Always track all four metrics together. |
| DORA metrics are objective and can't be gamed | All metrics can be gamed. Deployment frequency inflated by trivial commits; CFR understated by narrow failure definitions; MTTR shortened by declaring incidents resolved before verification. Governance and honest definition are required. |
| Your team's DORA band is permanent | DORA bands are a starting point for improvement, not a permanent label. The research shows teams can move from Low to High in 1–2 years with targeted investment in automation, testing, and CI/CD pipeline optimisation. |

---

### 🚨 Failure Modes & Diagnosis

**1. DORA Metrics Gamed by Incentive Misalignment**

**Symptom:** Deployment frequency shows 50 deploys/month (Elite). Lead time: 8 minutes (Elite). But CFR rose from 8% to 28% over the same period. Metric dashboard looks like Elite but users are suffering.

**Root Cause:** Team rewarded for frequency and lead time metrics without equal weight on CFR. Engineers learned that small, trivial deploys (documentation updates, comment changes, dependency bumps) inflate frequency without quality risk. Meanwhile, real feature code is rushed to maintain pace — leading to higher CFR.

**Diagnostic:**
```bash
# Analyse deployment content by type
git log main --oneline --since="30 days ago" | \
  head -50 | \
  while read sha msg; do
    files=$(git diff-tree --no-commit-id -r \
      --name-only $sha | wc -l)
    echo "$sha: $files files - $msg"
  done | sort -k2 -n -r
# High frequency of 1-2 file changes = gaming
```

**Fix:** Measure all four DORA metrics with equal weight. Report CFR and MTTR alongside frequency in all leadership reviews. Consider segmenting "feature deployments" vs "dependency/infrastructure deployments" to make superficial gaming visible.

**Prevention:** Include CFR trend in any discussion of deployment frequency improvement. Set a rule: CFR cannot worsen while frequency improves — if it does, investigate.

---

**2. Measurement Stops After Initial Baseline**

**Symptom:** Team measured DORA metrics for 2 months, established baseline, then stopped measuring. 6 months later, nobody knows whether the investments made (CI optimisation, observability tooling) improved performance.

**Root Cause:** DORA measurement treated as a one-time diagnostic rather than ongoing operational metric. No tooling automation — measurement required manual effort that was deprioritised.

**Diagnostic:**
```bash
# Check last DORA report date
ls -la dora-reports/
# If last file > 2 months old → measurement has lapsed

# Check CD pipeline for deployment event recording
# If events not recorded consistently → measurement gaps
```

**Fix:** Automate DORA measurement. Use LinearB, Sleuth, DORA4, or write a script that runs monthly and emails the report. Include in monthly engineering all-hands as a standing agenda item. Treat DORA metrics with the same status as customer SLOs.

**Prevention:** Automate everything that can be automated. Manual-only metrics get deprioritised. Put DORA metric review on the monthly engineering leadership calendar from day 1.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Deployment Frequency` — the first DORA metric; must understand before using the full framework
- `Lead Time for Changes` — the second DORA metric
- `Change Failure Rate` — the third DORA metric
- `MTTR` — the fourth DORA metric

**Builds On This (learn these next):**
- `Progressive Delivery` — the technical practice most directly improving both frequency and CFR simultaneously
- `Platform Engineering` — builds the internal tooling that makes Elite DORA metrics achievable at scale
- `SRE (Site Reliability Engineering)` — the organisational model that optimises for CFR and MTTR specifically

**Alternatives / Comparisons:**
- `SPACE Metrics` — extends DORA with developer satisfaction, activity, and communication dimensions
- `Flow Metrics` — product-level throughput metrics (feature velocity) that complement DORA's delivery pipeline focus
- `OKRs` — goal-setting framework; DORA metrics can be used as key results in engineering OKRs

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ 4 research-validated metrics (freq, lead  │
│              │ time, CFR, MTTR) predicting org outcomes  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Engineering performance measured by proxy │
│ SOLVES       │ metrics (velocity) with no business link  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Speed and stability are NOT in trade-off: │
│              │ elite teams excel at all 4 simultaneously │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — establish baseline before any    │
│              │ improvement investment                    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never skip — but track all 4 together;    │
│              │ gaming one metric at expense of others    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Research-validated insight vs measurement │
│              │ effort and potential for metric gaming    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Four vital signs for engineering health  │
│              │  — validated on 32,000 practitioners."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Progressive Delivery → Platform Eng →     │
│              │ SRE → SPACE Metrics → Accelerate book     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An engineering VP presents to the board: "We are now an Elite DORA performer on all four metrics." The board asks: "Does this mean our engineering team is actually delivering better business results?" What is the precise chain of causality in the DORA research connecting technical practices → DORA metric performance → organisational outcomes, and what are the conditions under which Elite DORA performance does NOT translate to better business outcomes?

**Q2.** The DORA research found that elite performers excel at ALL four metrics simultaneously. A team is Elite on deployment frequency and lead time (speed dimension) but Medium on CFR and MTTR (stability dimension). A consultant proposes: "You should slow down deployments (lower frequency, increase lead time) to allow more testing time and improve stability." Using DORA's research findings, critique this advice: what does the research say about the relationship between deployment pace and stability, and what would the research-supported intervention actually be?

