---
layout: default
title: "MTTR / MTBF"
parent: "System Design"
nav_order: 692
permalink: /system-design/mttr-mtbf/
number: "692"
category: System Design
difficulty: ★★☆
depends_on: "SLA / SLO / SLI, Observability"
used_by: "Disaster Recovery, RTO / RPO"
tags: #intermediate, #reliability, #observability, #architecture, #foundational
---

# 692 — MTTR / MTBF

`#intermediate` `#reliability` `#observability` `#architecture` `#foundational`

⚡ TL;DR — **MTBF** measures how long a system runs between failures (longer = more reliable); **MTTR** measures how fast you recover from failure (shorter = more resilient). High MTBF + low MTTR = highly available system.

| #692            | Category: System Design        | Difficulty: ★★☆ |
| :-------------- | :----------------------------- | :-------------- |
| **Depends on:** | SLA / SLO / SLI, Observability |                 |
| **Used by:**    | Disaster Recovery, RTO / RPO   |                 |

---

### 📘 Textbook Definition

**Mean Time Between Failures (MTBF)** is the average time between recoverable failures of a system or component, calculated as `MTBF = (total operational time) / (number of failures)`. A higher MTBF indicates greater reliability. **Mean Time To Recovery (MTTR)** is the average time required to restore a system to full operational status after a failure, calculated as `MTTR = (total downtime) / (number of failures)`. A lower MTTR indicates greater resilience. Together, these metrics define **availability**: `Availability = MTBF / (MTBF + MTTR)`. For example, MTBF=720 hours and MTTR=1 hour gives availability of 99.86%. Related metrics: **MTTD** (Mean Time To Detect — how long before failure is noticed), **MTTF** (Mean Time To Failure — for non-repairable items), **MTTS** (Mean Time To Stabilise). These metrics form the quantitative foundation of SRE incident management and reliability engineering.

---

### 🟢 Simple Definition (Easy)

MTBF: "On average, our system breaks every X hours." MTTR: "On average, we fix it in Y minutes." Higher MTBF = breaks less often. Lower MTTR = fixed faster. Both together define how available your system is to users.

---

### 🔵 Simple Definition (Elaborated)

A service had 5 incidents in the past year. Total operational time: 8,700 hours. Total downtime: 60 hours. MTBF = 8,700 / 5 = 1,740 hours between failures. MTTR = 60 / 5 = 12 hours per incident (very slow recovery). Availability = 1740 / (1740 + 12) = 99.3%. Two improvement strategies: raise MTBF (fewer failures — better reliability through redundancy, testing) and lower MTTR (faster recovery — better tooling, runbooks, automation). Usually MTTR is easier and faster to improve.

---

### 🔩 First Principles Explanation

**MTBF vs MTTR — which to improve?**

