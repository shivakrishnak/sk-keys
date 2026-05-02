---
layout: default
title: "Mean Time to Recovery (MTTR)"
parent: "CI/CD"
nav_order: 1026
permalink: /ci-cd/mean-time-to-recovery/
number: "1026"
category: CI/CD
difficulty: ★★★
depends_on: DORA Metrics, Change Failure Rate, Rollback Strategy, Observability
used_by: DORA Metrics, SRE, Incident Management
related: Change Failure Rate, DORA Metrics, Deployment Frequency, SLO
tags:
  - cicd
  - devops
  - deep-dive
  - metrics
  - reliability
---

# 1026 — Mean Time to Recovery (MTTR)

⚡ TL;DR — MTTR measures how long it takes to restore service after a production failure, and reducing it requires making detection fast, rollback instant, and incident response practiced.

| #1026 | Category: CI/CD | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DORA Metrics, Change Failure Rate, Rollback Strategy, Observability | |
| **Used by:** | DORA Metrics, SRE, Incident Management | |
| **Related:** | Change Failure Rate, DORA Metrics, Deployment Frequency, SLO | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A production outage starts at 2:14am. The alert fires at 2:38am (monitoring threshold too conservative). An on-call engineer sees it at 2:52am (phone on silent). They investigate until 3:41am, form a hypothesis, roll back until 4:15am, verify recovery by 4:30am. Total: 2 hours 16 minutes of user impact. No one was tracking MTTR. No one knows this is happening every 3 weeks. No impetus to improve.

**THE BREAKING POINT:**
Without measuring recovery time, there is no accountability for how long users endure degraded service, no baseline to improve from, and no mechanism to identify the specific bottlenecks (detection latency? investigation time? rollback speed?) that extend the duration of user impact. Every outage is treated as a unique, unavoidable event rather than a systematic process with improvable components.

**THE INVENTION MOMENT:**
This is exactly why MTTR exists as a DORA metric: make recovery time visible, measure it systematically, and enable data-driven investment in the specific capabilities — monitoring, automation, runbooks, rollback — that reduce service degradation duration.

---

### 📘 Textbook Definition

**Mean Time to Recovery (MTTR)** is a DORA metric measuring the average time to restore service after a production failure — typically calculated as the mean duration from the moment a production incident begins (first user impact or alert) to the moment full service is restored. DORA bands: **Elite** (< 1 hour), **High** (< 1 day), **Medium** (1 day to 1 week), **Low** (> 1 week). MTTR is the resilience/recovery dimension of DORA, complementing change failure rate (frequency of failures). MTTR has components: **detection time** (time from failure start to alert), **triage time** (time to identify root cause), **restoration time** (time to execute rollback or fix). Elite MTTR requires fast detection (monitoring, SLOs), fast diagnosis (distributed tracing, structured logging), and fast restoration (automated rollback, feature flags, tested runbooks).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
How long your users suffer when something breaks — the metric that makes incident response speed visible.

**One analogy:**
> MTTR is the emergency department's "door-to-discharge" time. A hospital that keeps ER patients waiting 8 hours has poor MTTR. One that discharges patients in 2 hours has excellent MTTR. Achieving fast MTTR requires pre-positioned resources (monitoring = nurses at the door), fast diagnostic tools (lab results in 30 min, not 3 hours), and practiced procedures (doctors know the protocol — no time spent deciding at 3am).

**One insight:**
MTTR is dominated by the weakest link in the recovery chain. Improving any one component without addressing the actual slowest component has minimal impact. If detection takes 90 minutes and the rollback takes 2 minutes, speeding up the rollback from 2 minutes to 30 seconds doesn't matter. The bottleneck is detection. MTTR improvement requires value stream mapping of the recovery process.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Failures in production are inevitable — the goal is to minimise their duration and user impact, not to eliminate them (which is impossible).
2. MTTR = detection time + triage time + restoration time; improving MTTR requires addressing each component's bottleneck separately.
3. Fast MTTR requires preparation before the incident — monitoring, runbooks, practiced response, automated rollback.

