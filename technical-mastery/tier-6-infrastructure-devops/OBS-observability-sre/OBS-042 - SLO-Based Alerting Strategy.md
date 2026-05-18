---
id: OBS-042
title: SLO-Based Alerting Strategy
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★★
depends_on: OBS-012, OBS-020, OBS-009, OBS-013
used_by: OBS-044, OBS-048, OBS-053
related: OBS-014, OBS-040, OBS-050
tags:
  - observability
  - reliability
  - devops
  - sre
  - advanced
  - concept
  - production
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Mastery"
nav_order: 42
permalink: /technical-mastery/obs/slo-based-alerting-strategy/
---

⚡ TL;DR - SLO-based alerting replaces arbitrary threshold
alerts with burn rate alerts that fire only when error
budget consumption is fast enough to cause an SLO breach

- eliminating alert fatigue while ensuring you are paged
  for every incident that actually matters.

| #042            | Category: Observability & SRE                                                 | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | SLO, Error Budget, Alerting Fundamentals, Prometheus Alerting                 |                 |
| **Used by:**    | Platform Observability Engineering, Formal SLO Theory, SLO Deep Dive          |                 |
| **Related:**    | Actionable Alerting Patterns, SRE Book Core Principles, SLO Trade-off Framing |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An on-call engineer receives 200 alerts per day. 180 of
them resolve automatically within 5 minutes and require
no action. 15 require investigation but are not customer-
impacting. 5 are genuine customer-impacting incidents.
The engineer cannot distinguish genuine incidents from
noise because all 200 alerts look identical: a threshold
was crossed. After 3 months, the engineer has alert fatigue.
They begin ignoring pages because past experience shows
most are noise. One Friday evening, a genuine P1 incident
fires. The engineer dismisses it as noise. 40 minutes later,
the CEO calls. The on-call system has failed.

**THE BREAKING POINT:**
Arbitrary threshold alerting (CPU > 80%, error rate > 5%)
is calibrated to detect symptoms, not to detect events
that will breach the SLO. The result is 40:1 noise-to-signal
ratio. This ratio makes on-call unsustainable and eventually
breaks the on-call engineer's ability to detect real incidents.

**THE INVENTION MOMENT:**
The Google SRE team developed burn rate alerting as the
answer: instead of alerting on absolute metrics, alert
on "how fast is the error budget being consumed?" If the
error budget is being consumed fast enough to exhaust it
before the SLO window ends, that is worth a page. If the
consumption rate is slow enough that the budget will still
be healthy at end of window, it is not worth waking anyone.

**EVOLUTION:**
SLO-based alerting was formalized in the Google SRE
Workbook (2018) in the chapter "Alerting on SLOs." The
approach uses burn rate - the ratio of current error
rate to the maximum sustainable error rate. A burn rate
of 1.0 means the error budget is being consumed exactly
at the rate that would exhaust it in the SLO window.
A burn rate of 14.4 means the budget will be exhausted
in 1/14.4 of the window (5 hours for a 30-day window).
Multi-window, multi-burn-rate alerts (MWMBA) check for
the same high burn rate in two time windows - a short
window catches fast burns quickly, a long window provides
stability against transient spikes.

---

### 📘 Textbook Definition

**SLO-based alerting** (burn rate alerting) is an alerting
strategy where alert thresholds are derived from SLO math
rather than arbitrary metric thresholds. A **burn rate**
is the ratio between the current error rate and the maximum
sustained error rate that would exactly exhaust the error
budget at the end of the SLO window:

$$\text{burn rate} = \frac{\text{current error rate}}{\text{error budget rate}}$$

where the error budget rate = (1 - SLO target) / window.
**Multi-window multi-burn-rate (MWMBA) alerts** combine
a fast short-window check (detect onset of high burn quickly)
with a slow long-window check (confirm the burn is sustained,
not a transient spike), reducing both false negative and
false positive rates.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Burn rate alerting fires when errors are accumulating
fast enough to exhaust your SLO budget before the window
ends - no more, no less.