```
AVAILABILITY FORMULA:
  Availability = MTBF / (MTBF + MTTR)

SCENARIO A: High MTBF, High MTTR (reliable but slow to recover)
  MTBF = 1000 hours (fails once every ~42 days)
  MTTR = 8 hours (8-hour recovery per incident)
  Availability = 1000 / (1000 + 8) = 99.2%

SCENARIO B: Lower MTBF, Low MTTR (fails more often but recovers fast)
  MTBF = 100 hours (fails every ~4 days — 10x more fragile)
  MTTR = 0.1 hour (6 minutes to recover — automated)
  Availability = 100 / (100 + 0.1) = 99.9%

  COUNTERINTUITIVE: System B fails 10x more often but is MORE available.
  Low MTTR dominates the availability calculation.
  SRE insight: invest in fast recovery, not just failure prevention.

MTTD (Mean Time To Detect) — the invisible contributor to MTTR:

  MTTR = MTTD + MTTI (Mean Time To Isolate) + MTTF (Mean Time To Fix)
       + MTTV (Mean Time To Verify)

  If MTTD = 2 hours (failure undetected for 2 hours):
  Even if fix takes 5 minutes, MTTR = 125 minutes.

  Improving MTTD:
  - Better monitoring and alerting (PagerDuty, SLO burn rate alerts)
  - Synthetic monitoring (detects issues before users report them)
  - Error budget burn rate alerts (detects degradation early)

  Improving MTTI (isolation):
  - Distributed tracing (Jaeger, Zipkin) → find root cause quickly
  - Service dashboards with drill-down capability
  - Runbooks for common failure modes

  Improving MTTF (fix):
  - Automated remediation (restart service, scale out, roll back)
  - Feature flags (disable bad feature in 30 seconds)
  - Blue-green deployments (rollback in 60 seconds vs. 30-minute rollback)

  Improving MTTV (verification):
  - Automated smoke tests post-deployment/recovery
  - Synthetic probes confirming user-facing functionality

RELIABILITY vs. RESILIENCE:

  RELIABILITY (high MTBF): build systems that DON'T fail
  - Redundant hardware, better testing, circuit breakers
  - Diminishing returns: going from 3 nines to 4 nines is expensive

  RESILIENCE (low MTTR): build systems that RECOVER FAST
  - Automated rollback, chaos engineering, runbooks
  - Often cheaper and more effective than chasing perfect reliability

  Google SRE philosophy: "Hope is not a strategy.
  Build for failure; reduce MTTR to near-zero."

  Example: Netflix Chaos Monkey
  - Deliberately kills random production services
  - Forces teams to build fast self-healing (low MTTR)
  - MTBF actually decreases (more failures)
  - MTTR decreases dramatically (teams build auto-recovery)
  - Net result: higher availability despite more frequent failures
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT MTBF/MTTR metrics:

- Reliability is subjective: "we had some outages this quarter"
- No baseline: can't measure improvement over time
- Prioritisation unclear: should we invest in prevention or recovery?

WITH MTBF/MTTR:
→ Quantified reliability: "MTBF dropped 40% this quarter → reliability degraded"
→ Targeted improvement: "MTTR=4 hours is the bottleneck → automate recovery"
→ SLA calculation: availability = f(MTBF, MTTR) → know if SLA is achievable

---

### 🧠 Mental Model / Analogy

> Car reliability statistics. MTBF = how many miles the car goes between breakdowns on average. MTTR = how long it sits at the mechanic after a breakdown. A car that breaks down every 50,000 miles but is fixed in 2 hours is MORE available for daily driving than a car that breaks down every 100,000 miles but requires a 3-week parts order. Reliability (MTBF) matters, but recovery speed (MTTR) matters too — and is often easier to improve.

"Miles between breakdowns" = MTBF (time between failures)
"Time at the mechanic" = MTTR (recovery time)
"Car availability for daily use" = system availability = MTBF/(MTBF+MTTR)
"Pre-ordering common spare parts" = runbooks and automation (reduce MTTR)

---

### ⚙️ How It Works (Mechanism)

**Calculating MTBF and MTTR from incident data:**

```python
from datetime import datetime, timedelta

incidents = [
    {"start": datetime(2024, 1, 5, 14, 0), "end": datetime(2024, 1, 5, 16, 30)},  # 2.5h
    {"start": datetime(2024, 2, 12, 3, 0), "end": datetime(2024, 2, 12, 4, 0)},   # 1h
    {"start": datetime(2024, 3, 20, 9, 0), "end": datetime(2024, 3, 20, 9, 15)},  # 15m
    {"start": datetime(2024, 4, 8, 18, 0), "end": datetime(2024, 4, 8, 21, 0)},   # 3h
    {"start": datetime(2024, 5, 1, 11, 0), "end": datetime(2024, 5, 1, 11, 20)},  # 20m
]

total_window = timedelta(days=150)  # 5-month tracking window
total_downtime = sum(
    (i["end"] - i["start"]).total_seconds() / 3600
    for i in incidents
)  # in hours
n = len(incidents)
total_operational = total_window.total_seconds() / 3600 - total_downtime

mtbf = total_operational / n          # hours between failures
mttr = total_downtime / n             # hours to recover
availability = mtbf / (mtbf + mttr)

print(f"MTBF: {mtbf:.1f} hours ({mtbf/24:.1f} days between failures)")
print(f"MTTR: {mttr:.2f} hours ({mttr*60:.0f} min avg recovery)")
print(f"Availability: {availability*100:.3f}%")
# MTBF: 713.4 hours (29.7 days between failures)
# MTTR: 1.41 hours (85 min avg recovery)
# Availability: 99.803%
```

---

### 🔄 How It Connects (Mini-Map)

```
SLA / SLO / SLI
(reliability targets)
        │
        ▼ (quantify underlying reliability)
MTBF / MTTR ◄──── (you are here)
(measure reliability + recovery speed)
        │
        ├── RTO / RPO (disaster recovery time targets — similar concept)
        ├── Disaster Recovery (MTTR for catastrophic failures)
        └── Observability (monitoring provides the data to calculate MTTR/MTBF)
```

---

### 💻 Code Example

**PagerDuty API: calculating MTTR from incident data:**

```bash
# Query PagerDuty API for incident history (last 90 days)
curl -X GET \
  "https://api.pagerduty.com/incidents?since=2024-01-01&until=2024-04-01&statuses[]=resolved&limit=100" \
  -H "Authorization: Token token=YOUR_API_KEY" \
  -H "Accept: application/json" \
  | jq '[.incidents[] | {
      id: .id,
      created: .created_at,
      resolved: .resolved_at,
      duration_hours: ((.resolved_at | fromdateiso8601) - (.created_at | fromdateiso8601)) / 3600
    }]'

