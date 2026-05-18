---
id: OBS-021
title: "Alerting Anti-Patterns (Alert Fatigue)"
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★☆
depends_on: OBS-009, OBS-012, OBS-020
used_by: OBS-042
related: OBS-009, OBS-012, OBS-020, OBS-026, OBS-042
tags:
  - observability
  - reliability
  - sre
  - devops
  - alerting
  - pattern
  - intermediate
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Mastery"
nav_order: 21
permalink: /technical-mastery/obs/alerting-anti-patterns-alert-fatigue/
---

⚡ TL;DR - Alert fatigue occurs when engineers receive
so many low-quality alerts that they stop treating
alerts as urgent. It is the single most destructive
failure mode in on-call engineering: it causes real
incidents to be ignored, burns out engineers, and
erodes trust in the monitoring system.

| #021            | Category: Observability & SRE                                          | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Alerting Fundamentals, SLO, Error Budget                               |                 |
| **Used by:**    | SLO-Based Alerting Strategy                                            |                 |
| **Related:**    | Alerting Fundamentals, SLO, Error Budget, Actionable Alerting Patterns |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An on-call engineer wakes up at 2 a.m. to 47 alerts.
They have been doing this for 6 months. 44 of those
47 alerts are known non-issues: a CPU alert that fires
every time the nightly batch job runs, a disk alert
that resolves itself when log rotation completes, a
memory alert that fires on every deployment and clears
after 5 minutes. The engineer silences the alert
batch, rolls over, and goes back to sleep.

The 3 real alerts - a database connection leak that
will cause a full outage at 6 a.m. - are buried in
the noise. By 6 a.m., checkout is down. Forty thousand
customers cannot complete purchases. The post-mortem
finds the alert fired at 2:17 a.m., but the on-call
engineer - conditioned by 6 months of false positives

- dismissed it as another false alarm.

**THE INVENTION:**
Alert quality frameworks (actionable, symptom-based,
SLO burn rate alerting) and anti-pattern catalogues
give teams the vocabulary and tools to diagnose and
fix noisy alert systems. The Google SRE Book's
principle: "Every page should be urgent, important,
actionable, and require human intelligence." Any alert
that does not meet all four criteria should be
demoted or eliminated.

---

### 📘 Textbook Definition

**Alert fatigue** is the desensitisation of on-call
engineers to alerts caused by excessive alert volume,
high false-positive rates, or alerts that do not
require human action. It manifests as:

- Auto-acknowledge behaviour (dismissing alerts without
  reading them)
- Delayed response to real incidents
- Attrition and burnout of on-call engineers
- Silent degradation of system reliability

**Alert quality** is measured by:

```
Signal-to-noise ratio = actionable_alerts / total_alerts
Ideal: > 90% of pages require human action
Red flag: < 50% of pages are actionable

False positive rate = non-actionable_pages / total_pages
Ideal: < 10%
Crisis: > 50%

Mean time to acknowledge (MTTA):
Ideal: < 5 minutes for P1 incidents
Red flag: > 15 minutes (engineer may be fatigued or asleep)
```

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Alert fatigue is what happens when the monitoring
system cries wolf too often - eventually the engineer
stops listening, and the real wolf eats the flock.

> Imagine a smoke detector that fires every time
> someone makes toast. After the first week, the
> tenants stop responding. They sleep through it. When
> the building actually catches fire, the alarm sounds
> exactly as it always has - and no one wakes up.
>
> An alert system with a high false-positive rate
> is that smoke detector. The engineers are the tenants.
> The goal of alert quality work is to make the detector
> silent except for actual fires.

---

### 🔩 First Principles Explanation

**THE FOUR TESTS (Google SRE Book):**

Every alert page must satisfy ALL four properties:

```
1. URGENT: if not acted on immediately, something
   bad happens (data loss, customer impact, cascade)

2. IMPORTANT: the system cannot self-heal; human
   intelligence is required to resolve the issue

3. ACTIONABLE: the on-call engineer can take a
   specific action that will improve the situation

4. NOVEL: the alert requires human decision-making,
   not a script execution that could be automated

If any property is missing:
- Not urgent → demote to ticket, not page
- Not important → system heals itself, remove alert
- Not actionable → alert gives no guidance, redesign
- Not novel → automate the response, remove the page
```

**THE ALERT HIERARCHY:**

