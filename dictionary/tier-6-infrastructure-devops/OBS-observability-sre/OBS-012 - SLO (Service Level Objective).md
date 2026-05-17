---
id: OBS-012
title: "SLO (Service Level Objective)"
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★☆☆
depends_on: OBS-005, OBS-011
used_by: OBS-013, OBS-020, OBS-009
related: OBS-011, OBS-013, OBS-020
tags:
  - observability
  - reliability
  - foundational
  - first-principles
  - sre
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 12
permalink: /obs/slo-service-level-objective/
---

# OBS-012 - SLO (Service Level Objective)

⚡ TL;DR - An SLO is the internal target threshold for
your SLI - the reliability promise you make to your own
team and to the error budget system, tighter than the
SLA and stricter than "best effort."

| #012            | Category: Observability & SRE            | Difficulty: ★☆☆ |
| :-------------- | :--------------------------------------- | :-------------- |
| **Depends on:** | SRE What It Is, SLI                      |                 |
| **Used by:**    | SLA, Error Budget, Alerting Fundamentals |                 |
| **Related:**    | SLI, SLA, Error Budget                   |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Development and operations teams negotiate reliability
informally. The product manager says "the service must
be highly available." The SRE team says "we do our
best." A new deployment causes 30 minutes of degradation.
The development team says: "30 minutes on a Sunday
night is fine." The SRE team says: "We were paged and
had to roll back - this is unacceptable." The argument
is political because there is no agreed, objective
definition of "acceptable."

**THE INVENTION MOMENT:**
Google SRE practice introduced the SLO as the internal
reliability target: a specific, measurable threshold
for an SLI that the team commits to maintaining.
The SLO converts the political "acceptable vs
unacceptable" debate into a data question: "is the
SLI above or below the SLO target?" This target then
generates an error budget: the allowed "room for
failure" over a time window.

---

### 📘 Textbook Definition

**A Service Level Objective (SLO)** is a target value
or range for an SLI over a specified time window.
It represents the reliability level that the service
team commits to maintaining. SLOs are internal
commitments - not customer-facing contracts (those
are SLAs) - typically set tighter than SLAs to provide
a buffer.

**SLO structure:**

```
SLO: <SLI expression> >= <target> over <window>

Example:
SLO: checkout_availability_sli >= 99.9% over 30 days
```

**Key SLO properties:**

- **Time window:** rolling (last 30 days) or calendar
  (this month). Rolling windows provide consistent
  error budget. Calendar windows align with business
  reporting.
- **Target:** the minimum acceptable SLI value. Not
  aspirational - achievable with current investment.
- **Error budget:** (1 - target) x seconds in window.
  For 99.9% SLO over 30 days: 43.2 minutes of
  allowed downtime.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An SLO is the internal reliability target: "we commit
to 99.9% checkout success rate over 30 days" - not a
contractual promise, but a binding internal engineering
commitment that drives error budget policy.

> Think of a hotel's internal service standard. The
> hotel's published guarantee (SLA) says "rooms ready
> by 3 PM or we give you a discount." The internal
> operations target (SLO) says "rooms ready by 2 PM
> or we escalate to housekeeping supervisor." The
> internal target is tighter to provide a buffer
> against the customer-facing guarantee. If the SLO
> is missed (2 PM), the team acts before the customer-
> facing SLA is breached.

**One insight:**
The most important property of an SLO: it must be set
at the minimum reliability level that keeps users
happy, not the maximum achievable. An SLO set too high
(99.999%) over-invests in reliability and freezes
feature development. An SLO set too low (95%) provides
poor user experience. The correct SLO is the minimum
that users find acceptable.

---

### 🔩 First Principles Explanation

**THE SLO DERIVES THE ERROR BUDGET:**

```
Error budget = (1 - SLO target) x window duration

99.9% SLO over 30 days:
= (1 - 0.999) x 2,592,000 seconds
= 0.001 x 2,592,000
= 2,592 seconds (43.2 minutes)

This means: over 30 days, up to 43.2 minutes of
"bad events" are allowed before the SLO is breached.
```

