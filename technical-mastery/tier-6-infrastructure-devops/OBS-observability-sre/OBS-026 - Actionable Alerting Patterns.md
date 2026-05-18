---
version: 2
layout: default
title: "Actionable Alerting Patterns"
parent: "Observability & SRE"
grand_parent: "Technical Mastery"
nav_order: 6
permalink: /technical-mastery/observability/actionable-alerting-patterns/
number: "OBS-006"
category: Observability & SRE
difficulty: ★★★
depends_on: Alerting, SRE, Observability
used_by: Observability & SRE
related: AWS CloudWatch Alarms, PagerDuty, SLO vs SLA vs SLI
tags:
  - observability
  - advanced
  - bestpractice
  - pattern
  - production
---

⚡ **TL;DR -** Actionable Alerting Patterns are a set of design principles that ensure every alert is meaningful, routable, and resolvable - eliminating alert fatigue while preserving detection coverage.

| Field | Value |
|---|---|
| **Depends on** | Alerting, SRE, Observability |
| **Used by** | Observability & SRE |
| **Related** | AWS CloudWatch Alarms, PagerDuty, SLO vs SLA vs SLI |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your on-call rotation receives 200 pages per week. Half fire at 2am. 80% resolve themselves before the engineer even logs in. The team learns to ignore pages - until the one real incident is buried in noise and goes undetected for 4 hours.

**THE BREAKING POINT:**
Alert fatigue is the operational equivalent of the boy who cried wolf. When alert volume exceeds the team's capacity to respond meaningfully, alerts lose their signal value. Engineers begin suppressing, acknowledging-without-acting, or sleeping through pages.

**THE INVENTION MOMENT:**
Actionable Alerting Patterns define a discipline: every alert must have a clear owner, a defined response, a linked runbook, and must represent a symptom (user impact) rather than a cause (internal metric). Alerts that do not meet these criteria should not exist.

---

### 📘 Textbook Definition

**Actionable Alerting Patterns** are a set of operational design principles for building alert systems in which every alert is: (1) **symptom-based** - triggered by user-visible impact, not internal implementation state; (2) **routable** - assigned to the correct team and severity; (3) **actionable** - solvable by the on-call engineer within the on-call window; (4) **linked** - connected to a runbook with diagnostic steps and resolution procedures; and (5) **calibrated** - tuned to fire rarely enough to preserve signal value. They include severity tiers (P1/P2/P3), SLO-based error budget burn rate alerting, and alert lifecycle management.

---

### ⏱️ Understand It in 30 Seconds

**One line:** An actionable alert is one where the on-call engineer knows exactly what to do within 5 minutes of receiving it.

> Like a fire alarm with zone indicators: not just "fire somewhere in the building" but "fire in Zone 3, Floor 2 - follow evacuation route C." The alarm tells you the symptom (fire), the location (Zone 3), and the action (route C).

**One insight:** The test of any alert is: "If I receive this at 3am, can I resolve it within 15 minutes without asking anyone?" If the answer is no, the alert is either missing a runbook or should not page at 3am.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. **Alerts must represent user impact** - internal metrics (CPU, queue depth, thread count) are causes, not symptoms; alert on error rate, latency SLO breach, and availability loss.
2. **Every alert requires a response** - if the correct response to an alert is "wait and see," it should not page; use a dashboard or a low-priority ticket instead.
3. **Alert volume is inversely proportional to signal quality** - the more alerts fire, the less attention each receives; fewer, higher-quality alerts are better than comprehensive noisy coverage.
4. **Severity must match response urgency** - P1 (wake-me-up) must be reserved for active user impact; P3 (next business day) for degraded-but-not-broken states.

**DERIVED DESIGN:**
Alert design follows a hierarchy: SLO error budget burn rate → symptom-based metrics → cause-based metrics (last resort). Runbooks are mandatory and versioned. Alert routing uses team ownership tags. Severity levels drive notification channels: P1 → call, P2 → SMS, P3 → ticket/email.

**THE TRADE-OFFS:**

**Gain:** Reduced alert fatigue, faster MTTD and MTTR, higher on-call quality of life, fewer missed incidents.

**Cost:** Requires investment in SLO definition, runbook writing, and ongoing alert review; symptom-based alerting may have slightly higher detection latency than cause-based alerting.

---

### 🧪 Thought Experiment

**SETUP:** Your checkout service has a database connection pool. You can alert on "connection pool utilisation > 80%" (cause) OR "checkout error rate > 1% for 3 minutes" (symptom).

**WHAT HAPPENS WITH CAUSE-BASED ALERT:**
The connection pool hits 80% at 2am - the system is under load but checkout is working fine (95% of requests succeed). The on-call engineer is woken up, investigates for 20 minutes, sees no user impact, and goes back to sleep frustrated. This happens twice a week.

