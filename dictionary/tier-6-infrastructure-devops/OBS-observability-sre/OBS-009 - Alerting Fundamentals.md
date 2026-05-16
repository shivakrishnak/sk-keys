---
id: OBS-009
title: Alerting Fundamentals
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★☆☆
depends_on: OBS-003, OBS-005, OBS-006
used_by: OBS-011, OBS-012, OBS-014
related: OBS-005, OBS-006, OBS-011
tags:
  - observability
  - reliability
  - foundational
  - first-principles
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 9
permalink: /obs/alerting-fundamentals/
---

# OBS-009 - Alerting Fundamentals

⚡ TL;DR - Effective alerts fire when users are being
harmed right now (SLO burn rate) and are silent when
everything is within acceptable bounds - not when
any threshold is breached in a noisy threshold system.

| #009 | Category: Observability & SRE | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Monitoring vs Observability, SRE What It Is, Metrics Types | |
| **Used by:** | SLI/SLO, Error Budget, On-Call Management | |
| **Related:** | SRE, Metrics Types, SLI Fundamentals | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
The on-call engineer receives 847 alerts between midnight
and 6 AM. The first 200 are CPU utilisation alerts firing
at 75%. The next 300 are disk space alerts at 80%.
The next 200 are memory usage at 70%. Each alert requires
a manual check: is this actually causing user impact?
In every case: no. By 6 AM, the engineer has investigated
300 non-urgent alerts. Alert 847 is a real payment
processing failure. The engineer misses it because they
assumed it was another false alarm, silenced their phone
after alert 300, and fell asleep.

**THE BREAKING POINT:**
Alert fatigue is the most common observability failure
pattern in production systems. Teams add threshold-based
alerts to every metric they can measure. Over 6 months,
a service accumulates 150 alert rules. The alert-to-
incident ratio is 20:1 (20 alerts fire per actual user
impact incident). Engineers learn to ignore alerts.
Real incidents go undetected.

**THE INVENTION MOMENT:**
The Google SRE Book (2016) formalised the principle:
"Alert on symptoms, not causes." An SLO burn rate alert
fires when users are experiencing failures now, not when
a resource metric crosses a threshold. This reframed
alerting from "monitor everything" to "alert only when
user experience is degrading faster than your error
budget allows."

---

### 📘 Textbook Definition

**Alerting** is the practice of generating automated
notifications when a system's observed state warrants
human attention. Effective alerting has three properties:
1. **High precision:** few false positives (alerts that
   fire when there is no user impact)
2. **High recall:** few false negatives (alerts that
   miss real incidents)
3. **Actionable:** every alert has a clear response action;
   no alert fires that cannot be actioned

**Alert types by category:**
- **Symptom alerts:** user-visible degradation (error rate,
  latency SLO breach). These are the alerts you page on.
- **Cause alerts:** internal system conditions (high CPU,
  disk full). These are ticket-worthy, not page-worthy.
- **SLO burn rate alerts:** the rate at which the monthly
  error budget is being consumed. The most effective
  production alerting approach.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Good alerts tell you when users are being harmed right now.
Bad alerts tell you about internal system conditions that
may or may not cause user harm.

> A car's warning light system is well-designed alerting.
> The "check engine" light (symptom alert) fires when the
> engine is misfiring - a user-impacting condition requiring
> immediate attention. The oil temperature gauge (cause
> metric) shows a number you can monitor at will. You are
> not paged because engine temperature is at 90°C vs normal
> 87°C. You are paged when the temperature reaches a level
> that will damage the engine. The distinction: the warning
> light requires action now; the gauge informs you.

**One insight:**
The most important metric in alerting is the alert-to-
incident ratio. A well-tuned alerting system has a ratio
near 1:1 (every alert represents a real incident). A
poorly tuned system has a ratio of 20:1 or higher.
The ratio is a direct measure of on-call toil.

---

### 🔩 First Principles Explanation

**THE FOUR ALERTING PROPERTIES (Rob Ewaschuk, 2013):**

1. **Every alert must be actionable** - if an engineer
   cannot do anything in response to the alert, it should
   not be an alert (it may be a dashboard, a log, or a
   low-priority ticket)