**WHY THE SLO IS TIGHTER THAN THE SLA:**
If the SLA is 99.5% and the SLO is also 99.5%, the
team has no buffer. Any SLO breach is immediately an
SLA breach - a contractual failure with financial
consequences. By setting the SLO at 99.9% with an SLA
at 99.5%, the SRE team has a 0.4% buffer. They can
breach the SLO (internal warning) without breaching
the SLA (contractual failure). This buffer is the
practical value of the SLO/SLA distinction.

**TRADE-OFFS:**
**SLO set too high (e.g., 99.999%):**

- Error budget = 26 seconds/month
- Every deployment risks breaching the budget
- Development freezes. Velocity drops to near zero.
- Users may not notice the difference from 99.9%

**SLO set too low (e.g., 95%):**

- Error budget = 36 hours/month
- 5% of users experience failures
- Development can ship freely, but user experience suffers
- Business impact: 5% checkout failure rate on a
  high-traffic day = significant lost revenue

**CORRECT SLO:**

- Set at the minimum level where users notice if it
  degrades further
- Validated against user research or business metrics
  (conversion rate drops when latency exceeds X ms)
- Started conservatively (at current measured reliability)
  and raised as the system improves

---

### 🧪 Thought Experiment

**SETUP:**
Your checkout service has measured 99.95% availability
over the last 90 days. The SLA with enterprise customers
is 99.5%. You need to set an SLO.

**THREE OPTIONS:**

**Option A: SLO = 99.5% (match the SLA)**
Error budget = 216 minutes/month. Development can ship
freely but any SLO breach is an SLA breach. No buffer.

**Option B: SLO = 99.95% (match current performance)**
Error budget = 21.6 minutes/month. This is achievable
today. Any regression from current state breaches the
SLO. Alerts fire on any degradation. Good starting point.

**Option C: SLO = 99.999% (aspirational)**
Error budget = 26 seconds/month. Every deployment
is risky. Development freezes entirely.

**RECOMMENDATION:**
Start with Option B (SLO = current measured performance).
This establishes an achievable baseline. After 3 months
of stable SLO compliance, evaluate whether to raise
the SLO or invest the freed budget in features. Never
start with an aspirational SLO that is not achievable
with current infrastructure.

**THE INSIGHT:**
An unachievable SLO is worse than no SLO. It permanently
depletes the error budget, freezes development, and
creates a never-ending reliability crisis.

---

### 🧠 Mental Model / Analogy

> A manufacturing plant runs a quality control process.
> The contractual promise to customers (SLA): "no more
> than 1% defective parts." The internal quality target
> (SLO): "no more than 0.1% defective parts." The
> internal target is tighter because any batch that
> exceeds 0.1% triggers an internal review and process
> improvement before it ever risks breaching the 1%
> customer contract. The gap between 0.1% and 1% is
> the buffer that protects customer relationships.

The SLO is the internal quality gate. The SLA is the
customer commitment. The SLO must be meaningfully
tighter than the SLA to provide a functional buffer.
An SLO equal to the SLA provides no early warning.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone):**
An SLO is a target: "we aim for 99.9% of requests to
succeed this month." If the target is missed, the team
investigates and fixes the problem.

**Level 2 - How to use it (junior developer):**
The SLO is the threshold in the SLO alert rule. Write
a PromQL expression that computes the current SLI.
The SLO defines the threshold where the burn rate
alert fires. The error budget is (1 - SLO) x month.

**Level 3 - How it works (mid-level):**
The SLO drives the error budget policy. When the error
budget is full (SLI > SLO consistently), development
can deploy freely. When the error budget is low (SLI
approaching the SLO), deployments are reviewed. When
the error budget is exhausted (SLI below SLO), all
non-critical deployments are frozen.

**Level 4 - Why it matters (senior/staff):**
SLO calibration is the key engineering art in SRE.
Three inputs: (1) user research - at what latency do
conversion rates drop? (2) competitive benchmarks -
what are comparable services offering? (3) current
measured performance - what is achievable today?
The SLO must be at the intersection: achievable, user-
meaningful, and competitive. Overly tight SLOs destroy
velocity. Overly loose SLOs destroy user experience.

