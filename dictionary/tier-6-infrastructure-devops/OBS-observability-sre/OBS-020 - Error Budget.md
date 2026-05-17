---
id: OBS-020
title: "Error Budget"
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★☆
depends_on: OBS-011, OBS-012, OBS-013
used_by: OBS-009, OBS-021
related: OBS-011, OBS-012, OBS-013, OBS-009
tags:
  - observability
  - reliability
  - sre
  - devops
  - pattern
  - intermediate
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 20
permalink: /obs/error-budget/
---

# OBS-020 - Error Budget

⚡ TL;DR - The error budget is the operational
consequence of an SLO: the maximum allowed "bad
events" in a time window before the SLO is breached.
It transforms reliability from a political debate
into a data-driven governance tool that balances
feature velocity against system stability.

| #020 | Category: Observability & SRE | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | SLI, SLO, SLA | |
| **Used by:** | Alerting Fundamentals, Alerting Anti-Patterns | |
| **Related:** | SLI, SLO, SLA, Alerting Fundamentals | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A development team wants to deploy a new feature every
week. The SRE team says the system is "not ready for
more deployments - too many recent incidents." The
development team says "those incidents were minor and
already fixed." The SRE team says "reliability must
come first." Development says "we're moving too slow."

This argument is political. Neither side has objective
data to prove their position. The solution depends on
who is more senior or more persuasive, not on what
is actually true. The system is either deployed too
aggressively (causing more incidents) or too
conservatively (slowing feature delivery).

**THE INVENTION:**
The error budget (from Google SRE Book) converts this
argument into arithmetic. If the SLO is 99.9% and the
current SLI is 99.5%, the budget is negative - the
SRE team's position is correct and supported by data.
If the SLO is 99.9% and the current SLI is 99.98%,
the budget is healthy - the development team's position
is correct. The error budget makes reliability
investment a data-driven decision, not a political one.

---

### 📘 Textbook Definition

**Error budget** is the maximum allowed unreliability
within a time window, derived from the SLO:

```
Error budget = (1 - SLO target) x window duration

99.9% SLO over 30 days:
= (1 - 0.999) x 30 x 24 x 60
= 0.001 x 43,200 minutes
= 43.2 minutes

This means: in any rolling 30-day period, the
service is allowed up to 43.2 minutes of "bad events"
(where the SLI falls below 100%) before the SLO
is breached.
```

**Budget consumption:** any event that reduces the
SLI below 100% consumes budget:
- Incidents (service outages, elevated error rates)
- Planned maintenance windows (if not excluded from SLO)
- Failed deployments that cause brief degradation
- Infrastructure events (cloud provider issues)

**Budget remaining:** how much budget is left in
the current window:
```
Budget remaining = Error budget - Budget consumed so far
Burn rate = Budget consumed rate / Budget accrual rate
```

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The error budget is the "room to fail" that the SLO
creates - when that room is full, deployments stop
until reliability improves.

> Think of a credit card with a $1,000 limit. The
> limit is the SLO: the maximum allowed spending (risk)
> per month. Every purchase (incident, deployment
> risk) consumes the credit limit. When the balance
> reaches $1,000 (error budget exhausted), the card
> is declined (deployment freeze). When the statement
> closes (month rolls over), the limit resets and
> new spending can begin.
>
> The key: having a credit card with a limit is not
> a constraint on living - it is a governance mechanism
> that enables measured risk-taking. Without a limit
> (no SLO), spending is unlimited. With a limit,
> the team knows exactly how much risk remains.

---

### 🔩 First Principles Explanation

**THE BURN RATE CONCEPT:**

The error budget burn rate measures how fast the
budget is being consumed relative to the sustainable
rate:

```
Burn rate = current_error_rate / (1 - SLO_target)

At SLO 99.9%:
  Burn rate = 1x: consuming budget at exactly the
    SLO rate. Budget lasts exactly 30 days.
  Burn rate = 2x: budget consumed in 15 days.
  Burn rate = 14.4x: budget consumed in ~2 days.
  Burn rate = 720x: budget consumed in ~1 hour.

If current error rate is 1% on a 99.9% SLO:
  Burn rate = 0.01 / (1 - 0.999) = 0.01/0.001 = 10x
  Budget will last: 30 days / 10 = 3 days
```

**THE THREE STATES:**

```
Budget healthy (>50% remaining):
  SLI well above SLO target.
  Current error rate is well below the SLO threshold.
  → Deploy freely. Accept higher risk for features.

Budget caution (20-50% remaining):
  SLI above SLO but budget is being consumed.
  Recent incidents or deployments have consumed budget.
  → Review deployments. No high-risk changes.

Budget exhausted (<0% remaining = SLO breached):
  SLI has dropped below SLO target for the current window.
  Error budget for the month is fully consumed.
  → Freeze all feature deployments.
  → Focus 100% on reliability improvement.
  → No exceptions except security patches.
```

**THE DEPLOYMENT RISK MODEL:**

```
Each deployment has a risk of causing an incident.
Risk varies by: deployment size, complexity, test coverage.

Example risk model for a typical deployment:
  Small config change: 2% chance of 5-minute incident
    Expected budget cost: 0.02 x 5 = 0.1 minutes
  Database migration: 10% chance of 30-minute incident
    Expected budget cost: 0.10 x 30 = 3 minutes
  Major rewrite: 25% chance of 120-minute incident
    Expected budget cost: 0.25 x 120 = 30 minutes

If budget remaining is 8 minutes:
  Small config change: acceptable (0.1 min expected)
  DB migration: review required (3 min expected)
  Major rewrite: defer to next month (30 min expected)
```

---

### 🧪 Thought Experiment

**THE VELOCITY vs RELIABILITY DEBATE:**

Two teams. Both have a 99.9% SLO for their checkout
service. Same 43.2-minute monthly error budget.

**Team A - Development-led:**
Ships 8 deployments per week. Each small. Low individual
risk (3% chance of 5-minute incident each). Expected
monthly incident time: 8 x 4 weeks x 0.03 x 5 = 48 min.
Budget: 43.2 min. SLO breached every month.
Result: customers experience degradation monthly.
Deployment freeze imposed mid-month every month.
Development velocity drops as the team becomes risk-
averse after the third consecutive SLO breach.

**Team B - SLO-governed:**
Same 8 deployments per week. But they track the budget.
When budget hits caution (20-50%), they add a
deployment review step. When budget is exhausted,
they pause feature deployments for 2 days and focus
on reliability improvements. In 6 months, their
deployment quality improves (better testing, smaller
changes) and the error rate per deployment drops.
Result: SLO maintained. Deployments approved on
merit. Reliability improves over time.

**The insight:** the error budget is not a constraint
on deployment velocity - it is a forcing function
that improves deployment quality over time.

---

### 🧠 Mental Model / Analogy

> A commercial pilot has a landing currency requirement:
> must complete 3 landings in the last 90 days to
> remain current. This is the SLO. Each landing
> consumed time and resources (the error budget). If
> the pilot has made 2 landings this month and the
> 3-landing requirement resets monthly, they have
> "budget" for one more required landing. If they
> go over budget (miss the currency requirement), they
> cannot legally fly passengers.
>
> The error budget works the same way. The SLO is the
> currency requirement. Each incident is a consumed
> landing slot. When the budget runs out (currency
> lapses), the pilot (team) must focus on recertification
> (reliability sprint) before flying passengers (deploying
> features) again.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone):**
The error budget is how much downtime or failures the
service is allowed this month before breaking the
reliability promise. When it runs out, we stop making
changes until next month.

**Level 2 - How to use it (junior):**
Check the error budget remaining before requesting
a deployment. If the Grafana SLO dashboard shows
budget < 20%, get SRE review. If < 0%, defer the
deployment or request an exception from the SRE team
lead.