**DERIVED DESIGN:**
MTTR components and their primary levers:

**Detection time** → SLO-based alerting with low latency. Alert when error budget burn rate exceeds threshold, not on arbitrary absolute thresholds. Response: 4 hours of error budget consumed in 5 minutes = Critical alert. With proper SLO alerts, detection time can be < 2 minutes.

**Triage/diagnosis time** → Distributed tracing (Jaeger, Tempo), structured logging, and correlation dashboards. The engineer should be able to trace a failed request from user → service → database within 5 minutes of starting investigation. Without observability, triage takes hours.

**Restoration time** → Automated rollback (if change-caused: rollback to last good version in < 5 minutes), feature flag disable (instant, no deployment needed), runbooks (documented, tested procedures that eliminate 3am decision-making uncertainty).

**THE TRADE-OFFS:**
**Gain:** Quantified accountability for user impact duration; identifies specific recovery bottlenecks; creates incentive to invest in monitoring, runbooks, and automated rollback.
**Cost:** Requires a precise "incident start" and "incident end" definition. Long debates about when impact started inflate or deflate MTTR artificially. Requires investment in observability tooling to drive detection and triage time down.

---

### 🧪 Thought Experiment

**SETUP:**
Same production failure (database connection pool exhaustion) happens in two different organisations. Compare their MTTR.

**ORGANISATION A (Poor MTTR — 4 hours):**
Failure starts 2am. Generic "service unavailable" alert fires at 3am (60 min detection — alert threshold too high). On-call pages at 3am. Engineer logs in, sees "503 errors," has no tracing, checks logs manually on 3 different services. Identifies root cause at 4am. Restores by increasing pool size manually at 5am. Verifies at 5:30am. MTTR: 3.5 hours.

**ORGANISATION B (Elite MTTR — 28 minutes):**
Failure starts 2am. SLO alerting fires at 2:03am (burn rate spike — 3 min detection). On-call auto-paged. Engineer opens trace dashboard — sees DB connection pool saturation immediately (5 min triage). Runbook: "connection pool exhaustion → scale pool or rollback recent migration." Last deploy was a migration. Feature flag disabled for migration (2 min by flipping flag). Service recovers. Postmortem scheduled. MTTR: 28 minutes.

**THE INSIGHT:**
The same failure, the same root cause, but 7x difference in MTTR. The difference is infrastructure investment: SLO alerting, distributed tracing, feature flags, and a tested runbook. MTTR is a choice — not a luck-of-the-draw.

---

### 🧠 Mental Model / Analogy

> MTTR is like a fire department's response benchmark. Fire departments track "turnout time" (time from alarm to truck rolling) and "travel time" (truck-to-scene). They practice, they pre-position equipment, they drill constantly — not because they can predict fires, but because they know the time-critical variables. Great engineering incident response is identical: you can't predict when the fire starts, but you can pre-position your "fire equipment" (monitoring, runbooks, automated rollback) and practice the response so the 3am response is automatic, not improvisational.

- "Fire alarm" → alerting system (SLOs, error rate thresholds)
- "Turnout time" → detection-to-engineer-engaged time
- "Travel time" → triage time
- "Extinguishing the fire" → rollback / fix deployment
- "Pre-positioned equipment" → runbooks, automated rollback, feature flags
- "Fire drill" → chaos engineering, gameday exercises

Where this analogy breaks down: fire departments fight the same types of fires repeatedly. Software incidents are often unique. This is why runbooks cover categories (database issues, deployment failures) rather than exact scenarios — the checklist guides the investigation, not the solution.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
MTTR measures how quickly a team gets their service back to normal after something breaks. If your app goes down and you fix it in 20 minutes, your MTTR for that incident is 20 minutes. Teams with low MTTR have good monitoring (they know something is wrong fast) and good tools (they can fix it fast).