**One analogy:**

> Burn rate alerting is like a car's fuel consumption
> warning system - but smarter than a simple "low fuel"
> light. Instead of alerting when the tank is at 10%
> (threshold alerting), it alerts when you are burning
> fuel fast enough that you will run out before reaching
> your destination (burn rate alerting). At 60mph with
> 100 miles to destination and 5 gallons remaining (7
> mpg car), you have exactly enough. If you suddenly
> start burning at 3mpg (40% more load on engine), the
> burn rate alert fires immediately - not when you are
> already on empty.

**One insight:**
The fundamental insight is that the right question is not
"is my error rate above threshold X?" but "at this current
error rate, will I run out of error budget before this
SLO window closes?" These two questions produce very
different alert strategies. The first produces false alarms
on transient spikes that don't affect user experience.
The second produces actionable alerts calibrated to actual
user-observable reliability degradation.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Error budget is a finite resource in a time window;
   burning it too fast is the event worth detecting
2. Alert precision (signal-to-noise ratio) and recall
   (catching all real incidents) are in tension - burn
   rate calibration determines the operating point on
   this curve
3. A short time window detects fast burns quickly but
   is noisy (transient spikes look like fast burns);
   a long time window is stable but slow to detect
4. The 5% budget-consumption threshold for a page is
   the commonly cited practical calibration: alert when
   a fast burn would consume 5% of the monthly budget
   if sustained for 1 hour

**BURN RATE MATH:**

For SLO = 99.9% (0.1% error budget), 30-day window:

- Error budget = 0.1% = 1 minute per 16.67 hours
- Budget per hour = 0.1% / (30 \* 24) = 0.000139%/hour
- Alert threshold: burn fast enough to consume 5% in 1 hour
- Required burn rate: 5% budget / 1 hour / 0.000139%/hour
  = **burn rate of 14.4**
- Burn rate 14.4 = error rate of 14.4 \* 0.1% = **1.44%**

This means: if the error rate exceeds 1.44% sustained
for 1 hour, that will consume 5% of the monthly error
budget - trigger a page.

**THE TRADE-OFFS:**

**Gain:** Near-zero false positive rate (only fires for
budget-threatening events); complete recall (every budget-
threatening event triggers a page); directly calibrated
to user-observable SLO impact.

**Cost:** Requires SLOs to be defined and measured;
more complex alert math than threshold alerts; burn rate
calibration requires understanding the SLO parameters.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Any alerting system that aims to wake
on-call engineers only for events that actually matter
must calibrate to the definition of "what matters" - which
is SLO impact, not metric threshold.

**Accidental:** Complex multi-alert trees with 50 threshold
alerts trying to approximate SLO impact without the math.

---

### 🧪 Thought Experiment

**SETUP:**
Your service has a 99.9% availability SLO over 30 days.
Two scenarios:

**Scenario A**: Error rate spikes to 20% for exactly 5 minutes.
Budget impact: 5 min _ 20% = 1 minute of errors consumed.
Total budget: 30 days _ 24h _ 60min _ 0.1% = 43.2 minutes.
Budget consumed: 1/43.2 = 2.3% of monthly budget.
Should this page? NO - it consumed 2.3% of budget.
Burn rate over 1 hour: 12 min (5 min _ 20% _ 12x) would be
projected if sustained, but it only lasted 5 min.
Short window (1h) check: too much noise from transient spikes.

**Scenario B**: Error rate sits at 2% for 6 hours.
Budget impact: 6 _ 60min _ 2% = 7.2 minutes of errors.
Budget consumed: 7.2/43.2 = 16.7% of monthly budget.
Should this page? YES - this is a material budget drain.
Burn rate: 2% / 0.1% = 20 (burning 20x the sustainable rate).