**Level 3 - How it works (mid-level):**
Error budget = (1 - SLO) x window. Budget consumption
comes from any period where the SLI is below 100%.
Monitor via burn rate: current error rate divided by
(1 - SLO). Multi-window burn rate alerts (1h + 5m
windows) detect fast budget consumption before the
SLO is breached. The error budget policy (what the
team does when budget is healthy/caution/exhausted)
must be written and enforced.

**Level 4 - Governance (senior):**
Error budget policy design: who can approve a freeze
exception? How is the exception logged? What reliability
improvement is required before deployments resume?
The quarterly SLO review: if the budget is never
spent, the SLO may be too conservative. If always
exhausted, reliability investment is needed. The
error budget as a communication tool: shows product
managers exactly how much reliability headroom exists
for risky feature deployments.

**Level 5 - Organisation design (staff):**
Error budget accounting in multi-team services. If
team A and team B both own parts of the checkout
service, the error budget is shared. An incident
caused by team A consumes budget for team B's
deployments too. This creates cross-team alignment:
both teams have incentive to keep incidents low,
not just their own components. Error budget at
the portfolio level: if a shared platform service
(auth, database, message broker) has a low error
budget, it blocks deployments across all consuming
services simultaneously - the blast radius of
a platform SLO breach.

---

### ⚙️ How It Works (Mechanism)

**BUDGET CALCULATION IN PROMETHEUS:**

```promql
# Error budget remaining as percentage
# SLO: 99.9% availability over 30 days

# Step 1: current SLI (30-day window)
(
  sum(increase(checkout_requests_total{
    status=~"2.."}[30d]))
  / sum(increase(checkout_requests_total{
    status!~"4.."}[30d]))
)

# Step 2: budget consumed
# = (1 - current_SLI) / (1 - SLO_target) * 100%
(
  (1 - sum(increase(checkout_ok[30d]))
       / sum(increase(checkout_total[30d])))
  / (1 - 0.999)
) * 100
# Returns: 60 (60% of budget consumed, 40% remaining)

# Step 3: budget remaining
100 - (
  (1 - sum(increase(checkout_ok[30d]))
       / sum(increase(checkout_total[30d])))
  / (1 - 0.999)
) * 100
# Returns: 40 (40% of budget remaining)
```

**BURN RATE ALERT (multi-window):**

```yaml
# Two-window burn rate alert
# Fast: fires when budget will be exhausted in ~2 days
# Slow: fires when budget will be exhausted in ~3 days
groups:
- name: checkout-error-budget
  rules:
  - alert: CheckoutFastBurnRate
    expr: |
      (
        (1 - sum(rate(checkout_ok[1h]))
        / sum(rate(checkout_total[1h])))
        / (1 - 0.999)
      ) > 14.4    # budget exhausted in <2 days at this rate
      AND
      (
        (1 - sum(rate(checkout_ok[5m]))
        / sum(rate(checkout_total[5m])))
        / (1 - 0.999)
      ) > 14.4
    labels:
      severity: page
    annotations:
      summary: "Checkout SLO fast burn: deploy freeze triggered"

  - alert: CheckoutSlowBurnRate
    expr: |
      (
        (1 - sum(rate(checkout_ok[6h]))
        / sum(rate(checkout_total[6h])))
        / (1 - 0.999)
      ) > 6       # budget exhausted in <5 days at this rate
      AND
      (
        (1 - sum(rate(checkout_ok[30m]))
        / sum(rate(checkout_total[30m])))
        / (1 - 0.999)
      ) > 6
    labels:
      severity: ticket
    annotations:
      summary: "Checkout SLO slow burn: deployment review required"
```

---

### 🔄 The Complete Picture - End-to-End Flow

**ERROR BUDGET LIFECYCLE (one month):**