**WHAT HAPPENS WITH SYMPTOM-BASED ALERT:**
The connection pool hits 100% and requests start failing. The error rate alarm fires at 2:00am (3 minutes detection window). The engineer is paged, opens the runbook, follows the "DB connection exhaustion" diagnosis steps, and resolves in 12 minutes. The on-call engineer was paged once, for a real incident, with a clear action.

**THE INSIGHT:** Cause-based alerts fire earlier but generate noise. Symptom-based alerts fire when users are actually affected - which is the only time a 2am wake-up is justified.

---

### 🧠 Mental Model / Analogy

> Actionable Alerting is like a hospital triage system. Not every patient who arrives goes straight to surgery (P1). Triage categorises by severity (P1/P2/P3), routes to the right specialist (alert routing), and each patient has a treatment protocol (runbook). The goal is not to admit every possible patient - it is to correctly treat the patients who truly need urgent care.

**Element mapping:**
- Patient = system event / alert candidate
- Triage severity = P1 / P2 / P3 severity
- Surgeon = on-call engineer
- Waiting room → next-day clinic = P3 ticket
- ICU = P1 page (wake-up)
- Treatment protocol = runbook
- Admission criteria = alert threshold / SLO definition

Where this analogy breaks down: hospitals deal with individual patients sequentially; alert systems may fire dozens of simultaneous alerts during a major incident.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Actionable Alerting Patterns are rules for designing alerts so that every time your phone rings at 3am, it is for something real that you can actually fix - and you know exactly what to do.

**Level 2 - How to use it (junior developer):**
For every alert you create, answer: (a) Does this represent user impact? (b) What does the on-call engineer do when this fires? (c) Is there a runbook? (d) What severity is it? If you cannot answer all four, the alert is not ready to go to production. Use P1 only for active user impact, P2 for degraded states, and P3 for non-urgent warnings.

**Level 3 - How it works (mid-level engineer):**
Implement alerts at three layers: (1) SLO error budget burn rate alerts (fast burn: 2% budget in 1 hour → P1; slow burn: 5% budget in 6 hours → P2); (2) symptom metrics (error rate, latency p99, availability); (3) cause metrics only for specific known failure modes with clear runbooks. Route alerts by service ownership labels. Every alert has: `runbook_url`, `severity`, `team`, `summary`, and `dashboard_url` as metadata. Review alert volume weekly - any alert firing > 5 times per week without human action is a candidate for automation or suppression.

**Level 4 - Why it was designed this way (senior/staff):**
SLO error budget burn rate alerting (pioneered in the Google SRE book) solves the fundamental problem with static thresholds: a 1% error rate might be catastrophic for a service with a 99.9% SLO (burning the entire monthly budget in an hour) or irrelevant for a service with a 95% SLO. Burn rate normalises the alert threshold to the SLO, making alerts proportional to actual SLO impact. Multi-window burn rate alerts (fast + slow) catch both sudden severe outages and slow creeping degradations. The discipline of requiring runbooks for every alert is not bureaucracy - it is a forcing function that ensures the alert designer has thought through the response procedure before an incident, rather than asking an exhausted on-call engineer to figure it out at 2am.

---

### ⚙️ How It Works (Mechanism)

```
Alert Design Process:
  1. Define SLO (e.g., 99.9% availability)
     ↓
  2. Compute error budget (0.1% = 43min/month)
     ↓
  3. Set burn rate thresholds:
     Fast: 14x burn rate → 1h window → P1
     Slow: 6x burn rate → 6h window → P2
     ↓
  4. Define symptom metrics:
     error_rate, latency_p99, availability
     ↓
  5. Write runbook for each alert:
     diagnosis steps + resolution options
     ↓
  6. Set routing + severity:
     P1 → PagerDuty → phone call
     P2 → PagerDuty → SMS
     P3 → Jira ticket → email
     ↓
  7. Review loop (weekly):
     firing_count, MTTA, resolution_rate
     → tune or remove underperforming alerts
```

**Error budget burn rate formula:**
```
burn_rate = current_error_rate / error_budget_rate

For 99.9% SLO (error_budget_rate = 0.001):
  Current error_rate = 0.014 (1.4%)
  burn_rate = 0.014 / 0.001 = 14x
  At 14x burn rate: budget exhausted in ~2h
  → P1 alert justified
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Checkout service running
  ↓ error_rate = 0.05% (normal)
SLO burn rate = 0.5x (healthy)
  ↓ No alert fires ← YOU ARE HERE
On-call engineer sleeps uninterrupted
Dashboard shows green SLO compliance
Weekly review: 0 pages this week
```