# Sum duration / count = MTTR
# Sort by duration to identify outlier incidents (ones that blew up MTTR)
```

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                                                                                                                     |
| ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MTBF is the most important availability metric    | MTTR often matters more and is easier to improve. A system that fails 10x more often but recovers in seconds can have higher availability than a reliable system with slow recovery. Prioritise MTTR reduction first — it has faster ROI                    |
| MTTR starts when the fix is deployed              | MTTR = total time from failure onset to full recovery, including: detection time (MTTD), diagnosis time, fix implementation, deployment, and verification. Detection time is often the largest component in practice and the most overlooked                |
| High MTBF means your system is production-ready   | MTBF measures historical failure frequency, not severity. A system with high MTBF might fail rarely but catastrophically (full data loss, unrecoverable state). MTBF + MTTR together with severity categorisation give a full picture                       |
| 99.9% availability = 8.76 hours downtime per year | This calculates unplanned downtime only. Planned maintenance windows (deployments, database migrations) also reduce availability. A system with 99.9% unplanned availability but 48 hours of planned downtime annually has effective availability of ~99.4% |

---

### 🔥 Pitfalls in Production

**MTTD (detection time) is often the biggest MTTR contributor:**

```
INCIDENT TIMELINE (real-world pattern):

  T+00:00  Failure occurs: database connection pool exhausted
  T+00:45  First user reports: "I can't log in" (Zendesk ticket)
  T+01:30  Support escalates to on-call
  T+01:35  On-call engineer paged
  T+01:55  Engineer investigates
  T+02:30  Root cause identified: connection pool exhaustion
  T+02:45  Fix deployed: pool size increased
  T+02:50  Verification: logins working

  MTTR: 2 hours 50 minutes
  Of which: MTTD = 1 hour 35 minutes (56% of total MTTR!)
  Actual fix time: 15 minutes

  PROBLEM: The failure was detectable at T+00:00 from metrics:
    db_connection_pool_exhausted counter spiked
    API error rate hit 100%
    HTTP 500s spiked in logs
    → All of this was measurable but no alert fired

FIX: Alert on SLO burn rate (detects failure within 2-5 minutes):

  # Prometheus: multi-window burn rate alert
  - alert: AvailabilitySLOBurnRateHigh
    expr: |
      (
        job:sli_availability:ratio_rate1h < (1 - 14.4 * (1-0.999))
      ) and (
        job:sli_availability:ratio_rate5m < (1 - 14.4 * (1-0.999))
      )
    labels:
      severity: critical
    annotations:
      summary: "High error burn rate — SLO breach imminent in <1 hour"

  # 14.4x burn rate = SLO breach in 1/14.4 of 28 days = ~46 hours
  # Multi-window: both 1h and 5m must confirm → reduces false positives

  Result: alert fires at T+00:05 → MTTD drops from 95 min to 5 min
          MTTR: 2h50m → ~25 minutes (90% reduction)
```

---

### 🔗 Related Keywords

- `SLA / SLO / SLI` — availability is derived from MTBF and MTTR; SLOs set targets for both
- `RTO / RPO` — disaster recovery variants of MTTR (Recovery Time Objective = target MTTR)
- `Observability` — monitoring + alerting enables the detection phase (reducing MTTD)
- `Disaster Recovery` — large-scale MTTR scenarios; DR plan is the MTTR playbook
- `Error Budget` — MTBF and MTTR feed into error budget calculations

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ MTBF = time between failures (reliability)│
│              │ MTTR = recovery time (resilience)         │
│              │ Availability = MTBF / (MTBF + MTTR)       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Measuring and improving service reliability│
│              │ SLO calibration; incident retrospectives  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Using MTBF alone without MTTR — high MTBF │
│              │ + slow MTTR = poor actual availability    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A car that breaks down often but is fixed │
│              │  in minutes beats one that's rarely fixed │
│              │  but takes weeks to repair."              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ RTO / RPO → Disaster Recovery             │
│              │ → SLO Error Budget                        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your service has MTBF=2,160 hours (90 days) and MTTR=4 hours. Your SLO target is 99.9% availability. Calculate the current availability. Is the SLO met? Now calculate: (a) how much would MTBF need to increase (MTTR unchanged) to meet 99.9%? (b) how much would MTTR need to decrease (MTBF unchanged) to meet 99.9%? Which improvement is more achievable, and why?

**Q2.** After analysing 12 months of incident data, your team finds: average MTTD = 45 minutes, average MTTI = 30 minutes, average MTTF = 20 minutes, average MTTV = 10 minutes. Total MTTR = 105 minutes. You have budget to implement ONE of the following improvements: (a) automated alerting on SLO burn rate (reduces MTTD to 5 minutes), (b) distributed tracing deployment (reduces MTTI to 5 minutes), (c) one-click rollback pipeline (reduces MTTF to 3 minutes). Rank these by impact on MTTR and overall availability, then identify which you would implement first.