```
[April 1: Month begins]
  Budget: 100% (43.2 minutes available)
  State: HEALTHY → Deploy freely
        ↓
[April 5: Deployment: checkout-api v1.47.1]
  Small risk. No incident. Budget: 100%
        ↓
[April 8: Incident - 5-minute degradation]
  SLI fell to 95% for 5 minutes
  Budget consumed: 5 / 43.2 = 11.6%
  Budget remaining: 88.4% → HEALTHY
        ↓
[April 12: Incident - 25-minute degradation]
  Major incident. Cart service timeout.
  Budget consumed: (5+25) / 43.2 = 69.4%
  Budget remaining: 30.6% → CAUTION
  [Deployment review required]
        ↓
[April 15: Deployment: checkout-api v1.47.2]
  Deployment review completed. Low risk. Approved.
  No incident. Budget: 30.6% → CAUTION
        ↓
[April 18: Incident - 20-minute partial degradation]
  Payment timeout. 40% of requests affected.
  Budget consumed: (30 + 20 x 0.4 x 43.2/43.2)
  Budget remaining: 30.6 - (20 x 0.4) / 43.2 * 100
                   = 30.6 - 18.5 = 12.1% → CAUTION
        ↓
[April 21: Incident - 15-minute degradation]
  Budget consumed fully:
  12.1% - (15/43.2)*100 = 12.1 - 34.7 = -22.6%
  SLO BREACHED. Budget exhausted.
  State: FREEZE
        ↓
[April 21-30: Reliability sprint]
  No feature deployments.
  Two root-cause fixes shipped (SRE-approved).
  Error rate stabilises at 0.01% (10x below SLO).
  Budget begins recovering (rolling 30d window:
  April 1-8 events falling off the window).
        ↓
[May 1: Window rolls]
  Budget reset. Post-mortem completed.
  Action items: circuit breaker, better deployment tests.
  State: HEALTHY
```

---

### 💻 Code Example

**Example 1 - BAD: Threshold-based alerting (not budget-aware):**

```yaml
# BAD: static threshold alert, not budget-aware
# Fires on any 1% error rate, even if budget is full
# Or: misses a 0.5% sustained error rate that slowly
# depletes the entire budget over 30 days

- alert: HighErrorRate
  expr: |
    sum(rate(checkout_errors_total[5m]))
    / sum(rate(checkout_requests_total[5m])) > 0.01
  # Problem 1: Fires on transient 1m spikes (noisy)
  # Problem 2: Does not account for SLO target
  # Problem 3: 0.5% error rate never fires but
  #   consumes budget 2x faster than SLO allows
```

**Example 2 - GOOD: Burn rate alert (budget-aware):**

```yaml
# GOOD: multi-window burn rate alert
# Fires only when budget is burning unsustainably
# Silent for transient spikes (5m confirmation required)
# Catches slow burns (6h window for sustained issues)

- alert: CheckoutFastBurn
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
  # Fires only when: both 1h AND 5m burn rate > 14.4x
  # 14.4x burn rate = budget exhausted in 30/14.4 = ~2d
  # False positive rate: very low (two-window confirmation)
```

**Example 3 - CI/CD error budget gate:**

```bash
#!/bin/bash
# Pre-deployment error budget check
# Run in CI/CD before every production deployment

PROMETHEUS_URL="${PROMETHEUS_URL:-http://prometheus:9090}"
SLO_TARGET=0.999
DEPLOY_BLOCK_THRESHOLD=0  # block if budget < 0%
DEPLOY_WARN_THRESHOLD=20  # warn if budget < 20%

# Query Prometheus for budget remaining
BUDGET_REMAINING=$(curl -sG "${PROMETHEUS_URL}/api/v1/query" \
  --data-urlencode 'query=100 - ((1 - sum(increase(checkout_ok_total[30d])) / sum(increase(checkout_requests_total[30d]))) / (1 - 0.999)) * 100' \
  | jq '.data.result[0].value[1]' | tr -d '"')

echo "Error budget remaining: ${BUDGET_REMAINING}%"

if (( $(echo "$BUDGET_REMAINING < $DEPLOY_BLOCK_THRESHOLD" | bc -l) )); then
  echo "ERROR: Error budget exhausted (${BUDGET_REMAINING}%)."
  echo "Deployment blocked by error budget policy."
  echo "Contact SRE for exception (security fixes only)."
  exit 1
elif (( $(echo "$BUDGET_REMAINING < $DEPLOY_WARN_THRESHOLD" | bc -l) )); then
  echo "WARNING: Error budget low (${BUDGET_REMAINING}%)."
  echo "Deployment review required. Notify SRE team."
  echo "Deployment will proceed - add SRE sign-off."
  # In practice: create a Jira ticket or require manual approval
fi

echo "Error budget check passed. Deployment approved."
```