**FAILURE PATH:**
```
DB connection pool exhausted
  ↓ error_rate rises to 5%
Burn rate = 50x → 1h window breached
  ↓ P1 alert fires → PagerDuty call
On-call engineer receives call (02:14)
  ↓ opens runbook link in alert
Runbook: "DB connection exhaustion"
  Step 1: check pool metrics
  Step 2: identify long-running queries
  Step 3: restart connection pool / scale
  ↓ resolved in 12 minutes (02:26)
Incident review: runbook updated
  → root cause: missing query timeout
```

**WHAT CHANGES AT SCALE:**
At large organisations with hundreds of services, alert governance requires tooling: alert catalogues, ownership enforcement, automated runbook link validation, and weekly alert review dashboards. PagerDuty / Opsgenie alert quality metrics (MTTA, pages per engineer per week, noise rate) become team-level KPIs.

---

### 💻 Code Example

**BAD - Cause-based, no runbook, wrong severity:**
```yaml
# Fires on internal metric, not user impact.
# No runbook. P1 for non-user-impacting state.
# Will generate fatigue within days.
- alert: HighConnectionPoolUsage
  expr: |
    db_pool_utilization > 0.8
  for: 1m
  labels:
    severity: critical  # wrong - P1 reserved
  annotations:
    summary: "DB pool over 80%"
    # No runbook_url
    # No dashboard_url
    # No description of impact
```

**GOOD - Symptom-based, SLO burn rate, runbook linked:**
```yaml
# Prometheus alerting rules (Alertmanager)

# P1: fast burn - exhausting error budget in 1h
- alert: CheckoutSLOFastBurn
  expr: |
    (
      rate(http_requests_total{
        job="checkout",status=~"5.."}[1h])
      /
      rate(http_requests_total{
        job="checkout"}[1h])
    ) > (14 * 0.001)
  for: 2m
  labels:
    severity: p1
    team: checkout
    service: checkout
  annotations:
    summary: >
      Checkout error rate burning SLO
      budget at 14x rate
    description: >
      At current error rate, monthly error
      budget will be exhausted in ~2 hours.
      Immediate investigation required.
    runbook_url: >
      https://wiki/runbooks/checkout-p1
    dashboard_url: >
      https://grafana/d/checkout-ops

# P2: slow burn - degraded over 6 hours
- alert: CheckoutSLOSlowBurn
  expr: |
    (
      rate(http_requests_total{
        job="checkout",status=~"5.."}[6h])
      /
      rate(http_requests_total{
        job="checkout"}[6h])
    ) > (6 * 0.001)
  for: 15m
  labels:
    severity: p2
    team: checkout
  annotations:
    summary: >
      Checkout error rate elevated (slow burn)
    runbook_url: >
      https://wiki/runbooks/checkout-p2

# P3: warning - investigate next business day
- alert: CheckoutLatencyElevated
  expr: |
    histogram_quantile(0.99,
      rate(http_duration_seconds_bucket{
        job="checkout"}[5m])
    ) > 2.0
  for: 30m
  labels:
    severity: p3
    team: checkout
  annotations:
    summary: "p99 latency > 2s for 30min"
    runbook_url: >
      https://wiki/runbooks/checkout-latency
```

---

### ⚖️ Comparison Table

| Alert Type | Symptom-based | Cause-based | SLO Burn Rate |
|---|---|---|---|
| **What it measures** | User impact (error rate, latency) | Internal state (CPU, pool usage) | Error budget consumption speed |
| **Detection latency** | Moderate (needs user impact) | Early (fires before impact) | Fast (burn rate windows) |
| **False positive rate** | Low | High | Low |
| **Requires SLO definition** | No | No | Yes |
| **Runbook complexity** | Medium | High | Medium |
| **Best for** | P1/P2 production alerts | Capacity planning warnings | SRE-mature teams with defined SLOs |
| **Alert fatigue risk** | Low | High | Very low |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "More alerts = better coverage" | More alerts = more noise = less attention per alert = missed incidents; fewer, higher-quality alerts provide better coverage |
| "P1 alerts should fire early before impact" | P1 should fire only on confirmed user impact; pre-impact warnings belong at P2/P3 to preserve P1 signal value |
| "Runbooks slow down incident response" | A good runbook accelerates response by 3–5x; the first 5 minutes of an incident are spent orienting - a runbook eliminates that |
| "Symptom-based alerts always catch issues" | Symptom-based alerts may miss issues that affect a small user segment below the threshold; complement with synthetic monitoring |
| "Alerting and monitoring are the same thing" | Monitoring collects all signals; alerting is the selective, curated subset of monitoring that demands human action |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Alert fatigue - on-call team ignoring pages**

**Symptom:** Mean time to acknowledge (MTTA) rises above 15 minutes; engineers report high stress; incidents are missed.

**Root Cause:** Alert volume too high, too many P1 alerts for non-user-impacting conditions, no runbooks.