**Level 5 - Mastery (distinguished engineer):**
The advanced SLO debate is multi-window SLOs. A single
30-day SLO allows a burst of failures at the start of
the month that does not breach the monthly SLO. A
multi-window SLO (e.g., 99.9% over 7 days AND 99.95%
over 30 days) prevents this. The short window catches
current incidents; the long window measures sustained
reliability. Staff engineers also recognise that SLOs
must be versioned. As the system improves, SLOs should
be raised. If an SLO is never breached and the error
budget is always full, the SLO is too conservative -
the team is over-investing in reliability relative to
user needs.

---

### ⚙️ How It Works (Mechanism)

**SLO COMPLIANCE CALCULATION:**

```
[Current month: day 15 of 30]

SLO: availability >= 99.9% over 30 days
Monthly error budget: 43.2 minutes

[PromQL: compute SLI over rolling 30d window]
1 - (
  sum(increase(checkout_errors_total[30d]))
  / sum(increase(checkout_requests_total[30d]))
)
= 0.9994 (99.94% - above SLO threshold)

[Error budget consumed]
Allowed errors = 0.001 x total requests in 30d
                = 0.001 x 1,296,000 = 1,296 errors
Actual errors  = 780 errors (60% consumed)
Budget remaining: 516 errors (40% remaining)

[Burn rate (5m window)]
burn_rate = current_error_rate / (1 - 0.999)
          = 0.0005 / 0.001 = 0.5x
            → burning at 0.5x: budget will last
              more than 30 days at this rate
```

**THE THREE SLO STATES:**

```
Budget healthy (> 50% remaining):
  → Deploy freely, accept more risk in features

Budget caution (20-50% remaining):
  → Review deployments, no risky changes

Budget exhausted (< 0% remaining = SLO breached):
  → Freeze all non-critical deployments
  → Focus engineering on reliability improvement
  → No new features until budget is restored
```

---

### 🔄 The Complete Picture - End-to-End Flow

**SLO GOVERNANCE FLOW:**

```
[Month start]
  Error budget: 100% (43.2 min available)
        ↓
[Day 3: deployment causes 5-min degradation]
  Budget consumed: 5/43.2 = 11.6%
  Budget remaining: 88.4%
  State: HEALTHY → Deploy OK
        ↓
[Day 10: incident causes 25-min degradation]
  Budget consumed: 30/43.2 = 69.4%
  Budget remaining: 30.6%
  State: CAUTION → Review deployments
  [SRE team ← YOU ARE HERE: review board triggered]
        ↓
[Day 15: small degradation, 15 min]
  Budget consumed: 45/43.2 = 104%
  SLO BREACHED
  State: FREEZE
  → All feature deployments paused
  → Reliability sprint begins
        ↓
[Day 25: reliability improvements ship]
  Error rate stabilises at 0.05% (5x below SLO)
  Budget begins to recover (rolling 30d window)
        ↓
[Day 30: window resets]
  Budget fully restored for next month
  Post-mortem completed, action items tracked
```

---

### 💻 Code Example

**Example 1 - BAD: Aspirational SLO not based on baseline:**

```yaml
# BAD: SLO of 99.999% on a service currently at 99.5%
# This creates permanent SLO breach from day 1.
# No deployments will ever be possible.
# The team will ignore the SLO within 2 weeks.
slo:
  service: checkout
  target: 0.99999 # aspirational, not measured
  window: 30d
  # Error budget: 26 seconds/month
  # Current performance: 99.5% → ALREADY BREACHED
```

**Example 2 - GOOD: SLO based on measured baseline:**

```yaml
# GOOD: SLO based on measured 90-day baseline
# with buffer below SLA
slo:
  service: checkout
  sli:
    # Good: HTTP 2xx responses
    # Bad: HTTP 5xx responses
    # Excluded: HTTP 4xx (user errors)
    query: |
      sum(rate(checkout_requests_total{
        status=~"2.."}[window]))
      / sum(rate(checkout_requests_total{
        status!~"4.."}[window]))
  target: 0.999 # 99.9% availability
  window: 30d # rolling calendar month
  sla: 0.995 # SLA is 99.5% - SLO provides buffer
  error_budget_policy:
    healthy: "budget > 50%: deploy freely"
    caution: "budget 20-50%: deployment review"
    exhausted: "budget < 0%: freeze + reliability sprint"
```