```
Page (interrupt-driven, wake-up)
├── Must satisfy all 4 Google SRE properties
├── Maximum sustainable rate: < 5/shift
└── P1 only: customer-visible, immediate action required

Ticket (high priority, same-day)
├── Important but not immediate (resolve by EOD)
├── Predictive alerts (disk filling in 3 days)
└── SLO burn rate slow-burn (6x for 6h+30m windows)

Log entry (for audit, not action)
├── Informational events
├── Successful operations worth recording
└── Background drift metrics (reviewed weekly)
```

**THE FIVE ANTI-PATTERNS:**

```
1. CAUSE-BASED ALERTING (not symptom-based)
   BAD: Alert on "CPU > 80%"
   Why: CPU at 80% may have zero customer impact.
   GOOD: Alert on "P99 latency > 2s for 5 minutes"
   Why: Directly measures customer experience.

2. STATIC THRESHOLD ALERTING
   BAD: Alert on "error_count > 100 in 5 minutes"
   Why: 100 errors at 10 req/s (1%) vs 100 errors
   at 100,000 req/s (0.0001%) are completely different.
   GOOD: Alert on error rate AND burn rate.

3. NO OWNERSHIP / ORPHANED ALERTS
   BAD: Alert fires → no clear owner → no one responds
   Why: Alert was set up by a team member who left.
   GOOD: Every alert has a named owner team and runbook.

4. MISSING RUNBOOK
   BAD: Alert fires with message "High memory usage"
   Why: Engineer wakes up at 3 a.m. with no guidance.
   GOOD: Every alert links to: expected action, escalation,
   self-healing steps, rollback procedure.

5. FLAPPING ALERTS
   BAD: Alert fires and resolves every 3 minutes
   Why: Threshold is at the edge of normal behavior.
   GOOD: Use sustained-window evaluation (for 5+ minutes)
   or alert only when state persists for > 2 consecutive
   evaluation periods.
```

---

### 🧪 Thought Experiment

**THE PAGER LOAD TEST:**

An on-call engineer is handed the pager for one week.
At the end of the week they answer: how many pages
did you receive? How many required action? How many
resolved themselves before you could act? How many
could have been automated? How many had a runbook?

**Week 1 (unhealthy system):**

- 312 pages in 7 days = 44.6 pages/day = 1.86/hour
- Actionable: 38 (12%) - required human decisions
- Self-healing: 201 (64%) - resolved before action taken
- Automatable: 47 (15%) - same action every time
- No runbook: 189 (61%)

The engineer is exhausted, burned out. The 38
critical incidents that needed human intelligence
were buried in 274 noise pages. Response latency
for real incidents: 23 minutes average (fatigued
engineer, slow to triage).

**Week 1 (healthy system, same infrastructure):**

- 31 pages in 7 days = 4.4 pages/day
- Actionable: 29 (94%)
- Self-healing: 0 (alert tuning eliminated these)
- Automatable: 0 (runbooks handle; remaining pages
  need human judgment)
- No runbook: 2 (new alerts just added, runbooks
  pending within 24h)

The 38 actionable alerts remained. The 274 noise
alerts were eliminated through: tuning, automation,
demotion to tickets, and runbook-driven auto-remediation.
Response latency for real incidents: 3 minutes average.

**The insight:** the 38 real incidents existed in
both scenarios. The difference is signal-to-noise.
Alert quality work does not hide problems - it makes
real problems visible.

---

### 🧠 Mental Model / Analogy

> An emergency department (ED) triage system works
> on a 5-level scale: Level 1 (resuscitation needed
> immediately) through Level 5 (non-urgent). The
> system exists because without it, every patient
> arriving at the ED is treated as an emergency -
> which means doctors sprint to every headache and
> stomach ache and miss the cardiac arrests.
>
> Alert triage is the same system for infrastructure.
> A P1 page is Level 1: act immediately, patient is
> dying (service is down). A ticket is Level 3-4:
> important but can wait for the next available
> provider. A log entry is Level 5: document it,
> no immediate action. The ED triage system is
> trained and enforced. Alert triage should be too.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone):**
When alerts fire too often for minor or fake reasons,
engineers stop taking them seriously. This is alert
fatigue. The solution is fewer, higher-quality alerts
that only fire when action is needed.