---

### ⚖️ Comparison Table

| Budget state | Budget remaining | Action | Who decides |
|---|---|---|---|
| Healthy | > 50% | Deploy freely, accept risk | Team |
| Caution | 20-50% | Deployment review required | Team + SRE review |
| Warning | 5-20% | Only low-risk deployments | SRE sign-off required |
| Exhausted | < 0% | Feature freeze, reliability sprint | SRE team authority |
| Exception | Exhausted + urgent | Security patch only | VP Engineering sign-off |

**Error budget policies across organisations:**

| Style | Enforcement | Benefit | Risk |
|---|---|---|---|
| Advisory | Documented, no gate | Low friction | Ignored under pressure |
| Automated gate | CI/CD blocks deploy | Consistent | May block urgent fixes |
| Review board | Human approval for caution/exhausted | Contextual | Bottleneck, slow |
| Hybrid | Gate + override + audit | Balanced | Requires governance setup |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Error budget = allowed downtime" | Error budget is allowed bad events (errors, slow requests), not just downtime. A 1% error rate for 1 hour consumes budget even if the service was technically "up." |
| "Exhausting the budget is a failure" | Error budgets are designed to be occasionally exhausted. The budget exists to govern risk-taking. An SLO that is never breached and budget always full may indicate an over-conservative SLO that is slowing development unnecessarily. |
| "100% SLO = maximum safety" | 100% SLO means zero error budget. Every deployment risks breaching the SLO. Development is paralysed. The correct SLO has enough error budget to allow controlled risk-taking. |
| "Error budget resets on Jan 1" | Rolling window error budgets (last 30 days) do not reset on calendar boundaries. As incidents age out of the 30-day window, budget recovers. Calendar month windows do reset - this creates "sprint to deploy everything in the first week" incentives. |
| "The error budget policy is optional" | Without an enforced policy, the error budget is just a number on a dashboard. The policy (what changes when budget is exhausted) is the mechanism that makes the error budget operationally meaningful. |

---

### 🚨 Failure Modes & Diagnosis

**Error budget always exhausted: unachievable SLO**

**Symptom:**
The error budget is exhausted by day 10 every month.
Feature deployments are frozen for the last 20 days
of every month. The development team has stopped
trusting the SLO system - they deploy anyway, saying
"it's always exhausted, it doesn't mean anything."
The reliability system has broken down.

**Root Cause:**
The SLO was set too high (aspirationally), above
the system's actual achievable reliability. The error
budget is structurally unachievable given current
infrastructure quality and incident rate.

**Diagnostic:**
```promql
# Check what the 90-day SLI performance actually is
# (to find the achievable baseline)
(
  sum(increase(checkout_ok_total[90d]))
  / sum(increase(checkout_requests_total[90d]))
)
# If result is 0.9952 (99.52%) but SLO is 0.999 (99.9%):
# The SLO is 38% more restrictive than actual performance
# Reset SLO to 0.995 (99.5%) as the achievable baseline
```

**Fix:**
Lower the SLO to the measured 90-day P10 performance
(worst typical month). Communicate the change as a
"baseline measurement phase" - the SLO will be raised
as reliability improves. Re-engage the development
team with a realistic SLO that creates an actionable
error budget.

---

**Error budget policy exists but is never enforced**