**Level 2 — How to use it (junior developer):**
Record MTTR for every production incident: start time (when users were affected or alert fired), end time (when service was confirmed restored). Calculate mean over 30 days. Track trends. Identify which incidents took longest and why. Common investments to reduce MTTR: (1) improve alerting sensitivity (SLO-based > threshold-based), (2) create runbooks for top 5 incident types, (3) ensure rollback can be executed in < 5 minutes without engineer judgment. Aim for Elite band: < 1 hour.

**Level 3 — How it works (mid-level engineer):**
MTTR has sub-components that can be measured independently: MTTD (mean time to detect), MTTI (mean time to identify root cause), MTTF (mean time to fix). Observability is the primary lever: distributed tracing (Jaeger, Zipkin, Tempo) connects request traces across services. Structured logging enables log aggregation queries. Metrics (Prometheus, Datadog) enable dashboards that reveal normal vs abnormal. SLO burn rate alerting fires faster than absolute thresholds because it detects sustained degradation even below hard failure rates. Feature flags enable < 30-second restoration without a deployment — the ultimate MTTR improvement for change-caused failures.

**Level 4 — Why it was designed this way (senior/staff):**
DORA's research initially focused on speed (deployment frequency, lead time). The addition of CFR and MTTR created a two-dimensional (speed × resilience) framework — high performers excel at all four dimensions simultaneously. MTTR is the resilience metric most directly actionable by engineering investment: monitoring tooling, on-call process design, runbook maintenance, and automated rollback. SRE (Site Reliability Engineering) formalised MTTR improvement as a discipline: the "error budget" model puts MTTR costs in business terms — 4 hours of outage × 1M active users × estimated revenue per user-hour = incident cost. This framing justifies observability investment in business terms.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│  MTTR COMPONENTS                            │
├─────────────────────────────────────────────┤
│                                             │
│  INCIDENT TIMELINE:                         │
│                                             │
│  T0: Failure starts (user impact begins)   │
│  │                                         │
│  ├── DETECTION (T0→T1)                     │
│  │   Alert fires: SLO burn rate exceeds    │
│  │   threshold → PagerDuty → on-call       │
│  │   Elite: < 2 min                        │
│  │   Poor: > 30 min (threshold too high)   │
│  │                                         │
│  T1: Engineer engaged                       │
│  │                                         │
│  ├── TRIAGE (T1→T2)                        │
│  │   Review metrics → traces → logs        │
│  │   Identify: what failed, how badly,     │
│  │   what caused it                        │
│  │   Elite: < 5 min (good observability)  │
│  │   Poor: > 60 min (manual log grep)     │
│  │                                         │
│  T2: Root cause identified                  │
│  │                                         │
│  ├── RESTORATION (T2→T3)                   │
│  │   Execute: rollback / feature flag off  │
│  │   / hotfix deploy / config change       │
│  │   Elite: < 5 min (automated rollback)  │
│  │   Poor: > 30 min (manual process)      │
│  │                                         │
│  T3: Service restored                       │
│                                             │
│  MTTR = T3 - T0                             │
│                                             │
│  ELITE: < 1 hour (T1<2min, T2<10min,       │
│         T3<15min)                          │
└─────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Error rate spike at 14:05 (T0)
  → SLO burn rate alert at 14:07 (T1, 2min MTTD)
  → On-call paged via PagerDuty
  → Engineer joins incident channel
  → Opens distributed trace for 14:06 requests
  → Sees: DB query timeout in order-service [← YOU ARE HERE]
  → Correlates: last deploy = 13:55 (10min before incident)
  → Incident root cause: missing index from migration
  → Executes: rollback order-service to 13:45 image
     helm rollback order-service 0
  → T2: 14:16 (9min triage)
  → T3: 14:22 (6min restoration)
  → MTTR = 17 minutes [ELITE]
  → Postmortem scheduled
```

**FAILURE PATH (slow MTTR):**
```
Same failure, poor observability:
  T0: 14:05 failure starts
  T1: 14:45 generic alert fires (40min MTTD)
  T2: 16:30 root cause identified (105min)
       (manual log grep, no tracing)
  T3: 17:15 restoration (45min)
       (manual rollback process, no runbook)
  MTTR = 3 hours 10 minutes [LOW]