**Level 2 - How to recognize it (junior):**
Signs of alert fatigue: on-call engineers "silence
all" on pager duty. Daily page count > 10. More than
half of pages resolve before anyone acts. Runbooks
say "restart the service" with no root-cause analysis.
Post-mortems show "alert was missed" as a contributing
factor.

**Level 3 - How to fix it (mid-level):**
Run an alert audit. Export all pages from the last
90 days. Classify each: actionable, self-healing,
automatable, or orphaned. Remove or demote each
non-actionable alert. Rebuild surviving alerts with:
sustained windows (not instantaneous), rate-based
thresholds (not count-based), and runbooks. Replace
static thresholds with SLO burn rate alerts.

**Level 4 - Governance (senior):**
Alert ownership register: every alert has an owner
team and a review date. Quarterly alert review:
any alert with 0 actionable responses in 90 days
is a candidate for deletion. Alert quality SLOs:
"90% of pages must be actionable" is itself a
measurable target. On-call load metrics: pages per
on-call shift, MTTA, false positive rate - tracked
and reviewed in team health reviews. New alert
approval process: new alerts require a runbook
before merging.

**Level 5 - Platform design (staff):**
Alert platform architecture: a central alert registry
where all alerts across all services are listed with
owner, runbook, last-review date, actionability
classification. Automated actionability auditing:
if an alert fires and the on-call response is
"acknowledged, no action taken" > 80% of the time,
it is automatically flagged for review and the owner
team is notified. On-call health scoring: a metric
per team tracking average daily pages, MTTA, and
alert actionability ratio - reviewed in engineering
all-hands as a reliability health indicator. The
"reliability tax": a team with low alert quality
scores is assigned reliability sprint time until
their on-call health score improves.

---

### ⚙️ How It Works (Mechanism)

**ALERT AUDIT METHODOLOGY:**

```bash
#!/bin/bash
# Alert audit: classify last 90 days of pages
# Requires: PagerDuty API access

SINCE=$(date -d "-90 days" --iso-8601=seconds)
UNTIL=$(date --iso-8601=seconds)
API_KEY="${PAGERDUTY_API_KEY}"

# Export all incidents from last 90 days
curl -s -H "Authorization: Token token=${API_KEY}" \
  -H "Accept: application/vnd.pagerduty+json;version=2" \
  "https://api.pagerduty.com/incidents?since=${SINCE}&until=${UNTIL}&limit=500" \
  | jq '.incidents[] | {
      id: .id,
      title: .title,
      created_at: .created_at,
      resolved_at: .resolved_at,
      time_to_resolve_minutes: (
        ((.resolved_at | fromdateiso8601) -
        (.created_at | fromdateiso8601)) / 60
        | floor
      ),
      acknowledged_by: .acknowledgements[0].acknowledger.summary,
      alert_count: .alerts_count
    }' > incidents_90d.json

# Classify by resolution time:
# < 5 min and no acknowledgement = self-healing
# > 0 acknowledgements and low resolve time = automatable
# Manual action taken = actionable
jq '[.[] | select(.time_to_resolve_minutes < 5 and
  (.acknowledged_by == null))]' incidents_90d.json \
  | jq length
# Output: N self-healing incidents (alert fatigue candidates)
```

**SUSTAINED-WINDOW EVALUATION (fixing flapping):**

```yaml
# BAD: fires on instantaneous metric breach
# Flaps every 30 seconds if metric oscillates around threshold
- alert: HighMemoryUsage
  expr: jvm_memory_used_bytes / jvm_memory_max_bytes > 0.85
  # No 'for' clause - fires on every single scrape breach

# GOOD: requires sustained breach for 5 minutes
# Eliminates transient spikes and flapping alerts
- alert: SustainedHighMemoryUsage
  expr: jvm_memory_used_bytes / jvm_memory_max_bytes > 0.85
  for: 5m # Must be true for 5 consecutive minutes
  labels:
    severity: warning
  annotations:
    summary: "JVM memory > 85% for 5+ minutes on {{ $labels.instance }}"
    runbook: "https://wiki.internal/runbooks/jvm-memory-high"
    description: |
      JVM heap is at {{ $value | humanizePercentage }}.
      Expected cause: memory leak or large payload processing.
      Action: check heap dump at /var/log/heap-dump.hprof
      Escalate to: platform-sre if not resolved in 30 minutes.
```

**SYMPTOM-BASED ALERTING CONVERSION:**