**THE MULTI-WINDOW ANSWER:**
A 1-hour window (short) checks: is burn rate > 14.4?
Scenario A: brief spike may briefly show high burn rate
in 1h window - but the 5-minute spike over 60 minutes
averages to: (5min _ 20% + 55min _ 0%) / 60min = 1.7%.
Burn rate: 1.7% / 0.1% = 17. Exceeds 14.4. Fires.
This is a false positive from a 5-minute spike.

The 5-minute window (very short) check: if sustained for
1h at this rate, would budget be consumed by >2%?
Scenario A: 5-min window shows 20% - burn rate 200.
But the long window (6h) shows: averaged 0.28%.
Multi-window: BOTH short AND long must exceed threshold.
Scenario A: 6h window = very low. Does NOT fire. Correct.
Scenario B: 1h window = 2% (burn rate 20). 6h window =
2% sustained (burn rate 20). Both fire. Pages. Correct.

---

### 🧠 Mental Model / Analogy

> SLO-based alerting is like a pilot's fuel warning
> system designed by an SRE. The naive system warns when
> fuel is below 10% (threshold alert). The SRE-designed
> system warns when fuel consumption rate will exhaust
> the remaining fuel before landing (burn rate alert).
> It uses two windows: a 5-minute fuel flow sensor to
> detect sudden fuel leaks quickly, and a 30-minute moving
> average to confirm the high consumption is sustained
> (not a brief climb-rate spike). The 5-minute sensor
> alone would trigger on any steep climb. The combination
> of 5-minute high AND 30-minute high is the signal
> that a genuine fuel emergency is underway.

Element mapping:

- "Fuel" → error budget
- "10% fuel warning" → threshold alerting
- "Fuel flow rate" → burn rate
- "5-minute fuel sensor" → short time window check
- "30-minute moving average" → long time window check
- "Both high" → multi-window multi-burn-rate alert logic

Where this analogy breaks down: aircraft fuel consumption
is physical; SLO burn rate is a statistical measure across
a fleet of requests. A single catastrophic failure mode
(aircraft engine stops) has no equivalent nuance - in
software, brief spikes are common and the multi-window
approach specifically handles this.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
SLO-based alerting means you only get paged when errors
are happening fast enough to actually break your service's
reliability goal. If errors are minor or brief, no page.
If errors are serious and sustained, you get paged.

**Level 2 - How to use it (junior developer):**
Implement the alerts in your Prometheus Alertmanager
configuration. Instead of `error_rate > 0.05`, use
`burn_rate > 14.4`. The burn_rate metric is computed
from your error rate divided by your error budget rate.
Use the Pyrra or Sloth tools to auto-generate the
Prometheus alerting rules from your SLO definition.

**Level 3 - How it works (mid-level engineer):**
A 30-day 99.9% SLO has an error budget of 43.2 minutes.
At burn rate 1.0, it takes 30 days to exhaust. At burn
rate 14.4, it takes 2 days. The MWMBA approach:

- Page-worthy (P1): burn rate > 14.4 in both 1h and 5min
  windows (will exhaust 5% budget in 1 hour)
- Warning (P2): burn rate > 6 in both 6h and 30min windows
  (will exhaust 5% budget in 5 hours)
- Info/ticket: burn rate > 3 over 3 days (slow drain worth
  tracking but not paging)

**Level 4 - Why it was designed this way (senior/staff):**
The 5% threshold was chosen because it represents roughly
1 page-worthy event per week for a service at 99.9% SLO.
If you page at 1% budget consumption, you page 100 times
per monthly window - too noisy. If you page at 50% budget
consumption, you miss half of all significant incidents.
5% is the calibration point that produces ~1 page per
incident and catches all incidents that materially threaten
the SLO. The multi-window requirement (both short AND long
window) is the deduplication mechanism: it ensures that
a 5-minute spike (which has a high instantaneous burn rate)
does not fire a page unless the burn is also elevated in
the longer window, confirming it is sustained.