```

**WHAT CHANGES AT SCALE:**
At large scale (Netflix, Google), MTTR is institutionalised: automated incident detection (auto-creates incidents, auto-assigns on-call, auto-links recent deploys), incident severity levels (SEV1-4) with SLA response times per level, mandatory postmortems for SEV1-2, chaos engineering (GameDays) to practice recovery procedures before real incidents. MTTR at scale is standardised, practiced, and measured as a product metric (SLOs commit to it explicitly).

---

### 💻 Code Example

**Example 1 — SLO-based alerting (faster MTTD):**
```yaml
# Prometheus alerting rules for fast MTTR detection
groups:
  - name: slo-alerts
    rules:
      # Burn rate alert: detects sustained degradation fast
      - alert: ErrorBudgetBurnRateCritical
        expr: |
          (
            rate(http_requests_total{
              status=~"5..",service="order-service"
            }[5m])
            /
            rate(http_requests_total{service="order-service"}[5m])
          ) > 0.02  # 2% error rate (SLO: 99.5%)
        for: 2m  # fires after 2 minutes sustained
        labels:
          severity: critical
          team: platform
        annotations:
          summary: "Order service error rate {{ $value | humanizePercentage }}"
          runbook: "https://runbooks/order-service/error-spike"
          # Link to runbook in alert — reduces triage time
```

**Example 2 — Automated rollback on monitoring trigger:**
```bash
#!/bin/bash
# post-deploy-monitor.sh
# Runs after deployment to detect and auto-rollback

SERVICE=$1
BASELINE_ERROR_RATE=0.005  # 0.5%
MONITORING_WINDOW=120      # 2 min
CHECK_INTERVAL=10          # check every 10s
MAX_CHECKS=$(( MONITORING_WINDOW / CHECK_INTERVAL ))

echo "Monitoring $SERVICE for $MONITORING_WINDOW seconds..."

for i in $(seq 1 $MAX_CHECKS); do
  ERROR_RATE=$(curl -sf \
    "http://prometheus/api/v1/query?query=\
    rate(http_errors_total{service='$SERVICE'}[1m])" | \
    jq '.data.result[0].value[1] // "0"')

  THRESHOLD=$(echo "$BASELINE_ERROR_RATE * 3" | bc -l)

  if (( $(echo "$ERROR_RATE > $THRESHOLD" | bc -l) )); then
    echo "ERROR SPIKE DETECTED: $ERROR_RATE — auto-rolling back"
    # Automated rollback — reduces restoration time to ~2 min
    helm rollback "$SERVICE" 0 --namespace production
    exit 1
  fi
  sleep $CHECK_INTERVAL
done

echo "Monitoring passed — deployment healthy"
```

**Example 3 — Incident timeline tracking for MTTR measurement:**
```python
# incident_tracker.py
from datetime import datetime
import json

class IncidentTracker:
    def __init__(self):
        self.incidents = []

    def start_incident(self, service, description):
        incident = {
            "id": len(self.incidents) + 1,
            "service": service,
            "description": description,
            "start_time": datetime.utcnow().isoformat(),
            "detection_time": None,
            "triage_complete_time": None,
            "end_time": None
        }
        self.incidents.append(incident)
        return incident["id"]

    def mark_detected(self, incident_id):
        inc = self._get(incident_id)
        inc["detection_time"] = datetime.utcnow().isoformat()

    def mark_resolved(self, incident_id):
        inc = self._get(incident_id)
        inc["end_time"] = datetime.utcnow().isoformat()
        start = datetime.fromisoformat(inc["start_time"])
        end = datetime.fromisoformat(inc["end_time"])
        inc["mttr_minutes"] = (end - start).seconds // 60

    def get_mean_mttr(self):
        resolved = [i for i in self.incidents
                    if i.get("mttr_minutes")]
        if not resolved:
            return None
        return sum(i["mttr_minutes"] for i in resolved) / \
               len(resolved)