**Diagnostic:**
```bash
# PagerDuty API: pages per week per service
curl -H "Authorization: Token $PD_TOKEN" \
  "https://api.pagerduty.com/incidents?\
start=2024-01-01&end=2024-01-31" \
  | jq '[.incidents[] | {
      service: .service.summary,
      urgency: .urgency
    }] | group_by(.service)
    | map({
        service: .[0].service,
        count: length
      })
    | sort_by(-.count)'
```
**Fix:** Conduct an alert audit: for each alert firing > 5 times per week, either automate the resolution, demote the severity, or delete it.

**Prevention:** Establish an alert creation review process; require runbook links before any alert goes to production.

---

**Mode 2: Silent failures - incidents missed by alerting**

**Symptom:** Users report problems; no alert fired. Post-mortem reveals the metric was below threshold throughout.

**Root Cause:** Alert threshold set too high, wrong metric selected (cause not symptom), or metric sampling too sparse.

**Diagnostic:**
```bash
# Replay historical metrics to find
# what threshold would have caught it
aws cloudwatch get-metric-statistics \
  --namespace MyApp/Checkout \
  --metric-name ErrorRate \
  --start-time 2024-01-15T01:00:00Z \
  --end-time 2024-01-15T05:00:00Z \
  --period 60 \
  --statistics Average \
  | jq '.Datapoints | sort_by(.Timestamp)'
```
**Fix:** Add synthetic monitoring (scheduled health checks from outside the system) to catch issues that internal metrics miss. Add user-journey availability metrics.

**Prevention:** After every incident, add a "detection" section to the post-mortem: "What would have detected this earlier?"

---

**Mode 3: Alert storms during major incidents**

**Symptom:** During a database outage, 150 individual service alerts fire simultaneously; on-call cannot determine root cause amid the noise.

**Root Cause:** Individual alerts on symptoms that are all caused by one upstream failure; no causal grouping.

**Diagnostic:**
```bash
# Check alert firing timeline
# (Alertmanager or PagerDuty timeline view)
# Look for alerts clustered at same timestamp
# → indicates common upstream cause
```
**Fix:** Implement inhibition rules in Alertmanager: if `DatabaseDown` alert fires, inhibit child service alerts from firing. Use Composite Alarms (AWS) or alert dependency chains.

**Prevention:** Design alert topology to mirror service dependency topology; root cause alerts suppress symptom alerts.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- SRE (Site Reliability Engineering) - the discipline that defines SLOs and error budgets
- SLO vs SLA vs SLI - the foundation of SLO-based burn rate alerting
- Observability - the capability that alerting operates on

**Builds On This (learn these next):**
- PagerDuty - on-call management and alert routing platform
- AWS CloudWatch Alarms - the AWS implementation of alert rules
- Incident Management - the process triggered when a P1 alert fires

**Alternatives / Comparisons:**
- Prometheus Alertmanager - open-source alert routing with inhibition and grouping
- Grafana Alerting - multi-datasource alerting with annotation integration
- Datadog Monitors - cross-service alerting with richer composite conditions

---

### 📌 Quick Reference Card

```
╔════════════════════════════════════════════╗
║ WHAT IT IS   Design principles for         ║
║              meaningful, low-noise alerts  ║
║ PROBLEM      Alert fatigue makes on-call   ║
║              ignore pages - real incidents ║
║              get missed                    ║
║ KEY INSIGHT  Alert on symptoms (user       ║
║              impact), not causes           ║
║ USE WHEN     Building or auditing an       ║
║              on-call alerting system       ║
║ AVOID WHEN   - (these are universal        ║
║              principles, always apply)     ║
║ TRADE-OFF    Symptom alerting: lower noise ║
║              vs slightly higher detection  ║
║              latency than cause alerting   ║
║ ONE-LINER    Every alert must be: real,    ║
║              routable, runbooked, resolved ║
║ NEXT EXPLORE SLO Burn Rate Alerting,       ║
║              Incident Management           ║
╚════════════════════════════════════════════╝
```

---

### 🧠 Think About This Before We Continue

1. **(D - Root Cause)** Your on-call team receives 80 pages per week. After an alert audit, you find 60 of them are for a `HighMemoryUsage` alert that resolves itself within 5 minutes every time and has never caused user impact. The engineer who created it refuses to delete it because "memory pressure could cause an OOM in the future." Construct the argument - using the principles of actionable alerting - for why this alert should be removed or redesigned, and propose what it should be replaced with.

2. **(B - Scale)** At a 1,000-service organisation, each team creates its own alerts independently. Alert quality varies wildly - some services have no alerts, others have 50. Design a governance process that establishes minimum alert quality standards without creating a bottleneck that slows down teams shipping new services.

3. **(C - Design Trade-off)** SLO burn rate alerting requires a defined SLO. A team argues that they cannot define an SLO because "the business hasn't decided what availability level they need." Design an alternative alerting strategy that provides meaningful coverage without a defined SLO, and explain what capability is lost compared to burn rate alerting.