**Level 5 - Mastery (distinguished engineer):**
Multi-window burn rate alerting trades alert latency for
precision. A page for a catastrophic failure (100% error
rate, burn rate 1000) should fire in seconds, not after
a 6-hour window confirms it. The MWMBA approach is
designed for this: the short window (1 minute, 5 minutes)
catches fast burns immediately; the long window (1 hour,
6 hours) filters transient spikes. The burn rate threshold
for the short window is set higher (14.4x) than for the
long window (6x) to compensate for the higher noise
level in short windows. This creates a two-level alert
system: urgent (short + high threshold = fast catastrophic
failure) and warning (long + lower threshold = slow sustained
degradation). Both are calibrated to budget impact, not
to arbitrary metric values.

---

### ⚙️ How It Works (Mechanism)

**BURN RATE CALCULATION:**

For SLO = 99.9%, 30-day window:

```
Error budget = 1 - 0.999 = 0.001 (0.1%)

Burn rate = (current error rate) / (error budget rate)
          = (current error rate) / 0.001

Example: error rate = 2% = 0.02
Burn rate = 0.02 / 0.001 = 20

Meaning: at 2% error rate, error budget will be
exhausted in 30 days / 20 = 1.5 days
```

**ALERT THRESHOLDS (GOOGLE SRE WORKBOOK):**

```
┌────────────────────────────────────────────────────────┐
│           MWMBA ALERT TIER CONFIGURATION              │
├──────────────┬──────────────┬──────────────┬──────────┤
│ Alert Tier   │ Burn Rate    │ Windows      │ Pct Used │
├──────────────┼──────────────┼──────────────┼──────────┤
│ PAGE (P1)    │ > 14.4       │ 1h AND 5min  │ 5% in 1h │
├──────────────┼──────────────┼──────────────┼──────────┤
│ WARN (P2)   │ > 6          │ 6h AND 30min │ 5% in 5h │
├──────────────┼──────────────┼──────────────┼──────────┤
│ INFO/TICKET  │ > 3          │ 3d AND 6h    │ 10% in 3d│
└──────────────┴──────────────┴──────────────┴──────────┘

For SLO = 99.9%, error budget rate = 0.1%:
  PAGE fires when error rate > 14.4 * 0.1% = 1.44%
       sustained for BOTH 5-min AND 1-hour windows
  WARN fires when error rate > 6 * 0.1% = 0.6%
       sustained for BOTH 30-min AND 6-hour windows
```

---

### 🔄 The Complete Picture - End-to-End Flow

**ALERT LIFECYCLE:**

```
Service emitting errors at 2% rate (burn rate 20)
   │
   ↓
Prometheus scrapes error_rate metric every 15s
   │
   ↓
Burn rate recording rule computes:
  burn_rate_5m = error_rate{window="5m"} / 0.001
  burn_rate_1h = error_rate{window="1h"} / 0.001
   │
   ↓
P1 alert rule evaluates:
  burn_rate_5m > 14.4 AND burn_rate_1h > 14.4
  → 2% / 0.1% = 20 > 14.4 → BOTH conditions TRUE
   │
   ↓
Alert fires → PagerDuty → on-call engineer paged
   │
   ↓
Engineer investigates in Grafana:
  - Error budget dashboard: 30% consumed in 2 hours
  - Trace view: 2% of requests returning 500
  - Log view: DB connection timeout errors
   │
   ↓
Incident resolved → error rate drops to 0%
  → Burn rate drops to 0
  → Alert resolves
   │
   ↓
Postmortem documents budget consumed (X%)
  and action items to prevent recurrence
```

**WHAT CHANGES AT SCALE:**
At 500 services, each with 2-3 SLOs, you have 1,000-1,500
burn rate alert rules. Managing these manually is not
scalable. Tools like **Pyrra** and **Sloth** take SLO
definitions in YAML and automatically generate the
Prometheus recording rules and alerting rules. This
ensures consistency across all services and reduces
the operational overhead of maintaining alert configs.