**Example 3 - Multi-window SLO alert (production grade):**

```yaml
# Multi-window SLO: catches current incidents (fast)
# and sustained degradation (slow)
groups:
  - name: checkout-slo
    rules:
      # Fast burn: 14.4x for 1h window (budget in <1 day)
      - alert: CheckoutSLOFastBurn
        expr: |
          (
            (1 - sum(rate(checkout_requests_total{
              status=~"2.."}[1h]))
            / sum(rate(checkout_requests_total[1h])))
            / (1 - 0.999)
          ) > 14.4
          and
          (
            (1 - sum(rate(checkout_requests_total{
              status=~"2.."}[5m]))
            / sum(rate(checkout_requests_total[5m])))
            / (1 - 0.999)
          ) > 14.4
        labels:
          severity: page
        annotations:
          summary: "Checkout SLO fast burn rate"
```

---

### ⚖️ Comparison Table

| SLO level | Error budget/month | Deployment risk | Typical use                      |
| --------- | ------------------ | --------------- | -------------------------------- |
| 99.0%     | 7.2 hours          | Low             | Internal tools, dev environments |
| 99.5%     | 3.6 hours          | Low-medium      | Non-critical web services        |
| 99.9%     | 43.2 minutes       | Medium          | Standard production APIs         |
| 99.95%    | 21.6 minutes       | Medium-high     | Payment, auth services           |
| 99.99%    | 4.3 minutes        | High            | Critical financial systems       |
| 99.999%   | 26 seconds         | Very high       | Telephone network grade          |

**SLO vs SLA vs SLI:**

| Term    | What it is          | Who sets it        | Consequence of breach                       |
| ------- | ------------------- | ------------------ | ------------------------------------------- |
| **SLI** | Current measurement | SRE team           | No direct consequence (it is just a number) |
| **SLO** | Internal target     | SRE + product team | Error budget depleted, deployment freeze    |
| **SLA** | Customer contract   | Business + legal   | Financial penalty, customer churn           |

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                                                                                           |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "SLO = SLA"                                  | SLOs are internal targets; SLAs are customer contracts. SLOs must be tighter than SLAs to provide buffer. A breach of the SLO is an internal warning; an SLA breach has contractual consequences. |
| "Higher SLO = better service"                | A 99.999% SLO on a service where users are satisfied at 99.9% wastes engineering investment. The right SLO is the minimum that keeps users satisfied.                                             |
| "The SLO should never be breached"           | SLOs are designed to be occasionally breached. The error budget is consumed by incidents and deployments. An SLO that is never breached may be set too conservatively.                            |
| "SLO is set once and never changed"          | SLOs should be reviewed quarterly. If the error budget is always full, the SLO may be too conservative. If it is always exhausted, the team needs to invest in reliability or lower the SLO.      |
| "SLOs are only for customer-facing services" | Internal services (databases, auth systems, data pipelines) benefit from SLOs. Internal service reliability failures cascade to user-visible failures.                                            |
| "100% SLO is the right target"               | 100% SLO is unachievable and costly. It requires eliminating all planned maintenance windows, all deployment downtime, and all test failures. The cost approaches infinity.                       |

---

### 🚨 Failure Modes & Diagnosis

**SLO set without measuring baseline first**

**Symptom:**
The error budget is exhausted on day 1 of the month.
Every month starts with a deployment freeze. The SRE
team and development team are in constant conflict.
Engineers have stopped trusting the SLO system.

**Root Cause:**
The SLO was set aspirationally (99.99%) without first
measuring the current SLI performance (which is 99.5%).
The SLO is unachievable given the current infrastructure
and code quality. The error budget is always negative.

**Diagnostic Command:**

```promql
# Measure actual 90-day SLI performance to establish
# a realistic baseline before setting an SLO
(
  sum(increase(checkout_requests_total{
    status=~"2.."}[90d]))
  / sum(increase(checkout_requests_total{
    status!~"4.."}[90d]))
)
# Example output: 0.9953 = 99.53% actual performance
# SLO should be set at or below this number initially
```