2. **Every alert must be urgent** - if the alert can wait
   until business hours, it should not page at 3 AM
3. **Every alert must be real** - if the alert fires but
   there is no user impact, it is a false positive and
   should be deleted or adjusted
4. **Every alert must be diagnosed quickly** - the alert
   should include the diagnostic context needed to resolve
   it within the SLO response time

**THE MATH OF SLO BURN RATE ALERTS:**

If your monthly SLO is 99.9% (0.1% error budget):
- Monthly error budget: 0.001 x 2,592,000s = 2,592s
  (43.2 minutes)
- Sustainable burn rate: 1.0 (consuming budget at exactly
  the rate that would exhaust it in 30 days)
- Fast burn rate: 14.4x (1 hour of fast burning = 2 hours
  of budget consumed)
- Fast burn alert threshold: if you burn at 14.4x for
  1 hour, you have burned 2/24 x 30 = 2.5 days of budget

```
burn_rate = (current error rate) / (1 - SLO target)
          = 0.05 / 0.001 = 50x  (5% errors on 99.9% SLO)
```

At 50x burn rate, monthly error budget is exhausted in:
`43.2 minutes / 50 = 0.86 minutes` - critical situation.

**TRADE-OFFS:**
**Symptom alerting gains:** low false positive rate, high
signal to noise, actionable, correlated to user impact.
**Symptom alerting costs:** requires SLO instrumentation,
requires histogram metrics for latency SLIs, more complex
to configure than threshold alerts.
**Threshold alerting gains:** simple to configure, no SLI
instrumentation required.
**Threshold alerting costs:** high false positive rate,
alert fatigue, no direct correlation to user impact.

---

### 🧪 Thought Experiment

**SETUP:**
Two teams monitor the same checkout service.

**TEAM A: Threshold-based alerting:**
- CPU > 80% → alert
- Memory > 75% → alert
- 5xx error count > 10 → alert
- Response time P50 > 500ms → alert
- Disk > 85% → alert
- Connection pool > 90% → alert

**TEAM B: SLO burn rate alerting:**
- SLO: 99.9% success, P99 < 500ms
- Alert: error budget burn rate > 14.4x for 5 min (page)
- Alert: error budget burn rate > 3x for 30 min (page)
- Ticket: error budget consumed > 10% in < 3 days

**WHAT HAPPENS ON A SLOW TRAFFIC NIGHT:**
Team A: CPU drops to 20%, memory at 40%, no requests.
3 AM: disk fills with log files. Disk > 85% alert fires.
Engineer is paged, reviews, creates a ticket to clean logs.
The system is healthy from a user perspective.

Team B: No requests, no errors. SLO burn rate = 0.
No alerts. Engineer sleeps.

**WHAT HAPPENS DURING AN ACTUAL INCIDENT:**
Checkout error rate spikes to 5% due to payment service
timeout. Team A: 5xx alert fires for each instance
independently (8 alerts within 2 minutes). Memory alert
fires because retry logic accumulates state (3 alerts).
Engineer has 11 simultaneous alerts to triage. Team B:
One burn rate alert fires. "Error budget consuming at
50x rate. Current error rate: 5%. P99 latency: 1.2s.
Runbook: [link]." Engineer has one alert with context.

**THE INSIGHT:**
Team B's alerting system is calibrated to user impact.
It is silent when the service is healthy, even if
internal metrics are high. It fires immediately when
users are experiencing failures.

---

### 🧠 Mental Model / Analogy

> Think of a hospital intensive care unit. The monitors
> display dozens of metrics: heart rate, blood pressure,
> oxygen saturation, respiratory rate, temperature.
> The monitors do not alarm when every metric changes.
> They alarm when a metric crosses a threshold that
> indicates patient deterioration. But sophisticated ICU
> systems go further: the alarm is weighted by context.
> A heart rate of 120 in a sleeping patient is alarming.
> A heart rate of 120 in a patient doing physical therapy
> is normal. The alert is correlated to the patient's
> clinical state, not just the raw number.

SLO burn rate alerts are the clinical state equivalent:
they fire based on the rate at which the patient is
deteriorating relative to their baseline (the error
budget), not just when a single metric is elevated.