**Symptom:**
The error budget is regularly exhausted in the last
10 days of the month. The deployment freeze policy
exists in the runbook. But every month, the same
conversation happens: "We need to deploy this urgent
feature." "The error budget is exhausted - we should
freeze." "This feature is different - it's for a big
customer." Feature deploys. Another incident. Budget
further exhausted.

**Root Cause:**
The policy has no automated enforcement. It is advisory,
not mandatory. Under pressure, it is always overridden
without logging or consequence.

**Fix:**
1. Implement the CI/CD gate (see code example above)
2. Add an override mechanism with explicit approval:
   the override creates a Jira ticket, requires VP
   Engineering approval comment, and is reviewed in
   the monthly post-mortem
3. Track override frequency as a metric: if overrides
   happen > 3 times/month, the policy or SLO is
   miscalibrated

---

**Budget consumed by planned maintenance (avoidable)**

**Symptom:**
A 4-hour planned maintenance window for database
migration consumed 556% of the monthly error budget
(4 hours vs 43-minute budget). The SLO was breached.
Service credits were issued to customers. The
maintenance was expected and announced - but the
SLO impact was not accounted for.

**Root Cause:**
Planned maintenance was not excluded from SLO measurement.
The SLO compliance query counts all downtime including
planned windows.

**Fix:**
Exclude planned maintenance from SLO measurement:
```promql
# Use a maintenance marker metric to exclude windows
# During maintenance: set maintenance_active = 1
# SLI calculation excludes maintenance periods

sum(increase(checkout_ok_total[30d]))
/ sum(
  increase(checkout_requests_total[30d])
  - increase(checkout_requests_total{maintenance="true"}[30d])
)
```

Or: schedule major maintenance immediately after
the SLO window resets (start of month) to give the
full 43-minute budget before the next window ends.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `SLI (Service Level Indicator)` - the measurement
  that the error budget is calculated from
- `SLO (Service Level Objective)` - the target that
  defines the error budget: error_budget = (1-SLO) x window

**Builds On This (learn these next):**
- `Alerting Fundamentals` - burn rate alerts fire
  when the error budget is being consumed faster
  than sustainable. The burn rate alert is the
  primary tool for detecting error budget risk.
- `Alerting Anti-Patterns` - understanding what
  alert fatigue looks like when error budget policy
  is not enforced

**Alternatives / Comparisons:**
- `Binary SLA` - the traditional alternative: "99.9%
  uptime or no credit." Simpler, but no daily
  operational signal. The error budget approach provides
  continuous feedback (burn rate) rather than a
  binary end-of-month judgment.

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ FORMULA      │ Budget = (1 - SLO) x window seconds       │
│              │ 99.9% SLO x 30d = 43.2 minutes           │
├──────────────┼───────────────────────────────────────────┤
│ BURN RATE    │ error_rate / (1 - SLO_target)             │
│              │ 1x = sustainable. 14.4x = budget in 2d   │
├──────────────┼───────────────────────────────────────────┤
│ 3 STATES     │ >50%: deploy freely                       │
│              │ 20-50%: deployment review                 │
│              │ <0%: freeze + reliability sprint          │
├──────────────┼───────────────────────────────────────────┤
│ ALERT        │ Fast burn: 14.4x for 1h + 5m → PAGE       │
│ THRESHOLDS   │ Slow burn: 6x for 6h + 30m → TICKET       │
├──────────────┼───────────────────────────────────────────┤
│ POLICY MUST  │ Written. Enforced. Override = logged.     │
│              │ Advisory policies are always bypassed     │
├──────────────┼───────────────────────────────────────────┤
│ REVIEW       │ Quarterly: never exhausted → SLO too low  │
│ CADENCE      │ Always exhausted → SLO too high           │
│              │ Target: budget occasionally ~depleted     │
├──────────────┼───────────────────────────────────────────┤
│ CONSUME      │ All incidents. Failed deployments.        │
│ SOURCES      │ Planned maintenance (if not excluded).    │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Policy not enforced = no operational value│
│              │ SLO too high = budget always exhausted    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Burn Rate Alerting → Alerting Anti-Patterns│
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Convert political arguments into data-driven decisions
by defining the measurement, the threshold, and
the consequence upfront. The error budget does this
for reliability vs velocity. The same principle
applies to: code coverage (policy: freeze new features
if coverage drops below 80%), performance budgets
(policy: block deploy if P99 regresses by > 20%),
technical debt (policy: dedicate 20% of sprint to
debt when debt metric exceeds threshold). In each
case: define the metric, define the threshold,
define the consequence. Remove the political variable.