**Fix:**
Lower the SLO to the measured 90-day P10 performance
(the 10th percentile month - i.e., the worst typical
month). This ensures the SLO is achievable on bad months.
Then build a roadmap to progressively raise it.

**Prevention:**
Never set an SLO without a minimum 30-day measurement
period. The first SLO should always be set below
current measured performance.

---

**SLO compliance calculation using wrong PromQL**

**Symptom:**
The monthly SLO report shows 99.97% compliance for
the month. However, manually reviewing incident records
shows 3 incidents totalling 2 hours of degradation,
which should breach a 99.9% SLO (error budget = 43.2
minutes). The SLO report appears incorrect.

**Root Cause:**
The monthly compliance query uses an instantaneous
`rate()` query against the current moment rather than
computing total counts over the month. The rate at
query time (midnight on the last day of the month)
is fine, producing an incorrect 99.97% reading.

**Diagnostic Command:**

```promql
# WRONG: instantaneous rate at query time
sum(rate(checkout_requests_total{status=~"2.."}[5m]))
/ sum(rate(checkout_requests_total[5m]))
# Returns: current 5-minute success rate, not monthly

# CORRECT: total counts over the full window
sum(increase(checkout_requests_total{status=~"2.."}[30d]))
/ sum(increase(checkout_requests_total[30d]))
# Returns: true 30-day availability
```

**Fix:**
Use `increase()` over the full window for monthly SLO
compliance reports. Use `rate()` only for real-time
alerting (burn rate).

**Prevention:**
Run both queries side-by-side during a known incident
period to verify the compliance query correctly reflects
incidents. Validate that the compliance query matches
manually calculated incident totals.

---

**SLO error budget policy not enforced**

**Symptom:**
The error budget is exhausted mid-month. A deployment
freeze policy exists. The development team deploys
anyway, citing "the deployment is urgent - it's a
feature for a major customer demo." The SRE team
objects. The debate escalates to management. The
deployment proceeds. Another incident occurs.

**Root Cause:**
The error budget policy exists as documentation but
has no enforcement mechanism. The freeze is advisory,
not automatic. Without automated enforcement or clear
escalation authority, the policy is bypassed under
pressure.

**Fix:**
Implement the error budget policy as an automated
gate in the CI/CD pipeline:

```bash
# CI/CD gate: check error budget before deploying
BUDGET_REMAINING=$(query_error_budget_remaining)
if (( $(echo "$BUDGET_REMAINING < 0" | bc -l) )); then
  echo "ERROR: SLO error budget exhausted."
  echo "Deployment blocked per error budget policy."
  echo "Contact SRE team for exception process."
  exit 1
fi
```

**Prevention:**
The error budget policy document must define: (1) who
can override a freeze and under what conditions (only
security patches, only VP Engineering approval), (2)
the override is logged and reviewed in the next post-
mortem. The override mechanism must exist but must be
explicit and audited.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `SLI (Service Level Indicator)` - the SLO is a target
  applied to an SLI; you cannot define an SLO without
  first defining the SLI it governs
- `SRE What It Is` - SLOs are the core governance tool
  of SRE practice

**Builds On This (learn these next):**

- `SLA (Service Level Agreement)` - the customer-facing
  contract derived from (and looser than) the SLO
- `Error Budget` - the operational consequence of the
  SLO: the allowed "room for failure" each month
- `Alerting Fundamentals` - SLO burn rate alerts fire
  when the error budget is being consumed too fast

**Alternatives / Comparisons:**