**Where this breaks down:** Medical alarms require humans
to interpret clinical context. SLO burn rate alerts
automate this context by building the baseline (SLO)
and the deterioration rate (burn rate) into the alert
formula. The analogy captures the philosophy but the
implementation is more mathematical.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone):**
Alerting sends a notification when something is wrong.
Good alerting only sends the notification when users are
actually experiencing problems - not just when a server
is busy.

**Level 2 - How to use it (junior developer):**
Write Prometheus alert rules that fire when the error
rate exceeds the SLO threshold. Use `for: 5m` to avoid
alerting on transient spikes. Every alert should have
a runbook URL in its annotations.

**Level 3 - How it works (mid-level):**
A Prometheus alert rule evaluates a PromQL expression
every evaluation interval (default 15s). When the
expression evaluates to true for the duration in `for:`,
the alert transitions from `pending` to `firing`.
Alertmanager routes firing alerts to PagerDuty/Slack,
applies deduplication, grouping, and inhibition rules.

**Level 4 - Why it matters (senior/staff):**
The most important alerting design decision is: symptom
vs cause. Symptom alerts (error rate, latency) directly
measure user impact. Cause alerts (CPU, memory, disk)
measure system conditions that may or may not affect
users. The key insight: SLO burn rate alerts are the
most precise symptom alerts because they measure the
rate of user impact relative to the defined tolerance
(error budget). A 1% error rate on a 99.9% SLO is a
crisis. A 1% error rate on a 95% SLO is well within
budget.

**Level 5 - Mastery (distinguished engineer):**
The multiwindow burn rate alert is the production-grade
approach. Using two windows simultaneously - short (1h
or 5m) for fast detection and long (6h or 3h) for
confirmation - prevents both missed alerts (slow window
catches persistent problems) and false positives (fast
window must be confirmed by the long window). The
Google SRE Workbook specifies exact thresholds: for
a 99.9% SLO, use burn_rate > 14.4 for 1h (fast) AND
burn_rate > 3 for 6h (slow). These numbers derive from
the maximum budget consumption that triggers an
immediate page vs a slower ticket.

---

### ⚙️ How It Works (Mechanism)

**PROMETHEUS ALERTING PIPELINE:**

```
[PromQL Expression evaluated every 15s]
  rate(errors[5m]) / rate(requests[5m]) > 0.001 * 14.4
        ↓
[Alert state machine]
  inactive → pending (condition becomes true)
  pending → firing (condition true for `for: 5m`)
  firing → resolved (condition false)
        ↓
[Alertmanager receives firing alert]
  Deduplication: group identical alerts
  Routing: match labels to routes (slack vs pagerduty)
  Inhibition: silence child alerts if parent fires
  Grouping: combine related alerts into one notification
        ↓
[Notification sent]
  PagerDuty: creates incident, pages on-call
  Slack: posts to #incidents channel
  Email: low-priority ticket (non-urgent)
        ↓
[On-call engineer receives page]
  Context: alert name, current metric value,
           severity, runbook URL, trace/log links
```

**BURN RATE FORMULA:**
```
# Error budget burn rate over window W
burn_rate(W) = (
  error_rate(W) / (1 - slo_target)
)

# Example: SLO = 99.9%, current error rate = 0.05 (5%)
burn_rate = 0.05 / (1 - 0.999) = 0.05 / 0.001 = 50x

# At 50x burn rate: budget exhausted in
# 43.2min / 50 = 0.86 min ← CRITICAL
```

---

### 🔄 The Complete Picture - End-to-End Flow

**FROM METRIC TO PAGERDUTY PAGE:**

```
[Checkout service: payment failures spike to 5%]
        ↓
[Prometheus collects SLI metric every 15s]
  checkout_errors_total / checkout_requests_total
  = 0.05 (5% error rate)
        ↓
[Alert rule evaluates burn rate]
  burn_rate = 0.05 / 0.001 = 50x
  Threshold: > 14.4 for 5 min → FIRING
        ↓
[SRE team ← YOU ARE HERE: Alertmanager routes alert]
  severity=page → PagerDuty
  Grouping: all checkout alerts combined into 1
        ↓
[PagerDuty pages on-call engineer]
  Alert: "CheckoutSLOFastBurn"
  Value: burn_rate=50 (exhausts budget in <1min)
  Runbook: https://wiki/runbooks/checkout-slo
  Logs: https://grafana/d/checkout?error=true
  Trace: https://jaeger?service=checkout&error=true
        ↓
[Engineer opens runbook, begins investigation]
  Step 1: check trace for most recent errors
  Step 2: identify failing payment method
  Step 3: check payment service health
  → Root cause: payment service certificate expired
```