---

### 💡 The Surprising Truth

The most counterintuitive error budget insight: an
error budget that is never consumed is a symptom
of over-investment in reliability. If the SLO budget
is never spent (SLI is always well above target),
the team is either: (a) not deploying frequently
enough, (b) has set the SLO too low, or (c) is
investing more in reliability than users require.
The error budget exists to be spent - it represents
the team's licence to take risk in the service of
feature delivery. A team that never spends its error
budget is like a company that never invests its
capital - technically safe, but failing to generate
value from its resources.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **[CALCULATE]** Given a 99.95% SLO, a 30-day window,
   and 3 incidents (8 min, 15 min, 5 min of degradation),
   calculate the budget remaining as both a duration
   and a percentage.
2. **[QUERY]** Write a PromQL expression that returns
   the current error budget remaining as a percentage
   for a service with a 99.9% SLO, using `increase()`
   over a 30-day rolling window.
3. **[ALERT]** Write a multi-window burn rate alert
   (1h+5m and 6h+30m) that fires when the error budget
   is being consumed faster than sustainable. Explain
   the threshold values (14.4x and 6x).
4. **[DESIGN]** Design an error budget policy for a
   new service: the three states, the deployment rules
   for each state, the override mechanism, and how
   the policy is enforced (advisory vs automated).
5. **[DIAGNOSE]** Given a service where the error budget
   is always exhausted by day 10, diagnose whether
   the problem is the SLO calibration, the incident
   rate, or the deployment frequency, and propose
   a specific fix for each root cause.

---

### 🧠 Think About This Before We Continue

**Q1.** It is April 20th (20 days into the month).
Your checkout service has a 99.9% SLO. The error budget
is 43.2 minutes/month. So far this month, incidents
have consumed 38 minutes. Your team wants to deploy
a database migration that has a 15% chance of causing
a 20-minute incident. Calculate: (a) current budget
remaining, (b) expected budget cost of the deployment,
(c) expected budget remaining after deployment,
(d) should you deploy or defer? Show your reasoning.
*Hint: (a) 43.2 - 38 = 5.2 minutes remaining = 12%.
(b) Expected cost: 0.15 x 20 = 3 minutes. (c) Expected
remaining: 5.2 - 3 = 2.2 minutes = 5%. (d) State:
WARNING (< 20% remaining). Expected state after deploy:
still above 0% but very close. Decision: high risk -
10% chance the deployment breaches the SLO outright
(uses the remaining 5.2 minutes + breach). Defer
to May 1 when budget resets, unless this is a critical
security or compliance fix.*

**Q2.** Your service has a 99.9% SLO. The monthly
error budget is 43.2 minutes. In the last 3 months:
- January: 41 minutes consumed (95% of budget)
- February: 39 minutes consumed (90% of budget)
- March: 44 minutes consumed (102% of budget - breached)

The SLO is at 99.9%. The SLA is at 99.5% (SLA not
breached in any month). What does this data tell you
about the SLO calibration? What action should the
SRE team take?
*Hint: The budget is consistently being almost-depleted
or depleted every month. This suggests either: (a)
the incident rate is too high (need reliability
investment), or (b) the SLO is set too high for the
current system state. Calculate 90-day SLI: if actual
SLI is consistently 99.91-99.93%, the SLO of 99.9%
is achievable but barely. Options: (1) reliability
sprint to reduce incident frequency to open up budget
headroom, (2) lower SLO to 99.8% to create more
headroom (controversial - appears to lower standards),
(3) raise SLA concern: if SLI is consistently 99.9%,
the SLA at 99.5% has massive buffer - the SLO is
doing its job but leaving no deployment budget.*