---

### 💻 Code Example

**Example 1 - BAD: threshold alerting**

```yaml
# BAD: arbitrary threshold alerting
# Fires on transient spikes, misses slow burns
# 40:1 noise-to-signal ratio typical result
- alert: HighErrorRate
  expr: >
    rate(http_requests_total{status=~"5.."}[5m]) /
    rate(http_requests_total[5m]) > 0.05
  for: 1m
  # Problem: a 30-second spike at 6% fires this alert
  # 30-second spikes are common, rarely SLO-threatening
  # A slow 1.5% sustained burn over 6 hours never fires
  # despite consuming 20% of monthly error budget
```

**Example 2 - GOOD: multi-window burn rate alerting**

```yaml
# GOOD: SLO-based burn rate alerting
# SLO: 99.9% availability, 30-day window
# Error budget rate: 0.001 (0.1%)

# Step 1: Recording rules (compute burn rates)
groups:
  - name: slo.recording_rules
    rules:
      - record: job:slo_error_rate:ratio_rate5m
        expr: >
          rate(http_requests_total{
            job="payment-api",status=~"5.."
          }[5m])
          /
          rate(http_requests_total{
            job="payment-api"
          }[5m])

      - record: job:slo_error_rate:ratio_rate1h
        expr: >
          rate(http_requests_total{
            job="payment-api",status=~"5.."
          }[1h])
          /
          rate(http_requests_total{
            job="payment-api"
          }[1h])

      - record: job:slo_error_rate:ratio_rate6h
        expr: >
          rate(http_requests_total{
            job="payment-api",status=~"5.."
          }[6h])
          /
          rate(http_requests_total{
            job="payment-api"
          }[6h])

  - name: slo.alerting_rules
    rules:
      # P1: Page - fast burn (>14.4x) in short windows
      - alert: PaymentAPIHighBurnRate
        expr: >
          job:slo_error_rate:ratio_rate5m{
            job="payment-api"
          } > (14.4 * 0.001)
          and
          job:slo_error_rate:ratio_rate1h{
            job="payment-api"
          } > (14.4 * 0.001)
        for: 2m
        labels:
          severity: page
          slo: availability
        annotations:
          summary: >
            Payment API burning error budget fast
          description: >
            Burn rate {{ $value | humanize }}x
            (SLO: 99.9%, threshold: 14.4x)
            Will exhaust monthly budget in
            {{ div 1 (mul $value 0.001) | humanize }}h

      # P2: Warning - slower sustained burn
      - alert: PaymentAPISlowBurnRate
        expr: >
          job:slo_error_rate:ratio_rate6h{
            job="payment-api"
          } > (6 * 0.001)
          and
          job:slo_error_rate:ratio_rate30m{
            job="payment-api"
          } > (6 * 0.001)
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: >
            Payment API slowly consuming error budget
```

**Example 3 - Pyrra SLO definition (auto-generates alerts)**

```yaml
# pyrra-slo.yaml - auto-generates all alerting rules
apiVersion: pyrra.dev/v1alpha1
kind: ServiceLevelObjective
metadata:
  name: payment-api-availability
  namespace: monitoring
spec:
  description: "99.9% of payment API requests succeed"
  target: "99.9"
  window: 30d
  indicator:
    ratio:
      errors:
        metric: >
          http_requests_total{
            job="payment-api",
            status=~"5.."
          }
      total:
        metric: >
          http_requests_total{
            job="payment-api"
          }

# Pyrra generates recording rules and all MWMBA alerts
# automatically from this single YAML definition
```