**WHAT CHANGES AT SCALE:**
At scale (50+ services), alert routing becomes critical.
Service teams must own their alerts. Each team's alerts
route to their own PagerDuty schedule. A cross-service
incident (multiple services degraded) requires alert
correlation: when checkout fires, the alerting system
should check if payment fired first (payment is likely
the root cause). Alertmanager inhibition rules implement
this: if `payment` is firing, inhibit `checkout` alert.

---

### 💻 Code Example

**Example 1 - BAD: Threshold-based CPU alert:**

```yaml
# BAD: threshold alert on a cause metric.
# CPU at 81% does not mean users are affected.
# This fires regularly during normal traffic spikes.
# It does not tell the engineer what to do.
# It will cause alert fatigue.
groups:
- name: bad-alerts
  rules:
  - alert: HighCPU
    expr: cpu_usage_percent > 80
    for: 5m
    annotations:
      summary: "CPU is high"
      # What should the engineer do? Unknown.
      # Is this causing user impact? Unknown.
```

**Example 2 - GOOD: SLO burn rate alert:**

```yaml
# GOOD: symptom alert on user-visible error rate.
# Only fires when users are experiencing failures
# at a rate that threatens the error budget.
# Includes context for fast diagnosis.
groups:
- name: checkout-slo
  rules:
  # Page immediately: fast burn (5x for 5min window)
  - alert: CheckoutSLOFastBurn
    expr: |
      (
        sum(rate(checkout_requests_total{
          status!~"2.."}[1h]))
        / sum(rate(checkout_requests_total[1h]))
      ) / (1 - 0.999) > 14.4
    for: 5m
    labels:
      severity: page
      service: checkout
      team: payments
    annotations:
      summary: >-
        Checkout error budget burning at
        {{ $value | humanize }}x rate
      description: >-
        At this burn rate, monthly error budget
        exhausted in {{ printf "%.1f" (43.2 / $value) }}
        minutes.
      runbook: "https://wiki/runbooks/checkout-slo"
      dashboard: "https://grafana/d/checkout"

  # Ticket: slow burn (3x for 30min - budget at risk)
  - alert: CheckoutSLOSlowBurn
    expr: |
      (
        sum(rate(checkout_requests_total{
          status!~"2.."}[6h]))
        / sum(rate(checkout_requests_total[6h]))
      ) / (1 - 0.999) > 3
    for: 30m
    labels:
      severity: ticket
      service: checkout
    annotations:
      summary: "Checkout error budget burn rate elevated"
      description: >-
        Budget burning at {{ $value | humanize }}x.
        Review before budget is exhausted.
```

**Example 3 - Multiwindow burn rate alert (best practice):**

```yaml
# BEST PRACTICE: dual window (short AND long window)
# Prevents false positives (single spike) while
# ensuring persistent problems are caught
- alert: CheckoutSLOBurnRatePage
  expr: |
    # Both windows must exceed threshold simultaneously
    (
      sum(rate(checkout_requests_total{
        status!~"2.."}[1h]))
      / sum(rate(checkout_requests_total[1h]))
    ) / (1 - 0.999) > 14.4
    and
    (
      sum(rate(checkout_requests_total{
        status!~"2.."}[5m]))
      / sum(rate(checkout_requests_total[5m]))
    ) / (1 - 0.999) > 14.4
  for: 2m
  labels:
    severity: page
```

---

### ⚖️ Comparison Table

| Alert approach | Precision | Recall | Alert fatigue | Complexity | Best For |
|---|---|---|---|---|---|
| **SLO burn rate** | High | High | Low | High | Production SLOs with metrics |
| Threshold (cause) | Low | Medium | High | Low | Simple systems, getting started |
| Threshold (symptom) | Medium | Medium | Medium | Low | No SLO instrumentation |
| Anomaly detection | Medium | Medium | Medium | High | Dynamic baselines |
| Composite (AND conditions) | High | Medium | Low | Medium | Correlated conditions |