```yaml
# CAUSE-BASED (anti-pattern) - fires on infrastructure metrics
- alert: HighCPU
  expr: cpu_usage_percent > 80
  # Problems:
  # 1. CPU at 80% might mean nothing to users
  # 2. Fires during expected batch processing
  # 3. No customer impact measurement

# SYMPTOM-BASED (pattern) - fires on customer experience
- alert: SlowCheckoutLatency
  expr: |
    histogram_quantile(
      0.99,
      sum by (le) (
        rate(checkout_duration_seconds_bucket[5m])
      )
    ) > 2.0
  for: 3m
  labels:
    severity: page
  annotations:
    summary: "Checkout P99 latency > 2s (SLO breach risk)"
    runbook: "https://wiki.internal/runbooks/checkout-latency"
    # Note: CPU at 80% might cause this - or might not.
    # This alert fires only when customers are actually affected.
```

---

### 🔄 The Complete Picture - End-to-End Flow

**ALERT QUALITY IMPROVEMENT CYCLE:**

```
[Month 0: Baseline measurement]
  Export 90-day page history from PagerDuty/Opsgenie
  Classify all incidents (actionable/self-healing/
    automatable/orphaned)
  Calculate: signal-to-noise ratio, MTTA, pages/shift

[Month 1: Quick wins]
  Remove orphaned alerts (no owner, not fired in 90d)
  Add 'for: 5m' to all instantaneous threshold alerts
  Add runbook links to all surviving alerts
  Move "warn" severity alerts from page to ticket
  Expected improvement: -40% page volume

[Month 2: Cause-to-symptom conversion]
  Audit top 10 most frequent alerts
  For each: identify what customer impact it signals
  Rewrite alert to measure the customer experience directly
  Validate: does the new alert catch the same incidents?
  Remove the old cause-based alert
  Expected improvement: -30% additional page volume

[Month 3: SLO burn rate migration]
  Convert top-level service alerts to burn rate alerts
  (fast burn 14.4x for 1h+5m, slow burn 6x for 6h+30m)
  Remove static error rate threshold alerts
  Expected improvement: -50% false positives for
    remaining high-severity alerts

[Month 4+: Governance]
  Establish quarterly alert review cadence
  Track on-call health score (pages/shift, MTTA, SNR)
  New alert requires runbook before merge
  Alert with SNR < 50% → owner team notification
  Alert with SNR < 20% for 2 quarters → auto-deleted
```

---

### 💻 Code Example

**Example 1 - BAD: Alert anti-pattern collection:**

```yaml
# BAD EXAMPLE 1: Cause-based, no runbook, no 'for'
# Fires on infrastructure metric, not customer symptom
- alert: HighCPU
  expr: cpu_usage_percent > 80
  # No 'for' - fires on every scrape
  # No runbook - engineer has no guidance at 3am
  # No owner - who responds to this?

# BAD EXAMPLE 2: Static count threshold
# Fires for 100 errors regardless of request rate
- alert: TooManyErrors
  expr: checkout_errors_total > 100
  # Problem: counter never resets - always True after
  # any 100 errors ever. Fires once, never resolves.
  # Should use rate() for ongoing alerting.

# BAD EXAMPLE 3: Alerting on everything "just in case"
# This alert has never had an actionable response
- alert: GCPauseDuration
  expr: jvm_gc_pause_seconds_max > 0.1
  # 100ms GC pause has zero customer impact at low load
  # This fires 200 times/week, all auto-acknowledged
  # Classic alert fatigue contributor
```

**Example 2 - GOOD: Actionable, symptom-based alerts:**