**How to test / verify correctness:**
Inject artificial errors: configure a route to return 500
for 2% of requests. Verify that the burn rate recording
rules reflect the 2% error rate within 2 scrape intervals.
Verify that the P1 alert fires within 2-5 minutes (the 5min
window must fill with the elevated rate before alerting).
Inject a brief 30-second spike at 20% error rate. Verify
that NO alert fires (the 1-hour window does not reach the
threshold from a 30-second spike, preventing false positive).

---

### ⚖️ Comparison Table

| Alerting Strategy       | Noise    | Recall    | Calibration | Best For                     |
| ----------------------- | -------- | --------- | ----------- | ---------------------------- |
| **Burn rate (MWMBA)**   | Very low | High      | SLO-driven  | Production on-call           |
| Threshold alerting      | High     | Medium    | Ad hoc      | Simple systems               |
| Anomaly detection       | Medium   | Very high | ML model    | Unpredictable workloads      |
| Composite alerts        | Medium   | Medium    | Complex     | Specific known failure modes |
| No alerts (ticket only) | None     | Low       | N/A         | Non-production environments  |

**How to choose:**
Use MWMBA burn rate alerting as the primary alerting strategy
for all production services with defined SLOs. Use threshold
alerting as a supplement for specific known failure modes
that do not affect the SLO directly but indicate upstream
risk (e.g., disk > 80% is not in the SLO but predicts
future SLO impact). Avoid anomaly detection for on-call
pages - its high recall produces too many false positives.

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                                                                                   |
| ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Burn rate alerting requires complex tooling          | The math is 3-4 Prometheus recording rules; tools like Pyrra/Sloth auto-generate them from a YAML SLO definition                                          |
| A high burn rate always requires immediate action    | A burn rate of 15 that lasts 30 seconds is not actionable; the `for:` duration in Prometheus ensures the condition must persist                           |
| MWMBA only works with Prometheus                     | The same approach works with Datadog SLO monitors, Grafana Alerting, and any alerting system that supports multiple time windows                          |
| SLO-based alerting replaces all other alerts         | Burn rate alerts cover SLO-impact events; you still need process-level alerts (OOM, disk full) that predict SLO impact but are not captured by error rate |
| Lower burn rate threshold = more thorough monitoring | Lower thresholds increase false positives and alert fatigue; the 14.4/6 calibration from the SRE Workbook is empirically derived                          |

---

### 🚨 Failure Modes & Diagnosis

**Burn Rate Alert Never Fires During Incident**

**Symptom:**
A P1 incident occurs. Error rate reaches 5% for 2 hours.
Users report widespread failures. No burn rate alert fired.
The incident was detected only when the CEO escalated.

**Root Cause:**
The burn rate recording rule was computing error rate
from a metric that excludes a specific error type (e.g.,
network timeouts counted separately from HTTP 5xx). The
SLI definition and the alert expression were misaligned.
The 5% error rate was visible in a different metric not
included in the alert computation.

**Diagnostic Questions:**

- Do the SLI metrics in the alert expression cover all
  failure modes the users experience?
- Is the error_rate recording rule tested with synthetic
  error injection?
- Do end-to-end synthetic transactions from the user's
  perspective validate the SLI?

**Fix:**
Define the SLI from the user's perspective, not from the
service's perspective. Include all failure modes in the
error rate: HTTP 5xx, timeouts, connection refused. Use
blackbox probes (synthetic transactions) as an additional
SLI signal to catch gaps in the instrumentation.

---

**False Positive Storm from Recording Rule Bug**

**Symptom:**
Burn rate P1 alert fires 50 times in one hour. On
investigation, error rate is 0.1% (well below threshold).
The alert is firing and resolving every 2 minutes.

**Root Cause:**
A recording rule has a division-by-zero edge case when
there are no requests in the time window (e.g., during
a maintenance window). `0 / 0` in PromQL evaluates to
NaN, which compares as greater than any threshold.
The alert fires whenever request volume is near-zero.

**Diagnostic Command:**