- `Uptime SLA (binary)` - the older, simpler alternative
  to SLOs: "99.9% uptime" as a contractual promise.
  Simpler but less nuanced than the SLI/SLO/error budget
  framework.

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DEFINITION   │ SLO = target threshold for SLI over a    │
│              │ time window. Internal commitment.         │
├──────────────┼───────────────────────────────────────────┤
│ FORMULA      │ Error budget = (1 - SLO) x window secs   │
│              │ 99.9% over 30d = 43.2 min budget         │
├──────────────┼───────────────────────────────────────────┤
│ SLO vs SLA   │ SLO: internal target (tighter)            │
│              │ SLA: customer contract (looser)           │
├──────────────┼───────────────────────────────────────────┤
│ SET SLO AT   │ Minimum reliability users find acceptable │
│              │ Never set aspirationally                  │
├──────────────┼───────────────────────────────────────────┤
│ BUDGET STATES│ >50%: deploy freely                       │
│              │ 20-50%: review deployments               │
│              │ <0%: freeze + reliability sprint          │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ SLO = 99.999% before measuring baseline.  │
│              │ Permanent freeze. Team ignores SLO.       │
├──────────────┼───────────────────────────────────────────┤
│ COMPLIANCE   │ Use increase() over full window, not      │
│ QUERY        │ rate() which gives current snapshot       │
├──────────────┼───────────────────────────────────────────┤
│ REVIEW       │ Quarterly: raise SLO if always healthy,   │
│ CADENCE      │ lower if chronically breached            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Error Budget → SLA → Burn Rate Alerting   │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Define targets before measuring, but set targets based
on measured reality. The SLO must be set before it
governs decisions (it must exist to have meaning), but
it must be anchored in what is currently achievable
(an impossible target demoralises teams and is ignored).
This applies to: performance benchmarks (set performance
budgets based on measured baselines), code quality gates
(set coverage thresholds based on current coverage
trends), and delivery metrics (set sprint velocity
targets based on measured historical velocity).

---

### 💡 The Surprising Truth

The most counterintuitive SLO insight: the right SLO
is often lower than what the system is currently
achieving. If a service maintains 99.97% availability
consistently, the SLO should be set at 99.9% (or even
99.5%). This is not "lowering standards" - it is
recognising that the 0.07% gap between current
performance (99.97%) and a tight SLO (99.97%) would
freeze all deployments during any regression. The
error budget created by a 99.9% SLO (43 minutes/month)
is the freedom to deploy and learn. The near-zero error
budget of a 99.97% SLO creates a system that is
technically reliable but organisationally paralysed.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[EXPLAIN]** Explain to a product manager why setting
   a 99.999% SLO on a service currently achieving 99.9%
   is counterproductive, and calculate the error budget
   at each level to demonstrate the deployment impact.
2. **[DEBUG]** Given a monthly SLO compliance report
   showing 99.97% when incidents account for 2 hours
   of downtime, identify the PromQL error in the
   compliance query and write the correct expression.
3. **[DECIDE]** Given a new payment service, walk through
   the process of setting the first SLO: what data you
   need, how long you must measure, what your first SLO
   target should be, and how you justify it to both the
   product team (why not 99.999%?) and the SLA team
   (why not 95%?).
4. **[BUILD]** Implement the complete error budget policy
   as an automated CI/CD gate: a script that queries
   Prometheus for current budget remaining, blocks
   deployment if below 0%, and provides an override
   mechanism with audit logging.
5. **[EXTEND]** Design a multi-window SLO (7-day and
   30-day windows simultaneously) for a checkout service,
   write the alert rules for both windows, and explain
   what failure modes each window catches that the other
   misses.

---

### 🧠 Think About This Before We Continue

**Q1.** It is day 20 of the month. Your checkout service
SLO is 99.9% over 30 days. So far this month, 3 incidents
have consumed 35 minutes of the 43.2-minute error budget.
The development team wants to deploy a major feature
rewrite. Your error budget policy says "deployment review
required when budget < 20%." Calculate: what is the
current budget remaining as a percentage? What percentage
of the month remains? If the feature deployment has a
30% chance of causing a 15-minute incident, should you
approve the deployment? Show your reasoning using the
error budget numbers.
_Hint: 8.2 minutes remaining out of 43.2 = 19% remaining.
You are below the 20% threshold - deployment review is
required. Expected incident cost = 0.3 x 15min = 4.5min.
Current remaining - expected cost = 8.2 - 4.5 = 3.7min
remaining after expected impact. High risk of SLO breach.
The correct answer: defer the deployment to next month
unless it contains a critical security fix._