```yaml
# GOOD: Symptom-based, sustained, with runbook and owner
- alert: CheckoutAvailabilityLow
  expr: |
    (
      sum(rate(checkout_requests_total{
        status=~"2.."}[5m]))
      / sum(rate(checkout_requests_total[5m]))
    ) < 0.99
  for: 3m # sustained breach, not transient
  labels:
    severity: page
    team: checkout-sre
    runbook: "checkout-availability-low"
  annotations:
    summary: >
      Checkout availability {{ $value | humanizePercentage }}
      (SLO target 99.9%)
    description: |
      Checkout success rate has been below 99% for 3+ min.
      Immediate customer impact. Expected actions:
      1. Check recent deployments (last 2 hours)
      2. Check upstream dependencies (payment, inventory)
      3. Review checkout error logs for error classification
      4. If deployment-related: initiate rollback
      Runbook: https://wiki.internal/runbooks/checkout-availability-low
      Escalate to: checkout-eng-lead if not resolved in 15 min

# GOOD: Burn rate alert instead of static error rate
- alert: CheckoutBurnRateFast
  expr: |
    (
      (1 - sum(rate(checkout_ok_total[1h]))
      / sum(rate(checkout_requests_total[1h])))
    ) / (1 - 0.999) > 14.4
    AND
    (
      (1 - sum(rate(checkout_ok_total[5m]))
      / sum(rate(checkout_requests_total[5m])))
    ) / (1 - 0.999) > 14.4
  labels:
    severity: page
    team: checkout-sre
  annotations:
    summary: "Checkout fast burn: SLO budget depleted in <2 days"
    runbook: "https://wiki.internal/runbooks/checkout-burn-rate"
```

**Example 3 - On-call health dashboard (PromQL):**

```promql
# Pages per on-call shift (8h window)
# Track as a health metric for the team
increase(pagerduty_incidents_total{
  team="checkout-sre"}[8h])

# Alert actionability ratio
# (requires tagging incidents as actionable/non-actionable
#  post-resolution in PagerDuty custom fields)
sum(pagerduty_incidents_total{
  team="checkout-sre",
  actionable="true"}[30d])
/
sum(pagerduty_incidents_total{
  team="checkout-sre"}[30d])

# Mean time to acknowledge (seconds)
avg(pagerduty_incident_time_to_acknowledge_seconds{
  team="checkout-sre"}[30d])
```

---

### ⚖️ Comparison Table

| Anti-pattern               | Cause                                    | Fix                                            | Impact                       |
| -------------------------- | ---------------------------------------- | ---------------------------------------------- | ---------------------------- |
| Cause-based alerting       | Alert on CPU/memory, not user experience | Convert to symptom-based (latency, error rate) | Fewer false positives        |
| Static count threshold     | `errors > 100` ignores request rate      | Use `rate()` or error ratio                    | Eliminates rate-blind alerts |
| No `for:` clause           | Fires on transient spikes                | Add `for: 5m` sustained window                 | Eliminates flapping          |
| No runbook                 | Engineer wakes up with no guidance       | Require runbook URL before alert merges        | Reduces MTTR                 |
| Orphaned alert             | Team disbanded, alert still fires        | Quarterly audit + owner register               | Removes noise                |
| Alert for everything       | "Set and forget" alert sprawl            | Require actionability justification            | Reduces volume               |
| Flapping alert             | Threshold at normal behavior boundary    | Raise threshold or add hysteresis              | Eliminates oscillation       |
| Ticket-worthy alert paging | Low-urgency alert triggers page          | Demote to ticket or log                        | Reduces interrupt rate       |

**Alert severity hierarchy:**

| Severity      | Response target     | Example                               |
| ------------- | ------------------- | ------------------------------------- |
| P1 / Page     | Immediate (< 5 min) | Checkout down, SLO fast burn          |
| P2 / Ticket   | Same business day   | Disk filling in 48h, SLO slow burn    |
| P3 / Log      | Weekly review       | Certificate expiring in 30 days       |
| Informational | Dashboard only      | Deploy completed, autoscale triggered |

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                                                                                   |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "More alerts = more safety"                  | More alerts = alert fatigue = real incidents missed. Quality beats quantity every time. 5 actionable alerts protect better than 50 noisy ones.                                            |
| "Alerting on symptoms ignores root causes"   | Symptom-based alerting detects impact first. Root cause diagnosis happens during incident response. The alert's job is to notify, not to diagnose.                                        |
| "We need alerts for everything just in case" | "Just in case" alerts that never require action train engineers to ignore all alerts. Every alert must have a clear "what I will do when this fires" answer written before it is created. |
| "Silent alerts are safe"                     | No. An alert with 100% false positive rate eventually becomes a silent alert in practice (ignored). The engineer cannot distinguish it from a real alert when both look identical.        |
| "We will tune alerts when we have time"      | Alert quality degrades monotonically without active maintenance. Alerting entropy: the number of noisy alerts grows without bounds unless actively pruned. Schedule quarterly reviews.    |

---

### 🚨 Failure Modes & Diagnosis

**The 2 a.m. ignored incident**