**Alert routing tools:**

| Tool | Strengths | Weaknesses |
|---|---|---|
| **Alertmanager** | Prometheus native, open source | Complex config, no mobile app |
| **PagerDuty** | Best on-call scheduling, escalations | Expensive at scale |
| **OpsGenie** | Flexible routing, good mobile | Less feature-rich than PD |
| **Grafana Alerting** | Unified UI, multi-datasource | Newer, less mature |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "More alerts = better monitoring" | More alerts = more alert fatigue = real alerts ignored. Each alert added must justify its existence by having a clear response action and a non-zero historical firing rate on real incidents. |
| "Every alert should page on-call" | Only page on-call for alerts that require immediate human action (within 15 minutes). Slow burns, predicted issues, and informational alerts belong in Slack or ticketing systems. |
| "Alerting on error count is equivalent to error rate" | A count of 100 errors/minute means nothing without context. Is that 100 out of 100 requests (100% error rate) or 100 out of 1,000,000 (0.01%)? Always alert on error rate relative to SLO. |
| "Silence noisy alerts by increasing threshold" | Raising the threshold masks the signal. The correct response to a noisy alert is: either fix the underlying condition causing the false positive, or delete the alert if it has no actionable response. |
| "Alert on all 5xx errors" | A single 5xx is not an alert. Set an appropriate `for: duration` to require the condition to persist. A 30-second spike might resolve itself; sustained degradation for 5 minutes is actionable. |
| "Flapping alerts can be ignored" | Flapping alerts indicate an unstable system or an improperly tuned alert. Investigate the cause. Flapping alerts that are silenced train engineers to ignore all alerts. |

---

### 🚨 Failure Modes & Diagnosis

**Alert fatigue causing missed production incident**