**Q2.** Your SRE team has been tracking the checkout
service SLO for 6 months. Every month, the error budget
is never less than 80% remaining. The development team
is frustrated that they cannot deploy as frequently as
other teams because their SLO is "too strict." You
review the data and find: current SLI is consistently
99.97%, SLO target is 99.9%, SLA is 99.5%. What does
this data tell you about the SLO? What action should
you take, and what is the expected impact on the
development team's deployment cadence?
_Hint: 99.97% consistently achieved vs 99.9% SLO means
you have 43 - 13 = 30 extra minutes/month of headroom.
This suggests the SLO can be tightened from 99.9% to
99.95% (21.6 min budget) while still providing reliable
operation. Or: the SLO is actually correctly set and
the development team's frustration is because they are
NEVER spending the error budget - suggesting they should
deploy more aggressively, not less._

**Q3 (TYPE G):** You are designing SLOs for a payment
platform that has a two-tier architecture: a consumer-
facing API (handles payment initiation) and an internal
settlement service (processes payments in batch overnight).
The consumer API is called 100,000 times/day. The
settlement service runs once per night. Design the SLO
framework for both services: what SLI to use for each,
what the appropriate SLO target should be for each,
how the error budget applies to batch systems (how do
you calculate "downtime" for a batch job?), and what
the error budget policy looks like when the settlement
service fails - especially if the failure affects the
consumer API's apparent reliability.
\*Hint: Consumer API uses request-based SLI (availability

- latency). Settlement uses timeliness SLI (fraction
  of runs completing before T hours deadline) and
  correctness SLI (fraction of records correctly settled).
  Error budget for batch: 99.9% SLO on nightly runs =
  0.1% of runs can fail = 0.36 runs/year. The settlement
  failure cascading to consumer API is a dependency SLO
  failure - the consumer SLO must account for settlement
  dependency health.\*

---

### 🎯 Interview Deep-Dive

**Q1: "Explain the difference between an SLI, SLO, and
SLA. Which is the most operationally important?"**
_Why they ask:_ Tests whether the candidate understands
the three-tier system and which layer drives daily
operations.
_Strong answer includes:_

- SLI: the measurement (current checkout success rate)
- SLO: the internal target (checkout success >= 99.9%
  over 30 days) - drives daily operations (error budget)
- SLA: the customer contract (checkout success >= 99.5%
  per month) - drives business consequences (penalties)
- Most operationally important: the SLO. It drives the
  error budget policy, deployment gates, and reliability
  investment decisions. The SLA is rarely breached in
  a well-run SRE org because the SLO provides buffer.
- Key insight: the SLO should always be tighter than
  the SLA. If they are equal, there is no buffer.

**Q2: "How do you set the right SLO level? What process
would you use for a new service?"**
_Why they ask:_ Tests practical SLO calibration knowledge.
_Strong answer includes:_

- Step 1: measure current SLI for 30-90 days before
  setting any target
- Step 2: ask the product/UX team "at what point do
  users notice degradation?" (conversion rate research,
  user surveys, competitive analysis)
- Step 3: set the initial SLO at or below the measured
  P10 monthly performance (worst typical month)
- Step 4: set the SLO tighter than the SLA by at
  least 0.1-0.5% to provide buffer
- Step 5: review quarterly - if never breached, the
  SLO may be too conservative; if always breached,
  reliability investment is needed before raising
- Key: never set an aspirational SLO on day 1

**Q3: "What happens when the error budget is exhausted?
Walk me through the process."**
_Why they ask:_ Tests understanding of the error budget
policy lifecycle - a key operational SRE competency.
_Strong answer includes:_

- SLO is breached (current month SLI < SLO target)
- Error budget policy triggers: deployment freeze for
  all non-critical changes (feature deployments,
  infrastructure changes)
- SRE team and development team both focus on
  reliability: root cause analysis, fixing the
  contributing factors from the month's incidents
- Only exception: security patches can deploy (with
  SRE approval and explicit rollback plan)
- Recovery: as time passes in the rolling 30-day window,
  older incidents fall off the window. Budget gradually
  recovers. New deployments can resume when budget
  is positive again.
- Post-mortem: mandatory review of what consumed the
  budget and what action items will prevent recurrence