**Symptom:**
A P1 incident was missed. The post-mortem shows the
alert fired at 2:17 a.m. The on-call engineer received
47 pages between midnight and 3 a.m. The critical
alert was on page 31 of the notification stream.
The engineer dismissed it with the same reflex used
for the other 46 alerts.

**Diagnosis:**

```bash
# PagerDuty API: analyze last 30 days of incidents
# Count pages per night shift (midnight-6am)
curl -s -H "Authorization: Token token=${PDKEY}" \
  "https://api.pagerduty.com/incidents?since=..." \
  | jq '[.incidents[] | select(
    (.created_at | strptime("%Y-%m-%dT%H:%M:%SZ") |
    .tm_hour >= 0 and .tm_hour < 6))] | length'
# If result > 5/night consistently: alert fatigue exists

# Check false positive rate for the missed alert type:
# How often did THIS alert fire with no action taken?
# (Requires post-incident tagging in PagerDuty custom fields)
```

**Fix:**

1. Immediate: audit all night-time alerts from
   the last 30 days, classify each
2. Remove or demote all alerts where the action was
   "acknowledged, no further action"
3. Implement the alert quality gate: PR review for
   all new `severity: page` alerts must include
   a runbook and a "when to page" justification
4. Set a team target: < 5 pages per on-call shift

---

**Alert flapping destroys sleep and trust**

**Symptom:**
An alert fires and resolves every 2-3 minutes.
The on-call engineer receives 30 pages in one hour.
After the 10th alert, the engineer silences the
alert in PagerDuty for 24 hours. The underlying
issue (intermittent connection pool exhaustion)
persists unmonitored for the rest of the day.

**Root Cause:**
The alert threshold is set at the edge of normal
behavior. When the connection pool hits 95% capacity
(the threshold), it triggers and resolves repeatedly
as connections are released and re-acquired.

**Fix:**

```yaml
# BAD: threshold at the oscillation edge
- alert: ConnectionPoolHigh
  expr: db_connections_used / db_connections_max > 0.95
  # Oscillates: 94% -> 96% -> 94% -> 96% every 2 min

# GOOD: hysteresis with sustained window + higher threshold
- alert: ConnectionPoolCritical
  expr: db_connections_used / db_connections_max > 0.98
  for: 5m
  # Only fires when > 98% for 5 consecutive minutes
  # After fix, must drop below 98% for 5 min to resolve
  # (Prometheus pending state provides natural hysteresis)
```

Or: use a predictive alert that fires when the pool
is trending toward exhaustion, not when it hits
the threshold:

```promql
# Predict pool exhaustion in < 30 minutes
predict_linear(
  db_connections_used[10m], 1800
) > db_connections_max
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Alerting Fundamentals` - alert routing, severity
  levels, and escalation policies that the anti-patterns
  exploit
- `SLO (Service Level Objective)` - the SLO defines
  the correct alerting target; anti-patterns arise
  when teams alert on infrastructure metrics instead
  of SLO compliance
- `Error Budget` - burn rate alerting (the primary
  solution to alert fatigue for service-level alerts)

**Builds On This (learn these next):**

- `SLO-Based Alerting Strategy` - the complete
  framework for replacing anti-pattern alerts with
  burn-rate-based SLO alerts
- `Actionable Alerting Patterns` - positive patterns
  to replace the anti-patterns catalogued here

**Alternatives / Comparisons:**