```

---

### ⚖️ Comparison Table

| DORA Metric | Measures | Category | DORA Band (Elite) |
|---|---|---|---|
| Deployment Frequency | Deploys/time | Speed | Multiple/day |
| Lead Time | Commit→production | Speed | < 1 hour |
| Change Failure Rate | % deploys causing incidents | Quality | 0–5% |
| **MTTR** | Time to restore service | Resilience | < 1 hour |

| MTTR Component | Technique to Reduce |
|---|---|
| Detection time (MTTD) | SLO burn-rate alerts, low-latency monitoring |
| Diagnosis time (MTTI) | Distributed tracing, structured logs, correlation |
| Restoration time (MTTF) | Automated rollback, feature flags, runbooks |

How to choose which to invest in: Measure each MTTR component separately. The largest component is your bottleneck. If MTTD > 30min: invest in alerting. If MTTI > 1 hour: invest in observability (tracing, logging). If MTTF > 20min: invest in automated rollback and runbooks.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| MTTR is the same as MTTF (Mean Time to Failure) | MTTF measures time between failures (reliability). MTTR measures recovery time from failures (resilience). DORA uses MTTR. MTTF is a different hardware reliability metric. |
| Low MTTR means fewer incidents | MTTR measures how fast you recover, not how often you fail (that's CFR). You can have low MTTR (fast recovery) with high CFR (frequent failures) — not a good combination, but they're independent dimensions. |
| MTTR should always be measured from alert fire time | DORA defines MTTR from actual service degradation (T0), not from alert fire time. If alerts fire late, the true MTTR is longer than what monitoring shows. Measuring from alert time conceals poor detection time. |
| You need complex tooling to measure MTTR | MTTR can be measured with a spreadsheet: incident start time (from PagerDuty or logs), end time (verified service restored), duration. Start with manual tracking; automate later. |

---

### 🚨 Failure Modes & Diagnosis

**1. Detection Time Dominates MTTR (Slow Alerting)**

**Symptom:** MTTR records show average of 90 minutes. Post-incident analysis shows T0→T1 (detection) averages 45 minutes. The actual fix takes only 20 minutes once the engineer is engaged.

**Root Cause:** Alerting configured on absolute thresholds (alert when error rate > 50%) rather than SLO burn rates. Below 50%, the system is degraded but not alerting.

**Diagnostic:**
```bash
# Check current alerting thresholds
kubectl get prometheusrule -n monitoring -o yaml | \
  grep -A 5 "alert:"

# Check historical alert fire times vs incident start
# In PagerDuty: compare incident start vs trigger time
pd incidents list --since "30d" \
  | jq '.incidents[] | {created_at, first_trigger: .first_trigger_log_entry.created_at}'
```

**Fix:**
```yaml
# Replace absolute-threshold alerts with SLO burn-rate alerts
# BEFORE (alerts at 50% — too late):
# expr: error_rate > 0.5

# AFTER: alert when 2% of monthly error budget burns in 5min
- alert: SloBurnRateCritical
  expr: |
    error_rate{service="myservice"} > 0.02
    AND
    error_rate{service="myservice"}[5m] > 0.001
  for: 2m  # sustained for 2 minutes
```

**Prevention:** Use SLO-based alerting from the start. Calibrate alert thresholds to fire when meaningful user impact threshold is crossed, not at 100% failure.

---

**2. Restoration Time Extended by Rollback Complexity**

**Symptom:** Root cause identified in 8 minutes but restoration takes 45 minutes. Post-mortem: rollback requires manual approval from a second engineer, who took 30 minutes to respond at 3am.

**Root Cause:** Rollback requires manual approval gate. The gate was designed for forward deployments (requiring peer review) but requires the same gate for rollbacks — counterproductive under incident conditions.

**Diagnostic:**
```bash
# Check rollback procedure documentation
cat runbooks/rollback.md
# If it contains "get approval from X" → gate exists