**Symptom:**
A payment processing failure affects 15% of users for
45 minutes on a Friday evening. The on-call engineer
was not paged. Post-mortem review finds the alert fired
(alert #47 that day) but the engineer had set their
phone to Do Not Disturb after alert #20.

**Root Cause:**
46 non-urgent alerts fired earlier in the day. All were
threshold alerts on cause metrics (CPU, memory, disk).
None required immediate action. The engineer learned to
ignore their phone. The real incident alert was missed.

**Diagnostic Command:**
```bash
# Count alerts by severity and firing state
# to measure alert fatigue indicators
curl -s localhost:9093/api/v1/alerts \
  | jq '[.data[]] | group_by(.labels.severity)
    | map({
        severity: .[0].labels.severity,
        count: length
      })'
```

**Fix:**
Audit every alert rule. Apply the rule: "If this alert
fired and the on-call engineer investigated and found
no user impact, delete this alert." Keep only alerts
with clear actionable responses and demonstrated history
of representing real user impact.

**Prevention:**
Track alert-to-incident ratio monthly. Target: < 3:1.
Review and prune alerts quarterly. No alert may be added
without: (1) an actionable response in the runbook,
(2) evidence it fires only on real user impact.

---

**Alert routing misconfiguration causing silent failure**

**Symptom:**
An incident occurs. No one is paged. Engineers discover
the incident from user complaints 2 hours later.
Alertmanager shows the alert as "firing" but it was
never delivered to PagerDuty.

**Root Cause:**
An Alertmanager routing rule has a match condition
that does not match the alert labels. The alert falls
through to a default route that sends to a Slack
channel no one monitors on evenings.

**Diagnostic Command:**
```bash
# Test routing using alertmanager routing debugger
amtool alert add \
  alertname=TestAlert \
  severity=page \
  service=checkout \
  --alertmanager.url=http://alertmanager:9093

# Check which route the alert was routed to
amtool config routes test \
  --verify.receivers=pagerduty-checkout \
  severity=page \
  service=checkout
```

**Fix:**
Add a catch-all route that sends all unrouted alerts
to a dead letter queue and generates a meta-alert.
Test routing rules with `amtool config routes test`
before deploying.

**Prevention:**
Maintain an alerting test suite: send synthetic alerts
for each severity/service combination and verify the
correct receiver is triggered.

---

**SLO burn rate alert miscalculation causing no alert on incident**

**Symptom:**
Error rate spikes to 3% for 20 minutes (a real incident
affecting users). No alert fires. Engineers discover
the incident from user support tickets.

**Root Cause:**
The burn rate alert uses `rate(errors[1h])`. A 20-minute
spike at 3% errors is diluted by 40 minutes of clean
traffic in the 1-hour window. The effective error rate
measured by the alert is: `(3% x 20min + 0% x 40min) /
60min = 1%`. The calculated burn rate is `1% / 0.1% = 10`.
The alert threshold is `14.4`. Alert does not fire.

**Diagnostic Command:**
```promql
# Compare short window vs long window burn rate
# to see the dilution effect
(sum(rate(errors[5m])) / sum(rate(requests[5m])))
  / 0.001          # short window: catches spike

(sum(rate(errors[1h])) / sum(rate(requests[1h])))
  / 0.001          # long window: dilutes spike
```

**Fix:**
Use the multiwindow approach: add a 5-minute short
window alert alongside the 1-hour alert. The 5-minute
window catches sharp spikes that are diluted in the
1-hour window.

**Prevention:**
Implement the dual-window burn rate alert pattern.
Use 5m and 1h windows simultaneously (both must fire).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Monitoring vs Observability` - alerting is the
  action layer of monitoring; understanding the
  distinction frames why symptom alerting is superior
- `SRE What It Is` - SLO-based alerting is a core SRE
  practice; error budget context is required to
  understand burn rate thresholds
- `Metrics Types` - burn rate alerts require counter
  metrics with `rate()` queries and correct histogram
  configuration for latency SLOs

**Builds On This (learn these next):**
- `SLI and SLO Fundamentals` - burn rate is calculated
  from the SLO target and current SLI value
- `On-Call Management and Incident Response` - alerting
  is the entry point to the incident response lifecycle
- `Runbooks and Playbooks` - every alert must link to
  a runbook describing the response procedure

**Alternatives / Comparisons:**
- `Anomaly Detection Alerting` - ML-based alerting can
  detect unusual patterns without predefined thresholds,
  useful for metrics without clear SLOs

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CORE RULE    │ Alert on symptoms (user impact), not      │
│              │ causes (CPU, disk). Page only if urgent   │
│              │ and actionable.                           │
├──────────────┼───────────────────────────────────────────┤
│ BURN RATE    │ burn = error_rate / (1 - slo_target)      │
│ FORMULA      │ burn > 1 = exhausting budget over time    │
│              │ burn > 14.4 = budget gone in <1 day       │
├──────────────┼───────────────────────────────────────────┤
│ PAGE WHEN    │ burn_rate > 14.4 (1h window) + 5m window  │
│              │ burn_rate > 3 (6h window) + 30m for:      │
├──────────────┼───────────────────────────────────────────┤
│ TICKET WHEN  │ burn_rate > 1 (sustained, budget at risk) │
│              │ or cause metric approaching threshold     │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ CPU > 80% → page. Error count > 10 → page │
│              │ These cause alert fatigue.                │
├──────────────┼───────────────────────────────────────────┤
│ GOOD ALERT   │ Must have: (1) runbook link,              │
│ ANATOMY      │ (2) current metric value in description,  │
│              │ (3) clear owner (team label)              │
├──────────────┼───────────────────────────────────────────┤
│ DUAL WINDOW  │ Short (1h/5m): detects fast spikes        │
│              │ Long (6h/30m): catches slow degradation   │
├──────────────┼───────────────────────────────────────────┤
│ HEALTH CHECK │ alert-to-incident ratio target: < 3:1     │
│              │ Review and prune alerts quarterly         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ SLI/SLO → Error Budget → On-Call Mgmt    │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Alert on symptoms (error rate, latency) not causes
   (CPU, disk). Users do not experience your CPU usage;
   they experience your error rate and response time.
2. SLO burn rate = error_rate / (1 - SLO target).
   Page when burn rate > 14.4 (fast burn). Ticket when
   burn rate > 3 (slow burn).
3. Every alert must be actionable. If there is no clear
   response in a runbook, the alert should not exist.
   Alert fatigue kills incident response.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Measure what you care about at the top of the stack,
not the conditions that might cause it. You care about
user experience (error rate, latency), not server
resources (CPU, memory). Threshold alerts on resources
are indirect and imprecise proxies for user impact.
SLO-based alerts are direct measurements. This principle
applies to: product metrics (DAU, conversion rate are
better business health indicators than page load time),
security monitoring (failed login rate is a better
attack indicator than firewall rule match count), and
financial systems (transaction failure rate is more
important than queue depth).

**Where else this pattern appears:**
- **Capacity planning** - plan for user-visible metrics
  (requests/second, concurrent users), not server metrics
  (CPU cores, RAM). Server metrics follow from user
  metrics with a known coefficient. Planning in reverse
  (add CPU → assume it handles more users) is imprecise.
- **Financial risk management** - Value at Risk (VaR)
  measures the maximum expected loss at a confidence
  level - a symptom metric. Individual trade position
  limits (like CPU thresholds) are cause metrics.
  Sophisticated risk management uses VaR (symptom),
  not just position limits (cause).

---

### 💡 The Surprising Truth

The most counterintuitive alerting insight: deleting
alerts improves incident detection. This seems backwards
(more alerts = more coverage), but the mechanism is
clear. Each false positive alert desensitises the on-call
engineer. When engineers receive 50 alerts per on-call
shift with a 2% real-incident rate, they begin treating
all alerts as noise. The true incident detection rate
drops to match the engineer's attention level. Deleting
50 false positive alerts and keeping 5 high-signal alerts
increases the probability that the 5 real alerts are
investigated immediately. The paradox: a smaller, higher-
quality alert set improves detection performance more
than a larger, lower-quality one.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **[EXPLAIN]** Given an alert rule that fires on CPU >
   80%, explain why this alert causes alert fatigue and
   rewrite it as an SLO symptom alert for the same service,
   including the PromQL expression, the `for:` duration,
   and a runbook URL annotation.
2. **[DEBUG]** Given a production incident where error
   rate spiked to 3% for 20 minutes but no alert fired,
   diagnose the alerting failure (dilution in the 1h burn
   rate window), calculate the effective burn rate seen
   by the alert rule, and explain how the dual-window
   approach would have caught this incident.
3. **[DECIDE]** For a service with an SLO of 99.5% success
   rate (0.5% error budget), calculate the burn rate
   thresholds for a fast-burn page alert (budget exhausted
   in < 1 hour) and a slow-burn ticket alert (budget at
   risk within 3 days). Write the PromQL expressions for
   both.
4. **[BUILD]** Write complete Alertmanager configuration
   for a checkout service: two alert rules (fast burn
   page + slow burn ticket), routing to PagerDuty for
   `severity=page` and Slack for `severity=ticket`,
   with a 5-minute group_wait and correct inhibition
   so checkout alerts are inhibited when payment fires.
5. **[EXTEND]** Design an alert health monitoring system:
   how do you detect that alerts are misconfigured or
   not routing correctly before they fail during a real
   incident? Describe synthetic alerting tests, alert
   coverage metrics, and how you track alert-to-incident
   ratio over time.

---

### 🧠 Think About This Before We Continue

**Q1.** Your payment service has an SLO of 99.9% success
rate. You are currently consuming 0% of your error budget
(the service is at 99.99% success rate). A senior engineer
suggests removing all alerts entirely since the service
is "too reliable to need monitoring." How do you respond?
What is the difference between the current state and the
SLO target, and what does that difference tell you about
the alert configuration?
*Hint: If the service is at 99.99% and the SLO is 99.9%,
the service has 10x more reliability than required. This
might indicate the SLO is set too low (meaning the
service is over-invested in reliability) OR that current
traffic patterns are not representative of peak load.
The correct response is not to remove alerts but to
review whether the SLO should be raised to 99.99%.*

**Q2.** Design the alerting strategy for a new feature
(A/B test) rolled out to 5% of users. The A/B test
affects only the checkout UI, not the payment backend.
Your checkout service SLO is 99.9%. How do you ensure
that errors from the 5% A/B test variant are reflected
in your SLO measurement and alerts? If the A/B variant
has a 2% error rate, does this breach your SLO? Calculate
the impact on the overall error rate and error budget.
*Hint: 5% of users at 2% error rate = 0.1% errors from
A/B test. 95% of users at 0.01% error rate = ~0.01%
errors from control. Total error rate = ~0.11%. SLO is
99.9% = 0.1% error budget. The A/B test alone is consuming
the entire error budget. Label A/B variant traffic with
`variant=treatment` and alert separately, or the A/B
test error rate will trigger SLO alerts on the baseline.*

**Q3 (TYPE G):** You are the SRE lead for a financial
trading platform with these characteristics: 50,000
trades/second during market open (9:30-16:00 ET), near-
zero traffic outside market hours, SLO of 99.999%
(5.26 minutes downtime/year), regulatory requirement
that all trading failures are investigated within 1 hour.
Design the complete alerting strategy: SLO calculation,
burn rate thresholds, alert routing (including after-hours
escalation), and how you handle the challenge that the
trading window is only 6.5 hours/day. What special
considerations apply to a service with bursty daily
traffic patterns vs steady-state traffic?
*Hint: 99.999% SLO on 5.26 min/year. Daily error budget
= 5.26min/365 = 0.86 seconds/day. During the 6.5-hour
trading window, the entire day's budget is consumed in
6.5 hours. At 50,000 trades/s: a 1-second outage = 50,000
missed trades - severe regulatory and financial impact.
Fast burn threshold needs to be much shorter than the
standard 1-hour window. Consider 5-minute windows.*

---

### 🎯 Interview Deep-Dive

**Q1: "Explain the difference between alerting on symptoms
vs alerting on causes. Give an example of each."**
*Why they ask:* Tests understanding of alert design
philosophy. Alert fatigue is one of the most common
SRE problems.
*Strong answer includes:*
- Cause alert: CPU > 80%, disk > 85%, memory > 75%.
  These measure internal conditions. They may or may
  not affect users. They cause alert fatigue.
- Symptom alert: error rate > 0.1% for 5 minutes.
  This measures user-visible impact directly. If it
  fires, users are experiencing failures.
- Best practice: cause metrics belong on dashboards for
  context during incident response. They should not
  page on-call at 3 AM.
- Key insight: CPU can be 95% and users can be fine
  (batch job running). Error rate can be 0.01% and
  users are experiencing critical payment failures.
  Symptom > cause always.

**Q2: "What is an SLO burn rate and how do you use it
in an alert rule?"**
*Why they ask:* Tests whether the candidate understands
SLO-based alerting beyond just knowing the term "SLO."
*Strong answer includes:*
- burn_rate = current_error_rate / (1 - slo_target)
- Example: SLO=99.9%, current error rate=5%:
  burn_rate = 0.05 / 0.001 = 50x
- At 50x burn rate: 43.2-minute monthly budget exhausted
  in 43.2/50 = 0.86 minutes
- Alert threshold: burn_rate > 14.4 means budget consumed
  in < 1 day (fires a page). burn_rate > 3 means budget
  consumed in < 10 days (creates a ticket).
- Dual window: use 1h and 5m windows simultaneously.
  5m catches fast spikes; 1h catches sustained degradation.
  Both must fire to trigger the page.

**Q3: "How would you reduce alert fatigue in a system
that is generating 200 alerts per on-call shift with
a 5% real-incident rate?"**
*Why they ask:* Tests practical alert tuning experience.
*Strong answer includes:*
- Step 1: Export all alert firings to a spreadsheet
  for the last 30 days. Label each: real incident or
  not. This data reveals which alerts have low signal.
- Step 2: Delete alerts that have never correlated with
  a real incident (zero historical signal). These are
  pure noise.
- Step 3: Convert cause alerts (CPU, disk) to tickets
  instead of pages. They should not wake the on-call
  engineer at 3 AM.
- Step 4: Replace remaining threshold alerts with SLO
  burn rate alerts. This directly measures user impact.
- Step 5: Set a quarterly alert review cadence.
  Any alert with > 10% false positive rate is reviewed
  and either fixed or deleted.
- Target: < 5 pages per on-call shift, all representing
  real user impact requiring immediate action.