- `Anomaly detection alerting` - ML-based alerting
  that adapts thresholds to normal behavior. Reduces
  false positives but adds false negative risk (misses
  novel failure modes) and adds operational complexity.
  Use as a complement to SLO burn rate alerts, not
  as a replacement.

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ FOUR TESTS   │ Urgent + Important + Actionable + Novel  │
│ (page must   │ If ANY is missing: demote or remove      │
│  pass all 4) │                                          │
├──────────────┼──────────────────────────────────────────┤
│ 5 ANTI-      │ 1. Cause-based (not symptom-based)       │
│ PATTERNS     │ 2. Static count threshold (not rate)     │
│              │ 3. No runbook                            │
│              │ 4. Flapping (no 'for:' sustained window) │
│              │ 5. Orphaned alert (no owner)             │
├──────────────┼──────────────────────────────────────────┤
│ HEALTH       │ Pages/shift: < 5 (ideal), > 15 (crisis)  │
│ METRICS      │ Actionable ratio: > 90% good, < 50% bad  │
│              │ MTTA: < 5 min healthy, > 15 min fatigued │
├──────────────┼──────────────────────────────────────────┤
│ QUICK WINS   │ Add 'for: 5m' to all instantaneous alerts│
│              │ Add runbook URL to all alerts            │
│              │ Demote warn-severity to ticket           │
│              │ Remove alerts with 0 action in 90 days   │
├──────────────┼──────────────────────────────────────────┤
│ SOLUTION     │ SLO burn rate alerts for service health  │
│              │ Symptom-based for customer experience    │
│              │ Predictive for capacity exhaustion       │
├──────────────┼──────────────────────────────────────────┤
│ GOVERNANCE   │ Quarterly alert audit mandatory          │
│              │ New alert requires runbook before merge  │
│              │ Pages/shift tracked as team health KPI   │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ "More alerts = more safety" = FALSE      │
│              │ "Just in case" alerts = alert fatigue    │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ SLO-Based Alerting Strategy              │
│              │ Actionable Alerting Patterns             │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Noise drowns signal. Every high-volume notification
channel (alerts, code review requests, Slack messages,
email) degrades in information density as volume
grows. The principle "every notification must require
action" applies to: CI/CD pipeline notifications
(only notify on failure, not every successful step),
Dependabot PRs (batch weekly, not one PR per dependency),
Jira ticket updates (subscribe to actionable state
changes, not every comment), Slack channel design
(dedicated channels for actionable alerts, not
informational noise). The alert fatigue framework
(four tests, severity hierarchy, runbooks, quarterly
audit) generalises to any notification system.

---

### 💡 The Surprising Truth

The most counterintuitive alert fatigue insight:
the best-run on-call teams have the fewest alerts.
It seems wrong - a team monitoring 50 microservices
should have more alerts than a team monitoring 5,
right? In practice, the best teams aggressively
prune alerts: they have defined alert quality standards,
quarterly reviews delete orphaned and non-actionable
alerts, and new alerts face scrutiny before merging.
A healthy on-call is "boring": 1-2 pages per shift,
all actionable, all resolved within 30 minutes,
engineer back to sleep within 20 minutes. The boring
on-call is the sign of a mature reliability culture.
The chaotic on-call with 50 nightly pages is not a
sign of a vigilant team - it is a sign of a team
that has lost control of its monitoring system.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[IDENTIFY]** Given a list of 10 alerts, apply
   the four Google SRE tests (urgent, important,
   actionable, novel) and classify which should be
   demoted to ticket or removed entirely.
2. **[FIX]** Rewrite a cause-based alert (e.g., "CPU
   > 80%") as a symptom-based alert (e.g., P99
   > latency degradation) and explain why the symptom-
   > based version has fewer false positives.
3. **[AUDIT]** Design a 90-day alert audit process:
   what data to export, how to classify each incident,
   and what action to take for each classification.
4. **[DESIGN]** Write an alert for a flapping condition
   (e.g., connection pool oscillating at 95%) using
   a sustained window and/or a predictive approach.
5. **[GOVERN]** Design the alert quality governance
   process for a team of 6 engineers: how new alerts
   are reviewed, how quarterly audits work, and what
   on-call health metrics are tracked.

---

### 🧠 Think About This Before We Continue

**Q1.** Your team has an alert "JVM heap memory > 85%"
that fires 200 times per month. Post-mortem analysis
shows: 185 times it resolved within 3 minutes without
action; 10 times the engineer restarted the JVM;
5 times it correlated with an actual customer-visible
latency spike. Apply the four Google SRE tests to
this alert. What should happen to it?
\*Hint: 185/200 = 92.5% false positive rate. Not
urgent (92.5% resolve without action), borderline
important (only 5/200 caused customer impact), not
actionable (what does the engineer do?), not novel
(restart the JVM is automatable). Verdict: (a)
Create a runbook. (b) Add a restart automation that
runs when heap > 90%. (c) Remove this alert. (d)
Create a new symptom-based alert: "JVM latency P99

> 2s for 5 minutes" - which captures the 5 real
> incidents without the 195 noise pages.\*