```promql
# Check if the denominator is near zero
rate(http_requests_total{job="payment-api"}[5m])
# If this shows 0 or very low values, the division
# produces NaN/Inf which triggers alerts spuriously
```

**Fix:**

```promql
# Add a minimum request threshold to the recording rule
rate(http_requests_total{status=~"5.."}[5m]) /
  clamp_min(
    rate(http_requests_total[5m]),
    0.1   # minimum request rate to compute error rate
  )
# Or use if() to return 0 when rate is zero
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `SLO` - the reliability target that burn rate is computed from
- `Error Budget` - the budget being "burned" that triggers alerts
- `Prometheus - Alerting Rules` - the implementation technology
- `Alerting Fundamentals` - the base concepts this builds on

**Builds On This (learn these next):**

- `Platform Observability Engineering` - organizational
  practice of running SLO alerting at scale
- `Formal SLO Theory` - mathematical foundations of
  burn rate calculations
- `Service Level Objectives (SLOs) Deep Dive` - the full
  SLO lifecycle that alerting is part of

**Alternatives / Comparisons:**

- `Actionable Alerting Patterns` - complementary strategies
  for non-SLO operational alerts
- `SRE Book - Core Principles` - the organizational model
  that SLO alerting is designed to support
- `SLO Trade-off Framing` - how to calibrate SLOs and
  thus alert thresholds

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Alerting strategy where thresholds are   │
│              │ derived from SLO math (burn rate) not    │
│              │ arbitrary metric values                  │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Threshold alerts have 40:1 noise ratio; │
│ SOLVES       │ burn rate alerts have near-zero false    │
│              │ positives while catching all SLO threats │
├──────────────┼──────────────────────────────────────────┤
│ KEY FORMULA  │ Burn rate = error_rate / error_budget_rat│
│              │ PAGE when burn rate > 14.4 (5% budget   │
│              │ consumed in 1h) in BOTH 5m and 1h windows│
├──────────────┼──────────────────────────────────────────┤
│ P1 THRESHOLD │ Burn rate > 14.4 in 5m AND 1h windows   │
│ P2 THRESHOLD │ Burn rate > 6 in 30m AND 6h windows     │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Any service with a defined SLO and an   │
│              │ on-call rotation that must be protected  │
│              │ from alert fatigue                       │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Burn rate based on a narrow SLI that    │
│              │ misses important failure modes - always  │
│              │ validate SLI covers all user-visible    │
│              │ failure modes                            │
├──────────────┼──────────────────────────────────────────┤
│ TOOL         │ Pyrra or Sloth for auto-generating       │
│              │ Prometheus rules from SLO YAML           │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Alert when budget burns, not when       │
│              │ thresholds cross."                       │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Formal SLO Theory → SLO Trade-off       │
│              │ Framing → SLO Deep Dive                  │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Burn rate = (error_rate) / (error_budget_rate). P1 threshold
   is 14.4x for a 99.9% SLO, 30-day window. This means
   error rate > 1.44% is page-worthy.
2. Multi-window (MWMBA): both short window (5min/1h) AND
   long window (30min/6h) must exceed threshold. Short window
   catches fast burns quickly; long window filters transient
   spikes.
3. Validate your SLI covers all user-visible failure modes.
   A burn rate alert is only as good as the error metric it
   is computed from.

**Interview one-liner:**
"SLO-based alerting replaces arbitrary threshold alerts with
burn rate alerts: alert when (current error rate / error
budget rate) is high enough that the SLO budget will be
exhausted before the window ends. For a 99.9% SLO over 30
days, error budget rate is 0.1%. Page threshold is burn
rate > 14.4 (>1.44% error rate) in both a 1-hour and 5-minute
window simultaneously. The two-window check filters transient
spikes. This approach produces near-zero false positive rate
while ensuring every SLO-threatening event triggers a page."

> Entry stub. Generate full content using Master Prompt v3.0.