**Q3 (TYPE G):** You are designing the error budget
framework for a platform team that owns 5 shared
infrastructure services (auth, database proxy,
message broker, object storage, service mesh).
These 5 services are consumed by 80 application teams.
When the auth service's error budget is exhausted,
it affects ALL 80 teams' deployments. Design the
error budget framework for this platform team:
SLO targets for each service, how the error budget
policy interacts with consuming teams, how consuming
teams are notified of platform budget status, and
what the platform team's responsibilities are during
a budget exhaustion event.
*Hint: Platform services need higher SLOs than
application services (auth failure = all users
affected). Auth SLO: 99.99%. DB proxy: 99.99%.
Message broker: 99.95%. When platform budget is
exhausted: notify all 80 teams via Slack/email
(automated). Platform team enters a reliability
sprint - no platform changes for 2 weeks. But:
consuming teams are NOT blocked from deploying
their own services (platform outage vs consuming
team deployment are independent). Exception: if
the platform issue is related to a specific
integration pattern that consuming teams use -
that pattern should be temporarily blocked.*

---

### 🎯 Interview Deep-Dive

**Q1: "What is an error budget and how does it
influence development velocity?"**
*Why they ask:* Tests understanding of the core SRE
governance mechanism and its operational impact.
*Strong answer includes:*
- Error budget = (1 - SLO) x window. For 99.9% SLO
  over 30 days: 43.2 minutes of allowed bad events.
- It influences velocity by providing a data-driven
  deployment gate: when budget is healthy (> 50%),
  deploy freely. When caution (20-50%), review
  deployments. When exhausted (< 0%), freeze features.
- The key insight: the error budget creates alignment
  between development (wants to deploy fast) and SRE
  (wants system stability). Both teams work from the
  same budget number. The argument becomes "what is
  the current budget?" not "how much risk is acceptable?"
- Long-term: teams with error budgets improve their
  deployment quality over time because they have
  direct feedback on the reliability cost of each
  deployment.

**Q2: "What is a burn rate and why do we use it for
SLO alerting?"**
*Why they ask:* Tests understanding of the most
important alerting pattern in SRE practice.
*Strong answer includes:*
- Burn rate = current error rate / (1 - SLO target)
- Burn rate > 1: consuming budget faster than accrual
  rate (budget will not last the full month)
- Burn rate of 14.4x: budget consumed in 30/14.4 = ~2 days
- Why burn rate vs threshold: a fixed threshold alert
  (error_rate > 1%) fires on transient spikes and
  misses sustained 0.5% error rates that slowly deplete
  the budget. Burn rate captures the budget impact,
  not just the instantaneous error rate.
- Multi-window (1h+5m): requires both windows to be
  above the threshold simultaneously. Reduces false
  positives from transient spikes.

**Q3: "How do you handle a situation where a critical
business feature must be deployed when the error
budget is exhausted?"**
*Why they ask:* Tests ability to balance SRE principles
with business reality.
*Strong answer includes:*
- First: clarify "critical" - is this a security
  vulnerability fix? (Yes, deploy with SRE oversight
  and rollback plan). A revenue-generating feature?
  (Probably not - defer to next month or the next
  sprint when the budget has recovered).
- If it must proceed: the override process: (1) explicit
  VP Engineering approval, (2) SRE team designs the
  deployment (small batch, canary, feature flag,
  explicit rollback plan), (3) the override is logged
  and reviewed in the post-mortem.
- The important principle: the override mechanism
  must exist (100% blocking is not operational) but
  must require explicit accountability. If overrides
  happen every month, the policy or SLO is miscalibrated.
- Track override frequency: > 3 overrides/quarter
  means the SLO or policy needs recalibration.