**Q2.** Design an on-call health score for a 4-person
team. What metrics would you track? What thresholds
indicate "healthy" vs "at risk" vs "crisis"? How
would you display this information and who would
act on it?
\*Hint: Track per-week per engineer: pages received,
actionable ratio, MTTA, sleep-hour pages (midnight-6am).
Healthy: < 5 pages/shift, > 90% actionable, MTTA < 5
min, < 1 sleep-hour page/week. At risk: 5-15 pages,
70-90% actionable, MTTA 5-15 min, 2-3 sleep pages/week.
Crisis: > 15 pages/shift, < 70% actionable, MTTA

> 15 min, > 5 sleep pages/week. Display: Grafana
> dashboard reviewed in weekly team meeting. Actions:
> at-risk triggers alert audit sprint; crisis triggers
> immediate escalation to engineering manager and
> mandatory reliability sprint.\*

**Q3 (TYPE G):** You are joining a team as the new
SRE lead. Their on-call stats for last quarter:
312 total pages, 38 actionable (12%), average MTTA
23 minutes, 7 sleep-hour pages per night. The team
is burning out and 2 engineers have already left.
The CTO asks for a 90-day plan to fix the on-call
health. What is your plan?
_Hint: Week 1: export all 312 incidents. Classify.
No new alerts added. Week 2-4: quick wins (add 'for:'
clauses, runbooks, demote warn-severity to ticket).
Target: -40% page volume. Month 2: convert top 10
most frequent alerts from cause-based to symptom-
based. Target: -30% additional. Month 2-3: SLO burn
rate migration for top 3 services. Month 3: establish
governance (alert review process, new alert checklist,
quarterly audit schedule). Measure: weekly on-call
health score. Report to CTO at day 30, 60, 90.
Target at day 90: < 50 pages/week, > 80% actionable,
MTTA < 8 minutes._

---

### 🎯 Interview Deep-Dive

**Q1: "What is alert fatigue and how would you
address it in an on-call system?"**
_Why they ask:_ Tests practical SRE experience and
understanding of monitoring system health.
_Strong answer includes:_

- Definition: desensitisation from excessive alert
  volume / high false positive rate
- Measurement: pages/shift, actionable ratio, MTTA
- Root causes: cause-based alerting, missing 'for:'
  clauses, orphaned alerts, no runbooks
- Fix process: 90-day audit (export, classify, remove/
  demote/fix), then governance (quarterly review,
  new alert checklist, on-call health KPI tracking)
- Key principle: "every page must satisfy the four
  Google SRE tests" - urgent, important, actionable,
  novel

**Q2: "What is the difference between cause-based
and symptom-based alerting? Give an example."**
_Why they ask:_ Discriminates engineers who understand
alerting philosophy from those who just write YAML.
_Strong answer includes:_

- Cause: alerts on infrastructure metrics (CPU, memory,
  disk) that may not correlate with customer impact
- Symptom: alerts on user-facing metrics (latency,
  error rate, availability) that directly measure
  customer experience
- Example: "CPU > 80%" (cause) vs "P99 checkout
  latency > 2s for 3 minutes" (symptom)
- Key insight: the symptom alert fires only when
  customers are affected. The cause alert fires
  whenever the infrastructure behaves in a certain
  way, regardless of user impact.
- Advanced: symptom-based alerting does not mean
  ignoring infrastructure. Infrastructure metrics
  are used for diagnosis during incident response,
  not as alert triggers.

**Q3: "How would you design the alerting strategy
for a new microservice?"**
_Why they ask:_ Tests ability to design alerting
from first principles rather than cargo-culting
existing patterns.
_Strong answer includes:_

- Step 1: Define the SLO first (what does "working"
  mean for this service?). The SLO defines the
  alerting target.
- Step 2: Create SLO burn rate alerts (fast burn:
  14.4x for 1h+5m windows; slow burn: 6x for 6h+30m
  windows). These are the primary on-call alerts.
- Step 3: Add symptom-based alerts for known failure
  modes (database unavailable, dependency timeout)
  only if they are not captured by the SLO burn rate.
- Step 4: For each alert: write the runbook first,
  then write the alert. If you cannot write the
  runbook, you cannot write a good alert.
- Step 5: Create dashboards for infrastructure metrics
  (CPU, memory, connections) - these are for diagnosis,
  not alerting.
- What to avoid: no alert for CPU/memory/disk by
  default; no count-based thresholds; no alerts
  without runbooks; no new pages that duplicate
  information already captured by SLO burn rate.