# Time each rollback step in last 5 incidents
# Calculate: T2 (root cause identified) to T3 (service restored)
```

**Fix:** Create a fast rollback path that bypasses normal approval gates:
- Automated rollback (helm rollback 0) triggered by monitoring — zero human approval needed when triggered by automated monitoring
- On-call engineer can execute rollback without peer approval (document this explicitly in on-call runbook)
- Post-incident review is the accountability mechanism, not pre-rollback approval

**Prevention:** Design rollback as an emergency procedure with a separate, faster approval model. Test rollback monthly to validate it actually works and takes < 5 minutes.

---

**3. MTTR Measurement Inconsistency — Incident Boundaries Undefined**

**Symptom:** Two engineers report different MTTR for the same incident: one says 23 minutes, another 4 hours. Both are correct by different definitions.

**Root Cause:** "Incident start" and "incident end" not precisely defined. One engineer measured from when the alert fired (T1), not from when users were impacted (T0). Another included post-recovery verification in the end time.

**Diagnostic:**
```bash
# Review incident timeline for last 10 incidents
# Does everyone use same T0 definition?
# Check: incident timeline in PagerDuty vs monitoring

# Plot MTTR histogram — is distribution bimodal?
# Two peaks = two definitions being used by different teams
```

**Fix:** Define precisely:
- T0 = first user impact OR first automated alert (whichever is earlier)
- T3 = service health check confirms full restoration (not engineer declares "fixed")
- Document in incident process handbook
- Add T0 and T3 fields to incident ticket template

**Prevention:** Use incident management tools (PagerDuty, Opsgenie) that have explicit "impact started" and "resolved" fields. Automate T3 detection: close incident via API when health check passes for 5 consecutive minutes.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `DORA Metrics` — MTTR is one of the four DORA metrics; the full framework provides essential context
- `Change Failure Rate` — MTTR is paired with CFR; CFR measures how often failures occur, MTTR measures how long they last
- `Observability` — monitoring, tracing, and logging are the primary investments that drive MTTD and MTTI down

**Builds On This (learn these next):**
- `SLO (Service Level Objectives)` — SLO burn-rate alerting is the most effective mechanism for minimising MTTD
- `Rollback Strategy` — automated rollback is the primary lever for minimising restoration time (MTTF)
- `Incident Management` — the process that governs how MTTR is tracked and improved

**Alternatives / Comparisons:**
- `Change Failure Rate` — frequency of failures vs duration; CFR tells you how often you break things, MTTR tells you how long users suffer when you do
- `MTTF (Mean Time to Failure)` — hardware reliability metric measuring time between failures; a completely different concept despite similar name
- `Error Budget` — SRE's budget-based framing of the same reliability concern; MTTR is the recovery component of error budget consumption

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Mean time from production failure start   │
│              │ to full service restoration               │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ User impact duration after failures is    │
│ SOLVES       │ invisible without systematic measurement  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ MTTR = detection + triage + restoration:  │
│              │ instrument each stage to find bottleneck  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — every production service needs   │
│              │ measured MTTR as baseline                 │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never skip — but define T0 precisely      │
│              │ before the first measurement or data is   │
│              │ inconsistent and unusable                 │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Investment in monitoring/runbooks/rollback│
│              │ vs operational overhead of maintaining    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "ER door-to-discharge time — pre-position │
│              │  resources before the patient arrives."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ DORA Metrics → SLO → Rollback Strategy → │
│              │ Chaos Engineering → Incident Management   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your MTTR is 3 hours. Value-stream mapping reveals: T0→T1 (detection) = 45 min, T1→T2 (triage) = 90 min, T2→T3 (restoration) = 45 min. Your team has capacity to invest in improving exactly ONE of these three stages. Which stage would you invest in to maximally reduce MTTR, and what specific technical investments would you make? Also explain why improving the other two stages is less effective, even though they're also slow.

**Q2.** Two SRE philosophies exist for MTTR management: (A) "high automation" — invest in automated detection, automated rollback, and automated runbook execution so incidents can self-resolve without human intervention in the majority of cases; (B) "high practice" — invest in training engineers to diagnose and resolve incidents quickly through regular GameDays, fire drills, and chaos engineering. Both reduce MTTR. Design a strategy that combines both — which class of incidents should be automated (A), which should be practiced (B), and what is the deciding criterion?

